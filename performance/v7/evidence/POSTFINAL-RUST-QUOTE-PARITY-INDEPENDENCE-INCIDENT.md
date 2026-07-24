# Post-final Rust quote parity: first independence-audit failure

This is an additive public-development experiment. The original one-time
24,576-case hidden final remains **FALSIFIED**. It was not reopened, read, or
retried.

After rebuilding the independently written Rust quote-parity matcher, the
unchanged original from-scratch audit was run with pinned CPython 3.14.6:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  -m tools.audit_from_scratch
```

The actual first result was:

```json
{"family_results": {"ast": true, "rust": true, "vm": true, "zig": true}, "manifest_passed": true, "native_elf_binary_count": 5, "native_elf_passed": true, "native_mapping_passed": true, "passed": false, "report": "candidates/audits/FROM-SCRATCH-AUDIT.json", "result": "FAIL", "rust_native_elf_passed": true, "self_test_checks": 0, "self_test_failures": ["isolated malicious-control subprocess exited unsuccessfully"], "verified_core_family_count": 3, "verified_distinct_pipeline_count": 4, "vm_native_elf_passed": true, "zig_native_elf_passed": true}
```

Exit status: `1`. The auditor does not replace its canonical report on a
failed run. The retained historical passing report still had SHA-256
`7c6575ee8a4dd373ebf7d59ce853fac47985b592429b9120f7d545fd184f2048` and did
**not** qualify the changed Rust source.

The exact proposed Rust source had SHA-256
`2750f9c77a746e019b0bcfa14ffa329b66d571d0202d9423fe67f9b0e8bd2df2`; its
rebuilt owned Rust engine had SHA-256
`0bdd8072d253dadce35358814dfdadb51bb83dd3d34b2e6d6c699592e14889c7`.
The unchanged Rust bridge source had SHA-256
`4379d491a68f6b218a0c0feacc9295f8d2a75ffe2ac2c5e21bd68d688c212ca2`.

The failing check is preserved rather than weakened, omitted, or reported as a
pass. Its precise cause is **NOT MEASURED**. The candidate remains **NOT
QUALIFIED**, and the new architecture's performance remains **NOT MEASURED**,
unless the original full audit and all original correctness gates subsequently
pass against these exact sources and actual loaded native libraries.

## Authorized, unchanged audit retry

The exact same pinned audit, candidate sources, five native libraries, and
original malicious-control requirements were then rerun with explicit shell
sandbox permission. No control, check, timeout, audit source, or passing
threshold was removed or changed. The actual retry produced:

```json
{"family_results": {"ast": true, "rust": true, "vm": true, "zig": true}, "manifest_passed": true, "native_elf_binary_count": 5, "native_elf_passed": true, "native_mapping_passed": true, "passed": true, "report": "candidates/audits/FROM-SCRATCH-AUDIT.json", "result": "PASS", "rust_native_elf_passed": true, "self_test_checks": 76, "verified_core_family_count": 3, "verified_distinct_pipeline_count": 4, "vm_native_elf_passed": true, "zig_native_elf_passed": true}
```

Exit status: `0`. The newly generated, source-bound canonical passing audit has
SHA-256 `b84d07c0b30ccf41af3214c9255ced18835998f19038b90e8464d5fd2d3ed5e4`.
It verifies the exact Rust source and native engine recorded above, all five
actually loaded native libraries, and all 76 original malicious controls.
Passing this independence check alone establishes neither public compatibility
nor speed: the separately versioned complete matching, object, observability,
property, and full 22-stage gates must still be rerun.
