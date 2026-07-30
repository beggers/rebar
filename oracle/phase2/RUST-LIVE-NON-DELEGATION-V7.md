# Live first-party Rust non-delegation proof V7

Status: **SOURCE FROZEN; LIVE ROOT-AUTHORIZED CANDIDATE PROOF NOT RUN.**

The optimized, independently written Rust candidate has already passed
10,434 of 10,434 wider public compatibility examples with zero differences.
Its earlier V30 architecture passed the complete original 31,237-case
Python suite with zero differences. The actual V33 candidate has not yet
rerun that original suite, so its original-suite result remains
**NOT MEASURED**. V5 separately passed a strict static first-party source
and native-link audit without importing or running the candidate.

A static inspection is insufficient to establish runtime independence.
V7 therefore freezes a genuine two-process runtime experiment for the exact
fully corrected V33 Rust source, its own Python adapter, and its two owned
native shared objects. Both candidate processes are isolated pinned Python
3.14.6 interpreters; no standard-library regex oracle runs in either
candidate process.

The exact independently reproduced V33 first-party owners are:

    Python adapter: f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227
    Rust engine:    7412a997975aa42ec18249bc28d17e3c39223a4089bd23e3f7d2ab8112993b38
    Rust search:    4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7
    C/Python FFI:   f6253fbecc76b64750a22dc9393180d3ea6e3f2e29aace006c0479543e94342e
    native engine:  e692633896b61141734d4bb6ddce4a66b2c93bbeaa29b940fcf85904cf6a42e8
    native bridge:  ecb19eb814430aeb571f60dd50ba4de4b3f54e7f57f056d2436c41714a257000

The frozen V33 build publication and private-root provenance have SHA-256:

    cfe1464e1e8ce96bfa514b15cf96879a0642686987159dd79c15f4d9db408749
    7122c9bdff731be0f68602a4a216c1fa9700e6a78f9da9b534eeaef282c64c1c

V7 separately authenticates and preserves three actual independent results:

    original V30 PASS, all 31,237 original cases:
    84804409997794ce7e8bfff67ca8ffdcada9651a1660bda2654742befbba20f5

    public V33 PASS, all 10,434 wider public cases:
    8e2343809a8d9226973b1b70ca9d7348f750573caa2729123afb007f02a03bd9

    V5 source/native-link PASS, zero external regex packages:
    a6962420b66e4e450abeddaef552a7f3d81e922ceb5254e00574609eabfc8203

The two private Rust builds remain distinct source and native file
identities. Root first authenticates four exact private sources and two
native objects per phase using descriptor-relative, no-symlink, bounded
SHA-256, owner, device, inode, byte-count, and permission checks. Their
source and native bytes were independently produced in the actual 28-process,
zero-external-crate V33 offline build.

Each candidate worker starts with no re, _sre, inspect, tokenize, or
third-party regex module. It installs an irreversible CPython audit hook
and a guarded import function before reading candidate sources, loading
native libraries, importing the Rust adapter, or performing matching.

The live hook rejects:

- Python regular-expression and external regex package imports.
- Other candidate-family Python modules and native engines.
- Computed or unapproved Python imports.
- Foreign native dynamic loading and cross-family bridges.
- Unexpected file paths, write-capable opens, and foreign code execution.
- Subprocesses, external commands, networking, and replacement audit hooks.
- Final proposals, hidden/final cases, private benchmarks, and archives.

Exactly one first-party Rust adapter and its same-family C bridge may be
imported. Native C metadata may import the ordinary copyreg helper; an actual
Match serialization operation confirms that import is observed and contained.
The actual same-family Rust engine and bridge must both appear at their exact
authenticated phase paths in live /proc/self/maps. No external regex library
or another project candidate may appear there.

Every worker executes the same 22 fixed, correctness-gated operations:

- Compiled named Unicode search; module search, match, and fullmatch.
- Memoryview/bytes matching and scoped Unicode category behavior.
- Verbose named Unicode escapes and ignored inline comments.
- Named findall/finditer, splitting, and replacement callbacks.
- Named replacement templates and Match.expand.
- Native pattern scanners and the public lexical Scanner interface.
- Bytes named replacement, lookbehind, backreferences, and ignore-case.
- Cache reuse and cache invalidation.
- Native copyreg serialization import and rejected scanner serialization.

Answers are compared with fixed public literals, never with a standard
library regex engine inside the production worker. Each operation must finish
with zero forbidden imports, zero external/cross-family native libraries, zero
process/network attempts, and the exact independently authenticated native
objects still loaded.

The immutable V6 predecessor was genuinely committed, pushed, and run.
Its first authorized candidate process safely failed before any matching
because Python's ordinary frozen import machinery requested its built-in
module named _io. V6 correctly blocked that undeclared module:

    oracle/phase2/evidence/rust-live-non-delegation-v6-actual-runtime-failure.json
    9dcc4d6dbf81ed828189cacf8e981de788190bcf9912d01b8858e6841397286b
    LIVE_NON_DELEGATION_DENIED: forbidden direct or relative import '_io'

V6's immutable source, protocol, contract, failure receipt, and exact
failure remain separately authenticated and preserved. V7 permits only
ordinary, explicitly named CPython bootstrap machinery such as _io,
_codecs, _weakref, _thread, and built-in collection helpers. It continues
to forbid re, _sre, inspect, tokenize, external regular-expression
packages, unapproved dynamic loading, and every cross-family engine.
The durable V7 proof truthfully records exactly one authorized workspace
mutation: publication of its exclusive runtime evidence receipt.

## Source-only gates

Only these three files belong to this frozen experiment:

    tools/verify_owned_rust_live_non_delegation_v7.py
    oracle/phase2/RUST-LIVE-NON-DELEGATION-V7.md
    oracle/phase2/rust-live-non-delegation-v7.json

The two source-only modes cannot import or run a candidate, inspect a
private root or native library, launch a worker, read any protected final
content, sample a clock, access Git, connect to a network, or mutate the
workspace. Verification authenticates exactly 18 pinned public owners:
the three V7 owners, three V33 owners, three V5 owners, three immutable V6
owners, and six exact V33-build/original-PASS/public-PASS/static-PASS/V6
failure receipts.

Run both modes under the normal environment and again under sterile
environment settings:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B -S tools/verify_owned_rust_live_non_delegation_v7.py --self-test

    env -i PATH=/usr/bin:/bin LC_ALL=C \
      /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B -S tools/verify_owned_rust_live_non_delegation_v7.py --self-test

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B -S tools/verify_owned_rust_live_non_delegation_v7.py --verify-source \
      --source-sha256 V7_SOURCE_SHA256 \
      --protocol-sha256 V7_PROTOCOL_SHA256 \
      --contract-sha256 V7_CONTRACT_SHA256

    env -i PATH=/usr/bin:/bin LC_ALL=C \
      /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B -S tools/verify_owned_rust_live_non_delegation_v7.py --verify-source \
      --source-sha256 V7_SOURCE_SHA256 \
      --protocol-sha256 V7_PROTOCOL_SHA256 \
      --contract-sha256 V7_CONTRACT_SHA256

## Root-only live operation

Only root may actually execute the candidate, only after all four source
gates pass and all three V7 files have been committed and pushed:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B -S tools/verify_owned_rust_live_non_delegation_v7.py \
      --run --root-authorized --pushed-source-sha256 EXACT_PUSHED_V7_SOURCE_SHA256

Two genuine new candidate processes and 44 actual first-party matching,
replacement, Unicode, scanner, and metadata operations are required.
Successful root execution exclusively creates one durable runtime receipt:

    oracle/phase2/evidence/rust-live-non-delegation-v7-actual-runtime-proof.json

The receipt preserves both complete worker observations, all allowed import
events and exact native mappings, every operation, the 31,237-case V30 PASS,
the 10,434-case V33 PASS, the V5 static PASS, and exact build provenance.
It does not claim V33 passed the original suite without an actual rerun.
It does not qualify three families, create a final case, measure speed, or
choose a winner.

Exact-V33 original Python suite: **NOT MEASURED**.
Exact-V33 wider public suite: **10,434/10,434 PASS**.
Live runtime non-delegation: **NOT RUN UNTIL ROOT EXECUTES THIS FREEZE**.
Independent families audited by V7: **1, Rust only**.
Three-family phase gate: **NOT PASSED**.
Final cases generated: **0**.
Performance: **NOT MEASURED**.
Winner: **NOT SELECTED**.
