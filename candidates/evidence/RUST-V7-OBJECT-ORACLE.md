# Independent Python `re` object-compatibility oracle

Python 3.14.6 is the reference. This separate, seeded correctness suite asks
whether each from-scratch engine returns objects that actually behave like
Python's `re` objects, not merely whether the matched text looks the same.

The frozen denominator is **14,783 checks per engine**. The pinned standard
library is independently run twice and agrees on **14,783 out of 14,783** cases.
Seed: `0x52454241525f4f42`.

| Engine | Checks | Matches Python | Differences |
| --- | ---: | ---: | ---: |
| Python `re` against itself | 14,783 | 14,783 | 0 |
| From-scratch Python tree | 14,783 | 3,749 | 11,034 |
| From-scratch Python/native VM | 14,783 | 4,076 | 10,707 |
| From-scratch Rust | 14,783 | 14,276 | 507 |
| From-scratch Zig | 14,783 | 14,242 | 541 |

These are correctness results, not speed measurements. None of the four
original engines passes this stricter complete object contract. Their earlier
matching or performance results must not be presented as proof of universal
drop-in compatibility.

| Object-behavior family | Checks | Tree differences | VM differences | Rust differences | Zig differences |
| --- | ---: | ---: | ---: | ---: | ---: |
| Compiled pattern, copying, cache, and named groups | 390 | 234 | 219 | 28 | 28 |
| Independent seeded byte, scanner, and buffer cases | 1,120 | 669 | 659 | 0 | 0 |
| Public function and method signatures | 43 | 29 | 33 | 15 | 15 |
| Match copying, garbage collection, and read-only fields | 34 | 18 | 12 | 8 | 10 |
| Group-index conversion, errors, and side effects | 150 | 10 | 20 | 0 | 20 |
| Changes to mutable byte buffers and scanners | 18 | 18 | 18 | 0 | 0 |
| Observable pattern-hash calls and errors | 24 | 12 | 12 | 12 | 12 |
| Warning text and warning call sites | 22 | 2 | 2 | 0 | 0 |
| Exact bytes objects and captured-object identity | 10,200 | 7,964 | 7,786 | 444 | 444 |
| Exact text objects and captured-object identity | 2,590 | 1,926 | 1,926 | 0 | 0 |
| Search boundaries, integer conversion, and exact errors | 192 | 152 | 20 | 0 | 12 |
| **Total** | **14,783** | **11,034** | **10,707** | **507** | **541** |

For example, Python preserves the original complete bytes object:

```python
import re

subject = b"aa"
pattern = re.compile(rb"a*")

assert pattern.search(subject).group(0) is subject
assert pattern.search(subject)[0] is subject
assert pattern.findall(subject)[0] is subject
```

Both native baselines return equal bytes with a different identity. A
single-byte input can conceal this because Python reuses some single-byte
objects; the suite checks empty inputs and lengths around 64, 128, and other
boundaries instead. Python also returns a fresh empty `dict` for unnamed
`groupindex`, a fresh read-only view for named groups, and exact documented
errors, signatures, hashing side effects, and garbage-collection behavior.

Runtime object addresses are replaced by `0x<address>` before comparison. The
initial private investigation reported one extra apparent difference because
two otherwise identical error messages contained different addresses; the
frozen results above exclude that false positive. Lone Unicode surrogates are
preserved as their exact `surrogatepass` UTF-8 hexadecimal representation so
all five archives remain readable by ordinary JSON tools.

The oracle is [`tools/rust_v7_object_oracle.py`](../../tools/rust_v7_object_oracle.py),
SHA-256 `5638474b89a0cc6ac3fa0a6133e65247b10e0c6a6638628c7bbd96b30db1b7a9`.
Each deterministic archive contains all 14,783 actual observations, every
failure with the Python reference and actual result, every family and
denominator, the exact seed, and hashes of the pinned Python executable,
standard-library oracle, candidate source, and loaded native code:

| Archived engine | Evidence | Archive SHA-256 |
| --- | --- | --- |
| Python self-reference | `rust-v7-object-stdlib.json.gz` | `8cb95b04477e94a391bfa459d5c56141bed6e54af921a33608ca23ba7c7b2748` |
| Python tree | `rust-v7-object-ast.json.gz` | `59df298525c715a303798633f6e5c01d8f4643379e62b97fb1f359a90910d83d` |
| Python/native VM | `rust-v7-object-vm.json.gz` | `21a698e845d7493d99bd08cce9702f535499b70a636bc29923c7f4e6e89067f0` |
| Rust | `rust-v7-object-rust.json.gz` | `43156c5b935822d80daaaf242daad4332dc8e4f58d14e4fa2c8d69d8313bc7ee` |
| Zig | `rust-v7-object-zig.json.gz` | `8467698968f8bffafb3beb2b30759c820d691f880591591bf90139781b0d3e58` |

Verify the frozen sources, binaries, complete records, denominators, failure
counts, and archives without modifying them:

```sh
PYTHONPATH=. /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  tools/rust_v7_object_oracle.py --check
```

To independently regenerate the five archives, supply a separate existing
output directory with `--output-dir`; do not replace the committed baselines.
No benchmark, holdout, third-party regex library, or candidate-to-candidate
delegation is used by this correctness oracle.
