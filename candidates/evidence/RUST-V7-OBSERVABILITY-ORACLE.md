# Rust V7: Python-visible behavior

The Rust implementation must do more than return the right matches. It must
also behave like Python's `re` when a program uses tracing, monitoring,
replacement callbacks, unusual arguments, recursive replacements, and objects
that must remain alive. This is a separate correctness test; it does not inspect
or measure benchmarks or holdout cases.

The [frozen test](../../tools/rust_v7_observability_oracle.py) compares two
independent copies of CPython 3.14.6 before testing the actual Rust module. Its
fixed seed is `2026072343`; its 479-case fixture has SHA-256
`1d5a84b9fe2213289d96126dab740d103958bd593b811b262238bfc57a4a5403`.

| Check | Cases | Result |
| --- | ---: | --- |
| Two independently run Python baselines | 479 each | Agree on every case |
| Rust compared with Python | 479 | 0 differences |
| Invalid native arguments and recovery | 34 | All pass |
| Deliberately disabled Python regex shortcuts | 13 | All remain disabled |
| Reproduced, rejected iterator-name false alarms | 2 | 0 actual differences |

The 479 cases consist of 192 replacement checks, 180 unusual public argument
checks, 16 tracing checks, 16 monitoring checks, eight recursive replacement
checks, three object-lifetime checks, and 64 reproducibly selected additional
cases. The monitoring checks run when CPython's `sys.monitoring` is available;
the archived Python 3.14.6 run confirms that it was available. Python-visible
callback events, exact exceptions, argument side effects, match results, and
recovery are compared. Private engine stack frames and internal iterator class
names are recorded only as diagnostics.

The first version of this check incorrectly treated Python's
`callable_iterator` and Rust's `_RustMatchIterator` as a compatibility
difference. Both iterators actually return the same matches, obey the same
iterator protocol, call custom argument conversions the same number of times,
and raise the same errors. The
[rejected-control archive](rust-v7-observability-rejected-iterator-control.json.gz)
preserves both false alarms, their complete baseline and Rust observations, and
the original investigation hashes.

The [manifest](rust-v7-observability-manifest.json.gz) records the complete
[first Python baseline](rust-v7-observability-stdlib-a.json.gz),
[second Python baseline](rust-v7-observability-stdlib-b.json.gz),
[479 actual Rust observations](rust-v7-observability-candidate.json.gz), and
[34 native-safety checks](rust-v7-observability-private-binders.json.gz). It
also records the exact five Rust source and loaded-native-file hashes and all
13 live tests proving that Python's built-in regex engine cannot be used as a
fallback.

Run these commands from the repository root using the pinned Python 3.14.6:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B tools/rust_v7_observability_oracle.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B tools/rust_v7_observability_oracle.py write
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B tools/rust_v7_observability_oracle.py verify
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B tools/rust_v7_observability_oracle.py candidate
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B tools/rust_v7_observability_oracle.py candidate \
  --edge-oracle candidates/evidence/rust-v7-edge-oracle-rust-corrected-v4.json.gz
```

`verify` checks the frozen case identities, every complete observation, every
archive hash, the original test source, the frozen five-file Rust provenance,
all poison tests, both explained false alarms, and deterministic gzip encoding.
It remains valid when later optimization replaces the original native files.
Plain `candidate` verifies the exact original production build.
`candidate --edge-oracle` accepts an optimized build only after an independent,
frozen 223,198-case test proves that its actual five production files are
correct. It then runs the same 479 Python-visible checks, 34 safety checks, and
13 no-fallback checks; it never substitutes a private engine. The self-test
also rejects missing, stale, duplicated, swapped, and incorrect correctness
evidence. Neither command reads or changes benchmark or holdout data.
Performance: **NOT MEASURED**.
