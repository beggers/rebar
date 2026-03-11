use rebar_core::{ParseError, Parser, TARGET_CPYTHON_SERIES};

#[test]
fn advertises_the_pinned_cpython_target() {
    let parser = Parser::new();

    assert_eq!(TARGET_CPYTHON_SERIES, "3.12.x");
    assert_eq!(parser.target_cpython_series(), "3.12.x");
}

#[test]
fn parse_entrypoint_is_explicitly_unimplemented() {
    let parser = Parser::new();

    assert_eq!(parser.parse("abc"), Err(ParseError::Unimplemented));
}
