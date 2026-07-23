# Broader performance result

This run retains **1,131,312** paired timing rows, all **49,728** engine/task results, and all **24,892** large slowdowns across practice and holdout. Raw SHA-256: `initial=a6fefab9e97c21e1ea17d258860fd05dbbc9adc3bb2154b66935abe3d3d84907; zig=e58c30e6350c6e98bd40e5176ee0c37290b7a978116aab1e1f52ca3cecfb7011`.

## Overall results

| Test set | Engine | Overall speed | 95% range | Clearly faster | Large slowdowns |
| --- | --- | ---: | ---: | ---: | ---: |
| calibration | Zig / rebar | 1.7282× | 1.7270–1.7294× | 5,610/6,216 | 5 |
| calibration | Native C engine | 1.2983× | 1.2973–1.2992× | 4,574/6,216 | 628 |
| calibration | Rust engine | 0.1333× | 0.1332–0.1333× | 226/6,216 | 5,892 |
| calibration | Python engine | 0.0205× | 0.0205–0.0205× | 223/6,216 | 5,902 |
| holdout | Zig / rebar | 1.7334× | 1.7321–1.7346× | 5,691/6,216 | 2 |
| holdout | Native C engine | 1.2830× | 1.2821–1.2839× | 4,577/6,216 | 653 |
| holdout | Rust engine | 0.1344× | 0.1343–0.1345× | 229/6,216 | 5,892 |
| holdout | Python engine | 0.0207× | 0.0207–0.0207× | 195/6,216 | 5,918 |
| all | Zig / rebar | 1.7308× | 1.7299–1.7316× | 11,301/12,432 | 7 |
| all | Native C engine | 1.2906× | 1.2900–1.2913× | 9,151/12,432 | 1,281 |
| all | Rust engine | 0.1338× | 0.1338–0.1339× | 455/12,432 | 11,784 |
| all | Python engine | 0.0206× | 0.0206–0.0206× | 418/12,432 | 11,820 |

## Every Zig / rebar holdout slowdown

There are **2** holdout tasks below 0.8×. Every task is listed with its stable ID and measured range; no slowdown is removed or reclassified.

### Why they are slower

- **ip version (2):** these six/seven-character version strings return four captures; at this size, building the result and crossing the Python/native boundary costs more than the match itself. Observed range: 0.730–0.767×.

### Every slower task

| Task | Kind of task | Speed | 95% range | Memory |
| --- | --- | ---: | ---: | ---: |
| `hold.expanded.ip-version.00` | expanded ip version | 0.767× | 0.677–0.836× | 0.01× |
| `hold.expanded.ip-version.06` | expanded ip version | 0.730× | 0.566–0.834× | 0.04× |

## All holdout workload families

Every family and engine is shown. `faster` counts tasks whose measured range is entirely above 1×; `slow` counts tasks below 0.8×.

| Workload family | Engine | Speed | Memory | Faster | Slow |
| --- | --- | ---: | ---: | ---: | ---: |
| backref | Zig / rebar | 1.070× | 0.14× | 1/1 | 0 |
| backref | Native C engine | 1.301× | 0.08× | 1/1 | 0 |
| backref | Rust engine | 0.170× | 0.06× | 0/1 | 1 |
| backref | Python engine | 0.020× | 6.45× | 0/1 | 1 |
| block dotall | Zig / rebar | 1.629× | 0.14× | 1/1 | 0 |
| block dotall | Native C engine | 1.497× | 0.08× | 1/1 | 0 |
| block dotall | Rust engine | 0.127× | 0.06× | 0/1 | 1 |
| block dotall | Python engine | 0.015× | 5.51× | 0/1 | 1 |
| branch control | Zig / rebar | 1.453× | 0.13× | 1/1 | 0 |
| branch control | Native C engine | 1.331× | 0.07× | 1/1 | 0 |
| branch control | Rust engine | 0.208× | 0.07× | 0/1 | 1 |
| branch control | Python engine | 0.032× | 4.26× | 0/1 | 1 |
| branch miss | Zig / rebar | 1.206× | 0.04× | 1/1 | 0 |
| branch miss | Native C engine | 1.093× | 0.00× | 1/1 | 0 |
| branch miss | Rust engine | 0.102× | 0.00× | 0/1 | 1 |
| branch miss | Python engine | 0.005× | 37.97× | 0/1 | 1 |
| branch prefix | Zig / rebar | 1.043× | 0.13× | 1/1 | 0 |
| branch prefix | Native C engine | 1.260× | 0.07× | 1/1 | 0 |
| branch prefix | Rust engine | 0.135× | 0.07× | 0/1 | 1 |
| branch prefix | Python engine | 0.022× | 6.11× | 0/1 | 1 |
| bytes | Zig / rebar | 2.102× | 0.17× | 1/1 | 0 |
| bytes | Native C engine | 2.611× | 0.18× | 1/1 | 0 |
| bytes | Rust engine | 0.297× | 0.82× | 0/1 | 1 |
| bytes | Python engine | 0.020× | 6.35× | 0/1 | 1 |
| bytes like | Zig / rebar | 1.825× | 0.17× | 1/1 | 0 |
| bytes like | Native C engine | 2.501× | 0.18× | 1/1 | 0 |
| bytes like | Rust engine | 0.296× | 0.75× | 0/1 | 1 |
| bytes like | Python engine | 0.016× | 7.78× | 0/1 | 1 |
| bytes replace | Zig / rebar | 2.032× | 0.17× | 1/1 | 0 |
| bytes replace | Native C engine | 0.997× | 1.16× | 0/1 | 0 |
| bytes replace | Rust engine | 0.084× | 1.45× | 0/1 | 1 |
| bytes replace | Python engine | 0.023× | 8.48× | 0/1 | 1 |
| bytes scan | Zig / rebar | 1.143× | 0.65× | 1/1 | 0 |
| bytes scan | Native C engine | 1.508× | 0.40× | 1/1 | 0 |
| bytes scan | Rust engine | 0.109× | 0.36× | 0/1 | 1 |
| bytes scan | Python engine | 0.019× | 7.67× | 0/1 | 1 |
| bytes view long | Zig / rebar | 2.123× | 0.59× | 1/1 | 0 |
| bytes view long | Native C engine | 1.316× | 0.60× | 1/1 | 0 |
| bytes view long | Rust engine | 0.557× | 5.66× | 0/1 | 1 |
| bytes view long | Python engine | 0.016× | 16.78× | 0/1 | 1 |
| capture look | Zig / rebar | 1.005× | 0.14× | 0/1 | 0 |
| capture look | Native C engine | 1.246× | 0.08× | 1/1 | 0 |
| capture look | Rust engine | 0.160× | 0.06× | 0/1 | 1 |
| capture look | Python engine | 0.019× | 11.42× | 0/1 | 1 |
| capture optional | Zig / rebar | 1.219× | 0.18× | 1/1 | 0 |
| capture optional | Native C engine | 1.301× | 0.18× | 1/1 | 0 |
| capture optional | Rust engine | 0.171× | 2.15× | 0/1 | 1 |
| capture optional | Python engine | 0.015× | 13.14× | 0/1 | 1 |
| cold | Zig / rebar | 2.723× | 0.46× | 1/1 | 0 |
| cold | Native C engine | 1.311× | 1.77× | 1/1 | 0 |
| cold | Rust engine | 1.147× | 0.93× | 1/1 | 0 |
| cold | Python engine | 0.091× | 5.57× | 0/1 | 1 |
| compile | Zig / rebar | 3.720× | 0.37× | 1/1 | 0 |
| compile | Native C engine | 1.374× | 2.11× | 1/1 | 0 |
| compile | Rust engine | 1.383× | 0.60× | 1/1 | 0 |
| compile | Python engine | 1.708× | 0.55× | 1/1 | 0 |
| compile complex | Zig / rebar | 7.244× | 0.22× | 1/1 | 0 |
| compile complex | Native C engine | 1.414× | 1.77× | 1/1 | 0 |
| compile complex | Rust engine | 1.333× | 0.55× | 1/1 | 0 |
| compile complex | Python engine | 1.777× | 0.38× | 1/1 | 0 |
| conditional | Zig / rebar | 1.158× | 0.14× | 1/1 | 0 |
| conditional | Native C engine | 1.273× | 0.08× | 1/1 | 0 |
| conditional | Rust engine | 0.144× | 0.06× | 0/1 | 1 |
| conditional | Python engine | 0.026× | 6.57× | 0/1 | 1 |
| deeper atomic alternatives | Zig / rebar | 2.127× | 0.53× | 64/64 | 0 |
| deeper atomic alternatives | Native C engine | 0.626× | 1.67× | 0/64 | 64 |
| deeper atomic alternatives | Rust engine | 0.159× | 4.44× | 0/64 | 64 |
| deeper atomic alternatives | Python engine | 0.013× | 17.32× | 0/64 | 64 |
| deeper backref named | Zig / rebar | 1.076× | 0.50× | 42/64 | 0 |
| deeper backref named | Native C engine | 1.109× | 0.39× | 56/64 | 0 |
| deeper backref named | Rust engine | 0.217× | 9.68× | 0/64 | 64 |
| deeper backref named | Python engine | 0.012× | 12.66× | 0/64 | 64 |
| deeper boundary positions | Zig / rebar | 1.356× | 0.83× | 64/64 | 0 |
| deeper boundary positions | Native C engine | 0.647× | 0.61× | 0/64 | 64 |
| deeper boundary positions | Rust engine | 0.143× | 0.66× | 0/64 | 64 |
| deeper boundary positions | Python engine | 0.007× | 9.95× | 0/64 | 64 |
| deeper bounded repeats | Zig / rebar | 1.402× | 0.72× | 64/64 | 0 |
| deeper bounded repeats | Native C engine | 1.403× | 0.53× | 64/64 | 0 |
| deeper bounded repeats | Rust engine | 0.145× | 0.51× | 0/64 | 64 |
| deeper bounded repeats | Python engine | 0.011× | 12.60× | 0/64 | 64 |
| deeper buffer tokenize | Zig / rebar | 1.182× | 0.85× | 56/64 | 0 |
| deeper buffer tokenize | Native C engine | 1.190× | 0.68× | 58/64 | 0 |
| deeper buffer tokenize | Rust engine | 0.097× | 0.54× | 0/64 | 64 |
| deeper buffer tokenize | Python engine | 0.014× | 6.73× | 0/64 | 64 |
| deeper byte highbit | Zig / rebar | 1.212× | 0.76× | 57/64 | 0 |
| deeper byte highbit | Native C engine | 1.125× | 0.45× | 53/64 | 0 |
| deeper byte highbit | Rust engine | 0.212× | 7.98× | 0/64 | 64 |
| deeper byte highbit | Python engine | 0.012× | 17.34× | 0/64 | 64 |
| deeper cold compile | Zig / rebar | 4.847× | 0.22× | 64/64 | 0 |
| deeper cold compile | Native C engine | 1.425× | 1.96× | 64/64 | 0 |
| deeper cold compile | Rust engine | 1.633× | 0.50× | 64/64 | 0 |
| deeper cold compile | Python engine | 1.843× | 0.40× | 64/64 | 0 |
| deeper combining wide | Zig / rebar | 1.968× | 0.82× | 64/64 | 0 |
| deeper combining wide | Native C engine | 1.406× | 0.60× | 64/64 | 0 |
| deeper combining wide | Rust engine | 0.031× | 0.89× | 0/64 | 64 |
| deeper combining wide | Python engine | 0.024× | 4.30× | 0/64 | 64 |
| deeper conditionals nested | Zig / rebar | 1.538× | 0.71× | 64/64 | 0 |
| deeper conditionals nested | Native C engine | 1.573× | 0.52× | 64/64 | 0 |
| deeper conditionals nested | Rust engine | 0.117× | 0.45× | 0/64 | 64 |
| deeper conditionals nested | Python engine | 0.018× | 7.94× | 0/64 | 64 |
| deeper config lines | Zig / rebar | 1.085× | 0.49× | 47/64 | 0 |
| deeper config lines | Native C engine | 0.874× | 0.40× | 0/64 | 0 |
| deeper config lines | Rust engine | 0.022× | 12.79× | 0/64 | 64 |
| deeper config lines | Python engine | 0.010× | 18.35× | 0/64 | 64 |
| deeper csv split even | Zig / rebar | 15.275× | 0.36× | 64/64 | 0 |
| deeper csv split even | Native C engine | 9.506× | 0.36× | 64/64 | 0 |
| deeper csv split even | Rust engine | 0.065× | 3.75× | 0/64 | 64 |
| deeper csv split even | Python engine | 0.008× | 21.78× | 0/64 | 64 |
| deeper dates zones | Zig / rebar | 1.661× | 0.53× | 64/64 | 0 |
| deeper dates zones | Native C engine | 1.327× | 0.38× | 64/64 | 0 |
| deeper dates zones | Rust engine | 0.161× | 0.39× | 0/64 | 64 |
| deeper dates zones | Python engine | 0.011× | 10.81× | 0/64 | 64 |
| deeper dense class finditer | Zig / rebar | 1.782× | 0.87× | 64/64 | 0 |
| deeper dense class finditer | Native C engine | 1.478× | 0.66× | 61/64 | 0 |
| deeper dense class finditer | Rust engine | 0.166× | 0.75× | 0/64 | 64 |
| deeper dense class finditer | Python engine | 0.024× | 3.58× | 0/64 | 64 |
| deeper dense literal findall | Zig / rebar | 1.032× | 1.00× | 30/64 | 0 |
| deeper dense literal findall | Native C engine | 0.865× | 1.00× | 0/64 | 2 |
| deeper dense literal findall | Rust engine | 0.310× | 10.49× | 0/64 | 64 |
| deeper dense literal findall | Python engine | 0.018× | 8.61× | 0/64 | 64 |
| deeper email mixed | Zig / rebar | 1.280× | 0.35× | 54/64 | 0 |
| deeper email mixed | Native C engine | 1.010× | 0.36× | 38/64 | 2 |
| deeper email mixed | Rust engine | 0.104× | 7.66× | 0/64 | 64 |
| deeper email mixed | Python engine | 0.013× | 10.92× | 0/64 | 64 |
| deeper error stack | Zig / rebar | 1.369× | 0.58× | 64/64 | 0 |
| deeper error stack | Native C engine | 1.288× | 0.49× | 64/64 | 0 |
| deeper error stack | Rust engine | 0.167× | 24.39× | 0/64 | 64 |
| deeper error stack | Python engine | 0.015× | 11.18× | 0/64 | 64 |
| deeper escape mixed | Zig / rebar | 1.004× | 0.95× | 2/64 | 0 |
| deeper escape mixed | Native C engine | 4.560× | 0.48× | 64/64 | 0 |
| deeper escape mixed | Rust engine | 1.000× | 0.95× | 1/64 | 0 |
| deeper escape mixed | Python engine | 0.999× | 0.95× | 1/64 | 0 |
| deeper file names | Zig / rebar | 2.061× | 0.41× | 64/64 | 0 |
| deeper file names | Native C engine | 0.798× | 0.31× | 0/64 | 36 |
| deeper file names | Rust engine | 0.218× | 1.85× | 0/64 | 64 |
| deeper file names | Python engine | 0.010× | 19.00× | 0/64 | 64 |
| deeper fullmatch structured | Zig / rebar | 1.812× | 0.06× | 64/64 | 0 |
| deeper fullmatch structured | Native C engine | 2.499× | 0.00× | 64/64 | 0 |
| deeper fullmatch structured | Rust engine | 0.057× | 0.00× | 0/64 | 64 |
| deeper fullmatch structured | Python engine | 0.013× | 13.92× | 0/64 | 64 |
| deeper html attributes | Zig / rebar | 1.085× | 0.89× | 50/64 | 0 |
| deeper html attributes | Native C engine | 0.854× | 0.61× | 0/64 | 4 |
| deeper html attributes | Rust engine | 0.101× | 19.27× | 0/64 | 64 |
| deeper html attributes | Python engine | 0.011× | 11.32× | 0/64 | 64 |
| deeper http headers | Zig / rebar | 1.480× | 0.73× | 64/64 | 0 |
| deeper http headers | Native C engine | 1.654× | 0.51× | 64/64 | 0 |
| deeper http headers | Rust engine | 0.065× | 0.52× | 0/64 | 64 |
| deeper http headers | Python engine | 0.018× | 7.88× | 0/64 | 64 |
| deeper inline modes | Zig / rebar | 1.663× | 0.24× | 64/64 | 0 |
| deeper inline modes | Native C engine | 1.031× | 0.29× | 38/64 | 0 |
| deeper inline modes | Rust engine | 0.044× | 4.72× | 0/64 | 64 |
| deeper inline modes | Python engine | 0.014× | 15.50× | 0/64 | 64 |
| deeper lookahead chain | Zig / rebar | 1.282× | 0.72× | 64/64 | 0 |
| deeper lookahead chain | Native C engine | 1.237× | 0.49× | 57/64 | 0 |
| deeper lookahead chain | Rust engine | 0.143× | 0.48× | 0/64 | 64 |
| deeper lookahead chain | Python engine | 0.015× | 10.03× | 0/64 | 64 |
| deeper lookbehind chain | Zig / rebar | 1.924× | 0.37× | 64/64 | 0 |
| deeper lookbehind chain | Native C engine | 1.237× | 0.30× | 61/64 | 0 |
| deeper lookbehind chain | Rust engine | 0.218× | 8.60× | 0/64 | 64 |
| deeper lookbehind chain | Python engine | 0.015× | 17.70× | 0/64 | 64 |
| deeper markdown code | Zig / rebar | 1.969× | 0.81× | 64/64 | 0 |
| deeper markdown code | Native C engine | 1.560× | 0.63× | 64/64 | 0 |
| deeper markdown code | Rust engine | 0.034× | 0.57× | 0/64 | 64 |
| deeper markdown code | Python engine | 0.008× | 5.67× | 0/64 | 64 |
| deeper match access | Zig / rebar | 1.418× | 0.04× | 64/64 | 0 |
| deeper match access | Native C engine | 1.098× | 0.00× | 53/64 | 0 |
| deeper match access | Rust engine | 0.150× | 0.00× | 0/64 | 64 |
| deeper match access | Python engine | 0.007× | 15.50× | 0/64 | 64 |
| deeper match short | Zig / rebar | 1.019× | 0.10× | 22/64 | 0 |
| deeper match short | Native C engine | 1.320× | 0.00× | 64/64 | 0 |
| deeper match short | Rust engine | 0.146× | 0.00× | 0/64 | 64 |
| deeper match short | Python engine | 0.021× | 7.59× | 0/64 | 64 |
| deeper module warm search | Zig / rebar | 0.933× | 0.11× | 0/64 | 0 |
| deeper module warm search | Native C engine | 1.311× | 0.06× | 61/64 | 0 |
| deeper module warm search | Rust engine | 0.356× | 0.06× | 0/64 | 64 |
| deeper module warm search | Python engine | 0.082× | 3.92× | 0/64 | 64 |
| deeper module warm sub | Zig / rebar | 1.216× | 0.13× | 52/64 | 0 |
| deeper module warm sub | Native C engine | 1.126× | 0.07× | 45/64 | 0 |
| deeper module warm sub | Rust engine | 0.102× | 4.07× | 0/64 | 64 |
| deeper module warm sub | Python engine | 0.030× | 9.38× | 0/64 | 64 |
| deeper money units | Zig / rebar | 1.798× | 0.51× | 64/64 | 0 |
| deeper money units | Native C engine | 0.922× | 0.48× | 0/64 | 1 |
| deeper money units | Rust engine | 0.132× | 3.52× | 0/64 | 64 |
| deeper money units | Python engine | 0.007× | 20.54× | 0/64 | 64 |
| deeper multiline anchors | Zig / rebar | 1.062× | 0.73× | 51/64 | 0 |
| deeper multiline anchors | Native C engine | 0.939× | 0.51× | 14/64 | 0 |
| deeper multiline anchors | Rust engine | 0.077× | 0.52× | 0/64 | 64 |
| deeper multiline anchors | Python engine | 0.011× | 8.59× | 0/64 | 64 |
| deeper negative class | Zig / rebar | 1.144× | 0.50× | 46/64 | 0 |
| deeper negative class | Native C engine | 1.280× | 0.41× | 63/64 | 0 |
| deeper negative class | Rust engine | 0.112× | 9.02× | 0/64 | 64 |
| deeper negative class | Python engine | 0.017× | 11.41× | 0/64 | 64 |
| deeper nullable positions | Zig / rebar | 2.860× | 0.80× | 64/64 | 0 |
| deeper nullable positions | Native C engine | 0.596× | 0.71× | 0/64 | 64 |
| deeper nullable positions | Rust engine | 0.178× | 0.64× | 0/64 | 64 |
| deeper nullable positions | Python engine | 0.008× | 9.75× | 0/64 | 64 |
| deeper path mixed bytes | Zig / rebar | 1.773× | 0.69× | 64/64 | 0 |
| deeper path mixed bytes | Native C engine | 1.039× | 1.16× | 29/64 | 0 |
| deeper path mixed bytes | Rust engine | 0.054× | 0.66× | 0/64 | 64 |
| deeper path mixed bytes | Python engine | 0.012× | 18.56× | 0/64 | 64 |
| deeper quote captures | Zig / rebar | 2.277× | 0.69× | 64/64 | 0 |
| deeper quote captures | Native C engine | 2.055× | 0.42× | 64/64 | 0 |
| deeper quote captures | Rust engine | 0.020× | 10.04× | 0/64 | 64 |
| deeper quote captures | Python engine | 0.003× | 12.39× | 0/64 | 64 |
| deeper request logs | Zig / rebar | 1.124× | 0.75× | 58/64 | 0 |
| deeper request logs | Native C engine | 1.074× | 0.58× | 29/64 | 0 |
| deeper request logs | Rust engine | 0.068× | 0.67× | 0/64 | 64 |
| deeper request logs | Python engine | 0.010× | 12.12× | 0/64 | 64 |
| deeper scanner window | Zig / rebar | 1.207× | 0.85× | 54/64 | 0 |
| deeper scanner window | Native C engine | 1.254× | 0.68× | 63/64 | 0 |
| deeper scanner window | Rust engine | 0.112× | 0.47× | 0/64 | 64 |
| deeper scanner window | Python engine | 0.015× | 5.10× | 0/64 | 64 |
| deeper search long hit | Zig / rebar | 5.157× | 1.33× | 63/64 | 0 |
| deeper search long hit | Native C engine | 0.755× | 0.73× | 32/64 | 29 |
| deeper search long hit | Rust engine | 0.378× | 0.67× | 0/64 | 64 |
| deeper search long hit | Python engine | 0.281× | 21.52× | 18/64 | 41 |
| deeper search long miss | Zig / rebar | 5.843× | 48.00× | 61/64 | 0 |
| deeper search long miss | Native C engine | 0.842× | 0.00× | 35/64 | 29 |
| deeper search long miss | Rust engine | 0.403× | 0.00× | 0/64 | 64 |
| deeper search long miss | Python engine | 0.526× | 112.00× | 24/64 | 40 |
| deeper shared prefix alternatives | Zig / rebar | 1.408× | 0.22× | 64/64 | 0 |
| deeper shared prefix alternatives | Native C engine | 0.505× | 0.27× | 0/64 | 64 |
| deeper shared prefix alternatives | Rust engine | 0.107× | 3.03× | 0/64 | 64 |
| deeper shared prefix alternatives | Python engine | 0.007× | 20.94× | 0/64 | 64 |
| deeper shell vars | Zig / rebar | 1.573× | 0.49× | 64/64 | 0 |
| deeper shell vars | Native C engine | 1.641× | 0.19× | 64/64 | 0 |
| deeper shell vars | Rust engine | 0.063× | 14.86× | 0/64 | 64 |
| deeper shell vars | Python engine | 0.017× | 12.20× | 0/64 | 64 |
| deeper source comments | Zig / rebar | 2.038× | 0.39× | 64/64 | 0 |
| deeper source comments | Native C engine | 1.349× | 0.28× | 64/64 | 0 |
| deeper source comments | Rust engine | 0.036× | 7.86× | 0/64 | 64 |
| deeper source comments | Python engine | 0.007× | 13.46× | 0/64 | 64 |
| deeper sql tokens | Zig / rebar | 1.507× | 0.88× | 64/64 | 0 |
| deeper sql tokens | Native C engine | 0.719× | 1.10× | 0/64 | 61 |
| deeper sql tokens | Rust engine | 0.111× | 0.64× | 0/64 | 64 |
| deeper sql tokens | Python engine | 0.015× | 4.87× | 0/64 | 64 |
| deeper unicode casefold | Zig / rebar | 2.534× | 0.76× | 64/64 | 0 |
| deeper unicode casefold | Native C engine | 1.092× | 0.67× | 54/64 | 0 |
| deeper unicode casefold | Rust engine | 0.025× | 1.56× | 0/64 | 64 |
| deeper unicode casefold | Python engine | 0.019× | 10.16× | 0/64 | 64 |
| deeper unicode word lines | Zig / rebar | 2.492× | 0.50× | 64/64 | 0 |
| deeper unicode word lines | Native C engine | 1.414× | 0.26× | 64/64 | 0 |
| deeper unicode word lines | Rust engine | 0.180× | 2.77× | 0/64 | 64 |
| deeper unicode word lines | Python engine | 0.008× | 48.34× | 0/64 | 64 |
| deeper uuid hash | Zig / rebar | 3.962× | 0.58× | 64/64 | 0 |
| deeper uuid hash | Native C engine | 2.196× | 0.53× | 64/64 | 0 |
| deeper uuid hash | Rust engine | 0.399× | 14.08× | 0/64 | 64 |
| deeper uuid hash | Python engine | 0.021× | 11.31× | 0/64 | 64 |
| deeper version tags | Zig / rebar | 1.225× | 0.16× | 64/64 | 0 |
| deeper version tags | Native C engine | 1.327× | 0.11× | 64/64 | 0 |
| deeper version tags | Rust engine | 0.098× | 0.05× | 0/64 | 64 |
| deeper version tags | Python engine | 0.012× | 18.30× | 0/64 | 64 |
| deeper windowed collect | Zig / rebar | 1.350× | 0.68× | 55/64 | 0 |
| deeper windowed collect | Native C engine | 1.089× | 0.49× | 38/64 | 1 |
| deeper windowed collect | Rust engine | 0.174× | 1.74× | 0/64 | 64 |
| deeper windowed collect | Python engine | 0.015× | 8.56× | 0/64 | 64 |
| dense iter | Zig / rebar | 1.945× | 0.75× | 1/1 | 0 |
| dense iter | Native C engine | 1.541× | 0.52× | 1/1 | 0 |
| dense iter | Rust engine | 0.172× | 0.50× | 0/1 | 1 |
| dense iter | Python engine | 0.022× | 4.65× | 0/1 | 1 |
| empty | Zig / rebar | 2.395× | 0.64× | 1/1 | 0 |
| empty | Native C engine | 2.363× | 0.38× | 1/1 | 0 |
| empty | Rust engine | 0.193× | 0.39× | 0/1 | 1 |
| empty | Python engine | 0.016× | 8.07× | 0/1 | 1 |
| escape | Zig / rebar | 0.941× | 0.68× | 0/1 | 0 |
| escape | Native C engine | 4.711× | 0.32× | 1/1 | 0 |
| escape | Rust engine | 0.988× | 0.68× | 0/1 | 0 |
| escape | Python engine | 0.997× | 0.68× | 0/1 | 0 |
| expanded ascii boundary | Zig / rebar | 1.855× | 0.79× | 48/48 | 0 |
| expanded ascii boundary | Native C engine | 1.269× | 0.56× | 47/48 | 0 |
| expanded ascii boundary | Rust engine | 0.048× | 0.79× | 0/48 | 48 |
| expanded ascii boundary | Python engine | 0.019× | 4.49× | 0/48 | 48 |
| expanded atomic possessive | Zig / rebar | 2.094× | 0.26× | 48/48 | 0 |
| expanded atomic possessive | Native C engine | 0.800× | 1.85× | 0/48 | 19 |
| expanded atomic possessive | Rust engine | 0.129× | 3.23× | 0/48 | 48 |
| expanded atomic possessive | Python engine | 0.014× | 14.70× | 0/48 | 48 |
| expanded backreference | Zig / rebar | 1.179× | 0.19× | 29/48 | 0 |
| expanded backreference | Native C engine | 1.081× | 0.21× | 35/48 | 0 |
| expanded backreference | Rust engine | 0.193× | 6.72× | 0/48 | 48 |
| expanded backreference | Python engine | 0.011× | 14.12× | 0/48 | 48 |
| expanded branch alternatives | Zig / rebar | 1.668× | 0.14× | 48/48 | 0 |
| expanded branch alternatives | Native C engine | 0.609× | 0.18× | 0/48 | 43 |
| expanded branch alternatives | Rust engine | 0.133× | 1.98× | 0/48 | 48 |
| expanded branch alternatives | Python engine | 0.009× | 20.02× | 0/48 | 48 |
| expanded byte buffer | Zig / rebar | 1.300× | 0.67× | 47/48 | 0 |
| expanded byte buffer | Native C engine | 1.410× | 0.42× | 48/48 | 0 |
| expanded byte buffer | Rust engine | 0.145× | 2.48× | 0/48 | 48 |
| expanded byte buffer | Python engine | 0.015× | 11.48× | 0/48 | 48 |
| expanded class heavy | Zig / rebar | 2.056× | 0.74× | 48/48 | 0 |
| expanded class heavy | Native C engine | 1.850× | 0.50× | 48/48 | 0 |
| expanded class heavy | Rust engine | 0.176× | 0.50× | 0/48 | 48 |
| expanded class heavy | Python engine | 0.016× | 12.20× | 0/48 | 48 |
| expanded cold compile | Zig / rebar | 5.030× | 0.19× | 48/48 | 0 |
| expanded cold compile | Native C engine | 1.351× | 1.97× | 48/48 | 0 |
| expanded cold compile | Rust engine | 1.733× | 0.46× | 48/48 | 0 |
| expanded cold compile | Python engine | 1.818× | 0.36× | 48/48 | 0 |
| expanded cold module | Zig / rebar | 3.660× | 0.39× | 48/48 | 0 |
| expanded cold module | Native C engine | 1.528× | 1.55× | 48/48 | 0 |
| expanded cold module | Rust engine | 1.181× | 0.82× | 48/48 | 0 |
| expanded cold module | Python engine | 0.099× | 6.73× | 0/48 | 48 |
| expanded combining emoji | Zig / rebar | 1.999× | 0.53× | 48/48 | 0 |
| expanded combining emoji | Native C engine | 1.216× | 0.53× | 47/48 | 0 |
| expanded combining emoji | Rust engine | 0.048× | 1.27× | 0/48 | 48 |
| expanded combining emoji | Python engine | 0.018× | 11.73× | 0/48 | 48 |
| expanded comment strip | Zig / rebar | 2.019× | 0.28× | 48/48 | 0 |
| expanded comment strip | Native C engine | 1.463× | 0.23× | 31/48 | 0 |
| expanded comment strip | Rust engine | 0.131× | 5.06× | 0/48 | 48 |
| expanded comment strip | Python engine | 0.017× | 8.60× | 0/48 | 48 |
| expanded conditionals | Zig / rebar | 1.555× | 0.66× | 48/48 | 0 |
| expanded conditionals | Native C engine | 1.604× | 0.44× | 48/48 | 0 |
| expanded conditionals | Rust engine | 0.143× | 0.36× | 0/48 | 48 |
| expanded conditionals | Python engine | 0.019× | 7.20× | 0/48 | 48 |
| expanded csv fields | Zig / rebar | 1.924× | 0.52× | 48/48 | 0 |
| expanded csv fields | Native C engine | 0.823× | 2.30× | 0/48 | 26 |
| expanded csv fields | Rust engine | 0.149× | 0.31× | 0/48 | 48 |
| expanded csv fields | Python engine | 0.011× | 21.07× | 0/48 | 48 |
| expanded dates numbers | Zig / rebar | 1.643× | 0.64× | 48/48 | 0 |
| expanded dates numbers | Native C engine | 1.219× | 0.41× | 45/48 | 0 |
| expanded dates numbers | Rust engine | 0.140× | 0.39× | 0/48 | 48 |
| expanded dates numbers | Python engine | 0.011× | 17.33× | 0/48 | 48 |
| expanded email extract | Zig / rebar | 1.270× | 0.25× | 39/48 | 0 |
| expanded email extract | Native C engine | 1.026× | 0.27× | 27/48 | 0 |
| expanded email extract | Rust engine | 0.106× | 5.51× | 0/48 | 48 |
| expanded email extract | Python engine | 0.013× | 10.82× | 0/48 | 48 |
| expanded html tags | Zig / rebar | 1.655× | 0.10× | 48/48 | 0 |
| expanded html tags | Native C engine | 0.892× | 1.60× | 0/48 | 0 |
| expanded html tags | Rust engine | 0.026× | 5.92× | 0/48 | 48 |
| expanded html tags | Python engine | 0.010× | 20.25× | 0/48 | 48 |
| expanded ip version | Zig / rebar | 1.342× | 0.18× | 39/48 | 2 |
| expanded ip version | Native C engine | 0.945× | 0.20× | 6/48 | 0 |
| expanded ip version | Rust engine | 0.123× | 3.71× | 0/48 | 48 |
| expanded ip version | Python engine | 0.009× | 29.14× | 0/48 | 48 |
| expanded json fields | Zig / rebar | 1.486× | 0.66× | 48/48 | 0 |
| expanded json fields | Native C engine | 1.458× | 0.44× | 48/48 | 0 |
| expanded json fields | Rust engine | 0.128× | 0.38× | 0/48 | 48 |
| expanded json fields | Python engine | 0.018× | 10.07× | 0/48 | 48 |
| expanded line records | Zig / rebar | 1.310× | 0.68× | 48/48 | 0 |
| expanded line records | Native C engine | 1.200× | 0.47× | 39/48 | 0 |
| expanded line records | Rust engine | 0.126× | 0.40× | 0/48 | 48 |
| expanded line records | Python engine | 0.012× | 10.87× | 0/48 | 48 |
| expanded long literal | Zig / rebar | 2.535× | 4.40× | 41/48 | 0 |
| expanded long literal | Native C engine | 0.865× | 0.00× | 20/48 | 17 |
| expanded long literal | Rust engine | 0.284× | 0.00× | 0/48 | 48 |
| expanded long literal | Python engine | 0.146× | 37.15× | 3/48 | 40 |
| expanded lookaround | Zig / rebar | 1.668× | 0.67× | 48/48 | 0 |
| expanded lookaround | Native C engine | 1.456× | 0.43× | 48/48 | 0 |
| expanded lookaround | Rust engine | 0.140× | 0.39× | 0/48 | 48 |
| expanded lookaround | Python engine | 0.021× | 8.93× | 0/48 | 48 |
| expanded markdown links | Zig / rebar | 1.748× | 0.67× | 48/48 | 0 |
| expanded markdown links | Native C engine | 1.852× | 0.46× | 48/48 | 0 |
| expanded markdown links | Rust engine | 0.092× | 0.39× | 0/48 | 48 |
| expanded markdown links | Python engine | 0.021× | 11.21× | 0/48 | 48 |
| expanded match surface | Zig / rebar | 1.383× | 0.04× | 48/48 | 0 |
| expanded match surface | Native C engine | 1.108× | 0.00× | 48/48 | 0 |
| expanded match surface | Rust engine | 0.152× | 0.00× | 0/48 | 48 |
| expanded match surface | Python engine | 0.008× | 15.49× | 0/48 | 48 |
| expanded newline normalize | Zig / rebar | 1.598× | 0.20× | 47/48 | 0 |
| expanded newline normalize | Native C engine | 1.361× | 0.17× | 46/48 | 0 |
| expanded newline normalize | Rust engine | 0.212× | 3.09× | 0/48 | 48 |
| expanded newline normalize | Python engine | 0.033× | 4.61× | 0/48 | 48 |
| expanded nullable empty | Zig / rebar | 3.019× | 0.58× | 48/48 | 0 |
| expanded nullable empty | Native C engine | 0.583× | 0.57× | 0/48 | 48 |
| expanded nullable empty | Rust engine | 0.180× | 0.39× | 0/48 | 48 |
| expanded nullable empty | Python engine | 0.008× | 20.70× | 0/48 | 48 |
| expanded path bytes | Zig / rebar | 1.879× | 0.64× | 48/48 | 0 |
| expanded path bytes | Native C engine | 1.874× | 0.39× | 48/48 | 0 |
| expanded path bytes | Rust engine | 0.066× | 0.60× | 0/48 | 48 |
| expanded path bytes | Python engine | 0.016× | 13.48× | 0/48 | 48 |
| expanded path text | Zig / rebar | 1.731× | 0.16× | 48/48 | 0 |
| expanded path text | Native C engine | 0.794× | 1.63× | 0/48 | 20 |
| expanded path text | Rust engine | 0.049× | 3.94× | 0/48 | 48 |
| expanded path text | Python engine | 0.010× | 28.83× | 0/48 | 48 |
| expanded phone postcode | Zig / rebar | 1.618× | 0.15× | 47/48 | 0 |
| expanded phone postcode | Native C engine | 1.097× | 0.19× | 33/48 | 0 |
| expanded phone postcode | Rust engine | 0.219× | 2.24× | 0/48 | 48 |
| expanded phone postcode | Python engine | 0.010× | 19.11× | 0/48 | 48 |
| expanded quoted escapes | Zig / rebar | 2.158× | 0.09× | 48/48 | 0 |
| expanded quoted escapes | Native C engine | 0.569× | 1.87× | 0/48 | 48 |
| expanded quoted escapes | Rust engine | 0.199× | 1.75× | 0/48 | 48 |
| expanded quoted escapes | Python engine | 0.007× | 35.20× | 0/48 | 48 |
| expanded replace callback | Zig / rebar | 1.424× | 0.30× | 48/48 | 0 |
| expanded replace callback | Native C engine | 1.355× | 0.25× | 48/48 | 0 |
| expanded replace callback | Rust engine | 0.183× | 0.67× | 0/48 | 48 |
| expanded replace callback | Python engine | 0.052× | 7.15× | 0/48 | 48 |
| expanded replace redact | Zig / rebar | 1.929× | 0.19× | 48/48 | 0 |
| expanded replace redact | Native C engine | 1.360× | 0.16× | 48/48 | 0 |
| expanded replace redact | Rust engine | 0.117× | 5.15× | 0/48 | 48 |
| expanded replace redact | Python engine | 0.020× | 10.04× | 0/48 | 48 |
| expanded replace template | Zig / rebar | 1.663× | 0.22× | 48/48 | 0 |
| expanded replace template | Native C engine | 1.849× | 0.18× | 48/48 | 0 |
| expanded replace template | Rust engine | 0.072× | 6.19× | 0/48 | 48 |
| expanded replace template | Python engine | 0.019× | 10.52× | 0/48 | 48 |
| expanded scanner | Zig / rebar | 1.266× | 0.81× | 47/48 | 0 |
| expanded scanner | Native C engine | 1.173× | 0.64× | 43/48 | 0 |
| expanded scanner | Rust engine | 0.097× | 0.38× | 0/48 | 48 |
| expanded scanner | Python engine | 0.013× | 6.69× | 0/48 | 48 |
| expanded source tokens | Zig / rebar | 1.714× | 0.86× | 48/48 | 0 |
| expanded source tokens | Native C engine | 1.277× | 0.69× | 47/48 | 0 |
| expanded source tokens | Rust engine | 0.124× | 0.51× | 0/48 | 48 |
| expanded source tokens | Python engine | 0.013× | 7.47× | 0/48 | 48 |
| expanded split captures | Zig / rebar | 1.848× | 0.56× | 48/48 | 0 |
| expanded split captures | Native C engine | 1.383× | 0.51× | 48/48 | 0 |
| expanded split captures | Rust engine | 0.170× | 3.81× | 0/48 | 48 |
| expanded split captures | Python engine | 0.024× | 9.41× | 0/48 | 48 |
| expanded split delimiters | Zig / rebar | 2.333× | 0.39× | 48/48 | 0 |
| expanded split delimiters | Native C engine | 1.579× | 0.41× | 48/48 | 0 |
| expanded split delimiters | Rust engine | 0.201× | 3.16× | 0/48 | 48 |
| expanded split delimiters | Python engine | 0.027× | 8.38× | 0/48 | 48 |
| expanded unicode case | Zig / rebar | 2.598× | 0.80× | 48/48 | 0 |
| expanded unicode case | Native C engine | 2.072× | 0.58× | 48/48 | 0 |
| expanded unicode case | Rust engine | 0.054× | 0.82× | 0/48 | 48 |
| expanded unicode case | Python engine | 0.037× | 3.08× | 0/48 | 48 |
| expanded unicode words | Zig / rebar | 1.643× | 0.58× | 48/48 | 0 |
| expanded unicode words | Native C engine | 0.980× | 0.59× | 3/48 | 0 |
| expanded unicode words | Rust engine | 0.033× | 1.38× | 0/48 | 48 |
| expanded unicode words | Python engine | 0.018× | 9.63× | 0/48 | 48 |
| expanded url extract | Zig / rebar | 1.859× | 0.46× | 48/48 | 0 |
| expanded url extract | Native C engine | 1.861× | 0.34× | 48/48 | 0 |
| expanded url extract | Rust engine | 0.042× | 0.29× | 0/48 | 48 |
| expanded url extract | Python engine | 0.014× | 12.45× | 0/48 | 48 |
| expanded whitespace clean | Zig / rebar | 2.863× | 0.17× | 48/48 | 0 |
| expanded whitespace clean | Native C engine | 2.719× | 0.14× | 48/48 | 0 |
| expanded whitespace clean | Rust engine | 0.313× | 2.84× | 0/48 | 48 |
| expanded whitespace clean | Python engine | 0.030× | 9.17× | 0/48 | 48 |
| expanded windowed | Zig / rebar | 1.331× | 0.43× | 44/48 | 0 |
| expanded windowed | Native C engine | 1.034× | 0.35× | 21/48 | 0 |
| expanded windowed | Rust engine | 0.167× | 0.69× | 0/48 | 48 |
| expanded windowed | Python engine | 0.015× | 10.02× | 0/48 | 48 |
| findall | Zig / rebar | 1.852× | 0.19× | 1/1 | 0 |
| findall | Native C engine | 2.389× | 0.21× | 1/1 | 0 |
| findall | Rust engine | 0.167× | 1.46× | 0/1 | 1 |
| findall | Python engine | 0.019× | 9.70× | 0/1 | 1 |
| finditer | Zig / rebar | 1.600× | 0.64× | 1/1 | 0 |
| finditer | Native C engine | 2.095× | 0.41× | 1/1 | 0 |
| finditer | Rust engine | 0.161× | 0.34× | 0/1 | 1 |
| finditer | Python engine | 0.021× | 6.58× | 0/1 | 1 |
| fullmatch | Zig / rebar | 1.291× | 0.13× | 1/1 | 0 |
| fullmatch | Native C engine | 1.533× | 0.07× | 1/1 | 0 |
| fullmatch | Rust engine | 0.134× | 0.06× | 0/1 | 1 |
| fullmatch | Python engine | 0.015× | 14.49× | 0/1 | 1 |
| fullmatch miss | Zig / rebar | 1.364× | 0.04× | 1/1 | 0 |
| fullmatch miss | Native C engine | 1.683× | 0.00× | 1/1 | 0 |
| fullmatch miss | Rust engine | 0.291× | 0.00× | 0/1 | 1 |
| fullmatch miss | Python engine | 0.020× | 9.31× | 0/1 | 1 |
| ignore case | Zig / rebar | 2.009× | 0.16× | 1/1 | 0 |
| ignore case | Native C engine | 1.718× | 0.16× | 1/1 | 0 |
| ignore case | Rust engine | 0.430× | 0.90× | 0/1 | 1 |
| ignore case | Python engine | 0.033× | 4.19× | 0/1 | 1 |
| large ascii mode | Zig / rebar | 1.785× | 0.37× | 32/32 | 0 |
| large ascii mode | Native C engine | 1.172× | 0.39× | 31/32 | 0 |
| large ascii mode | Rust engine | 0.057× | 1.23× | 0/32 | 32 |
| large ascii mode | Python engine | 0.021× | 6.62× | 0/32 | 32 |
| large branch control | Zig / rebar | 2.011× | 0.13× | 32/32 | 0 |
| large branch control | Native C engine | 1.635× | 0.63× | 32/32 | 0 |
| large branch control | Rust engine | 0.168× | 0.07× | 0/32 | 32 |
| large branch control | Python engine | 0.012× | 11.60× | 0/32 | 32 |
| large bytes buffer | Zig / rebar | 1.712× | 0.69× | 32/32 | 0 |
| large bytes buffer | Native C engine | 1.613× | 0.44× | 32/32 | 0 |
| large bytes buffer | Rust engine | 0.175× | 0.63× | 0/32 | 32 |
| large bytes buffer | Python engine | 0.023× | 5.12× | 0/32 | 32 |
| large bytes replace | Zig / rebar | 2.664× | 0.16× | 32/32 | 0 |
| large bytes replace | Native C engine | 1.175× | 1.59× | 27/32 | 0 |
| large bytes replace | Rust engine | 0.084× | 3.41× | 0/32 | 32 |
| large bytes replace | Python engine | 0.023× | 9.16× | 0/32 | 32 |
| large bytes tokens | Zig / rebar | 1.791× | 0.30× | 32/32 | 0 |
| large bytes tokens | Native C engine | 2.784× | 0.30× | 32/32 | 0 |
| large bytes tokens | Rust engine | 0.323× | 2.05× | 0/32 | 32 |
| large bytes tokens | Python engine | 0.023× | 6.93× | 0/32 | 32 |
| large cleanup | Zig / rebar | 2.246× | 0.27× | 32/32 | 0 |
| large cleanup | Native C engine | 2.009× | 0.24× | 32/32 | 0 |
| large cleanup | Rust engine | 0.274× | 2.29× | 0/32 | 32 |
| large cleanup | Python engine | 0.030× | 7.34× | 0/32 | 32 |
| large cold compile | Zig / rebar | 6.824× | 0.23× | 32/32 | 0 |
| large cold compile | Native C engine | 1.445× | 1.65× | 32/32 | 0 |
| large cold compile | Rust engine | 1.308× | 0.50× | 32/32 | 0 |
| large cold compile | Python engine | 1.792× | 0.39× | 32/32 | 0 |
| large cold search | Zig / rebar | 2.846× | 0.46× | 32/32 | 0 |
| large cold search | Native C engine | 1.342× | 1.77× | 32/32 | 0 |
| large cold search | Rust engine | 1.166× | 0.64× | 32/32 | 0 |
| large cold search | Python engine | 0.102× | 5.57× | 0/32 | 32 |
| large conditionals | Zig / rebar | 1.105× | 0.14× | 27/32 | 0 |
| large conditionals | Native C engine | 1.310× | 0.08× | 32/32 | 0 |
| large conditionals | Rust engine | 0.161× | 0.06× | 0/32 | 32 |
| large conditionals | Python engine | 0.026× | 6.55× | 0/32 | 32 |
| large empty iterator | Zig / rebar | 2.858× | 0.72× | 32/32 | 0 |
| large empty iterator | Native C engine | 2.095× | 0.47× | 32/32 | 0 |
| large empty iterator | Rust engine | 0.176× | 0.46× | 0/32 | 32 |
| large empty iterator | Python engine | 0.012× | 14.47× | 0/32 | 32 |
| large escape | Zig / rebar | 1.010× | 0.83× | 1/32 | 0 |
| large escape | Native C engine | 3.547× | 0.43× | 32/32 | 0 |
| large escape | Rust engine | 0.992× | 0.83× | 1/32 | 0 |
| large escape | Python engine | 1.002× | 0.83× | 3/32 | 0 |
| large everyday address | Zig / rebar | 1.451× | 0.18× | 32/32 | 0 |
| large everyday address | Native C engine | 1.066× | 0.14× | 20/32 | 11 |
| large everyday address | Rust engine | 0.109× | 0.27× | 0/32 | 32 |
| large everyday address | Python engine | 0.015× | 13.28× | 0/32 | 32 |
| large findall tokens | Zig / rebar | 1.839× | 0.21× | 32/32 | 0 |
| large findall tokens | Native C engine | 2.122× | 0.22× | 32/32 | 0 |
| large findall tokens | Rust engine | 0.156× | 2.47× | 0/32 | 32 |
| large findall tokens | Python engine | 0.019× | 10.14× | 0/32 | 32 |
| large finditer pairs | Zig / rebar | 1.597× | 0.67× | 32/32 | 0 |
| large finditer pairs | Native C engine | 2.018× | 0.45× | 32/32 | 0 |
| large finditer pairs | Rust engine | 0.150× | 0.37× | 0/32 | 32 |
| large finditer pairs | Python engine | 0.020× | 6.51× | 0/32 | 32 |
| large formatted lines | Zig / rebar | 1.741× | 0.13× | 32/32 | 0 |
| large formatted lines | Native C engine | 1.432× | 0.14× | 32/32 | 0 |
| large formatted lines | Rust engine | 0.398× | 2.93× | 0/32 | 32 |
| large formatted lines | Python engine | 0.023× | 7.15× | 0/32 | 32 |
| large literal hit | Zig / rebar | 1.079× | 1.33× | 18/32 | 0 |
| large literal hit | Native C engine | 1.161× | 0.73× | 31/32 | 0 |
| large literal hit | Rust engine | 0.168× | 0.67× | 0/32 | 32 |
| large literal hit | Python engine | 0.046× | 21.45× | 0/32 | 32 |
| large literal miss | Zig / rebar | 1.153× | 48.00× | 23/32 | 0 |
| large literal miss | Native C engine | 1.302× | 0.00× | 32/32 | 0 |
| large literal miss | Rust engine | 0.208× | 0.00× | 0/32 | 32 |
| large literal miss | Python engine | 0.188× | 112.00× | 0/32 | 32 |
| large long ending | Zig / rebar | 2.100× | 0.13× | 32/32 | 0 |
| large long ending | Native C engine | 2.378× | 0.07× | 32/32 | 0 |
| large long ending | Rust engine | 0.247× | 0.07× | 0/32 | 32 |
| large long ending | Python engine | 0.090× | 2.95× | 0/32 | 32 |
| large module replace | Zig / rebar | 1.631× | 0.10× | 32/32 | 0 |
| large module replace | Native C engine | 1.515× | 0.06× | 32/32 | 0 |
| large module replace | Rust engine | 0.105× | 3.77× | 0/32 | 32 |
| large module replace | Python engine | 0.026× | 9.41× | 0/32 | 32 |
| large module search | Zig / rebar | 0.941× | 0.13× | 0/32 | 0 |
| large module search | Native C engine | 1.211× | 0.07× | 32/32 | 0 |
| large module search | Rust engine | 0.323× | 0.07× | 0/32 | 32 |
| large module search | Python engine | 0.076× | 4.34× | 0/32 | 32 |
| large nearby capture | Zig / rebar | 1.416× | 0.14× | 32/32 | 0 |
| large nearby capture | Native C engine | 2.015× | 0.08× | 32/32 | 0 |
| large nearby capture | Rust engine | 0.293× | 0.06× | 0/32 | 32 |
| large nearby capture | Python engine | 0.030× | 11.42× | 0/32 | 32 |
| large prefix check | Zig / rebar | 1.195× | 0.10× | 30/32 | 0 |
| large prefix check | Native C engine | 1.447× | 0.00× | 32/32 | 0 |
| large prefix check | Rust engine | 0.191× | 0.00× | 0/32 | 32 |
| large prefix check | Python engine | 0.034× | 3.81× | 0/32 | 32 |
| large references | Zig / rebar | 1.052× | 0.12× | 24/32 | 0 |
| large references | Native C engine | 1.336× | 0.00× | 32/32 | 0 |
| large references | Rust engine | 0.191× | 0.00× | 0/32 | 32 |
| large references | Python engine | 0.020× | 6.55× | 0/32 | 32 |
| large replace callback | Zig / rebar | 1.217× | 0.29× | 31/32 | 0 |
| large replace callback | Native C engine | 1.249× | 0.24× | 31/32 | 0 |
| large replace callback | Rust engine | 0.226× | 0.64× | 0/32 | 32 |
| large replace callback | Python engine | 0.079× | 3.20× | 0/32 | 32 |
| large replace groups | Zig / rebar | 1.897× | 0.18× | 32/32 | 0 |
| large replace groups | Native C engine | 2.221× | 0.14× | 32/32 | 0 |
| large replace groups | Rust engine | 0.087× | 3.63× | 0/32 | 32 |
| large replace groups | Python engine | 0.022× | 8.73× | 0/32 | 32 |
| large request records | Zig / rebar | 1.179× | 0.67× | 32/32 | 0 |
| large request records | Native C engine | 0.960× | 0.45× | 4/32 | 0 |
| large request records | Rust engine | 0.133× | 0.37× | 0/32 | 32 |
| large request records | Python engine | 0.017× | 7.45× | 0/32 | 32 |
| large scanner bytes | Zig / rebar | 1.288× | 0.69× | 32/32 | 0 |
| large scanner bytes | Native C engine | 1.380× | 0.45× | 32/32 | 0 |
| large scanner bytes | Rust engine | 0.089× | 0.36× | 0/32 | 32 |
| large scanner bytes | Python engine | 0.016× | 8.00× | 0/32 | 32 |
| large scanner text | Zig / rebar | 1.258× | 0.69× | 30/32 | 0 |
| large scanner text | Native C engine | 1.363× | 0.45× | 32/32 | 0 |
| large scanner text | Rust engine | 0.101× | 0.25× | 0/32 | 32 |
| large scanner text | Python engine | 0.017× | 7.71× | 0/32 | 32 |
| large split keep | Zig / rebar | 1.138× | 0.41× | 27/32 | 0 |
| large split keep | Native C engine | 1.350× | 0.42× | 32/32 | 0 |
| large split keep | Rust engine | 0.143× | 3.27× | 0/32 | 32 |
| large split keep | Python engine | 0.022× | 6.73× | 0/32 | 32 |
| large structured text | Zig / rebar | 1.854× | 0.33× | 32/32 | 0 |
| large structured text | Native C engine | 1.986× | 0.29× | 32/32 | 0 |
| large structured text | Rust engine | 0.070× | 2.18× | 0/32 | 32 |
| large structured text | Python engine | 0.010× | 18.64× | 0/32 | 32 |
| large unicode casefold | Zig / rebar | 2.009× | 0.40× | 32/32 | 0 |
| large unicode casefold | Native C engine | 1.561× | 0.41× | 31/32 | 0 |
| large unicode casefold | Rust engine | 0.068× | 1.24× | 0/32 | 32 |
| large unicode casefold | Python engine | 0.032× | 5.03× | 0/32 | 32 |
| large unicode words | Zig / rebar | 1.622× | 0.43× | 32/32 | 0 |
| large unicode words | Native C engine | 1.089× | 0.45× | 25/32 | 0 |
| large unicode words | Rust engine | 0.073× | 1.11× | 0/32 | 32 |
| large unicode words | Python engine | 0.023× | 6.58× | 0/32 | 32 |
| large verbose dotall | Zig / rebar | 2.659× | 0.15× | 32/32 | 0 |
| large verbose dotall | Native C engine | 2.212× | 0.09× | 32/32 | 0 |
| large verbose dotall | Rust engine | 0.123× | 0.06× | 0/32 | 32 |
| large verbose dotall | Python engine | 0.010× | 9.08× | 0/32 | 32 |
| large whole check | Zig / rebar | 1.822× | 0.06× | 32/32 | 0 |
| large whole check | Native C engine | 1.519× | 0.83× | 32/32 | 0 |
| large whole check | Rust engine | 0.098× | 0.00× | 0/32 | 32 |
| large whole check | Python engine | 0.015× | 15.26× | 0/32 | 32 |
| large window collection | Zig / rebar | 1.660× | 0.58× | 32/32 | 0 |
| large window collection | Native C engine | 1.700× | 0.45× | 32/32 | 0 |
| large window collection | Rust engine | 0.227× | 0.96× | 0/32 | 32 |
| large window collection | Python engine | 0.024× | 4.73× | 0/32 | 32 |
| large window search | Zig / rebar | 1.072× | 0.24× | 29/32 | 0 |
| large window search | Native C engine | 0.927× | 0.18× | 0/32 | 0 |
| large window search | Rust engine | 0.210× | 0.17× | 0/32 | 32 |
| large window search | Python engine | 0.038× | 3.96× | 0/32 | 32 |
| lines records | Zig / rebar | 1.215× | 0.61× | 1/1 | 0 |
| lines records | Native C engine | 1.553× | 0.38× | 1/1 | 0 |
| lines records | Rust engine | 0.147× | 0.33× | 0/1 | 1 |
| lines records | Python engine | 0.012× | 12.06× | 0/1 | 1 |
| literal replace | Zig / rebar | 1.168× | 0.71× | 1/1 | 0 |
| literal replace | Native C engine | 1.349× | 0.51× | 1/1 | 0 |
| literal replace | Rust engine | 0.262× | 0.62× | 0/1 | 1 |
| literal replace | Python engine | 0.048× | 8.20× | 0/1 | 1 |
| look negative ahead | Zig / rebar | 1.074× | 0.13× | 1/1 | 0 |
| look negative ahead | Native C engine | 1.074× | 0.14× | 1/1 | 0 |
| look negative ahead | Rust engine | 0.195× | 1.58× | 0/1 | 1 |
| look negative ahead | Python engine | 0.010× | 13.50× | 0/1 | 1 |
| look negative behind | Zig / rebar | 1.415× | 0.09× | 1/1 | 0 |
| look negative behind | Native C engine | 1.342× | 0.10× | 1/1 | 0 |
| look negative behind | Rust engine | 0.338× | 1.04× | 0/1 | 1 |
| look negative behind | Python engine | 0.021× | 6.99× | 0/1 | 1 |
| many results | Zig / rebar | 1.932× | 0.18× | 1/1 | 0 |
| many results | Native C engine | 1.327× | 0.20× | 1/1 | 0 |
| many results | Rust engine | 0.122× | 1.24× | 0/1 | 1 |
| many results | Python engine | 0.022× | 5.29× | 0/1 | 1 |
| match | Zig / rebar | 1.141× | 0.13× | 1/1 | 0 |
| match | Native C engine | 1.433× | 0.07× | 1/1 | 0 |
| match | Rust engine | 0.196× | 0.07× | 0/1 | 1 |
| match | Python engine | 0.028× | 4.26× | 0/1 | 1 |
| match miss | Zig / rebar | 1.075× | 0.04× | 0/1 | 0 |
| match miss | Native C engine | 1.186× | 0.00× | 1/1 | 0 |
| match miss | Rust engine | 0.209× | 0.00× | 0/1 | 1 |
| match miss | Python engine | 0.037× | 4.24× | 0/1 | 1 |
| match surface | Zig / rebar | 1.035× | 0.37× | 0/1 | 0 |
| match surface | Native C engine | 1.125× | 0.32× | 1/1 | 0 |
| match surface | Rust engine | 0.142× | 0.67× | 0/1 | 1 |
| match surface | Python engine | 0.058× | 8.76× | 0/1 | 1 |
| mode ascii | Zig / rebar | 1.450× | 0.19× | 1/1 | 0 |
| mode ascii | Native C engine | 1.204× | 0.21× | 1/1 | 0 |
| mode ascii | Rust engine | 0.093× | 0.94× | 0/1 | 1 |
| mode ascii | Python engine | 0.021× | 6.31× | 0/1 | 1 |
| mode astral | Zig / rebar | 1.649× | 0.23× | 1/1 | 0 |
| mode astral | Native C engine | 1.702× | 0.25× | 1/1 | 0 |
| mode astral | Rust engine | 0.109× | 0.92× | 0/1 | 1 |
| mode astral | Python engine | 0.027× | 5.40× | 0/1 | 1 |
| mode casefold | Zig / rebar | 1.490× | 0.18× | 1/1 | 0 |
| mode casefold | Native C engine | 1.585× | 0.18× | 1/1 | 0 |
| mode casefold | Rust engine | 0.133× | 0.92× | 0/1 | 1 |
| mode casefold | Python engine | 0.030× | 4.22× | 0/1 | 1 |
| module | Zig / rebar | 0.948× | 0.13× | 0/1 | 0 |
| module | Native C engine | 1.257× | 0.07× | 1/1 | 0 |
| module | Rust engine | 0.320× | 0.07× | 0/1 | 1 |
| module | Python engine | 0.075× | 4.29× | 0/1 | 1 |
| module replace | Zig / rebar | 1.323× | 0.09× | 1/1 | 0 |
| module replace | Native C engine | 1.231× | 0.04× | 1/1 | 0 |
| module replace | Rust engine | 0.106× | 1.48× | 0/1 | 1 |
| module replace | Python engine | 0.028× | 8.92× | 0/1 | 1 |
| pattern verbose | Zig / rebar | 3.180× | 0.15× | 1/1 | 0 |
| pattern verbose | Native C engine | 3.196× | 0.09× | 1/1 | 0 |
| pattern verbose | Rust engine | 0.109× | 0.06× | 0/1 | 1 |
| pattern verbose | Python engine | 0.008× | 14.89× | 0/1 | 1 |
| real comments | Zig / rebar | 1.074× | 0.13× | 1/1 | 0 |
| real comments | Native C engine | 1.272× | 0.14× | 1/1 | 0 |
| real comments | Rust engine | 0.218× | 2.33× | 0/1 | 1 |
| real comments | Python engine | 0.023× | 5.08× | 0/1 | 1 |
| real config | Zig / rebar | 1.589× | 0.60× | 1/1 | 0 |
| real config | Native C engine | 1.404× | 0.37× | 1/1 | 0 |
| real config | Rust engine | 0.096× | 0.32× | 0/1 | 1 |
| real config | Python engine | 0.013× | 17.74× | 0/1 | 1 |
| real csv | Zig / rebar | 3.033× | 0.28× | 1/1 | 0 |
| real csv | Native C engine | 2.498× | 0.30× | 1/1 | 0 |
| real csv | Rust engine | 0.091× | 1.75× | 0/1 | 1 |
| real csv | Python engine | 0.008× | 13.67× | 0/1 | 1 |
| real datetime | Zig / rebar | 1.426× | 0.14× | 1/1 | 0 |
| real datetime | Native C engine | 1.261× | 0.09× | 1/1 | 0 |
| real datetime | Rust engine | 0.203× | 0.06× | 0/1 | 1 |
| real datetime | Python engine | 0.011× | 21.76× | 0/1 | 1 |
| real email | Zig / rebar | 1.162× | 0.11× | 1/1 | 0 |
| real email | Native C engine | 1.278× | 0.12× | 1/1 | 0 |
| real email | Rust engine | 0.114× | 2.05× | 0/1 | 1 |
| real email | Python engine | 0.011× | 8.62× | 0/1 | 1 |
| real ip | Zig / rebar | 1.335× | 0.13× | 1/1 | 0 |
| real ip | Native C engine | 1.142× | 0.07× | 1/1 | 0 |
| real ip | Rust engine | 0.086× | 0.06× | 0/1 | 1 |
| real ip | Python engine | 0.010× | 25.53× | 0/1 | 1 |
| real lines | Zig / rebar | 1.720× | 0.20× | 1/1 | 0 |
| real lines | Native C engine | 1.916× | 0.14× | 1/1 | 0 |
| real lines | Rust engine | 0.226× | 1.17× | 0/1 | 1 |
| real lines | Python engine | 0.028× | 6.25× | 0/1 | 1 |
| real log | Zig / rebar | 1.083× | 0.59× | 1/1 | 0 |
| real log | Native C engine | 1.108× | 0.35× | 0/1 | 0 |
| real log | Rust engine | 0.164× | 0.32× | 0/1 | 1 |
| real log | Python engine | 0.022× | 7.39× | 0/1 | 1 |
| real markup | Zig / rebar | 0.929× | 0.13× | 0/1 | 0 |
| real markup | Native C engine | 1.205× | 0.13× | 1/1 | 0 |
| real markup | Rust engine | 0.160× | 4.80× | 0/1 | 1 |
| real markup | Python engine | 0.012× | 10.91× | 0/1 | 1 |
| real path | Zig / rebar | 1.532× | 0.11× | 1/1 | 0 |
| real path | Native C engine | 2.951× | 0.12× | 1/1 | 0 |
| real path | Rust engine | 0.090× | 2.14× | 0/1 | 1 |
| real path | Python engine | 0.008× | 29.92× | 0/1 | 1 |
| real quotes | Zig / rebar | 1.523× | 0.09× | 1/1 | 0 |
| real quotes | Native C engine | 1.454× | 0.10× | 1/1 | 0 |
| real quotes | Rust engine | 0.134× | 3.77× | 0/1 | 1 |
| real quotes | Python engine | 0.010× | 11.05× | 0/1 | 1 |
| real url | Zig / rebar | 1.427× | 0.16× | 1/1 | 0 |
| real url | Native C engine | 1.369× | 0.11× | 1/1 | 0 |
| real url | Rust engine | 0.050× | 0.06× | 0/1 | 1 |
| real url | Python engine | 0.015× | 17.65× | 0/1 | 1 |
| real uuid | Zig / rebar | 1.241× | 0.13× | 1/1 | 0 |
| real uuid | Native C engine | 1.424× | 0.07× | 1/1 | 0 |
| real uuid | Rust engine | 0.183× | 0.06× | 0/1 | 1 |
| real uuid | Python engine | 0.012× | 13.88× | 0/1 | 1 |
| real version | Zig / rebar | 1.436× | 0.12× | 1/1 | 0 |
| real version | Native C engine | 1.507× | 0.06× | 1/1 | 0 |
| real version | Rust engine | 0.131× | 0.06× | 0/1 | 1 |
| real version | Python engine | 0.014× | 18.50× | 0/1 | 1 |
| real whitespace | Zig / rebar | 1.424× | 0.19× | 1/1 | 0 |
| real whitespace | Native C engine | 1.461× | 0.14× | 1/1 | 0 |
| real whitespace | Rust engine | 0.198× | 1.20× | 0/1 | 1 |
| real whitespace | Python engine | 0.036× | 3.91× | 0/1 | 1 |
| repeat nested | Zig / rebar | 1.891× | 0.06× | 1/1 | 0 |
| repeat nested | Native C engine | 1.420× | 0.64× | 1/1 | 0 |
| repeat nested | Rust engine | 0.091× | 0.03× | 0/1 | 1 |
| repeat nested | Python engine | 0.013× | 13.69× | 0/1 | 1 |
| replace limited | Zig / rebar | 1.477× | 0.21× | 1/1 | 0 |
| replace limited | Native C engine | 1.418× | 0.15× | 1/1 | 0 |
| replace limited | Rust engine | 0.164× | 1.21× | 0/1 | 1 |
| replace limited | Python engine | 0.033× | 3.81× | 0/1 | 1 |
| scanner | Zig / rebar | 1.092× | 0.64× | 1/1 | 0 |
| scanner | Native C engine | 1.344× | 0.38× | 1/1 | 0 |
| scanner | Rust engine | 0.117× | 0.22× | 0/1 | 1 |
| scanner | Python engine | 0.021× | 5.82× | 0/1 | 1 |
| search boundary | Zig / rebar | 10.701× | 0.13× | 1/1 | 0 |
| search boundary | Native C engine | 17.272× | 0.07× | 1/1 | 0 |
| search boundary | Rust engine | 0.302× | 0.07× | 0/1 | 1 |
| search boundary | Python engine | 0.354× | 2.98× | 0/1 | 1 |
| search class | Zig / rebar | 1.231× | 0.13× | 1/1 | 0 |
| search class | Native C engine | 1.381× | 0.07× | 1/1 | 0 |
| search class | Rust engine | 0.226× | 0.07× | 0/1 | 1 |
| search class | Python engine | 0.029× | 5.34× | 0/1 | 1 |
| search hit | Zig / rebar | 0.853× | 1.33× | 0/1 | 0 |
| search hit | Native C engine | 1.112× | 0.73× | 1/1 | 0 |
| search hit | Rust engine | 0.150× | 0.67× | 0/1 | 1 |
| search hit | Python engine | 0.043× | 20.93× | 0/1 | 1 |
| search miss | Zig / rebar | 0.888× | 48.00× | 0/1 | 0 |
| search miss | Native C engine | 1.184× | 0.00× | 1/1 | 0 |
| search miss | Rust engine | 0.176× | 0.00× | 0/1 | 1 |
| search miss | Python engine | 0.137× | 112.00× | 0/1 | 1 |
| split | Zig / rebar | 1.330× | 0.19× | 1/1 | 0 |
| split | Native C engine | 1.812× | 0.20× | 1/1 | 0 |
| split | Rust engine | 0.103× | 1.29× | 0/1 | 1 |
| split | Python engine | 0.017× | 7.83× | 0/1 | 1 |
| split limited | Zig / rebar | 1.537× | 0.17× | 1/1 | 0 |
| split limited | Native C engine | 1.501× | 0.19× | 1/1 | 0 |
| split limited | Rust engine | 0.114× | 1.22× | 0/1 | 1 |
| split limited | Python engine | 0.017× | 6.35× | 0/1 | 1 |
| sub | Zig / rebar | 1.833× | 0.17× | 1/1 | 0 |
| sub | Native C engine | 2.031× | 0.12× | 1/1 | 0 |
| sub | Rust engine | 0.084× | 1.51× | 0/1 | 1 |
| sub | Python engine | 0.021× | 8.20× | 0/1 | 1 |
| subn callable | Zig / rebar | 1.123× | 0.31× | 1/1 | 0 |
| subn callable | Native C engine | 1.105× | 0.25× | 1/1 | 0 |
| subn callable | Rust engine | 0.197× | 0.53× | 0/1 | 1 |
| subn callable | Python engine | 0.061× | 3.32× | 0/1 | 1 |
| template repeat | Zig / rebar | 1.426× | 0.19× | 1/1 | 0 |
| template repeat | Native C engine | 1.758× | 0.14× | 1/1 | 0 |
| template repeat | Rust engine | 0.086× | 1.11× | 0/1 | 1 |
| template repeat | Python engine | 0.028× | 5.39× | 0/1 | 1 |
| unicode | Zig / rebar | 1.522× | 0.20× | 1/1 | 0 |
| unicode | Native C engine | 1.674× | 0.20× | 1/1 | 0 |
| unicode | Rust engine | 0.116× | 0.87× | 0/1 | 1 |
| unicode | Python engine | 0.026× | 5.49× | 0/1 | 1 |
| unicode name | Zig / rebar | 1.234× | 0.13× | 1/1 | 0 |
| unicode name | Native C engine | 1.496× | 0.07× | 1/1 | 0 |
| unicode name | Rust engine | 0.192× | 0.10× | 0/1 | 1 |
| unicode name | Python engine | 0.047× | 3.17× | 0/1 | 1 |
| window findall | Zig / rebar | 1.166× | 0.25× | 1/1 | 0 |
| window findall | Native C engine | 1.090× | 0.22× | 1/1 | 0 |
| window findall | Rust engine | 0.347× | 0.67× | 0/1 | 1 |
| window findall | Python engine | 0.028× | 3.74× | 0/1 | 1 |
| window match | Zig / rebar | 0.967× | 0.24× | 0/1 | 0 |
| window match | Native C engine | 1.015× | 0.18× | 1/1 | 0 |
| window match | Rust engine | 0.219× | 0.17× | 0/1 | 1 |
| window match | Python engine | 0.035× | 3.89× | 0/1 | 1 |
| window scanner | Zig / rebar | 1.150× | 0.62× | 1/1 | 0 |
| window scanner | Native C engine | 1.199× | 0.33× | 1/1 | 0 |
| window scanner | Rust engine | 0.147× | 0.20× | 0/1 | 1 |
| window scanner | Python engine | 0.028× | 3.92× | 0/1 | 1 |
| window search | Zig / rebar | 1.085× | 0.24× | 1/1 | 0 |
| window search | Native C engine | 0.906× | 0.18× | 0/1 | 0 |
| window search | Rust engine | 0.227× | 0.17× | 0/1 | 1 |
| window search | Python engine | 0.041× | 3.92× | 0/1 | 1 |
| zero boundary | Zig / rebar | 2.885× | 0.68× | 1/1 | 0 |
| zero boundary | Native C engine | 2.320× | 0.43× | 1/1 | 0 |
| zero boundary | Rust engine | 0.177× | 0.43× | 0/1 | 1 |
| zero boundary | Python engine | 0.014× | 11.03× | 0/1 | 1 |

The compressed summary contains every individual practice/holdout result and every candidate slowdown; the compressed raw file contains all paired rows, order, operation count, correctness digest, and memory observations.
