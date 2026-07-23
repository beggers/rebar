# Final candidates selected before the hidden benchmark

The final experiment uses stable CPython **3.14.6** and exactly three independently written regex implementations: C, Rust, and Zig. The selection was stopped at pushed `main` commit `89e550923ede9cbd558c02f91b235aa17ffaff97`, before the hidden benchmark was opened.

The original frozen-protocol command generated [V9-FINAL-CANDIDATE-SELECTION-FREEZE.json](V9-FINAL-CANDIDATE-SELECTION-FREEZE.json), SHA-256 `52066760bb4210a57f7b10f13e9ff73e36c53982a5b97aff40ead330c79edf41`. It independently fixes the unchanged Python baseline, the exact three candidate modules and loaded native libraries, all three matching and public-object proofs, all three complete 22-stage correctness campaigns, and the unchanged original from-scratch audit.

| Frozen implementation | Complete correctness campaign | Measured public-practice speed | Final hidden speed |
| --- | --- | ---: | --- |
| C | `a29b540e01fc9f565e01e5cc62af14db30b38d9bacbaf55e4950e95b17c7ea40` | 1.334× | NOT MEASURED |
| Rust | `9ddbab81b16f0440ca19bffb8a539ea08d4a7ff33606ee3019eaf85977c2249a` | 1.150× | NOT MEASURED |
| Zig | `4ba7cb9c45a70b747cc0a6eb721f6bb51081157f527d1bf5e578e603715ae5dc` | 1.257× | NOT MEASURED |

All three campaigns actually ran the original **22** correctness stages, including **4,494,555** Unicode comparisons each. The independently verified original no-delegation audit is SHA-256 `a790fe1a75c8748df7f8bb6f1e39d0be841636055358aaee94db0aa35523f326` and covers all five actually loaded native libraries.

The freeze command reported `opening_read=false`, `hidden_cases_generated=0`, `performance_measured=false`, `failed=0`, and exactly three candidates. No hidden input, opening, marker, final result, or final timing was read. The earlier nine public practice comparisons remain separate under `performance/v7/evidence`.

A final winner can only be selected from the genuine previously frozen **24,576-case** result. It must have zero correctness failures, an at-least **1.5×** measured geometric-mean speedup over CPython, and statistically faster results on at least **14,746** of the **24,576** cases. Every slowdown of more than 20% must remain visible. Until that complete one-time benchmark and independent results replay finish, the outcome is **NOT MEASURED** and no candidate is the winner.
