# C: skip impossible starts in single-byte alternatives

**Outcome: all 22 compatibility stages passed; fastest in this public practice run; not a final winner.** The independently implemented C engine was **1.334067668×** as fast as Python on **624 public practice cases**, with a 95% confidence interval of **1.285686468–1.388670389×**. This does not meet the final **1.5×** requirement and is not a result from the separate **24,576-case** hidden benchmark.

| Implementation | Speed relative to Python | 95% confidence interval | Clearly faster cases | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| C | 1.334067668× | 1.285686468–1.388670389× | 441/624 | 46/624 |
| Zig | 1.256810915× | 1.208964948–1.305218283× | 341/624 | 96/624 |
| Rust | 1.150044166× | 1.104190357–1.196092337× | 260/624 | 114/624 |

Here **1× means Python's unmodified `re`**. Each confidence interval is a paired comparison against Python **within this one public practice run**. All **256** substantial slowdowns are retained: **46 C**, **96 Zig**, and **114 Rust**. “More than 20% slower” means that a case took strictly more than **1.2 times** Python's time.

C was clearly faster on **441/624** practice cases, meeting the public-practice **60%** case threshold, but **1.334067668× is below 1.5×**. Public practice cannot establish success or select a winner for an unopened final benchmark.

## What changed

The owned C engine already computes a table of the 256 possible first bytes that a compiled pattern can accept. When the first operation branches between alternatives and that table accepts **exactly one byte**, the engine can safely use C's `memchr` to skip positions containing any other byte. It still invokes the complete original regular-expression matcher at each plausible position.

The single accepted byte is stored as its numeric value **plus one**. This distinguishes “no unique byte” (`0`) from the valid byte `0x00` (`1`) and correctly represents `0xff` (`256`). The matching engine is allocated with zero-initialized memory, and the existing first-byte table is computed once before the shortcut is considered. Nullable branches, unknown instructions, lookarounds, anchors, unrestricted alternatives, character classes, and depth-limited analysis keep the existing conservative acceptance behavior. If a unique start is not proven, the new shortcut is not used.

The scan is restricted to an actual alternative instruction and actual contiguous **bytes, byte arrays, contiguous buffer or memory-view inputs, or one-byte Unicode**. Two-byte and four-byte Unicode continue through the original character-by-character matcher. The scan never crosses either the final valid start or the Python search window:

```c
Py_ssize_t scan_end = last_start < endpos
    ? last_start + 1 : endpos;
const unsigned char *pivot = memchr(
    data + start,
    (unsigned char)(vm->start_singleton - 1),
    (size_t)(scan_end - start)
);
if (!pivot) {
    start = scan_end - 1;
    continue;
}
```

The existing loop has already established `start <= last_start` and `start < endpos`, so the scan length is nonnegative and its checked branch cannot overflow. When no accepted byte remains, setting `start = scan_end - 1` lets the existing loop advance to `endpos`, preserving the possible **zero-width match at the end of the window**. A found byte remains subject to the original pair and triple filters, ordered backtracking, complete matching, captures, callbacks, scanners, newline rules, and exact error handling. The shortcut neither wraps an external package nor calls Python's regular-expression matcher, Rust, or Zig.

| C production artifact | SHA-256 |
| --- | --- |
| Independent C engine and bridge source | `2253ddd8608a19a06f25ed41251729365ecb1e25f6829f710cdcb858b10c4e0c` |
| Actually loaded native C engine | `f6458cb4bf190f042e7d417a40020d2d58cebcb39671fda7352aab9725a7f633` |
| Unchanged from-scratch C Python interface | `91d848e2627f19e552fef19b9943eb3e265e25537934128875645bab63cf7b80` |

## Correctness was established before timing

Pinned CPython **3.14.6** was the reference. Each fresh correctness artifact binds to the actual Stage 21 C source, loaded native engine, and public interface:

- [223,198 frozen matching comparisons across 49 categories](../../../candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-21-singleton-split-memchr.json.gz), with zero mismatches; compressed SHA-256 `a5214e9f0144b4549f8134d7df9bec21975f5debe9b6a392f47dd1097baec314`.
- [393 detailed Python object, method, descriptor, and error checks](../../../candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-21-SINGLETON-SPLIT-MEMCHR.json.gz), with zero public mismatches; compressed SHA-256 `907d6c684cd5e7161ef27b167f1d3bdd18243dff61bad4d5586ff3ef5b2d13cd`.
- [479 observable Python-behavior checks](../../../candidates/evidence/rust-v8-observability-vm-qualified-stage-21-singleton-split-memchr.json.gz), including **479** reference self-checks and **34** binding checks, with zero failures; compressed SHA-256 `0a975f63d3a5e20e317e3dc08c1324ce95a8ed371923b53c18e65f49c6414b8a`.
- [All 22 fresh sealed correctness stages](../../../candidates/evidence/rust-v8-vm-stage-21-singleton-split-memchr-sealed-campaign.json), including Python's own tests, callbacks, isolated crash and recursion checks, and **4,494,555 full-Unicode comparisons**; SHA-256 `a29b540e01fc9f565e01e5cc62af14db30b38d9bacbaf55e4950e95b17c7ea40`.
- [The independent from-scratch and no-delegation audit](../../../candidates/audits/FROM-SCRATCH-AUDIT.json), confirming **three independent engine families** and **four separate implementation pipelines**; SHA-256 `a790fe1a75c8748df7f8bb6f1e39d0be841636055358aaee94db0aa35523f326`.

The correctness campaign records performance **NOT MEASURED** and final-benchmark access **false**. The subsequent public practice run recorded **zero correctness failures**. The [already-qualified Rust engine](../../../candidates/evidence/rust-v8-rust-owned-capture-init-hoist-sealed-campaign.json), SHA-256 `9ddbab81b16f0440ca19bffb8a539ea08d4a7ff33606ee3019eaf85977c2249a`, and [already-qualified Zig engine](../../../candidates/evidence/rust-v8-zig-stage-13-sealed-campaign.json), SHA-256 `4ba7cb9c45a70b747cc0a6eb721f6bb51081157f527d1bf5e578e603715ae5dc`, remain separate and unchanged.

## Every C operation, including the losses

The practice measurement covers **12 regular-expression operations**, **624 cases per candidate**, **7 paired trials** per case, **4 warmups**, **499 predetermined confidence resamples**, **17,472 original timing rows**, **52,416 correctness checks**, and all **1,872 candidate-by-case outcomes**.

| C operation | Public cases | Clearly faster | More than 20% slower |
| --- | ---: | ---: | ---: |
| Compile a pattern | 48 | 42 | 0 |
| Escape pattern text | 48 | 48 | 0 |
| Find all matches | 80 | 42 | 16 |
| Iterate over matches | 67 | 40 | 9 |
| Match a complete string | 47 | 38 | 6 |
| Match at the start | 48 | 45 | 1 |
| Inspect match objects | 48 | 6 | 1 |
| Scanner | 48 | 20 | 9 |
| Search | 48 | 33 | 4 |
| Split | 47 | 41 | 0 |
| Replace matches | 48 | 44 | 0 |
| Replace and count | 47 | 42 | 0 |
| **All public C cases** | **624** | **441** | **46** |

In particular, all **46 C slowdowns** remain visible, including **16 find-all**, **9 iteration**, **9 scanner**, **6 full-match**, **4 search**, and **2 match or match-object** cases. The evidence identifies which operations regressed; it does not prove the cause of each slowdown or show that the shortcut caused a cross-run improvement.

- [Every public-practice version-nine case, interval, candidate ranking, and slowdown](three-qualified-engines-public-practice-v9-summary.json); SHA-256 `e0140380d6b3026e6195f27d3188e87e6d646b08d0e632c5e9eda38674e616ed`.
- [Every original same-run public-practice timing observation](three-qualified-engines-public-practice-v9-raw.jsonl.gz); compressed SHA-256 `004ef3e8ddb1bd81f88c6742843e3d5bc7c29ed4bfea120d40d3d28fdae4a651`; independently verified uncompressed SHA-256 `493f3d8ec3c0a030891306b71353714e7165d60a5ec12e629fa0bfcfd5558200`.

**The public practice files above are in `performance/v7/evidence/`. Their `v9` filenames designate the ninth public practice run. They are not the sealed `performance/v9` final benchmark, do not open it, and do not report its cases.**

## Preserve previous results and limitations

The [previous public-practice version-eight result](three-qualified-engines-public-practice-v8-summary.json), SHA-256 `77d3aa8ac970e126d11c9e9aad832f480670aceda1778966d16a4a768ca5a4c3`, remains unchanged. Its C implementation recorded **1.328250333×**, **441/624** clearly faster cases, and **46/624** substantial slowdowns; the three implementations recorded **261** substantial slowdowns in total. The separate new public run recorded **1.334067668×**, **441/624**, **46/624**, and **256** total slowdowns.

These are **different measurement runs**. There is no paired confidence interval between versions, no statistically demonstrated improvement over the previous C implementation, and no proof that bounded byte skipping caused their numerical difference. All preceding public practice runs and the [original C Stage 20 scanner experiment](C-STAGE-20-NATIVE-SCANNER-CMETHOD.md) remain historical evidence.

The existing [C independence-audit retry](C-STAGE-20-INDEPENDENCE-AUDIT-RETRY.md), [Rust verification incident](RUST-OWNED-MANDATORY-COMMON-PREFIX-VERIFIER-INCIDENTS.md), and [Zig reviewer-isolation incident](ZIG-STAGE-13-VERIFIER-INCIDENTS.md) remain preserved; none provides access to final benchmark cases.

Practice memory figures cover **Python-traced temporary allocations only**. Separate native allocation and independently isolated whole-process memory for each engine are **NOT MEASURED**.

Stage 21 C change: **CORRECTNESS QUALIFIED; NO PROVEN CROSS-RUN IMPROVEMENT**. Final **24,576-case** benchmark: **NOT MEASURED**. Final benchmark access: **NOT ACCESSED**. Final winner: **NOT SELECTED**.
