# Zig fixed-width lookbehind/reference follow-up

The from-scratch Zig engine now supports references to earlier fixed-width captures inside positive and negative lookbehind, including numbered/named captures, equal-width alternatives, text/bytes, Unicode, flags, and every common API. Variable-width or same-lookbehind references produce the same errors and locations as Python. No previous passing frozen case regressed.

![Zig compatibility gained from fixed-width lookbehind references](zig-lookbehind-correctness.svg)

![Overall Zig speed and the 36 balanced holdout families](zig-lookbehind-v4-family.svg)

## Headline result

| Frozen check | Before | After | New failures |
| --- | ---: | ---: | ---: |
| Expanded correctness matrix | 8,117/8,244 | **8,121/8,244** | 0 |
| Large correctness holdout | 35,402/35,840 | **35,402/35,840** | 0 |
| Large performance tasks | 2,448/2,448 | **2,448/2,448** | 0 |
| Official CPython methods | 124/144 | **125/144** | 0 |

The four expanded gains are the three valid named/numbered positive/negative references and the exact variable-width error. The official lookbehind method now passes. All **438** remaining large-holdout failures and **123** expanded failures are deeper valid patterns dominated by nullable/nested repeats and bounded executor state; invalid patterns/templates remain complete.

The full paired performance rerun covers **1,224 practice + 1,224 unseen holdout tasks**, frozen operation counts, 13 trials, memory, and **63,648** raw rows. Every result is checked before and after timing.

| Task set | Overall speed vs Python `re` | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: |
| Practice | 0.430x (0.415--0.445x) | 83/1,224 | 997/1,224 |
| Holdout | **0.459x (0.445--0.475x)** | **91/1,224** | **979/1,224** |
| All | 0.444x (0.434--0.455x) | 174/2,448 | 1,976/2,448 |

Overall speed is close to the previous **0.467x** run and the measured ranges overlap. Cold compilation is unchanged (**1.755 -> 1.753x**) and references are unchanged (**0.277 -> 0.275x**). Family movement is small and mixed: negative-lookbehind searches improve about 11%, while negative-ahead, UUID, short misses, and template substitution fall about 10--12%. The capture-returning core is **2.15x** overall on eight tasks, with seven faster and alternative search the sole loss. Every loss remains visible below and in the raw results.

## Correctness control and design

The new differential probe passes **32,912/32,912** comparisons across 16 fixed examples, 16 exact-error cases, and **32,768** seeded cases. It covers search, match, fullmatch, findall, finditer, split, replacement, scanners, metadata, numbered/named captures, positive/negative and nested lookbehind, equal-width alternatives/repeats, case modes, text, bytes, and Unicode. Its initial **4,240-case** run records **4,230** failures before implementation. The existing error, scoped-flag, full-plane Unicode, span, and capture controls pass **34,682**, **16,552**, **8,781**, **8,874**, and **5,214** checks. Debug plus address/undefined-behavior checks pass **8,336** focused lookbehind, **10,106** error, **4,264** scoped, **1,437** Unicode, and all span/capture checks with zero findings; official methods have zero crashes/timeouts.

Zig computes a referenced group's width directly from its already-built syntax tree when compiling lookbehind. Literals/classes, sequences, equal-width branches, fixed repeats, atomic/scoped groups, and earlier references compose without reparsing or runtime allocation. A small parser stack records the first group visible before entering nested lookbehind and rejects references defined inside it; the Python-side error validator mirrors that rule and reports the end position used by CPython. Variable referenced groups are rejected with the exact fixed-width error. The fixed program allocation remains **415,000 B** and matching bytecode is unchanged for patterns without these references.

## Detailed graphs

![Zig temporary memory on every holdout task family](zig-lookbehind-v4-memory.svg)

![Where Zig wins and loses on every holdout task family](zig-lookbehind-v4-regressions.svg)

All legacy and generated task families appear in the detailed graphs. Process high-water marks, every confidence range, and every regression remain in the raw data; denominators are unchanged.

## Evidence and reproduction

Performance rows are [zig-lookbehind-v4-raw.jsonl.gz](zig-lookbehind-v4-raw.jsonl.gz), with the full summary in [zig-lookbehind-v4-summary.json](zig-lookbehind-v4-summary.json). Correctness after results are [expanded](zig-lookbehind-v2-after.json.gz), [large holdout](zig-lookbehind-v3-after.json.gz), [performance qualification](zig-lookbehind-perf-v4-after.json), and [official](zig-lookbehind-upstream-after.json). Focused/safety evidence is [initial failures](zig-lookbehind-focused-before.json.gz), [focused](zig-lookbehind-focused.json), [errors](zig-lookbehind-errors.json), [scoped](zig-lookbehind-flags.json), [Unicode](zig-lookbehind-unicode.json), [span](zig-lookbehind-span.json), [capture](zig-lookbehind-capture.json), [instrumented focused](zig-lookbehind-sanitized-focused.json), [instrumented errors](zig-lookbehind-sanitized-errors.json), [instrumented scoped](zig-lookbehind-sanitized-flags.json), [instrumented Unicode](zig-lookbehind-sanitized-unicode.json), [instrumented span](zig-lookbehind-sanitized-span.json), and [instrumented capture](zig-lookbehind-sanitized-capture.json).

Reproduce with:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_zig_probe.sh
PYTHONPATH=. "$PY" tools/zig_lookbehind_refs_probe.py --output /tmp/zig-lookbehind.json --seeded-cases 32768
PYTHONPATH=. "$PY" tools/perf_v4.py verify --module candidates.zig_candidate --output /tmp/zig-performance-check.json
PYTHONPATH=. "$PY" tools/zig_perf_v4_pilot.py --raw /tmp/zig-performance.jsonl --output /tmp/zig-performance.json --chart /tmp/zig-speed.svg --memory-chart /tmp/zig-memory.svg --regression-chart /tmp/zig-regressions.svg --trials 13 --bootstraps 5000
```

The new probe is [tools/zig_lookbehind_refs_probe.py](../../tools/zig_lookbehind_refs_probe.py). Static/import and linkage audits report zero forbidden markers or blocked attempts; production links only the local Zig engine and the C runtime.
