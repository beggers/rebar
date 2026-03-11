//! Placeholder parser-core crate for `rebar`.
//!
//! This crate intentionally does not implement regex parsing yet. It only
//! exposes a tiny surface that later CPython-extension work can link against
//! while the compatibility harness and parser design are still being built out.

/// The pinned CPython compatibility line for the initial parser target.
pub const TARGET_CPYTHON_SERIES: &str = "3.12.x";

/// Minimal parser entrypoint placeholder for the future Rust implementation.
#[derive(Debug, Default, Clone, Copy, PartialEq, Eq)]
pub struct Parser;

impl Parser {
    /// Builds the placeholder parser handle.
    #[must_use]
    pub fn new() -> Self {
        Self
    }

    /// Returns the pinned CPython series this scaffold is meant to match.
    #[must_use]
    pub fn target_cpython_series(self) -> &'static str {
        TARGET_CPYTHON_SERIES
    }

    /// Placeholder parse hook for future extension integration.
    ///
    /// This returns an explicit error instead of fake parse data so follow-on
    /// work can evolve the real API without inheriting misleading semantics.
    pub fn parse(self, _pattern: &str) -> Result<ParsedPattern, ParseError> {
        Err(ParseError::Unimplemented)
    }
}

/// Future parser result placeholder.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ParsedPattern {
    _private: (),
}

/// Error surface exposed until real parser implementation work starts.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ParseError {
    /// The parser crate exists, but no regex parsing behavior is implemented yet.
    Unimplemented,
}

impl std::fmt::Display for ParseError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Unimplemented => f.write_str("rebar-core parser scaffold is not implemented yet"),
        }
    }
}

impl std::error::Error for ParseError {}
