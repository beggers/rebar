# Current-build correctness proofs: V10

This protocol adds V10 evidence only. It preserves the genuine V8 and V9 failures, the original correctness suites, all independently implemented candidates, and the existing full CPython baseline. A diagnostic cannot qualify a candidate. Performance is **NOT MEASURED**. The holdout is **NOT ACCESSED**.

## Unchanged reference and original correctness

Use the frozen, isolated CPython 3.14.6 reference and Unicode 16.0.0.

- Original edge producer: `tools/rust_v7_edge_oracle.py`, SHA-256 `fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca`. Preserve all **223,198** observations, all **49** categories, seed `2026072329`, the six independent generation seeds, all **eight** seeded cases, Unicode stride `4099`, and reference SHA-256 `b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526`.
- Original deep producer: `tools/rust_v8_multi_candidate_contract.py`, SHA-256 `167f9d9114f95cd9c9821465339264f8b6eca9bf7f70b84774f4108f62f11a70`. Its original suite is `tools/rust_v8_deep_contract_oracle.py`, SHA-256 `ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978`. Preserve both separate CPython workers, all **393** observations, all **64** seeded cases, seed `2026072347`, reference SHA-256 `b184f3388320909b3c28fbd3ce9c15cefc992d3e852e9495ad8fb503d1cbaad8`, and every observed mismatch.
- Genuine public guard: `tools/python_re_universal_public_oracle_stage07.py`, SHA-256 `150abcfc597658f48d64c04053889bd4b299c75ad7413bc1cafa5f864e9e7c25`.
- Full V5 official CPython reference: `oracle/cpython-3.14.6/evidence/postfinal-locale-v5-self-oracle.json`, SHA-256 `3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916`. Authenticate the complete original document using the genuine frozen V5 oracle, including both genuinely isolated roles, all **152** public methods, all **151** applicable passes, the sole exact named private skip, exact status vectors, stderr provenance, and the real memory resources.
- Preserve every genuine historical Rust, C, and Zig edge failure, respectively SHA-256 `3ffdb21d10f40deabd70fa1f408fa38ff2b027a2d269c4b75e607a05cefde3b8`, `2cce7c26d2487c8e400d2fd6b8cfbc81d4b734b08f7a8f356def910a9cbb385c`, and `5fa7283942994139d531593cc1bdf25f5da48f6de424d7604ce2ce569100788a`.
- Preserve the actual V8 pre-import Rust failure exactly, SHA-256 `2f8bfcba726d729865cb8411a25ef1c3e0633e80c70af8895e5875a71f15ed7b`.
- Preserve the actual V9 Rust pre-import cached-child guard failure exactly, SHA-256 `04e52f831534458e9af50ad3ab962d78ad43e6a8725cbfccfee37bf9c234f07c`. This is a complete real **failure**, not a qualification, replacement, synthetic record, or pass.

## Correct the actual V9 cached-module guard failure

Use the genuine frozen stage07 `_ForbiddenRegexModule` blocker and genuine stage07 `_poison_cached_module_aliases` helper. Discover live cached `re._compiler` and `re._parser` modules and all other actual loaded `re.*` descendants. Poison their `sys.modules` entries and all retained module references with the **same exact stage07 blocker object**. Require the exact blocker type, root and descendant `sys.modules` identity, cached reference identity, and blocked import behavior before and after real native text and bytes matching. A module-shaped substitute, an independently constructed blocker, a subclass, a same-name forgery, a surviving cached alias, a real Python regex function, a restored live module, or fabricated observations fails.

Every actual V10 native worker must record complete `stage07_guard_sentinel` and `stage07_matcher_descendant_guards` evidence, the pinned original stage07 source, exact `re._compiler` and `re._parser` descendants, exact complete before-and-after per-descendant observations, and true all-alias and before-and-after verification. Validate both records with the actual frozen V10 native owner and independently fail closed. Require all **13** real forbidden regex entry points, all **five** native-loader guards, all **16** ordinary public `Pattern` and `Match` pickle round trips per candidate, authentic matching representations, and a genuine current owned candidate graph.

Preserve **three** genuinely independent families, exactly **12** owned sources and **five** native binaries: Rust owns all **seven** of its source files and both its bridge and engine; C owns both sources and its own native engine; Zig owns all three sources and both its bridge and engine. Never delegate matching, wrap a third-party engine, substitute another family, weaken the guard, or execute an earlier V8/V9 worker.

## Authenticate real V10 all-family reports first

Qualified modes require explicit, independently observed actual `--base-report-sha256` and `--strict-report-sha256`. After authenticating only immutable protocol and source code, authenticate the **entire** actual V10 base report and the **entire** actual V10 strict report using the final frozen V10 validators. Validate all three original real worker records, the exact graph, all **48** ordinary public pickles, all **39** regex guards, all **15** loader guards, complete root and cached-descendant sentinel identities, and strict report binding to the actual base bytes. Do all of this **before** reading historical evidence, the CPython baseline, old incident records, any candidate-owned source or binary, or launching any candidate worker.

Missing, malformed, guessed, partial, repeated, historical, cross-family, diagnostic, or unbound reports fail closed. Never mutate a report, synthesize a report pin, monkeypatch a validator, or replace an original result with a pass. A qualified deep run additionally requires the exact same family's complete actual passing V10 **qualified** 223,198-observation edge archive.

## Additive exclusively created records

Preflight all possible pass, failure, crash, owner-failure, and invalidated destinations **before** starting a candidate worker. Publish each complete canonical compressed document using exclusive creation only.

```text
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v10-{diagnostic,qualified}-pass.json.gz
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v10-{diagnostic,qualified}-failures.json.gz
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v10-{diagnostic,qualified}-native-owner-failure.json.gz
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v10-{diagnostic,qualified}-producer-crash.json.gz
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v10-{diagnostic,qualified}-invalidated-after-owner-failure.json.gz

candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V10-PASS.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V10-FAILURES.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V10-PRODUCER-CRASH.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V10-INVALIDATED-AFTER-OWNER-FAILURE.json.gz
```

Every diagnostic explicitly records `campaign_qualified: false`. Preserve the actual complete worker result, stdout, stderr, return code, crash or timeout, independently reproducible content hashes, bounded reversible original bytes, and the actual reason. If a completed original result is later invalidated, retain its **unchanged original bytes** at the separate invalidated path. Never relabel a failure or overwrite existing evidence.

## Zero-effect source-only controls

Both frozen-runtime controls must pass at least **150** independent deterministic in-memory poison and source-integrity cases:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/postfinal_current_build_proofs_v10.py --self-test
env -i PATH=/usr/bin:/bin /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/postfinal_current_build_proofs_v10.py --self-test
```

The self-test must not import a candidate, start a worker, read an audit report or evidence, inspect holdout data, sample clocks, create files, modify history, or benchmark. Freeze, independently review, commit, and push these exact V10 sources before running any candidate diagnostic.

Performance: **NOT MEASURED**. Holdout: **NOT ACCESSED**.
