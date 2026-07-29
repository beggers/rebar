# Freeze a first-party one-pass Rust literal build, version 20

This is a source freeze, not a successful compatibility test or a speed
measurement. It prepares an independently reproducible build of the existing
first-party Rust engine with one narrowly reviewed Python-boundary change:
collect exact literal `findall` matches in one pass instead of counting every
match and then scanning the subject a second time.

Preserve all nine original Rust source owners, the zero-dependency Cargo lock,
the existing Rust matcher, the corrected public adapter, and the full audited
version-2 buffer, shape, replacement, and pickle bridge. Authenticate that
version-2 predecessor at SHA-256
`afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740`
and exactly 179,961 bytes. The independently authored one-pass bridge is
`candidates/rust/variants/buffer_shape_pickle_findall_v1/py_bridge.c`,
SHA-256
`b707e924a23980385b0c5b0306daecd55bbb03d6f2511437f0532b6d39b2a112`,
exactly 178,950 bytes. Prove that the two complete files have identical prefix
and suffix and differ only in the exact literal `findall` function. Preserve
Unicode and bytes, clamped windows, PEP 688 buffer lifetimes, complete-subject
bytes identity, owned-list append behavior, allocation failures, and the
underlying Python error. This static proof is not a correctness execution.

Authenticate the independently reviewed one-pass feature verifier, its
protocol, and its complete machine-readable source-freeze contract, in order:

    21fb0878e344ead0bba49f932120a35a897ca44cfd7710287861ebc6415c555e
    842d51127db54a26d0dd9f874f38834f122f7888ea71c6f3fe77b8911bbd65d6
    a2226d823610a578aeb65e9a51a2a33517348b6c51130ad89db840cc50833164

Authenticate the latest independently published, still-unopened expanded
final-test proposal by reading only its bounded public verifier, protocol,
and 71-field canonical proposal contract, in that order:

    3dd9abcbd7a87486186ee8da804de595e65d79020a3fe33413d0157dde4f3309
    818f1636d87ae721912f04a3fc8294ac04a59dff4a272319aa29a393f52a4fd4
    676aac4f48c9404f5253c89b692efde5c425170f8d9f152b4f85b3e2a5225a76

The current proposed denominator is **14,155,776**, not the earlier
**4,194,304**. Both numbers describe unopened proposals; retain the smaller
number only as documented historical evidence in the independently frozen
one-pass feature and version-86 graph. The new proposal remains PRE-PHASE-3,
NOT FROZEN, NOT GENERATED, NOT OPENED, and NOT RUN. Authenticating its
public source does not run its verifier, create a case, generate a secret,
sample a clock, or authorize a benchmark.

Authenticate the genuinely published version-19 source, protocol, and machine
contract, in that order:

    650b33a10d253e09d48a423d12c8a1bb8180af4c4e96222aa13e72c75427bb5c
    4cdc322b2a516b28bf771440202efaca77074f7c8cd31c25692dc6ffc81797b5
    78e31d32cd17e100613ea98cecec4051ca2f6563b0d3b198c66f69501171ac46

Authenticate its actual successful 28-process publication receipt and separate
actual no-follow private-root provenance receipt, in that order:

    27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc
    de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99

Use the receipts to authenticate historical archive and private-root metadata.
Do not open, inflate, or hash any archive; do not reopen or scan `/tmp`; and do
not load any historical native library. Preserve every genuine earlier result.

Bind the current published version-86 overview source, inputs, complete
summary, and SVG, in that order:

    49c529c7f8b695c501dd03f9d35056c2853c73fcd36425718d8bfceb599b1a7d
    42c534652a350eada8704581ebf8aa52c77687b6904e9fb486f03c2f117cbe6c
    ed728687e919410e6e9dae22ad3c976aa900d7a857f85231aaa93d0fc674f7cc
    4bbf196a48997dbee3ea6b966d9a4eefce860962861675ad202506f685a80e55

The frozen original Python suite remains 31,237 cases in 13 groups with 13
named private waivers. The additional 8,244 reference cases remain a separate
denominator. The complete historical Rust comparison remains 1,440 semantic
differences and 14,853 verified passes. Its later guarded version-15 attempt
completed only 8 of 13 groups, recorded 12,942 verified observations and five
actual worker failures, and did not establish its full semantic mismatch count.
Neither result is a passing replacement. Qualification remains blocked.

Only a separately authorized, caller-pinned future `--build` may compile the
new bridge. Use label `phase2-v20-rust-literal-findall-root-provenance`, pinned
first-party Rust 1.95, `--release --locked --offline --frozen`, two genuinely
distinct private phases, the exact original 14 compiler and ELF-inspection
roles per phase, seven unchanged source snapshots and two genuine private
overlays per phase, and complete byte-for-byte verification of both native
engine and bridge outputs. During the actual original reproducibility callback,
capture only the live, owner-private `0700` root with
`O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW`. Publish a fresh failure or
success archive and receipt using exclusive no-follow creation and directory
fsync; publish a root-provenance receipt only after an actual successful,
complete 28-process build.

The source-only self-test and frozen-context verification must physically
prevent matching imports, native loading, candidate or reference workers,
compiler processes, clocks, network, writes, temporary roots, private-root
scans, historical archives, and holdout access. Their synthetic process and
native examples are controls, not real builds.

The pre-existing 864-case practice collection exercises zero exact-literal
`findall` cases. It cannot establish a speed improvement for this change.
Before timing, independently freeze a representative, correctness-gated
development collection that actually exercises the new behavior. Keep the
14,155,776-case final holdout not frozen, not generated, and not opened.

Actual version-20 compiler processes: 0. Version-20 root provenance: NOT
MEASURED. Candidate matching: NOT RUN. Compatibility, speed, memory,
statistical confidence, and undefined behavior: NOT MEASURED. Runtime
non-delegation: NOT ESTABLISHED. Qualified candidates: 0. No winner selected.
