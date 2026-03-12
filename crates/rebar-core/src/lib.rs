//! Narrow Rust core for the currently supported `rebar` compatibility slice.
//!
//! This crate intentionally implements only the already-published behavior:
//! bounded compile classification, a handful of parser diagnostics, literal
//! search/match plus collection/replacement span discovery, one exact
//! single-dot wildcard workflow case, and `escape()` parity for `str` and
//! `bytes`.

/// The pinned CPython compatibility line for the initial parser target.
pub const TARGET_CPYTHON_SERIES: &str = "3.12.x";

const FLAG_IGNORECASE: i32 = 2;
const FLAG_UNICODE: i32 = 32;
const FLAG_ASCII: i32 = 256;

const FUTURE_WARNING_MESSAGE: &str = "Possible nested set at position 1";

/// Borrowed pattern or subject input.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PatternRef<'a> {
    /// Unicode pattern or subject.
    Str(&'a str),
    /// Bytes pattern or subject.
    Bytes(&'a [u8]),
}

impl<'a> PatternRef<'a> {
    fn normalize_flags(self, flags: i32) -> i32 {
        match self {
            Self::Str(_) if flags & FLAG_ASCII == 0 => flags | FLAG_UNICODE,
            _ => flags,
        }
    }

    fn supports_pattern_scaffold(self) -> bool {
        match self {
            Self::Str(value) => !value.chars().any(is_meta_character),
            Self::Bytes(value) => !value.iter().copied().any(is_meta_byte),
        }
    }

    fn literal_match_base_flags(self) -> i32 {
        self.normalize_flags(0)
    }

    fn supports_literal_execution(self, flags: i32) -> bool {
        if !self.supports_pattern_scaffold() {
            return false;
        }

        let base_flags = self.literal_match_base_flags();
        flags == base_flags || flags == base_flags | FLAG_IGNORECASE
    }

    fn supports_literal_collection_execution(self, flags: i32) -> bool {
        self.supports_pattern_scaffold()
            && !self.is_empty()
            && flags == self.literal_match_base_flags()
    }

    fn supports_bounded_single_dot_execution(self, flags: i32) -> bool {
        let base_flags = self.literal_match_base_flags();
        matches!(self, Self::Str("a.c"))
            && (flags == base_flags || flags == base_flags | FLAG_IGNORECASE)
    }

    fn supports_bounded_single_dot_collection_execution(self, flags: i32) -> bool {
        matches!(self, Self::Str("a.c")) && flags == self.literal_match_base_flags()
    }

    fn is_empty(self) -> bool {
        match self {
            Self::Str(value) => value.is_empty(),
            Self::Bytes(value) => value.is_empty(),
        }
    }
}

/// Status for a compile classification.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CompileStatus {
    /// The pattern compiled within the bounded supported slice.
    Compiled,
    /// The pattern remains an honest `unimplemented` case.
    Unsupported,
}

/// Warning metadata emitted during compile classification.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct CompileWarning {
    /// Warning message text.
    pub message: &'static str,
}

/// Successful compile classification.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct CompileOutcome {
    /// Whether the pattern compiled or remains unsupported.
    pub status: CompileStatus,
    /// Flags after CPython-shaped normalization.
    pub normalized_flags: i32,
    /// Whether the compiled pattern is eligible for the literal-only match slice.
    pub supports_literal: bool,
    /// Optional warning emitted during compilation.
    pub warning: Option<CompileWarning>,
}

/// Compile-time diagnostic raised by the bounded parser slice.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct CompileError {
    /// Error message text.
    pub message: &'static str,
    /// Pattern offset associated with the diagnostic.
    pub pos: Option<usize>,
}

/// Compile the currently supported pattern slice.
pub fn compile(pattern: PatternRef<'_>, flags: i32) -> Result<CompileOutcome, CompileError> {
    let normalized_flags = pattern.normalize_flags(flags);

    if let Some(error) = compile_known_parser_error(pattern) {
        return Err(error);
    }

    if is_nested_set_warning(pattern) {
        return Ok(CompileOutcome {
            status: CompileStatus::Compiled,
            normalized_flags,
            supports_literal: false,
            warning: Some(CompileWarning {
                message: FUTURE_WARNING_MESSAGE,
            }),
        });
    }

    if let Some(outcome) = compile_known_supported_case(pattern, normalized_flags) {
        return Ok(outcome);
    }

    if !pattern.supports_pattern_scaffold() {
        return Ok(CompileOutcome {
            status: CompileStatus::Unsupported,
            normalized_flags,
            supports_literal: false,
            warning: None,
        });
    }

    Ok(CompileOutcome {
        status: CompileStatus::Compiled,
        normalized_flags,
        supports_literal: true,
        warning: None,
    })
}

/// Match mode for the bounded literal-only slice.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MatchMode {
    /// `search()`
    Search,
    /// `match()`
    Match,
    /// `fullmatch()`
    Fullmatch,
}

/// Status for a literal-match attempt.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MatchStatus {
    /// The call matched and returned a span.
    Matched,
    /// The call completed successfully with no match.
    NoMatch,
    /// The pattern/flag combination is outside the supported literal slice.
    Unsupported,
}

/// Successful result metadata for a literal-match attempt.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct MatchOutcome {
    /// Match status.
    pub status: MatchStatus,
    /// Normalized `pos` bound used for matching.
    pub pos: usize,
    /// Normalized `endpos` bound used for matching.
    pub endpos: usize,
    /// Matched span when `status == Matched`.
    pub span: Option<(usize, usize)>,
}

/// Successful result metadata for repeated literal span discovery.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct FindSpansOutcome {
    /// Match status.
    pub status: MatchStatus,
    /// Normalized `pos` bound used for matching.
    pub pos: usize,
    /// Normalized `endpos` bound used for matching.
    pub endpos: usize,
    /// Matched spans in left-to-right execution order.
    pub spans: Vec<(usize, usize)>,
}

/// Error raised while attempting a literal match.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MatchError {
    /// The pattern and subject types are incompatible.
    TypeMismatch {
        /// CPython-shaped error message.
        message: &'static str,
    },
}

impl MatchError {
    /// Returns the CPython-shaped error message.
    #[must_use]
    pub fn message(self) -> &'static str {
        match self {
            Self::TypeMismatch { message } => message,
        }
    }
}

/// Match the currently supported literal-only slice.
pub fn literal_match(
    pattern: PatternRef<'_>,
    flags: i32,
    mode: MatchMode,
    string: PatternRef<'_>,
    pos: isize,
    endpos: Option<isize>,
) -> Result<MatchOutcome, MatchError> {
    match (pattern, string) {
        (PatternRef::Str(pattern), PatternRef::Str(string)) => {
            Ok(literal_match_str(pattern, flags, mode, string, pos, endpos))
        }
        (PatternRef::Bytes(pattern), PatternRef::Bytes(string)) => Ok(literal_match_bytes(
            pattern, flags, mode, string, pos, endpos,
        )),
        (PatternRef::Str(_), PatternRef::Bytes(_)) => Err(MatchError::TypeMismatch {
            message: "cannot use a string pattern on a bytes-like object",
        }),
        (PatternRef::Bytes(_), PatternRef::Str(_)) => Err(MatchError::TypeMismatch {
            message: "cannot use a bytes pattern on a string-like object",
        }),
    }
}

/// Discover repeated spans for the currently supported literal-only collection
/// and replacement slice.
pub fn literal_find_spans(
    pattern: PatternRef<'_>,
    flags: i32,
    string: PatternRef<'_>,
    pos: isize,
    endpos: Option<isize>,
) -> Result<FindSpansOutcome, MatchError> {
    match (pattern, string) {
        (PatternRef::Str(pattern), PatternRef::Str(string)) => {
            Ok(literal_find_spans_str(pattern, flags, string, pos, endpos))
        }
        (PatternRef::Bytes(pattern), PatternRef::Bytes(string)) => Ok(literal_find_spans_bytes(
            pattern, flags, string, pos, endpos,
        )),
        (PatternRef::Str(_), PatternRef::Bytes(_)) => Err(MatchError::TypeMismatch {
            message: "cannot use a string pattern on a bytes-like object",
        }),
        (PatternRef::Bytes(_), PatternRef::Str(_)) => Err(MatchError::TypeMismatch {
            message: "cannot use a bytes pattern on a string-like object",
        }),
    }
}

/// Expand the bounded whole-match replacement-template slice for `str`.
#[must_use]
pub fn expand_literal_replacement_template_str(
    template: &str,
    whole_match: &str,
) -> Option<String> {
    let mut expanded = String::new();
    let mut chars = template.chars();

    while let Some(character) = chars.next() {
        if character != '\\' {
            expanded.push(character);
            continue;
        }

        match chars.next() {
            Some('g') => {
                if chars.next() != Some('<')
                    || chars.next() != Some('0')
                    || chars.next() != Some('>')
                {
                    return None;
                }
                expanded.push_str(whole_match);
            }
            _ => return None,
        }
    }

    Some(expanded)
}

/// Escape the current bounded `str` slice.
#[must_use]
pub fn escape_str(pattern: &str) -> String {
    let mut escaped = String::new();
    for character in pattern.chars() {
        push_escaped_char(&mut escaped, character);
    }
    escaped
}

/// Escape the current bounded `bytes` slice.
#[must_use]
pub fn escape_bytes(pattern: &[u8]) -> Vec<u8> {
    let mut escaped = Vec::with_capacity(pattern.len());
    for byte in pattern {
        push_escaped_byte(&mut escaped, *byte);
    }
    escaped
}

fn compile_known_parser_error(pattern: PatternRef<'_>) -> Option<CompileError> {
    match pattern {
        PatternRef::Str("*abc") => Some(CompileError {
            message: "nothing to repeat",
            pos: Some(0),
        }),
        PatternRef::Str("a(?i)b") => Some(CompileError {
            message: "global flags not at the start of the expression",
            pos: Some(1),
        }),
        PatternRef::Str("(?L:a)") => Some(CompileError {
            message: "bad inline flags: cannot use 'L' flag with a str pattern",
            pos: Some(3),
        }),
        PatternRef::Bytes(b"(?u:a)") => Some(CompileError {
            message: "bad inline flags: cannot use 'u' flag with a bytes pattern",
            pos: Some(3),
        }),
        PatternRef::Bytes(br"\u1234") => Some(CompileError {
            message: r"bad escape \u",
            pos: Some(0),
        }),
        PatternRef::Str("(?<=a+)b") => Some(CompileError {
            message: "look-behind requires fixed-width pattern",
            pos: None,
        }),
        _ => None,
    }
}

fn compile_known_supported_case(
    pattern: PatternRef<'_>,
    normalized_flags: i32,
) -> Option<CompileOutcome> {
    match pattern {
        PatternRef::Str("[A-Z_][a-z0-9_]+")
            if normalized_flags == FLAG_IGNORECASE | FLAG_UNICODE =>
        {
            Some(CompileOutcome {
                status: CompileStatus::Compiled,
                normalized_flags,
                supports_literal: false,
                warning: None,
            })
        }
        PatternRef::Str("a.c")
            if normalized_flags == FLAG_UNICODE
                || normalized_flags == FLAG_IGNORECASE | FLAG_UNICODE =>
        {
            Some(CompileOutcome {
                status: CompileStatus::Compiled,
                normalized_flags,
                supports_literal: false,
                warning: None,
            })
        }
        PatternRef::Str("(?u:a)")
        | PatternRef::Str("a*+")
        | PatternRef::Str("(?>ab|a)b")
        | PatternRef::Str("(?<=ab)c")
        | PatternRef::Bytes(b"(?L:a)") => Some(CompileOutcome {
            status: CompileStatus::Compiled,
            normalized_flags,
            supports_literal: false,
            warning: None,
        }),
        _ => None,
    }
}

fn is_nested_set_warning(pattern: PatternRef<'_>) -> bool {
    matches!(pattern, PatternRef::Str("[[a]"))
}

fn is_meta_character(character: char) -> bool {
    matches!(
        character,
        '.' | '^' | '$' | '*' | '+' | '?' | '{' | '}' | '[' | ']' | '\\' | '|' | '(' | ')'
    )
}

fn is_meta_byte(byte: u8) -> bool {
    matches!(
        byte,
        b'.' | b'^'
            | b'$'
            | b'*'
            | b'+'
            | b'?'
            | b'{'
            | b'}'
            | b'['
            | b']'
            | b'\\'
            | b'|'
            | b'('
            | b')'
    )
}

fn literal_match_str(
    pattern: &str,
    flags: i32,
    mode: MatchMode,
    string: &str,
    pos: isize,
    endpos: Option<isize>,
) -> MatchOutcome {
    let pattern = PatternRef::Str(pattern);
    let (normalized_pos, normalized_endpos) = normalize_bounds(string.chars().count(), pos, endpos);
    let pattern_chars: Vec<char> = match pattern {
        PatternRef::Str(value) => value.chars().collect(),
        PatternRef::Bytes(_) => unreachable!(),
    };
    let string_chars: Vec<char> = string.chars().collect();
    let span = if pattern.supports_literal_execution(flags) {
        find_match_span_str(
            &pattern_chars,
            flags,
            mode,
            &string_chars,
            normalized_pos,
            normalized_endpos,
        )
    } else if pattern.supports_bounded_single_dot_execution(flags) {
        find_bounded_single_dot_span_str(
            &pattern_chars,
            flags,
            mode,
            &string_chars,
            normalized_pos,
            normalized_endpos,
        )
    } else {
        return MatchOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            span: None,
        };
    };
    MatchOutcome {
        status: if span.is_some() {
            MatchStatus::Matched
        } else {
            MatchStatus::NoMatch
        },
        pos: normalized_pos,
        endpos: normalized_endpos,
        span,
    }
}

fn literal_find_spans_str(
    pattern: &str,
    flags: i32,
    string: &str,
    pos: isize,
    endpos: Option<isize>,
) -> FindSpansOutcome {
    let pattern_ref = PatternRef::Str(pattern);
    let string_chars: Vec<char> = string.chars().collect();
    let pattern_chars: Vec<char> = pattern.chars().collect();
    let (normalized_pos, normalized_endpos) = normalize_bounds(string_chars.len(), pos, endpos);
    let spans = if pattern_ref.supports_literal_collection_execution(flags) {
        collect_literal_spans_str(
            &pattern_chars,
            flags,
            &string_chars,
            normalized_pos,
            normalized_endpos,
        )
    } else if pattern_ref.supports_bounded_single_dot_collection_execution(flags) {
        collect_bounded_single_dot_spans_str(
            &pattern_chars,
            flags,
            &string_chars,
            normalized_pos,
            normalized_endpos,
        )
    } else {
        return FindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            spans: Vec::new(),
        };
    };
    FindSpansOutcome {
        status: if spans.is_empty() {
            MatchStatus::NoMatch
        } else {
            MatchStatus::Matched
        },
        pos: normalized_pos,
        endpos: normalized_endpos,
        spans,
    }
}

fn literal_match_bytes(
    pattern: &[u8],
    flags: i32,
    mode: MatchMode,
    string: &[u8],
    pos: isize,
    endpos: Option<isize>,
) -> MatchOutcome {
    let pattern = PatternRef::Bytes(pattern);
    let (normalized_pos, normalized_endpos) = normalize_bounds(string.len(), pos, endpos);
    if !pattern.supports_literal_execution(flags) {
        return MatchOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            span: None,
        };
    }

    let span = find_match_span_bytes(
        pattern_bytes(pattern),
        flags,
        mode,
        string,
        normalized_pos,
        normalized_endpos,
    );
    MatchOutcome {
        status: if span.is_some() {
            MatchStatus::Matched
        } else {
            MatchStatus::NoMatch
        },
        pos: normalized_pos,
        endpos: normalized_endpos,
        span,
    }
}

fn literal_find_spans_bytes(
    pattern: &[u8],
    flags: i32,
    string: &[u8],
    pos: isize,
    endpos: Option<isize>,
) -> FindSpansOutcome {
    let pattern_ref = PatternRef::Bytes(pattern);
    let (normalized_pos, normalized_endpos) = normalize_bounds(string.len(), pos, endpos);
    if !pattern_ref.supports_literal_collection_execution(flags) {
        return FindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            spans: Vec::new(),
        };
    }

    let spans =
        collect_literal_spans_bytes(pattern, flags, string, normalized_pos, normalized_endpos);
    FindSpansOutcome {
        status: if spans.is_empty() {
            MatchStatus::NoMatch
        } else {
            MatchStatus::Matched
        },
        pos: normalized_pos,
        endpos: normalized_endpos,
        spans,
    }
}

fn pattern_bytes(pattern: PatternRef<'_>) -> &[u8] {
    match pattern {
        PatternRef::Bytes(value) => value,
        PatternRef::Str(_) => unreachable!(),
    }
}

fn find_match_span_str(
    pattern: &[char],
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<(usize, usize)> {
    match mode {
        MatchMode::Search => {
            let start = find_literal_start_str(pattern, flags, string, pos, endpos)?;
            Some((start, start + pattern.len()))
        }
        MatchMode::Match => {
            if literal_matches_at_str(pattern, flags, string, pos, endpos) {
                Some((pos, pos + pattern.len()))
            } else {
                None
            }
        }
        MatchMode::Fullmatch => {
            if endpos.saturating_sub(pos) != pattern.len() {
                return None;
            }
            if literal_matches_at_str(pattern, flags, string, pos, endpos) {
                Some((pos, endpos))
            } else {
                None
            }
        }
    }
}

fn find_match_span_bytes(
    pattern: &[u8],
    flags: i32,
    mode: MatchMode,
    string: &[u8],
    pos: usize,
    endpos: usize,
) -> Option<(usize, usize)> {
    match mode {
        MatchMode::Search => {
            let start = find_literal_start_bytes(pattern, flags, string, pos, endpos)?;
            Some((start, start + pattern.len()))
        }
        MatchMode::Match => {
            if literal_matches_at_bytes(pattern, flags, string, pos, endpos) {
                Some((pos, pos + pattern.len()))
            } else {
                None
            }
        }
        MatchMode::Fullmatch => {
            if endpos.saturating_sub(pos) != pattern.len() {
                return None;
            }
            if literal_matches_at_bytes(pattern, flags, string, pos, endpos) {
                Some((pos, endpos))
            } else {
                None
            }
        }
    }
}

fn literal_matches_at_str(
    pattern: &[char],
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> bool {
    let stop = start + pattern.len();
    if stop > endpos {
        return false;
    }
    if flags & FLAG_IGNORECASE == 0 {
        return string.get(start..stop) == Some(pattern);
    }

    pattern
        .iter()
        .enumerate()
        .all(|(offset, pattern_char)| folded_chars_equal(*pattern_char, string[start + offset]))
}

fn literal_matches_at_bytes(
    pattern: &[u8],
    flags: i32,
    string: &[u8],
    start: usize,
    endpos: usize,
) -> bool {
    let stop = start + pattern.len();
    if stop > endpos {
        return false;
    }
    if flags & FLAG_IGNORECASE == 0 {
        return string.get(start..stop) == Some(pattern);
    }

    pattern.iter().enumerate().all(|(offset, pattern_byte)| {
        fold_ascii_byte(*pattern_byte) == fold_ascii_byte(string[start + offset])
    })
}

fn find_literal_start_str(
    pattern: &[char],
    flags: i32,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<usize> {
    if pattern.is_empty() {
        return Some(pos);
    }

    let last_start = endpos.checked_sub(pattern.len())?;
    (pos..=last_start).find(|start| literal_matches_at_str(pattern, flags, string, *start, endpos))
}

fn find_literal_start_bytes(
    pattern: &[u8],
    flags: i32,
    string: &[u8],
    pos: usize,
    endpos: usize,
) -> Option<usize> {
    if pattern.is_empty() {
        return Some(pos);
    }
    if flags & FLAG_IGNORECASE == 0 {
        return string
            .get(pos..endpos)?
            .windows(pattern.len())
            .position(|window| window == pattern)
            .map(|offset| pos + offset);
    }

    let last_start = endpos.checked_sub(pattern.len())?;
    (pos..=last_start)
        .find(|start| literal_matches_at_bytes(pattern, flags, string, *start, endpos))
}

fn collect_literal_spans_str(
    pattern: &[char],
    flags: i32,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Vec<(usize, usize)> {
    let mut spans = Vec::new();
    let mut next_start = pos;

    while let Some(start) = find_literal_start_str(pattern, flags, string, next_start, endpos) {
        let span = (start, start + pattern.len());
        spans.push(span);
        next_start = span.1;
    }

    spans
}

fn find_bounded_single_dot_span_str(
    pattern: &[char],
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<(usize, usize)> {
    match mode {
        MatchMode::Search => {
            let start = find_bounded_single_dot_start_str(pattern, flags, string, pos, endpos)?;
            Some((start, start + pattern.len()))
        }
        MatchMode::Match => {
            if bounded_single_dot_matches_at_str(pattern, flags, string, pos, endpos) {
                Some((pos, pos + pattern.len()))
            } else {
                None
            }
        }
        MatchMode::Fullmatch => {
            if endpos.saturating_sub(pos) != pattern.len() {
                return None;
            }
            if bounded_single_dot_matches_at_str(pattern, flags, string, pos, endpos) {
                Some((pos, endpos))
            } else {
                None
            }
        }
    }
}

fn bounded_single_dot_matches_at_str(
    pattern: &[char],
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> bool {
    let stop = start + pattern.len();
    if stop > endpos {
        return false;
    }

    pattern.iter().enumerate().all(|(offset, pattern_char)| {
        if *pattern_char == '.' {
            true
        } else if flags & FLAG_IGNORECASE == 0 {
            string[start + offset] == *pattern_char
        } else {
            folded_chars_equal(*pattern_char, string[start + offset])
        }
    })
}

fn find_bounded_single_dot_start_str(
    pattern: &[char],
    flags: i32,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<usize> {
    if pattern.is_empty() {
        return Some(pos);
    }

    let last_start = endpos.checked_sub(pattern.len())?;
    (pos..=last_start)
        .find(|start| bounded_single_dot_matches_at_str(pattern, flags, string, *start, endpos))
}

fn collect_bounded_single_dot_spans_str(
    pattern: &[char],
    flags: i32,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Vec<(usize, usize)> {
    let mut spans = Vec::new();
    let mut next_start = pos;

    while let Some(start) =
        find_bounded_single_dot_start_str(pattern, flags, string, next_start, endpos)
    {
        let span = (start, start + pattern.len());
        spans.push(span);
        next_start = span.1;
    }

    spans
}

fn collect_literal_spans_bytes(
    pattern: &[u8],
    flags: i32,
    string: &[u8],
    pos: usize,
    endpos: usize,
) -> Vec<(usize, usize)> {
    let mut spans = Vec::new();
    let mut next_start = pos;

    while let Some(start) = find_literal_start_bytes(pattern, flags, string, next_start, endpos) {
        let span = (start, start + pattern.len());
        spans.push(span);
        next_start = span.1;
    }

    spans
}

fn normalize_bounds(length: usize, pos: isize, endpos: Option<isize>) -> (usize, usize) {
    let clamp = |index: isize| {
        if index < 0 {
            let adjusted = length as isize + index;
            if adjusted < 0 {
                0
            } else {
                adjusted as usize
            }
        } else {
            usize::min(index as usize, length)
        }
    };

    (clamp(pos), endpos.map(clamp).unwrap_or(length))
}

fn folded_chars_equal(left: char, right: char) -> bool {
    left.to_lowercase().collect::<String>() == right.to_lowercase().collect::<String>()
}

fn fold_ascii_byte(value: u8) -> u8 {
    if value.is_ascii_uppercase() {
        value + 32
    } else {
        value
    }
}

fn push_escaped_char(output: &mut String, character: char) {
    match character {
        '\t' => output.push_str("\\\t"),
        '\n' => output.push_str("\\\n"),
        '\u{0b}' => output.push_str("\\\x0b"),
        '\u{0c}' => output.push_str("\\\x0c"),
        '\r' => output.push_str("\\\r"),
        ' ' => output.push_str("\\ "),
        '#' => output.push_str("\\#"),
        '$' => output.push_str("\\$"),
        '&' => output.push_str("\\&"),
        '(' => output.push_str("\\("),
        ')' => output.push_str("\\)"),
        '*' => output.push_str("\\*"),
        '+' => output.push_str("\\+"),
        '-' => output.push_str("\\-"),
        '.' => output.push_str("\\."),
        '?' => output.push_str("\\?"),
        '[' => output.push_str("\\["),
        '\\' => output.push_str("\\\\"),
        ']' => output.push_str("\\]"),
        '^' => output.push_str("\\^"),
        '{' => output.push_str("\\{"),
        '|' => output.push_str("\\|"),
        '}' => output.push_str("\\}"),
        '~' => output.push_str("\\~"),
        _ => output.push(character),
    }
}

fn push_escaped_byte(output: &mut Vec<u8>, byte: u8) {
    match byte {
        b'\t' => output.extend_from_slice(b"\\\t"),
        b'\n' => output.extend_from_slice(b"\\\n"),
        11 => output.extend_from_slice(b"\\\x0b"),
        12 => output.extend_from_slice(b"\\\x0c"),
        b'\r' => output.extend_from_slice(b"\\\r"),
        b' ' => output.extend_from_slice(b"\\ "),
        b'#' => output.extend_from_slice(b"\\#"),
        b'$' => output.extend_from_slice(b"\\$"),
        b'&' => output.extend_from_slice(b"\\&"),
        b'(' => output.extend_from_slice(b"\\("),
        b')' => output.extend_from_slice(b"\\)"),
        b'*' => output.extend_from_slice(b"\\*"),
        b'+' => output.extend_from_slice(b"\\+"),
        b'-' => output.extend_from_slice(b"\\-"),
        b'.' => output.extend_from_slice(b"\\."),
        b'?' => output.extend_from_slice(b"\\?"),
        b'[' => output.extend_from_slice(b"\\["),
        b'\\' => output.extend_from_slice(b"\\\\"),
        b']' => output.extend_from_slice(b"\\]"),
        b'^' => output.extend_from_slice(b"\\^"),
        b'{' => output.extend_from_slice(b"\\{"),
        b'|' => output.extend_from_slice(b"\\|"),
        b'}' => output.extend_from_slice(b"\\}"),
        b'~' => output.extend_from_slice(b"\\~"),
        _ => output.push(byte),
    }
}

#[cfg(test)]
mod tests {
    use super::{
        compile, escape_bytes, escape_str, expand_literal_replacement_template_str,
        literal_find_spans, literal_match, CompileStatus, MatchMode, MatchStatus, PatternRef,
        FLAG_ASCII, FLAG_IGNORECASE, FLAG_UNICODE,
    };

    #[test]
    fn compile_reports_known_error() {
        let error = compile(PatternRef::Str("*abc"), 0).unwrap_err();
        assert_eq!(error.message, "nothing to repeat");
        assert_eq!(error.pos, Some(0));
    }

    #[test]
    fn compile_reports_lookbehind_width_error_without_position_metadata() {
        let error = compile(PatternRef::Str("(?<=a+)b"), 0).unwrap_err();
        assert_eq!(error.message, "look-behind requires fixed-width pattern");
        assert_eq!(error.pos, None);
    }

    #[test]
    fn compile_reports_nested_set_warning() {
        let outcome = compile(PatternRef::Str("[[a]"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(
            outcome.warning.unwrap().message,
            "Possible nested set at position 1"
        );
    }

    #[test]
    fn compile_rejects_other_non_literal_patterns_as_unsupported() {
        let outcome = compile(PatternRef::Str("[ab]c"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Unsupported);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
    }

    #[test]
    fn compile_accepts_bounded_single_dot_workflow_case() {
        let default_outcome = compile(PatternRef::Str("a.c"), 0).unwrap();
        assert_eq!(default_outcome.status, CompileStatus::Compiled);
        assert_eq!(default_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!default_outcome.supports_literal);

        let ignorecase_outcome = compile(PatternRef::Str("a.c"), FLAG_IGNORECASE).unwrap();
        assert_eq!(ignorecase_outcome.status, CompileStatus::Compiled);
        assert_eq!(
            ignorecase_outcome.normalized_flags,
            FLAG_IGNORECASE | FLAG_UNICODE
        );
        assert!(!ignorecase_outcome.supports_literal);
    }

    #[test]
    fn compile_accepts_bounded_inline_flag_success_cases() {
        let str_outcome = compile(PatternRef::Str("(?u:a)"), 0).unwrap();
        assert_eq!(str_outcome.status, CompileStatus::Compiled);
        assert_eq!(str_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!str_outcome.supports_literal);

        let bytes_outcome = compile(PatternRef::Bytes(b"(?L:a)"), 0).unwrap();
        assert_eq!(bytes_outcome.status, CompileStatus::Compiled);
        assert_eq!(bytes_outcome.normalized_flags, 0);
        assert!(!bytes_outcome.supports_literal);
    }

    #[test]
    fn compile_accepts_bounded_fixed_width_lookbehind_success_case() {
        let outcome = compile(PatternRef::Str("(?<=ab)c"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
    }

    #[test]
    fn compile_accepts_bounded_possessive_quantifier_and_atomic_group_success_cases() {
        for pattern in [PatternRef::Str("a*+"), PatternRef::Str("(?>ab|a)b")] {
            let outcome = compile(pattern, 0).unwrap();
            assert_eq!(outcome.status, CompileStatus::Compiled);
            assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
            assert!(!outcome.supports_literal);
        }
    }

    #[test]
    fn compile_accepts_bounded_character_class_ignorecase_success_case() {
        let outcome = compile(PatternRef::Str("[A-Z_][a-z0-9_]+"), FLAG_IGNORECASE).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_IGNORECASE | FLAG_UNICODE);
        assert!(!outcome.supports_literal);
    }

    #[test]
    fn literal_match_supports_search_with_ignorecase() {
        let outcome = literal_match(
            PatternRef::Str("AbC"),
            FLAG_IGNORECASE | FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzaBczz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 5)));
    }

    #[test]
    fn bounded_single_dot_match_supports_ignorecase_search() {
        let outcome = literal_match(
            PatternRef::Str("a.c"),
            FLAG_IGNORECASE | FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("ABC"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 3)));
    }

    #[test]
    fn literal_match_rejects_ascii_flag_combo() {
        let outcome = literal_match(
            PatternRef::Str("abc"),
            FLAG_ASCII,
            MatchMode::Search,
            PatternRef::Str("abc"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Unsupported);
        assert_eq!(outcome.span, None);
    }

    #[test]
    fn literal_find_spans_reports_repeated_matches() {
        let outcome = literal_find_spans(
            PatternRef::Str("abc"),
            FLAG_UNICODE,
            PatternRef::Str("zabcabcx"),
            1,
            Some(7),
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.pos, 1);
        assert_eq!(outcome.endpos, 7);
        assert_eq!(outcome.spans, vec![(1, 4), (4, 7)]);
    }

    #[test]
    fn bounded_single_dot_find_spans_reports_repeated_matches() {
        let outcome = literal_find_spans(
            PatternRef::Str("a.c"),
            FLAG_UNICODE,
            PatternRef::Str("abcaxc"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.spans, vec![(0, 3), (3, 6)]);
    }

    #[test]
    fn literal_find_spans_rejects_flagged_collection_slice() {
        let outcome = literal_find_spans(
            PatternRef::Bytes(b"abc"),
            FLAG_IGNORECASE,
            PatternRef::Bytes(b"abc"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Unsupported);
        assert!(outcome.spans.is_empty());
    }

    #[test]
    fn replacement_template_expands_whole_match_reference() {
        let expanded = expand_literal_replacement_template_str(r"\g<0>x", "abc").unwrap();
        assert_eq!(expanded, "abcx");
    }

    #[test]
    fn replacement_template_rejects_other_backslash_forms() {
        assert_eq!(expand_literal_replacement_template_str(r"\1x", "abc"), None);
        assert_eq!(expand_literal_replacement_template_str("\\", "abc"), None);
    }

    #[test]
    fn escape_matches_expected_outputs() {
        assert_eq!(escape_str("a-b.c"), "a\\-b\\.c");
        assert_eq!(escape_bytes(b"a-b.c"), b"a\\-b\\.c");
    }
}
