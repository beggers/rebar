# Activate only source-verified native Python replacements

The project is building independent, from-scratch replacements for Python's
`re`. A compiled file left in the repository does not prove which source
produced it. In particular, the historical C extension differs from its first
recorded fresh build, and that first build's treatment of versioned native
symbols was falsified. Neither binary, nor the version-one symbol audit, may
qualify a candidate.

An initial, source-only reviewed activation draft had SHA-256
`7b10c1b8ac7b1b62557c1ba655c2ac6bd95b10772ceaa764797a398a0de54372`.
Although its ordinary and isolated synthetic controls passed, independent
review falsified its recovery claim: a process killed after the first atomic
native replacement and before publication of the activation report and
receipt could not invoke its report-dependent restore command. That draft is
**rejected**, not a qualifying source. The corrected protocol below requires
an independently pinned recovery journal and a durable, per-file staged-inode
intention before each replacement; crash recovery needs neither an activation
report nor receipt.

This protocol freezes
[`../../tools/activate_verified_native_candidate_v1.py`](../../tools/activate_verified_native_candidate_v1.py)
**before** any activation. Activation is possible only after the corrected
version-two native build recorder and protocol have separately been committed,
pushed, and actually produced and durably published two matching, genuinely
independent source builds for the exact selected family. A source-only
synthetic self-test does not perform or authorize a build, activation, import,
test, benchmark, or holdout.

## Required published build

The only acceptable build recorder is
[`../../tools/reproduce_phase2_native_builds_v2.py`](../../tools/reproduce_phase2_native_builds_v2.py),
SHA-256
`e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796`.
Its only acceptable protocol is
[`NATIVE-SOURCE-BUILDS-V2.md`](NATIVE-SOURCE-BUILDS-V2.md), SHA-256
`f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603`.
The caller must supply, rather than guess, the actual subsequently published
version-two report and receipt hashes, source owners, build label, private
build root, and the observed hashes and exact byte sizes of each native file.

The activator authenticates all of the following **before** touching any
existing candidate binary:

- Its exact caller-pinned source and this protocol, the immutable objective,
  the completed 31,237-case Python correctness inventory, and the separately
  frozen version-two recorder and protocol.
- The exact canonical, compressed, exclusively published version-two report
  and its distinct, durably synchronized publication receipt.
- Every selected source owner, before and after the build, without following
  symlinks. C, Rust, and Zig must each have their complete, separate source
  closure; Rust has no external package dependencies.
- Two separately produced native files in the caller's genuine, private
  `/tmp/rebar-phase2-native-build-v2-FAMILY-...` root. The activator reads
  both `reference-a/native/` and `reference-b/native/` files, checks the exact
  size, hash, complete bytes, and stable distinct inodes, and requires the
  files to match both independently published build phases.
- Every actual compiler and GNU ELF inspection process. The complete dynamic
  symbol stream is reparsed using the real symbol-name column. A GNU version
  index such as `(2)` is never treated as a symbol. Standard-library regex,
  external packages, dynamic loading, and cross-family native symbols are
  rejected.
- The C implementation owns exactly one native extension. Rust and Zig each
  own exactly one engine and one bridge; each bridge must load only its own
  adjacent engine through `$ORIGIN`. Zig retains its own verified `ctypes`
  engine path.

An existing repository binary is never accepted as source-build evidence. Its
exact original bytes are authenticated only after the complete version-two
proof passes, solely to make a durable, reversible backup. No native library or
candidate module is loaded during activation.

## Exact activation

After the corrected version-two build evidence and the activator have been
separately committed and pushed, invoke the exact pinned CPython with actual
observed values:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  /home/dev-user/src/rebar/tools/activate_verified_native_candidate_v1.py \
  --activate \
  --family FAMILY \
  --build-label ACTUAL_PUBLISHED_V2_LABEL \
  --build-root /tmp/rebar-phase2-native-build-v2-FAMILY-ACTUAL_SUFFIX \
  --activation-source-sha256 ACTUAL_FROZEN_ACTIVATOR_SHA256 \
  --activation-protocol-sha256 ACTUAL_FROZEN_ACTIVATION_PROTOCOL_SHA256 \
  --build-source-sha256 ACTUAL_FROZEN_V2_RECORDER_SHA256 \
  --build-protocol-sha256 ACTUAL_FROZEN_V2_PROTOCOL_SHA256 \
  --build-report-sha256 ACTUAL_PUBLISHED_V2_ARCHIVE_SHA256 \
  --build-receipt-sha256 ACTUAL_PUBLISHED_V2_RECEIPT_SHA256 \
  --native-engine-sha256 ACTUAL_FRESH_ENGINE_SHA256 \
  --native-bridge-sha256 ACTUAL_FRESH_BRIDGE_SHA256 \
  --native-engine-bytes ACTUAL_FRESH_ENGINE_BYTES \
  --native-bridge-bytes ACTUAL_FRESH_BRIDGE_BYTES \
  --owned-source-sha256 RELATIVE/OWNER=ACTUAL_OWNER_SHA256
```

Repeat `--owned-source-sha256` for every exact owner in the selected
version-two source family. For C, the engine and bridge arguments must both
identify the same one extension. For Rust and Zig, they must identify their
two distinct native outputs. No placeholder is a real hash or a runnable
command.

The operation first creates exactly one new, user-owned, mode-0700 recovery
directory:

```text
/tmp/rebar-phase2-verified-native-activation-v1-FAMILY-UNIQUE/
  backups/
    candidates/
      EXACT_PREVIOUS_NATIVE_FILE_IF_PRESENT
  recovery-journal.json
  promotion-intent-ROLE.json
  activation-report.json
  activation-receipt.json
```

Before promotion, every previously existing, exact canonical native file is
read without following symlinks and copied to an exclusive mode-0600 file
under `backups/candidates/`. Its original and backup path, complete bytes,
size, SHA-256, device, and inode are recorded. Both the backup file and its
private directories are durably synchronized. An originally missing target is
explicitly recorded as missing; no imaginary backup is claimed.

The complete `recovery-journal.json` is itself written exclusively and
synchronized **before** any canonical target changes. Only the fixed exact
candidate native targets below may then be promoted:

```text
C:    candidates/_vm_native.cpython-314-x86_64-linux-gnu.so
Rust: candidates/_rust_engine.so
      candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so
Zig:  candidates/_zig_probe.so
      candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so
```

For each target, the exact two-source-build output is written into an
exclusively created mode-0600 temporary file immediately beside that one
target. The complete staged file is synchronized, reread, and checked for the
exact size, hash, and unchanged inode. The prior canonical target is checked
against the already preserved recovery entry. Before replacement, an
exclusively created, owner-only `promotion-intent-ROLE.json` is durably
synchronized in the private recovery directory. Each intention binds the
original recovery-journal hash, family, exact fixed role and target path,
staged SHA-256, byte size, device, inode, and original permission mode. A
directory-descriptor-bound `os.replace` then atomically installs only that
fixed filename. The candidate directory is synchronized, and the promoted
canonical file is reread and checked against the exact staged inode, its
durable intention, and both actual version-two outputs.

The two Rust or Zig files are promoted as separately atomic fixed-file steps;
the protocol does not falsely claim simultaneous group atomicity. On **any**
failure after the recovery journal is prepared, the activator rechecks every
target and restores already promoted files in reverse order from their exact
verified backups. A originally missing target is removed only if its exact
promoted hash and inode are authenticated. Unknown or user-modified files are
never overwritten. The private recovery journal and backups are retained for
restart-safe manual recovery.

The five independently frozen original guard files are **never copied,
rewritten, monkeypatched, or rebound**. Their exact original repository paths
and hashes are authenticated before promotion and recorded in its proof:

```text
8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce
1b6b217bd6883dcfc2ff3ceafa66fa49544770bb7007d210ebbe3a57e48d24a3
cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95
569036804b557b01eb29ba404c6fea0ecc5806bdbc2b6b9eb61c1ea18aa79267
55aced566c4ef0a236f26ddf4607dbe3e69ae9dc15ab6fd95399d4ddc346cea2
```

The original candidate import root remains
`/home/dev-user/src/rebar`. The original V1–V5 guard sources, unchanged
`ROOT` values, original CPython tests, support modules, warnings helper, and
test corpus remain at their exact independently frozen original paths. A
later real correctness worker must use the genuine unmodified original guard
and the newly source-verified canonical artifact. No private guard, alias,
module-origin substitution, or candidate-root rebinding is permitted.

## Frozen consumer handoff

The actual activation report schema is
`rebar-phase2-verified-native-candidate-activation-v1`. Its independently
created receipt schema is
`rebar-phase2-verified-native-candidate-activation-v1-durable-publication-receipt`.
Both are exact canonical, ASCII, sorted-key JSON terminated by one newline.
The report is `activation-report.json`; its distinct receipt is
`activation-receipt.json`, immediately inside the one new private **recovery**
root. The report and receipt explicitly record
`promotion_mode = recoverable-canonical-promotion`,
`candidate_import_root = /home/dev-user/src/rebar`, every actual canonical
target, the complete no-follow source and native ownership, both genuine
source-build phase files, the unchanged original guards, and the exact
durable recovery-journal and backup identities.

Every downstream candidate worker, including genuine subinterpreters, must
require all five independently caller-pinned arguments:

```text
--activation-root /tmp/rebar-phase2-verified-native-activation-v1-FAMILY-UNIQUE
--activation-source-sha256 ACTUAL_FROZEN_ACTIVATOR_SHA256
--activation-protocol-sha256 ACTUAL_FROZEN_ACTIVATION_PROTOCOL_SHA256
--activation-report-sha256 ACTUAL_PRIVATE_REPORT_SHA256
--activation-receipt-sha256 ACTUAL_PRIVATE_RECEIPT_SHA256
```

It must reauthenticate the report, receipt, exact mode-0700 recovery root,
recovery journal, complete recoverable prior native files, unchanged original
guards, full canonical family source closure, each actual promoted canonical
native inode, genuine GNU symbol records, and version-two build provenance
**before** loading a candidate. Its candidate import root must be the exact
original repository root, with the newly verified canonical artifacts; a
historical stale `.so`, private copied guard, or rebound original `ROOT` must
fail closed.

## Crash-safe recovery without a report

A process can be killed after any separately atomic canonical replacement and
before an activation report or receipt exists. The original, independently
pinned pre-promotion journal and the per-role intentions are sufficient to
recover safely:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  /home/dev-user/src/rebar/tools/activate_verified_native_candidate_v1.py \
  --recover \
  --family FAMILY \
  --activation-root /tmp/rebar-phase2-verified-native-activation-v1-FAMILY-UNIQUE \
  --activation-source-sha256 ACTUAL_FROZEN_ACTIVATOR_SHA256 \
  --activation-protocol-sha256 ACTUAL_FROZEN_ACTIVATION_PROTOCOL_SHA256 \
  --recovery-journal-sha256 ACTUAL_DURABLE_PREPROMOTION_JOURNAL_SHA256
```

`--restore` with these same journal-pinned options is an exact alias for
`--recover`; neither command requires an activation report or receipt. Before
changing a canonical target, recovery verifies the unchanged objective,
correctness inventory and original guard sources; the actual corrected
version-two archived report and receipt; both distinct on-disk build-phase
artifacts; the complete selected source graph; each same-inode private
backup; and each durably recorded original or staged device, inode, hash,
size, and permission mode. It rejects a same-content replacement with a
different inode, never overwrites an unrelated user file, restores only
verified promoted targets in reverse order, and publishes an exclusively
created, durable restoration receipt. Originally absent files are removed
only when they are still the exact intended promoted inode. The journal and
backups are retained.

## Explicit restoration after successful activation

A successfully promoted family can be restored without trusting environment
variables, deleting broad paths, or overwriting an unrelated changed file:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  /home/dev-user/src/rebar/tools/activate_verified_native_candidate_v1.py \
  --restore \
  --family FAMILY \
  --activation-root /tmp/rebar-phase2-verified-native-activation-v1-FAMILY-UNIQUE \
  --activation-source-sha256 ACTUAL_FROZEN_ACTIVATOR_SHA256 \
  --activation-protocol-sha256 ACTUAL_FROZEN_ACTIVATION_PROTOCOL_SHA256 \
  --activation-report-sha256 ACTUAL_PRIVATE_REPORT_SHA256 \
  --activation-receipt-sha256 ACTUAL_PRIVATE_RECEIPT_SHA256
```

Restoration first authenticates the separately pinned source, protocol,
canonical report, distinct receipt, durable journal, exact original guard
sources, complete owner graph, every same-inode backup, and every current
target. It refuses to overwrite a user-modified or unrelated file. Exact
previous native bytes are restored with an exclusive adjacent staged file,
same-directory atomic replacement, directory synchronization, and complete
post-restoration hash verification. An originally absent file is removed
only when it is still exactly the journaled promoted artifact. The original
recovery journal, all backups, and a new exclusively written
`restoration-receipt.json` are retained.

## Source-only self-test

The only pre-publication execution is:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  /home/dev-user/src/rebar/tools/activate_verified_native_candidate_v1.py \
  --self-test
```

Run the identical invocation normally and under `env -i`. Its synthetic
controls require passing C, Rust, and Zig fixtures and reject missing or
reordered build phases, forged reports, changed source owners, incorrect
native sizes or hashes, false version-index symbols, foreign regex imports,
cross-family engines, omitted command pins, unsafe temporary roots, malformed
archives, incomplete real process streams, and re-sealed reports that replace
integer-zero effect counters with `False`, `True`, floats, nonzero values, or
injected receipt-only fields. Filesystem operations,
environment access, imports, subprocesses, threads, network connections, and
all clock operations are actively blocked and individually exercised. The
canonical promotion, durable prior-binary journal, rollback evidence, and
report-based and reportless restore commands are separately rejected when
incomplete or forged. Reportless synthetic controls cover partially promoted
families, originally absent targets, and same-content substitutions of either
the original or promoted inode. No actual
source build, activation, restoration, repository binary change, candidate
import, native load, correctness run, benchmark, holdout access, winner, or
speed is claimed.
