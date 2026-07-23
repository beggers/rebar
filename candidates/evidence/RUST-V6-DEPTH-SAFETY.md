# Rust recursion, stack, and allocation safety oracle

A regular-expression parser must report invalid or excessively nested patterns without crashing the Python process. The first Rust candidate instead reached fatal native stack overflows and unchecked numeric conversions on inputs that CPython handles safely. This experiment freezes those failures in independently bounded subprocesses.

The reference is the pinned CPython **3.14.6**. The runner is [rust_depth_probe.py](../../tools/rust_depth_probe.py), SHA-256 `487bfc111b68c2a0e9d7f8e163544044090ad495803e2bf1cc33d31ddfedceed`. Its **348** deterministic cases use seed `2026072323`.

| Input category | Cases | Initial Rust differences |
| --- | ---: | ---: |
| Python's changing recursion limit | 112 | 70 |
| Deeply nested parser expressions | 105 | 63 |
| Seeded combinations of nested expressions | 32 | 10 |
| Huge and overflowing repetition counts | 24 | 0 |
| Oversized numeric conditional references | 20 | 8 |
| Large literals, alternatives, and capture allocations | 20 | 0 |
| Nested matching operations | 16 | 0 |
| Bounded adversarial backtracking | 15 | 0 |
| Deeply nested malformed expressions | 4 | 3 |
| Total | 348 | 154 |

Of those **154** differences, **31** terminate the original Python subprocess with a native signal. There are **zero** unexplained reference failures and **zero** timeouts. Every crash is retained with its exact signal, generated input, Python result, and Rust diagnostic.

Seven nested expression shapes are checked through depth **32,768**, including ordinary groups, lookaheads, negative lookaheads, lookbehinds, atomic groups, nullable repetitions, and noncapturing groups. Both **8,192**- and **16,384**-deep groups and lookaheads expose the initial stack overflow. Fourteen even and odd Python recursion limits exercise positions on both sides of the real CPython boundary; a fixed hard-coded maximum is insufficient.

Numeric cases include exact 32- and 64-bit boundaries, overflow, **64-, 80-, and 100-digit** references, all-zero and leading-zero conditionals, and both defined and undefined capture groups. Large inputs include **262,144-character** literals, **8,192** alternatives, and **2,048** captures.

Each reference and Rust operation runs in a separate subprocess with core dumps disabled, a **768 MiB** address-space limit, a **six-second** CPU limit, and a **five-second** parent-controlled timeout. Crucially, large patterns are reconstructed from a small deterministic descriptor delivered over standard input. They never become command-line arguments, so operating-system argument-length errors cannot mask a regex failure.

The [complete starting result](rust-v6-depth-baseline.json) has SHA-256 `65a5a1eff08de95beaf60995ab9e29525fc63c70651acadeb56276c195295b67`. The [Python self-check](rust-v6-depth-self.json) passes **348/348**, with **zero** crashes, **zero** timeouts, and **zero** unexplained reference failures; SHA-256 `f446a712f36ef9efd3e9aed9f7d3af1a6044287db1db52bdeb5c647b3fc2d234`.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONPATH=. "$PY" tools/rust_depth_probe.py \
  --module re --output /tmp/rebar-rust-depth-self.json

PYTHONPATH=. "$PY" tools/rust_depth_probe.py \
  --module candidates.rust_candidate \
  --output /tmp/rebar-rust-depth-current.json

PYTHONPATH=. "$PY" tools/rust_depth_probe.py \
  --module candidates.rust_candidate \
  --category dynamic-recursion-limit \
  --output /tmp/rebar-rust-dynamic-recursion-current.json
```

The candidate passes only when every case matches Python and no process crashes, runs out of time, or produces an unverified reference result. The recorded baseline is a real failure, not a waiver.
