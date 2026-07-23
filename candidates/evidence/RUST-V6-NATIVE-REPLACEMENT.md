# Rust replacement experiment

**Outcome: rejected.** A new, from-scratch Rust/C replacement path made the selected practice workload almost three times faster than the previous Rust path, but the complete independent compatibility check exposed **2,132 failures in 11,266 checks**. The original frozen subset contained **496 failures in 8,264 checks**; the frozen callback and buffer extension contained **674 failures in 8,862 checks**. In particular, valid callbacks that reuse a mutable buffer can produce the wrong successful answer. This historical implementation is not compatible with Python's `re`, is not a winner, and must not be promoted.

This report is exclusively about **697 frozen practice cases**. The final unseen test, the complete performance ranking, and the project's success conditions remain **NOT MEASURED** by this experiment.

## Why the faster attempt was rejected

Python collects the objects returned by replacement callbacks and joins them after it has visited every match. The experimental Rust/C bridge instead immediately copied or checked each callback result. This changes observable behavior even when the callback does not raise an exception:

```python
import re

buffer = bytearray(b"0")


def replacement(match):
    buffer[0] += 1
    return buffer


re.compile(b"a").sub(replacement, b"a-a-a-a")
# CPython:     b"4-4-4-4"
# Experiment:  b"1-2-3-4"
```

The same problem occurs when the callback returns a memory view or a mutable array through Python's buffer protocol. Invalid callback results expose a second consequence: CPython first runs all callbacks and then reports the exact original object type at join time; the streaming attempt stopped early or reported the type of an already-converted copy. CPython also drops callback results of `None`, gives a later callback exception priority over an earlier invalid return, and counts any preceding text when reporting the failing joined-item index. These observable details require retaining the original returned objects until the final join.

The independently expanded differential preserves the complete historical failure breakdown; its original **8,264-case** subset, **8,862-case** default, and **11,266-case** deep result are never substituted for one another:

| Rejected behavior | Failing checks |
| --- | ---: |
| Original callback return is checked or copied too early | 288 |
| Original exact-validation error reports the converted object type | 60 |
| Original replacement is hashed or validated without a match | 148 |
| Additional shared mutable callback-return checks | 18 |
| Additional delayed joining and exception-order checks | 56 |
| Additional replacement-template timing checks | 104 |
| Deep repeated literal result incorrectly shares object identity | 46 |
| Deep escaped-template errors have incorrect metadata | 144 |
| Deep custom hashing, buffer types, and buffer side effects | 1,268 |
| **Full historical failures** | **2,132 / 11,266** |

For example, replacing `"a"` in `"zzz"` with an `array.array` must return the original `"zzz"` without hashing the unused array. The rejected attempt raised an unhashable-array exception. On a match, using a `bytearray` in a text substitution must report `bytearray found`, not `bytes found`.

There is an important exception to delayed validation. Pinned CPython 3.14.6 validates replacement content containing template backslashes **before** searching, including when the input cannot match and when `count=-1`. This rule applies to text, bytes, and bytes-like `bytearray`, `memoryview`, and `array.array` replacements. For example, `re.compile("a").sub(r"\g<missing>", "zzz", count=-1)` raises `IndexError`; using a byte array containing `b"\g<missing>"` raises the same error. Invalid group numbers and unknown escapes similarly raise the exact `PatternError` before matching. Plain buffers and unhashable text or bytes subclasses without template backslashes must instead remain unhashed and unvalidated until a match uses them. Noncontiguous buffer views must be materialized exactly when CPython does. A compatible fix must inspect actual replacement content, eagerly parse real templates, preserve the original plain-buffer type, and retain the original callback return objects until CPython-equivalent joining.

Empty matches, unmatched capture groups, raised callback exceptions, count conversion, bound method identity, keyword arguments, and signatures showed **zero observed mismatches** in the expanded test. These passing categories do not cancel the 2,132 historical failures.

An earlier **2,156-check** focused differential, the **144-test** CPython upstream run, all **12,432** frozen practice-and-holdout correctness answers, **918** independent public-boundary checks, and **520** hostile boundary checks passed before the expanded callback test. That earlier coverage was insufficient. The full, independently self-checked **11,266-case** historical result controls the experiment's rejected status.

## Practice-only performance, including every slowdown

Both runs use the same **697** case IDs from **24** frozen practice families: **319** `sub` cases, **338** `subn` cases, **24** neighboring `search` cases, and **16** neighboring `split` cases. Each case has three seeded paired trials against unmodified CPython 3.14.6, four frozen warmups, at most eight operations per timing, and 101 seeded confidence resamples. Each run preserves all **4,182** raw timing rows and **12,546** before-, during-, and after-timing correctness checks.

Values greater than `1×` are faster than Python; values less than `1×` are slower. The range is the seeded 95% confidence interval for the practice cases, not the final holdout interval.

| Practice measurement | Previous Rust | Rejected streaming attempt |
| --- | ---: | ---: |
| All 697 cases, relative to Python | 0.265× (0.264–0.266×) | 0.794× (0.790–0.796×) |
| `sub`, 319 cases | 0.238× (0.237–0.238×) | 0.661× (0.658–0.664×) |
| `subn`, 338 cases | 0.241× (0.239–0.243×) | 0.880× (0.873–0.886×) |
| Cases confidently faster than Python | 62 / 697 | 186 / 697 |
| Cases genuinely more than 20% slower than Python | 632 / 697 | 316 / 697 |
| Historical archive flags using its incorrect `0.8×` boundary | 631 / 697 | 268 / 697 |
| Median Python-traced peak memory, relative to Python | 3.152× | 0.173× |

The practice-only change was **2.995×** faster than the previous Rust implementation overall, **2.783×** faster on `sub`, and **3.650×** faster on `subn`. These are comparisons against previous Rust; the rejected attempt remained **slower than Python overall** at `0.794×`. Python-traced memory excludes untracked native allocations. Neither speed nor traced memory excuses incorrect replacement results.

A result is genuinely more than 20% slower when its running time exceeds `1.2 ×` Python's running time, or equivalently when the reported speed ratio is **less than `5/6`**, not `0.8`. The historical pilot incorrectly named its stricter `speedup < 0.8` flags `regression_gt_20pct`. Its immutable summary and raw rows have not been altered. The verifier recomputes the true threshold independently from all 697 individual measurements, exposes both counts, and checks every family against its original denominator.

Every selected family and every genuinely greater-than-20% slowdown is shown below. Single-case families are explicitly identified by their denominators; they are not presented as broad conclusions.

| Frozen practice family | Cases | Previous / Python | Attempt / Python | Attempt 95% interval | >20% slower |
| --- | ---: | ---: | ---: | ---: | ---: |
| `bytes-replace` | 1 | 0.179× | 1.126× | 1.117–1.133× | 0 / 1 |
| `deeper-module-warm-sub` | 64 | 0.219× | 0.653× | 0.643–0.663× | 63 / 64 |
| `deeper-shell-vars` | 64 | 0.138× | 0.827× | 0.817–0.836× | 37 / 64 |
| `deeper-source-comments` | 64 | 0.150× | 0.241× | 0.238–0.245× | 64 / 64 |
| `expanded-cold-module` | 48 | 1.526× | 1.600× | 1.581–1.621× | 0 / 48 |
| `expanded-comment-strip` | 48 | 0.255× | 0.535× | 0.526–0.542× | 37 / 48 |
| `expanded-newline-normalize` | 48 | 0.212× | 0.820× | 0.805–0.830× | 29 / 48 |
| `expanded-replace-callback` | 48 | 0.569× | 0.998× | 0.987–1.011× | 2 / 48 |
| `expanded-replace-redact` | 48 | 0.222× | 1.082× | 1.055–1.107× | 1 / 48 |
| `expanded-replace-template` | 48 | 0.163× | 0.784× | 0.777–0.792× | 42 / 48 |
| `expanded-whitespace-clean` | 48 | 0.352× | 1.157× | 1.138–1.178× | 1 / 48 |
| `large-bytes-replace` | 32 | 0.171× | 1.174× | 1.143–1.203× | 0 / 32 |
| `large-cleanup` | 32 | 0.591× | 0.950× | 0.935–0.964× | 10 / 32 |
| `large-module-replace` | 32 | 0.191× | 0.786× | 0.774–0.802× | 22 / 32 |
| `large-replace-callback` | 32 | 0.472× | 0.921× | 0.903–0.935× | 2 / 32 |
| `large-replace-groups` | 32 | 0.152× | 0.886× | 0.876–0.896× | 1 / 32 |
| `literal-replace` | 1 | 0.426× | 0.603× | 0.581–0.618× | 1 / 1 |
| `module-replace` | 1 | 0.206× | 0.742× | 0.724–0.761× | 1 / 1 |
| `real-lines` | 1 | 0.247× | 0.870× | 0.831–0.901× | 0 / 1 |
| `real-whitespace` | 1 | 0.196× | 0.729× | 0.680–0.764× | 1 / 1 |
| `replace-limited` | 1 | 0.205× | 0.828× | 0.813–0.843× | 1 / 1 |
| `sub` | 1 | 0.160× | 0.903× | 0.897–0.914× | 0 / 1 |
| `subn-callable` | 1 | 0.383× | 0.890× | 0.840–0.959× | 0 / 1 |
| `template-repeat` | 1 | 0.160× | 0.815× | 0.799–0.836× | 1 / 1 |
| **Total** | **697** | **0.265×** | **0.794×** | **0.790–0.796×** | **316 / 697** |

`deeper-source-comments` remains the largest measured loss because native replacement does not remove the cost of the underlying Rust matching and alternation engine. Warm module replacement, grouped templates, and large module replacement also remain substantially slower. All **316** genuinely greater-than-20% losing cases, their paired confidence intervals, timings, and memory observations remain among the 697 complete archived case results. The archive also separately preserves its **268** historical `speedup < 0.8` flags; those flags are not represented as the correct 20% boundary.

## Frozen evidence and reproducibility

All compressed evidence uses deterministic gzip without a filename or timestamp. Digests below identify the **uncompressed original** measurement, so changing compression cannot silently alter the timing data.

- [Previous Rust: all 697 case results, family intervals, and every slowdown](rust-v6-native-replacement-before.json.gz): SHA-256 `a4abded3516eff9c902e5fcbd3b74f8e715c0aab5adf75c1bea829d592683333`.
- [Previous Rust: all 4,182 paired raw rows](rust-v6-native-replacement-before.jsonl.gz): SHA-256 `6e73bda0cb4140c432f3e42dd08ea7b24aa0a5a8a4317fcd918197e563f4f595`.
- [Rejected attempt: all 697 case results, family intervals, 316 correctly recomputable slowdowns, and 268 historical archive flags](rust-v6-native-replacement-after.json.gz): SHA-256 `3e202b82ec41a8129baf7c76d457416924a8b8975fb5e5324993611e17c0047b`.
- [Rejected attempt: all 4,182 paired raw rows](rust-v6-native-replacement-after.jsonl.gz): SHA-256 `3258380928054210d2853834b840510432dc46f9a0183bfc76b76eb5013b728a`.
- [Reproducible evidence and paired-interval verifier](../../tools/rust_replacement_calibration.py).
- [Recorded integrity self-test](rust-v6-native-replacement-self.json). This checks evidence integrity, **not** candidate compatibility.
- [Generated adversarial callback, replacement, and mutation results](rust-v6-native-replacement-adversarial.json).
- [Full immutable 11,266-case rejected baseline, all 2,132 failing cases, and both clean stdlib self-oracle passes](rust-v6-native-replacement-deep-baseline.json.gz): uncompressed SHA-256 `149223dd866396eb07b0cdbd44766ccbda3d18710d06f7e25db95ce4628d0fc9`.
- [Corrected rebuilt bridge: all 11,266 replacement, callback, buffer, and identity checks passing](rust-v6-native-replacement-deep-corrected.json.gz): uncompressed SHA-256 `cd6df5040a0193ff26a7c58fa97428fc6fdcb697b2cf8a50752a45db381e2778`. This is a replacement-correctness follow-up, not a performance or whole-project qualification.
- [Expanded replacement and callback differential](../../tools/rust_replacement_adversarial.py). Its failing result, not the performance pilot, determines whether an implementation is compatible.

Verify every compressed artifact, all paired rows, frozen case identities, unchanged practice-only selection, matching expected answers, all seeded case and family intervals, all faster/slower counts, and both complete slowdown lists:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

"$PY" tools/rust_replacement_calibration.py self-test
```

Reproduce the full independent historical rejection using the immutable original engine and bridge snapshots. The command intentionally exits unsuccessfully because it rediscovers all 2,132 failures; later production rebuilds do not change the archived binary pair:

```sh
LD_LIBRARY_PATH=/tmp/rebar-rust-replacement-capture.yfLkaAUh \
PYTHONPATH=. "$PY" tools/rust_replacement_adversarial.py \
  --deep \
  --module candidates.rust_candidate \
  --bridge-path /tmp/rebar-rust-replacement-capture.yfLkaAUh/_rust_bridge.cpython-314-x86_64-linux-gnu.so \
  --engine-path /tmp/rebar-rust-replacement-capture.yfLkaAUh/_rust_engine.so \
  --output /tmp/rebar-rust-native-replacement-deep-reproduced.json
```

Rerun the identical practice-only performance selection against whichever Rust candidate is currently built:

```sh
PYTHONPATH=. "$PY" tools/rust_replacement_calibration.py measure \
  --output /tmp/rebar-rust-native-replacement-current.json \
  --raw /tmp/rebar-rust-native-replacement-current.jsonl
```

The reproduction command cannot select or access holdout cases. Rerunning it measures the current binary; it cannot recreate either historical binary without its separately preserved source and build configuration. The archived before/after measurements remain the evidence for this rejected experiment.

**NOT MEASURED:** corrected deferred-join replacement speed; complete frozen holdout performance; 13-trial, 2,000-resample holdout intervals; the final percentage of faster holdout cases; native memory after a correctness fix; final rankings; or satisfaction of any winner threshold.
