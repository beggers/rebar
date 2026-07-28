# Verified native activation V4

Status: source freeze only. No native candidate has been activated or qualified.

## Purpose

Freeze one reversible, fail-closed way to activate six independently written Python regular-expression candidates only when the exact candidate has an independently proven, passing source build. Activating a native file, importing a candidate, running the correctness oracle, measuring performance, or opening the holdout is never implicit.

The unchanged reference is CPython 3.14.6. Its original correctness oracle contains 13 suites and 31,237 case executions. A passing native build is not a passing correctness result. Qualified candidates: 0.

## Exact families and artifacts

Each family owns its full, separate source closure. Together they own 25 distinct source files and 10 distinct possible import-time native targets.

- C: its own standalone extension.
- Rust: its own engine and its own bridge.
- Zig: its own engine and its own bridge.
- C++: one combined first-party bridge containing its own compiled C++ engine. No separate C++ engine file is invented. Its Python-facing `Match` remains Python-owned.
- Go: its own c-shared engine and separate C bridge. Its fresh, nine-export compiler-generated header is build evidence only and is never promoted. Its Python-facing `Match` remains Python-owned.
- Fortran: its own engine and bridge. The actual V6 Fortran build failed and is not eligible for activation.

No family may call Python `re`, `_sre`, a third-party matcher, another candidate, a fallback matcher, or a prebuilt engine. Native dependencies, all versioned symbols, exact exports, and bridge `$ORIGIN` runpaths are independently checked against the real source-build records.

## Preserve the actual evidence

All 65 distinct owner-only evidence files are authenticated without merging files with processes: 51 original candidate-history owners, six V4 build owners, four V5 failure owners, and four V6 build owners.

All 169 actual historical compiler and inspection processes remain separately accounted for: 39 V2 processes, 15 historical V3 Zig processes, 32 V4 processes, 31 V5 processes, and 52 V6 processes. Historical C, Rust, and Zig semantic mismatches remain respectively 2,094, 2,042, and 1,764. None is qualified.

The actual V4 C++ source build passed. Its real, combined bridge is SHA-256 `d444611316caceb4ba08783203bc4f1d396a8987f63a49bd24c81d5d2c532441`, 130,744 bytes. Its 10 real processes and two reproducible phases are preserved.

The actual V4 Go and Fortran builds failed. The actual V5 Go build failed after five recorded processes because its generated Go header required the missing GNU feature-test macro. The actual V5 Fortran build completed 26 successful processes and two phases but produced different engines. A durable publication receipt never changes a build failure into a pass.

The genuine V6 Go source build passed after 26 successful processes in two independent phases:

- Report: `05c24a5fff228d8eab8bec961d825b0e65504072e11e8c574ec580d9f3e6e245`, 37,619 compressed bytes.
- Receipt: `f3adcb20bb591946600e1e2b1db037fb3b4828c3d4a628a0347cfed40f262fca`, 3,262 bytes.
- Engine: `38ab223b8ef88340a7be86f2195c417ee7d2dd9deead48cc6495a5b4e3c31b27`, 2,712,912 bytes.
- Bridge: `dd71ab6cb15a98e1a07c38965cdb178da0dbba2a26db937975e0d6435a2a5d0c`, 41,904 bytes.
- Build-only header: `481ebb65cc587749677ce28abeb4f3de111e2f87a18ac547ff0157fce85d2c23`, 3,086 bytes.

The genuine V6 Fortran source build failed even though all 26 actual compiler and inspection processes succeeded and both phases completed:

- Failed-build report: `c62007d5519d1ef723da7e144b1c6eeb067aacf47e960638e9d6b8a604f05d12`, 26,102 compressed bytes.
- Actual canonical report: `b8186f02586e134b5db4275688513670cad814526ce4b42cad50802ed9f2f32b`, 166,999 bytes.
- Durable receipt: `6bc1ea1695247d8d137e6c2f50908b6c3a0518ff82978258bd07e8010e88ad7a`, 3,221 bytes. Publication passed; the build failed.
- First 74,544-byte engine: `6ed7afa0b7c2eb905cd00de0ec935a7c449f257431d44aaa652ae0f10191d1f7`.
- Second 74,544-byte engine: `1458072addc7988975317ac81d64748970ee3d4321437be73275a700fed831c9`.
- Identical 37,424-byte bridge in both phases: `f0808671b4d16f9b8d74a891d04ccd78bcf2e568ae2edbfb3997fb0db23c2fd7`.
- Both actual engine note streams have zero bytes. Disabling the GNU build ID did not make the engines identical. The differing raw binary section is NOT RECORDED.
- Exact real error: `BuildError: the two independently owned outputs are not genuinely byte-identical`.

Never describe the real Fortran result as a compiler failure. Never load, promote, activate, or qualify its failed output.

## Immutable source-build versions

A complete, matching triple selects exactly one source-build version; mixed versions fail closed.

Original V4:

- Source: `efb37ccca1524e98f32b734b600704a390bc55c73d374da61c089730aaff10b1`.
- Protocol: `e974b26562cc210c175c08cda7914e6b196fdee2ebe2a8232dd87c0cddbc0dfb`.
- Machine: `0b5641529bc49f55b9e56fe397ad38e7e23d6c9b3376587b743753814b8089d7`.

Corrected V6:

- Source: `2af9da3cb37a55782f3bfb8bdbdfdb7a945532994a5c988f4645d888dbe57ebc`.
- Protocol: `108dbd52144c78530221e36882a0070fe9805b1bef6a136caf4636148ae9131d`.
- Machine: `0121aaa5902b449e107396d6a1107ca8fe0fefebb0a0f09eb58d2d19c8888db4`.

Each passing record must independently prove both fresh source phases, distinct original and phase-owned file inodes, every exact command, offline environment, working directory, real process identity, complete standard output and error, dynamic dependencies, versioned symbols, sections, and notes. Both actual phase artifacts are reread and compared against the exact report inodes before any explicit activation.

## Reversible explicit activation

Recovery uses a fresh, mode-0700, V4 activation root. Evidence, journals, promotion intentions, and restoration records are owner-only. Before every individual replacement, persist the exact original bytes, mode, device, and inode, or truthfully record that the target was absent. Persist and synchronize a separate intention before each adjacent, exclusive, no-follow, individually atomic replacement.

A two-file promotion is not group-atomic. Interrupted activation remains recoverable from the durable journal and intentions even if no activation report or receipt was created. Reverse-order recovery restores only recorded, unmodified targets. A user-modified target is never overwritten or deleted. The Go-generated header is never a canonical target or a recovery target.

The source freezes explicit `--activate`, `--recover`, and `--restore` interfaces but performs none of them. Every explicit operation must caller-pin the published activation files, correct source-build version, independent report and receipt, all semantic source owners, and every real native role.

## Source-only verification

`--self-test` blocks and independently exercises every filesystem, subprocess, compiler, thread, clock including `clock_gettime`, network, candidate import, native library, environment, temporary-root, promotion, and holdout effect. Every actual-effect counter must remain zero.

`--verify-frozen-context` only authenticates the unchanged original oracle, all six first-party source closures, 13 pinned toolchain files, all 65 distinct evidence owners, complete historical process streams and actual outcomes, the safe existing restoration state, and the immutable V4 and V6 source-build freezes.

Run both modes with the exact CPython 3.14.6 executable in normal and clean environments. No source-only check builds or activates a candidate.

Correctness: NOT MEASURED. Undefined behavior: NOT MEASURED. Performance: NOT MEASURED. Memory: NOT MEASURED. Holdout: NOT OPENED. Winner: NOT SELECTED.
