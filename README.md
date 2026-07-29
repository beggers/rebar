# rebar: a faster Python `re` experiment

Build a faster, fully compatible, from-scratch replacement for
[Python 3.14.6](https://www.python.org/downloads/release/python-3146/)'s
regular-expression module:

```python
import rebar as re
```

Each engine must be independently written. Wrapping Python, an external
regular-expression package, or another candidate does not count.

## Results

**Six** from-scratch engines. **Zero** fully compatible replacements.
Speed versus Python: **NOT MEASURED**. There is no winner.

The newest Zig run passed **4,607** of the original Python checks and
revealed at least **1,700** differences. The chart below is the previous
published snapshot; its replacement is being generated from the newly
preserved results.

![Python compared with six independently written regular-expression engines. C passes 13,094 checks, Rust 15,749, and Zig 3,583; none passes all 31,237 compatibility checks, and speed has not been measured.](docs/evidence/candidate-current-overview-v91.svg)

Every engine is compared against the same **31,237** Python checks.
Passing some checks does not mean an engine can replace Python `re`.

| Engine | Compatibility with Python | Speed versus Python |
| --- | --- | --- |
| Python `re` | Baseline; reference checks pass | Not timed |
| Public `rebar` import | FAIL; still selects an unqualified Zig prototype | NOT MEASURED |
| Rust | FAIL; 12/13 groups completed; 15,749 passed; at least 1,296 differences | NOT MEASURED |
| C | FAIL; 5/13 groups completed; 13,094 passed; at least 236 differences | NOT MEASURED |
| Zig | FAIL; 12/13 groups completed; 4,607 passed; at least 1,700 differences | NOT MEASURED |
| C++ | FAIL; 2,308 differences and five worker failures | NOT MEASURED |
| Go | FAIL; 4,518 differences and four worker failures | NOT MEASURED |
| Fortran | FAIL; independent builds disagree; matching not tested | NOT MEASURED |

The frozen original Python suite contains **31,237** checks in **13**
groups. A separate **8,244**-case collection covers additional real-world
behavior; two independent Python reference runs each pass all **8,244**.
These are separate test sets and are never combined or counted twice.

C, Rust, and Zig were built independently from project-owned source.
Building an engine or passing some checks does not prove full Python
compatibility. Complete mismatch totals are **NOT MEASURED** while
test groups remain incomplete; runtime independence is
**NOT ESTABLISHED**.

## Detailed correctness

These historical charts show particular compatibility checks; none claims
a passing replacement or a speed measurement.

![Earlier replacement and changing-buffer compatibility checks](docs/evidence/substitution-buffer-overview-v2.svg)

![Earlier scanner compatibility checks against Python](docs/evidence/scanner-verbose-overview-v1.svg)

![Earlier memory-lifetime compatibility checks against Python](docs/evidence/managed-buffer-lifetime-overview-v1.svg)

## Final speed comparison

The latest proposed final test covers **14,155,776** unseen cases across
**36** Python operations, **24** kinds of regular expressions, and both
text and byte-oriented inputs. All four participants would run every case
in **24** balanced rounds. The earlier **4,194,304**-case proposal is
preserved.

The larger test is **NOT FROZEN**, **NOT GENERATED**, and **NOT OPENED**.
Speed, memory, and statistical confidence are **NOT MEASURED**.

Do not start this test until three independent engines pass both test
sets, the original two-billion-character checks, public API checks,
and the no-delegation audit. A winner must be at least **1.5×** faster
overall, faster on at least **60%** of measured cases, and explain every
slowdown over **20%**.

## Evidence

- [Reproduce the current chart](docs/REPRODUCING.md) and inspect its [independently verified headline renderer](tools/render_candidate_current_overview_v91.py).
- [Full experiment log, build evidence, failures, and rejected designs](docs/EXPERIMENT-LOG.md).
- [Complete Python correctness reference](oracle/phase1/P0-COMPLETENESS-V4.md).
- [Independent reference for the 8,244 additional checks](oracle/phase1/P0-DIFFERENTIAL-FUZZ-REFERENCE-V3.md).
- [Six independently written engine families](oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md) and [no-wrapping audit](oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md).
- [Frozen first-party C correctness procedure](oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V8.md), [latest actual C test results](oracle/phase2/evidence/repaired-c-original-campaign-v7-c-phase2-v18-c-subject-buffer-root-provenance-original-p0-v7-failures-publication-receipt.json), [first-party match-object correction](oracle/phase2/C-ORIGINAL-MATCH-SEMANTICS-V1.md), preserved [native-identity](oracle/phase2/evidence/c-original-match-semantics-source-build-v19-preactivation-failure.json) and [secure-randomness](oracle/phase2/evidence/c-original-match-semantics-source-build-v20-preactivation-failure.json) failures, and the [corrected from-scratch C build](oracle/phase2/C-ORIGINAL-MATCH-SEMANTICS-SOURCE-BUILD-V21.md), independently reproduced as [two matching native builds](oracle/phase2/evidence/native-source-build-v21-c-phase2-v21-c-original-match-semantics-publication-receipt.json) with [separately verified build provenance](oracle/phase2/evidence/native-source-build-v21-c-phase2-v21-c-original-match-semantics-root-provenance-receipt.json). Building successfully does not mean the corrected C engine has passed its compatibility tests.
- [Frozen first-party Zig correctness procedure](oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V12.md), [latest actual Zig test results](oracle/phase2/evidence/repaired-zig-original-campaign-v12-phase2-v13-zig-guard-clean-v1-original-p0-v12-failures-publication-receipt.json), and [preserved previous Zig results](oracle/phase2/evidence/repaired-zig-original-campaign-v10-phase2-v13-zig-guard-clean-v1-original-p0-v10-failures-publication-receipt.json). The latest run attempted all 13 test groups; its genuine failures are preserved.
- [First-party Rust correctness procedure](oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V20.md), [latest complete Rust test results](oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v21-rust-captured-findall-root-provenance-original-p0-v20-failures-publication-receipt.json), [preserved previous Rust results](oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v21-rust-captured-findall-root-provenance-original-p0-v19-failures-publication-receipt.json), [first-party substitution and buffer correction](oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V1.md), its [dependency-free native build](oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-SOURCE-BUILD-V22.md), and the actual [offline build](oracle/phase2/evidence/native-source-build-v22-rust-phase2-v22-rust-capture-shape-root-provenance-publication-receipt.json) and [independent source-phase receipts](oracle/phase2/evidence/native-source-build-v22-rust-phase2-v22-rust-capture-shape-root-provenance-root-provenance-receipt.json). The corrected Rust engine is built but has not passed its compatibility tests.
- [From-scratch Rust literal-search](oracle/phase2/RUST-LITERAL-FINDALL-ONE-PASS-V1.md), [captured-result experiments](oracle/phase2/RUST-CAPTURED-FINDALL-ONE-PASS-V1.md), and [exact Python scanner signatures](oracle/phase2/RUST-SCANNER-SIGNATURE-SOURCE-REPAIR-V22.md), with reproduced [literal](oracle/phase2/RUST-LITERAL-FINDALL-SOURCE-BUILD-V20.md) and [captured-result](oracle/phase2/RUST-CAPTURED-FINDALL-SOURCE-BUILD-V21.md) native builds; the scanner repair is not built, and full compatibility and speed are not established.
- [Larger, unopened 14,155,776-case speed-test proposal](oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md) and [preserved earlier proposal](docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md).
- [Original objective](GOAL.md), SHA-256
  `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`;
  [later clarifications](AMENDMENTS.md).
