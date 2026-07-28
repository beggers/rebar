# Rust public flags: an observed first-party source correction, version 2

This is a source freeze, not a successful candidate, build, benchmark, or
private source application. The canonical Rust adapter, every native file,
the historical version-1 source freeze, all published evidence, and the
unopened performance holdout remain unchanged.

## The actual observed failure

The complete, 13-worker Rust correctness run genuinely failed 1,087 of the
31,237 frozen original Python checks. Its durable failure archive is
`oracle/phase2/evidence/repaired-rust-original-campaign-v3-rust-phase2-v11-rust-dual-overlay-original-p0-failures.json.gz`,
SHA-256 `3ac7736c127d13d3fad579c4ab9974c6a83612b4253f7921ed3e44269f3a82ad`.
An earlier, independently bounded inspection consumed 55,267 compressed bytes,
read 57,344 compressed bytes, and emitted exactly 1,048,576 uncompressed bytes;
it did not complete the gzip member or parse the complete archive. The first
actual recorded mismatch starts at uncompressed offset 7,270.

The genuine upstream method is
`PatternReprTests.test_flags_repr`, lines 2881–2893 of both the byte-identical
committed `oracle/cpython-3.14.6/test_re.py` and the separately located upstream
`/tmp/rebar-cpython/cpython-3.14.6-upstream-source/Python-3.14.6/Lib/test/test_re.py`.
Both exact test files have SHA-256
`879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2`.
The exact failing assertion, at line 2887, compares `repr(~re.I)`:

- Actual Rust V1 output:
  `re.LOCALE|re.MULTILINE|re.DOTALL|re.UNICODE|re.VERBOSE|re.DEBUG|re.ASCII|0x1`.
- Actual CPython 3.14.6 expectation:
  `re.ASCII|re.LOCALE|re.UNICODE|re.MULTILINE|re.DOTALL|re.VERBOSE|re.DEBUG|0x1`.

The installed, pinned CPython standard `re` is under
`/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/`.
The upstream test checkout does not contain a substitute `Lib/re`. Verification
authenticates the actual installed `__init__.py`, `_compiler.py`, and
`_constants.py` separately. It never imports an installed `test` package that
does not exist, and source-only verification does not execute the upstream
unit or start an oracle worker.

## Exactly one evidence-backed change to the prior repair

Preserve all three uniquely anchored, first-party Rust public-source repairs
from version 1. Change only the known-flag order within its private derived
flag block to `ASCII, IGNORECASE, LOCALE, UNICODE, MULTILINE, DOTALL, VERBOSE,
DEBUG`. Preserve `re.NOFLAG`, `re.RegexFlag(1024)`, and
`re.ASCII|0x400`; preserve the previous public error, pattern representation,
pattern equality, pattern hash, type-sensitive cache, buffer policy, scanner,
pickle policy, native bridge, and Rust parser, compiler, and executor.

The exact original adapter remains
`6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b`,
31,151 bytes. The historically failing V1-derived adapter remains
`81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c`.
The corrected V2-derived adapter is
`f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5`,
31,464 bytes. It is computed in memory, not materialized. The corrected
665-byte flag block is
`20809c0aba32650d9bbc62b22efb8d819473bd9baf774c3a9ce9174b36629220`.

An isolated, in-memory source-only comparison checks all six genuine upstream
assertion vectors and 5,128 signed, ordinary, and sparse values directly
against the actually installed CPython `RegexFlag`. It reproduces the
historical bad ordering and confirms the corrected public representation. This
is not a rebuilt candidate correctness result.

## Preserve current evidence and the phase boundary

Preserve the current V30 overview, all 149 evidence owners and 154
authenticated references, all 13 original suites, all 31,237 obligations, and
all 13 named private exclusions. Rust remains failed with 1,087 differences
and 7,438 verified passing cases. The current C remains failed with 1,230
differences and 7,325 verified passing cases; its separate historical result
remains 1,262 differences. Zig remains failed with 2,172 differences. Preserve
the distinct earlier Zig failure that started zero matching workers.

Read the Rust failure gzip only as a descriptor-bound, caller-pinned compressed
owner. Authenticate the small existing Rust, C, Zig, and preflight receipts.
Do not decompress any matching archive, run V1 verification, inspect a native
target, run a candidate, build Rust, open a hidden case, sample a clock, or
touch the final holdout.

Only a later explicitly authorized and independently caller-pinned `--apply`
may create the corrected public source. It can target a fresh, owner-only Rust
`reference-a` or `reference-b` private source snapshot under `/tmp`, with two
distinct `0700` phase directories, an exclusively created `0600` no-follow
destination, full source readback, and a verified unchanged canonical adapter.
Applying, compiling, loading, running, recovery, and publishing are separate
future chunks.

Run the caller-pinned `--self-test` and `--verify-frozen-context` in ordinary
and sterile `env -i` environments. Synthetic self-tests physically block real
filesystem effects, writes, candidate or reference workers, imports, networks,
threads, clocks, native libraries, locks, signals, and gzip inflation.
Candidate correctness after V2, undefined behavior, memory, speed, confidence
intervals, and any reduction of the actual 1,087 candidate mismatches are
`NOT MEASURED`. The holdout is `NOT OPENED`; no winner is selected.
