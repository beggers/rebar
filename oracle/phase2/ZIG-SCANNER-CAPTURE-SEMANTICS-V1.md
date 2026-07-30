# First-party Zig scanner capture repair, version 1

Status: SOURCE FREEZE ONLY. No candidate, compiler, native library, matching
engine, archive, hidden test, speed test, or child interpreter is run.

## Preserve the complete observed failure

The original Python reference contains 31,237 checks in 13 groups. The last
genuine Zig campaign passed seven groups containing 4,607 checks and observed
1,700 actual differences in five completed groups. Its 128-check interpreter
group did not finish; the complete candidate failure count is **NOT MEASURED**.

The original 2,854-case scanner/comment group contains exactly **620** actual
failures: **310 text** cases and **310 byte** cases. A typical text callback
must expose inner capture `ab`, but the Zig implementation returns `#ab`.
The equivalent bytes case should return hexadecimal `6162`, but returns
`236162`. The whole matched token is correctly `#ab` in both engines; only
the exposed inner capture and its starting position differ.

## One independently owned native-source change

The Zig engine remains independently written in
`candidates/zig/mini_regex.zig`, SHA-256
`a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28`.
The existing owned C binding is `candidates/zig/py_bridge.c`, SHA-256
`67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b`.

Within `zig_scanner_project_match`, the existing loop correctly copies an
inner phrase capture into its public group. Immediately afterward, the owned
binding unconditionally overwrites the same group with the complete branch
span:

```c
size_t branch_group = active + 1;
match->spans[branch_group] = begins[0];
match->spans[exposed_stride + branch_group] = ends[0];
match->lastindex = (Py_ssize_t)branch_group;
```

The exact first-party correction keeps the complete branch span only when no
actual inner capture already occupies that public group:

```c
size_t branch_group = active + 1;
if (match->spans[branch_group] < 0) {
    match->spans[branch_group] = begins[0];
    match->spans[exposed_stride + branch_group] = ends[0];
}
match->lastindex = (Py_ssize_t)branch_group;
```

Exactly one unique source block changes. Non-scanner matches, scanner branch
selection, full-match spans, last indices, absent captures, missing capture
fallback, neighboring branches, validation, and the independent Zig matching
engine are unchanged. No external regular-expression package, Python `re`,
`_sre`, CPython matcher, other candidate, or test answers are used.

The correction is modeled to fix all **620** witnessed scanner failures,
leaving **1,080** other measured failures. Combined with the separately frozen
first-party public-adapter correction, the two source changes are modeled to
fix **932** cases and leave **768**: 32 native match-pickling failures, 64
replacement-lifetime failures, and 672 shape-changing-buffer failures. These
are predictions, **not measured candidate results**. The unfinished child
interpreter remains **NOT MEASURED**.

## Four source-only gates

Use pinned official CPython 3.14.6 with `-I -B -S`. Independently supply the
complete source, protocol, contract, original C bridge, original Zig engine,
actual previous failure receipt, independently frozen public-adapter source
triple, and frozen V15 campaign source triple. Verify exact bytes, fingerprints,
the 31,237-case denominator, all original failures, the 620 scanner rows, and
the entire unchanged C source outside the one correction.

Run `--verify-frozen-context` and `--self-test` in both the ordinary isolated
environment and the empty environment
`env -i PATH=/usr/bin:/bin LC_ALL=C PYTHONDONTWRITEBYTECODE=1`. Synthetic
controls reproduce the real text and byte capture failure, preserve branches
without inner groups, reject malformed capture boundaries and foreign branch
numbers, and prove no native dependency or entry point changes. A deny-default
physical read-only wall prevents matching, candidate imports, native loads,
builds, processes, hidden tests, timers, and writes.

The destination
`candidates/zig/variants/scanner_capture_semantics_v1/py_bridge.c` must remain
absent during every source-only check. Only a separately authorized, fully
pinned root-only `--apply` may exclusively create that exact new source file.
It never modifies the canonical C bridge or an existing variant.

Native build: **NOT RUN**. Correctness: **NOT RUN**. Runtime non-delegation:
**NOT ESTABLISHED**. Speed and memory: **NOT MEASURED**. Final test:
**NOT OPENED**. Qualified candidates: zero. Winner: none.
