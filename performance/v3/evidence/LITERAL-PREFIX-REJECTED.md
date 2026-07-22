# Rejected native literal-prefix experiment

This experiment taught the native search loop to jump to the next fixed starting word before entering the general matcher. The path was general (it followed groups and anchors, handled text and bytes, and never recognized benchmark inputs), and all correctness and delegation gates passed.

The full paired result did not justify keeping it. Native holdout speed falls from **1.0967× to 1.0908×** (1.0837–1.0977× measured range). It is clearly faster on **46/72** holdout tasks, but still has **12** large slowdowns. Useful gains are limited to a few tasks, while other searches become slower:

| Holdout task | Before | With prefix skipping |
| --- | ---: | ---: |
| Find line comments | 0.679× | **0.830×** |
| Find a word (present) | 1.115× | **1.170×** |
| Find a word (absent) | 1.173× | **1.217×** |
| Find a web or file address | 0.784× | **0.716×** |
| Search for one of many words (absent) | 0.748× | **0.697×** |

The optimization has been removed. The [complete result](LITERAL-PREFIX.md), [raw paired rows](literal-prefix-raw.jsonl), [summary](literal-prefix-summary.json), and generated charts preserve all 7,488 correctness-gated rows, confidence ranges, memory measurements, and regressions.

## Gates

- Original and expanded correctness suites: **10,292/10,292 pass** for the native engine.
- Long-pattern, boundary, and start-filter differential controls: **7,083/7,083 pass** across the applicable candidates.
- Broader pre-timing check: **576/576 pass** across stdlib and all three candidates.
- No-delegation audit: **pass** for all three candidates.
- Paired performance: **7,488/7,488 correctness-gated rows**.

Reproduce the analysis with the pinned interpreter:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONPATH=. "$PY" tools/perf_v3.py analyze \
  --input performance/v3/evidence/literal-prefix-raw.jsonl \
  --output /tmp/literal-prefix-summary.json
```
