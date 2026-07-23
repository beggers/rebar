# Extended Rust compatibility oracle

The first Rust engine passed the frozen project suites but did not yet reproduce several less common, real behaviors of Python `re`. This experiment adds a deterministic, self-checked oracle before treating a faster Rust implementation as interchangeable with the Python standard library.

The reference is the pinned, unmodified CPython **3.14.6**. The test source is [rust_v6_paths_probe.py](../../tools/rust_v6_paths_probe.py), SHA-256 `40e773053c348420a34f9ab3594035d11faeabc7b48c74df96594e3dca690dd3`. With seed `2026072307` and 16 generated inputs, it makes **47,944** direct comparisons.

| Check | Python compared with itself | Initial Rust compared with Python |
| --- | ---: | ---: |
| All test cases | 47,944/47,944 correct | 7,471 differences |
| Invalid and out-of-range search windows | 1,260/1,260 correct | 50 differences |
| Unpaired Unicode surrogate patterns | 380/380 correct | 100 differences |
| Case-insensitive numbered, named, and scoped backreferences | 1,645/1,645 correct | 64 differences |

The remaining **7,257** differences comprise **7,243** deterministic manual cases and **14** seeded cases. The deterministic cases include all **50** CPython case-fix keys and **56** directed case-fix mappings, all **24** connected mapping groups, all **102** Unicode characters whose uppercase form has multiple characters, ordinary matching and compilation, capture groups, assertions, nullable repetitions, byte strings, buffers, scanners, replacement, public errors, and five search windows.

The backreference check tests all **235** ordered character pairs from **26** case-equivalence groups against **seven** numbered, named, scoped, and ASCII matching patterns. This matters because Python deliberately applies different case-equivalence rules to matching a literal and matching a backreference.

The invalid-window check is the complete product of **10** patterns, **three** subjects, **six** position windows, and **seven** matching and scanner operations. In particular, Python can successfully match an empty pattern or word boundary even when `match` is given an end position lower than its starting position; `search`, `fullmatch`, and collection have independently verified behavior.

The surrogate check covers **19** direct and escaped literals, classes, ranges, captures, backreferences, category controls, and an ordinary non-surrogate control, against **four** flag combinations and **five** operations. Python accepts unpaired surrogate characters in pattern strings; a Rust parser must not mistake them for end-of-input.

The [complete initial differences](rust-v6-extended-paths-finding.json.gz) are deterministically compressed with `gzip -n`. Compressed SHA-256: `57fadb40a25cf66d210e497fa3596eae854eaf20e631c4bcee8830d656488b4f`. Expanded SHA-256: `ec63751ecea62efa0308c8bf26ee89df33319ad84e6bc0d4dd1afbc2be0a27a2`. The [Python self-check](rust-v6-extended-paths-self.json) has SHA-256 `5a9314af33ec2f9be7532bb26159044cc27c832090cf0a2e06b0b196c8362ce8` and contains **zero** failures.

The first optimized Rust virtual-machine checkpoint produced an **exactly byte-identical** report to the unoptimized baseline, with the same expanded SHA-256. Its performance architecture therefore did not hide, remove, or add any of these existing correctness failures. The failures remain real and must be fixed before any performance result can qualify.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONPATH=. "$PY" tools/rust_v6_paths_probe.py \
  --module re --seeded-cases 16 \
  --output /tmp/rebar-rust-v6-paths-expanded-self.json

PYTHONPATH=. "$PY" tools/rust_v6_paths_probe.py \
  --module candidates.rust_candidate --seeded-cases 16 \
  --output /tmp/rebar-rust-v6-paths-expanded-result.json

gzip -dc candidates/evidence/rust-v6-extended-paths-finding.json.gz \
  | sha256sum
```

The Rust command exits unsuccessfully when even one mismatch remains. The saved initial mismatch report is evidence of a real compatibility finding, not a passing gate, private waiver, approximation, or performance result.
