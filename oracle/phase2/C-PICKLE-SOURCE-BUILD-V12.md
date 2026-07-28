# First-party C pickle source build, version 12

This freezes a future source build. It does not build, import, activate, or run
the C regular-expression candidate. Candidate correctness, speed, memory, and
undefined behavior are **NOT MEASURED**. The original CPython 3.14.6 oracle,
all 13 groups, all 31,237 counted cases, and all 13 named private exclusions
remain unchanged. The final holdout remains unopened.

The published version-25 graph is preserved exactly: four independently
verified graph owners, 139 evidence owners, and 144 signed historical
references. Its complete C experiment still fails with 1,262 recorded
differences from 13 genuine candidate workers and 30 independently signed
result files. Eight complete groups pass; their 7,325 checks do not count
partial successes in failed groups. The real Rust build used 28 compiler and
inspection processes; the real Zig build used 26. Neither establishes a passing
candidate.

The existing C buffer-order repair produces 218,308 bytes with SHA-256
`f44694759174c1c3975423e07095ae91a853e66242c4e55d11836df03a730c4d`.
The independently frozen V2 Match repair then produces 219,227 bytes with
SHA-256
`8b35fba5b565ae18c5b9c180bec1dfbfb46b75bf3db7421626da4a73cdda2b94`.
The entire 6,912-case original public-types archive and its separate durable
receipt establish precisely 32 existing Match pickle differences: protocol 0
and protocol 1 should each succeed in 16 cases. All 64 original cases for
protocols 2 through 5 already reject Match pickling and must keep doing so.
This source freeze neither reruns those cases nor declares them repaired.

Only an explicit separately pinned `--build` can create a fresh private root.
The root deliberately keeps the original
`/tmp/rebar-phase2-native-build-v8-c-` convention required by the frozen V2
snapshot applier. It precreates distinct owner-only `reference-a` and
`reference-b` phase trees before any source application. Each phase receives
exactly one no-follow, exclusively created, owner-only 0600 V1-plus-V2 C
source and a separate unchanged original Python adapter. Repository source
files and the restored canonical native extension are never replaced.

Each phase may run only the existing immutable V8 first-party compiler kernel
and its seven pinned commands: `readelf --version`, the pinned GCC version,
one warning-clean offline C extension build, and four owned ELF inspections.
That is exactly 14 real processes across both phases. Each ELF is verified
against the actual owned compiler and readelf output, and both complete raw
ELFs must be byte-identical while originating from distinct private inodes.
External packages, borrowed engines, Python regex delegation, network access,
fallbacks, existing destinations, and prebuilt binaries remain forbidden.

A successful actual build may create only one fresh compressed evidence
archive and a separate fresh durable receipt. They are published only from
explicit `--build`; honest build failures retain distinct failure evidence.
Source-only self-tests and read-only context checks cannot apply a source,
create a private phase, invoke a compiler, import a candidate, run a test,
sample a clock, benchmark, change the workspace, or open the holdout. No
passing build is a passing correctness experiment or a qualified candidate.
