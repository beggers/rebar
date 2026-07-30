# First-party Rust exact-literal execution experiment V1

Status: **SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN.**

The existing combined Rust design is genuinely first-party: its parser,
compiler, execution engine, Python binding, and search implementation are
written in this repository. Its latest public measurement is **1.2298× Python**
across 416 cases, faster in 208 cases. It is not qualified and still differs
from Python in 1,145 of 10,434 wider public checks. These are historical public
observations only; this experiment's speed is **NOT MEASURED**.

This focused experiment composes an exact-case literal-search shortcut with the
already predicted, first-party scoped-Unicode correction. It uses only the
project's existing bounded byte-search helper, which itself uses the ordinary
platform `memchr` byte primitive. It does not use an external regex engine,
package, parser, compiler, generated answer, benchmark detector, or fallback
to Python's `re` implementation.

The immutable first-party parent is independently reconstructed from the
committed combined engine by applying the already frozen, one-site scoped
Unicode guard:

```text
combined original   c627012d0ce8d1e2cc3c70301956a060eecc6656f82137b219e44ec905f235ee
combined corrected  7412a997975aa42ec18249bc28d17e3c39223a4089bd23e3f7d2ab8112993b38
search source       4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7
target              candidates/rust/variants/exact_literal_fastpath_v1/lib.rs
```

The shortcut applies only when all of the following are proven from the
first-party parsed expression:

1. The root is an ordinary sequence containing only literal instructions.
2. There are no capturing groups.
3. The sequence contains between two and 32 complete byte-valued characters.
4. No literal uses case-insensitive or locale-sensitive matching.
5. The subject is either a bytes object or a one-byte Python text object.

All other patterns, empty expressions, single characters, non-ASCII-width
text, captures, alternatives, classes, anchors, repetitions, lookarounds,
conditional groups, locale-sensitive behavior, and case folding continue to
use the existing first-party Rust execution engine unchanged.

For eligible subjects, the native engine searches for the literal's final
byte using its existing safe first-party byte-search helper, then compares the
entire bounded candidate slice. It retains leftmost order, respects the
original physical subject length and the clamped `endpos` window, preserves
`search`, `match`, and `fullmatch` modes, sets all group-zero spans exactly,
and handles repeated non-overlapping collection without extra Python/native
crossings. Since eligible patterns are always nonempty, Python's special
empty-match progress rule remains in the unchanged original engine.

An independent bounded model checks candidate recognition, byte-valued text,
non-ASCII-width text, exact/locale/case flags, capture rejection, expression
shape rejection, all search modes, all bounded start/end windows,
non-overlapping collection, empty and singleton exclusions, high bytes, and
astral code points. It imports neither `re` nor any third-party engine, runs
no candidate, launches no subprocess, opens no raw public observations or
holdout, samples no clocks, and makes no workspace mutations.

The continuous, deny-default physical source wall authenticates exact
repository-relative, no-follow, owner-only plaintext source/evidence files by
device, inode, size, mode, owner, and complete SHA-256. It rejects imports,
native objects, dynamic execution, candidate processes, network access,
descriptor aliases, proposal/holdout metadata or contents, archives, timing,
all source-mode writes, and every nonexclusive target mutation. Root-only
materialization requires the complete freeze to be committed and pushed and
creates one new `0700` directory and one new `0600` `lib.rs` with
`O_CREAT | O_EXCL | O_NOFOLLOW`, synchronizing file and both directories.

Ordinary and sterile gates:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_exact_literal_fastpath_v1.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_exact_literal_fastpath_v1.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Repeat both commands under `env -i PATH=/usr/bin:/bin LC_ALL=C`.

Only root may apply the source after committing and pushing the exact three
freeze files:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_exact_literal_fastpath_v1.py \
  --apply --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256 \
  --frozen-commit PUSHED_COMMIT --pushed-commit PUSHED_COMMIT \
  --root-authorized --frozen-committed-pushed
```

Compatibility, speed, memory, undefined behavior, confidence, runtime
non-delegation, original-suite success, candidate qualification, and the final
comparison all remain **NOT MEASURED** until separate authorized runs.
