# Rust public API compatibility oracle

Matching the same text is not enough to replace Python `re`. A Rust replacement must also accept the same Python arguments, raise the same kinds of errors, preserve buffer and object lifetimes, and return compatible pattern and match objects. This independent test checks the actual public Python interface against the pinned CPython **3.14.6**.

The deterministic source is [rust_surface_probe.py](../../tools/rust_surface_probe.py), SHA-256 `84f65dc50c8d8cf2697c1d113d8782dbb1f7c89bb1caac4138bc4cdbfdc52b0f`. Each of its **1,198** checks runs the same operation against standard Python and the Rust candidate and records both complete results.

| Public behavior | Cases | Initial differences |
| --- | ---: | ---: |
| Bound methods, keywords, duplicate arguments, and explicit `None` | 480 | 28 |
| Custom indexes, overflows, scanners, and search windows | 350 | 0 |
| Match values, groups, copying, and read-only attributes | 164 | 12 |
| Replacement and split count arguments | 72 | 0 |
| String and byte subclass identity | 64 | 0 |
| Mutable, strided, multidimensional, and wide-element buffers | 32 | 0 |
| Pattern properties, weak references, copying, and pickling | 24 | 0 |
| User-provided hashing failures | 12 | 0 |
| Total | 1,198 | 40 |

The index and count checks include normal Python integers, objects implementing `__index__`, `bool`, negative values, overflow, invalid floats, noninteger `__index__` results, and intentionally raised exceptions. Buffer checks verify contiguous and noncontiguous memory, multidimensional views, element sizes, mutable buffer lifetime, and iterator and scanner ownership. Match checks cover named and optional captures, stable spans, cached registers, replacement expansion, exact subject and pattern identity, copying, and read-only fields.

The **28** initial bound-method differences demonstrate that explicitly passing `endpos=None` must raise `TypeError`; omitting `endpos` remains valid. Treating the two as equivalent silently changes Python's public contract. The **12** initial match differences are separately retained rather than hidden behind matching-result comparisons.

The [complete initial comparison](rust-v6-surface-baseline.json) retains every successful and unsuccessful case. Its SHA-256 is `a502c1c091bb61346194b5e71938c26c84f6815018a7e8e453aeb32edf357552`. The [independent Python self-check](rust-v6-surface-self.json) passes **1,198/1,198** with **zero** differences; SHA-256 `6396fe133955c931e862df3be0fbb4071dc6fbcae4477ad9cd374fa7369449dd`.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONPATH=. "$PY" tools/rust_surface_probe.py \
  --module re --output /tmp/rebar-rust-surface-self.json

PYTHONPATH=. "$PY" tools/rust_surface_probe.py \
  --module candidates.rust_candidate \
  --output /tmp/rebar-rust-surface-current.json
```

The candidate command fails if even one public behavior differs. The archived initial findings are not waived, approximated, or counted as passing.
