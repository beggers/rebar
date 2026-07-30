# Candidate runtime independence, version 4

Version 4 is an immutable, first-party correction to the real version 3
subinterpreter false positive. The unchanged pinned CPython 3.14.6 does not
deliver cpython.PyInterpreterState_New, _interpreters.create, or
_interpreters.exec to a parent Python audit hook during genuine interpreter
creation, execution, or destruction. Any such parent event can be synthesized
with sys.audit. Version 4 therefore rejects all three event names rather than
claiming an invented creation event, argument tuple, or audit count.

Authenticate all three immutable version 3 files, all three immutable version 2
files, all three immutable version 5 producer files, the pinned public provider
source, and all three independently supplied version 4 owner pins. The version
4 RuntimePolicy subclasses the exact frozen version 3 policy. Its prepare_family
method remains the same immutable version 2 function with the same version 2
globals, filename, and source-authenticated child bootstrap expected by the
unchanged version 5 producer.

For the actual original subinterpreter_v2 suite, first authenticate the genuine
public provider, its public create and Interpreter.exec/close code identities,
the exact temporary version 5 guarded-create closure, and the built-in
_interpreters module. Install bounded, restorable first-party wrappers around
the genuine create, exec, and destroy builtins. Each builtin call must originate
from the exact live code object and globals of its independently pinned public
provider caller, on the owning suite thread, with the exact original keyword
arguments and approved lifecycle state. Direct candidate calls, alternate
frames, forged objects, repeated IDs, synthetic events, replayed operations,
cross-thread calls, stale IDs, invented wrappers, and unscoped operations fail.

A successful creation requires the genuine builtin return value to be an exact
nonnegative int and both independently authenticated native and public live
sets to increase by precisely that new ID. The version 5 wrapper must return
the exact public Interpreter instance for the same ID. Count the creation only
after all real conditions succeed; no audit event is required. Keep the original
immutable version 2, challenge-bound child bootstrap and unique real
operating-system attestation pipe. Authenticate 11 real child creations,
11 real child destructions, 394 unchanged original case executions, 11 real
bootstrap executions, and 11 real cleanup executions, for 416 actual successful
public/native execution calls. Restore the preexisting interpreter live set and
all original public and built-in descriptors even when execution fails.

The original denominator remains 31,237 cases across 13 original suites, with
13 named private waivers. The separately scoped 8,244 supplemental cases and
their independent obligations are not included in that denominator. Preserve
all first-party family, native-owner, anti-delegation, Python-engine exclusion,
network/process/benchmark isolation, and unopened-holdout requirements.

Run both --self-test and --verify-frozen-context with pinned CPython using
-I -B -S, ordinarily and under an empty environment, and supply all twelve
independent V4/V3/V2/V5 SHA-256 pins. These four source-only gates never import
a candidate, load candidate-native code, create an interpreter, execute a child,
start another process or thread, open a private root or archive, read a hidden
case or holdout, or measure performance.

The separate --prove-provider mode is explicitly authorized by its mode and all
twelve independent pins. It is never invoked by either source-only gate. If a
later controller explicitly invokes it after publication, it creates and
destroys exactly one genuine child through the pinned builtin, confirms the
exact pinned public-provider create code on the immediate caller frame, restores
the original builtin and live set, and reports the absence of all three named
Python audit events. Its first-party proof namespace is not represented as the
imported public provider, a candidate, or a completed original suite.

Status: SOURCE FROZEN ONLY. Actual guarded candidate matching, candidate
compatibility, runtime non-delegation, memory, undefined behavior, and
performance remain NOT RUN, NOT ESTABLISHED, or NOT MEASURED. The explicit
provider proof is NOT RUN by this source freeze. No candidate is qualified, the
expanded performance holdout remains NOT OPENED, and no winner is selected.
