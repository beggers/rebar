# Unicode-safe public Python regex speed comparison

Status: **completed and independently verified**. The
[public results](RESULTS.md) preserve all original observations and
slowdowns. This remains a public development comparison, not the one-use
final test and not a winner.

## What is compared

Compare unmodified CPython **3.14.6** with three independently written
regular-expression engines: Rust, C, and Zig. Every engine runs in its own
continuously guarded process. No candidate may call Python's regex engine,
an external regex package, or another candidate.

The previous [8,192-case comparison](../postfinal-public-v4/RESULTS.md)
stopped when its benchmark communication could not carry a lone Unicode
surrogate. This version preserves its frozen workload, case weights, random
seeds, operations, trials, candidates, and correctness checks. Its only
communication change is ASCII-safe JSON, which transports the original
Python strings without losing Unicode information. The failed version's
manifest and all **310,700** original timing rows remain unchanged and are
authenticated in this new manifest.

The comparison contains **8,192** equally weighted public cases across
**260** workload categories:

| Python operation | Cases |
| --- | ---: |
| `compile` | 210 |
| `escape` | 161 |
| `findall` | 2,040 |
| `finditer` | 2,041 |
| `fullmatch` | 358 |
| `match` | 229 |
| Match-object access | 241 |
| `scanner` | 427 |
| `search` | 1,057 |
| `split` | 451 |
| `sub` | 447 |
| `subn` | 530 |
| Total | 8,192 |

Each case has **four** warmups and **13** counterbalanced paired trials
for Python and all three candidates. A complete comparison must contain:

- **425,984** original timing observations.
- **1,277,952** before, during, and after correctness checks.
- **24,579** reproducible 95% confidence intervals.
- **2,000** predeclared resamples per confidence interval.
- **65,544** worker, module, and native-library integrity checks.
- Every workload, every candidate, and every slowdown exceeding **20%**.

The overall result is the equally weighted geometric mean relative to
standard Python. **1×** means the same speed; higher means faster. Worker
startup, communication, answer comparison, and memory sampling are outside
the timed Python operation. Report Python-visible temporary allocations
separately from worker resident and high-water memory; neither is a complete
measure of native allocations.

## Correctness before timing

The manifest authenticates all **12** current-source proofs across the
Rust, C, and Zig implementations. Each engine passes:

- **223,198** matching, parsing, Unicode, and object checks.
- **393** independently tested public object behaviors.
- **479** callback, argument, buffer, and scanner checks.
- The complete **22-stage** compatibility campaign.
- **4,494,555** full-Unicode comparisons.

The expanded public oracle contributes **1,179,648** comparisons against
Python with zero differences. The original **76-control** source and
native-library audit and the separate **32-control** isolation audit both
pass. All five loaded native libraries are independently fingerprinted.
The controller never imports a production engine.

## Frozen inputs

| Input | SHA-256 |
| --- | --- |
| Public comparison manifest | `c9950c87079ccc1909ba4470ed573b08afe1f275b85a8932cbfe83b547b24f96` |
| Unicode-safe runner | `f4294a3b5434f43a92970635a958cf3b39db0eb926adef50e242ac0f6b9a1d22` |
| Six-chart renderer | `7684cf5d3696ce97699406ae5b6451d47482ad707c1b74261972a1f2bfd39196` |
| Preserved failed comparison manifest | `15789a8ab6ab35ea97b657fed2ae4be0e944da6300067bc7cb3e8222c7c5ea55` |
| Preserved failed comparison timing stream | `4132e485b605f924fbc4edf09324987f09361f0562a9884fd0ceb06e09544f8a` |
| Original frozen correctness suite | `744876e5b8409b8d49982ccfb61d93a99f3e2d4fd64d0543b29b831bd26796a0` |
| Current versioned correctness runner | `477c3f7e9955a9207b9345fc281705b6d643446b5d5c933009fa22a64b8d44ce` |
| All-engine public correctness proof | `a7b6aea6e612de511990d446c8572aa4e1d3094f28ddd2b9f012b1083e73f208` |

The selection, trial-order, and confidence-interval random seeds remain
`2026072404`, `2026072405`, and `2026072406`. The complete operation and
category lists, every candidate fingerprint, all **12** independent
correctness reports, and the exact preserved predecessor are in
[manifest.json](manifest.json).

## Reproduce the frozen state

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.postfinal_public_practice_v5 self-test

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/postfinal_public_practice_charts_v5.py --self-test

sha256sum performance/postfinal-public-v5/manifest.json \
  tools/postfinal_public_practice_v5.py \
  tools/postfinal_public_practice_charts_v5.py
```

The separate **65,536-case** one-use holdout remains unopened. Its
[four-channel adapter](../postfinal-fresh-holdout-v1/ADAPTER-AUDIT.md) is
independently verified on public cases; the one-use production controller is
**NOT YET INTEGRATED**. Final performance, final memory, and a drop-in
replacement winner are **NOT MEASURED**.
