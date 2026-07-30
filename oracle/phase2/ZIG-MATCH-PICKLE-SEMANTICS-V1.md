# First-party Zig match serialization, version 1

Status: SOURCE FREEZE ONLY. The independently written Zig engine and binding
are not built, imported, activated, run, or benchmarked by this experiment.

## Preserve every observed original failure

The complete original Python suite has **31,237** checks in **13** groups.
The previous actual Zig campaign verified **4,607** checks and preserved
**1,700** measured differences. Its **128** interpreter-isolation checks did
not finish, so the complete candidate mismatch count remains **NOT MEASURED**.

The 6,912-case public-type group contains **248** genuine differences. Exactly
**32** concern Python `Match` serialization: **16** use pickle protocol zero,
and **16** use protocol one. CPython returns a normal legacy object pickle
for these protocols; the independent Zig binding currently raises:

```text
TypeError: cannot pickle 're.Match' object
```

The frozen Python oracle only serializes these objects; it does not claim they
can be loaded. Protocol two and higher must retain their existing rejection.

## Compose two separately owned native corrections

Authenticate the original first-party C bridge and independently derive the
previously frozen scanner-capture correction entirely in memory. Its exact
intermediate source must have SHA-256
`a5ab490d0cfcbba295b68f3f738a1c6371ef3314e9a6c01cdcc0bb5978e3b148`.
Do not require or open its prospective not-yet-created variant.

Retain the existing `__reduce__` rejection. Replace the current unconditional
`__reduce_ex__` rejection with an owned C function that:

1. Safely converts and validates the supplied pickle protocol.
2. Rejects negative protocols and protocol two or higher using the unchanged
   existing `cannot pickle 're.Match' object` error.
3. Uses ordinary Python `copyreg._reconstructor` for protocols zero and one.
4. Returns exactly `(copyreg._reconstructor, (type(match), object, None))`.
5. Safely releases every temporary Python reference and preserves all errors.

`copyreg` provides generic Python object serialization, not a regular-
expression engine. No Python `re`, `_sre`, CPython matcher, external regex
package, other candidate, fallback, or hardcoded matching answer is used.
The independently written Zig parser, compiler, executor, engine, scanner,
and tests remain unchanged.

The composed source is modeled to correct **620** scanner differences and
**32** legacy-pickling differences, leaving **1,048** measured differences.
When combined with the separately frozen public-adapter correction, the
expected total is **964** corrected cases and **736** remaining: **64**
replacement-buffer lifetime differences and **672** shape-changing-buffer
differences. These counts are source-level predictions, **not candidate
correctness results**. The child-interpreter group remains **NOT MEASURED**.

## Frozen source-only checks

Use pinned official isolated CPython 3.14.6 with `-I -B -S`. Independently
pin this source, protocol, complete contract, original C bridge, Zig engine,
previous actual Zig receipt, and all six source/protocol/contract owners from
the frozen public-adapter and scanner experiments.

Run `--verify-frozen-context` and `--self-test` in the ordinary isolated
environment and the empty environment
`env -i PATH=/usr/bin:/bin LC_ALL=C PYTHONDONTWRITEBYTECODE=1`. Synthetic
ordinary-Python objects verify the exact protocol-zero and protocol-one
reconstruction, legacy serialized bytes, unchanged direct `__reduce__`
rejection, rejection of every higher protocol, scanner composition, and
hostile source changes. No candidate, native library, native compiler, final
test, archive, timer, or child interpreter is touched.

The prospective destination
`candidates/zig/variants/match_pickle_semantics_v1/py_bridge.c` must remain
absent in all source-only gates. A separately authorized, fully pinned,
root-only `--apply` may exclusively create that single new source; canonical
candidate files and prior variants are never changed.

Build: **NOT RUN**. Correctness: **NOT RUN**. Runtime non-delegation:
**NOT ESTABLISHED**. Performance and memory: **NOT MEASURED**. Final test:
**NOT OPENED**. Qualifying candidates: zero. Winner: none.
