# Rejected C engine: two inverted matching windows differ from Python

The proposed native C engine implements the complete pinned Python Unicode case-equivalence rules and genuinely completes all **4,494,555** frozen Unicode checks. Every full-plane Unicode partition matches Python exactly. The implementation is nevertheless **rejected** because that same unchanged worker exposes **two** incorrect empty-match results when the requested matching window has `pos > endpos`.

## Reproduce the one original failure

The pinned reference is CPython **3.14.6**. The original, complete Unicode correctness worker was invoked exactly once, using the frozen seed, every Unicode code point, and the required **1,024** seeded cases:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  tools/rust_unicode_probe.py \
  --module candidates.vm_candidate \
  --seed 2026072302 \
  --membership-stride 1 \
  --seeded-cases 1024 \
  --output candidates/evidence/rust-v8-vm-stage-17-unicode-fullplane.json
```

The actual exit is **1**. The [complete original worker report](rust-v8-vm-stage-17-unicode-fullplane.json) records exactly **4,494,555** completed checks, **two** mismatches, seed `2026072302`, a full-plane stride of **1**, and exactly **1,024** seeded cases. Unlike the previous campaign's clipped failure, both the full denominator and complete mismatch records are actually observed and preserved. The worker was not repeated.

## The two actual mismatches

Both records use frozen case `seeded-332`:

```text
pattern: (?:\w|\W)*?
flags:   ASCII | IGNORECASE (258)
subject: " "
pos:     1
endpos:  0
```

| Original Python operation | Python | Proposed C |
| --- | --- | --- |
| `match` | No match | Empty match at `(1, 1)` |
| `scanner.match` | No match | Empty match at `(1, 1)` |

Python permits empty matches when the requested window is valid, including `pos == endpos`. The specific defect is that the C engine also returns an empty match after an **inverted** window, `pos > endpos`. The failure must be fixed in the independently owned matcher; normalizing, weakening, filtering, or removing the frozen case would not constitute a fix.

## Unicode comparisons that actually pass

The same failed worker fully completes all four partitions. Each checks **1,114,112 Unicode code points** and reproduces Python's exact frozen SHA-256 observation:

| Full-plane partition | Incorrect observations | Verified Python and C observation SHA-256 |
| --- | ---: | --- |
| Unicode character categories | 0 | `c6bb3b50278d370bd288a040d07976730f92fe4475c947a7ac8e4158cdda6ec5` |
| ASCII character categories | 0 | `9888738c9f6e04a0b5e86300a648cf042531945a2761e7a666c2a407b5d6a339` |
| Unicode case-insensitive ranges | 0 | `b9394ae400bc6c32867be06a02363c740cc670bbcfd89668949a422ad93d8f1a` |
| ASCII case-insensitive ranges | 0 | `5084555e7d9ccfbbc9db1ea1e85b1d28820120a085739322159fe3bf79a7a554` |

All **50** Python extra-case keys, all **56** directed case-equivalence links, all **280** associated extra-case controls, and all **1,455** complete case-equivalence checks pass. These results belong only to the exact source and native library fingerprinted below.

## Exact rejected source

The [complete rejected source patch](C-STAGE-17-REJECTED-WINDOW.patch) preserves the actual native C and Python candidate changes byte-for-byte against the committed C implementation. SHA-256 fingerprints:

```text
GOAL.md
e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62

candidates/vm_candidate.py
0c49f88e9643f946caf4a46fd5a84d82ba1321790d7b46e5901acea8b0150c75

candidates/_vm_native.c
420a2e5e7e47d02d5433eceeadce8de02205d780a788be7c35c3c2759b6ac1e5

candidates/_vm_native.cpython-314-x86_64-linux-gnu.so
32981e9f5b3ac7cfef2da487b881824c16a09772254ac6b8e14b507a056a040c

candidates/evidence/C-STAGE-17-REJECTED-WINDOW.patch
e2e6648362cafa52c885495456518d19acf1c5c3f22e804de0e9c25377a375ad

tools/rust_unicode_probe.py
8d37556df43f3390e0ae42b5aae88f13c86de184daa2d6ada76487cb320752c5

candidates/evidence/rust-v8-vm-stage-17-unicode-fullplane.json
9a6f61f36d654e9bb40ac83a30ce56f6eadf18db9b2a90973173131e761c5731
```

For this exact Stage-17 source, a fresh independence audit, the other standalone correctness suites, and a complete 22-stage campaign were **NOT RUN**. It is not valid to attach the Stage-16 source-bound audit or proofs to this changed native library. The sealed **24,576-case** final performance benchmark remains unopened; speed, memory, ranking, and final-test results are **NOT MEASURED**.
