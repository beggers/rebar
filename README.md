# rebar: a faster Python `re` experiment

Build a genuine, faster replacement for Python 3.14.6's regular-expression module:

```python
import rebar as re
```

Each candidate must use its own matching engine built from scratch. Wrapping Python's engine, an external regular-expression package, or another candidate does not count.

## Headline results

![Compatibility against the same 2,807 Python checks: all three from-scratch Rust, C, and Zig engines pass every check](docs/evidence/candidate-correctness-overview-v2.svg)

![Expanded replacement checks: Python passes all 5,120 checks; Rust, C, and Zig have not yet been measured](docs/evidence/substitution-buffer-overview-v2.svg)

![Additional scanner checks: Python passes all 2,854; Rust and C each fail 116; Zig fails 1,364](docs/evidence/scanner-verbose-overview-v1.svg)

![Additional memory-safety checks: Python, Rust, C, and Zig all pass all 1,024 checks](docs/evidence/managed-buffer-lifetime-overview-v1.svg)

| Implementation | Built from scratch | Starting checks | Extra safety checks | Extra scanner checks | Expanded replacement checks | Speed compared with Python |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Python `re` | Baseline | 2,807 / 2,807 | 1,024 / 1,024 | 2,854 / 2,854 | 5,120 / 5,120 | 1.000× |
| Our Rust engine | PASS | 2,807 / 2,807 | 1,024 / 1,024 | 2,738 / 2,854 | NOT MEASURED | NOT MEASURED |
| Our C engine | PASS | 2,807 / 2,807 | 1,024 / 1,024 | 2,738 / 2,854 | NOT MEASURED | NOT MEASURED |
| Our Zig engine | PASS | 2,807 / 2,807 | 1,024 / 1,024 | 1,490 / 2,854 | NOT MEASURED | NOT MEASURED |

The starting checks and graphs are previously recorded development results.
New, independent two-Python references for the **864** general, **1,024**
scanner, and **768** buffer checks are **NOT RUN**. Each must be verified
separately before a candidate can pass the final compatibility gate. Current
speed and final results are **NOT MEASURED**.

All three engines are independently built from scratch and face the same 2,807 original checks. The scanner graph shows verified mismatches. The changing-buffer graph preserves a falsified historical test and does not establish **1,888** implementation failures. Original results and test-harness errors are preserved, never excluded.

A separate live audit confirms that each Rust, C, and Zig engine uses its own matching implementation. None calls Python's matcher, an external regular-expression package, or another candidate.

The 1.065× graph is a historical result for the earlier, pre-repair Rust engine on 864 public development examples. Its measured 95% interval is 1.049×–1.081×; it does not meet the 1.5× target and does not measure the current code. Current Rust, C, and Zig speeds are **NOT MEASURED**. The final comparison remains closed until all three engines pass every frozen compatibility, safety, and ownership check.

## Detailed compatibility

| Python behavior | Cases | Rust | C | Zig |
| --- | ---: | ---: | ---: | ---: |
| Python's original runnable public tests | 151 | 151 | 151 | 151 |
| General public behavior | 864 | 864 | 864 | 864 |
| Scanners and callbacks | 1,024 | 1,024 | 1,024 | 1,024 |
| Memory views and buffers | 768 | 768 | 768 | 768 |
| Total matching checks | 2,807 | 2,807 | 2,807 | 2,807 |
| Additional memory-lifetime safety, counted separately | 1,024 | 1,024 | 1,024 | 1,024 |
| Additional scanner and pattern-comment checks, counted separately | 2,854 | 2,738; 116 failures | 2,738; 116 failures | 1,490; 1,364 failures |
| Additional public types, copying, and serialization | 6,912 | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| Corrected replacement and buffer checks; original test preserved | 5,120 | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| Corrected changing-size buffer checks; original test preserved | 10,240 | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| Python buffer exporters and retained scanners | 264 | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| Simultaneous isolated Python interpreters | 128 | NOT MEASURED | NOT MEASURED | NOT MEASURED |

Python's genuine debug-only test is skipped equally and is not included in the denominator.

![Detailed public correctness: Python and the Rust engine match on all 864 public examples](docs/evidence/rust-public-correctness-v1.svg)

An additional, frozen 1,024-case memory-lifetime safety suite has a passing two-Python baseline. Rust, C, and the repaired Zig engine each pass all 1,024 cases. Rust's original 86 failures, Zig's earlier 47 failures, its unsafe intermediate design, and the rejected process-ID attempts all remain preserved. These cases are counted separately and are never silently added to the 2,807 original checks.

A separate, frozen 2,854-case scanner and pattern-comment suite has two matching Python baselines. Rust and C each pass 2,738 cases and fail 116. Zig passes 1,490 cases and fails 1,364. Every failure is preserved.

An additional **6,912** frozen checks cover Python's public pattern and match types, flags, object identity, copying, weak references, all six serialization formats, cache behavior, and warnings. Two independently isolated Python references agree on **6,912 / 6,912** cases. All three candidate results are **NOT MEASURED**.

A corrected, separately frozen **5,120**-case replacement test retains every original input, exception, callback, and buffer observation. It fixes only the reported identity of its own test callback. Two independently isolated Python reference processes now agree on **5,120 / 5,120** cases. All three candidate results are **NOT MEASURED**.

The original replacement test remains independently **FALSIFIED**. Its Python reference ran the test as a script while candidates imported it, producing **128 false failures for both C and Zig**. The preserved C report contains **464** differences: **128** test-harness errors and **336** real differences. The preserved Zig report contains **192**: **128** test-harness errors and **64** real differences. These historical results do not qualify either candidate.

A corrected, separately frozen **10,240**-case changing-buffer test retains every original input and observable result. It fixes only the reported identity of its own test callback. Two independently isolated Python references now agree on **10,240 / 10,240** cases. All three candidate results are **NOT MEASURED**.

An additional **128** frozen checks test real, simultaneous isolated Python interpreters, including separate regex caches, matching, callbacks, memory ownership, and safe interpreter shutdown. Two independent Python references pass all **128 / 128** stronger V2 checks; the original passing reference is also preserved. All three candidate results are **NOT MEASURED**.

Another **264** frozen checks cover direct and wrapped Python buffer exporters, all public matching operations, retained scanners, replacement callbacks, and exact memory-release order. Two independently isolated Python references now agree on **264 / 264** cases. Both original failed test attempts remain preserved. All three candidate results are **NOT MEASURED**.

The original changing-buffer test remains independently **FALSIFIED**. Its preserved C report records **1,888** differences: **496** test-harness errors and **1,392** other differences. The historical graph and earlier process-ID collision are preserved.

![Falsified historical changing-buffer report: its 1,888 recorded C differences include 496 test-harness errors](docs/evidence/shape-changing-buffer-overview-v1.svg)

This historical graph is preserved as evidence of the original error; its red bar is **NOT QUALIFIED** and must not be interpreted as **1,888** genuine implementation failures.

The first attempt to record the 5,120-case Python baseline exceeded the original recorder's safety limit. Its complete failure remains preserved alongside the later, independently passing baseline.

## Detailed development speed

![Historical speed before the latest compatibility repairs: Python at 1.000 times, old Rust at 1.065 times, and the 1.5-times target](docs/evidence/rust-public-speed-v2-overall.svg)

![Results for all 864 public examples: 183 clearly faster, 213 clearly slower, and 468 inconclusive](docs/evidence/rust-public-speed-v2-outcomes.svg)

![Rust development speed for each of the 36 measured operations, including operations that are slower than Python](docs/evidence/rust-public-speed-v2-operations.svg)

![Measured slowdowns greater than 20 percent: zero among all 864 public development examples](docs/evidence/rust-public-speed-v2-regressions.svg)

These historical development graphs include every measured result for the old Rust engine. On the 864 public examples, 183 are clearly faster, 213 are clearly slower, and 468 are inconclusive. No result is hidden. Current-candidate speed, native memory use, and final timings for Rust, C, and Zig are **NOT MEASURED**.

## Larger final comparison

The proposed final comparison contains 4,194,304 separately generated examples and 24 fairly ordered measurement rounds. It covers common Python operations, unusual patterns, strings, bytes, compilation, reuse, Python-to-native overhead, and memory.

The final examples will remain **NOT FROZEN**, **NOT GENERATED**, and **NOT OPENED** until three independently built candidates pass the same complete compatibility and ownership checks. Success requires at least a 1.5× overall speedup, statistically faster results on at least 60% of cases, and an explanation of every slowdown greater than 20%. There is **no winner**.

## Evidence and reproduction

- [Complete experiment log, raw results, rejected designs, and failure history](docs/EXPERIMENT-LOG.md).
- [Authenticated headline graph inputs](docs/evidence/candidate-correctness-overview-v2.inputs.json), [generated graph data](docs/evidence/candidate-correctness-overview-v2.json), and [graph generator](tools/render_candidate_correctness_overview_v2.py).
- [Frozen original Python compatibility tests](tools/independent_original_cpython_suite_v5.py) and [shared candidate behavior tests](tools/independent_public_contract_v3.py).
- [Complete accounting for Python's original regex tests](oracle/cpython-3.14.6/UPSTREAM-ACCOUNTING-V5.md), [source-ordered original-test manifest](oracle/cpython-3.14.6/manifest-v5.json), and [read-only original-test and reference verifier](tools/verify_original_cpython_accounting_v1.py); all **165** original methods, **152** public methods, and the only **13** named private waivers are preserved.
- [Separately frozen Python-only reference protocol](oracle/cpython-3.14.6/PUBLIC-CONTRACT-BASELINES-V1.md) and [failure-preserving public, scanner, and buffer reference recorder](tools/record_independent_public_contract_baselines_v1.py); the independent **864**, **1,024**, and **768**-case two-Python reference runs are **NOT RUN**, and new candidate results are **NOT MEASURED**.
- [Separately frozen 6,912-case Python public types, copying, identity, and serialization compatibility checks](tools/independent_public_type_identity_serialization_v1.py), [lossless, failure-preserving public-type evidence recorder](tools/record_independent_public_type_identity_serialization_v1.py), [complete matching two-Python public-type reference](experiments/rust_public_practice_v1/public-type-identity-serialization-v1-shared-suite-v1.json.gz), and [authenticated public-type reference receipt](experiments/rust_public_practice_v1/public-type-identity-serialization-v1-shared-suite-v1-publication-receipt.json); all candidate results **NOT MEASURED**.
- [Separately frozen 2,854-case scanner and pattern-comment compatibility checks](tools/independent_scanner_verbose_comments_v1.py), [complete baseline and candidate evidence recorder](tools/record_independent_scanner_verbose_comments_v1.py), [losslessly preserved two-Python scanner baseline](experiments/rust_public_practice_v1/scanner-verbose-comments-v1-shared-suite-v1.json.gz), [authenticated scanner graph inputs](docs/evidence/scanner-verbose-overview-v1.inputs.json), [generated scanner graph data](docs/evidence/scanner-verbose-overview-v1.json), and [independently frozen scanner graph generator](tools/render_scanner_verbose_overview_v1.py).
- [Corrected, separately frozen 5,120-case replacement and buffer compatibility checks](tools/independent_substitution_buffer_semantics_v2.py), [lossless, independently guarded replacement evidence recorder](tools/record_independent_substitution_buffer_semantics_v3.py), [complete matching two-Python reference](experiments/rust_public_practice_v1/substitution-buffer-semantics-v2-shared-suite-v2.json.gz), [authenticated replacement reference receipt](experiments/rust_public_practice_v1/substitution-buffer-semantics-v2-shared-suite-v2-publication-receipt.json), [independently frozen corrected graph inputs](docs/evidence/substitution-buffer-overview-v2.inputs.json), [generated corrected graph data](docs/evidence/substitution-buffer-overview-v2.json), and [corrected replacement comparison graph generator](tools/render_substitution_buffer_overview_v2.py); all three candidate results **NOT MEASURED**.
- [Independent, read-only verification of the preserved replacement and changing-buffer test-harness errors](tools/verify_independent_callback_oracle_falsification_v1.py) and [complete authenticated historical-error proof](docs/evidence/callback-oracle-falsification-v1.json).
- [Frozen 128-case simultaneous Python interpreter compatibility protocol](oracle/cpython-3.14.6/PUBLIC-SUBINTERPRETER-V2.md), [failure-preserving isolated-interpreter oracle](tools/python_re_subinterpreter_oracle_v2.py), [complete passing two-Python V2 reference](oracle/cpython-3.14.6/evidence/public-subinterpreter-v2-self-oracle.json.gz), [authenticated V2 reference receipt](oracle/cpython-3.14.6/evidence/public-subinterpreter-v2-self-oracle-publication-receipt.json), [preserved original passing reference](oracle/cpython-3.14.6/evidence/public-subinterpreter-v1-self-oracle.json), and [authenticated original receipt](oracle/cpython-3.14.6/evidence/public-subinterpreter-v1-self-oracle-publication-receipt.json); all three candidate results **NOT MEASURED**.
- [Frozen 264-case Python buffer-exporter and retained-scanner protocol](oracle/cpython-3.14.6/PUBLIC-BUFFER-EXPORTER-V4.md), [failure-preserving PEP 688 compatibility oracle](tools/python_re_buffer_exporter_oracle_v4.py), [complete matching two-Python reference](oracle/cpython-3.14.6/evidence/public-buffer-exporter-v4-self-oracle.json.gz), and [authenticated reference publication receipt](oracle/cpython-3.14.6/evidence/public-buffer-exporter-v4-self-oracle-publication-receipt.json); all candidate results **NOT MEASURED**.
- [Falsified original 5,120-case replacement and buffer test](tools/independent_substitution_buffer_semantics_v1.py), [preserved first evidence recorder](tools/record_independent_substitution_buffer_semantics_v1.py), [complete recorded first failure](experiments/rust_public_practice_v1/substitution-buffer-semantics-v1-shared-suite-v1-controller-failure-v1.json), [lossless, bounded historical baseline and candidate recorder](tools/record_independent_substitution_buffer_semantics_v2.py), [complete historical two-Python reference](experiments/rust_public_practice_v1/substitution-buffer-semantics-v1-shared-suite-v1.json.gz), [historical reference receipt](experiments/rust_public_practice_v1/substitution-buffer-semantics-v1-shared-suite-v1-publication-receipt.json), [preserved C report including the 128 test-harness errors](experiments/rust_public_practice_v1/c-substitution-buffer-semantics-v1-native-lifetime-repair-v1.json.gz), [authenticated C report receipt](experiments/rust_public_practice_v1/c-substitution-buffer-semantics-v1-native-lifetime-repair-v1-publication-receipt.json), [preserved Zig report including the same 128 test-harness errors](experiments/rust_public_practice_v1/zig-substitution-buffer-semantics-v1-owned-safe-buffer-repair-v1.json.gz), [authenticated Zig report receipt](experiments/rust_public_practice_v1/zig-substitution-buffer-semantics-v1-owned-safe-buffer-repair-v1-publication-receipt.json), and [preserved, not-yet-published historical replacement graph generator](tools/render_substitution_buffer_overview_v1.py).
- [Corrected, separately frozen 10,240-case changing-buffer compatibility checks](tools/independent_shape_changing_buffer_semantics_v2.py), [lossless, safely bounded changing-buffer evidence recorder](tools/record_independent_shape_changing_buffer_semantics_v2.py), [complete matching two-Python changing-buffer reference](experiments/rust_public_practice_v1/shape-changing-buffer-semantics-v2-shared-suite-v2.json.gz), and [authenticated changing-buffer reference receipt](experiments/rust_public_practice_v1/shape-changing-buffer-semantics-v2-shared-suite-v2-publication-receipt.json); all three candidate results **NOT MEASURED**.
- [Falsified original 10,240-case changing-size buffer test](tools/independent_shape_changing_buffer_semantics_v1.py), [complete historical changing-buffer evidence recorder](tools/record_independent_shape_changing_buffer_semantics_v1.py), [preserved two-Python historical reference](experiments/rust_public_practice_v1/shape-changing-buffer-semantics-v1-shared-suite-v1.json.gz), [authenticated historical reference receipt](experiments/rust_public_practice_v1/shape-changing-buffer-semantics-v1-shared-suite-v1-publication-receipt.json), [preserved inconclusive first C process-ID collision](experiments/rust_public_practice_v1/c-shape-changing-buffer-semantics-v1-native-lifetime-repair-v1.json.gz), [authenticated C collision receipt](experiments/rust_public_practice_v1/c-shape-changing-buffer-semantics-v1-native-lifetime-repair-v1-publication-receipt.json), [preserved C report including 496 test-harness errors](experiments/rust_public_practice_v1/c-shape-changing-buffer-semantics-v1-native-lifetime-repair-pid-retry-v1.json.gz), [authenticated C report receipt](experiments/rust_public_practice_v1/c-shape-changing-buffer-semantics-v1-native-lifetime-repair-pid-retry-v1-publication-receipt.json), [historical changing-buffer graph inputs](docs/evidence/shape-changing-buffer-overview-v1.inputs.json), [preserved historical graph data](docs/evidence/shape-changing-buffer-overview-v1.json), and [preserved historical graph generator](tools/render_shape_changing_buffer_overview_v1.py).
- [Current independent from-scratch engine ownership checks](tools/independent_from_scratch_audit_v3.py), [durable no-delegation audit recorder](tools/record_independent_from_scratch_audit_v3.py), [actual independently verified Rust engine audit](experiments/rust_public_practice_v1/rust-from-scratch-audit-v3-owned-buffer-repair-v1.json), [durable Rust audit receipt](experiments/rust_public_practice_v1/rust-from-scratch-audit-v3-owned-buffer-repair-v1-publication-receipt.json), [actual independently verified C engine audit](experiments/rust_public_practice_v1/c-from-scratch-audit-v3-native-lifetime-repair-v1.json), [durable C audit receipt](experiments/rust_public_practice_v1/c-from-scratch-audit-v3-native-lifetime-repair-v1-publication-receipt.json), [actual independently verified Zig engine audit](experiments/rust_public_practice_v1/zig-from-scratch-audit-v3-owned-safe-buffer-repair-v1.json), [durable Zig audit receipt](experiments/rust_public_practice_v1/zig-from-scratch-audit-v3-owned-safe-buffer-repair-v1-publication-receipt.json), and [preserved earlier ownership rules](tools/independent_from_scratch_audit_v2.py).
- [Additional frozen memory-lifetime safety checks](tools/independent_managed_buffer_lifetime_v1.py), [complete baseline recorder](tools/record_independent_managed_buffer_lifetime_v1.py), [independent three-candidate recorder](tools/record_independent_managed_buffer_candidates_v1.py), [verified lossless baseline evidence](docs/evidence/managed-buffer-lifetime-baseline-v1.archive.json), [safe report restoration](tools/restore_managed_buffer_lifetime_baseline_v1.py), [authenticated memory-safety graph inputs](docs/evidence/managed-buffer-lifetime-overview-v1.inputs.json), [generated memory-safety graph data](docs/evidence/managed-buffer-lifetime-overview-v1.json), [original memory-safety graph generator](tools/render_managed_buffer_lifetime_overview_v1.py), and [safe two-file graph updater](tools/render_managed_buffer_lifetime_overview_v2.py).
- [Reproducible, source-pinned Zig build controller](tools/reproduce_owned_zig_source_build_v4.py).
- [Proposed expanded final-comparison protocol](docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md).
- [Original objective](GOAL.md), SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`; [later clarifications](AMENDMENTS.md).

Verify the frozen test and chart tools without opening the final comparison:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

"$PY" -I -B tools/independent_original_cpython_suite_v5.py --self-test
"$PY" -I -B tools/independent_public_contract_v3.py --self-test
"$PY" -I -B tools/record_independent_public_contract_baselines_v1.py --self-test
"$PY" -I -B tools/independent_public_type_identity_serialization_v1.py --self-test
"$PY" -I -B tools/record_independent_public_type_identity_serialization_v1.py --self-test
"$PY" -I -B tools/record_independent_public_contract_v3.py --self-test
"$PY" -I -B tools/independent_scanner_verbose_comments_v1.py --self-test
"$PY" -I -B tools/record_independent_scanner_verbose_comments_v1.py --self-test
"$PY" -I -B tools/render_scanner_verbose_overview_v1.py --self-test
"$PY" -I -B tools/independent_substitution_buffer_semantics_v1.py --self-test
"$PY" -I -B tools/independent_substitution_buffer_semantics_v2.py --self-test
"$PY" -I -B tools/record_independent_substitution_buffer_semantics_v1.py --self-test
"$PY" -I -B tools/record_independent_substitution_buffer_semantics_v2.py --self-test
"$PY" -I -B tools/record_independent_substitution_buffer_semantics_v3.py --self-test
"$PY" -I -B tools/render_substitution_buffer_overview_v1.py --self-test
"$PY" -I -B tools/render_substitution_buffer_overview_v2.py --self-test
"$PY" -I -B tools/verify_independent_callback_oracle_falsification_v1.py --self-test
"$PY" -I -B tools/independent_shape_changing_buffer_semantics_v1.py --self-test
"$PY" -I -B tools/independent_shape_changing_buffer_semantics_v2.py --self-test
"$PY" -I -B tools/record_independent_shape_changing_buffer_semantics_v1.py --self-test
"$PY" -I -B tools/record_independent_shape_changing_buffer_semantics_v2.py --self-test
"$PY" -I -B tools/render_shape_changing_buffer_overview_v1.py --self-test
"$PY" -I -B tools/python_re_subinterpreter_oracle_v2.py --self-test
"$PY" -I -B tools/python_re_buffer_exporter_oracle_v4.py --self-test
"$PY" -I -B tools/independent_from_scratch_audit_v3.py --self-test
"$PY" -I -B tools/record_independent_from_scratch_audit_v3.py --self-test
"$PY" -I -B tools/independent_from_scratch_audit_v2.py --self-test
"$PY" -I -B tools/independent_managed_buffer_lifetime_v1.py --self-test
"$PY" -I -B tools/record_independent_managed_buffer_lifetime_v1.py --self-test
"$PY" -I -B tools/record_independent_managed_buffer_candidates_v1.py --self-test
"$PY" -I -B tools/restore_managed_buffer_lifetime_baseline_v1.py --self-test
"$PY" -I -B tools/render_managed_buffer_lifetime_overview_v1.py --self-test
"$PY" -I -B tools/render_managed_buffer_lifetime_overview_v2.py --self-test
"$PY" -I -B tools/reproduce_owned_zig_source_build_v4.py --self-test
"$PY" -I -B tools/render_candidate_correctness_overview_v2.py --self-test
```
