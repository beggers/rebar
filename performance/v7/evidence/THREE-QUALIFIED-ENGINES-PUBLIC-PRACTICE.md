# Three fully compatible engines: same-run public practice

The fully correctness-qualified Rust, C, and Zig engines and unchanged standard Python were compared on exactly the same **624 public practice cases**. This experiment began only after the blind **24,576-case** final protocol was frozen. It does not open that final test or establish a winner.

## Overall practice results

| Engine | Speed relative to Python | 95% uncertainty range | Clearly faster cases | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| Python | 1.000× baseline | Baseline | Baseline | Baseline |
| C | 1.315240664× | 1.268655846–1.367993166× | 426/624 | 49/624 |
| Rust | 1.121192007× | 1.076002177–1.165114712× | 247/624 | 139/624 |
| Zig | 1.007386478× | 0.960375090–1.053645936× | 229/624 | 238/624 |

The uncertainty ranges compare each engine with Python, not engines with one another. Zig's overall range includes **1×**. No practice result proves a **1.5×** final improvement.

## Every observation is preserved

- **624** identical practice cases per engine, across **12** public operations.
- **7** randomized, paired trials per case and engine.
- **499** predeclared bootstrap draws per confidence interval.
- **17,472** actual timing observations: 624 × 7 × 4.
- **52,416** successful before, memory, and after correctness checks.
- **1,872** retained candidate-case results.
- **1,875** independently recomputed case and overall confidence intervals.
- All **426** strictly more-than-20%-slower results; none are omitted.
- All **5** actual native libraries match the original passing source audit.
- Held-out final cases accessed: **0**.

The [complete source-bound practice summary](three-qualified-engines-public-practice-v1-summary.json) has SHA-256 `20c33badfc08d98566c5476452370f042cd8ff544ecc5ed98f6d1111550328f0`. The [complete compressed raw observations](three-qualified-engines-public-practice-v1-raw.jsonl.gz) have SHA-256 `9cc74e1baddc2dc954c26802956e0a37c10a320eef4f3eb9425b55977ea19f3c`; their uncompressed SHA-256 is `83fbd07a3062e6ba374d8558234f5997fbaf5b59050af85c9ba6bcd15d532881`.

## The exact original measurement

The frozen public-practice tool was invoked exactly once:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  -m tools.rust_v7_calibration_pilot measure \
  --exclusive-slot three-qualified-engines-public-practice-v1 \
  --cases 624 --trials 7 --bootstraps 499 --max-operations 16 \
  --module re \
  --module candidates.rust_candidate \
  --module candidates.vm_candidate \
  --module candidates.zig_candidate \
  --edge-oracle candidates/evidence/rust-v7-edge-oracle-rust-mandatory-prefix-inline-singleton.json.gz \
  --edge-oracle candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-19.json.gz \
  --edge-oracle candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-11.json.gz \
  --raw performance/v7/evidence/three-qualified-engines-public-practice-v1-raw.jsonl.gz \
  --output performance/v7/evidence/three-qualified-engines-public-practice-v1-summary.json
```

The candidate sources, bridges, and engines were independently checked before and after measurement. The [original from-scratch audit](../../../candidates/audits/FROM-SCRATCH-AUDIT.json) passes all **76** controls, all **five** actual native libraries, and all four independent source families.

## Independent replay and poisoning controls

The [independent recorded-data verifier](../../../tools/rust_v7_multi_candidate_practice_audit.py) does not import, execute, or time a production candidate. It replays every randomized trial and every seven-round speed ratio, checks both gzip and uncompressed raw hashes, recalculates all confidence bounds, verifies all source and native-library identities, and retains every slowdown. Its actual [verified result](three-qualified-engines-public-practice-v1-integrity.json) has SHA-256 `8739803b6cd020b8b4f663223435fd1e39ef5603e90195b2a268a9fa7fbc0340`.

The [28-control verifier self-test](three-qualified-engines-public-practice-v1-integrity-self-test.json) independently rejects missing and repeated observations, changed engines, altered confidence bounds, falsified case answers, changed trial order, invalid memory records, concealed slowdowns, and claims of a final result.

The [deterministic chart generator](../../../tools/rust_v7_multi_candidate_practice_charts.py) passes [33 additional synthetic corruption tests](three-qualified-engines-public-practice-v1-chart-self-test.json). It generates exactly six complete views from the verified result: [overall speed and uncertainty](three-qualified-engines-public-practice-v1-overall.svg), [all outcomes](three-qualified-engines-public-practice-v1-outcomes.svg), [all 12 operations](three-qualified-engines-public-practice-v1-api.svg), [all substantial slowdowns](three-qualified-engines-public-practice-v1-regressions.svg), [Python-visible temporary allocations](three-qualified-engines-public-practice-v1-memory.svg), and [practice rankings](three-qualified-engines-public-practice-v1-rankings.svg).

## Memory and scope limitations

All four engines run in the same process for this practice-only diagnostic. Per-case memory ratios describe Python-traced temporary allocations. The process's resident and high-water memory includes all imported candidates and cannot be attributed to an individual native engine. Isolated native memory is **NOT MEASURED**.

The **24,576-case** final test remains sealed. Its speed, memory, confidence intervals, regressions, and winner are **NOT MEASURED**.
