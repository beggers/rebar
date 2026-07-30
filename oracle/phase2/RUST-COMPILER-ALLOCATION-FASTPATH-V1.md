# First-party Rust compiler allocation fast path

Status: **SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN.**

This is a prospective, from-scratch Rust compiler experiment. It does not
wrap Python's matching engine, an existing regular-expression package, or
another candidate. The existing Rust crate contains exactly one package and
zero external dependencies. The original correctness denominator remains
**31,237** cases across **13** groups, with its named private waivers and the
separate **8,244**-case supplemental reference unchanged.

The most recent complete Rust correctness run failed **1,352** cases: **240**
replacement cases and **1,112** changing-buffer cases. It verified **15,877**
cases in completely passing groups. Its publication succeeded, but the Rust
candidate failed and remains unqualified. This compiler-only experiment
neither repairs nor conceals those failures.

The independently observed public practice run matched Python on **416** fresh
public cases and preserved all **1,664** paired observations. Those existing
observations are development evidence, not the hidden final comparison. The
proposed **141,557,760**-case final holdout remains **NOT FROZEN**, **NOT
GENERATED**, and **NOT OPENED**. This source-only experiment performs no new
timing, profiling, matching, native loading, or candidate execution.

The exact unchanged first-party source is:

```text
path    candidates/rust/src/lib.rs
SHA-256 c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d
bytes   177967
```

The derived variant makes exactly two semantic improvements:

1. `Parser<'a>` temporarily borrows the C-owned `&'a [u32]` pattern. Normal
   compilation and scanner phrases stop copying that input into an additional
   Rust `Vec<u32>`. The C bridge retains its stack, heap, or Unicode storage
   until the complete synchronous native compiler call returns. The parser,
   syntax tree, and compiled engine never retain the borrowed slice afterward.
   The Rust-only test helper explicitly owns its `Vec<u32>` while its parser
   borrows it.
2. `Parser::alt` parses its first branch before allocating branch storage. An
   alternation-free expression allocates no temporary branch `Vec`. An actual
   alternation starts with capacity two. Empty, leading, trailing, nested,
   escaped, class-contained, verbose-comment, global-flag, and scoped-flag
   alternatives retain their original behavior and diagnostic positions.

The complete, deterministic output is:

```text
target  candidates/rust/variants/compiler_allocation_fastpath_v1/lib.rs
SHA-256 64228afb698f5326e6a30fd93c2ea27bd81653ecdd4a4a8e2b0dda5983e895b6
bytes   178021
```

Exactly seven uniquely anchored, reversible source substitutions implement
those two improvements. The canonical Rust source, existing C bridge, current
capture-clamp variants, Cargo files, Python adapter, native binaries, and all
other candidates remain untouched. The source-only verifier authenticates the
complete original and its zero-dependency Cargo manifest/lock, the exact C
source-lifetime proof, the complete original correctness history, and all
preserved independently generated public practice records.

An installed deny-default audit and descriptor wall prevents candidate imports,
candidate or compiler processes, native library loads, clocks, network,
archives, workspace writes, hidden cases, and final holdout reads. Exactly one
metadata-only inspection confirms the unopened final comparison proposal.
Independent synthetic old/new parser models exhaustively preserve public
alternation trees, ordinary and scanner-specific runtime flags, and diagnostic
positions. Checked source-owner leases also reject early owner release,
use-after-free, stale views, and out-of-bounds access.

The root coordinator verifies both source-only modes normally and in a clean
environment using the independently pinned CPython 3.14.6 interpreter:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_compiler_allocation_fastpath_v1.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_compiler_allocation_fastpath_v1.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Only the root coordinator may materialize the derived source after committing
and pushing all three frozen owners. The same complete pushed commit must be
provided independently in both explicit authorization fields:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_compiler_allocation_fastpath_v1.py \
  --apply --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256 \
  --frozen-commit PUSHED_COMMIT --pushed-commit PUSHED_COMMIT
```

Application creates one new private directory and exactly one new regular
source file with `O_CREAT | O_EXCL | O_NOFOLLOW`. It cannot replace existing
files and does not compile or run the variant. Variant correctness, speed,
memory consumption, undefined behavior, and final ranking are **NOT MEASURED**.
