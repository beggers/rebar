//! Isolated, from-scratch experiments for exact ordered regex automata.
//!
//! This is deliberately not a production candidate.  Its companion Python
//! driver invokes CPython's regex engine in a separate oracle-only process.
//! The executable never calls Python, an external regex library, or another
//! candidate.  It tests whether conservative alternative dispatch and
//! fixed-offset literal filtering preserve the same captures and match order
//! as an independently implemented ordered backtracking machine.

#![forbid(unsafe_code)]

use std::hint::black_box;
use std::io::{self, BufRead, Write};
use std::time::Instant;

#[allow(dead_code)]
#[path = "../candidates/rust/src/unicode_tables.rs"]
mod unicode_tables;

const IGNORECASE: u32 = 2;
const DOTALL: u32 = 16;
const ASCII: u32 = 256;
const BYTE: u32 = 1 << 31;
const NO_BRANCH: u16 = u16::MAX;
const MULTIPLE_BRANCHES: u16 = u16::MAX - 1;

// CPython's literal/range case handling is not ordinary Rust Unicode casing.
// These components are copied from the independently generated Python-3.14.6
// compatibility design, not from an external regex implementation.
const CASE_COMPONENTS: [[u32; 4]; 28] = [
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

#[derive(Clone, Debug)]
enum ClassMember {
    Range(u32, u32),
    Category(u8),
}

#[derive(Clone, Debug)]
struct CharacterClass {
    members: Vec<ClassMember>,
    negative: bool,
    flags: u32,
}

#[derive(Clone, Debug)]
enum Expr {
    Empty,
    Literal(u32, u32),
    Dot(u32),
    Class(CharacterClass),
    Sequence(Vec<Expr>),
    Alternative(Vec<Expr>),
    Capture(usize, Box<Expr>),
    Repeat(Box<Expr>, usize, Option<usize>, bool),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct First {
    nullable: bool,
    consumes: bool,
}

#[derive(Clone, Debug)]
enum Instruction {
    Literal(u32, u32),
    Dot(u32),
    Class(usize),
    Split(usize, usize),
    Jump(usize),
    SaveBegin(usize),
    SaveEnd(usize),
    Dispatch(usize),
    Accept,
}

#[derive(Clone, Debug)]
struct Dispatch {
    branches: Vec<Expr>,
    targets: Vec<usize>,
    fallback: usize,
    table: [u16; 256],
}

#[derive(Clone, Debug)]
struct Program {
    code: Vec<Instruction>,
    classes: Vec<CharacterClass>,
    dispatches: Vec<Dispatch>,
    groups: usize,
    needle: Option<Needle>,
}

#[derive(Clone, Debug)]
struct Needle {
    offset: usize,
    values: Vec<u32>,
    failure: Vec<usize>,
}

#[derive(Clone, Copy, Debug, Default)]
struct Counts {
    steps: u64,
    starts: u64,
    choices: u64,
    dispatches: u64,
    filtered_units: u64,
}

#[derive(Clone, Copy, Debug)]
struct Undo {
    group: usize,
    begin: isize,
    end: isize,
    last: isize,
}

#[derive(Clone, Copy, Debug)]
struct Choice {
    pc: usize,
    position: usize,
    undo: usize,
}

#[derive(Clone, Copy, Debug)]
struct Thread {
    pc: usize,
    start: usize,
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct Outcome {
    start: usize,
    end: usize,
    last: isize,
    begins: Vec<isize>,
    ends: Vec<isize>,
    window_start: usize,
    window_end: usize,
}

#[inline]
fn ascii_lower(value: u32) -> u32 {
    if (u32::from(b'A')..=u32::from(b'Z')).contains(&value) {
        value + 32
    } else {
        value
    }
}

#[inline]
fn literal_matches(left: u32, right: u32, flags: u32) -> bool {
    if left == right {
        return true;
    }
    if flags & IGNORECASE == 0 {
        return false;
    }
    if flags & (ASCII | BYTE) != 0 {
        ascii_lower(left) == ascii_lower(right)
    } else {
        unicode_tables::literal_fold(left) == unicode_tables::literal_fold(right)
    }
}

#[inline]
fn range_matches(left: u32, right: u32, value: u32, flags: u32) -> bool {
    if (left..=right).contains(&value) {
        return true;
    }
    if flags & IGNORECASE == 0 {
        return false;
    }
    if flags & (ASCII | BYTE) != 0 {
        let lower = ascii_lower(value);
        let upper = if (u32::from(b'a')..=u32::from(b'z')).contains(&value) {
            value - 32
        } else {
            value
        };
        return (left..=right).contains(&lower) || (left..=right).contains(&upper);
    }
    let lower = unicode_tables::simple_lower(value);
    let upper = if unicode_tables::multi_upper(value) {
        value
    } else {
        unicode_tables::simple_upper(value)
    };
    let fold = unicode_tables::literal_fold(value);
    (left..=right).contains(&lower)
        || (left..=right).contains(&upper)
        || (left..=right).contains(&fold)
        || CASE_COMPONENTS.iter().any(|component| {
            component.iter().any(|&candidate| {
                (left..=right).contains(&candidate)
                    && unicode_tables::literal_fold(candidate) == fold
            })
        })
}

#[inline]
fn category_matches(code: u8, value: u32, flags: u32) -> bool {
    let ascii = flags & (ASCII | BYTE) != 0;
    let lower = code.to_ascii_lowercase();
    let matches = match lower {
        b'd' if ascii => (u32::from(b'0')..=u32::from(b'9')).contains(&value),
        b'd' => unicode_tables::category_mask(value) & unicode_tables::CATEGORY_DECIMAL != 0,
        b's' if ascii => matches!(value, 9 | 10 | 11 | 12 | 13 | 32),
        b's' => unicode_tables::category_mask(value) & unicode_tables::CATEGORY_WHITESPACE != 0,
        b'w' if ascii => {
            value == u32::from(b'_')
                || (u32::from(b'0')..=u32::from(b'9')).contains(&value)
                || (u32::from(b'a')..=u32::from(b'z')).contains(&ascii_lower(value))
        }
        b'w' => {
            value == u32::from(b'_')
                || unicode_tables::category_mask(value) & unicode_tables::CATEGORY_WORD != 0
        }
        _ => false,
    };
    if code.is_ascii_uppercase() {
        !matches
    } else {
        matches
    }
}

#[inline]
fn class_matches(class: &CharacterClass, value: u32) -> bool {
    let present = class.members.iter().any(|member| match *member {
        ClassMember::Range(left, right) => range_matches(left, right, value, class.flags),
        ClassMember::Category(category) => category_matches(category, value, class.flags),
    });
    present != class.negative
}

fn first_at(node: &Expr, value: u32) -> First {
    match node {
        Expr::Empty => First {
            nullable: true,
            consumes: false,
        },
        Expr::Literal(literal, flags) => First {
            nullable: false,
            consumes: literal_matches(*literal, value, *flags),
        },
        Expr::Dot(flags) => First {
            nullable: false,
            consumes: *flags & DOTALL != 0 || value != u32::from(b'\n'),
        },
        Expr::Class(class) => First {
            nullable: false,
            consumes: class_matches(class, value),
        },
        Expr::Capture(_, child) => first_at(child, value),
        Expr::Sequence(children) => {
            let mut consumes = false;
            for child in children {
                let result = first_at(child, value);
                consumes |= result.consumes;
                if !result.nullable {
                    return First {
                        nullable: false,
                        consumes,
                    };
                }
            }
            First {
                nullable: true,
                consumes,
            }
        }
        Expr::Alternative(children) => children.iter().fold(
            First {
                nullable: false,
                consumes: false,
            },
            |mut result, child| {
                let branch = first_at(child, value);
                result.nullable |= branch.nullable;
                result.consumes |= branch.consumes;
                result
            },
        ),
        Expr::Repeat(child, minimum, _, _) => {
            let result = first_at(child, value);
            First {
                nullable: *minimum == 0 || result.nullable,
                consumes: result.consumes,
            }
        }
    }
}

fn nullable(node: &Expr) -> bool {
    match node {
        Expr::Empty => true,
        Expr::Literal(_, _) | Expr::Dot(_) | Expr::Class(_) => false,
        Expr::Capture(_, child) => nullable(child),
        Expr::Sequence(children) => children.iter().all(nullable),
        Expr::Alternative(children) => children.iter().any(nullable),
        Expr::Repeat(child, minimum, _, _) => *minimum == 0 || nullable(child),
    }
}

struct Parser {
    values: Vec<u32>,
    at: usize,
    flags: u32,
    groups: usize,
}

impl Parser {
    fn new(values: Vec<u32>, flags: u32, bytes: bool) -> Self {
        Self {
            values,
            at: 0,
            flags: if bytes { flags | BYTE } else { flags },
            groups: 0,
        }
    }

    fn peek(&self) -> Option<u32> {
        self.values.get(self.at).copied()
    }

    fn take(&mut self) -> Option<u32> {
        let value = self.peek()?;
        self.at += 1;
        Some(value)
    }

    fn eat(&mut self, value: u8) -> bool {
        if self.peek() == Some(u32::from(value)) {
            self.at += 1;
            true
        } else {
            false
        }
    }

    fn parse(mut self) -> Result<(Expr, usize), String> {
        let root = self.alternative()?;
        if self.at != self.values.len() {
            return Err(format!("unexpected pattern codepoint at {}", self.at));
        }
        Ok((root, self.groups))
    }

    fn alternative(&mut self) -> Result<Expr, String> {
        let mut values = vec![self.sequence()?];
        while self.eat(b'|') {
            values.push(self.sequence()?);
        }
        Ok(if values.len() == 1 {
            values.pop().expect("one branch")
        } else {
            Expr::Alternative(values)
        })
    }

    fn sequence(&mut self) -> Result<Expr, String> {
        let mut values = Vec::new();
        while let Some(next) = self.peek() {
            if next == u32::from(b'|') || next == u32::from(b')') {
                break;
            }
            values.push(self.repeated()?);
        }
        Ok(match values.len() {
            0 => Expr::Empty,
            1 => values.pop().expect("one expression"),
            _ => Expr::Sequence(values),
        })
    }

    fn repeated(&mut self) -> Result<Expr, String> {
        let atom = self.atom()?;
        let bounds = if self.eat(b'*') {
            Some((0, None))
        } else if self.eat(b'+') {
            Some((1, None))
        } else if self.eat(b'?') {
            Some((0, Some(1)))
        } else {
            self.bounds()?
        };
        let Some((minimum, maximum)) = bounds else {
            return Ok(atom);
        };
        if maximum.is_some_and(|limit| limit < minimum) {
            return Err("repeat minimum exceeds maximum".to_owned());
        }
        if maximum.is_none() && nullable(&atom) {
            return Err("nullable unbounded repeat is outside this isolated lab".to_owned());
        }
        let lazy = self.eat(b'?');
        if self.peek() == Some(u32::from(b'+')) {
            return Err("possessive repeats are outside this isolated lab".to_owned());
        }
        Ok(Expr::Repeat(Box::new(atom), minimum, maximum, lazy))
    }

    fn bounds(&mut self) -> Result<Option<(usize, Option<usize>)>, String> {
        if self.peek() != Some(u32::from(b'{')) {
            return Ok(None);
        }
        let saved = self.at;
        self.at += 1;
        let Some(minimum) = self.number() else {
            self.at = saved;
            return Ok(None);
        };
        let maximum = if self.eat(b'}') {
            Some(minimum)
        } else if self.eat(b',') {
            let upper = self.number();
            if !self.eat(b'}') {
                self.at = saved;
                return Ok(None);
            }
            upper
        } else {
            self.at = saved;
            return Ok(None);
        };
        if minimum > 256 || maximum.is_some_and(|value| value > 256) {
            return Err("bounded repeat exceeds isolated lab limit".to_owned());
        }
        Ok(Some((minimum, maximum)))
    }

    fn number(&mut self) -> Option<usize> {
        let mut value = 0usize;
        let mut found = false;
        while let Some(next) = self.peek() {
            if !(u32::from(b'0')..=u32::from(b'9')).contains(&next) {
                break;
            }
            value = value
                .checked_mul(10)?
                .checked_add((next - u32::from(b'0')) as usize)?;
            self.at += 1;
            found = true;
        }
        found.then_some(value)
    }

    fn atom(&mut self) -> Result<Expr, String> {
        let value = self.take().ok_or_else(|| "missing atom".to_owned())?;
        match value {
            40 => self.group(),
            91 => self.class(),
            46 => Ok(Expr::Dot(self.flags)),
            92 => self.escape(false),
            42 | 43 | 63 => Err("nothing to repeat".to_owned()),
            94 | 36 => Err("anchors are outside this isolated automata lab".to_owned()),
            _ => Ok(Expr::Literal(value, self.flags)),
        }
    }

    fn group(&mut self) -> Result<Expr, String> {
        if !self.eat(b'?') {
            self.groups += 1;
            let group = self.groups;
            let value = self.alternative()?;
            if !self.eat(b')') {
                return Err("unclosed capturing group".to_owned());
            }
            return Ok(Expr::Capture(group, Box::new(value)));
        }
        if self.eat(b':') {
            let value = self.alternative()?;
            if !self.eat(b')') {
                return Err("unclosed noncapturing group".to_owned());
            }
            return Ok(value);
        }

        let original = self.flags;
        let mut disable = false;
        let mut found = false;
        loop {
            match self.peek() {
                Some(45) if !disable => {
                    disable = true;
                    self.at += 1;
                }
                Some(105) => {
                    found = true;
                    self.at += 1;
                    if disable {
                        self.flags &= !IGNORECASE;
                    } else {
                        self.flags |= IGNORECASE;
                    }
                }
                Some(115) => {
                    found = true;
                    self.at += 1;
                    if disable {
                        self.flags &= !DOTALL;
                    } else {
                        self.flags |= DOTALL;
                    }
                }
                Some(97) if !disable => {
                    found = true;
                    self.at += 1;
                    self.flags |= ASCII;
                }
                _ => break,
            }
        }
        if !found || !self.eat(b':') {
            self.flags = original;
            return Err("unsupported extension or global inline flags".to_owned());
        }
        let result = self.alternative();
        self.flags = original;
        let result = result?;
        if !self.eat(b')') {
            return Err("unclosed scoped-flags group".to_owned());
        }
        Ok(result)
    }

    fn escape(&mut self, inside: bool) -> Result<Expr, String> {
        let code = self.take().ok_or_else(|| "trailing escape".to_owned())?;
        let value = match code {
            100 | 68 | 115 | 83 | 119 | 87 => {
                return Ok(Expr::Class(CharacterClass {
                    members: vec![ClassMember::Category(code as u8)],
                    negative: false,
                    flags: self.flags,
                }));
            }
            110 => u32::from(b'\n'),
            114 => u32::from(b'\r'),
            116 => u32::from(b'\t'),
            102 => 12,
            118 => 11,
            98 if inside => 8,
            98 | 66 | 65 | 90 | 71 => {
                return Err("zero-width assertions are outside this isolated lab".to_owned());
            }
            48..=57 => {
                return Err(
                    "numeric backreferences and octal escapes are outside this isolated lab"
                        .to_owned(),
                );
            }
            120 => self.hex_digits(2)?,
            117 if self.flags & BYTE == 0 => self.hex_digits(4)?,
            85 if self.flags & BYTE == 0 => self.hex_digits(8)?,
            value if value < 128 && (value as u8).is_ascii_alphabetic() => {
                return Err(format!("unsupported escape \\{}", value as u8 as char));
            }
            value => value,
        };
        if self.flags & BYTE != 0 && value > 255 {
            return Err("bytes escape exceeds 255".to_owned());
        }
        if value > 0x10ffff {
            return Err("Unicode escape exceeds maximum codepoint".to_owned());
        }
        Ok(Expr::Literal(value, self.flags))
    }

    fn hex_digits(&mut self, length: usize) -> Result<u32, String> {
        let mut value = 0u32;
        for _ in 0..length {
            let digit = self.take().ok_or_else(|| "short hex escape".to_owned())?;
            let number = match digit {
                48..=57 => digit - 48,
                65..=70 => digit - 55,
                97..=102 => digit - 87,
                _ => return Err("invalid hex escape".to_owned()),
            };
            value = value
                .checked_mul(16)
                .and_then(|current| current.checked_add(number))
                .ok_or_else(|| "hex escape overflow".to_owned())?;
        }
        Ok(value)
    }

    fn class(&mut self) -> Result<Expr, String> {
        let negative = self.eat(b'^');
        let mut members = Vec::new();
        let mut first = true;
        loop {
            if self.peek().is_none() {
                return Err("unclosed character class".to_owned());
            }
            if !first && self.eat(b']') {
                break;
            }
            first = false;
            let atom = if self.eat(b'\\') {
                self.escape(true)?
            } else {
                Expr::Literal(self.take().expect("class value"), self.flags)
            };
            if self.peek() == Some(u32::from(b'-'))
                && self.values.get(self.at + 1).copied() != Some(u32::from(b']'))
            {
                self.at += 1;
                let end = if self.eat(b'\\') {
                    self.escape(true)?
                } else {
                    Expr::Literal(
                        self.take().ok_or_else(|| "missing range end".to_owned())?,
                        self.flags,
                    )
                };
                match (atom, end) {
                    (Expr::Literal(left, _), Expr::Literal(right, _)) if left <= right => {
                        members.push(ClassMember::Range(left, right));
                    }
                    _ => return Err("invalid character class range".to_owned()),
                }
            } else {
                match atom {
                    Expr::Literal(value, _) => members.push(ClassMember::Range(value, value)),
                    Expr::Class(class) => members.extend(class.members),
                    _ => return Err("invalid character class member".to_owned()),
                }
            }
        }
        Ok(Expr::Class(CharacterClass {
            members,
            negative,
            flags: self.flags,
        }))
    }
}

struct Compiler {
    code: Vec<Instruction>,
    classes: Vec<CharacterClass>,
    dispatches: Vec<Dispatch>,
    optimized: bool,
}

impl Compiler {
    fn emit(&mut self, value: Instruction) -> usize {
        let position = self.code.len();
        self.code.push(value);
        position
    }

    fn compile(root: Expr, groups: usize, optimized: bool) -> Result<Program, String> {
        let mut compiler = Self {
            code: Vec::with_capacity(32),
            classes: Vec::new(),
            dispatches: Vec::new(),
            optimized,
        };
        compiler.node(&root)?;
        compiler.emit(Instruction::Accept);
        Ok(Program {
            needle: if optimized { fixed_needle(&root) } else { None },
            code: compiler.code,
            classes: compiler.classes,
            dispatches: compiler.dispatches,
            groups,
        })
    }

    fn node(&mut self, node: &Expr) -> Result<(), String> {
        match node {
            Expr::Empty => {}
            Expr::Literal(value, flags) => {
                self.emit(Instruction::Literal(*value, *flags));
            }
            Expr::Dot(flags) => {
                self.emit(Instruction::Dot(*flags));
            }
            Expr::Class(class) => {
                let index = self.classes.len();
                self.classes.push(class.clone());
                self.emit(Instruction::Class(index));
            }
            Expr::Sequence(values) => {
                for value in values {
                    self.node(value)?;
                }
            }
            Expr::Capture(number, child) => {
                self.emit(Instruction::SaveBegin(*number));
                self.node(child)?;
                self.emit(Instruction::SaveEnd(*number));
            }
            Expr::Alternative(values) => self.alternative(values)?,
            Expr::Repeat(child, minimum, maximum, lazy) => {
                for _ in 0..*minimum {
                    self.node(child)?;
                }
                match maximum {
                    Some(limit) => {
                        for _ in *minimum..*limit {
                            let split = self.emit(Instruction::Split(0, 0));
                            let body = self.code.len();
                            self.node(child)?;
                            let finish = self.code.len();
                            self.code[split] = if *lazy {
                                Instruction::Split(finish, body)
                            } else {
                                Instruction::Split(body, finish)
                            };
                        }
                    }
                    None => {
                        let split = self.emit(Instruction::Split(0, 0));
                        let body = self.code.len();
                        self.node(child)?;
                        self.emit(Instruction::Jump(split));
                        let finish = self.code.len();
                        self.code[split] = if *lazy {
                            Instruction::Split(finish, body)
                        } else {
                            Instruction::Split(body, finish)
                        };
                    }
                }
            }
        }
        Ok(())
    }

    fn alternative(&mut self, branches: &[Expr]) -> Result<(), String> {
        if branches.is_empty() {
            return Ok(());
        }
        let eligible = self.optimized
            && branches.len() >= 3
            && branches.len() < usize::from(MULTIPLE_BRANCHES)
            && branches.iter().all(|branch| !nullable(branch));
        let dispatch_index = if eligible {
            let index = self.dispatches.len();
            self.dispatches.push(Dispatch {
                branches: branches.to_vec(),
                targets: Vec::with_capacity(branches.len()),
                fallback: 0,
                table: [NO_BRANCH; 256],
            });
            self.emit(Instruction::Dispatch(index));
            Some(index)
        } else {
            None
        };

        let fallback = self.code.len();
        let mut targets = Vec::with_capacity(branches.len());
        let mut jumps = Vec::with_capacity(branches.len().saturating_sub(1));
        for (index, branch) in branches.iter().enumerate() {
            if index + 1 == branches.len() {
                targets.push(self.code.len());
                self.node(branch)?;
            } else {
                let split = self.emit(Instruction::Split(0, 0));
                let first = self.code.len();
                targets.push(first);
                self.node(branch)?;
                let jump = self.emit(Instruction::Jump(0));
                let second = self.code.len();
                self.code[split] = Instruction::Split(first, second);
                jumps.push(jump);
            }
        }
        let finish = self.code.len();
        for position in jumps {
            self.code[position] = Instruction::Jump(finish);
        }
        if let Some(index) = dispatch_index {
            let dispatch = &mut self.dispatches[index];
            dispatch.targets = targets;
            dispatch.fallback = fallback;
            for value in 0u32..=255 {
                let mut selected = NO_BRANCH;
                for (number, branch) in dispatch.branches.iter().enumerate() {
                    if first_at(branch, value).consumes {
                        if selected != NO_BRANCH {
                            selected = MULTIPLE_BRANCHES;
                            break;
                        }
                        selected = number as u16;
                    }
                }
                dispatch.table[value as usize] = selected;
            }
        }
        Ok(())
    }
}

fn add_segment(
    node: &Expr,
    offset: &mut usize,
    active: &mut Vec<u32>,
    best: &mut (usize, Vec<u32>),
) -> bool {
    match node {
        Expr::Literal(value, flags) if flags & IGNORECASE == 0 => {
            if active.is_empty() {
                best.0 = best.0.min(*offset);
            }
            active.push(*value);
            *offset += 1;
            true
        }
        Expr::Capture(_, child) => add_segment(child, offset, active, best),
        Expr::Sequence(children) => {
            for child in children {
                if !add_segment(child, offset, active, best) {
                    return false;
                }
            }
            true
        }
        Expr::Class(_) | Expr::Dot(_) | Expr::Literal(_, _) => {
            finish_segment(offset, active, best);
            *offset += 1;
            true
        }
        Expr::Empty => true,
        Expr::Repeat(child, minimum, Some(maximum), _) if minimum == maximum && *minimum <= 32 => {
            for _ in 0..*minimum {
                if !add_segment(child, offset, active, best) {
                    return false;
                }
            }
            true
        }
        Expr::Repeat(_, _, _, _) | Expr::Alternative(_) => {
            finish_segment(offset, active, best);
            false
        }
    }
}

fn finish_segment(offset: &usize, active: &mut Vec<u32>, best: &mut (usize, Vec<u32>)) {
    if active.len() > best.1.len() {
        best.0 = *offset - active.len();
        best.1.clone_from(active);
    }
    active.clear();
}

fn fixed_needle(root: &Expr) -> Option<Needle> {
    let mut offset = 0;
    let mut active = Vec::new();
    let mut best = (usize::MAX, Vec::new());
    let _ = add_segment(root, &mut offset, &mut active, &mut best);
    finish_segment(&offset, &mut active, &mut best);
    if best.1.len() < 2 || best.0 == usize::MAX {
        return None;
    }
    let mut failure = vec![0; best.1.len()];
    let mut matched = 0;
    for index in 1..best.1.len() {
        while matched != 0 && best.1[matched] != best.1[index] {
            matched = failure[matched - 1];
        }
        if best.1[matched] == best.1[index] {
            matched += 1;
        }
        failure[index] = matched;
    }
    Some(Needle {
        offset: best.0,
        values: best.1,
        failure,
    })
}

fn rollback(
    undo: &mut Vec<Undo>,
    length: usize,
    begins: &mut [isize],
    ends: &mut [isize],
    last: &mut isize,
) {
    while undo.len() > length {
        let previous = undo.pop().expect("capture undo exists");
        begins[previous.group] = previous.begin;
        ends[previous.group] = previous.end;
        *last = previous.last;
    }
}

// Captures are transparent to *language acceptance* when a program contains
// no references, conditions, assertions, or other capture-reading operations.
// The isolated parser excludes those operations.  Keep higher-priority
// threads first and deduplicate only the same instruction at the same subject
// position; their possible future is then identical.  The ordinary ordered VM
// is still run once at the selected start to recover every real capture.
fn add_thread(
    program: &Program,
    destination: &mut Vec<Thread>,
    visited: &mut [bool],
    initial: usize,
    start: usize,
    counts: &mut Counts,
) {
    let mut pending = vec![initial];
    while let Some(pc) = pending.pop() {
        if visited[pc] {
            continue;
        }
        visited[pc] = true;
        counts.steps += 1;
        match program.code[pc] {
            Instruction::Split(first, second) => {
                pending.push(second);
                pending.push(first);
            }
            Instruction::Jump(target) => pending.push(target),
            Instruction::SaveBegin(_) | Instruction::SaveEnd(_) => pending.push(pc + 1),
            Instruction::Dispatch(_) => {
                unreachable!("ordered-thread programs are compiled without dispatch")
            }
            Instruction::Literal(_, _)
            | Instruction::Dot(_)
            | Instruction::Class(_)
            | Instruction::Accept => destination.push(Thread { pc, start }),
        }
    }
}

fn ordered_threads(
    program: &Program,
    subject: &[u32],
    start: usize,
    end: usize,
    mode: u8,
    counts: &mut Counts,
) -> Option<(usize, usize)> {
    let mut current = Vec::new();
    let mut visited = vec![false; program.code.len()];
    add_thread(program, &mut current, &mut visited, 0, start, counts);
    let mut accepted = None;

    for position in start..=end {
        let mut following = Vec::new();
        let mut following_visited = vec![false; program.code.len()];
        for thread in &current {
            counts.steps += 1;
            match &program.code[thread.pc] {
                Instruction::Literal(value, flags)
                    if position < end && literal_matches(*value, subject[position], *flags) =>
                {
                    add_thread(
                        program,
                        &mut following,
                        &mut following_visited,
                        thread.pc + 1,
                        thread.start,
                        counts,
                    );
                }
                Instruction::Dot(flags)
                    if position < end
                        && (*flags & DOTALL != 0 || subject[position] != u32::from(b'\n')) =>
                {
                    add_thread(
                        program,
                        &mut following,
                        &mut following_visited,
                        thread.pc + 1,
                        thread.start,
                        counts,
                    );
                }
                Instruction::Class(index)
                    if position < end
                        && class_matches(&program.classes[*index], subject[position]) =>
                {
                    add_thread(
                        program,
                        &mut following,
                        &mut following_visited,
                        thread.pc + 1,
                        thread.start,
                        counts,
                    );
                }
                Instruction::Accept if mode != b'f' || position == end => {
                    accepted = Some((thread.start, position));
                    // Lower-priority current threads cannot replace this
                    // result. Higher-priority threads in `following` may.
                    break;
                }
                _ => {}
            }
        }

        if following.is_empty() {
            if accepted.is_some() {
                return accepted;
            }
            if mode != b's' || position == end {
                return None;
            }
        }
        if accepted.is_none() && mode == b's' && position < end {
            // A later start is lower-priority than every earlier surviving
            // thread. The same-PC deduplication retains that ordering.
            add_thread(
                program,
                &mut following,
                &mut following_visited,
                0,
                position + 1,
                counts,
            );
        }
        if position == end {
            return accepted;
        }
        current = following;
    }
    accepted
}

fn run_at(
    program: &Program,
    subject: &[u32],
    start: usize,
    end: usize,
    full: bool,
    window_start: usize,
    counts: &mut Counts,
) -> Option<Outcome> {
    counts.starts += 1;
    let mut begins = vec![-1; program.groups + 1];
    let mut ends = vec![-1; program.groups + 1];
    let mut last = -1;
    let mut choices: Vec<Choice> = Vec::new();
    let mut undo: Vec<Undo> = Vec::new();
    let mut pc = 0usize;
    let mut position = start;
    loop {
        counts.steps += 1;
        match &program.code[pc] {
            Instruction::Literal(value, flags) => {
                if position < end && literal_matches(*value, subject[position], *flags) {
                    position += 1;
                    pc += 1;
                    continue;
                }
            }
            Instruction::Dot(flags) => {
                if position < end && (*flags & DOTALL != 0 || subject[position] != u32::from(b'\n'))
                {
                    position += 1;
                    pc += 1;
                    continue;
                }
            }
            Instruction::Class(index) => {
                if position < end && class_matches(&program.classes[*index], subject[position]) {
                    position += 1;
                    pc += 1;
                    continue;
                }
            }
            Instruction::Split(first, second) => {
                counts.choices += 1;
                choices.push(Choice {
                    pc: *second,
                    position,
                    undo: undo.len(),
                });
                pc = *first;
                continue;
            }
            Instruction::Jump(target) => {
                pc = *target;
                continue;
            }
            Instruction::SaveBegin(group) => {
                undo.push(Undo {
                    group: *group,
                    begin: begins[*group],
                    end: ends[*group],
                    last,
                });
                begins[*group] = position as isize;
                ends[*group] = -1;
                pc += 1;
                continue;
            }
            Instruction::SaveEnd(group) => {
                undo.push(Undo {
                    group: *group,
                    begin: begins[*group],
                    end: ends[*group],
                    last,
                });
                ends[*group] = position as isize;
                last = *group as isize;
                pc += 1;
                continue;
            }
            Instruction::Dispatch(index) => {
                counts.dispatches += 1;
                let dispatch = &program.dispatches[*index];
                if position >= end {
                    // Every eligible branch consumes at least one codepoint.
                } else {
                    let value = subject[position];
                    let selected = if value < 256 {
                        dispatch.table[value as usize]
                    } else {
                        let mut selected = NO_BRANCH;
                        for (number, branch) in dispatch.branches.iter().enumerate() {
                            if first_at(branch, value).consumes {
                                if selected != NO_BRANCH {
                                    selected = MULTIPLE_BRANCHES;
                                    break;
                                }
                                selected = number as u16;
                            }
                        }
                        selected
                    };
                    if selected == MULTIPLE_BRANCHES {
                        pc = dispatch.fallback;
                        continue;
                    }
                    if selected != NO_BRANCH {
                        pc = dispatch.targets[usize::from(selected)];
                        continue;
                    }
                }
            }
            Instruction::Accept => {
                if !full || position == end {
                    begins[0] = start as isize;
                    ends[0] = position as isize;
                    return Some(Outcome {
                        start,
                        end: position,
                        last,
                        begins,
                        ends,
                        window_start,
                        window_end: end,
                    });
                }
            }
        }
        let Some(choice) = choices.pop() else {
            return None;
        };
        rollback(&mut undo, choice.undo, &mut begins, &mut ends, &mut last);
        position = choice.position;
        pc = choice.pc;
    }
}

fn next_needle(
    subject: &[u32],
    needle: &Needle,
    scan: &mut usize,
    matched: &mut usize,
    end: usize,
    counts: &mut Counts,
) -> Option<usize> {
    while *scan < end {
        let value = subject[*scan];
        counts.filtered_units += 1;
        while *matched != 0 && needle.values[*matched] != value {
            *matched = needle.failure[*matched - 1];
        }
        if needle.values[*matched] == value {
            *matched += 1;
        }
        *scan += 1;
        if *matched == needle.values.len() {
            let found = *scan - needle.values.len();
            *matched = needle.failure[*matched - 1];
            return Some(found);
        }
    }
    None
}

fn normalized(value: isize, length: usize) -> usize {
    if value < 0 {
        0
    } else {
        (value as usize).min(length)
    }
}

fn execute(
    program: &Program,
    subject: &[u32],
    from: isize,
    until: isize,
    mode: u8,
    use_needle: bool,
    use_threads: bool,
) -> (Option<Outcome>, Counts) {
    let start = normalized(from, subject.len());
    let end = normalized(until, subject.len());
    let mut counts = Counts::default();
    if start > end {
        return (None, counts);
    }
    if use_threads {
        let Some((candidate, expected_end)) =
            ordered_threads(program, subject, start, end, mode, &mut counts)
        else {
            return (None, counts);
        };
        let result = run_at(
            program,
            subject,
            candidate,
            end,
            mode == b'f',
            start,
            &mut counts,
        );
        debug_assert!(
            result
                .as_ref()
                .is_some_and(|value| value.end == expected_end),
            "ordered-thread filter must preserve the exact accepted endpoint"
        );
        return (result, counts);
    }
    if mode != b's' {
        if use_needle && let Some(needle) = &program.needle {
            let Some(at) = start.checked_add(needle.offset) else {
                return (None, counts);
            };
            if at
                .checked_add(needle.values.len())
                .is_none_or(|finish| finish > end)
                || subject[at..at + needle.values.len()] != needle.values
            {
                return (None, counts);
            }
        }
        return (
            run_at(
                program,
                subject,
                start,
                end,
                mode == b'f',
                start,
                &mut counts,
            ),
            counts,
        );
    }
    if use_needle && let Some(needle) = &program.needle {
        let Some(mut scan) = start.checked_add(needle.offset) else {
            return (None, counts);
        };
        let mut matched = 0;
        while let Some(occurrence) =
            next_needle(subject, needle, &mut scan, &mut matched, end, &mut counts)
        {
            let position = occurrence - needle.offset;
            if let Some(result) = run_at(program, subject, position, end, false, start, &mut counts)
            {
                return (Some(result), counts);
            }
        }
        return (None, counts);
    }
    for position in start..=end {
        if let Some(result) = run_at(program, subject, position, end, false, start, &mut counts) {
            return (Some(result), counts);
        }
    }
    (None, counts)
}

fn nibble(value: u8) -> Option<u8> {
    match value {
        b'0'..=b'9' => Some(value - b'0'),
        b'a'..=b'f' => Some(value - b'a' + 10),
        b'A'..=b'F' => Some(value - b'A' + 10),
        _ => None,
    }
}

fn hex_bytes(value: &str) -> Result<Vec<u8>, String> {
    if value.len() % 2 != 0 {
        return Err("odd-length hexadecimal field".to_owned());
    }
    value
        .as_bytes()
        .chunks_exact(2)
        .map(|pair| {
            Ok(
                nibble(pair[0]).ok_or_else(|| "invalid hexadecimal".to_owned())? * 16
                    + nibble(pair[1]).ok_or_else(|| "invalid hexadecimal".to_owned())?,
            )
        })
        .collect()
}

fn decode(value: &str, bytes: bool) -> Result<Vec<u32>, String> {
    let raw = hex_bytes(value)?;
    if bytes {
        return Ok(raw.into_iter().map(u32::from).collect());
    }
    if raw.len() % 4 != 0 {
        return Err("text field is not whole UTF-32 codepoints".to_owned());
    }
    raw.chunks_exact(4)
        .map(|item| {
            let value = u32::from_be_bytes([item[0], item[1], item[2], item[3]]);
            if value > 0x10ffff {
                Err("invalid Unicode codepoint".to_owned())
            } else {
                Ok(value)
            }
        })
        .collect()
}

fn format_outcome(
    id: &str,
    outcome: &Option<Outcome>,
    counts: Counts,
    elapsed: u128,
    operations: usize,
    architecture: &str,
) -> String {
    let (status, start, end, last, registers, window_start, window_end) = match outcome {
        Some(result) => {
            let registers = result
                .begins
                .iter()
                .zip(&result.ends)
                .map(|(begin, end)| format!("{begin}:{end}"))
                .collect::<Vec<_>>()
                .join(",");
            (
                "match",
                result.start as isize,
                result.end as isize,
                result.last,
                registers,
                result.window_start as isize,
                result.window_end as isize,
            )
        }
        None => ("none", -1, -1, -1, "-".to_owned(), -1, -1),
    };
    format!(
        "{id}\t{status}\t{start}\t{end}\t{last}\t{registers}\t{window_start}\t{window_end}\t{}\t{}\t{}\t{}\t{}\t{elapsed}\t{operations}\t{architecture}",
        counts.steps, counts.starts, counts.choices, counts.dispatches, counts.filtered_units,
    )
}

fn process(line: &str, default_architecture: &str) -> Result<String, String> {
    let fields: Vec<&str> = line.split('\t').collect();
    if fields.len() < 8 {
        return Err("expected at least eight tab-separated fields".to_owned());
    }
    let id = fields[0];
    let bytes = match fields[1] {
        "b" => true,
        "t" => false,
        _ => return Err("input kind must be b or t".to_owned()),
    };
    let flags = fields[2]
        .parse::<u32>()
        .map_err(|_| "invalid regex flags".to_owned())?;
    let pattern = decode(fields[3], bytes)?;
    let subject = decode(fields[4], bytes)?;
    let from = fields[5]
        .parse::<isize>()
        .map_err(|_| "invalid window start".to_owned())?;
    let until = fields[6]
        .parse::<isize>()
        .map_err(|_| "invalid window end".to_owned())?;
    let mode = match fields[7] {
        "s" => b's',
        "m" => b'm',
        "f" => b'f',
        _ => return Err("mode must be s, m, or f".to_owned()),
    };
    let architecture = fields.get(8).copied().unwrap_or(default_architecture);
    if !matches!(architecture, "ordered" | "dispatch" | "needle" | "pike") {
        return Err("unknown automata architecture".to_owned());
    }
    let operations = fields
        .get(9)
        .map_or(Ok(0), |value| value.parse::<usize>())
        .map_err(|_| "invalid operation count".to_owned())?;
    let warmups = fields
        .get(10)
        .map_or(Ok(0), |value| value.parse::<usize>())
        .map_err(|_| "invalid warmup count".to_owned())?;
    let (root, groups) = Parser::new(pattern, flags, bytes).parse()?;
    let optimized = matches!(architecture, "dispatch" | "needle");
    let program = Compiler::compile(root, groups, optimized)?;
    let filtered = architecture == "needle";
    let threaded = architecture == "pike";
    let (before, counts) = execute(&program, &subject, from, until, mode, filtered, threaded);
    for _ in 0..warmups {
        black_box(execute(
            &program, &subject, from, until, mode, filtered, threaded,
        ));
    }
    let elapsed = if operations == 0 {
        0
    } else {
        let started = Instant::now();
        for _ in 0..operations {
            black_box(execute(
                &program, &subject, from, until, mode, filtered, threaded,
            ));
        }
        started.elapsed().as_nanos()
    };
    let (after, _) = execute(&program, &subject, from, until, mode, filtered, threaded);
    if before != after {
        return Err("pre- and post-timing results differ".to_owned());
    }
    Ok(format_outcome(
        id,
        &before,
        counts,
        elapsed,
        operations,
        architecture,
    ))
}

fn main() {
    let architecture = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "ordered".to_owned());
    if !matches!(
        architecture.as_str(),
        "ordered" | "dispatch" | "needle" | "pike" | "stream" | "probe"
    ) {
        eprintln!("usage: rust_automata_lab [ordered|dispatch|needle|pike|stream|probe]");
        std::process::exit(2);
    }
    let default = if architecture == "stream" || architecture == "probe" {
        "ordered"
    } else {
        architecture.as_str()
    };
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut output = io::BufWriter::new(stdout.lock());
    for (index, result) in stdin.lock().lines().enumerate() {
        let line = match result {
            Ok(value) => value,
            Err(error) => {
                eprintln!("input line {}: {error}", index + 1);
                std::process::exit(2);
            }
        };
        match process(&line, default) {
            Ok(value) => {
                if let Err(error) = writeln!(output, "{value}") {
                    eprintln!("output line {}: {error}", index + 1);
                    std::process::exit(2);
                }
            }
            Err(error) => {
                if architecture == "probe" {
                    let id = line.split('\t').next().unwrap_or("unknown");
                    if let Err(write_error) = writeln!(output, "{id}\terror\t{error}") {
                        eprintln!("output line {}: {write_error}", index + 1);
                        std::process::exit(2);
                    }
                    continue;
                }
                eprintln!("input line {}: {error}", index + 1);
                std::process::exit(2);
            }
        }
    }
    if let Err(error) = output.flush() {
        eprintln!("flush: {error}");
        std::process::exit(2);
    }
}
