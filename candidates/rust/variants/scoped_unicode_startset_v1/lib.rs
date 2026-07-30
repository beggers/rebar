use std::cell::RefCell;
use std::ffi::c_int;
use std::slice;

mod newline;
mod search;
mod stack;
mod unicode_tables;

use stack::InlineStack;

unsafe extern "C" {
    fn Py_GetRecursionLimit() -> i32;
    fn tolower(value: c_int) -> c_int;
    fn isalnum(value: c_int) -> c_int;
}

const I: u32 = 2;
const L: u32 = 4;
const M: u32 = 8;
const S: u32 = 16;
const U: u32 = 32;
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

#[derive(Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
enum Op {
    Literal,
    Dot,
    Category,
    Class,
    Anchor,
    Boundary,
    Split,
    Jump,
    SaveBegin,
    SaveEnd,
    Backref,
    Conditional,
    AtomicBegin,
    AtomicEnd,
    Look,
    Run,
    RepeatStart,
    RepeatCheck,
    RepeatEnd,
    Accept,
}

#[derive(Clone, Copy)]
struct Instruction {
    op: Op,
    left: usize,
    right: usize,
    value: usize,
    flags: u32,
}

impl Instruction {
    #[inline]
    const fn new(op: Op) -> Self {
        Self {
            op,
            left: 0,
            right: 0,
            value: 0,
            flags: 0,
        }
    }
}

struct CompiledClass {
    members: Vec<Member>,
    negative: bool,
    flags: u32,
}

struct CompiledRun {
    atom: Expr,
    width: usize,
    minimum: usize,
    maximum: Option<usize>,
    mode: u8,
    captures: Vec<(usize, usize, usize)>,
}

#[derive(Clone, Copy)]
struct CompiledRepeat {
    minimum: usize,
    maximum: Option<usize>,
    minimum_width: usize,
    mode: u8,
}

struct Program {
    code: Vec<Instruction>,
    classes: Vec<CompiledClass>,
    runs: Vec<CompiledRun>,
    repeats: Vec<CompiledRepeat>,
    guards: usize,
}

#[derive(Clone, Copy)]
struct MandatoryRunDelimiter {
    run: usize,
    delimiter: u8,
}

#[derive(Clone, Copy)]
struct EvenSuffixDelimiter {
    separator: u8,
    quote: u8,
}

const MANDATORY_LITERAL_PREFIX_CAPACITY: usize = 16;
const MANDATORY_LITERAL_PREFIX_DEPTH: usize = 64;

/// A necessary byte prefix and whether it describes the entire expression.
///
/// `exact` is true only when every successful path consumes exactly `bytes`.
/// In particular, a shared prefix of different alternatives is necessary but
/// not exact, so a parent sequence must not append its following expression.
#[derive(Clone, Copy)]
struct MandatoryLiteralPrefix {
    bytes: [u8; MANDATORY_LITERAL_PREFIX_CAPACITY],
    length: u8,
    exact: bool,
}

impl MandatoryLiteralPrefix {
    #[inline]
    const fn empty(exact: bool) -> Self {
        Self {
            bytes: [0; MANDATORY_LITERAL_PREFIX_CAPACITY],
            length: 0,
            exact,
        }
    }

    #[inline]
    fn as_slice(&self) -> &[u8] {
        &self.bytes[..usize::from(self.length)]
    }

    /// Append a child's necessary prefix; continue only if its whole width is known.
    #[inline]
    fn append(&mut self, child: &Self) -> bool {
        let start = usize::from(self.length);
        let available = MANDATORY_LITERAL_PREFIX_CAPACITY - start;
        let count = available.min(usize::from(child.length));
        self.bytes[start..start + count].copy_from_slice(&child.bytes[..count]);
        self.length = (start + count) as u8;
        if count != usize::from(child.length) || !child.exact {
            self.exact = false;
            return false;
        }
        true
    }
}

#[derive(Clone, Copy, Default)]
struct Choice {
    pc: usize,
    pos: usize,
    undo: usize,
    guard_undo: usize,
    repeat_undo: usize,
    atomic_depth: usize,
    run_chosen: usize,
    run_available: usize,
    run_resume: bool,
    enter_guard: usize,
}

#[derive(Clone, Copy, Default)]
struct CaptureUndo {
    group: usize,
    begin: isize,
    end: isize,
    last: isize,
}

#[derive(Clone, Copy, Default)]
struct GuardUndo {
    slot: usize,
    previous: usize,
}

#[derive(Clone, Copy, Default)]
struct RepeatState {
    count: usize,
    iteration_start: usize,
}

#[derive(Clone, Copy, Default)]
struct RepeatUndo {
    slot: usize,
    previous: RepeatState,
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum SearchAnchor {
    Unrestricted,
    Line,
    Absolute,
}

pub struct Engine {
    program: Program,
    groups: usize,
    names: Vec<(String, usize)>,
    flags: u32,
    starts: Option<[u8; 256]>,
    start_set: Option<search::StartSet>,
    mandatory_literal_prefix: Option<MandatoryLiteralPrefix>,
    mandatory_run_delimiter: Option<MandatoryRunDelimiter>,
    even_suffix_delimiter: Option<EvenSuffixDelimiter>,
    leading_lookbehind: Option<usize>,
    start_anchor: SearchAnchor,
    byte_mode: bool,
    deterministic: bool,
}
#[derive(Clone, Copy)]
struct BorrowedText<'a> {
    data: &'a [u8],
    kind: u8,
}

struct Context<'a> {
    chars: &'a [u32],
    folds: &'a [u32],
    masks: &'a [u8],
    bytes: Option<&'a [u8]>,
    wide: Option<BorrowedText<'a>>,
    end: usize,
}

impl Context<'_> {
    /// Distinguish physical subject storage from a clamped regex end window.
    #[inline(always)]
    fn has_character(&self, pos: usize) -> bool {
        if let Some(values) = self.bytes {
            return pos < values.len();
        }
        if let Some(wide) = self.wide {
            return pos < wide.data.len() / usize::from(wide.kind);
        }
        pos < self.chars.len()
    }

    #[inline(always)]
    fn character(&self, pos: usize) -> u32 {
        if let Some(values) = self.bytes {
            return u32::from(values[pos]);
        }
        if let Some(wide) = self.wide {
            return match wide.kind {
                1 => u32::from(wide.data[pos]),
                2 => {
                    let offset = pos * 2;
                    u32::from(u16::from_ne_bytes([
                        wide.data[offset],
                        wide.data[offset + 1],
                    ]))
                }
                4 => {
                    let offset = pos * 4;
                    u32::from_ne_bytes([
                        wide.data[offset],
                        wide.data[offset + 1],
                        wide.data[offset + 2],
                        wide.data[offset + 3],
                    ])
                }
                _ => unreachable!("validated CPython Unicode kind"),
            };
        }
        self.chars[pos]
    }

    #[inline(always)]
    fn mask(&self, pos: usize) -> u8 {
        if let Some(values) = self.bytes {
            let value = values[pos];
            return u8::from(value.is_ascii_digit())
                | (u8::from(matches!(value, 9 | 10 | 11 | 12 | 13 | 32)) << 1)
                | (u8::from(value.is_ascii_alphanumeric()) << 2);
        }
        if self.wide.is_some() {
            return unicode_category_mask(self.character(pos));
        }
        self.masks[pos]
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
    scanner_runtime_flags: Option<u32>,
    byte_mode: bool,
    groups: usize,
    names: Vec<(String, usize)>,
    widths: Vec<(usize, (usize, usize))>,
    named: Vec<(usize, u32)>,
    global_allowed: bool,
    recursion_limit: usize,
    group_depth: usize,
    open_groups: Vec<usize>,
    lookbehind_bases: Vec<usize>,
    pending_conditionals: Vec<(usize, usize)>,
    invalid_lookbehind_width: bool,
}
type PResult<T> = Result<T, (String, Option<usize>, bool)>;

impl Parser {
    #[inline]
    fn leaf_flags(&self, lexical_flags: u32) -> u32 {
        self.scanner_runtime_flags.unwrap_or(lexical_flags)
    }

    fn now(&self) -> Option<char> {
        self.source
            .get(self.at)
            .map(|&value| char::from_u32(value).unwrap_or(char::REPLACEMENT_CHARACTER))
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

    /// Consume a comment token using Python's backslash-and-character pairing.
    fn take_comment_token(&mut self) -> PResult<Option<char>> {
        let position = self.at;
        let Some(token) = self.take() else {
            return Ok(None);
        };
        if token == '\\' && self.take().is_none() {
            return self.fail("bad escape (end of pattern)".into(), Some(position), true);
        }
        Ok(Some(token))
    }

    fn skip(&mut self, flags: u32) -> PResult<()> {
        if flags & X == 0 {
            return Ok(());
        }
        loop {
            match self.now() {
                Some(' ' | '\t' | '\n' | '\r' | '\x0b' | '\x0c') => self.at += 1,
                Some('#') => {
                    self.at += 1;
                    while let Some(token) = self.take_comment_token()? {
                        if token == '\n' {
                            break;
                        }
                    }
                }
                _ => return Ok(()),
            }
        }
    }
    fn parse(&mut self) -> PResult<Expr> {
        let result = self.alt(self.flags)?;
        self.skip(self.flags)?;
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
        if self.invalid_lookbehind_width {
            return self.fail(
                "look-behind requires fixed-width pattern".into(),
                None,
                false,
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
            branches.swap_remove(0)
        } else {
            Expr::Alt(branches)
        })
    }
    fn seq(&mut self, mut flags: u32) -> PResult<Expr> {
        let mut result = Vec::new();
        loop {
            self.skip(flags)?;
            match self.now() {
                None | Some('|') | Some(')') => break,
                _ => {}
            }
            let start = self.at;
            let mut node = self.atom(flags)?;
            self.skip(flags)?;
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
        if matches!(node, Expr::Anchor(_, _) | Expr::Boundary(_, _)) {
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
            _ => {
                return self.fail("nothing to repeat".into(), Some(start), true);
            }
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
        let Some(raw) = self.source.get(self.at).copied() else {
            return self.fail("unexpected end of pattern".into(), Some(start), true);
        };
        let Some(value) = self.take() else {
            return self.fail("unexpected end of pattern".into(), Some(start), true);
        };
        let runtime_flags = self.leaf_flags(flags);
        match value {
            '.' => Ok(Expr::Dot(runtime_flags)),
            '^' | '$' => Ok(Expr::Anchor(value, runtime_flags)),
            '[' => self.class(flags, start),
            '\\' => self.escape(flags, false, start),
            '(' => self.group(flags, start),
            '*' | '+' | '?' => self.fail("nothing to repeat".into(), Some(start), true),
            '{' if self.brace_repeat(start) => {
                self.fail("nothing to repeat".into(), Some(start), true)
            }
            _ => Ok(Expr::Lit(raw, runtime_flags)),
        }
    }
    fn escape(&mut self, flags: u32, in_class: bool, slash: usize) -> PResult<Expr> {
        let raw = self.source.get(self.at).copied();
        let Some(ch) = self.take() else {
            return self.fail("bad escape (end of pattern)".into(), Some(slash), true);
        };
        let runtime_flags = self.leaf_flags(flags);
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
            return Ok(Expr::Lit(value, runtime_flags));
        }
        if ch == 'b' {
            return Ok(if in_class {
                Expr::Lit(8, runtime_flags)
            } else {
                Expr::Boundary(true, runtime_flags)
            });
        }
        if ch == 'B' && !in_class {
            return Ok(Expr::Boundary(false, runtime_flags));
        }
        if "dDsSwW".contains(ch) {
            return Ok(Expr::Cat(ch, runtime_flags));
        }
        if "AZz".contains(ch) && !in_class {
            return Ok(Expr::Anchor(ch, runtime_flags));
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
            return Ok(Expr::Lit(value, runtime_flags));
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
            return Ok(Expr::Lit(value, runtime_flags));
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
                return Ok(Expr::Lit(*value, runtime_flags));
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
                    let Some(digit) = self.take() else {
                        break;
                    };
                    digits.push(digit);
                }
                let Ok(value) = u32::from_str_radix(&digits, 8) else {
                    return self.fail(format!("bad escape \\{}", digits), Some(slash), true);
                };
                if value > 0o377 {
                    return self.fail(
                        format!("octal escape value \\{} outside of range 0-0o377", digits),
                        Some(slash),
                        true,
                    );
                }
                return Ok(Expr::Lit(value, runtime_flags));
            }
            if self.now().is_some_and(|v| v.is_ascii_digit()) {
                if let Some(digit) = self.take() {
                    digits.push(digit);
                }
            }
            let Ok(number) = digits.parse::<usize>() else {
                return self.fail(
                    format!("invalid group reference {}", digits),
                    Some(slash + 1),
                    true,
                );
            };
            self.check_reference(number, slash, Some(slash + 1), false)?;
            return Ok(Expr::Backref(number, runtime_flags));
        }
        if ch.is_ascii_alphabetic() {
            return self.fail(format!("bad escape \\{}", ch), Some(slash), true);
        }
        Ok(Expr::Lit(raw.unwrap_or(ch as u32), runtime_flags))
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
                return Ok(Expr::Class(values, negate, self.leaf_flags(flags)));
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
                            char::from_u32(a)
                                .map(|value| value.to_string())
                                .unwrap_or_else(|| format!("\\u{a:04x}")),
                            char::from_u32(b)
                                .map(|value| value.to_string())
                                .unwrap_or_else(|| format!("\\u{b:04x}"))
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
                    _ => {
                        return self.fail(
                            "bad character in character set".into(),
                            Some(left_start),
                            true,
                        );
                    }
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
        let valid = raw.iter().enumerate().all(|(index, &character)| {
            if index == 0 {
                unicode_tables::xid_start(character)
            } else {
                unicode_tables::xid_continue(character)
            }
        });
        if !valid || (self.byte_mode && raw.iter().any(|v| *v > 127)) {
            let shown = if self.byte_mode {
                raw.iter()
                    .map(|v| {
                        if *v < 128 {
                            char::from(*v as u8).to_string()
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
        if self.group_depth >= self.recursion_limit {
            return self.fail("maximum recursion depth exceeded".into(), None, false);
        }
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
                    self.invalid_lookbehind_width = true;
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
                loop {
                    match self.take_comment_token()? {
                        Some(')') => break,
                        Some(_) => {}
                        None => {
                            return self.fail(
                                "missing ), unterminated comment".into(),
                                Some(start),
                                true,
                            );
                        }
                    }
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
                    Ok(Expr::Backref(number, self.leaf_flags(flags)))
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
                let raw = &self.source[self.at..close];
                let reference: String = raw.iter().filter_map(|v| char::from_u32(*v)).collect();
                self.at = close + 1;
                if raw.is_empty() {
                    return self.fail("missing group name".into(), Some(position), true);
                }
                let number = if reference.chars().all(|v| v.is_ascii_digit()) {
                    let Ok(value) = reference.parse::<usize>() else {
                        return self.fail(
                            format!(
                                "invalid group reference {}",
                                reference.trim_start_matches('0')
                            ),
                            Some(position),
                            true,
                        );
                    };
                    if value == 0 {
                        return self.fail("bad group number".into(), Some(position), true);
                    }
                    self.check_reference(value, position, None, true)?;
                    value
                } else {
                    let valid = raw.iter().enumerate().all(|(index, &value)| {
                        if index == 0 {
                            unicode_tables::xid_start(value)
                        } else {
                            unicode_tables::xid_continue(value)
                        }
                    }) && (!self.byte_mode || raw.iter().all(|value| *value < 128));
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
                    let Some(value) = self.take() else {
                        break;
                    };
                    if value == '-' {
                        if removing {
                            return self.fail("missing flag".into(), Some(self.at - 1), true);
                        }
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
                if removing && off == 0 {
                    return self.fail("missing flag".into(), Some(self.at), true);
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
                    let previous_runtime_flags = self.scanner_runtime_flags;
                    if let Some(runtime_flags) = previous_runtime_flags {
                        let mut changed_runtime_flags = (runtime_flags | on) & !off;
                        if on & (A | L) != 0 {
                            changed_runtime_flags &= !U;
                        } else if on & U != 0 {
                            changed_runtime_flags &= !(A | L);
                        }
                        self.scanner_runtime_flags = Some(changed_runtime_flags);
                    }
                    let child = self.alt(changed);
                    self.scanner_runtime_flags = previous_runtime_flags;
                    let child = child?;
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

#[inline(always)]
fn locale_byte_flags(flags: u32) -> bool {
    flags & (L | BYTE) == L | BYTE
}

#[inline(always)]
fn locale_byte_lower(value: u32) -> u32 {
    let Ok(byte) = u8::try_from(value) else {
        return value;
    };
    let lowered = unsafe { tolower(c_int::from(byte)) };
    u8::try_from(lowered).map_or(value, u32::from)
}

#[inline]
fn locale_byte_other(value: u32) -> u32 {
    let Ok(byte) = u8::try_from(value) else {
        return value;
    };
    let lowered = locale_byte_lower(u32::from(byte));
    if lowered != value {
        return lowered;
    }
    (0_u32..=u32::from(u8::MAX))
        .find(|&candidate| candidate != value && locale_byte_lower(candidate) == lowered)
        .unwrap_or(value)
}

#[inline(always)]
fn locale_byte_isalnum(value: u32) -> bool {
    let Ok(byte) = u8::try_from(value) else {
        return false;
    };
    unsafe { isalnum(c_int::from(byte)) != 0 }
}

#[inline(always)]
fn unicode_simple_lower(value: u32, ascii_only: bool) -> u32 {
    if value < 128 {
        value.to_ascii_lowercase()
    } else if ascii_only {
        value
    } else {
        unicode_tables::simple_lower(value)
    }
}

#[inline(always)]
fn unicode_literal_fold(value: u32, ascii_only: bool) -> u32 {
    if ascii_only {
        return unicode_simple_lower(value, true);
    }
    unicode_tables::literal_fold(value)
}

#[inline(always)]
fn unicode_category_mask(value: u32) -> u8 {
    let mask = unicode_tables::category_mask(value);
    debug_assert!(
        mask & unicode_tables::CATEGORY_WORD == 0
            || mask
                & (unicode_tables::CATEGORY_ALPHA
                    | unicode_tables::CATEGORY_DECIMAL
                    | unicode_tables::CATEGORY_DIGIT
                    | unicode_tables::CATEGORY_NUMERIC)
                != 0
            || value == u32::from(b'_')
    );
    mask
}

#[inline(always)]
fn folded(value: u32, flags: u32, _ctx: &Context<'_>, _pos: usize) -> u32 {
    if locale_byte_flags(flags) {
        locale_byte_lower(value)
    } else {
        unicode_simple_lower(value, flags & (A | L | BYTE) != 0)
    }
}

fn eq(a: u32, b: u32, flags: u32, ctx: &Context<'_>, apos: usize, bpos: usize) -> bool {
    if a == b || flags & I == 0 {
        a == b
    } else {
        folded(a, flags, ctx, apos) == folded(b, flags, ctx, bpos)
    }
}
fn eq_lit(lit: u32, value: u32, flags: u32, ctx: &Context<'_>, pos: usize) -> bool {
    if lit == value || flags & I == 0 {
        lit == value
    } else if locale_byte_flags(flags) {
        locale_byte_lower(lit) == locale_byte_lower(value)
    } else {
        let _ = (ctx, pos);
        let ascii_only = flags & (A | L | BYTE) != 0;
        unicode_literal_fold(lit, ascii_only) == unicode_literal_fold(value, ascii_only)
    }
}

const CASE_VARIANTS: [[u32; 4]; 28] = [
    [0x0049, 0x0069, 0x0130, 0x0131],
    [0x0053, 0x0073, 0x017f, 0x017f],
    [0x004b, 0x006b, 0x212a, 0x212a],
    [0x0412, 0x0432, 0x1c80, 0x1c80],
    [0xfb05, 0xfb06, 0xfb05, 0xfb06],
    [0x00df, 0x1e9e, 0x00df, 0x1e9e],
    [0x00b5, 0x03bc, 0x00b5, 0x03bc],
    [0x0345, 0x03b9, 0x1fbe, 0x0345],
    [0x0390, 0x1fd3, 0x0390, 0x1fd3],
    [0x03b0, 0x1fe3, 0x03b0, 0x1fe3],
    [0x03b2, 0x03d0, 0x03b2, 0x03d0],
    [0x03b5, 0x03f5, 0x03b5, 0x03f5],
    [0x0398, 0x03b8, 0x03d1, 0x03f4],
    [0x03ba, 0x03f0, 0x03ba, 0x03f0],
    [0x03c0, 0x03d6, 0x03c0, 0x03d6],
    [0x03c1, 0x03f1, 0x03c1, 0x03f1],
    [0x03c2, 0x03c3, 0x03c2, 0x03c3],
    [0x03c6, 0x03d5, 0x03c6, 0x03d5],
    [0x0434, 0x1c81, 0x0434, 0x1c81],
    [0x043e, 0x1c82, 0x043e, 0x1c82],
    [0x0441, 0x1c83, 0x0441, 0x1c83],
    [0x0442, 0x1c84, 0x1c85, 0x0442],
    [0x044a, 0x1c86, 0x044a, 0x1c86],
    [0x0463, 0x1c87, 0x0463, 0x1c87],
    [0xa64b, 0x1c88, 0xa64b, 0x1c88],
    [0x1e61, 0x1e9b, 0x1e61, 0x1e9b],
    [0x03a9, 0x03c9, 0x2126, 0x03a9],
    [0x00c5, 0x00e5, 0x212b, 0x00c5],
];

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
    if locale_byte_flags(flags) {
        let Ok(first) = u8::try_from(left) else {
            return false;
        };
        let last = right.min(u32::from(u8::MAX));
        let folded = locale_byte_lower(value);
        return (u32::from(first)..=last)
            .any(|candidate| locale_byte_lower(candidate) == folded);
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
    let lower = unicode_simple_lower(value, false);
    let upper = if unicode_tables::multi_upper(value) {
        value
    } else {
        unicode_tables::simple_upper(value)
    };
    let _ = (ctx, pos);
    let fold = unicode_literal_fold(value, false);
    if (left <= lower && lower <= right)
        || (left <= upper && upper <= right)
        || (left <= fold && fold <= right)
    {
        return true;
    }
    CASE_VARIANTS.iter().any(|closure| {
        closure
            .iter()
            .any(|&item| left <= item && item <= right && unicode_literal_fold(item, false) == fold)
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
                ctx.mask(pos) & unicode_tables::CATEGORY_DECIMAL != 0
            }
        }
        's' => {
            if ascii {
                matches!(value, 9 | 10 | 11 | 12 | 13 | 32)
            } else {
                ctx.mask(pos) & unicode_tables::CATEGORY_WHITESPACE != 0
            }
        }
        _ => {
            if locale_byte_flags(flags) {
                locale_byte_isalnum(value) || value == u32::from(b'_')
            } else if ascii {
                value < 128
                    && ((value >= b'0' as u32 && value <= b'9' as u32)
                        || (value >= b'A' as u32 && value <= b'Z' as u32)
                        || (value >= b'a' as u32 && value <= b'z' as u32)
                        || value == b'_' as u32)
            } else {
                ctx.mask(pos) & unicode_tables::CATEGORY_WORD != 0 || value == b'_' as u32
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
    if !locale_byte_flags(flags)
        && value < 128
        && let Some(Member::Table(table)) = values.first()
    {
        return table[(value / 64) as usize] & (1_u64 << (value % 64)) != 0;
    }
    if negative
        && flags & (I | L) == I | L
        && !(values.len() == 1 && matches!(values.first(), Some(Member::Lit(_))))
    {
        let other = if locale_byte_flags(flags) {
            locale_byte_other(value)
        } else if (b'A' as u32..=b'Z' as u32).contains(&value) {
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
            if locale_byte_flags(*flags) {
                return;
            }
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

fn contains_group_capture(node: &Expr) -> bool {
    match node {
        Expr::Group(_, _) => true,
        Expr::Seq(values) | Expr::Alt(values) => values.iter().any(contains_group_capture),
        Expr::Repeat(child, _, _, _) | Expr::Look(_, _, child, _) | Expr::Atomic(child) => {
            contains_group_capture(child)
        }
        Expr::Cond(_, yes, no) => contains_group_capture(yes) || contains_group_capture(no),
        _ => false,
    }
}

/// Recognize an unbounded class that consumes every character except `quote`.
///
/// This must run before `prepare_classes` inserts its ASCII lookup table.
/// Singleton ranges and repeated equivalent literals describe the same set.
fn even_suffix_quote_star(node: &Expr, quote: u32, flags: u32) -> bool {
    let Expr::Repeat(child, minimum, maximum, mode) = node else {
        return false;
    };
    if *minimum != 0 || maximum.is_some() || *mode != 0 {
        return false;
    }

    let Expr::Class(members, true, class_flags) = child.as_ref() else {
        return false;
    };
    if *class_flags != flags || flags & (I | L) != 0 || members.is_empty() {
        return false;
    }

    members.iter().all(|member| match member {
        Member::Lit(value) => *value == quote,
        Member::Range(first, last) => *first == quote && *last == quote,
        Member::Cat(_) | Member::Table(_) => false,
    })
}

/// Prove that a capture-free delimiter is followed by an even-quote suffix.
///
/// The recognized expression is an exact-case, one-byte separator followed by
/// `(?=(?:[^q]*q[^q]*q)*[^q]*$)`. Recognition is derived exclusively from the
/// parsed AST. Multiline anchors, case or locale folding, non-greedy repeats,
/// capturing groups, newline quotes, and uncertain class members all fall back
/// to the original ordered, capture-aware VM.
fn even_suffix_delimiter(root: &Expr, groups: usize) -> Option<EvenSuffixDelimiter> {
    if groups != 0 {
        return None;
    }

    let Expr::Seq(values) = root else {
        return None;
    };
    let [Expr::Lit(separator, separator_flags), Expr::Look(false, true, child, 0)] =
        values.as_slice()
    else {
        return None;
    };
    if *separator_flags & (I | L) != 0 {
        return None;
    }

    let Expr::Seq(look_values) = child.as_ref() else {
        return None;
    };
    let [Expr::Repeat(pair, pair_minimum, pair_maximum, pair_mode), final_class, Expr::Anchor('$', anchor_flags)] =
        look_values.as_slice()
    else {
        return None;
    };
    if *pair_minimum != 0
        || pair_maximum.is_some()
        || *pair_mode != 0
        || *anchor_flags & (I | L | M) != 0
    {
        return None;
    }

    let Expr::Seq(pair_values) = pair.as_ref() else {
        return None;
    };
    let [first_class, Expr::Lit(first_quote, first_flags), second_class, Expr::Lit(second_quote, second_flags)] =
        pair_values.as_slice()
    else {
        return None;
    };
    if first_quote != second_quote
        || first_flags != second_flags
        || *first_flags & (I | L) != 0
    {
        return None;
    }

    let separator = u8::try_from(*separator).ok()?;
    let quote = u8::try_from(*first_quote).ok()?;
    if separator == quote || quote == b'\n' {
        return None;
    }
    if !even_suffix_quote_star(first_class, *first_quote, *first_flags)
        || !even_suffix_quote_star(second_class, *first_quote, *first_flags)
        || !even_suffix_quote_star(final_class, *first_quote, *first_flags)
    {
        return None;
    }

    Some(EvenSuffixDelimiter { separator, quote })
}

/// Derive only byte prefixes that every original, ordered AST path requires.
///
/// Assertions and captures are still executed by the original VM. An uncertain
/// expression, scoped case-folding, a nullable alternative, or the bounded
/// traversal depth can only shorten or disable the filter.
fn mandatory_literal_prefix(node: &Expr, depth: usize) -> MandatoryLiteralPrefix {
    if depth >= MANDATORY_LITERAL_PREFIX_DEPTH {
        return MandatoryLiteralPrefix::empty(false);
    }

    match node {
        Expr::Lit(value, flags) if flags & I == 0 => {
            let Ok(byte) = u8::try_from(*value) else {
                return MandatoryLiteralPrefix::empty(false);
            };
            let mut prefix = MandatoryLiteralPrefix::empty(true);
            prefix.bytes[0] = byte;
            prefix.length = 1;
            prefix
        }
        Expr::Anchor(_, _) | Expr::Boundary(_, _) => MandatoryLiteralPrefix::empty(true),
        Expr::Group(_, child) | Expr::Atomic(child) => {
            mandatory_literal_prefix(child, depth + 1)
        }
        Expr::Seq(values) => {
            let mut prefix = MandatoryLiteralPrefix::empty(true);
            for value in values {
                let child = mandatory_literal_prefix(value, depth + 1);
                if !prefix.append(&child) {
                    break;
                }
            }
            prefix
        }
        Expr::Alt(values) => {
            let mut branches = values.iter();
            let Some(first) = branches.next() else {
                return MandatoryLiteralPrefix::empty(true);
            };
            let mut common = mandatory_literal_prefix(first, depth + 1);
            for branch in branches {
                let other = mandatory_literal_prefix(branch, depth + 1);
                let previous_length = usize::from(common.length);
                let other_length = usize::from(other.length);
                let shared = common
                    .as_slice()
                    .iter()
                    .zip(other.as_slice())
                    .take_while(|(left, right)| left == right)
                    .count();
                common.exact = common.exact
                    && other.exact
                    && shared == previous_length
                    && shared == other_length;
                common.length = shared as u8;
            }
            common
        }
        Expr::Repeat(child, minimum, Some(maximum), _) if minimum == maximum => {
            if *minimum == 0 {
                return MandatoryLiteralPrefix::empty(true);
            }

            let child = mandatory_literal_prefix(child, depth + 1);
            if !child.exact || child.length == 0 {
                return child;
            }

            let child_length = usize::from(child.length);
            let bounded_repetitions =
                (*minimum).min(MANDATORY_LITERAL_PREFIX_CAPACITY / child_length + 1);
            let mut prefix = MandatoryLiteralPrefix::empty(true);
            for _ in 0..bounded_repetitions {
                if !prefix.append(&child) {
                    return prefix;
                }
            }
            if bounded_repetitions != *minimum {
                prefix.exact = false;
            }
            prefix
        }
        Expr::Lit(_, _)
        | Expr::Dot(_)
        | Expr::Cat(_, _)
        | Expr::Class(_, _, _)
        | Expr::Backref(_, _)
        | Expr::Repeat(_, _, _, _)
        | Expr::Look(_, _, _, _)
        | Expr::Cond(_, _, _) => MandatoryLiteralPrefix::empty(false),
    }
}

fn required_start_anchor(node: &Expr) -> SearchAnchor {
    match node {
        Expr::Anchor('A', _) => SearchAnchor::Absolute,
        Expr::Anchor('^', flags) => {
            if flags & M == 0 {
                SearchAnchor::Absolute
            } else {
                SearchAnchor::Line
            }
        }
        Expr::Group(_, child) | Expr::Atomic(child) => required_start_anchor(child),
        Expr::Repeat(child, minimum, _, _) if *minimum != 0 => required_start_anchor(child),
        Expr::Seq(values) => {
            for child in values {
                let anchor = required_start_anchor(child);
                if anchor != SearchAnchor::Unrestricted {
                    return anchor;
                }
                if width(child, &[]).1 != 0 {
                    return SearchAnchor::Unrestricted;
                }
            }
            SearchAnchor::Unrestricted
        }
        Expr::Alt(values) => {
            let mut anchor = SearchAnchor::Absolute;
            for child in values {
                match required_start_anchor(child) {
                    SearchAnchor::Unrestricted => {
                        return SearchAnchor::Unrestricted;
                    }
                    SearchAnchor::Line => anchor = SearchAnchor::Line,
                    SearchAnchor::Absolute => {}
                }
            }
            anchor
        }
        Expr::Cond(_, yes, no) => match (required_start_anchor(yes), required_start_anchor(no)) {
            (SearchAnchor::Absolute, SearchAnchor::Absolute) => SearchAnchor::Absolute,
            (SearchAnchor::Unrestricted, _) | (_, SearchAnchor::Unrestricted) => {
                SearchAnchor::Unrestricted
            }
            _ => SearchAnchor::Line,
        },
        _ => SearchAnchor::Unrestricted,
    }
}

#[inline]
fn next_line_start(context: &Context<'_>, start: usize) -> Option<usize> {
    if start > context.end {
        return None;
    }
    if start == 0 || context.character(start - 1) == u32::from(b'\n') {
        return Some(start);
    }
    let next = if let Some(bytes) = context.bytes {
        newline::next_newline(bytes, 1, start, context.end)
    } else if let Some(subject) = context.wide {
        newline::next_newline(subject.data, subject.kind, start, context.end)
    } else {
        newline::next_newline_chars(context.chars, start, context.end)
    };
    next.and_then(|position| position.checked_add(1))
}

fn leading_lookbehind(node: &Expr) -> Option<usize> {
    match node {
        Expr::Look(true, true, _, width) => Some(*width),
        Expr::Seq(values) => values.first().and_then(leading_lookbehind),
        Expr::Group(_, child) | Expr::Atomic(child) => leading_lookbehind(child),
        _ => None,
    }
}

#[inline]
fn prefix_iscased(value: u32, flags: u32) -> bool {
    if flags & I == 0 {
        return false;
    }
    if flags & (A | L | BYTE) != 0 {
        return value.wrapping_sub(u32::from(b'A')) < 26
            || value.wrapping_sub(u32::from(b'a')) < 26;
    }
    unicode_tables::simple_lower(value) != value || unicode_tables::simple_upper(value) != value
}

#[inline]
fn prefix_charset_is_cased(members: &[Member], flags: u32) -> bool {
    if flags & I == 0 {
        return false;
    }
    members.iter().any(|member| match *member {
        Member::Lit(value) => prefix_iscased(value, flags),
        Member::Range(left, right) => {
            right > 0xffff || (left..=right).any(|value| prefix_iscased(value, flags))
        }
        Member::Cat(_) | Member::Table(_) => false,
    })
}

fn has_scoped_category_prefix(node: &Expr, global_flags: u32) -> bool {
    match node {
        Expr::Cat(_, flags) | Expr::Class(_, _, flags) => {
            (*flags ^ global_flags) & (A | L | BYTE) != 0
        }
        Expr::Group(_, child) | Expr::Atomic(child) | Expr::Repeat(child, _, _, _) => {
            has_scoped_category_prefix(child, global_flags)
        }
        Expr::Seq(values) => {
            for value in values {
                if has_scoped_category_prefix(value, global_flags) {
                    return true;
                }
                if !Compiler::nullable(value) {
                    break;
                }
            }
            false
        }
        Expr::Alt(values) => values
            .iter()
            .any(|value| has_scoped_category_prefix(value, global_flags)),
        Expr::Cond(_, yes, no) => {
            has_scoped_category_prefix(yes, global_flags)
                || has_scoped_category_prefix(no, global_flags)
        }
        Expr::Lit(_, _)
        | Expr::Dot(_)
        | Expr::Anchor(_, _)
        | Expr::Boundary(_, _)
        | Expr::Backref(_, _)
        | Expr::Look(_, _, _, _) => false,
    }
}

fn add_starts(
    node: &Expr,
    starts: &mut [u8; 256],
    ctx: &Context<'_>,
    global_flags: u32,
) -> (bool, bool) {
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
            let prefix_flags = (*flags & !(A | L | BYTE)) | (global_flags & (A | L | BYTE));
            for (index, item) in starts.iter_mut().enumerate() {
                if category(*code, prefix_flags, ctx, index) {
                    *item = 1;
                }
            }
            (false, true)
        }
        Expr::Class(values, negative, flags) => {
            let prefix_flags = (*flags & !(A | L | BYTE)) | (global_flags & (A | L | BYTE));
            let members = if matches!(values.first(), Some(Member::Table(_))) {
                &values[1..]
            } else {
                values
            };
            if (*flags ^ global_flags) & (A | L | BYTE) != 0
                && prefix_charset_is_cased(members, *flags)
            {
                return (false, false);
            }
            for (index, item) in starts.iter_mut().enumerate() {
                if class_match(members, *negative, prefix_flags, ctx, index) {
                    *item = 1;
                }
            }
            (false, true)
        }
        Expr::Anchor(_, _) | Expr::Boundary(_, _) | Expr::Look(_, _, _, _) => (true, true),
        Expr::Group(_, child) | Expr::Atomic(child) => add_starts(child, starts, ctx, global_flags),
        Expr::Seq(values) => {
            for value in values {
                let (nullable, known) = add_starts(value, starts, ctx, global_flags);
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
            if values
                .iter()
                .any(|value| has_scoped_category_prefix(value, global_flags))
            {
                return (false, false);
            }
            let mut nullable = false;
            for value in values {
                let (empty, known) = add_starts(value, starts, ctx, global_flags);
                if !known {
                    return (false, false);
                }
                nullable |= empty;
            }
            (nullable, true)
        }
        Expr::Repeat(child, minimum, _, _) => {
            let (nullable, known) = add_starts(child, starts, ctx, global_flags);
            (*minimum == 0 || nullable, known)
        }
        Expr::Cond(_, yes, no) => {
            let (yes_empty, yes_known) = add_starts(yes, starts, ctx, global_flags);
            let (no_empty, no_known) = add_starts(no, starts, ctx, global_flags);
            (yes_empty || no_empty, yes_known && no_known)
        }
        Expr::Backref(_, _) => (false, false),
    }
}

fn contains_locale_sensitive_expression(node: &Expr) -> bool {
    match node {
        Expr::Lit(_, flags)
        | Expr::Dot(flags)
        | Expr::Cat(_, flags)
        | Expr::Class(_, _, flags)
        | Expr::Anchor(_, flags)
        | Expr::Boundary(_, flags)
        | Expr::Backref(_, flags) => locale_byte_flags(*flags),
        Expr::Seq(values) | Expr::Alt(values) => {
            values.iter().any(contains_locale_sensitive_expression)
        }
        Expr::Group(_, child)
        | Expr::Repeat(child, _, _, _)
        | Expr::Look(_, _, child, _)
        | Expr::Atomic(child) => contains_locale_sensitive_expression(child),
        Expr::Cond(_, yes, no) => {
            contains_locale_sensitive_expression(yes)
                || contains_locale_sensitive_expression(no)
        }
    }
}

fn start_table(root: &Expr, global_flags: u32) -> Option<[u8; 256]> {
    if locale_byte_flags(global_flags)
        || contains_locale_sensitive_expression(root)
        || has_scoped_category_prefix(root, global_flags)
    {
        return None;
    }
    let chars: [u32; 256] = std::array::from_fn(|index| index as u32);
    let folds: [u32; 256] = std::array::from_fn(|index| unicode_tables::simple_lower(index as u32));
    let masks: [u8; 256] = std::array::from_fn(|index| unicode_category_mask(index as u32));
    let context = Context {
        chars: &chars,
        folds: &folds,
        masks: &masks,
        bytes: None,
        wide: None,
        end: 256,
    };
    let mut starts = [0; 256];
    let (nullable, known) = add_starts(root, &mut starts, &context, global_flags);
    if known && !nullable {
        Some(starts)
    } else {
        None
    }
}

#[inline]
fn wide_prefix_allows(engine: &Engine, context: &Context<'_>, pos: usize) -> bool {
    let mut pc = 0;
    for _ in 0..engine.program.code.len() {
        let instruction = engine.program.code[pc];
        match instruction.op {
            Op::SaveBegin | Op::SaveEnd => pc += 1,
            Op::Jump => pc = instruction.left,
            Op::Category => {
                let flags = (instruction.flags & !(A | L | BYTE)) | (engine.flags & (A | L | BYTE));
                return char::from_u32(instruction.value as u32)
                    .is_none_or(|code| category(code, flags, context, pos));
            }
            Op::Class => {
                let class = &engine.program.classes[instruction.left];
                let flags = (class.flags & !(A | L | BYTE)) | (engine.flags & (A | L | BYTE));
                return class_match(&class.members, class.negative, flags, context, pos);
            }
            _ => return true,
        }
    }
    true
}

struct Compiler {
    program: Program,
}

impl Compiler {
    #[inline]
    fn emit(&mut self, instruction: Instruction) -> usize {
        let index = self.program.code.len();
        self.program.code.push(instruction);
        index
    }

    fn nullable(node: &Expr) -> bool {
        match node {
            Expr::Lit(_, _) | Expr::Dot(_) | Expr::Cat(_, _) | Expr::Class(_, _, _) => false,
            Expr::Anchor(_, _)
            | Expr::Boundary(_, _)
            | Expr::Look(_, _, _, _)
            | Expr::Backref(_, _) => true,
            Expr::Seq(values) => values.iter().all(Self::nullable),
            Expr::Alt(values) => values.iter().any(Self::nullable),
            Expr::Group(_, child) | Expr::Atomic(child) => Self::nullable(child),
            Expr::Repeat(child, minimum, _, _) => *minimum == 0 || Self::nullable(child),
            Expr::Cond(_, yes, no) => Self::nullable(yes) || Self::nullable(no),
        }
    }

    #[inline]
    fn repeat_body(&mut self, child: &Expr, possessive: bool) -> bool {
        if possessive {
            self.emit(Instruction::new(Op::AtomicBegin));
        }
        if !self.node(child) {
            return false;
        }
        if possessive {
            self.emit(Instruction::new(Op::AtomicEnd));
        }
        true
    }

    fn node(&mut self, node: &Expr) -> bool {
        match node {
            Expr::Lit(value, flags) => {
                let mut instruction = Instruction::new(Op::Literal);
                instruction.value = *value as usize;
                instruction.flags = *flags;
                self.emit(instruction);
            }
            Expr::Dot(flags) => {
                let mut instruction = Instruction::new(Op::Dot);
                instruction.flags = *flags;
                self.emit(instruction);
            }
            Expr::Cat(value, flags) => {
                let mut instruction = Instruction::new(Op::Category);
                instruction.value = *value as usize;
                instruction.flags = *flags;
                self.emit(instruction);
            }
            Expr::Class(members, negative, flags) => {
                let index = self.program.classes.len();
                self.program.classes.push(CompiledClass {
                    members: members.clone(),
                    negative: *negative,
                    flags: *flags,
                });
                let mut instruction = Instruction::new(Op::Class);
                instruction.left = index;
                self.emit(instruction);
            }
            Expr::Anchor(value, flags) => {
                let mut instruction = Instruction::new(Op::Anchor);
                instruction.value = *value as usize;
                instruction.flags = *flags;
                self.emit(instruction);
            }
            Expr::Boundary(value, flags) => {
                let mut instruction = Instruction::new(Op::Boundary);
                instruction.value = usize::from(*value);
                instruction.flags = *flags;
                self.emit(instruction);
            }
            Expr::Seq(values) => {
                for value in values {
                    if !self.node(value) {
                        return false;
                    }
                }
            }
            Expr::Alt(values) => {
                if values.is_empty() {
                    return true;
                }
                let mut jumps = Vec::with_capacity(values.len().saturating_sub(1));
                for (index, value) in values.iter().enumerate() {
                    if index + 1 == values.len() {
                        if !self.node(value) {
                            return false;
                        }
                    } else {
                        let split = self.emit(Instruction::new(Op::Split));
                        let first = self.program.code.len();
                        if !self.node(value) {
                            return false;
                        }
                        let jump = self.emit(Instruction::new(Op::Jump));
                        let second = self.program.code.len();
                        self.program.code[split].left = first;
                        self.program.code[split].right = second;
                        jumps.push(jump);
                    }
                }
                let finish = self.program.code.len();
                for jump in jumps {
                    self.program.code[jump].left = finish;
                }
            }
            Expr::Group(number, child) => {
                let mut begin = Instruction::new(Op::SaveBegin);
                begin.left = *number;
                self.emit(begin);
                if !self.node(child) {
                    return false;
                }
                let mut end = Instruction::new(Op::SaveEnd);
                end.left = *number;
                self.emit(end);
            }
            Expr::Backref(number, flags) => {
                let mut instruction = Instruction::new(Op::Backref);
                instruction.left = *number;
                instruction.flags = *flags;
                self.emit(instruction);
            }
            Expr::Repeat(child, minimum, maximum, mode) => {
                if let Some((atom, width, captures)) = repeat_layout(child)
                    && width != 0
                {
                    let index = self.program.runs.len();
                    self.program.runs.push(CompiledRun {
                        atom: atom.clone(),
                        width,
                        minimum: *minimum,
                        maximum: *maximum,
                        mode: *mode,
                        captures,
                    });
                    let mut instruction = Instruction::new(Op::Run);
                    instruction.left = index;
                    self.emit(instruction);
                    return true;
                }

                let possessive = *mode == 2;
                if possessive {
                    self.emit(Instruction::new(Op::AtomicBegin));
                }

                let counted = *minimum > 128
                    || maximum.is_some_and(|limit| limit.saturating_sub(*minimum) > 128);
                if counted {
                    let index = self.program.repeats.len();
                    self.program.repeats.push(CompiledRepeat {
                        minimum: *minimum,
                        maximum: *maximum,
                        minimum_width: width(child, &[]).0,
                        mode: *mode,
                    });

                    let mut start = Instruction::new(Op::RepeatStart);
                    start.left = index;
                    self.emit(start);

                    let mut check = Instruction::new(Op::RepeatCheck);
                    check.left = index;
                    let check_pc = self.emit(check);
                    let body = self.program.code.len();
                    if !self.repeat_body(child, possessive) {
                        return false;
                    }

                    let mut end = Instruction::new(Op::RepeatEnd);
                    end.left = index;
                    end.right = check_pc;
                    let end_pc = self.emit(end);
                    let finish = self.program.code.len();
                    self.program.code[check_pc].right = body;
                    self.program.code[check_pc].value = finish;
                    self.program.code[end_pc].value = finish;
                } else {
                    for _ in 0..*minimum {
                        if !self.repeat_body(child, possessive) {
                            return false;
                        }
                    }
                    match maximum {
                        Some(limit) => {
                            for _ in *minimum..*limit {
                                let split = self.emit(Instruction::new(Op::Split));
                                let body = self.program.code.len();
                                if !self.repeat_body(child, possessive) {
                                    return false;
                                }
                                let finish = self.program.code.len();
                                if *mode == 1 {
                                    self.program.code[split].left = finish;
                                    self.program.code[split].right = body;
                                } else {
                                    self.program.code[split].left = body;
                                    self.program.code[split].right = finish;
                                }
                            }
                        }
                        None => {
                            let split = self.emit(Instruction::new(Op::Split));
                            let body = self.program.code.len();
                            if !self.repeat_body(child, possessive) {
                                return false;
                            }
                            let mut jump = Instruction::new(Op::Jump);
                            jump.left = split;
                            self.emit(jump);
                            let finish = self.program.code.len();
                            if *mode == 1 {
                                self.program.code[split].left = finish;
                                self.program.code[split].right = body;
                            } else {
                                self.program.code[split].left = body;
                                self.program.code[split].right = finish;
                            }
                            if Self::nullable(child) {
                                let guard = self.program.guards;
                                self.program.guards += 1;
                                self.program.code[split].value = guard + 1;
                                self.program.code[split].flags = u32::from(*mode == 1);
                            }
                        }
                    }
                }
                if possessive {
                    self.emit(Instruction::new(Op::AtomicEnd));
                }
            }
            Expr::Look(behind, positive, child, width) => {
                let look = self.emit(Instruction::new(Op::Look));
                let entry = self.program.code.len();
                if !self.node(child) {
                    return false;
                }
                self.emit(Instruction::new(Op::Accept));
                let finish = self.program.code.len();
                self.program.code[look].left = entry;
                self.program.code[look].right = finish;
                self.program.code[look].value = *width;
                self.program.code[look].flags = u32::from(*positive)
                    | (u32::from(*behind) << 1)
                    | (u32::from(contains_group_capture(child)) << 2);
            }
            Expr::Atomic(child) => {
                self.emit(Instruction::new(Op::AtomicBegin));
                if !self.node(child) {
                    return false;
                }
                self.emit(Instruction::new(Op::AtomicEnd));
            }
            Expr::Cond(number, yes, no) => {
                let conditional = self.emit(Instruction::new(Op::Conditional));
                let yes_start = self.program.code.len();
                if !self.node(yes) {
                    return false;
                }
                let jump = self.emit(Instruction::new(Op::Jump));
                let no_start = self.program.code.len();
                if !self.node(no) {
                    return false;
                }
                let finish = self.program.code.len();
                self.program.code[conditional].left = yes_start;
                self.program.code[conditional].right = no_start;
                self.program.code[conditional].value = *number;
                self.program.code[jump].left = finish;
            }
        }
        true
    }

    fn compile(root: &Expr) -> Option<Program> {
        let mut compiler = Self {
            program: Program {
                code: Vec::with_capacity(24),
                classes: Vec::new(),
                runs: Vec::new(),
                repeats: Vec::new(),
                guards: 0,
            },
        };
        if !compiler.node(root) {
            return None;
        }
        compiler.emit(Instruction::new(Op::Accept));
        Some(compiler.program)
    }
}

/// Accept only bytecode whose execution never needs a backtracking stack.
///
/// Fixed-count runs cannot create an alternative: their minimum and maximum
/// coincide, irrespective of the requested greedy, lazy, or possessive mode.
/// All other repetition, control flow, assertions with subprograms, and
/// nonterminal acceptance remain in the original general-purpose interpreter.
fn deterministic_program(program: &Program, groups: usize) -> bool {
    if program.guards != 0 || !program.repeats.is_empty() {
        return false;
    }

    let Some((accept, instructions)) = program.code.split_last() else {
        return false;
    };
    if accept.op != Op::Accept {
        return false;
    }

    instructions.iter().all(|instruction| match instruction.op {
        Op::Literal | Op::Dot | Op::Anchor | Op::Boundary => true,
        Op::Category => char::from_u32(instruction.value as u32).is_some(),
        Op::Class => instruction.left < program.classes.len(),
        Op::SaveBegin | Op::SaveEnd | Op::Backref => instruction.left <= groups,
        Op::Run => program.runs.get(instruction.left).is_some_and(|run| {
            run.width != 0
                && run.maximum == Some(run.minimum)
                && run.mode <= 2
                && run.captures.iter().all(|&(number, begin, end)| {
                    number <= groups && begin <= end && end <= run.width
                })
        }),
        _ => false,
    })
}

/// Recognize only a mandatory, linear run followed by an exact byte literal.
///
/// Capture instructions do not consume a character. Any other instruction can
/// affect whether the run or delimiter is required, so it disables the filter.
fn mandatory_run_delimiter(program: &Program) -> Option<MandatoryRunDelimiter> {
    let mut pc = 0_usize;
    while matches!(
        program.code.get(pc).map(|instruction| instruction.op),
        Some(Op::SaveBegin | Op::SaveEnd)
    ) {
        pc = pc.checked_add(1)?;
    }

    let instruction = program.code.get(pc)?;
    if instruction.op != Op::Run {
        return None;
    }
    let run_index = instruction.left;
    let run = program.runs.get(run_index)?;
    if run.width != 1 || run.minimum == 0 {
        return None;
    }

    pc = pc.checked_add(1)?;
    while matches!(
        program.code.get(pc).map(|instruction| instruction.op),
        Some(Op::SaveBegin | Op::SaveEnd)
    ) {
        pc = pc.checked_add(1)?;
    }

    let instruction = program.code.get(pc)?;
    if instruction.op != Op::Literal || instruction.flags & I != 0 {
        return None;
    }
    Some(MandatoryRunDelimiter {
        run: run_index,
        delimiter: u8::try_from(instruction.value).ok()?,
    })
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
        scanner_runtime_flags: None,
        byte_mode: byte_mode != 0,
        groups: 0,
        names: vec![],
        widths: vec![],
        named,
        global_allowed: true,
        recursion_limit: usize::try_from(unsafe { Py_GetRecursionLimit() })
            .unwrap_or(1_000)
            .saturating_sub(9)
            / 2,
        group_depth: 0,
        open_groups: vec![],
        lookbehind_bases: vec![],
        pending_conditionals: vec![],
        invalid_lookbehind_width: false,
    };
    match parser.parse() {
        Ok(mut root) => {
            let even_suffix_delimiter = even_suffix_delimiter(&root, parser.groups);
            let chars: [u32; 128] = std::array::from_fn(|index| index as u32);
            let folds: [u32; 128] =
                std::array::from_fn(|index| unicode_tables::simple_lower(index as u32));
            let masks: [u8; 128] = std::array::from_fn(|index| unicode_category_mask(index as u32));
            let context = Context {
                chars: &chars,
                folds: &folds,
                masks: &masks,
                bytes: None,
                wide: None,
                end: 128,
            };
            prepare_classes(&mut root, &context);
            let lookbehind = leading_lookbehind(&root);
            let start_anchor = required_start_anchor(&root);
            let starts = start_table(&root, parser.flags);
            let start_set = starts.as_ref().map(search::StartSet::new);
            let prefix = mandatory_literal_prefix(&root, 0);
            let mandatory_literal_prefix = (prefix.length >= 2).then_some(prefix);
            let Some(program) = Compiler::compile(&root) else {
                set_error(
                    "regular expression could not be compiled".into(),
                    None,
                    false,
                );
                return std::ptr::null_mut();
            };
            let deterministic = deterministic_program(&program, parser.groups);
            let mandatory_run_delimiter = mandatory_run_delimiter(&program);
            set_error(String::new(), None, false);
            Box::into_raw(Box::new(Engine {
                program,
                groups: parser.groups,
                names: parser.names,
                flags: parser.flags & !BYTE,
                starts,
                start_set,
                mandatory_literal_prefix,
                mandatory_run_delimiter,
                even_suffix_delimiter,
                leading_lookbehind: lookbehind,
                start_anchor,
                byte_mode: byte_mode != 0,
                deterministic,
            }))
        }
        Err((msg, pos, include)) => {
            set_error(msg, pos, include);
            std::ptr::null_mut()
        }
    }
}

#[repr(C)]
pub struct RebarScannerPhrase {
    source: *const u32,
    length: usize,
    named_positions: *const usize,
    named_values: *const u32,
    named_count: usize,
    byte_mode: u8,
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn rebar_compile_scanner(
    phrases: *const RebarScannerPhrase,
    count: usize,
    flags: u32,
    failed_index: *mut usize,
) -> *mut Engine {
    if !failed_index.is_null() {
        unsafe { *failed_index = usize::MAX };
    }
    if count == 0 {
        set_error("invalid SRE code".into(), None, false);
        return std::ptr::null_mut();
    }
    if phrases.is_null() {
        set_error("null scanner lexicon".into(), None, false);
        return std::ptr::null_mut();
    }
    let type_flags = A | L | U;
    let runtime_flags = if flags & type_flags == 0 {
        flags | A
    } else {
        flags
    };
    let recursion_limit = usize::try_from(unsafe { Py_GetRecursionLimit() })
        .unwrap_or(1_000)
        .saturating_sub(9)
        / 2;
    let mut branches = Vec::with_capacity(count);

    for (index, phrase) in unsafe { slice::from_raw_parts(phrases, count) }
        .iter()
        .enumerate()
    {
        if !failed_index.is_null() {
            unsafe { *failed_index = index };
        }
        let byte_mode = phrase.byte_mode != 0;
        if byte_mode {
            if flags & U != 0 {
                set_error("cannot use UNICODE flag with a bytes pattern".into(), None, false);
                return std::ptr::null_mut();
            }
            if flags & A != 0 && flags & L != 0 {
                set_error("ASCII and LOCALE flags are incompatible".into(), None, false);
                return std::ptr::null_mut();
            }
        } else {
            if flags & L != 0 {
                set_error("cannot use LOCALE flag with a str pattern".into(), None, false);
                return std::ptr::null_mut();
            }
            if flags & A != 0 && flags & U != 0 {
                set_error("ASCII and UNICODE flags are incompatible".into(), None, false);
                return std::ptr::null_mut();
            }
        }
        if phrase.source.is_null() {
            set_error("null scanner phrase".into(), None, false);
            return std::ptr::null_mut();
        }
        let named = if phrase.named_count == 0 {
            Vec::new()
        } else {
            if phrase.named_positions.is_null() || phrase.named_values.is_null() {
                set_error("null named-escape table".into(), None, false);
                return std::ptr::null_mut();
            }
            unsafe { slice::from_raw_parts(phrase.named_positions, phrase.named_count) }
                .iter()
                .copied()
                .zip(
                    unsafe { slice::from_raw_parts(phrase.named_values, phrase.named_count) }
                        .iter()
                        .copied(),
                )
                .collect()
        };
        let mut parser = Parser {
            source: unsafe { slice::from_raw_parts(phrase.source, phrase.length) }.to_vec(),
            at: 0,
            flags: flags | if byte_mode { BYTE } else { 0 },
            scanner_runtime_flags: Some(runtime_flags),
            byte_mode,
            groups: 0,
            names: Vec::new(),
            widths: Vec::new(),
            named,
            global_allowed: true,
            recursion_limit,
            group_depth: 0,
            open_groups: Vec::new(),
            lookbehind_bases: Vec::new(),
            pending_conditionals: Vec::new(),
            invalid_lookbehind_width: false,
        };
        let child = match parser.parse() {
            Ok(child) => child,
            Err((message, position, include)) => {
                set_error(message, position, include);
                return std::ptr::null_mut();
            }
        };
        if parser.groups > count {
            set_error("invalid SRE code".into(), None, false);
            return std::ptr::null_mut();
        }
        branches.push(Expr::Group(index + 1, Box::new(child)));
    }

    let mut root = Expr::Alt(branches);
    let chars: [u32; 128] = std::array::from_fn(|index| index as u32);
    let folds: [u32; 128] =
        std::array::from_fn(|index| unicode_tables::simple_lower(index as u32));
    let masks: [u8; 128] = std::array::from_fn(|index| unicode_category_mask(index as u32));
    let context = Context {
        chars: &chars,
        folds: &folds,
        masks: &masks,
        bytes: None,
        wide: None,
        end: 128,
    };
    prepare_classes(&mut root, &context);
    let lookbehind = leading_lookbehind(&root);
    let start_anchor = required_start_anchor(&root);
    let starts = start_table(&root, runtime_flags);
    let start_set = starts.as_ref().map(search::StartSet::new);
    let prefix = mandatory_literal_prefix(&root, 0);
    let mandatory_literal_prefix = (prefix.length >= 2).then_some(prefix);
    let even_suffix_delimiter = even_suffix_delimiter(&root, count);
    let Some(program) = Compiler::compile(&root) else {
        set_error("regular expression could not be compiled".into(), None, false);
        return std::ptr::null_mut();
    };
    let deterministic = deterministic_program(&program, count);
    let mandatory_run_delimiter = mandatory_run_delimiter(&program);
    if !failed_index.is_null() {
        unsafe { *failed_index = usize::MAX };
    }
    set_error(String::new(), None, false);
    Box::into_raw(Box::new(Engine {
        program,
        groups: count,
        names: Vec::new(),
        flags,
        starts,
        start_set,
        mandatory_literal_prefix,
        mandatory_run_delimiter,
        even_suffix_delimiter,
        leading_lookbehind: lookbehind,
        start_anchor,
        byte_mode: false,
        deterministic,
    }))
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

#[inline]
fn undo_captures(
    undo: &mut InlineStack<CaptureUndo, 48>,
    wanted: usize,
    begins: &mut [isize],
    ends: &mut [isize],
    last: &mut isize,
) {
    while undo.len() > wanted {
        let Some(saved) = undo.pop() else {
            break;
        };
        begins[saved.group] = saved.begin;
        ends[saved.group] = saved.end;
        *last = saved.last;
    }
}

#[inline]
fn mark_capture(
    undo: &mut InlineStack<CaptureUndo, 48>,
    begins: &[isize],
    ends: &[isize],
    group: usize,
    last: isize,
) {
    undo.push(CaptureUndo {
        group,
        begin: begins[group],
        end: ends[group],
        last,
    });
}

#[inline]
fn undo_guards(undo: &mut InlineStack<GuardUndo, 16>, wanted: usize, guards: &mut [usize]) {
    while undo.len() > wanted {
        let Some(saved) = undo.pop() else {
            break;
        };
        guards[saved.slot] = saved.previous;
    }
}

#[inline]
fn enter_guard(
    undo: &mut InlineStack<GuardUndo, 16>,
    guards: &mut [usize],
    slot: usize,
    pos: usize,
) {
    undo.push(GuardUndo {
        slot,
        previous: guards[slot],
    });
    guards[slot] = pos;
}

#[inline]
fn undo_repeats(
    undo: &mut InlineStack<RepeatUndo, 16>,
    wanted: usize,
    repeats: &mut [RepeatState],
) {
    while undo.len() > wanted {
        let Some(saved) = undo.pop() else {
            break;
        };
        repeats[saved.slot] = saved.previous;
    }
}

#[inline]
fn mark_repeat(undo: &mut InlineStack<RepeatUndo, 16>, repeats: &[RepeatState], slot: usize) {
    undo.push(RepeatUndo {
        slot,
        previous: repeats[slot],
    });
}

#[inline]
fn run_look(
    program: &Program,
    context: &Context<'_>,
    pos: usize,
    instruction: Instruction,
    begins: &mut [isize],
    ends: &mut [isize],
    last: &mut isize,
) -> Option<usize> {
    if instruction.flags & 2 != 0 {
        if instruction.value == 0 {
            return run_program(
                program,
                context,
                pos,
                instruction.left,
                false,
                false,
                begins,
                ends,
                last,
            );
        }
        if pos > context.end {
            return None;
        }
        let begin = pos.checked_sub(instruction.value)?;
        let behind_context = Context {
            chars: context.chars,
            folds: context.folds,
            masks: context.masks,
            bytes: context.bytes,
            wide: context.wide,
            end: pos,
        };
        run_program(
            program,
            &behind_context,
            begin,
            instruction.left,
            true,
            false,
            begins,
            ends,
            last,
        )
    } else {
        run_program(
            program,
            context,
            pos,
            instruction.left,
            false,
            false,
            begins,
            ends,
            last,
        )
    }
}

/// Execute a validated, straight-line program without choice or undo stacks.
///
/// A failed candidate must restore every capture: the general interpreter does
/// this with its undo stack, whereas subsequent search candidates here reuse
/// the caller's capture buffers directly.
#[inline]
fn run_deterministic(
    program: &Program,
    context: &Context<'_>,
    start: usize,
    full: bool,
    nonempty: bool,
    begins: &mut [isize],
    ends: &mut [isize],
    last: &mut isize,
) -> Option<usize> {
    let mut pos = start;
    let result = 'execute: {
        for instruction in &program.code {
            match instruction.op {
                Op::Literal => {
                    if pos >= context.end
                        || !eq_lit(
                            instruction.value as u32,
                            context.character(pos),
                            instruction.flags,
                            context,
                            pos,
                        )
                    {
                        break 'execute None;
                    }
                    pos += 1;
                }
                Op::Dot => {
                    if pos >= context.end
                        || (instruction.flags & S == 0 && context.character(pos) == 10)
                    {
                        break 'execute None;
                    }
                    pos += 1;
                }
                Op::Category => {
                    if pos >= context.end
                        || !char::from_u32(instruction.value as u32)
                            .is_some_and(|code| category(code, instruction.flags, context, pos))
                    {
                        break 'execute None;
                    }
                    pos += 1;
                }
                Op::Class => {
                    if pos >= context.end {
                        break 'execute None;
                    }
                    let class = &program.classes[instruction.left];
                    if !class_match(&class.members, class.negative, class.flags, context, pos) {
                        break 'execute None;
                    }
                    pos += 1;
                }
                Op::Anchor => {
                    let matched = match instruction.value as u8 {
                        b'^' => {
                            pos == 0
                                || (instruction.flags & M != 0
                                    && pos > 0
                                    && context.character(pos - 1) == 10)
                        }
                        b'$' => {
                            pos == context.end
                                || (pos.checked_add(1) == Some(context.end)
                                    && pos < context.end
                                    && context.character(pos) == 10)
                                || (instruction.flags & M != 0
                                    && context.has_character(pos)
                                    && context.character(pos) == 10)
                        }
                        b'A' => pos == 0,
                        _ => pos == context.end,
                    };
                    if !matched {
                        break 'execute None;
                    }
                }
                Op::Boundary => {
                    let left = pos > 0 && category('w', instruction.flags, context, pos - 1);
                    let right = pos < context.end && category('w', instruction.flags, context, pos);
                    if (left != right) != (instruction.value != 0) {
                        break 'execute None;
                    }
                }
                Op::SaveBegin => {
                    begins[instruction.left] = pos as isize;
                }
                Op::SaveEnd => {
                    ends[instruction.left] = pos as isize;
                    *last = instruction.left as isize;
                }
                Op::Backref => {
                    let number = instruction.left;
                    let begin = begins[number];
                    let end = ends[number];
                    if begin < 0 || end < begin {
                        break 'execute None;
                    }
                    let begin = begin as usize;
                    let count = end as usize - begin;
                    if count > context.end.saturating_sub(pos)
                        || !(0..count).all(|offset| {
                            eq(
                                context.character(begin + offset),
                                context.character(pos + offset),
                                instruction.flags,
                                context,
                                begin + offset,
                                pos + offset,
                            )
                        })
                    {
                        break 'execute None;
                    }
                    pos += count;
                }
                Op::Run => {
                    let run = &program.runs[instruction.left];
                    if (pos > context.end && run.captures.is_empty())
                        || run.minimum > context.end.saturating_sub(pos) / run.width
                    {
                        break 'execute None;
                    }
                    for matched in 0..run.minimum {
                        let begin = pos + matched * run.width;
                        if !(begin..begin + run.width)
                            .all(|at| repeat_atom_match(&run.atom, context, at))
                        {
                            break 'execute None;
                        }
                    }
                    if run.minimum != 0 {
                        let base = pos + (run.minimum - 1) * run.width;
                        for &(number, begin, end) in &run.captures {
                            begins[number] = (base + begin) as isize;
                            ends[number] = (base + end) as isize;
                            *last = number as isize;
                        }
                    }
                    pos += run.minimum * run.width;
                }
                Op::Accept => {
                    if (!full || pos == context.end) && !(nonempty && pos == start) {
                        break 'execute Some(pos);
                    }
                    break 'execute None;
                }
                _ => break 'execute None,
            }
        }
        None
    };

    if result.is_none() {
        begins.fill(-1);
        ends.fill(-1);
        *last = -1;
    }
    result
}

fn run_program(
    program: &Program,
    context: &Context<'_>,
    start: usize,
    entry: usize,
    full: bool,
    nonempty: bool,
    begins: &mut [isize],
    ends: &mut [isize],
    last: &mut isize,
) -> Option<usize> {
    let mut choices = InlineStack::<Choice, 24>::new();
    let mut undo = InlineStack::<CaptureUndo, 48>::new();
    let mut guard_undo = InlineStack::<GuardUndo, 16>::new();
    let mut repeat_undo = InlineStack::<RepeatUndo, 16>::new();
    let mut atomic = InlineStack::<usize, 12>::new();
    const INLINE_STATE_SLOTS: usize = 8;
    let mut inline_guards = [usize::MAX; INLINE_STATE_SLOTS];
    let mut overflow_guards = Vec::new();
    let mut guards: &mut [usize] = if program.guards <= INLINE_STATE_SLOTS {
        &mut inline_guards[..program.guards]
    } else {
        overflow_guards.resize(program.guards, usize::MAX);
        overflow_guards.as_mut_slice()
    };
    let mut inline_repeats = [RepeatState::default(); INLINE_STATE_SLOTS];
    let mut overflow_repeats = Vec::new();
    let mut repeats: &mut [RepeatState] = if program.repeats.len() <= INLINE_STATE_SLOTS {
        &mut inline_repeats[..program.repeats.len()]
    } else {
        overflow_repeats.resize(program.repeats.len(), RepeatState::default());
        overflow_repeats.as_mut_slice()
    };
    let mut pc = entry;
    let mut pos = start;
    let mut resumed_run: Option<(usize, usize, usize)> = None;

    loop {
        let instruction = program.code[pc];
        let mut succeeded = false;
        match instruction.op {
            Op::Literal => {
                if pos < context.end
                    && eq_lit(
                        instruction.value as u32,
                        context.character(pos),
                        instruction.flags,
                        context,
                        pos,
                    )
                {
                    pos += 1;
                    pc += 1;
                    continue;
                }
            }
            Op::Dot => {
                if pos < context.end && (instruction.flags & S != 0 || context.character(pos) != 10)
                {
                    pos += 1;
                    pc += 1;
                    continue;
                }
            }
            Op::Category => {
                if pos < context.end
                    && char::from_u32(instruction.value as u32)
                        .is_some_and(|code| category(code, instruction.flags, context, pos))
                {
                    pos += 1;
                    pc += 1;
                    continue;
                }
            }
            Op::Class => {
                let class = &program.classes[instruction.left];
                if pos < context.end
                    && class_match(&class.members, class.negative, class.flags, context, pos)
                {
                    pos += 1;
                    pc += 1;
                    continue;
                }
            }
            Op::Anchor => {
                succeeded = match instruction.value as u8 {
                    b'^' => {
                        pos == 0
                            || (instruction.flags & M != 0
                                && pos > 0
                                && context.character(pos - 1) == 10)
                    }
                    b'$' => {
                        pos == context.end
                            || (pos.checked_add(1) == Some(context.end)
                                && pos < context.end
                                && context.character(pos) == 10)
                            || (instruction.flags & M != 0
                                && context.has_character(pos)
                                && context.character(pos) == 10)
                    }
                    b'A' => pos == 0,
                    _ => pos == context.end,
                };
            }
            Op::Boundary => {
                let left = pos > 0 && category('w', instruction.flags, context, pos - 1);
                let right = pos < context.end && category('w', instruction.flags, context, pos);
                succeeded = (left != right) == (instruction.value != 0);
            }
            Op::Split => {
                let guard = instruction.value.checked_sub(1);
                let alternate_enters_guard = guard.filter(|_| instruction.flags & 1 != 0);
                choices.push(Choice {
                    pc: instruction.right,
                    pos,
                    undo: undo.len(),
                    guard_undo: guard_undo.len(),
                    repeat_undo: repeat_undo.len(),
                    atomic_depth: atomic.len(),
                    run_chosen: 0,
                    run_available: 0,
                    run_resume: false,
                    enter_guard: alternate_enters_guard.unwrap_or(usize::MAX),
                });
                if instruction.flags & 1 == 0
                    && let Some(slot) = guard
                {
                    enter_guard(&mut guard_undo, &mut guards, slot, pos);
                }
                pc = instruction.left;
                continue;
            }
            Op::Jump => {
                let target = program.code[instruction.left];
                if target.op == Op::Split && target.value != 0 && guards[target.value - 1] == pos {
                    pc = if target.flags & 1 != 0 {
                        target.left
                    } else {
                        target.right
                    };
                } else {
                    pc = instruction.left;
                }
                continue;
            }
            Op::SaveBegin => {
                let number = instruction.left;
                mark_capture(&mut undo, begins, ends, number, *last);
                begins[number] = pos as isize;
                pc += 1;
                continue;
            }
            Op::SaveEnd => {
                let number = instruction.left;
                mark_capture(&mut undo, begins, ends, number, *last);
                ends[number] = pos as isize;
                *last = number as isize;
                pc += 1;
                continue;
            }
            Op::Backref => {
                let number = instruction.left;
                let begin = begins[number];
                let end = ends[number];
                if begin >= 0 && end >= begin {
                    let begin = begin as usize;
                    let count = end as usize - begin;
                    if count <= context.end.saturating_sub(pos)
                        && (0..count).all(|offset| {
                            eq(
                                context.character(begin + offset),
                                context.character(pos + offset),
                                instruction.flags,
                                context,
                                begin + offset,
                                pos + offset,
                            )
                        })
                    {
                        pos += count;
                        pc += 1;
                        continue;
                    }
                }
            }
            Op::Conditional => {
                let number = instruction.value;
                pc = if begins[number] >= 0 && ends[number] >= begins[number] {
                    instruction.left
                } else {
                    instruction.right
                };
                continue;
            }
            Op::AtomicBegin => {
                atomic.push(choices.len());
                pc += 1;
                continue;
            }
            Op::AtomicEnd => {
                let Some(mark) = atomic.pop() else {
                    return None;
                };
                choices.truncate(mark);
                pc += 1;
                continue;
            }
            Op::Look => {
                let positive = instruction.flags & 1 != 0;
                if instruction.flags & 4 == 0 {
                    let result = run_look(program, context, pos, instruction, begins, ends, last);
                    if result.is_some() == positive {
                        pc = instruction.right;
                        continue;
                    }
                } else {
                    const INLINE_LOOK_CAPTURE_SLOTS: usize = 16;
                    let mut inline_old_begins = [0_isize; INLINE_LOOK_CAPTURE_SLOTS];
                    let mut overflow_old_begins = Vec::new();
                    let old_begins: &[isize] = if begins.len() <= INLINE_LOOK_CAPTURE_SLOTS {
                        let snapshot = &mut inline_old_begins[..begins.len()];
                        snapshot.copy_from_slice(begins);
                        snapshot
                    } else {
                        overflow_old_begins.extend_from_slice(begins);
                        overflow_old_begins.as_slice()
                    };
                    let mut inline_old_ends = [0_isize; INLINE_LOOK_CAPTURE_SLOTS];
                    let mut overflow_old_ends = Vec::new();
                    let old_ends: &[isize] = if ends.len() <= INLINE_LOOK_CAPTURE_SLOTS {
                        let snapshot = &mut inline_old_ends[..ends.len()];
                        snapshot.copy_from_slice(ends);
                        snapshot
                    } else {
                        overflow_old_ends.extend_from_slice(ends);
                        overflow_old_ends.as_slice()
                    };
                    let old_last = *last;
                    let result = run_look(program, context, pos, instruction, begins, ends, last);
                    if result.is_some() == positive {
                        if positive {
                            let look_last = *last;
                            *last = old_last;
                            for number in 1..begins.len() {
                                if begins[number] != old_begins[number]
                                    || ends[number] != old_ends[number]
                                {
                                    let new_begin = begins[number];
                                    let new_end = ends[number];
                                    begins[number] = old_begins[number];
                                    ends[number] = old_ends[number];
                                    mark_capture(&mut undo, begins, ends, number, *last);
                                    begins[number] = new_begin;
                                    ends[number] = new_end;
                                }
                            }
                            if look_last != old_last && undo.len() == 0 {
                                mark_capture(&mut undo, begins, ends, 0, old_last);
                            }
                            *last = look_last;
                        } else {
                            begins.copy_from_slice(&old_begins);
                            ends.copy_from_slice(&old_ends);
                            *last = old_last;
                        }
                        pc = instruction.right;
                        continue;
                    }
                    begins.copy_from_slice(&old_begins);
                    ends.copy_from_slice(&old_ends);
                    *last = old_last;
                }
            }
            Op::RepeatStart => {
                let slot = instruction.left;
                let repeat = program.repeats[slot];
                let room = context.end.saturating_sub(pos);
                if repeat.minimum_width == 0 || repeat.minimum <= room / repeat.minimum_width {
                    mark_repeat(&mut repeat_undo, &repeats, slot);
                    repeats[slot] = RepeatState {
                        count: 0,
                        iteration_start: pos,
                    };
                    pc += 1;
                    continue;
                }
            }
            Op::RepeatCheck => {
                let slot = instruction.left;
                let repeat = program.repeats[slot];
                let count = repeats[slot].count;
                let can_repeat = repeat.maximum.is_none_or(|limit| count < limit);
                let can_exit = count >= repeat.minimum;

                if can_repeat {
                    mark_repeat(&mut repeat_undo, &repeats, slot);
                    repeats[slot].iteration_start = pos;
                    if can_exit {
                        let lazy = repeat.mode == 1;
                        let preferred = if lazy {
                            instruction.value
                        } else {
                            instruction.right
                        };
                        let alternate = if lazy {
                            instruction.right
                        } else {
                            instruction.value
                        };
                        choices.push(Choice {
                            pc: alternate,
                            pos,
                            undo: undo.len(),
                            guard_undo: guard_undo.len(),
                            repeat_undo: repeat_undo.len(),
                            atomic_depth: atomic.len(),
                            run_chosen: 0,
                            run_available: 0,
                            run_resume: false,
                            enter_guard: usize::MAX,
                        });
                        pc = preferred;
                    } else {
                        pc = instruction.right;
                    }
                    continue;
                }
                if can_exit {
                    pc = instruction.value;
                    continue;
                }
            }
            Op::RepeatEnd => {
                let slot = instruction.left;
                let previous = repeats[slot];
                if let Some(count) = previous.count.checked_add(1) {
                    mark_repeat(&mut repeat_undo, &repeats, slot);
                    repeats[slot].count = count;
                    pc = if pos == previous.iteration_start
                        && count >= program.repeats[slot].minimum
                    {
                        instruction.value
                    } else {
                        instruction.right
                    };
                    continue;
                }
            }
            Op::Run => {
                let run = &program.runs[instruction.left];
                if pos > context.end && run.captures.is_empty() {
                    // CPython's repeat-one instruction rejects an inverted
                    // window, even when its minimum is zero. A repeated
                    // capturing child instead uses the general repeat path
                    // and may still contribute its final empty capture.
                    // Preserve that distinction for match and scanners.
                } else {
                    let (chosen, available) = if let Some((resume_pc, count, maximum)) = resumed_run
                        && resume_pc == pc
                    {
                        resumed_run = None;
                        if run.mode == 1 {
                            let begin = pos + (count - 1) * run.width;
                            if (begin..begin + run.width)
                                .all(|at| repeat_atom_match(&run.atom, context, at))
                            {
                                (count, maximum)
                            } else {
                                (usize::MAX, maximum)
                            }
                        } else {
                            (count, maximum)
                        }
                    } else {
                        let room = context.end.saturating_sub(pos);
                        let possible = room / run.width;
                        let limit = run.maximum.map_or(possible, |bound| bound.min(possible));
                        if run.mode == 1 {
                            if run.minimum > limit {
                                (usize::MAX, limit)
                            } else {
                                let mut matched = 0;
                                while matched < run.minimum {
                                    let begin = pos + matched * run.width;
                                    if !(begin..begin + run.width)
                                        .all(|at| repeat_atom_match(&run.atom, context, at))
                                    {
                                        break;
                                    }
                                    matched += 1;
                                }
                                if matched == run.minimum {
                                    (matched, limit)
                                } else {
                                    (usize::MAX, limit)
                                }
                            }
                        } else {
                            let mut available = 0;
                            while available < limit {
                                let begin = pos + available * run.width;
                                if !(begin..begin + run.width)
                                    .all(|at| repeat_atom_match(&run.atom, context, at))
                                {
                                    break;
                                }
                                available += 1;
                            }
                            if available < run.minimum {
                                (usize::MAX, available)
                            } else {
                                (available, available)
                            }
                        }
                    };

                    if chosen != usize::MAX {
                        if run.mode != 2 {
                            let next = if run.mode == 1 {
                                (chosen < available).then_some(chosen + 1)
                            } else {
                                (chosen > run.minimum).then_some(chosen - 1)
                            };
                            if let Some(next) = next {
                                choices.push(Choice {
                                    pc,
                                    pos,
                                    undo: undo.len(),
                                    guard_undo: guard_undo.len(),
                                    repeat_undo: repeat_undo.len(),
                                    atomic_depth: atomic.len(),
                                    run_chosen: next,
                                    run_available: available,
                                    run_resume: true,
                                    enter_guard: usize::MAX,
                                });
                            }
                        }
                        if chosen != 0 {
                            let base = pos + (chosen - 1) * run.width;
                            for &(number, begin, end) in &run.captures {
                                mark_capture(&mut undo, begins, ends, number, *last);
                                begins[number] = (base + begin) as isize;
                                ends[number] = (base + end) as isize;
                                *last = number as isize;
                            }
                        }
                        pos += chosen * run.width;
                        pc += 1;
                        continue;
                    }
                }
            }
            Op::Accept => {
                if (!full || pos == context.end) && !(nonempty && pos == start) {
                    return Some(pos);
                }
            }
        }

        if succeeded {
            pc += 1;
            continue;
        }

        let Some(choice) = choices.pop() else {
            undo_captures(&mut undo, 0, begins, ends, last);
            undo_guards(&mut guard_undo, 0, &mut guards);
            undo_repeats(&mut repeat_undo, 0, &mut repeats);
            return None;
        };
        undo_captures(&mut undo, choice.undo, begins, ends, last);
        undo_guards(&mut guard_undo, choice.guard_undo, &mut guards);
        undo_repeats(&mut repeat_undo, choice.repeat_undo, &mut repeats);
        atomic.truncate(choice.atomic_depth);
        pc = choice.pc;
        pos = choice.pos;
        resumed_run = if choice.run_resume {
            Some((choice.pc, choice.run_chosen, choice.run_available))
        } else {
            None
        };
        if choice.enter_guard != usize::MAX {
            enter_guard(&mut guard_undo, &mut guards, choice.enter_guard, pos);
        }
    }
}

/// Reject a search only when every mandatory delimiter is provably impossible.
///
/// A viable delimiter must have every minimum-width repeated atom immediately
/// before it. Finding one leaves the original ordered, capture-aware VM intact.
#[inline]
fn mandatory_run_delimiter_allows(
    program: &Program,
    required: &MandatoryRunDelimiter,
    context: &Context<'_>,
    values: &[u8],
    first_start: usize,
) -> bool {
    let Some(run) = program.runs.get(required.run) else {
        return true;
    };
    let Some(mut cursor) = first_start.checked_add(run.minimum) else {
        return false;
    };

    while let Some(delimiter) =
        search::next_singleton(values, required.delimiter, cursor, context.end)
    {
        let mut preceding = delimiter;
        let mut remaining = run.minimum;
        let mut viable = true;
        while remaining != 0 {
            let Some(previous) = preceding.checked_sub(1) else {
                viable = false;
                break;
            };
            if previous < first_start || !repeat_atom_match(&run.atom, context, previous) {
                viable = false;
                break;
            }
            preceding = previous;
            remaining -= 1;
        }
        if viable {
            return true;
        }
        let Some(next) = delimiter.checked_add(1) else {
            return false;
        };
        cursor = next;
    }

    false
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
    let program = &engine.program;
    if pos > context.end && mode != 1 {
        return 0;
    }

    let last_start = if mode == 0 && engine.start_anchor == SearchAnchor::Absolute {
        0
    } else if mode == 0 {
        context.end
    } else {
        pos
    };
    let first_start = if mode == 0 {
        engine
            .leading_lookbehind
            .map_or(pos, |width| pos.max(width))
    } else {
        pos
    };
    if mode == 0
        && engine.start_anchor == SearchAnchor::Unrestricted
        && engine.leading_lookbehind.is_none()
        && let Some(required) = engine.mandatory_run_delimiter.as_ref()
        && let Some(values) = context.bytes.or_else(|| {
            context
                .wide
                .filter(|subject| subject.kind == 1)
                .map(|subject| subject.data)
        })
        && !mandatory_run_delimiter_allows(program, required, context, values, first_start)
    {
        return 0;
    }
    begins.fill(-1);
    ends.fill(-1);
    *last = -1;
    let mut start = first_start;
    while start <= last_start {
        if mode == 0 && engine.start_anchor == SearchAnchor::Line {
            let Some(next) = next_line_start(context, start) else {
                return 0;
            };
            start = next;
        }
        if mode == 0
            && start < context.end
            && let Some(starts) = &engine.starts
        {
            let contiguous = context.bytes.or_else(|| {
                context
                    .wide
                    .filter(|subject| subject.kind == 1)
                    .map(|subject| subject.data)
            });
            if let (Some(set), Some(values)) = (&engine.start_set, contiguous)
                && engine.start_anchor == SearchAnchor::Unrestricted
            {
                let Some(next) = set.next(values, start, context.end) else {
                    return 0;
                };
                start = next;
            } else {
                let first = context.character(start);
                if first < 256 && starts[first as usize] == 0 {
                    start += 1;
                    continue;
                }
                if first >= 256 && !wide_prefix_allows(engine, context, start) {
                    start += 1;
                    continue;
                }
            }
        }
        if mode == 0
            && engine.start_anchor == SearchAnchor::Unrestricted
            && engine.leading_lookbehind.is_none()
            && let Some(prefix) = engine.mandatory_literal_prefix.as_ref()
            && let Some(values) = context.bytes.or_else(|| {
                context
                    .wide
                    .filter(|subject| subject.kind == 1)
                    .map(|subject| subject.data)
            })
        {
            let Some(finish) = start.checked_add(usize::from(prefix.length)) else {
                return 0;
            };
            if finish > context.end {
                return 0;
            }
            if values.get(start..finish) != Some(prefix.as_slice()) {
                let Some(next) = start.checked_add(1) else {
                    return 0;
                };
                start = next;
                continue;
            }
        }
        let finish = if engine.deterministic {
            run_deterministic(
                program,
                context,
                start,
                mode == 2,
                nonempty != 0 && start == pos,
                begins,
                ends,
                last,
            )
        } else {
            run_program(
                program,
                context,
                start,
                0,
                mode == 2,
                nonempty != 0 && start == pos,
                begins,
                ends,
                last,
            )
        };
        if let Some(finish) = finish {
            begins[0] = start as isize;
            ends[0] = finish as isize;
            return 1;
        }
        start += 1;
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
        wide: None,
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
        wide: None,
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
pub unsafe extern "C" fn rebar_match_wide(
    handle: *const Engine,
    data: *const u8,
    length: usize,
    kind: u8,
    pos: usize,
    endpos: usize,
    mode: u8,
    nonempty: u8,
    begins: *mut isize,
    ends: *mut isize,
    last: *mut isize,
) -> i32 {
    if handle.is_null()
        || data.is_null()
        || !matches!(kind, 1 | 2 | 4)
        || begins.is_null()
        || ends.is_null()
        || last.is_null()
    {
        return -1;
    }
    let Some(size) = length.checked_mul(usize::from(kind)) else {
        return -1;
    };
    let engine = unsafe { &*handle };
    let storage = unsafe { slice::from_raw_parts(data, size) };
    let (bytes, wide) = if engine.byte_mode {
        if kind != 1 {
            return -1;
        }
        (Some(storage), None)
    } else {
        (
            None,
            Some(BorrowedText {
                data: storage,
                kind,
            }),
        )
    };
    let context = Context {
        chars: &[],
        folds: &[],
        masks: &[],
        bytes,
        wide,
        end: endpos.min(length),
    };
    let begins = unsafe { slice::from_raw_parts_mut(begins, engine.groups + 1) };
    let ends = unsafe { slice::from_raw_parts_mut(ends, engine.groups + 1) };
    run_match(
        engine,
        &context,
        pos.min(length),
        mode,
        nonempty,
        begins,
        ends,
        unsafe { &mut *last },
    )
}

#[inline]
fn collect_even_suffix_delimiters(
    delimiter: EvenSuffixDelimiter,
    text: &[u8],
    pos: usize,
    end: usize,
    capacity: usize,
    starts: &mut [isize],
    finishes: &mut [isize],
    last_values: &mut [isize],
) -> isize {
    if capacity == 0 || pos >= end {
        return 0;
    }

    let mut suffix_even = true;
    let mut quote = search::next_singleton(text, delimiter.quote, pos, end);
    while let Some(at) = quote {
        suffix_even = !suffix_even;
        let Some(next) = at.checked_add(1) else {
            return -1;
        };
        quote = search::next_singleton(text, delimiter.quote, next, end);
    }

    let mut next_quote = search::next_singleton(text, delimiter.quote, pos, end);
    let mut current = pos;
    let mut count = 0;
    while count < capacity {
        let Some(separator) =
            search::next_singleton(text, delimiter.separator, current, end)
        else {
            break;
        };

        while let Some(at) = next_quote {
            if at >= separator {
                break;
            }
            suffix_even = !suffix_even;
            let Some(next) = at.checked_add(1) else {
                return -1;
            };
            next_quote = search::next_singleton(text, delimiter.quote, next, end);
        }

        let Some(next) = separator.checked_add(1) else {
            return -1;
        };
        if suffix_even {
            starts[count] = separator as isize;
            finishes[count] = next as isize;
            last_values[count] = -1;
            count += 1;
        }
        current = next;
    }

    count as isize
}

#[inline]
fn collect_matches(
    engine: &Engine,
    context: &Context<'_>,
    pos: usize,
    capacity: usize,
    starts: &mut [isize],
    finishes: &mut [isize],
    last_values: &mut [isize],
) -> isize {
    if let Some(delimiter) = engine.even_suffix_delimiter
        && let Some(text) = context.bytes.or_else(|| {
            context
                .wide
                .filter(|subject| subject.kind == 1)
                .map(|subject| subject.data)
        })
    {
        return collect_even_suffix_delimiters(
            delimiter,
            text,
            pos,
            context.end.min(text.len()),
            capacity,
            starts,
            finishes,
            last_values,
        );
    }

    let stride = engine.groups + 1;
    let mut current = pos;
    let mut nonempty = 0;
    let mut count = 0;
    while current <= context.end && count < capacity {
        let offset = count * stride;
        let result = run_match(
            engine,
            context,
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
    let end = endpos.min(length);
    let storage = unsafe { slice::from_raw_parts(data, length) };
    let (bytes, wide) = if engine.byte_mode {
        (Some(storage), None)
    } else {
        (
            None,
            Some(BorrowedText {
                data: storage,
                kind: 1,
            }),
        )
    };
    let context = Context {
        chars: &[],
        folds: &[],
        masks: &[],
        bytes,
        wide,
        end,
    };
    collect_matches(
        engine,
        &context,
        pos.min(length),
        capacity,
        starts,
        finishes,
        last_values,
    )
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn rebar_collect_wide(
    handle: *const Engine,
    data: *const u8,
    length: usize,
    kind: u8,
    pos: usize,
    endpos: usize,
    capacity: usize,
    begins: *mut isize,
    ends: *mut isize,
    lasts: *mut isize,
) -> isize {
    if handle.is_null()
        || data.is_null()
        || !matches!(kind, 1 | 2 | 4)
        || begins.is_null()
        || ends.is_null()
        || lasts.is_null()
    {
        return -1;
    }
    let Some(size) = length.checked_mul(usize::from(kind)) else {
        return -1;
    };
    let engine = unsafe { &*handle };
    let Some(total) = capacity.checked_mul(engine.groups + 1) else {
        return -1;
    };
    let storage = unsafe { slice::from_raw_parts(data, size) };
    let (bytes, wide) = if engine.byte_mode {
        if kind != 1 {
            return -1;
        }
        (Some(storage), None)
    } else {
        (
            None,
            Some(BorrowedText {
                data: storage,
                kind,
            }),
        )
    };
    let context = Context {
        chars: &[],
        folds: &[],
        masks: &[],
        bytes,
        wide,
        end: endpos.min(length),
    };
    let starts = unsafe { slice::from_raw_parts_mut(begins, total) };
    let finishes = unsafe { slice::from_raw_parts_mut(ends, total) };
    let last_values = unsafe { slice::from_raw_parts_mut(lasts, capacity) };
    collect_matches(
        engine,
        &context,
        pos.min(length),
        capacity,
        starts,
        finishes,
        last_values,
    )
}

#[cfg(test)]
mod verbose_comment_tokenizer_tests {
    use super::{BYTE, Expr, PResult, Parser, X};

    fn parse(
        pattern: &str,
        lexical_flags: u32,
        byte_mode: bool,
        scanner_runtime: bool,
    ) -> PResult<Expr> {
        let source = if byte_mode {
            pattern.bytes().map(u32::from).collect()
        } else {
            pattern.chars().map(u32::from).collect()
        };
        let flags = lexical_flags | if byte_mode { BYTE } else { 0 };
        let mut parser = Parser {
            source,
            at: 0,
            flags,
            scanner_runtime_flags: scanner_runtime.then_some(flags),
            byte_mode,
            groups: 0,
            names: Vec::new(),
            widths: Vec::new(),
            named: Vec::new(),
            global_allowed: true,
            recursion_limit: 1_000,
            group_depth: 0,
            open_groups: Vec::new(),
            lookbehind_bases: Vec::new(),
            pending_conditionals: Vec::new(),
            invalid_lookbehind_width: false,
        };
        parser.parse()
    }

    fn collect_literals(expression: &Expr, values: &mut Vec<u32>) {
        match expression {
            Expr::Lit(value, _) => values.push(*value),
            Expr::Seq(children) => {
                for child in children {
                    collect_literals(child, values);
                }
            }
            _ => panic!("verbose comment test unexpectedly produced a non-literal expression"),
        }
    }

    fn assert_literals(pattern: &str, flags: u32, expected: &[u32]) {
        for byte_mode in [false, true] {
            for scanner_runtime in [false, true] {
                let expression = parse(pattern, flags, byte_mode, scanner_runtime)
                    .expect("comment pattern must parse");
                let mut actual = Vec::new();
                collect_literals(&expression, &mut actual);
                assert_eq!(
                    actual, expected,
                    "pattern={pattern:?}, byte_mode={byte_mode}, scanner={scanner_runtime}"
                );
            }
        }
    }

    fn assert_error(pattern: &str, flags: u32, message: &str, position: usize) {
        for byte_mode in [false, true] {
            for scanner_runtime in [false, true] {
                let actual = match parse(pattern, flags, byte_mode, scanner_runtime) {
                    Ok(_) => panic!(
                        "pattern={pattern:?}, byte_mode={byte_mode}, \
                         scanner={scanner_runtime} unexpectedly parsed"
                    ),
                    Err(error) => error,
                };
                assert_eq!(
                    actual,
                    (message.to_owned(), Some(position), true),
                    "pattern={pattern:?}, byte_mode={byte_mode}, scanner={scanner_runtime}"
                );
            }
        }
    }

    #[test]
    fn an_escaped_newline_does_not_end_a_verbose_comment() {
        let expected = [u32::from(b'a'), u32::from(b'b')];
        for pattern in [
            "a# ignored\\\nstill ignored\nb",
            "a# ignored\\\\\\\nstill ignored\nb",
            "a# ignored\\\nstill ignored\r\nb",
        ] {
            assert_literals(pattern, X, &expected);
        }
    }

    #[test]
    fn even_backslash_parity_leaves_a_real_comment_terminator() {
        let expected = [u32::from(b'a'), u32::from(b'b')];
        for pattern in [
            "a# ignored\nb",
            "a# ignored\\\\\nb",
            "a# ignored\\\\\\\\\nb",
            "a# ignored\\\r\nb",
            "a# ignored\\\\\r\nb",
        ] {
            assert_literals(pattern, X, &expected);
        }
    }

    #[test]
    fn carriage_return_alone_does_not_end_a_verbose_comment() {
        assert_literals("a# ignored\rb", X, &[u32::from(b'a')]);
        assert_literals("a# ignored\\\n", X, &[u32::from(b'a')]);
        assert_literals("a# ignored\\\\", X, &[u32::from(b'a')]);
    }

    #[test]
    fn scoped_verbose_flags_apply_comment_tokenization_locally() {
        assert_literals(
            "a(?x:# ignored\\\nstill ignored\nb)c",
            0,
            &[u32::from(b'a'), u32::from(b'b'), u32::from(b'c')],
        );
        assert_literals(
            "(?x)a# ignored\\\nstill ignored\nb",
            0,
            &[u32::from(b'a'), u32::from(b'b')],
        );
        assert_literals(
            "(?-x:#\\\nq)",
            X,
            &[u32::from(b'#'), u32::from(b'\n'), u32::from(b'q')],
        );
        assert_literals(
            "a(?x:# ignored\\\nstill ignored\nb(?-x:#\\\nc))d",
            0,
            &[
                u32::from(b'a'),
                u32::from(b'b'),
                u32::from(b'#'),
                u32::from(b'\n'),
                u32::from(b'c'),
                u32::from(b'd'),
            ],
        );
    }

    #[test]
    fn unicode_comment_positions_count_python_code_points() {
        let pattern = "é#🦀\\";
        for scanner_runtime in [false, true] {
            let actual = match parse(pattern, X, false, scanner_runtime) {
                Ok(_) => panic!("a trailing comment escape unexpectedly parsed"),
                Err(error) => error,
            };
            assert_eq!(
                actual,
                (
                    "bad escape (end of pattern)".to_owned(),
                    Some(pattern.chars().count() - 1),
                    true,
                )
            );
        }
    }

    #[test]
    fn verbose_comments_preserve_exact_trailing_escape_errors() {
        for pattern in ["#\\", "a# ignored\\", "a# ignored\\\\\\"] {
            assert_error(pattern, X, "bad escape (end of pattern)", pattern.len() - 1);
        }
    }

    #[test]
    fn parenthesized_comments_consume_escaped_closing_parentheses() {
        let expected = [u32::from(b'a'), u32::from(b'b')];
        for pattern in [
            "a(?# ignored\\) still ignored)b",
            "a(?# ignored\\\\)b",
            "a(?# ignored\\\nstill ignored)b",
            "a(?# ignored\nstill ignored)b",
        ] {
            assert_literals(pattern, 0, &expected);
            assert_literals(pattern, X, &expected);
        }
    }

    #[test]
    fn parenthesized_comments_preserve_exact_tokenization_errors() {
        for flags in [0, X] {
            assert_error("(?#\\)", flags, "missing ), unterminated comment", 0);
            for pattern in ["(?#\\", "a(?#ignored\\"] {
                assert_error(
                    pattern,
                    flags,
                    "bad escape (end of pattern)",
                    pattern.len() - 1,
                );
            }
        }
    }

    #[test]
    fn escaped_comment_newlines_preserve_following_quantifiers() {
        let pattern = "a# ignored\\\nstill ignored\n+";
        for byte_mode in [false, true] {
            for scanner_runtime in [false, true] {
                let expression = parse(pattern, X, byte_mode, scanner_runtime)
                    .expect("comment followed by a quantifier must parse");
                let Expr::Seq(children) = expression else {
                    panic!("a quantified pattern must remain a sequence");
                };
                assert_eq!(children.len(), 1);
                let Expr::Repeat(child, minimum, maximum, mode) = &children[0] else {
                    panic!("the quantifier must remain attached to its literal");
                };
                assert!(matches!(child.as_ref(), Expr::Lit(value, _) if *value == u32::from(b'a')));
                assert_eq!((*minimum, *maximum, *mode), (1, None, 0));
            }
        }
    }
}

#[cfg(test)]
mod assertion_snapshot_tests {
    use super::{run_match, Compiler, Context, Engine, Expr, SearchAnchor};

    fn literal(value: u8) -> Expr {
        Expr::Lit(u32::from(value), 0)
    }

    fn capture(number: usize, child: Expr) -> Expr {
        Expr::Group(number, Box::new(child))
    }

    fn assertion(behind: bool, positive: bool, child: Expr, width: usize) -> Expr {
        Expr::Look(behind, positive, Box::new(child), width)
    }

    fn execute(root: Expr, subject: &[u8], groups: usize) -> (i32, Vec<isize>, Vec<isize>, isize) {
        let program = Compiler::compile(&root).expect("owned test expression must compile");
        let engine = Engine {
            program,
            groups,
            names: Vec::new(),
            flags: 0,
            starts: None,
            start_set: None,
            mandatory_literal_prefix: None,
            mandatory_run_delimiter: None,
            even_suffix_delimiter: None,
            leading_lookbehind: None,
            start_anchor: SearchAnchor::Unrestricted,
            byte_mode: true,
            deterministic: false,
        };
        let context = Context {
            chars: &[],
            folds: &[],
            masks: &[],
            bytes: Some(subject),
            wide: None,
            end: subject.len(),
        };
        let mut begins = vec![-1; groups + 1];
        let mut ends = vec![-1; groups + 1];
        let mut last = -1;
        let result = run_match(
            &engine,
            &context,
            0,
            2,
            0,
            &mut begins,
            &mut ends,
            &mut last,
        );
        (result, begins, ends, last)
    }

    fn assert_sequential_assertion_captures(groups: usize, nested: bool) {
        let captures = Expr::Seq(
            (1..=groups)
                .map(|number| capture(number, literal(b'a')))
                .collect(),
        );
        let inner = assertion(false, true, captures, 0);
        let look = if nested {
            assertion(false, true, inner, 0)
        } else {
            inner
        };
        let consume = Expr::Repeat(Box::new(literal(b'a')), groups, Some(groups), 0);
        let subject = vec![b'a'; groups];
        let (matched, begins, ends, last) =
            execute(Expr::Seq(vec![look, consume]), &subject, groups);

        assert_eq!(matched, 1);
        assert_eq!(begins[0], 0);
        assert_eq!(ends[0], groups as isize);
        for number in 1..=groups {
            assert_eq!(begins[number], (number - 1) as isize);
            assert_eq!(ends[number], number as isize);
        }
        assert_eq!(last, groups as isize);
    }

    #[test]
    fn positive_assertion_preserves_capture_and_lastindex() {
        let root = Expr::Seq(vec![
            assertion(false, true, capture(1, literal(b'a')), 0),
            literal(b'a'),
        ]);
        let (matched, begins, ends, last) = execute(root, b"a", 1);

        assert_eq!(matched, 1);
        assert_eq!(begins, vec![0, 0]);
        assert_eq!(ends, vec![1, 1]);
        assert_eq!(last, 1);
    }

    #[test]
    fn positive_assertion_preserves_later_group_lastindex() {
        let root = Expr::Seq(vec![
            assertion(false, true, capture(1, literal(b'a')), 0),
            capture(2, literal(b'a')),
        ]);
        let (matched, begins, ends, last) = execute(root, b"a", 2);

        assert_eq!(matched, 1);
        assert_eq!(begins, vec![0, 0, 0]);
        assert_eq!(ends, vec![1, 1, 1]);
        assert_eq!(last, 2);
    }

    #[test]
    fn negative_assertion_restores_failed_child_captures() {
        let child = Expr::Seq(vec![capture(1, literal(b'a')), literal(b'b')]);
        let root = Expr::Seq(vec![assertion(false, false, child, 0), literal(b'a')]);
        let (matched, begins, ends, last) = execute(root, b"a", 1);

        assert_eq!(matched, 1);
        assert_eq!(begins, vec![0, -1]);
        assert_eq!(ends, vec![1, -1]);
        assert_eq!(last, -1);
    }

    #[test]
    fn nested_assertions_preserve_both_visible_captures() {
        let nested = assertion(false, true, capture(1, literal(b'a')), 0);
        let outer = Expr::Seq(vec![nested, capture(2, literal(b'a'))]);
        let root = Expr::Seq(vec![assertion(false, true, outer, 0), literal(b'a')]);
        let (matched, begins, ends, last) = execute(root, b"a", 2);

        assert_eq!(matched, 1);
        assert_eq!(begins, vec![0, 0, 0]);
        assert_eq!(ends, vec![1, 1, 1]);
        assert_eq!(last, 2);
    }

    #[test]
    fn failed_alternative_rolls_back_positive_assertion() {
        let first = Expr::Seq(vec![
            assertion(false, true, capture(1, literal(b'a')), 0),
            literal(b'a'),
            literal(b'b'),
        ]);
        let root = Expr::Alt(vec![first, literal(b'a')]);
        let (matched, begins, ends, last) = execute(root, b"a", 1);

        assert_eq!(matched, 1);
        assert_eq!(begins, vec![0, -1]);
        assert_eq!(ends, vec![1, -1]);
        assert_eq!(last, -1);
    }

    #[test]
    fn atomic_group_preserves_successful_assertion_capture() {
        let atomic = Expr::Atomic(Box::new(Expr::Seq(vec![
            assertion(false, true, capture(1, literal(b'a')), 0),
            literal(b'a'),
        ])));
        let root = Expr::Seq(vec![atomic, literal(b'b')]);
        let (matched, begins, ends, last) = execute(root, b"ab", 1);

        assert_eq!(matched, 1);
        assert_eq!(begins, vec![0, 0]);
        assert_eq!(ends, vec![2, 1]);
        assert_eq!(last, 1);
    }

    #[test]
    fn atomic_group_prevents_alternative_capture_leakage() {
        let first = Expr::Seq(vec![
            assertion(false, true, capture(1, literal(b'a')), 0),
            literal(b'a'),
        ]);
        let second = Expr::Seq(vec![literal(b'a'), literal(b'a')]);
        let atomic = Expr::Atomic(Box::new(Expr::Alt(vec![first, second])));
        let root = Expr::Seq(vec![atomic, literal(b'b')]);
        let (matched, begins, ends, last) = execute(root, b"aab", 1);

        assert_eq!(matched, 0);
        assert_eq!(begins, vec![-1, -1]);
        assert_eq!(ends, vec![-1, -1]);
        assert_eq!(last, -1);
    }

    #[test]
    fn assertion_snapshot_uses_exact_inline_boundary() {
        assert_sequential_assertion_captures(15, false);
    }

    #[test]
    fn assertion_snapshot_spills_after_inline_boundary() {
        assert_sequential_assertion_captures(16, false);
    }

    #[test]
    fn assertion_snapshot_preserves_large_heap_spill() {
        assert_sequential_assertion_captures(64, false);
    }

    #[test]
    fn nested_assertion_snapshots_preserve_independent_heap_spills() {
        assert_sequential_assertion_captures(32, true);
    }

    #[test]
    fn negative_assertion_restores_heap_spill_captures() {
        let groups = 32;
        let mut child: Vec<Expr> = (1..=groups)
            .map(|number| capture(number, literal(b'a')))
            .collect();
        child.push(literal(b'b'));
        let look = assertion(false, false, Expr::Seq(child), 0);
        let consume = Expr::Repeat(Box::new(literal(b'a')), groups, Some(groups), 0);
        let subject = vec![b'a'; groups];
        let (matched, begins, ends, last) =
            execute(Expr::Seq(vec![look, consume]), &subject, groups);

        assert_eq!(matched, 1);
        assert_eq!(begins[0], 0);
        assert_eq!(ends[0], groups as isize);
        assert!(begins[1..].iter().all(|value| *value == -1));
        assert!(ends[1..].iter().all(|value| *value == -1));
        assert_eq!(last, -1);
    }

    #[test]
    fn fixed_width_lookbehind_restores_positive_and_negative_captures() {
        let positive = Expr::Seq(vec![
            literal(b'a'),
            assertion(true, true, capture(1, literal(b'a')), 1),
            literal(b'b'),
        ]);
        let (matched, begins, ends, last) = execute(positive, b"ab", 1);
        assert_eq!(matched, 1);
        assert_eq!(begins, vec![0, 0]);
        assert_eq!(ends, vec![2, 1]);
        assert_eq!(last, 1);

        let negative = Expr::Seq(vec![
            literal(b'b'),
            assertion(true, false, capture(1, literal(b'a')), 1),
            literal(b'b'),
        ]);
        let (matched, begins, ends, last) = execute(negative, b"bb", 1);
        assert_eq!(matched, 1);
        assert_eq!(begins, vec![0, -1]);
        assert_eq!(ends, vec![2, -1]);
        assert_eq!(last, -1);
    }
}

#[cfg(test)]
mod locale_ctype_tests {
    use super::{
        category, class_match, contains_locale_sensitive_expression, deterministic_program,
        isalnum, locale_byte_flags, locale_byte_isalnum, locale_byte_lower, locale_byte_other,
        prepare_classes, run_match, start_table, tolower, Compiler, Context, Engine, Expr, Member,
        SearchAnchor, A, BYTE, I, L,
    };
    use std::ffi::c_int;

    fn byte_context(subject: &[u8]) -> Context<'_> {
        Context {
            chars: &[],
            folds: &[],
            masks: &[],
            bytes: Some(subject),
            wide: None,
            end: subject.len(),
        }
    }

    fn locale_match(mut root: Expr, subject: &[u8], groups: usize) -> bool {
        let alphabet: [u8; 128] = std::array::from_fn(|index| index as u8);
        let preparation = byte_context(&alphabet);
        prepare_classes(&mut root, &preparation);
        let starts = start_table(&root, BYTE | L | I);
        let program = Compiler::compile(&root).expect("owned locale expression must compile");
        let deterministic = deterministic_program(&program, groups);
        let engine = Engine {
            program,
            groups,
            names: Vec::new(),
            flags: L | I,
            starts,
            start_set: None,
            mandatory_literal_prefix: None,
            mandatory_run_delimiter: None,
            even_suffix_delimiter: None,
            leading_lookbehind: None,
            start_anchor: SearchAnchor::Unrestricted,
            byte_mode: true,
            deterministic,
        };
        let context = byte_context(subject);
        let mut begins = vec![-1; groups + 1];
        let mut ends = vec![-1; groups + 1];
        let mut last = -1;
        run_match(
            &engine,
            &context,
            0,
            2,
            0,
            &mut begins,
            &mut ends,
            &mut last,
        ) == 1
    }

    #[test]
    fn locale_ctype_requires_both_owned_byte_and_locale_flags() {
        assert!(locale_byte_flags(BYTE | L));
        assert!(locale_byte_flags(BYTE | L | I));
        assert!(!locale_byte_flags(0));
        assert!(!locale_byte_flags(BYTE));
        assert!(!locale_byte_flags(L));
        assert!(!locale_byte_flags(BYTE | A | I));
    }

    #[test]
    fn locale_lower_matches_libc_for_every_unsigned_byte() {
        for byte in u8::MIN..=u8::MAX {
            let raw = unsafe { tolower(c_int::from(byte)) };
            let expected = u8::try_from(raw).map_or(u32::from(byte), u32::from);
            assert_eq!(locale_byte_lower(u32::from(byte)), expected);
        }
        assert_eq!(locale_byte_lower(256), 256);
        assert_eq!(locale_byte_lower(u32::MAX), u32::MAX);
    }

    #[test]
    fn locale_word_membership_matches_libc_for_every_unsigned_byte() {
        for byte in u8::MIN..=u8::MAX {
            let expected = unsafe { isalnum(c_int::from(byte)) != 0 };
            assert_eq!(locale_byte_isalnum(u32::from(byte)), expected);
        }
        assert!(!locale_byte_isalnum(256));
        assert!(!locale_byte_isalnum(u32::MAX));
    }

    #[test]
    fn locale_case_partner_is_a_current_libc_fold_equivalent() {
        for byte in u8::MIN..=u8::MAX {
            let value = u32::from(byte);
            let other = locale_byte_other(value);
            assert!(u8::try_from(other).is_ok());
            assert_eq!(locale_byte_lower(other), locale_byte_lower(value));
            if other == value {
                assert!(
                    (0_u32..=u32::from(u8::MAX))
                        .all(|candidate| candidate == value
                            || locale_byte_lower(candidate) != locale_byte_lower(value))
                );
            }
        }
        assert_eq!(locale_byte_other(256), 256);
        assert_eq!(locale_byte_other(u32::MAX), u32::MAX);
    }

    #[test]
    fn locale_classes_do_not_cache_compile_time_ascii_membership() {
        let alphabet: [u8; 128] = std::array::from_fn(|index| index as u8);
        let context = byte_context(&alphabet);
        let mut dynamic = Expr::Class(
            vec![Member::Lit(u32::from(b'A'))],
            false,
            BYTE | L | I,
        );
        prepare_classes(&mut dynamic, &context);
        let Expr::Class(dynamic_members, _, _) = dynamic else {
            panic!("owned locale expression changed shape");
        };
        assert_eq!(dynamic_members.len(), 1);
        assert!(matches!(dynamic_members[0], Member::Lit(_)));

        let mut ordinary = Expr::Class(vec![Member::Lit(u32::from(b'A'))], false, BYTE | I);
        prepare_classes(&mut ordinary, &context);
        let Expr::Class(ordinary_members, _, _) = ordinary else {
            panic!("owned non-locale expression changed shape");
        };
        assert!(matches!(ordinary_members.first(), Some(Member::Table(_))));
    }

    #[test]
    fn locale_membership_ignores_a_stale_ascii_class_table() {
        let subject = [b'A'];
        let context = byte_context(&subject);
        let members = [Member::Table([0, 0]), Member::Lit(u32::from(b'A'))];
        assert!(class_match(
            &members,
            false,
            BYTE | L | I,
            &context,
            0,
        ));
    }

    #[test]
    fn scoped_locale_disables_stale_compile_time_start_filters() {
        let root = Expr::Seq(vec![Expr::Group(
            1,
            Box::new(Expr::Alt(vec![
                Expr::Lit(0xc5, BYTE | L | I),
                Expr::Lit(u32::from(b'x'), BYTE),
            ])),
        )]);
        assert!(contains_locale_sensitive_expression(&root));
        assert!(start_table(&root, BYTE).is_none());

        let ordinary = Expr::Lit(u32::from(b'A'), BYTE | I);
        assert!(!contains_locale_sensitive_expression(&ordinary));
        assert!(start_table(&ordinary, BYTE | I).is_some());
    }

    #[test]
    fn locale_literals_and_backreferences_use_current_byte_folding() {
        let upper = 0xc5_u32;
        let lower = 0xe5_u32;
        let expected = locale_byte_lower(upper) == locale_byte_lower(lower);
        assert_eq!(
            locale_match(Expr::Lit(upper, BYTE | L | I), &[lower as u8], 0),
            expected,
        );
        let root = Expr::Seq(vec![
            Expr::Group(1, Box::new(Expr::Lit(upper, BYTE | L | I))),
            Expr::Backref(1, BYTE | L | I),
        ]);
        assert_eq!(locale_match(root, &[upper as u8, lower as u8], 1), expected);
    }

    #[test]
    fn locale_word_categories_use_current_libc_membership() {
        for byte in [b'_', b'A', b'0', 0xc5, 0xe5, 0xff] {
            let subject = [byte];
            let context = byte_context(&subject);
            let expected = byte == b'_' || locale_byte_isalnum(u32::from(byte));
            assert_eq!(category('w', BYTE | L, &context, 0), expected);
            assert_eq!(category('W', BYTE | L, &context, 0), !expected);
            assert_eq!(
                locale_match(Expr::Cat('w', BYTE | L), &subject, 0),
                expected,
            );
        }
    }

    #[test]
    fn locale_singleton_complements_use_dynamic_folded_membership() {
        let expected = locale_byte_lower(0xc5) != locale_byte_lower(0xe5);
        let root = Expr::Class(vec![Member::Lit(0xc5)], true, BYTE | L | I);
        assert_eq!(locale_match(root, &[0xe5], 0), expected);
    }

    #[test]
    fn locale_range_complements_preserve_cpython_case_partner_rule() {
        let subject = 0xe5_u32;
        let other = locale_byte_other(subject);
        let raw = |value| (0xc0..=0xd6).contains(&value);
        let expected_negative = !raw(subject) || !raw(other);
        let negative = Expr::Class(
            vec![Member::Range(0xc0, 0xd6)],
            true,
            BYTE | L | I,
        );
        assert_eq!(locale_match(negative, &[subject as u8], 0), expected_negative);

        let expected_positive = (0xc0_u32..=0xd6)
            .any(|value| locale_byte_lower(value) == locale_byte_lower(subject));
        let positive = Expr::Class(
            vec![Member::Range(0xc0, 0xd6)],
            false,
            BYTE | L | I,
        );
        assert_eq!(locale_match(positive, &[subject as u8], 0), expected_positive);
    }
}
