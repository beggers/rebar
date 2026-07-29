# Reconcile the Python compatibility oracle without hiding unfinished tests

Status: **source crosswalk PASS; complete phase-one gate BLOCKED**.

The original goal and all published results are preserved. This additive
record does not edit the original correctness matrix, rerun an engine, open a
compressed report, install a replacement, start a compiler, or open the final
comparison. In particular, a passing source-only verification is **not** a
passing replacement and is **not** permission to build or benchmark one.

## Keep the original test count

The pinned reference is CPython **3.14.6**. The original matrix still has
exactly **31,237** case executions in **13** independently identified groups.
Their case counts, in source order, are:

```text
151  864  1,024  768  1,024  2,854  6,912
5,120  10,240  1,376  128  264  512
```

The original Python source has **165** test methods: **152** public methods,
including **151** that run in the release build, and exactly **13** named,
private-implementation exclusions. `ReTests.test_memory_leaks` is the genuine
debug-build-only public skip; it is neither a passing case nor a private
exclusion. The original **403** upstream corpus cases and **11** external
fixtures remain authenticated.

All **45** inherited and **28** additional public obligations, and all **34**
original coverage mappings, are checked against their complete published
objects and independently pinned fingerprints. All thirteen original evaluator
sources are opened read-only and verified by exact SHA-256, size, device,
inode, private permissions, and complete file contents. Nothing is silently
added to the original denominator.

## Correct the real reference-context mistake

The historical public-type reference genuinely ran, but its fixture classes
were created as `__main__`; replacement tests import the same evaluator under
`tools.independent_public_type_identity_serialization_v1`. The original
script-context vector

```text
0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21
```

is therefore **FALSIFIED for candidate-facing comparison**. Preserve it; do
not alter the published report, waive the affected **96** original cases, or
erase a real candidate failure.

Two genuinely distinct, previously published pinned Python workers, process
IDs **81** and **82**, each completed all **6,912** original public-type
cases under the correct imported-module context. Their complete record vector
is:

```text
6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2
```

The independently reproduced **96**-case cache vector is:

```text
587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad
```

The corrected plaintext publication receipt is authenticated independently:

```text
oracle/phase1/evidence/public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0-publication-receipt.json
ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966
```

A publication `PASS` does not substitute for `reference_status: PASS`, two
completed workers, two distinct actual recorded process IDs, both complete
case vectors, and the unchanged matrix. The frozen version-4 case producer
and version-10 case controller already use the **corrected** vector; their
actual historical candidate results must be preserved.

## Keep the extra 8,244 tests separate and blocked

The already frozen, plain-text property and differential fuzz corpus is:

```text
oracle/v2/expected.jsonl
7,602,476 bytes
8,244 complete, newline-terminated records
ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2
```

The verifier streams every byte, independently parses all **8,244** unique
records, checks all **19** frozen case-kind totals and all **45** inherited
obligations, and never loads the corpus as a single object. The largest actual
record is **83,668** bytes; the strict per-record bound is **262,144** bytes.
It independently authenticates all seven v2
protocol, suite, runner, manifest, seeds, corpus, and historical-result
owners. It also authenticates the complete v1 parent closure, including its
separately streamed **2,048** original corpus records.

The historical result records one Python `re` self-comparison passing
**8,244/8,244**. It records **no independent reference-worker process IDs**.
Therefore:

```text
Historical single-context Python result: PASS
Two independently recorded Python references: NOT RUN
Replacement run against all 8,244 cases: NOT RUN
Replacement qualification: NOT ESTABLISHED
```

The predecessor's two old abstract private labels are historical metadata,
not named CPython test-method exclusions. **Zero** are inherited into the
thirteen original private exclusions. The original count remains **31,237**.
The arithmetic **31,237 + 8,244 = 39,481** describes two separately counted
groups, not a silently enlarged or semantically deduplicated original suite.

## Other separately counted requirements

- The **50** callable-signature observations have a real, passing two-Python
  reference. Replacement observations are **NOT RUN**.
- The **32** public-import source observations preserve the actual
  `import rebar as re` entrypoint as **FAIL**: it exposes an unqualified Zig
  prototype and does not supply `__version__`.
- Another **32** independently frozen source observations preserve Python's
  two genuine **2,147,483,648**-character original tests. The historical
  Python reference passed; both full-size replacement tests are **NOT RUN**.
  The existing small-input controller caps its exercise at **5,147**.
- The **32** module-version observations in the existing shared-thread suite
  are already included in its **512** original cases. Do not add them again.
- Runtime proof of non-delegation is **NOT ESTABLISHED**. Speed, memory,
  native safety, and the unopened final comparison are **NOT MEASURED**.

## Interpret the gate correctly

`phase1_canonical_candidate_context_crosswalk: PASS` means that the unchanged
31,237-case matrix, all its owners and mappings, and the corrected public-type
reference have been consistently authenticated. It does **not** mean that
phase one is complete.

The canonical machine contract therefore has top-level `status: BLOCKED`, a
`BLOCKED` phase gate, and `candidate_evaluation_authorized: false`. The
existing version-17 native-build gate must continue to reject this contract.
It cannot become `PASS` until the extra fuzz corpus receives two genuinely
independent recorded Python references and the remaining required candidate
and public-behavior observations are completed.

## Reproduce the source-only verification

The only three new owners are:

```text
tools/verify_owned_p0_completeness_v2.py
oracle/phase1/P0-COMPLETENESS-V2.md
oracle/phase1/p0-completeness-v2.json
```

Independently compute their exact SHA-256 digests. Substitute them for
`SOURCE_SHA256`, `PROTOCOL_SHA256`, and `CONTRACT_SHA256`:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/verify_owned_p0_completeness_v2.py --self-test \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/verify_owned_p0_completeness_v2.py --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

Repeat both commands under `env -i PATH=/usr/bin:/bin LC_ALL=C`. The ordinary
and sterile output must be byte-identical for the same mode. Both report the
source-only check as `PASS` and the complete phase-one gate as `BLOCKED`.

The hostile self-test physically denies matcher and candidate imports,
external native loading, temporary files, compressed reports, hidden cases,
networking, process execution, clocks, and writes. It also rejects duplicate
JSON keys, changed denominators, invented or missing obligations and waivers,
inferred Python worker IDs, historical/corrected vector swaps, premature
candidate authorization, fabricated fuzz references, fabricated candidate
passes, and false full-size or public-import results.
