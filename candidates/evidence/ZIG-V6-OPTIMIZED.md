# Zig optimization on the broader holdout

The broader test initially exposed **243** large Zig slowdowns. After profiling and four general from-scratch optimizations, the final **6,216-task** holdout reaches **1.7334×** Python `re` speed (95% range **1.7321–1.7346×**), is clearly faster on **5,691/6,216 (91.6%)**, and has **two** explained large slowdowns. Practice is consistent at **1.7282×**, 5,610 clearly faster, with five slowdowns.

![Overall speed](zig-v6-final-overall.svg)

![Zig workload speed](zig-v6-final-zig-speed.svg)

## What changed

- **Literal collection:** a compiled pattern containing only literal text now finds all non-overlapping occurrences in one native call, creates the correct text/byte results, handles windows and buffers, and avoids capture-record allocation. The measured dense-literal family improves **0.676→1.032×** and its 63 large slowdowns disappear.
- **Shared prefixes:** the independent Zig compiler factors a common literal prefix across ordered alternatives, then emits guarded branch choices that still backtrack in the original order. Ambiguous prefixes and forced continuations remain correct. Shared-prefix workloads improve **0.627→1.408×**, eliminating 56 large slowdowns.
- **Character classes and ASCII:** prepared class flags are normalized once at compile time, avoiding repeated high-marker masks in hot runs. Before the fix, every ordinary class check missed its table; the correctness-gated profile now records a cache hit for every applicable check. Safe ASCII equality/category shortcuts retain Python's special Unicode folds and whitespace rules. Filenames improve **0.495→2.061×** and number/unit matching **0.899→1.798×**, removing 86 large slowdowns.
- **Line starts:** an expression that begins with `^` now skips directly between possible line starts during search, including wide Unicode input and input windows. The profiled Unicode-line workload falls from a median **415** matcher starts to **12** and improves **0.818→2.492×**, removing 32 large slowdowns.

The earlier reference and branch families also improve **1.018→1.179×** and **1.287→1.668×**; their six slowdowns disappear. Strong paths remain strong: balanced quoted CSV is **15.275×**, long successful searches **5.157×**, and long misses **5.843×**.

## Final performance evidence

The initial comparison measured all four independent engines and unmodified stdlib using the frozen protocol. The optimized Zig rerun uses the exact same **12,432** tasks, **4** warmups, operation counts, **13** deterministically ordered paired trials, memory collection, equal weights, and **2,000** seeded bootstrap samples. It retains **323,232** paired rows and **646,464** immediate before/after correctness checks; no incorrect timing is included.

| Test set | Zig speed | 95% range | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: | ---: |
| Practice | 1.7282× | 1.7270–1.7294× | 5,610/6,216 | 5 |
| Holdout | **1.7334×** | **1.7321–1.7346×** | **5,691/6,216** | **2** |
| All | 1.7308× | 1.7299–1.7316× | 11,301/12,432 | 7 |

The two holdout slowdowns are `hold.expanded.ip-version.00` (`v1.4.0`, **0.767×**, 0.677–0.836× range) and `.06` (`v1.10.0`, **0.730×**, 0.566–0.834× range). Both are six/seven-character inputs returning four captures: matching is tiny, so Python/native call and result construction dominate. The five practice slowdowns are four repeated short lookbehind/capture searches (`cal.large.nearby-capture.01`, `.02`, `.03`, `.15`) and a one-operation long-search timing (`cal.deeper.search-long-hit.44`); the corresponding holdout families remain faster overall.

Temporary Python memory is at or below stdlib on **5,722/6,216** holdout tasks with a **0.54×** median ratio. All candidate families, memory, and losses are shown in the [complete report](zig-v6-final-report.md).

![Speed by family and engine](zig-v6-final-family-speed.svg)

![Temporary memory](zig-v6-final-memory.svg)

![Wins and losses](zig-v6-final-win-loss.svg)

![Rankings](zig-v6-final-rankings.svg)

Raw SHA-256 is `e58c30e6350c6e98bd40e5176ee0c37290b7a978116aab1e1f52ca3cecfb7011`; expanded summary SHA-256 is `0e768b8b1596f0d22f865b623947a273e8d0a7cccc83e59901445123004d4713`. The compressed [raw rows](zig-v6-final-raw.jsonl.gz) and [summary](zig-v6-final-summary.json.gz) have SHA-256 `92fee2028706a254464f1ada2d43a5a4ebdf19a50967bf832b3795cb8831217d` and `4bb7156877c8cb138fd3530ad0904ec567333e740032a8c7dbcdde4f0ad68fb9`. The [combined four-engine summary](zig-v6-combined-summary.json.gz) retains the original candidate results and the final Zig result (expanded SHA-256 `edf51b699cba36d3d8b8a00bdaf67bb681ec093f84d2ec1c7cd57d51a6c2c2a7`, compressed SHA-256 `52dfa344da5037f791673b74db42e483c7619567df167053cec3de29fbb7273b`). The [first complete rerun](zig-v6-first-rerun-summary.json.gz) and its [raw rows](zig-v6-first-rerun-raw.jsonl.gz) are also retained.

Retiming all five engines was attempted and stopped cleanly after **177,980** correctness-tagged rows because the unchanged Python/Rust candidates make the frozen run take about **3.4 hours** (as the completed initial run demonstrates). The [partial rows](zig-v6-partial-five-engine-raw.jsonl.gz) and [log](zig-v6-partial-five-engine.log.gz) are retained; they are not summarized or used for selection.

## Correctness, safety, and rejected designs

Release gates pass **723,767** checks: both frozen correctness suites, both performance fixtures, all 144 runnable official methods, public surface, full-plane Unicode, large patterns/groups/repeats, syntax/flags/errors/references, spans/captures, existing dispatch/executor probes, and **230,337** new literal/choice/class/line/buffer/API differential checks. The stdlib self-check passes **115,649** new checks. Debug plus address/undefined-behavior builds pass another **264,775** checks. Both source/import delegation audits report zero forbidden markers and zero blocked imports.

The full-plane gate initially reproduced two failures: Unicode `\s` includes U+001C–U+001F while ASCII `\s` does not. The [finding](zig-v6-unicode-finding.json.gz) and [fixed result](zig-v6-unicode-fixed.json) are retained; all **1,114,112** codepoints now agree. Frozen, official, path, sanitizer, and audit outputs are linked alongside this report and the complete [gate archive](zig-v6-gates.tar.gz) retains all 112 results/logs.

The search tested and rejected several plausible architectures:

- counting literal matches first and preallocating the result list (**0.826×**) or using `memmem` for repeated short Unicode searches (**0.851×**) both lose to a one-pass Unicode search plus an allocation-aware append (**1.064×** pilot);
- checking a negative-lookbehind class before every possible start adds work and slows filenames/units;
- replacing the small-stack matcher boundary with heap growth removes a page probe but is neutral/slower on short calls;
- using Python's Unicode search for all literal searches makes medium/long inputs dramatically slower (29 holdout losses in each long-hit/miss family), so the existing long-scan path is preserved;
- a cached mode-object shortcut is neutral and removed.

All 46 pilot/raw results, the initial prefix-choice mismatch and fix, profiles, and rejected paths are in the [pilot archive](zig-v6-pilots.tar.gz), SHA-256 `ab8af40a8bcda0a8ac5b8a2673ac3183188a2c846bf951c06fc0d1b3f21a9e87`. The gate archive SHA-256 is `fbbe1ac0c039798a91c861dbcaab443ea8be2322810f95d5e9f400a72c1fedf8`.

## Reproduce

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_zig_probe.sh
PYTHONPATH=. "$PY" tools/zig_v6_paths_probe.py --module re --seeded-cases 4096 --output /tmp/zig-self.json
PYTHONPATH=. "$PY" tools/zig_v6_paths_probe.py --module rebar --seeded-cases 8192 --output /tmp/zig-paths.json
PYTHONPATH=. "$PY" tools/perf_v6.py verify --module rebar --output /tmp/zig-performance-check.json
PYTHONPATH=. "$PY" tools/zig_perf_v6.py self-test
PYTHONPATH=. "$PY" tools/zig_perf_v6.py measure --output /tmp/zig-raw.jsonl
PYTHONPATH=. "$PY" tools/zig_perf_v6.py analyze --input /tmp/zig-raw.jsonl --output /tmp/zig-summary.json
PYTHONPATH=. "$PY" tools/zig_merge_v6.py --initial performance/v6/evidence/initial-summary.json.gz --zig /tmp/zig-summary.json --output /tmp/zig-combined.json
PYTHONPATH=. "$PY" tools/performance_v6_charts.py --summary /tmp/zig-combined.json --prefix /tmp/zig

# Optional executor counters; rebuild the release matcher before timing.
PYTHON="$PY" sh tools/build_zig_profile_v6.sh
PYTHONPATH=. "$PY" tools/zig_profile_v6.py --output /tmp/zig-profile.json --category deeper-file-names --category deeper-money-units --category deeper-unicode-word-lines --category deeper-shared-prefix-alternatives --category deeper-dense-literal-findall
PYTHON="$PY" sh tools/build_zig_probe.sh
```
