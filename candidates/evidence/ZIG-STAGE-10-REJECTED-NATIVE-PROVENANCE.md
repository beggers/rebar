# Rejected Zig engine: safe recursion, failed native-library verification

This from-scratch Zig proposal fixes all original extreme-input failures and both genuine deep-recursion crashes. However, its first actual independence audit fails to verify the native library mapped into the running process. The proposal is **rejected**, not promoted, and not benchmarked.

## Both unchanged safety suites pass

The complete [isolated safety report](rust-v8-zig-stage-10-isolated-safety.json) records **254/254** passing checks across **10** frozen categories, with zero failures, crashes, timeouts, or Python-reference failures. Its SHA-256 is `e7b6cd5c90a3539f767c622d640d6f38cfd7b088938a5acb2b3054a14e7e5e58`.

The complete [deep-recursion report](rust-v8-zig-stage-10-depth-safety.json) records **348/348** passing checks across **nine** frozen categories, with zero failures, crashes, timeouts, or Python-reference failures. Its SHA-256 is `1874c3f1802482a946fde8838620024ff399943388bd02dbe8ce207aed687032`. Both legal patterns that caused the [two previous native crashes](ZIG-STAGE-09-REJECTED-DYNAMIC-RECURSION.md) now compile correctly.

The implementation preserves literal-branch optimization but moves its **4,088-byte** temporary buffers into a nonrecursive, non-inlined helper. The helper cannot recursively call the compiler. This removes the prior **8,339,520-byte** recursive stack amplification at nesting depth **2,040**, without rejecting patterns Python accepts.

## The first real independence audit fails

The unchanged original auditor is `tools/audit_from_scratch.py`, SHA-256 `4c47a77cf096df354e59d03096447c56bff890389869c6a75667a36c8471d024`. Its genuine self-test passes all **76** controls. The following production command was then invoked exactly once:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  -m tools.audit_from_scratch
```

It exits **1** and emits:

```json
{"family_results": {"ast": true, "rust": true, "vm": true, "zig": false}, "manifest_passed": true, "native_elf_binary_count": 5, "native_elf_passed": true, "native_mapping_passed": false, "passed": false, "report": "candidates/audits/FROM-SCRATCH-AUDIT.json", "result": "FAIL", "rust_native_elf_passed": true, "self_test_checks": 76, "verified_core_family_count": 3, "verified_distinct_pipeline_count": 4, "vm_native_elf_passed": true, "zig_native_elf_passed": true}
```

All five native files pass static inspection; the actual running-process library verification fails for Zig. The original output does **not** record the mismatching loaded path, mapped digest, or detailed reason. These facts are **NOT MEASURED**, not inferred.

The frozen auditor writes `candidates/audits/FROM-SCRATCH-AUDIT.json` only when every check passes. Its existing SHA-256, `6867580e7634163bd009d1f4e699d3fe4fb9ddc89b183ef60200363d1a8ab24e`, therefore remains unchanged. That older report verifies the already-qualified Rust and C implementations and the previous Zig implementation; it does **not** verify this proposal. The [preserved original failure output](../audits/FROM-SCRATCH-AUDIT-ZIG-STAGE-10-FAILURE.json), SHA-256 `03e818e7df469a4488340b4a3e7058589396e4fdc1c5587fd79acef59f2c9509`, is explicitly process-output evidence, not a passing canonical report.

## Exact rejected source

The [complete archived patch](ZIG-STAGE-10-REJECTED-NATIVE-PROVENANCE.patch) is byte-for-byte identical to the actual uncommitted changes to all three proposal source files. Its SHA-256 is `cf4efd3cf41ddee8cae2150966a91760ecadb841a164dc0aaf4199479316e82d`.

```text
GOAL.md
e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62

candidates/zig/mini_regex.zig
666d9431b5151383eefd78db3fdffc5626685260db474fbecd1d7277da605dc5

candidates/zig/py_bridge.c
dfc791360c116fabca4b782fc506ea02b67ca77f84bb500d134b4cd1154300cb

candidates/zig_candidate.py
95a2010152099f2db61595927542b2f25a675eb72bd33125659969d804360239

candidates/_zig_probe.so
1a692ca2cabcb30f9605676adac83a43685b8ef3e8aa2d3d9f4e93dd97b0e32e

candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so
411a337fef2c6a524bf58043923fb26470031e1ede5da5b8dfc67b08d06cf8bb
```

No full-Unicode run, full compatibility campaign, timing, memory measurement, or expanded-final-benchmark case was run for this rejected proposal. The **24,576-case final benchmark** remains unopened; comparative performance is **NOT MEASURED**.
