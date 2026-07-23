# Rust calibration-only optimization checks

Rust design changes are compared on practice tasks before the final unseen holdout is measured. The [frozen calibration plan](rust-v6-calibration-plan.json) contains **108** tasks drawn exclusively from the original performance suite's practice set. It never silently substitutes practice measurements for the **6,216-task** holdout.

The fixed plan includes two bounded examples from each of the **48** newer workload families, all **12** public operations, all **three** compilation/caching lifecycles, text, bytes, mutable byte buffers, memory views, all four result densities, and the **12** worst older practice families. Every task is identified by the frozen fixture, its expected-result digest, its original operation count, its result density, and its reason for selection.

| Coverage | Fixed practice-only plan |
| --- | ---: |
| Tasks | 108 |
| New workload families | 48/48 |
| Public operation types | 12/12 |
| Lifecycle types | 3/3 |
| Existing severe-loss families | 12 |
| Result-density types | 4/4 |
| Holdout tasks | 0 |

The runner retains deterministic paired ordering, all **four** frozen warmups, per-trial Python and process memory, matching-output checks before and after each timed trial, native-binary hashes before and after measurement, and seeded confidence intervals. It refuses changed fixtures, changed native code during a run, bad results, incomplete pairs, or accidental holdout inclusion. The default is `calibration`; accessing holdout cases requires explicitly requesting `--cohort holdout` or `--cohort both`.

A pilot is a diagnostic, not an overall ranking. The final Rust result must still use every frozen practice and holdout task, all **13** paired trials, **2,000** bootstrap samples, all memory observations, and every slowdown.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONPATH=. "$PY" tools/rust_v6_calibration_pilot.py self-test

PYTHONPATH=. "$PY" tools/rust_v6_calibration_pilot.py measure \
  --trials 5 --max-ops 16 --bootstraps 300 \
  --raw /tmp/rebar-rust-calibration-pilot-raw.jsonl \
  --output /tmp/rebar-rust-calibration-pilot.json
```

The pinned expected-result SHA-256 is `c8e32e879cc7a134748f8f3f29fed49678895745fdecebe63ceec46b6a3b5335`. Optimized, full-holdout Rust performance is **NOT MEASURED** by this plan.
