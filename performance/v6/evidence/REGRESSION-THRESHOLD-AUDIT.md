# Correcting the historical slowdown threshold

A result is **more than 20% slower** when a replacement takes more than `1.2 ×` Python's time. Because reported speed is `Python time / replacement time`, the correct cutoff is `speed < 1 / 1.2`, or `speed < 5 / 6`.

The earlier version-6 code instead used `speed < 0.8`. That flags replacements only when they are more than **25% slower**. It therefore omitted the more-than-20%-through-25% interval. The frozen inputs, original timings, official summaries, and confidence ranges have **not** been changed or rerun.

## Original five-engine test

All counts use the complete **6,216-case unseen holdout**. Python `re` is the unchanged reference.

| Engine | Original reported slowdowns | Corrected more-than-20% slowdowns | Previously omitted |
| --- | ---: | ---: | ---: |
| Python `re` baseline | 0/6,216 | 0/6,216 | 0 |
| Python engine | 5,918/6,216 | 5,919/6,216 | 1 |
| Native C engine | 653/6,216 | 742/6,216 | 89 |
| Rust engine | 5,892/6,216 | 5,892/6,216 | 0 |
| Zig / `rebar` | 243/6,216 | 255/6,216 | 12 |

## Optimized Zig and preserved final comparison

The optimized Zig rerun originally reported **2** large holdout slowdowns. Applying the correct threshold to its existing 6,216 measured speedups gives **7**, including **5** previously omitted cases.

| Engine in final comparison | Corrected holdout slowdowns | Previously omitted |
| --- | ---: | ---: |
| Python `re` baseline | 0/6,216 | 0 |
| Python engine | 5,919/6,216 | 1 |
| Native C engine | 742/6,216 | 89 |
| Rust engine | 5,892/6,216 | 0 |
| Zig / `rebar` | 7/6,216 | 5 |

### Every corrected optimized-Zig holdout slowdown

- **Six short version strings:** each frozen `findall` case matches one short semantic version and returns four captures. The earlier Zig report attributes this already-profiled family to Python/native call and capture-result construction exceeding the small matching cost. Four of these six cases were previously omitted.
- **One short negated-class field:** the frozen `findall` case checks one `key=value` record with two bounded negated classes, two captures, and a delimiter lookahead. Its measured 20.25% slowdown was previously omitted. A more specific implementation-level explanation is **NOT MEASURED**; this audit does not re-profile the holdout.

| Frozen task | Workload | Speed relative to Python | Extra time | Omitted before? |
| --- | --- | ---: | ---: | --- |
| `hold.deeper.negative-class.00` | `deeper-negative-class` | 0.8316× | 20.25% | Yes |
| `hold.expanded.ip-version.00` | `expanded-ip-version` | 0.7667× | 30.44% | No |
| `hold.expanded.ip-version.06` | `expanded-ip-version` | 0.7299× | 37.01% | No |
| `hold.expanded.ip-version.12` | `expanded-ip-version` | 0.8144× | 22.79% | Yes |
| `hold.expanded.ip-version.18` | `expanded-ip-version` | 0.8258× | 21.10% | Yes |
| `hold.expanded.ip-version.24` | `expanded-ip-version` | 0.8294× | 20.57% | Yes |
| `hold.expanded.ip-version.30` | `expanded-ip-version` | 0.8194× | 22.05% | Yes |

The frozen task names identify the exact kind of work. Category counts and every previously omitted case for every engine and test set are retained in [regression-threshold-audit.json](regression-threshold-audit.json). This audit does not infer an unmeasured implementation cause or claim a new speed measurement.

## Evidence and reproduction

The audit verifies the version-6 expected-result hash, every candidate and holdout denominator, each historical flag and ranking, and that the final combined comparison exactly preserves all original non-Zig results plus the optimized Zig run. Compressed and expanded source hashes are recorded in the JSON evidence.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONPATH=. "$PY" tools/perf_regression_audit.py
```

The command reads already-recorded summaries and regenerates the audit and newly named corrected charts. It never executes a regex candidate, times an operation, changes the frozen fixture, or rewrites a historical result.
