# Preserved common-prefix verification incidents

This report concerns public-practice verification. Neither incident generated a final test case, opened the final secret, measured the final benchmark, or changed any matching engine.

## First synthetic verifier self-test failed

The first version of the dedicated practice verifier had source SHA-256 `58f5f9650d93e60d6acde045c96cdbcbd26b37cd54719813d31f4390f23e4864`. Its unchanged command was:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  -m tools.rust_v7_multi_candidate_practice_v5_audit self-test
```

Its actual first exit status was **1**, with the recorded error:

```json
{"error":"the recorded original Rust source is not v1","failed":1,"holdout_accessed":false,"result":"FAIL","schema":"rebar-v7-multi-candidate-practice-integrity-v5","timing_performed":false}
```

The synthetic test had incorrectly given earlier practice fixtures the current Rust bridge identity. The verifier was corrected to retain the actual, different bridge identities of each historical experiment; no source, history, candidate, native-library, confidence, or regression check was removed. Its corrected source is `7236508d80094d5c7a4fd3e33725b6e9485b73b7cdacd33b6a72d2ccc4cf6590`.

The same original command subsequently returned **0** and passed all **119** corruption controls. Only afterward did the independent [actual-result replay](three-qualified-engines-public-practice-v5-integrity.json) verify all **17,472** observations, **1,875** confidence intervals, **407** slowdowns, and all five current native libraries. The failed synthetic run was not a failed engine-correctness test, a real-data replay, or a final-benchmark run.

## Overly broad read-only review was quarantined

A delegated public-practice reviewer used `rg --files tools practice` followed by an `rg -n` search over `tools`. Those commands exposed final-protocol and holdout-named Python **source paths** outside the reviewer's authorized scope, including `tools/performance_v9_charts.py`, `tools/rust_v9_holdout_protocol.py`, `tools/performance_v9_results_audit.py`, and `tools/rust_v9_opening_custodian.py`. Their content search matched holdout-named protocol source.

The reviewer reported the scope violation, stopped, and was excluded from this verification, final-protocol work, and all future hidden-data review. A replacement reviewer was restricted to explicit public-practice files. The original reviewer read **no final secret, opening bytes, unseal marker, hidden workload, final-case data, or final results**; ran **no candidate, benchmark, correctness suite, or final protocol**; and changed **no file or Git state**.

The [unchanged original final-protocol verification](../../v9/evidence/HOLDOUT-PROTOCOL-VERIFIED.json) continues to report `opening_read=false`, `hidden_cases_generated=0`, and `timing_performed=false`. This record does not treat protocol-source exposure as hidden-case access or claim that the scope violation never occurred.

Final benchmark: **NOT ACCESSED**. Final performance: **NOT MEASURED**.
