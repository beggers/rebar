# Rust candidate: complete correctness gate

Result: **PASS. All 21 gate records passed against the actual rebuilt Rust candidate.** No unexplained mismatches, crashes, timeouts, changed frozen test cases, hidden fallback, or external regular-expression package were found.

This is correctness evidence, not a performance result. Speed, memory ranking, and the final winner are **NOT MEASURED** by this gate.

## What passed

| Check | Result |
| --- | --- |
| Rust, C bridge, Python wrapper, and complete dependency audit | No regular-expression delegation; no external search or regex package; no legacy fallback. |
| Two additional guarded production-import audits | Both passed. |
| Native-boundary integrity | 354 semantic cases; 192 boundary cases in 24 families; all five deliberately damaged controls rejected. |
| Native-boundary Python-versus-Python control | 546/546. |
| Real production Rust–Python boundary | 738/738. |
| Original frozen correctness suite | 8,244/8,244. |
| Expanded frozen correctness suite | 44,084/44,084; all 51 required behaviors covered. |
| Official CPython tests | 144 passed; two explicitly documented missing-locale skips; 146 methods in total. |
| Original performance-case correctness | 12,432/12,432. |
| Frozen performance-suite integrity controls | Passed without running or timing a benchmark. |
| Expanded performance-case correctness | 20,624/20,624, including 10,312 calibration cases and 10,312 held-out cases. |
| Existing public-interface checks | 190/190. |
| Extended Rust public-interface checks | 1,198/1,198. |
| Invalid Unicode group-name behavior | 420/420; the Python-versus-Python control has zero failures. |
| Replacement and callback behavior | 8,862/8,862. |
| Extended replacement and callback behavior | 11,266/11,266. |
| Difficult matching, case handling, buffers, and index windows | 72,248/72,248. |
| Isolated malformed-input and resource safety | 254/254; zero crashes, timeouts, or reference failures. |
| Isolated nesting, recursion, allocation, and overflow safety | 348/348; zero crashes, timeouts, or reference failures. |
| Full Unicode plane and seeded Unicode edge cases | 4,494,555/4,494,555. |

The case counts above are intentionally overlapping. Their sum is not a count of unique regular expressions or unique test scenarios.

The two official skips are `ReTests.test_locale_caching` and `ReTests.test_locale_compiled`. Each requires the unavailable `en_US.iso88591` system locale. They are recorded, not counted as passing or silently removed.

## Exact frozen inputs and production code

- Python baseline: CPython `3.14.6`.
- Immutable `GOAL.md` SHA-256: `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`.
- Frozen expanded correctness SHA-256: `782c41ff0b1239eeb0bb5312b4a893b41d7882c7fdcf64b29587518839e51669`.
- Frozen expanded performance-case SHA-256: `2e6c098bd3a4757620461363106a9795f8defa98fe8bc9c13c0ebbf7ed58b598`.
- Correctness-gate runner SHA-256: `44f20e2c69c5180065ec075484571199bbed573bea7d5142172cbba6bc76d77e`.
- Rust engine source SHA-256: `f529040ab9082eedf80ba9c39b407def3edf9520a9a1fc8d70cb6e8399f7723f`.
- C bridge source SHA-256: `36f91d6e6970b508ad6a9fe4299055b0538917b1c2a751840e9b3accc24dbc9e`.
- Python wrapper SHA-256: `a6394022bf647f8992f01f73e9fc1a02dd7178734948cc2dc4e5ed9dcf7b6a35`.
- Built Rust engine SHA-256: `6a0716543ebe49dad44f9d1fa0cd7a8ee3de8e8cf4e2f6e4ad077211a655c161`.
- Built Python bridge SHA-256: `a86f2b6e917edd97136cb72a158ff8130c839ecebcaf19ef4b455442db9b66d2`.

Every Unicode character was checked under regular Unicode, ASCII-only, Unicode-ignore-case, and ASCII-ignore-case rules. Each of the four independent 1,114,112-character result hashes exactly matches CPython.

## Original failures remain visible

Fixing a result did not remove the original evidence:

- [`rust-v6-c0-prefx-paths-finding.json.gz`](rust-v6-c0-prefx-paths-finding.json.gz) records the original matching failures.
- [`rust-v6-c0-prefx-safety-finding.json.gz`](rust-v6-c0-prefx-safety-finding.json.gz) records the original error-handling differences.
- [`rust-v6-unicode-c0-f33-baseline.json.gz`](rust-v6-unicode-c0-f33-baseline.json.gz) records all 277 original wide-text Unicode failures.
- [`rust-v6-unicode-c0-f33-fixed.json.gz`](rust-v6-unicode-c0-f33-fixed.json.gz) records the complete corrected Unicode run.
- [`rust-v6-group-name-adversarial-baseline.json.gz`](rust-v6-group-name-adversarial-baseline.json.gz) and [`rust-v6-group-name-adversarial-corrected.json.gz`](rust-v6-group-name-adversarial-corrected.json.gz) preserve both sides of the Unicode group-name fix.
- [`rust-v6-ffi-lab.json.gz`](rust-v6-ffi-lab.json.gz) preserves the original and corrected native-boundary evidence.

## Reproduce and verify

Run the same fail-fast gate using the pinned Python:

```sh
PYTHONPATH=. /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  tools/rust_campaign_gate.py \
  --output /tmp/rebar-rust-campaign-rerun.json
```

The complete original, deterministically compressed gate report is [`rust-v6-campaign-gate.json.gz`](rust-v6-campaign-gate.json.gz).

- Compressed SHA-256: `f5a92f7ffd27286235fb73d3c7a2f33fbc1397d419ef0c5d3856b81b185b397f`.
- Decompressed JSON SHA-256: `240d5bf096d9c3978bee6e49bf1a5e0a86260b273830109703a243c4ee349260`.
- Gate records: `21/21`.

```sh
sha256sum candidates/evidence/rust-v6-campaign-gate.json.gz
gzip -cd candidates/evidence/rust-v6-campaign-gate.json.gz | sha256sum
```

Timing comparisons, confidence intervals, memory comparisons, ranking, and a final speed claim remain **NOT MEASURED** in this correctness experiment.
