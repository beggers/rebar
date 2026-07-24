# Frozen V12 recovery of the unchanged V11 deep-correctness format

This is an additive recovery protocol, not a new regular-expression engine, a new
test, a benchmark, an amendment to V11, or evidence that V11 finished
successfully. The exact isolated baseline is CPython 3.14.6. The unchanged frozen
original edge contains 223,198 checks in 49 categories; the unchanged frozen
original deep contract contains 393 checks, including 64 seeded cases. The
original isolated candidate and both isolated CPython references must genuinely
run. Speed is **NOT MEASURED** and the holdout is **NOT ACCESSED**.

## Preserve the actual first V11 failure

The first Rust V11 deep invocation started the original worker, which returned 0
and produced all 393 passing observations. The parent nevertheless failed before
validation because `rust_v8_deep_contract_oracle.py` requires the *parent*
environment variable `PYTHONDONTWRITEBYTECODE=1`. Python's `-B` flag does not
create that environment variable. V11 set the variable for its worker but did
not require it in its parent. Therefore the child observations were invalidated;
the first invocation did not publish a passing deep result and did not qualify.

The exact immutable original failure is
`candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-CURRENT-BUILD-V11-PRODUCER-CRASH.json.gz`,
SHA-256
`360d430666bfae146eb9abc18cab2bcd9822096f78e6f21ed3b938bb50631c39`.
Its actual integrity error is exactly `AssertionError` with the message
`PYTHONDONTWRITEBYTECODE=1 is mandatory`. Its return code is 0, it was not a
timeout, its complete stdout and stderr are retained, and its result is FAIL.

The actual complete, invalidated original is
`candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-CURRENT-BUILD-V11-INVALIDATED-AFTER-OWNER-FAILURE.json.gz`,
SHA-256
`9cc30b172575c83b399f680057a6d33ae952e44f920079c3d8c3b67566afb407`.
It must be decoded as the original compact deep archive. It records 393 original
observations, 64 seeded cases, no mismatches, and matching independent reference
and candidate observation SHA-256
`b184f3388320909b3c28fbd3ce9c15cefc992d3e852e9495ad8fb503d1cbaad8`.
Those observations do not retroactively qualify the failed invocation. V12 must
authenticate and substantively validate *both* complete archives before it
starts any retry. Never overwrite, remove, replay into, or republish these
occupied V11 failure paths.

## Require the actual parent environment first

The sole allowed real invocation is the exact pinned interpreter, with `-I -B`,
`--qualified-deep`, one named real family, and both externally supplied real
V10 report hashes. Before reading production evidence, candidate source, native
binaries, historical results, or launching any worker, V12 must check all three
actual parent environment values:

```text
PYTHONDONTWRITEBYTECODE=1
PYTHONHASHSEED=0
PYTHONPATH=/home/dev-user/src/rebar
```

`PYTHONPATH` must be exactly the resolved repository root, not a relative path,
an additional search path, an alias, a missing value, or a normalized equivalent.
CPython must really be the frozen executable, version 3.14.6, isolated, and
bytecode-disabled. Source-only self-tests must independently test this rule with
synthetic mappings; they must not require or borrow an ambient production
environment. A worker receives an explicitly constructed environment containing
exactly `PYTHONDONTWRITEBYTECODE=1`, `PYTHONHASHSEED=0`, the exact-root
`PYTHONPATH`, `LC_ALL=C`, and `PATH=/usr/bin:/bin`.

## Authenticate the real dependencies before a retry

Freeze and authenticate:

- V11 controller `tools/postfinal_current_build_proofs_v11.py` at
  `2895dd28b3dc69985cc0f6f8575398e8b8b10f58141f0612645a687478da9f04`.
- V11 protocol `oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V11.md` at
  `334405521f2f945cc58cabf246cf8f784e8a6a5be7091a20587b0daf428412af`.
- Frozen original archive validator `tools/postfinal_current_build_proofs_v8.py`
  at `0f9e12847855797669206ea89de94948da66c29742d64820a625ce5a6570b313`.
- Original deep suite `tools/rust_v8_deep_contract_oracle.py` at
  `ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978`.
- Original independent worker
  `tools/rust_v8_multi_candidate_contract.py` at
  `167f9d9114f95cd9c9821465339264f8b6eca9bf7f70b84774f4108f62f11a70`.
- Real corrected V10 owner source at
  `0c4d3f07bb51b0ce5ddc148810cb157d21067ddb07b578d3a793aaac5c671505`,
  real strict V10 source at
  `885168bd6df92ac9cabc8fc78a8389ee487f0be8d3c7fe67a393e984011b8d95`,
  and immutable native-ownership protocol at
  `902bc095d08331089dcc1d1d11233747438a0cacb0cf1057ae41a2474bde2fa6`.
- Independently supplied actual V10 base report at
  `589321a768e10c52f039a68acb211574ec884598771ede2152f91994cc69f353`
  and actual strict report at
  `d8f31dd480bdba530a454b38428a23ef347c6e3cce7796f8992d6e7767381f4b`.

Authenticate both complete real V10 audit reports with the immutable V11 audit
validator **before** historical evidence, candidate snapshots, or workers. Both
reports must qualify all three families, all 12 exact owned candidate sources,
all five actual native ELF files, and the real corrected native-owner workers.
The earlier unqualified historical V10 raw-only Rust PASS remains explicitly
unqualified and fixed at
`37de9f254dc3edb72bfe04f51cea8c528449064fba62df273032bb5d7b58b419`.

Authenticate the already published original qualified V11 edge archive and its
complete immutable V11 owner proof for the requested family. Reconstruct and
verify the exact recorded original producer streams; call the frozen original
V8 edge validator and the real immutable V11 durable-wrapper validator. Check
the actual edge denominator, zero failures, the full audited source/native
graph, real independent V10 owners, canonical bytes and exact archive/proof
fingerprints. An archive by itself or stdout by itself never qualifies.

## Publish V11-format compatibility and separate honest V12 provenance

V18 expects the original exact, as-yet-unoccupied names:

```text
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V11-PASS.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V11-PASS-PROOF.json
```

V12 may publish these exact immutable *format-compatible* original archive and
owner proof only by generating new genuine observations using the unchanged
original launcher and frozen deep suite; passing the complete bytes to the
unchanged `v8.validate_deep`; passing the actual V10 owners, complete original
process, streams and graph to the unchanged `v11.build_durable_wrapper`; and
verifying the result with the unchanged `v11.validate_durable_wrapper`. This
means V11 is the original **format and validator**, not the controller that ran
the retry. V12 must neither call `v11.refresh_deep`, `v11.run_original`,
`v11.observe_owner`, `v11.preflight_targets`, nor any V11 failure publisher.

The genuine retry must also create a separate exclusive per-family complete
canonical V12 provenance report:

```text
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V12-RETRY-PASS-PROOF.json
```

That actual report must identify the exact V12 source bytes and frozen V12
protocol, the V12 invoking controller, actual checked parent and explicit
worker environments, real original command, exact complete original worker
streams and return code, authenticated actual V11 first failure and invalidated
original, exact real V10 reports, the full 12-source/five-ELF graph, complete
real current family snapshot, genuine owner records before and after, qualified
original edge and owner proof, exact new V11-format original deep archive and
canonical owner proof, 393 original checks, and every relevant fingerprint. It
must explicitly say that the first V11 invocation failed, that V11 did not
execute the V12 retry, that the output uses the immutable V11 artifact format,
and that stdout is not durable evidence. Reject any rewritten or incomplete
provenance before publishing.

Only use canonical resolved existing evidence directories and
`O_CREAT | O_EXCL | O_NOFOLLOW`, complete file `fsync`, complete real directory
`fsync`, and exact post-publication reads. Preflight only the **passing** V11
archive/proof paths and all distinct new V12 retry paths. Never preflight the
already occupied first V11 crash or invalidation as if it needed to be fresh.
Never overwrite, truncate, delete, rename, or retry any result. An unpaired
archive, missing owner proof, missing V12 provenance, interrupted write, or
invalid final reread does not qualify.

Any actual V12 retry failure goes exclusively to distinct additive
`...-V12-PRODUCER-CRASH.json.gz`,
`...-V12-INVALIDATED-AFTER-OWNER-FAILURE.json.gz`, or
`...-V12-RETRY-FAIL-PROOF.json` paths. Preserve real completed original bytes,
real worker return code and streams, real before/after owner observations when
available, actual exception, prior immutable V11 failure, the actual current
publication state, and `campaign_qualified=false`. Never fabricate an owner,
worker, stream, result, timeout, failure, archive, or invocation. If the
V11-format compatibility artifact cannot be produced with completely truthful
additional V12 provenance, **stop without retry** and propose additive V12-only
artifacts and a separately frozen V19 public runner.

## Candidate-free controls and required order

Freeze and commit this protocol and the exact V12 source. Obtain two independent
source reviews before any real retry. Both reviewers may run only the direct
pinned `-I -B --self-test` and the `env -i PATH=/usr/bin:/bin` equivalent. The
self-test must retain the frozen V11 source-only controls and add at least 150
distinct V12 boundary, parent-environment, incident, path, provenance, stream,
immutability, denominator, and negative controls. Block candidate and external
engine imports, production/archive/report/holdout reads, subprocesses, clocks,
filesystem writes, and synthetic qualification. Self-tests must not access any
real candidate, report, evidence, benchmark, holdout, or native worker.

After reviews, a real retry must occur in exactly this order: check actual parent
environment; authenticate immutable controller and protocol; authenticate both
actual full V10 reports; authenticate both actual preserved first V11 failure
archives; authenticate real original qualified V11 edge and owner proof; check
full current audited owner graph and exclusive destinations; observe a genuine
V10 owner before; launch the unchanged original deep worker in a private `/tmp`
directory with the exact explicit worker environment; independently validate
all original bytes and observations in the correctly configured parent;
observe a genuine V10 owner after; reauthenticate every frozen audit, prior
failure, edge and full snapshot; build and independently validate the complete
immutable V11-format wrapper and complete honest V12 proof; exclusively publish
and reread the original V11-format archive, immutable V11-format owner proof,
and distinct honest V12 proof; and report only their verified fingerprints.
There is no fallback, substitute external engine, approximation, benchmark,
holdout access, weakened check, silent denominator change, or retroactive
qualification of a failed or unqualified invocation.
