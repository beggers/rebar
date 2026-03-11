# Initial Regex Syntax Scope

## Purpose

This document narrows the parser-side compatibility target for `rebar`. It refines [`docs/spec/drop-in-re-compatibility.md`](docs/spec/drop-in-re-compatibility.md) by defining which CPython regex syntax families the first implementation must accept, reject, and diagnose compatibly.

The scope here is the pattern parser and compile-time validation path, not the full matching engine or the replacement-template grammar used by `sub` and `subn`.

## Initial Reference Target

- The first bug-for-bug parser target is the CPython `re` pattern syntax accepted by the `3.12.x` family.
- `3.12.x` is the initial pin because it is a stable version family, it already includes modern `re` syntax such as atomic groups and possessive quantifiers, and it avoids treating future syntax drift as part of the first milestone by default.
- Assumption: patch releases within `3.12.x` should not intentionally fork the regex grammar in user-visible ways. If differential testing finds a real patch-level difference, `rebar` should pin the exact tested patch release in follow-up work instead of averaging the behavior.
- Cross-version compatibility beyond `3.12.x` remains project scope, but it is deferred until the first correctness harness can prove one version cleanly.

## What "Compatible With CPython" Means At The Parser Boundary

At the parser boundary, compatibility means:

- The same pattern/flag combinations compile successfully or fail.
- Compile-time warnings and exceptions appear at the same user-visible boundary, with the same practical meaning, for the same inputs.
- Group numbering, group naming, backreference resolution, scoped-flag handling, and compile-time width checks follow CPython's rules.
- `str` and `bytes` patterns follow CPython's separate acceptance rules rather than a merged or simplified grammar.
- Internal Rust data structures may differ from CPython internals, but any parser decision that changes public `re` behavior counts as a compatibility issue.

This matters to user-visible `re` behavior because parser decisions determine whether `compile()` succeeds, which flags a `Pattern` carries, how groups are numbered and named, whether later `Match` objects expose the expected metadata, and which diagnostics users see when patterns are invalid.

## Initial Syntax Support Map

| Construct family | Initial status | Scope notes |
| --- | --- | --- |
| Pattern text model | Required in first milestone | Support both `str` and `bytes` patterns with CPython-compatible acceptance and rejection rules. Do not normalize them into one grammar. |
| Literal text and escapes | Required in first milestone | Support literal characters plus compile-time handling for escaped metacharacters and standard escape forms such as octal, hex, Unicode, named-character, and category escapes exactly where CPython `3.12` accepts them. |
| Character classes and sets | Required in first milestone | Support bracket classes, negated sets, ranges, escaped members, shorthand classes inside sets, and the compile-time warnings/errors around ambiguous or invalid set syntax that CPython surfaces. |
| Concatenation and alternation | Required in first milestone | Preserve CPython precedence and branch structure for ordinary sequence parsing and `|` alternation. |
| Quantifiers | Required in first milestone | Support greedy, lazy, and possessive repetition forms, including `*`, `+`, `?`, `{m}`, `{m,}`, `{m,n}`, and the corresponding `?`/`+` suffixes where CPython `3.12` allows them. Match CPython's validation of malformed repeat syntax and nested-repeat errors. |
| Grouping forms | Required in first milestone | Support capturing groups, named groups, non-capturing groups, comment groups, inline-flag groups, scoped-flag groups, and atomic groups. Duplicate-name handling and invalid-group syntax must follow CPython `3.12`. |
| Assertions and anchors | Required in first milestone | Support start/end anchors, word-boundary assertions, lookahead, and lookbehind. Compile-time validation for lookbehind width must match CPython `3.12`. |
| Backreferences and conditionals | Required in first milestone | Support numeric and named backreferences plus conditional subpatterns that CPython `re` accepts. Invalid forward or malformed references must fail compatibly. |
| Flag syntax | Required in first milestone | Support API-level flags and inline flag forms, including global `(?aiLmsux)`-style declarations and scoped flag groups. Invalid flag combinations, placement, and text-model restrictions must match CPython `3.12`. |
| Verbose-mode tokenization | Required in first milestone | Whitespace/comment stripping under `re.X` and inline verbose scopes is parser behavior and must match CPython, including the cases where whitespace remains significant. |
| Parser diagnostics | Required in first milestone | Error and warning categories, trigger conditions, and message shape are part of the compatibility target where users can observe them through `re.compile()` and related APIs. |

## Deferred But Still In Project Scope

These areas should not be invented away, but they do not need to be fully settled by this document:

- Exact patch-level pinning inside `3.12.x` if differential testing discovers a material regex-parser difference between patch releases.
- Cross-version drift between `3.12.x` and later CPython releases such as `3.13+`.
- The replacement-template grammar for `sub` and `subn`, which is user-visible but not part of the pattern parser itself.
- Private parse-tree or helper-module details exposed through CPython internals such as `sre_parse` or `re._parser`, unless later tasks decide they must be treated as compatibility surfaces.
- Locale-sensitive matching semantics that do not change parse acceptance, while still preserving parser acceptance rules for the corresponding flags.

## Explicit Non-Goals For The First Syntax Document

- Do not add regex constructs that CPython `re` rejects.
- Do not broaden the syntax toward PCRE, Oniguruma, or Matthew Barnett's third-party `regex` module.
- Treat constructs such as recursion, subroutine calls, branch-reset groups, callouts, and `\\p{...}` Unicode-property escapes as rejected syntax unless a CPython version pin proves otherwise.
- Do not promise compatibility for private CPython parser object layouts in this document.

## Assumptions To Validate Later

- This document assumes CPython `3.12.x` is the right first parser target for the whole project.
- This document assumes atomic groups and possessive quantifiers belong in the first compatibility milestone because they are part of CPython `3.12` syntax, not optional extensions.
- This document assumes parser diagnostics are compatibility-relevant even when exact wording may require later differential tests to pin down more precisely.

Later correctness work should turn these assumptions into executable differential tests rather than leaving them as prose.
