# Fresh-process Rust runtime independence, V8

Status: **SOURCE FROZEN; ROOT-ONLY LIVE PROOF NOT RUN.**

The exact V33 Rust engine passed all **31,237 original compatibility cases**
across 13 independent workers and all **10,434 public compatibility cases**.
Both actual passes authenticate the very same V33 Python adapter, native
engine, native bridge, and independently reproduced build. Its earlier V30
original-suite pass remains visible separately. The V5 static source and
native-link audit also found no external regular-expression engine.

The exact same-build V33 original-suite publication is:

    5204823a291ec01890913218582ff978cbe923dd5c787c8d6ae68a9790c43064

Two actual unsuccessful runtime experiments remain immutable and visible:

- V6 rejected Python's safe built-in `_io` import:
  `9dcc4d6dbf81ed828189cacf8e981de788190bcf9912d01b8858e6841397286b`.
- V7 terminated with exit 137, signal `SIGKILL`, and no output:
  `ba92eb59cc0dc188f2990a4d2bdacab59824d15613b36cafd700712306e12660`.

The project's earlier from-scratch audit independently recorded the same
exit 137 when extensive audit work accumulated in one process. Its recorded,
successful remedy was fresh isolated subprocesses for small bounded work.
The exact immutable source documenting that prior failure and remedy is:

    tools/audit_from_scratch.py
    4c47a77cf096df354e59d03096447c56bff890389869c6a75667a36c8471d024

V8 applies that proven architecture without claiming its historical report
covered V33: that old report audited different Rust source and native hashes.
Each of two independently built V33 phases launches eight fresh pinned Python
3.14.6 processes. A process performs only one to three fixed checks, then
exits. All 16 independent processes together perform the same 44 checks
previously attempted by two much larger V7 workers.

The frozen cohorts are `entry`, `types`, `unicode`, `replacement`,
`scanners`, `advanced`, `lifecycle`, and `serialization`. Every worker starts
without `re`, `_sre`, `inspect`, `tokenize`, an external regular-expression
package, or another candidate. It installs an irreversible CPython audit
hook and a strictly named import guard before opening its exact candidate,
loading the exact same-family engine and bridge, or matching anything.

Each worker separately authenticates all four exact source owners and both
exact native owners, rejects foreign paths, writes, dynamic libraries,
candidate families, subprocesses, networking, protected cases, and benchmark
content, and verifies both native objects in its own `/proc/self/maps`.
Audit events, mapping contents, process output, and the final durable receipt
are explicitly bounded. The parent keeps only a compact per-cohort result.

The exact independently built V33 owners are:

    adapter:        f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227
    bridge source:  f6253fbecc76b64750a22dc9393180d3ea6e3f2e29aace006c0479543e94342e
    engine source:  7412a997975aa42ec18249bc28d17e3c39223a4089bd23e3f7d2ab8112993b38
    search source:  4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7
    native bridge:  ecb19eb814430aeb571f60dd50ba4de4b3f54e7f57f056d2436c41714a257000
    native engine:  e692633896b61141734d4bb6ddce4a66b2c93bbeaa29b940fcf85904cf6a42e8

Only these three new files belong to the experiment:

    tools/verify_owned_rust_live_non_delegation_v8.py
    oracle/phase2/RUST-LIVE-NON-DELEGATION-V8.md
    oracle/phase2/rust-live-non-delegation-v8.json

The source-only gates run once normally and once under a sterile environment.
Neither mode may inspect a private build, read a candidate, load native code,
execute candidate operations, launch a subprocess, sample a clock, read a
protected case, access Git, or mutate the workspace. Source verification
authenticates exactly 24 frozen public owners, including the exact same-build
31,237-case V33 PASS, the 10,434-case V33 PASS, V6, V7, both genuine failure
receipts, and the proven earlier cumulative-SIGKILL diagnosis:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B -S tools/verify_owned_rust_live_non_delegation_v8.py --self-test

    env -i PATH=/usr/bin:/bin LC_ALL=C \
      /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B -S tools/verify_owned_rust_live_non_delegation_v8.py --self-test

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B -S tools/verify_owned_rust_live_non_delegation_v8.py --verify-source \
      --source-sha256 V8_SOURCE_SHA256 \
      --protocol-sha256 V8_PROTOCOL_SHA256 \
      --contract-sha256 V8_CONTRACT_SHA256

    env -i PATH=/usr/bin:/bin LC_ALL=C \
      /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B -S tools/verify_owned_rust_live_non_delegation_v8.py --verify-source \
      --source-sha256 V8_SOURCE_SHA256 \
      --protocol-sha256 V8_PROTOCOL_SHA256 \
      --contract-sha256 V8_CONTRACT_SHA256

After all four gates pass and all three files are committed and pushed, only
the root agent may run the frozen candidate experiment:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B -S tools/verify_owned_rust_live_non_delegation_v8.py \
      --run --root-authorized --pushed-source-sha256 EXACT_PUSHED_V8_SOURCE_SHA256

A successful run exclusively creates:

    oracle/phase2/evidence/rust-live-non-delegation-v8-actual-runtime-proof.json

It establishes runtime independence for one exact candidate and 44 exercised
operations. When the live audit actually passes, the already-authenticated
same-build original PASS, same-build public PASS, static zero-delegation PASS,
and actual live PASS qualify exactly **one** independent Rust family. Two
additional qualified families are still required. The experiment does not
measure performance, generate final cases, or select a winner.

Exact V33 original suite: **31,237/31,237 PASS**.
Exact V33 public suite: **10,434/10,434 PASS**.
Qualified families after a successful live run: **1; THREE REQUIRED**.
Performance: **NOT MEASURED**.
Winner: **NOT SELECTED**.
