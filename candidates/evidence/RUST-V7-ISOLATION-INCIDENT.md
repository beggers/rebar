# Historical benchmark isolation incident

This report records an auxiliary research mistake and the measures taken to protect the frozen final speed test.

After the corrected Rust baseline and its practice-only measurements were committed as `29a6ba4d`, one auxiliary research branch performed a broad, read-only source search. The search results exposed text from a previously committed version-6 benchmark report. Some historical benchmark cases can overlap with the version-7 unseen test, so this exposure must not influence architecture selection even though it did not run a benchmark.

The branch reported the mistake immediately. The complete branch, including its child researchers and all of its native-boundary architecture proposals, was quarantined. Its research is excluded from optimization selection, measurements, and interpretation. No source was edited by the search, no frozen final fixture was generated or decoded, and no practice or final measurement was started by that branch.

The corrected-Rust baseline had already been independently measured, audited, committed, and pushed before this incident. Its [complete integrity report](../../performance/v7/evidence/rust-v7-calibration-corrected-v4-baseline-integrity.json) preserves all **8,736** timing records, all **175** large slowdowns, and verifies that all **10,312** final cases were inaccessible. The published baseline and its results are unchanged.

Subsequent experiments use only independently prepared candidates from researchers who did not encounter the historical report. Each candidate must pass the unchanged **223,198-case** correctness oracle and the sealed practice-only native-artifact checks before an exclusive, separately recorded timing run.

Final unseen benchmark: **NOT ACCESSED**. Quarantined-branch timing: **NOT MEASURED**.
