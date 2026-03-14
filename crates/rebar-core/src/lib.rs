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

/// One repeated match span plus positional capture spans.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CapturedMatchSpan {
    /// Whole-match span.
    pub span: (usize, usize),
    /// Positional capture spans aligned to groups `1..=n`.
    pub group_spans: Vec<Option<(usize, usize)>>,
}

/// Successful result metadata for repeated grouped matches that expose capture
/// spans on each match.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CapturedFindSpansOutcome {
    /// Match status.
    pub status: MatchStatus,
    /// Normalized `pos` bound used for matching.
    pub pos: usize,
    /// Normalized `endpos` bound used for matching.
    pub endpos: usize,
    /// Matched spans plus positional capture spans.
    pub matches: Vec<CapturedMatchSpan>,
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
    numbered_captures: &[Option<&str>],
    named_captures: &[(&str, &str)],
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
                } else {
                    let (_, value) = named_captures
                        .iter()
                        .find(|(name, _)| *name == group_name)
                        .copied()?;
                    expanded.push_str(value);
                }
            }
            Some(group) if group.is_ascii_digit() && group != '0' => {
                let group_index = group.to_digit(10)? as usize;
                expanded.push_str(numbered_captures.get(group_index - 1).copied().flatten()?);
            }
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
struct QuantifiedNestedCaptureLiteralPattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    inner_capture: LiteralCapture<'a>,
    suffix: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct QuantifiedNestedGroupAlternationPattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    inner_name: Option<&'a str>,
    branches: Vec<&'a str>,
    suffix: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct QuantifiedNestedGroupAlternationBranchLocalBackreferencePattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    inner_name: Option<&'a str>,
    branches: Vec<&'a str>,
    suffix: &'a str,
    max_repeat: Option<usize>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct NestedAlternationLiteralPattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    outer_prefix: &'a str,
    inner_capture_name: Option<&'a str>,
    inner_branches: Vec<&'a str>,
    outer_suffix: &'a str,
    suffix: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct NestedAlternationBranchLocalBackreferencePattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    inner_name: Option<&'a str>,
    branches: Vec<&'a str>,
    suffix: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct BranchLocalBackreferencePattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    inner_name: Option<&'a str>,
    inner_body: &'a str,
    _alternate_branch: &'a str,
    suffix: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct QuantifiedBranchLocalBackreferencePattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    inner_name: Option<&'a str>,
    inner_body: &'a str,
    _alternate_branch: &'a str,
    suffix: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct ConditionalBranchLocalBackreferencePattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    inner_name: Option<&'a str>,
    inner_body: &'a str,
    _alternate_branch: &'a str,
    yes_branch: &'a str,
    _no_branch: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct OptionalGroupPattern<'a> {
    prefix: &'a str,
    capture: LiteralCapture<'a>,
    suffix: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct OptionalGroupAlternationPattern<'a> {
    prefix: &'a str,
    branches: Vec<&'a str>,
    capture_name: Option<&'a str>,
    suffix: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct OptionalGroupAlternationBranchLocalBackreferencePattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    inner_name: Option<&'a str>,
    branches: Vec<&'a str>,
    suffix: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct QuantifiedAlternationBranchLocalBackreferencePattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    inner_name: Option<&'a str>,
    branches: Vec<&'a str>,
    suffix: &'a str,
    max_repeat: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct QuantifiedAlternationPattern<'a> {
    prefix: &'a str,
    branches: Vec<&'a str>,
    capture_name: Option<&'a str>,
    suffix: &'a str,
    min_repeat: usize,
    max_repeat: Option<usize>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct QuantifiedAlternationNestedBranchPattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    inner_branches: Vec<&'a str>,
    literal_branch: &'a str,
    suffix: &'a str,
    max_repeat: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct QuantifiedAlternationConditionalPattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    branches: Vec<&'a str>,
    yes_branch: &'a str,
    no_branch: &'a str,
    min_repeat: usize,
    max_repeat: Option<usize>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct ConditionalGroupExistsPattern<'a> {
    prefix: &'a str,
    capture: LiteralCapture<'a>,
    middle: &'a str,
    yes_branch: &'a str,
    yes_branch_alternation: Option<Vec<&'a str>>,
    no_branch_alternation: Option<Vec<&'a str>>,
    nested_yes_branch: Option<&'a str>,
    nested_no_branch: Option<NestedConditionalGroupExistsEmptyYesElseBranch<'a>>,
    no_branch: Option<&'a str>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct QuantifiedConditionalGroupExistsPattern<'a> {
    conditional: ConditionalGroupExistsPattern<'a>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct QuantifiedConditionalGroupExistsWholePattern<'a> {
    conditional: ConditionalGroupExistsPattern<'a>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct NestedConditionalGroupExistsEmptyYesElseBranch<'a> {
    yes_branch: &'a str,
    no_branch: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct NestedConditionalGroupExistsFullyEmptyBranch;

#[derive(Debug, Clone, PartialEq, Eq)]
struct ExactRepeatGroupPattern<'a> {
    prefix: &'a str,
    capture: LiteralCapture<'a>,
    suffix: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct ExactRepeatGroupAlternationPattern<'a> {
    prefix: &'a str,
    branches: Vec<&'a str>,
    capture_name: Option<&'a str>,
    suffix: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct RangedRepeatGroupPattern<'a> {
    prefix: &'a str,
    capture: LiteralCapture<'a>,
    suffix: &'a str,
    max_repeat: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct WiderRangedRepeatGroupedAlternationBacktrackingHeavyPattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    branches: Vec<&'a str>,
    repeated_suffix: &'a str,
    suffix: &'a str,
    max_repeat: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct OpenEndedQuantifiedGroupAlternationBacktrackingHeavyPattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    branches: Vec<&'a str>,
    repeated_suffix: &'a str,
    suffix: &'a str,
    min_repeat: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct NestedOpenEndedQuantifiedGroupAlternationPattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    branches: Vec<&'a str>,
    suffix: &'a str,
    min_repeat: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationPattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    branches: Vec<&'a str>,
    suffix: &'a str,
    min_repeat: usize,
    max_repeat: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationBacktrackingHeavyPattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    branches: Vec<&'a str>,
    repeated_suffix: &'a str,
    suffix: &'a str,
    max_repeat: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationConditionalPattern<'a> {
    prefix: &'a str,
    outer_name: Option<&'a str>,
    branches: Vec<&'a str>,
    middle: &'a str,
    yes_branch: &'a str,
    no_branch: &'a str,
    min_repeat: usize,
    max_repeat: usize,
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

impl<'a> QuantifiedNestedCaptureLiteralPattern<'a> {
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

    fn group_spans(&self, match_start: usize, repeat_count: usize) -> Vec<Option<(usize, usize)>> {
        let outer_start = match_start + self.prefix.chars().count();
        let inner_len = self.inner_capture.body.chars().count();
        let outer_end = outer_start + inner_len * repeat_count;
        let inner_start = outer_end - inner_len;
        vec![
            Some((outer_start, outer_end)),
            Some((inner_start, outer_end)),
        ]
    }
}

impl<'a> QuantifiedNestedGroupAlternationPattern<'a> {
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
        if let Some(name) = self.inner_name {
            groups.push(NamedGroup {
                name: name.to_string(),
                index: 2,
            });
        }
        groups
    }

    fn group_spans(
        &self,
        outer_span: (usize, usize),
        inner_span: (usize, usize),
    ) -> Vec<Option<(usize, usize)>> {
        vec![Some(outer_span), Some(inner_span)]
    }

    fn matched_lastindex(&self, group_spans: &[Option<(usize, usize)>]) -> Option<usize> {
        group_spans.first().copied().flatten().map(|_| 1)
    }
}

impl<'a> QuantifiedNestedGroupAlternationBranchLocalBackreferencePattern<'a> {
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
        if let Some(name) = self.inner_name {
            groups.push(NamedGroup {
                name: name.to_string(),
                index: 2,
            });
        }
        groups
    }

    fn group_spans(
        &self,
        outer_span: (usize, usize),
        inner_span: (usize, usize),
    ) -> Vec<Option<(usize, usize)>> {
        vec![Some(outer_span), Some(inner_span)]
    }

    fn matched_lastindex(&self, group_spans: &[Option<(usize, usize)>]) -> Option<usize> {
        group_spans.first().copied().flatten().map(|_| 1)
    }
}

impl<'a> NestedAlternationLiteralPattern<'a> {
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
        if let Some(name) = self.inner_capture_name {
            groups.push(NamedGroup {
                name: name.to_string(),
                index: 2,
            });
        }
        groups
    }

    fn group_spans_for_branch_len(
        &self,
        match_start: usize,
        branch_len: usize,
    ) -> Vec<Option<(usize, usize)>> {
        let outer_start = match_start + self.prefix.chars().count();
        let inner_start = outer_start + self.outer_prefix.chars().count();
        let inner_end = inner_start + branch_len;
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

impl<'a> NestedAlternationBranchLocalBackreferencePattern<'a> {
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
        if let Some(name) = self.inner_name {
            groups.push(NamedGroup {
                name: name.to_string(),
                index: 2,
            });
        }
        groups
    }

    fn group_spans(&self, match_start: usize, matched_branch: &str) -> Vec<Option<(usize, usize)>> {
        let outer_start = match_start + self.prefix.chars().count();
        let outer_end = outer_start + matched_branch.chars().count();
        vec![
            Some((outer_start, outer_end)),
            Some((outer_start, outer_end)),
        ]
    }

    fn lastindex(&self) -> usize {
        1
    }
}

impl<'a> BranchLocalBackreferencePattern<'a> {
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
        if let Some(name) = self.inner_name {
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
            .chain(self.inner_body.chars())
            .chain(self.inner_body.chars())
            .chain(self.suffix.chars())
            .collect()
    }

    fn group_spans(&self, match_start: usize) -> Vec<Option<(usize, usize)>> {
        let start = match_start + self.prefix.chars().count();
        let end = start + self.inner_body.chars().count();
        vec![Some((start, end)), Some((start, end))]
    }

    fn lastindex(&self) -> usize {
        1
    }
}

impl<'a> QuantifiedBranchLocalBackreferencePattern<'a> {
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
        if let Some(name) = self.inner_name {
            groups.push(NamedGroup {
                name: name.to_string(),
                index: 2,
            });
        }
        groups
    }

    fn group_spans(&self, match_start: usize, repeat_count: usize) -> Vec<Option<(usize, usize)>> {
        let outer_start = match_start + self.prefix.chars().count();
        let inner_len = self.inner_body.chars().count();
        let outer_end = outer_start + inner_len * repeat_count;
        let inner_start = outer_end - inner_len;

        vec![
            Some((outer_start, outer_end)),
            Some((inner_start, outer_end)),
        ]
    }

    fn lastindex(&self) -> usize {
        1
    }
}

impl<'a> ConditionalBranchLocalBackreferencePattern<'a> {
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
        if let Some(name) = self.inner_name {
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
            .chain(self.inner_body.chars())
            .chain(self.inner_body.chars())
            .chain(self.yes_branch.chars())
            .collect()
    }

    fn group_spans(&self, match_start: usize) -> Vec<Option<(usize, usize)>> {
        let start = match_start + self.prefix.chars().count();
        let end = start + self.inner_body.chars().count();
        vec![Some((start, end)), Some((start, end))]
    }

    fn lastindex(&self) -> usize {
        1
    }
}

impl<'a> OptionalGroupPattern<'a> {
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

    fn group_spans(
        &self,
        match_start: usize,
        capture_present: bool,
    ) -> Vec<Option<(usize, usize)>> {
        if !capture_present {
            return vec![None];
        }

        let start = match_start + self.prefix.chars().count();
        let end = start + self.capture.body.chars().count();
        vec![Some((start, end))]
    }
}

impl<'a> OptionalGroupAlternationPattern<'a> {
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

    fn group_spans(
        &self,
        match_start: usize,
        matched_branch: Option<&str>,
    ) -> Vec<Option<(usize, usize)>> {
        let Some(branch) = matched_branch else {
            return vec![None];
        };

        let start = match_start + self.prefix.chars().count();
        let end = start + branch.chars().count();
        vec![Some((start, end))]
    }
}

impl<'a> OptionalGroupAlternationBranchLocalBackreferencePattern<'a> {
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
        if let Some(name) = self.inner_name {
            groups.push(NamedGroup {
                name: name.to_string(),
                index: 2,
            });
        }
        groups
    }

    fn group_spans(
        &self,
        match_start: usize,
        matched_branch: Option<&str>,
    ) -> Vec<Option<(usize, usize)>> {
        let Some(branch) = matched_branch else {
            return vec![None, None];
        };

        let outer_start = match_start + self.prefix.chars().count();
        let inner_end = outer_start + branch.chars().count();
        let outer_end = inner_end + branch.chars().count();
        vec![
            Some((outer_start, outer_end)),
            Some((outer_start, inner_end)),
        ]
    }

    fn matched_lastindex(&self, group_spans: &[Option<(usize, usize)>]) -> Option<usize> {
        group_spans.first().copied().flatten().map(|_| 1)
    }
}

impl<'a> QuantifiedAlternationBranchLocalBackreferencePattern<'a> {
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
        if let Some(name) = self.inner_name {
            groups.push(NamedGroup {
                name: name.to_string(),
                index: 2,
            });
        }
        groups
    }

    fn group_spans(
        &self,
        match_start: usize,
        repeat_count: usize,
        last_branch: &str,
    ) -> Vec<Option<(usize, usize)>> {
        let prefix_len = self.prefix.chars().count();
        let branch_len = last_branch.chars().count();
        let repeated_branch_len = branch_len * 2;
        let outer_start =
            match_start + prefix_len + repeated_branch_len * repeat_count.saturating_sub(1);
        let inner_end = outer_start + branch_len;
        let outer_end = inner_end + branch_len;
        vec![
            Some((outer_start, outer_end)),
            Some((outer_start, inner_end)),
        ]
    }

    fn lastindex(&self) -> usize {
        1
    }
}

impl<'a> QuantifiedAlternationPattern<'a> {
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

    fn group_spans(&self, last_branch_span: (usize, usize)) -> Vec<Option<(usize, usize)>> {
        vec![Some(last_branch_span)]
    }
}

impl<'a> QuantifiedAlternationNestedBranchPattern<'a> {
    fn group_count(&self) -> usize {
        2
    }

    fn named_groups(&self) -> Vec<NamedGroup> {
        self.outer_name
            .map(|name| {
                vec![NamedGroup {
                    name: name.to_string(),
                    index: 1,
                }]
            })
            .unwrap_or_default()
    }

    fn group_spans(
        &self,
        outer_span: Option<(usize, usize)>,
        inner_span: Option<(usize, usize)>,
    ) -> Vec<Option<(usize, usize)>> {
        vec![outer_span, inner_span]
    }

    fn matched_lastindex(&self, group_spans: &[Option<(usize, usize)>]) -> Option<usize> {
        group_spans.first().copied().flatten().map(|_| 1)
    }
}

impl<'a> QuantifiedAlternationConditionalPattern<'a> {
    fn group_count(&self) -> usize {
        2
    }

    fn named_groups(&self) -> Vec<NamedGroup> {
        self.outer_name
            .map(|name| {
                vec![NamedGroup {
                    name: name.to_string(),
                    index: 1,
                }]
            })
            .unwrap_or_default()
    }

    fn group_spans(
        &self,
        outer_span: Option<(usize, usize)>,
        inner_span: Option<(usize, usize)>,
    ) -> Vec<Option<(usize, usize)>> {
        vec![outer_span, inner_span]
    }

    fn matched_lastindex(&self, group_spans: &[Option<(usize, usize)>]) -> Option<usize> {
        group_spans.first().copied().flatten().map(|_| 1)
    }
}

impl<'a> ConditionalGroupExistsPattern<'a> {
    fn group_count(&self) -> usize {
        1 + usize::from(self.yes_branch_alternation.is_some())
            + usize::from(self.no_branch_alternation.is_some())
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

    fn group_spans(
        &self,
        match_start: usize,
        capture_present: bool,
        matched_alternation_branch: Option<&str>,
    ) -> Vec<Option<(usize, usize)>> {
        let has_yes_alternation = self.yes_branch_alternation.is_some();
        let has_no_alternation = self.no_branch_alternation.is_some();
        if !capture_present {
            let mut spans = vec![None];
            if has_yes_alternation {
                spans.push(None);
            }
            if has_no_alternation {
                let no_branch_span = matched_alternation_branch.map(|branch| {
                    let start =
                        match_start + self.prefix.chars().count() + self.middle.chars().count();
                    let end = start + branch.chars().count();
                    (start, end)
                });
                spans.push(no_branch_span);
            }
            return spans;
        }

        let capture_start = match_start + self.prefix.chars().count();
        let capture_end = capture_start + self.capture.body.chars().count();
        let mut spans = vec![Some((capture_start, capture_end))];

        if has_yes_alternation {
            let yes_group_span = matched_alternation_branch.map(|branch| {
                let start = capture_end + self.middle.chars().count();
                let end = start + branch.chars().count();
                (start, end)
            });
            spans.push(yes_group_span);
        }
        if has_no_alternation {
            spans.push(None);
        }

        spans
    }
}

impl<'a> ExactRepeatGroupPattern<'a> {
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
            .chain(self.capture.body.chars())
            .chain(self.suffix.chars())
            .collect()
    }

    fn group_spans(&self, match_start: usize) -> Vec<Option<(usize, usize)>> {
        let prefix_len = self.prefix.chars().count();
        let capture_len = self.capture.body.chars().count();
        let start = match_start + prefix_len + capture_len;
        let end = start + capture_len;
        vec![Some((start, end))]
    }
}

impl<'a> ExactRepeatGroupAlternationPattern<'a> {
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

    fn group_spans(&self, last_branch_span: (usize, usize)) -> Vec<Option<(usize, usize)>> {
        vec![Some(last_branch_span)]
    }
}

impl<'a> QuantifiedConditionalGroupExistsPattern<'a> {
    fn group_count(&self) -> usize {
        self.conditional.group_count()
    }

    fn named_groups(&self) -> Vec<NamedGroup> {
        self.conditional.named_groups()
    }

    fn group_spans(
        &self,
        match_start: usize,
        capture_present: bool,
        repeated_alternation_branches: Option<(&str, &str)>,
    ) -> Vec<Option<(usize, usize)>> {
        if repeated_alternation_branches.is_none() {
            return self
                .conditional
                .group_spans(match_start, capture_present, None);
        }

        let conditional = &self.conditional;
        let capture_start = match_start + conditional.prefix.chars().count();
        let capture_end = capture_start + conditional.capture.body.chars().count();
        let middle_start = if capture_present {
            capture_end
        } else {
            capture_start
        };
        let branch_start = middle_start + conditional.middle.chars().count();
        let (first_branch, last_branch) =
            repeated_alternation_branches.expect("guarded quantified alternation branches");
        let last_branch_start = branch_start + first_branch.chars().count();

        let mut spans = vec![if capture_present {
            Some((capture_start, capture_end))
        } else {
            None
        }];

        if conditional.yes_branch_alternation.is_some() {
            spans.push(if capture_present {
                Some((
                    last_branch_start,
                    last_branch_start + last_branch.chars().count(),
                ))
            } else {
                None
            });
        }

        if conditional.no_branch_alternation.is_some() {
            spans.push(if capture_present {
                None
            } else {
                Some((
                    last_branch_start,
                    last_branch_start + last_branch.chars().count(),
                ))
            });
        }

        spans
    }
}

impl<'a> QuantifiedConditionalGroupExistsWholePattern<'a> {
    fn group_count(&self) -> usize {
        self.conditional.group_count()
    }

    fn named_groups(&self) -> Vec<NamedGroup> {
        self.conditional.named_groups()
    }

    fn group_spans(&self, capture_span: Option<(usize, usize)>) -> Vec<Option<(usize, usize)>> {
        vec![capture_span]
    }
}

impl<'a> RangedRepeatGroupPattern<'a> {
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

    fn group_spans(&self, match_start: usize, repeat_count: usize) -> Vec<Option<(usize, usize)>> {
        let prefix_len = self.prefix.chars().count();
        let capture_len = self.capture.body.chars().count();
        let start = match_start + prefix_len + capture_len * repeat_count.saturating_sub(1);
        let end = start + capture_len;
        vec![Some((start, end))]
    }
}

impl<'a> WiderRangedRepeatGroupedAlternationBacktrackingHeavyPattern<'a> {
    fn group_count(&self) -> usize {
        2
    }

    fn named_groups(&self) -> Vec<NamedGroup> {
        self.outer_name
            .map(|name| {
                vec![NamedGroup {
                    name: name.to_string(),
                    index: 1,
                }]
            })
            .unwrap_or_default()
    }

    fn group_spans(
        &self,
        outer_span: (usize, usize),
        inner_span: (usize, usize),
    ) -> Vec<Option<(usize, usize)>> {
        vec![Some(outer_span), Some(inner_span)]
    }

    fn matched_lastindex(&self, group_spans: &[Option<(usize, usize)>]) -> Option<usize> {
        group_spans.first().copied().flatten().map(|_| 1)
    }
}

impl<'a> OpenEndedQuantifiedGroupAlternationBacktrackingHeavyPattern<'a> {
    fn group_count(&self) -> usize {
        2
    }

    fn named_groups(&self) -> Vec<NamedGroup> {
        self.outer_name
            .map(|name| {
                vec![NamedGroup {
                    name: name.to_string(),
                    index: 1,
                }]
            })
            .unwrap_or_default()
    }

    fn group_spans(
        &self,
        outer_span: (usize, usize),
        inner_span: (usize, usize),
    ) -> Vec<Option<(usize, usize)>> {
        vec![Some(outer_span), Some(inner_span)]
    }

    fn matched_lastindex(&self, group_spans: &[Option<(usize, usize)>]) -> Option<usize> {
        group_spans.first().copied().flatten().map(|_| 1)
    }
}

impl<'a> NestedOpenEndedQuantifiedGroupAlternationPattern<'a> {
    fn group_count(&self) -> usize {
        2
    }

    fn named_groups(&self) -> Vec<NamedGroup> {
        self.outer_name
            .map(|name| {
                vec![NamedGroup {
                    name: name.to_string(),
                    index: 1,
                }]
            })
            .unwrap_or_default()
    }

    fn group_spans(
        &self,
        outer_span: (usize, usize),
        inner_span: (usize, usize),
    ) -> Vec<Option<(usize, usize)>> {
        vec![Some(outer_span), Some(inner_span)]
    }

    fn matched_lastindex(&self, group_spans: &[Option<(usize, usize)>]) -> Option<usize> {
        group_spans.first().copied().flatten().map(|_| 1)
    }
}

impl<'a> NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationPattern<'a> {
    fn group_count(&self) -> usize {
        2
    }

    fn named_groups(&self) -> Vec<NamedGroup> {
        self.outer_name
            .map(|name| {
                vec![NamedGroup {
                    name: name.to_string(),
                    index: 1,
                }]
            })
            .unwrap_or_default()
    }

    fn group_spans(
        &self,
        outer_span: (usize, usize),
        inner_span: (usize, usize),
    ) -> Vec<Option<(usize, usize)>> {
        vec![Some(outer_span), Some(inner_span)]
    }

    fn matched_lastindex(&self, group_spans: &[Option<(usize, usize)>]) -> Option<usize> {
        group_spans.first().copied().flatten().map(|_| 1)
    }
}

impl<'a> NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationBacktrackingHeavyPattern<'a> {
    fn group_count(&self) -> usize {
        3
    }

    fn named_groups(&self) -> Vec<NamedGroup> {
        self.outer_name
            .map(|name| {
                vec![NamedGroup {
                    name: name.to_string(),
                    index: 1,
                }]
            })
            .unwrap_or_default()
    }

    fn group_spans(
        &self,
        outer_span: (usize, usize),
        repeated_span: (usize, usize),
        inner_span: (usize, usize),
    ) -> Vec<Option<(usize, usize)>> {
        vec![Some(outer_span), Some(repeated_span), Some(inner_span)]
    }

    fn matched_lastindex(&self, group_spans: &[Option<(usize, usize)>]) -> Option<usize> {
        group_spans.first().copied().flatten().map(|_| 1)
    }
}

impl<'a> NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationConditionalPattern<'a> {
    fn group_count(&self) -> usize {
        3
    }

    fn named_groups(&self) -> Vec<NamedGroup> {
        self.outer_name
            .map(|name| {
                vec![NamedGroup {
                    name: name.to_string(),
                    index: 1,
                }]
            })
            .unwrap_or_default()
    }

    fn group_spans(
        &self,
        outer_span: Option<(usize, usize)>,
        inner_span: Option<(usize, usize)>,
        branch_span: Option<(usize, usize)>,
    ) -> Vec<Option<(usize, usize)>> {
        vec![outer_span, inner_span, branch_span]
    }

    fn matched_lastindex(&self, group_spans: &[Option<(usize, usize)>]) -> Option<usize> {
        group_spans.first().copied().flatten().map(|_| 1)
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
        PatternRef::Str("a(?(?=b)b|c)d") => Some(CompileError {
            message: "bad character in group name '?=b'",
            pos: Some(4),
        }),
        PatternRef::Str("a(?(?!b)b|c)d") => Some(CompileError {
            message: "bad character in group name '?!b'",
            pos: Some(4),
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
        PatternRef::Str(pattern)
            if parse_quantified_nested_capture_literal_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_quantified_nested_capture_literal_pattern_str(pattern)
                .expect("guarded quantified nested capture literal");
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
            if parse_quantified_nested_group_alternation_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_quantified_nested_group_alternation_pattern_str(pattern)
                .expect("guarded quantified nested-group alternation literal");
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
            if parse_quantified_nested_group_alternation_branch_local_numbered_backreference_pattern_str(pattern)
                .is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_quantified_nested_group_alternation_branch_local_numbered_backreference_pattern_str(
                    pattern,
                )
                .expect(
                    "guarded quantified nested-group alternation branch-local numbered backreference literal",
                );
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
            if parse_quantified_nested_group_alternation_branch_local_named_backreference_pattern_str(pattern)
                .is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_quantified_nested_group_alternation_branch_local_named_backreference_pattern_str(
                    pattern,
                )
                .expect(
                    "guarded quantified nested-group alternation branch-local named backreference literal",
                );
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
            if parse_nested_alternation_literal_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_nested_alternation_literal_pattern_str(pattern)
                .expect("guarded nested alternation literal");
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
            if parse_nested_alternation_branch_local_numbered_backreference_pattern_str(pattern)
                .is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_nested_alternation_branch_local_numbered_backreference_pattern_str(pattern)
                    .expect(
                        "guarded nested alternation branch-local numbered backreference literal",
                    );
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
            if parse_nested_alternation_branch_local_named_backreference_pattern_str(pattern)
                .is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_nested_alternation_branch_local_named_backreference_pattern_str(pattern)
                    .expect(
                        "guarded nested alternation branch-local named backreference literal",
                    );
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
            if parse_branch_local_numbered_backreference_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_branch_local_numbered_backreference_pattern_str(pattern)
                .expect("guarded branch-local numbered backreference literal");
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
            if parse_branch_local_named_backreference_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_branch_local_named_backreference_pattern_str(pattern)
                .expect("guarded branch-local named backreference literal");
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
            if parse_quantified_branch_local_numbered_backreference_pattern_str(pattern)
                .is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_quantified_branch_local_numbered_backreference_pattern_str(pattern)
                    .expect("guarded quantified branch-local numbered backreference literal");
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
            if parse_quantified_branch_local_named_backreference_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_quantified_branch_local_named_backreference_pattern_str(pattern)
                    .expect("guarded quantified branch-local named backreference literal");
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
            if parse_conditional_branch_local_numbered_backreference_pattern_str(pattern)
                .is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_conditional_branch_local_numbered_backreference_pattern_str(pattern)
                    .expect("guarded conditional branch-local numbered backreference literal");
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
            if parse_conditional_branch_local_named_backreference_pattern_str(pattern)
                .is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_conditional_branch_local_named_backreference_pattern_str(pattern)
                    .expect("guarded conditional branch-local named backreference literal");
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
            if parse_optional_group_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_optional_group_pattern_str(pattern).expect("guarded optional group literal");
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
            if parse_optional_group_alternation_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_optional_group_alternation_pattern_str(pattern)
                .expect("guarded optional-group alternation literal");
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
            if parse_optional_group_alternation_branch_local_numbered_backreference_pattern_str(
                pattern,
            )
            .is_some() && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_optional_group_alternation_branch_local_numbered_backreference_pattern_str(
                    pattern,
                )
                .expect(
                    "guarded optional-group alternation branch-local numbered backreference literal",
                );
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
            if parse_optional_group_alternation_branch_local_named_backreference_pattern_str(
                pattern,
            )
            .is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_optional_group_alternation_branch_local_named_backreference_pattern_str(
                    pattern,
                )
                .expect(
                    "guarded optional-group alternation branch-local named backreference literal",
                );
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
            if parse_quantified_conditional_group_exists_whole_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_quantified_conditional_group_exists_whole_pattern_str(pattern)
                    .expect("guarded quantified whole conditional group-exists literal");
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
            if parse_quantified_conditional_group_exists_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_quantified_conditional_group_exists_pattern_str(pattern)
                .expect("guarded quantified conditional group-exists literal");
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
            if parse_conditional_group_exists_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_conditional_group_exists_pattern_str(pattern)
                .expect("guarded conditional group-exists literal");
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
            if parse_exact_repeat_group_alternation_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_exact_repeat_group_alternation_pattern_str(pattern)
                .expect("guarded exact-repeat grouped alternation literal");
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
            if parse_exact_repeat_group_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_exact_repeat_group_pattern_str(pattern)
                .expect("guarded exact-repeat group literal");
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
            if parse_ranged_repeat_group_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_ranged_repeat_group_pattern_str(pattern)
                .expect("guarded ranged-repeat group literal");
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
            if parse_nested_open_ended_quantified_group_alternation_pattern_str(pattern)
                .is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_nested_open_ended_quantified_group_alternation_pattern_str(pattern)
                    .expect("guarded nested open-ended grouped alternation literal");
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
            if parse_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_pattern_str(
                pattern,
            )
            .is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_pattern_str(
                    pattern,
                )
                .expect("guarded nested broader-range grouped alternation literal");
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
            if parse_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_pattern_str(
                pattern,
            )
            .is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_pattern_str(
                    pattern,
                )
                .expect("guarded nested broader-range grouped backtracking-heavy literal");
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
            if parse_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_pattern_str(
                pattern,
            )
            .is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_pattern_str(
                    pattern,
                )
                .expect("guarded nested broader-range grouped alternation conditional literal");
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
            if parse_open_ended_quantified_group_alternation_backtracking_heavy_pattern_str(
                pattern,
            )
            .is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_open_ended_quantified_group_alternation_backtracking_heavy_pattern_str(
                    pattern,
                )
                .expect("guarded open-ended grouped backtracking-heavy literal");
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
            if parse_wider_ranged_repeat_grouped_alternation_backtracking_heavy_pattern_str(
                pattern,
            )
            .is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_wider_ranged_repeat_grouped_alternation_backtracking_heavy_pattern_str(
                    pattern,
                )
                .expect("guarded wider ranged-repeat grouped backtracking-heavy literal");
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
            if parse_quantified_alternation_nested_branch_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_quantified_alternation_nested_branch_pattern_str(pattern)
                .expect("guarded quantified-alternation nested-branch literal");
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
            if parse_quantified_alternation_conditional_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_quantified_alternation_conditional_pattern_str(pattern)
                .expect("guarded quantified-alternation conditional literal");
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
            if parse_quantified_alternation_backtracking_heavy_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_quantified_alternation_backtracking_heavy_pattern_str(pattern)
                    .expect("guarded quantified-alternation backtracking-heavy literal");
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
            if parse_quantified_alternation_pattern_str(pattern).is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern = parse_quantified_alternation_pattern_str(pattern)
                .expect("guarded quantified-alternation literal");
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
            if parse_quantified_alternation_branch_local_numbered_backreference_pattern_str(
                pattern,
            )
            .is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_quantified_alternation_branch_local_numbered_backreference_pattern_str(
                    pattern,
                )
                .expect(
                    "guarded quantified-alternation branch-local numbered backreference literal",
                );
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
            if parse_quantified_alternation_branch_local_named_backreference_pattern_str(
                pattern,
            )
            .is_some()
                && normalized_flags == FLAG_UNICODE =>
        {
            let grouped_pattern =
                parse_quantified_alternation_branch_local_named_backreference_pattern_str(pattern)
                    .expect(
                        "guarded quantified-alternation branch-local named backreference literal",
                    );
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

fn parse_quantified_nested_capture_literal_pattern_str(
    pattern: &str,
) -> Option<QuantifiedNestedCaptureLiteralPattern<'_>> {
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

    let inner_remainder = outer_body.strip_prefix('(')?;
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

    let suffix = inner_remainder[inner_close_offset + 1..].strip_prefix("+)")?;
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(QuantifiedNestedCaptureLiteralPattern {
        prefix,
        outer_name,
        inner_capture: LiteralCapture {
            body: inner_body,
            name: inner_name,
        },
        suffix,
    })
}

fn parse_quantified_nested_group_alternation_pattern_str(
    pattern: &str,
) -> Option<QuantifiedNestedGroupAlternationPattern<'_>> {
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

    let inner_remainder = outer_body.strip_prefix('(')?;
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

    if outer_name.is_some() != inner_name.is_some() {
        return None;
    }

    let branches: Vec<&str> = inner_body.split('|').collect();
    if branches.as_slice() != ["b", "c"] {
        return None;
    }

    let suffix = inner_remainder[inner_close_offset + 1..].strip_prefix("+)")?;
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(QuantifiedNestedGroupAlternationPattern {
        prefix,
        outer_name,
        inner_name,
        branches,
        suffix,
    })
}

fn parse_quantified_nested_group_alternation_branch_local_numbered_backreference_pattern_str(
    pattern: &str,
) -> Option<QuantifiedNestedGroupAlternationBranchLocalBackreferencePattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let inner_remainder = remainder.strip_prefix('(')?;
    if inner_remainder.starts_with("?P<") {
        return None;
    }

    let inner_close_offset = inner_remainder.find(')')?;
    let inner_body = &inner_remainder[..inner_close_offset];
    let branches: Vec<&str> = inner_body.split('|').collect();
    if branches.as_slice() != ["b", "c"] {
        return None;
    }

    let quantifier_and_remainder = &inner_remainder[inner_close_offset + 1..];
    let (max_repeat, quantified_remainder) =
        if let Some(quantified_remainder) = quantifier_and_remainder.strip_prefix("+)") {
            (None, quantified_remainder)
        } else {
            let quantified_remainder = quantifier_and_remainder.strip_prefix("{1,4})")?;
            (Some(4), quantified_remainder)
        };

    let suffix = quantified_remainder.strip_prefix(r"\2")?;
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(
        QuantifiedNestedGroupAlternationBranchLocalBackreferencePattern {
            prefix,
            outer_name: None,
            inner_name: None,
            branches,
            suffix,
            max_repeat,
        },
    )
}

fn parse_quantified_nested_group_alternation_branch_local_named_backreference_pattern_str(
    pattern: &str,
) -> Option<QuantifiedNestedGroupAlternationBranchLocalBackreferencePattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let outer_remainder = remainder.strip_prefix("?P<")?;
    let outer_name_end = outer_remainder.find('>')?;
    let outer_name = &outer_remainder[..outer_name_end];
    if !is_supported_group_name(outer_name) {
        return None;
    }

    let outer_body = &outer_remainder[outer_name_end + 1..];
    let inner_remainder = outer_body.strip_prefix("(?P<")?;
    let inner_name_end = inner_remainder.find('>')?;
    let inner_name = &inner_remainder[..inner_name_end];
    if !is_supported_group_name(inner_name) {
        return None;
    }

    let inner_body_and_remainder = &inner_remainder[inner_name_end + 1..];
    let inner_close_offset = inner_body_and_remainder.find(')')?;
    let inner_body = &inner_body_and_remainder[..inner_close_offset];
    let branches: Vec<&str> = inner_body.split('|').collect();
    if branches.as_slice() != ["b", "c"] {
        return None;
    }

    let quantifier_and_remainder = &inner_body_and_remainder[inner_close_offset + 1..];
    let (max_repeat, quantified_remainder) =
        if let Some(quantified_remainder) = quantifier_and_remainder.strip_prefix("+)") {
            (None, quantified_remainder)
        } else {
            let quantified_remainder = quantifier_and_remainder.strip_prefix("{1,4})")?;
            (Some(4), quantified_remainder)
        };

    let backreference = quantified_remainder.strip_prefix("(?P=")?;
    let reference_close_offset = backreference.find(')')?;
    let reference_name = &backreference[..reference_close_offset];
    if reference_name != inner_name {
        return None;
    }

    let suffix = &backreference[reference_close_offset + 1..];
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(
        QuantifiedNestedGroupAlternationBranchLocalBackreferencePattern {
            prefix,
            outer_name: Some(outer_name),
            inner_name: Some(inner_name),
            branches,
            suffix,
            max_repeat,
        },
    )
}

fn parse_nested_alternation_literal_pattern_str(
    pattern: &str,
) -> Option<NestedAlternationLiteralPattern<'_>> {
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
    let (inner_capture_name, inner_body, inner_close_offset) =
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

    let inner_branches: Vec<&str> = inner_body.split('|').collect();
    if inner_branches.len() < 2
        || inner_branches
            .iter()
            .any(|branch| branch.is_empty() || branch.chars().any(is_meta_character))
    {
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

    Some(NestedAlternationLiteralPattern {
        prefix,
        outer_name,
        outer_prefix,
        inner_capture_name,
        inner_branches,
        outer_suffix,
        suffix,
    })
}

fn parse_nested_alternation_branch_local_numbered_backreference_pattern_str(
    pattern: &str,
) -> Option<NestedAlternationBranchLocalBackreferencePattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let inner_remainder = remainder.strip_prefix('(')?;
    if inner_remainder.starts_with("?P<") {
        return None;
    }

    let inner_close_offset = inner_remainder.find(')')?;
    let inner_body = &inner_remainder[..inner_close_offset];
    let branches: Vec<&str> = inner_body.split('|').collect();
    if branches.len() < 2
        || branches
            .iter()
            .any(|branch| branch.is_empty() || branch.chars().any(is_meta_character))
    {
        return None;
    }

    let outer_remainder = inner_remainder[inner_close_offset + 1..].strip_prefix(')')?;
    let suffix = outer_remainder.strip_prefix(r"\2")?;
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(NestedAlternationBranchLocalBackreferencePattern {
        prefix,
        outer_name: None,
        inner_name: None,
        branches,
        suffix,
    })
}

fn parse_nested_alternation_branch_local_named_backreference_pattern_str(
    pattern: &str,
) -> Option<NestedAlternationBranchLocalBackreferencePattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let outer_remainder = remainder.strip_prefix("?P<")?;
    let outer_name_end = outer_remainder.find('>')?;
    let outer_name = &outer_remainder[..outer_name_end];
    if !is_supported_group_name(outer_name) {
        return None;
    }

    let outer_body = &outer_remainder[outer_name_end + 1..];
    let inner_remainder = outer_body.strip_prefix("(?P<")?;
    let inner_name_end = inner_remainder.find('>')?;
    let inner_name = &inner_remainder[..inner_name_end];
    if !is_supported_group_name(inner_name) {
        return None;
    }

    let inner_body_and_remainder = &inner_remainder[inner_name_end + 1..];
    let inner_close_offset = inner_body_and_remainder.find(')')?;
    let inner_body = &inner_body_and_remainder[..inner_close_offset];
    let branches: Vec<&str> = inner_body.split('|').collect();
    if branches.len() < 2
        || branches
            .iter()
            .any(|branch| branch.is_empty() || branch.chars().any(is_meta_character))
    {
        return None;
    }

    let after_outer = inner_body_and_remainder[inner_close_offset + 1..].strip_prefix(')')?;
    let backreference = after_outer.strip_prefix("(?P=")?;
    let reference_close_offset = backreference.find(')')?;
    let reference_name = &backreference[..reference_close_offset];
    if reference_name != inner_name {
        return None;
    }

    let suffix = &backreference[reference_close_offset + 1..];
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(NestedAlternationBranchLocalBackreferencePattern {
        prefix,
        outer_name: Some(outer_name),
        inner_name: Some(inner_name),
        branches,
        suffix,
    })
}

fn parse_branch_local_numbered_backreference_pattern_str(
    pattern: &str,
) -> Option<BranchLocalBackreferencePattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let inner_remainder = remainder.strip_prefix('(')?;
    if inner_remainder.starts_with("?P<") {
        return None;
    }

    let inner_close_offset = inner_remainder.find(')')?;
    let inner_body = &inner_remainder[..inner_close_offset];
    if inner_body.is_empty() || inner_body.chars().any(is_meta_character) {
        return None;
    }

    let alternate_and_outer = inner_remainder[inner_close_offset + 1..].strip_prefix('|')?;
    let outer_close_offset = alternate_and_outer.find(')')?;
    let alternate_branch = &alternate_and_outer[..outer_close_offset];
    if alternate_branch.is_empty() || alternate_branch.chars().any(is_meta_character) {
        return None;
    }

    let suffix = alternate_and_outer[outer_close_offset + 1..].strip_prefix(r"\2")?;
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(BranchLocalBackreferencePattern {
        prefix,
        outer_name: None,
        inner_name: None,
        inner_body,
        _alternate_branch: alternate_branch,
        suffix,
    })
}

fn parse_branch_local_named_backreference_pattern_str(
    pattern: &str,
) -> Option<BranchLocalBackreferencePattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let outer_remainder = remainder.strip_prefix("?P<")?;
    let outer_name_end = outer_remainder.find('>')?;
    let outer_name = &outer_remainder[..outer_name_end];
    if !is_supported_group_name(outer_name) {
        return None;
    }

    let outer_body = &outer_remainder[outer_name_end + 1..];
    let inner_remainder = outer_body.strip_prefix("(?P<")?;
    let inner_name_end = inner_remainder.find('>')?;
    let inner_name = &inner_remainder[..inner_name_end];
    if !is_supported_group_name(inner_name) {
        return None;
    }

    let inner_body_and_remainder = &inner_remainder[inner_name_end + 1..];
    let inner_close_offset = inner_body_and_remainder.find(')')?;
    let inner_body = &inner_body_and_remainder[..inner_close_offset];
    if inner_body.is_empty() || inner_body.chars().any(is_meta_character) {
        return None;
    }

    let alternate_and_outer =
        inner_body_and_remainder[inner_close_offset + 1..].strip_prefix('|')?;
    let outer_close_offset = alternate_and_outer.find(')')?;
    let alternate_branch = &alternate_and_outer[..outer_close_offset];
    if alternate_branch.is_empty() || alternate_branch.chars().any(is_meta_character) {
        return None;
    }

    let backreference_and_suffix = &alternate_and_outer[outer_close_offset + 1..];
    let backreference = backreference_and_suffix.strip_prefix("(?P=")?;
    let reference_close_offset = backreference.find(')')?;
    let reference_name = &backreference[..reference_close_offset];
    if reference_name != inner_name {
        return None;
    }

    let suffix = &backreference[reference_close_offset + 1..];
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(BranchLocalBackreferencePattern {
        prefix,
        outer_name: Some(outer_name),
        inner_name: Some(inner_name),
        inner_body,
        _alternate_branch: alternate_branch,
        suffix,
    })
}

fn parse_quantified_branch_local_numbered_backreference_pattern_str(
    pattern: &str,
) -> Option<QuantifiedBranchLocalBackreferencePattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let inner_remainder = remainder.strip_prefix('(')?;
    if inner_remainder.starts_with("?P<") {
        return None;
    }

    let inner_close_offset = inner_remainder.find(')')?;
    let inner_body = &inner_remainder[..inner_close_offset];
    if inner_body.is_empty() || inner_body.chars().any(is_meta_character) {
        return None;
    }

    let alternate_and_outer = inner_remainder[inner_close_offset + 1..].strip_prefix("+|")?;
    let outer_close_offset = alternate_and_outer.find(')')?;
    let alternate_branch = &alternate_and_outer[..outer_close_offset];
    if alternate_branch.is_empty() || alternate_branch.chars().any(is_meta_character) {
        return None;
    }

    let suffix = alternate_and_outer[outer_close_offset + 1..].strip_prefix(r"\2")?;
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(QuantifiedBranchLocalBackreferencePattern {
        prefix,
        outer_name: None,
        inner_name: None,
        inner_body,
        _alternate_branch: alternate_branch,
        suffix,
    })
}

fn parse_quantified_branch_local_named_backreference_pattern_str(
    pattern: &str,
) -> Option<QuantifiedBranchLocalBackreferencePattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let outer_remainder = remainder.strip_prefix("?P<")?;
    let outer_name_end = outer_remainder.find('>')?;
    let outer_name = &outer_remainder[..outer_name_end];
    if !is_supported_group_name(outer_name) {
        return None;
    }

    let outer_body = &outer_remainder[outer_name_end + 1..];
    let inner_remainder = outer_body.strip_prefix("(?P<")?;
    let inner_name_end = inner_remainder.find('>')?;
    let inner_name = &inner_remainder[..inner_name_end];
    if !is_supported_group_name(inner_name) {
        return None;
    }

    let inner_body_and_remainder = &inner_remainder[inner_name_end + 1..];
    let inner_close_offset = inner_body_and_remainder.find(')')?;
    let inner_body = &inner_body_and_remainder[..inner_close_offset];
    if inner_body.is_empty() || inner_body.chars().any(is_meta_character) {
        return None;
    }

    let alternate_and_outer =
        inner_body_and_remainder[inner_close_offset + 1..].strip_prefix("+|")?;
    let outer_close_offset = alternate_and_outer.find(')')?;
    let alternate_branch = &alternate_and_outer[..outer_close_offset];
    if alternate_branch.is_empty() || alternate_branch.chars().any(is_meta_character) {
        return None;
    }

    let backreference_and_suffix = &alternate_and_outer[outer_close_offset + 1..];
    let backreference = backreference_and_suffix.strip_prefix("(?P=")?;
    let reference_close_offset = backreference.find(')')?;
    let reference_name = &backreference[..reference_close_offset];
    if reference_name != inner_name {
        return None;
    }

    let suffix = &backreference[reference_close_offset + 1..];
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(QuantifiedBranchLocalBackreferencePattern {
        prefix,
        outer_name: Some(outer_name),
        inner_name: Some(inner_name),
        inner_body,
        _alternate_branch: alternate_branch,
        suffix,
    })
}

fn parse_conditional_branch_local_numbered_backreference_pattern_str(
    pattern: &str,
) -> Option<ConditionalBranchLocalBackreferencePattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let inner_remainder = remainder.strip_prefix('(')?;
    if inner_remainder.starts_with("?P<") {
        return None;
    }

    let inner_close_offset = inner_remainder.find(')')?;
    let inner_body = &inner_remainder[..inner_close_offset];
    if inner_body.is_empty() || inner_body.chars().any(is_meta_character) {
        return None;
    }

    let alternate_and_outer = inner_remainder[inner_close_offset + 1..].strip_prefix('|')?;
    let outer_close_offset = alternate_and_outer.find(')')?;
    let alternate_branch = &alternate_and_outer[..outer_close_offset];
    if alternate_branch.is_empty() || alternate_branch.chars().any(is_meta_character) {
        return None;
    }

    let conditional = alternate_and_outer[outer_close_offset + 1..]
        .strip_prefix(r"\2(?(2)")?
        .strip_suffix(')')?;
    let (yes_branch, no_branch) = split_first_top_level_pipe(conditional)?;
    if yes_branch.is_empty()
        || no_branch.is_empty()
        || yes_branch.chars().any(is_meta_character)
        || no_branch.chars().any(is_meta_character)
    {
        return None;
    }

    Some(ConditionalBranchLocalBackreferencePattern {
        prefix,
        outer_name: None,
        inner_name: None,
        inner_body,
        _alternate_branch: alternate_branch,
        yes_branch,
        _no_branch: no_branch,
    })
}

fn parse_conditional_branch_local_named_backreference_pattern_str(
    pattern: &str,
) -> Option<ConditionalBranchLocalBackreferencePattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let outer_remainder = remainder.strip_prefix("?P<")?;
    let outer_name_end = outer_remainder.find('>')?;
    let outer_name = &outer_remainder[..outer_name_end];
    if !is_supported_group_name(outer_name) {
        return None;
    }

    let outer_body = &outer_remainder[outer_name_end + 1..];
    let inner_remainder = outer_body.strip_prefix("(?P<")?;
    let inner_name_end = inner_remainder.find('>')?;
    let inner_name = &inner_remainder[..inner_name_end];
    if !is_supported_group_name(inner_name) {
        return None;
    }

    let inner_body_and_remainder = &inner_remainder[inner_name_end + 1..];
    let inner_close_offset = inner_body_and_remainder.find(')')?;
    let inner_body = &inner_body_and_remainder[..inner_close_offset];
    if inner_body.is_empty() || inner_body.chars().any(is_meta_character) {
        return None;
    }

    let alternate_and_outer =
        inner_body_and_remainder[inner_close_offset + 1..].strip_prefix('|')?;
    let outer_close_offset = alternate_and_outer.find(')')?;
    let alternate_branch = &alternate_and_outer[..outer_close_offset];
    if alternate_branch.is_empty() || alternate_branch.chars().any(is_meta_character) {
        return None;
    }

    let after_backreference = alternate_and_outer[outer_close_offset + 1..]
        .strip_prefix("(?P=")?
        .strip_prefix(inner_name)?
        .strip_prefix(")(?(")?;
    let reference_end = after_backreference.find(')')?;
    if &after_backreference[..reference_end] != inner_name {
        return None;
    }
    let branches = after_backreference[reference_end + 1..].strip_suffix(')')?;
    let (yes_branch, no_branch) = split_first_top_level_pipe(branches)?;
    if yes_branch.is_empty()
        || no_branch.is_empty()
        || yes_branch.chars().any(is_meta_character)
        || no_branch.chars().any(is_meta_character)
    {
        return None;
    }

    Some(ConditionalBranchLocalBackreferencePattern {
        prefix,
        outer_name: Some(outer_name),
        inner_name: Some(inner_name),
        inner_body,
        _alternate_branch: alternate_branch,
        yes_branch,
        _no_branch: no_branch,
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

fn parse_optional_group_pattern_str(pattern: &str) -> Option<OptionalGroupPattern<'_>> {
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

    let suffix = remainder[close_offset + 1..].strip_prefix('?')?;
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(OptionalGroupPattern {
        prefix,
        capture: LiteralCapture { body, name },
        suffix,
    })
}

fn parse_optional_group_alternation_pattern_str(
    pattern: &str,
) -> Option<OptionalGroupAlternationPattern<'_>> {
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

    let suffix = remainder[close_offset + 1..].strip_prefix('?')?;
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(OptionalGroupAlternationPattern {
        prefix,
        branches,
        capture_name,
        suffix,
    })
}

fn parse_optional_group_alternation_branch_local_numbered_backreference_pattern_str(
    pattern: &str,
) -> Option<OptionalGroupAlternationBranchLocalBackreferencePattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let inner_remainder = remainder.strip_prefix('(')?;
    if inner_remainder.starts_with("?P<") {
        return None;
    }

    let inner_close_offset = inner_remainder.find(')')?;
    let inner_body = &inner_remainder[..inner_close_offset];
    let branches: Vec<&str> = inner_body.split('|').collect();
    if branches.len() < 2
        || branches
            .iter()
            .any(|branch| branch.is_empty() || branch.chars().any(is_meta_character))
    {
        return None;
    }

    let suffix = inner_remainder[inner_close_offset + 1..].strip_prefix(r"\2)?")?;
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(OptionalGroupAlternationBranchLocalBackreferencePattern {
        prefix,
        outer_name: None,
        inner_name: None,
        branches,
        suffix,
    })
}

fn parse_optional_group_alternation_branch_local_named_backreference_pattern_str(
    pattern: &str,
) -> Option<OptionalGroupAlternationBranchLocalBackreferencePattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let outer_remainder = remainder.strip_prefix("?P<")?;
    let outer_name_end = outer_remainder.find('>')?;
    let outer_name = &outer_remainder[..outer_name_end];
    if !is_supported_group_name(outer_name) {
        return None;
    }

    let outer_body = &outer_remainder[outer_name_end + 1..];
    let inner_remainder = outer_body.strip_prefix("(?P<")?;
    let inner_name_end = inner_remainder.find('>')?;
    let inner_name = &inner_remainder[..inner_name_end];
    if !is_supported_group_name(inner_name) {
        return None;
    }

    let inner_body_and_remainder = &inner_remainder[inner_name_end + 1..];
    let inner_close_offset = inner_body_and_remainder.find(')')?;
    let inner_body = &inner_body_and_remainder[..inner_close_offset];
    let branches: Vec<&str> = inner_body.split('|').collect();
    if branches.len() < 2
        || branches
            .iter()
            .any(|branch| branch.is_empty() || branch.chars().any(is_meta_character))
    {
        return None;
    }

    let backreference = inner_body_and_remainder[inner_close_offset + 1..].strip_prefix("(?P=")?;
    let reference_close_offset = backreference.find(')')?;
    let reference_name = &backreference[..reference_close_offset];
    if reference_name != inner_name {
        return None;
    }

    let suffix = backreference[reference_close_offset + 1..].strip_prefix(")?")?;
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(OptionalGroupAlternationBranchLocalBackreferencePattern {
        prefix,
        outer_name: Some(outer_name),
        inner_name: Some(inner_name),
        branches,
        suffix,
    })
}

fn parse_quantified_alternation_pattern_str(
    pattern: &str,
) -> Option<QuantifiedAlternationPattern<'_>> {
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
    let branch_len = branches[0].chars().count();
    if branches
        .iter()
        .any(|branch| branch.chars().count() != branch_len)
    {
        return None;
    }

    let (min_repeat, max_repeat, suffix) =
        if let Some(suffix) = remainder[close_offset + 1..].strip_prefix("{1,2}") {
            (1, Some(2), suffix)
        } else if let Some(suffix) = remainder[close_offset + 1..].strip_prefix("{1,3}") {
            (1, Some(3), suffix)
        } else if branches.as_slice() == ["bc", "de"] {
            if let Some(suffix) = remainder[close_offset + 1..].strip_prefix("{1,4}") {
                (1, Some(4), suffix)
            } else if let Some(suffix) = remainder[close_offset + 1..].strip_prefix("{1,}") {
                (1, None, suffix)
            } else {
                let suffix = remainder[close_offset + 1..].strip_prefix("{2,}")?;
                (2, None, suffix)
            }
        } else if matches!(branches.as_slice(), ["b", "c"] | ["bc", "de"]) {
            if let Some(suffix) = remainder[close_offset + 1..].strip_prefix("{1,}") {
                (1, None, suffix)
            } else {
                return None;
            }
        } else {
            return None;
        };
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(QuantifiedAlternationPattern {
        prefix,
        branches,
        capture_name,
        suffix,
        min_repeat,
        max_repeat,
    })
}

fn parse_quantified_alternation_backtracking_heavy_pattern_str(
    pattern: &str,
) -> Option<QuantifiedAlternationPattern<'_>> {
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
    if branches.len() != 2
        || branches
            .iter()
            .any(|branch| branch.is_empty() || branch.chars().any(is_meta_character))
    {
        return None;
    }

    let first_len = branches[0].chars().count();
    let second_len = branches[1].chars().count();
    if second_len != first_len + 1 || !branches[1].starts_with(branches[0]) {
        return None;
    }

    let suffix = remainder[close_offset + 1..].strip_prefix("{1,2}")?;
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(QuantifiedAlternationPattern {
        prefix,
        branches,
        capture_name,
        suffix,
        min_repeat: 1,
        max_repeat: Some(2),
    })
}

fn parse_quantified_alternation_nested_branch_pattern_str(
    pattern: &str,
) -> Option<QuantifiedAlternationNestedBranchPattern<'_>> {
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

    let inner_remainder = outer_body.strip_prefix('(')?;
    if inner_remainder.starts_with("?P<") {
        return None;
    }

    let inner_close_offset = inner_remainder.find(')')?;
    let inner_body = &inner_remainder[..inner_close_offset];
    let inner_branches: Vec<&str> = inner_body.split('|').collect();
    if inner_branches.len() < 2
        || inner_branches
            .iter()
            .any(|branch| branch.is_empty() || branch.chars().any(is_meta_character))
    {
        return None;
    }
    let inner_branch_len = inner_branches[0].chars().count();
    if inner_branches
        .iter()
        .any(|branch| branch.chars().count() != inner_branch_len)
    {
        return None;
    }

    let literal_branch_and_remainder =
        inner_remainder[inner_close_offset + 1..].strip_prefix('|')?;
    let outer_close_offset = literal_branch_and_remainder.find(')')?;
    let literal_branch = &literal_branch_and_remainder[..outer_close_offset];
    if literal_branch.is_empty() || literal_branch.chars().any(is_meta_character) {
        return None;
    }

    let suffix = literal_branch_and_remainder[outer_close_offset + 1..].strip_prefix("{1,2}")?;
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(QuantifiedAlternationNestedBranchPattern {
        prefix,
        outer_name,
        inner_branches,
        literal_branch,
        suffix,
        max_repeat: 2,
    })
}

fn parse_quantified_alternation_conditional_pattern_str(
    pattern: &str,
) -> Option<QuantifiedAlternationConditionalPattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let (outer_name, outer_body_and_remainder) =
        if let Some(named_remainder) = remainder.strip_prefix("?P<") {
            let outer_name_end = named_remainder.find('>')?;
            let outer_name = &named_remainder[..outer_name_end];
            if !is_supported_group_name(outer_name) {
                return None;
            }
            (Some(outer_name), &named_remainder[outer_name_end + 1..])
        } else {
            (None, remainder)
        };

    let inner_remainder = outer_body_and_remainder.strip_prefix('(')?;
    if inner_remainder.starts_with("?P<") {
        return None;
    }

    let inner_close_offset = inner_remainder.find(')')?;
    let inner_body = &inner_remainder[..inner_close_offset];
    let branches: Vec<&str> = inner_body.split('|').collect();
    if branches.len() < 2
        || branches
            .iter()
            .any(|branch| branch.is_empty() || branch.chars().any(is_meta_character))
    {
        return None;
    }
    let branch_len = branches[0].chars().count();
    if branches
        .iter()
        .any(|branch| branch.chars().count() != branch_len)
    {
        return None;
    }

    let (min_repeat, max_repeat, outer_suffix) = if let Some(outer_suffix) =
        inner_remainder[inner_close_offset + 1..].strip_prefix("{1,2})?")
    {
        (1, Some(2), outer_suffix)
    } else if branches.as_slice() == ["bc", "de"] {
        if let Some(outer_suffix) =
            inner_remainder[inner_close_offset + 1..].strip_prefix("{1,3})?")
        {
            (1, Some(3), outer_suffix)
        } else if let Some(outer_suffix) =
            inner_remainder[inner_close_offset + 1..].strip_prefix("{1,4})?")
        {
            (1, Some(4), outer_suffix)
        } else if let Some(outer_suffix) =
            inner_remainder[inner_close_offset + 1..].strip_prefix("{2,})?")
        {
            (2, None, outer_suffix)
        } else {
            let outer_suffix = inner_remainder[inner_close_offset + 1..].strip_prefix("{1,})?")?;
            (1, None, outer_suffix)
        }
    } else {
        return None;
    };
    let conditional = outer_suffix.strip_prefix("(?(")?.strip_suffix(')')?;
    let reference_end = conditional.find(')')?;
    let reference = &conditional[..reference_end];
    match outer_name {
        Some(name) if reference == name => {}
        None if reference == "1" => {}
        _ => return None,
    }

    let (yes_branch, no_branch) = split_first_top_level_pipe(&conditional[reference_end + 1..])?;
    if yes_branch.is_empty()
        || no_branch.is_empty()
        || yes_branch.chars().any(is_meta_character)
        || no_branch.chars().any(is_meta_character)
    {
        return None;
    }

    Some(QuantifiedAlternationConditionalPattern {
        prefix,
        outer_name,
        branches,
        yes_branch,
        no_branch,
        min_repeat,
        max_repeat,
    })
}

fn parse_quantified_alternation_branch_local_numbered_backreference_pattern_str(
    pattern: &str,
) -> Option<QuantifiedAlternationBranchLocalBackreferencePattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let inner_remainder = remainder.strip_prefix('(')?;
    if inner_remainder.starts_with("?P<") {
        return None;
    }

    let inner_close_offset = inner_remainder.find(')')?;
    let inner_body = &inner_remainder[..inner_close_offset];
    let branches: Vec<&str> = inner_body.split('|').collect();
    if branches.len() < 2
        || branches
            .iter()
            .any(|branch| branch.is_empty() || branch.chars().any(is_meta_character))
    {
        return None;
    }
    let branch_len = branches[0].chars().count();
    if branches
        .iter()
        .any(|branch| branch.chars().count() != branch_len)
    {
        return None;
    }

    let suffix = inner_remainder[inner_close_offset + 1..].strip_prefix(r"\2){1,2}")?;
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(QuantifiedAlternationBranchLocalBackreferencePattern {
        prefix,
        outer_name: None,
        inner_name: None,
        branches,
        suffix,
        max_repeat: 2,
    })
}

fn parse_quantified_alternation_branch_local_named_backreference_pattern_str(
    pattern: &str,
) -> Option<QuantifiedAlternationBranchLocalBackreferencePattern<'_>> {
    let open_offset = pattern.find('(')?;
    let prefix = &pattern[..open_offset];
    if prefix.is_empty() || prefix.chars().any(is_meta_character) {
        return None;
    }

    let remainder = &pattern[open_offset + 1..];
    let outer_remainder = remainder.strip_prefix("?P<")?;
    let outer_name_end = outer_remainder.find('>')?;
    let outer_name = &outer_remainder[..outer_name_end];
    if !is_supported_group_name(outer_name) {
        return None;
    }

    let outer_body = &outer_remainder[outer_name_end + 1..];
    let inner_remainder = outer_body.strip_prefix("(?P<")?;
    let inner_name_end = inner_remainder.find('>')?;
    let inner_name = &inner_remainder[..inner_name_end];
    if !is_supported_group_name(inner_name) {
        return None;
    }

    let inner_body_and_remainder = &inner_remainder[inner_name_end + 1..];
    let inner_close_offset = inner_body_and_remainder.find(')')?;
    let inner_body = &inner_body_and_remainder[..inner_close_offset];
    let branches: Vec<&str> = inner_body.split('|').collect();
    if branches.len() < 2
        || branches
            .iter()
            .any(|branch| branch.is_empty() || branch.chars().any(is_meta_character))
    {
        return None;
    }
    let branch_len = branches[0].chars().count();
    if branches
        .iter()
        .any(|branch| branch.chars().count() != branch_len)
    {
        return None;
    }

    let backreference_and_remainder = &inner_body_and_remainder[inner_close_offset + 1..];
    let backreference = backreference_and_remainder.strip_prefix("(?P=")?;
    let reference_close_offset = backreference.find(')')?;
    let reference_name = &backreference[..reference_close_offset];
    if reference_name != inner_name {
        return None;
    }

    let suffix = backreference[reference_close_offset + 1..].strip_prefix("){1,2}")?;
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(QuantifiedAlternationBranchLocalBackreferencePattern {
        prefix,
        outer_name: Some(outer_name),
        inner_name: Some(inner_name),
        branches,
        suffix,
        max_repeat: 2,
    })
}

fn split_first_top_level_pipe(value: &str) -> Option<(&str, &str)> {
    let mut depth = 0usize;
    for (index, character) in value.char_indices() {
        match character {
            '(' => depth += 1,
            ')' => depth = depth.checked_sub(1)?,
            '|' if depth == 0 => {
                return Some((&value[..index], &value[index + character.len_utf8()..]));
            }
            _ => {}
        }
    }
    (depth == 0).then_some((value, ""))
}

fn parse_grouped_literal_alternation_branch(branch: &str) -> Option<Vec<&str>> {
    let inner = branch.strip_prefix('(')?.strip_suffix(')')?;
    if inner
        .chars()
        .any(|character| matches!(character, '(' | ')'))
    {
        return None;
    }

    let branches: Vec<&str> = inner.split('|').collect();
    if branches.len() != 2
        || branches
            .iter()
            .any(|branch| branch.is_empty() || branch.chars().any(is_meta_character))
    {
        return None;
    }

    Some(branches)
}

fn parse_empty_non_capturing_alternation_branch(branch: &str) -> bool {
    let Some(inner) = branch.strip_prefix("(?:") else {
        return false;
    };
    let Some(inner) = inner.strip_suffix(')') else {
        return false;
    };
    let Some((left_branch, right_branch)) = split_first_top_level_pipe(inner) else {
        return false;
    };
    left_branch.is_empty() && right_branch.is_empty()
}

fn parse_nested_conditional_group_exists_yes_branch<'a>(
    branch: &'a str,
    capture_name: Option<&str>,
) -> Option<&'a str> {
    let conditional = branch.strip_prefix("(?(")?.strip_suffix(')')?;
    let reference_end = conditional.find(')')?;
    let reference = &conditional[..reference_end];
    match capture_name {
        Some(name) if reference == name => {}
        None if reference == "1" => {}
        _ => return None,
    }

    let inner_branches = &conditional[reference_end + 1..];
    let (inner_yes_branch, inner_no_branch) = split_first_top_level_pipe(inner_branches)?;
    if inner_yes_branch.is_empty() || inner_yes_branch.chars().any(is_meta_character) {
        return None;
    }
    if !inner_no_branch.is_empty() && inner_no_branch.chars().any(is_meta_character) {
        return None;
    }

    Some(inner_yes_branch)
}

fn parse_nested_conditional_group_exists_empty_yes_else_no_branch<'a>(
    branch: &'a str,
    capture_name: Option<&str>,
) -> Option<NestedConditionalGroupExistsEmptyYesElseBranch<'a>> {
    let conditional = branch.strip_prefix("(?(")?.strip_suffix(')')?;
    let reference_end = conditional.find(')')?;
    let reference = &conditional[..reference_end];
    match capture_name {
        Some(name) if reference == name => {}
        None if reference == "1" => {}
        _ => return None,
    }

    let inner_branches = &conditional[reference_end + 1..];
    let (inner_yes_branch, inner_no_branch) = split_first_top_level_pipe(inner_branches)?;
    if inner_yes_branch.is_empty()
        || inner_no_branch.is_empty()
        || inner_yes_branch.chars().any(is_meta_character)
        || inner_no_branch.chars().any(is_meta_character)
    {
        return None;
    }

    Some(NestedConditionalGroupExistsEmptyYesElseBranch {
        yes_branch: inner_yes_branch,
        no_branch: inner_no_branch,
    })
}

fn parse_nested_conditional_group_exists_fully_empty_no_branch(
    branch: &str,
    capture_name: Option<&str>,
) -> Option<NestedConditionalGroupExistsFullyEmptyBranch> {
    let conditional = branch.strip_prefix("(?(")?.strip_suffix(')')?;
    let reference_end = conditional.find(')')?;
    let reference = &conditional[..reference_end];
    match capture_name {
        Some(name) if reference == name => {}
        None if reference == "1" => {}
        _ => return None,
    }

    let inner_branches = &conditional[reference_end + 1..];
    let (inner_yes_branch, inner_no_branch) = split_first_top_level_pipe(inner_branches)?;
    if !inner_yes_branch.is_empty() || !inner_no_branch.is_empty() {
        return None;
    }

    Some(NestedConditionalGroupExistsFullyEmptyBranch)
}

fn parse_conditional_group_exists_pattern_str(
    pattern: &str,
) -> Option<ConditionalGroupExistsPattern<'_>> {
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

    if body.is_empty() || body.chars().any(is_meta_character) {
        return None;
    }

    let suffix_and_conditional = remainder[close_offset + 1..].strip_prefix('?')?;
    let conditional_offset = suffix_and_conditional.find("(?(")?;
    let middle = &suffix_and_conditional[..conditional_offset];
    if middle.is_empty() || middle.chars().any(is_meta_character) {
        return None;
    }

    let conditional = &suffix_and_conditional[conditional_offset + 3..];
    let reference_end = conditional.find(')')?;
    let reference = &conditional[..reference_end];
    match capture_name {
        Some(name) if reference == name => {}
        None if reference == "1" => {}
        _ => return None,
    }

    let branches = conditional[reference_end + 1..].strip_suffix(')')?;
    let (yes_branch, no_branch) = match split_first_top_level_pipe(branches) {
        Some((yes_branch, no_branch)) if no_branch.is_empty() && branches != yes_branch => {
            (yes_branch, Some(no_branch))
        }
        Some((yes_branch, _)) if branches == yes_branch => (yes_branch, None),
        Some((yes_branch, no_branch)) => (yes_branch, Some(no_branch)),
        None => return None,
    };

    let nested_yes_branch = if yes_branch.is_empty() {
        None
    } else {
        parse_nested_conditional_group_exists_yes_branch(yes_branch, capture_name)
    };
    let nested_no_branch = if yes_branch.is_empty() {
        no_branch.and_then(|branch| {
            parse_nested_conditional_group_exists_empty_yes_else_no_branch(branch, capture_name)
                .or_else(|| {
                    parse_nested_conditional_group_exists_fully_empty_no_branch(
                        branch,
                        capture_name,
                    )
                    .map(|_| NestedConditionalGroupExistsEmptyYesElseBranch {
                        yes_branch: "",
                        no_branch: "",
                    })
                })
        })
    } else {
        None
    };

    let normalized_yes_branch = nested_yes_branch.unwrap_or(yes_branch);
    let yes_branch_alternation = if normalized_yes_branch.is_empty() {
        None
    } else if nested_yes_branch.is_none() && normalized_yes_branch.chars().any(is_meta_character) {
        parse_grouped_literal_alternation_branch(normalized_yes_branch)
    } else {
        None
    };
    let normalized_no_branch = if normalized_yes_branch.is_empty()
        && no_branch.is_some_and(parse_empty_non_capturing_alternation_branch)
    {
        Some("")
    } else {
        no_branch
    };

    let no_branch_alternation = normalized_no_branch.and_then(|branch| {
        if nested_no_branch.is_some() || !branch.chars().any(is_meta_character) {
            return None;
        }
        parse_grouped_literal_alternation_branch(branch)
    });

    if yes_branch_alternation.is_none() && normalized_yes_branch.chars().any(is_meta_character) {
        return None;
    }

    if let Some(no_branch) = normalized_no_branch {
        if nested_no_branch.is_none()
            && no_branch_alternation.is_none()
            && no_branch.chars().any(is_meta_character)
        {
            return None;
        }
    } else if normalized_yes_branch.is_empty() {
        return None;
    }

    Some(ConditionalGroupExistsPattern {
        prefix,
        capture: LiteralCapture {
            body,
            name: capture_name,
        },
        middle,
        yes_branch: normalized_yes_branch,
        yes_branch_alternation,
        no_branch_alternation,
        nested_yes_branch,
        nested_no_branch,
        no_branch: normalized_no_branch,
    })
}

fn parse_quantified_conditional_group_exists_pattern_str(
    pattern: &str,
) -> Option<QuantifiedConditionalGroupExistsPattern<'_>> {
    let grouped_pattern = parse_conditional_group_exists_pattern_str(pattern.strip_suffix("{2}")?)?;
    let supports_plain_two_repeat = grouped_pattern.yes_branch_alternation.is_none()
        && grouped_pattern.no_branch_alternation.is_none();
    let supports_two_arm_alternation_repeat = grouped_pattern.yes_branch_alternation.is_some()
        && grouped_pattern.no_branch_alternation.is_some()
        && grouped_pattern.no_branch.is_some();
    if grouped_pattern.yes_branch.is_empty()
        || grouped_pattern.nested_yes_branch.is_some()
        || grouped_pattern.nested_no_branch.is_some()
        || (!supports_plain_two_repeat && !supports_two_arm_alternation_repeat)
    {
        return None;
    }

    Some(QuantifiedConditionalGroupExistsPattern {
        conditional: grouped_pattern,
    })
}

fn parse_quantified_conditional_group_exists_whole_pattern_str(
    pattern: &str,
) -> Option<QuantifiedConditionalGroupExistsWholePattern<'_>> {
    let inner = pattern.strip_prefix("(?:")?.strip_suffix("){2}")?;
    let grouped_pattern = parse_conditional_group_exists_pattern_str(inner)?;
    if !grouped_pattern.yes_branch.is_empty()
        || grouped_pattern.no_branch.is_none()
        || grouped_pattern.yes_branch_alternation.is_some()
        || grouped_pattern.no_branch_alternation.is_some()
        || grouped_pattern.nested_yes_branch.is_some()
        || grouped_pattern.nested_no_branch.is_some()
    {
        return None;
    }

    Some(QuantifiedConditionalGroupExistsWholePattern {
        conditional: grouped_pattern,
    })
}

fn parse_exact_repeat_group_pattern_str(pattern: &str) -> Option<ExactRepeatGroupPattern<'_>> {
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

    let suffix = remainder[close_offset + 1..].strip_prefix("{2}")?;
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(ExactRepeatGroupPattern {
        prefix,
        capture: LiteralCapture { body, name },
        suffix,
    })
}

fn parse_exact_repeat_group_alternation_pattern_str(
    pattern: &str,
) -> Option<ExactRepeatGroupAlternationPattern<'_>> {
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
    if branches.as_slice() != ["bc", "de"] {
        return None;
    }

    let suffix = remainder[close_offset + 1..].strip_prefix("{2}")?;
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(ExactRepeatGroupAlternationPattern {
        prefix,
        branches,
        capture_name,
        suffix,
    })
}

fn parse_ranged_repeat_group_pattern_str(pattern: &str) -> Option<RangedRepeatGroupPattern<'_>> {
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

    let (max_repeat, suffix) =
        if let Some(suffix) = remainder[close_offset + 1..].strip_prefix("{1,2}") {
            (2, suffix)
        } else if let Some(suffix) = remainder[close_offset + 1..].strip_prefix("{1,3}") {
            (3, suffix)
        } else {
            return None;
        };
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(RangedRepeatGroupPattern {
        prefix,
        capture: LiteralCapture { body, name },
        suffix,
        max_repeat,
    })
}

fn parse_wider_ranged_repeat_grouped_alternation_backtracking_heavy_pattern_str(
    pattern: &str,
) -> Option<WiderRangedRepeatGroupedAlternationBacktrackingHeavyPattern<'_>> {
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

    let inner_remainder = outer_body.strip_prefix('(')?;
    if inner_remainder.starts_with("?P<") {
        return None;
    }

    let inner_close_offset = inner_remainder.find(')')?;
    let inner_body = &inner_remainder[..inner_close_offset];
    let branches: Vec<&str> = inner_body.split('|').collect();
    if branches.as_slice() != ["bc", "b"] {
        return None;
    }

    let outer_suffix_and_remainder = &outer_body[inner_close_offset + 2..];
    let outer_close_offset = outer_suffix_and_remainder.find(')')?;
    let repeated_suffix = &outer_suffix_and_remainder[..outer_close_offset];
    if repeated_suffix != "c" {
        return None;
    }

    let (max_repeat, suffix) = if let Some(suffix) =
        outer_suffix_and_remainder[outer_close_offset + 1..].strip_prefix("{1,3}")
    {
        (3, suffix)
    } else {
        let suffix = outer_suffix_and_remainder[outer_close_offset + 1..].strip_prefix("{1,4}")?;
        (4, suffix)
    };
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(
        WiderRangedRepeatGroupedAlternationBacktrackingHeavyPattern {
            prefix,
            outer_name,
            branches,
            repeated_suffix,
            suffix,
            max_repeat,
        },
    )
}

fn parse_open_ended_quantified_group_alternation_backtracking_heavy_pattern_str(
    pattern: &str,
) -> Option<OpenEndedQuantifiedGroupAlternationBacktrackingHeavyPattern<'_>> {
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

    let inner_remainder = outer_body.strip_prefix('(')?;
    if inner_remainder.starts_with("?P<") {
        return None;
    }

    let inner_close_offset = inner_remainder.find(')')?;
    let inner_body = &inner_remainder[..inner_close_offset];
    let branches: Vec<&str> = inner_body.split('|').collect();
    if branches.as_slice() != ["bc", "b"] {
        return None;
    }

    let outer_suffix_and_remainder = &outer_body[inner_close_offset + 2..];
    let outer_close_offset = outer_suffix_and_remainder.find(')')?;
    let repeated_suffix = &outer_suffix_and_remainder[..outer_close_offset];
    if repeated_suffix != "c" {
        return None;
    }

    let (min_repeat, suffix) = if let Some(suffix) =
        outer_suffix_and_remainder[outer_close_offset + 1..].strip_prefix("{1,}")
    {
        (1, suffix)
    } else if let Some(suffix) =
        outer_suffix_and_remainder[outer_close_offset + 1..].strip_prefix("{2,}")
    {
        (2, suffix)
    } else {
        return None;
    };
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(
        OpenEndedQuantifiedGroupAlternationBacktrackingHeavyPattern {
            prefix,
            outer_name,
            branches,
            repeated_suffix,
            suffix,
            min_repeat,
        },
    )
}

fn parse_nested_open_ended_quantified_group_alternation_pattern_str(
    pattern: &str,
) -> Option<NestedOpenEndedQuantifiedGroupAlternationPattern<'_>> {
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

    let inner_remainder = outer_body.strip_prefix('(')?;
    if inner_remainder.starts_with("?P<") {
        return None;
    }

    let inner_close_offset = inner_remainder.find(')')?;
    let inner_body = &inner_remainder[..inner_close_offset];
    let branches: Vec<&str> = inner_body.split('|').collect();
    if branches.as_slice() != ["bc", "de"] {
        return None;
    }

    let outer_quantifier_and_remainder = &inner_remainder[inner_close_offset + 1..];
    let outer_close_offset = outer_quantifier_and_remainder.find(')')?;
    if &outer_quantifier_and_remainder[..outer_close_offset] != "{1,}" {
        return None;
    }

    let suffix = &outer_quantifier_and_remainder[outer_close_offset + 1..];
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(NestedOpenEndedQuantifiedGroupAlternationPattern {
        prefix,
        outer_name,
        branches,
        suffix,
        min_repeat: 1,
    })
}

fn parse_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_pattern_str(
    pattern: &str,
) -> Option<NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationPattern<'_>> {
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

    let inner_remainder = outer_body.strip_prefix('(')?;
    if inner_remainder.starts_with("?P<") {
        return None;
    }

    let inner_close_offset = inner_remainder.find(')')?;
    let inner_body = &inner_remainder[..inner_close_offset];
    let branches: Vec<&str> = inner_body.split('|').collect();
    if branches.as_slice() != ["bc", "de"] {
        return None;
    }

    let outer_quantifier_and_remainder = &inner_remainder[inner_close_offset + 1..];
    let outer_close_offset = outer_quantifier_and_remainder.find(')')?;
    if &outer_quantifier_and_remainder[..outer_close_offset] != "{1,4}" {
        return None;
    }

    let suffix = &outer_quantifier_and_remainder[outer_close_offset + 1..];
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(
        NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationPattern {
            prefix,
            outer_name,
            branches,
            suffix,
            min_repeat: 1,
            max_repeat: 4,
        },
    )
}

fn parse_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_pattern_str(
    pattern: &str,
) -> Option<NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationBacktrackingHeavyPattern<'_>>
{
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

    let repeated_remainder = outer_body.strip_prefix('(')?;
    if repeated_remainder.starts_with("?P<") {
        return None;
    }

    let inner_remainder = repeated_remainder.strip_prefix('(')?;
    if inner_remainder.starts_with("?P<") {
        return None;
    }

    let inner_close_offset = inner_remainder.find(')')?;
    let inner_body = &inner_remainder[..inner_close_offset];
    let branches: Vec<&str> = inner_body.split('|').collect();
    if branches.as_slice() != ["bc", "b"] {
        return None;
    }

    let after_inner = &inner_remainder[inner_close_offset + 1..];
    let repeated_suffix = "c";
    let outer_quantifier_and_remainder = after_inner.strip_prefix("c)")?;
    let outer_close_offset = outer_quantifier_and_remainder.find(')')?;
    if &outer_quantifier_and_remainder[..outer_close_offset] != "{1,4}" {
        return None;
    }

    let suffix = &outer_quantifier_and_remainder[outer_close_offset + 1..];
    if suffix.is_empty() || suffix.chars().any(is_meta_character) {
        return None;
    }

    Some(
        NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationBacktrackingHeavyPattern {
            prefix,
            outer_name,
            branches,
            repeated_suffix,
            suffix,
            max_repeat: 4,
        },
    )
}

fn parse_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_pattern_str(
    pattern: &str,
) -> Option<NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationConditionalPattern<'_>> {
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

    let inner_remainder = outer_body.strip_prefix('(')?;
    if inner_remainder.starts_with("?P<") {
        return None;
    }

    let repeated_remainder = inner_remainder.strip_prefix('(')?;
    if repeated_remainder.starts_with("?P<") {
        return None;
    }

    let inner_close_offset = repeated_remainder.find(')')?;
    let inner_body = &repeated_remainder[..inner_close_offset];
    let branches: Vec<&str> = inner_body.split('|').collect();
    if branches.as_slice() != ["bc", "de"] {
        return None;
    }

    let after_inner = repeated_remainder[inner_close_offset + 1..].strip_prefix("{1,4})d)?")?;
    let conditional = after_inner.strip_prefix("(?(")?.strip_suffix(')')?;
    let reference_end = conditional.find(')')?;
    let reference = &conditional[..reference_end];
    match outer_name {
        Some(name) if reference == name => {}
        None if reference == "1" => {}
        _ => return None,
    }

    let (yes_branch, no_branch) = split_first_top_level_pipe(&conditional[reference_end + 1..])?;
    if yes_branch.is_empty()
        || no_branch.is_empty()
        || yes_branch.chars().any(is_meta_character)
        || no_branch.chars().any(is_meta_character)
    {
        return None;
    }

    Some(
        NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationConditionalPattern {
            prefix,
            outer_name,
            branches,
            middle: "d",
            yes_branch,
            no_branch,
            min_repeat: 1,
            max_repeat: 4,
        },
    )
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
            } else if let Some(grouped_pattern) =
                parse_nested_alternation_literal_pattern_str(pattern_value)
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

                find_nested_alternation_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_quantified_nested_group_alternation_pattern_str(pattern_value)
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

                find_quantified_nested_group_alternation_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_quantified_nested_group_alternation_branch_local_numbered_backreference_pattern_str(
                    pattern_value,
                )
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

                find_quantified_nested_group_alternation_branch_local_backreference_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_quantified_nested_group_alternation_branch_local_named_backreference_pattern_str(
                    pattern_value,
                )
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

                find_quantified_nested_group_alternation_branch_local_backreference_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_nested_alternation_branch_local_numbered_backreference_pattern_str(
                    pattern_value,
                )
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

                find_nested_alternation_branch_local_backreference_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_nested_alternation_branch_local_named_backreference_pattern_str(
                    pattern_value,
                )
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

                find_nested_alternation_branch_local_backreference_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_branch_local_numbered_backreference_pattern_str(pattern_value)
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
                parse_branch_local_named_backreference_pattern_str(pattern_value)
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
                parse_quantified_branch_local_numbered_backreference_pattern_str(pattern_value)
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
                find_quantified_branch_local_backreference_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_quantified_branch_local_named_backreference_pattern_str(pattern_value)
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
                find_quantified_branch_local_backreference_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_conditional_branch_local_numbered_backreference_pattern_str(pattern_value)
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
                parse_conditional_branch_local_named_backreference_pattern_str(pattern_value)
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
            } else if let Some(grouped_pattern) = parse_optional_group_pattern_str(pattern_value) {
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

                find_optional_group_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_optional_group_alternation_pattern_str(pattern_value)
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

                find_optional_group_alternation_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_optional_group_alternation_branch_local_numbered_backreference_pattern_str(
                    pattern_value,
                )
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

                find_optional_group_alternation_branch_local_backreference_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_optional_group_alternation_branch_local_named_backreference_pattern_str(
                    pattern_value,
                )
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

                find_optional_group_alternation_branch_local_backreference_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_quantified_conditional_group_exists_whole_pattern_str(pattern_value)
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

                find_quantified_conditional_group_exists_whole_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_quantified_conditional_group_exists_pattern_str(pattern_value)
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

                find_quantified_conditional_group_exists_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_quantified_alternation_conditional_pattern_str(pattern_value)
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

                find_quantified_alternation_conditional_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_conditional_group_exists_pattern_str(pattern_value)
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

                find_conditional_group_exists_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_exact_repeat_group_alternation_pattern_str(pattern_value)
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

                find_exact_repeat_group_alternation_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_exact_repeat_group_pattern_str(pattern_value)
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
                parse_ranged_repeat_group_pattern_str(pattern_value)
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

                find_ranged_repeat_group_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_nested_open_ended_quantified_group_alternation_pattern_str(pattern_value)
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

                find_nested_open_ended_quantified_group_alternation_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_pattern_str(
                    pattern_value,
                )
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

                find_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_pattern_str(
                    pattern_value,
                )
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

                find_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_pattern_str(
                    pattern_value,
                )
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

                find_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_open_ended_quantified_group_alternation_backtracking_heavy_pattern_str(
                    pattern_value,
                )
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

                find_open_ended_quantified_group_alternation_backtracking_heavy_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_wider_ranged_repeat_grouped_alternation_backtracking_heavy_pattern_str(
                    pattern_value,
                )
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

                find_wider_ranged_repeat_grouped_alternation_backtracking_heavy_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_quantified_alternation_nested_branch_pattern_str(pattern_value)
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

                find_quantified_alternation_nested_branch_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_quantified_alternation_backtracking_heavy_pattern_str(pattern_value)
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

                find_quantified_alternation_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_quantified_alternation_pattern_str(pattern_value)
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

                find_quantified_alternation_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_quantified_alternation_branch_local_numbered_backreference_pattern_str(
                    pattern_value,
                )
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

                find_quantified_alternation_branch_local_backreference_match_span_str(
                    &grouped_pattern,
                    flags,
                    mode,
                    &string_chars,
                    normalized_pos,
                    normalized_endpos,
                )
                .map_or((None, Vec::new()), |(span, group_spans)| {
                    (Some(span), group_spans)
                })
            } else if let Some(grouped_pattern) =
                parse_quantified_alternation_branch_local_named_backreference_pattern_str(
                    pattern_value,
                )
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

                find_quantified_alternation_branch_local_backreference_match_span_str(
                    &grouped_pattern,
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
            PatternRef::Str(pattern_value) => parse_nested_capture_literal_pattern_str(
                pattern_value,
            )
            .map(|grouped_pattern| grouped_pattern.lastindex())
            .or_else(|| {
                parse_nested_alternation_literal_pattern_str(pattern_value)
                    .map(|grouped_pattern| grouped_pattern.lastindex())
            })
            .or_else(|| {
                parse_quantified_nested_group_alternation_pattern_str(pattern_value)
                    .and_then(|grouped_pattern| grouped_pattern.matched_lastindex(&group_spans))
            })
            .or_else(|| {
                parse_quantified_nested_group_alternation_branch_local_numbered_backreference_pattern_str(
                    pattern_value,
                )
                .and_then(|grouped_pattern| grouped_pattern.matched_lastindex(&group_spans))
            })
            .or_else(|| {
                parse_quantified_nested_group_alternation_branch_local_named_backreference_pattern_str(
                    pattern_value,
                )
                .and_then(|grouped_pattern| grouped_pattern.matched_lastindex(&group_spans))
            })
            .or_else(|| {
                parse_nested_alternation_branch_local_numbered_backreference_pattern_str(
                    pattern_value,
                )
                .map(|grouped_pattern| grouped_pattern.lastindex())
            })
            .or_else(|| {
                parse_nested_alternation_branch_local_named_backreference_pattern_str(
                    pattern_value,
                )
                .map(|grouped_pattern| grouped_pattern.lastindex())
            })
            .or_else(|| {
                parse_branch_local_numbered_backreference_pattern_str(pattern_value)
                    .map(|grouped_pattern| grouped_pattern.lastindex())
            })
            .or_else(|| {
                parse_branch_local_named_backreference_pattern_str(pattern_value)
                    .map(|grouped_pattern| grouped_pattern.lastindex())
            })
            .or_else(|| {
                parse_quantified_branch_local_numbered_backreference_pattern_str(pattern_value)
                    .map(|grouped_pattern| grouped_pattern.lastindex())
            })
            .or_else(|| {
                parse_quantified_branch_local_named_backreference_pattern_str(pattern_value)
                    .map(|grouped_pattern| grouped_pattern.lastindex())
            })
            .or_else(|| {
                parse_conditional_branch_local_numbered_backreference_pattern_str(pattern_value)
                    .map(|grouped_pattern| grouped_pattern.lastindex())
            })
            .or_else(|| {
                parse_conditional_branch_local_named_backreference_pattern_str(pattern_value)
                    .map(|grouped_pattern| grouped_pattern.lastindex())
            })
            .or_else(|| {
                parse_quantified_alternation_nested_branch_pattern_str(pattern_value)
                    .and_then(|grouped_pattern| grouped_pattern.matched_lastindex(&group_spans))
            })
            .or_else(|| {
                parse_quantified_alternation_conditional_pattern_str(pattern_value)
                    .and_then(|grouped_pattern| grouped_pattern.matched_lastindex(&group_spans))
            })
            .or_else(|| {
                parse_nested_open_ended_quantified_group_alternation_pattern_str(pattern_value)
                    .and_then(|grouped_pattern| grouped_pattern.matched_lastindex(&group_spans))
            })
            .or_else(|| {
                parse_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_pattern_str(
                    pattern_value,
                )
                .and_then(|grouped_pattern| grouped_pattern.matched_lastindex(&group_spans))
            })
            .or_else(|| {
                parse_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_pattern_str(
                    pattern_value,
                )
                .and_then(|grouped_pattern| grouped_pattern.matched_lastindex(&group_spans))
            })
            .or_else(|| {
                parse_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_pattern_str(
                    pattern_value,
                )
                .and_then(|grouped_pattern| grouped_pattern.matched_lastindex(&group_spans))
            })
            .or_else(|| {
                parse_open_ended_quantified_group_alternation_backtracking_heavy_pattern_str(
                    pattern_value,
                )
                .and_then(|grouped_pattern| grouped_pattern.matched_lastindex(&group_spans))
            })
            .or_else(|| {
                parse_wider_ranged_repeat_grouped_alternation_backtracking_heavy_pattern_str(
                    pattern_value,
                )
                .and_then(|grouped_pattern| grouped_pattern.matched_lastindex(&group_spans))
            })
            .or_else(|| {
                parse_optional_group_alternation_branch_local_numbered_backreference_pattern_str(
                    pattern_value,
                )
                .and_then(|grouped_pattern| grouped_pattern.matched_lastindex(&group_spans))
            })
            .or_else(|| {
                parse_optional_group_alternation_branch_local_named_backreference_pattern_str(
                    pattern_value,
                )
                .and_then(|grouped_pattern| grouped_pattern.matched_lastindex(&group_spans))
            })
            .or_else(|| {
                parse_quantified_alternation_branch_local_numbered_backreference_pattern_str(
                    pattern_value,
                )
                .map(|grouped_pattern| grouped_pattern.lastindex())
            })
            .or_else(|| {
                parse_quantified_alternation_branch_local_named_backreference_pattern_str(
                    pattern_value,
                )
                .map(|grouped_pattern| grouped_pattern.lastindex())
            })
            .or_else(|| lastindex_from_group_spans(&group_spans)),
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

/// Discover repeated spans for the bounded nested-group replacement slice
/// while preserving capture spans for template expansion.
#[must_use]
pub fn nested_capture_find_spans_str(
    pattern: &str,
    flags: i32,
    string: &str,
    pos: isize,
    endpos: Option<isize>,
) -> CapturedFindSpansOutcome {
    let string_chars: Vec<char> = string.chars().collect();
    let (normalized_pos, normalized_endpos) = normalize_bounds(string_chars.len(), pos, endpos);
    let Some(grouped_pattern) = parse_nested_capture_literal_pattern_str(pattern) else {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    };
    if flags != FLAG_UNICODE {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    }

    let pattern_chars = grouped_pattern.pattern_chars();
    let mut matches = Vec::new();
    let mut next_start = normalized_pos;
    while let Some((start, end)) = find_match_span_str(
        pattern_chars.as_slice(),
        flags,
        MatchMode::Search,
        &string_chars,
        next_start,
        normalized_endpos,
    ) {
        matches.push(CapturedMatchSpan {
            span: (start, end),
            group_spans: grouped_pattern.group_spans(start),
        });
        next_start = end;
    }

    CapturedFindSpansOutcome {
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

fn find_quantified_nested_capture_match_span_str(
    pattern: &QuantifiedNestedCaptureLiteralPattern<'_>,
    prefix_chars: &[char],
    inner_chars: &[char],
    suffix_chars: &[char],
    flags: i32,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    let inner_len = inner_chars.len();
    for start in pos..=endpos {
        if !literal_matches_at_str(prefix_chars, flags, string, start, endpos) {
            continue;
        }

        let outer_start = start + prefix_chars.len();
        let mut repeat_count = 0;
        let mut next_inner_start = outer_start;
        while literal_matches_at_str(inner_chars, flags, string, next_inner_start, endpos) {
            repeat_count += 1;
            next_inner_start += inner_len;
        }

        while repeat_count > 0 {
            let outer_end = outer_start + inner_len * repeat_count;
            if literal_matches_at_str(suffix_chars, flags, string, outer_end, endpos) {
                let match_end = outer_end + suffix_chars.len();
                return Some(((start, match_end), pattern.group_spans(start, repeat_count)));
            }
            repeat_count -= 1;
        }
    }

    None
}

/// Discover repeated spans for the bounded quantified nested-group
/// replacement slice while preserving capture spans for template expansion.
#[must_use]
pub fn quantified_nested_capture_find_spans_str(
    pattern: &str,
    flags: i32,
    string: &str,
    pos: isize,
    endpos: Option<isize>,
) -> CapturedFindSpansOutcome {
    let string_chars: Vec<char> = string.chars().collect();
    let (normalized_pos, normalized_endpos) = normalize_bounds(string_chars.len(), pos, endpos);
    let Some(grouped_pattern) = parse_quantified_nested_capture_literal_pattern_str(pattern) else {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    };
    if flags != FLAG_UNICODE {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    }

    let prefix_chars: Vec<char> = grouped_pattern.prefix.chars().collect();
    let inner_chars: Vec<char> = grouped_pattern.inner_capture.body.chars().collect();
    let suffix_chars: Vec<char> = grouped_pattern.suffix.chars().collect();
    let mut matches = Vec::new();
    let mut next_start = normalized_pos;
    while let Some((span, group_spans)) = find_quantified_nested_capture_match_span_str(
        &grouped_pattern,
        prefix_chars.as_slice(),
        inner_chars.as_slice(),
        suffix_chars.as_slice(),
        flags,
        &string_chars,
        next_start,
        normalized_endpos,
    ) {
        matches.push(CapturedMatchSpan { span, group_spans });
        next_start = span.1;
    }

    CapturedFindSpansOutcome {
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

/// Discover repeated spans for the bounded two-arm conditional replacement
/// slice while preserving capture spans for result marshalling.
#[must_use]
pub fn conditional_group_exists_find_spans_str(
    pattern: &str,
    flags: i32,
    string: &str,
    pos: isize,
    endpos: Option<isize>,
) -> CapturedFindSpansOutcome {
    let string_chars: Vec<char> = string.chars().collect();
    let (normalized_pos, normalized_endpos) = normalize_bounds(string_chars.len(), pos, endpos);
    let Some(grouped_pattern) = parse_conditional_group_exists_pattern_str(pattern) else {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    };
    if flags != FLAG_UNICODE
        || grouped_pattern.yes_branch.is_empty()
        || grouped_pattern.no_branch.is_none_or(str::is_empty)
        || grouped_pattern.yes_branch_alternation.is_some()
        || grouped_pattern.no_branch_alternation.is_some()
        || grouped_pattern.nested_yes_branch.is_some()
        || grouped_pattern.nested_no_branch.is_some()
    {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    }

    let mut matches = Vec::new();
    let mut next_start = normalized_pos;
    while let Some((match_start, capture_present, match_end, matched_yes_branch)) =
        (next_start..=normalized_endpos).find_map(|candidate_start| {
            conditional_group_exists_matches_at_str(
                &grouped_pattern,
                flags,
                &string_chars,
                candidate_start,
                normalized_endpos,
            )
            .map(|(capture_present, match_end, matched_yes_branch)| {
                (
                    candidate_start,
                    capture_present,
                    match_end,
                    matched_yes_branch,
                )
            })
        })
    {
        matches.push(CapturedMatchSpan {
            span: (match_start, match_end),
            group_spans: grouped_pattern.group_spans(
                match_start,
                capture_present,
                matched_yes_branch,
            ),
        });
        next_start = match_end;
    }

    CapturedFindSpansOutcome {
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

/// Discover repeated spans for the bounded nested two-arm conditional
/// replacement slice while preserving capture spans for result marshalling.
#[must_use]
pub fn conditional_group_exists_nested_find_spans_str(
    pattern: &str,
    flags: i32,
    string: &str,
    pos: isize,
    endpos: Option<isize>,
) -> CapturedFindSpansOutcome {
    let string_chars: Vec<char> = string.chars().collect();
    let (normalized_pos, normalized_endpos) = normalize_bounds(string_chars.len(), pos, endpos);
    let Some(grouped_pattern) = parse_conditional_group_exists_pattern_str(pattern) else {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    };
    if flags != FLAG_UNICODE
        || grouped_pattern.yes_branch.is_empty()
        || grouped_pattern.no_branch.is_none_or(str::is_empty)
        || grouped_pattern.yes_branch_alternation.is_some()
        || grouped_pattern.no_branch_alternation.is_some()
        || grouped_pattern.nested_yes_branch.is_none()
        || grouped_pattern.nested_no_branch.is_some()
    {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    }

    let mut matches = Vec::new();
    let mut next_start = normalized_pos;
    while let Some((match_start, capture_present, match_end, matched_yes_branch)) =
        (next_start..=normalized_endpos).find_map(|candidate_start| {
            conditional_group_exists_matches_at_str(
                &grouped_pattern,
                flags,
                &string_chars,
                candidate_start,
                normalized_endpos,
            )
            .map(|(capture_present, match_end, matched_yes_branch)| {
                (
                    candidate_start,
                    capture_present,
                    match_end,
                    matched_yes_branch,
                )
            })
        })
    {
        matches.push(CapturedMatchSpan {
            span: (match_start, match_end),
            group_spans: grouped_pattern.group_spans(
                match_start,
                capture_present,
                matched_yes_branch,
            ),
        });
        next_start = match_end;
    }

    CapturedFindSpansOutcome {
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

/// Discover repeated spans for the bounded alternation-heavy two-arm
/// conditional replacement slice while preserving capture spans for result
/// marshalling.
#[must_use]
pub fn conditional_group_exists_alternation_find_spans_str(
    pattern: &str,
    flags: i32,
    string: &str,
    pos: isize,
    endpos: Option<isize>,
) -> CapturedFindSpansOutcome {
    let string_chars: Vec<char> = string.chars().collect();
    let (normalized_pos, normalized_endpos) = normalize_bounds(string_chars.len(), pos, endpos);
    let Some(grouped_pattern) = parse_conditional_group_exists_pattern_str(pattern) else {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    };
    if flags != FLAG_UNICODE
        || grouped_pattern.yes_branch_alternation.is_none()
        || grouped_pattern.no_branch_alternation.is_none()
        || grouped_pattern.nested_yes_branch.is_some()
        || grouped_pattern.nested_no_branch.is_some()
    {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    }

    let mut matches = Vec::new();
    let mut next_start = normalized_pos;
    while let Some((match_start, capture_present, match_end, matched_branch)) =
        (next_start..=normalized_endpos).find_map(|candidate_start| {
            conditional_group_exists_matches_at_str(
                &grouped_pattern,
                flags,
                &string_chars,
                candidate_start,
                normalized_endpos,
            )
            .map(|(capture_present, match_end, matched_branch)| {
                (candidate_start, capture_present, match_end, matched_branch)
            })
        })
    {
        matches.push(CapturedMatchSpan {
            span: (match_start, match_end),
            group_spans: grouped_pattern.group_spans(match_start, capture_present, matched_branch),
        });
        next_start = match_end;
    }

    CapturedFindSpansOutcome {
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

/// Discover repeated spans for the bounded quantified two-arm conditional
/// replacement slice while preserving capture spans for result marshalling.
#[must_use]
pub fn conditional_group_exists_quantified_find_spans_str(
    pattern: &str,
    flags: i32,
    string: &str,
    pos: isize,
    endpos: Option<isize>,
) -> CapturedFindSpansOutcome {
    let string_chars: Vec<char> = string.chars().collect();
    let (normalized_pos, normalized_endpos) = normalize_bounds(string_chars.len(), pos, endpos);
    let Some(grouped_pattern) = parse_quantified_conditional_group_exists_pattern_str(pattern)
    else {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    };
    if flags != FLAG_UNICODE
        || grouped_pattern.conditional.yes_branch.is_empty()
        || grouped_pattern
            .conditional
            .no_branch
            .is_none_or(str::is_empty)
        || grouped_pattern.conditional.yes_branch_alternation.is_some()
        || grouped_pattern.conditional.no_branch_alternation.is_some()
        || grouped_pattern.conditional.nested_yes_branch.is_some()
        || grouped_pattern.conditional.nested_no_branch.is_some()
    {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    }

    let mut matches = Vec::new();
    let mut next_start = normalized_pos;
    while let Some((match_start, capture_present, match_end, repeated_alternation_branches)) =
        (next_start..=normalized_endpos).find_map(|candidate_start| {
            quantified_conditional_group_exists_matches_at_str(
                &grouped_pattern,
                flags,
                &string_chars,
                candidate_start,
                normalized_endpos,
            )
            .map(
                |(capture_present, match_end, repeated_alternation_branches)| {
                    (
                        candidate_start,
                        capture_present,
                        match_end,
                        repeated_alternation_branches,
                    )
                },
            )
        })
    {
        matches.push(CapturedMatchSpan {
            span: (match_start, match_end),
            group_spans: grouped_pattern.group_spans(
                match_start,
                capture_present,
                repeated_alternation_branches,
            ),
        });
        next_start = match_end;
    }

    CapturedFindSpansOutcome {
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

/// Discover repeated spans for the bounded omitted-no-arm conditional
/// replacement slice while preserving capture spans for result marshalling.
#[must_use]
pub fn conditional_group_exists_no_else_find_spans_str(
    pattern: &str,
    flags: i32,
    string: &str,
    pos: isize,
    endpos: Option<isize>,
) -> CapturedFindSpansOutcome {
    let string_chars: Vec<char> = string.chars().collect();
    let (normalized_pos, normalized_endpos) = normalize_bounds(string_chars.len(), pos, endpos);
    let Some(grouped_pattern) = parse_conditional_group_exists_pattern_str(pattern) else {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    };
    if flags != FLAG_UNICODE
        || grouped_pattern.no_branch.is_some()
        || grouped_pattern.yes_branch_alternation.is_some()
        || grouped_pattern.no_branch_alternation.is_some()
        || grouped_pattern.nested_yes_branch.is_some()
        || grouped_pattern.nested_no_branch.is_some()
    {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    }

    let mut matches = Vec::new();
    let mut next_start = normalized_pos;
    while let Some((match_start, capture_present, match_end, matched_yes_branch)) =
        (next_start..=normalized_endpos).find_map(|candidate_start| {
            conditional_group_exists_matches_at_str(
                &grouped_pattern,
                flags,
                &string_chars,
                candidate_start,
                normalized_endpos,
            )
            .map(|(capture_present, match_end, matched_yes_branch)| {
                (
                    candidate_start,
                    capture_present,
                    match_end,
                    matched_yes_branch,
                )
            })
        })
    {
        matches.push(CapturedMatchSpan {
            span: (match_start, match_end),
            group_spans: grouped_pattern.group_spans(
                match_start,
                capture_present,
                matched_yes_branch,
            ),
        });
        next_start = match_end;
    }

    CapturedFindSpansOutcome {
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

/// Discover repeated spans for the bounded explicit-empty-else conditional
/// replacement slice while preserving capture spans for result marshalling.
#[must_use]
pub fn conditional_group_exists_empty_else_find_spans_str(
    pattern: &str,
    flags: i32,
    string: &str,
    pos: isize,
    endpos: Option<isize>,
) -> CapturedFindSpansOutcome {
    let string_chars: Vec<char> = string.chars().collect();
    let (normalized_pos, normalized_endpos) = normalize_bounds(string_chars.len(), pos, endpos);
    let Some(grouped_pattern) = parse_conditional_group_exists_pattern_str(pattern) else {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    };
    if flags != FLAG_UNICODE
        || grouped_pattern.no_branch != Some("")
        || grouped_pattern.yes_branch_alternation.is_some()
        || grouped_pattern.no_branch_alternation.is_some()
        || grouped_pattern.nested_no_branch.is_some()
    {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    }

    let mut matches = Vec::new();
    let mut next_start = normalized_pos;
    while let Some((match_start, capture_present, match_end, matched_yes_branch)) =
        (next_start..=normalized_endpos).find_map(|candidate_start| {
            conditional_group_exists_matches_at_str(
                &grouped_pattern,
                flags,
                &string_chars,
                candidate_start,
                normalized_endpos,
            )
            .map(|(capture_present, match_end, matched_yes_branch)| {
                (
                    candidate_start,
                    capture_present,
                    match_end,
                    matched_yes_branch,
                )
            })
        })
    {
        matches.push(CapturedMatchSpan {
            span: (match_start, match_end),
            group_spans: grouped_pattern.group_spans(
                match_start,
                capture_present,
                matched_yes_branch,
            ),
        });
        next_start = match_end;
    }

    CapturedFindSpansOutcome {
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

/// Discover repeated spans for the bounded empty-yes-arm conditional
/// replacement slice while preserving capture spans for result marshalling.
#[must_use]
pub fn conditional_group_exists_empty_yes_else_find_spans_str(
    pattern: &str,
    flags: i32,
    string: &str,
    pos: isize,
    endpos: Option<isize>,
) -> CapturedFindSpansOutcome {
    let string_chars: Vec<char> = string.chars().collect();
    let (normalized_pos, normalized_endpos) = normalize_bounds(string_chars.len(), pos, endpos);
    let Some(grouped_pattern) = parse_conditional_group_exists_pattern_str(pattern) else {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    };
    if flags != FLAG_UNICODE
        || !grouped_pattern.yes_branch.is_empty()
        || grouped_pattern.no_branch.is_none_or(str::is_empty)
        || grouped_pattern.yes_branch_alternation.is_some()
        || grouped_pattern.no_branch_alternation.is_some()
        || grouped_pattern.nested_no_branch.is_some()
    {
        return CapturedFindSpansOutcome {
            status: MatchStatus::Unsupported,
            pos: normalized_pos,
            endpos: normalized_endpos,
            matches: Vec::new(),
        };
    }

    let mut matches = Vec::new();
    let mut next_start = normalized_pos;
    while let Some((match_start, capture_present, match_end, matched_yes_branch)) =
        (next_start..=normalized_endpos).find_map(|candidate_start| {
            conditional_group_exists_matches_at_str(
                &grouped_pattern,
                flags,
                &string_chars,
                candidate_start,
                normalized_endpos,
            )
            .map(|(capture_present, match_end, matched_yes_branch)| {
                (
                    candidate_start,
                    capture_present,
                    match_end,
                    matched_yes_branch,
                )
            })
        })
    {
        matches.push(CapturedMatchSpan {
            span: (match_start, match_end),
            group_spans: grouped_pattern.group_spans(
                match_start,
                capture_present,
                matched_yes_branch,
            ),
        });
        next_start = match_end;
    }

    CapturedFindSpansOutcome {
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

fn optional_group_matches_at_str(
    pattern: &OptionalGroupPattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<(bool, usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let capture_chars: Vec<char> = pattern.capture.body.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let capture_start = start + prefix_chars.len();
    let capture_end = capture_start + capture_chars.len();

    if literal_matches_at_str(
        capture_chars.as_slice(),
        flags,
        string,
        capture_start,
        endpos,
    ) && literal_matches_at_str(suffix_chars.as_slice(), flags, string, capture_end, endpos)
    {
        return Some((true, capture_end + suffix_chars.len()));
    }

    literal_matches_at_str(
        suffix_chars.as_slice(),
        flags,
        string,
        capture_start,
        endpos,
    )
    .then_some((false, capture_start + suffix_chars.len()))
}

fn find_optional_group_match_span_str(
    pattern: &OptionalGroupPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            optional_group_matches_at_str(pattern, flags, string, start, endpos).map(
                |(capture_present, match_end)| {
                    (
                        (start, match_end),
                        pattern.group_spans(start, capture_present),
                    )
                },
            )
        }),
        MatchMode::Match => optional_group_matches_at_str(pattern, flags, string, pos, endpos).map(
            |(capture_present, match_end)| {
                ((pos, match_end), pattern.group_spans(pos, capture_present))
            },
        ),
        MatchMode::Fullmatch => optional_group_matches_at_str(pattern, flags, string, pos, endpos)
            .and_then(|(capture_present, match_end)| {
                (match_end == endpos)
                    .then_some(((pos, match_end), pattern.group_spans(pos, capture_present)))
            }),
    }
}

fn optional_group_alternation_matches_at_str<'a>(
    pattern: &'a OptionalGroupAlternationPattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<(Option<&'a str>, usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let capture_start = start + prefix_chars.len();
    for branch in &pattern.branches {
        let branch_chars: Vec<char> = branch.chars().collect();
        let capture_end = capture_start + branch_chars.len();
        if literal_matches_at_str(
            branch_chars.as_slice(),
            flags,
            string,
            capture_start,
            endpos,
        ) && literal_matches_at_str(suffix_chars.as_slice(), flags, string, capture_end, endpos)
        {
            return Some((Some(*branch), capture_end + suffix_chars.len()));
        }
    }

    literal_matches_at_str(
        suffix_chars.as_slice(),
        flags,
        string,
        capture_start,
        endpos,
    )
    .then_some((None, capture_start + suffix_chars.len()))
}

fn find_optional_group_alternation_match_span_str(
    pattern: &OptionalGroupAlternationPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            optional_group_alternation_matches_at_str(pattern, flags, string, start, endpos).map(
                |(matched_branch, match_end)| {
                    (
                        (start, match_end),
                        pattern.group_spans(start, matched_branch),
                    )
                },
            )
        }),
        MatchMode::Match => optional_group_alternation_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .map(|(matched_branch, match_end)| {
            ((pos, match_end), pattern.group_spans(pos, matched_branch))
        }),
        MatchMode::Fullmatch => optional_group_alternation_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .and_then(|(matched_branch, match_end)| {
            (match_end == endpos)
                .then_some(((pos, match_end), pattern.group_spans(pos, matched_branch)))
        }),
    }
}

fn optional_group_alternation_branch_local_backreference_matches_at_str<'a>(
    pattern: &'a OptionalGroupAlternationBranchLocalBackreferencePattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<(Option<&'a str>, usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let outer_start = start + prefix_chars.len();
    for branch in &pattern.branches {
        let branch_chars: Vec<char> = branch.chars().collect();
        let inner_end = outer_start + branch_chars.len();
        let outer_end = inner_end + branch_chars.len();

        if literal_matches_at_str(branch_chars.as_slice(), flags, string, outer_start, endpos)
            && literal_matches_at_str(branch_chars.as_slice(), flags, string, inner_end, endpos)
            && literal_matches_at_str(suffix_chars.as_slice(), flags, string, outer_end, endpos)
        {
            return Some((Some(*branch), outer_end + suffix_chars.len()));
        }
    }

    literal_matches_at_str(suffix_chars.as_slice(), flags, string, outer_start, endpos)
        .then_some((None, outer_start + suffix_chars.len()))
}

fn find_optional_group_alternation_branch_local_backreference_match_span_str(
    pattern: &OptionalGroupAlternationBranchLocalBackreferencePattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            optional_group_alternation_branch_local_backreference_matches_at_str(
                pattern, flags, string, start, endpos,
            )
            .map(|(matched_branch, match_end)| {
                (
                    (start, match_end),
                    pattern.group_spans(start, matched_branch),
                )
            })
        }),
        MatchMode::Match => optional_group_alternation_branch_local_backreference_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .map(|(matched_branch, match_end)| {
            ((pos, match_end), pattern.group_spans(pos, matched_branch))
        }),
        MatchMode::Fullmatch => {
            optional_group_alternation_branch_local_backreference_matches_at_str(
                pattern, flags, string, pos, endpos,
            )
            .and_then(|(matched_branch, match_end)| {
                (match_end == endpos)
                    .then_some(((pos, match_end), pattern.group_spans(pos, matched_branch)))
            })
        }
    }
}

fn conditional_group_exists_matches_at_str<'a>(
    pattern: &ConditionalGroupExistsPattern<'a>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<(bool, usize, Option<&'a str>)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let capture_chars: Vec<char> = pattern.capture.body.chars().collect();
    let middle_chars: Vec<char> = pattern.middle.chars().collect();
    let no_branch_chars = pattern
        .no_branch
        .map(|branch| branch.chars().collect::<Vec<char>>());

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let capture_start = start + prefix_chars.len();
    let (capture_present, middle_start) = if literal_matches_at_str(
        capture_chars.as_slice(),
        flags,
        string,
        capture_start,
        endpos,
    ) {
        (true, capture_start + capture_chars.len())
    } else {
        (false, capture_start)
    };

    if !literal_matches_at_str(middle_chars.as_slice(), flags, string, middle_start, endpos) {
        return None;
    }

    let branch_start = middle_start + middle_chars.len();
    if capture_present {
        if let Some(yes_branch_alternation) = &pattern.yes_branch_alternation {
            for branch in yes_branch_alternation {
                let branch_chars: Vec<char> = branch.chars().collect();
                if literal_matches_at_str(
                    branch_chars.as_slice(),
                    flags,
                    string,
                    branch_start,
                    endpos,
                ) {
                    return Some((true, branch_start + branch_chars.len(), Some(branch)));
                }
            }
            return None;
        }

        let yes_branch_chars: Vec<char> = pattern.yes_branch.chars().collect();
        return literal_matches_at_str(
            yes_branch_chars.as_slice(),
            flags,
            string,
            branch_start,
            endpos,
        )
        .then_some((true, branch_start + yes_branch_chars.len(), None));
    }

    if let Some(no_branch_alternation) = &pattern.no_branch_alternation {
        for branch in no_branch_alternation {
            let branch_chars: Vec<char> = branch.chars().collect();
            if literal_matches_at_str(branch_chars.as_slice(), flags, string, branch_start, endpos)
            {
                return Some((false, branch_start + branch_chars.len(), Some(branch)));
            }
        }
        return None;
    }

    if let Some(nested_no_branch) = &pattern.nested_no_branch {
        let selected_branch_chars: Vec<char> = nested_no_branch.no_branch.chars().collect();
        return literal_matches_at_str(
            selected_branch_chars.as_slice(),
            flags,
            string,
            branch_start,
            endpos,
        )
        .then_some((false, branch_start + selected_branch_chars.len(), None));
    }

    let selected_branch = no_branch_chars.as_deref().unwrap_or(&[]);
    literal_matches_at_str(selected_branch, flags, string, branch_start, endpos).then_some((
        false,
        branch_start + selected_branch.len(),
        None,
    ))
}

fn find_conditional_group_exists_match_span_str(
    pattern: &ConditionalGroupExistsPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            conditional_group_exists_matches_at_str(pattern, flags, string, start, endpos).map(
                |(capture_present, match_end, matched_yes_branch)| {
                    (
                        (start, match_end),
                        pattern.group_spans(start, capture_present, matched_yes_branch),
                    )
                },
            )
        }),
        MatchMode::Match => conditional_group_exists_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .map(|(capture_present, match_end, matched_yes_branch)| {
            (
                (pos, match_end),
                pattern.group_spans(pos, capture_present, matched_yes_branch),
            )
        }),
        MatchMode::Fullmatch => conditional_group_exists_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .and_then(|(capture_present, match_end, matched_yes_branch)| {
            (match_end == endpos).then_some((
                (pos, match_end),
                pattern.group_spans(pos, capture_present, matched_yes_branch),
            ))
        }),
    }
}

fn quantified_conditional_group_exists_matches_at_str<'a>(
    pattern: &'a QuantifiedConditionalGroupExistsPattern<'a>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<(bool, usize, Option<(&'a str, &'a str)>)> {
    let conditional = &pattern.conditional;
    let prefix_chars: Vec<char> = conditional.prefix.chars().collect();
    let capture_chars: Vec<char> = conditional.capture.body.chars().collect();
    let middle_chars: Vec<char> = conditional.middle.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let capture_start = start + prefix_chars.len();
    let (capture_present, middle_start) = if literal_matches_at_str(
        capture_chars.as_slice(),
        flags,
        string,
        capture_start,
        endpos,
    ) {
        (true, capture_start + capture_chars.len())
    } else {
        (false, capture_start)
    };

    if !literal_matches_at_str(middle_chars.as_slice(), flags, string, middle_start, endpos) {
        return None;
    }

    let branch_chars: Vec<char> = if capture_present {
        conditional.yes_branch.chars().collect()
    } else {
        conditional.no_branch.unwrap_or("").chars().collect()
    };

    let first_branch_start = middle_start + middle_chars.len();
    if capture_present {
        if let Some(branches) = &conditional.yes_branch_alternation {
            return match_repeated_conditional_alternation_branches_at_str(
                branches.as_slice(),
                flags,
                string,
                first_branch_start,
                endpos,
            )
            .map(|(first_branch, last_branch, match_end)| {
                (true, match_end, Some((first_branch, last_branch)))
            });
        }
    } else if let Some(branches) = &conditional.no_branch_alternation {
        return match_repeated_conditional_alternation_branches_at_str(
            branches.as_slice(),
            flags,
            string,
            first_branch_start,
            endpos,
        )
        .map(|(first_branch, last_branch, match_end)| {
            (false, match_end, Some((first_branch, last_branch)))
        });
    }

    if !literal_matches_at_str(
        branch_chars.as_slice(),
        flags,
        string,
        first_branch_start,
        endpos,
    ) {
        return None;
    }

    let second_branch_start = first_branch_start + branch_chars.len();
    literal_matches_at_str(
        branch_chars.as_slice(),
        flags,
        string,
        second_branch_start,
        endpos,
    )
    .then_some((
        capture_present,
        second_branch_start + branch_chars.len(),
        None,
    ))
}

fn match_repeated_conditional_alternation_branches_at_str<'a>(
    branches: &[&'a str],
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<(&'a str, &'a str, usize)> {
    for first_branch in branches {
        let first_branch_chars: Vec<char> = first_branch.chars().collect();
        if !literal_matches_at_str(first_branch_chars.as_slice(), flags, string, start, endpos) {
            continue;
        }

        let second_start = start + first_branch_chars.len();
        for second_branch in branches {
            let second_branch_chars: Vec<char> = second_branch.chars().collect();
            if literal_matches_at_str(
                second_branch_chars.as_slice(),
                flags,
                string,
                second_start,
                endpos,
            ) {
                return Some((
                    *first_branch,
                    *second_branch,
                    second_start + second_branch_chars.len(),
                ));
            }
        }
    }

    None
}

fn quantified_conditional_group_exists_whole_matches_at_str(
    pattern: &QuantifiedConditionalGroupExistsWholePattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<(Option<(usize, usize)>, usize)> {
    let conditional = &pattern.conditional;
    let prefix_chars: Vec<char> = conditional.prefix.chars().collect();
    let capture_chars: Vec<char> = conditional.capture.body.chars().collect();
    let middle_chars: Vec<char> = conditional.middle.chars().collect();
    let no_branch_chars: Vec<char> = conditional
        .no_branch
        .expect("quantified whole conditional group-exists pattern must have a no-branch")
        .chars()
        .collect();
    let mut cursor = start;
    let mut capture_span = None;

    for _ in 0..2 {
        if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, cursor, endpos) {
            return None;
        }

        let capture_start = cursor + prefix_chars.len();
        let capture_end = capture_start + capture_chars.len();
        let middle_start = if literal_matches_at_str(
            capture_chars.as_slice(),
            flags,
            string,
            capture_start,
            endpos,
        ) {
            capture_span = Some((capture_start, capture_end));
            capture_end
        } else {
            capture_start
        };

        if !literal_matches_at_str(middle_chars.as_slice(), flags, string, middle_start, endpos) {
            return None;
        }

        let branch_start = middle_start + middle_chars.len();
        if capture_span.is_none()
            && !literal_matches_at_str(
                no_branch_chars.as_slice(),
                flags,
                string,
                branch_start,
                endpos,
            )
        {
            return None;
        }

        cursor = if capture_span.is_some() {
            branch_start
        } else {
            branch_start + no_branch_chars.len()
        };
    }

    Some((capture_span, cursor))
}

fn find_quantified_conditional_group_exists_match_span_str(
    pattern: &QuantifiedConditionalGroupExistsPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            quantified_conditional_group_exists_matches_at_str(
                pattern, flags, string, start, endpos,
            )
            .map(
                |(capture_present, match_end, repeated_alternation_branches)| {
                    (
                        (start, match_end),
                        pattern.group_spans(start, capture_present, repeated_alternation_branches),
                    )
                },
            )
        }),
        MatchMode::Match => {
            quantified_conditional_group_exists_matches_at_str(pattern, flags, string, pos, endpos)
                .map(
                    |(capture_present, match_end, repeated_alternation_branches)| {
                        (
                            (pos, match_end),
                            pattern.group_spans(
                                pos,
                                capture_present,
                                repeated_alternation_branches,
                            ),
                        )
                    },
                )
        }
        MatchMode::Fullmatch => {
            quantified_conditional_group_exists_matches_at_str(pattern, flags, string, pos, endpos)
                .and_then(
                    |(capture_present, match_end, repeated_alternation_branches)| {
                        (match_end == endpos).then_some((
                            (pos, match_end),
                            pattern.group_spans(
                                pos,
                                capture_present,
                                repeated_alternation_branches,
                            ),
                        ))
                    },
                )
        }
    }
}

fn find_quantified_conditional_group_exists_whole_match_span_str(
    pattern: &QuantifiedConditionalGroupExistsWholePattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            quantified_conditional_group_exists_whole_matches_at_str(
                pattern, flags, string, start, endpos,
            )
            .map(|(capture_span, match_end)| {
                ((start, match_end), pattern.group_spans(capture_span))
            })
        }),
        MatchMode::Match => quantified_conditional_group_exists_whole_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .map(|(capture_span, match_end)| ((pos, match_end), pattern.group_spans(capture_span))),
        MatchMode::Fullmatch => quantified_conditional_group_exists_whole_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .and_then(|(capture_span, match_end)| {
            (match_end == endpos).then_some(((pos, match_end), pattern.group_spans(capture_span)))
        }),
    }
}

fn ranged_repeat_group_matches_at_str(
    pattern: &RangedRepeatGroupPattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<(usize, usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let capture_chars: Vec<char> = pattern.capture.body.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let capture_start = start + prefix_chars.len();
    let capture_end = capture_start + capture_chars.len();
    if !literal_matches_at_str(
        capture_chars.as_slice(),
        flags,
        string,
        capture_start,
        endpos,
    ) {
        return None;
    }

    let mut repeat_count = 1;
    let mut repeat_end = capture_end;

    while repeat_count < pattern.max_repeat
        && literal_matches_at_str(capture_chars.as_slice(), flags, string, repeat_end, endpos)
    {
        repeat_end += capture_chars.len();
        repeat_count += 1;
    }

    for candidate_count in (1..=repeat_count).rev() {
        let candidate_end = capture_start + capture_chars.len() * candidate_count;
        if literal_matches_at_str(
            suffix_chars.as_slice(),
            flags,
            string,
            candidate_end,
            endpos,
        ) {
            return Some((candidate_count, candidate_end + suffix_chars.len()));
        }
    }

    None
}

fn exact_repeat_group_alternation_matches_at_str<'a>(
    pattern: &'a ExactRepeatGroupAlternationPattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<((usize, usize), usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let branch_start = start + prefix_chars.len();
    quantified_alternation_matches_exact_repeats(
        pattern.branches.as_slice(),
        flags,
        string,
        branch_start,
        endpos,
        2,
        suffix_chars.as_slice(),
    )
}

fn find_exact_repeat_group_alternation_match_span_str(
    pattern: &ExactRepeatGroupAlternationPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            exact_repeat_group_alternation_matches_at_str(pattern, flags, string, start, endpos)
                .map(|(last_branch_span, match_end)| {
                    ((start, match_end), pattern.group_spans(last_branch_span))
                })
        }),
        MatchMode::Match => exact_repeat_group_alternation_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .map(|(last_branch_span, match_end)| {
            ((pos, match_end), pattern.group_spans(last_branch_span))
        }),
        MatchMode::Fullmatch => {
            exact_repeat_group_alternation_matches_at_str(pattern, flags, string, pos, endpos)
                .and_then(|(last_branch_span, match_end)| {
                    (match_end == endpos)
                        .then_some(((pos, match_end), pattern.group_spans(last_branch_span)))
                })
        }
    }
}

fn find_ranged_repeat_group_match_span_str(
    pattern: &RangedRepeatGroupPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            ranged_repeat_group_matches_at_str(pattern, flags, string, start, endpos).map(
                |(repeat_count, match_end)| {
                    ((start, match_end), pattern.group_spans(start, repeat_count))
                },
            )
        }),
        MatchMode::Match => ranged_repeat_group_matches_at_str(pattern, flags, string, pos, endpos)
            .map(|(repeat_count, match_end)| {
                ((pos, match_end), pattern.group_spans(pos, repeat_count))
            }),
        MatchMode::Fullmatch => ranged_repeat_group_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .and_then(|(repeat_count, match_end)| {
            (match_end == endpos)
                .then_some(((pos, match_end), pattern.group_spans(pos, repeat_count)))
        }),
    }
}

fn wider_ranged_repeat_grouped_alternation_backtracking_heavy_matches_exact_repeats<'a>(
    branches: &[&'a str],
    repeated_suffix_chars: &[char],
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
    repeat_count: usize,
    suffix_chars: &[char],
) -> Option<(((usize, usize), (usize, usize)), usize)> {
    for branch in branches {
        let branch_chars: Vec<char> = branch.chars().collect();
        let branch_end = start + branch_chars.len();
        let outer_end = branch_end + repeated_suffix_chars.len();
        if !literal_matches_at_str(branch_chars.as_slice(), flags, string, start, endpos)
            || !literal_matches_at_str(repeated_suffix_chars, flags, string, branch_end, endpos)
        {
            continue;
        }

        if repeat_count == 1 {
            if literal_matches_at_str(suffix_chars, flags, string, outer_end, endpos) {
                return Some((
                    ((start, outer_end), (start, branch_end)),
                    outer_end + suffix_chars.len(),
                ));
            }
            continue;
        }

        if let Some(result) =
            wider_ranged_repeat_grouped_alternation_backtracking_heavy_matches_exact_repeats(
                branches,
                repeated_suffix_chars,
                flags,
                string,
                outer_end,
                endpos,
                repeat_count - 1,
                suffix_chars,
            )
        {
            return Some(result);
        }
    }

    None
}

fn wider_ranged_repeat_grouped_alternation_backtracking_heavy_matches_at_str<'a>(
    pattern: &'a WiderRangedRepeatGroupedAlternationBacktrackingHeavyPattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<((usize, usize), (usize, usize), usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let repeated_suffix_chars: Vec<char> = pattern.repeated_suffix.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let repetition_start = start + prefix_chars.len();
    for candidate_count in (1..=pattern.max_repeat).rev() {
        if let Some(((outer_span, inner_span), match_end)) =
            wider_ranged_repeat_grouped_alternation_backtracking_heavy_matches_exact_repeats(
                pattern.branches.as_slice(),
                repeated_suffix_chars.as_slice(),
                flags,
                string,
                repetition_start,
                endpos,
                candidate_count,
                suffix_chars.as_slice(),
            )
        {
            return Some((outer_span, inner_span, match_end));
        }
    }

    None
}

fn find_wider_ranged_repeat_grouped_alternation_backtracking_heavy_match_span_str(
    pattern: &WiderRangedRepeatGroupedAlternationBacktrackingHeavyPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            wider_ranged_repeat_grouped_alternation_backtracking_heavy_matches_at_str(
                pattern, flags, string, start, endpos,
            )
            .map(|(outer_span, inner_span, match_end)| {
                (
                    (start, match_end),
                    pattern.group_spans(outer_span, inner_span),
                )
            })
        }),
        MatchMode::Match => {
            wider_ranged_repeat_grouped_alternation_backtracking_heavy_matches_at_str(
                pattern, flags, string, pos, endpos,
            )
            .map(|(outer_span, inner_span, match_end)| {
                (
                    (pos, match_end),
                    pattern.group_spans(outer_span, inner_span),
                )
            })
        }
        MatchMode::Fullmatch => {
            wider_ranged_repeat_grouped_alternation_backtracking_heavy_matches_at_str(
                pattern, flags, string, pos, endpos,
            )
            .and_then(|(outer_span, inner_span, match_end)| {
                (match_end == endpos).then_some((
                    (pos, match_end),
                    pattern.group_spans(outer_span, inner_span),
                ))
            })
        }
    }
}

fn open_ended_quantified_group_alternation_backtracking_heavy_max_repeats(
    pattern: &OpenEndedQuantifiedGroupAlternationBacktrackingHeavyPattern<'_>,
    string_len: usize,
    start: usize,
    suffix_chars: &[char],
) -> usize {
    let min_branch_len = pattern
        .branches
        .iter()
        .map(|branch| branch.chars().count())
        .min()
        .unwrap_or(0);
    let repeated_suffix_len = pattern.repeated_suffix.chars().count();
    let min_repeat_len = min_branch_len + repeated_suffix_len;

    if min_repeat_len == 0 || start + min_repeat_len + suffix_chars.len() > string_len {
        return 0;
    }

    (string_len - start - suffix_chars.len()) / min_repeat_len
}

fn open_ended_quantified_group_alternation_backtracking_heavy_matches_at_str<'a>(
    pattern: &'a OpenEndedQuantifiedGroupAlternationBacktrackingHeavyPattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<((usize, usize), (usize, usize), usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let repeated_suffix_chars: Vec<char> = pattern.repeated_suffix.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let repetition_start = start + prefix_chars.len();
    let max_repeat = open_ended_quantified_group_alternation_backtracking_heavy_max_repeats(
        pattern,
        endpos,
        repetition_start,
        suffix_chars.as_slice(),
    );
    if max_repeat < pattern.min_repeat {
        return None;
    }
    for candidate_count in (pattern.min_repeat..=max_repeat).rev() {
        if let Some(((outer_span, inner_span), match_end)) =
            wider_ranged_repeat_grouped_alternation_backtracking_heavy_matches_exact_repeats(
                pattern.branches.as_slice(),
                repeated_suffix_chars.as_slice(),
                flags,
                string,
                repetition_start,
                endpos,
                candidate_count,
                suffix_chars.as_slice(),
            )
        {
            return Some((outer_span, inner_span, match_end));
        }
    }

    None
}

fn find_open_ended_quantified_group_alternation_backtracking_heavy_match_span_str(
    pattern: &OpenEndedQuantifiedGroupAlternationBacktrackingHeavyPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            open_ended_quantified_group_alternation_backtracking_heavy_matches_at_str(
                pattern, flags, string, start, endpos,
            )
            .map(|(outer_span, inner_span, match_end)| {
                (
                    (start, match_end),
                    pattern.group_spans(outer_span, inner_span),
                )
            })
        }),
        MatchMode::Match => {
            open_ended_quantified_group_alternation_backtracking_heavy_matches_at_str(
                pattern, flags, string, pos, endpos,
            )
            .map(|(outer_span, inner_span, match_end)| {
                (
                    (pos, match_end),
                    pattern.group_spans(outer_span, inner_span),
                )
            })
        }
        MatchMode::Fullmatch => {
            open_ended_quantified_group_alternation_backtracking_heavy_matches_at_str(
                pattern, flags, string, pos, endpos,
            )
            .and_then(|(outer_span, inner_span, match_end)| {
                (match_end == endpos).then_some((
                    (pos, match_end),
                    pattern.group_spans(outer_span, inner_span),
                ))
            })
        }
    }
}

fn nested_open_ended_quantified_group_alternation_matches_at_str(
    pattern: &NestedOpenEndedQuantifiedGroupAlternationPattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<((usize, usize), (usize, usize), usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let repetition_start = start + prefix_chars.len();
    let max_repeat = quantified_alternation_open_ended_max_repeats_for_branches(
        pattern.branches.as_slice(),
        flags,
        string,
        repetition_start,
        endpos,
        suffix_chars.as_slice(),
    );
    if max_repeat < pattern.min_repeat {
        return None;
    }

    for candidate_count in (pattern.min_repeat..=max_repeat).rev() {
        if let Some((inner_span, match_end)) = quantified_alternation_matches_exact_repeats(
            pattern.branches.as_slice(),
            flags,
            string,
            repetition_start,
            endpos,
            candidate_count,
            suffix_chars.as_slice(),
        ) {
            return Some(((repetition_start, inner_span.1), inner_span, match_end));
        }
    }

    None
}

fn find_nested_open_ended_quantified_group_alternation_match_span_str(
    pattern: &NestedOpenEndedQuantifiedGroupAlternationPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            nested_open_ended_quantified_group_alternation_matches_at_str(
                pattern, flags, string, start, endpos,
            )
            .map(|(outer_span, inner_span, match_end)| {
                (
                    (start, match_end),
                    pattern.group_spans(outer_span, inner_span),
                )
            })
        }),
        MatchMode::Match => nested_open_ended_quantified_group_alternation_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .map(|(outer_span, inner_span, match_end)| {
            (
                (pos, match_end),
                pattern.group_spans(outer_span, inner_span),
            )
        }),
        MatchMode::Fullmatch => nested_open_ended_quantified_group_alternation_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .and_then(|(outer_span, inner_span, match_end)| {
            (match_end == endpos).then_some((
                (pos, match_end),
                pattern.group_spans(outer_span, inner_span),
            ))
        }),
    }
}

fn nested_broader_range_wider_ranged_repeat_quantified_group_alternation_matches_at_str(
    pattern: &NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationPattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<((usize, usize), (usize, usize), usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let repetition_start = start + prefix_chars.len();
    let max_repeat = usize::min(
        pattern.max_repeat,
        quantified_alternation_open_ended_max_repeats_for_branches(
            pattern.branches.as_slice(),
            flags,
            string,
            repetition_start,
            endpos,
            suffix_chars.as_slice(),
        ),
    );
    if max_repeat < pattern.min_repeat {
        return None;
    }

    for candidate_count in (pattern.min_repeat..=max_repeat).rev() {
        if let Some((inner_span, match_end)) = quantified_alternation_matches_exact_repeats(
            pattern.branches.as_slice(),
            flags,
            string,
            repetition_start,
            endpos,
            candidate_count,
            suffix_chars.as_slice(),
        ) {
            return Some(((repetition_start, inner_span.1), inner_span, match_end));
        }
    }

    None
}

fn find_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_match_span_str(
    pattern: &NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            nested_broader_range_wider_ranged_repeat_quantified_group_alternation_matches_at_str(
                pattern, flags, string, start, endpos,
            )
            .map(|(outer_span, inner_span, match_end)| {
                (
                    (start, match_end),
                    pattern.group_spans(outer_span, inner_span),
                )
            })
        }),
        MatchMode::Match => {
            nested_broader_range_wider_ranged_repeat_quantified_group_alternation_matches_at_str(
                pattern, flags, string, pos, endpos,
            )
            .map(|(outer_span, inner_span, match_end)| {
                (
                    (pos, match_end),
                    pattern.group_spans(outer_span, inner_span),
                )
            })
        }
        MatchMode::Fullmatch => {
            nested_broader_range_wider_ranged_repeat_quantified_group_alternation_matches_at_str(
                pattern, flags, string, pos, endpos,
            )
            .and_then(|(outer_span, inner_span, match_end)| {
                (match_end == endpos).then_some((
                    (pos, match_end),
                    pattern.group_spans(outer_span, inner_span),
                ))
            })
        }
    }
}

fn nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_matches_at_str(
    pattern: &NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationBacktrackingHeavyPattern<
        '_,
    >,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<((usize, usize), (usize, usize), (usize, usize), usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let repeated_suffix_chars: Vec<char> = pattern.repeated_suffix.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let repetition_start = start + prefix_chars.len();
    for candidate_count in (1..=pattern.max_repeat).rev() {
        if let Some(((repeated_span, inner_span), match_end)) =
            wider_ranged_repeat_grouped_alternation_backtracking_heavy_matches_exact_repeats(
                pattern.branches.as_slice(),
                repeated_suffix_chars.as_slice(),
                flags,
                string,
                repetition_start,
                endpos,
                candidate_count,
                suffix_chars.as_slice(),
            )
        {
            return Some((
                (repetition_start, repeated_span.1),
                repeated_span,
                inner_span,
                match_end,
            ));
        }
    }

    None
}

fn find_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_match_span_str(
    pattern: &NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationBacktrackingHeavyPattern<
        '_,
    >,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_matches_at_str(
                pattern, flags, string, start, endpos,
            )
            .map(|(outer_span, repeated_span, inner_span, match_end)| {
                (
                    (start, match_end),
                    pattern.group_spans(outer_span, repeated_span, inner_span),
                )
            })
        }),
        MatchMode::Match => {
            nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_matches_at_str(
                pattern, flags, string, pos, endpos,
            )
            .map(|(outer_span, repeated_span, inner_span, match_end)| {
                (
                    (pos, match_end),
                    pattern.group_spans(outer_span, repeated_span, inner_span),
                )
            })
        }
        MatchMode::Fullmatch => {
            nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_matches_at_str(
                pattern, flags, string, pos, endpos,
            )
            .and_then(|(outer_span, repeated_span, inner_span, match_end)| {
                (match_end == endpos).then_some((
                    (pos, match_end),
                    pattern.group_spans(outer_span, repeated_span, inner_span),
                ))
            })
        }
    }
}

fn nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_matches_at_str(
    pattern: &NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationConditionalPattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<(
    Option<(usize, usize)>,
    Option<(usize, usize)>,
    Option<(usize, usize)>,
    usize,
)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let middle_chars: Vec<char> = pattern.middle.chars().collect();
    let yes_branch_chars: Vec<char> = pattern.yes_branch.chars().collect();
    let no_branch_chars: Vec<char> = pattern.no_branch.chars().collect();
    let present_suffix_chars: Vec<char> = pattern
        .middle
        .chars()
        .chain(pattern.yes_branch.chars())
        .collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let repetition_start = start + prefix_chars.len();
    let max_repeat = usize::min(
        pattern.max_repeat,
        quantified_alternation_open_ended_max_repeats_for_branches(
            pattern.branches.as_slice(),
            flags,
            string,
            repetition_start,
            endpos,
            present_suffix_chars.as_slice(),
        ),
    );
    if max_repeat >= pattern.min_repeat {
        for candidate_count in (pattern.min_repeat..=max_repeat).rev() {
            if let Some((branch_span, match_end)) = quantified_alternation_matches_exact_repeats(
                pattern.branches.as_slice(),
                flags,
                string,
                repetition_start,
                endpos,
                candidate_count,
                present_suffix_chars.as_slice(),
            ) {
                let outer_end = match_end.saturating_sub(yes_branch_chars.len());
                let inner_end = outer_end.saturating_sub(middle_chars.len());
                return Some((
                    Some((repetition_start, outer_end)),
                    Some((repetition_start, inner_end)),
                    Some(branch_span),
                    match_end,
                ));
            }
        }
    }

    literal_matches_at_str(
        no_branch_chars.as_slice(),
        flags,
        string,
        repetition_start,
        endpos,
    )
    .then_some((None, None, None, repetition_start + no_branch_chars.len()))
}

fn find_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_match_span_str(
    pattern: &NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationConditionalPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_matches_at_str(
                pattern, flags, string, start, endpos,
            )
            .map(|(outer_span, inner_span, branch_span, match_end)| {
                (
                    (start, match_end),
                    pattern.group_spans(outer_span, inner_span, branch_span),
                )
            })
        }),
        MatchMode::Match => {
            nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_matches_at_str(
                pattern, flags, string, pos, endpos,
            )
            .map(|(outer_span, inner_span, branch_span, match_end)| {
                (
                    (pos, match_end),
                    pattern.group_spans(outer_span, inner_span, branch_span),
                )
            })
        }
        MatchMode::Fullmatch => {
            nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_matches_at_str(
                pattern, flags, string, pos, endpos,
            )
            .and_then(|(outer_span, inner_span, branch_span, match_end)| {
                (match_end == endpos).then_some((
                    (pos, match_end),
                    pattern.group_spans(outer_span, inner_span, branch_span),
                ))
            })
        }
    }
}

fn quantified_alternation_matches_at_str<'a>(
    pattern: &'a QuantifiedAlternationPattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<((usize, usize), usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let branch_start = start + prefix_chars.len();
    let max_repeat = pattern.max_repeat.unwrap_or_else(|| {
        quantified_alternation_open_ended_max_repeats(
            pattern,
            flags,
            string,
            branch_start,
            endpos,
            suffix_chars.as_slice(),
        )
    });
    if max_repeat < pattern.min_repeat {
        return None;
    }
    for candidate_count in (pattern.min_repeat..=max_repeat).rev() {
        if let Some((last_branch_span, match_end)) = quantified_alternation_matches_exact_repeats(
            pattern.branches.as_slice(),
            flags,
            string,
            branch_start,
            endpos,
            candidate_count,
            suffix_chars.as_slice(),
        ) {
            return Some((last_branch_span, match_end));
        }
    }

    None
}

fn quantified_alternation_open_ended_max_repeats(
    pattern: &QuantifiedAlternationPattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
    suffix_chars: &[char],
) -> usize {
    quantified_alternation_open_ended_max_repeats_for_branches(
        pattern.branches.as_slice(),
        flags,
        string,
        start,
        endpos,
        suffix_chars,
    )
}

fn quantified_alternation_open_ended_max_repeats_for_branches(
    branches: &[&str],
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
    suffix_chars: &[char],
) -> usize {
    let branch_len = branches
        .first()
        .map(|branch| branch.chars().count())
        .unwrap_or(0);
    if branch_len == 0 {
        return 0;
    }

    let mut cursor = start;
    let mut max_repeat = 0;
    while cursor + branch_len + suffix_chars.len() <= endpos {
        let matched = branches.iter().any(|branch| {
            let branch_chars: Vec<char> = branch.chars().collect();
            literal_matches_at_str(branch_chars.as_slice(), flags, string, cursor, endpos)
        });
        if !matched {
            break;
        }
        max_repeat += 1;
        cursor += branch_len;
    }

    max_repeat
}

fn quantified_alternation_matches_exact_repeats<'a>(
    branches: &[&'a str],
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
    repeat_count: usize,
    suffix_chars: &[char],
) -> Option<((usize, usize), usize)> {
    if repeat_count == 0 {
        return literal_matches_at_str(suffix_chars, flags, string, start, endpos)
            .then_some(((start, start), start + suffix_chars.len()));
    }

    for branch in branches {
        let branch_chars: Vec<char> = branch.chars().collect();
        let branch_end = start + branch_chars.len();
        if !literal_matches_at_str(branch_chars.as_slice(), flags, string, start, endpos) {
            continue;
        }

        if repeat_count == 1 {
            if literal_matches_at_str(suffix_chars, flags, string, branch_end, endpos) {
                return Some(((start, branch_end), branch_end + suffix_chars.len()));
            }
            continue;
        }

        if let Some(result) = quantified_alternation_matches_exact_repeats(
            branches,
            flags,
            string,
            branch_end,
            endpos,
            repeat_count - 1,
            suffix_chars,
        ) {
            return Some(result);
        }
    }

    None
}

fn quantified_alternation_nested_branch_matches_at_str(
    pattern: &QuantifiedAlternationNestedBranchPattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<(Option<(usize, usize)>, Option<(usize, usize)>, usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();
    let literal_branch_chars: Vec<char> = pattern.literal_branch.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let repetition_start = start + prefix_chars.len();
    for candidate_count in (1..=pattern.max_repeat).rev() {
        for first_branch in &pattern.inner_branches {
            let first_branch_chars: Vec<char> = first_branch.chars().collect();
            let first_branch_end = repetition_start + first_branch_chars.len();
            if !literal_matches_at_str(
                first_branch_chars.as_slice(),
                flags,
                string,
                repetition_start,
                endpos,
            ) {
                continue;
            }

            if candidate_count == 1 {
                if literal_matches_at_str(
                    suffix_chars.as_slice(),
                    flags,
                    string,
                    first_branch_end,
                    endpos,
                ) {
                    return Some((
                        Some((repetition_start, first_branch_end)),
                        Some((repetition_start, first_branch_end)),
                        first_branch_end + suffix_chars.len(),
                    ));
                }
                continue;
            }

            let second_repetition_start = first_branch_end;
            for second_branch in &pattern.inner_branches {
                let second_branch_chars: Vec<char> = second_branch.chars().collect();
                let second_branch_end = second_repetition_start + second_branch_chars.len();
                if literal_matches_at_str(
                    second_branch_chars.as_slice(),
                    flags,
                    string,
                    second_repetition_start,
                    endpos,
                ) && literal_matches_at_str(
                    suffix_chars.as_slice(),
                    flags,
                    string,
                    second_branch_end,
                    endpos,
                ) {
                    return Some((
                        Some((second_repetition_start, second_branch_end)),
                        Some((second_repetition_start, second_branch_end)),
                        second_branch_end + suffix_chars.len(),
                    ));
                }
            }

            let second_literal_end = second_repetition_start + literal_branch_chars.len();
            if literal_matches_at_str(
                literal_branch_chars.as_slice(),
                flags,
                string,
                second_repetition_start,
                endpos,
            ) && literal_matches_at_str(
                suffix_chars.as_slice(),
                flags,
                string,
                second_literal_end,
                endpos,
            ) {
                return Some((
                    Some((second_repetition_start, second_literal_end)),
                    Some((repetition_start, first_branch_end)),
                    second_literal_end + suffix_chars.len(),
                ));
            }
        }

        let first_literal_end = repetition_start + literal_branch_chars.len();
        if literal_matches_at_str(
            literal_branch_chars.as_slice(),
            flags,
            string,
            repetition_start,
            endpos,
        ) {
            if candidate_count == 1 {
                if literal_matches_at_str(
                    suffix_chars.as_slice(),
                    flags,
                    string,
                    first_literal_end,
                    endpos,
                ) {
                    return Some((
                        Some((repetition_start, first_literal_end)),
                        None,
                        first_literal_end + suffix_chars.len(),
                    ));
                }
                continue;
            }

            let second_repetition_start = first_literal_end;
            for second_branch in &pattern.inner_branches {
                let second_branch_chars: Vec<char> = second_branch.chars().collect();
                let second_branch_end = second_repetition_start + second_branch_chars.len();
                if literal_matches_at_str(
                    second_branch_chars.as_slice(),
                    flags,
                    string,
                    second_repetition_start,
                    endpos,
                ) && literal_matches_at_str(
                    suffix_chars.as_slice(),
                    flags,
                    string,
                    second_branch_end,
                    endpos,
                ) {
                    return Some((
                        Some((second_repetition_start, second_branch_end)),
                        Some((second_repetition_start, second_branch_end)),
                        second_branch_end + suffix_chars.len(),
                    ));
                }
            }

            let second_literal_end = second_repetition_start + literal_branch_chars.len();
            if literal_matches_at_str(
                literal_branch_chars.as_slice(),
                flags,
                string,
                second_repetition_start,
                endpos,
            ) && literal_matches_at_str(
                suffix_chars.as_slice(),
                flags,
                string,
                second_literal_end,
                endpos,
            ) {
                return Some((
                    Some((second_repetition_start, second_literal_end)),
                    None,
                    second_literal_end + suffix_chars.len(),
                ));
            }
        }
    }

    None
}

fn quantified_alternation_conditional_matches_at_str<'a>(
    pattern: &'a QuantifiedAlternationConditionalPattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<(Option<(usize, usize)>, Option<(usize, usize)>, usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let yes_branch_chars: Vec<char> = pattern.yes_branch.chars().collect();
    let no_branch_chars: Vec<char> = pattern.no_branch.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let branch_start = start + prefix_chars.len();
    let max_repeat = pattern.max_repeat.unwrap_or_else(|| {
        quantified_alternation_open_ended_max_repeats_for_branches(
            pattern.branches.as_slice(),
            flags,
            string,
            branch_start,
            endpos,
            &[],
        )
    });
    for candidate_count in (pattern.min_repeat..=max_repeat).rev() {
        if let Some((last_branch_span, repeated_end)) = quantified_alternation_matches_exact_repeats(
            pattern.branches.as_slice(),
            flags,
            string,
            branch_start,
            endpos,
            candidate_count,
            &[],
        ) {
            if literal_matches_at_str(
                yes_branch_chars.as_slice(),
                flags,
                string,
                repeated_end,
                endpos,
            ) {
                return Some((
                    Some((branch_start, repeated_end)),
                    Some(last_branch_span),
                    repeated_end + yes_branch_chars.len(),
                ));
            }
        }
    }

    literal_matches_at_str(
        no_branch_chars.as_slice(),
        flags,
        string,
        branch_start,
        endpos,
    )
    .then_some((None, None, branch_start + no_branch_chars.len()))
}

fn quantified_branch_local_backreference_matches_at_str(
    pattern: &QuantifiedBranchLocalBackreferencePattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<(usize, usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let inner_chars: Vec<char> = pattern.inner_body.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let branch_start = start + prefix_chars.len();
    let mut max_repeat = 0;
    let mut cursor = branch_start;
    while literal_matches_at_str(inner_chars.as_slice(), flags, string, cursor, endpos) {
        max_repeat += 1;
        cursor += inner_chars.len();
    }

    if max_repeat == 0 {
        return None;
    }

    for repeat_count in (1..=max_repeat).rev() {
        let repeated_end = branch_start + inner_chars.len() * repeat_count;
        let backreference_end = repeated_end + inner_chars.len();

        if literal_matches_at_str(inner_chars.as_slice(), flags, string, repeated_end, endpos)
            && literal_matches_at_str(
                suffix_chars.as_slice(),
                flags,
                string,
                backreference_end,
                endpos,
            )
        {
            return Some((repeat_count, backreference_end + suffix_chars.len()));
        }
    }

    None
}

fn find_quantified_branch_local_backreference_match_span_str(
    pattern: &QuantifiedBranchLocalBackreferencePattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            quantified_branch_local_backreference_matches_at_str(
                pattern, flags, string, start, endpos,
            )
            .map(|(repeat_count, match_end)| {
                ((start, match_end), pattern.group_spans(start, repeat_count))
            })
        }),
        MatchMode::Match => quantified_branch_local_backreference_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .map(|(repeat_count, match_end)| {
            ((pos, match_end), pattern.group_spans(pos, repeat_count))
        }),
        MatchMode::Fullmatch => quantified_branch_local_backreference_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .and_then(|(repeat_count, match_end)| {
            (match_end == endpos)
                .then_some(((pos, match_end), pattern.group_spans(pos, repeat_count)))
        }),
    }
}

fn find_quantified_alternation_match_span_str(
    pattern: &QuantifiedAlternationPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            quantified_alternation_matches_at_str(pattern, flags, string, start, endpos).map(
                |(last_branch_span, match_end)| {
                    ((start, match_end), pattern.group_spans(last_branch_span))
                },
            )
        }),
        MatchMode::Match => quantified_alternation_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .map(|(last_branch_span, match_end)| {
            ((pos, match_end), pattern.group_spans(last_branch_span))
        }),
        MatchMode::Fullmatch => quantified_alternation_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .and_then(|(last_branch_span, match_end)| {
            (match_end == endpos)
                .then_some(((pos, match_end), pattern.group_spans(last_branch_span)))
        }),
    }
}

fn find_quantified_alternation_nested_branch_match_span_str(
    pattern: &QuantifiedAlternationNestedBranchPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            quantified_alternation_nested_branch_matches_at_str(
                pattern, flags, string, start, endpos,
            )
            .map(|(outer_span, inner_span, match_end)| {
                (
                    (start, match_end),
                    pattern.group_spans(outer_span, inner_span),
                )
            })
        }),
        MatchMode::Match => {
            quantified_alternation_nested_branch_matches_at_str(pattern, flags, string, pos, endpos)
                .map(|(outer_span, inner_span, match_end)| {
                    (
                        (pos, match_end),
                        pattern.group_spans(outer_span, inner_span),
                    )
                })
        }
        MatchMode::Fullmatch => {
            quantified_alternation_nested_branch_matches_at_str(pattern, flags, string, pos, endpos)
                .and_then(|(outer_span, inner_span, match_end)| {
                    (match_end == endpos).then_some((
                        (pos, match_end),
                        pattern.group_spans(outer_span, inner_span),
                    ))
                })
        }
    }
}

fn find_quantified_alternation_conditional_match_span_str(
    pattern: &QuantifiedAlternationConditionalPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            quantified_alternation_conditional_matches_at_str(pattern, flags, string, start, endpos)
                .map(|(outer_span, inner_span, match_end)| {
                    (
                        (start, match_end),
                        pattern.group_spans(outer_span, inner_span),
                    )
                })
        }),
        MatchMode::Match => {
            quantified_alternation_conditional_matches_at_str(pattern, flags, string, pos, endpos)
                .map(|(outer_span, inner_span, match_end)| {
                    (
                        (pos, match_end),
                        pattern.group_spans(outer_span, inner_span),
                    )
                })
        }
        MatchMode::Fullmatch => {
            quantified_alternation_conditional_matches_at_str(pattern, flags, string, pos, endpos)
                .and_then(|(outer_span, inner_span, match_end)| {
                    (match_end == endpos).then_some((
                        (pos, match_end),
                        pattern.group_spans(outer_span, inner_span),
                    ))
                })
        }
    }
}

fn quantified_alternation_branch_local_backreference_matches_at_str<'a>(
    pattern: &'a QuantifiedAlternationBranchLocalBackreferencePattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<(usize, &'a str, usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let repetition_start = start + prefix_chars.len();
    let mut max_repeat = 0usize;
    let mut cursor = repetition_start;
    while max_repeat < pattern.max_repeat {
        let mut matched_branch = None;
        for branch in &pattern.branches {
            let branch_chars: Vec<char> = branch.chars().collect();
            let branch_end = cursor + branch_chars.len();
            let outer_end = branch_end + branch_chars.len();
            if literal_matches_at_str(branch_chars.as_slice(), flags, string, cursor, endpos)
                && literal_matches_at_str(
                    branch_chars.as_slice(),
                    flags,
                    string,
                    branch_end,
                    endpos,
                )
            {
                matched_branch = Some(outer_end);
                break;
            }
        }

        let Some(branch_end) = matched_branch else {
            break;
        };
        max_repeat += 1;
        cursor = branch_end;
    }

    if max_repeat == 0 {
        return None;
    }

    for repeat_count in (1..=max_repeat).rev() {
        let mut cursor = repetition_start;
        let mut last_branch = None;

        for _ in 0..repeat_count {
            let mut matched_branch = None;
            for branch in &pattern.branches {
                let branch_chars: Vec<char> = branch.chars().collect();
                let branch_end = cursor + branch_chars.len();
                let outer_end = branch_end + branch_chars.len();
                if literal_matches_at_str(branch_chars.as_slice(), flags, string, cursor, endpos)
                    && literal_matches_at_str(
                        branch_chars.as_slice(),
                        flags,
                        string,
                        branch_end,
                        endpos,
                    )
                {
                    matched_branch = Some((*branch, outer_end));
                    break;
                }
            }

            let Some((branch, branch_end)) = matched_branch else {
                last_branch = None;
                break;
            };
            last_branch = Some(branch);
            cursor = branch_end;
        }

        let Some(last_branch) = last_branch else {
            continue;
        };

        if literal_matches_at_str(suffix_chars.as_slice(), flags, string, cursor, endpos) {
            return Some((repeat_count, last_branch, cursor + suffix_chars.len()));
        }
    }

    None
}

fn find_quantified_alternation_branch_local_backreference_match_span_str(
    pattern: &QuantifiedAlternationBranchLocalBackreferencePattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            quantified_alternation_branch_local_backreference_matches_at_str(
                pattern, flags, string, start, endpos,
            )
            .map(|(repeat_count, last_branch, match_end)| {
                (
                    (start, match_end),
                    pattern.group_spans(start, repeat_count, last_branch),
                )
            })
        }),
        MatchMode::Match => quantified_alternation_branch_local_backreference_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .map(|(repeat_count, last_branch, match_end)| {
            (
                (pos, match_end),
                pattern.group_spans(pos, repeat_count, last_branch),
            )
        }),
        MatchMode::Fullmatch => quantified_alternation_branch_local_backreference_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .and_then(|(repeat_count, last_branch, match_end)| {
            (match_end == endpos).then_some((
                (pos, match_end),
                pattern.group_spans(pos, repeat_count, last_branch),
            ))
        }),
    }
}

fn nested_alternation_matches_at_str(
    pattern: &NestedAlternationLiteralPattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<(usize, usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let outer_prefix_chars: Vec<char> = pattern.outer_prefix.chars().collect();
    let outer_suffix_chars: Vec<char> = pattern.outer_suffix.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();
    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let outer_start = start + prefix_chars.len();
    if !literal_matches_at_str(
        outer_prefix_chars.as_slice(),
        flags,
        string,
        outer_start,
        endpos,
    ) {
        return None;
    }

    let inner_start = outer_start + outer_prefix_chars.len();
    pattern.inner_branches.iter().find_map(|branch| {
        let branch_chars: Vec<char> = branch.chars().collect();
        let branch_len = branch_chars.len();
        let outer_suffix_start = inner_start + branch_len;
        let match_end = outer_suffix_start + outer_suffix_chars.len() + suffix_chars.len();
        (literal_matches_at_str(branch_chars.as_slice(), flags, string, inner_start, endpos)
            && literal_matches_at_str(
                outer_suffix_chars.as_slice(),
                flags,
                string,
                outer_suffix_start,
                endpos,
            )
            && literal_matches_at_str(
                suffix_chars.as_slice(),
                flags,
                string,
                outer_suffix_start + outer_suffix_chars.len(),
                endpos,
            ))
        .then_some((branch_len, match_end))
    })
}

fn find_nested_alternation_match_span_str(
    pattern: &NestedAlternationLiteralPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            nested_alternation_matches_at_str(pattern, flags, string, start, endpos).map(
                |(branch_len, match_end)| {
                    (
                        (start, match_end),
                        pattern.group_spans_for_branch_len(start, branch_len),
                    )
                },
            )
        }),
        MatchMode::Match => nested_alternation_matches_at_str(pattern, flags, string, pos, endpos)
            .map(|(branch_len, match_end)| {
                (
                    (pos, match_end),
                    pattern.group_spans_for_branch_len(pos, branch_len),
                )
            }),
        MatchMode::Fullmatch => nested_alternation_matches_at_str(
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

fn nested_alternation_branch_local_backreference_matches_at_str<'a>(
    pattern: &'a NestedAlternationBranchLocalBackreferencePattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<(&'a str, usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();
    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let outer_start = start + prefix_chars.len();
    for branch in &pattern.branches {
        let branch_chars: Vec<char> = branch.chars().collect();
        let capture_end = outer_start + branch_chars.len();
        let backreference_end = capture_end + branch_chars.len();
        if literal_matches_at_str(branch_chars.as_slice(), flags, string, outer_start, endpos)
            && literal_matches_at_str(branch_chars.as_slice(), flags, string, capture_end, endpos)
            && literal_matches_at_str(
                suffix_chars.as_slice(),
                flags,
                string,
                backreference_end,
                endpos,
            )
        {
            return Some((*branch, backreference_end + suffix_chars.len()));
        }
    }

    None
}

fn find_nested_alternation_branch_local_backreference_match_span_str(
    pattern: &NestedAlternationBranchLocalBackreferencePattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            nested_alternation_branch_local_backreference_matches_at_str(
                pattern, flags, string, start, endpos,
            )
            .map(|(matched_branch, match_end)| {
                (
                    (start, match_end),
                    pattern.group_spans(start, matched_branch),
                )
            })
        }),
        MatchMode::Match => nested_alternation_branch_local_backreference_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .map(|(matched_branch, match_end)| {
            ((pos, match_end), pattern.group_spans(pos, matched_branch))
        }),
        MatchMode::Fullmatch => nested_alternation_branch_local_backreference_matches_at_str(
            pattern, flags, string, pos, endpos,
        )
        .and_then(|(matched_branch, match_end)| {
            (match_end == endpos)
                .then_some(((pos, match_end), pattern.group_spans(pos, matched_branch)))
        }),
    }
}

fn quantified_nested_group_alternation_matches_at_str(
    pattern: &QuantifiedNestedGroupAlternationPattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<((usize, usize), (usize, usize), usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let repetition_start = start + prefix_chars.len();
    let max_repeat = quantified_alternation_open_ended_max_repeats_for_branches(
        pattern.branches.as_slice(),
        flags,
        string,
        repetition_start,
        endpos,
        suffix_chars.as_slice(),
    );
    if max_repeat == 0 {
        return None;
    }

    for candidate_count in (1..=max_repeat).rev() {
        if let Some((inner_span, match_end)) = quantified_alternation_matches_exact_repeats(
            pattern.branches.as_slice(),
            flags,
            string,
            repetition_start,
            endpos,
            candidate_count,
            suffix_chars.as_slice(),
        ) {
            return Some(((repetition_start, inner_span.1), inner_span, match_end));
        }
    }

    None
}

fn find_quantified_nested_group_alternation_match_span_str(
    pattern: &QuantifiedNestedGroupAlternationPattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            quantified_nested_group_alternation_matches_at_str(
                pattern, flags, string, start, endpos,
            )
            .map(|(outer_span, inner_span, match_end)| {
                (
                    (start, match_end),
                    pattern.group_spans(outer_span, inner_span),
                )
            })
        }),
        MatchMode::Match => {
            quantified_nested_group_alternation_matches_at_str(pattern, flags, string, pos, endpos)
                .map(|(outer_span, inner_span, match_end)| {
                    (
                        (pos, match_end),
                        pattern.group_spans(outer_span, inner_span),
                    )
                })
        }
        MatchMode::Fullmatch => {
            quantified_nested_group_alternation_matches_at_str(pattern, flags, string, pos, endpos)
                .and_then(|(outer_span, inner_span, match_end)| {
                    (match_end == endpos).then_some((
                        (pos, match_end),
                        pattern.group_spans(outer_span, inner_span),
                    ))
                })
        }
    }
}

fn quantified_nested_group_alternation_branch_local_backreference_matches_exact_repeats(
    branches: &[&str],
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
    repeat_count: usize,
    suffix_chars: &[char],
) -> Option<((usize, usize), usize)> {
    if repeat_count == 0 {
        return None;
    }

    for branch in branches {
        let branch_chars: Vec<char> = branch.chars().collect();
        let branch_end = start + branch_chars.len();
        if !literal_matches_at_str(branch_chars.as_slice(), flags, string, start, endpos) {
            continue;
        }

        if repeat_count == 1 {
            let backreference_end = branch_end + branch_chars.len();
            if literal_matches_at_str(branch_chars.as_slice(), flags, string, branch_end, endpos)
                && literal_matches_at_str(suffix_chars, flags, string, backreference_end, endpos)
            {
                return Some(((start, branch_end), backreference_end + suffix_chars.len()));
            }
            continue;
        }

        if let Some(result) =
            quantified_nested_group_alternation_branch_local_backreference_matches_exact_repeats(
                branches,
                flags,
                string,
                branch_end,
                endpos,
                repeat_count - 1,
                suffix_chars,
            )
        {
            return Some(result);
        }
    }

    None
}

fn quantified_nested_group_alternation_branch_local_backreference_matches_at_str(
    pattern: &QuantifiedNestedGroupAlternationBranchLocalBackreferencePattern<'_>,
    flags: i32,
    string: &[char],
    start: usize,
    endpos: usize,
) -> Option<((usize, usize), (usize, usize), usize)> {
    let prefix_chars: Vec<char> = pattern.prefix.chars().collect();
    let suffix_chars: Vec<char> = pattern.suffix.chars().collect();

    if !literal_matches_at_str(prefix_chars.as_slice(), flags, string, start, endpos) {
        return None;
    }

    let repetition_start = start + prefix_chars.len();
    let mut backreference_suffix_chars: Vec<char> = pattern
        .branches
        .first()
        .expect("guarded quantified nested-group alternation branch-local backreference branches")
        .chars()
        .collect();
    backreference_suffix_chars.extend(suffix_chars.iter().copied());

    let max_repeat = quantified_alternation_open_ended_max_repeats_for_branches(
        pattern.branches.as_slice(),
        flags,
        string,
        repetition_start,
        endpos,
        backreference_suffix_chars.as_slice(),
    );
    let max_repeat = pattern
        .max_repeat
        .map_or(max_repeat, |bounded_max_repeat| usize::min(bounded_max_repeat, max_repeat));
    if max_repeat == 0 {
        return None;
    }

    for candidate_count in (1..=max_repeat).rev() {
        if let Some((inner_span, match_end)) =
            quantified_nested_group_alternation_branch_local_backreference_matches_exact_repeats(
                pattern.branches.as_slice(),
                flags,
                string,
                repetition_start,
                endpos,
                candidate_count,
                suffix_chars.as_slice(),
            )
        {
            return Some(((repetition_start, inner_span.1), inner_span, match_end));
        }
    }

    None
}

fn find_quantified_nested_group_alternation_branch_local_backreference_match_span_str(
    pattern: &QuantifiedNestedGroupAlternationBranchLocalBackreferencePattern<'_>,
    flags: i32,
    mode: MatchMode,
    string: &[char],
    pos: usize,
    endpos: usize,
) -> Option<((usize, usize), Vec<Option<(usize, usize)>>)> {
    match mode {
        MatchMode::Search => (pos..=endpos).find_map(|start| {
            quantified_nested_group_alternation_branch_local_backreference_matches_at_str(
                pattern, flags, string, start, endpos,
            )
            .map(|(outer_span, inner_span, match_end)| {
                (
                    (start, match_end),
                    pattern.group_spans(outer_span, inner_span),
                )
            })
        }),
        MatchMode::Match => {
            quantified_nested_group_alternation_branch_local_backreference_matches_at_str(
                pattern, flags, string, pos, endpos,
            )
            .map(|(outer_span, inner_span, match_end)| {
                (
                    (pos, match_end),
                    pattern.group_spans(outer_span, inner_span),
                )
            })
        }
        MatchMode::Fullmatch => {
            quantified_nested_group_alternation_branch_local_backreference_matches_at_str(
                pattern, flags, string, pos, endpos,
            )
            .and_then(|(outer_span, inner_span, match_end)| {
                (match_end == endpos).then_some((
                    (pos, match_end),
                    pattern.group_spans(outer_span, inner_span),
                ))
            })
        }
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
        compile, conditional_group_exists_alternation_find_spans_str,
        conditional_group_exists_empty_else_find_spans_str,
        conditional_group_exists_empty_yes_else_find_spans_str,
        conditional_group_exists_find_spans_str, conditional_group_exists_nested_find_spans_str,
        conditional_group_exists_no_else_find_spans_str,
        conditional_group_exists_quantified_find_spans_str, escape_bytes, escape_str,
        expand_literal_replacement_template_str, grouped_alternation_find_spans_str,
        grouped_literal_find_spans_str, literal_find_spans, literal_match,
        nested_capture_find_spans_str, CapturedMatchSpan, CompileStatus,
        GroupedAlternationMatchSpan, MatchMode, MatchStatus, NamedGroup, PatternRef, FLAG_ASCII,
        FLAG_IGNORECASE, FLAG_LOCALE, FLAG_UNICODE,
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
    fn compile_accepts_bounded_nested_group_alternation_cases() {
        let outcome = compile(PatternRef::Str("a((b|c))d"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 2);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<outer>(?P<inner>b|c))d"), 0).unwrap();
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
    fn compile_accepts_bounded_branch_local_numbered_backreference_case() {
        let outcome = compile(PatternRef::Str(r"a((b)|c)\2d"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 2);
        assert!(outcome.named_groups.is_empty());
    }

    #[test]
    fn compile_accepts_bounded_branch_local_named_backreference_case() {
        let outcome = compile(PatternRef::Str("a(?P<outer>(?P<inner>b)|c)(?P=inner)d"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 2);
        assert_eq!(
            outcome.named_groups,
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
    fn compile_accepts_bounded_conditional_branch_local_backreference_cases() {
        let outcome = compile(PatternRef::Str(r"a((b)|c)\2(?(2)d|e)"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 2);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(
            PatternRef::Str("a(?P<outer>(?P<inner>b)|c)(?P=inner)(?(inner)d|e)"),
            0,
        )
        .unwrap();
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
    fn compile_accepts_bounded_quantified_branch_local_backreference_cases() {
        let outcome = compile(PatternRef::Str(r"a((b)+|c)\2d"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 2);
        assert!(outcome.named_groups.is_empty());

        let named_outcome =
            compile(PatternRef::Str("a(?P<outer>(?P<inner>b)+|c)(?P=inner)d"), 0).unwrap();
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
    fn compile_accepts_bounded_optional_group_cases() {
        let outcome = compile(PatternRef::Str("a(b)?d"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b)?d"), 0).unwrap();
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
    fn compile_accepts_bounded_optional_group_alternation_cases() {
        let outcome = compile(PatternRef::Str("a(b|c)?d"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b|c)?d"), 0).unwrap();
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
    fn compile_accepts_bounded_optional_group_alternation_branch_local_backreference_cases() {
        let outcome = compile(PatternRef::Str(r"a((b|c)\2)?d"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 2);
        assert!(outcome.named_groups.is_empty());

        let named_outcome =
            compile(PatternRef::Str("a(?P<outer>(?P<inner>b|c)(?P=inner))?d"), 0).unwrap();
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
    fn compile_accepts_bounded_conditional_group_exists_cases() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)d|e)"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b)?c(?(word)d|e)"), 0).unwrap();
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
    fn compile_accepts_bounded_conditional_group_exists_no_else_cases() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)d)"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b)?c(?(word)d)"), 0).unwrap();
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
    fn compile_accepts_bounded_nested_conditional_group_exists_no_else_cases() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)(?(1)d))"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome =
            compile(PatternRef::Str("a(?P<word>b)?c(?(word)(?(word)d))"), 0).unwrap();
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
    fn compile_accepts_bounded_nested_conditional_group_exists_two_arm_cases() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)(?(1)d|e)|f)"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome =
            compile(PatternRef::Str("a(?P<word>b)?c(?(word)(?(word)d|e)|f)"), 0).unwrap();
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
    fn compile_accepts_bounded_conditional_group_exists_empty_else_cases() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)d|)"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b)?c(?(word)d|)"), 0).unwrap();
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
    fn compile_accepts_bounded_conditional_group_exists_empty_else_alternation_cases() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)(de|df)|)"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 2);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b)?c(?(word)(de|df)|)"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!named_outcome.supports_literal);
        assert_eq!(named_outcome.group_count, 2);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "word".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn compile_accepts_bounded_conditional_group_exists_no_else_alternation_cases() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)(de|df))"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 2);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b)?c(?(word)(de|df))"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!named_outcome.supports_literal);
        assert_eq!(named_outcome.group_count, 2);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "word".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn compile_accepts_bounded_conditional_group_exists_empty_yes_else_cases() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)|e)"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b)?c(?(word)|e)"), 0).unwrap();
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
    fn compile_accepts_bounded_conditional_group_exists_empty_yes_else_alternation_cases() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)|(e|f))"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 2);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b)?c(?(word)|(e|f))"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!named_outcome.supports_literal);
        assert_eq!(named_outcome.group_count, 2);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "word".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn compile_accepts_bounded_conditional_group_exists_fully_empty_alternation_cases() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)|(?:|))"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b)?c(?(word)|(?:|))"), 0).unwrap();
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
    fn compile_accepts_bounded_quantified_conditional_group_exists_empty_yes_else_cases() {
        let outcome = compile(PatternRef::Str("(?:a(b)?c(?(1)|e)){2}"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome =
            compile(PatternRef::Str("(?:a(?P<word>b)?c(?(word)|e)){2}"), 0).unwrap();
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
    fn compile_accepts_bounded_quantified_conditional_group_exists_no_else_cases() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)d){2}"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b)?c(?(word)d){2}"), 0).unwrap();
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
    fn compile_accepts_bounded_quantified_conditional_group_exists_empty_else_cases() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)d|){2}"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b)?c(?(word)d|){2}"), 0).unwrap();
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
    fn compile_accepts_bounded_quantified_conditional_group_exists_fully_empty_cases() {
        let outcome = compile(PatternRef::Str("(?:a(b)?c(?(1)|)){2}"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("(?:a(?P<word>b)?c(?(word)|)){2}"), 0).unwrap();
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
    fn compile_accepts_bounded_quantified_conditional_group_exists_two_arm_alternation_cases() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)(de|df)|(eg|eh)){2}"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 3);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(
            PatternRef::Str("a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}"),
            0,
        )
        .unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!named_outcome.supports_literal);
        assert_eq!(named_outcome.group_count, 3);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "word".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn compile_accepts_bounded_conditional_group_exists_fully_empty_cases() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)|)"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b)?c(?(word)|)"), 0).unwrap();
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
    fn compile_accepts_bounded_nested_conditional_group_exists_empty_yes_else_cases() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)|(?(1)e|f))"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome =
            compile(PatternRef::Str("a(?P<word>b)?c(?(word)|(?(word)e|f))"), 0).unwrap();
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
    fn compile_accepts_bounded_nested_conditional_group_exists_fully_empty_cases() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)|(?(1)|))"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome =
            compile(PatternRef::Str("a(?P<word>b)?c(?(word)|(?(word)|))"), 0).unwrap();
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
    fn compile_rejects_assertion_conditioned_group_exists_cases() {
        let positive = compile(PatternRef::Str("a(?(?=b)b|c)d"), 0).unwrap_err();
        assert_eq!(positive.message, "bad character in group name '?=b'");
        assert_eq!(positive.pos, Some(4));

        let negative = compile(PatternRef::Str("a(?(?!b)b|c)d"), 0).unwrap_err();
        assert_eq!(negative.message, "bad character in group name '?!b'");
        assert_eq!(negative.pos, Some(4));
    }

    #[test]
    fn compile_accepts_bounded_exact_repeat_group_cases() {
        let outcome = compile(PatternRef::Str("a(bc){2}d"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>bc){2}d"), 0).unwrap();
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
    fn compile_accepts_bounded_exact_repeat_group_alternation_cases() {
        let outcome = compile(PatternRef::Str("a(bc|de){2}d"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>bc|de){2}d"), 0).unwrap();
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
    fn compile_accepts_bounded_ranged_repeat_group_cases() {
        let outcome = compile(PatternRef::Str("a(bc){1,2}d"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>bc){1,2}d"), 0).unwrap();
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

        let wider_outcome = compile(PatternRef::Str("a(bc){1,3}d"), 0).unwrap();
        assert_eq!(wider_outcome.status, CompileStatus::Compiled);
        assert_eq!(wider_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!wider_outcome.supports_literal);
        assert_eq!(wider_outcome.group_count, 1);
        assert!(wider_outcome.named_groups.is_empty());

        let wider_named_outcome = compile(PatternRef::Str("a(?P<word>bc){1,3}d"), 0).unwrap();
        assert_eq!(wider_named_outcome.status, CompileStatus::Compiled);
        assert_eq!(wider_named_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!wider_named_outcome.supports_literal);
        assert_eq!(wider_named_outcome.group_count, 1);
        assert_eq!(
            wider_named_outcome.named_groups,
            vec![NamedGroup {
                name: "word".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn compile_accepts_bounded_quantified_alternation_cases() {
        let outcome = compile(PatternRef::Str("a(b|c){1,2}d"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b|c){1,2}d"), 0).unwrap();
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
    fn compile_accepts_bounded_quantified_alternation_backtracking_heavy_cases() {
        let outcome = compile(PatternRef::Str("a(b|bc){1,2}d"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 1);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b|bc){1,2}d"), 0).unwrap();
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
    fn compile_accepts_bounded_quantified_alternation_nested_branch_cases() {
        let outcome = compile(PatternRef::Str("a((b|c)|de){1,2}d"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 2);
        assert!(outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>(b|c)|de){1,2}d"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!named_outcome.supports_literal);
        assert_eq!(named_outcome.group_count, 2);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "word".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn compile_accepts_bounded_quantified_alternation_conditional_cases() {
        let outcome = compile(PatternRef::Str("a((b|c){1,2})?(?(1)d|e)"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 2);
        assert!(outcome.named_groups.is_empty());

        let named_outcome =
            compile(PatternRef::Str("a(?P<outer>(b|c){1,2})?(?(outer)d|e)"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!named_outcome.supports_literal);
        assert_eq!(named_outcome.group_count, 2);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "outer".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn compile_accepts_wider_ranged_repeat_grouped_alternation_conditional_cases() {
        let outcome = compile(PatternRef::Str("a((bc|de){1,3})?(?(1)d|e)"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 2);
        assert!(outcome.named_groups.is_empty());

        let named_outcome =
            compile(PatternRef::Str("a(?P<outer>(bc|de){1,3})?(?(outer)d|e)"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!named_outcome.supports_literal);
        assert_eq!(named_outcome.group_count, 2);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "outer".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn compile_accepts_broader_range_wider_ranged_repeat_grouped_alternation_conditional_cases() {
        let outcome = compile(PatternRef::Str("a((bc|de){1,4})?(?(1)d|e)"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 2);
        assert!(outcome.named_groups.is_empty());

        let named_outcome =
            compile(PatternRef::Str("a(?P<outer>(bc|de){1,4})?(?(outer)d|e)"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!named_outcome.supports_literal);
        assert_eq!(named_outcome.group_count, 2);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "outer".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn compile_accepts_open_ended_quantified_group_alternation_conditional_cases() {
        let outcome = compile(PatternRef::Str("a((bc|de){1,})?(?(1)d|e)"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 2);
        assert!(outcome.named_groups.is_empty());

        let named_outcome =
            compile(PatternRef::Str("a(?P<outer>(bc|de){1,})?(?(outer)d|e)"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!named_outcome.supports_literal);
        assert_eq!(named_outcome.group_count, 2);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "outer".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn compile_accepts_broader_range_open_ended_quantified_group_alternation_conditional_cases() {
        let outcome = compile(PatternRef::Str("a((bc|de){2,})?(?(1)d|e)"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert!(!outcome.supports_literal);
        assert_eq!(outcome.group_count, 2);
        assert!(outcome.named_groups.is_empty());

        let named_outcome =
            compile(PatternRef::Str("a(?P<outer>(bc|de){2,})?(?(outer)d|e)"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert!(!named_outcome.supports_literal);
        assert_eq!(named_outcome.group_count, 2);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "outer".to_string(),
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
    fn branch_local_numbered_backreference_match_reports_outer_lastindex() {
        let outcome = literal_match(
            PatternRef::Str(r"a((b)|c)\2d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabbdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4)), Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn branch_local_named_backreference_fullmatch_reports_outer_lastgroup() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<outer>(?P<inner>b)|c)(?P=inner)d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abbd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 4)));
        assert_eq!(outcome.group_spans, vec![Some((1, 2)), Some((1, 2))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn conditional_branch_local_numbered_backreference_search_reports_outer_lastindex() {
        let outcome = literal_match(
            PatternRef::Str(r"a((b)|c)\2(?(2)d|e)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabbdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4)), Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn conditional_branch_local_named_backreference_reports_c_branch_as_no_match() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<outer>(?P<inner>b)|c)(?P=inner)(?(inner)d|e)"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ace"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn quantified_branch_local_numbered_backreference_search_reports_lower_bound_capture_spans() {
        let outcome = literal_match(
            PatternRef::Str(r"a((b)+|c)\2d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabbdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4)), Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn quantified_branch_local_named_backreference_fullmatch_reports_second_iteration_spans() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<outer>(?P<inner>b)+|c)(?P=inner)d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abbbd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 5)));
        assert_eq!(outcome.group_spans, vec![Some((1, 3)), Some((2, 3))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn quantified_branch_local_named_backreference_reports_c_branch_as_no_match() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<outer>(?P<inner>b)+|c)(?P=inner)d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("acd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn optional_group_search_reports_present_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 5)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_optional_group_fullmatch_reports_absent_capture_as_none() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ad"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 2)));
        assert_eq!(outcome.group_spans, vec![None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn optional_group_alternation_search_reports_selected_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b|c)?d"),
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
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_optional_group_alternation_fullmatch_reports_absent_capture_as_none() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b|c)?d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ad"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 2)));
        assert_eq!(outcome.group_spans, vec![None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn optional_group_alternation_branch_local_numbered_search_reports_outer_lastindex() {
        let outcome = literal_match(
            PatternRef::Str(r"a((b|c)\2)?d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabbdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 5)), Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn optional_group_alternation_branch_local_numbered_fullmatch_reports_absent_groups_as_none() {
        let outcome = literal_match(
            PatternRef::Str(r"a((b|c)\2)?d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ad"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 2)));
        assert_eq!(outcome.group_spans, vec![None, None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn optional_group_alternation_branch_local_named_fullmatch_reports_invalid_present_group_as_no_match(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<outer>(?P<inner>b|c)(?P=inner))?d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_search_reports_present_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)d|e)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_conditional_group_exists_fullmatch_reports_absent_capture_as_none() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)d|e)"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ace"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 3)));
        assert_eq!(outcome.group_spans, vec![None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_no_else_search_reports_present_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)d)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_conditional_group_exists_no_else_fullmatch_reports_absent_capture_as_none() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)d)"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ac"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 2)));
        assert_eq!(outcome.group_spans, vec![None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_no_else_nested_search_reports_present_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)(?(1)d))"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_conditional_group_exists_no_else_nested_fullmatch_reports_absent_capture_as_none() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)(?(word)d))"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ac"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 2)));
        assert_eq!(outcome.group_spans, vec![None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_nested_search_reports_present_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)(?(1)d|e)|f)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_conditional_group_exists_nested_fullmatch_reports_absent_capture_as_none() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)(?(word)d|e)|f)"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("acf"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 3)));
        assert_eq!(outcome.group_spans, vec![None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_nested_reports_unreachable_inner_else_as_no_match() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)(?(1)d|e)|f)"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abce"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_empty_else_search_reports_present_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)d|)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_conditional_group_exists_empty_else_fullmatch_reports_absent_capture_as_none() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)d|)"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ac"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 2)));
        assert_eq!(outcome.group_spans, vec![None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_empty_else_alternation_search_reports_selected_yes_branch_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)(de|df)|)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdfzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 7)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4)), Some((5, 7))]);
        assert_eq!(outcome.lastindex, Some(2));
    }

    #[test]
    fn named_conditional_group_exists_empty_else_alternation_fullmatch_reports_absent_groups_as_none(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)(de|df)|)"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ac"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 2)));
        assert_eq!(outcome.group_spans, vec![None, None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_no_else_alternation_search_reports_selected_yes_branch_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)(de|df))"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdfzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 7)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4)), Some((5, 7))]);
        assert_eq!(outcome.lastindex, Some(2));
    }

    #[test]
    fn named_conditional_group_exists_no_else_alternation_fullmatch_reports_absent_groups_as_none()
    {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)(de|df))"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ac"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 2)));
        assert_eq!(outcome.group_spans, vec![None, None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_empty_yes_else_search_reports_present_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)|e)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabczz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 5)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_conditional_group_exists_empty_yes_else_fullmatch_reports_absent_capture_as_none() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)|e)"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ace"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 3)));
        assert_eq!(outcome.group_spans, vec![None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_empty_yes_else_alternation_search_reports_present_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)|(e|f))"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabczz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 5)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4)), None]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_conditional_group_exists_empty_yes_else_alternation_fullmatch_reports_selected_no_branch_span(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)|(e|f))"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("acf"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 3)));
        assert_eq!(outcome.group_spans, vec![None, Some((2, 3))]);
        assert_eq!(outcome.lastindex, Some(2));
    }

    #[test]
    fn conditional_group_exists_fully_empty_alternation_search_reports_present_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)|(?:|))"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabczz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 5)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_conditional_group_exists_fully_empty_alternation_fullmatch_reports_absent_capture_as_none(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)|(?:|))"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ac"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 2)));
        assert_eq!(outcome.group_spans, vec![None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_two_arm_alternation_search_reports_yes_branch_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)(de|df)|(eg|eh))"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdfzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 7)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4)), Some((5, 7)), None]);
        assert_eq!(outcome.lastindex, Some(2));
    }

    #[test]
    fn named_conditional_group_exists_two_arm_alternation_fullmatch_reports_no_branch_capture_span()
    {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)(de|df)|(eg|eh))"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("aceh"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 4)));
        assert_eq!(outcome.group_spans, vec![None, None, Some((2, 4))]);
        assert_eq!(outcome.lastindex, Some(3));
    }

    #[test]
    fn compile_reports_two_arm_conditional_alternation_group_count() {
        let outcome = compile(PatternRef::Str("a(b)?c(?(1)(de|df)|(eg|eh))"), 0).unwrap();
        assert_eq!(outcome.status, CompileStatus::Compiled);
        assert_eq!(outcome.normalized_flags, FLAG_UNICODE);
        assert_eq!(outcome.group_count, 3);
        assert!(outcome.named_groups.is_empty());

        let named_outcome =
            compile(PatternRef::Str("a(?P<word>b)?c(?(word)(de|df)|(eg|eh))"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.group_count, 3);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "word".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn conditional_group_exists_empty_yes_else_quantified_fullmatch_reports_last_repetition_capture_span(
    ) {
        let outcome = literal_match(
            PatternRef::Str("(?:a(b)?c(?(1)|e)){2}"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("aceabc"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 6)));
        assert_eq!(outcome.group_spans, vec![Some((4, 5))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_conditional_group_exists_empty_yes_else_quantified_fullmatch_reports_last_repetition_absent_capture_as_none(
    ) {
        let outcome = literal_match(
            PatternRef::Str("(?:a(?P<word>b)?c(?(word)|e)){2}"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("aceace"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 6)));
        assert_eq!(outcome.group_spans, vec![None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_empty_yes_else_quantified_reports_present_then_absent_as_no_match()
    {
        let outcome = literal_match(
            PatternRef::Str("(?:a(b)?c(?(1)|e)){2}"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcace"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_no_else_quantified_search_reports_present_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)d){2}"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcddzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 7)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_conditional_group_exists_no_else_quantified_fullmatch_reports_absent_capture_as_none()
    {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)d){2}"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ac"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 2)));
        assert_eq!(outcome.group_spans, vec![None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_no_else_quantified_reports_missing_repeat_as_no_match() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)d){2}"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_empty_else_quantified_search_reports_present_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)d|){2}"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcddzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 7)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_conditional_group_exists_empty_else_quantified_fullmatch_reports_absent_capture_as_none(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)d|){2}"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ac"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 2)));
        assert_eq!(outcome.group_spans, vec![None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_empty_else_quantified_reports_missing_repeat_as_no_match() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)d|){2}"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_fully_empty_search_reports_present_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)|)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabczz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 5)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_conditional_group_exists_fully_empty_fullmatch_reports_absent_capture_as_none() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)|)"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ac"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 2)));
        assert_eq!(outcome.group_spans, vec![None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_fully_empty_quantified_fullmatch_reports_last_repetition_capture_span(
    ) {
        let outcome = literal_match(
            PatternRef::Str("(?:a(b)?c(?(1)|)){2}"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("acabc"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 5)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_conditional_group_exists_fully_empty_quantified_fullmatch_reports_last_repetition_absent_capture_as_none(
    ) {
        let outcome = literal_match(
            PatternRef::Str("(?:a(?P<word>b)?c(?(word)|)){2}"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("acac"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 4)));
        assert_eq!(outcome.group_spans, vec![None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_fully_empty_quantified_reports_extra_suffix_as_no_match() {
        let outcome = literal_match(
            PatternRef::Str("(?:a(b)?c(?(1)|)){2}"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("acace"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_two_arm_alternation_quantified_fullmatch_reports_last_yes_branch_span(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)(de|df)|(eg|eh)){2}"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcdedf"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 7)));
        assert_eq!(outcome.group_spans, vec![Some((1, 2)), Some((5, 7)), None]);
        assert_eq!(outcome.lastindex, Some(2));
    }

    #[test]
    fn named_conditional_group_exists_two_arm_alternation_quantified_fullmatch_reports_last_no_branch_span(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("acegeh"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 6)));
        assert_eq!(outcome.group_spans, vec![None, None, Some((4, 6))]);
        assert_eq!(outcome.lastindex, Some(3));
    }

    #[test]
    fn conditional_group_exists_empty_yes_else_nested_search_reports_present_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)|(?(1)e|f))"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabczz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 5)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_conditional_group_exists_empty_yes_else_nested_fullmatch_reports_absent_capture_as_none(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)|(?(word)e|f))"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("acf"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 3)));
        assert_eq!(outcome.group_spans, vec![None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_empty_yes_else_nested_reports_absent_yes_arm_as_no_match() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)|(?(1)e|f))"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ace"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_fully_empty_nested_search_reports_present_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)|(?(1)|))"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabczz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 5)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_conditional_group_exists_fully_empty_nested_fullmatch_reports_absent_capture_as_none()
    {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b)?c(?(word)|(?(word)|))"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("ac"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 2)));
        assert_eq!(outcome.group_spans, vec![None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn conditional_group_exists_fully_empty_nested_reports_extra_suffix_as_no_match() {
        let outcome = literal_match(
            PatternRef::Str("a(b)?c(?(1)|(?(1)|))"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("acf"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn exact_repeat_group_search_reports_final_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(bc){2}d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcbcdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 8)));
        assert_eq!(outcome.group_spans, vec![Some((5, 7))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_exact_repeat_group_fullmatch_reports_final_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>bc){2}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 5))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn exact_repeat_group_alternation_search_reports_final_de_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(bc|de){2}d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdedzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 8)));
        assert_eq!(outcome.group_spans, vec![Some((5, 7))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_exact_repeat_group_alternation_fullmatch_reports_final_de_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>bc|de){2}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("adeded"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 5))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn exact_repeat_group_alternation_fullmatch_reports_extra_repetition_as_no_match() {
        let outcome = literal_match(
            PatternRef::Str("a(bc|de){2}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbcbcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn ranged_repeat_group_search_reports_lower_bound_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(bc){1,2}d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 5))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_ranged_repeat_group_fullmatch_reports_upper_bound_final_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>bc){1,2}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 5))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn wider_ranged_repeat_group_fullmatch_reports_third_repetition_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(bc){1,3}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbcbcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 8)));
        assert_eq!(outcome.group_spans, vec![Some((5, 7))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn wider_named_ranged_repeat_group_search_reports_third_repetition_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>bc){1,3}d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcbcbcdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 10)));
        assert_eq!(outcome.group_spans, vec![Some((7, 9))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn compile_accepts_wider_ranged_repeat_grouped_backtracking_heavy_cases() {
        let numbered_outcome = compile(PatternRef::Str("a((bc|b)c){1,3}d"), 0).unwrap();
        assert_eq!(numbered_outcome.status, CompileStatus::Compiled);
        assert_eq!(numbered_outcome.normalized_flags, FLAG_UNICODE);
        assert_eq!(numbered_outcome.group_count, 2);
        assert!(numbered_outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>(bc|b)c){1,3}d"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert_eq!(named_outcome.group_count, 2);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "word".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn wider_ranged_repeat_grouped_backtracking_heavy_search_reports_short_branch_spans() {
        let outcome = literal_match(
            PatternRef::Str("a((bc|b)c){1,3}d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 5)), Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn wider_ranged_repeat_grouped_backtracking_heavy_fullmatch_backtracks_to_long_branch() {
        let outcome = literal_match(
            PatternRef::Str("a((bc|b)c){1,3}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbccd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 7)));
        assert_eq!(outcome.group_spans, vec![Some((3, 6)), Some((3, 5))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_wider_ranged_repeat_grouped_backtracking_heavy_fullmatch_reports_third_repetition() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>(bc|b)c){1,3}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbcbccd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 9)));
        assert_eq!(outcome.group_spans, vec![Some((5, 8)), Some((5, 7))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn wider_ranged_repeat_grouped_backtracking_heavy_fullmatch_reports_no_match() {
        let outcome = literal_match(
            PatternRef::Str("a((bc|b)c){1,3}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcccd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn compile_accepts_open_ended_quantified_group_alternation_backtracking_heavy_cases() {
        let numbered_outcome = compile(PatternRef::Str("a((bc|b)c){1,}d"), 0).unwrap();
        assert_eq!(numbered_outcome.status, CompileStatus::Compiled);
        assert_eq!(numbered_outcome.normalized_flags, FLAG_UNICODE);
        assert_eq!(numbered_outcome.group_count, 2);
        assert!(numbered_outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>(bc|b)c){1,}d"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert_eq!(named_outcome.group_count, 2);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "word".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn open_ended_quantified_group_alternation_backtracking_heavy_search_reports_short_branch_spans(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a((bc|b)c){1,}d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 5)), Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn open_ended_quantified_group_alternation_backtracking_heavy_fullmatch_backtracks_to_long_branch(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a((bc|b)c){1,}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbccd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 7)));
        assert_eq!(outcome.group_spans, vec![Some((3, 6)), Some((3, 5))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_open_ended_quantified_group_alternation_backtracking_heavy_fullmatch_reports_fourth_repetition(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>(bc|b)c){1,}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbcbcbcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 10)));
        assert_eq!(outcome.group_spans, vec![Some((7, 9)), Some((7, 8))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn open_ended_quantified_group_alternation_backtracking_heavy_fullmatch_reports_no_match() {
        let outcome = literal_match(
            PatternRef::Str("a((bc|b)c){1,}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcccd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn compile_accepts_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_cases(
    ) {
        let numbered_outcome = compile(PatternRef::Str("a((bc|b)c){2,}d"), 0).unwrap();
        assert_eq!(numbered_outcome.status, CompileStatus::Compiled);
        assert_eq!(numbered_outcome.normalized_flags, FLAG_UNICODE);
        assert_eq!(numbered_outcome.group_count, 2);
        assert!(numbered_outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>(bc|b)c){2,}d"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert_eq!(named_outcome.group_count, 2);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "word".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn broader_range_open_ended_quantified_group_alternation_backtracking_heavy_search_reports_lower_bound_short_branch_spans(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a((bc|b)c){2,}d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcbcdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 8)));
        assert_eq!(outcome.group_spans, vec![Some((5, 7)), Some((5, 6))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn broader_range_open_ended_quantified_group_alternation_backtracking_heavy_fullmatch_backtracks_to_long_branch(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a((bc|b)c){2,}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abccbcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 7)));
        assert_eq!(outcome.group_spans, vec![Some((4, 6)), Some((4, 5))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_fullmatch_reports_fourth_repetition(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>(bc|b)c){2,}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbcbcbcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 10)));
        assert_eq!(outcome.group_spans, vec![Some((7, 9)), Some((7, 8))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn broader_range_open_ended_quantified_group_alternation_backtracking_heavy_fullmatch_rejects_below_lower_bound(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a((bc|b)c){2,}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn compile_accepts_broader_range_wider_ranged_repeat_grouped_backtracking_heavy_cases() {
        let numbered_outcome = compile(PatternRef::Str("a((bc|b)c){1,4}d"), 0).unwrap();
        assert_eq!(numbered_outcome.status, CompileStatus::Compiled);
        assert_eq!(numbered_outcome.normalized_flags, FLAG_UNICODE);
        assert_eq!(numbered_outcome.group_count, 2);
        assert!(numbered_outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>(bc|b)c){1,4}d"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert_eq!(named_outcome.group_count, 2);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "word".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn broader_range_wider_ranged_repeat_grouped_backtracking_heavy_search_reports_short_branch_spans(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a((bc|b)c){1,4}d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 5)), Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn broader_range_wider_ranged_repeat_grouped_backtracking_heavy_search_reports_long_branch_spans(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a((bc|b)c){1,4}d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabccdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 7)));
        assert_eq!(outcome.group_spans, vec![Some((3, 6)), Some((3, 5))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn broader_range_wider_ranged_repeat_grouped_backtracking_heavy_fullmatch_backtracks_to_short_final_branch(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a((bc|b)c){1,4}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abccbcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 7)));
        assert_eq!(outcome.group_spans, vec![Some((4, 6)), Some((4, 5))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_broader_range_wider_ranged_repeat_grouped_backtracking_heavy_fullmatch_reports_fourth_repetition(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>(bc|b)c){1,4}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbccbccbcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 12)));
        assert_eq!(outcome.group_spans, vec![Some((9, 11)), Some((9, 10))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn broader_range_wider_ranged_repeat_grouped_backtracking_heavy_fullmatch_rejects_overflow() {
        let outcome = literal_match(
            PatternRef::Str("a((bc|b)c){1,4}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbcbcbcbcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn quantified_alternation_search_reports_lower_bound_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b|c){1,2}d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzacdz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 5)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_quantified_alternation_fullmatch_reports_second_repetition_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b|c){1,2}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("acbd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 4)));
        assert_eq!(outcome.group_spans, vec![Some((2, 3))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn compile_accepts_broader_range_quantified_alternation_cases() {
        let numbered_outcome = compile(PatternRef::Str("a(b|c){1,3}d"), 0).unwrap();
        assert_eq!(numbered_outcome.status, CompileStatus::Compiled);
        assert_eq!(numbered_outcome.normalized_flags, FLAG_UNICODE);
        assert_eq!(numbered_outcome.group_count, 1);
        assert!(numbered_outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b|c){1,3}d"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
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
    fn compile_accepts_open_ended_quantified_alternation_cases() {
        let numbered_outcome = compile(PatternRef::Str("a(b|c){1,}d"), 0).unwrap();
        assert_eq!(numbered_outcome.status, CompileStatus::Compiled);
        assert_eq!(numbered_outcome.normalized_flags, FLAG_UNICODE);
        assert_eq!(numbered_outcome.group_count, 1);
        assert!(numbered_outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>b|c){1,}d"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
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
    fn compile_accepts_open_ended_quantified_group_alternation_cases() {
        let numbered_outcome = compile(PatternRef::Str("a(bc|de){1,}d"), 0).unwrap();
        assert_eq!(numbered_outcome.status, CompileStatus::Compiled);
        assert_eq!(numbered_outcome.normalized_flags, FLAG_UNICODE);
        assert_eq!(numbered_outcome.group_count, 1);
        assert!(numbered_outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>bc|de){1,}d"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
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
    fn compile_accepts_nested_open_ended_quantified_group_alternation_cases() {
        let numbered_outcome = compile(PatternRef::Str("a((bc|de){1,})d"), 0).unwrap();
        assert_eq!(numbered_outcome.status, CompileStatus::Compiled);
        assert_eq!(numbered_outcome.normalized_flags, FLAG_UNICODE);
        assert_eq!(numbered_outcome.group_count, 2);
        assert!(numbered_outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<outer>(bc|de){1,})d"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
        assert_eq!(named_outcome.group_count, 2);
        assert_eq!(
            named_outcome.named_groups,
            vec![NamedGroup {
                name: "outer".to_string(),
                index: 1,
            }]
        );
    }

    #[test]
    fn compile_accepts_broader_range_open_ended_quantified_group_alternation_cases() {
        let numbered_outcome = compile(PatternRef::Str("a(bc|de){2,}d"), 0).unwrap();
        assert_eq!(numbered_outcome.status, CompileStatus::Compiled);
        assert_eq!(numbered_outcome.normalized_flags, FLAG_UNICODE);
        assert_eq!(numbered_outcome.group_count, 1);
        assert!(numbered_outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>bc|de){2,}d"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
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
    fn compile_accepts_broader_range_wider_ranged_repeat_quantified_group_alternation_cases() {
        let numbered_outcome = compile(PatternRef::Str("a(bc|de){1,4}d"), 0).unwrap();
        assert_eq!(numbered_outcome.status, CompileStatus::Compiled);
        assert_eq!(numbered_outcome.normalized_flags, FLAG_UNICODE);
        assert_eq!(numbered_outcome.group_count, 1);
        assert!(numbered_outcome.named_groups.is_empty());

        let named_outcome = compile(PatternRef::Str("a(?P<word>bc|de){1,4}d"), 0).unwrap();
        assert_eq!(named_outcome.status, CompileStatus::Compiled);
        assert_eq!(named_outcome.normalized_flags, FLAG_UNICODE);
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
    fn quantified_alternation_fullmatch_reports_third_repetition_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b|c){1,3}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abbbd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 5)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn quantified_alternation_open_ended_fullmatch_reports_fourth_repetition_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(b|c){1,}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 6)));
        assert_eq!(outcome.group_spans, vec![Some((4, 5))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_quantified_alternation_open_ended_search_reports_lower_bound_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b|c){1,}d"),
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
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn quantified_group_alternation_open_ended_search_reports_lower_bound_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a(bc|de){1,}d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 5))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_quantified_group_alternation_open_ended_fullmatch_reports_fourth_repetition_capture_span(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>bc|de){1,}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("adededed"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 8)));
        assert_eq!(outcome.group_spans, vec![Some((5, 7))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn quantified_group_alternation_open_ended_fullmatch_reports_invalid_branch_as_no_match() {
        let outcome = literal_match(
            PatternRef::Str("a(bc|de){1,}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abed"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn nested_open_ended_quantified_group_alternation_search_reports_lower_bound_capture_spans() {
        let outcome = literal_match(
            PatternRef::Str("a((bc|de){1,})d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 5)), Some((3, 5))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_nested_open_ended_quantified_group_alternation_fullmatch_reports_outer_and_inner_spans(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<outer>(bc|de){1,})d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbcded"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 8)));
        assert_eq!(outcome.group_spans, vec![Some((1, 7)), Some((5, 7))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn nested_open_ended_quantified_group_alternation_fullmatch_reports_no_match() {
        let outcome = literal_match(
            PatternRef::Str("a((bc|de){1,})d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbcdede"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn broader_range_open_ended_quantified_group_alternation_search_reports_lower_bound_capture_span(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(bc|de){2,}d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcbcdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 8)));
        assert_eq!(outcome.group_spans, vec![Some((5, 7))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_broader_range_open_ended_quantified_group_alternation_fullmatch_reports_fourth_repetition_capture_span(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>bc|de){2,}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("adededed"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 8)));
        assert_eq!(outcome.group_spans, vec![Some((5, 7))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn broader_range_open_ended_quantified_group_alternation_fullmatch_rejects_below_lower_bound() {
        let outcome = literal_match(
            PatternRef::Str("a(bc|de){2,}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn broader_range_wider_ranged_repeat_quantified_group_alternation_search_reports_lower_bound_capture_span(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(bc|de){1,4}d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 5))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_broader_range_wider_ranged_repeat_quantified_group_alternation_fullmatch_reports_upper_bound_capture_span(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>bc|de){1,4}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbcdeded"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 10)));
        assert_eq!(outcome.group_spans, vec![Some((7, 9))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn broader_range_wider_ranged_repeat_quantified_group_alternation_fullmatch_rejects_overflow() {
        let outcome = literal_match(
            PatternRef::Str("a(bc|de){1,4}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbcbcbcbcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn quantified_alternation_backtracking_heavy_fullmatch_backtracks_to_longer_second_branch() {
        let outcome = literal_match(
            PatternRef::Str("a(b|bc){1,2}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abbcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 5)));
        assert_eq!(outcome.group_spans, vec![Some((2, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn quantified_alternation_backtracking_heavy_fullmatch_backtracks_to_longer_first_branch() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>b|bc){1,2}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 5)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn quantified_alternation_backtracking_heavy_fullmatch_reports_no_match() {
        let outcome = literal_match(
            PatternRef::Str("a(b|bc){1,2}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abccd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn quantified_alternation_nested_branch_search_reports_inner_branch_spans() {
        let outcome = literal_match(
            PatternRef::Str("a((b|c)|de){1,2}d"),
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
    fn quantified_alternation_nested_branch_fullmatch_preserves_prior_inner_capture_span() {
        let outcome = literal_match(
            PatternRef::Str("a((b|c)|de){1,2}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abded"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 5)));
        assert_eq!(outcome.group_spans, vec![Some((2, 4)), Some((1, 2))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_quantified_alternation_nested_branch_fullmatch_reports_named_outer_span() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<word>(b|c)|de){1,2}d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("adebd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 5)));
        assert_eq!(outcome.group_spans, vec![Some((3, 4)), Some((3, 4))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn quantified_alternation_conditional_search_reports_optional_absent_groups() {
        let outcome = literal_match(
            PatternRef::Str("a((b|c){1,2})?(?(1)d|e)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzaezz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 4)));
        assert_eq!(outcome.group_spans, vec![None, None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn quantified_alternation_conditional_fullmatch_reports_outer_and_inner_spans() {
        let outcome = literal_match(
            PatternRef::Str("a((b|c){1,2})?(?(1)d|e)"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 4)));
        assert_eq!(outcome.group_spans, vec![Some((1, 3)), Some((2, 3))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_quantified_alternation_conditional_search_reports_named_outer_lastindex() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<outer>(b|c){1,2})?(?(outer)d|e)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzaccdzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 6)));
        assert_eq!(outcome.group_spans, vec![Some((3, 5)), Some((4, 5))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn wider_ranged_repeat_grouped_alternation_conditional_search_reports_absent_groups() {
        let outcome = literal_match(
            PatternRef::Str("a((bc|de){1,3})?(?(1)d|e)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzaezz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 4)));
        assert_eq!(outcome.group_spans, vec![None, None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn wider_ranged_repeat_grouped_alternation_conditional_fullmatch_reports_outer_and_inner_spans()
    {
        let outcome = literal_match(
            PatternRef::Str("a((bc|de){1,3})?(?(1)d|e)"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcded"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 6)));
        assert_eq!(outcome.group_spans, vec![Some((1, 5)), Some((3, 5))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_wider_ranged_repeat_grouped_alternation_conditional_search_reports_named_outer_lastindex(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<outer>(bc|de){1,3})?(?(outer)d|e)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcbcdedzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 10)));
        assert_eq!(outcome.group_spans, vec![Some((3, 9)), Some((7, 9))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn broader_range_wider_ranged_repeat_grouped_alternation_conditional_search_reports_absent_groups(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a((bc|de){1,4})?(?(1)d|e)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzaezz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 4)));
        assert_eq!(outcome.group_spans, vec![None, None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn broader_range_wider_ranged_repeat_grouped_alternation_conditional_fullmatch_reports_upper_bound_outer_and_inner_spans(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a((bc|de){1,4})?(?(1)d|e)"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcdededed"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 10)));
        assert_eq!(outcome.group_spans, vec![Some((1, 9)), Some((7, 9))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_broader_range_wider_ranged_repeat_grouped_alternation_conditional_search_reports_named_outer_lastindex(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<outer>(bc|de){1,4})?(?(outer)d|e)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzabcdedededzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 12)));
        assert_eq!(outcome.group_spans, vec![Some((3, 11)), Some((9, 11))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn broader_range_wider_ranged_repeat_grouped_alternation_conditional_fullmatch_rejects_overflow(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a((bc|de){1,4})?(?(1)d|e)"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbcbcbcbcd"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::NoMatch);
        assert_eq!(outcome.span, None);
        assert!(outcome.group_spans.is_empty());
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn open_ended_quantified_group_alternation_conditional_search_reports_absent_groups() {
        let outcome = literal_match(
            PatternRef::Str("a((bc|de){1,})?(?(1)d|e)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzaezz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 4)));
        assert_eq!(outcome.group_spans, vec![None, None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn open_ended_quantified_group_alternation_conditional_fullmatch_reports_outer_and_inner_spans()
    {
        let outcome = literal_match(
            PatternRef::Str("a((bc|de){1,})?(?(1)d|e)"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbcded"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 8)));
        assert_eq!(outcome.group_spans, vec![Some((1, 7)), Some((5, 7))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_open_ended_quantified_group_alternation_conditional_search_reports_named_outer_lastindex(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<outer>(bc|de){1,})?(?(outer)d|e)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzadedededzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 10)));
        assert_eq!(outcome.group_spans, vec![Some((3, 9)), Some((7, 9))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn broader_range_open_ended_quantified_group_alternation_conditional_search_reports_absent_groups(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a((bc|de){2,})?(?(1)d|e)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzaezz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 4)));
        assert_eq!(outcome.group_spans, vec![None, None]);
        assert_eq!(outcome.lastindex, None);
    }

    #[test]
    fn broader_range_open_ended_quantified_group_alternation_conditional_fullmatch_reports_outer_and_inner_spans(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a((bc|de){2,})?(?(1)d|e)"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("abcbcded"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((0, 8)));
        assert_eq!(outcome.group_spans, vec![Some((1, 7)), Some((5, 7))]);
        assert_eq!(outcome.lastindex, Some(1));
    }

    #[test]
    fn named_broader_range_open_ended_quantified_group_alternation_conditional_search_reports_named_outer_lastindex(
    ) {
        let outcome = literal_match(
            PatternRef::Str("a(?P<outer>(bc|de){2,})?(?(outer)d|e)"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzadedededzz"),
            0,
            None,
        )
        .unwrap();

        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.span, Some((2, 10)));
        assert_eq!(outcome.group_spans, vec![Some((3, 9)), Some((7, 9))]);
        assert_eq!(outcome.lastindex, Some(1));
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
    fn nested_group_alternation_search_matches_second_branch_and_reports_capture_spans() {
        let outcome = literal_match(
            PatternRef::Str("a((b|c))d"),
            FLAG_UNICODE,
            MatchMode::Search,
            PatternRef::Str("zzacdzz"),
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
    fn named_nested_group_alternation_fullmatch_reports_outer_lastindex() {
        let outcome = literal_match(
            PatternRef::Str("a(?P<outer>(?P<inner>b|c))d"),
            FLAG_UNICODE,
            MatchMode::Fullmatch,
            PatternRef::Str("acd"),
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
        let expanded = expand_literal_replacement_template_str(r"\g<0>x", "abc", &[], &[]).unwrap();
        assert_eq!(expanded, "abcx");
    }

    #[test]
    fn replacement_template_expands_group_1_reference_for_grouped_literal_case() {
        let expanded =
            expand_literal_replacement_template_str(r"\1x", "abc", &[Some("abc")], &[]).unwrap();
        assert_eq!(expanded, "abcx");
    }

    #[test]
    fn replacement_template_expands_named_group_reference_for_named_group_case() {
        let expanded = expand_literal_replacement_template_str(
            r"<\g<word>>",
            "abc",
            &[Some("abc")],
            &[("word", "abc")],
        )
        .unwrap();
        assert_eq!(expanded, "<abc>");
    }

    #[test]
    fn replacement_template_expands_nested_group_references() {
        let expanded = expand_literal_replacement_template_str(
            r"\1-\2-\g<outer>-\g<inner>",
            "abd",
            &[Some("b"), Some("b")],
            &[("outer", "b"), ("inner", "b")],
        )
        .unwrap();
        assert_eq!(expanded, "b-b-b-b");
    }

    #[test]
    fn replacement_template_rejects_unsupported_backslash_forms() {
        assert_eq!(
            expand_literal_replacement_template_str(r"\1x", "abc", &[], &[]),
            None
        );
        assert_eq!(
            expand_literal_replacement_template_str("\\", "abc", &[], &[]),
            None
        );
        assert_eq!(
            expand_literal_replacement_template_str(r"\g<word>", "abc", &[], &[]),
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
    fn nested_capture_find_spans_reports_repeated_matches_and_capture_spans() {
        let outcome =
            nested_capture_find_spans_str("a((b))d", FLAG_UNICODE, "zabdabdx", 1, Some(7));
        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.pos, 1);
        assert_eq!(outcome.endpos, 7);
        assert_eq!(
            outcome.matches,
            vec![
                CapturedMatchSpan {
                    span: (1, 4),
                    group_spans: vec![Some((2, 3)), Some((2, 3))],
                },
                CapturedMatchSpan {
                    span: (4, 7),
                    group_spans: vec![Some((5, 6)), Some((5, 6))],
                },
            ]
        );
    }

    #[test]
    fn nested_capture_find_spans_reports_named_nested_capture_spans() {
        let outcome = nested_capture_find_spans_str(
            "a(?P<outer>(?P<inner>b))d",
            FLAG_UNICODE,
            "zabdabdx",
            1,
            Some(7),
        );
        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.pos, 1);
        assert_eq!(outcome.endpos, 7);
        assert_eq!(
            outcome.matches,
            vec![
                CapturedMatchSpan {
                    span: (1, 4),
                    group_spans: vec![Some((2, 3)), Some((2, 3))],
                },
                CapturedMatchSpan {
                    span: (4, 7),
                    group_spans: vec![Some((5, 6)), Some((5, 6))],
                },
            ]
        );
    }

    #[test]
    fn conditional_group_exists_no_else_find_spans_reports_repeated_matches_and_capture_spans() {
        let outcome = conditional_group_exists_no_else_find_spans_str(
            "a(b)?c(?(1)d)",
            FLAG_UNICODE,
            "zzabcdaczz",
            2,
            Some(8),
        );
        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.pos, 2);
        assert_eq!(outcome.endpos, 8);
        assert_eq!(
            outcome.matches,
            vec![
                CapturedMatchSpan {
                    span: (2, 6),
                    group_spans: vec![Some((3, 4))],
                },
                CapturedMatchSpan {
                    span: (6, 8),
                    group_spans: vec![None],
                },
            ]
        );
    }

    #[test]
    fn conditional_group_exists_no_else_find_spans_rejects_other_conditional_shapes() {
        let empty_else = conditional_group_exists_no_else_find_spans_str(
            "a(b)?c(?(1)d|)",
            FLAG_UNICODE,
            "zzabcdzz",
            0,
            None,
        );
        assert_eq!(empty_else.status, MatchStatus::Unsupported);

        let alternation = conditional_group_exists_no_else_find_spans_str(
            "a(b)?c(?(1)(de|df))",
            FLAG_UNICODE,
            "zabcdex",
            0,
            None,
        );
        assert_eq!(alternation.status, MatchStatus::Unsupported);

        let nested = conditional_group_exists_no_else_find_spans_str(
            "a(b)?c(?(1)(?(1)d))",
            FLAG_UNICODE,
            "zzabcdzz",
            0,
            None,
        );
        assert_eq!(nested.status, MatchStatus::Unsupported);
    }

    #[test]
    fn conditional_group_exists_find_spans_reports_repeated_matches_and_capture_spans() {
        let outcome = conditional_group_exists_find_spans_str(
            "a(b)?c(?(1)d|e)",
            FLAG_UNICODE,
            "zzabcdacezz",
            2,
            Some(9),
        );
        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.pos, 2);
        assert_eq!(outcome.endpos, 9);
        assert_eq!(
            outcome.matches,
            vec![
                CapturedMatchSpan {
                    span: (2, 6),
                    group_spans: vec![Some((3, 4))],
                },
                CapturedMatchSpan {
                    span: (6, 9),
                    group_spans: vec![None],
                },
            ]
        );
    }

    #[test]
    fn conditional_group_exists_find_spans_rejects_other_conditional_shapes() {
        let no_else = conditional_group_exists_find_spans_str(
            "a(b)?c(?(1)d)",
            FLAG_UNICODE,
            "zzabcdzz",
            0,
            None,
        );
        assert_eq!(no_else.status, MatchStatus::Unsupported);

        let empty_else = conditional_group_exists_find_spans_str(
            "a(b)?c(?(1)d|)",
            FLAG_UNICODE,
            "zzabcdzz",
            0,
            None,
        );
        assert_eq!(empty_else.status, MatchStatus::Unsupported);

        let empty_yes_else = conditional_group_exists_find_spans_str(
            "a(b)?c(?(1)|e)",
            FLAG_UNICODE,
            "zzacezz",
            0,
            None,
        );
        assert_eq!(empty_yes_else.status, MatchStatus::Unsupported);

        let alternation = conditional_group_exists_find_spans_str(
            "a(b)?c(?(1)(de|df)|(eg|eh))",
            FLAG_UNICODE,
            "zabcdegx",
            0,
            None,
        );
        assert_eq!(alternation.status, MatchStatus::Unsupported);

        let nested = conditional_group_exists_find_spans_str(
            "a(b)?c(?(1)(?(1)d|e)|f)",
            FLAG_UNICODE,
            "zzabcdzz",
            0,
            None,
        );
        assert_eq!(nested.status, MatchStatus::Unsupported);
    }

    #[test]
    fn conditional_group_exists_nested_find_spans_reports_repeated_matches_and_capture_spans() {
        let outcome = conditional_group_exists_nested_find_spans_str(
            "a(b)?c(?(1)(?(1)d|e)|f)",
            FLAG_UNICODE,
            "zzabcdacfzz",
            2,
            Some(11),
        );
        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.pos, 2);
        assert_eq!(outcome.endpos, 11);
        assert_eq!(
            outcome.matches,
            vec![
                CapturedMatchSpan {
                    span: (2, 6),
                    group_spans: vec![Some((3, 4))],
                },
                CapturedMatchSpan {
                    span: (6, 9),
                    group_spans: vec![None],
                },
            ]
        );
    }

    #[test]
    fn conditional_group_exists_nested_find_spans_rejects_other_conditional_shapes() {
        let plain_two_arm = conditional_group_exists_nested_find_spans_str(
            "a(b)?c(?(1)d|e)",
            FLAG_UNICODE,
            "zzabcdzz",
            0,
            None,
        );
        assert_eq!(plain_two_arm.status, MatchStatus::Unsupported);

        let alternation = conditional_group_exists_nested_find_spans_str(
            "a(b)?c(?(1)(de|df)|(eg|eh))",
            FLAG_UNICODE,
            "zzabcdezz",
            0,
            None,
        );
        assert_eq!(alternation.status, MatchStatus::Unsupported);

        let nested_no_branch = conditional_group_exists_nested_find_spans_str(
            "a(b)?c(?(1)|(?(1)e|f))",
            FLAG_UNICODE,
            "zzabczz",
            0,
            None,
        );
        assert_eq!(nested_no_branch.status, MatchStatus::Unsupported);
    }

    #[test]
    fn conditional_group_exists_alternation_find_spans_reports_repeated_matches_and_capture_spans()
    {
        let outcome = conditional_group_exists_alternation_find_spans_str(
            "a(b)?c(?(1)(de|df)|(eg|eh))",
            FLAG_UNICODE,
            "zabcdeacehx",
            1,
            Some(10),
        );
        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.pos, 1);
        assert_eq!(outcome.endpos, 10);
        assert_eq!(
            outcome.matches,
            vec![
                CapturedMatchSpan {
                    span: (1, 6),
                    group_spans: vec![Some((2, 3)), Some((4, 6)), None],
                },
                CapturedMatchSpan {
                    span: (6, 10),
                    group_spans: vec![None, None, Some((8, 10))],
                },
            ]
        );
    }

    #[test]
    fn conditional_group_exists_alternation_find_spans_rejects_other_conditional_shapes() {
        let plain_two_arm = conditional_group_exists_alternation_find_spans_str(
            "a(b)?c(?(1)d|e)",
            FLAG_UNICODE,
            "zzabcdzz",
            0,
            None,
        );
        assert_eq!(plain_two_arm.status, MatchStatus::Unsupported);

        let no_else = conditional_group_exists_alternation_find_spans_str(
            "a(b)?c(?(1)(de|df))",
            FLAG_UNICODE,
            "zzabcdezz",
            0,
            None,
        );
        assert_eq!(no_else.status, MatchStatus::Unsupported);

        let nested = conditional_group_exists_alternation_find_spans_str(
            "a(b)?c(?(1)(?(1)d|e)|f)",
            FLAG_UNICODE,
            "zzabcdzz",
            0,
            None,
        );
        assert_eq!(nested.status, MatchStatus::Unsupported);
    }

    #[test]
    fn conditional_group_exists_quantified_find_spans_reports_repeated_matches_and_capture_spans() {
        let outcome = conditional_group_exists_quantified_find_spans_str(
            "a(b)?c(?(1)d|e){2}",
            FLAG_UNICODE,
            "zzabcddaceezz",
            2,
            Some(11),
        );
        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.pos, 2);
        assert_eq!(outcome.endpos, 11);
        assert_eq!(
            outcome.matches,
            vec![
                CapturedMatchSpan {
                    span: (2, 7),
                    group_spans: vec![Some((3, 4))],
                },
                CapturedMatchSpan {
                    span: (7, 11),
                    group_spans: vec![None],
                },
            ]
        );
    }

    #[test]
    fn conditional_group_exists_quantified_find_spans_rejects_other_conditional_shapes() {
        let plain_two_arm = conditional_group_exists_quantified_find_spans_str(
            "a(b)?c(?(1)d|e)",
            FLAG_UNICODE,
            "zzabcdzz",
            0,
            None,
        );
        assert_eq!(plain_two_arm.status, MatchStatus::Unsupported);

        let alternation = conditional_group_exists_quantified_find_spans_str(
            "a(b)?c(?(1)(de|df)|(eg|eh)){2}",
            FLAG_UNICODE,
            "zzabcdfdfzz",
            0,
            None,
        );
        assert_eq!(alternation.status, MatchStatus::Unsupported);

        let nested = conditional_group_exists_quantified_find_spans_str(
            "a(b)?c(?(1)(?(1)d|e)|f){2}",
            FLAG_UNICODE,
            "zzabcdabcdzz",
            0,
            None,
        );
        assert_eq!(nested.status, MatchStatus::Unsupported);
    }

    #[test]
    fn conditional_group_exists_empty_else_find_spans_reports_repeated_matches_and_capture_spans() {
        let outcome = conditional_group_exists_empty_else_find_spans_str(
            "a(b)?c(?(1)d|)",
            FLAG_UNICODE,
            "zzabcdaczz",
            2,
            Some(8),
        );
        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.pos, 2);
        assert_eq!(outcome.endpos, 8);
        assert_eq!(
            outcome.matches,
            vec![
                CapturedMatchSpan {
                    span: (2, 6),
                    group_spans: vec![Some((3, 4))],
                },
                CapturedMatchSpan {
                    span: (6, 8),
                    group_spans: vec![None],
                },
            ]
        );
    }

    #[test]
    fn conditional_group_exists_empty_else_find_spans_rejects_other_conditional_shapes() {
        let no_else = conditional_group_exists_empty_else_find_spans_str(
            "a(b)?c(?(1)d)",
            FLAG_UNICODE,
            "zzabcdzz",
            0,
            None,
        );
        assert_eq!(no_else.status, MatchStatus::Unsupported);

        let alternation = conditional_group_exists_empty_else_find_spans_str(
            "a(b)?c(?(1)(de|df)|)",
            FLAG_UNICODE,
            "zabcdex",
            0,
            None,
        );
        assert_eq!(alternation.status, MatchStatus::Unsupported);
    }

    #[test]
    fn conditional_group_exists_empty_yes_else_find_spans_reports_repeated_matches_and_capture_spans(
    ) {
        let outcome = conditional_group_exists_empty_yes_else_find_spans_str(
            "a(b)?c(?(1)|e)",
            FLAG_UNICODE,
            "zzabcacezz",
            2,
            Some(8),
        );
        assert_eq!(outcome.status, MatchStatus::Matched);
        assert_eq!(outcome.pos, 2);
        assert_eq!(outcome.endpos, 8);
        assert_eq!(
            outcome.matches,
            vec![
                CapturedMatchSpan {
                    span: (2, 5),
                    group_spans: vec![Some((3, 4))],
                },
                CapturedMatchSpan {
                    span: (5, 8),
                    group_spans: vec![None],
                },
            ]
        );
    }

    #[test]
    fn conditional_group_exists_empty_yes_else_find_spans_rejects_other_conditional_shapes() {
        let empty_else = conditional_group_exists_empty_yes_else_find_spans_str(
            "a(b)?c(?(1)d|)",
            FLAG_UNICODE,
            "zzabcdzz",
            0,
            None,
        );
        assert_eq!(empty_else.status, MatchStatus::Unsupported);

        let fully_empty = conditional_group_exists_empty_yes_else_find_spans_str(
            "a(b)?c(?(1)|)",
            FLAG_UNICODE,
            "zzabczz",
            0,
            None,
        );
        assert_eq!(fully_empty.status, MatchStatus::Unsupported);

        let nested = conditional_group_exists_empty_yes_else_find_spans_str(
            "a(b)?c(?(1)|(?(1)e|f))",
            FLAG_UNICODE,
            "zzabczz",
            0,
            None,
        );
        assert_eq!(nested.status, MatchStatus::Unsupported);
    }

    #[test]
    fn escape_matches_expected_outputs() {
        assert_eq!(escape_str("a-b.c"), "a\\-b\\.c");
        assert_eq!(escape_bytes(b"a-b.c"), b"a\\-b\\.c");
    }
}
