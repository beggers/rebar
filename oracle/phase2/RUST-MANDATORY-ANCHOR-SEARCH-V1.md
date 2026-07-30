# First-party Rust candidate-position search

This experiment changes only how the independently authored Rust matcher finds
positions worth checking. Its original parser, compiler, ordered matcher,
captures, backtracking, and Python-facing bridge remain responsible for every
actual regular-expression decision. It adds no package or alternate engine.

The already-preserved public practice run checks 416 cases against Python
3.14.6, with identical complete outcomes. Its four-round timing file contains
1,664 paired rows. The 416 rows in the dense-pattern group total 21,797,729 ns
for Python and 102,371,349 ns for Rust. One alternative-pattern search totals
254,724 ns for Python and 2,554,459 ns for Rust. These are public development
measurements, not a final benchmark or an unseen test.

The proposed first-party improvement derives necessary byte sets at fixed
positions directly from Rust's own parsed pattern. For example, both branches
of `AAAAAAB|AAAAAAC` require either `B` or `C` at position six. Required sets
are unioned across alternatives and conditions, fixed-width unknown characters
preserve their offsets, and uncertain case folding, locale behavior,
backreferences, variable widths, oversized sets, and wide Unicode subjects
conservatively retain the old behavior.

An adaptive two-position filter uses runtime-checked AVX2 when available and a
portable scalar search otherwise. It returns the earliest possible position;
the unchanged ordered Rust matcher still validates the complete match,
captures, assertions, and alternative priority. Pure ungrouped literals
already use the bridge's existing native string-search fast path and are not
the reason for this experiment.

The frozen transformer authenticates the original Rust source, one-package
zero-dependency Cargo lock, previous independently measured search experiment,
and all three complete public-practice evidence files. Source-only verification
physically blocks candidate imports, native libraries, subprocesses, clocks,
workspace writes, archive/holdout access, and unapproved file reads. Its
deterministic model compares original and filtered ordered matching across
opposite anchor densities, overlapping matches, empty windows, vector
boundaries, alternatives, captures, lookarounds, locale and scoped folding,
fixed/variable repetition, references, high bytes, and full-width Unicode.

Only a separately committed, pushed, explicitly root-authorized `--apply` may
create these new, exclusive files:

- `candidates/rust/variants/mandatory_anchor_search_v1/lib.rs`
- `candidates/rust/variants/mandatory_anchor_search_v1/search.rs`

The canonical candidate sources, existing bridge variants, native libraries,
and sealed final comparison are never changed or opened. Native compilation,
full candidate correctness, memory use, and the resulting speed improvement
remain **NOT MEASURED** until independently authorized later experiments.

Source-only reproduction:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/apply_owned_rust_mandatory_anchor_search_v1.py --verify-source
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/apply_owned_rust_mandatory_anchor_search_v1.py --self-test
```
