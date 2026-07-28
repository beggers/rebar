# Freeze one first-party Zig scanner correction

This is a source freeze, not a candidate result. No original implementation is changed, no Zig engine is built or loaded, and no matching or speed is measured.

The isolated baseline remains stable CPython 3.14.6 with the unchanged 13-suite, 31,237-case correctness oracle and its 13 named private waivers. The committed V21 graph preserves exactly 103 actual evidence owners and 108 distinct digest-addressed historical references. They are different counts. All 25 original source owners, the six independent implementation families, the corrected V3 producer, and every original Zig failure remain independently authenticated.

## The frozen source change

Original owned file: candidates/zig/py_bridge.c.

Original file SHA-256:

    67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b

Original size: 173,026 bytes.

The only changed function is zig_scanner_project_match. Its original 190-byte block has SHA-256:

    42009e889c83ee06194f14223b629bb221326ce7a3ebf3efe09f5d1a76344978

The derived 246-byte block has SHA-256:

    7a7fa3a9a16d9dae07e74845984bbd36d17309c1f06ddb091d6d3986b4e27177

It guards the original branch fallback with:

    if (match->spans[branch_group] < 0)

An existing locally projected capture is preserved. A branch without a local capture still receives its original whole-match fallback. The existing lastindex, range and overflow checks, branch identification, native-last handling, iterator lifetime, matching engine, replacement, buffer handling, and every other source byte remain unchanged.

The exact derived complete source SHA-256 is:

    a5ab490d0cfcbba295b68f3f738a1c6371ef3314e9a6c01cdcc0bb5978e3b148

Derived size: 173,082 bytes. The derived source is not materialized by either verification mode.

## What remains observed

The original complete Zig result is still FAIL: 1,764 observed mismatches, zero qualified candidates, and 3,583 passing individual cases that do not qualify the candidate.

The scanner-verbose receipt still contains all 620 actual failures out of 2,854 cases. The source change has not been built or run; no claim is made that any case now passes. The 64 distinct scanner failures, 248 public-type failures, 64 substitution failures, 672 changing-buffer failures including 176 Match.expand failures, and 96 public-surface failures are not hidden, removed, or called repaired. The recorded subinterpreter infrastructure failure is not reclassified as a semantic success. The passing 1,024-case managed-buffer receipt is retained.

The independently owned Zig implementation remains exactly three original source files. Its pinned stable Zig 0.16.0 compiler is authenticated but never executed. No third-party regex package, CPython regex implementation, candidate fallback, another candidate family, or substitute compiler is used.

The 4,194,304 planned final comparison cases are NOT OPENED. Speed, confidence intervals, memory, undefined behavior, and corrected-candidate correctness are NOT MEASURED.

## Source-only gates

Every command uses the independently pinned stable interpreter:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B

Use the exact independent SHA-256 digests of the new tool, this protocol, and its canonical JSON contract.

The two source-only self-tests are:

    python -I -B tools/apply_owned_zig_scanner_capture_source_repair_v1.py \
      --self-test --source-sha256 SOURCE_SHA256 \
      --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

    env -i PATH=/usr/bin:/bin python -I -B \
      tools/apply_owned_zig_scanner_capture_source_repair_v1.py \
      --self-test --source-sha256 SOURCE_SHA256 \
      --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

Replace python with the exact stable interpreter shown above. Synthetic controls block and count every filesystem read or write, compiler, candidate import, subprocess, network, thread, holdout operation, and performance clock.

The two complete read-only context checks use the same ordinary and sterile commands with --verify-frozen-context instead of --self-test. They independently authenticate all 108 historical evidence references, the exact 103-owner V21 accounting, all 25 distinct semantic source owners, the corrected V3 producer, the original Zig failure receipts, the compiler lock, and the original official compiler bytes. No existing build-controller source is accessed.

## Future application is not authorized

An explicit --apply invocation is a separate future operation. If separately authorized, it can only exclusively create a mode-0600 derived file under a fresh owner-only mode-0700 private snapshot:

    /tmp/rebar-phase2-zig-scanner-capture-source-build-v1-PRIVATE/
      reference-a/source/candidates/zig/py_bridge.c

The independent reference-b phase has the same restrictions. Both phase roots must already exist, be distinct, and be owned by the current user. A repository path, pre-existing destination, symlink, cross-family phase, wide path, native artifact, compiler invocation, activation, benchmark, or holdout operation is forbidden. This freeze does not invoke --apply.
