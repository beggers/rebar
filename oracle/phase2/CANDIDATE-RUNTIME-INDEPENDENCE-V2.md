# Candidate runtime independence, version 2

Reference: the frozen CPython 3.14.6 P0 correctness oracle, the complete
published overview 74, and the immutable version 1 candidate guard. This is a
source and policy freeze. It does not execute, qualify, or time a candidate.

The previous policy prevented an external matcher from being imported but also
blocked an independently written candidate's own native bridge and every real
sub-interpreter in the unchanged Python tests. Version 2 preserves the full
ban on Python `re`, `_sre`, third-party regular-expression engines,
cross-candidate implementations, process fallbacks, and network access. It
permits exactly one caller-selected first-party adapter and exactly that
adapter's separately fingerprinted native bridge and native engine.

Start every actual candidate worker with pinned CPython 3.14.6 using `-I -B
-S`. Authenticate the frozen guard while `re`, `_sre`, external engines, and
candidate modules are absent. Install the irreversible audit hook and import
finder before reading or importing an activated candidate. Read the chosen
native bridge and engine through independently pinned, no-follow descriptors;
verify device, inode, owner, file size, SHA-256, and stable identity. Permit
only the exact family-to-bridge mapping frozen in the machine contract. Bind
the chosen candidate as `sys.modules['re']`; expose only the data constant
`MAXGROUPS = 1073741823` from `re._constants`.

The unchanged original `subinterpreter_v2` suite contains 128 cases, creates
and destroys 11 genuine Python interpreters, and performs 394 case executions.
An actual run must explicitly scope interpreter creation to that suite,
authenticate and register each child's first program, and install a fresh
independent version 2 guard inside each child *before* importing the producer,
the selected candidate, its bridge, Python `re`, or `_sre`. Reject a missing,
substituted, unrestricted, unregistered, or unguarded child. Recreate the exact
first program from all three guard fingerprints, the selected family, both
verified native artifacts, the original interpreter owner, and a fresh
challenge. A child is not considered guarded merely because an audit event
says its program was dispatched: require the actual child to return its
challenge-bound attestation through an operating-system pipe after physically
installing its own guard and verifying its own bridge. Require all 11
distinct child identities and all 394 original case executions. Original
cleanup removes the candidate `re` and data-only `re._constants` aliases;
it never invents or restores a standard-library matcher. A source-only gate
creates no children.

Permit `os.fork` only during the original public
`ReTests.test_regression_gh94675` and at most once. Permit at most two
`rebar.correctness.clock` events only during the original
`ReTests.test_search_anchor_at_beginning`. These are required upstream
correctness operations, not a speed benchmark. Locale fixtures are obtained
only in a separate isolated reference process; do not permit a candidate
process or external matcher to supply them.

Preserve the original 13 suites, all 31,237 cases, all 73 mapped obligations,
and exactly 13 named private waivers. Keep the separate 8,244 extra cases,
50 signature cases, and the original large-input obligations independent. Do
not merge denominators, invent a pass, omit a case, use cached oracle answers,
or open the final 4,194,304-case speed-test proposal.

The safe `--self-test` and `--verify-frozen-context` commands require seven
independently supplied SHA-256 pins: the V2 source, protocol and contract and
all four actual published V74 graph owners. Repeat each command under a normal
environment and `env -i PATH=/usr/bin:/bin LC_ALL=C`. Each gate must verify
the complete original history and physically reject real hostile imports,
cross-family bridges, unscoped forks, clocks, interpreters, native-loader
events, subprocesses, and network operations. These synthetic controls never
import an actual candidate or touch native output.

Status: **source frozen only**. Runtime independence is **NOT ESTABLISHED**;
candidate matching, the guard's use on an actual candidate, and interpreter
execution are **NOT RUN**. Compatibility, speed, memory, confidence intervals,
and undefined behavior are **NOT MEASURED**. The final holdout is **NOT
OPENED**. No candidate is qualified and no winner is selected.
