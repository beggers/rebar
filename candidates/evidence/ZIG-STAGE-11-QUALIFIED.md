# Zig candidate: correctness qualified

Stage 11 is the first Zig implementation to pass the complete original CPython 3.14.6 correctness and from-scratch independence gates. This qualifies it for a future fair speed comparison; it does not establish that Zig is faster.

## Headline

- Complete original sealed campaign: **22 of 22 stages passed**; no mismatches, crashes, unexplained failures, substitutions, external regular-expression engines, or candidate delegation.
- Complete Unicode test: **4,494,555 checks passed**, including all four 1,114,112-code-point partitions and all 50 CPython extra-case keys, 56 links, and 280 checks.
- Independent original audit: **all 4 candidate families passed**, **all 5 actual native binaries were mapped and verified**, and **all 76 malicious and delegation controls passed**.
- Performance: **NOT MEASURED**. Holdout: **NOT ACCESSED**. No winner has been selected.

## What was actually checked

| Original archived check | Checks | Result | Evidence |
| --- | ---: | --- | --- |
| Subprocess crashes, hostile inputs, and 1,024 captures | 254 | PASS; no crashes, timeouts, or oracle failures | `rust-v8-zig-stage-11-isolated-safety.json` |
| Live recursion limits, deep groups, and overflow | 348 | PASS; no crashes, timeouts, or oracle failures | `rust-v8-zig-stage-11-depth-safety.json` |
| Complete Unicode plane and CPython case folding | 4,494,555 | PASS | `rust-v8-zig-stage-11-unicode-fullplane.json` |
| Original frozen extended-path worker | 72,248 | PASS | `rust-v8-zig-stage-11-extended-original.json` |
| Separate lossless extended-path diagnostic | 72,248 | PASS | `rust-v8-zig-stage-11-extended-path-failures.json.gz` |
| Frozen generated pattern grammar | 20,480 | PASS; no hidden external package | `rust-v7-grammar-zig-v8-deep-stage-11.json.gz` |
| Frozen edge and API differential checks | 223,198 | PASS | `rust-v8-edge-oracle-zig-deep-stage-11.json.gz` |
| Replacement strings and Python callbacks | 8,862 | PASS | `rust-v8-replacement-zig-stage-11-from-scratch-failures.json.gz` |
| Deep replacement strings and Python callbacks | 11,266 | PASS | `rust-v8-replacement-zig-stage-11-from-scratch-deep-failures.json.gz` |
| Independent public contract and engine guards | 393 | PASS; 10 cross-engine and 13 forbidden-regex guards | `../audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-11.json.gz` |
| Observable Python behavior and callbacks | 479 | PASS; 34 additional native-binder checks passed | `rust-v8-observability-zig-qualified-stage-11.json.gz` |

Each row cites its actual archived evidence. The original extended-path report has schema `rebar-rust-v6-paths-probe-v1`, seed `2026072307`, 512 seeded cases, 895 manual cases, 380 surrogate checks, and all 50 CPython extra-case keys and 56 directed links; SHA-256 `f086f0e7cb7e53999908e3336821b595f6d48a51478dbfd81706e398f907dbb6`. The separate lossless diagnostic is not the campaign payload and is not the original report. Both cover the same 72,248-case obligation; their denominators must not be added together. The sealed campaign independently executes and passes the original `extended-cpython-paths` worker. There was no separate Stage 11 repeat-controls suite. The sealed campaign additionally passes the frozen v2 and v3 suites, the official CPython tests, both public API suites, and the Unicode group-name error suite.

## The complete sealed campaign

The one actual Stage 11 campaign invocation was:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
tools/rust_v8_multi_candidate_campaign.py \
  --module candidates.zig_candidate \
  --edge-oracle candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-11.json.gz \
  --deep-proof candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-11.json.gz \
  --output candidates/evidence/rust-v8-zig-stage-11-sealed-campaign.json \
  --memory-mib 2048
```

It exited successfully on that single invocation. The actual original stages, in order, were:

1. `from-scratch-static-audit`
2. `independent-source-no-delegation`
3. `independent-owned-native-pipeline`
4. `candidate-frozen-edge-proof`
5. `candidate-frozen-deep-public-proof`
6. `independent-native-boundary-self-oracle`
7. `independent-native-boundary-integrity`
8. `independent-native-boundary-poison`
9. `independent-native-boundary-compatibility`
10. `frozen-cross-family-observability`
11. `frozen-correctness-v2`
12. `frozen-correctness-v3`
13. `official-cpython-tests`
14. `upstream-public-surface`
15. `candidate-public-surface`
16. `unicode-group-name-errors`
17. `replacement-and-callback-adversarial`
18. `deep-replacement-and-callback-adversarial`
19. `extended-cpython-paths`
20. `isolated-crash-and-resource-safety`
21. `isolated-depth-and-overflow-safety`
22. `full-unicode-plane`

The campaign explicitly excludes the original three performance or holdout steps. Campaign evidence: `rust-v8-zig-stage-11-sealed-campaign.json`; SHA-256 `d5ad2b2828861ec346e47c6e120cc00ad1ca97d2469089c27e3e8607b3653c30`.

## Why the independence failure is genuinely fixed

Stage 10 was rejected because the frozen auditor found two forbidden recursion externs in the Zig engine; its static diagnostic also establishes that the candidate runtime was skipped. Stage 11 keeps the original owned `rebar_zig_compile` symbol, adds the owned `rebar_zig_compile_guarded` entry point, and supplies Python recursion enter/leave callbacks from the candidate's own C bridge. The Zig engine does not import those Python recursion symbols or another regex engine. The original auditor now validates the real parser, compiler, executor, all four independent families, all five owned native binary mappings, and the existing 76 poison controls.

The current successful canonical report is `../audits/FROM-SCRATCH-AUDIT.json`; SHA-256 `94b00886ab790d096f243775540d2590c33ea7a316d9a6098cd40d52b19f6f09`. Its unchanged pinned auditor is `tools/audit_from_scratch.py`; SHA-256 `4c47a77cf096df354e59d03096447c56bff890389869c6a75667a36c8471d024`.

## Exact qualified implementation

| Owned Stage 11 file | SHA-256 |
| --- | --- |
| `candidates/zig/mini_regex.zig` | `4deca5a442cccd02bebfcecd4ceeb73de62a68837c5a3bdadee4dcaf84cf0ee3` |
| `candidates/zig/py_bridge.c` | `cdcf335f92f90c7ce98a93add914dabd0b607dc2742a4e7190a2187e538e959d` |
| `candidates/zig_candidate.py` | `95a2010152099f2db61595927542b2f25a675eb72bd33125659969d804360239` |
| `candidates/_zig_probe.so` | `70bafca56a3f48477b2011f016a81b625e5f40a772af6a986d32b9098269f614` |
| `candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so` | `4d0dc7ece7ef42e34a8f425fab55429460e2fd66c587ce13c70539979393d13c` |

The immutable original objective remains `GOAL.md`; SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`.

## Failed attempts remain visible

Stage 09's genuine two-crash depth rejection is retained in `rust-v8-zig-stage-09-depth-safety.json`; SHA-256 `d71fc63e0077b772a4872bc3e6c2b71a16df4275da8f51f147354c1dd0542bf7`. Its exact rejected implementation remains in `ZIG-STAGE-09-REJECTED-DYNAMIC-RECURSION.patch`; SHA-256 `8e9b19484dad6fc1076e4dfc0eb2ee2b16c440fac7cf9d7f20b399cb40245f42`.

Stage 10's original independence failure remains in `../audits/FROM-SCRATCH-AUDIT-ZIG-STAGE-10-FAILURE.json`; SHA-256 `03e818e7df469a4488340b4a3e7058589396e4fdc1c5587fd79acef59f2c9509`. Its exact static root cause and truthful two-invocation accounting remain in `../audits/FROM-SCRATCH-AUDIT-ZIG-STAGE-10-STATIC-DIAGNOSTIC.json`; SHA-256 `4e63f97adc8f603921a5b98560a024ba0a8050efda628868542dad88e56eacc2`. Passing Stage 10 safety and depth reports were not used as independence evidence.

Stage 11 is **correctness-qualified, not performance-qualified**. Speed, memory, confidence intervals, relative rankings, and the held-out workloads are **NOT MEASURED**; the performance holdout remains **NOT ACCESSED**.
