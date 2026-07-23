# C experiment: correctly report Python pattern errors

The C implementation has its own Python parser and separately written native matching engine. Its previous frozen full-campaign attempt exposed **144 actual mismatches in 420** Unicode group-name error checks. The complete [original 420-case failure](rust-v8-vm-stage-10-unicode-group-name-failure.json) remains unchanged.

The errors occur inside the C candidate's own parser before its native matcher runs. Python represents unusual conditional group names with their correctly escaped `repr`; line-and-column details must also be included when the complete pattern contains a newline, even if the error occurs on its first line. The repaired independent front-end implements those two general Python behaviors without calling Python's regex engine, importing an external regex package, changing another candidate, or hard-coding test cases.

| Frozen compatibility gate | Actual result |
| --- | ---: |
| Unicode group-name errors | 420/420 |
| Python's official `re` tests | 144 passed; 2 documented skips |
| Frozen baseline behavior | 8,244/8,244 |
| Public interface | 190/190 |
| Matching | 223,198/223,198 |
| Independent parser | 20,480/20,480 |
| Object and lifetime behavior | 393/393 |
| Tracing and native binding | 479/479 |
| Standard replacements | 8,862/8,862 |
| Deep replacements and callbacks | 11,266/11,266 |
| Complete 22-stage campaign | **FAIL: extended Python compatibility** |

The [one complete campaign attempt](rust-v8-vm-stage-11-sealed-campaign-failure.json) reaches the frozen `extended-cpython-paths` test and fails. Its unmodified reporter cannot serialize Python's compiled `Pattern` object while reporting the first actual mismatch. The number of completed extended checks and the mismatching case are **NOT REPORTED** and are not guessed. The [separate first-mismatch diagnostic](rust-v8-vm-stage-11-extended-path-first-mismatch-interrupted.json) was explicitly stopped before any case was emitted to provide an uncontended Rust timing slot; it is **INCONCLUSIVE**, not a passing check. Both failures, their exact command, exit codes, sources, unchanged full-campaign reporter, and all previous mismatches remain visible.

- [Original 144 Unicode group-name failures](rust-v8-vm-stage-10-unicode-group-name-failure.json).
- [All repaired Unicode group-name checks](rust-v8-vm-stage-11-unicode-group-name.json).
- [Official Python test results](rust-v8-vm-stage-11-official-cpython-tests.json).
- [All frozen baseline cases](rust-v8-vm-stage-11-frozen-correctness-v2.json).
- [All public interface checks](rust-v8-vm-stage-11-upstream-public-surface.json).
- [All independent matching cases](rust-v8-edge-oracle-vm-deep-stage-11.json.gz).
- [All independent parser cases](rust-v7-grammar-vm-v8-deep-stage-11.json.gz).
- [Object and lifetime checks](../audits/RUST-V8-DEEP-CONTRACT-C-STAGE-11.json.gz).
- [Tracing, native-binding, and engine-independence checks](rust-v8-observability-vm-qualified-stage-11.json.gz).
- [Standard replacements](rust-v8-replacement-vm-stage-11.json.gz).
- [Deep replacements](rust-v8-replacement-vm-deep-stage-11.json.gz).
- [Complete preserved failed campaign](rust-v8-vm-stage-11-sealed-campaign-failure.json).
- [Preserved interrupted mismatch diagnostic](rust-v8-vm-stage-11-extended-path-first-mismatch-interrupted.json).

Full compatibility: **NOT QUALIFIED**. Final benchmark: **NOT ACCESSED**. Final speed: **NOT MEASURED**.
