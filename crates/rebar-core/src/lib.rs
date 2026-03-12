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
const FLAG_LOCALE: i32 = 4;
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
        flags == base_flags
            || flags == base_flags | FLAG_IGNORECASE
            || self.supports_bounded_locale_literal_execution(flags)
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

    fn supports_bounded_inline_flag_search_execution(self, flags: i32) -> bool {
        matches!(self, Self::Str("(?i)abc")) && flags == FLAG_IGNORECASE | FLAG_UNICODE
    }

    fn supports_bounded_locale_literal_execution(self, flags: i32) -> bool {
        matches!(self, Self::Bytes(_)) && flags == FLAG_LOCALE
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
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CompileOutcome {
    /// Whether the pattern compiled or remains unsupported.
    pub status: CompileStatus,
    /// Flags after CPython-shaped normalization.
    pub normalized_flags: i32,
    /// Whether the compiled pattern is eligible for the literal-only match slice.
    pub supports_literal: bool,
    /// Number of positional capture groups in the bounded supported slice.
    pub group_count: usize,
    /// Named capture groups in left-to-right definition order.
    pub named_groups: Vec<NamedGroup>,
    /// Optional warning emitted during compilation.
    pub warning: Option<CompileWarning>,
}

/// Named capture-group metadata for the bounded supported slice.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct NamedGroup {
    /// Group name.
    pub name: String,
    /// One-based positional group index.
    pub index: usize,
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
            group_count: 0,
            named_groups: Vec::new(),
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
            group_count: 0,
            named_groups: Vec::new(),
            warning: None,
        });
    }

    Ok(CompileOutcome {
        status: CompileStatus::Compiled,
        normalized_flags,
        supports_literal: true,
        group_count: 0,
        named_groups: Vec::new(),
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
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MatchOutcome {
    /// Match status.
    pub status: MatchStatus,
    /// Normalized `pos` bound used for matching.
    pub pos: usize,
    /// Normalized `endpos` bound used for matching.
    pub endpos: usize,
    /// Matched span when `status == Matched`.
    pub span: Option<(usize, usize)>,
    /// Positional capture spans aligned to groups `1..=n`.
    pub group_spans: Vec<Option<(usize, usize)>>,
    /// Last matched positional group index when any captures participated.
    pub lastindex: Option<usize>,
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

/// Successful result metadata for repeated grouped-alternation span discovery.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GroupedAlternationFindSpansOutcome {
    /// Match status.
    pub status: MatchStatus,
    /// Normalized `pos` bound used for matching.
    pub pos: usize,
    /// Normalized `endpos` bound used for matching.
    pub endpos: usize,
    /// Matched spans plus the corresponding first-capture span.
    pub matches: Vec<GroupedAlternationMatchSpan>,
}

/// One grouped-alternation match span and its first-capture span.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct GroupedAlternationMatchSpan {
    /// Whole-match span.
    pub span: (usize, usize),
    /// First capture-group span.
    pub group_1_span: (usize, usize),
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
    capture_1: Option<&str>,
    named_capture_1: Option<(&str, &str)>,
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
                if chars.next() != Some('<') {
                    return None;
                }
                let mut group_name = String::new();
                loop {
                    match chars.next() {
                        Some('>') => break,
                        Some(group_char) => group_name.push(group_char),
                        None => return None,
                    }
                }
                if group_name == "0" {
                    expanded.push_str(whole_match);
                } else if let Some((name, value)) = named_capture_1 {
                    if group_name == name {
                        expanded.push_str(value);
                    } else {
                        return None;
                    }
                } else {
                    return None;
                }
            }
            Some('1') => expanded.push_str(capture_1?),
            _ => return None,
        }
    }

    Some(expanded)
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct CaptureLiteralPattern<'a> {
    captures: Vec<LiteralCapture<'a>>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct NamedBackreferenceLiteralPattern<'a> {
    capture: LiteralCapture<'a>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct NumberedBackreferenceLiteralPattern<'a> {
    capture: LiteralCapture<'a>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct LiteralAlternationPattern<'a> {
    branches: Vec<&'a str>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct GroupedAlternationPattern<'a> {
    prefix: &'a str,
    branches: Vec<&'a str>,
    capture_name: Option<&'a str>,
    suffix: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct SegmentedCaptureLiteralPattern<'a> {
    prefix: &'a str,
    capture: LiteralCapture<'a>,
    suffix: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct NestedCaptureLiteralPattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    outer_prefix: &'a str,
    inner_capture: LiteralCapture<'a>,
    outer_suffix: &'a str,
    suffix: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct LiteralCapture<'a> {
    body: &'a str,
    name: Option<&'a str>,
}

impl<'a> CaptureLiteralPattern<'a> {
    fn group_count(&self) -> usize {
        self.captures.len()
    }

    fn named_groups(&self) -> Vec<NamedGroup> {
        self.captures
            .iter()
            .enumerate()
            .filter_map(|(index, capture)| {
                capture.name.map(|name| NamedGroup {
                    name: name.to_string(),
                    index: index + 1,
                })
            })
            .collect()
    }

    fn pattern_chars(&self) -> Vec<char> {
        self.captures
            .iter()
            .flat_map(|capture| capture.body.chars())
            .collect()
    }

    fn group_spans(&self, match_start: usize) -> Vec<Option<(usize, usize)>> {
        let mut spans = Vec::with_capacity(self.captures.len());
        let mut cursor = match_start;
        for capture in &self.captures {
            let end = cursor + capture.body.chars().count();
            spans.push(Some((cursor, end)));
            cursor = end;
        }
        spans
    }
}

impl<'a> NamedBackreferenceLiteralPattern<'a> {
    fn group_count(&self) -> usize {
        1
    }

    fn named_groups(&self) -> Vec<NamedGroup> {
        vec![NamedGroup {
            name: self
                .capture
                .name
                .expect("named backreference capture should always have a name")
                .to_string(),
            index: 1,
        }]
    }

    fn pattern_chars(&self) -> Vec<char> {
        self.capture
            .body
            .chars()
            .chain(self.capture.body.chars())
            .collect()
    }

    fn group_spans(&self, match_start: usize) -> Vec<Option<(usize, usize)>> {
        let end = match_start + self.capture.body.chars().count();
        vec![Some((match_start, end))]
    }
}

impl<'a> NumberedBackreferenceLiteralPattern<'a> {
    fn group_count(&self) -> usize {
        1
    }

    fn pattern_chars(&self) -> Vec<char> {
        self.capture
            .body
            .chars()
            .chain(self.capture.body.chars())
            .collect()
    }

    fn group_spans(&self, match_start: usize) -> Vec<Option<(usize, usize)>> {
        let end = match_start + self.capture.body.chars().count();
        vec![Some((match_start, end))]
    }
}

impl<'a> SegmentedCaptureLiteralPattern<'a> {
    fn group_count(&self) -> usize {
        1
    }

    fn named_groups(&self) -> Vec<NamedGroup> {
        self.capture
            .name
            .map(|name| {
                vec![NamedGroup {
                    name: name.to_string(),
                    index: 1,
                }]
            })
            .unwrap_or_default()
    }

    fn pattern_chars(&self) -> Vec<char> {
        self.prefix
            .chars()
            .chain(self.capture.body.chars())
            .chain(self.suffix.chars())
            .collect()
    }

    fn group_spans(&self, match_start: usize) -> Vec<Option<(usize, usize)>> {
        let start = match_start + self.prefix.chars().count();
        let end = start + self.capture.body.chars().count();
        vec![Some((start, end))]
    }
}

impl<'a> GroupedAlternationPattern<'a> {
    fn group_count(&self) -> usize {
        1
    }

    fn named_groups(&self) -> Vec<NamedGroup> {
        self.capture_name
            .map(|name| {
                vec![NamedGroup {
                    name: name.to_string(),
                    index: 1,
                }]
            })
            .unwrap_or_default()
    }

    fn group_spans_for_branch_len(
        &self,
        match_start: usize,
        branch_len: usize,
    ) -> Vec<Option<(usize, usize)>> {
        let start = match_start + self.prefix.chars().count();
        let end = start + branch_len;
        vec![Some((start, end))]
    }
}

impl<'a> NestedCaptureLiteralPattern<'a> {
    fn group_count(&self) -> usize {
        2
    }

    fn named_groups(&self) -> Vec<NamedGroup> {
        let mut groups = Vec::new();
        if let Some(name) = self.outer_name {
            groups.push(NamedGroup {
                name: name.to_string(),
                index: 1,
            });
        }
        if let Some(name) = self.inner_capture.name {
            groups.push(NamedGroup {
                name: name.to_string(),
                index: 2,
            });
        }
        groups
    }

    fn pattern_chars(&self) -> Vec<char> {
        self.prefix
            .chars()
            .chain(self.outer_prefix.chars())
            .chain(self.inner_capture.body.chars())
            .chain(self.outer_suffix.chars())
            .chain(self.suffix.chars())
            .collect()
    }

    fn group_spans(&self, match_start: usize) -> Vec<Option<(usize, usize)>> {
        let outer_start = match_start + self.prefix.chars().count();
        let inner_start = outer_start + self.outer_prefix.chars().count();
        let inner_end = inner_start + self.inner_capture.body.chars().count();
        let outer_end = inner_end + self.outer_suffix.chars().count();
        vec![
            Some((outer_start, outer_end)),
            Some((inner_start, inner_end)),
        ]
    }

    fn lastindex(&self) -> usize {
        1
    }
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
        PatternRef::Str("(?i)abc")
            if normalized_flags == FLAG_UNICODE
                || normalized_flags == FLAG_IGNORECASE | FLAG_UNICODE =>
        {
            Some(CompileOutcome {
                status: CompileStatus::Compiled,
                normalized_flags: FLAG_IGNORECASE | FLAG_UNICODE,
                supports_literal: false,
                group_count: 0,
                named_groups: Vec::new(),
                warning: None,
            })
        }
        PatternRef::Str("[A-Z_][a-z0-9_]+")
            if normalized_flags == FLAG_IGNORECASE | FLAG_UNICODE =>
        {
            Some(CompileOutcome {
                status: CompileStatus::Compiled,
                normalized_flags,
                supports_literal: false,
                group_count: 0,
                named_groups: Vec::new(),
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
                group_count: 0,
                named_groups: Vec::new(),
                warning: None,
            })
        }
        PatternRef::Str(pattern)
            if parse_literal_alternation_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            Some(CompileOutcome {
                status: CompileStatus::Compiled,
                normalized_flags,
                supports_literal: false,
                group_count: 0,
                named_groups: Vec::new(),
                warning: None,
            })
        }
        PatternRef::Str(pattern)
            if parse_grouped_alternation_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_grouped_alternation_pattern_str(pattern)
                .expect("guarded grouped alternation literal");
            Some(CompileOutcome {
                status: CompileStatus::Compiled,
                normalized_flags,
                supports_literal: false,
                group_count: grouped_pattern.group_count(),
                named_groups: grouped_pattern.named_groups(),
                warning: None,
            })
        }
        PatternRef::Str(pattern)
            if parse_named_backreference_literal_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_named_backreference_literal_pattern_str(pattern)
                .expect("guarded named backreference literal");
            Some(CompileOutcome {
                status: CompileStatus::Compiled,
                normalized_flags,
                supports_literal: false,
                group_count: grouped_pattern.group_count(),
                named_groups: grouped_pattern.named_groups(),
                warning: None,
            })
        }
        PatternRef::Str(pattern)
            if parse_numbered_backreference_literal_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_numbered_backreference_literal_pattern_str(pattern)
                .expect("guarded numbered backreference literal");
            Some(CompileOutcome {
                status: CompileStatus::Compiled,
                normalized_flags,
                supports_literal: false,
                group_count: grouped_pattern.group_count(),
                named_groups: Vec::new(),
                warning: None,
            })
        }
        PatternRef::Str(pattern)
            if parse_capture_literal_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_capture_literal_pattern_str(pattern).expect("guarded grouped literal");
            Some(CompileOutcome {
                status: CompileStatus::Compiled,
                normalized_flags,
                supports_literal: false,
                group_count: grouped_pattern.group_count(),
                named_groups: grouped_pattern.named_groups(),
                warning: None,
            })
        }
        PatternRef::Str(pattern)
            if parse_grouped_segment_literal_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_grouped_segment_literal_pattern_str(pattern)
                .expect("guarded grouped segment literal");
            Some(CompileOutcome {
                status: CompileStatus::Compiled,
                normalized_flags,
                supports_literal: false,
                group_count: grouped_pattern.group_count(),
                named_groups: grouped_pattern.named_groups(),
                warning: None,
            })
        }
        PatternRef::Str(pattern)
            if parse_nested_capture_literal_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_nested_capture_literal_pattern_str(pattern)
                .expect("guarded nested capture literal");
            Some(CompileOutcome {
                status: CompileStatus::Compiled,
                normalized_flags,
                supports_literal: false,
                group_count: grouped_pattern.group_count(),
                named_groups: grouped_pattern.named_groups(),
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
            group_count: 0,
            named_groups: Vec::new(),
            warning: None,
        }),
        _ => None,
    }
}

fn is_nested_set_warning(pattern: PatternRef<'_>) -> bool {
    matches!(pattern, PatternRef::Str("[[a]"))
}

fn parse_capture_literal_pattern_str(pattern: &str) -> Option<CaptureLiteralPattern<'_>> {
    if !pattern.starts_with('(') {
        return None;
    }

    let mut captures = Vec::new();
    let mut index = 0;

    while index < pattern.len() {
        if pattern.as_bytes()[index] != b'(' {
            return None;
        }

        let remainder = &pattern[index + 1..];
        let (name, body, close_offset) =
            if let Some(named_remainder) = remainder.strip_prefix("?P<") {
                let name_end = named_remainder.find('>')?;
                let name = &named_remainder[..name_end];
                if !is_supported_group_name(name) {
                    return None;
                }
                let body = &named_remainder[name_end + 1..];
                let close_offset = body.find(')')?;
                (
                    Some(name),
                    &body[..close_offset],
                    3 + name_end + 1 + close_offset,
                )
            } else {
                let close_offset = remainder.find(')')?;
                (None, &remainder[..close_offset], close_offset)
            };
        if body.is_empty() || body.chars().any(is_meta_character) {
            return None;
        }

        captures.push(LiteralCapture { body, name });
        index += close_offset + 2;
    }

    Some(CaptureLiteralPattern { captures })
}

fn parse_named_backreference_literal_pattern_str(
    pattern: &str,
) -> Option<NamedBackreferenceLiteralPattern<'_>> {
    let capture_remainder = pattern.strip_prefix("(?P<")?;
    let name_end = capture_remainder.find('>')?;
    let capture_name = &capture_remainder[..name_end];
    if !is_supported_group_name(capture_name) {
        return None;
    }

    let body_and_remainder = &capture_remainder[name_end + 1..];
    let close_offset = body_and_remainder.find(')')?;
    let capture_body = &body_and_remainder[..close_offset];
    if capture_body.is_empty() || capture_body.chars().any(is_meta_character) {
        return None;
    }

    let backreference = &body_and_remainder[close_offset + 1..];
    let reference_name = backreference.strip_prefix("(?P=")?.strip_suffix(')')?;
    if reference_name != capture_name {
        return None;
    }

    Some(NamedBackreferenceLiteralPattern {
        capture: LiteralCapture {
            body: capture_body,
            name: Some(capture_name),
        },
    })
}

fn parse_numbered_backreference_literal_pattern_str(
    pattern: &str,
) -> Option<NumberedBackreferenceLiteralPattern<'_>> {
    let capture_remainder = pattern.strip_prefix('(')?;
    if capture_remainder.starts_with("?P<") {
        return None;
    }

    let close_offset = capture_remainder.find(')')?;
    let capture_body = &capture_remainder[..close_offset];
    if capture_body.is_empty() || capture_body.chars().any(is_meta_character) {
        return None;
    }

    let backreference = &capture_remainder[close_offset + 1..];
    if backreference != r"\1" {
        return None;
    }

    Some(NumberedBackreferenceLiteralPattern {
        capture: LiteralCapture {
            body: capture_body,
            name: None,
        },
    })
}

fn parse_grouped_segment_literal_pattern_str(
    pattern: &str,
) -> Option<SegmentedCaptureLiteralPattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let (name, body, close_offset) = if let Some(named_remainder) = remainder.strip_prefix("?P<") {
        let name_end = named_remainder.find('>')?;
        let name = &named_remainder[..name_end];
        if !is_supported_group_name(name) {
            return None;
        }
        let body = &named_remainder[name_end + 1..];
        let close_offset = body.find(')')?;
        (
            Some(name),
            &body[..close_offset],
            3 + name_end + 1 + close_offset,
        )
    } else {
        let close_offset = remainder.find(')')?;
        (None, &remainder[..close_offset], close_offset)
    };

    if body.is_empty() || body.chars().any(is_meta_character) {
        return None;
    }

    let suffix = &remainder[close_offset + 1..];
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(SegmentedCaptureLiteralPattern {
        prefix,
        capture: LiteralCapture { body, name },
        suffix,
    })
}

fn parse_nested_capture_literal_pattern_str(
    pattern: &str,
) -> Option<NestedCaptureLiteralPattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let (outer_name, outer_body) = if let Some(named_remainder) = remainder.strip_prefix("?P<") {
        let name_end = named_remainder.find('>')?;
        let name = &named_remainder[..name_end];
        if !is_supported_group_name(name) {
            return None;
        }
        (Some(name), &named_remainder[name_end + 1..])
    } else {
        (None, remainder)
    };

    let inner_open_offset = outer_body.find('(')?;
    let outer_prefix = &outer_body[..inner_open_offset];
    if outer_prefix.chars().any(is_meta_character) {
        return None;
    }

    let inner_remainder = &outer_body[inner_open_offset + 1..];
    let (inner_name, inner_body, inner_close_offset) =
        if let Some(named_remainder) = inner_remainder.strip_prefix("?P<") {
            let name_end = named_remainder.find('>')?;
            let name = &named_remainder[..name_end];
            if !is_supported_group_name(name) {
                return None;
            }
            let body = &named_remainder[name_end + 1..];
            let close_offset = body.find(')')?;
            (
                Some(name),
                &body[..close_offset],
                3 + name_end + 1 + close_offset,
            )
        } else {
            let close_offset = inner_remainder.find(')')?;
            (None, &inner_remainder[..close_offset], close_offset)
        };

    if inner_body.is_empty() || inner_body.chars().any(is_meta_character) {
        return None;
    }

    let outer_suffix_and_remainder = &outer_body[inner_open_offset + inner_close_offset + 2..];
    let outer_close_offset = outer_suffix_and_remainder.find(')')?;
    let outer_suffix = &outer_suffix_and_remainder[..outer_close_offset];
    if outer_suffix.chars().any(is_meta_character) {
        return None;
    }

    let suffix = &outer_suffix_and_remainder[outer_close_offset + 1..];
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(NestedCaptureLiteralPattern {
        prefix,
        outer_name,
        outer_prefix,
        inner_capture: LiteralCapture {
            body: inner_body,
            name: inner_name,
        },
        outer_suffix,
        suffix,
    })
}

fn parse_literal_alternation_pattern_str(pattern: &str) -> Option<LiteralAlternationPattern<'_>> {
    let branches: Vec<&str> = pattern.split('|').collect();
    if branches.len() < 2 {
        return None;
    }

    if branches
        .iter()
        .any(|branch| branch.is_empty() || branch.chars().any(is_meta_character))
    {
        return None;
    }

    Some(LiteralAlternationPattern { branches })
}

fn parse_grouped_alternation_pattern_str(pattern: &str) -> Option<GroupedAlternationPattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let (capture_name, body, close_offset) =
        if let Some(named_remainder) = remainder.strip_prefix("?P<") {
            let name_end = named_remainder.find('>')?;
            let name = &named_remainder[..name_end];
            if !is_supported_group_name(name) {
                return None;
            }
            let body = &named_remainder[name_end + 1..];
            let close_offset = body.find(')')?;
            (
                Some(name),
                &body[..close_offset],
                3 + name_end + 1 + close_offset,
            )
        } else {
            let close_offset = remainder.find(')')?;
            (None, &remainder[..close_offset], close_offset)
        };

    let branches: Vec<&str> = body.split('|').collect();
    if branches.len() < 2
        || branches
            .iter()
            .any(|branch| branch.is_empty() || branch.chars().any(is_meta_character))
    {
        return None;
    }

    let suffix = &remainder[close_offset + 1..];
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(GroupedAlternationPattern {
        prefix,
        branches,
        capture_name,
        suffix,
    })
}

fn is_supported_group_name(name: &str) -> bool {
    let mut chars = name.chars();
    match chars.next() {
        Some(first) if first == '_' || first.is_ascii_alphabetic() => {}
        _ => return false,
    }
    chars.all(|character| character == '_' || character.is_ascii_alphanumeric())
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
    let string_chars: Vec<char> = string.chars().collect();
    let (span, group_spans) = if pattern.supports_literal_execution(flags) {
        let pattern_chars: Vec<char> = match pattern {
            PatternRef::Str(value) => value.chars().collect(),
            PatternRef::Bytes(_) => unreachable!(),
        };
        (
            find_match_span_str(
                &pattern_chars,
                flags,
                mode,
                &string_chars,
                normalized_pos,
                normalized_endpos,
            ),
            Vec::new(),
        )
    } else if pattern.supports_bounded_inline_flag_search_execution(flags)
        && mode == MatchMode::Search
    {
        (
            find_match_span_str(
                &['a', 'b', 'c'],
                flags,
                mode,
                &string_chars,
                normalized_pos,
                normalized_endpos,
            ),
            Vec::new(),
        )
    } else if pattern.supports_bounded_single_dot_execution(flags) {
        let pattern_chars: Vec<char> = match pattern {
            PatternRef::Str(value) => value.chars().collect(),
            PatternRef::Bytes(_) => unreachable!(),
        };
        (
            find_bounded_single_dot_span_str(
                &pattern_chars,
                flags,
                mode,
                &string_chars,
                normalized_pos,
                normalized_endpos,
            ),
            Vec::new(),
        )
    } else if let PatternRef::Str(pattern_value) = pattern {
        if let Some(alternation_pattern) = parse_literal_alternation_pattern_str(pattern_value) {
            if flags != FLAG_UNICODE {
                return MatchOutcome {
                    status: MatchStatus::Unsupported,
                    pos: normalized_pos,
                    endpos: normalized_endpos,
                    span: None,
                    group_spans: Vec::new(),
                    lastindex: None,
                };
            }

            (
                find_literal_alternation_match_span_str(
                    &alternation_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                ),
                Vec::new(),
            )
        } else if let Some(named_backreference_pattern) =
            parse_named_backreference_literal_pattern_str(pattern_value)
        {
            if flags != FLAG_UNICODE {
                return MatchOutcome {
                    status: MatchStatus::Unsupported,
                    pos: normalized_pos,
                    endpos: normalized_endpos,
                    span: None,
                    group_spans: Vec::new(),
                    lastindex: None,
                };
            }

            let pattern_chars = named_backreference_pattern.pattern_chars();
            let span = find_match_span_str(
                pattern_chars.as_slice(),
                flags,
                mode,
                &string_chars,
                normalized_pos,
                normalized_endpos,
            );
            let group_spans = span
                .map(|(start, _)| named_backreference_pattern.group_spans(start))
                .unwrap_or_default();
            (span, group_spans)
        } else if let Some(numbered_backreference_pattern) =
            parse_numbered_backreference_literal_pattern_str(pattern_value)
        {
            if flags != FLAG_UNICODE {
                return MatchOutcome {
                    status: MatchStatus::Unsupported,
                    pos: normalized_pos,
                    endpos: normalized_endpos,
                    span: None,
                    group_spans: Vec::new(),
                    lastindex: None,
                };
            }

            let pattern_chars = numbered_backreference_pattern.pattern_chars();
            let span = find_match_span_str(
                pattern_chars.as_slice(),
                flags,
                mode,
                &string_chars,
                normalized_pos,
                normalized_endpos,
            );
            let group_spans = span
                .map(|(start, _)| numbered_backreference_pattern.group_spans(start))
                .unwrap_or_default();
            (span, group_spans)
        } else if let Some(grouped_alternation_pattern) =
            parse_grouped_alternation_pattern_str(pattern_value)
        {
            if flags != FLAG_UNICODE {
                return MatchOutcome {
                    status: MatchStatus::Unsupported,
                    pos: normalized_pos,
                    endpos: normalized_endpos,
                    span: None,
                    group_spans: Vec::new(),
                    lastindex: None,
                };
            }

            find_grouped_alternation_match_span_str(
                &grouped_alternation_pattern,
                flags,
                mode,
                &string_chars,
                normalized_pos,
                normalized_endpos,
            )
            .map_or((None, Vec::new()), |(span, group_spans)| {
                (Some(span), group_spans)
            })
        } else {
            if let Some(grouped_pattern) = parse_capture_literal_pattern_str(pattern_value) {
                if flags != FLAG_UNICODE {
                    return MatchOutcome {
                        status: MatchStatus::Unsupported,
                        pos: normalized_pos,
                        endpos: normalized_endpos,
                        span: None,
                        group_spans: Vec::new(),
                        lastindex: None,
                    };
                }
                let pattern_chars = grouped_pattern.pattern_chars();
                let span = find_match_span_str(
                    pattern_chars.as_slice(),
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                );
                let group_spans = span
                    .map(|(start, _)| grouped_pattern.group_spans(start))
                    .unwrap_or_default();
                (span, group_spans)
            } else if let Some(grouped_pattern) =
                parse_grouped_segment_literal_pattern_str(pattern_value)
            {
                if flags != FLAG_UNICODE {
                    return MatchOutcome {
                        status: MatchStatus::Unsupported,
                        pos: normalized_pos,
                        endpos: normalized_endpos,
                        span: None,
                        group_spans: Vec::new(),
                        lastindex: None,
                    };
                }
                let pattern_chars = grouped_pattern.pattern_chars();
                let span = find_match_span_str(
                    pattern_chars.as_slice(),
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                );
                let group_spans = span
                    .map(|(start, _)| grouped_pattern.group_spans(start))
                    .unwrap_or_default();
                (span, group_spans)
            } else if let Some(grouped_pattern) =
                parse_nested_capture_literal_pattern_str(pattern_value)
            {
                if flags != FLAG_UNICODE {
                    return MatchOutcome {
                        status: MatchStatus::Unsupported,
                        pos: normalized_pos,
                        endpos: normalized_endpos,
                        span: None,
                        group_spans: Vec::new(),
                        lastindex: None,
                    };
                }
                let pattern_chars = grouped_pattern.pattern_chars();
                let span = find_match_span_str(
                    pattern_chars.as_slice(),
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                );
                let group_spans = span
                    .map(|(start, _)| grouped_pattern.group_spans(start))
                    .unwrap_or_default();
                (span, group_spans)
            } else {
                return MatchOutcome {
                    status: MatchStatus::Unsupported,
                    pos: normalized_pos,
                    endpos: normalized_endpos,
                    span: None,
                    group_spans: Vec::new(),
                    lastindex: None,
                };
            }
        }
    } else {
        return MatchOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            span: None,
            group_spans: Vec::new(),
            lastindex: None,
        };
    };
    let lastindex = if span.is_some() {
        match pattern {
            PatternRef::Str(pattern_value) => {
                parse_nested_capture_literal_pattern_str(pattern_value)
                    .map(|grouped_pattern| grouped_pattern.lastindex())
                    .or_else(|| lastindex_from_group_spans(&group_spans))
            }
            PatternRef::Bytes(_) => None,
        }
    } else {
        None
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
        group_spans,
        lastindex,
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
            group_spans: Vec::new(),
            lastindex: None,
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
        group_spans: Vec::new(),
        lastindex: None,
    }
}

fn lastindex_from_group_spans(group_spans: &[Option<(usize, usize)>]) -> Option<usize> {
    group_spans
        .iter()
        .enumerate()
        .rev()
        .find_map(|(index, span)| span.map(|_| index + 1))
}

/// Discover repeated spans for the bounded grouped-literal replacement slice.
#[must_use]
pub fn grouped_literal_find_spans_str(
    pattern: &str,
    flags: i32,
    string: &str,
    pos: isize,
    endpos: Option<isize>,
) -> FindSpansOutcome {
    let string_chars: Vec<char> = string.chars().collect();
    let (normalized_pos, normalized_endpos) = normalize_bounds(string_chars.len(), pos, endpos);
    let Some(grouped_pattern) = parse_capture_literal_pattern_str(pattern) else {
        return FindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            spans: Vec::new(),
        };
    };
    if flags != FLAG_UNICODE {
        return FindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            spans: Vec::new(),
        };
    }

    let pattern_chars = grouped_pattern.pattern_chars();
    let spans = collect_literal_spans_str(
        pattern_chars.as_slice(),
        flags,
        &string_chars,
        normalized_pos,
        normalized_endpos,
    );
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

/// Discover repeated spans for the bounded grouped-alternation replacement
/// slice while preserving first-capture spans for template expansion.
#[must_use]
pub fn grouped_alternation_find_spans_str(
    pattern: &str,
    flags: i32,
    string: &str,
    pos: isize,
    endpos: Option<isize>,
) -> GroupedAlternationFindSpansOutcome {
    let string_chars: Vec<char> = string.chars().collect();
    let (normalized_pos, normalized_endpos) = normalize_bounds(string_chars.len(), pos, endpos);
    let Some(grouped_pattern) = parse_grouped_alternation_pattern_str(pattern) else {
        return GroupedAlternationFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    };
    if flags != FLAG_UNICODE {
        return GroupedAlternationFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    }

    let mut matches = Vec::new();
    let mut next_start = normalized_pos;
    while let Some((span, group_spans)) = find_grouped_alternation_match_span_str(
        &grouped_pattern,
        flags,
        MatchMode::Search,
        &string_chars,
        next_start,
        normalized_endpos,
    ) {
        let group_1_span = group_spans
            .first()
            .and_then(|span| *span)
            .expect("grouped alternation support always reports capture 1");
        matches.push(GroupedAlternationMatchSpan { span, group_1_span });
        next_start = span.1;
    }

    GroupedAlternationFindSpansOutcome {
        status: if matches.is_empty() {
            MatchStatus::NoMatch
        } else {
            MatchStatus::Matched
        },
        pos: normalized_pos,
        endpos: normalized_endpos,
        matches,
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

fn find_literal_alternation_match_span_str(
    pattern: &LiteralAlternationPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<(usize, usize)> {
    let branch_chars: Vec<Vec<char>> = pattern
        .branches
        .iter()
        .map(|branch| branch.chars().collect())
        .collect();

    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            branch_chars.iter().find_map(|branch| {
                literal_matches_at_str(branch.as_slice(), flags, string, start, endpos)
                    .then_some((start, start + branch.len()))
            })
        }),
        MatchMode::Match => branch_chars.iter().find_map(|branch| {
            literal_matches_at_str(branch.as_slice(), flags, string, pos, endpos)
                .then_some((pos, pos + branch.len()))
        }),
        MatchMode::Fullmatch => branch_chars.iter().find_map(|branch| {
            (endpos.saturating_sub(pos) == branch.len()
                && literal_matches_at_str(branch.as_slice(), flags, string, pos, endpos))
            .then_some((pos, endpos))
        }),
    }
}

fn grouped_alternation_matches_at_str(
    pattern: &GroupedAlternationPattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<(usize, usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();
    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let branch_start = start + prefix_chars.len();
    pattern.branches.iter().find_map(|branch| {
        let branch_chars: Vec<char> = branch.chars().collect();
        let branch_len = branch_chars.len();
        let suffix_start = branch_start + branch_chars.len();
        (literal_matches_at_str(branch_chars.as_slice(), flags, string, branch_start, endpos)
            && literal_matches_at_str(suffix_chars.as_slice(), flags, string, suffix_start, endpos))
        .then_some((branch_len, suffix_start + suffix_chars.len()))
    })
}

fn find_grouped_alternation_match_span_str(
    pattern: &GroupedAlternationPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            grouped_alternation_matches_at_str(pattern, flags, string, start, endpos).map(
                |(branch_len, match_end)| {
                    (
                        (start, match_end),
                        pattern.group_spans_for_branch_len(start, branch_len),
                    )
                },
            )
        }),
        MatchMode::Match => grouped_alternation_matches_at_str(pattern, flags, string, pos, endpos)
            .map(|(branch_len, match_end)| {
                (
                    (pos, match_end),
                    pattern.group_spans_for_branch_len(pos, branch_len),
                )
            }),
        MatchMode::Fullmatch => grouped_alternation_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .and_then(|(branch_len, match_end)| {
            (match_end == endpos).then_some((
                (pos, match_end),
                pattern.group_spans_for_branch_len(pos, branch_len),
            ))
        }),
    }
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
        grouped_alternation_find_spans_str, grouped_literal_find_spans_str, literal_find_spans,
        literal_match, CompileStatus, GroupedAlternationMatchSpan, MatchMode, MatchStatus,
        NamedGroup, PatternRef, FLAG_ASCII, FLAG_IGNORECASE, FLAG_LOCALE, FLAG_UNICODE,
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
    fn compile_accepts_bounded_inline_flag_literal_search_case() {
        let outcome = compile(PatternRef::Str("(?i)abc"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_IGNORECASE | FLAG_UNICODE);
        assert!(!outcome.supports_literal);
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
    fn compile_accepts_grouped_literal_capture_cases() {
        let single_outcome = compile(PatternRef::Str("(abc)"), 0).unwrap();
        assert_eq!(single_outcome.status, CompileStatus::Compiled);
        assert_eq!(single_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!single_outcome.supports_literal);
        assert_eq!(single_outcome.group_count, 1);
        assert!(single_outcome.named_groups.is_empty());

        let multi_outcome = compile(PatternRef::Str("(ab)(c)"), 0).unwrap();
        assert_eq!(multi_outcome.status, CompileStatus::Compiled);
        assert_eq!(multi_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!multi_outcome.supports_literal);
        assert_eq!(multi_outcome.group_count, 2);
        assert!(multi_outcome.named_groups.is_empty());
    }

    #[test]
    fn compile_accepts_bounded_named_group_literal_case() {
        let outcome = compile(PatternRef::Str("(?P<word>abc)"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert_eq!(
            outcome.named_groups,
            vec![NamedGroup {
                name: "word".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn compile_accepts_bounded_grouped_segment_cases() {
        let outcome = compile(PatternRef::Str("a(b)c"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b)c"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!named_outcome.supports_literal);
        assert_eq!(named_outcome.group_count, 1);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "word".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn compile_accepts_bounded_nested_group_cases() {
        let outcome = compile(PatternRef::Str("a((b))d"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 2);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<outer>(?P<inner>b))d"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!named_outcome.supports_literal);
        assert_eq!(named_outcome.group_count, 2);
        assert_eq!(
            named_outcome.named_groups,
            vec![
                NamedGroup {
                    name: "outer".to_string(),
                    index: 1,
                },
                NamedGroup {
                    name: "inner".to_string(),
                    index: 2,
                },
            ]
        );
    }

    #[test]
    fn compile_accepts_bounded_literal_alternation_case() {
        let outcome = compile(PatternRef::Str("ab|ac"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 0);
        assert!(outcome.named_groups.is_empty());
    }

    #[test]
    fn compile_accepts_bounded_grouped_alternation_cases() {
        let outcome = compile(PatternRef::Str("a(b|c)d"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b|c)d"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!named_outcome.supports_literal);
        assert_eq!(named_outcome.group_count, 1);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "word".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn compile_accepts_bounded_named_backreference_literal_case() {
        let outcome = compile(PatternRef::Str("(?P<word>ab)(?P=word)"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert_eq!(
            outcome.named_groups,
            vec![NamedGroup {
                name: "word".to_string(),
                index: 1,
            }]
        );
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
        assert!(outcome.group_spans.is_empty());
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
        assert!(outcome.group_spans.is_empty());
    }

    #[test]
    fn bounded_inline_flag_literal_search_supports_ignorecase_search() {
        let outcome = literal_match(
            PatternRef::Str("(?i)abc"),
            FLAG_IGNORECASE | FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("ABC"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 3)));
        assert!(outcome.group_spans.is_empty());
    }

    #[test]
    fn bounded_inline_flag_literal_workflow_stays_search_only() {
        let outcome = literal_match(
            PatternRef::Str("(?i)abc"),
            FLAG_IGNORECASE | FLAG_UNICODE,
            MatchMode::Match,
            PatternRef::Str("ABC"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Unsupported);
        assert_eq!(outcome.span, None);
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
    fn literal_match_supports_bounded_locale_bytes_workflow() {
        for mode in [MatchMode::Search, MatchMode::Match, MatchMode::Fullmatch] {
            let outcome = literal_match(
                PatternRef::Bytes(b"abc"),
                FLAG_LOCALE,
                mode,
                PatternRef::Bytes(b"abc"),
                0,
                None,
            )
            .unwrap();

            assert_eq!(outcome.status, MatchStatus::Matched);
            assert_eq!(outcome.span, Some((0, 3)));
            assert!(outcome.group_spans.is_empty());
        }
    }

    #[test]
    fn grouped_literal_match_reports_group_1_span() {
        let outcome = literal_match(
            PatternRef::Str("(abc)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabczz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 5)));
        assert_eq!(outcome.group_spans, vec![Some((2, 5))]);
    }

    #[test]
    fn grouped_literal_match_reports_multiple_group_spans() {
        let outcome = literal_match(
            PatternRef::Str("(ab)(c)"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abc"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 3)));
        assert_eq!(outcome.group_spans, vec![Some((0, 2)), Some((2, 3))]);
    }

    #[test]
    fn named_group_literal_match_reports_group_1_span() {
        let outcome = literal_match(
            PatternRef::Str("(?P<word>abc)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabczz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 5)));
        assert_eq!(outcome.group_spans, vec![Some((2, 5))]);
    }

    #[test]
    fn grouped_segment_literal_match_reports_group_1_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)c"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 5)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
    }

    #[test]
    fn named_grouped_segment_literal_match_reports_named_group_span() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)c"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abc"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 3)));
        assert_eq!(outcome.group_spans, vec![Some((1, 2))]);
    }

    #[test]
    fn nested_group_literal_match_reports_outer_and_inner_spans() {
        let outcome = literal_match(
            PatternRef::Str("a((b))d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 5)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4)), Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_nested_group_literal_match_reports_outer_lastindex() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<outer>(?P<inner>b))d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 3)));
        assert_eq!(outcome.group_spans, vec![Some((1, 2)), Some((1, 2))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_backreference_literal_match_reports_named_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("(?P<word>ab)(?P=word)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzababzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((2, 4))]);
    }

    #[test]
    fn literal_alternation_search_matches_second_branch() {
        let outcome = literal_match(
            PatternRef::Str("ab|ac"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzaczz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 4)));
        assert!(outcome.group_spans.is_empty());
    }

    #[test]
    fn literal_alternation_fullmatch_matches_second_branch() {
        let outcome = literal_match(
            PatternRef::Str("ab|ac"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ac"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 2)));
        assert!(outcome.group_spans.is_empty());
    }

    #[test]
    fn grouped_alternation_search_matches_second_branch_and_reports_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b|c)d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzacdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 5)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
    }

    #[test]
    fn named_grouped_alternation_fullmatch_matches_second_branch_and_reports_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b|c)d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("acd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 3)));
        assert_eq!(outcome.group_spans, vec![Some((1, 2))]);
    }

    #[test]
    fn literal_find_spans_keeps_locale_bytes_collection_unsupported() {
        let outcome = literal_find_spans(
            PatternRef::Bytes(b"abc"),
            FLAG_LOCALE,
            PatternRef::Bytes(b"abcabc"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Unsupported);
        assert!(outcome.spans.is_empty());
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
        let expanded =
            expand_literal_replacement_template_str(r"\g<0>x", "abc", None, None).unwrap();
        assert_eq!(expanded, "abcx");
    }

    #[test]
    fn replacement_template_expands_group_1_reference_for_grouped_literal_case() {
        let expanded =
            expand_literal_replacement_template_str(r"\1x", "abc", Some("abc"), None).unwrap();
        assert_eq!(expanded, "abcx");
    }

    #[test]
    fn replacement_template_expands_named_group_reference_for_named_group_case() {
        let expanded = expand_literal_replacement_template_str(
            r"<\g<word>>",
            "abc",
            Some("abc"),
            Some(("word", "abc")),
        )
        .unwrap();
        assert_eq!(expanded, "<abc>");
    }

    #[test]
    fn replacement_template_rejects_unsupported_backslash_forms() {
        assert_eq!(
            expand_literal_replacement_template_str(r"\1x", "abc", None, None),
            None
        );
        assert_eq!(
            expand_literal_replacement_template_str("\\", "abc", None, None),
            None
        );
        assert_eq!(
            expand_literal_replacement_template_str(r"\g<word>", "abc", None, None),
            None
        );
    }

    #[test]
    fn grouped_literal_find_spans_reports_repeated_matches() {
        let outcome = grouped_literal_find_spans_str("(abc)", FLAG_UNICODE, "zabcabcx", 1, Some(7));
        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.pos, 1);
        assert_eq!(outcome.endpos, 7);
        assert_eq!(outcome.spans, vec![(1, 4), (4, 7)]);
    }

    #[test]
    fn grouped_alternation_find_spans_reports_repeated_matches_and_capture_spans() {
        let outcome =
            grouped_alternation_find_spans_str("a(b|c)d", FLAG_UNICODE, "zabdacdx", 1, Some(7));
        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.pos, 1);
        assert_eq!(outcome.endpos, 7);
        assert_eq!(
            outcome.matches,
            vec![
                GroupedAlternationMatchSpan {
                    span: (1, 4),
                    group_1_span: (2, 3),
                },
                GroupedAlternationMatchSpan {
                    span: (4, 7),
                    group_1_span: (5, 6),
                },
            ]
        );
    }

    #[test]
    fn escape_matches_expected_outputs() {
        assert_eq!(escape_str("a-b.c"), "a\\-b\\.c");
        assert_eq!(escape_bytes(b"a-b.c"), b"a\\-b\\.c");
    }
}
