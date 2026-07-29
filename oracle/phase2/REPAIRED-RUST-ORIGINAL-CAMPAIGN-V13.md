# Frozen guard-clean original Rust campaign V13

This is a source-only correctness experiment, not a passing candidate or a
performance result. It fixes the actual V12 infrastructure failure without
changing the matching engine, reducing the test suite, relaxing the runtime
guard, opening compressed evidence, or reading the performance holdout.

The baseline is the exact isolated CPython 3.14.6 interpreter. The complete
original correctness test remains 31,237 case executions across 13 suites:

- original_bounded_v5: 151;
- public_v3: 864;
- scanner_v3: 1,024;
- buffer_v3: 768;
- managed_v1: 1,024;
- scanner_verbose_v1: 2,854;
- public_types_v1: 6,912;
- substitution_v2: 5,120;
- shape_v2: 10,240;
- public_surface_v19: 1,376;
- subinterpreter_v2: 128;
- pep688_v4: 264;
- threaded_pattern_v1: 512.

The 13 existing named private waivers are unchanged. The additional 8,244
supplemental cases remain separately counted and never enter the original
denominator. The nested suite retains its original 128 cases, 394 executions,
and 11 independently guarded child interpreters.

## Preserve the real failed experiment

The V12 campaign really started all 13 original workers. None completed: all 13
failed during guarded infrastructure initialization, before a complete
matching observation. Its semantic mismatches are NOT MEASURED, its verified
passing cases are zero, and the candidate did not qualify. The controller
restored all four exact original source and native owners before publishing
its durable failure receipt.

The small, independently authenticated receipt is
oracle/phase2/evidence/repaired-rust-original-campaign-v12-rust-phase2-v19-rust-buffer-shape-root-provenance-original-p0-v12-failures-publication-receipt.json.
Its SHA-256 is
6537561a46fe6b7ab294126628fa5d82c34f03c3d0bac6455112dae3eea11658;
its size is 6,744 bytes; its device is 2064; its inode is 524989.
PASS on this receipt means durable publication only. It does not mean a passing
candidate, complete suite, working guard, or measured speed. V13 authenticates
the receipt itself and its complete V78 graph feature without opening the
separate compressed forensic archive.

## The precise repair

Under the already installed second-generation runtime guard, importing the
standard-library ctypes module immediately attempts ctypes.dlopen. That event
must remain forbidden. Four genuine historical modules each contained exactly
one eager, bare, module-level import ctypes:

- V11 controller and worker source, exact original line 18;
- V7 recovery-helper source, exact original line 16;
- V2 recovery-helper source, exact original line 15;
- V4 historical original producer source, exact original line 21.

For each source, verify its exact original device, inode, owner, mode, length,
and SHA-256 first. Parse its original Python syntax. Require the unique bare
import at the exact line, reject renamed, repeated, from-import, or dynamic
ctypes, and replace only that one statement in memory. The replacement is a
module-local inert object that raises on every attribute, including CDLL,
PyDLL, _dlopen, pythonapi, __dict__, and __class__. Never preload ctypes and
never modify or republish a historical source.

Perform this transformation only after the actual worker has installed the
unchanged V2 audit hook and selected the hash-authenticated first-party Rust
candidate. Sanitize V11 before compiling it; intercept V7 only inside the
authenticated V11 module loader; intercept V2 only inside the authenticated
V7 module loader; and intercept V4 only inside the authenticated V5 producer
loader. The original upstream suite does not load V4. Each direct or nested
suite loads it once. The unguarded controller and exact-inode recovery retain
their unmodified historical helper sources.

Source-only hostile controls authenticate and compile all four transformations
without executing their historical module bodies. They reject changed source
hashes, missing imports, aliases, repeated imports, from-imports, every inert
proxy bypass, native ctypes audit events, CPython's regex matcher, external
regex packages, and cross-family candidates. The controls do not physically
install an audit hook, import ctypes, import a candidate, open a private build
root or archive, start a process, run a clock, or open the holdout.

## Freeze the actual current evidence

Freeze the complete and truthful V78 graph, including its renderer, inputs,
summary, and SVG. Its current evidence and history lower bounds are 257 and
262. Adding only these three V13 source owners produces prospective lower
bounds of 260 and 265. Preserve the actual V12 failure, historical Rust results
of 1,440 mismatches and 14,853 verified passing cases, the historical C results,
the exact V5 original observer, the exact V2 runtime guard, and the
receipt-attested 28-process, two-phase V19 native build.

The only new owners of this source chunk are:

- tools/run_owned_repaired_rust_original_campaign_v13.py;
- oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V13.md;
- oracle/phase2/repaired-rust-original-campaign-v13.json.

## Reproduce source-only verification

Replace SOURCE_SHA256, PROTOCOL_SHA256, and CONTRACT_SHA256 with the final
complete hashes of those three files. Run both modes ordinarily and under an
empty environment. None of these four commands starts a candidate:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S tools/run_owned_repaired_rust_original_campaign_v13.py --self-test --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S tools/run_owned_repaired_rust_original_campaign_v13.py --verify-frozen-context --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
    env -i PATH=/usr/bin:/bin /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S tools/run_owned_repaired_rust_original_campaign_v13.py --self-test --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
    env -i PATH=/usr/bin:/bin /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S tools/run_owned_repaired_rust_original_campaign_v13.py --verify-frozen-context --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

## Separately authorized actual campaign

Do not execute the following command until the exact V13 source, protocol, and
contract have been separately committed and pushed and the complete actual run
is explicitly authorized. The isolated reference process must first verify the
preexisting locale fixture. Keep both en_US.iso88591 and en_US.utf8; every
candidate worker inherits LOCPATH and never runs localedef.

    env -i PATH=/usr/bin:/bin LC_ALL=C LOCPATH=/tmp/rebar-official-locale-proof-0EdjeBJ1lS /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S tools/run_owned_repaired_rust_original_campaign_v13.py --run \
      --source-sha256 SOURCE_SHA256 \
      --protocol-sha256 PROTOCOL_SHA256 \
      --contract-sha256 CONTRACT_SHA256 \
      --family rust \
      --label phase2-v19-rust-buffer-shape-root-provenance-original-p0-v13 \
      --activation-root /tmp/rebar-phase2-repaired-rust-original-campaign-v13-phase2-v19-rust-buffer-shape-root-provenance-original-p0 \
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
      --runtime-guard-contract-sha256 813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473 \
      --previous-failure-receipt-sha256 6537561a46fe6b7ab294126628fa5d82c34f03c3d0bac6455112dae3eea11658 \
      --current-graph-source-sha256 9eb7fc8ec89c93e8b2ca9acb0aee5dd9398e2aae5103a9788c3bc0abb5f0cf2b \
      --current-graph-inputs-sha256 58ba719afc7e8fd0aef8abc3e1412a122072e1443034a498558d99ec17266685 \
      --current-graph-summary-sha256 d11dd0c8aa531f430d7a5fd693a24332c9332b7b3add7423121ce9c245ae069b \
      --current-graph-svg-sha256 ff645c702b0d0e4d7222a8b65bc6fa934f58d68e1bc405c6bdaf8caa4d6767ee

The controller separately provides each real worker with the exact live
activation-report, activation-receipt, and recovery-journal hashes. Never guess
those hashes. On failure, preserve every case and error, complete four-role
reverse-order recovery, and publish the true result. Until an authorized full
run actually passes, candidate qualification and runtime non-delegation remain
NOT ESTABLISHED, candidate matching is NOT RUN, performance is NOT MEASURED,
the holdout is NOT OPENED, and no winner is selected.
