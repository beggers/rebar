# Rust public compatibility: private source repair, version 1

This is a source freeze, not a passing candidate or a performance result. The
real Rust candidate and every recorded failure remain unchanged.

## What the historical tests established

All 13 original CPython suites, 31,237 counted cases, and 13 named private
exclusions stay unchanged. The published version-22 overview retains 105 real
evidence files and 110 separately authenticated history paths.

The original Rust candidate remains unqualified. Its signed results contain
2,042 actual differences: 1,392 shape-changing buffer differences, 336
replacement differences, 248 public-type differences, and 66 additional
public-surface differences. Its interpreter result remains an infrastructure
failure, not a successful matching result. The corrected C run also remains a
preserved infrastructure failure: matching was NOT MEASURED.

Two independently recorded Python reference workers show that all 66
public-surface differences are the formatting of unknown regular-expression
flags. The signed public-type history independently identifies the module name
of the owned public exception, flag order and formatting, and equality between
value-equivalent patterns from string subclasses.

## Exactly three independently implemented source changes

The frozen repair derives a separate Rust Python adapter from the unchanged
first-party candidates/rust_candidate.py. It changes exactly three uniquely
identified source blocks:

1. Give the owned PatternError its Python-compatible public module name.
2. Display known flags in Python order and display an entirely unknown value
   as re.RegexFlag(decimal).
3. Keep a compiled pattern's original bare hexadecimal display for an
   entirely unknown flag while comparing and hashing patterns by their pattern
   value and flags.

The existing type-sensitive compilation-cache keys remain byte-for-byte
unchanged. Buffer handling, replacement handling, scanner behavior, matching
and parser implementation, native bridge, Cargo files, generic aliases,
pickling, every other Rust source file, and all third-party dependency rules
remain unchanged. No regex package, Python regex engine, other candidate, or
fallback is introduced.

The original source has SHA-256
6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b
and contains 31,151 bytes. The derived source has SHA-256
81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c
and contains 31,464 bytes. The derived source has not been materialized.

## Private application only

An explicit future application may create candidates/rust_candidate.py only
inside a new, owner-only Rust reference-a or reference-b source snapshot under
/tmp. Both independent phase directories must exist, have mode 0700, and have
different identities. Every directory is opened without following links.
The private derived file is created once with O_CREAT, O_EXCL, O_NOFOLLOW and
mode 0600. Its complete contents are re-read and authenticated. Existing
destinations, the current working tree, candidate activation, builds, and
native-library loading are forbidden.

## Verification and honest results

Source-only self-tests use synthetic inputs and block real filesystem access,
candidate imports, subprocesses, network access, clocks, and private source
application. Read-only verification authenticates all nine Rust source
owners, the dependency-free Cargo lock, all 16 preserved Rust historical
evidence and receipt files, all original 13 suites, both genuine public
references, the exact 66 historical public failures, and the published V21
and V22 histories. It separately verifies both real corrected-C failure
owners without claiming that C matching occurred.

Both ordinary and minimal-environment gates are required before any future
private application. Rust correctness after this source change, candidate
qualification, speed, memory, and undefined behavior are NOT MEASURED. The
performance holdout remains NOT OPENED. No winner is selected.
