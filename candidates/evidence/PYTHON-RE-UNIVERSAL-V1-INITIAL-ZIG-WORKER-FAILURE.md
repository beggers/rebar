# Initial all-engine public oracle: preserved Zig harness failure

Status: **REJECTED TEST HARNESS; not a candidate correctness result.**

The first universal-public-oracle source had SHA-256
`6304e095b4038e4b16a143c4391c52fa25ad6c6cb89910529cda6123ac528395`.
The exact attempted all-candidate command was:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  tools/python_re_universal_public_oracle_v1.py \
  --candidate all \
  --output candidates/evidence/python-re-universal-public-oracle-v1-all.json
```

It exited unsuccessfully before creating the requested evidence. Its
controller reported:

```text
OracleIntegrityError: isolated zig/candidate ended before its exact public JSON record
```

The absence of a complete output is a real test-run failure. It must not be
reported as a passing Rust, C, or Zig differential; completed comparisons
cannot be inferred from this aborted all-candidate run.

## Independent cause

A separate pinned, isolated Zig-only diagnostic recovered the candidate
worker's exact failure without opening or timing a holdout:

```text
Traceback (most recent call last):
  File "/home/dev-user/src/rebar/tools/python_re_universal_public_oracle_v1.py", line 2480, in <module>
    raise SystemExit(main())
  File "/home/dev-user/src/rebar/tools/python_re_universal_public_oracle_v1.py", line 2472, in main
    run_worker(args.worker, args.candidate, provenance)
  File "/home/dev-user/src/rebar/tools/python_re_universal_public_oracle_v1.py", line 1647, in run_worker
    module = importlib.import_module(CANDIDATES[name]["module"])
  File "/home/dev-user/src/rebar/tools/python_re_universal_public_oracle_v1.py", line 1504, in guarded_import_module
    return original_import_module(module_name, package)
  File "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/importlib/__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
  File "<frozen importlib._bootstrap>", line 1406, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1371, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1342, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 938, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 759, in exec_module
  File "<frozen importlib._bootstrap>", line 491, in _call_with_frames_removed
  File "/home/dev-user/src/rebar/candidates/zig_candidate.py", line 3, in <module>
    import ctypes
  File "/home/dev-user/src/rebar/tools/python_re_universal_public_oracle_v1.py", line 1499, in guarded_import
    return original_import(module_name, globals, locals, fromlist, level)
  File "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/ctypes/__init__.py", line 568, in <module>
    pythonapi = PyDLL(None)
  File "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/ctypes/__init__.py", line 433, in __init__
    self._handle = self._load_library(name, mode, handle, winmode)
  File "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/ctypes/__init__.py", line 475, in _load_library
    return _dlopen(name, mode)
  File "/home/dev-user/src/rebar/tools/python_re_universal_public_oracle_v1.py", line 1448, in hook
    deny("foreign_native_loader", target)
  File "/home/dev-user/src/rebar/tools/python_re_universal_public_oracle_v1.py", line 1434, in deny
    raise ImportError(f"universal public isolated worker rejected {kind}: {target}")
ImportError: universal public isolated worker rejected foreign_native_loader: None
```

The standard-library `ctypes` module initializes its own `pythonapi` before
Zig can load its independently audited native engine. The strict isolation
audit already initializes that standard-library module **before** installing
its permanent guard; it continues to reject candidate-initiated
`dlopen(None)`, foreign native engines, Python `re`, and every cross-family
candidate afterward. The public oracle must follow the same proven order.

The failure is preserved rather than hidden. It is not evidence that Zig
delegated to Python, wrapped an external regex package, mismatched a regex
result, or passed the comprehensive public oracle. Hidden cases, benchmark
observations, and final performance remain **NOT MEASURED**.
