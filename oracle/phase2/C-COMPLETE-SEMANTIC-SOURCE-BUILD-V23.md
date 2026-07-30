# Integrated first-party C engine build, version 23

Status: **SOURCE FROZEN; TWO-PHASE BUILD NOT RUN.**

This experiment prepares two genuinely independent native builds of the
project's own corrected C matching engine together with its corrected Python
adapter. It does not wrap or link an external regular-expression package,
borrow another candidate, run Python's `re` implementation, run correctness
cases, or measure performance.

The reference remains official CPython 3.14.6. Its unchanged correctness
oracle contains **31,237** original checks across **13** groups, **13** named
private waivers, and **8,244** separately reported reference checks. The
proposed **14,155,776**-case holdout remains **NOT GENERATED; NOT OPENED**.

## Preserve the actual failed candidate and previous build history

The latest genuinely executed C12 candidate failed. Exactly **16,413** checks
passed before five completed groups recorded **606** genuine differences:
16 managed-buffer, 248 public-object, 224 replacement, 114 public-surface, and
four retained-scanner cases. The child-interpreter group did not finish, so
the full mismatch count is **NOT MEASURED**. Its complete actual receipt is:

    oracle/phase2/evidence/repaired-c-original-campaign-v12-c-phase2-v21-c-original-match-semantics-original-p0-v12-failures-publication-receipt.json
    SHA-256  a3f4b90b8f289df9dfe49f776266e3c290edb2c21c62713137f501a5f997c21b

The actual prior C21 dual build and its separately durable private-root
receipt remain unchanged. They preserve two earlier genuine C19/C20 failures,
all previous immutable authority, and the necessary correction from
unavailable `os.getrandom` to supported `os.urandom`. Their source and both
real receipts are authenticated in every verification:

    tools/reproduce_owned_c_original_match_semantics_source_build_v21.py
    SHA-256  a1879dfefab15e91bfec95a74c4665d44e9894bef881c4945bccb3121be04726

    oracle/phase2/evidence/native-source-build-v21-c-phase2-v21-c-original-match-semantics-publication-receipt.json
    SHA-256  9475dd0c441a0440136f12425f94e6a4244e4cdc52d49f803e891f6663a647df

    oracle/phase2/evidence/native-source-build-v21-c-phase2-v21-c-original-match-semantics-root-provenance-receipt.json
    SHA-256  8f913d623bf5bb4aec3669e9b3daa882df16aad6f2f1bc3db1f02f4988a8afa2

The subsequently committed V22 build genuinely failed before creating its
private root. The first `os.urandom(16)` triggered CPython's audit event
`open("/dev/urandom", None, 524288)`, but the former deny-default build wall
had no ticket for that exact operating-system entropy-device opening. Preserve
the complete failed V22 source freeze and its separately pushed failure:

    tools/reproduce_owned_c_complete_semantic_source_build_v22.py
    SHA-256  c52d88c9f0124a85de2a573822a40b87486568da0dbc5353f2dde997c0c2d932

    oracle/phase2/C-COMPLETE-SEMANTIC-SOURCE-BUILD-V22.md
    SHA-256  463845709a50fd9b539d2443af84d7722269c97b02ba00a5f281ce97055158ed

    oracle/phase2/c-complete-semantic-source-build-v22.json
    SHA-256  8ffd9a546afa7fb0447bf84e64d6e69435ab3d0c6580828e16fa38eccd5ad8c1

    oracle/phase2/evidence/c-complete-semantic-source-build-v22-actual-build-failure.json
    SHA-256  66f8b8205ac3264ee85fe5b4d0ed46545e9dba91deab0ac6bd5d6544610bff14

Historical source hashes, failures, test cases, results, and receipts are never
rewritten. Their private build roots and compressed failure archive are not
opened during source verification or the new build.

## Pair both independently materialized corrected sources

The corrected C source restores protocols zero and one for Match pickling,
keeps nested exporter views alive until captures are materialized, releases
the subject precisely before replacement joining, and matches original
scanner garbage-collection visibility:

    candidates/c/variants/complete_native_semantics_v1/vm_native.c
    SHA-256  0654fe3a970760cc3efb08d819c8a4d8abadb152c35f370e662123e4de20e31f
    bytes    221557
    inode    525629

Its genuine root-only materialization receipt is:

    oracle/phase2/evidence/c-complete-native-semantics-v1-application.json
    SHA-256  1ac3c69067e7b76968fe852e35be7d689149d6de90a48c25a254ff9e9f287a9c

The separately corrected Python adapter restores public flag identity and
aliases, exact Match/Pattern public behavior, subclass cache identity,
bounded standard cache semantics, uncached `DEBUG`, and complete cache purge:

    candidates/c/variants/public_adapter_semantics_v2/vm_candidate.py
    SHA-256  4a62cb318592600d53e5ed6b9f8b9edf4edf2068fb2453892ca2130bb203410a
    bytes    61663
    inode    525120

Its genuine root-only materialization receipt is:

    oracle/phase2/evidence/c-public-adapter-semantics-v2-application.json
    SHA-256  e3e63acfde8f1eef32f81d48bddc613fb386880a5f1974b898e36b211ab55476

The adapter's native configuration must run while its original owned module
identity is intact; public `RegexFlag.__module__` changes only afterward.
The engine accounts for **276** known differences and the adapter for the
other **330**, preserving all **606** previous observations without asserting
candidate correctness before a real run.

## Strict source-only boundary

The independently authenticated native correction controller is bootstrapped
from its exact complete immutable plaintext source before a deny-default audit
hook and descriptor wall are installed. Synthetic self-test reads that one
controller but no other workspace owner, candidate, compiler, or private root.

Source verification authenticates exactly **24** immutable plaintext owners,
including that one bootstrap: the new controller/protocol/contract, native
correction triple, adapter correction triple, corrected V4 guard triple,
historical C21 triple, two actual materialization receipts, two actual C21
build/root receipts, the latest actual C12 failure receipt, the complete
failed V22 source freeze, and its real committed failure receipt.

It physically denies both corrected candidate source files, both canonical
candidate source files, the installed native extension, archive/final-test
owners, private root/journal entropy, direct compiler/process startup,
network, clocks, and all workspace mutations. The inherited native correction
and integrated build model undergo hundreds of hostile controls.

Run both source checks normally and again under
`env -i PATH=/usr/bin:/bin LC_ALL=C`:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/reproduce_owned_c_complete_semantic_source_build_v23.py \
  --self-test

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/reproduce_owned_c_complete_semantic_source_build_v23.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Candidate compatibility, runtime non-delegation, undefined behavior, speed,
memory, and compiled artifact identity remain **NOT MEASURED**. No candidate
is qualified and no winner is selected.

## Separately authorized reproducible actual build

Only after these exact three V23 owners are committed and pushed may the root
coordinator use the separately explicit authorization below. Every corrected
source/failure/guard/prior-build fingerprint is an independently required
authority; the frozen and pushed commit must be identical.

The build authenticates the entire GCC 13 executable, pinned CPython 3.14.6,
`Python.h`, `patchlevel.h`, and GNU `readelf` before creating a fresh private
`0700` `/tmp/rebar-phase2-c-complete-native-semantics-v23-*` root with
`os.urandom(16)`. It creates two separate `0700` phase directories. In each it
exclusively writes and syncs one corrected `0600` native source and one
corrected `0600` Python adapter, then launches seven authenticated processes
directly through POSIX spawn: `readelf --version`, `gcc --version`, GCC
compilation, and four distinct ELF inspections.

The V23 wall corrects the observed V22 failure with a single narrow,
short-lived entropy ticket. Only while executing the controller's own
`os.urandom(12)` or `os.urandom(16)`, it admits at most one exact
`open("/dev/urandom", None, os.O_CLOEXEC)` event. Other devices, paths,
opening modes, flags, request lengths, duplicate device openings, nested
tickets, source-only entropy requests, and out-of-scope access remain denied.
Synthetic hostile controls check all these boundaries without opening the
entropy device or changing the workspace.

The exact compiler command for each private phase is:

```text
/usr/bin/x86_64-linux-gnu-gcc-13 -std=c11 -O3 -g0 -fPIC -shared \
  -fno-semantic-interposition \
  -ffile-prefix-map=PHASE_PATH=/rebar/c-complete-v23 \
  -I /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14 \
  -Wl,--build-id=sha1 -Wl,--hash-style=gnu \
  -o PHASE_PATH/_vm_native.cpython-314-x86_64-linux-gnu.so \
  PHASE_PATH/vm_native.c
```

All **14** process IDs must be distinct, all four source inodes independent,
both compiled ELF inodes independent, and both complete ELF hashes identical.
No compiled hash, size, correctness result, or speed is guessed in advance.
Exact required Python extension identity is `PyInit__vm_native`. ELF symbols
and dependencies reject external matching packages and dynamic delegation.

A private atomic `0600` recovery journal is updated before compilation, after
each phase, and after durable receipts, using `os.urandom(12)` and file/root
directory syncing. The private root and journal survive both success and
failure. Success exclusively publishes and syncs two fresh evidence files:

    oracle/phase2/evidence/native-source-build-v23-c-phase2-v23-c-complete-semantics-publication-receipt.json
    oracle/phase2/evidence/native-source-build-v23-c-phase2-v23-c-complete-semantics-root-provenance-receipt.json

The build never activates its extension and never modifies either corrected
source, either canonical source, or the installed canonical native extension.
The original native must remain SHA-256
`075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd`,
149,976 bytes, inode `430300`, mode `0755`, device `2064`, with one link.

The actual root-only command is:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/reproduce_owned_c_complete_semantic_source_build_v23.py \
  --build --authorize-first-party-complete-native-build-v23 \
  --frozen-commit PUSHED_FROZEN_COMMIT \
  --pushed-commit PUSHED_FROZEN_COMMIT \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256 \
  --native-source-sha256 378b3941b3038f8af7b9a42199044517973b2c23012c11faa504a645123341f9 \
  --native-protocol-sha256 2dcea6c1d7e03f56bc4662e459f97162b9061041052b0f6459138ae5a55f067e \
  --native-contract-sha256 46f0f7e409bf60c5271bf84819f88b551bcc2b852a88b69f1045bb7f3a656f0e \
  --native-application-sha256 1ac3c69067e7b76968fe852e35be7d689149d6de90a48c25a254ff9e9f287a9c \
  --adapter-source-sha256 13173033914a706f4d80e76dc8c95ee016a125f7d3261fdf252ed404a60ebb55 \
  --adapter-protocol-sha256 ad91932c5b60cace2a632d11ff62e80d3890de4e4018e8e9ed7e6a4b466436a2 \
  --adapter-contract-sha256 ed5421ca2ab6a99c59945529cd8ae640636bad2ad42806bd7f36c8cf3ef584ce \
  --adapter-application-sha256 e3e63acfde8f1eef32f81d48bddc613fb386880a5f1974b898e36b211ab55476 \
  --guard-source-sha256 5b498643fa730dc09090bdc9e189e2d395cbe41a2b14019937eb251fd38240f3 \
  --guard-protocol-sha256 835473a98f62c9b2cb0dee61736b6cbbab4460f14d8371597e80933c64721a16 \
  --guard-contract-sha256 30f5c52d5aadfd6e8a7be7c6f355d9628510384d7fd922bcfb609dfe854acea2 \
  --c21-source-sha256 a1879dfefab15e91bfec95a74c4665d44e9894bef881c4945bccb3121be04726 \
  --c21-protocol-sha256 20844ff1c5a4b4908bc903d1a3c3e31e72c7f397b863741fce528ecd8b20d226 \
  --c21-contract-sha256 a32651018f9c60cfa5963768ffd0cb4463e6c691556958dfd3cd3bea0a42a382 \
  --c21-build-receipt-sha256 9475dd0c441a0440136f12425f94e6a4244e4cdc52d49f803e891f6663a647df \
  --c21-root-receipt-sha256 8f913d623bf5bb4aec3669e9b3daa882df16aad6f2f1bc3db1f02f4988a8afa2 \
  --c22-source-sha256 c52d88c9f0124a85de2a573822a40b87486568da0dbc5353f2dde997c0c2d932 \
  --c22-protocol-sha256 463845709a50fd9b539d2443af84d7722269c97b02ba00a5f281ce97055158ed \
  --c22-contract-sha256 8ffd9a546afa7fb0447bf84e64d6e69435ab3d0c6580828e16fa38eccd5ad8c1 \
  --c22-failure-receipt-sha256 66f8b8205ac3264ee85fe5b4d0ed46545e9dba91deab0ac6bd5d6544610bff14 \
  --c12-failure-receipt-sha256 a3f4b90b8f289df9dfe49f776266e3c290edb2c21c62713137f501a5f997c21b \
  --corrected-native-sha256 0654fe3a970760cc3efb08d819c8a4d8abadb152c35f370e662123e4de20e31f \
  --corrected-adapter-sha256 4a62cb318592600d53e5ed6b9f8b9edf4edf2068fb2453892ca2130bb203410a \
  --installed-native-sha256 075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd
```

A successful build proves only reproducible compilation. The frozen V4 guard
and V5 producer import `candidates.vm_candidate` and `candidates._vm_native`
under their exact canonical names, so a later, separately authorized
correctness campaign must safely stage **both** corrected adapter and native
artifact at those names, record the temporary adapter change honestly, and
restore both original inodes and modes. This build does none of those actions.
