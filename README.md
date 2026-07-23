# rebar: a faster Python `re`

`rebar` is an experiment to build a faster, fully compatible replacement for Python’s regular-expression module. The intended public interface is `import rebar as re`. The comparison uses stable Python 3.14.6 and four separately written Rust, Zig, C, and Python implementations.

No implementation may call Python’s existing regex engine, wrap an external regex package, or delegate matching to another implementation.

## Headline results

The first graph shows whether each independently written engine gives Python's answers on the same **223,198** frozen matching checks. Matching correctness is not a claim of complete compatibility or speed.

![All four independently written engines compared with Python on the same 223,198 matching tests, with the original failures and current results preserved](candidates/evidence/rust-v8-correctness-progress.svg)

The second graph compares each measured Rust design directly with Python on the same **624** practice cases. **1× means the same speed as Python; higher is faster.** The latest fully checked Rust design is **0.929×**, so it is not yet faster than Python. The lower **0.754×** bar is the previous fully checked design; the third bar is an earlier, less completely checked design. All cases, slowdowns, and uncertainty ranges are included.

![Overall practice speed of each recorded Rust design compared with Python, including every case and confidence interval](performance/v7/evidence/rust-v7-calibration-overall.svg)

The existing **12,288-case** final comparison remains unopened. An independently reviewed, larger final protocol is being prepared before any final measurement. Final results for Rust, Zig, and C are **NOT MEASURED**.

## Compatibility at a glance

Every result below uses the same frozen Python answers. “Differences” means observable behavior that does not match Python.

| Built-from-scratch engine | Matching checks | Parser checks | Object and lifetime checks | Tracing and unusual-argument checks |
| --- | ---: | ---: | ---: | ---: |
| Rust | [223,198/223,198](candidates/evidence/rust-v7-edge-oracle-rust-native-interned-attributes.json.gz) | [20,480/20,480](candidates/evidence/rust-v8-rust-interned-attributes-sealed-campaign.json) | [0/393 differences](candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-INTERNED-ATTRIBUTES.json.gz) | [0/479 differences](candidates/evidence/rust-v8-observability-rust-qualified-interned-attributes.json.gz) |
| Zig | [223,198/223,198](candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-06.json.gz) | [20,480/20,480](candidates/evidence/rust-v7-grammar-zig-v8-deep-stage-06.json.gz) | [0/393 differences](candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-06.json.gz) | [0/479 differences](candidates/evidence/rust-v8-observability-zig-qualified-stage-06.json.gz) |
| C | [223,198/223,198](candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-07.json.gz) | [20,480/20,480](candidates/evidence/rust-v7-grammar-vm-v8-deep-stage-07.json.gz) | [0/393 differences](candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-07.json.gz) | [0/479 differences](candidates/evidence/rust-v8-observability-vm-qualified-stage-07.json.gz) |
| Independent Python | [223,198/223,198](candidates/evidence/rust-v8-edge-oracle-ast-deep-stage-01.json.gz) | [20,480/20,480](candidates/evidence/rust-v7-grammar-ast-deep-stage-01.json.gz) | [93/393 differences](candidates/audits/RUST-V8-DEEP-CONTRACT-AST-STAGE-01.json.gz) | NOT MEASURED |

Rust, Zig, and C additionally pass the object and tracing checks in the table. All [75 original C argument failures](candidates/evidence/rust-v8-observability-vm-qualified.json.gz) remain recorded; the independent Python engine still has 93 object-behavior differences.

The larger frozen replacement-and-callback suites expose further real differences:

| Engine | Replacement and callback checks | Deep replacement and callback checks |
| --- | ---: | ---: |
| Rust | [0/8,862 differences](candidates/evidence/rust-v8-replacement-rust-interned-attributes.json.gz) | [0/11,266 differences](candidates/evidence/rust-v8-replacement-rust-interned-attributes-deep.json.gz) |
| Zig | [0/8,862 differences](candidates/evidence/rust-v8-replacement-zig-stage-06-from-scratch-failures.json.gz) | [0/11,266 differences](candidates/evidence/rust-v8-replacement-zig-stage-06-from-scratch-deep-failures.json.gz) |
| C | [0/8,862 differences](candidates/evidence/rust-v8-replacement-vm-stage-07.json.gz) | [0/11,266 differences](candidates/evidence/rust-v8-replacement-vm-deep-stage-07.json.gz) |

Rust also passes the entire [22-stage compatibility campaign](candidates/evidence/rust-v8-rust-interned-attributes-sealed-campaign.json), including Python's own tests and **4,494,555** full-Unicode comparisons. The separately repaired C and Zig engines each pass the six checks listed above, but that is not enough to establish complete compatibility. C's first full campaign exposed [six additional differences in 8,244 frozen checks](candidates/evidence/rust-v8-vm-stage-07-sealed-campaign-failure.json); Zig's full campaign has **NOT YET PASSED**. All original and newly discovered failures remain in the [experiment log](docs/EXPERIMENT-LOG.md).

The [current four-engine from-scratch audit](candidates/audits/FROM-SCRATCH-AUDIT.json) verifies the exact repaired Rust, Zig, C, and Python source, all five loaded native libraries, and **76** checks against external packages and hidden engine-sharing. The [independent Rust audit](candidates/audits/RUST-V8-INTERNED-ATTRIBUTES-FROM-SCRATCH.json) adds **134** checks specific to the current Rust design. The [audit immediately before the final C and Zig repairs](candidates/audits/FROM-SCRATCH-AUDIT-BEFORE-FINAL-REPLACEMENT-REPAIRS.json), [original audit](candidates/audits/FROM-SCRATCH-AUDIT-HISTORICAL-BEFORE-V8-FINAL.json), and [earlier C audit](candidates/audits/FROM-SCRATCH-AUDIT-BEFORE-C-BINDER-REPAIR.json) remain unchanged.

## Overall speed compared with Python

**Final, unseen speed: NOT MEASURED.** On the separate practice data, the fully compatibility-qualified Rust implementation currently measures **0.929×** Python's speed, up from **0.754×** before the first native-call optimization. Neither practice result is a final-test score or a speed claim about Zig or C.

The existing [12,288-case final protocol](performance/v8/HOLDOUT-PROTOCOL.md) and its opening remain unused. Before any final run, an independently reviewed successor must establish that its test inputs are genuinely unpredictable, that timing measures real Python operations, and that each approved engine is the exact version that passed every compatibility and from-scratch check. No final speed, ranking, or confidence interval is invented.

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

Rust improvements use a separate, frozen **624-case practice test**; the final 12,288 cases are never opened to choose an optimization. The [first native-call optimization](performance/v7/evidence/RUST-NATIVE-INTERNED-ATTRIBUTES.md) measures **0.929×** Python's speed, with a **0.893–0.967×** confidence interval and **243/624** substantial slowdowns. The [fully compatible starting point](performance/v7/evidence/RUST-NATIVE-HEAP-BASELINE.md) measured **0.754×**, with **347/624** slowdowns. The [previous, less completely qualified baseline](performance/v7/evidence/RUST-CALIBRATION-BASELINE.md) measured **0.994×**, with **175/624** slowdowns. All three complete results appear in the regenerated graphs; no result demonstrates that the current Rust engine is faster than Python.

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
  tools/audit_rust_interned_attributes_from_scratch.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/rust_v8_multi_candidate_observability.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/rust_v8_multi_candidate_campaign.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v8_holdout_protocol verify --evidence
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/performance_v8_charts.py --self-test
```
