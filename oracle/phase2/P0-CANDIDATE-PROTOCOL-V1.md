# Frozen Python compatibility test for independent replacements

This protocol is frozen before any candidate in this phase is imported,
built, timed, or tested. Its purpose is to answer one precise question: does
an independently implemented replacement reproduce the complete, published
CPython 3.14.6 compatibility standard?

The input is the published phase-one inventory
`oracle/phase1/p0-completeness-v1.json`, SHA-256
`cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f`.
Its independently verified baseline has exactly 13 ordered suites and 31,237
counted case executions. The inventory, original Python source, matrices,
seeds, all 11 archive and receipt families, all 73 public obligations, the
13 named private waivers, and the single genuine debug-build skip are not
changed by this protocol.

## The exact denominator

| Frozen Python suite | Counted candidate cases | Actual execution |
| --- | ---: | --- |
| Original CPython public tests | 151 | The original source-ordered tests and actual guarded native worker. The one genuine debug-build skip is reported, not counted as a pass. |
| General public matching | 864 | The frozen producer's actual matching and callback operations. |
| Scanner behavior | 1,024 | The frozen producer's actual scanner, pattern, and callback operations. |
| Ordinary buffer behavior | 768 | The frozen producer's actual memory and replacement operations. |
| Managed buffer lifetimes | 1,024 | The original buffer owner, callbacks, release events, and lifecycle records. |
| Verbose scanner comments | 2,854 | Every original scanner and tokenizer case, including real exceptions. |
| Public types and serialization | 6,912 | Every original type, cache, warning, flag, identity, and pickle case. |
| Substitution and nested buffers | 5,120 | Every original replacement, callback, nested buffer, and exception. |
| Changing buffer shapes | 10,240 | Every original outer and nested buffer shape, window, release, and error. |
| Full public surface | 1,376 | The original evaluator, including 64 real locale cases and 192 genuine locale transitions. |
| Real subinterpreters | 128 | The original cases in 11 real created and destroyed subinterpreters, with 394 actual interpreter executions and complete A/B/A, fresh-interpreter, and teardown records. |
| Python buffer exporters | 264 | The original PEP 688 exporters, actual acquisitions and releases, retained holders, callbacks, exceptions, and garbage collection. |
| Real shared-pattern threads | 512 | The original two genuinely simultaneous threads for each cohort: 32 starts, 32 joins, 1,024 thread-side case executions, and 2,176 actual regex operations. |
| **Total** | **31,237** | Every suite is required. |

The 32 thread metadata checks are already inside the 512 thread cases. The
three observations of each subinterpreter case are real lifecycle evidence,
not 384 additional counted cases. Nothing is silently deduplicated or added.

## Candidate ownership and isolation

Version one recognizes three actual, separately implemented native families:
`rust`, `c`, and `zig`. For each run, explicitly pin every selected Python
adapter, native engine, native Python bridge, and complete family-specific
source closure. C's engine and bridge are the same authenticated binary;
Rust's and Zig's are separate. Zig may load only its exact, hash-pinned owned
native library. The public family name `c` selects the independence audit's
`c_vm` family and the exact `candidates.vm_candidate` adapter. A future
language or independent engine requires its own
separately published protocol; changing a wrapper is not a new family.

Before importing a candidate, authenticate the complete phase-one baseline
using its actual frozen verifier. The independent static source audit is
`tools/audit_candidate_independence_v1.py`, SHA-256
`f18d9b99a3f11fdf20c47d6cb43cb353532c894ababbdaeb7088c14e397ae3b5`;
its protocol is `oracle/phase2/CANDIDATE-INDEPENDENCE-V1.md`, SHA-256
`a7ee45f0ea76ee7fedacc564c3122b7f37272d918ef28f1c527c9e8adf351292`.
The audit is static; it does not claim to prove actual runtime independence.
The public, scanner, and buffer categories additionally pin the exact
three-family controller `tools/independent_public_contract_v3.py`, SHA-256
`9a831571c81e542d7d43ae56aea271f8e6c69550173d97ae1c9f8213eef40bf3`.
Run each suite in its own pinned
`python3.14 -I -B` process. Before importing its adapter, install the frozen
original-V5 continuous identity-based matcher quarantine. It blocks calls to
the actual CPython regex functions and `_sre`, external regex engines,
sibling candidates, foreign native libraries, and subprocess delegation. It
authenticates the genuine selected bridge and source owners both before and
after each actual case. A support-module import is not falsely counted as
matching; an actual call into Python's regex engine fails the run.

The original upstream suite uses its unchanged, already frozen guarded
candidate worker. All other executable suites invoke the exact frozen
producer's matrix and observation functions, rather than substitute a
simulated fixture. In particular, real shared threads use
`_run_thread_cohort`, and Python exporters use the original `execute_case`
and complete event validator. The public-surface candidate path uses the
original V17 evaluator and V19's cycle-safe normalizer; the historical V19
`--candidate all` path is genuinely blocked and must never be used.

## One explicit, lossless subinterpreter identity projection

The genuine Python-reference subinterpreter rows assert
`candidate_imports == 0` and `stdlib_origin_verified == true`. A genuine
independent candidate cannot truthfully satisfy either reference-process
assertion. Its `__name__` and source origin also must identify its own
adapter. Copying those reference answers would be a forbidden fallback.

Consequently, version one preserves and compares every original case ID,
cohort, ordinal, full seed, variant, status, actual execution, locale result,
pinned-executable result, and complete matching observation. It projects
only the two reference-only top-level fields `candidate_imports` and
`stdlib_origin_verified`. They are replaced, not dropped, by independently
validated selected-candidate source, native bridge and engine hashes,
candidate-module identity, no-delegation evidence, real interpreter identity,
and genuine in-interpreter imports.

Preserve every observation value. Bijectively rename only the following
Python-implementation-specific observation labels:

| Original Python observation | Independent candidate observation |
| --- | --- |
| `stdlib_re_module` | `engine_module_name_verified` |
| `module_identity` | `engine_sysmodules_identity_verified` |
| `actual_stdlib_reimport` | `actual_engine_reimport` |
| `reimported_origin_verified` | `engine_reimported_origin_verified` |
| `stdlib_owner` | `engine_sysmodules_owner_verified` |
| `pattern_is_stdlib_pattern` | `pattern_is_engine_pattern` |
| `match_is_stdlib_match` | `match_is_engine_match` |

Every candidate-side value must verify its real independently owned module,
source, bridge, engine, pattern, or match. None may claim to own Python's
stdlib matcher. The complete original projected vector, encoded with the
authentic subinterpreter producer's compact ASCII JSON without a trailing
newline, is SHA-256
`cf5633c8dc1038d650603eee421371285d0e32f6446190ce728590f1f5c55021`.
No matching result, capture, warning, buffer, flag, error, cache, generic
type, callback, cross-interpreter operation, or cleanup is projected away.

The exact unmodified producer program is checked against its pinned source.
Each reference-only marker must occur exactly once before deterministic
candidate-owner substitution. A genuine candidate is loaded inside each real
interpreter. The three complete A/B/A observation vectors, all eight
fresh-interpreter cases, the real A-after-B-close observation, the real fresh
C observation, all 11 created and closed interpreter identities, all 394
`Interpreter.exec` calls, and every observation-pipe cleanup remain
mandatory. The complete original reference digest is reported separately;
a candidate digest is never falsely labeled as the stdlib reference digest.

## Evidence and failure

Authenticate both original reference vectors, their exact case IDs, their
producer-specific canonical digests, and their signed archives before
starting each corresponding candidate worker. Decode genuinely escaped lone
surrogates, reject duplicate JSON keys and non-finite numbers, and use the
original producer's digest conventions. The large managed-buffer archive and
the compact public-type, substitution, and shaped-buffer archives must be
decoded from their complete producer-owned streams; absent top-level records
cannot be invented.

Retain all candidate records, all original reference records, every mismatch,
the first failing case and exact seed, complete real standard-output and
standard-error streams, nonzero exit codes, signals, timeouts, and completed
thread or interpreter cleanup. A crash, incomplete suite, unsupported native
subinterpreter, forged owner, changed original source, failure to obtain two
genuine differently encoded locales, omitted record, or nonzero delegation
attempt makes the complete run fail. No candidate is correct unless every
one of the 13 suites actually completes and all 31,237 counted cases pass.

The source-only self-test performs no real file access, candidate import,
reference execution, subprocess, thread, subinterpreter, garbage collection,
clock sampling, benchmarking, or holdout access. It uses synthetic positive
and hostile controls for exact suite order, denominators, original skips,
duplicate or missing cases, seeds, digest changes, source ownership,
cross-family imports, the lossless subinterpreter projection, thread and
interpreter lifecycles, locale counts, complete streams, and truthful failure
classification.

## Current actual status

This commit freezes a test protocol, not a passing candidate. The genuinely
candidate-owned multi-interpreter worker required for the 128 subinterpreter
cases is **NOT IMPLEMENTED**. Therefore the version-one runner fails the
complete candidate gate before importing or executing any candidate. Frozen
producer routes and available helper functions are not completed candidate
results. No candidate can qualify until a separately committed and pushed
chunk implements and verifies the real in-interpreter route, and every one
of the 13 suites actually runs.

Performance, memory, the final expanded holdout, and a winner remain
**NOT MEASURED**. A passing correctness test does not authorize the holdout.
