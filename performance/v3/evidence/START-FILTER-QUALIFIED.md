# Native start and class filters: correctness and performance follow-up

The broader profile showed that alternative-heavy searches entered the full backtracker at many impossible positions and that repeated character classes rescanned their members for every ASCII character. This focused experiment adds three general native paths without recognizing benchmark strings or weakening semantics:

- A lazy one-character start table follows alternatives, optional prefixes, assertions, groups, and repeats. Alternative-leading programs also receive a compact two-character table, allowing an absent-word search to skip almost every impossible position before backtracking. Non-ASCII input remains on the safe general path.
- Each character class lazily caches ASCII membership for normal, ASCII-case-insensitive, and Unicode-case-insensitive modes. Unicode/special equivalences still use the full matcher.
- Safe greedy single-character repeats record their no-backtracking decision during compilation, avoiding repeated suffix-choice analysis while preserving specialized collection paths and greedy results.

The full paired holdout confirms the gains:

| Holdout task | Native speed before | Native speed after | Traced-memory ratio after |
| --- | ---: | ---: | ---: |
| Search for one of many words (absent) | 0.074× | **0.748×** | 0.00× |
| Read request lines from a log | 0.271× | **0.833×** | 0.33× |
| Check a version string | 0.796× | **1.095×** | 0.06× |
| Check a structured repeated path | 0.760× | **1.058×** | 0.64× |
| Find unescaped tagged words | 0.613× | **1.067×** | 0.10× |

Overall native holdout speed improves from **0.9735× to 1.0967×** (1.0897–1.1037× measured range), with **37/72** clearly faster and **12** remaining large slowdowns. Two cold-compilation tasks use more traced memory (1.91× and 1.67×); this is retained in the memory graph. The [complete result](START-FILTER.md) retains every case, confidence range, and slowdown.

## Gate results

| Gate | Result |
| --- | --- |
| Original seeded oracle | **PASS** — 2,048/2,048 for native, Python, and Rust |
| Expanded seeded oracle | **PASS** — 8,244/8,244 for native, Python, and Rust |
| Broader pre-timing check | **PASS** — 576/576 comparisons |
| Full official CPython suite | **PASS** — 144/144 runnable methods in every engine; zero failures, crashes, or timeouts |
| Start/class differential controls | **PASS** — 1,800/1,800 comparisons, seed `20260723` |
| Boundary and long-pattern controls | **PASS** — 2,223/2,223 and 3,060/3,060 comparisons |
| Native address/undefined-behavior checks | **PASS** — expanded oracle, all 144 tasks, and all start/class controls |
| Rust address/overflow checks | **PASS** — expanded oracle and all 144 tasks |
| Delegation audit | **PASS** — zero forbidden markers or blocked import attempts in all three engines |
| Paired performance rows | **PASS** — 7,488/7,488 correctness-gated rows |

The complete deterministic control output is [start-filter-controls.json](start-filter-controls.json), SHA-256 `476b1d64244159595f0c51d50c7eae2f08b11069cb6b09f2826c285f18c08281`. Raw paired rows are [start-filter-raw.jsonl](start-filter-raw.jsonl), SHA-256 `84162c86b6565be74aef3812db670450d517deb239652f1d16963a0394544b6b`.

Reproduce the checks and analysis:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
RUSTFLAGS='-D warnings' sh tools/build_rust.sh
PYTHONPATH=. "$PY" tools/start_filter_controls.py --output /tmp/start-filter-controls.json
PYTHONPATH=. "$PY" tools/perf_v3.py verify
PYTHONPATH=. "$PY" tools/perf_v3.py analyze --input performance/v3/evidence/start-filter-raw.jsonl --output /tmp/start-filter-summary.json
```
