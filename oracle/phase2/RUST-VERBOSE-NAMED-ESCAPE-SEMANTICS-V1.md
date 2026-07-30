# First-party Rust comment-aware Unicode named escapes V1

Status: **SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN.**

The Rust matching engine remains entirely first-party and unchanged. Its Python
adapter currently expands every textual `\N{...}` before the native parser can
recognize ignored comment contents. Consequently, an unknown or malformed
Unicode name in an inline `(?#...)` comment, an effective-global `VERBOSE`
line comment, or an enabled scoped `(?x:...)` line comment incorrectly raises
before Rust can parse the pattern. Pinned CPython ignores the whole comment.
Bytes never enter the named-Unicode resolver and must remain unchanged.

Exactly two immutable latest public development publication receipts are read:

    V26  oracle/phase2/evidence/rust-native-architecture-public-gate-v2-v26-anchor-public-run-001-publication-receipt.json
    SHA-256  23baf96a92f4fd2bf2809730bed056606de0c9c350ed46eea31fa9bdff6a8d80
    bytes    40906
    device   2064
    inode    525333

    V27  oracle/phase2/evidence/rust-native-architecture-public-gate-v2-v27-compiler-public-run-001-publication-receipt.json
    SHA-256  a825c358434fb44ab9d52eb8021271115b12e41c58b26243c7770faf4d533449
    bytes    68330
    device   2064
    inode    525426

Both receipts successfully published the complete 10,434-case public
development run; both candidates failed with exactly 1,145 semantic mismatches.
The smaller 416-case correctness gate passed, but that does not override the
failed complete gate, establish qualification, or make exploratory timing a
final result. Their executed private overlay adapter has SHA-256
`d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e`;
the immutable canonical adapter below is separately identified in each
receipt's complete before-and-after canonical-source ledger. No overlay,
native object, artifact archive, proposal, private source, or process is opened.

The only additional historical evidence is the original V25 plaintext ledger:

    oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-original-p0-v25-failures-publication-receipt.json
    SHA-256  d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59
    bytes    11832
    device   2064
    inode    524846

Its publication succeeded and the candidate failed: all 13 suites were fully
observed; 31,237 executed cases produced 1,352 semantic mismatches and 15,877
verified passing cases. The two failing suites remain exactly
`substitution_v2` with 240 mismatches and `shape_v2` with 1,112. Their passing
counts remain zero because incomplete-suite passes cannot be invented. All 13
named private waivers remain intact.

The frozen canonical input is:

    input   candidates/rust_candidate.py
    SHA-256 6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b
    bytes   31151
    device  2064
    inode   428100
    mode    0600

Source-only verification authenticates that input identity through both public
receipts without opening the canonical adapter. Only separately authorized
root-only materialization, after the frozen three-owner commit has been pushed,
may read the canonical file once.

The byte-anchored correction has exactly three reversible owned sites:

1. `_Native.compile` forwards its effective public flags to
   `_named_escapes(pattern, flags)`.
2. `_Native.compile_scanner` forwards the same effective flags for each textual
   scanner phrase.
3. The existing named-escape helper becomes a first-party lexical scanner that
   tracks global `VERBOSE`, nested enabled/disabled scoped inline flags, escaped
   characters, initial/negated character-class closing rules, `(?#...)` inline
   comments, and `#` line comments through their exact `LF` terminator.

Unknown, malformed, empty, unterminated, or multi-codepoint Unicode names are
resolved only outside ignored comments. Active lookups retain the original
`unicodedata.lookup`, `PatternError` messages, pattern object, and exact error
offsets, including names inside character classes. Escaped `#`, `(`, `[`, and
backslashes retain their original lexical meaning. Bytes, native engine calls,
public flags, warning behavior, capture semantics, bridge architecture, and
compile-cache behavior remain untouched. The production adapter imports neither
the standard-library matcher nor an external engine.

The complete modeled public correction partition is:

    text.comment.inline_unknown_named_unicode            108
    text.comment.global_verbose_unknown_named_unicode    108
    text.comment.scoped_verbose_unknown_named_unicode    108
    total                                                324

Each dataset contains 99 disjoint comment-only records, five scanner-overlap
records, and four substitution-overlap records. Across the three datasets,
these are exactly **297 + 15 + 12 = 324**. The arithmetic remainder
`1,145 - 324 = 821` is a source-only prediction, **not a measured candidate
result**; no other pattern correction is claimed. The independent lexical
witness executes at least 800 semantic cases, including all 324 modeled public
records, scoped enable/disable nesting, global inline flags, escaped newlines,
literal class `#`, initial class `]`, valid/unknown/malformed Unicode names,
byte patterns, and original error offsets.

The predicted exclusive immutable successor is:

    target  candidates/rust/variants/verbose_named_escape_semantics_v1/rust_candidate.py
    SHA-256 c1d150d467d5732eab4cc589f7e18583e59892592fb48d7d6f37700c00dccda0
    bytes   33256
    delta   +2105 bytes at exactly three reversible owned sites

Every self-test and source verification installs its deny-default audit and
descriptor wall before any owner read. Its only approved reads are the source,
this protocol, the contract, the V26/V27 public receipts, and the V25 original
ledger. It forbids candidate and native files, archive/proposal/final roots,
`.git`, imports, compiled or dynamically executed code, subprocesses, compiler
launches, network, clocks, candidate execution, and filesystem writes. Self-test
reads no workspace file at all. All source-only gates report zero candidate
reads, zero candidate execution, zero native opens, zero proposal/archive opens,
zero clocks, zero processes, and zero workspace mutations.

Use the isolated pinned interpreter for the two normal gates:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_verbose_named_escape_semantics_v1.py \
  --self-test

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_verbose_named_escape_semantics_v1.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Repeat those exact two commands under `env -i` for the two sterile gates; no
environment variable, configured import path, external package, or inherited
credential is required.

Only the root coordinator may materialize after all three owned files were
committed and pushed. The full frozen and pushed 40-character commit must be
identical and explicit root authorization is mandatory:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_verbose_named_escape_semantics_v1.py \
  --apply --root-authorized \
  --frozen-commit PUSHED_FROZEN_COMMIT \
  --pushed-commit PUSHED_FROZEN_COMMIT \
  --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

Root-only application creates exactly one new exclusive `0700` variant
directory and one exclusive `0600` `rust_candidate.py` using descriptor-relative
`O_NOFOLLOW | O_CREAT | O_EXCL`, fsyncs both, and verifies the durable complete
readback. Existing variants, the canonical adapter, Rust sources, README,
native objects, original evidence, and final holdout are never modified.

The former final holdout remains **INVALIDATED; REKEYED SUCCESSOR REQUIRED**.
Candidate correctness, runtime non-delegation, final performance, independent
qualification, native execution, and winner selection remain **NOT MEASURED**,
**NOT ESTABLISHED**, **NOT RUN**, or **false** as applicable.
