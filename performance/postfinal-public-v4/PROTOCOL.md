# Expanded public Python regex speed comparison

Status: **frozen and NOT MEASURED**. This is a public development benchmark,
not the fresh one-use holdout and not a final winner.

## What is compared

Compare unmodified CPython **3.14.6** with the separately authored Rust, C,
and Zig implementations. Each engine has its own persistent, permanently
guarded process. The controller never imports a candidate, and no candidate
can call Python's regex engine, an external regex library, or another
candidate.

The manifest freezes **8,192** distinct, equally weighted public cases from
**260** workload categories. Its exact operation counts are:

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

Each case has **four** warmups and **13** counterbalanced, paired trials for
all four engines. The complete result must contain:

- **425,984** original timing observations.
- **1,277,952** independent before, during, and after correctness checks.
- **24,579** reproducible 95% confidence intervals.
- **2,000** predeclared bootstrap samples per confidence interval.
- **65,544** worker, module, and native-library integrity checks.
- Every workload, every slowdown exceeding **20%**, and every candidate.

Overall speed is the equally weighted geometric mean relative to standard
Python. **1×** means parity, greater values are faster, and no candidate is
declared a winner without the separately specified final proof. Worker
setup, request transport, answer comparison, and memory sampling remain
outside the measured Python operation.

Report Python-visible traced allocations separately from dedicated worker
RSS and high-water observations. Neither measure is presented as exact
native allocation accounting.

## Correctness before timing

Timing refuses to start unless the exact frozen source and native-library
fingerprints still pass all **12** current Rust, C, and Zig proofs:

- **223,198** matching, Unicode, parser, and object checks per engine.
- **393** separate public-object checks per engine.
- **479** callback, argument, buffer, and scanner checks per engine.
- All **22** original compatibility stages and **4,494,555** full-Unicode
  comparisons per engine.

The freeze also independently verifies both the **76-control** source and
native audit and the **32-control** permanent no-delegation audit. Its
expanded public oracle binds all **1,179,648** Python comparisons, exactly
zero differences, the immutable original suite, and all five actual native
libraries.

## Frozen inputs

| Input | SHA-256 |
| --- | --- |
| Frozen public manifest | `15789a8ab6ab35ea97b657fed2ae4be0e944da6300067bc7cb3e8222c7c5ea55` |
| Public runner | `69d42bf668b60145520ac54873966ccf52c42d624bab809e484e239229256600` |
| Six-chart renderer | `85ea57956381d67b76517c04a7d99777c72f1ea9bbd52670637b52376d913e79` |
| Frozen original correctness suite | `744876e5b8409b8d49982ccfb61d93a99f3e2d4fd64d0543b29b831bd26796a0` |
| Current versioned correctness runner | `477c3f7e9955a9207b9345fc281705b6d643446b5d5c933009fa22a64b8d44ce` |
| All-engine correctness proof | `a7b6aea6e612de511990d446c8572aa4e1d3094f28ddd2b9f012b1083e73f208` |

Selection, order, and bootstrap seeds are respectively `2026072404`,
`2026072405`, and `2026072406`. The three candidate edge, object,
observability, and complete campaign hashes are frozen individually in
`manifest.json`.

## Reproduce the frozen state

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.postfinal_public_practice_v4 self-test

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/postfinal_public_practice_charts_v4.py --self-test

sha256sum performance/postfinal-public-v4/manifest.json \
  tools/postfinal_public_practice_v4.py \
  tools/postfinal_public_practice_charts_v4.py
```

The **65,536-case** one-use holdout is separate and remains unopened. Its
required four-channel isolated execution adapter is **NOT IMPLEMENTED**.
No speed, confidence interval, regression, memory measurement, generated
chart, holdout case, or replacement winner is implied by this freeze.
