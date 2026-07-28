# Fix the actual Rust compiled-pattern flag order

This document freezes an evidence-backed, from-scratch source correction. It
does not apply a repair, rebuild or activate a candidate, run a compatibility
suite, measure speed, or open the final holdout.

## The actual current failure

The corrected Rust engine genuinely completed all 13 frozen Python test groups.
It still has 1,036 mismatches and 8,965 independently verified passing cases
against the unchanged 31,237-case denominator. The actual failure receipt is
`oracle/phase2/evidence/repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-original-p0-failures-publication-receipt.json`,
SHA-256 `201b7edc94d54f9ea2054f2eab98a68c83850def841ceade6a14c8db7d05cdd3`.
Its separate compressed archive has SHA-256
`2ab266d193728e1297382ed233a813c7ef62c0aa407355cf44fef6aaeffa134f`.

The first six actual groups pass. The seventh, `public_types_v1`, has 140
mismatches across its original 6,912 cases. The first actual failing case is
`pattern-and-match-representation/058`. Its complete 901-byte canonical
mismatch has SHA-256
`1130da7818fe8b27a0d74f607bd4531c43f5f12ec9d6674419aa448786884d75`.
For `(?P<word>[A-Za-z]+)(?P<number>[0-9]+)` and flags 258:

- Python expects
  `re.compile('(?P<word>[A-Za-z]+)(?P<number>[0-9]+)', re.IGNORECASE|re.ASCII)`.
- The tested Rust candidate returned
  `re.compile('(?P<word>[A-Za-z]+)(?P<number>[0-9]+)', re.ASCII|re.IGNORECASE)`.
- Both return the identical match representation
  `<re.Match object; span=(0, 7), match='Alpha42'>`.

The immutable frozen public-type evaluator is
`tools/independent_public_type_identity_serialization_v1.py`, SHA-256
`7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20`.
Its actual case evaluator returns `(repr(compiled), repr(match))`.

The expressly authorized forensic read consumed 1,179,658 compressed outer
bytes and expanded only the first 1,638,400 bytes, with prefix SHA-256
`9d90192b27a21c183b5208e87e4a86cf396a98306873aa7b570c1162d0a03c6d`.
The retained public-type observation has a compressed SHA-256 of
`1c2c54598d2642c9f3ed764e7cebf3498273defbf1242594bc9e394e8a90b8a0`.
Its separate inner forensic read expanded only 4,096 of a maximum 65,536
authorized bytes and stopped at the first complete mismatch. The inner prefix
SHA-256 is
`d865de60cfb433dc63b2cc2175f8f8e4ddf70465ba7ec9e8c20414a8a90622f3`.
Neither complete matching archive was inflated. Source verification never
repeats these forensic decompressions.

## Correct only the separately defined pattern representation

Version 2 correctly displays standalone `RegexFlag` values. Its exact tested
adapter is
`f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5`,
31,464 bytes. Do not reverse its standalone flag ordering: all 5,128 isolated
CPython `RegexFlag` examples must stay correct.

The actual defect is that version 2 also uses `repr(RegexFlag(flags))` when
rendering a compiled pattern. Python uses a separately ordered flag list for
compiled-pattern representations. Replace only that one uniquely anchored
compiled-pattern block. Keep standalone flags, `NOFLAG`, unknown bits, implicit
Unicode handling, public errors, equality, hashing, caches, scanning, pickling,
the native Rust parser, the executor, and the first-party bridge unchanged.

The resulting source is derived only in memory from the original owned adapter.
Its exact SHA-256 is
`d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e`;
its length is 31,934 bytes. A synthetic in-memory class reproduces the actual
failure and corrects it without importing or activating a candidate. It also
preserves all 5,128 standalone flags and validates compiled-pattern examples
derived directly from the real frozen CPython test source.

## Historical evidence is not current evidence

The published version-32 graph is an immutable historical snapshot with 153
evidence owners and 158 authenticated references. It must not be reported as
the current state after subsequent evidence is published.

The genuine Zig version-12 source build has since published two new owners:

- Its 48,371-byte build archive has SHA-256
  `3e0ccc41de392c17eaec64100776eacecafb3f0bb3355e18ef4d65fcdc79ea8d`.
- Its 2,029-byte publication receipt has SHA-256
  `6269fb49b67919e772ffbcdd211c696aae871971ab524bc0b1612a797d4c2f9b`.

The receipt authenticates 26 build processes, two actual first-party source
applications, and a current lower bound of 155 evidence owners and 160
references. It does not run or qualify the new Zig candidate. Last-tested Zig
still has 2,172 mismatches. Later append-only evidence remains allowed; the
version-32 graph is checked only as a historical snapshot.

The original denominator remains 31,237 cases, 13 groups, and 13 named private
exclusions. The separate 50-case callable-signature supplement is frozen; its
reference is **NOT RUN**. Rust remains failed with 1,036 mismatches, C remains
failed with 1,230, and last-tested Zig remains failed with 2,172. Correctness
after applying this source correction, undefined behavior, memory,
confidence intervals, and speed are **NOT MEASURED**. The final 4,194,304-case
holdout is **NOT OPENED**. There is no winner.

## Verify the frozen source before any future application

Independently pin the version-3 source, this explanation, and the exact
canonical machine contract in every `--self-test` and
`--verify-frozen-context` command. Run both modes with the pinned CPython
3.14.6 executable, `-I -B`, in ordinary and sterile environments.

The synthetic self-test physically blocks filesystem access, writes,
candidate and reference processes, candidate imports, networking, threads,
clocks, native loading, recovery locks, signals, and decompression. The
read-only context authenticates exact owner-only descriptors; it reads the
Rust matching archive and new Zig build archive as compressed bytes only.

Only a separately and explicitly authorized future `--apply` may create one
new exclusive, mode-`0600`, no-follow Rust source snapshot. It must be under
one of two distinct owner-only `reference-a` or `reference-b` directories in
`/tmp`, independently pinned to the exact 31,934 derived bytes. It must
revalidate the unchanged canonical adapter before and after creation. Applying
a source, compiling it, activating it, running it, and publishing actual
results are distinct future chunks. None occurs in this source freeze.
