# Expanded, sealed performance test

This is a new, independent final test of whether a regular-expression engine
written from scratch can replace Python 3.14.6 `re` and actually run faster. Its
**12,288 cases are not practice cases**. None has been generated, read, timed,
or used to select an implementation. The original **10,312-case** final test,
its inputs, its case counts, and its historically published original-engine
results stay separate and unchanged. Corrected Rust has not been measured on
that original final test.

The test is frozen by the [manifest](holdout-manifest.json), the
[protocol verifier](../../tools/rust_v8_holdout_protocol.py), and the committed
[synthetic safety checks](evidence/HOLDOUT-PROTOCOL-SELF-TEST.json). A
cryptographically random 32-byte opening is kept only in the exact manifest
path under `/tmp` with `0600` permissions. Only its SHA-256 commitment appears
in the repository. Those permissions do **not** protect the opening against
another process running as the same Unix user: blindness depends on not reading
or using it until candidate selection, binary identities, compatibility
results, the stopping decision, and this protocol have all been committed.
A lost, revealed, previously opened, substituted, or reused opening invalidates
the expansion. Do not replace it silently.

## What the 12,288 cases mean

There are **12 public operation families × 8 workload families × 128 cases**,
giving exactly **1,024 cases for every operation**. The operations are compile,
escape, search, match, fullmatch, findall, finditer, split, sub, subn,
inspection of actual successful match objects, and compiled-pattern scanners.

The eight workload families cover literals and long prefixes; character ranges
and Unicode; anchors, boundaries, and search windows; greedy, lazy, atomic, and
possessive matching; alternatives, captures, and backreferences; lookarounds
and zero-width matching; replacements, splitting, callbacks, and result counts;
and representative logs, paths, URLs, identifiers, and noisy text.

For each of the eight ordinary matching operations, each 128-case cell is
exactly balanced across module versus compiled calls, text versus bytes, and
successful versus unsuccessful results, with **16 distinct variants for each
combination**. Compile and escape have no fictional compiled-pattern method;
they have their own genuine cache, input, length, and special-character
controls. Match-object cases always start with a successful match. Scanner
cases use real compiled-pattern scanners and balance `search`, `match`, text,
bytes, and zero-width progression. Callbacks, groups, buffers, replacement
counts, windows, flags, warnings, exact errors, and subject mutation must
retain the same observable behavior as Python wherever applicable. Invalid and
pathological inputs remain mandatory compatibility and safety checks; they
are not disguised as valid timing samples.

Each matching or compilation case has its own bounded, harmless regular-
expression comment derived from its unique operation, family, index, and a
domain-separated keyed digest. The comment is added after every family-specific
pattern and scanner override, so it changes neither matching semantics nor
zero-width progression. Escaping cases instead receive independently unique
inputs. Byte-array and memory-view cases use a tagged, exact-byte transport;
the isolated worker reconstructs an actual `bytearray` or `memoryview` before
calling the implementation. They are not ordinary bytes relabelled as buffers.
Synthetic verification uses only **44 explicitly synthetic cases** and a
separate public synthetic opening; it never generates a real final case or
reads the blinded opening.

Every candidate must first pass the unchanged **223,198-check, 49-category**
canonical Python compatibility oracle. The exact frozen runner has SHA-256
`fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca` and the
required complete Python-answer SHA-256 is
`b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526`.
The separately frozen **20,480** grammar checks, **14,783** object checks,
**4,494,555** full-Unicode checks, **479** Python-observability checks, and
**34** native-binder safety checks also retain their exact denominators. The
earlier **44,084-case, 51-obligation** original P0 oracle is additionally
preserved as historical evidence; it does not replace or downgrade the current
223,198-check test and is not a separately required obsolete proof.

Each candidate must additionally pass the independently frozen **393-case
real-user public-contract oracle**. Its exact source SHA-256 is
`ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978`,
its fixture SHA-256 is
`c72a5e47f15c94ce13ce34d4918c05ef81eea5b010ac119b255264e60939ef16`,
and its two independent pinned-Python observations both have SHA-256
`b184f3388320909b3c28fbd3ce9c15cefc992d3e852e9495ad8fb503d1cbaad8`.
All **64** implementation-private object-topology diagnostics are retained
separately; none is asserted or waived as a documented public behavior.

The preserved original Rust result has **104 actual public differences out
of 393**. Its complete failing archive has SHA-256
`db43cbf8be1d6891eb4f009b8ae92995a6434f9753b944fbf0a8ed0b44237192`.
The expanded holdout cannot be opened while any candidate retains even one
of these failures. No extra public behavior is waived.

Every timed result is independently checked against pinned CPython before,
during, and after its measurement. A mismatch, crash, timeout, missing case,
missing candidate, changed native binary, or unpaired observation fails the
entire test. No result is removed from a denominator.

## Fair comparison

Python `re` and at least **three complete, independently implemented engines**
are compared over **four warmups and 31 paired rounds** per case. A frozen,
seeded, counterbalanced rotation gives each engine first position either seven
or eight times when four engines are compared. Each case has a fixed one-second
safety guard and a maximum of 16 identical operations. The actual Python call,
argument conversion, Python/native crossing, matching, and returned objects
all belong in the reported end-to-end time.

For the minimum four-engine comparison, this is exactly **1,523,712 raw timing
rows** and **4,571,136 before/during/after correctness observations**. If more
than three candidates qualify, both denominators grow by the exact published
formula `12,288 × 31 × engine count`; they are never silently kept at the
four-engine number.

Production candidates must not import or delegate to `re`, `_sre`, another
candidate, or an external engine such as `regex`, RE2, PCRE, Hyperscan, or
Oniguruma. Native sources, lockfiles, dynamic dependencies, actually loaded
native code, and candidate-specific full-oracle proofs must agree with the
sealed candidate identities. Each engine is measured in its own persistent,
isolated process. A candidate timing process must not have Python `re` or
`_sre` loaded.

`tracemalloc` itself imports both `re` and `_sre` on pinned CPython 3.14.6.
It therefore cannot run inside an isolated candidate timing process. Python
allocation peaks are measured in explicitly separate instrumentation workers
and identified as **Python allocations, not native memory**. Whole-process
current and peak memory are separately reported using process resident memory.
The memory cohort contains **768 cases: eight per operation/workload cell**.
All measured increases and the complete memory denominator are reported.

## What counts as success

For each case and round, the paired observation is
`log(Python time / candidate time)`. Each case has a two-sided 95% confidence
interval using all 31 paired logs and the explicitly declared Student-t
critical value for 30 degrees of freedom. A case is statistically faster only
when the **lower** bound is strictly greater than `1×`; a point estimate above
`1×` is insufficient.

The overall score equally weights all **12 operations**, all **eight workload
families within each operation**, and all **128 cases within each family**.
Its 95% interval uses **9,999 seeded, stratified, paired case-cluster bootstrap
draws**. Each draw resamples complete paired case clusters within their original
operation/workload cell. Case-level intervals use the declared Student-t
method; they are not mislabelled as 9,999-bootstrap intervals.

A candidate succeeds only when:

- All frozen compatibility, independence, native-identity, and per-measurement
  correctness checks pass.
- The **lower bound** of the overall 95% speed interval is at least `1.5×`.
- At least **7,373 of all 12,288 cases** are individually, statistically
  faster. The full denominator remains 12,288.
- Every case taking **strictly more than 20% longer** is reported and explained.
  Equivalently, `Python time / candidate time` is strictly less than `5/6`;
  exactly `5/6` is not a more-than-20% regression.

The original holdout, this expansion, and any combined score must be reported
as three distinct measurements. The original 10,312-case denominator, existing
weights, and historically published original-engine results must never change
or be concealed. A combined score, if published, requires separately
predeclared weights before either test is opened.

Until the candidate identities and stopping decision are frozen and the
opening is explicitly authorized, **corrected Rust on the original holdout**,
the **new 12,288-case expansion**, final rankings of corrected candidates, and
a combined corrected-candidate score are **NOT MEASURED**. This statement does
not erase previously published results for the original engines.

## Verify without opening the test

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v8_holdout_protocol self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v8_holdout_protocol verify --evidence
```

These commands use only the public manifest, the frozen protocol source, and
explicit synthetic poison. They do not read an old fixture, open the secret,
generate a held-back case, import a candidate, build a native library, or
measure speed or memory.

The tool also provides separate `freeze-candidates` and `preflight` commands.
They require a passing, actual-native-binary **223,198-check** proof, a
current complete performance-blind correctness campaign, and a passing frozen
**393-case real-user** proof for each of at least three candidates. A separate
from-scratch audit must prove all five VM, Rust, and Zig owned native libraries
and their actual process mappings. The commands bind every candidate artifact
and every exact proof digest to a complete stopping-commit hash without opening
the final test. The irreversible `final` command additionally requires the
exact authorization string
`UNSEAL-FROZEN-V8-HOLDOUT-AFTER-CANDIDATE-SELECTION`, the committed candidate
freeze, and four distinct previously nonexistent evidence outputs. It creates
a one-use marker before opening the committed seed and streams all raw timing,
all separate memory rows, all 12,288 candidate case intervals, all losses, and
the final seed opening to reproducible evidence. A missing qualification,
changed engine, incomplete candidate list, reused marker, mismatch, crash, or
timeout stops the run; it cannot open or retry silently.

Before final selection, inspect available options without opening the test:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v8_holdout_protocol freeze-candidates --help
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v8_holdout_protocol preflight --help
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.rust_v8_holdout_protocol final --help
```
