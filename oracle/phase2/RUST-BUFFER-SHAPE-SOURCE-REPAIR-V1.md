# First-party Rust buffer and replacement source repair V1

This is a source-only repair to the existing from-scratch Rust candidate. It is
not a new candidate family, a candidate run, a benchmark, or a qualification.

## Starting point

The most recent completed Rust run remains **FAIL**: 928 observed compatibility
differences, 8,965 explicitly verified passing checks, all 13 distinct worker
processes completed, and no runner failures, against the unchanged 31,237-case
correctness oracle. Its small, plain-text publication receipt is
`b87ff02f10103c1c8e7da7ed7ef77cd58936af2fe9e9b3c47448e8a449b01943`.

The actually tested historical bridge is
`4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257`
(176,118 bytes). The actually tested public adapter is
`d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e`
(31,934 bytes). The verifier reproduces both exactly in memory from their
hash-pinned original source and the literal blocks in the independently frozen
first-party repair sources. It does not load, execute, or import either repair.
The canonical bridge, canonical adapter, Rust engine, and Cargo lock stay
unchanged.

The historically committed V48 experiment log
`bfec908f1689bf940e479688e51b209b6182eed29f50996792507fb2668362db`
reports 224 buffer and replacement-order differences, 672 match-expansion and
replacement-shape differences, and a separate 32 match-serialization
differences. These category counts are attributed to the authenticated
historical log, **not** to the small receipt. The verifier does not read or
depend on the mutable live experiment log. This source-only repair does not
open, read, decompress, or recompute any failure archive, and does not claim
that any of the historical mismatches have been fixed.

## Source change

The complete, append-only variant is
`candidates/rust/variants/buffer_shape_v1/py_bridge.c`, SHA-256
`29421096dc81759ca11c53080b7f838cc29ad16baa7e379c18c8417d35ab37b3`
(180,436 bytes). It reproduces from the actually tested V13 bridge using unique,
independently verified source transformations. It:

- acquires and safely snapshots a non-callable buffer subject before observable
  replacement validation, retaining the original object for match identity;
- hashes the original replacement after releasing its initial buffer export,
  safely copies possibly non-contiguous full-read-only buffers with
  `PyBuffer_ToContiguous`, and releases every acquired export exactly once;
- reconstructs template errors against the original replacement, retaining its
  observable length and ordinary exception behavior;
- checks newly reacquired capture lengths before reading; and
- preserves callable replacements, the existing first-party Rust engine and
  adapter, and the separate match-serialization implementation.

No Python standard-library regular-expression engine, external regular-expression
package, or other candidate is called. Source inspection establishes only the
first-party source change: runtime non-delegation, undefined behavior, memory,
correctness, and performance remain **NOT MEASURED**.

The original denominator stays 31,237 cases in 13 suites, with 13 named private
waivers. The 32 large-input checks, 32 public-import checks, and 50 callable
introspection checks remain separate supplements; none is added to that
denominator or reported as a new candidate pass.

## Reproduction and boundaries

Use the pinned CPython 3.14.6 executable at
`/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14`.
For each invocation pass the three independently computed SHA-256 values of
`tools/apply_owned_rust_buffer_shape_source_repair_v1.py`, this protocol, and
`oracle/phase2/rust-buffer-shape-source-repair-v1.json`:

```text
python3.14 -I -B tools/apply_owned_rust_buffer_shape_source_repair_v1.py \\
  --self-test --source-sha256 SOURCE --protocol-sha256 PROTOCOL \\
  --contract-sha256 CONTRACT

python3.14 -I -B tools/apply_owned_rust_buffer_shape_source_repair_v1.py \\
  --verify-frozen-context --source-sha256 SOURCE --protocol-sha256 PROTOCOL \\
  --contract-sha256 CONTRACT
```

Repeat both commands under `env -i PATH=/usr/bin:/bin LC_ALL=C` with the
absolute pinned interpreter path. All four gates must pass.

The verifier rejects a bootstrap that imported `re` or `_sre`, installs an
irrevocable process-wide audit wall, admits only exact, authenticated
plaintext owners, parses historical repair sources as bounded abstract syntax
trees, and reconstructs both the historical source and complete variant in
memory. It rejects archive access, the hidden holdout, regex imports, native
loading, subprocesses, network access, clocks, and writes. Its strict JSON
parser rejects duplicate keys and malformed source evidence. Hostile controls
exercise both the source derivation and real blocked audit events.

The expanded 4,194,304-case holdout remains **NOT OPENED** and ungenerated.
The variant remains **NOT BUILT**, correctness **NOT MEASURED**, and
performance **NOT MEASURED**. No winner is selected.
