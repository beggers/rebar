# rebar: a faster Python `re` experiment

Build a faster, fully compatible replacement for Python 3.14.6's
regular-expression module:

```python
import rebar as re
```

Every candidate must use its own matching engine built from scratch. Wrapping
Python, another regular-expression package, or another candidate does not count.

## Headline results

Python passes all **31,237** frozen compatibility checks. No replacement
has yet passed them. Rust, C, and Zig now each have two independently
matching, from-scratch builds. Rust passes **7,461** verified cases in
eight groups; C passes **7,197** in seven; Zig passes **3,583** in six.
All three still fail the complete Python compatibility standard. Zig's
full run records **1,764** actual behavior differences; its separate
interpreter-cleanup failure is not counted as a matching difference.
The run also exposed an interpreter-report bug in the earlier test
harness; the corrected full test preserves that failure.
Its original failed source build is preserved alongside the corrected build.
C++ also has two matching, independently built native outputs, but its
Python compatibility has **NOT BEEN TESTED**. Go's original source
build failed; its separately isolated engine now compiles, but the
Python bridge fails because `SSIZE_MAX` is unavailable. Both actual
failures are preserved.
Fortran's second independent build experiment again compiles both
engines and both Python bridges. The bridges match, but the engine
files still differ, so the reproducibility check fails.
A narrowly targeted Go and Fortran build correction is frozen but has
**NOT BEEN RUN**.
All six candidate source trees pass the independently frozen
first-party ownership audit; this does not qualify their behavior.
Every replacement's speed is **NOT MEASURED**; the final comparison
remains **NOT OPENED**.

![Python passes all 31,237 checks; Rust passes 7,461, C passes 7,197, and Zig passes 3,583 but all fail complete compatibility; C++ builds but is not tested, Go's engine builds but its bridge fails, both Fortran attempts produce different engine files, and speed is not measured](docs/evidence/candidate-current-overview-v13.svg)

| Engine | Current build | Complete compatibility | Speed against Python |
| --- | --- | --- | --- |
| Python `re` | Reference | 31,237 / 31,237 | Reference; not timed |
| Rust | Two matching builds | 7,461 verified; five groups failed; not qualified | NOT MEASURED |
| C | Two matching builds | 7,197 verified; six groups failed; not qualified | NOT MEASURED |
| Zig | Two matching builds; original failure preserved | 3,583 verified; seven groups failed; not qualified | NOT MEASURED |
| C++ | Two matching source builds | NOT MEASURED | NOT MEASURED |
| Go | Engine builds; Python bridge fails | NOT MEASURED | NOT MEASURED |
| Fortran | Two attempts; engines differ | NOT MEASURED | NOT MEASURED |

Historical graphs below describe earlier binaries. They do not qualify
the current implementations. The complete history and rejected
experiments are preserved in the [experiment log](docs/EXPERIMENT-LOG.md).

## Detailed compatibility

| Python behavior | Cases | Rust | C | Zig |
| --- | ---: | ---: | ---: | ---: |
| Python's original runnable public tests | 151 | 151 | 151 | 151 |
| General public behavior | 864 | 864 | 864 | 864 |
| Scanners and callbacks | 1,024 | 1,024 | 1,024 | 960; 64 failures |
| Memory views and buffers | 768 | 768 | 768 | 768 |
| Total initial matching checks | 2,807 | 2,807 | 2,807 | 2,743; 64 failures |
| Additional memory-lifetime safety, counted separately | 1,024 | 1,024 | 1,024 | 1,024 |
| Verbose scanners and pattern comments | 2,854 | 2,854 | 2,854 | 2,234; 620 failures |
| Additional public types, copying, and serialization | 6,912 | 248 failures | 248 failures | 248 failures |
| Replacement and buffer behavior | 5,120 | 336 failures | 336 failures | 64 failures |
| Changing-size buffer behavior | 10,240 | 1,392 failures | 1,392 failures | 672 failures |
| Broad public behavior and real locales | 1,376 | 66 failures | 114 failures | 96 failures |
| Python buffer exporters and retained scanners | 264 | 264 | 4 failures | 264 |
| Simultaneous isolated Python interpreters | 128 | Setup failed; matching not established | Setup failed; no cases verified | Cleanup and report verification failed; no complete suite |
| Patterns shared across simultaneous Python threads | 512 | 512 | 512 | 512 |
| Full frozen compatibility gate | 31,237 | Failed; 7,461 verified; five groups failed | Failed; 7,197 verified; six groups failed | Failed; 3,583 verified; seven groups failed |

Python's genuine debug-only test is skipped equally and is not included in the denominator.
Passing examples inside a failed group do not qualify that group or the replacement.
Zig's interpreter worker completed **385** matching calls before failing to
restore the original Python matcher; this cleanup failure is preserved but
is not counted as a regex mismatch. The outer test runner also rejects the
interpreter report because the two recorders name its verified file-sync
field differently. Both failures are recorded separately.

![Historical starting checks: earlier Python, Rust, C, and Zig binaries each pass 2,807 starting cases; these are not results for the current candidate sources](docs/evidence/candidate-correctness-overview-v2.svg)

![Historical replacement checks recorded before the current C run; this earlier graph does not contain the newly recorded 336 C replacement failures](docs/evidence/substitution-buffer-overview-v2.svg)

![Historical scanner checks: Python passes all 2,854; earlier Rust and C each fail 116, and earlier Zig fails 1,364](docs/evidence/scanner-verbose-overview-v1.svg)

![Historical memory-safety checks: earlier Python, Rust, C, and Zig binaries each pass 1,024 cases; these are not results for the current candidate sources](docs/evidence/managed-buffer-lifetime-overview-v1.svg)

![Detailed public correctness: Python and the Rust engine match on all 864 public examples](docs/evidence/rust-public-correctness-v1.svg)

![Falsified historical changing-buffer report: its 1,888 recorded C differences include 496 test-harness errors](docs/evidence/shape-changing-buffer-overview-v1.svg)

This historical graph contains a known test-harness error; its red bar is
**NOT QUALIFIED**. Complete failures, corrections, and raw reports remain in
the [experiment log](docs/EXPERIMENT-LOG.md).

## Detailed development speed

![Historical speed before the latest compatibility repairs: Python at 1.000 times, old Rust at 1.065 times, and the 1.5-times target](docs/evidence/rust-public-speed-v2-overall.svg)

![Results for all 864 public examples: 183 clearly faster, 213 clearly slower, and 468 inconclusive](docs/evidence/rust-public-speed-v2-outcomes.svg)

![Rust development speed for each of the 36 measured operations, including operations that are slower than Python](docs/evidence/rust-public-speed-v2-operations.svg)

![Measured slowdowns greater than 20 percent: zero among all 864 public development examples](docs/evidence/rust-public-speed-v2-regressions.svg)

These graphs measure an earlier Rust development build, not a current
candidate. Among all **864** historical cases, **183** were faster, **213**
were slower, and **468** were inconclusive. Current speed and memory remain
**NOT MEASURED**.

## Final comparison

The proposed final comparison will use **4,194,304** unseen examples and
**24** balanced measurement rounds. It will cover ordinary and unusual
patterns, text and bytes, compilation, repeated use, native-code overhead,
and memory.

Those final examples are **NOT FROZEN**, **NOT GENERATED**, and
**NOT OPENED**. Three independently built candidates must first pass every
compatibility and ownership check. Success requires at least **1.5×**
overall speedup, statistically faster results on at least **60%** of cases,
and an explanation of every slowdown greater than **20%**. There is no winner.

## Evidence and reproduction

- [Complete 31,237-check compatibility standard](oracle/phase1/P0-COMPLETENESS-V1.md), [machine-readable test inventory](oracle/phase1/p0-completeness-v1.json), and [independent fail-closed verifier](tools/verify_p0_completeness_v1.py).
- [Original Python compatibility tests for all six first-party engines](oracle/phase2/SIX-FAMILY-P0-PRODUCER-V1.md), [frozen six-language test inventory](oracle/phase2/six-family-p0-producer-v1.json), and [independently verified six-language test runner](tools/run_owned_six_family_original_p0_producer_v1.py); preserves all **31,237** original cases, real buffer, thread, and interpreter behavior, six separate matching engines, and all **61** evidence files without claiming an untested engine has passed.
- [Corrected complete candidate standard](oracle/phase2/P0-CANDIDATE-PROTOCOL-V7.md), [frozen 31,237-case candidate inventory](oracle/phase2/p0-candidate-protocol-v7.json), [independently verified full-test worker](tools/run_frozen_p0_candidate_worker_v5.py), and [complete candidate runner](tools/run_frozen_p0_candidate_v7.py); all **13** original suites, all **57** evidence records, the real Zig interpreter failure, and every candidate mismatch remain unchanged.
- [Preserved earlier complete candidate standard](oracle/phase2/P0-CANDIDATE-PROTOCOL-V6.md), [original inventory](oracle/phase2/p0-candidate-protocol-v6.json), and [earlier candidate runner](tools/run_frozen_p0_candidate_v6.py); its original Zig failure and discovered interpreter-report defect remain available.
- Complete actual compatibility failures for [C](oracle/phase2/evidence/frozen-p0-candidate-v5-c-phase2-v5-failures.json.gz), [Rust](oracle/phase2/evidence/frozen-p0-candidate-v5-rust-phase2-v5-failures.json.gz), and [Zig](oracle/phase2/evidence/frozen-p0-candidate-v6-zig-phase2-v6-failures.json.gz); the [experiment log](docs/EXPERIMENT-LOG.md) links every independent worker report, publication receipt, failure, and restoration.
- [Actual isolated-interpreter Zig failure](oracle/phase2/evidence/owned-candidate-subinterpreters-v3-zig-phase2-v6-subinterpreters-failures.json.gz) and [independent failure receipt](oracle/phase2/evidence/owned-candidate-subinterpreters-v3-zig-phase2-v6-subinterpreters-failures-publication-receipt.json); 385 genuine matching calls precede cleanup failure.
- [Complete reproducible C++ source-build report](oracle/phase2/evidence/native-source-build-v4-cpp-phase2-v4.json.gz) and [independent C++ publication receipt](oracle/phase2/evidence/native-source-build-v4-cpp-phase2-v4-publication-receipt.json); two fresh source builds produce the same native library, without running a candidate or claiming Python compatibility.
- [Complete first Go source-build failure](oracle/phase2/evidence/native-source-build-v4-go-phase2-v4-failures.json.gz) and [verified Go failure publication receipt](oracle/phase2/evidence/native-source-build-v4-go-phase2-v4-failures-publication-receipt.json); the real Go compiler accidentally includes the Python bridge in the Go engine and fails before building a native library or running a compatibility check.
- [Complete isolated-Go source-build failure](oracle/phase2/evidence/native-source-build-v5-go-phase2-v5-failures.json.gz) and [verified isolated-Go failure receipt](oracle/phase2/evidence/native-source-build-v5-go-phase2-v5-failures-publication-receipt.json); the genuinely isolated Go engine compiles but the separate Python bridge fails on the original `SSIZE_MAX` compiler error.
- [Original Fortran reproducibility failure](oracle/phase2/evidence/native-source-build-v4-fortran-phase2-v4-failures.json.gz) and [verified original Fortran failure receipt](oracle/phase2/evidence/native-source-build-v4-fortran-phase2-v4-failures-publication-receipt.json); both independent engine and bridge builds compile, but the two Fortran engine files differ.
- [Independently repeated Fortran reproducibility failure](oracle/phase2/evidence/native-source-build-v5-fortran-phase2-v5-failures.json.gz) and [verified repeated Fortran failure receipt](oracle/phase2/evidence/native-source-build-v5-fortran-phase2-v5-failures-publication-receipt.json); all **26** compiler and binary-inspection processes succeed and both bridges match, but the engine files and their recorded build identifiers still differ.
- [Frozen first-party Go and Fortran build corrections](oracle/phase2/NATIVE-SOURCE-BUILD-V6.md), [exact correction and source inventory](oracle/phase2/native-source-build-v6.json), and [independently verified build recorder](tools/reproduce_owned_native_source_build_v6.py); tests precisely the actual Go bridge error and the observed differing Fortran build identifiers, without claiming either corrected build has run.
- [Corrected from-scratch build rules for all six languages](oracle/phase2/NATIVE-SOURCE-BUILD-V5.md), [exact source and compiler inventory](oracle/phase2/native-source-build-v5.json), and [independent source-build recorder](tools/reproduce_owned_native_source_build_v5.py); preserves the real isolated-Go bridge failure and the independently repeated Fortran reproducibility failure without claiming either candidate is compatible.
- [Preserved original six-language build rules](oracle/phase2/NATIVE-SOURCE-BUILD-V4.md), [original frozen inventory](oracle/phase2/native-source-build-v4.json), and [original source-build recorder](tools/reproduce_owned_native_source_build_v4.py); retains the actual C++, Go, and Fortran build outcomes unchanged.
- [Reversible six-engine native-loading rules](oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V3.md), [frozen source and recovery inventory](oracle/phase2/verified-native-activation-v3.json), and [verified native activation and crash recovery](tools/activate_verified_native_candidate_v3.py); only a genuinely reproducible, independently source-built engine may be loaded, and no candidate is claimed to have been run.
- [Six-engine first-party ownership and no-wrapping standard](oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md), [complete source and dependency inventory](oracle/phase2/candidate-independence-v2.json), and [independent six-language ownership audit](tools/audit_candidate_independence_v2.py); verifies all 25 engine sources, both project dependency files, and all 34 actual C and Rust failure artifacts without claiming that a source audit proves correctness.
- [Current source-pinned headline graph inputs](docs/evidence/candidate-current-overview-v13.inputs.json), [complete current graph summary](docs/evidence/candidate-current-overview-v13.json), and [reproducible current-results graph generator](tools/render_candidate_current_overview_v13.py); the graph independently authenticates all six engine designs, the C/Rust/Zig compatibility results, C++'s reproducible build, both actual Go failures, both actual Fortran failures, and all **61** preserved evidence files.
- [Complete experiment log, raw evidence, rejected approaches, and preserved failures](docs/EXPERIMENT-LOG.md).
- [Proposed expanded final comparison](docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md); the final cases remain **NOT GENERATED** and **NOT OPENED**.
- [Original objective](GOAL.md), SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`; [later clarifications](AMENDMENTS.md).

Run the source-only safety checks without opening the final comparison:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

"$PY" -I -B tools/verify_p0_completeness_v1.py --self-test
"$PY" -I -B tools/run_frozen_p0_candidate_worker_v4.py --self-test
"$PY" -I -B tools/run_frozen_p0_candidate_v6.py --self-test
"$PY" -I -B tools/run_frozen_p0_candidate_worker_v5.py --self-test
"$PY" -I -B tools/run_frozen_p0_candidate_v7.py --self-test
"$PY" -I -B tools/run_owned_six_family_original_p0_producer_v1.py --self-test
"$PY" -I -B tools/run_owned_candidate_subinterpreters_v3.py --self-test
"$PY" -I -B tools/reproduce_owned_native_source_build_v4.py --self-test
"$PY" -I -B tools/reproduce_owned_native_source_build_v4.py --verify-context
"$PY" -I -B tools/reproduce_owned_native_source_build_v5.py --self-test
"$PY" -I -B tools/reproduce_owned_native_source_build_v5.py --verify-context
"$PY" -I -B tools/reproduce_owned_native_source_build_v6.py --self-test
"$PY" -I -B tools/reproduce_owned_native_source_build_v6.py --verify-context
"$PY" -I -B tools/activate_verified_native_candidate_v2.py --self-test
"$PY" -I -B tools/activate_verified_native_candidate_v3.py --self-test
"$PY" -I -B tools/activate_verified_native_candidate_v3.py --verify-frozen-context
"$PY" -I -B tools/audit_candidate_independence_v2.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v13.py --self-test
```

Verify the current headline graph without rerunning a candidate or
opening a benchmark:

```sh
"$PY" -I -B tools/run_frozen_p0_candidate_v7.py --verify-frozen-context \
  --source-sha256 08ab73a0d42a2bb3bb658cf6924786a7ba396aacd229957a710866572e178690 \
  --worker-source-sha256 66f869e71e1aaf77944f4b7115e91ab34f6bc9b06fb4d17f097ea26c97c9c780 \
  --protocol-sha256 ed595cbb3d5f040454da7efff3d8330befb09dda2ac6eebc681b630b96f32733 \
  --document-sha256 16f24a46113e0a120fc5cf7fea2122d78e76445665959a9553b610a27b8843b1

"$PY" -I -B tools/run_owned_six_family_original_p0_producer_v1.py \
  --verify-frozen-context \
  --source-sha256 36451c10221857cca8c77fad7533382f4e3969a20a5cdf73c055beea1d315d33 \
  --protocol-sha256 1e7ed2cbd63e080c563dd49b4ea2a2be284d831d75739c47edecfae50373ce17 \
  --document-sha256 5206bcc097cd399cddd91a8d0356fd780b44ef7c173d70605d28a175dac71c0b

"$PY" -I -B tools/render_candidate_current_overview_v13.py --verify \
  --source-sha256 427a68b34e34aa203bc695a93f887ed7b4daa89bdb3d4aa00e4c92e8429e3922 \
  --go-bridge-sha256 52101f0afe29a568e3c2e22a06d47c89c051e08a0e2024ad4891c5ae2d60fb6a \
  --manifest-sha256 577d27a0b88f623b7cc14f909da9a360946474563d916cd9a558a4352cd68dd2
```

The [complete compatibility standard](oracle/phase1/P0-COMPLETENESS-V1.md)
contains the source-pinned, read-only full-verification command.
