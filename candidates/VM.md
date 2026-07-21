# Candidate B: native bytecode VM

`candidates.vm_candidate` is a second, independently runnable from-scratch family. Its semantic parser is an **iterative frame-stack parser**, not Candidate A's recursive parser. A separate compiler lowers expressions into bytecode (`SPLIT`, `JUMP`, capture saves, classes, assertions, atomics, and conditionals); the dependency-free C extension executes that bytecode with an explicit backtracking stack and UTF/bytes-aware character operations. Lookarounds run isolated subprograms and atomics trim their backtracking region.

No stdlib or third-party regex code is imported or linked. Python's Unicode character tables are used only for documented character classification and case mapping. The extension is built locally and intentionally ignored by Git; source, compiler, build script, and result are committed.

Build and reproduce the complete gate with the pinned CPython:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 "$PY" tools/oracle.py verify --module candidates.vm_candidate --output candidates/evidence/vm-correctness.json
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 "$PY" tools/audit_candidate.py candidates/vm_candidate.py candidates.vm_candidate candidates/_vm_native.c
```

The committed [result](evidence/vm-correctness.json) passes 2,048/2,048 cases with zero mismatches or crashes and all 38 obligations mapped. Search scans starts inside the VM, and `findall`, `finditer`, and `split` collect all non-overlapping results in one native call. Fixed suffixes and leading character constraints reject impossible starts before allocating execution state. The native gate is also run with address and undefined-behavior sanitizers; no sanitizer failure is accepted.
