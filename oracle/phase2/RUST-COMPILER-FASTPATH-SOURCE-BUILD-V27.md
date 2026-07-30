# Reproduce the first-party Rust parser-allocation architecture

Status: **SOURCE FROZEN; NATIVE BUILD NOT RUN; CORRECTNESS AND SPEED NOT
MEASURED.**

This V27 experiment asks one narrow, falsifiable question: does eliminating
unnecessary allocations while compiling regular expressions improve a genuine
first-party Rust implementation? It changes no public Python behavior and uses
the ordinary existing Rust search implementation, so its results can later be
compared fairly with the separate required-character search architecture.

## Preserve what actually happened

The frozen original test suite has 31,237 cases across 13 suites, with 13 named
private waivers. The preceding complete Rust run failed 1,352 cases: 240
substitution failures and 1,112 shape-changing failures; 15,877 cases were
observed passing. Publication of that failed result succeeded, but the candidate
did not pass. The separate 8,244 supplemental cases and 6,912 corrected
reference cases never change the original denominator.

Preserve the complete successful V25 first-party build and its real 28 compiler
or inspection processes:

    V25 build publication
    55cdccb1114e0cc7e4bdcecb8311b3c80c4e020dcfdabd1d8597cf3cececeefc

    V25 private-root provenance
    e8633ac1224235db9f8ea48c683c833fba3015cd73f071cd2488fa0b13a117a2

The historical engine was
`5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f`.
The new engine has not been built or measured. Preserve all three complete
public practice files, their 416 cases, and their 1,664 paired observations;
they measure the previous Rust implementation, not this new architecture.

The complete, separately performed V25 original correctness run also failed:

    d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59

All 13 candidate workers completed all 13 suites with no infrastructure
failures. Exactly 15,877 cases were observed passing; exactly 1,352 mismatches
remain: 240 substitution cases and 1,112 shape-changing cases. The separate
runtime non-delegation audit still fails. Its complete compressed evidence has
hash `dee05f06d473af52db5447b485265d886e66e5420cb3e814b5b972d8798a04a7`
and is never opened by this source freeze. A publication status of `PASS`
means that the failing evidence was safely recorded; the candidate itself is
still **FAIL**, not qualified, and not interchangeable with Python `re`.

## Exactly which first-party source changes

The immutable canonical Rust matcher remains unchanged:

    candidates/rust/src/lib.rs
    c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d
    177967 bytes

The separately frozen and exclusively materialized compiler variant is:

    candidates/rust/variants/compiler_allocation_fastpath_v1/lib.rs
    64228afb698f5326e6a30fd93c2ea27bd81653ecdd4a4a8e2b0dda5983e895b6
    178021 bytes

Seven reversible source replacements implement two changes: borrow the
caller's pattern only during synchronous parsing, and allocate alternation
storage only when a real alternation occurs. Authenticate the complete frozen
transformer, its separate application receipt, and all 960 synthetic semantic
checks, including 42 scanner-flag cases and 40 pattern-lifetime controls.

The search source is the unchanged canonical file:

    candidates/rust/src/search.rs
    4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe

Do not combine this experiment with the independently created required-
character search variant. That variant has a different `lib.rs` based on the
unoptimized canonical source; silently applying it here would remove these
parser improvements.

## Root-authorized offline build

Only after all three V27 owners are frozen, committed, and pushed may root
explicitly authorize the actual build. Each of two genuinely fresh private
source trees receives six unchanged canonical owners and exactly three
exclusive, synchronized, independently authenticated overlays:

    Rust parser source
    64228afb698f5326e6a30fd93c2ea27bd81653ecdd4a4a8e2b0dda5983e895b6

    Safe capture-clamping bridge
    a127ef85945a4dfa40a1b6c98f6c1a73ca7e1a487e190e8dde1d5aa2be47bb54

    Corrected public Python adapter
    d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e

Both private phases must genuinely execute all 14 pinned compiler or ELF
inspection roles, producing 28 distinct successful process IDs. The complete
engine files must match byte-for-byte across phases; so must the complete
bridges. The resulting engine must not be the old V25 engine. Preserve and
restore all nine canonical source owners and all five important original
runtime targets, including canonical `lib.rs`, the original bridge and Python
adapter, and both installed native files.

Use pinned Rust 1.95.0, GCC 13, and CPython 3.14.6. Cargo runs
`build --release --locked --offline --frozen` with one first-party package,
zero external dependencies, one job, and deterministic source-prefix remaps.
No standard-library regular-expression engine, external package, other
candidate, fallback, benchmark detection, or network access is permitted.

## Source-only boundary

Run `--self-test` and `--verify-frozen-context` under both the ordinary and
sterile environments with the exact pinned interpreter and `-I -B -S`. An
irreversible deny-default wall is installed before reading predecessor owners.
It rejects private roots, native binaries, candidate imports, compiler starts,
compressed archives, clocks, entropy, network access, hidden cases, and every
final-holdout file.

The proposed 141,557,760-case final holdout remains unopened and unfrozen.
Native output hashes, candidate correctness, memory, speed, confidence,
undefined-behavior safety, qualification, and any winner remain **NOT
MEASURED** until the corresponding independently authorized experiment.
