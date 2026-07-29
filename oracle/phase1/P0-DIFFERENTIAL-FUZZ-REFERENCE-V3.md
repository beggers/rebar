# Two independent Python references for the preserved fuzz cases

Status: **source frozen; two-worker reference NOT RUN; phase-one gate BLOCKED**.

This is an independently runnable controller for the exact **8,244**
additional differential, property, and fuzz cases already committed in
`oracle/v2/expected.jsonl`. The cases remain separate from the original
**31,237** unchanged CPython tests. Freezing this controller does not run
Python's matcher, run a candidate, build native code, open an archive, open
the final comparison, or measure performance.

## Fixed reference

Both future workers must be genuine, separately observed executions of the
same pinned CPython **3.14.6** binary:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016
```

Each worker executes the unchanged original test runner:

```text
tools/oracle_v2.py
f038145dc0527f802203e18556f03b4bba636bb219105dc38c675c52a23e0fbb
verify --module re --output FRESH_WORKER_RESULT
```

The original runner loads its first-generation helper under its original
`rebar_oracle_v1_runner` name. The controller preserves its C locale,
Python warning behavior, byte-string handling, complete case order,
serialization, actual exit status, and all real failures. It starts two real
workers with `os.posix_spawn`, proves that their process IDs differ, drains
both stdout and stderr without importing a regular-expression engine, and
writes the original complete results into a freshly created exclusive
evidence directory.

The immutable full-corpus fingerprint is:

```text
ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2
7,602,476 bytes
8,244 independently named cases
19 case kinds
45 mapped historical obligations
7 frozen seeds
83,668 maximum actual physical line bytes
262,144 maximum permitted physical line bytes
```

The frozen source verifies the complete original parent closure, all fixed
case categories and seeds, and the inherited phase-one source-owner closure.
It verifies the pinned original Python executable by contents, device, inode,
length, and permissions. Source-only verification must report zero reference
and candidate workers, zero native activations, zero clocks, zero archive and
holdout reads, a **PASS** for the already corrected public-reference
crosswalk, and **BLOCKED** for complete phase one.

The historical one-process Python summary is not a two-worker result. The
historical private fuzz labels are not additional exclusions from the
original **13** specifically named CPython private methods. Do not merge the
original and supplemental denominators or silently claim a larger original
suite. All candidate qualification, native compilation, performance,
memory, undefined behavior, and holdout access remain unauthorized.

## Reproduce the source-only freeze

First measure the three source-owner SHA-256 values independently. With the
pinned Python executable above, run:

```text
python3.14 -I -B tools/run_owned_differential_fuzz_reference_v3.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

python3.14 -I -B tools/run_owned_differential_fuzz_reference_v3.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Repeat both commands under `env -i PATH=/usr/bin:/bin LC_ALL=C`.
These four commands must independently pass while reporting
`reference_status: NOT RUN` and `phase_gate_status: BLOCKED`.

`--run-reference` is a separate actual experiment. It is not executed when
rendering, verifying, reviewing, committing, or pushing this source-only
freeze. Any later genuine execution requires the exact frozen source,
protocol, and contract pins plus a fresh explicitly supplied safe run label.
It preserves both complete original worker results and all real errors.
