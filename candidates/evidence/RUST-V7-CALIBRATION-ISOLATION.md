# Rust practice-data isolation

The Rust optimization campaign must not use the independently held-back
performance cases to decide which Rust architecture to improve. Practice
results are not final results.

## Rejected original approach

The first practice tools called `tools.perf_v7.frozen()` and then filtered its
results. This was unsafe: `frozen()` generates both workload groups, reads the
entire expected-results file, and deserializes both groups before returning.
The original priority tool also decompressed and deserialized the complete
mixed-group performance summary before selecting its practice results.

The original archive is preserved, without a byte being changed, at
`candidates/evidence/rust-v7-calibration-priorities-rejected-mixed-loader.json.gz`.
Its SHA-256 is
`3ce4c876fab304dc474e3b77b57bd6d6f4ce545ad6d7097de3534e991291cba0`.
Its practice numbers were correct, but the procedure that obtained them was
not isolated. It must not be used to select or validate new architectures.

## Sealed practice fixture

`performance/v7/evidence/rust-calibration-fixture.jsonl.gz` contains exactly
10,312 practice cases, their Python-verified expected answers, their original
case positions, and the existing practice-only historical results. It contains
no held-back case or answer. Its SHA-256 is
`c9fb716b609bfd1b007482db251bc8095990ba7f571e5f041db0dbc6abf41bf5`.

`performance/v7/evidence/rust-calibration-fixture-manifest.json` records its
hash, uncompressed-content hash, original suite, runner and expected-data
hashes, the unchanged practice seed and protocol, the original practice
rankings, and zero generated or decoded held-back cases. Its SHA-256 is
`2ff780cd43ab4948a2af2f37e3d5dd3bbb69b9dd924385de1f2f3fc924dd276a`.

The one-time freezer executes only the original base-suite declarations whose
case identifiers begin with `cal.`. It loads the four additive suite sources
without importing or calling their parent full-workload generators, and calls
each additive generator only with `"calibration"`. It checks the original
expected-data stream for the practice-group marker **before** parsing an
answer as JSON. Held-back answer lines remain opaque bytes and are never
deserialized. The complete original expected-file hash is verified during that
single streaming freeze. Normal planning, self-tests, ranking and optimization
use only the sealed practice fixture and manifest.

The 624 selected practice cases, their original positions, all 260 workload
categories, and selection seed `1986072311` are unchanged. The existing
`candidates/evidence/rust-v7-calibration-plan.json` is not rewritten; its
SHA-256 remains
`8e3da72df3c69ad68c181574ad62ed6bf77e2e9cd9987111aa7accbec6901744`.

The rebuilt `candidates/evidence/rust-v7-calibration-priorities.json.gz`
reproduces all 10,312 original practice rows, 41,248 candidate practice
results, every workload group, every candidate ranking, and the original
summary and raw-data reference hashes. Unlike the rejected original, it is
derived entirely from the sealed practice fixture. Its SHA-256 is
`2e361fd891db0c85bf721e287cf0b368ff0725bb44d44ab660a9b10fba41ded9`.

These are historical practice observations. New Rust architecture performance
is **NOT MEASURED** until an explicitly authorized, independently
correctness-gated comparison is run.

## Exact Rust artifact verification

Before creating any timing output, the practice runner requires a passing
report from the committed independent compatibility oracle. For Rust the
report must contain each of these five roles exactly once:

- The actual public Python module.
- The actual loaded native Python bridge.
- The actual loaded Rust engine.
- The exact Rust engine source.
- The exact native bridge source.

Every path and SHA-256 must match the production file and the module actually
imported by the runner. Native engine and bridge paths must also appear in the
running process's mapped libraries. Missing, extra, duplicated, swapped,
stale, foreign, or changed artifacts fail before raw benchmark evidence can
be opened. The correctness report's source hash must match the current
committed oracle, not an earlier version.

## Reproduce the isolation checks

Use the frozen CPython 3.14.6 interpreter from the repository root:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  tools/rust_v7_calibration_pilot.py self-test

env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  tools/rust_v7_calibration_pilot.py plan --verify

env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  tools/rust_v7_calibration_priorities.py --self-test

env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  tools/rust_v7_calibration_priorities.py
```

Poisoned held-back records are deliberately invalid JSON: the checks pass only
if the decoder never receives them. A poisoned generator rejects every cohort
other than practice, and full-suite generation is a hard error. The native
checks independently reject missing roles, duplicated roles, swapped paths,
stale source hashes, and an engine different from the one that passed
compatibility. Both gzip archives have deterministic headers without a stored
filename or timestamp.

No Rust candidate is built, timed, or selected by these checks.
