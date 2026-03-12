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
