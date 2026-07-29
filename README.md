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

![Python baseline compared with six independently written regular-expression engines. C and Rust build successfully; none passes every compatibility test, no relative speed has been measured, and the 14-million-case final comparison remains unopened.](docs/evidence/candidate-current-overview-v88.svg)

The chart precedes the latest C and Zig tests and Rust preflight;
current results are below.

| Engine | Compatibility with Python | Speed versus Python |
| --- | --- | --- |
| Python `re` | Baseline; reference checks pass | Not timed |
| Public `rebar` import | FAIL; still selects an unqualified Zig prototype | NOT MEASURED |
| Rust | FAIL; 8/13 groups completed; 12,942 passed; at least 1,296 differences | NOT MEASURED |
| C | FAIL; 5/13 groups completed; 13,094 passed; at least 236 differences | NOT MEASURED |
| Zig | FAIL; 3/13 groups completed; 927 passed; 10 worker failures | NOT MEASURED |
| C++ | FAIL; 2,308 differences and five worker failures | NOT MEASURED |
| Go | FAIL; 4,518 differences and four worker failures | NOT MEASURED |
| Fortran | FAIL; independent builds disagree; matching not tested | NOT MEASURED |

The frozen original Python suite contains **31,237** checks in **13**
groups. A separate **8,244**-case collection covers additional real-world
behavior; two independent Python reference runs each pass all **8,244**.
These are separate test sets and are never combined or counted twice.

First-party native source builds recorded **14** C, **28** Rust, and
**26** Zig compiler and binary-inspection steps. The corrected C engine
and both the literal-search and captured-result Rust engines each
passed their own two independent build phases. No successful build
proves compatibility.
The corrected Rust engine attempted all **13** groups, completed
**8**, verified **12,942** passing cases, and exposed at least
**1,296** differences; **5** workers failed. The corrected C engine actually
attempted all **13** groups, completed **5**, verified **13,094**
passing cases, and exposed at least **236** differences; **7** groups
had candidate failures and **1** had a result-encoding failure. The
complete mismatch count is **NOT MEASURED**. The Zig engine actually
attempted all **13** groups, completed **3**, and verified **927**
passing cases; **10** groups encountered test-worker infrastructure
failures. Its complete mismatch count is also **NOT MEASURED**.
Zig's earlier **1,764** differences remain a separate historical
result; no candidate qualifies.
Full-suite matching is **NOT MEASURED**.
Runtime independence is **NOT ESTABLISHED**.

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

- [Reproduce the current chart](docs/REPRODUCING.md) and inspect its [fully sourced headline-comparison renderer](tools/render_candidate_current_overview_v88.py).
- [Full experiment log, build evidence, failures, and rejected designs](docs/EXPERIMENT-LOG.md).
- [Complete Python correctness reference](oracle/phase1/P0-COMPLETENESS-V4.md).
- [Independent reference for the 8,244 additional checks](oracle/phase1/P0-DIFFERENTIAL-FUZZ-REFERENCE-V3.md).
- [Six independently written engine families](oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md) and [no-wrapping audit](oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md).
- [Guarded, exhaustive first-party C correctness](oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V7.md), [complete public C test results](oracle/phase2/evidence/repaired-c-original-campaign-v7-c-phase2-v18-c-subject-buffer-root-provenance-original-p0-v7-failures-publication-receipt.json), [reproducible native source-build procedure](oracle/phase2/C-SUBJECT-BUFFER-SOURCE-BUILD-V18.md), [independently authenticated C build](oracle/phase2/evidence/native-source-build-v18-c-phase2-v18-c-subject-buffer-root-provenance-publication-receipt.json), and a [not-yet-built C match-object compatibility correction](oracle/phase2/C-ORIGINAL-MATCH-SEMANTICS-V1.md).
- [Complete first-party Zig compatibility procedure](oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V9.md) and [complete public Zig test results](oracle/phase2/evidence/repaired-zig-original-campaign-v9-phase2-v13-zig-guard-clean-v1-original-p0-v9-failures-publication-receipt.json); all earlier attempts remain in the experiment log.
- [Complete first-party Rust compatibility procedure](oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V19.md) and [complete public Rust test results](oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v21-rust-captured-findall-root-provenance-original-p0-v19-failures-publication-receipt.json); all earlier attempts remain in the experiment log.
- [From-scratch Rust literal-search](oracle/phase2/RUST-LITERAL-FINDALL-ONE-PASS-V1.md), [captured-result experiments](oracle/phase2/RUST-CAPTURED-FINDALL-ONE-PASS-V1.md), and [exact Python scanner signatures](oracle/phase2/RUST-SCANNER-SIGNATURE-SOURCE-REPAIR-V22.md), with reproduced [literal](oracle/phase2/RUST-LITERAL-FINDALL-SOURCE-BUILD-V20.md) and [captured-result](oracle/phase2/RUST-CAPTURED-FINDALL-SOURCE-BUILD-V21.md) native builds; the scanner repair is not built, and full compatibility and speed are not established.
- [Larger, unopened 14,155,776-case speed-test proposal](oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md) and [preserved earlier proposal](docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md).
- [Original objective](GOAL.md), SHA-256
  `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`;
  [later clarifications](AMENDMENTS.md).
