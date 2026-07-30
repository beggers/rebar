# Combined first-party Rust engine with corrected scoped Unicode handling

Status: **SOURCE FROZEN; CORRECTED COMBINATION NOT MATERIALIZED; NOT BUILT;
NOT RUN.**

The complete original Python compatibility denominator remains exactly 31,237
cases across 13 suites. The last completed original Rust run failed 1,352
cases: 240 substitution differences and 1,112 match-shape differences. The
separate public development comparison contained 10,434 cases, with 1,145
known differences. Published failure evidence does not qualify a candidate.

Two of those public differences expose an unsafe Rust acceleration for scoped
Unicode categories under a globally ASCII pattern:

```text
rust-public-practice.v2.04362  pattern.search.pos_endpos
rust-public-practice.v2.04371  pattern.finditer.pos_endpos

pattern  (?P<word>(?u:\w+))(?P<number>\d*)
subject  café42
flags    ASCII (256)
pos      3
endpos   6
expected é42 at [3, 6)
previous 42  at [4, 6)
```

The independently frozen and materialized first-party scoped-Unicode fix
changes exactly one existing start-set safety guard. The independently frozen
and materialized first-party optimized Rust engine combines its mandatory-byte
search and reduced-allocation compiler. This experiment applies the already
proven one-site correction to that exact optimized source; no parser,
compiler, virtual machine, search implementation, dependency, or other byte is
changed:

```rust
if locale_byte_flags(global_flags)
    || contains_locale_sensitive_expression(root)
    || has_scoped_category_prefix(root, global_flags)
{
    return None;
}
```

```text
existing materialized standalone scoped correction
candidates/rust/variants/scoped_unicode_startset_v1/lib.rs
SHA-256 e5971616329a1622a7514954ec26871ff8465db87ad1a956cea104ee8a8478ac
bytes   178037

existing materialized optimized combined engine
candidates/rust/variants/combined_search_compiler_fastpath_v2/lib.rs
SHA-256 c627012d0ce8d1e2cc3c70301956a060eecc6656f82137b219e44ec905f235ee
bytes   189423

corrected optimized combined engine, not materialized
candidates/rust/variants/combined_scoped_unicode_engine_v1/lib.rs
SHA-256 7412a997975aa42ec18249bc28d17e3c39223a4089bd23e3f7d2ab8112993b38
bytes   189493

unchanged optimized first-party search source
candidates/rust/variants/combined_search_compiler_fastpath_v2/search.rs
SHA-256 4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7
bytes   24305
```

The complete standalone freeze and its successful root application authenticate
both exact public failures, a previous 42,718-case independent bounded proof,
and the exact combined result predicted before this experiment. A fresh
independent bounded expression model exercises scoped and global Unicode/ASCII
categories and classes, groups, repetitions, nullable prefixes, alternatives,
conditionals, bytes, locale bytes, ordinary required anchors, non-ASCII and
astral characters, and every bounded search interval. It reproduces the exact
legacy `[4, 6)` result, restores `[3, 6)`, and checks that unaffected
accelerators remain unchanged. This model executes no candidate.

Verification authenticates the original completeness ledger, its actual Rust
failure, both materialized first-party lineages, the zero-dependency Cargo
manifest and lock, canonical Rust source, the independent mandatory-anchor
source, and the optimized engine and search files. The standalone correction is
first rederived from canonical bytes and compared with its actual materialized
source. The optimized correction is then derived once, checked against the
previously committed prediction, checked for exact reversibility, and proven
to preserve every other source byte.

An irreversible deny-default descriptor and audit wall is installed before any
owner read. It opens no candidate, native binary, raw public observation,
archive, private build root, proposal, hidden case, holdout, or final metadata.
It performs no import, candidate process, compiler process, timing, or source
mutation. Hostile controls cover descriptor aliases, metadata, imports,
execution, clocks, forged authority, Linux's complete `O_TMPFILE` composite,
and malformed or nonfinite evidence.

Only the root coordinator may create the corrected source after this complete
source/protocol/contract triple is committed and pushed. Root supplies all
three exact hashes, two matching complete pushed-commit hashes, and both
explicit authorization flags. The continuous wall creates one new `0700`
directory below the pinned existing variants parent and one new `0600`
`lib.rs` using `O_CREAT | O_EXCL | O_NOFOLLOW`. The source, its directory, and
its parent are synchronized; existing candidates remain untouched.

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_combined_scoped_unicode_engine_v1.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_combined_scoped_unicode_engine_v1.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_combined_scoped_unicode_engine_v1.py \
  --apply --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256 \
  --frozen-commit PUSHED_COMMIT --pushed-commit PUSHED_COMMIT \
  --root-authorized --frozen-committed-pushed
```

Composed native correctness, speed, memory, confidence, undefined behavior,
qualification, and final comparison remain **NOT MEASURED**. No final
benchmark is opened, generated, frozen, or run by this source experiment.
