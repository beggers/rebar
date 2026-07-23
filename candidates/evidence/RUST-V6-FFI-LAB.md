# Rust Python-boundary correctness

This checks whether the from-scratch Rust regex engine behaves like Python
when results cross the Python/native boundary. It does not use an external
regex engine, read a performance holdout, or claim an overall speed result.

| Check | Cases | Result |
| --- | ---: | --- |
| Unmodified Python compared with itself | 546 | 546 passed |
| Original complete Rust boundary checkpoint | 738 | 736 passed; 2 failed |
| Corrected, independently loaded Rust bridge | 738 | 738 passed |
| Corrected production Rust bridge | 738 | 738 passed |
| Complete-holdout speed or ranking | — | NOT MEASURED |

The 738-case Rust gate consists of 354 separate Python-compatibility cases and
192 independently generated diagnostic inputs, each checked through both the
public Rust interface and the project's own direct native entry point. Every
check uses pinned CPython 3.14.6. The direct native entry point is the same
from-scratch Rust engine, not a second candidate or an external package.

## What the checks cover

The compatibility cases cover result and object identity, short and wide
Unicode strings, unmatched and named groups, literal-match result sharing,
strided and multidimensional buffers, mutable subjects, callback order and
exceptions, mutable callback return values, replacement escapes, hostile
user-defined hashing, public function errors and warnings, argument conversion,
cache clearing, scanners, iterators, and garbage-collected object lifetimes.

The test deliberately found two observable differences after thousands of
earlier checks had passed. Python keeps a subject-to-scanner or
subject-to-iterator reference cycle alive. The original Rust bridge collected
both cycles. All the objects are tracked by Python's garbage collector; the
difference is which subject references the scanner or iterator exposes to
cycle detection. Ordinary match-object cycles still have to be collectible.
The independently tested bridge changes only scanner and iterator reference
traversal and preserves the match behavior. Neither failure is waived or
removed.

The compressed evidence preserves all 546 self-oracle records, all 738 original
records, both original failures, reference and garbage-collector diagnostics,
all 738 successful independently loaded corrected records, and all 738
successful production records. The isolated correction uses the same matching
engine as the failing checkpoint, so it isolates the bridge fix. The final
production build contains a newer Rust matching engine; both old and new
engine fingerprints are preserved and the change is explicitly reported.

## Performance status

The diagnostic fixture contains 192 cases from 24 families, including fresh
versus reused Python bound methods, Python module calls, native entry points,
matching, splitting, replacement, captures, scanners, buffers, compilation,
and all four Unicode storage widths. These inputs are not the frozen
holdout.

Timing, memory, confidence intervals, overall ranking, and complete-holdout
performance are **NOT MEASURED** by this correctness-only checkpoint. When
timing is authorized, a result will be counted as more than 20% slower only
when its speedup is strictly below `5/6`: its running time then exceeds
`1.2` times Python's baseline. The laboratory self-tests both sides of this
boundary.

## Reproduce

Run from the repository root with the pinned Python:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONPATH=. "$PY" tools/rust_ffi_lab.py self-test \
  --output /tmp/rebar-rust-ffi-self-v1.json

PYTHONPATH=. "$PY" tools/rust_ffi_lab.py oracle-self \
  --output /tmp/rebar-rust-ffi-oracle-self-v1.json

PYTHONPATH=. "$PY" tools/rust_ffi_lab.py verify \
  --output /tmp/rebar-rust-ffi-production-v1.json

gzip -dc candidates/evidence/rust-v6-ffi-lab.json.gz | jq \
  '{self_oracle_checks, self_oracle_mismatches,
    candidate_checks, candidate_mismatches,
    isolated_corrected_mismatches,
    production_corrected_mismatches,
    timing, holdout_accessed, waivers}'
```

The complete reproducible code is
[the independent Rust Python-boundary laboratory](../../tools/rust_ffi_lab.py).
The complete original and corrected observations are
[the compressed, fingerprinted boundary evidence](rust-v6-ffi-lab.json.gz).
