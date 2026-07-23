# Rejected C engine: full Unicode case matching differs from Python

The proposed C implementation fixes the previously recorded repeat and recursion failures and passes every standalone correctness, safety, and independence check. It is nevertheless **rejected**: the original full correctness campaign passes **21 of its 22 stages** and fails the final full-Unicode stage. The candidate is not a fully compatible Python `re` replacement and is not promoted.

## Exact failed campaign

The pinned reference is stable CPython **3.14.6**. The complete frozen campaign was invoked exactly once with the matching, public-object, and native-code evidence from this precise candidate:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  tools/rust_v8_multi_candidate_campaign.py \
  --module candidates.vm_candidate \
  --edge-oracle candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-16.json.gz \
  --deep-proof candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-16.json.gz \
  --output candidates/evidence/rust-v8-vm-stage-16-sealed-campaign.json \
  --memory-mib 2048
```

The genuine exit is **1**. The success output above was **not** created. The [complete first-run failure report](rust-v8-vm-stage-16-sealed-campaign-failure.json) preserves the actual parent traceback, the frozen child's original **3,000-character** clipped error output, all **nine** complete observable mismatch records, the initial partial mismatch, the actual command, and the hashes of every source, native library, and prerequisite.

The final suite normally contains **4,494,555** frozen Unicode comparisons. That figure is the intended full denominator, **not** the number completed by the failed run. The exact number actually completed and the total number of mismatches are **NOT MEASURED**: the unchanged fail-fast worker removed its temporary output after failing. No second campaign was run.

## Actually preserved failures

Every complete error record below comes directly from the failed original worker. Each is an `IGNORECASE` singleton character range that matches in pinned Python but incorrectly does not match in the proposed C engine.

| Pattern code point | Input code point | Python | Proposed C |
| --- | --- | --- | --- |
| `U+1FBE` | `U+0399` | Match | No match |
| `U+1FBE` | `U+03B9` | Match | No match |
| `U+0390` | `U+1FD3` | Match | No match |
| `U+1FD3` | `U+0390` | Match | No match |
| `U+03B0` | `U+1FE3` | Match | No match |
| `U+1FE3` | `U+03B0` | Match | No match |
| `U+03B2` | `U+03D0` | Match | No match |
| `U+03D0` | `U+0392` | Match | No match |
| `U+03D0` | `U+03B2` | Match | No match |

The clipped output also retains part of a `U+0345` record. A partial record is not counted as a complete mismatch. Python's extra Unicode case-equivalence components must be implemented in the C engine itself; importing Python's `re`, wrapping another regex package, relaxing the frozen oracle, or disabling a search filter is not an acceptable fix.

## Independently verified passing checks

The same exact rejected source passes these unchanged frozen standalone checks:

| Check | Actual result | Evidence |
| --- | ---: | --- |
| Deeper recursion, overflow, and changed recursion limits | 348/348 | [Complete deeper safety report](rust-v8-vm-stage-16-depth-safety.json) |
| Crashes, malformed input, Unicode, and allocation safety | 254/254 | [Complete isolated safety report](rust-v8-vm-stage-16-isolated-safety.json) |
| Extended Python behavior | 72,248/72,248 | [Complete extended report](rust-v8-vm-stage-16-extended-path-failures.json.gz) |
| Matching and edge cases | 223,198/223,198 | [Complete matching report](rust-v8-edge-oracle-vm-deep-stage-16.json.gz) |
| Independently generated patterns | 20,480/20,480 | [Complete parser report](rust-v7-grammar-vm-v8-deep-stage-16.json.gz) |
| Public objects and lifetimes | 393/393 | [Complete public-contract report](../audits/RUST-V8-DEEP-CONTRACT-C-STAGE-16.json.gz) |
| Tracing, iterators, and unusual arguments | 479/479 | [Complete observability report](rust-v8-observability-vm-qualified-stage-16.json.gz) |
| Replacements and callbacks | 8,862/8,862 | [Complete replacement report](rust-v8-replacement-vm-stage-16.json.gz) |
| Deeper replacements and callbacks | 11,266/11,266 | [Complete deep replacement report](rust-v8-replacement-vm-deep-stage-16.json.gz) |

The public-contract report explicitly retains **one** implementation-private garbage-collection topology difference under the original named private waiver. It records **zero public mismatches**, zero standard-library self-oracle failures, and all original forbidden-engine controls.

The [actual passing four-family independence audit](../audits/FROM-SCRATCH-AUDIT-C-STAGE-16-PASS.json) verifies all four separately written parsing, compilation, and matching pipelines; all five actually loaded native libraries; and all **76** original anti-delegation controls. The C candidate does not import `re`, `_sre`, `sys`, a third-party regex package, or another candidate.

## Lossless source and evidence hashes

The [complete rejected source patch](C-STAGE-16-REJECTED-UNICODE.patch) is byte-for-byte identical to the complete native-C and Python candidate changes against the committed production engine. Verified SHA-256 fingerprints are:

```text
GOAL.md
e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62

candidates/vm_candidate.py
0c49f88e9643f946caf4a46fd5a84d82ba1321790d7b46e5901acea8b0150c75

candidates/_vm_native.c
b210f45a81454c1e8cc342f14fafeb5ebc8c3ebed66a70d590445842f7d3d00f

candidates/_vm_native.cpython-314-x86_64-linux-gnu.so
fb609951744c926a2ea0845bb4492fb5e2eaa39b1d1f3ecf9fd81c0692eeaf8e

candidates/evidence/C-STAGE-16-REJECTED-UNICODE.patch
dbeca65f78d77567a4706c7f1008f0d7e26d9ecdb7b8b2a06daa4e654e7c7c66

candidates/evidence/rust-v8-vm-stage-16-sealed-campaign-failure.json
2c18c3f87133fc528a6cef35eec682932d19dbe2f27a7b4af1b0da70f873e3b8

candidates/audits/FROM-SCRATCH-AUDIT-C-STAGE-16-PASS.json
6ed1679f3bfb1cbb2bbc0fe39df8dd639f112a3555c813f7d1ab658046af6875
```

The sealed **24,576-case final performance benchmark** was not opened, generated, or run. C final speed, memory, ranking, and complete Unicode mismatch totals remain **NOT MEASURED**.
