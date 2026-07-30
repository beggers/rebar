# First-party Rust matching-workspace reuse

Status: **SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN.**

This is one independently measurable, from-scratch Rust-engine experiment.
It does not wrap Python's matcher, an existing regular-expression library,
or another candidate. The unchanged Rust crate contains exactly one package
and zero external dependencies. Existing compiler and required-character
experiments remain separate; this variant derives directly from the exact
original Rust source so its effect can be measured independently.

The original correctness denominator remains **31,237** checks in **13**
groups. The latest complete version-25 Rust run failed **1,352** checks:
**240** replacement differences and **1,112** changing-buffer differences.
It verified **15,877** checks in passing groups. Its durable publication
passed, but the candidate failed and remains unqualified.

The completed, separate public practice run matched Python on all **416**
public cases before timing or profiling. All **1,664** paired observations
are preserved: Python took **97,941,980 ns** and the current Rust candidate
took **164,386,504 ns** in clean timing. Those numbers do not measure this
unbuilt variant and do not open or represent the final comparison.

Its native allocation report attributes **984** allocation events totaling
**397,248 bytes** to the Rust matching interpreter. Of these, **408** events
and **120,768 bytes** are its per-attempt guard/repetition storage; another
**576** events and **276,480 bytes** are capture-history growth. This first
variant reuses the former and the large lookaround capture snapshots. It
does not yet reuse capture-history storage; that is a separate experiment.

The profiler file called `rust.cpu.txt` actually reports allocated and
leaked bytes. Its authenticated log says `itimer could not be set`, and no
clock-profile packets exist. **Function-level CPU time is NOT MEASURED.**
Instrumented profiler elapsed time is never substituted for the separately
collected clean paired timings.

The unchanged input source is:

```text
path    candidates/rust/src/lib.rs
SHA-256 c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d
bytes   177967
```

The derived source makes one exact architectural change: each top-level
matching call owns four reusable vectors for overflow guards, overflow
repeat states, and large lookaround capture-start/end snapshots. Failed
candidate positions reuse that storage; all guards are reset to
`usize::MAX`, and all repeat states are reset to `RepeatState::default()`
before every new attempt. Nested positive/negative assertions and
lookbehinds always use separate local workspaces, preserving rollback,
capture ownership, and recursive execution. Callback reentry cannot share
a caller's stack-local workspace. The existing eight-slot state arrays,
sixteen-capture snapshot arrays, and all five existing inline stacks remain
unchanged.

The target is exclusively:

```text
candidates/rust/variants/vm_workspace_reuse_v1/lib.rs
SHA-256 0bd199957ed96cbf67109d4621698a6be300cb5c88d0ae30d25402f51777ba36
bytes   178647
```

Verification authenticates the complete actual version-25 correctness
receipt, the zero-dependency Rust sources, the entire successful public
profiler summary, all paired rows, exact allocation function/caller
reports, and the genuine failed CPU-clock log. A deny-default descriptor
and audit wall prevents candidate imports, external matcher imports, native
libraries, candidate/compiler processes, clocks, network, private roots,
archives, hidden cases, ordinary file access, and workspace writes. The
**141,557,760**-case final proposal receives exactly one metadata-only
check; its contents remain **NOT FROZEN / NOT GENERATED / NOT OPENED**.

Independent old-versus-new synthetic state models cover overflow and inline
guard/repetition state, capture counts below/at/above the snapshot boundary,
sequential positive/negative assertions, nested assertions, capture
rollback, search retries, and callback reentry. Every original source test
and public API remains unchanged.

After replacing each uppercase digest with its independently frozen value,
the root coordinator runs the ordinary and clean-environment gates:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_vm_workspace_reuse_v1.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_vm_workspace_reuse_v1.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Only the root coordinator may create the variant after all three source
owners have been committed and pushed. Both explicit commit identities
must match the real pushed commit; root separately checks Git state:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_vm_workspace_reuse_v1.py \
  --apply --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256 \
  --frozen-commit PUSHED_COMMIT --pushed-commit PUSHED_COMMIT \
  --root-authorized --frozen-committed-pushed
```

The actual operation authenticates the owned parent directory, creates one
new private `0700` directory and exactly one `0600` source with
`O_CREAT | O_EXCL | O_NOFOLLOW`, and synchronizes the file and both
directories. It never modifies existing sources, compiles, runs a candidate,
or measures speed. Variant correctness, memory, undefined behavior, CPU,
and performance remain **NOT MEASURED**.
