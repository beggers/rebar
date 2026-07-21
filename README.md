# rebar

| Status | Current evidence |
|---|---|
| Phase | 1 — CORRECTNESS ORACLE |
| Gate | Bootstrap **PASS**; CPython source pin **PASS**; P0 matrix and suite **NOT FROZEN** |
| Verdict | **NOT MEASURED** |
| Next chunk | Freeze the versioned P0 public-API and observable-object obligation matrix |
| Correctness | v1 baseline only: 0/0 P0 obligations frozen; stdlib self-oracle **NOT MEASURED** |
| Candidates | 0/3 required independent families complete; **NOT MEASURED** |
| Benchmarks | 0/0 cohorts frozen; ranking **NOT MEASURED** |
| Failures / gaps | Matrix, CPython-derived suite, differential/property/fuzz corpus, three candidates, delegation audit, performance oracle, holdout, and final falsification remain open |

## Evidence

- Immutable objective: [`GOAL.md`](GOAL.md)
- `GOAL.md` SHA-256: `2284aba879b0cb609311865c19f84d1eb6b2988227c7216e35a2f554cce7921b`
- Oracle baseline rationale and reproduction: [`oracle/v1/BASELINE.md`](oracle/v1/BASELINE.md)
- Machine-readable baseline lock: [`oracle/v1/baseline.json`](oracle/v1/baseline.json)
- Correctness chart: **NOT MEASURED**
- Speed/confidence chart: **NOT MEASURED**
- Memory chart: **NOT MEASURED**
- Regression chart: **NOT MEASURED**
- Ranking chart: **NOT MEASURED**

## Frozen baseline

The oracle and eventual baseline are the unmodified `re` module in CPython
3.14.6 built from the official python.org source archive. The archive hash was
verified locally on 2026-07-21. Python 3.15 was still pre-release and CPython
3.14.7 was not yet released on that snapshot date.

No candidate design has been selected. Nothing has been benchmarked.
