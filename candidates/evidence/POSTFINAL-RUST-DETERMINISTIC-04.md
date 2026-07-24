# Direct Rust matching: correctness evidence

This is a correctness-qualified Rust architecture, not a performance result.
The original final remains failed and no new holdout was opened.

## What changed

Rust now examines its own compiled instructions once. It uses its own
straight-line matcher only for literals, character classes, boundaries,
anchors, captures, backreferences, and validated fixed-count repetitions.
The direct path allocates no choice or undo stacks. Branching, lookarounds,
variable repetitions, conditionals, atomic expressions, and every uncertain
program retain Rust's existing general matcher.

Both paths preserve Python's Unicode character representations,
case-folding, capture ordering, `lastindex`, zero-width progression, clipped
windows, final-newline behavior, and full-match semantics. The direct path
restores captures after an unsuccessful match. It does not call standard
Python `re`, `_sre`, another candidate, or an external regex library.

## Passing gates

| Gate | Checks | Result | Evidence SHA-256 |
| --- | ---: | --- | --- |
| Frozen matching and parser differential | 223,198 | PASS | `2e68ae9e61cbc1a4a4d5ecb63a4c1721b6f2e6512a402b20264c535550a604a6` |
| Family-bound public-object contract | 393 | PASS | `fa5a5bacf900e126736bbac4182fd1bb47c072258a3d6cfa0fbf256539cf35c2` |
| Observability, ownership, and tracing | 479 | PASS | `e1ec43e10ae32b78ddc27283b1ecc538b62848f3e1b4eed27d4c80cec4c95dea` |
| Complete frozen compatibility campaign | 22 stages | PASS | `2910654dba7260391dd482420448fa3c28f0784f77cfacbb616b3483404724b4` |
| Independently generated quote differential | 83,968 | PASS | `5dcd6f35395ea766f9d9ad0216625ae472162d6ed57d774271939ecfc5d8e1f2` |
| Rust release unit tests | 20 | PASS | Build-time test output; not a fabricated artifact |

The compatibility campaign includes the complete **4,494,555-comparison**
Unicode gate, official CPython tests, replacements and callbacks, native
boundaries, crash and resource safety, object ownership, public signatures,
and separately isolated standard-library comparisons. It explicitly excludes
every historical performance and hidden benchmark.

Current exact source and audit:

| File | SHA-256 |
| --- | --- |
| Rust matcher | `97e13d239ef9413b067e74bb81fcf18a1b81e1deea6a747bb28d706f11108746` |
| Rust native engine | `c6c09ae96e3a840dc7a62870b3f8c54f6ebc4d82537b319f77520175e84a3255` |
| Native Python bridge | `148f34b2ff70413dcd4268b9b4ba85bfa6e5da4e60d503d0a9e08901ca61d28c` |
| Original 76-control audit | `c2d4885c8161e366bd1e0e00e047ca832d09f1a11f936afcb47b312fbee7435a` |
| Additive quote-oracle source | `9827f47f9f155b68135b4e9a0c23b2a188f99e7f28d44d7146003d0bcad531d6` |

## Preserved rejected controls

A naive independent string scan incorrectly rejected the literal public type
name `_sre.SRE_Scanner`. This name reproduces CPython's observable scanner
type; it is not an import, dependency, execution call, or Python-regex
fallback. Preserve the complete
[failed naive-string control](rust-v8-rust-post-final-stage-04-deterministic-static-string-control-failure.json).

The first 393-case
[deep-contract diagnostic](../audits/RUST-V8-DEEP-CONTRACT-RUST-POST-FINAL-STAGE-04-DETERMINISTIC-VARIANT-DIAGNOSTIC.json.gz)
and the corresponding 479-case
[tracing diagnostic](rust-v8-observability-rust-post-final-stage-04-deterministic-variant-diagnostic.json.gz)
both had zero Python mismatches, but the preliminary deep report did not
explicitly identify the candidate family. Neither was accepted as a final
proof. Their stronger replacements bind `candidates.rust_candidate`, the
`RUST` family, the exact edge proof, current source, and loaded binaries.

## Reproduction

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

cargo test --manifest-path candidates/rust/Cargo.toml \
  --offline --release --target-dir /tmp/rebar-rust-target

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/rust_postfinal_quote_parity_stage04_oracle.py --self-test

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.audit_from_scratch --self-test
```

The complete immutable evidence is retained beside this report. Performance,
fresh hidden-case accuracy, final confidence intervals, final native memory,
and a final winner are **NOT MEASURED**.
