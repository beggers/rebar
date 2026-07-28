# Restore an honest Python-to-Python public-type comparison

Status: **SOURCE FREEZE ONLY. The original public-type reference is
FALSIFIED for the way candidates are evaluated. The corrected two-process
reference is NOT RUN. Candidate matching must remain stopped.**

This is an additive correction to phase one. It does not remove, rename, skip,
or waive an original case. The frozen denominator remains **31,237 cases in 13
suites with 13 named private waivers**. The public-type suite remains exactly
**6,912** of those original cases, with its original matrix, source, and seed.
The separately published 50 callable-signature reference cases are still
separate and passing; they are not added to 31,237.

## What actually failed

The original baseline ran the public-type evaluator as a Python script. The
candidate runner imported the exact same evaluator under its normal module
name. Consequently, test-only classes were named differently before any regex
engine was compared:

```text
Original reference fixture: __main__.TextSubclass
Candidate fixture:         tools.independent_public_type_identity_serialization_v1.TextSubclass

Original reference fixture: __main__.BytesSubclass
Candidate fixture:         tools.independent_public_type_identity_serialization_v1.BytesSubclass
```

This difference is observable because the frozen evaluator deliberately records
the module of the input subclass. The exact false difference is:

```text
outcome.value.items[2].module
```

This is not an untested hypothesis. A real, isolated, pinned CPython 3.14.6
process, process ID 80, imported the actual frozen candidate gate, then used
that gate's own `import_suite_source` and the unmodified standard-library `re`
to repeat all **96** affected cases. Its standard-library answers matched all
96 historical Rust answers exactly and disagreed with all 96 script-context
reference answers solely at the test fixture's module name. No candidate or
external regex engine was imported. No additional reference worker, candidate
worker, benchmark, evidence file, or holdout was started or created.

Exactly **48** cases use the genuine text subclass and **48** use the genuine
bytes subclass. Their original case identifiers are
`cache-pattern-type-separation/000` through
`cache-pattern-type-separation/095`. The compact identifier vector has
SHA-256 `a27fa99515fa1deef0253d49c5663a18821a07646cd8fadc5ebb5330d8cec35e`.
Using the frozen evaluator's canonical JSON format, including its one trailing
newline, the same identifier vector has SHA-256
`df43bd52adb112c0fde2bfe24a45200ca2ac30a9c41dfdc5716e3e81cbe19ce0`.

The unchanged 96-case source matrix has canonical SHA-256
`09b5d7cb665af227b8d6c733c795d68f9a1e22c62956b9d64105a9234af6abca`.
The original script-context reference records have canonical SHA-256
`df849727d5aa74cbec19950c2d56764bd592404b76c49abe87418bccd3a5013a`.
Both the actual named-context standard reference and all corresponding
historical Rust records have the identical canonical SHA-256
`587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad`.

For the first original case, `/000`, the canonical original reference record
is `33d63c67211bba811706bef2457230573cd13b498642c5ba0fa27b2e5091688c`.
The canonical named-context standard-library and historical Rust records are
both `7d8752048b7a3520b2657a21c3fe03722a507e0914d777404f16ffeec60d2292`.
The canonical complete Rust mismatch is
`3ec02cbb18243fd1f7a170146c22c82c00560a8b46447b9f87f2b1fb2e5130bd`.
All canonical hashes in this paragraph include the evaluator's one trailing
newline.

The frozen public evaluator is
`tools/independent_public_type_identity_serialization_v1.py`, SHA-256
`7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20`.
The actual candidate-facing gate is
`tools/run_frozen_p0_candidate_v1.py`, SHA-256
`c8378cd59a3b4dfaf75609c5b06f5a5ec20114d428e8e06ccc0f12ceec2076b8`.
The full original public matrix is
`c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123`.
The original seed is `6077977430793212465`.

## Preserve the baseline and every genuine candidate failure

Preserve the previous, two-process baseline instead of overwriting it:

```text
experiments/rust_public_practice_v1/public-type-identity-serialization-v1-shared-suite-v1.json.gz
8956c0b26e074d1537a47047062fb51e11d3f0196dc97ce4a6e24d2ae45128e2

experiments/rust_public_practice_v1/public-type-identity-serialization-v1-shared-suite-v1-publication-receipt.json
6a8ce4334d0b605483e0f78a909f620a8bcdd0e5ad8cdb4fae4960fc237132fd
```

The previous reference really did execute all 6,912 cases in two independent
processes, IDs 82 and 83. Its agreement was real **in script context**, but
did not test the same fixture context used for candidate evaluation. The
correction is not to pretend that either historical reference did not run.

Historical Rust remains **FAIL**, with 1,036 observed mismatches and 8,965
verified passes. Its newer independently built version remains **NOT RUN**
against the original matching suite. Historical C remains **FAIL**, with
1,230 mismatches and 7,325 verified passes. Zig remains **FAIL**, with 1,764
mismatches and 3,711 verified passes.

In particular, the C candidate has a real, independent failure in every one
of the same 96 cases. Python considers the original pattern and an equal
string-subclass pattern equal while still using their distinct types as
compile-cache keys. The tested C candidate incorrectly reports unequal
patterns:

```text
outcome.value.items[1].value: expected true, actual false
```

The C case `/000` has canonical mismatch SHA-256
`63e4cd7d491fac94c70df35f5c83ba96f5fdc0aceb3d5d212b92e90d59575b34`.
Correcting a test class's module does not correct or waive this real semantic
failure. Zig's corresponding complete cache records were not independently
retained; whether the exact 96-case witness also applies to Zig is
**NOT ESTABLISHED**. Do not guess.

## Freeze the actual correction before running it

Run both future reference workers using the same frozen named-import route as
candidate evaluation:

```python
gate = importlib.import_module("tools.run_frozen_p0_candidate_v1")
spec = gate.suite_spec("public_types_v1")
source = gate.import_suite_source(spec)
matrix = source.build_matrix()
support = source.preload_support_modules()
records = [source.observe_case(case, standard_library_re, support)
           for case in matrix]
```

Each genuine worker must execute **all 6,912 original cases**, preserve the
exact matrix and published seed, and independently reproduce all 96
named-context cache records. The two worker process IDs must be distinct.
Their complete vectors must agree. They must import only the exact pinned
CPython standard `re`; no candidate, external matcher, holdout, timing, or
network is allowed.

Only a future, separately authorized `--record-reference` may create the
new compressed evidence and its independently durable receipt. Both paths are
exclusive, owner-only, no-follow, and individually file- and
directory-synchronized. A publication receipt's `PASS` means durable
publication only; the actual two-reference result is a separate field.

Before starting either worker, that future controller must first create an
exclusive, owner-only, mode-`0700` recovery directory under `/tmp`. Its
append-only, mode-`0600` journal is synchronized before each process attempt,
immediately after recording each real process ID, after retaining both
complete bounded process streams, after validation, and before publication.
Attempted, actually started, completed, and validated worker counts remain
separate. A failed or timed-out second worker must retain its real ID and
complete output alongside the successful first worker. If publishing a
receipt fails after its archive was published, the existing archive and its
durable private recovery record remain; nothing is overwritten or deleted.

## Four mandatory source-only gates

Use the exact independently frozen source, protocol, and machine-contract
SHA-256 values. Run the synthetic self-test and the complete read-only
context both in the ordinary environment and in a sterile environment:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/verify_owned_public_type_reference_context_v1.py --self-test --source-sha256 <source-sha256> --protocol-sha256 <protocol-sha256> --contract-sha256 <contract-sha256>

env -i PATH=/usr/bin:/bin LC_ALL=C /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/verify_owned_public_type_reference_context_v1.py --self-test --source-sha256 <source-sha256> --protocol-sha256 <protocol-sha256> --contract-sha256 <contract-sha256>

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/verify_owned_public_type_reference_context_v1.py --verify-frozen-context --source-sha256 <source-sha256> --protocol-sha256 <protocol-sha256> --contract-sha256 <contract-sha256>

env -i PATH=/usr/bin:/bin LC_ALL=C /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/verify_owned_public_type_reference_context_v1.py --verify-frozen-context --source-sha256 <source-sha256> --protocol-sha256 <protocol-sha256> --contract-sha256 <contract-sha256>
```

The synthetic self-test physically blocks filesystem access, writes, native
loading, subprocesses, imports, networking, threads, clocks, locks, signals,
and archive decompression. Its hostile probes also directly test the actual
CPython low-level aliases: built-in import, `_io` and `posix`, every available
`os.exec` path, `_posixsubprocess.fork_exec`, `_ctypes.dlopen`, the actual
extension loader's `create_module` and `exec_module`, `_imp.create_dynamic`,
`_imp.exec_dynamic`, `_socket`, and `_thread`. It injects simulated
process-start, malformed-second-worker,
timeout, archive-publication, and receipt-publication failures without
starting a process or writing a file. The complete recovery evidence and
distinct worker counts must survive each simulated failure. The self-test
must reject at least 200 independently mutated case, context, process, and
effect controls.

The read-only gate authenticates existing source owners, historical receipts,
and compressed evidence. It **never inflates** historical reference or
candidate archives. Source-only verification never starts the corrected
reference or imports a candidate.

Until a separately committed, pushed, and executed corrected two-process
baseline is independently authenticated, phase one remains **NOT COMPLETE**,
candidate matching is **NOT AUTHORIZED**, no candidate is qualified, the
4,194,304-case holdout is **NOT OPENED**, and performance, memory, and
undefined behavior are **NOT MEASURED**.
