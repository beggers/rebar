# rebar: a faster Python `re` experiment

Can a regular-expression engine built from scratch replace
[Python 3.14.6's](https://www.python.org/downloads/release/python-3146/)
`re` and run faster? The intended interface is `import rebar as re`.
Every candidate must use its own matching engine, not Python's engine,
an external regular-expression package, or another candidate.

**Current result:** the independently built C, Rust, and Zig engines each
pass **223,198** initial cases and **393** harder cases. Rust is the only
engine tested against Python's **152** applicable original public-test
records: **150 passed, one exposed a real missing pickling feature, and
one genuinely requires a Python debug build**. There are **no remaining
test-harness failures**. C and Zig have **NOT RUN** those tests. Current
speed and memory are **NOT MEASURED**. There is no winner.

## Current results

![Current Python compatibility: Rust passes 150 original tests, one pickling test remains, one test requires a debug build, and C and Zig have not yet run the original suite](docs/evidence/current-native-correctness-v6.svg)

Python's original test file contains **165** tests. **152** test the
public replacement interface; the other **13** test CPython's private
implementation and are explicitly excluded in two named classes:
`DebugTests` (**4**) and `ImplementationTest` (**9**). No public test is
waived. Both actual Python reference runs pass **151** public tests;
the remaining test genuinely requires a Python debug build.

Rust ran the same **152** public-test records: **150 passed**, one real
pickling incompatibility remains, and the same debug-only test was
skipped. The earlier **11** test-harness errors are resolved, not hidden.
C and Zig are **NOT RUN**. The graph is
[generated from the complete, independently verified current and historical evidence](docs/evidence/current-native-correctness-v6.json).

## Headline results from the last completed comparison

The archived C, Rust, and Zig builds each ran the same 8,192 public examples
as unmodified Python. In these graphs, **1× is Python's speed, higher is
faster, and 1.5× is the target**.

![Overall speed of three archived engines compared with Python; these results do not measure the current builds](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-overall.svg)

| Archived engine | Speed compared with Python | Clearly faster examples | More than 20% slower |
| --- | ---: | ---: | ---: |
| Python baseline | 1.000× | — | — |
| Zig | 1.214× | 4,680 / 8,192 (57.1%) | 1,401 / 8,192 |
| C | 1.124× | 4,511 / 8,192 (55.1%) | 1,433 / 8,192 |
| Previous Rust | 0.957× | 2,444 / 8,192 (29.8%) | 3,106 / 8,192 |

No archived engine achieved both the 1.5× speed target and a clear speed
improvement on at least 60% of examples. The numbers do not predict how the
current builds will perform.

![Faster, uncertain, and slower cases for every archived engine](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-outcomes.svg)

## More detail from that archived comparison

![Archived speed results by regular-expression operation and kind of workload](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-api.svg)

![Every archived example running more than 20 percent slower than Python](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-regressions.svg)

![Temporary Python-visible memory used by the archived engines](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-memory.svg)

The memory graph shows temporary allocations visible to Python; memory
allocated privately by the native engines remains **NOT MEASURED**.

![Overall ranking of the archived engines; this is not a ranking of the current builds](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-rankings.svg)

The [published comparison](performance/postfinal-public-v6/RESULTS.md),
[preserved exact builds](performance/postfinal-public-v6/NATIVE-ARCHIVE-V1.md),
and [predeclared measurement rules](performance/postfinal-public-v6/PROTOCOL.md)
retain the complete results, uncertainty ranges, and all regressions.

## Current engine details

Each engine uses its own implementation. The frozen source and native-binary
[ownership check](candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V21.json)
and independent
[no-delegation check](candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V21.json)
verify that none uses Python's matcher, an external regex package, or another
candidate. Those checks do not establish full compatibility or speed.

A [stricter next engine-independence check](oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V23.md)
has been frozen and independently verified before any engine changes.
Running that check against newly changed engines is **NOT RUN**.
A [matching correctness-proof protocol](oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V26.md)
has also been frozen. Fresh proofs for changed engines are **NOT RUN**.

| From-scratch engine | Initial correctness cases | Harder correctness cases | 152 original public-test records |
| --- | --- | --- | --- |
| Rust | [223,198 / 223,198](candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v24-qualified-pass-proof.json) | [393 / 393](candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-CURRENT-BUILD-V24-PASS-PROOF.json) | [150 passes, 1 incompatibility, 1 debug skip](oracle/cpython-3.14.6/evidence/postfinal-locale-v16-rust-failures-production-summary.json) |
| C | [223,198 / 223,198](candidates/evidence/rust-v7-edge-oracle-vm-postfinal-current-build-v24-qualified-pass-proof.json) | [393 / 393](candidates/audits/RUST-V8-DEEP-CONTRACT-C-POSTFINAL-CURRENT-BUILD-V24-PASS-PROOF.json) | NOT RUN |
| Zig | [223,198 / 223,198](candidates/evidence/rust-v7-edge-oracle-zig-postfinal-current-build-v24-qualified-pass-proof.json) | [393 / 393](candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-CURRENT-BUILD-V24-PASS-PROOF.json) | NOT RUN |

The [original Python baseline](oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle.json),
[complete current Rust failure](oracle/cpython-3.14.6/evidence/postfinal-locale-v16-rust-failures.json),
and [independent failure verification](oracle/cpython-3.14.6/evidence/postfinal-locale-v16-rust-readonly-failure-forensic.json)
are preserved alongside the [earlier unsuccessful run](oracle/cpython-3.14.6/evidence/postfinal-locale-v15-rust-failures.json).
The separately
[frozen expanded public-interface tests](oracle/cpython-3.14.6/PUBLIC-SURFACE-V27.md)
cover **1,376** examples across **43** categories. Python's two reference
runs pass them; the current candidates have **NOT RUN** those tests.
A [separate 264-case buffer-lifetime test](oracle/cpython-3.14.6/PUBLIC-BUFFER-EXPORTER-V1.md)
is frozen for Python's mutable inputs, callbacks, iterators, and scanners.
Its [first Python reference genuinely failed](oracle/cpython-3.14.6/evidence/public-buffer-exporter-v1-self-oracle-failures.json)
because the test assumed every buffer had already been acquired and
released. The original failure is preserved; candidate runs are **NOT RUN**.
A [separate 128-case interpreter-isolation test](oracle/cpython-3.14.6/PUBLIC-SUBINTERPRETER-V1.md)
is frozen for independent Python interpreters, pattern caches, and object
lifetimes. [Two actual Python reference processes pass all 128 cases](oracle/cpython-3.14.6/evidence/public-subinterpreter-v1-self-oracle.json).
Candidate interpreter-isolation runs are **NOT RUN**.

The [corrected original-test protocol](oracle/cpython-3.14.6/POSTFINAL-LOCALE-V16.md)
keeps every public test and removes only the test harness's own interference.
An [independent read-only check](oracle/cpython-3.14.6/evidence/postfinal-locale-v16-readonly-native-bridge-integration-pass.json)
verifies the two Python baselines, all three from-scratch engines, and their
preserved evidence without importing or running an engine. A
[separate independently replayed verification](oracle/cpython-3.14.6/evidence/postfinal-locale-v16-root-verified-readonly-native-bridge-integration-pass.json)
checks the actual historical failure, all twelve engine proofs, and both
Python references again. The corrected protocol has now run the full Rust
suite; its one real incompatibility remains. C and Zig have **NOT RUN**
that suite.

The [independent-language inventory](experiments/FROM-SCRATCH-LANGUAGE-LANDSCAPE-V1.md)
also covers separately authored
[C++](experiments/cpp_from_scratch_v1/STATIC-GAPS-V1.md) and
[Go](experiments/go_from_scratch_v1/STATIC-GAPS-V1.md) designs. They are
**NOT BUILT, NOT RUN, and NOT QUALIFIED**. The
[pinned official Zig compiler](toolchains/zig-0.16.0.lock.json) makes the
existing Zig engine reproducible from its own source. Different bindings
to the same matching engine never count as independent candidates.

Detailed experiments, rejected approaches, setup failures, commands, and
complete evidence belong in the [experiment log](docs/EXPERIMENT-LOG.md),
not in this overview.

## Larger fair speed comparison

The planned public comparison and independently generated final test
will each cover **131,072 examples**: nearly four times the previous
**33,280-example** plan. The comparison will balance everyday matching,
searching, splitting, replacements, Unicode, bytes, compilation, cached
patterns, iterators, callbacks, unusual inputs, memory, and the cost of
calling each native engine from Python.

Freeze and open the final test only after all three genuinely separate,
from-scratch engines pass every required correctness and independence
check. Run Python and each qualifying engine on exactly the same cases;
report overall speed, uncertainty, memory, and every slowdown. The
expanded test is **NOT FROZEN** and **NOT OPENED**. Current speed, memory,
uncertainty, slowdowns, and rankings are **NOT MEASURED**.

## Evidence and reproduction

The [experiment log](docs/EXPERIMENT-LOG.md) records the detailed
experiments, rejected designs, genuine failures, and their resolutions.
The original objective in [GOAL.md](GOAL.md) remains unchanged, with
SHA-256
`e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`.
[AMENDMENTS.md](AMENDMENTS.md) records later clarifications separately.

Recheck the frozen current-engine audits, original public-test runner,
expanded public tests, and the exact generated headline chart without
benchmarking a candidate:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

"$PY" -I -B tools/postfinal_independent_engine_audit_v21.py --self-test
"$PY" -I -B tools/postfinal_independent_engine_audit_v23.py --self-test
"$PY" -I -B tools/postfinal_current_build_proofs_v24.py --self-test
"$PY" -I -B tools/postfinal_current_build_proofs_v26.py --self-test
"$PY" -I -B tools/postfinal_cpython_locale_oracle_v15.py --self-test
"$PY" -I -B tools/postfinal_cpython_locale_oracle_v16.py --self-test
"$PY" -I -B tools/python_re_public_surface_oracle_stage27.py --self-test
"$PY" -I -B tools/python_re_buffer_exporter_oracle_v1.py --self-test
"$PY" -I -B tools/python_re_subinterpreter_oracle_v1.py --self-test
"$PY" -I -B tools/render_current_correctness_v6.py --self-test
"$PY" -I -B tools/render_current_correctness_v6.py --check
```
