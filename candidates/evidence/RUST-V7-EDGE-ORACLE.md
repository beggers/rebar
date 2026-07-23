# Frozen post-v7 correctness edge oracle

The question is whether each from-scratch implementation behaves exactly like
CPython 3.14.6, not merely whether it passed the earlier frozen suites. This
correctness-only experiment freezes one **223,198-check** matrix before any
implementation is fixed and applies the same checks, seeds, and error
comparisons to CPython, Rust, Zig, C, and Python.

- Runner: [`tools/rust_v7_edge_oracle.py`](../../tools/rust_v7_edge_oracle.py).
- Frozen runner SHA-256:
  `fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca`.
- Oracle: CPython 3.14.6, Unicode 16.0.0, `C` character locale.
- Main seed: `2026072329`; Unicode sampling stride: `4099`.
- Full-plane Unicode in this particular run: **NOT MEASURED**. The runner's
  `--unicode-stride 1` option separately checks every Unicode codepoint against
  all four independently frozen CPython partition hashes.
- Performance, memory, benchmarks, and performance holdout: **NOT MEASURED**
  and **NOT ACCESSED**.

Every output records every mismatch, category, input, expected result, actual
result, exception, seed, source hash, bridge hash, and native-engine hash. JSON
evidence is compressed reproducibly with gzip level 9 and timestamp zero.
Lone Unicode surrogates are recorded losslessly as
`{"kind": "str", "surrogatepass_utf8_hex": "..."}`. Decoding the hex with
UTF-8 `surrogatepass` restores the exact original Python string. This happens
only when writing reports, after all cases have been compared and hashed, so
standard JSON tools can read every archive without changing any test or result.
The shared oracle-result SHA-256 is
`b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526` for
**every** implementation.

## Baseline

| Implementation | Module | Checks | Mismatches | Evidence |
| --- | --- | ---: | ---: | --- |
| CPython 3.14.6 | `re` | 223,198 | 0 | `rust-v7-edge-oracle-stdlib-baseline.json.gz` |
| Rust | `candidates.rust_candidate` | 223,198 | 24,462 | `rust-v7-edge-oracle-rust-baseline.json.gz` |
| Zig | `candidates.zig_candidate` | 223,198 | 5,281 | `rust-v7-edge-oracle-zig-baseline.json.gz` |
| C | `candidates.vm_candidate` | 223,198 | 52,655 | `rust-v7-edge-oracle-c-baseline.json.gz` |
| Python | `candidates.ast_candidate` | 223,198 | 52,151 | `rust-v7-edge-oracle-python-baseline.json.gz` |

These counts are correctness failures, **not speed measurements**. An
implementation must pass the complete, unchanged matrix before it is considered
a drop-in replacement.

Deterministic compressed evidence SHA-256:

- CPython: `392cda0f0e17a2ec020d445a594958e46f2521ff951b4341c99f6fb5af5e722f`.
- Rust: `93fdaf429c2db09f831a16e9190f6ada6d5cab025fa1fb277c446b6d06132bae`.
- Zig: `80a0e9292f3231000748d2b2d5a3de95ee72d76d9c489c23d0f51f1ec64144a2`.
- C: `54f204265237f7c86776df32adacfb6a123e50b3a3bcd29846bb23c6a8f4b343`.
- Python: `3c6f1cd044771bddcad7d0026764835d54cbaf85bfe6999a9037c8133f9d5db6`.

The Rust baseline is independently tied to original source SHA-256
`f529040ab9082eedf80ba9c39b407def3edf9520a9a1fc8d70cb6e8399f7723f`,
native-engine SHA-256
`6a0716543ebe49dad44f9d1fa0cd7a8ee3de8e8cf4e2f6e4ad077211a655c161`,
and native-bridge SHA-256
`a86f2b6e917edd97136cb72a158ff8130c839ecebcaf19ef4b455442db9b66d2`.
These are hashes of the unchanged public baseline only. Linker-interposed or
private overlay experiments must independently record their actually loaded
engine and source; they must not reuse public baseline hashes as provenance.

## What is tested

- The original 74,652-check independent gate: all 256 byte values and buffer
  types; Unicode boundaries and case-folding; `search`, `match`, `fullmatch`,
  `findall`, `finditer`, scanners, captures, empty-match progression,
  replacement, reentrant callbacks, parser errors, and seeded cases.
- All 69,260 independently frozen C0-whitespace observations: the four control
  characters U+001C–U+001F; all 24 patterns; five global flag combinations; all
  nine text, byte, subclass, and buffer sources; and all 12 bound or module
  operations. This includes CPython's counterintuitive scoped-flag behavior
  and both scoped alternations.
- The exact 19,600-case bytes-identity matrix across 16 patterns, 12 subject
  lengths, five source types, seven APIs, captures, scanners, and windows; an
  additional 6,216 whole-span identity controls.
- All 224 independently frozen hash, cache, purge, callback, and `KeyError`
  observations; exact `inspect.signature` for `split`, `sub`, and `subn`.
- Every combination of four zero-width assertions, nine quantifiers, five
  contexts, text or bytes, and four flags. All 1,440 CPython-valid patterns
  run their compilation and seven matching operations; rejected compilation
  remains an explicit failure for **each** promised operation.
- All 36 independently generated quantified lookaround and boundary controls;
  all 384 seeded memory-safety grammar scenarios; exact previously failing
  inverted-window `match` and scanner cases.
- All 14,783 independent pattern, match, text, buffer, mutation, copy,
  read-only, warning, indexing, signature, hashing, and object-identity cases.
  Only nondeterministic hexadecimal addresses in Python error representations
  are canonicalized to `0xADDRESS`; values, types, traces, error messages, and
  substantive identity are preserved.
- The complete 20,480-case, 16-family independent parser-grammar fixture. It
  is regenerated from its exact seed, checked against frozen SHA-256
  `f2b0e9bfaa7dedacdf201e66499019f30860050b75dd722310f27bb1c79e35dd`, and
  compared without omitting invalid patterns or error offsets.
- All 1,198 cases in the existing public-object and native-boundary surface
  probe. Its raw expected and actual error observations are preserved.

## Reproduce

Run each command from the repository root using the pinned Python:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B tools/rust_v7_edge_oracle.py --module re --output candidates/evidence/rust-v7-edge-oracle-stdlib-baseline.json.gz
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B tools/rust_v7_edge_oracle.py --module candidates.rust_candidate --output candidates/evidence/rust-v7-edge-oracle-rust-baseline.json.gz
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B tools/rust_v7_edge_oracle.py --module candidates.zig_candidate --output candidates/evidence/rust-v7-edge-oracle-zig-baseline.json.gz
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B tools/rust_v7_edge_oracle.py --module candidates.vm_candidate --output candidates/evidence/rust-v7-edge-oracle-c-baseline.json.gz
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B tools/rust_v7_edge_oracle.py --module candidates.ast_candidate --output candidates/evidence/rust-v7-edge-oracle-python-baseline.json.gz
```

A candidate with any mismatches intentionally returns exit status 1 **after**
writing its complete deterministic evidence. The CPython self-oracle returns
exit status 0. No benchmark, timing, performance ranking, external regex engine,
or holdout file is read.

Any report can also be checked with standard JSON tools:

```text
gzip -dc candidates/evidence/rust-v7-edge-oracle-zig-baseline.json.gz | jq -e .
```
