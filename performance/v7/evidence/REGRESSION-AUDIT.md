# Measured slowdowns against Python

This report accounts for every case in which a replacement took more than 20% longer than the unchanged Python 3.14.6 `re` module. Nothing is removed when a result is inconvenient.

- Total benchmark: **20,624** different workloads, **10,312** of them independently held back.
- Competitors: **4** independent implementations, each measured against the same Python baseline and workloads.
- Complete strict slowdowns across every competitor and workload: **29,771**.
- A speed above `1×` is faster than Python. A slowdown is counted only when `Python time / replacement time < 5/6`; exactly `5/6` is not more than 20% slower.
- Confidence intervals come from the original frozen, paired benchmark. The audit performs no new timing and does not change the held-back tests.

## Overall results

| Engine | Cases | Overall speed versus Python | 95% confidence interval | Reliably faster cases | More-than-20% slowdowns |
| --- | ---: | ---: | ---: | ---: | ---: |
| Zig engine | 20,624 | 1.611× | 1.610×–1.611× | 17,751/20,624 | 217 |
| C engine | 20,624 | 1.280× | 1.280×–1.281× | 14,791/20,624 | 2,171 |
| Rust engine | 20,624 | 0.931× | 0.931×–0.931× | 7,294/20,624 | 7,628 |
| Python engine | 20,624 | 0.022× | 0.022×–0.022× | 557/20,624 | 19,755 |

## Independently held-back results

| Engine | Held-back cases | Overall speed versus Python | 95% confidence interval | Reliably faster cases | More-than-20% slowdowns |
| --- | ---: | ---: | ---: | ---: | ---: |
| Zig engine | 10,312 | 1.609× | 1.608×–1.610× | 8,868/10,312 | 105 |
| C engine | 10,312 | 1.271× | 1.270×–1.272× | 7,369/10,312 | 1,116 |
| Rust engine | 10,312 | 0.925× | 0.925×–0.926× | 3,623/10,312 | 3,905 |
| Python engine | 10,312 | 0.022× | 0.022×–0.022× | 271/10,312 | 9,884 |

## Every held-back Zig slowdown

The Zig engine has **105** more-than-20% slowdowns among **10,312** held-back workloads and **217** across all **20,624** workloads. Every held-back case appears below.

The explanations describe what the frozen benchmark actually timed. They are not claims that a particular parser, matcher, Python/native call, memory allocation, or conversion was independently responsible: individual component costs were **NOT MEASURED**.

### By kind of workload

| Group | Slower cases | Median speed versus Python | Slowest case | Largest extra time |
| --- | ---: | ---: | ---: | ---: |
| warm module search | 49 | 0.797× | 0.732× | 36.7% |
| dual lookaround password | 9 | 0.826× | 0.794× | 26.0% |
| http cookie pairs | 9 | 0.822× | 0.750× | 33.3% |
| c preprocessor line | 8 | 0.808× | 0.757× | 32.0% |
| rfc5424 syslog | 7 | 0.813× | 0.786× | 27.2% |
| warm module findall | 7 | 0.791× | 0.770× | 29.9% |
| expanded ip version | 4 | 0.822× | 0.792× | 26.3% |
| named match surface | 3 | 0.812× | 0.784× | 27.5% |
| callable capture replace | 2 | 0.829× | 0.828× | 20.8% |
| jwt token segments | 2 | 0.830× | 0.827× | 20.9% |
| bracketed ipv6 host | 1 | 0.760× | 0.760× | 31.5% |
| python relative import | 1 | 0.825× | 0.825× | 21.2% |
| warm module sub | 1 | 0.830× | 0.830× | 20.5% |
| windowed binary collect | 1 | 0.799× | 0.799× | 25.1% |
| config lines | 1 | 0.804× | 0.804× | 24.4% |

### By Python operation

| Group | Slower cases | Median speed versus Python | Slowest case | Largest extra time |
| --- | ---: | ---: | ---: | ---: |
| search | 60 | 0.800× | 0.732× | 36.7% |
| findall | 29 | 0.810× | 0.757× | 32.0% |
| scanner | 9 | 0.822× | 0.750× | 33.3% |
| match surface | 3 | 0.812× | 0.784× | 27.5% |
| sub | 3 | 0.830× | 0.828× | 20.8% |
| fullmatch | 1 | 0.760× | 0.760× | 31.5% |

### By pattern lifetime

| Group | Slower cases | Median speed versus Python | Slowest case | Largest extra time |
| --- | ---: | ---: | ---: | ---: |
| module | 57 | 0.797× | 0.732× | 36.7% |
| compiled | 48 | 0.820× | 0.750× | 33.3% |

### By text or binary input

| Group | Slower cases | Median speed versus Python | Slowest case | Largest extra time |
| --- | ---: | ---: | ---: | ---: |
| text | 104 | 0.807× | 0.732× | 36.7% |
| memoryview | 1 | 0.799× | 0.799× | 25.1% |

### All individual held-back cases

| Frozen case | Workload | Python operation | Pattern lifetime | Input | Speed versus Python | Extra time | 95% confidence interval | Operations per trial | What was actually measured |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `hold.broader.bracketed-ipv6-host.53` | bracketed ipv6 host | `fullmatch` | compiled | text | 0.760× | 31.5% | 0.488×–0.969× | 8 | Compiled fullmatch includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.c-preprocessor-line.00` | c preprocessor line | `findall` | compiled | text | 0.757× | 32.0% | 0.656×–0.846× | 96 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.c-preprocessor-line.08` | c preprocessor line | `findall` | compiled | text | 0.823× | 21.5% | 0.816×–0.830× | 96 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.c-preprocessor-line.16` | c preprocessor line | `findall` | compiled | text | 0.810× | 23.5% | 0.796×–0.825× | 96 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.c-preprocessor-line.24` | c preprocessor line | `findall` | compiled | text | 0.807× | 23.9% | 0.684×–0.943× | 96 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.c-preprocessor-line.32` | c preprocessor line | `findall` | compiled | text | 0.810× | 23.5% | 0.797×–0.819× | 96 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.c-preprocessor-line.40` | c preprocessor line | `findall` | compiled | text | 0.833× | 20.1% | 0.788×–0.885× | 96 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.c-preprocessor-line.48` | c preprocessor line | `findall` | compiled | text | 0.782× | 27.9% | 0.721×–0.820× | 96 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.c-preprocessor-line.56` | c preprocessor line | `findall` | compiled | text | 0.805× | 24.2% | 0.792×–0.818× | 96 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.callable-capture-replace.25` | callable capture replace | `sub` | compiled | text | 0.828× | 20.8% | 0.735×–0.910× | 48 | Compiled sub includes invoking the Python replacement callback and constructing the output; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.callable-capture-replace.57` | callable capture replace | `sub` | compiled | text | 0.830× | 20.5% | 0.733×–0.910× | 48 | Compiled sub includes invoking the Python replacement callback and constructing the output; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.dual-lookaround-password.10` | dual lookaround password | `search` | compiled | text | 0.830× | 20.4% | 0.757×–0.878× | 32 | Compiled search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.dual-lookaround-password.23` | dual lookaround password | `search` | compiled | text | 0.828× | 20.7% | 0.782×–0.874× | 4 | Compiled search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.dual-lookaround-password.33` | dual lookaround password | `search` | compiled | text | 0.828× | 20.8% | 0.716×–0.902× | 48 | Compiled search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.dual-lookaround-password.37` | dual lookaround password | `search` | compiled | text | 0.813× | 23.0% | 0.747×–0.869× | 8 | Compiled search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.dual-lookaround-password.39` | dual lookaround password | `search` | compiled | text | 0.794× | 26.0% | 0.676×–0.879× | 4 | Compiled search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.dual-lookaround-password.44` | dual lookaround password | `search` | compiled | text | 0.828× | 20.8% | 0.786×–0.867× | 12 | Compiled search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.dual-lookaround-password.53` | dual lookaround password | `search` | compiled | text | 0.801× | 24.9% | 0.765×–0.836× | 8 | Compiled search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.dual-lookaround-password.59` | dual lookaround password | `search` | compiled | text | 0.821× | 21.9% | 0.728×–0.882× | 24 | Compiled search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.dual-lookaround-password.62` | dual lookaround password | `search` | compiled | text | 0.826× | 21.1% | 0.752×–0.888× | 6 | Compiled search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.http-cookie-pairs.00` | http cookie pairs | `scanner` | compiled | text | 0.822× | 21.6% | 0.761×–0.898× | 96 | Precompiled scanning includes creating the scanner, repeated search calls and collecting match objects; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.http-cookie-pairs.08` | http cookie pairs | `scanner` | compiled | text | 0.750× | 33.3% | 0.687×–0.810× | 96 | Precompiled scanning includes creating the scanner, repeated search calls and collecting match objects; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.http-cookie-pairs.16` | http cookie pairs | `scanner` | compiled | text | 0.822× | 21.7% | 0.807×–0.836× | 96 | Precompiled scanning includes creating the scanner, repeated search calls and collecting match objects; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.http-cookie-pairs.24` | http cookie pairs | `scanner` | compiled | text | 0.829× | 20.6% | 0.792×–0.891× | 96 | Precompiled scanning includes creating the scanner, repeated search calls and collecting match objects; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.http-cookie-pairs.32` | http cookie pairs | `scanner` | compiled | text | 0.824× | 21.3% | 0.804×–0.846× | 96 | Precompiled scanning includes creating the scanner, repeated search calls and collecting match objects; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.http-cookie-pairs.33` | http cookie pairs | `scanner` | compiled | text | 0.819× | 22.1% | 0.731×–0.896× | 48 | Precompiled scanning includes creating the scanner, repeated search calls and collecting match objects; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.http-cookie-pairs.40` | http cookie pairs | `scanner` | compiled | text | 0.803× | 24.5% | 0.763×–0.836× | 96 | Precompiled scanning includes creating the scanner, repeated search calls and collecting match objects; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.http-cookie-pairs.48` | http cookie pairs | `scanner` | compiled | text | 0.819× | 22.0% | 0.790×–0.867× | 96 | Precompiled scanning includes creating the scanner, repeated search calls and collecting match objects; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.http-cookie-pairs.56` | http cookie pairs | `scanner` | compiled | text | 0.822× | 21.7% | 0.802×–0.841× | 96 | Precompiled scanning includes creating the scanner, repeated search calls and collecting match objects; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.jwt-token-segments.35` | jwt token segments | `search` | compiled | text | 0.833× | 20.0% | 0.657×–1.018× | 24 | Compiled search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.jwt-token-segments.38` | jwt token segments | `search` | compiled | text | 0.827× | 20.9% | 0.733×–0.903× | 6 | Compiled search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.named-match-surface.07` | named match surface | `match-surface` | compiled | text | 0.822× | 21.6% | 0.805×–0.842× | 4 | Match access includes the search, groups, named groups, spans and template expansion; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.named-match-surface.31` | named match surface | `match-surface` | compiled | text | 0.784× | 27.5% | 0.645×–0.885× | 4 | Match access includes the search, groups, named groups, spans and template expansion; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.named-match-surface.61` | named match surface | `match-surface` | compiled | text | 0.812× | 23.2% | 0.698×–0.923× | 8 | Match access includes the search, groups, named groups, spans and template expansion; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.python-relative-import.32` | python relative import | `findall` | compiled | text | 0.825× | 21.2% | 0.775×–0.858× | 96 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.rfc5424-syslog.00` | rfc5424 syslog | `findall` | compiled | text | 0.832× | 20.2% | 0.824×–0.841× | 96 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.rfc5424-syslog.08` | rfc5424 syslog | `findall` | compiled | text | 0.813× | 23.0% | 0.753×–0.852× | 96 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.rfc5424-syslog.16` | rfc5424 syslog | `findall` | compiled | text | 0.827× | 21.0% | 0.822×–0.831× | 96 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.rfc5424-syslog.24` | rfc5424 syslog | `findall` | compiled | text | 0.812× | 23.1% | 0.770×–0.842× | 96 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.rfc5424-syslog.25` | rfc5424 syslog | `findall` | compiled | text | 0.786× | 27.2% | 0.692×–0.859× | 48 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.rfc5424-syslog.32` | rfc5424 syslog | `findall` | compiled | text | 0.801× | 24.8% | 0.737×–0.854× | 96 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.rfc5424-syslog.48` | rfc5424 syslog | `findall` | compiled | text | 0.828× | 20.8% | 0.813×–0.849× | 96 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-findall.00` | warm module findall | `findall` | module | text | 0.805× | 24.2% | 0.765×–0.858× | 96 | Module findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-findall.08` | warm module findall | `findall` | module | text | 0.770× | 29.9% | 0.707×–0.816× | 96 | Module findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-findall.16` | warm module findall | `findall` | module | text | 0.778× | 28.6% | 0.709×–0.819× | 96 | Module findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-findall.24` | warm module findall | `findall` | module | text | 0.791× | 26.4% | 0.765×–0.811× | 96 | Module findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-findall.32` | warm module findall | `findall` | module | text | 0.789× | 26.7% | 0.776×–0.800× | 96 | Module findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-findall.40` | warm module findall | `findall` | module | text | 0.811× | 23.3% | 0.804×–0.820× | 96 | Module findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-findall.48` | warm module findall | `findall` | module | text | 0.825× | 21.2% | 0.805×–0.859× | 96 | Module findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.00` | warm module search | `search` | module | text | 0.766× | 30.6% | 0.688×–0.817× | 96 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.01` | warm module search | `search` | module | text | 0.817× | 22.4% | 0.794×–0.854× | 48 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.02` | warm module search | `search` | module | text | 0.795× | 25.8% | 0.784×–0.807× | 32 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.03` | warm module search | `search` | module | text | 0.794× | 26.0% | 0.778×–0.809× | 24 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.04` | warm module search | `search` | module | text | 0.750× | 33.4% | 0.689×–0.804× | 12 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.05` | warm module search | `search` | module | text | 0.807× | 23.9% | 0.774×–0.846× | 8 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.07` | warm module search | `search` | module | text | 0.832× | 20.2% | 0.802×–0.866× | 4 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.08` | warm module search | `search` | module | text | 0.790× | 26.6% | 0.780×–0.799× | 96 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.09` | warm module search | `search` | module | text | 0.797× | 25.5% | 0.786×–0.808× | 48 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.10` | warm module search | `search` | module | text | 0.816× | 22.5% | 0.806×–0.827× | 32 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.11` | warm module search | `search` | module | text | 0.753× | 32.9% | 0.672×–0.803× | 24 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.12` | warm module search | `search` | module | text | 0.823× | 21.4% | 0.801×–0.849× | 12 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.13` | warm module search | `search` | module | text | 0.796× | 25.6% | 0.769×–0.822× | 8 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.14` | warm module search | `search` | module | text | 0.805× | 24.2% | 0.767×–0.834× | 6 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.16` | warm module search | `search` | module | text | 0.740× | 35.2% | 0.641×–0.806× | 96 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.17` | warm module search | `search` | module | text | 0.797× | 25.5% | 0.787×–0.807× | 48 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.19` | warm module search | `search` | module | text | 0.789× | 26.8% | 0.778×–0.798× | 24 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.20` | warm module search | `search` | module | text | 0.783× | 27.8% | 0.749×–0.806× | 12 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.21` | warm module search | `search` | module | text | 0.813× | 23.0% | 0.780×–0.851× | 8 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.22` | warm module search | `search` | module | text | 0.815× | 22.8% | 0.776×–0.853× | 6 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.24` | warm module search | `search` | module | text | 0.787× | 27.0% | 0.755×–0.809× | 96 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.26` | warm module search | `search` | module | text | 0.742× | 34.7% | 0.645×–0.804× | 32 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.28` | warm module search | `search` | module | text | 0.791× | 26.4% | 0.781×–0.801× | 12 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.32` | warm module search | `search` | module | text | 0.789× | 26.8% | 0.757×–0.810× | 96 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.34` | warm module search | `search` | module | text | 0.775× | 29.0% | 0.725×–0.808× | 32 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.35` | warm module search | `search` | module | text | 0.795× | 25.7% | 0.785×–0.806× | 24 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.36` | warm module search | `search` | module | text | 0.809× | 23.6% | 0.788×–0.832× | 12 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.37` | warm module search | `search` | module | text | 0.822× | 21.6% | 0.771×–0.883× | 8 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.39` | warm module search | `search` | module | text | 0.772× | 29.5% | 0.631×–0.910× | 4 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.40` | warm module search | `search` | module | text | 0.818× | 22.2% | 0.793×–0.861× | 96 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.41` | warm module search | `search` | module | text | 0.798× | 25.4% | 0.788×–0.807× | 48 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.42` | warm module search | `search` | module | text | 0.799× | 25.1% | 0.792×–0.805× | 32 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.43` | warm module search | `search` | module | text | 0.783× | 27.6% | 0.741×–0.811× | 24 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.44` | warm module search | `search` | module | text | 0.807× | 23.9% | 0.788×–0.827× | 12 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.45` | warm module search | `search` | module | text | 0.808× | 23.8% | 0.788×–0.828× | 8 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.46` | warm module search | `search` | module | text | 0.821× | 21.8% | 0.796×–0.851× | 6 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.48` | warm module search | `search` | module | text | 0.788× | 26.8% | 0.758×–0.808× | 96 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.49` | warm module search | `search` | module | text | 0.801× | 24.8% | 0.789×–0.813× | 48 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.50` | warm module search | `search` | module | text | 0.796× | 25.6% | 0.780×–0.807× | 32 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.51` | warm module search | `search` | module | text | 0.800× | 25.0% | 0.788×–0.812× | 24 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.52` | warm module search | `search` | module | text | 0.787× | 27.1% | 0.774×–0.801× | 12 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.53` | warm module search | `search` | module | text | 0.813× | 23.0% | 0.795×–0.832× | 8 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.55` | warm module search | `search` | module | text | 0.823× | 21.5% | 0.799×–0.850× | 4 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.56` | warm module search | `search` | module | text | 0.799× | 25.1% | 0.791×–0.808× | 96 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.57` | warm module search | `search` | module | text | 0.786× | 27.2% | 0.771×–0.798× | 48 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.58` | warm module search | `search` | module | text | 0.795× | 25.7% | 0.788×–0.804× | 32 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.59` | warm module search | `search` | module | text | 0.824× | 21.4% | 0.750×–0.951× | 24 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.62` | warm module search | `search` | module | text | 0.732× | 36.7% | 0.588×–0.829× | 6 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-search.63` | warm module search | `search` | module | text | 0.833× | 20.1% | 0.790×–0.888× | 4 | Module search includes performing the match and returning the Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.warm-module-sub.25` | warm module sub | `sub` | module | text | 0.830× | 20.5% | 0.750×–0.909× | 48 | Module sub includes replacement expansion and constructing the output; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.broader.windowed-binary-collect.20` | windowed binary collect | `findall` | compiled | memoryview | 0.799× | 25.1% | 0.660×–0.920× | 12 | Compiled findall includes constructing the complete Python result on memoryview input; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.deeper.config-lines.00` | config lines | `findall` | compiled | text | 0.804× | 24.4% | 0.622×–0.920× | 128 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.expanded.ip-version.00` | expanded ip version | `findall` | compiled | text | 0.816× | 22.5% | 0.784×–0.835× | 144 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.expanded.ip-version.06` | expanded ip version | `findall` | compiled | text | 0.792× | 26.3% | 0.719×–0.834× | 144 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.expanded.ip-version.24` | expanded ip version | `findall` | compiled | text | 0.832× | 20.3% | 0.824×–0.840× | 144 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |
| `hold.expanded.ip-version.42` | expanded ip version | `findall` | compiled | text | 0.827× | 21.0% | 0.819×–0.835× | 144 | Compiled findall includes constructing the complete Python result; separate engine, boundary and allocation costs NOT MEASURED. |

## Complete machine-readable evidence

[`initial-regressions.json.gz`](initial-regressions.json.gz) contains all **29,771** measured slowdowns, for all four candidates and both cohorts, including their original measured results, confidence intervals, traced-memory ratios, frozen workload metadata, and honest descriptions of timed work.

- Frozen correctness and workload digest: `2e6c098bd3a4757620461363106a9795f8defa98fe8bc9c13c0ebbf7ed58b598`.
- Complete raw measurement digest: `28777bab1930508446e53eeeb8a08190f9121be3617198c1132beb713be059c7`.
- Complete original analysis digest: `076d66bb0606a6acebcaf1d1e2c510d35b232f16710b1024f1fe0f55aee521da`.
- Independently audited integrity report digest: `429f6475b8767b4576e46e0fc36bad85fa1560773191a9ba06c06fbbda40c50f`.
- Compressed complete-slowdown archive digest: `c51a0d16f27d3a1d7fdf4622720ebd23115891bd1e0f3f4183a4a56012c7f8f6`.
- Restored complete-slowdown evidence digest: `2165555aab417909121077c04d17be35f742655a223e06e35d95f01d129430e6`.

Reproduce this report without running or changing the benchmark:

```sh
PYTHONPATH=. /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 tools/perf_v7_regression_audit.py --self-test
PYTHONPATH=. /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 tools/perf_v7_regression_audit.py --integrity performance/v7/evidence/initial-integrity.json --summary performance/v7/evidence/initial-summary.json.gz --output performance/v7/evidence/REGRESSION-AUDIT.md --json-output performance/v7/evidence/initial-regressions.json.gz
```
