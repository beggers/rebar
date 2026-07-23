# Rust crash and resource-safety oracle

A drop-in replacement for Python `re` must not terminate its Python process when given a bad regular expression. Normal in-process compatibility tests cannot safely report such failures: a Rust panic can end Python before a result is recorded. This experiment runs every pattern and every engine in its own resource-limited subprocess.

The pinned reference is CPython **3.14.6**. The deterministic runner is [rust_safety_probe.py](../../tools/rust_safety_probe.py), SHA-256 `f5720cf85f1db2537587fd8936deae72b92a409eeeab56ea0c4a4e34f16004c7`. Its **254** cases exercise **10** independently recorded categories. Both the reference and candidate receive exactly the same input.

Every subprocess disables core dumps before importing the candidate. It has a **768 MiB** address-space limit, a **five-second** CPU limit, and a **four-second** parent-enforced wall-clock timeout. A signal, process error, timeout, invalid output, wrong result, or incorrect regular-expression error is recorded explicitly. Neither the initial run nor the reference run has any reference crash or timeout.

| Category | Inputs | Initial Rust differences | Initial Rust process crashes |
| --- | ---: | ---: | ---: |
| Reversed surrogate character ranges | 20 | 20 | 20 |
| Valid surrogate patterns and matching | 44 | 28 | 0 |
| Unicode group names | 12 | 12 | 0 |
| Seeded malformed expressions | 48 | 15 | 0 |
| Nested groups and lookarounds | 16 | 8 | 0 |
| Repetition and overflow boundaries | 24 | 2 | 0 |
| Search position and end boundaries | 35 | 4 | 0 |
| Malformed patterns and escapes | 27 | 0 | 0 |
| Byte strings and buffer layouts | 20 | 0 | 0 |
| Large capture and alternative counts | 8 | 0 | 0 |
| Total | 254 | 89 | 20 |

All **20** process crashes reproduce from five malformed reversed ranges under each of four flag combinations. Python raises `PatternError` and continues; the starting Rust parser instead panics while formatting a surrogate character and terminates Python with `SIGABRT`. The [complete baseline](rust-v6-safety-baseline.json) preserves every input, signal, diagnostic, reference result, and failure. Its SHA-256 is `c485379220ab7240a8105c557c5f210c1775e96ef611e15b2051a283692ffb16`.

The [complete self-check](rust-v6-safety-self.json) compares Python with Python in independent subprocesses. It passes **254/254** with **zero** crashes, **zero** timeouts, and **zero** unexplained reference failures. Its SHA-256 is `9da40ef674cf611555ff7087c403925b40382f0d44fb75d9565a154f384904a5`.

The remaining differences expose valid unpaired Unicode characters, Python's exact Unicode identifier rules, nested-pattern recursion behavior, possessive repetitions, explicit `None` end positions, and exact syntax-error locations. They are reported as compatibility failures; accepting a malformed pattern, rejecting a valid pattern, or producing a more permissive result is not counted as a pass.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONPATH=. "$PY" tools/rust_safety_probe.py \
  --module re --output /tmp/rebar-rust-safety-self.json

PYTHONPATH=. "$PY" tools/rust_safety_probe.py \
  --module candidates.rust_candidate \
  --output /tmp/rebar-rust-safety-current.json

PYTHONPATH=. "$PY" tools/rust_safety_probe.py \
  --module candidates.rust_candidate \
  --category surrogate-reversed-range \
  --output /tmp/rebar-rust-surrogate-safety-current.json
```

The candidate command exits unsuccessfully if any process crashes, times out, disagrees with Python, or produces an unexplained reference failure. The archived baseline is a finding, not a passing gate or a performance claim.
