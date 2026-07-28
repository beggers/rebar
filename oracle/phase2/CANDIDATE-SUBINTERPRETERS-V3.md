# Verify real independent Python interpreters without changing Python's tests

The original Python interpreter oracle remains unchanged: **128** ordered
cases, **394** genuine matching observations, **11** independently created and
destroyed interpreters, **11** matcher-guard initializations, and **11** guard
cleanups. These checks are additional proof of the original **13-suite,
31,237-case** correctness standard. They are never added to that denominator.

Freeze, commit, and push this document, the machine-readable
[`candidate-subinterpreters-v3.json`](candidate-subinterpreters-v3.json), and
[`../../tools/run_owned_candidate_subinterpreters_v3.py`](../../tools/run_owned_candidate_subinterpreters_v3.py)
before recording an actual version-three candidate. Their synthetic
`--self-test` neither reads a file nor creates an interpreter, candidate,
native build, worker, activation, timing result, or benchmark evidence.

## Preserve the actual failure

The published original C run genuinely failed before matching its first
interpreter case. Its
[complete failure archive](evidence/owned-candidate-subinterpreters-v1-c-phase2-v5-subinterpreters-failures.json.gz)
is SHA-256
`e375edafd74a0b77e349178b59d2d38d2cf423272b9b91dfb4baad91ad94c0f6`.
Its independently durable
[failure publication receipt](evidence/owned-candidate-subinterpreters-v1-c-phase2-v5-subinterpreters-failures-publication-receipt.json)
is SHA-256
`3e05efd1a83cd650ab3d91cebf0380df0f0cacd5758e6c92f91e08f8acd26a62`.
The uncompressed complete report is **14,943 bytes**, SHA-256
`24a0dbc4bb7e331f5bec729b58476d159e16c5bfcbab2ba651dcea33377a7b9c`.

The actual failed worker, process **204**, created interpreters A and B,
started **one** guard initialization, ran **zero** matching cases, and
recorded both real failed cleanup attempts. Its exact error was:

```text
an exact independently owned source or native size is mandatory
```

The frozen original interpreter wrapper supplied a **256 MiB** maximum to the
unchanged original matcher guard, whose independently frozen upper limit is
**128 MiB**. A valid C extension was **163,136 bytes**. The error proves a
wrapper-size incompatibility; it does not prove a candidate matching failure
or a passing interpreter case. The successful publication of a failure
receipt means only that the actual failure was durably preserved.

Preserve the complete original C campaign: all **13** recorded suite
outcomes, **7** passing suites, **6** failing suites, **7,197** genuinely
executed passing cases, **16** distinct actual process identities, the
complete failure streams, and
[byte-for-byte restoration of the original C native file](evidence/frozen-p0-candidate-v5-c-phase2-v5-restoration-receipt.json).
The restored original binary is SHA-256
`075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd`.
No earlier candidate failure is erased or upgraded to a qualification.

The independently built Rust candidate failed for a genuinely different
reason. Preserve its
[complete failed Rust interpreter report](evidence/owned-candidate-subinterpreters-v1-rust-phase2-v5-subinterpreters-failures.json.gz),
SHA-256
`b73ea6fd2f944a46bbc89a593df251a054f62bed288b60765eb3c9dc3a9619cd`,
and its independently durable
[Rust failure publication receipt](evidence/owned-candidate-subinterpreters-v1-rust-phase2-v5-subinterpreters-failures-publication-receipt.json),
SHA-256
`99b32d784182800b92b3fcb555add6c8d27d599a91dc5255b46ca597667c6049`.
The exact static-audit process was **203**. Its genuine failure was:

```text
candidates/_rust_engine.so: unexpected native library identity
```

No Rust interpreter worker started; no Rust interpreter was created and no
interpreter matching case ran. This was not the C wrapper's **256 MiB** size
failure. Preserve Rust's actual **13** suite reports, **8** passing suites,
**5** failing suites, **7,461** genuinely executed passing cases, and **15**
distinct actual process identities. Also preserve
[byte-for-byte restoration of both original Rust native files](evidence/frozen-p0-candidate-v5-rust-phase2-v5-restoration-receipt.json),
whose receipt is SHA-256
`3cd828fbd507d048d0e80715efef754930e89f3c176717ba1dd8985784832889`.
Publication of either failed result does not qualify either candidate.

## Correct only the authenticated byte sizes

Retain the exact original version-one worker source,
`45e9b47c7c635fc30ebdb2cb4830d2d1fe382a5a7e4b663fb1a8e0112779e1a7`;
its JSON protocol,
`7d282b559952df68b95b5ebd55634b99d922ffc27b7a640778822ec3eed6ebe2`;
and its explanation,
`1dee7ebb7a98ccfec65cdb58f95378836a6747c1c9532ca676599cce62367332`.
Preserve the separately frozen version-two nested worker source,
`7dd5b4a5cdfecbe6dd674632bb5cee456ee877291de88ffc76ba60472d81408a`;
its protocol,
`f740da205f8431898f0a1089df5419f01612c2384def78c7d9831748ecca1b24`;
and explanation,
`c7a501f4487dfbe547c2cf8f5844be5179da035e7ae5f5e89f803234f3bf32dc`.

Derive every interpreter bootstrap from the source-authenticated, original
version-one `interpreter_bootstrap_source`. Supply the real, separately
authenticated **positive file size of each original guard source**, **each
candidate-owned source**, and **each actual native engine and bridge** to the
unchanged original guard. Reject boolean sizes, zero, negatives, mismatched
sizes, and either a native size or a claimed maximum above the actual original
**128 MiB** guard limit. Do not edit, copy, redirect, monkeypatch, or bypass
the original matcher guard. Never call either older actual `internal_worker`:
both preserve the genuinely falsified **256 MiB** bootstrap.

Use the original reference archive, original source-ordered matrix, original
program and exact seven identity-field renames, original pipe observers,
original warning/identity/import guards, and original full worker validator.
Keep distinct simultaneous interpreters A and B, repeat A after B, run all
eight independently created temporary interpreters, rerun A after closing B,
then create and close an independent final C. Every real operating-system
pipe must reach EOF and close all descriptors. Restore every interpreter,
matcher guard, buffer lifetime, candidate module, and process-global locale.
Preserve complete failures, timeout streams, initialization errors, and
cleanup errors.

## Authenticate the exact independent native engine

The only native activator is the separately published
[`../../tools/activate_verified_native_candidate_v2.py`](../../tools/activate_verified_native_candidate_v2.py),
SHA-256
`e6e8a72feffcf670da9a3e4d2e8b642e933c1d81cfe5bf7d1636385f207d6218`.
Its frozen
[`VERIFIED-NATIVE-ACTIVATION-V2.md`](VERIFIED-NATIVE-ACTIVATION-V2.md)
is SHA-256
`a675b411873c01ae88ea50d4f95aab7231a29dde38a458a947437f07ed850529`.

Explicitly select the actual, separately built native version:

- C, version **2**: explicitly pinned independent adapter
  `b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096`;
  exact fresh extension **163,136 bytes**,
  `ed57383dad99ce311664d165635fa300f3894df6b4816b5f54801d0e68263697`.
- Rust, version **2**: explicitly pinned independent adapter
  `6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b`;
  exact engine **658,344 bytes**,
  `5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f`;
  exact separate bridge **148,536 bytes**,
  `9e13396f93872222f77577ac7658609f5e2d3e77c0655a27c83572f0a1a06b4c`.
- Zig, version **3**: explicitly pinned independent adapter
  `2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862`;
  exact engine **108,888 bytes**,
  `caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071`;
  exact separate bridge **133,656 bytes**,
  `c579cf52b767b84ecc3d0a60f837d526978ace4e7739fe4cf51c2d2c8cfd90d9`.

Reread the complete actual passing source-build archive and distinct receipt.
Require `report.status = PASS`, `receipt.status = PASS`, and
`receipt.build_status = PASS`. Invoke the source-authenticated activator's
`authenticate_preserved_v2_history()`; independently reread and validate all
**39** real previous native-build processes. Require that the actual returned
history exactly matches both separately authenticated activation documents;
never accept an unverified process-count summary. Reuse the genuine versioned
GNU-symbol, fresh-source, zero-dependency, and complete process validator.
Verify both genuine independently built source-phase
files, exact bytes, correct family, matching hashes, positive sizes, and two
distinct native file identities. Preserve all **39** historical native-build
processes, including the genuinely failed previous Zig reproducibility result.

Require the actual private, no-follow, owner-only **0700** activation root
and separately owner-only **0600** report, receipt, recovery journal,
per-role intention, and original native backup. Independently reopen each
real original backup under the owner-only recovery root. Verify its complete
bytes, exact size, unchanged hash, device, inode, mode, genuine rich original
durability flags, positive typed write count, and original native mode; reject
a deleted, symlink-substituted, wrong-inode, or invented backup. Authenticate
the exact typed
seven-field native and intention identity independently of the four richer
published durability flags:

```text
relative, path, sha256, size_bytes, device, inode, mode

exclusive_creation, same_inode_readback_verified,
file_fsync_completed, directory_fsync_completed
```

Require a genuine, strictly positive integer `write_calls`; separately verify
every atomic promotion and candidate-directory synchronization. A later
readback never invents a previous file or directory fsync. Reject cross-family
or cross-version source, roots, archive names, old Zig failure receipts,
omitted roles, changed inode, native-size disagreement, and old activation
schemas. Verify guards before importing any candidate. No engine may call
stdlib `re`, `_sre`, an outside regex package, another candidate, or a foreign
native engine.

## Distinct, failure-preserving version-three evidence

Actual recordings exclusively create their own archive and receipt. No
previous result is overwritten:

```text
owned-candidate-subinterpreters-v3-FAMILY-LABEL.json.gz
owned-candidate-subinterpreters-v3-FAMILY-LABEL-publication-receipt.json

owned-candidate-subinterpreters-v3-FAMILY-LABEL-failures.json.gz
owned-candidate-subinterpreters-v3-FAMILY-LABEL-failures-publication-receipt.json
```

Synchronize every exact archive and receipt and their genuine directory.
Retain complete worker stdout, stderr, return code, PID, timeout, all case
rows, pipe ledgers, and cleanup observations. Never mark an incomplete or
failed record as passing.

Safe synthetic source-only commands:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/run_owned_candidate_subinterpreters_v3.py --self-test

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/run_owned_candidate_subinterpreters_v3.py --self-test
```

A separately caller-pinned `--verify-frozen-context` rereads the immutable
published sources, independently reauthenticates all **39** original native
build processes, and verifies both distinct complete C and Rust campaigns,
their failure receipts, and both native restorations. It never imports or
executes a candidate, activates or changes a native file, starts an
interpreter, samples a clock, or opens the holdout.

At this source freeze, actual **version-three nested interpreter candidate
results are NOT MEASURED**. Performance and memory are **NOT MEASURED**. The
expanded final holdout is **NOT GENERATED and NOT OPENED**. No candidate is
qualified and no winner is selected by publication of this source.
