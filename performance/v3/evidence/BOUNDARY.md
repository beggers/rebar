# Broader performance: API-boundary paths

All 7488 raw timing rows, 432 engine/task results, and 315 large slowdowns are retained. Raw SHA-256: `5754989a48db93cc5e31688595352bfb1457b466baac78ca2c92db4bdb8d1c14`.

## At a glance

The holdout tasks were kept separate from tuning. **1× means the same speed as Python `re`; higher is faster.** A result is clearly faster only when its measured range stays above 1×. A large slowdown means more than 20% slower.

| Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: | ---: |
| Native C engine | **0.9735×** | 0.9676–0.9795× | 37/72 | 19/72 |
| Rust engine | **0.0135×** | 0.0135–0.0136× | 2/72 | 69/72 |
| Python engine | **0.0116×** | 0.0115–0.0116× | 2/72 | 69/72 |

## Overall results

| Task set | Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |
| --- | --- | ---: | ---: | ---: | ---: |
| Practice | Python engine | 0.0113× | 0.0112–0.0113× | 2/72 | 69 |
| Practice | Native C engine | 0.9563× | 0.9512–0.9613× | 35/72 | 20 |
| Practice | Rust engine | 0.0134× | 0.0134–0.0135× | 2/72 | 69 |
| Holdout | Python engine | 0.0116× | 0.0115–0.0116× | 2/72 | 69 |
| Holdout | Native C engine | 0.9735× | 0.9676–0.9795× | 37/72 | 19 |
| Holdout | Rust engine | 0.0135× | 0.0135–0.0136× | 2/72 | 69 |
| All | Python engine | 0.0114× | 0.0114–0.0114× | 4/144 | 138 |
| All | Native C engine | 0.9649× | 0.9610–0.9686× | 72/144 | 39 |
| All | Rust engine | 0.0135× | 0.0134–0.0135× | 4/144 | 138 |

## Every task

`FASTER` means the measured range stays above 1×. `SLOWER` means more than 20% slower. Memory compares median traced Python memory with Python `re`.

| Task set | Task | Engine | Speed | Measured range | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Practice | `cal.search.literal.hit` | Python engine | 0.0072× | 0.0070–0.0073× | 102.00× | SLOWER |
| Practice | `cal.search.literal.hit` | Native C engine | 1.1067× | 1.0971–1.1150× | 0.73× | FASTER |
| Practice | `cal.search.literal.hit` | Rust engine | 0.0085× | 0.0085–0.0086× | 34.03× | SLOWER |
| Practice | `cal.search.literal.miss` | Python engine | 0.0021× | 0.0020–0.0021× | 14408.00× | SLOWER |
| Practice | `cal.search.literal.miss` | Native C engine | 1.1447× | 1.1373–1.1528× | 0.00× | FASTER |
| Practice | `cal.search.literal.miss` | Rust engine | 0.0056× | 0.0055–0.0057× | 4375.00× | SLOWER |
| Practice | `cal.search.long-boundary` | Python engine | 0.0003× | 0.0003–0.0003× | 129.57× | SLOWER |
| Practice | `cal.search.long-boundary` | Native C engine | 12.1715× | 11.2448–13.4085× | 0.07× | FASTER |
| Practice | `cal.search.long-boundary` | Rust engine | 0.0010× | 0.0009–0.0010× | 140.03× | SLOWER |
| Practice | `cal.search.class-anchor` | Python engine | 0.0113× | 0.0109–0.0118× | 11.57× | SLOWER |
| Practice | `cal.search.class-anchor` | Native C engine | 1.0753× | 1.0420–1.1214× | 0.07× | FASTER |
| Practice | `cal.search.class-anchor` | Rust engine | 0.0144× | 0.0137–0.0151× | 3.36× | SLOWER |
| Practice | `cal.match.prefix` | Python engine | 0.0234× | 0.0229–0.0239× | 3.87× | SLOWER |
| Practice | `cal.match.prefix` | Native C engine | 1.0811× | 1.0662–1.1010× | 0.07× | FASTER |
| Practice | `cal.match.prefix` | Rust engine | 0.0152× | 0.0150–0.0154× | 2.89× | SLOWER |
| Practice | `cal.fullmatch.structured` | Python engine | 0.0127× | 0.0125–0.0128× | 12.07× | SLOWER |
| Practice | `cal.fullmatch.structured` | Native C engine | 0.9534× | 0.9364–0.9674× | 0.07× | — |
| Practice | `cal.fullmatch.structured` | Rust engine | 0.0183× | 0.0182–0.0185× | 3.04× | SLOWER |
| Practice | `cal.search.look-capture` | Python engine | 0.0073× | 0.0072–0.0073× | 17.28× | SLOWER |
| Practice | `cal.search.look-capture` | Native C engine | 1.2170× | 1.1968–1.2332× | 0.08× | FASTER |
| Practice | `cal.search.look-capture` | Rust engine | 0.0155× | 0.0154–0.0157× | 3.29× | SLOWER |
| Practice | `cal.findall.tokens` | Python engine | 0.0102× | 0.0099–0.0104× | 7.14× | SLOWER |
| Practice | `cal.findall.tokens` | Native C engine | 0.8960× | 0.8696–0.9215× | 0.28× | — |
| Practice | `cal.findall.tokens` | Rust engine | 0.0037× | 0.0036–0.0038× | 3.26× | SLOWER |
| Practice | `cal.finditer.groups` | Python engine | 0.0126× | 0.0122–0.0130× | 7.75× | SLOWER |
| Practice | `cal.finditer.groups` | Native C engine | 1.4199× | 1.3638–1.4708× | 0.39× | FASTER |
| Practice | `cal.finditer.groups` | Rust engine | 0.0096× | 0.0093–0.0099× | 1.91× | SLOWER |
| Practice | `cal.split.capture` | Python engine | 0.0100× | 0.0099–0.0101× | 11.37× | SLOWER |
| Practice | `cal.split.capture` | Native C engine | 1.7695× | 1.7512–1.7851× | 0.20× | FASTER |
| Practice | `cal.split.capture` | Rust engine | 0.0067× | 0.0067–0.0068× | 2.62× | SLOWER |
| Practice | `cal.sub.template` | Python engine | 0.0168× | 0.0158–0.0185× | 9.30× | SLOWER |
| Practice | `cal.sub.template` | Native C engine | 1.9247× | 1.7895–2.1478× | 0.12× | FASTER |
| Practice | `cal.sub.template` | Rust engine | 0.0152× | 0.0145–0.0167× | 2.39× | SLOWER |
| Practice | `cal.subn.callable` | Python engine | 0.0235× | 0.0228–0.0243× | 5.05× | SLOWER |
| Practice | `cal.subn.callable` | Native C engine | 1.0649× | 1.0327–1.1004× | 0.25× | FASTER |
| Practice | `cal.subn.callable` | Rust engine | 0.0190× | 0.0186–0.0196× | 2.56× | SLOWER |
| Practice | `cal.bytes.tokens` | Python engine | 0.0074× | 0.0073–0.0075× | 8.29× | SLOWER |
| Practice | `cal.bytes.tokens` | Native C engine | 0.8494× | 0.8175–0.8703× | 0.12× | — |
| Practice | `cal.bytes.tokens` | Rust engine | 0.0055× | 0.0055–0.0056× | 3.43× | SLOWER |
| Practice | `cal.unicode.words` | Python engine | 0.0063× | 0.0060–0.0069× | 6.52× | SLOWER |
| Practice | `cal.unicode.words` | Native C engine | 0.7808× | 0.7460–0.8490× | 0.20× | SLOWER |
| Practice | `cal.unicode.words` | Rust engine | 0.0101× | 0.0096–0.0109× | 2.69× | SLOWER |
| Practice | `cal.cold.compile-search` | Python engine | 0.2905× | 0.2865–0.2946× | 5.84× | SLOWER |
| Practice | `cal.cold.compile-search` | Native C engine | 1.5308× | 1.5028–1.5580× | 0.76× | FASTER |
| Practice | `cal.cold.compile-search` | Rust engine | 0.6858× | 0.6630–0.7032× | 1.95× | SLOWER |
| Practice | `cal.module.warm` | Python engine | 0.0105× | 0.0104–0.0108× | 7.21× | SLOWER |
| Practice | `cal.module.warm` | Native C engine | 1.1610× | 1.1422–1.1835× | 0.07× | FASTER |
| Practice | `cal.module.warm` | Rust engine | 0.0313× | 0.0308–0.0319× | 3.39× | SLOWER |
| Practice | `cal.empty.finditer` | Python engine | 0.0098× | 0.0095–0.0100× | 8.09× | SLOWER |
| Practice | `cal.empty.finditer` | Native C engine | 0.7016× | 0.6755–0.7287× | 0.59× | SLOWER |
| Practice | `cal.empty.finditer` | Rust engine | 0.0211× | 0.0207–0.0216× | 1.67× | SLOWER |
| Practice | `cal.backref.fullmatch` | Python engine | 0.0187× | 0.0171–0.0207× | 6.99× | SLOWER |
| Practice | `cal.backref.fullmatch` | Native C engine | 1.1411× | 1.0466–1.2830× | 0.08× | FASTER |
| Practice | `cal.backref.fullmatch` | Rust engine | 0.0191× | 0.0175–0.0215× | 3.04× | SLOWER |
| Practice | `cal.conditional.match` | Python engine | 0.0177× | 0.0173–0.0180× | 6.78× | SLOWER |
| Practice | `cal.conditional.match` | Native C engine | 1.0673× | 1.0509–1.0843× | 0.08× | FASTER |
| Practice | `cal.conditional.match` | Rust engine | 0.0159× | 0.0156–0.0162× | 2.97× | SLOWER |
| Practice | `cal.atomic.search` | Python engine | 0.0096× | 0.0095–0.0096× | 8.80× | SLOWER |
| Practice | `cal.atomic.search` | Native C engine | 0.5488× | 0.5384–0.5583× | 0.50× | SLOWER |
| Practice | `cal.atomic.search` | Rust engine | 0.0186× | 0.0185–0.0188× | 3.14× | SLOWER |
| Practice | `cal.byteslike.findall` | Python engine | 0.0107× | 0.0106–0.0108× | 7.48× | SLOWER |
| Practice | `cal.byteslike.findall` | Native C engine | 1.8822× | 1.8613–1.9072× | 0.18× | FASTER |
| Practice | `cal.byteslike.findall` | Rust engine | 0.0079× | 0.0078–0.0080× | 2.93× | SLOWER |
| Practice | `cal.unicode-name.search` | Python engine | 0.0136× | 0.0135–0.0138× | 4.37× | SLOWER |
| Practice | `cal.unicode-name.search` | Native C engine | 1.3209× | 1.3020–1.3402× | 0.07× | FASTER |
| Practice | `cal.unicode-name.search` | Rust engine | 0.0186× | 0.0183–0.0189× | 3.14× | SLOWER |
| Practice | `cal.ignorecase.findall` | Python engine | 0.0071× | 0.0071–0.0072× | 5.14× | SLOWER |
| Practice | `cal.ignorecase.findall` | Native C engine | 1.0988× | 1.0901–1.1093× | 0.16× | FASTER |
| Practice | `cal.ignorecase.findall` | Rust engine | 0.0080× | 0.0078–0.0081× | 2.96× | SLOWER |
| Practice | `cal.many.split` | Python engine | 0.0123× | 0.0121–0.0126× | 8.86× | SLOWER |
| Practice | `cal.many.split` | Native C engine | 1.1803× | 1.1420–1.2186× | 0.20× | FASTER |
| Practice | `cal.many.split` | Rust engine | 0.0045× | 0.0044–0.0046× | 2.86× | SLOWER |
| Practice | `cal.escape.text` | Python engine | 0.9734× | 0.9334–1.0033× | 1.00× | — |
| Practice | `cal.escape.text` | Native C engine | 0.9838× | 0.9783–0.9886× | 1.00× | — |
| Practice | `cal.escape.text` | Rust engine | 0.9981× | 0.9893–1.0075× | 1.00× | — |
| Practice | `cal.compile.only` | Python engine | 2.1553× | 2.0926–2.2115× | 0.50× | FASTER |
| Practice | `cal.compile.only` | Native C engine | 1.6684× | 1.6479–1.6888× | 0.76× | FASTER |
| Practice | `cal.compile.only` | Rust engine | 1.7195× | 1.6815–1.7476× | 0.56× | FASTER |
| Practice | `cal.scanner.search` | Python engine | 0.0132× | 0.0127–0.0139× | 6.71× | SLOWER |
| Practice | `cal.scanner.search` | Native C engine | 1.0324× | 0.9898–1.0913× | 0.36× | — |
| Practice | `cal.scanner.search` | Rust engine | 0.0089× | 0.0086–0.0093× | 1.98× | SLOWER |
| Practice | `cal.match.surface` | Python engine | 0.0141× | 0.0139–0.0142× | 12.88× | SLOWER |
| Practice | `cal.match.surface` | Native C engine | 1.2708× | 1.2561–1.2866× | 0.32× | FASTER |
| Practice | `cal.match.surface` | Rust engine | 0.0473× | 0.0468–0.0478× | 3.26× | SLOWER |
| Holdout | `hold.search.literal.hit` | Python engine | 0.0073× | 0.0072–0.0073× | 102.00× | SLOWER |
| Holdout | `hold.search.literal.hit` | Native C engine | 1.0877× | 1.0589–1.1087× | 0.73× | FASTER |
| Holdout | `hold.search.literal.hit` | Rust engine | 0.0088× | 0.0087–0.0088× | 33.96× | SLOWER |
| Holdout | `hold.search.literal.miss` | Python engine | 0.0023× | 0.0023–0.0023× | 14408.00× | SLOWER |
| Holdout | `hold.search.literal.miss` | Native C engine | 1.1390× | 1.0718–1.1787× | 0.00× | FASTER |
| Holdout | `hold.search.literal.miss` | Rust engine | 0.0056× | 0.0055–0.0057× | 4375.00× | SLOWER |
| Holdout | `hold.search.long-boundary` | Python engine | 0.0003× | 0.0003–0.0003× | 130.58× | SLOWER |
| Holdout | `hold.search.long-boundary` | Native C engine | 16.7742× | 15.2636–18.3895× | 0.07× | FASTER |
| Holdout | `hold.search.long-boundary` | Rust engine | 0.0010× | 0.0009–0.0010× | 218.22× | SLOWER |
| Holdout | `hold.search.class-anchor` | Python engine | 0.0097× | 0.0095–0.0101× | 11.17× | SLOWER |
| Holdout | `hold.search.class-anchor` | Native C engine | 1.0115× | 0.9873–1.0558× | 0.07× | — |
| Holdout | `hold.search.class-anchor` | Rust engine | 0.0127× | 0.0124–0.0133× | 3.39× | SLOWER |
| Holdout | `hold.match.prefix` | Python engine | 0.0236× | 0.0232–0.0239× | 3.87× | SLOWER |
| Holdout | `hold.match.prefix` | Native C engine | 1.0535× | 1.0486–1.0586× | 0.07× | FASTER |
| Holdout | `hold.match.prefix` | Rust engine | 0.0152× | 0.0150–0.0153× | 2.87× | SLOWER |
| Holdout | `hold.fullmatch.structured` | Python engine | 0.0112× | 0.0111–0.0114× | 16.36× | SLOWER |
| Holdout | `hold.fullmatch.structured` | Native C engine | 0.8917× | 0.8514–0.9248× | 0.07× | — |
| Holdout | `hold.fullmatch.structured` | Rust engine | 0.0188× | 0.0183–0.0191× | 3.04× | SLOWER |
| Holdout | `hold.search.look-capture` | Python engine | 0.0100× | 0.0098–0.0102× | 17.64× | SLOWER |
| Holdout | `hold.search.look-capture` | Native C engine | 0.9110× | 0.8813–0.9353× | 0.17× | — |
| Holdout | `hold.search.look-capture` | Rust engine | 0.0173× | 0.0170–0.0176× | 3.26× | SLOWER |
| Holdout | `hold.findall.tokens` | Python engine | 0.0109× | 0.0105–0.0117× | 11.27× | SLOWER |
| Holdout | `hold.findall.tokens` | Native C engine | 1.3831× | 1.2271–1.5339× | 0.21× | FASTER |
| Holdout | `hold.findall.tokens` | Rust engine | 0.0059× | 0.0057–0.0063× | 3.10× | SLOWER |
| Holdout | `hold.finditer.groups` | Python engine | 0.0126× | 0.0123–0.0131× | 7.75× | SLOWER |
| Holdout | `hold.finditer.groups` | Native C engine | 1.3751× | 1.3313–1.4234× | 0.39× | FASTER |
| Holdout | `hold.finditer.groups` | Rust engine | 0.0090× | 0.0087–0.0093× | 1.93× | SLOWER |
| Holdout | `hold.split.capture` | Python engine | 0.0099× | 0.0098–0.0102× | 11.37× | SLOWER |
| Holdout | `hold.split.capture` | Native C engine | 1.7617× | 1.7155–1.8096× | 0.20× | FASTER |
| Holdout | `hold.split.capture` | Rust engine | 0.0067× | 0.0066–0.0069× | 2.62× | SLOWER |
| Holdout | `hold.sub.template` | Python engine | 0.0156× | 0.0155–0.0158× | 9.29× | SLOWER |
| Holdout | `hold.sub.template` | Native C engine | 1.8102× | 1.7944–1.8284× | 0.12× | FASTER |
| Holdout | `hold.sub.template` | Rust engine | 0.0142× | 0.0141–0.0143× | 2.39× | SLOWER |
| Holdout | `hold.subn.callable` | Python engine | 0.0270× | 0.0263–0.0278× | 4.58× | SLOWER |
| Holdout | `hold.subn.callable` | Native C engine | 1.0945× | 1.0396–1.1526× | 0.25× | FASTER |
| Holdout | `hold.subn.callable` | Rust engine | 0.0220× | 0.0214–0.0227× | 2.53× | SLOWER |
| Holdout | `hold.bytes.tokens` | Python engine | 0.0101× | 0.0098–0.0104× | 8.71× | SLOWER |
| Holdout | `hold.bytes.tokens` | Native C engine | 1.8908× | 1.7964–1.9806× | 0.18× | FASTER |
| Holdout | `hold.bytes.tokens` | Rust engine | 0.0083× | 0.0081–0.0086× | 2.92× | SLOWER |
| Holdout | `hold.unicode.words` | Python engine | 0.0087× | 0.0085–0.0089× | 6.63× | SLOWER |
| Holdout | `hold.unicode.words` | Native C engine | 1.5964× | 1.5223–1.6593× | 0.20× | FASTER |
| Holdout | `hold.unicode.words` | Rust engine | 0.0116× | 0.0114–0.0119× | 2.67× | SLOWER |
| Holdout | `hold.cold.compile-search` | Python engine | 0.4848× | 0.4779–0.4909× | 5.95× | SLOWER |
| Holdout | `hold.cold.compile-search` | Native C engine | 1.4910× | 1.4675–1.5129× | 0.79× | FASTER |
| Holdout | `hold.cold.compile-search` | Rust engine | 0.7381× | 0.7260–0.7495× | 1.93× | SLOWER |
| Holdout | `hold.module.warm` | Python engine | 0.0194× | 0.0189–0.0200× | 7.12× | SLOWER |
| Holdout | `hold.module.warm` | Native C engine | 1.1033× | 1.0773–1.1382× | 0.07× | FASTER |
| Holdout | `hold.module.warm` | Rust engine | 0.0316× | 0.0309–0.0327× | 3.38× | SLOWER |
| Holdout | `hold.empty.finditer` | Python engine | 0.0091× | 0.0088–0.0093× | 8.52× | SLOWER |
| Holdout | `hold.empty.finditer` | Native C engine | 0.6740× | 0.6479–0.6988× | 0.61× | SLOWER |
| Holdout | `hold.empty.finditer` | Rust engine | 0.0211× | 0.0206–0.0217× | 1.62× | SLOWER |
| Holdout | `hold.backref.fullmatch` | Python engine | 0.0191× | 0.0189–0.0194× | 6.99× | SLOWER |
| Holdout | `hold.backref.fullmatch` | Native C engine | 1.1278× | 1.1099–1.1434× | 0.08× | FASTER |
| Holdout | `hold.backref.fullmatch` | Rust engine | 0.0200× | 0.0198–0.0201× | 3.04× | SLOWER |
| Holdout | `hold.conditional.match` | Python engine | 0.0200× | 0.0198–0.0202× | 6.78× | SLOWER |
| Holdout | `hold.conditional.match` | Native C engine | 1.1708× | 1.1550–1.1877× | 0.08× | FASTER |
| Holdout | `hold.conditional.match` | Rust engine | 0.0195× | 0.0192–0.0198× | 2.94× | SLOWER |
| Holdout | `hold.atomic.search` | Python engine | 0.0110× | 0.0105–0.0117× | 6.53× | SLOWER |
| Holdout | `hold.atomic.search` | Native C engine | 0.9019× | 0.8861–0.9197× | 0.07× | — |
| Holdout | `hold.atomic.search` | Rust engine | 0.0230× | 0.0222–0.0245× | 3.13× | SLOWER |
| Holdout | `hold.byteslike.findall` | Python engine | 0.0114× | 0.0112–0.0115× | 7.39× | SLOWER |
| Holdout | `hold.byteslike.findall` | Native C engine | 1.9216× | 1.8976–1.9483× | 0.18× | FASTER |
| Holdout | `hold.byteslike.findall` | Rust engine | 0.0083× | 0.0082–0.0084× | 2.83× | SLOWER |
| Holdout | `hold.unicode-name.search` | Python engine | 0.0133× | 0.0132–0.0135× | 4.69× | SLOWER |
| Holdout | `hold.unicode-name.search` | Native C engine | 1.3490× | 1.2262–1.4228× | 0.07× | FASTER |
| Holdout | `hold.unicode-name.search` | Rust engine | 0.0197× | 0.0195–0.0200× | 3.14× | SLOWER |
| Holdout | `hold.ignorecase.findall` | Python engine | 0.0078× | 0.0076–0.0082× | 4.86× | SLOWER |
| Holdout | `hold.ignorecase.findall` | Native C engine | 1.1137× | 1.0882–1.1560× | 0.16× | FASTER |
| Holdout | `hold.ignorecase.findall` | Rust engine | 0.0094× | 0.0092–0.0098× | 2.94× | SLOWER |
| Holdout | `hold.many.split` | Python engine | 0.0126× | 0.0125–0.0128× | 8.86× | SLOWER |
| Holdout | `hold.many.split` | Native C engine | 1.2214× | 1.1904–1.2409× | 0.20× | FASTER |
| Holdout | `hold.many.split` | Rust engine | 0.0046× | 0.0046–0.0047× | 2.86× | SLOWER |
| Holdout | `hold.escape.bytes` | Python engine | 0.9884× | 0.9546–1.0137× | 0.68× | — |
| Holdout | `hold.escape.bytes` | Native C engine | 0.9657× | 0.9323–0.9939× | 0.68× | — |
| Holdout | `hold.escape.bytes` | Rust engine | 0.9964× | 0.9735–1.0151× | 0.68× | — |
| Holdout | `hold.compile.only` | Python engine | 1.9152× | 1.8498–1.9760× | 0.54× | FASTER |
| Holdout | `hold.compile.only` | Native C engine | 1.3911× | 1.3474–1.4302× | 0.92× | FASTER |
| Holdout | `hold.compile.only` | Rust engine | 1.6886× | 1.6493–1.7259× | 0.60× | FASTER |
| Holdout | `hold.scanner.search` | Python engine | 0.0131× | 0.0126–0.0134× | 6.71× | SLOWER |
| Holdout | `hold.scanner.search` | Native C engine | 1.0621× | 1.0463–1.0785× | 0.36× | FASTER |
| Holdout | `hold.scanner.search` | Rust engine | 0.0090× | 0.0089–0.0091× | 1.98× | SLOWER |
| Holdout | `hold.match.surface` | Python engine | 0.0209× | 0.0208–0.0211× | 12.79× | SLOWER |
| Holdout | `hold.match.surface` | Native C engine | 1.0901× | 1.0800–1.1009× | 0.32× | FASTER |
| Holdout | `hold.match.surface` | Rust engine | 0.0411× | 0.0408–0.0414× | 3.25× | SLOWER |
| Practice | `cal.real.log` | Python engine | 0.0031× | 0.0029–0.0034× | 27.33× | SLOWER |
| Practice | `cal.real.log` | Native C engine | 0.2994× | 0.2814–0.3258× | 0.33× | SLOWER |
| Practice | `cal.real.log` | Rust engine | 0.0063× | 0.0059–0.0068× | 3.19× | SLOWER |
| Practice | `cal.real.url` | Python engine | 0.0062× | 0.0061–0.0064× | 26.38× | SLOWER |
| Practice | `cal.real.url` | Native C engine | 0.7097× | 0.6952–0.7264× | 0.11× | SLOWER |
| Practice | `cal.real.url` | Rust engine | 0.0116× | 0.0112–0.0119× | 3.49× | SLOWER |
| Practice | `cal.real.email` | Python engine | 0.0052× | 0.0052–0.0052× | 9.90× | SLOWER |
| Practice | `cal.real.email` | Native C engine | 0.4759× | 0.4597–0.4879× | 0.12× | SLOWER |
| Practice | `cal.real.email` | Rust engine | 0.0057× | 0.0056–0.0057× | 3.85× | SLOWER |
| Practice | `cal.real.datetime` | Python engine | 0.0072× | 0.0070–0.0074× | 23.68× | SLOWER |
| Practice | `cal.real.datetime` | Native C engine | 0.7282× | 0.6166–0.8272× | 0.09× | SLOWER |
| Practice | `cal.real.datetime` | Rust engine | 0.0150× | 0.0147–0.0153× | 3.49× | SLOWER |
| Practice | `cal.real.version` | Python engine | 0.0110× | 0.0105–0.0118× | 22.95× | SLOWER |
| Practice | `cal.real.version` | Native C engine | 1.1500× | 1.0278–1.2678× | 0.00× | FASTER |
| Practice | `cal.real.version` | Rust engine | 0.0294× | 0.0283–0.0312× | 3.46× | SLOWER |
| Practice | `cal.real.uuid` | Python engine | 0.0062× | 0.0060–0.0064× | 18.66× | SLOWER |
| Practice | `cal.real.uuid` | Native C engine | 0.7919× | 0.7216–0.8364× | 0.07× | SLOWER |
| Practice | `cal.real.uuid` | Rust engine | 0.0131× | 0.0129–0.0134× | 3.96× | SLOWER |
| Practice | `cal.real.ip` | Python engine | 0.0077× | 0.0077–0.0078× | 29.12× | SLOWER |
| Practice | `cal.real.ip` | Native C engine | 0.8635× | 0.8532–0.8734× | 0.07× | — |
| Practice | `cal.real.ip` | Rust engine | 0.0253× | 0.0251–0.0255× | 3.02× | SLOWER |
| Practice | `cal.real.path` | Python engine | 0.0056× | 0.0055–0.0058× | 30.63× | SLOWER |
| Practice | `cal.real.path` | Native C engine | 0.7481× | 0.7213–0.7691× | 0.12× | SLOWER |
| Practice | `cal.real.path` | Rust engine | 0.0104× | 0.0101–0.0110× | 3.60× | SLOWER |
| Practice | `cal.real.config` | Python engine | 0.0085× | 0.0083–0.0089× | 16.04× | SLOWER |
| Practice | `cal.real.config` | Native C engine | 1.0089× | 0.9828–1.0501× | 0.35× | — |
| Practice | `cal.real.config` | Rust engine | 0.0171× | 0.0166–0.0178× | 2.32× | SLOWER |
| Practice | `cal.real.comments` | Python engine | 0.0062× | 0.0061–0.0063× | 11.73× | SLOWER |
| Practice | `cal.real.comments` | Native C engine | 0.7514× | 0.7381–0.7636× | 0.14× | SLOWER |
| Practice | `cal.real.comments` | Rust engine | 0.0038× | 0.0037–0.0038× | 3.74× | SLOWER |
| Practice | `cal.real.whitespace` | Python engine | 0.0066× | 0.0065–0.0066× | 8.36× | SLOWER |
| Practice | `cal.real.whitespace` | Native C engine | 1.3640× | 1.3516–1.3747× | 0.14× | FASTER |
| Practice | `cal.real.whitespace` | Rust engine | 0.0072× | 0.0071–0.0072× | 2.79× | SLOWER |
| Practice | `cal.real.lines` | Python engine | 0.0091× | 0.0091–0.0092× | 14.09× | SLOWER |
| Practice | `cal.real.lines` | Native C engine | 0.9167× | 0.8878–0.9367× | 0.15× | — |
| Practice | `cal.real.lines` | Rust engine | 0.0089× | 0.0088–0.0090× | 2.83× | SLOWER |
| Practice | `cal.real.markup` | Python engine | 0.0045× | 0.0044–0.0045× | 13.23× | SLOWER |
| Practice | `cal.real.markup` | Native C engine | 0.5678× | 0.5443–0.5839× | 0.10× | SLOWER |
| Practice | `cal.real.markup` | Rust engine | 0.0036× | 0.0036–0.0036× | 4.19× | SLOWER |
| Practice | `cal.real.quotes` | Python engine | 0.0041× | 0.0041–0.0042× | 18.83× | SLOWER |
| Practice | `cal.real.quotes` | Native C engine | 0.5989× | 0.5867–0.6090× | 0.10× | SLOWER |
| Practice | `cal.real.quotes` | Rust engine | 0.0070× | 0.0070–0.0071× | 3.83× | SLOWER |
| Practice | `cal.real.csv` | Python engine | 0.0048× | 0.0047–0.0048× | 19.83× | SLOWER |
| Practice | `cal.real.csv` | Native C engine | 0.3845× | 0.3750–0.3922× | 0.32× | SLOWER |
| Practice | `cal.real.csv` | Rust engine | 0.0105× | 0.0104–0.0106× | 2.97× | SLOWER |
| Practice | `cal.branch.prefix` | Python engine | 0.0089× | 0.0087–0.0091× | 12.65× | SLOWER |
| Practice | `cal.branch.prefix` | Native C engine | 0.7006× | 0.6792–0.7243× | 0.07× | SLOWER |
| Practice | `cal.branch.prefix` | Rust engine | 0.0125× | 0.0122–0.0129× | 3.37× | SLOWER |
| Practice | `cal.branch.miss` | Python engine | 0.0009× | 0.0009–0.0010× | 83.64× | SLOWER |
| Practice | `cal.branch.miss` | Native C engine | 0.0862× | 0.0849–0.0879× | 0.00× | SLOWER |
| Practice | `cal.branch.miss` | Rust engine | 0.0124× | 0.0121–0.0128× | 4.25× | SLOWER |
| Practice | `cal.repeat.nested` | Python engine | 0.0099× | 0.0098–0.0101× | 15.24× | SLOWER |
| Practice | `cal.repeat.nested` | Native C engine | 0.8257× | 0.8149–0.8374× | 0.64× | — |
| Practice | `cal.repeat.nested` | Rust engine | 0.0231× | 0.0228–0.0235× | 1.57× | SLOWER |
| Practice | `cal.lines.records` | Python engine | 0.0083× | 0.0080–0.0085× | 14.74× | SLOWER |
| Practice | `cal.lines.records` | Native C engine | 0.9689× | 0.9402–0.9986× | 0.36× | — |
| Practice | `cal.lines.records` | Rust engine | 0.0072× | 0.0070–0.0074× | 2.56× | SLOWER |
| Practice | `cal.block.dotall` | Python engine | 0.0065× | 0.0064–0.0066× | 17.13× | SLOWER |
| Practice | `cal.block.dotall` | Native C engine | 0.6629× | 0.6545–0.6717× | 0.08× | SLOWER |
| Practice | `cal.block.dotall` | Rust engine | 0.0130× | 0.0129–0.0132× | 3.97× | SLOWER |
| Practice | `cal.pattern.verbose` | Python engine | 0.0040× | 0.0040–0.0040× | 14.85× | SLOWER |
| Practice | `cal.pattern.verbose` | Native C engine | 0.5223× | 0.5143–0.5289× | 0.09× | SLOWER |
| Practice | `cal.pattern.verbose` | Rust engine | 0.0197× | 0.0196–0.0198× | 3.43× | SLOWER |
| Practice | `cal.mode.ascii` | Python engine | 0.0053× | 0.0052–0.0054× | 7.27× | SLOWER |
| Practice | `cal.mode.ascii` | Native C engine | 0.8633× | 0.8523–0.8753× | 0.13× | — |
| Practice | `cal.mode.ascii` | Rust engine | 0.0093× | 0.0092–0.0094× | 3.04× | SLOWER |
| Practice | `cal.mode.casefold` | Python engine | 0.0079× | 0.0078–0.0080× | 5.52× | SLOWER |
| Practice | `cal.mode.casefold` | Native C engine | 1.0967× | 1.0503–1.1264× | 0.20× | FASTER |
| Practice | `cal.mode.casefold` | Rust engine | 0.0086× | 0.0085–0.0086× | 2.90× | SLOWER |
| Practice | `cal.mode.astral` | Python engine | 0.0094× | 0.0093–0.0095× | 7.05× | SLOWER |
| Practice | `cal.mode.astral` | Native C engine | 1.6283× | 1.6094–1.6482× | 0.25× | FASTER |
| Practice | `cal.mode.astral` | Rust engine | 0.0092× | 0.0091–0.0093× | 2.76× | SLOWER |
| Practice | `cal.look.negative-ahead` | Python engine | 0.0037× | 0.0036–0.0040× | 15.69× | SLOWER |
| Practice | `cal.look.negative-ahead` | Native C engine | 0.3648× | 0.3415–0.3904× | 0.53× | SLOWER |
| Practice | `cal.look.negative-ahead` | Rust engine | 0.0073× | 0.0070–0.0078× | 3.46× | SLOWER |
| Practice | `cal.look.negative-behind` | Python engine | 0.0066× | 0.0065–0.0066× | 12.65× | SLOWER |
| Practice | `cal.look.negative-behind` | Native C engine | 0.6300× | 0.5958–0.6517× | 0.10× | SLOWER |
| Practice | `cal.look.negative-behind` | Rust engine | 0.0099× | 0.0098–0.0100× | 3.19× | SLOWER |
| Practice | `cal.bytes.replace` | Python engine | 0.0163× | 0.0158–0.0169× | 9.71× | SLOWER |
| Practice | `cal.bytes.replace` | Native C engine | 1.0520× | 0.9952–1.1137× | 0.95× | — |
| Practice | `cal.bytes.replace` | Rust engine | 0.0158× | 0.0155–0.0162× | 2.52× | SLOWER |
| Practice | `cal.bytes.scan` | Python engine | 0.0113× | 0.0112–0.0114× | 8.55× | SLOWER |
| Practice | `cal.bytes.scan` | Native C engine | 1.2106× | 1.1997–1.2215× | 0.38× | FASTER |
| Practice | `cal.bytes.scan` | Rust engine | 0.0092× | 0.0091–0.0092× | 1.87× | SLOWER |
| Practice | `cal.compile.complex` | Python engine | 1.7265× | 1.6826–1.7633× | 0.39× | FASTER |
| Practice | `cal.compile.complex` | Native C engine | 1.3974× | 1.3826–1.4118× | 0.98× | FASTER |
| Practice | `cal.compile.complex` | Rust engine | 1.7223× | 1.6986–1.7458× | 0.52× | FASTER |
| Practice | `cal.module.replace` | Python engine | 0.0216× | 0.0211–0.0222× | 10.12× | SLOWER |
| Practice | `cal.module.replace` | Native C engine | 1.2508× | 1.2316–1.2760× | 0.04× | FASTER |
| Practice | `cal.module.replace` | Rust engine | 0.0202× | 0.0198–0.0208× | 2.52× | SLOWER |
| Practice | `cal.zero.boundary` | Python engine | 0.0077× | 0.0075–0.0080× | 13.81× | SLOWER |
| Practice | `cal.zero.boundary` | Native C engine | 0.5591× | 0.5418–0.5812× | 0.62× | SLOWER |
| Practice | `cal.zero.boundary` | Rust engine | 0.0136× | 0.0132–0.0142× | 1.69× | SLOWER |
| Practice | `cal.dense.iter` | Python engine | 0.0158× | 0.0154–0.0163× | 4.92× | SLOWER |
| Practice | `cal.dense.iter` | Native C engine | 1.2419× | 1.1646–1.3058× | 0.51× | FASTER |
| Practice | `cal.dense.iter` | Rust engine | 0.0081× | 0.0079–0.0084× | 1.49× | SLOWER |
| Practice | `cal.capture.optional` | Python engine | 0.0099× | 0.0097–0.0100× | 14.26× | SLOWER |
| Practice | `cal.capture.optional` | Native C engine | 0.9402× | 0.9115–0.9577× | 0.18× | — |
| Practice | `cal.capture.optional` | Rust engine | 0.0085× | 0.0085–0.0086× | 2.79× | SLOWER |
| Practice | `cal.split.limited` | Python engine | 0.0064× | 0.0064–0.0065× | 7.47× | SLOWER |
| Practice | `cal.split.limited` | Native C engine | 0.8274× | 0.8035–0.8476× | 0.19× | — |
| Practice | `cal.split.limited` | Rust engine | 0.0075× | 0.0075–0.0076× | 2.82× | SLOWER |
| Practice | `cal.replace.limited` | Python engine | 0.0132× | 0.0130–0.0135× | 6.04× | SLOWER |
| Practice | `cal.replace.limited` | Native C engine | 1.2683× | 1.2456–1.2927× | 0.15× | FASTER |
| Practice | `cal.replace.limited` | Rust engine | 0.0094× | 0.0092–0.0097× | 2.90× | SLOWER |
| Practice | `cal.bytes.view-long` | Python engine | 0.0064× | 0.0062–0.0065× | 48.64× | SLOWER |
| Practice | `cal.bytes.view-long` | Native C engine | 1.0752× | 1.0495–1.0996× | 0.60× | FASTER |
| Practice | `cal.bytes.view-long` | Rust engine | 0.0009× | 0.0009–0.0009× | 5.61× | SLOWER |
| Practice | `cal.window.search` | Python engine | 0.0191× | 0.0187–0.0195× | 4.40× | SLOWER |
| Practice | `cal.window.search` | Native C engine | 0.8738× | 0.8298–0.9069× | 0.18× | — |
| Practice | `cal.window.search` | Rust engine | 0.0157× | 0.0154–0.0159× | 3.30× | SLOWER |
| Practice | `cal.window.findall` | Python engine | 0.0168× | 0.0166–0.0170× | 4.02× | SLOWER |
| Practice | `cal.window.findall` | Native C engine | 0.9427× | 0.8325–1.0266× | 0.23× | — |
| Practice | `cal.window.findall` | Rust engine | 0.0075× | 0.0074–0.0075× | 3.01× | SLOWER |
| Practice | `cal.window.scanner` | Python engine | 0.0176× | 0.0174–0.0178× | 4.46× | SLOWER |
| Practice | `cal.window.scanner` | Native C engine | 1.0356× | 1.0228–1.0479× | 0.30× | FASTER |
| Practice | `cal.window.scanner` | Rust engine | 0.0094× | 0.0093–0.0095× | 2.20× | SLOWER |
| Practice | `cal.window.match` | Python engine | 0.0362× | 0.0354–0.0370× | 3.55× | SLOWER |
| Practice | `cal.window.match` | Native C engine | 0.9045× | 0.8574–0.9407× | 0.18× | — |
| Practice | `cal.window.match` | Rust engine | 0.0183× | 0.0179–0.0187× | 2.45× | SLOWER |
| Practice | `cal.literal.replace` | Python engine | 0.0060× | 0.0059–0.0061× | 41.75× | SLOWER |
| Practice | `cal.literal.replace` | Native C engine | 1.2735× | 1.2156–1.3131× | 0.53× | FASTER |
| Practice | `cal.literal.replace` | Rust engine | 0.0051× | 0.0050–0.0052× | 10.40× | SLOWER |
| Practice | `cal.template.repeat` | Python engine | 0.0184× | 0.0180–0.0190× | 6.29× | SLOWER |
| Practice | `cal.template.repeat` | Native C engine | 1.5317× | 1.4935–1.5813× | 0.15× | FASTER |
| Practice | `cal.template.repeat` | Rust engine | 0.0125× | 0.0121–0.0130× | 2.29× | SLOWER |
| Practice | `cal.match.miss` | Python engine | 0.0288× | 0.0271–0.0319× | 5.02× | SLOWER |
| Practice | `cal.match.miss` | Native C engine | 1.1821× | 1.1103–1.3001× | 0.00× | FASTER |
| Practice | `cal.match.miss` | Rust engine | 0.0082× | 0.0077–0.0090× | 4.00× | SLOWER |
| Practice | `cal.fullmatch.miss` | Python engine | 0.0166× | 0.0164–0.0167× | 11.09× | SLOWER |
| Practice | `cal.fullmatch.miss` | Native C engine | 1.1729× | 1.1659–1.1797× | 0.00× | FASTER |
| Practice | `cal.fullmatch.miss` | Rust engine | 0.0216× | 0.0210–0.0220× | 3.32× | SLOWER |
| Holdout | `hold.real.log` | Python engine | 0.0028× | 0.0027–0.0029× | 36.41× | SLOWER |
| Holdout | `hold.real.log` | Native C engine | 0.2713× | 0.2612–0.2826× | 0.33× | SLOWER |
| Holdout | `hold.real.log` | Rust engine | 0.0057× | 0.0055–0.0059× | 3.23× | SLOWER |
| Holdout | `hold.real.url` | Python engine | 0.0054× | 0.0051–0.0059× | 26.93× | SLOWER |
| Holdout | `hold.real.url` | Native C engine | 0.4778× | 0.4633–0.4933× | 0.11× | SLOWER |
| Holdout | `hold.real.url` | Rust engine | 0.0104× | 0.0098–0.0113× | 3.79× | SLOWER |
| Holdout | `hold.real.email` | Python engine | 0.0044× | 0.0041–0.0047× | 12.09× | SLOWER |
| Holdout | `hold.real.email` | Native C engine | 0.6788× | 0.6327–0.7450× | 0.12× | SLOWER |
| Holdout | `hold.real.email` | Rust engine | 0.0071× | 0.0067–0.0076× | 3.88× | SLOWER |
| Holdout | `hold.real.datetime` | Python engine | 0.0072× | 0.0072–0.0073× | 27.33× | SLOWER |
| Holdout | `hold.real.datetime` | Native C engine | 0.8905× | 0.8842–0.8974× | 0.09× | — |
| Holdout | `hold.real.datetime` | Rust engine | 0.0166× | 0.0164–0.0168× | 3.42× | SLOWER |
| Holdout | `hold.real.version` | Python engine | 0.0091× | 0.0089–0.0093× | 23.70× | SLOWER |
| Holdout | `hold.real.version` | Native C engine | 0.7964× | 0.7675–0.8171× | 0.06× | SLOWER |
| Holdout | `hold.real.version` | Rust engine | 0.0205× | 0.0201–0.0209× | 3.01× | SLOWER |
| Holdout | `hold.real.uuid` | Python engine | 0.0061× | 0.0061–0.0062× | 18.05× | SLOWER |
| Holdout | `hold.real.uuid` | Native C engine | 0.7392× | 0.7304–0.7469× | 0.07× | SLOWER |
| Holdout | `hold.real.uuid` | Rust engine | 0.0129× | 0.0128–0.0130× | 3.95× | SLOWER |
| Holdout | `hold.real.ip` | Python engine | 0.0089× | 0.0084–0.0098× | 30.05× | SLOWER |
| Holdout | `hold.real.ip` | Native C engine | 0.9633× | 0.8603–1.0916× | 0.07× | — |
| Holdout | `hold.real.ip` | Rust engine | 0.0205× | 0.0189–0.0222× | 3.02× | SLOWER |
| Holdout | `hold.real.path` | Python engine | 0.0058× | 0.0055–0.0064× | 26.39× | SLOWER |
| Holdout | `hold.real.path` | Native C engine | 0.7734× | 0.7288–0.8559× | 0.12× | SLOWER |
| Holdout | `hold.real.path` | Rust engine | 0.0098× | 0.0093–0.0108× | 3.84× | SLOWER |
| Holdout | `hold.real.config` | Python engine | 0.0090× | 0.0082–0.0103× | 18.02× | SLOWER |
| Holdout | `hold.real.config` | Native C engine | 0.9496× | 0.8995–1.0099× | 0.35× | — |
| Holdout | `hold.real.config` | Rust engine | 0.0162× | 0.0148–0.0182× | 2.32× | SLOWER |
| Holdout | `hold.real.comments` | Python engine | 0.0046× | 0.0046–0.0047× | 16.97× | SLOWER |
| Holdout | `hold.real.comments` | Native C engine | 0.7129× | 0.7054–0.7211× | 0.14× | SLOWER |
| Holdout | `hold.real.comments` | Rust engine | 0.0031× | 0.0031–0.0032× | 4.05× | SLOWER |
| Holdout | `hold.real.whitespace` | Python engine | 0.0069× | 0.0068–0.0070× | 8.45× | SLOWER |
| Holdout | `hold.real.whitespace` | Native C engine | 1.3437× | 1.2439–1.4140× | 0.14× | FASTER |
| Holdout | `hold.real.whitespace` | Rust engine | 0.0069× | 0.0068–0.0070× | 2.74× | SLOWER |
| Holdout | `hold.real.lines` | Python engine | 0.0092× | 0.0089–0.0095× | 13.22× | SLOWER |
| Holdout | `hold.real.lines` | Native C engine | 0.9559× | 0.9382–0.9809× | 0.14× | — |
| Holdout | `hold.real.lines` | Rust engine | 0.0089× | 0.0086–0.0091× | 2.82× | SLOWER |
| Holdout | `hold.real.markup` | Python engine | 0.0046× | 0.0045–0.0047× | 14.16× | SLOWER |
| Holdout | `hold.real.markup` | Native C engine | 0.5736× | 0.5414–0.6022× | 0.13× | SLOWER |
| Holdout | `hold.real.markup` | Rust engine | 0.0031× | 0.0030–0.0032× | 4.34× | SLOWER |
| Holdout | `hold.real.quotes` | Python engine | 0.0040× | 0.0040–0.0040× | 18.87× | SLOWER |
| Holdout | `hold.real.quotes` | Native C engine | 0.6114× | 0.6075–0.6149× | 0.10× | SLOWER |
| Holdout | `hold.real.quotes` | Rust engine | 0.0069× | 0.0069–0.0070× | 3.58× | SLOWER |
| Holdout | `hold.real.csv` | Python engine | 0.0039× | 0.0039–0.0039× | 18.08× | SLOWER |
| Holdout | `hold.real.csv` | Native C engine | 0.3077× | 0.2756–0.3297× | 0.32× | SLOWER |
| Holdout | `hold.real.csv` | Rust engine | 0.0090× | 0.0089–0.0092× | 3.21× | SLOWER |
| Holdout | `hold.branch.prefix` | Python engine | 0.0098× | 0.0097–0.0099× | 11.86× | SLOWER |
| Holdout | `hold.branch.prefix` | Native C engine | 0.7206× | 0.6579–0.7606× | 0.07× | SLOWER |
| Holdout | `hold.branch.prefix` | Rust engine | 0.0130× | 0.0128–0.0132× | 3.36× | SLOWER |
| Holdout | `hold.branch.miss` | Python engine | 0.0008× | 0.0008–0.0008× | 80.13× | SLOWER |
| Holdout | `hold.branch.miss` | Native C engine | 0.0738× | 0.0729–0.0747× | 0.00× | SLOWER |
| Holdout | `hold.branch.miss` | Rust engine | 0.0109× | 0.0107–0.0111× | 4.57× | SLOWER |
| Holdout | `hold.repeat.nested` | Python engine | 0.0095× | 0.0093–0.0096× | 15.24× | SLOWER |
| Holdout | `hold.repeat.nested` | Native C engine | 0.7600× | 0.7340–0.7801× | 0.64× | SLOWER |
| Holdout | `hold.repeat.nested` | Rust engine | 0.0211× | 0.0208–0.0215× | 1.57× | SLOWER |
| Holdout | `hold.lines.records` | Python engine | 0.0085× | 0.0083–0.0088× | 14.74× | SLOWER |
| Holdout | `hold.lines.records` | Native C engine | 1.0053× | 0.9758–1.0401× | 0.36× | — |
| Holdout | `hold.lines.records` | Rust engine | 0.0076× | 0.0074–0.0078× | 2.55× | SLOWER |
| Holdout | `hold.block.dotall` | Python engine | 0.0063× | 0.0061–0.0067× | 18.13× | SLOWER |
| Holdout | `hold.block.dotall` | Native C engine | 0.6483× | 0.6275–0.6821× | 0.08× | SLOWER |
| Holdout | `hold.block.dotall` | Rust engine | 0.0131× | 0.0127–0.0137× | 4.00× | SLOWER |
| Holdout | `hold.pattern.verbose` | Python engine | 0.0039× | 0.0036–0.0045× | 15.91× | SLOWER |
| Holdout | `hold.pattern.verbose` | Native C engine | 0.5212× | 0.4911–0.5768× | 0.09× | SLOWER |
| Holdout | `hold.pattern.verbose` | Rust engine | 0.0259× | 0.0241–0.0284× | 3.45× | SLOWER |
| Holdout | `hold.mode.ascii` | Python engine | 0.0055× | 0.0052–0.0057× | 7.82× | SLOWER |
| Holdout | `hold.mode.ascii` | Native C engine | 0.9239× | 0.8905–0.9730× | 0.21× | — |
| Holdout | `hold.mode.ascii` | Rust engine | 0.0081× | 0.0078–0.0085× | 3.02× | SLOWER |
| Holdout | `hold.mode.casefold` | Python engine | 0.0081× | 0.0079–0.0083× | 5.44× | SLOWER |
| Holdout | `hold.mode.casefold` | Native C engine | 1.1250× | 1.0418–1.1859× | 0.18× | FASTER |
| Holdout | `hold.mode.casefold` | Rust engine | 0.0104× | 0.0101–0.0106× | 2.93× | SLOWER |
| Holdout | `hold.mode.astral` | Python engine | 0.0093× | 0.0087–0.0103× | 7.06× | SLOWER |
| Holdout | `hold.mode.astral` | Native C engine | 1.6195× | 1.5404–1.7719× | 0.25× | FASTER |
| Holdout | `hold.mode.astral` | Rust engine | 0.0090× | 0.0089–0.0092× | 2.77× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Python engine | 0.0035× | 0.0035–0.0035× | 16.30× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Native C engine | 0.3490× | 0.3343–0.3579× | 0.53× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Rust engine | 0.0071× | 0.0071–0.0072× | 3.47× | SLOWER |
| Holdout | `hold.look.negative-behind` | Python engine | 0.0065× | 0.0064–0.0065× | 12.65× | SLOWER |
| Holdout | `hold.look.negative-behind` | Native C engine | 0.6126× | 0.5743–0.6388× | 0.10× | SLOWER |
| Holdout | `hold.look.negative-behind` | Rust engine | 0.0098× | 0.0098–0.0099× | 3.19× | SLOWER |
| Holdout | `hold.bytes.replace` | Python engine | 0.0165× | 0.0156–0.0177× | 9.71× | SLOWER |
| Holdout | `hold.bytes.replace` | Native C engine | 1.1111× | 1.0358–1.2051× | 0.93× | FASTER |
| Holdout | `hold.bytes.replace` | Rust engine | 0.0161× | 0.0153–0.0172× | 2.52× | SLOWER |
| Holdout | `hold.bytes.scan` | Python engine | 0.0116× | 0.0112–0.0120× | 8.55× | SLOWER |
| Holdout | `hold.bytes.scan` | Native C engine | 1.2568× | 1.1845–1.3875× | 0.38× | FASTER |
| Holdout | `hold.bytes.scan` | Rust engine | 0.0099× | 0.0091–0.0110× | 1.87× | SLOWER |
| Holdout | `hold.compile.complex` | Python engine | 1.8723× | 1.8019–1.9973× | 0.37× | FASTER |
| Holdout | `hold.compile.complex` | Native C engine | 1.4026× | 1.2928–1.5216× | 0.89× | FASTER |
| Holdout | `hold.compile.complex` | Rust engine | 1.5176× | 1.4019–1.6553× | 0.55× | FASTER |
| Holdout | `hold.module.replace` | Python engine | 0.0209× | 0.0208–0.0211× | 10.12× | SLOWER |
| Holdout | `hold.module.replace` | Native C engine | 1.2130× | 1.1833–1.2324× | 0.04× | FASTER |
| Holdout | `hold.module.replace` | Rust engine | 0.0195× | 0.0194–0.0197× | 2.52× | SLOWER |
| Holdout | `hold.zero.boundary` | Python engine | 0.0082× | 0.0080–0.0084× | 8.20× | SLOWER |
| Holdout | `hold.zero.boundary` | Native C engine | 0.5768× | 0.5581–0.5978× | 0.62× | SLOWER |
| Holdout | `hold.zero.boundary` | Rust engine | 0.0141× | 0.0138–0.0146× | 1.67× | SLOWER |
| Holdout | `hold.dense.iter` | Python engine | 0.0153× | 0.0153–0.0154× | 4.92× | SLOWER |
| Holdout | `hold.dense.iter` | Native C engine | 1.2094× | 1.1870–1.2331× | 0.51× | FASTER |
| Holdout | `hold.dense.iter` | Rust engine | 0.0078× | 0.0077–0.0078× | 1.50× | SLOWER |
| Holdout | `hold.capture.optional` | Python engine | 0.0099× | 0.0098–0.0101× | 14.26× | SLOWER |
| Holdout | `hold.capture.optional` | Native C engine | 0.9290× | 0.9127–0.9464× | 0.18× | — |
| Holdout | `hold.capture.optional` | Rust engine | 0.0083× | 0.0081–0.0084× | 2.79× | SLOWER |
| Holdout | `hold.split.limited` | Python engine | 0.0063× | 0.0062–0.0063× | 7.46× | SLOWER |
| Holdout | `hold.split.limited` | Native C engine | 0.8365× | 0.8127–0.8530× | 0.19× | — |
| Holdout | `hold.split.limited` | Rust engine | 0.0071× | 0.0071–0.0072× | 2.83× | SLOWER |
| Holdout | `hold.replace.limited` | Python engine | 0.0131× | 0.0126–0.0137× | 6.04× | SLOWER |
| Holdout | `hold.replace.limited` | Native C engine | 1.2388× | 1.2019–1.2934× | 0.15× | FASTER |
| Holdout | `hold.replace.limited` | Rust engine | 0.0089× | 0.0087–0.0093× | 2.90× | SLOWER |
| Holdout | `hold.bytes.view-long` | Python engine | 0.0067× | 0.0066–0.0068× | 48.64× | SLOWER |
| Holdout | `hold.bytes.view-long` | Native C engine | 1.1242× | 1.1025–1.1439× | 0.60× | FASTER |
| Holdout | `hold.bytes.view-long` | Rust engine | 0.0009× | 0.0009–0.0010× | 5.61× | SLOWER |
| Holdout | `hold.window.search` | Python engine | 0.0185× | 0.0183–0.0186× | 4.40× | SLOWER |
| Holdout | `hold.window.search` | Native C engine | 0.8805× | 0.8738–0.8877× | 0.18× | — |
| Holdout | `hold.window.search` | Rust engine | 0.0145× | 0.0144–0.0146× | 3.32× | SLOWER |
| Holdout | `hold.window.findall` | Python engine | 0.0174× | 0.0171–0.0177× | 4.03× | SLOWER |
| Holdout | `hold.window.findall` | Native C engine | 0.9655× | 0.9486–0.9841× | 0.22× | — |
| Holdout | `hold.window.findall` | Rust engine | 0.0072× | 0.0071–0.0074× | 2.86× | SLOWER |
| Holdout | `hold.window.scanner` | Python engine | 0.0179× | 0.0171–0.0192× | 4.46× | SLOWER |
| Holdout | `hold.window.scanner` | Native C engine | 1.0658× | 1.0154–1.1418× | 0.30× | FASTER |
| Holdout | `hold.window.scanner` | Rust engine | 0.0096× | 0.0091–0.0102× | 2.20× | SLOWER |
| Holdout | `hold.window.match` | Python engine | 0.0328× | 0.0311–0.0353× | 3.55× | SLOWER |
| Holdout | `hold.window.match` | Native C engine | 0.8082× | 0.7306–0.8685× | 0.18× | — |
| Holdout | `hold.window.match` | Rust engine | 0.0174× | 0.0167–0.0185× | 2.46× | SLOWER |
| Holdout | `hold.literal.replace` | Python engine | 0.0061× | 0.0059–0.0063× | 38.88× | SLOWER |
| Holdout | `hold.literal.replace` | Native C engine | 1.2526× | 1.2210–1.2954× | 0.52× | FASTER |
| Holdout | `hold.literal.replace` | Rust engine | 0.0053× | 0.0052–0.0055× | 10.36× | SLOWER |
| Holdout | `hold.template.repeat` | Python engine | 0.0189× | 0.0185–0.0193× | 6.32× | SLOWER |
| Holdout | `hold.template.repeat` | Native C engine | 1.5409× | 1.4841–1.5952× | 0.14× | FASTER |
| Holdout | `hold.template.repeat` | Rust engine | 0.0140× | 0.0137–0.0144× | 2.28× | SLOWER |
| Holdout | `hold.match.miss` | Python engine | 0.0275× | 0.0271–0.0278× | 5.02× | SLOWER |
| Holdout | `hold.match.miss` | Native C engine | 1.1389× | 1.1281–1.1500× | 0.00× | FASTER |
| Holdout | `hold.match.miss` | Rust engine | 0.0072× | 0.0071–0.0073× | 4.20× | SLOWER |
| Holdout | `hold.fullmatch.miss` | Python engine | 0.0172× | 0.0170–0.0173× | 11.09× | SLOWER |
| Holdout | `hold.fullmatch.miss` | Native C engine | 1.2026× | 1.1919–1.2134× | 0.00× | FASTER |
| Holdout | `hold.fullmatch.miss` | Rust engine | 0.0221× | 0.0215–0.0226× | 3.31× | SLOWER |

## Large slowdowns

- Python engine: `cal.search.literal.hit` (0.007×), `cal.search.literal.miss` (0.002×), `cal.search.long-boundary` (0.000×), `cal.search.class-anchor` (0.011×), `cal.match.prefix` (0.023×), `cal.fullmatch.structured` (0.013×), `cal.search.look-capture` (0.007×), `cal.findall.tokens` (0.010×), `cal.finditer.groups` (0.013×), `cal.split.capture` (0.010×), `cal.sub.template` (0.017×), `cal.subn.callable` (0.023×), `cal.bytes.tokens` (0.007×), `cal.unicode.words` (0.006×), `cal.cold.compile-search` (0.291×), `cal.module.warm` (0.011×), `cal.empty.finditer` (0.010×), `cal.backref.fullmatch` (0.019×), `cal.conditional.match` (0.018×), `cal.atomic.search` (0.010×), `cal.byteslike.findall` (0.011×), `cal.unicode-name.search` (0.014×), `cal.ignorecase.findall` (0.007×), `cal.many.split` (0.012×), `cal.scanner.search` (0.013×), `cal.match.surface` (0.014×), `hold.search.literal.hit` (0.007×), `hold.search.literal.miss` (0.002×), `hold.search.long-boundary` (0.000×), `hold.search.class-anchor` (0.010×), `hold.match.prefix` (0.024×), `hold.fullmatch.structured` (0.011×), `hold.search.look-capture` (0.010×), `hold.findall.tokens` (0.011×), `hold.finditer.groups` (0.013×), `hold.split.capture` (0.010×), `hold.sub.template` (0.016×), `hold.subn.callable` (0.027×), `hold.bytes.tokens` (0.010×), `hold.unicode.words` (0.009×), `hold.cold.compile-search` (0.485×), `hold.module.warm` (0.019×), `hold.empty.finditer` (0.009×), `hold.backref.fullmatch` (0.019×), `hold.conditional.match` (0.020×), `hold.atomic.search` (0.011×), `hold.byteslike.findall` (0.011×), `hold.unicode-name.search` (0.013×), `hold.ignorecase.findall` (0.008×), `hold.many.split` (0.013×), `hold.scanner.search` (0.013×), `hold.match.surface` (0.021×), `cal.real.log` (0.003×), `cal.real.url` (0.006×), `cal.real.email` (0.005×), `cal.real.datetime` (0.007×), `cal.real.version` (0.011×), `cal.real.uuid` (0.006×), `cal.real.ip` (0.008×), `cal.real.path` (0.006×), `cal.real.config` (0.009×), `cal.real.comments` (0.006×), `cal.real.whitespace` (0.007×), `cal.real.lines` (0.009×), `cal.real.markup` (0.004×), `cal.real.quotes` (0.004×), `cal.real.csv` (0.005×), `cal.branch.prefix` (0.009×), `cal.branch.miss` (0.001×), `cal.repeat.nested` (0.010×), `cal.lines.records` (0.008×), `cal.block.dotall` (0.006×), `cal.pattern.verbose` (0.004×), `cal.mode.ascii` (0.005×), `cal.mode.casefold` (0.008×), `cal.mode.astral` (0.009×), `cal.look.negative-ahead` (0.004×), `cal.look.negative-behind` (0.007×), `cal.bytes.replace` (0.016×), `cal.bytes.scan` (0.011×), `cal.module.replace` (0.022×), `cal.zero.boundary` (0.008×), `cal.dense.iter` (0.016×), `cal.capture.optional` (0.010×), `cal.split.limited` (0.006×), `cal.replace.limited` (0.013×), `cal.bytes.view-long` (0.006×), `cal.window.search` (0.019×), `cal.window.findall` (0.017×), `cal.window.scanner` (0.018×), `cal.window.match` (0.036×), `cal.literal.replace` (0.006×), `cal.template.repeat` (0.018×), `cal.match.miss` (0.029×), `cal.fullmatch.miss` (0.017×), `hold.real.log` (0.003×), `hold.real.url` (0.005×), `hold.real.email` (0.004×), `hold.real.datetime` (0.007×), `hold.real.version` (0.009×), `hold.real.uuid` (0.006×), `hold.real.ip` (0.009×), `hold.real.path` (0.006×), `hold.real.config` (0.009×), `hold.real.comments` (0.005×), `hold.real.whitespace` (0.007×), `hold.real.lines` (0.009×), `hold.real.markup` (0.005×), `hold.real.quotes` (0.004×), `hold.real.csv` (0.004×), `hold.branch.prefix` (0.010×), `hold.branch.miss` (0.001×), `hold.repeat.nested` (0.009×), `hold.lines.records` (0.009×), `hold.block.dotall` (0.006×), `hold.pattern.verbose` (0.004×), `hold.mode.ascii` (0.005×), `hold.mode.casefold` (0.008×), `hold.mode.astral` (0.009×), `hold.look.negative-ahead` (0.004×), `hold.look.negative-behind` (0.006×), `hold.bytes.replace` (0.017×), `hold.bytes.scan` (0.012×), `hold.module.replace` (0.021×), `hold.zero.boundary` (0.008×), `hold.dense.iter` (0.015×), `hold.capture.optional` (0.010×), `hold.split.limited` (0.006×), `hold.replace.limited` (0.013×), `hold.bytes.view-long` (0.007×), `hold.window.search` (0.018×), `hold.window.findall` (0.017×), `hold.window.scanner` (0.018×), `hold.window.match` (0.033×), `hold.literal.replace` (0.006×), `hold.template.repeat` (0.019×), `hold.match.miss` (0.027×), `hold.fullmatch.miss` (0.017×).
- Rust engine: `cal.search.literal.hit` (0.009×), `cal.search.literal.miss` (0.006×), `cal.search.long-boundary` (0.001×), `cal.search.class-anchor` (0.014×), `cal.match.prefix` (0.015×), `cal.fullmatch.structured` (0.018×), `cal.search.look-capture` (0.016×), `cal.findall.tokens` (0.004×), `cal.finditer.groups` (0.010×), `cal.split.capture` (0.007×), `cal.sub.template` (0.015×), `cal.subn.callable` (0.019×), `cal.bytes.tokens` (0.005×), `cal.unicode.words` (0.010×), `cal.cold.compile-search` (0.686×), `cal.module.warm` (0.031×), `cal.empty.finditer` (0.021×), `cal.backref.fullmatch` (0.019×), `cal.conditional.match` (0.016×), `cal.atomic.search` (0.019×), `cal.byteslike.findall` (0.008×), `cal.unicode-name.search` (0.019×), `cal.ignorecase.findall` (0.008×), `cal.many.split` (0.004×), `cal.scanner.search` (0.009×), `cal.match.surface` (0.047×), `hold.search.literal.hit` (0.009×), `hold.search.literal.miss` (0.006×), `hold.search.long-boundary` (0.001×), `hold.search.class-anchor` (0.013×), `hold.match.prefix` (0.015×), `hold.fullmatch.structured` (0.019×), `hold.search.look-capture` (0.017×), `hold.findall.tokens` (0.006×), `hold.finditer.groups` (0.009×), `hold.split.capture` (0.007×), `hold.sub.template` (0.014×), `hold.subn.callable` (0.022×), `hold.bytes.tokens` (0.008×), `hold.unicode.words` (0.012×), `hold.cold.compile-search` (0.738×), `hold.module.warm` (0.032×), `hold.empty.finditer` (0.021×), `hold.backref.fullmatch` (0.020×), `hold.conditional.match` (0.020×), `hold.atomic.search` (0.023×), `hold.byteslike.findall` (0.008×), `hold.unicode-name.search` (0.020×), `hold.ignorecase.findall` (0.009×), `hold.many.split` (0.005×), `hold.scanner.search` (0.009×), `hold.match.surface` (0.041×), `cal.real.log` (0.006×), `cal.real.url` (0.012×), `cal.real.email` (0.006×), `cal.real.datetime` (0.015×), `cal.real.version` (0.029×), `cal.real.uuid` (0.013×), `cal.real.ip` (0.025×), `cal.real.path` (0.010×), `cal.real.config` (0.017×), `cal.real.comments` (0.004×), `cal.real.whitespace` (0.007×), `cal.real.lines` (0.009×), `cal.real.markup` (0.004×), `cal.real.quotes` (0.007×), `cal.real.csv` (0.011×), `cal.branch.prefix` (0.013×), `cal.branch.miss` (0.012×), `cal.repeat.nested` (0.023×), `cal.lines.records` (0.007×), `cal.block.dotall` (0.013×), `cal.pattern.verbose` (0.020×), `cal.mode.ascii` (0.009×), `cal.mode.casefold` (0.009×), `cal.mode.astral` (0.009×), `cal.look.negative-ahead` (0.007×), `cal.look.negative-behind` (0.010×), `cal.bytes.replace` (0.016×), `cal.bytes.scan` (0.009×), `cal.module.replace` (0.020×), `cal.zero.boundary` (0.014×), `cal.dense.iter` (0.008×), `cal.capture.optional` (0.009×), `cal.split.limited` (0.008×), `cal.replace.limited` (0.009×), `cal.bytes.view-long` (0.001×), `cal.window.search` (0.016×), `cal.window.findall` (0.007×), `cal.window.scanner` (0.009×), `cal.window.match` (0.018×), `cal.literal.replace` (0.005×), `cal.template.repeat` (0.013×), `cal.match.miss` (0.008×), `cal.fullmatch.miss` (0.022×), `hold.real.log` (0.006×), `hold.real.url` (0.010×), `hold.real.email` (0.007×), `hold.real.datetime` (0.017×), `hold.real.version` (0.021×), `hold.real.uuid` (0.013×), `hold.real.ip` (0.021×), `hold.real.path` (0.010×), `hold.real.config` (0.016×), `hold.real.comments` (0.003×), `hold.real.whitespace` (0.007×), `hold.real.lines` (0.009×), `hold.real.markup` (0.003×), `hold.real.quotes` (0.007×), `hold.real.csv` (0.009×), `hold.branch.prefix` (0.013×), `hold.branch.miss` (0.011×), `hold.repeat.nested` (0.021×), `hold.lines.records` (0.008×), `hold.block.dotall` (0.013×), `hold.pattern.verbose` (0.026×), `hold.mode.ascii` (0.008×), `hold.mode.casefold` (0.010×), `hold.mode.astral` (0.009×), `hold.look.negative-ahead` (0.007×), `hold.look.negative-behind` (0.010×), `hold.bytes.replace` (0.016×), `hold.bytes.scan` (0.010×), `hold.module.replace` (0.020×), `hold.zero.boundary` (0.014×), `hold.dense.iter` (0.008×), `hold.capture.optional` (0.008×), `hold.split.limited` (0.007×), `hold.replace.limited` (0.009×), `hold.bytes.view-long` (0.001×), `hold.window.search` (0.015×), `hold.window.findall` (0.007×), `hold.window.scanner` (0.010×), `hold.window.match` (0.017×), `hold.literal.replace` (0.005×), `hold.template.repeat` (0.014×), `hold.match.miss` (0.007×), `hold.fullmatch.miss` (0.022×).
- Native C engine: `cal.unicode.words` (0.781×), `cal.empty.finditer` (0.702×), `cal.atomic.search` (0.549×), `hold.empty.finditer` (0.674×), `cal.real.log` (0.299×), `cal.real.url` (0.710×), `cal.real.email` (0.476×), `cal.real.datetime` (0.728×), `cal.real.uuid` (0.792×), `cal.real.path` (0.748×), `cal.real.comments` (0.751×), `cal.real.markup` (0.568×), `cal.real.quotes` (0.599×), `cal.real.csv` (0.385×), `cal.branch.prefix` (0.701×), `cal.branch.miss` (0.086×), `cal.block.dotall` (0.663×), `cal.pattern.verbose` (0.522×), `cal.look.negative-ahead` (0.365×), `cal.look.negative-behind` (0.630×), `cal.zero.boundary` (0.559×), `hold.real.log` (0.271×), `hold.real.url` (0.478×), `hold.real.email` (0.679×), `hold.real.version` (0.796×), `hold.real.uuid` (0.739×), `hold.real.path` (0.773×), `hold.real.comments` (0.713×), `hold.real.markup` (0.574×), `hold.real.quotes` (0.611×), `hold.real.csv` (0.308×), `hold.branch.prefix` (0.721×), `hold.branch.miss` (0.074×), `hold.repeat.nested` (0.760×), `hold.block.dotall` (0.648×), `hold.pattern.verbose` (0.521×), `hold.look.negative-ahead` (0.349×), `hold.look.negative-behind` (0.613×), `hold.zero.boundary` (0.577×).

The Python engine performs matching work in Python, and the Rust engine repeatedly prepares data and crosses the Python/Rust boundary; both costs dominate short tasks. Native-C losses expose specific boundary and general-path costs:
- Repeated text/Unicode matching needs character-category and word-boundary checks that cannot use the simplest one-pass scan.
- Empty matches and controlled branches use the general backtracking/iterator path and construct more match state.
- Everyday log, address, path, comment, markup, quote, and comma-separated-field tasks combine repeated classes, captures, or lookarounds; they take the general native backtracking path instead of its compact single-pass path.
- Searches across many alternative words, especially a complete miss, try branches at successive positions because the native engine has no shared-prefix or start-character filter for these alternatives.
- Structured repeated paths, multi-line blocks, and readable formatted fields require general repeat/capture backtracking, which carries more state than the simple literal and single-character fast paths.
- Excluded-prefix and tagged-word searches evaluate a negative lookaround for each possible match, so the native executor repeats assertion work while scanning.
- Word/separator-position iteration and limited mixed-separator splits repeatedly use the general iterator or whitespace-backtracking path; each small match pays state and result-construction costs.

No loss is removed from the denominator or hidden from the charts.
