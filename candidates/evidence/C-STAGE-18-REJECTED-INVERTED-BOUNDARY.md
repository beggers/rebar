# Rejected C engine: inverted windows can contain valid boundary matches

The proposed native C change rejects inverted search windows in its shared matcher. It corrects the two prior nullable-repeat failures, and its frozen Unicode worker actually completes all **4,494,555** checks. However, Python still permits certain genuine zero-width boundary matches after an inverted window. The proposed guard incorrectly rejects **six** of those matches and is therefore **rejected**.

## Exact one-shot correctness test

The pinned CPython **3.14.6** Unicode worker was invoked once, with its original full-plane and seeded settings:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  tools/rust_unicode_probe.py \
  --module candidates.vm_candidate \
  --seed 2026072302 \
  --membership-stride 1 \
  --seeded-cases 1024 \
  --output candidates/evidence/rust-v8-vm-stage-18-unicode-fullplane.json
```

The actual exit is **1**. The [complete unchanged worker report](rust-v8-vm-stage-18-unicode-fullplane.json) records **4,494,555 completed checks**, exactly **six** failures, the unchanged original seed, all **1,024** seeded patterns, and the full actual expected and observed result for each mismatch. No worker or full campaign was rerun.

## Every observed failure

All records use normal Unicode flags (`0`). The correct Python result is a zero-width match at `pos`; the candidate incorrectly returns no match.

| Frozen case | Pattern | Subject | `pos` | `endpos` | Failing operations |
| --- | --- | --- | ---: | ---: | --- |
| `seeded-110` | `\b|\B` | `_Ω` | 2 | 0 | `match`, `scanner.match` |
| `seeded-578` | `\b|\B` | `ВK\t` | 3 | 1 | `match`, `scanner.match` |
| `seeded-1016` | `(\b|\B)` | `в９K` | 3 | 1 | `match`, `scanner.match` |

The previous [two `seeded-332` nullable-repeat failures](C-STAGE-17-REJECTED-WINDOW.md) are no longer present. Nevertheless, replacing two real failures with six others is not compatibility. The next implementation must distinguish legitimate zero-width boundary assertions from nullable repeats without checking for frozen patterns, seed identifiers, or benchmark inputs.

## Unicode work that actually passes

The report confirms zero errors across all four complete **1,114,112-code-point** Unicode partitions. Each candidate observation hash exactly matches the pinned Python reference:

```text
unicode-categories
c6bb3b50278d370bd288a040d07976730f92fe4475c947a7ac8e4158cdda6ec5

ascii-categories
9888738c9f6e04a0b5e86300a648cf042531945a2761e7a666c2a407b5d6a339

unicode-ignorecase-ranges
b9394ae400bc6c32867be06a02363c740cc670bbcfd89668949a422ad93d8f1a

ascii-ignorecase-ranges
5084555e7d9ccfbbc9db1ea1e85b1d28820120a085739322159fe3bf79a7a554
```

All **50** Python extra-case keys, **56** extra-case links, **280** extra-case controls, **1,455** case-equivalence checks, and **34,816** seeded API checks are included. Exactly six seeded API observations fail.

## Rejected source and reproducible hashes

The [complete rejected source patch](C-STAGE-18-REJECTED-INVERTED-BOUNDARY.patch) preserves the full native-C and Python candidate diff byte-for-byte. Actual SHA-256 fingerprints:

```text
GOAL.md
e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62

candidates/vm_candidate.py
0c49f88e9643f946caf4a46fd5a84d82ba1321790d7b46e5901acea8b0150c75

candidates/_vm_native.c
2f7779573c98772cbc35402119de4e3f3f1547abba011b370224d3ee9b8b254f

candidates/_vm_native.cpython-314-x86_64-linux-gnu.so
d07304b2fcbf1b14049050807b5857a798fb398142b70cebcc0a7a5874289554

candidates/evidence/C-STAGE-18-REJECTED-INVERTED-BOUNDARY.patch
21606ba03bf59bd5e58f23d5320af1c9d55a725432e59c4d38c2b0c5877d9739

tools/rust_unicode_probe.py
8d37556df43f3390e0ae42b5aae88f13c86de184daa2d6ada76487cb320752c5

candidates/evidence/rust-v8-vm-stage-18-unicode-fullplane.json
adda292f23dc0490fc02eebb2064a09c415cd5e0d0fae20e0a4530bcc57d96d0
```

The Stage-18 independence audit, safety gates, replacement gates, and full campaign were **NOT RUN** for this rejected native binary. The sealed **24,576-case** final performance benchmark remains unopened; final speed, memory, and ranking are **NOT MEASURED**.
