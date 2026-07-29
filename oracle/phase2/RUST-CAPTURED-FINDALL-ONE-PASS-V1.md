# Freeze a first-party Rust captured-search experiment

Status: **SOURCE FROZEN; NOT BUILT; NOT RUN; NOT BENCHMARKED.**

This is a cumulative source-only experiment in the independently written Rust
engine. It does not establish compatibility, speed, memory use, runtime
independence, or a winning replacement. No final benchmark is authorized.

## Authenticated first-party history

The original source-built buffer and pickle predecessor is
`candidates/rust/variants/buffer_shape_pickle_v2/py_bridge.c`:

```text
SHA-256  afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740
bytes    179961
lines    4774
```

Its historical two-phase, 28-process native-build receipt is
`27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc`.
Its separate source-root provenance receipt is
`de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99`.
These receipts authenticate the historical predecessor only.

The immediate, complete one-pass literal-search predecessor is
`candidates/rust/variants/buffer_shape_pickle_findall_v1/py_bridge.c`:

```text
SHA-256  b707e924a23980385b0c5b0306daecd55bbb03d6f2511437f0532b6d39b2a112
bytes    178950
lines    4757
```

Its source-only verifier, protocol, and contract remain independently
authenticated. Its new captured-search successor is
`candidates/rust/variants/buffer_shape_pickle_findall_captures_v1/py_bridge.c`:

```text
SHA-256  a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a
bytes    179520
lines    4774
```

Exactly one function changes: `rust_append_batched_findall`. For exactly two
capturing groups, the new source constructs one two-item Python tuple and
appends it directly using the existing owned-list helper. It preserves the
original group order, unmatched-group empty values, string and bytes behavior,
full-subject bytes identity, buffer lifetime, allocation failure propagation,
and reference ownership. All zero-, one-, and greater-than-two-group paths,
the Rust matcher, the single-pass literal improvement, and every other
predecessor byte remain unchanged.

## Open public evidence; no hidden benchmark

The only inspected timing corpus is the already published, explicitly public
864-case historical practice report:

```text
experiments/rust_public_practice_v1/rust-memoryview-native-exporter-fix-public-practice.json
SHA-256  76015482b066b613ec6290b6d0fb28bd5ea76df21a9930e64f4ea2628211c9b2
bytes    6229575
```

The frozen report contains **48** module or compiled-pattern `findall` cases
with exactly two named capturing groups. Its frozen CPython reference records
materialize captured tuples in **44** of those cases; the other **four**
correctly return empty lists. This proves that the proposed branch covers a
previously public workload. It does not prove that the new source is correct
or faster: this variant has not been compiled, activated, matched, or timed.

The complete correctness requirements remain all **31,237** original cases in
**13** groups and the separate **8,244** differential and property cases. The
**13** existing named private waivers are unchanged. A fresh first-party
native build, both complete correctness campaigns, public API and buffer
checks, and the runtime no-delegation audit must independently pass before
any performance claim. No existing candidate, external regular-expression
package, CPython matching engine, or standard-library `re` is a production
dependency.

## Reproduce the source-only verification

Use the exact frozen CPython **3.14.6** executable:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
```

Hash the source-only verifier, this protocol, and the canonical JSON contract.
Run both modes with exact caller-supplied hashes:

```text
python3.14 -I -B tools/verify_owned_rust_captured_findall_source_v1.py \
  --self-test \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

python3.14 -I -B tools/verify_owned_rust_captured_findall_source_v1.py \
  --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

Repeat each command under `env -i PATH=/usr/bin:/bin LC_ALL=C`. The verifier
rejects an unpinned interpreter, bytecode writes, unexpected file reads,
changes to authenticated source, child processes, native loading, clocks,
network access, writable files, regular-expression imports, or hidden cases.
It independently recounts the 48 public captured-search cases and their 44
nonempty CPython outcomes from the exact authenticated public report.

The latest independently frozen **source-only proposal**, not the hidden
benchmark, specifies **14,155,776** future cases. Its exact public owners are:

```text
tools/verify_expanded_sealed_holdout_v1.py
SHA-256  3dd9abcbd7a87486186ee8da804de595e65d79020a3fe33413d0157dde4f3309
bytes    27311

oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md
SHA-256  818f1636d87ae721912f04a3fc8294ac04a59dff4a272319aa29a393f52a4fd4
bytes    13237

oracle/phase3/expanded-sealed-holdout-v1.json
SHA-256  676aac4f48c9404f5253c89b692efde5c425170f8d9f152b4f85b3e2a5225a76
bytes    6628
```

The verifier reads and authenticates only these three bounded, public
specification files. It never reads a case generator, benchmark input,
secret, or hidden output. The final protocol and case generator remain
**NOT FROZEN**. All **14,155,776** final cases remain **NOT GENERATED and
NOT OPENED**. Running the final benchmark requires at least **three**
fully compatible, genuinely independent, first-party candidates with
passing runtime no-delegation audits. The prior **4,194,304**-case proposal
is preserved as historical evidence; it is not the current proposal.

Current speed, memory, statistical confidence, complete compatibility, and
undefined behavior are **NOT MEASURED**. Runtime independence is **NOT
ESTABLISHED**. Qualified candidates: **0**. No winner has been selected.
