# Exact Python group-name errors

Python's regular-expression API exposes more than whether a pattern is accepted. Invalid named groups and references must reproduce the reference exception type, message, original pattern, character position, line, and column.

The independently seeded [group-name oracle](../../tools/rust_group_name_adversarial.py) freezes **420** definitions, references, and conditionals covering surrogates, zero-width joiners, non-printable characters, Unicode-16 unassigned characters, and text and bytes. Its reference is CPython **3.14.6**. Two Python-against-Python controls pass, with zero unstable or unexplained cases.

| Recorded implementation | Cases | Failures |
| --- | ---: | ---: |
| Original Rust implementation | 420 | 416 |
| First corrected name formatter | 420 | 12 |
| Final native Rust implementation | 420 | 0 |

All three results are preserved; the intermediate failures are not replaced or silently removed:

- [Original baseline and all 416 failures](rust-v6-group-name-adversarial-baseline.json.gz).
- [Intermediate formatter and all 12 failures](rust-v6-group-name-adversarial-intermediate.json.gz).
- [Corrected implementation and all 420 passing cases](rust-v6-group-name-adversarial-corrected.json.gz).

All three files use deterministic, timestamp-free compression and pin seed `5139257352621277517`. The final implementation does not import or delegate to a regex package.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONPATH=. "$PY" tools/rust_group_name_adversarial.py \
  --module re --output /tmp/rebar-group-name-self.json.gz
PYTHONPATH=. "$PY" tools/rust_group_name_adversarial.py \
  --module candidates.rust_candidate \
  --output /tmp/rebar-group-name-rust.json.gz
```

This oracle measures compatibility only. Runtime, memory use, rankings, and speed on the larger unseen benchmark are **NOT MEASURED**.
