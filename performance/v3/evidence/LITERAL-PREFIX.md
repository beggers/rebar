# Rejected native literal-prefix experiment

All 7488 raw timing rows, 432 engine/task results, and 301 large slowdowns are retained. Raw SHA-256: `c02c54c13d1536210dd43505c4e34c6b7a430d164309da97be899b30725404f4`.

## At a glance

The holdout tasks were kept separate from tuning. **1× means the same speed as Python `re`; higher is faster.** A result is clearly faster only when its measured range stays above 1×. A large slowdown means more than 20% slower.

| Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: | ---: |
| Native C engine | **1.0908×** | 1.0837–1.0977× | 46/72 | 12/72 |
| Rust engine | **0.0137×** | 0.0136–0.0137× | 2/72 | 69/72 |
| Python engine | **0.0116×** | 0.0116–0.0117× | 3/72 | 69/72 |

## Overall results

| Task set | Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |
| --- | --- | ---: | ---: | ---: | ---: |
| Practice | Python engine | 0.0114× | 0.0114–0.0115× | 2/72 | 69 |
| Practice | Native C engine | 1.0675× | 1.0617–1.0733× | 41/72 | 13 |
| Practice | Rust engine | 0.0136× | 0.0136–0.0137× | 2/72 | 69 |
| Holdout | Python engine | 0.0116× | 0.0116–0.0117× | 3/72 | 69 |
| Holdout | Native C engine | 1.0908× | 1.0837–1.0977× | 46/72 | 12 |
| Holdout | Rust engine | 0.0137× | 0.0136–0.0137× | 2/72 | 69 |
| All | Python engine | 0.0115× | 0.0115–0.0116× | 5/144 | 138 |
| All | Native C engine | 1.0791× | 1.0747–1.0836× | 87/144 | 25 |
| All | Rust engine | 0.0136× | 0.0136–0.0137× | 4/144 | 138 |

## Every task

`FASTER` means the measured range stays above 1×. `SLOWER` means more than 20% slower. Memory compares median traced Python memory with Python `re`.

| Task set | Task | Engine | Speed | Measured range | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Practice | `cal.search.literal.hit` | Python engine | 0.0074× | 0.0072–0.0075× | 102.00× | SLOWER |
| Practice | `cal.search.literal.hit` | Native C engine | 1.1124× | 1.1054–1.1196× | 0.73× | FASTER |
| Practice | `cal.search.literal.hit` | Rust engine | 0.0085× | 0.0085–0.0086× | 34.03× | SLOWER |
| Practice | `cal.search.literal.miss` | Python engine | 0.0023× | 0.0022–0.0025× | 14408.00× | SLOWER |
| Practice | `cal.search.literal.miss` | Native C engine | 1.2017× | 1.1442–1.3163× | 0.00× | FASTER |
| Practice | `cal.search.literal.miss` | Rust engine | 0.0058× | 0.0056–0.0063× | 4375.00× | SLOWER |
| Practice | `cal.search.long-boundary` | Python engine | 0.0003× | 0.0003–0.0003× | 129.57× | SLOWER |
| Practice | `cal.search.long-boundary` | Native C engine | 10.7420× | 10.0951–11.5412× | 0.07× | FASTER |
| Practice | `cal.search.long-boundary` | Rust engine | 0.0010× | 0.0009–0.0010× | 140.03× | SLOWER |
| Practice | `cal.search.class-anchor` | Python engine | 0.0111× | 0.0109–0.0113× | 11.57× | SLOWER |
| Practice | `cal.search.class-anchor` | Native C engine | 0.9900× | 0.9731–1.0081× | 0.07× | — |
| Practice | `cal.search.class-anchor` | Rust engine | 0.0146× | 0.0143–0.0149× | 3.36× | SLOWER |
| Practice | `cal.match.prefix` | Python engine | 0.0236× | 0.0229–0.0250× | 3.87× | SLOWER |
| Practice | `cal.match.prefix` | Native C engine | 1.1145× | 1.0741–1.1834× | 0.07× | FASTER |
| Practice | `cal.match.prefix` | Rust engine | 0.0152× | 0.0147–0.0161× | 2.89× | SLOWER |
| Practice | `cal.fullmatch.structured` | Python engine | 0.0126× | 0.0124–0.0128× | 12.07× | SLOWER |
| Practice | `cal.fullmatch.structured` | Native C engine | 1.0336× | 1.0182–1.0507× | 0.07× | FASTER |
| Practice | `cal.fullmatch.structured` | Rust engine | 0.0184× | 0.0181–0.0186× | 3.04× | SLOWER |
| Practice | `cal.search.look-capture` | Python engine | 0.0078× | 0.0076–0.0081× | 17.28× | SLOWER |
| Practice | `cal.search.look-capture` | Native C engine | 1.2422× | 1.2069–1.2991× | 0.08× | FASTER |
| Practice | `cal.search.look-capture` | Rust engine | 0.0167× | 0.0162–0.0175× | 3.29× | SLOWER |
| Practice | `cal.findall.tokens` | Python engine | 0.0102× | 0.0100–0.0104× | 7.14× | SLOWER |
| Practice | `cal.findall.tokens` | Native C engine | 0.9860× | 0.9756–0.9968× | 0.28× | — |
| Practice | `cal.findall.tokens` | Rust engine | 0.0038× | 0.0037–0.0039× | 3.26× | SLOWER |
| Practice | `cal.finditer.groups` | Python engine | 0.0129× | 0.0126–0.0133× | 7.75× | SLOWER |
| Practice | `cal.finditer.groups` | Native C engine | 1.4597× | 1.4154–1.5001× | 0.39× | FASTER |
| Practice | `cal.finditer.groups` | Rust engine | 0.0098× | 0.0096–0.0101× | 1.91× | SLOWER |
| Practice | `cal.split.capture` | Python engine | 0.0098× | 0.0098–0.0099× | 11.37× | SLOWER |
| Practice | `cal.split.capture` | Native C engine | 1.7436× | 1.7163–1.7727× | 0.20× | FASTER |
| Practice | `cal.split.capture` | Rust engine | 0.0067× | 0.0066–0.0067× | 2.62× | SLOWER |
| Practice | `cal.sub.template` | Python engine | 0.0158× | 0.0157–0.0160× | 9.30× | SLOWER |
| Practice | `cal.sub.template` | Native C engine | 1.8171× | 1.7963–1.8379× | 0.12× | FASTER |
| Practice | `cal.sub.template` | Rust engine | 0.0146× | 0.0145–0.0148× | 2.39× | SLOWER |
| Practice | `cal.subn.callable` | Python engine | 0.0244× | 0.0231–0.0269× | 5.05× | SLOWER |
| Practice | `cal.subn.callable` | Native C engine | 1.1011× | 1.0389–1.2192× | 0.25× | FASTER |
| Practice | `cal.subn.callable` | Rust engine | 0.0192× | 0.0182–0.0204× | 2.56× | SLOWER |
| Practice | `cal.bytes.tokens` | Python engine | 0.0073× | 0.0073–0.0074× | 8.29× | SLOWER |
| Practice | `cal.bytes.tokens` | Native C engine | 1.0392× | 1.0318–1.0461× | 0.12× | FASTER |
| Practice | `cal.bytes.tokens` | Rust engine | 0.0055× | 0.0055–0.0055× | 3.43× | SLOWER |
| Practice | `cal.unicode.words` | Python engine | 0.0062× | 0.0061–0.0064× | 6.52× | SLOWER |
| Practice | `cal.unicode.words` | Native C engine | 0.9297× | 0.9093–0.9625× | 0.20× | — |
| Practice | `cal.unicode.words` | Rust engine | 0.0098× | 0.0096–0.0101× | 2.69× | SLOWER |
| Practice | `cal.cold.compile-search` | Python engine | 0.2959× | 0.2930–0.2993× | 5.84× | SLOWER |
| Practice | `cal.cold.compile-search` | Native C engine | 0.7407× | 0.7353–0.7480× | 1.50× | SLOWER |
| Practice | `cal.cold.compile-search` | Rust engine | 0.6983× | 0.6847–0.7114× | 1.95× | SLOWER |
| Practice | `cal.module.warm` | Python engine | 0.0104× | 0.0103–0.0107× | 7.21× | SLOWER |
| Practice | `cal.module.warm` | Native C engine | 1.1897× | 1.1660–1.2177× | 0.07× | FASTER |
| Practice | `cal.module.warm` | Rust engine | 0.0309× | 0.0303–0.0316× | 3.39× | SLOWER |
| Practice | `cal.empty.finditer` | Python engine | 0.0098× | 0.0096–0.0100× | 8.09× | SLOWER |
| Practice | `cal.empty.finditer` | Native C engine | 0.6934× | 0.6724–0.7122× | 0.59× | SLOWER |
| Practice | `cal.empty.finditer` | Rust engine | 0.0210× | 0.0207–0.0215× | 1.67× | SLOWER |
| Practice | `cal.backref.fullmatch` | Python engine | 0.0184× | 0.0182–0.0186× | 6.99× | SLOWER |
| Practice | `cal.backref.fullmatch` | Native C engine | 1.0774× | 1.0654–1.0905× | 0.08× | FASTER |
| Practice | `cal.backref.fullmatch` | Rust engine | 0.0180× | 0.0176–0.0183× | 3.04× | SLOWER |
| Practice | `cal.conditional.match` | Python engine | 0.0178× | 0.0176–0.0179× | 6.78× | SLOWER |
| Practice | `cal.conditional.match` | Native C engine | 1.1520× | 1.1398–1.1635× | 0.08× | FASTER |
| Practice | `cal.conditional.match` | Rust engine | 0.0160× | 0.0159–0.0162× | 2.97× | SLOWER |
| Practice | `cal.atomic.search` | Python engine | 0.0095× | 0.0094–0.0096× | 8.80× | SLOWER |
| Practice | `cal.atomic.search` | Native C engine | 0.9810× | 0.9730–0.9890× | 0.50× | — |
| Practice | `cal.atomic.search` | Rust engine | 0.0184× | 0.0182–0.0186× | 3.14× | SLOWER |
| Practice | `cal.byteslike.findall` | Python engine | 0.0111× | 0.0106–0.0121× | 7.48× | SLOWER |
| Practice | `cal.byteslike.findall` | Native C engine | 2.0879× | 1.9625–2.2932× | 0.18× | FASTER |
| Practice | `cal.byteslike.findall` | Rust engine | 0.0081× | 0.0077–0.0089× | 2.93× | SLOWER |
| Practice | `cal.unicode-name.search` | Python engine | 0.0138× | 0.0136–0.0139× | 4.37× | SLOWER |
| Practice | `cal.unicode-name.search` | Native C engine | 1.2612× | 1.2446–1.2777× | 0.07× | FASTER |
| Practice | `cal.unicode-name.search` | Rust engine | 0.0188× | 0.0186–0.0190× | 3.14× | SLOWER |
| Practice | `cal.ignorecase.findall` | Python engine | 0.0073× | 0.0073–0.0074× | 5.14× | SLOWER |
| Practice | `cal.ignorecase.findall` | Native C engine | 1.2394× | 1.2324–1.2486× | 0.16× | FASTER |
| Practice | `cal.ignorecase.findall` | Rust engine | 0.0083× | 0.0082–0.0084× | 2.96× | SLOWER |
| Practice | `cal.many.split` | Python engine | 0.0126× | 0.0122–0.0132× | 8.86× | SLOWER |
| Practice | `cal.many.split` | Native C engine | 1.2475× | 1.2106–1.2976× | 0.20× | FASTER |
| Practice | `cal.many.split` | Rust engine | 0.0046× | 0.0045–0.0048× | 2.86× | SLOWER |
| Practice | `cal.escape.text` | Python engine | 1.0045× | 0.9744–1.0529× | 1.00× | — |
| Practice | `cal.escape.text` | Native C engine | 1.0061× | 0.9784–1.0538× | 1.00× | — |
| Practice | `cal.escape.text` | Rust engine | 0.9607× | 0.8643–1.0399× | 1.00× | — |
| Practice | `cal.compile.only` | Python engine | 2.2013× | 2.1722–2.2287× | 0.50× | FASTER |
| Practice | `cal.compile.only` | Native C engine | 1.6422× | 1.6095–1.6698× | 1.41× | FASTER |
| Practice | `cal.compile.only` | Rust engine | 1.7184× | 1.6668–1.7619× | 0.56× | FASTER |
| Practice | `cal.scanner.search` | Python engine | 0.0129× | 0.0128–0.0130× | 6.71× | SLOWER |
| Practice | `cal.scanner.search` | Native C engine | 1.0309× | 1.0144–1.0447× | 0.36× | FASTER |
| Practice | `cal.scanner.search` | Rust engine | 0.0086× | 0.0084–0.0087× | 1.98× | SLOWER |
| Practice | `cal.match.surface` | Python engine | 0.0143× | 0.0140–0.0146× | 12.88× | SLOWER |
| Practice | `cal.match.surface` | Native C engine | 1.2363× | 1.1693–1.2974× | 0.32× | FASTER |
| Practice | `cal.match.surface` | Rust engine | 0.0479× | 0.0471–0.0489× | 3.26× | SLOWER |
| Holdout | `hold.search.literal.hit` | Python engine | 0.0078× | 0.0076–0.0079× | 102.00× | SLOWER |
| Holdout | `hold.search.literal.hit` | Native C engine | 1.1696× | 1.1407–1.1983× | 0.73× | FASTER |
| Holdout | `hold.search.literal.hit` | Rust engine | 0.0095× | 0.0093–0.0097× | 33.96× | SLOWER |
| Holdout | `hold.search.literal.miss` | Python engine | 0.0025× | 0.0024–0.0026× | 14408.00× | SLOWER |
| Holdout | `hold.search.literal.miss` | Native C engine | 1.2173× | 1.1733–1.2846× | 0.00× | FASTER |
| Holdout | `hold.search.literal.miss` | Rust engine | 0.0059× | 0.0057–0.0062× | 4375.00× | SLOWER |
| Holdout | `hold.search.long-boundary` | Python engine | 0.0003× | 0.0003–0.0003× | 130.58× | SLOWER |
| Holdout | `hold.search.long-boundary` | Native C engine | 15.6742× | 14.1289–17.4899× | 0.07× | FASTER |
| Holdout | `hold.search.long-boundary` | Rust engine | 0.0010× | 0.0009–0.0011× | 218.22× | SLOWER |
| Holdout | `hold.search.class-anchor` | Python engine | 0.0105× | 0.0098–0.0116× | 11.17× | SLOWER |
| Holdout | `hold.search.class-anchor` | Native C engine | 0.9517× | 0.8238–1.0565× | 0.07× | — |
| Holdout | `hold.search.class-anchor` | Rust engine | 0.0142× | 0.0133–0.0157× | 3.39× | SLOWER |
| Holdout | `hold.match.prefix` | Python engine | 0.0245× | 0.0243–0.0247× | 3.87× | SLOWER |
| Holdout | `hold.match.prefix` | Native C engine | 1.1385× | 1.1311–1.1460× | 0.07× | FASTER |
| Holdout | `hold.match.prefix` | Rust engine | 0.0155× | 0.0146–0.0160× | 2.87× | SLOWER |
| Holdout | `hold.fullmatch.structured` | Python engine | 0.0114× | 0.0113–0.0114× | 16.36× | SLOWER |
| Holdout | `hold.fullmatch.structured` | Native C engine | 1.0367× | 1.0267–1.0452× | 0.07× | FASTER |
| Holdout | `hold.fullmatch.structured` | Rust engine | 0.0193× | 0.0192–0.0194× | 3.04× | SLOWER |
| Holdout | `hold.search.look-capture` | Python engine | 0.0097× | 0.0095–0.0099× | 17.64× | SLOWER |
| Holdout | `hold.search.look-capture` | Native C engine | 0.9157× | 0.9068–0.9253× | 0.17× | — |
| Holdout | `hold.search.look-capture` | Rust engine | 0.0169× | 0.0165–0.0172× | 3.26× | SLOWER |
| Holdout | `hold.findall.tokens` | Python engine | 0.0111× | 0.0106–0.0116× | 11.27× | SLOWER |
| Holdout | `hold.findall.tokens` | Native C engine | 1.4527× | 1.3931–1.5308× | 0.21× | FASTER |
| Holdout | `hold.findall.tokens` | Rust engine | 0.0061× | 0.0059–0.0063× | 3.10× | SLOWER |
| Holdout | `hold.finditer.groups` | Python engine | 0.0135× | 0.0128–0.0145× | 7.75× | SLOWER |
| Holdout | `hold.finditer.groups` | Native C engine | 1.4514× | 1.3568–1.5572× | 0.39× | FASTER |
| Holdout | `hold.finditer.groups` | Rust engine | 0.0095× | 0.0090–0.0102× | 1.93× | SLOWER |
| Holdout | `hold.split.capture` | Python engine | 0.0100× | 0.0098–0.0102× | 11.37× | SLOWER |
| Holdout | `hold.split.capture` | Native C engine | 1.6357× | 1.4951–1.7258× | 0.20× | FASTER |
| Holdout | `hold.split.capture` | Rust engine | 0.0067× | 0.0066–0.0069× | 2.62× | SLOWER |
| Holdout | `hold.sub.template` | Python engine | 0.0162× | 0.0159–0.0165× | 9.29× | SLOWER |
| Holdout | `hold.sub.template` | Native C engine | 1.8493× | 1.8206–1.8843× | 0.12× | FASTER |
| Holdout | `hold.sub.template` | Rust engine | 0.0148× | 0.0146–0.0151× | 2.39× | SLOWER |
| Holdout | `hold.subn.callable` | Python engine | 0.0268× | 0.0262–0.0277× | 4.58× | SLOWER |
| Holdout | `hold.subn.callable` | Native C engine | 1.0731× | 1.0362–1.1093× | 0.25× | FASTER |
| Holdout | `hold.subn.callable` | Rust engine | 0.0215× | 0.0210–0.0222× | 2.53× | SLOWER |
| Holdout | `hold.bytes.tokens` | Python engine | 0.0103× | 0.0101–0.0106× | 8.71× | SLOWER |
| Holdout | `hold.bytes.tokens` | Native C engine | 2.1908× | 2.1414–2.2500× | 0.18× | FASTER |
| Holdout | `hold.bytes.tokens` | Rust engine | 0.0083× | 0.0081–0.0086× | 2.92× | SLOWER |
| Holdout | `hold.unicode.words` | Python engine | 0.0087× | 0.0084–0.0093× | 6.63× | SLOWER |
| Holdout | `hold.unicode.words` | Native C engine | 1.5311× | 1.4679–1.6424× | 0.20× | FASTER |
| Holdout | `hold.unicode.words` | Rust engine | 0.0117× | 0.0113–0.0125× | 2.67× | SLOWER |
| Holdout | `hold.cold.compile-search` | Python engine | 0.4839× | 0.4792–0.4885× | 5.95× | SLOWER |
| Holdout | `hold.cold.compile-search` | Native C engine | 0.7993× | 0.7896–0.8085× | 1.56× | SLOWER |
| Holdout | `hold.cold.compile-search` | Rust engine | 0.7345× | 0.7253–0.7428× | 1.93× | SLOWER |
| Holdout | `hold.module.warm` | Python engine | 0.0192× | 0.0190–0.0193× | 7.12× | SLOWER |
| Holdout | `hold.module.warm` | Native C engine | 1.1053× | 1.0834–1.1230× | 0.07× | FASTER |
| Holdout | `hold.module.warm` | Rust engine | 0.0312× | 0.0309–0.0314× | 3.38× | SLOWER |
| Holdout | `hold.empty.finditer` | Python engine | 0.0091× | 0.0089–0.0093× | 8.52× | SLOWER |
| Holdout | `hold.empty.finditer` | Native C engine | 0.6452× | 0.6175–0.6685× | 0.61× | SLOWER |
| Holdout | `hold.empty.finditer` | Rust engine | 0.0213× | 0.0209–0.0217× | 1.62× | SLOWER |
| Holdout | `hold.backref.fullmatch` | Python engine | 0.0181× | 0.0179–0.0184× | 6.99× | SLOWER |
| Holdout | `hold.backref.fullmatch` | Native C engine | 1.0194× | 0.9141–1.0900× | 0.08× | — |
| Holdout | `hold.backref.fullmatch` | Rust engine | 0.0192× | 0.0188–0.0195× | 3.04× | SLOWER |
| Holdout | `hold.conditional.match` | Python engine | 0.0195× | 0.0185–0.0212× | 6.78× | SLOWER |
| Holdout | `hold.conditional.match` | Native C engine | 1.1894× | 1.1297–1.2974× | 0.08× | FASTER |
| Holdout | `hold.conditional.match` | Rust engine | 0.0193× | 0.0183–0.0210× | 2.94× | SLOWER |
| Holdout | `hold.atomic.search` | Python engine | 0.0121× | 0.0108–0.0137× | 6.53× | SLOWER |
| Holdout | `hold.atomic.search` | Native C engine | 1.4211× | 1.2214–1.6451× | 0.07× | FASTER |
| Holdout | `hold.atomic.search` | Rust engine | 0.0245× | 0.0223–0.0270× | 3.13× | SLOWER |
| Holdout | `hold.byteslike.findall` | Python engine | 0.0115× | 0.0109–0.0121× | 7.39× | SLOWER |
| Holdout | `hold.byteslike.findall` | Native C engine | 2.1426× | 2.0384–2.2807× | 0.18× | FASTER |
| Holdout | `hold.byteslike.findall` | Rust engine | 0.0083× | 0.0080–0.0088× | 2.83× | SLOWER |
| Holdout | `hold.unicode-name.search` | Python engine | 0.0139× | 0.0138–0.0140× | 4.69× | SLOWER |
| Holdout | `hold.unicode-name.search` | Native C engine | 1.4136× | 1.4045–1.4229× | 0.07× | FASTER |
| Holdout | `hold.unicode-name.search` | Rust engine | 0.0207× | 0.0206–0.0208× | 3.14× | SLOWER |
| Holdout | `hold.ignorecase.findall` | Python engine | 0.0075× | 0.0074–0.0077× | 4.86× | SLOWER |
| Holdout | `hold.ignorecase.findall` | Native C engine | 1.2591× | 1.2379–1.2909× | 0.16× | FASTER |
| Holdout | `hold.ignorecase.findall` | Rust engine | 0.0091× | 0.0089–0.0093× | 2.94× | SLOWER |
| Holdout | `hold.many.split` | Python engine | 0.0127× | 0.0125–0.0128× | 8.86× | SLOWER |
| Holdout | `hold.many.split` | Native C engine | 1.2439× | 1.2243–1.2623× | 0.20× | FASTER |
| Holdout | `hold.many.split` | Rust engine | 0.0046× | 0.0046–0.0047× | 2.86× | SLOWER |
| Holdout | `hold.escape.bytes` | Python engine | 1.0581× | 1.0055–1.1485× | 0.68× | FASTER |
| Holdout | `hold.escape.bytes` | Native C engine | 1.0382× | 1.0065–1.0823× | 0.68× | FASTER |
| Holdout | `hold.escape.bytes` | Rust engine | 1.0531× | 0.9994–1.1475× | 0.68× | — |
| Holdout | `hold.compile.only` | Python engine | 1.9696× | 1.9364–1.9980× | 0.54× | FASTER |
| Holdout | `hold.compile.only` | Native C engine | 1.3675× | 1.3464–1.3856× | 1.91× | FASTER |
| Holdout | `hold.compile.only` | Rust engine | 1.6493× | 1.6276–1.6692× | 0.60× | FASTER |
| Holdout | `hold.scanner.search` | Python engine | 0.0129× | 0.0128–0.0131× | 6.71× | SLOWER |
| Holdout | `hold.scanner.search` | Native C engine | 1.0357× | 1.0185–1.0490× | 0.36× | FASTER |
| Holdout | `hold.scanner.search` | Rust engine | 0.0087× | 0.0086–0.0088× | 1.98× | SLOWER |
| Holdout | `hold.match.surface` | Python engine | 0.0210× | 0.0208–0.0213× | 12.79× | SLOWER |
| Holdout | `hold.match.surface` | Native C engine | 1.0459× | 1.0233–1.0674× | 0.32× | FASTER |
| Holdout | `hold.match.surface` | Rust engine | 0.0412× | 0.0407–0.0417× | 3.25× | SLOWER |
| Practice | `cal.real.log` | Python engine | 0.0030× | 0.0029–0.0031× | 27.33× | SLOWER |
| Practice | `cal.real.log` | Native C engine | 0.8834× | 0.8511–0.9174× | 0.33× | — |
| Practice | `cal.real.log` | Rust engine | 0.0062× | 0.0060–0.0064× | 3.19× | SLOWER |
| Practice | `cal.real.url` | Python engine | 0.0064× | 0.0062–0.0068× | 26.38× | SLOWER |
| Practice | `cal.real.url` | Native C engine | 0.8903× | 0.8562–0.9467× | 0.11× | — |
| Practice | `cal.real.url` | Rust engine | 0.0121× | 0.0116–0.0129× | 3.49× | SLOWER |
| Practice | `cal.real.email` | Python engine | 0.0055× | 0.0055–0.0056× | 9.90× | SLOWER |
| Practice | `cal.real.email` | Native C engine | 0.6516× | 0.6444–0.6583× | 0.12× | SLOWER |
| Practice | `cal.real.email` | Rust engine | 0.0062× | 0.0061–0.0062× | 3.85× | SLOWER |
| Practice | `cal.real.datetime` | Python engine | 0.0077× | 0.0075–0.0081× | 23.68× | SLOWER |
| Practice | `cal.real.datetime` | Native C engine | 0.9337× | 0.9053–0.9746× | 0.09× | — |
| Practice | `cal.real.datetime` | Rust engine | 0.0159× | 0.0155–0.0166× | 3.49× | SLOWER |
| Practice | `cal.real.version` | Python engine | 0.0114× | 0.0108–0.0126× | 22.95× | SLOWER |
| Practice | `cal.real.version` | Native C engine | 1.4997× | 1.4207–1.6547× | 0.00× | FASTER |
| Practice | `cal.real.version` | Rust engine | 0.0300× | 0.0284–0.0331× | 3.46× | SLOWER |
| Practice | `cal.real.uuid` | Python engine | 0.0064× | 0.0063–0.0064× | 18.66× | SLOWER |
| Practice | `cal.real.uuid` | Native C engine | 0.8047× | 0.7908–0.8169× | 0.07× | — |
| Practice | `cal.real.uuid` | Rust engine | 0.0135× | 0.0134–0.0136× | 3.96× | SLOWER |
| Practice | `cal.real.ip` | Python engine | 0.0079× | 0.0078–0.0081× | 29.12× | SLOWER |
| Practice | `cal.real.ip` | Native C engine | 1.0029× | 0.9907–1.0172× | 0.07× | — |
| Practice | `cal.real.ip` | Rust engine | 0.0262× | 0.0259–0.0266× | 3.02× | SLOWER |
| Practice | `cal.real.path` | Python engine | 0.0057× | 0.0056–0.0058× | 30.63× | SLOWER |
| Practice | `cal.real.path` | Native C engine | 0.8952× | 0.8739–0.9112× | 0.12× | — |
| Practice | `cal.real.path` | Rust engine | 0.0106× | 0.0106–0.0107× | 3.60× | SLOWER |
| Practice | `cal.real.config` | Python engine | 0.0083× | 0.0082–0.0085× | 16.04× | SLOWER |
| Practice | `cal.real.config` | Native C engine | 1.0410× | 1.0106–1.0695× | 0.35× | FASTER |
| Practice | `cal.real.config` | Rust engine | 0.0171× | 0.0167–0.0174× | 2.32× | SLOWER |
| Practice | `cal.real.comments` | Python engine | 0.0060× | 0.0060–0.0061× | 11.73× | SLOWER |
| Practice | `cal.real.comments` | Native C engine | 0.7620× | 0.7310–0.7808× | 0.14× | SLOWER |
| Practice | `cal.real.comments` | Rust engine | 0.0037× | 0.0037–0.0038× | 3.74× | SLOWER |
| Practice | `cal.real.whitespace` | Python engine | 0.0066× | 0.0065–0.0067× | 8.36× | SLOWER |
| Practice | `cal.real.whitespace` | Native C engine | 1.3070× | 1.2953–1.3199× | 0.14× | FASTER |
| Practice | `cal.real.whitespace` | Rust engine | 0.0074× | 0.0072–0.0075× | 2.79× | SLOWER |
| Practice | `cal.real.lines` | Python engine | 0.0095× | 0.0093–0.0099× | 14.09× | SLOWER |
| Practice | `cal.real.lines` | Native C engine | 1.6214× | 1.5522–1.7024× | 0.15× | FASTER |
| Practice | `cal.real.lines` | Rust engine | 0.0093× | 0.0092–0.0095× | 2.83× | SLOWER |
| Practice | `cal.real.markup` | Python engine | 0.0045× | 0.0045–0.0045× | 13.23× | SLOWER |
| Practice | `cal.real.markup` | Native C engine | 0.6073× | 0.5866–0.6200× | 0.10× | SLOWER |
| Practice | `cal.real.markup` | Rust engine | 0.0037× | 0.0036–0.0037× | 4.19× | SLOWER |
| Practice | `cal.real.quotes` | Python engine | 0.0044× | 0.0041–0.0048× | 18.83× | SLOWER |
| Practice | `cal.real.quotes` | Native C engine | 0.6921× | 0.6463–0.7675× | 0.10× | SLOWER |
| Practice | `cal.real.quotes` | Rust engine | 0.0077× | 0.0071–0.0086× | 3.83× | SLOWER |
| Practice | `cal.real.csv` | Python engine | 0.0051× | 0.0047–0.0057× | 19.83× | SLOWER |
| Practice | `cal.real.csv` | Native C engine | 0.4296× | 0.3967–0.4779× | 0.29× | SLOWER |
| Practice | `cal.real.csv` | Rust engine | 0.0112× | 0.0104–0.0125× | 2.97× | SLOWER |
| Practice | `cal.branch.prefix` | Python engine | 0.0094× | 0.0089–0.0103× | 12.65× | SLOWER |
| Practice | `cal.branch.prefix` | Native C engine | 0.7401× | 0.6815–0.7797× | 0.07× | SLOWER |
| Practice | `cal.branch.prefix` | Rust engine | 0.0134× | 0.0127–0.0146× | 3.37× | SLOWER |
| Practice | `cal.branch.miss` | Python engine | 0.0009× | 0.0009–0.0009× | 83.64× | SLOWER |
| Practice | `cal.branch.miss` | Native C engine | 0.4503× | 0.4387–0.4591× | 0.00× | SLOWER |
| Practice | `cal.branch.miss` | Rust engine | 0.0126× | 0.0125–0.0128× | 4.25× | SLOWER |
| Practice | `cal.repeat.nested` | Python engine | 0.0104× | 0.0100–0.0109× | 15.24× | SLOWER |
| Practice | `cal.repeat.nested` | Native C engine | 1.0959× | 1.0244–1.1741× | 0.64× | FASTER |
| Practice | `cal.repeat.nested` | Rust engine | 0.0244× | 0.0236–0.0258× | 1.57× | SLOWER |
| Practice | `cal.lines.records` | Python engine | 0.0080× | 0.0078–0.0083× | 14.74× | SLOWER |
| Practice | `cal.lines.records` | Native C engine | 0.9381× | 0.8870–0.9807× | 0.36× | — |
| Practice | `cal.lines.records` | Rust engine | 0.0071× | 0.0069–0.0073× | 2.56× | SLOWER |
| Practice | `cal.block.dotall` | Python engine | 0.0064× | 0.0063–0.0064× | 17.13× | SLOWER |
| Practice | `cal.block.dotall` | Native C engine | 0.6608× | 0.6572–0.6646× | 0.08× | SLOWER |
| Practice | `cal.block.dotall` | Rust engine | 0.0129× | 0.0128–0.0130× | 3.97× | SLOWER |
| Practice | `cal.pattern.verbose` | Python engine | 0.0040× | 0.0040–0.0041× | 14.85× | SLOWER |
| Practice | `cal.pattern.verbose` | Native C engine | 0.6418× | 0.6378–0.6462× | 0.09× | SLOWER |
| Practice | `cal.pattern.verbose` | Rust engine | 0.0199× | 0.0197–0.0200× | 3.43× | SLOWER |
| Practice | `cal.mode.ascii` | Python engine | 0.0052× | 0.0052–0.0053× | 7.27× | SLOWER |
| Practice | `cal.mode.ascii` | Native C engine | 0.9564× | 0.9127–0.9818× | 0.13× | — |
| Practice | `cal.mode.ascii` | Rust engine | 0.0092× | 0.0092–0.0093× | 3.04× | SLOWER |
| Practice | `cal.mode.casefold` | Python engine | 0.0082× | 0.0079–0.0086× | 5.52× | SLOWER |
| Practice | `cal.mode.casefold` | Native C engine | 1.3340× | 1.2924–1.3918× | 0.20× | FASTER |
| Practice | `cal.mode.casefold` | Rust engine | 0.0087× | 0.0083–0.0090× | 2.90× | SLOWER |
| Practice | `cal.mode.astral` | Python engine | 0.0095× | 0.0093–0.0099× | 7.05× | SLOWER |
| Practice | `cal.mode.astral` | Native C engine | 1.5577× | 1.5091–1.6300× | 0.25× | FASTER |
| Practice | `cal.mode.astral` | Rust engine | 0.0093× | 0.0090–0.0096× | 2.76× | SLOWER |
| Practice | `cal.look.negative-ahead` | Python engine | 0.0037× | 0.0037–0.0039× | 15.69× | SLOWER |
| Practice | `cal.look.negative-ahead` | Native C engine | 0.4339× | 0.4226–0.4508× | 0.53× | SLOWER |
| Practice | `cal.look.negative-ahead` | Rust engine | 0.0074× | 0.0072–0.0077× | 3.46× | SLOWER |
| Practice | `cal.look.negative-behind` | Python engine | 0.0065× | 0.0065–0.0065× | 12.65× | SLOWER |
| Practice | `cal.look.negative-behind` | Native C engine | 1.0495× | 1.0449–1.0545× | 0.10× | FASTER |
| Practice | `cal.look.negative-behind` | Rust engine | 0.0099× | 0.0098–0.0099× | 3.19× | SLOWER |
| Practice | `cal.bytes.replace` | Python engine | 0.0164× | 0.0162–0.0166× | 9.71× | SLOWER |
| Practice | `cal.bytes.replace` | Native C engine | 1.1010× | 1.0822–1.1199× | 0.95× | FASTER |
| Practice | `cal.bytes.replace` | Rust engine | 0.0158× | 0.0156–0.0160× | 2.52× | SLOWER |
| Practice | `cal.bytes.scan` | Python engine | 0.0117× | 0.0116–0.0118× | 8.55× | SLOWER |
| Practice | `cal.bytes.scan` | Native C engine | 1.3017× | 1.2821–1.3214× | 0.38× | FASTER |
| Practice | `cal.bytes.scan` | Rust engine | 0.0094× | 0.0093–0.0095× | 1.87× | SLOWER |
| Practice | `cal.compile.complex` | Python engine | 1.7536× | 1.7394–1.7676× | 0.39× | FASTER |
| Practice | `cal.compile.complex` | Native C engine | 1.3744× | 1.3622–1.3870× | 1.65× | FASTER |
| Practice | `cal.compile.complex` | Rust engine | 1.7045× | 1.6902–1.7207× | 0.52× | FASTER |
| Practice | `cal.module.replace` | Python engine | 0.0211× | 0.0208–0.0216× | 10.12× | SLOWER |
| Practice | `cal.module.replace` | Native C engine | 1.2288× | 1.2059–1.2578× | 0.04× | FASTER |
| Practice | `cal.module.replace` | Rust engine | 0.0199× | 0.0196–0.0204× | 2.52× | SLOWER |
| Practice | `cal.zero.boundary` | Python engine | 0.0074× | 0.0073–0.0076× | 13.81× | SLOWER |
| Practice | `cal.zero.boundary` | Native C engine | 0.5095× | 0.5008–0.5195× | 0.62× | SLOWER |
| Practice | `cal.zero.boundary` | Rust engine | 0.0131× | 0.0129–0.0133× | 1.69× | SLOWER |
| Practice | `cal.dense.iter` | Python engine | 0.0156× | 0.0152–0.0159× | 4.92× | SLOWER |
| Practice | `cal.dense.iter` | Native C engine | 1.3811× | 1.3547–1.4090× | 0.51× | FASTER |
| Practice | `cal.dense.iter` | Rust engine | 0.0081× | 0.0079–0.0082× | 1.49× | SLOWER |
| Practice | `cal.capture.optional` | Python engine | 0.0107× | 0.0102–0.0113× | 14.26× | SLOWER |
| Practice | `cal.capture.optional` | Native C engine | 1.1528× | 1.0828–1.2313× | 0.18× | FASTER |
| Practice | `cal.capture.optional` | Rust engine | 0.0093× | 0.0088–0.0099× | 2.79× | SLOWER |
| Practice | `cal.split.limited` | Python engine | 0.0065× | 0.0064–0.0066× | 7.47× | SLOWER |
| Practice | `cal.split.limited` | Native C engine | 1.0391× | 0.9423–1.1144× | 0.19× | — |
| Practice | `cal.split.limited` | Rust engine | 0.0076× | 0.0075–0.0077× | 2.82× | SLOWER |
| Practice | `cal.replace.limited` | Python engine | 0.0125× | 0.0123–0.0128× | 6.04× | SLOWER |
| Practice | `cal.replace.limited` | Native C engine | 1.2219× | 1.2040–1.2399× | 0.15× | FASTER |
| Practice | `cal.replace.limited` | Rust engine | 0.0092× | 0.0091–0.0093× | 2.90× | SLOWER |
| Practice | `cal.bytes.view-long` | Python engine | 0.0072× | 0.0065–0.0081× | 48.64× | SLOWER |
| Practice | `cal.bytes.view-long` | Native C engine | 1.3177× | 1.2788–1.3589× | 0.60× | FASTER |
| Practice | `cal.bytes.view-long` | Rust engine | 0.0010× | 0.0009–0.0011× | 5.61× | SLOWER |
| Practice | `cal.window.search` | Python engine | 0.0195× | 0.0187–0.0208× | 4.40× | SLOWER |
| Practice | `cal.window.search` | Native C engine | 0.9811× | 0.9446–1.0455× | 0.18× | — |
| Practice | `cal.window.search` | Rust engine | 0.0161× | 0.0155–0.0172× | 3.30× | SLOWER |
| Practice | `cal.window.findall` | Python engine | 0.0168× | 0.0165–0.0172× | 4.02× | SLOWER |
| Practice | `cal.window.findall` | Native C engine | 1.0021× | 0.9591–1.0378× | 0.23× | — |
| Practice | `cal.window.findall` | Rust engine | 0.0077× | 0.0076–0.0078× | 3.01× | SLOWER |
| Practice | `cal.window.scanner` | Python engine | 0.0175× | 0.0173–0.0176× | 4.46× | SLOWER |
| Practice | `cal.window.scanner` | Native C engine | 1.0293× | 1.0219–1.0369× | 0.30× | FASTER |
| Practice | `cal.window.scanner` | Rust engine | 0.0093× | 0.0092–0.0094× | 2.20× | SLOWER |
| Practice | `cal.window.match` | Python engine | 0.0374× | 0.0349–0.0406× | 3.55× | SLOWER |
| Practice | `cal.window.match` | Native C engine | 1.0222× | 0.9528–1.1106× | 0.18× | — |
| Practice | `cal.window.match` | Rust engine | 0.0191× | 0.0178–0.0210× | 2.45× | SLOWER |
| Practice | `cal.literal.replace` | Python engine | 0.0058× | 0.0057–0.0059× | 41.75× | SLOWER |
| Practice | `cal.literal.replace` | Native C engine | 1.2717× | 1.2600–1.2846× | 0.53× | FASTER |
| Practice | `cal.literal.replace` | Rust engine | 0.0050× | 0.0049–0.0051× | 10.40× | SLOWER |
| Practice | `cal.template.repeat` | Python engine | 0.0183× | 0.0181–0.0184× | 6.29× | SLOWER |
| Practice | `cal.template.repeat` | Native C engine | 1.3799× | 1.3254–1.4179× | 0.15× | FASTER |
| Practice | `cal.template.repeat` | Rust engine | 0.0127× | 0.0126–0.0129× | 2.29× | SLOWER |
| Practice | `cal.match.miss` | Python engine | 0.0278× | 0.0274–0.0283× | 5.02× | SLOWER |
| Practice | `cal.match.miss` | Native C engine | 1.0863× | 0.9859–1.1664× | 0.00× | — |
| Practice | `cal.match.miss` | Rust engine | 0.0079× | 0.0078–0.0080× | 4.00× | SLOWER |
| Practice | `cal.fullmatch.miss` | Python engine | 0.0172× | 0.0163–0.0188× | 11.09× | SLOWER |
| Practice | `cal.fullmatch.miss` | Native C engine | 1.3053× | 1.1281–1.5085× | 0.00× | FASTER |
| Practice | `cal.fullmatch.miss` | Rust engine | 0.0218× | 0.0193–0.0250× | 3.32× | SLOWER |
| Holdout | `hold.real.log` | Python engine | 0.0028× | 0.0027–0.0030× | 36.41× | SLOWER |
| Holdout | `hold.real.log` | Native C engine | 0.8303× | 0.7896–0.8731× | 0.33× | — |
| Holdout | `hold.real.log` | Rust engine | 0.0058× | 0.0056–0.0061× | 3.23× | SLOWER |
| Holdout | `hold.real.url` | Python engine | 0.0052× | 0.0050–0.0053× | 26.93× | SLOWER |
| Holdout | `hold.real.url` | Native C engine | 0.7158× | 0.6420–0.7764× | 0.11× | SLOWER |
| Holdout | `hold.real.url` | Rust engine | 0.0102× | 0.0099–0.0105× | 3.79× | SLOWER |
| Holdout | `hold.real.email` | Python engine | 0.0042× | 0.0042–0.0043× | 12.09× | SLOWER |
| Holdout | `hold.real.email` | Native C engine | 0.8398× | 0.8317–0.8488× | 0.12× | — |
| Holdout | `hold.real.email` | Rust engine | 0.0067× | 0.0065–0.0069× | 3.88× | SLOWER |
| Holdout | `hold.real.datetime` | Python engine | 0.0073× | 0.0072–0.0073× | 27.33× | SLOWER |
| Holdout | `hold.real.datetime` | Native C engine | 1.0138× | 1.0077–1.0206× | 0.09× | FASTER |
| Holdout | `hold.real.datetime` | Rust engine | 0.0170× | 0.0168–0.0172× | 3.42× | SLOWER |
| Holdout | `hold.real.version` | Python engine | 0.0093× | 0.0092–0.0093× | 23.70× | SLOWER |
| Holdout | `hold.real.version` | Native C engine | 1.0447× | 0.9611–1.0951× | 0.06× | — |
| Holdout | `hold.real.version` | Rust engine | 0.0210× | 0.0208–0.0212× | 3.01× | SLOWER |
| Holdout | `hold.real.uuid` | Python engine | 0.0061× | 0.0060–0.0061× | 18.05× | SLOWER |
| Holdout | `hold.real.uuid` | Native C engine | 0.7641× | 0.7573–0.7710× | 0.07× | SLOWER |
| Holdout | `hold.real.uuid` | Rust engine | 0.0130× | 0.0129–0.0130× | 3.95× | SLOWER |
| Holdout | `hold.real.ip` | Python engine | 0.0086× | 0.0085–0.0087× | 30.05× | SLOWER |
| Holdout | `hold.real.ip` | Native C engine | 1.0696× | 1.0509–1.0877× | 0.07× | FASTER |
| Holdout | `hold.real.ip` | Rust engine | 0.0208× | 0.0205–0.0211× | 3.02× | SLOWER |
| Holdout | `hold.real.path` | Python engine | 0.0055× | 0.0055–0.0056× | 26.39× | SLOWER |
| Holdout | `hold.real.path` | Native C engine | 0.8603× | 0.8424–0.8748× | 0.12× | — |
| Holdout | `hold.real.path` | Rust engine | 0.0094× | 0.0093–0.0095× | 3.84× | SLOWER |
| Holdout | `hold.real.config` | Python engine | 0.0084× | 0.0083–0.0086× | 18.02× | SLOWER |
| Holdout | `hold.real.config` | Native C engine | 1.0472× | 1.0304–1.0634× | 0.35× | FASTER |
| Holdout | `hold.real.config` | Rust engine | 0.0151× | 0.0149–0.0154× | 2.32× | SLOWER |
| Holdout | `hold.real.comments` | Python engine | 0.0048× | 0.0047–0.0049× | 16.97× | SLOWER |
| Holdout | `hold.real.comments` | Native C engine | 0.8303× | 0.7867–0.8642× | 0.14× | — |
| Holdout | `hold.real.comments` | Rust engine | 0.0033× | 0.0032–0.0033× | 4.05× | SLOWER |
| Holdout | `hold.real.whitespace` | Python engine | 0.0071× | 0.0069–0.0073× | 8.45× | SLOWER |
| Holdout | `hold.real.whitespace` | Native C engine | 1.3398× | 1.2948–1.3929× | 0.14× | FASTER |
| Holdout | `hold.real.whitespace` | Rust engine | 0.0071× | 0.0069–0.0074× | 2.74× | SLOWER |
| Holdout | `hold.real.lines` | Python engine | 0.0097× | 0.0096–0.0099× | 13.22× | SLOWER |
| Holdout | `hold.real.lines` | Native C engine | 1.5739× | 1.5422–1.6114× | 0.14× | FASTER |
| Holdout | `hold.real.lines` | Rust engine | 0.0093× | 0.0092–0.0095× | 2.82× | SLOWER |
| Holdout | `hold.real.markup` | Python engine | 0.0046× | 0.0046–0.0047× | 14.16× | SLOWER |
| Holdout | `hold.real.markup` | Native C engine | 0.6205× | 0.6152–0.6269× | 0.13× | SLOWER |
| Holdout | `hold.real.markup` | Rust engine | 0.0031× | 0.0031–0.0032× | 4.34× | SLOWER |
| Holdout | `hold.real.quotes` | Python engine | 0.0041× | 0.0040–0.0041× | 18.87× | SLOWER |
| Holdout | `hold.real.quotes` | Native C engine | 0.6604× | 0.6542–0.6660× | 0.10× | SLOWER |
| Holdout | `hold.real.quotes` | Rust engine | 0.0072× | 0.0071–0.0073× | 3.58× | SLOWER |
| Holdout | `hold.real.csv` | Python engine | 0.0041× | 0.0040–0.0042× | 18.08× | SLOWER |
| Holdout | `hold.real.csv` | Native C engine | 0.3477× | 0.3409–0.3580× | 0.30× | SLOWER |
| Holdout | `hold.real.csv` | Rust engine | 0.0095× | 0.0093–0.0098× | 3.21× | SLOWER |
| Holdout | `hold.branch.prefix` | Python engine | 0.0099× | 0.0097–0.0100× | 11.86× | SLOWER |
| Holdout | `hold.branch.prefix` | Native C engine | 0.8017× | 0.7899–0.8145× | 0.07× | — |
| Holdout | `hold.branch.prefix` | Rust engine | 0.0133× | 0.0131–0.0135× | 3.36× | SLOWER |
| Holdout | `hold.branch.miss` | Python engine | 0.0008× | 0.0008–0.0008× | 80.13× | SLOWER |
| Holdout | `hold.branch.miss` | Native C engine | 0.6974× | 0.6908–0.7045× | 0.00× | SLOWER |
| Holdout | `hold.branch.miss` | Rust engine | 0.0111× | 0.0110–0.0112× | 4.57× | SLOWER |
| Holdout | `hold.repeat.nested` | Python engine | 0.0102× | 0.0098–0.0110× | 15.24× | SLOWER |
| Holdout | `hold.repeat.nested` | Native C engine | 1.0428× | 0.9981–1.1259× | 0.64× | — |
| Holdout | `hold.repeat.nested` | Rust engine | 0.0229× | 0.0218–0.0249× | 1.57× | SLOWER |
| Holdout | `hold.lines.records` | Python engine | 0.0084× | 0.0082–0.0087× | 14.74× | SLOWER |
| Holdout | `hold.lines.records` | Native C engine | 0.9976× | 0.9664–1.0381× | 0.36× | — |
| Holdout | `hold.lines.records` | Rust engine | 0.0076× | 0.0074–0.0079× | 2.55× | SLOWER |
| Holdout | `hold.block.dotall` | Python engine | 0.0063× | 0.0063–0.0064× | 18.13× | SLOWER |
| Holdout | `hold.block.dotall` | Native C engine | 0.6559× | 0.6517–0.6603× | 0.08× | SLOWER |
| Holdout | `hold.block.dotall` | Rust engine | 0.0131× | 0.0130–0.0132× | 4.00× | SLOWER |
| Holdout | `hold.pattern.verbose` | Python engine | 0.0037× | 0.0035–0.0038× | 15.91× | SLOWER |
| Holdout | `hold.pattern.verbose` | Native C engine | 0.6182× | 0.5352–0.6784× | 0.09× | SLOWER |
| Holdout | `hold.pattern.verbose` | Rust engine | 0.0257× | 0.0241–0.0274× | 3.45× | SLOWER |
| Holdout | `hold.mode.ascii` | Python engine | 0.0052× | 0.0052–0.0053× | 7.82× | SLOWER |
| Holdout | `hold.mode.ascii` | Native C engine | 1.0479× | 1.0065–1.0751× | 0.21× | FASTER |
| Holdout | `hold.mode.ascii` | Rust engine | 0.0077× | 0.0076–0.0078× | 3.02× | SLOWER |
| Holdout | `hold.mode.casefold` | Python engine | 0.0081× | 0.0080–0.0084× | 5.44× | SLOWER |
| Holdout | `hold.mode.casefold` | Native C engine | 1.3704× | 1.3406–1.4190× | 0.18× | FASTER |
| Holdout | `hold.mode.casefold` | Rust engine | 0.0102× | 0.0100–0.0106× | 2.93× | SLOWER |
| Holdout | `hold.mode.astral` | Python engine | 0.0091× | 0.0089–0.0093× | 7.06× | SLOWER |
| Holdout | `hold.mode.astral` | Native C engine | 1.5270× | 1.5073–1.5462× | 0.25× | FASTER |
| Holdout | `hold.mode.astral` | Rust engine | 0.0091× | 0.0091–0.0092× | 2.77× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Python engine | 0.0037× | 0.0035–0.0041× | 16.30× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Native C engine | 0.4236× | 0.3998–0.4693× | 0.53× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Rust engine | 0.0071× | 0.0066–0.0079× | 3.47× | SLOWER |
| Holdout | `hold.look.negative-behind` | Python engine | 0.0066× | 0.0066–0.0067× | 12.65× | SLOWER |
| Holdout | `hold.look.negative-behind` | Native C engine | 1.0618× | 1.0507–1.0728× | 0.10× | FASTER |
| Holdout | `hold.look.negative-behind` | Rust engine | 0.0100× | 0.0099–0.0100× | 3.19× | SLOWER |
| Holdout | `hold.bytes.replace` | Python engine | 0.0167× | 0.0165–0.0169× | 9.71× | SLOWER |
| Holdout | `hold.bytes.replace` | Native C engine | 1.1293× | 1.0969–1.1618× | 0.93× | FASTER |
| Holdout | `hold.bytes.replace` | Rust engine | 0.0160× | 0.0159–0.0162× | 2.52× | SLOWER |
| Holdout | `hold.bytes.scan` | Python engine | 0.0115× | 0.0114–0.0116× | 8.55× | SLOWER |
| Holdout | `hold.bytes.scan` | Native C engine | 1.1716× | 1.0460–1.2678× | 0.38× | FASTER |
| Holdout | `hold.bytes.scan` | Rust engine | 0.0091× | 0.0090–0.0092× | 1.87× | SLOWER |
| Holdout | `hold.compile.complex` | Python engine | 1.8260× | 1.8197–1.8318× | 0.37× | FASTER |
| Holdout | `hold.compile.complex` | Native C engine | 1.4185× | 1.4091–1.4275× | 1.67× | FASTER |
| Holdout | `hold.compile.complex` | Rust engine | 1.5364× | 1.5262–1.5464× | 0.55× | FASTER |
| Holdout | `hold.module.replace` | Python engine | 0.0208× | 0.0206–0.0212× | 10.12× | SLOWER |
| Holdout | `hold.module.replace` | Native C engine | 1.2069× | 1.1927–1.2281× | 0.04× | FASTER |
| Holdout | `hold.module.replace` | Rust engine | 0.0195× | 0.0193–0.0198× | 2.52× | SLOWER |
| Holdout | `hold.zero.boundary` | Python engine | 0.0081× | 0.0080–0.0083× | 8.20× | SLOWER |
| Holdout | `hold.zero.boundary` | Native C engine | 0.5278× | 0.5165–0.5393× | 0.62× | SLOWER |
| Holdout | `hold.zero.boundary` | Rust engine | 0.0141× | 0.0138–0.0144× | 1.67× | SLOWER |
| Holdout | `hold.dense.iter` | Python engine | 0.0156× | 0.0154–0.0158× | 4.92× | SLOWER |
| Holdout | `hold.dense.iter` | Native C engine | 1.3404× | 1.2999–1.3756× | 0.51× | FASTER |
| Holdout | `hold.dense.iter` | Rust engine | 0.0079× | 0.0078–0.0080× | 1.50× | SLOWER |
| Holdout | `hold.capture.optional` | Python engine | 0.0097× | 0.0096–0.0099× | 14.26× | SLOWER |
| Holdout | `hold.capture.optional` | Native C engine | 1.0306× | 1.0171–1.0427× | 0.18× | FASTER |
| Holdout | `hold.capture.optional` | Rust engine | 0.0082× | 0.0081–0.0082× | 2.79× | SLOWER |
| Holdout | `hold.split.limited` | Python engine | 0.0063× | 0.0061–0.0065× | 7.46× | SLOWER |
| Holdout | `hold.split.limited` | Native C engine | 1.0899× | 1.0613–1.1348× | 0.19× | FASTER |
| Holdout | `hold.split.limited` | Rust engine | 0.0072× | 0.0071–0.0075× | 2.83× | SLOWER |
| Holdout | `hold.replace.limited` | Python engine | 0.0128× | 0.0124–0.0135× | 6.04× | SLOWER |
| Holdout | `hold.replace.limited` | Native C engine | 1.1715× | 1.1320–1.2322× | 0.15× | FASTER |
| Holdout | `hold.replace.limited` | Rust engine | 0.0088× | 0.0085–0.0093× | 2.90× | SLOWER |
| Holdout | `hold.bytes.view-long` | Python engine | 0.0066× | 0.0063–0.0067× | 48.64× | SLOWER |
| Holdout | `hold.bytes.view-long` | Native C engine | 1.2628× | 1.1380–1.3400× | 0.60× | FASTER |
| Holdout | `hold.bytes.view-long` | Rust engine | 0.0010× | 0.0009–0.0010× | 5.61× | SLOWER |
| Holdout | `hold.window.search` | Python engine | 0.0185× | 0.0184–0.0187× | 4.40× | SLOWER |
| Holdout | `hold.window.search` | Native C engine | 0.9156× | 0.8867–0.9339× | 0.18× | — |
| Holdout | `hold.window.search` | Rust engine | 0.0146× | 0.0145–0.0148× | 3.32× | SLOWER |
| Holdout | `hold.window.findall` | Python engine | 0.0171× | 0.0167–0.0174× | 4.03× | SLOWER |
| Holdout | `hold.window.findall` | Native C engine | 0.9031× | 0.8458–0.9381× | 0.22× | — |
| Holdout | `hold.window.findall` | Rust engine | 0.0072× | 0.0071–0.0073× | 2.86× | SLOWER |
| Holdout | `hold.window.scanner` | Python engine | 0.0177× | 0.0173–0.0180× | 4.46× | SLOWER |
| Holdout | `hold.window.scanner` | Native C engine | 1.0614× | 1.0461–1.0791× | 0.30× | FASTER |
| Holdout | `hold.window.scanner` | Rust engine | 0.0095× | 0.0094–0.0097× | 2.20× | SLOWER |
| Holdout | `hold.window.match` | Python engine | 0.0324× | 0.0321–0.0327× | 3.55× | SLOWER |
| Holdout | `hold.window.match` | Native C engine | 0.9162× | 0.9074–0.9258× | 0.18× | — |
| Holdout | `hold.window.match` | Rust engine | 0.0172× | 0.0169–0.0174× | 2.46× | SLOWER |
| Holdout | `hold.literal.replace` | Python engine | 0.0063× | 0.0060–0.0070× | 38.88× | SLOWER |
| Holdout | `hold.literal.replace` | Native C engine | 1.2386× | 1.1241–1.3921× | 0.52× | FASTER |
| Holdout | `hold.literal.replace` | Rust engine | 0.0055× | 0.0052–0.0059× | 10.36× | SLOWER |
| Holdout | `hold.template.repeat` | Python engine | 0.0186× | 0.0183–0.0190× | 6.32× | SLOWER |
| Holdout | `hold.template.repeat` | Native C engine | 1.4185× | 1.4015–1.4441× | 0.14× | FASTER |
| Holdout | `hold.template.repeat` | Rust engine | 0.0135× | 0.0133–0.0138× | 2.28× | SLOWER |
| Holdout | `hold.match.miss` | Python engine | 0.0287× | 0.0260–0.0321× | 5.02× | SLOWER |
| Holdout | `hold.match.miss` | Native C engine | 1.1964× | 1.0856–1.3336× | 0.00× | FASTER |
| Holdout | `hold.match.miss` | Rust engine | 0.0077× | 0.0074–0.0084× | 4.20× | SLOWER |
| Holdout | `hold.fullmatch.miss` | Python engine | 0.0175× | 0.0173–0.0177× | 11.09× | SLOWER |
| Holdout | `hold.fullmatch.miss` | Native C engine | 1.3604× | 1.3430–1.3800× | 0.00× | FASTER |
| Holdout | `hold.fullmatch.miss` | Rust engine | 0.0224× | 0.0221–0.0228× | 3.31× | SLOWER |

## Large slowdowns

- Python engine: `cal.search.literal.hit` (0.007×), `cal.search.literal.miss` (0.002×), `cal.search.long-boundary` (0.000×), `cal.search.class-anchor` (0.011×), `cal.match.prefix` (0.024×), `cal.fullmatch.structured` (0.013×), `cal.search.look-capture` (0.008×), `cal.findall.tokens` (0.010×), `cal.finditer.groups` (0.013×), `cal.split.capture` (0.010×), `cal.sub.template` (0.016×), `cal.subn.callable` (0.024×), `cal.bytes.tokens` (0.007×), `cal.unicode.words` (0.006×), `cal.cold.compile-search` (0.296×), `cal.module.warm` (0.010×), `cal.empty.finditer` (0.010×), `cal.backref.fullmatch` (0.018×), `cal.conditional.match` (0.018×), `cal.atomic.search` (0.010×), `cal.byteslike.findall` (0.011×), `cal.unicode-name.search` (0.014×), `cal.ignorecase.findall` (0.007×), `cal.many.split` (0.013×), `cal.scanner.search` (0.013×), `cal.match.surface` (0.014×), `hold.search.literal.hit` (0.008×), `hold.search.literal.miss` (0.002×), `hold.search.long-boundary` (0.000×), `hold.search.class-anchor` (0.011×), `hold.match.prefix` (0.025×), `hold.fullmatch.structured` (0.011×), `hold.search.look-capture` (0.010×), `hold.findall.tokens` (0.011×), `hold.finditer.groups` (0.014×), `hold.split.capture` (0.010×), `hold.sub.template` (0.016×), `hold.subn.callable` (0.027×), `hold.bytes.tokens` (0.010×), `hold.unicode.words` (0.009×), `hold.cold.compile-search` (0.484×), `hold.module.warm` (0.019×), `hold.empty.finditer` (0.009×), `hold.backref.fullmatch` (0.018×), `hold.conditional.match` (0.019×), `hold.atomic.search` (0.012×), `hold.byteslike.findall` (0.011×), `hold.unicode-name.search` (0.014×), `hold.ignorecase.findall` (0.008×), `hold.many.split` (0.013×), `hold.scanner.search` (0.013×), `hold.match.surface` (0.021×), `cal.real.log` (0.003×), `cal.real.url` (0.006×), `cal.real.email` (0.006×), `cal.real.datetime` (0.008×), `cal.real.version` (0.011×), `cal.real.uuid` (0.006×), `cal.real.ip` (0.008×), `cal.real.path` (0.006×), `cal.real.config` (0.008×), `cal.real.comments` (0.006×), `cal.real.whitespace` (0.007×), `cal.real.lines` (0.010×), `cal.real.markup` (0.005×), `cal.real.quotes` (0.004×), `cal.real.csv` (0.005×), `cal.branch.prefix` (0.009×), `cal.branch.miss` (0.001×), `cal.repeat.nested` (0.010×), `cal.lines.records` (0.008×), `cal.block.dotall` (0.006×), `cal.pattern.verbose` (0.004×), `cal.mode.ascii` (0.005×), `cal.mode.casefold` (0.008×), `cal.mode.astral` (0.010×), `cal.look.negative-ahead` (0.004×), `cal.look.negative-behind` (0.007×), `cal.bytes.replace` (0.016×), `cal.bytes.scan` (0.012×), `cal.module.replace` (0.021×), `cal.zero.boundary` (0.007×), `cal.dense.iter` (0.016×), `cal.capture.optional` (0.011×), `cal.split.limited` (0.006×), `cal.replace.limited` (0.013×), `cal.bytes.view-long` (0.007×), `cal.window.search` (0.019×), `cal.window.findall` (0.017×), `cal.window.scanner` (0.017×), `cal.window.match` (0.037×), `cal.literal.replace` (0.006×), `cal.template.repeat` (0.018×), `cal.match.miss` (0.028×), `cal.fullmatch.miss` (0.017×), `hold.real.log` (0.003×), `hold.real.url` (0.005×), `hold.real.email` (0.004×), `hold.real.datetime` (0.007×), `hold.real.version` (0.009×), `hold.real.uuid` (0.006×), `hold.real.ip` (0.009×), `hold.real.path` (0.006×), `hold.real.config` (0.008×), `hold.real.comments` (0.005×), `hold.real.whitespace` (0.007×), `hold.real.lines` (0.010×), `hold.real.markup` (0.005×), `hold.real.quotes` (0.004×), `hold.real.csv` (0.004×), `hold.branch.prefix` (0.010×), `hold.branch.miss` (0.001×), `hold.repeat.nested` (0.010×), `hold.lines.records` (0.008×), `hold.block.dotall` (0.006×), `hold.pattern.verbose` (0.004×), `hold.mode.ascii` (0.005×), `hold.mode.casefold` (0.008×), `hold.mode.astral` (0.009×), `hold.look.negative-ahead` (0.004×), `hold.look.negative-behind` (0.007×), `hold.bytes.replace` (0.017×), `hold.bytes.scan` (0.011×), `hold.module.replace` (0.021×), `hold.zero.boundary` (0.008×), `hold.dense.iter` (0.016×), `hold.capture.optional` (0.010×), `hold.split.limited` (0.006×), `hold.replace.limited` (0.013×), `hold.bytes.view-long` (0.007×), `hold.window.search` (0.019×), `hold.window.findall` (0.017×), `hold.window.scanner` (0.018×), `hold.window.match` (0.032×), `hold.literal.replace` (0.006×), `hold.template.repeat` (0.019×), `hold.match.miss` (0.029×), `hold.fullmatch.miss` (0.017×).
- Rust engine: `cal.search.literal.hit` (0.009×), `cal.search.literal.miss` (0.006×), `cal.search.long-boundary` (0.001×), `cal.search.class-anchor` (0.015×), `cal.match.prefix` (0.015×), `cal.fullmatch.structured` (0.018×), `cal.search.look-capture` (0.017×), `cal.findall.tokens` (0.004×), `cal.finditer.groups` (0.010×), `cal.split.capture` (0.007×), `cal.sub.template` (0.015×), `cal.subn.callable` (0.019×), `cal.bytes.tokens` (0.005×), `cal.unicode.words` (0.010×), `cal.cold.compile-search` (0.698×), `cal.module.warm` (0.031×), `cal.empty.finditer` (0.021×), `cal.backref.fullmatch` (0.018×), `cal.conditional.match` (0.016×), `cal.atomic.search` (0.018×), `cal.byteslike.findall` (0.008×), `cal.unicode-name.search` (0.019×), `cal.ignorecase.findall` (0.008×), `cal.many.split` (0.005×), `cal.scanner.search` (0.009×), `cal.match.surface` (0.048×), `hold.search.literal.hit` (0.009×), `hold.search.literal.miss` (0.006×), `hold.search.long-boundary` (0.001×), `hold.search.class-anchor` (0.014×), `hold.match.prefix` (0.015×), `hold.fullmatch.structured` (0.019×), `hold.search.look-capture` (0.017×), `hold.findall.tokens` (0.006×), `hold.finditer.groups` (0.010×), `hold.split.capture` (0.007×), `hold.sub.template` (0.015×), `hold.subn.callable` (0.022×), `hold.bytes.tokens` (0.008×), `hold.unicode.words` (0.012×), `hold.cold.compile-search` (0.735×), `hold.module.warm` (0.031×), `hold.empty.finditer` (0.021×), `hold.backref.fullmatch` (0.019×), `hold.conditional.match` (0.019×), `hold.atomic.search` (0.024×), `hold.byteslike.findall` (0.008×), `hold.unicode-name.search` (0.021×), `hold.ignorecase.findall` (0.009×), `hold.many.split` (0.005×), `hold.scanner.search` (0.009×), `hold.match.surface` (0.041×), `cal.real.log` (0.006×), `cal.real.url` (0.012×), `cal.real.email` (0.006×), `cal.real.datetime` (0.016×), `cal.real.version` (0.030×), `cal.real.uuid` (0.014×), `cal.real.ip` (0.026×), `cal.real.path` (0.011×), `cal.real.config` (0.017×), `cal.real.comments` (0.004×), `cal.real.whitespace` (0.007×), `cal.real.lines` (0.009×), `cal.real.markup` (0.004×), `cal.real.quotes` (0.008×), `cal.real.csv` (0.011×), `cal.branch.prefix` (0.013×), `cal.branch.miss` (0.013×), `cal.repeat.nested` (0.024×), `cal.lines.records` (0.007×), `cal.block.dotall` (0.013×), `cal.pattern.verbose` (0.020×), `cal.mode.ascii` (0.009×), `cal.mode.casefold` (0.009×), `cal.mode.astral` (0.009×), `cal.look.negative-ahead` (0.007×), `cal.look.negative-behind` (0.010×), `cal.bytes.replace` (0.016×), `cal.bytes.scan` (0.009×), `cal.module.replace` (0.020×), `cal.zero.boundary` (0.013×), `cal.dense.iter` (0.008×), `cal.capture.optional` (0.009×), `cal.split.limited` (0.008×), `cal.replace.limited` (0.009×), `cal.bytes.view-long` (0.001×), `cal.window.search` (0.016×), `cal.window.findall` (0.008×), `cal.window.scanner` (0.009×), `cal.window.match` (0.019×), `cal.literal.replace` (0.005×), `cal.template.repeat` (0.013×), `cal.match.miss` (0.008×), `cal.fullmatch.miss` (0.022×), `hold.real.log` (0.006×), `hold.real.url` (0.010×), `hold.real.email` (0.007×), `hold.real.datetime` (0.017×), `hold.real.version` (0.021×), `hold.real.uuid` (0.013×), `hold.real.ip` (0.021×), `hold.real.path` (0.009×), `hold.real.config` (0.015×), `hold.real.comments` (0.003×), `hold.real.whitespace` (0.007×), `hold.real.lines` (0.009×), `hold.real.markup` (0.003×), `hold.real.quotes` (0.007×), `hold.real.csv` (0.010×), `hold.branch.prefix` (0.013×), `hold.branch.miss` (0.011×), `hold.repeat.nested` (0.023×), `hold.lines.records` (0.008×), `hold.block.dotall` (0.013×), `hold.pattern.verbose` (0.026×), `hold.mode.ascii` (0.008×), `hold.mode.casefold` (0.010×), `hold.mode.astral` (0.009×), `hold.look.negative-ahead` (0.007×), `hold.look.negative-behind` (0.010×), `hold.bytes.replace` (0.016×), `hold.bytes.scan` (0.009×), `hold.module.replace` (0.019×), `hold.zero.boundary` (0.014×), `hold.dense.iter` (0.008×), `hold.capture.optional` (0.008×), `hold.split.limited` (0.007×), `hold.replace.limited` (0.009×), `hold.bytes.view-long` (0.001×), `hold.window.search` (0.015×), `hold.window.findall` (0.007×), `hold.window.scanner` (0.010×), `hold.window.match` (0.017×), `hold.literal.replace` (0.005×), `hold.template.repeat` (0.014×), `hold.match.miss` (0.008×), `hold.fullmatch.miss` (0.022×).
- Native C engine: `cal.cold.compile-search` (0.741×), `cal.empty.finditer` (0.693×), `hold.cold.compile-search` (0.799×), `hold.empty.finditer` (0.645×), `cal.real.email` (0.652×), `cal.real.comments` (0.762×), `cal.real.markup` (0.607×), `cal.real.quotes` (0.692×), `cal.real.csv` (0.430×), `cal.branch.prefix` (0.740×), `cal.branch.miss` (0.450×), `cal.block.dotall` (0.661×), `cal.pattern.verbose` (0.642×), `cal.look.negative-ahead` (0.434×), `cal.zero.boundary` (0.509×), `hold.real.url` (0.716×), `hold.real.uuid` (0.764×), `hold.real.markup` (0.621×), `hold.real.quotes` (0.660×), `hold.real.csv` (0.348×), `hold.branch.miss` (0.697×), `hold.block.dotall` (0.656×), `hold.pattern.verbose` (0.618×), `hold.look.negative-ahead` (0.424×), `hold.zero.boundary` (0.528×).

The Python engine performs matching work in Python, and the Rust engine repeatedly prepares data and crosses the Python/Rust boundary; both costs dominate short tasks. Native-C losses expose specific boundary and general-path costs:
- Empty matches and controlled branches use the general backtracking/iterator path and construct more match state.
- Everyday log, address, path, comment, markup, quote, and comma-separated-field tasks combine repeated classes, captures, or lookarounds; they take the general native backtracking path instead of its compact single-pass path.
- Searches across many alternative words still test the remaining branches when a possible prefix survives; the native one/two-character start filter removes impossible positions but does not build a full shared-prefix trie.
- Structured repeated paths, multi-line blocks, and readable formatted fields require general repeat/capture backtracking, which carries more state than the simple literal and single-character fast paths.
- Excluded-prefix and tagged-word searches evaluate a negative lookaround for each possible match, so the native executor repeats assertion work while scanning.
- Word/separator-position iteration and limited mixed-separator splits repeatedly use the general iterator or whitespace-backtracking path; each small match pays state and result-construction costs.

No loss is removed from the denominator or hidden from the charts.
