# Three independently written engines pass every original Python check

Status: **SOURCE FROZEN; GRAPH NOT YET GENERATED.**

Build a clear compatibility graph for three independently implemented,
from-scratch regular-expression engines. Python 3.14.6 is the unchanged
reference. **Rust, Zig, and C each pass all 31,237 original Python checks**
across **13** separate real workers with **zero differences**.

This graph measures compatibility, not speed. Rust additionally passes all
**10,434** separate wider checks using the same exact engine, Python adapter,
and native bridge. Wider Zig and C correctness is **NOT MEASURED**. Keep the
original denominator at 31,237; never add wider checks to it.

Authenticate the actual latest C result, SHA-256
`34f1b7ccd9fe06408cdc6094f86bf98f4776bc7716ad970264bfbbda0d1280f2`,
10,657 bytes, immutable inode 525275. Bind it to the exact independently
repeated C V24 build publication
`ed0c119b2e672342f3665c9dc7c4896977ea590bceec08ff3b97cd56b9f92a75`
and root-provenance publication
`36cb6adcf3a28d635fc997c090e62e1ce5563754deab02c05b41f4d034ad3048`.
Both independently built native C engines have SHA-256
`891acc0d0f496045e90e2efc0f0a3125e4f508352c2ee5e31ee807ea2fb1801a`.

Preserve the earlier C results with **224** and **606** differences and the
earlier Zig result with **1,156** differences. Preserve every existing V104
and V108 graph and all immutable V107 and V108 source-freeze owners.

The earlier first-party Rust static inspection applies only to an **older
V30 build**. Its engine, bridge, and adapter differ from the V33 build that
passes both current correctness suites. Current V33 static independence and
all live independence remain **NOT ESTABLISHED**; never transfer old findings
to a different build or claim a fully qualified candidate.

Read only explicitly authenticated public plaintext source, graph, and
evidence owners. Authenticate exact content digest, size, device, inode,
owner, permissions, and link count. Never read or inspect candidate sources,
native binaries, private roots, compressed archives, benchmark data,
proposed or actual holdout cases, secret seeds, or clocks. Never start a
candidate, reference worker, compiler, native loader, profiler, or network.

Run `--verify-frozen-context` and `--self-test` normally and under
`env -i PATH=/usr/bin:/bin LC_ALL=C`, always using pinned CPython 3.14.6
with `-I -B -S`. Reject changed results, omitted workers, mixed denominators,
invented wider Zig/C passes, erased earlier differences, false static or live
independence, hidden measurements, candidate qualification, and winner claims.

Only root, after committing and pushing this complete source freeze, may run
`--render-graph --root-authorized --frozen-committed-pushed
--frozen-commit COMMIT --pushed-commit COMMIT`. It creates only
`docs/evidence/candidate-current-overview-v110.svg`, its
`.inputs.json`, and its `.json`, each by exclusive no-follow creation.

Hidden final speed: **NOT MEASURED**. Fully qualified candidates: **0**.
Runtime independence: **NOT ESTABLISHED**. Winner: **none**.
