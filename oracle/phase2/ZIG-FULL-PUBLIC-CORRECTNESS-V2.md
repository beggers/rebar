# Correct the complete Zig wider-public recovery setup

The unchanged first-party Zig engine already passes all **31,237** original
Python checks across all **13** independently isolated groups. Its preserved
original-suite success has SHA-256
`b2762eaea6dd505aa34bd446996b0464b7a0e057e7fb7162355885e065e19bd0`.
The previous **1,156** observed Zig failures remain independently archived.

The separately frozen V1 wider-public campaign authenticates the unchanged
**10,434-case**, **111-operation**, **94-dataset** correctness oracle used for
Rust. Its immutable owners are:

    tools/run_owned_zig_full_public_correctness_v1.py
    SHA-256 5ac635da716a7472b5d5a5bd6865bc2ad519ae354f240e3e6c1a8673f2cab087

    oracle/phase2/ZIG-FULL-PUBLIC-CORRECTNESS-V1.md
    SHA-256 679d6472ac44dd602a5b8aee57fba12b54f46c6ab8b4b5c35a287fe2fa8e9fb6

    oracle/phase2/zig-full-public-correctness-v1.json
    SHA-256 4efc2b4effc284808e21911c13079890722a6afdefd5ba346c5816b5769ee80f

Its actual committed first attempt failed before any candidate import,
activation, matching, file replacement, or timing:

    oracle/phase2/evidence/zig-full-public-correctness-v1-v17-zig-public-v1-run-001-preactivation-failure.json
    SHA-256 50199c81810b376c0711fb300fdf7dc3b2d781a35404b8704fb21dbdd12644ee
    bytes   1544
    inode   526690

The exact authenticated exception is:

    CampaignError: reject an unsafe exact recovery target

The independently successful V18 original-suite recovery helper intentionally
requires every recovery directory to remain directly beneath `/tmp` and to
start with this exact, unchanged prefix:

    /tmp/rebar-phase2-repaired-zig-original-campaign-v18-

The wider-public V1 coordinator and candidate worker both incorrectly supplied
the incompatible `/tmp/rebar-zig-public-v1-recovery-` prefix. The inherited
safety check correctly rejected that target. The candidate's wider-public
correctness therefore remained **NOT MEASURED**; this failure is not a
matching result and must never be hidden or overwritten.

## One narrow, append-only correction

The V2 coordinator and separately isolated candidate worker both derive the
same fresh, session-specific recovery path:

    /tmp/rebar-phase2-repaired-zig-original-campaign-v18-zig-public-v2-
      + SESSION

The session must start with `v17-zig-public-v2-` and contain only lowercase
letters, digits, and hyphens. Traversal, other directories, hidden/final-test
names, and reused V1 sessions are rejected. The exact V18 recovery-directory
guard, three-role journal, exclusive lock, original source/native file
identities, restoration order, native provenance, and strict version-4
pre-import independence guard remain unchanged.

The previous V1 source, protocol, contract, and genuine preactivation failure
are independently authenticated in every V2 source gate. No V1 file is
modified. Eight synthetic source-only controls independently reject empty,
V1, traversal, uppercase, hidden, slashed, non-string, and null sessions.
No recovery directory is created during a source-only check.

## Exact unchanged wider-public oracle

All **10,434** cases remain frozen: **5,217** text and **5,217** bytes,
**94** datasets, and the same complete **111** Python operations. The published
seed remains `5928217332825411634`; the matrix SHA-256 remains
`0c88d1ec7066ede05466c1a91126086cd52256548eda13a31778ff284439d97d`.
The independently adapted first-party Zig harness remains
`dfb0eaa7cef2ff96562e663ac774d02463e445f3bb5a015bfda471c684350b49`.

One isolated unchanged CPython reference worker and one isolated,
strict-version-4-guarded Zig worker must each execute every case. All answers,
individual mismatches, errors, worker identities, and public operation counts
must be published. A successful evidence publication alone does not mean a
successful candidate: candidate PASS requires exactly **zero** mismatches.

## Freeze before any candidate execution

Run ordinary `--self-test` and `--verify-frozen-context` gates under pinned
CPython **3.14.6** with `-I -B -S`. Repeat both in a sterile
`env -i PATH=/usr/bin:/bin LC_ALL=C LANG=C TZ=UTC` environment. The permanent
source-only wall authenticates only explicitly pinned, public, phase-two
plaintext owners. No source gate imports or runs a candidate, opens private
roots/native artifacts/compressed archives/hidden or proposed final cases,
creates a recovery directory, starts a worker, records a clock, writes files,
or runs Git.

Only after the exact V2 source, protocol, and complete contract are committed
and pushed may the root coordinator authorize `--run`. The exact previously
correctness-tested V17 native Zig engine and bridge remain independently built
without external regular-expression libraries or other candidate engines.
All three temporarily activated candidate owners must be restored to their
exact original inode identities before publication.

V2 candidate wider-public correctness: **NOT MEASURED**. Live runtime
independence: **NOT ESTABLISHED**. Performance, memory, hidden-final-test
results, and undefined behavior: **NOT MEASURED**. Qualified candidates:
zero. No winner.
