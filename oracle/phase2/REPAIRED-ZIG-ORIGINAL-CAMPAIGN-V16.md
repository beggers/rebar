# Corrected first-party Zig original correctness campaign V16

This freeze tests the corrected Zig implementation against every original
CPython correctness case. It does not claim that Zig passes before the actual
independently authorized campaign has run.

The unchanged denominator is **31,237 original cases across 13 suites**. The
separate 8,244 differential cases stay separate. The frozen matrix has 73
original obligations, 34 source crosswalks, and exactly 13 named private
waivers. No cases are removed, replaced, estimated, or counted twice.

## Corrected first-party implementation

The candidate is built entirely from project-owned source:

- Zig parser, compiler, and execution engine:
  `candidates/zig/mini_regex.zig`, SHA-256
  `a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28`.
- First-party CPython bridge:
  `candidates/zig/variants/replacement_event_semantics_v1/py_bridge.c`, SHA-256
  `07337863f6b4a0e749a8d60b2e5704bb961e43dc09bfa85c238f0efa40d3583c`.
- First-party public Python compatibility layer:
  `candidates/zig/variants/public_adapter_semantics_v1/zig_candidate.py`,
  SHA-256
  `7129c63bdfd3c265a44541500238c26a8a5511f8932140de7d06bb49c13f588d`.

The completed V16 build produced two independent copies. The root-authorized
campaign uses the `reference-a` private artifacts only after validating the
completed public build and private-root receipts:

- Native engine: SHA-256
  `caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071`,
  108,888 bytes.
- Native bridge: SHA-256
  `59b2c21c220ec019338289e6c64dc73b820645cc273cb5100268ab770127d4fe`,
  138,104 bytes.

Static native audits contain no external regular-expression implementation,
CPython regular-expression engine, package-provided matcher, general Python
module importer, Python code loader, or cross-candidate engine. Exactly one
digest-bound bridge compatibility call may import the standard-library
`copyreg` helper; it is not a matching engine and does not authorize any other
import.

## Preserved prior observations

The historical Zig campaign actually observed at least **1,700 semantic
mismatches**, verified 4,607 passing cases, completed 12 of 13 suites, and had
one infrastructure failure. Its total mismatch count remains **NOT MEASURED**.
The prior publication receipt is authenticated as plaintext; its compressed
case archive is never opened by the source-only freeze.

## Strict runtime and recovery

Every actual suite runs in its own clean, isolated CPython 3.14.6 process.
The strict V4 runtime guard is installed before either native owner is prepared
and before the only first-party Zig candidate import. Native bridge and engine
owners must each contain exactly 14 authenticated identity fields. The original
subinterpreter suite must use its genuine provider boundaries: 11 interpreter
creations, 11 destructions, 394 case execution calls, 11 bootstrap calls, and
11 cleanup calls, for 416 actual calls in total. Parent Python audit hooks do
not receive interpreter creation events on the pinned interpreter; invented
audit events do not count.

The root-authorized controller preserves the exact original adapter, engine,
and bridge inodes using journaled hard-link backups, activates corrected
mode-0600 repository-device copies, attempts all 13 suites even after failures,
and restores all three original owner identities before publishing complete
durable results. Timeouts, crashes, stderr, and every actual mismatch record
are preserved. A successful publication only proves durable publication;
candidate qualification remains false until every original and supplemental
gate is independently satisfied.

## Source-only boundary

`--render-contract`, `--verify-frozen-context`, and `--self-test` authenticate
only exact plaintext owners. They do not inspect the private root, execute the
build controller or runtime guard, import candidate code, activate native
objects, open an archive or holdout proposal, start a worker, run a benchmark,
change a file, or invoke Git. Hostile source-only controls must reject those
operations physically. Actual execution additionally requires explicit root
authorization, a matching already-committed and pushed freeze, and every
independent Python, goal, producer, guard, build, historical, source, and
native identity pin.

Corrected original matching: **NOT RUN**. Runtime non-delegation:
**NOT ESTABLISHED**. Candidate qualification: **NOT ESTABLISHED**. Holdout:
**NOT OPENED**. Speed, memory, and undefined behavior: **NOT MEASURED**.
Winner: **NOT SELECTED**.
