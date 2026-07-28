# See why independently built regex engines differ, before guessing

We are building Python `re` replacements from scratch, not wrapping another regex package. Before changing an engine, this source freeze adds a way to inspect the **actual bytes** produced by each of six independent native implementations: C, Rust, Zig, C++, Go, and Fortran.

This is a forensic-tool freeze. It does **not** run a build, activate a candidate, run matching, measure speed, open the holdout, or declare a winner. Candidate correctness, speed, and memory remain **NOT MEASURED**. The final holdout is **NOT OPENED**. Correctness-qualified candidates: **0**.

## What the evidence actually says

The baseline remains the unchanged, isolated CPython 3.14.6 correctness oracle: **13 original suites and 31,237 original case executions**. All **25 distinct first-party implementation source files** and all **13 exact compiler, interpreter, and toolchain-file owners** remain frozen. There is no external regex engine, shared semantic implementation, stdlib matching fallback, network fetch, or substitute compiler.

There are **65 distinct, signed, mode-0600 historical evidence-file owners**: the 51 original candidate evidence owners, 6 version-4 build owners, 4 version-5 build owners, and 4 genuine version-6 Go and Fortran report and receipt owners. Owners are counted by distinct file identity, not by the number of compiler processes.

The historical compiler-process scopes are **71** for versions 2 and 4; **102** after version 5; **117** including the independently recorded version-3 Zig run; and **169** after both actual 26-process version-6 builds. A failed build with 26 successful compiler and inspection processes still contributes 26 real historical processes; it does not become a successful build.

### Go was actually reproducible

The frozen V6 Go build completed all **26 of 26** compiler and inspection processes and both independently snapshotted phases. Its real Go engine exports all 9 required first-party symbols. The separately owned C bridge force-includes the compiler-generated header, with exactly one `-D_GNU_SOURCE` before that header; the Go engine package contains only the authentic first-party `go.mod` and `engine.go`. Both phases produced identical outputs:

- Engine: 2,712,912 bytes; SHA-256 `38ab223b8ef88340a7be86f2195c417ee7d2dd9deead48cc6495a5b4e3c31b27`.
- Bridge: 41,904 bytes; SHA-256 `dd71ab6cb15a98e1a07c38965cdb178da0dbba2a26db937975e0d6435a2a5d0c`.
- Generated build-only header: 3,086 bytes; SHA-256 `481ebb65cc587749677ce28abeb4f3de111e2f87a18ac547ff0157fce85d2c23`.
- Actual signed passing report: 37,619 compressed bytes; SHA-256 `05c24a5fff228d8eab8bec961d825b0e65504072e11e8c574ec580d9f3e6e245`; 262,323 uncompressed bytes; SHA-256 `37c97e72530ffc1022741429be2ffc9eebe7afaec6063c763d7ff86f6f7bd8ae`.
- Actual passing publication receipt: 3,262 bytes; SHA-256 `f3adcb20bb591946600e1e2b1db037fb3b4828c3d4a628a0347cfed40f262fca`.

This is a **source-build pass**, not a regex-correctness pass and not a benchmark.

### Fortran genuinely failed to reproduce

The frozen V6 Fortran build also completed all **26 of 26** compiler and inspection processes and both independently snapshotted phases. Its bridges were genuinely identical: 37,424 bytes with SHA-256 `f0808671b4d16f9b8d74a891d04ccd78bcf2e568ae2edbfb3997fb0db23c2fd7`. Its two 74,544-byte engines were **not** identical:

- Phase A: SHA-256 `6ed7afa0b7c2eb905cd00de0ec935a7c449f257431d44aaa652ae0f10191d1f7`.
- Phase B: SHA-256 `1458072addc7988975317ac81d64748970ee3d4321437be73275a700fed831c9`.

Both engines had **zero build-ID-note bytes**. The actual section listings were identical: 2,833 bytes with SHA-256 `3f15407ebd8d72adb59d7ffc87f4c43195ed5417c595e92e05d941ad244992c3`. That listing describes the sections; it does not record their raw payload. The historical differing raw section is therefore **NOT RECORDED**. The fixed random seed, path maps, and removal of the GNU build ID have already been experimentally refuted as sufficient explanations. No different cause is guessed.

- Actual signed failing report: 26,102 compressed bytes; SHA-256 `c62007d5519d1ef723da7e144b1c6eeb067aacf47e960638e9d6b8a604f05d12`; 166,999 uncompressed bytes; SHA-256 `b8186f02586e134b5db4275688513670cad814526ce4b42cad50802ed9f2f32b`.
- Actual passing failure-publication receipt: 3,221 bytes; SHA-256 `6bc1ea1695247d8d137e6c2f50908b6c3a0518ff82978258bd07e8010e88ad7a`.

A receipt marked `PASS` means the authentic **failure report was safely published**. The Fortran source build remains `FAIL`, and no Fortran candidate is activated or correctness-qualified.

## What V7 adds

Every version-6 compiler command, compiler and linker flag, two-phase source snapshot, offline Go environment, private root isolation, generated-header rule, and complete `readelf` stream is preserved. No speculative Fortran repair or extra inspection process is introduced.

During a separately authorized future build, V7 will read the complete actual phase-native binary through its already authenticated first-party file descriptor, check its exact file size, SHA-256, device, and inode, and then parse the in-memory bytes using Python’s built-in `struct`. It records:

- The genuine 64-bit, little-endian, x86-64 ELF header, program headers, section headers, and bounded section-name table.
- Every actual file-backed section’s complete original byte range and SHA-256. Memory-only `NOBITS` sections are recorded as memory-only; no fake file bytes or hashes are invented.
- Authentic symbol tables, extended section indexes, genuine GNU symbol versions, linked dynamic string tables, and bounded compressed-section contents.
- Independently hashed ELF headers, program and section tables, padding, unclaimed regions, and trailing bytes.
- Every actual differing byte and exact differing offset range across both complete phase files. At most 64 range previews are displayed; the total range count, omitted range count, and streaming SHA-256 of the **complete** range manifest always disclose any truncation.

The exact native owner and all bytes are authenticated again after the existing `readelf` inspections. The full raw-byte comparison is recorded **before** declaring a source build reproducible or failed. An explanation naming one differing section is allowed only when the entire file proves that every differing byte lies in that same independently identified section. Otherwise the report preserves the complete observed evidence and says **NOT ESTABLISHED**.

This instrumentation is not itself a matching engine. It starts zero additional compiler, inspection, reference, candidate, timing, network, or benchmark processes.

## Reproduce only the safe source gates

Run from the repository root with the exact pinned CPython 3.14.6:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/reproduce_owned_native_source_build_v7.py --self-test

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/reproduce_owned_native_source_build_v7.py --self-test
```

For the complete 65-owner, read-only frozen context, substitute the independently computed full SHA-256 values of the V7 source, this protocol, and `oracle/phase2/native-source-build-v7.json`:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/reproduce_owned_native_source_build_v7.py --verify-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/reproduce_owned_native_source_build_v7.py --verify-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

Both self-tests are entirely synthetic and effect-blocked. Both context checks are strictly read-only. None authorizes a build, candidate, activation, regex match, benchmark, or holdout.
