# Rust performance starting point

The independent Rust engine is being optimized against the same pinned CPython **3.14.6** baseline and the unchanged, already-frozen **6,216-task** performance holdout. This document records its measured starting point before claiming any improvement.

| Test set | Speed relative to Python `re` | 95% range | Clearly faster | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| Practice | 0.1333× | 0.1332–0.1333× | 226/6,216 | 5,892/6,216 |
| Holdout | 0.1344× | 0.1343–0.1345× | 229/6,216 | 5,892/6,216 |
| Combined | 0.1338× | 0.1338–0.1339× | 455/12,432 | 11,784/12,432 |

**1× means the same speed as Python `re`; higher is faster.** The holdout result is exactly `0.13442162253182238×`, with the 95% range `0.13434517066223214–0.13449907992666935×`. This is an existing, correctness-gated measurement, not a pilot or a prediction.

## Where the time goes

The preserved family results show that ordinary matching, collecting results, captures, scanning, and Unicode are the problem. For example, quoted captures are **0.020×**, configuration lines **0.022×**, Unicode case folding **0.025×**, combined wide characters **0.031×**, Markdown **0.034×**, shared-prefix alternatives **0.107×**, dense literal collection **0.310×**, and long literal searches **0.378–0.403×**. These holdout families each retain all **64** measured inputs and all their losses in the [complete family-by-family comparison](zig-v6-final-report.md).

Fresh compilation is already faster on the larger frozen families: **1.633×** for 64 deeper cold-compilation tasks and **1.733×** for 48 expanded cold-compilation tasks. Optimization must preserve that measured advantage rather than trade it away unnoticed.

Source inspection identifies four general architectural costs:

- The matching interpreter constructs collections of intermediate states and copies capture storage while exploring alternatives and repeats.
- Searching starts new matching state repeatedly instead of reusing a compact, ordered execution state.
- Non-ASCII Python text is decoded, case-folded, and classified into temporary full-string arrays for each native match.
- Python/native calls box match arguments, allocate spans, and build intermediate match/collection results; collection reserves storage based on the whole input and group count.

An isolated [all-family execution profile](rust-v6-baseline-profile.json) checks **568** representative frozen holdout cases against stdlib (**1,136** correctness checks) without changing the production binary. A separate [native-allocation profile](rust-v6-baseline-allocations.json) confirms the scaling problem: one quoted-capture action performs **511,095** native allocations and requests **103.9 MB**, and one CSV split performs **1,288,260** allocations and requests **165.8 MB**. These are observations about the starting architecture, not claimed optimized results.

## Newly exposed compatibility gap

Passing the existing frozen matrix is not sufficient evidence that the starting Rust engine is a drop-in replacement. A deterministic [new API/property oracle](rust-v6-baseline-paths-finding.json) exposes **7,281 mismatches in 44,659** checks; its [stdlib-vs-stdlib control](rust-v6-baseline-paths-self.json) passes all **44,659**. The new [Unicode oracle](rust-v6-baseline-unicode-probe.json) exposes **554 mismatches in 3,495** checks; its [stdlib control](rust-v6-baseline-unicode-self.json) passes all **3,495**. Its exhaustive [full-Unicode-plane self-control](rust-v6-baseline-unicode-self-fullplane.json) additionally passes **4,494,555** checks with zero failures across every code point and four text/flag partitions. These controls include all **50** authoritative special-fold keys and **56** directed edges, **102** characters with expanding uppercase, nullable captures, and position/window/scanner semantics.

A small direct check also exposes **seven mismatches in eight** ordinary case-insensitive examples:

| Pattern | Input | Python `re` | Starting Rust |
| --- | --- | --- | --- |
| `(?i)σ` | `ς` | matches | does not match |
| `(?i)μ` | `µ` | matches | does not match |
| `(?i)[σ]` | `ς` | matches | does not match |
| `(?i)д` | `ᲁ` | matches | does not match |
| `(?i)θ` | `ϑ` | matches | does not match |
| `(?i)φ` | `ϕ` | matches | does not match |
| `(?i)κ` | `ϰ` | matches | does not match |

These failures are not waived, hidden, or counted as acceptable. A second independently preserved [1,200-check Unicode investigation](rust-v6-baseline-unicode-hidden.json) records **326** failures. The [raw-surrogate pattern gate](rust-v6-baseline-surrogates.json) exposes **100 failures in 380** checks while its [stdlib control](rust-v6-baseline-surrogates-self.json) passes all **380**. A [790-check backreference oracle](rust-v6-baseline-unicode-backreferences.json) establishes that case-insensitive literals/classes and backreferences use different equivalence rules. The campaign must fix all of these Python matching rules before claiming a compatible or performance-qualified result. A [full-plane scalar-FFI experiment](rust-v6-unicode-ffi-fullplane.json) separately verifies Python's non-regex Unicode data helpers against all **1,114,112** code points; it is feasibility evidence, not a production-engine performance result.

## Reproducibility

The authoritative [initial five-engine result](../../performance/v6/evidence/INITIAL.md) contains **808,080** raw timing rows, all **49,728** engine/task results, all memory observations, confidence intervals, and losses. Its expanded raw SHA-256 is `a6fefab9e97c21e1ea17d258860fd05dbbc9adc3bb2154b66935abe3d3d84907`; the deterministic compressed [initial summary](../../performance/v6/evidence/initial-summary.json.gz) has SHA-256 `22dc707132dea304cc518ea867cfcf4f489f4df9d1d3d336b0dbac9435c20be4`.

The frozen fixture SHA-256 is `c8e32e879cc7a134748f8f3f29fed49678895745fdecebe63ceec46b6a3b5335`. The starting source is pinned to commit `55583702`:

| Starting-point file | SHA-256 |
| --- | --- |
| Rust parser and matching engine | `3261aadfae745c156e6a05fae5d8b32fe878d31a41109e1424dcd1aa509d83da` |
| Python/native C bridge | `a324d193faeb7a046f02f490200499bba0371fb37a5f324898d570dcd9d4e880` |
| Python public interface | `86504fcb4a2666c9044eb4fd86479c43470ca22fecf72d101c95a080c272d072` |
| Rust build configuration | `2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966` |
| Rust/native build script | `ed28e98378d12d9a676916c9948cc9ded5a02442a3dd4b5f3d1bd8d3de314df3` |

The Rust implementation remains entirely from scratch: no external regular-expression package, Python `re`, `_sre`, Zig engine, or native C regex engine may perform production matching. Frozen correctness, upstream CPython tests, deterministic differential/property tests, Unicode, safety, and source/import audits must pass before timing.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_rust.sh
PYTHONPATH=. "$PY" tools/oracle_v2.py verify --module candidates.rust_candidate --output /tmp/rebar-rust-v2.json
PYTHONPATH=. "$PY" tools/oracle_v3.py verify --module candidates.rust_candidate --cohort holdout --output /tmp/rebar-rust-v3.json
PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify --module candidates.rust_candidate --output /tmp/rebar-rust-official.json
PYTHONPATH=. "$PY" tools/perf_v6.py verify --module candidates.rust_candidate --output /tmp/rebar-rust-v6.json
PYTHONPATH=. "$PY" tools/rust_v6_paths_probe.py --module re --seeded-cases 16 --output /tmp/rebar-rust-paths-self.json
PYTHONPATH=. "$PY" tools/rust_v6_paths_probe.py --module candidates.rust_candidate --seeded-cases 16 --output /tmp/rebar-rust-paths.json
PYTHONPATH=. "$PY" tools/rust_unicode_probe.py --module re --membership-stride 65537 --seeded-cases 4 --output /tmp/rebar-rust-unicode-self.json
PYTHONPATH=. "$PY" tools/rust_unicode_probe.py --module candidates.rust_candidate --membership-stride 65537 --seeded-cases 4 --output /tmp/rebar-rust-unicode.json
PYTHONPATH=. "$PY" tools/rust_perf_v6.py self-test
PYTHONPATH=. "$PY" tools/rust_merge_v6.py --self-test
PYTHONPATH=. "$PY" tools/rust_v6_loss_probe.py --self-test
PYTHONPATH=. "$PY" tools/audit_candidate.py candidates/rust_candidate.py candidates.rust_candidate candidates/rust/src/lib.rs
PYTHONPATH=. "$PY" tools/audit_candidate.py candidates/rust_candidate.py candidates.rust_candidate candidates/rust/py_bridge.c
```
