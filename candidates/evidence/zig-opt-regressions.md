# Every large Zig slowdown

The final expanded holdout has **259** tasks below 0.8×. Every task is listed here with its measured range, median time, and the workload-specific reason; no result is omitted or reclassified.

## Causes by kind of task

- **expanded match surface (48):** group access, dictionaries, spans, and expansion expose match-object construction cost. Observed range: 0.602–0.707×.
- **large references (32):** backreferences require capture restoration and comparison. Observed range: 0.675–0.791×.
- **large verbose dotall (32):** verbose parsing or multi-line lazy matching adds compile/matcher work. Observed range: 0.620–0.746×.
- **large literal hit (21):** short calls make matcher setup and Python/native boundary cost visible. Observed range: 0.638–0.796×.
- **expanded branch alternatives (16):** many alternatives require repeated branch checks; native counters confirm hundreds of direct matcher steps per call. Observed range: 0.538–0.780×.
- **large literal miss (15):** an absent phrase requires scanning every possible start. Observed range: 0.646–0.781×.
- **expanded long literal (11):** long present/absent scans expose literal-start filtering and boundary cost; native counters confirm the direct path does no bytecode steps, so remaining losses are call and scan overhead. Observed range: 0.691–0.796×.
- **large scanner bytes (10):** byte scanning and result construction amplify native-boundary work. Observed range: 0.664–0.799×.
- **large structured text (10):** configuration, paths, and quotes combine line starts, repeats, and captures. Observed range: 0.700–0.799×.
- **large scanner text (9):** incremental scanning creates many match results and boundary calls. Observed range: 0.651–0.788×.
- **expanded backreference (8):** capture restoration and repeated captured-text comparison amplify matching work. Observed range: 0.710–0.770×.
- **expanded comment strip (8):** line and block comments combine repeated scans, lazy matching, and replacement joining. Observed range: 0.606–0.660×.
- **expanded email extract (8):** email-like collection repeatedly checks character classes and constructs many results. Observed range: 0.659–0.761×.
- **expanded newline normalize (7):** many short newline matches and replacements amplify per-result and join overhead. Observed range: 0.760–0.790×.
- **expanded ip version (6):** large alternatives and bounded repeats add branch and character-check work. Observed range: 0.754–0.794×.
- **expanded phone postcode (2):** several structured alternatives require repeated branch and character checks. Observed range: 0.785–0.797×.
- **expanded replace template (2):** capture lookup, template expansion, and joining dominate replacement. Observed range: 0.697–0.781×.
- **block dotall (1):** lazy multi-line matching repeatedly retries the closing text. Observed range: 0.736–0.736×.
- **branch miss (1):** an absent choice requires checking many alternatives at every plausible start. Observed range: 0.451–0.451×.
- **branch prefix (1):** controlled alternatives add branch and state work to a short search. Observed range: 0.783–0.783×.
- **empty (1):** many empty results require safe progress and repeated iterator/result construction. Observed range: 0.765–0.765×.
- **expanded scanner (1):** incremental text/byte scanning creates many results and repeatedly crosses the native boundary. Observed range: 0.799–0.799×.
- **large conditionals (1):** optional delimiters depend on capture state and branch selection for every result. Observed range: 0.722–0.722×.
- **literal replace (1):** a very short replacement is dominated by argument handling and result construction. Observed range: 0.625–0.625×.
- **look negative ahead (1):** negative lookahead and word-boundary checks repeat across the input. Observed range: 0.739–0.739×.
- **match miss (1):** very short anchored misses are dominated by call/setup cost. Observed range: 0.797–0.797×.
- **pattern verbose (1):** short verbose expressions expose capture and native-boundary setup. Observed range: 0.692–0.692×.
- **real csv (1):** quoted-field lookahead requires repeated scans and backtracking. Observed range: 0.625–0.625×.
- **real email (1):** several repeated character classes and returned values amplify collection work. Observed range: 0.748–0.748×.
- **search hit (1):** very short successful searches are dominated by the Python/native call and match-object setup. Observed range: 0.654–0.654×.
- **search miss (1):** very short misses still pay the Python/native call cost. Observed range: 0.665–0.665×.

## Every task

| Task | Kind of task | Speed | 95% range | Python re | Zig |
| --- | --- | ---: | ---: | ---: | ---: |
| `hold.block.dotall` | block dotall | 0.736× | 0.723–0.755× | 426 ns | 585 ns |
| `hold.branch.miss` | branch miss | 0.451× | 0.437–0.462× | 617 ns | 1326 ns |
| `hold.branch.prefix` | branch prefix | 0.783× | 0.777–0.788× | 231 ns | 294 ns |
| `hold.empty.finditer` | empty | 0.765× | 0.749–0.775× | 1330 ns | 1732 ns |
| `hold.expanded.backreference.00` | expanded backreference | 0.726× | 0.719–0.732× | 329 ns | 452 ns |
| `hold.expanded.backreference.06` | expanded backreference | 0.745× | 0.708–0.822× | 331 ns | 465 ns |
| `hold.expanded.backreference.12` | expanded backreference | 0.711× | 0.692–0.724× | 332 ns | 462 ns |
| `hold.expanded.backreference.18` | expanded backreference | 0.726× | 0.723–0.730× | 331 ns | 455 ns |
| `hold.expanded.backreference.24` | expanded backreference | 0.710× | 0.685–0.726× | 341 ns | 471 ns |
| `hold.expanded.backreference.30` | expanded backreference | 0.762× | 0.752–0.774× | 348 ns | 458 ns |
| `hold.expanded.backreference.36` | expanded backreference | 0.765× | 0.760–0.771× | 350 ns | 456 ns |
| `hold.expanded.backreference.42` | expanded backreference | 0.770× | 0.736–0.826× | 340 ns | 457 ns |
| `hold.expanded.branch-alternatives.00` | expanded branch alternatives | 0.574× | 0.551–0.614× | 263 ns | 471 ns |
| `hold.expanded.branch-alternatives.06` | expanded branch alternatives | 0.637× | 0.615–0.674× | 282 ns | 453 ns |
| `hold.expanded.branch-alternatives.07` | expanded branch alternatives | 0.740× | 0.723–0.764× | 474 ns | 653 ns |
| `hold.expanded.branch-alternatives.12` | expanded branch alternatives | 0.545× | 0.542–0.547× | 358 ns | 657 ns |
| `hold.expanded.branch-alternatives.13` | expanded branch alternatives | 0.681× | 0.657–0.727× | 497 ns | 753 ns |
| `hold.expanded.branch-alternatives.18` | expanded branch alternatives | 0.635× | 0.632–0.638× | 276 ns | 434 ns |
| `hold.expanded.branch-alternatives.24` | expanded branch alternatives | 0.538× | 0.534–0.541× | 330 ns | 614 ns |
| `hold.expanded.branch-alternatives.25` | expanded branch alternatives | 0.700× | 0.695–0.704× | 481 ns | 687 ns |
| `hold.expanded.branch-alternatives.26` | expanded branch alternatives | 0.748× | 0.732–0.761× | 835 ns | 1110 ns |
| `hold.expanded.branch-alternatives.30` | expanded branch alternatives | 0.624× | 0.572–0.739× | 295 ns | 514 ns |
| `hold.expanded.branch-alternatives.31` | expanded branch alternatives | 0.699× | 0.689–0.714× | 470 ns | 679 ns |
| `hold.expanded.branch-alternatives.36` | expanded branch alternatives | 0.617× | 0.567–0.696× | 299 ns | 523 ns |
| `hold.expanded.branch-alternatives.37` | expanded branch alternatives | 0.780× | 0.768–0.792× | 485 ns | 621 ns |
| `hold.expanded.branch-alternatives.42` | expanded branch alternatives | 0.576× | 0.552–0.594× | 282 ns | 484 ns |
| `hold.expanded.branch-alternatives.43` | expanded branch alternatives | 0.678× | 0.673–0.683× | 493 ns | 728 ns |
| `hold.expanded.branch-alternatives.44` | expanded branch alternatives | 0.753× | 0.730–0.795× | 1449 ns | 1975 ns |
| `hold.expanded.comment-strip.00` | expanded comment strip | 0.606× | 0.583–0.622× | 589 ns | 963 ns |
| `hold.expanded.comment-strip.06` | expanded comment strip | 0.629× | 0.616–0.640× | 608 ns | 958 ns |
| `hold.expanded.comment-strip.12` | expanded comment strip | 0.646× | 0.624–0.668× | 610 ns | 946 ns |
| `hold.expanded.comment-strip.18` | expanded comment strip | 0.660× | 0.631–0.715× | 599 ns | 944 ns |
| `hold.expanded.comment-strip.24` | expanded comment strip | 0.626× | 0.619–0.632× | 613 ns | 970 ns |
| `hold.expanded.comment-strip.30` | expanded comment strip | 0.637× | 0.621–0.650× | 632 ns | 983 ns |
| `hold.expanded.comment-strip.36` | expanded comment strip | 0.641× | 0.635–0.648× | 621 ns | 970 ns |
| `hold.expanded.comment-strip.42` | expanded comment strip | 0.637× | 0.626–0.646× | 620 ns | 964 ns |
| `hold.expanded.email-extract.00` | expanded email extract | 0.713× | 0.705–0.720× | 343 ns | 479 ns |
| `hold.expanded.email-extract.06` | expanded email extract | 0.709× | 0.705–0.712× | 338 ns | 475 ns |
| `hold.expanded.email-extract.12` | expanded email extract | 0.740× | 0.734–0.747× | 351 ns | 475 ns |
| `hold.expanded.email-extract.18` | expanded email extract | 0.707× | 0.703–0.713× | 338 ns | 479 ns |
| `hold.expanded.email-extract.24` | expanded email extract | 0.659× | 0.573–0.709× | 337 ns | 480 ns |
| `hold.expanded.email-extract.30` | expanded email extract | 0.701× | 0.667–0.721× | 340 ns | 475 ns |
| `hold.expanded.email-extract.36` | expanded email extract | 0.744× | 0.731–0.761× | 348 ns | 473 ns |
| `hold.expanded.email-extract.42` | expanded email extract | 0.761× | 0.703–0.885× | 336 ns | 477 ns |
| `hold.expanded.ip-version.00` | expanded ip version | 0.794× | 0.764–0.813× | 332 ns | 413 ns |
| `hold.expanded.ip-version.06` | expanded ip version | 0.759× | 0.755–0.762× | 346 ns | 457 ns |
| `hold.expanded.ip-version.12` | expanded ip version | 0.761× | 0.755–0.765× | 343 ns | 450 ns |
| `hold.expanded.ip-version.18` | expanded ip version | 0.778× | 0.771–0.785× | 354 ns | 453 ns |
| `hold.expanded.ip-version.36` | expanded ip version | 0.759× | 0.753–0.765× | 349 ns | 459 ns |
| `hold.expanded.ip-version.42` | expanded ip version | 0.754× | 0.713–0.779× | 352 ns | 453 ns |
| `hold.expanded.long-literal.00` | expanded long literal | 0.711× | 0.693–0.725× | 143 ns | 197 ns |
| `hold.expanded.long-literal.01` | expanded long literal | 0.750× | 0.740–0.759× | 177 ns | 235 ns |
| `hold.expanded.long-literal.02` | expanded long literal | 0.740× | 0.715–0.758× | 177 ns | 235 ns |
| `hold.expanded.long-literal.03` | expanded long literal | 0.691× | 0.637–0.724× | 144 ns | 199 ns |
| `hold.expanded.long-literal.04` | expanded long literal | 0.720× | 0.673–0.754× | 177 ns | 237 ns |
| `hold.expanded.long-literal.36` | expanded long literal | 0.745× | 0.724–0.785× | 144 ns | 198 ns |
| `hold.expanded.long-literal.37` | expanded long literal | 0.742× | 0.739–0.746× | 178 ns | 239 ns |
| `hold.expanded.long-literal.38` | expanded long literal | 0.728× | 0.684–0.755× | 178 ns | 236 ns |
| `hold.expanded.long-literal.39` | expanded long literal | 0.725× | 0.721–0.730× | 144 ns | 198 ns |
| `hold.expanded.long-literal.40` | expanded long literal | 0.796× | 0.777–0.825× | 178 ns | 228 ns |
| `hold.expanded.long-literal.41` | expanded long literal | 0.776× | 0.729–0.803× | 178 ns | 223 ns |
| `hold.expanded.match-surface.00` | expanded match surface | 0.634× | 0.621–0.644× | 919 ns | 1440 ns |
| `hold.expanded.match-surface.01` | expanded match surface | 0.627× | 0.624–0.630× | 1180 ns | 1879 ns |
| `hold.expanded.match-surface.02` | expanded match surface | 0.640× | 0.635–0.644× | 935 ns | 1457 ns |
| `hold.expanded.match-surface.03` | expanded match surface | 0.633× | 0.628–0.639× | 1202 ns | 1902 ns |
| `hold.expanded.match-surface.04` | expanded match surface | 0.602× | 0.532–0.657× | 997 ns | 1529 ns |
| `hold.expanded.match-surface.05` | expanded match surface | 0.653× | 0.644–0.665× | 1320 ns | 2030 ns |
| `hold.expanded.match-surface.06` | expanded match surface | 0.633× | 0.624–0.639× | 917 ns | 1441 ns |
| `hold.expanded.match-surface.07` | expanded match surface | 0.638× | 0.577–0.722× | 1183 ns | 1876 ns |
| `hold.expanded.match-surface.08` | expanded match surface | 0.664× | 0.641–0.708× | 939 ns | 1457 ns |
| `hold.expanded.match-surface.09` | expanded match surface | 0.632× | 0.627–0.637× | 1203 ns | 1901 ns |
| `hold.expanded.match-surface.10` | expanded match surface | 0.707× | 0.644–0.838× | 985 ns | 1508 ns |
| `hold.expanded.match-surface.11` | expanded match surface | 0.648× | 0.637–0.659× | 1304 ns | 2028 ns |
| `hold.expanded.match-surface.12` | expanded match surface | 0.646× | 0.644–0.648× | 932 ns | 1441 ns |
| `hold.expanded.match-surface.13` | expanded match surface | 0.632× | 0.630–0.634× | 1192 ns | 1883 ns |
| `hold.expanded.match-surface.14` | expanded match surface | 0.645× | 0.640–0.650× | 939 ns | 1460 ns |
| `hold.expanded.match-surface.15` | expanded match surface | 0.618× | 0.575–0.643× | 1216 ns | 1905 ns |
| `hold.expanded.match-surface.16` | expanded match surface | 0.649× | 0.637–0.661× | 986 ns | 1516 ns |
| `hold.expanded.match-surface.17` | expanded match surface | 0.635× | 0.608–0.652× | 1324 ns | 2030 ns |
| `hold.expanded.match-surface.18` | expanded match surface | 0.643× | 0.632–0.653× | 1010 ns | 1566 ns |
| `hold.expanded.match-surface.19` | expanded match surface | 0.637× | 0.631–0.642× | 1201 ns | 1880 ns |
| `hold.expanded.match-surface.20` | expanded match surface | 0.654× | 0.648–0.659× | 958 ns | 1460 ns |
| `hold.expanded.match-surface.21` | expanded match surface | 0.644× | 0.638–0.650× | 1231 ns | 1904 ns |
| `hold.expanded.match-surface.22` | expanded match surface | 0.661× | 0.654–0.668× | 1006 ns | 1514 ns |
| `hold.expanded.match-surface.23` | expanded match surface | 0.652× | 0.622–0.681× | 1405 ns | 2148 ns |
| `hold.expanded.match-surface.24` | expanded match surface | 0.652× | 0.648–0.655× | 940 ns | 1441 ns |
| `hold.expanded.match-surface.25` | expanded match surface | 0.636× | 0.626–0.642× | 1204 ns | 1880 ns |
| `hold.expanded.match-surface.26` | expanded match surface | 0.654× | 0.651–0.658× | 954 ns | 1458 ns |
| `hold.expanded.match-surface.27` | expanded match surface | 0.645× | 0.641–0.649× | 1227 ns | 1903 ns |
| `hold.expanded.match-surface.28` | expanded match surface | 0.661× | 0.650–0.675× | 995 ns | 1513 ns |
| `hold.expanded.match-surface.29` | expanded match surface | 0.657× | 0.648–0.667× | 1327 ns | 2033 ns |
| `hold.expanded.match-surface.30` | expanded match surface | 0.634× | 0.621–0.644× | 1009 ns | 1566 ns |
| `hold.expanded.match-surface.31` | expanded match surface | 0.651× | 0.637–0.679× | 1204 ns | 1879 ns |
| `hold.expanded.match-surface.32` | expanded match surface | 0.607× | 0.520–0.658× | 956 ns | 1463 ns |
| `hold.expanded.match-surface.33` | expanded match surface | 0.645× | 0.640–0.649× | 1230 ns | 1905 ns |
| `hold.expanded.match-surface.34` | expanded match surface | 0.658× | 0.652–0.665× | 1077 ns | 1644 ns |
| `hold.expanded.match-surface.35` | expanded match surface | 0.661× | 0.650–0.678× | 1327 ns | 2023 ns |
| `hold.expanded.match-surface.36` | expanded match surface | 0.670× | 0.653–0.694× | 941 ns | 1444 ns |
| `hold.expanded.match-surface.37` | expanded match surface | 0.616× | 0.582–0.636× | 1271 ns | 2006 ns |
| `hold.expanded.match-surface.38` | expanded match surface | 0.657× | 0.651–0.663× | 960 ns | 1461 ns |
| `hold.expanded.match-surface.39` | expanded match surface | 0.644× | 0.639–0.649× | 1221 ns | 1899 ns |
| `hold.expanded.match-surface.40` | expanded match surface | 0.667× | 0.659–0.675× | 1009 ns | 1507 ns |
| `hold.expanded.match-surface.41` | expanded match surface | 0.657× | 0.645–0.670× | 1327 ns | 2030 ns |
| `hold.expanded.match-surface.42` | expanded match surface | 0.649× | 0.642–0.654× | 940 ns | 1440 ns |
| `hold.expanded.match-surface.43` | expanded match surface | 0.647× | 0.633–0.666× | 1270 ns | 2006 ns |
| `hold.expanded.match-surface.44` | expanded match surface | 0.653× | 0.649–0.656× | 954 ns | 1459 ns |
| `hold.expanded.match-surface.45` | expanded match surface | 0.642× | 0.634–0.649× | 1222 ns | 1902 ns |
| `hold.expanded.match-surface.46` | expanded match surface | 0.665× | 0.649–0.682× | 997 ns | 1506 ns |
| `hold.expanded.match-surface.47` | expanded match surface | 0.646× | 0.633–0.660× | 1332 ns | 2036 ns |
| `hold.expanded.newline-normalize.00` | expanded newline normalize | 0.760× | 0.754–0.767× | 611 ns | 804 ns |
| `hold.expanded.newline-normalize.06` | expanded newline normalize | 0.771× | 0.743–0.791× | 633 ns | 805 ns |
| `hold.expanded.newline-normalize.12` | expanded newline normalize | 0.784× | 0.760–0.813× | 632 ns | 809 ns |
| `hold.expanded.newline-normalize.18` | expanded newline normalize | 0.768× | 0.760–0.774× | 613 ns | 796 ns |
| `hold.expanded.newline-normalize.30` | expanded newline normalize | 0.780× | 0.762–0.791× | 628 ns | 800 ns |
| `hold.expanded.newline-normalize.36` | expanded newline normalize | 0.781× | 0.777–0.786× | 627 ns | 804 ns |
| `hold.expanded.newline-normalize.42` | expanded newline normalize | 0.790× | 0.783–0.799× | 634 ns | 804 ns |
| `hold.expanded.phone-postcode.18` | expanded phone postcode | 0.797× | 0.717–0.844× | 318 ns | 379 ns |
| `hold.expanded.phone-postcode.30` | expanded phone postcode | 0.785× | 0.685–0.851× | 319 ns | 379 ns |
| `hold.expanded.replace-template.12` | expanded replace template | 0.697× | 0.494–0.833× | 736 ns | 895 ns |
| `hold.expanded.replace-template.18` | expanded replace template | 0.781× | 0.725–0.821× | 734 ns | 900 ns |
| `hold.expanded.scanner.18` | expanded scanner | 0.799× | 0.725–0.889× | 963 ns | 1128 ns |
| `hold.large.conditionals.30` | large conditionals | 0.722× | 0.617–0.848× | 228 ns | 380 ns |
| `hold.large.literal-hit.00` | large literal hit | 0.681× | 0.674–0.687× | 154 ns | 225 ns |
| `hold.large.literal-hit.01` | large literal hit | 0.739× | 0.733–0.746× | 166 ns | 226 ns |
| `hold.large.literal-hit.02` | large literal hit | 0.747× | 0.674–0.792× | 188 ns | 239 ns |
| `hold.large.literal-hit.04` | large literal hit | 0.712× | 0.704–0.720× | 156 ns | 220 ns |
| `hold.large.literal-hit.05` | large literal hit | 0.738× | 0.728–0.748× | 170 ns | 228 ns |
| `hold.large.literal-hit.06` | large literal hit | 0.792× | 0.785–0.799× | 188 ns | 236 ns |
| `hold.large.literal-hit.08` | large literal hit | 0.700× | 0.695–0.706× | 155 ns | 221 ns |
| `hold.large.literal-hit.09` | large literal hit | 0.741× | 0.733–0.748× | 165 ns | 222 ns |
| `hold.large.literal-hit.10` | large literal hit | 0.792× | 0.709–0.897× | 189 ns | 236 ns |
| `hold.large.literal-hit.12` | large literal hit | 0.638× | 0.522–0.709× | 156 ns | 221 ns |
| `hold.large.literal-hit.13` | large literal hit | 0.738× | 0.730–0.746× | 167 ns | 226 ns |
| `hold.large.literal-hit.14` | large literal hit | 0.796× | 0.790–0.802× | 189 ns | 239 ns |
| `hold.large.literal-hit.16` | large literal hit | 0.688× | 0.682–0.694× | 154 ns | 224 ns |
| `hold.large.literal-hit.17` | large literal hit | 0.766× | 0.648–0.937× | 166 ns | 226 ns |
| `hold.large.literal-hit.20` | large literal hit | 0.737× | 0.644–0.854× | 156 ns | 222 ns |
| `hold.large.literal-hit.21` | large literal hit | 0.731× | 0.727–0.735× | 166 ns | 226 ns |
| `hold.large.literal-hit.24` | large literal hit | 0.685× | 0.631–0.728× | 156 ns | 222 ns |
| `hold.large.literal-hit.25` | large literal hit | 0.753× | 0.748–0.757× | 170 ns | 226 ns |
| `hold.large.literal-hit.28` | large literal hit | 0.712× | 0.707–0.718× | 159 ns | 222 ns |
| `hold.large.literal-hit.29` | large literal hit | 0.771× | 0.735–0.839× | 169 ns | 227 ns |
| `hold.large.literal-hit.30` | large literal hit | 0.791× | 0.783–0.799× | 189 ns | 239 ns |
| `hold.large.literal-miss.00` | large literal miss | 0.683× | 0.671–0.694× | 135 ns | 198 ns |
| `hold.large.literal-miss.01` | large literal miss | 0.781× | 0.775–0.786× | 158 ns | 202 ns |
| `hold.large.literal-miss.04` | large literal miss | 0.710× | 0.704–0.716× | 140 ns | 196 ns |
| `hold.large.literal-miss.05` | large literal miss | 0.766× | 0.718–0.795× | 159 ns | 201 ns |
| `hold.large.literal-miss.08` | large literal miss | 0.679× | 0.620–0.720× | 140 ns | 198 ns |
| `hold.large.literal-miss.09` | large literal miss | 0.781× | 0.773–0.789× | 161 ns | 207 ns |
| `hold.large.literal-miss.12` | large literal miss | 0.693× | 0.687–0.698× | 138 ns | 199 ns |
| `hold.large.literal-miss.13` | large literal miss | 0.693× | 0.590–0.771× | 160 ns | 211 ns |
| `hold.large.literal-miss.16` | large literal miss | 0.716× | 0.706–0.730× | 141 ns | 198 ns |
| `hold.large.literal-miss.17` | large literal miss | 0.743× | 0.726–0.766× | 157 ns | 213 ns |
| `hold.large.literal-miss.20` | large literal miss | 0.751× | 0.710–0.827× | 140 ns | 197 ns |
| `hold.large.literal-miss.21` | large literal miss | 0.749× | 0.742–0.757× | 156 ns | 209 ns |
| `hold.large.literal-miss.24` | large literal miss | 0.677× | 0.672–0.684× | 140 ns | 206 ns |
| `hold.large.literal-miss.25` | large literal miss | 0.766× | 0.759–0.773× | 160 ns | 209 ns |
| `hold.large.literal-miss.28` | large literal miss | 0.646× | 0.562–0.697× | 138 ns | 201 ns |
| `hold.large.references.00` | large references | 0.750× | 0.727–0.794× | 186 ns | 254 ns |
| `hold.large.references.01` | large references | 0.723× | 0.719–0.727× | 190 ns | 263 ns |
| `hold.large.references.02` | large references | 0.723× | 0.713–0.732× | 199 ns | 273 ns |
| `hold.large.references.03` | large references | 0.791× | 0.745–0.878× | 215 ns | 282 ns |
| `hold.large.references.04` | large references | 0.732× | 0.728–0.736× | 187 ns | 255 ns |
| `hold.large.references.05` | large references | 0.723× | 0.715–0.731× | 183 ns | 252 ns |
| `hold.large.references.06` | large references | 0.687× | 0.609–0.732× | 194 ns | 266 ns |
| `hold.large.references.07` | large references | 0.718× | 0.708–0.729× | 208 ns | 291 ns |
| `hold.large.references.08` | large references | 0.758× | 0.728–0.816× | 189 ns | 259 ns |
| `hold.large.references.09` | large references | 0.751× | 0.743–0.762× | 189 ns | 255 ns |
| `hold.large.references.10` | large references | 0.725× | 0.720–0.731× | 196 ns | 270 ns |
| `hold.large.references.11` | large references | 0.743× | 0.732–0.756× | 204 ns | 276 ns |
| `hold.large.references.12` | large references | 0.740× | 0.734–0.746× | 185 ns | 251 ns |
| `hold.large.references.13` | large references | 0.727× | 0.723–0.732× | 190 ns | 261 ns |
| `hold.large.references.14` | large references | 0.720× | 0.675–0.746× | 204 ns | 275 ns |
| `hold.large.references.15` | large references | 0.735× | 0.723–0.748× | 210 ns | 285 ns |
| `hold.large.references.16` | large references | 0.728× | 0.724–0.731× | 187 ns | 257 ns |
| `hold.large.references.17` | large references | 0.723× | 0.718–0.729× | 182 ns | 252 ns |
| `hold.large.references.18` | large references | 0.736× | 0.711–0.757× | 197 ns | 267 ns |
| `hold.large.references.19` | large references | 0.716× | 0.702–0.728× | 210 ns | 290 ns |
| `hold.large.references.20` | large references | 0.728× | 0.723–0.732× | 190 ns | 261 ns |
| `hold.large.references.21` | large references | 0.735× | 0.729–0.741× | 189 ns | 257 ns |
| `hold.large.references.22` | large references | 0.728× | 0.719–0.739× | 194 ns | 269 ns |
| `hold.large.references.23` | large references | 0.724× | 0.700–0.741× | 204 ns | 278 ns |
| `hold.large.references.24` | large references | 0.787× | 0.736–0.895× | 185 ns | 250 ns |
| `hold.large.references.25` | large references | 0.733× | 0.726–0.742× | 189 ns | 261 ns |
| `hold.large.references.26` | large references | 0.675× | 0.593–0.726× | 199 ns | 274 ns |
| `hold.large.references.27` | large references | 0.717× | 0.657–0.757× | 210 ns | 283 ns |
| `hold.large.references.28` | large references | 0.730× | 0.727–0.733× | 186 ns | 255 ns |
| `hold.large.references.29` | large references | 0.723× | 0.718–0.727× | 182 ns | 251 ns |
| `hold.large.references.30` | large references | 0.734× | 0.730–0.739× | 194 ns | 265 ns |
| `hold.large.references.31` | large references | 0.748× | 0.737–0.761× | 214 ns | 285 ns |
| `hold.large.scanner-bytes.00` | large scanner bytes | 0.664× | 0.657–0.673× | 522 ns | 788 ns |
| `hold.large.scanner-bytes.01` | large scanner bytes | 0.799× | 0.787–0.812× | 849 ns | 1072 ns |
| `hold.large.scanner-bytes.04` | large scanner bytes | 0.670× | 0.657–0.684× | 521 ns | 775 ns |
| `hold.large.scanner-bytes.08` | large scanner bytes | 0.677× | 0.666–0.688× | 522 ns | 772 ns |
| `hold.large.scanner-bytes.12` | large scanner bytes | 0.667× | 0.656–0.679× | 526 ns | 789 ns |
| `hold.large.scanner-bytes.16` | large scanner bytes | 0.676× | 0.665–0.688× | 524 ns | 774 ns |
| `hold.large.scanner-bytes.20` | large scanner bytes | 0.669× | 0.659–0.679× | 521 ns | 776 ns |
| `hold.large.scanner-bytes.21` | large scanner bytes | 0.794× | 0.745–0.826× | 853 ns | 1043 ns |
| `hold.large.scanner-bytes.24` | large scanner bytes | 0.674× | 0.662–0.688× | 527 ns | 775 ns |
| `hold.large.scanner-bytes.28` | large scanner bytes | 0.676× | 0.666–0.684× | 532 ns | 790 ns |
| `hold.large.scanner-text.00` | large scanner text | 0.677× | 0.667–0.686× | 529 ns | 784 ns |
| `hold.large.scanner-text.04` | large scanner text | 0.763× | 0.657–0.932× | 581 ns | 903 ns |
| `hold.large.scanner-text.05` | large scanner text | 0.788× | 0.732–0.832× | 865 ns | 1051 ns |
| `hold.large.scanner-text.08` | large scanner text | 0.651× | 0.613–0.675× | 526 ns | 784 ns |
| `hold.large.scanner-text.12` | large scanner text | 0.680× | 0.667–0.694× | 530 ns | 778 ns |
| `hold.large.scanner-text.16` | large scanner text | 0.659× | 0.647–0.671× | 526 ns | 796 ns |
| `hold.large.scanner-text.20` | large scanner text | 0.662× | 0.649–0.675× | 530 ns | 799 ns |
| `hold.large.scanner-text.24` | large scanner text | 0.716× | 0.662–0.823× | 527 ns | 778 ns |
| `hold.large.scanner-text.28` | large scanner text | 0.702× | 0.690–0.714× | 895 ns | 1268 ns |
| `hold.large.structured-text.02` | large structured text | 0.799× | 0.758–0.880× | 2173 ns | 2842 ns |
| `hold.large.structured-text.05` | large structured text | 0.760× | 0.757–0.763× | 1077 ns | 1418 ns |
| `hold.large.structured-text.08` | large structured text | 0.722× | 0.719–0.724× | 619 ns | 855 ns |
| `hold.large.structured-text.11` | large structured text | 0.700× | 0.697–0.703× | 4205 ns | 5999 ns |
| `hold.large.structured-text.14` | large structured text | 0.741× | 0.716–0.756× | 2152 ns | 2853 ns |
| `hold.large.structured-text.17` | large structured text | 0.758× | 0.752–0.763× | 1091 ns | 1439 ns |
| `hold.large.structured-text.20` | large structured text | 0.721× | 0.714–0.730× | 605 ns | 841 ns |
| `hold.large.structured-text.23` | large structured text | 0.703× | 0.699–0.709× | 4208 ns | 5984 ns |
| `hold.large.structured-text.26` | large structured text | 0.737× | 0.734–0.739× | 2293 ns | 3117 ns |
| `hold.large.structured-text.29` | large structured text | 0.721× | 0.696–0.736× | 1176 ns | 1601 ns |
| `hold.large.verbose-dotall.00` | large verbose dotall | 0.701× | 0.669–0.720× | 345 ns | 479 ns |
| `hold.large.verbose-dotall.01` | large verbose dotall | 0.648× | 0.621–0.668× | 698 ns | 1047 ns |
| `hold.large.verbose-dotall.02` | large verbose dotall | 0.660× | 0.623–0.687× | 864 ns | 1263 ns |
| `hold.large.verbose-dotall.03` | large verbose dotall | 0.661× | 0.582–0.730× | 729 ns | 1080 ns |
| `hold.large.verbose-dotall.04` | large verbose dotall | 0.728× | 0.676–0.795× | 365 ns | 505 ns |
| `hold.large.verbose-dotall.05` | large verbose dotall | 0.705× | 0.670–0.779× | 698 ns | 1040 ns |
| `hold.large.verbose-dotall.06` | large verbose dotall | 0.710× | 0.639–0.806× | 921 ns | 1312 ns |
| `hold.large.verbose-dotall.07` | large verbose dotall | 0.685× | 0.674–0.702× | 731 ns | 1080 ns |
| `hold.large.verbose-dotall.08` | large verbose dotall | 0.688× | 0.645–0.720× | 365 ns | 506 ns |
| `hold.large.verbose-dotall.09` | large verbose dotall | 0.682× | 0.664–0.709× | 701 ns | 1042 ns |
| `hold.large.verbose-dotall.10` | large verbose dotall | 0.678× | 0.669–0.685× | 901 ns | 1317 ns |
| `hold.large.verbose-dotall.11` | large verbose dotall | 0.626× | 0.553–0.685× | 730 ns | 1074 ns |
| `hold.large.verbose-dotall.12` | large verbose dotall | 0.710× | 0.699–0.718× | 364 ns | 508 ns |
| `hold.large.verbose-dotall.13` | large verbose dotall | 0.664× | 0.653–0.672× | 701 ns | 1044 ns |
| `hold.large.verbose-dotall.14` | large verbose dotall | 0.696× | 0.689–0.706× | 904 ns | 1312 ns |
| `hold.large.verbose-dotall.15` | large verbose dotall | 0.658× | 0.613–0.689× | 736 ns | 1084 ns |
| `hold.large.verbose-dotall.16` | large verbose dotall | 0.707× | 0.670–0.739× | 354 ns | 495 ns |
| `hold.large.verbose-dotall.17` | large verbose dotall | 0.690× | 0.671–0.726× | 700 ns | 1042 ns |
| `hold.large.verbose-dotall.18` | large verbose dotall | 0.643× | 0.544–0.704× | 910 ns | 1312 ns |
| `hold.large.verbose-dotall.19` | large verbose dotall | 0.677× | 0.673–0.681× | 726 ns | 1076 ns |
| `hold.large.verbose-dotall.20` | large verbose dotall | 0.687× | 0.616–0.728× | 368 ns | 506 ns |
| `hold.large.verbose-dotall.21` | large verbose dotall | 0.682× | 0.667–0.711× | 700 ns | 1048 ns |
| `hold.large.verbose-dotall.22` | large verbose dotall | 0.690× | 0.686–0.696× | 907 ns | 1314 ns |
| `hold.large.verbose-dotall.23` | large verbose dotall | 0.677× | 0.673–0.681× | 728 ns | 1078 ns |
| `hold.large.verbose-dotall.24` | large verbose dotall | 0.724× | 0.718–0.729× | 365 ns | 505 ns |
| `hold.large.verbose-dotall.25` | large verbose dotall | 0.671× | 0.669–0.673× | 701 ns | 1044 ns |
| `hold.large.verbose-dotall.26` | large verbose dotall | 0.746× | 0.686–0.841× | 945 ns | 1371 ns |
| `hold.large.verbose-dotall.27` | large verbose dotall | 0.620× | 0.520–0.681× | 728 ns | 1080 ns |
| `hold.large.verbose-dotall.28` | large verbose dotall | 0.704× | 0.675–0.722× | 373 ns | 522 ns |
| `hold.large.verbose-dotall.29` | large verbose dotall | 0.660× | 0.637–0.673× | 701 ns | 1044 ns |
| `hold.large.verbose-dotall.30` | large verbose dotall | 0.726× | 0.683–0.806× | 943 ns | 1376 ns |
| `hold.large.verbose-dotall.31` | large verbose dotall | 0.680× | 0.673–0.690× | 727 ns | 1079 ns |
| `hold.literal.replace` | literal replace | 0.625× | 0.613–0.639× | 406 ns | 654 ns |
| `hold.look.negative-ahead` | look negative ahead | 0.739× | 0.707–0.795× | 728 ns | 1014 ns |
| `hold.match.miss` | match miss | 0.797× | 0.791–0.806× | 160 ns | 202 ns |
| `hold.pattern.verbose` | pattern verbose | 0.692× | 0.689–0.697× | 725 ns | 1047 ns |
| `hold.real.csv` | real csv | 0.625× | 0.567–0.668× | 1472 ns | 2207 ns |
| `hold.real.email` | real email | 0.748× | 0.728–0.760× | 648 ns | 854 ns |
| `hold.search.literal.hit` | search hit | 0.654× | 0.643–0.663× | 145 ns | 220 ns |
| `hold.search.literal.miss` | search miss | 0.665× | 0.659–0.670× | 128 ns | 194 ns |
