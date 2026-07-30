# Full wider-public correctness for the original-qualified Zig engine

This experiment applies the same frozen, published wider-public oracle already
used for Rust to the independently written Zig regular-expression engine.
Python 3.14.6 remains the isolated standard-library reference.

The exact Zig source-built candidate already passes all 31,237 original Python
checks, in 13 independently isolated workers with zero mismatches. Its
original-pass publication is
`b2762eaea6dd505aa34bd446996b0464b7a0e057e7fb7162355885e065e19bd0`.
The earlier complete 1,156-mismatch Zig failure remains preserved.

## Frozen public oracle

The unchanged public corpus contains 10,434 cases from 94 datasets and all
111 independently frozen Python operations. Exactly 5,217 cases use text and
5,217 use bytes. Each operation occurs once per dataset, with equal weights.
The published seed is `5928217332825411634`, and the unchanged matrix hash is
`0c88d1ec7066ede05466c1a91126086cd52256548eda13a31778ff284439d97d`.

Operations include module and compiled-pattern calls; matching, searching,
full matching, collection, splitting, substitutions, callback failures,
buffer exporters, changing subjects, match groups and spans, scanner
lifetimes and pickle behavior, signatures, cache behavior, and object
lifecycles. No operation, dataset, weight, seed, or case identifier is
altered for Zig.

The unchanged Rust wider-public harness source is independently authenticated
at SHA-256
`a3d7e70343d231bf433fbad6a6669025a970d83691c49cb9f434a186aef3d9e6`.
A narrowly defined in-memory transformation changes only first-party candidate
module and native-extension names, plus the candidate-presence assertion
required after installing the stricter runtime guard. Its exact result is
`dfb0eaa7cef2ff96562e663ac774d02463e445f3bb5a015bfda471c684350b49`.
The complete 111-operation AST remains unchanged.

## Exact independently built Zig candidate

The authenticated V17 build completed 26 independent compiler processes over
two separately owned source-build phases. Its first-party sources are:

- Zig engine: `a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28`;
- C-to-Python bridge:
  `4228199b7c65c4d02a78e0e9764a52aed63ff9a4c8230381925d5d3f2eb588ac`;
- Python adapter:
  `a6587f43112cc54f2fbf86c8c62ea28426950caae94c6fce2ccead61fcc0f124`.

The exact reproduced native engine is
`caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071`;
the exact native bridge is
`34c75d06820f9ec3495c9da3158e2f571aee753e58b62a369ea59336130b380b`.
Independent native audits report zero standard-library matching engines,
external regular-expression dependencies, and cross-family engines.

The immutable V4 first-party runtime guard is installed inside the isolated
candidate worker before importing the Zig adapter. Its sole narrow
compatibility exception permits the bridge's preauthenticated nonmatching
`copyreg` import. The standard-library oracle runs in a completely separate
worker and never imports a candidate.

## Source gates and actual execution

The source-freeze controller installs a deny-default physical audit wall
before authenticating any public source or receipt. Ordinary and sterile
self-tests and frozen-context verification must pass. These source-only gates
do not open candidates, private roots, native libraries, compressed archives,
raw benchmark results, hidden holdouts, or proposed holdouts; they start no
workers and sample no clock.

Only after the source, protocol, and complete contract are committed and
pushed may root authorize an actual run. The exact previously successful V18
three-role activation and recovery machinery authenticates and temporarily
activates the original-pass V17 Zig build. Every preexisting candidate file is
restored at its exact original inode even if either worker fails.

One isolated CPython reference process and one strictly V4-guarded isolated
Zig process each execute all 10,434 cases. Every baseline record, candidate
record, and mismatch is durably published without truncation or cherry-picking.
A successful publication is not a candidate correctness claim: candidate PASS
requires zero actual mismatches.

Correctness: NOT MEASURED. Runtime independence: NOT ESTABLISHED.
Performance, memory, and undefined behavior: NOT MEASURED.
No hidden cases are read. No candidate is qualified and no winner is selected.

