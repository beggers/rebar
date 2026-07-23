# rebar: a faster Python `re`

`rebar` is an experiment to build a faster, fully compatible replacement for Python's `re`, from scratch. It compares independently written Zig, C, Rust, and Python engines with [stable Python 3.14.6](https://www.python.org/downloads/release/python-3146/). No engine may use Python's existing regex implementation, an external regex package, or another candidate's engine. The intended public import is `import rebar as re`.

**Current status:** all four independently written engines pass every original matching test. Zig and C also pass every tougher real-world behavior test. Rust is undergoing final verification; the independent Python implementation still has recorded differences. The larger, final speed test remains sealed.

| From-scratch engine | Original compatibility tests | Tougher object and lifetime tests |
| --- | ---: | ---: |
| [Rust](candidates/evidence/rust-v8-edge-oracle-rust-scanner-cmethod.json.gz) | 223,198/223,198 | [43 differences](candidates/audits/RUST-V8-DEEP-CONTRACT-SCANNER-CMETHOD.json.gz) |
| [Zig](candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-04.json.gz) | 223,198/223,198 | [0 differences](candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-04.json.gz) |
| [C](candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-03.json.gz) | 223,198/223,198 | [0 differences](candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-03.json.gz) |
| [Independent Python](candidates/evidence/rust-v8-edge-oracle-ast-deep-stage-01.json.gz) | 223,198/223,198 | [93 differences](candidates/audits/RUST-V8-DEEP-CONTRACT-AST-STAGE-01.json.gz) |

The [original 104 Rust failures](candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz) remain preserved. The final speed of a fully compatible engine is **NOT MEASURED**.

![Original and current differences from Python for all four independently built engines, on the same 223,198 compatibility tests](candidates/evidence/rust-v8-correctness-progress.svg)

This graph shows matching correctness, not speed. The separate **393-test** behavior results remain visible in the table above.

The [expanded final speed test](performance/v8/HOLDOUT-PROTOCOL.md) contains **12,288 genuinely different, still-unseen cases**, with **31** repeated comparisons per case. It stays sealed until at least three independently written engines pass every compatibility and no-wrapper check. Its results are **NOT MEASURED**.

## Overall speed compared with Python

These are the **original measurements**, not results from the new sealed test. The original test had **20,624 cases**, including **10,312** held-back cases. Each original engine received the same inputs and **13** repeated comparisons, producing **1,340,560** recorded measurements. In every graph, **1× is Python's speed; higher is faster**.

![Overall speed of all four replacements compared with Python re on 10,312 unseen cases](performance/v7/evidence/initial-overall.svg)

| From-scratch engine | Speed on unseen cases | 95% confidence interval | Clearly faster cases | Cases more than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| Original Zig | **1.609×** | 1.608–1.610× | **8,868/10,312** | **105/10,312** |
| C | **1.271×** | 1.270–1.272× | 7,369/10,312 | 1,116/10,312 |
| Original Rust, before compatibility fixes | **0.925×** | 0.925–0.926× | 3,623/10,312 | 3,905/10,312 |
| Independent Python engine | **0.022×** | 0.022–0.022× | 271/10,312 | 9,884/10,312 |

The original Zig engine was fastest, but **none of these measured engines passed the complete compatibility tests**. Their speed does not make them drop-in replacements. The updated Rust engine has not been measured on the original held-back cases or the newly expanded final test.

A separate [223,198-check compatibility test](candidates/evidence/RUST-V7-EDGE-ORACLE.md) was frozen before changing any engine. Standard Python passes all **223,198** checks. The original Zig engine has **5,281** differences, Rust **24,462**, C **52,655**, and the independent Python engine **52,151**. **No original candidate is a drop-in replacement for every Python `re` user.** The original failures, inputs, expected answers, and seeds are preserved; a replacement must pass every check before it can be selected.

The previous [corrected Rust baseline](candidates/evidence/RUST-V7-CORRECTED-V4.md) passed **223,198/223,198** original compatibility checks, **20,480/20,480** independent parser tests, **14,783/14,783** object checks, and **4,494,555/4,494,555** Unicode checks, without external Rust packages. It also passed Python's own runnable tests, with two explicitly recorded unavailable-locale skips. The stronger **393-test** suite subsequently exposed **104** real differences. The [first repaired Rust version](candidates/audits/RUST-V8-DEEP-CONTRACT-SCANNER-LIFETIMES.json.gz) retains **223,198/223,198** and reduces those differences to **62**. Rust is not yet a universal replacement.

![Corrected Rust passes all 223,198 Python compatibility checks; every original from-scratch engine has visible mismatches](candidates/evidence/rust-v7-correctness.svg)

The [corrected-Rust practice comparison](performance/v7/evidence/RUST-CALIBRATION-BASELINE.md) measures **624** separate practice cases, not the unseen test. Rust runs at **0.994×** Python's speed, with a **0.956–1.034×** confidence interval. Because that interval includes **1×**, a speedup has **not** been established. The complete results preserve all **175/624** cases taking more than 20% longer. All unsuccessful changes and their measurements remain in the [experiment log](docs/EXPERIMENT-LOG.md).

![Corrected Rust practice speed compared with Python, including its full confidence interval; the unseen test remains sealed](performance/v7/evidence/rust-v7-calibration-overall.svg)

The [independent 20,480-pattern grammar audit](candidates/evidence/RUST-V7-GRAMMAR-ORACLE.md) additionally retains all **5,662 invalid patterns**, their exact Python error messages and positions, and every original candidate failure.

The [14,783-check object and API audit](candidates/evidence/RUST-V7-OBJECT-ORACLE.md) separately verifies Python's match objects, exact byte identity, search windows, buffer lifetimes, signatures, hashing, warnings, and errors.

The [independent tracing and callback audit](candidates/evidence/RUST-V7-OBSERVABILITY-ORACLE.md) adds **479** Python-visible checks, **34** malformed native calls, and **13** active checks against using Python's regex engine. The [latest Rust result](candidates/evidence/rust-v8-observability-scanner-cmethod.json.gz) passes every check and verifies that its genuine native iterator behaves like Python's. Its [source and native-code audit](candidates/audits/RUST-V8-CMETHOD-FROM-SCRATCH.json) verifies all five Rust artifacts, zero external packages, **76** shared no-delegation checks, and **104** variant-specific integrity checks.

The stronger tests preserve all **104** original Rust failures and both intermediate Rust results, at **62** and **43** differences. Zig improves from **141** differences to **zero**; C improves from **130**, through **38**, to **zero**; and independent Python improves from **129** to **93**. All engines face exactly the same frozen **393** cases. Python agrees with itself on every case, and private garbage-collector details are never counted as public failures.

Rust improvements are compared using a [sealed practice-only test](candidates/evidence/RUST-V7-CALIBRATION-ISOLATION.md). It keeps all **10,312** unseen final cases inaccessible while testing **624** representative practice cases; improved Rust speed remains **NOT MEASURED**.

![Overall rankings on the practice cases, independently unseen cases, and all cases](performance/v7/evidence/initial-rankings.svg)

The [complete slowdown audit](performance/v7/evidence/REGRESSION-AUDIT.md) lists all **105** unseen Zig slowdowns and preserves all **29,771** slowdowns across all four engines and both cohorts. A slowdown means a task actually took more than 20% longer than Python: `Python time / candidate time < 5/6`. No case, candidate, unfavorable result, or confidence interval has been removed.

## What was tested

The test covers text, bytes and buffers; Unicode; short and long inputs; captures; replacements; search, match, split, scanners, and iteration; compilation and repeated calls; source code, configuration, structured data, and logs; lookarounds, boundaries, and backreferences; matching, nonmatching, and zero-length results. All **64 added workload families** contain distinct practice and unseen examples.

![Coverage of the expanded Python regular-expression benchmark](performance/v7/evidence/coverage.svg)

All five original engines agreed with Python on the **20,624 original speed-test answers**; the separate **223,198-check** compatibility test exposes the more difficult differences. The [original measurement protocol](performance/v7/PROTOCOL.md) fixes cases, repetitions, correctness checks, and memory reporting. The preserved [all-engine audit](candidates/audits/FROM-SCRATCH-AUDIT.json) records the exact original source and libraries it verified; historical results do not certify newer binaries. The [current Rust-only audit](candidates/audits/RUST-V8-CMETHOD-FROM-SCRATCH.json) separately verifies the latest Rust source, compiler, engine, native bindings, actual loaded libraries, and **zero external Rust packages**.

## Detailed graphs

The larger, still-unseen test has a [self-testing graph generator](tools/performance_v8_charts.py) for overall speed, confidence, every operation, memory, every slowdown, and final rankings. No graph or measurement is invented before that test is run.

The first two graphs are explicitly **practice-only** and include all **624** corrected-Rust cases; they are not final unseen results.

![Corrected Rust practice results for all 12 regular-expression operations](performance/v7/evidence/rust-v7-calibration-api.svg)

![Every faster, slower, unresolved, and more-than-20-percent-slower corrected-Rust practice case](performance/v7/evidence/rust-v7-calibration-win-loss.svg)

![Every one of the 175 corrected-Rust practice cases taking more than 20 percent longer, shown by operation](performance/v7/evidence/rust-v7-calibration-regressions.svg)

![Python-traced temporary memory for corrected Rust across all 12 practice operations; this does not estimate native process memory](performance/v7/evidence/rust-v7-calibration-memory.svg)

The remaining historical graphs show the complete original unseen results, not selected examples. Each new workload row represents all **64** independently held-back cases.

![Where the from-scratch Zig replacement is faster or slower than Python](performance/v7/evidence/initial-zig-speed.svg)

![Where the from-scratch Rust replacement is faster or slower than Python](performance/v7/evidence/initial-rust-speed.svg)

![Speed of every candidate across the 64 expanded workload families](performance/v7/evidence/initial-family-speed.svg)

![Temporary Python memory used by each candidate relative to Python re](performance/v7/evidence/initial-memory.svg)

![Every clearly faster case and every slowdown for each candidate and workload](performance/v7/evidence/initial-win-loss.svg)

Python-traced temporary memory on the unseen cases has a median ratio of **0.503×** for Zig, **0.442×** for C, **0.676×** for Rust, and **9.687×** for the independent Python engine. Process memory was also recorded for every trial, but all engines shared one measurement process, so those observations **cannot establish engine-specific process-memory usage**.

## Reproduce

The [complete experiment log](docs/EXPERIMENT-LOG.md) keeps previous designs, measurements, rejected experiments, correctness failures, and isolation incidents out of the headline results. The immutable objective is [GOAL.md](GOAL.md), SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`; scope amendments are recorded in [AMENDMENTS.md](AMENDMENTS.md).

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.audit_from_scratch --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/audit_rust_from_scratch.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/audit_rust_from_scratch.py \
  --edge-oracle candidates/evidence/rust-v8-edge-oracle-rust-scanner-lifetimes.json.gz
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/audit_rust_variants_from_scratch.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/audit_rust_variants_from_scratch.py \
  --edge-oracle candidates/evidence/rust-v8-edge-oracle-rust-scanner-cmethod.json.gz
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.audit_from_scratch
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v8_holdout_protocol self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v8_holdout_protocol verify --evidence
PYTHONPATH=. "$PY" tools/performance_v8_charts.py --self-test
PYTHONPATH=. "$PY" tools/perf_v7.py self-test
PYTHONPATH=. "$PY" tools/perf_v7.py verify --output /tmp/rebar-v7-correctness.json
PYTHONPATH=. "$PY" tools/perf_v7_delegation_audit.py
PYTHONPATH=. "$PY" tools/perf_v7_regression_audit.py --self-test
PYTHONPATH=. "$PY" tools/rust_v7_edge_oracle.py \
  --module re --output /tmp/rebar-v7-edge-self.json.gz
PYTHONPATH=. "$PY" tools/rust_v7_edge_oracle.py \
  --module candidates.rust_candidate --output /tmp/rebar-v7-edge-rust.json.gz
PYTHONPATH=. "$PY" tools/rust_v7_correctness_chart.py --self-test
PYTHONPATH=. "$PY" tools/rust_v7_grammar_oracle.py verify
PYTHONPATH=. "$PY" tools/rust_v7_grammar_oracle.py gate \
  --module candidates.rust_candidate --require-pass
gzip -dc candidates/evidence/rust-v7-corrected-v4/rust-v7-object-rust.json.gz \
  | jq -e '.checks == 14783 and .failed == 0'
PYTHONPATH=. "$PY" tools/rust_campaign_gate.py --sealed-practice-self-test
PYTHONPATH=. "$PY" tools/rust_campaign_gate.py --sealed-practice-only \
  --output /tmp/rebar-rust-sealed-correctness.json
PYTHONPATH=. "$PY" tools/rust_v7_observability_oracle.py --self-test
PYTHONPATH=. "$PY" tools/rust_v7_observability_oracle.py verify
PYTHONPATH=. "$PY" tools/rust_v7_observability_variant.py verify \
  --edge-oracle candidates/evidence/rust-v8-edge-oracle-rust-scanner-lifetimes.json.gz
PYTHONPATH=. "$PY" tools/rust_v8_observability_variants.py verify \
  --edge-oracle candidates/evidence/rust-v8-edge-oracle-rust-scanner-cmethod.json.gz
PYTHONPATH=. "$PY" tools/rust_v8_deep_contract_oracle.py --self-test
PYTHONPATH=. "$PY" tools/rust_v8_deep_contract_variant.py --self-test
PYTHONPATH=. "$PY" tools/rust_v8_multi_candidate_contract.py --self-test
PYTHONPATH=. "$PY" tools/rust_v8_correctness_progress.py self-test
# Inspect both preserved complete compatibility results without overwriting them:
gzip -dc candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz \
  | jq '{checks, status, public_mismatch_count, public_mismatch_family_counts}'
gzip -dc candidates/audits/RUST-V8-DEEP-CONTRACT-SCANNER-LIFETIMES.json.gz \
  | jq '{checks, status, public_mismatch_count, public_mismatch_family_counts}'
PYTHONPATH=. "$PY" tools/rust_v7_calibration_pilot.py self-test
PYTHONPATH=. "$PY" tools/rust_v7_calibration_pilot.py plan --verify
PYTHONPATH=. "$PY" tools/rust_v7_calibration_priorities.py --self-test
PYTHONPATH=. "$PY" tools/rust_v7_calibration_result_audit.py --self-test
PYTHONPATH=. "$PY" tools/rust_v7_calibration_variant_audit.py --self-test
PYTHONPATH=. "$PY" tools/rust_v7_calibration_charts.py --self-test

gzip -dc performance/v7/evidence/initial-raw.jsonl.gz > /tmp/rebar-v7-raw.jsonl
gzip -dc performance/v7/evidence/initial-summary.json.gz > /tmp/rebar-v7-summary.json

PYTHONPATH=. "$PY" tools/perf_v7_result_audit.py \
  --raw /tmp/rebar-v7-raw.jsonl \
  --summary /tmp/rebar-v7-summary.json \
  --output /tmp/rebar-v7-integrity.json

PYTHONPATH=. "$PY" tools/performance_v7_charts.py \
  --summary /tmp/rebar-v7-summary.json --prefix /tmp/rebar-v7

PYTHONPATH=. "$PY" tools/perf_v7_regression_audit.py \
  --integrity performance/v7/evidence/initial-integrity.json \
  --summary performance/v7/evidence/initial-summary.json.gz \
  --output /tmp/rebar-v7-regressions.md \
  --json-output /tmp/rebar-v7-regressions.json.gz
```
