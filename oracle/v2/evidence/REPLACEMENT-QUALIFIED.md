# Replacement behavior: correctness and performance follow-up

The frozen suites already covered ordinary replacements, but an additional differential check found a subtle compatibility gap: Python accepts a wrong-type replacement when the pattern finds nothing, while still validating malformed templates before matching. A caller can rely on this distinction.

The new matrix checks **13,000 cases per engine** and **39,000 comparisons** in total. It covers compiled/module `sub` and `subn`, `Match.expand`, positive/zero/negative limits, text, bytes, byte arrays and views, empty/no-match/prefix/multiple-match inputs, named/numbered groups, valid and invalid templates, non-callable invalid values, and callbacks returning text/bytes/buffers.

![Replacement compatibility before and after the fix](replacement-correctness.svg)

The first run exposes **19,088** mismatches: native C passes 6,616/13,000, Python and Rust each pass 6,648/13,000. The complete initial failures are retained in [replacement-initial.json](replacement-initial.json), SHA-256 `6b45a001ba954746a661d52cc010364b643a703c6a7470e55937015d505020ea`.

All three independent implementations now match CPython on **39,000/39,000** checks. The fixes preserve the important distinctions:

- Template syntax is interpreted using the replacement's type, not the subject's type; malformed templates and invalid group references fail even when there is no match.
- A valid but wrong-type literal is allowed when unused and raises the same join error only when a match is replaced. `Match.expand` reports mixed group/template types correctly.
- Byte-array/view replacements and callback results work for bytes, while text reports the original incompatible type and exact item position.
- Invalid non-callable values, unhashable replacements, empty prefixes, and error wording/order now agree with CPython.

The clean result is [replacement-controls.json](replacement-controls.json), SHA-256 `ec5e85f2251f9f7910f4b0eaebcd41e2fc86e42818ef04a53ff9cf74bf52a997`.

## Gates and full paired result

| Gate | Result |
| --- | --- |
| Original and expanded seeded suites | **PASS** — all 2,048 and 8,244 cases in each engine |
| Replacement matrix | **PASS** — 39,000/39,000 comparisons |
| Long-pattern, boundary, and start-filter controls | **PASS** — 3,060, 2,223, and 1,800 comparisons |
| Official CPython `re` suite | **PASS** — 144/144 runnable methods in each engine; zero failures, crashes, or timeouts |
| Native address/undefined-behavior check | **PASS** — expanded suite, all 144 performance cases, and all replacement checks |
| Delegation audit | **PASS** — zero forbidden markers or blocked imports in all three engines |
| Broader pre-timing check | **PASS** — 576/576 comparisons |
| Full paired performance | **PASS** — all 7,488 timing rows correctness-gated |

The [full broader result](../../../performance/v3/evidence/REPLACEMENT.md) reports native C at **1.1132×** overall on the 72-task holdout (1.1054–1.1206× measured range), clearly faster on **46/72**, with **11** large slowdowns. Rust and Python remain dominated by per-call conversion/execution costs. Every case, slowdown, memory result, and confidence range is retained; raw paired rows have SHA-256 `7409a9a2c4a36448285f956200bd83afc36966a81598e3401ed186a3cb7e3322`.

Reproduce the focused check and graph with the pinned interpreter:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
RUSTFLAGS='-D warnings' sh tools/build_rust.sh
PYTHONPATH=. "$PY" tools/replacement_controls.py \
  --output /tmp/replacement-controls.json \
  --initial oracle/v2/evidence/replacement-initial.json \
  --chart /tmp/replacement-correctness.svg
PYTHONPATH=. "$PY" tools/perf_v3.py verify
```
