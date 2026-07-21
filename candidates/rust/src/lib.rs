use std::cell::RefCell;
use std::slice;

const I: u32 = 2;
const L: u32 = 4;
const M: u32 = 8;
const S: u32 = 16;
const X: u32 = 64;
const A: u32 = 256;
const BYTE: u32 = 1 << 20;

#[derive(Clone)]
enum Member {
    Lit(u32),
    Range(u32, u32),
    Cat(char),
}

#[derive(Clone)]
enum Expr {
    Lit(u32, u32),
    Dot(u32),
    Cat(char, u32),
    Class(Vec<Member>, bool, u32),
    Anchor(char, u32),
    Boundary(bool, u32),
    Seq(Vec<Expr>),
    Alt(Vec<Expr>),
    Group(usize, Box<Expr>),
    Backref(usize, u32),
    Repeat(Box<Expr>, usize, Option<usize>, u8),
    Look(bool, bool, Box<Expr>, usize),
    Atomic(Box<Expr>),
    Cond(usize, Box<Expr>, Box<Expr>),
}

pub struct Engine {
    root: Expr,
    groups: usize,
    names: Vec<(String, usize)>,
    flags: u32,
}
#[derive(Clone)]
struct State {
    pos: usize,
    caps: Vec<Option<(usize, usize)>>,
    last: Option<usize>,
}
struct Context<'a> {
    chars: &'a [u32],
    folds: &'a [u32],
    masks: &'a [u8],
    end: usize,
}

thread_local! { static LAST: RefCell<(String,isize,bool)> = const { RefCell::new((String::new(),-1,false)) }; }

fn set_error(msg: String, pos: Option<usize>, include: bool) {
    LAST.with(|value| *value.borrow_mut() = (msg, pos.map_or(-1, |v| v as isize), include));
}

struct Parser {
    source: Vec<u32>,
    at: usize,
    flags: u32,
    byte_mode: bool,
    groups: usize,
    names: Vec<(String, usize)>,
    widths: Vec<(usize, (usize, usize))>,
    named: Vec<(usize, u32)>,
}
type PResult<T> = Result<T, (String, Option<usize>, bool)>;

impl Parser {
    fn now(&self) -> Option<char> {
        self.source.get(self.at).and_then(|v| char::from_u32(*v))
    }
    fn take(&mut self) -> Option<char> {
        let value = self.now();
        if value.is_some() {
            self.at += 1;
        }
        value
    }
    fn fail<T>(&self, msg: String, pos: Option<usize>, include: bool) -> PResult<T> {
        Err((msg, pos, include))
    }
    fn skip(&mut self, flags: u32) {
        if flags & X == 0 {
            return;
        }
        loop {
            match self.now() {
                Some(' ' | '\t' | '\n' | '\r' | '\u{b}' | '\u{c}') => self.at += 1,
                Some('#') => {
                    while self.now().is_some() && self.now() != Some('\n') {
                        self.at += 1;
                    }
                }
                _ => break,
            }
        }
    }
    fn parse(&mut self) -> PResult<Expr> {
        let result = self.alt(self.flags)?;
        self.skip(self.flags);
        if self.at != self.source.len() {
            return self.fail("unbalanced parenthesis".into(), Some(self.at), true);
        }
        Ok(result)
    }
    fn alt(&mut self, flags: u32) -> PResult<Expr> {
        let mut branches = vec![self.seq(flags)?];
        while self.now() == Some('|') {
            self.at += 1;
            branches.push(self.seq(flags)?);
        }
        Ok(if branches.len() == 1 {
            branches.pop().unwrap()
        } else {
            Expr::Alt(branches)
        })
    }
    fn seq(&mut self, mut flags: u32) -> PResult<Expr> {
        let mut result = Vec::new();
        loop {
            self.skip(flags);
            match self.now() {
                None | Some('|') | Some(')') => break,
                _ => {}
            }
            let start = self.at;
            let mut node = self.atom(flags)?;
            self.skip(flags);
            node = self.repeat(node, flags)?;
            if let Expr::Seq(ref values) = node {
                if values.is_empty()
                    && self.at > start
                    && self.source.get(start + 1) == Some(&(b'?' as u32))
                    && self.source.get(self.at.saturating_sub(1)) == Some(&(b')' as u32))
                {
                    if start != 0 {
                        return self.fail(
                            "global flags not at the start of the expression".into(),
                            Some(start),
                            true,
                        );
                    }
                    flags = self.flags;
                    continue;
                }
            }
            result.push(node);
        }
        Ok(Expr::Seq(result))
    }
    fn repeat(&mut self, node: Expr, flags: u32) -> PResult<Expr> {
        let start = self.at;
        let Some(mark) = self.now() else {
            return Ok(node);
        };
        if !matches!(mark, '*' | '+' | '?' | '{') {
            return Ok(node);
        }
        if matches!(
            node,
            Expr::Anchor(_, _) | Expr::Boundary(_, _) | Expr::Look(_, _, _, _)
        ) {
            return self.fail("nothing to repeat".into(), Some(start), true);
        }
        self.at += 1;
        let (min, max) = match mark {
            '*' => (0, None),
            '+' => (1, None),
            '?' => (0, Some(1)),
            '{' => {
                let mut close = self.at;
                while close < self.source.len() && self.source[close] != b'}' as u32 {
                    close += 1;
                }
                if close == self.source.len() {
                    self.at = start;
                    return Ok(node);
                }
                let spec: String = self.source[self.at..close]
                    .iter()
                    .filter_map(|v| char::from_u32(*v))
                    .collect();
                if spec.is_empty()
                    || spec.chars().filter(|c| *c == ',').count() > 1
                    || spec.chars().any(|c| !c.is_ascii_digit() && c != ',')
                {
                    self.at = start;
                    return Ok(node);
                }
                self.at = close + 1;
                let pair = if let Some((left, right)) = spec.split_once(',') {
                    (
                        if left.is_empty() {
                            0
                        } else {
                            left.parse().unwrap()
                        },
                        if right.is_empty() {
                            None
                        } else {
                            Some(right.parse().unwrap())
                        },
                    )
                } else {
                    let n = spec.parse().unwrap();
                    (n, Some(n))
                };
                if pair.1.is_some_and(|right| pair.0 > right) {
                    return self.fail(
                        "min repeat greater than max repeat".into(),
                        Some(start + 1),
                        true,
                    );
                }
                pair
            }
            _ => unreachable!(),
        };
        let mode = match self.now() {
            Some('?') => {
                self.at += 1;
                1
            }
            Some('+') => {
                self.at += 1;
                2
            }
            _ => 0,
        };
        if matches!(self.now(), Some('*' | '+' | '?')) {
            return self.fail("multiple repeat".into(), Some(self.at), true);
        }
        let _ = flags;
        Ok(Expr::Repeat(Box::new(node), min, max, mode))
    }
    fn atom(&mut self, flags: u32) -> PResult<Expr> {
        let start = self.at;
        let value = self.take().unwrap();
        match value {
            '.' => Ok(Expr::Dot(flags)),
            '^' | '$' => Ok(Expr::Anchor(value, flags)),
            '[' => self.class(flags, start),
            '\\' => self.escape(flags, false, start),
            '(' => self.group(flags, start),
            '*' | '+' | '?' => self.fail("nothing to repeat".into(), Some(start), true),
            _ => Ok(Expr::Lit(value as u32, flags)),
        }
    }
    fn escape(&mut self, flags: u32, in_class: bool, slash: usize) -> PResult<Expr> {
        let Some(ch) = self.take() else {
            return self.fail("bad escape (end of pattern)".into(), Some(slash), true);
        };
        let controls = match ch {
            'a' => Some(7),
            'f' => Some(12),
            'n' => Some(10),
            'r' => Some(13),
            't' => Some(9),
            'v' => Some(11),
            _ => None,
        };
        if let Some(value) = controls {
            return Ok(Expr::Lit(value, flags));
        }
        if ch == 'b' {
            return Ok(if in_class {
                Expr::Lit(8, flags)
            } else {
                Expr::Boundary(true, flags)
            });
        }
        if ch == 'B' && !in_class {
            return Ok(Expr::Boundary(false, flags));
        }
        if "dDsSwW".contains(ch) {
            return Ok(Expr::Cat(ch, flags));
        }
        if "AZz".contains(ch) && !in_class {
            return Ok(Expr::Anchor(ch, flags));
        }
        if ch == 'x' {
            if self.at + 2 > self.source.len() {
                return self.fail("incomplete escape \\x".into(), Some(slash), true);
            }
            let text: String = self.source[self.at..self.at + 2]
                .iter()
                .filter_map(|v| char::from_u32(*v))
                .collect();
            let Ok(value) = u32::from_str_radix(&text, 16) else {
                return self.fail("incomplete escape \\x".into(), Some(slash), true);
            };
            self.at += 2;
            return Ok(Expr::Lit(value, flags));
        }
        if matches!(ch, 'u' | 'U') && !self.byte_mode {
            let count = if ch == 'u' { 4 } else { 8 };
            if self.at + count > self.source.len() {
                return self.fail(format!("incomplete escape \\{}", ch), Some(slash), true);
            }
            let text: String = self.source[self.at..self.at + count]
                .iter()
                .filter_map(|v| char::from_u32(*v))
                .collect();
            let Ok(value) = u32::from_str_radix(&text, 16) else {
                return self.fail(format!("incomplete escape \\{}", ch), Some(slash), true);
            };
            self.at += count;
            return Ok(Expr::Lit(value, flags));
        }
        if ch == 'N' && !self.byte_mode && self.now() == Some('{') {
            self.at += 1;
            while self.now().is_some() && self.now() != Some('}') {
                self.at += 1;
            }
            if self.take() != Some('}') {
                return self.fail("missing }, unterminated name".into(), Some(slash + 2), true);
            }
            if let Some((_, value)) = self.named.iter().find(|(position, _)| *position == slash) {
                return Ok(Expr::Lit(*value, flags));
            }
            return self.fail("undefined character name".into(), Some(slash), true);
        }
        if ch.is_ascii_digit() {
            let mut digits = String::from(ch);
            if ch == '0' || in_class {
                while digits.len() < 3 && self.now().is_some_and(|v| matches!(v, '0'..='7')) {
                    digits.push(self.take().unwrap());
                }
                return Ok(Expr::Lit(u32::from_str_radix(&digits, 8).unwrap(), flags));
            }
            if self.now().is_some_and(|v| v.is_ascii_digit()) {
                digits.push(self.take().unwrap());
            }
            let number: usize = digits.parse().unwrap();
            if number > self.groups {
                return self.fail(
                    format!("invalid group reference {}", number),
                    Some(slash + 1),
                    true,
                );
            }
            return Ok(Expr::Backref(number, flags));
        }
        if ch.is_ascii_alphabetic() {
            return self.fail(format!("bad escape \\{}", ch), Some(slash), true);
        }
        Ok(Expr::Lit(ch as u32, flags))
    }
    fn class(&mut self, flags: u32, start: usize) -> PResult<Expr> {
        let negate = self.now() == Some('^');
        if negate {
            self.at += 1;
        }
        let mut first = true;
        let mut values = Vec::new();
        loop {
            let Some(ch) = self.now() else {
                return self.fail("unterminated character set".into(), Some(start), true);
            };
            if ch == ']' && !first {
                self.at += 1;
                return Ok(Expr::Class(values, negate, flags));
            }
            first = false;
            let left = if ch == '\\' {
                let slash = self.at;
                self.at += 1;
                self.escape(flags, true, slash)?
            } else {
                self.at += 1;
                Expr::Lit(ch as u32, flags)
            };
            if self.now() == Some('-')
                && self.at + 1 < self.source.len()
                && self.source[self.at + 1] != b']' as u32
            {
                let dash = self.at;
                self.at += 1;
                let right = if self.now() == Some('\\') {
                    let slash = self.at;
                    self.at += 1;
                    self.escape(flags, true, slash)?
                } else {
                    Expr::Lit(self.take().unwrap() as u32, flags)
                };
                let (Expr::Lit(a, _), Expr::Lit(b, _)) = (left, right) else {
                    return self.fail("bad character range".into(), Some(dash), true);
                };
                if a > b {
                    return self.fail(
                        format!(
                            "bad character range {}-{}",
                            char::from_u32(a).unwrap(),
                            char::from_u32(b).unwrap()
                        ),
                        Some(dash - 1),
                        true,
                    );
                }
                values.push(Member::Range(a, b));
            } else {
                match left {
                    Expr::Lit(a, _) => values.push(Member::Lit(a)),
                    Expr::Cat(c, _) => values.push(Member::Cat(c)),
                    _ => unreachable!(),
                }
            }
        }
    }
    fn name(&mut self, terminator: char, position: usize) -> PResult<String> {
        let mut close = self.at;
        while close < self.source.len() && self.source[close] != terminator as u32 {
            close += 1;
        }
        if close == self.source.len() {
            return self.fail(
                format!("missing {}, unterminated name", terminator),
                Some(position),
                true,
            );
        }
        let raw = &self.source[self.at..close];
        self.at = close + 1;
        if raw.is_empty() {
            return self.fail("missing group name".into(), Some(position), true);
        }
        let value: String = raw.iter().filter_map(|v| char::from_u32(*v)).collect();
        let valid = value.chars().enumerate().all(|(i, ch)| {
            if i == 0 {
                ch == '_' || ch.is_alphabetic()
            } else {
                ch == '_' || ch.is_alphanumeric()
            }
        });
        if !valid || (self.byte_mode && raw.iter().any(|v| *v > 127)) {
            let shown = if self.byte_mode {
                raw.iter()
                    .map(|v| {
                        if *v < 128 {
                            char::from_u32(*v).unwrap().to_string()
                        } else {
                            format!("\\x{:02x}", v)
                        }
                    })
                    .collect::<String>()
            } else {
                value.clone()
            };
            return self.fail(
                format!("bad character in group name '{}'", shown),
                Some(position),
                true,
            );
        }
        Ok(value)
    }
    fn group(&mut self, flags: u32, start: usize) -> PResult<Expr> {
        if self.now() != Some('?') {
            self.groups += 1;
            let number = self.groups;
            let child = self.alt(flags)?;
            if self.take() != Some(')') {
                return self.fail(
                    "missing ), unterminated subpattern".into(),
                    Some(start),
                    true,
                );
            }
            self.widths.push((number, width(&child, &self.widths)));
            return Ok(Expr::Group(number, Box::new(child)));
        }
        self.at += 1;
        let Some(kind) = self.take() else {
            return self.fail("unexpected end of pattern".into(), Some(start), true);
        };
        match kind {
            ':' => {
                let child = self.alt(flags)?;
                if self.take() != Some(')') {
                    return self.fail(
                        "missing ), unterminated subpattern".into(),
                        Some(start),
                        true,
                    );
                }
                Ok(child)
            }
            '=' | '!' => {
                let child = self.alt(flags)?;
                if self.take() != Some(')') {
                    return self.fail(
                        "missing ), unterminated subpattern".into(),
                        Some(start),
                        true,
                    );
                }
                Ok(Expr::Look(false, kind == '=', Box::new(child), 0))
            }
            '<' if matches!(self.now(), Some('=' | '!')) => {
                let positive = self.take() == Some('=');
                let child = self.alt(flags)?;
                if self.take() != Some(')') {
                    return self.fail(
                        "missing ), unterminated subpattern".into(),
                        Some(start),
                        true,
                    );
                }
                let (low, high) = width(&child, &self.widths);
                if low != high {
                    return self.fail(
                        "look-behind requires fixed-width pattern".into(),
                        None,
                        false,
                    );
                }
                Ok(Expr::Look(true, positive, Box::new(child), low))
            }
            '>' => {
                let child = self.alt(flags)?;
                if self.take() != Some(')') {
                    return self.fail(
                        "missing ), unterminated subpattern".into(),
                        Some(start),
                        true,
                    );
                }
                Ok(Expr::Atomic(Box::new(child)))
            }
            '#' => {
                while self.now().is_some() && self.now() != Some(')') {
                    self.at += 1;
                }
                if self.take() != Some(')') {
                    return self.fail("missing ), unterminated comment".into(), Some(start), true);
                }
                Ok(Expr::Seq(vec![]))
            }
            'P' => {
                let Some(form) = self.take() else {
                    return self.fail("unknown extension ?P".into(), Some(start + 1), true);
                };
                if form == '<' {
                    let position = self.at;
                    let name = self.name('>', position)?;
                    self.groups += 1;
                    let number = self.groups;
                    if let Some((_, old)) = self.names.iter().find(|(value, _)| *value == name) {
                        return self.fail(
                            format!(
                                "redefinition of group name '{}' as group {}; was group {}",
                                name, number, old
                            ),
                            Some(position),
                            true,
                        );
                    }
                    self.names.push((name, number));
                    let child = self.alt(flags)?;
                    if self.take() != Some(')') {
                        return self.fail(
                            "missing ), unterminated subpattern".into(),
                            Some(start),
                            true,
                        );
                    }
                    self.widths.push((number, width(&child, &self.widths)));
                    Ok(Expr::Group(number, Box::new(child)))
                } else if form == '=' {
                    let position = self.at;
                    let name = self.name(')', position)?;
                    let Some((_, number)) = self.names.iter().find(|(value, _)| *value == name)
                    else {
                        return self.fail(
                            format!("unknown group name '{}'", name),
                            Some(position),
                            true,
                        );
                    };
                    Ok(Expr::Backref(*number, flags))
                } else {
                    self.fail("unknown extension ?P".into(), Some(start + 1), true)
                }
            }
            '(' => {
                let position = self.at;
                let mut close = self.at;
                while close < self.source.len() && self.source[close] != b')' as u32 {
                    close += 1;
                }
                if close == self.source.len() {
                    return self.fail("missing ), unterminated name".into(), Some(position), true);
                }
                let reference: String = self.source[self.at..close]
                    .iter()
                    .filter_map(|v| char::from_u32(*v))
                    .collect();
                self.at = close + 1;
                let number = if reference.chars().all(|v| v.is_ascii_digit()) {
                    let value: usize = reference.parse().unwrap();
                    if value < 1 || value > self.groups {
                        return self.fail(
                            format!("invalid group reference {}", value),
                            Some(position),
                            true,
                        );
                    }
                    value
                } else {
                    let Some((_, value)) = self.names.iter().find(|(name, _)| *name == reference)
                    else {
                        return self.fail(
                            format!("unknown group name '{}'", reference),
                            Some(position),
                            true,
                        );
                    };
                    *value
                };
                let yes = self.seq(flags)?;
                let no = if self.now() == Some('|') {
                    self.at += 1;
                    self.seq(flags)?
                } else {
                    Expr::Seq(vec![])
                };
                if self.take() != Some(')') {
                    return self.fail(
                        "missing ), unterminated subpattern".into(),
                        Some(start),
                        true,
                    );
                }
                Ok(Expr::Cond(number, Box::new(yes), Box::new(no)))
            }
            ch if "aiLmsux-".contains(ch) => {
                self.at -= 1;
                let mut on = 0;
                let mut off = 0;
                let mut removing = false;
                while self.now().is_some() && !matches!(self.now(), Some(':' | ')')) {
                    let value = self.take().unwrap();
                    if value == '-' {
                        removing = true;
                        continue;
                    }
                    let flag = match value {
                        'a' => A,
                        'i' => I,
                        'L' => L,
                        'm' => M,
                        's' => S,
                        'u' => 32,
                        'x' => X,
                        _ => {
                            return self.fail(
                                format!("unknown flag '{}'", value),
                                Some(self.at - 1),
                                true,
                            );
                        }
                    };
                    if removing {
                        if matches!(value, 'a' | 'u' | 'L') {
                            return self.fail(
                                "bad inline flags: cannot turn off flags 'a', 'u' and 'L'".into(),
                                Some(self.at),
                                true,
                            );
                        }
                        off |= flag;
                    } else {
                        if value == 'L' && !self.byte_mode {
                            return self.fail(
                                "bad inline flags: cannot use 'L' flag with a str pattern".into(),
                                Some(self.at),
                                true,
                            );
                        }
                        if matches!(value, 'a' | 'u' | 'L') && on & (A | L | 32) != 0 {
                            return self.fail(
                                "bad inline flags: flags 'a', 'u' and 'L' are incompatible".into(),
                                Some(self.at),
                                true,
                            );
                        }
                        on |= flag;
                    }
                }
                if on & off != 0 {
                    return self.fail(
                        "bad inline flags: flag turned on and off".into(),
                        Some(self.at),
                        true,
                    );
                }
                let changed = (flags | on) & !off;
                let Some(end) = self.take() else {
                    return self.fail("missing -, : or )".into(), Some(self.at), true);
                };
                if end == ')' {
                    if start != 0 {
                        return self.fail(
                            "global flags not at the start of the expression".into(),
                            Some(start),
                            true,
                        );
                    }
                    self.flags = changed;
                    Ok(Expr::Seq(vec![]))
                } else {
                    let child = self.alt(changed)?;
                    if self.take() != Some(')') {
                        return self.fail(
                            "missing ), unterminated subpattern".into(),
                            Some(start),
                            true,
                        );
                    }
                    Ok(child)
                }
            }
            _ => self.fail(
                format!("unknown extension ?{}", kind),
                Some(start + 1),
                true,
            ),
        }
    }
}

fn width(node: &Expr, groups: &[(usize, (usize, usize))]) -> (usize, usize) {
    match node {
        Expr::Lit(_, _) | Expr::Dot(_) | Expr::Cat(_, _) | Expr::Class(_, _, _) => (1, 1),
        Expr::Anchor(_, _) | Expr::Boundary(_, _) | Expr::Look(_, _, _, _) => (0, 0),
        Expr::Backref(number, _) => groups
            .iter()
            .find(|(item, _)| item == number)
            .map_or((0, usize::MAX / 8), |(_, value)| *value),
        Expr::Group(_, child) | Expr::Atomic(child) => width(child, groups),
        Expr::Seq(values) => values
            .iter()
            .map(|item| width(item, groups))
            .fold((0, 0), |(a, b), (c, d)| {
                (a.saturating_add(c), b.saturating_add(d))
            }),
        Expr::Alt(values) => values
            .iter()
            .map(|item| width(item, groups))
            .fold((usize::MAX, 0), |(a, b), (c, d)| (a.min(c), b.max(d))),
        Expr::Cond(_, yes, no) => {
            let a = width(yes, groups);
            let b = width(no, groups);
            (a.0.min(b.0), a.1.max(b.1))
        }
        Expr::Repeat(child, min, max, _) => {
            let value = width(child, groups);
            (
                value.0.saturating_mul(*min),
                max.map_or(usize::MAX / 8, |v| value.1.saturating_mul(v)),
            )
        }
    }
}

fn folded(value: u32, flags: u32, ctx: &Context<'_>, pos: usize) -> u32 {
    if flags & (A | L | BYTE) != 0 {
        if value < 128 {
            value.to_ascii_lowercase()
        } else {
            value
        }
    } else {
        ctx.folds[pos]
    }
}
trait LowerAscii {
    fn to_ascii_lowercase(self) -> Self;
}
impl LowerAscii for u32 {
    fn to_ascii_lowercase(self) -> Self {
        if (b'A' as u32..=b'Z' as u32).contains(&self) {
            self + 32
        } else {
            self
        }
    }
}
fn eq(a: u32, b: u32, flags: u32, ctx: &Context<'_>, apos: usize, bpos: usize) -> bool {
    if flags & I == 0 {
        a == b
    } else {
        folded(a, flags, ctx, apos) == folded(b, flags, ctx, bpos)
    }
}
fn eq_lit(lit: u32, value: u32, flags: u32, ctx: &Context<'_>, pos: usize) -> bool {
    if flags & I == 0 {
        lit == value
    } else {
        let left = if flags & (A | L | BYTE) != 0 {
            lit.to_ascii_lowercase()
        } else {
            match lit {
                0x130 | 0x131 => b'i' as u32,
                0x17f => b's' as u32,
                0x212a => b'k' as u32,
                _ => char::from_u32(lit)
                    .and_then(|c| c.to_lowercase().next())
                    .map_or(lit, |c| c as u32),
            }
        };
        left == folded(value, flags, ctx, pos)
    }
}
fn category(code: char, flags: u32, ctx: &Context<'_>, pos: usize) -> bool {
    let value = ctx.chars[pos];
    let ascii = flags & (A | L | BYTE) != 0;
    let result = match code.to_ascii_lowercase() {
        'd' => {
            if ascii {
                value >= b'0' as u32 && value <= b'9' as u32
            } else {
                ctx.masks[pos] & 1 != 0
            }
        }
        's' => {
            if ascii {
                matches!(value, 9 | 10 | 11 | 12 | 13 | 32)
            } else {
                ctx.masks[pos] & 2 != 0
            }
        }
        _ => {
            if ascii {
                value < 128
                    && ((value >= b'0' as u32 && value <= b'9' as u32)
                        || (value >= b'A' as u32 && value <= b'Z' as u32)
                        || (value >= b'a' as u32 && value <= b'z' as u32)
                        || value == b'_' as u32)
            } else {
                ctx.masks[pos] & 4 != 0 || value == b'_' as u32
            }
        }
    };
    if code.is_ascii_uppercase() {
        !result
    } else {
        result
    }
}
fn class_match(
    values: &[Member],
    negative: bool,
    flags: u32,
    ctx: &Context<'_>,
    pos: usize,
) -> bool {
    let value = ctx.chars[pos];
    let found = values.iter().any(|item| match *item {
        Member::Lit(ch) => eq_lit(ch, value, flags, ctx, pos),
        Member::Cat(ch) => category(ch, flags, ctx, pos),
        Member::Range(left, right) => {
            (left <= value && value <= right)
                || (flags & I != 0 && {
                    let folded_value = folded(value, flags, ctx, pos);
                    let low = if flags & (A | L | BYTE) != 0 {
                        left.to_ascii_lowercase()
                    } else {
                        char::from_u32(left)
                            .and_then(|c| c.to_lowercase().next())
                            .map_or(left, |c| c as u32)
                    };
                    let high = if flags & (A | L | BYTE) != 0 {
                        right.to_ascii_lowercase()
                    } else {
                        char::from_u32(right)
                            .and_then(|c| c.to_lowercase().next())
                            .map_or(right, |c| c as u32)
                    };
                    low <= folded_value && folded_value <= high
                })
        }
    });
    if negative { !found } else { found }
}

fn eval(node: &Expr, state: &State, ctx: &Context<'_>) -> Vec<State> {
    match node {
        Expr::Lit(value, flags) => {
            if state.pos < ctx.end && eq_lit(*value, ctx.chars[state.pos], *flags, ctx, state.pos) {
                let mut next = state.clone();
                next.pos += 1;
                vec![next]
            } else {
                vec![]
            }
        }
        Expr::Dot(flags) => {
            if state.pos < ctx.end && (*flags & S != 0 || ctx.chars[state.pos] != 10) {
                let mut next = state.clone();
                next.pos += 1;
                vec![next]
            } else {
                vec![]
            }
        }
        Expr::Cat(code, flags) => {
            if state.pos < ctx.end && category(*code, *flags, ctx, state.pos) {
                let mut next = state.clone();
                next.pos += 1;
                vec![next]
            } else {
                vec![]
            }
        }
        Expr::Class(values, negative, flags) => {
            if state.pos < ctx.end && class_match(values, *negative, *flags, ctx, state.pos) {
                let mut next = state.clone();
                next.pos += 1;
                vec![next]
            } else {
                vec![]
            }
        }
        Expr::Anchor(code, flags) => {
            let okay = match *code {
                '^' => {
                    state.pos == 0
                        || (*flags & M != 0 && state.pos > 0 && ctx.chars[state.pos - 1] == 10)
                }
                '$' => {
                    state.pos == ctx.end
                        || (state.pos + 1 == ctx.end && ctx.chars.get(state.pos) == Some(&10))
                        || (*flags & M != 0 && state.pos < ctx.end && ctx.chars[state.pos] == 10)
                }
                'A' => state.pos == 0,
                _ => state.pos == ctx.end,
            };
            if okay { vec![state.clone()] } else { vec![] }
        }
        Expr::Boundary(want, flags) => {
            let left = state.pos > 0 && category('w', *flags, ctx, state.pos - 1);
            let right = state.pos < ctx.end && category('w', *flags, ctx, state.pos);
            if (left != right) == *want {
                vec![state.clone()]
            } else {
                vec![]
            }
        }
        Expr::Seq(values) => {
            let mut current = vec![state.clone()];
            for item in values {
                current = current
                    .iter()
                    .flat_map(|value| eval(item, value, ctx))
                    .collect();
                if current.is_empty() {
                    break;
                }
            }
            current
        }
        Expr::Alt(values) => values
            .iter()
            .flat_map(|value| eval(value, state, ctx))
            .collect(),
        Expr::Group(number, child) => eval(child, state, ctx)
            .into_iter()
            .map(|mut value| {
                value.caps[*number] = Some((state.pos, value.pos));
                value.last = Some(*number);
                value
            })
            .collect(),
        Expr::Backref(number, flags) => {
            let Some((begin, end)) = state.caps[*number] else {
                return vec![];
            };
            let count = end - begin;
            if state.pos + count > ctx.end {
                return vec![];
            };
            if (0..count).all(|off| {
                eq(
                    ctx.chars[begin + off],
                    ctx.chars[state.pos + off],
                    *flags,
                    ctx,
                    begin + off,
                    state.pos + off,
                )
            }) {
                let mut next = state.clone();
                next.pos += count;
                vec![next]
            } else {
                vec![]
            }
        }
        Expr::Repeat(child, min, max, mode) => {
            fn walk(
                child: &Expr,
                state: &State,
                count: usize,
                min: usize,
                max: usize,
                mode: u8,
                ctx: &Context<'_>,
                out: &mut Vec<State>,
            ) {
                if mode == 1 && count >= min {
                    out.push(state.clone());
                }
                if count < max {
                    for next in eval(child, state, ctx) {
                        if next.pos == state.pos {
                            if count + 1 < min {
                                walk(child, &next, count + 1, min, max, mode, ctx, out);
                            } else {
                                out.push(next);
                            }
                            continue;
                        }
                        walk(child, &next, count + 1, min, max, mode, ctx, out);
                    }
                }
                if mode != 1 && count >= min {
                    out.push(state.clone());
                }
            }
            let limit = max.unwrap_or_else(|| ctx.end - state.pos + min + 1);
            let mut result = Vec::new();
            walk(child, state, 0, *min, limit, *mode, ctx, &mut result);
            if *mode == 2 {
                result.into_iter().take(1).collect()
            } else {
                result
            }
        }
        Expr::Look(behind, positive, child, width) => {
            let mut seed = state.clone();
            if *behind {
                if state.pos < *width {
                    return if *positive {
                        vec![]
                    } else {
                        vec![state.clone()]
                    };
                };
                seed.pos = state.pos - *width;
            }
            let mut found = eval(child, &seed, ctx)
                .into_iter()
                .filter(|value| !*behind || value.pos == state.pos);
            let first = found.next();
            if *positive {
                if let Some(mut value) = first {
                    value.pos = state.pos;
                    vec![value]
                } else {
                    vec![]
                }
            } else if first.is_none() {
                vec![state.clone()]
            } else {
                vec![]
            }
        }
        Expr::Atomic(child) => eval(child, state, ctx).into_iter().take(1).collect(),
        Expr::Cond(number, yes, no) => eval(
            if state.caps[*number].is_some() {
                yes
            } else {
                no
            },
            state,
            ctx,
        ),
    }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn rebar_compile(
    pattern: *const u32,
    length: usize,
    flags: u32,
    byte_mode: u8,
    named_positions: *const usize,
    named_values: *const u32,
    named_count: usize,
) -> *mut Engine {
    if pattern.is_null() {
        set_error("null pattern".into(), None, false);
        return std::ptr::null_mut();
    }
    let source = unsafe { slice::from_raw_parts(pattern, length) }.to_vec();
    let named = if named_count == 0 {
        vec![]
    } else if named_positions.is_null() || named_values.is_null() {
        set_error("null named-escape table".into(), None, false);
        return std::ptr::null_mut();
    } else {
        unsafe { slice::from_raw_parts(named_positions, named_count) }
            .iter()
            .copied()
            .zip(
                unsafe { slice::from_raw_parts(named_values, named_count) }
                    .iter()
                    .copied(),
            )
            .collect()
    };
    let mut parser = Parser {
        source,
        at: 0,
        flags: flags | if byte_mode != 0 { BYTE } else { 0 },
        byte_mode: byte_mode != 0,
        groups: 0,
        names: vec![],
        widths: vec![],
        named,
    };
    match parser.parse() {
        Ok(root) => {
            set_error(String::new(), None, false);
            Box::into_raw(Box::new(Engine {
                root,
                groups: parser.groups,
                names: parser.names,
                flags: parser.flags & !BYTE,
            }))
        }
        Err((msg, pos, include)) => {
            set_error(msg, pos, include);
            std::ptr::null_mut()
        }
    }
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn rebar_free(handle: *mut Engine) {
    if !handle.is_null() {
        drop(unsafe { Box::from_raw(handle) });
    }
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn rebar_groups(handle: *const Engine) -> usize {
    if handle.is_null() {
        0
    } else {
        unsafe { (*handle).groups }
    }
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn rebar_flags(handle: *const Engine) -> u32 {
    if handle.is_null() {
        0
    } else {
        unsafe { (*handle).flags }
    }
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn rebar_name_count(handle: *const Engine) -> usize {
    if handle.is_null() {
        0
    } else {
        unsafe { (*handle).names.len() }
    }
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn rebar_name_len(handle: *const Engine, index: usize) -> usize {
    if handle.is_null() {
        0
    } else {
        unsafe {
            (&(*handle).names)
                .get(index)
                .map_or(0, |value| value.0.len())
        }
    }
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn rebar_name_group(handle: *const Engine, index: usize) -> usize {
    if handle.is_null() {
        0
    } else {
        unsafe { (&(*handle).names).get(index).map_or(0, |value| value.1) }
    }
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn rebar_name_copy(
    handle: *const Engine,
    index: usize,
    out: *mut u8,
    length: usize,
) -> usize {
    if handle.is_null() || out.is_null() {
        return 0;
    }
    let Some(value) = (unsafe { (&(*handle).names).get(index) }) else {
        return 0;
    };
    let count = value.0.len().min(length);
    unsafe { std::ptr::copy_nonoverlapping(value.0.as_ptr(), out, count) };
    count
}
#[unsafe(no_mangle)]
pub extern "C" fn rebar_error_len() -> usize {
    LAST.with(|value| value.borrow().0.len())
}
#[unsafe(no_mangle)]
pub extern "C" fn rebar_error_pos() -> isize {
    LAST.with(|value| value.borrow().1)
}
#[unsafe(no_mangle)]
pub extern "C" fn rebar_error_include() -> u8 {
    LAST.with(|value| u8::from(value.borrow().2))
}
#[unsafe(no_mangle)]
pub unsafe extern "C" fn rebar_error_copy(out: *mut u8, length: usize) -> usize {
    if out.is_null() {
        return 0;
    }
    LAST.with(|value| {
        let borrow = value.borrow();
        let count = borrow.0.len().min(length);
        unsafe { std::ptr::copy_nonoverlapping(borrow.0.as_ptr(), out, count) };
        count
    })
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn rebar_match(
    handle: *const Engine,
    chars: *const u32,
    folds: *const u32,
    masks: *const u8,
    length: usize,
    pos: usize,
    endpos: usize,
    mode: u8,
    nonempty: u8,
    begins: *mut isize,
    ends: *mut isize,
    last: *mut isize,
) -> i32 {
    if handle.is_null()
        || chars.is_null()
        || folds.is_null()
        || masks.is_null()
        || begins.is_null()
        || ends.is_null()
        || last.is_null()
    {
        return -1;
    }
    let engine = unsafe { &*handle };
    let context = Context {
        chars: unsafe { slice::from_raw_parts(chars, length) },
        folds: unsafe { slice::from_raw_parts(folds, length) },
        masks: unsafe { slice::from_raw_parts(masks, length) },
        end: endpos.min(length),
    };
    let begins = unsafe { slice::from_raw_parts_mut(begins, engine.groups + 1) };
    let ends = unsafe { slice::from_raw_parts_mut(ends, engine.groups + 1) };
    if pos > context.end {
        return 0;
    }
    let last_start = if mode == 0 { context.end } else { pos };
    for start in pos..=last_start {
        let state = State {
            pos: start,
            caps: vec![None; engine.groups + 1],
            last: None,
        };
        for value in eval(&engine.root, &state, &context) {
            if mode == 2 && value.pos != context.end {
                continue;
            }
            if nonempty != 0 && start == pos && value.pos == start {
                continue;
            }
            begins.fill(-1);
            ends.fill(-1);
            begins[0] = start as isize;
            ends[0] = value.pos as isize;
            for (number, span) in value.caps.iter().enumerate().skip(1) {
                if let Some((a, b)) = span {
                    begins[number] = *a as isize;
                    ends[number] = *b as isize;
                }
            }
            unsafe { *last = value.last.map_or(-1, |v| v as isize) };
            return 1;
        }
    }
    0
}
