# Post-final Rust split: first independence-audit failure

This is a separate public-development experiment. The consumed 24,576-case
hidden final remains **FALSIFIED** and was not reopened or retried.

After rebuilding the independently written Rust split-batching change, the
original, unchanged independence auditor was run with the pinned Python:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  -m tools.audit_from_scratch
```

Its actual first result was:

```json
{"family_results": {"ast": true, "rust": true, "vm": true, "zig": true}, "manifest_passed": true, "native_elf_binary_count": 5, "native_elf_passed": true, "native_mapping_passed": true, "passed": false, "report": "candidates/audits/FROM-SCRATCH-AUDIT.json", "result": "FAIL", "rust_native_elf_passed": true, "self_test_checks": 0, "self_test_failures": ["isolated malicious-control subprocess exited unsuccessfully"], "verified_core_family_count": 3, "verified_distinct_pipeline_count": 4, "vm_native_elf_passed": true, "zig_native_elf_passed": true}
```

Exit status: `1`. The original auditor writes its canonical report only after a
complete passing run. Consequently, the earlier passing report remained exactly
`a790fe1a75c8748df7f8bb6f1e39d0be841636055358aaee94db0aa35523f326`;
it is **not** proof that the changed Rust bridge passed. At the first failure,
the changed bridge source was
`4379d491a68f6b218a0c0feacc9295f8d2a75ffe2ac2c5e21bd68d688c212ca2`,
and its built bridge was
`0371f3e36fe23564562d99dae480d684a0e122fd12ffda221f62394ed84c08c3`.

The failure is retained without changing an auditor, weakening a control,
inventing an explanation, running a performance measurement, or using the
hidden final test. The post-final change is **NOT QUALIFIED** until the full
original audit subsequently passes on these exact sources and binaries.

## Unchanged, isolated retry

First, the precise isolated malicious-control command used by the original
auditor was independently run and passed all 76 controls. The complete,
unchanged production audit was then rerun alone with the same command shown
above. Its actual output was:

```json
{"family_results": {"ast": true, "rust": true, "vm": true, "zig": true}, "manifest_passed": true, "native_elf_binary_count": 5, "native_elf_passed": true, "native_mapping_passed": true, "passed": true, "report": "candidates/audits/FROM-SCRATCH-AUDIT.json", "result": "PASS", "rust_native_elf_passed": true, "self_test_checks": 76, "verified_core_family_count": 3, "verified_distinct_pipeline_count": 4, "vm_native_elf_passed": true, "zig_native_elf_passed": true}
```

Exit status: `0`. The newly written, five-binary passing report is
`7c6575ee8a4dd373ebf7d59ce853fac47985b592429b9120f7d545fd184f2048`.
It verifies the changed bridge source and loaded bridge recorded above. This
does not establish correctness or speed: all unchanged correctness gates must
still complete before any post-final public timing.

## First full-campaign preflight failure

After the independent `223,198`-check matching gate, `393`-check public-object
gate, and `479`-check observability gate had each genuinely passed, the original
22-stage campaign was started with the fresh proofs:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  tools/rust_v8_multi_candidate_campaign.py \
  --module candidates.rust_candidate \
  --edge-oracle candidates/evidence/rust-v7-edge-oracle-rust-post-final-stage-01.json.gz \
  --deep-proof candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POST-FINAL-STAGE-01.json.gz \
  --output candidates/evidence/rust-v8-rust-post-final-stage-01-sealed-campaign.json \
  --memory-mib 2048
```

Its first invocation exited with status `1` before producing a campaign file or
starting its 22 correctness stages:

```text
Traceback (most recent call last):
  File "/home/dev-user/src/rebar/tools/rust_v8_multi_candidate_campaign.py", line 1439, in <module>
    raise SystemExit(main())
                     ~~~~^^
  File "/home/dev-user/src/rebar/tools/rust_v8_multi_candidate_campaign.py", line 1427, in main
    result = run_campaign(
        args.module,
    ...<3 lines>...
        args.memory_mib,
    )
  File "/home/dev-user/src/rebar/tools/rust_v8_multi_candidate_campaign.py", line 1024, in run_campaign
    audit = static_family_audit(module, edge)
  File "/home/dev-user/src/rebar/tools/rust_v8_multi_candidate_campaign.py", line 415, in static_family_audit
    require(evidence.get("passed") is True, "complete from-scratch audit failed")
    ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/dev-user/src/rebar/tools/rust_v8_multi_candidate_campaign.py", line 79, in require
    raise AssertionError(message)
AssertionError: complete from-scratch audit failed
```

The campaign correctly performs its **own** complete original independence
audit; the earlier passing canonical report is insufficient on its own. This
first campaign failure is preserved, the untouched historical hidden test
remains closed, and post-final performance is **NOT MEASURED**.

Calling the unchanged auditor's `isolated_self_test()` directly exposed the
actual first subprocess exit status without changing or replacing the auditor:

```json
{"check_count": 0, "execution": {"exit_code": -9, "expected_check_count": 76, "interpreter": "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14", "isolated_subprocess": true, "maximum_response_bytes": 262144, "validated": false}, "failed": ["isolated malicious-control subprocess exited unsuccessfully"], "passed": false}
```

`-9` establishes only that the malicious-control child was terminated; a
specific termination mechanism remains **NOT MEASURED**. No preflight check,
campaign stage, malicious-control requirement, or timeout was removed.

An identical, unchanged second campaign invocation reproduced the same
`AssertionError: complete from-scratch audit failed` before producing any
campaign report or reaching its first stage. Both failed preflight attempts
are retained; neither is represented as a passing campaign.

## Authorized unchanged campaign

The exact same pinned campaign, edge proof, deep proof, memory limit,
independence checks, malicious controls, candidate, and output path were then
run with explicitly authorized shell isolation. No frozen source or passing
threshold was changed. The genuine complete result was:

```json
{"candidate": "candidates.rust_candidate", "deep_checks": 393, "deep_public_mismatches": 0, "edge_checks": 223198, "excluded_steps": ["frozen-performance-correctness-v6", "frozen-performance-v7-integrity", "frozen-performance-correctness-v7"], "holdout_accessed": false, "mode": "sealed-practice-only", "output": "candidates/evidence/rust-v8-rust-post-final-stage-01-sealed-campaign.json", "output_sha256": "38f222f89694e13ce48bd33eb433a1234ab4da83b9e4f63b3656ac793b997413", "passed": true, "performance": "NOT MEASURED", "schema": "rebar-rust-campaign-gate-v1", "status": "PASS", "steps": 22, "timing_performed": false}
```

Exit status: `0`; all **22** original stages passed. The complete report binds
the current Rust source and loaded bridge and retains the full-Unicode,
replacement, crash, parser, public-object, and observability checks. The old
hidden final remains falsified; this is a new public-correctness qualification,
not a final winner or a performance result.
