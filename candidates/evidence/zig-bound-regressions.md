# Every large Zig slowdown

The final expanded holdout has **93** tasks below 0.8×. Every task is listed here with its measured range, median time, and the workload-specific reason; no result is omitted or reclassified.

## Causes by kind of task

- **expanded match surface (48):** these generated inputs never match: a digit interrupts the leading text run before the dash, so the matcher retries the run at many starts; the result-building path is not reached. Observed range: 0.559–0.718×.
- **large verbose dotall (24):** verbose parsing or multi-line lazy matching adds compile/matcher work. Observed range: 0.706–0.767×.
- **expanded branch alternatives (15):** many alternatives require repeated branch checks; native counters confirm hundreds of direct matcher steps per call. Observed range: 0.579–0.783×.
- **large structured text (2):** configuration, paths, and quotes combine line starts, repeats, and captures. Observed range: 0.753–0.758×.
- **branch miss (1):** an absent choice requires checking many alternatives at every plausible start. Observed range: 0.473–0.473×.
- **look negative ahead (1):** negative lookahead and word-boundary checks repeat across the input. Observed range: 0.748–0.748×.
- **pattern verbose (1):** short verbose expressions expose capture and native-boundary setup. Observed range: 0.727–0.727×.
- **real csv (1):** quoted-field lookahead requires repeated scans and backtracking. Observed range: 0.688–0.688×.

## Every task

| Task | Kind of task | Speed | 95% range | Python re | Zig |
| --- | --- | ---: | ---: | ---: | ---: |
| `hold.branch.miss` | branch miss | 0.473× | 0.470–0.477× | 593 ns | 1265 ns |
| `hold.expanded.branch-alternatives.00` | expanded branch alternatives | 0.643× | 0.634–0.654× | 262 ns | 409 ns |
| `hold.expanded.branch-alternatives.06` | expanded branch alternatives | 0.692× | 0.683–0.700× | 271 ns | 394 ns |
| `hold.expanded.branch-alternatives.07` | expanded branch alternatives | 0.780× | 0.772–0.788× | 460 ns | 592 ns |
| `hold.expanded.branch-alternatives.12` | expanded branch alternatives | 0.579× | 0.549–0.602× | 360 ns | 603 ns |
| `hold.expanded.branch-alternatives.13` | expanded branch alternatives | 0.689× | 0.647–0.713× | 499 ns | 703 ns |
| `hold.expanded.branch-alternatives.18` | expanded branch alternatives | 0.722× | 0.713–0.731× | 268 ns | 371 ns |
| `hold.expanded.branch-alternatives.24` | expanded branch alternatives | 0.605× | 0.597–0.614× | 326 ns | 540 ns |
| `hold.expanded.branch-alternatives.25` | expanded branch alternatives | 0.748× | 0.743–0.754× | 468 ns | 625 ns |
| `hold.expanded.branch-alternatives.26` | expanded branch alternatives | 0.754× | 0.714–0.779× | 814 ns | 1054 ns |
| `hold.expanded.branch-alternatives.30` | expanded branch alternatives | 0.646× | 0.639–0.653× | 292 ns | 455 ns |
| `hold.expanded.branch-alternatives.31` | expanded branch alternatives | 0.783× | 0.759–0.828× | 463 ns | 607 ns |
| `hold.expanded.branch-alternatives.36` | expanded branch alternatives | 0.641× | 0.633–0.650× | 295 ns | 460 ns |
| `hold.expanded.branch-alternatives.42` | expanded branch alternatives | 0.649× | 0.625–0.667× | 283 ns | 428 ns |
| `hold.expanded.branch-alternatives.43` | expanded branch alternatives | 0.719× | 0.710–0.727× | 477 ns | 666 ns |
| `hold.expanded.branch-alternatives.44` | expanded branch alternatives | 0.764× | 0.762–0.766× | 1441 ns | 1884 ns |
| `hold.expanded.match-surface.00` | expanded match surface | 0.659× | 0.635–0.691× | 923 ns | 1411 ns |
| `hold.expanded.match-surface.01` | expanded match surface | 0.642× | 0.639–0.645× | 1184 ns | 1847 ns |
| `hold.expanded.match-surface.02` | expanded match surface | 0.718× | 0.650–0.838× | 937 ns | 1435 ns |
| `hold.expanded.match-surface.03` | expanded match surface | 0.645× | 0.641–0.650× | 1205 ns | 1872 ns |
| `hold.expanded.match-surface.04` | expanded match surface | 0.651× | 0.636–0.668× | 980 ns | 1513 ns |
| `hold.expanded.match-surface.05` | expanded match surface | 0.654× | 0.637–0.676× | 1300 ns | 2006 ns |
| `hold.expanded.match-surface.06` | expanded match surface | 0.661× | 0.629–0.705× | 922 ns | 1412 ns |
| `hold.expanded.match-surface.07` | expanded match surface | 0.635× | 0.622–0.644× | 1185 ns | 1846 ns |
| `hold.expanded.match-surface.08` | expanded match surface | 0.695× | 0.605–0.843× | 939 ns | 1432 ns |
| `hold.expanded.match-surface.09` | expanded match surface | 0.667× | 0.639–0.722× | 1205 ns | 1882 ns |
| `hold.expanded.match-surface.10` | expanded match surface | 0.660× | 0.654–0.666× | 991 ns | 1511 ns |
| `hold.expanded.match-surface.11` | expanded match surface | 0.646× | 0.633–0.658× | 1304 ns | 2016 ns |
| `hold.expanded.match-surface.12` | expanded match surface | 0.668× | 0.662–0.678× | 934 ns | 1412 ns |
| `hold.expanded.match-surface.13` | expanded match surface | 0.648× | 0.645–0.650× | 1197 ns | 1851 ns |
| `hold.expanded.match-surface.14` | expanded match surface | 0.661× | 0.657–0.665× | 949 ns | 1432 ns |
| `hold.expanded.match-surface.15` | expanded match surface | 0.696× | 0.644–0.808× | 1219 ns | 1887 ns |
| `hold.expanded.match-surface.16` | expanded match surface | 0.652× | 0.647–0.657× | 991 ns | 1532 ns |
| `hold.expanded.match-surface.17` | expanded match surface | 0.655× | 0.650–0.661× | 1330 ns | 2036 ns |
| `hold.expanded.match-surface.18` | expanded match surface | 0.662× | 0.636–0.696× | 1014 ns | 1538 ns |
| `hold.expanded.match-surface.19` | expanded match surface | 0.661× | 0.650–0.680× | 1207 ns | 1853 ns |
| `hold.expanded.match-surface.20` | expanded match surface | 0.685× | 0.664–0.720× | 959 ns | 1427 ns |
| `hold.expanded.match-surface.21` | expanded match surface | 0.653× | 0.648–0.657× | 1229 ns | 1880 ns |
| `hold.expanded.match-surface.22` | expanded match surface | 0.679× | 0.665–0.699× | 998 ns | 1502 ns |
| `hold.expanded.match-surface.23` | expanded match surface | 0.655× | 0.646–0.664× | 1397 ns | 2118 ns |
| `hold.expanded.match-surface.24` | expanded match surface | 0.650× | 0.617–0.670× | 945 ns | 1412 ns |
| `hold.expanded.match-surface.25` | expanded match surface | 0.653× | 0.649–0.657× | 1207 ns | 1852 ns |
| `hold.expanded.match-surface.26` | expanded match surface | 0.674× | 0.653–0.697× | 966 ns | 1436 ns |
| `hold.expanded.match-surface.27` | expanded match surface | 0.654× | 0.650–0.658× | 1227 ns | 1884 ns |
| `hold.expanded.match-surface.28` | expanded match surface | 0.668× | 0.659–0.677× | 1000 ns | 1497 ns |
| `hold.expanded.match-surface.29` | expanded match surface | 0.648× | 0.635–0.660× | 1322 ns | 2050 ns |
| `hold.expanded.match-surface.30` | expanded match surface | 0.655× | 0.637–0.666× | 1019 ns | 1539 ns |
| `hold.expanded.match-surface.31` | expanded match surface | 0.637× | 0.608–0.653× | 1207 ns | 1853 ns |
| `hold.expanded.match-surface.32` | expanded match surface | 0.666× | 0.660–0.673× | 961 ns | 1433 ns |
| `hold.expanded.match-surface.33` | expanded match surface | 0.657× | 0.651–0.664× | 1227 ns | 1883 ns |
| `hold.expanded.match-surface.34` | expanded match surface | 0.663× | 0.655–0.672× | 1074 ns | 1632 ns |
| `hold.expanded.match-surface.35` | expanded match surface | 0.673× | 0.662–0.687× | 1344 ns | 2000 ns |
| `hold.expanded.match-surface.36` | expanded match surface | 0.718× | 0.678–0.777× | 969 ns | 1411 ns |
| `hold.expanded.match-surface.37` | expanded match surface | 0.651× | 0.641–0.660× | 1292 ns | 1976 ns |
| `hold.expanded.match-surface.38` | expanded match surface | 0.698× | 0.670–0.738× | 982 ns | 1437 ns |
| `hold.expanded.match-surface.39` | expanded match surface | 0.684× | 0.659–0.729× | 1248 ns | 1878 ns |
| `hold.expanded.match-surface.40` | expanded match surface | 0.679× | 0.668–0.688× | 1018 ns | 1490 ns |
| `hold.expanded.match-surface.41` | expanded match surface | 0.680× | 0.662–0.699× | 1357 ns | 2010 ns |
| `hold.expanded.match-surface.42` | expanded match surface | 0.672× | 0.649–0.704× | 960 ns | 1418 ns |
| `hold.expanded.match-surface.43` | expanded match surface | 0.680× | 0.655–0.730× | 1292 ns | 1975 ns |
| `hold.expanded.match-surface.44` | expanded match surface | 0.660× | 0.619–0.686× | 976 ns | 1437 ns |
| `hold.expanded.match-surface.45` | expanded match surface | 0.645× | 0.607–0.669× | 1242 ns | 1885 ns |
| `hold.expanded.match-surface.46` | expanded match surface | 0.559× | 0.396–0.685× | 1013 ns | 1501 ns |
| `hold.expanded.match-surface.47` | expanded match surface | 0.648× | 0.566–0.708× | 1362 ns | 2036 ns |
| `hold.large.structured-text.11` | large structured text | 0.753× | 0.745–0.758× | 4420 ns | 5855 ns |
| `hold.large.structured-text.23` | large structured text | 0.758× | 0.753–0.761× | 4456 ns | 5866 ns |
| `hold.large.verbose-dotall.01` | large verbose dotall | 0.754× | 0.727–0.808× | 719 ns | 983 ns |
| `hold.large.verbose-dotall.02` | large verbose dotall | 0.706× | 0.647–0.742× | 889 ns | 1210 ns |
| `hold.large.verbose-dotall.03` | large verbose dotall | 0.739× | 0.734–0.747× | 748 ns | 1017 ns |
| `hold.large.verbose-dotall.05` | large verbose dotall | 0.717× | 0.694–0.732× | 718 ns | 985 ns |
| `hold.large.verbose-dotall.06` | large verbose dotall | 0.735× | 0.731–0.739× | 928 ns | 1266 ns |
| `hold.large.verbose-dotall.07` | large verbose dotall | 0.731× | 0.723–0.737× | 750 ns | 1019 ns |
| `hold.large.verbose-dotall.09` | large verbose dotall | 0.733× | 0.731–0.735× | 718 ns | 981 ns |
| `hold.large.verbose-dotall.10` | large verbose dotall | 0.737× | 0.732–0.744× | 927 ns | 1266 ns |
| `hold.large.verbose-dotall.11` | large verbose dotall | 0.741× | 0.735–0.748× | 749 ns | 1014 ns |
| `hold.large.verbose-dotall.13` | large verbose dotall | 0.723× | 0.708–0.732× | 719 ns | 983 ns |
| `hold.large.verbose-dotall.14` | large verbose dotall | 0.767× | 0.733–0.833× | 938 ns | 1268 ns |
| `hold.large.verbose-dotall.15` | large verbose dotall | 0.737× | 0.732–0.741× | 747 ns | 1016 ns |
| `hold.large.verbose-dotall.17` | large verbose dotall | 0.717× | 0.694–0.732× | 720 ns | 983 ns |
| `hold.large.verbose-dotall.18` | large verbose dotall | 0.741× | 0.736–0.747× | 929 ns | 1256 ns |
| `hold.large.verbose-dotall.19` | large verbose dotall | 0.732× | 0.723–0.739× | 750 ns | 1019 ns |
| `hold.large.verbose-dotall.21` | large verbose dotall | 0.711× | 0.661–0.740× | 722 ns | 982 ns |
| `hold.large.verbose-dotall.22` | large verbose dotall | 0.738× | 0.728–0.746× | 930 ns | 1255 ns |
| `hold.large.verbose-dotall.23` | large verbose dotall | 0.738× | 0.734–0.744× | 749 ns | 1016 ns |
| `hold.large.verbose-dotall.25` | large verbose dotall | 0.732× | 0.725–0.743× | 719 ns | 985 ns |
| `hold.large.verbose-dotall.26` | large verbose dotall | 0.734× | 0.728–0.740× | 970 ns | 1320 ns |
| `hold.large.verbose-dotall.27` | large verbose dotall | 0.735× | 0.730–0.740× | 747 ns | 1017 ns |
| `hold.large.verbose-dotall.29` | large verbose dotall | 0.734× | 0.731–0.738× | 723 ns | 985 ns |
| `hold.large.verbose-dotall.30` | large verbose dotall | 0.711× | 0.659–0.740× | 973 ns | 1326 ns |
| `hold.large.verbose-dotall.31` | large verbose dotall | 0.728× | 0.718–0.737× | 748 ns | 1022 ns |
| `hold.look.negative-ahead` | look negative ahead | 0.748× | 0.744–0.753× | 717 ns | 959 ns |
| `hold.pattern.verbose` | pattern verbose | 0.727× | 0.725–0.730× | 729 ns | 1001 ns |
| `hold.real.csv` | real csv | 0.688× | 0.683–0.693× | 1537 ns | 2241 ns |
