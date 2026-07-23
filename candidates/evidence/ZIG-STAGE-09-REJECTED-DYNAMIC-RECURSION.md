# Rejected Zig engine: two legal deep patterns still crash

The independently implemented Zig proposal fixes every one of its **22 original crash and safety failures** in the frozen 254-case suite. Its true 348-case dynamic-recursion test nevertheless exposes **two native crashes**. The proposal is therefore **rejected** and is not promoted as a fully compatible Python `re` replacement.

## Original safety test genuinely passes

The exact Stage-09 source and the two owned native libraries were built once with the original repository script:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
PYTHON=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
REBAR_ZIG=/tmp/rebar-design-survey/zig-0.16.0/zig \
  sh tools/build_zig_probe.sh
```

The original isolated-safety worker was invoked exactly once:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  tools/rust_safety_probe.py \
  --module candidates.zig_candidate \
  --seed 2026072319 \
  --timeout 4 \
  --memory-mib 768 \
  --output candidates/evidence/rust-v8-zig-stage-09-isolated-safety.json
```

The genuine exit is **0**. The [complete first-run safety report](rust-v8-zig-stage-09-isolated-safety.json) records **254/254** passing cases, all **10** frozen categories, **zero** crashes, **zero** timeouts, and **zero** Python-reference failures. It includes a pattern with **1,024** capture groups, reversed Unicode ranges, possessive repeats, and malformed deeply nested input. The [original Stage-08 baseline](rust-v8-zig-stage-08-isolated-safety-baseline.json) and its **22** failures remain unchanged.

## The larger frozen depth test fails

Run the original deeper worker with the unchanged reference, bounds, and seed:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  tools/rust_depth_probe.py \
  --module candidates.zig_candidate \
  --seed 2026072323 \
  --timeout 5 \
  --memory-mib 768 \
  --output candidates/evidence/rust-v8-zig-stage-09-depth-safety.json
```

The genuine exit is **1**. The [complete original depth report](rust-v8-zig-stage-09-depth-safety.json) retains **all 348 cases**, all **nine** frozen categories, and both exact native `SIGSEGV` crashes:

| Frozen case | Pattern structure | Python recursion limit | Nesting | Python | Zig |
| --- | --- | ---: | ---: | --- | --- |
| `limit.4096.groups.-8` | Nested groups | 4,096 | 2,040 | Compiles | `SIGSEGV` |
| `limit.4096.lookahead.-8` | Nested lookahead | 4,096 | 2,040 | Compiles | `SIGSEGV` |

The run records **346 passing cases**, exactly **two** crashes, **zero** timeouts, and **zero** standard-library self-oracle failures. Both tested patterns are valid: rejecting them earlier or hardcoding a lower nesting limit would not reproduce Python.

The recursive Zig compiler currently reserves four fixed branch-optimization buffers in every compiler frame. Their combined **4,088-byte** footprint repeats at every nesting level; at depth **2,040**, those buffers alone require **8,339,520 bytes** of native stack. The next fix must relocate temporary branch storage out of the recursive compiler frame while preserving valid deep-pattern compilation, capture behavior, and the independently implemented matcher.

## Exact rejected source and reports

The [complete rejected source patch](ZIG-STAGE-09-REJECTED-DYNAMIC-RECURSION.patch) is byte-for-byte identical to the actual three Zig candidate source changes. Actual SHA-256 fingerprints:

```text
GOAL.md
e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62

candidates/zig/mini_regex.zig
cbfa9792a32f31fe65a8c8b7fdc4894dbfdcebae1409d7dd06080be23e219c87

candidates/zig/py_bridge.c
dfc791360c116fabca4b782fc506ea02b67ca77f84bb500d134b4cd1154300cb

candidates/zig_candidate.py
95a2010152099f2db61595927542b2f25a675eb72bd33125659969d804360239

candidates/_zig_probe.so
3f73ea60ecb6f254492318959007a7d1fcf7b4c2a55eeb6ee77570bb0280281f

candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so
411a337fef2c6a524bf58043923fb26470031e1ede5da5b8dfc67b08d06cf8bb

candidates/evidence/ZIG-STAGE-09-REJECTED-DYNAMIC-RECURSION.patch
8e9b19484dad6fc1076e4dfc0eb2ee2b16c440fac7cf9d7f20b399cb40245f42

candidates/evidence/rust-v8-zig-stage-09-isolated-safety.json
e7b6cd5c90a3539f767c622d640d6f38cfd7b088938a5acb2b3054a14e7e5e58

candidates/evidence/rust-v8-zig-stage-09-depth-safety.json
d71fc63e0077b772a4872bc3e6c2b71a16df4275da8f51f147354c1dd0542bf7
```

No fresh independence audit, full-Unicode suite, public-contract gate, or 22-stage campaign was run for this rejected source. The sealed **24,576-case final benchmark** remains unopened; all final speed and memory results are **NOT MEASURED**.
