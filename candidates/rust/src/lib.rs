use std::cell::RefCell;
use std::slice;

const I: u32 = 2;
const L: u32 = 4;
const M: u32 = 8;
const S: u32 = 16;
const X: u32 = 64;
const A: u32 = 256;
const BYTE: u32 = 1 << 31;

#[derive(Clone)]
enum Member {
    Lit(u32),
    Range(u32, u32),
    Cat(char),
    Table([u64; 2]),
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
    starts: Option<[u8; 256]>,
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
    bytes: Option<&'a [u8]>,
    end: usize,
}

impl Context<'_> {
    #[inline]
    fn character(&self, pos: usize) -> u32 {
        self.bytes
            .map_or_else(|| self.chars[pos], |values| u32::from(values[pos]))
    }

    #[inline]
    fn fold(&self, pos: usize) -> u32 {
        self.bytes.map_or_else(
            || self.folds[pos],
            |values| u32::from(values[pos].to_ascii_lowercase()),
        )
    }

    #[inline]
    fn mask(&self, pos: usize) -> u8 {
        self.bytes.map_or_else(
            || self.masks[pos],
            |values| {
                let value = values[pos];
                u8::from(value.is_ascii_digit())
                    | (u8::from(matches!(value, 9 | 10 | 11 | 12 | 13 | 32)) << 1)
                    | (u8::from(value.is_ascii_alphanumeric()) << 2)
            },
        )
    }
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
    global_allowed: bool,
    group_depth: usize,
    open_groups: Vec<usize>,
    lookbehind_bases: Vec<usize>,
    pending_conditionals: Vec<(usize, usize)>,
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
    fn global_group(&self, start: usize) -> bool {
        if self.source.get(start) != Some(&(b'(' as u32))
            || self.source.get(start + 1) != Some(&(b'?' as u32))
        {
            return false;
        }
        let mut cursor = start + 2;
        while let Some(value) = self.source.get(cursor).copied().and_then(char::from_u32) {
            if matches!(value, 'a' | 'i' | 'L' | 'm' | 's' | 'u' | 'x' | '-') {
                cursor += 1;
                continue;
            }
            return value == ')';
        }
        false
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
        if let Some((number, position)) = self
            .pending_conditionals
            .iter()
            .find(|(number, _)| *number > self.groups)
        {
            return self.fail(
                format!("invalid group reference {}", number),
                Some(*position),
                true,
            );
        }
        Ok(result)
    }
    fn alt(&mut self, flags: u32) -> PResult<Expr> {
        let mut branches = vec![self.seq(flags)?];
        while self.now() == Some('|') {
            self.global_allowed = false;
            self.at += 1;
            let branch_flags = if self.group_depth == 0 {
                self.flags
            } else {
                flags
            };
            branches.push(self.seq(branch_flags)?);
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
            if self.global_group(start)
                && (matches!(self.now(), Some('*' | '+' | '?')) || self.brace_repeat(self.at))
            {
                return self.fail("nothing to repeat".into(), Some(self.at), true);
            }
            node = self.repeat(node, flags)?;
            if let Expr::Seq(ref values) = node {
                if values.is_empty()
                    && self.at > start
                    && self.source.get(start + 1) == Some(&(b'?' as u32))
                    && self.global_group(start)
                {
                    if self.group_depth != 0 || !self.global_allowed {
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
            let comment = matches!(&node, Expr::Seq(values) if values.is_empty())
                && self.source.get(start + 1) == Some(&(b'?' as u32))
                && self.source.get(start + 2) == Some(&(b'#' as u32));
            if !comment {
                self.global_allowed = false;
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
                let parse_number = |text: &str| {
                    text.parse::<usize>()
                        .ok()
                        .filter(|value| *value < 0xffff_ffff)
                        .ok_or_else(|| ("the repetition number is too large".into(), None, false))
                };
                let pair = if let Some((left, right)) = spec.split_once(',') {
                    (
                        if left.is_empty() {
                            0
                        } else {
                            parse_number(left)?
                        },
                        if right.is_empty() {
                            None
                        } else {
                            Some(parse_number(right)?)
                        },
                    )
                } else {
                    let n = parse_number(&spec)?;
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
        if matches!(self.now(), Some('*' | '+' | '?')) || self.brace_repeat(self.at) {
            return self.fail("multiple repeat".into(), Some(self.at), true);
        }
        let _ = flags;
        Ok(Expr::Repeat(Box::new(node), min, max, mode))
    }
    fn brace_repeat(&self, position: usize) -> bool {
        if self.source.get(position) != Some(&(b'{' as u32)) {
            return false;
        }
        let mut close = position + 1;
        let mut commas = 0;
        while close < self.source.len() && self.source[close] != b'}' as u32 {
            match char::from_u32(self.source[close]) {
                Some('0'..='9') => {}
                Some(',') => commas += 1,
                _ => return false,
            }
            close += 1;
        }
        close < self.source.len() && close > position + 1 && commas <= 1
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
            '{' if self.brace_repeat(start) => {
                self.fail("nothing to repeat".into(), Some(start), true)
            }
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
            let end = (self.at + 2).min(self.source.len());
            let text: String = self.source[self.at..end]
                .iter()
                .filter_map(|v| char::from_u32(*v))
                .collect();
            let valid: String = text.chars().take_while(|v| v.is_ascii_hexdigit()).collect();
            if text.len() != 2 || valid.len() != 2 {
                return self.fail(format!("incomplete escape \\x{}", valid), Some(slash), true);
            }
            let Ok(value) = u32::from_str_radix(&text, 16) else {
                return self.fail(format!("incomplete escape \\x{}", valid), Some(slash), true);
            };
            self.at += 2;
            return Ok(Expr::Lit(value, flags));
        }
        if matches!(ch, 'u' | 'U') && !self.byte_mode {
            let count = if ch == 'u' { 4 } else { 8 };
            let end = (self.at + count).min(self.source.len());
            let text: String = self.source[self.at..end]
                .iter()
                .filter_map(|v| char::from_u32(*v))
                .collect();
            let valid: String = text.chars().take_while(|v| v.is_ascii_hexdigit()).collect();
            if text.len() != count || valid.len() != count {
                return self.fail(
                    format!("incomplete escape \\{}{}", ch, valid),
                    Some(slash),
                    true,
                );
            }
            let Ok(value) = u32::from_str_radix(&text, 16) else {
                return self.fail(
                    format!("incomplete escape \\{}{}", ch, valid),
                    Some(slash),
                    true,
                );
            };
            self.at += count;
            if value > 0x10ffff {
                return self.fail(format!("bad escape \\{}{}", ch, text), Some(slash), true);
            }
            return Ok(Expr::Lit(value, flags));
        }
        if ch == 'N' && !self.byte_mode {
            if self.now() != Some('{') {
                return self.fail("missing {".into(), Some(slash + 2), true);
            }
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
            let octal = ch == '0'
                || in_class
                || (matches!(ch, '1'..='7')
                    && self.at + 1 < self.source.len()
                    && matches!(char::from_u32(self.source[self.at]), Some('0'..='7'))
                    && matches!(char::from_u32(self.source[self.at + 1]), Some('0'..='7')));
            if octal {
                if !matches!(ch, '0'..='7') {
                    return self.fail(format!("bad escape \\{}", ch), Some(slash), true);
                }
                while digits.len() < 3 && self.now().is_some_and(|v| matches!(v, '0'..='7')) {
                    digits.push(self.take().unwrap());
                }
                let value = u32::from_str_radix(&digits, 8).unwrap();
                if value > 0o377 {
                    return self.fail(
                        format!("octal escape value \\{} outside of range 0-0o377", digits),
                        Some(slash),
                        true,
                    );
                }
                return Ok(Expr::Lit(value, flags));
            }
            if self.now().is_some_and(|v| v.is_ascii_digit()) {
                digits.push(self.take().unwrap());
            }
            let number: usize = digits.parse().unwrap();
            self.check_reference(number, slash, Some(slash + 1), false)?;
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
            let Some(raw) = self.source.get(self.at).copied() else {
                return self.fail("unterminated character set".into(), Some(start), true);
            };
            if raw == b']' as u32 && !first {
                self.at += 1;
                return Ok(Expr::Class(values, negate, flags));
            }
            first = false;
            let left_start = self.at;
            let left = if raw == b'\\' as u32 {
                let slash = self.at;
                self.at += 1;
                self.escape(flags, true, slash)?
            } else {
                self.at += 1;
                Expr::Lit(raw, flags)
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
                    let value = self.source[self.at];
                    self.at += 1;
                    Expr::Lit(value, flags)
                };
                let (Expr::Lit(a, _), Expr::Lit(b, _)) = (left, right) else {
                    let text: String = self.source[left_start..self.at]
                        .iter()
                        .filter_map(|v| char::from_u32(*v))
                        .collect();
                    return self.fail(
                        format!("bad character range {}", text),
                        Some(left_start),
                        true,
                    );
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
            if self.at == self.source.len() {
                return self.fail("missing group name".into(), Some(position), true);
            }
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
    fn check_reference(
        &mut self,
        number: usize,
        position: usize,
        invalid_position: Option<usize>,
        forward: bool,
    ) -> PResult<()> {
        if self
            .lookbehind_bases
            .iter()
            .min()
            .is_some_and(|base| number > *base)
        {
            if number <= self.groups {
                return self.fail(
                    "cannot refer to group defined in the same lookbehind subpattern".into(),
                    Some(position + 2),
                    true,
                );
            }
            return self.fail(
                "cannot refer to an open group".into(),
                Some(position + 2),
                true,
            );
        }
        if self.open_groups.contains(&number) {
            return self.fail("cannot refer to an open group".into(), Some(position), true);
        }
        if number > self.groups {
            let error_position = invalid_position.unwrap_or(position);
            if forward {
                self.pending_conditionals.push((number, error_position));
            } else {
                return self.fail(
                    format!("invalid group reference {}", number),
                    Some(error_position),
                    true,
                );
            }
        }
        Ok(())
    }
    fn group(&mut self, flags: u32, start: usize) -> PResult<Expr> {
        self.group_depth += 1;
        let result = self.group_inner(flags, start);
        self.group_depth -= 1;
        result
    }

    fn group_inner(&mut self, flags: u32, start: usize) -> PResult<Expr> {
        if self.now() != Some('?') {
            self.groups += 1;
            let number = self.groups;
            self.open_groups.push(number);
            let child = self.alt(flags)?;
            if self.take() != Some(')') {
                return self.fail(
                    "missing ), unterminated subpattern".into(),
                    Some(start),
                    true,
                );
            }
            self.widths.push((number, width(&child, &self.widths)));
            self.open_groups.pop();
            return Ok(Expr::Group(number, Box::new(child)));
        }
        self.at += 1;
        let Some(kind) = self.take() else {
            return self.fail("unexpected end of pattern".into(), Some(self.at), true);
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
                self.lookbehind_bases.push(self.groups);
                let child = self.alt(flags)?;
                if self.take() != Some(')') {
                    return self.fail(
                        "missing ), unterminated subpattern".into(),
                        Some(start),
                        true,
                    );
                }
                let (low, high) = width(&child, &self.widths);
                self.lookbehind_bases.pop();
                if low != high {
                    return self.fail(
                        "look-behind requires fixed-width pattern".into(),
                        None,
                        false,
                    );
                }
                if low > 0xffff_ffff {
                    return self.fail("looks too much behind".into(), None, false);
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
                    return self.fail("unexpected end of pattern".into(), Some(self.at), true);
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
                    self.open_groups.push(number);
                    let child = self.alt(flags)?;
                    if self.take() != Some(')') {
                        return self.fail(
                            "missing ), unterminated subpattern".into(),
                            Some(start),
                            true,
                        );
                    }
                    self.widths.push((number, width(&child, &self.widths)));
                    self.open_groups.pop();
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
                    let number = *number;
                    self.check_reference(number, position, None, false)?;
                    Ok(Expr::Backref(number, flags))
                } else {
                    self.fail(
                        format!("unknown extension ?P{}", form),
                        Some(start + 1),
                        true,
                    )
                }
            }
            '(' => {
                let position = self.at;
                let mut close = self.at;
                while close < self.source.len() && self.source[close] != b')' as u32 {
                    close += 1;
                }
                if close == self.source.len() {
                    if self.at == self.source.len() {
                        return self.fail("missing group name".into(), Some(position), true);
                    }
                    return self.fail("missing ), unterminated name".into(), Some(position), true);
                }
                let reference: String = self.source[self.at..close]
                    .iter()
                    .filter_map(|v| char::from_u32(*v))
                    .collect();
                self.at = close + 1;
                if reference.is_empty() {
                    return self.fail("missing group name".into(), Some(position), true);
                }
                let number = if reference.chars().all(|v| v.is_ascii_digit()) {
                    let value: usize = reference.parse().unwrap();
                    if value == 0 {
                        return self.fail("bad group number".into(), Some(position), true);
                    }
                    self.check_reference(value, position, None, true)?;
                    value
                } else {
                    let valid = reference.chars().enumerate().all(|(index, value)| {
                        if index == 0 {
                            value == '_' || value.is_alphabetic()
                        } else {
                            value == '_' || value.is_alphanumeric()
                        }
                    }) && (!self.byte_mode || reference.is_ascii());
                    if !valid {
                        let shown = if self.byte_mode {
                            reference
                                .chars()
                                .map(|value| {
                                    if value.is_ascii() {
                                        value.to_string()
                                    } else {
                                        format!("\\x{:02x}", value as u32)
                                    }
                                })
                                .collect::<String>()
                        } else {
                            reference.clone()
                        };
                        return self.fail(
                            format!("bad character in group name '{}'", shown),
                            Some(position),
                            true,
                        );
                    }
                    let Some((_, value)) = self.names.iter().find(|(name, _)| *name == reference)
                    else {
                        return self.fail(
                            format!("unknown group name '{}'", reference),
                            Some(position),
                            true,
                        );
                    };
                    let value = *value;
                    self.check_reference(value, position, None, false)?;
                    value
                };
                let yes = self.seq(flags)?;
                let no = if self.now() == Some('|') {
                    self.at += 1;
                    self.seq(flags)?
                } else {
                    Expr::Seq(vec![])
                };
                if self.now() == Some('|') {
                    return self.fail(
                        "conditional backref with more than two branches".into(),
                        Some(self.at),
                        true,
                    );
                }
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
                            if removing && off == 0 && matches!(value, '+' | '*' | '?' | '{') {
                                return self.fail("missing flag".into(), Some(self.at - 1), true);
                            }
                            if removing && matches!(value, '+' | '*' | '?' | '{') {
                                return self.fail("missing :".into(), Some(self.at - 1), true);
                            }
                            if !removing && matches!(value, '+' | '*' | '?' | '{') {
                                return self.fail(
                                    "missing -, : or )".into(),
                                    Some(self.at - 1),
                                    true,
                                );
                            }
                            return self.fail("unknown flag".into(), Some(self.at - 1), true);
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
                        if value == 'u' && self.byte_mode {
                            return self.fail(
                                "bad inline flags: cannot use 'u' flag with a bytes pattern".into(),
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
                let mut changed = (flags | on) & !off;
                if on & (A | L) != 0 {
                    changed &= !32;
                } else if on & 32 != 0 {
                    changed &= !(A | L);
                }
                let Some(end) = self.take() else {
                    if removing && off == 0 {
                        return self.fail("missing flag".into(), Some(self.at), true);
                    }
                    if removing {
                        return self.fail("missing :".into(), Some(self.at), true);
                    }
                    return self.fail("missing -, : or )".into(), Some(self.at), true);
                };
                if end == ')' {
                    if removing {
                        return self.fail("missing :".into(), Some(self.at - 1), true);
                    }
                    if self.group_depth != 1 || !self.global_allowed {
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
            '<' => match self.now() {
                None => self.fail("unexpected end of pattern".into(), Some(self.at), true),
                Some(value) => self.fail(
                    format!("unknown extension ?<{}", value),
                    Some(start + 1),
                    true,
                ),
            },
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
        ctx.fold(pos)
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
                0x1c80 => 0x432,
                0xfb05 | 0xfb06 => 0xfb05,
                0xdf | 0x1e9e => 0xdf,
                _ => char::from_u32(lit)
                    .and_then(|c| c.to_lowercase().next())
                    .map_or(lit, |c| c as u32),
            }
        };
        left == folded(value, flags, ctx, pos)
    }
}

fn range_case_match(
    left: u32,
    right: u32,
    value: u32,
    flags: u32,
    ctx: &Context<'_>,
    pos: usize,
) -> bool {
    if left <= value && value <= right {
        return true;
    }
    let ascii = flags & (A | L | BYTE) != 0;
    if ascii {
        let lower = value.to_ascii_lowercase();
        let upper = if (b'a' as u32..=b'z' as u32).contains(&value) {
            value - 32
        } else {
            value
        };
        return (left <= lower && lower <= right) || (left <= upper && upper <= right);
    }
    let lower = char::from_u32(value)
        .and_then(|c| c.to_lowercase().next())
        .map_or(value, |c| c as u32);
    let upper = char::from_u32(value)
        .and_then(|c| c.to_uppercase().next())
        .map_or(value, |c| c as u32);
    let fold = folded(value, flags, ctx, pos);
    if (left <= lower && lower <= right)
        || (left <= upper && upper <= right)
        || (left <= fold && fold <= right)
    {
        return true;
    }
    let closures: &[&[u32]] = &[
        &[b'I' as u32, b'i' as u32, 0x130, 0x131],
        &[b'S' as u32, b's' as u32, 0x17f],
        &[b'K' as u32, b'k' as u32, 0x212a],
        &[0x412, 0x432, 0x1c80],
        &[0xfb05, 0xfb06],
        &[0xdf, 0x1e9e],
    ];
    closures.iter().any(|closure| {
        closure.contains(&value) && closure.iter().any(|item| left <= *item && *item <= right)
    })
}
fn category(code: char, flags: u32, ctx: &Context<'_>, pos: usize) -> bool {
    let value = ctx.character(pos);
    let ascii = flags & (A | L | BYTE) != 0;
    let result = match code.to_ascii_lowercase() {
        'd' => {
            if ascii {
                value >= b'0' as u32 && value <= b'9' as u32
            } else {
                ctx.mask(pos) & 1 != 0
            }
        }
        's' => {
            if ascii {
                matches!(value, 9 | 10 | 11 | 12 | 13 | 32)
            } else {
                ctx.mask(pos) & 2 != 0
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
                ctx.mask(pos) & 4 != 0 || value == b'_' as u32
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
    let value = ctx.character(pos);
    if value < 128
        && let Some(Member::Table(table)) = values.first()
    {
        return table[(value / 64) as usize] & (1_u64 << (value % 64)) != 0;
    }
    if negative
        && flags & (I | L) == I | L
        && !(values.len() == 1 && matches!(values.first(), Some(Member::Lit(_))))
    {
        let other = if (b'A' as u32..=b'Z' as u32).contains(&value) {
            value + 32
        } else if (b'a' as u32..=b'z' as u32).contains(&value) {
            value - 32
        } else {
            value
        };
        let raw_found = |candidate| {
            values.iter().any(|item| match *item {
                Member::Lit(ch) => ch == candidate,
                Member::Cat(ch) => category(ch, flags & !I, ctx, pos),
                Member::Range(left, right) => left <= candidate && candidate <= right,
                Member::Table(_) => false,
            })
        };
        return !raw_found(value) || !raw_found(other);
    }
    let found = values.iter().any(|item| match *item {
        Member::Lit(ch) => eq_lit(ch, value, flags, ctx, pos),
        Member::Cat(ch) => category(ch, flags, ctx, pos),
        Member::Range(left, right) => {
            if flags & I != 0 {
                range_case_match(left, right, value, flags, ctx, pos)
            } else {
                left <= value && value <= right
            }
        }
        Member::Table(_) => false,
    });
    if negative { !found } else { found }
}

fn prepare_classes(node: &mut Expr, ctx: &Context<'_>) {
    match node {
        Expr::Class(values, negative, flags) => {
            let mut table = [0_u64; 2];
            for value in 0..128 {
                if class_match(values, *negative, *flags, ctx, value) {
                    table[value / 64] |= 1_u64 << (value % 64);
                }
            }
            values.insert(0, Member::Table(table));
        }
        Expr::Seq(values) | Expr::Alt(values) => {
            for value in values {
                prepare_classes(value, ctx);
            }
        }
        Expr::Group(_, child)
        | Expr::Repeat(child, _, _, _)
        | Expr::Look(_, _, child, _)
        | Expr::Atomic(child) => prepare_classes(child, ctx),
        Expr::Cond(_, yes, no) => {
            prepare_classes(yes, ctx);
            prepare_classes(no, ctx);
        }
        _ => {}
    }
}

fn repeat_layout(node: &Expr) -> Option<(&Expr, usize, Vec<(usize, usize, usize)>)> {
    match node {
        Expr::Lit(_, _) | Expr::Dot(_) | Expr::Cat(_, _) | Expr::Class(_, _, _) => {
            Some((node, 1, Vec::new()))
        }
        Expr::Seq(values) if values.len() == 1 => repeat_layout(&values[0]),
        Expr::Alt(values) => {
            for value in values {
                let (_, width, captures) = repeat_layout(value)?;
                if width != 1 || !captures.is_empty() {
                    return None;
                }
            }
            Some((node, 1, Vec::new()))
        }
        Expr::Group(number, child) => {
            let (leaf, width, mut captures) = repeat_layout(child)?;
            captures.push((*number, 0, width));
            Some((leaf, width, captures))
        }
        Expr::Repeat(child, minimum, Some(maximum), _) if minimum == maximum => {
            let (leaf, width, captures) = repeat_layout(child)?;
            let total = width.checked_mul(*minimum)?;
            let offset = if *minimum == 0 {
                0
            } else {
                width.checked_mul(*minimum - 1)?
            };
            Some((
                leaf,
                total,
                captures
                    .into_iter()
                    .map(|(number, begin, end)| (number, begin + offset, end + offset))
                    .collect(),
            ))
        }
        _ => None,
    }
}

fn advance_atom(node: &Expr, state: &mut State, ctx: &Context<'_>) -> bool {
    match node {
        Expr::Lit(value, flags) => {
            if state.pos < ctx.end
                && eq_lit(*value, ctx.character(state.pos), *flags, ctx, state.pos)
            {
                state.pos += 1;
                true
            } else {
                false
            }
        }
        Expr::Dot(flags) => {
            if state.pos < ctx.end && (*flags & S != 0 || ctx.character(state.pos) != 10) {
                state.pos += 1;
                true
            } else {
                false
            }
        }
        Expr::Cat(code, flags) => {
            if state.pos < ctx.end && category(*code, *flags, ctx, state.pos) {
                state.pos += 1;
                true
            } else {
                false
            }
        }
        Expr::Class(values, negative, flags) => {
            if state.pos < ctx.end && class_match(values, *negative, *flags, ctx, state.pos) {
                state.pos += 1;
                true
            } else {
                false
            }
        }
        Expr::Anchor(code, flags) => match *code {
            '^' => {
                state.pos == 0
                    || (*flags & M != 0 && state.pos > 0 && ctx.character(state.pos - 1) == 10)
            }
            '$' => {
                state.pos == ctx.end
                    || (state.pos + 1 == ctx.end
                        && state.pos < ctx.end
                        && ctx.character(state.pos) == 10)
                    || (*flags & M != 0 && state.pos < ctx.end && ctx.character(state.pos) == 10)
            }
            'A' => state.pos == 0,
            _ => state.pos == ctx.end,
        },
        Expr::Boundary(want, flags) => {
            let left = state.pos > 0 && category('w', *flags, ctx, state.pos - 1);
            let right = state.pos < ctx.end && category('w', *flags, ctx, state.pos);
            (left != right) == *want
        }
        _ => false,
    }
}

fn repeat_atom_match(node: &Expr, ctx: &Context<'_>, pos: usize) -> bool {
    match node {
        Expr::Lit(value, flags) => eq_lit(*value, ctx.character(pos), *flags, ctx, pos),
        Expr::Dot(flags) => *flags & S != 0 || ctx.character(pos) != 10,
        Expr::Cat(code, flags) => category(*code, *flags, ctx, pos),
        Expr::Class(values, negative, flags) => class_match(values, *negative, *flags, ctx, pos),
        Expr::Alt(values) => values
            .iter()
            .any(|value| repeat_atom_match(value, ctx, pos)),
        Expr::Seq(values) if values.len() == 1 => repeat_atom_match(&values[0], ctx, pos),
        Expr::Group(_, child) => repeat_atom_match(child, ctx, pos),
        Expr::Repeat(child, minimum, Some(maximum), _) if minimum == maximum => {
            repeat_atom_match(child, ctx, pos)
        }
        _ => false,
    }
}

fn leading_lookbehind(node: &Expr) -> Option<usize> {
    match node {
        Expr::Look(true, true, _, width) => Some(*width),
        Expr::Seq(values) => values.first().and_then(leading_lookbehind),
        Expr::Group(_, child) | Expr::Atomic(child) => leading_lookbehind(child),
        _ => None,
    }
}

fn add_starts(node: &Expr, starts: &mut [u8; 256], ctx: &Context<'_>) -> (bool, bool) {
    match node {
        Expr::Lit(value, flags) => {
            for index in 0..256 {
                if eq_lit(*value, ctx.character(index), *flags, ctx, index) {
                    starts[index] = 1;
                }
            }
            (false, true)
        }
        Expr::Dot(flags) => {
            for (index, item) in starts.iter_mut().enumerate() {
                if *flags & S != 0 || index != 10 {
                    *item = 1;
                }
            }
            (false, true)
        }
        Expr::Cat(code, flags) => {
            for (index, item) in starts.iter_mut().enumerate() {
                if category(*code, *flags, ctx, index) {
                    *item = 1;
                }
            }
            (false, true)
        }
        Expr::Class(values, negative, flags) => {
            for (index, item) in starts.iter_mut().enumerate() {
                if class_match(values, *negative, *flags, ctx, index) {
                    *item = 1;
                }
            }
            (false, true)
        }
        Expr::Anchor(_, _) | Expr::Boundary(_, _) | Expr::Look(_, _, _, _) => (true, true),
        Expr::Group(_, child) | Expr::Atomic(child) => add_starts(child, starts, ctx),
        Expr::Seq(values) => {
            for value in values {
                let (nullable, known) = add_starts(value, starts, ctx);
                if !known {
                    return (false, false);
                }
                if !nullable {
                    return (false, true);
                }
            }
            (true, true)
        }
        Expr::Alt(values) => {
            let mut nullable = false;
            for value in values {
                let (empty, known) = add_starts(value, starts, ctx);
                if !known {
                    return (false, false);
                }
                nullable |= empty;
            }
            (nullable, true)
        }
        Expr::Repeat(child, minimum, _, _) => {
            let (nullable, known) = add_starts(child, starts, ctx);
            (*minimum == 0 || nullable, known)
        }
        Expr::Cond(_, yes, no) => {
            let (yes_empty, yes_known) = add_starts(yes, starts, ctx);
            let (no_empty, no_known) = add_starts(no, starts, ctx);
            (yes_empty || no_empty, yes_known && no_known)
        }
        Expr::Backref(_, _) => (false, false),
    }
}

fn start_table(root: &Expr) -> Option<[u8; 256]> {
    let chars: Vec<u32> = (0..256).collect();
    let folds: Vec<u32> = chars
        .iter()
        .map(|value| {
            if (65..=90).contains(value) {
                value + 32
            } else {
                *value
            }
        })
        .collect();
    let masks: Vec<u8> = chars
        .iter()
        .map(|value| {
            let byte = *value as u8;
            u8::from(byte.is_ascii_digit())
                | (u8::from(matches!(byte, 9 | 10 | 11 | 12 | 13 | 32)) << 1)
                | (u8::from(byte.is_ascii_alphanumeric()) << 2)
        })
        .collect();
    let context = Context {
        chars: &chars,
        folds: &folds,
        masks: &masks,
        bytes: None,
        end: 256,
    };
    let mut starts = [0; 256];
    let (nullable, known) = add_starts(root, &mut starts, &context);
    starts[128..].fill(1);
    if known && !nullable {
        Some(starts)
    } else {
        None
    }
}

fn eval(node: &Expr, state: &State, ctx: &Context<'_>) -> Vec<State> {
    match node {
        Expr::Lit(value, flags) => {
            if state.pos < ctx.end
                && eq_lit(*value, ctx.character(state.pos), *flags, ctx, state.pos)
            {
                let mut next = state.clone();
                next.pos += 1;
                vec![next]
            } else {
                vec![]
            }
        }
        Expr::Dot(flags) => {
            if state.pos < ctx.end && (*flags & S != 0 || ctx.character(state.pos) != 10) {
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
                        || (*flags & M != 0 && state.pos > 0 && ctx.character(state.pos - 1) == 10)
                }
                '$' => {
                    state.pos == ctx.end
                        || (state.pos + 1 == ctx.end
                            && state.pos < ctx.end
                            && ctx.character(state.pos) == 10)
                        || (*flags & M != 0
                            && state.pos < ctx.end
                            && ctx.character(state.pos) == 10)
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
                if matches!(
                    item,
                    Expr::Lit(_, _)
                        | Expr::Dot(_)
                        | Expr::Cat(_, _)
                        | Expr::Class(_, _, _)
                        | Expr::Anchor(_, _)
                        | Expr::Boundary(_, _)
                ) {
                    current.retain_mut(|value| advance_atom(item, value, ctx));
                } else {
                    current = current
                        .iter()
                        .flat_map(|value| eval(item, value, ctx))
                        .collect();
                }
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
                    ctx.character(begin + off),
                    ctx.character(state.pos + off),
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
            if let Some((leaf, width, captures)) = repeat_layout(child)
                && width > 0
            {
                let available = (ctx.end - state.pos) / width;
                let limit = max.map_or(available, |value| value.min(available));
                let mut matched = 0;
                while matched < limit {
                    let begin = state.pos + matched * width;
                    if !(begin..begin + width).all(|pos| repeat_atom_match(&leaf, ctx, pos)) {
                        break;
                    }
                    matched += 1;
                }
                if matched < *min {
                    return vec![];
                }
                let mut result =
                    Vec::with_capacity(if *mode == 2 { 1 } else { matched - *min + 1 });
                let mut add = |count| {
                    let mut value = state.clone();
                    value.pos += count * width;
                    if count > 0 {
                        let base = state.pos + (count - 1) * width;
                        for (number, begin, end) in &captures {
                            value.caps[*number] = Some((base + begin, base + end));
                            value.last = Some(*number);
                        }
                    }
                    result.push(value);
                };
                if *mode == 1 {
                    for count in *min..=matched {
                        add(count);
                    }
                } else if *mode == 2 {
                    add(matched);
                } else {
                    for count in (*min..=matched).rev() {
                        add(count);
                    }
                }
                return result;
            }
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
        global_allowed: true,
        group_depth: 0,
        open_groups: vec![],
        lookbehind_bases: vec![],
        pending_conditionals: vec![],
    };
    match parser.parse() {
        Ok(mut root) => {
            let chars: Vec<u32> = (0..128).collect();
            let folds: Vec<u32> = chars
                .iter()
                .map(|value| {
                    if (65..=90).contains(value) {
                        value + 32
                    } else {
                        *value
                    }
                })
                .collect();
            let masks: Vec<u8> = chars
                .iter()
                .map(|value| {
                    let byte = *value as u8;
                    u8::from(byte.is_ascii_digit())
                        | (u8::from(matches!(byte, 9 | 10 | 11 | 12 | 13 | 32)) << 1)
                        | (u8::from(byte.is_ascii_alphanumeric()) << 2)
                })
                .collect();
            let context = Context {
                chars: &chars,
                folds: &folds,
                masks: &masks,
                bytes: None,
                end: 128,
            };
            prepare_classes(&mut root, &context);
            let starts = start_table(&root);
            set_error(String::new(), None, false);
            Box::into_raw(Box::new(Engine {
                root,
                groups: parser.groups,
                names: parser.names,
                flags: parser.flags & !BYTE,
                starts,
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

fn run_match(
    engine: &Engine,
    context: &Context<'_>,
    pos: usize,
    mode: u8,
    nonempty: u8,
    begins: &mut [isize],
    ends: &mut [isize],
    last: &mut isize,
) -> i32 {
    if pos > context.end {
        return 0;
    }
    let last_start = if mode == 0 { context.end } else { pos };
    let first_start = if mode == 0 {
        leading_lookbehind(&engine.root).map_or(pos, |width| pos.max(width))
    } else {
        pos
    };
    for start in first_start..=last_start {
        if mode == 0
            && start < context.end
            && let Some(starts) = &engine.starts
            && context.character(start) < 256
            && starts[context.character(start) as usize] == 0
        {
            continue;
        }
        let state = State {
            pos: start,
            caps: vec![None; engine.groups + 1],
            last: None,
        };
        for value in eval(&engine.root, &state, context) {
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
            *last = value.last.map_or(-1, |v| v as isize);
            return 1;
        }
    }
    0
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
        bytes: None,
        end: endpos.min(length),
    };
    let begins = unsafe { slice::from_raw_parts_mut(begins, engine.groups + 1) };
    let ends = unsafe { slice::from_raw_parts_mut(ends, engine.groups + 1) };
    run_match(
        engine,
        &context,
        pos,
        mode,
        nonempty,
        begins,
        ends,
        unsafe { &mut *last },
    )
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn rebar_match_ascii(
    handle: *const Engine,
    data: *const u8,
    length: usize,
    pos: usize,
    endpos: usize,
    mode: u8,
    nonempty: u8,
    begins: *mut isize,
    ends: *mut isize,
    last: *mut isize,
) -> i32 {
    if handle.is_null() || data.is_null() || begins.is_null() || ends.is_null() || last.is_null() {
        return -1;
    }
    let engine = unsafe { &*handle };
    let context = Context {
        chars: &[],
        folds: &[],
        masks: &[],
        bytes: Some(unsafe { slice::from_raw_parts(data, length) }),
        end: endpos.min(length),
    };
    let begins = unsafe { slice::from_raw_parts_mut(begins, engine.groups + 1) };
    let ends = unsafe { slice::from_raw_parts_mut(ends, engine.groups + 1) };
    run_match(
        engine,
        &context,
        pos,
        mode,
        nonempty,
        begins,
        ends,
        unsafe { &mut *last },
    )
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn rebar_collect_ascii(
    handle: *const Engine,
    data: *const u8,
    length: usize,
    pos: usize,
    endpos: usize,
    capacity: usize,
    begins: *mut isize,
    ends: *mut isize,
    lasts: *mut isize,
) -> isize {
    if handle.is_null() || data.is_null() || begins.is_null() || ends.is_null() || lasts.is_null() {
        return -1;
    }
    let engine = unsafe { &*handle };
    let Some(total) = capacity.checked_mul(engine.groups + 1) else {
        return -1;
    };
    let starts = unsafe { slice::from_raw_parts_mut(begins, total) };
    let finishes = unsafe { slice::from_raw_parts_mut(ends, total) };
    let last_values = unsafe { slice::from_raw_parts_mut(lasts, capacity) };
    let stride = engine.groups + 1;
    let end = endpos.min(length);
    let context = Context {
        chars: &[],
        folds: &[],
        masks: &[],
        bytes: Some(unsafe { slice::from_raw_parts(data, length) }),
        end,
    };
    let mut current = pos;
    let mut nonempty = 0;
    let mut count = 0;
    while current <= end && count < capacity {
        let offset = count * stride;
        let result = run_match(
            engine,
            &context,
            current,
            0,
            nonempty,
            &mut starts[offset..offset + stride],
            &mut finishes[offset..offset + stride],
            &mut last_values[count],
        );
        if result < 0 {
            return -1;
        }
        if result == 0 {
            break;
        }
        let begin = starts[offset] as usize;
        let finish = finishes[offset] as usize;
        count += 1;
        if begin == finish {
            current = begin;
            nonempty = 1;
        } else {
            current = finish;
            nonempty = 0;
        }
    }
    count as isize
}
