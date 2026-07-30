# First-party C full public correctness V1

This source-only freeze preserves the immutable Rust V5 public correctness
oracle and the same exact C24 native artifact and corrected adapter that have
already completed all 31,237 independently observed original cases under C16.
Freezing or verifying this document is not candidate execution, qualification,
benchmarking, or final holdout access.

The immutable public matrix contains exactly 10,434 cases: 94 independently
frozen datasets times 111 source-defined operations, split equally into 5,217
text cases and 5,217 bytes cases. Its published seed is 5928217332825411634;
its matrix SHA-256 is
`0c88d1ec7066ede05466c1a91126086cd52256548eda13a31778ff284439d97d`.

The unmodified complete Rust V5 public harness is
`a3d7e70343d231bf433fbad6a6669025a970d83691c49cb9f434a186aef3d9e6`.
Four count-checked in-memory substitutions produce the complete C-only harness
`140ff194bdd0d49dbfc5819282a46bb72391899bf3c17f735adfc96ed181c829` (112,748
bytes), while retaining exactly the original 111 operation definitions and every
dataset, case, expected outcome, warning, callback, buffer event, nested error,
and exception identity.

The actual C24 independent source-build publication receipt is
`ed0c119b2e672342f3665c9dc7c4896977ea590bceec08ff3b97cd56b9f92a75`; its
private-root provenance receipt is
`36cb6adcf3a28d635fc997c090e62e1ce5563754deab02c05b41f4d034ad3048`.
The exact corrected native SHA-256 is
`891acc0d0f496045e90e2efc0f0a3125e4f508352c2ee5e31ee807ea2fb1801a` (163,544
bytes). The corrected native-source SHA-256 is
`99f45846551705379ccd7365333995ee68fe25e10d101655a17ad45c5e13a5e6` (221,715
bytes). The corrected first-party C adapter is
`e91819b1d6b399954b3384519fdfddb6ccd6d4e4099a34e06d702c9959a79193` (62,209
bytes). Both independent phases and all four distinct source-owner inodes are
authenticated from published plaintext receipts without inspecting the private
root in source mode.

The actual C16 full-original PASS receipt is
`34f1b7ccd9fe06408cdc6094f86bf98f4776bc7716ad970264bfbbda0d1280f2`. It records
exactly 31,237 passing cases, 13 independently executed suites and workers,
zero mismatches, zero candidate execution failures, and the same exact C24
native and corrected adapter hashes. The separately authenticated strict V4
guard source is
`5b498643fa730dc09090bdc9e189e2d395cbe41a2b14019937eb251fd38240f3`.

The immutable Zig V2 wider-public guard failure is retained verbatim. C avoids
the historical invented outer-result metadata requirement: the candidate
process instead invokes C16's exact authenticated V4 installation function,
requires the actual installed policy object, selected C module, both native
owner roles, and guard-before-import module identity, and then verifies the
complete 10,434 actual public records.

Actual execution is a separately authorized, commit-and-push-pinned root-only
operation. It creates fresh C16 adapter/native recovery journals, atomically
activates only the authenticated independently built C24 owners, and runs one
isolated genuine stdlib reference process plus one isolated strict-V4 candidate
process. Every actual case and complete nested error remains in the durable raw
observations; every unequal complete record is preserved without truncation.

Both canonical originals must be restored to their exact authenticated original
inodes, modes, byte lengths, and SHA-256 fingerprints before any public result
directory, raw public artifact, or publication receipt is created. An actual
semantic failure is published truthfully as candidate `FAIL`; publication
`PASS` means durable publication only. This freeze never claims candidate
qualification, timing, memory, undefined behavior, winner selection, runtime
non-delegation, or final holdout access.

Source `--self-test`, `--verify-frozen-context`, and `--render-contract` are
irreversibly limited to exact pinned public plaintext owners. The physical
source wall denies all candidate paths, native binaries, private-root opens and
metadata, archives, phase-three proposals and holdouts, imports, subprocesses,
clocks, entropy, writes, and mutations. The final holdout remains
`INVALIDATED; REKEYED SUCCESSOR REQUIRED`.
