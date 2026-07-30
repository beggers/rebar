# First-party Rust scoped-Unicode start-set soundness correction V1

Status: **SOURCE FROZEN; CORRECTED VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN.**

The complete original correctness denominator remains 31,237 cases across 13
original suites. The last complete original Rust campaign failed: 240
substitution mismatches plus 1,112 shape mismatches, 1,352 total, with 15,877
verified passing cases. Durable publication of that failure was successful;
the candidate was not. Independently published V26 mandatory-anchor and V27
compiler-allocation architectures each failed 1,145 of the separate 10,434
public development cases. Neither architecture qualifies, and these public
results never replace, enlarge, or reduce the original correctness denominator.

After the separately owned scanner, substitution, and lexer corrections, the
two remaining distinct public first-party engine failures are:

```text
rust-public-practice.v2.04362  pattern.search.pos_endpos
rust-public-practice.v2.04371  pattern.finditer.pos_endpos

dataset  text.scanner.scoped_u_override
pattern  (?P<word>(?u:\w+))(?P<number>\d*)
subject  café42
flags    ASCII (256)
pos      3
endpos   6
expected é42 at [3, 6)
actual   42  at [4, 6)
```

These exact case identifiers and bounds are reconstructed from the authenticated
published seed, operation order, dataset order, and benchmark source using an
independent CPython-compatible MT19937 implementation. No raw correctness
observation or generated benchmark file is opened by this freeze.

The first-party parser and VM already preserve the scoped Unicode lexical mode.
The bug is the accelerator: `add_starts` replaces the local category/class
`A | L | BYTE` flags with global ASCII flags, and `wide_prefix_allows` makes the
same substitution. Therefore `search::StartSet` rejects the actual `é` start
before the correct VM can run. The existing `has_scoped_category_prefix` helper
already recognizes this precise unsafe condition through sequences, groups,
repeats, alternatives, conditionals, category leaves, and class leaves. Extend
the existing `start_table` safety guard by exactly one condition:

```rust
if locale_byte_flags(global_flags)
    || contains_locale_sensitive_expression(root)
    || has_scoped_category_prefix(root, global_flags)
{
    return None;
}
```

This disables only an unsound leading-category/class accelerator; parser flags,
scanner flags, Unicode VM category/class behavior, locale-byte guards, unrelated
literal start sets, first-party mandatory-anchor search, and compiler-allocation
improvements remain unchanged. The canonical standalone source and both
independent composition results are predicted exactly and reversibly:

```text
unchanged canonical engine
candidates/rust/src/lib.rs
SHA-256 c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d
bytes   177967

standalone corrected engine
candidates/rust/variants/scoped_unicode_startset_v1/lib.rs
SHA-256 e5971616329a1622a7514954ec26871ff8465db87ad1a956cea104ee8a8478ac
bytes   178037

corrected mandatory-anchor composition, not materialized
SHA-256 b5172d0506b67f484254f4488b8023591c353cb40140e652b4f993875d3ea1ab
bytes   189439

corrected combined mandatory-anchor plus compiler composition, not materialized
SHA-256 7412a997975aa42ec18249bc28d17e3c39223a4089bd23e3f7d2ab8112993b38
bytes   189493

unchanged combined mandatory-anchor search implementation
SHA-256 4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7
bytes   24305
```

A bounded independent differential model checks scoped `(?u:)` under global
ASCII, scoped `(?a:)` under global Unicode, direct and nested category/class
prefixes, repeats, nullable prefixes, alternatives, conditionals, global ASCII,
ordinary Unicode, bytes, locale bytes, non-ASCII and astral code points,
multibyte text, and every valid bounded `pos`/`endpos` pair. The legacy model
reproduces the exact `[4, 6)` failure; the corrected model restores `[3, 6)`
without introducing any unrelated semantic difference or changing unaffected
start-set acceleration.

Normal and sterile verification each run both `--verify-source` and
`--self-test` under the exact pinned CPython 3.14.6 executable with `-I -B -S`.
An irreversible deny-default audit and descriptor wall is installed before any
owner read. It authenticates the original ledger, the actual original failure,
the public matrix freeze, both V26/V27 native build and root receipts, both
V26/V27 public failure receipts, the existing combined-source freeze and
application, and only the exact first-party plaintext Rust owners. It opens zero
raw observations, archives, installed native libraries, private build roots,
final cases, holdouts, or final metadata. It runs zero candidates, processes,
timers, clocks, regex engines, external packages, or filesystem writes.

Only the root coordinator may materialize one fresh standalone source after the
complete source/protocol/contract freeze is committed and pushed. Root must
provide exact independent hashes, two matching complete pushed-commit hashes,
and both explicit authorization flags. The continuous wall then authenticates
the exact existing private Rust-variants parent, creates one fresh `0700`
directory, and exclusively writes one `0600` `lib.rs` using
`O_CREAT | O_EXCL | O_NOFOLLOW`; the file, child, and parent are synchronized.
Existing canonical Rust sources and existing architecture variants are never
edited, overwritten, or deleted.

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_scoped_unicode_startset_v1.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_scoped_unicode_startset_v1.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_scoped_unicode_startset_v1.py \
  --apply --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256 \
  --frozen-commit PUSHED_COMMIT --pushed-commit PUSHED_COMMIT \
  --root-authorized --frozen-committed-pushed
```

Corrected native correctness, speed, memory, confidence, undefined behavior,
qualification, and final comparison remain **NOT MEASURED**. This freeze does
not authorize a candidate run, a final holdout, a benchmark winner, or a
materialization by a delegated author.
