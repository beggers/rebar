# C Stage 20: preserved independence-audit retry

The original, unchanged independence auditor is `tools/audit_from_scratch.py`, SHA-256 `4c47a77cf096df354e59d03096447c56bff890389869c6a75667a36c8471d024`. No audit rule, malicious control, engine source, benchmark case, final-test secret, or passing threshold was altered after the failure described here.

## Original first failure

While checking the fully correctness-qualified C scanner change, the main agent incorrectly started the original production independence audit in parallel with the same auditor's synthetic self-test and a no-opening final-manifest verification. The production audit's isolated malicious-control subprocess failed. Its actual standard output and nonzero exit status were:

```json
{"family_results":{"ast":true,"rust":true,"vm":true,"zig":true},"manifest_passed":true,"native_elf_binary_count":5,"native_elf_passed":true,"native_mapping_passed":true,"passed":false,"report":"candidates/audits/FROM-SCRATCH-AUDIT.json","result":"FAIL","rust_native_elf_passed":true,"self_test_checks":0,"self_test_failures":["isolated malicious-control subprocess exited unsuccessfully"],"verified_core_family_count":3,"verified_distinct_pipeline_count":4,"vm_native_elf_passed":true,"zig_native_elf_passed":true}
```

Exit status: `1`. The existing passing canonical audit report remained byte-for-byte `f875068b829482d0c5dd28290a5706dd0a5c0ed91018b857cee82b6defe40f0a`; the failed run did not overwrite it. Concurrency is an observed difference in invocation, not proof of a particular subprocess failure mechanism.

## Isolated original retry

The unchanged original production audit was then run on its own:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  -m tools.audit_from_scratch
```

Its actual standard output was:

```json
{"family_results":{"ast":true,"rust":true,"vm":true,"zig":true},"manifest_passed":true,"native_elf_binary_count":5,"native_elf_passed":true,"native_mapping_passed":true,"passed":true,"report":"candidates/audits/FROM-SCRATCH-AUDIT.json","result":"PASS","rust_native_elf_passed":true,"self_test_checks":76,"verified_core_family_count":3,"verified_distinct_pipeline_count":4,"vm_native_elf_passed":true,"zig_native_elf_passed":true}
```

Exit status: `0`. The exact 76-control, four-family, five-native passing report remains `f875068b829482d0c5dd28290a5706dd0a5c0ed91018b857cee82b6defe40f0a`. Subsequent independence audits and corruption self-tests must run one at a time. The 24,576-case final benchmark remains unopened and **NOT MEASURED**.
