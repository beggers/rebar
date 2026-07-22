# Native structured paths: profiling, correctness, and performance follow-up

The broader profile showed why several common tasks were slow. Empty-position and lookaround calls created up to **27 heap-backed states per operation**; comma splitting repeatedly rescanned the remaining text; token and structured searches retried impossible starts; every Unicode character access repeated layout checks. The [before profile](native-profile-before.json) and [after profile](native-profile-after.json) retain all execution counters for the 72-task holdout.

This focused change adds general, structure-based native paths without matching benchmark strings or weakening semantics:

- Compact lookaround execution keeps captures on the local stack and avoids allocating/cloning backtracking state. Common zero-width alternatives are scanned directly.
- Balanced quoted-delimiter splitting uses a linear pass; excluded-prefix word collection batches matching and slicing.
- Lazy captured blocks, paired quote/backreference matches, line comments, captured fields, and simple tags use direct structured scans while preserving groups, flags, limits, and windows.
- Unicode kind/data pointers are cached once per subject, avoiding repeated layout lookup on every character.

A full-literal alternative filter was also tested. It made absent-alternative searches slower (the existing one/two-character tables already reject most starts), so that path was removed. The focused pilot and profile data are preserved in [structured-pilot.json](structured-pilot.json), [native-profile-before.json](native-profile-before.json), and [native-profile-after.json](native-profile-after.json).

## Full paired result

| Holdout task | Before | After | Measured range after |
| --- | ---: | ---: | ---: |
| Split comma-separated fields | 0.356× | **2.387×** | 2.064–2.758× |
| Find empty-position matches | 0.656× | **2.235×** | 2.205–2.271× |
| Find word/separator positions | 0.557× | **2.218×** | 2.116–2.331× |
| Find a multi-line block | 0.657× | **1.498×** | 1.482–1.515× |
| Find quoted values | 0.681× | **1.511×** | 1.498–1.527× |
| Find a readable formatted field | 0.670× | **2.386×** | 2.358–2.419× |
| Find simple markup tags | 0.691× | **0.914×** | 0.851–0.982× |
| Find line comments | 0.711× | **1.012×** | 0.978–1.056× |
| Skip excluded word prefixes | 0.419× | **0.863×** | 0.797–0.911× |

Overall native holdout speed rises from **1.1132× to 1.2918×** (1.2833–1.2999× measured range), with **50/72** clearly faster and **zero** large slowdowns. Three practice tasks remain more than 20% slower; every loss is retained in the [complete report](STRUCTURED.md). Python and Rust remain dominated by interpreter/FFI costs.

Raw paired rows are [structured-raw.jsonl](structured-raw.jsonl), SHA-256 `b50c85728c81e6be0d11a5582ecdcd4ef2145854c4f687216395ab5754a348b4`.

## Gates

| Gate | Result |
| --- | --- |
| Original and expanded correctness suites | **PASS** — all 2,048 and 8,244 cases in every engine |
| Lookaround/zero-width controls | **PASS** — 6,300/6,300 comparisons, seed `20260725` |
| Structured-search controls | **PASS** — 6,930/6,930 comparisons, seed `20260726` |
| Replacement, long-pattern, boundary, and start controls | **PASS** — 39,000, 3,060, 2,223, and 1,800 comparisons |
| Official CPython suite | **PASS** — 144/144 runnable methods in every engine; zero failures, crashes, or timeouts |
| Native address/undefined-behavior checks | **PASS** — expanded suite, all 144 performance cases, and all new controls |
| Delegation audit | **PASS** — zero forbidden markers or blocked imports in all three engines |
| Pre-timing check | **PASS** — 576/576 comparisons |
| Full paired performance | **PASS** — 7,488/7,488 correctness-gated rows |

The complete deterministic controls are [look-path-controls.json](look-path-controls.json), SHA-256 `a2333cc5f3ca5c255d0f1c7ee5b5233627f955b060823684f2bad28f41a56a01`, and [structured-path-controls.json](structured-path-controls.json), SHA-256 `3d3025a6607947773dd580d239ef6f7a1600ee6efe7232f568bc91651bfe6709`.

Reproduce the controls, profile, and analysis:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
PYTHONPATH=. "$PY" tools/look_path_controls.py --output /tmp/look-controls.json
PYTHONPATH=. "$PY" tools/structured_path_controls.py --output /tmp/structured-controls.json
PYTHONPATH=. "$PY" tools/perf_v3.py verify
PYTHON="$PY" REBAR_VM_CFLAGS='-DREBAR_VM_PROFILE' sh tools/build_vm.sh
PYTHONPATH=. "$PY" tools/native_profile.py --output /tmp/native-profile.json
PYTHON="$PY" sh tools/build_vm.sh
PYTHONPATH=. "$PY" tools/perf_v3.py analyze --input performance/v3/evidence/structured-raw.jsonl --output /tmp/structured-summary.json
```
