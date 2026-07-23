# Rejected Rust match-object optimization

This experiment tests a plausible native optimization against all **624** frozen practice cases. It does not open the final benchmark.

The native Python bridge was changed to use compact integer conversion, pre-sized fresh dictionaries, cached hashes for exact strings, and zero-copy complete-string captures. The change retains all Python-visible object identity, custom mapping behavior, profiling, tracing, callbacks, and exceptions. It passes the independent **223,198-case** correctness oracle, the **20,480-case** grammar suite, the **14,783-case** object suite, all **479** tracing and callback checks, and the full **18-step** safety campaign.

Nevertheless, the measured result does not support keeping the optimization:

| Frozen practice result | Corrected baseline | Match-object experiment |
| --- | ---: | ---: |
| Complete practice cases | 624 | 624 |
| Paired trials against Python | 7 | 7 |
| Overall speed compared with Python | 0.993845× | 0.983540× |
| 95% confidence interval | 0.955726–1.033812× | 0.944778–1.023386× |
| Cases significantly faster than Python | 245 | 252 |
| Cases taking more than 20% longer | 175 | 172 |
| Match-object cases taking more than 20% longer | 48/48 | 48/48 |
| Average match-object speed compared with Python | 0.326710× | 0.327588× |

Both confidence intervals include **1×**. The slight decrease in large slowdowns does not fix the targeted match-object bottleneck, and the overall measured speed is lower. The two runs were separately paired against Python, not directly paired against each other; no direct architecture-comparison confidence interval is claimed.

Decision: **REJECTED**. Restore the simpler, fully compatible baseline bridge.

All evidence is retained:

- [Complete 8,736-row experiment](rust-v7-calibration-corrected-v4-match-combined-raw.jsonl.gz).
- [All 624 case results and 172 large slowdowns](rust-v7-calibration-corrected-v4-match-combined-summary.json).
- [Independent architecture and native-binary integrity audit](rust-v7-calibration-corrected-v4-match-combined-integrity.json).
- [All 223,198 compatibility results](../../../candidates/evidence/rust-v7-edge-oracle-rust-corrected-v4-match-combined.json.gz).
- [Complete independently frozen grammar results](../../../candidates/evidence/rust-v7-grammar-rust-corrected-v4-match-combined.json.gz).
- [Complete object and safety evidence](../../../candidates/evidence/rust-v7-match-combined/).
- [Exact rejected bridge source change](../../../candidates/evidence/rust-v7-match-combined-rejected.patch).

The archived source change is preserved byte-for-byte, including its two original whitespace-only lines, and is independently checked with `git apply --check` against the restored bridge.

The experiment contains **8,736** timing rows and **26,208** per-operation correctness gates. The optimized bridge source has SHA-256 `559e8bcb6aeac226784ab50b7053a26931be53e9b1050b11a6bafa8c962b6170`; its source, mapped native engine, mapped native bridge, and Python module are independently verified before and after timing. All **175** original baseline regressions and all **172** experiment regressions remain visible.

Final unseen speed: **NOT MEASURED**. Final unseen cases read: **0**.
