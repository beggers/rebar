# Rejected C experiment: large repeats pass, safety does not

The [first compact-repeat design](C-STAGE-12-REJECTED-COMPACT-REPEAT.md) changed Python's empty-capture behavior. The [second design](C-STAGE-13-REJECTED-SAFETY.patch) corrects that behavior, retains the existing fast path for small repetitions, compiles large repeated subpatterns once, and attempts lazy matching incrementally.

| Frozen check | Actual result |
| --- | ---: |
| Original bounded patterns | [784/784](rust-v8-vm-stage-13-bounded-manual-path-diagnostic.json) |
| Complete extended Python checks | [72,248/72,248](rust-v8-vm-stage-13-extended-path-failures.json.gz) |
| Complete isolated safety checks | [10 differences in 254](rust-v8-vm-stage-13-isolated-safety.json) |
| Incorrect escaped-surrogate errors | 8 |
| Incorrect possessive-repeat matches | 2 |
| Native crashes | 0 |
| Timeouts | 0 |
| Python-reference failures | 0 |

The safety check retains all **10** exact failure rows. Python expects the displayed escaped Unicode endpoints and precise error offsets; the proposed C engine instead reports decoded surrogate values at the wrong positions. For both possessive-repeat patterns, Python correctly reports no full match while the candidate incorrectly returns a match. These are genuine observable correctness failures.

The rejected Python compiler's SHA-256 is `ad9b1d6868a9ca695f38f68be3e096548e73d8c1f6f55d9eec84ffc8c7dfc27a`; the native C source is `892696cbf35a146c4da3e9e677058c3873199a4d9053b7ba9e7b4a34d5908ee5`; its actual built native library is `6520023f79cc69afed8e0fd8a95d3822e458774eb79a65ded262f76014302e47`. The [complete source patch](C-STAGE-13-REJECTED-SAFETY.patch), both genuine passing reports, and complete failing safety report remain preserved.

Qualification: **FAILED**. Final performance: **NOT MEASURED**. Hidden final test: **NOT ACCESSED**.
