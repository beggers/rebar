# Current-build correctness proofs: V9

This additive protocol preserves every previous result and fixes a genuine V8
native-ownership error. It never edits a frozen source, hides a failure, wraps
an external regex package, delegates matching to Python `re` or another
candidate, opens a holdout, or runs a performance experiment.

## Frozen original correctness

Use exactly isolated CPython 3.14.6 and Unicode 16.0.0.

- The original edge producer is `tools/rust_v7_edge_oracle.py`, SHA-256
  `fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca`.
  Preserve all **223,198** actual observations, all **49** categories, the
  original seed `2026072329`, all six independent generation seeds, all eight
  seeded cases, Unicode stride `4099`, and expected SHA-256
  `b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526`.
- The original deep suite is `tools/rust_v8_deep_contract_oracle.py`, SHA-256
  `ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978`.
  Preserve all **393** actual observations, all **64** seeded cases, original
  seed `2026072347`, and reference SHA-256
  `b184f3388320909b3c28fbd3ce9c15cefc992d3e852e9495ad8fb503d1cbaad8`.
- The genuine original deep producer is
  `tools/rust_v8_multi_candidate_contract.py`, SHA-256
  `167f9d9114f95cd9c9821465339264f8b6eca9bf7f70b84774f4108f62f11a70`.
  Preserve both independent CPython reference workers, all native guards,
  exact original compressed observations, and every actual public mismatch.
- The exact genuine stage07 guard source is
  `tools/python_re_universal_public_oracle_stage07.py`, SHA-256
  `150abcfc597658f48d64c04053889bd4b299c75ad7413bc1cafa5f864e9e7c25`.
- Preserve the genuine earlier Rust 16, C 33, and Zig 16 edge failures with
  archive SHA-256 values
  `3ffdb21d10f40deabd70fa1f408fa38ff2b027a2d269c4b75e607a05cefde3b8`,
  `2cce7c26d2487c8e400d2fd6b8cfbc81d4b734b08f7a8f356def910a9cbb385c`,
  and `5fa7283942994139d531593cc1bdf25f5da48f6de424d7604ce2ce569100788a`.
- Preserve the actual pre-import V8 Rust guard failure
  `candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v8-diagnostic-native-owner-failure.json.gz`,
  SHA-256 `2f8bfcba726d729865cb8411a25ef1c3e0633e80c70af8895e5875a71f15ed7b`.
  It is a real failure; it never qualifies a candidate.
- Preserve the actual two-reference official CPython V5 self-oracle
  `oracle/cpython-3.14.6/evidence/postfinal-locale-v5-self-oracle.json`,
  SHA-256 `3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916`.
  Require both genuinely isolated references, all **152** public methods, all
  **151** applicable passes, and exactly the one named private skip.

## Correct the genuine sentinel error

An imported cached module must not be mistaken for an imported forbidden
engine. Before and after real matching, prove that the exact stage07-created
sentinel has the precise `_ForbiddenRegexModule` type, the identical
`sys.modules` entry, and the identical `importlib` result. Reject a newly
constructed sentinel, a subclass, a same-name forgery, a restored live regex
module, and any changed binding. Require an actual PASS for all **13** Python
matching guards, all **five** protected native-loader aliases, all **16**
ordinary public `Pattern` and `Match` pickle round trips, genuine native text
and bytes matching, and every expected source and ELF before starting the
unchanged original edge producer. Repeat the corrected owner after it finishes.

Require `stage07_guard_sentinel` with the exact frozen stage07 source SHA-256
and true `sentinel_type_exact`, `sys_modules_sentinel_identity`,
`imported_sentinel_identity`, `before_matching_verified`,
`after_matching_verified`, `fresh_sentinel_rejected`,
`subclass_sentinel_rejected`, `same_name_forged_sentinel_rejected`, and
`live_module_rejected` fields.

## Additive evidence

Use only new V9 family-specific, deterministic and exclusively created paths.
Always check every pass, failure, crash, owner-failure, and invalidated-output
path before the first worker.

```text
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v9-diagnostic-pass.json.gz
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v9-diagnostic-failures.json.gz
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v9-diagnostic-native-owner-failure.json.gz
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v9-diagnostic-producer-crash.json.gz
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v9-diagnostic-invalidated-after-owner-failure.json.gz
```

Diagnostics always explicitly say `campaign_qualified: false`; a passing
one-family diagnostic is not an all-family correctness result.

Qualified edge paths replace `diagnostic` with `qualified`. The independently
original full deep contract uses:

```text
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V9-PASS.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V9-FAILURES.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V9-PRODUCER-CRASH.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V9-INVALIDATED-AFTER-OWNER-FAILURE.json.gz
```

Preserve a worker crash, timeout, oversized stream, or actual native failure
exactly once with complete actual SHA-256 values and bounded reversible byte
previews. If a completed original result is invalidated by a later owner,
source, audit, or protocol failure, preserve the original unchanged bytes to
the distinct invalidated path. Never turn a failure into a pass.

## Genuine external all-family pins

Qualified modes require both `--base-report-sha256` and
`--strict-report-sha256` supplied as independently observed actual V9 report
digests. Before a candidate worker, authenticate exact frozen V9 ownership and
strict sources, the V9 native ownership protocol, complete actual passing V9
base and strict reports, all **12** owned sources, **five** native binaries,
**three** genuine native workers, **48** ordinary public pickle round trips,
**six** actual match representations, the real stage07 sentinel before and
after matching, all historical failures, and the exact official CPython V5
self-oracle. Never mutate an immutable source or in-memory audit pin. Unknown,
missing, repeated, historical, cross-family, or guessed reports fail closed.

`--qualified-deep` additionally requires that exact same candidate's actual
passing V9 **qualified** 223,198-case edge archive. A diagnostic, earlier V8
result, failing edge, guessed digest, or different family never qualifies.

## Source-only control

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/postfinal_current_build_proofs_v9.py --self-test
```

The direct clean and explicitly configured source-only controls exercise at
least **150** exact in-memory poison cases. They start no worker, import no
candidate, read no evidence or report, sample no clock, write no file, and
never open holdout data. Freeze and push this source before any diagnosis.

Performance: **NOT MEASURED**. Holdout: **NOT ACCESSED**.
