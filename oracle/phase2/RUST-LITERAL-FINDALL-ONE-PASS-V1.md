# Freeze an independently owned one-pass Rust literal-search experiment

Status: **SOURCE FROZEN; NOT BUILT; NOT RUN; NOT BENCHMARKED.**

This is one isolated, first-party Rust architecture experiment. It is not a
replacement qualification, a successful native build, a matching result, a
performance claim, or permission to inspect the final holdout.

## Exact predecessor

The independently built, two-phase version-19 predecessor is
`candidates/rust/variants/buffer_shape_pickle_v2/py_bridge.c`:

```text
SHA-256  afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740
bytes    179961
lines    4774
```

Its actual passing native-build publication receipt is
`27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc`.
Its separate, passing root-provenance receipt is
`de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99`.
Those receipts prove the historical build and source provenance, not that
this new variant has been built, executed, or timed.

## Exactly one changed function

The new, independently preserved complete variant is
`candidates/rust/variants/buffer_shape_pickle_findall_v1/py_bridge.c`:

```text
SHA-256  b707e924a23980385b0c5b0306daecd55bbb03d6f2511437f0532b6d39b2a112
bytes    178950
lines    4757
```

Every predecessor byte outside `rust_pattern_literal_findall_direct` is
unchanged. The old function counted all non-overlapping literal occurrences
and then scanned the same subject again to construct its result. The new
function performs one forward, non-overlapping search, appending each owned
result as it is found.

The original Python index conversion, window clamping, empty-window and
zero-width behavior, Python buffer acquisition, subject release, Unicode
single-character and multi-character searches, bytes `memmem` search,
native exception propagation, Python list ownership, exact full-subject
bytes identity, and existing first-party Rust engine are preserved. Existing
`rust_findall_item` and `rust_list_append_owned` provide the same Python
values and amortized, overflow-checked Python list allocation. Every error
path releases the original subject exactly once.

No generic batching function, replacement function, Python adapter, existing
variant, native artifact, external matching engine, external regular-expression
package, or other candidate is modified.

## What has and has not been measured

**Existing 864-case pilot literal-findall coverage: 0.** All historical
`pattern.findall` cases in that pilot use nonliteral named-group patterns.
This experiment does not explain, repair, or accelerate those cases. Its
effect on real literal workloads is **NOT MEASURED**.

Before timing, separately freeze representative public literal cases. Before
any compatibility or speed claim, independently freeze and complete a fresh
version-20 two-phase first-party native build and provenance proof, all
**31,237** original cases and **13** groups, all separate **8,244**
differential and property cases, complete public API and Python-buffer
checks, and the runtime no-delegation audit. Preserve every failure.

The original **13** named private waivers are unchanged. No new waiver is
created. Source inspection does not establish runtime independence, undefined
behavior, memory use, or compatibility.

## Source-only reproduction

Independently hash the verifier, this protocol, and the canonical JSON
contract. Use the frozen CPython **3.14.6** executable:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
```

Run each source-only mode normally and with
`env -i PATH=/usr/bin:/bin LC_ALL=C`:

```text
python3.14 -I -B tools/verify_owned_rust_literal_findall_source_v1.py \
  --self-test \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

python3.14 -I -B tools/verify_owned_rust_literal_findall_source_v1.py \
  --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

Both modes are source-only. Neither may import a matching engine, load a
native library, invoke a worker, compile or activate a candidate, read an
archive, read the holdout, sample a clock, start a network request, or write
a file. The **4,194,304**-case final holdout remains **NOT FROZEN, NOT
GENERATED, and NOT OPENED**. Compatibility, speed, memory, confidence
intervals, undefined behavior, and runtime independence remain **NOT
MEASURED**. Qualified candidates: **0**. There is no winner.
