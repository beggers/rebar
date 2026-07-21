# rebar

This repository is a phase-gated experiment to find a compatible, materially faster replacement for Python's `re` module.

The immutable objective is [GOAL.md](GOAL.md), SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`. Scope clarifications are in [AMENDMENTS.md](AMENDMENTS.md).

## Status

| Gate | Result |
| --- | --- |
| Correctness oracle | PASS v1.1 — 2,048/2,048, 38/38 obligations, zero invalid successes or false properties |
| Qualified candidates | 3/3 — independent AST, native bytecode VM, and Rust/FFI families each pass 2,048/2,048 |
| Performance oracle | NOT MEASURED |
| Winner | NOT MEASURED |

The baseline is [CPython 3.14.6](oracle/v1/BASELINE.md). The [P0 matrix](oracle/v1/P0.md) covers the complete public API, documented syntax, errors, warnings, seeded differential/property/fuzz cases, and two explicitly named private waivers. The v1.1 fixture SHA-256 is `983885ee6411fd806edf3d72efbcc989f9b9f7775a6d127dc7c865673eeb0fed`; the denominator and all seeds are unchanged. Two isolated stdlib runs agree, and the committed failure list is empty. The pre-candidate strengthening is recorded in [AMENDMENTS.md](AMENDMENTS.md).

The [candidate discovery experiment](candidates/evidence/DISCOVERY.md) and all raw losses are preserved as rejected binding experiments. Three independent, dependency-free families are correctness-qualified: the [recursive AST backtracker](candidates/AST.md), the [iterative parser/native bytecode VM](candidates/VM.md), and the [Rust continuation arena/FFI](candidates/RUST.md). Native gates include sanitizer runs and zero-delegation audits. No performance claim has been made.

![Correctness oracle status](oracle/v1/evidence/correctness.svg)

![Raw candidate correctness status](candidates/evidence/discovery-correctness.svg)

![Qualified AST candidate correctness status](candidates/evidence/ast-correctness.svg)

![Qualified candidate correctness status](candidates/evidence/qualified-correctness.svg)

To regenerate and self-check the current oracle using the pinned runtime:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
"$PY" tools/oracle.py freeze
"$PY" tools/oracle.py verify --module re --output oracle/v1/evidence/correctness-self.json
"$PY" tools/oracle.py chart --input oracle/v1/evidence/correctness-self.json --output oracle/v1/evidence/correctness.svg
# Reproduce a single stable case ID, including fuzz/property cases:
"$PY" tools/oracle.py verify --module re --case fuzz.str.0377
```
