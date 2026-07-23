# rebar: a faster Python `re`

`rebar` is an experiment to build a faster, fully compatible replacement for Python’s regular-expression module. The intended public interface is `import rebar as re`. The comparison uses stable Python 3.14.6 and four separately written Rust, Zig, C, and Python implementations.

No implementation may call Python’s existing regex engine, wrap an external regex package, or delegate matching to another implementation.

## Compatibility at a glance

Every result below uses the same frozen Python answers. “Differences” means observable behavior that does not match Python.

| Built-from-scratch engine | Matching checks | Parser checks | Object and lifetime checks | Tracing and unusual-argument checks |
| --- | ---: | ---: | ---: | ---: |
| Rust | [223,198/223,198](candidates/evidence/rust-v8-edge-oracle-rust-native-heap-final.json.gz) | [20,480/20,480](candidates/evidence/rust-v7-grammar-rust-v8-native-heap-final.json.gz) | [0/393 differences](candidates/audits/RUST-V8-DEEP-CONTRACT-NATIVE-HEAP-FINAL.json.gz) | [0/479 differences](candidates/evidence/rust-v8-observability-rust-qualified.json.gz) |
| Zig | [223,198/223,198](candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-04.json.gz) | [20,480/20,480](candidates/evidence/rust-v7-grammar-zig-deep-stage-04.json.gz) | [0/393 differences](candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-04.json.gz) | [0/479 differences](candidates/evidence/rust-v8-observability-zig-qualified.json.gz) |
| C | [223,198/223,198](candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-04.json.gz) | [20,480/20,480](candidates/evidence/rust-v7-grammar-vm-v8-deep-stage-04.json.gz) | [0/393 differences](candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-04.json.gz) | [0/479 differences](candidates/evidence/rust-v8-observability-vm-qualified-stage-04.json.gz) |
| Independent Python | [223,198/223,198](candidates/evidence/rust-v8-edge-oracle-ast-deep-stage-01.json.gz) | [20,480/20,480](candidates/evidence/rust-v7-grammar-ast-deep-stage-01.json.gz) | [93/393 differences](candidates/audits/RUST-V8-DEEP-CONTRACT-AST-STAGE-01.json.gz) | NOT MEASURED |

![All four from-scratch engines compared with Python on the same 223,198 matching tests, including every original failure and every current result](candidates/evidence/rust-v8-correctness-progress.svg)

This graph shows matching correctness, not speed. Rust, Zig, and C additionally pass the complete behavior and tracing checks. All [75 original C argument failures](candidates/evidence/rust-v8-observability-vm-qualified.json.gz) remain recorded; the independent Python engine still has 93 object-behavior differences and is not presented as fully compatible.

The [current all-engine audit](candidates/audits/FROM-SCRATCH-AUDIT.json) independently verifies all four parsers and matching engines, all five actually loaded native libraries, and **76** checks against external engines, hidden delegation, altered binaries, and unsafe loading. Both the [original audit](candidates/audits/FROM-SCRATCH-AUDIT-HISTORICAL-BEFORE-V8-FINAL.json) and the [pre-repair audit](candidates/audits/FROM-SCRATCH-AUDIT-BEFORE-C-BINDER-REPAIR.json) are preserved unchanged.

## Overall speed compared with Python

**The speed of the current fully compatible replacements is NOT MEASURED.**

The [new, frozen final test](performance/v8/HOLDOUT-PROTOCOL.md) contains **12,288 genuinely different, still-unseen cases** and **31** paired repetitions per case. It remains sealed until at least three independent replacements pass every frozen compatibility and source-code check. No unseen result, final ranking, or confidence interval is invented.

![Historical overall speed of the original Rust, Zig, C, and Python engines relative to Python; these older engines did not pass the full compatibility checks](performance/v7/evidence/initial-overall.svg)

The graph immediately above is **historical context only**. It measures older, not fully compatible engines on the original **10,312-case** unseen test. A value above **1×** was faster than Python.

| Original engine, before complete compatibility fixes | Historical speed | 95% confidence interval | Clearly faster cases | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| Zig | 1.609× | 1.608–1.610× | 8,868/10,312 | 105/10,312 |
| C | 1.271× | 1.270–1.272× | 7,369/10,312 | 1,116/10,312 |
| Rust | 0.925× | 0.925–0.926× | 3,623/10,312 | 3,905/10,312 |
| Independent Python | 0.022× | 0.022–0.022× | 271/10,312 | 9,884/10,312 |

These measurements cannot establish the speed of any corrected engine or select a winner.

## Detailed practice results

Rust improvements use a separate, frozen **624-case practice test**; the final 12,288 cases are never opened to choose an optimization. The [previous corrected Rust baseline](performance/v7/evidence/RUST-CALIBRATION-BASELINE.md) measured **0.994×** Python’s speed, with a **0.956–1.034×** confidence interval. That interval crosses **1×**, so it does not establish a speedup. All **175/624** cases taking more than 20% longer remain visible.

![Previous corrected Rust practice speed and full confidence interval relative to Python](performance/v7/evidence/rust-v7-calibration-overall.svg)

![Rust practice speed for all 12 regular-expression operations](performance/v7/evidence/rust-v7-calibration-api.svg)

![Every faster, slower, unresolved, and substantially slower Rust practice case](performance/v7/evidence/rust-v7-calibration-win-loss.svg)

![Every Rust practice slowdown greater than 20%, grouped by operation](performance/v7/evidence/rust-v7-calibration-regressions.svg)

![Temporary Python allocations for all 12 Rust practice operations](performance/v7/evidence/rust-v7-calibration-memory.svg)

This memory graph measures allocations visible to Python. It does not establish native Rust memory use or engine-specific process memory.

## Detailed historical results

The following graphs retain every original workload and loss. They describe the **older, not fully compatible engines**, not the expanded sealed final test.

![Historical overall rankings on the complete original practice, unseen, and combined cases](performance/v7/evidence/initial-rankings.svg)

![Historical Zig speedups and slowdowns across the original workloads](performance/v7/evidence/initial-zig-speed.svg)

![Historical Rust speedups and slowdowns across the original workloads](performance/v7/evidence/initial-rust-speed.svg)

![Historical results for every original engine and all expanded workload families](performance/v7/evidence/initial-family-speed.svg)

![Historical Python-traced temporary allocations for each original engine](performance/v7/evidence/initial-memory.svg)

![Every historical faster case and slowdown, without omitting an engine or workload](performance/v7/evidence/initial-win-loss.svg)

## Reproduce and inspect the experiment

The [experiment log](docs/EXPERIMENT-LOG.md) contains intermediate designs, complete failed tests, rejected optimizations, previous measurements, and isolation incidents. The [expanded benchmark](performance/v8/HOLDOUT-PROTOCOL.md) fixes its cases, paired repetitions, memory checks, confidence calculation, and passing rules before any final measurement.

The objective in [GOAL.md](GOAL.md) is immutable. Its SHA-256 is `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`; later clarifications are kept in [AMENDMENTS.md](AMENDMENTS.md).

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.audit_from_scratch --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.audit_from_scratch
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/audit_rust_native_heap_from_scratch.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/rust_v8_multi_candidate_observability.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/rust_v8_multi_candidate_campaign.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v8_holdout_protocol verify --evidence
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/performance_v8_charts.py --self-test
```
