# Rust public profile v1 source freeze

This is **fresh public practice only**. It is not a qualification, hidden
benchmark, holdout, final result, fixture replay, or winner selection. Its sole
execution source is `tools/rust_public_profile_v1.py`; its source and protocol
freeze is `oracle/phase3/rust-public-profile-v1.json`.

All regular-expression patterns, text subjects, byte carriers, callbacks,
replacements, and scanner lexicons are generated from new literals embedded in
the driver. No performance result, previous benchmark matrix, fixture, archive,
holdout, undisclosed case, or other candidate is loaded. The published seed is
`0x5255535450524f31`; the matrix has sixteen equally weighted datasets, eight
text and eight bytes, across the same 26 public operations. Its SHA-256 is
`b13ff74122041ea792774fd5ee2d1f6d38033e94a1a6703c6e48522e461552a7`.

The balanced cohorts deliberately include dense subjects with 2,048 identical
first bytes and an impossible mandatory literal suffix, mandatory-prefix
alternations, forty capturing groups that exceed the native inline capture
buffer, thirty-six captures within a lookahead guard, nested bounded repeats,
named Unicode/high-byte subjects, mutable/readonly byte carriers, scanner
callbacks, and anchored multiline subjects. These literals were derived from
static inspection of the independently owned Rust adapter, C bridge, and
engine sources, not from a fixture or previous evidence.

The strict source modes use the exact isolated, bytecode-disabled, pinned
CPython 3.14.6 executable:

```
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B /home/dev-user/src/rebar/tools/rust_public_profile_v1.py --verify-source
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B /home/dev-user/src/rebar/tools/rust_public_profile_v1.py --self-test
```

Both commands have exactly zero candidate imports, subprocesses, clock
samples, profiler invocations, workspace mutations, or writes. They read only
the exact no-symlink driver and its exact no-symlink public manifest. The
self-test regenerates and hashes every case, checks equal domain and operation
weights, verifies native-overflow and dense-prefix cohorts, and rejects hostile
absolute, relative, traversal, symlink-shaped, reserved, hidden, legacy, final,
holdout, archive, and nonapproved output paths without touching those paths.

An actual run is allowed only after the frozen source has been committed and
only when the owning/root agent explicitly chooses a fresh approved session:

```
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B /home/dev-user/src/rebar/tools/rust_public_profile_v1.py --run --output experiments/rust_public_profile_v1/public-run-001/summary.json
```

Before any timing, profiler execution, or output-directory creation, separate
CPython and Rust worker processes must produce byte-for-byte identical
normalized outcomes for **all 416 public cases**, including capture groups,
spans, subject carrier identities, callback sequences, scanner remainder
mutability, warnings, and exceptions. The candidate worker authenticates the
owned `candidates/rust_candidate.py` adapter and its genuine
`candidates._rust_bridge` extension loader and native builtins. A
candidate-attributed import guard rejects candidate-owned production attempts
to load `re`, `_sre`, `regex`, `re2`, PCRE, Oniguruma, or related reference
engines, while allowing imports genuinely initiated by harness-owned warning,
inspection, or standard-library plumbing.

After parity, fresh isolated pairs alternate original-first and Rust-first
execution order while checking the original outcome before, during, and after
each measured case. Native profiling then runs each engine separately through
the frozen installed `/usr/bin/gprofng` dispatcher:

```
gprofng collect app -a off -F off -j off -S off -p hi -H on -o <engine>.er <pinned-python> -I -B <frozen-source> --internal-worker ...
gprofng display text -functions <engine>.er
gprofng display text -callers-callees <engine>.er
gprofng display text -allocs <engine>.er
gprofng display text -heapstat <engine>.er
```

`-a off` explicitly disables profiler archiving, `-F off` prevents collection
from descendants, `-p hi` enables CPU sampling, and `-H on` enables native
allocation/heap tracing. Independent Python `tracemalloc`, allocated-block,
maximum-RSS, user-CPU, and system-CPU observations supplement native CPU,
heap, allocation, and native FFI caller/callee evidence. Rust reports must
contain an independently owned native bridge/engine symbol before publication.

Every collector stdout/stderr stream, full correctness vector, paired timing
row, CPU function report, FFI caller/callee report, allocation report, heap
report, and raw `.er` experiment remains inside the single explicitly approved
`experiments/rust_public_profile_v1/<session>/` directory. Components are
opened with `O_NOFOLLOW`; sessions and files are created exclusively and never
overwritten, deleted, cleaned up, or reused. Profilers run descriptor-anchored
inside that directory with relative fixed experiment names. This delegated
source freeze does not execute an engine, timing run, gprofng command, or
candidate; actual `--run` remains reserved for the owning/root agent.
