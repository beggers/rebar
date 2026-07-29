# rebar: a faster Python `re` experiment

Build a faster, fully compatible replacement for Python 3.14.6's
regular-expression module:

```python
import rebar as re
```

Every candidate must use its own matching engine built from scratch. Wrapping
Python, another regular-expression package, or another candidate does not count.

## Results at a glance

**Six** from-scratch engine designs. **Zero** fully compatible
replacements. Speed compared with Python: **NOT MEASURED**.

![Six independently written regular-expression engines; Rust's first-party build succeeds and its full Python compatibility test is frozen but not yet run; the latest completed test found 928 differences; no engine qualifies; speed remains unmeasured; the 4.2-million-example final comparison is unopened](docs/evidence/candidate-current-overview-v53.svg)

The new Rust engine, including both first-party compatibility repairs,
has successfully completed an independently reproducible offline build.
Its complete, recovery-safe compatibility test is now frozen.
**The newly built engine has not yet taken that test.**
The last complete Rust test found **928** differences across all
**13** groups of Python's unchanged **31,237** original checks.

No engine wraps Python's matcher, an external regular-expression
package, or another candidate. The stronger runtime proof that no
engine delegates matching is **NOT ESTABLISHED**. There is no winner.

| Engine | Current build | Complete compatibility | Speed against Python |
| --- | --- | --- | --- |
| Python `re` | Python 3.14.6; independently verified reference | Reference checks agree | Reference; not timed |
| Public `rebar` import | Still selects an unqualified Zig prototype | FAIL; `__version__` missing | NOT MEASURED |
| Rust | First-party engine built; complete test frozen | New test NOT RUN; previous run: 928 differences | NOT MEASURED |
| C | First-party engine; corrected test prepared | Previous run: 1,230 differences | NOT MEASURED |
| Zig | First-party engine; corrected test prepared | Previous run: 1,764 differences | NOT MEASURED |
| C++ | First-party engine | Previous run: 2,308 differences; five worker failures | NOT MEASURED |
| Go | First-party engine | Previous run: 4,518 differences; four worker failures | NOT MEASURED |
| Fortran | First-party engine | NOT TESTED | NOT MEASURED |

Failed or interrupted groups are never counted as passes. All previous
failures remain available in the [experiment log](docs/EXPERIMENT-LOG.md).

## Detailed compatibility

These graphs describe particular behaviors in earlier development
builds. They do not show a passing replacement or a speed result.

![Earlier replacement and changing-buffer compatibility checks](docs/evidence/substitution-buffer-overview-v2.svg)

![Earlier scanner compatibility checks against Python](docs/evidence/scanner-verbose-overview-v1.svg)

![Earlier memory-lifetime compatibility checks against Python](docs/evidence/managed-buffer-lifetime-overview-v1.svg)

## Final comparison

The planned final comparison contains **4,194,304** unseen examples
and **24** balanced measurement rounds. Its examples are **NOT
FROZEN**, **NOT GENERATED**, and **NOT OPENED**. Speed, memory, and
confidence intervals are **NOT MEASURED**.

First, three independently built engines must pass all **31,237**
original checks, Python's two genuine **2,147,483,648**-character
tests, and separate public-import, signature, and runtime-independence
checks. The full-size replacement tests are **NOT RUN**. The winner
must be at least **1.5×** faster overall, measurably faster on at
least **60%** of cases, and explain every slowdown greater than
**20%**. There is no winner.

## Evidence and reproduction

- [Reproduce the results and verify every graph](docs/REPRODUCING.md).
- [Experiment log, original reports, failures, and rejected designs](docs/EXPERIMENT-LOG.md).
- [Frozen Python compatibility checks](oracle/phase1/P0-COMPLETENESS-V1.md).
- [Python's original two-billion-character compatibility requirements](oracle/phase1/P0-LARGE-INPUT-INDEXING-V1.md).
- [Corrected, independently verified Python reference](oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md).
- [Six from-scratch engine families](oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md) and [independent no-wrapping audit](oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md).
- [First-party Rust build protocol](oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V16.md), [actual build report](oracle/phase2/evidence/native-source-build-v16-rust-phase2-v16-rust-buffer-shape-pickle.json.gz), and [durable build receipt](oracle/phase2/evidence/native-source-build-v16-rust-phase2-v16-rust-buffer-shape-pickle-publication-receipt.json).
- [Frozen complete Rust compatibility test and safe recovery](oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V8.md).
- [Last complete Rust compatibility result](oracle/phase2/evidence/repaired-rust-original-campaign-v7-rust-phase2-v13-rust-pattern-repr-original-p0-failures.json.gz) and [independent failure and safe-restoration receipt](oracle/phase2/evidence/repaired-rust-original-campaign-v7-rust-phase2-v13-rust-pattern-repr-original-p0-failures-publication-receipt.json).
- [Separate public-import checks](oracle/phase1/P0-PUBLIC-ENTRYPOINT-IMPORT-V1.md) and [function-signature checks](oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md).
- [Expanded, still-unopened final comparison](docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md).
- [Original objective](GOAL.md), SHA-256
  `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`;
  [later clarifications](AMENDMENTS.md).
