# Rejected C engine: deeper recursion does not yet match Python

The proposed C engine is independently implemented, handles enormous repeated patterns, and passes every separately run matching, replacement, object, and initial safety test below. It is nevertheless **rejected** because the unchanged complete campaign exposes **50 differences in 348 deeper recursion-safety checks**. It is not a drop-in replacement and is not promoted as a fully compatible candidate.

## Reproduce the actual failure

The pinned correctness reference is stable CPython **3.14.6**. The frozen depth worker runs the standard-library reference and the candidate in separate, bounded subprocesses; it does not allow the candidate to call Python's regex engine. Its actual invocation is:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  tools/rust_depth_probe.py \
  --module candidates.vm_candidate \
  --seed 2026072323 \
  --timeout 5 \
  --memory-mib 768 \
  --output candidates/evidence/rust-v8-vm-stage-15-depth-safety-original-worker-mismatches.json
```

The expected exit is **1** because the engine is incorrect. The [complete original-worker report](rust-v8-vm-stage-15-depth-safety-original-worker-mismatches.json) contains all **348** checked cases and all **50** individual mismatches, including the exact expected and observed errors. It records **zero crashes**, **zero timeouts**, and **zero standard-library self-oracle failures**.

| Frozen recursion-safety category | Observed differences |
| --- | ---: |
| Runtime changes to Python's recursion limit | 28 |
| Deeply nested parser inputs | 14 |
| Reproducibly seeded nested patterns | 5 |
| Deep malformed patterns | 3 |
| Total | **50/348** |

The separate [single full-campaign failure](rust-v8-vm-stage-15-sealed-campaign-failure.json) records the same original worker, seed, denominator, categories, and failure totals. That campaign was invoked **once**. Because the campaign removes its private temporary output, one separately run, unchanged original worker preserves the actual individual failures rather than inventing or reconstructing them.

The failures occur while compiling patterns. Some nested patterns incorrectly compile when Python raises `RecursionError`; other valid lookaround patterns incorrectly raise `RecursionError` when Python compiles them. Three deeply malformed patterns report a pattern error instead of Python's earlier `RecursionError`. Consequently, adding only an arbitrary depth cap would not solve the problem: both parser error precedence and real compiler stack use must match the current Python recursion limit.

## Tests that actually passed

The exact same rejected C source separately passes every following unchanged frozen check:

| Frozen check | Actual result | Complete evidence |
| --- | ---: | --- |
| Initial isolated safety | 254/254 | [Original bounded safety report](rust-v8-vm-stage-15-isolated-safety.json) |
| Extended Python behavior | 72,248/72,248 | [Complete extended report](rust-v8-vm-stage-15-extended-path-failures.json.gz) |
| Matching and edge cases | 223,198/223,198 | [Complete matching report](rust-v8-edge-oracle-vm-deep-stage-15.json.gz) |
| Independently generated parser cases | 20,480/20,480 | [Complete parser report](rust-v7-grammar-vm-v8-deep-stage-15.json.gz) |
| Public objects and lifetimes | 393/393 | [Complete public-contract report](../audits/RUST-V8-DEEP-CONTRACT-C-STAGE-15.json.gz) |
| Tracing, iterators, and unusual arguments | 479/479 | [Complete observability report](rust-v8-observability-vm-qualified-stage-15.json.gz) |
| Replacements and callbacks | 8,862/8,862 | [Complete replacement report](rust-v8-replacement-vm-stage-15.json.gz) |
| Deeper replacements and callbacks | 11,266/11,266 | [Complete deep replacement report](rust-v8-replacement-vm-deep-stage-15.json.gz) |

The [unchanged independence audit](../audits/FROM-SCRATCH-AUDIT-C-STAGE-15-PASS.json) passes for all four separately implemented engine families and all five actually loaded native libraries. The C code uses its own Python parser, its own bytecode compiler, and its own native C executor. It does not call `re`, `_sre`, another candidate, or an external regex package. Unlike the previously rejected proposal, native integer width is obtained from `struct.calcsize("n")`, without importing the forbidden `sys` module. The [audit immediately before this experiment](../audits/FROM-SCRATCH-AUDIT-BEFORE-C-STAGE-15.json) is also preserved.

## Exact rejected implementation

The [lossless source patch](C-STAGE-15-REJECTED-RECURSION.patch) preserves the complete proposed changes against the committed production C engine. The verified SHA-256 fingerprints at the time the tests were run are:

```text
GOAL.md
e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62

candidates/vm_candidate.py
5eda18175df026b31e7488733f56fd8abc6cd7b7f5a235f23f4d6b37ca3328b2

candidates/_vm_native.c
892696cbf35a146c4da3e9e677058c3873199a4d9053b7ba9e7b4a34d5908ee5

candidates/_vm_native.cpython-314-x86_64-linux-gnu.so
6520023f79cc69afed8e0fd8a95d3822e458774eb79a65ded262f76014302e47

candidates/evidence/C-STAGE-15-REJECTED-RECURSION.patch
764130a93b5e731f1bca0167c7fd88ed9fec49a68ee4c725302962dd1187fbda

candidates/evidence/rust-v8-vm-stage-15-sealed-campaign-failure.json
6bc87ea49395b82cd053309c7fb5d8c2462a876dc7a6f27fbccfab76d50187e8

candidates/evidence/rust-v8-vm-stage-15-depth-safety-original-worker-mismatches.json
90129b92745513eadc546813ec76d4d7c558690dd1e95d9ab9611ddc8bcf9e73

candidates/audits/FROM-SCRATCH-AUDIT-C-STAGE-15-PASS.json
240c9cd8920838922e77b35e9ff84e6e1725727d82c30e45fb8c171c81caabcb
```

The sealed **24,576-case** final benchmark was not opened, generated, or run. C final performance, memory, speed, and ranking are **NOT MEASURED**.
