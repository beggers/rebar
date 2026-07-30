# Preserve the actual nested Zig wider-public failure

The independently written Zig replacement passes all **31,237** original
Python checks across **13** independent groups. Its wider public suite is the
same unchanged **10,434-case**, **111-operation**, **94-dataset** oracle used
for Rust, with **5,217** text and **5,217** bytes cases. The published seed
remains `5928217332825411634`; the exact matrix SHA-256 remains
`0c88d1ec7066ede05466c1a91126086cd52256548eda13a31778ff284439d97d`.

## Preserve both genuinely failed wider-public attempts

The immutable V1 freeze and genuine preactivation failure remain preserved:

    tools/run_owned_zig_full_public_correctness_v1.py
    SHA-256 5ac635da716a7472b5d5a5bd6865bc2ad519ae354f240e3e6c1a8673f2cab087

    oracle/phase2/ZIG-FULL-PUBLIC-CORRECTNESS-V1.md
    SHA-256 679d6472ac44dd602a5b8aee57fba12b54f46c6ab8b4b5c35a287fe2fa8e9fb6

    oracle/phase2/zig-full-public-correctness-v1.json
    SHA-256 4efc2b4effc284808e21911c13079890722a6afdefd5ba346c5816b5769ee80f

    oracle/phase2/evidence/zig-full-public-correctness-v1-v17-zig-public-v1-run-001-preactivation-failure.json
    SHA-256 50199c81810b376c0711fb300fdf7dc3b2d781a35404b8704fb21dbdd12644ee

V1 genuinely failed before candidate activation because its recovery-directory
prefix violated the unchanged V18 original-suite safety rule. The append-only
V2 successor corrected that directory prefix in both coordinator and worker.
The complete immutable V2 freeze and actual V2 failure also remain preserved:

    tools/run_owned_zig_full_public_correctness_v2.py
    SHA-256 4eb351a11383df97d5f6b5f1f242e988a685992bafbaa87ee89e67fa1dcb0f3c

    oracle/phase2/ZIG-FULL-PUBLIC-CORRECTNESS-V2.md
    SHA-256 047cf9ff200f7c0423419230aa63ce0c2f3479361f70dd85c354612192b07abd

    oracle/phase2/zig-full-public-correctness-v2.json
    SHA-256 48f59c6a10412cb250b1995e1a37033aa73fc99aa2689117b01b8a2d07f5453c

    oracle/phase2/evidence/zig-full-public-correctness-v2-v17-zig-public-v2-run-001-guard-failure.json
    SHA-256 4466d9be63f9c480ac24de1d42b13524c1a4f82dba4d543779014605dcd74aa3
    bytes   1533
    inode   526724

V2 replaced the authentic nested V18 worker result with a generic outer
exception. Its receipt therefore lacks the actual nested activation stage,
whether the candidate was imported, and how many matching cases ran. Existing
receipt claims that the failure occurred before matching, that zero matches
ran, or that guard identity failed are **NOT ESTABLISHED**: all three facts are
**NOT MEASURED** because the actual inner result was discarded. Separate
read-only inspection confirms every immutable version-4 guard identity check
and guard installation succeeds in the same public source context; that does
not identify the later failing operation.

The V2 receipt remains byte-for-byte unchanged as historical evidence. This V3
protocol corrects its interpretation append-only; it does not silently reuse
or repeat its unsupported statements.

## Preserve the complete authentic nested failure first

The unmodified, pinned V18 original-suite worker already returns a complete
bounded failure document, including its actual:

- activation stage;
- exact error type, message, authenticated bounded traceback and frames;
- observed version-4 guard-installation state;
- observed candidate-import state; and
- original suite/candidate identities and no-hidden-case evidence.

V3 validates and propagates that complete document without replacing it with
a generic assertion. A failed isolated candidate worker emits its exact
authenticated failure as structured JSON and exits unsuccessfully. The root
coordinator accepts that nonzero exit **only** when the complete JSON,
original V18 schema, failure status, strict version-4 identity, bounded
diagnostics, candidate family, and all nested facts independently validate.

The coordinator retains the entire nested document, restores all **three**
original candidate-owner inode identities, then exclusively creates a durable
root failure receipt containing the exact genuine activation stage, error,
traceback, guard observation, and candidate-import observation. The matching
case count remains **NOT MEASURED** unless genuine case evidence establishes
it. No failed observation is treated as a candidate pass.

A successful worker still requires all **10,434** authentic candidate records,
all **10,434** isolated Python reference records, the exact **111** frozen
operations, and preserved complete mismatches. Candidate PASS still requires
zero mismatches. No regular-expression package, external engine, fallback,
other candidate, benchmark shortcut, or weaker guard is introduced.

## Preserve independently enforced recovery and isolation

The coordinator and candidate worker retain one exact fresh recovery path:

    /tmp/rebar-phase2-repaired-zig-original-campaign-v18-zig-public-v3-
      + SESSION

The session must start with `v17-zig-public-v3-`. The immutable V18 recovery
prefix guard, strict version-4 pre-import runtime guard, exact first-party
engine/bridge provenance, independently recorded historical **1,156** Zig
mismatches, and **31,237-case** original-suite pass are unchanged.

Both earlier source/protocol/contract triples and both genuine failure receipts
are authenticated as exact public phase-two plaintext. No earlier source,
candidate, receipt, or history is edited.

Run ordinary pinned CPython **3.14.6** `-I -B -S` self-test and frozen-context
verification, then repeat both under sterile
`env -i PATH=/usr/bin:/bin LC_ALL=C LANG=C TZ=UTC`. Source-only tests exercise
the permanent deny-default filesystem wall, unsafe recovery sessions, and
forged or missing bounded nested failures without candidate imports, candidate
execution, private/native access, holdout reads, archive reads, clock
measurements, file writes, Git operations, or recovery-directory creation.

After the exact V3 source, protocol, and complete contract are committed and
pushed, only root may authorize the full run. The actual result may reveal a
genuine previously hidden worker failure or all **10,434** matching results;
neither outcome is presumed.

Wider-public Zig correctness: **NOT MEASURED**. Authentic V2 nested activation
stage, guard-installation result, candidate-import state, and matching count:
**NOT MEASURED**. Live runtime independence: **NOT ESTABLISHED**. Performance,
memory, hidden final-test results, and undefined behavior: **NOT MEASURED**.
Qualified candidates: zero. No winner.
