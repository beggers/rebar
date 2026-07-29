# From-scratch Rust replacement and changing-buffer correction

Status: **SOURCE FROZEN; NOT BUILT; NOT RUN; NOT BENCHMARKED.**

This is a small change to our own Rust engine's Python bridge. It does not wrap
another regular-expression implementation, run a matcher, start a compiler,
change the existing candidate, or open the final performance comparison.

## What the latest actual Rust test established

The complete public V19 test receipt is SHA-256
`e48a4115a85d827cbf16a32b6b44390d2bf4b092e1823989c9bcafe874fa04fe`.
Thirteen genuine workers attempted the frozen **31,237** Python compatibility
checks. Eight groups completed, five encountered separately recorded test
infrastructure errors, and six passing groups establish **12,942** actual
passing cases.

The completely observed substitution group contains **240** differences. The
completely observed changing-buffer group contains **1,056** differences. These
are group-local observations. Since five groups are incomplete, the total
number of Rust differences remains **NOT MEASURED**. A successful publication
of these failures does not mean that the Rust candidate passed.

The frozen supplemental **8,244** differential and property checks remain a
separate case set. They are not added to the original **31,237** denominator.

## The exact first-party change

The actually tested first-party bridge is
`candidates/rust/variants/buffer_shape_pickle_findall_captures_v1/py_bridge.c`,
SHA-256 `a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a`.
The verifier derives the entire proposed corrected bridge in memory; it does
not write, activate, or replace any candidate.

Exactly two functions change:

1. `rust_restore_original_template_error` retains the position already
   reported by the parser for the actual visible bytes. Its historical
   trailing-escape branch used the outer exporter's `__len__`, which probes
   unrelated storage, adds a visible event, and substitutes the outer length
   for the nested buffer length. Removing only that branch preserves the
   original error class, message, exporter, and genuine parsed position.
2. `rust_replacement_cache` preserves an original replacement `BufferError`
   and a released replacement-memoryview `ValueError` immediately after the
   original failed acquisition. It does not alter subject failures, suppress
   custom hashes, add a retry, acquire another export, or introduce a regex
   fallback.

The source verifier requires the separately frozen Python oracle's exact
`subject SIMPLE, subject SIMPLE, replacement FULL_READONLY` flags `(0, 0,
284)` and the corresponding replacement-first, nested-subject-first release
order. It preserves the complete existing two-capture native fast path, the
actual Rust matching engine, the original live subject, reentrant capture
acquisition, callable replacements, zero-width progression, and the distinct
errors for released subjects, released replacements, writable replacement
views, failing exporters, and failing custom hashes.

The observed **240** and **1,056** differences do not prove that these two
source changes fix every case. Their effect, the complete **31,237** original
results, the separate **8,244** results, fresh native builds, runtime
independence, and public replacement compatibility are **NOT MEASURED** until
a new complete campaign is independently frozen and run.

## Reproduce the source-only checks

Use exactly the pinned stable Python:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
```

Independently calculate SHA-256 for the three new owners:

```text
tools/apply_owned_rust_capture_shape_semantics_v1.py
oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V1.md
oracle/phase2/rust-capture-shape-semantics-v1.json
```

Run each mode with all three caller-supplied hashes:

```text
python3.14 -I -B -S tools/apply_owned_rust_capture_shape_semantics_v1.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

python3.14 -I -B -S tools/apply_owned_rust_capture_shape_semantics_v1.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Repeat both commands under `env -i PATH=/usr/bin:/bin LC_ALL=C` with the
absolute pinned interpreter. The source-only audit must reject candidate and
regex imports, subprocesses, native loading, all compressed evidence, private
roots, timing, network access, writes, reordered exports, changed exception
types, outer-length positions, fabricated passing cases, and weakened frozen
denominators.

The proposed **14,155,776**-case final speed comparison remains **NOT
GENERATED and NOT OPENED**. No candidate qualifies. Speed, memory, confidence
intervals, undefined behavior, and the effects of this source change are **NOT
MEASURED**. No winner has been chosen.
