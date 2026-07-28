# Safely select six genuinely independently built engines

This is a frozen safety protocol. It does **not** install a replacement, run a
candidate, execute a compiler, change an existing native library, open a
performance holdout, or claim a speed improvement.

Freeze, commit, and push this document, the exact machine-readable
[`verified-native-activation-v3.json`](verified-native-activation-v3.json),
and the standalone
[`../../tools/activate_verified_native_candidate_v3.py`](../../tools/activate_verified_native_candidate_v3.py)
before authorizing any version-three activation. This activation version is
for the independently frozen **version-four source-build protocol**; it does
not relabel or replace version-two or version-three build evidence.

## The exact baseline and six owned families

The unchanged reference is pinned stable CPython **3.14.6**. All **13**
reference suites and **31,237** frozen case executions passed for CPython.
No candidate is thereby qualified. The final holdout remains closed.

| Family | Exact files eligible for future activation |
| --- | --- |
| C | `_vm_native.cpython-314-x86_64-linux-gnu.so` |
| Rust | `_rust_engine.so`, `_rust_bridge.cpython-314-x86_64-linux-gnu.so` |
| Zig | `_zig_probe.so`, `_zig_bridge.cpython-314-x86_64-linux-gnu.so` |
| C++ | `_cpp_bridge.cpython-314-x86_64-linux-gnu.so` |
| Go | `_go_engine.so`, `_go_bridge.cpython-314-x86_64-linux-gnu.so` |
| Fortran | `_fortran_engine.so`, `_fortran_bridge.cpython-314-x86_64-linux-gnu.so` |

Every filename is immediately inside the original repository's `candidates/`
directory. The machine contract independently freezes all **25** source
paths, complete SHA-256 hashes, original source sizes, and exact matching
target names. A wrapper, another family's engine, Python `re`, `_sre`, Go
`regexp`, C++ `<regex>`, RE2, PCRE, Oniguruma, Hyperscan, an outside package,
fallback, alternate import root, pre-existing binary, or guessed source-build
report cannot qualify.

## Only actual version-four source-build evidence

A future activation requires the exact separately published version-four
owners:

```text
source    efb37ccca1524e98f32b734b600704a390bc55c73d374da61c089730aaff10b1
protocol  e974b26562cc210c175c08cda7914e6b196fdee2ebe2a8232dd87c0cddbc0dfb
contract  0b5641529bc49f55b9e56fe397ad38e7e23d6c9b3376587b743753814b8089d7
```

The caller must independently provide the exact newly created V4 archive
and independently durable receipt, build label, actual private build root,
every source-owner hash, and every role's native hash and positive byte count.
A previously built C/Rust/Zig artifact is not V4 evidence. An old report or a
receipt marked `PASS` for a failed build cannot authorize a new activation.

Require all of the following before opening or changing a canonical target:

- Report schema `rebar-phase2-owned-native-source-build-v4` and receipt
  schema
  `rebar-phase2-owned-native-source-build-v4-durable-publication-receipt`.
- Independently pinned, complete, canonical and bounded V4 report and
  receipt; `report.status`, `receipt.status`, and `receipt.build_status` must
  all be `PASS`.
- The exact frozen V4 recorder, protocol, source contract, unchanged
  correctness oracle, original five correctness guard files, complete
  first-party source closure, and full authentic preserved history.
- Two complete and distinct `reference-a` and `reference-b` source phases
  beneath the exact owner-only
  `/tmp/rebar-phase2-native-build-v4-FAMILY-...` root.
- Real, independently produced native files with the exact recorded bytes,
  full SHA-256 hashes, distinct phase inodes, source-owned compilation, exact
  complete compiler argument vectors and environments, unique compiler
  process IDs, and complete authenticated output and error streams.
- Complete GNU dynamic-symbol rows, genuine versioned undefined symbols,
  family-specific runtime libraries, exact owned matching exports and bridge
  imports, and `$ORIGIN`; reject `RPATH`, external engines, and sibling
  engines.
- For Go, both fresh phase-generated `_go_engine.h` files, all nine owned
  exported C declarations, byte equality, distinct phase inodes, and the
  exact per-phase `-include` bridge compiler command. A generated header is
  verified build evidence, **never** promoted as a canonical engine.
- For Fortran, all nine forward engine functions and all three reverse
  Unicode/locale callbacks genuinely defined by its own bridge.

The pinned Zig compiler is the actual official
`/tmp/zig-x86_64-linux-0.16.0/zig`; an ambient `PATH` miss is not evidence
that it is unavailable. C++ may use its actual C++ runtime; Fortran may use
its actual Fortran runtime. Neither permission authorizes a regex library.

## Preserve real earlier results

The V2 C and Rust build successes, the genuine V2 Zig build failure, the
genuine corrected V3 Zig build success, and their independent reports and
receipts remain immutable. Preserve all original V2 compiler/inspection
processes: **8 C + 16 Rust + 15 failed Zig = 39**. The corrected V3 Zig
success has another **15** genuine processes. Require unique real PIDs only
within each actual run; never invent uniqueness across separate runs.

Also preserve the actual V6 Zig candidate failure, its worker failure, its
subinterpreter failure, all three durable failure receipts, and the real
owner-only restoration receipt
`c415ba80c055d39a933617a839624037b557adbe30c418c2a0e859131fbe9028`.
Authenticate all **17 independently published archive, receipt, subordinate,
and restoration owners for each** previously evaluated C, Rust, and Zig
family: **51 distinct actual mode-`0600` candidate evidence files**. The C and
Rust V5 graphs remain pinned through
`docs/evidence/candidate-current-overview-v7.inputs.json`, SHA-256
`744f86e241e3489cf07c5fccccf291eb68c44a50605d79723dd1ae1092d8511f`;
the complete Zig V6 graph is pinned directly. Do not describe 17 artifacts
from one family as all 51 actual owners. No archived failing family becomes
a qualifying candidate.

Separately preserve the three real, later V4 source-build experiments:

| Build | Actual build result | Processes | Complete phases |
| --- | --- | ---: | ---: |
| C++ | PASS; independently reproduced bridge | 10 | 2 |
| Go | FAIL; `py_bridge.c` could not find `Python.h` | 4 | 0 |
| Fortran | FAIL; the two independently built engines differ | 18 | 2 |

Independently authenticate both mode-`0600` owners for each experiment:

```text
C++ archive   48910a6328e8aaacdac993b2c029995d878960a456359a14db5c83b9fc518df9
C++ receipt   7742eda3ce777b1378d0c7fb87fc064f222850ca8bcf15cd23ff8a4d87d8bebf
Go archive    fcf643b7b8e9fbe80bd3b40c7ed884695a844f46e1117f5ebdb130135e5db4bb
Go receipt    215e9680bbe0f8d2250fcca8bae0335017606288e13e7636224b7c76336b5e41
Fortran archive ba35ea4f0d28814f716a36d2ccb384ef034a88a4029ca3f3cbf4f91eae268103
Fortran receipt 86b4b2648adf651481eea8d8b427a432f121c59322f508b522eca18af0749a08
```

There are **57 distinct actual evidence-owner inodes**: the 51 candidate
owners plus these six later source-build owners. The V4 process count is
**10 + 4 + 18 = 32**. The V2-plus-V4 subtotal is **39 + 32 = 71**; adding
the separately preserved corrected V3 Zig run gives **86 actual processes
across all seven build reports**. Do not describe the 71-process subtotal as
all reports or silently drop the 15 successful V3 Zig processes.

The two Fortran bridges both hash to
`eba8c1d145a53a2017fc9b7a6e4651b31ec4aef2e67e6c176c6435bffafc7b26`.
The engine hashes are genuinely different:
`37557a44033a80aa11a81fa145ca76c2bbd44ee544b31974dcf6e59ba0f2949c`
and
`696126d3f3e7239cac55975f53beb3b5e5cffc6948f08258817b6b2d86422199`.
A receipt's `PASS` records that its failure was published safely; it does
not change a Go or Fortran build result to `PASS`. The genuine C++ source
build is not a correctness-qualified replacement and does not activate its
bridge. No V4 build is started by this V3 freeze or either verification mode.

The old files and restored byte owners are evidence, not qualifying V4
artifacts. The independently falsified V1 symbol parser is never upgraded to
a pass. A durable failure receipt proves only that the failure was preserved.

## Crash-safe, reversible canonical promotion

Only an explicitly requested, separately authorized future operation may
create one fresh owner-only root:

```text
/tmp/rebar-phase2-verified-native-activation-v3-FAMILY-UNIQUE/
  backups/candidates/EXACT_ORIGINAL_FILENAME
  recovery-journal.json
  promotion-intent-ROLE.json
  activation-report.json
  activation-receipt.json
```

The root and backup directories have mode `0700`; every recovery evidence
file is created exclusively with mode `0600`. A canonical original that
exists is authenticated using its seven exact fields: relative path,
absolute path, complete SHA-256, positive byte count, device, inode, and
original permission mode. Its complete original bytes are copied to a fresh,
separately synchronized backup before any change. An originally missing file
is recorded honestly; no backup is fabricated. Preserve an existing file's
actual permission mode. Use `0755` only for an originally missing native
executable.

Synchronize the complete owner-only recovery journal **before** changing any
canonical target. Stage each genuine source-built file in a fresh exclusive
file immediately beside that one canonical target. Synchronize it and verify
its original mode, complete bytes, exact inode, hash and size. Exclusively
write and synchronize the owner-only per-role promotion intention binding the
journal, exact role, exact target, and exact staged inode. Only then replace
the one fixed filename through directory-bound file descriptors, synchronize
the actual candidate directory, and reauthenticate the promoted inode.

Each file replacement is individually atomic. Replacing two engine/bridge
files is **not group-atomic**. A crash after the first replacement can be
recovered using only the pre-promotion journal, the per-role durable
intention, actual canonical inode, unchanged passing V4 build evidence, and
owner-only original backup. An activation report or receipt is not required
for crash recovery.

Never replace, remove, or restore a modified or unrelated user file. An
originally missing target may be removed only after verifying that it is the
exact source-built, intention-bound, promoted inode. Restore originally
present files from their exact verified backup in reverse promotion order.
Keep the journal and backups; do not rewrite historical evidence.

## Exact future commands

After this freeze, future activation requires an independently published,
fully passing V4 build for the exact requested family and explicit real values:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/activate_verified_native_candidate_v3.py --activate \
  --family FAMILY --build-label REAL-V4-LABEL --build-root REAL-V4-ROOT \
  --activation-source-sha256 REAL-PUBLISHED-ACTIVATOR-SHA256 \
  --activation-protocol-sha256 REAL-PUBLISHED-PROTOCOL-SHA256 \
  --activation-contract-sha256 REAL-PUBLISHED-ACTIVATION-CONTRACT-SHA256 \
  --build-source-sha256 efb37ccca1524e98f32b734b600704a390bc55c73d374da61c089730aaff10b1 \
  --build-protocol-sha256 e974b26562cc210c175c08cda7914e6b196fdee2ebe2a8232dd87c0cddbc0dfb \
  --build-contract-sha256 0b5641529bc49f55b9e56fe397ad38e7e23d6c9b3376587b743753814b8089d7 \
  --build-report-sha256 REAL-PUBLISHED-V4-ARCHIVE-SHA256 \
  --build-receipt-sha256 REAL-PUBLISHED-V4-RECEIPT-SHA256 \
  --owned-source-sha256 RELATIVE/PATH=REAL-FROZEN-SOURCE-SHA256 \
  --native-sha256 ROLE=REAL-OUTPUT-SHA256 \
  --native-bytes ROLE=REAL-POSITIVE-OUTPUT-BYTES
```

Repeat the last three options separately for every owned source and every
source-built role. Go also pins its genuinely generated `generated_header`
hash and bytes, although the header is never installed. These placeholders
are not a runnable command or proof that the requested family passed.

Reportless crash recovery uses the independently pinned prepared journal:

```text
--recover --family FAMILY \
--activation-root EXACT-PRIVATE-V3-ACTIVATION-ROOT \
--activation-source-sha256 REAL-PUBLISHED-ACTIVATOR-SHA256 \
--activation-protocol-sha256 REAL-PUBLISHED-PROTOCOL-SHA256 \
--activation-contract-sha256 REAL-PUBLISHED-ACTIVATION-CONTRACT-SHA256 \
--recovery-journal-sha256 REAL-PREPROMOTION-JOURNAL-SHA256
```

`--restore` with a journal hash is the same reportless operation. A published
report-and-receipt restore instead pins both actual activation documents.

## Verify without any activation

The guarded synthetic checks use only fabricated in-memory bytes. They do
not open a file, access the environment, create a process, inspect a live
binary, start a compiler, load a library, create a recovery root, modify a
canonical file, read a benchmark, or sample a clock:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/activate_verified_native_candidate_v3.py --self-test

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/activate_verified_native_candidate_v3.py --self-test
```

The separately named frozen-context checks read and authenticate only exact
published source owners, original guard files, previously published records,
the official toolchain pins, and the actual restored Zig evidence. They never
start a subprocess, candidate, compiler, reference worker, or activation:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/activate_verified_native_candidate_v3.py --verify-frozen-context

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/activate_verified_native_candidate_v3.py --verify-frozen-context
```

Historical V4 builds: **C++ PASS; Go FAIL; Fortran FAIL**. Builds or V3
activations started by this freeze or its verification: **0**. Fully qualified
candidates: **0**. Correctness of any replacement, subinterpreter safety,
undefined behavior, execution speed, memory consumption, the expanded
holdout, and a winner: **NOT MEASURED**.
