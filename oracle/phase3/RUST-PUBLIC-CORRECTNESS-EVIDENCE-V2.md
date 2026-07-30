# Rust public correctness evidence v2

PUBLIC DEVELOPMENT/PRACTICE ONLY. This separate controller never opens,
enumerates, derives from, or authorizes a sealed final holdout, private
benchmark, hidden test, fixture, or historical archive. A result never
qualifies a candidate or selects a final winner.

The existing public benchmark remains byte-for-byte unchanged. Its
`--correctness-only` mode deliberately writes nothing and returns exit 1 when
any mismatch exists. The independent evidence controller treats that genuine
FAIL as a complete, valuable result, never as a reason to suppress failures.

## Independently frozen public inputs

- Controller source: `tools/run_rust_public_correctness_evidence_v2.py`.
- Controller protocol: `oracle/phase3/RUST-PUBLIC-CORRECTNESS-EVIDENCE-V2.md`.
- Controller manifest: `oracle/phase3/rust-public-correctness-evidence-v2.json`.
- Immutable existing benchmark source SHA-256:
  `a3d7e70343d231bf433fbad6a6669025a970d83691c49cb9f434a186aef3d9e6`.
- Immutable existing benchmark protocol SHA-256:
  `4040c458119a6d347c1eb876e1120a4400f76b8f16611d21de15371b50508586`.
- Immutable existing benchmark manifest SHA-256:
  `7c4120c549a006cc162abb545032e1808637cf3c088f4a21023d5c99fb351e4a`.
- Frozen canonical public matrix SHA-256:
  `0c88d1ec7066ede05466c1a91126086cd52256548eda13a31778ff284439d97d`.
- Exact denominator: 10,434 cases, consisting of 5,217 text and 5,217 bytes
  cases from 94 public datasets and 111 equally weighted operations.
- Exact official interpreter:
  `/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14`.

The three *controller* owner digests are supplied independently by the caller
after the controller source, documentation, and manifest are frozen. They are
not confused with the three immutable preexisting benchmark owner digests.

## Exact evidence boundary

An authorized run launches precisely this one isolated official process:

```text
python3.14 -I -B tools/rust_public_practice_benchmark_v2.py --correctness-only
```

That immutable process starts one separately isolated standard-library worker
and one separately isolated Rust worker. Its complete single-line canonical
stdout includes all 10,434-case baseline and Rust vector SHA-256 digests,
distinct genuine worker PIDs, the exact denominator, and **every mismatch**
with both complete original outcomes. The controller retains that stdout
byte-for-byte as the primary evidence file, including when the process exits 1
for a genuine FAIL. Its separately durable receipt repeats every mismatch,
records the complete stdout SHA-256 and byte length, authenticates all source,
runtime, and candidate owners, and retains all distinct process identities.

The immutable benchmark does **not** expose individual passing per-case
outcomes in correctness-only stdout. The full 10,434-case worker vectors are
represented by their authentic complete-vector digests. The controller never
claims to have individual passing records, fabricates them, reruns candidate
code to recover them, or changes the benchmark to produce them.

The root coordinator must not run any currently restored Rust candidate whose
changing-exporter capture path lacks the required bounds clamp. Actual
execution is allowed only after a safe clamped first-party variant has been
compiled, activated, caller-pinned, and explicitly acknowledged.

## Physical source-only boundary

`--verify-source` and `--self-test` install a one-way audit wall that permits
reads of exactly six named first-party public source/protocol/manifest files.
They reject candidate imports and owner reads, process launches, clock calls,
native-owner reads or activation, external communication, filesystem
mutations, foreign owner reads, and holdout/archive/fixture access. The
synthetic self-test attempts each class through the actual installed wall and
also rejects malformed canonical JSON, hidden FAILs, omitted or reordered
mismatches, substituted domains or operations, forged worker PIDs, changed
vector digests or denominators, hidden timing/holdout reads, forged typed
buffers, and unauthorized publication paths.

Replace the three uppercase placeholders with independently frozen SHA-256
digests of the controller source, this protocol, and its manifest:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/run_rust_public_correctness_evidence_v2.py --verify-source \
  --source-sha256 CONTROLLER_SOURCE_SHA256 \
  --protocol-sha256 CONTROLLER_PROTOCOL_SHA256 \
  --manifest-sha256 CONTROLLER_MANIFEST_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/run_rust_public_correctness_evidence_v2.py --self-test \
  --source-sha256 CONTROLLER_SOURCE_SHA256 \
  --protocol-sha256 CONTROLLER_PROTOCOL_SHA256 \
  --manifest-sha256 CONTROLLER_MANIFEST_SHA256
```

Neither source-only command accepts a candidate pin, runtime-binary pin,
output path, root authorization, published commit, or actual-run flag.

## Exclusive root-only durable publication

Only the root coordinating agent may run this command, and only after all
controller owners have been committed and pushed and a safe clamped
first-party Rust candidate has been compiled and activated. The root must
independently pass the exact canonical public adapter, semantic native Rust
engine, canonical official-ABI bridge, and pinned CPython executable SHA-256
values; the controller checks those four owners both before and after its one
comparison.

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/run_rust_public_correctness_evidence_v2.py --run \
  --source-sha256 CONTROLLER_SOURCE_SHA256 \
  --protocol-sha256 CONTROLLER_PROTOCOL_SHA256 \
  --manifest-sha256 CONTROLLER_MANIFEST_SHA256 \
  --python-sha256 PINNED_CPYTHON_SHA256 \
  --adapter-sha256 CANONICAL_PUBLIC_RUST_ADAPTER_SHA256 \
  --native-engine-sha256 FIRST_PARTY_RUST_ENGINE_SHA256 \
  --native-bridge-sha256 OFFICIAL_CPYTHON_RUST_BRIDGE_SHA256 \
  --published-commit FORTY_CHARACTER_PUSHED_COMMIT_SHA \
  --root-authorized --frozen-committed-pushed --safe-clamped-candidate \
  --output oracle/phase3/evidence/rust-public-correctness-v2.json
```

The only approved directory prefixes are `oracle/phase3/evidence/` and
`experiments/rust_public_practice_v2/`. The report and its
`-publication-receipt.json` companion are distinct exclusively created
`O_NOFOLLOW | O_EXCL` files; no existing file can be replaced. Each complete
file and retained no-follow parent directory is `fsync`-durable and each full
byte-for-byte readback is independently verified. No timing, hidden cases,
fixtures, archives, sealed final holdout, qualification, or winner selection
is allowed.
