# Candidate runtime independence, version 3

This is an independently frozen correction to the original candidate guard.
It does not execute a candidate, create an interpreter, establish
compatibility, measure performance, or open the benchmark holdout.

The pinned CPython is 3.14.6. Its genuine public interpreter provider is
`concurrent.interpreters`. Creating a real interpreter emits
`cpython.PyInterpreterState_New`; the provider executes child source through
the real `concurrent.interpreters.Interpreter.exec` method. The old guard's
`_interpreters.create` and `_interpreters.exec` audit-event assumptions do
not establish either real operation. A user can also call `sys.audit` with
arbitrary text. Therefore, an audit-event name or generated child program,
by itself, is not proof that a real interpreter was created or that child
source was executed. The genuine creation event's argument tuple is **NOT
MEASURED** by this source freeze and must not be invented.

Version 3 authenticates and subclasses the complete, physically pinned
version 2 implementation. Its `prepare_family` method is the *same function*
with the *same version 2 globals, code filename, and child bootstrap source*.
This is necessary because the immutable version 5 producer independently
authenticates that exact version 2 identity. Neither predecessor is edited,
recompiled into a replacement policy, or weakened.

At the start of the original `subinterpreter_v2` suite, authenticate the
pinned public provider from its complete no-follow source, then verify the
exact version 5 guarded-create closure and its genuine original public
`create` function against independently compiled authenticated source. Wrap
that *then-current* version 5 closure; version 5 captured the real original
before beginning the suite. Accept a creation audit only while that
source-verified original public provider is on the genuine live call stack,
on the owning thread, and inside one bounded create operation. Confirm the
result against an actual, unique change to the independently verified native
and public live-interpreter sets. Synthetic `sys.audit`, guessed event
arguments, fabricated objects, duplicate IDs, stale children, alternate
provider functions, cross-thread events, and replayed creations cannot
establish a real child.

Authenticate the original public create function against the freshly compiled
pinned source, but bind the audit frame to that function's *actual live code
object*. Separately compiled, source-equal code is not the same runtime
object. Source-only controls explicitly prove and reject this distinction.

Wrap only the source-verified original public `Interpreter.exec` class
descriptor. Permit execution only for the exact live interpreter previously
created, uniquely registered, and bound to its immutable version 2 challenge,
canonical child source, and fresh operating-system attestation pipe. The
original method must actually return before any execution is counted.
The first call must install the original version 2 guard and prove it over
the real pipe before further child calls. Require 11 genuinely created and
destroyed interpreters, all 394 unchanged original case executions, 11 real
bootstrap calls, and 11 real cleanup calls: 416 actual public method
invocations. Restore the original class descriptor even when a case fails;
do not reinstall version 5's temporary create wrapper after the producer has
already restored the genuine original.

Native bridge and engine owners must each contain exactly the 14 fields
produced by the immutable version 5 producer. The family, role, canonical
absolute and relative paths, filename, SHA-256, file and duplicate sizes,
device, inode, permissions, effective owner, link count, and unloaded state
must match the already no-follow-authenticated version 2 prepared owners.
Reject all missing, extra, substituted, cross-family, or preloaded fields.
Continue to reject the Python regular-expression engine, `_sre`, external
engines, other candidates, fallback matching, unscoped native loading,
subprocesses, networking, unrestricted interpreter creation, and benchmarks.

The original correctness denominator remains 31,237 cases across 13 suites
with exactly 13 named private waivers. The separate 8,244-case supplement,
50 signature obligations, and large-input obligations remain separate and
must not be represented as completed by this source gate.

Run both `--self-test` and `--verify-frozen-context` using pinned CPython
with `-I -B -S`, both ordinarily and under an empty environment. Supply all
nine independent SHA-256 pins: the three version 3 files, all three immutable
version 2 files, and all three immutable version 5 producer files. The
source-only hostile controls must create no interpreter, start no candidate
or reference worker, load no native library, open no private build root or
compressed archive, sample no benchmark clock, and read no holdout.

Status: **SOURCE FROZEN ONLY**. Actual version 3 guarded children, actual
candidate matching, genuine runtime non-delegation, compatibility, memory,
performance, and undefined behavior are **NOT RUN**, **NOT ESTABLISHED**, or
**NOT MEASURED** as appropriate. No candidate is qualified. The expanded
performance holdout is **NOT OPENED**. No winner is selected.
