# Clean first-party Rust source and native-link audit V5

Status: **SOURCE FROZEN; ROOT CANDIDATE AUDIT NOT RUN.**

This additive, Rust-only audit answers one narrow question: do the exact
independently rebuilt, corrected Rust candidate and both native outputs
contain any Python regular-expression delegation, external regex package,
borrowed candidate engine, foreign native matcher, hidden dynamic loader,
or surviving private inspect escape hatch?

It does not erase the existing V4 result. The authentic, committed global
V4 audit remains **FAIL with one finding** in the older canonical Rust
bridge. Its exact 20,985-byte public receipt is:

    oracle/phase2/evidence/runtime-non-delegation-v4-actual-source-audit-failure.json
    c3020fe067ad06c2bf7309a73b960884572addd9e984d01d2cf27d5cd9d61f19

V5 never changes that bridge or claims all six families now pass. It
instead checks the separately rebuilt clean Rust source, native artifacts,
and same-family Python binding. Source-only verification authenticates the
three immutable V4 source owners, its actual one-finding failure, all three
V30 source owners, and both exact successful V30 publication receipts.

The independently frozen V30 build actually ran two fresh, owner-only Rust
source phases and 28 successful offline compiler/inspection processes. Both
builds used exactly one first-party Cargo package and zero external crates.
The exact public receipts are:

    ...-publication-receipt.json
    c29361f0436f73ada037ba497a0eb008eeadac6ebb41c50019521c0212448abd

    ...-root-provenance-receipt.json
    26445b833ac0e846538a1f648059a1c8a224e4e2f1acd58f82e9458dcc142404

The V30 inputs to be checked are:

    optimized first-party Rust engine
    c627012d0ce8d1e2cc3c70301956a060eecc6656f82137b219e44ec905f235ee

    independently written first-party search
    4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7

    complete clean first-party C/Python bridge
    254a8cea354556789496ce9dbfe70b4fed73ed9ee8e3b7f1c107dfe8662d7f55

    corrected, direct-native-descriptor Python adapter
    d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e

Each private phase has nine authenticated source owners: the Rust manifest,
its one-package lock, the C/Python bridge, the engine, four first-party Rust
modules, and its Python adapter. The two phases have 18 distinct source
file identities and four independently created native artifact identities:

    optimized engine: 3c952a1a9eee234f646bdbd119978d8fb18c223ac71b63db1ed0eada9aed1237
    clean C bridge:   ee63273fe7fc79934004db26a5c8df5b94ec3d0083837aed4bee701a7ed52256

Both clean bridges and both optimized engines are byte-identical between
phases. V5 checks every private file through exact descriptor-relative,
no-symlink, bounded, owner-only identity reads and authenticates its device,
inode, mode, digest, byte count, and unchanged descriptor identity.

The private-source audit parses Python imports and indirect module/loader
access, C headers and Python C-API imports, Rust source including nested
comments/lifetimes/raw strings, Cargo dependencies, and every ELF dynamic
library, search path, exported/imported symbol, and same-family binding.
Only the exact first-party Rust engine and ordinary C runtime libraries are
allowed. The one permitted native Python import is ordinary first-party
metadata (copyreg); importing inspect, re, _sre, external regex engines,
dynamic loaders, and other candidate families is forbidden.

The private build root is never opened by the self-test or verify-source
modes. A source-only verification opens exactly 12 pinned public owners:
three V5 files, three V4 files, one V4 failure receipt, three V30 files, and
two V30 publication/provenance receipts. It reads zero candidate sources or
native binaries and opens zero private build directories.

Run all four source-only gates using the pinned interpreter normally and
with a sterile environment:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B -S tools/audit_clean_rust_runtime_non_delegation_v5.py --self-test

    env -i PATH=/usr/bin:/bin LC_ALL=C \
      /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B -S tools/audit_clean_rust_runtime_non_delegation_v5.py --self-test

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B -S tools/audit_clean_rust_runtime_non_delegation_v5.py --verify-source \
      --source-sha256 V5_SOURCE_SHA256 \
      --protocol-sha256 V5_PROTOCOL_SHA256 \
      --contract-sha256 V5_CONTRACT_SHA256

    env -i PATH=/usr/bin:/bin LC_ALL=C \
      /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B -S tools/audit_clean_rust_runtime_non_delegation_v5.py --verify-source \
      --source-sha256 V5_SOURCE_SHA256 \
      --protocol-sha256 V5_PROTOCOL_SHA256 \
      --contract-sha256 V5_CONTRACT_SHA256

Only root may invoke the actual candidate/static ELF audit after the entire
V5 source triple has been independently verified, committed, and pushed:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B -S tools/audit_clean_rust_runtime_non_delegation_v5.py \
      --audit --root-authorized --pushed-source-sha256 EXACT_PUSHED_V5_SOURCE_SHA256

A successful root audit means the exact rebuilt Rust candidate has passed
static first-party source and native-link inspection. It is not a runtime
execution proof, does not qualify this or any other candidate, does not run
correctness cases or benchmarks, and does not remove the historical global
V4 finding.

Runtime non-delegation: **NOT ESTABLISHED**.
Candidate execution: **NOT RUN BY THIS AUDIT**.
Audited candidate families: **1 (Rust only)**.
Other candidate families: **NOT AUDITED BY V5**.
Final cases generated: **0**.
Candidate qualification: **NOT ESTABLISHED**.
Performance: **NOT MEASURED**.
Winner: **NOT SELECTED**.
