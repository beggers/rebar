# Candidate A: recursive AST backtracker

`candidates.ast_candidate` is an independently runnable, dependency-free Python implementation. It does not import or execute stdlib `re`, `_sre`, or any third-party engine. Its parser produces an explicit AST; a recursive generator executor explores ordered alternatives and backtracking states, while preserving captures, `lastindex`, lookarounds, atomics, possessives, and zero-width advancement. Its public `Pattern`, `Match`, scanner, flag, error, and replacement-template implementations are local.

This is deliberately the simple reference architecture, not a performance claim. It passes every frozen correctness-v1.1 case:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 "$PY" tools/oracle.py verify --module candidates.ast_candidate --output candidates/evidence/ast-correctness.json
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 "$PY" tools/audit_candidate.py candidates/ast_candidate.py candidates.ast_candidate
```

The result is committed in [evidence/ast-correctness.json](evidence/ast-correctness.json). No waiver was added: 2,048/2,048 cases pass, 38/38 obligations remain mapped, and the failure list is empty.
