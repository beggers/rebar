# Corrected Rust public performance V4

Status: SOURCE FROZEN; PUBLIC TIMING NOT RUN; CANDIDATE NOT QUALIFIED.

Final holdout: INVALIDATED; REKEYED SUCCESSOR REQUIRED.

This first-party public-only performance campaign is authorized only after the
actual fully corrected V33 Rust candidate has passed every complete public
correctness case (10,434/10,434) and independently passed every original suite
case (31,237/31,237), using the identical exact V33 native engine, bridge, and
seven-repair adapter for both campaigns. An earlier, different V30 native build
also passed 31,237/31,237 and remains separately labeled as historical; its
result is never substituted for the exact V33 PASS. The separately frozen
zero-finding
source/ELF static non-delegation audit also remains explicitly historical and
static only. Four distinct evidence owners are independently authenticated:

- Exact V33 native-build original 31,237-case PASS:
  `5204823a291ec01890913218582ff978cbe923dd5c787c8d6ae68a9790c43064`.
- Historical V30 native-build original 31,237-case PASS (not V33):
  `84804409997794ce7e8bfff67ca8ffdcada9651a1660bda2654742befbba20f5`.
- Corrected V33 public 10,434-case PASS:
  `8e2343809a8d9226973b1b70ca9d7348f750573caa2729123afb007f02a03bd9`.
- Zero external-regex package/library/symbol static PASS:
  `a6962420b66e4e450abeddaef552a7f3d81e922ceb5254e00574609eabfc8203`.

Both immutable failed attempts preceding the exact V33 original success remain
independently preserved: the preworker entry failure
`c552d72cc3544c65a5811515853d966d402e9a654846082a4bfc7244caa9ea80`
and the unrecorded-worker failure
`5f72042155383ae3e8deeefc8e97cb418e0457088aed84518e9552511daa9ece`.

The exact successful V33 28-process, two-phase publication and root receipts
are separately caller-pinned. Their live private root is
`/tmp/rebar-phase2-native-build-v9-rust-zy4tpbu8`, device 2049, inode
11677247. Both exact independently reproduced private native phases are
authenticated. The selected first-party native engine is
`e692633896b61141734d4bb6ddce4a66b2c93bbeaa29b940fcf85904cf6a42e8`
at 672,440 bytes; the native bridge is
`ecb19eb814430aeb571f60dd50ba4de4b3f54e7f57f056d2436c41714a257000`
at 148,728 bytes. The exclusive seven-repair private adapter is
`f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227`
at 34,039 bytes.

## Exact same public workload and fairness contract

The identical previously frozen public matrix contains 416 cases: 16 public
datasets and 26 first-party complete Python `re` operations. Its published
matrix SHA-256 is
`b13ff74122041ea792774fd5ee2d1f6d38033e94a1a6703c6e48522e461552a7`,
and the published seed is 5932739705720426289. The immutable first-party V1
public worker harness is used unchanged for both stdlib and Rust.

Two independent untimed worker processes first compare every complete public
outcome. Any mismatch terminates before timing, memory profiling, or persistent
public output. Four independent paired rounds then execute every one of the
416 cases once on each engine: exactly 1,664 paired rows, with two stdlib-first
rounds and two Rust-first rounds. Both engines use the exact same isolated
CPython 3.14.6 executable, environment, case order, process policy, warmup
count (1), batch iterations (3), and five correctness checks per case per
engine. No candidate-specific benchmark-detection switch, workload shortcut,
native-only timing, hidden-case access, or reference substitution is permitted.

The point estimate is the equally weighted geometric mean across all 416 case
ratios, each ratio using all four paired elapsed-time observations. A
deterministic 400-resample published-seed percentile bootstrap reports a
two-sided 95% confidence interval. Every faster, slower, equal, and greater-
than-20-percent regression case is preserved. Complete ranked case, operation,
and cohort tables are published so downstream visualizations can show honest
relative speedups. Two identically configured, correctness-gated memory
workers independently report maximum RSS, peak traced allocations, and allocation
block changes across 416 cases times three profile passes.

All independently observed V26/V27/V28 results remain immutable and separately
authenticated:

- V26: 1.2520878685068846×, 247 faster cases, 11 regressions.
- V27: 0.7967512788167544×, 138 faster cases, 143 regressions.
- V28: 1.2298384265743338×, 208 faster cases, 8 regressions.

## Irreversible SOURCE-ONLY WALL

The source-only audit wall is installed before the first owner read. Only exact
descriptor-pinned public first-party source and historical evidence owners can
be opened. Candidate files, native objects, private roots, archives, final
proposals, final-proposal metadata, hidden cases, candidate imports, subprocess
creation, networking, clocks, entropy, directory enumeration, dynamic code, and
workspace mutation are denied. Source gates execute no candidate, sample no
timer, create no process, and perform no proposal reads or metadata probes.

Use the pinned isolated CPython with `-I -B -S` and independently pin the
source/protocol when rendering; the rendered canonical contract is the exact
third immutable freeze owner. Every self-test or verification invocation
requires all three explicit pins; bare `--self-test` is rejected deliberately:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S \
      tools/run_owned_corrected_rust_public_performance_v4.py \
      --self-test \
      --source-sha256 SOURCE_SHA256 \
      --protocol-sha256 PROTOCOL_SHA256 \
      --contract-sha256 CONTRACT_SHA256

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S \
      tools/run_owned_corrected_rust_public_performance_v4.py \
      --verify-frozen-context \
      --source-sha256 SOURCE_SHA256 \
      --protocol-sha256 PROTOCOL_SHA256 \
      --contract-sha256 CONTRACT_SHA256

Run both commands in the normal environment and again in a sterile environment
(`env -i PATH=/usr/bin:/bin`), yielding exactly four independent source gates.

Actual timing is root-only and starts only after all three freeze owners are
committed and pushed together. The exact frozen and pushed commit IDs must
match, every independent V26/V27/V28/V33 receipt must be caller-pinned, and the
actual operation uses only a fresh private native overlay and exclusive public
artifact paths. No canonical candidate or installed native owner is modified.

Measured speed does not establish winner status. Runtime non-delegation remains
NOT ESTABLISHED; the static audit is explicitly static only. Rust remains
unqualified and no winner may be selected until at least three independently
qualified candidate families exist. No final proposal or holdout is opened,
probed, generated, scored, or promoted.
