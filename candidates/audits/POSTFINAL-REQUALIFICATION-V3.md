# Requalifying the rebuilt from-scratch Rust engine

Status: the rebuilt Rust engine has passed its current source and
independence audits, **33** native Rust tests, **223,198** public edge
checks, **393** deep Python-behaviour checks, the **1,179,648**-comparison
all-engine public campaign, and **479** callback and scanner checks.
Its accepted, fail-closed **22**-stage compatibility campaign passed
all **4,494,555** Unicode observations and **144** official tests.
Its speed and memory use are **NOT MEASURED**.

## Bind every result to the current engine

| Current source, executable, or completed proof | SHA-256 |
| --- | --- |
| Rust engine source | `94de5c9ea872bb3649a24a49e99abf5f4e4acd42cfd6d2695f7d17d101f6b888` |
| Rebuilt Rust native engine | `1d0851d461fcb4caf4873a4c6fb30c1fd133dfb2140b0602622b9d06e9c1f0d1` |
| Unchanged Rust-to-Python bridge | `81fc4c4a92005f0588dd9b811988587d4d421dd8e1102eebcab53f4deb27cd36` |
| Current from-scratch audit controller | `d8230d1f0272bffc6ef2fb61136935047a4d4008afd8a66291c87c48b7a36767` |
| Completed from-scratch audit | `f1a1f2402819d85d0d9135b0fc2b89aecd2212bb3259700bf7628cb881a32f05` |
| Current no-delegation audit controller | `80d2450439893e1d6e1e2d1986cc59cc7da20e4d4c871f6670b31587da0f24f5` |
| Completed no-delegation audit | `51f745b0cf4a1a91457d865b8fac26b71534f801ca6632b2fd762bd6933c6ab5` |
| Completed compressed edge-check report | `f4bbacc480b284685e8b6fb0dfff656f323605dd5efbc3331c0b5e26ea3c03d7` |
| Completed compressed deep-behaviour report | `88dda18f6498d6cbb078fb89a8dbbfebe4ae357d4d7ca3de795bd9e6a5828e1a` |
| Completed all-engine public comparison | `d5b06b914d63f1b89cfd78c2f72c45f432755ce6895b6194e8e7d3fee9c0c2ca` |
| Completed compressed callback and scanner report | `4fb158e17dd36ed7a9ba8b7b54cdf66e87643cc82c7181ba163e961df593936a` |
| Accepted fail-closed compatibility campaign controller | `cdabec673a905b122c474a8279b84f194534fda77a0c70555fb9aa9fd299592d` |
| Accepted complete version-two compatibility campaign | `9015b2a02bdf32e1f4dfdb3eb0c8fb8e67d07b78649ccb1ba3ba4da6cd4b76e8` |

The completed source audit is
`candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V3.json`. It proves
that all **four** separately implemented source pipelines pass, including
the **three** distinct native-engine families. All **five** expected
native-library roles are present, fingerprinted, and confirmed in the
correct isolated worker's actual memory mappings.

Its **76** original checks, **52** version-two checks, and **129**
version-three checks are synthetic, in-memory safeguards; they are not
223,198 matching examples or performance measurements. The original
**76** checks also passed again in the required fresh, isolated pinned
Python process.

The completed independent no-delegation audit is
`candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V3.json`. It binds the
exact current source-audit report, repeats the **76** inherited checks,
and passes **32** actual production independence checks. All four
source families and all five native-library roles pass. Neither audit
uses Python's regular-expression implementation, an external
regular-expression package, a different candidate's engine, a
benchmark, or a hidden test.

The first production source-audit attempt did not create a report: its
isolated original-control worker exited with signal **9**. An
out-of-memory cause is **NOT ESTABLISHED**. The controller now releases
the already verified predecessor report and its encoded bytes, and
collects unreachable objects before running the unchanged full
version-two and original audits. The subsequent actual source audit
passed all **76** fresh isolated original controls. No control was
cached, skipped, injected, replaced, or weakened.

## Completed public checks

| Check | Current-engine result | Evidence |
| --- | --- | --- |
| Native Rust tests | **33 passed** | Current rebuilt Rust source and native engine above. |
| Public matching edge cases | **223,198 checks; zero mismatches** | `candidates/evidence/rust-v7-edge-oracle-rust-postfinal-assertion-snapshot-v1.json.gz` |
| Deep Python-object behaviour | **393 checks; zero mismatches** | `candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-ASSERTION-SNAPSHOT-V1.json.gz` |
| Complete all-engine public comparison | **8,192 public cases × 48 observations × 3 native candidates = 1,179,648 comparisons; zero mismatches** | `candidates/evidence/python-re-universal-public-oracle-v5-all.json` |
| Callback and scanner observations | **479 candidate checks and 479 self-oracle checks; zero failures** | `candidates/evidence/rust-v8-observability-rust-qualified-postfinal-assertion-snapshot-v1.json.gz` |
| Complete accepted compatibility campaign | **22 stages passed, including 4,494,555 Unicode observations and 144 official tests** | `candidates/evidence/rust-v8-rust-postfinal-assertion-snapshot-v2-sealed-campaign.json` |
| Rebuilt-engine speed | **NOT MEASURED** | A separately frozen current-engine performance protocol and result are required. |
| Rebuilt-engine memory | **NOT MEASURED** | A separately frozen current-engine memory protocol and result are required. |
| Final cases | **NOT OPENED** | No final result is claimed. |

The first attempt at the full **22**-stage campaign produced no report.
It stopped immediately with `AssertionError: complete from-scratch audit
failed`: the historical controller called the older direct audit entry
point after the engine changed. Its preserved controller is
`tools/rust_v8_multi_candidate_campaign.py`, SHA-256
`46e53abac0d2347d5fc505aa792a5ee5f55489a6e73b1f57edf37a93a0a6d45d`.

A first additive wrapper then genuinely passed all **22** stages using
the current version-three audit. Its preserved intermediate report is
`candidates/evidence/rust-v8-rust-postfinal-assertion-snapshot-v1-sealed-campaign.json`,
SHA-256
`9e744de16c6c627715303bcf27ae9ef628b04fcdc078e3ebe9e936204b719db2`.
That report is **not the accepted proof**: independent review found the
wrapper would have allowed a legacy fallback if the current proof were
missing, even though no fallback occurred in the actual first run.

The accepted controller,
`tools/rust_v8_multi_candidate_campaign_postfinal_v2.py`, rejects a
missing or invalid current proof. Its **43** new file-free rejection
checks, **46** inherited safeguards, and **129** current source-audit
checks precede all **22** real campaign stages. The accepted evidence
is exclusively
`candidates/evidence/rust-v8-rust-postfinal-assertion-snapshot-v2-sealed-campaign.json`.
Every stage passed without benchmarking or opening final cases.

For an independent, source-bound statement of what has actually passed,
see `candidates/evidence/RUST-POSTFINAL-ASSERTION-SNAPSHOT-V1.md`.

## Preserve the previous measured engine

The following results belong only to the earlier, rejected Rust engine
and its historical version-six comparison. Its **12** compatibility
proofs, **425,984** timing observations, and **5,940** individually
preserved slowdowns remain evidence about that earlier engine. They are
not results for the rebuilt engine.

| Historical source or historical verified result | SHA-256 |
| --- | --- |
| Earlier Rust source | `398773b8542c88cfc55fe13ceac1e84a00155217b76b8461ddf9704d2f6c82c5` |
| Earlier Rust native engine | `83394c5c3b5d9e9d98c8474aac60ca5a81517dc7ec7c53b3b625e6ed0a04c165` |
| Earlier from-scratch report | `5e299a767cbd494683100519a6ad461d1a0eb9de1564b1437c7e0229cca7a551` |
| Earlier no-delegation report | `183cd04f5e1587c181505c09867566b4bd18db270f974475c2b456ff09af1d9f` |
| Earlier all-engine Python comparison | `facb736a3409f459cdc812e6dc740df399f98ebb84745a22b615ef130ccdb137` |
| Earlier public workload manifest | `65e024a1a79d13b03e4e5ad0f3d4ae010dbb6e4f09b52a8542837a2ea4c6198a` |
| Earlier full public speed summary | `539fe6ba0ac492ffab121845da21033676ad7e7154ce9107f7f1778f55ceed4c` |
| Earlier independently verified replay | `8eb2e6bba6894a71f63e32cc35cca5317bb1beccc32c2905bbeacebedb868fd2` |
| Original native-engine archive manifest | `136a64a89fed1dce245c3774539720beb171c660291d2ca0e1e1b6303115efd6` |

Historical results remain available in
`performance/postfinal-public-v6/RESULTS.md`. Do not overwrite, reuse,
or present them as measurements of the rebuilt engine.

## Reproduce only candidate-free audit controls

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_from_scratch_audit_v3.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_no_delegation_audit_v3.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage05.py --self-test
```

Self-tests are not production candidate runs, correctness results,
speed trials, memory measurements, or final-case access.
