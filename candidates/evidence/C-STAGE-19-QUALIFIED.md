# C candidate passes the complete Python compatibility campaign

The independently implemented C candidate is now **correctness-qualified**. The pinned CPython **3.14.6** reference, all frozen correctness obligations, and the original independence rules are unchanged. Its first complete Stage-19 campaign genuinely executes and passes **all 22 required stages**; no candidate delegates matching to Python, `_sre`, an external regex package, or another project engine.

This report establishes **correctness, not speed**. The sealed **24,576-case final performance benchmark** has not been opened. C speed, memory, ranking, and the required **1.5×** improvement remain **NOT MEASURED**.

## Complete one-shot campaign

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  tools/rust_v8_multi_candidate_campaign.py \
  --module candidates.vm_candidate \
  --edge-oracle candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-19.json.gz \
  --deep-proof candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-19.json.gz \
  --output candidates/evidence/rust-v8-vm-stage-19-sealed-campaign.json \
  --memory-mib 2048
```

The genuine first-run result is **PASS**. The [complete source-bound campaign](rust-v8-vm-stage-19-sealed-campaign.json) records all **22** actual passing stages, including Python's own tests, full-Unicode behavior, both replacement suites, public objects, tracing, resource safety, recursion safety, four-family independence, and forbidden-engine poison controls. It records `holdout_accessed=false`, `performance="NOT MEASURED"`, and `timing_performed=false`; all performance fixtures are explicitly excluded.

## Independently verified frozen checks

| Original correctness obligation | Actual result | Complete evidence |
| --- | ---: | --- |
| Full Unicode plane and seeded Python API cases | 4,494,555/4,494,555 | [Complete Unicode report](rust-v8-vm-stage-19-unicode-fullplane.json) |
| Unicode code points in each full-plane partition | 1,114,112/1,114,112 | [All four complete expected and observed hashes](rust-v8-vm-stage-19-unicode-fullplane.json) |
| Extra Unicode case-equivalence controls | 280/280 | [All 50 keys and 56 case links](rust-v8-vm-stage-19-unicode-fullplane.json) |
| Matching and edge cases | 223,198/223,198 | [Complete edge report](rust-v8-edge-oracle-vm-deep-stage-19.json.gz) |
| Extended Python compatibility | 72,248/72,248 | [Complete extended report](rust-v8-vm-stage-19-extended-path-failures.json.gz) |
| Independently generated parser cases | 20,480/20,480 | [Complete grammar report](rust-v7-grammar-vm-v8-deep-stage-19.json.gz) |
| Replacement and callbacks | 8,862/8,862 | [Complete replacement report](rust-v8-replacement-vm-stage-19.json.gz) |
| Deeper replacement and callbacks | 11,266/11,266 | [Complete deep replacement report](rust-v8-replacement-vm-deep-stage-19.json.gz) |
| Public object and lifetime behavior | 393/393 | [Complete public-contract report](../audits/RUST-V8-DEEP-CONTRACT-C-STAGE-19.json.gz) |
| Public tracing, scanners, and unusual arguments | 479/479 | [Complete observability report](rust-v8-observability-vm-qualified-stage-19.json.gz) |
| Deep recursion and overflow safety | 348/348 | [Complete isolated depth report](rust-v8-vm-stage-19-depth-safety.json) |
| Crash, malformed-input, and allocation safety | 254/254 | [Complete isolated safety report](rust-v8-vm-stage-19-isolated-safety.json) |
| Original anti-delegation controls | 76/76 | [Canonical four-engine independence audit](../audits/FROM-SCRATCH-AUDIT.json) |

The public-contract report records **zero public mismatches**. It preserves the original named waiver for one implementation-private garbage-collection topology difference; no private difference is hidden or presented as public behavior.

## All preceding failures remain available

The final implementation preserves rather than overwrites the actual failed experiments:

- [Unbounded large-repeat failure](C-STAGE-11-BOUNDED-REPEAT-DIAGNOSTIC.md).
- [Incorrect repeat capture](C-STAGE-12-REJECTED-COMPACT-REPEAT.md).
- [Ten safety mismatches](C-STAGE-13-REJECTED-SAFETY.md).
- [Forbidden `sys` import and failed independence audit](C-STAGE-14-REJECTED-INDEPENDENCE.md).
- [Fifty recursion-limit mismatches](C-STAGE-15-REJECTED-RECURSION.md).
- [Incomplete Unicode character equivalence](C-STAGE-16-REJECTED-UNICODE.md).
- [Two inverted-window nullable matches](C-STAGE-17-REJECTED-WINDOW.md).
- [Six incorrectly rejected boundary matches](C-STAGE-18-REJECTED-INVERTED-BOUNDARY.md).

The accepted implementation derives runtime recursion from public CPython APIs, implements all **24** pinned Unicode equivalence groups itself, compiles consuming category alternatives using its existing native single-character repeat instruction, and correctly applies locally scoped flags to its own search filter. Python's own matching engine is used only in the separate frozen correctness processes.

## Exact source and passing artifacts

```text
GOAL.md
e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62

candidates/vm_candidate.py
91d848e2627f19e552fef19b9943eb3e265e25537934128875645bab63cf7b80

candidates/_vm_native.c
bb4df5960e169c24e772d9fa0a193fcc6a9e8d31ab60d20aabb48ab07e5fe06d

candidates/_vm_native.cpython-314-x86_64-linux-gnu.so
d3ec19d66161f789056f2146c3abadccb98fa7bfd979fd66e1fb68540ad0f078

candidates/audits/FROM-SCRATCH-AUDIT.json
6867580e7634163bd009d1f4e699d3fe4fb9ddc89b183ef60200363d1a8ab24e

candidates/evidence/rust-v8-vm-stage-19-unicode-fullplane.json
b1200f3e2cefadbab3348ddc927c69bf5f50c9b7df032f032235477371c49556

candidates/evidence/rust-v8-vm-stage-19-sealed-campaign.json
d16a046cd00996291be449f9304d401917c8db16c178e8d4f003f81c688b2677
```

Rust and C have both genuinely passed the frozen complete correctness campaign. Zig has not. Final comparative performance remains **NOT MEASURED** until at least three independent candidates actually qualify.
