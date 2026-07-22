# Large performance holdout: initial results

Raw SHA-256: `e2c320457eeeecec63efbcc80c3ab0a17b1e27332a45d34155fa9819ffd13f2b`. Rows: **127,296**. All **7,344** candidate/task results and all **4,616** large slowdowns are retained below.

## Rankings

| Test set | Engine | Overall speed | 95% range | Clearly faster | Large slowdowns |
| --- | --- | ---: | ---: | ---: | ---: |
| calibration | Python engine | 0.0297× | 0.0296–0.0297× | 34/1,224 | 1,157 |
| calibration | Native C engine | 1.5267× | 1.5244–1.5293× | 1,133/1,224 | 43 |
| calibration | Rust engine | 0.1730× | 0.1727–0.1732× | 76/1,224 | 1,124 |
| holdout | Python engine | 0.0329× | 0.0328–0.0329× | 36/1,224 | 1,157 |
| holdout | Native C engine | 1.5613× | 1.5589–1.5638× | 1,130/1,224 | 11 |
| holdout | Rust engine | 0.1814× | 0.1811–0.1816× | 72/1,224 | 1,124 |
| all | Python engine | 0.0312× | 0.0312–0.0313× | 70/2,448 | 2,314 |
| all | Native C engine | 1.5439× | 1.5422–1.5456× | 2,263/2,448 | 54 |
| all | Rust engine | 0.1771× | 0.1769–0.1773× | 148/2,448 | 2,248 |

## Every large slowdown and its cause

Every result below 0.8× is grouped by engine and workload family. The stable task IDs are listed explicitly, so no slowdown is removed or hidden.

### Native C engine — 54 large slowdowns

- **everyday address (22):** the email-like find-all cases return many matches and repeatedly check several character classes; native profiling confirms the compact matcher performs 26–230 class checks and 60–518 repeated-character checks per call. `cal.large.everyday-address.01` (0.785×), `cal.large.everyday-address.04` (0.761×), `cal.large.everyday-address.07` (0.793×), `cal.large.everyday-address.10` (0.738×), `cal.large.everyday-address.13` (0.783×), `cal.large.everyday-address.16` (0.741×), `cal.large.everyday-address.19` (0.787×), `cal.large.everyday-address.22` (0.772×), `cal.large.everyday-address.25` (0.737×), `cal.large.everyday-address.28` (0.725×), `cal.large.everyday-address.31` (0.781×), `hold.large.everyday-address.01` (0.772×), `hold.large.everyday-address.04` (0.731×), `hold.large.everyday-address.07` (0.754×), `hold.large.everyday-address.10` (0.734×), `hold.large.everyday-address.13` (0.727×), `hold.large.everyday-address.16` (0.730×), `hold.large.everyday-address.19` (0.765×), `hold.large.everyday-address.22` (0.763×), `hold.large.everyday-address.25` (0.770×), `hold.large.everyday-address.28` (0.750×), `hold.large.everyday-address.31` (0.751×).
- **window search (32):** short windowed searches expose position/boundary overhead. `cal.large.window-search.00` (0.780×), `cal.large.window-search.01` (0.722×), `cal.large.window-search.02` (0.745×), `cal.large.window-search.03` (0.729×), `cal.large.window-search.04` (0.718×), `cal.large.window-search.05` (0.714×), `cal.large.window-search.06` (0.722×), `cal.large.window-search.07` (0.729×), `cal.large.window-search.08` (0.683×), `cal.large.window-search.09` (0.722×), `cal.large.window-search.10` (0.733×), `cal.large.window-search.11` (0.747×), `cal.large.window-search.12` (0.724×), `cal.large.window-search.13` (0.706×), `cal.large.window-search.14` (0.716×), `cal.large.window-search.15` (0.737×), `cal.large.window-search.16` (0.726×), `cal.large.window-search.17` (0.725×), `cal.large.window-search.18` (0.760×), `cal.large.window-search.19` (0.729×), `cal.large.window-search.20` (0.707×), `cal.large.window-search.21` (0.725×), `cal.large.window-search.22` (0.726×), `cal.large.window-search.23` (0.717×), `cal.large.window-search.24` (0.735×), `cal.large.window-search.25` (0.725×), `cal.large.window-search.26` (0.720×), `cal.large.window-search.27` (0.759×), `cal.large.window-search.28` (0.727×), `cal.large.window-search.29` (0.725×), `cal.large.window-search.30` (0.727×), `cal.large.window-search.31` (0.734×).

### Python engine — 2,314 large slowdowns

- **ascii mode (64):** word-boundary/category checks are repeated across the input. `cal.large.ascii-mode.00` (0.020×), `cal.large.ascii-mode.01` (0.021×), `cal.large.ascii-mode.02` (0.021×), `cal.large.ascii-mode.03` (0.020×), `cal.large.ascii-mode.04` (0.021×), `cal.large.ascii-mode.05` (0.021×), `cal.large.ascii-mode.06` (0.021×), `cal.large.ascii-mode.07` (0.020×), `cal.large.ascii-mode.08` (0.021×), `cal.large.ascii-mode.09` (0.021×), `cal.large.ascii-mode.10` (0.021×), `cal.large.ascii-mode.11` (0.021×), `cal.large.ascii-mode.12` (0.021×), `cal.large.ascii-mode.13` (0.021×), `cal.large.ascii-mode.14` (0.020×), `cal.large.ascii-mode.15` (0.021×), `cal.large.ascii-mode.16` (0.021×), `cal.large.ascii-mode.17` (0.021×), `cal.large.ascii-mode.18` (0.020×), `cal.large.ascii-mode.19` (0.020×), `cal.large.ascii-mode.20` (0.021×), `cal.large.ascii-mode.21` (0.021×), `cal.large.ascii-mode.22` (0.020×), `cal.large.ascii-mode.23` (0.021×), `cal.large.ascii-mode.24` (0.021×), `cal.large.ascii-mode.25` (0.022×), `cal.large.ascii-mode.26` (0.022×), `cal.large.ascii-mode.27` (0.021×), `cal.large.ascii-mode.28` (0.021×), `cal.large.ascii-mode.29` (0.022×), `cal.large.ascii-mode.30` (0.021×), `cal.large.ascii-mode.31` (0.021×), `hold.large.ascii-mode.00` (0.021×), `hold.large.ascii-mode.01` (0.021×), `hold.large.ascii-mode.02` (0.021×), `hold.large.ascii-mode.03` (0.020×), `hold.large.ascii-mode.04` (0.021×), `hold.large.ascii-mode.05` (0.021×), `hold.large.ascii-mode.06` (0.020×), `hold.large.ascii-mode.07` (0.020×), `hold.large.ascii-mode.08` (0.021×), `hold.large.ascii-mode.09` (0.022×), `hold.large.ascii-mode.10` (0.020×), `hold.large.ascii-mode.11` (0.021×), `hold.large.ascii-mode.12` (0.021×), `hold.large.ascii-mode.13` (0.020×), `hold.large.ascii-mode.14` (0.020×), `hold.large.ascii-mode.15` (0.020×), `hold.large.ascii-mode.16` (0.020×), `hold.large.ascii-mode.17` (0.020×), `hold.large.ascii-mode.18` (0.021×), `hold.large.ascii-mode.19` (0.021×), `hold.large.ascii-mode.20` (0.021×), `hold.large.ascii-mode.21` (0.021×), `hold.large.ascii-mode.22` (0.020×), `hold.large.ascii-mode.23` (0.021×), `hold.large.ascii-mode.24` (0.021×), `hold.large.ascii-mode.25` (0.021×), `hold.large.ascii-mode.26` (0.021×), `hold.large.ascii-mode.27` (0.021×), `hold.large.ascii-mode.28` (0.021×), `hold.large.ascii-mode.29` (0.021×), `hold.large.ascii-mode.30` (0.020×), `hold.large.ascii-mode.31` (0.021×).
- **branch control (64):** atomic/possessive and alternative paths require controlled backtracking. `cal.large.branch-control.00` (0.017×), `cal.large.branch-control.01` (0.015×), `cal.large.branch-control.02` (0.014×), `cal.large.branch-control.03` (0.013×), `cal.large.branch-control.04` (0.017×), `cal.large.branch-control.05` (0.015×), `cal.large.branch-control.06` (0.015×), `cal.large.branch-control.07` (0.013×), `cal.large.branch-control.08` (0.017×), `cal.large.branch-control.09` (0.015×), `cal.large.branch-control.10` (0.014×), `cal.large.branch-control.11` (0.013×), `cal.large.branch-control.12` (0.017×), `cal.large.branch-control.13` (0.015×), `cal.large.branch-control.14` (0.015×), `cal.large.branch-control.15` (0.013×), `cal.large.branch-control.16` (0.017×), `cal.large.branch-control.17` (0.015×), `cal.large.branch-control.18` (0.014×), `cal.large.branch-control.19` (0.013×), `cal.large.branch-control.20` (0.017×), `cal.large.branch-control.21` (0.015×), `cal.large.branch-control.22` (0.014×), `cal.large.branch-control.23` (0.013×), `cal.large.branch-control.24` (0.017×), `cal.large.branch-control.25` (0.015×), `cal.large.branch-control.26` (0.014×), `cal.large.branch-control.27` (0.013×), `cal.large.branch-control.28` (0.018×), `cal.large.branch-control.29` (0.015×), `cal.large.branch-control.30` (0.014×), `cal.large.branch-control.31` (0.013×), `hold.large.branch-control.00` (0.016×), `hold.large.branch-control.01` (0.013×), `hold.large.branch-control.02` (0.011×), `hold.large.branch-control.03` (0.010×), `hold.large.branch-control.04` (0.016×), `hold.large.branch-control.05` (0.014×), `hold.large.branch-control.06` (0.011×), `hold.large.branch-control.07` (0.010×), `hold.large.branch-control.08` (0.015×), `hold.large.branch-control.09` (0.013×), `hold.large.branch-control.10` (0.011×), `hold.large.branch-control.11` (0.010×), `hold.large.branch-control.12` (0.015×), `hold.large.branch-control.13` (0.013×), `hold.large.branch-control.14` (0.011×), `hold.large.branch-control.15` (0.010×), `hold.large.branch-control.16` (0.016×), `hold.large.branch-control.17` (0.013×), `hold.large.branch-control.18` (0.011×), `hold.large.branch-control.19` (0.010×), `hold.large.branch-control.20` (0.015×), `hold.large.branch-control.21` (0.013×), `hold.large.branch-control.22` (0.011×), `hold.large.branch-control.23` (0.010×), `hold.large.branch-control.24` (0.016×), `hold.large.branch-control.25` (0.013×), `hold.large.branch-control.26` (0.011×), `hold.large.branch-control.27` (0.010×), `hold.large.branch-control.28` (0.015×), `hold.large.branch-control.29` (0.013×), `hold.large.branch-control.30` (0.011×), `hold.large.branch-control.31` (0.010×).
- **bytes buffer (64):** mutable-buffer handling and match construction add boundary work. `cal.large.bytes-buffer.00` (0.018×), `cal.large.bytes-buffer.01` (0.015×), `cal.large.bytes-buffer.02` (0.013×), `cal.large.bytes-buffer.03` (0.012×), `cal.large.bytes-buffer.04` (0.018×), `cal.large.bytes-buffer.05` (0.015×), `cal.large.bytes-buffer.06` (0.014×), `cal.large.bytes-buffer.07` (0.012×), `cal.large.bytes-buffer.08` (0.018×), `cal.large.bytes-buffer.09` (0.015×), `cal.large.bytes-buffer.10` (0.013×), `cal.large.bytes-buffer.11` (0.012×), `cal.large.bytes-buffer.12` (0.018×), `cal.large.bytes-buffer.13` (0.015×), `cal.large.bytes-buffer.14` (0.014×), `cal.large.bytes-buffer.15` (0.012×), `cal.large.bytes-buffer.16` (0.017×), `cal.large.bytes-buffer.17` (0.015×), `cal.large.bytes-buffer.18` (0.013×), `cal.large.bytes-buffer.19` (0.013×), `cal.large.bytes-buffer.20` (0.018×), `cal.large.bytes-buffer.21` (0.015×), `cal.large.bytes-buffer.22` (0.014×), `cal.large.bytes-buffer.23` (0.012×), `cal.large.bytes-buffer.24` (0.018×), `cal.large.bytes-buffer.25` (0.015×), `cal.large.bytes-buffer.26` (0.014×), `cal.large.bytes-buffer.27` (0.012×), `cal.large.bytes-buffer.28` (0.017×), `cal.large.bytes-buffer.29` (0.014×), `cal.large.bytes-buffer.30` (0.013×), `cal.large.bytes-buffer.31` (0.012×), `hold.large.bytes-buffer.00` (0.032×), `hold.large.bytes-buffer.01` (0.025×), `hold.large.bytes-buffer.02` (0.022×), `hold.large.bytes-buffer.03` (0.020×), `hold.large.bytes-buffer.04` (0.028×), `hold.large.bytes-buffer.05` (0.024×), `hold.large.bytes-buffer.06` (0.022×), `hold.large.bytes-buffer.07` (0.020×), `hold.large.bytes-buffer.08` (0.028×), `hold.large.bytes-buffer.09` (0.024×), `hold.large.bytes-buffer.10` (0.021×), `hold.large.bytes-buffer.11` (0.020×), `hold.large.bytes-buffer.12` (0.027×), `hold.large.bytes-buffer.13` (0.023×), `hold.large.bytes-buffer.14` (0.021×), `hold.large.bytes-buffer.15` (0.019×), `hold.large.bytes-buffer.16` (0.027×), `hold.large.bytes-buffer.17` (0.024×), `hold.large.bytes-buffer.18` (0.022×), `hold.large.bytes-buffer.19` (0.021×), `hold.large.bytes-buffer.20` (0.030×), `hold.large.bytes-buffer.21` (0.024×), `hold.large.bytes-buffer.22` (0.021×), `hold.large.bytes-buffer.23` (0.021×), `hold.large.bytes-buffer.24` (0.028×), `hold.large.bytes-buffer.25` (0.024×), `hold.large.bytes-buffer.26` (0.022×), `hold.large.bytes-buffer.27` (0.020×), `hold.large.bytes-buffer.28` (0.027×), `hold.large.bytes-buffer.29` (0.024×), `hold.large.bytes-buffer.30` (0.021×), `hold.large.bytes-buffer.31` (0.019×).
- **bytes replace (64):** byte templates, captures, and joining amplify boundary work. `cal.large.bytes-replace.00` (0.027×), `cal.large.bytes-replace.01` (0.023×), `cal.large.bytes-replace.02` (0.022×), `cal.large.bytes-replace.03` (0.020×), `cal.large.bytes-replace.04` (0.027×), `cal.large.bytes-replace.05` (0.022×), `cal.large.bytes-replace.06` (0.024×), `cal.large.bytes-replace.07` (0.020×), `cal.large.bytes-replace.08` (0.028×), `cal.large.bytes-replace.09` (0.022×), `cal.large.bytes-replace.10` (0.023×), `cal.large.bytes-replace.11` (0.020×), `cal.large.bytes-replace.12` (0.027×), `cal.large.bytes-replace.13` (0.022×), `cal.large.bytes-replace.14` (0.021×), `cal.large.bytes-replace.15` (0.024×), `cal.large.bytes-replace.16` (0.026×), `cal.large.bytes-replace.17` (0.023×), `cal.large.bytes-replace.18` (0.022×), `cal.large.bytes-replace.19` (0.021×), `cal.large.bytes-replace.20` (0.026×), `cal.large.bytes-replace.21` (0.022×), `cal.large.bytes-replace.22` (0.021×), `cal.large.bytes-replace.23` (0.020×), `cal.large.bytes-replace.24` (0.028×), `cal.large.bytes-replace.25` (0.023×), `cal.large.bytes-replace.26` (0.021×), `cal.large.bytes-replace.27` (0.019×), `cal.large.bytes-replace.28` (0.025×), `cal.large.bytes-replace.29` (0.024×), `cal.large.bytes-replace.30` (0.023×), `cal.large.bytes-replace.31` (0.021×), `hold.large.bytes-replace.00` (0.026×), `hold.large.bytes-replace.01` (0.023×), `hold.large.bytes-replace.02` (0.022×), `hold.large.bytes-replace.03` (0.020×), `hold.large.bytes-replace.04` (0.027×), `hold.large.bytes-replace.05` (0.021×), `hold.large.bytes-replace.06` (0.022×), `hold.large.bytes-replace.07` (0.020×), `hold.large.bytes-replace.08` (0.027×), `hold.large.bytes-replace.09` (0.023×), `hold.large.bytes-replace.10` (0.024×), `hold.large.bytes-replace.11` (0.020×), `hold.large.bytes-replace.12` (0.027×), `hold.large.bytes-replace.13` (0.023×), `hold.large.bytes-replace.14` (0.024×), `hold.large.bytes-replace.15` (0.023×), `hold.large.bytes-replace.16` (0.026×), `hold.large.bytes-replace.17` (0.022×), `hold.large.bytes-replace.18` (0.023×), `hold.large.bytes-replace.19` (0.020×), `hold.large.bytes-replace.20` (0.027×), `hold.large.bytes-replace.21` (0.023×), `hold.large.bytes-replace.22` (0.022×), `hold.large.bytes-replace.23` (0.020×), `hold.large.bytes-replace.24` (0.027×), `hold.large.bytes-replace.25` (0.022×), `hold.large.bytes-replace.26` (0.022×), `hold.large.bytes-replace.27` (0.020×), `hold.large.bytes-replace.28` (0.027×), `hold.large.bytes-replace.29` (0.022×), `hold.large.bytes-replace.30` (0.023×), `hold.large.bytes-replace.31` (0.020×).
- **bytes tokens (64):** many byte results amplify collection and conversion work. `cal.large.bytes-tokens.00` (0.020×), `cal.large.bytes-tokens.01` (0.020×), `cal.large.bytes-tokens.02` (0.020×), `cal.large.bytes-tokens.03` (0.021×), `cal.large.bytes-tokens.04` (0.020×), `cal.large.bytes-tokens.05` (0.020×), `cal.large.bytes-tokens.06` (0.020×), `cal.large.bytes-tokens.07` (0.020×), `cal.large.bytes-tokens.08` (0.021×), `cal.large.bytes-tokens.09` (0.020×), `cal.large.bytes-tokens.10` (0.019×), `cal.large.bytes-tokens.11` (0.020×), `cal.large.bytes-tokens.12` (0.021×), `cal.large.bytes-tokens.13` (0.020×), `cal.large.bytes-tokens.14` (0.020×), `cal.large.bytes-tokens.15` (0.020×), `cal.large.bytes-tokens.16` (0.020×), `cal.large.bytes-tokens.17` (0.020×), `cal.large.bytes-tokens.18` (0.020×), `cal.large.bytes-tokens.19` (0.019×), `cal.large.bytes-tokens.20` (0.021×), `cal.large.bytes-tokens.21` (0.020×), `cal.large.bytes-tokens.22` (0.020×), `cal.large.bytes-tokens.23` (0.021×), `cal.large.bytes-tokens.24` (0.021×), `cal.large.bytes-tokens.25` (0.020×), `cal.large.bytes-tokens.26` (0.020×), `cal.large.bytes-tokens.27` (0.019×), `cal.large.bytes-tokens.28` (0.021×), `cal.large.bytes-tokens.29` (0.021×), `cal.large.bytes-tokens.30` (0.020×), `cal.large.bytes-tokens.31` (0.018×), `hold.large.bytes-tokens.00` (0.028×), `hold.large.bytes-tokens.01` (0.025×), `hold.large.bytes-tokens.02` (0.022×), `hold.large.bytes-tokens.03` (0.021×), `hold.large.bytes-tokens.04` (0.028×), `hold.large.bytes-tokens.05` (0.025×), `hold.large.bytes-tokens.06` (0.023×), `hold.large.bytes-tokens.07` (0.021×), `hold.large.bytes-tokens.08` (0.028×), `hold.large.bytes-tokens.09` (0.024×), `hold.large.bytes-tokens.10` (0.022×), `hold.large.bytes-tokens.11` (0.021×), `hold.large.bytes-tokens.12` (0.030×), `hold.large.bytes-tokens.13` (0.024×), `hold.large.bytes-tokens.14` (0.022×), `hold.large.bytes-tokens.15` (0.021×), `hold.large.bytes-tokens.16` (0.027×), `hold.large.bytes-tokens.17` (0.024×), `hold.large.bytes-tokens.18` (0.022×), `hold.large.bytes-tokens.19` (0.021×), `hold.large.bytes-tokens.20` (0.028×), `hold.large.bytes-tokens.21` (0.024×), `hold.large.bytes-tokens.22` (0.023×), `hold.large.bytes-tokens.23` (0.021×), `hold.large.bytes-tokens.24` (0.028×), `hold.large.bytes-tokens.25` (0.024×), `hold.large.bytes-tokens.26` (0.023×), `hold.large.bytes-tokens.27` (0.022×), `hold.large.bytes-tokens.28` (0.028×), `hold.large.bytes-tokens.29` (0.024×), `hold.large.bytes-tokens.30` (0.022×), `hold.large.bytes-tokens.31` (0.020×).
- **cleanup (64):** line cleanup and splitting amplify repeated scanning and collection. `cal.large.cleanup.00` (0.037×), `cal.large.cleanup.01` (0.026×), `cal.large.cleanup.02` (0.032×), `cal.large.cleanup.03` (0.025×), `cal.large.cleanup.04` (0.040×), `cal.large.cleanup.05` (0.024×), `cal.large.cleanup.06` (0.035×), `cal.large.cleanup.07` (0.026×), `cal.large.cleanup.08` (0.038×), `cal.large.cleanup.09` (0.025×), `cal.large.cleanup.10` (0.034×), `cal.large.cleanup.11` (0.025×), `cal.large.cleanup.12` (0.036×), `cal.large.cleanup.13` (0.025×), `cal.large.cleanup.14` (0.032×), `cal.large.cleanup.15` (0.025×), `cal.large.cleanup.16` (0.037×), `cal.large.cleanup.17` (0.025×), `cal.large.cleanup.18` (0.032×), `cal.large.cleanup.19` (0.022×), `cal.large.cleanup.20` (0.038×), `cal.large.cleanup.21` (0.025×), `cal.large.cleanup.22` (0.035×), `cal.large.cleanup.23` (0.026×), `cal.large.cleanup.24` (0.039×), `cal.large.cleanup.25` (0.025×), `cal.large.cleanup.26` (0.032×), `cal.large.cleanup.27` (0.026×), `cal.large.cleanup.28` (0.036×), `cal.large.cleanup.29` (0.025×), `cal.large.cleanup.30` (0.031×), `cal.large.cleanup.31` (0.025×), `hold.large.cleanup.00` (0.036×), `hold.large.cleanup.01` (0.025×), `hold.large.cleanup.02` (0.032×), `hold.large.cleanup.03` (0.026×), `hold.large.cleanup.04` (0.037×), `hold.large.cleanup.05` (0.025×), `hold.large.cleanup.06` (0.032×), `hold.large.cleanup.07` (0.026×), `hold.large.cleanup.08` (0.037×), `hold.large.cleanup.09` (0.025×), `hold.large.cleanup.10` (0.034×), `hold.large.cleanup.11` (0.025×), `hold.large.cleanup.12` (0.037×), `hold.large.cleanup.13` (0.025×), `hold.large.cleanup.14` (0.033×), `hold.large.cleanup.15` (0.025×), `hold.large.cleanup.16` (0.037×), `hold.large.cleanup.17` (0.028×), `hold.large.cleanup.18` (0.032×), `hold.large.cleanup.19` (0.025×), `hold.large.cleanup.20` (0.037×), `hold.large.cleanup.21` (0.028×), `hold.large.cleanup.22` (0.034×), `hold.large.cleanup.23` (0.025×), `hold.large.cleanup.24` (0.035×), `hold.large.cleanup.25` (0.025×), `hold.large.cleanup.26` (0.032×), `hold.large.cleanup.27` (0.025×), `hold.large.cleanup.28` (0.039×), `hold.large.cleanup.29` (0.025×), `hold.large.cleanup.30` (0.032×), `hold.large.cleanup.31` (0.024×).
- **cold search (64):** fresh compilation dominates a single short search. `cal.large.cold-search.00` (0.095×), `cal.large.cold-search.01` (0.095×), `cal.large.cold-search.02` (0.089×), `cal.large.cold-search.03` (0.094×), `cal.large.cold-search.04` (0.092×), `cal.large.cold-search.05` (0.092×), `cal.large.cold-search.06` (0.090×), `cal.large.cold-search.07` (0.096×), `cal.large.cold-search.08` (0.096×), `cal.large.cold-search.09` (0.093×), `cal.large.cold-search.10` (0.093×), `cal.large.cold-search.11` (0.092×), `cal.large.cold-search.12` (0.091×), `cal.large.cold-search.13` (0.090×), `cal.large.cold-search.14` (0.096×), `cal.large.cold-search.15` (0.096×), `cal.large.cold-search.16` (0.094×), `cal.large.cold-search.17` (0.094×), `cal.large.cold-search.18` (0.092×), `cal.large.cold-search.19` (0.091×), `cal.large.cold-search.20` (0.091×), `cal.large.cold-search.21` (0.096×), `cal.large.cold-search.22` (0.095×), `cal.large.cold-search.23` (0.094×), `cal.large.cold-search.24` (0.093×), `cal.large.cold-search.25` (0.093×), `cal.large.cold-search.26` (0.093×), `cal.large.cold-search.27` (0.090×), `cal.large.cold-search.28` (0.097×), `cal.large.cold-search.29` (0.096×), `cal.large.cold-search.30` (0.096×), `cal.large.cold-search.31` (0.094×), `hold.large.cold-search.00` (0.104×), `hold.large.cold-search.01` (0.105×), `hold.large.cold-search.02` (0.102×), `hold.large.cold-search.03` (0.103×), `hold.large.cold-search.04` (0.102×), `hold.large.cold-search.05` (0.101×), `hold.large.cold-search.06` (0.100×), `hold.large.cold-search.07` (0.104×), `hold.large.cold-search.08` (0.105×), `hold.large.cold-search.09` (0.105×), `hold.large.cold-search.10` (0.102×), `hold.large.cold-search.11` (0.100×), `hold.large.cold-search.12` (0.101×), `hold.large.cold-search.13` (0.098×), `hold.large.cold-search.14` (0.099×), `hold.large.cold-search.15` (0.101×), `hold.large.cold-search.16` (0.103×), `hold.large.cold-search.17` (0.097×), `hold.large.cold-search.18` (0.100×), `hold.large.cold-search.19` (0.100×), `hold.large.cold-search.20` (0.105×), `hold.large.cold-search.21` (0.110×), `hold.large.cold-search.22` (0.106×), `hold.large.cold-search.23` (0.104×), `hold.large.cold-search.24` (0.101×), `hold.large.cold-search.25` (0.101×), `hold.large.cold-search.26` (0.102×), `hold.large.cold-search.27` (0.102×), `hold.large.cold-search.28` (0.107×), `hold.large.cold-search.29` (0.105×), `hold.large.cold-search.30` (0.104×), `hold.large.cold-search.31` (0.101×).
- **conditionals (64):** conditionals depend on capture state and branch selection. `cal.large.conditionals.00` (0.027×), `cal.large.conditionals.01` (0.027×), `cal.large.conditionals.02` (0.030×), `cal.large.conditionals.03` (0.029×), `cal.large.conditionals.04` (0.027×), `cal.large.conditionals.05` (0.028×), `cal.large.conditionals.06` (0.028×), `cal.large.conditionals.07` (0.030×), `cal.large.conditionals.08` (0.026×), `cal.large.conditionals.09` (0.027×), `cal.large.conditionals.10` (0.029×), `cal.large.conditionals.11` (0.031×), `cal.large.conditionals.12` (0.028×), `cal.large.conditionals.13` (0.027×), `cal.large.conditionals.14` (0.028×), `cal.large.conditionals.15` (0.030×), `cal.large.conditionals.16` (0.027×), `cal.large.conditionals.17` (0.027×), `cal.large.conditionals.18` (0.028×), `cal.large.conditionals.19` (0.030×), `cal.large.conditionals.20` (0.028×), `cal.large.conditionals.21` (0.027×), `cal.large.conditionals.22` (0.028×), `cal.large.conditionals.23` (0.029×), `cal.large.conditionals.24` (0.027×), `cal.large.conditionals.25` (0.027×), `cal.large.conditionals.26` (0.028×), `cal.large.conditionals.27` (0.030×), `cal.large.conditionals.28` (0.027×), `cal.large.conditionals.29` (0.027×), `cal.large.conditionals.30` (0.029×), `cal.large.conditionals.31` (0.031×), `hold.large.conditionals.00` (0.027×), `hold.large.conditionals.01` (0.027×), `hold.large.conditionals.02` (0.029×), `hold.large.conditionals.03` (0.030×), `hold.large.conditionals.04` (0.027×), `hold.large.conditionals.05` (0.027×), `hold.large.conditionals.06` (0.029×), `hold.large.conditionals.07` (0.030×), `hold.large.conditionals.08` (0.028×), `hold.large.conditionals.09` (0.028×), `hold.large.conditionals.10` (0.028×), `hold.large.conditionals.11` (0.031×), `hold.large.conditionals.12` (0.027×), `hold.large.conditionals.13` (0.029×), `hold.large.conditionals.14` (0.028×), `hold.large.conditionals.15` (0.030×), `hold.large.conditionals.16` (0.029×), `hold.large.conditionals.17` (0.029×), `hold.large.conditionals.18` (0.028×), `hold.large.conditionals.19` (0.031×), `hold.large.conditionals.20` (0.027×), `hold.large.conditionals.21` (0.028×), `hold.large.conditionals.22` (0.029×), `hold.large.conditionals.23` (0.031×), `hold.large.conditionals.24` (0.028×), `hold.large.conditionals.25` (0.026×), `hold.large.conditionals.26` (0.028×), `hold.large.conditionals.27` (0.031×), `hold.large.conditionals.28` (0.027×), `hold.large.conditionals.29` (0.027×), `hold.large.conditionals.30` (0.029×), `hold.large.conditionals.31` (0.030×).
- **earlier 72 (138):** the earlier mixed workloads retain their documented scanning, Unicode, collection, and boundary costs. `cal.search.literal.hit` (0.042×), `cal.search.literal.miss` (0.140×), `cal.search.long-boundary` (0.285×), `cal.search.class-anchor` (0.028×), `cal.match.prefix` (0.025×), `cal.fullmatch.structured` (0.018×), `cal.search.look-capture` (0.024×), `cal.findall.tokens` (0.020×), `cal.finditer.groups` (0.020×), `cal.split.capture` (0.018×), `cal.sub.template` (0.021×), `cal.subn.callable` (0.063×), `cal.bytes.tokens` (0.019×), `cal.unicode.words` (0.023×), `cal.cold.compile-search` (0.080×), `cal.module.warm` (0.022×), `cal.empty.finditer` (0.018×), `cal.backref.fullmatch` (0.021×), `cal.conditional.match` (0.026×), `cal.atomic.search` (0.029×), `cal.byteslike.findall` (0.016×), `cal.unicode-name.search` (0.046×), `cal.ignorecase.findall` (0.031×), `cal.many.split` (0.024×), `cal.scanner.search` (0.021×), `cal.match.surface` (0.024×), `hold.search.literal.hit` (0.044×), `hold.search.literal.miss` (0.142×), `hold.search.long-boundary` (0.376×), `hold.search.class-anchor` (0.028×), `hold.match.prefix` (0.027×), `hold.fullmatch.structured` (0.014×), `hold.search.look-capture` (0.019×), `hold.findall.tokens` (0.019×), `hold.finditer.groups` (0.021×), `hold.split.capture` (0.017×), `hold.sub.template` (0.022×), `hold.subn.callable` (0.060×), `hold.bytes.tokens` (0.020×), `hold.unicode.words` (0.026×), `hold.cold.compile-search` (0.092×), `hold.module.warm` (0.074×), `hold.empty.finditer` (0.015×), `hold.backref.fullmatch` (0.019×), `hold.conditional.match` (0.028×), `hold.atomic.search` (0.032×), `hold.byteslike.findall` (0.017×), `hold.unicode-name.search` (0.046×), `hold.ignorecase.findall` (0.032×), `hold.many.split` (0.023×), `hold.scanner.search` (0.020×), `hold.match.surface` (0.057×), `cal.real.log` (0.022×), `cal.real.url` (0.014×), `cal.real.email` (0.014×), `cal.real.datetime` (0.011×), `cal.real.version` (0.016×), `cal.real.uuid` (0.014×), `cal.real.ip` (0.009×), `cal.real.path` (0.009×), `cal.real.config` (0.015×), `cal.real.comments` (0.020×), `cal.real.whitespace` (0.038×), `cal.real.lines` (0.028×), `cal.real.markup` (0.012×), `cal.real.quotes` (0.009×), `cal.real.csv` (0.009×), `cal.branch.prefix` (0.022×), `cal.branch.miss` (0.005×), `cal.repeat.nested` (0.014×), `cal.lines.records` (0.012×), `cal.block.dotall` (0.016×), `cal.pattern.verbose` (0.008×), `cal.mode.ascii` (0.021×), `cal.mode.casefold` (0.024×), `cal.mode.astral` (0.025×), `cal.look.negative-ahead` (0.010×), `cal.look.negative-behind` (0.020×), `cal.bytes.replace` (0.023×), `cal.bytes.scan` (0.017×), `cal.module.replace` (0.028×), `cal.zero.boundary` (0.013×), `cal.dense.iter` (0.022×), `cal.capture.optional` (0.016×), `cal.split.limited` (0.017×), `cal.replace.limited` (0.034×), `cal.bytes.view-long` (0.017×), `cal.window.search` (0.042×), `cal.window.findall` (0.034×), `cal.window.scanner` (0.028×), `cal.window.match` (0.035×), `cal.literal.replace` (0.047×), `cal.template.repeat` (0.027×), `cal.match.miss` (0.034×), `cal.fullmatch.miss` (0.020×), `hold.real.log` (0.022×), `hold.real.url` (0.016×), `hold.real.email` (0.011×), `hold.real.datetime` (0.014×), `hold.real.version` (0.014×), `hold.real.uuid` (0.012×), `hold.real.ip` (0.010×), `hold.real.path` (0.008×), `hold.real.config` (0.013×), `hold.real.comments` (0.022×), `hold.real.whitespace` (0.034×), `hold.real.lines` (0.026×), `hold.real.markup` (0.012×), `hold.real.quotes` (0.010×), `hold.real.csv` (0.008×), `hold.branch.prefix` (0.021×), `hold.branch.miss` (0.005×), `hold.repeat.nested` (0.013×), `hold.lines.records` (0.012×), `hold.block.dotall` (0.014×), `hold.pattern.verbose` (0.008×), `hold.mode.ascii` (0.020×), `hold.mode.casefold` (0.027×), `hold.mode.astral` (0.024×), `hold.look.negative-ahead` (0.009×), `hold.look.negative-behind` (0.021×), `hold.bytes.replace` (0.022×), `hold.bytes.scan` (0.017×), `hold.module.replace` (0.028×), `hold.zero.boundary` (0.014×), `hold.dense.iter` (0.023×), `hold.capture.optional` (0.015×), `hold.split.limited` (0.017×), `hold.replace.limited` (0.032×), `hold.bytes.view-long` (0.016×), `hold.window.search` (0.041×), `hold.window.findall` (0.027×), `hold.window.scanner` (0.029×), `hold.window.match` (0.033×), `hold.literal.replace` (0.049×), `hold.template.repeat` (0.026×), `hold.match.miss` (0.036×), `hold.fullmatch.miss` (0.019×).
- **empty iterator (64):** empty matches require careful progress and many result objects. `cal.large.empty-iterator.00` (0.017×), `cal.large.empty-iterator.01` (0.016×), `cal.large.empty-iterator.02` (0.015×), `cal.large.empty-iterator.03` (0.015×), `cal.large.empty-iterator.04` (0.018×), `cal.large.empty-iterator.05` (0.016×), `cal.large.empty-iterator.06` (0.016×), `cal.large.empty-iterator.07` (0.016×), `cal.large.empty-iterator.08` (0.019×), `cal.large.empty-iterator.09` (0.015×), `cal.large.empty-iterator.10` (0.016×), `cal.large.empty-iterator.11` (0.015×), `cal.large.empty-iterator.12` (0.019×), `cal.large.empty-iterator.13` (0.016×), `cal.large.empty-iterator.14` (0.015×), `cal.large.empty-iterator.15` (0.015×), `cal.large.empty-iterator.16` (0.017×), `cal.large.empty-iterator.17` (0.017×), `cal.large.empty-iterator.18` (0.015×), `cal.large.empty-iterator.19` (0.015×), `cal.large.empty-iterator.20` (0.019×), `cal.large.empty-iterator.21` (0.016×), `cal.large.empty-iterator.22` (0.015×), `cal.large.empty-iterator.23` (0.016×), `cal.large.empty-iterator.24` (0.018×), `cal.large.empty-iterator.25` (0.016×), `cal.large.empty-iterator.26` (0.014×), `cal.large.empty-iterator.27` (0.015×), `cal.large.empty-iterator.28` (0.019×), `cal.large.empty-iterator.29` (0.016×), `cal.large.empty-iterator.30` (0.015×), `cal.large.empty-iterator.31` (0.015×), `hold.large.empty-iterator.00` (0.015×), `hold.large.empty-iterator.01` (0.012×), `hold.large.empty-iterator.02` (0.011×), `hold.large.empty-iterator.03` (0.011×), `hold.large.empty-iterator.04` (0.015×), `hold.large.empty-iterator.05` (0.012×), `hold.large.empty-iterator.06` (0.011×), `hold.large.empty-iterator.07` (0.011×), `hold.large.empty-iterator.08` (0.015×), `hold.large.empty-iterator.09` (0.012×), `hold.large.empty-iterator.10` (0.011×), `hold.large.empty-iterator.11` (0.011×), `hold.large.empty-iterator.12` (0.015×), `hold.large.empty-iterator.13` (0.012×), `hold.large.empty-iterator.14` (0.012×), `hold.large.empty-iterator.15` (0.011×), `hold.large.empty-iterator.16` (0.015×), `hold.large.empty-iterator.17` (0.012×), `hold.large.empty-iterator.18` (0.011×), `hold.large.empty-iterator.19` (0.010×), `hold.large.empty-iterator.20` (0.015×), `hold.large.empty-iterator.21` (0.013×), `hold.large.empty-iterator.22` (0.011×), `hold.large.empty-iterator.23` (0.011×), `hold.large.empty-iterator.24` (0.016×), `hold.large.empty-iterator.25` (0.012×), `hold.large.empty-iterator.26` (0.011×), `hold.large.empty-iterator.27` (0.011×), `hold.large.empty-iterator.28` (0.015×), `hold.large.empty-iterator.29` (0.013×), `hold.large.empty-iterator.30` (0.012×), `hold.large.empty-iterator.31` (0.011×).
- **everyday address (64):** the email-like find-all cases return many matches and repeatedly check several character classes; native profiling confirms the compact matcher performs 26–230 class checks and 60–518 repeated-character checks per call. `cal.large.everyday-address.00` (0.014×), `cal.large.everyday-address.01` (0.016×), `cal.large.everyday-address.02` (0.012×), `cal.large.everyday-address.03` (0.018×), `cal.large.everyday-address.04` (0.016×), `cal.large.everyday-address.05` (0.011×), `cal.large.everyday-address.06` (0.016×), `cal.large.everyday-address.07` (0.016×), `cal.large.everyday-address.08` (0.011×), `cal.large.everyday-address.09` (0.015×), `cal.large.everyday-address.10` (0.016×), `cal.large.everyday-address.11` (0.013×), `cal.large.everyday-address.12` (0.015×), `cal.large.everyday-address.13` (0.016×), `cal.large.everyday-address.14` (0.012×), `cal.large.everyday-address.15` (0.018×), `cal.large.everyday-address.16` (0.016×), `cal.large.everyday-address.17` (0.011×), `cal.large.everyday-address.18` (0.016×), `cal.large.everyday-address.19` (0.017×), `cal.large.everyday-address.20` (0.011×), `cal.large.everyday-address.21` (0.016×), `cal.large.everyday-address.22` (0.016×), `cal.large.everyday-address.23` (0.013×), `cal.large.everyday-address.24` (0.015×), `cal.large.everyday-address.25` (0.016×), `cal.large.everyday-address.26` (0.012×), `cal.large.everyday-address.27` (0.018×), `cal.large.everyday-address.28` (0.016×), `cal.large.everyday-address.29` (0.011×), `cal.large.everyday-address.30` (0.016×), `cal.large.everyday-address.31` (0.016×), `hold.large.everyday-address.00` (0.015×), `hold.large.everyday-address.01` (0.016×), `hold.large.everyday-address.02` (0.011×), `hold.large.everyday-address.03` (0.019×), `hold.large.everyday-address.04` (0.016×), `hold.large.everyday-address.05` (0.011×), `hold.large.everyday-address.06` (0.017×), `hold.large.everyday-address.07` (0.016×), `hold.large.everyday-address.08` (0.011×), `hold.large.everyday-address.09` (0.017×), `hold.large.everyday-address.10` (0.016×), `hold.large.everyday-address.11` (0.013×), `hold.large.everyday-address.12` (0.016×), `hold.large.everyday-address.13` (0.016×), `hold.large.everyday-address.14` (0.012×), `hold.large.everyday-address.15` (0.019×), `hold.large.everyday-address.16` (0.016×), `hold.large.everyday-address.17` (0.011×), `hold.large.everyday-address.18` (0.016×), `hold.large.everyday-address.19` (0.015×), `hold.large.everyday-address.20` (0.011×), `hold.large.everyday-address.21` (0.017×), `hold.large.everyday-address.22` (0.017×), `hold.large.everyday-address.23` (0.013×), `hold.large.everyday-address.24` (0.015×), `hold.large.everyday-address.25` (0.015×), `hold.large.everyday-address.26` (0.011×), `hold.large.everyday-address.27` (0.018×), `hold.large.everyday-address.28` (0.016×), `hold.large.everyday-address.29` (0.011×), `hold.large.everyday-address.30` (0.017×), `hold.large.everyday-address.31` (0.016×).
- **findall tokens (64):** many returned tokens amplify scanning and result construction. `cal.large.findall-tokens.00` (0.019×), `cal.large.findall-tokens.01` (0.020×), `cal.large.findall-tokens.02` (0.020×), `cal.large.findall-tokens.03` (0.019×), `cal.large.findall-tokens.04` (0.020×), `cal.large.findall-tokens.05` (0.020×), `cal.large.findall-tokens.06` (0.019×), `cal.large.findall-tokens.07` (0.019×), `cal.large.findall-tokens.08` (0.019×), `cal.large.findall-tokens.09` (0.019×), `cal.large.findall-tokens.10` (0.019×), `cal.large.findall-tokens.11` (0.019×), `cal.large.findall-tokens.12` (0.019×), `cal.large.findall-tokens.13` (0.019×), `cal.large.findall-tokens.14` (0.019×), `cal.large.findall-tokens.15` (0.019×), `cal.large.findall-tokens.16` (0.021×), `cal.large.findall-tokens.17` (0.018×), `cal.large.findall-tokens.18` (0.021×), `cal.large.findall-tokens.19` (0.019×), `cal.large.findall-tokens.20` (0.021×), `cal.large.findall-tokens.21` (0.021×), `cal.large.findall-tokens.22` (0.020×), `cal.large.findall-tokens.23` (0.020×), `cal.large.findall-tokens.24` (0.018×), `cal.large.findall-tokens.25` (0.019×), `cal.large.findall-tokens.26` (0.019×), `cal.large.findall-tokens.27` (0.019×), `cal.large.findall-tokens.28` (0.019×), `cal.large.findall-tokens.29` (0.019×), `cal.large.findall-tokens.30` (0.019×), `cal.large.findall-tokens.31` (0.020×), `hold.large.findall-tokens.00` (0.021×), `hold.large.findall-tokens.01` (0.020×), `hold.large.findall-tokens.02` (0.020×), `hold.large.findall-tokens.03` (0.019×), `hold.large.findall-tokens.04` (0.019×), `hold.large.findall-tokens.05` (0.019×), `hold.large.findall-tokens.06` (0.020×), `hold.large.findall-tokens.07` (0.019×), `hold.large.findall-tokens.08` (0.020×), `hold.large.findall-tokens.09` (0.019×), `hold.large.findall-tokens.10` (0.020×), `hold.large.findall-tokens.11` (0.020×), `hold.large.findall-tokens.12` (0.020×), `hold.large.findall-tokens.13` (0.020×), `hold.large.findall-tokens.14` (0.020×), `hold.large.findall-tokens.15` (0.020×), `hold.large.findall-tokens.16` (0.020×), `hold.large.findall-tokens.17` (0.020×), `hold.large.findall-tokens.18` (0.020×), `hold.large.findall-tokens.19` (0.019×), `hold.large.findall-tokens.20` (0.021×), `hold.large.findall-tokens.21` (0.019×), `hold.large.findall-tokens.22` (0.019×), `hold.large.findall-tokens.23` (0.020×), `hold.large.findall-tokens.24` (0.020×), `hold.large.findall-tokens.25` (0.019×), `hold.large.findall-tokens.26` (0.020×), `hold.large.findall-tokens.27` (0.020×), `hold.large.findall-tokens.28` (0.019×), `hold.large.findall-tokens.29` (0.020×), `hold.large.findall-tokens.30` (0.020×), `hold.large.findall-tokens.31` (0.019×).
- **finditer pairs (64):** many captures amplify iterator and match-object construction. `cal.large.finditer-pairs.00` (0.026×), `cal.large.finditer-pairs.01` (0.021×), `cal.large.finditer-pairs.02` (0.018×), `cal.large.finditer-pairs.03` (0.017×), `cal.large.finditer-pairs.04` (0.025×), `cal.large.finditer-pairs.05` (0.021×), `cal.large.finditer-pairs.06` (0.019×), `cal.large.finditer-pairs.07` (0.017×), `cal.large.finditer-pairs.08` (0.025×), `cal.large.finditer-pairs.09` (0.021×), `cal.large.finditer-pairs.10` (0.019×), `cal.large.finditer-pairs.11` (0.018×), `cal.large.finditer-pairs.12` (0.026×), `cal.large.finditer-pairs.13` (0.021×), `cal.large.finditer-pairs.14` (0.020×), `cal.large.finditer-pairs.15` (0.018×), `cal.large.finditer-pairs.16` (0.025×), `cal.large.finditer-pairs.17` (0.022×), `cal.large.finditer-pairs.18` (0.019×), `cal.large.finditer-pairs.19` (0.018×), `cal.large.finditer-pairs.20` (0.026×), `cal.large.finditer-pairs.21` (0.020×), `cal.large.finditer-pairs.22` (0.018×), `cal.large.finditer-pairs.23` (0.018×), `cal.large.finditer-pairs.24` (0.025×), `cal.large.finditer-pairs.25` (0.021×), `cal.large.finditer-pairs.26` (0.018×), `cal.large.finditer-pairs.27` (0.018×), `cal.large.finditer-pairs.28` (0.025×), `cal.large.finditer-pairs.29` (0.020×), `cal.large.finditer-pairs.30` (0.018×), `cal.large.finditer-pairs.31` (0.017×), `hold.large.finditer-pairs.00` (0.026×), `hold.large.finditer-pairs.01` (0.021×), `hold.large.finditer-pairs.02` (0.018×), `hold.large.finditer-pairs.03` (0.017×), `hold.large.finditer-pairs.04` (0.025×), `hold.large.finditer-pairs.05` (0.020×), `hold.large.finditer-pairs.06` (0.018×), `hold.large.finditer-pairs.07` (0.017×), `hold.large.finditer-pairs.08` (0.025×), `hold.large.finditer-pairs.09` (0.021×), `hold.large.finditer-pairs.10` (0.019×), `hold.large.finditer-pairs.11` (0.017×), `hold.large.finditer-pairs.12` (0.024×), `hold.large.finditer-pairs.13` (0.020×), `hold.large.finditer-pairs.14` (0.018×), `hold.large.finditer-pairs.15` (0.017×), `hold.large.finditer-pairs.16` (0.025×), `hold.large.finditer-pairs.17` (0.020×), `hold.large.finditer-pairs.18` (0.019×), `hold.large.finditer-pairs.19` (0.017×), `hold.large.finditer-pairs.20` (0.025×), `hold.large.finditer-pairs.21` (0.021×), `hold.large.finditer-pairs.22` (0.019×), `hold.large.finditer-pairs.23` (0.017×), `hold.large.finditer-pairs.24` (0.025×), `hold.large.finditer-pairs.25` (0.021×), `hold.large.finditer-pairs.26` (0.019×), `hold.large.finditer-pairs.27` (0.018×), `hold.large.finditer-pairs.28` (0.025×), `hold.large.finditer-pairs.29` (0.021×), `hold.large.finditer-pairs.30` (0.018×), `hold.large.finditer-pairs.31` (0.018×).
- **formatted lines (64):** many line starts and character-class checks amplify per-match work. `cal.large.formatted-lines.00` (0.012×), `cal.large.formatted-lines.01` (0.009×), `cal.large.formatted-lines.02` (0.009×), `cal.large.formatted-lines.03` (0.009×), `cal.large.formatted-lines.04` (0.011×), `cal.large.formatted-lines.05` (0.010×), `cal.large.formatted-lines.06` (0.009×), `cal.large.formatted-lines.07` (0.009×), `cal.large.formatted-lines.08` (0.011×), `cal.large.formatted-lines.09` (0.010×), `cal.large.formatted-lines.10` (0.009×), `cal.large.formatted-lines.11` (0.009×), `cal.large.formatted-lines.12` (0.011×), `cal.large.formatted-lines.13` (0.009×), `cal.large.formatted-lines.14` (0.009×), `cal.large.formatted-lines.15` (0.009×), `cal.large.formatted-lines.16` (0.011×), `cal.large.formatted-lines.17` (0.010×), `cal.large.formatted-lines.18` (0.009×), `cal.large.formatted-lines.19` (0.009×), `cal.large.formatted-lines.20` (0.011×), `cal.large.formatted-lines.21` (0.009×), `cal.large.formatted-lines.22` (0.009×), `cal.large.formatted-lines.23` (0.009×), `cal.large.formatted-lines.24` (0.011×), `cal.large.formatted-lines.25` (0.010×), `cal.large.formatted-lines.26` (0.009×), `cal.large.formatted-lines.27` (0.009×), `cal.large.formatted-lines.28` (0.011×), `cal.large.formatted-lines.29` (0.010×), `cal.large.formatted-lines.30` (0.009×), `cal.large.formatted-lines.31` (0.008×), `hold.large.formatted-lines.00` (0.023×), `hold.large.formatted-lines.01` (0.022×), `hold.large.formatted-lines.02` (0.021×), `hold.large.formatted-lines.03` (0.021×), `hold.large.formatted-lines.04` (0.025×), `hold.large.formatted-lines.05` (0.023×), `hold.large.formatted-lines.06` (0.021×), `hold.large.formatted-lines.07` (0.022×), `hold.large.formatted-lines.08` (0.024×), `hold.large.formatted-lines.09` (0.022×), `hold.large.formatted-lines.10` (0.021×), `hold.large.formatted-lines.11` (0.021×), `hold.large.formatted-lines.12` (0.025×), `hold.large.formatted-lines.13` (0.022×), `hold.large.formatted-lines.14` (0.021×), `hold.large.formatted-lines.15` (0.021×), `hold.large.formatted-lines.16` (0.024×), `hold.large.formatted-lines.17` (0.023×), `hold.large.formatted-lines.18` (0.022×), `hold.large.formatted-lines.19` (0.021×), `hold.large.formatted-lines.20` (0.024×), `hold.large.formatted-lines.21` (0.022×), `hold.large.formatted-lines.22` (0.022×), `hold.large.formatted-lines.23` (0.021×), `hold.large.formatted-lines.24` (0.024×), `hold.large.formatted-lines.25` (0.024×), `hold.large.formatted-lines.26` (0.024×), `hold.large.formatted-lines.27` (0.021×), `hold.large.formatted-lines.28` (0.025×), `hold.large.formatted-lines.29` (0.023×), `hold.large.formatted-lines.30` (0.021×), `hold.large.formatted-lines.31` (0.021×).
- **literal hit (64):** short calls make matcher setup and Python/native boundary cost visible. `cal.large.literal-hit.00` (0.040×), `cal.large.literal-hit.01` (0.042×), `cal.large.literal-hit.02` (0.049×), `cal.large.literal-hit.03` (0.060×), `cal.large.literal-hit.04` (0.038×), `cal.large.literal-hit.05` (0.041×), `cal.large.literal-hit.06` (0.043×), `cal.large.literal-hit.07` (0.057×), `cal.large.literal-hit.08` (0.038×), `cal.large.literal-hit.09` (0.039×), `cal.large.literal-hit.10` (0.047×), `cal.large.literal-hit.11` (0.059×), `cal.large.literal-hit.12` (0.039×), `cal.large.literal-hit.13` (0.042×), `cal.large.literal-hit.14` (0.051×), `cal.large.literal-hit.15` (0.059×), `cal.large.literal-hit.16` (0.043×), `cal.large.literal-hit.17` (0.041×), `cal.large.literal-hit.18` (0.046×), `cal.large.literal-hit.19` (0.052×), `cal.large.literal-hit.20` (0.039×), `cal.large.literal-hit.21` (0.041×), `cal.large.literal-hit.22` (0.048×), `cal.large.literal-hit.23` (0.060×), `cal.large.literal-hit.24` (0.042×), `cal.large.literal-hit.25` (0.041×), `cal.large.literal-hit.26` (0.046×), `cal.large.literal-hit.27` (0.051×), `cal.large.literal-hit.28` (0.039×), `cal.large.literal-hit.29` (0.042×), `cal.large.literal-hit.30` (0.051×), `cal.large.literal-hit.31` (0.057×), `hold.large.literal-hit.00` (0.042×), `hold.large.literal-hit.01` (0.043×), `hold.large.literal-hit.02` (0.049×), `hold.large.literal-hit.03` (0.065×), `hold.large.literal-hit.04` (0.041×), `hold.large.literal-hit.05` (0.041×), `hold.large.literal-hit.06` (0.046×), `hold.large.literal-hit.07` (0.058×), `hold.large.literal-hit.08` (0.038×), `hold.large.literal-hit.09` (0.042×), `hold.large.literal-hit.10` (0.047×), `hold.large.literal-hit.11` (0.061×), `hold.large.literal-hit.12` (0.038×), `hold.large.literal-hit.13` (0.041×), `hold.large.literal-hit.14` (0.046×), `hold.large.literal-hit.15` (0.057×), `hold.large.literal-hit.16` (0.040×), `hold.large.literal-hit.17` (0.041×), `hold.large.literal-hit.18` (0.048×), `hold.large.literal-hit.19` (0.060×), `hold.large.literal-hit.20` (0.039×), `hold.large.literal-hit.21` (0.041×), `hold.large.literal-hit.22` (0.046×), `hold.large.literal-hit.23` (0.057×), `hold.large.literal-hit.24` (0.039×), `hold.large.literal-hit.25` (0.042×), `hold.large.literal-hit.26` (0.049×), `hold.large.literal-hit.27` (0.061×), `hold.large.literal-hit.28` (0.039×), `hold.large.literal-hit.29` (0.040×), `hold.large.literal-hit.30` (0.046×), `hold.large.literal-hit.31` (0.056×).
- **literal miss (64):** an absent phrase requires scanning every possible start. `cal.large.literal-miss.00` (0.150×), `cal.large.literal-miss.01` (0.169×), `cal.large.literal-miss.02` (0.198×), `cal.large.literal-miss.03` (0.265×), `cal.large.literal-miss.04` (0.146×), `cal.large.literal-miss.05` (0.169×), `cal.large.literal-miss.06` (0.183×), `cal.large.literal-miss.07` (0.254×), `cal.large.literal-miss.08` (0.147×), `cal.large.literal-miss.09` (0.167×), `cal.large.literal-miss.10` (0.183×), `cal.large.literal-miss.11` (0.248×), `cal.large.literal-miss.12` (0.150×), `cal.large.literal-miss.13` (0.173×), `cal.large.literal-miss.14` (0.196×), `cal.large.literal-miss.15` (0.287×), `cal.large.literal-miss.16` (0.151×), `cal.large.literal-miss.17` (0.163×), `cal.large.literal-miss.18` (0.200×), `cal.large.literal-miss.19` (0.269×), `cal.large.literal-miss.20` (0.143×), `cal.large.literal-miss.21` (0.157×), `cal.large.literal-miss.22` (0.193×), `cal.large.literal-miss.23` (0.244×), `cal.large.literal-miss.24` (0.137×), `cal.large.literal-miss.25` (0.171×), `cal.large.literal-miss.26` (0.202×), `cal.large.literal-miss.27` (0.272×), `cal.large.literal-miss.28` (0.149×), `cal.large.literal-miss.29` (0.172×), `cal.large.literal-miss.30` (0.198×), `cal.large.literal-miss.31` (0.245×), `hold.large.literal-miss.00` (0.149×), `hold.large.literal-miss.01` (0.173×), `hold.large.literal-miss.02` (0.202×), `hold.large.literal-miss.03` (0.230×), `hold.large.literal-miss.04` (0.153×), `hold.large.literal-miss.05` (0.167×), `hold.large.literal-miss.06` (0.208×), `hold.large.literal-miss.07` (0.271×), `hold.large.literal-miss.08` (0.154×), `hold.large.literal-miss.09` (0.173×), `hold.large.literal-miss.10` (0.212×), `hold.large.literal-miss.11` (0.266×), `hold.large.literal-miss.12` (0.152×), `hold.large.literal-miss.13` (0.173×), `hold.large.literal-miss.14` (0.199×), `hold.large.literal-miss.15` (0.255×), `hold.large.literal-miss.16` (0.152×), `hold.large.literal-miss.17` (0.168×), `hold.large.literal-miss.18` (0.202×), `hold.large.literal-miss.19` (0.271×), `hold.large.literal-miss.20` (0.153×), `hold.large.literal-miss.21` (0.169×), `hold.large.literal-miss.22` (0.213×), `hold.large.literal-miss.23` (0.241×), `hold.large.literal-miss.24` (0.154×), `hold.large.literal-miss.25` (0.172×), `hold.large.literal-miss.26` (0.204×), `hold.large.literal-miss.27` (0.281×), `hold.large.literal-miss.28` (0.151×), `hold.large.literal-miss.29` (0.175×), `hold.large.literal-miss.30` (0.211×), `hold.large.literal-miss.31` (0.265×).
- **long ending (64):** long inputs amplify scanning and end-boundary work. `cal.large.long-ending.00` (0.047×), `cal.large.long-ending.01` (0.048×), `cal.large.long-ending.02` (0.048×), `cal.large.long-ending.03` (0.048×), `cal.large.long-ending.04` (0.059×), `cal.large.long-ending.05` (0.061×), `cal.large.long-ending.06` (0.063×), `cal.large.long-ending.07` (0.061×), `cal.large.long-ending.08` (0.095×), `cal.large.long-ending.09` (0.097×), `cal.large.long-ending.10` (0.097×), `cal.large.long-ending.11` (0.098×), `cal.large.long-ending.12` (0.188×), `cal.large.long-ending.13` (0.210×), `cal.large.long-ending.14` (0.211×), `cal.large.long-ending.15` (0.180×), `cal.large.long-ending.16` (0.048×), `cal.large.long-ending.17` (0.044×), `cal.large.long-ending.18` (0.047×), `cal.large.long-ending.19` (0.048×), `cal.large.long-ending.20` (0.058×), `cal.large.long-ending.21` (0.058×), `cal.large.long-ending.22` (0.066×), `cal.large.long-ending.23` (0.060×), `cal.large.long-ending.24` (0.101×), `cal.large.long-ending.25` (0.098×), `cal.large.long-ending.26` (0.103×), `cal.large.long-ending.27` (0.100×), `cal.large.long-ending.28` (0.181×), `cal.large.long-ending.29` (0.184×), `cal.large.long-ending.30` (0.180×), `cal.large.long-ending.31` (0.186×), `hold.large.long-ending.00` (0.049×), `hold.large.long-ending.01` (0.050×), `hold.large.long-ending.02` (0.049×), `hold.large.long-ending.03` (0.049×), `hold.large.long-ending.04` (0.063×), `hold.large.long-ending.05` (0.066×), `hold.large.long-ending.06` (0.064×), `hold.large.long-ending.07` (0.063×), `hold.large.long-ending.08` (0.105×), `hold.large.long-ending.09` (0.107×), `hold.large.long-ending.10` (0.103×), `hold.large.long-ending.11` (0.102×), `hold.large.long-ending.12` (0.204×), `hold.large.long-ending.13` (0.194×), `hold.large.long-ending.14` (0.198×), `hold.large.long-ending.15` (0.200×), `hold.large.long-ending.16` (0.049×), `hold.large.long-ending.17` (0.049×), `hold.large.long-ending.18` (0.050×), `hold.large.long-ending.19` (0.050×), `hold.large.long-ending.20` (0.063×), `hold.large.long-ending.21` (0.063×), `hold.large.long-ending.22` (0.068×), `hold.large.long-ending.23` (0.063×), `hold.large.long-ending.24` (0.104×), `hold.large.long-ending.25` (0.104×), `hold.large.long-ending.26` (0.102×), `hold.large.long-ending.27` (0.104×), `hold.large.long-ending.28` (0.202×), `hold.large.long-ending.29` (0.187×), `hold.large.long-ending.30` (0.185×), `hold.large.long-ending.31` (0.193×).
- **module replace (64):** module/cache lookup combines with template and collection work. `cal.large.module-replace.00` (0.032×), `cal.large.module-replace.01` (0.026×), `cal.large.module-replace.02` (0.023×), `cal.large.module-replace.03` (0.022×), `cal.large.module-replace.04` (0.033×), `cal.large.module-replace.05` (0.027×), `cal.large.module-replace.06` (0.024×), `cal.large.module-replace.07` (0.021×), `cal.large.module-replace.08` (0.034×), `cal.large.module-replace.09` (0.028×), `cal.large.module-replace.10` (0.024×), `cal.large.module-replace.11` (0.021×), `cal.large.module-replace.12` (0.034×), `cal.large.module-replace.13` (0.027×), `cal.large.module-replace.14` (0.023×), `cal.large.module-replace.15` (0.022×), `cal.large.module-replace.16` (0.034×), `cal.large.module-replace.17` (0.027×), `cal.large.module-replace.18` (0.023×), `cal.large.module-replace.19` (0.021×), `cal.large.module-replace.20` (0.034×), `cal.large.module-replace.21` (0.027×), `cal.large.module-replace.22` (0.023×), `cal.large.module-replace.23` (0.022×), `cal.large.module-replace.24` (0.034×), `cal.large.module-replace.25` (0.027×), `cal.large.module-replace.26` (0.022×), `cal.large.module-replace.27` (0.021×), `cal.large.module-replace.28` (0.033×), `cal.large.module-replace.29` (0.026×), `cal.large.module-replace.30` (0.024×), `cal.large.module-replace.31` (0.022×), `hold.large.module-replace.00` (0.035×), `hold.large.module-replace.01` (0.028×), `hold.large.module-replace.02` (0.024×), `hold.large.module-replace.03` (0.021×), `hold.large.module-replace.04` (0.034×), `hold.large.module-replace.05` (0.028×), `hold.large.module-replace.06` (0.025×), `hold.large.module-replace.07` (0.022×), `hold.large.module-replace.08` (0.033×), `hold.large.module-replace.09` (0.027×), `hold.large.module-replace.10` (0.023×), `hold.large.module-replace.11` (0.021×), `hold.large.module-replace.12` (0.033×), `hold.large.module-replace.13` (0.027×), `hold.large.module-replace.14` (0.023×), `hold.large.module-replace.15` (0.021×), `hold.large.module-replace.16` (0.034×), `hold.large.module-replace.17` (0.027×), `hold.large.module-replace.18` (0.024×), `hold.large.module-replace.19` (0.022×), `hold.large.module-replace.20` (0.034×), `hold.large.module-replace.21` (0.028×), `hold.large.module-replace.22` (0.024×), `hold.large.module-replace.23` (0.021×), `hold.large.module-replace.24` (0.033×), `hold.large.module-replace.25` (0.027×), `hold.large.module-replace.26` (0.025×), `hold.large.module-replace.27` (0.021×), `hold.large.module-replace.28` (0.033×), `hold.large.module-replace.29` (0.027×), `hold.large.module-replace.30` (0.023×), `hold.large.module-replace.31` (0.022×).
- **module search (64):** module lookup and cache handling dominate short searches. `cal.large.module-search.00` (0.024×), `cal.large.module-search.01` (0.024×), `cal.large.module-search.02` (0.024×), `cal.large.module-search.03` (0.026×), `cal.large.module-search.04` (0.024×), `cal.large.module-search.05` (0.025×), `cal.large.module-search.06` (0.025×), `cal.large.module-search.07` (0.026×), `cal.large.module-search.08` (0.024×), `cal.large.module-search.09` (0.024×), `cal.large.module-search.10` (0.025×), `cal.large.module-search.11` (0.026×), `cal.large.module-search.12` (0.024×), `cal.large.module-search.13` (0.024×), `cal.large.module-search.14` (0.025×), `cal.large.module-search.15` (0.027×), `cal.large.module-search.16` (0.024×), `cal.large.module-search.17` (0.024×), `cal.large.module-search.18` (0.025×), `cal.large.module-search.19` (0.026×), `cal.large.module-search.20` (0.024×), `cal.large.module-search.21` (0.025×), `cal.large.module-search.22` (0.025×), `cal.large.module-search.23` (0.026×), `cal.large.module-search.24` (0.024×), `cal.large.module-search.25` (0.025×), `cal.large.module-search.26` (0.025×), `cal.large.module-search.27` (0.026×), `cal.large.module-search.28` (0.024×), `cal.large.module-search.29` (0.024×), `cal.large.module-search.30` (0.025×), `cal.large.module-search.31` (0.026×), `hold.large.module-search.00` (0.074×), `hold.large.module-search.01` (0.073×), `hold.large.module-search.02` (0.075×), `hold.large.module-search.03` (0.078×), `hold.large.module-search.04` (0.072×), `hold.large.module-search.05` (0.076×), `hold.large.module-search.06` (0.075×), `hold.large.module-search.07` (0.081×), `hold.large.module-search.08` (0.074×), `hold.large.module-search.09` (0.073×), `hold.large.module-search.10` (0.074×), `hold.large.module-search.11` (0.077×), `hold.large.module-search.12` (0.076×), `hold.large.module-search.13` (0.076×), `hold.large.module-search.14` (0.075×), `hold.large.module-search.15` (0.080×), `hold.large.module-search.16` (0.072×), `hold.large.module-search.17` (0.073×), `hold.large.module-search.18` (0.073×), `hold.large.module-search.19` (0.085×), `hold.large.module-search.20` (0.071×), `hold.large.module-search.21` (0.074×), `hold.large.module-search.22` (0.075×), `hold.large.module-search.23` (0.079×), `hold.large.module-search.24` (0.073×), `hold.large.module-search.25` (0.076×), `hold.large.module-search.26` (0.076×), `hold.large.module-search.27` (0.079×), `hold.large.module-search.28` (0.074×), `hold.large.module-search.29` (0.072×), `hold.large.module-search.30` (0.075×), `hold.large.module-search.31` (0.078×).
- **nearby capture (64):** lookaround and capture construction add work to short searches. `cal.large.nearby-capture.00` (0.014×), `cal.large.nearby-capture.01` (0.012×), `cal.large.nearby-capture.02` (0.011×), `cal.large.nearby-capture.03` (0.010×), `cal.large.nearby-capture.04` (0.014×), `cal.large.nearby-capture.05` (0.012×), `cal.large.nearby-capture.06` (0.011×), `cal.large.nearby-capture.07` (0.010×), `cal.large.nearby-capture.08` (0.014×), `cal.large.nearby-capture.09` (0.012×), `cal.large.nearby-capture.10` (0.011×), `cal.large.nearby-capture.11` (0.011×), `cal.large.nearby-capture.12` (0.015×), `cal.large.nearby-capture.13` (0.013×), `cal.large.nearby-capture.14` (0.011×), `cal.large.nearby-capture.15` (0.010×), `cal.large.nearby-capture.16` (0.014×), `cal.large.nearby-capture.17` (0.012×), `cal.large.nearby-capture.18` (0.011×), `cal.large.nearby-capture.19` (0.010×), `cal.large.nearby-capture.20` (0.014×), `cal.large.nearby-capture.21` (0.013×), `cal.large.nearby-capture.22` (0.011×), `cal.large.nearby-capture.23` (0.010×), `cal.large.nearby-capture.24` (0.015×), `cal.large.nearby-capture.25` (0.012×), `cal.large.nearby-capture.26` (0.011×), `cal.large.nearby-capture.27` (0.010×), `cal.large.nearby-capture.28` (0.014×), `cal.large.nearby-capture.29` (0.013×), `cal.large.nearby-capture.30` (0.011×), `cal.large.nearby-capture.31` (0.010×), `hold.large.nearby-capture.00` (0.021×), `hold.large.nearby-capture.01` (0.025×), `hold.large.nearby-capture.02` (0.033×), `hold.large.nearby-capture.03` (0.045×), `hold.large.nearby-capture.04` (0.021×), `hold.large.nearby-capture.05` (0.026×), `hold.large.nearby-capture.06` (0.033×), `hold.large.nearby-capture.07` (0.046×), `hold.large.nearby-capture.08` (0.021×), `hold.large.nearby-capture.09` (0.026×), `hold.large.nearby-capture.10` (0.033×), `hold.large.nearby-capture.11` (0.045×), `hold.large.nearby-capture.12` (0.022×), `hold.large.nearby-capture.13` (0.025×), `hold.large.nearby-capture.14` (0.033×), `hold.large.nearby-capture.15` (0.045×), `hold.large.nearby-capture.16` (0.022×), `hold.large.nearby-capture.17` (0.027×), `hold.large.nearby-capture.18` (0.033×), `hold.large.nearby-capture.19` (0.048×), `hold.large.nearby-capture.20` (0.021×), `hold.large.nearby-capture.21` (0.027×), `hold.large.nearby-capture.22` (0.034×), `hold.large.nearby-capture.23` (0.046×), `hold.large.nearby-capture.24` (0.021×), `hold.large.nearby-capture.25` (0.026×), `hold.large.nearby-capture.26` (0.033×), `hold.large.nearby-capture.27` (0.045×), `hold.large.nearby-capture.28` (0.021×), `hold.large.nearby-capture.29` (0.025×), `hold.large.nearby-capture.30` (0.032×), `hold.large.nearby-capture.31` (0.044×).
- **prefix check (64):** very short prefix checks are dominated by call/setup cost. `cal.large.prefix-check.00` (0.029×), `cal.large.prefix-check.01` (0.028×), `cal.large.prefix-check.02` (0.029×), `cal.large.prefix-check.03` (0.063×), `cal.large.prefix-check.04` (0.026×), `cal.large.prefix-check.05` (0.027×), `cal.large.prefix-check.06` (0.028×), `cal.large.prefix-check.07` (0.062×), `cal.large.prefix-check.08` (0.027×), `cal.large.prefix-check.09` (0.028×), `cal.large.prefix-check.10` (0.028×), `cal.large.prefix-check.11` (0.061×), `cal.large.prefix-check.12` (0.026×), `cal.large.prefix-check.13` (0.029×), `cal.large.prefix-check.14` (0.029×), `cal.large.prefix-check.15` (0.065×), `cal.large.prefix-check.16` (0.028×), `cal.large.prefix-check.17` (0.029×), `cal.large.prefix-check.18` (0.030×), `cal.large.prefix-check.19` (0.066×), `cal.large.prefix-check.20` (0.027×), `cal.large.prefix-check.21` (0.028×), `cal.large.prefix-check.22` (0.027×), `cal.large.prefix-check.23` (0.067×), `cal.large.prefix-check.24` (0.026×), `cal.large.prefix-check.25` (0.026×), `cal.large.prefix-check.26` (0.028×), `cal.large.prefix-check.27` (0.062×), `cal.large.prefix-check.28` (0.025×), `cal.large.prefix-check.29` (0.026×), `cal.large.prefix-check.30` (0.026×), `cal.large.prefix-check.31` (0.064×), `hold.large.prefix-check.00` (0.028×), `hold.large.prefix-check.01` (0.028×), `hold.large.prefix-check.02` (0.030×), `hold.large.prefix-check.03` (0.063×), `hold.large.prefix-check.04` (0.026×), `hold.large.prefix-check.05` (0.027×), `hold.large.prefix-check.06` (0.028×), `hold.large.prefix-check.07` (0.062×), `hold.large.prefix-check.08` (0.027×), `hold.large.prefix-check.09` (0.027×), `hold.large.prefix-check.10` (0.028×), `hold.large.prefix-check.11` (0.062×), `hold.large.prefix-check.12` (0.026×), `hold.large.prefix-check.13` (0.027×), `hold.large.prefix-check.14` (0.028×), `hold.large.prefix-check.15` (0.063×), `hold.large.prefix-check.16` (0.026×), `hold.large.prefix-check.17` (0.027×), `hold.large.prefix-check.18` (0.028×), `hold.large.prefix-check.19` (0.065×), `hold.large.prefix-check.20` (0.026×), `hold.large.prefix-check.21` (0.027×), `hold.large.prefix-check.22` (0.027×), `hold.large.prefix-check.23` (0.066×), `hold.large.prefix-check.24` (0.027×), `hold.large.prefix-check.25` (0.030×), `hold.large.prefix-check.26` (0.028×), `hold.large.prefix-check.27` (0.063×), `hold.large.prefix-check.28` (0.025×), `hold.large.prefix-check.29` (0.026×), `hold.large.prefix-check.30` (0.027×), `hold.large.prefix-check.31` (0.063×).
- **references (64):** backreferences require capture restoration and comparison. `cal.large.references.00` (0.022×), `cal.large.references.01` (0.021×), `cal.large.references.02` (0.021×), `cal.large.references.03` (0.025×), `cal.large.references.04` (0.021×), `cal.large.references.05` (0.021×), `cal.large.references.06` (0.024×), `cal.large.references.07` (0.026×), `cal.large.references.08` (0.021×), `cal.large.references.09` (0.022×), `cal.large.references.10` (0.022×), `cal.large.references.11` (0.021×), `cal.large.references.12` (0.023×), `cal.large.references.13` (0.022×), `cal.large.references.14` (0.022×), `cal.large.references.15` (0.025×), `cal.large.references.16` (0.022×), `cal.large.references.17` (0.020×), `cal.large.references.18` (0.025×), `cal.large.references.19` (0.023×), `cal.large.references.20` (0.020×), `cal.large.references.21` (0.023×), `cal.large.references.22` (0.023×), `cal.large.references.23` (0.021×), `cal.large.references.24` (0.022×), `cal.large.references.25` (0.021×), `cal.large.references.26` (0.022×), `cal.large.references.27` (0.025×), `cal.large.references.28` (0.021×), `cal.large.references.29` (0.020×), `cal.large.references.30` (0.023×), `cal.large.references.31` (0.024×), `hold.large.references.00` (0.023×), `hold.large.references.01` (0.022×), `hold.large.references.02` (0.023×), `hold.large.references.03` (0.027×), `hold.large.references.04` (0.022×), `hold.large.references.05` (0.021×), `hold.large.references.06` (0.024×), `hold.large.references.07` (0.024×), `hold.large.references.08` (0.021×), `hold.large.references.09` (0.023×), `hold.large.references.10` (0.023×), `hold.large.references.11` (0.024×), `hold.large.references.12` (0.025×), `hold.large.references.13` (0.023×), `hold.large.references.14` (0.024×), `hold.large.references.15` (0.026×), `hold.large.references.16` (0.022×), `hold.large.references.17` (0.022×), `hold.large.references.18` (0.024×), `hold.large.references.19` (0.024×), `hold.large.references.20` (0.021×), `hold.large.references.21` (0.023×), `hold.large.references.22` (0.023×), `hold.large.references.23` (0.026×), `hold.large.references.24` (0.024×), `hold.large.references.25` (0.022×), `hold.large.references.26` (0.023×), `hold.large.references.27` (0.026×), `hold.large.references.28` (0.022×), `hold.large.references.29` (0.020×), `hold.large.references.30` (0.024×), `hold.large.references.31` (0.025×).
- **replace callback (64):** repeated Python callbacks dominate replacement. `cal.large.replace-callback.00` (0.078×), `cal.large.replace-callback.01` (0.079×), `cal.large.replace-callback.02` (0.077×), `cal.large.replace-callback.03` (0.074×), `cal.large.replace-callback.04` (0.087×), `cal.large.replace-callback.05` (0.078×), `cal.large.replace-callback.06` (0.073×), `cal.large.replace-callback.07` (0.075×), `cal.large.replace-callback.08` (0.081×), `cal.large.replace-callback.09` (0.071×), `cal.large.replace-callback.10` (0.075×), `cal.large.replace-callback.11` (0.078×), `cal.large.replace-callback.12` (0.076×), `cal.large.replace-callback.13` (0.075×), `cal.large.replace-callback.14` (0.081×), `cal.large.replace-callback.15` (0.075×), `cal.large.replace-callback.16` (0.085×), `cal.large.replace-callback.17` (0.081×), `cal.large.replace-callback.18` (0.073×), `cal.large.replace-callback.19` (0.076×), `cal.large.replace-callback.20` (0.083×), `cal.large.replace-callback.21` (0.072×), `cal.large.replace-callback.22` (0.076×), `cal.large.replace-callback.23` (0.075×), `cal.large.replace-callback.24` (0.076×), `cal.large.replace-callback.25` (0.078×), `cal.large.replace-callback.26` (0.080×), `cal.large.replace-callback.27` (0.073×), `cal.large.replace-callback.28` (0.086×), `cal.large.replace-callback.29` (0.080×), `cal.large.replace-callback.30` (0.074×), `cal.large.replace-callback.31` (0.085×), `hold.large.replace-callback.00` (0.079×), `hold.large.replace-callback.01` (0.078×), `hold.large.replace-callback.02` (0.079×), `hold.large.replace-callback.03` (0.076×), `hold.large.replace-callback.04` (0.083×), `hold.large.replace-callback.05` (0.077×), `hold.large.replace-callback.06` (0.075×), `hold.large.replace-callback.07` (0.079×), `hold.large.replace-callback.08` (0.085×), `hold.large.replace-callback.09` (0.069×), `hold.large.replace-callback.10` (0.080×), `hold.large.replace-callback.11` (0.075×), `hold.large.replace-callback.12` (0.077×), `hold.large.replace-callback.13` (0.079×), `hold.large.replace-callback.14` (0.084×), `hold.large.replace-callback.15` (0.073×), `hold.large.replace-callback.16` (0.086×), `hold.large.replace-callback.17` (0.081×), `hold.large.replace-callback.18` (0.073×), `hold.large.replace-callback.19` (0.077×), `hold.large.replace-callback.20` (0.086×), `hold.large.replace-callback.21` (0.070×), `hold.large.replace-callback.22` (0.077×), `hold.large.replace-callback.23` (0.077×), `hold.large.replace-callback.24` (0.078×), `hold.large.replace-callback.25` (0.081×), `hold.large.replace-callback.26` (0.079×), `hold.large.replace-callback.27` (0.075×), `hold.large.replace-callback.28` (0.085×), `hold.large.replace-callback.29` (0.080×), `hold.large.replace-callback.30` (0.072×), `hold.large.replace-callback.31` (0.077×).
- **replace groups (64):** capture/template expansion and joining dominate replacement. `cal.large.replace-groups.00` (0.024×), `cal.large.replace-groups.01` (0.022×), `cal.large.replace-groups.02` (0.021×), `cal.large.replace-groups.03` (0.021×), `cal.large.replace-groups.04` (0.023×), `cal.large.replace-groups.05` (0.020×), `cal.large.replace-groups.06` (0.020×), `cal.large.replace-groups.07` (0.020×), `cal.large.replace-groups.08` (0.023×), `cal.large.replace-groups.09` (0.021×), `cal.large.replace-groups.10` (0.023×), `cal.large.replace-groups.11` (0.022×), `cal.large.replace-groups.12` (0.025×), `cal.large.replace-groups.13` (0.021×), `cal.large.replace-groups.14` (0.020×), `cal.large.replace-groups.15` (0.024×), `cal.large.replace-groups.16` (0.024×), `cal.large.replace-groups.17` (0.023×), `cal.large.replace-groups.18` (0.021×), `cal.large.replace-groups.19` (0.020×), `cal.large.replace-groups.20` (0.022×), `cal.large.replace-groups.21` (0.022×), `cal.large.replace-groups.22` (0.021×), `cal.large.replace-groups.23` (0.020×), `cal.large.replace-groups.24` (0.023×), `cal.large.replace-groups.25` (0.020×), `cal.large.replace-groups.26` (0.020×), `cal.large.replace-groups.27` (0.020×), `cal.large.replace-groups.28` (0.023×), `cal.large.replace-groups.29` (0.021×), `cal.large.replace-groups.30` (0.023×), `cal.large.replace-groups.31` (0.020×), `hold.large.replace-groups.00` (0.024×), `hold.large.replace-groups.01` (0.022×), `hold.large.replace-groups.02` (0.020×), `hold.large.replace-groups.03` (0.020×), `hold.large.replace-groups.04` (0.023×), `hold.large.replace-groups.05` (0.020×), `hold.large.replace-groups.06` (0.021×), `hold.large.replace-groups.07` (0.021×), `hold.large.replace-groups.08` (0.024×), `hold.large.replace-groups.09` (0.021×), `hold.large.replace-groups.10` (0.021×), `hold.large.replace-groups.11` (0.020×), `hold.large.replace-groups.12` (0.025×), `hold.large.replace-groups.13` (0.021×), `hold.large.replace-groups.14` (0.020×), `hold.large.replace-groups.15` (0.022×), `hold.large.replace-groups.16` (0.024×), `hold.large.replace-groups.17` (0.021×), `hold.large.replace-groups.18` (0.020×), `hold.large.replace-groups.19` (0.019×), `hold.large.replace-groups.20` (0.023×), `hold.large.replace-groups.21` (0.022×), `hold.large.replace-groups.22` (0.020×), `hold.large.replace-groups.23` (0.019×), `hold.large.replace-groups.24` (0.024×), `hold.large.replace-groups.25` (0.021×), `hold.large.replace-groups.26` (0.020×), `hold.large.replace-groups.27` (0.019×), `hold.large.replace-groups.28` (0.023×), `hold.large.replace-groups.29` (0.022×), `hold.large.replace-groups.30` (0.021×), `hold.large.replace-groups.31` (0.019×).
- **request records (64):** many structured captures and alternatives amplify matching work. `cal.large.request-records.00` (0.022×), `cal.large.request-records.01` (0.018×), `cal.large.request-records.02` (0.016×), `cal.large.request-records.03` (0.016×), `cal.large.request-records.04` (0.022×), `cal.large.request-records.05` (0.018×), `cal.large.request-records.06` (0.016×), `cal.large.request-records.07` (0.016×), `cal.large.request-records.08` (0.021×), `cal.large.request-records.09` (0.018×), `cal.large.request-records.10` (0.017×), `cal.large.request-records.11` (0.015×), `cal.large.request-records.12` (0.021×), `cal.large.request-records.13` (0.019×), `cal.large.request-records.14` (0.016×), `cal.large.request-records.15` (0.016×), `cal.large.request-records.16` (0.021×), `cal.large.request-records.17` (0.019×), `cal.large.request-records.18` (0.016×), `cal.large.request-records.19` (0.016×), `cal.large.request-records.20` (0.021×), `cal.large.request-records.21` (0.019×), `cal.large.request-records.22` (0.016×), `cal.large.request-records.23` (0.016×), `cal.large.request-records.24` (0.021×), `cal.large.request-records.25` (0.019×), `cal.large.request-records.26` (0.018×), `cal.large.request-records.27` (0.016×), `cal.large.request-records.28` (0.021×), `cal.large.request-records.29` (0.019×), `cal.large.request-records.30` (0.017×), `cal.large.request-records.31` (0.016×), `hold.large.request-records.00` (0.021×), `hold.large.request-records.01` (0.018×), `hold.large.request-records.02` (0.016×), `hold.large.request-records.03` (0.016×), `hold.large.request-records.04` (0.020×), `hold.large.request-records.05` (0.019×), `hold.large.request-records.06` (0.016×), `hold.large.request-records.07` (0.016×), `hold.large.request-records.08` (0.021×), `hold.large.request-records.09` (0.018×), `hold.large.request-records.10` (0.016×), `hold.large.request-records.11` (0.015×), `hold.large.request-records.12` (0.021×), `hold.large.request-records.13` (0.018×), `hold.large.request-records.14` (0.016×), `hold.large.request-records.15` (0.016×), `hold.large.request-records.16` (0.021×), `hold.large.request-records.17` (0.018×), `hold.large.request-records.18` (0.016×), `hold.large.request-records.19` (0.016×), `hold.large.request-records.20` (0.020×), `hold.large.request-records.21` (0.018×), `hold.large.request-records.22` (0.016×), `hold.large.request-records.23` (0.015×), `hold.large.request-records.24` (0.021×), `hold.large.request-records.25` (0.019×), `hold.large.request-records.26` (0.016×), `hold.large.request-records.27` (0.015×), `hold.large.request-records.28` (0.020×), `hold.large.request-records.29` (0.017×), `hold.large.request-records.30` (0.015×), `hold.large.request-records.31` (0.015×).
- **scanner bytes (64):** byte scanning and result construction amplify native-boundary work. `cal.large.scanner-bytes.00` (0.019×), `cal.large.scanner-bytes.01` (0.018×), `cal.large.scanner-bytes.02` (0.017×), `cal.large.scanner-bytes.03` (0.016×), `cal.large.scanner-bytes.04` (0.019×), `cal.large.scanner-bytes.05` (0.017×), `cal.large.scanner-bytes.06` (0.017×), `cal.large.scanner-bytes.07` (0.016×), `cal.large.scanner-bytes.08` (0.018×), `cal.large.scanner-bytes.09` (0.017×), `cal.large.scanner-bytes.10` (0.016×), `cal.large.scanner-bytes.11` (0.017×), `cal.large.scanner-bytes.12` (0.018×), `cal.large.scanner-bytes.13` (0.017×), `cal.large.scanner-bytes.14` (0.016×), `cal.large.scanner-bytes.15` (0.016×), `cal.large.scanner-bytes.16` (0.019×), `cal.large.scanner-bytes.17` (0.017×), `cal.large.scanner-bytes.18` (0.017×), `cal.large.scanner-bytes.19` (0.016×), `cal.large.scanner-bytes.20` (0.019×), `cal.large.scanner-bytes.21` (0.018×), `cal.large.scanner-bytes.22` (0.016×), `cal.large.scanner-bytes.23` (0.016×), `cal.large.scanner-bytes.24` (0.018×), `cal.large.scanner-bytes.25` (0.017×), `cal.large.scanner-bytes.26` (0.016×), `cal.large.scanner-bytes.27` (0.016×), `cal.large.scanner-bytes.28` (0.018×), `cal.large.scanner-bytes.29` (0.018×), `cal.large.scanner-bytes.30` (0.017×), `cal.large.scanner-bytes.31` (0.017×), `hold.large.scanner-bytes.00` (0.020×), `hold.large.scanner-bytes.01` (0.018×), `hold.large.scanner-bytes.02` (0.017×), `hold.large.scanner-bytes.03` (0.017×), `hold.large.scanner-bytes.04` (0.019×), `hold.large.scanner-bytes.05` (0.017×), `hold.large.scanner-bytes.06` (0.016×), `hold.large.scanner-bytes.07` (0.017×), `hold.large.scanner-bytes.08` (0.019×), `hold.large.scanner-bytes.09` (0.018×), `hold.large.scanner-bytes.10` (0.017×), `hold.large.scanner-bytes.11` (0.017×), `hold.large.scanner-bytes.12` (0.019×), `hold.large.scanner-bytes.13` (0.018×), `hold.large.scanner-bytes.14` (0.017×), `hold.large.scanner-bytes.15` (0.017×), `hold.large.scanner-bytes.16` (0.019×), `hold.large.scanner-bytes.17` (0.018×), `hold.large.scanner-bytes.18` (0.017×), `hold.large.scanner-bytes.19` (0.017×), `hold.large.scanner-bytes.20` (0.020×), `hold.large.scanner-bytes.21` (0.018×), `hold.large.scanner-bytes.22` (0.017×), `hold.large.scanner-bytes.23` (0.017×), `hold.large.scanner-bytes.24` (0.019×), `hold.large.scanner-bytes.25` (0.018×), `hold.large.scanner-bytes.26` (0.017×), `hold.large.scanner-bytes.27` (0.017×), `hold.large.scanner-bytes.28` (0.020×), `hold.large.scanner-bytes.29` (0.018×), `hold.large.scanner-bytes.30` (0.017×), `hold.large.scanner-bytes.31` (0.017×).
- **scanner text (64):** incremental scanning creates many match results and boundary calls. `cal.large.scanner-text.00` (0.020×), `cal.large.scanner-text.01` (0.018×), `cal.large.scanner-text.02` (0.017×), `cal.large.scanner-text.03` (0.017×), `cal.large.scanner-text.04` (0.019×), `cal.large.scanner-text.05` (0.018×), `cal.large.scanner-text.06` (0.017×), `cal.large.scanner-text.07` (0.017×), `cal.large.scanner-text.08` (0.018×), `cal.large.scanner-text.09` (0.018×), `cal.large.scanner-text.10` (0.017×), `cal.large.scanner-text.11` (0.017×), `cal.large.scanner-text.12` (0.019×), `cal.large.scanner-text.13` (0.018×), `cal.large.scanner-text.14` (0.017×), `cal.large.scanner-text.15` (0.017×), `cal.large.scanner-text.16` (0.019×), `cal.large.scanner-text.17` (0.018×), `cal.large.scanner-text.18` (0.017×), `cal.large.scanner-text.19` (0.017×), `cal.large.scanner-text.20` (0.018×), `cal.large.scanner-text.21` (0.018×), `cal.large.scanner-text.22` (0.017×), `cal.large.scanner-text.23` (0.017×), `cal.large.scanner-text.24` (0.019×), `cal.large.scanner-text.25` (0.018×), `cal.large.scanner-text.26` (0.016×), `cal.large.scanner-text.27` (0.017×), `cal.large.scanner-text.28` (0.019×), `cal.large.scanner-text.29` (0.018×), `cal.large.scanner-text.30` (0.017×), `cal.large.scanner-text.31` (0.018×), `hold.large.scanner-text.00` (0.023×), `hold.large.scanner-text.01` (0.021×), `hold.large.scanner-text.02` (0.018×), `hold.large.scanner-text.03` (0.020×), `hold.large.scanner-text.04` (0.022×), `hold.large.scanner-text.05` (0.021×), `hold.large.scanner-text.06` (0.017×), `hold.large.scanner-text.07` (0.020×), `hold.large.scanner-text.08` (0.022×), `hold.large.scanner-text.09` (0.020×), `hold.large.scanner-text.10` (0.018×), `hold.large.scanner-text.11` (0.017×), `hold.large.scanner-text.12` (0.020×), `hold.large.scanner-text.13` (0.018×), `hold.large.scanner-text.14` (0.017×), `hold.large.scanner-text.15` (0.020×), `hold.large.scanner-text.16` (0.023×), `hold.large.scanner-text.17` (0.022×), `hold.large.scanner-text.18` (0.017×), `hold.large.scanner-text.19` (0.020×), `hold.large.scanner-text.20` (0.022×), `hold.large.scanner-text.21` (0.019×), `hold.large.scanner-text.22` (0.017×), `hold.large.scanner-text.23` (0.017×), `hold.large.scanner-text.24` (0.020×), `hold.large.scanner-text.25` (0.018×), `hold.large.scanner-text.26` (0.017×), `hold.large.scanner-text.27` (0.017×), `hold.large.scanner-text.28` (0.020×), `hold.large.scanner-text.29` (0.018×), `hold.large.scanner-text.30` (0.017×), `hold.large.scanner-text.31` (0.017×).
- **split keep (64):** splitting and retained separators amplify collection work. `cal.large.split-keep.00` (0.024×), `cal.large.split-keep.01` (0.021×), `cal.large.split-keep.02` (0.020×), `cal.large.split-keep.03` (0.020×), `cal.large.split-keep.04` (0.024×), `cal.large.split-keep.05` (0.021×), `cal.large.split-keep.06` (0.020×), `cal.large.split-keep.07` (0.019×), `cal.large.split-keep.08` (0.024×), `cal.large.split-keep.09` (0.021×), `cal.large.split-keep.10` (0.021×), `cal.large.split-keep.11` (0.019×), `cal.large.split-keep.12` (0.024×), `cal.large.split-keep.13` (0.021×), `cal.large.split-keep.14` (0.020×), `cal.large.split-keep.15` (0.019×), `cal.large.split-keep.16` (0.024×), `cal.large.split-keep.17` (0.021×), `cal.large.split-keep.18` (0.020×), `cal.large.split-keep.19` (0.019×), `cal.large.split-keep.20` (0.024×), `cal.large.split-keep.21` (0.022×), `cal.large.split-keep.22` (0.021×), `cal.large.split-keep.23` (0.020×), `cal.large.split-keep.24` (0.024×), `cal.large.split-keep.25` (0.021×), `cal.large.split-keep.26` (0.019×), `cal.large.split-keep.27` (0.018×), `cal.large.split-keep.28` (0.024×), `cal.large.split-keep.29` (0.022×), `cal.large.split-keep.30` (0.021×), `cal.large.split-keep.31` (0.020×), `hold.large.split-keep.00` (0.024×), `hold.large.split-keep.01` (0.022×), `hold.large.split-keep.02` (0.022×), `hold.large.split-keep.03` (0.020×), `hold.large.split-keep.04` (0.024×), `hold.large.split-keep.05` (0.022×), `hold.large.split-keep.06` (0.020×), `hold.large.split-keep.07` (0.020×), `hold.large.split-keep.08` (0.024×), `hold.large.split-keep.09` (0.022×), `hold.large.split-keep.10` (0.020×), `hold.large.split-keep.11` (0.021×), `hold.large.split-keep.12` (0.024×), `hold.large.split-keep.13` (0.022×), `hold.large.split-keep.14` (0.020×), `hold.large.split-keep.15` (0.021×), `hold.large.split-keep.16` (0.025×), `hold.large.split-keep.17` (0.021×), `hold.large.split-keep.18` (0.020×), `hold.large.split-keep.19` (0.019×), `hold.large.split-keep.20` (0.025×), `hold.large.split-keep.21` (0.022×), `hold.large.split-keep.22` (0.020×), `hold.large.split-keep.23` (0.019×), `hold.large.split-keep.24` (0.024×), `hold.large.split-keep.25` (0.022×), `hold.large.split-keep.26` (0.020×), `hold.large.split-keep.27` (0.020×), `hold.large.split-keep.28` (0.024×), `hold.large.split-keep.29` (0.022×), `hold.large.split-keep.30` (0.021×), `hold.large.split-keep.31` (0.020×).
- **structured text (64):** configuration, paths, and quotes combine line starts, repeats, and captures. `cal.large.structured-text.00` (0.014×), `cal.large.structured-text.01` (0.011×), `cal.large.structured-text.02` (0.007×), `cal.large.structured-text.03` (0.012×), `cal.large.structured-text.04` (0.011×), `cal.large.structured-text.05` (0.008×), `cal.large.structured-text.06` (0.013×), `cal.large.structured-text.07` (0.010×), `cal.large.structured-text.08` (0.009×), `cal.large.structured-text.09` (0.013×), `cal.large.structured-text.10` (0.011×), `cal.large.structured-text.11` (0.005×), `cal.large.structured-text.12` (0.014×), `cal.large.structured-text.13` (0.011×), `cal.large.structured-text.14` (0.006×), `cal.large.structured-text.15` (0.012×), `cal.large.structured-text.16` (0.011×), `cal.large.structured-text.17` (0.008×), `cal.large.structured-text.18` (0.011×), `cal.large.structured-text.19` (0.010×), `cal.large.structured-text.20` (0.009×), `cal.large.structured-text.21` (0.013×), `cal.large.structured-text.22` (0.010×), `cal.large.structured-text.23` (0.005×), `cal.large.structured-text.24` (0.014×), `cal.large.structured-text.25` (0.011×), `cal.large.structured-text.26` (0.006×), `cal.large.structured-text.27` (0.012×), `cal.large.structured-text.28` (0.012×), `cal.large.structured-text.29` (0.007×), `cal.large.structured-text.30` (0.012×), `cal.large.structured-text.31` (0.010×), `hold.large.structured-text.00` (0.014×), `hold.large.structured-text.01` (0.011×), `hold.large.structured-text.02` (0.006×), `hold.large.structured-text.03` (0.012×), `hold.large.structured-text.04` (0.011×), `hold.large.structured-text.05` (0.008×), `hold.large.structured-text.06` (0.013×), `hold.large.structured-text.07` (0.011×), `hold.large.structured-text.08` (0.009×), `hold.large.structured-text.09` (0.013×), `hold.large.structured-text.10` (0.011×), `hold.large.structured-text.11` (0.005×), `hold.large.structured-text.12` (0.014×), `hold.large.structured-text.13` (0.011×), `hold.large.structured-text.14` (0.006×), `hold.large.structured-text.15` (0.012×), `hold.large.structured-text.16` (0.011×), `hold.large.structured-text.17` (0.008×), `hold.large.structured-text.18` (0.012×), `hold.large.structured-text.19` (0.010×), `hold.large.structured-text.20` (0.009×), `hold.large.structured-text.21` (0.013×), `hold.large.structured-text.22` (0.011×), `hold.large.structured-text.23` (0.005×), `hold.large.structured-text.24` (0.014×), `hold.large.structured-text.25` (0.011×), `hold.large.structured-text.26` (0.006×), `hold.large.structured-text.27` (0.012×), `hold.large.structured-text.28` (0.012×), `hold.large.structured-text.29` (0.008×), `hold.large.structured-text.30` (0.012×), `hold.large.structured-text.31` (0.010×).
- **unicode casefold (64):** full Unicode case handling requires extra character checks. `cal.large.unicode-casefold.00` (0.029×), `cal.large.unicode-casefold.01` (0.030×), `cal.large.unicode-casefold.02` (0.032×), `cal.large.unicode-casefold.03` (0.032×), `cal.large.unicode-casefold.04` (0.029×), `cal.large.unicode-casefold.05` (0.031×), `cal.large.unicode-casefold.06` (0.032×), `cal.large.unicode-casefold.07` (0.033×), `cal.large.unicode-casefold.08` (0.029×), `cal.large.unicode-casefold.09` (0.030×), `cal.large.unicode-casefold.10` (0.032×), `cal.large.unicode-casefold.11` (0.033×), `cal.large.unicode-casefold.12` (0.029×), `cal.large.unicode-casefold.13` (0.031×), `cal.large.unicode-casefold.14` (0.031×), `cal.large.unicode-casefold.15` (0.032×), `cal.large.unicode-casefold.16` (0.029×), `cal.large.unicode-casefold.17` (0.028×), `cal.large.unicode-casefold.18` (0.032×), `cal.large.unicode-casefold.19` (0.031×), `cal.large.unicode-casefold.20` (0.029×), `cal.large.unicode-casefold.21` (0.029×), `cal.large.unicode-casefold.22` (0.033×), `cal.large.unicode-casefold.23` (0.033×), `cal.large.unicode-casefold.24` (0.029×), `cal.large.unicode-casefold.25` (0.030×), `cal.large.unicode-casefold.26` (0.031×), `cal.large.unicode-casefold.27` (0.033×), `cal.large.unicode-casefold.28` (0.028×), `cal.large.unicode-casefold.29` (0.032×), `cal.large.unicode-casefold.30` (0.033×), `cal.large.unicode-casefold.31` (0.033×), `hold.large.unicode-casefold.00` (0.030×), `hold.large.unicode-casefold.01` (0.031×), `hold.large.unicode-casefold.02` (0.030×), `hold.large.unicode-casefold.03` (0.033×), `hold.large.unicode-casefold.04` (0.030×), `hold.large.unicode-casefold.05` (0.032×), `hold.large.unicode-casefold.06` (0.029×), `hold.large.unicode-casefold.07` (0.034×), `hold.large.unicode-casefold.08` (0.028×), `hold.large.unicode-casefold.09` (0.030×), `hold.large.unicode-casefold.10` (0.029×), `hold.large.unicode-casefold.11` (0.032×), `hold.large.unicode-casefold.12` (0.029×), `hold.large.unicode-casefold.13` (0.030×), `hold.large.unicode-casefold.14` (0.030×), `hold.large.unicode-casefold.15` (0.033×), `hold.large.unicode-casefold.16` (0.029×), `hold.large.unicode-casefold.17` (0.030×), `hold.large.unicode-casefold.18` (0.031×), `hold.large.unicode-casefold.19` (0.033×), `hold.large.unicode-casefold.20` (0.031×), `hold.large.unicode-casefold.21` (0.030×), `hold.large.unicode-casefold.22` (0.030×), `hold.large.unicode-casefold.23` (0.032×), `hold.large.unicode-casefold.24` (0.029×), `hold.large.unicode-casefold.25` (0.030×), `hold.large.unicode-casefold.26` (0.030×), `hold.large.unicode-casefold.27` (0.032×), `hold.large.unicode-casefold.28` (0.029×), `hold.large.unicode-casefold.29` (0.031×), `hold.large.unicode-casefold.30` (0.030×), `hold.large.unicode-casefold.31` (0.032×).
- **unicode words (64):** Unicode category and boundary checks are more expensive than ASCII scans. `cal.large.unicode-words.00` (0.022×), `cal.large.unicode-words.01` (0.022×), `cal.large.unicode-words.02` (0.023×), `cal.large.unicode-words.03` (0.023×), `cal.large.unicode-words.04` (0.022×), `cal.large.unicode-words.05` (0.023×), `cal.large.unicode-words.06` (0.022×), `cal.large.unicode-words.07` (0.021×), `cal.large.unicode-words.08` (0.020×), `cal.large.unicode-words.09` (0.021×), `cal.large.unicode-words.10` (0.021×), `cal.large.unicode-words.11` (0.021×), `cal.large.unicode-words.12` (0.021×), `cal.large.unicode-words.13` (0.020×), `cal.large.unicode-words.14` (0.021×), `cal.large.unicode-words.15` (0.021×), `cal.large.unicode-words.16` (0.020×), `cal.large.unicode-words.17` (0.021×), `cal.large.unicode-words.18` (0.021×), `cal.large.unicode-words.19` (0.023×), `cal.large.unicode-words.20` (0.022×), `cal.large.unicode-words.21` (0.022×), `cal.large.unicode-words.22` (0.022×), `cal.large.unicode-words.23` (0.023×), `cal.large.unicode-words.24` (0.021×), `cal.large.unicode-words.25` (0.022×), `cal.large.unicode-words.26` (0.022×), `cal.large.unicode-words.27` (0.023×), `cal.large.unicode-words.28` (0.022×), `cal.large.unicode-words.29` (0.022×), `cal.large.unicode-words.30` (0.023×), `cal.large.unicode-words.31` (0.023×), `hold.large.unicode-words.00` (0.022×), `hold.large.unicode-words.01` (0.022×), `hold.large.unicode-words.02` (0.023×), `hold.large.unicode-words.03` (0.022×), `hold.large.unicode-words.04` (0.023×), `hold.large.unicode-words.05` (0.022×), `hold.large.unicode-words.06` (0.022×), `hold.large.unicode-words.07` (0.022×), `hold.large.unicode-words.08` (0.021×), `hold.large.unicode-words.09` (0.022×), `hold.large.unicode-words.10` (0.021×), `hold.large.unicode-words.11` (0.022×), `hold.large.unicode-words.12` (0.022×), `hold.large.unicode-words.13` (0.022×), `hold.large.unicode-words.14` (0.022×), `hold.large.unicode-words.15` (0.023×), `hold.large.unicode-words.16` (0.025×), `hold.large.unicode-words.17` (0.022×), `hold.large.unicode-words.18` (0.024×), `hold.large.unicode-words.19` (0.023×), `hold.large.unicode-words.20` (0.021×), `hold.large.unicode-words.21` (0.024×), `hold.large.unicode-words.22` (0.022×), `hold.large.unicode-words.23` (0.023×), `hold.large.unicode-words.24` (0.022×), `hold.large.unicode-words.25` (0.023×), `hold.large.unicode-words.26` (0.022×), `hold.large.unicode-words.27` (0.023×), `hold.large.unicode-words.28` (0.022×), `hold.large.unicode-words.29` (0.023×), `hold.large.unicode-words.30` (0.022×), `hold.large.unicode-words.31` (0.023×).
- **verbose dotall (64):** verbose parsing or multi-line lazy matching adds compile/matcher work. `cal.large.verbose-dotall.00` (0.015×), `cal.large.verbose-dotall.01` (0.007×), `cal.large.verbose-dotall.02` (0.013×), `cal.large.verbose-dotall.03` (0.009×), `cal.large.verbose-dotall.04` (0.017×), `cal.large.verbose-dotall.05` (0.008×), `cal.large.verbose-dotall.06` (0.013×), `cal.large.verbose-dotall.07` (0.008×), `cal.large.verbose-dotall.08` (0.016×), `cal.large.verbose-dotall.09` (0.008×), `cal.large.verbose-dotall.10` (0.013×), `cal.large.verbose-dotall.11` (0.008×), `cal.large.verbose-dotall.12` (0.015×), `cal.large.verbose-dotall.13` (0.007×), `cal.large.verbose-dotall.14` (0.013×), `cal.large.verbose-dotall.15` (0.008×), `cal.large.verbose-dotall.16` (0.016×), `cal.large.verbose-dotall.17` (0.008×), `cal.large.verbose-dotall.18` (0.013×), `cal.large.verbose-dotall.19` (0.008×), `cal.large.verbose-dotall.20` (0.016×), `cal.large.verbose-dotall.21` (0.008×), `cal.large.verbose-dotall.22` (0.013×), `cal.large.verbose-dotall.23` (0.008×), `cal.large.verbose-dotall.24` (0.015×), `cal.large.verbose-dotall.25` (0.007×), `cal.large.verbose-dotall.26` (0.014×), `cal.large.verbose-dotall.27` (0.008×), `cal.large.verbose-dotall.28` (0.015×), `cal.large.verbose-dotall.29` (0.007×), `cal.large.verbose-dotall.30` (0.013×), `cal.large.verbose-dotall.31` (0.008×), `hold.large.verbose-dotall.00` (0.016×), `hold.large.verbose-dotall.01` (0.007×), `hold.large.verbose-dotall.02` (0.014×), `hold.large.verbose-dotall.03` (0.008×), `hold.large.verbose-dotall.04` (0.015×), `hold.large.verbose-dotall.05` (0.008×), `hold.large.verbose-dotall.06` (0.013×), `hold.large.verbose-dotall.07` (0.008×), `hold.large.verbose-dotall.08` (0.016×), `hold.large.verbose-dotall.09` (0.008×), `hold.large.verbose-dotall.10` (0.013×), `hold.large.verbose-dotall.11` (0.009×), `hold.large.verbose-dotall.12` (0.015×), `hold.large.verbose-dotall.13` (0.008×), `hold.large.verbose-dotall.14` (0.013×), `hold.large.verbose-dotall.15` (0.009×), `hold.large.verbose-dotall.16` (0.016×), `hold.large.verbose-dotall.17` (0.008×), `hold.large.verbose-dotall.18` (0.013×), `hold.large.verbose-dotall.19` (0.008×), `hold.large.verbose-dotall.20` (0.016×), `hold.large.verbose-dotall.21` (0.007×), `hold.large.verbose-dotall.22` (0.013×), `hold.large.verbose-dotall.23` (0.008×), `hold.large.verbose-dotall.24` (0.015×), `hold.large.verbose-dotall.25` (0.008×), `hold.large.verbose-dotall.26` (0.013×), `hold.large.verbose-dotall.27` (0.008×), `hold.large.verbose-dotall.28` (0.016×), `hold.large.verbose-dotall.29` (0.008×), `hold.large.verbose-dotall.30` (0.013×), `hold.large.verbose-dotall.31` (0.008×).
- **whole check (64):** structured repeats and full-string checks require more matcher state. `cal.large.whole-check.00` (0.020×), `cal.large.whole-check.01` (0.015×), `cal.large.whole-check.02` (0.013×), `cal.large.whole-check.03` (0.013×), `cal.large.whole-check.04` (0.020×), `cal.large.whole-check.05` (0.015×), `cal.large.whole-check.06` (0.014×), `cal.large.whole-check.07` (0.012×), `cal.large.whole-check.08` (0.020×), `cal.large.whole-check.09` (0.014×), `cal.large.whole-check.10` (0.013×), `cal.large.whole-check.11` (0.013×), `cal.large.whole-check.12` (0.020×), `cal.large.whole-check.13` (0.014×), `cal.large.whole-check.14` (0.012×), `cal.large.whole-check.15` (0.012×), `cal.large.whole-check.16` (0.020×), `cal.large.whole-check.17` (0.014×), `cal.large.whole-check.18` (0.013×), `cal.large.whole-check.19` (0.014×), `cal.large.whole-check.20` (0.016×), `cal.large.whole-check.21` (0.015×), `cal.large.whole-check.22` (0.012×), `cal.large.whole-check.23` (0.013×), `cal.large.whole-check.24` (0.020×), `cal.large.whole-check.25` (0.015×), `cal.large.whole-check.26` (0.013×), `cal.large.whole-check.27` (0.013×), `cal.large.whole-check.28` (0.019×), `cal.large.whole-check.29` (0.015×), `cal.large.whole-check.30` (0.013×), `cal.large.whole-check.31` (0.012×), `hold.large.whole-check.00` (0.020×), `hold.large.whole-check.01` (0.015×), `hold.large.whole-check.02` (0.014×), `hold.large.whole-check.03` (0.012×), `hold.large.whole-check.04` (0.019×), `hold.large.whole-check.05` (0.014×), `hold.large.whole-check.06` (0.014×), `hold.large.whole-check.07` (0.012×), `hold.large.whole-check.08` (0.019×), `hold.large.whole-check.09` (0.014×), `hold.large.whole-check.10` (0.013×), `hold.large.whole-check.11` (0.012×), `hold.large.whole-check.12` (0.019×), `hold.large.whole-check.13` (0.014×), `hold.large.whole-check.14` (0.013×), `hold.large.whole-check.15` (0.012×), `hold.large.whole-check.16` (0.019×), `hold.large.whole-check.17` (0.015×), `hold.large.whole-check.18` (0.013×), `hold.large.whole-check.19` (0.012×), `hold.large.whole-check.20` (0.016×), `hold.large.whole-check.21` (0.015×), `hold.large.whole-check.22` (0.013×), `hold.large.whole-check.23` (0.012×), `hold.large.whole-check.24` (0.020×), `hold.large.whole-check.25` (0.014×), `hold.large.whole-check.26` (0.013×), `hold.large.whole-check.27` (0.012×), `hold.large.whole-check.28` (0.019×), `hold.large.whole-check.29` (0.014×), `hold.large.whole-check.30` (0.014×), `hold.large.whole-check.31` (0.012×).
- **window collection (64):** window checks combine with repeated collection work. `cal.large.window-collection.00` (0.032×), `cal.large.window-collection.01` (0.021×), `cal.large.window-collection.02` (0.029×), `cal.large.window-collection.03` (0.022×), `cal.large.window-collection.04` (0.035×), `cal.large.window-collection.05` (0.022×), `cal.large.window-collection.06` (0.029×), `cal.large.window-collection.07` (0.022×), `cal.large.window-collection.08` (0.035×), `cal.large.window-collection.09` (0.022×), `cal.large.window-collection.10` (0.029×), `cal.large.window-collection.11` (0.022×), `cal.large.window-collection.12` (0.034×), `cal.large.window-collection.13` (0.022×), `cal.large.window-collection.14` (0.030×), `cal.large.window-collection.15` (0.023×), `cal.large.window-collection.16` (0.035×), `cal.large.window-collection.17` (0.020×), `cal.large.window-collection.18` (0.032×), `cal.large.window-collection.19` (0.023×), `cal.large.window-collection.20` (0.035×), `cal.large.window-collection.21` (0.022×), `cal.large.window-collection.22` (0.028×), `cal.large.window-collection.23` (0.021×), `cal.large.window-collection.24` (0.036×), `cal.large.window-collection.25` (0.022×), `cal.large.window-collection.26` (0.030×), `cal.large.window-collection.27` (0.022×), `cal.large.window-collection.28` (0.036×), `cal.large.window-collection.29` (0.021×), `cal.large.window-collection.30` (0.029×), `cal.large.window-collection.31` (0.022×), `hold.large.window-collection.00` (0.034×), `hold.large.window-collection.01` (0.023×), `hold.large.window-collection.02` (0.030×), `hold.large.window-collection.03` (0.021×), `hold.large.window-collection.04` (0.036×), `hold.large.window-collection.05` (0.022×), `hold.large.window-collection.06` (0.030×), `hold.large.window-collection.07` (0.022×), `hold.large.window-collection.08` (0.035×), `hold.large.window-collection.09` (0.022×), `hold.large.window-collection.10` (0.029×), `hold.large.window-collection.11` (0.022×), `hold.large.window-collection.12` (0.035×), `hold.large.window-collection.13` (0.022×), `hold.large.window-collection.14` (0.030×), `hold.large.window-collection.15` (0.022×), `hold.large.window-collection.16` (0.036×), `hold.large.window-collection.17` (0.022×), `hold.large.window-collection.18` (0.030×), `hold.large.window-collection.19` (0.022×), `hold.large.window-collection.20` (0.035×), `hold.large.window-collection.21` (0.022×), `hold.large.window-collection.22` (0.029×), `hold.large.window-collection.23` (0.022×), `hold.large.window-collection.24` (0.035×), `hold.large.window-collection.25` (0.023×), `hold.large.window-collection.26` (0.030×), `hold.large.window-collection.27` (0.022×), `hold.large.window-collection.28` (0.035×), `hold.large.window-collection.29` (0.022×), `hold.large.window-collection.30` (0.029×), `hold.large.window-collection.31` (0.022×).
- **window search (64):** short windowed searches expose position/boundary overhead. `cal.large.window-search.00` (0.026×), `cal.large.window-search.01` (0.026×), `cal.large.window-search.02` (0.027×), `cal.large.window-search.03` (0.028×), `cal.large.window-search.04` (0.025×), `cal.large.window-search.05` (0.025×), `cal.large.window-search.06` (0.026×), `cal.large.window-search.07` (0.027×), `cal.large.window-search.08` (0.024×), `cal.large.window-search.09` (0.025×), `cal.large.window-search.10` (0.026×), `cal.large.window-search.11` (0.028×), `cal.large.window-search.12` (0.026×), `cal.large.window-search.13` (0.025×), `cal.large.window-search.14` (0.026×), `cal.large.window-search.15` (0.028×), `cal.large.window-search.16` (0.026×), `cal.large.window-search.17` (0.025×), `cal.large.window-search.18` (0.027×), `cal.large.window-search.19` (0.028×), `cal.large.window-search.20` (0.025×), `cal.large.window-search.21` (0.026×), `cal.large.window-search.22` (0.026×), `cal.large.window-search.23` (0.029×), `cal.large.window-search.24` (0.025×), `cal.large.window-search.25` (0.026×), `cal.large.window-search.26` (0.026×), `cal.large.window-search.27` (0.029×), `cal.large.window-search.28` (0.024×), `cal.large.window-search.29` (0.024×), `cal.large.window-search.30` (0.025×), `cal.large.window-search.31` (0.026×), `hold.large.window-search.00` (0.040×), `hold.large.window-search.01` (0.041×), `hold.large.window-search.02` (0.040×), `hold.large.window-search.03` (0.042×), `hold.large.window-search.04` (0.038×), `hold.large.window-search.05` (0.039×), `hold.large.window-search.06` (0.040×), `hold.large.window-search.07` (0.042×), `hold.large.window-search.08` (0.038×), `hold.large.window-search.09` (0.039×), `hold.large.window-search.10` (0.040×), `hold.large.window-search.11` (0.042×), `hold.large.window-search.12` (0.038×), `hold.large.window-search.13` (0.040×), `hold.large.window-search.14` (0.042×), `hold.large.window-search.15` (0.041×), `hold.large.window-search.16` (0.038×), `hold.large.window-search.17` (0.041×), `hold.large.window-search.18` (0.040×), `hold.large.window-search.19` (0.052×), `hold.large.window-search.20` (0.038×), `hold.large.window-search.21` (0.043×), `hold.large.window-search.22` (0.039×), `hold.large.window-search.23` (0.042×), `hold.large.window-search.24` (0.038×), `hold.large.window-search.25` (0.040×), `hold.large.window-search.26` (0.042×), `hold.large.window-search.27` (0.042×), `hold.large.window-search.28` (0.036×), `hold.large.window-search.29` (0.037×), `hold.large.window-search.30` (0.038×), `hold.large.window-search.31` (0.038×).

### Rust engine — 2,248 large slowdowns

- **ascii mode (64):** word-boundary/category checks are repeated across the input. `cal.large.ascii-mode.00` (0.094×), `cal.large.ascii-mode.01` (0.079×), `cal.large.ascii-mode.02` (0.052×), `cal.large.ascii-mode.03` (0.035×), `cal.large.ascii-mode.04` (0.096×), `cal.large.ascii-mode.05` (0.073×), `cal.large.ascii-mode.06` (0.051×), `cal.large.ascii-mode.07` (0.032×), `cal.large.ascii-mode.08` (0.094×), `cal.large.ascii-mode.09` (0.073×), `cal.large.ascii-mode.10` (0.049×), `cal.large.ascii-mode.11` (0.032×), `cal.large.ascii-mode.12` (0.095×), `cal.large.ascii-mode.13` (0.073×), `cal.large.ascii-mode.14` (0.050×), `cal.large.ascii-mode.15` (0.033×), `cal.large.ascii-mode.16` (0.091×), `cal.large.ascii-mode.17` (0.073×), `cal.large.ascii-mode.18` (0.050×), `cal.large.ascii-mode.19` (0.032×), `cal.large.ascii-mode.20` (0.088×), `cal.large.ascii-mode.21` (0.072×), `cal.large.ascii-mode.22` (0.055×), `cal.large.ascii-mode.23` (0.033×), `cal.large.ascii-mode.24` (0.094×), `cal.large.ascii-mode.25` (0.075×), `cal.large.ascii-mode.26` (0.052×), `cal.large.ascii-mode.27` (0.031×), `cal.large.ascii-mode.28` (0.092×), `cal.large.ascii-mode.29` (0.078×), `cal.large.ascii-mode.30` (0.054×), `cal.large.ascii-mode.31` (0.031×), `hold.large.ascii-mode.00` (0.091×), `hold.large.ascii-mode.01` (0.072×), `hold.large.ascii-mode.02` (0.050×), `hold.large.ascii-mode.03` (0.032×), `hold.large.ascii-mode.04` (0.092×), `hold.large.ascii-mode.05` (0.072×), `hold.large.ascii-mode.06` (0.050×), `hold.large.ascii-mode.07` (0.032×), `hold.large.ascii-mode.08` (0.091×), `hold.large.ascii-mode.09` (0.073×), `hold.large.ascii-mode.10` (0.049×), `hold.large.ascii-mode.11` (0.031×), `hold.large.ascii-mode.12` (0.091×), `hold.large.ascii-mode.13` (0.071×), `hold.large.ascii-mode.14` (0.050×), `hold.large.ascii-mode.15` (0.031×), `hold.large.ascii-mode.16` (0.092×), `hold.large.ascii-mode.17` (0.069×), `hold.large.ascii-mode.18` (0.049×), `hold.large.ascii-mode.19` (0.032×), `hold.large.ascii-mode.20` (0.091×), `hold.large.ascii-mode.21` (0.070×), `hold.large.ascii-mode.22` (0.049×), `hold.large.ascii-mode.23` (0.032×), `hold.large.ascii-mode.24` (0.092×), `hold.large.ascii-mode.25` (0.072×), `hold.large.ascii-mode.26` (0.051×), `hold.large.ascii-mode.27` (0.032×), `hold.large.ascii-mode.28` (0.091×), `hold.large.ascii-mode.29` (0.070×), `hold.large.ascii-mode.30` (0.049×), `hold.large.ascii-mode.31` (0.033×).
- **branch control (64):** atomic/possessive and alternative paths require controlled backtracking. `cal.large.branch-control.00` (0.163×), `cal.large.branch-control.01` (0.184×), `cal.large.branch-control.02` (0.212×), `cal.large.branch-control.03` (0.235×), `cal.large.branch-control.04` (0.166×), `cal.large.branch-control.05` (0.183×), `cal.large.branch-control.06` (0.232×), `cal.large.branch-control.07` (0.235×), `cal.large.branch-control.08` (0.166×), `cal.large.branch-control.09` (0.185×), `cal.large.branch-control.10` (0.212×), `cal.large.branch-control.11` (0.244×), `cal.large.branch-control.12` (0.164×), `cal.large.branch-control.13` (0.185×), `cal.large.branch-control.14` (0.225×), `cal.large.branch-control.15` (0.232×), `cal.large.branch-control.16` (0.163×), `cal.large.branch-control.17` (0.184×), `cal.large.branch-control.18` (0.222×), `cal.large.branch-control.19` (0.236×), `cal.large.branch-control.20` (0.169×), `cal.large.branch-control.21` (0.187×), `cal.large.branch-control.22` (0.213×), `cal.large.branch-control.23` (0.233×), `cal.large.branch-control.24` (0.167×), `cal.large.branch-control.25` (0.185×), `cal.large.branch-control.26` (0.205×), `cal.large.branch-control.27` (0.229×), `cal.large.branch-control.28` (0.174×), `cal.large.branch-control.29` (0.185×), `cal.large.branch-control.30` (0.209×), `cal.large.branch-control.31` (0.238×), `hold.large.branch-control.00` (0.150×), `hold.large.branch-control.01` (0.158×), `hold.large.branch-control.02` (0.175×), `hold.large.branch-control.03` (0.175×), `hold.large.branch-control.04` (0.145×), `hold.large.branch-control.05` (0.168×), `hold.large.branch-control.06` (0.178×), `hold.large.branch-control.07` (0.175×), `hold.large.branch-control.08` (0.144×), `hold.large.branch-control.09` (0.156×), `hold.large.branch-control.10` (0.168×), `hold.large.branch-control.11` (0.178×), `hold.large.branch-control.12` (0.139×), `hold.large.branch-control.13` (0.156×), `hold.large.branch-control.14` (0.169×), `hold.large.branch-control.15` (0.177×), `hold.large.branch-control.16` (0.152×), `hold.large.branch-control.17` (0.157×), `hold.large.branch-control.18` (0.169×), `hold.large.branch-control.19` (0.179×), `hold.large.branch-control.20` (0.145×), `hold.large.branch-control.21` (0.157×), `hold.large.branch-control.22` (0.167×), `hold.large.branch-control.23` (0.178×), `hold.large.branch-control.24` (0.147×), `hold.large.branch-control.25` (0.157×), `hold.large.branch-control.26` (0.167×), `hold.large.branch-control.27` (0.176×), `hold.large.branch-control.28` (0.141×), `hold.large.branch-control.29` (0.157×), `hold.large.branch-control.30` (0.168×), `hold.large.branch-control.31` (0.174×).
- **bytes buffer (64):** mutable-buffer handling and match construction add boundary work. `cal.large.bytes-buffer.00` (0.172×), `cal.large.bytes-buffer.01` (0.168×), `cal.large.bytes-buffer.02` (0.157×), `cal.large.bytes-buffer.03` (0.153×), `cal.large.bytes-buffer.04` (0.178×), `cal.large.bytes-buffer.05` (0.167×), `cal.large.bytes-buffer.06` (0.160×), `cal.large.bytes-buffer.07` (0.152×), `cal.large.bytes-buffer.08` (0.172×), `cal.large.bytes-buffer.09` (0.166×), `cal.large.bytes-buffer.10` (0.157×), `cal.large.bytes-buffer.11` (0.153×), `cal.large.bytes-buffer.12` (0.177×), `cal.large.bytes-buffer.13` (0.166×), `cal.large.bytes-buffer.14` (0.160×), `cal.large.bytes-buffer.15` (0.154×), `cal.large.bytes-buffer.16` (0.172×), `cal.large.bytes-buffer.17` (0.167×), `cal.large.bytes-buffer.18` (0.155×), `cal.large.bytes-buffer.19` (0.156×), `cal.large.bytes-buffer.20` (0.173×), `cal.large.bytes-buffer.21` (0.168×), `cal.large.bytes-buffer.22` (0.162×), `cal.large.bytes-buffer.23` (0.153×), `cal.large.bytes-buffer.24` (0.174×), `cal.large.bytes-buffer.25` (0.165×), `cal.large.bytes-buffer.26` (0.157×), `cal.large.bytes-buffer.27` (0.152×), `cal.large.bytes-buffer.28` (0.170×), `cal.large.bytes-buffer.29` (0.165×), `cal.large.bytes-buffer.30` (0.154×), `cal.large.bytes-buffer.31` (0.157×), `hold.large.bytes-buffer.00` (0.207×), `hold.large.bytes-buffer.01` (0.194×), `hold.large.bytes-buffer.02` (0.172×), `hold.large.bytes-buffer.03` (0.175×), `hold.large.bytes-buffer.04` (0.186×), `hold.large.bytes-buffer.05` (0.185×), `hold.large.bytes-buffer.06` (0.164×), `hold.large.bytes-buffer.07` (0.179×), `hold.large.bytes-buffer.08` (0.186×), `hold.large.bytes-buffer.09` (0.185×), `hold.large.bytes-buffer.10` (0.169×), `hold.large.bytes-buffer.11` (0.175×), `hold.large.bytes-buffer.12` (0.184×), `hold.large.bytes-buffer.13` (0.181×), `hold.large.bytes-buffer.14` (0.163×), `hold.large.bytes-buffer.15` (0.170×), `hold.large.bytes-buffer.16` (0.181×), `hold.large.bytes-buffer.17` (0.188×), `hold.large.bytes-buffer.18` (0.174×), `hold.large.bytes-buffer.19` (0.178×), `hold.large.bytes-buffer.20` (0.196×), `hold.large.bytes-buffer.21` (0.188×), `hold.large.bytes-buffer.22` (0.170×), `hold.large.bytes-buffer.23` (0.182×), `hold.large.bytes-buffer.24` (0.186×), `hold.large.bytes-buffer.25` (0.184×), `hold.large.bytes-buffer.26` (0.173×), `hold.large.bytes-buffer.27` (0.173×), `hold.large.bytes-buffer.28` (0.183×), `hold.large.bytes-buffer.29` (0.179×), `hold.large.bytes-buffer.30` (0.168×), `hold.large.bytes-buffer.31` (0.170×).
- **bytes replace (64):** byte templates, captures, and joining amplify boundary work. `cal.large.bytes-replace.00` (0.086×), `cal.large.bytes-replace.01` (0.087×), `cal.large.bytes-replace.02` (0.089×), `cal.large.bytes-replace.03` (0.088×), `cal.large.bytes-replace.04` (0.085×), `cal.large.bytes-replace.05` (0.084×), `cal.large.bytes-replace.06` (0.092×), `cal.large.bytes-replace.07` (0.087×), `cal.large.bytes-replace.08` (0.088×), `cal.large.bytes-replace.09` (0.084×), `cal.large.bytes-replace.10` (0.071×), `cal.large.bytes-replace.11` (0.087×), `cal.large.bytes-replace.12` (0.085×), `cal.large.bytes-replace.13` (0.087×), `cal.large.bytes-replace.14` (0.084×), `cal.large.bytes-replace.15` (0.058×), `cal.large.bytes-replace.16` (0.083×), `cal.large.bytes-replace.17` (0.086×), `cal.large.bytes-replace.18` (0.086×), `cal.large.bytes-replace.19` (0.091×), `cal.large.bytes-replace.20` (0.089×), `cal.large.bytes-replace.21` (0.085×), `cal.large.bytes-replace.22` (0.086×), `cal.large.bytes-replace.23` (0.089×), `cal.large.bytes-replace.24` (0.087×), `cal.large.bytes-replace.25` (0.085×), `cal.large.bytes-replace.26` (0.084×), `cal.large.bytes-replace.27` (0.080×), `cal.large.bytes-replace.28` (0.081×), `cal.large.bytes-replace.29` (0.090×), `cal.large.bytes-replace.30` (0.070×), `cal.large.bytes-replace.31` (0.088×), `hold.large.bytes-replace.00` (0.085×), `hold.large.bytes-replace.01` (0.088×), `hold.large.bytes-replace.02` (0.087×), `hold.large.bytes-replace.03` (0.088×), `hold.large.bytes-replace.04` (0.085×), `hold.large.bytes-replace.05` (0.082×), `hold.large.bytes-replace.06` (0.087×), `hold.large.bytes-replace.07` (0.087×), `hold.large.bytes-replace.08` (0.087×), `hold.large.bytes-replace.09` (0.087×), `hold.large.bytes-replace.10` (0.074×), `hold.large.bytes-replace.11` (0.084×), `hold.large.bytes-replace.12` (0.085×), `hold.large.bytes-replace.13` (0.088×), `hold.large.bytes-replace.14` (0.088×), `hold.large.bytes-replace.15` (0.056×), `hold.large.bytes-replace.16` (0.083×), `hold.large.bytes-replace.17` (0.083×), `hold.large.bytes-replace.18` (0.087×), `hold.large.bytes-replace.19` (0.088×), `hold.large.bytes-replace.20` (0.084×), `hold.large.bytes-replace.21` (0.086×), `hold.large.bytes-replace.22` (0.086×), `hold.large.bytes-replace.23` (0.086×), `hold.large.bytes-replace.24` (0.087×), `hold.large.bytes-replace.25` (0.084×), `hold.large.bytes-replace.26` (0.086×), `hold.large.bytes-replace.27` (0.087×), `hold.large.bytes-replace.28` (0.088×), `hold.large.bytes-replace.29` (0.085×), `hold.large.bytes-replace.30` (0.070×), `hold.large.bytes-replace.31` (0.086×).
- **bytes tokens (64):** many byte results amplify collection and conversion work. `cal.large.bytes-tokens.00` (0.262×), `cal.large.bytes-tokens.01` (0.283×), `cal.large.bytes-tokens.02` (0.303×), `cal.large.bytes-tokens.03` (0.377×), `cal.large.bytes-tokens.04` (0.246×), `cal.large.bytes-tokens.05` (0.281×), `cal.large.bytes-tokens.06` (0.301×), `cal.large.bytes-tokens.07` (0.327×), `cal.large.bytes-tokens.08` (0.259×), `cal.large.bytes-tokens.09` (0.286×), `cal.large.bytes-tokens.10` (0.289×), `cal.large.bytes-tokens.11` (0.329×), `cal.large.bytes-tokens.12` (0.257×), `cal.large.bytes-tokens.13` (0.280×), `cal.large.bytes-tokens.14` (0.316×), `cal.large.bytes-tokens.15` (0.335×), `cal.large.bytes-tokens.16` (0.271×), `cal.large.bytes-tokens.17` (0.298×), `cal.large.bytes-tokens.18` (0.289×), `cal.large.bytes-tokens.19` (0.300×), `cal.large.bytes-tokens.20` (0.255×), `cal.large.bytes-tokens.21` (0.295×), `cal.large.bytes-tokens.22` (0.288×), `cal.large.bytes-tokens.23` (0.333×), `cal.large.bytes-tokens.24` (0.259×), `cal.large.bytes-tokens.25` (0.293×), `cal.large.bytes-tokens.26` (0.306×), `cal.large.bytes-tokens.27` (0.281×), `cal.large.bytes-tokens.28` (0.272×), `cal.large.bytes-tokens.29` (0.285×), `cal.large.bytes-tokens.30` (0.301×), `cal.large.bytes-tokens.31` (0.289×), `hold.large.bytes-tokens.00` (0.330×), `hold.large.bytes-tokens.01` (0.341×), `hold.large.bytes-tokens.02` (0.343×), `hold.large.bytes-tokens.03` (0.347×), `hold.large.bytes-tokens.04` (0.305×), `hold.large.bytes-tokens.05` (0.325×), `hold.large.bytes-tokens.06` (0.360×), `hold.large.bytes-tokens.07` (0.349×), `hold.large.bytes-tokens.08` (0.297×), `hold.large.bytes-tokens.09` (0.304×), `hold.large.bytes-tokens.10` (0.313×), `hold.large.bytes-tokens.11` (0.345×), `hold.large.bytes-tokens.12` (0.342×), `hold.large.bytes-tokens.13` (0.305×), `hold.large.bytes-tokens.14` (0.332×), `hold.large.bytes-tokens.15` (0.319×), `hold.large.bytes-tokens.16` (0.293×), `hold.large.bytes-tokens.17` (0.314×), `hold.large.bytes-tokens.18` (0.338×), `hold.large.bytes-tokens.19` (0.341×), `hold.large.bytes-tokens.20` (0.317×), `hold.large.bytes-tokens.21` (0.330×), `hold.large.bytes-tokens.22` (0.322×), `hold.large.bytes-tokens.23` (0.342×), `hold.large.bytes-tokens.24` (0.297×), `hold.large.bytes-tokens.25` (0.306×), `hold.large.bytes-tokens.26` (0.321×), `hold.large.bytes-tokens.27` (0.335×), `hold.large.bytes-tokens.28` (0.317×), `hold.large.bytes-tokens.29` (0.314×), `hold.large.bytes-tokens.30` (0.327×), `hold.large.bytes-tokens.31` (0.330×).
- **cleanup (64):** line cleanup and splitting amplify repeated scanning and collection. `cal.large.cleanup.00` (0.260×), `cal.large.cleanup.01` (0.257×), `cal.large.cleanup.02` (0.260×), `cal.large.cleanup.03` (0.319×), `cal.large.cleanup.04` (0.278×), `cal.large.cleanup.05` (0.250×), `cal.large.cleanup.06` (0.278×), `cal.large.cleanup.07` (0.322×), `cal.large.cleanup.08` (0.266×), `cal.large.cleanup.09` (0.262×), `cal.large.cleanup.10` (0.272×), `cal.large.cleanup.11` (0.323×), `cal.large.cleanup.12` (0.250×), `cal.large.cleanup.13` (0.257×), `cal.large.cleanup.14` (0.259×), `cal.large.cleanup.15` (0.311×), `cal.large.cleanup.16` (0.264×), `cal.large.cleanup.17` (0.253×), `cal.large.cleanup.18` (0.262×), `cal.large.cleanup.19` (0.284×), `cal.large.cleanup.20` (0.275×), `cal.large.cleanup.21` (0.255×), `cal.large.cleanup.22` (0.290×), `cal.large.cleanup.23` (0.317×), `cal.large.cleanup.24` (0.276×), `cal.large.cleanup.25` (0.263×), `cal.large.cleanup.26` (0.259×), `cal.large.cleanup.27` (0.328×), `cal.large.cleanup.28` (0.255×), `cal.large.cleanup.29` (0.260×), `cal.large.cleanup.30` (0.258×), `cal.large.cleanup.31` (0.322×), `hold.large.cleanup.00` (0.259×), `hold.large.cleanup.01` (0.253×), `hold.large.cleanup.02` (0.266×), `hold.large.cleanup.03` (0.308×), `hold.large.cleanup.04` (0.264×), `hold.large.cleanup.05` (0.255×), `hold.large.cleanup.06` (0.258×), `hold.large.cleanup.07` (0.325×), `hold.large.cleanup.08` (0.266×), `hold.large.cleanup.09` (0.251×), `hold.large.cleanup.10` (0.285×), `hold.large.cleanup.11` (0.312×), `hold.large.cleanup.12` (0.260×), `hold.large.cleanup.13` (0.253×), `hold.large.cleanup.14` (0.265×), `hold.large.cleanup.15` (0.316×), `hold.large.cleanup.16` (0.266×), `hold.large.cleanup.17` (0.267×), `hold.large.cleanup.18` (0.259×), `hold.large.cleanup.19` (0.307×), `hold.large.cleanup.20` (0.263×), `hold.large.cleanup.21` (0.283×), `hold.large.cleanup.22` (0.280×), `hold.large.cleanup.23` (0.322×), `hold.large.cleanup.24` (0.253×), `hold.large.cleanup.25` (0.255×), `hold.large.cleanup.26` (0.260×), `hold.large.cleanup.27` (0.308×), `hold.large.cleanup.28` (0.262×), `hold.large.cleanup.29` (0.258×), `hold.large.cleanup.30` (0.264×), `hold.large.cleanup.31` (0.306×).
- **conditionals (64):** conditionals depend on capture state and branch selection. `cal.large.conditionals.00` (0.144×), `cal.large.conditionals.01` (0.152×), `cal.large.conditionals.02` (0.162×), `cal.large.conditionals.03` (0.173×), `cal.large.conditionals.04` (0.150×), `cal.large.conditionals.05` (0.150×), `cal.large.conditionals.06` (0.152×), `cal.large.conditionals.07` (0.167×), `cal.large.conditionals.08` (0.161×), `cal.large.conditionals.09` (0.149×), `cal.large.conditionals.10` (0.167×), `cal.large.conditionals.11` (0.156×), `cal.large.conditionals.12` (0.152×), `cal.large.conditionals.13` (0.175×), `cal.large.conditionals.14` (0.170×), `cal.large.conditionals.15` (0.163×), `cal.large.conditionals.16` (0.155×), `cal.large.conditionals.17` (0.161×), `cal.large.conditionals.18` (0.153×), `cal.large.conditionals.19` (0.168×), `cal.large.conditionals.20` (0.139×), `cal.large.conditionals.21` (0.145×), `cal.large.conditionals.22` (0.159×), `cal.large.conditionals.23` (0.162×), `cal.large.conditionals.24` (0.150×), `cal.large.conditionals.25` (0.154×), `cal.large.conditionals.26` (0.158×), `cal.large.conditionals.27` (0.180×), `cal.large.conditionals.28` (0.175×), `cal.large.conditionals.29` (0.146×), `cal.large.conditionals.30` (0.155×), `cal.large.conditionals.31` (0.182×), `hold.large.conditionals.00` (0.174×), `hold.large.conditionals.01` (0.185×), `hold.large.conditionals.02` (0.176×), `hold.large.conditionals.03` (0.174×), `hold.large.conditionals.04` (0.171×), `hold.large.conditionals.05` (0.169×), `hold.large.conditionals.06` (0.178×), `hold.large.conditionals.07` (0.193×), `hold.large.conditionals.08` (0.169×), `hold.large.conditionals.09` (0.171×), `hold.large.conditionals.10` (0.178×), `hold.large.conditionals.11` (0.188×), `hold.large.conditionals.12` (0.168×), `hold.large.conditionals.13` (0.185×), `hold.large.conditionals.14` (0.176×), `hold.large.conditionals.15` (0.189×), `hold.large.conditionals.16` (0.187×), `hold.large.conditionals.17` (0.179×), `hold.large.conditionals.18` (0.176×), `hold.large.conditionals.19` (0.190×), `hold.large.conditionals.20` (0.167×), `hold.large.conditionals.21` (0.170×), `hold.large.conditionals.22` (0.185×), `hold.large.conditionals.23` (0.185×), `hold.large.conditionals.24` (0.175×), `hold.large.conditionals.25` (0.179×), `hold.large.conditionals.26` (0.164×), `hold.large.conditionals.27` (0.175×), `hold.large.conditionals.28` (0.159×), `hold.large.conditionals.29` (0.155×), `hold.large.conditionals.30` (0.170×), `hold.large.conditionals.31` (0.182×).
- **earlier 72 (136):** the earlier mixed workloads retain their documented scanning, Unicode, collection, and boundary costs. `cal.search.literal.hit` (0.145×), `cal.search.literal.miss` (0.162×), `cal.search.long-boundary` (0.315×), `cal.search.class-anchor` (0.201×), `cal.match.prefix` (0.181×), `cal.fullmatch.structured` (0.111×), `cal.search.look-capture` (0.166×), `cal.findall.tokens` (0.314×), `cal.finditer.groups` (0.165×), `cal.split.capture` (0.106×), `cal.sub.template` (0.084×), `cal.subn.callable` (0.202×), `cal.bytes.tokens` (0.208×), `cal.unicode.words` (0.114×), `cal.module.warm` (0.200×), `cal.empty.finditer` (0.192×), `cal.backref.fullmatch` (0.178×), `cal.conditional.match` (0.145×), `cal.atomic.search` (0.186×), `cal.byteslike.findall` (0.291×), `cal.unicode-name.search` (0.178×), `cal.ignorecase.findall` (0.403×), `cal.many.split` (0.127×), `cal.scanner.search` (0.120×), `cal.match.surface` (0.141×), `hold.search.literal.hit` (0.152×), `hold.search.literal.miss` (0.177×), `hold.search.long-boundary` (0.328×), `hold.search.class-anchor` (0.213×), `hold.match.prefix` (0.190×), `hold.fullmatch.structured` (0.126×), `hold.search.look-capture` (0.155×), `hold.findall.tokens` (0.167×), `hold.finditer.groups` (0.162×), `hold.split.capture` (0.104×), `hold.sub.template` (0.085×), `hold.subn.callable` (0.195×), `hold.bytes.tokens` (0.307×), `hold.unicode.words` (0.119×), `hold.module.warm` (0.317×), `hold.empty.finditer` (0.185×), `hold.backref.fullmatch` (0.175×), `hold.conditional.match` (0.158×), `hold.atomic.search` (0.207×), `hold.byteslike.findall` (0.315×), `hold.unicode-name.search` (0.187×), `hold.ignorecase.findall` (0.416×), `hold.many.split` (0.123×), `hold.scanner.search` (0.115×), `hold.match.surface` (0.141×), `cal.real.log` (0.168×), `cal.real.url` (0.062×), `cal.real.email` (0.140×), `cal.real.datetime` (0.151×), `cal.real.version` (0.223×), `cal.real.uuid` (0.213×), `cal.real.ip` (0.129×), `cal.real.path` (0.110×), `cal.real.config` (0.146×), `cal.real.comments` (0.188×), `cal.real.whitespace` (0.206×), `cal.real.lines` (0.222×), `cal.real.markup` (0.172×), `cal.real.quotes` (0.138×), `cal.real.csv` (0.104×), `cal.branch.prefix` (0.121×), `cal.branch.miss` (0.092×), `cal.repeat.nested` (0.095×), `cal.lines.records` (0.141×), `cal.block.dotall` (0.134×), `cal.pattern.verbose` (0.097×), `cal.mode.ascii` (0.099×), `cal.mode.casefold` (0.108×), `cal.mode.astral` (0.107×), `cal.look.negative-ahead` (0.187×), `cal.look.negative-behind` (0.328×), `cal.bytes.replace` (0.083×), `cal.bytes.scan` (0.102×), `cal.module.replace` (0.108×), `cal.zero.boundary` (0.174×), `cal.dense.iter` (0.171×), `cal.capture.optional` (0.192×), `cal.split.limited` (0.116×), `cal.replace.limited` (0.171×), `cal.bytes.view-long` (0.566×), `cal.window.search` (0.233×), `cal.window.findall` (0.373×), `cal.window.scanner` (0.146×), `cal.window.match` (0.211×), `cal.literal.replace` (0.262×), `cal.template.repeat` (0.082×), `cal.match.miss` (0.194×), `cal.fullmatch.miss` (0.290×), `hold.real.log` (0.170×), `hold.real.url` (0.052×), `hold.real.email` (0.130×), `hold.real.datetime` (0.243×), `hold.real.version` (0.128×), `hold.real.uuid` (0.198×), `hold.real.ip` (0.086×), `hold.real.path` (0.092×), `hold.real.config` (0.099×), `hold.real.comments` (0.204×), `hold.real.whitespace` (0.192×), `hold.real.lines` (0.207×), `hold.real.markup` (0.167×), `hold.real.quotes` (0.142×), `hold.real.csv` (0.095×), `hold.branch.prefix` (0.126×), `hold.branch.miss` (0.099×), `hold.repeat.nested` (0.090×), `hold.lines.records` (0.144×), `hold.block.dotall` (0.133×), `hold.pattern.verbose` (0.115×), `hold.mode.ascii` (0.093×), `hold.mode.casefold` (0.122×), `hold.mode.astral` (0.103×), `hold.look.negative-ahead` (0.199×), `hold.look.negative-behind` (0.339×), `hold.bytes.replace` (0.080×), `hold.bytes.scan` (0.101×), `hold.module.replace` (0.108×), `hold.zero.boundary` (0.170×), `hold.dense.iter` (0.173×), `hold.capture.optional` (0.182×), `hold.split.limited` (0.117×), `hold.replace.limited` (0.158×), `hold.bytes.view-long` (0.547×), `hold.window.search` (0.244×), `hold.window.findall` (0.326×), `hold.window.scanner` (0.145×), `hold.window.match` (0.204×), `hold.literal.replace` (0.261×), `hold.template.repeat` (0.080×), `hold.match.miss` (0.199×), `hold.fullmatch.miss` (0.277×).
- **empty iterator (64):** empty matches require careful progress and many result objects. `cal.large.empty-iterator.00` (0.163×), `cal.large.empty-iterator.01` (0.153×), `cal.large.empty-iterator.02` (0.149×), `cal.large.empty-iterator.03` (0.151×), `cal.large.empty-iterator.04` (0.163×), `cal.large.empty-iterator.05` (0.153×), `cal.large.empty-iterator.06` (0.153×), `cal.large.empty-iterator.07` (0.154×), `cal.large.empty-iterator.08` (0.175×), `cal.large.empty-iterator.09` (0.151×), `cal.large.empty-iterator.10` (0.156×), `cal.large.empty-iterator.11` (0.151×), `cal.large.empty-iterator.12` (0.172×), `cal.large.empty-iterator.13` (0.155×), `cal.large.empty-iterator.14` (0.149×), `cal.large.empty-iterator.15` (0.153×), `cal.large.empty-iterator.16` (0.160×), `cal.large.empty-iterator.17` (0.159×), `cal.large.empty-iterator.18` (0.154×), `cal.large.empty-iterator.19` (0.155×), `cal.large.empty-iterator.20` (0.177×), `cal.large.empty-iterator.21` (0.159×), `cal.large.empty-iterator.22` (0.157×), `cal.large.empty-iterator.23` (0.156×), `cal.large.empty-iterator.24` (0.173×), `cal.large.empty-iterator.25` (0.155×), `cal.large.empty-iterator.26` (0.159×), `cal.large.empty-iterator.27` (0.162×), `cal.large.empty-iterator.28` (0.177×), `cal.large.empty-iterator.29` (0.157×), `cal.large.empty-iterator.30` (0.152×), `cal.large.empty-iterator.31` (0.154×), `hold.large.empty-iterator.00` (0.199×), `hold.large.empty-iterator.01` (0.172×), `hold.large.empty-iterator.02` (0.163×), `hold.large.empty-iterator.03` (0.158×), `hold.large.empty-iterator.04` (0.195×), `hold.large.empty-iterator.05` (0.173×), `hold.large.empty-iterator.06` (0.162×), `hold.large.empty-iterator.07` (0.163×), `hold.large.empty-iterator.08` (0.189×), `hold.large.empty-iterator.09` (0.172×), `hold.large.empty-iterator.10` (0.156×), `hold.large.empty-iterator.11` (0.160×), `hold.large.empty-iterator.12` (0.189×), `hold.large.empty-iterator.13` (0.173×), `hold.large.empty-iterator.14` (0.165×), `hold.large.empty-iterator.15` (0.160×), `hold.large.empty-iterator.16` (0.187×), `hold.large.empty-iterator.17` (0.172×), `hold.large.empty-iterator.18` (0.165×), `hold.large.empty-iterator.19` (0.160×), `hold.large.empty-iterator.20` (0.189×), `hold.large.empty-iterator.21` (0.172×), `hold.large.empty-iterator.22` (0.162×), `hold.large.empty-iterator.23` (0.157×), `hold.large.empty-iterator.24` (0.192×), `hold.large.empty-iterator.25` (0.173×), `hold.large.empty-iterator.26` (0.162×), `hold.large.empty-iterator.27` (0.161×), `hold.large.empty-iterator.28` (0.190×), `hold.large.empty-iterator.29` (0.168×), `hold.large.empty-iterator.30` (0.170×), `hold.large.empty-iterator.31` (0.164×).
- **everyday address (64):** the email-like find-all cases return many matches and repeatedly check several character classes; native profiling confirms the compact matcher performs 26–230 class checks and 60–518 repeated-character checks per call. `cal.large.everyday-address.00` (0.050×), `cal.large.everyday-address.01` (0.115×), `cal.large.everyday-address.02` (0.219×), `cal.large.everyday-address.03` (0.060×), `cal.large.everyday-address.04` (0.113×), `cal.large.everyday-address.05` (0.209×), `cal.large.everyday-address.06` (0.053×), `cal.large.everyday-address.07` (0.120×), `cal.large.everyday-address.08` (0.195×), `cal.large.everyday-address.09` (0.052×), `cal.large.everyday-address.10` (0.116×), `cal.large.everyday-address.11` (0.238×), `cal.large.everyday-address.12` (0.050×), `cal.large.everyday-address.13` (0.117×), `cal.large.everyday-address.14` (0.219×), `cal.large.everyday-address.15` (0.060×), `cal.large.everyday-address.16` (0.111×), `cal.large.everyday-address.17` (0.217×), `cal.large.everyday-address.18` (0.055×), `cal.large.everyday-address.19` (0.125×), `cal.large.everyday-address.20` (0.208×), `cal.large.everyday-address.21` (0.052×), `cal.large.everyday-address.22` (0.116×), `cal.large.everyday-address.23` (0.222×), `cal.large.everyday-address.24` (0.048×), `cal.large.everyday-address.25` (0.112×), `cal.large.everyday-address.26` (0.215×), `cal.large.everyday-address.27` (0.060×), `cal.large.everyday-address.28` (0.107×), `cal.large.everyday-address.29` (0.218×), `cal.large.everyday-address.30` (0.055×), `cal.large.everyday-address.31` (0.121×), `hold.large.everyday-address.00` (0.050×), `hold.large.everyday-address.01` (0.114×), `hold.large.everyday-address.02` (0.221×), `hold.large.everyday-address.03` (0.066×), `hold.large.everyday-address.04` (0.113×), `hold.large.everyday-address.05` (0.209×), `hold.large.everyday-address.06` (0.054×), `hold.large.everyday-address.07` (0.112×), `hold.large.everyday-address.08` (0.202×), `hold.large.everyday-address.09` (0.053×), `hold.large.everyday-address.10` (0.117×), `hold.large.everyday-address.11` (0.229×), `hold.large.everyday-address.12` (0.053×), `hold.large.everyday-address.13` (0.117×), `hold.large.everyday-address.14` (0.210×), `hold.large.everyday-address.15` (0.062×), `hold.large.everyday-address.16` (0.113×), `hold.large.everyday-address.17` (0.210×), `hold.large.everyday-address.18` (0.056×), `hold.large.everyday-address.19` (0.118×), `hold.large.everyday-address.20` (0.208×), `hold.large.everyday-address.21` (0.055×), `hold.large.everyday-address.22` (0.122×), `hold.large.everyday-address.23` (0.228×), `hold.large.everyday-address.24` (0.049×), `hold.large.everyday-address.25` (0.114×), `hold.large.everyday-address.26` (0.215×), `hold.large.everyday-address.27` (0.057×), `hold.large.everyday-address.28` (0.112×), `hold.large.everyday-address.29` (0.209×), `hold.large.everyday-address.30` (0.058×), `hold.large.everyday-address.31` (0.117×).
- **findall tokens (64):** many returned tokens amplify scanning and result construction. `cal.large.findall-tokens.00` (0.204×), `cal.large.findall-tokens.01` (0.174×), `cal.large.findall-tokens.02` (0.175×), `cal.large.findall-tokens.03` (0.173×), `cal.large.findall-tokens.04` (0.145×), `cal.large.findall-tokens.05` (0.145×), `cal.large.findall-tokens.06` (0.153×), `cal.large.findall-tokens.07` (0.168×), `cal.large.findall-tokens.08` (0.152×), `cal.large.findall-tokens.09` (0.142×), `cal.large.findall-tokens.10` (0.209×), `cal.large.findall-tokens.11` (0.174×), `cal.large.findall-tokens.12` (0.152×), `cal.large.findall-tokens.13` (0.142×), `cal.large.findall-tokens.14` (0.155×), `cal.large.findall-tokens.15` (0.152×), `cal.large.findall-tokens.16` (0.146×), `cal.large.findall-tokens.17` (0.195×), `cal.large.findall-tokens.18` (0.183×), `cal.large.findall-tokens.19` (0.170×), `cal.large.findall-tokens.20` (0.154×), `cal.large.findall-tokens.21` (0.176×), `cal.large.findall-tokens.22` (0.158×), `cal.large.findall-tokens.23` (0.159×), `cal.large.findall-tokens.24` (0.191×), `cal.large.findall-tokens.25` (0.162×), `cal.large.findall-tokens.26` (0.173×), `cal.large.findall-tokens.27` (0.163×), `cal.large.findall-tokens.28` (0.132×), `cal.large.findall-tokens.29` (0.150×), `cal.large.findall-tokens.30` (0.145×), `cal.large.findall-tokens.31` (0.165×), `hold.large.findall-tokens.00` (0.177×), `hold.large.findall-tokens.01` (0.163×), `hold.large.findall-tokens.02` (0.173×), `hold.large.findall-tokens.03` (0.173×), `hold.large.findall-tokens.04` (0.158×), `hold.large.findall-tokens.05` (0.168×), `hold.large.findall-tokens.06` (0.176×), `hold.large.findall-tokens.07` (0.177×), `hold.large.findall-tokens.08` (0.158×), `hold.large.findall-tokens.09` (0.167×), `hold.large.findall-tokens.10` (0.152×), `hold.large.findall-tokens.11` (0.157×), `hold.large.findall-tokens.12` (0.161×), `hold.large.findall-tokens.13` (0.171×), `hold.large.findall-tokens.14` (0.149×), `hold.large.findall-tokens.15` (0.180×), `hold.large.findall-tokens.16` (0.160×), `hold.large.findall-tokens.17` (0.170×), `hold.large.findall-tokens.18` (0.174×), `hold.large.findall-tokens.19` (0.179×), `hold.large.findall-tokens.20` (0.168×), `hold.large.findall-tokens.21` (0.145×), `hold.large.findall-tokens.22` (0.176×), `hold.large.findall-tokens.23` (0.154×), `hold.large.findall-tokens.24` (0.158×), `hold.large.findall-tokens.25` (0.146×), `hold.large.findall-tokens.26` (0.155×), `hold.large.findall-tokens.27` (0.172×), `hold.large.findall-tokens.28` (0.150×), `hold.large.findall-tokens.29` (0.161×), `hold.large.findall-tokens.30` (0.165×), `hold.large.findall-tokens.31` (0.151×).
- **finditer pairs (64):** many captures amplify iterator and match-object construction. `cal.large.finditer-pairs.00` (0.182×), `cal.large.finditer-pairs.01` (0.156×), `cal.large.finditer-pairs.02` (0.142×), `cal.large.finditer-pairs.03` (0.135×), `cal.large.finditer-pairs.04` (0.175×), `cal.large.finditer-pairs.05` (0.159×), `cal.large.finditer-pairs.06` (0.143×), `cal.large.finditer-pairs.07` (0.137×), `cal.large.finditer-pairs.08` (0.177×), `cal.large.finditer-pairs.09` (0.157×), `cal.large.finditer-pairs.10` (0.140×), `cal.large.finditer-pairs.11` (0.139×), `cal.large.finditer-pairs.12` (0.186×), `cal.large.finditer-pairs.13` (0.154×), `cal.large.finditer-pairs.14` (0.146×), `cal.large.finditer-pairs.15` (0.139×), `cal.large.finditer-pairs.16` (0.179×), `cal.large.finditer-pairs.17` (0.159×), `cal.large.finditer-pairs.18` (0.146×), `cal.large.finditer-pairs.19` (0.154×), `cal.large.finditer-pairs.20` (0.184×), `cal.large.finditer-pairs.21` (0.141×), `cal.large.finditer-pairs.22` (0.153×), `cal.large.finditer-pairs.23` (0.140×), `cal.large.finditer-pairs.24` (0.177×), `cal.large.finditer-pairs.25` (0.160×), `cal.large.finditer-pairs.26` (0.137×), `cal.large.finditer-pairs.27` (0.136×), `cal.large.finditer-pairs.28` (0.174×), `cal.large.finditer-pairs.29` (0.151×), `cal.large.finditer-pairs.30` (0.136×), `cal.large.finditer-pairs.31` (0.134×), `hold.large.finditer-pairs.00` (0.186×), `hold.large.finditer-pairs.01` (0.153×), `hold.large.finditer-pairs.02` (0.140×), `hold.large.finditer-pairs.03` (0.133×), `hold.large.finditer-pairs.04` (0.177×), `hold.large.finditer-pairs.05` (0.152×), `hold.large.finditer-pairs.06` (0.137×), `hold.large.finditer-pairs.07` (0.135×), `hold.large.finditer-pairs.08` (0.173×), `hold.large.finditer-pairs.09` (0.153×), `hold.large.finditer-pairs.10` (0.142×), `hold.large.finditer-pairs.11` (0.128×), `hold.large.finditer-pairs.12` (0.171×), `hold.large.finditer-pairs.13` (0.151×), `hold.large.finditer-pairs.14` (0.139×), `hold.large.finditer-pairs.15` (0.132×), `hold.large.finditer-pairs.16` (0.177×), `hold.large.finditer-pairs.17` (0.149×), `hold.large.finditer-pairs.18` (0.146×), `hold.large.finditer-pairs.19` (0.133×), `hold.large.finditer-pairs.20` (0.172×), `hold.large.finditer-pairs.21` (0.152×), `hold.large.finditer-pairs.22` (0.142×), `hold.large.finditer-pairs.23` (0.140×), `hold.large.finditer-pairs.24` (0.178×), `hold.large.finditer-pairs.25` (0.157×), `hold.large.finditer-pairs.26` (0.138×), `hold.large.finditer-pairs.27` (0.137×), `hold.large.finditer-pairs.28` (0.173×), `hold.large.finditer-pairs.29` (0.156×), `hold.large.finditer-pairs.30` (0.137×), `hold.large.finditer-pairs.31` (0.138×).
- **formatted lines (64):** many line starts and character-class checks amplify per-match work. `cal.large.formatted-lines.00` (0.237×), `cal.large.formatted-lines.01` (0.190×), `cal.large.formatted-lines.02` (0.203×), `cal.large.formatted-lines.03` (0.216×), `cal.large.formatted-lines.04` (0.200×), `cal.large.formatted-lines.05` (0.199×), `cal.large.formatted-lines.06` (0.200×), `cal.large.formatted-lines.07` (0.205×), `cal.large.formatted-lines.08` (0.203×), `cal.large.formatted-lines.09` (0.202×), `cal.large.formatted-lines.10` (0.212×), `cal.large.formatted-lines.11` (0.202×), `cal.large.formatted-lines.12` (0.201×), `cal.large.formatted-lines.13` (0.192×), `cal.large.formatted-lines.14` (0.200×), `cal.large.formatted-lines.15` (0.199×), `cal.large.formatted-lines.16` (0.199×), `cal.large.formatted-lines.17` (0.197×), `cal.large.formatted-lines.18` (0.200×), `cal.large.formatted-lines.19` (0.200×), `cal.large.formatted-lines.20` (0.199×), `cal.large.formatted-lines.21` (0.194×), `cal.large.formatted-lines.22` (0.203×), `cal.large.formatted-lines.23` (0.202×), `cal.large.formatted-lines.24` (0.200×), `cal.large.formatted-lines.25` (0.198×), `cal.large.formatted-lines.26` (0.198×), `cal.large.formatted-lines.27` (0.208×), `cal.large.formatted-lines.28` (0.204×), `cal.large.formatted-lines.29` (0.198×), `cal.large.formatted-lines.30` (0.198×), `cal.large.formatted-lines.31` (0.192×), `hold.large.formatted-lines.00` (0.311×), `hold.large.formatted-lines.01` (0.388×), `hold.large.formatted-lines.02` (0.429×), `hold.large.formatted-lines.03` (0.457×), `hold.large.formatted-lines.04` (0.333×), `hold.large.formatted-lines.05` (0.386×), `hold.large.formatted-lines.06` (0.419×), `hold.large.formatted-lines.07` (0.490×), `hold.large.formatted-lines.08` (0.313×), `hold.large.formatted-lines.09` (0.357×), `hold.large.formatted-lines.10` (0.419×), `hold.large.formatted-lines.11` (0.482×), `hold.large.formatted-lines.12` (0.326×), `hold.large.formatted-lines.13` (0.376×), `hold.large.formatted-lines.14` (0.429×), `hold.large.formatted-lines.15` (0.460×), `hold.large.formatted-lines.16` (0.318×), `hold.large.formatted-lines.17` (0.385×), `hold.large.formatted-lines.18` (0.420×), `hold.large.formatted-lines.19` (0.473×), `hold.large.formatted-lines.20` (0.316×), `hold.large.formatted-lines.21` (0.381×), `hold.large.formatted-lines.22` (0.426×), `hold.large.formatted-lines.23` (0.475×), `hold.large.formatted-lines.24` (0.320×), `hold.large.formatted-lines.25` (0.407×), `hold.large.formatted-lines.26` (0.454×), `hold.large.formatted-lines.27` (0.461×), `hold.large.formatted-lines.28` (0.339×), `hold.large.formatted-lines.29` (0.392×), `hold.large.formatted-lines.30` (0.424×), `hold.large.formatted-lines.31` (0.463×).
- **literal hit (64):** short calls make matcher setup and Python/native boundary cost visible. `cal.large.literal-hit.00` (0.156×), `cal.large.literal-hit.01` (0.157×), `cal.large.literal-hit.02` (0.171×), `cal.large.literal-hit.03` (0.164×), `cal.large.literal-hit.04` (0.154×), `cal.large.literal-hit.05` (0.147×), `cal.large.literal-hit.06` (0.156×), `cal.large.literal-hit.07` (0.181×), `cal.large.literal-hit.08` (0.150×), `cal.large.literal-hit.09` (0.153×), `cal.large.literal-hit.10` (0.149×), `cal.large.literal-hit.11` (0.150×), `cal.large.literal-hit.12` (0.154×), `cal.large.literal-hit.13` (0.162×), `cal.large.literal-hit.14` (0.152×), `cal.large.literal-hit.15` (0.217×), `cal.large.literal-hit.16` (0.159×), `cal.large.literal-hit.17` (0.154×), `cal.large.literal-hit.18` (0.169×), `cal.large.literal-hit.19` (0.188×), `cal.large.literal-hit.20` (0.143×), `cal.large.literal-hit.21` (0.147×), `cal.large.literal-hit.22` (0.149×), `cal.large.literal-hit.23` (0.190×), `cal.large.literal-hit.24` (0.146×), `cal.large.literal-hit.25` (0.145×), `cal.large.literal-hit.26` (0.147×), `cal.large.literal-hit.27` (0.186×), `cal.large.literal-hit.28` (0.152×), `cal.large.literal-hit.29` (0.165×), `cal.large.literal-hit.30` (0.193×), `cal.large.literal-hit.31` (0.202×), `hold.large.literal-hit.00` (0.161×), `hold.large.literal-hit.01` (0.148×), `hold.large.literal-hit.02` (0.175×), `hold.large.literal-hit.03` (0.162×), `hold.large.literal-hit.04` (0.158×), `hold.large.literal-hit.05` (0.157×), `hold.large.literal-hit.06` (0.163×), `hold.large.literal-hit.07` (0.202×), `hold.large.literal-hit.08` (0.155×), `hold.large.literal-hit.09` (0.156×), `hold.large.literal-hit.10` (0.171×), `hold.large.literal-hit.11` (0.158×), `hold.large.literal-hit.12` (0.155×), `hold.large.literal-hit.13` (0.152×), `hold.large.literal-hit.14` (0.174×), `hold.large.literal-hit.15` (0.199×), `hold.large.literal-hit.16` (0.153×), `hold.large.literal-hit.17` (0.159×), `hold.large.literal-hit.18` (0.148×), `hold.large.literal-hit.19` (0.201×), `hold.large.literal-hit.20` (0.149×), `hold.large.literal-hit.21` (0.157×), `hold.large.literal-hit.22` (0.175×), `hold.large.literal-hit.23` (0.198×), `hold.large.literal-hit.24` (0.154×), `hold.large.literal-hit.25` (0.160×), `hold.large.literal-hit.26` (0.152×), `hold.large.literal-hit.27` (0.163×), `hold.large.literal-hit.28` (0.150×), `hold.large.literal-hit.29` (0.161×), `hold.large.literal-hit.30` (0.175×), `hold.large.literal-hit.31` (0.201×).
- **literal miss (64):** an absent phrase requires scanning every possible start. `cal.large.literal-miss.00` (0.190×), `cal.large.literal-miss.01` (0.203×), `cal.large.literal-miss.02` (0.222×), `cal.large.literal-miss.03` (0.266×), `cal.large.literal-miss.04` (0.189×), `cal.large.literal-miss.05` (0.200×), `cal.large.literal-miss.06` (0.226×), `cal.large.literal-miss.07` (0.269×), `cal.large.literal-miss.08` (0.188×), `cal.large.literal-miss.09` (0.155×), `cal.large.literal-miss.10` (0.227×), `cal.large.literal-miss.11` (0.266×), `cal.large.literal-miss.12` (0.179×), `cal.large.literal-miss.13` (0.206×), `cal.large.literal-miss.14` (0.230×), `cal.large.literal-miss.15` (0.279×), `cal.large.literal-miss.16` (0.186×), `cal.large.literal-miss.17` (0.154×), `cal.large.literal-miss.18` (0.226×), `cal.large.literal-miss.19` (0.267×), `cal.large.literal-miss.20` (0.180×), `cal.large.literal-miss.21` (0.153×), `cal.large.literal-miss.22` (0.239×), `cal.large.literal-miss.23` (0.136×), `cal.large.literal-miss.24` (0.158×), `cal.large.literal-miss.25` (0.200×), `cal.large.literal-miss.26` (0.221×), `cal.large.literal-miss.27` (0.286×), `cal.large.literal-miss.28` (0.180×), `cal.large.literal-miss.29` (0.208×), `cal.large.literal-miss.30` (0.234×), `cal.large.literal-miss.31` (0.269×), `hold.large.literal-miss.00` (0.188×), `hold.large.literal-miss.01` (0.162×), `hold.large.literal-miss.02` (0.223×), `hold.large.literal-miss.03` (0.258×), `hold.large.literal-miss.04` (0.190×), `hold.large.literal-miss.05` (0.201×), `hold.large.literal-miss.06` (0.229×), `hold.large.literal-miss.07` (0.156×), `hold.large.literal-miss.08` (0.166×), `hold.large.literal-miss.09` (0.204×), `hold.large.literal-miss.10` (0.231×), `hold.large.literal-miss.11` (0.252×), `hold.large.literal-miss.12` (0.185×), `hold.large.literal-miss.13` (0.166×), `hold.large.literal-miss.14` (0.228×), `hold.large.literal-miss.15` (0.266×), `hold.large.literal-miss.16` (0.191×), `hold.large.literal-miss.17` (0.199×), `hold.large.literal-miss.18` (0.231×), `hold.large.literal-miss.19` (0.155×), `hold.large.literal-miss.20` (0.188×), `hold.large.literal-miss.21` (0.193×), `hold.large.literal-miss.22` (0.231×), `hold.large.literal-miss.23` (0.266×), `hold.large.literal-miss.24` (0.165×), `hold.large.literal-miss.25` (0.158×), `hold.large.literal-miss.26` (0.223×), `hold.large.literal-miss.27` (0.270×), `hold.large.literal-miss.28` (0.187×), `hold.large.literal-miss.29` (0.162×), `hold.large.literal-miss.30` (0.152×), `hold.large.literal-miss.31` (0.274×).
- **long ending (64):** long inputs amplify scanning and end-boundary work. `cal.large.long-ending.00` (0.210×), `cal.large.long-ending.01` (0.211×), `cal.large.long-ending.02` (0.211×), `cal.large.long-ending.03` (0.212×), `cal.large.long-ending.04` (0.229×), `cal.large.long-ending.05` (0.227×), `cal.large.long-ending.06` (0.229×), `cal.large.long-ending.07` (0.229×), `cal.large.long-ending.08` (0.260×), `cal.large.long-ending.09` (0.258×), `cal.large.long-ending.10` (0.257×), `cal.large.long-ending.11` (0.262×), `cal.large.long-ending.12` (0.294×), `cal.large.long-ending.13` (0.303×), `cal.large.long-ending.14` (0.345×), `cal.large.long-ending.15` (0.279×), `cal.large.long-ending.16` (0.220×), `cal.large.long-ending.17` (0.195×), `cal.large.long-ending.18` (0.206×), `cal.large.long-ending.19` (0.216×), `cal.large.long-ending.20` (0.224×), `cal.large.long-ending.21` (0.208×), `cal.large.long-ending.22` (0.251×), `cal.large.long-ending.23` (0.230×), `cal.large.long-ending.24` (0.266×), `cal.large.long-ending.25` (0.262×), `cal.large.long-ending.26` (0.282×), `cal.large.long-ending.27` (0.252×), `cal.large.long-ending.28` (0.293×), `cal.large.long-ending.29` (0.287×), `cal.large.long-ending.30` (0.308×), `cal.large.long-ending.31` (0.289×), `hold.large.long-ending.00` (0.206×), `hold.large.long-ending.01` (0.205×), `hold.large.long-ending.02` (0.198×), `hold.large.long-ending.03` (0.203×), `hold.large.long-ending.04` (0.225×), `hold.large.long-ending.05` (0.235×), `hold.large.long-ending.06` (0.230×), `hold.large.long-ending.07` (0.224×), `hold.large.long-ending.08` (0.266×), `hold.large.long-ending.09` (0.254×), `hold.large.long-ending.10` (0.260×), `hold.large.long-ending.11` (0.259×), `hold.large.long-ending.12` (0.302×), `hold.large.long-ending.13` (0.287×), `hold.large.long-ending.14` (0.292×), `hold.large.long-ending.15` (0.293×), `hold.large.long-ending.16` (0.207×), `hold.large.long-ending.17` (0.208×), `hold.large.long-ending.18` (0.206×), `hold.large.long-ending.19` (0.207×), `hold.large.long-ending.20` (0.226×), `hold.large.long-ending.21` (0.222×), `hold.large.long-ending.22` (0.239×), `hold.large.long-ending.23` (0.227×), `hold.large.long-ending.24` (0.260×), `hold.large.long-ending.25` (0.264×), `hold.large.long-ending.26` (0.264×), `hold.large.long-ending.27` (0.263×), `hold.large.long-ending.28` (0.299×), `hold.large.long-ending.29` (0.286×), `hold.large.long-ending.30` (0.294×), `hold.large.long-ending.31` (0.285×).
- **module replace (64):** module/cache lookup combines with template and collection work. `cal.large.module-replace.00` (0.112×), `cal.large.module-replace.01` (0.108×), `cal.large.module-replace.02` (0.101×), `cal.large.module-replace.03` (0.105×), `cal.large.module-replace.04` (0.114×), `cal.large.module-replace.05` (0.106×), `cal.large.module-replace.06` (0.105×), `cal.large.module-replace.07` (0.101×), `cal.large.module-replace.08` (0.111×), `cal.large.module-replace.09` (0.107×), `cal.large.module-replace.10` (0.103×), `cal.large.module-replace.11` (0.101×), `cal.large.module-replace.12` (0.110×), `cal.large.module-replace.13` (0.105×), `cal.large.module-replace.14` (0.104×), `cal.large.module-replace.15` (0.103×), `cal.large.module-replace.16` (0.111×), `cal.large.module-replace.17` (0.104×), `cal.large.module-replace.18` (0.102×), `cal.large.module-replace.19` (0.101×), `cal.large.module-replace.20` (0.107×), `cal.large.module-replace.21` (0.105×), `cal.large.module-replace.22` (0.103×), `cal.large.module-replace.23` (0.099×), `cal.large.module-replace.24` (0.107×), `cal.large.module-replace.25` (0.105×), `cal.large.module-replace.26` (0.101×), `cal.large.module-replace.27` (0.100×), `cal.large.module-replace.28` (0.111×), `cal.large.module-replace.29` (0.104×), `cal.large.module-replace.30` (0.103×), `cal.large.module-replace.31` (0.102×), `hold.large.module-replace.00` (0.116×), `hold.large.module-replace.01` (0.108×), `hold.large.module-replace.02` (0.104×), `hold.large.module-replace.03` (0.103×), `hold.large.module-replace.04` (0.111×), `hold.large.module-replace.05` (0.108×), `hold.large.module-replace.06` (0.109×), `hold.large.module-replace.07` (0.105×), `hold.large.module-replace.08` (0.110×), `hold.large.module-replace.09` (0.105×), `hold.large.module-replace.10` (0.104×), `hold.large.module-replace.11` (0.102×), `hold.large.module-replace.12` (0.110×), `hold.large.module-replace.13` (0.107×), `hold.large.module-replace.14` (0.103×), `hold.large.module-replace.15` (0.101×), `hold.large.module-replace.16` (0.112×), `hold.large.module-replace.17` (0.106×), `hold.large.module-replace.18` (0.106×), `hold.large.module-replace.19` (0.104×), `hold.large.module-replace.20` (0.110×), `hold.large.module-replace.21` (0.107×), `hold.large.module-replace.22` (0.103×), `hold.large.module-replace.23` (0.101×), `hold.large.module-replace.24` (0.109×), `hold.large.module-replace.25` (0.107×), `hold.large.module-replace.26` (0.108×), `hold.large.module-replace.27` (0.102×), `hold.large.module-replace.28` (0.110×), `hold.large.module-replace.29` (0.105×), `hold.large.module-replace.30` (0.101×), `hold.large.module-replace.31` (0.103×).
- **module search (64):** module lookup and cache handling dominate short searches. `cal.large.module-search.00` (0.219×), `cal.large.module-search.01` (0.225×), `cal.large.module-search.02` (0.223×), `cal.large.module-search.03` (0.231×), `cal.large.module-search.04` (0.224×), `cal.large.module-search.05` (0.227×), `cal.large.module-search.06` (0.222×), `cal.large.module-search.07` (0.232×), `cal.large.module-search.08` (0.215×), `cal.large.module-search.09` (0.218×), `cal.large.module-search.10` (0.222×), `cal.large.module-search.11` (0.230×), `cal.large.module-search.12` (0.217×), `cal.large.module-search.13` (0.219×), `cal.large.module-search.14` (0.217×), `cal.large.module-search.15` (0.244×), `cal.large.module-search.16` (0.217×), `cal.large.module-search.17` (0.219×), `cal.large.module-search.18` (0.222×), `cal.large.module-search.19` (0.233×), `cal.large.module-search.20` (0.215×), `cal.large.module-search.21` (0.223×), `cal.large.module-search.22` (0.227×), `cal.large.module-search.23` (0.237×), `cal.large.module-search.24` (0.215×), `cal.large.module-search.25` (0.224×), `cal.large.module-search.26` (0.219×), `cal.large.module-search.27` (0.229×), `cal.large.module-search.28` (0.214×), `cal.large.module-search.29` (0.215×), `cal.large.module-search.30` (0.218×), `cal.large.module-search.31` (0.228×), `hold.large.module-search.00` (0.323×), `hold.large.module-search.01` (0.319×), `hold.large.module-search.02` (0.327×), `hold.large.module-search.03` (0.336×), `hold.large.module-search.04` (0.307×), `hold.large.module-search.05` (0.324×), `hold.large.module-search.06` (0.319×), `hold.large.module-search.07` (0.344×), `hold.large.module-search.08` (0.326×), `hold.large.module-search.09` (0.320×), `hold.large.module-search.10` (0.326×), `hold.large.module-search.11` (0.336×), `hold.large.module-search.12` (0.317×), `hold.large.module-search.13` (0.306×), `hold.large.module-search.14` (0.322×), `hold.large.module-search.15` (0.343×), `hold.large.module-search.16` (0.318×), `hold.large.module-search.17` (0.320×), `hold.large.module-search.18` (0.362×), `hold.large.module-search.19` (0.362×), `hold.large.module-search.20` (0.306×), `hold.large.module-search.21` (0.319×), `hold.large.module-search.22` (0.310×), `hold.large.module-search.23` (0.336×), `hold.large.module-search.24` (0.317×), `hold.large.module-search.25` (0.329×), `hold.large.module-search.26` (0.328×), `hold.large.module-search.27` (0.334×), `hold.large.module-search.28` (0.308×), `hold.large.module-search.29` (0.309×), `hold.large.module-search.30` (0.317×), `hold.large.module-search.31` (0.322×).
- **nearby capture (64):** lookaround and capture construction add work to short searches. `cal.large.nearby-capture.00` (0.165×), `cal.large.nearby-capture.01` (0.168×), `cal.large.nearby-capture.02` (0.175×), `cal.large.nearby-capture.03` (0.180×), `cal.large.nearby-capture.04` (0.157×), `cal.large.nearby-capture.05` (0.159×), `cal.large.nearby-capture.06` (0.168×), `cal.large.nearby-capture.07` (0.181×), `cal.large.nearby-capture.08` (0.157×), `cal.large.nearby-capture.09` (0.158×), `cal.large.nearby-capture.10` (0.174×), `cal.large.nearby-capture.11` (0.197×), `cal.large.nearby-capture.12` (0.162×), `cal.large.nearby-capture.13` (0.160×), `cal.large.nearby-capture.14` (0.163×), `cal.large.nearby-capture.15` (0.176×), `cal.large.nearby-capture.16` (0.155×), `cal.large.nearby-capture.17` (0.160×), `cal.large.nearby-capture.18` (0.168×), `cal.large.nearby-capture.19` (0.179×), `cal.large.nearby-capture.20` (0.154×), `cal.large.nearby-capture.21` (0.163×), `cal.large.nearby-capture.22` (0.168×), `cal.large.nearby-capture.23` (0.180×), `cal.large.nearby-capture.24` (0.158×), `cal.large.nearby-capture.25` (0.158×), `cal.large.nearby-capture.26` (0.168×), `cal.large.nearby-capture.27` (0.179×), `cal.large.nearby-capture.28` (0.149×), `cal.large.nearby-capture.29` (0.157×), `cal.large.nearby-capture.30` (0.163×), `cal.large.nearby-capture.31` (0.179×), `hold.large.nearby-capture.00` (0.208×), `hold.large.nearby-capture.01` (0.257×), `hold.large.nearby-capture.02` (0.353×), `hold.large.nearby-capture.03` (0.495×), `hold.large.nearby-capture.04` (0.190×), `hold.large.nearby-capture.05` (0.239×), `hold.large.nearby-capture.06` (0.321×), `hold.large.nearby-capture.07` (0.480×), `hold.large.nearby-capture.08` (0.184×), `hold.large.nearby-capture.09` (0.242×), `hold.large.nearby-capture.10` (0.333×), `hold.large.nearby-capture.11` (0.487×), `hold.large.nearby-capture.12` (0.199×), `hold.large.nearby-capture.13` (0.224×), `hold.large.nearby-capture.14` (0.328×), `hold.large.nearby-capture.15` (0.490×), `hold.large.nearby-capture.16` (0.199×), `hold.large.nearby-capture.17` (0.252×), `hold.large.nearby-capture.18` (0.321×), `hold.large.nearby-capture.19` (0.514×), `hold.large.nearby-capture.20` (0.195×), `hold.large.nearby-capture.21` (0.252×), `hold.large.nearby-capture.22` (0.334×), `hold.large.nearby-capture.23` (0.492×), `hold.large.nearby-capture.24` (0.190×), `hold.large.nearby-capture.25` (0.238×), `hold.large.nearby-capture.26` (0.325×), `hold.large.nearby-capture.27` (0.449×), `hold.large.nearby-capture.28` (0.186×), `hold.large.nearby-capture.29` (0.227×), `hold.large.nearby-capture.30` (0.312×), `hold.large.nearby-capture.31` (0.466×).
- **prefix check (64):** very short prefix checks are dominated by call/setup cost. `cal.large.prefix-check.00` (0.194×), `cal.large.prefix-check.01` (0.180×), `cal.large.prefix-check.02` (0.179×), `cal.large.prefix-check.03` (0.222×), `cal.large.prefix-check.04` (0.165×), `cal.large.prefix-check.05` (0.172×), `cal.large.prefix-check.06` (0.179×), `cal.large.prefix-check.07` (0.237×), `cal.large.prefix-check.08` (0.179×), `cal.large.prefix-check.09` (0.185×), `cal.large.prefix-check.10` (0.180×), `cal.large.prefix-check.11` (0.238×), `cal.large.prefix-check.12` (0.171×), `cal.large.prefix-check.13` (0.191×), `cal.large.prefix-check.14` (0.190×), `cal.large.prefix-check.15` (0.246×), `cal.large.prefix-check.16` (0.182×), `cal.large.prefix-check.17` (0.180×), `cal.large.prefix-check.18` (0.178×), `cal.large.prefix-check.19` (0.244×), `cal.large.prefix-check.20` (0.175×), `cal.large.prefix-check.21` (0.179×), `cal.large.prefix-check.22` (0.184×), `cal.large.prefix-check.23` (0.249×), `cal.large.prefix-check.24` (0.166×), `cal.large.prefix-check.25` (0.182×), `cal.large.prefix-check.26` (0.185×), `cal.large.prefix-check.27` (0.232×), `cal.large.prefix-check.28` (0.170×), `cal.large.prefix-check.29` (0.171×), `cal.large.prefix-check.30` (0.177×), `cal.large.prefix-check.31` (0.238×), `hold.large.prefix-check.00` (0.179×), `hold.large.prefix-check.01` (0.174×), `hold.large.prefix-check.02` (0.185×), `hold.large.prefix-check.03` (0.238×), `hold.large.prefix-check.04` (0.171×), `hold.large.prefix-check.05` (0.170×), `hold.large.prefix-check.06` (0.178×), `hold.large.prefix-check.07` (0.233×), `hold.large.prefix-check.08` (0.175×), `hold.large.prefix-check.09` (0.174×), `hold.large.prefix-check.10` (0.179×), `hold.large.prefix-check.11` (0.230×), `hold.large.prefix-check.12` (0.159×), `hold.large.prefix-check.13` (0.167×), `hold.large.prefix-check.14` (0.177×), `hold.large.prefix-check.15` (0.227×), `hold.large.prefix-check.16` (0.169×), `hold.large.prefix-check.17` (0.168×), `hold.large.prefix-check.18` (0.181×), `hold.large.prefix-check.19` (0.236×), `hold.large.prefix-check.20` (0.171×), `hold.large.prefix-check.21` (0.174×), `hold.large.prefix-check.22` (0.180×), `hold.large.prefix-check.23` (0.240×), `hold.large.prefix-check.24` (0.171×), `hold.large.prefix-check.25` (0.193×), `hold.large.prefix-check.26` (0.180×), `hold.large.prefix-check.27` (0.199×), `hold.large.prefix-check.28` (0.166×), `hold.large.prefix-check.29` (0.161×), `hold.large.prefix-check.30` (0.179×), `hold.large.prefix-check.31` (0.229×).
- **references (64):** backreferences require capture restoration and comparison. `cal.large.references.00` (0.196×), `cal.large.references.01` (0.193×), `cal.large.references.02` (0.183×), `cal.large.references.03` (0.221×), `cal.large.references.04` (0.191×), `cal.large.references.05` (0.238×), `cal.large.references.06` (0.211×), `cal.large.references.07` (0.230×), `cal.large.references.08` (0.184×), `cal.large.references.09` (0.194×), `cal.large.references.10` (0.199×), `cal.large.references.11` (0.243×), `cal.large.references.12` (0.208×), `cal.large.references.13` (0.196×), `cal.large.references.14` (0.192×), `cal.large.references.15` (0.222×), `cal.large.references.16` (0.199×), `cal.large.references.17` (0.232×), `cal.large.references.18` (0.228×), `cal.large.references.19` (0.215×), `cal.large.references.20` (0.177×), `cal.large.references.21` (0.206×), `cal.large.references.22` (0.205×), `cal.large.references.23` (0.256×), `cal.large.references.24` (0.202×), `cal.large.references.25` (0.191×), `cal.large.references.26` (0.196×), `cal.large.references.27` (0.223×), `cal.large.references.28` (0.188×), `cal.large.references.29` (0.236×), `cal.large.references.30` (0.211×), `cal.large.references.31` (0.216×), `hold.large.references.00` (0.207×), `hold.large.references.01` (0.199×), `hold.large.references.02` (0.205×), `hold.large.references.03` (0.239×), `hold.large.references.04` (0.196×), `hold.large.references.05` (0.249×), `hold.large.references.06` (0.213×), `hold.large.references.07` (0.227×), `hold.large.references.08` (0.184×), `hold.large.references.09` (0.187×), `hold.large.references.10` (0.208×), `hold.large.references.11` (0.295×), `hold.large.references.12` (0.234×), `hold.large.references.13` (0.196×), `hold.large.references.14` (0.200×), `hold.large.references.15` (0.218×), `hold.large.references.16` (0.210×), `hold.large.references.17` (0.263×), `hold.large.references.18` (0.210×), `hold.large.references.19` (0.221×), `hold.large.references.20` (0.180×), `hold.large.references.21` (0.198×), `hold.large.references.22` (0.173×), `hold.large.references.23` (0.317×), `hold.large.references.24` (0.216×), `hold.large.references.25` (0.202×), `hold.large.references.26` (0.208×), `hold.large.references.27` (0.229×), `hold.large.references.28` (0.203×), `hold.large.references.29` (0.247×), `hold.large.references.30` (0.214×), `hold.large.references.31` (0.220×).
- **replace callback (64):** repeated Python callbacks dominate replacement. `cal.large.replace-callback.00` (0.214×), `cal.large.replace-callback.01` (0.227×), `cal.large.replace-callback.02` (0.220×), `cal.large.replace-callback.03` (0.216×), `cal.large.replace-callback.04` (0.241×), `cal.large.replace-callback.05` (0.221×), `cal.large.replace-callback.06` (0.211×), `cal.large.replace-callback.07` (0.228×), `cal.large.replace-callback.08` (0.225×), `cal.large.replace-callback.09` (0.207×), `cal.large.replace-callback.10` (0.226×), `cal.large.replace-callback.11` (0.235×), `cal.large.replace-callback.12` (0.213×), `cal.large.replace-callback.13` (0.232×), `cal.large.replace-callback.14` (0.243×), `cal.large.replace-callback.15` (0.210×), `cal.large.replace-callback.16` (0.232×), `cal.large.replace-callback.17` (0.230×), `cal.large.replace-callback.18` (0.205×), `cal.large.replace-callback.19` (0.232×), `cal.large.replace-callback.20` (0.236×), `cal.large.replace-callback.21` (0.209×), `cal.large.replace-callback.22` (0.222×), `cal.large.replace-callback.23` (0.230×), `cal.large.replace-callback.24` (0.212×), `cal.large.replace-callback.25` (0.222×), `cal.large.replace-callback.26` (0.238×), `cal.large.replace-callback.27` (0.212×), `cal.large.replace-callback.28` (0.233×), `cal.large.replace-callback.29` (0.233×), `cal.large.replace-callback.30` (0.217×), `cal.large.replace-callback.31` (0.257×), `hold.large.replace-callback.00` (0.215×), `hold.large.replace-callback.01` (0.220×), `hold.large.replace-callback.02` (0.234×), `hold.large.replace-callback.03` (0.210×), `hold.large.replace-callback.04` (0.232×), `hold.large.replace-callback.05` (0.230×), `hold.large.replace-callback.06` (0.209×), `hold.large.replace-callback.07` (0.239×), `hold.large.replace-callback.08` (0.235×), `hold.large.replace-callback.09` (0.199×), `hold.large.replace-callback.10` (0.236×), `hold.large.replace-callback.11` (0.231×), `hold.large.replace-callback.12` (0.216×), `hold.large.replace-callback.13` (0.226×), `hold.large.replace-callback.14` (0.248×), `hold.large.replace-callback.15` (0.202×), `hold.large.replace-callback.16` (0.240×), `hold.large.replace-callback.17` (0.226×), `hold.large.replace-callback.18` (0.201×), `hold.large.replace-callback.19` (0.234×), `hold.large.replace-callback.20` (0.237×), `hold.large.replace-callback.21` (0.200×), `hold.large.replace-callback.22` (0.231×), `hold.large.replace-callback.23` (0.229×), `hold.large.replace-callback.24` (0.220×), `hold.large.replace-callback.25` (0.225×), `hold.large.replace-callback.26` (0.227×), `hold.large.replace-callback.27` (0.210×), `hold.large.replace-callback.28` (0.233×), `hold.large.replace-callback.29` (0.233×), `hold.large.replace-callback.30` (0.205×), `hold.large.replace-callback.31` (0.234×).
- **replace groups (64):** capture/template expansion and joining dominate replacement. `cal.large.replace-groups.00` (0.077×), `cal.large.replace-groups.01` (0.082×), `cal.large.replace-groups.02` (0.089×), `cal.large.replace-groups.03` (0.095×), `cal.large.replace-groups.04` (0.076×), `cal.large.replace-groups.05` (0.077×), `cal.large.replace-groups.06` (0.087×), `cal.large.replace-groups.07` (0.092×), `cal.large.replace-groups.08` (0.074×), `cal.large.replace-groups.09` (0.080×), `cal.large.replace-groups.10` (0.070×), `cal.large.replace-groups.11` (0.101×), `cal.large.replace-groups.12` (0.079×), `cal.large.replace-groups.13` (0.082×), `cal.large.replace-groups.14` (0.088×), `cal.large.replace-groups.15` (0.056×), `cal.large.replace-groups.16` (0.079×), `cal.large.replace-groups.17` (0.088×), `cal.large.replace-groups.18` (0.088×), `cal.large.replace-groups.19` (0.092×), `cal.large.replace-groups.20` (0.077×), `cal.large.replace-groups.21` (0.080×), `cal.large.replace-groups.22` (0.088×), `cal.large.replace-groups.23` (0.091×), `cal.large.replace-groups.24` (0.075×), `cal.large.replace-groups.25` (0.081×), `cal.large.replace-groups.26` (0.087×), `cal.large.replace-groups.27` (0.091×), `cal.large.replace-groups.28` (0.078×), `cal.large.replace-groups.29` (0.084×), `cal.large.replace-groups.30` (0.070×), `cal.large.replace-groups.31` (0.093×), `hold.large.replace-groups.00` (0.081×), `hold.large.replace-groups.01` (0.088×), `hold.large.replace-groups.02` (0.090×), `hold.large.replace-groups.03` (0.096×), `hold.large.replace-groups.04` (0.081×), `hold.large.replace-groups.05` (0.083×), `hold.large.replace-groups.06` (0.091×), `hold.large.replace-groups.07` (0.091×), `hold.large.replace-groups.08` (0.082×), `hold.large.replace-groups.09` (0.084×), `hold.large.replace-groups.10` (0.067×), `hold.large.replace-groups.11` (0.092×), `hold.large.replace-groups.12` (0.085×), `hold.large.replace-groups.13` (0.085×), `hold.large.replace-groups.14` (0.091×), `hold.large.replace-groups.15` (0.050×), `hold.large.replace-groups.16` (0.083×), `hold.large.replace-groups.17` (0.086×), `hold.large.replace-groups.18` (0.088×), `hold.large.replace-groups.19` (0.094×), `hold.large.replace-groups.20` (0.079×), `hold.large.replace-groups.21` (0.089×), `hold.large.replace-groups.22` (0.089×), `hold.large.replace-groups.23` (0.093×), `hold.large.replace-groups.24` (0.081×), `hold.large.replace-groups.25` (0.086×), `hold.large.replace-groups.26` (0.090×), `hold.large.replace-groups.27` (0.092×), `hold.large.replace-groups.28` (0.080×), `hold.large.replace-groups.29` (0.089×), `hold.large.replace-groups.30` (0.068×), `hold.large.replace-groups.31` (0.094×).
- **request records (64):** many structured captures and alternatives amplify matching work. `cal.large.request-records.00` (0.165×), `cal.large.request-records.01` (0.147×), `cal.large.request-records.02` (0.131×), `cal.large.request-records.03` (0.127×), `cal.large.request-records.04` (0.161×), `cal.large.request-records.05` (0.139×), `cal.large.request-records.06` (0.129×), `cal.large.request-records.07` (0.128×), `cal.large.request-records.08` (0.155×), `cal.large.request-records.09` (0.145×), `cal.large.request-records.10` (0.134×), `cal.large.request-records.11` (0.126×), `cal.large.request-records.12` (0.160×), `cal.large.request-records.13` (0.144×), `cal.large.request-records.14` (0.130×), `cal.large.request-records.15` (0.125×), `cal.large.request-records.16` (0.160×), `cal.large.request-records.17` (0.143×), `cal.large.request-records.18` (0.130×), `cal.large.request-records.19` (0.129×), `cal.large.request-records.20` (0.156×), `cal.large.request-records.21` (0.143×), `cal.large.request-records.22` (0.132×), `cal.large.request-records.23` (0.124×), `cal.large.request-records.24` (0.164×), `cal.large.request-records.25` (0.144×), `cal.large.request-records.26` (0.131×), `cal.large.request-records.27` (0.128×), `cal.large.request-records.28` (0.158×), `cal.large.request-records.29` (0.140×), `cal.large.request-records.30` (0.128×), `cal.large.request-records.31` (0.129×), `hold.large.request-records.00` (0.168×), `hold.large.request-records.01` (0.151×), `hold.large.request-records.02` (0.137×), `hold.large.request-records.03` (0.141×), `hold.large.request-records.04` (0.162×), `hold.large.request-records.05` (0.155×), `hold.large.request-records.06` (0.131×), `hold.large.request-records.07` (0.141×), `hold.large.request-records.08` (0.165×), `hold.large.request-records.09` (0.146×), `hold.large.request-records.10` (0.138×), `hold.large.request-records.11` (0.132×), `hold.large.request-records.12` (0.164×), `hold.large.request-records.13` (0.148×), `hold.large.request-records.14` (0.133×), `hold.large.request-records.15` (0.134×), `hold.large.request-records.16` (0.163×), `hold.large.request-records.17` (0.147×), `hold.large.request-records.18` (0.135×), `hold.large.request-records.19` (0.136×), `hold.large.request-records.20` (0.158×), `hold.large.request-records.21` (0.145×), `hold.large.request-records.22` (0.139×), `hold.large.request-records.23` (0.129×), `hold.large.request-records.24` (0.166×), `hold.large.request-records.25` (0.148×), `hold.large.request-records.26` (0.132×), `hold.large.request-records.27` (0.126×), `hold.large.request-records.28` (0.161×), `hold.large.request-records.29` (0.139×), `hold.large.request-records.30` (0.128×), `hold.large.request-records.31` (0.134×).
- **scanner bytes (64):** byte scanning and result construction amplify native-boundary work. `cal.large.scanner-bytes.00` (0.098×), `cal.large.scanner-bytes.01` (0.102×), `cal.large.scanner-bytes.02` (0.098×), `cal.large.scanner-bytes.03` (0.098×), `cal.large.scanner-bytes.04` (0.099×), `cal.large.scanner-bytes.05` (0.100×), `cal.large.scanner-bytes.06` (0.096×), `cal.large.scanner-bytes.07` (0.105×), `cal.large.scanner-bytes.08` (0.099×), `cal.large.scanner-bytes.09` (0.099×), `cal.large.scanner-bytes.10` (0.094×), `cal.large.scanner-bytes.11` (0.099×), `cal.large.scanner-bytes.12` (0.100×), `cal.large.scanner-bytes.13` (0.099×), `cal.large.scanner-bytes.14` (0.094×), `cal.large.scanner-bytes.15` (0.099×), `cal.large.scanner-bytes.16` (0.101×), `cal.large.scanner-bytes.17` (0.099×), `cal.large.scanner-bytes.18` (0.096×), `cal.large.scanner-bytes.19` (0.098×), `cal.large.scanner-bytes.20` (0.101×), `cal.large.scanner-bytes.21` (0.100×), `cal.large.scanner-bytes.22` (0.099×), `cal.large.scanner-bytes.23` (0.098×), `cal.large.scanner-bytes.24` (0.099×), `cal.large.scanner-bytes.25` (0.107×), `cal.large.scanner-bytes.26` (0.094×), `cal.large.scanner-bytes.27` (0.094×), `cal.large.scanner-bytes.28` (0.100×), `cal.large.scanner-bytes.29` (0.101×), `cal.large.scanner-bytes.30` (0.095×), `cal.large.scanner-bytes.31` (0.105×), `hold.large.scanner-bytes.00` (0.106×), `hold.large.scanner-bytes.01` (0.102×), `hold.large.scanner-bytes.02` (0.099×), `hold.large.scanner-bytes.03` (0.100×), `hold.large.scanner-bytes.04` (0.102×), `hold.large.scanner-bytes.05` (0.098×), `hold.large.scanner-bytes.06` (0.096×), `hold.large.scanner-bytes.07` (0.094×), `hold.large.scanner-bytes.08` (0.103×), `hold.large.scanner-bytes.09` (0.102×), `hold.large.scanner-bytes.10` (0.097×), `hold.large.scanner-bytes.11` (0.099×), `hold.large.scanner-bytes.12` (0.102×), `hold.large.scanner-bytes.13` (0.104×), `hold.large.scanner-bytes.14` (0.096×), `hold.large.scanner-bytes.15` (0.101×), `hold.large.scanner-bytes.16` (0.102×), `hold.large.scanner-bytes.17` (0.103×), `hold.large.scanner-bytes.18` (0.097×), `hold.large.scanner-bytes.19` (0.102×), `hold.large.scanner-bytes.20` (0.105×), `hold.large.scanner-bytes.21` (0.102×), `hold.large.scanner-bytes.22` (0.097×), `hold.large.scanner-bytes.23` (0.101×), `hold.large.scanner-bytes.24` (0.105×), `hold.large.scanner-bytes.25` (0.101×), `hold.large.scanner-bytes.26` (0.097×), `hold.large.scanner-bytes.27` (0.102×), `hold.large.scanner-bytes.28` (0.106×), `hold.large.scanner-bytes.29` (0.102×), `hold.large.scanner-bytes.30` (0.098×), `hold.large.scanner-bytes.31` (0.101×).
- **scanner text (64):** incremental scanning creates many match results and boundary calls. `cal.large.scanner-text.00` (0.119×), `cal.large.scanner-text.01` (0.111×), `cal.large.scanner-text.02` (0.109×), `cal.large.scanner-text.03` (0.103×), `cal.large.scanner-text.04` (0.117×), `cal.large.scanner-text.05` (0.110×), `cal.large.scanner-text.06` (0.105×), `cal.large.scanner-text.07` (0.112×), `cal.large.scanner-text.08` (0.123×), `cal.large.scanner-text.09` (0.114×), `cal.large.scanner-text.10` (0.104×), `cal.large.scanner-text.11` (0.110×), `cal.large.scanner-text.12` (0.116×), `cal.large.scanner-text.13` (0.109×), `cal.large.scanner-text.14` (0.110×), `cal.large.scanner-text.15` (0.106×), `cal.large.scanner-text.16` (0.116×), `cal.large.scanner-text.17` (0.111×), `cal.large.scanner-text.18` (0.101×), `cal.large.scanner-text.19` (0.107×), `cal.large.scanner-text.20` (0.122×), `cal.large.scanner-text.21` (0.110×), `cal.large.scanner-text.22` (0.108×), `cal.large.scanner-text.23` (0.115×), `cal.large.scanner-text.24` (0.113×), `cal.large.scanner-text.25` (0.108×), `cal.large.scanner-text.26` (0.104×), `cal.large.scanner-text.27` (0.106×), `cal.large.scanner-text.28` (0.115×), `cal.large.scanner-text.29` (0.116×), `cal.large.scanner-text.30` (0.109×), `cal.large.scanner-text.31` (0.118×), `hold.large.scanner-text.00` (0.140×), `hold.large.scanner-text.01` (0.131×), `hold.large.scanner-text.02` (0.112×), `hold.large.scanner-text.03` (0.129×), `hold.large.scanner-text.04` (0.136×), `hold.large.scanner-text.05` (0.133×), `hold.large.scanner-text.06` (0.107×), `hold.large.scanner-text.07` (0.124×), `hold.large.scanner-text.08` (0.132×), `hold.large.scanner-text.09` (0.121×), `hold.large.scanner-text.10` (0.113×), `hold.large.scanner-text.11` (0.107×), `hold.large.scanner-text.12` (0.121×), `hold.large.scanner-text.13` (0.110×), `hold.large.scanner-text.14` (0.107×), `hold.large.scanner-text.15` (0.125×), `hold.large.scanner-text.16` (0.139×), `hold.large.scanner-text.17` (0.135×), `hold.large.scanner-text.18` (0.110×), `hold.large.scanner-text.19` (0.124×), `hold.large.scanner-text.20` (0.130×), `hold.large.scanner-text.21` (0.119×), `hold.large.scanner-text.22` (0.107×), `hold.large.scanner-text.23` (0.110×), `hold.large.scanner-text.24` (0.123×), `hold.large.scanner-text.25` (0.115×), `hold.large.scanner-text.26` (0.110×), `hold.large.scanner-text.27` (0.109×), `hold.large.scanner-text.28` (0.122×), `hold.large.scanner-text.29` (0.114×), `hold.large.scanner-text.30` (0.109×), `hold.large.scanner-text.31` (0.108×).
- **split keep (64):** splitting and retained separators amplify collection work. `cal.large.split-keep.00` (0.145×), `cal.large.split-keep.01` (0.132×), `cal.large.split-keep.02` (0.134×), `cal.large.split-keep.03` (0.141×), `cal.large.split-keep.04` (0.145×), `cal.large.split-keep.05` (0.137×), `cal.large.split-keep.06` (0.133×), `cal.large.split-keep.07` (0.137×), `cal.large.split-keep.08` (0.140×), `cal.large.split-keep.09` (0.140×), `cal.large.split-keep.10` (0.144×), `cal.large.split-keep.11` (0.128×), `cal.large.split-keep.12` (0.146×), `cal.large.split-keep.13` (0.132×), `cal.large.split-keep.14` (0.138×), `cal.large.split-keep.15` (0.129×), `cal.large.split-keep.16` (0.145×), `cal.large.split-keep.17` (0.138×), `cal.large.split-keep.18` (0.134×), `cal.large.split-keep.19` (0.135×), `cal.large.split-keep.20` (0.147×), `cal.large.split-keep.21` (0.140×), `cal.large.split-keep.22` (0.142×), `cal.large.split-keep.23` (0.140×), `cal.large.split-keep.24` (0.145×), `cal.large.split-keep.25` (0.139×), `cal.large.split-keep.26` (0.129×), `cal.large.split-keep.27` (0.128×), `cal.large.split-keep.28` (0.142×), `cal.large.split-keep.29` (0.147×), `cal.large.split-keep.30` (0.140×), `cal.large.split-keep.31` (0.142×), `hold.large.split-keep.00` (0.145×), `hold.large.split-keep.01` (0.147×), `hold.large.split-keep.02` (0.151×), `hold.large.split-keep.03` (0.140×), `hold.large.split-keep.04` (0.145×), `hold.large.split-keep.05` (0.140×), `hold.large.split-keep.06` (0.138×), `hold.large.split-keep.07` (0.139×), `hold.large.split-keep.08` (0.145×), `hold.large.split-keep.09` (0.146×), `hold.large.split-keep.10` (0.139×), `hold.large.split-keep.11` (0.152×), `hold.large.split-keep.12` (0.147×), `hold.large.split-keep.13` (0.139×), `hold.large.split-keep.14` (0.138×), `hold.large.split-keep.15` (0.149×), `hold.large.split-keep.16` (0.150×), `hold.large.split-keep.17` (0.140×), `hold.large.split-keep.18` (0.138×), `hold.large.split-keep.19` (0.138×), `hold.large.split-keep.20` (0.150×), `hold.large.split-keep.21` (0.144×), `hold.large.split-keep.22` (0.138×), `hold.large.split-keep.23` (0.142×), `hold.large.split-keep.24` (0.144×), `hold.large.split-keep.25` (0.140×), `hold.large.split-keep.26` (0.139×), `hold.large.split-keep.27` (0.139×), `hold.large.split-keep.28` (0.143×), `hold.large.split-keep.29` (0.146×), `hold.large.split-keep.30` (0.145×), `hold.large.split-keep.31` (0.140×).
- **structured text (64):** configuration, paths, and quotes combine line starts, repeats, and captures. `cal.large.structured-text.00` (0.098×), `cal.large.structured-text.01` (0.059×), `cal.large.structured-text.02` (0.048×), `cal.large.structured-text.03` (0.092×), `cal.large.structured-text.04` (0.060×), `cal.large.structured-text.05` (0.090×), `cal.large.structured-text.06` (0.096×), `cal.large.structured-text.07` (0.060×), `cal.large.structured-text.08` (0.160×), `cal.large.structured-text.09` (0.096×), `cal.large.structured-text.10` (0.053×), `cal.large.structured-text.11` (0.023×), `cal.large.structured-text.12` (0.102×), `cal.large.structured-text.13` (0.057×), `cal.large.structured-text.14` (0.045×), `cal.large.structured-text.15` (0.089×), `cal.large.structured-text.16` (0.060×), `cal.large.structured-text.17` (0.090×), `cal.large.structured-text.18` (0.088×), `cal.large.structured-text.19` (0.054×), `cal.large.structured-text.20` (0.153×), `cal.large.structured-text.21` (0.094×), `cal.large.structured-text.22` (0.061×), `cal.large.structured-text.23` (0.023×), `cal.large.structured-text.24` (0.100×), `cal.large.structured-text.25` (0.063×), `cal.large.structured-text.26` (0.048×), `cal.large.structured-text.27` (0.090×), `cal.large.structured-text.28` (0.055×), `cal.large.structured-text.29` (0.090×), `cal.large.structured-text.30` (0.090×), `cal.large.structured-text.31` (0.052×), `hold.large.structured-text.00` (0.100×), `hold.large.structured-text.01` (0.057×), `hold.large.structured-text.02` (0.046×), `hold.large.structured-text.03` (0.091×), `hold.large.structured-text.04` (0.058×), `hold.large.structured-text.05` (0.094×), `hold.large.structured-text.06` (0.096×), `hold.large.structured-text.07` (0.057×), `hold.large.structured-text.08` (0.151×), `hold.large.structured-text.09` (0.101×), `hold.large.structured-text.10` (0.053×), `hold.large.structured-text.11` (0.024×), `hold.large.structured-text.12` (0.101×), `hold.large.structured-text.13` (0.056×), `hold.large.structured-text.14` (0.046×), `hold.large.structured-text.15` (0.090×), `hold.large.structured-text.16` (0.058×), `hold.large.structured-text.17` (0.092×), `hold.large.structured-text.18` (0.092×), `hold.large.structured-text.19` (0.053×), `hold.large.structured-text.20` (0.160×), `hold.large.structured-text.21` (0.093×), `hold.large.structured-text.22` (0.054×), `hold.large.structured-text.23` (0.023×), `hold.large.structured-text.24` (0.098×), `hold.large.structured-text.25` (0.054×), `hold.large.structured-text.26` (0.046×), `hold.large.structured-text.27` (0.092×), `hold.large.structured-text.28` (0.058×), `hold.large.structured-text.29` (0.090×), `hold.large.structured-text.30` (0.092×), `hold.large.structured-text.31` (0.049×).
- **unicode casefold (64):** full Unicode case handling requires extra character checks. `cal.large.unicode-casefold.00` (0.106×), `cal.large.unicode-casefold.01` (0.082×), `cal.large.unicode-casefold.02` (0.057×), `cal.large.unicode-casefold.03` (0.039×), `cal.large.unicode-casefold.04` (0.106×), `cal.large.unicode-casefold.05` (0.081×), `cal.large.unicode-casefold.06` (0.060×), `cal.large.unicode-casefold.07` (0.038×), `cal.large.unicode-casefold.08` (0.105×), `cal.large.unicode-casefold.09` (0.082×), `cal.large.unicode-casefold.10` (0.064×), `cal.large.unicode-casefold.11` (0.038×), `cal.large.unicode-casefold.12` (0.106×), `cal.large.unicode-casefold.13` (0.086×), `cal.large.unicode-casefold.14` (0.059×), `cal.large.unicode-casefold.15` (0.039×), `cal.large.unicode-casefold.16` (0.105×), `cal.large.unicode-casefold.17` (0.083×), `cal.large.unicode-casefold.18` (0.058×), `cal.large.unicode-casefold.19` (0.041×), `cal.large.unicode-casefold.20` (0.105×), `cal.large.unicode-casefold.21` (0.082×), `cal.large.unicode-casefold.22` (0.059×), `cal.large.unicode-casefold.23` (0.039×), `cal.large.unicode-casefold.24` (0.107×), `cal.large.unicode-casefold.25` (0.083×), `cal.large.unicode-casefold.26` (0.064×), `cal.large.unicode-casefold.27` (0.040×), `cal.large.unicode-casefold.28` (0.103×), `cal.large.unicode-casefold.29` (0.084×), `cal.large.unicode-casefold.30` (0.063×), `cal.large.unicode-casefold.31` (0.040×), `hold.large.unicode-casefold.00` (0.104×), `hold.large.unicode-casefold.01` (0.087×), `hold.large.unicode-casefold.02` (0.055×), `hold.large.unicode-casefold.03` (0.040×), `hold.large.unicode-casefold.04` (0.108×), `hold.large.unicode-casefold.05` (0.084×), `hold.large.unicode-casefold.06` (0.054×), `hold.large.unicode-casefold.07` (0.044×), `hold.large.unicode-casefold.08` (0.105×), `hold.large.unicode-casefold.09` (0.083×), `hold.large.unicode-casefold.10` (0.055×), `hold.large.unicode-casefold.11` (0.037×), `hold.large.unicode-casefold.12` (0.108×), `hold.large.unicode-casefold.13` (0.085×), `hold.large.unicode-casefold.14` (0.057×), `hold.large.unicode-casefold.15` (0.039×), `hold.large.unicode-casefold.16` (0.107×), `hold.large.unicode-casefold.17` (0.083×), `hold.large.unicode-casefold.18` (0.055×), `hold.large.unicode-casefold.19` (0.039×), `hold.large.unicode-casefold.20` (0.104×), `hold.large.unicode-casefold.21` (0.084×), `hold.large.unicode-casefold.22` (0.058×), `hold.large.unicode-casefold.23` (0.037×), `hold.large.unicode-casefold.24` (0.106×), `hold.large.unicode-casefold.25` (0.085×), `hold.large.unicode-casefold.26` (0.057×), `hold.large.unicode-casefold.27` (0.038×), `hold.large.unicode-casefold.28` (0.106×), `hold.large.unicode-casefold.29` (0.085×), `hold.large.unicode-casefold.30` (0.056×), `hold.large.unicode-casefold.31` (0.038×).
- **unicode words (64):** Unicode category and boundary checks are more expensive than ASCII scans. `cal.large.unicode-words.00` (0.109×), `cal.large.unicode-words.01` (0.092×), `cal.large.unicode-words.02` (0.066×), `cal.large.unicode-words.03` (0.044×), `cal.large.unicode-words.04` (0.107×), `cal.large.unicode-words.05` (0.093×), `cal.large.unicode-words.06` (0.068×), `cal.large.unicode-words.07` (0.041×), `cal.large.unicode-words.08` (0.098×), `cal.large.unicode-words.09` (0.084×), `cal.large.unicode-words.10` (0.063×), `cal.large.unicode-words.11` (0.041×), `cal.large.unicode-words.12` (0.106×), `cal.large.unicode-words.13` (0.086×), `cal.large.unicode-words.14` (0.062×), `cal.large.unicode-words.15` (0.041×), `cal.large.unicode-words.16` (0.099×), `cal.large.unicode-words.17` (0.083×), `cal.large.unicode-words.18` (0.065×), `cal.large.unicode-words.19` (0.043×), `cal.large.unicode-words.20` (0.106×), `cal.large.unicode-words.21` (0.089×), `cal.large.unicode-words.22` (0.066×), `cal.large.unicode-words.23` (0.044×), `cal.large.unicode-words.24` (0.107×), `cal.large.unicode-words.25` (0.093×), `cal.large.unicode-words.26` (0.065×), `cal.large.unicode-words.27` (0.044×), `cal.large.unicode-words.28` (0.105×), `cal.large.unicode-words.29` (0.087×), `cal.large.unicode-words.30` (0.064×), `cal.large.unicode-words.31` (0.043×), `hold.large.unicode-words.00` (0.110×), `hold.large.unicode-words.01` (0.091×), `hold.large.unicode-words.02` (0.066×), `hold.large.unicode-words.03` (0.044×), `hold.large.unicode-words.04` (0.114×), `hold.large.unicode-words.05` (0.088×), `hold.large.unicode-words.06` (0.065×), `hold.large.unicode-words.07` (0.043×), `hold.large.unicode-words.08` (0.105×), `hold.large.unicode-words.09` (0.088×), `hold.large.unicode-words.10` (0.065×), `hold.large.unicode-words.11` (0.043×), `hold.large.unicode-words.12` (0.108×), `hold.large.unicode-words.13` (0.091×), `hold.large.unicode-words.14` (0.066×), `hold.large.unicode-words.15` (0.045×), `hold.large.unicode-words.16` (0.120×), `hold.large.unicode-words.17` (0.088×), `hold.large.unicode-words.18` (0.070×), `hold.large.unicode-words.19` (0.048×), `hold.large.unicode-words.20` (0.109×), `hold.large.unicode-words.21` (0.098×), `hold.large.unicode-words.22` (0.065×), `hold.large.unicode-words.23` (0.043×), `hold.large.unicode-words.24` (0.107×), `hold.large.unicode-words.25` (0.092×), `hold.large.unicode-words.26` (0.066×), `hold.large.unicode-words.27` (0.043×), `hold.large.unicode-words.28` (0.105×), `hold.large.unicode-words.29` (0.091×), `hold.large.unicode-words.30` (0.066×), `hold.large.unicode-words.31` (0.044×).
- **verbose dotall (64):** verbose parsing or multi-line lazy matching adds compile/matcher work. `cal.large.verbose-dotall.00` (0.127×), `cal.large.verbose-dotall.01` (0.112×), `cal.large.verbose-dotall.02` (0.155×), `cal.large.verbose-dotall.03` (0.138×), `cal.large.verbose-dotall.04` (0.134×), `cal.large.verbose-dotall.05` (0.120×), `cal.large.verbose-dotall.06` (0.156×), `cal.large.verbose-dotall.07` (0.119×), `cal.large.verbose-dotall.08` (0.134×), `cal.large.verbose-dotall.09` (0.121×), `cal.large.verbose-dotall.10` (0.154×), `cal.large.verbose-dotall.11` (0.115×), `cal.large.verbose-dotall.12` (0.130×), `cal.large.verbose-dotall.13` (0.111×), `cal.large.verbose-dotall.14` (0.155×), `cal.large.verbose-dotall.15` (0.114×), `cal.large.verbose-dotall.16` (0.128×), `cal.large.verbose-dotall.17` (0.113×), `cal.large.verbose-dotall.18` (0.158×), `cal.large.verbose-dotall.19` (0.118×), `cal.large.verbose-dotall.20` (0.125×), `cal.large.verbose-dotall.21` (0.115×), `cal.large.verbose-dotall.22` (0.160×), `cal.large.verbose-dotall.23` (0.122×), `cal.large.verbose-dotall.24` (0.127×), `cal.large.verbose-dotall.25` (0.104×), `cal.large.verbose-dotall.26` (0.159×), `cal.large.verbose-dotall.27` (0.119×), `cal.large.verbose-dotall.28` (0.128×), `cal.large.verbose-dotall.29` (0.110×), `cal.large.verbose-dotall.30` (0.159×), `cal.large.verbose-dotall.31` (0.124×), `hold.large.verbose-dotall.00` (0.130×), `hold.large.verbose-dotall.01` (0.106×), `hold.large.verbose-dotall.02` (0.163×), `hold.large.verbose-dotall.03` (0.115×), `hold.large.verbose-dotall.04` (0.131×), `hold.large.verbose-dotall.05` (0.110×), `hold.large.verbose-dotall.06` (0.155×), `hold.large.verbose-dotall.07` (0.110×), `hold.large.verbose-dotall.08` (0.132×), `hold.large.verbose-dotall.09` (0.110×), `hold.large.verbose-dotall.10` (0.160×), `hold.large.verbose-dotall.11` (0.120×), `hold.large.verbose-dotall.12` (0.127×), `hold.large.verbose-dotall.13` (0.107×), `hold.large.verbose-dotall.14` (0.149×), `hold.large.verbose-dotall.15` (0.116×), `hold.large.verbose-dotall.16` (0.128×), `hold.large.verbose-dotall.17` (0.107×), `hold.large.verbose-dotall.18` (0.152×), `hold.large.verbose-dotall.19` (0.114×), `hold.large.verbose-dotall.20` (0.134×), `hold.large.verbose-dotall.21` (0.105×), `hold.large.verbose-dotall.22` (0.156×), `hold.large.verbose-dotall.23` (0.114×), `hold.large.verbose-dotall.24` (0.129×), `hold.large.verbose-dotall.25` (0.108×), `hold.large.verbose-dotall.26` (0.155×), `hold.large.verbose-dotall.27` (0.112×), `hold.large.verbose-dotall.28` (0.136×), `hold.large.verbose-dotall.29` (0.105×), `hold.large.verbose-dotall.30` (0.156×), `hold.large.verbose-dotall.31` (0.112×).
- **whole check (64):** structured repeats and full-string checks require more matcher state. `cal.large.whole-check.00` (0.152×), `cal.large.whole-check.01` (0.095×), `cal.large.whole-check.02` (0.087×), `cal.large.whole-check.03` (0.072×), `cal.large.whole-check.04` (0.110×), `cal.large.whole-check.05` (0.088×), `cal.large.whole-check.06` (0.238×), `cal.large.whole-check.07` (0.073×), `cal.large.whole-check.08` (0.110×), `cal.large.whole-check.09` (0.104×), `cal.large.whole-check.10` (0.084×), `cal.large.whole-check.11` (0.074×), `cal.large.whole-check.12` (0.109×), `cal.large.whole-check.13` (0.247×), `cal.large.whole-check.14` (0.101×), `cal.large.whole-check.15` (0.074×), `cal.large.whole-check.16` (0.105×), `cal.large.whole-check.17` (0.086×), `cal.large.whole-check.18` (0.083×), `cal.large.whole-check.19` (0.095×), `cal.large.whole-check.20` (0.259×), `cal.large.whole-check.21` (0.088×), `cal.large.whole-check.22` (0.101×), `cal.large.whole-check.23` (0.087×), `cal.large.whole-check.24` (0.103×), `cal.large.whole-check.25` (0.088×), `cal.large.whole-check.26` (0.082×), `cal.large.whole-check.27` (0.240×), `cal.large.whole-check.28` (0.102×), `cal.large.whole-check.29` (0.083×), `cal.large.whole-check.30` (0.076×), `cal.large.whole-check.31` (0.090×), `hold.large.whole-check.00` (0.104×), `hold.large.whole-check.01` (0.096×), `hold.large.whole-check.02` (0.092×), `hold.large.whole-check.03` (0.078×), `hold.large.whole-check.04` (0.106×), `hold.large.whole-check.05` (0.085×), `hold.large.whole-check.06` (0.221×), `hold.large.whole-check.07` (0.081×), `hold.large.whole-check.08` (0.109×), `hold.large.whole-check.09` (0.079×), `hold.large.whole-check.10` (0.074×), `hold.large.whole-check.11` (0.080×), `hold.large.whole-check.12` (0.108×), `hold.large.whole-check.13` (0.240×), `hold.large.whole-check.14` (0.075×), `hold.large.whole-check.15` (0.077×), `hold.large.whole-check.16` (0.108×), `hold.large.whole-check.17` (0.088×), `hold.large.whole-check.18` (0.076×), `hold.large.whole-check.19` (0.078×), `hold.large.whole-check.20` (0.260×), `hold.large.whole-check.21` (0.088×), `hold.large.whole-check.22` (0.067×), `hold.large.whole-check.23` (0.079×), `hold.large.whole-check.24` (0.098×), `hold.large.whole-check.25` (0.084×), `hold.large.whole-check.26` (0.078×), `hold.large.whole-check.27` (0.230×), `hold.large.whole-check.28` (0.098×), `hold.large.whole-check.29` (0.082×), `hold.large.whole-check.30` (0.083×), `hold.large.whole-check.31` (0.076×).
- **window collection (64):** window checks combine with repeated collection work. `cal.large.window-collection.00` (0.202×), `cal.large.window-collection.01` (0.306×), `cal.large.window-collection.02` (0.171×), `cal.large.window-collection.03` (0.331×), `cal.large.window-collection.04` (0.200×), `cal.large.window-collection.05` (0.277×), `cal.large.window-collection.06` (0.172×), `cal.large.window-collection.07` (0.350×), `cal.large.window-collection.08` (0.205×), `cal.large.window-collection.09` (0.282×), `cal.large.window-collection.10` (0.177×), `cal.large.window-collection.11` (0.371×), `cal.large.window-collection.12` (0.196×), `cal.large.window-collection.13` (0.299×), `cal.large.window-collection.14` (0.178×), `cal.large.window-collection.15` (0.348×), `cal.large.window-collection.16` (0.208×), `cal.large.window-collection.17` (0.308×), `cal.large.window-collection.18` (0.176×), `cal.large.window-collection.19` (0.370×), `cal.large.window-collection.20` (0.191×), `cal.large.window-collection.21` (0.302×), `cal.large.window-collection.22` (0.168×), `cal.large.window-collection.23` (0.367×), `cal.large.window-collection.24` (0.212×), `cal.large.window-collection.25` (0.279×), `cal.large.window-collection.26` (0.182×), `cal.large.window-collection.27` (0.328×), `cal.large.window-collection.28` (0.204×), `cal.large.window-collection.29` (0.296×), `cal.large.window-collection.30` (0.174×), `cal.large.window-collection.31` (0.315×), `hold.large.window-collection.00` (0.212×), `hold.large.window-collection.01` (0.346×), `hold.large.window-collection.02` (0.169×), `hold.large.window-collection.03` (0.351×), `hold.large.window-collection.04` (0.203×), `hold.large.window-collection.05` (0.312×), `hold.large.window-collection.06` (0.176×), `hold.large.window-collection.07` (0.351×), `hold.large.window-collection.08` (0.202×), `hold.large.window-collection.09` (0.314×), `hold.large.window-collection.10` (0.174×), `hold.large.window-collection.11` (0.346×), `hold.large.window-collection.12` (0.201×), `hold.large.window-collection.13` (0.309×), `hold.large.window-collection.14` (0.169×), `hold.large.window-collection.15` (0.349×), `hold.large.window-collection.16` (0.203×), `hold.large.window-collection.17` (0.284×), `hold.large.window-collection.18` (0.169×), `hold.large.window-collection.19` (0.311×), `hold.large.window-collection.20` (0.205×), `hold.large.window-collection.21` (0.308×), `hold.large.window-collection.22` (0.175×), `hold.large.window-collection.23` (0.348×), `hold.large.window-collection.24` (0.205×), `hold.large.window-collection.25` (0.290×), `hold.large.window-collection.26` (0.168×), `hold.large.window-collection.27` (0.339×), `hold.large.window-collection.28` (0.201×), `hold.large.window-collection.29` (0.275×), `hold.large.window-collection.30` (0.170×), `hold.large.window-collection.31` (0.334×).
- **window search (64):** short windowed searches expose position/boundary overhead. `cal.large.window-search.00` (0.206×), `cal.large.window-search.01` (0.207×), `cal.large.window-search.02` (0.206×), `cal.large.window-search.03` (0.211×), `cal.large.window-search.04` (0.197×), `cal.large.window-search.05` (0.197×), `cal.large.window-search.06` (0.198×), `cal.large.window-search.07` (0.227×), `cal.large.window-search.08` (0.209×), `cal.large.window-search.09` (0.199×), `cal.large.window-search.10` (0.198×), `cal.large.window-search.11` (0.214×), `cal.large.window-search.12` (0.210×), `cal.large.window-search.13` (0.194×), `cal.large.window-search.14` (0.198×), `cal.large.window-search.15` (0.205×), `cal.large.window-search.16` (0.214×), `cal.large.window-search.17` (0.199×), `cal.large.window-search.18` (0.217×), `cal.large.window-search.19` (0.205×), `cal.large.window-search.20` (0.194×), `cal.large.window-search.21` (0.196×), `cal.large.window-search.22` (0.199×), `cal.large.window-search.23` (0.219×), `cal.large.window-search.24` (0.190×), `cal.large.window-search.25` (0.193×), `cal.large.window-search.26` (0.197×), `cal.large.window-search.27` (0.235×), `cal.large.window-search.28` (0.190×), `cal.large.window-search.29` (0.195×), `cal.large.window-search.30` (0.201×), `cal.large.window-search.31` (0.199×), `hold.large.window-search.00` (0.224×), `hold.large.window-search.01` (0.225×), `hold.large.window-search.02` (0.221×), `hold.large.window-search.03` (0.228×), `hold.large.window-search.04` (0.214×), `hold.large.window-search.05` (0.209×), `hold.large.window-search.06` (0.223×), `hold.large.window-search.07` (0.225×), `hold.large.window-search.08` (0.208×), `hold.large.window-search.09` (0.218×), `hold.large.window-search.10` (0.221×), `hold.large.window-search.11` (0.223×), `hold.large.window-search.12` (0.205×), `hold.large.window-search.13` (0.224×), `hold.large.window-search.14` (0.235×), `hold.large.window-search.15` (0.222×), `hold.large.window-search.16` (0.212×), `hold.large.window-search.17` (0.214×), `hold.large.window-search.18` (0.222×), `hold.large.window-search.19` (0.279×), `hold.large.window-search.20` (0.222×), `hold.large.window-search.21` (0.238×), `hold.large.window-search.22` (0.212×), `hold.large.window-search.23` (0.232×), `hold.large.window-search.24` (0.213×), `hold.large.window-search.25` (0.219×), `hold.large.window-search.26` (0.228×), `hold.large.window-search.27` (0.236×), `hold.large.window-search.28` (0.209×), `hold.large.window-search.29` (0.215×), `hold.large.window-search.30` (0.217×), `hold.large.window-search.31` (0.216×).

## Every task

`FASTER` means the lower end of the measured range exceeds 1×. `SLOWDOWN` means the result is below 0.8×. Memory is the median traced-peak engine/baseline ratio.

| Test set | Task | Engine | Speed | 95% range | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| calibration | `cal.search.literal.hit` | Python engine | 0.0425× | 0.0417–0.0431× | 21.47× | SLOWDOWN |
| calibration | `cal.search.literal.hit` | Native C engine | 1.1101× | 1.1021–1.1174× | 0.73× | FASTER |
| calibration | `cal.search.literal.hit` | Rust engine | 0.1449× | 0.1429–0.1467× | 0.67× | SLOWDOWN |
| calibration | `cal.search.literal.miss` | Python engine | 0.1399× | 0.1374–0.1416× | 112.00× | SLOWDOWN |
| calibration | `cal.search.literal.miss` | Native C engine | 1.1557× | 1.1525–1.1591× | 0.00× | FASTER |
| calibration | `cal.search.literal.miss` | Rust engine | 0.1619× | 0.1599–0.1637× | 0.00× | SLOWDOWN |
| calibration | `cal.search.long-boundary` | Python engine | 0.2849× | 0.2815–0.2883× | 2.98× | SLOWDOWN |
| calibration | `cal.search.long-boundary` | Native C engine | 12.7567× | 12.3939–13.0514× | 0.07× | FASTER |
| calibration | `cal.search.long-boundary` | Rust engine | 0.3153× | 0.3058–0.3226× | 0.07× | SLOWDOWN |
| calibration | `cal.search.class-anchor` | Python engine | 0.0278× | 0.0274–0.0284× | 5.34× | SLOWDOWN |
| calibration | `cal.search.class-anchor` | Native C engine | 1.2750× | 1.2595–1.2992× | 0.07× | FASTER |
| calibration | `cal.search.class-anchor` | Rust engine | 0.2010× | 0.1982–0.2035× | 0.07× | SLOWDOWN |
| calibration | `cal.match.prefix` | Python engine | 0.0245× | 0.0243–0.0248× | 4.26× | SLOWDOWN |
| calibration | `cal.match.prefix` | Native C engine | 1.2445× | 1.1276–1.3115× | 0.07× | FASTER |
| calibration | `cal.match.prefix` | Rust engine | 0.1814× | 0.1779–0.1845× | 0.07× | SLOWDOWN |
| calibration | `cal.fullmatch.structured` | Python engine | 0.0184× | 0.0179–0.0193× | 9.93× | SLOWDOWN |
| calibration | `cal.fullmatch.structured` | Native C engine | 1.5493× | 1.5011–1.6258× | 0.07× | FASTER |
| calibration | `cal.fullmatch.structured` | Rust engine | 0.1111× | 0.1081–0.1156× | 0.06× | SLOWDOWN |
| calibration | `cal.search.look-capture` | Python engine | 0.0236× | 0.0235–0.0238× | 10.27× | SLOWDOWN |
| calibration | `cal.search.look-capture` | Native C engine | 1.4974× | 1.4855–1.5085× | 0.08× | FASTER |
| calibration | `cal.search.look-capture` | Rust engine | 0.1663× | 0.1654–0.1672× | 0.06× | SLOWDOWN |
| calibration | `cal.findall.tokens` | Python engine | 0.0198× | 0.0195–0.0203× | 5.35× | SLOWDOWN |
| calibration | `cal.findall.tokens` | Native C engine | 1.3008× | 1.2202–1.3649× | 0.28× | FASTER |
| calibration | `cal.findall.tokens` | Rust engine | 0.3140× | 0.3074–0.3229× | 1.74× | SLOWDOWN |
| calibration | `cal.finditer.groups` | Python engine | 0.0204× | 0.0199–0.0210× | 6.58× | SLOWDOWN |
| calibration | `cal.finditer.groups` | Native C engine | 2.0246× | 1.9748–2.0754× | 0.41× | FASTER |
| calibration | `cal.finditer.groups` | Rust engine | 0.1653× | 0.1605–0.1704× | 0.34× | SLOWDOWN |
| calibration | `cal.split.capture` | Python engine | 0.0181× | 0.0171–0.0196× | 7.83× | SLOWDOWN |
| calibration | `cal.split.capture` | Native C engine | 1.9690× | 1.8667–2.1198× | 0.20× | FASTER |
| calibration | `cal.split.capture` | Rust engine | 0.1063× | 0.0996–0.1119× | 1.29× | SLOWDOWN |
| calibration | `cal.sub.template` | Python engine | 0.0210× | 0.0207–0.0213× | 8.21× | SLOWDOWN |
| calibration | `cal.sub.template` | Native C engine | 2.0061× | 1.9850–2.0280× | 0.12× | FASTER |
| calibration | `cal.sub.template` | Rust engine | 0.0837× | 0.0828–0.0849× | 1.44× | SLOWDOWN |
| calibration | `cal.subn.callable` | Python engine | 0.0628× | 0.0616–0.0644× | 3.32× | SLOWDOWN |
| calibration | `cal.subn.callable` | Native C engine | 1.1974× | 1.1712–1.2346× | 0.25× | FASTER |
| calibration | `cal.subn.callable` | Rust engine | 0.2020× | 0.1978–0.2076× | 0.54× | SLOWDOWN |
| calibration | `cal.bytes.tokens` | Python engine | 0.0186× | 0.0185–0.0188× | 5.51× | SLOWDOWN |
| calibration | `cal.bytes.tokens` | Native C engine | 1.1433× | 1.0831–1.1817× | 0.12× | FASTER |
| calibration | `cal.bytes.tokens` | Rust engine | 0.2083× | 0.1982–0.2161× | 1.20× | SLOWDOWN |
| calibration | `cal.unicode.words` | Python engine | 0.0233× | 0.0220–0.0251× | 6.02× | SLOWDOWN |
| calibration | `cal.unicode.words` | Native C engine | 1.0255× | 0.9694–1.1117× | 0.20× | — |
| calibration | `cal.unicode.words` | Rust engine | 0.1139× | 0.1081–0.1222× | 0.87× | SLOWDOWN |
| calibration | `cal.cold.compile-search` | Python engine | 0.0799× | 0.0792–0.0808× | 6.87× | SLOWDOWN |
| calibration | `cal.cold.compile-search` | Native C engine | 1.3566× | 1.3071–1.3908× | 1.71× | FASTER |
| calibration | `cal.cold.compile-search` | Rust engine | 1.0686× | 1.0587–1.0803× | 0.90× | FASTER |
| calibration | `cal.module.warm` | Python engine | 0.0218× | 0.0213–0.0221× | 5.79× | SLOWDOWN |
| calibration | `cal.module.warm` | Native C engine | 1.3576× | 1.3421–1.3694× | 0.07× | FASTER |
| calibration | `cal.module.warm` | Rust engine | 0.2001× | 0.1986–0.2013× | 0.07× | SLOWDOWN |
| calibration | `cal.empty.finditer` | Python engine | 0.0181× | 0.0177–0.0187× | 7.17× | SLOWDOWN |
| calibration | `cal.empty.finditer` | Native C engine | 2.2531× | 2.2000–2.3321× | 0.36× | FASTER |
| calibration | `cal.empty.finditer` | Rust engine | 0.1922× | 0.1873–0.1993× | 0.37× | SLOWDOWN |
| calibration | `cal.backref.fullmatch` | Python engine | 0.0208× | 0.0206–0.0210× | 6.45× | SLOWDOWN |
| calibration | `cal.backref.fullmatch` | Native C engine | 1.4140× | 1.3951–1.4332× | 0.08× | FASTER |
| calibration | `cal.backref.fullmatch` | Rust engine | 0.1783× | 0.1692–0.1839× | 0.06× | SLOWDOWN |
| calibration | `cal.conditional.match` | Python engine | 0.0263× | 0.0261–0.0265× | 6.57× | SLOWDOWN |
| calibration | `cal.conditional.match` | Native C engine | 1.4018× | 1.3938–1.4103× | 0.08× | FASTER |
| calibration | `cal.conditional.match` | Rust engine | 0.1449× | 0.1392–0.1491× | 0.06× | SLOWDOWN |
| calibration | `cal.atomic.search` | Python engine | 0.0293× | 0.0291–0.0295× | 4.84× | SLOWDOWN |
| calibration | `cal.atomic.search` | Native C engine | 1.0943× | 1.0858–1.1028× | 0.50× | FASTER |
| calibration | `cal.atomic.search` | Rust engine | 0.1863× | 0.1841–0.1881× | 0.07× | SLOWDOWN |
| calibration | `cal.byteslike.findall` | Python engine | 0.0157× | 0.0155–0.0158× | 7.88× | SLOWDOWN |
| calibration | `cal.byteslike.findall` | Native C engine | 2.4768× | 2.4307–2.5216× | 0.18× | FASTER |
| calibration | `cal.byteslike.findall` | Rust engine | 0.2910× | 0.2867–0.2945× | 0.75× | SLOWDOWN |
| calibration | `cal.unicode-name.search` | Python engine | 0.0456× | 0.0448–0.0462× | 3.17× | SLOWDOWN |
| calibration | `cal.unicode-name.search` | Native C engine | 1.4961× | 1.4868–1.5056× | 0.07× | FASTER |
| calibration | `cal.unicode-name.search` | Rust engine | 0.1783× | 0.1773–0.1794× | 0.09× | SLOWDOWN |
| calibration | `cal.ignorecase.findall` | Python engine | 0.0310× | 0.0310–0.0311× | 4.23× | SLOWDOWN |
| calibration | `cal.ignorecase.findall` | Native C engine | 1.7343× | 1.7169–1.7497× | 0.16× | FASTER |
| calibration | `cal.ignorecase.findall` | Rust engine | 0.4030× | 0.4006–0.4056× | 1.05× | SLOWDOWN |
| calibration | `cal.many.split` | Python engine | 0.0240× | 0.0236–0.0245× | 5.29× | SLOWDOWN |
| calibration | `cal.many.split` | Native C engine | 1.3420× | 1.3217–1.3749× | 0.20× | FASTER |
| calibration | `cal.many.split` | Rust engine | 0.1269× | 0.1246–0.1301× | 1.24× | SLOWDOWN |
| calibration | `cal.escape.text` | Python engine | 0.9869× | 0.9658–0.9989× | 1.00× | — |
| calibration | `cal.escape.text` | Native C engine | 3.3842× | 3.3579–3.4150× | 1.00× | FASTER |
| calibration | `cal.escape.text` | Rust engine | 0.9965× | 0.9931–1.0003× | 1.00× | — |
| calibration | `cal.compile.only` | Python engine | 1.9634× | 1.9331–1.9921× | 0.52× | FASTER |
| calibration | `cal.compile.only` | Native C engine | 1.6229× | 1.6045–1.6414× | 1.59× | FASTER |
| calibration | `cal.compile.only` | Rust engine | 1.3986× | 1.3540–1.4307× | 0.56× | FASTER |
| calibration | `cal.scanner.search` | Python engine | 0.0211× | 0.0209–0.0213× | 5.82× | SLOWDOWN |
| calibration | `cal.scanner.search` | Native C engine | 1.3521× | 1.3268–1.3789× | 0.38× | FASTER |
| calibration | `cal.scanner.search` | Rust engine | 0.1200× | 0.1183–0.1212× | 0.22× | SLOWDOWN |
| calibration | `cal.match.surface` | Python engine | 0.0243× | 0.0239–0.0246× | 11.53× | SLOWDOWN |
| calibration | `cal.match.surface` | Native C engine | 1.4235× | 1.3840–1.4543× | 0.32× | FASTER |
| calibration | `cal.match.surface` | Rust engine | 0.1414× | 0.1396–0.1436× | 0.67× | SLOWDOWN |
| holdout | `hold.search.literal.hit` | Python engine | 0.0439× | 0.0434–0.0444× | 20.93× | SLOWDOWN |
| holdout | `hold.search.literal.hit` | Native C engine | 1.0824× | 1.0159–1.1245× | 0.73× | FASTER |
| holdout | `hold.search.literal.hit` | Rust engine | 0.1524× | 0.1505–0.1547× | 0.67× | SLOWDOWN |
| holdout | `hold.search.literal.miss` | Python engine | 0.1420× | 0.1395–0.1436× | 112.00× | SLOWDOWN |
| holdout | `hold.search.literal.miss` | Native C engine | 1.1702× | 1.1616–1.1789× | 0.00× | FASTER |
| holdout | `hold.search.literal.miss` | Rust engine | 0.1772× | 0.1746–0.1798× | 0.00× | SLOWDOWN |
| holdout | `hold.search.long-boundary` | Python engine | 0.3756× | 0.3583–0.4031× | 2.98× | SLOWDOWN |
| holdout | `hold.search.long-boundary` | Native C engine | 18.3950× | 17.3698–19.8503× | 0.07× | FASTER |
| holdout | `hold.search.long-boundary` | Rust engine | 0.3282× | 0.3126–0.3529× | 0.07× | SLOWDOWN |
| holdout | `hold.search.class-anchor` | Python engine | 0.0282× | 0.0280–0.0284× | 5.34× | SLOWDOWN |
| holdout | `hold.search.class-anchor` | Native C engine | 1.3522× | 1.2654–1.4019× | 0.07× | FASTER |
| holdout | `hold.search.class-anchor` | Rust engine | 0.2127× | 0.2084–0.2161× | 0.07× | SLOWDOWN |
| holdout | `hold.match.prefix` | Python engine | 0.0267× | 0.0257–0.0281× | 4.26× | SLOWDOWN |
| holdout | `hold.match.prefix` | Native C engine | 1.3718× | 1.3170–1.4530× | 0.07× | FASTER |
| holdout | `hold.match.prefix` | Rust engine | 0.1896× | 0.1819–0.2007× | 0.07× | SLOWDOWN |
| holdout | `hold.fullmatch.structured` | Python engine | 0.0143× | 0.0141–0.0145× | 14.49× | SLOWDOWN |
| holdout | `hold.fullmatch.structured` | Native C engine | 1.3808× | 1.3641–1.3996× | 0.07× | FASTER |
| holdout | `hold.fullmatch.structured` | Rust engine | 0.1255× | 0.1239–0.1272× | 0.06× | SLOWDOWN |
| holdout | `hold.search.look-capture` | Python engine | 0.0188× | 0.0179–0.0205× | 11.42× | SLOWDOWN |
| holdout | `hold.search.look-capture` | Native C engine | 1.1578× | 1.0702–1.2121× | 0.08× | FASTER |
| holdout | `hold.search.look-capture` | Rust engine | 0.1545× | 0.1532–0.1562× | 0.06× | SLOWDOWN |
| holdout | `hold.findall.tokens` | Python engine | 0.0189× | 0.0187–0.0193× | 9.70× | SLOWDOWN |
| holdout | `hold.findall.tokens` | Native C engine | 2.2323× | 2.0486–2.3601× | 0.21× | FASTER |
| holdout | `hold.findall.tokens` | Rust engine | 0.1669× | 0.1635–0.1710× | 1.46× | SLOWDOWN |
| holdout | `hold.finditer.groups` | Python engine | 0.0209× | 0.0203–0.0217× | 6.58× | SLOWDOWN |
| holdout | `hold.finditer.groups` | Native C engine | 2.0550× | 1.9980–2.1374× | 0.41× | FASTER |
| holdout | `hold.finditer.groups` | Rust engine | 0.1618× | 0.1567–0.1690× | 0.34× | SLOWDOWN |
| holdout | `hold.split.capture` | Python engine | 0.0170× | 0.0155–0.0187× | 7.83× | SLOWDOWN |
| holdout | `hold.split.capture` | Native C engine | 1.8266× | 1.8055–1.8469× | 0.20× | FASTER |
| holdout | `hold.split.capture` | Rust engine | 0.1042× | 0.0971–0.1127× | 1.29× | SLOWDOWN |
| holdout | `hold.sub.template` | Python engine | 0.0215× | 0.0210–0.0222× | 8.20× | SLOWDOWN |
| holdout | `hold.sub.template` | Native C engine | 2.0615× | 2.0126–2.1224× | 0.12× | FASTER |
| holdout | `hold.sub.template` | Rust engine | 0.0853× | 0.0834–0.0881× | 1.51× | SLOWDOWN |
| holdout | `hold.subn.callable` | Python engine | 0.0597× | 0.0562–0.0626× | 3.32× | SLOWDOWN |
| holdout | `hold.subn.callable` | Native C engine | 1.1510× | 1.0913–1.2094× | 0.25× | FASTER |
| holdout | `hold.subn.callable` | Rust engine | 0.1953× | 0.1906–0.2004× | 0.53× | SLOWDOWN |
| holdout | `hold.bytes.tokens` | Python engine | 0.0201× | 0.0194–0.0209× | 6.35× | SLOWDOWN |
| holdout | `hold.bytes.tokens` | Native C engine | 2.6011× | 2.5409–2.6790× | 0.18× | FASTER |
| holdout | `hold.bytes.tokens` | Rust engine | 0.3074× | 0.2990–0.3194× | 0.82× | SLOWDOWN |
| holdout | `hold.unicode.words` | Python engine | 0.0263× | 0.0247–0.0291× | 5.49× | SLOWDOWN |
| holdout | `hold.unicode.words` | Native C engine | 1.6232× | 1.5834–1.6739× | 0.20× | FASTER |
| holdout | `hold.unicode.words` | Rust engine | 0.1187× | 0.1124–0.1276× | 0.87× | SLOWDOWN |
| holdout | `hold.cold.compile-search` | Python engine | 0.0921× | 0.0905–0.0935× | 5.57× | SLOWDOWN |
| holdout | `hold.cold.compile-search` | Native C engine | 1.3328× | 1.3076–1.3560× | 1.77× | FASTER |
| holdout | `hold.cold.compile-search` | Rust engine | 1.1448× | 1.1219–1.1666× | 0.62× | FASTER |
| holdout | `hold.module.warm` | Python engine | 0.0742× | 0.0723–0.0768× | 4.29× | SLOWDOWN |
| holdout | `hold.module.warm` | Native C engine | 1.2378× | 1.2051–1.2812× | 0.07× | FASTER |
| holdout | `hold.module.warm` | Rust engine | 0.3166× | 0.3095–0.3263× | 0.07× | SLOWDOWN |
| holdout | `hold.empty.finditer` | Python engine | 0.0151× | 0.0146–0.0157× | 8.07× | SLOWDOWN |
| holdout | `hold.empty.finditer` | Native C engine | 2.3188× | 2.2676–2.4011× | 0.38× | FASTER |
| holdout | `hold.empty.finditer` | Rust engine | 0.1848× | 0.1798–0.1916× | 0.39× | SLOWDOWN |
| holdout | `hold.backref.fullmatch` | Python engine | 0.0193× | 0.0191–0.0195× | 6.45× | SLOWDOWN |
| holdout | `hold.backref.fullmatch` | Native C engine | 1.3432× | 1.3311–1.3547× | 0.08× | FASTER |
| holdout | `hold.backref.fullmatch` | Rust engine | 0.1750× | 0.1705–0.1780× | 0.06× | SLOWDOWN |
| holdout | `hold.conditional.match` | Python engine | 0.0279× | 0.0266–0.0302× | 6.57× | SLOWDOWN |
| holdout | `hold.conditional.match` | Native C engine | 1.4599× | 1.3890–1.5832× | 0.08× | FASTER |
| holdout | `hold.conditional.match` | Rust engine | 0.1584× | 0.1477–0.1731× | 0.06× | SLOWDOWN |
| holdout | `hold.atomic.search` | Python engine | 0.0315× | 0.0311–0.0319× | 4.26× | SLOWDOWN |
| holdout | `hold.atomic.search` | Native C engine | 1.3906× | 1.3767–1.4043× | 0.07× | FASTER |
| holdout | `hold.atomic.search` | Rust engine | 0.2066× | 0.2032–0.2095× | 0.07× | SLOWDOWN |
| holdout | `hold.byteslike.findall` | Python engine | 0.0166× | 0.0162–0.0171× | 7.78× | SLOWDOWN |
| holdout | `hold.byteslike.findall` | Native C engine | 2.5395× | 2.4854–2.6181× | 0.18× | FASTER |
| holdout | `hold.byteslike.findall` | Rust engine | 0.3148× | 0.3066–0.3259× | 0.75× | SLOWDOWN |
| holdout | `hold.unicode-name.search` | Python engine | 0.0465× | 0.0459–0.0470× | 3.17× | SLOWDOWN |
| holdout | `hold.unicode-name.search` | Native C engine | 1.4410× | 1.4282–1.4569× | 0.07× | FASTER |
| holdout | `hold.unicode-name.search` | Rust engine | 0.1875× | 0.1829–0.1903× | 0.10× | SLOWDOWN |
| holdout | `hold.ignorecase.findall` | Python engine | 0.0322× | 0.0316–0.0330× | 4.19× | SLOWDOWN |
| holdout | `hold.ignorecase.findall` | Native C engine | 1.6846× | 1.6591–1.7264× | 0.16× | FASTER |
| holdout | `hold.ignorecase.findall` | Rust engine | 0.4156× | 0.4022–0.4261× | 0.90× | SLOWDOWN |
| holdout | `hold.many.split` | Python engine | 0.0228× | 0.0221–0.0240× | 5.29× | SLOWDOWN |
| holdout | `hold.many.split` | Native C engine | 1.1432× | 1.0257–1.2437× | 0.20× | FASTER |
| holdout | `hold.many.split` | Rust engine | 0.1227× | 0.1147–0.1354× | 1.24× | SLOWDOWN |
| holdout | `hold.escape.bytes` | Python engine | 1.0070× | 1.0014–1.0147× | 0.68× | FASTER |
| holdout | `hold.escape.bytes` | Native C engine | 4.5121× | 4.0304–4.8064× | 0.32× | FASTER |
| holdout | `hold.escape.bytes` | Rust engine | 1.0048× | 0.9750–1.0221× | 0.68× | — |
| holdout | `hold.compile.only` | Python engine | 1.8258× | 1.7617–1.9306× | 0.55× | FASTER |
| holdout | `hold.compile.only` | Native C engine | 1.4083× | 1.3527–1.4961× | 2.11× | FASTER |
| holdout | `hold.compile.only` | Rust engine | 1.3984× | 1.3479–1.4794× | 0.60× | FASTER |
| holdout | `hold.scanner.search` | Python engine | 0.0196× | 0.0191–0.0200× | 5.82× | SLOWDOWN |
| holdout | `hold.scanner.search` | Native C engine | 1.2904× | 1.2697–1.3109× | 0.38× | FASTER |
| holdout | `hold.scanner.search` | Rust engine | 0.1153× | 0.1139–0.1165× | 0.22× | SLOWDOWN |
| holdout | `hold.match.surface` | Python engine | 0.0570× | 0.0564–0.0576× | 8.76× | SLOWDOWN |
| holdout | `hold.match.surface` | Native C engine | 1.0758× | 1.0105–1.1160× | 0.32× | FASTER |
| holdout | `hold.match.surface` | Rust engine | 0.1413× | 0.1399–0.1426× | 0.67× | SLOWDOWN |
| calibration | `cal.real.log` | Python engine | 0.0218× | 0.0216–0.0221× | 7.24× | SLOWDOWN |
| calibration | `cal.real.log` | Native C engine | 1.1501× | 1.1397–1.1611× | 0.35× | FASTER |
| calibration | `cal.real.log` | Rust engine | 0.1675× | 0.1646–0.1707× | 0.32× | SLOWDOWN |
| calibration | `cal.real.url` | Python engine | 0.0139× | 0.0133–0.0144× | 17.84× | SLOWDOWN |
| calibration | `cal.real.url` | Native C engine | 1.4727× | 1.4512–1.4967× | 0.11× | FASTER |
| calibration | `cal.real.url` | Rust engine | 0.0622× | 0.0610–0.0635× | 0.06× | SLOWDOWN |
| calibration | `cal.real.email` | Python engine | 0.0136× | 0.0133–0.0139× | 7.21× | SLOWDOWN |
| calibration | `cal.real.email` | Native C engine | 0.8657× | 0.7435–0.9916× | 0.12× | — |
| calibration | `cal.real.email` | Rust engine | 0.1397× | 0.1379–0.1415× | 1.93× | SLOWDOWN |
| calibration | `cal.real.datetime` | Python engine | 0.0113× | 0.0109–0.0116× | 18.78× | SLOWDOWN |
| calibration | `cal.real.datetime` | Native C engine | 1.2091× | 1.1933–1.2253× | 0.09× | FASTER |
| calibration | `cal.real.datetime` | Rust engine | 0.1508× | 0.1454–0.1553× | 0.06× | SLOWDOWN |
| calibration | `cal.real.version` | Python engine | 0.0158× | 0.0154–0.0160× | 17.88× | SLOWDOWN |
| calibration | `cal.real.version` | Native C engine | 2.0714× | 2.0462–2.0953× | 0.00× | FASTER |
| calibration | `cal.real.version` | Rust engine | 0.2232× | 0.2193–0.2265× | 0.00× | SLOWDOWN |
| calibration | `cal.real.uuid` | Python engine | 0.0136× | 0.0130–0.0144× | 13.65× | SLOWDOWN |
| calibration | `cal.real.uuid` | Native C engine | 1.5301× | 1.3874–1.6534× | 0.07× | FASTER |
| calibration | `cal.real.uuid` | Rust engine | 0.2133× | 0.1958–0.2292× | 0.06× | SLOWDOWN |
| calibration | `cal.real.ip` | Python engine | 0.0092× | 0.0088–0.0098× | 27.73× | SLOWDOWN |
| calibration | `cal.real.ip` | Native C engine | 1.1180× | 1.0759–1.1975× | 0.07× | FASTER |
| calibration | `cal.real.ip` | Rust engine | 0.1287× | 0.1221–0.1396× | 0.06× | SLOWDOWN |
| calibration | `cal.real.path` | Python engine | 0.0087× | 0.0085–0.0090× | 21.19× | SLOWDOWN |
| calibration | `cal.real.path` | Native C engine | 1.3315× | 1.3135–1.3469× | 0.12× | FASTER |
| calibration | `cal.real.path` | Rust engine | 0.1100× | 0.1079–0.1131× | 1.97× | SLOWDOWN |
| calibration | `cal.real.config` | Python engine | 0.0146× | 0.0130–0.0166× | 17.97× | SLOWDOWN |
| calibration | `cal.real.config` | Native C engine | 1.9207× | 1.6553–2.1938× | 0.37× | FASTER |
| calibration | `cal.real.config` | Rust engine | 0.1456× | 0.1330–0.1632× | 0.32× | SLOWDOWN |
| calibration | `cal.real.comments` | Python engine | 0.0205× | 0.0185–0.0231× | 5.07× | SLOWDOWN |
| calibration | `cal.real.comments` | Native C engine | 1.4119× | 1.2905–1.5803× | 0.14× | FASTER |
| calibration | `cal.real.comments` | Rust engine | 0.1878× | 0.1744–0.2087× | 1.91× | SLOWDOWN |
| calibration | `cal.real.whitespace` | Python engine | 0.0384× | 0.0349–0.0432× | 3.76× | SLOWDOWN |
| calibration | `cal.real.whitespace` | Native C engine | 1.3079× | 1.2146–1.4573× | 0.14× | FASTER |
| calibration | `cal.real.whitespace` | Rust engine | 0.2060× | 0.1961–0.2167× | 1.22× | SLOWDOWN |
| calibration | `cal.real.lines` | Python engine | 0.0284× | 0.0267–0.0308× | 6.25× | SLOWDOWN |
| calibration | `cal.real.lines` | Native C engine | 1.9100× | 1.8432–1.9944× | 0.15× | FASTER |
| calibration | `cal.real.lines` | Rust engine | 0.2223× | 0.1929–0.2575× | 1.23× | SLOWDOWN |
| calibration | `cal.real.markup` | Python engine | 0.0121× | 0.0113–0.0135× | 10.32× | SLOWDOWN |
| calibration | `cal.real.markup` | Native C engine | 1.2365× | 1.1664–1.3606× | 0.10× | FASTER |
| calibration | `cal.real.markup` | Rust engine | 0.1717× | 0.1638–0.1858× | 4.27× | SLOWDOWN |
| calibration | `cal.real.quotes` | Python engine | 0.0095× | 0.0089–0.0102× | 11.03× | SLOWDOWN |
| calibration | `cal.real.quotes` | Native C engine | 1.4863× | 1.3571–1.6142× | 0.10× | FASTER |
| calibration | `cal.real.quotes` | Rust engine | 0.1381× | 0.1335–0.1465× | 4.04× | SLOWDOWN |
| calibration | `cal.real.csv` | Python engine | 0.0089× | 0.0085–0.0095× | 13.75× | SLOWDOWN |
| calibration | `cal.real.csv` | Native C engine | 2.6441× | 2.5244–2.8163× | 0.29× | FASTER |
| calibration | `cal.real.csv` | Rust engine | 0.1041× | 0.0993–0.1112× | 1.41× | SLOWDOWN |
| calibration | `cal.branch.prefix` | Python engine | 0.0217× | 0.0210–0.0224× | 5.87× | SLOWDOWN |
| calibration | `cal.branch.prefix` | Native C engine | 1.2325× | 1.1267–1.3194× | 0.07× | FASTER |
| calibration | `cal.branch.prefix` | Rust engine | 0.1213× | 0.1167–0.1254× | 0.07× | SLOWDOWN |
| calibration | `cal.branch.miss` | Python engine | 0.0048× | 0.0045–0.0054× | 40.87× | SLOWDOWN |
| calibration | `cal.branch.miss` | Native C engine | 0.8956× | 0.8098–1.0084× | 0.00× | — |
| calibration | `cal.branch.miss` | Rust engine | 0.0921× | 0.0856–0.1021× | 0.00× | SLOWDOWN |
| calibration | `cal.repeat.nested` | Python engine | 0.0138× | 0.0135–0.0142× | 13.69× | SLOWDOWN |
| calibration | `cal.repeat.nested` | Native C engine | 1.3887× | 1.3551–1.4492× | 0.64× | FASTER |
| calibration | `cal.repeat.nested` | Rust engine | 0.0950× | 0.0917–0.0997× | 0.03× | SLOWDOWN |
| calibration | `cal.lines.records` | Python engine | 0.0123× | 0.0121–0.0126× | 12.06× | SLOWDOWN |
| calibration | `cal.lines.records` | Native C engine | 1.2104× | 1.1826–1.2541× | 0.38× | FASTER |
| calibration | `cal.lines.records` | Rust engine | 0.1413× | 0.1350–0.1478× | 0.33× | SLOWDOWN |
| calibration | `cal.block.dotall` | Python engine | 0.0162× | 0.0150–0.0179× | 5.51× | SLOWDOWN |
| calibration | `cal.block.dotall` | Native C engine | 1.5823× | 1.4715–1.7658× | 0.08× | FASTER |
| calibration | `cal.block.dotall` | Rust engine | 0.1340× | 0.1287–0.1414× | 0.06× | SLOWDOWN |
| calibration | `cal.pattern.verbose` | Python engine | 0.0083× | 0.0083–0.0084× | 13.98× | SLOWDOWN |
| calibration | `cal.pattern.verbose` | Native C engine | 2.2213× | 2.2020–2.2410× | 0.09× | FASTER |
| calibration | `cal.pattern.verbose` | Rust engine | 0.0973× | 0.0961–0.0983× | 0.06× | SLOWDOWN |
| calibration | `cal.mode.ascii` | Python engine | 0.0206× | 0.0203–0.0210× | 6.38× | SLOWDOWN |
| calibration | `cal.mode.ascii` | Native C engine | 1.1154× | 1.1026–1.1336× | 0.13× | FASTER |
| calibration | `cal.mode.ascii` | Rust engine | 0.0988× | 0.0967–0.1011× | 0.88× | SLOWDOWN |
| calibration | `cal.mode.casefold` | Python engine | 0.0236× | 0.0234–0.0237× | 4.30× | SLOWDOWN |
| calibration | `cal.mode.casefold` | Native C engine | 1.4254× | 1.4133–1.4364× | 0.20× | FASTER |
| calibration | `cal.mode.casefold` | Rust engine | 0.1078× | 0.1063–0.1091× | 0.93× | SLOWDOWN |
| calibration | `cal.mode.astral` | Python engine | 0.0250× | 0.0245–0.0256× | 5.40× | SLOWDOWN |
| calibration | `cal.mode.astral` | Native C engine | 1.6682× | 1.6329–1.7165× | 0.25× | FASTER |
| calibration | `cal.mode.astral` | Rust engine | 0.1069× | 0.1051–0.1097× | 0.92× | SLOWDOWN |
| calibration | `cal.look.negative-ahead` | Python engine | 0.0097× | 0.0095–0.0098× | 13.04× | SLOWDOWN |
| calibration | `cal.look.negative-ahead` | Native C engine | 0.9997× | 0.9230–1.0583× | 0.14× | — |
| calibration | `cal.look.negative-ahead` | Rust engine | 0.1873× | 0.1682–0.2029× | 1.50× | SLOWDOWN |
| calibration | `cal.look.negative-behind` | Python engine | 0.0203× | 0.0202–0.0204× | 6.99× | SLOWDOWN |
| calibration | `cal.look.negative-behind` | Native C engine | 1.1105× | 1.0896–1.1255× | 0.10× | FASTER |
| calibration | `cal.look.negative-behind` | Rust engine | 0.3281× | 0.3186–0.3353× | 1.04× | SLOWDOWN |
| calibration | `cal.bytes.replace` | Python engine | 0.0231× | 0.0227–0.0238× | 8.48× | SLOWDOWN |
| calibration | `cal.bytes.replace` | Native C engine | 1.0501× | 1.0160–1.0845× | 1.18× | FASTER |
| calibration | `cal.bytes.replace` | Rust engine | 0.0830× | 0.0816–0.0854× | 1.45× | SLOWDOWN |
| calibration | `cal.bytes.scan` | Python engine | 0.0168× | 0.0164–0.0171× | 7.67× | SLOWDOWN |
| calibration | `cal.bytes.scan` | Native C engine | 1.4929× | 1.4733–1.5147× | 0.40× | FASTER |
| calibration | `cal.bytes.scan` | Rust engine | 0.1018× | 0.1007–0.1031× | 0.36× | SLOWDOWN |
| calibration | `cal.compile.complex` | Python engine | 1.7150× | 1.6792–1.7538× | 0.41× | FASTER |
| calibration | `cal.compile.complex` | Native C engine | 1.3921× | 1.3591–1.4279× | 1.75× | FASTER |
| calibration | `cal.compile.complex` | Rust engine | 1.5058× | 1.4368–1.5557× | 0.52× | FASTER |
| calibration | `cal.module.replace` | Python engine | 0.0279× | 0.0277–0.0281× | 8.92× | SLOWDOWN |
| calibration | `cal.module.replace` | Native C engine | 1.2437× | 1.2168–1.2599× | 0.04× | FASTER |
| calibration | `cal.module.replace` | Rust engine | 0.1080× | 0.1073–0.1087× | 1.48× | SLOWDOWN |
| calibration | `cal.zero.boundary` | Python engine | 0.0130× | 0.0127–0.0135× | 9.11× | SLOWDOWN |
| calibration | `cal.zero.boundary` | Native C engine | 2.1800× | 2.0640–2.2795× | 0.43× | FASTER |
| calibration | `cal.zero.boundary` | Rust engine | 0.1744× | 0.1704–0.1796× | 0.43× | SLOWDOWN |
| calibration | `cal.dense.iter` | Python engine | 0.0222× | 0.0218–0.0227× | 4.65× | SLOWDOWN |
| calibration | `cal.dense.iter` | Native C engine | 1.6396× | 1.6122–1.6818× | 0.52× | FASTER |
| calibration | `cal.dense.iter` | Rust engine | 0.1707× | 0.1681–0.1743× | 0.50× | SLOWDOWN |
| calibration | `cal.capture.optional` | Python engine | 0.0157× | 0.0154–0.0164× | 13.14× | SLOWDOWN |
| calibration | `cal.capture.optional` | Native C engine | 1.3513× | 1.2959–1.4167× | 0.18× | FASTER |
| calibration | `cal.capture.optional` | Rust engine | 0.1920× | 0.1870–0.1990× | 2.15× | SLOWDOWN |
| calibration | `cal.split.limited` | Python engine | 0.0170× | 0.0169–0.0171× | 6.35× | SLOWDOWN |
| calibration | `cal.split.limited` | Native C engine | 1.5351× | 1.5239–1.5454× | 0.19× | FASTER |
| calibration | `cal.split.limited` | Rust engine | 0.1164× | 0.1150–0.1176× | 1.15× | SLOWDOWN |
| calibration | `cal.replace.limited` | Python engine | 0.0343× | 0.0337–0.0349× | 3.81× | SLOWDOWN |
| calibration | `cal.replace.limited` | Native C engine | 1.4349× | 1.3863–1.4772× | 0.15× | FASTER |
| calibration | `cal.replace.limited` | Rust engine | 0.1711× | 0.1678–0.1747× | 1.21× | SLOWDOWN |
| calibration | `cal.bytes.view-long` | Python engine | 0.0166× | 0.0164–0.0169× | 16.78× | SLOWDOWN |
| calibration | `cal.bytes.view-long` | Native C engine | 1.3293× | 1.2943–1.3635× | 0.60× | FASTER |
| calibration | `cal.bytes.view-long` | Rust engine | 0.5657× | 0.5572–0.5765× | 5.66× | SLOWDOWN |
| calibration | `cal.window.search` | Python engine | 0.0417× | 0.0412–0.0421× | 3.92× | SLOWDOWN |
| calibration | `cal.window.search` | Native C engine | 0.8149× | 0.7970–0.8365× | 0.18× | — |
| calibration | `cal.window.search` | Rust engine | 0.2332× | 0.2315–0.2349× | 0.17× | SLOWDOWN |
| calibration | `cal.window.findall` | Python engine | 0.0339× | 0.0330–0.0355× | 3.74× | SLOWDOWN |
| calibration | `cal.window.findall` | Native C engine | 1.1664× | 1.1014–1.2459× | 0.23× | FASTER |
| calibration | `cal.window.findall` | Rust engine | 0.3730× | 0.3623–0.3913× | 0.80× | SLOWDOWN |
| calibration | `cal.window.scanner` | Python engine | 0.0277× | 0.0268–0.0290× | 3.92× | SLOWDOWN |
| calibration | `cal.window.scanner` | Native C engine | 1.2185× | 1.1254–1.2923× | 0.33× | FASTER |
| calibration | `cal.window.scanner` | Rust engine | 0.1459× | 0.1416–0.1519× | 0.20× | SLOWDOWN |
| calibration | `cal.window.match` | Python engine | 0.0352× | 0.0349–0.0356× | 3.89× | SLOWDOWN |
| calibration | `cal.window.match` | Native C engine | 0.9446× | 0.8808–0.9878× | 0.18× | — |
| calibration | `cal.window.match` | Rust engine | 0.2106× | 0.2045–0.2150× | 0.17× | SLOWDOWN |
| calibration | `cal.literal.replace` | Python engine | 0.0465× | 0.0449–0.0487× | 8.20× | SLOWDOWN |
| calibration | `cal.literal.replace` | Native C engine | 1.4464× | 1.4046–1.5043× | 0.51× | FASTER |
| calibration | `cal.literal.replace` | Rust engine | 0.2623× | 0.2539–0.2742× | 0.62× | SLOWDOWN |
| calibration | `cal.template.repeat` | Python engine | 0.0269× | 0.0264–0.0274× | 5.36× | SLOWDOWN |
| calibration | `cal.template.repeat` | Native C engine | 1.6332× | 1.5937–1.6695× | 0.15× | FASTER |
| calibration | `cal.template.repeat` | Rust engine | 0.0822× | 0.0803–0.0842× | 1.29× | SLOWDOWN |
| calibration | `cal.match.miss` | Python engine | 0.0345× | 0.0340–0.0349× | 4.24× | SLOWDOWN |
| calibration | `cal.match.miss` | Native C engine | 1.1338× | 1.1223–1.1456× | 0.00× | FASTER |
| calibration | `cal.match.miss` | Rust engine | 0.1937× | 0.1919–0.1955× | 0.00× | SLOWDOWN |
| calibration | `cal.fullmatch.miss` | Python engine | 0.0198× | 0.0191–0.0210× | 9.31× | SLOWDOWN |
| calibration | `cal.fullmatch.miss` | Native C engine | 1.7221× | 1.6688–1.8245× | 0.00× | FASTER |
| calibration | `cal.fullmatch.miss` | Rust engine | 0.2897× | 0.2721–0.3110× | 0.00× | SLOWDOWN |
| holdout | `hold.real.log` | Python engine | 0.0223× | 0.0216–0.0232× | 7.39× | SLOWDOWN |
| holdout | `hold.real.log` | Native C engine | 1.1169× | 1.0003–1.2065× | 0.35× | FASTER |
| holdout | `hold.real.log` | Rust engine | 0.1700× | 0.1642–0.1774× | 0.32× | SLOWDOWN |
| holdout | `hold.real.url` | Python engine | 0.0157× | 0.0151–0.0166× | 17.65× | SLOWDOWN |
| holdout | `hold.real.url` | Native C engine | 1.4070× | 1.3586–1.4895× | 0.11× | FASTER |
| holdout | `hold.real.url` | Rust engine | 0.0523× | 0.0505–0.0555× | 0.06× | SLOWDOWN |
| holdout | `hold.real.email` | Python engine | 0.0111× | 0.0107–0.0116× | 8.62× | SLOWDOWN |
| holdout | `hold.real.email` | Native C engine | 1.2883× | 1.2094–1.3838× | 0.12× | FASTER |
| holdout | `hold.real.email` | Rust engine | 0.1305× | 0.1255–0.1373× | 2.05× | SLOWDOWN |
| holdout | `hold.real.datetime` | Python engine | 0.0136× | 0.0119–0.0158× | 21.76× | SLOWDOWN |
| holdout | `hold.real.datetime` | Native C engine | 1.4611× | 1.2905–1.6714× | 0.09× | FASTER |
| holdout | `hold.real.datetime` | Rust engine | 0.2432× | 0.2108–0.2845× | 0.06× | SLOWDOWN |
| holdout | `hold.real.version` | Python engine | 0.0143× | 0.0140–0.0146× | 18.50× | SLOWDOWN |
| holdout | `hold.real.version` | Native C engine | 1.4599× | 1.4331–1.4939× | 0.06× | FASTER |
| holdout | `hold.real.version` | Rust engine | 0.1280× | 0.1212–0.1335× | 0.06× | SLOWDOWN |
| holdout | `hold.real.uuid` | Python engine | 0.0120× | 0.0120–0.0121× | 13.88× | SLOWDOWN |
| holdout | `hold.real.uuid` | Native C engine | 1.4928× | 1.4835–1.5040× | 0.07× | FASTER |
| holdout | `hold.real.uuid` | Rust engine | 0.1983× | 0.1948–0.2012× | 0.06× | SLOWDOWN |
| holdout | `hold.real.ip` | Python engine | 0.0103× | 0.0102–0.0105× | 25.53× | SLOWDOWN |
| holdout | `hold.real.ip` | Native C engine | 1.1081× | 1.0951–1.1215× | 0.07× | FASTER |
| holdout | `hold.real.ip` | Rust engine | 0.0857× | 0.0845–0.0869× | 0.06× | SLOWDOWN |
| holdout | `hold.real.path` | Python engine | 0.0085× | 0.0080–0.0087× | 29.92× | SLOWDOWN |
| holdout | `hold.real.path` | Native C engine | 3.0957× | 3.0594–3.1264× | 0.12× | FASTER |
| holdout | `hold.real.path` | Rust engine | 0.0917× | 0.0893–0.0937× | 2.14× | SLOWDOWN |
| holdout | `hold.real.config` | Python engine | 0.0132× | 0.0131–0.0134× | 17.74× | SLOWDOWN |
| holdout | `hold.real.config` | Native C engine | 1.4345× | 1.3559–1.4921× | 0.37× | FASTER |
| holdout | `hold.real.config` | Rust engine | 0.0988× | 0.0977–0.0998× | 0.32× | SLOWDOWN |
| holdout | `hold.real.comments` | Python engine | 0.0216× | 0.0214–0.0219× | 5.08× | SLOWDOWN |
| holdout | `hold.real.comments` | Native C engine | 1.1979× | 1.1847–1.2093× | 0.14× | FASTER |
| holdout | `hold.real.comments` | Rust engine | 0.2044× | 0.1992–0.2080× | 2.33× | SLOWDOWN |
| holdout | `hold.real.whitespace` | Python engine | 0.0341× | 0.0339–0.0342× | 3.91× | SLOWDOWN |
| holdout | `hold.real.whitespace` | Native C engine | 1.3425× | 1.3295–1.3573× | 0.14× | FASTER |
| holdout | `hold.real.whitespace` | Rust engine | 0.1924× | 0.1906–0.1940× | 1.20× | SLOWDOWN |
| holdout | `hold.real.lines` | Python engine | 0.0258× | 0.0256–0.0261× | 6.25× | SLOWDOWN |
| holdout | `hold.real.lines` | Native C engine | 1.7328× | 1.6506–1.7831× | 0.14× | FASTER |
| holdout | `hold.real.lines` | Rust engine | 0.2067× | 0.2045–0.2091× | 1.17× | SLOWDOWN |
| holdout | `hold.real.markup` | Python engine | 0.0115× | 0.0114–0.0117× | 10.91× | SLOWDOWN |
| holdout | `hold.real.markup` | Native C engine | 1.2035× | 1.1965–1.2113× | 0.13× | FASTER |
| holdout | `hold.real.markup` | Rust engine | 0.1674× | 0.1656–0.1693× | 4.80× | SLOWDOWN |
| holdout | `hold.real.quotes` | Python engine | 0.0100× | 0.0097–0.0107× | 11.05× | SLOWDOWN |
| holdout | `hold.real.quotes` | Native C engine | 1.5021× | 1.4434–1.6117× | 0.10× | FASTER |
| holdout | `hold.real.quotes` | Rust engine | 0.1419× | 0.1363–0.1520× | 3.77× | SLOWDOWN |
| holdout | `hold.real.csv` | Python engine | 0.0081× | 0.0078–0.0085× | 13.67× | SLOWDOWN |
| holdout | `hold.real.csv` | Native C engine | 2.5218× | 2.3832–2.6829× | 0.30× | FASTER |
| holdout | `hold.real.csv` | Rust engine | 0.0955× | 0.0920–0.1008× | 1.75× | SLOWDOWN |
| holdout | `hold.branch.prefix` | Python engine | 0.0212× | 0.0205–0.0221× | 6.11× | SLOWDOWN |
| holdout | `hold.branch.prefix` | Native C engine | 1.2062× | 1.1744–1.2585× | 0.07× | FASTER |
| holdout | `hold.branch.prefix` | Rust engine | 0.1261× | 0.1203–0.1327× | 0.07× | SLOWDOWN |
| holdout | `hold.branch.miss` | Python engine | 0.0050× | 0.0049–0.0050× | 37.97× | SLOWDOWN |
| holdout | `hold.branch.miss` | Native C engine | 1.0425× | 0.9800–1.0788× | 0.00× | — |
| holdout | `hold.branch.miss` | Rust engine | 0.0992× | 0.0982–0.1001× | 0.00× | SLOWDOWN |
| holdout | `hold.repeat.nested` | Python engine | 0.0130× | 0.0127–0.0135× | 13.69× | SLOWDOWN |
| holdout | `hold.repeat.nested` | Native C engine | 1.2337× | 1.2062–1.2788× | 0.64× | FASTER |
| holdout | `hold.repeat.nested` | Rust engine | 0.0896× | 0.0873–0.0930× | 0.03× | SLOWDOWN |
| holdout | `hold.lines.records` | Python engine | 0.0123× | 0.0121–0.0125× | 12.06× | SLOWDOWN |
| holdout | `hold.lines.records` | Native C engine | 1.6250× | 1.5021–1.7015× | 0.38× | FASTER |
| holdout | `hold.lines.records` | Rust engine | 0.1437× | 0.1404–0.1465× | 0.33× | SLOWDOWN |
| holdout | `hold.block.dotall` | Python engine | 0.0143× | 0.0140–0.0145× | 5.51× | SLOWDOWN |
| holdout | `hold.block.dotall` | Native C engine | 1.4981× | 1.4781–1.5152× | 0.08× | FASTER |
| holdout | `hold.block.dotall` | Rust engine | 0.1334× | 0.1310–0.1355× | 0.06× | SLOWDOWN |
| holdout | `hold.pattern.verbose` | Python engine | 0.0080× | 0.0076–0.0088× | 14.89× | SLOWDOWN |
| holdout | `hold.pattern.verbose` | Native C engine | 3.2176× | 2.7145–3.7807× | 0.09× | FASTER |
| holdout | `hold.pattern.verbose` | Rust engine | 0.1150× | 0.1080–0.1284× | 0.06× | SLOWDOWN |
| holdout | `hold.mode.ascii` | Python engine | 0.0203× | 0.0200–0.0205× | 6.31× | SLOWDOWN |
| holdout | `hold.mode.ascii` | Native C engine | 1.1307× | 1.0751–1.1653× | 0.21× | FASTER |
| holdout | `hold.mode.ascii` | Rust engine | 0.0928× | 0.0921–0.0936× | 0.94× | SLOWDOWN |
| holdout | `hold.mode.casefold` | Python engine | 0.0273× | 0.0263–0.0291× | 4.22× | SLOWDOWN |
| holdout | `hold.mode.casefold` | Native C engine | 1.5054× | 1.4515–1.6038× | 0.18× | FASTER |
| holdout | `hold.mode.casefold` | Rust engine | 0.1219× | 0.1164–0.1307× | 0.92× | SLOWDOWN |
| holdout | `hold.mode.astral` | Python engine | 0.0243× | 0.0237–0.0248× | 5.40× | SLOWDOWN |
| holdout | `hold.mode.astral` | Native C engine | 1.5897× | 1.5635–1.6140× | 0.25× | FASTER |
| holdout | `hold.mode.astral` | Rust engine | 0.1028× | 0.1010–0.1042× | 0.92× | SLOWDOWN |
| holdout | `hold.look.negative-ahead` | Python engine | 0.0092× | 0.0089–0.0093× | 13.50× | SLOWDOWN |
| holdout | `hold.look.negative-ahead` | Native C engine | 0.9954× | 0.9133–1.0601× | 0.14× | — |
| holdout | `hold.look.negative-ahead` | Rust engine | 0.1994× | 0.1969–0.2021× | 1.58× | SLOWDOWN |
| holdout | `hold.look.negative-behind` | Python engine | 0.0208× | 0.0207–0.0209× | 6.99× | SLOWDOWN |
| holdout | `hold.look.negative-behind` | Native C engine | 1.3650× | 1.3533–1.3766× | 0.10× | FASTER |
| holdout | `hold.look.negative-behind` | Rust engine | 0.3390× | 0.3366–0.3408× | 1.04× | SLOWDOWN |
| holdout | `hold.bytes.replace` | Python engine | 0.0218× | 0.0217–0.0219× | 8.47× | SLOWDOWN |
| holdout | `hold.bytes.replace` | Native C engine | 1.0141× | 0.9951–1.0321× | 1.16× | — |
| holdout | `hold.bytes.replace` | Rust engine | 0.0804× | 0.0798–0.0809× | 1.45× | SLOWDOWN |
| holdout | `hold.bytes.scan` | Python engine | 0.0166× | 0.0164–0.0169× | 7.67× | SLOWDOWN |
| holdout | `hold.bytes.scan` | Native C engine | 1.4607× | 1.3917–1.5024× | 0.40× | FASTER |
| holdout | `hold.bytes.scan` | Rust engine | 0.1010× | 0.0997–0.1021× | 0.36× | SLOWDOWN |
| holdout | `hold.compile.complex` | Python engine | 1.7427× | 1.6778–1.7970× | 0.38× | FASTER |
| holdout | `hold.compile.complex` | Native C engine | 1.4375× | 1.4113–1.4664× | 1.77× | FASTER |
| holdout | `hold.compile.complex` | Rust engine | 1.3288× | 1.2972–1.3627× | 0.55× | FASTER |
| holdout | `hold.module.replace` | Python engine | 0.0278× | 0.0271–0.0287× | 8.92× | SLOWDOWN |
| holdout | `hold.module.replace` | Native C engine | 1.2458× | 1.1924–1.2980× | 0.04× | FASTER |
| holdout | `hold.module.replace` | Rust engine | 0.1084× | 0.1060–0.1120× | 1.48× | SLOWDOWN |
| holdout | `hold.zero.boundary` | Python engine | 0.0136× | 0.0133–0.0138× | 11.03× | SLOWDOWN |
| holdout | `hold.zero.boundary` | Native C engine | 2.1308× | 1.9950–2.2193× | 0.43× | FASTER |
| holdout | `hold.zero.boundary` | Rust engine | 0.1702× | 0.1685–0.1717× | 0.43× | SLOWDOWN |
| holdout | `hold.dense.iter` | Python engine | 0.0226× | 0.0220–0.0234× | 4.65× | SLOWDOWN |
| holdout | `hold.dense.iter` | Native C engine | 1.6164× | 1.5709–1.6724× | 0.52× | FASTER |
| holdout | `hold.dense.iter` | Rust engine | 0.1728× | 0.1692–0.1773× | 0.50× | SLOWDOWN |
| holdout | `hold.capture.optional` | Python engine | 0.0152× | 0.0146–0.0160× | 13.14× | SLOWDOWN |
| holdout | `hold.capture.optional` | Native C engine | 1.3168× | 1.2414–1.4001× | 0.18× | FASTER |
| holdout | `hold.capture.optional` | Rust engine | 0.1819× | 0.1745–0.1920× | 2.15× | SLOWDOWN |
| holdout | `hold.split.limited` | Python engine | 0.0175× | 0.0172–0.0177× | 6.35× | SLOWDOWN |
| holdout | `hold.split.limited` | Native C engine | 1.5138× | 1.4927–1.5359× | 0.19× | FASTER |
| holdout | `hold.split.limited` | Rust engine | 0.1167× | 0.1146–0.1187× | 1.22× | SLOWDOWN |
| holdout | `hold.replace.limited` | Python engine | 0.0324× | 0.0318–0.0330× | 3.81× | SLOWDOWN |
| holdout | `hold.replace.limited` | Native C engine | 1.3719× | 1.3547–1.3892× | 0.15× | FASTER |
| holdout | `hold.replace.limited` | Rust engine | 0.1580× | 0.1553–0.1607× | 1.21× | SLOWDOWN |
| holdout | `hold.bytes.view-long` | Python engine | 0.0161× | 0.0159–0.0163× | 16.78× | SLOWDOWN |
| holdout | `hold.bytes.view-long` | Native C engine | 1.3095× | 1.2757–1.3318× | 0.60× | FASTER |
| holdout | `hold.bytes.view-long` | Rust engine | 0.5475× | 0.5287–0.5588× | 5.66× | SLOWDOWN |
| holdout | `hold.window.search` | Python engine | 0.0405× | 0.0389–0.0436× | 3.92× | SLOWDOWN |
| holdout | `hold.window.search` | Native C engine | 0.8545× | 0.7992–0.9295× | 0.18× | — |
| holdout | `hold.window.search` | Rust engine | 0.2437× | 0.2348–0.2607× | 0.17× | SLOWDOWN |
| holdout | `hold.window.findall` | Python engine | 0.0272× | 0.0267–0.0277× | 3.74× | SLOWDOWN |
| holdout | `hold.window.findall` | Native C engine | 1.0565× | 1.0426–1.0682× | 0.22× | FASTER |
| holdout | `hold.window.findall` | Rust engine | 0.3265× | 0.3135–0.3369× | 0.67× | SLOWDOWN |
| holdout | `hold.window.scanner` | Python engine | 0.0285× | 0.0276–0.0302× | 3.92× | SLOWDOWN |
| holdout | `hold.window.scanner` | Native C engine | 1.2827× | 1.2297–1.3584× | 0.33× | FASTER |
| holdout | `hold.window.scanner` | Rust engine | 0.1452× | 0.1371–0.1536× | 0.20× | SLOWDOWN |
| holdout | `hold.window.match` | Python engine | 0.0329× | 0.0324–0.0333× | 3.89× | SLOWDOWN |
| holdout | `hold.window.match` | Native C engine | 0.8608× | 0.8391–0.8888× | 0.18× | — |
| holdout | `hold.window.match` | Rust engine | 0.2041× | 0.1962–0.2107× | 0.17× | SLOWDOWN |
| holdout | `hold.literal.replace` | Python engine | 0.0494× | 0.0458–0.0541× | 8.20× | SLOWDOWN |
| holdout | `hold.literal.replace` | Native C engine | 1.3928× | 1.2998–1.5348× | 0.51× | FASTER |
| holdout | `hold.literal.replace` | Rust engine | 0.2612× | 0.2352–0.2888× | 0.62× | SLOWDOWN |
| holdout | `hold.template.repeat` | Python engine | 0.0261× | 0.0255–0.0265× | 5.39× | SLOWDOWN |
| holdout | `hold.template.repeat` | Native C engine | 1.6253× | 1.5766–1.6596× | 0.14× | FASTER |
| holdout | `hold.template.repeat` | Rust engine | 0.0797× | 0.0776–0.0815× | 1.11× | SLOWDOWN |
| holdout | `hold.match.miss` | Python engine | 0.0359× | 0.0340–0.0393× | 4.24× | SLOWDOWN |
| holdout | `hold.match.miss` | Native C engine | 1.1816× | 1.1279–1.2781× | 0.00× | FASTER |
| holdout | `hold.match.miss` | Rust engine | 0.1991× | 0.1865–0.2185× | 0.00× | SLOWDOWN |
| holdout | `hold.fullmatch.miss` | Python engine | 0.0189× | 0.0184–0.0193× | 9.31× | SLOWDOWN |
| holdout | `hold.fullmatch.miss` | Native C engine | 1.6123× | 1.5235–1.6654× | 0.00× | FASTER |
| holdout | `hold.fullmatch.miss` | Rust engine | 0.2774× | 0.2602–0.2881× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-hit.00` | Python engine | 0.0400× | 0.0374–0.0433× | 20.93× | SLOWDOWN |
| calibration | `cal.large.literal-hit.00` | Native C engine | 1.1425× | 1.0928–1.2323× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.00` | Rust engine | 0.1563× | 0.1496–0.1681× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.01` | Python engine | 0.0418× | 0.0407–0.0427× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.01` | Native C engine | 1.0075× | 0.9330–1.0519× | 0.73× | — |
| calibration | `cal.large.literal-hit.01` | Rust engine | 0.1571× | 0.1516–0.1611× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.02` | Python engine | 0.0487× | 0.0468–0.0511× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.02` | Native C engine | 1.0979× | 1.0656–1.1492× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.02` | Rust engine | 0.1708× | 0.1590–0.1828× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.03` | Python engine | 0.0598× | 0.0589–0.0608× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.03` | Native C engine | 1.1049× | 1.0837–1.1254× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.03` | Rust engine | 0.1644× | 0.1264–0.1990× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.04` | Python engine | 0.0383× | 0.0358–0.0417× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.04` | Native C engine | 1.1247× | 1.0752–1.2091× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.04` | Rust engine | 0.1538× | 0.1440–0.1670× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.05` | Python engine | 0.0414× | 0.0405–0.0421× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.05` | Native C engine | 1.1644× | 1.1546–1.1742× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.05` | Rust engine | 0.1474× | 0.1460–0.1488× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.06` | Python engine | 0.0430× | 0.0385–0.0467× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.06` | Native C engine | 1.1198× | 1.1098–1.1299× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.06` | Rust engine | 0.1565× | 0.1362–0.1688× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.07` | Python engine | 0.0570× | 0.0558–0.0583× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.07` | Native C engine | 1.0738× | 0.9224–1.1711× | 0.73× | — |
| calibration | `cal.large.literal-hit.07` | Rust engine | 0.1808× | 0.1643–0.1952× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.08` | Python engine | 0.0379× | 0.0368–0.0386× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.08` | Native C engine | 1.1102× | 1.0993–1.1219× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.08` | Rust engine | 0.1499× | 0.1435–0.1539× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.09` | Python engine | 0.0386× | 0.0344–0.0412× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.09` | Native C engine | 1.1253× | 1.0995–1.1485× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.09` | Rust engine | 0.1533× | 0.1443–0.1600× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.10` | Python engine | 0.0474× | 0.0464–0.0482× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.10` | Native C engine | 1.1349× | 1.0941–1.1608× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.10` | Rust engine | 0.1495× | 0.1481–0.1509× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.11` | Python engine | 0.0592× | 0.0568–0.0611× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.11` | Native C engine | 1.1583× | 1.1216–1.1890× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.11` | Rust engine | 0.1505× | 0.1376–0.1587× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.12` | Python engine | 0.0392× | 0.0375–0.0421× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.12` | Native C engine | 1.1172× | 1.0001–1.2288× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.12` | Rust engine | 0.1540× | 0.1458–0.1663× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.13` | Python engine | 0.0419× | 0.0412–0.0426× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.13` | Native C engine | 1.1068× | 1.0447–1.1463× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.13` | Rust engine | 0.1625× | 0.1548–0.1671× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.14` | Python engine | 0.0508× | 0.0479–0.0557× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.14` | Native C engine | 1.0909× | 1.0415–1.1865× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.14` | Rust engine | 0.1524× | 0.1473–0.1566× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.15` | Python engine | 0.0592× | 0.0527–0.0682× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.15` | Native C engine | 1.2374× | 1.1196–1.4016× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.15` | Rust engine | 0.2171× | 0.1923–0.2516× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.16` | Python engine | 0.0435× | 0.0398–0.0490× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.16` | Native C engine | 1.2342× | 1.1371–1.3602× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.16` | Rust engine | 0.1589× | 0.1438–0.1805× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.17` | Python engine | 0.0412× | 0.0383–0.0455× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.17` | Native C engine | 0.9683× | 0.8087–1.1417× | 0.73× | — |
| calibration | `cal.large.literal-hit.17` | Rust engine | 0.1541× | 0.1417–0.1734× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.18` | Python engine | 0.0456× | 0.0437–0.0471× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.18` | Native C engine | 1.1482× | 1.1348–1.1609× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.18` | Rust engine | 0.1686× | 0.1588–0.1751× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.19` | Python engine | 0.0522× | 0.0513–0.0531× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.19` | Native C engine | 1.0576× | 1.0203–1.0856× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.19` | Rust engine | 0.1879× | 0.1813–0.1926× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.20` | Python engine | 0.0393× | 0.0389–0.0398× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.20` | Native C engine | 1.0608× | 0.9633–1.1208× | 0.73× | — |
| calibration | `cal.large.literal-hit.20` | Rust engine | 0.1431× | 0.1397–0.1460× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.21` | Python engine | 0.0409× | 0.0394–0.0423× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.21` | Native C engine | 1.0507× | 0.9950–1.0885× | 0.73× | — |
| calibration | `cal.large.literal-hit.21` | Rust engine | 0.1473× | 0.1389–0.1553× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.22` | Python engine | 0.0476× | 0.0469–0.0482× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.22` | Native C engine | 1.1505× | 1.1115–1.1764× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.22` | Rust engine | 0.1485× | 0.1440–0.1521× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.23` | Python engine | 0.0596× | 0.0583–0.0607× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.23` | Native C engine | 1.2481× | 1.1479–1.3139× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.23` | Rust engine | 0.1895× | 0.1679–0.2058× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.24` | Python engine | 0.0418× | 0.0394–0.0463× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.24` | Native C engine | 1.1369× | 1.0620–1.2658× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.24` | Rust engine | 0.1462× | 0.1254–0.1691× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.25` | Python engine | 0.0413× | 0.0406–0.0420× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.25` | Native C engine | 1.1412× | 1.1240–1.1565× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.25` | Rust engine | 0.1451× | 0.1425–0.1473× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.26` | Python engine | 0.0459× | 0.0442–0.0474× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.26` | Native C engine | 1.0406× | 1.0296–1.0506× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.26` | Rust engine | 0.1473× | 0.1113–0.1749× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.27` | Python engine | 0.0505× | 0.0490–0.0518× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.27` | Native C engine | 1.0469× | 1.0222–1.0657× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.27` | Rust engine | 0.1860× | 0.1829–0.1889× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.28` | Python engine | 0.0388× | 0.0372–0.0416× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.28` | Native C engine | 1.1402× | 1.0330–1.2544× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.28` | Rust engine | 0.1522× | 0.1459–0.1633× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.29` | Python engine | 0.0421× | 0.0400–0.0459× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.29` | Native C engine | 1.1690× | 1.1133–1.2715× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.29` | Rust engine | 0.1648× | 0.1594–0.1746× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.30` | Python engine | 0.0506× | 0.0453–0.0601× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.30` | Native C engine | 1.3467× | 1.2032–1.6057× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.30` | Rust engine | 0.1933× | 0.1724–0.2351× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-hit.31` | Python engine | 0.0571× | 0.0557–0.0585× | 21.47× | SLOWDOWN |
| calibration | `cal.large.literal-hit.31` | Native C engine | 1.0647× | 1.0494–1.0825× | 0.73× | FASTER |
| calibration | `cal.large.literal-hit.31` | Rust engine | 0.2025× | 0.1972–0.2069× | 0.67× | SLOWDOWN |
| calibration | `cal.large.literal-miss.00` | Python engine | 0.1503× | 0.1473–0.1522× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.00` | Native C engine | 1.2111× | 1.2073–1.2151× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.00` | Rust engine | 0.1896× | 0.1863–0.1918× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.01` | Python engine | 0.1692× | 0.1637–0.1726× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.01` | Native C engine | 1.3351× | 1.3217–1.3478× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.01` | Rust engine | 0.2031× | 0.2008–0.2054× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.02` | Python engine | 0.1977× | 0.1956–0.1996× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.02` | Native C engine | 1.4700× | 1.4599–1.4805× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.02` | Rust engine | 0.2216× | 0.2190–0.2242× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.03` | Python engine | 0.2650× | 0.2630–0.2672× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.03` | Native C engine | 1.6012× | 1.5769–1.6221× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.03` | Rust engine | 0.2657× | 0.2636–0.2679× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.04` | Python engine | 0.1458× | 0.1382–0.1507× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.04` | Native C engine | 1.1658× | 1.1603–1.1708× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.04` | Rust engine | 0.1889× | 0.1874–0.1902× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.05` | Python engine | 0.1693× | 0.1686–0.1700× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.05` | Native C engine | 1.3058× | 1.2976–1.3138× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.05` | Rust engine | 0.1997× | 0.1908–0.2052× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.06` | Python engine | 0.1827× | 0.1527–0.2006× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.06` | Native C engine | 1.1982× | 1.1903–1.2062× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.06` | Rust engine | 0.2262× | 0.2232–0.2287× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.07` | Python engine | 0.2541× | 0.2523–0.2560× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.07` | Native C engine | 1.1655× | 1.1152–1.2003× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.07` | Rust engine | 0.2689× | 0.2661–0.2718× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.08` | Python engine | 0.1466× | 0.1407–0.1506× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.08` | Native C engine | 1.1200× | 0.9923–1.1922× | 0.00× | — |
| calibration | `cal.large.literal-miss.08` | Rust engine | 0.1882× | 0.1867–0.1898× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.09` | Python engine | 0.1665× | 0.1644–0.1695× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.09` | Native C engine | 1.2680× | 1.2455–1.2973× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.09` | Rust engine | 0.1553× | 0.1481–0.1620× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.10` | Python engine | 0.1825× | 0.1489–0.2049× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.10` | Native C engine | 1.2179× | 1.1942–1.2469× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.10` | Rust engine | 0.2268× | 0.2181–0.2340× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.11` | Python engine | 0.2481× | 0.2409–0.2534× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.11` | Native C engine | 1.1517× | 1.1363–1.1662× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.11` | Rust engine | 0.2660× | 0.2602–0.2709× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.12` | Python engine | 0.1497× | 0.1488–0.1507× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.12` | Native C engine | 1.1937× | 1.1885–1.1989× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.12` | Rust engine | 0.1785× | 0.1596–0.1905× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.13` | Python engine | 0.1726× | 0.1717–0.1734× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.13` | Native C engine | 1.3100× | 1.3009–1.3188× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.13` | Rust engine | 0.2059× | 0.2041–0.2075× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.14` | Python engine | 0.1963× | 0.1943–0.1982× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.14` | Native C engine | 1.1993× | 1.1834–1.2139× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.14` | Rust engine | 0.2297× | 0.2285–0.2310× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.15` | Python engine | 0.2872× | 0.2853–0.2891× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.15` | Native C engine | 1.6816× | 1.6592–1.7094× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.15` | Rust engine | 0.2790× | 0.2758–0.2819× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.16` | Python engine | 0.1513× | 0.1462–0.1543× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.16` | Native C engine | 1.2053× | 1.1975–1.2124× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.16` | Rust engine | 0.1864× | 0.1806–0.1901× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.17` | Python engine | 0.1635× | 0.1615–0.1650× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.17` | Native C engine | 1.2484× | 1.2410–1.2564× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.17` | Rust engine | 0.1542× | 0.1471–0.1585× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.18` | Python engine | 0.2001× | 0.1979–0.2020× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.18` | Native C engine | 1.4552× | 1.4331–1.4762× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.18` | Rust engine | 0.2258× | 0.2229–0.2286× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.19` | Python engine | 0.2687× | 0.2651–0.2728× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.19` | Native C engine | 1.5809× | 1.5306–1.6250× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.19` | Rust engine | 0.2671× | 0.2633–0.2708× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.20` | Python engine | 0.1430× | 0.1353–0.1502× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.20` | Native C engine | 0.9749× | 0.6994–1.2038× | 0.00× | — |
| calibration | `cal.large.literal-miss.20` | Rust engine | 0.1797× | 0.1688–0.1894× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.21` | Python engine | 0.1573× | 0.1477–0.1654× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.21` | Native C engine | 1.1951× | 1.0666–1.2957× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.21` | Rust engine | 0.1533× | 0.1449–0.1601× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.22` | Python engine | 0.1927× | 0.1507–0.2352× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.22` | Native C engine | 1.4070× | 1.2662–1.5061× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.22` | Rust engine | 0.2392× | 0.2217–0.2701× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.23` | Python engine | 0.2444× | 0.2198–0.2605× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.23` | Native C engine | 1.5940× | 1.5540–1.6394× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.23` | Rust engine | 0.1356× | 0.1255–0.1439× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.24` | Python engine | 0.1370× | 0.1273–0.1460× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.24` | Native C engine | 1.0619× | 0.9516–1.1650× | 0.00× | — |
| calibration | `cal.large.literal-miss.24` | Rust engine | 0.1583× | 0.1517–0.1637× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.25` | Python engine | 0.1712× | 0.1701–0.1724× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.25` | Native C engine | 1.3197× | 1.3112–1.3278× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.25` | Rust engine | 0.1995× | 0.1908–0.2060× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.26` | Python engine | 0.2019× | 0.1996–0.2040× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.26` | Native C engine | 1.4735× | 1.4604–1.4858× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.26` | Rust engine | 0.2209× | 0.2073–0.2295× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.27` | Python engine | 0.2715× | 0.2534–0.3049× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.27` | Native C engine | 1.2747× | 1.2025–1.4240× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.27` | Rust engine | 0.2862× | 0.2704–0.3177× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.28` | Python engine | 0.1491× | 0.1446–0.1517× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.28` | Native C engine | 1.1510× | 1.1081–1.1776× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.28` | Rust engine | 0.1796× | 0.1633–0.1892× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.29` | Python engine | 0.1718× | 0.1662–0.1750× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.29` | Native C engine | 1.3341× | 1.3169–1.3462× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.29` | Rust engine | 0.2084× | 0.2066–0.2099× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.30` | Python engine | 0.1977× | 0.1963–0.1989× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.30` | Native C engine | 1.1146× | 1.0788–1.1360× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.30` | Rust engine | 0.2339× | 0.2325–0.2351× | 0.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.31` | Python engine | 0.2454× | 0.2261–0.2567× | 112.00× | SLOWDOWN |
| calibration | `cal.large.literal-miss.31` | Native C engine | 1.1773× | 1.1283–1.2087× | 0.00× | FASTER |
| calibration | `cal.large.literal-miss.31` | Rust engine | 0.2695× | 0.2672–0.2719× | 0.00× | SLOWDOWN |
| calibration | `cal.large.long-ending.00` | Python engine | 0.0473× | 0.0464–0.0481× | 2.95× | SLOWDOWN |
| calibration | `cal.large.long-ending.00` | Native C engine | 1.3084× | 1.0701–1.4792× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.00` | Rust engine | 0.2101× | 0.2069–0.2141× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.01` | Python engine | 0.0480× | 0.0469–0.0490× | 2.90× | SLOWDOWN |
| calibration | `cal.large.long-ending.01` | Native C engine | 1.4967× | 1.4674–1.5293× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.01` | Rust engine | 0.2107× | 0.2056–0.2161× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.02` | Python engine | 0.0482× | 0.0475–0.0489× | 2.95× | SLOWDOWN |
| calibration | `cal.large.long-ending.02` | Native C engine | 1.4376× | 1.3394–1.5092× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.02` | Rust engine | 0.2115× | 0.2082–0.2148× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.03` | Python engine | 0.0481× | 0.0473–0.0489× | 2.90× | SLOWDOWN |
| calibration | `cal.large.long-ending.03` | Native C engine | 1.4644× | 1.4439–1.4865× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.03` | Rust engine | 0.2124× | 0.2099–0.2151× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.04` | Python engine | 0.0594× | 0.0576–0.0610× | 2.95× | SLOWDOWN |
| calibration | `cal.large.long-ending.04` | Native C engine | 1.7729× | 1.7428–1.8055× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.04` | Rust engine | 0.2287× | 0.2261–0.2314× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.05` | Python engine | 0.0608× | 0.0595–0.0627× | 2.95× | SLOWDOWN |
| calibration | `cal.large.long-ending.05` | Native C engine | 1.7658× | 1.7230–1.8186× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.05` | Rust engine | 0.2274× | 0.2192–0.2355× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.06` | Python engine | 0.0634× | 0.0602–0.0698× | 2.95× | SLOWDOWN |
| calibration | `cal.large.long-ending.06` | Native C engine | 1.8772× | 1.7695–2.0709× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.06` | Rust engine | 0.2287× | 0.2044–0.2602× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.07` | Python engine | 0.0611× | 0.0605–0.0616× | 2.95× | SLOWDOWN |
| calibration | `cal.large.long-ending.07` | Native C engine | 1.6887× | 1.4887–1.8147× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.07` | Rust engine | 0.2290× | 0.2271–0.2307× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.08` | Python engine | 0.0954× | 0.0905–0.0993× | 2.98× | SLOWDOWN |
| calibration | `cal.large.long-ending.08` | Native C engine | 2.6835× | 2.6148–2.7468× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.08` | Rust engine | 0.2595× | 0.2559–0.2633× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.09` | Python engine | 0.0969× | 0.0945–0.0994× | 2.98× | SLOWDOWN |
| calibration | `cal.large.long-ending.09` | Native C engine | 2.6862× | 2.6056–2.7828× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.09` | Rust engine | 0.2584× | 0.2522–0.2655× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.10` | Python engine | 0.0967× | 0.0916–0.1001× | 2.98× | SLOWDOWN |
| calibration | `cal.large.long-ending.10` | Native C engine | 2.6467× | 2.5053–2.7468× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.10` | Rust engine | 0.2567× | 0.2520–0.2606× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.11` | Python engine | 0.0983× | 0.0955–0.1008× | 2.98× | SLOWDOWN |
| calibration | `cal.large.long-ending.11` | Native C engine | 2.6833× | 2.6033–2.7530× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.11` | Rust engine | 0.2616× | 0.2564–0.2665× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.12` | Python engine | 0.1878× | 0.1809–0.1946× | 2.98× | SLOWDOWN |
| calibration | `cal.large.long-ending.12` | Native C engine | 3.9680× | 3.7947–4.1470× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.12` | Rust engine | 0.2937× | 0.2855–0.3022× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.13` | Python engine | 0.2102× | 0.1943–0.2297× | 2.95× | SLOWDOWN |
| calibration | `cal.large.long-ending.13` | Native C engine | 3.4287× | 3.1104–3.7135× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.13` | Rust engine | 0.3034× | 0.2674–0.3479× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.14` | Python engine | 0.2109× | 0.1821–0.2470× | 2.98× | SLOWDOWN |
| calibration | `cal.large.long-ending.14` | Native C engine | 4.1681× | 3.4063–5.0759× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.14` | Rust engine | 0.3450× | 0.2968–0.4036× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.15` | Python engine | 0.1804× | 0.1665–0.1916× | 2.90× | SLOWDOWN |
| calibration | `cal.large.long-ending.15` | Native C engine | 3.4859× | 3.0144–3.8953× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.15` | Rust engine | 0.2795× | 0.2520–0.3000× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.16` | Python engine | 0.0483× | 0.0453–0.0532× | 2.95× | SLOWDOWN |
| calibration | `cal.large.long-ending.16` | Native C engine | 1.4217× | 1.2122–1.6460× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.16` | Rust engine | 0.2200× | 0.2063–0.2407× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.17` | Python engine | 0.0435× | 0.0404–0.0471× | 2.90× | SLOWDOWN |
| calibration | `cal.large.long-ending.17` | Native C engine | 1.3521× | 1.2059–1.4570× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.17` | Rust engine | 0.1949× | 0.1744–0.2134× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.18` | Python engine | 0.0470× | 0.0434–0.0507× | 2.95× | SLOWDOWN |
| calibration | `cal.large.long-ending.18` | Native C engine | 1.5671× | 1.4585–1.7272× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.18` | Rust engine | 0.2064× | 0.1810–0.2328× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.19` | Python engine | 0.0479× | 0.0458–0.0507× | 2.90× | SLOWDOWN |
| calibration | `cal.large.long-ending.19` | Native C engine | 1.4887× | 1.3421–1.6823× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.19` | Rust engine | 0.2157× | 0.2004–0.2397× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.20` | Python engine | 0.0584× | 0.0566–0.0602× | 2.95× | SLOWDOWN |
| calibration | `cal.large.long-ending.20` | Native C engine | 1.7945× | 1.7638–1.8265× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.20` | Rust engine | 0.2238× | 0.2156–0.2301× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.21` | Python engine | 0.0585× | 0.0536–0.0626× | 2.95× | SLOWDOWN |
| calibration | `cal.large.long-ending.21` | Native C engine | 1.8276× | 1.7825–1.9001× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.21` | Rust engine | 0.2083× | 0.1867–0.2264× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.22` | Python engine | 0.0661× | 0.0595–0.0748× | 2.95× | SLOWDOWN |
| calibration | `cal.large.long-ending.22` | Native C engine | 1.8995× | 1.7776–2.0728× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.22` | Rust engine | 0.2512× | 0.2249–0.2847× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.23` | Python engine | 0.0605× | 0.0592–0.0615× | 2.95× | SLOWDOWN |
| calibration | `cal.large.long-ending.23` | Native C engine | 1.8049× | 1.7642–1.8365× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.23` | Rust engine | 0.2305× | 0.2284–0.2327× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.24` | Python engine | 0.1006× | 0.0979–0.1033× | 2.98× | SLOWDOWN |
| calibration | `cal.large.long-ending.24` | Native C engine | 2.7668× | 2.7053–2.8303× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.24` | Rust engine | 0.2658× | 0.2606–0.2716× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.25` | Python engine | 0.0978× | 0.0935–0.1019× | 2.98× | SLOWDOWN |
| calibration | `cal.large.long-ending.25` | Native C engine | 2.6936× | 2.6254–2.7644× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.25` | Rust engine | 0.2623× | 0.2547–0.2700× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.26` | Python engine | 0.1030× | 0.0931–0.1171× | 2.98× | SLOWDOWN |
| calibration | `cal.large.long-ending.26` | Native C engine | 2.8766× | 2.6411–3.2016× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.26` | Rust engine | 0.2818× | 0.2609–0.3144× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.27` | Python engine | 0.1000× | 0.0917–0.1130× | 2.98× | SLOWDOWN |
| calibration | `cal.large.long-ending.27` | Native C engine | 2.6088× | 2.2863–2.9601× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.27` | Rust engine | 0.2522× | 0.2155–0.2983× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.28` | Python engine | 0.1814× | 0.1621–0.2026× | 2.98× | SLOWDOWN |
| calibration | `cal.large.long-ending.28` | Native C engine | 4.1180× | 3.8493–4.4954× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.28` | Rust engine | 0.2930× | 0.2705–0.3197× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.29` | Python engine | 0.1836× | 0.1651–0.2031× | 2.95× | SLOWDOWN |
| calibration | `cal.large.long-ending.29` | Native C engine | 3.4785× | 2.9527–4.0195× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.29` | Rust engine | 0.2866× | 0.2685–0.3113× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.30` | Python engine | 0.1798× | 0.1657–0.1996× | 2.98× | SLOWDOWN |
| calibration | `cal.large.long-ending.30` | Native C engine | 3.7072× | 3.0039–4.2796× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.30` | Rust engine | 0.3080× | 0.2880–0.3393× | 0.07× | SLOWDOWN |
| calibration | `cal.large.long-ending.31` | Python engine | 0.1855× | 0.1718–0.2017× | 2.90× | SLOWDOWN |
| calibration | `cal.large.long-ending.31` | Native C engine | 3.8364× | 3.3839–4.3086× | 0.07× | FASTER |
| calibration | `cal.large.long-ending.31` | Rust engine | 0.2889× | 0.2510–0.3296× | 0.07× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.00` | Python engine | 0.0123× | 0.0104–0.0147× | 8.61× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.00` | Native C engine | 1.3738× | 1.2242–1.5623× | 0.07× | FASTER |
| calibration | `cal.large.formatted-lines.00` | Rust engine | 0.2366× | 0.2074–0.2733× | 1.24× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.01` | Python engine | 0.0093× | 0.0089–0.0095× | 11.26× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.01` | Native C engine | 1.2599× | 1.2504–1.2709× | 0.11× | FASTER |
| calibration | `cal.large.formatted-lines.01` | Rust engine | 0.1902× | 0.1860–0.1935× | 2.29× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.02` | Python engine | 0.0089× | 0.0084–0.0094× | 15.69× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.02` | Native C engine | 1.2807× | 1.1821–1.3689× | 0.18× | FASTER |
| calibration | `cal.large.formatted-lines.02` | Rust engine | 0.2027× | 0.1967–0.2119× | 4.01× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.03` | Python engine | 0.0088× | 0.0084–0.0097× | 22.49× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.03` | Native C engine | 1.2846× | 1.2480–1.3123× | 0.29× | FASTER |
| calibration | `cal.large.formatted-lines.03` | Rust engine | 0.2158× | 0.2050–0.2364× | 6.31× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.04` | Python engine | 0.0111× | 0.0110–0.0113× | 8.61× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.04` | Native C engine | 1.2263× | 1.2118–1.2389× | 0.07× | FASTER |
| calibration | `cal.large.formatted-lines.04` | Rust engine | 0.1997× | 0.1969–0.2019× | 1.24× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.05` | Python engine | 0.0097× | 0.0096–0.0098× | 11.28× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.05` | Native C engine | 1.2260× | 1.1457–1.2784× | 0.11× | FASTER |
| calibration | `cal.large.formatted-lines.05` | Rust engine | 0.1988× | 0.1958–0.2014× | 2.21× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.06` | Python engine | 0.0088× | 0.0086–0.0089× | 15.69× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.06` | Native C engine | 1.2888× | 1.2749–1.3027× | 0.18× | FASTER |
| calibration | `cal.large.formatted-lines.06` | Rust engine | 0.2002× | 0.1965–0.2030× | 4.01× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.07` | Python engine | 0.0087× | 0.0085–0.0093× | 22.27× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.07` | Native C engine | 1.3587× | 1.3101–1.4477× | 0.30× | FASTER |
| calibration | `cal.large.formatted-lines.07` | Rust engine | 0.2049× | 0.1970–0.2179× | 6.74× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.08` | Python engine | 0.0111× | 0.0108–0.0118× | 8.62× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.08` | Native C engine | 1.2517× | 1.2109–1.3280× | 0.07× | FASTER |
| calibration | `cal.large.formatted-lines.08` | Rust engine | 0.2035× | 0.1987–0.2115× | 1.20× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.09` | Python engine | 0.0097× | 0.0094–0.0103× | 11.28× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.09` | Native C engine | 1.3046× | 1.2681–1.3691× | 0.11× | FASTER |
| calibration | `cal.large.formatted-lines.09` | Rust engine | 0.2020× | 0.1937–0.2129× | 2.21× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.10` | Python engine | 0.0090× | 0.0087–0.0095× | 15.78× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.10` | Native C engine | 1.1868× | 0.9305–1.3852× | 0.17× | — |
| calibration | `cal.large.formatted-lines.10` | Rust engine | 0.2116× | 0.2055–0.2221× | 3.74× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.11` | Python engine | 0.0087× | 0.0084–0.0093× | 22.30× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.11` | Native C engine | 1.3186× | 1.2334–1.4133× | 0.30× | FASTER |
| calibration | `cal.large.formatted-lines.11` | Rust engine | 0.2020× | 0.1906–0.2179× | 6.74× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.12` | Python engine | 0.0114× | 0.0109–0.0121× | 8.62× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.12` | Native C engine | 1.2668× | 1.2168–1.3559× | 0.07× | FASTER |
| calibration | `cal.large.formatted-lines.12` | Rust engine | 0.2008× | 0.1833–0.2193× | 1.20× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.13` | Python engine | 0.0094× | 0.0091–0.0096× | 11.26× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.13` | Native C engine | 1.2602× | 1.2475–1.2724× | 0.11× | FASTER |
| calibration | `cal.large.formatted-lines.13` | Rust engine | 0.1923× | 0.1883–0.1951× | 2.29× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.14` | Python engine | 0.0088× | 0.0088–0.0088× | 15.69× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.14` | Native C engine | 1.2846× | 1.2726–1.2963× | 0.18× | FASTER |
| calibration | `cal.large.formatted-lines.14` | Rust engine | 0.1998× | 0.1991–0.2005× | 4.01× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.15` | Python engine | 0.0086× | 0.0085–0.0086× | 22.27× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.15` | Native C engine | 1.3108× | 1.2892–1.3300× | 0.30× | FASTER |
| calibration | `cal.large.formatted-lines.15` | Rust engine | 0.1988× | 0.1934–0.2028× | 6.74× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.16` | Python engine | 0.0109× | 0.0108–0.0110× | 8.62× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.16` | Native C engine | 1.2129× | 1.2062–1.2197× | 0.07× | FASTER |
| calibration | `cal.large.formatted-lines.16` | Rust engine | 0.1992× | 0.1975–0.2004× | 1.20× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.17` | Python engine | 0.0096× | 0.0096–0.0097× | 11.28× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.17` | Native C engine | 1.2710× | 1.2591–1.2836× | 0.11× | FASTER |
| calibration | `cal.large.formatted-lines.17` | Rust engine | 0.1965× | 0.1922–0.2001× | 2.21× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.18` | Python engine | 0.0090× | 0.0089–0.0091× | 15.69× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.18` | Native C engine | 1.3027× | 1.2874–1.3163× | 0.18× | FASTER |
| calibration | `cal.large.formatted-lines.18` | Rust engine | 0.2003× | 0.1969–0.2033× | 4.01× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.19` | Python engine | 0.0085× | 0.0085–0.0086× | 22.27× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.19` | Native C engine | 1.3163× | 1.3012–1.3303× | 0.30× | FASTER |
| calibration | `cal.large.formatted-lines.19` | Rust engine | 0.2002× | 0.1960–0.2035× | 6.74× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.20` | Python engine | 0.0109× | 0.0108–0.0110× | 8.62× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.20` | Native C engine | 1.2074× | 1.1973–1.2166× | 0.07× | FASTER |
| calibration | `cal.large.formatted-lines.20` | Rust engine | 0.1985× | 0.1955–0.2008× | 1.20× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.21` | Python engine | 0.0095× | 0.0092–0.0097× | 11.26× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.21` | Native C engine | 1.2170× | 1.1441–1.2711× | 0.11× | FASTER |
| calibration | `cal.large.formatted-lines.21` | Rust engine | 0.1939× | 0.1912–0.1963× | 2.29× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.22` | Python engine | 0.0090× | 0.0089–0.0091× | 15.69× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.22` | Native C engine | 1.3024× | 1.2884–1.3167× | 0.18× | FASTER |
| calibration | `cal.large.formatted-lines.22` | Rust engine | 0.2028× | 0.2011–0.2049× | 4.01× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.23` | Python engine | 0.0086× | 0.0085–0.0087× | 22.27× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.23` | Native C engine | 1.3113× | 1.2955–1.3285× | 0.30× | FASTER |
| calibration | `cal.large.formatted-lines.23` | Rust engine | 0.2023× | 0.2009–0.2037× | 6.74× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.24` | Python engine | 0.0110× | 0.0106–0.0112× | 8.62× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.24` | Native C engine | 1.1826× | 1.0920–1.2368× | 0.07× | FASTER |
| calibration | `cal.large.formatted-lines.24` | Rust engine | 0.2004× | 0.1945–0.2052× | 1.20× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.25` | Python engine | 0.0096× | 0.0095–0.0097× | 11.28× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.25` | Native C engine | 1.1747× | 1.0773–1.2739× | 0.11× | FASTER |
| calibration | `cal.large.formatted-lines.25` | Rust engine | 0.1978× | 0.1941–0.2007× | 2.21× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.26` | Python engine | 0.0089× | 0.0088–0.0090× | 15.69× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.26` | Native C engine | 1.2576× | 1.1873–1.3029× | 0.18× | FASTER |
| calibration | `cal.large.formatted-lines.26` | Rust engine | 0.1980× | 0.1932–0.2016× | 4.01× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.27` | Python engine | 0.0089× | 0.0083–0.0100× | 22.16× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.27` | Native C engine | 1.4136× | 1.3131–1.5888× | 0.30× | FASTER |
| calibration | `cal.large.formatted-lines.27` | Rust engine | 0.2076× | 0.1915–0.2315× | 6.96× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.28` | Python engine | 0.0112× | 0.0107–0.0118× | 8.62× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.28` | Native C engine | 1.2557× | 1.2032–1.3340× | 0.07× | FASTER |
| calibration | `cal.large.formatted-lines.28` | Rust engine | 0.2043× | 0.1961–0.2157× | 1.20× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.29` | Python engine | 0.0097× | 0.0094–0.0103× | 11.28× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.29` | Native C engine | 1.2493× | 1.1167–1.3891× | 0.11× | FASTER |
| calibration | `cal.large.formatted-lines.29` | Rust engine | 0.1977× | 0.1800–0.2174× | 2.21× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.30` | Python engine | 0.0089× | 0.0088–0.0090× | 15.64× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.30` | Native C engine | 1.3076× | 1.2927–1.3222× | 0.18× | FASTER |
| calibration | `cal.large.formatted-lines.30` | Rust engine | 0.1979× | 0.1963–0.1994× | 4.14× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.31` | Python engine | 0.0081× | 0.0078–0.0084× | 22.27× | SLOWDOWN |
| calibration | `cal.large.formatted-lines.31` | Native C engine | 1.2120× | 1.0533–1.3573× | 0.30× | FASTER |
| calibration | `cal.large.formatted-lines.31` | Rust engine | 0.1923× | 0.1770–0.2038× | 6.74× | SLOWDOWN |
| calibration | `cal.large.prefix-check.00` | Python engine | 0.0289× | 0.0273–0.0320× | 4.26× | SLOWDOWN |
| calibration | `cal.large.prefix-check.00` | Native C engine | 1.4648× | 1.2746–1.6861× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.00` | Rust engine | 0.1941× | 0.1842–0.2134× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.01` | Python engine | 0.0283× | 0.0279–0.0286× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.01` | Native C engine | 1.4577× | 1.4392–1.4755× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.01` | Rust engine | 0.1796× | 0.1774–0.1818× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.02` | Python engine | 0.0290× | 0.0286–0.0294× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.02` | Native C engine | 1.4232× | 1.4024–1.4444× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.02` | Rust engine | 0.1789× | 0.1707–0.1846× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.03` | Python engine | 0.0626× | 0.0600–0.0650× | 2.64× | SLOWDOWN |
| calibration | `cal.large.prefix-check.03` | Native C engine | 1.3508× | 1.3065–1.4034× | 0.00× | FASTER |
| calibration | `cal.large.prefix-check.03` | Rust engine | 0.2221× | 0.1923–0.2419× | 0.00× | SLOWDOWN |
| calibration | `cal.large.prefix-check.04` | Python engine | 0.0258× | 0.0253–0.0262× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.04` | Native C engine | 1.4930× | 1.4840–1.5017× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.04` | Rust engine | 0.1653× | 0.1577–0.1709× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.05` | Python engine | 0.0271× | 0.0268–0.0274× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.05` | Native C engine | 1.4841× | 1.4674–1.5037× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.05` | Rust engine | 0.1724× | 0.1663–0.1769× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.06` | Python engine | 0.0278× | 0.0271–0.0284× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.06` | Native C engine | 1.4281× | 1.3985–1.4576× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.06` | Rust engine | 0.1793× | 0.1755–0.1821× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.07` | Python engine | 0.0618× | 0.0594–0.0638× | 2.64× | SLOWDOWN |
| calibration | `cal.large.prefix-check.07` | Native C engine | 1.3398× | 1.3058–1.3732× | 0.00× | FASTER |
| calibration | `cal.large.prefix-check.07` | Rust engine | 0.2370× | 0.2345–0.2395× | 0.00× | SLOWDOWN |
| calibration | `cal.large.prefix-check.08` | Python engine | 0.0271× | 0.0259–0.0291× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.08` | Native C engine | 1.4562× | 1.3373–1.5828× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.08` | Rust engine | 0.1789× | 0.1717–0.1926× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.09` | Python engine | 0.0282× | 0.0268–0.0309× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.09` | Native C engine | 1.5345× | 1.4625–1.6777× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.09` | Rust engine | 0.1853× | 0.1763–0.2035× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.10` | Python engine | 0.0276× | 0.0270–0.0282× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.10` | Native C engine | 1.4444× | 1.4205–1.4682× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.10` | Rust engine | 0.1800× | 0.1779–0.1823× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.11` | Python engine | 0.0609× | 0.0584–0.0633× | 2.64× | SLOWDOWN |
| calibration | `cal.large.prefix-check.11` | Native C engine | 1.3292× | 1.3012–1.3557× | 0.00× | FASTER |
| calibration | `cal.large.prefix-check.11` | Rust engine | 0.2376× | 0.2336–0.2411× | 0.00× | SLOWDOWN |
| calibration | `cal.large.prefix-check.12` | Python engine | 0.0262× | 0.0256–0.0268× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.12` | Native C engine | 1.5105× | 1.4944–1.5285× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.12` | Rust engine | 0.1707× | 0.1682–0.1735× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.13` | Python engine | 0.0294× | 0.0272–0.0328× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.13` | Native C engine | 1.5185× | 1.3914–1.6735× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.13` | Rust engine | 0.1909× | 0.1754–0.2134× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.14` | Python engine | 0.0292× | 0.0277–0.0319× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.14` | Native C engine | 1.5285× | 1.4501–1.6739× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.14` | Rust engine | 0.1900× | 0.1831–0.2018× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.15` | Python engine | 0.0654× | 0.0638–0.0669× | 2.64× | SLOWDOWN |
| calibration | `cal.large.prefix-check.15` | Native C engine | 1.3793× | 1.3627–1.3969× | 0.00× | FASTER |
| calibration | `cal.large.prefix-check.15` | Rust engine | 0.2456× | 0.2407–0.2509× | 0.00× | SLOWDOWN |
| calibration | `cal.large.prefix-check.16` | Python engine | 0.0277× | 0.0262–0.0296× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.16` | Native C engine | 1.5300× | 1.4015–1.6786× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.16` | Rust engine | 0.1818× | 0.1745–0.1924× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.17` | Python engine | 0.0287× | 0.0268–0.0318× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.17` | Native C engine | 1.4635× | 1.2186–1.7045× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.17` | Rust engine | 0.1804× | 0.1659–0.2015× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.18` | Python engine | 0.0295× | 0.0267–0.0341× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.18` | Native C engine | 1.4094× | 1.1027–1.7097× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.18` | Rust engine | 0.1783× | 0.1599–0.2004× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.19` | Python engine | 0.0656× | 0.0634–0.0683× | 2.64× | SLOWDOWN |
| calibration | `cal.large.prefix-check.19` | Native C engine | 1.1960× | 0.8670–1.4298× | 0.00× | — |
| calibration | `cal.large.prefix-check.19` | Rust engine | 0.2441× | 0.2344–0.2548× | 0.00× | SLOWDOWN |
| calibration | `cal.large.prefix-check.20` | Python engine | 0.0265× | 0.0259–0.0271× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.20` | Native C engine | 1.4785× | 1.4088–1.5339× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.20` | Rust engine | 0.1751× | 0.1725–0.1786× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.21` | Python engine | 0.0281× | 0.0261–0.0304× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.21` | Native C engine | 1.4820× | 1.2968–1.6482× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.21` | Rust engine | 0.1790× | 0.1613–0.1982× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.22` | Python engine | 0.0273× | 0.0259–0.0283× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.22` | Native C engine | 1.3474× | 1.2228–1.4297× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.22` | Rust engine | 0.1844× | 0.1735–0.1918× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.23` | Python engine | 0.0667× | 0.0630–0.0731× | 2.64× | SLOWDOWN |
| calibration | `cal.large.prefix-check.23` | Native C engine | 1.3571× | 1.1926–1.5287× | 0.00× | FASTER |
| calibration | `cal.large.prefix-check.23` | Rust engine | 0.2485× | 0.2351–0.2731× | 0.00× | SLOWDOWN |
| calibration | `cal.large.prefix-check.24` | Python engine | 0.0264× | 0.0246–0.0288× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.24` | Native C engine | 1.4742× | 1.3099–1.6410× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.24` | Rust engine | 0.1658× | 0.1500–0.1854× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.25` | Python engine | 0.0265× | 0.0255–0.0271× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.25` | Native C engine | 1.4502× | 1.4321–1.4664× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.25` | Rust engine | 0.1824× | 0.1778–0.1862× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.26` | Python engine | 0.0282× | 0.0273–0.0294× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.26` | Native C engine | 1.3944× | 1.2591–1.4822× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.26` | Rust engine | 0.1854× | 0.1815–0.1911× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.27` | Python engine | 0.0619× | 0.0588–0.0640× | 2.64× | SLOWDOWN |
| calibration | `cal.large.prefix-check.27` | Native C engine | 1.3467× | 1.3242–1.3721× | 0.00× | FASTER |
| calibration | `cal.large.prefix-check.27` | Rust engine | 0.2321× | 0.2228–0.2383× | 0.00× | SLOWDOWN |
| calibration | `cal.large.prefix-check.28` | Python engine | 0.0250× | 0.0248–0.0252× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.28` | Native C engine | 1.4567× | 1.4446–1.4676× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.28` | Rust engine | 0.1700× | 0.1678–0.1722× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.29` | Python engine | 0.0260× | 0.0257–0.0263× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.29` | Native C engine | 1.4381× | 1.3475–1.4986× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.29` | Rust engine | 0.1710× | 0.1662–0.1742× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.30` | Python engine | 0.0265× | 0.0261–0.0268× | 4.31× | SLOWDOWN |
| calibration | `cal.large.prefix-check.30` | Native C engine | 1.4416× | 1.4182–1.4657× | 0.07× | FASTER |
| calibration | `cal.large.prefix-check.30` | Rust engine | 0.1774× | 0.1758–0.1791× | 0.07× | SLOWDOWN |
| calibration | `cal.large.prefix-check.31` | Python engine | 0.0644× | 0.0632–0.0656× | 2.64× | SLOWDOWN |
| calibration | `cal.large.prefix-check.31` | Native C engine | 1.3342× | 1.2995–1.3650× | 0.00× | FASTER |
| calibration | `cal.large.prefix-check.31` | Rust engine | 0.2378× | 0.2337–0.2418× | 0.00× | SLOWDOWN |
| calibration | `cal.large.whole-check.00` | Python engine | 0.0204× | 0.0186–0.0238× | 10.00× | SLOWDOWN |
| calibration | `cal.large.whole-check.00` | Native C engine | 1.4790× | 1.3645–1.7212× | 0.69× | FASTER |
| calibration | `cal.large.whole-check.00` | Rust engine | 0.1525× | 0.1407–0.1768× | 0.06× | SLOWDOWN |
| calibration | `cal.large.whole-check.01` | Python engine | 0.0148× | 0.0146–0.0150× | 17.30× | SLOWDOWN |
| calibration | `cal.large.whole-check.01` | Native C engine | 1.2997× | 1.2885–1.3106× | 0.98× | FASTER |
| calibration | `cal.large.whole-check.01` | Rust engine | 0.0946× | 0.0927–0.0964× | 0.06× | SLOWDOWN |
| calibration | `cal.large.whole-check.02` | Python engine | 0.0131× | 0.0128–0.0135× | 15.80× | SLOWDOWN |
| calibration | `cal.large.whole-check.02` | Native C engine | 1.4209× | 1.3872–1.4539× | 0.80× | FASTER |
| calibration | `cal.large.whole-check.02` | Rust engine | 0.0866× | 0.0843–0.0887× | 0.03× | SLOWDOWN |
| calibration | `cal.large.whole-check.03` | Python engine | 0.0126× | 0.0121–0.0133× | 18.16× | SLOWDOWN |
| calibration | `cal.large.whole-check.03` | Native C engine | 1.5842× | 1.5138–1.6813× | 0.85× | FASTER |
| calibration | `cal.large.whole-check.03` | Rust engine | 0.0725× | 0.0691–0.0771× | 0.02× | SLOWDOWN |
| calibration | `cal.large.whole-check.04` | Python engine | 0.0196× | 0.0194–0.0197× | 10.00× | SLOWDOWN |
| calibration | `cal.large.whole-check.04` | Native C engine | 1.3207× | 1.2994–1.3407× | 0.69× | FASTER |
| calibration | `cal.large.whole-check.04` | Rust engine | 0.1098× | 0.1091–0.1106× | 0.06× | SLOWDOWN |
| calibration | `cal.large.whole-check.05` | Python engine | 0.0146× | 0.0145–0.0148× | 17.30× | SLOWDOWN |
| calibration | `cal.large.whole-check.05` | Native C engine | 1.3018× | 1.2875–1.3147× | 0.98× | FASTER |
| calibration | `cal.large.whole-check.05` | Rust engine | 0.0880× | 0.0867–0.0891× | 0.06× | SLOWDOWN |
| calibration | `cal.large.whole-check.06` | Python engine | 0.0135× | 0.0134–0.0136× | 17.52× | SLOWDOWN |
| calibration | `cal.large.whole-check.06` | Native C engine | 3.4211× | 3.1433–3.5831× | 0.83× | FASTER |
| calibration | `cal.large.whole-check.06` | Rust engine | 0.2377× | 0.2350–0.2402× | 0.00× | SLOWDOWN |
| calibration | `cal.large.whole-check.07` | Python engine | 0.0123× | 0.0120–0.0126× | 18.16× | SLOWDOWN |
| calibration | `cal.large.whole-check.07` | Native C engine | 1.5273× | 1.4875–1.5678× | 0.85× | FASTER |
| calibration | `cal.large.whole-check.07` | Rust engine | 0.0727× | 0.0710–0.0742× | 0.02× | SLOWDOWN |
| calibration | `cal.large.whole-check.08` | Python engine | 0.0200× | 0.0192–0.0211× | 10.00× | SLOWDOWN |
| calibration | `cal.large.whole-check.08` | Native C engine | 1.3244× | 1.2055–1.4330× | 0.69× | FASTER |
| calibration | `cal.large.whole-check.08` | Rust engine | 0.1099× | 0.1041–0.1172× | 0.06× | SLOWDOWN |
| calibration | `cal.large.whole-check.09` | Python engine | 0.0135× | 0.0134–0.0137× | 17.30× | SLOWDOWN |
| calibration | `cal.large.whole-check.09` | Native C engine | 1.2140× | 1.1000–1.2861× | 0.98× | FASTER |
| calibration | `cal.large.whole-check.09` | Rust engine | 0.1043× | 0.0959–0.1094× | 0.06× | SLOWDOWN |
| calibration | `cal.large.whole-check.10` | Python engine | 0.0131× | 0.0129–0.0133× | 15.80× | SLOWDOWN |
| calibration | `cal.large.whole-check.10` | Native C engine | 1.4147× | 1.3948–1.4376× | 0.80× | FASTER |
| calibration | `cal.large.whole-check.10` | Rust engine | 0.0836× | 0.0826–0.0846× | 0.03× | SLOWDOWN |
| calibration | `cal.large.whole-check.11` | Python engine | 0.0125× | 0.0122–0.0128× | 18.16× | SLOWDOWN |
| calibration | `cal.large.whole-check.11` | Native C engine | 1.5775× | 1.5533–1.6070× | 0.85× | FASTER |
| calibration | `cal.large.whole-check.11` | Rust engine | 0.0743× | 0.0726–0.0759× | 0.02× | SLOWDOWN |
| calibration | `cal.large.whole-check.12` | Python engine | 0.0199× | 0.0194–0.0207× | 10.00× | SLOWDOWN |
| calibration | `cal.large.whole-check.12` | Native C engine | 1.3390× | 1.3044–1.3873× | 0.69× | FASTER |
| calibration | `cal.large.whole-check.12` | Rust engine | 0.1086× | 0.1050–0.1138× | 0.06× | SLOWDOWN |
| calibration | `cal.large.whole-check.13` | Python engine | 0.0145× | 0.0138–0.0155× | 21.54× | SLOWDOWN |
| calibration | `cal.large.whole-check.13` | Native C engine | 3.5808× | 3.3841–3.8550× | 1.08× | FASTER |
| calibration | `cal.large.whole-check.13` | Rust engine | 0.2475× | 0.2358–0.2646× | 0.00× | SLOWDOWN |
| calibration | `cal.large.whole-check.14` | Python engine | 0.0123× | 0.0122–0.0124× | 15.80× | SLOWDOWN |
| calibration | `cal.large.whole-check.14` | Native C engine | 1.3796× | 1.3657–1.3926× | 0.80× | FASTER |
| calibration | `cal.large.whole-check.14` | Rust engine | 0.1009× | 0.1000–0.1017× | 0.03× | SLOWDOWN |
| calibration | `cal.large.whole-check.15` | Python engine | 0.0125× | 0.0120–0.0128× | 18.16× | SLOWDOWN |
| calibration | `cal.large.whole-check.15` | Native C engine | 1.5916× | 1.5644–1.6143× | 0.85× | FASTER |
| calibration | `cal.large.whole-check.15` | Rust engine | 0.0737× | 0.0717–0.0755× | 0.02× | SLOWDOWN |
| calibration | `cal.large.whole-check.16` | Python engine | 0.0200× | 0.0193–0.0211× | 10.00× | SLOWDOWN |
| calibration | `cal.large.whole-check.16` | Native C engine | 1.3495× | 1.3280–1.3790× | 0.69× | FASTER |
| calibration | `cal.large.whole-check.16` | Rust engine | 0.1052× | 0.0967–0.1107× | 0.06× | SLOWDOWN |
| calibration | `cal.large.whole-check.17` | Python engine | 0.0144× | 0.0140–0.0148× | 17.30× | SLOWDOWN |
| calibration | `cal.large.whole-check.17` | Native C engine | 1.2980× | 1.2758–1.3217× | 0.98× | FASTER |
| calibration | `cal.large.whole-check.17` | Rust engine | 0.0860× | 0.0840–0.0880× | 0.06× | SLOWDOWN |
| calibration | `cal.large.whole-check.18` | Python engine | 0.0129× | 0.0127–0.0131× | 15.80× | SLOWDOWN |
| calibration | `cal.large.whole-check.18` | Native C engine | 1.3821× | 1.2989–1.4439× | 0.80× | FASTER |
| calibration | `cal.large.whole-check.18` | Rust engine | 0.0830× | 0.0818–0.0842× | 0.03× | SLOWDOWN |
| calibration | `cal.large.whole-check.19` | Python engine | 0.0141× | 0.0123–0.0179× | 18.16× | SLOWDOWN |
| calibration | `cal.large.whole-check.19` | Native C engine | 1.7562× | 1.5305–2.1891× | 0.85× | FASTER |
| calibration | `cal.large.whole-check.19` | Rust engine | 0.0948× | 0.0829–0.1194× | 0.02× | SLOWDOWN |
| calibration | `cal.large.whole-check.20` | Python engine | 0.0159× | 0.0157–0.0161× | 15.03× | SLOWDOWN |
| calibration | `cal.large.whole-check.20` | Native C engine | 2.6988× | 2.4784–2.8233× | 0.76× | FASTER |
| calibration | `cal.large.whole-check.20` | Rust engine | 0.2588× | 0.2487–0.2652× | 0.00× | SLOWDOWN |
| calibration | `cal.large.whole-check.21` | Python engine | 0.0146× | 0.0145–0.0147× | 17.30× | SLOWDOWN |
| calibration | `cal.large.whole-check.21` | Native C engine | 1.3230× | 1.3060–1.3381× | 0.98× | FASTER |
| calibration | `cal.large.whole-check.21` | Rust engine | 0.0881× | 0.0874–0.0888× | 0.06× | SLOWDOWN |
| calibration | `cal.large.whole-check.22` | Python engine | 0.0123× | 0.0121–0.0126× | 15.80× | SLOWDOWN |
| calibration | `cal.large.whole-check.22` | Native C engine | 1.3866× | 1.3590–1.4118× | 0.80× | FASTER |
| calibration | `cal.large.whole-check.22` | Rust engine | 0.1008× | 0.0992–0.1027× | 0.03× | SLOWDOWN |
| calibration | `cal.large.whole-check.23` | Python engine | 0.0129× | 0.0123–0.0139× | 18.16× | SLOWDOWN |
| calibration | `cal.large.whole-check.23` | Native C engine | 1.6142× | 1.5427–1.7423× | 0.85× | FASTER |
| calibration | `cal.large.whole-check.23` | Rust engine | 0.0872× | 0.0832–0.0941× | 0.02× | SLOWDOWN |
| calibration | `cal.large.whole-check.24` | Python engine | 0.0198× | 0.0182–0.0217× | 10.00× | SLOWDOWN |
| calibration | `cal.large.whole-check.24` | Native C engine | 1.3175× | 1.1778–1.4718× | 0.69× | FASTER |
| calibration | `cal.large.whole-check.24` | Rust engine | 0.1026× | 0.0932–0.1137× | 0.06× | SLOWDOWN |
| calibration | `cal.large.whole-check.25` | Python engine | 0.0146× | 0.0145–0.0148× | 17.30× | SLOWDOWN |
| calibration | `cal.large.whole-check.25` | Native C engine | 1.2840× | 1.2267–1.3198× | 0.98× | FASTER |
| calibration | `cal.large.whole-check.25` | Rust engine | 0.0884× | 0.0877–0.0890× | 0.06× | SLOWDOWN |
| calibration | `cal.large.whole-check.26` | Python engine | 0.0129× | 0.0128–0.0130× | 15.80× | SLOWDOWN |
| calibration | `cal.large.whole-check.26` | Native C engine | 1.4178× | 1.4054–1.4311× | 0.80× | FASTER |
| calibration | `cal.large.whole-check.26` | Rust engine | 0.0821× | 0.0808–0.0833× | 0.03× | SLOWDOWN |
| calibration | `cal.large.whole-check.27` | Python engine | 0.0131× | 0.0130–0.0133× | 19.08× | SLOWDOWN |
| calibration | `cal.large.whole-check.27` | Native C engine | 3.7868× | 3.7333–3.8380× | 0.87× | FASTER |
| calibration | `cal.large.whole-check.27` | Rust engine | 0.2400× | 0.2376–0.2425× | 0.00× | SLOWDOWN |
| calibration | `cal.large.whole-check.28` | Python engine | 0.0193× | 0.0191–0.0195× | 10.00× | SLOWDOWN |
| calibration | `cal.large.whole-check.28` | Native C engine | 1.3484× | 1.3300–1.3684× | 0.69× | FASTER |
| calibration | `cal.large.whole-check.28` | Rust engine | 0.1019× | 0.1004–0.1034× | 0.06× | SLOWDOWN |
| calibration | `cal.large.whole-check.29` | Python engine | 0.0145× | 0.0144–0.0146× | 17.30× | SLOWDOWN |
| calibration | `cal.large.whole-check.29` | Native C engine | 1.3062× | 1.2988–1.3147× | 0.98× | FASTER |
| calibration | `cal.large.whole-check.29` | Rust engine | 0.0827× | 0.0821–0.0832× | 0.06× | SLOWDOWN |
| calibration | `cal.large.whole-check.30` | Python engine | 0.0129× | 0.0127–0.0131× | 15.80× | SLOWDOWN |
| calibration | `cal.large.whole-check.30` | Native C engine | 1.4162× | 1.3951–1.4397× | 0.80× | FASTER |
| calibration | `cal.large.whole-check.30` | Rust engine | 0.0756× | 0.0742–0.0769× | 0.03× | SLOWDOWN |
| calibration | `cal.large.whole-check.31` | Python engine | 0.0121× | 0.0117–0.0124× | 18.16× | SLOWDOWN |
| calibration | `cal.large.whole-check.31` | Native C engine | 1.5210× | 1.4818–1.5566× | 0.85× | FASTER |
| calibration | `cal.large.whole-check.31` | Rust engine | 0.0902× | 0.0880–0.0925× | 0.02× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.00` | Python engine | 0.0141× | 0.0139–0.0142× | 12.80× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.00` | Native C engine | 1.3986× | 1.3878–1.4099× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.00` | Rust engine | 0.1648× | 0.1636–0.1662× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.01` | Python engine | 0.0123× | 0.0122–0.0124× | 14.65× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.01` | Native C engine | 1.7125× | 1.6952–1.7338× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.01` | Rust engine | 0.1682× | 0.1654–0.1704× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.02` | Python engine | 0.0107× | 0.0106–0.0108× | 18.35× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.02` | Native C engine | 2.1807× | 2.1493–2.2135× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.02` | Rust engine | 0.1752× | 0.1732–0.1772× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.03` | Python engine | 0.0101× | 0.0100–0.0102× | 25.75× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.03` | Native C engine | 2.9590× | 2.8789–3.0547× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.03` | Rust engine | 0.1800× | 0.1754–0.1835× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.04` | Python engine | 0.0142× | 0.0138–0.0147× | 12.80× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.04` | Native C engine | 1.3788× | 1.2630–1.4526× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.04` | Rust engine | 0.1567× | 0.1522–0.1631× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.05` | Python engine | 0.0124× | 0.0123–0.0125× | 14.65× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.05` | Native C engine | 1.6372× | 1.4607–1.7395× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.05` | Rust engine | 0.1592× | 0.1563–0.1615× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.06` | Python engine | 0.0107× | 0.0107–0.0108× | 18.35× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.06` | Native C engine | 2.1931× | 2.1476–2.2350× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.06` | Rust engine | 0.1680× | 0.1646–0.1702× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.07` | Python engine | 0.0098× | 0.0095–0.0100× | 25.75× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.07` | Native C engine | 2.9331× | 2.8983–2.9684× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.07` | Rust engine | 0.1809× | 0.1794–0.1824× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.08` | Python engine | 0.0143× | 0.0136–0.0153× | 12.80× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.08` | Native C engine | 1.4194× | 1.3083–1.5270× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.08` | Rust engine | 0.1573× | 0.1518–0.1663× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.09` | Python engine | 0.0122× | 0.0120–0.0123× | 14.65× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.09` | Native C engine | 1.7197× | 1.6960–1.7368× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.09` | Rust engine | 0.1575× | 0.1549–0.1599× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.10` | Python engine | 0.0111× | 0.0106–0.0121× | 18.35× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.10` | Native C engine | 2.2696× | 2.1582–2.4573× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.10` | Rust engine | 0.1742× | 0.1656–0.1894× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.11` | Python engine | 0.0106× | 0.0095–0.0120× | 25.75× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.11` | Native C engine | 3.1829× | 2.9185–3.6105× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.11` | Rust engine | 0.1973× | 0.1796–0.2233× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.12` | Python engine | 0.0149× | 0.0141–0.0159× | 12.80× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.12` | Native C engine | 1.5216× | 1.4428–1.6159× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.12` | Rust engine | 0.1625× | 0.1536–0.1736× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.13` | Python engine | 0.0125× | 0.0123–0.0128× | 14.65× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.13` | Native C engine | 1.7466× | 1.7152–1.7941× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.13` | Rust engine | 0.1600× | 0.1554–0.1628× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.14` | Python engine | 0.0107× | 0.0106–0.0108× | 18.35× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.14` | Native C engine | 2.1904× | 2.1617–2.2172× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.14` | Rust engine | 0.1625× | 0.1548–0.1681× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.15` | Python engine | 0.0100× | 0.0099–0.0101× | 25.75× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.15` | Native C engine | 2.9279× | 2.8414–3.0028× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.15` | Rust engine | 0.1757× | 0.1667–0.1818× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.16` | Python engine | 0.0142× | 0.0141–0.0143× | 12.80× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.16` | Native C engine | 1.4334× | 1.4247–1.4425× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.16` | Rust engine | 0.1548× | 0.1536–0.1559× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.17` | Python engine | 0.0125× | 0.0124–0.0126× | 14.65× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.17` | Native C engine | 1.7116× | 1.6950–1.7270× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.17` | Rust engine | 0.1604× | 0.1585–0.1623× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.18` | Python engine | 0.0107× | 0.0106–0.0108× | 18.35× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.18` | Native C engine | 2.1748× | 2.0920–2.2341× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.18` | Rust engine | 0.1685× | 0.1668–0.1697× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.19` | Python engine | 0.0099× | 0.0098–0.0101× | 25.75× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.19` | Native C engine | 2.7937× | 2.5526–2.9681× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.19` | Rust engine | 0.1792× | 0.1737–0.1831× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.20` | Python engine | 0.0140× | 0.0137–0.0143× | 12.80× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.20` | Native C engine | 1.4523× | 1.4378–1.4686× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.20` | Rust engine | 0.1543× | 0.1520–0.1565× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.21` | Python engine | 0.0128× | 0.0120–0.0139× | 14.65× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.21` | Native C engine | 1.8028× | 1.7066–1.9510× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.21` | Rust engine | 0.1631× | 0.1473–0.1808× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.22` | Python engine | 0.0106× | 0.0103–0.0108× | 18.35× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.22` | Native C engine | 2.2066× | 2.1838–2.2332× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.22` | Rust engine | 0.1675× | 0.1636–0.1701× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.23` | Python engine | 0.0100× | 0.0098–0.0102× | 25.75× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.23` | Native C engine | 2.9566× | 2.8863–3.0216× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.23` | Rust engine | 0.1796× | 0.1772–0.1819× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.24` | Python engine | 0.0154× | 0.0140–0.0172× | 12.80× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.24` | Native C engine | 1.4544× | 1.2972–1.6113× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.24` | Rust engine | 0.1575× | 0.1460–0.1679× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.25` | Python engine | 0.0121× | 0.0119–0.0123× | 14.65× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.25` | Native C engine | 1.7043× | 1.6903–1.7180× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.25` | Rust engine | 0.1576× | 0.1539–0.1605× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.26` | Python engine | 0.0107× | 0.0106–0.0109× | 18.35× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.26` | Native C engine | 2.1490× | 2.1008–2.1922× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.26` | Rust engine | 0.1678× | 0.1641–0.1706× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.27` | Python engine | 0.0100× | 0.0100–0.0101× | 25.75× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.27` | Native C engine | 2.9625× | 2.9091–3.0138× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.27` | Rust engine | 0.1791× | 0.1781–0.1801× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.28` | Python engine | 0.0142× | 0.0142–0.0143× | 12.80× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.28` | Native C engine | 1.4393× | 1.4303–1.4492× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.28` | Rust engine | 0.1491× | 0.1483–0.1498× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.29` | Python engine | 0.0130× | 0.0123–0.0141× | 14.65× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.29` | Native C engine | 1.7879× | 1.7110–1.9384× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.29` | Rust engine | 0.1575× | 0.1412–0.1770× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.30` | Python engine | 0.0106× | 0.0105–0.0108× | 18.35× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.30` | Native C engine | 2.1887× | 2.1666–2.2106× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.30` | Rust engine | 0.1631× | 0.1607–0.1649× | 0.06× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.31` | Python engine | 0.0100× | 0.0100–0.0101× | 25.75× | SLOWDOWN |
| calibration | `cal.large.nearby-capture.31` | Native C engine | 2.9762× | 2.9297–3.0202× | 0.08× | FASTER |
| calibration | `cal.large.nearby-capture.31` | Rust engine | 0.1788× | 0.1769–0.1805× | 0.06× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.00` | Python engine | 0.0186× | 0.0184–0.0189× | 8.60× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.00` | Native C engine | 1.8389× | 1.8108–1.8715× | 0.10× | FASTER |
| calibration | `cal.large.findall-tokens.00` | Rust engine | 0.2039× | 0.2016–0.2070× | 0.77× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.01` | Python engine | 0.0197× | 0.0191–0.0208× | 9.47× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.01` | Native C engine | 2.1404× | 2.0766–2.2442× | 0.17× | FASTER |
| calibration | `cal.large.findall-tokens.01` | Rust engine | 0.1739× | 0.1677–0.1835× | 1.78× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.02` | Python engine | 0.0196× | 0.0195–0.0198× | 10.69× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.02` | Native C engine | 2.2275× | 2.2054–2.2474× | 0.29× | FASTER |
| calibration | `cal.large.findall-tokens.02` | Rust engine | 0.1746× | 0.1730–0.1761× | 3.29× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.03` | Python engine | 0.0193× | 0.0192–0.0196× | 12.31× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.03` | Native C engine | 2.3428× | 2.3147–2.3776× | 0.45× | FASTER |
| calibration | `cal.large.findall-tokens.03` | Rust engine | 0.1726× | 0.1697–0.1749× | 5.23× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.04` | Python engine | 0.0202× | 0.0192–0.0221× | 8.55× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.04` | Native C engine | 1.9232× | 1.8276–2.1068× | 0.11× | FASTER |
| calibration | `cal.large.findall-tokens.04` | Rust engine | 0.1447× | 0.1369–0.1590× | 1.08× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.05` | Python engine | 0.0199× | 0.0193–0.0207× | 9.42× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.05` | Native C engine | 2.1559× | 2.0938–2.2497× | 0.17× | FASTER |
| calibration | `cal.large.findall-tokens.05` | Rust engine | 0.1455× | 0.1432–0.1478× | 2.06× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.06` | Python engine | 0.0194× | 0.0192–0.0197× | 10.63× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.06` | Native C engine | 2.2494× | 2.2278–2.2721× | 0.29× | FASTER |
| calibration | `cal.large.findall-tokens.06` | Rust engine | 0.1533× | 0.1516–0.1554× | 3.57× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.07` | Python engine | 0.0191× | 0.0190–0.0192× | 12.31× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.07` | Native C engine | 2.3379× | 2.3119–2.3626× | 0.45× | FASTER |
| calibration | `cal.large.findall-tokens.07` | Rust engine | 0.1680× | 0.1624–0.1719× | 5.23× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.08` | Python engine | 0.0193× | 0.0191–0.0195× | 8.57× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.08` | Native C engine | 1.8481× | 1.8365–1.8595× | 0.10× | FASTER |
| calibration | `cal.large.findall-tokens.08` | Rust engine | 0.1520× | 0.1500–0.1537× | 1.00× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.09` | Python engine | 0.0190× | 0.0186–0.0194× | 9.42× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.09` | Native C engine | 2.0052× | 1.8104–2.1317× | 0.17× | FASTER |
| calibration | `cal.large.findall-tokens.09` | Rust engine | 0.1418× | 0.1372–0.1464× | 2.06× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.10` | Python engine | 0.0188× | 0.0183–0.0196× | 10.78× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.10` | Native C engine | 2.2821× | 2.2211–2.3858× | 0.28× | FASTER |
| calibration | `cal.large.findall-tokens.10` | Rust engine | 0.2093× | 0.1983–0.2213× | 2.88× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.11` | Python engine | 0.0193× | 0.0190–0.0195× | 12.31× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.11` | Native C engine | 2.3560× | 2.3207–2.3945× | 0.45× | FASTER |
| calibration | `cal.large.findall-tokens.11` | Rust engine | 0.1742× | 0.1722–0.1763× | 5.23× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.12` | Python engine | 0.0191× | 0.0189–0.0194× | 8.57× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.12` | Native C engine | 1.8360× | 1.8127–1.8545× | 0.10× | FASTER |
| calibration | `cal.large.findall-tokens.12` | Rust engine | 0.1523× | 0.1505–0.1539× | 1.00× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.13` | Python engine | 0.0192× | 0.0190–0.0194× | 9.42× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.13` | Native C engine | 2.1096× | 2.0892–2.1333× | 0.17× | FASTER |
| calibration | `cal.large.findall-tokens.13` | Rust engine | 0.1425× | 0.1405–0.1443× | 2.06× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.14` | Python engine | 0.0195× | 0.0191–0.0201× | 10.63× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.14` | Native C engine | 2.3025× | 2.2450–2.3985× | 0.29× | FASTER |
| calibration | `cal.large.findall-tokens.14` | Rust engine | 0.1547× | 0.1509–0.1607× | 3.57× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.15` | Python engine | 0.0192× | 0.0191–0.0193× | 12.22× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.15` | Native C engine | 2.3135× | 2.2911–2.3339× | 0.45× | FASTER |
| calibration | `cal.large.findall-tokens.15` | Rust engine | 0.1520× | 0.1499–0.1539× | 5.56× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.16` | Python engine | 0.0207× | 0.0193–0.0225× | 8.55× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.16` | Native C engine | 1.9594× | 1.8555–2.0898× | 0.11× | FASTER |
| calibration | `cal.large.findall-tokens.16` | Rust engine | 0.1461× | 0.1364–0.1585× | 1.08× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.17` | Python engine | 0.0178× | 0.0177–0.0179× | 9.50× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.17` | Native C engine | 2.0706× | 2.0564–2.0858× | 0.16× | FASTER |
| calibration | `cal.large.findall-tokens.17` | Rust engine | 0.1946× | 0.1882–0.2004× | 1.65× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.18` | Python engine | 0.0206× | 0.0189–0.0228× | 10.68× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.18` | Native C engine | 2.1837× | 1.8526–2.5448× | 0.29× | FASTER |
| calibration | `cal.large.findall-tokens.18` | Rust engine | 0.1834× | 0.1701–0.2038× | 3.34× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.19` | Python engine | 0.0191× | 0.0189–0.0193× | 12.31× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.19` | Native C engine | 2.3298× | 2.3001–2.3586× | 0.45× | FASTER |
| calibration | `cal.large.findall-tokens.19` | Rust engine | 0.1696× | 0.1656–0.1730× | 5.23× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.20` | Python engine | 0.0206× | 0.0193–0.0227× | 8.57× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.20` | Native C engine | 1.8913× | 1.6384–2.1579× | 0.10× | FASTER |
| calibration | `cal.large.findall-tokens.20` | Rust engine | 0.1545× | 0.1358–0.1743× | 1.00× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.21` | Python engine | 0.0208× | 0.0192–0.0235× | 9.45× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.21` | Native C engine | 2.2836× | 2.1118–2.5608× | 0.17× | FASTER |
| calibration | `cal.large.findall-tokens.21` | Rust engine | 0.1758× | 0.1637–0.1933× | 1.92× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.22` | Python engine | 0.0199× | 0.0192–0.0210× | 10.63× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.22` | Native C engine | 2.2484× | 2.1565–2.3815× | 0.29× | FASTER |
| calibration | `cal.large.findall-tokens.22` | Rust engine | 0.1581× | 0.1510–0.1675× | 3.57× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.23` | Python engine | 0.0198× | 0.0191–0.0206× | 12.22× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.23` | Native C engine | 2.4049× | 2.3400–2.4932× | 0.45× | FASTER |
| calibration | `cal.large.findall-tokens.23` | Rust engine | 0.1586× | 0.1535–0.1651× | 5.56× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.24` | Python engine | 0.0180× | 0.0179–0.0181× | 8.59× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.24` | Native C engine | 1.7976× | 1.7425–1.8355× | 0.10× | FASTER |
| calibration | `cal.large.findall-tokens.24` | Rust engine | 0.1910× | 0.1837–0.1961× | 0.85× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.25` | Python engine | 0.0192× | 0.0190–0.0194× | 9.45× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.25` | Native C engine | 2.1025× | 2.0854–2.1219× | 0.17× | FASTER |
| calibration | `cal.large.findall-tokens.25` | Rust engine | 0.1624× | 0.1598–0.1649× | 1.92× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.26` | Python engine | 0.0194× | 0.0192–0.0196× | 10.68× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.26` | Native C engine | 2.2302× | 2.2021–2.2554× | 0.29× | FASTER |
| calibration | `cal.large.findall-tokens.26` | Rust engine | 0.1731× | 0.1707–0.1752× | 3.34× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.27` | Python engine | 0.0195× | 0.0193–0.0196× | 12.22× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.27` | Native C engine | 2.3250× | 2.3037–2.3469× | 0.45× | FASTER |
| calibration | `cal.large.findall-tokens.27` | Rust engine | 0.1625× | 0.1599–0.1643× | 5.56× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.28` | Python engine | 0.0192× | 0.0191–0.0194× | 8.54× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.28` | Native C engine | 1.8703× | 1.8542–1.8859× | 0.11× | FASTER |
| calibration | `cal.large.findall-tokens.28` | Rust engine | 0.1324× | 0.1301–0.1346× | 1.15× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.29` | Python engine | 0.0189× | 0.0187–0.0191× | 9.42× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.29` | Native C engine | 2.0875× | 2.0615–2.1154× | 0.17× | FASTER |
| calibration | `cal.large.findall-tokens.29` | Rust engine | 0.1497× | 0.1477–0.1518× | 2.06× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.30` | Python engine | 0.0194× | 0.0193–0.0195× | 10.58× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.30` | Native C engine | 2.2270× | 2.1938–2.2603× | 0.30× | FASTER |
| calibration | `cal.large.findall-tokens.30` | Rust engine | 0.1453× | 0.1434–0.1471× | 3.79× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.31` | Python engine | 0.0195× | 0.0187–0.0204× | 12.22× | SLOWDOWN |
| calibration | `cal.large.findall-tokens.31` | Native C engine | 2.3778× | 2.3127–2.4701× | 0.45× | FASTER |
| calibration | `cal.large.findall-tokens.31` | Rust engine | 0.1650× | 0.1603–0.1723× | 5.56× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.00` | Python engine | 0.0257× | 0.0253–0.0262× | 6.64× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.00` | Native C engine | 1.9293× | 1.8556–2.0038× | 0.35× | FASTER |
| calibration | `cal.large.finditer-pairs.00` | Rust engine | 0.1822× | 0.1774–0.1871× | 0.32× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.01` | Python engine | 0.0213× | 0.0209–0.0217× | 6.58× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.01` | Native C engine | 2.0494× | 2.0126–2.0919× | 0.41× | FASTER |
| calibration | `cal.large.finditer-pairs.01` | Rust engine | 0.1559× | 0.1529–0.1588× | 0.34× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.02` | Python engine | 0.0184× | 0.0182–0.0186× | 6.50× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.02` | Native C engine | 1.9635× | 1.9298–1.9969× | 0.49× | FASTER |
| calibration | `cal.large.finditer-pairs.02` | Rust engine | 0.1416× | 0.1403–0.1431× | 0.38× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.03` | Python engine | 0.0172× | 0.0169–0.0174× | 6.33× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.03` | Native C engine | 1.9293× | 1.8847–1.9712× | 0.59× | FASTER |
| calibration | `cal.large.finditer-pairs.03` | Rust engine | 0.1355× | 0.1334–0.1374× | 0.44× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.04` | Python engine | 0.0246× | 0.0242–0.0250× | 6.64× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.04` | Native C engine | 1.9020× | 1.8470–1.9543× | 0.35× | FASTER |
| calibration | `cal.large.finditer-pairs.04` | Rust engine | 0.1746× | 0.1711–0.1786× | 0.32× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.05` | Python engine | 0.0213× | 0.0207–0.0222× | 6.58× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.05` | Native C engine | 2.1031× | 2.0290–2.1912× | 0.41× | FASTER |
| calibration | `cal.large.finditer-pairs.05` | Rust engine | 0.1586× | 0.1544–0.1640× | 0.34× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.06` | Python engine | 0.0188× | 0.0182–0.0198× | 6.50× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.06` | Native C engine | 2.0716× | 2.0145–2.1522× | 0.49× | FASTER |
| calibration | `cal.large.finditer-pairs.06` | Rust engine | 0.1427× | 0.1354–0.1507× | 0.38× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.07` | Python engine | 0.0171× | 0.0163–0.0177× | 6.33× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.07` | Native C engine | 2.0390× | 1.9689–2.1109× | 0.59× | FASTER |
| calibration | `cal.large.finditer-pairs.07` | Rust engine | 0.1367× | 0.1335–0.1394× | 0.44× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.08` | Python engine | 0.0248× | 0.0242–0.0252× | 6.64× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.08` | Native C engine | 1.9565× | 1.9409–1.9723× | 0.35× | FASTER |
| calibration | `cal.large.finditer-pairs.08` | Rust engine | 0.1767× | 0.1737–0.1793× | 0.32× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.09` | Python engine | 0.0208× | 0.0205–0.0211× | 6.58× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.09` | Native C engine | 2.0224× | 1.9873–2.0625× | 0.41× | FASTER |
| calibration | `cal.large.finditer-pairs.09` | Rust engine | 0.1565× | 0.1534–0.1600× | 0.34× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.10` | Python engine | 0.0186× | 0.0182–0.0191× | 6.50× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.10` | Native C engine | 1.8272× | 1.5836–2.0152× | 0.49× | FASTER |
| calibration | `cal.large.finditer-pairs.10` | Rust engine | 0.1403× | 0.1329–0.1454× | 0.38× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.11` | Python engine | 0.0178× | 0.0173–0.0183× | 6.33× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.11` | Native C engine | 1.9251× | 1.7107–2.0851× | 0.59× | FASTER |
| calibration | `cal.large.finditer-pairs.11` | Rust engine | 0.1385× | 0.1357–0.1415× | 0.44× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.12` | Python engine | 0.0261× | 0.0248–0.0281× | 6.64× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.12` | Native C engine | 1.9380× | 1.9171–1.9607× | 0.35× | FASTER |
| calibration | `cal.large.finditer-pairs.12` | Rust engine | 0.1864× | 0.1760–0.2053× | 0.32× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.13` | Python engine | 0.0205× | 0.0195–0.0219× | 6.58× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.13` | Native C engine | 1.9608× | 1.7414–2.2002× | 0.41× | FASTER |
| calibration | `cal.large.finditer-pairs.13` | Rust engine | 0.1536× | 0.1471–0.1615× | 0.34× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.14` | Python engine | 0.0197× | 0.0186–0.0213× | 6.50× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.14` | Native C engine | 2.1183× | 1.9130–2.3292× | 0.49× | FASTER |
| calibration | `cal.large.finditer-pairs.14` | Rust engine | 0.1462× | 0.1290–0.1647× | 0.38× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.15` | Python engine | 0.0177× | 0.0175–0.0179× | 6.33× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.15` | Native C engine | 2.0134× | 1.9109–2.0938× | 0.59× | FASTER |
| calibration | `cal.large.finditer-pairs.15` | Rust engine | 0.1392× | 0.1371–0.1414× | 0.44× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.16` | Python engine | 0.0247× | 0.0243–0.0251× | 6.64× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.16` | Native C engine | 1.9322× | 1.8988–1.9662× | 0.35× | FASTER |
| calibration | `cal.large.finditer-pairs.16` | Rust engine | 0.1791× | 0.1778–0.1805× | 0.32× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.17` | Python engine | 0.0219× | 0.0207–0.0235× | 6.58× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.17` | Native C engine | 2.0814× | 1.8908–2.2809× | 0.41× | FASTER |
| calibration | `cal.large.finditer-pairs.17` | Rust engine | 0.1589× | 0.1501–0.1705× | 0.34× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.18` | Python engine | 0.0191× | 0.0184–0.0203× | 6.50× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.18` | Native C engine | 1.9035× | 1.6287–2.1762× | 0.49× | FASTER |
| calibration | `cal.large.finditer-pairs.18` | Rust engine | 0.1461× | 0.1386–0.1575× | 0.38× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.19` | Python engine | 0.0182× | 0.0173–0.0196× | 6.33× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.19` | Native C engine | 2.1282× | 2.0324–2.2844× | 0.59× | FASTER |
| calibration | `cal.large.finditer-pairs.19` | Rust engine | 0.1543× | 0.1451–0.1673× | 0.44× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.20` | Python engine | 0.0258× | 0.0247–0.0275× | 6.64× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.20` | Native C engine | 1.9839× | 1.9070–2.1205× | 0.35× | FASTER |
| calibration | `cal.large.finditer-pairs.20` | Rust engine | 0.1835× | 0.1749–0.1970× | 0.32× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.21` | Python engine | 0.0200× | 0.0198–0.0202× | 6.58× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.21` | Native C engine | 1.7342× | 1.4990–1.9225× | 0.41× | FASTER |
| calibration | `cal.large.finditer-pairs.21` | Rust engine | 0.1415× | 0.1306–0.1489× | 0.34× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.22` | Python engine | 0.0184× | 0.0180–0.0187× | 6.50× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.22` | Native C engine | 1.9577× | 1.9112–2.0055× | 0.49× | FASTER |
| calibration | `cal.large.finditer-pairs.22` | Rust engine | 0.1533× | 0.1500–0.1565× | 0.38× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.23` | Python engine | 0.0178× | 0.0175–0.0180× | 6.33× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.23` | Native C engine | 2.0007× | 1.9425–2.0638× | 0.59× | FASTER |
| calibration | `cal.large.finditer-pairs.23` | Rust engine | 0.1397× | 0.1371–0.1420× | 0.44× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.24` | Python engine | 0.0252× | 0.0249–0.0255× | 6.64× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.24` | Native C engine | 1.9283× | 1.8733–1.9707× | 0.35× | FASTER |
| calibration | `cal.large.finditer-pairs.24` | Rust engine | 0.1770× | 0.1742–0.1793× | 0.32× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.25` | Python engine | 0.0214× | 0.0209–0.0220× | 6.58× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.25` | Native C engine | 2.0147× | 1.9757–2.0711× | 0.41× | FASTER |
| calibration | `cal.large.finditer-pairs.25` | Rust engine | 0.1598× | 0.1572–0.1635× | 0.34× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.26` | Python engine | 0.0185× | 0.0182–0.0187× | 6.50× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.26` | Native C engine | 1.9345× | 1.8957–1.9788× | 0.49× | FASTER |
| calibration | `cal.large.finditer-pairs.26` | Rust engine | 0.1368× | 0.1249–0.1441× | 0.38× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.27` | Python engine | 0.0180× | 0.0170–0.0197× | 6.33× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.27` | Native C engine | 1.9627× | 1.8200–2.2021× | 0.59× | FASTER |
| calibration | `cal.large.finditer-pairs.27` | Rust engine | 0.1355× | 0.1267–0.1516× | 0.44× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.28` | Python engine | 0.0248× | 0.0242–0.0259× | 6.64× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.28` | Native C engine | 1.9730× | 1.9168–2.0599× | 0.35× | FASTER |
| calibration | `cal.large.finditer-pairs.28` | Rust engine | 0.1735× | 0.1676–0.1823× | 0.32× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.29` | Python engine | 0.0203× | 0.0189–0.0217× | 6.58× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.29` | Native C engine | 1.9422× | 1.8400–2.0596× | 0.41× | FASTER |
| calibration | `cal.large.finditer-pairs.29` | Rust engine | 0.1513× | 0.1460–0.1579× | 0.34× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.30` | Python engine | 0.0181× | 0.0177–0.0185× | 6.50× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.30` | Native C engine | 1.9046× | 1.8774–1.9326× | 0.49× | FASTER |
| calibration | `cal.large.finditer-pairs.30` | Rust engine | 0.1364× | 0.1296–0.1417× | 0.38× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.31` | Python engine | 0.0174× | 0.0171–0.0177× | 6.33× | SLOWDOWN |
| calibration | `cal.large.finditer-pairs.31` | Native C engine | 1.9379× | 1.8668–2.0050× | 0.59× | FASTER |
| calibration | `cal.large.finditer-pairs.31` | Rust engine | 0.1337× | 0.1313–0.1366× | 0.44× | SLOWDOWN |
| calibration | `cal.large.split-keep.00` | Python engine | 0.0241× | 0.0238–0.0243× | 5.84× | SLOWDOWN |
| calibration | `cal.large.split-keep.00` | Native C engine | 1.2149× | 1.1642–1.2487× | 0.27× | FASTER |
| calibration | `cal.large.split-keep.00` | Rust engine | 0.1450× | 0.1434–0.1465× | 1.85× | SLOWDOWN |
| calibration | `cal.large.split-keep.01` | Python engine | 0.0212× | 0.0210–0.0214× | 6.30× | SLOWDOWN |
| calibration | `cal.large.split-keep.01` | Native C engine | 1.2706× | 1.2603–1.2799× | 0.36× | FASTER |
| calibration | `cal.large.split-keep.01` | Rust engine | 0.1321× | 0.1250–0.1375× | 2.60× | SLOWDOWN |
| calibration | `cal.large.split-keep.02` | Python engine | 0.0196× | 0.0195–0.0198× | 7.12× | SLOWDOWN |
| calibration | `cal.large.split-keep.02` | Native C engine | 1.3151× | 1.3027–1.3283× | 0.50× | FASTER |
| calibration | `cal.large.split-keep.02` | Rust engine | 0.1337× | 0.1322–0.1351× | 3.96× | SLOWDOWN |
| calibration | `cal.large.split-keep.03` | Python engine | 0.0199× | 0.0198–0.0201× | 7.79× | SLOWDOWN |
| calibration | `cal.large.split-keep.03` | Native C engine | 1.2748× | 1.2623–1.2866× | 0.62× | FASTER |
| calibration | `cal.large.split-keep.03` | Rust engine | 0.1414× | 0.1403–0.1425× | 6.20× | SLOWDOWN |
| calibration | `cal.large.split-keep.04` | Python engine | 0.0243× | 0.0241–0.0245× | 5.84× | SLOWDOWN |
| calibration | `cal.large.split-keep.04` | Native C engine | 1.2270× | 1.1974–1.2489× | 0.27× | FASTER |
| calibration | `cal.large.split-keep.04` | Rust engine | 0.1446× | 0.1429–0.1461× | 1.80× | SLOWDOWN |
| calibration | `cal.large.split-keep.05` | Python engine | 0.0211× | 0.0210–0.0212× | 6.30× | SLOWDOWN |
| calibration | `cal.large.split-keep.05` | Native C engine | 1.2542× | 1.2452–1.2634× | 0.36× | FASTER |
| calibration | `cal.large.split-keep.05` | Rust engine | 0.1369× | 0.1352–0.1383× | 2.65× | SLOWDOWN |
| calibration | `cal.large.split-keep.06` | Python engine | 0.0196× | 0.0196–0.0197× | 7.12× | SLOWDOWN |
| calibration | `cal.large.split-keep.06` | Native C engine | 1.2982× | 1.2793–1.3146× | 0.50× | FASTER |
| calibration | `cal.large.split-keep.06` | Rust engine | 0.1327× | 0.1312–0.1340× | 3.96× | SLOWDOWN |
| calibration | `cal.large.split-keep.07` | Python engine | 0.0194× | 0.0192–0.0197× | 7.85× | SLOWDOWN |
| calibration | `cal.large.split-keep.07` | Native C engine | 1.3324× | 1.3053–1.3621× | 0.62× | FASTER |
| calibration | `cal.large.split-keep.07` | Rust engine | 0.1366× | 0.1352–0.1386× | 5.60× | SLOWDOWN |
| calibration | `cal.large.split-keep.08` | Python engine | 0.0236× | 0.0233–0.0240× | 5.86× | SLOWDOWN |
| calibration | `cal.large.split-keep.08` | Native C engine | 1.2890× | 1.2706–1.3097× | 0.27× | FASTER |
| calibration | `cal.large.split-keep.08` | Rust engine | 0.1396× | 0.1376–0.1420× | 1.53× | SLOWDOWN |
| calibration | `cal.large.split-keep.09` | Python engine | 0.0214× | 0.0211–0.0219× | 6.30× | SLOWDOWN |
| calibration | `cal.large.split-keep.09` | Native C engine | 1.2402× | 1.1483–1.3040× | 0.36× | FASTER |
| calibration | `cal.large.split-keep.09` | Rust engine | 0.1401× | 0.1379–0.1429× | 2.65× | SLOWDOWN |
| calibration | `cal.large.split-keep.10` | Python engine | 0.0210× | 0.0195–0.0233× | 7.12× | SLOWDOWN |
| calibration | `cal.large.split-keep.10` | Native C engine | 1.4189× | 1.3235–1.5605× | 0.50× | FASTER |
| calibration | `cal.large.split-keep.10` | Rust engine | 0.1441× | 0.1342–0.1594× | 3.92× | SLOWDOWN |
| calibration | `cal.large.split-keep.11` | Python engine | 0.0187× | 0.0185–0.0188× | 7.97× | SLOWDOWN |
| calibration | `cal.large.split-keep.11` | Native C engine | 1.4438× | 1.4313–1.4568× | 0.62× | FASTER |
| calibration | `cal.large.split-keep.11` | Rust engine | 0.1277× | 0.1260–0.1291× | 4.31× | SLOWDOWN |
| calibration | `cal.large.split-keep.12` | Python engine | 0.0244× | 0.0241–0.0248× | 5.84× | SLOWDOWN |
| calibration | `cal.large.split-keep.12` | Native C engine | 1.2295× | 1.2143–1.2460× | 0.27× | FASTER |
| calibration | `cal.large.split-keep.12` | Rust engine | 0.1457× | 0.1432–0.1482× | 1.85× | SLOWDOWN |
| calibration | `cal.large.split-keep.13` | Python engine | 0.0206× | 0.0205–0.0207× | 6.34× | SLOWDOWN |
| calibration | `cal.large.split-keep.13` | Native C engine | 1.2790× | 1.1771–1.3439× | 0.36× | FASTER |
| calibration | `cal.large.split-keep.13` | Rust engine | 0.1317× | 0.1301–0.1332× | 2.09× | SLOWDOWN |
| calibration | `cal.large.split-keep.14` | Python engine | 0.0202× | 0.0196–0.0214× | 7.12× | SLOWDOWN |
| calibration | `cal.large.split-keep.14` | Native C engine | 1.3611× | 1.3200–1.4356× | 0.50× | FASTER |
| calibration | `cal.large.split-keep.14` | Rust engine | 0.1377× | 0.1326–0.1462× | 3.96× | SLOWDOWN |
| calibration | `cal.large.split-keep.15` | Python engine | 0.0186× | 0.0185–0.0187× | 7.97× | SLOWDOWN |
| calibration | `cal.large.split-keep.15` | Native C engine | 1.4564× | 1.4447–1.4680× | 0.62× | FASTER |
| calibration | `cal.large.split-keep.15` | Rust engine | 0.1289× | 0.1281–0.1299× | 4.28× | SLOWDOWN |
| calibration | `cal.large.split-keep.16` | Python engine | 0.0244× | 0.0235–0.0260× | 5.86× | SLOWDOWN |
| calibration | `cal.large.split-keep.16` | Native C engine | 1.3001× | 1.1980–1.4082× | 0.27× | FASTER |
| calibration | `cal.large.split-keep.16` | Rust engine | 0.1447× | 0.1387–0.1543× | 1.53× | SLOWDOWN |
| calibration | `cal.large.split-keep.17` | Python engine | 0.0213× | 0.0211–0.0215× | 6.30× | SLOWDOWN |
| calibration | `cal.large.split-keep.17` | Native C engine | 1.2665× | 1.2559–1.2774× | 0.36× | FASTER |
| calibration | `cal.large.split-keep.17` | Rust engine | 0.1384× | 0.1375–0.1394× | 2.65× | SLOWDOWN |
| calibration | `cal.large.split-keep.18` | Python engine | 0.0197× | 0.0196–0.0198× | 7.12× | SLOWDOWN |
| calibration | `cal.large.split-keep.18` | Native C engine | 1.2726× | 1.1852–1.3234× | 0.50× | FASTER |
| calibration | `cal.large.split-keep.18` | Rust engine | 0.1345× | 0.1326–0.1359× | 3.96× | SLOWDOWN |
| calibration | `cal.large.split-keep.19` | Python engine | 0.0192× | 0.0191–0.0194× | 7.85× | SLOWDOWN |
| calibration | `cal.large.split-keep.19` | Native C engine | 1.3351× | 1.3195–1.3500× | 0.62× | FASTER |
| calibration | `cal.large.split-keep.19` | Rust engine | 0.1349× | 0.1322–0.1366× | 5.57× | SLOWDOWN |
| calibration | `cal.large.split-keep.20` | Python engine | 0.0245× | 0.0239–0.0256× | 5.84× | SLOWDOWN |
| calibration | `cal.large.split-keep.20` | Native C engine | 1.2666× | 1.2329–1.3258× | 0.27× | FASTER |
| calibration | `cal.large.split-keep.20` | Rust engine | 0.1465× | 0.1430–0.1527× | 1.80× | SLOWDOWN |
| calibration | `cal.large.split-keep.21` | Python engine | 0.0216× | 0.0210–0.0226× | 6.30× | SLOWDOWN |
| calibration | `cal.large.split-keep.21` | Native C engine | 1.2725× | 1.2324–1.3300× | 0.36× | FASTER |
| calibration | `cal.large.split-keep.21` | Rust engine | 0.1405× | 0.1368–0.1469× | 2.65× | SLOWDOWN |
| calibration | `cal.large.split-keep.22` | Python engine | 0.0206× | 0.0202–0.0211× | 7.08× | SLOWDOWN |
| calibration | `cal.large.split-keep.22` | Native C engine | 1.2902× | 1.2710–1.3144× | 0.51× | FASTER |
| calibration | `cal.large.split-keep.22` | Rust engine | 0.1422× | 0.1409–0.1436× | 4.38× | SLOWDOWN |
| calibration | `cal.large.split-keep.23` | Python engine | 0.0199× | 0.0193–0.0210× | 7.85× | SLOWDOWN |
| calibration | `cal.large.split-keep.23` | Native C engine | 1.3647× | 1.3188–1.4455× | 0.62× | FASTER |
| calibration | `cal.large.split-keep.23` | Rust engine | 0.1402× | 0.1349–0.1490× | 5.60× | SLOWDOWN |
| calibration | `cal.large.split-keep.24` | Python engine | 0.0243× | 0.0240–0.0247× | 5.84× | SLOWDOWN |
| calibration | `cal.large.split-keep.24` | Native C engine | 1.2475× | 1.2302–1.2655× | 0.27× | FASTER |
| calibration | `cal.large.split-keep.24` | Rust engine | 0.1453× | 0.1427–0.1479× | 1.80× | SLOWDOWN |
| calibration | `cal.large.split-keep.25` | Python engine | 0.0214× | 0.0211–0.0218× | 6.30× | SLOWDOWN |
| calibration | `cal.large.split-keep.25` | Native C engine | 1.2864× | 1.2545–1.3165× | 0.36× | FASTER |
| calibration | `cal.large.split-keep.25` | Rust engine | 0.1392× | 0.1364–0.1424× | 2.60× | SLOWDOWN |
| calibration | `cal.large.split-keep.26` | Python engine | 0.0192× | 0.0190–0.0194× | 7.19× | SLOWDOWN |
| calibration | `cal.large.split-keep.26` | Native C engine | 1.3760× | 1.2483–1.4519× | 0.50× | FASTER |
| calibration | `cal.large.split-keep.26` | Rust engine | 0.1293× | 0.1280–0.1307× | 3.05× | SLOWDOWN |
| calibration | `cal.large.split-keep.27` | Python engine | 0.0185× | 0.0183–0.0187× | 7.97× | SLOWDOWN |
| calibration | `cal.large.split-keep.27` | Native C engine | 1.4289× | 1.4075–1.4465× | 0.62× | FASTER |
| calibration | `cal.large.split-keep.27` | Rust engine | 0.1283× | 0.1268–0.1296× | 4.31× | SLOWDOWN |
| calibration | `cal.large.split-keep.28` | Python engine | 0.0239× | 0.0238–0.0241× | 5.84× | SLOWDOWN |
| calibration | `cal.large.split-keep.28` | Native C engine | 1.2347× | 1.2241–1.2460× | 0.27× | FASTER |
| calibration | `cal.large.split-keep.28` | Rust engine | 0.1422× | 0.1398–0.1442× | 1.80× | SLOWDOWN |
| calibration | `cal.large.split-keep.29` | Python engine | 0.0223× | 0.0215–0.0236× | 6.28× | SLOWDOWN |
| calibration | `cal.large.split-keep.29` | Native C engine | 1.2797× | 1.2336–1.3549× | 0.36× | FASTER |
| calibration | `cal.large.split-keep.29` | Rust engine | 0.1473× | 0.1417–0.1566× | 2.93× | SLOWDOWN |
| calibration | `cal.large.split-keep.30` | Python engine | 0.0206× | 0.0205–0.0207× | 7.08× | SLOWDOWN |
| calibration | `cal.large.split-keep.30` | Native C engine | 1.2698× | 1.2584–1.2821× | 0.51× | FASTER |
| calibration | `cal.large.split-keep.30` | Rust engine | 0.1396× | 0.1371–0.1416× | 4.42× | SLOWDOWN |
| calibration | `cal.large.split-keep.31` | Python engine | 0.0202× | 0.0200–0.0204× | 7.79× | SLOWDOWN |
| calibration | `cal.large.split-keep.31` | Native C engine | 1.2834× | 1.2572–1.3070× | 0.63× | FASTER |
| calibration | `cal.large.split-keep.31` | Rust engine | 0.1416× | 0.1388–0.1441× | 6.23× | SLOWDOWN |
| calibration | `cal.large.replace-groups.00` | Python engine | 0.0242× | 0.0233–0.0256× | 7.83× | SLOWDOWN |
| calibration | `cal.large.replace-groups.00` | Native C engine | 1.8194× | 1.7509–1.9157× | 0.13× | FASTER |
| calibration | `cal.large.replace-groups.00` | Rust engine | 0.0770× | 0.0741–0.0810× | 1.47× | SLOWDOWN |
| calibration | `cal.large.replace-groups.01` | Python engine | 0.0216× | 0.0214–0.0219× | 8.29× | SLOWDOWN |
| calibration | `cal.large.replace-groups.01` | Native C engine | 1.9640× | 1.9417–1.9889× | 0.13× | FASTER |
| calibration | `cal.large.replace-groups.01` | Rust engine | 0.0821× | 0.0812–0.0832× | 2.49× | SLOWDOWN |
| calibration | `cal.large.replace-groups.02` | Python engine | 0.0205× | 0.0201–0.0209× | 8.98× | SLOWDOWN |
| calibration | `cal.large.replace-groups.02` | Native C engine | 2.0966× | 2.0341–2.1373× | 0.14× | FASTER |
| calibration | `cal.large.replace-groups.02` | Rust engine | 0.0887× | 0.0877–0.0897× | 4.56× | SLOWDOWN |
| calibration | `cal.large.replace-groups.03` | Python engine | 0.0206× | 0.0200–0.0217× | 9.97× | SLOWDOWN |
| calibration | `cal.large.replace-groups.03` | Native C engine | 2.3275× | 2.2478–2.4484× | 0.15× | FASTER |
| calibration | `cal.large.replace-groups.03` | Rust engine | 0.0949× | 0.0916–0.1000× | 7.07× | SLOWDOWN |
| calibration | `cal.large.replace-groups.04` | Python engine | 0.0235× | 0.0229–0.0242× | 7.81× | SLOWDOWN |
| calibration | `cal.large.replace-groups.04` | Native C engine | 1.7833× | 1.7342–1.8490× | 0.13× | FASTER |
| calibration | `cal.large.replace-groups.04` | Rust engine | 0.0763× | 0.0744–0.0788× | 1.73× | SLOWDOWN |
| calibration | `cal.large.replace-groups.05` | Python engine | 0.0202× | 0.0200–0.0206× | 8.67× | SLOWDOWN |
| calibration | `cal.large.replace-groups.05` | Native C engine | 1.9825× | 1.9584–2.0097× | 0.15× | FASTER |
| calibration | `cal.large.replace-groups.05` | Rust engine | 0.0766× | 0.0753–0.0780× | 2.87× | SLOWDOWN |
| calibration | `cal.large.replace-groups.06` | Python engine | 0.0204× | 0.0200–0.0207× | 8.95× | SLOWDOWN |
| calibration | `cal.large.replace-groups.06` | Native C engine | 2.0550× | 1.9089–2.1462× | 0.15× | FASTER |
| calibration | `cal.large.replace-groups.06` | Rust engine | 0.0873× | 0.0864–0.0882× | 4.97× | SLOWDOWN |
| calibration | `cal.large.replace-groups.07` | Python engine | 0.0202× | 0.0197–0.0213× | 9.91× | SLOWDOWN |
| calibration | `cal.large.replace-groups.07` | Native C engine | 2.2736× | 2.2135–2.3856× | 0.16× | FASTER |
| calibration | `cal.large.replace-groups.07` | Rust engine | 0.0925× | 0.0898–0.0973× | 7.71× | SLOWDOWN |
| calibration | `cal.large.replace-groups.08` | Python engine | 0.0230× | 0.0228–0.0231× | 7.82× | SLOWDOWN |
| calibration | `cal.large.replace-groups.08` | Native C engine | 1.7096× | 1.6336–1.7581× | 0.13× | FASTER |
| calibration | `cal.large.replace-groups.08` | Rust engine | 0.0742× | 0.0738–0.0747× | 1.60× | SLOWDOWN |
| calibration | `cal.large.replace-groups.09` | Python engine | 0.0211× | 0.0209–0.0213× | 8.27× | SLOWDOWN |
| calibration | `cal.large.replace-groups.09` | Native C engine | 1.9510× | 1.9421–1.9612× | 0.14× | FASTER |
| calibration | `cal.large.replace-groups.09` | Rust engine | 0.0801× | 0.0784–0.0815× | 2.74× | SLOWDOWN |
| calibration | `cal.large.replace-groups.10` | Python engine | 0.0227× | 0.0216–0.0250× | 8.65× | SLOWDOWN |
| calibration | `cal.large.replace-groups.10` | Native C engine | 2.0955× | 1.9848–2.3093× | 0.18× | FASTER |
| calibration | `cal.large.replace-groups.10` | Rust engine | 0.0696× | 0.0660–0.0767× | 6.02× | SLOWDOWN |
| calibration | `cal.large.replace-groups.11` | Python engine | 0.0217× | 0.0210–0.0223× | 9.97× | SLOWDOWN |
| calibration | `cal.large.replace-groups.11` | Native C engine | 2.4597× | 2.3779–2.5353× | 0.15× | FASTER |
| calibration | `cal.large.replace-groups.11` | Rust engine | 0.1008× | 0.0977–0.1037× | 7.07× | SLOWDOWN |
| calibration | `cal.large.replace-groups.12` | Python engine | 0.0246× | 0.0239–0.0252× | 7.81× | SLOWDOWN |
| calibration | `cal.large.replace-groups.12` | Native C engine | 1.8480× | 1.7983–1.8959× | 0.13× | FASTER |
| calibration | `cal.large.replace-groups.12` | Rust engine | 0.0789× | 0.0766–0.0809× | 1.73× | SLOWDOWN |
| calibration | `cal.large.replace-groups.13` | Python engine | 0.0214× | 0.0212–0.0215× | 8.27× | SLOWDOWN |
| calibration | `cal.large.replace-groups.13` | Native C engine | 1.9704× | 1.9551–1.9844× | 0.14× | FASTER |
| calibration | `cal.large.replace-groups.13` | Rust engine | 0.0816× | 0.0807–0.0824× | 2.74× | SLOWDOWN |
| calibration | `cal.large.replace-groups.14` | Python engine | 0.0199× | 0.0197–0.0201× | 9.05× | SLOWDOWN |
| calibration | `cal.large.replace-groups.14` | Native C engine | 2.0602× | 2.0436–2.0760× | 0.13× | FASTER |
| calibration | `cal.large.replace-groups.14` | Rust engine | 0.0884× | 0.0872–0.0894× | 3.73× | SLOWDOWN |
| calibration | `cal.large.replace-groups.15` | Python engine | 0.0242× | 0.0222–0.0286× | 8.65× | SLOWDOWN |
| calibration | `cal.large.replace-groups.15` | Native C engine | 1.8767× | 1.4779–2.3869× | 0.24× | FASTER |
| calibration | `cal.large.replace-groups.15` | Rust engine | 0.0563× | 0.0515–0.0664× | 11.82× | SLOWDOWN |
| calibration | `cal.large.replace-groups.16` | Python engine | 0.0243× | 0.0237–0.0249× | 7.82× | SLOWDOWN |
| calibration | `cal.large.replace-groups.16` | Native C engine | 1.8521× | 1.8048–1.8934× | 0.13× | FASTER |
| calibration | `cal.large.replace-groups.16` | Rust engine | 0.0790× | 0.0769–0.0809× | 1.60× | SLOWDOWN |
| calibration | `cal.large.replace-groups.17` | Python engine | 0.0233× | 0.0224–0.0245× | 8.24× | SLOWDOWN |
| calibration | `cal.large.replace-groups.17` | Native C engine | 2.0674× | 1.9174–2.2065× | 0.14× | FASTER |
| calibration | `cal.large.replace-groups.17` | Rust engine | 0.0883× | 0.0849–0.0927× | 2.98× | SLOWDOWN |
| calibration | `cal.large.replace-groups.18` | Python engine | 0.0206× | 0.0203–0.0209× | 8.98× | SLOWDOWN |
| calibration | `cal.large.replace-groups.18` | Native C engine | 2.0966× | 2.0741–2.1230× | 0.14× | FASTER |
| calibration | `cal.large.replace-groups.18` | Rust engine | 0.0880× | 0.0869–0.0894× | 4.56× | SLOWDOWN |
| calibration | `cal.large.replace-groups.19` | Python engine | 0.0197× | 0.0194–0.0200× | 9.97× | SLOWDOWN |
| calibration | `cal.large.replace-groups.19` | Native C engine | 2.2704× | 2.2507–2.2905× | 0.15× | FASTER |
| calibration | `cal.large.replace-groups.19` | Rust engine | 0.0920× | 0.0911–0.0930× | 7.07× | SLOWDOWN |
| calibration | `cal.large.replace-groups.20` | Python engine | 0.0225× | 0.0223–0.0227× | 7.85× | SLOWDOWN |
| calibration | `cal.large.replace-groups.20` | Native C engine | 1.7839× | 1.7682–1.7987× | 0.13× | FASTER |
| calibration | `cal.large.replace-groups.20` | Rust engine | 0.0767× | 0.0761–0.0772× | 1.33× | SLOWDOWN |
| calibration | `cal.large.replace-groups.21` | Python engine | 0.0216× | 0.0213–0.0218× | 8.24× | SLOWDOWN |
| calibration | `cal.large.replace-groups.21` | Native C engine | 1.9640× | 1.9487–1.9797× | 0.14× | FASTER |
| calibration | `cal.large.replace-groups.21` | Rust engine | 0.0800× | 0.0745–0.0833× | 2.98× | SLOWDOWN |
| calibration | `cal.large.replace-groups.22` | Python engine | 0.0207× | 0.0205–0.0208× | 8.98× | SLOWDOWN |
| calibration | `cal.large.replace-groups.22` | Native C engine | 2.1090× | 2.0945–2.1227× | 0.14× | FASTER |
| calibration | `cal.large.replace-groups.22` | Rust engine | 0.0881× | 0.0871–0.0891× | 4.56× | SLOWDOWN |
| calibration | `cal.large.replace-groups.23` | Python engine | 0.0199× | 0.0198–0.0201× | 9.91× | SLOWDOWN |
| calibration | `cal.large.replace-groups.23` | Native C engine | 2.2230× | 2.2037–2.2418× | 0.16× | FASTER |
| calibration | `cal.large.replace-groups.23` | Rust engine | 0.0913× | 0.0907–0.0920× | 7.71× | SLOWDOWN |
| calibration | `cal.large.replace-groups.24` | Python engine | 0.0233× | 0.0232–0.0235× | 7.82× | SLOWDOWN |
| calibration | `cal.large.replace-groups.24` | Native C engine | 1.7182× | 1.6171–1.7804× | 0.13× | FASTER |
| calibration | `cal.large.replace-groups.24` | Rust engine | 0.0750× | 0.0744–0.0756× | 1.60× | SLOWDOWN |
| calibration | `cal.large.replace-groups.25` | Python engine | 0.0201× | 0.0196–0.0205× | 8.71× | SLOWDOWN |
| calibration | `cal.large.replace-groups.25` | Native C engine | 2.0345× | 2.0102–2.0591× | 0.14× | FASTER |
| calibration | `cal.large.replace-groups.25` | Rust engine | 0.0807× | 0.0796–0.0818× | 2.36× | SLOWDOWN |
| calibration | `cal.large.replace-groups.26` | Python engine | 0.0202× | 0.0200–0.0203× | 9.05× | SLOWDOWN |
| calibration | `cal.large.replace-groups.26` | Native C engine | 1.9330× | 1.7200–2.1018× | 0.13× | FASTER |
| calibration | `cal.large.replace-groups.26` | Rust engine | 0.0869× | 0.0838–0.0896× | 3.73× | SLOWDOWN |
| calibration | `cal.large.replace-groups.27` | Python engine | 0.0199× | 0.0195–0.0206× | 9.91× | SLOWDOWN |
| calibration | `cal.large.replace-groups.27` | Native C engine | 2.2196× | 2.1709–2.3043× | 0.16× | FASTER |
| calibration | `cal.large.replace-groups.27` | Rust engine | 0.0913× | 0.0891–0.0946× | 7.71× | SLOWDOWN |
| calibration | `cal.large.replace-groups.28` | Python engine | 0.0233× | 0.0228–0.0241× | 7.83× | SLOWDOWN |
| calibration | `cal.large.replace-groups.28` | Native C engine | 1.7847× | 1.7466–1.8475× | 0.13× | FASTER |
| calibration | `cal.large.replace-groups.28` | Rust engine | 0.0778× | 0.0763–0.0805× | 1.47× | SLOWDOWN |
| calibration | `cal.large.replace-groups.29` | Python engine | 0.0214× | 0.0207–0.0223× | 8.29× | SLOWDOWN |
| calibration | `cal.large.replace-groups.29` | Native C engine | 2.0073× | 1.9589–2.0841× | 0.13× | FASTER |
| calibration | `cal.large.replace-groups.29` | Rust engine | 0.0842× | 0.0821–0.0875× | 2.49× | SLOWDOWN |
| calibration | `cal.large.replace-groups.30` | Python engine | 0.0228× | 0.0215–0.0249× | 8.64× | SLOWDOWN |
| calibration | `cal.large.replace-groups.30` | Native C engine | 2.0066× | 1.7720–2.2806× | 0.19× | FASTER |
| calibration | `cal.large.replace-groups.30` | Rust engine | 0.0698× | 0.0661–0.0767× | 6.53× | SLOWDOWN |
| calibration | `cal.large.replace-groups.31` | Python engine | 0.0199× | 0.0195–0.0208× | 9.91× | SLOWDOWN |
| calibration | `cal.large.replace-groups.31` | Native C engine | 2.2353× | 2.1849–2.3266× | 0.16× | FASTER |
| calibration | `cal.large.replace-groups.31` | Rust engine | 0.0927× | 0.0899–0.0974× | 7.71× | SLOWDOWN |
| calibration | `cal.large.replace-callback.00` | Python engine | 0.0777× | 0.0766–0.0795× | 3.07× | SLOWDOWN |
| calibration | `cal.large.replace-callback.00` | Native C engine | 1.1810× | 1.1572–1.2077× | 0.25× | FASTER |
| calibration | `cal.large.replace-callback.00` | Rust engine | 0.2140× | 0.2100–0.2195× | 0.53× | SLOWDOWN |
| calibration | `cal.large.replace-callback.01` | Python engine | 0.0790× | 0.0775–0.0812× | 3.14× | SLOWDOWN |
| calibration | `cal.large.replace-callback.01` | Native C engine | 1.2434× | 1.2193–1.2800× | 0.23× | FASTER |
| calibration | `cal.large.replace-callback.01` | Rust engine | 0.2270× | 0.2224–0.2339× | 0.60× | SLOWDOWN |
| calibration | `cal.large.replace-callback.02` | Python engine | 0.0769× | 0.0761–0.0777× | 3.22× | SLOWDOWN |
| calibration | `cal.large.replace-callback.02` | Native C engine | 1.2835× | 1.2684–1.3006× | 0.22× | FASTER |
| calibration | `cal.large.replace-callback.02` | Rust engine | 0.2204× | 0.2162–0.2244× | 0.71× | SLOWDOWN |
| calibration | `cal.large.replace-callback.03` | Python engine | 0.0737× | 0.0706–0.0762× | 3.32× | SLOWDOWN |
| calibration | `cal.large.replace-callback.03` | Native C engine | 1.1337× | 1.1216–1.1457× | 0.32× | FASTER |
| calibration | `cal.large.replace-callback.03` | Rust engine | 0.2163× | 0.2146–0.2177× | 0.67× | SLOWDOWN |
| calibration | `cal.large.replace-callback.04` | Python engine | 0.0867× | 0.0826–0.0935× | 3.07× | SLOWDOWN |
| calibration | `cal.large.replace-callback.04` | Native C engine | 1.2343× | 1.1741–1.3282× | 0.25× | FASTER |
| calibration | `cal.large.replace-callback.04` | Rust engine | 0.2414× | 0.2295–0.2602× | 0.53× | SLOWDOWN |
| calibration | `cal.large.replace-callback.05` | Python engine | 0.0780× | 0.0772–0.0789× | 3.13× | SLOWDOWN |
| calibration | `cal.large.replace-callback.05` | Native C engine | 1.2138× | 1.1687–1.2414× | 0.23× | FASTER |
| calibration | `cal.large.replace-callback.05` | Rust engine | 0.2205× | 0.2185–0.2225× | 0.60× | SLOWDOWN |
| calibration | `cal.large.replace-callback.06` | Python engine | 0.0734× | 0.0728–0.0740× | 3.32× | SLOWDOWN |
| calibration | `cal.large.replace-callback.06` | Native C engine | 1.0908× | 0.9979–1.1486× | 0.28× | — |
| calibration | `cal.large.replace-callback.06` | Rust engine | 0.2107× | 0.2081–0.2132× | 0.59× | SLOWDOWN |
| calibration | `cal.large.replace-callback.07` | Python engine | 0.0754× | 0.0741–0.0769× | 3.34× | SLOWDOWN |
| calibration | `cal.large.replace-callback.07` | Native C engine | 1.2718× | 1.2451–1.2948× | 0.19× | FASTER |
| calibration | `cal.large.replace-callback.07` | Rust engine | 0.2281× | 0.2247–0.2318× | 0.82× | SLOWDOWN |
| calibration | `cal.large.replace-callback.08` | Python engine | 0.0813× | 0.0740–0.0898× | 3.06× | SLOWDOWN |
| calibration | `cal.large.replace-callback.08` | Native C engine | 1.1454× | 1.0532–1.2192× | 0.25× | FASTER |
| calibration | `cal.large.replace-callback.08` | Rust engine | 0.2254× | 0.2165–0.2327× | 0.53× | SLOWDOWN |
| calibration | `cal.large.replace-callback.09` | Python engine | 0.0710× | 0.0699–0.0723× | 3.32× | SLOWDOWN |
| calibration | `cal.large.replace-callback.09` | Native C engine | 1.1624× | 1.1283–1.1925× | 0.25× | FASTER |
| calibration | `cal.large.replace-callback.09` | Rust engine | 0.2073× | 0.2038–0.2111× | 0.55× | SLOWDOWN |
| calibration | `cal.large.replace-callback.10` | Python engine | 0.0752× | 0.0720–0.0772× | 3.23× | SLOWDOWN |
| calibration | `cal.large.replace-callback.10` | Native C engine | 1.2715× | 1.2581–1.2862× | 0.21× | FASTER |
| calibration | `cal.large.replace-callback.10` | Rust engine | 0.2264× | 0.2226–0.2295× | 0.70× | SLOWDOWN |
| calibration | `cal.large.replace-callback.11` | Python engine | 0.0776× | 0.0748–0.0823× | 3.34× | SLOWDOWN |
| calibration | `cal.large.replace-callback.11` | Native C engine | 1.3402× | 1.2946–1.4229× | 0.19× | FASTER |
| calibration | `cal.large.replace-callback.11` | Rust engine | 0.2355× | 0.2272–0.2503× | 0.82× | SLOWDOWN |
| calibration | `cal.large.replace-callback.12` | Python engine | 0.0761× | 0.0749–0.0772× | 3.07× | SLOWDOWN |
| calibration | `cal.large.replace-callback.12` | Native C engine | 1.1187× | 1.0761–1.1494× | 0.25× | FASTER |
| calibration | `cal.large.replace-callback.12` | Rust engine | 0.2128× | 0.2109–0.2151× | 0.53× | SLOWDOWN |
| calibration | `cal.large.replace-callback.13` | Python engine | 0.0747× | 0.0741–0.0754× | 3.15× | SLOWDOWN |
| calibration | `cal.large.replace-callback.13` | Native C engine | 1.2062× | 1.1639–1.2335× | 0.22× | FASTER |
| calibration | `cal.large.replace-callback.13` | Rust engine | 0.2323× | 0.2308–0.2338× | 0.60× | SLOWDOWN |
| calibration | `cal.large.replace-callback.14` | Python engine | 0.0812× | 0.0761–0.0891× | 3.23× | SLOWDOWN |
| calibration | `cal.large.replace-callback.14` | Native C engine | 1.3061× | 1.2729–1.3616× | 0.21× | FASTER |
| calibration | `cal.large.replace-callback.14` | Rust engine | 0.2430× | 0.2294–0.2625× | 0.70× | SLOWDOWN |
| calibration | `cal.large.replace-callback.15` | Python engine | 0.0750× | 0.0738–0.0760× | 3.27× | SLOWDOWN |
| calibration | `cal.large.replace-callback.15` | Native C engine | 1.1320× | 1.1060–1.1550× | 0.33× | FASTER |
| calibration | `cal.large.replace-callback.15` | Rust engine | 0.2097× | 0.2049–0.2142× | 0.70× | SLOWDOWN |
| calibration | `cal.large.replace-callback.16` | Python engine | 0.0851× | 0.0817–0.0895× | 3.06× | SLOWDOWN |
| calibration | `cal.large.replace-callback.16` | Native C engine | 1.1805× | 1.1068–1.2583× | 0.25× | FASTER |
| calibration | `cal.large.replace-callback.16` | Rust engine | 0.2322× | 0.2222–0.2451× | 0.53× | SLOWDOWN |
| calibration | `cal.large.replace-callback.17` | Python engine | 0.0813× | 0.0781–0.0866× | 3.13× | SLOWDOWN |
| calibration | `cal.large.replace-callback.17` | Native C engine | 1.2724× | 1.2199–1.3481× | 0.23× | FASTER |
| calibration | `cal.large.replace-callback.17` | Rust engine | 0.2299× | 0.2200–0.2439× | 0.60× | SLOWDOWN |
| calibration | `cal.large.replace-callback.18` | Python engine | 0.0728× | 0.0715–0.0737× | 3.31× | SLOWDOWN |
| calibration | `cal.large.replace-callback.18` | Native C engine | 1.1451× | 1.1320–1.1576× | 0.29× | FASTER |
| calibration | `cal.large.replace-callback.18` | Rust engine | 0.2050× | 0.1990–0.2096× | 0.61× | SLOWDOWN |
| calibration | `cal.large.replace-callback.19` | Python engine | 0.0756× | 0.0735–0.0784× | 3.34× | SLOWDOWN |
| calibration | `cal.large.replace-callback.19` | Native C engine | 1.2717× | 1.2109–1.3207× | 0.19× | FASTER |
| calibration | `cal.large.replace-callback.19` | Rust engine | 0.2319× | 0.2269–0.2390× | 0.82× | SLOWDOWN |
| calibration | `cal.large.replace-callback.20` | Python engine | 0.0830× | 0.0788–0.0872× | 3.07× | SLOWDOWN |
| calibration | `cal.large.replace-callback.20` | Native C engine | 1.2021× | 1.1684–1.2547× | 0.25× | FASTER |
| calibration | `cal.large.replace-callback.20` | Rust engine | 0.2361× | 0.2286–0.2467× | 0.53× | SLOWDOWN |
| calibration | `cal.large.replace-callback.21` | Python engine | 0.0721× | 0.0709–0.0735× | 3.32× | SLOWDOWN |
| calibration | `cal.large.replace-callback.21` | Native C engine | 1.1883× | 1.1720–1.2100× | 0.25× | FASTER |
| calibration | `cal.large.replace-callback.21` | Rust engine | 0.2093× | 0.2066–0.2130× | 0.55× | SLOWDOWN |
| calibration | `cal.large.replace-callback.22` | Python engine | 0.0765× | 0.0758–0.0772× | 3.22× | SLOWDOWN |
| calibration | `cal.large.replace-callback.22` | Native C engine | 1.2879× | 1.2725–1.3028× | 0.22× | FASTER |
| calibration | `cal.large.replace-callback.22` | Rust engine | 0.2224× | 0.2200–0.2248× | 0.71× | SLOWDOWN |
| calibration | `cal.large.replace-callback.23` | Python engine | 0.0750× | 0.0743–0.0760× | 3.34× | SLOWDOWN |
| calibration | `cal.large.replace-callback.23` | Native C engine | 1.2962× | 1.2823–1.3099× | 0.19× | FASTER |
| calibration | `cal.large.replace-callback.23` | Rust engine | 0.2302× | 0.2279–0.2330× | 0.82× | SLOWDOWN |
| calibration | `cal.large.replace-callback.24` | Python engine | 0.0759× | 0.0738–0.0785× | 3.07× | SLOWDOWN |
| calibration | `cal.large.replace-callback.24` | Native C engine | 1.1597× | 1.1335–1.1945× | 0.25× | FASTER |
| calibration | `cal.large.replace-callback.24` | Rust engine | 0.2119× | 0.2074–0.2179× | 0.53× | SLOWDOWN |
| calibration | `cal.large.replace-callback.25` | Python engine | 0.0784× | 0.0773–0.0801× | 3.13× | SLOWDOWN |
| calibration | `cal.large.replace-callback.25` | Native C engine | 1.2038× | 1.1277–1.2625× | 0.23× | FASTER |
| calibration | `cal.large.replace-callback.25` | Rust engine | 0.2217× | 0.2172–0.2277× | 0.60× | SLOWDOWN |
| calibration | `cal.large.replace-callback.26` | Python engine | 0.0796× | 0.0771–0.0835× | 3.23× | SLOWDOWN |
| calibration | `cal.large.replace-callback.26` | Native C engine | 1.2818× | 1.1623–1.3816× | 0.21× | FASTER |
| calibration | `cal.large.replace-callback.26` | Rust engine | 0.2376× | 0.2315–0.2482× | 0.70× | SLOWDOWN |
| calibration | `cal.large.replace-callback.27` | Python engine | 0.0728× | 0.0717–0.0739× | 3.24× | SLOWDOWN |
| calibration | `cal.large.replace-callback.27` | Native C engine | 1.0966× | 1.0704–1.1246× | 0.34× | FASTER |
| calibration | `cal.large.replace-callback.27` | Rust engine | 0.2118× | 0.2084–0.2154× | 0.71× | SLOWDOWN |
| calibration | `cal.large.replace-callback.28` | Python engine | 0.0862× | 0.0821–0.0936× | 3.07× | SLOWDOWN |
| calibration | `cal.large.replace-callback.28` | Native C engine | 1.1713× | 1.0498–1.2846× | 0.25× | FASTER |
| calibration | `cal.large.replace-callback.28` | Rust engine | 0.2334× | 0.2227–0.2448× | 0.53× | SLOWDOWN |
| calibration | `cal.large.replace-callback.29` | Python engine | 0.0798× | 0.0780–0.0823× | 3.13× | SLOWDOWN |
| calibration | `cal.large.replace-callback.29` | Native C engine | 1.2389× | 1.2159–1.2762× | 0.23× | FASTER |
| calibration | `cal.large.replace-callback.29` | Rust engine | 0.2330× | 0.2276–0.2408× | 0.60× | SLOWDOWN |
| calibration | `cal.large.replace-callback.30` | Python engine | 0.0738× | 0.0716–0.0767× | 3.31× | SLOWDOWN |
| calibration | `cal.large.replace-callback.30` | Native C engine | 1.1535× | 1.0318–1.2997× | 0.29× | FASTER |
| calibration | `cal.large.replace-callback.30` | Rust engine | 0.2172× | 0.2088–0.2325× | 0.62× | SLOWDOWN |
| calibration | `cal.large.replace-callback.31` | Python engine | 0.0848× | 0.0767–0.0950× | 3.33× | SLOWDOWN |
| calibration | `cal.large.replace-callback.31` | Native C engine | 1.2908× | 1.2044–1.4100× | 0.19× | FASTER |
| calibration | `cal.large.replace-callback.31` | Rust engine | 0.2575× | 0.2373–0.2837× | 0.82× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.00` | Python engine | 0.0202× | 0.0200–0.0205× | 5.84× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.00` | Native C engine | 2.3018× | 2.2709–2.3294× | 0.18× | FASTER |
| calibration | `cal.large.bytes-tokens.00` | Rust engine | 0.2625× | 0.2557–0.2680× | 1.00× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.01` | Python engine | 0.0196× | 0.0189–0.0200× | 6.29× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.01` | Native C engine | 2.5459× | 2.5101–2.5789× | 0.29× | FASTER |
| calibration | `cal.large.bytes-tokens.01` | Rust engine | 0.2834× | 0.2818–0.2851× | 1.47× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.02` | Python engine | 0.0195× | 0.0194–0.0196× | 7.11× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.02` | Native C engine | 2.7444× | 2.7089–2.7731× | 0.43× | FASTER |
| calibration | `cal.large.bytes-tokens.02` | Rust engine | 0.3028× | 0.2999–0.3052× | 2.38× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.03` | Python engine | 0.0212× | 0.0205–0.0226× | 8.17× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.03` | Native C engine | 3.0187× | 2.8806–3.2377× | 0.58× | FASTER |
| calibration | `cal.large.bytes-tokens.03` | Rust engine | 0.3774× | 0.3640–0.4030× | 2.76× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.04` | Python engine | 0.0204× | 0.0203–0.0206× | 5.84× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.04` | Native C engine | 2.3001× | 2.2727–2.3246× | 0.18× | FASTER |
| calibration | `cal.large.bytes-tokens.04` | Rust engine | 0.2458× | 0.2271–0.2567× | 1.07× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.05` | Python engine | 0.0199× | 0.0194–0.0206× | 6.28× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.05` | Native C engine | 2.3245× | 2.0265–2.5418× | 0.30× | FASTER |
| calibration | `cal.large.bytes-tokens.05` | Rust engine | 0.2813× | 0.2755–0.2880× | 1.59× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.06` | Python engine | 0.0199× | 0.0195–0.0205× | 7.11× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.06` | Native C engine | 2.6701× | 2.4322–2.8512× | 0.43× | FASTER |
| calibration | `cal.large.bytes-tokens.06` | Rust engine | 0.3009× | 0.2892–0.3146× | 2.38× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.07` | Python engine | 0.0199× | 0.0197–0.0201× | 8.09× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.07` | Native C engine | 2.8693× | 2.8223–2.9103× | 0.58× | FASTER |
| calibration | `cal.large.bytes-tokens.07` | Rust engine | 0.3268× | 0.3207–0.3320× | 3.32× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.08` | Python engine | 0.0206× | 0.0204–0.0208× | 5.84× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.08` | Native C engine | 2.3646× | 2.3367–2.3894× | 0.18× | FASTER |
| calibration | `cal.large.bytes-tokens.08` | Rust engine | 0.2586× | 0.2551–0.2618× | 1.07× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.09` | Python engine | 0.0201× | 0.0186–0.0218× | 6.28× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.09` | Native C engine | 2.4284× | 2.1660–2.5991× | 0.30× | FASTER |
| calibration | `cal.large.bytes-tokens.09` | Rust engine | 0.2860× | 0.2725–0.3076× | 1.59× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.10` | Python engine | 0.0192× | 0.0188–0.0195× | 7.09× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.10` | Native C engine | 2.6963× | 2.6700–2.7191× | 0.43× | FASTER |
| calibration | `cal.large.bytes-tokens.10` | Rust engine | 0.2888× | 0.2874–0.2902× | 2.58× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.11` | Python engine | 0.0200× | 0.0199–0.0201× | 8.09× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.11` | Native C engine | 2.8704× | 2.8340–2.9047× | 0.58× | FASTER |
| calibration | `cal.large.bytes-tokens.11` | Rust engine | 0.3288× | 0.3265–0.3310× | 3.32× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.12` | Python engine | 0.0208× | 0.0205–0.0214× | 5.84× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.12` | Native C engine | 2.3253× | 2.2812–2.3966× | 0.18× | FASTER |
| calibration | `cal.large.bytes-tokens.12` | Rust engine | 0.2569× | 0.2507–0.2658× | 1.07× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.13` | Python engine | 0.0199× | 0.0197–0.0201× | 6.28× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.13` | Native C engine | 2.5116× | 2.4729–2.5456× | 0.30× | FASTER |
| calibration | `cal.large.bytes-tokens.13` | Rust engine | 0.2800× | 0.2783–0.2817× | 1.59× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.14` | Python engine | 0.0205× | 0.0195–0.0226× | 7.11× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.14` | Native C engine | 2.6359× | 2.1820–3.0969× | 0.43× | FASTER |
| calibration | `cal.large.bytes-tokens.14` | Rust engine | 0.3165× | 0.2986–0.3512× | 2.38× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.15` | Python engine | 0.0204× | 0.0200–0.0210× | 8.09× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.15` | Native C engine | 2.8903× | 2.8156–2.9835× | 0.58× | FASTER |
| calibration | `cal.large.bytes-tokens.15` | Rust engine | 0.3349× | 0.3288–0.3452× | 3.32× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.16` | Python engine | 0.0205× | 0.0203–0.0206× | 5.85× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.16` | Native C engine | 2.2360× | 2.1061–2.3228× | 0.18× | FASTER |
| calibration | `cal.large.bytes-tokens.16` | Rust engine | 0.2712× | 0.2674–0.2743× | 0.92× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.17` | Python engine | 0.0203× | 0.0198–0.0211× | 6.30× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.17` | Native C engine | 2.5988× | 2.5397–2.6946× | 0.29× | FASTER |
| calibration | `cal.large.bytes-tokens.17` | Rust engine | 0.2981× | 0.2910–0.3107× | 1.35× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.18` | Python engine | 0.0196× | 0.0195–0.0197× | 7.09× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.18` | Native C engine | 2.7120× | 2.6875–2.7376× | 0.43× | FASTER |
| calibration | `cal.large.bytes-tokens.18` | Rust engine | 0.2890× | 0.2876–0.2904× | 2.58× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.19` | Python engine | 0.0195× | 0.0190–0.0200× | 8.06× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.19` | Native C engine | 2.8355× | 2.7557–2.9134× | 0.59× | FASTER |
| calibration | `cal.large.bytes-tokens.19` | Rust engine | 0.3002× | 0.2916–0.3082× | 3.59× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.20` | Python engine | 0.0207× | 0.0205–0.0210× | 5.84× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.20` | Native C engine | 2.2932× | 2.1725–2.3781× | 0.18× | FASTER |
| calibration | `cal.large.bytes-tokens.20` | Rust engine | 0.2548× | 0.2497–0.2596× | 1.07× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.21` | Python engine | 0.0200× | 0.0199–0.0202× | 6.30× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.21` | Native C engine | 2.4307× | 2.2564–2.5423× | 0.29× | FASTER |
| calibration | `cal.large.bytes-tokens.21` | Rust engine | 0.2950× | 0.2902–0.2990× | 1.35× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.22` | Python engine | 0.0196× | 0.0195–0.0197× | 7.09× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.22` | Native C engine | 2.7407× | 2.7151–2.7657× | 0.43× | FASTER |
| calibration | `cal.large.bytes-tokens.22` | Rust engine | 0.2881× | 0.2824–0.2917× | 2.58× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.23` | Python engine | 0.0206× | 0.0196–0.0221× | 8.09× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.23` | Native C engine | 2.9998× | 2.8582–3.1934× | 0.58× | FASTER |
| calibration | `cal.large.bytes-tokens.23` | Rust engine | 0.3329× | 0.3119–0.3572× | 3.32× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.24` | Python engine | 0.0211× | 0.0207–0.0219× | 5.84× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.24` | Native C engine | 2.3890× | 2.3215–2.4790× | 0.18× | FASTER |
| calibration | `cal.large.bytes-tokens.24` | Rust engine | 0.2594× | 0.2522–0.2702× | 1.07× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.25` | Python engine | 0.0200× | 0.0199–0.0201× | 6.30× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.25` | Native C engine | 2.5291× | 2.5038–2.5555× | 0.29× | FASTER |
| calibration | `cal.large.bytes-tokens.25` | Rust engine | 0.2933× | 0.2847–0.2995× | 1.35× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.26` | Python engine | 0.0195× | 0.0194–0.0196× | 7.11× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.26` | Native C engine | 2.6489× | 2.4480–2.7671× | 0.43× | FASTER |
| calibration | `cal.large.bytes-tokens.26` | Rust engine | 0.3064× | 0.3042–0.3083× | 2.38× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.27` | Python engine | 0.0188× | 0.0182–0.0194× | 8.02× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.27` | Native C engine | 2.7099× | 2.6287–2.7934× | 0.59× | FASTER |
| calibration | `cal.large.bytes-tokens.27` | Rust engine | 0.2806× | 0.2675–0.2925× | 3.87× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.28` | Python engine | 0.0210× | 0.0209–0.0212× | 5.84× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.28` | Native C engine | 2.3936× | 2.3707–2.4181× | 0.18× | FASTER |
| calibration | `cal.large.bytes-tokens.28` | Rust engine | 0.2723× | 0.2683–0.2760× | 1.00× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.29` | Python engine | 0.0208× | 0.0203–0.0215× | 6.27× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.29` | Native C engine | 2.6142× | 2.5529–2.7021× | 0.30× | FASTER |
| calibration | `cal.large.bytes-tokens.29` | Rust engine | 0.2852× | 0.2794–0.2959× | 1.72× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.30` | Python engine | 0.0199× | 0.0198–0.0200× | 7.09× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.30` | Native C engine | 2.7375× | 2.7084–2.7619× | 0.43× | FASTER |
| calibration | `cal.large.bytes-tokens.30` | Rust engine | 0.3006× | 0.2993–0.3020× | 2.58× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.31` | Python engine | 0.0182× | 0.0180–0.0183× | 8.06× | SLOWDOWN |
| calibration | `cal.large.bytes-tokens.31` | Native C engine | 2.5846× | 2.5507–2.6150× | 0.59× | FASTER |
| calibration | `cal.large.bytes-tokens.31` | Rust engine | 0.2887× | 0.2850–0.2916× | 3.59× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.00` | Python engine | 0.0175× | 0.0173–0.0178× | 4.63× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.00` | Native C engine | 1.3460× | 1.3356–1.3559× | 0.34× | FASTER |
| calibration | `cal.large.bytes-buffer.00` | Rust engine | 0.1721× | 0.1703–0.1737× | 0.67× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.01` | Python engine | 0.0149× | 0.0148–0.0150× | 5.79× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.01` | Native C engine | 1.2695× | 1.2597–1.2799× | 0.40× | FASTER |
| calibration | `cal.large.bytes-buffer.01` | Rust engine | 0.1684× | 0.1661–0.1703× | 0.56× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.02` | Python engine | 0.0134× | 0.0133–0.0135× | 7.51× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.02` | Native C engine | 1.2387× | 1.2266–1.2505× | 0.49× | FASTER |
| calibration | `cal.large.bytes-buffer.02` | Rust engine | 0.1566× | 0.1549–0.1581× | 0.68× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.03` | Python engine | 0.0125× | 0.0123–0.0126× | 8.73× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.03` | Native C engine | 1.1871× | 1.1658–1.2087× | 0.57× | FASTER |
| calibration | `cal.large.bytes-buffer.03` | Rust engine | 0.1530× | 0.1499–0.1560× | 0.62× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.04` | Python engine | 0.0177× | 0.0173–0.0182× | 4.63× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.04` | Native C engine | 1.3617× | 1.3031–1.4153× | 0.34× | FASTER |
| calibration | `cal.large.bytes-buffer.04` | Rust engine | 0.1780× | 0.1746–0.1830× | 0.67× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.05` | Python engine | 0.0146× | 0.0145–0.0147× | 5.81× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.05` | Native C engine | 1.2563× | 1.2127–1.2841× | 0.40× | FASTER |
| calibration | `cal.large.bytes-buffer.05` | Rust engine | 0.1668× | 0.1648–0.1687× | 0.56× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.06` | Python engine | 0.0139× | 0.0134–0.0146× | 7.51× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.06` | Native C engine | 1.2390× | 1.1554–1.3270× | 0.49× | FASTER |
| calibration | `cal.large.bytes-buffer.06` | Rust engine | 0.1603× | 0.1559–0.1678× | 0.68× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.07` | Python engine | 0.0124× | 0.0123–0.0125× | 8.73× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.07` | Native C engine | 1.1654× | 1.1525–1.1783× | 0.57× | FASTER |
| calibration | `cal.large.bytes-buffer.07` | Rust engine | 0.1517× | 0.1501–0.1533× | 0.62× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.08` | Python engine | 0.0177× | 0.0174–0.0180× | 4.63× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.08` | Native C engine | 1.3831× | 1.3581–1.4138× | 0.34× | FASTER |
| calibration | `cal.large.bytes-buffer.08` | Rust engine | 0.1722× | 0.1689–0.1763× | 0.67× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.09` | Python engine | 0.0146× | 0.0146–0.0147× | 5.81× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.09` | Native C engine | 1.2686× | 1.2605–1.2753× | 0.40× | FASTER |
| calibration | `cal.large.bytes-buffer.09` | Rust engine | 0.1657× | 0.1642–0.1670× | 0.56× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.10` | Python engine | 0.0134× | 0.0133–0.0134× | 7.51× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.10` | Native C engine | 1.2413× | 1.2280–1.2540× | 0.49× | FASTER |
| calibration | `cal.large.bytes-buffer.10` | Rust engine | 0.1567× | 0.1554–0.1579× | 0.68× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.11` | Python engine | 0.0124× | 0.0122–0.0125× | 8.73× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.11` | Native C engine | 1.1707× | 1.1539–1.1885× | 0.57× | FASTER |
| calibration | `cal.large.bytes-buffer.11` | Rust engine | 0.1529× | 0.1504–0.1553× | 0.62× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.12` | Python engine | 0.0177× | 0.0175–0.0179× | 4.63× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.12` | Native C engine | 1.3597× | 1.3033–1.3945× | 0.34× | FASTER |
| calibration | `cal.large.bytes-buffer.12` | Rust engine | 0.1767× | 0.1751–0.1785× | 0.67× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.13` | Python engine | 0.0147× | 0.0145–0.0148× | 5.81× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.13` | Native C engine | 1.2817× | 1.2694–1.2948× | 0.40× | FASTER |
| calibration | `cal.large.bytes-buffer.13` | Rust engine | 0.1660× | 0.1639–0.1679× | 0.56× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.14` | Python engine | 0.0136× | 0.0133–0.0142× | 7.51× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.14` | Native C engine | 1.2466× | 1.1789–1.3136× | 0.49× | FASTER |
| calibration | `cal.large.bytes-buffer.14` | Rust engine | 0.1597× | 0.1563–0.1653× | 0.68× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.15` | Python engine | 0.0124× | 0.0120–0.0126× | 8.73× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.15` | Native C engine | 1.1679× | 1.1320–1.1946× | 0.57× | FASTER |
| calibration | `cal.large.bytes-buffer.15` | Rust engine | 0.1538× | 0.1516–0.1561× | 0.62× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.16` | Python engine | 0.0174× | 0.0168–0.0179× | 4.63× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.16` | Native C engine | 1.3802× | 1.3396–1.4266× | 0.34× | FASTER |
| calibration | `cal.large.bytes-buffer.16` | Rust engine | 0.1724× | 0.1674–0.1783× | 0.67× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.17` | Python engine | 0.0146× | 0.0145–0.0147× | 5.81× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.17` | Native C engine | 1.2743× | 1.2633–1.2847× | 0.40× | FASTER |
| calibration | `cal.large.bytes-buffer.17` | Rust engine | 0.1667× | 0.1655–0.1676× | 0.56× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.18` | Python engine | 0.0133× | 0.0133–0.0134× | 7.51× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.18` | Native C engine | 1.1631× | 1.0358–1.2467× | 0.49× | FASTER |
| calibration | `cal.large.bytes-buffer.18` | Rust engine | 0.1551× | 0.1510–0.1579× | 0.68× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.19` | Python engine | 0.0126× | 0.0122–0.0131× | 8.73× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.19` | Native C engine | 1.1967× | 1.1597–1.2463× | 0.57× | FASTER |
| calibration | `cal.large.bytes-buffer.19` | Rust engine | 0.1560× | 0.1517–0.1624× | 0.62× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.20` | Python engine | 0.0176× | 0.0172–0.0180× | 4.63× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.20` | Native C engine | 1.3717× | 1.3409–1.4009× | 0.34× | FASTER |
| calibration | `cal.large.bytes-buffer.20` | Rust engine | 0.1732× | 0.1703–0.1765× | 0.67× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.21` | Python engine | 0.0148× | 0.0146–0.0150× | 5.81× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.21` | Native C engine | 1.2838× | 1.2699–1.3003× | 0.40× | FASTER |
| calibration | `cal.large.bytes-buffer.21` | Rust engine | 0.1677× | 0.1659–0.1699× | 0.56× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.22` | Python engine | 0.0139× | 0.0135–0.0144× | 7.51× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.22` | Native C engine | 1.2909× | 1.2545–1.3425× | 0.49× | FASTER |
| calibration | `cal.large.bytes-buffer.22` | Rust engine | 0.1616× | 0.1567–0.1677× | 0.68× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.23` | Python engine | 0.0124× | 0.0123–0.0125× | 8.17× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.23` | Native C engine | 1.1829× | 1.1699–1.1960× | 0.57× | FASTER |
| calibration | `cal.large.bytes-buffer.23` | Rust engine | 0.1535× | 0.1521–0.1548× | 0.62× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.24` | Python engine | 0.0178× | 0.0174–0.0184× | 4.63× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.24` | Native C engine | 1.3973× | 1.3642–1.4434× | 0.34× | FASTER |
| calibration | `cal.large.bytes-buffer.24` | Rust engine | 0.1745× | 0.1704–0.1803× | 0.67× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.25` | Python engine | 0.0147× | 0.0145–0.0149× | 5.81× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.25` | Native C engine | 1.2785× | 1.2641–1.2956× | 0.40× | FASTER |
| calibration | `cal.large.bytes-buffer.25` | Rust engine | 0.1653× | 0.1631–0.1679× | 0.56× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.26` | Python engine | 0.0135× | 0.0134–0.0137× | 7.51× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.26` | Native C engine | 1.2444× | 1.2186–1.2673× | 0.49× | FASTER |
| calibration | `cal.large.bytes-buffer.26` | Rust engine | 0.1573× | 0.1551–0.1595× | 0.68× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.27` | Python engine | 0.0122× | 0.0120–0.0123× | 8.85× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.27` | Native C engine | 1.1952× | 1.1784–1.2106× | 0.57× | FASTER |
| calibration | `cal.large.bytes-buffer.27` | Rust engine | 0.1519× | 0.1498–0.1544× | 0.62× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.28` | Python engine | 0.0172× | 0.0170–0.0177× | 4.64× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.28` | Native C engine | 1.3774× | 1.3533–1.4095× | 0.34× | FASTER |
| calibration | `cal.large.bytes-buffer.28` | Rust engine | 0.1697× | 0.1664–0.1743× | 0.67× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.29` | Python engine | 0.0143× | 0.0141–0.0146× | 5.83× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.29` | Native C engine | 1.2830× | 1.2665–1.3027× | 0.40× | FASTER |
| calibration | `cal.large.bytes-buffer.29` | Rust engine | 0.1652× | 0.1633–0.1679× | 0.56× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.30` | Python engine | 0.0132× | 0.0130–0.0134× | 7.56× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.30` | Native C engine | 1.1505× | 1.0610–1.2325× | 0.49× | FASTER |
| calibration | `cal.large.bytes-buffer.30` | Rust engine | 0.1538× | 0.1518–0.1560× | 0.68× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.31` | Python engine | 0.0125× | 0.0121–0.0130× | 8.85× | SLOWDOWN |
| calibration | `cal.large.bytes-buffer.31` | Native C engine | 1.2161× | 1.1841–1.2667× | 0.57× | FASTER |
| calibration | `cal.large.bytes-buffer.31` | Rust engine | 0.1571× | 0.1534–0.1634× | 0.62× | SLOWDOWN |
| calibration | `cal.large.unicode-words.00` | Python engine | 0.0219× | 0.0217–0.0220× | 6.83× | SLOWDOWN |
| calibration | `cal.large.unicode-words.00` | Native C engine | 1.0504× | 1.0334–1.0638× | 0.25× | FASTER |
| calibration | `cal.large.unicode-words.00` | Rust engine | 0.1091× | 0.1085–0.1096× | 0.91× | SLOWDOWN |
| calibration | `cal.large.unicode-words.01` | Python engine | 0.0221× | 0.0220–0.0223× | 6.63× | SLOWDOWN |
| calibration | `cal.large.unicode-words.01` | Native C engine | 1.0747× | 1.0709–1.0785× | 0.40× | FASTER |
| calibration | `cal.large.unicode-words.01` | Rust engine | 0.0918× | 0.0912–0.0923× | 1.03× | SLOWDOWN |
| calibration | `cal.large.unicode-words.02` | Python engine | 0.0225× | 0.0224–0.0227× | 6.49× | SLOWDOWN |
| calibration | `cal.large.unicode-words.02` | Native C engine | 1.0882× | 1.0806–1.0958× | 0.56× | FASTER |
| calibration | `cal.large.unicode-words.02` | Rust engine | 0.0663× | 0.0659–0.0666× | 1.20× | SLOWDOWN |
| calibration | `cal.large.unicode-words.03` | Python engine | 0.0227× | 0.0224–0.0232× | 6.39× | SLOWDOWN |
| calibration | `cal.large.unicode-words.03` | Native C engine | 1.1075× | 1.0922–1.1319× | 0.71× | FASTER |
| calibration | `cal.large.unicode-words.03` | Rust engine | 0.0441× | 0.0434–0.0451× | 1.33× | SLOWDOWN |
| calibration | `cal.large.unicode-words.04` | Python engine | 0.0222× | 0.0220–0.0225× | 6.82× | SLOWDOWN |
| calibration | `cal.large.unicode-words.04` | Native C engine | 1.0412× | 1.0212–1.0576× | 0.25× | FASTER |
| calibration | `cal.large.unicode-words.04` | Rust engine | 0.1074× | 0.1059–0.1089× | 0.92× | SLOWDOWN |
| calibration | `cal.large.unicode-words.05` | Python engine | 0.0230× | 0.0222–0.0244× | 6.62× | SLOWDOWN |
| calibration | `cal.large.unicode-words.05` | Native C engine | 1.0903× | 1.0450–1.1643× | 0.40× | FASTER |
| calibration | `cal.large.unicode-words.05` | Rust engine | 0.0930× | 0.0896–0.0988× | 1.04× | SLOWDOWN |
| calibration | `cal.large.unicode-words.06` | Python engine | 0.0218× | 0.0213–0.0222× | 6.52× | SLOWDOWN |
| calibration | `cal.large.unicode-words.06` | Native C engine | 1.0676× | 1.0430–1.0910× | 0.56× | FASTER |
| calibration | `cal.large.unicode-words.06` | Rust engine | 0.0678× | 0.0663–0.0692× | 1.16× | SLOWDOWN |
| calibration | `cal.large.unicode-words.07` | Python engine | 0.0210× | 0.0209–0.0212× | 6.39× | SLOWDOWN |
| calibration | `cal.large.unicode-words.07` | Native C engine | 1.0253× | 1.0202–1.0312× | 0.71× | FASTER |
| calibration | `cal.large.unicode-words.07` | Rust engine | 0.0410× | 0.0407–0.0413× | 1.33× | SLOWDOWN |
| calibration | `cal.large.unicode-words.08` | Python engine | 0.0204× | 0.0203–0.0206× | 6.81× | SLOWDOWN |
| calibration | `cal.large.unicode-words.08` | Native C engine | 0.9716× | 0.9651–0.9789× | 0.25× | — |
| calibration | `cal.large.unicode-words.08` | Rust engine | 0.0980× | 0.0970–0.0991× | 0.92× | SLOWDOWN |
| calibration | `cal.large.unicode-words.09` | Python engine | 0.0210× | 0.0210–0.0211× | 6.61× | SLOWDOWN |
| calibration | `cal.large.unicode-words.09` | Native C engine | 0.9869× | 0.9593–1.0036× | 0.40× | — |
| calibration | `cal.large.unicode-words.09` | Rust engine | 0.0839× | 0.0836–0.0843× | 1.05× | SLOWDOWN |
| calibration | `cal.large.unicode-words.10` | Python engine | 0.0213× | 0.0209–0.0218× | 6.50× | SLOWDOWN |
| calibration | `cal.large.unicode-words.10` | Native C engine | 1.0303× | 1.0133–1.0543× | 0.56× | FASTER |
| calibration | `cal.large.unicode-words.10` | Rust engine | 0.0632× | 0.0621–0.0647× | 1.19× | SLOWDOWN |
| calibration | `cal.large.unicode-words.11` | Python engine | 0.0210× | 0.0209–0.0212× | 6.39× | SLOWDOWN |
| calibration | `cal.large.unicode-words.11` | Native C engine | 1.0098× | 0.9849–1.0292× | 0.71× | — |
| calibration | `cal.large.unicode-words.11` | Rust engine | 0.0407× | 0.0401–0.0411× | 1.33× | SLOWDOWN |
| calibration | `cal.large.unicode-words.12` | Python engine | 0.0214× | 0.0205–0.0228× | 6.83× | SLOWDOWN |
| calibration | `cal.large.unicode-words.12` | Native C engine | 1.0289× | 0.9771–1.0928× | 0.25× | — |
| calibration | `cal.large.unicode-words.12` | Rust engine | 0.1064× | 0.1011–0.1132× | 0.90× | SLOWDOWN |
| calibration | `cal.large.unicode-words.13` | Python engine | 0.0205× | 0.0203–0.0207× | 6.63× | SLOWDOWN |
| calibration | `cal.large.unicode-words.13` | Native C engine | 0.9941× | 0.9861–1.0034× | 0.40× | — |
| calibration | `cal.large.unicode-words.13` | Rust engine | 0.0860× | 0.0849–0.0871× | 1.02× | SLOWDOWN |
| calibration | `cal.large.unicode-words.14` | Python engine | 0.0208× | 0.0207–0.0210× | 6.50× | SLOWDOWN |
| calibration | `cal.large.unicode-words.14` | Native C engine | 1.0088× | 0.9890–1.0222× | 0.56× | — |
| calibration | `cal.large.unicode-words.14` | Rust engine | 0.0619× | 0.0614–0.0624× | 1.19× | SLOWDOWN |
| calibration | `cal.large.unicode-words.15` | Python engine | 0.0208× | 0.0207–0.0209× | 6.39× | SLOWDOWN |
| calibration | `cal.large.unicode-words.15` | Native C engine | 1.0104× | 0.9779–1.0298× | 0.71× | — |
| calibration | `cal.large.unicode-words.15` | Rust engine | 0.0409× | 0.0407–0.0411× | 1.33× | SLOWDOWN |
| calibration | `cal.large.unicode-words.16` | Python engine | 0.0203× | 0.0201–0.0204× | 6.82× | SLOWDOWN |
| calibration | `cal.large.unicode-words.16` | Native C engine | 0.9641× | 0.9395–0.9808× | 0.25× | — |
| calibration | `cal.large.unicode-words.16` | Rust engine | 0.0987× | 0.0981–0.0994× | 0.92× | SLOWDOWN |
| calibration | `cal.large.unicode-words.17` | Python engine | 0.0210× | 0.0208–0.0211× | 6.61× | SLOWDOWN |
| calibration | `cal.large.unicode-words.17` | Native C engine | 1.0012× | 0.9960–1.0061× | 0.40× | — |
| calibration | `cal.large.unicode-words.17` | Rust engine | 0.0832× | 0.0827–0.0837× | 1.05× | SLOWDOWN |
| calibration | `cal.large.unicode-words.18` | Python engine | 0.0208× | 0.0204–0.0210× | 6.52× | SLOWDOWN |
| calibration | `cal.large.unicode-words.18` | Native C engine | 1.0202× | 1.0136–1.0273× | 0.56× | FASTER |
| calibration | `cal.large.unicode-words.18` | Rust engine | 0.0647× | 0.0641–0.0652× | 1.16× | SLOWDOWN |
| calibration | `cal.large.unicode-words.19` | Python engine | 0.0226× | 0.0225–0.0227× | 6.38× | SLOWDOWN |
| calibration | `cal.large.unicode-words.19` | Native C engine | 1.0649× | 1.0253–1.0941× | 0.71× | FASTER |
| calibration | `cal.large.unicode-words.19` | Rust engine | 0.0431× | 0.0429–0.0434× | 1.35× | SLOWDOWN |
| calibration | `cal.large.unicode-words.20` | Python engine | 0.0219× | 0.0213–0.0228× | 6.82× | SLOWDOWN |
| calibration | `cal.large.unicode-words.20` | Native C engine | 1.0178× | 0.9568–1.0785× | 0.25× | — |
| calibration | `cal.large.unicode-words.20` | Rust engine | 0.1064× | 0.1032–0.1111× | 0.92× | SLOWDOWN |
| calibration | `cal.large.unicode-words.21` | Python engine | 0.0218× | 0.0210–0.0228× | 6.62× | SLOWDOWN |
| calibration | `cal.large.unicode-words.21` | Native C engine | 1.0285× | 0.9737–1.0810× | 0.40× | — |
| calibration | `cal.large.unicode-words.21` | Rust engine | 0.0893× | 0.0861–0.0933× | 1.04× | SLOWDOWN |
| calibration | `cal.large.unicode-words.22` | Python engine | 0.0220× | 0.0217–0.0223× | 6.50× | SLOWDOWN |
| calibration | `cal.large.unicode-words.22` | Native C engine | 1.0661× | 1.0515–1.0785× | 0.56× | FASTER |
| calibration | `cal.large.unicode-words.22` | Rust engine | 0.0655× | 0.0645–0.0664× | 1.19× | SLOWDOWN |
| calibration | `cal.large.unicode-words.23` | Python engine | 0.0229× | 0.0226–0.0235× | 6.38× | SLOWDOWN |
| calibration | `cal.large.unicode-words.23` | Native C engine | 1.1077× | 1.0852–1.1393× | 0.71× | FASTER |
| calibration | `cal.large.unicode-words.23` | Rust engine | 0.0436× | 0.0427–0.0449× | 1.35× | SLOWDOWN |
| calibration | `cal.large.unicode-words.24` | Python engine | 0.0214× | 0.0213–0.0216× | 6.83× | SLOWDOWN |
| calibration | `cal.large.unicode-words.24` | Native C engine | 1.0315× | 0.9945–1.0554× | 0.25× | — |
| calibration | `cal.large.unicode-words.24` | Rust engine | 0.1073× | 0.1036–0.1097× | 0.90× | SLOWDOWN |
| calibration | `cal.large.unicode-words.25` | Python engine | 0.0220× | 0.0213–0.0227× | 6.63× | SLOWDOWN |
| calibration | `cal.large.unicode-words.25` | Native C engine | 1.0618× | 1.0291–1.0988× | 0.40× | FASTER |
| calibration | `cal.large.unicode-words.25` | Rust engine | 0.0928× | 0.0899–0.0962× | 1.02× | SLOWDOWN |
| calibration | `cal.large.unicode-words.26` | Python engine | 0.0224× | 0.0223–0.0225× | 6.49× | SLOWDOWN |
| calibration | `cal.large.unicode-words.26` | Native C engine | 1.0794× | 1.0702–1.0872× | 0.56× | FASTER |
| calibration | `cal.large.unicode-words.26` | Rust engine | 0.0649× | 0.0636–0.0657× | 1.20× | SLOWDOWN |
| calibration | `cal.large.unicode-words.27` | Python engine | 0.0234× | 0.0224–0.0248× | 6.37× | SLOWDOWN |
| calibration | `cal.large.unicode-words.27` | Native C engine | 1.0716× | 1.0182–1.1229× | 0.71× | FASTER |
| calibration | `cal.large.unicode-words.27` | Rust engine | 0.0443× | 0.0425–0.0470× | 1.35× | SLOWDOWN |
| calibration | `cal.large.unicode-words.28` | Python engine | 0.0223× | 0.0219–0.0229× | 6.81× | SLOWDOWN |
| calibration | `cal.large.unicode-words.28` | Native C engine | 1.0472× | 1.0225–1.0776× | 0.25× | FASTER |
| calibration | `cal.large.unicode-words.28` | Rust engine | 0.1053× | 0.1037–0.1072× | 0.92× | SLOWDOWN |
| calibration | `cal.large.unicode-words.29` | Python engine | 0.0219× | 0.0215–0.0223× | 6.61× | SLOWDOWN |
| calibration | `cal.large.unicode-words.29` | Native C engine | 1.0451× | 1.0263–1.0622× | 0.40× | FASTER |
| calibration | `cal.large.unicode-words.29` | Rust engine | 0.0867× | 0.0854–0.0879× | 1.05× | SLOWDOWN |
| calibration | `cal.large.unicode-words.30` | Python engine | 0.0226× | 0.0225–0.0227× | 6.48× | SLOWDOWN |
| calibration | `cal.large.unicode-words.30` | Native C engine | 1.0653× | 1.0363–1.0829× | 0.56× | FASTER |
| calibration | `cal.large.unicode-words.30` | Rust engine | 0.0644× | 0.0641–0.0647× | 1.22× | SLOWDOWN |
| calibration | `cal.large.unicode-words.31` | Python engine | 0.0228× | 0.0222–0.0236× | 6.37× | SLOWDOWN |
| calibration | `cal.large.unicode-words.31` | Native C engine | 1.0876× | 1.0468–1.1329× | 0.71× | FASTER |
| calibration | `cal.large.unicode-words.31` | Rust engine | 0.0428× | 0.0408–0.0447× | 1.35× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.00` | Python engine | 0.0289× | 0.0283–0.0295× | 4.36× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.00` | Native C engine | 1.3855× | 1.2713–1.4804× | 0.22× | FASTER |
| calibration | `cal.large.unicode-casefold.00` | Rust engine | 0.1060× | 0.1035–0.1087× | 0.97× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.01` | Python engine | 0.0296× | 0.0289–0.0302× | 4.75× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.01` | Native C engine | 1.5125× | 1.4789–1.5452× | 0.36× | FASTER |
| calibration | `cal.large.unicode-casefold.01` | Rust engine | 0.0818× | 0.0800–0.0835× | 1.14× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.02` | Python engine | 0.0322× | 0.0313–0.0332× | 5.32× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.02` | Native C engine | 1.5169× | 1.4335–1.5783× | 0.52× | FASTER |
| calibration | `cal.large.unicode-casefold.02` | Rust engine | 0.0566× | 0.0543–0.0590× | 1.38× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.03` | Python engine | 0.0325× | 0.0323–0.0326× | 5.79× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.03` | Native C engine | 1.6045× | 1.5942–1.6157× | 0.69× | FASTER |
| calibration | `cal.large.unicode-casefold.03` | Rust engine | 0.0386× | 0.0382–0.0389× | 1.55× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.04` | Python engine | 0.0289× | 0.0287–0.0291× | 4.36× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.04` | Native C engine | 1.4617× | 1.4477–1.4756× | 0.22× | FASTER |
| calibration | `cal.large.unicode-casefold.04` | Rust engine | 0.1058× | 0.1050–0.1066× | 0.97× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.05` | Python engine | 0.0308× | 0.0298–0.0316× | 4.74× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.05` | Native C engine | 1.5111× | 1.4733–1.5442× | 0.37× | FASTER |
| calibration | `cal.large.unicode-casefold.05` | Rust engine | 0.0811× | 0.0789–0.0830× | 1.16× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.06` | Python engine | 0.0318× | 0.0312–0.0327× | 5.34× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.06` | Native C engine | 1.6168× | 1.5889–1.6626× | 0.52× | FASTER |
| calibration | `cal.large.unicode-casefold.06` | Rust engine | 0.0599× | 0.0589–0.0615× | 1.35× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.07` | Python engine | 0.0332× | 0.0330–0.0334× | 5.77× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.07` | Native C engine | 1.6154× | 1.6051–1.6268× | 0.69× | FASTER |
| calibration | `cal.large.unicode-casefold.07` | Rust engine | 0.0376× | 0.0372–0.0380× | 1.58× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.08` | Python engine | 0.0289× | 0.0284–0.0293× | 4.36× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.08` | Native C engine | 1.4712× | 1.4428–1.4926× | 0.22× | FASTER |
| calibration | `cal.large.unicode-casefold.08` | Rust engine | 0.1049× | 0.1032–0.1064× | 0.97× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.09` | Python engine | 0.0297× | 0.0289–0.0305× | 4.75× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.09` | Native C engine | 1.5198× | 1.4794–1.5585× | 0.36× | FASTER |
| calibration | `cal.large.unicode-casefold.09` | Rust engine | 0.0822× | 0.0799–0.0846× | 1.14× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.10` | Python engine | 0.0315× | 0.0311–0.0322× | 5.37× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.10` | Native C engine | 1.6213× | 1.5943–1.6647× | 0.52× | FASTER |
| calibration | `cal.large.unicode-casefold.10` | Rust engine | 0.0639× | 0.0624–0.0658× | 1.29× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.11` | Python engine | 0.0331× | 0.0330–0.0332× | 5.77× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.11` | Native C engine | 1.6093× | 1.5991–1.6197× | 0.69× | FASTER |
| calibration | `cal.large.unicode-casefold.11` | Rust engine | 0.0376× | 0.0375–0.0378× | 1.58× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.12` | Python engine | 0.0287× | 0.0283–0.0290× | 4.37× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.12` | Native C engine | 1.4555× | 1.4332–1.4730× | 0.22× | FASTER |
| calibration | `cal.large.unicode-casefold.12` | Rust engine | 0.1063× | 0.1047–0.1076× | 0.95× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.13` | Python engine | 0.0306× | 0.0296–0.0318× | 4.75× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.13` | Native C engine | 1.5142× | 1.4387–1.5917× | 0.36× | FASTER |
| calibration | `cal.large.unicode-casefold.13` | Rust engine | 0.0856× | 0.0828–0.0887× | 1.14× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.14` | Python engine | 0.0315× | 0.0310–0.0318× | 5.34× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.14` | Native C engine | 1.5763× | 1.5504–1.5990× | 0.52× | FASTER |
| calibration | `cal.large.unicode-casefold.14` | Rust engine | 0.0590× | 0.0580–0.0598× | 1.35× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.15` | Python engine | 0.0325× | 0.0324–0.0326× | 5.79× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.15` | Native C engine | 1.6068× | 1.5949–1.6180× | 0.69× | FASTER |
| calibration | `cal.large.unicode-casefold.15` | Rust engine | 0.0387× | 0.0385–0.0389× | 1.55× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.16` | Python engine | 0.0290× | 0.0283–0.0296× | 4.36× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.16` | Native C engine | 1.4698× | 1.4335–1.5023× | 0.22× | FASTER |
| calibration | `cal.large.unicode-casefold.16` | Rust engine | 0.1052× | 0.1032–0.1070× | 0.97× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.17` | Python engine | 0.0283× | 0.0276–0.0290× | 4.77× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.17` | Native C engine | 1.4721× | 1.4379–1.5060× | 0.36× | FASTER |
| calibration | `cal.large.unicode-casefold.17` | Rust engine | 0.0828× | 0.0807–0.0851× | 1.10× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.18` | Python engine | 0.0325× | 0.0323–0.0327× | 5.32× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.18` | Native C engine | 1.5520× | 1.4965–1.5850× | 0.52× | FASTER |
| calibration | `cal.large.unicode-casefold.18` | Rust engine | 0.0583× | 0.0579–0.0588× | 1.38× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.19` | Python engine | 0.0314× | 0.0312–0.0316× | 5.84× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.19` | Native C engine | 1.6048× | 1.5967–1.6134× | 0.69× | FASTER |
| calibration | `cal.large.unicode-casefold.19` | Rust engine | 0.0406× | 0.0404–0.0409× | 1.47× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.20` | Python engine | 0.0289× | 0.0281–0.0297× | 4.36× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.20` | Native C engine | 1.4555× | 1.4050–1.5050× | 0.22× | FASTER |
| calibration | `cal.large.unicode-casefold.20` | Rust engine | 0.1048× | 0.1017–0.1080× | 0.97× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.21` | Python engine | 0.0292× | 0.0283–0.0301× | 4.75× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.21` | Native C engine | 1.5023× | 1.4563–1.5459× | 0.36× | FASTER |
| calibration | `cal.large.unicode-casefold.21` | Rust engine | 0.0817× | 0.0791–0.0844× | 1.14× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.22` | Python engine | 0.0329× | 0.0323–0.0337× | 5.32× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.22` | Native C engine | 1.5927× | 1.5654–1.6246× | 0.52× | FASTER |
| calibration | `cal.large.unicode-casefold.22` | Rust engine | 0.0587× | 0.0576–0.0600× | 1.38× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.23` | Python engine | 0.0330× | 0.0324–0.0341× | 5.79× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.23` | Native C engine | 1.6318× | 1.5997–1.6880× | 0.69× | FASTER |
| calibration | `cal.large.unicode-casefold.23` | Rust engine | 0.0392× | 0.0385–0.0405× | 1.55× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.24` | Python engine | 0.0289× | 0.0284–0.0295× | 4.36× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.24` | Native C engine | 1.4853× | 1.4580–1.5182× | 0.22× | FASTER |
| calibration | `cal.large.unicode-casefold.24` | Rust engine | 0.1072× | 0.1056–0.1096× | 0.97× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.25` | Python engine | 0.0296× | 0.0288–0.0306× | 4.75× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.25` | Native C engine | 1.5238× | 1.4797–1.5732× | 0.36× | FASTER |
| calibration | `cal.large.unicode-casefold.25` | Rust engine | 0.0831× | 0.0807–0.0858× | 1.14× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.26` | Python engine | 0.0309× | 0.0307–0.0311× | 5.37× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.26` | Native C engine | 1.6079× | 1.5980–1.6181× | 0.52× | FASTER |
| calibration | `cal.large.unicode-casefold.26` | Rust engine | 0.0639× | 0.0633–0.0644× | 1.29× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.27` | Python engine | 0.0327× | 0.0312–0.0346× | 5.79× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.27` | Native C engine | 1.5482× | 1.4003–1.6762× | 0.69× | FASTER |
| calibration | `cal.large.unicode-casefold.27` | Rust engine | 0.0399× | 0.0383–0.0418× | 1.55× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.28` | Python engine | 0.0282× | 0.0274–0.0288× | 4.36× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.28` | Native C engine | 1.4174× | 1.3362–1.4722× | 0.22× | FASTER |
| calibration | `cal.large.unicode-casefold.28` | Rust engine | 0.1029× | 0.0987–0.1063× | 0.97× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.29` | Python engine | 0.0319× | 0.0313–0.0324× | 4.74× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.29` | Native C engine | 1.4871× | 1.3534–1.5750× | 0.37× | FASTER |
| calibration | `cal.large.unicode-casefold.29` | Rust engine | 0.0840× | 0.0823–0.0853× | 1.16× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.30` | Python engine | 0.0333× | 0.0315–0.0356× | 5.34× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.30` | Native C engine | 1.6951× | 1.6010–1.8138× | 0.52× | FASTER |
| calibration | `cal.large.unicode-casefold.30` | Rust engine | 0.0635× | 0.0600–0.0676× | 1.35× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.31` | Python engine | 0.0334× | 0.0322–0.0349× | 5.79× | SLOWDOWN |
| calibration | `cal.large.unicode-casefold.31` | Native C engine | 1.6608× | 1.6113–1.7309× | 0.69× | FASTER |
| calibration | `cal.large.unicode-casefold.31` | Rust engine | 0.0398× | 0.0385–0.0417× | 1.55× | SLOWDOWN |
| calibration | `cal.large.cold-compile.00` | Python engine | 1.7563× | 1.7170–1.7993× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.00` | Native C engine | 1.4367× | 1.4061–1.4744× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.00` | Rust engine | 1.5237× | 1.4248–1.5988× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.01` | Python engine | 1.6721× | 1.5770–1.7505× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.01` | Native C engine | 1.3950× | 1.3574–1.4398× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.01` | Rust engine | 1.5390× | 1.5072–1.5819× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.02` | Python engine | 1.7077× | 1.6856–1.7310× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.02` | Native C engine | 1.4136× | 1.3909–1.4388× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.02` | Rust engine | 1.5298× | 1.4908–1.5701× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.03` | Python engine | 1.6816× | 1.6586–1.7042× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.03` | Native C engine | 1.3988× | 1.3812–1.4170× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.03` | Rust engine | 1.5290× | 1.5017–1.5529× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.04` | Python engine | 1.6964× | 1.6687–1.7216× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.04` | Native C engine | 1.3907× | 1.3685–1.4140× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.04` | Rust engine | 1.5066× | 1.4738–1.5382× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.05` | Python engine | 1.6788× | 1.6544–1.7018× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.05` | Native C engine | 1.3836× | 1.3658–1.3988× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.05` | Rust engine | 1.5270× | 1.5084–1.5435× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.06` | Python engine | 1.6856× | 1.6708–1.6998× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.06` | Native C engine | 1.4016× | 1.3901–1.4126× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.06` | Rust engine | 1.5119× | 1.4942–1.5281× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.07` | Python engine | 1.6863× | 1.6647–1.7101× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.07` | Native C engine | 1.3874× | 1.3732–1.4027× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.07` | Rust engine | 1.5256× | 1.5083–1.5445× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.08` | Python engine | 1.7146× | 1.6949–1.7347× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.08` | Native C engine | 1.4149× | 1.4012–1.4285× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.08` | Rust engine | 1.5385× | 1.5100–1.5651× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.09` | Python engine | 1.7076× | 1.6877–1.7271× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.09` | Native C engine | 1.4147× | 1.3933–1.4357× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.09` | Rust engine | 1.5624× | 1.5407–1.5814× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.10` | Python engine | 1.6840× | 1.6522–1.7196× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.10` | Native C engine | 1.4092× | 1.3960–1.4242× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.10` | Rust engine | 1.5377× | 1.5178–1.5598× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.11` | Python engine | 1.7115× | 1.6962–1.7265× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.11` | Native C engine | 1.3993× | 1.3784–1.4183× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.11` | Rust engine | 1.5458× | 1.5291–1.5616× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.12` | Python engine | 1.6977× | 1.6773–1.7183× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.12` | Native C engine | 1.4032× | 1.3874–1.4205× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.12` | Rust engine | 1.5273× | 1.5093–1.5437× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.13` | Python engine | 1.7124× | 1.6948–1.7305× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.13` | Native C engine | 1.4109× | 1.3964–1.4250× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.13` | Rust engine | 1.5380× | 1.5258–1.5505× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.14` | Python engine | 1.6869× | 1.6666–1.7056× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.14` | Native C engine | 1.3880× | 1.3732–1.4029× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.14` | Rust engine | 1.5164× | 1.4989–1.5340× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.15` | Python engine | 1.6804× | 1.6625–1.6976× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.15` | Native C engine | 1.3873× | 1.3719–1.4039× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.15` | Rust engine | 1.5224× | 1.4998–1.5446× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.16` | Python engine | 1.6768× | 1.6562–1.6959× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.16` | Native C engine | 1.3752× | 1.3596–1.3909× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.16` | Rust engine | 1.5472× | 1.5291–1.5656× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.17` | Python engine | 1.6946× | 1.6661–1.7220× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.17` | Native C engine | 1.4049× | 1.3826–1.4265× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.17` | Rust engine | 1.5414× | 1.5130–1.5722× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.18` | Python engine | 1.6826× | 1.6673–1.6991× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.18` | Native C engine | 1.3919× | 1.3800–1.4048× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.18` | Rust engine | 1.5373× | 1.5217–1.5536× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.19` | Python engine | 1.6711× | 1.6539–1.6874× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.19` | Native C engine | 1.3736× | 1.3515–1.3978× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.19` | Rust engine | 1.5251× | 1.5083–1.5443× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.20` | Python engine | 1.7049× | 1.6834–1.7264× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.20` | Native C engine | 1.3953× | 1.3755–1.4136× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.20` | Rust engine | 1.5270× | 1.5090–1.5441× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.21` | Python engine | 1.6813× | 1.6557–1.7021× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.21` | Native C engine | 1.3894× | 1.3709–1.4049× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.21` | Rust engine | 1.5182× | 1.5019–1.5343× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.22` | Python engine | 1.7119× | 1.6916–1.7311× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.22` | Native C engine | 1.3909× | 1.3747–1.4079× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.22` | Rust engine | 1.5276× | 1.5113–1.5421× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.23` | Python engine | 1.6806× | 1.6616–1.6989× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.23` | Native C engine | 1.3841× | 1.3731–1.3971× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.23` | Rust engine | 1.5093× | 1.4937–1.5238× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.24` | Python engine | 1.7092× | 1.6742–1.7423× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.24` | Native C engine | 1.4126× | 1.3965–1.4322× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.24` | Rust engine | 1.5389× | 1.5077–1.5701× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.25` | Python engine | 1.7044× | 1.6643–1.7336× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.25` | Native C engine | 1.4082× | 1.3837–1.4342× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.25` | Rust engine | 1.5644× | 1.5451–1.5827× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.26` | Python engine | 1.7156× | 1.7003–1.7312× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.26` | Native C engine | 1.3995× | 1.3844–1.4131× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.26` | Rust engine | 1.5433× | 1.5286–1.5569× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.27` | Python engine | 1.7085× | 1.6894–1.7278× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.27` | Native C engine | 1.3906× | 1.3735–1.4077× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.27` | Rust engine | 1.5457× | 1.5266–1.5634× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.28` | Python engine | 1.6843× | 1.6685–1.7016× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.28` | Native C engine | 1.3844× | 1.3656–1.4011× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.28` | Rust engine | 1.5155× | 1.4980–1.5308× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.29` | Python engine | 1.6742× | 1.6543–1.6920× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.29` | Native C engine | 1.3802× | 1.3691–1.3917× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.29` | Rust engine | 1.5191× | 1.5034–1.5356× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.30` | Python engine | 1.6909× | 1.6746–1.7080× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.30` | Native C engine | 1.3933× | 1.3787–1.4064× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.30` | Rust engine | 1.5252× | 1.5035–1.5448× | 0.52× | FASTER |
| calibration | `cal.large.cold-compile.31` | Python engine | 1.6843× | 1.6513–1.7242× | 0.41× | FASTER |
| calibration | `cal.large.cold-compile.31` | Native C engine | 1.4004× | 1.3726–1.4339× | 1.75× | FASTER |
| calibration | `cal.large.cold-compile.31` | Rust engine | 1.5259× | 1.5028–1.5538× | 0.52× | FASTER |
| calibration | `cal.large.cold-search.00` | Python engine | 0.0950× | 0.0939–0.0960× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.00` | Native C engine | 1.3514× | 1.3186–1.3831× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.00` | Rust engine | 1.1139× | 1.0946–1.1310× | 0.72× | FASTER |
| calibration | `cal.large.cold-search.01` | Python engine | 0.0949× | 0.0928–0.0977× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.01` | Native C engine | 1.3454× | 1.3180–1.3838× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.01` | Rust engine | 1.1117× | 1.0863–1.1446× | 0.94× | FASTER |
| calibration | `cal.large.cold-search.02` | Python engine | 0.0895× | 0.0822–0.0939× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.02` | Native C engine | 1.3467× | 1.3254–1.3640× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.02` | Rust engine | 1.1068× | 1.0908–1.1208× | 0.70× | FASTER |
| calibration | `cal.large.cold-search.03` | Python engine | 0.0938× | 0.0922–0.0958× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.03` | Native C engine | 1.3607× | 1.3309–1.3902× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.03` | Rust engine | 1.1204× | 1.1024–1.1406× | 0.68× | FASTER |
| calibration | `cal.large.cold-search.04` | Python engine | 0.0919× | 0.0904–0.0934× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.04` | Native C engine | 1.3560× | 1.3204–1.3846× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.04` | Rust engine | 1.1100× | 1.0931–1.1265× | 0.94× | FASTER |
| calibration | `cal.large.cold-search.05` | Python engine | 0.0923× | 0.0913–0.0933× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.05` | Native C engine | 1.3463× | 1.3222–1.3713× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.05` | Rust engine | 1.1098× | 1.0967–1.1237× | 0.94× | FASTER |
| calibration | `cal.large.cold-search.06` | Python engine | 0.0896× | 0.0887–0.0904× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.06` | Native C engine | 1.3273× | 1.3049–1.3468× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.06` | Rust engine | 1.0819× | 1.0658–1.0982× | 0.66× | FASTER |
| calibration | `cal.large.cold-search.07` | Python engine | 0.0955× | 0.0944–0.0966× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.07` | Native C engine | 1.3480× | 1.3100–1.3817× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.07` | Rust engine | 1.0924× | 1.0580–1.1217× | 0.72× | FASTER |
| calibration | `cal.large.cold-search.08` | Python engine | 0.0963× | 0.0945–0.0984× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.08` | Native C engine | 1.3653× | 1.3162–1.4137× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.08` | Rust engine | 1.1172× | 1.0759–1.1520× | 0.94× | FASTER |
| calibration | `cal.large.cold-search.09` | Python engine | 0.0930× | 0.0903–0.0957× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.09` | Native C engine | 1.3533× | 1.3136–1.3986× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.09` | Rust engine | 1.1020× | 1.0688–1.1357× | 0.70× | FASTER |
| calibration | `cal.large.cold-search.10` | Python engine | 0.0927× | 0.0915–0.0937× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.10` | Native C engine | 1.2844× | 1.1614–1.3698× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.10` | Rust engine | 1.1128× | 1.0923–1.1349× | 0.94× | FASTER |
| calibration | `cal.large.cold-search.11` | Python engine | 0.0924× | 0.0913–0.0939× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.11` | Native C engine | 1.3533× | 1.3248–1.3840× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.11` | Rust engine | 1.1083× | 1.0857–1.1341× | 0.67× | FASTER |
| calibration | `cal.large.cold-search.12` | Python engine | 0.0911× | 0.0836–0.0969× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.12` | Native C engine | 1.3376× | 1.2493–1.4332× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.12` | Rust engine | 1.1032× | 1.0625–1.1452× | 0.94× | FASTER |
| calibration | `cal.large.cold-search.13` | Python engine | 0.0901× | 0.0887–0.0914× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.13` | Native C engine | 1.2770× | 1.1554–1.3580× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.13` | Rust engine | 1.0906× | 1.0714–1.1125× | 0.94× | FASTER |
| calibration | `cal.large.cold-search.14` | Python engine | 0.0958× | 0.0948–0.0970× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.14` | Native C engine | 1.3449× | 1.3199–1.3722× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.14` | Rust engine | 1.1246× | 1.0997–1.1467× | 0.72× | FASTER |
| calibration | `cal.large.cold-search.15` | Python engine | 0.0958× | 0.0918–0.1002× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.15` | Native C engine | 1.3325× | 1.2511–1.4069× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.15` | Rust engine | 1.1163× | 1.0503–1.1766× | 0.70× | FASTER |
| calibration | `cal.large.cold-search.16` | Python engine | 0.0939× | 0.0928–0.0951× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.16` | Native C engine | 1.3505× | 1.3229–1.3769× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.16` | Rust engine | 1.1030× | 1.0739–1.1290× | 0.94× | FASTER |
| calibration | `cal.large.cold-search.17` | Python engine | 0.0937× | 0.0921–0.0958× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.17` | Native C engine | 1.3797× | 1.3517–1.4166× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.17` | Rust engine | 1.1136× | 1.0957–1.1371× | 0.94× | FASTER |
| calibration | `cal.large.cold-search.18` | Python engine | 0.0918× | 0.0907–0.0931× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.18` | Native C engine | 1.3521× | 1.3254–1.3807× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.18` | Rust engine | 1.0965× | 1.0789–1.1137× | 0.68× | FASTER |
| calibration | `cal.large.cold-search.19` | Python engine | 0.0909× | 0.0896–0.0923× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.19` | Native C engine | 1.3460× | 1.3200–1.3752× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.19` | Rust engine | 1.0889× | 1.0621–1.1185× | 0.66× | FASTER |
| calibration | `cal.large.cold-search.20` | Python engine | 0.0914× | 0.0899–0.0930× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.20` | Native C engine | 1.3560× | 1.3303–1.3835× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.20` | Rust engine | 1.0948× | 1.0729–1.1200× | 0.94× | FASTER |
| calibration | `cal.large.cold-search.21` | Python engine | 0.0963× | 0.0954–0.0971× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.21` | Native C engine | 1.3767× | 1.3570–1.3952× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.21` | Rust engine | 1.1220× | 1.1025–1.1392× | 0.72× | FASTER |
| calibration | `cal.large.cold-search.22` | Python engine | 0.0948× | 0.0934–0.0963× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.22` | Native C engine | 1.3399× | 1.3153–1.3632× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.22` | Rust engine | 1.1111× | 1.0918–1.1281× | 0.94× | FASTER |
| calibration | `cal.large.cold-search.23` | Python engine | 0.0942× | 0.0918–0.0976× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.23` | Native C engine | 1.3519× | 1.2897–1.4160× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.23` | Rust engine | 1.1091× | 1.0972–1.1211× | 0.94× | FASTER |
| calibration | `cal.large.cold-search.24` | Python engine | 0.0929× | 0.0914–0.0943× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.24` | Native C engine | 1.3474× | 1.3210–1.3735× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.24` | Rust engine | 1.0931× | 1.0770–1.1107× | 0.69× | FASTER |
| calibration | `cal.large.cold-search.25` | Python engine | 0.0931× | 0.0912–0.0955× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.25` | Native C engine | 1.3746× | 1.3352–1.4244× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.25` | Rust engine | 1.1133× | 1.0844–1.1457× | 0.67× | FASTER |
| calibration | `cal.large.cold-search.26` | Python engine | 0.0930× | 0.0901–0.0965× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.26` | Native C engine | 1.3831× | 1.3266–1.4468× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.26` | Rust engine | 1.1252× | 1.1003–1.1561× | 0.94× | FASTER |
| calibration | `cal.large.cold-search.27` | Python engine | 0.0904× | 0.0886–0.0920× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.27` | Native C engine | 1.3386× | 1.3187–1.3568× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.27` | Rust engine | 1.1097× | 1.0872–1.1345× | 0.66× | FASTER |
| calibration | `cal.large.cold-search.28` | Python engine | 0.0968× | 0.0947–0.0992× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.28` | Native C engine | 1.3546× | 1.2977–1.4097× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.28` | Rust engine | 1.1000× | 1.0172–1.1616× | 0.94× | FASTER |
| calibration | `cal.large.cold-search.29` | Python engine | 0.0957× | 0.0940–0.0975× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.29` | Native C engine | 1.3598× | 1.3268–1.3902× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.29` | Rust engine | 1.1366× | 1.1170–1.1560× | 0.70× | FASTER |
| calibration | `cal.large.cold-search.30` | Python engine | 0.0958× | 0.0941–0.0975× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.30` | Native C engine | 1.3853× | 1.3523–1.4164× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.30` | Rust engine | 1.1415× | 1.1130–1.1656× | 0.94× | FASTER |
| calibration | `cal.large.cold-search.31` | Python engine | 0.0938× | 0.0925–0.0949× | 7.14× | SLOWDOWN |
| calibration | `cal.large.cold-search.31` | Native C engine | 1.3490× | 1.3156–1.3749× | 1.77× | FASTER |
| calibration | `cal.large.cold-search.31` | Rust engine | 1.1054× | 1.0775–1.1279× | 0.94× | FASTER |
| calibration | `cal.large.module-search.00` | Python engine | 0.0241× | 0.0236–0.0249× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.00` | Native C engine | 1.3302× | 1.2976–1.3740× | 0.07× | FASTER |
| calibration | `cal.large.module-search.00` | Rust engine | 0.2192× | 0.2139–0.2265× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.01` | Python engine | 0.0245× | 0.0237–0.0256× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.01` | Native C engine | 1.3539× | 1.3230–1.4058× | 0.07× | FASTER |
| calibration | `cal.large.module-search.01` | Rust engine | 0.2248× | 0.2198–0.2339× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.02` | Python engine | 0.0238× | 0.0224–0.0247× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.02` | Native C engine | 1.2842× | 1.2638–1.3033× | 0.07× | FASTER |
| calibration | `cal.large.module-search.02` | Rust engine | 0.2232× | 0.2216–0.2249× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.03` | Python engine | 0.0258× | 0.0254–0.0261× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.03` | Native C engine | 1.2954× | 1.2834–1.3079× | 0.07× | FASTER |
| calibration | `cal.large.module-search.03` | Rust engine | 0.2306× | 0.2294–0.2318× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.04` | Python engine | 0.0241× | 0.0235–0.0250× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.04` | Native C engine | 1.3780× | 1.3367–1.4280× | 0.07× | FASTER |
| calibration | `cal.large.module-search.04` | Rust engine | 0.2238× | 0.2176–0.2314× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.05` | Python engine | 0.0249× | 0.0237–0.0264× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.05` | Native C engine | 1.3480× | 1.2930–1.4229× | 0.07× | FASTER |
| calibration | `cal.large.module-search.05` | Rust engine | 0.2273× | 0.2165–0.2414× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.06` | Python engine | 0.0246× | 0.0243–0.0248× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.06` | Native C engine | 1.3094× | 1.2867–1.3315× | 0.07× | FASTER |
| calibration | `cal.large.module-search.06` | Rust engine | 0.2223× | 0.2201–0.2240× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.07` | Python engine | 0.0256× | 0.0250–0.0261× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.07` | Native C engine | 1.2814× | 1.2418–1.3130× | 0.07× | FASTER |
| calibration | `cal.large.module-search.07` | Rust engine | 0.2320× | 0.2293–0.2348× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.08` | Python engine | 0.0237× | 0.0236–0.0238× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.08` | Native C engine | 1.3165× | 1.2966–1.3344× | 0.07× | FASTER |
| calibration | `cal.large.module-search.08` | Rust engine | 0.2149× | 0.2120–0.2175× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.09` | Python engine | 0.0241× | 0.0239–0.0243× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.09` | Native C engine | 1.2946× | 1.2814–1.3081× | 0.07× | FASTER |
| calibration | `cal.large.module-search.09` | Rust engine | 0.2178× | 0.2163–0.2195× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.10` | Python engine | 0.0247× | 0.0242–0.0256× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.10` | Native C engine | 1.2863× | 1.1796–1.3647× | 0.07× | FASTER |
| calibration | `cal.large.module-search.10` | Rust engine | 0.2224× | 0.2194–0.2258× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.11` | Python engine | 0.0260× | 0.0257–0.0264× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.11` | Native C engine | 1.3026× | 1.2830–1.3239× | 0.07× | FASTER |
| calibration | `cal.large.module-search.11` | Rust engine | 0.2297× | 0.2266–0.2325× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.12` | Python engine | 0.0237× | 0.0236–0.0239× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.12` | Native C engine | 1.3217× | 1.3042–1.3401× | 0.07× | FASTER |
| calibration | `cal.large.module-search.12` | Rust engine | 0.2170× | 0.2151–0.2187× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.13` | Python engine | 0.0242× | 0.0241–0.0244× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.13` | Native C engine | 1.3116× | 1.2961–1.3259× | 0.07× | FASTER |
| calibration | `cal.large.module-search.13` | Rust engine | 0.2186× | 0.2176–0.2196× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.14` | Python engine | 0.0248× | 0.0246–0.0250× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.14` | Native C engine | 1.3010× | 1.2787–1.3169× | 0.07× | FASTER |
| calibration | `cal.large.module-search.14` | Rust engine | 0.2171× | 0.2101–0.2225× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.15` | Python engine | 0.0271× | 0.0254–0.0303× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.15` | Native C engine | 1.3596× | 1.2835–1.5040× | 0.07× | FASTER |
| calibration | `cal.large.module-search.15` | Rust engine | 0.2438× | 0.2299–0.2716× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.16` | Python engine | 0.0238× | 0.0237–0.0239× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.16` | Native C engine | 1.3332× | 1.3199–1.3461× | 0.07× | FASTER |
| calibration | `cal.large.module-search.16` | Rust engine | 0.2165× | 0.2145–0.2183× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.17` | Python engine | 0.0243× | 0.0242–0.0245× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.17` | Native C engine | 1.2990× | 1.2863–1.3101× | 0.07× | FASTER |
| calibration | `cal.large.module-search.17` | Rust engine | 0.2191× | 0.2179–0.2203× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.18` | Python engine | 0.0248× | 0.0246–0.0250× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.18` | Native C engine | 1.2963× | 1.2824–1.3102× | 0.07× | FASTER |
| calibration | `cal.large.module-search.18` | Rust engine | 0.2220× | 0.2201–0.2240× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.19` | Python engine | 0.0259× | 0.0255–0.0263× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.19` | Native C engine | 1.2990× | 1.2763–1.3182× | 0.07× | FASTER |
| calibration | `cal.large.module-search.19` | Rust engine | 0.2326× | 0.2292–0.2356× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.20` | Python engine | 0.0237× | 0.0235–0.0240× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.20` | Native C engine | 1.2914× | 1.2367–1.3295× | 0.07× | FASTER |
| calibration | `cal.large.module-search.20` | Rust engine | 0.2150× | 0.2130–0.2165× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.21` | Python engine | 0.0247× | 0.0241–0.0259× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.21` | Native C engine | 1.3332× | 1.2913–1.3974× | 0.07× | FASTER |
| calibration | `cal.large.module-search.21` | Rust engine | 0.2232× | 0.2177–0.2333× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.22` | Python engine | 0.0248× | 0.0246–0.0250× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.22` | Native C engine | 1.2619× | 1.1044–1.3586× | 0.07× | FASTER |
| calibration | `cal.large.module-search.22` | Rust engine | 0.2270× | 0.2258–0.2281× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.23` | Python engine | 0.0262× | 0.0257–0.0269× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.23` | Native C engine | 1.3454× | 1.3290–1.3636× | 0.07× | FASTER |
| calibration | `cal.large.module-search.23` | Rust engine | 0.2370× | 0.2337–0.2419× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.24` | Python engine | 0.0237× | 0.0236–0.0239× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.24` | Native C engine | 1.2483× | 1.2022–1.2922× | 0.07× | FASTER |
| calibration | `cal.large.module-search.24` | Rust engine | 0.2149× | 0.2135–0.2163× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.25` | Python engine | 0.0248× | 0.0242–0.0258× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.25` | Native C engine | 1.2554× | 1.1287–1.3424× | 0.07× | FASTER |
| calibration | `cal.large.module-search.25` | Rust engine | 0.2242× | 0.2190–0.2313× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.26` | Python engine | 0.0247× | 0.0246–0.0249× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.26` | Native C engine | 1.2818× | 1.2628–1.2996× | 0.07× | FASTER |
| calibration | `cal.large.module-search.26` | Rust engine | 0.2189× | 0.2134–0.2231× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.27` | Python engine | 0.0257× | 0.0254–0.0260× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.27` | Native C engine | 1.2994× | 1.2824–1.3170× | 0.07× | FASTER |
| calibration | `cal.large.module-search.27` | Rust engine | 0.2289× | 0.2261–0.2317× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.28` | Python engine | 0.0238× | 0.0236–0.0240× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.28` | Native C engine | 1.3160× | 1.3041–1.3297× | 0.07× | FASTER |
| calibration | `cal.large.module-search.28` | Rust engine | 0.2139× | 0.2120–0.2157× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.29` | Python engine | 0.0242× | 0.0241–0.0243× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.29` | Native C engine | 1.2607× | 1.1921–1.3022× | 0.07× | FASTER |
| calibration | `cal.large.module-search.29` | Rust engine | 0.2147× | 0.2118–0.2169× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.30` | Python engine | 0.0246× | 0.0245–0.0248× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.30` | Native C engine | 1.2982× | 1.2798–1.3147× | 0.07× | FASTER |
| calibration | `cal.large.module-search.30` | Rust engine | 0.2183× | 0.2135–0.2221× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-search.31` | Python engine | 0.0256× | 0.0251–0.0260× | 5.79× | SLOWDOWN |
| calibration | `cal.large.module-search.31` | Native C engine | 1.3368× | 1.3174–1.3542× | 0.07× | FASTER |
| calibration | `cal.large.module-search.31` | Rust engine | 0.2282× | 0.2211–0.2333× | 0.07× | SLOWDOWN |
| calibration | `cal.large.module-replace.00` | Python engine | 0.0321× | 0.0316–0.0325× | 8.58× | SLOWDOWN |
| calibration | `cal.large.module-replace.00` | Native C engine | 1.1631× | 1.1494–1.1731× | 0.04× | FASTER |
| calibration | `cal.large.module-replace.00` | Rust engine | 0.1120× | 0.1115–0.1126× | 1.22× | SLOWDOWN |
| calibration | `cal.large.module-replace.01` | Python engine | 0.0263× | 0.0256–0.0267× | 9.06× | SLOWDOWN |
| calibration | `cal.large.module-replace.01` | Native C engine | 1.3710× | 1.3640–1.3778× | 0.04× | FASTER |
| calibration | `cal.large.module-replace.01` | Rust engine | 0.1082× | 0.1072–0.1091× | 2.11× | SLOWDOWN |
| calibration | `cal.large.module-replace.02` | Python engine | 0.0232× | 0.0231–0.0234× | 9.69× | SLOWDOWN |
| calibration | `cal.large.module-replace.02` | Native C engine | 1.6480× | 1.6376–1.6578× | 0.06× | FASTER |
| calibration | `cal.large.module-replace.02` | Rust engine | 0.1008× | 0.0972–0.1032× | 4.89× | SLOWDOWN |
| calibration | `cal.large.module-replace.03` | Python engine | 0.0220× | 0.0204–0.0243× | 10.65× | SLOWDOWN |
| calibration | `cal.large.module-replace.03` | Native C engine | 1.9416× | 1.8804–2.0205× | 0.08× | FASTER |
| calibration | `cal.large.module-replace.03` | Rust engine | 0.1046× | 0.0970–0.1148× | 7.54× | SLOWDOWN |
| calibration | `cal.large.module-replace.04` | Python engine | 0.0328× | 0.0327–0.0330× | 8.56× | SLOWDOWN |
| calibration | `cal.large.module-replace.04` | Native C engine | 1.1772× | 1.1692–1.1854× | 0.04× | FASTER |
| calibration | `cal.large.module-replace.04` | Rust engine | 0.1139× | 0.1130–0.1148× | 1.37× | SLOWDOWN |
| calibration | `cal.large.module-replace.05` | Python engine | 0.0272× | 0.0270–0.0274× | 8.95× | SLOWDOWN |
| calibration | `cal.large.module-replace.05` | Native C engine | 1.3956× | 1.3809–1.4109× | 0.05× | FASTER |
| calibration | `cal.large.module-replace.05` | Rust engine | 0.1058× | 0.1048–0.1069× | 3.18× | SLOWDOWN |
| calibration | `cal.large.module-replace.06` | Python engine | 0.0236× | 0.0230–0.0245× | 9.69× | SLOWDOWN |
| calibration | `cal.large.module-replace.06` | Native C engine | 1.6626× | 1.6204–1.7297× | 0.06× | FASTER |
| calibration | `cal.large.module-replace.06` | Rust engine | 0.1046× | 0.1023–0.1087× | 4.89× | SLOWDOWN |
| calibration | `cal.large.module-replace.07` | Python engine | 0.0214× | 0.0212–0.0217× | 10.58× | SLOWDOWN |
| calibration | `cal.large.module-replace.07` | Native C engine | 1.9275× | 1.9016–1.9574× | 0.09× | FASTER |
| calibration | `cal.large.module-replace.07` | Rust engine | 0.1011× | 0.0995–0.1030× | 8.23× | SLOWDOWN |
| calibration | `cal.large.module-replace.08` | Python engine | 0.0335× | 0.0333–0.0339× | 8.53× | SLOWDOWN |
| calibration | `cal.large.module-replace.08` | Native C engine | 1.1661× | 1.1517–1.1821× | 0.04× | FASTER |
| calibration | `cal.large.module-replace.08` | Rust engine | 0.1106× | 0.1095–0.1119× | 1.66× | SLOWDOWN |
| calibration | `cal.large.module-replace.09` | Python engine | 0.0275× | 0.0270–0.0283× | 8.98× | SLOWDOWN |
| calibration | `cal.large.module-replace.09` | Native C engine | 1.4110× | 1.3821–1.4519× | 0.05× | FASTER |
| calibration | `cal.large.module-replace.09` | Rust engine | 0.1071× | 0.1046–0.1102× | 2.91× | SLOWDOWN |
| calibration | `cal.large.module-replace.10` | Python engine | 0.0236× | 0.0231–0.0246× | 9.69× | SLOWDOWN |
| calibration | `cal.large.module-replace.10` | Native C engine | 1.6628× | 1.6247–1.7323× | 0.06× | FASTER |
| calibration | `cal.large.module-replace.10` | Rust engine | 0.1035× | 0.1007–0.1083× | 4.89× | SLOWDOWN |
| calibration | `cal.large.module-replace.11` | Python engine | 0.0211× | 0.0207–0.0213× | 10.65× | SLOWDOWN |
| calibration | `cal.large.module-replace.11` | Native C engine | 1.8969× | 1.8007–1.9539× | 0.08× | FASTER |
| calibration | `cal.large.module-replace.11` | Rust engine | 0.1013× | 0.1000–0.1023× | 7.54× | SLOWDOWN |
| calibration | `cal.large.module-replace.12` | Python engine | 0.0336× | 0.0332–0.0344× | 8.53× | SLOWDOWN |
| calibration | `cal.large.module-replace.12` | Native C engine | 1.1794× | 1.1603–1.2095× | 0.04× | FASTER |
| calibration | `cal.large.module-replace.12` | Rust engine | 0.1105× | 0.1086–0.1132× | 1.66× | SLOWDOWN |
| calibration | `cal.large.module-replace.13` | Python engine | 0.0271× | 0.0270–0.0272× | 8.95× | SLOWDOWN |
| calibration | `cal.large.module-replace.13` | Native C engine | 1.3772× | 1.3533–1.3949× | 0.05× | FASTER |
| calibration | `cal.large.module-replace.13` | Rust engine | 0.1052× | 0.1046–0.1058× | 3.18× | SLOWDOWN |
| calibration | `cal.large.module-replace.14` | Python engine | 0.0235× | 0.0233–0.0237× | 9.69× | SLOWDOWN |
| calibration | `cal.large.module-replace.14` | Native C engine | 1.6472× | 1.6327–1.6607× | 0.06× | FASTER |
| calibration | `cal.large.module-replace.14` | Rust engine | 0.1043× | 0.1036–0.1050× | 4.89× | SLOWDOWN |
| calibration | `cal.large.module-replace.15` | Python engine | 0.0216× | 0.0213–0.0219× | 10.65× | SLOWDOWN |
| calibration | `cal.large.module-replace.15` | Native C engine | 1.9560× | 1.9231–1.9945× | 0.08× | FASTER |
| calibration | `cal.large.module-replace.15` | Rust engine | 0.1029× | 0.1013–0.1047× | 7.54× | SLOWDOWN |
| calibration | `cal.large.module-replace.16` | Python engine | 0.0337× | 0.0334–0.0340× | 8.53× | SLOWDOWN |
| calibration | `cal.large.module-replace.16` | Native C engine | 1.1748× | 1.1652–1.1842× | 0.04× | FASTER |
| calibration | `cal.large.module-replace.16` | Rust engine | 0.1105× | 0.1092–0.1119× | 1.66× | SLOWDOWN |
| calibration | `cal.large.module-replace.17` | Python engine | 0.0272× | 0.0270–0.0275× | 8.95× | SLOWDOWN |
| calibration | `cal.large.module-replace.17` | Native C engine | 1.3741× | 1.3238–1.4052× | 0.05× | FASTER |
| calibration | `cal.large.module-replace.17` | Rust engine | 0.1043× | 0.1034–0.1051× | 3.18× | SLOWDOWN |
| calibration | `cal.large.module-replace.18` | Python engine | 0.0232× | 0.0231–0.0233× | 9.69× | SLOWDOWN |
| calibration | `cal.large.module-replace.18` | Native C engine | 1.6361× | 1.6196–1.6496× | 0.06× | FASTER |
| calibration | `cal.large.module-replace.18` | Rust engine | 0.1024× | 0.1018–0.1029× | 4.89× | SLOWDOWN |
| calibration | `cal.large.module-replace.19` | Python engine | 0.0213× | 0.0212–0.0215× | 10.58× | SLOWDOWN |
| calibration | `cal.large.module-replace.19` | Native C engine | 1.9433× | 1.9291–1.9578× | 0.09× | FASTER |
| calibration | `cal.large.module-replace.19` | Rust engine | 0.1011× | 0.0998–0.1021× | 8.23× | SLOWDOWN |
| calibration | `cal.large.module-replace.20` | Python engine | 0.0337× | 0.0333–0.0343× | 8.51× | SLOWDOWN |
| calibration | `cal.large.module-replace.20` | Native C engine | 1.1816× | 1.1651–1.2038× | 0.04× | FASTER |
| calibration | `cal.large.module-replace.20` | Rust engine | 0.1071× | 0.1012–0.1112× | 1.81× | SLOWDOWN |
| calibration | `cal.large.module-replace.21` | Python engine | 0.0270× | 0.0269–0.0272× | 8.95× | SLOWDOWN |
| calibration | `cal.large.module-replace.21` | Native C engine | 1.3875× | 1.3794–1.3963× | 0.05× | FASTER |
| calibration | `cal.large.module-replace.21` | Rust engine | 0.1052× | 0.1042–0.1062× | 3.18× | SLOWDOWN |
| calibration | `cal.large.module-replace.22` | Python engine | 0.0232× | 0.0230–0.0236× | 9.69× | SLOWDOWN |
| calibration | `cal.large.module-replace.22` | Native C engine | 1.6045× | 1.5320–1.6635× | 0.06× | FASTER |
| calibration | `cal.large.module-replace.22` | Rust engine | 0.1032× | 0.1019–0.1050× | 4.89× | SLOWDOWN |
| calibration | `cal.large.module-replace.23` | Python engine | 0.0217× | 0.0212–0.0226× | 10.65× | SLOWDOWN |
| calibration | `cal.large.module-replace.23` | Native C engine | 1.9617× | 1.9056–2.0465× | 0.08× | FASTER |
| calibration | `cal.large.module-replace.23` | Rust engine | 0.0994× | 0.0915–0.1065× | 7.54× | SLOWDOWN |
| calibration | `cal.large.module-replace.24` | Python engine | 0.0336× | 0.0335–0.0337× | 8.53× | SLOWDOWN |
| calibration | `cal.large.module-replace.24` | Native C engine | 1.1085× | 1.0674–1.1468× | 0.04× | FASTER |
| calibration | `cal.large.module-replace.24` | Rust engine | 0.1074× | 0.1027–0.1102× | 1.66× | SLOWDOWN |
| calibration | `cal.large.module-replace.25` | Python engine | 0.0271× | 0.0269–0.0273× | 8.95× | SLOWDOWN |
| calibration | `cal.large.module-replace.25` | Native C engine | 1.3861× | 1.3759–1.3946× | 0.05× | FASTER |
| calibration | `cal.large.module-replace.25` | Rust engine | 0.1053× | 0.1045–0.1060× | 3.18× | SLOWDOWN |
| calibration | `cal.large.module-replace.26` | Python engine | 0.0225× | 0.0212–0.0232× | 9.66× | SLOWDOWN |
| calibration | `cal.large.module-replace.26` | Native C engine | 1.6164× | 1.5425–1.6605× | 0.07× | FASTER |
| calibration | `cal.large.module-replace.26` | Rust engine | 0.1010× | 0.0998–0.1020× | 5.22× | SLOWDOWN |
| calibration | `cal.large.module-replace.27` | Python engine | 0.0213× | 0.0213–0.0214× | 10.51× | SLOWDOWN |
| calibration | `cal.large.module-replace.27` | Native C engine | 1.9181× | 1.8589–1.9543× | 0.09× | FASTER |
| calibration | `cal.large.module-replace.27` | Rust engine | 0.1004× | 0.0994–0.1014× | 8.90× | SLOWDOWN |
| calibration | `cal.large.module-replace.28` | Python engine | 0.0333× | 0.0328–0.0340× | 8.50× | SLOWDOWN |
| calibration | `cal.large.module-replace.28` | Native C engine | 1.1814× | 1.1611–1.2092× | 0.04× | FASTER |
| calibration | `cal.large.module-replace.28` | Rust engine | 0.1108× | 0.1090–0.1133× | 1.95× | SLOWDOWN |
| calibration | `cal.large.module-replace.29` | Python engine | 0.0265× | 0.0259–0.0269× | 8.95× | SLOWDOWN |
| calibration | `cal.large.module-replace.29` | Native C engine | 1.3613× | 1.3178–1.3885× | 0.05× | FASTER |
| calibration | `cal.large.module-replace.29` | Rust engine | 0.1042× | 0.1026–0.1054× | 3.18× | SLOWDOWN |
| calibration | `cal.large.module-replace.30` | Python engine | 0.0236× | 0.0231–0.0245× | 9.65× | SLOWDOWN |
| calibration | `cal.large.module-replace.30` | Native C engine | 1.6360× | 1.5325–1.7327× | 0.07× | FASTER |
| calibration | `cal.large.module-replace.30` | Rust engine | 0.1031× | 0.1000–0.1075× | 5.33× | SLOWDOWN |
| calibration | `cal.large.module-replace.31` | Python engine | 0.0217× | 0.0213–0.0223× | 10.58× | SLOWDOWN |
| calibration | `cal.large.module-replace.31` | Native C engine | 1.9759× | 1.9390–2.0341× | 0.09× | FASTER |
| calibration | `cal.large.module-replace.31` | Rust engine | 0.1023× | 0.1002–0.1055× | 8.23× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.00` | Python engine | 0.0174× | 0.0171–0.0178× | 7.21× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.00` | Native C engine | 2.3824× | 2.2362–2.4848× | 0.47× | FASTER |
| calibration | `cal.large.empty-iterator.00` | Rust engine | 0.1626× | 0.1598–0.1659× | 0.46× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.01` | Python engine | 0.0157× | 0.0152–0.0161× | 8.85× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.01` | Native C engine | 2.5177× | 2.4668–2.5756× | 0.57× | FASTER |
| calibration | `cal.large.empty-iterator.01` | Rust engine | 0.1528× | 0.1502–0.1563× | 0.54× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.02` | Python engine | 0.0150× | 0.0149–0.0151× | 10.12× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.02` | Native C engine | 2.4206× | 2.3732–2.4691× | 0.63× | FASTER |
| calibration | `cal.large.empty-iterator.02` | Rust engine | 0.1487× | 0.1471–0.1504× | 0.59× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.03` | Python engine | 0.0147× | 0.0144–0.0152× | 7.47× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.03` | Native C engine | 2.3263× | 2.2600–2.3897× | 0.67× | FASTER |
| calibration | `cal.large.empty-iterator.03` | Rust engine | 0.1510× | 0.1482–0.1544× | 0.62× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.04` | Python engine | 0.0178× | 0.0174–0.0182× | 7.21× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.04` | Native C engine | 2.5433× | 2.4934–2.6003× | 0.47× | FASTER |
| calibration | `cal.large.empty-iterator.04` | Rust engine | 0.1630× | 0.1591–0.1675× | 0.46× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.05` | Python engine | 0.0159× | 0.0158–0.0160× | 8.85× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.05` | Native C engine | 2.5306× | 2.4970–2.5650× | 0.57× | FASTER |
| calibration | `cal.large.empty-iterator.05` | Rust engine | 0.1530× | 0.1514–0.1545× | 0.54× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.06` | Python engine | 0.0158× | 0.0154–0.0162× | 10.12× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.06` | Native C engine | 2.4846× | 2.3445–2.6191× | 0.63× | FASTER |
| calibration | `cal.large.empty-iterator.06` | Rust engine | 0.1531× | 0.1488–0.1576× | 0.59× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.07` | Python engine | 0.0156× | 0.0152–0.0161× | 10.13× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.07` | Native C engine | 2.4261× | 2.3540–2.5016× | 0.68× | FASTER |
| calibration | `cal.large.empty-iterator.07` | Rust engine | 0.1544× | 0.1501–0.1597× | 0.63× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.08` | Python engine | 0.0191× | 0.0188–0.0195× | 7.21× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.08` | Native C engine | 2.5633× | 2.3720–2.7232× | 0.47× | FASTER |
| calibration | `cal.large.empty-iterator.08` | Rust engine | 0.1751× | 0.1722–0.1795× | 0.46× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.09` | Python engine | 0.0154× | 0.0144–0.0160× | 8.77× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.09` | Native C engine | 2.4709× | 2.3688–2.5448× | 0.56× | FASTER |
| calibration | `cal.large.empty-iterator.09` | Rust engine | 0.1512× | 0.1492–0.1533× | 0.53× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.10` | Python engine | 0.0159× | 0.0155–0.0163× | 10.12× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.10` | Native C engine | 2.5681× | 2.4939–2.6485× | 0.63× | FASTER |
| calibration | `cal.large.empty-iterator.10` | Rust engine | 0.1564× | 0.1527–0.1603× | 0.59× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.11` | Python engine | 0.0152× | 0.0150–0.0155× | 10.71× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.11` | Native C engine | 2.3704× | 2.3107–2.4334× | 0.68× | FASTER |
| calibration | `cal.large.empty-iterator.11` | Rust engine | 0.1510× | 0.1493–0.1527× | 0.63× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.12` | Python engine | 0.0189× | 0.0187–0.0192× | 7.21× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.12` | Native C engine | 2.6325× | 2.5185–2.7202× | 0.47× | FASTER |
| calibration | `cal.large.empty-iterator.12` | Rust engine | 0.1716× | 0.1665–0.1761× | 0.46× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.13` | Python engine | 0.0161× | 0.0159–0.0165× | 8.77× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.13` | Native C engine | 2.5260× | 2.4838–2.5734× | 0.56× | FASTER |
| calibration | `cal.large.empty-iterator.13` | Rust engine | 0.1547× | 0.1521–0.1580× | 0.53× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.14` | Python engine | 0.0153× | 0.0152–0.0155× | 10.00× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.14` | Native C engine | 2.3757× | 2.2142–2.5028× | 0.64× | FASTER |
| calibration | `cal.large.empty-iterator.14` | Rust engine | 0.1489× | 0.1457–0.1522× | 0.60× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.15` | Python engine | 0.0154× | 0.0152–0.0155× | 10.13× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.15` | Native C engine | 2.4401× | 2.3812–2.4991× | 0.68× | FASTER |
| calibration | `cal.large.empty-iterator.15` | Rust engine | 0.1528× | 0.1509–0.1546× | 0.63× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.16` | Python engine | 0.0173× | 0.0172–0.0174× | 7.33× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.16` | Native C engine | 2.4803× | 2.3960–2.5346× | 0.48× | FASTER |
| calibration | `cal.large.empty-iterator.16` | Rust engine | 0.1604× | 0.1593–0.1617× | 0.47× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.17` | Python engine | 0.0166× | 0.0164–0.0167× | 8.77× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.17` | Native C engine | 2.5720× | 2.5371–2.6075× | 0.56× | FASTER |
| calibration | `cal.large.empty-iterator.17` | Rust engine | 0.1592× | 0.1575–0.1609× | 0.53× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.18` | Python engine | 0.0150× | 0.0145–0.0154× | 6.62× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.18` | Native C engine | 2.3810× | 2.2141–2.5058× | 0.61× | FASTER |
| calibration | `cal.large.empty-iterator.18` | Rust engine | 0.1538× | 0.1489–0.1570× | 0.57× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.19` | Python engine | 0.0148× | 0.0137–0.0164× | 6.41× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.19` | Native C engine | 2.5143× | 2.3409–2.7839× | 0.69× | FASTER |
| calibration | `cal.large.empty-iterator.19` | Rust engine | 0.1547× | 0.1416–0.1706× | 0.64× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.20` | Python engine | 0.0191× | 0.0172–0.0215× | 7.07× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.20` | Native C engine | 2.7793× | 2.5212–3.1610× | 0.43× | FASTER |
| calibration | `cal.large.empty-iterator.20` | Rust engine | 0.1775× | 0.1627–0.1976× | 0.43× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.21` | Python engine | 0.0165× | 0.0152–0.0180× | 8.77× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.21` | Native C engine | 2.6485× | 2.4631–2.9313× | 0.56× | FASTER |
| calibration | `cal.large.empty-iterator.21` | Rust engine | 0.1588× | 0.1423–0.1782× | 0.53× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.22` | Python engine | 0.0148× | 0.0140–0.0156× | 6.62× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.22` | Native C engine | 2.3184× | 2.0849–2.5278× | 0.61× | FASTER |
| calibration | `cal.large.empty-iterator.22` | Rust engine | 0.1569× | 0.1504–0.1653× | 0.57× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.23` | Python engine | 0.0159× | 0.0146–0.0176× | 10.61× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.23` | Native C engine | 2.3342× | 2.0381–2.6391× | 0.68× | FASTER |
| calibration | `cal.large.empty-iterator.23` | Rust engine | 0.1563× | 0.1382–0.1752× | 0.63× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.24` | Python engine | 0.0181× | 0.0174–0.0188× | 7.21× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.24` | Native C engine | 2.6875× | 2.4399–2.8620× | 0.47× | FASTER |
| calibration | `cal.large.empty-iterator.24` | Rust engine | 0.1727× | 0.1667–0.1782× | 0.46× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.25` | Python engine | 0.0161× | 0.0155–0.0165× | 8.60× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.25` | Native C engine | 2.3521× | 2.1348–2.5606× | 0.51× | FASTER |
| calibration | `cal.large.empty-iterator.25` | Rust engine | 0.1546× | 0.1414–0.1662× | 0.49× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.26` | Python engine | 0.0143× | 0.0136–0.0150× | 10.12× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.26` | Native C engine | 2.5836× | 2.4998–2.6808× | 0.63× | FASTER |
| calibration | `cal.large.empty-iterator.26` | Rust engine | 0.1586× | 0.1533–0.1647× | 0.59× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.27` | Python engine | 0.0151× | 0.0134–0.0171× | 10.13× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.27` | Native C engine | 2.5193× | 2.3198–2.7192× | 0.68× | FASTER |
| calibration | `cal.large.empty-iterator.27` | Rust engine | 0.1622× | 0.1497–0.1804× | 0.63× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.28` | Python engine | 0.0191× | 0.0176–0.0204× | 7.21× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.28` | Native C engine | 2.6147× | 2.3703–2.7879× | 0.47× | FASTER |
| calibration | `cal.large.empty-iterator.28` | Rust engine | 0.1772× | 0.1740–0.1813× | 0.46× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.29` | Python engine | 0.0163× | 0.0158–0.0170× | 8.85× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.29` | Native C engine | 2.5661× | 2.5067–2.6498× | 0.57× | FASTER |
| calibration | `cal.large.empty-iterator.29` | Rust engine | 0.1571× | 0.1532–0.1634× | 0.54× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.30` | Python engine | 0.0152× | 0.0148–0.0156× | 10.00× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.30` | Native C engine | 2.5132× | 2.4565–2.5762× | 0.64× | FASTER |
| calibration | `cal.large.empty-iterator.30` | Rust engine | 0.1520× | 0.1489–0.1564× | 0.60× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.31` | Python engine | 0.0151× | 0.0149–0.0152× | 10.13× | SLOWDOWN |
| calibration | `cal.large.empty-iterator.31` | Native C engine | 2.3005× | 2.1394–2.4265× | 0.68× | FASTER |
| calibration | `cal.large.empty-iterator.31` | Rust engine | 0.1540× | 0.1519–0.1561× | 0.63× | SLOWDOWN |
| calibration | `cal.large.references.00` | Python engine | 0.0216× | 0.0212–0.0221× | 6.44× | SLOWDOWN |
| calibration | `cal.large.references.00` | Native C engine | 1.4341× | 1.4071–1.4625× | 0.08× | FASTER |
| calibration | `cal.large.references.00` | Rust engine | 0.1956× | 0.1922–0.1993× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.01` | Python engine | 0.0212× | 0.0209–0.0214× | 6.45× | SLOWDOWN |
| calibration | `cal.large.references.01` | Native C engine | 1.4133× | 1.3872–1.4482× | 0.08× | FASTER |
| calibration | `cal.large.references.01` | Rust engine | 0.1926× | 0.1889–0.1956× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.02` | Python engine | 0.0205× | 0.0189–0.0217× | 6.50× | SLOWDOWN |
| calibration | `cal.large.references.02` | Native C engine | 1.2117× | 1.0008–1.3669× | 0.08× | FASTER |
| calibration | `cal.large.references.02` | Rust engine | 0.1828× | 0.1676–0.1923× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.03` | Python engine | 0.0250× | 0.0240–0.0258× | 6.50× | SLOWDOWN |
| calibration | `cal.large.references.03` | Native C engine | 1.3647× | 1.3324–1.3958× | 0.08× | FASTER |
| calibration | `cal.large.references.03` | Rust engine | 0.2211× | 0.2165–0.2255× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.04` | Python engine | 0.0209× | 0.0206–0.0212× | 6.45× | SLOWDOWN |
| calibration | `cal.large.references.04` | Native C engine | 1.4500× | 1.4231–1.4759× | 0.08× | FASTER |
| calibration | `cal.large.references.04` | Rust engine | 0.1908× | 0.1860–0.1953× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.05` | Python engine | 0.0207× | 0.0195–0.0228× | 6.95× | SLOWDOWN |
| calibration | `cal.large.references.05` | Native C engine | 1.6550× | 1.5630–1.8233× | 0.00× | FASTER |
| calibration | `cal.large.references.05` | Rust engine | 0.2377× | 0.2197–0.2611× | 0.00× | SLOWDOWN |
| calibration | `cal.large.references.06` | Python engine | 0.0235× | 0.0229–0.0240× | 6.50× | SLOWDOWN |
| calibration | `cal.large.references.06` | Native C engine | 1.4180× | 1.3936–1.4456× | 0.08× | FASTER |
| calibration | `cal.large.references.06` | Rust engine | 0.2110× | 0.2083–0.2136× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.07` | Python engine | 0.0263× | 0.0242–0.0305× | 6.50× | SLOWDOWN |
| calibration | `cal.large.references.07` | Native C engine | 1.4608× | 1.3375–1.6932× | 0.08× | FASTER |
| calibration | `cal.large.references.07` | Rust engine | 0.2297× | 0.2103–0.2654× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.08` | Python engine | 0.0207× | 0.0198–0.0220× | 6.45× | SLOWDOWN |
| calibration | `cal.large.references.08` | Native C engine | 1.4215× | 1.2628–1.5657× | 0.08× | FASTER |
| calibration | `cal.large.references.08` | Rust engine | 0.1840× | 0.1753–0.1967× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.09` | Python engine | 0.0220× | 0.0210–0.0227× | 6.44× | SLOWDOWN |
| calibration | `cal.large.references.09` | Native C engine | 1.4069× | 1.3622–1.4446× | 0.08× | FASTER |
| calibration | `cal.large.references.09` | Rust engine | 0.1937× | 0.1846–0.2023× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.10` | Python engine | 0.0218× | 0.0214–0.0224× | 6.50× | SLOWDOWN |
| calibration | `cal.large.references.10` | Native C engine | 1.3660× | 1.3421–1.3887× | 0.08× | FASTER |
| calibration | `cal.large.references.10` | Rust engine | 0.1987× | 0.1911–0.2048× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.11` | Python engine | 0.0214× | 0.0208–0.0220× | 7.01× | SLOWDOWN |
| calibration | `cal.large.references.11` | Native C engine | 1.4944× | 1.4603–1.5241× | 0.00× | FASTER |
| calibration | `cal.large.references.11` | Rust engine | 0.2427× | 0.2309–0.2513× | 0.00× | SLOWDOWN |
| calibration | `cal.large.references.12` | Python engine | 0.0229× | 0.0217–0.0248× | 6.44× | SLOWDOWN |
| calibration | `cal.large.references.12` | Native C engine | 1.5105× | 1.4430–1.6257× | 0.08× | FASTER |
| calibration | `cal.large.references.12` | Rust engine | 0.2079× | 0.1987–0.2241× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.13` | Python engine | 0.0217× | 0.0214–0.0220× | 6.45× | SLOWDOWN |
| calibration | `cal.large.references.13` | Native C engine | 1.4359× | 1.4194–1.4523× | 0.08× | FASTER |
| calibration | `cal.large.references.13` | Rust engine | 0.1963× | 0.1928–0.1993× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.14` | Python engine | 0.0219× | 0.0217–0.0222× | 6.50× | SLOWDOWN |
| calibration | `cal.large.references.14` | Native C engine | 1.3324× | 1.2042–1.4149× | 0.08× | FASTER |
| calibration | `cal.large.references.14` | Rust engine | 0.1922× | 0.1885–0.1957× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.15` | Python engine | 0.0253× | 0.0248–0.0259× | 6.50× | SLOWDOWN |
| calibration | `cal.large.references.15` | Native C engine | 1.3287× | 1.2846–1.3674× | 0.08× | FASTER |
| calibration | `cal.large.references.15` | Rust engine | 0.2221× | 0.2176–0.2266× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.16` | Python engine | 0.0217× | 0.0204–0.0234× | 6.45× | SLOWDOWN |
| calibration | `cal.large.references.16` | Native C engine | 1.5015× | 1.4266–1.6174× | 0.08× | FASTER |
| calibration | `cal.large.references.16` | Rust engine | 0.1993× | 0.1900–0.2120× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.17` | Python engine | 0.0196× | 0.0185–0.0214× | 6.95× | SLOWDOWN |
| calibration | `cal.large.references.17` | Native C engine | 1.6212× | 1.4879–1.7917× | 0.00× | FASTER |
| calibration | `cal.large.references.17` | Rust engine | 0.2315× | 0.2128–0.2551× | 0.00× | SLOWDOWN |
| calibration | `cal.large.references.18` | Python engine | 0.0250× | 0.0228–0.0279× | 6.50× | SLOWDOWN |
| calibration | `cal.large.references.18` | Native C engine | 1.5714× | 1.4345–1.7430× | 0.08× | FASTER |
| calibration | `cal.large.references.18` | Rust engine | 0.2282× | 0.2012–0.2583× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.19` | Python engine | 0.0233× | 0.0222–0.0244× | 6.50× | SLOWDOWN |
| calibration | `cal.large.references.19` | Native C engine | 1.2082× | 1.0717–1.3282× | 0.08× | FASTER |
| calibration | `cal.large.references.19` | Rust engine | 0.2148× | 0.2095–0.2197× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.20` | Python engine | 0.0196× | 0.0192–0.0199× | 6.45× | SLOWDOWN |
| calibration | `cal.large.references.20` | Native C engine | 1.3060× | 1.1233–1.4512× | 0.08× | FASTER |
| calibration | `cal.large.references.20` | Rust engine | 0.1767× | 0.1721–0.1812× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.21` | Python engine | 0.0229× | 0.0219–0.0248× | 6.44× | SLOWDOWN |
| calibration | `cal.large.references.21` | Native C engine | 1.4685× | 1.3540–1.6258× | 0.08× | FASTER |
| calibration | `cal.large.references.21` | Rust engine | 0.2059× | 0.1907–0.2269× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.22` | Python engine | 0.0228× | 0.0216–0.0247× | 6.50× | SLOWDOWN |
| calibration | `cal.large.references.22` | Native C engine | 1.3834× | 1.2295–1.5513× | 0.08× | FASTER |
| calibration | `cal.large.references.22` | Rust engine | 0.2055× | 0.1833–0.2271× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.23` | Python engine | 0.0215× | 0.0207–0.0225× | 7.01× | SLOWDOWN |
| calibration | `cal.large.references.23` | Native C engine | 1.4813× | 1.3322–1.5987× | 0.00× | FASTER |
| calibration | `cal.large.references.23` | Rust engine | 0.2565× | 0.2473–0.2698× | 0.00× | SLOWDOWN |
| calibration | `cal.large.references.24` | Python engine | 0.0220× | 0.0210–0.0238× | 6.44× | SLOWDOWN |
| calibration | `cal.large.references.24` | Native C engine | 1.4732× | 1.4132–1.5833× | 0.08× | FASTER |
| calibration | `cal.large.references.24` | Rust engine | 0.2023× | 0.1923–0.2187× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.25` | Python engine | 0.0211× | 0.0208–0.0215× | 6.45× | SLOWDOWN |
| calibration | `cal.large.references.25` | Native C engine | 1.4363× | 1.4056–1.4680× | 0.08× | FASTER |
| calibration | `cal.large.references.25` | Rust engine | 0.1906× | 0.1816–0.1981× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.26` | Python engine | 0.0217× | 0.0203–0.0238× | 6.50× | SLOWDOWN |
| calibration | `cal.large.references.26` | Native C engine | 1.3743× | 1.1835–1.5655× | 0.08× | FASTER |
| calibration | `cal.large.references.26` | Rust engine | 0.1959× | 0.1815–0.2155× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.27` | Python engine | 0.0253× | 0.0249–0.0258× | 6.50× | SLOWDOWN |
| calibration | `cal.large.references.27` | Native C engine | 1.3947× | 1.3653–1.4257× | 0.08× | FASTER |
| calibration | `cal.large.references.27` | Rust engine | 0.2227× | 0.2191–0.2266× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.28` | Python engine | 0.0210× | 0.0200–0.0227× | 6.45× | SLOWDOWN |
| calibration | `cal.large.references.28` | Native C engine | 1.3857× | 1.2119–1.5584× | 0.08× | FASTER |
| calibration | `cal.large.references.28` | Rust engine | 0.1883× | 0.1821–0.1936× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.29` | Python engine | 0.0196× | 0.0191–0.0201× | 6.95× | SLOWDOWN |
| calibration | `cal.large.references.29` | Native C engine | 1.5650× | 1.5221–1.6080× | 0.00× | FASTER |
| calibration | `cal.large.references.29` | Rust engine | 0.2358× | 0.2326–0.2392× | 0.00× | SLOWDOWN |
| calibration | `cal.large.references.30` | Python engine | 0.0233× | 0.0227–0.0240× | 6.50× | SLOWDOWN |
| calibration | `cal.large.references.30` | Native C engine | 1.4101× | 1.3765–1.4447× | 0.08× | FASTER |
| calibration | `cal.large.references.30` | Rust engine | 0.2108× | 0.2059–0.2155× | 0.06× | SLOWDOWN |
| calibration | `cal.large.references.31` | Python engine | 0.0240× | 0.0231–0.0247× | 6.50× | SLOWDOWN |
| calibration | `cal.large.references.31` | Native C engine | 1.3576× | 1.3303–1.3849× | 0.08× | FASTER |
| calibration | `cal.large.references.31` | Rust engine | 0.2165× | 0.2115–0.2214× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.00` | Python engine | 0.0266× | 0.0258–0.0281× | 6.52× | SLOWDOWN |
| calibration | `cal.large.conditionals.00` | Native C engine | 1.4660× | 1.4214–1.5474× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.00` | Rust engine | 0.1442× | 0.1381–0.1516× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.01` | Python engine | 0.0267× | 0.0264–0.0271× | 6.52× | SLOWDOWN |
| calibration | `cal.large.conditionals.01` | Native C engine | 1.4207× | 1.4057–1.4348× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.01` | Rust engine | 0.1522× | 0.1483–0.1545× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.02` | Python engine | 0.0304× | 0.0277–0.0347× | 6.57× | SLOWDOWN |
| calibration | `cal.large.conditionals.02` | Native C engine | 1.5656× | 1.4337–1.7734× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.02` | Rust engine | 0.1622× | 0.1453–0.1829× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.03` | Python engine | 0.0287× | 0.0281–0.0293× | 6.57× | SLOWDOWN |
| calibration | `cal.large.conditionals.03` | Native C engine | 1.3108× | 1.2814–1.3435× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.03` | Rust engine | 0.1734× | 0.1605–0.1820× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.04` | Python engine | 0.0270× | 0.0263–0.0282× | 6.52× | SLOWDOWN |
| calibration | `cal.large.conditionals.04` | Native C engine | 1.4744× | 1.4411–1.5338× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.04` | Rust engine | 0.1499× | 0.1449–0.1559× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.05` | Python engine | 0.0276× | 0.0272–0.0280× | 6.52× | SLOWDOWN |
| calibration | `cal.large.conditionals.05` | Native C engine | 1.3936× | 1.2708–1.4656× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.05` | Rust engine | 0.1502× | 0.1488–0.1517× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.06` | Python engine | 0.0278× | 0.0272–0.0283× | 6.57× | SLOWDOWN |
| calibration | `cal.large.conditionals.06` | Native C engine | 1.3899× | 1.3764–1.4029× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.06` | Rust engine | 0.1521× | 0.1466–0.1556× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.07` | Python engine | 0.0297× | 0.0290–0.0304× | 6.57× | SLOWDOWN |
| calibration | `cal.large.conditionals.07` | Native C engine | 1.3139× | 1.2298–1.3779× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.07` | Rust engine | 0.1669× | 0.1639–0.1702× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.08` | Python engine | 0.0265× | 0.0261–0.0270× | 6.52× | SLOWDOWN |
| calibration | `cal.large.conditionals.08` | Native C engine | 1.3978× | 1.3842–1.4143× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.08` | Rust engine | 0.1608× | 0.1595–0.1625× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.09` | Python engine | 0.0272× | 0.0269–0.0275× | 6.52× | SLOWDOWN |
| calibration | `cal.large.conditionals.09` | Native C engine | 1.3895× | 1.3566–1.4149× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.09` | Rust engine | 0.1488× | 0.1456–0.1509× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.10` | Python engine | 0.0287× | 0.0276–0.0306× | 6.57× | SLOWDOWN |
| calibration | `cal.large.conditionals.10` | Native C engine | 1.4314× | 1.3774–1.5229× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.10` | Rust engine | 0.1670× | 0.1606–0.1782× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.11` | Python engine | 0.0308× | 0.0302–0.0314× | 6.57× | SLOWDOWN |
| calibration | `cal.large.conditionals.11` | Native C engine | 1.3986× | 1.3854–1.4117× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.11` | Rust engine | 0.1558× | 0.1393–0.1665× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.12` | Python engine | 0.0280× | 0.0273–0.0292× | 6.52× | SLOWDOWN |
| calibration | `cal.large.conditionals.12` | Native C engine | 1.4909× | 1.4378–1.5617× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.12` | Rust engine | 0.1516× | 0.1475–0.1580× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.13` | Python engine | 0.0269× | 0.0262–0.0281× | 6.52× | SLOWDOWN |
| calibration | `cal.large.conditionals.13` | Native C engine | 1.3701× | 1.3255–1.4345× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.13` | Rust engine | 0.1748× | 0.1706–0.1819× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.14` | Python engine | 0.0278× | 0.0275–0.0281× | 6.57× | SLOWDOWN |
| calibration | `cal.large.conditionals.14` | Native C engine | 1.3584× | 1.3353–1.3833× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.14` | Rust engine | 0.1696× | 0.1679–0.1712× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.15` | Python engine | 0.0303× | 0.0297–0.0308× | 6.57× | SLOWDOWN |
| calibration | `cal.large.conditionals.15` | Native C engine | 1.3708× | 1.3310–1.4036× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.15` | Rust engine | 0.1632× | 0.1612–0.1652× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.16` | Python engine | 0.0265× | 0.0263–0.0268× | 6.52× | SLOWDOWN |
| calibration | `cal.large.conditionals.16` | Native C engine | 1.3789× | 1.2869–1.4332× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.16` | Rust engine | 0.1546× | 0.1518–0.1565× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.17` | Python engine | 0.0266× | 0.0263–0.0271× | 6.52× | SLOWDOWN |
| calibration | `cal.large.conditionals.17` | Native C engine | 1.3854× | 1.3603–1.4101× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.17` | Rust engine | 0.1612× | 0.1559–0.1645× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.18` | Python engine | 0.0280× | 0.0272–0.0287× | 6.57× | SLOWDOWN |
| calibration | `cal.large.conditionals.18` | Native C engine | 1.4183× | 1.3989–1.4384× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.18` | Rust engine | 0.1531× | 0.1518–0.1544× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.19` | Python engine | 0.0299× | 0.0294–0.0306× | 6.57× | SLOWDOWN |
| calibration | `cal.large.conditionals.19` | Native C engine | 1.3501× | 1.3136–1.3824× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.19` | Rust engine | 0.1684× | 0.1660–0.1707× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.20` | Python engine | 0.0276× | 0.0268–0.0290× | 6.52× | SLOWDOWN |
| calibration | `cal.large.conditionals.20` | Native C engine | 1.4557× | 1.4370–1.4701× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.20` | Rust engine | 0.1387× | 0.1268–0.1462× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.21` | Python engine | 0.0270× | 0.0267–0.0273× | 6.52× | SLOWDOWN |
| calibration | `cal.large.conditionals.21` | Native C engine | 1.4143× | 1.3954–1.4310× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.21` | Rust engine | 0.1453× | 0.1349–0.1515× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.22` | Python engine | 0.0275× | 0.0270–0.0280× | 6.57× | SLOWDOWN |
| calibration | `cal.large.conditionals.22` | Native C engine | 1.3768× | 1.3430–1.4032× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.22` | Rust engine | 0.1588× | 0.1540–0.1623× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.23` | Python engine | 0.0293× | 0.0282–0.0302× | 6.57× | SLOWDOWN |
| calibration | `cal.large.conditionals.23` | Native C engine | 1.3495× | 1.3174–1.3773× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.23` | Rust engine | 0.1617× | 0.1578–0.1656× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.24` | Python engine | 0.0274× | 0.0258–0.0296× | 6.52× | SLOWDOWN |
| calibration | `cal.large.conditionals.24` | Native C engine | 1.5146× | 1.4622–1.6146× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.24` | Rust engine | 0.1497× | 0.1435–0.1600× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.25` | Python engine | 0.0271× | 0.0267–0.0276× | 6.52× | SLOWDOWN |
| calibration | `cal.large.conditionals.25` | Native C engine | 1.4241× | 1.4058–1.4445× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.25` | Rust engine | 0.1542× | 0.1524–0.1562× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.26` | Python engine | 0.0283× | 0.0279–0.0289× | 6.57× | SLOWDOWN |
| calibration | `cal.large.conditionals.26` | Native C engine | 1.4194× | 1.3907–1.4559× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.26` | Rust engine | 0.1585× | 0.1553–0.1626× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.27` | Python engine | 0.0296× | 0.0291–0.0301× | 6.57× | SLOWDOWN |
| calibration | `cal.large.conditionals.27` | Native C engine | 1.3221× | 1.2815–1.3663× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.27` | Rust engine | 0.1804× | 0.1759–0.1843× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.28` | Python engine | 0.0272× | 0.0260–0.0294× | 6.52× | SLOWDOWN |
| calibration | `cal.large.conditionals.28` | Native C engine | 1.2803× | 1.0654–1.4931× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.28` | Rust engine | 0.1748× | 0.1657–0.1906× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.29` | Python engine | 0.0268× | 0.0266–0.0270× | 6.52× | SLOWDOWN |
| calibration | `cal.large.conditionals.29` | Native C engine | 1.4139× | 1.4039–1.4260× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.29` | Rust engine | 0.1459× | 0.1410–0.1495× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.30` | Python engine | 0.0289× | 0.0262–0.0316× | 6.57× | SLOWDOWN |
| calibration | `cal.large.conditionals.30` | Native C engine | 1.4182× | 1.4003–1.4345× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.30` | Rust engine | 0.1548× | 0.1525–0.1571× | 0.06× | SLOWDOWN |
| calibration | `cal.large.conditionals.31` | Python engine | 0.0312× | 0.0290–0.0350× | 6.57× | SLOWDOWN |
| calibration | `cal.large.conditionals.31` | Native C engine | 1.4304× | 1.3469–1.5850× | 0.08× | FASTER |
| calibration | `cal.large.conditionals.31` | Rust engine | 0.1822× | 0.1715–0.2038× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.00` | Python engine | 0.0166× | 0.0159–0.0170× | 7.38× | SLOWDOWN |
| calibration | `cal.large.branch-control.00` | Native C engine | 1.2545× | 1.2422–1.2665× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.00` | Rust engine | 0.1630× | 0.1595–0.1657× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.01` | Python engine | 0.0152× | 0.0150–0.0154× | 9.07× | SLOWDOWN |
| calibration | `cal.large.branch-control.01` | Native C engine | 1.4892× | 1.3584–1.5731× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.01` | Rust engine | 0.1841× | 0.1789–0.1879× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.02` | Python engine | 0.0142× | 0.0139–0.0145× | 12.46× | SLOWDOWN |
| calibration | `cal.large.branch-control.02` | Native C engine | 2.0663× | 2.0223–2.1070× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.02` | Rust engine | 0.2116× | 0.2003–0.2191× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.03` | Python engine | 0.0130× | 0.0128–0.0132× | 19.23× | SLOWDOWN |
| calibration | `cal.large.branch-control.03` | Native C engine | 2.6198× | 2.5340–2.6958× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.03` | Rust engine | 0.2348× | 0.2283–0.2402× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.04` | Python engine | 0.0171× | 0.0169–0.0173× | 7.38× | SLOWDOWN |
| calibration | `cal.large.branch-control.04` | Native C engine | 1.2738× | 1.2572–1.2895× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.04` | Rust engine | 0.1661× | 0.1648–0.1673× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.05` | Python engine | 0.0154× | 0.0152–0.0156× | 9.07× | SLOWDOWN |
| calibration | `cal.large.branch-control.05` | Native C engine | 1.5334× | 1.5168–1.5494× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.05` | Rust engine | 0.1831× | 0.1791–0.1864× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.06` | Python engine | 0.0152× | 0.0138–0.0176× | 12.46× | SLOWDOWN |
| calibration | `cal.large.branch-control.06` | Native C engine | 2.2031× | 1.9996–2.5824× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.06` | Rust engine | 0.2323× | 0.2109–0.2730× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.07` | Python engine | 0.0128× | 0.0124–0.0131× | 19.23× | SLOWDOWN |
| calibration | `cal.large.branch-control.07` | Native C engine | 2.6207× | 2.5558–2.6892× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.07` | Rust engine | 0.2349× | 0.2281–0.2397× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.08` | Python engine | 0.0172× | 0.0169–0.0177× | 7.38× | SLOWDOWN |
| calibration | `cal.large.branch-control.08` | Native C engine | 1.2469× | 1.2260–1.2802× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.08` | Rust engine | 0.1660× | 0.1626–0.1704× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.09` | Python engine | 0.0151× | 0.0150–0.0153× | 9.07× | SLOWDOWN |
| calibration | `cal.large.branch-control.09` | Native C engine | 1.5494× | 1.5266–1.5714× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.09` | Rust engine | 0.1849× | 0.1833–0.1865× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.10` | Python engine | 0.0139× | 0.0137–0.0141× | 12.46× | SLOWDOWN |
| calibration | `cal.large.branch-control.10` | Native C engine | 2.0539× | 2.0184–2.0867× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.10` | Rust engine | 0.2119× | 0.2096–0.2142× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.11` | Python engine | 0.0129× | 0.0123–0.0133× | 19.23× | SLOWDOWN |
| calibration | `cal.large.branch-control.11` | Native C engine | 2.6890× | 2.6227–2.7549× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.11` | Rust engine | 0.2444× | 0.2416–0.2474× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.12` | Python engine | 0.0169× | 0.0168–0.0170× | 7.38× | SLOWDOWN |
| calibration | `cal.large.branch-control.12` | Native C engine | 1.2567× | 1.2448–1.2702× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.12` | Rust engine | 0.1639× | 0.1609–0.1662× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.13` | Python engine | 0.0152× | 0.0149–0.0156× | 9.07× | SLOWDOWN |
| calibration | `cal.large.branch-control.13` | Native C engine | 1.5476× | 1.5137–1.5782× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.13` | Rust engine | 0.1853× | 0.1831–0.1874× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.14` | Python engine | 0.0148× | 0.0138–0.0167× | 12.46× | SLOWDOWN |
| calibration | `cal.large.branch-control.14` | Native C engine | 2.1443× | 1.9955–2.4115× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.14` | Rust engine | 0.2249× | 0.2096–0.2534× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.15` | Python engine | 0.0132× | 0.0129–0.0136× | 19.23× | SLOWDOWN |
| calibration | `cal.large.branch-control.15` | Native C engine | 2.5944× | 2.4514–2.7336× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.15` | Rust engine | 0.2323× | 0.2168–0.2445× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.16` | Python engine | 0.0170× | 0.0168–0.0172× | 7.38× | SLOWDOWN |
| calibration | `cal.large.branch-control.16` | Native C engine | 1.2554× | 1.2450–1.2667× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.16` | Rust engine | 0.1633× | 0.1605–0.1658× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.17` | Python engine | 0.0154× | 0.0152–0.0156× | 9.07× | SLOWDOWN |
| calibration | `cal.large.branch-control.17` | Native C engine | 1.5443× | 1.5272–1.5602× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.17` | Rust engine | 0.1844× | 0.1807–0.1876× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.18` | Python engine | 0.0145× | 0.0137–0.0158× | 12.46× | SLOWDOWN |
| calibration | `cal.large.branch-control.18` | Native C engine | 2.1153× | 1.9957–2.3222× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.18` | Rust engine | 0.2220× | 0.2108–0.2424× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.19` | Python engine | 0.0131× | 0.0128–0.0134× | 19.23× | SLOWDOWN |
| calibration | `cal.large.branch-control.19` | Native C engine | 2.5418× | 2.2570–2.7469× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.19` | Rust engine | 0.2363× | 0.2234–0.2474× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.20` | Python engine | 0.0172× | 0.0167–0.0176× | 7.38× | SLOWDOWN |
| calibration | `cal.large.branch-control.20` | Native C engine | 1.2602× | 1.2155–1.2920× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.20` | Rust engine | 0.1686× | 0.1663–0.1709× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.21` | Python engine | 0.0154× | 0.0152–0.0156× | 9.07× | SLOWDOWN |
| calibration | `cal.large.branch-control.21` | Native C engine | 1.5671× | 1.5328–1.5976× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.21` | Rust engine | 0.1870× | 0.1839–0.1904× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.22` | Python engine | 0.0140× | 0.0137–0.0143× | 12.46× | SLOWDOWN |
| calibration | `cal.large.branch-control.22` | Native C engine | 2.0279× | 1.9696–2.0859× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.22` | Rust engine | 0.2127× | 0.2090–0.2165× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.23` | Python engine | 0.0129× | 0.0126–0.0131× | 19.23× | SLOWDOWN |
| calibration | `cal.large.branch-control.23` | Native C engine | 2.5994× | 2.5610–2.6464× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.23` | Rust engine | 0.2325× | 0.2181–0.2424× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.24` | Python engine | 0.0172× | 0.0170–0.0174× | 7.38× | SLOWDOWN |
| calibration | `cal.large.branch-control.24` | Native C engine | 1.2774× | 1.2574–1.2962× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.24` | Rust engine | 0.1671× | 0.1634–0.1699× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.25` | Python engine | 0.0155× | 0.0153–0.0157× | 9.07× | SLOWDOWN |
| calibration | `cal.large.branch-control.25` | Native C engine | 1.5616× | 1.5421–1.5862× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.25` | Rust engine | 0.1852× | 0.1818–0.1882× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.26` | Python engine | 0.0138× | 0.0137–0.0140× | 12.46× | SLOWDOWN |
| calibration | `cal.large.branch-control.26` | Native C engine | 2.0225× | 1.9868–2.0583× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.26` | Rust engine | 0.2052× | 0.1917–0.2136× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.27` | Python engine | 0.0130× | 0.0129–0.0132× | 19.23× | SLOWDOWN |
| calibration | `cal.large.branch-control.27` | Native C engine | 2.6383× | 2.5478–2.7204× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.27` | Rust engine | 0.2288× | 0.2106–0.2399× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.28` | Python engine | 0.0180× | 0.0170–0.0198× | 7.38× | SLOWDOWN |
| calibration | `cal.large.branch-control.28` | Native C engine | 1.3301× | 1.2520–1.4718× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.28` | Rust engine | 0.1740× | 0.1641–0.1926× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.29` | Python engine | 0.0153× | 0.0151–0.0154× | 9.07× | SLOWDOWN |
| calibration | `cal.large.branch-control.29` | Native C engine | 1.5667× | 1.5505–1.5830× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.29` | Rust engine | 0.1850× | 0.1811–0.1879× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.30` | Python engine | 0.0139× | 0.0138–0.0140× | 12.46× | SLOWDOWN |
| calibration | `cal.large.branch-control.30` | Native C engine | 1.8727× | 1.5865–2.0457× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.30` | Rust engine | 0.2088× | 0.2011–0.2134× | 0.06× | SLOWDOWN |
| calibration | `cal.large.branch-control.31` | Python engine | 0.0132× | 0.0123–0.0143× | 19.23× | SLOWDOWN |
| calibration | `cal.large.branch-control.31` | Native C engine | 2.4188× | 2.1539–2.6233× | 0.93× | FASTER |
| calibration | `cal.large.branch-control.31` | Rust engine | 0.2383× | 0.2181–0.2633× | 0.06× | SLOWDOWN |
| calibration | `cal.large.scanner-text.00` | Python engine | 0.0204× | 0.0193–0.0224× | 7.30× | SLOWDOWN |
| calibration | `cal.large.scanner-text.00` | Native C engine | 1.3160× | 1.2213–1.4135× | 0.34× | FASTER |
| calibration | `cal.large.scanner-text.00` | Rust engine | 0.1191× | 0.1079–0.1328× | 0.16× | SLOWDOWN |
| calibration | `cal.large.scanner-text.01` | Python engine | 0.0177× | 0.0174–0.0180× | 7.53× | SLOWDOWN |
| calibration | `cal.large.scanner-text.01` | Native C engine | 1.4322× | 1.4055–1.4589× | 0.40× | FASTER |
| calibration | `cal.large.scanner-text.01` | Rust engine | 0.1108× | 0.1088–0.1126× | 0.21× | SLOWDOWN |
| calibration | `cal.large.scanner-text.02` | Python engine | 0.0173× | 0.0171–0.0175× | 7.76× | SLOWDOWN |
| calibration | `cal.large.scanner-text.02` | Native C engine | 1.5737× | 1.5485–1.5978× | 0.50× | FASTER |
| calibration | `cal.large.scanner-text.02` | Rust engine | 0.1092× | 0.1069–0.1113× | 0.29× | SLOWDOWN |
| calibration | `cal.large.scanner-text.03` | Python engine | 0.0167× | 0.0163–0.0171× | 8.26× | SLOWDOWN |
| calibration | `cal.large.scanner-text.03` | Native C engine | 1.5866× | 1.5535–1.6217× | 0.60× | FASTER |
| calibration | `cal.large.scanner-text.03` | Rust engine | 0.1027× | 0.1004–0.1049× | 0.38× | SLOWDOWN |
| calibration | `cal.large.scanner-text.04` | Python engine | 0.0190× | 0.0187–0.0194× | 7.30× | SLOWDOWN |
| calibration | `cal.large.scanner-text.04` | Native C engine | 1.2546× | 1.1780–1.3067× | 0.34× | FASTER |
| calibration | `cal.large.scanner-text.04` | Rust engine | 0.1165× | 0.1123–0.1193× | 0.16× | SLOWDOWN |
| calibration | `cal.large.scanner-text.05` | Python engine | 0.0176× | 0.0173–0.0178× | 7.53× | SLOWDOWN |
| calibration | `cal.large.scanner-text.05` | Native C engine | 1.3611× | 1.2675–1.4265× | 0.40× | FASTER |
| calibration | `cal.large.scanner-text.05` | Rust engine | 0.1096× | 0.1079–0.1111× | 0.21× | SLOWDOWN |
| calibration | `cal.large.scanner-text.06` | Python engine | 0.0166× | 0.0163–0.0170× | 7.76× | SLOWDOWN |
| calibration | `cal.large.scanner-text.06` | Native C engine | 1.5270× | 1.4922–1.5679× | 0.50× | FASTER |
| calibration | `cal.large.scanner-text.06` | Rust engine | 0.1047× | 0.1026–0.1070× | 0.29× | SLOWDOWN |
| calibration | `cal.large.scanner-text.07` | Python engine | 0.0165× | 0.0162–0.0169× | 8.26× | SLOWDOWN |
| calibration | `cal.large.scanner-text.07` | Native C engine | 1.5047× | 1.3523–1.6117× | 0.60× | FASTER |
| calibration | `cal.large.scanner-text.07` | Rust engine | 0.1116× | 0.1058–0.1158× | 0.38× | SLOWDOWN |
| calibration | `cal.large.scanner-text.08` | Python engine | 0.0181× | 0.0177–0.0184× | 7.30× | SLOWDOWN |
| calibration | `cal.large.scanner-text.08` | Native C engine | 1.2824× | 1.2544–1.3097× | 0.34× | FASTER |
| calibration | `cal.large.scanner-text.08` | Rust engine | 0.1230× | 0.1203–0.1254× | 0.16× | SLOWDOWN |
| calibration | `cal.large.scanner-text.09` | Python engine | 0.0184× | 0.0175–0.0200× | 7.53× | SLOWDOWN |
| calibration | `cal.large.scanner-text.09` | Native C engine | 1.3864× | 1.2330–1.5611× | 0.40× | FASTER |
| calibration | `cal.large.scanner-text.09` | Rust engine | 0.1139× | 0.1075–0.1250× | 0.21× | SLOWDOWN |
| calibration | `cal.large.scanner-text.10` | Python engine | 0.0168× | 0.0166–0.0171× | 7.76× | SLOWDOWN |
| calibration | `cal.large.scanner-text.10` | Native C engine | 1.5218× | 1.4903–1.5529× | 0.50× | FASTER |
| calibration | `cal.large.scanner-text.10` | Rust engine | 0.1042× | 0.1017–0.1064× | 0.29× | SLOWDOWN |
| calibration | `cal.large.scanner-text.11` | Python engine | 0.0172× | 0.0164–0.0185× | 8.26× | SLOWDOWN |
| calibration | `cal.large.scanner-text.11` | Native C engine | 1.6420× | 1.5715–1.7428× | 0.60× | FASTER |
| calibration | `cal.large.scanner-text.11` | Rust engine | 0.1099× | 0.1046–0.1173× | 0.38× | SLOWDOWN |
| calibration | `cal.large.scanner-text.12` | Python engine | 0.0192× | 0.0189–0.0195× | 7.30× | SLOWDOWN |
| calibration | `cal.large.scanner-text.12` | Native C engine | 1.2889× | 1.2675–1.3073× | 0.34× | FASTER |
| calibration | `cal.large.scanner-text.12` | Rust engine | 0.1162× | 0.1142–0.1181× | 0.16× | SLOWDOWN |
| calibration | `cal.large.scanner-text.13` | Python engine | 0.0175× | 0.0172–0.0178× | 7.53× | SLOWDOWN |
| calibration | `cal.large.scanner-text.13` | Native C engine | 1.4096× | 1.3887–1.4277× | 0.40× | FASTER |
| calibration | `cal.large.scanner-text.13` | Rust engine | 0.1087× | 0.1069–0.1104× | 0.21× | SLOWDOWN |
| calibration | `cal.large.scanner-text.14` | Python engine | 0.0175× | 0.0171–0.0179× | 7.76× | SLOWDOWN |
| calibration | `cal.large.scanner-text.14` | Native C engine | 1.5660× | 1.5286–1.6051× | 0.50× | FASTER |
| calibration | `cal.large.scanner-text.14` | Rust engine | 0.1098× | 0.1073–0.1123× | 0.29× | SLOWDOWN |
| calibration | `cal.large.scanner-text.15` | Python engine | 0.0166× | 0.0163–0.0170× | 8.26× | SLOWDOWN |
| calibration | `cal.large.scanner-text.15` | Native C engine | 1.6008× | 1.5606–1.6428× | 0.60× | FASTER |
| calibration | `cal.large.scanner-text.15` | Rust engine | 0.1062× | 0.1041–0.1082× | 0.38× | SLOWDOWN |
| calibration | `cal.large.scanner-text.16` | Python engine | 0.0194× | 0.0191–0.0197× | 7.30× | SLOWDOWN |
| calibration | `cal.large.scanner-text.16` | Native C engine | 1.3138× | 1.2890–1.3389× | 0.34× | FASTER |
| calibration | `cal.large.scanner-text.16` | Rust engine | 0.1160× | 0.1145–0.1172× | 0.16× | SLOWDOWN |
| calibration | `cal.large.scanner-text.17` | Python engine | 0.0177× | 0.0175–0.0179× | 7.53× | SLOWDOWN |
| calibration | `cal.large.scanner-text.17` | Native C engine | 1.4102× | 1.3922–1.4308× | 0.40× | FASTER |
| calibration | `cal.large.scanner-text.17` | Rust engine | 0.1106× | 0.1087–0.1122× | 0.21× | SLOWDOWN |
| calibration | `cal.large.scanner-text.18` | Python engine | 0.0169× | 0.0161–0.0177× | 7.76× | SLOWDOWN |
| calibration | `cal.large.scanner-text.18` | Native C engine | 1.3795× | 1.1898–1.5605× | 0.50× | FASTER |
| calibration | `cal.large.scanner-text.18` | Rust engine | 0.1009× | 0.0940–0.1079× | 0.29× | SLOWDOWN |
| calibration | `cal.large.scanner-text.19` | Python engine | 0.0167× | 0.0163–0.0170× | 8.26× | SLOWDOWN |
| calibration | `cal.large.scanner-text.19` | Native C engine | 1.6028× | 1.5560–1.6474× | 0.60× | FASTER |
| calibration | `cal.large.scanner-text.19` | Rust engine | 0.1071× | 0.1053–0.1090× | 0.38× | SLOWDOWN |
| calibration | `cal.large.scanner-text.20` | Python engine | 0.0182× | 0.0178–0.0186× | 7.30× | SLOWDOWN |
| calibration | `cal.large.scanner-text.20` | Native C engine | 1.2779× | 1.2491–1.3046× | 0.34× | FASTER |
| calibration | `cal.large.scanner-text.20` | Rust engine | 0.1222× | 0.1192–0.1250× | 0.16× | SLOWDOWN |
| calibration | `cal.large.scanner-text.21` | Python engine | 0.0176× | 0.0174–0.0179× | 7.53× | SLOWDOWN |
| calibration | `cal.large.scanner-text.21` | Native C engine | 1.4026× | 1.3828–1.4234× | 0.40× | FASTER |
| calibration | `cal.large.scanner-text.21` | Rust engine | 0.1098× | 0.1078–0.1116× | 0.21× | SLOWDOWN |
| calibration | `cal.large.scanner-text.22` | Python engine | 0.0173× | 0.0170–0.0175× | 7.76× | SLOWDOWN |
| calibration | `cal.large.scanner-text.22` | Native C engine | 1.5577× | 1.5203–1.5929× | 0.50× | FASTER |
| calibration | `cal.large.scanner-text.22` | Rust engine | 0.1083× | 0.1056–0.1109× | 0.29× | SLOWDOWN |
| calibration | `cal.large.scanner-text.23` | Python engine | 0.0166× | 0.0163–0.0169× | 8.26× | SLOWDOWN |
| calibration | `cal.large.scanner-text.23` | Native C engine | 1.5863× | 1.5573–1.6156× | 0.60× | FASTER |
| calibration | `cal.large.scanner-text.23` | Rust engine | 0.1149× | 0.1129–0.1167× | 0.38× | SLOWDOWN |
| calibration | `cal.large.scanner-text.24` | Python engine | 0.0191× | 0.0188–0.0194× | 7.30× | SLOWDOWN |
| calibration | `cal.large.scanner-text.24` | Native C engine | 1.2877× | 1.2618–1.3192× | 0.34× | FASTER |
| calibration | `cal.large.scanner-text.24` | Rust engine | 0.1131× | 0.1082–0.1170× | 0.16× | SLOWDOWN |
| calibration | `cal.large.scanner-text.25` | Python engine | 0.0180× | 0.0176–0.0185× | 7.53× | SLOWDOWN |
| calibration | `cal.large.scanner-text.25` | Native C engine | 1.4535× | 1.4211–1.4873× | 0.40× | FASTER |
| calibration | `cal.large.scanner-text.25` | Rust engine | 0.1084× | 0.0983–0.1150× | 0.21× | SLOWDOWN |
| calibration | `cal.large.scanner-text.26` | Python engine | 0.0164× | 0.0161–0.0167× | 7.76× | SLOWDOWN |
| calibration | `cal.large.scanner-text.26` | Native C engine | 1.4961× | 1.4707–1.5226× | 0.50× | FASTER |
| calibration | `cal.large.scanner-text.26` | Rust engine | 0.1043× | 0.1026–0.1057× | 0.29× | SLOWDOWN |
| calibration | `cal.large.scanner-text.27` | Python engine | 0.0167× | 0.0164–0.0170× | 8.26× | SLOWDOWN |
| calibration | `cal.large.scanner-text.27` | Native C engine | 1.5813× | 1.5451–1.6157× | 0.60× | FASTER |
| calibration | `cal.large.scanner-text.27` | Rust engine | 0.1059× | 0.1035–0.1080× | 0.38× | SLOWDOWN |
| calibration | `cal.large.scanner-text.28` | Python engine | 0.0190× | 0.0187–0.0193× | 7.30× | SLOWDOWN |
| calibration | `cal.large.scanner-text.28` | Native C engine | 1.2792× | 1.2154–1.3232× | 0.34× | FASTER |
| calibration | `cal.large.scanner-text.28` | Rust engine | 0.1150× | 0.1127–0.1172× | 0.16× | SLOWDOWN |
| calibration | `cal.large.scanner-text.29` | Python engine | 0.0178× | 0.0176–0.0180× | 7.53× | SLOWDOWN |
| calibration | `cal.large.scanner-text.29` | Native C engine | 1.4322× | 1.4117–1.4519× | 0.40× | FASTER |
| calibration | `cal.large.scanner-text.29` | Rust engine | 0.1159× | 0.1141–0.1173× | 0.21× | SLOWDOWN |
| calibration | `cal.large.scanner-text.30` | Python engine | 0.0175× | 0.0171–0.0179× | 7.76× | SLOWDOWN |
| calibration | `cal.large.scanner-text.30` | Native C engine | 1.5978× | 1.5507–1.6427× | 0.50× | FASTER |
| calibration | `cal.large.scanner-text.30` | Rust engine | 0.1092× | 0.1067–0.1118× | 0.29× | SLOWDOWN |
| calibration | `cal.large.scanner-text.31` | Python engine | 0.0184× | 0.0175–0.0197× | 8.26× | SLOWDOWN |
| calibration | `cal.large.scanner-text.31` | Native C engine | 1.7331× | 1.6419–1.8713× | 0.60× | FASTER |
| calibration | `cal.large.scanner-text.31` | Rust engine | 0.1177× | 0.1123–0.1256× | 0.38× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.00` | Python engine | 0.0188× | 0.0187–0.0189× | 7.37× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.00` | Native C engine | 1.3421× | 1.3332–1.3513× | 0.34× | FASTER |
| calibration | `cal.large.scanner-bytes.00` | Rust engine | 0.0982× | 0.0974–0.0988× | 0.34× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.01` | Python engine | 0.0179× | 0.0177–0.0182× | 7.68× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.01` | Native C engine | 1.4406× | 1.3882–1.4780× | 0.40× | FASTER |
| calibration | `cal.large.scanner-bytes.01` | Rust engine | 0.1025× | 0.1006–0.1043× | 0.30× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.02` | Python engine | 0.0170× | 0.0161–0.0183× | 8.12× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.02` | Native C engine | 1.5874× | 1.4785–1.7383× | 0.50× | FASTER |
| calibration | `cal.large.scanner-bytes.02` | Rust engine | 0.0983× | 0.0937–0.1064× | 0.41× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.03` | Python engine | 0.0164× | 0.0161–0.0166× | 8.87× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.03` | Native C engine | 1.5652× | 1.5184–1.6183× | 0.60× | FASTER |
| calibration | `cal.large.scanner-bytes.03` | Rust engine | 0.0977× | 0.0960–0.0994× | 0.42× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.04` | Python engine | 0.0185× | 0.0182–0.0188× | 7.37× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.04` | Native C engine | 1.3277× | 1.3072–1.3484× | 0.34× | FASTER |
| calibration | `cal.large.scanner-bytes.04` | Rust engine | 0.0988× | 0.0973–0.1008× | 0.34× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.05` | Python engine | 0.0173× | 0.0169–0.0177× | 7.69× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.05` | Native C engine | 1.3945× | 1.3664–1.4257× | 0.40× | FASTER |
| calibration | `cal.large.scanner-bytes.05` | Rust engine | 0.1000× | 0.0985–0.1014× | 0.30× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.06` | Python engine | 0.0165× | 0.0163–0.0168× | 8.12× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.06` | Native C engine | 1.5953× | 1.5619–1.6301× | 0.50× | FASTER |
| calibration | `cal.large.scanner-bytes.06` | Rust engine | 0.0956× | 0.0945–0.0968× | 0.41× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.07` | Python engine | 0.0164× | 0.0161–0.0167× | 8.74× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.07` | Native C engine | 1.5251× | 1.4831–1.5645× | 0.60× | FASTER |
| calibration | `cal.large.scanner-bytes.07` | Rust engine | 0.1047× | 0.1029–0.1063× | 0.42× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.08` | Python engine | 0.0184× | 0.0181–0.0186× | 7.37× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.08` | Native C engine | 1.3419× | 1.3149–1.3687× | 0.34× | FASTER |
| calibration | `cal.large.scanner-bytes.08` | Rust engine | 0.0992× | 0.0976–0.1007× | 0.34× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.09` | Python engine | 0.0175× | 0.0169–0.0185× | 7.70× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.09` | Native C engine | 1.4165× | 1.3579–1.5045× | 0.40× | FASTER |
| calibration | `cal.large.scanner-bytes.09` | Rust engine | 0.0990× | 0.0947–0.1049× | 0.30× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.10` | Python engine | 0.0163× | 0.0159–0.0166× | 8.15× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.10` | Native C engine | 1.4418× | 1.2894–1.5549× | 0.50× | FASTER |
| calibration | `cal.large.scanner-bytes.10` | Rust engine | 0.0939× | 0.0917–0.0958× | 0.41× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.11` | Python engine | 0.0165× | 0.0162–0.0168× | 8.87× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.11` | Native C engine | 1.5312× | 1.4979–1.5671× | 0.60× | FASTER |
| calibration | `cal.large.scanner-bytes.11` | Rust engine | 0.0993× | 0.0980–0.1008× | 0.42× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.12` | Python engine | 0.0184× | 0.0181–0.0186× | 7.37× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.12` | Native C engine | 1.3041× | 1.2633–1.3426× | 0.34× | FASTER |
| calibration | `cal.large.scanner-bytes.12` | Rust engine | 0.0996× | 0.0985–0.1007× | 0.34× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.13` | Python engine | 0.0175× | 0.0173–0.0177× | 7.70× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.13` | Native C engine | 1.4069× | 1.3855–1.4311× | 0.40× | FASTER |
| calibration | `cal.large.scanner-bytes.13` | Rust engine | 0.0987× | 0.0973–0.1004× | 0.30× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.14` | Python engine | 0.0165× | 0.0162–0.0167× | 8.15× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.14` | Native C engine | 1.5734× | 1.5423–1.6055× | 0.50× | FASTER |
| calibration | `cal.large.scanner-bytes.14` | Rust engine | 0.0944× | 0.0926–0.0960× | 0.41× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.15` | Python engine | 0.0163× | 0.0160–0.0166× | 8.87× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.15` | Native C engine | 1.5708× | 1.5209–1.6250× | 0.60× | FASTER |
| calibration | `cal.large.scanner-bytes.15` | Rust engine | 0.0987× | 0.0970–0.1001× | 0.42× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.16` | Python engine | 0.0188× | 0.0184–0.0194× | 7.37× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.16` | Native C engine | 1.3086× | 1.2710–1.3516× | 0.34× | FASTER |
| calibration | `cal.large.scanner-bytes.16` | Rust engine | 0.1012× | 0.0991–0.1040× | 0.34× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.17` | Python engine | 0.0173× | 0.0171–0.0174× | 7.69× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.17` | Native C engine | 1.3948× | 1.3717–1.4199× | 0.40× | FASTER |
| calibration | `cal.large.scanner-bytes.17` | Rust engine | 0.0990× | 0.0977–0.1002× | 0.30× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.18` | Python engine | 0.0166× | 0.0163–0.0168× | 8.12× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.18` | Native C engine | 1.5385× | 1.5152–1.5653× | 0.50× | FASTER |
| calibration | `cal.large.scanner-bytes.18` | Rust engine | 0.0959× | 0.0941–0.0977× | 0.41× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.19` | Python engine | 0.0165× | 0.0161–0.0168× | 8.87× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.19` | Native C engine | 1.5503× | 1.4866–1.6156× | 0.60× | FASTER |
| calibration | `cal.large.scanner-bytes.19` | Rust engine | 0.0979× | 0.0954–0.1004× | 0.42× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.20` | Python engine | 0.0187× | 0.0185–0.0188× | 7.37× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.20` | Native C engine | 1.3451× | 1.3328–1.3570× | 0.34× | FASTER |
| calibration | `cal.large.scanner-bytes.20` | Rust engine | 0.1010× | 0.1000–0.1018× | 0.34× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.21` | Python engine | 0.0176× | 0.0172–0.0180× | 7.69× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.21` | Native C engine | 1.4594× | 1.4225–1.5059× | 0.40× | FASTER |
| calibration | `cal.large.scanner-bytes.21` | Rust engine | 0.0999× | 0.0977–0.1028× | 0.30× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.22` | Python engine | 0.0159× | 0.0157–0.0161× | 8.07× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.22` | Native C engine | 1.5465× | 1.5289–1.5632× | 0.50× | FASTER |
| calibration | `cal.large.scanner-bytes.22` | Rust engine | 0.0989× | 0.0978–0.0999× | 0.41× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.23` | Python engine | 0.0164× | 0.0161–0.0167× | 8.87× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.23` | Native C engine | 1.5553× | 1.5296–1.5831× | 0.60× | FASTER |
| calibration | `cal.large.scanner-bytes.23` | Rust engine | 0.0983× | 0.0968–0.0998× | 0.42× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.24` | Python engine | 0.0185× | 0.0182–0.0187× | 7.37× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.24` | Native C engine | 1.3422× | 1.3062–1.3820× | 0.34× | FASTER |
| calibration | `cal.large.scanner-bytes.24` | Rust engine | 0.0994× | 0.0976–0.1009× | 0.34× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.25` | Python engine | 0.0171× | 0.0168–0.0174× | 7.68× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.25` | Native C engine | 1.4183× | 1.3516–1.4745× | 0.40× | FASTER |
| calibration | `cal.large.scanner-bytes.25` | Rust engine | 0.1071× | 0.1053–0.1092× | 0.30× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.26` | Python engine | 0.0162× | 0.0159–0.0165× | 8.15× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.26` | Native C engine | 1.5344× | 1.5091–1.5593× | 0.50× | FASTER |
| calibration | `cal.large.scanner-bytes.26` | Rust engine | 0.0939× | 0.0923–0.0955× | 0.41× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.27` | Python engine | 0.0165× | 0.0162–0.0168× | 9.00× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.27` | Native C engine | 1.5520× | 1.5151–1.5893× | 0.60× | FASTER |
| calibration | `cal.large.scanner-bytes.27` | Rust engine | 0.0939× | 0.0905–0.0970× | 0.42× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.28` | Python engine | 0.0182× | 0.0177–0.0186× | 7.37× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.28` | Native C engine | 1.3192× | 1.2376–1.3755× | 0.34× | FASTER |
| calibration | `cal.large.scanner-bytes.28` | Rust engine | 0.0997× | 0.0974–0.1018× | 0.34× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.29` | Python engine | 0.0178× | 0.0175–0.0180× | 7.71× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.29` | Native C engine | 1.4344× | 1.4039–1.4698× | 0.40× | FASTER |
| calibration | `cal.large.scanner-bytes.29` | Rust engine | 0.1005× | 0.0989–0.1021× | 0.30× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.30` | Python engine | 0.0168× | 0.0162–0.0177× | 8.17× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.30` | Native C engine | 1.5804× | 1.5094–1.6811× | 0.50× | FASTER |
| calibration | `cal.large.scanner-bytes.30` | Rust engine | 0.0949× | 0.0914–0.1007× | 0.41× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.31` | Python engine | 0.0174× | 0.0157–0.0192× | 8.94× | SLOWDOWN |
| calibration | `cal.large.scanner-bytes.31` | Native C engine | 1.7111× | 1.5909–1.8874× | 0.60× | FASTER |
| calibration | `cal.large.scanner-bytes.31` | Rust engine | 0.1049× | 0.0965–0.1171× | 0.42× | SLOWDOWN |
| calibration | `cal.large.window-search.00` | Python engine | 0.0259× | 0.0233–0.0291× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.00` | Native C engine | 0.7801× | 0.6947–0.8874× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.00` | Rust engine | 0.2064× | 0.1865–0.2323× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.01` | Python engine | 0.0264× | 0.0261–0.0269× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.01` | Native C engine | 0.7222× | 0.7048–0.7371× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.01` | Rust engine | 0.2073× | 0.2045–0.2115× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.02` | Python engine | 0.0269× | 0.0260–0.0283× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.02` | Native C engine | 0.7450× | 0.7237–0.7832× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.02` | Rust engine | 0.2057× | 0.1938–0.2198× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.03` | Python engine | 0.0275× | 0.0266–0.0284× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.03` | Native C engine | 0.7286× | 0.7081–0.7514× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.03` | Rust engine | 0.2115× | 0.2074–0.2169× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.04` | Python engine | 0.0250× | 0.0247–0.0253× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.04` | Native C engine | 0.7180× | 0.7063–0.7268× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.04` | Rust engine | 0.1965× | 0.1949–0.1981× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.05` | Python engine | 0.0250× | 0.0241–0.0256× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.05` | Native C engine | 0.7136× | 0.6833–0.7357× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.05` | Rust engine | 0.1967× | 0.1919–0.2006× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.06` | Python engine | 0.0257× | 0.0254–0.0259× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.06` | Native C engine | 0.7220× | 0.7131–0.7326× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.06` | Rust engine | 0.1978× | 0.1912–0.2020× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.07` | Python engine | 0.0274× | 0.0272–0.0276× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.07` | Native C engine | 0.7291× | 0.7197–0.7377× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.07` | Rust engine | 0.2266× | 0.2240–0.2287× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.08` | Python engine | 0.0242× | 0.0229–0.0250× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.08` | Native C engine | 0.6832× | 0.6350–0.7161× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.08` | Rust engine | 0.2093× | 0.2053–0.2119× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.09` | Python engine | 0.0253× | 0.0249–0.0256× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.09` | Native C engine | 0.7223× | 0.7148–0.7297× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.09` | Rust engine | 0.1985× | 0.1964–0.2009× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.10` | Python engine | 0.0256× | 0.0251–0.0262× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.10` | Native C engine | 0.7333× | 0.7255–0.7415× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.10` | Rust engine | 0.1985× | 0.1962–0.2009× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.11` | Python engine | 0.0278× | 0.0266–0.0292× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.11` | Native C engine | 0.7466× | 0.7252–0.7730× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.11` | Rust engine | 0.2142× | 0.2083–0.2225× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.12` | Python engine | 0.0255× | 0.0242–0.0273× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.12` | Native C engine | 0.7238× | 0.6871–0.7717× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.12` | Rust engine | 0.2104× | 0.2017–0.2237× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.13` | Python engine | 0.0249× | 0.0245–0.0252× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.13` | Native C engine | 0.7060× | 0.6896–0.7184× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.13` | Rust engine | 0.1943× | 0.1892–0.1986× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.14` | Python engine | 0.0256× | 0.0248–0.0262× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.14` | Native C engine | 0.7160× | 0.7044–0.7260× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.14` | Rust engine | 0.1981× | 0.1909–0.2029× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.15` | Python engine | 0.0277× | 0.0271–0.0281× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.15` | Native C engine | 0.7370× | 0.7262–0.7496× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.15` | Rust engine | 0.2047× | 0.1911–0.2132× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.16` | Python engine | 0.0257× | 0.0247–0.0274× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.16` | Native C engine | 0.7257× | 0.6900–0.7774× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.16` | Rust engine | 0.2139× | 0.2067–0.2250× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.17` | Python engine | 0.0252× | 0.0248–0.0256× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.17` | Native C engine | 0.7245× | 0.7194–0.7300× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.17` | Rust engine | 0.1988× | 0.1969–0.2006× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.18` | Python engine | 0.0275× | 0.0263–0.0296× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.18` | Native C engine | 0.7604× | 0.7226–0.8343× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.18` | Rust engine | 0.2168× | 0.1942–0.2468× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.19` | Python engine | 0.0277× | 0.0273–0.0281× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.19` | Native C engine | 0.7293× | 0.7206–0.7386× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.19` | Rust engine | 0.2052× | 0.1958–0.2113× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.20` | Python engine | 0.0248× | 0.0244–0.0251× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.20` | Native C engine | 0.7069× | 0.6878–0.7202× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.20` | Rust engine | 0.1938× | 0.1908–0.1962× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.21` | Python engine | 0.0256× | 0.0253–0.0258× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.21` | Native C engine | 0.7252× | 0.7171–0.7346× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.21` | Rust engine | 0.1961× | 0.1892–0.2008× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.22` | Python engine | 0.0263× | 0.0259–0.0265× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.22` | Native C engine | 0.7261× | 0.7181–0.7343× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.22` | Rust engine | 0.1987× | 0.1931–0.2023× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.23` | Python engine | 0.0286× | 0.0273–0.0306× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.23` | Native C engine | 0.7166× | 0.6350–0.8185× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.23` | Rust engine | 0.2189× | 0.1980–0.2346× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.24` | Python engine | 0.0254× | 0.0245–0.0269× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.24` | Native C engine | 0.7346× | 0.7090–0.7776× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.24` | Rust engine | 0.1904× | 0.1838–0.2002× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.25` | Python engine | 0.0256× | 0.0254–0.0257× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.25` | Native C engine | 0.7253× | 0.7192–0.7322× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.25` | Rust engine | 0.1928× | 0.1913–0.1942× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.26` | Python engine | 0.0258× | 0.0255–0.0260× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.26` | Native C engine | 0.7199× | 0.7038–0.7341× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.26` | Rust engine | 0.1969× | 0.1951–0.1987× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.27` | Python engine | 0.0286× | 0.0268–0.0316× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.27` | Native C engine | 0.7586× | 0.7022–0.8415× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.27` | Rust engine | 0.2348× | 0.2185–0.2618× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.28` | Python engine | 0.0242× | 0.0237–0.0247× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.28` | Native C engine | 0.7271× | 0.7188–0.7366× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.28` | Rust engine | 0.1896× | 0.1852–0.1930× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.29` | Python engine | 0.0243× | 0.0238–0.0247× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.29` | Native C engine | 0.7253× | 0.7176–0.7332× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.29` | Rust engine | 0.1952× | 0.1936–0.1969× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.30` | Python engine | 0.0251× | 0.0247–0.0256× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.30` | Native C engine | 0.7266× | 0.7140–0.7439× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.30` | Rust engine | 0.2009× | 0.1980–0.2043× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-search.31` | Python engine | 0.0262× | 0.0251–0.0269× | 4.43× | SLOWDOWN |
| calibration | `cal.large.window-search.31` | Native C engine | 0.7345× | 0.7201–0.7476× | 0.18× | SLOWDOWN |
| calibration | `cal.large.window-search.31` | Rust engine | 0.1992× | 0.1857–0.2101× | 0.17× | SLOWDOWN |
| calibration | `cal.large.window-collection.00` | Python engine | 0.0324× | 0.0316–0.0335× | 3.44× | SLOWDOWN |
| calibration | `cal.large.window-collection.00` | Native C engine | 1.5500× | 1.5064–1.5991× | 0.36× | FASTER |
| calibration | `cal.large.window-collection.00` | Rust engine | 0.2023× | 0.1954–0.2101× | 0.37× | SLOWDOWN |
| calibration | `cal.large.window-collection.01` | Python engine | 0.0208× | 0.0206–0.0209× | 5.54× | SLOWDOWN |
| calibration | `cal.large.window-collection.01` | Native C engine | 1.8696× | 1.8501–1.8887× | 0.34× | FASTER |
| calibration | `cal.large.window-collection.01` | Rust engine | 0.3061× | 0.2995–0.3107× | 1.30× | SLOWDOWN |
| calibration | `cal.large.window-collection.02` | Python engine | 0.0289× | 0.0286–0.0291× | 3.73× | SLOWDOWN |
| calibration | `cal.large.window-collection.02` | Native C engine | 1.6735× | 1.6384–1.7017× | 0.52× | FASTER |
| calibration | `cal.large.window-collection.02` | Rust engine | 0.1714× | 0.1697–0.1734× | 0.50× | SLOWDOWN |
| calibration | `cal.large.window-collection.03` | Python engine | 0.0217× | 0.0215–0.0220× | 7.10× | SLOWDOWN |
| calibration | `cal.large.window-collection.03` | Native C engine | 2.3421× | 2.3042–2.3892× | 0.63× | FASTER |
| calibration | `cal.large.window-collection.03` | Rust engine | 0.3306× | 0.3052–0.3465× | 3.00× | SLOWDOWN |
| calibration | `cal.large.window-collection.04` | Python engine | 0.0352× | 0.0344–0.0366× | 3.44× | SLOWDOWN |
| calibration | `cal.large.window-collection.04` | Native C engine | 1.5893× | 1.5426–1.6586× | 0.36× | FASTER |
| calibration | `cal.large.window-collection.04` | Rust engine | 0.2003× | 0.1836–0.2151× | 0.37× | SLOWDOWN |
| calibration | `cal.large.window-collection.05` | Python engine | 0.0216× | 0.0213–0.0218× | 5.52× | SLOWDOWN |
| calibration | `cal.large.window-collection.05` | Native C engine | 1.9246× | 1.8954–1.9524× | 0.35× | FASTER |
| calibration | `cal.large.window-collection.05` | Rust engine | 0.2774× | 0.2713–0.2814× | 1.53× | SLOWDOWN |
| calibration | `cal.large.window-collection.06` | Python engine | 0.0291× | 0.0287–0.0294× | 3.73× | SLOWDOWN |
| calibration | `cal.large.window-collection.06` | Native C engine | 1.7127× | 1.6941–1.7320× | 0.52× | FASTER |
| calibration | `cal.large.window-collection.06` | Rust engine | 0.1720× | 0.1689–0.1746× | 0.50× | SLOWDOWN |
| calibration | `cal.large.window-collection.07` | Python engine | 0.0222× | 0.0217–0.0232× | 7.10× | SLOWDOWN |
| calibration | `cal.large.window-collection.07` | Native C engine | 2.3621× | 2.2956–2.4609× | 0.63× | FASTER |
| calibration | `cal.large.window-collection.07` | Rust engine | 0.3501× | 0.3393–0.3662× | 3.00× | SLOWDOWN |
| calibration | `cal.large.window-collection.08` | Python engine | 0.0352× | 0.0341–0.0366× | 3.44× | SLOWDOWN |
| calibration | `cal.large.window-collection.08` | Native C engine | 1.5528× | 1.4652–1.6312× | 0.36× | FASTER |
| calibration | `cal.large.window-collection.08` | Rust engine | 0.2048× | 0.1984–0.2127× | 0.37× | SLOWDOWN |
| calibration | `cal.large.window-collection.09` | Python engine | 0.0223× | 0.0213–0.0236× | 5.52× | SLOWDOWN |
| calibration | `cal.large.window-collection.09` | Native C engine | 1.9197× | 1.6831–2.1158× | 0.35× | FASTER |
| calibration | `cal.large.window-collection.09` | Rust engine | 0.2824× | 0.2705–0.2991× | 1.53× | SLOWDOWN |
| calibration | `cal.large.window-collection.10` | Python engine | 0.0294× | 0.0285–0.0305× | 3.73× | SLOWDOWN |
| calibration | `cal.large.window-collection.10` | Native C engine | 1.7295× | 1.6917–1.7817× | 0.52× | FASTER |
| calibration | `cal.large.window-collection.10` | Rust engine | 0.1768× | 0.1726–0.1823× | 0.50× | SLOWDOWN |
| calibration | `cal.large.window-collection.11` | Python engine | 0.0216× | 0.0214–0.0219× | 7.16× | SLOWDOWN |
| calibration | `cal.large.window-collection.11` | Native C engine | 2.3241× | 2.2813–2.3642× | 0.62× | FASTER |
| calibration | `cal.large.window-collection.11` | Rust engine | 0.3710× | 0.3655–0.3760× | 2.49× | SLOWDOWN |
| calibration | `cal.large.window-collection.12` | Python engine | 0.0344× | 0.0339–0.0351× | 3.44× | SLOWDOWN |
| calibration | `cal.large.window-collection.12` | Native C engine | 1.5131× | 1.4544–1.5590× | 0.36× | FASTER |
| calibration | `cal.large.window-collection.12` | Rust engine | 0.1962× | 0.1927–0.2007× | 0.37× | SLOWDOWN |
| calibration | `cal.large.window-collection.13` | Python engine | 0.0216× | 0.0213–0.0218× | 5.53× | SLOWDOWN |
| calibration | `cal.large.window-collection.13` | Native C engine | 1.9005× | 1.8676–1.9315× | 0.34× | FASTER |
| calibration | `cal.large.window-collection.13` | Rust engine | 0.2987× | 0.2918–0.3050× | 1.41× | SLOWDOWN |
| calibration | `cal.large.window-collection.14` | Python engine | 0.0297× | 0.0288–0.0308× | 3.73× | SLOWDOWN |
| calibration | `cal.large.window-collection.14` | Native C engine | 1.7477× | 1.7067–1.8032× | 0.52× | FASTER |
| calibration | `cal.large.window-collection.14` | Rust engine | 0.1778× | 0.1728–0.1837× | 0.50× | SLOWDOWN |
| calibration | `cal.large.window-collection.15` | Python engine | 0.0233× | 0.0212–0.0266× | 7.06× | SLOWDOWN |
| calibration | `cal.large.window-collection.15` | Native C engine | 2.4018× | 2.3310–2.4964× | 0.63× | FASTER |
| calibration | `cal.large.window-collection.15` | Rust engine | 0.3478× | 0.3148–0.3998× | 3.25× | SLOWDOWN |
| calibration | `cal.large.window-collection.16` | Python engine | 0.0350× | 0.0329–0.0375× | 3.44× | SLOWDOWN |
| calibration | `cal.large.window-collection.16` | Native C engine | 1.5942× | 1.4557–1.7388× | 0.36× | FASTER |
| calibration | `cal.large.window-collection.16` | Rust engine | 0.2084× | 0.1926–0.2260× | 0.37× | SLOWDOWN |
| calibration | `cal.large.window-collection.17` | Python engine | 0.0203× | 0.0200–0.0206× | 5.55× | SLOWDOWN |
| calibration | `cal.large.window-collection.17` | Native C engine | 1.8754× | 1.7412–1.9607× | 0.34× | FASTER |
| calibration | `cal.large.window-collection.17` | Rust engine | 0.3076× | 0.2961–0.3183× | 1.18× | SLOWDOWN |
| calibration | `cal.large.window-collection.18` | Python engine | 0.0322× | 0.0290–0.0367× | 3.73× | SLOWDOWN |
| calibration | `cal.large.window-collection.18` | Native C engine | 1.8074× | 1.6347–2.0598× | 0.52× | FASTER |
| calibration | `cal.large.window-collection.18` | Rust engine | 0.1764× | 0.1553–0.2028× | 0.50× | SLOWDOWN |
| calibration | `cal.large.window-collection.19` | Python engine | 0.0225× | 0.0201–0.0253× | 7.10× | SLOWDOWN |
| calibration | `cal.large.window-collection.19` | Native C engine | 2.2870× | 1.9715–2.6739× | 0.63× | FASTER |
| calibration | `cal.large.window-collection.19` | Rust engine | 0.3697× | 0.3386–0.4126× | 3.00× | SLOWDOWN |
| calibration | `cal.large.window-collection.20` | Python engine | 0.0347× | 0.0315–0.0375× | 3.44× | SLOWDOWN |
| calibration | `cal.large.window-collection.20` | Native C engine | 1.4665× | 1.2899–1.6154× | 0.36× | FASTER |
| calibration | `cal.large.window-collection.20` | Rust engine | 0.1909× | 0.1769–0.2024× | 0.37× | SLOWDOWN |
| calibration | `cal.large.window-collection.21` | Python engine | 0.0217× | 0.0215–0.0219× | 5.53× | SLOWDOWN |
| calibration | `cal.large.window-collection.21` | Native C engine | 1.9110× | 1.8756–1.9391× | 0.34× | FASTER |
| calibration | `cal.large.window-collection.21` | Rust engine | 0.3021× | 0.2938–0.3076× | 1.41× | SLOWDOWN |
| calibration | `cal.large.window-collection.22` | Python engine | 0.0285× | 0.0275–0.0292× | 3.73× | SLOWDOWN |
| calibration | `cal.large.window-collection.22` | Native C engine | 1.7195× | 1.6992–1.7399× | 0.52× | FASTER |
| calibration | `cal.large.window-collection.22` | Rust engine | 0.1683× | 0.1652–0.1711× | 0.50× | SLOWDOWN |
| calibration | `cal.large.window-collection.23` | Python engine | 0.0212× | 0.0210–0.0214× | 7.16× | SLOWDOWN |
| calibration | `cal.large.window-collection.23` | Native C engine | 2.3285× | 2.2989–2.3573× | 0.62× | FASTER |
| calibration | `cal.large.window-collection.23` | Rust engine | 0.3666× | 0.3637–0.3690× | 2.49× | SLOWDOWN |
| calibration | `cal.large.window-collection.24` | Python engine | 0.0362× | 0.0348–0.0380× | 3.44× | SLOWDOWN |
| calibration | `cal.large.window-collection.24` | Native C engine | 1.6372× | 1.5789–1.7129× | 0.36× | FASTER |
| calibration | `cal.large.window-collection.24` | Rust engine | 0.2120× | 0.2030–0.2224× | 0.37× | SLOWDOWN |
| calibration | `cal.large.window-collection.25` | Python engine | 0.0219× | 0.0217–0.0220× | 5.52× | SLOWDOWN |
| calibration | `cal.large.window-collection.25` | Native C engine | 1.9600× | 1.9424–1.9770× | 0.35× | FASTER |
| calibration | `cal.large.window-collection.25` | Rust engine | 0.2787× | 0.2736–0.2833× | 1.53× | SLOWDOWN |
| calibration | `cal.large.window-collection.26` | Python engine | 0.0302× | 0.0286–0.0324× | 3.73× | SLOWDOWN |
| calibration | `cal.large.window-collection.26` | Native C engine | 1.6964× | 1.5075–1.8791× | 0.52× | FASTER |
| calibration | `cal.large.window-collection.26` | Rust engine | 0.1822× | 0.1725–0.1951× | 0.50× | SLOWDOWN |
| calibration | `cal.large.window-collection.27` | Python engine | 0.0217× | 0.0211–0.0227× | 7.06× | SLOWDOWN |
| calibration | `cal.large.window-collection.27` | Native C engine | 2.4141× | 2.3297–2.5501× | 0.63× | FASTER |
| calibration | `cal.large.window-collection.27` | Rust engine | 0.3275× | 0.3128–0.3465× | 3.25× | SLOWDOWN |
| calibration | `cal.large.window-collection.28` | Python engine | 0.0357× | 0.0339–0.0380× | 3.44× | SLOWDOWN |
| calibration | `cal.large.window-collection.28` | Native C engine | 1.5994× | 1.4890–1.7167× | 0.36× | FASTER |
| calibration | `cal.large.window-collection.28` | Rust engine | 0.2037× | 0.1936–0.2167× | 0.37× | SLOWDOWN |
| calibration | `cal.large.window-collection.29` | Python engine | 0.0213× | 0.0210–0.0215× | 5.52× | SLOWDOWN |
| calibration | `cal.large.window-collection.29` | Native C engine | 1.8827× | 1.8487–1.9187× | 0.35× | FASTER |
| calibration | `cal.large.window-collection.29` | Rust engine | 0.2958× | 0.2929–0.2984× | 1.53× | SLOWDOWN |
| calibration | `cal.large.window-collection.30` | Python engine | 0.0292× | 0.0288–0.0296× | 3.73× | SLOWDOWN |
| calibration | `cal.large.window-collection.30` | Native C engine | 1.6706× | 1.5218–1.7674× | 0.52× | FASTER |
| calibration | `cal.large.window-collection.30` | Rust engine | 0.1739× | 0.1714–0.1766× | 0.50× | SLOWDOWN |
| calibration | `cal.large.window-collection.31` | Python engine | 0.0219× | 0.0210–0.0235× | 7.03× | SLOWDOWN |
| calibration | `cal.large.window-collection.31` | Native C engine | 2.3875× | 2.2750–2.5787× | 0.63× | FASTER |
| calibration | `cal.large.window-collection.31` | Rust engine | 0.3148× | 0.2980–0.3418× | 3.49× | SLOWDOWN |
| calibration | `cal.large.request-records.00` | Python engine | 0.0218× | 0.0210–0.0228× | 7.39× | SLOWDOWN |
| calibration | `cal.large.request-records.00` | Native C engine | 1.1598× | 1.1205–1.2108× | 0.35× | FASTER |
| calibration | `cal.large.request-records.00` | Rust engine | 0.1647× | 0.1569–0.1729× | 0.32× | SLOWDOWN |
| calibration | `cal.large.request-records.01` | Python engine | 0.0181× | 0.0167–0.0191× | 7.49× | SLOWDOWN |
| calibration | `cal.large.request-records.01` | Native C engine | 1.0983× | 1.0755–1.1222× | 0.41× | FASTER |
| calibration | `cal.large.request-records.01` | Rust engine | 0.1467× | 0.1442–0.1494× | 0.34× | SLOWDOWN |
| calibration | `cal.large.request-records.02` | Python engine | 0.0163× | 0.0160–0.0168× | 7.62× | SLOWDOWN |
| calibration | `cal.large.request-records.02` | Native C engine | 1.0301× | 1.0074–1.0599× | 0.49× | FASTER |
| calibration | `cal.large.request-records.02` | Rust engine | 0.1313× | 0.1281–0.1352× | 0.38× | SLOWDOWN |
| calibration | `cal.large.request-records.03` | Python engine | 0.0158× | 0.0154–0.0161× | 7.66× | SLOWDOWN |
| calibration | `cal.large.request-records.03` | Native C engine | 0.9914× | 0.9473–1.0294× | 0.59× | — |
| calibration | `cal.large.request-records.03` | Rust engine | 0.1266× | 0.1234–0.1297× | 0.44× | SLOWDOWN |
| calibration | `cal.large.request-records.04` | Python engine | 0.0217× | 0.0211–0.0226× | 7.39× | SLOWDOWN |
| calibration | `cal.large.request-records.04` | Native C engine | 1.1440× | 1.1114–1.1887× | 0.35× | FASTER |
| calibration | `cal.large.request-records.04` | Rust engine | 0.1613× | 0.1563–0.1675× | 0.32× | SLOWDOWN |
| calibration | `cal.large.request-records.05` | Python engine | 0.0182× | 0.0180–0.0185× | 7.49× | SLOWDOWN |
| calibration | `cal.large.request-records.05` | Native C engine | 1.0679× | 1.0508–1.0848× | 0.41× | FASTER |
| calibration | `cal.large.request-records.05` | Rust engine | 0.1391× | 0.1348–0.1435× | 0.34× | SLOWDOWN |
| calibration | `cal.large.request-records.06` | Python engine | 0.0162× | 0.0158–0.0166× | 7.62× | SLOWDOWN |
| calibration | `cal.large.request-records.06` | Native C engine | 0.9809× | 0.8923–1.0404× | 0.49× | — |
| calibration | `cal.large.request-records.06` | Rust engine | 0.1290× | 0.1264–0.1320× | 0.38× | SLOWDOWN |
| calibration | `cal.large.request-records.07` | Python engine | 0.0160× | 0.0158–0.0162× | 7.66× | SLOWDOWN |
| calibration | `cal.large.request-records.07` | Native C engine | 1.0230× | 1.0013–1.0447× | 0.59× | FASTER |
| calibration | `cal.large.request-records.07` | Rust engine | 0.1278× | 0.1260–0.1296× | 0.44× | SLOWDOWN |
| calibration | `cal.large.request-records.08` | Python engine | 0.0209× | 0.0207–0.0211× | 7.39× | SLOWDOWN |
| calibration | `cal.large.request-records.08` | Native C engine | 1.1157× | 1.1042–1.1276× | 0.35× | FASTER |
| calibration | `cal.large.request-records.08` | Rust engine | 0.1554× | 0.1528–0.1575× | 0.32× | SLOWDOWN |
| calibration | `cal.large.request-records.09` | Python engine | 0.0182× | 0.0177–0.0186× | 7.49× | SLOWDOWN |
| calibration | `cal.large.request-records.09` | Native C engine | 1.0625× | 1.0468–1.0745× | 0.41× | FASTER |
| calibration | `cal.large.request-records.09` | Rust engine | 0.1448× | 0.1414–0.1477× | 0.34× | SLOWDOWN |
| calibration | `cal.large.request-records.10` | Python engine | 0.0167× | 0.0164–0.0172× | 7.62× | SLOWDOWN |
| calibration | `cal.large.request-records.10` | Native C engine | 0.9901× | 0.9200–1.0467× | 0.49× | — |
| calibration | `cal.large.request-records.10` | Rust engine | 0.1342× | 0.1316–0.1376× | 0.38× | SLOWDOWN |
| calibration | `cal.large.request-records.11` | Python engine | 0.0151× | 0.0148–0.0154× | 7.66× | SLOWDOWN |
| calibration | `cal.large.request-records.11` | Native C engine | 0.9271× | 0.9039–0.9513× | 0.59× | — |
| calibration | `cal.large.request-records.11` | Rust engine | 0.1261× | 0.1235–0.1288× | 0.44× | SLOWDOWN |
| calibration | `cal.large.request-records.12` | Python engine | 0.0209× | 0.0207–0.0213× | 7.39× | SLOWDOWN |
| calibration | `cal.large.request-records.12` | Native C engine | 1.1030× | 1.0881–1.1178× | 0.35× | FASTER |
| calibration | `cal.large.request-records.12` | Rust engine | 0.1597× | 0.1561–0.1633× | 0.32× | SLOWDOWN |
| calibration | `cal.large.request-records.13` | Python engine | 0.0187× | 0.0185–0.0188× | 7.49× | SLOWDOWN |
| calibration | `cal.large.request-records.13` | Native C engine | 1.0095× | 0.9513–1.0550× | 0.41× | — |
| calibration | `cal.large.request-records.13` | Rust engine | 0.1437× | 0.1411–0.1459× | 0.34× | SLOWDOWN |
| calibration | `cal.large.request-records.14` | Python engine | 0.0162× | 0.0159–0.0164× | 7.62× | SLOWDOWN |
| calibration | `cal.large.request-records.14` | Native C engine | 0.9901× | 0.9779–1.0037× | 0.49× | — |
| calibration | `cal.large.request-records.14` | Rust engine | 0.1296× | 0.1284–0.1309× | 0.38× | SLOWDOWN |
| calibration | `cal.large.request-records.15` | Python engine | 0.0156× | 0.0154–0.0159× | 7.66× | SLOWDOWN |
| calibration | `cal.large.request-records.15` | Native C engine | 0.9796× | 0.9564–1.0042× | 0.59× | — |
| calibration | `cal.large.request-records.15` | Rust engine | 0.1253× | 0.1228–0.1278× | 0.44× | SLOWDOWN |
| calibration | `cal.large.request-records.16` | Python engine | 0.0214× | 0.0208–0.0222× | 7.39× | SLOWDOWN |
| calibration | `cal.large.request-records.16` | Native C engine | 1.0931× | 1.0669–1.1336× | 0.35× | FASTER |
| calibration | `cal.large.request-records.16` | Rust engine | 0.1600× | 0.1560–0.1662× | 0.32× | SLOWDOWN |
| calibration | `cal.large.request-records.17` | Python engine | 0.0187× | 0.0185–0.0190× | 7.49× | SLOWDOWN |
| calibration | `cal.large.request-records.17` | Native C engine | 1.0673× | 1.0468–1.0834× | 0.41× | FASTER |
| calibration | `cal.large.request-records.17` | Rust engine | 0.1427× | 0.1411–0.1444× | 0.34× | SLOWDOWN |
| calibration | `cal.large.request-records.18` | Python engine | 0.0162× | 0.0160–0.0164× | 7.62× | SLOWDOWN |
| calibration | `cal.large.request-records.18` | Native C engine | 1.0038× | 0.9903–1.0174× | 0.49× | — |
| calibration | `cal.large.request-records.18` | Rust engine | 0.1305× | 0.1286–0.1323× | 0.38× | SLOWDOWN |
| calibration | `cal.large.request-records.19` | Python engine | 0.0160× | 0.0157–0.0162× | 7.66× | SLOWDOWN |
| calibration | `cal.large.request-records.19` | Native C engine | 0.9661× | 0.9098–1.0090× | 0.59× | — |
| calibration | `cal.large.request-records.19` | Rust engine | 0.1290× | 0.1270–0.1309× | 0.44× | SLOWDOWN |
| calibration | `cal.large.request-records.20` | Python engine | 0.0210× | 0.0208–0.0212× | 7.39× | SLOWDOWN |
| calibration | `cal.large.request-records.20` | Native C engine | 1.1067× | 1.0957–1.1154× | 0.35× | FASTER |
| calibration | `cal.large.request-records.20` | Rust engine | 0.1560× | 0.1539–0.1580× | 0.32× | SLOWDOWN |
| calibration | `cal.large.request-records.21` | Python engine | 0.0187× | 0.0185–0.0190× | 7.49× | SLOWDOWN |
| calibration | `cal.large.request-records.21` | Native C engine | 1.0806× | 1.0696–1.0905× | 0.41× | FASTER |
| calibration | `cal.large.request-records.21` | Rust engine | 0.1433× | 0.1410–0.1455× | 0.34× | SLOWDOWN |
| calibration | `cal.large.request-records.22` | Python engine | 0.0165× | 0.0163–0.0167× | 7.62× | SLOWDOWN |
| calibration | `cal.large.request-records.22` | Native C engine | 1.0356× | 1.0181–1.0557× | 0.49× | FASTER |
| calibration | `cal.large.request-records.22` | Rust engine | 0.1321× | 0.1304–0.1338× | 0.38× | SLOWDOWN |
| calibration | `cal.large.request-records.23` | Python engine | 0.0156× | 0.0154–0.0159× | 7.66× | SLOWDOWN |
| calibration | `cal.large.request-records.23` | Native C engine | 0.9602× | 0.9020–1.0034× | 0.59× | — |
| calibration | `cal.large.request-records.23` | Rust engine | 0.1237× | 0.1212–0.1258× | 0.44× | SLOWDOWN |
| calibration | `cal.large.request-records.24` | Python engine | 0.0213× | 0.0207–0.0222× | 7.39× | SLOWDOWN |
| calibration | `cal.large.request-records.24` | Native C engine | 1.1326× | 1.1060–1.1774× | 0.35× | FASTER |
| calibration | `cal.large.request-records.24` | Rust engine | 0.1640× | 0.1593–0.1704× | 0.32× | SLOWDOWN |
| calibration | `cal.large.request-records.25` | Python engine | 0.0189× | 0.0181–0.0203× | 7.49× | SLOWDOWN |
| calibration | `cal.large.request-records.25` | Native C engine | 1.1035× | 1.0626–1.1768× | 0.41× | FASTER |
| calibration | `cal.large.request-records.25` | Rust engine | 0.1439× | 0.1365–0.1555× | 0.34× | SLOWDOWN |
| calibration | `cal.large.request-records.26` | Python engine | 0.0177× | 0.0168–0.0188× | 7.62× | SLOWDOWN |
| calibration | `cal.large.request-records.26` | Native C engine | 1.0463× | 1.0130–1.0921× | 0.49× | FASTER |
| calibration | `cal.large.request-records.26` | Rust engine | 0.1308× | 0.1262–0.1352× | 0.38× | SLOWDOWN |
| calibration | `cal.large.request-records.27` | Python engine | 0.0163× | 0.0153–0.0178× | 7.66× | SLOWDOWN |
| calibration | `cal.large.request-records.27` | Native C engine | 1.0282× | 0.9676–1.1215× | 0.59× | — |
| calibration | `cal.large.request-records.27` | Rust engine | 0.1276× | 0.1194–0.1387× | 0.44× | SLOWDOWN |
| calibration | `cal.large.request-records.28` | Python engine | 0.0213× | 0.0211–0.0217× | 7.39× | SLOWDOWN |
| calibration | `cal.large.request-records.28` | Native C engine | 1.1278× | 1.1137–1.1424× | 0.35× | FASTER |
| calibration | `cal.large.request-records.28` | Rust engine | 0.1579× | 0.1561–0.1602× | 0.32× | SLOWDOWN |
| calibration | `cal.large.request-records.29` | Python engine | 0.0187× | 0.0185–0.0189× | 7.49× | SLOWDOWN |
| calibration | `cal.large.request-records.29` | Native C engine | 1.0670× | 1.0129–1.1025× | 0.41× | FASTER |
| calibration | `cal.large.request-records.29` | Rust engine | 0.1401× | 0.1385–0.1416× | 0.34× | SLOWDOWN |
| calibration | `cal.large.request-records.30` | Python engine | 0.0167× | 0.0164–0.0171× | 7.62× | SLOWDOWN |
| calibration | `cal.large.request-records.30` | Native C engine | 1.0460× | 1.0216–1.0736× | 0.49× | FASTER |
| calibration | `cal.large.request-records.30` | Rust engine | 0.1282× | 0.1252–0.1315× | 0.38× | SLOWDOWN |
| calibration | `cal.large.request-records.31` | Python engine | 0.0163× | 0.0157–0.0171× | 7.66× | SLOWDOWN |
| calibration | `cal.large.request-records.31` | Native C engine | 1.0076× | 0.9375–1.0797× | 0.59× | — |
| calibration | `cal.large.request-records.31` | Rust engine | 0.1294× | 0.1247–0.1367× | 0.44× | SLOWDOWN |
| calibration | `cal.large.everyday-address.00` | Python engine | 0.0145× | 0.0143–0.0145× | 18.55× | SLOWDOWN |
| calibration | `cal.large.everyday-address.00` | Native C engine | 1.3078× | 1.2847–1.3258× | 0.11× | FASTER |
| calibration | `cal.large.everyday-address.00` | Rust engine | 0.0504× | 0.0499–0.0509× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.01` | Python engine | 0.0161× | 0.0157–0.0163× | 6.09× | SLOWDOWN |
| calibration | `cal.large.everyday-address.01` | Native C engine | 0.7854× | 0.7749–0.7960× | 0.22× | SLOWDOWN |
| calibration | `cal.large.everyday-address.01` | Rust engine | 0.1151× | 0.1132–0.1170× | 4.36× | SLOWDOWN |
| calibration | `cal.large.everyday-address.02` | Python engine | 0.0115× | 0.0112–0.0117× | 23.69× | SLOWDOWN |
| calibration | `cal.large.everyday-address.02` | Native C engine | 1.1549× | 1.1372–1.1731× | 0.09× | FASTER |
| calibration | `cal.large.everyday-address.02` | Rust engine | 0.2194× | 0.2160–0.2226× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.03` | Python engine | 0.0175× | 0.0170–0.0183× | 18.55× | SLOWDOWN |
| calibration | `cal.large.everyday-address.03` | Native C engine | 1.2709× | 1.2286–1.3200× | 0.11× | FASTER |
| calibration | `cal.large.everyday-address.03` | Rust engine | 0.0604× | 0.0581–0.0626× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.04` | Python engine | 0.0164× | 0.0162–0.0165× | 6.21× | SLOWDOWN |
| calibration | `cal.large.everyday-address.04` | Native C engine | 0.7610× | 0.7529–0.7684× | 0.13× | SLOWDOWN |
| calibration | `cal.large.everyday-address.04` | Rust engine | 0.1126× | 0.1117–0.1135× | 2.37× | SLOWDOWN |
| calibration | `cal.large.everyday-address.05` | Python engine | 0.0110× | 0.0109–0.0112× | 23.69× | SLOWDOWN |
| calibration | `cal.large.everyday-address.05` | Native C engine | 1.1394× | 1.1125–1.1591× | 0.09× | FASTER |
| calibration | `cal.large.everyday-address.05` | Rust engine | 0.2092× | 0.2068–0.2114× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.06` | Python engine | 0.0161× | 0.0158–0.0163× | 18.55× | SLOWDOWN |
| calibration | `cal.large.everyday-address.06` | Native C engine | 1.2806× | 1.2593–1.3021× | 0.11× | FASTER |
| calibration | `cal.large.everyday-address.06` | Rust engine | 0.0533× | 0.0522–0.0544× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.07` | Python engine | 0.0160× | 0.0158–0.0162× | 5.52× | SLOWDOWN |
| calibration | `cal.large.everyday-address.07` | Native C engine | 0.7931× | 0.7760–0.8085× | 0.53× | SLOWDOWN |
| calibration | `cal.large.everyday-address.07` | Rust engine | 0.1201× | 0.1177–0.1223× | 10.49× | SLOWDOWN |
| calibration | `cal.large.everyday-address.08` | Python engine | 0.0106× | 0.0103–0.0107× | 23.69× | SLOWDOWN |
| calibration | `cal.large.everyday-address.08` | Native C engine | 1.1508× | 1.1357–1.1649× | 0.09× | FASTER |
| calibration | `cal.large.everyday-address.08` | Rust engine | 0.1954× | 0.1814–0.2035× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.09` | Python engine | 0.0150× | 0.0148–0.0152× | 18.55× | SLOWDOWN |
| calibration | `cal.large.everyday-address.09` | Native C engine | 1.2816× | 1.2654–1.2998× | 0.11× | FASTER |
| calibration | `cal.large.everyday-address.09` | Rust engine | 0.0523× | 0.0518–0.0529× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.10` | Python engine | 0.0160× | 0.0159–0.0162× | 5.81× | SLOWDOWN |
| calibration | `cal.large.everyday-address.10` | Native C engine | 0.7383× | 0.6938–0.7646× | 0.37× | SLOWDOWN |
| calibration | `cal.large.everyday-address.10` | Rust engine | 0.1158× | 0.1146–0.1171× | 7.30× | SLOWDOWN |
| calibration | `cal.large.everyday-address.11` | Python engine | 0.0130× | 0.0126–0.0134× | 23.69× | SLOWDOWN |
| calibration | `cal.large.everyday-address.11` | Native C engine | 1.0385× | 0.8376–1.1771× | 0.09× | — |
| calibration | `cal.large.everyday-address.11` | Rust engine | 0.2383× | 0.2333–0.2432× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.12` | Python engine | 0.0146× | 0.0144–0.0147× | 18.55× | SLOWDOWN |
| calibration | `cal.large.everyday-address.12` | Native C engine | 1.2467× | 1.1187–1.3397× | 0.11× | FASTER |
| calibration | `cal.large.everyday-address.12` | Rust engine | 0.0496× | 0.0491–0.0501× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.13` | Python engine | 0.0161× | 0.0159–0.0162× | 6.10× | SLOWDOWN |
| calibration | `cal.large.everyday-address.13` | Native C engine | 0.7827× | 0.7752–0.7908× | 0.22× | SLOWDOWN |
| calibration | `cal.large.everyday-address.13` | Rust engine | 0.1168× | 0.1143–0.1191× | 4.23× | SLOWDOWN |
| calibration | `cal.large.everyday-address.14` | Python engine | 0.0116× | 0.0114–0.0118× | 23.69× | SLOWDOWN |
| calibration | `cal.large.everyday-address.14` | Native C engine | 1.1383× | 1.1177–1.1570× | 0.09× | FASTER |
| calibration | `cal.large.everyday-address.14` | Rust engine | 0.2195× | 0.2157–0.2233× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.15` | Python engine | 0.0176× | 0.0172–0.0179× | 18.55× | SLOWDOWN |
| calibration | `cal.large.everyday-address.15` | Native C engine | 1.2597× | 1.2369–1.2863× | 0.11× | FASTER |
| calibration | `cal.large.everyday-address.15` | Rust engine | 0.0598× | 0.0570–0.0617× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.16` | Python engine | 0.0157× | 0.0142–0.0174× | 6.20× | SLOWDOWN |
| calibration | `cal.large.everyday-address.16` | Native C engine | 0.7408× | 0.6657–0.8013× | 0.14× | SLOWDOWN |
| calibration | `cal.large.everyday-address.16` | Rust engine | 0.1114× | 0.0990–0.1262× | 2.44× | SLOWDOWN |
| calibration | `cal.large.everyday-address.17` | Python engine | 0.0108× | 0.0095–0.0124× | 23.69× | SLOWDOWN |
| calibration | `cal.large.everyday-address.17` | Native C engine | 1.1778× | 1.1536–1.2075× | 0.09× | FASTER |
| calibration | `cal.large.everyday-address.17` | Rust engine | 0.2170× | 0.1991–0.2443× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.18` | Python engine | 0.0161× | 0.0148–0.0181× | 18.55× | SLOWDOWN |
| calibration | `cal.large.everyday-address.18` | Native C engine | 1.3074× | 1.1593–1.4938× | 0.11× | FASTER |
| calibration | `cal.large.everyday-address.18` | Rust engine | 0.0555× | 0.0543–0.0565× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.19` | Python engine | 0.0167× | 0.0159–0.0183× | 5.52× | SLOWDOWN |
| calibration | `cal.large.everyday-address.19` | Native C engine | 0.7866× | 0.7654–0.8057× | 0.53× | SLOWDOWN |
| calibration | `cal.large.everyday-address.19` | Rust engine | 0.1254× | 0.1187–0.1378× | 10.49× | SLOWDOWN |
| calibration | `cal.large.everyday-address.20` | Python engine | 0.0109× | 0.0104–0.0119× | 23.69× | SLOWDOWN |
| calibration | `cal.large.everyday-address.20` | Native C engine | 1.1820× | 1.1258–1.2887× | 0.09× | FASTER |
| calibration | `cal.large.everyday-address.20` | Rust engine | 0.2078× | 0.1957–0.2274× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.21` | Python engine | 0.0159× | 0.0151–0.0173× | 18.55× | SLOWDOWN |
| calibration | `cal.large.everyday-address.21` | Native C engine | 1.3612× | 1.2914–1.4813× | 0.11× | FASTER |
| calibration | `cal.large.everyday-address.21` | Rust engine | 0.0522× | 0.0497–0.0569× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.22` | Python engine | 0.0160× | 0.0159–0.0160× | 5.84× | SLOWDOWN |
| calibration | `cal.large.everyday-address.22` | Native C engine | 0.7721× | 0.7675–0.7766× | 0.36× | SLOWDOWN |
| calibration | `cal.large.everyday-address.22` | Rust engine | 0.1160× | 0.1146–0.1170× | 7.10× | SLOWDOWN |
| calibration | `cal.large.everyday-address.23` | Python engine | 0.0126× | 0.0123–0.0129× | 23.69× | SLOWDOWN |
| calibration | `cal.large.everyday-address.23` | Native C engine | 1.0530× | 0.9464–1.1450× | 0.09× | — |
| calibration | `cal.large.everyday-address.23` | Rust engine | 0.2218× | 0.2005–0.2365× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.24` | Python engine | 0.0145× | 0.0144–0.0147× | 18.55× | SLOWDOWN |
| calibration | `cal.large.everyday-address.24` | Native C engine | 1.3227× | 1.3093–1.3369× | 0.11× | FASTER |
| calibration | `cal.large.everyday-address.24` | Rust engine | 0.0480× | 0.0476–0.0485× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.25` | Python engine | 0.0160× | 0.0158–0.0161× | 6.07× | SLOWDOWN |
| calibration | `cal.large.everyday-address.25` | Native C engine | 0.7366× | 0.6957–0.7602× | 0.22× | SLOWDOWN |
| calibration | `cal.large.everyday-address.25` | Rust engine | 0.1121× | 0.1101–0.1139× | 4.49× | SLOWDOWN |
| calibration | `cal.large.everyday-address.26` | Python engine | 0.0116× | 0.0114–0.0117× | 23.69× | SLOWDOWN |
| calibration | `cal.large.everyday-address.26` | Native C engine | 1.1022× | 1.0314–1.1548× | 0.09× | FASTER |
| calibration | `cal.large.everyday-address.26` | Rust engine | 0.2152× | 0.2105–0.2193× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.27` | Python engine | 0.0179× | 0.0173–0.0184× | 18.55× | SLOWDOWN |
| calibration | `cal.large.everyday-address.27` | Native C engine | 1.3057× | 1.2624–1.3553× | 0.11× | FASTER |
| calibration | `cal.large.everyday-address.27` | Rust engine | 0.0596× | 0.0578–0.0612× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.28` | Python engine | 0.0162× | 0.0161–0.0164× | 6.19× | SLOWDOWN |
| calibration | `cal.large.everyday-address.28` | Native C engine | 0.7251× | 0.6907–0.7465× | 0.14× | SLOWDOWN |
| calibration | `cal.large.everyday-address.28` | Rust engine | 0.1073× | 0.1050–0.1094× | 2.52× | SLOWDOWN |
| calibration | `cal.large.everyday-address.29` | Python engine | 0.0113× | 0.0107–0.0124× | 23.69× | SLOWDOWN |
| calibration | `cal.large.everyday-address.29` | Native C engine | 1.1918× | 1.1298–1.3059× | 0.09× | FASTER |
| calibration | `cal.large.everyday-address.29` | Rust engine | 0.2178× | 0.2077–0.2378× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.30` | Python engine | 0.0156× | 0.0153–0.0159× | 18.55× | SLOWDOWN |
| calibration | `cal.large.everyday-address.30` | Native C engine | 1.2877× | 1.2650–1.3057× | 0.11× | FASTER |
| calibration | `cal.large.everyday-address.30` | Rust engine | 0.0545× | 0.0536–0.0554× | 0.06× | SLOWDOWN |
| calibration | `cal.large.everyday-address.31` | Python engine | 0.0157× | 0.0155–0.0159× | 5.55× | SLOWDOWN |
| calibration | `cal.large.everyday-address.31` | Native C engine | 0.7807× | 0.7714–0.7902× | 0.53× | SLOWDOWN |
| calibration | `cal.large.everyday-address.31` | Rust engine | 0.1208× | 0.1179–0.1230× | 10.23× | SLOWDOWN |
| calibration | `cal.large.structured-text.00` | Python engine | 0.0140× | 0.0138–0.0142× | 21.12× | SLOWDOWN |
| calibration | `cal.large.structured-text.00` | Native C engine | 1.4742× | 1.3937–1.5285× | 0.34× | FASTER |
| calibration | `cal.large.structured-text.00` | Rust engine | 0.0980× | 0.0956–0.0999× | 0.31× | SLOWDOWN |
| calibration | `cal.large.structured-text.01` | Python engine | 0.0111× | 0.0108–0.0117× | 20.92× | SLOWDOWN |
| calibration | `cal.large.structured-text.01` | Native C engine | 1.4265× | 1.3794–1.4985× | 0.19× | FASTER |
| calibration | `cal.large.structured-text.01` | Rust engine | 0.0590× | 0.0570–0.0620× | 3.10× | SLOWDOWN |
| calibration | `cal.large.structured-text.02` | Python engine | 0.0066× | 0.0063–0.0070× | 12.12× | SLOWDOWN |
| calibration | `cal.large.structured-text.02` | Native C engine | 1.9551× | 1.8766–2.0775× | 0.30× | FASTER |
| calibration | `cal.large.structured-text.02` | Rust engine | 0.0481× | 0.0460–0.0512× | 10.96× | SLOWDOWN |
| calibration | `cal.large.structured-text.03` | Python engine | 0.0121× | 0.0120–0.0123× | 24.25× | SLOWDOWN |
| calibration | `cal.large.structured-text.03` | Native C engine | 1.5117× | 1.4847–1.5391× | 0.58× | FASTER |
| calibration | `cal.large.structured-text.03` | Rust engine | 0.0919× | 0.0906–0.0931× | 0.43× | SLOWDOWN |
| calibration | `cal.large.structured-text.04` | Python engine | 0.0113× | 0.0110–0.0116× | 18.56× | SLOWDOWN |
| calibration | `cal.large.structured-text.04` | Native C engine | 1.3614× | 1.3306–1.3945× | 0.12× | FASTER |
| calibration | `cal.large.structured-text.04` | Rust engine | 0.0599× | 0.0587–0.0614× | 1.78× | SLOWDOWN |
| calibration | `cal.large.structured-text.05` | Python engine | 0.0078× | 0.0076–0.0080× | 11.51× | SLOWDOWN |
| calibration | `cal.large.structured-text.05` | Native C engine | 1.7969× | 1.7567–1.8598× | 0.17× | FASTER |
| calibration | `cal.large.structured-text.05` | Rust engine | 0.0904× | 0.0885–0.0932× | 6.77× | SLOWDOWN |
| calibration | `cal.large.structured-text.06` | Python engine | 0.0132× | 0.0124–0.0145× | 32.80× | SLOWDOWN |
| calibration | `cal.large.structured-text.06` | Native C engine | 1.6264× | 1.5178–1.7947× | 0.48× | FASTER |
| calibration | `cal.large.structured-text.06` | Rust engine | 0.0963× | 0.0918–0.1019× | 0.38× | SLOWDOWN |
| calibration | `cal.large.structured-text.07` | Python engine | 0.0104× | 0.0099–0.0112× | 19.84× | SLOWDOWN |
| calibration | `cal.large.structured-text.07` | Native C engine | 1.4265× | 1.3063–1.5454× | 0.48× | FASTER |
| calibration | `cal.large.structured-text.07` | Rust engine | 0.0601× | 0.0577–0.0641× | 7.49× | SLOWDOWN |
| calibration | `cal.large.structured-text.08` | Python engine | 0.0089× | 0.0086–0.0096× | 10.99× | SLOWDOWN |
| calibration | `cal.large.structured-text.08` | Native C engine | 1.7293× | 1.6646–1.8544× | 0.11× | FASTER |
| calibration | `cal.large.structured-text.08` | Rust engine | 0.1597× | 0.1482–0.1725× | 3.49× | SLOWDOWN |
| calibration | `cal.large.structured-text.09` | Python engine | 0.0134× | 0.0128–0.0146× | 26.20× | SLOWDOWN |
| calibration | `cal.large.structured-text.09` | Native C engine | 1.5005× | 1.4413–1.5537× | 0.40× | FASTER |
| calibration | `cal.large.structured-text.09` | Rust engine | 0.0958× | 0.0946–0.0975× | 0.34× | SLOWDOWN |
| calibration | `cal.large.structured-text.10` | Python engine | 0.0106× | 0.0105–0.0107× | 20.75× | SLOWDOWN |
| calibration | `cal.large.structured-text.10` | Native C engine | 1.4203× | 1.4060–1.4347× | 0.33× | FASTER |
| calibration | `cal.large.structured-text.10` | Rust engine | 0.0531× | 0.0527–0.0536× | 5.56× | SLOWDOWN |
| calibration | `cal.large.structured-text.11` | Python engine | 0.0046× | 0.0046–0.0047× | 12.92× | SLOWDOWN |
| calibration | `cal.large.structured-text.11` | Native C engine | 1.8551× | 1.8381–1.8729× | 0.46× | FASTER |
| calibration | `cal.large.structured-text.11` | Rust engine | 0.0225× | 0.0223–0.0227× | 17.78× | SLOWDOWN |
| calibration | `cal.large.structured-text.12` | Python engine | 0.0136× | 0.0134–0.0139× | 21.12× | SLOWDOWN |
| calibration | `cal.large.structured-text.12` | Native C engine | 1.4972× | 1.4569–1.5297× | 0.34× | FASTER |
| calibration | `cal.large.structured-text.12` | Rust engine | 0.1015× | 0.1000–0.1033× | 0.31× | SLOWDOWN |
| calibration | `cal.large.structured-text.13` | Python engine | 0.0106× | 0.0105–0.0108× | 20.92× | SLOWDOWN |
| calibration | `cal.large.structured-text.13` | Native C engine | 1.3841× | 1.3611–1.4086× | 0.19× | FASTER |
| calibration | `cal.large.structured-text.13` | Rust engine | 0.0569× | 0.0559–0.0577× | 3.10× | SLOWDOWN |
| calibration | `cal.large.structured-text.14` | Python engine | 0.0062× | 0.0061–0.0062× | 12.12× | SLOWDOWN |
| calibration | `cal.large.structured-text.14` | Native C engine | 1.8250× | 1.7849–1.8573× | 0.30× | FASTER |
| calibration | `cal.large.structured-text.14` | Rust engine | 0.0448× | 0.0443–0.0453× | 10.96× | SLOWDOWN |
| calibration | `cal.large.structured-text.15` | Python engine | 0.0118× | 0.0116–0.0122× | 24.25× | SLOWDOWN |
| calibration | `cal.large.structured-text.15` | Native C engine | 1.3774× | 1.2613–1.4923× | 0.58× | FASTER |
| calibration | `cal.large.structured-text.15` | Rust engine | 0.0892× | 0.0870–0.0916× | 0.43× | SLOWDOWN |
| calibration | `cal.large.structured-text.16` | Python engine | 0.0110× | 0.0108–0.0112× | 18.58× | SLOWDOWN |
| calibration | `cal.large.structured-text.16` | Native C engine | 1.2803× | 1.1963–1.3382× | 0.12× | FASTER |
| calibration | `cal.large.structured-text.16` | Rust engine | 0.0599× | 0.0585–0.0612× | 1.71× | SLOWDOWN |
| calibration | `cal.large.structured-text.17` | Python engine | 0.0077× | 0.0076–0.0077× | 11.54× | SLOWDOWN |
| calibration | `cal.large.structured-text.17` | Native C engine | 1.7097× | 1.6886–1.7304× | 0.17× | FASTER |
| calibration | `cal.large.structured-text.17` | Rust engine | 0.0895× | 0.0879–0.0909× | 6.46× | SLOWDOWN |
| calibration | `cal.large.structured-text.18` | Python engine | 0.0112× | 0.0106–0.0119× | 32.80× | SLOWDOWN |
| calibration | `cal.large.structured-text.18` | Native C engine | 1.4967× | 1.4308–1.5653× | 0.48× | FASTER |
| calibration | `cal.large.structured-text.18` | Rust engine | 0.0878× | 0.0842–0.0919× | 0.38× | SLOWDOWN |
| calibration | `cal.large.structured-text.19` | Python engine | 0.0104× | 0.0099–0.0115× | 19.58× | SLOWDOWN |
| calibration | `cal.large.structured-text.19` | Native C engine | 1.4232× | 1.2528–1.6109× | 0.49× | FASTER |
| calibration | `cal.large.structured-text.19` | Rust engine | 0.0544× | 0.0514–0.0588× | 8.06× | SLOWDOWN |
| calibration | `cal.large.structured-text.20` | Python engine | 0.0088× | 0.0086–0.0090× | 10.99× | SLOWDOWN |
| calibration | `cal.large.structured-text.20` | Native C engine | 1.4906× | 1.2937–1.6350× | 0.11× | FASTER |
| calibration | `cal.large.structured-text.20` | Rust engine | 0.1530× | 0.1463–0.1582× | 3.67× | SLOWDOWN |
| calibration | `cal.large.structured-text.21` | Python engine | 0.0129× | 0.0127–0.0133× | 26.20× | SLOWDOWN |
| calibration | `cal.large.structured-text.21` | Native C engine | 1.5124× | 1.4848–1.5487× | 0.40× | FASTER |
| calibration | `cal.large.structured-text.21` | Rust engine | 0.0944× | 0.0925–0.0967× | 0.34× | SLOWDOWN |
| calibration | `cal.large.structured-text.22` | Python engine | 0.0105× | 0.0104–0.0105× | 21.11× | SLOWDOWN |
| calibration | `cal.large.structured-text.22` | Native C engine | 1.4355× | 1.4182–1.4527× | 0.32× | FASTER |
| calibration | `cal.large.structured-text.22` | Rust engine | 0.0610× | 0.0596–0.0622× | 4.76× | SLOWDOWN |
| calibration | `cal.large.structured-text.23` | Python engine | 0.0046× | 0.0046–0.0047× | 12.92× | SLOWDOWN |
| calibration | `cal.large.structured-text.23` | Native C engine | 1.8774× | 1.8563–1.8962× | 0.46× | FASTER |
| calibration | `cal.large.structured-text.23` | Rust engine | 0.0229× | 0.0226–0.0232× | 16.92× | SLOWDOWN |
| calibration | `cal.large.structured-text.24` | Python engine | 0.0138× | 0.0136–0.0141× | 21.12× | SLOWDOWN |
| calibration | `cal.large.structured-text.24` | Native C engine | 1.5020× | 1.4830–1.5211× | 0.34× | FASTER |
| calibration | `cal.large.structured-text.24` | Rust engine | 0.1000× | 0.0990–0.1010× | 0.31× | SLOWDOWN |
| calibration | `cal.large.structured-text.25` | Python engine | 0.0108× | 0.0107–0.0109× | 21.03× | SLOWDOWN |
| calibration | `cal.large.structured-text.25` | Native C engine | 1.2947× | 1.1452–1.3863× | 0.19× | FASTER |
| calibration | `cal.large.structured-text.25` | Rust engine | 0.0626× | 0.0619–0.0633× | 2.85× | SLOWDOWN |
| calibration | `cal.large.structured-text.26` | Python engine | 0.0063× | 0.0062–0.0065× | 12.06× | SLOWDOWN |
| calibration | `cal.large.structured-text.26` | Native C engine | 2.0215× | 1.9809–2.0761× | 0.30× | FASTER |
| calibration | `cal.large.structured-text.26` | Rust engine | 0.0484× | 0.0473–0.0498× | 10.36× | SLOWDOWN |
| calibration | `cal.large.structured-text.27` | Python engine | 0.0119× | 0.0117–0.0122× | 24.25× | SLOWDOWN |
| calibration | `cal.large.structured-text.27` | Native C engine | 1.4915× | 1.4239–1.5465× | 0.58× | FASTER |
| calibration | `cal.large.structured-text.27` | Rust engine | 0.0905× | 0.0887–0.0925× | 0.43× | SLOWDOWN |
| calibration | `cal.large.structured-text.28` | Python engine | 0.0118× | 0.0113–0.0120× | 18.53× | SLOWDOWN |
| calibration | `cal.large.structured-text.28` | Native C engine | 1.3147× | 1.3046–1.3265× | 0.12× | FASTER |
| calibration | `cal.large.structured-text.28` | Rust engine | 0.0554× | 0.0546–0.0562× | 1.85× | SLOWDOWN |
| calibration | `cal.large.structured-text.29` | Python engine | 0.0075× | 0.0072–0.0078× | 11.48× | SLOWDOWN |
| calibration | `cal.large.structured-text.29` | Native C engine | 1.8193× | 1.7884–1.8520× | 0.18× | FASTER |
| calibration | `cal.large.structured-text.29` | Rust engine | 0.0897× | 0.0875–0.0932× | 6.75× | SLOWDOWN |
| calibration | `cal.large.structured-text.30` | Python engine | 0.0122× | 0.0121–0.0123× | 33.46× | SLOWDOWN |
| calibration | `cal.large.structured-text.30` | Native C engine | 1.5353× | 1.5198–1.5502× | 0.48× | FASTER |
| calibration | `cal.large.structured-text.30` | Rust engine | 0.0900× | 0.0885–0.0913× | 0.38× | SLOWDOWN |
| calibration | `cal.large.structured-text.31` | Python engine | 0.0102× | 0.0101–0.0104× | 19.58× | SLOWDOWN |
| calibration | `cal.large.structured-text.31` | Native C engine | 1.4321× | 1.4214–1.4425× | 0.49× | FASTER |
| calibration | `cal.large.structured-text.31` | Rust engine | 0.0524× | 0.0515–0.0533× | 8.06× | SLOWDOWN |
| calibration | `cal.large.cleanup.00` | Python engine | 0.0366× | 0.0357–0.0380× | 5.56× | SLOWDOWN |
| calibration | `cal.large.cleanup.00` | Native C engine | 1.9093× | 1.8458–1.9903× | 0.25× | FASTER |
| calibration | `cal.large.cleanup.00` | Rust engine | 0.2602× | 0.2561–0.2661× | 1.42× | SLOWDOWN |
| calibration | `cal.large.cleanup.01` | Python engine | 0.0260× | 0.0250–0.0274× | 7.61× | SLOWDOWN |
| calibration | `cal.large.cleanup.01` | Native C engine | 1.8978× | 1.8205–1.9817× | 0.16× | FASTER |
| calibration | `cal.large.cleanup.01` | Rust engine | 0.2574× | 0.2502–0.2655× | 1.54× | SLOWDOWN |
| calibration | `cal.large.cleanup.02` | Python engine | 0.0319× | 0.0316–0.0322× | 5.67× | SLOWDOWN |
| calibration | `cal.large.cleanup.02` | Native C engine | 2.0316× | 2.0105–2.0553× | 0.45× | FASTER |
| calibration | `cal.large.cleanup.02` | Rust engine | 0.2603× | 0.2537–0.2655× | 3.12× | SLOWDOWN |
| calibration | `cal.large.cleanup.03` | Python engine | 0.0249× | 0.0248–0.0251× | 12.10× | SLOWDOWN |
| calibration | `cal.large.cleanup.03` | Native C engine | 2.2606× | 2.1523–2.3234× | 0.17× | FASTER |
| calibration | `cal.large.cleanup.03` | Rust engine | 0.3189× | 0.3108–0.3248× | 3.86× | SLOWDOWN |
| calibration | `cal.large.cleanup.04` | Python engine | 0.0396× | 0.0382–0.0423× | 5.55× | SLOWDOWN |
| calibration | `cal.large.cleanup.04` | Native C engine | 2.0029× | 1.9274–2.1486× | 0.25× | FASTER |
| calibration | `cal.large.cleanup.04` | Rust engine | 0.2779× | 0.2629–0.3016× | 1.54× | SLOWDOWN |
| calibration | `cal.large.cleanup.05` | Python engine | 0.0245× | 0.0243–0.0247× | 7.61× | SLOWDOWN |
| calibration | `cal.large.cleanup.05` | Native C engine | 1.8534× | 1.8389–1.8708× | 0.16× | FASTER |
| calibration | `cal.large.cleanup.05` | Rust engine | 0.2497× | 0.2413–0.2552× | 1.54× | SLOWDOWN |
| calibration | `cal.large.cleanup.06` | Python engine | 0.0345× | 0.0319–0.0387× | 5.67× | SLOWDOWN |
| calibration | `cal.large.cleanup.06` | Native C engine | 2.1548× | 1.9764–2.4017× | 0.45× | FASTER |
| calibration | `cal.large.cleanup.06` | Rust engine | 0.2780× | 0.2537–0.3116× | 3.12× | SLOWDOWN |
| calibration | `cal.large.cleanup.07` | Python engine | 0.0256× | 0.0246–0.0276× | 12.10× | SLOWDOWN |
| calibration | `cal.large.cleanup.07` | Native C engine | 2.3701× | 2.2794–2.5447× | 0.17× | FASTER |
| calibration | `cal.large.cleanup.07` | Rust engine | 0.3223× | 0.3057–0.3414× | 3.86× | SLOWDOWN |
| calibration | `cal.large.cleanup.08` | Python engine | 0.0376× | 0.0374–0.0378× | 5.55× | SLOWDOWN |
| calibration | `cal.large.cleanup.08` | Native C engine | 1.8637× | 1.7348–1.9374× | 0.25× | FASTER |
| calibration | `cal.large.cleanup.08` | Rust engine | 0.2656× | 0.2582–0.2728× | 1.51× | SLOWDOWN |
| calibration | `cal.large.cleanup.09` | Python engine | 0.0251× | 0.0250–0.0252× | 7.60× | SLOWDOWN |
| calibration | `cal.large.cleanup.09` | Native C engine | 1.8041× | 1.6364–1.9008× | 0.16× | FASTER |
| calibration | `cal.large.cleanup.09` | Rust engine | 0.2624× | 0.2615–0.2635× | 1.61× | SLOWDOWN |
| calibration | `cal.large.cleanup.10` | Python engine | 0.0335× | 0.0315–0.0365× | 5.67× | SLOWDOWN |
| calibration | `cal.large.cleanup.10` | Native C engine | 2.1238× | 2.0005–2.3175× | 0.45× | FASTER |
| calibration | `cal.large.cleanup.10` | Rust engine | 0.2723× | 0.2542–0.2968× | 3.12× | SLOWDOWN |
| calibration | `cal.large.cleanup.11` | Python engine | 0.0254× | 0.0252–0.0256× | 12.05× | SLOWDOWN |
| calibration | `cal.large.cleanup.11` | Native C engine | 2.3405× | 2.3307–2.3509× | 0.18× | FASTER |
| calibration | `cal.large.cleanup.11` | Rust engine | 0.3235× | 0.3155–0.3299× | 4.04× | SLOWDOWN |
| calibration | `cal.large.cleanup.12` | Python engine | 0.0362× | 0.0360–0.0365× | 5.56× | SLOWDOWN |
| calibration | `cal.large.cleanup.12` | Native C engine | 1.9106× | 1.8888–1.9324× | 0.25× | FASTER |
| calibration | `cal.large.cleanup.12` | Rust engine | 0.2505× | 0.2422–0.2581× | 1.42× | SLOWDOWN |
| calibration | `cal.large.cleanup.13` | Python engine | 0.0253× | 0.0251–0.0256× | 7.60× | SLOWDOWN |
| calibration | `cal.large.cleanup.13` | Native C engine | 1.8975× | 1.8791–1.9161× | 0.16× | FASTER |
| calibration | `cal.large.cleanup.13` | Rust engine | 0.2570× | 0.2494–0.2630× | 1.61× | SLOWDOWN |
| calibration | `cal.large.cleanup.14` | Python engine | 0.0321× | 0.0312–0.0337× | 5.67× | SLOWDOWN |
| calibration | `cal.large.cleanup.14` | Native C engine | 1.9013× | 1.7389–2.0775× | 0.45× | FASTER |
| calibration | `cal.large.cleanup.14` | Rust engine | 0.2591× | 0.2492–0.2725× | 3.12× | SLOWDOWN |
| calibration | `cal.large.cleanup.15` | Python engine | 0.0248× | 0.0238–0.0269× | 12.15× | SLOWDOWN |
| calibration | `cal.large.cleanup.15` | Native C engine | 2.3156× | 2.2137–2.5116× | 0.17× | FASTER |
| calibration | `cal.large.cleanup.15` | Rust engine | 0.3110× | 0.2912–0.3406× | 3.68× | SLOWDOWN |
| calibration | `cal.large.cleanup.16` | Python engine | 0.0369× | 0.0365–0.0376× | 5.56× | SLOWDOWN |
| calibration | `cal.large.cleanup.16` | Native C engine | 1.9280× | 1.9048–1.9613× | 0.25× | FASTER |
| calibration | `cal.large.cleanup.16` | Rust engine | 0.2639× | 0.2607–0.2685× | 1.45× | SLOWDOWN |
| calibration | `cal.large.cleanup.17` | Python engine | 0.0251× | 0.0235–0.0274× | 7.62× | SLOWDOWN |
| calibration | `cal.large.cleanup.17` | Native C engine | 1.8484× | 1.6707–2.0925× | 0.16× | FASTER |
| calibration | `cal.large.cleanup.17` | Rust engine | 0.2526× | 0.2336–0.2810× | 1.47× | SLOWDOWN |
| calibration | `cal.large.cleanup.18` | Python engine | 0.0315× | 0.0305–0.0327× | 5.67× | SLOWDOWN |
| calibration | `cal.large.cleanup.18` | Native C engine | 2.0386× | 2.0036–2.0956× | 0.45× | FASTER |
| calibration | `cal.large.cleanup.18` | Rust engine | 0.2623× | 0.2596–0.2643× | 3.12× | SLOWDOWN |
| calibration | `cal.large.cleanup.19` | Python engine | 0.0221× | 0.0216–0.0225× | 12.19× | SLOWDOWN |
| calibration | `cal.large.cleanup.19` | Native C engine | 2.1198× | 2.1027–2.1385× | 0.17× | FASTER |
| calibration | `cal.large.cleanup.19` | Rust engine | 0.2840× | 0.2744–0.2902× | 3.49× | SLOWDOWN |
| calibration | `cal.large.cleanup.20` | Python engine | 0.0381× | 0.0378–0.0384× | 5.55× | SLOWDOWN |
| calibration | `cal.large.cleanup.20` | Native C engine | 1.9412× | 1.9142–1.9655× | 0.25× | FASTER |
| calibration | `cal.large.cleanup.20` | Rust engine | 0.2751× | 0.2725–0.2774× | 1.54× | SLOWDOWN |
| calibration | `cal.large.cleanup.21` | Python engine | 0.0253× | 0.0247–0.0262× | 7.61× | SLOWDOWN |
| calibration | `cal.large.cleanup.21` | Native C engine | 1.8392× | 1.7525–1.8935× | 0.16× | FASTER |
| calibration | `cal.large.cleanup.21` | Rust engine | 0.2551× | 0.2488–0.2618× | 1.54× | SLOWDOWN |
| calibration | `cal.large.cleanup.22` | Python engine | 0.0351× | 0.0335–0.0380× | 5.64× | SLOWDOWN |
| calibration | `cal.large.cleanup.22` | Native C engine | 2.1182× | 2.0248–2.2937× | 0.45× | FASTER |
| calibration | `cal.large.cleanup.22` | Rust engine | 0.2897× | 0.2748–0.3150× | 3.39× | SLOWDOWN |
| calibration | `cal.large.cleanup.23` | Python engine | 0.0264× | 0.0241–0.0299× | 12.15× | SLOWDOWN |
| calibration | `cal.large.cleanup.23` | Native C engine | 2.2467× | 2.1987–2.2913× | 0.17× | FASTER |
| calibration | `cal.large.cleanup.23` | Rust engine | 0.3167× | 0.3086–0.3257× | 3.68× | SLOWDOWN |
| calibration | `cal.large.cleanup.24` | Python engine | 0.0385× | 0.0379–0.0395× | 5.55× | SLOWDOWN |
| calibration | `cal.large.cleanup.24` | Native C engine | 1.8698× | 1.6848–1.9923× | 0.25× | FASTER |
| calibration | `cal.large.cleanup.24` | Rust engine | 0.2755× | 0.2691–0.2836× | 1.54× | SLOWDOWN |
| calibration | `cal.large.cleanup.25` | Python engine | 0.0253× | 0.0242–0.0272× | 7.61× | SLOWDOWN |
| calibration | `cal.large.cleanup.25` | Native C engine | 1.8474× | 1.6571–2.0669× | 0.16× | FASTER |
| calibration | `cal.large.cleanup.25` | Rust engine | 0.2635× | 0.2524–0.2852× | 1.54× | SLOWDOWN |
| calibration | `cal.large.cleanup.26` | Python engine | 0.0321× | 0.0314–0.0327× | 5.67× | SLOWDOWN |
| calibration | `cal.large.cleanup.26` | Native C engine | 2.0200× | 1.9555–2.0793× | 0.45× | FASTER |
| calibration | `cal.large.cleanup.26` | Rust engine | 0.2592× | 0.2518–0.2656× | 3.12× | SLOWDOWN |
| calibration | `cal.large.cleanup.27` | Python engine | 0.0255× | 0.0253–0.0258× | 12.05× | SLOWDOWN |
| calibration | `cal.large.cleanup.27` | Native C engine | 2.3437× | 2.3036–2.3856× | 0.18× | FASTER |
| calibration | `cal.large.cleanup.27` | Rust engine | 0.3279× | 0.3141–0.3381× | 4.04× | SLOWDOWN |
| calibration | `cal.large.cleanup.28` | Python engine | 0.0360× | 0.0358–0.0362× | 5.56× | SLOWDOWN |
| calibration | `cal.large.cleanup.28` | Native C engine | 1.9019× | 1.8934–1.9109× | 0.25× | FASTER |
| calibration | `cal.large.cleanup.28` | Rust engine | 0.2551× | 0.2490–0.2596× | 1.42× | SLOWDOWN |
| calibration | `cal.large.cleanup.29` | Python engine | 0.0254× | 0.0251–0.0257× | 7.60× | SLOWDOWN |
| calibration | `cal.large.cleanup.29` | Native C engine | 1.8330× | 1.6946–1.9179× | 0.16× | FASTER |
| calibration | `cal.large.cleanup.29` | Rust engine | 0.2603× | 0.2548–0.2648× | 1.61× | SLOWDOWN |
| calibration | `cal.large.cleanup.30` | Python engine | 0.0314× | 0.0307–0.0319× | 5.67× | SLOWDOWN |
| calibration | `cal.large.cleanup.30` | Native C engine | 1.9965× | 1.9755–2.0172× | 0.45× | FASTER |
| calibration | `cal.large.cleanup.30` | Rust engine | 0.2582× | 0.2507–0.2628× | 3.12× | SLOWDOWN |
| calibration | `cal.large.cleanup.31` | Python engine | 0.0250× | 0.0247–0.0254× | 12.10× | SLOWDOWN |
| calibration | `cal.large.cleanup.31` | Native C engine | 2.1926× | 1.9599–2.3361× | 0.17× | FASTER |
| calibration | `cal.large.cleanup.31` | Rust engine | 0.3222× | 0.3169–0.3288× | 3.86× | SLOWDOWN |
| calibration | `cal.large.escape.00` | Python engine | 1.0336× | 0.9960–1.0888× | 1.00× | — |
| calibration | `cal.large.escape.00` | Native C engine | 3.3074× | 3.1816–3.5041× | 0.59× | FASTER |
| calibration | `cal.large.escape.00` | Rust engine | 1.0304× | 0.9906–1.0878× | 1.00× | — |
| calibration | `cal.large.escape.01` | Python engine | 0.9663× | 0.9185–0.9992× | 0.68× | — |
| calibration | `cal.large.escape.01` | Native C engine | 4.3256× | 4.2428–4.4086× | 0.32× | FASTER |
| calibration | `cal.large.escape.01` | Rust engine | 0.9770× | 0.8996–1.0271× | 0.68× | — |
| calibration | `cal.large.escape.02` | Python engine | 0.9498× | 0.8768–0.9944× | 1.00× | — |
| calibration | `cal.large.escape.02` | Native C engine | 2.9654× | 2.9344–2.9875× | 0.59× | FASTER |
| calibration | `cal.large.escape.02` | Rust engine | 0.9948× | 0.9794–1.0089× | 1.00× | — |
| calibration | `cal.large.escape.03` | Python engine | 0.9869× | 0.9681–1.0038× | 0.68× | — |
| calibration | `cal.large.escape.03` | Native C engine | 3.7041× | 3.6333–3.7901× | 0.32× | FASTER |
| calibration | `cal.large.escape.03` | Rust engine | 0.9777× | 0.9072–1.0238× | 0.68× | — |
| calibration | `cal.large.escape.04` | Python engine | 0.9746× | 0.9320–0.9983× | 1.00× | — |
| calibration | `cal.large.escape.04` | Native C engine | 3.2272× | 3.2051–3.2553× | 0.59× | FASTER |
| calibration | `cal.large.escape.04` | Rust engine | 1.0021× | 0.9986–1.0063× | 1.00× | — |
| calibration | `cal.large.escape.05` | Python engine | 0.9949× | 0.9896–0.9994× | 0.68× | — |
| calibration | `cal.large.escape.05` | Native C engine | 4.3078× | 4.2546–4.3548× | 0.32× | FASTER |
| calibration | `cal.large.escape.05` | Rust engine | 0.9749× | 0.8979–1.0207× | 0.68× | — |
| calibration | `cal.large.escape.06` | Python engine | 0.9995× | 0.9855–1.0161× | 1.00× | — |
| calibration | `cal.large.escape.06` | Native C engine | 2.9222× | 2.8960–2.9511× | 0.59× | FASTER |
| calibration | `cal.large.escape.06` | Rust engine | 0.9931× | 0.9863–0.9987× | 1.00× | — |
| calibration | `cal.large.escape.07` | Python engine | 0.9289× | 0.7994–1.0058× | 0.68× | — |
| calibration | `cal.large.escape.07` | Native C engine | 3.7763× | 3.6112–3.9635× | 0.32× | FASTER |
| calibration | `cal.large.escape.07` | Rust engine | 1.0200× | 1.0072–1.0342× | 0.68× | FASTER |
| calibration | `cal.large.escape.08` | Python engine | 0.9731× | 0.9405–0.9944× | 1.00× | — |
| calibration | `cal.large.escape.08` | Native C engine | 3.0441× | 2.8499–3.1523× | 0.59× | FASTER |
| calibration | `cal.large.escape.08` | Rust engine | 1.0000× | 0.9953–1.0043× | 1.00× | — |
| calibration | `cal.large.escape.09` | Python engine | 0.9957× | 0.9238–1.0700× | 0.68× | — |
| calibration | `cal.large.escape.09` | Native C engine | 4.4588× | 4.3313–4.6999× | 0.32× | FASTER |
| calibration | `cal.large.escape.09` | Rust engine | 1.0400× | 1.0121–1.0920× | 0.68× | FASTER |
| calibration | `cal.large.escape.10` | Python engine | 0.9878× | 0.9730–1.0018× | 1.00× | — |
| calibration | `cal.large.escape.10` | Native C engine | 2.9077× | 2.8357–3.0008× | 0.59× | FASTER |
| calibration | `cal.large.escape.10` | Rust engine | 1.0010× | 0.9837–1.0193× | 1.00× | — |
| calibration | `cal.large.escape.11` | Python engine | 1.0013× | 0.9806–1.0205× | 0.68× | — |
| calibration | `cal.large.escape.11` | Native C engine | 3.9057× | 3.7772–4.0472× | 0.32× | FASTER |
| calibration | `cal.large.escape.11` | Rust engine | 1.0250× | 1.0067–1.0455× | 0.68× | FASTER |
| calibration | `cal.large.escape.12` | Python engine | 1.0145× | 0.9854–1.0545× | 1.00× | — |
| calibration | `cal.large.escape.12` | Native C engine | 3.2821× | 3.1960–3.4050× | 0.59× | FASTER |
| calibration | `cal.large.escape.12` | Rust engine | 1.0073× | 0.9650–1.0521× | 1.00× | — |
| calibration | `cal.large.escape.13` | Python engine | 0.9990× | 0.9939–1.0034× | 0.68× | — |
| calibration | `cal.large.escape.13` | Native C engine | 4.3525× | 4.2586–4.4778× | 0.32× | FASTER |
| calibration | `cal.large.escape.13` | Rust engine | 1.0163× | 1.0127–1.0202× | 0.68× | FASTER |
| calibration | `cal.large.escape.14` | Python engine | 0.9848× | 0.9731–0.9954× | 1.00× | — |
| calibration | `cal.large.escape.14` | Native C engine | 2.9214× | 2.8844–2.9542× | 0.59× | FASTER |
| calibration | `cal.large.escape.14` | Rust engine | 1.0074× | 0.9894–1.0233× | 1.00× | — |
| calibration | `cal.large.escape.15` | Python engine | 1.0039× | 0.9836–1.0286× | 0.68× | — |
| calibration | `cal.large.escape.15` | Native C engine | 3.9980× | 3.7988–4.2201× | 0.32× | FASTER |
| calibration | `cal.large.escape.15` | Rust engine | 1.0195× | 0.9960–1.0511× | 0.68× | — |
| calibration | `cal.large.escape.16` | Python engine | 0.9908× | 0.9862–0.9947× | 1.00× | — |
| calibration | `cal.large.escape.16` | Native C engine | 3.2141× | 3.1961–3.2311× | 0.59× | FASTER |
| calibration | `cal.large.escape.16` | Rust engine | 0.9736× | 0.9338–0.9970× | 1.00× | — |
| calibration | `cal.large.escape.17` | Python engine | 1.0028× | 0.9925–1.0133× | 0.68× | — |
| calibration | `cal.large.escape.17` | Native C engine | 4.3130× | 4.2238–4.3925× | 0.32× | FASTER |
| calibration | `cal.large.escape.17` | Rust engine | 1.0219× | 1.0120–1.0312× | 0.68× | FASTER |
| calibration | `cal.large.escape.18` | Python engine | 0.9845× | 0.9737–0.9914× | 1.00× | — |
| calibration | `cal.large.escape.18` | Native C engine | 2.9341× | 2.9112–2.9554× | 0.59× | FASTER |
| calibration | `cal.large.escape.18` | Rust engine | 0.9911× | 0.9803–1.0040× | 1.00× | — |
| calibration | `cal.large.escape.19` | Python engine | 0.9705× | 0.9299–0.9956× | 0.68× | — |
| calibration | `cal.large.escape.19` | Native C engine | 3.9342× | 3.7981–4.0892× | 0.32× | FASTER |
| calibration | `cal.large.escape.19` | Rust engine | 1.0136× | 1.0003–1.0257× | 0.68× | FASTER |
| calibration | `cal.large.escape.20` | Python engine | 1.0063× | 0.9897–1.0349× | 1.00× | — |
| calibration | `cal.large.escape.20` | Native C engine | 3.0899× | 2.7731–3.3236× | 0.59× | FASTER |
| calibration | `cal.large.escape.20` | Rust engine | 1.0033× | 0.9670–1.0407× | 1.00× | — |
| calibration | `cal.large.escape.21` | Python engine | 1.0244× | 0.9599–1.0982× | 0.68× | — |
| calibration | `cal.large.escape.21` | Native C engine | 4.6036× | 4.3759–4.9114× | 0.32× | FASTER |
| calibration | `cal.large.escape.21` | Rust engine | 1.0527× | 1.0029–1.1254× | 0.68× | FASTER |
| calibration | `cal.large.escape.22` | Python engine | 1.0885× | 0.9549–1.3687× | 1.00× | — |
| calibration | `cal.large.escape.22` | Native C engine | 3.3222× | 2.9245–4.2512× | 0.59× | FASTER |
| calibration | `cal.large.escape.22` | Rust engine | 1.1179× | 0.9915–1.4004× | 1.00× | — |
| calibration | `cal.large.escape.23` | Python engine | 0.9985× | 0.9871–1.0084× | 0.68× | — |
| calibration | `cal.large.escape.23` | Native C engine | 3.7467× | 3.6855–3.7978× | 0.32× | FASTER |
| calibration | `cal.large.escape.23` | Rust engine | 1.0285× | 1.0126–1.0432× | 0.68× | FASTER |
| calibration | `cal.large.escape.24` | Python engine | 0.9959× | 0.9748–1.0163× | 1.00× | — |
| calibration | `cal.large.escape.24` | Native C engine | 3.2614× | 3.2075–3.3322× | 0.59× | FASTER |
| calibration | `cal.large.escape.24` | Rust engine | 1.0027× | 0.9878–1.0218× | 1.00× | — |
| calibration | `cal.large.escape.25` | Python engine | 0.9967× | 0.9908–1.0029× | 0.68× | — |
| calibration | `cal.large.escape.25` | Native C engine | 4.3643× | 4.3030–4.4111× | 0.32× | FASTER |
| calibration | `cal.large.escape.25` | Rust engine | 1.0117× | 1.0079–1.0149× | 0.68× | FASTER |
| calibration | `cal.large.escape.26` | Python engine | 0.9975× | 0.9818–1.0116× | 1.00× | — |
| calibration | `cal.large.escape.26` | Native C engine | 2.7384× | 2.4239–2.9246× | 0.59× | FASTER |
| calibration | `cal.large.escape.26` | Rust engine | 0.9907× | 0.9605–1.0151× | 1.00× | — |
| calibration | `cal.large.escape.27` | Python engine | 0.9939× | 0.9757–1.0134× | 0.68× | — |
| calibration | `cal.large.escape.27` | Native C engine | 4.0514× | 3.7680–4.5396× | 0.32× | FASTER |
| calibration | `cal.large.escape.27` | Rust engine | 1.0392× | 0.9606–1.1710× | 0.68× | — |
| calibration | `cal.large.escape.28` | Python engine | 0.9916× | 0.9828–0.9976× | 1.00× | — |
| calibration | `cal.large.escape.28` | Native C engine | 3.1438× | 2.9841–3.2360× | 0.59× | FASTER |
| calibration | `cal.large.escape.28` | Rust engine | 0.9738× | 0.9292–1.0037× | 1.00× | — |
| calibration | `cal.large.escape.29` | Python engine | 0.9939× | 0.9842–1.0033× | 0.68× | — |
| calibration | `cal.large.escape.29` | Native C engine | 4.4465× | 4.3718–4.5426× | 0.32× | FASTER |
| calibration | `cal.large.escape.29` | Rust engine | 0.9811× | 0.9141–1.0224× | 0.68× | — |
| calibration | `cal.large.escape.30` | Python engine | 0.9851× | 0.9713–0.9989× | 1.00× | — |
| calibration | `cal.large.escape.30` | Native C engine | 2.8702× | 2.8317–2.9084× | 0.59× | FASTER |
| calibration | `cal.large.escape.30` | Rust engine | 0.9848× | 0.9740–0.9949× | 1.00× | — |
| calibration | `cal.large.escape.31` | Python engine | 1.0090× | 0.8958–1.1535× | 0.68× | — |
| calibration | `cal.large.escape.31` | Native C engine | 3.8091× | 3.3626–4.3169× | 0.32× | FASTER |
| calibration | `cal.large.escape.31` | Rust engine | 1.0407× | 0.9807–1.1472× | 0.68× | — |
| calibration | `cal.large.bytes-replace.00` | Python engine | 0.0267× | 0.0257–0.0276× | 8.07× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.00` | Native C engine | 1.0364× | 0.9969–1.0731× | 0.85× | — |
| calibration | `cal.large.bytes-replace.00` | Rust engine | 0.0862× | 0.0848–0.0882× | 1.47× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.01` | Python engine | 0.0228× | 0.0222–0.0238× | 9.37× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.01` | Native C engine | 1.1634× | 1.1159–1.2512× | 1.47× | FASTER |
| calibration | `cal.large.bytes-replace.01` | Rust engine | 0.0875× | 0.0842–0.0934× | 2.53× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.02` | Python engine | 0.0224× | 0.0219–0.0231× | 9.62× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.02` | Native C engine | 1.2686× | 1.2395–1.3146× | 2.55× | FASTER |
| calibration | `cal.large.bytes-replace.02` | Rust engine | 0.0894× | 0.0877–0.0918× | 3.85× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.03` | Python engine | 0.0205× | 0.0198–0.0215× | 9.81× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.03` | Native C engine | 1.3118× | 1.2492–1.3864× | 2.68× | FASTER |
| calibration | `cal.large.bytes-replace.03` | Rust engine | 0.0881× | 0.0840–0.0932× | 4.91× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.04` | Python engine | 0.0270× | 0.0258–0.0289× | 8.06× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.04` | Native C engine | 1.0159× | 0.9567–1.0582× | 0.85× | — |
| calibration | `cal.large.bytes-replace.04` | Rust engine | 0.0852× | 0.0789–0.0945× | 1.60× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.05` | Python engine | 0.0221× | 0.0204–0.0244× | 9.75× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.05` | Native C engine | 1.1186× | 1.0406–1.2434× | 1.28× | FASTER |
| calibration | `cal.large.bytes-replace.05` | Rust engine | 0.0842× | 0.0765–0.0938× | 3.15× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.06` | Python engine | 0.0236× | 0.0224–0.0260× | 9.55× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.06` | Native C engine | 1.3215× | 1.2488–1.4548× | 2.54× | FASTER |
| calibration | `cal.large.bytes-replace.06` | Rust engine | 0.0917× | 0.0868–0.1009× | 4.71× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.07` | Python engine | 0.0200× | 0.0196–0.0203× | 9.81× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.07` | Native C engine | 1.2961× | 1.2772–1.3134× | 2.68× | FASTER |
| calibration | `cal.large.bytes-replace.07` | Rust engine | 0.0873× | 0.0861–0.0884× | 4.91× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.08` | Python engine | 0.0278× | 0.0263–0.0306× | 8.06× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.08` | Native C engine | 1.0483× | 1.0171–1.0762× | 0.85× | FASTER |
| calibration | `cal.large.bytes-replace.08` | Rust engine | 0.0879× | 0.0829–0.0967× | 1.60× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.09` | Python engine | 0.0221× | 0.0219–0.0223× | 9.35× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.09` | Native C engine | 1.0028× | 0.8944–1.1082× | 1.47× | — |
| calibration | `cal.large.bytes-replace.09` | Rust engine | 0.0841× | 0.0834–0.0848× | 2.77× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.10` | Python engine | 0.0233× | 0.0231–0.0236× | 9.02× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.10` | Native C engine | 1.0712× | 1.0494–1.0894× | 1.33× | FASTER |
| calibration | `cal.large.bytes-replace.10` | Rust engine | 0.0706× | 0.0697–0.0715× | 5.56× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.11` | Python engine | 0.0200× | 0.0198–0.0202× | 9.81× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.11` | Native C engine | 1.2501× | 1.1720–1.3092× | 2.68× | FASTER |
| calibration | `cal.large.bytes-replace.11` | Rust engine | 0.0869× | 0.0857–0.0880× | 4.91× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.12` | Python engine | 0.0268× | 0.0265–0.0272× | 8.06× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.12` | Native C engine | 1.0662× | 1.0524–1.0802× | 0.85× | FASTER |
| calibration | `cal.large.bytes-replace.12` | Rust engine | 0.0854× | 0.0839–0.0868× | 1.60× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.13` | Python engine | 0.0224× | 0.0214–0.0237× | 9.38× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.13` | Native C engine | 1.1335× | 1.0133–1.2383× | 1.47× | FASTER |
| calibration | `cal.large.bytes-replace.13` | Rust engine | 0.0870× | 0.0822–0.0926× | 2.28× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.14` | Python engine | 0.0215× | 0.0211–0.0218× | 9.55× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.14` | Native C engine | 1.1913× | 1.0921–1.2515× | 2.54× | FASTER |
| calibration | `cal.large.bytes-replace.14` | Rust engine | 0.0840× | 0.0830–0.0851× | 4.71× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.15` | Python engine | 0.0236× | 0.0227–0.0250× | 10.04× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.15` | Native C engine | 1.0063× | 0.8759–1.1278× | 1.42× | — |
| calibration | `cal.large.bytes-replace.15` | Rust engine | 0.0580× | 0.0557–0.0615× | 10.89× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.16` | Python engine | 0.0263× | 0.0258–0.0269× | 8.06× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.16` | Native C engine | 1.0554× | 1.0330–1.0784× | 0.85× | FASTER |
| calibration | `cal.large.bytes-replace.16` | Rust engine | 0.0833× | 0.0809–0.0853× | 1.60× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.17` | Python engine | 0.0230× | 0.0224–0.0238× | 9.35× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.17` | Native C engine | 1.1579× | 1.1336–1.1905× | 1.47× | FASTER |
| calibration | `cal.large.bytes-replace.17` | Rust engine | 0.0863× | 0.0834–0.0900× | 2.77× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.18` | Python engine | 0.0223× | 0.0221–0.0224× | 9.52× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.18` | Native C engine | 1.2243× | 1.1684–1.2573× | 2.54× | FASTER |
| calibration | `cal.large.bytes-replace.18` | Rust engine | 0.0865× | 0.0854–0.0874× | 5.13× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.19` | Python engine | 0.0206× | 0.0196–0.0221× | 9.81× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.19` | Native C engine | 1.3620× | 1.3052–1.4370× | 2.68× | FASTER |
| calibration | `cal.large.bytes-replace.19` | Rust engine | 0.0905× | 0.0864–0.0961× | 4.91× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.20` | Python engine | 0.0264× | 0.0255–0.0277× | 8.08× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.20` | Native C engine | 1.0821× | 1.0275–1.1491× | 0.85× | FASTER |
| calibration | `cal.large.bytes-replace.20` | Rust engine | 0.0887× | 0.0857–0.0927× | 1.34× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.21` | Python engine | 0.0225× | 0.0222–0.0230× | 9.35× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.21` | Native C engine | 1.0975× | 1.0350–1.1504× | 1.47× | FASTER |
| calibration | `cal.large.bytes-replace.21` | Rust engine | 0.0853× | 0.0819–0.0882× | 2.77× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.22` | Python engine | 0.0212× | 0.0204–0.0218× | 9.62× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.22` | Native C engine | 1.2170× | 1.1744–1.2494× | 2.55× | FASTER |
| calibration | `cal.large.bytes-replace.22` | Rust engine | 0.0865× | 0.0841–0.0880× | 3.85× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.23` | Python engine | 0.0205× | 0.0199–0.0216× | 9.81× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.23` | Native C engine | 1.3075× | 1.2665–1.3702× | 2.68× | FASTER |
| calibration | `cal.large.bytes-replace.23` | Rust engine | 0.0888× | 0.0860–0.0934× | 4.91× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.24` | Python engine | 0.0277× | 0.0264–0.0293× | 8.06× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.24` | Native C engine | 1.0764× | 1.0157–1.1420× | 0.85× | FASTER |
| calibration | `cal.large.bytes-replace.24` | Rust engine | 0.0867× | 0.0794–0.0928× | 1.60× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.25` | Python engine | 0.0229× | 0.0213–0.0256× | 9.76× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.25` | Native C engine | 1.0652× | 1.0323–1.1157× | 1.28× | FASTER |
| calibration | `cal.large.bytes-replace.25` | Rust engine | 0.0846× | 0.0812–0.0894× | 2.89× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.26` | Python engine | 0.0212× | 0.0204–0.0220× | 9.52× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.26` | Native C engine | 1.2160× | 1.1594–1.2612× | 2.54× | FASTER |
| calibration | `cal.large.bytes-replace.26` | Rust engine | 0.0841× | 0.0810–0.0871× | 5.13× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.27` | Python engine | 0.0194× | 0.0187–0.0202× | 9.79× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.27` | Native C engine | 1.2956× | 1.2200–1.3719× | 2.65× | FASTER |
| calibration | `cal.large.bytes-replace.27` | Rust engine | 0.0800× | 0.0714–0.0874× | 5.77× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.28` | Python engine | 0.0254× | 0.0249–0.0258× | 8.04× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.28` | Native C engine | 1.0062× | 0.9447–1.0538× | 0.85× | — |
| calibration | `cal.large.bytes-replace.28` | Rust engine | 0.0811× | 0.0772–0.0837× | 1.74× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.29` | Python engine | 0.0236× | 0.0215–0.0260× | 9.33× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.29` | Native C engine | 1.2576× | 1.1663–1.3867× | 1.47× | FASTER |
| calibration | `cal.large.bytes-replace.29` | Rust engine | 0.0898× | 0.0828–0.0988× | 3.02× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.30` | Python engine | 0.0225× | 0.0213–0.0234× | 9.01× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.30` | Native C engine | 1.0881× | 1.0668–1.1074× | 1.33× | FASTER |
| calibration | `cal.large.bytes-replace.30` | Rust engine | 0.0696× | 0.0684–0.0707× | 6.07× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.31` | Python engine | 0.0207× | 0.0189–0.0232× | 9.80× | SLOWDOWN |
| calibration | `cal.large.bytes-replace.31` | Native C engine | 1.3238× | 1.1998–1.4739× | 2.66× | FASTER |
| calibration | `cal.large.bytes-replace.31` | Rust engine | 0.0882× | 0.0800–0.0987× | 5.35× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.00` | Python engine | 0.0204× | 0.0196–0.0213× | 6.32× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.00` | Native C engine | 1.1401× | 1.0108–1.2334× | 0.21× | FASTER |
| calibration | `cal.large.ascii-mode.00` | Rust engine | 0.0943× | 0.0919–0.0964× | 0.93× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.01` | Python engine | 0.0215× | 0.0197–0.0239× | 6.44× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.01` | Native C engine | 1.2817× | 1.1836–1.4466× | 0.35× | FASTER |
| calibration | `cal.large.ascii-mode.01` | Rust engine | 0.0788× | 0.0737–0.0870× | 1.11× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.02` | Python engine | 0.0206× | 0.0195–0.0215× | 6.73× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.02` | Native C engine | 1.1983× | 1.1609–1.2236× | 0.50× | FASTER |
| calibration | `cal.large.ascii-mode.02` | Rust engine | 0.0520× | 0.0497–0.0554× | 1.33× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.03` | Python engine | 0.0202× | 0.0199–0.0208× | 7.10× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.03` | Native C engine | 1.2197× | 1.1727–1.2731× | 0.66× | FASTER |
| calibration | `cal.large.ascii-mode.03` | Rust engine | 0.0348× | 0.0342–0.0357× | 1.46× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.04` | Python engine | 0.0208× | 0.0205–0.0213× | 6.32× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.04` | Native C engine | 1.1289× | 1.0557–1.1929× | 0.21× | FASTER |
| calibration | `cal.large.ascii-mode.04` | Rust engine | 0.0960× | 0.0942–0.0984× | 0.93× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.05` | Python engine | 0.0212× | 0.0208–0.0218× | 6.42× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.05` | Native C engine | 1.2136× | 1.1632–1.2632× | 0.35× | FASTER |
| calibration | `cal.large.ascii-mode.05` | Rust engine | 0.0729× | 0.0716–0.0752× | 1.14× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.06` | Python engine | 0.0207× | 0.0200–0.0215× | 6.73× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.06` | Native C engine | 1.2570× | 1.2295–1.2971× | 0.50× | FASTER |
| calibration | `cal.large.ascii-mode.06` | Rust engine | 0.0511× | 0.0496–0.0530× | 1.33× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.07` | Python engine | 0.0203× | 0.0202–0.0204× | 7.04× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.07` | Native C engine | 1.2286× | 1.2212–1.2357× | 0.66× | FASTER |
| calibration | `cal.large.ascii-mode.07` | Rust engine | 0.0317× | 0.0316–0.0319× | 1.55× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.08` | Python engine | 0.0213× | 0.0207–0.0223× | 6.31× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.08` | Native C engine | 1.2113× | 1.1796–1.2721× | 0.21× | FASTER |
| calibration | `cal.large.ascii-mode.08` | Rust engine | 0.0936× | 0.0908–0.0983× | 0.96× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.09` | Python engine | 0.0209× | 0.0205–0.0216× | 6.44× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.09` | Native C engine | 1.1763× | 1.0940–1.2411× | 0.35× | FASTER |
| calibration | `cal.large.ascii-mode.09` | Rust engine | 0.0726× | 0.0706–0.0753× | 1.12× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.10` | Python engine | 0.0209× | 0.0206–0.0212× | 6.71× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.10` | Native C engine | 1.2060× | 1.1487–1.2439× | 0.50× | FASTER |
| calibration | `cal.large.ascii-mode.10` | Rust engine | 0.0491× | 0.0485–0.0498× | 1.36× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.11` | Python engine | 0.0205× | 0.0201–0.0211× | 7.04× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.11` | Native C engine | 1.2546× | 1.2336–1.2887× | 0.66× | FASTER |
| calibration | `cal.large.ascii-mode.11` | Rust engine | 0.0324× | 0.0319–0.0332× | 1.55× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.12` | Python engine | 0.0207× | 0.0205–0.0210× | 6.32× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.12` | Native C engine | 1.1466× | 1.1040–1.1772× | 0.21× | FASTER |
| calibration | `cal.large.ascii-mode.12` | Rust engine | 0.0950× | 0.0938–0.0964× | 0.93× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.13` | Python engine | 0.0208× | 0.0203–0.0214× | 6.44× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.13` | Native C engine | 1.1957× | 1.1446–1.2392× | 0.35× | FASTER |
| calibration | `cal.large.ascii-mode.13` | Rust engine | 0.0731× | 0.0720–0.0749× | 1.12× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.14` | Python engine | 0.0203× | 0.0202–0.0205× | 6.73× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.14` | Native C engine | 1.2161× | 1.2065–1.2239× | 0.50× | FASTER |
| calibration | `cal.large.ascii-mode.14` | Rust engine | 0.0498× | 0.0495–0.0500× | 1.33× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.15` | Python engine | 0.0207× | 0.0203–0.0214× | 7.04× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.15` | Native C engine | 1.2524× | 1.2268–1.2948× | 0.66× | FASTER |
| calibration | `cal.large.ascii-mode.15` | Rust engine | 0.0326× | 0.0320–0.0336× | 1.55× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.16` | Python engine | 0.0214× | 0.0210–0.0221× | 6.31× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.16` | Native C engine | 1.1493× | 1.1164–1.1758× | 0.21× | FASTER |
| calibration | `cal.large.ascii-mode.16` | Rust engine | 0.0906× | 0.0820–0.1002× | 0.96× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.17` | Python engine | 0.0209× | 0.0207–0.0211× | 6.44× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.17` | Native C engine | 1.2170× | 1.2046–1.2308× | 0.35× | FASTER |
| calibration | `cal.large.ascii-mode.17` | Rust engine | 0.0735× | 0.0726–0.0746× | 1.12× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.18` | Python engine | 0.0204× | 0.0201–0.0206× | 6.73× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.18` | Native C engine | 1.2106× | 1.2009–1.2202× | 0.50× | FASTER |
| calibration | `cal.large.ascii-mode.18` | Rust engine | 0.0502× | 0.0498–0.0505× | 1.33× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.19` | Python engine | 0.0202× | 0.0199–0.0205× | 7.04× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.19` | Native C engine | 1.2255× | 1.2181–1.2328× | 0.66× | FASTER |
| calibration | `cal.large.ascii-mode.19` | Rust engine | 0.0320× | 0.0319–0.0322× | 1.55× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.20` | Python engine | 0.0211× | 0.0208–0.0215× | 6.30× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.20` | Native C engine | 1.1890× | 1.1791–1.1986× | 0.21× | FASTER |
| calibration | `cal.large.ascii-mode.20` | Rust engine | 0.0877× | 0.0830–0.0914× | 0.97× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.21` | Python engine | 0.0209× | 0.0207–0.0210× | 6.42× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.21` | Native C engine | 1.2066× | 1.1990–1.2160× | 0.35× | FASTER |
| calibration | `cal.large.ascii-mode.21` | Rust engine | 0.0718× | 0.0714–0.0722× | 1.14× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.22` | Python engine | 0.0201× | 0.0194–0.0209× | 6.78× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.22` | Native C engine | 1.2388× | 1.2133–1.2719× | 0.50× | FASTER |
| calibration | `cal.large.ascii-mode.22` | Rust engine | 0.0554× | 0.0542–0.0572× | 1.27× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.23` | Python engine | 0.0209× | 0.0196–0.0223× | 7.04× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.23` | Native C engine | 1.2469× | 1.1653–1.3104× | 0.66× | FASTER |
| calibration | `cal.large.ascii-mode.23` | Rust engine | 0.0330× | 0.0315–0.0345× | 1.55× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.24` | Python engine | 0.0214× | 0.0202–0.0231× | 6.31× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.24` | Native C engine | 1.2104× | 1.1615–1.2958× | 0.21× | FASTER |
| calibration | `cal.large.ascii-mode.24` | Rust engine | 0.0942× | 0.0910–0.0996× | 0.96× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.25` | Python engine | 0.0220× | 0.0218–0.0221× | 6.42× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.25` | Native C engine | 1.2598× | 1.2474–1.2730× | 0.35× | FASTER |
| calibration | `cal.large.ascii-mode.25` | Rust engine | 0.0751× | 0.0746–0.0757× | 1.14× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.26` | Python engine | 0.0216× | 0.0212–0.0221× | 6.72× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.26` | Native C engine | 1.2626× | 1.2370–1.3034× | 0.50× | FASTER |
| calibration | `cal.large.ascii-mode.26` | Rust engine | 0.0519× | 0.0509–0.0534× | 1.35× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.27` | Python engine | 0.0209× | 0.0208–0.0210× | 7.00× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.27` | Native C engine | 1.2330× | 1.2243–1.2415× | 0.66× | FASTER |
| calibration | `cal.large.ascii-mode.27` | Rust engine | 0.0306× | 0.0305–0.0307× | 1.61× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.28` | Python engine | 0.0213× | 0.0212–0.0214× | 6.30× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.28` | Native C engine | 1.1799× | 1.1669–1.1937× | 0.21× | FASTER |
| calibration | `cal.large.ascii-mode.28` | Rust engine | 0.0923× | 0.0917–0.0930× | 0.96× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.29` | Python engine | 0.0225× | 0.0220–0.0233× | 6.43× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.29` | Native C engine | 1.2855× | 1.2559–1.3253× | 0.35× | FASTER |
| calibration | `cal.large.ascii-mode.29` | Rust engine | 0.0779× | 0.0760–0.0805× | 1.13× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.30` | Python engine | 0.0206× | 0.0204–0.0207× | 6.77× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.30` | Native C engine | 1.2290× | 1.2188–1.2392× | 0.50× | FASTER |
| calibration | `cal.large.ascii-mode.30` | Rust engine | 0.0542× | 0.0538–0.0546× | 1.28× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.31` | Python engine | 0.0207× | 0.0205–0.0208× | 7.03× | SLOWDOWN |
| calibration | `cal.large.ascii-mode.31` | Native C engine | 1.2086× | 1.1623–1.2384× | 0.66× | FASTER |
| calibration | `cal.large.ascii-mode.31` | Rust engine | 0.0313× | 0.0303–0.0319× | 1.57× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.00` | Python engine | 0.0153× | 0.0147–0.0157× | 5.51× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.00` | Native C engine | 1.4601× | 1.4464–1.4746× | 0.08× | FASTER |
| calibration | `cal.large.verbose-dotall.00` | Rust engine | 0.1274× | 0.1256–0.1290× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.01` | Python engine | 0.0074× | 0.0071–0.0075× | 14.89× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.01` | Native C engine | 3.0827× | 3.0635–3.1031× | 0.09× | FASTER |
| calibration | `cal.large.verbose-dotall.01` | Rust engine | 0.1116× | 0.1107–0.1124× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.02` | Python engine | 0.0131× | 0.0130–0.0132× | 5.56× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.02` | Native C engine | 1.8337× | 1.8158–1.8528× | 0.08× | FASTER |
| calibration | `cal.large.verbose-dotall.02` | Rust engine | 0.1551× | 0.1499–0.1592× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.03` | Python engine | 0.0089× | 0.0078–0.0105× | 14.89× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.03` | Native C engine | 3.3141× | 2.8993–3.8549× | 0.09× | FASTER |
| calibration | `cal.large.verbose-dotall.03` | Rust engine | 0.1375× | 0.1229–0.1572× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.04` | Python engine | 0.0165× | 0.0157–0.0178× | 5.51× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.04` | Native C engine | 1.4625× | 1.2647–1.6742× | 0.08× | FASTER |
| calibration | `cal.large.verbose-dotall.04` | Rust engine | 0.1345× | 0.1311–0.1379× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.05` | Python engine | 0.0078× | 0.0074–0.0085× | 14.89× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.05` | Native C engine | 3.2477× | 3.0832–3.5565× | 0.09× | FASTER |
| calibration | `cal.large.verbose-dotall.05` | Rust engine | 0.1195× | 0.1143–0.1299× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.06` | Python engine | 0.0130× | 0.0128–0.0131× | 5.56× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.06` | Native C engine | 1.6990× | 1.5318–1.8061× | 0.08× | FASTER |
| calibration | `cal.large.verbose-dotall.06` | Rust engine | 0.1561× | 0.1521–0.1587× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.07` | Python engine | 0.0079× | 0.0078–0.0080× | 14.89× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.07` | Native C engine | 2.7518× | 2.6934–2.8088× | 0.09× | FASTER |
| calibration | `cal.large.verbose-dotall.07` | Rust engine | 0.1186× | 0.1151–0.1217× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.08` | Python engine | 0.0160× | 0.0154–0.0170× | 5.51× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.08` | Native C engine | 1.5242× | 1.4656–1.6284× | 0.08× | FASTER |
| calibration | `cal.large.verbose-dotall.08` | Rust engine | 0.1341× | 0.1290–0.1435× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.09` | Python engine | 0.0075× | 0.0071–0.0081× | 14.89× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.09` | Native C engine | 3.1832× | 3.0701–3.3624× | 0.09× | FASTER |
| calibration | `cal.large.verbose-dotall.09` | Rust engine | 0.1208× | 0.1146–0.1303× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.10` | Python engine | 0.0129× | 0.0127–0.0130× | 5.56× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.10` | Native C engine | 1.8136× | 1.7878–1.8381× | 0.08× | FASTER |
| calibration | `cal.large.verbose-dotall.10` | Rust engine | 0.1543× | 0.1511–0.1568× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.11` | Python engine | 0.0080× | 0.0079–0.0081× | 14.89× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.11` | Native C engine | 2.8172× | 2.7632–2.8757× | 0.09× | FASTER |
| calibration | `cal.large.verbose-dotall.11` | Rust engine | 0.1150× | 0.1120–0.1174× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.12` | Python engine | 0.0154× | 0.0152–0.0156× | 5.51× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.12` | Native C engine | 1.4887× | 1.4706–1.5082× | 0.08× | FASTER |
| calibration | `cal.large.verbose-dotall.12` | Rust engine | 0.1303× | 0.1293–0.1315× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.13` | Python engine | 0.0075× | 0.0075–0.0075× | 14.89× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.13` | Native C engine | 3.0114× | 2.8017–3.1475× | 0.09× | FASTER |
| calibration | `cal.large.verbose-dotall.13` | Rust engine | 0.1105× | 0.1088–0.1121× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.14` | Python engine | 0.0128× | 0.0126–0.0130× | 5.56× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.14` | Native C engine | 1.8586× | 1.8395–1.8775× | 0.08× | FASTER |
| calibration | `cal.large.verbose-dotall.14` | Rust engine | 0.1550× | 0.1513–0.1574× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.15` | Python engine | 0.0082× | 0.0080–0.0087× | 14.89× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.15` | Native C engine | 2.8216× | 2.7536–2.8918× | 0.09× | FASTER |
| calibration | `cal.large.verbose-dotall.15` | Rust engine | 0.1143× | 0.1078–0.1200× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.16` | Python engine | 0.0158× | 0.0157–0.0160× | 5.51× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.16` | Native C engine | 1.4039× | 1.3870–1.4192× | 0.08× | FASTER |
| calibration | `cal.large.verbose-dotall.16` | Rust engine | 0.1283× | 0.1273–0.1293× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.17` | Python engine | 0.0076× | 0.0075–0.0077× | 14.89× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.17` | Native C engine | 3.1536× | 3.1099–3.2021× | 0.09× | FASTER |
| calibration | `cal.large.verbose-dotall.17` | Rust engine | 0.1130× | 0.1115–0.1149× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.18` | Python engine | 0.0131× | 0.0131–0.0132× | 5.56× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.18` | Native C engine | 1.8429× | 1.8275–1.8586× | 0.08× | FASTER |
| calibration | `cal.large.verbose-dotall.18` | Rust engine | 0.1577× | 0.1560–0.1590× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.19` | Python engine | 0.0082× | 0.0080–0.0083× | 14.89× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.19` | Native C engine | 2.8517× | 2.7874–2.9123× | 0.09× | FASTER |
| calibration | `cal.large.verbose-dotall.19` | Rust engine | 0.1183× | 0.1166–0.1201× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.20` | Python engine | 0.0157× | 0.0155–0.0158× | 5.51× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.20` | Native C engine | 1.4515× | 1.4302–1.4677× | 0.08× | FASTER |
| calibration | `cal.large.verbose-dotall.20` | Rust engine | 0.1248× | 0.1222–0.1272× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.21` | Python engine | 0.0077× | 0.0074–0.0081× | 14.89× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.21` | Native C engine | 3.2279× | 3.1143–3.4106× | 0.09× | FASTER |
| calibration | `cal.large.verbose-dotall.21` | Rust engine | 0.1146× | 0.1106–0.1221× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.22` | Python engine | 0.0133× | 0.0131–0.0135× | 5.56× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.22` | Native C engine | 1.8061× | 1.7841–1.8355× | 0.08× | FASTER |
| calibration | `cal.large.verbose-dotall.22` | Rust engine | 0.1598× | 0.1581–0.1621× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.23` | Python engine | 0.0080× | 0.0079–0.0080× | 14.89× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.23` | Native C engine | 2.8413× | 2.7841–2.8928× | 0.09× | FASTER |
| calibration | `cal.large.verbose-dotall.23` | Rust engine | 0.1222× | 0.1196–0.1240× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.24` | Python engine | 0.0152× | 0.0151–0.0153× | 5.51× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.24` | Native C engine | 1.4801× | 1.4692–1.4910× | 0.08× | FASTER |
| calibration | `cal.large.verbose-dotall.24` | Rust engine | 0.1267× | 0.1223–0.1297× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.25` | Python engine | 0.0073× | 0.0072–0.0074× | 14.89× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.25` | Native C engine | 2.9344× | 2.6763–3.0860× | 0.09× | FASTER |
| calibration | `cal.large.verbose-dotall.25` | Rust engine | 0.1041× | 0.0954–0.1102× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.26` | Python engine | 0.0136× | 0.0126–0.0151× | 5.56× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.26` | Native C engine | 1.9041× | 1.7994–2.0776× | 0.08× | FASTER |
| calibration | `cal.large.verbose-dotall.26` | Rust engine | 0.1585× | 0.1467–0.1784× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.27` | Python engine | 0.0081× | 0.0079–0.0083× | 14.89× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.27` | Native C engine | 2.6844× | 2.3821–2.9127× | 0.09× | FASTER |
| calibration | `cal.large.verbose-dotall.27` | Rust engine | 0.1188× | 0.1147–0.1229× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.28` | Python engine | 0.0153× | 0.0145–0.0163× | 5.51× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.28` | Native C engine | 1.4468× | 1.3774–1.4931× | 0.08× | FASTER |
| calibration | `cal.large.verbose-dotall.28` | Rust engine | 0.1278× | 0.1201–0.1375× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.29` | Python engine | 0.0075× | 0.0074–0.0075× | 14.89× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.29` | Native C engine | 3.1032× | 3.0664–3.1374× | 0.09× | FASTER |
| calibration | `cal.large.verbose-dotall.29` | Rust engine | 0.1102× | 0.1085–0.1117× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.30` | Python engine | 0.0133× | 0.0124–0.0147× | 5.56× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.30` | Native C engine | 1.9734× | 1.8592–2.1937× | 0.08× | FASTER |
| calibration | `cal.large.verbose-dotall.30` | Rust engine | 0.1592× | 0.1493–0.1762× | 0.06× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.31` | Python engine | 0.0083× | 0.0079–0.0088× | 14.89× | SLOWDOWN |
| calibration | `cal.large.verbose-dotall.31` | Native C engine | 2.7023× | 2.3352–3.0518× | 0.09× | FASTER |
| calibration | `cal.large.verbose-dotall.31` | Rust engine | 0.1242× | 0.1156–0.1367× | 0.06× | SLOWDOWN |
| holdout | `hold.large.literal-hit.00` | Python engine | 0.0422× | 0.0393–0.0456× | 20.93× | SLOWDOWN |
| holdout | `hold.large.literal-hit.00` | Native C engine | 1.1577× | 1.0145–1.3120× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.00` | Rust engine | 0.1609× | 0.1483–0.1765× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.01` | Python engine | 0.0427× | 0.0407–0.0455× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.01` | Native C engine | 1.0394× | 0.8683–1.2046× | 0.73× | — |
| holdout | `hold.large.literal-hit.01` | Rust engine | 0.1481× | 0.1406–0.1559× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.02` | Python engine | 0.0491× | 0.0486–0.0496× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.02` | Native C engine | 1.0832× | 1.0709–1.0964× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.02` | Rust engine | 0.1748× | 0.1711–0.1777× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.03` | Python engine | 0.0652× | 0.0636–0.0673× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.03` | Native C engine | 1.1124× | 1.0512–1.1616× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.03` | Rust engine | 0.1621× | 0.1583–0.1672× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.04` | Python engine | 0.0406× | 0.0375–0.0447× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.04` | Native C engine | 1.1483× | 1.0300–1.2753× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.04` | Rust engine | 0.1577× | 0.1475–0.1705× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.05` | Python engine | 0.0409× | 0.0397–0.0418× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.05` | Native C engine | 1.0029× | 0.9247–1.0652× | 0.73× | — |
| holdout | `hold.large.literal-hit.05` | Rust engine | 0.1574× | 0.1536–0.1605× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.06` | Python engine | 0.0457× | 0.0439–0.0472× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.06` | Native C engine | 1.0958× | 0.9877–1.1655× | 0.73× | — |
| holdout | `hold.large.literal-hit.06` | Rust engine | 0.1633× | 0.1511–0.1738× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.07` | Python engine | 0.0575× | 0.0556–0.0594× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.07` | Native C engine | 1.1333× | 1.1147–1.1532× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.07` | Rust engine | 0.2017× | 0.1981–0.2057× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.08` | Python engine | 0.0384× | 0.0368–0.0409× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.08` | Native C engine | 1.1476× | 1.1114–1.2109× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.08` | Rust engine | 0.1553× | 0.1500–0.1635× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.09` | Python engine | 0.0423× | 0.0419–0.0427× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.09` | Native C engine | 1.0659× | 1.0549–1.0766× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.09` | Rust engine | 0.1561× | 0.1522–0.1586× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.10` | Python engine | 0.0465× | 0.0454–0.0473× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.10` | Native C engine | 1.0760× | 0.9549–1.1469× | 0.73× | — |
| holdout | `hold.large.literal-hit.10` | Rust engine | 0.1707× | 0.1667–0.1737× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.11` | Python engine | 0.0609× | 0.0579–0.0632× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.11` | Native C engine | 1.2336× | 1.1978–1.2723× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.11` | Rust engine | 0.1581× | 0.1543–0.1621× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.12` | Python engine | 0.0380× | 0.0356–0.0408× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.12` | Native C engine | 1.1206× | 1.0098–1.2356× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.12` | Rust engine | 0.1549× | 0.1480–0.1657× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.13` | Python engine | 0.0407× | 0.0395–0.0421× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.13` | Native C engine | 1.1422× | 1.1155–1.1728× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.13` | Rust engine | 0.1524× | 0.1438–0.1601× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.14` | Python engine | 0.0465× | 0.0454–0.0475× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.14` | Native C engine | 1.1487× | 1.1320–1.1660× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.14` | Rust engine | 0.1740× | 0.1717–0.1766× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.15` | Python engine | 0.0571× | 0.0557–0.0583× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.15` | Native C engine | 1.1188× | 1.0179–1.1830× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.15` | Rust engine | 0.1991× | 0.1946–0.2033× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.16` | Python engine | 0.0403× | 0.0379–0.0442× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.16` | Native C engine | 1.1429× | 1.0839–1.2547× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.16` | Rust engine | 0.1535× | 0.1434–0.1699× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.17` | Python engine | 0.0407× | 0.0400–0.0414× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.17` | Native C engine | 1.1614× | 1.1510–1.1720× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.17` | Rust engine | 0.1589× | 0.1572–0.1606× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.18` | Python engine | 0.0479× | 0.0475–0.0485× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.18` | Native C engine | 1.1682× | 1.1460–1.1858× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.18` | Rust engine | 0.1480× | 0.1411–0.1522× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.19` | Python engine | 0.0602× | 0.0594–0.0613× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.19` | Native C engine | 1.1657× | 1.1462–1.1852× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.19` | Rust engine | 0.2008× | 0.1976–0.2040× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.20` | Python engine | 0.0387× | 0.0382–0.0391× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.20` | Native C engine | 1.1202× | 1.1012–1.1360× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.20` | Rust engine | 0.1491× | 0.1454–0.1525× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.21` | Python engine | 0.0413× | 0.0409–0.0419× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.21` | Native C engine | 1.1437× | 1.1299–1.1589× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.21` | Rust engine | 0.1569× | 0.1556–0.1586× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.22` | Python engine | 0.0460× | 0.0447–0.0474× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.22` | Native C engine | 1.1427× | 1.1162–1.1708× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.22` | Rust engine | 0.1748× | 0.1719–0.1787× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.23` | Python engine | 0.0572× | 0.0547–0.0593× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.23` | Native C engine | 1.1435× | 1.0993–1.1890× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.23` | Rust engine | 0.1977× | 0.1928–0.2028× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.24` | Python engine | 0.0394× | 0.0378–0.0422× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.24` | Native C engine | 1.1412× | 1.1007–1.2185× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.24` | Rust engine | 0.1536× | 0.1433–0.1670× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.25` | Python engine | 0.0419× | 0.0414–0.0423× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.25` | Native C engine | 1.0606× | 1.0468–1.0731× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.25` | Rust engine | 0.1600× | 0.1583–0.1618× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.26` | Python engine | 0.0493× | 0.0470–0.0510× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.26` | Native C engine | 1.1577× | 1.1465–1.1691× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.26` | Rust engine | 0.1519× | 0.1507–0.1531× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.27` | Python engine | 0.0611× | 0.0602–0.0620× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.27` | Native C engine | 1.0522× | 0.9299–1.1306× | 0.73× | — |
| holdout | `hold.large.literal-hit.27` | Rust engine | 0.1629× | 0.1610–0.1650× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.28` | Python engine | 0.0386× | 0.0368–0.0418× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.28` | Native C engine | 1.1480× | 1.0768–1.2534× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.28` | Rust engine | 0.1496× | 0.1436–0.1611× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.29` | Python engine | 0.0400× | 0.0395–0.0405× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.29` | Native C engine | 0.9534× | 0.6932–1.1256× | 0.73× | — |
| holdout | `hold.large.literal-hit.29` | Rust engine | 0.1608× | 0.1598–0.1620× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.30` | Python engine | 0.0460× | 0.0443–0.0484× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.30` | Native C engine | 1.2617× | 1.2279–1.3212× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.30` | Rust engine | 0.1755× | 0.1705–0.1828× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-hit.31` | Python engine | 0.0561× | 0.0553–0.0570× | 21.47× | SLOWDOWN |
| holdout | `hold.large.literal-hit.31` | Native C engine | 1.2808× | 1.2041–1.3293× | 0.73× | FASTER |
| holdout | `hold.large.literal-hit.31` | Rust engine | 0.2005× | 0.1954–0.2049× | 0.67× | SLOWDOWN |
| holdout | `hold.large.literal-miss.00` | Python engine | 0.1494× | 0.1489–0.1499× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.00` | Native C engine | 1.1855× | 1.1807–1.1904× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.00` | Rust engine | 0.1878× | 0.1868–0.1889× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.01` | Python engine | 0.1729× | 0.1712–0.1751× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.01` | Native C engine | 1.3315× | 1.3129–1.3498× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.01` | Rust engine | 0.1623× | 0.1610–0.1637× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.02` | Python engine | 0.2018× | 0.1999–0.2033× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.02` | Native C engine | 1.4563× | 1.4430–1.4715× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.02` | Rust engine | 0.2227× | 0.2205–0.2249× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.03` | Python engine | 0.2304× | 0.1859–0.2584× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.03` | Native C engine | 1.1882× | 1.1614–1.2109× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.03` | Rust engine | 0.2577× | 0.2473–0.2644× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.04` | Python engine | 0.1526× | 0.1493–0.1549× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.04` | Native C engine | 1.2242× | 1.2174–1.2302× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.04` | Rust engine | 0.1896× | 0.1887–0.1906× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.05` | Python engine | 0.1666× | 0.1553–0.1735× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.05` | Native C engine | 1.3277× | 1.3199–1.3356× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.05` | Rust engine | 0.2012× | 0.1947–0.2054× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.06` | Python engine | 0.2083× | 0.1993–0.2139× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.06` | Native C engine | 1.5534× | 1.5427–1.5660× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.06` | Rust engine | 0.2294× | 0.2265–0.2319× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.07` | Python engine | 0.2709× | 0.2671–0.2755× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.07` | Native C engine | 1.2614× | 1.2402–1.2866× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.07` | Rust engine | 0.1557× | 0.1537–0.1582× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.08` | Python engine | 0.1539× | 0.1530–0.1553× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.08` | Native C engine | 1.2119× | 1.2043–1.2240× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.08` | Rust engine | 0.1657× | 0.1635–0.1680× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.09` | Python engine | 0.1731× | 0.1713–0.1747× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.09` | Native C engine | 1.3492× | 1.3343–1.3603× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.09` | Rust engine | 0.2041× | 0.2029–0.2054× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.10` | Python engine | 0.2123× | 0.2107–0.2140× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.10` | Native C engine | 1.5127× | 1.4931–1.5324× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.10` | Rust engine | 0.2305× | 0.2285–0.2325× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.11` | Python engine | 0.2660× | 0.2631–0.2691× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.11` | Native C engine | 1.6139× | 1.5804–1.6426× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.11` | Rust engine | 0.2521× | 0.2339–0.2633× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.12` | Python engine | 0.1520× | 0.1509–0.1533× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.12` | Native C engine | 1.1485× | 1.0604–1.2012× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.12` | Rust engine | 0.1847× | 0.1791–0.1887× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.13` | Python engine | 0.1732× | 0.1718–0.1747× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.13` | Native C engine | 1.2567× | 1.2452–1.2700× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.13` | Rust engine | 0.1659× | 0.1645–0.1676× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.14` | Python engine | 0.1988× | 0.1966–0.2012× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.14` | Native C engine | 1.2120× | 1.1963–1.2287× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.14` | Rust engine | 0.2281× | 0.2263–0.2298× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.15` | Python engine | 0.2552× | 0.2498–0.2602× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.15` | Native C engine | 1.2045× | 1.1897–1.2214× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.15` | Rust engine | 0.2664× | 0.2627–0.2704× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.16` | Python engine | 0.1521× | 0.1495–0.1539× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.16` | Native C engine | 1.2018× | 1.1968–1.2066× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.16` | Rust engine | 0.1906× | 0.1873–0.1930× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.17` | Python engine | 0.1683× | 0.1672–0.1693× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.17` | Native C engine | 1.2240× | 1.2115–1.2338× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.17` | Rust engine | 0.1994× | 0.1963–0.2019× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.18` | Python engine | 0.2022× | 0.2007–0.2037× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.18` | Native C engine | 1.0089× | 0.8777–1.0851× | 0.00× | — |
| holdout | `hold.large.literal-miss.18` | Rust engine | 0.2313× | 0.2303–0.2324× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.19` | Python engine | 0.2714× | 0.2674–0.2742× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.19` | Native C engine | 1.2504× | 1.1796–1.2940× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.19` | Rust engine | 0.1554× | 0.1540–0.1566× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.20` | Python engine | 0.1533× | 0.1523–0.1542× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.20` | Native C engine | 1.1297× | 0.9670–1.2347× | 0.00× | — |
| holdout | `hold.large.literal-miss.20` | Rust engine | 0.1878× | 0.1870–0.1886× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.21` | Python engine | 0.1687× | 0.1662–0.1718× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.21` | Native C engine | 1.2265× | 1.2104–1.2461× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.21` | Rust engine | 0.1926× | 0.1741–0.2045× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.22` | Python engine | 0.2127× | 0.2110–0.2148× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.22` | Native C engine | 1.4416× | 1.4287–1.4569× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.22` | Rust engine | 0.2312× | 0.2292–0.2333× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.23` | Python engine | 0.2413× | 0.2202–0.2545× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.23` | Native C engine | 1.1851× | 1.1752–1.1949× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.23` | Rust engine | 0.2659× | 0.2640–0.2676× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.24` | Python engine | 0.1538× | 0.1531–0.1544× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.24` | Native C engine | 1.1894× | 1.1825–1.1969× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.24` | Rust engine | 0.1651× | 0.1642–0.1661× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.25` | Python engine | 0.1725× | 0.1716–0.1734× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.25` | Native C engine | 1.2542× | 1.2445–1.2627× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.25` | Rust engine | 0.1584× | 0.1500–0.1635× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.26` | Python engine | 0.2039× | 0.2020–0.2057× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.26` | Native C engine | 1.5182× | 1.5068–1.5328× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.26` | Rust engine | 0.2226× | 0.2215–0.2237× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.27` | Python engine | 0.2808× | 0.2759–0.2854× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.27` | Native C engine | 1.4399× | 1.4217–1.4576× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.27` | Rust engine | 0.2703× | 0.2673–0.2734× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.28` | Python engine | 0.1508× | 0.1500–0.1515× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.28` | Native C engine | 1.1718× | 1.1589–1.1820× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.28` | Rust engine | 0.1873× | 0.1863–0.1882× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.29` | Python engine | 0.1753× | 0.1742–0.1765× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.29` | Native C engine | 1.2667× | 1.2607–1.2736× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.29` | Rust engine | 0.1618× | 0.1582–0.1641× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.30` | Python engine | 0.2106× | 0.2064–0.2133× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.30` | Native C engine | 1.2463× | 1.2367–1.2557× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.30` | Rust engine | 0.1522× | 0.1384–0.1599× | 0.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.31` | Python engine | 0.2648× | 0.2587–0.2736× | 112.00× | SLOWDOWN |
| holdout | `hold.large.literal-miss.31` | Native C engine | 1.2529× | 1.2254–1.2900× | 0.00× | FASTER |
| holdout | `hold.large.literal-miss.31` | Rust engine | 0.2738× | 0.2679–0.2827× | 0.00× | SLOWDOWN |
| holdout | `hold.large.long-ending.00` | Python engine | 0.0488× | 0.0470–0.0501× | 2.95× | SLOWDOWN |
| holdout | `hold.large.long-ending.00` | Native C engine | 1.4844× | 1.4645–1.5007× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.00` | Rust engine | 0.2062× | 0.2034–0.2087× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.01` | Python engine | 0.0505× | 0.0499–0.0515× | 2.90× | SLOWDOWN |
| holdout | `hold.large.long-ending.01` | Native C engine | 1.4894× | 1.4732–1.5116× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.01` | Rust engine | 0.2054× | 0.1998–0.2117× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.02` | Python engine | 0.0490× | 0.0476–0.0500× | 2.95× | SLOWDOWN |
| holdout | `hold.large.long-ending.02` | Native C engine | 1.4886× | 1.4793–1.4997× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.02` | Rust engine | 0.1981× | 0.1828–0.2069× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.03` | Python engine | 0.0494× | 0.0488–0.0499× | 2.90× | SLOWDOWN |
| holdout | `hold.large.long-ending.03` | Native C engine | 1.4717× | 1.4624–1.4791× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.03` | Rust engine | 0.2027× | 0.1994–0.2049× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.04` | Python engine | 0.0632× | 0.0627–0.0637× | 2.95× | SLOWDOWN |
| holdout | `hold.large.long-ending.04` | Native C engine | 1.8253× | 1.8087–1.8413× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.04` | Rust engine | 0.2246× | 0.2229–0.2261× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.05` | Python engine | 0.0656× | 0.0618–0.0721× | 2.95× | SLOWDOWN |
| holdout | `hold.large.long-ending.05` | Native C engine | 1.8987× | 1.8038–2.0782× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.05` | Rust engine | 0.2347× | 0.2236–0.2569× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.06` | Python engine | 0.0641× | 0.0635–0.0647× | 2.95× | SLOWDOWN |
| holdout | `hold.large.long-ending.06` | Native C engine | 1.8193× | 1.7957–1.8450× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.06` | Rust engine | 0.2296× | 0.2276–0.2321× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.07` | Python engine | 0.0634× | 0.0629–0.0639× | 2.95× | SLOWDOWN |
| holdout | `hold.large.long-ending.07` | Native C engine | 1.8168× | 1.8003–1.8318× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.07` | Rust engine | 0.2241× | 0.2169–0.2286× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.08` | Python engine | 0.1050× | 0.1027–0.1072× | 2.98× | SLOWDOWN |
| holdout | `hold.large.long-ending.08` | Native C engine | 2.8590× | 2.7865–2.9412× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.08` | Rust engine | 0.2664× | 0.2619–0.2716× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.09` | Python engine | 0.1066× | 0.1050–0.1081× | 2.98× | SLOWDOWN |
| holdout | `hold.large.long-ending.09` | Native C engine | 2.8233× | 2.7781–2.8677× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.09` | Rust engine | 0.2544× | 0.2310–0.2689× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.10` | Python engine | 0.1029× | 0.0991–0.1056× | 2.98× | SLOWDOWN |
| holdout | `hold.large.long-ending.10` | Native C engine | 2.7410× | 2.6862–2.7954× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.10` | Rust engine | 0.2599× | 0.2563–0.2636× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.11` | Python engine | 0.1024× | 0.0999–0.1050× | 2.98× | SLOWDOWN |
| holdout | `hold.large.long-ending.11` | Native C engine | 2.7130× | 2.6301–2.7869× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.11` | Rust engine | 0.2587× | 0.2537–0.2637× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.12` | Python engine | 0.2036× | 0.1888–0.2233× | 2.98× | SLOWDOWN |
| holdout | `hold.large.long-ending.12` | Native C engine | 4.2622× | 3.9258–4.6857× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.12` | Rust engine | 0.3016× | 0.2887–0.3209× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.13` | Python engine | 0.1936× | 0.1880–0.1995× | 2.95× | SLOWDOWN |
| holdout | `hold.large.long-ending.13` | Native C engine | 4.0777× | 3.8770–4.2687× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.13` | Rust engine | 0.2873× | 0.2782–0.2959× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.14` | Python engine | 0.1980× | 0.1920–0.2044× | 2.98× | SLOWDOWN |
| holdout | `hold.large.long-ending.14` | Native C engine | 4.3161× | 4.1548–4.4793× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.14` | Rust engine | 0.2918× | 0.2692–0.3073× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.15` | Python engine | 0.2003× | 0.1877–0.2234× | 2.90× | SLOWDOWN |
| holdout | `hold.large.long-ending.15` | Native C engine | 4.3778× | 4.1268–4.8170× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.15` | Rust engine | 0.2934× | 0.2736–0.3268× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.16` | Python engine | 0.0488× | 0.0474–0.0502× | 2.95× | SLOWDOWN |
| holdout | `hold.large.long-ending.16` | Native C engine | 1.4887× | 1.4745–1.5071× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.16` | Rust engine | 0.2072× | 0.2050–0.2100× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.17` | Python engine | 0.0492× | 0.0471–0.0507× | 2.90× | SLOWDOWN |
| holdout | `hold.large.long-ending.17` | Native C engine | 1.4972× | 1.4841–1.5131× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.17` | Rust engine | 0.2084× | 0.2060–0.2115× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.18` | Python engine | 0.0498× | 0.0491–0.0503× | 2.95× | SLOWDOWN |
| holdout | `hold.large.long-ending.18` | Native C engine | 1.4953× | 1.4884–1.5021× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.18` | Rust engine | 0.2056× | 0.2028–0.2077× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.19` | Python engine | 0.0498× | 0.0495–0.0502× | 2.90× | SLOWDOWN |
| holdout | `hold.large.long-ending.19` | Native C engine | 1.4894× | 1.4786–1.5010× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.19` | Rust engine | 0.2068× | 0.2055–0.2082× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.20` | Python engine | 0.0629× | 0.0621–0.0637× | 2.95× | SLOWDOWN |
| holdout | `hold.large.long-ending.20` | Native C engine | 1.6340× | 1.3371–1.8236× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.20` | Rust engine | 0.2262× | 0.2240–0.2284× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.21` | Python engine | 0.0632× | 0.0623–0.0637× | 2.95× | SLOWDOWN |
| holdout | `hold.large.long-ending.21` | Native C engine | 1.6942× | 1.4645–1.8301× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.21` | Rust engine | 0.2220× | 0.2131–0.2276× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.22` | Python engine | 0.0682× | 0.0636–0.0763× | 2.95× | SLOWDOWN |
| holdout | `hold.large.long-ending.22` | Native C engine | 1.9606× | 1.8345–2.2001× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.22` | Rust engine | 0.2389× | 0.2203–0.2700× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.23` | Python engine | 0.0633× | 0.0626–0.0639× | 2.95× | SLOWDOWN |
| holdout | `hold.large.long-ending.23` | Native C engine | 1.8377× | 1.8262–1.8479× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.23` | Rust engine | 0.2270× | 0.2251–0.2291× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.24` | Python engine | 0.1043× | 0.1013–0.1074× | 2.98× | SLOWDOWN |
| holdout | `hold.large.long-ending.24` | Native C engine | 2.7282× | 2.6321–2.8200× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.24` | Rust engine | 0.2598× | 0.2512–0.2689× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.25` | Python engine | 0.1039× | 0.1005–0.1070× | 2.98× | SLOWDOWN |
| holdout | `hold.large.long-ending.25` | Native C engine | 2.7140× | 2.6313–2.7858× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.25` | Rust engine | 0.2640× | 0.2580–0.2697× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.26` | Python engine | 0.1018× | 0.0982–0.1051× | 2.98× | SLOWDOWN |
| holdout | `hold.large.long-ending.26` | Native C engine | 2.7942× | 2.7375–2.8496× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.26` | Rust engine | 0.2637× | 0.2585–0.2690× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.27` | Python engine | 0.1038× | 0.1004–0.1070× | 2.98× | SLOWDOWN |
| holdout | `hold.large.long-ending.27` | Native C engine | 2.7210× | 2.6445–2.7987× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.27` | Rust engine | 0.2633× | 0.2566–0.2699× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.28` | Python engine | 0.2016× | 0.1910–0.2162× | 2.98× | SLOWDOWN |
| holdout | `hold.large.long-ending.28` | Native C engine | 4.2661× | 4.0623–4.5439× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.28` | Rust engine | 0.2994× | 0.2863–0.3175× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.29` | Python engine | 0.1871× | 0.1769–0.1946× | 2.95× | SLOWDOWN |
| holdout | `hold.large.long-ending.29` | Native C engine | 4.0155× | 3.8505–4.1804× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.29` | Rust engine | 0.2860× | 0.2807–0.2922× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.30` | Python engine | 0.1848× | 0.1704–0.1971× | 2.98× | SLOWDOWN |
| holdout | `hold.large.long-ending.30` | Native C engine | 3.9950× | 3.7779–4.2338× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.30` | Rust engine | 0.2936× | 0.2863–0.3007× | 0.07× | SLOWDOWN |
| holdout | `hold.large.long-ending.31` | Python engine | 0.1928× | 0.1851–0.2003× | 2.95× | SLOWDOWN |
| holdout | `hold.large.long-ending.31` | Native C engine | 3.9201× | 3.7226–4.1255× | 0.07× | FASTER |
| holdout | `hold.large.long-ending.31` | Rust engine | 0.2849× | 0.2755–0.2950× | 0.07× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.00` | Python engine | 0.0230× | 0.0222–0.0236× | 7.08× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.00` | Native C engine | 1.2283× | 1.1270–1.2887× | 0.07× | FASTER |
| holdout | `hold.large.formatted-lines.00` | Rust engine | 0.3114× | 0.3038–0.3181× | 1.20× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.01` | Python engine | 0.0225× | 0.0218–0.0236× | 7.29× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.01` | Native C engine | 1.4004× | 1.3531–1.4932× | 0.11× | FASTER |
| holdout | `hold.large.formatted-lines.01` | Rust engine | 0.3878× | 0.3734–0.4129× | 2.21× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.02` | Python engine | 0.0214× | 0.0211–0.0218× | 7.24× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.02` | Native C engine | 1.4617× | 1.4377–1.4852× | 0.18× | FASTER |
| holdout | `hold.large.formatted-lines.02` | Rust engine | 0.4289× | 0.4223–0.4361× | 4.01× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.03` | Python engine | 0.0206× | 0.0203–0.0208× | 7.04× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.03` | Native C engine | 1.4775× | 1.4625–1.4920× | 0.30× | FASTER |
| holdout | `hold.large.formatted-lines.03` | Rust engine | 0.4571× | 0.4324–0.4727× | 6.74× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.04` | Python engine | 0.0245× | 0.0235–0.0264× | 7.03× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.04` | Native C engine | 1.3394× | 1.2812–1.4497× | 0.07× | FASTER |
| holdout | `hold.large.formatted-lines.04` | Rust engine | 0.3332× | 0.3201–0.3583× | 1.20× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.05` | Python engine | 0.0232× | 0.0220–0.0256× | 7.28× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.05` | Native C engine | 1.4519× | 1.3772–1.5827× | 0.11× | FASTER |
| holdout | `hold.large.formatted-lines.05` | Rust engine | 0.3862× | 0.3749–0.4031× | 2.29× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.06` | Python engine | 0.0211× | 0.0208–0.0213× | 7.24× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.06` | Native C engine | 1.4571× | 1.4422–1.4710× | 0.18× | FASTER |
| holdout | `hold.large.formatted-lines.06` | Rust engine | 0.4190× | 0.3995–0.4313× | 4.01× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.07` | Python engine | 0.0218× | 0.0208–0.0236× | 7.04× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.07` | Native C engine | 1.5306× | 1.4580–1.6662× | 0.30× | FASTER |
| holdout | `hold.large.formatted-lines.07` | Rust engine | 0.4901× | 0.4670–0.5346× | 6.74× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.08` | Python engine | 0.0235× | 0.0233–0.0237× | 7.02× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.08` | Native C engine | 1.2351× | 1.1654–1.2812× | 0.07× | FASTER |
| holdout | `hold.large.formatted-lines.08` | Rust engine | 0.3135× | 0.3050–0.3184× | 1.24× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.09` | Python engine | 0.0218× | 0.0213–0.0222× | 7.29× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.09` | Native C engine | 1.3624× | 1.3509–1.3744× | 0.11× | FASTER |
| holdout | `hold.large.formatted-lines.09` | Rust engine | 0.3567× | 0.3301–0.3781× | 2.21× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.10` | Python engine | 0.0214× | 0.0210–0.0219× | 7.24× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.10` | Native C engine | 1.3645× | 1.1933–1.4710× | 0.18× | FASTER |
| holdout | `hold.large.formatted-lines.10` | Rust engine | 0.4188× | 0.3994–0.4345× | 4.01× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.11` | Python engine | 0.0214× | 0.0205–0.0232× | 7.04× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.11` | Native C engine | 1.5165× | 1.4512–1.6424× | 0.30× | FASTER |
| holdout | `hold.large.formatted-lines.11` | Rust engine | 0.4815× | 0.4615–0.5208× | 6.74× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.12` | Python engine | 0.0245× | 0.0238–0.0257× | 7.03× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.12` | Native C engine | 1.3244× | 1.2879–1.3871× | 0.07× | FASTER |
| holdout | `hold.large.formatted-lines.12` | Rust engine | 0.3259× | 0.3159–0.3424× | 1.20× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.13` | Python engine | 0.0222× | 0.0220–0.0224× | 7.28× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.13` | Native C engine | 1.3255× | 1.2130–1.4024× | 0.11× | FASTER |
| holdout | `hold.large.formatted-lines.13` | Rust engine | 0.3763× | 0.3622–0.3849× | 2.29× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.14` | Python engine | 0.0212× | 0.0210–0.0213× | 7.24× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.14` | Native C engine | 1.4453× | 1.4320–1.4594× | 0.18× | FASTER |
| holdout | `hold.large.formatted-lines.14` | Rust engine | 0.4293× | 0.4261–0.4326× | 4.01× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.15` | Python engine | 0.0208× | 0.0207–0.0210× | 7.04× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.15` | Native C engine | 1.4911× | 1.4804–1.5021× | 0.30× | FASTER |
| holdout | `hold.large.formatted-lines.15` | Rust engine | 0.4596× | 0.4457–0.4692× | 6.74× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.16` | Python engine | 0.0239× | 0.0236–0.0243× | 7.02× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.16` | Native C engine | 1.2956× | 1.2758–1.3238× | 0.07× | FASTER |
| holdout | `hold.large.formatted-lines.16` | Rust engine | 0.3182× | 0.3139–0.3246× | 1.24× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.17` | Python engine | 0.0226× | 0.0217–0.0240× | 7.28× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.17` | Native C engine | 1.4169× | 1.3724–1.5006× | 0.11× | FASTER |
| holdout | `hold.large.formatted-lines.17` | Rust engine | 0.3851× | 0.3755–0.4034× | 2.29× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.18` | Python engine | 0.0215× | 0.0213–0.0217× | 7.22× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.18` | Native C engine | 1.4055× | 1.2924–1.4738× | 0.18× | FASTER |
| holdout | `hold.large.formatted-lines.18` | Rust engine | 0.4196× | 0.4081–0.4276× | 4.14× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.19` | Python engine | 0.0208× | 0.0203–0.0211× | 7.04× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.19` | Native C engine | 1.4859× | 1.4711–1.5007× | 0.30× | FASTER |
| holdout | `hold.large.formatted-lines.19` | Rust engine | 0.4728× | 0.4682–0.4770× | 6.74× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.20` | Python engine | 0.0240× | 0.0237–0.0242× | 7.03× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.20` | Native C engine | 1.2178× | 1.1339–1.2734× | 0.07× | FASTER |
| holdout | `hold.large.formatted-lines.20` | Rust engine | 0.3162× | 0.3131–0.3191× | 1.20× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.21` | Python engine | 0.0222× | 0.0221–0.0223× | 7.29× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.21` | Native C engine | 1.3779× | 1.3691–1.3862× | 0.11× | FASTER |
| holdout | `hold.large.formatted-lines.21` | Rust engine | 0.3805× | 0.3777–0.3831× | 2.21× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.22` | Python engine | 0.0216× | 0.0214–0.0218× | 7.22× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.22` | Native C engine | 1.3806× | 1.2222–1.4715× | 0.18× | FASTER |
| holdout | `hold.large.formatted-lines.22` | Rust engine | 0.4261× | 0.4221–0.4297× | 4.14× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.23` | Python engine | 0.0211× | 0.0210–0.0212× | 7.04× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.23` | Native C engine | 1.4357× | 1.3152–1.5064× | 0.30× | FASTER |
| holdout | `hold.large.formatted-lines.23` | Rust engine | 0.4751× | 0.4727–0.4775× | 6.74× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.24` | Python engine | 0.0241× | 0.0237–0.0244× | 7.03× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.24` | Native C engine | 1.2604× | 1.1983–1.2964× | 0.07× | FASTER |
| holdout | `hold.large.formatted-lines.24` | Rust engine | 0.3204× | 0.3173–0.3238× | 1.20× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.25` | Python engine | 0.0241× | 0.0227–0.0261× | 7.29× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.25` | Native C engine | 1.4195× | 1.3432–1.5520× | 0.11× | FASTER |
| holdout | `hold.large.formatted-lines.25` | Rust engine | 0.4066× | 0.3841–0.4425× | 2.21× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.26` | Python engine | 0.0237× | 0.0219–0.0262× | 7.24× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.26` | Native C engine | 1.3202× | 1.1274–1.5229× | 0.18× | FASTER |
| holdout | `hold.large.formatted-lines.26` | Rust engine | 0.4542× | 0.4296–0.4967× | 4.01× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.27` | Python engine | 0.0207× | 0.0204–0.0210× | 7.04× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.27` | Native C engine | 1.3717× | 1.2102–1.4955× | 0.30× | FASTER |
| holdout | `hold.large.formatted-lines.27` | Rust engine | 0.4606× | 0.4382–0.4739× | 6.74× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.28` | Python engine | 0.0249× | 0.0237–0.0264× | 7.03× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.28` | Native C engine | 1.3611× | 1.2877–1.4658× | 0.07× | FASTER |
| holdout | `hold.large.formatted-lines.28` | Rust engine | 0.3389× | 0.3221–0.3636× | 1.20× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.29` | Python engine | 0.0226× | 0.0209–0.0253× | 7.29× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.29` | Native C engine | 1.3488× | 1.1787–1.5510× | 0.11× | FASTER |
| holdout | `hold.large.formatted-lines.29` | Rust engine | 0.3915× | 0.3739–0.4163× | 2.21× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.30` | Python engine | 0.0212× | 0.0210–0.0215× | 7.22× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.30` | Native C engine | 1.4516× | 1.4378–1.4664× | 0.18× | FASTER |
| holdout | `hold.large.formatted-lines.30` | Rust engine | 0.4241× | 0.4206–0.4276× | 4.14× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.31` | Python engine | 0.0208× | 0.0205–0.0211× | 7.04× | SLOWDOWN |
| holdout | `hold.large.formatted-lines.31` | Native C engine | 1.4832× | 1.4671–1.5008× | 0.30× | FASTER |
| holdout | `hold.large.formatted-lines.31` | Rust engine | 0.4634× | 0.4489–0.4738× | 6.74× | SLOWDOWN |
| holdout | `hold.large.prefix-check.00` | Python engine | 0.0277× | 0.0262–0.0296× | 4.26× | SLOWDOWN |
| holdout | `hold.large.prefix-check.00` | Native C engine | 1.5071× | 1.4607–1.5917× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.00` | Rust engine | 0.1785× | 0.1727–0.1889× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.01` | Python engine | 0.0285× | 0.0283–0.0287× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.01` | Native C engine | 1.4550× | 1.4424–1.4674× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.01` | Rust engine | 0.1740× | 0.1665–0.1786× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.02` | Python engine | 0.0296× | 0.0289–0.0301× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.02` | Native C engine | 1.4217× | 1.4001–1.4419× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.02` | Rust engine | 0.1853× | 0.1823–0.1877× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.03` | Python engine | 0.0625× | 0.0589–0.0652× | 2.64× | SLOWDOWN |
| holdout | `hold.large.prefix-check.03` | Native C engine | 1.3770× | 1.3379–1.4231× | 0.00× | FASTER |
| holdout | `hold.large.prefix-check.03` | Rust engine | 0.2381× | 0.2329–0.2443× | 0.00× | SLOWDOWN |
| holdout | `hold.large.prefix-check.04` | Python engine | 0.0263× | 0.0259–0.0266× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.04` | Native C engine | 1.4756× | 1.4659–1.4868× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.04` | Rust engine | 0.1707× | 0.1693–0.1720× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.05` | Python engine | 0.0267× | 0.0264–0.0270× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.05` | Native C engine | 1.4564× | 1.4451–1.4689× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.05` | Rust engine | 0.1698× | 0.1685–0.1711× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.06` | Python engine | 0.0284× | 0.0280–0.0287× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.06` | Native C engine | 1.4425× | 1.4261–1.4582× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.06` | Rust engine | 0.1781× | 0.1723–0.1826× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.07` | Python engine | 0.0621× | 0.0590–0.0641× | 2.64× | SLOWDOWN |
| holdout | `hold.large.prefix-check.07` | Native C engine | 1.3461× | 1.3260–1.3655× | 0.00× | FASTER |
| holdout | `hold.large.prefix-check.07` | Rust engine | 0.2333× | 0.2281–0.2384× | 0.00× | SLOWDOWN |
| holdout | `hold.large.prefix-check.08` | Python engine | 0.0269× | 0.0261–0.0282× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.08` | Native C engine | 1.5096× | 1.4703–1.5826× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.08` | Rust engine | 0.1752× | 0.1700–0.1840× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.09` | Python engine | 0.0269× | 0.0263–0.0274× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.09` | Native C engine | 1.4599× | 1.4447–1.4743× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.09` | Rust engine | 0.1741× | 0.1709–0.1762× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.10` | Python engine | 0.0278× | 0.0273–0.0283× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.10` | Native C engine | 1.4378× | 1.4172–1.4545× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.10` | Rust engine | 0.1788× | 0.1764–0.1814× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.11` | Python engine | 0.0622× | 0.0604–0.0640× | 2.64× | SLOWDOWN |
| holdout | `hold.large.prefix-check.11` | Native C engine | 1.3292× | 1.3136–1.3480× | 0.00× | FASTER |
| holdout | `hold.large.prefix-check.11` | Rust engine | 0.2303× | 0.2269–0.2345× | 0.00× | SLOWDOWN |
| holdout | `hold.large.prefix-check.12` | Python engine | 0.0263× | 0.0256–0.0273× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.12` | Native C engine | 1.4352× | 1.3491–1.4864× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.12` | Rust engine | 0.1587× | 0.1450–0.1676× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.13` | Python engine | 0.0266× | 0.0263–0.0269× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.13` | Native C engine | 1.4292× | 1.3517–1.4757× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.13` | Rust engine | 0.1667× | 0.1609–0.1711× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.14` | Python engine | 0.0276× | 0.0271–0.0281× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.14` | Native C engine | 1.4441× | 1.4231–1.4636× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.14` | Rust engine | 0.1772× | 0.1757–0.1783× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.15` | Python engine | 0.0635× | 0.0609–0.0656× | 2.64× | SLOWDOWN |
| holdout | `hold.large.prefix-check.15` | Native C engine | 1.3265× | 1.2509–1.3905× | 0.00× | FASTER |
| holdout | `hold.large.prefix-check.15` | Rust engine | 0.2273× | 0.2078–0.2399× | 0.00× | SLOWDOWN |
| holdout | `hold.large.prefix-check.16` | Python engine | 0.0264× | 0.0261–0.0267× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.16` | Native C engine | 1.4388× | 1.4062–1.4674× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.16` | Rust engine | 0.1688× | 0.1655–0.1715× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.17` | Python engine | 0.0270× | 0.0265–0.0274× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.17` | Native C engine | 1.4569× | 1.4390–1.4778× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.17` | Rust engine | 0.1684× | 0.1581–0.1754× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.18` | Python engine | 0.0284× | 0.0280–0.0288× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.18` | Native C engine | 1.3890× | 1.2761–1.4638× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.18` | Rust engine | 0.1811× | 0.1789–0.1832× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.19` | Python engine | 0.0648× | 0.0633–0.0662× | 2.64× | SLOWDOWN |
| holdout | `hold.large.prefix-check.19` | Native C engine | 1.3585× | 1.3254–1.3903× | 0.00× | FASTER |
| holdout | `hold.large.prefix-check.19` | Rust engine | 0.2361× | 0.2325–0.2398× | 0.00× | SLOWDOWN |
| holdout | `hold.large.prefix-check.20` | Python engine | 0.0262× | 0.0260–0.0264× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.20` | Native C engine | 1.4818× | 1.4694–1.4943× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.20` | Rust engine | 0.1706× | 0.1675–0.1733× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.21` | Python engine | 0.0272× | 0.0269–0.0276× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.21` | Native C engine | 1.4663× | 1.4490–1.4827× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.21` | Rust engine | 0.1736× | 0.1682–0.1770× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.22` | Python engine | 0.0273× | 0.0254–0.0285× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.22` | Native C engine | 1.3836× | 1.3305–1.4337× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.22` | Rust engine | 0.1802× | 0.1774–0.1829× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.23` | Python engine | 0.0656× | 0.0635–0.0681× | 2.64× | SLOWDOWN |
| holdout | `hold.large.prefix-check.23` | Native C engine | 1.3517× | 1.2958–1.4075× | 0.00× | FASTER |
| holdout | `hold.large.prefix-check.23` | Rust engine | 0.2396× | 0.2322–0.2484× | 0.00× | SLOWDOWN |
| holdout | `hold.large.prefix-check.24` | Python engine | 0.0267× | 0.0264–0.0269× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.24` | Native C engine | 1.4800× | 1.4657–1.4934× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.24` | Rust engine | 0.1713× | 0.1690–0.1737× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.25` | Python engine | 0.0302× | 0.0271–0.0358× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.25` | Native C engine | 1.5911× | 1.4375–1.8818× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.25` | Rust engine | 0.1932× | 0.1755–0.2264× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.26` | Python engine | 0.0280× | 0.0274–0.0286× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.26` | Native C engine | 1.4582× | 1.4314–1.4877× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.26` | Rust engine | 0.1798× | 0.1771–0.1826× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.27` | Python engine | 0.0632× | 0.0611–0.0656× | 2.64× | SLOWDOWN |
| holdout | `hold.large.prefix-check.27` | Native C engine | 1.3313× | 1.2999–1.3644× | 0.00× | FASTER |
| holdout | `hold.large.prefix-check.27` | Rust engine | 0.1986× | 0.1419–0.2385× | 0.00× | SLOWDOWN |
| holdout | `hold.large.prefix-check.28` | Python engine | 0.0249× | 0.0241–0.0255× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.28` | Native C engine | 1.4873× | 1.4761–1.5007× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.28` | Rust engine | 0.1657× | 0.1587–0.1704× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.29` | Python engine | 0.0258× | 0.0254–0.0261× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.29` | Native C engine | 1.4749× | 1.4622–1.4877× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.29` | Rust engine | 0.1607× | 0.1501–0.1688× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.30` | Python engine | 0.0268× | 0.0265–0.0271× | 4.31× | SLOWDOWN |
| holdout | `hold.large.prefix-check.30` | Native C engine | 1.4019× | 1.3328–1.4550× | 0.07× | FASTER |
| holdout | `hold.large.prefix-check.30` | Rust engine | 0.1788× | 0.1772–0.1808× | 0.07× | SLOWDOWN |
| holdout | `hold.large.prefix-check.31` | Python engine | 0.0630× | 0.0621–0.0639× | 2.64× | SLOWDOWN |
| holdout | `hold.large.prefix-check.31` | Native C engine | 1.3161× | 1.2777–1.3580× | 0.00× | FASTER |
| holdout | `hold.large.prefix-check.31` | Rust engine | 0.2290× | 0.2232–0.2342× | 0.00× | SLOWDOWN |
| holdout | `hold.large.whole-check.00` | Python engine | 0.0197× | 0.0195–0.0200× | 10.00× | SLOWDOWN |
| holdout | `hold.large.whole-check.00` | Native C engine | 1.2827× | 1.2020–1.3323× | 0.69× | FASTER |
| holdout | `hold.large.whole-check.00` | Rust engine | 0.1043× | 0.1031–0.1055× | 0.06× | SLOWDOWN |
| holdout | `hold.large.whole-check.01` | Python engine | 0.0147× | 0.0136–0.0161× | 17.30× | SLOWDOWN |
| holdout | `hold.large.whole-check.01` | Native C engine | 1.2629× | 1.2106–1.3598× | 0.98× | FASTER |
| holdout | `hold.large.whole-check.01` | Rust engine | 0.0963× | 0.0916–0.1041× | 0.06× | SLOWDOWN |
| holdout | `hold.large.whole-check.02` | Python engine | 0.0138× | 0.0128–0.0156× | 15.80× | SLOWDOWN |
| holdout | `hold.large.whole-check.02` | Native C engine | 1.3813× | 1.1975–1.6254× | 0.80× | FASTER |
| holdout | `hold.large.whole-check.02` | Rust engine | 0.0918× | 0.0832–0.1041× | 0.03× | SLOWDOWN |
| holdout | `hold.large.whole-check.03` | Python engine | 0.0117× | 0.0115–0.0120× | 18.16× | SLOWDOWN |
| holdout | `hold.large.whole-check.03` | Native C engine | 1.4323× | 1.4078–1.4555× | 0.85× | FASTER |
| holdout | `hold.large.whole-check.03` | Rust engine | 0.0784× | 0.0765–0.0801× | 0.02× | SLOWDOWN |
| holdout | `hold.large.whole-check.04` | Python engine | 0.0191× | 0.0190–0.0193× | 10.00× | SLOWDOWN |
| holdout | `hold.large.whole-check.04` | Native C engine | 1.3111× | 1.3024–1.3191× | 0.69× | FASTER |
| holdout | `hold.large.whole-check.04` | Rust engine | 0.1059× | 0.1038–0.1073× | 0.06× | SLOWDOWN |
| holdout | `hold.large.whole-check.05` | Python engine | 0.0142× | 0.0141–0.0143× | 17.30× | SLOWDOWN |
| holdout | `hold.large.whole-check.05` | Native C engine | 1.2426× | 1.2347–1.2516× | 0.98× | FASTER |
| holdout | `hold.large.whole-check.05` | Rust engine | 0.0855× | 0.0851–0.0859× | 0.06× | SLOWDOWN |
| holdout | `hold.large.whole-check.06` | Python engine | 0.0136× | 0.0134–0.0137× | 17.15× | SLOWDOWN |
| holdout | `hold.large.whole-check.06` | Native C engine | 2.8129× | 2.2528–3.1693× | 0.83× | FASTER |
| holdout | `hold.large.whole-check.06` | Rust engine | 0.2207× | 0.2141–0.2257× | 0.00× | SLOWDOWN |
| holdout | `hold.large.whole-check.07` | Python engine | 0.0120× | 0.0116–0.0127× | 18.16× | SLOWDOWN |
| holdout | `hold.large.whole-check.07` | Native C engine | 1.4728× | 1.4217–1.5456× | 0.85× | FASTER |
| holdout | `hold.large.whole-check.07` | Rust engine | 0.0813× | 0.0783–0.0850× | 0.02× | SLOWDOWN |
| holdout | `hold.large.whole-check.08` | Python engine | 0.0194× | 0.0192–0.0196× | 10.00× | SLOWDOWN |
| holdout | `hold.large.whole-check.08` | Native C engine | 1.3038× | 1.2639–1.3308× | 0.69× | FASTER |
| holdout | `hold.large.whole-check.08` | Rust engine | 0.1090× | 0.1077–0.1101× | 0.06× | SLOWDOWN |
| holdout | `hold.large.whole-check.09` | Python engine | 0.0142× | 0.0139–0.0145× | 17.30× | SLOWDOWN |
| holdout | `hold.large.whole-check.09` | Native C engine | 1.2876× | 1.2747–1.3003× | 0.98× | FASTER |
| holdout | `hold.large.whole-check.09` | Rust engine | 0.0791× | 0.0783–0.0798× | 0.06× | SLOWDOWN |
| holdout | `hold.large.whole-check.10` | Python engine | 0.0129× | 0.0127–0.0130× | 15.80× | SLOWDOWN |
| holdout | `hold.large.whole-check.10` | Native C engine | 1.3915× | 1.3712–1.4118× | 0.80× | FASTER |
| holdout | `hold.large.whole-check.10` | Rust engine | 0.0745× | 0.0727–0.0760× | 0.03× | SLOWDOWN |
| holdout | `hold.large.whole-check.11` | Python engine | 0.0120× | 0.0119–0.0121× | 18.16× | SLOWDOWN |
| holdout | `hold.large.whole-check.11` | Native C engine | 1.4384× | 1.4048–1.4695× | 0.85× | FASTER |
| holdout | `hold.large.whole-check.11` | Rust engine | 0.0795× | 0.0782–0.0807× | 0.02× | SLOWDOWN |
| holdout | `hold.large.whole-check.12` | Python engine | 0.0192× | 0.0191–0.0193× | 10.00× | SLOWDOWN |
| holdout | `hold.large.whole-check.12` | Native C engine | 1.3097× | 1.3016–1.3184× | 0.69× | FASTER |
| holdout | `hold.large.whole-check.12` | Rust engine | 0.1081× | 0.1076–0.1085× | 0.06× | SLOWDOWN |
| holdout | `hold.large.whole-check.13` | Python engine | 0.0140× | 0.0138–0.0142× | 20.39× | SLOWDOWN |
| holdout | `hold.large.whole-check.13` | Native C engine | 3.0440× | 3.0072–3.1005× | 1.08× | FASTER |
| holdout | `hold.large.whole-check.13` | Rust engine | 0.2405× | 0.2382–0.2437× | 0.00× | SLOWDOWN |
| holdout | `hold.large.whole-check.14` | Python engine | 0.0128× | 0.0126–0.0129× | 15.80× | SLOWDOWN |
| holdout | `hold.large.whole-check.14` | Native C engine | 1.3891× | 1.3695–1.4092× | 0.80× | FASTER |
| holdout | `hold.large.whole-check.14` | Rust engine | 0.0755× | 0.0747–0.0762× | 0.03× | SLOWDOWN |
| holdout | `hold.large.whole-check.15` | Python engine | 0.0119× | 0.0116–0.0121× | 18.16× | SLOWDOWN |
| holdout | `hold.large.whole-check.15` | Native C engine | 1.4340× | 1.4022–1.4668× | 0.85× | FASTER |
| holdout | `hold.large.whole-check.15` | Rust engine | 0.0767× | 0.0703–0.0810× | 0.02× | SLOWDOWN |
| holdout | `hold.large.whole-check.16` | Python engine | 0.0192× | 0.0188–0.0195× | 10.00× | SLOWDOWN |
| holdout | `hold.large.whole-check.16` | Native C engine | 1.3031× | 1.2834–1.3208× | 0.69× | FASTER |
| holdout | `hold.large.whole-check.16` | Rust engine | 0.1085× | 0.1067–0.1098× | 0.06× | SLOWDOWN |
| holdout | `hold.large.whole-check.17` | Python engine | 0.0145× | 0.0144–0.0146× | 17.30× | SLOWDOWN |
| holdout | `hold.large.whole-check.17` | Native C engine | 1.2924× | 1.2766–1.3060× | 0.98× | FASTER |
| holdout | `hold.large.whole-check.17` | Rust engine | 0.0878× | 0.0869–0.0886× | 0.06× | SLOWDOWN |
| holdout | `hold.large.whole-check.18` | Python engine | 0.0128× | 0.0123–0.0131× | 15.80× | SLOWDOWN |
| holdout | `hold.large.whole-check.18` | Native C engine | 1.4086× | 1.3895–1.4285× | 0.80× | FASTER |
| holdout | `hold.large.whole-check.18` | Rust engine | 0.0758× | 0.0742–0.0773× | 0.03× | SLOWDOWN |
| holdout | `hold.large.whole-check.19` | Python engine | 0.0115× | 0.0113–0.0117× | 18.16× | SLOWDOWN |
| holdout | `hold.large.whole-check.19` | Native C engine | 1.4142× | 1.3865–1.4424× | 0.85× | FASTER |
| holdout | `hold.large.whole-check.19` | Rust engine | 0.0779× | 0.0757–0.0798× | 0.02× | SLOWDOWN |
| holdout | `hold.large.whole-check.20` | Python engine | 0.0157× | 0.0155–0.0160× | 15.03× | SLOWDOWN |
| holdout | `hold.large.whole-check.20` | Native C engine | 2.4564× | 2.2573–2.6124× | 0.76× | FASTER |
| holdout | `hold.large.whole-check.20` | Rust engine | 0.2596× | 0.2565–0.2630× | 0.00× | SLOWDOWN |
| holdout | `hold.large.whole-check.21` | Python engine | 0.0149× | 0.0143–0.0161× | 17.30× | SLOWDOWN |
| holdout | `hold.large.whole-check.21` | Native C engine | 1.2807× | 1.2242–1.3828× | 0.98× | FASTER |
| holdout | `hold.large.whole-check.21` | Rust engine | 0.0881× | 0.0846–0.0943× | 0.06× | SLOWDOWN |
| holdout | `hold.large.whole-check.22` | Python engine | 0.0126× | 0.0124–0.0128× | 15.80× | SLOWDOWN |
| holdout | `hold.large.whole-check.22` | Native C engine | 1.3439× | 1.3170–1.3692× | 0.80× | FASTER |
| holdout | `hold.large.whole-check.22` | Rust engine | 0.0672× | 0.0660–0.0684× | 0.03× | SLOWDOWN |
| holdout | `hold.large.whole-check.23` | Python engine | 0.0117× | 0.0115–0.0119× | 18.16× | SLOWDOWN |
| holdout | `hold.large.whole-check.23` | Native C engine | 1.4527× | 1.4212–1.4865× | 0.85× | FASTER |
| holdout | `hold.large.whole-check.23` | Rust engine | 0.0792× | 0.0771–0.0810× | 0.02× | SLOWDOWN |
| holdout | `hold.large.whole-check.24` | Python engine | 0.0199× | 0.0188–0.0220× | 10.00× | SLOWDOWN |
| holdout | `hold.large.whole-check.24` | Native C engine | 1.3246× | 1.3112–1.3396× | 0.69× | FASTER |
| holdout | `hold.large.whole-check.24` | Rust engine | 0.0983× | 0.0895–0.1103× | 0.06× | SLOWDOWN |
| holdout | `hold.large.whole-check.25` | Python engine | 0.0136× | 0.0123–0.0146× | 17.30× | SLOWDOWN |
| holdout | `hold.large.whole-check.25` | Native C engine | 1.2975× | 1.2809–1.3156× | 0.98× | FASTER |
| holdout | `hold.large.whole-check.25` | Rust engine | 0.0836× | 0.0754–0.0888× | 0.06× | SLOWDOWN |
| holdout | `hold.large.whole-check.26` | Python engine | 0.0133× | 0.0125–0.0146× | 15.80× | SLOWDOWN |
| holdout | `hold.large.whole-check.26` | Native C engine | 1.3675× | 1.3335–1.4054× | 0.80× | FASTER |
| holdout | `hold.large.whole-check.26` | Rust engine | 0.0780× | 0.0737–0.0849× | 0.03× | SLOWDOWN |
| holdout | `hold.large.whole-check.27` | Python engine | 0.0120× | 0.0115–0.0125× | 19.29× | SLOWDOWN |
| holdout | `hold.large.whole-check.27` | Native C engine | 3.8940× | 3.6182–4.0859× | 0.87× | FASTER |
| holdout | `hold.large.whole-check.27` | Rust engine | 0.2303× | 0.2202–0.2387× | 0.00× | SLOWDOWN |
| holdout | `hold.large.whole-check.28` | Python engine | 0.0188× | 0.0178–0.0206× | 10.00× | SLOWDOWN |
| holdout | `hold.large.whole-check.28` | Native C engine | 1.2817× | 1.1233–1.4574× | 0.69× | FASTER |
| holdout | `hold.large.whole-check.28` | Rust engine | 0.0980× | 0.0915–0.1073× | 0.06× | SLOWDOWN |
| holdout | `hold.large.whole-check.29` | Python engine | 0.0137× | 0.0134–0.0141× | 17.30× | SLOWDOWN |
| holdout | `hold.large.whole-check.29` | Native C engine | 1.2891× | 1.2694–1.3073× | 0.98× | FASTER |
| holdout | `hold.large.whole-check.29` | Rust engine | 0.0817× | 0.0803–0.0830× | 0.06× | SLOWDOWN |
| holdout | `hold.large.whole-check.30` | Python engine | 0.0141× | 0.0120–0.0166× | 15.80× | SLOWDOWN |
| holdout | `hold.large.whole-check.30` | Native C engine | 1.5788× | 1.3525–1.8565× | 0.80× | FASTER |
| holdout | `hold.large.whole-check.30` | Rust engine | 0.0830× | 0.0734–0.0957× | 0.03× | SLOWDOWN |
| holdout | `hold.large.whole-check.31` | Python engine | 0.0116× | 0.0110–0.0125× | 18.16× | SLOWDOWN |
| holdout | `hold.large.whole-check.31` | Native C engine | 1.3252× | 1.2171–1.4156× | 0.85× | FASTER |
| holdout | `hold.large.whole-check.31` | Rust engine | 0.0755× | 0.0696–0.0856× | 0.02× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.00` | Python engine | 0.0205× | 0.0199–0.0210× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.00` | Native C engine | 1.4189× | 1.3617–1.4522× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.00` | Rust engine | 0.2078× | 0.2031–0.2108× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.01` | Python engine | 0.0252× | 0.0246–0.0256× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.01` | Native C engine | 1.5948× | 1.4372–1.6964× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.01` | Rust engine | 0.2569× | 0.2500–0.2615× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.02` | Python engine | 0.0333× | 0.0329–0.0336× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.02` | Native C engine | 2.2236× | 2.1944–2.2492× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.02` | Rust engine | 0.3534× | 0.3500–0.3570× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.03` | Python engine | 0.0452× | 0.0445–0.0458× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.03` | Native C engine | 2.9980× | 2.9614–3.0338× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.03` | Rust engine | 0.4945× | 0.4908–0.4980× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.04` | Python engine | 0.0211× | 0.0208–0.0213× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.04` | Native C engine | 1.4433× | 1.4335–1.4533× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.04` | Rust engine | 0.1896× | 0.1856–0.1936× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.05` | Python engine | 0.0259× | 0.0254–0.0267× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.05` | Native C engine | 1.7211× | 1.6852–1.7757× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.05` | Rust engine | 0.2390× | 0.2319–0.2469× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.06` | Python engine | 0.0327× | 0.0324–0.0331× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.06` | Native C engine | 2.1842× | 2.1179–2.2316× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.06` | Rust engine | 0.3205× | 0.3082–0.3289× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.07` | Python engine | 0.0460× | 0.0452–0.0468× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.07` | Native C engine | 3.0119× | 2.9603–3.0628× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.07` | Rust engine | 0.4804× | 0.4476–0.5036× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.08` | Python engine | 0.0209× | 0.0207–0.0211× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.08` | Native C engine | 1.4301× | 1.3937–1.4532× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.08` | Rust engine | 0.1841× | 0.1719–0.1936× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.09` | Python engine | 0.0256× | 0.0253–0.0259× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.09` | Native C engine | 1.7100× | 1.6866–1.7402× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.09` | Rust engine | 0.2416× | 0.2378–0.2457× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.10` | Python engine | 0.0334× | 0.0321–0.0356× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.10` | Native C engine | 2.2927× | 2.1978–2.4652× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.10` | Rust engine | 0.3334× | 0.3192–0.3585× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.11` | Python engine | 0.0449× | 0.0445–0.0454× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.11` | Native C engine | 2.9859× | 2.9173–3.0472× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.11` | Rust engine | 0.4868× | 0.4737–0.4957× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.12` | Python engine | 0.0216× | 0.0210–0.0227× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.12` | Native C engine | 1.5007× | 1.4525–1.5873× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.12` | Rust engine | 0.1987× | 0.1910–0.2111× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.13` | Python engine | 0.0252× | 0.0251–0.0254× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.13` | Native C engine | 1.6793× | 1.6692–1.6890× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.13` | Rust engine | 0.2242× | 0.2111–0.2353× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.14` | Python engine | 0.0326× | 0.0323–0.0329× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.14` | Native C engine | 2.1470× | 1.9552–2.2676× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.14` | Rust engine | 0.3278× | 0.3247–0.3311× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.15` | Python engine | 0.0450× | 0.0444–0.0456× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.15` | Native C engine | 2.7116× | 2.2925–2.9777× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.15` | Rust engine | 0.4896× | 0.4827–0.4948× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.16` | Python engine | 0.0217× | 0.0209–0.0228× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.16` | Native C engine | 1.5005× | 1.4476–1.5754× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.16` | Rust engine | 0.1991× | 0.1914–0.2100× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.17` | Python engine | 0.0268× | 0.0254–0.0290× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.17` | Native C engine | 1.7909× | 1.6947–1.9503× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.17` | Rust engine | 0.2523× | 0.2387–0.2762× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.18` | Python engine | 0.0328× | 0.0325–0.0331× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.18` | Native C engine | 2.0909× | 1.8509–2.2359× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.18` | Rust engine | 0.3205× | 0.3117–0.3261× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.19` | Python engine | 0.0476× | 0.0450–0.0528× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.19` | Native C engine | 3.1140× | 2.9407–3.4427× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.19` | Rust engine | 0.5142× | 0.4868–0.5687× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.20` | Python engine | 0.0212× | 0.0210–0.0214× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.20` | Native C engine | 1.4339× | 1.4123–1.4526× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.20` | Rust engine | 0.1945× | 0.1931–0.1963× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.21` | Python engine | 0.0265× | 0.0250–0.0292× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.21` | Native C engine | 1.6837× | 1.4946–1.8800× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.21` | Rust engine | 0.2515× | 0.2381–0.2747× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.22` | Python engine | 0.0337× | 0.0324–0.0361× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.22` | Native C engine | 2.2722× | 2.1757–2.4287× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.22` | Rust engine | 0.3338× | 0.3218–0.3562× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.23` | Python engine | 0.0456× | 0.0449–0.0462× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.23` | Native C engine | 2.9992× | 2.9542–3.0427× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.23` | Rust engine | 0.4921× | 0.4893–0.4950× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.24` | Python engine | 0.0211× | 0.0208–0.0214× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.24` | Native C engine | 1.4535× | 1.4445–1.4623× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.24` | Rust engine | 0.1903× | 0.1863–0.1936× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.25` | Python engine | 0.0257× | 0.0255–0.0258× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.25` | Native C engine | 1.6400× | 1.5204–1.7112× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.25` | Rust engine | 0.2380× | 0.2365–0.2397× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.26` | Python engine | 0.0331× | 0.0327–0.0334× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.26` | Native C engine | 2.2189× | 2.1987–2.2375× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.26` | Rust engine | 0.3245× | 0.3196–0.3284× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.27` | Python engine | 0.0453× | 0.0449–0.0457× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.27` | Native C engine | 2.9081× | 2.8494–2.9635× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.27` | Rust engine | 0.4488× | 0.4157–0.4734× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.28` | Python engine | 0.0210× | 0.0205–0.0216× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.28` | Native C engine | 1.4581× | 1.4454–1.4739× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.28` | Rust engine | 0.1857× | 0.1814–0.1898× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.29` | Python engine | 0.0255× | 0.0253–0.0256× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.29` | Native C engine | 1.6823× | 1.6672–1.6950× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.29` | Rust engine | 0.2268× | 0.2225–0.2303× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.30` | Python engine | 0.0323× | 0.0319–0.0326× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.30` | Native C engine | 2.2063× | 2.1735–2.2383× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.30` | Rust engine | 0.3120× | 0.3097–0.3143× | 0.06× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.31` | Python engine | 0.0441× | 0.0425–0.0452× | 11.42× | SLOWDOWN |
| holdout | `hold.large.nearby-capture.31` | Native C engine | 2.8867× | 2.8403–2.9355× | 0.08× | FASTER |
| holdout | `hold.large.nearby-capture.31` | Rust engine | 0.4663× | 0.4628–0.4698× | 0.06× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.00` | Python engine | 0.0206× | 0.0197–0.0221× | 8.58× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.00` | Native C engine | 1.9330× | 1.8553–2.0765× | 0.10× | FASTER |
| holdout | `hold.large.findall-tokens.00` | Rust engine | 0.1767× | 0.1688–0.1905× | 0.93× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.01` | Python engine | 0.0202× | 0.0196–0.0212× | 9.45× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.01` | Native C engine | 2.1743× | 2.1071–2.2931× | 0.17× | FASTER |
| holdout | `hold.large.findall-tokens.01` | Rust engine | 0.1631× | 0.1584–0.1714× | 1.92× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.02` | Python engine | 0.0198× | 0.0196–0.0200× | 10.69× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.02` | Native C engine | 2.2630× | 2.2422–2.2834× | 0.29× | FASTER |
| holdout | `hold.large.findall-tokens.02` | Rust engine | 0.1733× | 0.1645–0.1799× | 3.29× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.03` | Python engine | 0.0189× | 0.0177–0.0195× | 12.31× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.03` | Native C engine | 2.3556× | 2.3291–2.3811× | 0.45× | FASTER |
| holdout | `hold.large.findall-tokens.03` | Rust engine | 0.1728× | 0.1597–0.1803× | 5.23× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.04` | Python engine | 0.0192× | 0.0183–0.0197× | 8.57× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.04` | Native C engine | 1.8479× | 1.8354–1.8614× | 0.10× | FASTER |
| holdout | `hold.large.findall-tokens.04` | Rust engine | 0.1578× | 0.1568–0.1587× | 1.00× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.05` | Python engine | 0.0194× | 0.0193–0.0196× | 9.45× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.05` | Native C engine | 2.1230× | 2.0983–2.1467× | 0.17× | FASTER |
| holdout | `hold.large.findall-tokens.05` | Rust engine | 0.1680× | 0.1671–0.1692× | 1.92× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.06` | Python engine | 0.0196× | 0.0194–0.0197× | 10.68× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.06` | Native C engine | 2.2566× | 2.2347–2.2806× | 0.29× | FASTER |
| holdout | `hold.large.findall-tokens.06` | Rust engine | 0.1761× | 0.1721–0.1785× | 3.34× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.07` | Python engine | 0.0194× | 0.0193–0.0195× | 12.31× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.07` | Native C engine | 2.3729× | 2.3544–2.3949× | 0.45× | FASTER |
| holdout | `hold.large.findall-tokens.07` | Rust engine | 0.1774× | 0.1747–0.1800× | 5.23× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.08` | Python engine | 0.0203× | 0.0187–0.0219× | 8.57× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.08` | Native C engine | 1.9005× | 1.8469–1.9847× | 0.10× | FASTER |
| holdout | `hold.large.findall-tokens.08` | Rust engine | 0.1582× | 0.1432–0.1698× | 1.00× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.09` | Python engine | 0.0191× | 0.0188–0.0194× | 9.45× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.09` | Native C engine | 2.1161× | 2.0966–2.1373× | 0.17× | FASTER |
| holdout | `hold.large.findall-tokens.09` | Rust engine | 0.1675× | 0.1653–0.1698× | 1.92× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.10` | Python engine | 0.0196× | 0.0195–0.0196× | 10.63× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.10` | Native C engine | 2.2704× | 2.2377–2.2972× | 0.29× | FASTER |
| holdout | `hold.large.findall-tokens.10` | Rust engine | 0.1519× | 0.1510–0.1527× | 3.57× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.11` | Python engine | 0.0199× | 0.0196–0.0203× | 12.22× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.11` | Native C engine | 2.3885× | 2.3535–2.4361× | 0.45× | FASTER |
| holdout | `hold.large.findall-tokens.11` | Rust engine | 0.1571× | 0.1548–0.1604× | 5.56× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.12` | Python engine | 0.0200× | 0.0195–0.0208× | 8.57× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.12` | Native C engine | 1.8750× | 1.8558–1.8914× | 0.10× | FASTER |
| holdout | `hold.large.findall-tokens.12` | Rust engine | 0.1607× | 0.1559–0.1681× | 1.00× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.13` | Python engine | 0.0196× | 0.0191–0.0203× | 9.45× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.13` | Native C engine | 2.1920× | 2.1114–2.2973× | 0.17× | FASTER |
| holdout | `hold.large.findall-tokens.13` | Rust engine | 0.1709× | 0.1655–0.1784× | 1.92× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.14` | Python engine | 0.0196× | 0.0192–0.0198× | 10.63× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.14` | Native C engine | 2.2598× | 2.2407–2.2830× | 0.29× | FASTER |
| holdout | `hold.large.findall-tokens.14` | Rust engine | 0.1492× | 0.1447–0.1523× | 3.57× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.15` | Python engine | 0.0195× | 0.0194–0.0196× | 12.31× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.15` | Native C engine | 2.3323× | 2.2970–2.3636× | 0.45× | FASTER |
| holdout | `hold.large.findall-tokens.15` | Rust engine | 0.1800× | 0.1786–0.1816× | 5.23× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.16` | Python engine | 0.0198× | 0.0197–0.0199× | 8.57× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.16` | Native C engine | 1.8720× | 1.8496–1.8943× | 0.10× | FASTER |
| holdout | `hold.large.findall-tokens.16` | Rust engine | 0.1595× | 0.1582–0.1611× | 1.00× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.17` | Python engine | 0.0198× | 0.0194–0.0203× | 9.45× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.17` | Native C engine | 2.0700× | 1.9530–2.1545× | 0.17× | FASTER |
| holdout | `hold.large.findall-tokens.17` | Rust engine | 0.1696× | 0.1658–0.1746× | 1.92× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.18` | Python engine | 0.0196× | 0.0195–0.0197× | 10.68× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.18` | Native C engine | 2.2429× | 2.2220–2.2653× | 0.29× | FASTER |
| holdout | `hold.large.findall-tokens.18` | Rust engine | 0.1743× | 0.1716–0.1767× | 3.34× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.19` | Python engine | 0.0191× | 0.0180–0.0197× | 12.31× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.19` | Native C engine | 2.2873× | 2.1033–2.3954× | 0.45× | FASTER |
| holdout | `hold.large.findall-tokens.19` | Rust engine | 0.1786× | 0.1746–0.1819× | 5.23× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.20` | Python engine | 0.0207× | 0.0197–0.0219× | 8.57× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.20` | Native C engine | 1.9772× | 1.8910–2.0852× | 0.10× | FASTER |
| holdout | `hold.large.findall-tokens.20` | Rust engine | 0.1682× | 0.1582–0.1798× | 1.00× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.21` | Python engine | 0.0192× | 0.0186–0.0201× | 9.42× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.21` | Native C engine | 2.1229× | 2.1080–2.1372× | 0.17× | FASTER |
| holdout | `hold.large.findall-tokens.21` | Rust engine | 0.1452× | 0.1432–0.1476× | 2.06× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.22` | Python engine | 0.0192× | 0.0184–0.0198× | 10.68× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.22` | Native C engine | 2.1929× | 2.0676–2.2676× | 0.29× | FASTER |
| holdout | `hold.large.findall-tokens.22` | Rust engine | 0.1762× | 0.1736–0.1784× | 3.34× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.23` | Python engine | 0.0196× | 0.0194–0.0197× | 12.22× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.23` | Native C engine | 2.3370× | 2.3017–2.3670× | 0.45× | FASTER |
| holdout | `hold.large.findall-tokens.23` | Rust engine | 0.1543× | 0.1529–0.1555× | 5.56× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.24` | Python engine | 0.0197× | 0.0195–0.0199× | 8.57× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.24` | Native C engine | 1.8691× | 1.8459–1.8970× | 0.10× | FASTER |
| holdout | `hold.large.findall-tokens.24` | Rust engine | 0.1576× | 0.1555–0.1597× | 1.00× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.25` | Python engine | 0.0195× | 0.0192–0.0198× | 9.42× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.25` | Native C engine | 2.1381× | 2.1120–2.1646× | 0.17× | FASTER |
| holdout | `hold.large.findall-tokens.25` | Rust engine | 0.1464× | 0.1438–0.1488× | 2.06× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.26` | Python engine | 0.0199× | 0.0192–0.0210× | 10.63× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.26` | Native C engine | 2.3213× | 2.2510–2.4409× | 0.29× | FASTER |
| holdout | `hold.large.findall-tokens.26` | Rust engine | 0.1553× | 0.1494–0.1641× | 3.57× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.27` | Python engine | 0.0198× | 0.0196–0.0201× | 12.22× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.27` | Native C engine | 2.3650× | 2.3234–2.4062× | 0.45× | FASTER |
| holdout | `hold.large.findall-tokens.27` | Rust engine | 0.1717× | 0.1694–0.1740× | 5.56× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.28` | Python engine | 0.0194× | 0.0192–0.0196× | 8.55× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.28` | Native C engine | 1.8719× | 1.8461–1.8951× | 0.11× | FASTER |
| holdout | `hold.large.findall-tokens.28` | Rust engine | 0.1505× | 0.1495–0.1515× | 1.08× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.29` | Python engine | 0.0198× | 0.0192–0.0209× | 9.42× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.29` | Native C engine | 2.1481× | 2.0775–2.2757× | 0.17× | FASTER |
| holdout | `hold.large.findall-tokens.29` | Rust engine | 0.1612× | 0.1557–0.1711× | 2.06× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.30` | Python engine | 0.0196× | 0.0195–0.0198× | 10.63× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.30` | Native C engine | 2.2629× | 2.2382–2.2847× | 0.29× | FASTER |
| holdout | `hold.large.findall-tokens.30` | Rust engine | 0.1649× | 0.1612–0.1683× | 3.57× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.31` | Python engine | 0.0194× | 0.0193–0.0195× | 12.14× | SLOWDOWN |
| holdout | `hold.large.findall-tokens.31` | Native C engine | 2.3683× | 2.3521–2.3851× | 0.46× | FASTER |
| holdout | `hold.large.findall-tokens.31` | Rust engine | 0.1510× | 0.1489–0.1526× | 5.90× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.00` | Python engine | 0.0262× | 0.0254–0.0273× | 6.64× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.00` | Native C engine | 1.9981× | 1.9366–2.0798× | 0.35× | FASTER |
| holdout | `hold.large.finditer-pairs.00` | Rust engine | 0.1856× | 0.1780–0.1945× | 0.32× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.01` | Python engine | 0.0208× | 0.0206–0.0210× | 6.58× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.01` | Native C engine | 1.9516× | 1.9400–1.9635× | 0.41× | FASTER |
| holdout | `hold.large.finditer-pairs.01` | Rust engine | 0.1530× | 0.1512–0.1547× | 0.34× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.02` | Python engine | 0.0183× | 0.0180–0.0186× | 6.50× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.02` | Native C engine | 1.9828× | 1.9328–2.0365× | 0.49× | FASTER |
| holdout | `hold.large.finditer-pairs.02` | Rust engine | 0.1398× | 0.1377–0.1420× | 0.38× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.03` | Python engine | 0.0174× | 0.0171–0.0177× | 6.33× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.03` | Native C engine | 1.9169× | 1.8609–1.9778× | 0.59× | FASTER |
| holdout | `hold.large.finditer-pairs.03` | Rust engine | 0.1334× | 0.1314–0.1352× | 0.44× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.04` | Python engine | 0.0248× | 0.0244–0.0252× | 6.64× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.04` | Native C engine | 1.9114× | 1.8779–1.9480× | 0.35× | FASTER |
| holdout | `hold.large.finditer-pairs.04` | Rust engine | 0.1773× | 0.1751–0.1803× | 0.32× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.05` | Python engine | 0.0204× | 0.0202–0.0207× | 6.58× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.05` | Native C engine | 1.9396× | 1.9112–1.9689× | 0.41× | FASTER |
| holdout | `hold.large.finditer-pairs.05` | Rust engine | 0.1522× | 0.1493–0.1549× | 0.34× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.06` | Python engine | 0.0183× | 0.0181–0.0185× | 6.50× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.06` | Native C engine | 1.9550× | 1.9240–1.9890× | 0.49× | FASTER |
| holdout | `hold.large.finditer-pairs.06` | Rust engine | 0.1374× | 0.1359–0.1390× | 0.38× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.07` | Python engine | 0.0172× | 0.0168–0.0178× | 6.33× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.07` | Native C engine | 1.8422× | 1.7813–1.9155× | 0.59× | FASTER |
| holdout | `hold.large.finditer-pairs.07` | Rust engine | 0.1349× | 0.1315–0.1392× | 0.44× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.08` | Python engine | 0.0248× | 0.0242–0.0258× | 6.64× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.08` | Native C engine | 1.9339× | 1.8812–2.0160× | 0.35× | FASTER |
| holdout | `hold.large.finditer-pairs.08` | Rust engine | 0.1735× | 0.1683–0.1814× | 0.32× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.09` | Python engine | 0.0208× | 0.0201–0.0220× | 6.58× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.09` | Native C engine | 1.9100× | 1.7493–2.0614× | 0.41× | FASTER |
| holdout | `hold.large.finditer-pairs.09` | Rust engine | 0.1529× | 0.1470–0.1624× | 0.34× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.10` | Python engine | 0.0195× | 0.0183–0.0212× | 6.50× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.10` | Native C engine | 2.0223× | 1.9103–2.2318× | 0.49× | FASTER |
| holdout | `hold.large.finditer-pairs.10` | Rust engine | 0.1422× | 0.1393–0.1455× | 0.38× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.11` | Python engine | 0.0170× | 0.0168–0.0172× | 6.33× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.11` | Native C engine | 1.7199× | 1.5257–1.8894× | 0.59× | FASTER |
| holdout | `hold.large.finditer-pairs.11` | Rust engine | 0.1284× | 0.1226–0.1327× | 0.44× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.12` | Python engine | 0.0242× | 0.0240–0.0244× | 6.64× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.12` | Native C engine | 1.8138× | 1.6800–1.8954× | 0.35× | FASTER |
| holdout | `hold.large.finditer-pairs.12` | Rust engine | 0.1709× | 0.1658–0.1745× | 0.32× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.13` | Python engine | 0.0203× | 0.0201–0.0206× | 6.58× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.13` | Native C engine | 1.9600× | 1.9099–2.0132× | 0.41× | FASTER |
| holdout | `hold.large.finditer-pairs.13` | Rust engine | 0.1508× | 0.1480–0.1541× | 0.34× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.14` | Python engine | 0.0179× | 0.0176–0.0183× | 6.50× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.14` | Native C engine | 1.9222× | 1.8831–1.9663× | 0.49× | FASTER |
| holdout | `hold.large.finditer-pairs.14` | Rust engine | 0.1385× | 0.1361–0.1413× | 0.38× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.15` | Python engine | 0.0173× | 0.0171–0.0176× | 6.33× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.15` | Native C engine | 1.9076× | 1.8444–1.9708× | 0.59× | FASTER |
| holdout | `hold.large.finditer-pairs.15` | Rust engine | 0.1324× | 0.1279–0.1358× | 0.44× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.16` | Python engine | 0.0248× | 0.0241–0.0259× | 6.64× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.16` | Native C engine | 1.9243× | 1.8648–2.0090× | 0.35× | FASTER |
| holdout | `hold.large.finditer-pairs.16` | Rust engine | 0.1768× | 0.1710–0.1854× | 0.32× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.17` | Python engine | 0.0203× | 0.0201–0.0206× | 6.58× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.17` | Native C engine | 1.9567× | 1.9234–1.9951× | 0.41× | FASTER |
| holdout | `hold.large.finditer-pairs.17` | Rust engine | 0.1494× | 0.1474–0.1517× | 0.34× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.18` | Python engine | 0.0191× | 0.0182–0.0205× | 6.50× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.18` | Native C engine | 2.0327× | 1.9313–2.1934× | 0.49× | FASTER |
| holdout | `hold.large.finditer-pairs.18` | Rust engine | 0.1457× | 0.1391–0.1567× | 0.38× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.19` | Python engine | 0.0173× | 0.0170–0.0177× | 6.33× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.19` | Native C engine | 1.7838× | 1.6191–1.9010× | 0.59× | FASTER |
| holdout | `hold.large.finditer-pairs.19` | Rust engine | 0.1332× | 0.1305–0.1361× | 0.44× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.20` | Python engine | 0.0245× | 0.0244–0.0246× | 6.64× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.20` | Native C engine | 1.9088× | 1.8952–1.9212× | 0.35× | FASTER |
| holdout | `hold.large.finditer-pairs.20` | Rust engine | 0.1720× | 0.1711–0.1729× | 0.32× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.21` | Python engine | 0.0208× | 0.0204–0.0212× | 6.58× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.21` | Native C engine | 2.0078× | 1.9761–2.0372× | 0.41× | FASTER |
| holdout | `hold.large.finditer-pairs.21` | Rust engine | 0.1521× | 0.1491–0.1552× | 0.34× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.22` | Python engine | 0.0187× | 0.0183–0.0191× | 6.50× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.22` | Native C engine | 1.9972× | 1.9101–2.0779× | 0.49× | FASTER |
| holdout | `hold.large.finditer-pairs.22` | Rust engine | 0.1420× | 0.1398–0.1448× | 0.38× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.23` | Python engine | 0.0173× | 0.0163–0.0188× | 6.33× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.23` | Native C engine | 1.8755× | 1.7416–2.0602× | 0.59× | FASTER |
| holdout | `hold.large.finditer-pairs.23` | Rust engine | 0.1405× | 0.1334–0.1521× | 0.44× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.24` | Python engine | 0.0248× | 0.0243–0.0251× | 6.64× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.24` | Native C engine | 1.8820× | 1.7586–1.9584× | 0.35× | FASTER |
| holdout | `hold.large.finditer-pairs.24` | Rust engine | 0.1776× | 0.1755–0.1798× | 0.32× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.25` | Python engine | 0.0212× | 0.0208–0.0216× | 6.58× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.25` | Native C engine | 1.9371× | 1.7707–2.0540× | 0.41× | FASTER |
| holdout | `hold.large.finditer-pairs.25` | Rust engine | 0.1573× | 0.1532–0.1615× | 0.34× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.26` | Python engine | 0.0186× | 0.0184–0.0188× | 6.50× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.26` | Native C engine | 2.0220× | 1.9827–2.0609× | 0.49× | FASTER |
| holdout | `hold.large.finditer-pairs.26` | Rust engine | 0.1382× | 0.1361–0.1402× | 0.38× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.27` | Python engine | 0.0177× | 0.0174–0.0180× | 6.33× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.27` | Native C engine | 1.9385× | 1.8838–1.9962× | 0.59× | FASTER |
| holdout | `hold.large.finditer-pairs.27` | Rust engine | 0.1366× | 0.1344–0.1387× | 0.44× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.28` | Python engine | 0.0247× | 0.0245–0.0249× | 6.64× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.28` | Native C engine | 1.9403× | 1.9276–1.9537× | 0.35× | FASTER |
| holdout | `hold.large.finditer-pairs.28` | Rust engine | 0.1726× | 0.1709–0.1745× | 0.32× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.29` | Python engine | 0.0211× | 0.0206–0.0215× | 6.58× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.29` | Native C engine | 2.0392× | 1.9939–2.0835× | 0.41× | FASTER |
| holdout | `hold.large.finditer-pairs.29` | Rust engine | 0.1558× | 0.1524–0.1594× | 0.34× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.30` | Python engine | 0.0180× | 0.0178–0.0182× | 6.50× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.30` | Native C engine | 1.9741× | 1.9393–2.0053× | 0.49× | FASTER |
| holdout | `hold.large.finditer-pairs.30` | Rust engine | 0.1367× | 0.1348–0.1386× | 0.38× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.31` | Python engine | 0.0176× | 0.0171–0.0185× | 6.33× | SLOWDOWN |
| holdout | `hold.large.finditer-pairs.31` | Native C engine | 1.9702× | 1.8859–2.0776× | 0.59× | FASTER |
| holdout | `hold.large.finditer-pairs.31` | Rust engine | 0.1376× | 0.1333–0.1440× | 0.44× | SLOWDOWN |
| holdout | `hold.large.split-keep.00` | Python engine | 0.0242× | 0.0238–0.0247× | 5.84× | SLOWDOWN |
| holdout | `hold.large.split-keep.00` | Native C engine | 1.2115× | 1.1412–1.2627× | 0.27× | FASTER |
| holdout | `hold.large.split-keep.00` | Rust engine | 0.1454× | 0.1422–0.1491× | 1.85× | SLOWDOWN |
| holdout | `hold.large.split-keep.01` | Python engine | 0.0224× | 0.0215–0.0241× | 6.30× | SLOWDOWN |
| holdout | `hold.large.split-keep.01` | Native C engine | 1.3346× | 1.2800–1.4391× | 0.36× | FASTER |
| holdout | `hold.large.split-keep.01` | Rust engine | 0.1471× | 0.1413–0.1581× | 2.65× | SLOWDOWN |
| holdout | `hold.large.split-keep.02` | Python engine | 0.0219× | 0.0201–0.0245× | 7.12× | SLOWDOWN |
| holdout | `hold.large.split-keep.02` | Native C engine | 1.4155× | 1.2129–1.6456× | 0.50× | FASTER |
| holdout | `hold.large.split-keep.02` | Rust engine | 0.1509× | 0.1406–0.1660× | 3.96× | SLOWDOWN |
| holdout | `hold.large.split-keep.03` | Python engine | 0.0199× | 0.0187–0.0221× | 7.85× | SLOWDOWN |
| holdout | `hold.large.split-keep.03` | Native C engine | 1.4385× | 1.3632–1.5901× | 0.62× | FASTER |
| holdout | `hold.large.split-keep.03` | Rust engine | 0.1403× | 0.1369–0.1441× | 5.60× | SLOWDOWN |
| holdout | `hold.large.split-keep.04` | Python engine | 0.0241× | 0.0240–0.0243× | 5.84× | SLOWDOWN |
| holdout | `hold.large.split-keep.04` | Native C engine | 1.2551× | 1.2462–1.2635× | 0.27× | FASTER |
| holdout | `hold.large.split-keep.04` | Rust engine | 0.1447× | 0.1432–0.1463× | 1.85× | SLOWDOWN |
| holdout | `hold.large.split-keep.05` | Python engine | 0.0216× | 0.0214–0.0217× | 6.30× | SLOWDOWN |
| holdout | `hold.large.split-keep.05` | Native C engine | 1.2899× | 1.2790–1.2996× | 0.36× | FASTER |
| holdout | `hold.large.split-keep.05` | Rust engine | 0.1402× | 0.1385–0.1417× | 2.65× | SLOWDOWN |
| holdout | `hold.large.split-keep.06` | Python engine | 0.0201× | 0.0200–0.0202× | 7.12× | SLOWDOWN |
| holdout | `hold.large.split-keep.06` | Native C engine | 1.3431× | 1.3334–1.3524× | 0.50× | FASTER |
| holdout | `hold.large.split-keep.06` | Rust engine | 0.1378× | 0.1366–0.1389× | 3.96× | SLOWDOWN |
| holdout | `hold.large.split-keep.07` | Python engine | 0.0196× | 0.0194–0.0199× | 7.85× | SLOWDOWN |
| holdout | `hold.large.split-keep.07` | Native C engine | 1.3678× | 1.3529–1.3865× | 0.62× | FASTER |
| holdout | `hold.large.split-keep.07` | Rust engine | 0.1388× | 0.1369–0.1413× | 5.60× | SLOWDOWN |
| holdout | `hold.large.split-keep.08` | Python engine | 0.0243× | 0.0242–0.0244× | 5.84× | SLOWDOWN |
| holdout | `hold.large.split-keep.08` | Native C engine | 1.2260× | 1.2027–1.2447× | 0.27× | FASTER |
| holdout | `hold.large.split-keep.08` | Rust engine | 0.1454× | 0.1441–0.1466× | 1.85× | SLOWDOWN |
| holdout | `hold.large.split-keep.09` | Python engine | 0.0224× | 0.0214–0.0240× | 6.30× | SLOWDOWN |
| holdout | `hold.large.split-keep.09` | Native C engine | 1.3396× | 1.2797–1.4310× | 0.36× | FASTER |
| holdout | `hold.large.split-keep.09` | Rust engine | 0.1465× | 0.1390–0.1571× | 2.65× | SLOWDOWN |
| holdout | `hold.large.split-keep.10` | Python engine | 0.0201× | 0.0198–0.0204× | 7.12× | SLOWDOWN |
| holdout | `hold.large.split-keep.10` | Native C engine | 1.3561× | 1.3424–1.3697× | 0.50× | FASTER |
| holdout | `hold.large.split-keep.10` | Rust engine | 0.1390× | 0.1374–0.1407× | 3.96× | SLOWDOWN |
| holdout | `hold.large.split-keep.11` | Python engine | 0.0212× | 0.0202–0.0230× | 7.79× | SLOWDOWN |
| holdout | `hold.large.split-keep.11` | Native C engine | 1.3367× | 1.2557–1.4640× | 0.62× | FASTER |
| holdout | `hold.large.split-keep.11` | Rust engine | 0.1522× | 0.1452–0.1657× | 6.20× | SLOWDOWN |
| holdout | `hold.large.split-keep.12` | Python engine | 0.0243× | 0.0241–0.0246× | 5.84× | SLOWDOWN |
| holdout | `hold.large.split-keep.12` | Native C engine | 1.2505× | 1.2394–1.2619× | 0.27× | FASTER |
| holdout | `hold.large.split-keep.12` | Rust engine | 0.1471× | 0.1459–0.1484× | 1.85× | SLOWDOWN |
| holdout | `hold.large.split-keep.13` | Python engine | 0.0216× | 0.0214–0.0217× | 6.30× | SLOWDOWN |
| holdout | `hold.large.split-keep.13` | Native C engine | 1.2909× | 1.2799–1.3020× | 0.36× | FASTER |
| holdout | `hold.large.split-keep.13` | Rust engine | 0.1388× | 0.1368–0.1405× | 2.65× | SLOWDOWN |
| holdout | `hold.large.split-keep.14` | Python engine | 0.0202× | 0.0199–0.0203× | 7.12× | SLOWDOWN |
| holdout | `hold.large.split-keep.14` | Native C engine | 1.3125× | 1.2252–1.3627× | 0.50× | FASTER |
| holdout | `hold.large.split-keep.14` | Rust engine | 0.1379× | 0.1365–0.1392× | 3.92× | SLOWDOWN |
| holdout | `hold.large.split-keep.15` | Python engine | 0.0206× | 0.0203–0.0209× | 7.79× | SLOWDOWN |
| holdout | `hold.large.split-keep.15` | Native C engine | 1.3286× | 1.3087–1.3486× | 0.63× | FASTER |
| holdout | `hold.large.split-keep.15` | Rust engine | 0.1486× | 0.1460–0.1513× | 6.23× | SLOWDOWN |
| holdout | `hold.large.split-keep.16` | Python engine | 0.0249× | 0.0242–0.0261× | 5.84× | SLOWDOWN |
| holdout | `hold.large.split-keep.16` | Native C engine | 1.2869× | 1.2438–1.3467× | 0.27× | FASTER |
| holdout | `hold.large.split-keep.16` | Rust engine | 0.1498× | 0.1452–0.1570× | 1.85× | SLOWDOWN |
| holdout | `hold.large.split-keep.17` | Python engine | 0.0214× | 0.0213–0.0215× | 6.30× | SLOWDOWN |
| holdout | `hold.large.split-keep.17` | Native C engine | 1.2789× | 1.2720–1.2850× | 0.36× | FASTER |
| holdout | `hold.large.split-keep.17` | Rust engine | 0.1396× | 0.1381–0.1407× | 2.65× | SLOWDOWN |
| holdout | `hold.large.split-keep.18` | Python engine | 0.0200× | 0.0199–0.0201× | 7.12× | SLOWDOWN |
| holdout | `hold.large.split-keep.18` | Native C engine | 1.3421× | 1.3214–1.3580× | 0.50× | FASTER |
| holdout | `hold.large.split-keep.18` | Rust engine | 0.1382× | 0.1376–0.1388× | 3.96× | SLOWDOWN |
| holdout | `hold.large.split-keep.19` | Python engine | 0.0194× | 0.0193–0.0196× | 7.85× | SLOWDOWN |
| holdout | `hold.large.split-keep.19` | Native C engine | 1.3060× | 1.2136–1.3597× | 0.62× | FASTER |
| holdout | `hold.large.split-keep.19` | Rust engine | 0.1380× | 0.1368–0.1391× | 5.60× | SLOWDOWN |
| holdout | `hold.large.split-keep.20` | Python engine | 0.0249× | 0.0240–0.0266× | 5.84× | SLOWDOWN |
| holdout | `hold.large.split-keep.20` | Native C engine | 1.2740× | 1.2218–1.3647× | 0.27× | FASTER |
| holdout | `hold.large.split-keep.20` | Rust engine | 0.1497× | 0.1437–0.1604× | 1.85× | SLOWDOWN |
| holdout | `hold.large.split-keep.21` | Python engine | 0.0218× | 0.0212–0.0230× | 6.30× | SLOWDOWN |
| holdout | `hold.large.split-keep.21` | Native C engine | 1.3034× | 1.2646–1.3725× | 0.36× | FASTER |
| holdout | `hold.large.split-keep.21` | Rust engine | 0.1441× | 0.1402–0.1515× | 2.65× | SLOWDOWN |
| holdout | `hold.large.split-keep.22` | Python engine | 0.0201× | 0.0200–0.0202× | 7.12× | SLOWDOWN |
| holdout | `hold.large.split-keep.22` | Native C engine | 1.3571× | 1.3494–1.3648× | 0.50× | FASTER |
| holdout | `hold.large.split-keep.22` | Rust engine | 0.1384× | 0.1361–0.1401× | 3.96× | SLOWDOWN |
| holdout | `hold.large.split-keep.23` | Python engine | 0.0195× | 0.0177–0.0213× | 7.85× | SLOWDOWN |
| holdout | `hold.large.split-keep.23` | Native C engine | 1.3720× | 1.3529–1.3983× | 0.62× | FASTER |
| holdout | `hold.large.split-keep.23` | Rust engine | 0.1415× | 0.1354–0.1516× | 5.60× | SLOWDOWN |
| holdout | `hold.large.split-keep.24` | Python engine | 0.0242× | 0.0239–0.0245× | 5.84× | SLOWDOWN |
| holdout | `hold.large.split-keep.24` | Native C engine | 1.2406× | 1.2200–1.2588× | 0.27× | FASTER |
| holdout | `hold.large.split-keep.24` | Rust engine | 0.1444× | 0.1427–0.1462× | 1.85× | SLOWDOWN |
| holdout | `hold.large.split-keep.25` | Python engine | 0.0216× | 0.0215–0.0218× | 6.28× | SLOWDOWN |
| holdout | `hold.large.split-keep.25` | Native C engine | 1.1961× | 1.1045–1.2475× | 0.36× | FASTER |
| holdout | `hold.large.split-keep.25` | Rust engine | 0.1398× | 0.1317–0.1448× | 2.93× | SLOWDOWN |
| holdout | `hold.large.split-keep.26` | Python engine | 0.0201× | 0.0200–0.0202× | 7.12× | SLOWDOWN |
| holdout | `hold.large.split-keep.26` | Native C engine | 1.3293× | 1.2885–1.3599× | 0.50× | FASTER |
| holdout | `hold.large.split-keep.26` | Rust engine | 0.1392× | 0.1383–0.1402× | 3.96× | SLOWDOWN |
| holdout | `hold.large.split-keep.27` | Python engine | 0.0195× | 0.0194–0.0197× | 7.85× | SLOWDOWN |
| holdout | `hold.large.split-keep.27` | Native C engine | 1.3604× | 1.3479–1.3726× | 0.62× | FASTER |
| holdout | `hold.large.split-keep.27` | Rust engine | 0.1387× | 0.1373–0.1399× | 5.60× | SLOWDOWN |
| holdout | `hold.large.split-keep.28` | Python engine | 0.0241× | 0.0239–0.0244× | 5.84× | SLOWDOWN |
| holdout | `hold.large.split-keep.28` | Native C engine | 1.2602× | 1.2479–1.2743× | 0.27× | FASTER |
| holdout | `hold.large.split-keep.28` | Rust engine | 0.1434× | 0.1417–0.1453× | 1.80× | SLOWDOWN |
| holdout | `hold.large.split-keep.29` | Python engine | 0.0221× | 0.0218–0.0225× | 6.28× | SLOWDOWN |
| holdout | `hold.large.split-keep.29` | Native C engine | 1.2154× | 1.1137–1.2848× | 0.36× | FASTER |
| holdout | `hold.large.split-keep.29` | Rust engine | 0.1462× | 0.1439–0.1491× | 2.93× | SLOWDOWN |
| holdout | `hold.large.split-keep.30` | Python engine | 0.0212× | 0.0204–0.0225× | 7.12× | SLOWDOWN |
| holdout | `hold.large.split-keep.30` | Native C engine | 1.4193× | 1.3699–1.5005× | 0.50× | FASTER |
| holdout | `hold.large.split-keep.30` | Rust engine | 0.1453× | 0.1400–0.1539× | 3.96× | SLOWDOWN |
| holdout | `hold.large.split-keep.31` | Python engine | 0.0196× | 0.0195–0.0198× | 7.85× | SLOWDOWN |
| holdout | `hold.large.split-keep.31` | Native C engine | 1.3712× | 1.3615–1.3816× | 0.62× | FASTER |
| holdout | `hold.large.split-keep.31` | Rust engine | 0.1399× | 0.1393–0.1406× | 5.60× | SLOWDOWN |
| holdout | `hold.large.replace-groups.00` | Python engine | 0.0239× | 0.0233–0.0247× | 7.84× | SLOWDOWN |
| holdout | `hold.large.replace-groups.00` | Native C engine | 1.9352× | 1.8703–2.0110× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.00` | Rust engine | 0.0813× | 0.0794–0.0841× | 1.60× | SLOWDOWN |
| holdout | `hold.large.replace-groups.01` | Python engine | 0.0218× | 0.0212–0.0229× | 8.32× | SLOWDOWN |
| holdout | `hold.large.replace-groups.01` | Native C engine | 2.1307× | 2.0780–2.2295× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.01` | Rust engine | 0.0877× | 0.0850–0.0923× | 2.50× | SLOWDOWN |
| holdout | `hold.large.replace-groups.02` | Python engine | 0.0200× | 0.0199–0.0202× | 9.05× | SLOWDOWN |
| holdout | `hold.large.replace-groups.02` | Native C engine | 2.2222× | 2.2064–2.2400× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.02` | Rust engine | 0.0902× | 0.0893–0.0911× | 4.60× | SLOWDOWN |
| holdout | `hold.large.replace-groups.03` | Python engine | 0.0195× | 0.0184–0.0208× | 10.08× | SLOWDOWN |
| holdout | `hold.large.replace-groups.03` | Native C engine | 2.4347× | 2.2571–2.6177× | 0.14× | FASTER |
| holdout | `hold.large.replace-groups.03` | Rust engine | 0.0958× | 0.0895–0.1032× | 7.16× | SLOWDOWN |
| holdout | `hold.large.replace-groups.04` | Python engine | 0.0232× | 0.0213–0.0260× | 7.84× | SLOWDOWN |
| holdout | `hold.large.replace-groups.04` | Native C engine | 1.8889× | 1.7952–1.9559× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.04` | Rust engine | 0.0806× | 0.0732–0.0912× | 1.60× | SLOWDOWN |
| holdout | `hold.large.replace-groups.05` | Python engine | 0.0197× | 0.0186–0.0212× | 8.70× | SLOWDOWN |
| holdout | `hold.large.replace-groups.05` | Native C engine | 2.2119× | 2.1189–2.3409× | 0.14× | FASTER |
| holdout | `hold.large.replace-groups.05` | Rust engine | 0.0827× | 0.0791–0.0879× | 2.88× | SLOWDOWN |
| holdout | `hold.large.replace-groups.06` | Python engine | 0.0205× | 0.0184–0.0229× | 9.05× | SLOWDOWN |
| holdout | `hold.large.replace-groups.06` | Native C engine | 2.2350× | 1.9397–2.5401× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.06` | Rust engine | 0.0911× | 0.0816–0.1026× | 4.60× | SLOWDOWN |
| holdout | `hold.large.replace-groups.07` | Python engine | 0.0209× | 0.0195–0.0229× | 10.08× | SLOWDOWN |
| holdout | `hold.large.replace-groups.07` | Native C engine | 2.3977× | 2.3777–2.4226× | 0.14× | FASTER |
| holdout | `hold.large.replace-groups.07` | Rust engine | 0.0911× | 0.0830–0.0971× | 7.16× | SLOWDOWN |
| holdout | `hold.large.replace-groups.08` | Python engine | 0.0236× | 0.0227–0.0247× | 7.84× | SLOWDOWN |
| holdout | `hold.large.replace-groups.08` | Native C engine | 1.8844× | 1.6337–2.0998× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.08` | Rust engine | 0.0818× | 0.0777–0.0879× | 1.60× | SLOWDOWN |
| holdout | `hold.large.replace-groups.09` | Python engine | 0.0211× | 0.0209–0.0213× | 8.28× | SLOWDOWN |
| holdout | `hold.large.replace-groups.09` | Native C engine | 2.0513× | 1.9169–2.1301× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.09` | Rust engine | 0.0840× | 0.0831–0.0849× | 2.99× | SLOWDOWN |
| holdout | `hold.large.replace-groups.10` | Python engine | 0.0211× | 0.0208–0.0213× | 8.70× | SLOWDOWN |
| holdout | `hold.large.replace-groups.10` | Native C engine | 2.0922× | 2.0270–2.1390× | 0.16× | FASTER |
| holdout | `hold.large.replace-groups.10` | Rust engine | 0.0673× | 0.0658–0.0687× | 5.53× | SLOWDOWN |
| holdout | `hold.large.replace-groups.11` | Python engine | 0.0196× | 0.0192–0.0201× | 10.02× | SLOWDOWN |
| holdout | `hold.large.replace-groups.11` | Native C engine | 2.3882× | 2.3375–2.4642× | 0.14× | FASTER |
| holdout | `hold.large.replace-groups.11` | Rust engine | 0.0920× | 0.0876–0.0955× | 7.80× | SLOWDOWN |
| holdout | `hold.large.replace-groups.12` | Python engine | 0.0247× | 0.0235–0.0260× | 7.84× | SLOWDOWN |
| holdout | `hold.large.replace-groups.12` | Native C engine | 2.0307× | 1.9363–2.1535× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.12` | Rust engine | 0.0853× | 0.0813–0.0901× | 1.60× | SLOWDOWN |
| holdout | `hold.large.replace-groups.13` | Python engine | 0.0211× | 0.0209–0.0213× | 8.30× | SLOWDOWN |
| holdout | `hold.large.replace-groups.13` | Native C engine | 2.0870× | 2.0709–2.1045× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.13` | Rust engine | 0.0855× | 0.0843–0.0867× | 2.75× | SLOWDOWN |
| holdout | `hold.large.replace-groups.14` | Python engine | 0.0200× | 0.0195–0.0207× | 9.05× | SLOWDOWN |
| holdout | `hold.large.replace-groups.14` | Native C engine | 2.2318× | 2.1880–2.3072× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.14` | Rust engine | 0.0910× | 0.0891–0.0942× | 4.60× | SLOWDOWN |
| holdout | `hold.large.replace-groups.15` | Python engine | 0.0222× | 0.0219–0.0224× | 8.68× | SLOWDOWN |
| holdout | `hold.large.replace-groups.15` | Native C engine | 2.0567× | 2.0325–2.0809× | 0.22× | FASTER |
| holdout | `hold.large.replace-groups.15` | Rust engine | 0.0503× | 0.0487–0.0516× | 11.86× | SLOWDOWN |
| holdout | `hold.large.replace-groups.16` | Python engine | 0.0237× | 0.0228–0.0252× | 7.84× | SLOWDOWN |
| holdout | `hold.large.replace-groups.16` | Native C engine | 1.9767× | 1.9030–2.1040× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.16` | Rust engine | 0.0826× | 0.0793–0.0882× | 1.60× | SLOWDOWN |
| holdout | `hold.large.replace-groups.17` | Python engine | 0.0210× | 0.0207–0.0214× | 8.30× | SLOWDOWN |
| holdout | `hold.large.replace-groups.17` | Native C engine | 2.1008× | 2.0827–2.1220× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.17` | Rust engine | 0.0856× | 0.0845–0.0867× | 2.75× | SLOWDOWN |
| holdout | `hold.large.replace-groups.18` | Python engine | 0.0196× | 0.0193–0.0198× | 9.05× | SLOWDOWN |
| holdout | `hold.large.replace-groups.18` | Native C engine | 2.1965× | 2.1133–2.2469× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.18` | Rust engine | 0.0879× | 0.0847–0.0902× | 4.60× | SLOWDOWN |
| holdout | `hold.large.replace-groups.19` | Python engine | 0.0194× | 0.0193–0.0194× | 10.08× | SLOWDOWN |
| holdout | `hold.large.replace-groups.19` | Native C engine | 2.3491× | 2.3273–2.3686× | 0.14× | FASTER |
| holdout | `hold.large.replace-groups.19` | Rust engine | 0.0938× | 0.0928–0.0948× | 7.16× | SLOWDOWN |
| holdout | `hold.large.replace-groups.20` | Python engine | 0.0230× | 0.0228–0.0233× | 7.84× | SLOWDOWN |
| holdout | `hold.large.replace-groups.20` | Native C engine | 1.9388× | 1.9185–1.9667× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.20` | Rust engine | 0.0794× | 0.0784–0.0807× | 1.60× | SLOWDOWN |
| holdout | `hold.large.replace-groups.21` | Python engine | 0.0220× | 0.0204–0.0242× | 8.30× | SLOWDOWN |
| holdout | `hold.large.replace-groups.21` | Native C engine | 2.2090× | 2.0644–2.4274× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.21` | Rust engine | 0.0887× | 0.0823–0.0977× | 2.75× | SLOWDOWN |
| holdout | `hold.large.replace-groups.22` | Python engine | 0.0199× | 0.0197–0.0200× | 9.05× | SLOWDOWN |
| holdout | `hold.large.replace-groups.22` | Native C engine | 2.2004× | 2.1730–2.2248× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.22` | Rust engine | 0.0889× | 0.0875–0.0902× | 4.60× | SLOWDOWN |
| holdout | `hold.large.replace-groups.23` | Python engine | 0.0191× | 0.0185–0.0195× | 10.08× | SLOWDOWN |
| holdout | `hold.large.replace-groups.23` | Native C engine | 2.2682× | 2.1004–2.3638× | 0.14× | FASTER |
| holdout | `hold.large.replace-groups.23` | Rust engine | 0.0931× | 0.0919–0.0942× | 7.16× | SLOWDOWN |
| holdout | `hold.large.replace-groups.24` | Python engine | 0.0236× | 0.0232–0.0245× | 7.84× | SLOWDOWN |
| holdout | `hold.large.replace-groups.24` | Native C engine | 1.9403× | 1.8923–2.0161× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.24` | Rust engine | 0.0813× | 0.0795–0.0843× | 1.60× | SLOWDOWN |
| holdout | `hold.large.replace-groups.25` | Python engine | 0.0214× | 0.0201–0.0234× | 8.70× | SLOWDOWN |
| holdout | `hold.large.replace-groups.25` | Native C engine | 2.2532× | 2.1133–2.4681× | 0.14× | FASTER |
| holdout | `hold.large.replace-groups.25` | Rust engine | 0.0858× | 0.0802–0.0944× | 2.88× | SLOWDOWN |
| holdout | `hold.large.replace-groups.26` | Python engine | 0.0199× | 0.0198–0.0201× | 9.05× | SLOWDOWN |
| holdout | `hold.large.replace-groups.26` | Native C engine | 2.2172× | 2.1974–2.2370× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.26` | Rust engine | 0.0902× | 0.0894–0.0909× | 4.60× | SLOWDOWN |
| holdout | `hold.large.replace-groups.27` | Python engine | 0.0193× | 0.0191–0.0195× | 10.02× | SLOWDOWN |
| holdout | `hold.large.replace-groups.27` | Native C engine | 2.2281× | 1.9637–2.3852× | 0.14× | FASTER |
| holdout | `hold.large.replace-groups.27` | Rust engine | 0.0924× | 0.0891–0.0944× | 7.80× | SLOWDOWN |
| holdout | `hold.large.replace-groups.28` | Python engine | 0.0230× | 0.0229–0.0232× | 7.82× | SLOWDOWN |
| holdout | `hold.large.replace-groups.28` | Native C engine | 1.9085× | 1.8960–1.9226× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.28` | Rust engine | 0.0798× | 0.0791–0.0805× | 1.74× | SLOWDOWN |
| holdout | `hold.large.replace-groups.29` | Python engine | 0.0221× | 0.0211–0.0239× | 8.28× | SLOWDOWN |
| holdout | `hold.large.replace-groups.29` | Native C engine | 2.1922× | 2.0964–2.3811× | 0.13× | FASTER |
| holdout | `hold.large.replace-groups.29` | Rust engine | 0.0890× | 0.0853–0.0963× | 2.99× | SLOWDOWN |
| holdout | `hold.large.replace-groups.30` | Python engine | 0.0212× | 0.0210–0.0214× | 8.68× | SLOWDOWN |
| holdout | `hold.large.replace-groups.30` | Native C engine | 2.0514× | 1.9821–2.1093× | 0.16× | FASTER |
| holdout | `hold.large.replace-groups.30` | Rust engine | 0.0676× | 0.0667–0.0685× | 6.04× | SLOWDOWN |
| holdout | `hold.large.replace-groups.31` | Python engine | 0.0194× | 0.0193–0.0196× | 10.02× | SLOWDOWN |
| holdout | `hold.large.replace-groups.31` | Native C engine | 2.3913× | 2.3783–2.4083× | 0.14× | FASTER |
| holdout | `hold.large.replace-groups.31` | Rust engine | 0.0938× | 0.0924–0.0950× | 7.80× | SLOWDOWN |
| holdout | `hold.large.replace-callback.00` | Python engine | 0.0787× | 0.0769–0.0814× | 3.07× | SLOWDOWN |
| holdout | `hold.large.replace-callback.00` | Native C engine | 1.1628× | 1.1152–1.2136× | 0.25× | FASTER |
| holdout | `hold.large.replace-callback.00` | Rust engine | 0.2153× | 0.2101–0.2227× | 0.53× | SLOWDOWN |
| holdout | `hold.large.replace-callback.01` | Python engine | 0.0781× | 0.0772–0.0791× | 3.13× | SLOWDOWN |
| holdout | `hold.large.replace-callback.01` | Native C engine | 1.2411× | 1.2223–1.2616× | 0.23× | FASTER |
| holdout | `hold.large.replace-callback.01` | Rust engine | 0.2205× | 0.2173–0.2236× | 0.60× | SLOWDOWN |
| holdout | `hold.large.replace-callback.02` | Python engine | 0.0786× | 0.0769–0.0814× | 3.23× | SLOWDOWN |
| holdout | `hold.large.replace-callback.02` | Native C engine | 1.2991× | 1.2742–1.3370× | 0.21× | FASTER |
| holdout | `hold.large.replace-callback.02` | Rust engine | 0.2344× | 0.2295–0.2419× | 0.70× | SLOWDOWN |
| holdout | `hold.large.replace-callback.03` | Python engine | 0.0757× | 0.0736–0.0781× | 3.24× | SLOWDOWN |
| holdout | `hold.large.replace-callback.03` | Native C engine | 1.1558× | 1.1281–1.1887× | 0.34× | FASTER |
| holdout | `hold.large.replace-callback.03` | Rust engine | 0.2105× | 0.2063–0.2154× | 0.71× | SLOWDOWN |
| holdout | `hold.large.replace-callback.04` | Python engine | 0.0828× | 0.0815–0.0842× | 3.07× | SLOWDOWN |
| holdout | `hold.large.replace-callback.04` | Native C engine | 1.1646× | 1.1128–1.2015× | 0.25× | FASTER |
| holdout | `hold.large.replace-callback.04` | Rust engine | 0.2321× | 0.2298–0.2348× | 0.53× | SLOWDOWN |
| holdout | `hold.large.replace-callback.05` | Python engine | 0.0766× | 0.0713–0.0803× | 3.14× | SLOWDOWN |
| holdout | `hold.large.replace-callback.05` | Native C engine | 1.2058× | 1.1519–1.2406× | 0.23× | FASTER |
| holdout | `hold.large.replace-callback.05` | Rust engine | 0.2301× | 0.2273–0.2331× | 0.60× | SLOWDOWN |
| holdout | `hold.large.replace-callback.06` | Python engine | 0.0748× | 0.0710–0.0814× | 3.31× | SLOWDOWN |
| holdout | `hold.large.replace-callback.06` | Native C engine | 1.2092× | 1.1545–1.3045× | 0.29× | FASTER |
| holdout | `hold.large.replace-callback.06` | Rust engine | 0.2091× | 0.1971–0.2297× | 0.62× | SLOWDOWN |
| holdout | `hold.large.replace-callback.07` | Python engine | 0.0789× | 0.0771–0.0817× | 3.34× | SLOWDOWN |
| holdout | `hold.large.replace-callback.07` | Native C engine | 1.3130× | 1.2452–1.3777× | 0.19× | FASTER |
| holdout | `hold.large.replace-callback.07` | Rust engine | 0.2388× | 0.2340–0.2465× | 0.82× | SLOWDOWN |
| holdout | `hold.large.replace-callback.08` | Python engine | 0.0849× | 0.0833–0.0870× | 3.07× | SLOWDOWN |
| holdout | `hold.large.replace-callback.08` | Native C engine | 1.2101× | 1.1920–1.2293× | 0.25× | FASTER |
| holdout | `hold.large.replace-callback.08` | Rust engine | 0.2350× | 0.2307–0.2409× | 0.53× | SLOWDOWN |
| holdout | `hold.large.replace-callback.09` | Python engine | 0.0692× | 0.0680–0.0703× | 3.31× | SLOWDOWN |
| holdout | `hold.large.replace-callback.09` | Native C engine | 1.1626× | 1.1476–1.1786× | 0.26× | FASTER |
| holdout | `hold.large.replace-callback.09` | Rust engine | 0.1991× | 0.1949–0.2024× | 0.56× | SLOWDOWN |
| holdout | `hold.large.replace-callback.10` | Python engine | 0.0800× | 0.0783–0.0826× | 3.23× | SLOWDOWN |
| holdout | `hold.large.replace-callback.10` | Native C engine | 1.2859× | 1.2470–1.3394× | 0.21× | FASTER |
| holdout | `hold.large.replace-callback.10` | Rust engine | 0.2358× | 0.2307–0.2440× | 0.70× | SLOWDOWN |
| holdout | `hold.large.replace-callback.11` | Python engine | 0.0748× | 0.0711–0.0772× | 3.34× | SLOWDOWN |
| holdout | `hold.large.replace-callback.11` | Native C engine | 1.3095× | 1.2940–1.3253× | 0.19× | FASTER |
| holdout | `hold.large.replace-callback.11` | Rust engine | 0.2311× | 0.2281–0.2346× | 0.82× | SLOWDOWN |
| holdout | `hold.large.replace-callback.12` | Python engine | 0.0767× | 0.0749–0.0781× | 3.07× | SLOWDOWN |
| holdout | `hold.large.replace-callback.12` | Native C engine | 1.1724× | 1.1602–1.1839× | 0.25× | FASTER |
| holdout | `hold.large.replace-callback.12` | Rust engine | 0.2163× | 0.2131–0.2193× | 0.53× | SLOWDOWN |
| holdout | `hold.large.replace-callback.13` | Python engine | 0.0788× | 0.0772–0.0816× | 3.13× | SLOWDOWN |
| holdout | `hold.large.replace-callback.13` | Native C engine | 1.2535× | 1.2317–1.2876× | 0.23× | FASTER |
| holdout | `hold.large.replace-callback.13` | Rust engine | 0.2256× | 0.2203–0.2327× | 0.60× | SLOWDOWN |
| holdout | `hold.large.replace-callback.14` | Python engine | 0.0837× | 0.0782–0.0920× | 3.23× | SLOWDOWN |
| holdout | `hold.large.replace-callback.14` | Native C engine | 1.3482× | 1.2937–1.4078× | 0.21× | FASTER |
| holdout | `hold.large.replace-callback.14` | Rust engine | 0.2483× | 0.2325–0.2713× | 0.70× | SLOWDOWN |
| holdout | `hold.large.replace-callback.15` | Python engine | 0.0730× | 0.0701–0.0751× | 3.24× | SLOWDOWN |
| holdout | `hold.large.replace-callback.15` | Native C engine | 1.1013× | 1.0156–1.1514× | 0.34× | FASTER |
| holdout | `hold.large.replace-callback.15` | Rust engine | 0.2017× | 0.1851–0.2116× | 0.71× | SLOWDOWN |
| holdout | `hold.large.replace-callback.16` | Python engine | 0.0859× | 0.0826–0.0904× | 3.07× | SLOWDOWN |
| holdout | `hold.large.replace-callback.16` | Native C engine | 1.2303× | 1.1823–1.2843× | 0.25× | FASTER |
| holdout | `hold.large.replace-callback.16` | Rust engine | 0.2395× | 0.2307–0.2520× | 0.53× | SLOWDOWN |
| holdout | `hold.large.replace-callback.17` | Python engine | 0.0806× | 0.0787–0.0831× | 3.13× | SLOWDOWN |
| holdout | `hold.large.replace-callback.17` | Native C engine | 1.2661× | 1.2365–1.3051× | 0.23× | FASTER |
| holdout | `hold.large.replace-callback.17` | Rust engine | 0.2258× | 0.2181–0.2344× | 0.60× | SLOWDOWN |
| holdout | `hold.large.replace-callback.18` | Python engine | 0.0725× | 0.0709–0.0741× | 3.31× | SLOWDOWN |
| holdout | `hold.large.replace-callback.18` | Native C engine | 1.1673× | 1.1482–1.1874× | 0.29× | FASTER |
| holdout | `hold.large.replace-callback.18` | Rust engine | 0.2014× | 0.1948–0.2067× | 0.62× | SLOWDOWN |
| holdout | `hold.large.replace-callback.19` | Python engine | 0.0774× | 0.0767–0.0780× | 3.34× | SLOWDOWN |
| holdout | `hold.large.replace-callback.19` | Native C engine | 1.3219× | 1.3139–1.3298× | 0.19× | FASTER |
| holdout | `hold.large.replace-callback.19` | Rust engine | 0.2336× | 0.2321–0.2350× | 0.82× | SLOWDOWN |
| holdout | `hold.large.replace-callback.20` | Python engine | 0.0856× | 0.0837–0.0887× | 3.07× | SLOWDOWN |
| holdout | `hold.large.replace-callback.20` | Native C engine | 1.2089× | 1.1771–1.2523× | 0.25× | FASTER |
| holdout | `hold.large.replace-callback.20` | Rust engine | 0.2371× | 0.2311–0.2452× | 0.53× | SLOWDOWN |
| holdout | `hold.large.replace-callback.21` | Python engine | 0.0696× | 0.0690–0.0701× | 3.31× | SLOWDOWN |
| holdout | `hold.large.replace-callback.21` | Native C engine | 1.1788× | 1.1658–1.1923× | 0.26× | FASTER |
| holdout | `hold.large.replace-callback.21` | Rust engine | 0.1997× | 0.1951–0.2026× | 0.56× | SLOWDOWN |
| holdout | `hold.large.replace-callback.22` | Python engine | 0.0774× | 0.0765–0.0781× | 3.23× | SLOWDOWN |
| holdout | `hold.large.replace-callback.22` | Native C engine | 1.2374× | 1.1550–1.2870× | 0.21× | FASTER |
| holdout | `hold.large.replace-callback.22` | Rust engine | 0.2305× | 0.2281–0.2323× | 0.70× | SLOWDOWN |
| holdout | `hold.large.replace-callback.23` | Python engine | 0.0765× | 0.0758–0.0771× | 3.34× | SLOWDOWN |
| holdout | `hold.large.replace-callback.23` | Native C engine | 1.2921× | 1.2826–1.3018× | 0.19× | FASTER |
| holdout | `hold.large.replace-callback.23` | Rust engine | 0.2294× | 0.2271–0.2313× | 0.82× | SLOWDOWN |
| holdout | `hold.large.replace-callback.24` | Python engine | 0.0776× | 0.0753–0.0805× | 3.06× | SLOWDOWN |
| holdout | `hold.large.replace-callback.24` | Native C engine | 1.1663× | 1.1468–1.1831× | 0.25× | FASTER |
| holdout | `hold.large.replace-callback.24` | Rust engine | 0.2202× | 0.2093–0.2401× | 0.53× | SLOWDOWN |
| holdout | `hold.large.replace-callback.25` | Python engine | 0.0805× | 0.0789–0.0830× | 3.13× | SLOWDOWN |
| holdout | `hold.large.replace-callback.25` | Native C engine | 1.2509× | 1.2258–1.2831× | 0.23× | FASTER |
| holdout | `hold.large.replace-callback.25` | Rust engine | 0.2253× | 0.2190–0.2338× | 0.60× | SLOWDOWN |
| holdout | `hold.large.replace-callback.26` | Python engine | 0.0785× | 0.0769–0.0812× | 3.22× | SLOWDOWN |
| holdout | `hold.large.replace-callback.26` | Native C engine | 1.2757× | 1.1868–1.3536× | 0.22× | FASTER |
| holdout | `hold.large.replace-callback.26` | Rust engine | 0.2269× | 0.2207–0.2359× | 0.71× | SLOWDOWN |
| holdout | `hold.large.replace-callback.27` | Python engine | 0.0749× | 0.0687–0.0847× | 3.21× | SLOWDOWN |
| holdout | `hold.large.replace-callback.27` | Native C engine | 1.1734× | 1.0826–1.3263× | 0.35× | FASTER |
| holdout | `hold.large.replace-callback.27` | Rust engine | 0.2099× | 0.2043–0.2166× | 0.73× | SLOWDOWN |
| holdout | `hold.large.replace-callback.28` | Python engine | 0.0851× | 0.0798–0.0915× | 3.07× | SLOWDOWN |
| holdout | `hold.large.replace-callback.28` | Native C engine | 1.2440× | 1.1860–1.3240× | 0.25× | FASTER |
| holdout | `hold.large.replace-callback.28` | Rust engine | 0.2331× | 0.2189–0.2497× | 0.53× | SLOWDOWN |
| holdout | `hold.large.replace-callback.29` | Python engine | 0.0799× | 0.0790–0.0807× | 3.13× | SLOWDOWN |
| holdout | `hold.large.replace-callback.29` | Native C engine | 1.2152× | 1.1677–1.2469× | 0.23× | FASTER |
| holdout | `hold.large.replace-callback.29` | Rust engine | 0.2332× | 0.2279–0.2374× | 0.60× | SLOWDOWN |
| holdout | `hold.large.replace-callback.30` | Python engine | 0.0718× | 0.0694–0.0741× | 3.31× | SLOWDOWN |
| holdout | `hold.large.replace-callback.30` | Native C engine | 1.1749× | 1.1395–1.2139× | 0.29× | FASTER |
| holdout | `hold.large.replace-callback.30` | Rust engine | 0.2050× | 0.1969–0.2119× | 0.62× | SLOWDOWN |
| holdout | `hold.large.replace-callback.31` | Python engine | 0.0771× | 0.0763–0.0780× | 3.33× | SLOWDOWN |
| holdout | `hold.large.replace-callback.31` | Native C engine | 1.2937× | 1.2782–1.3097× | 0.19× | FASTER |
| holdout | `hold.large.replace-callback.31` | Rust engine | 0.2342× | 0.2293–0.2384× | 0.82× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.00` | Python engine | 0.0275× | 0.0262–0.0289× | 5.90× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.00` | Native C engine | 2.6448× | 2.5318–2.7805× | 0.14× | FASTER |
| holdout | `hold.large.bytes-tokens.00` | Rust engine | 0.3301× | 0.3157–0.3464× | 1.01× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.01` | Python engine | 0.0250× | 0.0239–0.0266× | 6.50× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.01` | Native C engine | 2.8601× | 2.7282–3.0693× | 0.25× | FASTER |
| holdout | `hold.large.bytes-tokens.01` | Rust engine | 0.3410× | 0.3212–0.3643× | 1.54× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.02` | Python engine | 0.0221× | 0.0217–0.0227× | 7.33× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.02` | Native C engine | 2.9076× | 2.8474–2.9855× | 0.40× | FASTER |
| holdout | `hold.large.bytes-tokens.02` | Rust engine | 0.3427× | 0.3370–0.3515× | 2.49× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.03` | Python engine | 0.0211× | 0.0209–0.0213× | 8.28× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.03` | Native C engine | 2.7244× | 2.4418–2.9214× | 0.57× | FASTER |
| holdout | `hold.large.bytes-tokens.03` | Rust engine | 0.3467× | 0.3443–0.3491× | 3.43× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.04` | Python engine | 0.0281× | 0.0276–0.0287× | 5.90× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.04` | Native C engine | 2.6298× | 2.5845–2.6795× | 0.14× | FASTER |
| holdout | `hold.large.bytes-tokens.04` | Rust engine | 0.3052× | 0.2817–0.3222× | 1.09× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.05` | Python engine | 0.0246× | 0.0240–0.0254× | 6.49× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.05` | Native C engine | 2.7019× | 2.4904–2.8645× | 0.25× | FASTER |
| holdout | `hold.large.bytes-tokens.05` | Rust engine | 0.3255× | 0.3149–0.3399× | 1.67× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.06` | Python engine | 0.0231× | 0.0220–0.0249× | 7.33× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.06` | Native C engine | 3.0285× | 2.8696–3.2485× | 0.40× | FASTER |
| holdout | `hold.large.bytes-tokens.06` | Rust engine | 0.3596× | 0.3413–0.3829× | 2.49× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.07` | Python engine | 0.0215× | 0.0211–0.0219× | 8.28× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.07` | Native C engine | 2.8210× | 2.6010–2.9964× | 0.57× | FASTER |
| holdout | `hold.large.bytes-tokens.07` | Rust engine | 0.3487× | 0.3380–0.3589× | 3.43× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.08` | Python engine | 0.0277× | 0.0272–0.0283× | 5.89× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.08` | Native C engine | 2.6057× | 2.4573–2.7206× | 0.14× | FASTER |
| holdout | `hold.large.bytes-tokens.08` | Rust engine | 0.2967× | 0.2911–0.3042× | 1.16× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.09` | Python engine | 0.0240× | 0.0237–0.0242× | 6.48× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.09` | Native C engine | 2.7526× | 2.7214–2.7884× | 0.25× | FASTER |
| holdout | `hold.large.bytes-tokens.09` | Rust engine | 0.3038× | 0.2979–0.3087× | 1.80× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.10` | Python engine | 0.0221× | 0.0219–0.0225× | 7.30× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.10` | Native C engine | 2.9261× | 2.8718–2.9773× | 0.40× | FASTER |
| holdout | `hold.large.bytes-tokens.10` | Rust engine | 0.3135× | 0.3086–0.3192× | 2.70× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.11` | Python engine | 0.0209× | 0.0206–0.0211× | 8.28× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.11` | Native C engine | 2.8662× | 2.7908–2.9366× | 0.57× | FASTER |
| holdout | `hold.large.bytes-tokens.11` | Rust engine | 0.3450× | 0.3375–0.3505× | 3.43× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.12` | Python engine | 0.0296× | 0.0275–0.0339× | 5.90× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.12` | Native C engine | 2.8309× | 2.6391–3.2350× | 0.14× | FASTER |
| holdout | `hold.large.bytes-tokens.12` | Rust engine | 0.3416× | 0.3178–0.3921× | 1.09× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.13` | Python engine | 0.0241× | 0.0238–0.0244× | 6.48× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.13` | Native C engine | 2.7880× | 2.7521–2.8243× | 0.25× | FASTER |
| holdout | `hold.large.bytes-tokens.13` | Rust engine | 0.3054× | 0.3001–0.3103× | 1.80× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.14` | Python engine | 0.0217× | 0.0216–0.0220× | 7.33× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.14` | Native C engine | 2.8688× | 2.8294–2.9056× | 0.40× | FASTER |
| holdout | `hold.large.bytes-tokens.14` | Rust engine | 0.3318× | 0.3242–0.3385× | 2.49× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.15` | Python engine | 0.0210× | 0.0207–0.0212× | 8.25× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.15` | Native C engine | 2.9405× | 2.9007–2.9820× | 0.57× | FASTER |
| holdout | `hold.large.bytes-tokens.15` | Rust engine | 0.3192× | 0.3129–0.3244× | 3.72× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.16` | Python engine | 0.0274× | 0.0272–0.0276× | 5.89× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.16` | Native C engine | 2.6214× | 2.5736–2.6609× | 0.14× | FASTER |
| holdout | `hold.large.bytes-tokens.16` | Rust engine | 0.2933× | 0.2909–0.2957× | 1.16× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.17` | Python engine | 0.0241× | 0.0239–0.0243× | 6.49× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.17` | Native C engine | 2.7778× | 2.7588–2.7967× | 0.25× | FASTER |
| holdout | `hold.large.bytes-tokens.17` | Rust engine | 0.3141× | 0.3048–0.3234× | 1.67× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.18` | Python engine | 0.0220× | 0.0217–0.0223× | 7.33× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.18` | Native C engine | 2.7796× | 2.5143–2.9432× | 0.40× | FASTER |
| holdout | `hold.large.bytes-tokens.18` | Rust engine | 0.3381× | 0.3303–0.3444× | 2.49× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.19` | Python engine | 0.0208× | 0.0206–0.0209× | 8.28× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.19` | Native C engine | 2.8924× | 2.8404–2.9418× | 0.57× | FASTER |
| holdout | `hold.large.bytes-tokens.19` | Rust engine | 0.3408× | 0.3344–0.3462× | 3.43× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.20` | Python engine | 0.0277× | 0.0272–0.0285× | 5.90× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.20` | Native C engine | 2.5547× | 2.3460–2.7115× | 0.14× | FASTER |
| holdout | `hold.large.bytes-tokens.20` | Rust engine | 0.3171× | 0.3082–0.3281× | 1.09× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.21` | Python engine | 0.0244× | 0.0238–0.0254× | 6.49× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.21` | Native C engine | 2.6856× | 2.4521–2.8738× | 0.25× | FASTER |
| holdout | `hold.large.bytes-tokens.21` | Rust engine | 0.3299× | 0.3203–0.3445× | 1.67× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.22` | Python engine | 0.0227× | 0.0216–0.0241× | 7.30× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.22` | Native C engine | 3.0001× | 2.8759–3.1822× | 0.40× | FASTER |
| holdout | `hold.large.bytes-tokens.22` | Rust engine | 0.3225× | 0.3050–0.3437× | 2.70× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.23` | Python engine | 0.0210× | 0.0209–0.0211× | 8.28× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.23` | Native C engine | 2.9206× | 2.8859–2.9523× | 0.57× | FASTER |
| holdout | `hold.large.bytes-tokens.23` | Rust engine | 0.3416× | 0.3355–0.3467× | 3.43× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.24` | Python engine | 0.0278× | 0.0274–0.0285× | 5.89× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.24` | Native C engine | 2.6819× | 2.6392–2.7461× | 0.14× | FASTER |
| holdout | `hold.large.bytes-tokens.24` | Rust engine | 0.2968× | 0.2912–0.3038× | 1.16× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.25` | Python engine | 0.0241× | 0.0238–0.0244× | 6.48× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.25` | Native C engine | 2.6761× | 2.4667–2.8029× | 0.25× | FASTER |
| holdout | `hold.large.bytes-tokens.25` | Rust engine | 0.3057× | 0.3000–0.3111× | 1.80× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.26` | Python engine | 0.0228× | 0.0218–0.0241× | 7.30× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.26` | Native C engine | 2.9764× | 2.8497–3.1487× | 0.40× | FASTER |
| holdout | `hold.large.bytes-tokens.26` | Rust engine | 0.3211× | 0.3058–0.3409× | 2.70× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.27` | Python engine | 0.0215× | 0.0210–0.0225× | 8.25× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.27` | Native C engine | 2.9858× | 2.8960–3.1301× | 0.57× | FASTER |
| holdout | `hold.large.bytes-tokens.27` | Rust engine | 0.3349× | 0.3194–0.3551× | 3.72× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.28` | Python engine | 0.0284× | 0.0271–0.0298× | 5.89× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.28` | Native C engine | 2.6421× | 2.3890–2.8421× | 0.14× | FASTER |
| holdout | `hold.large.bytes-tokens.28` | Rust engine | 0.3167× | 0.3063–0.3306× | 1.16× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.29` | Python engine | 0.0239× | 0.0237–0.0241× | 6.48× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.29` | Native C engine | 2.7344× | 2.7041–2.7617× | 0.25× | FASTER |
| holdout | `hold.large.bytes-tokens.29` | Rust engine | 0.3136× | 0.3082–0.3185× | 1.80× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.30` | Python engine | 0.0217× | 0.0216–0.0219× | 7.30× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.30` | Native C engine | 2.8391× | 2.7968–2.8803× | 0.40× | FASTER |
| holdout | `hold.large.bytes-tokens.30` | Rust engine | 0.3272× | 0.3253–0.3292× | 2.70× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.31` | Python engine | 0.0197× | 0.0182–0.0208× | 8.25× | SLOWDOWN |
| holdout | `hold.large.bytes-tokens.31` | Native C engine | 2.8973× | 2.8485–2.9439× | 0.57× | FASTER |
| holdout | `hold.large.bytes-tokens.31` | Rust engine | 0.3304× | 0.3216–0.3367× | 3.72× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.00` | Python engine | 0.0321× | 0.0309–0.0336× | 3.98× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.00` | Native C engine | 1.9013× | 1.8276–1.9903× | 0.34× | FASTER |
| holdout | `hold.large.bytes-buffer.00` | Rust engine | 0.2069× | 0.1989–0.2160× | 0.67× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.01` | Python engine | 0.0254× | 0.0246–0.0267× | 4.48× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.01` | Native C engine | 1.7078× | 1.6591–1.7891× | 0.40× | FASTER |
| holdout | `hold.large.bytes-buffer.01` | Rust engine | 0.1937× | 0.1879–0.2021× | 0.56× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.02` | Python engine | 0.0216× | 0.0214–0.0219× | 5.39× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.02` | Native C engine | 1.5988× | 1.4980–1.6675× | 0.49× | FASTER |
| holdout | `hold.large.bytes-buffer.02` | Rust engine | 0.1724× | 0.1696–0.1754× | 0.68× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.03` | Python engine | 0.0203× | 0.0198–0.0212× | 7.11× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.03` | Native C engine | 1.5876× | 1.5358–1.6671× | 0.57× | FASTER |
| holdout | `hold.large.bytes-buffer.03` | Rust engine | 0.1749× | 0.1703–0.1825× | 0.62× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.04` | Python engine | 0.0284× | 0.0281–0.0286× | 3.98× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.04` | Native C engine | 1.6952× | 1.6139–1.7451× | 0.34× | FASTER |
| holdout | `hold.large.bytes-buffer.04` | Rust engine | 0.1864× | 0.1826–0.1894× | 0.67× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.05` | Python engine | 0.0238× | 0.0236–0.0241× | 4.49× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.05` | Native C engine | 1.6313× | 1.6092–1.6528× | 0.40× | FASTER |
| holdout | `hold.large.bytes-buffer.05` | Rust engine | 0.1853× | 0.1830–0.1873× | 0.56× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.06` | Python engine | 0.0218× | 0.0207–0.0233× | 5.39× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.06` | Native C engine | 1.4492× | 1.2233–1.6833× | 0.49× | FASTER |
| holdout | `hold.large.bytes-buffer.06` | Rust engine | 0.1637× | 0.1455–0.1804× | 0.68× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.07` | Python engine | 0.0205× | 0.0194–0.0223× | 7.11× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.07` | Native C engine | 1.6260× | 1.5524–1.7511× | 0.57× | FASTER |
| holdout | `hold.large.bytes-buffer.07` | Rust engine | 0.1786× | 0.1696–0.1946× | 0.62× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.08` | Python engine | 0.0278× | 0.0276–0.0280× | 3.98× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.08` | Native C engine | 1.6538× | 1.5796–1.7010× | 0.34× | FASTER |
| holdout | `hold.large.bytes-buffer.08` | Rust engine | 0.1857× | 0.1844–0.1875× | 0.67× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.09` | Python engine | 0.0240× | 0.0236–0.0243× | 4.49× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.09` | Native C engine | 1.6474× | 1.6121–1.6802× | 0.40× | FASTER |
| holdout | `hold.large.bytes-buffer.09` | Rust engine | 0.1854× | 0.1822–0.1886× | 0.56× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.10` | Python engine | 0.0212× | 0.0211–0.0214× | 5.39× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.10` | Native C engine | 1.6076× | 1.5839–1.6296× | 0.49× | FASTER |
| holdout | `hold.large.bytes-buffer.10` | Rust engine | 0.1695× | 0.1671–0.1718× | 0.68× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.11` | Python engine | 0.0204× | 0.0197–0.0216× | 7.11× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.11` | Native C engine | 1.5512× | 1.4354–1.6760× | 0.57× | FASTER |
| holdout | `hold.large.bytes-buffer.11` | Rust engine | 0.1749× | 0.1691–0.1857× | 0.62× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.12` | Python engine | 0.0273× | 0.0271–0.0276× | 3.98× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.12` | Native C engine | 1.6680× | 1.6533–1.6849× | 0.34× | FASTER |
| holdout | `hold.large.bytes-buffer.12` | Rust engine | 0.1838× | 0.1816–0.1861× | 0.67× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.13` | Python engine | 0.0233× | 0.0231–0.0235× | 4.49× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.13` | Native C engine | 1.6159× | 1.5994–1.6324× | 0.40× | FASTER |
| holdout | `hold.large.bytes-buffer.13` | Rust engine | 0.1806× | 0.1776–0.1834× | 0.56× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.14` | Python engine | 0.0206× | 0.0193–0.0215× | 5.39× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.14` | Native C engine | 1.5641× | 1.4044–1.6597× | 0.49× | FASTER |
| holdout | `hold.large.bytes-buffer.14` | Rust engine | 0.1628× | 0.1506–0.1725× | 0.68× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.15` | Python engine | 0.0194× | 0.0184–0.0201× | 7.11× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.15` | Native C engine | 1.5485× | 1.5189–1.5753× | 0.57× | FASTER |
| holdout | `hold.large.bytes-buffer.15` | Rust engine | 0.1703× | 0.1682–0.1723× | 0.62× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.16` | Python engine | 0.0269× | 0.0267–0.0272× | 3.98× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.16` | Native C engine | 1.6621× | 1.6423–1.6839× | 0.34× | FASTER |
| holdout | `hold.large.bytes-buffer.16` | Rust engine | 0.1810× | 0.1778–0.1840× | 0.67× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.17` | Python engine | 0.0243× | 0.0236–0.0257× | 4.49× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.17` | Native C engine | 1.6770× | 1.6178–1.7833× | 0.40× | FASTER |
| holdout | `hold.large.bytes-buffer.17` | Rust engine | 0.1876× | 0.1812–0.1990× | 0.56× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.18` | Python engine | 0.0217× | 0.0213–0.0225× | 5.39× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.18` | Native C engine | 1.6689× | 1.6259–1.7364× | 0.49× | FASTER |
| holdout | `hold.large.bytes-buffer.18` | Rust engine | 0.1738× | 0.1696–0.1801× | 0.68× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.19` | Python engine | 0.0209× | 0.0203–0.0218× | 7.11× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.19` | Native C engine | 1.6475× | 1.5934–1.7197× | 0.57× | FASTER |
| holdout | `hold.large.bytes-buffer.19` | Rust engine | 0.1783× | 0.1730–0.1857× | 0.62× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.20` | Python engine | 0.0296× | 0.0294–0.0299× | 3.98× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.20` | Native C engine | 1.7876× | 1.7705–1.8035× | 0.34× | FASTER |
| holdout | `hold.large.bytes-buffer.20` | Rust engine | 0.1957× | 0.1926–0.1983× | 0.67× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.21` | Python engine | 0.0244× | 0.0241–0.0247× | 4.49× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.21` | Native C engine | 1.6563× | 1.6282–1.6858× | 0.40× | FASTER |
| holdout | `hold.large.bytes-buffer.21` | Rust engine | 0.1882× | 0.1848–0.1914× | 0.56× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.22` | Python engine | 0.0214× | 0.0213–0.0216× | 5.39× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.22` | Native C engine | 1.6159× | 1.5928–1.6373× | 0.49× | FASTER |
| holdout | `hold.large.bytes-buffer.22` | Rust engine | 0.1701× | 0.1675–0.1720× | 0.68× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.23` | Python engine | 0.0212× | 0.0206–0.0220× | 7.11× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.23` | Native C engine | 1.6633× | 1.6237–1.7173× | 0.57× | FASTER |
| holdout | `hold.large.bytes-buffer.23` | Rust engine | 0.1821× | 0.1766–0.1899× | 0.62× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.24` | Python engine | 0.0278× | 0.0276–0.0279× | 3.98× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.24` | Native C engine | 1.7002× | 1.6879–1.7116× | 0.34× | FASTER |
| holdout | `hold.large.bytes-buffer.24` | Rust engine | 0.1857× | 0.1845–0.1869× | 0.67× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.25` | Python engine | 0.0237× | 0.0235–0.0239× | 4.49× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.25` | Native C engine | 1.6259× | 1.6049–1.6485× | 0.40× | FASTER |
| holdout | `hold.large.bytes-buffer.25` | Rust engine | 0.1836× | 0.1806–0.1861× | 0.56× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.26` | Python engine | 0.0218× | 0.0213–0.0226× | 5.39× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.26` | Native C engine | 1.6580× | 1.6064–1.7300× | 0.49× | FASTER |
| holdout | `hold.large.bytes-buffer.26` | Rust engine | 0.1733× | 0.1685–0.1799× | 0.68× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.27` | Python engine | 0.0198× | 0.0196–0.0200× | 7.24× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.27` | Native C engine | 1.6534× | 1.6328–1.6733× | 0.57× | FASTER |
| holdout | `hold.large.bytes-buffer.27` | Rust engine | 0.1732× | 0.1716–0.1748× | 0.62× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.28` | Python engine | 0.0268× | 0.0266–0.0269× | 3.99× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.28` | Native C engine | 1.6536× | 1.5696–1.7069× | 0.34× | FASTER |
| holdout | `hold.large.bytes-buffer.28` | Rust engine | 0.1831× | 0.1819–0.1842× | 0.67× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.29` | Python engine | 0.0239× | 0.0232–0.0250× | 4.51× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.29` | Native C engine | 1.6929× | 1.6397–1.7747× | 0.40× | FASTER |
| holdout | `hold.large.bytes-buffer.29` | Rust engine | 0.1790× | 0.1659–0.1887× | 0.56× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.30` | Python engine | 0.0206× | 0.0204–0.0207× | 5.43× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.30` | Native C engine | 1.5795× | 1.4808–1.6412× | 0.49× | FASTER |
| holdout | `hold.large.bytes-buffer.30` | Rust engine | 0.1677× | 0.1667–0.1687× | 0.68× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.31` | Python engine | 0.0194× | 0.0191–0.0199× | 7.24× | SLOWDOWN |
| holdout | `hold.large.bytes-buffer.31` | Native C engine | 1.5367× | 1.4585–1.6018× | 0.57× | FASTER |
| holdout | `hold.large.bytes-buffer.31` | Rust engine | 0.1696× | 0.1678–0.1714× | 0.62× | SLOWDOWN |
| holdout | `hold.large.unicode-words.00` | Python engine | 0.0219× | 0.0216–0.0221× | 6.83× | SLOWDOWN |
| holdout | `hold.large.unicode-words.00` | Native C engine | 1.0677× | 1.0560–1.0817× | 0.25× | FASTER |
| holdout | `hold.large.unicode-words.00` | Rust engine | 0.1099× | 0.1086–0.1115× | 0.91× | SLOWDOWN |
| holdout | `hold.large.unicode-words.01` | Python engine | 0.0220× | 0.0217–0.0222× | 6.63× | SLOWDOWN |
| holdout | `hold.large.unicode-words.01` | Native C engine | 1.0635× | 1.0538–1.0749× | 0.40× | FASTER |
| holdout | `hold.large.unicode-words.01` | Rust engine | 0.0915× | 0.0906–0.0925× | 1.03× | SLOWDOWN |
| holdout | `hold.large.unicode-words.02` | Python engine | 0.0227× | 0.0224–0.0233× | 6.49× | SLOWDOWN |
| holdout | `hold.large.unicode-words.02` | Native C engine | 1.0890× | 1.0736–1.1153× | 0.56× | FASTER |
| holdout | `hold.large.unicode-words.02` | Rust engine | 0.0658× | 0.0644–0.0676× | 1.20× | SLOWDOWN |
| holdout | `hold.large.unicode-words.03` | Python engine | 0.0220× | 0.0209–0.0228× | 6.39× | SLOWDOWN |
| holdout | `hold.large.unicode-words.03` | Native C engine | 1.0652× | 1.0240–1.0912× | 0.71× | FASTER |
| holdout | `hold.large.unicode-words.03` | Rust engine | 0.0439× | 0.0435–0.0443× | 1.33× | SLOWDOWN |
| holdout | `hold.large.unicode-words.04` | Python engine | 0.0228× | 0.0211–0.0251× | 6.82× | SLOWDOWN |
| holdout | `hold.large.unicode-words.04` | Native C engine | 1.0872× | 0.9367–1.2501× | 0.25× | — |
| holdout | `hold.large.unicode-words.04` | Rust engine | 0.1135× | 0.1049–0.1264× | 0.92× | SLOWDOWN |
| holdout | `hold.large.unicode-words.05` | Python engine | 0.0222× | 0.0220–0.0223× | 6.61× | SLOWDOWN |
| holdout | `hold.large.unicode-words.05` | Native C engine | 1.0597× | 1.0539–1.0654× | 0.40× | FASTER |
| holdout | `hold.large.unicode-words.05` | Rust engine | 0.0883× | 0.0878–0.0888× | 1.05× | SLOWDOWN |
| holdout | `hold.large.unicode-words.06` | Python engine | 0.0216× | 0.0214–0.0218× | 6.50× | SLOWDOWN |
| holdout | `hold.large.unicode-words.06` | Native C engine | 1.0575× | 1.0491–1.0652× | 0.56× | FASTER |
| holdout | `hold.large.unicode-words.06` | Rust engine | 0.0651× | 0.0645–0.0655× | 1.19× | SLOWDOWN |
| holdout | `hold.large.unicode-words.07` | Python engine | 0.0219× | 0.0216–0.0221× | 6.39× | SLOWDOWN |
| holdout | `hold.large.unicode-words.07` | Native C engine | 1.0624× | 1.0572–1.0679× | 0.71× | FASTER |
| holdout | `hold.large.unicode-words.07` | Rust engine | 0.0430× | 0.0428–0.0432× | 1.33× | SLOWDOWN |
| holdout | `hold.large.unicode-words.08` | Python engine | 0.0214× | 0.0210–0.0220× | 6.82× | SLOWDOWN |
| holdout | `hold.large.unicode-words.08` | Native C engine | 1.0247× | 1.0011–1.0559× | 0.25× | FASTER |
| holdout | `hold.large.unicode-words.08` | Rust engine | 0.1049× | 0.1029–0.1076× | 0.92× | SLOWDOWN |
| holdout | `hold.large.unicode-words.09` | Python engine | 0.0222× | 0.0216–0.0230× | 6.61× | SLOWDOWN |
| holdout | `hold.large.unicode-words.09` | Native C engine | 1.0532× | 1.0184–1.0930× | 0.40× | FASTER |
| holdout | `hold.large.unicode-words.09` | Rust engine | 0.0880× | 0.0848–0.0915× | 1.05× | SLOWDOWN |
| holdout | `hold.large.unicode-words.10` | Python engine | 0.0215× | 0.0213–0.0216× | 6.50× | SLOWDOWN |
| holdout | `hold.large.unicode-words.10` | Native C engine | 1.0529× | 1.0447–1.0634× | 0.56× | FASTER |
| holdout | `hold.large.unicode-words.10` | Rust engine | 0.0651× | 0.0647–0.0655× | 1.19× | SLOWDOWN |
| holdout | `hold.large.unicode-words.11` | Python engine | 0.0225× | 0.0222–0.0227× | 6.38× | SLOWDOWN |
| holdout | `hold.large.unicode-words.11` | Native C engine | 1.0722× | 1.0271–1.1011× | 0.71× | FASTER |
| holdout | `hold.large.unicode-words.11` | Rust engine | 0.0428× | 0.0423–0.0434× | 1.35× | SLOWDOWN |
| holdout | `hold.large.unicode-words.12` | Python engine | 0.0217× | 0.0212–0.0222× | 6.82× | SLOWDOWN |
| holdout | `hold.large.unicode-words.12` | Native C engine | 1.0525× | 1.0352–1.0758× | 0.25× | FASTER |
| holdout | `hold.large.unicode-words.12` | Rust engine | 0.1082× | 0.1063–0.1105× | 0.92× | SLOWDOWN |
| holdout | `hold.large.unicode-words.13` | Python engine | 0.0221× | 0.0218–0.0227× | 6.62× | SLOWDOWN |
| holdout | `hold.large.unicode-words.13` | Native C engine | 1.0765× | 1.0579–1.1059× | 0.40× | FASTER |
| holdout | `hold.large.unicode-words.13` | Rust engine | 0.0910× | 0.0891–0.0937× | 1.04× | SLOWDOWN |
| holdout | `hold.large.unicode-words.14` | Python engine | 0.0221× | 0.0213–0.0233× | 6.50× | SLOWDOWN |
| holdout | `hold.large.unicode-words.14` | Native C engine | 1.0535× | 0.9930–1.1196× | 0.56× | — |
| holdout | `hold.large.unicode-words.14` | Rust engine | 0.0663× | 0.0639–0.0699× | 1.19× | SLOWDOWN |
| holdout | `hold.large.unicode-words.15` | Python engine | 0.0227× | 0.0218–0.0240× | 6.39× | SLOWDOWN |
| holdout | `hold.large.unicode-words.15` | Native C engine | 1.0992× | 1.0825–1.1245× | 0.71× | FASTER |
| holdout | `hold.large.unicode-words.15` | Rust engine | 0.0449× | 0.0437–0.0469× | 1.33× | SLOWDOWN |
| holdout | `hold.large.unicode-words.16` | Python engine | 0.0246× | 0.0222–0.0277× | 6.82× | SLOWDOWN |
| holdout | `hold.large.unicode-words.16` | Native C engine | 1.1192× | 0.9743–1.3016× | 0.25× | — |
| holdout | `hold.large.unicode-words.16` | Rust engine | 0.1196× | 0.1088–0.1344× | 0.92× | SLOWDOWN |
| holdout | `hold.large.unicode-words.17` | Python engine | 0.0218× | 0.0208–0.0228× | 6.61× | SLOWDOWN |
| holdout | `hold.large.unicode-words.17` | Native C engine | 1.0925× | 1.0593–1.1342× | 0.40× | FASTER |
| holdout | `hold.large.unicode-words.17` | Rust engine | 0.0879× | 0.0833–0.0930× | 1.05× | SLOWDOWN |
| holdout | `hold.large.unicode-words.18` | Python engine | 0.0237× | 0.0222–0.0257× | 6.49× | SLOWDOWN |
| holdout | `hold.large.unicode-words.18` | Native C engine | 1.0579× | 0.9366–1.1944× | 0.56× | — |
| holdout | `hold.large.unicode-words.18` | Rust engine | 0.0700× | 0.0654–0.0757× | 1.20× | SLOWDOWN |
| holdout | `hold.large.unicode-words.19` | Python engine | 0.0227× | 0.0206–0.0256× | 6.39× | SLOWDOWN |
| holdout | `hold.large.unicode-words.19` | Native C engine | 1.1008× | 1.0680–1.1295× | 0.71× | FASTER |
| holdout | `hold.large.unicode-words.19` | Rust engine | 0.0480× | 0.0436–0.0550× | 1.33× | SLOWDOWN |
| holdout | `hold.large.unicode-words.20` | Python engine | 0.0215× | 0.0204–0.0227× | 6.82× | SLOWDOWN |
| holdout | `hold.large.unicode-words.20` | Native C engine | 1.0486× | 1.0043–1.0970× | 0.25× | FASTER |
| holdout | `hold.large.unicode-words.20` | Rust engine | 0.1090× | 0.1067–0.1130× | 0.92× | SLOWDOWN |
| holdout | `hold.large.unicode-words.21` | Python engine | 0.0238× | 0.0225–0.0251× | 6.62× | SLOWDOWN |
| holdout | `hold.large.unicode-words.21` | Native C engine | 1.0559× | 0.9543–1.1437× | 0.40× | — |
| holdout | `hold.large.unicode-words.21` | Rust engine | 0.0984× | 0.0931–0.1039× | 1.04× | SLOWDOWN |
| holdout | `hold.large.unicode-words.22` | Python engine | 0.0223× | 0.0220–0.0226× | 6.49× | SLOWDOWN |
| holdout | `hold.large.unicode-words.22` | Native C engine | 1.0736× | 1.0601–1.0863× | 0.56× | FASTER |
| holdout | `hold.large.unicode-words.22` | Rust engine | 0.0650× | 0.0640–0.0659× | 1.20× | SLOWDOWN |
| holdout | `hold.large.unicode-words.23` | Python engine | 0.0228× | 0.0226–0.0230× | 6.38× | SLOWDOWN |
| holdout | `hold.large.unicode-words.23` | Native C engine | 1.1001× | 1.0874–1.1147× | 0.71× | FASTER |
| holdout | `hold.large.unicode-words.23` | Rust engine | 0.0435× | 0.0430–0.0439× | 1.35× | SLOWDOWN |
| holdout | `hold.large.unicode-words.24` | Python engine | 0.0217× | 0.0215–0.0220× | 6.82× | SLOWDOWN |
| holdout | `hold.large.unicode-words.24` | Native C engine | 1.0283× | 0.9940–1.0518× | 0.25× | — |
| holdout | `hold.large.unicode-words.24` | Rust engine | 0.1065× | 0.1054–0.1078× | 0.92× | SLOWDOWN |
| holdout | `hold.large.unicode-words.25` | Python engine | 0.0228× | 0.0221–0.0237× | 6.61× | SLOWDOWN |
| holdout | `hold.large.unicode-words.25` | Native C engine | 1.0862× | 1.0539–1.1325× | 0.40× | FASTER |
| holdout | `hold.large.unicode-words.25` | Rust engine | 0.0922× | 0.0897–0.0960× | 1.05× | SLOWDOWN |
| holdout | `hold.large.unicode-words.26` | Python engine | 0.0220× | 0.0216–0.0225× | 6.50× | SLOWDOWN |
| holdout | `hold.large.unicode-words.26` | Native C engine | 1.0696× | 1.0473–1.0902× | 0.56× | FASTER |
| holdout | `hold.large.unicode-words.26` | Rust engine | 0.0662× | 0.0648–0.0676× | 1.19× | SLOWDOWN |
| holdout | `hold.large.unicode-words.27` | Python engine | 0.0226× | 0.0223–0.0228× | 6.37× | SLOWDOWN |
| holdout | `hold.large.unicode-words.27` | Native C engine | 1.0892× | 1.0797–1.0984× | 0.71× | FASTER |
| holdout | `hold.large.unicode-words.27` | Rust engine | 0.0429× | 0.0426–0.0432× | 1.35× | SLOWDOWN |
| holdout | `hold.large.unicode-words.28` | Python engine | 0.0224× | 0.0222–0.0226× | 6.81× | SLOWDOWN |
| holdout | `hold.large.unicode-words.28` | Native C engine | 1.0108× | 0.9220–1.0632× | 0.25× | — |
| holdout | `hold.large.unicode-words.28` | Rust engine | 0.1053× | 0.1030–0.1074× | 0.93× | SLOWDOWN |
| holdout | `hold.large.unicode-words.29` | Python engine | 0.0226× | 0.0223–0.0230× | 6.61× | SLOWDOWN |
| holdout | `hold.large.unicode-words.29` | Native C engine | 1.0897× | 1.0801–1.1013× | 0.40× | FASTER |
| holdout | `hold.large.unicode-words.29` | Rust engine | 0.0908× | 0.0900–0.0917× | 1.05× | SLOWDOWN |
| holdout | `hold.large.unicode-words.30` | Python engine | 0.0224× | 0.0214–0.0237× | 6.49× | SLOWDOWN |
| holdout | `hold.large.unicode-words.30` | Native C engine | 1.0755× | 1.0384–1.1221× | 0.56× | FASTER |
| holdout | `hold.large.unicode-words.30` | Rust engine | 0.0657× | 0.0628–0.0691× | 1.20× | SLOWDOWN |
| holdout | `hold.large.unicode-words.31` | Python engine | 0.0230× | 0.0225–0.0238× | 6.37× | SLOWDOWN |
| holdout | `hold.large.unicode-words.31` | Native C engine | 1.1012× | 1.0526–1.1641× | 0.71× | FASTER |
| holdout | `hold.large.unicode-words.31` | Rust engine | 0.0438× | 0.0427–0.0459× | 1.35× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.00` | Python engine | 0.0305× | 0.0303–0.0306× | 4.36× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.00` | Native C engine | 1.4662× | 1.4523–1.4792× | 0.22× | FASTER |
| holdout | `hold.large.unicode-casefold.00` | Rust engine | 0.1040× | 0.1031–0.1050× | 0.98× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.01` | Python engine | 0.0314× | 0.0305–0.0326× | 4.75× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.01` | Native C engine | 1.5138× | 1.4117–1.5949× | 0.36× | FASTER |
| holdout | `hold.large.unicode-casefold.01` | Rust engine | 0.0873× | 0.0850–0.0905× | 1.14× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.02` | Python engine | 0.0298× | 0.0286–0.0311× | 5.34× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.02` | Native C engine | 1.4667× | 1.4106–1.5270× | 0.52× | FASTER |
| holdout | `hold.large.unicode-casefold.02` | Rust engine | 0.0550× | 0.0533–0.0573× | 1.35× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.03` | Python engine | 0.0330× | 0.0313–0.0363× | 5.79× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.03` | Native C engine | 1.6405× | 1.5334–1.8130× | 0.69× | FASTER |
| holdout | `hold.large.unicode-casefold.03` | Rust engine | 0.0396× | 0.0377–0.0429× | 1.55× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.04` | Python engine | 0.0298× | 0.0281–0.0333× | 4.36× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.04` | Native C engine | 1.5011× | 1.3856–1.6928× | 0.22× | FASTER |
| holdout | `hold.large.unicode-casefold.04` | Rust engine | 0.1083× | 0.0993–0.1231× | 0.97× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.05` | Python engine | 0.0317× | 0.0310–0.0325× | 4.74× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.05` | Native C engine | 1.5777× | 1.5480–1.6225× | 0.37× | FASTER |
| holdout | `hold.large.unicode-casefold.05` | Rust engine | 0.0845× | 0.0826–0.0870× | 1.16× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.06` | Python engine | 0.0287× | 0.0283–0.0293× | 5.34× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.06` | Native C engine | 1.4459× | 1.3873–1.4950× | 0.52× | FASTER |
| holdout | `hold.large.unicode-casefold.06` | Rust engine | 0.0545× | 0.0536–0.0556× | 1.35× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.07` | Python engine | 0.0344× | 0.0324–0.0372× | 5.79× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.07` | Native C engine | 1.6426× | 1.5278–1.8127× | 0.69× | FASTER |
| holdout | `hold.large.unicode-casefold.07` | Rust engine | 0.0435× | 0.0396–0.0488× | 1.55× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.08` | Python engine | 0.0285× | 0.0283–0.0286× | 4.36× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.08` | Native C engine | 1.4510× | 1.4361–1.4671× | 0.22× | FASTER |
| holdout | `hold.large.unicode-casefold.08` | Rust engine | 0.1047× | 0.1035–0.1058× | 0.97× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.09` | Python engine | 0.0298× | 0.0290–0.0303× | 4.75× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.09` | Native C engine | 1.5411× | 1.5233–1.5587× | 0.36× | FASTER |
| holdout | `hold.large.unicode-casefold.09` | Rust engine | 0.0832× | 0.0819–0.0845× | 1.14× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.10` | Python engine | 0.0293× | 0.0287–0.0301× | 5.34× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.10` | Native C engine | 1.4895× | 1.4554–1.5303× | 0.52× | FASTER |
| holdout | `hold.large.unicode-casefold.10` | Rust engine | 0.0549× | 0.0536–0.0564× | 1.35× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.11` | Python engine | 0.0324× | 0.0319–0.0328× | 5.77× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.11` | Native C engine | 1.4977× | 1.3480–1.6029× | 0.69× | FASTER |
| holdout | `hold.large.unicode-casefold.11` | Rust engine | 0.0365× | 0.0359–0.0370× | 1.58× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.12` | Python engine | 0.0292× | 0.0284–0.0302× | 4.36× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.12` | Native C engine | 1.4892× | 1.4544–1.5313× | 0.22× | FASTER |
| holdout | `hold.large.unicode-casefold.12` | Rust engine | 0.1077× | 0.1050–0.1111× | 0.97× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.13` | Python engine | 0.0302× | 0.0300–0.0304× | 4.75× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.13` | Native C engine | 1.5442× | 1.5325–1.5550× | 0.36× | FASTER |
| holdout | `hold.large.unicode-casefold.13` | Rust engine | 0.0847× | 0.0837–0.0857× | 1.14× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.14` | Python engine | 0.0298× | 0.0290–0.0307× | 5.34× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.14` | Native C engine | 1.5124× | 1.4636–1.5633× | 0.52× | FASTER |
| holdout | `hold.large.unicode-casefold.14` | Rust engine | 0.0566× | 0.0552–0.0581× | 1.35× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.15` | Python engine | 0.0325× | 0.0316–0.0338× | 5.79× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.15` | Native C engine | 1.5226× | 1.3571–1.6636× | 0.69× | FASTER |
| holdout | `hold.large.unicode-casefold.15` | Rust engine | 0.0390× | 0.0380–0.0405× | 1.55× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.16` | Python engine | 0.0288× | 0.0286–0.0290× | 4.36× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.16` | Native C engine | 1.4682× | 1.4537–1.4814× | 0.22× | FASTER |
| holdout | `hold.large.unicode-casefold.16` | Rust engine | 0.1067× | 0.1059–0.1074× | 0.97× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.17` | Python engine | 0.0303× | 0.0302–0.0305× | 4.75× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.17` | Native C engine | 1.5459× | 1.5331–1.5565× | 0.36× | FASTER |
| holdout | `hold.large.unicode-casefold.17` | Rust engine | 0.0831× | 0.0802–0.0850× | 1.14× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.18` | Python engine | 0.0309× | 0.0301–0.0317× | 5.32× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.18` | Native C engine | 1.4317× | 1.3016–1.5333× | 0.52× | FASTER |
| holdout | `hold.large.unicode-casefold.18` | Rust engine | 0.0545× | 0.0532–0.0560× | 1.38× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.19` | Python engine | 0.0329× | 0.0319–0.0349× | 5.79× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.19` | Native C engine | 1.6408× | 1.5885–1.7355× | 0.69× | FASTER |
| holdout | `hold.large.unicode-casefold.19` | Rust engine | 0.0391× | 0.0378–0.0414× | 1.55× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.20` | Python engine | 0.0305× | 0.0301–0.0312× | 4.36× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.20` | Native C engine | 1.4738× | 1.4549–1.4972× | 0.22× | FASTER |
| holdout | `hold.large.unicode-casefold.20` | Rust engine | 0.1041× | 0.1012–0.1070× | 0.98× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.21` | Python engine | 0.0300× | 0.0295–0.0304× | 4.75× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.21` | Native C engine | 1.5651× | 1.5370–1.6041× | 0.36× | FASTER |
| holdout | `hold.large.unicode-casefold.21` | Rust engine | 0.0844× | 0.0838–0.0851× | 1.14× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.22` | Python engine | 0.0303× | 0.0291–0.0319× | 5.34× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.22` | Native C engine | 1.5418× | 1.4779–1.6133× | 0.52× | FASTER |
| holdout | `hold.large.unicode-casefold.22` | Rust engine | 0.0576× | 0.0554–0.0606× | 1.35× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.23` | Python engine | 0.0316× | 0.0310–0.0320× | 5.79× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.23` | Native C engine | 1.5739× | 1.5298–1.5990× | 0.69× | FASTER |
| holdout | `hold.large.unicode-casefold.23` | Rust engine | 0.0374× | 0.0361–0.0383× | 1.55× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.24` | Python engine | 0.0290× | 0.0281–0.0305× | 4.36× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.24` | Native C engine | 1.4640× | 1.3883–1.5506× | 0.22× | FASTER |
| holdout | `hold.large.unicode-casefold.24` | Rust engine | 0.1064× | 0.1028–0.1120× | 0.97× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.25` | Python engine | 0.0299× | 0.0296–0.0301× | 4.75× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.25` | Native C engine | 1.4965× | 1.4013–1.5506× | 0.36× | FASTER |
| holdout | `hold.large.unicode-casefold.25` | Rust engine | 0.0845× | 0.0840–0.0851× | 1.14× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.26` | Python engine | 0.0298× | 0.0288–0.0309× | 5.34× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.26` | Native C engine | 1.5058× | 1.4576–1.5604× | 0.52× | FASTER |
| holdout | `hold.large.unicode-casefold.26` | Rust engine | 0.0566× | 0.0549–0.0588× | 1.35× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.27` | Python engine | 0.0322× | 0.0320–0.0327× | 5.79× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.27` | Native C engine | 1.6043× | 1.5904–1.6216× | 0.69× | FASTER |
| holdout | `hold.large.unicode-casefold.27` | Rust engine | 0.0380× | 0.0376–0.0385× | 1.55× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.28` | Python engine | 0.0287× | 0.0285–0.0289× | 4.36× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.28` | Native C engine | 1.4505× | 1.4290–1.4738× | 0.22× | FASTER |
| holdout | `hold.large.unicode-casefold.28` | Rust engine | 0.1061× | 0.1052–0.1071× | 0.97× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.29` | Python engine | 0.0306× | 0.0303–0.0308× | 4.75× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.29` | Native C engine | 1.5439× | 1.5252–1.5620× | 0.36× | FASTER |
| holdout | `hold.large.unicode-casefold.29` | Rust engine | 0.0851× | 0.0843–0.0859× | 1.14× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.30` | Python engine | 0.0299× | 0.0292–0.0307× | 5.34× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.30` | Native C engine | 1.5027× | 1.4658–1.5424× | 0.52× | FASTER |
| holdout | `hold.large.unicode-casefold.30` | Rust engine | 0.0561× | 0.0549–0.0573× | 1.35× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.31` | Python engine | 0.0320× | 0.0317–0.0325× | 5.79× | SLOWDOWN |
| holdout | `hold.large.unicode-casefold.31` | Native C engine | 1.6036× | 1.5926–1.6179× | 0.69× | FASTER |
| holdout | `hold.large.unicode-casefold.31` | Rust engine | 0.0382× | 0.0379–0.0385× | 1.55× | SLOWDOWN |
| holdout | `hold.large.cold-compile.00` | Python engine | 1.8798× | 1.7277–2.1620× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.00` | Native C engine | 1.5415× | 1.4258–1.7735× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.00` | Rust engine | 1.4123× | 1.3163–1.6073× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.01` | Python engine | 1.7929× | 1.7737–1.8071× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.01` | Native C engine | 1.4461× | 1.4284–1.4615× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.01` | Rust engine | 1.3123× | 1.2931–1.3298× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.02` | Python engine | 1.7893× | 1.7654–1.8100× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.02` | Native C engine | 1.4503× | 1.4371–1.4639× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.02` | Rust engine | 1.3017× | 1.2842–1.3195× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.03` | Python engine | 1.7766× | 1.7556–1.7965× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.03` | Native C engine | 1.4381× | 1.4157–1.4582× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.03` | Rust engine | 1.3076× | 1.2950–1.3192× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.04` | Python engine | 1.7909× | 1.7592–1.8197× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.04` | Native C engine | 1.4464× | 1.4247–1.4683× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.04` | Rust engine | 1.3072× | 1.2936–1.3220× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.05` | Python engine | 1.7488× | 1.7240–1.7741× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.05` | Native C engine | 1.4262× | 1.4101–1.4434× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.05` | Rust engine | 1.2967× | 1.2864–1.3069× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.06` | Python engine | 1.7692× | 1.7523–1.7861× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.06` | Native C engine | 1.4223× | 1.4093–1.4351× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.06` | Rust engine | 1.2834× | 1.2676–1.2980× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.07` | Python engine | 1.7735× | 1.7561–1.7901× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.07` | Native C engine | 1.4242× | 1.4130–1.4349× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.07` | Rust engine | 1.2926× | 1.2779–1.3053× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.08` | Python engine | 1.8113× | 1.7849–1.8361× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.08` | Native C engine | 1.4429× | 1.4166–1.4696× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.08` | Rust engine | 1.3333× | 1.3160–1.3492× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.09` | Python engine | 1.7931× | 1.7721–1.8139× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.09` | Native C engine | 1.4403× | 1.4172–1.4606× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.09` | Rust engine | 1.3188× | 1.3033–1.3329× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.10` | Python engine | 1.8003× | 1.7781–1.8226× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.10` | Native C engine | 1.4461× | 1.4279–1.4651× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.10` | Rust engine | 1.3147× | 1.3015–1.3285× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.11` | Python engine | 1.7945× | 1.7787–1.8085× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.11` | Native C engine | 1.4367× | 1.4276–1.4465× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.11` | Rust engine | 1.3082× | 1.2961–1.3202× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.12` | Python engine | 1.7835× | 1.7547–1.8119× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.12` | Native C engine | 1.4331× | 1.4071–1.4597× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.12` | Rust engine | 1.3086× | 1.2943–1.3251× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.13` | Python engine | 1.7747× | 1.7438–1.8039× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.13` | Native C engine | 1.4341× | 1.4121–1.4544× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.13` | Rust engine | 1.3056× | 1.2850–1.3259× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.14` | Python engine | 1.7780× | 1.7586–1.7969× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.14` | Native C engine | 1.4359× | 1.4185–1.4540× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.14` | Rust engine | 1.2902× | 1.2729–1.3095× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.15` | Python engine | 1.7603× | 1.7424–1.7780× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.15` | Native C engine | 1.4009× | 1.3865–1.4146× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.15` | Rust engine | 1.2809× | 1.2666–1.2961× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.16` | Python engine | 1.7665× | 1.6501–1.8393× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.16` | Native C engine | 1.4506× | 1.4284–1.4733× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.16` | Rust engine | 1.3255× | 1.3066–1.3456× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.17` | Python engine | 1.7890× | 1.7627–1.8153× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.17` | Native C engine | 1.4396× | 1.4277–1.4535× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.17` | Rust engine | 1.3184× | 1.2975–1.3378× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.18` | Python engine | 1.7807× | 1.7559–1.8033× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.18` | Native C engine | 1.4386× | 1.4205–1.4555× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.18` | Rust engine | 1.3207× | 1.3054–1.3342× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.19` | Python engine | 1.8150× | 1.7829–1.8493× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.19` | Native C engine | 1.4639× | 1.4358–1.5020× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.19` | Rust engine | 1.3082× | 1.2867–1.3293× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.20` | Python engine | 1.7688× | 1.7484–1.7890× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.20` | Native C engine | 1.4082× | 1.3863–1.4324× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.20` | Rust engine | 1.2880× | 1.2708–1.3046× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.21` | Python engine | 1.7828× | 1.7558–1.8176× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.21` | Native C engine | 1.4347× | 1.4145–1.4582× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.21` | Rust engine | 1.3058× | 1.2855–1.3295× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.22` | Python engine | 1.7363× | 1.7008–1.7703× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.22` | Native C engine | 1.3895× | 1.3127–1.4409× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.22` | Rust engine | 1.2322× | 1.1421–1.2872× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.23` | Python engine | 1.7760× | 1.6146–1.9280× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.23` | Native C engine | 1.4778× | 1.4283–1.5570× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.23` | Rust engine | 1.2963× | 1.2359–1.3603× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.24` | Python engine | 1.8143× | 1.7840–1.8464× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.24` | Native C engine | 1.4629× | 1.4359–1.4926× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.24` | Rust engine | 1.3340× | 1.3116–1.3551× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.25` | Python engine | 1.8740× | 1.7532–2.0521× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.25` | Native C engine | 1.5073× | 1.4222–1.6306× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.25` | Rust engine | 1.3702× | 1.2766–1.4891× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.26` | Python engine | 1.7891× | 1.7647–1.8133× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.26` | Native C engine | 1.4440× | 1.4194–1.4682× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.26` | Rust engine | 1.3173× | 1.2974–1.3398× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.27` | Python engine | 1.8013× | 1.7727–1.8291× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.27` | Native C engine | 1.4445× | 1.4194–1.4664× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.27` | Rust engine | 1.3116× | 1.2909–1.3300× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.28` | Python engine | 1.8015× | 1.7800–1.8240× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.28` | Native C engine | 1.4371× | 1.4089–1.4687× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.28` | Rust engine | 1.2920× | 1.2615–1.3184× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.29` | Python engine | 1.7848× | 1.7571–1.8086× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.29` | Native C engine | 1.4575× | 1.4439–1.4715× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.29` | Rust engine | 1.2880× | 1.2312–1.3242× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.30` | Python engine | 1.7616× | 1.7412–1.7819× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.30` | Native C engine | 1.4206× | 1.3980–1.4434× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.30` | Rust engine | 1.2769× | 1.2549–1.2987× | 0.50× | FASTER |
| holdout | `hold.large.cold-compile.31` | Python engine | 1.7803× | 1.7596–1.8003× | 0.39× | FASTER |
| holdout | `hold.large.cold-compile.31` | Native C engine | 1.4313× | 1.4111–1.4521× | 1.65× | FASTER |
| holdout | `hold.large.cold-compile.31` | Rust engine | 1.2789× | 1.2601–1.2986× | 0.50× | FASTER |
| holdout | `hold.large.cold-search.00` | Python engine | 0.1040× | 0.1019–0.1063× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.00` | Native C engine | 1.3373× | 1.2964–1.3782× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.00` | Rust engine | 1.1862× | 1.1632–1.2116× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.01` | Python engine | 0.1051× | 0.1031–0.1078× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.01` | Native C engine | 1.3679× | 1.3267–1.4084× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.01` | Rust engine | 1.1981× | 1.1672–1.2284× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.02` | Python engine | 0.1020× | 0.1009–0.1031× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.02` | Native C engine | 1.3410× | 1.3062–1.3713× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.02` | Rust engine | 1.1742× | 1.1493–1.1975× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.03` | Python engine | 0.1031× | 0.1009–0.1055× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.03` | Native C engine | 1.3498× | 1.3167–1.3821× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.03` | Rust engine | 1.1956× | 1.1703–1.2238× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.04` | Python engine | 0.1022× | 0.1001–0.1047× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.04` | Native C engine | 1.3368× | 1.2630–1.3925× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.04` | Rust engine | 1.1767× | 1.1488–1.2095× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.05` | Python engine | 0.1007× | 0.1000–0.1015× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.05` | Native C engine | 1.3124× | 1.2748–1.3517× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.05` | Rust engine | 1.1704× | 1.1513–1.1888× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.06` | Python engine | 0.0997× | 0.0983–0.1014× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.06` | Native C engine | 1.3345× | 1.2873–1.3776× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.06` | Rust engine | 1.1609× | 1.1329–1.1909× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.07` | Python engine | 0.1038× | 0.1025–0.1050× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.07` | Native C engine | 1.3285× | 1.2992–1.3566× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.07` | Rust engine | 1.1687× | 1.1368–1.1991× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.08` | Python engine | 0.1049× | 0.1033–0.1068× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.08` | Native C engine | 1.3550× | 1.3288–1.3852× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.08` | Rust engine | 1.1955× | 1.1598–1.2236× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.09` | Python engine | 0.1049× | 0.1020–0.1088× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.09` | Native C engine | 1.3769× | 1.3392–1.4220× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.09` | Rust engine | 1.2020× | 1.1549–1.2534× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.10` | Python engine | 0.1021× | 0.1007–0.1035× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.10` | Native C engine | 1.3510× | 1.3287–1.3721× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.10` | Rust engine | 1.1905× | 1.1740–1.2068× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.11` | Python engine | 0.0998× | 0.0978–0.1017× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.11` | Native C engine | 1.3145× | 1.2708–1.3564× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.11` | Rust engine | 1.1701× | 1.1478–1.1914× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.12` | Python engine | 0.1013× | 0.0997–0.1028× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.12` | Native C engine | 1.3464× | 1.3249–1.3674× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.12` | Rust engine | 1.1771× | 1.1546–1.1977× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.13` | Python engine | 0.0982× | 0.0912–0.1030× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.13` | Native C engine | 1.3457× | 1.2624–1.4068× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.13` | Rust engine | 1.1876× | 1.1599–1.2167× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.14` | Python engine | 0.0988× | 0.0928–0.1060× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.14` | Native C engine | 1.3075× | 1.2228–1.3752× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.14` | Rust engine | 1.2317× | 1.1419–1.3565× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.15` | Python engine | 0.1007× | 0.0912–0.1098× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.15` | Native C engine | 1.3087× | 1.1491–1.4665× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.15` | Rust engine | 1.0812× | 0.9651–1.1956× | 0.63× | — |
| holdout | `hold.large.cold-search.16` | Python engine | 0.1025× | 0.0967–0.1078× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.16` | Native C engine | 1.2172× | 1.0937–1.3427× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.16` | Rust engine | 1.2271× | 1.1744–1.2823× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.17` | Python engine | 0.0973× | 0.0914–0.1028× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.17` | Native C engine | 1.2789× | 1.1794–1.3612× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.17` | Rust engine | 1.1180× | 1.0397–1.1934× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.18` | Python engine | 0.0996× | 0.0958–0.1055× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.18` | Native C engine | 1.3270× | 1.3089–1.3465× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.18` | Rust engine | 1.1767× | 1.1119–1.2760× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.19` | Python engine | 0.1005× | 0.0971–0.1050× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.19` | Native C engine | 1.3210× | 1.2713–1.3724× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.19` | Rust engine | 1.1985× | 1.1410–1.2880× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.20` | Python engine | 0.1046× | 0.0989–0.1134× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.20` | Native C engine | 1.4459× | 1.3624–1.5747× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.20` | Rust engine | 1.2056× | 1.1128–1.3427× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.21` | Python engine | 0.1103× | 0.1032–0.1198× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.21` | Native C engine | 1.3998× | 1.3014–1.5376× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.21` | Rust engine | 1.2512× | 1.1789–1.3427× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.22` | Python engine | 0.1056× | 0.1043–0.1070× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.22` | Native C engine | 1.3420× | 1.2996–1.3817× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.22` | Rust engine | 1.2110× | 1.1837–1.2399× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.23` | Python engine | 0.1039× | 0.1022–0.1058× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.23` | Native C engine | 1.3662× | 1.3224–1.4058× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.23` | Rust engine | 1.1977× | 1.1680–1.2251× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.24` | Python engine | 0.1013× | 0.0990–0.1035× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.24` | Native C engine | 1.3094× | 1.2710–1.3518× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.24` | Rust engine | 1.1523× | 1.1010–1.1958× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.25` | Python engine | 0.1007× | 0.0963–0.1044× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.25` | Native C engine | 1.3657× | 1.3192–1.4117× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.25` | Rust engine | 1.1837× | 1.1388–1.2211× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.26` | Python engine | 0.1015× | 0.1004–0.1027× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.26` | Native C engine | 1.3443× | 1.3219–1.3664× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.26` | Rust engine | 1.1732× | 1.1455–1.1987× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.27` | Python engine | 0.1016× | 0.0974–0.1081× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.27` | Native C engine | 1.3430× | 1.2580–1.4457× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.27` | Rust engine | 1.1943× | 1.1456–1.2753× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.28` | Python engine | 0.1066× | 0.1040–0.1099× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.28` | Native C engine | 1.3621× | 1.3026–1.4125× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.28` | Rust engine | 1.2138× | 1.1846–1.2478× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.29` | Python engine | 0.1050× | 0.1028–0.1076× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.29` | Native C engine | 1.3763× | 1.3447–1.4085× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.29` | Rust engine | 1.1871× | 1.1590–1.2172× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.30` | Python engine | 0.1039× | 0.1019–0.1058× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.30` | Native C engine | 1.3245× | 1.2267–1.3934× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.30` | Rust engine | 1.1935× | 1.1628–1.2238× | 0.63× | FASTER |
| holdout | `hold.large.cold-search.31` | Python engine | 0.1010× | 0.0995–0.1023× | 5.57× | SLOWDOWN |
| holdout | `hold.large.cold-search.31` | Native C engine | 1.3203× | 1.2915–1.3468× | 1.77× | FASTER |
| holdout | `hold.large.cold-search.31` | Rust engine | 1.1743× | 1.1541–1.1920× | 0.63× | FASTER |
| holdout | `hold.large.module-search.00` | Python engine | 0.0737× | 0.0717–0.0770× | 4.29× | SLOWDOWN |
| holdout | `hold.large.module-search.00` | Native C engine | 1.2223× | 1.1889–1.2738× | 0.07× | FASTER |
| holdout | `hold.large.module-search.00` | Rust engine | 0.3227× | 0.3147–0.3364× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.01` | Python engine | 0.0732× | 0.0722–0.0742× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.01` | Native C engine | 1.1502× | 1.0592–1.2118× | 0.07× | FASTER |
| holdout | `hold.large.module-search.01` | Rust engine | 0.3194× | 0.3152–0.3228× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.02` | Python engine | 0.0752× | 0.0731–0.0772× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.02` | Native C engine | 1.2116× | 1.1449–1.2590× | 0.07× | FASTER |
| holdout | `hold.large.module-search.02` | Rust engine | 0.3266× | 0.3164–0.3360× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.03` | Python engine | 0.0785× | 0.0754–0.0810× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.03` | Native C engine | 1.2163× | 1.1905–1.2420× | 0.07× | FASTER |
| holdout | `hold.large.module-search.03` | Rust engine | 0.3356× | 0.3266–0.3423× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.04` | Python engine | 0.0715× | 0.0703–0.0726× | 4.29× | SLOWDOWN |
| holdout | `hold.large.module-search.04` | Native C engine | 1.1855× | 1.0980–1.2360× | 0.07× | FASTER |
| holdout | `hold.large.module-search.04` | Rust engine | 0.3074× | 0.2954–0.3177× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.05` | Python engine | 0.0760× | 0.0710–0.0845× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.05` | Native C engine | 1.2078× | 1.0944–1.3706× | 0.07× | FASTER |
| holdout | `hold.large.module-search.05` | Rust engine | 0.3244× | 0.3042–0.3550× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.06` | Python engine | 0.0751× | 0.0737–0.0762× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.06` | Native C engine | 1.1817× | 1.1082–1.2311× | 0.07× | FASTER |
| holdout | `hold.large.module-search.06` | Rust engine | 0.3195× | 0.3114–0.3252× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.07` | Python engine | 0.0811× | 0.0791–0.0839× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.07` | Native C engine | 1.1396× | 0.9613–1.2484× | 0.07× | — |
| holdout | `hold.large.module-search.07` | Rust engine | 0.3436× | 0.3354–0.3549× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.08` | Python engine | 0.0742× | 0.0724–0.0770× | 4.29× | SLOWDOWN |
| holdout | `hold.large.module-search.08` | Native C engine | 1.2657× | 1.2246–1.3231× | 0.07× | FASTER |
| holdout | `hold.large.module-search.08` | Rust engine | 0.3256× | 0.3161–0.3408× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.09` | Python engine | 0.0734× | 0.0709–0.0751× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.09` | Native C engine | 1.2360× | 1.2206–1.2556× | 0.07× | FASTER |
| holdout | `hold.large.module-search.09` | Rust engine | 0.3198× | 0.3114–0.3260× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.10` | Python engine | 0.0740× | 0.0718–0.0757× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.10` | Native C engine | 1.2150× | 1.2001–1.2310× | 0.07× | FASTER |
| holdout | `hold.large.module-search.10` | Rust engine | 0.3259× | 0.3230–0.3291× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.11` | Python engine | 0.0773× | 0.0753–0.0789× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.11` | Native C engine | 1.1975× | 1.1819–1.2132× | 0.07× | FASTER |
| holdout | `hold.large.module-search.11` | Rust engine | 0.3359× | 0.3335–0.3383× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.12` | Python engine | 0.0756× | 0.0722–0.0811× | 4.29× | SLOWDOWN |
| holdout | `hold.large.module-search.12` | Native C engine | 1.2496× | 1.1399–1.3693× | 0.07× | FASTER |
| holdout | `hold.large.module-search.12` | Rust engine | 0.3169× | 0.3076–0.3264× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.13` | Python engine | 0.0755× | 0.0710–0.0834× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.13` | Native C engine | 1.1581× | 1.0871–1.2037× | 0.07× | FASTER |
| holdout | `hold.large.module-search.13` | Rust engine | 0.3057× | 0.2925–0.3172× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.14` | Python engine | 0.0745× | 0.0726–0.0760× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.14` | Native C engine | 1.1931× | 1.1702–1.2125× | 0.07× | FASTER |
| holdout | `hold.large.module-search.14` | Rust engine | 0.3222× | 0.3195–0.3249× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.15` | Python engine | 0.0795× | 0.0782–0.0809× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.15` | Native C engine | 1.2138× | 1.1657–1.2554× | 0.07× | FASTER |
| holdout | `hold.large.module-search.15` | Rust engine | 0.3429× | 0.3374–0.3491× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.16` | Python engine | 0.0721× | 0.0711–0.0730× | 4.29× | SLOWDOWN |
| holdout | `hold.large.module-search.16` | Native C engine | 1.2043× | 1.1918–1.2156× | 0.07× | FASTER |
| holdout | `hold.large.module-search.16` | Rust engine | 0.3178× | 0.3149–0.3205× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.17` | Python engine | 0.0732× | 0.0722–0.0741× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.17` | Native C engine | 1.1252× | 1.0080–1.2222× | 0.07× | FASTER |
| holdout | `hold.large.module-search.17` | Rust engine | 0.3202× | 0.3138–0.3262× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.18` | Python engine | 0.0734× | 0.0585–0.0911× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.18` | Native C engine | 1.3511× | 1.1829–1.6374× | 0.07× | FASTER |
| holdout | `hold.large.module-search.18` | Rust engine | 0.3616× | 0.3205–0.4289× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.19` | Python engine | 0.0845× | 0.0743–0.1008× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.19` | Native C engine | 1.3190× | 1.1670–1.5642× | 0.07× | FASTER |
| holdout | `hold.large.module-search.19` | Rust engine | 0.3621× | 0.3224–0.4254× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.20` | Python engine | 0.0711× | 0.0682–0.0729× | 4.29× | SLOWDOWN |
| holdout | `hold.large.module-search.20` | Native C engine | 1.1789× | 1.1139–1.2190× | 0.07× | FASTER |
| holdout | `hold.large.module-search.20` | Rust engine | 0.3055× | 0.2951–0.3131× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.21` | Python engine | 0.0735× | 0.0726–0.0744× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.21` | Native C engine | 1.2248× | 1.2095–1.2389× | 0.07× | FASTER |
| holdout | `hold.large.module-search.21` | Rust engine | 0.3186× | 0.3102–0.3244× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.22` | Python engine | 0.0746× | 0.0732–0.0758× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.22` | Native C engine | 1.2186× | 1.2044–1.2327× | 0.07× | FASTER |
| holdout | `hold.large.module-search.22` | Rust engine | 0.3097× | 0.2925–0.3241× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.23` | Python engine | 0.0791× | 0.0778–0.0804× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.23` | Native C engine | 1.2255× | 1.2114–1.2393× | 0.07× | FASTER |
| holdout | `hold.large.module-search.23` | Rust engine | 0.3362× | 0.3324–0.3399× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.24` | Python engine | 0.0730× | 0.0722–0.0739× | 4.29× | SLOWDOWN |
| holdout | `hold.large.module-search.24` | Native C engine | 1.2257× | 1.2087–1.2406× | 0.07× | FASTER |
| holdout | `hold.large.module-search.24` | Rust engine | 0.3174× | 0.3148–0.3200× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.25` | Python engine | 0.0757× | 0.0734–0.0796× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.25` | Native C engine | 1.2435× | 1.2066–1.3062× | 0.07× | FASTER |
| holdout | `hold.large.module-search.25` | Rust engine | 0.3292× | 0.3198–0.3454× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.26` | Python engine | 0.0765× | 0.0755–0.0776× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.26` | Native C engine | 1.2279× | 1.2155–1.2412× | 0.07× | FASTER |
| holdout | `hold.large.module-search.26` | Rust engine | 0.3282× | 0.3231–0.3335× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.27` | Python engine | 0.0788× | 0.0777–0.0801× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.27` | Native C engine | 1.2195× | 1.1840–1.2483× | 0.07× | FASTER |
| holdout | `hold.large.module-search.27` | Rust engine | 0.3337× | 0.3285–0.3392× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.28` | Python engine | 0.0739× | 0.0714–0.0776× | 4.29× | SLOWDOWN |
| holdout | `hold.large.module-search.28` | Native C engine | 1.2552× | 1.2127–1.3135× | 0.07× | FASTER |
| holdout | `hold.large.module-search.28` | Rust engine | 0.3082× | 0.2843–0.3302× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.29` | Python engine | 0.0718× | 0.0704–0.0730× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.29` | Native C engine | 1.1983× | 1.1833–1.2113× | 0.07× | FASTER |
| holdout | `hold.large.module-search.29` | Rust engine | 0.3087× | 0.3062–0.3113× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.30` | Python engine | 0.0751× | 0.0739–0.0762× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.30` | Native C engine | 1.2246× | 1.2023–1.2528× | 0.07× | FASTER |
| holdout | `hold.large.module-search.30` | Rust engine | 0.3165× | 0.3026–0.3261× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-search.31` | Python engine | 0.0775× | 0.0747–0.0798× | 4.34× | SLOWDOWN |
| holdout | `hold.large.module-search.31` | Native C engine | 1.2181× | 1.1914–1.2483× | 0.07× | FASTER |
| holdout | `hold.large.module-search.31` | Rust engine | 0.3220× | 0.2913–0.3419× | 0.07× | SLOWDOWN |
| holdout | `hold.large.module-replace.00` | Python engine | 0.0353× | 0.0335–0.0384× | 8.55× | SLOWDOWN |
| holdout | `hold.large.module-replace.00` | Native C engine | 1.2026× | 1.1213–1.3199× | 0.04× | FASTER |
| holdout | `hold.large.module-replace.00` | Rust engine | 0.1157× | 0.1097–0.1267× | 1.52× | SLOWDOWN |
| holdout | `hold.large.module-replace.01` | Python engine | 0.0276× | 0.0273–0.0280× | 9.00× | SLOWDOWN |
| holdout | `hold.large.module-replace.01` | Native C engine | 1.4010× | 1.3859–1.4156× | 0.05× | FASTER |
| holdout | `hold.large.module-replace.01` | Rust engine | 0.1075× | 0.1059–0.1091× | 2.65× | SLOWDOWN |
| holdout | `hold.large.module-replace.02` | Python engine | 0.0237× | 0.0235–0.0238× | 9.69× | SLOWDOWN |
| holdout | `hold.large.module-replace.02` | Native C engine | 1.6536× | 1.6326–1.6734× | 0.06× | FASTER |
| holdout | `hold.large.module-replace.02` | Rust engine | 0.1039× | 0.1030–0.1048× | 4.89× | SLOWDOWN |
| holdout | `hold.large.module-replace.03` | Python engine | 0.0214× | 0.0213–0.0216× | 10.65× | SLOWDOWN |
| holdout | `hold.large.module-replace.03` | Native C engine | 1.9351× | 1.9211–1.9484× | 0.08× | FASTER |
| holdout | `hold.large.module-replace.03` | Rust engine | 0.1025× | 0.1010–0.1040× | 7.54× | SLOWDOWN |
| holdout | `hold.large.module-replace.04` | Python engine | 0.0338× | 0.0335–0.0342× | 8.51× | SLOWDOWN |
| holdout | `hold.large.module-replace.04` | Native C engine | 1.1766× | 1.1635–1.1916× | 0.04× | FASTER |
| holdout | `hold.large.module-replace.04` | Rust engine | 0.1110× | 0.1099–0.1123× | 1.81× | SLOWDOWN |
| holdout | `hold.large.module-replace.05` | Python engine | 0.0280× | 0.0278–0.0281× | 8.98× | SLOWDOWN |
| holdout | `hold.large.module-replace.05` | Native C engine | 1.4154× | 1.4072–1.4239× | 0.05× | FASTER |
| holdout | `hold.large.module-replace.05` | Rust engine | 0.1078× | 0.1070–0.1087× | 2.91× | SLOWDOWN |
| holdout | `hold.large.module-replace.06` | Python engine | 0.0249× | 0.0240–0.0266× | 9.69× | SLOWDOWN |
| holdout | `hold.large.module-replace.06` | Native C engine | 1.7676× | 1.7032–1.8841× | 0.06× | FASTER |
| holdout | `hold.large.module-replace.06` | Rust engine | 0.1086× | 0.1046–0.1155× | 4.89× | SLOWDOWN |
| holdout | `hold.large.module-replace.07` | Python engine | 0.0219× | 0.0216–0.0223× | 10.65× | SLOWDOWN |
| holdout | `hold.large.module-replace.07` | Native C engine | 1.8718× | 1.7204–1.9830× | 0.08× | FASTER |
| holdout | `hold.large.module-replace.07` | Rust engine | 0.1046× | 0.1034–0.1061× | 7.54× | SLOWDOWN |
| holdout | `hold.large.module-replace.08` | Python engine | 0.0332× | 0.0326–0.0340× | 8.53× | SLOWDOWN |
| holdout | `hold.large.module-replace.08` | Native C engine | 1.1761× | 1.1628–1.1965× | 0.04× | FASTER |
| holdout | `hold.large.module-replace.08` | Rust engine | 0.1104× | 0.1089–0.1128× | 1.66× | SLOWDOWN |
| holdout | `hold.large.module-replace.09` | Python engine | 0.0269× | 0.0267–0.0271× | 8.98× | SLOWDOWN |
| holdout | `hold.large.module-replace.09` | Native C engine | 1.3358× | 1.2717–1.3823× | 0.05× | FASTER |
| holdout | `hold.large.module-replace.09` | Rust engine | 0.1050× | 0.1039–0.1062× | 2.91× | SLOWDOWN |
| holdout | `hold.large.module-replace.10` | Python engine | 0.0234× | 0.0224–0.0246× | 9.65× | SLOWDOWN |
| holdout | `hold.large.module-replace.10` | Native C engine | 1.6598× | 1.5599–1.7467× | 0.07× | FASTER |
| holdout | `hold.large.module-replace.10` | Rust engine | 0.1042× | 0.1005–0.1087× | 5.33× | SLOWDOWN |
| holdout | `hold.large.module-replace.11` | Python engine | 0.0213× | 0.0211–0.0215× | 10.65× | SLOWDOWN |
| holdout | `hold.large.module-replace.11` | Native C engine | 1.9545× | 1.9431–1.9669× | 0.08× | FASTER |
| holdout | `hold.large.module-replace.11` | Rust engine | 0.1017× | 0.1005–0.1029× | 7.54× | SLOWDOWN |
| holdout | `hold.large.module-replace.12` | Python engine | 0.0334× | 0.0332–0.0337× | 8.53× | SLOWDOWN |
| holdout | `hold.large.module-replace.12` | Native C engine | 1.1589× | 1.1236–1.1816× | 0.04× | FASTER |
| holdout | `hold.large.module-replace.12` | Rust engine | 0.1100× | 0.1092–0.1110× | 1.66× | SLOWDOWN |
| holdout | `hold.large.module-replace.13` | Python engine | 0.0274× | 0.0271–0.0278× | 8.98× | SLOWDOWN |
| holdout | `hold.large.module-replace.13` | Native C engine | 1.3926× | 1.3753–1.4178× | 0.05× | FASTER |
| holdout | `hold.large.module-replace.13` | Rust engine | 0.1066× | 0.1052–0.1085× | 2.91× | SLOWDOWN |
| holdout | `hold.large.module-replace.14` | Python engine | 0.0231× | 0.0230–0.0233× | 9.69× | SLOWDOWN |
| holdout | `hold.large.module-replace.14` | Native C engine | 1.6349× | 1.6206–1.6472× | 0.06× | FASTER |
| holdout | `hold.large.module-replace.14` | Rust engine | 0.1032× | 0.1024–0.1040× | 4.89× | SLOWDOWN |
| holdout | `hold.large.module-replace.15` | Python engine | 0.0214× | 0.0208–0.0223× | 10.58× | SLOWDOWN |
| holdout | `hold.large.module-replace.15` | Native C engine | 1.9890× | 1.9329–2.0720× | 0.09× | FASTER |
| holdout | `hold.large.module-replace.15` | Rust engine | 0.1014× | 0.0965–0.1065× | 8.23× | SLOWDOWN |
| holdout | `hold.large.module-replace.16` | Python engine | 0.0338× | 0.0332–0.0350× | 8.53× | SLOWDOWN |
| holdout | `hold.large.module-replace.16` | Native C engine | 1.1874× | 1.1618–1.2301× | 0.04× | FASTER |
| holdout | `hold.large.module-replace.16` | Rust engine | 0.1124× | 0.1099–0.1165× | 1.66× | SLOWDOWN |
| holdout | `hold.large.module-replace.17` | Python engine | 0.0273× | 0.0271–0.0275× | 8.95× | SLOWDOWN |
| holdout | `hold.large.module-replace.17` | Native C engine | 1.3571× | 1.2730–1.4057× | 0.05× | FASTER |
| holdout | `hold.large.module-replace.17` | Rust engine | 0.1056× | 0.1043–0.1069× | 3.18× | SLOWDOWN |
| holdout | `hold.large.module-replace.18` | Python engine | 0.0244× | 0.0242–0.0246× | 9.65× | SLOWDOWN |
| holdout | `hold.large.module-replace.18` | Native C engine | 1.7282× | 1.7103–1.7460× | 0.07× | FASTER |
| holdout | `hold.large.module-replace.18` | Rust engine | 0.1062× | 0.1047–0.1078× | 5.33× | SLOWDOWN |
| holdout | `hold.large.module-replace.19` | Python engine | 0.0217× | 0.0214–0.0219× | 10.65× | SLOWDOWN |
| holdout | `hold.large.module-replace.19` | Native C engine | 1.9763× | 1.9554–2.0003× | 0.08× | FASTER |
| holdout | `hold.large.module-replace.19` | Rust engine | 0.1041× | 0.1027–0.1054× | 7.54× | SLOWDOWN |
| holdout | `hold.large.module-replace.20` | Python engine | 0.0336× | 0.0331–0.0341× | 8.53× | SLOWDOWN |
| holdout | `hold.large.module-replace.20` | Native C engine | 1.1376× | 1.0862–1.1841× | 0.04× | FASTER |
| holdout | `hold.large.module-replace.20` | Rust engine | 0.1104× | 0.1087–0.1123× | 1.66× | SLOWDOWN |
| holdout | `hold.large.module-replace.21` | Python engine | 0.0276× | 0.0267–0.0289× | 8.98× | SLOWDOWN |
| holdout | `hold.large.module-replace.21` | Native C engine | 1.4138× | 1.3800–1.4742× | 0.05× | FASTER |
| holdout | `hold.large.module-replace.21` | Rust engine | 0.1074× | 0.1045–0.1121× | 2.91× | SLOWDOWN |
| holdout | `hold.large.module-replace.22` | Python engine | 0.0235× | 0.0233–0.0237× | 9.69× | SLOWDOWN |
| holdout | `hold.large.module-replace.22` | Native C engine | 1.6541× | 1.6284–1.6758× | 0.06× | FASTER |
| holdout | `hold.large.module-replace.22` | Rust engine | 0.1028× | 0.1012–0.1044× | 4.89× | SLOWDOWN |
| holdout | `hold.large.module-replace.23` | Python engine | 0.0213× | 0.0211–0.0214× | 10.65× | SLOWDOWN |
| holdout | `hold.large.module-replace.23` | Native C engine | 1.9311× | 1.9095–1.9516× | 0.08× | FASTER |
| holdout | `hold.large.module-replace.23` | Rust engine | 0.1008× | 0.0992–0.1024× | 7.54× | SLOWDOWN |
| holdout | `hold.large.module-replace.24` | Python engine | 0.0335× | 0.0333–0.0337× | 8.53× | SLOWDOWN |
| holdout | `hold.large.module-replace.24` | Native C engine | 1.1253× | 1.0316–1.1782× | 0.04× | FASTER |
| holdout | `hold.large.module-replace.24` | Rust engine | 0.1093× | 0.1082–0.1105× | 1.66× | SLOWDOWN |
| holdout | `hold.large.module-replace.25` | Python engine | 0.0274× | 0.0273–0.0276× | 8.98× | SLOWDOWN |
| holdout | `hold.large.module-replace.25` | Native C engine | 1.4018× | 1.3922–1.4113× | 0.05× | FASTER |
| holdout | `hold.large.module-replace.25` | Rust engine | 0.1070× | 0.1058–0.1081× | 2.91× | SLOWDOWN |
| holdout | `hold.large.module-replace.26` | Python engine | 0.0246× | 0.0235–0.0263× | 9.62× | SLOWDOWN |
| holdout | `hold.large.module-replace.26` | Native C engine | 1.7719× | 1.6898–1.8821× | 0.07× | FASTER |
| holdout | `hold.large.module-replace.26` | Rust engine | 0.1081× | 0.1033–0.1152× | 5.67× | SLOWDOWN |
| holdout | `hold.large.module-replace.27` | Python engine | 0.0214× | 0.0213–0.0216× | 10.58× | SLOWDOWN |
| holdout | `hold.large.module-replace.27` | Native C engine | 1.9609× | 1.9426–1.9797× | 0.09× | FASTER |
| holdout | `hold.large.module-replace.27` | Rust engine | 0.1019× | 0.1009–0.1029× | 8.23× | SLOWDOWN |
| holdout | `hold.large.module-replace.28` | Python engine | 0.0331× | 0.0328–0.0335× | 8.51× | SLOWDOWN |
| holdout | `hold.large.module-replace.28` | Native C engine | 1.1537× | 1.1209–1.1818× | 0.04× | FASTER |
| holdout | `hold.large.module-replace.28` | Rust engine | 0.1097× | 0.1085–0.1111× | 1.81× | SLOWDOWN |
| holdout | `hold.large.module-replace.29` | Python engine | 0.0269× | 0.0267–0.0271× | 8.93× | SLOWDOWN |
| holdout | `hold.large.module-replace.29` | Native C engine | 1.3977× | 1.3888–1.4061× | 0.05× | FASTER |
| holdout | `hold.large.module-replace.29` | Rust engine | 0.1053× | 0.1047–0.1059× | 3.44× | SLOWDOWN |
| holdout | `hold.large.module-replace.30` | Python engine | 0.0232× | 0.0231–0.0233× | 9.65× | SLOWDOWN |
| holdout | `hold.large.module-replace.30` | Native C engine | 1.6433× | 1.6325–1.6547× | 0.07× | FASTER |
| holdout | `hold.large.module-replace.30` | Rust engine | 0.1008× | 0.0995–0.1021× | 5.33× | SLOWDOWN |
| holdout | `hold.large.module-replace.31` | Python engine | 0.0219× | 0.0212–0.0230× | 10.51× | SLOWDOWN |
| holdout | `hold.large.module-replace.31` | Native C engine | 1.9408× | 1.8022–2.0874× | 0.09× | FASTER |
| holdout | `hold.large.module-replace.31` | Rust engine | 0.1031× | 0.0994–0.1093× | 8.90× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.00` | Python engine | 0.0154× | 0.0146–0.0165× | 9.40× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.00` | Native C engine | 2.3845× | 2.2637–2.5459× | 0.36× | FASTER |
| holdout | `hold.large.empty-iterator.00` | Rust engine | 0.1991× | 0.1889–0.2115× | 0.37× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.01` | Python engine | 0.0124× | 0.0123–0.0126× | 13.40× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.01` | Native C engine | 2.1271× | 2.1015–2.1510× | 0.43× | FASTER |
| holdout | `hold.large.empty-iterator.01` | Rust engine | 0.1716× | 0.1683–0.1748× | 0.43× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.02` | Python engine | 0.0111× | 0.0109–0.0115× | 18.79× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.02` | Native C engine | 2.0404× | 1.9964–2.1053× | 0.52× | FASTER |
| holdout | `hold.large.empty-iterator.02` | Rust engine | 0.1632× | 0.1587–0.1689× | 0.50× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.03` | Python engine | 0.0108× | 0.0104–0.0112× | 21.82× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.03` | Native C engine | 1.9862× | 1.9357–2.0417× | 0.61× | FASTER |
| holdout | `hold.large.empty-iterator.03` | Rust engine | 0.1583× | 0.1519–0.1639× | 0.57× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.04` | Python engine | 0.0146× | 0.0142–0.0151× | 9.81× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.04` | Native C engine | 2.3018× | 2.2361–2.3917× | 0.36× | FASTER |
| holdout | `hold.large.empty-iterator.04` | Rust engine | 0.1946× | 0.1892–0.2017× | 0.37× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.05` | Python engine | 0.0125× | 0.0123–0.0126× | 13.40× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.05` | Native C engine | 2.0988× | 1.9825–2.1773× | 0.43× | FASTER |
| holdout | `hold.large.empty-iterator.05` | Rust engine | 0.1727× | 0.1704–0.1750× | 0.43× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.06` | Python engine | 0.0113× | 0.0112–0.0114× | 17.82× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.06` | Native C engine | 2.0431× | 2.0162–2.0697× | 0.52× | FASTER |
| holdout | `hold.large.empty-iterator.06` | Rust engine | 0.1622× | 0.1599–0.1641× | 0.50× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.07` | Python engine | 0.0110× | 0.0107–0.0114× | 21.82× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.07` | Native C engine | 2.0209× | 1.9580–2.1069× | 0.61× | FASTER |
| holdout | `hold.large.empty-iterator.07` | Rust engine | 0.1627× | 0.1586–0.1695× | 0.57× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.08` | Python engine | 0.0147× | 0.0145–0.0148× | 9.40× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.08` | Native C engine | 2.1582× | 2.0193–2.2423× | 0.36× | FASTER |
| holdout | `hold.large.empty-iterator.08` | Rust engine | 0.1889× | 0.1873–0.1905× | 0.37× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.09` | Python engine | 0.0124× | 0.0123–0.0124× | 13.40× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.09` | Native C engine | 2.0847× | 1.9638–2.1572× | 0.43× | FASTER |
| holdout | `hold.large.empty-iterator.09` | Rust engine | 0.1722× | 0.1710–0.1734× | 0.43× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.10` | Python engine | 0.0109× | 0.0108–0.0109× | 18.79× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.10` | Native C engine | 1.9760× | 1.9112–2.0174× | 0.52× | FASTER |
| holdout | `hold.large.empty-iterator.10` | Rust engine | 0.1564× | 0.1466–0.1624× | 0.50× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.11` | Python engine | 0.0112× | 0.0110–0.0113× | 16.55× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.11` | Native C engine | 2.0185× | 1.9775–2.0582× | 0.61× | FASTER |
| holdout | `hold.large.empty-iterator.11` | Rust engine | 0.1602× | 0.1582–0.1626× | 0.57× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.12` | Python engine | 0.0148× | 0.0145–0.0152× | 9.40× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.12` | Native C engine | 2.2421× | 2.1873–2.3150× | 0.36× | FASTER |
| holdout | `hold.large.empty-iterator.12` | Rust engine | 0.1891× | 0.1851–0.1950× | 0.37× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.13` | Python engine | 0.0125× | 0.0123–0.0127× | 13.40× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.13` | Native C engine | 2.0715× | 1.9215–2.1706× | 0.43× | FASTER |
| holdout | `hold.large.empty-iterator.13` | Rust engine | 0.1730× | 0.1691–0.1771× | 0.43× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.14` | Python engine | 0.0117× | 0.0116–0.0118× | 14.03× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.14` | Native C engine | 2.0266× | 1.9766–2.0711× | 0.52× | FASTER |
| holdout | `hold.large.empty-iterator.14` | Rust engine | 0.1646× | 0.1632–0.1660× | 0.50× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.15` | Python engine | 0.0107× | 0.0106–0.0108× | 21.82× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.15` | Native C engine | 1.9302× | 1.7983–2.0138× | 0.61× | FASTER |
| holdout | `hold.large.empty-iterator.15` | Rust engine | 0.1598× | 0.1572–0.1618× | 0.57× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.16` | Python engine | 0.0146× | 0.0145–0.0147× | 9.40× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.16` | Native C engine | 2.2384× | 2.2139–2.2603× | 0.36× | FASTER |
| holdout | `hold.large.empty-iterator.16` | Rust engine | 0.1868× | 0.1849–0.1884× | 0.37× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.17` | Python engine | 0.0124× | 0.0123–0.0126× | 13.40× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.17` | Native C engine | 2.1161× | 2.0875–2.1472× | 0.43× | FASTER |
| holdout | `hold.large.empty-iterator.17` | Rust engine | 0.1720× | 0.1701–0.1742× | 0.43× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.18` | Python engine | 0.0114× | 0.0113–0.0115× | 17.82× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.18` | Native C engine | 2.0557× | 2.0240–2.0933× | 0.52× | FASTER |
| holdout | `hold.large.empty-iterator.18` | Rust engine | 0.1647× | 0.1629–0.1664× | 0.50× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.19` | Python engine | 0.0104× | 0.0103–0.0104× | 18.06× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.19` | Native C engine | 1.9487× | 1.9109–1.9919× | 0.61× | FASTER |
| holdout | `hold.large.empty-iterator.19` | Rust engine | 0.1598× | 0.1585–0.1610× | 0.57× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.20` | Python engine | 0.0146× | 0.0145–0.0148× | 9.40× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.20` | Native C engine | 2.2170× | 2.1755–2.2488× | 0.36× | FASTER |
| holdout | `hold.large.empty-iterator.20` | Rust engine | 0.1889× | 0.1865–0.1912× | 0.37× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.21` | Python engine | 0.0127× | 0.0125–0.0129× | 11.03× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.21` | Native C engine | 2.1402× | 2.0947–2.1790× | 0.43× | FASTER |
| holdout | `hold.large.empty-iterator.21` | Rust engine | 0.1715× | 0.1692–0.1741× | 0.43× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.22` | Python engine | 0.0108× | 0.0106–0.0110× | 18.79× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.22` | Native C engine | 2.0231× | 1.9983–2.0484× | 0.52× | FASTER |
| holdout | `hold.large.empty-iterator.22` | Rust engine | 0.1617× | 0.1595–0.1637× | 0.50× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.23` | Python engine | 0.0106× | 0.0105–0.0107× | 21.82× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.23` | Native C engine | 2.0103× | 1.9571–2.0585× | 0.61× | FASTER |
| holdout | `hold.large.empty-iterator.23` | Rust engine | 0.1575× | 0.1554–0.1595× | 0.57× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.24` | Python engine | 0.0155× | 0.0148–0.0165× | 9.40× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.24` | Native C engine | 2.3446× | 2.2447–2.4989× | 0.36× | FASTER |
| holdout | `hold.large.empty-iterator.24` | Rust engine | 0.1919× | 0.1872–0.1980× | 0.37× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.25` | Python engine | 0.0122× | 0.0120–0.0125× | 14.08× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.25` | Native C engine | 2.0256× | 1.8878–2.1126× | 0.43× | FASTER |
| holdout | `hold.large.empty-iterator.25` | Rust engine | 0.1730× | 0.1695–0.1780× | 0.43× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.26` | Python engine | 0.0112× | 0.0111–0.0112× | 17.82× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.26` | Native C engine | 1.9286× | 1.7902–2.0159× | 0.52× | FASTER |
| holdout | `hold.large.empty-iterator.26` | Rust engine | 0.1618× | 0.1608–0.1627× | 0.50× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.27` | Python engine | 0.0105× | 0.0101–0.0109× | 21.82× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.27` | Native C engine | 1.9748× | 1.8446–2.0696× | 0.61× | FASTER |
| holdout | `hold.large.empty-iterator.27` | Rust engine | 0.1612× | 0.1584–0.1644× | 0.57× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.28` | Python engine | 0.0148× | 0.0147–0.0150× | 9.40× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.28` | Native C engine | 2.2631× | 2.2438–2.2829× | 0.36× | FASTER |
| holdout | `hold.large.empty-iterator.28` | Rust engine | 0.1904× | 0.1877–0.1932× | 0.37× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.29` | Python engine | 0.0128× | 0.0127–0.0129× | 11.03× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.29` | Native C engine | 1.9658× | 1.7730–2.1269× | 0.43× | FASTER |
| holdout | `hold.large.empty-iterator.29` | Rust engine | 0.1680× | 0.1576–0.1748× | 0.43× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.30` | Python engine | 0.0118× | 0.0112–0.0130× | 17.82× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.30` | Native C engine | 2.1548× | 2.0328–2.3579× | 0.52× | FASTER |
| holdout | `hold.large.empty-iterator.30` | Rust engine | 0.1701× | 0.1604–0.1880× | 0.50× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.31` | Python engine | 0.0112× | 0.0107–0.0123× | 21.82× | SLOWDOWN |
| holdout | `hold.large.empty-iterator.31` | Native C engine | 2.1072× | 1.9670–2.3339× | 0.61× | FASTER |
| holdout | `hold.large.empty-iterator.31` | Rust engine | 0.1640× | 0.1525–0.1829× | 0.57× | SLOWDOWN |
| holdout | `hold.large.references.00` | Python engine | 0.0230× | 0.0227–0.0233× | 6.44× | SLOWDOWN |
| holdout | `hold.large.references.00` | Native C engine | 1.5105× | 1.4934–1.5289× | 0.08× | FASTER |
| holdout | `hold.large.references.00` | Rust engine | 0.2065× | 0.2023–0.2104× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.01` | Python engine | 0.0223× | 0.0220–0.0227× | 6.45× | SLOWDOWN |
| holdout | `hold.large.references.01` | Native C engine | 1.4670× | 1.4473–1.4862× | 0.08× | FASTER |
| holdout | `hold.large.references.01` | Rust engine | 0.1986× | 0.1893–0.2051× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.02` | Python engine | 0.0229× | 0.0224–0.0232× | 6.50× | SLOWDOWN |
| holdout | `hold.large.references.02` | Native C engine | 1.4679× | 1.4440–1.4909× | 0.08× | FASTER |
| holdout | `hold.large.references.02` | Rust engine | 0.2049× | 0.2024–0.2073× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.03` | Python engine | 0.0271× | 0.0248–0.0310× | 6.50× | SLOWDOWN |
| holdout | `hold.large.references.03` | Native C engine | 1.3420× | 1.1746–1.5596× | 0.08× | FASTER |
| holdout | `hold.large.references.03` | Rust engine | 0.2393× | 0.2200–0.2708× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.04` | Python engine | 0.0220× | 0.0218–0.0223× | 6.45× | SLOWDOWN |
| holdout | `hold.large.references.04` | Native C engine | 1.5175× | 1.4981–1.5376× | 0.08× | FASTER |
| holdout | `hold.large.references.04` | Rust engine | 0.1960× | 0.1871–0.2032× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.05` | Python engine | 0.0212× | 0.0196–0.0225× | 6.95× | SLOWDOWN |
| holdout | `hold.large.references.05` | Native C engine | 1.6838× | 1.6529–1.7180× | 0.00× | FASTER |
| holdout | `hold.large.references.05` | Rust engine | 0.2493× | 0.2419–0.2576× | 0.00× | SLOWDOWN |
| holdout | `hold.large.references.06` | Python engine | 0.0241× | 0.0232–0.0254× | 6.50× | SLOWDOWN |
| holdout | `hold.large.references.06` | Native C engine | 1.3612× | 1.2259–1.4762× | 0.08× | FASTER |
| holdout | `hold.large.references.06` | Rust engine | 0.2132× | 0.1989–0.2271× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.07` | Python engine | 0.0244× | 0.0227–0.0267× | 6.50× | SLOWDOWN |
| holdout | `hold.large.references.07` | Native C engine | 1.2392× | 1.0612–1.4245× | 0.08× | FASTER |
| holdout | `hold.large.references.07` | Rust engine | 0.2268× | 0.2079–0.2491× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.08` | Python engine | 0.0207× | 0.0191–0.0224× | 6.45× | SLOWDOWN |
| holdout | `hold.large.references.08` | Native C engine | 1.4568× | 1.2802–1.6446× | 0.08× | FASTER |
| holdout | `hold.large.references.08` | Rust engine | 0.1838× | 0.1704–0.1969× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.09` | Python engine | 0.0230× | 0.0218–0.0241× | 6.44× | SLOWDOWN |
| holdout | `hold.large.references.09` | Native C engine | 1.5048× | 1.3988–1.6185× | 0.08× | FASTER |
| holdout | `hold.large.references.09` | Rust engine | 0.1867× | 0.1646–0.2063× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.10` | Python engine | 0.0226× | 0.0220–0.0232× | 6.50× | SLOWDOWN |
| holdout | `hold.large.references.10` | Native C engine | 1.4393× | 1.4118–1.4681× | 0.08× | FASTER |
| holdout | `hold.large.references.10` | Rust engine | 0.2081× | 0.2044–0.2120× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.11` | Python engine | 0.0236× | 0.0203–0.0284× | 7.01× | SLOWDOWN |
| holdout | `hold.large.references.11` | Native C engine | 1.7820× | 1.5656–2.0999× | 0.00× | FASTER |
| holdout | `hold.large.references.11` | Rust engine | 0.2948× | 0.2626–0.3442× | 0.00× | SLOWDOWN |
| holdout | `hold.large.references.12` | Python engine | 0.0247× | 0.0223–0.0287× | 6.44× | SLOWDOWN |
| holdout | `hold.large.references.12` | Native C engine | 1.6840× | 1.4888–1.9650× | 0.08× | FASTER |
| holdout | `hold.large.references.12` | Rust engine | 0.2338× | 0.2088–0.2721× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.13` | Python engine | 0.0232× | 0.0222–0.0245× | 6.50× | SLOWDOWN |
| holdout | `hold.large.references.13` | Native C engine | 1.4096× | 1.2895–1.5095× | 0.08× | FASTER |
| holdout | `hold.large.references.13` | Rust engine | 0.1960× | 0.1796–0.2089× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.14` | Python engine | 0.0239× | 0.0221–0.0264× | 6.50× | SLOWDOWN |
| holdout | `hold.large.references.14` | Native C engine | 1.4310× | 1.2891–1.5650× | 0.08× | FASTER |
| holdout | `hold.large.references.14` | Rust engine | 0.1998× | 0.1782–0.2244× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.15` | Python engine | 0.0257× | 0.0244–0.0268× | 6.50× | SLOWDOWN |
| holdout | `hold.large.references.15` | Native C engine | 1.3597× | 1.2961–1.4137× | 0.08× | FASTER |
| holdout | `hold.large.references.15` | Rust engine | 0.2181× | 0.2023–0.2304× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.16` | Python engine | 0.0222× | 0.0209–0.0239× | 6.45× | SLOWDOWN |
| holdout | `hold.large.references.16` | Native C engine | 1.5763× | 1.5177–1.6727× | 0.08× | FASTER |
| holdout | `hold.large.references.16` | Rust engine | 0.2103× | 0.2024–0.2216× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.17` | Python engine | 0.0215× | 0.0204–0.0234× | 6.95× | SLOWDOWN |
| holdout | `hold.large.references.17` | Native C engine | 1.6899× | 1.5642–1.8407× | 0.00× | FASTER |
| holdout | `hold.large.references.17` | Rust engine | 0.2625× | 0.2503–0.2838× | 0.00× | SLOWDOWN |
| holdout | `hold.large.references.18` | Python engine | 0.0235× | 0.0225–0.0245× | 6.50× | SLOWDOWN |
| holdout | `hold.large.references.18` | Native C engine | 1.4267× | 1.3943–1.4607× | 0.08× | FASTER |
| holdout | `hold.large.references.18` | Rust engine | 0.2095× | 0.1920–0.2207× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.19` | Python engine | 0.0245× | 0.0235–0.0256× | 6.50× | SLOWDOWN |
| holdout | `hold.large.references.19` | Native C engine | 1.2896× | 1.1923–1.3653× | 0.08× | FASTER |
| holdout | `hold.large.references.19` | Rust engine | 0.2213× | 0.2166–0.2266× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.20` | Python engine | 0.0211× | 0.0206–0.0217× | 6.45× | SLOWDOWN |
| holdout | `hold.large.references.20` | Native C engine | 1.4655× | 1.3937–1.5128× | 0.08× | FASTER |
| holdout | `hold.large.references.20` | Rust engine | 0.1797× | 0.1636–0.1914× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.21` | Python engine | 0.0233× | 0.0223–0.0246× | 6.44× | SLOWDOWN |
| holdout | `hold.large.references.21` | Native C engine | 1.4873× | 1.4601–1.5148× | 0.08× | FASTER |
| holdout | `hold.large.references.21` | Rust engine | 0.1975× | 0.1770–0.2128× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.22` | Python engine | 0.0230× | 0.0220–0.0238× | 6.50× | SLOWDOWN |
| holdout | `hold.large.references.22` | Native C engine | 1.3589× | 1.2342–1.4414× | 0.08× | FASTER |
| holdout | `hold.large.references.22` | Rust engine | 0.1728× | 0.1218–0.2117× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.23` | Python engine | 0.0257× | 0.0224–0.0330× | 7.01× | SLOWDOWN |
| holdout | `hold.large.references.23` | Native C engine | 1.7872× | 1.5481–2.3060× | 0.00× | FASTER |
| holdout | `hold.large.references.23` | Rust engine | 0.3174× | 0.2685–0.4179× | 0.00× | SLOWDOWN |
| holdout | `hold.large.references.24` | Python engine | 0.0238× | 0.0225–0.0253× | 6.44× | SLOWDOWN |
| holdout | `hold.large.references.24` | Native C engine | 1.6010× | 1.5184–1.7284× | 0.08× | FASTER |
| holdout | `hold.large.references.24` | Rust engine | 0.2160× | 0.2070–0.2314× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.25` | Python engine | 0.0220× | 0.0205–0.0242× | 6.45× | SLOWDOWN |
| holdout | `hold.large.references.25` | Native C engine | 1.5451× | 1.4810–1.6568× | 0.08× | FASTER |
| holdout | `hold.large.references.25` | Rust engine | 0.2018× | 0.1888–0.2150× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.26` | Python engine | 0.0232× | 0.0224–0.0243× | 6.50× | SLOWDOWN |
| holdout | `hold.large.references.26` | Native C engine | 1.4828× | 1.4431–1.5409× | 0.08× | FASTER |
| holdout | `hold.large.references.26` | Rust engine | 0.2075× | 0.2014–0.2175× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.27` | Python engine | 0.0263× | 0.0257–0.0269× | 6.50× | SLOWDOWN |
| holdout | `hold.large.references.27` | Native C engine | 1.3909× | 1.3531–1.4281× | 0.08× | FASTER |
| holdout | `hold.large.references.27` | Rust engine | 0.2293× | 0.2236–0.2345× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.28` | Python engine | 0.0223× | 0.0208–0.0242× | 6.45× | SLOWDOWN |
| holdout | `hold.large.references.28` | Native C engine | 1.4024× | 1.2711–1.5031× | 0.08× | FASTER |
| holdout | `hold.large.references.28` | Rust engine | 0.2030× | 0.1872–0.2229× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.29` | Python engine | 0.0205× | 0.0197–0.0212× | 6.95× | SLOWDOWN |
| holdout | `hold.large.references.29` | Native C engine | 1.6645× | 1.5343–1.7690× | 0.00× | FASTER |
| holdout | `hold.large.references.29` | Rust engine | 0.2470× | 0.2382–0.2533× | 0.00× | SLOWDOWN |
| holdout | `hold.large.references.30` | Python engine | 0.0242× | 0.0238–0.0245× | 6.50× | SLOWDOWN |
| holdout | `hold.large.references.30` | Native C engine | 1.4356× | 1.4034–1.4664× | 0.08× | FASTER |
| holdout | `hold.large.references.30` | Rust engine | 0.2136× | 0.2084–0.2183× | 0.06× | SLOWDOWN |
| holdout | `hold.large.references.31` | Python engine | 0.0248× | 0.0242–0.0254× | 6.50× | SLOWDOWN |
| holdout | `hold.large.references.31` | Native C engine | 1.3525× | 1.3066–1.3955× | 0.08× | FASTER |
| holdout | `hold.large.references.31` | Rust engine | 0.2205× | 0.2158–0.2249× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.00` | Python engine | 0.0270× | 0.0263–0.0275× | 6.52× | SLOWDOWN |
| holdout | `hold.large.conditionals.00` | Native C engine | 1.4428× | 1.4140–1.4667× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.00` | Rust engine | 0.1736× | 0.1690–0.1772× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.01` | Python engine | 0.0273× | 0.0268–0.0277× | 6.52× | SLOWDOWN |
| holdout | `hold.large.conditionals.01` | Native C engine | 1.4135× | 1.4006–1.4281× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.01` | Rust engine | 0.1849× | 0.1829–0.1869× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.02` | Python engine | 0.0287× | 0.0280–0.0293× | 6.57× | SLOWDOWN |
| holdout | `hold.large.conditionals.02` | Native C engine | 1.4025× | 1.3810–1.4284× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.02` | Rust engine | 0.1758× | 0.1723–0.1797× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.03` | Python engine | 0.0301× | 0.0295–0.0307× | 6.57× | SLOWDOWN |
| holdout | `hold.large.conditionals.03` | Native C engine | 1.1220× | 0.9133–1.3087× | 0.08× | — |
| holdout | `hold.large.conditionals.03` | Rust engine | 0.1740× | 0.1576–0.1846× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.04` | Python engine | 0.0267× | 0.0262–0.0271× | 6.52× | SLOWDOWN |
| holdout | `hold.large.conditionals.04` | Native C engine | 1.4357× | 1.4156–1.4538× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.04` | Rust engine | 0.1708× | 0.1621–0.1766× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.05` | Python engine | 0.0275× | 0.0271–0.0278× | 6.52× | SLOWDOWN |
| holdout | `hold.large.conditionals.05` | Native C engine | 1.4162× | 1.3980–1.4352× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.05` | Rust engine | 0.1691× | 0.1669–0.1715× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.06` | Python engine | 0.0288× | 0.0284–0.0292× | 6.57× | SLOWDOWN |
| holdout | `hold.large.conditionals.06` | Native C engine | 1.3928× | 1.3529–1.4240× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.06` | Rust engine | 0.1778× | 0.1755–0.1801× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.07` | Python engine | 0.0296× | 0.0284–0.0306× | 6.57× | SLOWDOWN |
| holdout | `hold.large.conditionals.07` | Native C engine | 1.3271× | 1.2733–1.3710× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.07` | Rust engine | 0.1927× | 0.1886–0.1967× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.08` | Python engine | 0.0277× | 0.0267–0.0292× | 6.52× | SLOWDOWN |
| holdout | `hold.large.conditionals.08` | Native C engine | 1.4065× | 1.2829–1.5202× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.08` | Rust engine | 0.1693× | 0.1615–0.1798× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.09` | Python engine | 0.0277× | 0.0268–0.0284× | 6.52× | SLOWDOWN |
| holdout | `hold.large.conditionals.09` | Native C engine | 1.4292× | 1.4068–1.4523× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.09` | Rust engine | 0.1705× | 0.1646–0.1749× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.10` | Python engine | 0.0283× | 0.0279–0.0287× | 6.57× | SLOWDOWN |
| holdout | `hold.large.conditionals.10` | Native C engine | 1.3867× | 1.3590–1.4176× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.10` | Rust engine | 0.1779× | 0.1705–0.1831× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.11` | Python engine | 0.0308× | 0.0304–0.0312× | 6.57× | SLOWDOWN |
| holdout | `hold.large.conditionals.11` | Native C engine | 1.3562× | 1.3315–1.3816× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.11` | Rust engine | 0.1880× | 0.1852–0.1910× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.12` | Python engine | 0.0269× | 0.0266–0.0272× | 6.52× | SLOWDOWN |
| holdout | `hold.large.conditionals.12` | Native C engine | 1.4355× | 1.4139–1.4549× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.12` | Rust engine | 0.1675× | 0.1652–0.1695× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.13` | Python engine | 0.0287× | 0.0272–0.0316× | 6.52× | SLOWDOWN |
| holdout | `hold.large.conditionals.13` | Native C engine | 1.4856× | 1.4088–1.6324× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.13` | Rust engine | 0.1846× | 0.1748–0.2037× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.14` | Python engine | 0.0284× | 0.0278–0.0290× | 6.57× | SLOWDOWN |
| holdout | `hold.large.conditionals.14` | Native C engine | 1.3937× | 1.3600–1.4285× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.14` | Rust engine | 0.1764× | 0.1726–0.1803× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.15` | Python engine | 0.0302× | 0.0291–0.0314× | 6.57× | SLOWDOWN |
| holdout | `hold.large.conditionals.15` | Native C engine | 1.3755× | 1.3351–1.4161× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.15` | Rust engine | 0.1894× | 0.1858–0.1936× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.16` | Python engine | 0.0287× | 0.0270–0.0317× | 6.52× | SLOWDOWN |
| holdout | `hold.large.conditionals.16` | Native C engine | 1.5200× | 1.4317–1.6841× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.16` | Rust engine | 0.1866× | 0.1756–0.2067× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.17` | Python engine | 0.0287× | 0.0273–0.0313× | 6.52× | SLOWDOWN |
| holdout | `hold.large.conditionals.17` | Native C engine | 1.4854× | 1.4163–1.6177× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.17` | Rust engine | 0.1786× | 0.1700–0.1948× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.18` | Python engine | 0.0284× | 0.0278–0.0289× | 6.57× | SLOWDOWN |
| holdout | `hold.large.conditionals.18` | Native C engine | 1.3696× | 1.3307–1.4020× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.18` | Rust engine | 0.1764× | 0.1745–0.1785× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.19` | Python engine | 0.0307× | 0.0297–0.0320× | 6.57× | SLOWDOWN |
| holdout | `hold.large.conditionals.19` | Native C engine | 1.3696× | 1.3156–1.4383× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.19` | Rust engine | 0.1901× | 0.1744–0.2021× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.20` | Python engine | 0.0271× | 0.0267–0.0274× | 6.52× | SLOWDOWN |
| holdout | `hold.large.conditionals.20` | Native C engine | 1.4324× | 1.4133–1.4532× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.20` | Rust engine | 0.1670× | 0.1627–0.1701× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.21` | Python engine | 0.0276× | 0.0272–0.0280× | 6.52× | SLOWDOWN |
| holdout | `hold.large.conditionals.21` | Native C engine | 1.3511× | 1.2182–1.4340× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.21` | Rust engine | 0.1702× | 0.1647–0.1741× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.22` | Python engine | 0.0290× | 0.0283–0.0295× | 6.57× | SLOWDOWN |
| holdout | `hold.large.conditionals.22` | Native C engine | 1.4169× | 1.3914–1.4403× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.22` | Rust engine | 0.1853× | 0.1828–0.1878× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.23` | Python engine | 0.0306× | 0.0301–0.0312× | 6.57× | SLOWDOWN |
| holdout | `hold.large.conditionals.23` | Native C engine | 1.3609× | 1.3237–1.3980× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.23` | Rust engine | 0.1850× | 0.1782–0.1906× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.24` | Python engine | 0.0284× | 0.0267–0.0306× | 6.52× | SLOWDOWN |
| holdout | `hold.large.conditionals.24` | Native C engine | 1.5223× | 1.4078–1.6518× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.24` | Rust engine | 0.1754× | 0.1657–0.1887× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.25` | Python engine | 0.0259× | 0.0248–0.0269× | 6.52× | SLOWDOWN |
| holdout | `hold.large.conditionals.25` | Native C engine | 1.3741× | 1.2928–1.4311× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.25` | Rust engine | 0.1792× | 0.1767–0.1819× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.26` | Python engine | 0.0282× | 0.0277–0.0288× | 6.57× | SLOWDOWN |
| holdout | `hold.large.conditionals.26` | Native C engine | 1.3819× | 1.3563–1.4069× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.26` | Rust engine | 0.1641× | 0.1607–0.1672× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.27` | Python engine | 0.0307× | 0.0302–0.0314× | 6.57× | SLOWDOWN |
| holdout | `hold.large.conditionals.27` | Native C engine | 1.3686× | 1.3315–1.4044× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.27` | Rust engine | 0.1748× | 0.1708–0.1786× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.28` | Python engine | 0.0272× | 0.0266–0.0280× | 6.52× | SLOWDOWN |
| holdout | `hold.large.conditionals.28` | Native C engine | 1.3959× | 1.3249–1.4422× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.28` | Rust engine | 0.1592× | 0.1530–0.1643× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.29` | Python engine | 0.0271× | 0.0263–0.0280× | 6.52× | SLOWDOWN |
| holdout | `hold.large.conditionals.29` | Native C engine | 1.3376× | 1.1692–1.5147× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.29` | Rust engine | 0.1552× | 0.1410–0.1667× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.30` | Python engine | 0.0291× | 0.0273–0.0317× | 6.57× | SLOWDOWN |
| holdout | `hold.large.conditionals.30` | Native C engine | 1.4250× | 1.3597–1.5350× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.30` | Rust engine | 0.1700× | 0.1624–0.1830× | 0.06× | SLOWDOWN |
| holdout | `hold.large.conditionals.31` | Python engine | 0.0301× | 0.0292–0.0307× | 6.57× | SLOWDOWN |
| holdout | `hold.large.conditionals.31` | Native C engine | 1.3778× | 1.3455–1.4182× | 0.08× | FASTER |
| holdout | `hold.large.conditionals.31` | Rust engine | 0.1820× | 0.1795–0.1846× | 0.06× | SLOWDOWN |
| holdout | `hold.large.branch-control.00` | Python engine | 0.0163× | 0.0148–0.0186× | 8.19× | SLOWDOWN |
| holdout | `hold.large.branch-control.00` | Native C engine | 1.2943× | 1.2347–1.4094× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.00` | Rust engine | 0.1496× | 0.1401–0.1653× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.01` | Python engine | 0.0128× | 0.0127–0.0129× | 9.69× | SLOWDOWN |
| holdout | `hold.large.branch-control.01` | Native C engine | 1.5101× | 1.4982–1.5234× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.01` | Rust engine | 0.1575× | 0.1562–0.1589× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.02` | Python engine | 0.0115× | 0.0109–0.0126× | 12.53× | SLOWDOWN |
| holdout | `hold.large.branch-control.02` | Native C engine | 2.0183× | 1.9024–2.2232× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.02` | Rust engine | 0.1750× | 0.1655–0.1930× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.03` | Python engine | 0.0096× | 0.0095–0.0097× | 18.23× | SLOWDOWN |
| holdout | `hold.large.branch-control.03` | Native C engine | 2.3462× | 2.2762–2.4127× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.03` | Rust engine | 0.1751× | 0.1732–0.1771× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.04` | Python engine | 0.0161× | 0.0151–0.0176× | 8.19× | SLOWDOWN |
| holdout | `hold.large.branch-control.04` | Native C engine | 1.2093× | 1.0860–1.3320× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.04` | Rust engine | 0.1449× | 0.1414–0.1490× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.05` | Python engine | 0.0136× | 0.0127–0.0154× | 9.69× | SLOWDOWN |
| holdout | `hold.large.branch-control.05` | Native C engine | 1.6013× | 1.4903–1.8080× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.05` | Rust engine | 0.1683× | 0.1571–0.1904× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.06` | Python engine | 0.0115× | 0.0109–0.0127× | 12.53× | SLOWDOWN |
| holdout | `hold.large.branch-control.06` | Native C engine | 1.8839× | 1.7101–2.1348× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.06` | Rust engine | 0.1778× | 0.1688–0.1959× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.07` | Python engine | 0.0096× | 0.0095–0.0097× | 18.23× | SLOWDOWN |
| holdout | `hold.large.branch-control.07` | Native C engine | 2.3535× | 2.3153–2.3907× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.07` | Rust engine | 0.1753× | 0.1701–0.1792× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.08` | Python engine | 0.0151× | 0.0150–0.0151× | 8.19× | SLOWDOWN |
| holdout | `hold.large.branch-control.08` | Native C engine | 1.2295× | 1.2201–1.2412× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.08` | Rust engine | 0.1442× | 0.1419–0.1457× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.09` | Python engine | 0.0129× | 0.0128–0.0130× | 9.69× | SLOWDOWN |
| holdout | `hold.large.branch-control.09` | Native C engine | 1.5018× | 1.4802–1.5210× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.09` | Rust engine | 0.1557× | 0.1512–0.1595× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.10` | Python engine | 0.0109× | 0.0107–0.0110× | 12.53× | SLOWDOWN |
| holdout | `hold.large.branch-control.10` | Native C engine | 1.8833× | 1.8471–1.9211× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.10` | Rust engine | 0.1682× | 0.1653–0.1711× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.11` | Python engine | 0.0096× | 0.0095–0.0098× | 18.23× | SLOWDOWN |
| holdout | `hold.large.branch-control.11` | Native C engine | 2.4149× | 2.3665–2.4593× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.11` | Rust engine | 0.1783× | 0.1760–0.1810× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.12` | Python engine | 0.0151× | 0.0135–0.0169× | 8.19× | SLOWDOWN |
| holdout | `hold.large.branch-control.12` | Native C engine | 1.1276× | 0.9623–1.2963× | 0.63× | — |
| holdout | `hold.large.branch-control.12` | Rust engine | 0.1395× | 0.1239–0.1553× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.13` | Python engine | 0.0129× | 0.0125–0.0135× | 9.69× | SLOWDOWN |
| holdout | `hold.large.branch-control.13` | Native C engine | 1.4807× | 1.3628–1.5974× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.13` | Rust engine | 0.1565× | 0.1510–0.1644× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.14` | Python engine | 0.0110× | 0.0109–0.0111× | 12.53× | SLOWDOWN |
| holdout | `hold.large.branch-control.14` | Native C engine | 1.9103× | 1.8767–1.9427× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.14` | Rust engine | 0.1687× | 0.1667–0.1708× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.15` | Python engine | 0.0097× | 0.0096–0.0098× | 18.23× | SLOWDOWN |
| holdout | `hold.large.branch-control.15` | Native C engine | 2.3316× | 2.2652–2.4008× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.15` | Rust engine | 0.1774× | 0.1756–0.1793× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.16` | Python engine | 0.0158× | 0.0150–0.0174× | 8.19× | SLOWDOWN |
| holdout | `hold.large.branch-control.16` | Native C engine | 1.2496× | 1.1066–1.4289× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.16` | Rust engine | 0.1521× | 0.1441–0.1673× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.17` | Python engine | 0.0127× | 0.0126–0.0127× | 9.69× | SLOWDOWN |
| holdout | `hold.large.branch-control.17` | Native C engine | 1.4877× | 1.4682–1.5059× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.17` | Rust engine | 0.1571× | 0.1561–0.1582× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.18` | Python engine | 0.0109× | 0.0108–0.0111× | 12.53× | SLOWDOWN |
| holdout | `hold.large.branch-control.18` | Native C engine | 1.8879× | 1.8303–1.9430× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.18` | Rust engine | 0.1692× | 0.1672–0.1714× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.19` | Python engine | 0.0096× | 0.0095–0.0097× | 18.23× | SLOWDOWN |
| holdout | `hold.large.branch-control.19` | Native C engine | 2.3265× | 2.2779–2.3779× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.19` | Rust engine | 0.1789× | 0.1767–0.1814× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.20` | Python engine | 0.0151× | 0.0150–0.0152× | 8.19× | SLOWDOWN |
| holdout | `hold.large.branch-control.20` | Native C engine | 1.1991× | 1.1123–1.2475× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.20` | Rust engine | 0.1447× | 0.1432–0.1459× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.21` | Python engine | 0.0126× | 0.0125–0.0127× | 9.69× | SLOWDOWN |
| holdout | `hold.large.branch-control.21` | Native C engine | 1.4937× | 1.4764–1.5088× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.21` | Rust engine | 0.1566× | 0.1550–0.1582× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.22` | Python engine | 0.0109× | 0.0108–0.0110× | 12.53× | SLOWDOWN |
| holdout | `hold.large.branch-control.22` | Native C engine | 1.8861× | 1.8644–1.9071× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.22` | Rust engine | 0.1667× | 0.1645–0.1685× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.23` | Python engine | 0.0098× | 0.0096–0.0099× | 18.23× | SLOWDOWN |
| holdout | `hold.large.branch-control.23` | Native C engine | 2.4424× | 2.3956–2.4920× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.23` | Rust engine | 0.1777× | 0.1709–0.1824× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.24` | Python engine | 0.0157× | 0.0151–0.0167× | 8.19× | SLOWDOWN |
| holdout | `hold.large.branch-control.24` | Native C engine | 1.2702× | 1.2175–1.3645× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.24` | Rust engine | 0.1473× | 0.1374–0.1597× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.25` | Python engine | 0.0127× | 0.0126–0.0128× | 9.69× | SLOWDOWN |
| holdout | `hold.large.branch-control.25` | Native C engine | 1.4973× | 1.4793–1.5177× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.25` | Rust engine | 0.1566× | 0.1555–0.1579× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.26` | Python engine | 0.0109× | 0.0108–0.0110× | 12.53× | SLOWDOWN |
| holdout | `hold.large.branch-control.26` | Native C engine | 1.9023× | 1.8716–1.9363× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.26` | Rust engine | 0.1666× | 0.1627–0.1696× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.27` | Python engine | 0.0096× | 0.0092–0.0098× | 18.23× | SLOWDOWN |
| holdout | `hold.large.branch-control.27` | Native C engine | 2.4176× | 2.3675–2.4684× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.27` | Rust engine | 0.1756× | 0.1693–0.1802× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.28` | Python engine | 0.0149× | 0.0148–0.0151× | 8.19× | SLOWDOWN |
| holdout | `hold.large.branch-control.28` | Native C engine | 1.2169× | 1.2081–1.2262× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.28` | Rust engine | 0.1410× | 0.1374–0.1441× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.29` | Python engine | 0.0125× | 0.0123–0.0127× | 9.69× | SLOWDOWN |
| holdout | `hold.large.branch-control.29` | Native C engine | 1.5010× | 1.4856–1.5166× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.29` | Rust engine | 0.1574× | 0.1550–0.1596× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.30` | Python engine | 0.0111× | 0.0108–0.0114× | 12.53× | SLOWDOWN |
| holdout | `hold.large.branch-control.30` | Native C engine | 1.8703× | 1.8154–1.9436× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.30` | Rust engine | 0.1685× | 0.1632–0.1744× | 0.07× | SLOWDOWN |
| holdout | `hold.large.branch-control.31` | Python engine | 0.0096× | 0.0092–0.0099× | 18.23× | SLOWDOWN |
| holdout | `hold.large.branch-control.31` | Native C engine | 2.4055× | 2.3490–2.4619× | 0.63× | FASTER |
| holdout | `hold.large.branch-control.31` | Rust engine | 0.1743× | 0.1644–0.1809× | 0.07× | SLOWDOWN |
| holdout | `hold.large.scanner-text.00` | Python engine | 0.0231× | 0.0223–0.0243× | 7.30× | SLOWDOWN |
| holdout | `hold.large.scanner-text.00` | Native C engine | 1.5540× | 1.4936–1.6386× | 0.34× | FASTER |
| holdout | `hold.large.scanner-text.00` | Rust engine | 0.1405× | 0.1352–0.1466× | 0.16× | SLOWDOWN |
| holdout | `hold.large.scanner-text.01` | Python engine | 0.0209× | 0.0207–0.0211× | 7.53× | SLOWDOWN |
| holdout | `hold.large.scanner-text.01` | Native C engine | 1.6505× | 1.6344–1.6668× | 0.40× | FASTER |
| holdout | `hold.large.scanner-text.01` | Rust engine | 0.1314× | 0.1297–0.1329× | 0.21× | SLOWDOWN |
| holdout | `hold.large.scanner-text.02` | Python engine | 0.0177× | 0.0170–0.0187× | 7.76× | SLOWDOWN |
| holdout | `hold.large.scanner-text.02` | Native C engine | 1.5881× | 1.5225–1.6872× | 0.50× | FASTER |
| holdout | `hold.large.scanner-text.02` | Rust engine | 0.1116× | 0.1075–0.1183× | 0.29× | SLOWDOWN |
| holdout | `hold.large.scanner-text.03` | Python engine | 0.0205× | 0.0192–0.0230× | 8.26× | SLOWDOWN |
| holdout | `hold.large.scanner-text.03` | Native C engine | 1.9750× | 1.8494–2.1903× | 0.60× | FASTER |
| holdout | `hold.large.scanner-text.03` | Rust engine | 0.1294× | 0.1197–0.1457× | 0.38× | SLOWDOWN |
| holdout | `hold.large.scanner-text.04` | Python engine | 0.0222× | 0.0219–0.0224× | 7.30× | SLOWDOWN |
| holdout | `hold.large.scanner-text.04` | Native C engine | 1.5025× | 1.4841–1.5212× | 0.34× | FASTER |
| holdout | `hold.large.scanner-text.04` | Rust engine | 0.1358× | 0.1345–0.1371× | 0.16× | SLOWDOWN |
| holdout | `hold.large.scanner-text.05` | Python engine | 0.0214× | 0.0207–0.0226× | 7.53× | SLOWDOWN |
| holdout | `hold.large.scanner-text.05` | Native C engine | 1.7237× | 1.6688–1.8053× | 0.40× | FASTER |
| holdout | `hold.large.scanner-text.05` | Rust engine | 0.1332× | 0.1288–0.1400× | 0.21× | SLOWDOWN |
| holdout | `hold.large.scanner-text.06` | Python engine | 0.0170× | 0.0167–0.0173× | 7.76× | SLOWDOWN |
| holdout | `hold.large.scanner-text.06` | Native C engine | 1.5696× | 1.5377–1.6046× | 0.50× | FASTER |
| holdout | `hold.large.scanner-text.06` | Rust engine | 0.1071× | 0.1047–0.1094× | 0.29× | SLOWDOWN |
| holdout | `hold.large.scanner-text.07` | Python engine | 0.0196× | 0.0193–0.0199× | 8.26× | SLOWDOWN |
| holdout | `hold.large.scanner-text.07` | Native C engine | 1.8864× | 1.8562–1.9166× | 0.60× | FASTER |
| holdout | `hold.large.scanner-text.07` | Rust engine | 0.1239× | 0.1204–0.1268× | 0.38× | SLOWDOWN |
| holdout | `hold.large.scanner-text.08` | Python engine | 0.0220× | 0.0216–0.0224× | 7.30× | SLOWDOWN |
| holdout | `hold.large.scanner-text.08` | Native C engine | 1.4831× | 1.4490–1.5148× | 0.34× | FASTER |
| holdout | `hold.large.scanner-text.08` | Rust engine | 0.1320× | 0.1274–0.1356× | 0.16× | SLOWDOWN |
| holdout | `hold.large.scanner-text.09` | Python engine | 0.0200× | 0.0190–0.0213× | 7.53× | SLOWDOWN |
| holdout | `hold.large.scanner-text.09` | Native C engine | 1.6217× | 1.5394–1.7265× | 0.40× | FASTER |
| holdout | `hold.large.scanner-text.09` | Rust engine | 0.1206× | 0.1144–0.1284× | 0.21× | SLOWDOWN |
| holdout | `hold.large.scanner-text.10` | Python engine | 0.0178× | 0.0165–0.0197× | 7.76× | SLOWDOWN |
| holdout | `hold.large.scanner-text.10` | Native C engine | 1.6065× | 1.5006–1.7496× | 0.50× | FASTER |
| holdout | `hold.large.scanner-text.10` | Rust engine | 0.1126× | 0.1051–0.1227× | 0.29× | SLOWDOWN |
| holdout | `hold.large.scanner-text.11` | Python engine | 0.0170× | 0.0167–0.0173× | 8.26× | SLOWDOWN |
| holdout | `hold.large.scanner-text.11` | Native C engine | 1.6284× | 1.5929–1.6612× | 0.60× | FASTER |
| holdout | `hold.large.scanner-text.11` | Rust engine | 0.1074× | 0.1047–0.1100× | 0.38× | SLOWDOWN |
| holdout | `hold.large.scanner-text.12` | Python engine | 0.0200× | 0.0196–0.0205× | 7.30× | SLOWDOWN |
| holdout | `hold.large.scanner-text.12` | Native C engine | 1.3070× | 1.1708–1.3979× | 0.34× | FASTER |
| holdout | `hold.large.scanner-text.12` | Rust engine | 0.1212× | 0.1181–0.1240× | 0.16× | SLOWDOWN |
| holdout | `hold.large.scanner-text.13` | Python engine | 0.0180× | 0.0174–0.0185× | 7.53× | SLOWDOWN |
| holdout | `hold.large.scanner-text.13` | Native C engine | 1.4663× | 1.4439–1.4862× | 0.40× | FASTER |
| holdout | `hold.large.scanner-text.13` | Rust engine | 0.1103× | 0.1074–0.1127× | 0.21× | SLOWDOWN |
| holdout | `hold.large.scanner-text.14` | Python engine | 0.0170× | 0.0168–0.0173× | 7.76× | SLOWDOWN |
| holdout | `hold.large.scanner-text.14` | Native C engine | 1.4627× | 1.3466–1.5538× | 0.50× | FASTER |
| holdout | `hold.large.scanner-text.14` | Rust engine | 0.1071× | 0.1051–0.1089× | 0.29× | SLOWDOWN |
| holdout | `hold.large.scanner-text.15` | Python engine | 0.0196× | 0.0193–0.0198× | 8.26× | SLOWDOWN |
| holdout | `hold.large.scanner-text.15` | Native C engine | 1.7922× | 1.6198–1.9148× | 0.60× | FASTER |
| holdout | `hold.large.scanner-text.15` | Rust engine | 0.1245× | 0.1226–0.1264× | 0.38× | SLOWDOWN |
| holdout | `hold.large.scanner-text.16` | Python engine | 0.0229× | 0.0222–0.0237× | 7.30× | SLOWDOWN |
| holdout | `hold.large.scanner-text.16` | Native C engine | 1.5427× | 1.4959–1.6037× | 0.34× | FASTER |
| holdout | `hold.large.scanner-text.16` | Rust engine | 0.1392× | 0.1347–0.1452× | 0.16× | SLOWDOWN |
| holdout | `hold.large.scanner-text.17` | Python engine | 0.0215× | 0.0206–0.0229× | 7.53× | SLOWDOWN |
| holdout | `hold.large.scanner-text.17` | Native C engine | 1.7703× | 1.6911–1.9040× | 0.40× | FASTER |
| holdout | `hold.large.scanner-text.17` | Rust engine | 0.1349× | 0.1286–0.1442× | 0.21× | SLOWDOWN |
| holdout | `hold.large.scanner-text.18` | Python engine | 0.0173× | 0.0171–0.0175× | 7.76× | SLOWDOWN |
| holdout | `hold.large.scanner-text.18` | Native C engine | 1.5591× | 1.5341–1.5873× | 0.50× | FASTER |
| holdout | `hold.large.scanner-text.18` | Rust engine | 0.1099× | 0.1087–0.1113× | 0.29× | SLOWDOWN |
| holdout | `hold.large.scanner-text.19` | Python engine | 0.0199× | 0.0194–0.0206× | 8.26× | SLOWDOWN |
| holdout | `hold.large.scanner-text.19` | Native C engine | 1.9175× | 1.8587–1.9858× | 0.60× | FASTER |
| holdout | `hold.large.scanner-text.19` | Rust engine | 0.1245× | 0.1207–0.1292× | 0.38× | SLOWDOWN |
| holdout | `hold.large.scanner-text.20` | Python engine | 0.0220× | 0.0212–0.0230× | 7.30× | SLOWDOWN |
| holdout | `hold.large.scanner-text.20` | Native C engine | 1.4023× | 1.2476–1.5409× | 0.34× | FASTER |
| holdout | `hold.large.scanner-text.20` | Rust engine | 0.1301× | 0.1196–0.1404× | 0.16× | SLOWDOWN |
| holdout | `hold.large.scanner-text.21` | Python engine | 0.0192× | 0.0185–0.0199× | 7.53× | SLOWDOWN |
| holdout | `hold.large.scanner-text.21` | Native C engine | 1.5590× | 1.5008–1.6245× | 0.40× | FASTER |
| holdout | `hold.large.scanner-text.21` | Rust engine | 0.1194× | 0.1152–0.1239× | 0.21× | SLOWDOWN |
| holdout | `hold.large.scanner-text.22` | Python engine | 0.0172× | 0.0167–0.0177× | 7.76× | SLOWDOWN |
| holdout | `hold.large.scanner-text.22` | Native C engine | 1.5434× | 1.5082–1.5779× | 0.50× | FASTER |
| holdout | `hold.large.scanner-text.22` | Rust engine | 0.1069× | 0.1035–0.1102× | 0.29× | SLOWDOWN |
| holdout | `hold.large.scanner-text.23` | Python engine | 0.0174× | 0.0172–0.0177× | 8.26× | SLOWDOWN |
| holdout | `hold.large.scanner-text.23` | Native C engine | 1.6565× | 1.6289–1.6847× | 0.60× | FASTER |
| holdout | `hold.large.scanner-text.23` | Rust engine | 0.1104× | 0.1084–0.1125× | 0.38× | SLOWDOWN |
| holdout | `hold.large.scanner-text.24` | Python engine | 0.0203× | 0.0195–0.0216× | 7.30× | SLOWDOWN |
| holdout | `hold.large.scanner-text.24` | Native C engine | 1.4056× | 1.3486–1.4939× | 0.34× | FASTER |
| holdout | `hold.large.scanner-text.24` | Rust engine | 0.1225× | 0.1168–0.1308× | 0.16× | SLOWDOWN |
| holdout | `hold.large.scanner-text.25` | Python engine | 0.0184× | 0.0182–0.0187× | 7.53× | SLOWDOWN |
| holdout | `hold.large.scanner-text.25` | Native C engine | 1.5034× | 1.4767–1.5337× | 0.40× | FASTER |
| holdout | `hold.large.scanner-text.25` | Rust engine | 0.1151× | 0.1133–0.1168× | 0.21× | SLOWDOWN |
| holdout | `hold.large.scanner-text.26` | Python engine | 0.0175× | 0.0172–0.0177× | 7.76× | SLOWDOWN |
| holdout | `hold.large.scanner-text.26` | Native C engine | 1.5939× | 1.5626–1.6256× | 0.50× | FASTER |
| holdout | `hold.large.scanner-text.26` | Rust engine | 0.1100× | 0.1078–0.1120× | 0.29× | SLOWDOWN |
| holdout | `hold.large.scanner-text.27` | Python engine | 0.0173× | 0.0170–0.0176× | 8.26× | SLOWDOWN |
| holdout | `hold.large.scanner-text.27` | Native C engine | 1.6581× | 1.6085–1.7024× | 0.60× | FASTER |
| holdout | `hold.large.scanner-text.27` | Rust engine | 0.1094× | 0.1061–0.1120× | 0.38× | SLOWDOWN |
| holdout | `hold.large.scanner-text.28` | Python engine | 0.0198× | 0.0195–0.0201× | 7.30× | SLOWDOWN |
| holdout | `hold.large.scanner-text.28` | Native C engine | 1.3628× | 1.3350–1.3903× | 0.34× | FASTER |
| holdout | `hold.large.scanner-text.28` | Rust engine | 0.1220× | 0.1200–0.1238× | 0.16× | SLOWDOWN |
| holdout | `hold.large.scanner-text.29` | Python engine | 0.0185× | 0.0183–0.0187× | 7.53× | SLOWDOWN |
| holdout | `hold.large.scanner-text.29` | Native C engine | 1.5236× | 1.5024–1.5429× | 0.40× | FASTER |
| holdout | `hold.large.scanner-text.29` | Rust engine | 0.1142× | 0.1128–0.1158× | 0.21× | SLOWDOWN |
| holdout | `hold.large.scanner-text.30` | Python engine | 0.0174× | 0.0170–0.0177× | 7.76× | SLOWDOWN |
| holdout | `hold.large.scanner-text.30` | Native C engine | 1.4899× | 1.3532–1.5876× | 0.50× | FASTER |
| holdout | `hold.large.scanner-text.30` | Rust engine | 0.1087× | 0.1070–0.1104× | 0.29× | SLOWDOWN |
| holdout | `hold.large.scanner-text.31` | Python engine | 0.0170× | 0.0166–0.0175× | 8.26× | SLOWDOWN |
| holdout | `hold.large.scanner-text.31` | Native C engine | 1.6214× | 1.5756–1.6774× | 0.60× | FASTER |
| holdout | `hold.large.scanner-text.31` | Rust engine | 0.1076× | 0.1046–0.1113× | 0.38× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.00` | Python engine | 0.0196× | 0.0188–0.0209× | 7.36× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.00` | Native C engine | 1.3706× | 1.3036–1.4745× | 0.34× | FASTER |
| holdout | `hold.large.scanner-bytes.00` | Rust engine | 0.1057× | 0.1010–0.1129× | 0.34× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.01` | Python engine | 0.0180× | 0.0178–0.0182× | 7.69× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.01` | Native C engine | 1.4435× | 1.4250–1.4610× | 0.40× | FASTER |
| holdout | `hold.large.scanner-bytes.01` | Rust engine | 0.1018× | 0.1006–0.1031× | 0.30× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.02` | Python engine | 0.0172× | 0.0165–0.0184× | 8.12× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.02` | Native C engine | 1.5829× | 1.5150–1.7030× | 0.50× | FASTER |
| holdout | `hold.large.scanner-bytes.02` | Rust engine | 0.0991× | 0.0948–0.1069× | 0.41× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.03` | Python engine | 0.0169× | 0.0165–0.0176× | 8.87× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.03` | Native C engine | 1.5918× | 1.5424–1.6526× | 0.60× | FASTER |
| holdout | `hold.large.scanner-bytes.03` | Rust engine | 0.1002× | 0.0973–0.1042× | 0.42× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.04` | Python engine | 0.0187× | 0.0185–0.0189× | 7.37× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.04` | Native C engine | 1.3365× | 1.2909–1.3764× | 0.34× | FASTER |
| holdout | `hold.large.scanner-bytes.04` | Rust engine | 0.1016× | 0.1003–0.1028× | 0.34× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.05` | Python engine | 0.0175× | 0.0173–0.0176× | 7.69× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.05` | Native C engine | 1.4227× | 1.3986–1.4471× | 0.40× | FASTER |
| holdout | `hold.large.scanner-bytes.05` | Rust engine | 0.0984× | 0.0967–0.1001× | 0.30× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.06` | Python engine | 0.0165× | 0.0162–0.0167× | 8.12× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.06` | Native C engine | 1.5889× | 1.5567–1.6259× | 0.50× | FASTER |
| holdout | `hold.large.scanner-bytes.06` | Rust engine | 0.0959× | 0.0944–0.0974× | 0.41× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.07` | Python engine | 0.0165× | 0.0160–0.0169× | 8.87× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.07` | Native C engine | 1.5916× | 1.5562–1.6248× | 0.60× | FASTER |
| holdout | `hold.large.scanner-bytes.07` | Rust engine | 0.0943× | 0.0855–0.0999× | 0.42× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.08` | Python engine | 0.0192× | 0.0187–0.0198× | 7.37× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.08` | Native C engine | 1.4401× | 1.3581–1.5935× | 0.34× | FASTER |
| holdout | `hold.large.scanner-bytes.08` | Rust engine | 0.1031× | 0.1005–0.1060× | 0.34× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.09` | Python engine | 0.0177× | 0.0176–0.0179× | 7.69× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.09` | Native C engine | 1.4319× | 1.4193–1.4433× | 0.40× | FASTER |
| holdout | `hold.large.scanner-bytes.09` | Rust engine | 0.1020× | 0.1008–0.1032× | 0.30× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.10` | Python engine | 0.0169× | 0.0166–0.0172× | 8.15× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.10` | Native C engine | 1.5826× | 1.5442–1.6180× | 0.50× | FASTER |
| holdout | `hold.large.scanner-bytes.10` | Rust engine | 0.0969× | 0.0945–0.0990× | 0.41× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.11` | Python engine | 0.0167× | 0.0164–0.0169× | 8.87× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.11` | Native C engine | 1.5822× | 1.5418–1.6200× | 0.60× | FASTER |
| holdout | `hold.large.scanner-bytes.11` | Rust engine | 0.0994× | 0.0971–0.1014× | 0.42× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.12` | Python engine | 0.0188× | 0.0184–0.0191× | 7.37× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.12` | Native C engine | 1.3601× | 1.3269–1.3954× | 0.34× | FASTER |
| holdout | `hold.large.scanner-bytes.12` | Rust engine | 0.1019× | 0.1002–0.1038× | 0.34× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.13` | Python engine | 0.0182× | 0.0179–0.0185× | 7.69× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.13` | Native C engine | 1.4866× | 1.4525–1.5265× | 0.40× | FASTER |
| holdout | `hold.large.scanner-bytes.13` | Rust engine | 0.1044× | 0.1030–0.1064× | 0.30× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.14` | Python engine | 0.0166× | 0.0164–0.0168× | 8.12× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.14` | Native C engine | 1.4816× | 1.3287–1.5746× | 0.50× | FASTER |
| holdout | `hold.large.scanner-bytes.14` | Rust engine | 0.0960× | 0.0950–0.0971× | 0.41× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.15` | Python engine | 0.0171× | 0.0166–0.0178× | 8.94× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.15` | Native C engine | 1.6443× | 1.5897–1.7102× | 0.60× | FASTER |
| holdout | `hold.large.scanner-bytes.15` | Rust engine | 0.1009× | 0.0982–0.1048× | 0.42× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.16` | Python engine | 0.0187× | 0.0184–0.0190× | 7.37× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.16` | Native C engine | 1.3354× | 1.2911–1.3668× | 0.34× | FASTER |
| holdout | `hold.large.scanner-bytes.16` | Rust engine | 0.1017× | 0.1000–0.1034× | 0.34× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.17` | Python engine | 0.0178× | 0.0177–0.0179× | 7.69× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.17` | Native C engine | 1.3707× | 1.2095–1.4710× | 0.40× | FASTER |
| holdout | `hold.large.scanner-bytes.17` | Rust engine | 0.1025× | 0.1016–0.1032× | 0.30× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.18` | Python engine | 0.0168× | 0.0166–0.0170× | 8.12× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.18` | Native C engine | 1.5906× | 1.5643–1.6155× | 0.50× | FASTER |
| holdout | `hold.large.scanner-bytes.18` | Rust engine | 0.0970× | 0.0961–0.0979× | 0.41× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.19` | Python engine | 0.0171× | 0.0167–0.0177× | 8.87× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.19` | Native C engine | 1.6089× | 1.5634–1.6573× | 0.60× | FASTER |
| holdout | `hold.large.scanner-bytes.19` | Rust engine | 0.1021× | 0.0995–0.1055× | 0.42× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.20` | Python engine | 0.0195× | 0.0190–0.0200× | 7.37× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.20` | Native C engine | 1.4075× | 1.3663–1.4491× | 0.34× | FASTER |
| holdout | `hold.large.scanner-bytes.20` | Rust engine | 0.1055× | 0.1024–0.1085× | 0.34× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.21` | Python engine | 0.0179× | 0.0175–0.0182× | 7.69× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.21` | Native C engine | 1.4603× | 1.4203–1.5016× | 0.40× | FASTER |
| holdout | `hold.large.scanner-bytes.21` | Rust engine | 0.1019× | 0.0996–0.1042× | 0.30× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.22` | Python engine | 0.0168× | 0.0167–0.0170× | 8.12× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.22` | Native C engine | 1.5982× | 1.5680–1.6298× | 0.50× | FASTER |
| holdout | `hold.large.scanner-bytes.22` | Rust engine | 0.0967× | 0.0951–0.0980× | 0.41× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.23` | Python engine | 0.0169× | 0.0166–0.0172× | 8.87× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.23` | Native C engine | 1.5890× | 1.5642–1.6189× | 0.60× | FASTER |
| holdout | `hold.large.scanner-bytes.23` | Rust engine | 0.1011× | 0.1002–0.1021× | 0.42× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.24` | Python engine | 0.0193× | 0.0186–0.0204× | 7.37× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.24` | Native C engine | 1.3885× | 1.3383–1.4665× | 0.34× | FASTER |
| holdout | `hold.large.scanner-bytes.24` | Rust engine | 0.1045× | 0.1008–0.1110× | 0.34× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.25` | Python engine | 0.0178× | 0.0172–0.0187× | 7.69× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.25` | Native C engine | 1.4455× | 1.3958–1.5280× | 0.40× | FASTER |
| holdout | `hold.large.scanner-bytes.25` | Rust engine | 0.1008× | 0.0976–0.1056× | 0.30× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.26` | Python engine | 0.0170× | 0.0168–0.0173× | 8.15× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.26` | Native C engine | 1.6354× | 1.6077–1.6630× | 0.50× | FASTER |
| holdout | `hold.large.scanner-bytes.26` | Rust engine | 0.0970× | 0.0956–0.0984× | 0.41× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.27` | Python engine | 0.0171× | 0.0168–0.0174× | 8.94× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.27` | Native C engine | 1.5409× | 1.4118–1.6333× | 0.60× | FASTER |
| holdout | `hold.large.scanner-bytes.27` | Rust engine | 0.1015× | 0.1001–0.1030× | 0.42× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.28` | Python engine | 0.0196× | 0.0189–0.0207× | 7.37× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.28` | Native C engine | 1.4417× | 1.3911–1.5195× | 0.34× | FASTER |
| holdout | `hold.large.scanner-bytes.28` | Rust engine | 0.1059× | 0.1022–0.1116× | 0.34× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.29` | Python engine | 0.0180× | 0.0177–0.0182× | 7.71× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.29` | Native C engine | 1.4905× | 1.4677–1.5140× | 0.40× | FASTER |
| holdout | `hold.large.scanner-bytes.29` | Rust engine | 0.1019× | 0.1004–0.1034× | 0.30× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.30` | Python engine | 0.0170× | 0.0166–0.0173× | 8.15× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.30` | Native C engine | 1.6230× | 1.5878–1.6544× | 0.50× | FASTER |
| holdout | `hold.large.scanner-bytes.30` | Rust engine | 0.0979× | 0.0962–0.1001× | 0.41× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.31` | Python engine | 0.0169× | 0.0167–0.0171× | 8.94× | SLOWDOWN |
| holdout | `hold.large.scanner-bytes.31` | Native C engine | 1.6318× | 1.5938–1.6667× | 0.60× | FASTER |
| holdout | `hold.large.scanner-bytes.31` | Rust engine | 0.1008× | 0.0990–0.1025× | 0.42× | SLOWDOWN |
| holdout | `hold.large.window-search.00` | Python engine | 0.0397× | 0.0393–0.0401× | 3.92× | SLOWDOWN |
| holdout | `hold.large.window-search.00` | Native C engine | 0.8394× | 0.8179–0.8637× | 0.18× | — |
| holdout | `hold.large.window-search.00` | Rust engine | 0.2236× | 0.2217–0.2257× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.01` | Python engine | 0.0406× | 0.0403–0.0409× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.01` | Native C engine | 0.8562× | 0.8460–0.8710× | 0.18× | — |
| holdout | `hold.large.window-search.01` | Rust engine | 0.2254× | 0.2233–0.2274× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.02` | Python engine | 0.0400× | 0.0395–0.0405× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.02` | Native C engine | 0.8909× | 0.8683–0.9155× | 0.18× | — |
| holdout | `hold.large.window-search.02` | Rust engine | 0.2208× | 0.2174–0.2239× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.03` | Python engine | 0.0419× | 0.0415–0.0423× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.03` | Native C engine | 0.8652× | 0.8430–0.8921× | 0.18× | — |
| holdout | `hold.large.window-search.03` | Rust engine | 0.2285× | 0.2234–0.2326× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.04` | Python engine | 0.0380× | 0.0376–0.0385× | 3.92× | SLOWDOWN |
| holdout | `hold.large.window-search.04` | Native C engine | 0.8736× | 0.8531–0.8951× | 0.18× | — |
| holdout | `hold.large.window-search.04` | Rust engine | 0.2145× | 0.2119–0.2162× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.05` | Python engine | 0.0386× | 0.0382–0.0390× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.05` | Native C engine | 0.8740× | 0.8565–0.8942× | 0.18× | — |
| holdout | `hold.large.window-search.05` | Rust engine | 0.2089× | 0.2044–0.2126× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.06` | Python engine | 0.0404× | 0.0397–0.0412× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.06` | Native C engine | 0.8974× | 0.8750–0.9181× | 0.18× | — |
| holdout | `hold.large.window-search.06` | Rust engine | 0.2230× | 0.2198–0.2268× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.07` | Python engine | 0.0423× | 0.0418–0.0428× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.07` | Native C engine | 0.8873× | 0.8647–0.9117× | 0.18× | — |
| holdout | `hold.large.window-search.07` | Rust engine | 0.2249× | 0.2233–0.2265× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.08` | Python engine | 0.0380× | 0.0377–0.0384× | 3.92× | SLOWDOWN |
| holdout | `hold.large.window-search.08` | Native C engine | 0.8774× | 0.8593–0.8997× | 0.18× | — |
| holdout | `hold.large.window-search.08` | Rust engine | 0.2083× | 0.2058–0.2106× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.09` | Python engine | 0.0388× | 0.0384–0.0391× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.09` | Native C engine | 0.8592× | 0.8500–0.8715× | 0.18× | — |
| holdout | `hold.large.window-search.09` | Rust engine | 0.2180× | 0.2166–0.2192× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.10` | Python engine | 0.0398× | 0.0395–0.0402× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.10` | Native C engine | 0.8550× | 0.8443–0.8670× | 0.18× | — |
| holdout | `hold.large.window-search.10` | Rust engine | 0.2211× | 0.2190–0.2230× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.11` | Python engine | 0.0423× | 0.0415–0.0429× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.11` | Native C engine | 0.9098× | 0.8850–0.9373× | 0.18× | — |
| holdout | `hold.large.window-search.11` | Rust engine | 0.2225× | 0.2119–0.2301× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.12` | Python engine | 0.0380× | 0.0376–0.0383× | 3.92× | SLOWDOWN |
| holdout | `hold.large.window-search.12` | Native C engine | 0.8874× | 0.8716–0.9057× | 0.18× | — |
| holdout | `hold.large.window-search.12` | Rust engine | 0.2048× | 0.1963–0.2101× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.13` | Python engine | 0.0401× | 0.0387–0.0426× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.13` | Native C engine | 0.8927× | 0.8535–0.9530× | 0.18× | — |
| holdout | `hold.large.window-search.13` | Rust engine | 0.2243× | 0.2165–0.2383× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.14` | Python engine | 0.0422× | 0.0382–0.0487× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.14` | Native C engine | 0.9636× | 0.8636–1.1173× | 0.18× | — |
| holdout | `hold.large.window-search.14` | Rust engine | 0.2349× | 0.2129–0.2706× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.15` | Python engine | 0.0413× | 0.0404–0.0420× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.15` | Native C engine | 0.9111× | 0.8808–0.9413× | 0.18× | — |
| holdout | `hold.large.window-search.15` | Rust engine | 0.2217× | 0.2198–0.2235× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.16` | Python engine | 0.0375× | 0.0349–0.0405× | 3.92× | SLOWDOWN |
| holdout | `hold.large.window-search.16` | Native C engine | 0.8519× | 0.7778–0.9242× | 0.18× | — |
| holdout | `hold.large.window-search.16` | Rust engine | 0.2123× | 0.2040–0.2250× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.17` | Python engine | 0.0405× | 0.0385–0.0446× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.17` | Native C engine | 0.8070× | 0.6148–0.9873× | 0.18× | — |
| holdout | `hold.large.window-search.17` | Rust engine | 0.2144× | 0.1902–0.2431× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.18` | Python engine | 0.0399× | 0.0394–0.0404× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.18` | Native C engine | 0.8923× | 0.8674–0.9189× | 0.18× | — |
| holdout | `hold.large.window-search.18` | Rust engine | 0.2221× | 0.2202–0.2238× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.19` | Python engine | 0.0519× | 0.0404–0.0831× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.19` | Native C engine | 1.1105× | 0.8607–1.7978× | 0.18× | — |
| holdout | `hold.large.window-search.19` | Rust engine | 0.2789× | 0.2196–0.4431× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.20` | Python engine | 0.0378× | 0.0352–0.0409× | 3.92× | SLOWDOWN |
| holdout | `hold.large.window-search.20` | Native C engine | 0.9083× | 0.8694–0.9695× | 0.18× | — |
| holdout | `hold.large.window-search.20` | Rust engine | 0.2225× | 0.2062–0.2426× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.21` | Python engine | 0.0432× | 0.0382–0.0493× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.21` | Native C engine | 0.9409× | 0.8514–1.0744× | 0.18× | — |
| holdout | `hold.large.window-search.21` | Rust engine | 0.2377× | 0.2013–0.2741× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.22` | Python engine | 0.0395× | 0.0389–0.0400× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.22` | Native C engine | 0.8929× | 0.8720–0.9139× | 0.18× | — |
| holdout | `hold.large.window-search.22` | Rust engine | 0.2118× | 0.1984–0.2227× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.23` | Python engine | 0.0423× | 0.0417–0.0430× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.23` | Native C engine | 0.8864× | 0.8560–0.9192× | 0.18× | — |
| holdout | `hold.large.window-search.23` | Rust engine | 0.2320× | 0.2289–0.2352× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.24` | Python engine | 0.0379× | 0.0374–0.0382× | 3.92× | SLOWDOWN |
| holdout | `hold.large.window-search.24` | Native C engine | 0.8439× | 0.7959–0.8772× | 0.18× | — |
| holdout | `hold.large.window-search.24` | Rust engine | 0.2128× | 0.2085–0.2162× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.25` | Python engine | 0.0399× | 0.0387–0.0419× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.25` | Native C engine | 0.8846× | 0.8567–0.9292× | 0.18× | — |
| holdout | `hold.large.window-search.25` | Rust engine | 0.2187× | 0.2059–0.2326× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.26` | Python engine | 0.0416× | 0.0380–0.0495× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.26` | Native C engine | 0.9538× | 0.8635–1.1327× | 0.18× | — |
| holdout | `hold.large.window-search.26` | Rust engine | 0.2279× | 0.1996–0.2779× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.27` | Python engine | 0.0421× | 0.0396–0.0467× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.27` | Native C engine | 0.9244× | 0.8460–1.0381× | 0.18× | — |
| holdout | `hold.large.window-search.27` | Rust engine | 0.2363× | 0.2230–0.2625× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.28` | Python engine | 0.0358× | 0.0349–0.0364× | 3.92× | SLOWDOWN |
| holdout | `hold.large.window-search.28` | Native C engine | 0.8426× | 0.8066–0.8746× | 0.18× | — |
| holdout | `hold.large.window-search.28` | Rust engine | 0.2088× | 0.2061–0.2107× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.29` | Python engine | 0.0373× | 0.0368–0.0378× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.29` | Native C engine | 0.8737× | 0.8522–0.8979× | 0.18× | — |
| holdout | `hold.large.window-search.29` | Rust engine | 0.2145× | 0.2123–0.2167× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.30` | Python engine | 0.0380× | 0.0375–0.0384× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.30` | Native C engine | 0.8829× | 0.8659–0.9032× | 0.18× | — |
| holdout | `hold.large.window-search.30` | Rust engine | 0.2174× | 0.2150–0.2203× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-search.31` | Python engine | 0.0378× | 0.0358–0.0397× | 3.97× | SLOWDOWN |
| holdout | `hold.large.window-search.31` | Native C engine | 0.8838× | 0.8585–0.9113× | 0.18× | — |
| holdout | `hold.large.window-search.31` | Rust engine | 0.2164× | 0.2023–0.2273× | 0.17× | SLOWDOWN |
| holdout | `hold.large.window-collection.00` | Python engine | 0.0338× | 0.0324–0.0358× | 3.44× | SLOWDOWN |
| holdout | `hold.large.window-collection.00` | Native C engine | 1.5676× | 1.4819–1.6713× | 0.36× | FASTER |
| holdout | `hold.large.window-collection.00` | Rust engine | 0.2119× | 0.2030–0.2241× | 0.37× | SLOWDOWN |
| holdout | `hold.large.window-collection.01` | Python engine | 0.0228× | 0.0210–0.0250× | 5.54× | SLOWDOWN |
| holdout | `hold.large.window-collection.01` | Native C engine | 2.1622× | 1.9921–2.3698× | 0.34× | FASTER |
| holdout | `hold.large.window-collection.01` | Rust engine | 0.3455× | 0.3167–0.3792× | 1.30× | SLOWDOWN |
| holdout | `hold.large.window-collection.02` | Python engine | 0.0302× | 0.0290–0.0322× | 3.73× | SLOWDOWN |
| holdout | `hold.large.window-collection.02` | Native C engine | 1.5788× | 1.4578–1.6910× | 0.52× | FASTER |
| holdout | `hold.large.window-collection.02` | Rust engine | 0.1690× | 0.1596–0.1773× | 0.50× | SLOWDOWN |
| holdout | `hold.large.window-collection.03` | Python engine | 0.0211× | 0.0202–0.0223× | 7.10× | SLOWDOWN |
| holdout | `hold.large.window-collection.03` | Native C engine | 2.3618× | 2.3087–2.4172× | 0.63× | FASTER |
| holdout | `hold.large.window-collection.03` | Rust engine | 0.3510× | 0.3479–0.3545× | 3.00× | SLOWDOWN |
| holdout | `hold.large.window-collection.04` | Python engine | 0.0357× | 0.0339–0.0372× | 3.44× | SLOWDOWN |
| holdout | `hold.large.window-collection.04` | Native C engine | 1.5587× | 1.4434–1.6476× | 0.36× | FASTER |
| holdout | `hold.large.window-collection.04` | Rust engine | 0.2032× | 0.1935–0.2122× | 0.37× | SLOWDOWN |
| holdout | `hold.large.window-collection.05` | Python engine | 0.0225× | 0.0218–0.0235× | 5.53× | SLOWDOWN |
| holdout | `hold.large.window-collection.05` | Native C engine | 1.9929× | 1.9411–2.0824× | 0.34× | FASTER |
| holdout | `hold.large.window-collection.05` | Rust engine | 0.3117× | 0.3005–0.3258× | 1.41× | SLOWDOWN |
| holdout | `hold.large.window-collection.06` | Python engine | 0.0300× | 0.0297–0.0302× | 3.73× | SLOWDOWN |
| holdout | `hold.large.window-collection.06` | Native C engine | 1.6601× | 1.5489–1.7407× | 0.52× | FASTER |
| holdout | `hold.large.window-collection.06` | Rust engine | 0.1758× | 0.1726–0.1784× | 0.50× | SLOWDOWN |
| holdout | `hold.large.window-collection.07` | Python engine | 0.0222× | 0.0219–0.0226× | 7.10× | SLOWDOWN |
| holdout | `hold.large.window-collection.07` | Native C engine | 2.4281× | 2.3912–2.4595× | 0.63× | FASTER |
| holdout | `hold.large.window-collection.07` | Rust engine | 0.3508× | 0.3472–0.3548× | 3.00× | SLOWDOWN |
| holdout | `hold.large.window-collection.08` | Python engine | 0.0348× | 0.0343–0.0353× | 3.44× | SLOWDOWN |
| holdout | `hold.large.window-collection.08` | Native C engine | 1.5412× | 1.5244–1.5573× | 0.36× | FASTER |
| holdout | `hold.large.window-collection.08` | Rust engine | 0.2019× | 0.1995–0.2044× | 0.37× | SLOWDOWN |
| holdout | `hold.large.window-collection.09` | Python engine | 0.0223× | 0.0221–0.0225× | 5.53× | SLOWDOWN |
| holdout | `hold.large.window-collection.09` | Native C engine | 1.9316× | 1.7949–2.0194× | 0.34× | FASTER |
| holdout | `hold.large.window-collection.09` | Rust engine | 0.3142× | 0.3107–0.3177× | 1.41× | SLOWDOWN |
| holdout | `hold.large.window-collection.10` | Python engine | 0.0294× | 0.0291–0.0298× | 3.73× | SLOWDOWN |
| holdout | `hold.large.window-collection.10` | Native C engine | 1.7036× | 1.6824–1.7288× | 0.52× | FASTER |
| holdout | `hold.large.window-collection.10` | Rust engine | 0.1739× | 0.1724–0.1754× | 0.50× | SLOWDOWN |
| holdout | `hold.large.window-collection.11` | Python engine | 0.0218× | 0.0217–0.0220× | 7.10× | SLOWDOWN |
| holdout | `hold.large.window-collection.11` | Native C engine | 2.2470× | 2.0056–2.3922× | 0.63× | FASTER |
| holdout | `hold.large.window-collection.11` | Rust engine | 0.3457× | 0.3434–0.3479× | 3.00× | SLOWDOWN |
| holdout | `hold.large.window-collection.12` | Python engine | 0.0350× | 0.0346–0.0355× | 3.44× | SLOWDOWN |
| holdout | `hold.large.window-collection.12` | Native C engine | 1.5346× | 1.5095–1.5625× | 0.36× | FASTER |
| holdout | `hold.large.window-collection.12` | Rust engine | 0.2006× | 0.1981–0.2034× | 0.37× | SLOWDOWN |
| holdout | `hold.large.window-collection.13` | Python engine | 0.0220× | 0.0219–0.0221× | 5.53× | SLOWDOWN |
| holdout | `hold.large.window-collection.13` | Native C engine | 1.9705× | 1.9539–1.9881× | 0.34× | FASTER |
| holdout | `hold.large.window-collection.13` | Rust engine | 0.3087× | 0.3069–0.3106× | 1.41× | SLOWDOWN |
| holdout | `hold.large.window-collection.14` | Python engine | 0.0295× | 0.0293–0.0297× | 3.73× | SLOWDOWN |
| holdout | `hold.large.window-collection.14` | Native C engine | 1.7080× | 1.6868–1.7337× | 0.52× | FASTER |
| holdout | `hold.large.window-collection.14` | Rust engine | 0.1690× | 0.1673–0.1709× | 0.50× | SLOWDOWN |
| holdout | `hold.large.window-collection.15` | Python engine | 0.0221× | 0.0218–0.0224× | 7.10× | SLOWDOWN |
| holdout | `hold.large.window-collection.15` | Native C engine | 2.3949× | 2.3538–2.4369× | 0.63× | FASTER |
| holdout | `hold.large.window-collection.15` | Rust engine | 0.3488× | 0.3442–0.3538× | 3.00× | SLOWDOWN |
| holdout | `hold.large.window-collection.16` | Python engine | 0.0355× | 0.0348–0.0366× | 3.44× | SLOWDOWN |
| holdout | `hold.large.window-collection.16` | Native C engine | 1.5629× | 1.5285–1.6073× | 0.36× | FASTER |
| holdout | `hold.large.window-collection.16` | Rust engine | 0.2031× | 0.1985–0.2092× | 0.37× | SLOWDOWN |
| holdout | `hold.large.window-collection.17` | Python engine | 0.0219× | 0.0217–0.0222× | 5.52× | SLOWDOWN |
| holdout | `hold.large.window-collection.17` | Native C engine | 1.9908× | 1.9722–2.0100× | 0.35× | FASTER |
| holdout | `hold.large.window-collection.17` | Rust engine | 0.2841× | 0.2817–0.2870× | 1.53× | SLOWDOWN |
| holdout | `hold.large.window-collection.18` | Python engine | 0.0296× | 0.0292–0.0300× | 3.73× | SLOWDOWN |
| holdout | `hold.large.window-collection.18` | Native C engine | 1.6964× | 1.6743–1.7197× | 0.52× | FASTER |
| holdout | `hold.large.window-collection.18` | Rust engine | 0.1690× | 0.1662–0.1718× | 0.50× | SLOWDOWN |
| holdout | `hold.large.window-collection.19` | Python engine | 0.0219× | 0.0214–0.0222× | 7.06× | SLOWDOWN |
| holdout | `hold.large.window-collection.19` | Native C engine | 2.3572× | 2.3141–2.3972× | 0.63× | FASTER |
| holdout | `hold.large.window-collection.19` | Rust engine | 0.3115× | 0.2985–0.3208× | 3.25× | SLOWDOWN |
| holdout | `hold.large.window-collection.20` | Python engine | 0.0353× | 0.0346–0.0364× | 3.44× | SLOWDOWN |
| holdout | `hold.large.window-collection.20` | Native C engine | 1.5441× | 1.5084–1.5874× | 0.36× | FASTER |
| holdout | `hold.large.window-collection.20` | Rust engine | 0.2048× | 0.2004–0.2113× | 0.37× | SLOWDOWN |
| holdout | `hold.large.window-collection.21` | Python engine | 0.0222× | 0.0220–0.0225× | 5.53× | SLOWDOWN |
| holdout | `hold.large.window-collection.21` | Native C engine | 1.9720× | 1.9427–2.0066× | 0.34× | FASTER |
| holdout | `hold.large.window-collection.21` | Rust engine | 0.3077× | 0.3049–0.3117× | 1.41× | SLOWDOWN |
| holdout | `hold.large.window-collection.22` | Python engine | 0.0294× | 0.0283–0.0302× | 3.73× | SLOWDOWN |
| holdout | `hold.large.window-collection.22` | Native C engine | 1.6352× | 1.5293–1.7308× | 0.52× | FASTER |
| holdout | `hold.large.window-collection.22` | Rust engine | 0.1746× | 0.1720–0.1781× | 0.50× | SLOWDOWN |
| holdout | `hold.large.window-collection.23` | Python engine | 0.0220× | 0.0218–0.0222× | 7.10× | SLOWDOWN |
| holdout | `hold.large.window-collection.23` | Native C engine | 2.3528× | 2.2986–2.4027× | 0.63× | FASTER |
| holdout | `hold.large.window-collection.23` | Rust engine | 0.3478× | 0.3449–0.3511× | 3.00× | SLOWDOWN |
| holdout | `hold.large.window-collection.24` | Python engine | 0.0354× | 0.0348–0.0360× | 3.44× | SLOWDOWN |
| holdout | `hold.large.window-collection.24` | Native C engine | 1.5285× | 1.4954–1.5668× | 0.36× | FASTER |
| holdout | `hold.large.window-collection.24` | Rust engine | 0.2055× | 0.2030–0.2088× | 0.37× | SLOWDOWN |
| holdout | `hold.large.window-collection.25` | Python engine | 0.0225× | 0.0220–0.0233× | 5.52× | SLOWDOWN |
| holdout | `hold.large.window-collection.25` | Native C engine | 1.9663× | 1.8099–2.0797× | 0.35× | FASTER |
| holdout | `hold.large.window-collection.25` | Rust engine | 0.2902× | 0.2837–0.2999× | 1.53× | SLOWDOWN |
| holdout | `hold.large.window-collection.26` | Python engine | 0.0302× | 0.0292–0.0317× | 3.73× | SLOWDOWN |
| holdout | `hold.large.window-collection.26` | Native C engine | 1.6783× | 1.5291–1.8185× | 0.52× | FASTER |
| holdout | `hold.large.window-collection.26` | Rust engine | 0.1682× | 0.1509–0.1830× | 0.50× | SLOWDOWN |
| holdout | `hold.large.window-collection.27` | Python engine | 0.0219× | 0.0216–0.0221× | 7.06× | SLOWDOWN |
| holdout | `hold.large.window-collection.27` | Native C engine | 2.3597× | 2.3204–2.3923× | 0.63× | FASTER |
| holdout | `hold.large.window-collection.27` | Rust engine | 0.3387× | 0.3354–0.3423× | 3.25× | SLOWDOWN |
| holdout | `hold.large.window-collection.28` | Python engine | 0.0347× | 0.0344–0.0351× | 3.44× | SLOWDOWN |
| holdout | `hold.large.window-collection.28` | Native C engine | 1.5307× | 1.5014–1.5579× | 0.36× | FASTER |
| holdout | `hold.large.window-collection.28` | Rust engine | 0.2007× | 0.1985–0.2033× | 0.37× | SLOWDOWN |
| holdout | `hold.large.window-collection.29` | Python engine | 0.0221× | 0.0218–0.0225× | 5.51× | SLOWDOWN |
| holdout | `hold.large.window-collection.29` | Native C engine | 1.9624× | 1.9234–1.9994× | 0.35× | FASTER |
| holdout | `hold.large.window-collection.29` | Rust engine | 0.2752× | 0.2664–0.2831× | 1.64× | SLOWDOWN |
| holdout | `hold.large.window-collection.30` | Python engine | 0.0292× | 0.0287–0.0297× | 3.73× | SLOWDOWN |
| holdout | `hold.large.window-collection.30` | Native C engine | 1.6786× | 1.5910–1.7346× | 0.52× | FASTER |
| holdout | `hold.large.window-collection.30` | Rust engine | 0.1701× | 0.1632–0.1747× | 0.50× | SLOWDOWN |
| holdout | `hold.large.window-collection.31` | Python engine | 0.0217× | 0.0216–0.0218× | 7.06× | SLOWDOWN |
| holdout | `hold.large.window-collection.31` | Native C engine | 2.3849× | 2.3539–2.4161× | 0.63× | FASTER |
| holdout | `hold.large.window-collection.31` | Rust engine | 0.3345× | 0.3324–0.3369× | 3.25× | SLOWDOWN |
| holdout | `hold.large.request-records.00` | Python engine | 0.0212× | 0.0206–0.0217× | 7.69× | SLOWDOWN |
| holdout | `hold.large.request-records.00` | Native C engine | 1.1150× | 1.0831–1.1463× | 0.35× | FASTER |
| holdout | `hold.large.request-records.00` | Rust engine | 0.1685× | 0.1631–0.1740× | 0.32× | SLOWDOWN |
| holdout | `hold.large.request-records.01` | Python engine | 0.0183× | 0.0178–0.0189× | 8.00× | SLOWDOWN |
| holdout | `hold.large.request-records.01` | Native C engine | 1.0342× | 1.0136–1.0574× | 0.41× | FASTER |
| holdout | `hold.large.request-records.01` | Rust engine | 0.1510× | 0.1474–0.1552× | 0.34× | SLOWDOWN |
| holdout | `hold.large.request-records.02` | Python engine | 0.0160× | 0.0158–0.0162× | 8.43× | SLOWDOWN |
| holdout | `hold.large.request-records.02` | Native C engine | 0.9737× | 0.9464–0.9954× | 0.49× | — |
| holdout | `hold.large.request-records.02` | Rust engine | 0.1367× | 0.1346–0.1389× | 0.38× | SLOWDOWN |
| holdout | `hold.large.request-records.03` | Python engine | 0.0162× | 0.0153–0.0178× | 6.06× | SLOWDOWN |
| holdout | `hold.large.request-records.03` | Native C engine | 0.9987× | 0.9308–1.1142× | 0.59× | — |
| holdout | `hold.large.request-records.03` | Rust engine | 0.1406× | 0.1327–0.1550× | 0.44× | SLOWDOWN |
| holdout | `hold.large.request-records.04` | Python engine | 0.0203× | 0.0199–0.0208× | 7.69× | SLOWDOWN |
| holdout | `hold.large.request-records.04` | Native C engine | 1.0632× | 1.0384–1.0937× | 0.35× | FASTER |
| holdout | `hold.large.request-records.04` | Rust engine | 0.1616× | 0.1588–0.1653× | 0.32× | SLOWDOWN |
| holdout | `hold.large.request-records.05` | Python engine | 0.0188× | 0.0179–0.0202× | 8.00× | SLOWDOWN |
| holdout | `hold.large.request-records.05` | Native C engine | 1.0735× | 1.0275–1.1449× | 0.41× | FASTER |
| holdout | `hold.large.request-records.05` | Rust engine | 0.1551× | 0.1481–0.1669× | 0.34× | SLOWDOWN |
| holdout | `hold.large.request-records.06` | Python engine | 0.0160× | 0.0158–0.0161× | 8.43× | SLOWDOWN |
| holdout | `hold.large.request-records.06` | Native C engine | 0.9548× | 0.9446–0.9660× | 0.49× | — |
| holdout | `hold.large.request-records.06` | Rust engine | 0.1311× | 0.1284–0.1335× | 0.38× | SLOWDOWN |
| holdout | `hold.large.request-records.07` | Python engine | 0.0163× | 0.0153–0.0177× | 5.84× | SLOWDOWN |
| holdout | `hold.large.request-records.07` | Native C engine | 0.9966× | 0.9469–1.0773× | 0.59× | — |
| holdout | `hold.large.request-records.07` | Rust engine | 0.1414× | 0.1329–0.1542× | 0.44× | SLOWDOWN |
| holdout | `hold.large.request-records.08` | Python engine | 0.0208× | 0.0204–0.0216× | 7.69× | SLOWDOWN |
| holdout | `hold.large.request-records.08` | Native C engine | 1.0804× | 1.0547–1.1189× | 0.35× | FASTER |
| holdout | `hold.large.request-records.08` | Rust engine | 0.1648× | 0.1606–0.1706× | 0.32× | SLOWDOWN |
| holdout | `hold.large.request-records.09` | Python engine | 0.0179× | 0.0176–0.0181× | 8.00× | SLOWDOWN |
| holdout | `hold.large.request-records.09` | Native C engine | 1.0218× | 1.0043–1.0411× | 0.41× | FASTER |
| holdout | `hold.large.request-records.09` | Rust engine | 0.1457× | 0.1432–0.1488× | 0.34× | SLOWDOWN |
| holdout | `hold.large.request-records.10` | Python engine | 0.0163× | 0.0157–0.0173× | 8.43× | SLOWDOWN |
| holdout | `hold.large.request-records.10` | Native C engine | 0.9897× | 0.9524–1.0523× | 0.49× | — |
| holdout | `hold.large.request-records.10` | Rust engine | 0.1383× | 0.1326–0.1475× | 0.38× | SLOWDOWN |
| holdout | `hold.large.request-records.11` | Python engine | 0.0155× | 0.0152–0.0157× | 5.84× | SLOWDOWN |
| holdout | `hold.large.request-records.11` | Native C engine | 0.9482× | 0.9297–0.9650× | 0.59× | — |
| holdout | `hold.large.request-records.11` | Rust engine | 0.1321× | 0.1289–0.1348× | 0.44× | SLOWDOWN |
| holdout | `hold.large.request-records.12` | Python engine | 0.0205× | 0.0201–0.0210× | 7.69× | SLOWDOWN |
| holdout | `hold.large.request-records.12` | Native C engine | 1.0870× | 1.0692–1.1097× | 0.35× | FASTER |
| holdout | `hold.large.request-records.12` | Rust engine | 0.1637× | 0.1609–0.1671× | 0.32× | SLOWDOWN |
| holdout | `hold.large.request-records.13` | Python engine | 0.0179× | 0.0176–0.0181× | 8.00× | SLOWDOWN |
| holdout | `hold.large.request-records.13` | Native C engine | 0.9827× | 0.8924–1.0411× | 0.41× | — |
| holdout | `hold.large.request-records.13` | Rust engine | 0.1475× | 0.1458–0.1494× | 0.34× | SLOWDOWN |
| holdout | `hold.large.request-records.14` | Python engine | 0.0158× | 0.0156–0.0160× | 8.43× | SLOWDOWN |
| holdout | `hold.large.request-records.14` | Native C engine | 0.9369× | 0.8915–0.9674× | 0.49× | — |
| holdout | `hold.large.request-records.14` | Rust engine | 0.1329× | 0.1311–0.1347× | 0.38× | SLOWDOWN |
| holdout | `hold.large.request-records.15` | Python engine | 0.0159× | 0.0152–0.0170× | 6.04× | SLOWDOWN |
| holdout | `hold.large.request-records.15` | Native C engine | 0.8771× | 0.7837–0.9595× | 0.59× | — |
| holdout | `hold.large.request-records.15` | Rust engine | 0.1343× | 0.1287–0.1437× | 0.44× | SLOWDOWN |
| holdout | `hold.large.request-records.16` | Python engine | 0.0208× | 0.0202–0.0218× | 7.69× | SLOWDOWN |
| holdout | `hold.large.request-records.16` | Native C engine | 1.0442× | 0.9284–1.1313× | 0.35× | — |
| holdout | `hold.large.request-records.16` | Rust engine | 0.1635× | 0.1579–0.1719× | 0.32× | SLOWDOWN |
| holdout | `hold.large.request-records.17` | Python engine | 0.0180× | 0.0178–0.0183× | 8.00× | SLOWDOWN |
| holdout | `hold.large.request-records.17` | Native C engine | 1.0194× | 1.0034–1.0395× | 0.41× | FASTER |
| holdout | `hold.large.request-records.17` | Rust engine | 0.1475× | 0.1455–0.1497× | 0.34× | SLOWDOWN |
| holdout | `hold.large.request-records.18` | Python engine | 0.0158× | 0.0153–0.0161× | 8.43× | SLOWDOWN |
| holdout | `hold.large.request-records.18` | Native C engine | 0.9740× | 0.9607–0.9876× | 0.49× | — |
| holdout | `hold.large.request-records.18` | Rust engine | 0.1345× | 0.1328–0.1362× | 0.38× | SLOWDOWN |
| holdout | `hold.large.request-records.19` | Python engine | 0.0156× | 0.0152–0.0160× | 5.84× | SLOWDOWN |
| holdout | `hold.large.request-records.19` | Native C engine | 0.9626× | 0.9424–0.9832× | 0.59× | — |
| holdout | `hold.large.request-records.19` | Rust engine | 0.1357× | 0.1329–0.1384× | 0.44× | SLOWDOWN |
| holdout | `hold.large.request-records.20` | Python engine | 0.0200× | 0.0195–0.0205× | 7.69× | SLOWDOWN |
| holdout | `hold.large.request-records.20` | Native C engine | 1.0695× | 1.0536–1.0853× | 0.35× | FASTER |
| holdout | `hold.large.request-records.20` | Rust engine | 0.1580× | 0.1523–0.1627× | 0.32× | SLOWDOWN |
| holdout | `hold.large.request-records.21` | Python engine | 0.0180× | 0.0177–0.0183× | 8.00× | SLOWDOWN |
| holdout | `hold.large.request-records.21` | Native C engine | 1.0280× | 1.0121–1.0476× | 0.41× | FASTER |
| holdout | `hold.large.request-records.21` | Rust engine | 0.1453× | 0.1432–0.1479× | 0.34× | SLOWDOWN |
| holdout | `hold.large.request-records.22` | Python engine | 0.0163× | 0.0157–0.0172× | 8.43× | SLOWDOWN |
| holdout | `hold.large.request-records.22` | Native C engine | 0.9681× | 0.9400–0.9929× | 0.49× | — |
| holdout | `hold.large.request-records.22` | Rust engine | 0.1388× | 0.1341–0.1473× | 0.38× | SLOWDOWN |
| holdout | `hold.large.request-records.23` | Python engine | 0.0153× | 0.0149–0.0156× | 5.84× | SLOWDOWN |
| holdout | `hold.large.request-records.23` | Native C engine | 0.9498× | 0.9303–0.9704× | 0.59× | — |
| holdout | `hold.large.request-records.23` | Rust engine | 0.1288× | 0.1220–0.1341× | 0.44× | SLOWDOWN |
| holdout | `hold.large.request-records.24` | Python engine | 0.0207× | 0.0200–0.0218× | 7.69× | SLOWDOWN |
| holdout | `hold.large.request-records.24` | Native C engine | 1.1043× | 1.0744–1.1530× | 0.35× | FASTER |
| holdout | `hold.large.request-records.24` | Rust engine | 0.1656× | 0.1617–0.1717× | 0.32× | SLOWDOWN |
| holdout | `hold.large.request-records.25` | Python engine | 0.0186× | 0.0179–0.0198× | 8.00× | SLOWDOWN |
| holdout | `hold.large.request-records.25` | Native C engine | 1.0570× | 1.0102–1.1293× | 0.41× | FASTER |
| holdout | `hold.large.request-records.25` | Rust engine | 0.1476× | 0.1394–0.1587× | 0.34× | SLOWDOWN |
| holdout | `hold.large.request-records.26` | Python engine | 0.0157× | 0.0155–0.0159× | 8.43× | SLOWDOWN |
| holdout | `hold.large.request-records.26` | Native C engine | 0.9494× | 0.9329–0.9651× | 0.49× | — |
| holdout | `hold.large.request-records.26` | Rust engine | 0.1320× | 0.1303–0.1337× | 0.38× | SLOWDOWN |
| holdout | `hold.large.request-records.27` | Python engine | 0.0152× | 0.0148–0.0155× | 5.84× | SLOWDOWN |
| holdout | `hold.large.request-records.27` | Native C engine | 0.9126× | 0.8807–0.9453× | 0.59× | — |
| holdout | `hold.large.request-records.27` | Rust engine | 0.1260× | 0.1222–0.1300× | 0.44× | SLOWDOWN |
| holdout | `hold.large.request-records.28` | Python engine | 0.0202× | 0.0194–0.0209× | 7.69× | SLOWDOWN |
| holdout | `hold.large.request-records.28` | Native C engine | 1.0292× | 0.9285–1.0937× | 0.35× | — |
| holdout | `hold.large.request-records.28` | Rust engine | 0.1610× | 0.1584–0.1639× | 0.32× | SLOWDOWN |
| holdout | `hold.large.request-records.29` | Python engine | 0.0171× | 0.0166–0.0176× | 8.00× | SLOWDOWN |
| holdout | `hold.large.request-records.29` | Native C engine | 0.9997× | 0.9367–1.0423× | 0.41× | — |
| holdout | `hold.large.request-records.29` | Rust engine | 0.1390× | 0.1350–0.1426× | 0.34× | SLOWDOWN |
| holdout | `hold.large.request-records.30` | Python engine | 0.0154× | 0.0148–0.0160× | 8.43× | SLOWDOWN |
| holdout | `hold.large.request-records.30` | Native C engine | 0.9330× | 0.8779–0.9885× | 0.49× | — |
| holdout | `hold.large.request-records.30` | Rust engine | 0.1280× | 0.1208–0.1351× | 0.38× | SLOWDOWN |
| holdout | `hold.large.request-records.31` | Python engine | 0.0146× | 0.0131–0.0164× | 6.04× | SLOWDOWN |
| holdout | `hold.large.request-records.31` | Native C engine | 0.9085× | 0.7816–1.0422× | 0.59× | — |
| holdout | `hold.large.request-records.31` | Rust engine | 0.1342× | 0.1255–0.1494× | 0.44× | SLOWDOWN |
| holdout | `hold.large.everyday-address.00` | Python engine | 0.0145× | 0.0137–0.0155× | 17.65× | SLOWDOWN |
| holdout | `hold.large.everyday-address.00` | Native C engine | 1.3979× | 1.3448–1.4809× | 0.11× | FASTER |
| holdout | `hold.large.everyday-address.00` | Rust engine | 0.0504× | 0.0480–0.0538× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.01` | Python engine | 0.0156× | 0.0152–0.0159× | 6.09× | SLOWDOWN |
| holdout | `hold.large.everyday-address.01` | Native C engine | 0.7717× | 0.7620–0.7825× | 0.22× | SLOWDOWN |
| holdout | `hold.large.everyday-address.01` | Rust engine | 0.1139× | 0.1108–0.1169× | 4.36× | SLOWDOWN |
| holdout | `hold.large.everyday-address.02` | Python engine | 0.0113× | 0.0106–0.0118× | 23.69× | SLOWDOWN |
| holdout | `hold.large.everyday-address.02` | Native C engine | 1.1503× | 1.1265–1.1772× | 0.09× | FASTER |
| holdout | `hold.large.everyday-address.02` | Rust engine | 0.2213× | 0.2171–0.2264× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.03` | Python engine | 0.0191× | 0.0177–0.0212× | 17.65× | SLOWDOWN |
| holdout | `hold.large.everyday-address.03` | Native C engine | 1.3048× | 1.1357–1.5133× | 0.11× | FASTER |
| holdout | `hold.large.everyday-address.03` | Rust engine | 0.0661× | 0.0615–0.0729× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.04` | Python engine | 0.0161× | 0.0156–0.0165× | 6.20× | SLOWDOWN |
| holdout | `hold.large.everyday-address.04` | Native C engine | 0.7314× | 0.6575–0.7747× | 0.14× | SLOWDOWN |
| holdout | `hold.large.everyday-address.04` | Rust engine | 0.1127× | 0.1113–0.1136× | 2.44× | SLOWDOWN |
| holdout | `hold.large.everyday-address.05` | Python engine | 0.0113× | 0.0111–0.0114× | 23.69× | SLOWDOWN |
| holdout | `hold.large.everyday-address.05` | Native C engine | 1.1734× | 1.1548–1.1899× | 0.09× | FASTER |
| holdout | `hold.large.everyday-address.05` | Rust engine | 0.2092× | 0.1992–0.2152× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.06` | Python engine | 0.0167× | 0.0164–0.0171× | 17.65× | SLOWDOWN |
| holdout | `hold.large.everyday-address.06` | Native C engine | 1.3686× | 1.3361–1.4001× | 0.11× | FASTER |
| holdout | `hold.large.everyday-address.06` | Rust engine | 0.0545× | 0.0530–0.0557× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.07` | Python engine | 0.0156× | 0.0155–0.0158× | 5.49× | SLOWDOWN |
| holdout | `hold.large.everyday-address.07` | Native C engine | 0.7544× | 0.7481–0.7615× | 0.54× | SLOWDOWN |
| holdout | `hold.large.everyday-address.07` | Rust engine | 0.1124× | 0.1080–0.1163× | 10.75× | SLOWDOWN |
| holdout | `hold.large.everyday-address.08` | Python engine | 0.0108× | 0.0107–0.0108× | 23.69× | SLOWDOWN |
| holdout | `hold.large.everyday-address.08` | Native C engine | 1.1657× | 1.1578–1.1735× | 0.09× | FASTER |
| holdout | `hold.large.everyday-address.08` | Rust engine | 0.2021× | 0.1944–0.2080× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.09` | Python engine | 0.0168× | 0.0155–0.0189× | 17.65× | SLOWDOWN |
| holdout | `hold.large.everyday-address.09` | Native C engine | 1.3977× | 1.3455–1.4776× | 0.11× | FASTER |
| holdout | `hold.large.everyday-address.09` | Rust engine | 0.0529× | 0.0478–0.0577× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.10` | Python engine | 0.0158× | 0.0152–0.0161× | 5.84× | SLOWDOWN |
| holdout | `hold.large.everyday-address.10` | Native C engine | 0.7338× | 0.6971–0.7550× | 0.36× | SLOWDOWN |
| holdout | `hold.large.everyday-address.10` | Rust engine | 0.1166× | 0.1138–0.1186× | 7.10× | SLOWDOWN |
| holdout | `hold.large.everyday-address.11` | Python engine | 0.0127× | 0.0124–0.0129× | 23.69× | SLOWDOWN |
| holdout | `hold.large.everyday-address.11` | Native C engine | 1.0569× | 0.9876–1.1081× | 0.09× | — |
| holdout | `hold.large.everyday-address.11` | Rust engine | 0.2292× | 0.2248–0.2331× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.12` | Python engine | 0.0159× | 0.0147–0.0176× | 17.65× | SLOWDOWN |
| holdout | `hold.large.everyday-address.12` | Native C engine | 1.3940× | 1.2148–1.6219× | 0.11× | FASTER |
| holdout | `hold.large.everyday-address.12` | Rust engine | 0.0533× | 0.0497–0.0589× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.13` | Python engine | 0.0162× | 0.0148–0.0183× | 6.10× | SLOWDOWN |
| holdout | `hold.large.everyday-address.13` | Native C engine | 0.7271× | 0.6355–0.8459× | 0.22× | SLOWDOWN |
| holdout | `hold.large.everyday-address.13` | Rust engine | 0.1173× | 0.1063–0.1336× | 4.23× | SLOWDOWN |
| holdout | `hold.large.everyday-address.14` | Python engine | 0.0123× | 0.0112–0.0139× | 23.69× | SLOWDOWN |
| holdout | `hold.large.everyday-address.14` | Native C engine | 1.1827× | 0.9989–1.3819× | 0.09× | — |
| holdout | `hold.large.everyday-address.14` | Rust engine | 0.2098× | 0.1784–0.2550× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.15` | Python engine | 0.0192× | 0.0172–0.0220× | 17.65× | SLOWDOWN |
| holdout | `hold.large.everyday-address.15` | Native C engine | 1.2842× | 1.0390–1.6012× | 0.11× | FASTER |
| holdout | `hold.large.everyday-address.15` | Rust engine | 0.0622× | 0.0541–0.0719× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.16` | Python engine | 0.0161× | 0.0156–0.0164× | 6.21× | SLOWDOWN |
| holdout | `hold.large.everyday-address.16` | Native C engine | 0.7299× | 0.6777–0.7633× | 0.13× | SLOWDOWN |
| holdout | `hold.large.everyday-address.16` | Rust engine | 0.1135× | 0.1119–0.1146× | 2.37× | SLOWDOWN |
| holdout | `hold.large.everyday-address.17` | Python engine | 0.0112× | 0.0110–0.0113× | 23.69× | SLOWDOWN |
| holdout | `hold.large.everyday-address.17` | Native C engine | 1.1551× | 1.1404–1.1709× | 0.09× | FASTER |
| holdout | `hold.large.everyday-address.17` | Rust engine | 0.2102× | 0.2032–0.2151× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.18` | Python engine | 0.0161× | 0.0151–0.0167× | 17.65× | SLOWDOWN |
| holdout | `hold.large.everyday-address.18` | Native C engine | 1.3224× | 1.2949–1.3455× | 0.11× | FASTER |
| holdout | `hold.large.everyday-address.18` | Rust engine | 0.0555× | 0.0538–0.0569× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.19` | Python engine | 0.0154× | 0.0149–0.0158× | 5.49× | SLOWDOWN |
| holdout | `hold.large.everyday-address.19` | Native C engine | 0.7645× | 0.7573–0.7723× | 0.54× | SLOWDOWN |
| holdout | `hold.large.everyday-address.19` | Rust engine | 0.1178× | 0.1160–0.1191× | 10.75× | SLOWDOWN |
| holdout | `hold.large.everyday-address.20` | Python engine | 0.0110× | 0.0109–0.0111× | 23.69× | SLOWDOWN |
| holdout | `hold.large.everyday-address.20` | Native C engine | 1.1751× | 1.1624–1.1890× | 0.09× | FASTER |
| holdout | `hold.large.everyday-address.20` | Rust engine | 0.2084× | 0.2047–0.2114× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.21` | Python engine | 0.0166× | 0.0156–0.0185× | 17.65× | SLOWDOWN |
| holdout | `hold.large.everyday-address.21` | Native C engine | 1.4202× | 1.3314–1.5874× | 0.11× | FASTER |
| holdout | `hold.large.everyday-address.21` | Rust engine | 0.0551× | 0.0512–0.0615× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.22` | Python engine | 0.0167× | 0.0157–0.0178× | 5.84× | SLOWDOWN |
| holdout | `hold.large.everyday-address.22` | Native C engine | 0.7633× | 0.6787–0.8542× | 0.36× | SLOWDOWN |
| holdout | `hold.large.everyday-address.22` | Rust engine | 0.1222× | 0.1148–0.1313× | 7.10× | SLOWDOWN |
| holdout | `hold.large.everyday-address.23` | Python engine | 0.0129× | 0.0127–0.0131× | 23.69× | SLOWDOWN |
| holdout | `hold.large.everyday-address.23` | Native C engine | 1.1691× | 1.1377–1.2009× | 0.09× | FASTER |
| holdout | `hold.large.everyday-address.23` | Rust engine | 0.2285× | 0.2106–0.2396× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.24` | Python engine | 0.0150× | 0.0148–0.0152× | 17.65× | SLOWDOWN |
| holdout | `hold.large.everyday-address.24` | Native C engine | 1.3554× | 1.3345–1.3733× | 0.11× | FASTER |
| holdout | `hold.large.everyday-address.24` | Rust engine | 0.0491× | 0.0486–0.0497× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.25` | Python engine | 0.0153× | 0.0142–0.0160× | 6.09× | SLOWDOWN |
| holdout | `hold.large.everyday-address.25` | Native C engine | 0.7697× | 0.7625–0.7771× | 0.22× | SLOWDOWN |
| holdout | `hold.large.everyday-address.25` | Rust engine | 0.1136× | 0.1113–0.1156× | 4.36× | SLOWDOWN |
| holdout | `hold.large.everyday-address.26` | Python engine | 0.0115× | 0.0109–0.0120× | 23.69× | SLOWDOWN |
| holdout | `hold.large.everyday-address.26` | Native C engine | 1.1389× | 1.1121–1.1636× | 0.09× | FASTER |
| holdout | `hold.large.everyday-address.26` | Rust engine | 0.2150× | 0.2034–0.2238× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.27` | Python engine | 0.0180× | 0.0174–0.0184× | 17.65× | SLOWDOWN |
| holdout | `hold.large.everyday-address.27` | Native C engine | 1.2408× | 1.1665–1.2940× | 0.11× | FASTER |
| holdout | `hold.large.everyday-address.27` | Rust engine | 0.0573× | 0.0531–0.0604× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.28` | Python engine | 0.0162× | 0.0157–0.0165× | 6.21× | SLOWDOWN |
| holdout | `hold.large.everyday-address.28` | Native C engine | 0.7501× | 0.7409–0.7587× | 0.13× | SLOWDOWN |
| holdout | `hold.large.everyday-address.28` | Rust engine | 0.1122× | 0.1094–0.1145× | 2.37× | SLOWDOWN |
| holdout | `hold.large.everyday-address.29` | Python engine | 0.0110× | 0.0109–0.0111× | 23.69× | SLOWDOWN |
| holdout | `hold.large.everyday-address.29` | Native C engine | 1.1309× | 1.1067–1.1476× | 0.09× | FASTER |
| holdout | `hold.large.everyday-address.29` | Rust engine | 0.2086× | 0.2072–0.2102× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.30` | Python engine | 0.0172× | 0.0163–0.0188× | 17.65× | SLOWDOWN |
| holdout | `hold.large.everyday-address.30` | Native C engine | 1.3765× | 1.2903–1.5117× | 0.11× | FASTER |
| holdout | `hold.large.everyday-address.30` | Rust engine | 0.0578× | 0.0551–0.0626× | 0.06× | SLOWDOWN |
| holdout | `hold.large.everyday-address.31` | Python engine | 0.0157× | 0.0156–0.0159× | 5.49× | SLOWDOWN |
| holdout | `hold.large.everyday-address.31` | Native C engine | 0.7505× | 0.7410–0.7602× | 0.54× | SLOWDOWN |
| holdout | `hold.large.everyday-address.31` | Rust engine | 0.1170× | 0.1147–0.1189× | 10.75× | SLOWDOWN |
| holdout | `hold.large.structured-text.00` | Python engine | 0.0140× | 0.0139–0.0141× | 20.42× | SLOWDOWN |
| holdout | `hold.large.structured-text.00` | Native C engine | 1.4768× | 1.4598–1.4941× | 0.34× | FASTER |
| holdout | `hold.large.structured-text.00` | Rust engine | 0.0998× | 0.0986–0.1009× | 0.31× | SLOWDOWN |
| holdout | `hold.large.structured-text.01` | Python engine | 0.0109× | 0.0108–0.0110× | 20.87× | SLOWDOWN |
| holdout | `hold.large.structured-text.01` | Native C engine | 2.8021× | 2.7639–2.8415× | 0.19× | FASTER |
| holdout | `hold.large.structured-text.01` | Rust engine | 0.0566× | 0.0559–0.0573× | 3.22× | SLOWDOWN |
| holdout | `hold.large.structured-text.02` | Python engine | 0.0062× | 0.0061–0.0063× | 12.12× | SLOWDOWN |
| holdout | `hold.large.structured-text.02` | Native C engine | 1.8163× | 1.7937–1.8389× | 0.30× | FASTER |
| holdout | `hold.large.structured-text.02` | Rust engine | 0.0462× | 0.0457–0.0467× | 10.96× | SLOWDOWN |
| holdout | `hold.large.structured-text.03` | Python engine | 0.0119× | 0.0118–0.0121× | 24.25× | SLOWDOWN |
| holdout | `hold.large.structured-text.03` | Native C engine | 1.5029× | 1.4785–1.5279× | 0.58× | FASTER |
| holdout | `hold.large.structured-text.03` | Rust engine | 0.0907× | 0.0895–0.0919× | 0.43× | SLOWDOWN |
| holdout | `hold.large.structured-text.04` | Python engine | 0.0112× | 0.0112–0.0113× | 18.53× | SLOWDOWN |
| holdout | `hold.large.structured-text.04` | Native C engine | 2.4293× | 2.3974–2.4634× | 0.12× | FASTER |
| holdout | `hold.large.structured-text.04` | Rust engine | 0.0577× | 0.0572–0.0582× | 1.85× | SLOWDOWN |
| holdout | `hold.large.structured-text.05` | Python engine | 0.0078× | 0.0078–0.0079× | 11.54× | SLOWDOWN |
| holdout | `hold.large.structured-text.05` | Native C engine | 1.7432× | 1.7185–1.7686× | 0.17× | FASTER |
| holdout | `hold.large.structured-text.05` | Rust engine | 0.0938× | 0.0927–0.0950× | 6.13× | SLOWDOWN |
| holdout | `hold.large.structured-text.06` | Python engine | 0.0126× | 0.0123–0.0131× | 35.01× | SLOWDOWN |
| holdout | `hold.large.structured-text.06` | Native C engine | 1.5497× | 1.5133–1.6004× | 0.48× | FASTER |
| holdout | `hold.large.structured-text.06` | Rust engine | 0.0957× | 0.0933–0.0990× | 0.38× | SLOWDOWN |
| holdout | `hold.large.structured-text.07` | Python engine | 0.0105× | 0.0102–0.0111× | 19.58× | SLOWDOWN |
| holdout | `hold.large.structured-text.07` | Native C engine | 3.0897× | 3.0058–3.1579× | 0.49× | FASTER |
| holdout | `hold.large.structured-text.07` | Rust engine | 0.0573× | 0.0545–0.0621× | 8.06× | SLOWDOWN |
| holdout | `hold.large.structured-text.08` | Python engine | 0.0089× | 0.0088–0.0089× | 10.99× | SLOWDOWN |
| holdout | `hold.large.structured-text.08` | Native C engine | 1.6731× | 1.6605–1.6854× | 0.11× | FASTER |
| holdout | `hold.large.structured-text.08` | Rust engine | 0.1511× | 0.1482–0.1535× | 3.49× | SLOWDOWN |
| holdout | `hold.large.structured-text.09` | Python engine | 0.0134× | 0.0128–0.0144× | 26.59× | SLOWDOWN |
| holdout | `hold.large.structured-text.09` | Native C engine | 1.5793× | 1.5041–1.7047× | 0.40× | FASTER |
| holdout | `hold.large.structured-text.09` | Rust engine | 0.1009× | 0.0962–0.1090× | 0.34× | SLOWDOWN |
| holdout | `hold.large.structured-text.10` | Python engine | 0.0107× | 0.0106–0.0108× | 20.75× | SLOWDOWN |
| holdout | `hold.large.structured-text.10` | Native C engine | 2.9722× | 2.9403–3.0077× | 0.33× | FASTER |
| holdout | `hold.large.structured-text.10` | Rust engine | 0.0533× | 0.0524–0.0541× | 5.56× | SLOWDOWN |
| holdout | `hold.large.structured-text.11` | Python engine | 0.0047× | 0.0046–0.0048× | 12.92× | SLOWDOWN |
| holdout | `hold.large.structured-text.11` | Native C engine | 1.8905× | 1.8365–1.9467× | 0.46× | FASTER |
| holdout | `hold.large.structured-text.11` | Rust engine | 0.0236× | 0.0232–0.0240× | 16.92× | SLOWDOWN |
| holdout | `hold.large.structured-text.12` | Python engine | 0.0138× | 0.0136–0.0140× | 19.25× | SLOWDOWN |
| holdout | `hold.large.structured-text.12` | Native C engine | 1.4828× | 1.4294–1.5156× | 0.34× | FASTER |
| holdout | `hold.large.structured-text.12` | Rust engine | 0.1012× | 0.1003–0.1020× | 0.31× | SLOWDOWN |
| holdout | `hold.large.structured-text.13` | Python engine | 0.0106× | 0.0106–0.0107× | 20.87× | SLOWDOWN |
| holdout | `hold.large.structured-text.13` | Native C engine | 2.6647× | 2.4080–2.8229× | 0.19× | FASTER |
| holdout | `hold.large.structured-text.13` | Rust engine | 0.0555× | 0.0544–0.0564× | 3.22× | SLOWDOWN |
| holdout | `hold.large.structured-text.14` | Python engine | 0.0062× | 0.0060–0.0063× | 12.12× | SLOWDOWN |
| holdout | `hold.large.structured-text.14` | Native C engine | 1.8484× | 1.8279–1.8668× | 0.30× | FASTER |
| holdout | `hold.large.structured-text.14` | Rust engine | 0.0464× | 0.0459–0.0468× | 10.96× | SLOWDOWN |
| holdout | `hold.large.structured-text.15` | Python engine | 0.0119× | 0.0115–0.0123× | 24.25× | SLOWDOWN |
| holdout | `hold.large.structured-text.15` | Native C engine | 1.4945× | 1.4558–1.5381× | 0.58× | FASTER |
| holdout | `hold.large.structured-text.15` | Rust engine | 0.0901× | 0.0881–0.0929× | 0.43× | SLOWDOWN |
| holdout | `hold.large.structured-text.16` | Python engine | 0.0114× | 0.0111–0.0119× | 18.53× | SLOWDOWN |
| holdout | `hold.large.structured-text.16` | Native C engine | 2.4591× | 2.3926–2.5644× | 0.12× | FASTER |
| holdout | `hold.large.structured-text.16` | Rust engine | 0.0583× | 0.0567–0.0608× | 1.85× | SLOWDOWN |
| holdout | `hold.large.structured-text.17` | Python engine | 0.0077× | 0.0076–0.0078× | 11.54× | SLOWDOWN |
| holdout | `hold.large.structured-text.17` | Native C engine | 1.7712× | 1.7614–1.7798× | 0.17× | FASTER |
| holdout | `hold.large.structured-text.17` | Rust engine | 0.0922× | 0.0900–0.0939× | 6.13× | SLOWDOWN |
| holdout | `hold.large.structured-text.18` | Python engine | 0.0122× | 0.0121–0.0123× | 35.01× | SLOWDOWN |
| holdout | `hold.large.structured-text.18` | Native C engine | 1.4966× | 1.4837–1.5086× | 0.48× | FASTER |
| holdout | `hold.large.structured-text.18` | Rust engine | 0.0915× | 0.0907–0.0923× | 0.38× | SLOWDOWN |
| holdout | `hold.large.structured-text.19` | Python engine | 0.0102× | 0.0102–0.0103× | 19.46× | SLOWDOWN |
| holdout | `hold.large.structured-text.19` | Native C engine | 3.0105× | 2.9657–3.0566× | 0.50× | FASTER |
| holdout | `hold.large.structured-text.19` | Rust engine | 0.0529× | 0.0521–0.0536× | 8.34× | SLOWDOWN |
| holdout | `hold.large.structured-text.20` | Python engine | 0.0091× | 0.0091–0.0092× | 11.00× | SLOWDOWN |
| holdout | `hold.large.structured-text.20` | Native C engine | 1.6436× | 1.6304–1.6596× | 0.10× | FASTER |
| holdout | `hold.large.structured-text.20` | Rust engine | 0.1601× | 0.1580–0.1618× | 3.32× | SLOWDOWN |
| holdout | `hold.large.structured-text.21` | Python engine | 0.0130× | 0.0128–0.0133× | 26.59× | SLOWDOWN |
| holdout | `hold.large.structured-text.21` | Native C engine | 1.4984× | 1.4175–1.5602× | 0.40× | FASTER |
| holdout | `hold.large.structured-text.21` | Rust engine | 0.0926× | 0.0908–0.0950× | 0.34× | SLOWDOWN |
| holdout | `hold.large.structured-text.22` | Python engine | 0.0106× | 0.0106–0.0107× | 20.75× | SLOWDOWN |
| holdout | `hold.large.structured-text.22` | Native C engine | 2.9501× | 2.9026–2.9976× | 0.33× | FASTER |
| holdout | `hold.large.structured-text.22` | Rust engine | 0.0539× | 0.0535–0.0543× | 5.56× | SLOWDOWN |
| holdout | `hold.large.structured-text.23` | Python engine | 0.0047× | 0.0047–0.0047× | 12.92× | SLOWDOWN |
| holdout | `hold.large.structured-text.23` | Native C engine | 1.8631× | 1.8368–1.8887× | 0.46× | FASTER |
| holdout | `hold.large.structured-text.23` | Rust engine | 0.0234× | 0.0231–0.0236× | 16.92× | SLOWDOWN |
| holdout | `hold.large.structured-text.24` | Python engine | 0.0141× | 0.0139–0.0143× | 19.25× | SLOWDOWN |
| holdout | `hold.large.structured-text.24` | Native C engine | 1.5111× | 1.4954–1.5290× | 0.34× | FASTER |
| holdout | `hold.large.structured-text.24` | Rust engine | 0.0980× | 0.0945–0.1007× | 0.31× | SLOWDOWN |
| holdout | `hold.large.structured-text.25` | Python engine | 0.0108× | 0.0107–0.0110× | 20.81× | SLOWDOWN |
| holdout | `hold.large.structured-text.25` | Native C engine | 2.7627× | 2.6584–2.8365× | 0.20× | FASTER |
| holdout | `hold.large.structured-text.25` | Rust engine | 0.0545× | 0.0538–0.0551× | 3.35× | SLOWDOWN |
| holdout | `hold.large.structured-text.26` | Python engine | 0.0061× | 0.0057–0.0066× | 12.06× | SLOWDOWN |
| holdout | `hold.large.structured-text.26` | Native C engine | 1.9096× | 1.8245–2.0289× | 0.30× | FASTER |
| holdout | `hold.large.structured-text.26` | Rust engine | 0.0457× | 0.0437–0.0487× | 12.03× | SLOWDOWN |
| holdout | `hold.large.structured-text.27` | Python engine | 0.0121× | 0.0118–0.0125× | 34.93× | SLOWDOWN |
| holdout | `hold.large.structured-text.27` | Native C engine | 1.5309× | 1.4986–1.5731× | 0.58× | FASTER |
| holdout | `hold.large.structured-text.27` | Rust engine | 0.0923× | 0.0906–0.0946× | 0.43× | SLOWDOWN |
| holdout | `hold.large.structured-text.28` | Python engine | 0.0121× | 0.0112–0.0132× | 18.53× | SLOWDOWN |
| holdout | `hold.large.structured-text.28` | Native C engine | 2.2488× | 1.9923–2.4502× | 0.12× | FASTER |
| holdout | `hold.large.structured-text.28` | Rust engine | 0.0575× | 0.0533–0.0625× | 1.85× | SLOWDOWN |
| holdout | `hold.large.structured-text.29` | Python engine | 0.0075× | 0.0074–0.0077× | 11.48× | SLOWDOWN |
| holdout | `hold.large.structured-text.29` | Native C engine | 1.8682× | 1.8428–1.9037× | 0.18× | FASTER |
| holdout | `hold.large.structured-text.29` | Rust engine | 0.0904× | 0.0890–0.0923× | 6.75× | SLOWDOWN |
| holdout | `hold.large.structured-text.30` | Python engine | 0.0125× | 0.0123–0.0127× | 33.46× | SLOWDOWN |
| holdout | `hold.large.structured-text.30` | Native C engine | 1.5331× | 1.5042–1.5652× | 0.48× | FASTER |
| holdout | `hold.large.structured-text.30` | Rust engine | 0.0919× | 0.0900–0.0937× | 0.38× | SLOWDOWN |
| holdout | `hold.large.structured-text.31` | Python engine | 0.0104× | 0.0103–0.0105× | 19.33× | SLOWDOWN |
| holdout | `hold.large.structured-text.31` | Native C engine | 3.0691× | 3.0208–3.1335× | 0.50× | FASTER |
| holdout | `hold.large.structured-text.31` | Rust engine | 0.0493× | 0.0464–0.0513× | 8.61× | SLOWDOWN |
| holdout | `hold.large.cleanup.00` | Python engine | 0.0362× | 0.0357–0.0366× | 5.56× | SLOWDOWN |
| holdout | `hold.large.cleanup.00` | Native C engine | 1.8593× | 1.8266–1.8806× | 0.25× | FASTER |
| holdout | `hold.large.cleanup.00` | Rust engine | 0.2590× | 0.2552–0.2621× | 1.45× | SLOWDOWN |
| holdout | `hold.large.cleanup.01` | Python engine | 0.0253× | 0.0244–0.0264× | 7.61× | SLOWDOWN |
| holdout | `hold.large.cleanup.01` | Native C engine | 1.8582× | 1.8144–1.9247× | 0.16× | FASTER |
| holdout | `hold.large.cleanup.01` | Rust engine | 0.2532× | 0.2421–0.2656× | 1.54× | SLOWDOWN |
| holdout | `hold.large.cleanup.02` | Python engine | 0.0321× | 0.0315–0.0325× | 5.67× | SLOWDOWN |
| holdout | `hold.large.cleanup.02` | Native C engine | 2.0192× | 2.0005–2.0406× | 0.45× | FASTER |
| holdout | `hold.large.cleanup.02` | Rust engine | 0.2662× | 0.2636–0.2701× | 3.12× | SLOWDOWN |
| holdout | `hold.large.cleanup.03` | Python engine | 0.0262× | 0.0248–0.0288× | 12.10× | SLOWDOWN |
| holdout | `hold.large.cleanup.03` | Native C engine | 2.3842× | 2.2587–2.6161× | 0.17× | FASTER |
| holdout | `hold.large.cleanup.03` | Rust engine | 0.3078× | 0.2866–0.3253× | 3.86× | SLOWDOWN |
| holdout | `hold.large.cleanup.04` | Python engine | 0.0367× | 0.0365–0.0370× | 5.56× | SLOWDOWN |
| holdout | `hold.large.cleanup.04` | Native C engine | 1.8992× | 1.8871–1.9101× | 0.25× | FASTER |
| holdout | `hold.large.cleanup.04` | Rust engine | 0.2637× | 0.2610–0.2662× | 1.45× | SLOWDOWN |
| holdout | `hold.large.cleanup.05` | Python engine | 0.0254× | 0.0249–0.0264× | 7.61× | SLOWDOWN |
| holdout | `hold.large.cleanup.05` | Native C engine | 1.8588× | 1.8167–1.9315× | 0.16× | FASTER |
| holdout | `hold.large.cleanup.05` | Rust engine | 0.2553× | 0.2483–0.2666× | 1.54× | SLOWDOWN |
| holdout | `hold.large.cleanup.06` | Python engine | 0.0319× | 0.0316–0.0322× | 5.67× | SLOWDOWN |
| holdout | `hold.large.cleanup.06` | Native C engine | 2.0300× | 2.0054–2.0521× | 0.45× | FASTER |
| holdout | `hold.large.cleanup.06` | Rust engine | 0.2575× | 0.2522–0.2618× | 3.09× | SLOWDOWN |
| holdout | `hold.large.cleanup.07` | Python engine | 0.0258× | 0.0249–0.0274× | 12.10× | SLOWDOWN |
| holdout | `hold.large.cleanup.07` | Native C engine | 2.3427× | 2.2749–2.4690× | 0.17× | FASTER |
| holdout | `hold.large.cleanup.07` | Rust engine | 0.3249× | 0.3107–0.3477× | 3.86× | SLOWDOWN |
| holdout | `hold.large.cleanup.08` | Python engine | 0.0374× | 0.0370–0.0377× | 5.55× | SLOWDOWN |
| holdout | `hold.large.cleanup.08` | Native C engine | 1.9094× | 1.8887–1.9289× | 0.25× | FASTER |
| holdout | `hold.large.cleanup.08` | Rust engine | 0.2659× | 0.2589–0.2715× | 1.51× | SLOWDOWN |
| holdout | `hold.large.cleanup.09` | Python engine | 0.0249× | 0.0248–0.0250× | 7.61× | SLOWDOWN |
| holdout | `hold.large.cleanup.09` | Native C engine | 1.8208× | 1.8082–1.8323× | 0.16× | FASTER |
| holdout | `hold.large.cleanup.09` | Rust engine | 0.2510× | 0.2475–0.2535× | 1.54× | SLOWDOWN |
| holdout | `hold.large.cleanup.10` | Python engine | 0.0344× | 0.0339–0.0351× | 5.64× | SLOWDOWN |
| holdout | `hold.large.cleanup.10` | Native C engine | 1.9925× | 1.8509–2.1060× | 0.45× | FASTER |
| holdout | `hold.large.cleanup.10` | Rust engine | 0.2851× | 0.2804–0.2926× | 3.39× | SLOWDOWN |
| holdout | `hold.large.cleanup.11` | Python engine | 0.0248× | 0.0246–0.0251× | 12.10× | SLOWDOWN |
| holdout | `hold.large.cleanup.11` | Native C engine | 2.2610× | 2.2446–2.2786× | 0.17× | FASTER |
| holdout | `hold.large.cleanup.11` | Rust engine | 0.3116× | 0.3037–0.3184× | 3.86× | SLOWDOWN |
| holdout | `hold.large.cleanup.12` | Python engine | 0.0365× | 0.0363–0.0368× | 5.56× | SLOWDOWN |
| holdout | `hold.large.cleanup.12` | Native C engine | 1.8839× | 1.8714–1.8939× | 0.25× | FASTER |
| holdout | `hold.large.cleanup.12` | Rust engine | 0.2601× | 0.2585–0.2616× | 1.45× | SLOWDOWN |
| holdout | `hold.large.cleanup.13` | Python engine | 0.0249× | 0.0247–0.0251× | 7.61× | SLOWDOWN |
| holdout | `hold.large.cleanup.13` | Native C engine | 1.8439× | 1.8277–1.8574× | 0.16× | FASTER |
| holdout | `hold.large.cleanup.13` | Rust engine | 0.2526× | 0.2490–0.2559× | 1.54× | SLOWDOWN |
| holdout | `hold.large.cleanup.14` | Python engine | 0.0325× | 0.0314–0.0346× | 5.67× | SLOWDOWN |
| holdout | `hold.large.cleanup.14` | Native C engine | 1.9785× | 1.7732–2.1738× | 0.45× | FASTER |
| holdout | `hold.large.cleanup.14` | Rust engine | 0.2649× | 0.2521–0.2841× | 3.12× | SLOWDOWN |
| holdout | `hold.large.cleanup.15` | Python engine | 0.0250× | 0.0248–0.0252× | 12.10× | SLOWDOWN |
| holdout | `hold.large.cleanup.15` | Native C engine | 2.2805× | 2.2579–2.3050× | 0.17× | FASTER |
| holdout | `hold.large.cleanup.15` | Rust engine | 0.3161× | 0.3081–0.3230× | 3.86× | SLOWDOWN |
| holdout | `hold.large.cleanup.16` | Python engine | 0.0370× | 0.0368–0.0373× | 5.56× | SLOWDOWN |
| holdout | `hold.large.cleanup.16` | Native C engine | 1.9140× | 1.9022–1.9269× | 0.25× | FASTER |
| holdout | `hold.large.cleanup.16` | Rust engine | 0.2661× | 0.2641–0.2680× | 1.45× | SLOWDOWN |
| holdout | `hold.large.cleanup.17` | Python engine | 0.0277× | 0.0250–0.0314× | 7.61× | SLOWDOWN |
| holdout | `hold.large.cleanup.17` | Native C engine | 1.9609× | 1.8527–2.1308× | 0.16× | FASTER |
| holdout | `hold.large.cleanup.17` | Rust engine | 0.2670× | 0.2503–0.2907× | 1.54× | SLOWDOWN |
| holdout | `hold.large.cleanup.18` | Python engine | 0.0317× | 0.0315–0.0319× | 5.67× | SLOWDOWN |
| holdout | `hold.large.cleanup.18` | Native C engine | 2.0107× | 2.0002–2.0204× | 0.45× | FASTER |
| holdout | `hold.large.cleanup.18` | Rust engine | 0.2589× | 0.2534–0.2630× | 3.12× | SLOWDOWN |
| holdout | `hold.large.cleanup.19` | Python engine | 0.0248× | 0.0227–0.0274× | 12.10× | SLOWDOWN |
| holdout | `hold.large.cleanup.19` | Native C engine | 2.3703× | 2.2614–2.5619× | 0.17× | FASTER |
| holdout | `hold.large.cleanup.19` | Rust engine | 0.3075× | 0.2728–0.3446× | 3.86× | SLOWDOWN |
| holdout | `hold.large.cleanup.20` | Python engine | 0.0372× | 0.0364–0.0386× | 5.56× | SLOWDOWN |
| holdout | `hold.large.cleanup.20` | Native C engine | 1.9195× | 1.8767–2.0007× | 0.25× | FASTER |
| holdout | `hold.large.cleanup.20` | Rust engine | 0.2626× | 0.2532–0.2761× | 1.45× | SLOWDOWN |
| holdout | `hold.large.cleanup.21` | Python engine | 0.0277× | 0.0255–0.0310× | 7.60× | SLOWDOWN |
| holdout | `hold.large.cleanup.21` | Native C engine | 1.9567× | 1.8652–2.1264× | 0.16× | FASTER |
| holdout | `hold.large.cleanup.21` | Rust engine | 0.2826× | 0.2571–0.3210× | 1.61× | SLOWDOWN |
| holdout | `hold.large.cleanup.22` | Python engine | 0.0340× | 0.0334–0.0348× | 5.64× | SLOWDOWN |
| holdout | `hold.large.cleanup.22` | Native C engine | 2.0528× | 2.0235–2.0944× | 0.45× | FASTER |
| holdout | `hold.large.cleanup.22` | Rust engine | 0.2797× | 0.2737–0.2866× | 3.36× | SLOWDOWN |
| holdout | `hold.large.cleanup.23` | Python engine | 0.0252× | 0.0248–0.0259× | 12.10× | SLOWDOWN |
| holdout | `hold.large.cleanup.23` | Native C engine | 2.2931× | 2.2573–2.3543× | 0.17× | FASTER |
| holdout | `hold.large.cleanup.23` | Rust engine | 0.3223× | 0.3164–0.3320× | 3.86× | SLOWDOWN |
| holdout | `hold.large.cleanup.24` | Python engine | 0.0354× | 0.0336–0.0374× | 5.56× | SLOWDOWN |
| holdout | `hold.large.cleanup.24` | Native C engine | 1.8088× | 1.6036–1.9659× | 0.25× | FASTER |
| holdout | `hold.large.cleanup.24` | Rust engine | 0.2533× | 0.2391–0.2683× | 1.45× | SLOWDOWN |
| holdout | `hold.large.cleanup.25` | Python engine | 0.0251× | 0.0246–0.0257× | 7.61× | SLOWDOWN |
| holdout | `hold.large.cleanup.25` | Native C engine | 1.8757× | 1.8183–1.9719× | 0.16× | FASTER |
| holdout | `hold.large.cleanup.25` | Rust engine | 0.2547× | 0.2427–0.2688× | 1.54× | SLOWDOWN |
| holdout | `hold.large.cleanup.26` | Python engine | 0.0317× | 0.0313–0.0321× | 5.67× | SLOWDOWN |
| holdout | `hold.large.cleanup.26` | Native C engine | 1.9427× | 1.8076–2.0217× | 0.45× | FASTER |
| holdout | `hold.large.cleanup.26` | Rust engine | 0.2600× | 0.2552–0.2638× | 3.12× | SLOWDOWN |
| holdout | `hold.large.cleanup.27` | Python engine | 0.0249× | 0.0246–0.0253× | 12.10× | SLOWDOWN |
| holdout | `hold.large.cleanup.27` | Native C engine | 2.2808× | 2.2597–2.3137× | 0.17× | FASTER |
| holdout | `hold.large.cleanup.27` | Rust engine | 0.3084× | 0.2986–0.3177× | 3.86× | SLOWDOWN |
| holdout | `hold.large.cleanup.28` | Python engine | 0.0389× | 0.0364–0.0425× | 5.56× | SLOWDOWN |
| holdout | `hold.large.cleanup.28` | Native C engine | 2.0012× | 1.8523–2.2065× | 0.25× | FASTER |
| holdout | `hold.large.cleanup.28` | Rust engine | 0.2621× | 0.2450–0.2857× | 1.45× | SLOWDOWN |
| holdout | `hold.large.cleanup.29` | Python engine | 0.0254× | 0.0246–0.0267× | 7.61× | SLOWDOWN |
| holdout | `hold.large.cleanup.29` | Native C engine | 1.8136× | 1.6555–1.9597× | 0.16× | FASTER |
| holdout | `hold.large.cleanup.29` | Rust engine | 0.2585× | 0.2495–0.2712× | 1.54× | SLOWDOWN |
| holdout | `hold.large.cleanup.30` | Python engine | 0.0320× | 0.0317–0.0322× | 5.67× | SLOWDOWN |
| holdout | `hold.large.cleanup.30` | Native C engine | 2.0234× | 2.0051–2.0431× | 0.45× | FASTER |
| holdout | `hold.large.cleanup.30` | Rust engine | 0.2639× | 0.2627–0.2651× | 3.12× | SLOWDOWN |
| holdout | `hold.large.cleanup.31` | Python engine | 0.0241× | 0.0240–0.0243× | 12.15× | SLOWDOWN |
| holdout | `hold.large.cleanup.31` | Native C engine | 2.2274× | 2.2130–2.2412× | 0.17× | FASTER |
| holdout | `hold.large.cleanup.31` | Rust engine | 0.3055× | 0.2988–0.3110× | 3.68× | SLOWDOWN |
| holdout | `hold.large.escape.00` | Python engine | 0.9709× | 0.9309–0.9974× | 1.00× | — |
| holdout | `hold.large.escape.00` | Native C engine | 3.1239× | 3.0997–3.1562× | 0.59× | FASTER |
| holdout | `hold.large.escape.00` | Rust engine | 0.9952× | 0.9883–1.0006× | 1.00× | — |
| holdout | `hold.large.escape.01` | Python engine | 0.9979× | 0.9897–1.0056× | 0.68× | — |
| holdout | `hold.large.escape.01` | Native C engine | 4.1491× | 3.6044–4.5444× | 0.32× | FASTER |
| holdout | `hold.large.escape.01` | Rust engine | 0.9878× | 0.9348–1.0211× | 0.68× | — |
| holdout | `hold.large.escape.02` | Python engine | 1.0520× | 0.9966–1.1305× | 1.00× | — |
| holdout | `hold.large.escape.02` | Native C engine | 3.0639× | 2.8928–3.2823× | 0.59× | FASTER |
| holdout | `hold.large.escape.02` | Rust engine | 1.0489× | 0.9938–1.1288× | 1.00× | — |
| holdout | `hold.large.escape.03` | Python engine | 1.0434× | 0.9906–1.1449× | 0.68× | — |
| holdout | `hold.large.escape.03` | Native C engine | 4.0445× | 3.7641–4.4170× | 0.32× | FASTER |
| holdout | `hold.large.escape.03` | Rust engine | 1.0526× | 0.9971–1.1557× | 0.68× | — |
| holdout | `hold.large.escape.04` | Python engine | 1.0048× | 0.9741–1.0516× | 1.00× | — |
| holdout | `hold.large.escape.04` | Native C engine | 3.2398× | 3.1608–3.3723× | 0.59× | FASTER |
| holdout | `hold.large.escape.04` | Rust engine | 1.0148× | 0.9901–1.0582× | 1.00× | — |
| holdout | `hold.large.escape.05` | Python engine | 1.0009× | 0.9899–1.0120× | 0.68× | — |
| holdout | `hold.large.escape.05` | Native C engine | 4.3659× | 4.2910–4.4320× | 0.32× | FASTER |
| holdout | `hold.large.escape.05` | Rust engine | 1.0109× | 1.0013–1.0205× | 0.68× | FASTER |
| holdout | `hold.large.escape.06` | Python engine | 0.9953× | 0.9907–1.0006× | 1.00× | — |
| holdout | `hold.large.escape.06` | Native C engine | 2.9261× | 2.8972–2.9552× | 0.59× | FASTER |
| holdout | `hold.large.escape.06` | Rust engine | 1.0038× | 0.9953–1.0151× | 1.00× | — |
| holdout | `hold.large.escape.07` | Python engine | 0.9915× | 0.9611–1.0180× | 0.68× | — |
| holdout | `hold.large.escape.07` | Native C engine | 3.6582× | 3.5724–3.7521× | 0.32× | FASTER |
| holdout | `hold.large.escape.07` | Rust engine | 1.0288× | 1.0058–1.0565× | 0.68× | FASTER |
| holdout | `hold.large.escape.08` | Python engine | 1.0024× | 0.9680–1.0483× | 1.00× | — |
| holdout | `hold.large.escape.08` | Native C engine | 3.2840× | 3.2034–3.4078× | 0.59× | FASTER |
| holdout | `hold.large.escape.08` | Rust engine | 0.9921× | 0.9269–1.0466× | 1.00× | — |
| holdout | `hold.large.escape.09` | Python engine | 1.0020× | 0.9962–1.0078× | 0.68× | — |
| holdout | `hold.large.escape.09` | Native C engine | 4.2893× | 4.1937–4.4037× | 0.32× | FASTER |
| holdout | `hold.large.escape.09` | Rust engine | 1.0201× | 1.0148–1.0266× | 0.68× | FASTER |
| holdout | `hold.large.escape.10` | Python engine | 0.9989× | 0.9580–1.0610× | 1.00× | — |
| holdout | `hold.large.escape.10` | Native C engine | 3.0450× | 2.8915–3.2284× | 0.59× | FASTER |
| holdout | `hold.large.escape.10` | Rust engine | 1.0114× | 0.9764–1.0681× | 1.00× | — |
| holdout | `hold.large.escape.11` | Python engine | 0.9367× | 0.8386–1.0102× | 0.68× | — |
| holdout | `hold.large.escape.11` | Native C engine | 3.9310× | 3.7685–4.1426× | 0.32× | FASTER |
| holdout | `hold.large.escape.11` | Rust engine | 1.0040× | 0.9884–1.0170× | 0.68× | — |
| holdout | `hold.large.escape.12` | Python engine | 1.0406× | 0.9936–1.1277× | 1.00× | — |
| holdout | `hold.large.escape.12` | Native C engine | 3.2503× | 2.9473–3.6163× | 0.59× | FASTER |
| holdout | `hold.large.escape.12` | Rust engine | 1.0470× | 0.9996–1.1328× | 1.00× | — |
| holdout | `hold.large.escape.13` | Python engine | 1.0254× | 0.9930–1.0826× | 0.68× | — |
| holdout | `hold.large.escape.13` | Native C engine | 4.5162× | 4.2896–4.8199× | 0.32× | FASTER |
| holdout | `hold.large.escape.13` | Rust engine | 1.0358× | 1.0042–1.0909× | 0.68× | FASTER |
| holdout | `hold.large.escape.14` | Python engine | 0.9935× | 0.9815–1.0067× | 1.00× | — |
| holdout | `hold.large.escape.14` | Native C engine | 2.8294× | 2.7901–2.8656× | 0.59× | FASTER |
| holdout | `hold.large.escape.14` | Rust engine | 0.9883× | 0.9767–1.0002× | 1.00× | — |
| holdout | `hold.large.escape.15` | Python engine | 0.9964× | 0.9785–1.0163× | 0.68× | — |
| holdout | `hold.large.escape.15` | Native C engine | 3.7082× | 3.5786–3.8864× | 0.32× | FASTER |
| holdout | `hold.large.escape.15` | Rust engine | 1.0121× | 0.9935–1.0323× | 0.68× | — |
| holdout | `hold.large.escape.16` | Python engine | 1.0103× | 0.9929–1.0338× | 1.00× | — |
| holdout | `hold.large.escape.16` | Native C engine | 3.1579× | 2.9903–3.2896× | 0.59× | FASTER |
| holdout | `hold.large.escape.16` | Rust engine | 1.0027× | 0.9748–1.0309× | 1.00× | — |
| holdout | `hold.large.escape.17` | Python engine | 0.9904× | 0.9829–0.9977× | 0.68× | — |
| holdout | `hold.large.escape.17` | Native C engine | 4.3286× | 4.2127–4.4502× | 0.32× | FASTER |
| holdout | `hold.large.escape.17` | Rust engine | 1.0122× | 1.0040–1.0200× | 0.68× | FASTER |
| holdout | `hold.large.escape.18` | Python engine | 0.9528× | 0.8706–0.9994× | 1.00× | — |
| holdout | `hold.large.escape.18` | Native C engine | 2.9218× | 2.8759–2.9922× | 0.59× | FASTER |
| holdout | `hold.large.escape.18` | Rust engine | 0.9926× | 0.9647–1.0126× | 1.00× | — |
| holdout | `hold.large.escape.19` | Python engine | 0.9935× | 0.9749–1.0153× | 0.68× | — |
| holdout | `hold.large.escape.19` | Native C engine | 3.6942× | 3.6163–3.7754× | 0.32× | FASTER |
| holdout | `hold.large.escape.19` | Rust engine | 1.0096× | 0.9906–1.0271× | 0.68× | — |
| holdout | `hold.large.escape.20` | Python engine | 0.9863× | 0.9676–1.0005× | 1.00× | — |
| holdout | `hold.large.escape.20` | Native C engine | 2.9953× | 2.6678–3.1837× | 0.59× | FASTER |
| holdout | `hold.large.escape.20` | Rust engine | 0.9891× | 0.9717–1.0009× | 1.00× | — |
| holdout | `hold.large.escape.21` | Python engine | 1.0020× | 0.9913–1.0132× | 0.68× | — |
| holdout | `hold.large.escape.21` | Native C engine | 4.2376× | 4.1208–4.3463× | 0.32× | FASTER |
| holdout | `hold.large.escape.21` | Rust engine | 1.0049× | 0.9872–1.0201× | 0.68× | — |
| holdout | `hold.large.escape.22` | Python engine | 0.9506× | 0.8702–0.9990× | 1.00× | — |
| holdout | `hold.large.escape.22` | Native C engine | 2.9384× | 2.8573–3.0405× | 0.59× | FASTER |
| holdout | `hold.large.escape.22` | Rust engine | 0.9942× | 0.9804–1.0073× | 1.00× | — |
| holdout | `hold.large.escape.23` | Python engine | 0.8639× | 0.6565–0.9962× | 0.68× | — |
| holdout | `hold.large.escape.23` | Native C engine | 3.8220× | 3.6982–3.9998× | 0.32× | FASTER |
| holdout | `hold.large.escape.23` | Rust engine | 0.9590× | 0.8519–1.0252× | 0.68× | — |
| holdout | `hold.large.escape.24` | Python engine | 1.0006× | 0.9905–1.0172× | 1.00× | — |
| holdout | `hold.large.escape.24` | Native C engine | 3.1805× | 3.1045–3.2523× | 0.59× | FASTER |
| holdout | `hold.large.escape.24` | Rust engine | 1.0055× | 0.9960–1.0214× | 1.00× | — |
| holdout | `hold.large.escape.25` | Python engine | 0.9556× | 0.8942–0.9917× | 0.68× | — |
| holdout | `hold.large.escape.25` | Native C engine | 4.2839× | 4.1855–4.3694× | 0.32× | FASTER |
| holdout | `hold.large.escape.25` | Rust engine | 0.9896× | 0.9566–1.0093× | 0.68× | — |
| holdout | `hold.large.escape.26` | Python engine | 1.0144× | 0.9812–1.0699× | 1.00× | — |
| holdout | `hold.large.escape.26` | Native C engine | 3.0364× | 2.8981–3.2219× | 0.59× | FASTER |
| holdout | `hold.large.escape.26` | Rust engine | 1.0222× | 0.9858–1.0801× | 1.00× | — |
| holdout | `hold.large.escape.27` | Python engine | 1.0018× | 0.9855–1.0193× | 0.68× | — |
| holdout | `hold.large.escape.27` | Native C engine | 3.8978× | 3.7441–4.0907× | 0.32× | FASTER |
| holdout | `hold.large.escape.27` | Rust engine | 0.9620× | 0.8736–1.0202× | 0.68× | — |
| holdout | `hold.large.escape.28` | Python engine | 0.9631× | 0.8780–1.0215× | 1.00× | — |
| holdout | `hold.large.escape.28` | Native C engine | 3.2291× | 3.1813–3.2937× | 0.59× | FASTER |
| holdout | `hold.large.escape.28` | Rust engine | 0.9994× | 0.9624–1.0289× | 1.00× | — |
| holdout | `hold.large.escape.29` | Python engine | 0.9995× | 0.9904–1.0085× | 0.68× | — |
| holdout | `hold.large.escape.29` | Native C engine | 4.4996× | 4.4038–4.6035× | 0.32× | FASTER |
| holdout | `hold.large.escape.29` | Rust engine | 1.0184× | 1.0049–1.0287× | 0.68× | FASTER |
| holdout | `hold.large.escape.30` | Python engine | 1.0705× | 1.0116–1.1540× | 1.00× | FASTER |
| holdout | `hold.large.escape.30` | Native C engine | 3.1374× | 2.9415–3.4045× | 0.59× | FASTER |
| holdout | `hold.large.escape.30` | Rust engine | 1.0378× | 0.9544–1.1359× | 1.00× | — |
| holdout | `hold.large.escape.31` | Python engine | 0.9557× | 0.9080–0.9915× | 0.68× | — |
| holdout | `hold.large.escape.31` | Native C engine | 3.8306× | 3.6141–4.0866× | 0.32× | FASTER |
| holdout | `hold.large.escape.31` | Rust engine | 0.8736× | 0.6582–1.0190× | 0.68× | — |
| holdout | `hold.large.bytes-replace.00` | Python engine | 0.0264× | 0.0260–0.0268× | 8.07× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.00` | Native C engine | 1.0172× | 0.9827–1.0450× | 0.85× | — |
| holdout | `hold.large.bytes-replace.00` | Rust engine | 0.0848× | 0.0841–0.0854× | 1.47× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.01` | Python engine | 0.0227× | 0.0221–0.0236× | 9.37× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.01` | Native C engine | 1.1073× | 1.0096–1.1824× | 1.47× | FASTER |
| holdout | `hold.large.bytes-replace.01` | Rust engine | 0.0879× | 0.0849–0.0920× | 2.53× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.02` | Python engine | 0.0225× | 0.0221–0.0230× | 9.55× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.02` | Native C engine | 1.2439× | 1.1808–1.2915× | 2.54× | FASTER |
| holdout | `hold.large.bytes-replace.02` | Rust engine | 0.0869× | 0.0852–0.0888× | 4.71× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.03` | Python engine | 0.0205× | 0.0202–0.0208× | 9.81× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.03` | Native C engine | 1.2754× | 1.2537–1.2978× | 2.68× | FASTER |
| holdout | `hold.large.bytes-replace.03` | Rust engine | 0.0880× | 0.0872–0.0892× | 4.91× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.04` | Python engine | 0.0269× | 0.0266–0.0273× | 8.06× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.04` | Native C engine | 1.0566× | 1.0392–1.0746× | 0.85× | FASTER |
| holdout | `hold.large.bytes-replace.04` | Rust engine | 0.0847× | 0.0838–0.0857× | 1.60× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.05` | Python engine | 0.0214× | 0.0213–0.0217× | 9.76× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.05` | Native C engine | 1.0564× | 1.0365–1.0794× | 1.28× | FASTER |
| holdout | `hold.large.bytes-replace.05` | Rust engine | 0.0819× | 0.0805–0.0832× | 2.89× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.06` | Python engine | 0.0224× | 0.0218–0.0231× | 9.55× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.06` | Native C engine | 1.2671× | 1.2381–1.3089× | 2.54× | FASTER |
| holdout | `hold.large.bytes-replace.06` | Rust engine | 0.0869× | 0.0850–0.0894× | 4.71× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.07` | Python engine | 0.0204× | 0.0197–0.0218× | 9.80× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.07` | Native C engine | 1.2769× | 1.1716–1.4047× | 2.66× | FASTER |
| holdout | `hold.large.bytes-replace.07` | Rust engine | 0.0870× | 0.0820–0.0940× | 5.35× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.08` | Python engine | 0.0272× | 0.0262–0.0284× | 8.06× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.08` | Native C engine | 1.0854× | 1.0482–1.1226× | 0.85× | FASTER |
| holdout | `hold.large.bytes-replace.08` | Rust engine | 0.0873× | 0.0851–0.0905× | 1.60× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.09` | Python engine | 0.0233× | 0.0219–0.0254× | 9.35× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.09` | Native C engine | 1.0898× | 0.9464–1.2428× | 1.47× | — |
| holdout | `hold.large.bytes-replace.09` | Rust engine | 0.0866× | 0.0811–0.0941× | 2.77× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.10` | Python engine | 0.0239× | 0.0224–0.0263× | 9.02× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.10` | Native C engine | 1.1231× | 1.0752–1.2029× | 1.33× | FASTER |
| holdout | `hold.large.bytes-replace.10` | Rust engine | 0.0738× | 0.0705–0.0803× | 5.56× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.11` | Python engine | 0.0196× | 0.0194–0.0197× | 9.81× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.11` | Native C engine | 1.2663× | 1.2539–1.2787× | 2.68× | FASTER |
| holdout | `hold.large.bytes-replace.11` | Rust engine | 0.0844× | 0.0810–0.0865× | 4.91× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.12` | Python engine | 0.0266× | 0.0256–0.0277× | 8.06× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.12` | Native C engine | 0.9994× | 0.9361–1.0516× | 0.85× | — |
| holdout | `hold.large.bytes-replace.12` | Rust engine | 0.0846× | 0.0828–0.0867× | 1.60× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.13` | Python engine | 0.0231× | 0.0221–0.0250× | 9.35× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.13` | Native C engine | 1.1855× | 1.1294–1.2819× | 1.47× | FASTER |
| holdout | `hold.large.bytes-replace.13` | Rust engine | 0.0880× | 0.0843–0.0951× | 2.77× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.14` | Python engine | 0.0236× | 0.0224–0.0252× | 9.55× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.14` | Native C engine | 1.2919× | 1.1611–1.4118× | 2.54× | FASTER |
| holdout | `hold.large.bytes-replace.14` | Rust engine | 0.0879× | 0.0798–0.0969× | 4.71× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.15` | Python engine | 0.0233× | 0.0229–0.0237× | 10.04× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.15` | Native C engine | 1.0768× | 1.0587–1.0958× | 1.42× | FASTER |
| holdout | `hold.large.bytes-replace.15` | Rust engine | 0.0563× | 0.0547–0.0577× | 10.89× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.16` | Python engine | 0.0262× | 0.0254–0.0272× | 8.06× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.16` | Native C engine | 1.0468× | 1.0052–1.0973× | 0.85× | FASTER |
| holdout | `hold.large.bytes-replace.16` | Rust engine | 0.0826× | 0.0796–0.0860× | 1.60× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.17` | Python engine | 0.0219× | 0.0212–0.0229× | 9.33× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.17` | Native C engine | 1.1324× | 1.0921–1.1946× | 1.47× | FASTER |
| holdout | `hold.large.bytes-replace.17` | Rust engine | 0.0834× | 0.0797–0.0885× | 3.02× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.18` | Python engine | 0.0227× | 0.0211–0.0248× | 9.55× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.18` | Native C engine | 1.2666× | 1.1542–1.4023× | 2.54× | FASTER |
| holdout | `hold.large.bytes-replace.18` | Rust engine | 0.0866× | 0.0802–0.0947× | 4.71× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.19` | Python engine | 0.0203× | 0.0188–0.0223× | 9.80× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.19` | Native C engine | 1.2355× | 1.0834–1.3818× | 2.66× | FASTER |
| holdout | `hold.large.bytes-replace.19` | Rust engine | 0.0885× | 0.0801–0.0985× | 5.35× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.20` | Python engine | 0.0265× | 0.0252–0.0278× | 8.04× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.20` | Native C engine | 1.1085× | 1.0669–1.1586× | 0.85× | FASTER |
| holdout | `hold.large.bytes-replace.20` | Rust engine | 0.0835× | 0.0794–0.0878× | 1.74× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.21` | Python engine | 0.0230× | 0.0217–0.0253× | 9.33× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.21` | Native C engine | 1.1068× | 0.9968–1.2583× | 1.47× | — |
| holdout | `hold.large.bytes-replace.21` | Rust engine | 0.0865× | 0.0802–0.0962× | 3.02× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.22` | Python engine | 0.0221× | 0.0213–0.0226× | 9.55× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.22` | Native C engine | 1.2209× | 1.1453–1.2690× | 2.54× | FASTER |
| holdout | `hold.large.bytes-replace.22` | Rust engine | 0.0864× | 0.0845–0.0878× | 4.71× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.23` | Python engine | 0.0198× | 0.0197–0.0199× | 9.80× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.23` | Native C engine | 1.2726× | 1.2571–1.2856× | 2.66× | FASTER |
| holdout | `hold.large.bytes-replace.23` | Rust engine | 0.0860× | 0.0855–0.0865× | 5.35× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.24` | Python engine | 0.0274× | 0.0267–0.0285× | 8.06× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.24` | Native C engine | 1.0844× | 1.0519–1.1346× | 0.85× | FASTER |
| holdout | `hold.large.bytes-replace.24` | Rust engine | 0.0870× | 0.0847–0.0908× | 1.60× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.25` | Python engine | 0.0219× | 0.0214–0.0227× | 9.76× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.25` | Native C engine | 1.0854× | 1.0543–1.1291× | 1.28× | FASTER |
| holdout | `hold.large.bytes-replace.25` | Rust engine | 0.0840× | 0.0817–0.0877× | 2.89× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.26` | Python engine | 0.0222× | 0.0216–0.0231× | 9.52× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.26` | Native C engine | 1.2925× | 1.2569–1.3449× | 2.54× | FASTER |
| holdout | `hold.large.bytes-replace.26` | Rust engine | 0.0861× | 0.0827–0.0902× | 5.13× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.27` | Python engine | 0.0201× | 0.0197–0.0204× | 9.80× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.27` | Native C engine | 1.3019× | 1.2791–1.3293× | 2.66× | FASTER |
| holdout | `hold.large.bytes-replace.27` | Rust engine | 0.0871× | 0.0856–0.0888× | 5.35× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.28` | Python engine | 0.0273× | 0.0268–0.0282× | 8.03× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.28` | Native C engine | 1.0899× | 1.0536–1.1320× | 0.85× | FASTER |
| holdout | `hold.large.bytes-replace.28` | Rust engine | 0.0876× | 0.0854–0.0907× | 1.87× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.29` | Python engine | 0.0220× | 0.0218–0.0223× | 9.33× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.29` | Native C engine | 1.1095× | 1.0636–1.1396× | 1.47× | FASTER |
| holdout | `hold.large.bytes-replace.29` | Rust engine | 0.0846× | 0.0836–0.0858× | 3.02× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.30` | Python engine | 0.0234× | 0.0229–0.0240× | 8.99× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.30` | Native C engine | 1.1026× | 1.0730–1.1341× | 1.34× | FASTER |
| holdout | `hold.large.bytes-replace.30` | Rust engine | 0.0697× | 0.0681–0.0715× | 6.59× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.31` | Python engine | 0.0198× | 0.0197–0.0199× | 9.80× | SLOWDOWN |
| holdout | `hold.large.bytes-replace.31` | Native C engine | 1.2806× | 1.2634–1.2959× | 2.66× | FASTER |
| holdout | `hold.large.bytes-replace.31` | Rust engine | 0.0865× | 0.0858–0.0872× | 5.35× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.00` | Python engine | 0.0207× | 0.0205–0.0208× | 6.31× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.00` | Native C engine | 1.1569× | 1.1475–1.1669× | 0.21× | FASTER |
| holdout | `hold.large.ascii-mode.00` | Rust engine | 0.0911× | 0.0903–0.0919× | 0.95× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.01` | Python engine | 0.0210× | 0.0206–0.0217× | 6.43× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.01` | Native C engine | 1.1983× | 1.1732–1.2355× | 0.35× | FASTER |
| holdout | `hold.large.ascii-mode.01` | Rust engine | 0.0724× | 0.0710–0.0747× | 1.13× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.02` | Python engine | 0.0206× | 0.0205–0.0208× | 6.73× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.02` | Native C engine | 1.2104× | 1.1974–1.2243× | 0.50× | FASTER |
| holdout | `hold.large.ascii-mode.02` | Rust engine | 0.0502× | 0.0497–0.0507× | 1.33× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.03` | Python engine | 0.0203× | 0.0203–0.0204× | 7.04× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.03` | Native C engine | 1.1788× | 1.1151–1.2168× | 0.66× | FASTER |
| holdout | `hold.large.ascii-mode.03` | Rust engine | 0.0316× | 0.0313–0.0318× | 1.55× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.04` | Python engine | 0.0214× | 0.0208–0.0223× | 6.31× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.04` | Native C engine | 1.1727× | 1.1374–1.2250× | 0.21× | FASTER |
| holdout | `hold.large.ascii-mode.04` | Rust engine | 0.0925× | 0.0898–0.0964× | 0.96× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.05` | Python engine | 0.0208× | 0.0205–0.0211× | 6.44× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.05` | Native C engine | 1.1941× | 1.1746–1.2133× | 0.35× | FASTER |
| holdout | `hold.large.ascii-mode.05` | Rust engine | 0.0721× | 0.0708–0.0734× | 1.12× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.06` | Python engine | 0.0204× | 0.0203–0.0205× | 6.73× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.06` | Native C engine | 1.1989× | 1.1884–1.2083× | 0.50× | FASTER |
| holdout | `hold.large.ascii-mode.06` | Rust engine | 0.0495× | 0.0489–0.0500× | 1.33× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.07` | Python engine | 0.0203× | 0.0200–0.0206× | 7.04× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.07` | Native C engine | 1.1599× | 1.1043–1.2087× | 0.66× | FASTER |
| holdout | `hold.large.ascii-mode.07` | Rust engine | 0.0318× | 0.0315–0.0323× | 1.55× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.08` | Python engine | 0.0210× | 0.0209–0.0212× | 6.31× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.08` | Native C engine | 1.1542× | 1.1422–1.1644× | 0.21× | FASTER |
| holdout | `hold.large.ascii-mode.08` | Rust engine | 0.0912× | 0.0907–0.0917× | 0.96× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.09` | Python engine | 0.0215× | 0.0203–0.0239× | 6.44× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.09` | Native C engine | 1.0966× | 0.9666–1.1915× | 0.35× | — |
| holdout | `hold.large.ascii-mode.09` | Rust engine | 0.0734× | 0.0652–0.0838× | 1.12× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.10` | Python engine | 0.0204× | 0.0203–0.0205× | 6.73× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.10` | Native C engine | 1.1747× | 1.1378–1.1975× | 0.50× | FASTER |
| holdout | `hold.large.ascii-mode.10` | Rust engine | 0.0494× | 0.0488–0.0499× | 1.33× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.11` | Python engine | 0.0205× | 0.0204–0.0207× | 7.01× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.11` | Native C engine | 1.1984× | 1.1610–1.2223× | 0.66× | FASTER |
| holdout | `hold.large.ascii-mode.11` | Rust engine | 0.0306× | 0.0304–0.0308× | 1.59× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.12` | Python engine | 0.0210× | 0.0207–0.0213× | 6.31× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.12` | Native C engine | 1.1431× | 1.1313–1.1547× | 0.21× | FASTER |
| holdout | `hold.large.ascii-mode.12` | Rust engine | 0.0914× | 0.0897–0.0938× | 0.96× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.13` | Python engine | 0.0203× | 0.0202–0.0204× | 6.44× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.13` | Native C engine | 1.0679× | 0.9593–1.1493× | 0.35× | — |
| holdout | `hold.large.ascii-mode.13` | Rust engine | 0.0709× | 0.0702–0.0716× | 1.12× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.14` | Python engine | 0.0204× | 0.0203–0.0205× | 6.73× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.14` | Native C engine | 1.1959× | 1.1907–1.2006× | 0.50× | FASTER |
| holdout | `hold.large.ascii-mode.14` | Rust engine | 0.0497× | 0.0495–0.0499× | 1.33× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.15` | Python engine | 0.0203× | 0.0202–0.0204× | 7.04× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.15` | Native C engine | 1.2132× | 1.2057–1.2204× | 0.66× | FASTER |
| holdout | `hold.large.ascii-mode.15` | Rust engine | 0.0314× | 0.0312–0.0316× | 1.55× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.16` | Python engine | 0.0205× | 0.0192–0.0212× | 6.31× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.16` | Native C engine | 1.1404× | 1.1230–1.1554× | 0.21× | FASTER |
| holdout | `hold.large.ascii-mode.16` | Rust engine | 0.0924× | 0.0908–0.0946× | 0.96× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.17` | Python engine | 0.0200× | 0.0185–0.0209× | 6.42× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.17` | Native C engine | 1.1440× | 1.0665–1.1891× | 0.35× | FASTER |
| holdout | `hold.large.ascii-mode.17` | Rust engine | 0.0686× | 0.0651–0.0706× | 1.14× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.18` | Python engine | 0.0209× | 0.0208–0.0211× | 6.71× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.18` | Native C engine | 1.2054× | 1.1990–1.2137× | 0.50× | FASTER |
| holdout | `hold.large.ascii-mode.18` | Rust engine | 0.0486× | 0.0481–0.0491× | 1.36× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.19` | Python engine | 0.0207× | 0.0201–0.0215× | 7.04× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.19` | Native C engine | 1.2283× | 1.1754–1.2874× | 0.66× | FASTER |
| holdout | `hold.large.ascii-mode.19` | Rust engine | 0.0324× | 0.0315–0.0338× | 1.55× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.20` | Python engine | 0.0209× | 0.0208–0.0210× | 6.31× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.20` | Native C engine | 1.1474× | 1.1314–1.1613× | 0.21× | FASTER |
| holdout | `hold.large.ascii-mode.20` | Rust engine | 0.0906× | 0.0898–0.0915× | 0.96× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.21` | Python engine | 0.0207× | 0.0206–0.0209× | 6.42× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.21` | Native C engine | 1.1561× | 1.1177–1.1822× | 0.35× | FASTER |
| holdout | `hold.large.ascii-mode.21` | Rust engine | 0.0699× | 0.0693–0.0707× | 1.14× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.22` | Python engine | 0.0204× | 0.0200–0.0207× | 6.73× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.22` | Native C engine | 1.1907× | 1.1619–1.2160× | 0.50× | FASTER |
| holdout | `hold.large.ascii-mode.22` | Rust engine | 0.0495× | 0.0488–0.0503× | 1.33× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.23` | Python engine | 0.0206× | 0.0203–0.0213× | 7.04× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.23` | Native C engine | 1.2333× | 1.2101–1.2734× | 0.66× | FASTER |
| holdout | `hold.large.ascii-mode.23` | Rust engine | 0.0318× | 0.0311–0.0330× | 1.55× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.24` | Python engine | 0.0212× | 0.0206–0.0219× | 6.31× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.24` | Native C engine | 1.1514× | 1.1023–1.2041× | 0.21× | FASTER |
| holdout | `hold.large.ascii-mode.24` | Rust engine | 0.0917× | 0.0892–0.0949× | 0.96× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.25` | Python engine | 0.0207× | 0.0200–0.0215× | 6.44× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.25` | Native C engine | 1.2148× | 1.1840–1.2548× | 0.35× | FASTER |
| holdout | `hold.large.ascii-mode.25` | Rust engine | 0.0724× | 0.0710–0.0742× | 1.12× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.26` | Python engine | 0.0212× | 0.0204–0.0223× | 6.72× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.26` | Native C engine | 1.2372× | 1.1920–1.3028× | 0.50× | FASTER |
| holdout | `hold.large.ascii-mode.26` | Rust engine | 0.0506× | 0.0488–0.0532× | 1.35× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.27` | Python engine | 0.0207× | 0.0202–0.0214× | 7.03× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.27` | Native C engine | 1.2423× | 1.2112–1.2852× | 0.66× | FASTER |
| holdout | `hold.large.ascii-mode.27` | Rust engine | 0.0318× | 0.0311–0.0329× | 1.57× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.28` | Python engine | 0.0214× | 0.0205–0.0227× | 6.30× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.28` | Native C engine | 1.1677× | 1.1012–1.2494× | 0.21× | FASTER |
| holdout | `hold.large.ascii-mode.28` | Rust engine | 0.0911× | 0.0869–0.0952× | 0.96× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.29` | Python engine | 0.0209× | 0.0203–0.0215× | 6.42× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.29` | Native C engine | 1.1551× | 1.1110–1.1886× | 0.35× | FASTER |
| holdout | `hold.large.ascii-mode.29` | Rust engine | 0.0696× | 0.0689–0.0705× | 1.15× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.30` | Python engine | 0.0205× | 0.0204–0.0206× | 6.72× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.30` | Native C engine | 1.1882× | 1.1681–1.2022× | 0.50× | FASTER |
| holdout | `hold.large.ascii-mode.30` | Rust engine | 0.0488× | 0.0485–0.0491× | 1.35× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.31` | Python engine | 0.0212× | 0.0201–0.0231× | 7.03× | SLOWDOWN |
| holdout | `hold.large.ascii-mode.31` | Native C engine | 1.2709× | 1.2071–1.3741× | 0.66× | FASTER |
| holdout | `hold.large.ascii-mode.31` | Rust engine | 0.0326× | 0.0309–0.0354× | 1.57× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.00` | Python engine | 0.0164× | 0.0163–0.0167× | 5.51× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.00` | Native C engine | 1.5125× | 1.4938–1.5333× | 0.08× | FASTER |
| holdout | `hold.large.verbose-dotall.00` | Rust engine | 0.1300× | 0.1270–0.1327× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.01` | Python engine | 0.0075× | 0.0074–0.0075× | 14.89× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.01` | Native C engine | 3.1652× | 3.1460–3.1842× | 0.09× | FASTER |
| holdout | `hold.large.verbose-dotall.01` | Rust engine | 0.1056× | 0.1041–0.1068× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.02` | Python engine | 0.0138× | 0.0132–0.0150× | 5.56× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.02` | Native C engine | 1.9052× | 1.8142–2.0727× | 0.08× | FASTER |
| holdout | `hold.large.verbose-dotall.02` | Rust engine | 0.1631× | 0.1540–0.1793× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.03` | Python engine | 0.0080× | 0.0079–0.0081× | 14.89× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.03` | Native C engine | 2.8486× | 2.7705–2.9217× | 0.09× | FASTER |
| holdout | `hold.large.verbose-dotall.03` | Rust engine | 0.1150× | 0.1135–0.1166× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.04` | Python engine | 0.0154× | 0.0153–0.0156× | 5.51× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.04` | Native C engine | 1.4858× | 1.4737–1.4984× | 0.08× | FASTER |
| holdout | `hold.large.verbose-dotall.04` | Rust engine | 0.1310× | 0.1300–0.1320× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.05` | Python engine | 0.0075× | 0.0074–0.0076× | 14.89× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.05` | Native C engine | 3.1410× | 3.1069–3.1746× | 0.09× | FASTER |
| holdout | `hold.large.verbose-dotall.05` | Rust engine | 0.1101× | 0.1090–0.1111× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.06` | Python engine | 0.0131× | 0.0130–0.0132× | 5.56× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.06` | Native C engine | 1.7826× | 1.6673–1.8544× | 0.08× | FASTER |
| holdout | `hold.large.verbose-dotall.06` | Rust engine | 0.1553× | 0.1538–0.1565× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.07` | Python engine | 0.0080× | 0.0078–0.0081× | 14.89× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.07` | Native C engine | 2.8255× | 2.7461–2.8840× | 0.09× | FASTER |
| holdout | `hold.large.verbose-dotall.07` | Rust engine | 0.1100× | 0.1071–0.1127× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.08` | Python engine | 0.0157× | 0.0151–0.0169× | 5.51× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.08` | Native C engine | 1.5149× | 1.4532–1.6306× | 0.08× | FASTER |
| holdout | `hold.large.verbose-dotall.08` | Rust engine | 0.1325× | 0.1265–0.1427× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.09` | Python engine | 0.0075× | 0.0074–0.0078× | 14.89× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.09` | Native C engine | 3.2261× | 3.1718–3.3120× | 0.09× | FASTER |
| holdout | `hold.large.verbose-dotall.09` | Rust engine | 0.1099× | 0.1078–0.1130× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.10` | Python engine | 0.0133× | 0.0129–0.0141× | 5.56× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.10` | Native C engine | 1.8896× | 1.8123–2.0274× | 0.08× | FASTER |
| holdout | `hold.large.verbose-dotall.10` | Rust engine | 0.1600× | 0.1550–0.1699× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.11` | Python engine | 0.0086× | 0.0080–0.0100× | 14.89× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.11` | Native C engine | 2.9630× | 2.5180–3.5464× | 0.09× | FASTER |
| holdout | `hold.large.verbose-dotall.11` | Rust engine | 0.1205× | 0.1103–0.1401× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.12` | Python engine | 0.0152× | 0.0149–0.0155× | 5.51× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.12` | Native C engine | 1.4661× | 1.4487–1.4868× | 0.08× | FASTER |
| holdout | `hold.large.verbose-dotall.12` | Rust engine | 0.1274× | 0.1248–0.1296× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.13` | Python engine | 0.0075× | 0.0075–0.0076× | 14.89× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.13` | Native C engine | 3.1835× | 3.1273–3.2230× | 0.09× | FASTER |
| holdout | `hold.large.verbose-dotall.13` | Rust engine | 0.1070× | 0.1057–0.1082× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.14` | Python engine | 0.0129× | 0.0126–0.0131× | 5.56× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.14` | Native C engine | 1.8009× | 1.7673–1.8336× | 0.08× | FASTER |
| holdout | `hold.large.verbose-dotall.14` | Rust engine | 0.1491× | 0.1423–0.1554× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.15` | Python engine | 0.0085× | 0.0080–0.0095× | 14.89× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.15` | Native C engine | 3.0457× | 2.8918–3.2880× | 0.09× | FASTER |
| holdout | `hold.large.verbose-dotall.15` | Rust engine | 0.1164× | 0.1087–0.1305× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.16` | Python engine | 0.0156× | 0.0154–0.0157× | 5.51× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.16` | Native C engine | 1.4530× | 1.4295–1.4774× | 0.08× | FASTER |
| holdout | `hold.large.verbose-dotall.16` | Rust engine | 0.1279× | 0.1258–0.1297× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.17` | Python engine | 0.0075× | 0.0075–0.0076× | 14.89× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.17` | Native C engine | 3.1266× | 3.0863–3.1620× | 0.09× | FASTER |
| holdout | `hold.large.verbose-dotall.17` | Rust engine | 0.1066× | 0.1061–0.1070× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.18` | Python engine | 0.0129× | 0.0128–0.0130× | 5.56× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.18` | Native C engine | 1.8330× | 1.8163–1.8494× | 0.08× | FASTER |
| holdout | `hold.large.verbose-dotall.18` | Rust engine | 0.1523× | 0.1481–0.1551× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.19` | Python engine | 0.0084× | 0.0080–0.0091× | 14.89× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.19` | Native C engine | 2.6845× | 2.4094–2.9216× | 0.09× | FASTER |
| holdout | `hold.large.verbose-dotall.19` | Rust engine | 0.1137× | 0.1051–0.1256× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.20` | Python engine | 0.0159× | 0.0154–0.0168× | 5.51× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.20` | Native C engine | 1.5214× | 1.4707–1.6058× | 0.08× | FASTER |
| holdout | `hold.large.verbose-dotall.20` | Rust engine | 0.1339× | 0.1291–0.1421× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.21` | Python engine | 0.0075× | 0.0075–0.0075× | 14.89× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.21` | Native C engine | 3.1391× | 3.1089–3.1675× | 0.09× | FASTER |
| holdout | `hold.large.verbose-dotall.21` | Rust engine | 0.1049× | 0.1038–0.1059× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.22` | Python engine | 0.0131× | 0.0130–0.0132× | 5.56× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.22` | Native C engine | 1.8628× | 1.8388–1.8896× | 0.08× | FASTER |
| holdout | `hold.large.verbose-dotall.22` | Rust engine | 0.1555× | 0.1536–0.1581× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.23` | Python engine | 0.0081× | 0.0080–0.0082× | 14.89× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.23` | Native C engine | 2.6234× | 2.1616–2.9322× | 0.09× | FASTER |
| holdout | `hold.large.verbose-dotall.23` | Rust engine | 0.1138× | 0.1126–0.1152× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.24` | Python engine | 0.0152× | 0.0152–0.0153× | 5.51× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.24` | Native C engine | 1.4806× | 1.4672–1.4936× | 0.08× | FASTER |
| holdout | `hold.large.verbose-dotall.24` | Rust engine | 0.1285× | 0.1269–0.1299× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.25` | Python engine | 0.0076× | 0.0075–0.0079× | 14.89× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.25` | Native C engine | 3.2200× | 3.1503–3.3330× | 0.09× | FASTER |
| holdout | `hold.large.verbose-dotall.25` | Rust engine | 0.1081× | 0.1060–0.1117× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.26` | Python engine | 0.0129× | 0.0128–0.0130× | 5.56× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.26` | Native C engine | 1.8384× | 1.8130–1.8598× | 0.08× | FASTER |
| holdout | `hold.large.verbose-dotall.26` | Rust engine | 0.1549× | 0.1539–0.1559× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.27` | Python engine | 0.0082× | 0.0079–0.0087× | 14.89× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.27` | Native C engine | 2.9646× | 2.8575–3.1041× | 0.09× | FASTER |
| holdout | `hold.large.verbose-dotall.27` | Rust engine | 0.1122× | 0.1082–0.1184× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.28` | Python engine | 0.0156× | 0.0151–0.0162× | 5.51× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.28` | Native C engine | 1.5467× | 1.4743–1.6824× | 0.08× | FASTER |
| holdout | `hold.large.verbose-dotall.28` | Rust engine | 0.1359× | 0.1200–0.1547× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.29` | Python engine | 0.0076× | 0.0076–0.0076× | 14.89× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.29` | Native C engine | 3.1949× | 3.1705–3.2201× | 0.09× | FASTER |
| holdout | `hold.large.verbose-dotall.29` | Rust engine | 0.1052× | 0.1039–0.1063× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.30` | Python engine | 0.0131× | 0.0129–0.0133× | 5.56× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.30` | Native C engine | 1.8437× | 1.8202–1.8692× | 0.08× | FASTER |
| holdout | `hold.large.verbose-dotall.30` | Rust engine | 0.1561× | 0.1547–0.1582× | 0.06× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.31` | Python engine | 0.0082× | 0.0080–0.0084× | 14.89× | SLOWDOWN |
| holdout | `hold.large.verbose-dotall.31` | Native C engine | 2.9261× | 2.8696–2.9932× | 0.09× | FASTER |
| holdout | `hold.large.verbose-dotall.31` | Rust engine | 0.1120× | 0.1098–0.1147× | 0.06× | SLOWDOWN |
