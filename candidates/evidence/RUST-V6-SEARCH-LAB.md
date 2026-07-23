# Rust search architecture experiment

This experiment measures from-scratch ways to find promising match positions. It is a focused microbenchmark, not the frozen Python end-to-end holdout. A result here does not claim that the complete Rust candidate is faster than Python `re`.

The experiment tests five literal-search strategies and four fully general byte-class strategies. It uses no external Rust packages or regular-expression engines. Standard system `memchr` and `memmem` are byte-search primitives, not regex implementations. The vectorized implementations explicitly check whether the processor supports AVX2 or SSSE3 and retain a portable fallback.

## Correctness

The deterministic seed is `0x52454241525f5336`. Before timing, the experiment checks **30,720** literal-search results and **526,336** class-search results against the simple scalar implementations. This includes empty needles, random byte strings, lengths on either side of the 16-byte and 32-byte vector boundaries, successful and unsuccessful searches, all 256 individual byte values, and 512 arbitrary full-range byte classes.

All **557,056** checks pass. The experiment then checks the expected answer again for all 665 measured rows. The captured run reports that both AVX2 and SSSE3 are available.

## Literal search

Seven input sizes from 64 bytes to 256 KiB, four needle sizes, and three distributions are tested. Each number below is the geometric mean relative to the ordinary scalar sliding-window implementation. These are component-level measurements on the AMD EPYC host, not speedups over CPython.

| Strategy | Distinct first byte, miss | Distinct first byte, late hit | Common first byte, miss |
| --- | ---: | ---: | ---: |
| Scalar sliding windows | 1.00× | 1.00× | 1.00× |
| Scalar first-byte check | 5.74× | 5.93× | 0.94× |
| System `memchr` plus verification | 196.48× | 175.72× | 0.50× |
| System `memmem` | 41.29× | 38.66× | 13.53× |
| Runtime-selected AVX2 first-and-last filter | 55.89× | 55.31× | 50.02× |

The important counterexample is retained: repeated calls to `memchr` are approximately twice as slow as scalar search when the first needle byte is common but the complete needle is absent. The vectorized first-and-last filter eliminates those false starts. A complete engine should therefore select an algorithm using a general property of the pattern and subject, not unconditionally assume that one byte is rare.

## General byte-class search

The vectorized byte-class algorithm handles any subset of all 256 possible bytes, including high-bit byte values. It splits a byte into its high and low nibbles and uses two 16-entry shuffle tables, so it does not approximate a class by a smaller ASCII range.

Five classes are tested: digits, word characters, a newline, punctuation, and sparse values including `0x80`, `0xfe`, and `0xff`. The table reports the geometric mean over all five classes, misses and late hits.

| Input size | SSSE3 versus scalar table | AVX2 versus scalar table |
| --- | ---: | ---: |
| 64 bytes | 3.64× | 5.90× |
| 256 bytes | 4.51× | 10.29× |
| 1,024 bytes | 4.42× | 11.32× |
| 4,096 bytes | 4.25× | 11.36× |
| 16,384 bytes | 4.32× | 11.13× |
| 65,536 bytes | 4.39× | 11.35× |
| 262,144 bytes | 4.46× | 11.46× |

These measurements support testing a vectorized candidate-position filter in the production Rust engine. They do not establish its end-to-end benefit: dense matches, short strings, Python-boundary costs, captures, Unicode semantics, and the frozen holdout must all be tested after integration.

## Reproduce

```sh
rustc --edition=2024 -C opt-level=3 -C lto=fat \
  -C codegen-units=1 -C panic=abort -D warnings \
  tools/rust_search_lab.rs -o /tmp/rebar-rust-search-lab
taskset -c 15 /tmp/rebar-rust-search-lab
```

The original uncompressed output contains 666 JSON lines: one correctness record, 385 literal-timing records, and 280 class-timing records. Its SHA-256 is `62f65b1c82223fe1755697a1ce8e8426e04fc6064650552595b3bf6fe24edcb4`. The complete rows are retained as [rust-v6-search-lab.jsonl.gz](rust-v6-search-lab.jsonl.gz), compressed with deterministic `gzip -n`; the compressed SHA-256 is `dfed5e200fa644dce3e5cd2cbd35695fd370a2d6f5bcafac92dda5de40ad7259`. The Rust source SHA-256 is `45726e1ba3e4864ef64b441eb63c67d68729a43be3bd2f02682453fe113c35c7`.

The timing procedure takes the median of five trials and scales repetitions to approximately 2 MiB of scanned input per trial, with at least eight and at most 20,000 operations. The benchmark uses `black_box` to prevent compile-time elimination. Timing numbers naturally vary with host load; the correctness checks, distributions, row counts, and seed are deterministic.
