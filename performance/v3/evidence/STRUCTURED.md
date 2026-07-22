# Native structured paths: full paired result

All 7488 raw timing rows, 432 engine/task results, and 279 large slowdowns are retained. Raw SHA-256: `b50c85728c81e6be0d11a5582ecdcd4ef2145854c4f687216395ab5754a348b4`.

## At a glance

The holdout tasks were kept separate from tuning. **1× means the same speed as Python `re`; higher is faster.** A result is clearly faster only when its measured range stays above 1×. A large slowdown means more than 20% slower.

| Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: | ---: |
| Native C engine | **1.2918×** | 1.2833–1.2999× | 50/72 | 0/72 |
| Rust engine | **0.0136×** | 0.0136–0.0137× | 2/72 | 69/72 |
| Python engine | **0.0116×** | 0.0116–0.0117× | 3/72 | 69/72 |

## Overall results

| Task set | Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |
| --- | --- | ---: | ---: | ---: | ---: |
| Practice | Python engine | 0.0115× | 0.0114–0.0115× | 2/72 | 69 |
| Practice | Native C engine | 1.2605× | 1.2525–1.2680× | 52/72 | 3 |
| Practice | Rust engine | 0.0137× | 0.0136–0.0138× | 2/72 | 69 |
| Holdout | Python engine | 0.0116× | 0.0116–0.0117× | 3/72 | 69 |
| Holdout | Native C engine | 1.2918× | 1.2833–1.2999× | 50/72 | 0 |
| Holdout | Rust engine | 0.0136× | 0.0136–0.0137× | 2/72 | 69 |
| All | Python engine | 0.0115× | 0.0115–0.0116× | 5/144 | 138 |
| All | Native C engine | 1.2760× | 1.2702–1.2818× | 102/144 | 3 |
| All | Rust engine | 0.0137× | 0.0136–0.0137× | 4/144 | 138 |

## Every task

`FASTER` means the measured range stays above 1×. `SLOWER` means more than 20% slower. Memory compares median traced Python memory with Python `re`.

| Task set | Task | Engine | Speed | Measured range | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Practice | `cal.search.literal.hit` | Python engine | 0.0076× | 0.0072–0.0082× | 102.00× | SLOWER |
| Practice | `cal.search.literal.hit` | Native C engine | 1.1418× | 1.0946–1.2345× | 0.73× | FASTER |
| Practice | `cal.search.literal.hit` | Rust engine | 0.0088× | 0.0086–0.0093× | 34.03× | SLOWER |
| Practice | `cal.search.literal.miss` | Python engine | 0.0024× | 0.0022–0.0026× | 14408.00× | SLOWER |
| Practice | `cal.search.literal.miss` | Native C engine | 1.2255× | 1.1293–1.3767× | 0.00× | FASTER |
| Practice | `cal.search.literal.miss` | Rust engine | 0.0064× | 0.0057–0.0073× | 4375.00× | SLOWER |
| Practice | `cal.search.long-boundary` | Python engine | 0.0003× | 0.0003–0.0003× | 129.57× | SLOWER |
| Practice | `cal.search.long-boundary` | Native C engine | 13.3477× | 11.3199–15.1957× | 0.07× | FASTER |
| Practice | `cal.search.long-boundary` | Rust engine | 0.0011× | 0.0010–0.0012× | 140.03× | SLOWER |
| Practice | `cal.search.class-anchor` | Python engine | 0.0108× | 0.0107–0.0110× | 11.57× | SLOWER |
| Practice | `cal.search.class-anchor` | Native C engine | 1.1863× | 1.1230–1.2228× | 0.07× | FASTER |
| Practice | `cal.search.class-anchor` | Rust engine | 0.0143× | 0.0141–0.0144× | 3.36× | SLOWER |
| Practice | `cal.match.prefix` | Python engine | 0.0239× | 0.0233–0.0246× | 3.87× | SLOWER |
| Practice | `cal.match.prefix` | Native C engine | 1.1880× | 1.1607–1.2250× | 0.07× | FASTER |
| Practice | `cal.match.prefix` | Rust engine | 0.0154× | 0.0149–0.0159× | 2.89× | SLOWER |
| Practice | `cal.fullmatch.structured` | Python engine | 0.0127× | 0.0125–0.0131× | 12.07× | SLOWER |
| Practice | `cal.fullmatch.structured` | Native C engine | 1.2146× | 1.1898–1.2535× | 0.07× | FASTER |
| Practice | `cal.fullmatch.structured` | Rust engine | 0.0188× | 0.0184–0.0194× | 3.04× | SLOWER |
| Practice | `cal.search.look-capture` | Python engine | 0.0076× | 0.0075–0.0077× | 17.28× | SLOWER |
| Practice | `cal.search.look-capture` | Native C engine | 1.3043× | 1.2848–1.3230× | 0.08× | FASTER |
| Practice | `cal.search.look-capture` | Rust engine | 0.0160× | 0.0158–0.0162× | 3.29× | SLOWER |
| Practice | `cal.findall.tokens` | Python engine | 0.0107× | 0.0104–0.0112× | 7.14× | SLOWER |
| Practice | `cal.findall.tokens` | Native C engine | 1.0910× | 1.0527–1.1209× | 0.28× | FASTER |
| Practice | `cal.findall.tokens` | Rust engine | 0.0039× | 0.0038–0.0041× | 3.26× | SLOWER |
| Practice | `cal.finditer.groups` | Python engine | 0.0127× | 0.0125–0.0129× | 7.75× | SLOWER |
| Practice | `cal.finditer.groups` | Native C engine | 1.5134× | 1.4878–1.5405× | 0.39× | FASTER |
| Practice | `cal.finditer.groups` | Rust engine | 0.0096× | 0.0094–0.0098× | 1.91× | SLOWER |
| Practice | `cal.split.capture` | Python engine | 0.0100× | 0.0099–0.0102× | 11.37× | SLOWER |
| Practice | `cal.split.capture` | Native C engine | 1.9367× | 1.9194–1.9515× | 0.20× | FASTER |
| Practice | `cal.split.capture` | Rust engine | 0.0067× | 0.0066–0.0069× | 2.62× | SLOWER |
| Practice | `cal.sub.template` | Python engine | 0.0163× | 0.0160–0.0169× | 9.30× | SLOWER |
| Practice | `cal.sub.template` | Native C engine | 1.7480× | 1.7308–1.7680× | 0.12× | FASTER |
| Practice | `cal.sub.template` | Rust engine | 0.0150× | 0.0146–0.0156× | 2.39× | SLOWER |
| Practice | `cal.subn.callable` | Python engine | 0.0235× | 0.0233–0.0237× | 5.05× | SLOWER |
| Practice | `cal.subn.callable` | Native C engine | 1.0626× | 0.9895–1.1318× | 0.25× | — |
| Practice | `cal.subn.callable` | Rust engine | 0.0191× | 0.0188–0.0194× | 2.56× | SLOWER |
| Practice | `cal.bytes.tokens` | Python engine | 0.0074× | 0.0073–0.0074× | 8.29× | SLOWER |
| Practice | `cal.bytes.tokens` | Native C engine | 1.0514× | 1.0433–1.0584× | 0.12× | FASTER |
| Practice | `cal.bytes.tokens` | Rust engine | 0.0055× | 0.0054–0.0055× | 3.43× | SLOWER |
| Practice | `cal.unicode.words` | Python engine | 0.0064× | 0.0063–0.0064× | 6.52× | SLOWER |
| Practice | `cal.unicode.words` | Native C engine | 0.9638× | 0.9568–0.9710× | 0.20× | — |
| Practice | `cal.unicode.words` | Rust engine | 0.0100× | 0.0099–0.0101× | 2.69× | SLOWER |
| Practice | `cal.cold.compile-search` | Python engine | 0.2929× | 0.2896–0.2967× | 5.84× | SLOWER |
| Practice | `cal.cold.compile-search` | Native C engine | 0.7689× | 0.7587–0.7804× | 1.50× | SLOWER |
| Practice | `cal.cold.compile-search` | Rust engine | 0.6991× | 0.6878–0.7076× | 1.95× | SLOWER |
| Practice | `cal.module.warm` | Python engine | 0.0103× | 0.0102–0.0105× | 7.21× | SLOWER |
| Practice | `cal.module.warm` | Native C engine | 1.2580× | 1.2265–1.2840× | 0.07× | FASTER |
| Practice | `cal.module.warm` | Rust engine | 0.0314× | 0.0310–0.0318× | 3.39× | SLOWER |
| Practice | `cal.empty.finditer` | Python engine | 0.0099× | 0.0097–0.0102× | 8.09× | SLOWER |
| Practice | `cal.empty.finditer` | Native C engine | 2.0260× | 1.8462–2.1669× | 0.34× | FASTER |
| Practice | `cal.empty.finditer` | Rust engine | 0.0215× | 0.0209–0.0222× | 1.67× | SLOWER |
| Practice | `cal.backref.fullmatch` | Python engine | 0.0185× | 0.0184–0.0187× | 6.99× | SLOWER |
| Practice | `cal.backref.fullmatch` | Native C engine | 1.1415× | 0.9813–1.2392× | 0.08× | — |
| Practice | `cal.backref.fullmatch` | Rust engine | 0.0185× | 0.0183–0.0186× | 3.04× | SLOWER |
| Practice | `cal.conditional.match` | Python engine | 0.0179× | 0.0177–0.0181× | 6.78× | SLOWER |
| Practice | `cal.conditional.match` | Native C engine | 1.1980× | 1.1851–1.2112× | 0.08× | FASTER |
| Practice | `cal.conditional.match` | Rust engine | 0.0163× | 0.0161–0.0164× | 2.97× | SLOWER |
| Practice | `cal.atomic.search` | Python engine | 0.0100× | 0.0099–0.0100× | 8.80× | SLOWER |
| Practice | `cal.atomic.search` | Native C engine | 1.0891× | 1.0786–1.0999× | 0.50× | FASTER |
| Practice | `cal.atomic.search` | Rust engine | 0.0192× | 0.0190–0.0193× | 3.14× | SLOWER |
| Practice | `cal.byteslike.findall` | Python engine | 0.0113× | 0.0110–0.0118× | 7.48× | SLOWER |
| Practice | `cal.byteslike.findall` | Native C engine | 2.0470× | 1.9835–2.1404× | 0.18× | FASTER |
| Practice | `cal.byteslike.findall` | Rust engine | 0.0083× | 0.0079–0.0087× | 2.93× | SLOWER |
| Practice | `cal.unicode-name.search` | Python engine | 0.0141× | 0.0140–0.0142× | 4.37× | SLOWER |
| Practice | `cal.unicode-name.search` | Native C engine | 1.4587× | 1.4447–1.4728× | 0.07× | FASTER |
| Practice | `cal.unicode-name.search` | Rust engine | 0.0193× | 0.0191–0.0195× | 3.14× | SLOWER |
| Practice | `cal.ignorecase.findall` | Python engine | 0.0073× | 0.0073–0.0074× | 5.14× | SLOWER |
| Practice | `cal.ignorecase.findall` | Native C engine | 1.4105× | 1.3982–1.4224× | 0.16× | FASTER |
| Practice | `cal.ignorecase.findall` | Rust engine | 0.0083× | 0.0082–0.0083× | 2.96× | SLOWER |
| Practice | `cal.many.split` | Python engine | 0.0126× | 0.0122–0.0131× | 8.86× | SLOWER |
| Practice | `cal.many.split` | Native C engine | 1.2836× | 1.2110–1.3582× | 0.20× | FASTER |
| Practice | `cal.many.split` | Rust engine | 0.0045× | 0.0044–0.0047× | 2.86× | SLOWER |
| Practice | `cal.escape.text` | Python engine | 0.9953× | 0.9931–0.9973× | 1.00× | — |
| Practice | `cal.escape.text` | Native C engine | 0.9970× | 0.9939–0.9998× | 1.00× | — |
| Practice | `cal.escape.text` | Rust engine | 0.9794× | 0.9477–0.9976× | 1.00× | — |
| Practice | `cal.compile.only` | Python engine | 2.1835× | 2.1534–2.2132× | 0.50× | FASTER |
| Practice | `cal.compile.only` | Native C engine | 1.6473× | 1.6236–1.6704× | 1.40× | FASTER |
| Practice | `cal.compile.only` | Rust engine | 1.7707× | 1.7453–1.7947× | 0.56× | FASTER |
| Practice | `cal.scanner.search` | Python engine | 0.0134× | 0.0128–0.0141× | 6.71× | SLOWER |
| Practice | `cal.scanner.search` | Native C engine | 1.1237× | 1.0442–1.2002× | 0.36× | FASTER |
| Practice | `cal.scanner.search` | Rust engine | 0.0091× | 0.0088–0.0096× | 1.98× | SLOWER |
| Practice | `cal.match.surface` | Python engine | 0.0144× | 0.0142–0.0145× | 12.88× | SLOWER |
| Practice | `cal.match.surface` | Native C engine | 1.1885× | 1.0698–1.2645× | 0.42× | FASTER |
| Practice | `cal.match.surface` | Rust engine | 0.0483× | 0.0478–0.0489× | 3.26× | SLOWER |
| Holdout | `hold.search.literal.hit` | Python engine | 0.0076× | 0.0073–0.0081× | 102.00× | SLOWER |
| Holdout | `hold.search.literal.hit` | Native C engine | 1.1373× | 1.0984–1.1927× | 0.73× | FASTER |
| Holdout | `hold.search.literal.hit` | Rust engine | 0.0093× | 0.0090–0.0098× | 33.96× | SLOWER |
| Holdout | `hold.search.literal.miss` | Python engine | 0.0024× | 0.0024–0.0024× | 14408.00× | SLOWER |
| Holdout | `hold.search.literal.miss` | Native C engine | 1.0844× | 0.9898–1.1556× | 0.00× | — |
| Holdout | `hold.search.literal.miss` | Rust engine | 0.0057× | 0.0056–0.0057× | 4375.00× | SLOWER |
| Holdout | `hold.search.long-boundary` | Python engine | 0.0003× | 0.0003–0.0003× | 130.58× | SLOWER |
| Holdout | `hold.search.long-boundary` | Native C engine | 18.2319× | 16.2502–20.4423× | 0.07× | FASTER |
| Holdout | `hold.search.long-boundary` | Rust engine | 0.0010× | 0.0009–0.0011× | 218.22× | SLOWER |
| Holdout | `hold.search.class-anchor` | Python engine | 0.0104× | 0.0099–0.0114× | 11.17× | SLOWER |
| Holdout | `hold.search.class-anchor` | Native C engine | 1.2238× | 1.2124–1.2322× | 0.07× | FASTER |
| Holdout | `hold.search.class-anchor` | Rust engine | 0.0140× | 0.0133–0.0152× | 3.39× | SLOWER |
| Holdout | `hold.match.prefix` | Python engine | 0.0255× | 0.0243–0.0269× | 3.87× | SLOWER |
| Holdout | `hold.match.prefix` | Native C engine | 1.2276× | 1.1836–1.2917× | 0.07× | FASTER |
| Holdout | `hold.match.prefix` | Rust engine | 0.0168× | 0.0162–0.0176× | 2.87× | SLOWER |
| Holdout | `hold.fullmatch.structured` | Python engine | 0.0114× | 0.0113–0.0115× | 16.36× | SLOWER |
| Holdout | `hold.fullmatch.structured` | Native C engine | 1.1300× | 1.0767–1.1679× | 0.07× | FASTER |
| Holdout | `hold.fullmatch.structured` | Rust engine | 0.0193× | 0.0192–0.0195× | 3.04× | SLOWER |
| Holdout | `hold.search.look-capture` | Python engine | 0.0098× | 0.0097–0.0098× | 17.64× | SLOWER |
| Holdout | `hold.search.look-capture` | Native C engine | 1.0349× | 0.9839–1.0658× | 0.08× | — |
| Holdout | `hold.search.look-capture` | Rust engine | 0.0167× | 0.0166–0.0168× | 3.26× | SLOWER |
| Holdout | `hold.findall.tokens` | Python engine | 0.0105× | 0.0104–0.0106× | 11.27× | SLOWER |
| Holdout | `hold.findall.tokens` | Native C engine | 1.6113× | 1.5380–1.6571× | 0.21× | FASTER |
| Holdout | `hold.findall.tokens` | Rust engine | 0.0057× | 0.0057–0.0058× | 3.10× | SLOWER |
| Holdout | `hold.finditer.groups` | Python engine | 0.0127× | 0.0125–0.0129× | 7.75× | SLOWER |
| Holdout | `hold.finditer.groups` | Native C engine | 1.4362× | 1.4128–1.4630× | 0.39× | FASTER |
| Holdout | `hold.finditer.groups` | Rust engine | 0.0089× | 0.0088–0.0091× | 1.93× | SLOWER |
| Holdout | `hold.split.capture` | Python engine | 0.0102× | 0.0100–0.0105× | 11.37× | SLOWER |
| Holdout | `hold.split.capture` | Native C engine | 1.9347× | 1.8978–1.9808× | 0.20× | FASTER |
| Holdout | `hold.split.capture` | Rust engine | 0.0068× | 0.0067–0.0070× | 2.62× | SLOWER |
| Holdout | `hold.sub.template` | Python engine | 0.0162× | 0.0160–0.0164× | 9.29× | SLOWER |
| Holdout | `hold.sub.template` | Native C engine | 1.7562× | 1.7148–1.7859× | 0.12× | FASTER |
| Holdout | `hold.sub.template` | Rust engine | 0.0148× | 0.0147–0.0149× | 2.39× | SLOWER |
| Holdout | `hold.subn.callable` | Python engine | 0.0274× | 0.0258–0.0294× | 4.58× | SLOWER |
| Holdout | `hold.subn.callable` | Native C engine | 1.1958× | 1.1466–1.2715× | 0.25× | FASTER |
| Holdout | `hold.subn.callable` | Rust engine | 0.0229× | 0.0219–0.0244× | 2.53× | SLOWER |
| Holdout | `hold.bytes.tokens` | Python engine | 0.0102× | 0.0101–0.0102× | 8.71× | SLOWER |
| Holdout | `hold.bytes.tokens` | Native C engine | 2.0819× | 2.0504–2.1127× | 0.18× | FASTER |
| Holdout | `hold.bytes.tokens` | Rust engine | 0.0083× | 0.0082–0.0084× | 2.92× | SLOWER |
| Holdout | `hold.unicode.words` | Python engine | 0.0089× | 0.0087–0.0092× | 6.63× | SLOWER |
| Holdout | `hold.unicode.words` | Native C engine | 1.7406× | 1.7101–1.7880× | 0.20× | FASTER |
| Holdout | `hold.unicode.words` | Rust engine | 0.0119× | 0.0117–0.0123× | 2.67× | SLOWER |
| Holdout | `hold.cold.compile-search` | Python engine | 0.4723× | 0.4580–0.4830× | 5.95× | SLOWER |
| Holdout | `hold.cold.compile-search` | Native C engine | 0.8131× | 0.8017–0.8259× | 1.55× | — |
| Holdout | `hold.cold.compile-search` | Rust engine | 0.7331× | 0.7237–0.7431× | 1.93× | SLOWER |
| Holdout | `hold.module.warm` | Python engine | 0.0192× | 0.0190–0.0196× | 7.12× | SLOWER |
| Holdout | `hold.module.warm` | Native C engine | 1.1839× | 1.1639–1.2086× | 0.07× | FASTER |
| Holdout | `hold.module.warm` | Rust engine | 0.0315× | 0.0310–0.0321× | 3.38× | SLOWER |
| Holdout | `hold.empty.finditer` | Python engine | 0.0091× | 0.0089–0.0093× | 8.52× | SLOWER |
| Holdout | `hold.empty.finditer` | Native C engine | 2.2352× | 2.2054–2.2709× | 0.37× | FASTER |
| Holdout | `hold.empty.finditer` | Rust engine | 0.0213× | 0.0209–0.0218× | 1.62× | SLOWER |
| Holdout | `hold.backref.fullmatch` | Python engine | 0.0180× | 0.0178–0.0182× | 6.99× | SLOWER |
| Holdout | `hold.backref.fullmatch` | Native C engine | 1.2129× | 1.1887–1.2316× | 0.08× | FASTER |
| Holdout | `hold.backref.fullmatch` | Rust engine | 0.0190× | 0.0188–0.0191× | 3.04× | SLOWER |
| Holdout | `hold.conditional.match` | Python engine | 0.0188× | 0.0185–0.0192× | 6.78× | SLOWER |
| Holdout | `hold.conditional.match` | Native C engine | 1.1275× | 1.0771–1.1820× | 0.08× | FASTER |
| Holdout | `hold.conditional.match` | Rust engine | 0.0183× | 0.0181–0.0185× | 2.94× | SLOWER |
| Holdout | `hold.atomic.search` | Python engine | 0.0102× | 0.0102–0.0103× | 6.53× | SLOWER |
| Holdout | `hold.atomic.search` | Native C engine | 1.4733× | 1.4574–1.4889× | 0.07× | FASTER |
| Holdout | `hold.atomic.search` | Rust engine | 0.0213× | 0.0212–0.0214× | 3.13× | SLOWER |
| Holdout | `hold.byteslike.findall` | Python engine | 0.0111× | 0.0110–0.0112× | 7.39× | SLOWER |
| Holdout | `hold.byteslike.findall` | Native C engine | 2.0241× | 2.0126–2.0352× | 0.18× | FASTER |
| Holdout | `hold.byteslike.findall` | Rust engine | 0.0081× | 0.0080–0.0082× | 2.83× | SLOWER |
| Holdout | `hold.unicode-name.search` | Python engine | 0.0128× | 0.0127–0.0128× | 4.69× | SLOWER |
| Holdout | `hold.unicode-name.search` | Native C engine | 1.4770× | 1.4684–1.4873× | 0.07× | FASTER |
| Holdout | `hold.unicode-name.search` | Rust engine | 0.0191× | 0.0190–0.0193× | 3.14× | SLOWER |
| Holdout | `hold.ignorecase.findall` | Python engine | 0.0075× | 0.0075–0.0076× | 4.86× | SLOWER |
| Holdout | `hold.ignorecase.findall` | Native C engine | 1.4046× | 1.3938–1.4165× | 0.16× | FASTER |
| Holdout | `hold.ignorecase.findall` | Rust engine | 0.0090× | 0.0090–0.0091× | 2.94× | SLOWER |
| Holdout | `hold.many.split` | Python engine | 0.0126× | 0.0124–0.0128× | 8.86× | SLOWER |
| Holdout | `hold.many.split` | Native C engine | 1.2627× | 1.2170–1.2927× | 0.20× | FASTER |
| Holdout | `hold.many.split` | Rust engine | 0.0046× | 0.0045–0.0047× | 2.86× | SLOWER |
| Holdout | `hold.escape.bytes` | Python engine | 1.0191× | 1.0111–1.0294× | 0.68× | FASTER |
| Holdout | `hold.escape.bytes` | Native C engine | 0.9968× | 0.9662–1.0221× | 0.68× | — |
| Holdout | `hold.escape.bytes` | Rust engine | 0.9951× | 0.9510–1.0236× | 0.68× | — |
| Holdout | `hold.compile.only` | Python engine | 1.9876× | 1.9191–2.0529× | 0.54× | FASTER |
| Holdout | `hold.compile.only` | Native C engine | 1.3684× | 1.3210–1.4068× | 1.91× | FASTER |
| Holdout | `hold.compile.only` | Rust engine | 1.6521× | 1.6153–1.6829× | 0.60× | FASTER |
| Holdout | `hold.scanner.search` | Python engine | 0.0129× | 0.0128–0.0131× | 6.71× | SLOWER |
| Holdout | `hold.scanner.search` | Native C engine | 1.1056× | 1.0851–1.1276× | 0.36× | FASTER |
| Holdout | `hold.scanner.search` | Rust engine | 0.0087× | 0.0086–0.0089× | 1.98× | SLOWER |
| Holdout | `hold.match.surface` | Python engine | 0.0225× | 0.0217–0.0236× | 12.79× | SLOWER |
| Holdout | `hold.match.surface` | Native C engine | 1.0641× | 1.0205–1.1153× | 0.41× | FASTER |
| Holdout | `hold.match.surface` | Rust engine | 0.0436× | 0.0418–0.0458× | 3.25× | SLOWER |
| Practice | `cal.real.log` | Python engine | 0.0029× | 0.0028–0.0030× | 27.33× | SLOWER |
| Practice | `cal.real.log` | Native C engine | 0.9300× | 0.9004–0.9622× | 0.33× | — |
| Practice | `cal.real.log` | Rust engine | 0.0059× | 0.0057–0.0061× | 3.19× | SLOWER |
| Practice | `cal.real.url` | Python engine | 0.0062× | 0.0062–0.0063× | 26.38× | SLOWER |
| Practice | `cal.real.url` | Native C engine | 0.9310× | 0.9192–0.9439× | 0.11× | — |
| Practice | `cal.real.url` | Rust engine | 0.0117× | 0.0115–0.0118× | 3.49× | SLOWER |
| Practice | `cal.real.email` | Python engine | 0.0053× | 0.0053–0.0054× | 9.90× | SLOWER |
| Practice | `cal.real.email` | Native C engine | 0.6625× | 0.6562–0.6705× | 0.12× | SLOWER |
| Practice | `cal.real.email` | Rust engine | 0.0059× | 0.0058–0.0059× | 3.85× | SLOWER |
| Practice | `cal.real.datetime` | Python engine | 0.0075× | 0.0075–0.0076× | 23.68× | SLOWER |
| Practice | `cal.real.datetime` | Native C engine | 1.0013× | 0.9912–1.0121× | 0.09× | — |
| Practice | `cal.real.datetime` | Rust engine | 0.0153× | 0.0151–0.0155× | 3.49× | SLOWER |
| Practice | `cal.real.version` | Python engine | 0.0113× | 0.0108–0.0122× | 22.95× | SLOWER |
| Practice | `cal.real.version` | Native C engine | 1.6573× | 1.5798–1.7955× | 0.00× | FASTER |
| Practice | `cal.real.version` | Rust engine | 0.0297× | 0.0283–0.0322× | 3.46× | SLOWER |
| Practice | `cal.real.uuid` | Python engine | 0.0067× | 0.0065–0.0071× | 18.66× | SLOWER |
| Practice | `cal.real.uuid` | Native C engine | 1.0946× | 1.0640–1.1319× | 0.07× | FASTER |
| Practice | `cal.real.uuid` | Rust engine | 0.0140× | 0.0135–0.0147× | 3.96× | SLOWER |
| Practice | `cal.real.ip` | Python engine | 0.0081× | 0.0080–0.0082× | 29.12× | SLOWER |
| Practice | `cal.real.ip` | Native C engine | 1.0772× | 1.0620–1.0886× | 0.07× | FASTER |
| Practice | `cal.real.ip` | Rust engine | 0.0265× | 0.0261–0.0268× | 3.02× | SLOWER |
| Practice | `cal.real.path` | Python engine | 0.0057× | 0.0056–0.0057× | 30.63× | SLOWER |
| Practice | `cal.real.path` | Native C engine | 0.9816× | 0.9700–0.9933× | 0.12× | — |
| Practice | `cal.real.path` | Rust engine | 0.0104× | 0.0103–0.0105× | 3.60× | SLOWER |
| Practice | `cal.real.config` | Python engine | 0.0086× | 0.0083–0.0090× | 16.04× | SLOWER |
| Practice | `cal.real.config` | Native C engine | 1.1145× | 1.0745–1.1670× | 0.35× | FASTER |
| Practice | `cal.real.config` | Rust engine | 0.0173× | 0.0168–0.0180× | 2.32× | SLOWER |
| Practice | `cal.real.comments` | Python engine | 0.0063× | 0.0061–0.0064× | 11.73× | SLOWER |
| Practice | `cal.real.comments` | Native C engine | 1.0689× | 1.0482–1.0894× | 0.14× | FASTER |
| Practice | `cal.real.comments` | Rust engine | 0.0038× | 0.0037–0.0039× | 3.74× | SLOWER |
| Practice | `cal.real.whitespace` | Python engine | 0.0069× | 0.0067–0.0072× | 8.36× | SLOWER |
| Practice | `cal.real.whitespace` | Native C engine | 1.4168× | 1.3301–1.4982× | 0.14× | FASTER |
| Practice | `cal.real.whitespace` | Rust engine | 0.0076× | 0.0074–0.0080× | 2.79× | SLOWER |
| Practice | `cal.real.lines` | Python engine | 0.0094× | 0.0093–0.0096× | 14.09× | SLOWER |
| Practice | `cal.real.lines` | Native C engine | 1.6134× | 1.5715–1.6463× | 0.15× | FASTER |
| Practice | `cal.real.lines` | Rust engine | 0.0092× | 0.0091–0.0093× | 2.83× | SLOWER |
| Practice | `cal.real.markup` | Python engine | 0.0046× | 0.0045–0.0047× | 13.23× | SLOWER |
| Practice | `cal.real.markup` | Native C engine | 0.9205× | 0.8848–0.9513× | 0.10× | — |
| Practice | `cal.real.markup` | Rust engine | 0.0037× | 0.0037–0.0038× | 4.19× | SLOWER |
| Practice | `cal.real.quotes` | Python engine | 0.0044× | 0.0042–0.0045× | 18.83× | SLOWER |
| Practice | `cal.real.quotes` | Native C engine | 1.5962× | 1.5548–1.6633× | 0.10× | FASTER |
| Practice | `cal.real.quotes` | Rust engine | 0.0075× | 0.0073–0.0078× | 3.83× | SLOWER |
| Practice | `cal.real.csv` | Python engine | 0.0049× | 0.0048–0.0050× | 19.83× | SLOWER |
| Practice | `cal.real.csv` | Native C engine | 2.4587× | 2.3952–2.5540× | 0.29× | FASTER |
| Practice | `cal.real.csv` | Rust engine | 0.0106× | 0.0103–0.0109× | 2.97× | SLOWER |
| Practice | `cal.branch.prefix` | Python engine | 0.0093× | 0.0092–0.0095× | 12.65× | SLOWER |
| Practice | `cal.branch.prefix` | Native C engine | 0.8717× | 0.8563–0.8859× | 0.07× | — |
| Practice | `cal.branch.prefix` | Rust engine | 0.0129× | 0.0127–0.0131× | 3.37× | SLOWER |
| Practice | `cal.branch.miss` | Python engine | 0.0010× | 0.0009–0.0010× | 83.64× | SLOWER |
| Practice | `cal.branch.miss` | Native C engine | 0.5139× | 0.4847–0.5475× | 0.00× | SLOWER |
| Practice | `cal.branch.miss` | Rust engine | 0.0128× | 0.0125–0.0133× | 4.25× | SLOWER |
| Practice | `cal.repeat.nested` | Python engine | 0.0099× | 0.0098–0.0101× | 15.24× | SLOWER |
| Practice | `cal.repeat.nested` | Native C engine | 1.1992× | 1.1873–1.2142× | 0.64× | FASTER |
| Practice | `cal.repeat.nested` | Rust engine | 0.0234× | 0.0231–0.0238× | 1.57× | SLOWER |
| Practice | `cal.lines.records` | Python engine | 0.0086× | 0.0081–0.0091× | 14.74× | SLOWER |
| Practice | `cal.lines.records` | Native C engine | 1.1337× | 1.0776–1.1952× | 0.36× | FASTER |
| Practice | `cal.lines.records` | Rust engine | 0.0074× | 0.0070–0.0078× | 2.56× | SLOWER |
| Practice | `cal.block.dotall` | Python engine | 0.0064× | 0.0064–0.0065× | 17.13× | SLOWER |
| Practice | `cal.block.dotall` | Native C engine | 1.4561× | 1.4383–1.4764× | 0.08× | FASTER |
| Practice | `cal.block.dotall` | Rust engine | 0.0129× | 0.0128–0.0131× | 3.97× | SLOWER |
| Practice | `cal.pattern.verbose` | Python engine | 0.0040× | 0.0040–0.0040× | 14.85× | SLOWER |
| Practice | `cal.pattern.verbose` | Native C engine | 1.6401× | 1.6271–1.6523× | 0.09× | FASTER |
| Practice | `cal.pattern.verbose` | Rust engine | 0.0194× | 0.0193–0.0196× | 3.43× | SLOWER |
| Practice | `cal.mode.ascii` | Python engine | 0.0054× | 0.0053–0.0054× | 7.27× | SLOWER |
| Practice | `cal.mode.ascii` | Native C engine | 1.0918× | 1.0855–1.0973× | 0.13× | FASTER |
| Practice | `cal.mode.ascii` | Rust engine | 0.0093× | 0.0091–0.0095× | 3.04× | SLOWER |
| Practice | `cal.mode.casefold` | Python engine | 0.0084× | 0.0082–0.0089× | 5.52× | SLOWER |
| Practice | `cal.mode.casefold` | Native C engine | 1.4906× | 1.4499–1.5692× | 0.20× | FASTER |
| Practice | `cal.mode.casefold` | Rust engine | 0.0091× | 0.0088–0.0096× | 2.90× | SLOWER |
| Practice | `cal.mode.astral` | Python engine | 0.0096× | 0.0095–0.0100× | 7.05× | SLOWER |
| Practice | `cal.mode.astral` | Native C engine | 1.7766× | 1.7385–1.8364× | 0.25× | FASTER |
| Practice | `cal.mode.astral` | Rust engine | 0.0094× | 0.0092–0.0097× | 2.76× | SLOWER |
| Practice | `cal.look.negative-ahead` | Python engine | 0.0037× | 0.0036–0.0039× | 15.69× | SLOWER |
| Practice | `cal.look.negative-ahead` | Native C engine | 0.9020× | 0.8746–0.9480× | 0.14× | — |
| Practice | `cal.look.negative-ahead` | Rust engine | 0.0073× | 0.0071–0.0076× | 3.46× | SLOWER |
| Practice | `cal.look.negative-behind` | Python engine | 0.0065× | 0.0064–0.0065× | 12.65× | SLOWER |
| Practice | `cal.look.negative-behind` | Native C engine | 1.1627× | 1.0856–1.2055× | 0.10× | FASTER |
| Practice | `cal.look.negative-behind` | Rust engine | 0.0098× | 0.0097–0.0098× | 3.19× | SLOWER |
| Practice | `cal.bytes.replace` | Python engine | 0.0165× | 0.0160–0.0169× | 9.71× | SLOWER |
| Practice | `cal.bytes.replace` | Native C engine | 1.0083× | 0.9802–1.0312× | 1.18× | — |
| Practice | `cal.bytes.replace` | Rust engine | 0.0159× | 0.0154–0.0162× | 2.52× | SLOWER |
| Practice | `cal.bytes.scan` | Python engine | 0.0117× | 0.0112–0.0125× | 8.55× | SLOWER |
| Practice | `cal.bytes.scan` | Native C engine | 1.2490× | 1.1538–1.3095× | 0.38× | FASTER |
| Practice | `cal.bytes.scan` | Rust engine | 0.0095× | 0.0090–0.0103× | 1.87× | SLOWER |
| Practice | `cal.compile.complex` | Python engine | 1.7586× | 1.7296–1.7936× | 0.39× | FASTER |
| Practice | `cal.compile.complex` | Native C engine | 1.3792× | 1.3554–1.4061× | 1.64× | FASTER |
| Practice | `cal.compile.complex` | Rust engine | 1.6895× | 1.6387–1.7312× | 0.52× | FASTER |
| Practice | `cal.module.replace` | Python engine | 0.0227× | 0.0210–0.0249× | 10.12× | SLOWER |
| Practice | `cal.module.replace` | Native C engine | 1.2733× | 1.1973–1.3997× | 0.04× | FASTER |
| Practice | `cal.module.replace` | Rust engine | 0.0217× | 0.0198–0.0243× | 2.52× | SLOWER |
| Practice | `cal.zero.boundary` | Python engine | 0.0075× | 0.0073–0.0077× | 13.81× | SLOWER |
| Practice | `cal.zero.boundary` | Native C engine | 2.1069× | 2.0595–2.1667× | 0.42× | FASTER |
| Practice | `cal.zero.boundary` | Rust engine | 0.0131× | 0.0128–0.0135× | 1.69× | SLOWER |
| Practice | `cal.dense.iter` | Python engine | 0.0160× | 0.0157–0.0164× | 4.92× | SLOWER |
| Practice | `cal.dense.iter` | Native C engine | 1.3844× | 1.3501–1.4266× | 0.51× | FASTER |
| Practice | `cal.dense.iter` | Rust engine | 0.0083× | 0.0082–0.0085× | 1.49× | SLOWER |
| Practice | `cal.capture.optional` | Python engine | 0.0107× | 0.0106–0.0108× | 14.26× | SLOWER |
| Practice | `cal.capture.optional` | Native C engine | 1.1840× | 1.1436–1.2143× | 0.18× | FASTER |
| Practice | `cal.capture.optional` | Rust engine | 0.0091× | 0.0090–0.0092× | 2.79× | SLOWER |
| Practice | `cal.split.limited` | Python engine | 0.0065× | 0.0064–0.0066× | 7.47× | SLOWER |
| Practice | `cal.split.limited` | Native C engine | 1.1659× | 1.1514–1.1820× | 0.19× | FASTER |
| Practice | `cal.split.limited` | Rust engine | 0.0076× | 0.0075–0.0076× | 2.82× | SLOWER |
| Practice | `cal.replace.limited` | Python engine | 0.0133× | 0.0131–0.0135× | 6.04× | SLOWER |
| Practice | `cal.replace.limited` | Native C engine | 1.3279× | 1.3025–1.3524× | 0.15× | FASTER |
| Practice | `cal.replace.limited` | Rust engine | 0.0094× | 0.0093–0.0095× | 2.90× | SLOWER |
| Practice | `cal.bytes.view-long` | Python engine | 0.0067× | 0.0065–0.0068× | 48.64× | SLOWER |
| Practice | `cal.bytes.view-long` | Native C engine | 1.3157× | 1.2851–1.3458× | 0.60× | FASTER |
| Practice | `cal.bytes.view-long` | Rust engine | 0.0009× | 0.0009–0.0010× | 5.61× | SLOWER |
| Practice | `cal.window.search` | Python engine | 0.0192× | 0.0188–0.0197× | 4.40× | SLOWER |
| Practice | `cal.window.search` | Native C engine | 1.0184× | 0.9746–1.0863× | 0.18× | — |
| Practice | `cal.window.search` | Rust engine | 0.0157× | 0.0152–0.0164× | 3.30× | SLOWER |
| Practice | `cal.window.findall` | Python engine | 0.0168× | 0.0167–0.0168× | 4.02× | SLOWER |
| Practice | `cal.window.findall` | Native C engine | 1.0297× | 0.9920–1.0521× | 0.23× | — |
| Practice | `cal.window.findall` | Rust engine | 0.0074× | 0.0073–0.0075× | 3.01× | SLOWER |
| Practice | `cal.window.scanner` | Python engine | 0.0170× | 0.0165–0.0174× | 4.46× | SLOWER |
| Practice | `cal.window.scanner` | Native C engine | 1.0497× | 0.9902–1.0874× | 0.30× | — |
| Practice | `cal.window.scanner` | Rust engine | 0.0093× | 0.0092–0.0094× | 2.20× | SLOWER |
| Practice | `cal.window.match` | Python engine | 0.0353× | 0.0343–0.0360× | 3.55× | SLOWER |
| Practice | `cal.window.match` | Native C engine | 0.9796× | 0.9720–0.9861× | 0.18× | — |
| Practice | `cal.window.match` | Rust engine | 0.0182× | 0.0180–0.0185× | 2.45× | SLOWER |
| Practice | `cal.literal.replace` | Python engine | 0.0061× | 0.0057–0.0069× | 41.75× | SLOWER |
| Practice | `cal.literal.replace` | Native C engine | 1.1168× | 0.9669–1.3022× | 0.53× | — |
| Practice | `cal.literal.replace` | Rust engine | 0.0054× | 0.0050–0.0061× | 10.40× | SLOWER |
| Practice | `cal.template.repeat` | Python engine | 0.0190× | 0.0183–0.0200× | 6.29× | SLOWER |
| Practice | `cal.template.repeat` | Native C engine | 1.4474× | 1.2790–1.6069× | 0.15× | FASTER |
| Practice | `cal.template.repeat` | Rust engine | 0.0130× | 0.0125–0.0136× | 2.29× | SLOWER |
| Practice | `cal.match.miss` | Python engine | 0.0285× | 0.0268–0.0314× | 5.02× | SLOWER |
| Practice | `cal.match.miss` | Native C engine | 1.1137× | 1.0533–1.1638× | 0.00× | FASTER |
| Practice | `cal.match.miss` | Rust engine | 0.0079× | 0.0072–0.0088× | 4.00× | SLOWER |
| Practice | `cal.fullmatch.miss` | Python engine | 0.0153× | 0.0142–0.0164× | 11.09× | SLOWER |
| Practice | `cal.fullmatch.miss` | Native C engine | 1.3806× | 1.3185–1.4445× | 0.00× | FASTER |
| Practice | `cal.fullmatch.miss` | Rust engine | 0.0200× | 0.0189–0.0213× | 3.32× | SLOWER |
| Holdout | `hold.real.log` | Python engine | 0.0027× | 0.0026–0.0029× | 36.41× | SLOWER |
| Holdout | `hold.real.log` | Native C engine | 0.8742× | 0.8120–0.9443× | 0.33× | — |
| Holdout | `hold.real.log` | Rust engine | 0.0057× | 0.0054–0.0061× | 3.23× | SLOWER |
| Holdout | `hold.real.url` | Python engine | 0.0054× | 0.0053–0.0055× | 26.93× | SLOWER |
| Holdout | `hold.real.url` | Native C engine | 0.8724× | 0.8483–0.9094× | 0.11× | — |
| Holdout | `hold.real.url` | Rust engine | 0.0105× | 0.0102–0.0109× | 3.79× | SLOWER |
| Holdout | `hold.real.email` | Python engine | 0.0041× | 0.0041–0.0042× | 12.09× | SLOWER |
| Holdout | `hold.real.email` | Native C engine | 0.8082× | 0.7321–0.8680× | 0.12× | — |
| Holdout | `hold.real.email` | Rust engine | 0.0067× | 0.0066–0.0067× | 3.88× | SLOWER |
| Holdout | `hold.real.datetime` | Python engine | 0.0073× | 0.0072–0.0074× | 27.33× | SLOWER |
| Holdout | `hold.real.datetime` | Native C engine | 1.0702× | 1.0524–1.0900× | 0.09× | FASTER |
| Holdout | `hold.real.datetime` | Rust engine | 0.0166× | 0.0164–0.0168× | 3.42× | SLOWER |
| Holdout | `hold.real.version` | Python engine | 0.0092× | 0.0091–0.0093× | 23.70× | SLOWER |
| Holdout | `hold.real.version` | Native C engine | 1.1030× | 0.9912–1.1746× | 0.06× | — |
| Holdout | `hold.real.version` | Rust engine | 0.0207× | 0.0205–0.0209× | 3.01× | SLOWER |
| Holdout | `hold.real.uuid` | Python engine | 0.0064× | 0.0061–0.0072× | 18.05× | SLOWER |
| Holdout | `hold.real.uuid` | Native C engine | 1.0428× | 0.9831–1.1587× | 0.07× | — |
| Holdout | `hold.real.uuid` | Rust engine | 0.0136× | 0.0129–0.0151× | 3.95× | SLOWER |
| Holdout | `hold.real.ip` | Python engine | 0.0088× | 0.0086–0.0089× | 30.05× | SLOWER |
| Holdout | `hold.real.ip` | Native C engine | 1.1304× | 1.1094–1.1513× | 0.07× | FASTER |
| Holdout | `hold.real.ip` | Rust engine | 0.0213× | 0.0209–0.0217× | 3.02× | SLOWER |
| Holdout | `hold.real.path` | Python engine | 0.0055× | 0.0054–0.0056× | 26.39× | SLOWER |
| Holdout | `hold.real.path` | Native C engine | 0.9505× | 0.8936–0.9864× | 0.12× | — |
| Holdout | `hold.real.path` | Rust engine | 0.0093× | 0.0091–0.0094× | 3.84× | SLOWER |
| Holdout | `hold.real.config` | Python engine | 0.0081× | 0.0079–0.0083× | 18.02× | SLOWER |
| Holdout | `hold.real.config` | Native C engine | 1.0674× | 1.0447–1.0897× | 0.35× | FASTER |
| Holdout | `hold.real.config` | Rust engine | 0.0147× | 0.0144–0.0150× | 2.32× | SLOWER |
| Holdout | `hold.real.comments` | Python engine | 0.0049× | 0.0047–0.0051× | 16.97× | SLOWER |
| Holdout | `hold.real.comments` | Native C engine | 1.0118× | 0.9784–1.0564× | 0.14× | — |
| Holdout | `hold.real.comments` | Rust engine | 0.0033× | 0.0032–0.0035× | 4.05× | SLOWER |
| Holdout | `hold.real.whitespace` | Python engine | 0.0074× | 0.0072–0.0078× | 8.45× | SLOWER |
| Holdout | `hold.real.whitespace` | Native C engine | 1.5107× | 1.4680–1.5895× | 0.14× | FASTER |
| Holdout | `hold.real.whitespace` | Rust engine | 0.0073× | 0.0071–0.0077× | 2.74× | SLOWER |
| Holdout | `hold.real.lines` | Python engine | 0.0096× | 0.0095–0.0097× | 13.22× | SLOWER |
| Holdout | `hold.real.lines` | Native C engine | 1.5727× | 1.5626–1.5824× | 0.14× | FASTER |
| Holdout | `hold.real.lines` | Rust engine | 0.0091× | 0.0089–0.0092× | 2.82× | SLOWER |
| Holdout | `hold.real.markup` | Python engine | 0.0046× | 0.0045–0.0048× | 14.16× | SLOWER |
| Holdout | `hold.real.markup` | Native C engine | 0.9144× | 0.8506–0.9819× | 0.13× | — |
| Holdout | `hold.real.markup` | Rust engine | 0.0031× | 0.0030–0.0032× | 4.34× | SLOWER |
| Holdout | `hold.real.quotes` | Python engine | 0.0041× | 0.0041–0.0042× | 18.87× | SLOWER |
| Holdout | `hold.real.quotes` | Native C engine | 1.5111× | 1.4976–1.5270× | 0.10× | FASTER |
| Holdout | `hold.real.quotes` | Rust engine | 0.0072× | 0.0071–0.0072× | 3.58× | SLOWER |
| Holdout | `hold.real.csv` | Python engine | 0.0043× | 0.0040–0.0049× | 18.08× | SLOWER |
| Holdout | `hold.real.csv` | Native C engine | 2.3866× | 2.0638–2.7584× | 0.30× | FASTER |
| Holdout | `hold.real.csv` | Rust engine | 0.0100× | 0.0093–0.0113× | 3.21× | SLOWER |
| Holdout | `hold.branch.prefix` | Python engine | 0.0095× | 0.0094–0.0097× | 11.86× | SLOWER |
| Holdout | `hold.branch.prefix` | Native C engine | 0.8504× | 0.7934–0.8872× | 0.07× | — |
| Holdout | `hold.branch.prefix` | Rust engine | 0.0128× | 0.0126–0.0129× | 3.36× | SLOWER |
| Holdout | `hold.branch.miss` | Python engine | 0.0008× | 0.0008–0.0008× | 80.13× | SLOWER |
| Holdout | `hold.branch.miss` | Native C engine | 0.8149× | 0.8037–0.8260× | 0.00× | — |
| Holdout | `hold.branch.miss` | Rust engine | 0.0110× | 0.0109–0.0111× | 4.57× | SLOWER |
| Holdout | `hold.repeat.nested` | Python engine | 0.0099× | 0.0094–0.0108× | 15.24× | SLOWER |
| Holdout | `hold.repeat.nested` | Native C engine | 1.0636× | 0.9595–1.1893× | 0.64× | — |
| Holdout | `hold.repeat.nested` | Rust engine | 0.0217× | 0.0212–0.0222× | 1.57× | SLOWER |
| Holdout | `hold.lines.records` | Python engine | 0.0085× | 0.0082–0.0087× | 14.74× | SLOWER |
| Holdout | `hold.lines.records` | Native C engine | 1.0881× | 1.0199–1.1388× | 0.36× | FASTER |
| Holdout | `hold.lines.records` | Rust engine | 0.0076× | 0.0074–0.0078× | 2.55× | SLOWER |
| Holdout | `hold.block.dotall` | Python engine | 0.0063× | 0.0063–0.0064× | 18.13× | SLOWER |
| Holdout | `hold.block.dotall` | Native C engine | 1.4983× | 1.4818–1.5151× | 0.08× | FASTER |
| Holdout | `hold.block.dotall` | Rust engine | 0.0132× | 0.0130–0.0133× | 4.00× | SLOWER |
| Holdout | `hold.pattern.verbose` | Python engine | 0.0038× | 0.0036–0.0041× | 15.91× | SLOWER |
| Holdout | `hold.pattern.verbose` | Native C engine | 2.3859× | 2.3585–2.4191× | 0.09× | FASTER |
| Holdout | `hold.pattern.verbose` | Rust engine | 0.0260× | 0.0246–0.0286× | 3.45× | SLOWER |
| Holdout | `hold.mode.ascii` | Python engine | 0.0053× | 0.0052–0.0054× | 7.82× | SLOWER |
| Holdout | `hold.mode.ascii` | Native C engine | 1.0992× | 1.0193–1.1685× | 0.21× | FASTER |
| Holdout | `hold.mode.ascii` | Rust engine | 0.0078× | 0.0077–0.0080× | 3.02× | SLOWER |
| Holdout | `hold.mode.casefold` | Python engine | 0.0081× | 0.0079–0.0082× | 5.44× | SLOWER |
| Holdout | `hold.mode.casefold` | Native C engine | 1.5106× | 1.4880–1.5337× | 0.18× | FASTER |
| Holdout | `hold.mode.casefold` | Rust engine | 0.0104× | 0.0102–0.0105× | 2.93× | SLOWER |
| Holdout | `hold.mode.astral` | Python engine | 0.0094× | 0.0093–0.0095× | 7.06× | SLOWER |
| Holdout | `hold.mode.astral` | Native C engine | 1.6796× | 1.5935–1.7349× | 0.25× | FASTER |
| Holdout | `hold.mode.astral` | Rust engine | 0.0093× | 0.0092–0.0095× | 2.77× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Python engine | 0.0035× | 0.0035–0.0036× | 16.30× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Native C engine | 0.8627× | 0.7971–0.9115× | 0.14× | — |
| Holdout | `hold.look.negative-ahead` | Rust engine | 0.0071× | 0.0071–0.0072× | 3.47× | SLOWER |
| Holdout | `hold.look.negative-behind` | Python engine | 0.0065× | 0.0064–0.0066× | 12.65× | SLOWER |
| Holdout | `hold.look.negative-behind` | Native C engine | 1.2098× | 1.2001–1.2195× | 0.10× | FASTER |
| Holdout | `hold.look.negative-behind` | Rust engine | 0.0098× | 0.0098–0.0099× | 3.19× | SLOWER |
| Holdout | `hold.bytes.replace` | Python engine | 0.0174× | 0.0165–0.0192× | 9.71× | SLOWER |
| Holdout | `hold.bytes.replace` | Native C engine | 1.0366× | 0.9170–1.1838× | 1.16× | — |
| Holdout | `hold.bytes.replace` | Rust engine | 0.0163× | 0.0149–0.0182× | 2.52× | SLOWER |
| Holdout | `hold.bytes.scan` | Python engine | 0.0113× | 0.0109–0.0119× | 8.55× | SLOWER |
| Holdout | `hold.bytes.scan` | Native C engine | 1.2497× | 1.2068–1.3144× | 0.38× | FASTER |
| Holdout | `hold.bytes.scan` | Rust engine | 0.0090× | 0.0087–0.0095× | 1.87× | SLOWER |
| Holdout | `hold.compile.complex` | Python engine | 1.7552× | 1.7333–1.7793× | 0.37× | FASTER |
| Holdout | `hold.compile.complex` | Native C engine | 1.4300× | 1.4136–1.4492× | 1.67× | FASTER |
| Holdout | `hold.compile.complex` | Rust engine | 1.5519× | 1.5161–1.5841× | 0.55× | FASTER |
| Holdout | `hold.module.replace` | Python engine | 0.0211× | 0.0205–0.0217× | 10.12× | SLOWER |
| Holdout | `hold.module.replace` | Native C engine | 1.2373× | 1.1920–1.2779× | 0.04× | FASTER |
| Holdout | `hold.module.replace` | Rust engine | 0.0201× | 0.0197–0.0206× | 2.52× | SLOWER |
| Holdout | `hold.zero.boundary` | Python engine | 0.0084× | 0.0081–0.0088× | 8.20× | SLOWER |
| Holdout | `hold.zero.boundary` | Native C engine | 2.2182× | 2.1157–2.3311× | 0.42× | FASTER |
| Holdout | `hold.zero.boundary` | Rust engine | 0.0148× | 0.0142–0.0154× | 1.67× | SLOWER |
| Holdout | `hold.dense.iter` | Python engine | 0.0156× | 0.0153–0.0158× | 4.92× | SLOWER |
| Holdout | `hold.dense.iter` | Native C engine | 1.3429× | 1.2941–1.3808× | 0.51× | FASTER |
| Holdout | `hold.dense.iter` | Rust engine | 0.0080× | 0.0078–0.0081× | 1.50× | SLOWER |
| Holdout | `hold.capture.optional` | Python engine | 0.0111× | 0.0104–0.0123× | 14.26× | SLOWER |
| Holdout | `hold.capture.optional` | Native C engine | 1.2044× | 1.0844–1.3559× | 0.18× | FASTER |
| Holdout | `hold.capture.optional` | Rust engine | 0.0093× | 0.0087–0.0103× | 2.79× | SLOWER |
| Holdout | `hold.split.limited` | Python engine | 0.0062× | 0.0061–0.0063× | 7.46× | SLOWER |
| Holdout | `hold.split.limited` | Native C engine | 1.1249× | 1.1089–1.1420× | 0.19× | FASTER |
| Holdout | `hold.split.limited` | Rust engine | 0.0071× | 0.0070–0.0071× | 2.83× | SLOWER |
| Holdout | `hold.replace.limited` | Python engine | 0.0130× | 0.0129–0.0132× | 6.04× | SLOWER |
| Holdout | `hold.replace.limited` | Native C engine | 1.2356× | 1.2210–1.2519× | 0.15× | FASTER |
| Holdout | `hold.replace.limited` | Rust engine | 0.0085× | 0.0082–0.0087× | 2.90× | SLOWER |
| Holdout | `hold.bytes.view-long` | Python engine | 0.0066× | 0.0064–0.0069× | 48.64× | SLOWER |
| Holdout | `hold.bytes.view-long` | Native C engine | 1.2791× | 1.2115–1.3427× | 0.60× | FASTER |
| Holdout | `hold.bytes.view-long` | Rust engine | 0.0009× | 0.0009–0.0010× | 5.61× | SLOWER |
| Holdout | `hold.window.search` | Python engine | 0.0187× | 0.0184–0.0189× | 4.40× | SLOWER |
| Holdout | `hold.window.search` | Native C engine | 0.9426× | 0.8704–0.9833× | 0.18× | — |
| Holdout | `hold.window.search` | Rust engine | 0.0147× | 0.0146–0.0148× | 3.32× | SLOWER |
| Holdout | `hold.window.findall` | Python engine | 0.0178× | 0.0168–0.0193× | 4.03× | SLOWER |
| Holdout | `hold.window.findall` | Native C engine | 0.9594× | 0.9495–0.9700× | 0.22× | — |
| Holdout | `hold.window.findall` | Rust engine | 0.0074× | 0.0072–0.0076× | 2.86× | SLOWER |
| Holdout | `hold.window.scanner` | Python engine | 0.0173× | 0.0168–0.0177× | 4.46× | SLOWER |
| Holdout | `hold.window.scanner` | Native C engine | 1.0400× | 0.9512–1.0927× | 0.30× | — |
| Holdout | `hold.window.scanner` | Rust engine | 0.0094× | 0.0093–0.0095× | 2.20× | SLOWER |
| Holdout | `hold.window.match` | Python engine | 0.0331× | 0.0325–0.0338× | 3.55× | SLOWER |
| Holdout | `hold.window.match` | Native C engine | 0.9647× | 0.9424–0.9924× | 0.18× | — |
| Holdout | `hold.window.match` | Rust engine | 0.0175× | 0.0171–0.0180× | 2.46× | SLOWER |
| Holdout | `hold.literal.replace` | Python engine | 0.0064× | 0.0063–0.0066× | 38.88× | SLOWER |
| Holdout | `hold.literal.replace` | Native C engine | 1.1427× | 1.1254–1.1636× | 0.52× | FASTER |
| Holdout | `hold.literal.replace` | Rust engine | 0.0056× | 0.0055–0.0057× | 10.36× | SLOWER |
| Holdout | `hold.template.repeat` | Python engine | 0.0193× | 0.0189–0.0198× | 6.32× | SLOWER |
| Holdout | `hold.template.repeat` | Native C engine | 1.5604× | 1.5000–1.6139× | 0.14× | FASTER |
| Holdout | `hold.template.repeat` | Rust engine | 0.0144× | 0.0141–0.0147× | 2.28× | SLOWER |
| Holdout | `hold.match.miss` | Python engine | 0.0256× | 0.0234–0.0276× | 5.02× | SLOWER |
| Holdout | `hold.match.miss` | Native C engine | 1.0198× | 0.8902–1.1558× | 0.00× | — |
| Holdout | `hold.match.miss` | Rust engine | 0.0072× | 0.0071–0.0074× | 4.20× | SLOWER |
| Holdout | `hold.fullmatch.miss` | Python engine | 0.0180× | 0.0171–0.0199× | 11.09× | SLOWER |
| Holdout | `hold.fullmatch.miss` | Native C engine | 1.4678× | 1.3911–1.6201× | 0.00× | FASTER |
| Holdout | `hold.fullmatch.miss` | Rust engine | 0.0235× | 0.0222–0.0259× | 3.31× | SLOWER |

## Large slowdowns

- Python engine: `cal.search.literal.hit` (0.008×), `cal.search.literal.miss` (0.002×), `cal.search.long-boundary` (0.000×), `cal.search.class-anchor` (0.011×), `cal.match.prefix` (0.024×), `cal.fullmatch.structured` (0.013×), `cal.search.look-capture` (0.008×), `cal.findall.tokens` (0.011×), `cal.finditer.groups` (0.013×), `cal.split.capture` (0.010×), `cal.sub.template` (0.016×), `cal.subn.callable` (0.023×), `cal.bytes.tokens` (0.007×), `cal.unicode.words` (0.006×), `cal.cold.compile-search` (0.293×), `cal.module.warm` (0.010×), `cal.empty.finditer` (0.010×), `cal.backref.fullmatch` (0.019×), `cal.conditional.match` (0.018×), `cal.atomic.search` (0.010×), `cal.byteslike.findall` (0.011×), `cal.unicode-name.search` (0.014×), `cal.ignorecase.findall` (0.007×), `cal.many.split` (0.013×), `cal.scanner.search` (0.013×), `cal.match.surface` (0.014×), `hold.search.literal.hit` (0.008×), `hold.search.literal.miss` (0.002×), `hold.search.long-boundary` (0.000×), `hold.search.class-anchor` (0.010×), `hold.match.prefix` (0.025×), `hold.fullmatch.structured` (0.011×), `hold.search.look-capture` (0.010×), `hold.findall.tokens` (0.011×), `hold.finditer.groups` (0.013×), `hold.split.capture` (0.010×), `hold.sub.template` (0.016×), `hold.subn.callable` (0.027×), `hold.bytes.tokens` (0.010×), `hold.unicode.words` (0.009×), `hold.cold.compile-search` (0.472×), `hold.module.warm` (0.019×), `hold.empty.finditer` (0.009×), `hold.backref.fullmatch` (0.018×), `hold.conditional.match` (0.019×), `hold.atomic.search` (0.010×), `hold.byteslike.findall` (0.011×), `hold.unicode-name.search` (0.013×), `hold.ignorecase.findall` (0.008×), `hold.many.split` (0.013×), `hold.scanner.search` (0.013×), `hold.match.surface` (0.023×), `cal.real.log` (0.003×), `cal.real.url` (0.006×), `cal.real.email` (0.005×), `cal.real.datetime` (0.008×), `cal.real.version` (0.011×), `cal.real.uuid` (0.007×), `cal.real.ip` (0.008×), `cal.real.path` (0.006×), `cal.real.config` (0.009×), `cal.real.comments` (0.006×), `cal.real.whitespace` (0.007×), `cal.real.lines` (0.009×), `cal.real.markup` (0.005×), `cal.real.quotes` (0.004×), `cal.real.csv` (0.005×), `cal.branch.prefix` (0.009×), `cal.branch.miss` (0.001×), `cal.repeat.nested` (0.010×), `cal.lines.records` (0.009×), `cal.block.dotall` (0.006×), `cal.pattern.verbose` (0.004×), `cal.mode.ascii` (0.005×), `cal.mode.casefold` (0.008×), `cal.mode.astral` (0.010×), `cal.look.negative-ahead` (0.004×), `cal.look.negative-behind` (0.006×), `cal.bytes.replace` (0.017×), `cal.bytes.scan` (0.012×), `cal.module.replace` (0.023×), `cal.zero.boundary` (0.007×), `cal.dense.iter` (0.016×), `cal.capture.optional` (0.011×), `cal.split.limited` (0.006×), `cal.replace.limited` (0.013×), `cal.bytes.view-long` (0.007×), `cal.window.search` (0.019×), `cal.window.findall` (0.017×), `cal.window.scanner` (0.017×), `cal.window.match` (0.035×), `cal.literal.replace` (0.006×), `cal.template.repeat` (0.019×), `cal.match.miss` (0.029×), `cal.fullmatch.miss` (0.015×), `hold.real.log` (0.003×), `hold.real.url` (0.005×), `hold.real.email` (0.004×), `hold.real.datetime` (0.007×), `hold.real.version` (0.009×), `hold.real.uuid` (0.006×), `hold.real.ip` (0.009×), `hold.real.path` (0.006×), `hold.real.config` (0.008×), `hold.real.comments` (0.005×), `hold.real.whitespace` (0.007×), `hold.real.lines` (0.010×), `hold.real.markup` (0.005×), `hold.real.quotes` (0.004×), `hold.real.csv` (0.004×), `hold.branch.prefix` (0.010×), `hold.branch.miss` (0.001×), `hold.repeat.nested` (0.010×), `hold.lines.records` (0.008×), `hold.block.dotall` (0.006×), `hold.pattern.verbose` (0.004×), `hold.mode.ascii` (0.005×), `hold.mode.casefold` (0.008×), `hold.mode.astral` (0.009×), `hold.look.negative-ahead` (0.004×), `hold.look.negative-behind` (0.007×), `hold.bytes.replace` (0.017×), `hold.bytes.scan` (0.011×), `hold.module.replace` (0.021×), `hold.zero.boundary` (0.008×), `hold.dense.iter` (0.016×), `hold.capture.optional` (0.011×), `hold.split.limited` (0.006×), `hold.replace.limited` (0.013×), `hold.bytes.view-long` (0.007×), `hold.window.search` (0.019×), `hold.window.findall` (0.018×), `hold.window.scanner` (0.017×), `hold.window.match` (0.033×), `hold.literal.replace` (0.006×), `hold.template.repeat` (0.019×), `hold.match.miss` (0.026×), `hold.fullmatch.miss` (0.018×).
- Rust engine: `cal.search.literal.hit` (0.009×), `cal.search.literal.miss` (0.006×), `cal.search.long-boundary` (0.001×), `cal.search.class-anchor` (0.014×), `cal.match.prefix` (0.015×), `cal.fullmatch.structured` (0.019×), `cal.search.look-capture` (0.016×), `cal.findall.tokens` (0.004×), `cal.finditer.groups` (0.010×), `cal.split.capture` (0.007×), `cal.sub.template` (0.015×), `cal.subn.callable` (0.019×), `cal.bytes.tokens` (0.005×), `cal.unicode.words` (0.010×), `cal.cold.compile-search` (0.699×), `cal.module.warm` (0.031×), `cal.empty.finditer` (0.021×), `cal.backref.fullmatch` (0.018×), `cal.conditional.match` (0.016×), `cal.atomic.search` (0.019×), `cal.byteslike.findall` (0.008×), `cal.unicode-name.search` (0.019×), `cal.ignorecase.findall` (0.008×), `cal.many.split` (0.005×), `cal.scanner.search` (0.009×), `cal.match.surface` (0.048×), `hold.search.literal.hit` (0.009×), `hold.search.literal.miss` (0.006×), `hold.search.long-boundary` (0.001×), `hold.search.class-anchor` (0.014×), `hold.match.prefix` (0.017×), `hold.fullmatch.structured` (0.019×), `hold.search.look-capture` (0.017×), `hold.findall.tokens` (0.006×), `hold.finditer.groups` (0.009×), `hold.split.capture` (0.007×), `hold.sub.template` (0.015×), `hold.subn.callable` (0.023×), `hold.bytes.tokens` (0.008×), `hold.unicode.words` (0.012×), `hold.cold.compile-search` (0.733×), `hold.module.warm` (0.031×), `hold.empty.finditer` (0.021×), `hold.backref.fullmatch` (0.019×), `hold.conditional.match` (0.018×), `hold.atomic.search` (0.021×), `hold.byteslike.findall` (0.008×), `hold.unicode-name.search` (0.019×), `hold.ignorecase.findall` (0.009×), `hold.many.split` (0.005×), `hold.scanner.search` (0.009×), `hold.match.surface` (0.044×), `cal.real.log` (0.006×), `cal.real.url` (0.012×), `cal.real.email` (0.006×), `cal.real.datetime` (0.015×), `cal.real.version` (0.030×), `cal.real.uuid` (0.014×), `cal.real.ip` (0.026×), `cal.real.path` (0.010×), `cal.real.config` (0.017×), `cal.real.comments` (0.004×), `cal.real.whitespace` (0.008×), `cal.real.lines` (0.009×), `cal.real.markup` (0.004×), `cal.real.quotes` (0.007×), `cal.real.csv` (0.011×), `cal.branch.prefix` (0.013×), `cal.branch.miss` (0.013×), `cal.repeat.nested` (0.023×), `cal.lines.records` (0.007×), `cal.block.dotall` (0.013×), `cal.pattern.verbose` (0.019×), `cal.mode.ascii` (0.009×), `cal.mode.casefold` (0.009×), `cal.mode.astral` (0.009×), `cal.look.negative-ahead` (0.007×), `cal.look.negative-behind` (0.010×), `cal.bytes.replace` (0.016×), `cal.bytes.scan` (0.009×), `cal.module.replace` (0.022×), `cal.zero.boundary` (0.013×), `cal.dense.iter` (0.008×), `cal.capture.optional` (0.009×), `cal.split.limited` (0.008×), `cal.replace.limited` (0.009×), `cal.bytes.view-long` (0.001×), `cal.window.search` (0.016×), `cal.window.findall` (0.007×), `cal.window.scanner` (0.009×), `cal.window.match` (0.018×), `cal.literal.replace` (0.005×), `cal.template.repeat` (0.013×), `cal.match.miss` (0.008×), `cal.fullmatch.miss` (0.020×), `hold.real.log` (0.006×), `hold.real.url` (0.010×), `hold.real.email` (0.007×), `hold.real.datetime` (0.017×), `hold.real.version` (0.021×), `hold.real.uuid` (0.014×), `hold.real.ip` (0.021×), `hold.real.path` (0.009×), `hold.real.config` (0.015×), `hold.real.comments` (0.003×), `hold.real.whitespace` (0.007×), `hold.real.lines` (0.009×), `hold.real.markup` (0.003×), `hold.real.quotes` (0.007×), `hold.real.csv` (0.010×), `hold.branch.prefix` (0.013×), `hold.branch.miss` (0.011×), `hold.repeat.nested` (0.022×), `hold.lines.records` (0.008×), `hold.block.dotall` (0.013×), `hold.pattern.verbose` (0.026×), `hold.mode.ascii` (0.008×), `hold.mode.casefold` (0.010×), `hold.mode.astral` (0.009×), `hold.look.negative-ahead` (0.007×), `hold.look.negative-behind` (0.010×), `hold.bytes.replace` (0.016×), `hold.bytes.scan` (0.009×), `hold.module.replace` (0.020×), `hold.zero.boundary` (0.015×), `hold.dense.iter` (0.008×), `hold.capture.optional` (0.009×), `hold.split.limited` (0.007×), `hold.replace.limited` (0.008×), `hold.bytes.view-long` (0.001×), `hold.window.search` (0.015×), `hold.window.findall` (0.007×), `hold.window.scanner` (0.009×), `hold.window.match` (0.017×), `hold.literal.replace` (0.006×), `hold.template.repeat` (0.014×), `hold.match.miss` (0.007×), `hold.fullmatch.miss` (0.024×).
- Native C engine: `cal.cold.compile-search` (0.769×), `cal.real.email` (0.662×), `cal.branch.miss` (0.514×).

The Python engine performs matching work in Python, and the Rust engine repeatedly prepares data and crosses the Python/Rust boundary; both costs dominate short tasks. Native-C losses expose specific boundary and general-path costs:
- Everyday log, address, path, comment, markup, quote, and comma-separated-field tasks combine repeated classes, captures, or lookarounds; they take the general native backtracking path instead of its compact single-pass path.
- Searches across many alternative words still test the remaining branches when a possible prefix survives; the native one/two-character start filter removes impossible positions but does not build a full shared-prefix trie.

No loss is removed from the denominator or hidden from the charts.
