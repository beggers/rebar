# rebar: a faster Python `re` experiment

Build a faster, fully compatible replacement for
[Python 3.14.6](https://www.python.org/downloads/release/python-3146/)'s
regular-expression module:

```python
import rebar as re
```

Every candidate must use its own matching engine built from scratch. Wrapping
Python, another regular-expression package, or another candidate does not count.

## Results at a glance

**Six** from-scratch engine designs. **Zero** fully compatible
replacements. Speed compared with Python: **NOT MEASURED**.

![Six independently built regular-expression replacements compared with Python. The corrected Python reference is verified. Rust still has 1,440 observed differences, and the complete test gate remains blocked until 8,244 additional cases receive two independent reference runs. No replacement qualifies, no speed is measured, and the final comparison remains unopened.](docs/evidence/candidate-current-overview-v61.svg)

The independently built Rust engine has completed all **13** groups
of Python's unchanged **31,237** original checks with **13** real
test workers and no infrastructure failures. It is **not compatible**:
the run found **1,440** differences, **512 more** than the previous
Rust result of **928**. The three failures concern buffer lifetime,
substitution, and replacement shape. All four original engine files
were restored exactly before the result was published.

A narrowly scoped fix now keeps the original Python buffer alive during
replacement. It is implemented in our own code and reproduces exactly
from the failing source. A reproducible, two-independent-build recipe
is frozen, but the correction is **not yet built or retested**; it does
not change the reported result.

The original test checklist has now been reconciled with the corrected
Python reference; two independently recorded Python workers agree on
all **6,912** affected cases. Every one of the additional **8,244**
fuzz and property cases is frozen and individually verified. Those
extra cases still need two independent Python-reference runs and
complete candidate runs. Builds, compatibility claims, and benchmarks
remain blocked until those checks genuinely pass.

No engine wraps Python's matcher, an external regular-expression
package, or another candidate. The stronger runtime proof that no
engine delegates matching is **NOT ESTABLISHED**. There is no winner.

| Engine | Current build | Complete compatibility | Speed against Python |
| --- | --- | --- | --- |
| Python `re` | Pinned Python 3.14.6 | Original reference agrees; extra fuzz replay pending | Reference; not timed |
| Public `rebar` import | Still selects an unqualified Zig prototype | FAIL; `__version__` missing | NOT MEASURED |
| Rust | Latest engine tested; new buffer fix not yet built | FAIL; 1,440 differences, 512 more than its previous run | NOT MEASURED |
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

First, independently verify all **8,244** additional fuzz and property
checks against Python, without adding them to the **31,237** original
cases. Then three
independently built engines must pass all **31,237** original checks,
the additional cases, Python's two genuine
**2,147,483,648**-character tests, and separate public-import,
signature, and runtime-independence checks. The full-size replacement
tests are **NOT RUN**. The winner must be at least **1.5×** faster
overall, measurably faster on at least **60%** of cases, and explain
every slowdown greater than **20%**. There is no winner.

## Evidence and reproduction

- [Reproduce the results and verify every graph](docs/REPRODUCING.md).
- [Experiment log, original reports, failures, and rejected designs](docs/EXPERIMENT-LOG.md).
- [Corrected Python compatibility checklist](oracle/phase1/P0-COMPLETENESS-V2.md); the original checks stay fixed, while the extra fuzz reference remains pending.
- [Original, preserved Python compatibility checklist](oracle/phase1/P0-COMPLETENESS-V1.md) and [separately frozen 8,244-case fuzz corpus](oracle/v2/expected.jsonl).
- [Python's original two-billion-character compatibility requirements](oracle/phase1/P0-LARGE-INPUT-INDEXING-V1.md).
- [Corrected, independently verified Python reference](oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md).
- [Six from-scratch engine families](oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md) and [independent no-wrapping audit](oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md).
- [First-party Rust build protocol](oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V16.md), [actual build report](oracle/phase2/evidence/native-source-build-v16-rust-phase2-v16-rust-buffer-shape-pickle.json.gz), and [durable build receipt](oracle/phase2/evidence/native-source-build-v16-rust-phase2-v16-rust-buffer-shape-pickle-publication-receipt.json).
- [Complete latest Rust compatibility report](oracle/phase2/evidence/repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures.json.gz), [durable result receipt](oracle/phase2/evidence/repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures-publication-receipt.json), and [independent failure analysis](oracle/phase2/evidence/repaired-rust-original-campaign-v10-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures-forensic-summary.json).
- [Reproducible from-scratch Rust buffer correction](oracle/phase2/RUST-BUFFER-SHAPE-PICKLE-SOURCE-REPAIR-V2.md); its corrected source is frozen but not yet built or retested.
- [Frozen, independently reproducible Rust build recipe](oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V17.md); compilation remains blocked until all required Python-reference checks pass.
- [Separate public-import checks](oracle/phase1/P0-PUBLIC-ENTRYPOINT-IMPORT-V1.md) and [function-signature checks](oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md).
- [Expanded, still-unopened final comparison](docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md).
- [Original objective](GOAL.md), SHA-256
  `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`;
  [later clarifications](AMENDMENTS.md).
