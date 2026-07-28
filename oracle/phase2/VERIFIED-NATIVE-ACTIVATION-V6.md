# V6: safely activate the two genuine Zig native outputs

Status: SOURCE FROZEN; NO ACTIVATION PERFORMED.

## Purpose

Preserve both existing user-owned Zig native files while making only the actually reproduced, independently audited Zig build eligible for a future correctness run. This freeze neither activates a regular-expression engine nor proves that it is compatible or faster.

The exact original test remains CPython 3.14.6, all 13 frozen suites, 31,237 case executions and exactly 13 named private waivers. The final 4,194,304-case holdout is NOT OPENED. Correctness, undefined behavior, speed, memory, confidence intervals, and rankings are NOT MEASURED.

## Preserve the actual published history

The published V25 overview contains 139 real evidence owners and 144 authenticated references. Its four immutable owners are separately authenticated. The complete C campaign really started 13 workers, recorded 7,325 passing case executions, 1,262 semantic mismatches and zero infrastructure failures; it failed. The later, independently reproducible Rust build used 28 real compiler and inspection processes and applied each of its two distinct source repairs twice. Neither build qualifies a matching candidate.

The actual passing Zig V11 build had the earlier 135-owner, 140-reference history at the moment it was published. Do not rewrite that historical denominator as the later V25 total. The independently published original build report and separate receipt are both passing; 26 real, distinct compiler and inspection processes built two separate source phases and applied the original signed Zig scanner repair exactly once in each. Both phases contain byte-identical but independently owned engine and bridge artifacts. All process output, original source closures, complete raw ELF evidence and no-delegation symbol audits remain authenticated.

Actual own engine: `_zig_probe.so`; 108,888 bytes; SHA-256 `caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071`.

Actual own Python bridge: `_zig_bridge.cpython-314-x86_64-linux-gnu.so`; 133,656 bytes; SHA-256 `75032107c7769f24f0c80a6e473a26dad3c74f99290e3d89bf46767e07ec3681`.

The separately derived, privately compiled scanner bridge has SHA-256 `a5ab490d0cfcbba295b68f3f738a1c6371ef3314e9a6c01cdcc0bb5978e3b148` and 173,082 bytes. The original checked-in bridge remains separately pinned and unchanged.

## Two real, existing original files

Both canonical Zig targets are originally present. The existing engine is device 2064, inode 431260, mode `0700`, 478,432 bytes, owner 1000, link count one, SHA-256 `b76eb6c7ecd60c1d221f6ddb822573a5f962641cf4e6f16da75d21561b104652`. The existing bridge is device 2064, inode 431274, mode `0700`, 134,112 bytes, owner 1000, link count one, SHA-256 `d8ac0da492d960716cbc74c25d7cb5027aea3fcfe2bf0a6fb2ec8e432345fb3b`.

Self-test, context verification, and contract rendering do not open, stat, hash, link, copy, modify, or replace either canonical target. The stated original identities are explicit independently observed preconditions; the future activation must verify them before any change.

## Real original-inode preservation

The independently hash-pinned V2 dual-role activation source supplies mature no-follow reading, private `0700` root verification, exclusive `0600` journal creation, durable control files, candidate directory ownership and directory synchronization. Its byte-copy restoration is deliberately forbidden.

An explicitly requested future activation first verifies all evidence and both original files. It exclusively creates and synchronizes a fresh `0700` private journal before any canonical operation. For each role, it first writes and synchronizes a role-specific hardlink intention. It then creates an adjacent, same-directory, no-follow hardlink to the exact original inode. The original link count is verified changing from one to two; the genuine backup is synchronized. A separate synchronized promotion intention is written before creating an exclusive adjacent stage initially mode `0600`. Only complete source-built bytes may enter that stage; the original `0700` mode is restored before promotion. Each same-directory replacement and the candidate directory are synchronized.

Engine and bridge replacements are individually atomic. Replacing two files is NOT group-atomic. An interrupted activation remains recoverable directly from its original pinned journal even before an activation report exists. Recovery verifies the real promoted and backed-up inodes, then atomically moves the original hardlinked bridge inode back first and the original hardlinked engine inode back second. It proves each exact original device, inode, bytes, SHA-256, `0700` mode, user and final link count one. Unrelated, symlinked, foreign, changed or missing original targets are never deleted or overwritten. The C and Rust native files are never targets.

No actual target promotion is implicit. After an activation, the complete original correctness campaign must restore both targets successfully before it publishes or qualifies a result.

## Four source-only gates

Replace `SOURCE_SHA256`, `PROTOCOL_SHA256`, and `CONTRACT_SHA256` with the three exact independently frozen owner digests:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/activate_verified_native_candidate_v6.py --self-test --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/activate_verified_native_candidate_v6.py --verify-frozen-context --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/activate_verified_native_candidate_v6.py --self-test --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/activate_verified_native_candidate_v6.py --verify-frozen-context --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Every gate must report zero actual activations, target reads, target stats, native links, native replacements, candidate imports, builds, compiler processes, clocks, holdout reads, and workspace mutations. Future activation and reportless recovery are separate, caller-pinned operations; this freeze invokes neither.

Holdout: NOT OPENED. Matching: NOT MEASURED. Performance: NOT MEASURED. Memory: NOT MEASURED. Winner: NOT SELECTED.
