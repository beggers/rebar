# Every large Zig slowdown

The final expanded holdout has **4** tasks below 0.8×. Every task is listed here with its measured range, median time, and the workload-specific reason; no result is omitted or reclassified.

## Causes by kind of task

- **large literal miss (1):** an absent phrase requires scanning every possible start. Observed range: 0.753–0.753×.
- **large scanner text (1):** incremental scanning creates many match results and boundary calls. Observed range: 0.799–0.799×.
- **real csv (1):** quoted-field lookahead requires repeated scans and backtracking. Observed range: 0.736–0.736×.
- **search hit (1):** very short successful searches are dominated by the Python/native call and match-object setup. Observed range: 0.759–0.759×.

## Every task

| Task | Kind of task | Speed | 95% range | Python re | Zig |
| --- | --- | ---: | ---: | ---: | ---: |
| `hold.large.literal-miss.28` | large literal miss | 0.753× | 0.409–1.088× | 142 ns | 154 ns |
| `hold.large.scanner-text.00` | large scanner text | 0.799× | 0.677–0.879× | 550 ns | 644 ns |
| `hold.real.csv` | real csv | 0.736× | 0.730–0.745× | 1518 ns | 2070 ns |
| `hold.search.literal.hit` | search hit | 0.759× | 0.727–0.781× | 145 ns | 188 ns |
