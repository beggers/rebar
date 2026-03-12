use rebar_core::{
    compile, literal_match, CompileStatus, MatchMode, MatchStatus, PatternRef,
    TARGET_CPYTHON_SERIES,
};

#[test]
fn advertises_the_pinned_cpython_target() {
    assert_eq!(TARGET_CPYTHON_SERIES, "3.12.x");
}

#[test]
fn compile_classifies_the_supported_literal_slice() {
    let outcome = compile(PatternRef::Str("abc"), 0).unwrap();

    assert_eq!(outcome.status, CompileStatus::Compiled);
    assert_eq!(outcome.normalized_flags, 32);
    assert!(outcome.supports_literal);
    assert_eq!(outcome.warning, None);
}

#[test]
fn literal_match_reports_a_span_for_supported_searches() {
    let outcome = literal_match(
        PatternRef::Str("abc"),
        32,
        MatchMode::Search,
        PatternRef::Str("zzabczz"),
        0,
        None,
    )
    .unwrap();

    assert_eq!(outcome.status, MatchStatus::Matched);
    assert_eq!(outcome.pos, 0);
    assert_eq!(outcome.endpos, 7);
    assert_eq!(outcome.span, Some((2, 5)));
}

#[test]
fn numbered_backreference_compile_and_search_are_supported() {
    let compile_outcome = compile(PatternRef::Str("(ab)\\1"), 0).unwrap();

    assert_eq!(compile_outcome.status, CompileStatus::Compiled);
    assert_eq!(compile_outcome.normalized_flags, 32);
    assert!(!compile_outcome.supports_literal);
    assert_eq!(compile_outcome.group_count, 1);
    assert!(compile_outcome.named_groups.is_empty());

    let match_outcome = literal_match(
        PatternRef::Str("(ab)\\1"),
        32,
        MatchMode::Search,
        PatternRef::Str("zzababzz"),
        0,
        None,
    )
    .unwrap();

    assert_eq!(match_outcome.status, MatchStatus::Matched);
    assert_eq!(match_outcome.span, Some((2, 6)));
    assert_eq!(match_outcome.group_spans, vec![Some((2, 4))]);
}
