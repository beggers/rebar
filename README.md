# rebar: a faster Python `re` experiment

`rebar` is an experiment to build a faster, fully compatible replacement for Python’s regular-expression module. The intended public interface is `import rebar as re`. The comparison uses stable Python 3.14.6 and four separately written Rust, Zig, C, and Python implementations.

No implementation may call Python’s existing regex engine, wrap an external regex package, or delegate matching to another implementation.

The experiment was **falsified**: the hidden final test found that Zig's `split` does not always match Python. The current Zig-backed source-checkout import is **not a verified drop-in replacement**. There is no winning or installable implementation.

## Headline results

The frozen **24,576-case** final test stopped at a genuine hidden compatibility failure: `v9.split.literal-and-long-prefix.006:warmup:candidates.zig_candidate`. The one-time seal was consumed and was not retried. A faster result is irrelevant when the answers do not match.

![Final hidden compatibility test failed: Zig returned a different split result from Python; no implementation was selected as winner](performance/v9/evidence/V9-FINAL-HOLDOUT-24576-FAILURE-correctness.svg)

The original run completed **14,342 of 24,576 cases**, preserving **1,778,408 of 3,047,424** planned paired observations before failing. Complete final speed, confidence intervals, memory, regression counts, rankings, and the **1.5×** success threshold are **NOT MEASURED**.

![Actual final-test progress before the genuine hidden correctness failure: 14,342 of 24,576 cases and 1,778,408 of 3,047,424 paired rows](performance/v9/evidence/V9-FINAL-HOLDOUT-24576-FAILURE-progress.svg)

The [complete failure report](performance/v9/evidence/FINAL-HOLDOUT-FAILURE.md), [independent failure replay](performance/v9/evidence/V9-FINAL-HOLDOUT-24576-FAILURE.json), [original partial observations](performance/v9/evidence/V9-FINAL-HOLDOUT-24576-RAW.jsonl.gz), and [irreversible one-time marker](performance/v9/evidence/V9-FINAL-HOLDOUT-24576-UNSEAL-MARKER.json) are preserved. The candidates were [selected and frozen before the hidden test](performance/v9/evidence/FINAL-CANDIDATE-FREEZE.md); none was changed after its result.

## Development and public-practice results

All three native engines passed the same **223,198** pre-final matching checks and all **22** development-correctness stages. Those results did not cover the hidden Zig failure and are not proof of final compatibility.

![Original pre-final matching checks for all independently written engines; not evidence of passing the hidden final test](candidates/evidence/rust-v8-correctness-progress.svg)

The latest fair practice run compares C, Zig, and Rust against Python on the **same 624 public cases**. **1× is Python; higher is faster.** C measures **1.334×**, Zig **1.257×**, and Rust **1.150×**. These are practice results only, not final scores or evidence of a successful replacement.

![Overall practice speed and uncertainty for C, Zig, and Rust against standard Python on the same 624 cases](performance/v7/evidence/three-qualified-engines-public-practice-v9-overall.svg)

![Every practice win, uncertain case, loss, and substantial slowdown for C, Zig, and Rust](performance/v7/evidence/three-qualified-engines-public-practice-v9-outcomes.svg)

Rust, Zig, and C each have separately written engines; none wraps Python's `re`, an external package, or another candidate. The independent Python prototype remains incomplete. Passing the earlier development stages does not override the failed hidden test.

## Compatibility at a glance

Every result below uses the same frozen **development** Python answers. “Differences” means observable development-test behavior that does not match Python. The later hidden final test additionally found the Zig `split` mismatch reported above.

| Built-from-scratch engine | Matching checks | Parser checks | Object and lifetime checks | Tracing and unusual-argument checks |
| --- | ---: | ---: | ---: | ---: |
| Rust | [223,198/223,198](candidates/evidence/rust-v7-edge-oracle-rust-owned-capture-init-hoist.json.gz) | [20,480/20,480](candidates/evidence/rust-v8-rust-owned-capture-init-hoist-sealed-campaign.json) | [0/393 differences](candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-OWNED-CAPTURE-INIT-HOIST.json.gz) | [0/479 differences](candidates/evidence/rust-v8-observability-rust-qualified-owned-capture-init-hoist.json.gz) |
| Zig | [223,198/223,198](candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-13.json.gz) | [20,480/20,480](candidates/evidence/rust-v8-zig-stage-13-sealed-campaign.json) | [0/393 differences](candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-13.json.gz) | [0/479 differences](candidates/evidence/rust-v8-observability-zig-qualified-stage-13.json.gz) |
| C | [223,198/223,198](candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-21-singleton-split-memchr.json.gz) | [20,480/20,480](candidates/evidence/rust-v8-vm-stage-21-singleton-split-memchr-sealed-campaign.json) | [0/393 differences](candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-21-SINGLETON-SPLIT-MEMCHR.json.gz) | [0/479 differences](candidates/evidence/rust-v8-observability-vm-qualified-stage-21-singleton-split-memchr.json.gz) |
| Independent Python | [223,198/223,198](candidates/evidence/rust-v8-edge-oracle-ast-deep-stage-01.json.gz) | [20,480/20,480](candidates/evidence/rust-v7-grammar-ast-deep-stage-01.json.gz) | [93/393 differences](candidates/audits/RUST-V8-DEEP-CONTRACT-AST-STAGE-01.json.gz) | NOT MEASURED |

The larger frozen replacement-and-callback checks use the same Python baseline:

| Engine | Replacement and callback checks | Deep replacement and callback checks |
| --- | ---: | ---: |
| Rust | [0/8,862 differences](candidates/evidence/rust-v8-rust-owned-capture-init-hoist-sealed-campaign.json) | [0/11,266 differences](candidates/evidence/rust-v8-rust-owned-capture-init-hoist-sealed-campaign.json) |
| Zig | [0/8,862 differences](candidates/evidence/rust-v8-zig-stage-13-sealed-campaign.json) | [0/11,266 differences](candidates/evidence/rust-v8-zig-stage-13-sealed-campaign.json) |
| C | [0/8,862 differences](candidates/evidence/rust-v8-vm-stage-21-singleton-split-memchr-sealed-campaign.json) | [0/11,266 differences](candidates/evidence/rust-v8-vm-stage-21-singleton-split-memchr-sealed-campaign.json) |

Each engine independently passed the complete **pre-final** 22-stage campaign: [Rust](candidates/evidence/rust-v8-rust-owned-capture-init-hoist-sealed-campaign.json), [Zig](candidates/evidence/rust-v8-zig-stage-13-sealed-campaign.json), and [C](candidates/evidence/rust-v8-vm-stage-21-singleton-split-memchr-sealed-campaign.json). The checks include Python's own tests, all **4,494,555** full-Unicode comparisons, **72,248** extended behavior checks, replacements, callbacks, and isolated crash and deep-recursion tests. Zig nevertheless failed a genuinely hidden final case.

The current [from-scratch audit](candidates/audits/FROM-SCRATCH-AUDIT.json) independently verifies all four implementations, all **five** actual loaded native libraries, and all **76** checks against external packages, Python's existing engine, hidden engine sharing, and substituted native code.

## Public-practice speed compared with Python

**Complete final speed: NOT MEASURED; final compatibility: FAILED.** The following results are from one shared, correctness-checked **public practice run only**. All candidates and Python received the same **624** practice cases and **seven** paired trials.

| Development-tested engine | Overall practice speed | 95% uncertainty range | Clearly faster cases | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| C | 1.334× | 1.286–1.389× | 441/624 | 46/624 |
| Zig | 1.257× | 1.209–1.305× | 341/624 | 96/624 |
| Rust | 1.150× | 1.104–1.196× | 260/624 | 114/624 |

The [complete practice report](performance/v7/evidence/C-STAGE-21-SINGLETON-SPLIT-MEMCHR.md) retains all **17,472** timing rows, **52,416** correctness checks, and all **256** substantial practice slowdowns. The [independent verifier](performance/v7/evidence/three-qualified-engines-public-practice-v9-integrity.json) recomputes all **1,875** confidence intervals and checks all five loaded native libraries. This is the ninth **public practice** comparison, not a final result. It cannot overcome the failed hidden correctness case or establish the required final **1.5×** speedup.

The frozen [24,576-case final protocol](performance/v9/HOLDOUT-PROTOCOL.md) fixes **31** paired rounds, **9,999** confidence draws, hidden real patterns and inputs, genuinely precompiled patterns, and **16** real calls per timed sample. Its [75-check, manifest-bound verification](performance/v9/evidence/HOLDOUT-PROTOCOL-SELF-TEST.json), [prospective seal](performance/v9/evidence/HOLDOUT-PROSPECTIVE-FREEZE.md), and [exact pre-test candidate freeze](performance/v9/evidence/V9-FINAL-CANDIDATE-SELECTION-FREEZE.json) are preserved. The actual one-time final failed on a hidden Zig correctness check; no retry was performed. The [earlier 12,288-case protocol](performance/v8/HOLDOUT-PROTOCOL.md) remains preserved and unopened.

The original [complete-result graph generator](tools/performance_v9_charts.py) and [complete-result verifier](tools/performance_v9_results_audit.py) passed their [95](performance/v9/evidence/PERFORMANCE-CHARTS-PUBLIC-SYNTHETIC-SELF-TEST.json) and [93](performance/v9/evidence/PERFORMANCE-RESULTS-AUDIT-PUBLIC-SYNTHETIC-SELF-TEST.json) synthetic integrity checks. They cannot produce a successful final report because the actual correctness-gated run did not complete. The [separate failed-run replay](tools/audit_v9_failed_holdout.py) and [failure graph generator](tools/render_v9_failed_holdout.py) instead report the genuine failure and clearly label all complete-result metrics **NOT MEASURED**.

## Final failure details

The failed final benchmark provides no valid final speed, confidence interval, memory measurement, regression count, ranking, or winner. Each graph below is generated from the preserved and independently audited incomplete run; none substitutes a public practice result.

![Complete final speed and confidence intervals cannot be established because the hidden compatibility gate failed](performance/v9/evidence/V9-FINAL-HOLDOUT-24576-FAILURE-speed.svg)

![Final memory results were not collected because the one-time correctness-gated benchmark stopped](performance/v9/evidence/V9-FINAL-HOLDOUT-24576-FAILURE-memory.svg)

![Complete final regression counts cannot be established from an incomplete correctness-gated benchmark](performance/v9/evidence/V9-FINAL-HOLDOUT-24576-FAILURE-regressions.svg)

![No candidate ranking or winner is established after the hidden compatibility test failed](performance/v9/evidence/V9-FINAL-HOLDOUT-24576-FAILURE-rankings.svg)

## Detailed practice results

Each graph below is generated directly from the same [independently verified, four-way practice run](performance/v7/evidence/three-qualified-engines-public-practice-v9-integrity.json). No final-test case is used.

![All three candidate engines across all 12 regular-expression operations, with the actual number of cases labeled](performance/v7/evidence/three-qualified-engines-public-practice-v9-api.svg)

![Every one of the 256 substantial practice slowdowns, grouped by candidate and operation](performance/v7/evidence/three-qualified-engines-public-practice-v9-regressions.svg)

![Python-visible temporary allocations for all three engines, including zero-allocation cases](performance/v7/evidence/three-qualified-engines-public-practice-v9-memory.svg)

Memory results describe Python-visible temporary allocations in a shared benchmark process. They do **not** establish isolated native-engine or whole-process memory.

![Overall practice rankings of C, Zig, and Rust against the unchanged Python baseline](performance/v7/evidence/three-qualified-engines-public-practice-v9-rankings.svg)

## Reproduce and inspect the experiment

The [experiment log](docs/EXPERIMENT-LOG.md) preserves intermediate designs, the genuine final failure, rejected optimizations, previous practice measurements, and isolation incidents. The [expanded 24,576-case benchmark](performance/v9/HOLDOUT-PROTOCOL.md) prospectively fixed its hidden test inputs, real-operation timing, memory checks, confidence calculation, and passing rules before the one-time failed final run.

The objective in [GOAL.md](GOAL.md) is immutable. Its SHA-256 is `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`; later clarifications are kept in [AMENDMENTS.md](AMENDMENTS.md).

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.audit_from_scratch --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.audit_from_scratch
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/audit_rust_interned_attributes_from_scratch.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/rust_v8_multi_candidate_observability.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/rust_v8_multi_candidate_campaign.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v9_holdout_protocol self-test --public-synthetic-only
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v9_holdout_protocol verify \
  --manifest performance/v9/holdout-manifest.json --evidence
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/run_frozen_v9_final.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/audit_v9_failed_holdout.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/render_v9_failed_holdout.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_audit self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_charts --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_v2_audit self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_v2_charts --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_v3_audit self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_v3_charts --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_v4_audit self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_v4_charts --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_v5_audit self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_v5_charts --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_v6_audit self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_v6_charts --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_v7_audit self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_v7_charts --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_v8_audit self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_v8_charts --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_v9_audit self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v7_multi_candidate_practice_v9_charts --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/performance_v9_charts.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/performance_v9_results_audit.py self-test --public-synthetic-only \
  --source-sha256 fc85ca331504c12ee012db8ebb02464ed49f22327c7e84ec36f612a2b8d6aa3d \
  --protocol-sha256 a699ce1e661ead447af0643584d69f080e72712059ad611fbd6b998f2ca19219 \
  --output performance/v9/evidence/PERFORMANCE-RESULTS-AUDIT-PUBLIC-SYNTHETIC-SELF-TEST-REPRODUCED.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v8_holdout_protocol verify --evidence
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/performance_v8_charts.py --self-test
```
