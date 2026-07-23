# Failed-final charts: preserve the first synthetic safety-check failure

**Incident: the first synthetic chart self-test failed safely.** The graph renderer correctly refused to publish a ranking graph that did not visibly say **NOT ESTABLISHED** after the real final experiment had failed. The renderer exited with status **1**. This was a test of synthetic records and graph text, not another benchmark, candidate execution, holdout opening, or attempt to change the actual final result.

The exact first-failed renderer source has SHA-256 `4dc7561cc60774c7e22595041bea65cf4e09eb6da49bf661a289d5ced99621e4`.

## Exact recorded first failure

```text
Traceback (most recent call last):
  File "<frozen runpy>", line 203, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/home/dev-user/src/rebar/tools/render_v9_failed_holdout.py", line 589, in <module>
    main()
  File "/home/dev-user/src/rebar/tools/render_v9_failed_holdout.py", line 572, in main
    self_test()
  File "/home/dev-user/src/rebar/tools/render_v9_failed_holdout.py", line 538, in self_test
    graphs = build_charts(record)
  File "/home/dev-user/src/rebar/tools/render_v9_failed_holdout.py", line 402, in build_charts
    require("NOT ESTABLISHED" in graph or suffix == "progress", f"the {suffix} graph implied a successful final result")
  File "/home/dev-user/src/rebar/tools/render_v9_failed_holdout.py", line 116, in require
    raise ValueError(message)
ValueError: the rankings graph implied a successful final result
```

The failure identifies the `rankings` graph. It does not indicate a mismatch in the already preserved failure record; it indicates that the proposed synthetic ranking graphic did not satisfy the existing, intentionally strict rule that an unsuccessful final result must not be depicted as an established candidate ranking.

## Preserve the original guard

The required correction is to visibly include the literal **NOT ESTABLISHED** in the ranking graph. Preserve the original check exactly:

```python
require(
    "NOT ESTABLISHED" in graph or suffix == "progress",
    f"the {suffix} graph implied a successful final result",
)
```

Do not remove, bypass, relax, special-case, or rewrite that requirement. Preserve the actual final-case denominator, the incomplete raw-row denominator, the failed outcome, and all original marker and no-retry semantics. A correction to graph labeling must never turn a failed or partial benchmark into a final ranking.

The initial incident was recorded while the corrected source and graphs were still pending. The subsequently released corrected renderer has SHA-256 `2ec285157b6b7cc512661e1b88a93a6db4057fca586c49f0898a2ac18f640974`. It visibly labels the ranking and every other required graph **NOT ESTABLISHED**, preserving the exact strict check above. Its synthetic self-test subsequently **passed all 58 controls** and generated six source-bound, deterministic failure graphs from the genuine audited failure. The initial failed source and exact traceback remain recorded.

## The irreversible final failure is unchanged

The genuine final-failure evidence JSON has SHA-256 `b3c9ac416d0a748a9fbe4f80f97efefb56ae7f598eea425c614aa278cb177069`. The unchanged source of its independent failure auditor has SHA-256 `510695deb6f6383fe321f0ae13225034f455011fcb5c22614815c24529b8a822`. Neither artifact is replaced or weakened by this separate synthetic chart incident.

The [complete explanation of the irreversibly opened, failed final benchmark](FINAL-HOLDOUT-FAILURE.md) and the [separate failure that occurred before unsealing](FINAL-PREUNSEAL-MISSING-TIME-INCIDENT.md) remain separate records. The real final benchmark completed **14,342 of 24,576 cases**, stopped on the genuine Zig-versus-CPython correctness mismatch, and cannot be retried. The synthetic chart failure neither reran a candidate nor accessed hidden subjects, the external seed, the marker, or a final measurement.

Final benchmark: **OPENED; FAILED; NO RETRY**. Completed cases: **14,342/24,576**. Complete final speed: **NOT MEASURED**. Final candidate ranking: **NOT ESTABLISHED**. Final winner: **NONE**.
