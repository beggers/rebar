# C diagnostic: safely identify a huge-repeat failure

The [original C campaign](rust-v8-vm-stage-11-sealed-campaign-failure.json) failed a frozen extended Python compatibility check without preserving the failing case. Its previous [unbounded diagnostic](../../tools/rust_v8_extended_paths_diagnostic_unbounded_v1.py) remains archived without modification.

The [new bounded diagnostic](../../tools/rust_v8_extended_paths_diagnostic.py) uses the exact original frozen patterns and Python comparison. Each candidate runs in a separate process, with a **three-second** limit per pattern, a **60-second** overall limit, and at most the first **16** existing manual patterns. Progress and timeout output are preserved. No frozen tests, expected results, or error comparisons are weakened.

The [two-reference self-test](rust-v8-extended-path-diagnostic-bounded-self-test.json) verifies all **16** patterns:

| Independently run Python reference | Completed checks | Differences |
| --- | ---: | ---: |
| First Python process | 784/784 | 0 |
| Second Python process | 784/784 | 0 |

The self-test also checks that a timeout fails safely, original worker output is retained, no timed-out process is retried, pattern objects remain distinguishable, and the unchanged frozen source is hash-verified.

The [one actual C run](rust-v8-vm-stage-11-bounded-manual-path-diagnostic.json) passes **441** checks across the first **nine** patterns. Frozen manual pattern **9** is `(?:ab){4294967294}` against `abab`. Python handles it within the bounded check, while the C implementation's Python front-end tries to expand **4,294,967,294** copies of the two-character pattern. The isolated C process exceeds its **three-second** limit and is terminated. Its unobserved matching answer is recorded as **NOT OBSERVED**, not as a guessed incorrect result.

This is a diagnosis, not a passing C campaign or performance benchmark. The complete **72,248-case** extended C result remains **NOT MEASURED**. The hidden final benchmark is **NOT ACCESSED**. C remains **NOT QUALIFIED**.

A [first attempted compact-repeat repair](C-STAGE-12-REJECTED-COMPACT-REPEAT.md) was independently checked, found to change optional-capture behavior, and rejected. Its exact failed implementation and both genuine differences remain preserved.

A [second compact-repeat repair](C-STAGE-13-REJECTED-SAFETY.md) subsequently passes all **784** original bounded comparisons and all **72,248** extended tests. Its separate isolated safety check reveals **10** remaining error and possessive-repeat differences, so it is also preserved rather than accepted.

A [third proposed repair](C-STAGE-14-REJECTED-INDEPENDENCE.md) fixes those safety differences and passes all frozen standalone compatibility categories. The unchanged no-delegation audit still rejects its `sys` import, so its source is preserved separately and not promoted.
