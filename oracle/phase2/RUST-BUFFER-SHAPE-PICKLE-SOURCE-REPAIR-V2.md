# From-scratch Rust buffer-lifetime repair V2

This change freezes a small correction to our own Rust candidate. It does not
build that candidate, execute a regular expression, start a test worker, measure
speed, inspect the final holdout, or qualify a replacement.

## What really failed

The latest completed run of the original 31,237 Python checks used 13 real
workers and completed all 13 groups. The candidate failed 1,440 checks. Only
14,853 checks are independently verified as passes; cases from the three
failing groups are not silently counted as passes. The previous completed run
failed 928 checks, so the latest run is a regression of 512. Both results stay
visible.

The real failures are 16 buffer-lifetime differences, 368 replacement
differences, and 1,056 changing-buffer differences. The independently preserved
forensic summary contains all 13 real group outcomes and six exact failing
examples. It identifies a single first-party function, `rust_substitute_core`,
which copied a live Python buffer into bytes and released the original buffer
too early. A successful publication receipt or forensic analysis means the
failed result was recorded correctly; it does not mean the candidate passed.

## The exact first-party correction

The source actually tested was
`candidates/rust/variants/buffer_shape_pickle_v1/py_bridge.c`, SHA-256
`00271ad5fff71e2f2e30cda6b446a61d0c300cb91eec2091b8ada17662d9a335`
(181,004 bytes). The append-only corrected variant is
`candidates/rust/variants/buffer_shape_pickle_v2/py_bridge.c`, SHA-256
`afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740`
(179,961 bytes).

The verifier reconstructs the whole corrected file, byte for byte, from the
actual failed source. It removes exactly one premature bytes-copy block, its
declaration, and its eight obsolete snapshot cleanup lines. The real original
buffer remains held for the entire replacement. All eight real-buffer cleanup
exits, both match constructions, callback behavior, and every byte outside the
one function are preserved. The outside-function SHA-256 stays
`1a4e1713e2ea2dd6a42d56baac4e66907392b1971b94a1f5007fecab5c25830b`.

No external regular-expression package, Python matching engine, or other
candidate is introduced. This is a source inspection, not a proof of runtime
independence. Whether the change fixes the observed failures is **NOT
MEASURED** until a separately frozen native build and a fresh complete run.

## Safe reproduction

Use the frozen CPython 3.14.6 executable:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
```

Independently calculate the SHA-256 of the verifier, this protocol, and the
canonical source contract. Run both modes with `-I -B` and all three pins:

```text
python3.14 -I -B \
  tools/apply_owned_rust_buffer_shape_pickle_source_repair_v2.py \
  --self-test \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

python3.14 -I -B \
  tools/apply_owned_rust_buffer_shape_pickle_source_repair_v2.py \
  --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

Repeat both commands under `env -i PATH=/usr/bin:/bin LC_ALL=C` using the
absolute interpreter. All four checks must pass.

The verifier installs an irreversible audit wall. It permits only the exact
hash-pinned, bounded, private plaintext source and evidence owners. It rejects
duplicate JSON keys, archive and holdout reads, imports of matching engines,
candidate activation, native loading, subprocesses, clocks, network access,
file writes, missing or duplicated groups, invented event vectors, failed cases
reported as passes, and fabricated speed claims.

The expanded 4,194,304-example final comparison remains **NOT GENERATED** and
**NOT OPENED**. The new variant is **NOT BUILT** and **NOT RUN**. Performance,
memory, confidence intervals, undefined behavior, and the effect of this
repair are **NOT MEASURED**. No candidate qualifies and there is no winner.
