# Rust public profile V2 source freeze

This is **fresh public practice only**. It is not a final result, hidden
comparison, holdout, qualification, winner selection, or external-engine wrapper.
The original independently written Rust engine and pinned official CPython
3.14.6 remain separate isolated processes. All 416 public cases must match
exactly before timing, profiler execution, or output-directory creation.

The immutable V1 run passed that complete correctness gate and recorded four
balanced rounds comprising 1,664 paired public observations. Native collection
then stopped because `gprofng` printed its own single-line announcement to
standard output before the worker's otherwise valid canonical JSON:

```
Creating experiment directory stdlib.er (Process ID: 91) ...
{"archive_files_read":0,...,"pid":91,...,"status":"PASS"}
```

The original V1 source, protocol, manifest, failed run directory, complete
collector stream, and all paired timing rows remain unchanged. V2 authenticates
their exact hashes and the failed directory/file ownership identities before
loading the previously frozen first-party implementation. It never consumes a
fixture, hidden benchmark, holdout, external package, or another regex engine.

V2 accepts exactly one printable ASCII announcement for the expected engine and
relative `<engine>.er` experiment, followed by exactly one canonical JSON
document. The announcement's positive, minimally encoded decimal process ID
must equal the actual worker document's integer process ID. Missing or repeated
announcements, substituted engines or paths, mismatched process IDs, duplicate
JSON keys, noncanonical JSON, extra output, Unicode, control characters, CRLF,
and trailing data are rejected. The complete raw collector stream and the
separately normalized worker JSON are preserved as distinct exclusive artifacts.

Use the isolated pinned interpreter for strictly read-only source checks:

```
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B /home/dev-user/src/rebar/tools/rust_public_profile_v2.py --verify-source
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B /home/dev-user/src/rebar/tools/rust_public_profile_v2.py --self-test
```

Those modes start no processes, sample no clocks, import no candidates, invoke
no profilers, load no native engines, access no archives or holdout cases, and
create or modify no files. They authenticate the real V1 failure and exercise
hundreds of hostile path, announcement, and JSON controls.

Only the root agent may run the experiment, after these three V2 source files
have been committed and pushed. It must use an entirely fresh V2 output root:

```
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B /home/dev-user/src/rebar/tools/rust_public_profile_v2.py --run --output experiments/rust_public_profile_v2/public-run-001/summary.json
```

No V1 session is reused, overwritten, deleted, or cleaned. The final sealed
comparison remains **NOT FROZEN / NOT GENERATED / NOT OPENED**. Final speed,
compatibility qualification, and winner selection remain **NOT MEASURED**.
