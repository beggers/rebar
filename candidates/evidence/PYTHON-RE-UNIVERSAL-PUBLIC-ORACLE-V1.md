# Expanded Python regex compatibility test

Status: **FAIL. None of the three engines is a complete replacement.**

This is a newly generated public correctness test. It is not the historical
hidden final, and it performs no timing.

## Complete measured results

Pinned Python **3.14.6** independently supplies the expected results. Rust,
C, and Zig each execute in their own guarded process with external regex
packages, the standard-library regex engine, and the other candidates
blocked.

| From-scratch engine | Fresh public patterns | Checks | Mismatches | Result |
| --- | ---: | ---: | ---: | --- |
| Rust | 8,192 | 393,216 | 693 | FAIL |
| C | 8,192 | 393,216 | 368 | FAIL |
| Zig | 8,192 | 393,216 | 355 | FAIL |
| **Total** | **8,192 shared patterns** | **1,179,648** | **1,416** | **FAIL** |

The complete per-engine comparison counts are genuine; the table does not
claim that an all-candidate passing report exists. No engine crashes in a
completed comparison. No benchmark or held-out cases are read.

The fixed population comprises **16** independently generated grammar
families, **16** subject, Unicode, and buffer strata, and **32** seeded
examples per family and stratum. Each case contributes exactly **48**
observations across compiled and module calls, positional windows, exact
exception chains, replacements and callbacks, warning behavior, scanners,
zero-width progression, and match metadata.

## Genuine failure types

- Rust's recorded examples reveal incorrect evaluation order when a
  user-provided `__index__` is combined with an incompatible, released, or
  noncontiguous subject. Python exposes the index conversion and its side
  effects first.
- C and Zig disagree with Python when a newline is used inside a
  quote-parity lookahead ending in `$`; Python permits `$` before a final
  newline.
- C and Zig also lose Python's exact nested exception context and context
  suppression when a group name is defined twice.

Examples are bounded to the first **256** records per candidate. The complete
number of disagreements and the cryptographic digest of the complete
disagreement stream are recorded; omitted examples must not be mistaken for
passing cases.

| Evidence | SHA-256 |
| --- | --- |
| Frozen public-oracle source | `744876e5b8409b8d49982ccfb61d93a99f3e2d4fd64d0543b29b831bd26796a0` |
| Rust complete failure report | `2a02af3d1b6925aa3aa080a2576e4fd9fa3b1d9a123737f711eb55a866582f1b` |
| C complete failure report | `8391457aa874caf407bfa9d1629254f6148e2a2e4a3a70e5c86e72ee3e643ca2` |
| Zig complete failure report | `42940bd1824f5a10530bc951e5f1aa2ba00347b263453e155b47a77a034835ab` |

The preserved
[initial Zig-worker failure](PYTHON-RE-UNIVERSAL-V1-INITIAL-ZIG-WORKER-FAILURE.md)
is a separately diagnosed test-harness problem. It is not combined with,
substituted for, or hidden behind Zig's later complete **355-mismatch**
report.

## Reproduce the source and inspect every report

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/python_re_universal_public_oracle_v1.py --self-test

jq '{status, selected, cases, observations_per_case,
      observations_per_candidate, mismatches, comparison_complete}' \
  candidates/evidence/python-re-universal-public-oracle-v1-rust.json \
  candidates/evidence/python-re-universal-public-oracle-v1-vm.json \
  candidates/evidence/python-re-universal-public-oracle-v1-zig.json
```

The exclusive evidence files are preserved, not silently overwritten. The
larger public speed test, fresh one-use holdout, native-memory measurements,
and a replacement winner are **NOT MEASURED**.
