# Current original compatibility and honest speed compared with Python

Freeze a simple, readable speed graph with Python fixed at **1.00×**.
Measured Rust **V33** passes all **31,237 original** and **10,434 wider**
checks and runs **1.2424347186648022×** as fast as Python across **416**
public workloads. The 95% interval is **1.189358106927207–1.301024782265517×**.
Rust is faster in **252** tasks, slower in **164**, and more than 20% slower
in **14**. Show every substantial slowdown and preserve all **1,664** pairs.

Rust, Zig, and C now each pass all **31,237 original checks**. Authenticate
the actual latest C PASS, SHA-256
`34f1b7ccd9fe06408cdc6094f86bf98f4776bc7716ad970264bfbbda0d1280f2`,
10,657 bytes, inode 525275. Preserve the earlier C results with **224** and
**606** differences and Zig’s earlier **1,156** differences. Zig and C
**speed is NOT MEASURED**.

A newer separately built Rust **V35** exists, publication SHA-256
`442fba9a323d527977b3b19b9cb733d81a63d93adf6f4e9f25510f01ae5b4a2e`.
Its correctness, speed, and undefined behavior are **NOT MEASURED**; exact
static/live independence is **NOT ESTABLISHED**. Never transfer the measured
V33 result to this newer, untested V35 build.

Preserve all V33 timings, confidence bounds, losses, memory, and V26/V27/V28
history. Whole-process memory is **44,032 KiB** for both; Python-traced peaks
are **111,026 bytes** Rust and **181,952 bytes** Python. Each older experiment
failed **1,145 wider checks**. The old V30 static audit covers neither V33 nor
V35; their exact static and live independence are **NOT ESTABLISHED**.

Preserve V106/V107 falsifications and V108 history. Preserve the complete
immutable V109 source freeze, whose C result became stale after the real C
PASS; never publish its stale C claim. Bind to the published V110 graph,
which correctly shows Rust, Zig, and C each passing all original checks.

Source-only gates read only digest-, size-, inode-, device-, mode-, and
link-count-authenticated public plaintext evidence and existing measured
practice data. Never inspect candidates, native binaries, private roots,
compressed archives, holdout proposals or cases, hidden seeds, clocks, or
new timings. Never start a worker, candidate, compiler, native loader,
profiler, network request, or Git action.

Run `--verify-frozen-context` and `--self-test` in normal and sterile
environments using pinned isolated no-site CPython 3.14.6. Reject invented
speedups, intervals, memory, hidden results, compatibility failures, erased
losses, delegated independence, candidate qualification, or winner claims.

Only root may use `--render-graph --root-authorized --frozen-committed-pushed
--frozen-commit COMMIT --pushed-commit COMMIT` after this freeze is committed
and pushed. Create only `docs/evidence/candidate-current-overview-v111.svg`,
its `.inputs.json`, and its `.json`. Never modify V109 or another predecessor.
Final speed: **NOT MEASURED**. Qualified candidates: **0**. Winner: **none**.

