# Refresh the current-build correctness proofs

Status: **NOT RUN.** No refreshed edge proof, deep proof, or complete
correctness campaign has yet passed. Speed, memory use, held-out
performance, rankings, and a winner are **NOT MEASURED**.

## Why a refresh is necessary

The first real attempt to run the frozen 22-stage Rust campaign stopped
before its first correctness stage. Its old correctness proof identified
an earlier Python wrapper and native bridge, not the rebuilt engine. The
unchanged first-failure record is:

```text
candidates/evidence/rust-v8-rust-postfinal-locale-v7-sealed-campaign-first-failure.json
62aba93fa8bdd6df7be93199aea6f58be7b24c095750c520179e96b98084b75a
```

It records `AssertionError: the RUST public-python is stale or
unproven`, zero completed campaign stages, and zero matching workers.
This is a genuine failed experiment. It must remain unchanged and must
not be counted as a candidate failure, a passed campaign, or a benchmark.

The exact immutable goal remains:

```text
GOAL.md
e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62
```

## Frozen prerequisites

Run everything with the unmodified, pinned CPython:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
Python 3.14.6; Unicode 16.0.0
```

The additive refresh controller is
`tools/postfinal_current_build_proofs_v7.py`. Freeze, commit, and push
the controller and this protocol before starting a real candidate.
Every invocation verifies the exact frozen original inputs before it
can start a worker:

```text
tools/rust_v7_edge_oracle.py
fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca

tools/rust_v8_deep_contract_oracle.py
ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978

tools/rust_v8_multi_candidate_contract.py
167f9d9114f95cd9c9821465339264f8b6eca9bf7f70b84774f4108f62f11a70

candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz
db43cbf8be1d6891eb4f009b8ae92995a6434f9753b944fbf0a8ed0b44237192

tools/postfinal_from_scratch_audit_v7.py
defa306e47a0d325af7d4c7fabb54324f6cb6d4653a494c46846838f5e2cf487

candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json
efae1f94fb06a1eabbab352794410c4d8e20a78202dcbf769b08ff9c7cee130a

tools/postfinal_no_delegation_audit_v7.py
9283457064f32658747b449c4ee6ebd20ca7cc7dc442ce03ece6b02896cff4e4

candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json
1f71caac01bffdffbf7ffdc2e21a9aa8d6936c452051cbdaa4c90ac67010fd34

tools/rust_v8_multi_candidate_campaign_postfinal_v7.py
92e397149585ee35ce5d26e984f00d093992471d3e92b929f65dd0386f75b243

tools/rust_v8_multi_candidate_campaign.py
46e53abac0d2347d5fc505aa792a5ee5f55489a6e73b1f57edf37a93a0a6d45d

oracle/cpython-3.14.6/POSTFINAL-CAMPAIGN-V7.md
dd7e6f80128fb9c8198398755caa178ede0a0ce178fedce2049a7e066be3250c
```

Both passing source audits, all 12 current owned production source
files, and all five current owned native binaries must still have
their exact audited SHA-256 values. Rust, C, and Zig must retain
independent matching implementations. Python `re`, `_sre`, an external
regular-expression package, or another candidate cannot do their
matching.

## Refresh one complete edge proof at a time

The original edge suite, original seed `2026072329`, original eight
generated edge cases, original Unicode stride `4099`, all 223,198
observations, and all 49 categories are unchanged. The original edge
writer is not safe to run directly against a final evidence path: it
would overwrite an existing file. The additive controller runs the
unchanged writer only inside a fresh private `/tmp` directory, checks
the complete result and every current native role against the original
frozen validator, and publishes a passing deterministic gzip archive
with exclusive, no-follow creation. It never replaces an archive.

Run, verify, record, commit, and push **one** family before starting
the next chunk:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_current_build_proofs_v7.py \
  --edge --module candidates.rust_candidate

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_current_build_proofs_v7.py \
  --edge --module candidates.vm_candidate

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_current_build_proofs_v7.py \
  --edge --module candidates.zig_candidate
```

The only permitted published edge paths are:

```text
candidates/evidence/rust-v7-edge-oracle-rust-postfinal-locale-v7.json.gz
candidates/evidence/rust-v7-edge-oracle-vm-postfinal-locale-v7.json.gz
candidates/evidence/rust-v7-edge-oracle-zig-postfinal-locale-v7.json.gz
```

A failed original edge run publishes no passing evidence. Its actual
complete failure is preserved byte for byte in a separate, exclusively
created, no-follow first-failure archive. The original Python
reference, unchanged edge source, seed, category denominator, all
mismatch rows, and the exact current owned native roles are checked
before preservation. The failure never occupies a passing evidence
path and can never qualify a candidate. The only authorized edge
failure paths are:

```text
candidates/evidence/rust-v7-edge-oracle-rust-postfinal-locale-v7-first-failure.json.gz
candidates/evidence/rust-v7-edge-oracle-vm-postfinal-locale-v7-first-failure.json.gz
candidates/evidence/rust-v7-edge-oracle-zig-postfinal-locale-v7-first-failure.json.gz
```

Check that both a family's passing path and its first-failure path are
absent before starting its edge worker. Never retry over an existing
failure. If the original worker crashes without writing an archive,
report its actual exit code and complete available diagnostics without
inventing completed observations or a passing result.

## Refresh one complete deep proof at a time

Each deep run uses its own freshly passed current-build edge archive.
It invokes the unchanged frozen multi-candidate producer and retains
the original seed `2026072347`, all 393 cases, all 64 seeded cases,
both independent Python reference streams, the active Python and
cross-engine poison guards, and every original matching observation.
The original producer exclusively creates its actual passing **or
failing** archive. A real failure remains on disk, remains a failure,
and is never replaced or automatically retried.

Run, verify, record, commit, and push each family separately:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_current_build_proofs_v7.py \
  --deep --module candidates.rust_candidate

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_current_build_proofs_v7.py \
  --deep --module candidates.vm_candidate

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_current_build_proofs_v7.py \
  --deep --module candidates.zig_candidate
```

The only permitted published deep paths are:

```text
candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-LOCALE-V7.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-C-POSTFINAL-LOCALE-V7.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-LOCALE-V7.json.gz
```

The C candidate's public module is `candidates.vm_candidate`; its
deep-proof family is `C`, not `VM`.

## Candidate-free verification

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_current_build_proofs_v7.py --self-test
```

The self-test uses only authenticated source, audit, and failure
records and clearly identified, in-memory synthetic controls. It
cannot start a candidate, create a temporary directory, publish
evidence, access a benchmark or holdout, or turn a synthetic case into
a production proof. It must reject changed frozen inputs, stale
production roles, crossed family paths, missing observations,
noncanonical gzip, poisoned reference digests, hidden mismatches,
missing active guards, counterfeit or crossed passing and failure
archives, and existing outputs.

A successful self-test is **not** an edge pass, a deep pass, a complete
campaign, or a performance result. Resume the unchanged 22-stage
campaign only after the actual matching family has both freshly
generated, fully passing, current-build proof archives.
