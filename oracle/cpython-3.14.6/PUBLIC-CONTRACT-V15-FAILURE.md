# Preserve the failed first expanded Python reference

Status: **FAIL.** The first complete Stage15 Python-reference experiment
produced two matching genuine 3,584-case observation streams. Both
isolated Python workers returned all their actual results. However,
both workers and both reference fields recorded the same ordinary JSON
transport digest. The original, unchanged Stage15 correctness contract
uses a different, surrogate-aware canonical form. For the actual
preserved observations, these two genuine digests differ, so the
original Stage15 reference fails its own frozen validation.

The original evidence remains unchanged and publicly inspectable:

```text
oracle/cpython-3.14.6/evidence/public-contract-v15-self-oracle.json
755cb818f59259bb5adb05a93782afc3eef12e001c41a976ba4b9258ae54ac01
```

The ordinary durable JSON transport digest, genuinely present in both
original worker reports and both top-level record fields, is:

```text
0d6a74b1f923436c14569bfdd84431e4251f3bb8dd3129fbbcaf82a47f906b94
```

The distinct digest computed from each complete original 3,584-row
stream by the immutable surrogate-aware Stage15 validator is:

```text
7a3bed83093800085fe1bd084820108142929f60e37632b3c24a02c6a4584d72
```

The unchanged Stage15 validator rejects the authentic original report
both outside and inside its original execution context. A JSON field
claiming `PASS` does not turn this rejected first experiment into a
passing oracle.

## Frozen original experiment

```text
tools/python_re_universal_public_oracle_stage15.py
fc288f0771462a850d5ac4859ba05fe3731953e7160419ddcdbf98e8563ac580

oracle/cpython-3.14.6/PUBLIC-CONTRACT-V15.md
546c5e6152310eda173e182011cb13ab359e0960018b76cd6ce18c7b6006d691

seed: 2026072479
seed domain: rebar/python-re/public-contract/v15
matrix: 3e643ab0c455bc789e4939af2dba73af18abb033f2f34f003b49b1299b35eeeb
Python reference cases: 3,584 per worker
actual Python observations: 7,168
isolated Python workers: 2
incorrectly declared digests: 4
native candidates executed: 0
```

The failure recorder independently authenticates the already passing
12-source, five-binary V7 independence graph; the genuine four-role
146-method original Python suite; the corrected full two-reference and
three-candidate Stage14 evidence; and the preserved earlier official
Rust failure. These passed predecessors do not convert the failed
Stage15 reference into a pass.

## Preserve exactly one additional failure record

The only authorized new result is:

```text
oracle/cpython-3.14.6/evidence/public-contract-v15-reference-failures.json
```

Its schema is
`rebar-python-re-public-contract-v15-reference-failure-v1`; its actual
status and result must both be `FAIL`. Include the complete unmodified
original reference document, both 3,584-row arrays, both complete
isolated worker reports, all four actual declared transport digests,
the distinct recomputed frozen-contract digest, both
unchanged-validator rejections, the exact actual upstream provenance,
and the source fingerprints of this
recorder and protocol. Label all three candidate families **NOT RUN**.
Do not inspect candidate output locations to infer a result.

Create the additive report once with `O_CREAT | O_EXCL | O_NOFOLLOW`,
flush and synchronize the file and its real parent directory, and
verify that the original false-pass file retains its exact original
SHA-256 before and after preservation. Never modify, recreate,
overwrite, rename, or delete that original evidence. Never run a
reference worker, candidate, locale compilation, clock, benchmark,
memory measurement, hidden holdout, or performance fixture.

Freeze, commit, and push the recorder source and this protocol before
root alone records the real failure. This command exercises only
synthetic, in-memory, malicious-input and zero-effect safety checks:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/python_re_universal_public_oracle_stage15_failure.py --self-test
```

Only after freezing and pushing those two files may root invoke the
one-use actual recorder:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/python_re_universal_public_oracle_stage15_failure.py --record
```

A passing recorder self-test is not a passing Stage15 reference. The
expanded correctness gate remains **FALSIFIED**. Every full candidate
campaign, performance result, holdout, speedup, memory measurement,
ranking, and winner remains **NOT MEASURED** until a separately frozen,
independently executed replacement reference genuinely passes.
