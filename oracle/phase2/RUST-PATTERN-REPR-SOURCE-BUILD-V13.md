# Freeze two independent builds of the repaired Rust engine

This is a source freeze. It does not apply source, run a compiler, change or
activate a candidate, test matching, publish build evidence, measure speed, or
open the final holdout.

## Preserve the actual result

CPython 3.14.6 remains the reference. The original gate remains 31,237 cases,
13 groups, and 13 named private exclusions. Rust has actually completed all
groups and still fails with **1,036 mismatches and 8,965 verified passes**.

The first failing frozen case is
`pattern-and-match-representation/058`. Its 901-byte record has SHA-256
`1130da7818fe8b27a0d74f607bd4531c43f5f12ec9d6674419aa448786884d75`.
Python expects `re.IGNORECASE|re.ASCII` in the compiled-pattern display;
the tested candidate returned `re.ASCII|re.IGNORECASE`.

The frozen V3 repair source, explanation, and machine contract have SHA-256
digests `5e57da2379e736bba75eacdb57f84710dc144c0d4088d5827b3139a6b71d8859`,
`2aeb81e55548b46011c75815465d2bc2fa461d57ba7b990fc7a7b87d2d687a34`,
and `82bce0066181dd16f3de52d88f31e930f25706b5ff3da2ba18b10c8b31b4f6a1`.
The newly derived first-party public adapter is exactly 31,934 bytes with
SHA-256 `d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e`.
Preserve all 5,128 standalone flag examples, the owned Rust engine, native
bridge, public error, hashing, copying, and serialization. Do not reuse the
old tested `f8afb6c6` adapter.

The immutable V33 graph is historical: it records 155 evidence owners, 160
references, and an older Zig result of 2,172 mismatches and 2,847 verified
passes. Historical V34 records 157 owners and 162 references. At that time
the separate callable-signature reference had not run. C has 1,230
mismatches. Zig V12 was genuinely built in 26 real processes with two source
applications. Its subsequent corrected V3 matching campaign actually
completed all 13 groups and **failed with 1,764 mismatches and 3,711 verified
passes**. All 13 candidate workers completed without infrastructure failures.

Independently authenticate the 4,111-byte actual Zig matching receipt with
SHA-256 `40be94851ae23d8c4a9d2ac759d28231605247a499b0703e727c757d25b2fb96`
and its exact 3,722,337-byte compressed archive with SHA-256
`ab857c82369ea0c1a443d2d140c8009d7f4b5216b5ee6a0bb4e9280000cb9d6b`.
Never decompress the archive.

The separate 50-case Python reference has since actually **passed** in two
independent pinned CPython workers, process IDs 81 and 82, with no reference
failures. Its separately durable 3,533-byte receipt has SHA-256
`29b4a389e1b99cce15f07069ee1a0895f193e13400f944a037a4f42832619334`.
Its 8,538-byte compressed archive has SHA-256
`7875f249a6cec7910e31800566ef5ccb1ee7398a29a403f307c5de88e647736c`.
Authenticate the exact receipt, its original source freeze, and compressed
archive without inflating it. The original denominator stays at 31,237;
candidate execution of the 50 extra cases is **NOT RUN**. The current
authenticated evidence lower bounds are 159 owners and 164 references, and
later append-only evidence remains allowed.

## Freeze a real two-phase from-scratch build

Only a separately authorized `--build` may create fresh private trees:

    /tmp/rebar-phase2-native-build-v9-rust-.../reference-a
    /tmp/rebar-phase2-native-build-v9-rust-.../reference-b

Independently pin all nine actual canonical sources, the exact repaired bridge,
and the 31,934-byte V3 public adapter. Create owner-only mode-`0700`
directories. In each phase, exclusively create seven ordinary source snapshots
and two repaired mode-`0600` no-follow overlays. Authenticate all 18 distinct
source inodes and all original canonical files. Never activate a candidate.

Reuse only the frozen, first-party V9/V7 low-level build and binary-audit
primitives. Authenticate Rust 1.95.0, Cargo, GCC, and `readelf`. Cargo must
stay locked, frozen, and offline. Forbid external regex packages, `re`,
`_sre`, other candidate engines, networking, and prebuilt native outputs.

A real build must execute these 14 successful processes in each phase:

    readelf_version
    gcc_version
    rustc_version
    cargo_version
    build_rust_engine
    build_rust_bridge
    engine_dynamic
    engine_symbols
    bridge_dynamic
    bridge_symbols
    engine_sections
    engine_notes
    bridge_sections
    bridge_notes

Accept a build only after 28 distinct real successful process IDs, two separate
phase trees, and independently owned byte-identical first-party engine and
bridge binaries. Preserve a real failure under a separately named exclusive
failure archive. Use `native-source-build-v13-rust-` archives and separately
durable receipts. Cap both the complete compressed and expanded build report
at **2 MiB**. Build success never proves matching.

## Source-only verification

Run ordinary and sterile `--self-test` and `--verify-frozen-context`
commands with independently pinned source, explanation, and canonical machine
contract. Use pinned Python 3.14.6 with `-I -B`.

The self-test physically blocks filesystem access, writes, processes, imports,
networks, threads, clocks, native loading, locks, signals, and archive
inflation. Check at least 100 hostile controls against the complete synthetic
two-phase, 18-source, 28-process plan.

The context authenticates historical V33 and V34, the actual Rust V4 failure,
the actual previous Rust V12 build, the Zig V12 build and its completed V3
matching campaign, both successful supplementary CPython reference workers,
all independent Rust and reference source owners, Rust 1.95.0, the single
first-party Cargo package, and the original low-level build kernels. Existing
archives are authenticated as compressed bytes only.

Corrected Rust V3 matching, undefined behavior, memory, confidence intervals,
and performance are **NOT MEASURED**. The 4,194,304-case holdout is
**NOT OPENED**. No candidate or winner is qualified.
