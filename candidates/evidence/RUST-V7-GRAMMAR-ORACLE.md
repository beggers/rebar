# Independent Python regular-expression grammar check

This test asks whether each from-scratch implementation really understands the
same expressions as Python 3.14.6. It is separate from every performance test and
has never read the performance holdout.

One fixed seed produces **20,480 distinct cases**, divided evenly across 16
families. These include repeated positive and negative lookaheads and
lookbehinds; nested captures and conditionals; local and invalid flag changes;
verbose expressions and comments; byte patterns and named backreferences; atomic
groups; possessive repeats; empty alternatives; character classes; and malformed
escapes. The reference includes **14,818 valid expressions and all 5,662 invalid
expressions**. Invalid inputs must produce the same exception, message, pattern,
position, line, and column as Python.

Python produced exactly the same complete answer in two separate reference
processes: **20,480/20,480; zero unexplained failures**. The original candidates
were then compared with the same frozen expressions and reference answers,
before any grammar fix:

| From-scratch candidate | Cases | Differences from Python | Crashes | Timeouts |
| --- | ---: | ---: | ---: | ---: |
| Python implementation | 20,480 | 5,573 | 0 | 0 |
| Native C implementation | 20,480 | 5,587 | 0 | 0 |
| Rust implementation | 20,480 | 5,535 | 0 | 0 |
| Zig implementation | 20,480 | 279 | 0 | 0 |

These are initial correctness results, not speeds. None of these original
versions passes this broader grammar check. In particular, Python accepts
repeated lookarounds such as `(?=a){2}`, `(?=a)+`, and `(?<=a){2}`; the original
Python, native C, and Rust candidates incorrectly reject them. The original Zig
candidate handles those expressions but still differs on some verbose patterns,
lookbehind/backreferences, and exact parser errors. All failures are preserved;
none is waived.

The fixture SHA-256 is
`f2b0e9bfaa7dedacdf201e66499019f30860050b75dd722310f27bb1c79e35dd`.
Both complete Python reference passes have SHA-256
`740e4602f67fa1cfc1ba65d176453009470316a5653cceb19b3c62853a7faab7`.
The original Rust source is
`f529040ab9082eedf80ba9c39b407def3edf9520a9a1fc8d70cb6e8399f7723f`;
the full candidate source and native-binary hashes are in the compressed
manifest. The deterministic seed is
`6518143889424763005106639421778`.

`rust-v7-grammar-manifest.json.gz` identifies and verifies all ten deterministic
archives. These contain the entire frozen fixture, both complete reference
passes, the complete original result for each candidate, **every individual
failure**, exact error details, the source hashes, and concise reproductions.
Compression uses an empty filename and zero timestamp; no cases are sampled,
dropped, merged, or hidden.

Use the pinned Python to verify the frozen fixture and every compressed record:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  tools/rust_v7_grammar_oracle.py verify
```

Run a changed Rust candidate against every unchanged reference answer:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  tools/rust_v7_grammar_oracle.py gate \
  --module candidates.rust_candidate --require-pass
```

The gate compares compiled pattern metadata; warnings; exact parser errors;
search, match, and full-match results over four windows; all captures and named
groups; collected matches; splitting; and both replacement operations. Each
candidate runs in crash-isolated child processes. The complete denominator stays
20,480, including every negative case. A pass requires zero differences, crashes,
or timeouts; passing this grammar check makes no claim about performance.
