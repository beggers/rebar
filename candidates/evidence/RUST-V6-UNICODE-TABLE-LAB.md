# Building Python-compatible Unicode support from scratch

This experiment asks which native Rust lookup-table design most quickly and
accurately reproduces the character behavior of CPython **3.14.6** and Unicode
**16.0.0**. It is an experiment on a component of the Rust regex engine, not a
measurement of the complete `re` replacement. Overall regex speed is **NOT
MEASURED** here.

The [complete results and all raw measurements](rust-v6-unicode-table-lab.json.gz)
preserve the direct Python-character-data baseline, all **13** alternative
from-scratch native designs, all **7,280** randomized timing observations, all
confidence intervals, every slower result, and every measured binary size.

## Every tested design

Here, **1×** means the same speed as directly calling Python's pinned native
character-data helpers in the isolated experiment. Higher is faster. These are
character-operation measurements, not complete regex benchmark results.

| Native character-data design | Speed | 95% range | Extra native binary size |
| --- | ---: | ---: | ---: |
| Direct Python-character-data reference | 1.000× | Reference | 0 B |
| 16-bit page indexes, 32-bit differences | 1.369× | 1.339–1.401× | 125,840 B |
| 8-bit page indexes, 32-bit differences | 1.369× | 1.340–1.402× | 112,784 B |
| 8-bit page indexes, 16-bit differences | 1.355× | 1.327–1.384× | 87,912 B |
| 128-character case pages | 1.374× | 1.344–1.406× | 107,672 B |
| Direct first 256 character properties | 1.395× | 1.364–1.428× | 112,752 B |
| 128-character case pages and direct first 256 properties | 1.399× | 1.370–1.431× | 107,640 B |
| Direct first 4,096 character properties | 1.402× | 1.372–1.431× | 111,920 B |
| Direct first 16,384 character properties | 1.421× | 1.392–1.452× | 124,208 B |
| Direct properties for the whole basic multilingual plane | 1.438× | 1.410–1.468× | 173,360 B |
| Direct first 4,096 lowercase and case-equivalence values | 1.452× | 1.416–1.488× | 140,720 B |
| 4,096 direct properties plus 4,096 direct case values | 1.457× | 1.423–1.493× | 144,960 B |
| **16,384 direct properties plus 4,096 direct case values** | **1.463×** | **1.430–1.499×** | **157,248 B** |
| Basic-plane direct properties plus 4,096 direct case values | 1.491× | 1.455–1.527× | 206,400 B |

In a direct comparison of the exact same **520** trials, the adopted
middle-sized design is **1.0041×** faster than the smaller 4,096-property
design. Its 95% range, **0.9953–1.0129×**, does not establish a reliable
difference. The larger basic-plane design is **1.0189×** faster than the
adopted design, and its 95% range, **1.0106–1.0277×**, establishes a real
improvement in this character-only experiment. It also adds **49,152 B**.
The larger design is preserved, and its speed advantage is not hidden. The
production module currently uses the smaller-memory middle-sized design;
whether the larger design improves the complete regex engine is **NOT
MEASURED** here and must be decided by the full paired calibration.

The larger option is also retained as an independently reproducible,
complete-API candidate. Its [isolated production generator](../../tools/rust_unicode_bmp_production_generate.py)
reuses the same frozen Unicode source rather than copying another engine, and
its [full-character compatibility proof](rust-v6-unicode-bmp-production-fullplane.json)
passes all **13,369,344** direct Python comparisons. The exact generated
alternative has SHA-256
`ea93d9bfd3d089a9333a38e3eabdaf05ae932a6b01b3a6fe8f388808ae47107d`;
its committed proof has SHA-256
`52fd24d5fc4189e1be08d2b4493cd7cff07f80cabcccce559ab4f98f635723d6`.
Generating or checking this alternative does not change the selected
production module.

The adopted design is faster on **39 of 40** subject-and-operation comparisons.
Its one nominally slower case is the word-character check on
`hold.deeper.unicode-casefold.03`: **0.9947×**, with 95% range
**0.9442–1.0434×**. The measured **0.53%** difference is not statistically
established; the result and its full uncertainty range are preserved, not
excluded. No measured case in the adopted design is more than 20% slower.
All **520** detailed per-design case results remain in the raw archive.

| Operation | Adopted design versus direct character-data reference | Faster subjects |
| --- | ---: | ---: |
| Word characters | 1.281× | 7/8 |
| Decimal digits | 1.443× | 8/8 |
| Whitespace | 1.267× | 8/8 |
| Python's simple lowercase rule | 1.386× | 8/8 |
| Case-insensitive literal equivalence | 2.064× | 8/8 |

## Correctness and measurement protocol

Every design checks all **1,114,112** Unicode code points for each of the five
measured operations before entering the timing trials: **72,417,280** checked
character operations in total, with **zero** unexplained failures. Every
warmup and every measured timing also checks its result against the pinned
reference before retaining the timing.

The [independent production-module proof](rust-v6-unicode-production-fullplane.json)
also checks **all 1,114,112 characters directly against all 12 pinned Python
property and case-mapping values**: **13,369,344 individual comparisons**,
with **zero** differences. It separately checks all **2,048** surrogate
characters, all **102** expanding-uppercase characters, and **three**
out-of-range 32-bit values. All four original Unicode source hashes match the
generated module. The reproducible proof has SHA-256
`1b8a3ce0459d12ed862f2b55a3d0992bdd11b4d5b5a1429a3f90f1d5819e99c2`.

The test uses **eight unchanged subjects** from the frozen project holdout:

- `hold.deeper.unicode-word-lines.00`, `.03`, and `.07`.
- `hold.deeper.unicode-casefold.00`, `.03`, and `.07`.
- `hold.deeper.combining-wide.00` and `.07`.

Each subject is run for all **five** operations, with **four** warmups and
**13** randomized, directly paired trials of all **14** implementations. The
uncertainty ranges use the frozen protocol's **2,000** bootstrap resamples.
The random execution-order seed is `1985072201`; the bootstrap seed is
`1985072202`. No holdout cases, measured alternatives, raw timing positions,
checksums, confidence intervals, or losses are removed.

The fixed fixture is checked before any measurement:

| Frozen input | SHA-256 |
| --- | --- |
| Performance suite | `091d7be04f7251781e2b8568f6cb19acbe603cb1d945926a69ba32adaf9b6b0f` |
| Expected results | `c8e32e879cc7a134748f8f3f29fed49678895745fdecebe63ceec46b6a3b5335` |
| Performance manifest | `06c3b09a203d036e3129d90b6c412e716a3835e4c4e2827df73c189dec4956f1` |

The production table includes **all eight** pinned Python character
properties, including exact valid first and subsequent characters for named
capture groups. The full-Unicode counts, in table order, are **142,940** word
characters, **760** decimal digits, **888** digit characters, **2,002** numeric
characters, **141,028** alphabetic characters, **29** whitespace characters,
**141,247** valid identifier-start characters, and **144,522** valid
identifier-continuation characters.

Python applies different case rules to case-insensitive literals and to
backreferences. The table deliberately preserves both: raw simple lowercase
for backreferences, and the **24** connected case-equivalence groups covering
**50** special lowercase values for literals and character classes. It also
preserves exact simple uppercase, all **102** characters with expanding
uppercase, unpaired surrogate characters, and safe out-of-range handling.
Using Rust's currently newer Unicode data would not reproduce the frozen
Python rules.

The production module does not call Python, import `re`, use `_sre`, wrap
another regex engine, or depend on an external regex package. The pinned
Python character-data helpers appear only in the isolated table generator and
comparison process. The source data are independently identifiable:

| Complete Unicode-16 input | SHA-256 |
| --- | --- |
| Eight character properties | `1319144f169e188aeef4f778a4506bfb1a941c9d4519f25714c640e45a5a60bc` |
| Python simple lowercase | `dc773c96a0faf9357e7244c4758295e2c7d4651104703758cf830a1fd6734299` |
| Python simple uppercase | `86f1f043f57ba429c209379543cf370614bd070f76402bc18d1f4fe2584cdc41` |
| Case-insensitive literal equivalence | `9d2779e2c62d3b0b1347bb203400e7b8549bdce88cec65269433c77aae7b1bb6` |

The generated [production Unicode module](../rust/src/unicode_tables.rs) has
SHA-256 `f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af`
and separately passes Rust formatting and compilation with warnings denied.
The compressed raw result has SHA-256
`4727f71b229a893d0d4dfe621f6ee6f6cab491589264188995d7b9b037f95791`;
its decompressed contents have SHA-256
`aa26e926c49028adc7c0f8c7eb536d90a9fc4afaf42db7eb47d769978c1c701a`.

## Reproduce

The [committed experiment and table generator](../../tools/rust_unicode_table_lab.py)
regenerates the complete table directly from the pinned Python character data,
checks the unchanged holdout and all Unicode code points, builds all 14 native
alternatives from scratch, and retains every trial. The separate
[production-module verifier](../../tools/rust_unicode_production_verify.py)
independently checks the exact generated production source without importing
Python `re`, `_sre`, an external regex package, or another candidate engine:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONPATH=. "$PY" tools/rust_unicode_production_verify.py \
  --output /tmp/rebar-rust-unicode-production-fullplane-reproduced.json

PYTHONPATH=. "$PY" tools/rust_unicode_table_lab.py \
  --output /tmp/rebar-rust-unicode-table-lab-reproduced.json.gz

PYTHONPATH=. "$PY" tools/rust_unicode_table_lab.py \
  --generate-only \
  --emit-production-module /tmp/rebar-rust-unicode-tables-reproduced.rs

PYTHONPATH=. "$PY" tools/rust_unicode_bmp_production_generate.py \
  --output /tmp/rebar-rust-unicode-bmp-production-fullplane-reproduced.json

sha256sum /tmp/rebar-rust-unicode-tables-reproduced.rs \
  candidates/rust/src/unicode_tables.rs
```

The final project-level comparison, complete Python `re` correctness gates,
memory measurements, and candidate rankings remain separate and must be
reported from the complete frozen regex performance oracle.
