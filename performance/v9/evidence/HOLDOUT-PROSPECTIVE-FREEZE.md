# Expanded performance test: genuinely frozen, not opened

The **24,576-case** final benchmark is prospectively sealed after Rust, C, and Zig each pass their full **22-stage** correctness campaigns, and before further candidate optimization. This document reports the public commitment and its reproducible controls. It does not report performance.

## Exact frozen test

- Reference: CPython **3.14.6**.
- Cases: **24,576**; **12** operations × **8** workloads × **256** cases.
- Paired rounds: **31**; **16** actual public calls per timing sample.
- Overall confidence calculation: **9,999** predeclared, whole-case bootstrap draws.
- Four-engine timing rows: **3,047,424**.
- Before, during, and after correctness comparisons: **9,142,272**.
- Separate memory cases: **1,536** per engine.
- Success requires an overall lower confidence bound of at least **1.5×** and at least **14,746** individually significant faster cases.
- Hidden final cases generated: **0**.
- Hidden final cases read: **0**.
- Final timing and memory: **NOT MEASURED**.

The exact [frozen public manifest](../holdout-manifest.json) has source binding `a699ce1e661ead447af0643584d69f080e72712059ad611fbd6b998f2ca19219` and manifest binding `1ebfa3b1a57c285826627e0362c78daff016b4029529639502325550a1ac0aaf`.

## One genuine, unpublished opening

The [auditable custodian](../../../tools/rust_v9_opening_custodian.py) uses operating-system randomness to create the specified **32-byte**, owner-only opening exactly once. Its public commitment is:

```text
3ad3ff2bc34fd1dc371aa6516ac0a122f1d3e3e9da373d0db8c5cb5589da5bbb
```

The [original creation attestation](HOLDOUT-CUSTODIAN-ATTESTATION.json) records exclusive file creation, mode `0600`, owner verification, file and directory synchronization, no read-back, and zero candidate imports, final-case generation, or performance observations. The actual opening is outside the repository. It was never printed and will not be read until the single authorized final measurement.

The protection is **procedural, not an operating-system security boundary**. The custodian and candidates run as the same operating-system user; the experiment does not claim that a malicious process under that account is unable to inspect the file.

The custodian's independently archived [27-control synthetic self-test](HOLDOUT-CUSTODIAN-SELF-TEST.json) verifies rejection of an existing file, symlink, zero-byte write, and failed synchronization. It verifies safe partial writes, private file permissions, one-line public-only output, domain-separated synthetic input, and erasure of the working secret buffer. This self-test never touches the actual opening.

## The real manifest-bound gate

The original frozen performance protocol generated the manifest using only the custodian's **public** digest:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  -m tools.rust_v9_holdout_protocol manifest \
  --opening-sha256 3ad3ff2bc34fd1dc371aa6516ac0a122f1d3e3e9da373d0db8c5cb5589da5bbb
```

The [original first manifest check](HOLDOUT-PROTOCOL-MANIFEST-VERIFY.json) passes without opening a hidden case. The [manifest-bound synthetic proof](HOLDOUT-PROTOCOL-SELF-TEST.json) then passes all **75** controls, including **70** intentional poisons. Unlike the previously committed public-dummy check, its `manifest_mode` is `committed-prospective-manifest` and its `manifest_sha256` is the exact current frozen manifest.

Reproduce the complete independent proof without accessing the opening:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  -m tools.rust_v9_holdout_protocol verify \
  --manifest performance/v9/holdout-manifest.json --evidence
```

The [genuine final verification](HOLDOUT-PROTOCOL-VERIFIED.json) reports `failed=0`, `opening_read=false`, `hidden_cases_generated=0`, `candidate_imported=false`, and `timing_performed=false`. It independently recalculates and verifies the entire manifest-bound synthetic report.

## Candidate and objective state

The pre-optimization qualifying commit is `0df60778f47199458739f35966af1109a1f4894e`. Its three independently written engines each pass all **22** original safety and compatibility stages. The four-family from-scratch audit verifies all **five** actual native binaries and all **76** anti-delegation controls. Candidate selection will be frozen separately after subsequent practice-only optimization; the final opening remains forbidden until that later freeze, preflight, and explicit single-use authorization.

The unchanged objective `GOAL.md` has SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`. There is no winner, final ranking, final confidence interval, or final speed result. Performance is **NOT MEASURED**.
