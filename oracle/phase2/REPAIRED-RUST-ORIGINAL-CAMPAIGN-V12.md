# Frozen original Rust campaign V12

This is a source-only correctness experiment. It does not claim that the Rust
candidate has passed, that the runtime guard has already guarded a candidate,
or that any speed or memory result has been measured.

The baseline is the pinned, isolated, site-free, bytecode-free CPython 3.14.6
interpreter. The campaign freezes the passing P0 V4 reference, both the
historical first-party V4 producer and the corrected guard-clean V5 producer,
and all 13 original suites in their published order. Their complete execution
denominator is 31,237 cases; the upstream suite retains exactly its 13 named
private waivers. The two independently recorded corrected-reference workers
are process IDs 81 and 82.

The build is the actual, 28-process, two-phase V19 first-party Rust source
build, identified by
`phase2-v19-rust-buffer-shape-root-provenance`. Source-only gates authenticate
its two small published receipts. The callback-bound receipt authenticates
private root device 2049 and inode 11673243, and both phases' exact first-party
engine and bridge hashes. No source-only gate opens, scans, or stats that root,
opens or decompresses a build archive, executes a compiler, or loads a native
library. A receipt is provenance, not a claim that the candidate has run.

The unchanged, SHA-256-pinned V11 implementation supplies the real original
13-worker controller, the independently runnable original worker, and the
four-role, reverse-order exact-inode recovery. The published V11 controller
remains V18-only and is never falsely presented as a V19 run. V12 authenticates
that complete source and adapts its build, graph, activation, and recovery pins
only in memory. Its separately authorized `--run`, `--worker`, and `--recover`
operations really dispatch the original controller, original suite observer,
and original exact-inode recovery. Its worker command is the actual V12 source
under `-I -B -S`, not the V11 command. Source-only gates never import or
evaluate the V11 implementation.

Every actual operation must supply all exact V19, reference, producer, root,
native, activation, recovery, runtime-guard, source, protocol, and contract
pins. A real controller derives both complete source-build phases using only
nofollow reads of the receipt-attested private source and native owners. It
never opens the build archive. Each actual suite worker physically installs
the independently published, irreversible runtime guard before importing its
one authenticated Rust candidate and own native bridge. Its operational
second-generation guard independently verifies every child interpreter before
candidate import. The frozen fifth-generation observer retains the complete
128-case, 394-execution, 11-child original suite and the authentic original
thread and locale cases. None of these cases has run in a source-only gate.

Historical original-suite infrastructure that expected to import the CPython
matcher inside a candidate process remains preserved as historical evidence,
not as an actual V12 observer. The V5 observer executes the real original
cases directly against the exact isolated Rust candidate. CPython and `_sre`
never become candidate fallbacks. If any real case fails, keep its complete
failure, retain all named suites and the entire denominator, restore all four
original inodes, and report that the candidate has not qualified. Never turn
an infrastructure failure into a waiver, a passing case, a performance result,
or runtime-independence proof.

The frozen current chart is V76, not a predecessor. Its authenticated lower
bounds are 252 evidence owners and 257 historical references. Only the three
V12 source-freeze owners imply prospective bounds of 255 and 260; those are
lower bounds, not a filesystem census. Preserve the actual Rust result of
1,440 mismatches and 14,853 verified passes, and the actual C result of 1,230
mismatches and 7,325 verified passes. Qualification remains blocked. Do not
change an existing failure, import a candidate, start a worker, open a hidden
holdout, benchmark, read a clock, or select a winner.

The sole mutable owners of this chunk are:

- `tools/run_owned_repaired_rust_original_campaign_v12.py`;
- `oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V12.md`;
- `oracle/phase2/repaired-rust-original-campaign-v12.json`.

Reproduce each source-only gate twice, once normally and once with a sterile
environment. In the commands below, replace the three lowercase hexadecimal
placeholders with the complete SHA-256 values of these exact owners:

```text
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
$PY -I -B -S tools/run_owned_repaired_rust_original_campaign_v12.py --self-test --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
$PY -I -B -S tools/run_owned_repaired_rust_original_campaign_v12.py --verify-frozen-context --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
env -i PATH=/usr/bin:/bin $PY -I -B -S tools/run_owned_repaired_rust_original_campaign_v12.py --self-test --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
env -i PATH=/usr/bin:/bin $PY -I -B -S tools/run_owned_repaired_rust_original_campaign_v12.py --verify-frozen-context --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

An actual candidate campaign is a separate, explicitly authorized operation.
Do not run it until this exact V12 source, protocol, and machine contract have
been committed and pushed, and the original locale fixture has been prepared
by an isolated reference process. Set `LOCPATH` to that independently verified
private fixture; a candidate worker never runs `localedef` or any other
subprocess. Replace only the three V12 owner placeholders below. Every other
pin is the exact previously published first-party evidence:

```text
$PY -I -B -S tools/run_owned_repaired_rust_original_campaign_v12.py --run \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256 \
  --family rust \
  --label phase2-v19-rust-buffer-shape-root-provenance-original-p0-v12 \
  --activation-root /tmp/rebar-phase2-repaired-rust-original-campaign-v12-phase2-v19-rust-buffer-shape-root-provenance-original-p0 \
  --build-private-root /tmp/rebar-phase2-native-build-v9-rust-9m_y1apm \
  --build-private-root-device 2049 \
  --build-private-root-inode 11673243 \
  --producer-source-sha256 b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538 \
  --producer-protocol-sha256 9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4 \
  --producer-contract-sha256 c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53 \
  --phase1-v4-source-sha256 8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d \
  --phase1-v4-protocol-sha256 4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2 \
  --phase1-v4-contract-sha256 aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1 \
  --build-source-sha256 650b33a10d253e09d48a423d12c8a1bb8180af4c4e96222aa13e72c75427bb5c \
  --build-protocol-sha256 4cdc322b2a516b28bf771440202efaca77074f7c8cd31c25692dc6ffc81797b5 \
  --build-contract-sha256 78e31d32cd17e100613ea98cecec4051ca2f6563b0d3b198c66f69501171ac46 \
  --build-archive-sha256 c4e3971fc207af50081d920a98d29dc06b5bdce07c5e1fb19e3e6fdf99a1c1bb \
  --build-receipt-sha256 27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc \
  --root-receipt-sha256 de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99 \
  --native-engine-sha256 5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f \
  --native-engine-bytes 658344 \
  --native-bridge-sha256 7127b1b5d6e50947e34f39e6c33ff76e71a9f753473c6d5eac0f1bdf6b0e66d4 \
  --native-bridge-bytes 148832 \
  --runtime-guard-source-sha256 f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a \
  --runtime-guard-protocol-sha256 2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c \
  --runtime-guard-contract-sha256 813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473
```

The controller supplies the actual, freshly recorded activation report,
activation receipt, and recovery-journal hashes separately to each of its 13
`--worker` processes. Emergency `--recover` additionally requires the exact
published recovery-journal hash. Never guess one of these live hashes.

A passing source gate means only that the complete original experiment and its
published first-party owners are correctly frozen. It is not candidate
correctness, runtime independence, undefined-behavior evidence, a performance
measurement, holdout access, or a winner.
