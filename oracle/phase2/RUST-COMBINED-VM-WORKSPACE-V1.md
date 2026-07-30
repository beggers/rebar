# First-party Rust compiler, mandatory-anchor search, and VM-workspace composition

Status: **SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN.**

This independent source experiment composes the actual, separately frozen and
materialized Rust compiler/search V2 and VM-workspace V1 variants. Its matcher
remains the original first-party ordered Rust VM; the crate retains one package
and zero external dependencies. The independently authenticated, optional
changing-buffer C bridge is only a future build option. No candidate, native
library, compiler, worker, timing clock, archive, hidden case, or final comparison
is imported, opened, started, or executed by any source gate.

The two exact source-only predecessors are:

```text
combined compiler/search V2 lib.rs
SHA-256 c627012d0ce8d1e2cc3c70301956a060eecc6656f82137b219e44ec905f235ee
bytes   189423

independent VM-workspace V1 lib.rs
SHA-256 0bd199957ed96cbf67109d4621698a6be300cb5c88d0ae30d25402f51777ba36
bytes   178647
```

Both complete frozen source/protocol/contract triples and both genuine application
receipts are pinned before use. All seven exact, reversible VM substitutions
apply once to the compiler/search V2 source; applying the same substitutions to
the original source independently reproduces the already materialized workspace
V1 source. The complete composition is independently pinned:

```text
candidates/rust/variants/combined_vm_workspace_v1/lib.rs
SHA-256 9fcd158da1af49dabf916168472938d00d9dde527a4c877a5281d5829200b4ab
bytes   190103

candidates/rust/variants/combined_vm_workspace_v1/search.rs
SHA-256 4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7
bytes   24305
```

Borrowed parser input, lazy alternation allocation, scanner runtime flags,
conservative owned fixed-position byte anchors, AVX2/scalar fallback, ordered
alternative priority, captures, lookarounds, source lifetimes, and the public FFI
remain unchanged. Each top-level search owns one stack-local four-vector frame.
Failed candidate positions reuse overflow guards, overflow repetition states,
and large assertion begin/end snapshots. Every new attempt resets guards to
`usize::MAX` and repetitions to `RepeatState::default()`. Snapshots are cleared
before reuse. All nested lookarounds and callback reentry use independent local
frames. Inline guard/repetition, assertion-capture, and capture-undo capacities
remain eight, sixteen, and forty-eight respectively. Capture-history reuse and
converging the mandatory-anchor/start-set filters are **separate future
experiments; neither is implemented in this freeze**.

Both complete public profiles are authenticated. The first preserves all 416
identical public outcomes and 1,664 timing observations. The second preserves
all 416 gated outcomes, all 1,664 clean paired rows, and actual native allocation
evidence: 408 guard/repetition allocations totaling 120,768 bytes and 576
unchanged capture-history allocations totaling 276,480 bytes. The alleged
function-level CPU profile is still **NOT MEASURED**: its authenticated log says
`itimer could not be set`. Previous measurements describe previous engines,
never this unbuilt source experiment.

The original denominator remains **31,237** cases in **13** suites. The latest
complete, genuinely published Rust V25 result is **FAIL**, with **1,352**
differences: **1,112** changing-buffer and **240** substitution mismatches;
**15,877** checks passed in fully passing suites. This composition neither hides
nor claims to repair those known failures. Its independent source models rerun
all **18,144** workspace differential cases, then perform **110,592** new
combined ordered-anchor/window/high-byte/vector-boundary/ownership checks,
including **1,728** isolated nested-assertion and callback-reentry controls.

The former V2 final proposal is **INVALIDATED**. A **REKEYED SUCCESSOR IS
REQUIRED** before any later final protocol or comparison. Neither the retired
proposal nor any successor receives even a metadata inspection here: proposal
content opens, metadata probes, generated final cases, and opened final cases
are all exactly zero. The final protocol remains **NOT FROZEN** and final cases
remain **NOT GENERATED / NOT OPENED**.

An always-on, deny-default descriptor/audit wall is installed before every owner
read. It permits only exact pinned first-party sources and already-public
evidence. It blocks candidate imports, native libraries, foreign descriptors,
subprocesses, clocks, archives, hidden/final cases, holdout metadata, source
writes, descriptor aliases, unsafe directory modes, and complete Linux
`O_TMPFILE` masks. Ordinary safe read-only directory flags remain valid.

Ordinary and sterile environments each run both source-only gates with exact,
independently pinned freeze-owner digests:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_combined_vm_workspace_v1.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_combined_vm_workspace_v1.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Only the root coordinator may publish after the exact source/protocol/contract
freeze has been independently committed and pushed. The real full frozen and
pushed commit identities must match, and both explicit root-authority switches
must be present:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_combined_vm_workspace_v1.py \
  --apply --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256 \
  --frozen-commit PUSHED_COMMIT --pushed-commit PUSHED_COMMIT \
  --root-authorized --frozen-committed-pushed
```

Publication creates exactly one fresh `0700` variant directory and two fresh
`0600` files using descriptor-anchored `O_CREAT | O_EXCL | O_NOFOLLOW`. Both
sources, their private directory, and the pinned parent are synchronized. No
existing source is modified or silently overwritten. This freeze does not build,
execute, qualify, benchmark, or select a candidate. Correctness, performance,
memory, CPU, and undefined behavior remain **NOT MEASURED**.
