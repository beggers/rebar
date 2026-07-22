# Broader performance: native start and class filters

All 7488 raw timing rows, 432 engine/task results, and 300 large slowdowns are retained. Raw SHA-256: `84162c86b6565be74aef3812db670450d517deb239652f1d16963a0394544b6b`.

## At a glance

The holdout tasks were kept separate from tuning. **1× means the same speed as Python `re`; higher is faster.** A result is clearly faster only when its measured range stays above 1×. A large slowdown means more than 20% slower.

| Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: | ---: |
| Native C engine | **1.0967×** | 1.0897–1.1037× | 37/72 | 12/72 |
| Rust engine | **0.0136×** | 0.0136–0.0137× | 2/72 | 69/72 |
| Python engine | **0.0116×** | 0.0115–0.0116× | 2/72 | 69/72 |

## Overall results

| Task set | Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |
| --- | --- | ---: | ---: | ---: | ---: |
| Practice | Python engine | 0.0113× | 0.0113–0.0114× | 2/72 | 69 |
| Practice | Native C engine | 1.0664× | 1.0591–1.0736× | 42/72 | 12 |
| Practice | Rust engine | 0.0135× | 0.0134–0.0136× | 2/72 | 69 |
| Holdout | Python engine | 0.0116× | 0.0115–0.0116× | 2/72 | 69 |
| Holdout | Native C engine | 1.0967× | 1.0897–1.1037× | 37/72 | 12 |
| Holdout | Rust engine | 0.0136× | 0.0136–0.0137× | 2/72 | 69 |
| All | Python engine | 0.0115× | 0.0114–0.0115× | 4/144 | 138 |
| All | Native C engine | 1.0814× | 1.0764–1.0865× | 79/144 | 24 |
| All | Rust engine | 0.0136× | 0.0135–0.0136× | 4/144 | 138 |

## Every task

`FASTER` means the measured range stays above 1×. `SLOWER` means more than 20% slower. Memory compares median traced Python memory with Python `re`.

| Task set | Task | Engine | Speed | Measured range | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Practice | `cal.search.literal.hit` | Python engine | 0.0074× | 0.0072–0.0075× | 102.00× | SLOWER |
| Practice | `cal.search.literal.hit` | Native C engine | 1.1186× | 1.1029–1.1345× | 0.73× | FASTER |
| Practice | `cal.search.literal.hit` | Rust engine | 0.0087× | 0.0087–0.0088× | 34.03× | SLOWER |
| Practice | `cal.search.literal.miss` | Python engine | 0.0022× | 0.0021–0.0024× | 14408.00× | SLOWER |
| Practice | `cal.search.literal.miss` | Native C engine | 1.1492× | 1.0188–1.2854× | 0.00× | FASTER |
| Practice | `cal.search.literal.miss` | Rust engine | 0.0059× | 0.0056–0.0064× | 4375.00× | SLOWER |
| Practice | `cal.search.long-boundary` | Python engine | 0.0003× | 0.0003–0.0003× | 129.57× | SLOWER |
| Practice | `cal.search.long-boundary` | Native C engine | 12.0735× | 11.2192–13.2779× | 0.07× | FASTER |
| Practice | `cal.search.long-boundary` | Rust engine | 0.0010× | 0.0009–0.0011× | 140.03× | SLOWER |
| Practice | `cal.search.class-anchor` | Python engine | 0.0111× | 0.0110–0.0113× | 11.57× | SLOWER |
| Practice | `cal.search.class-anchor` | Native C engine | 1.0660× | 1.0480–1.0854× | 0.07× | FASTER |
| Practice | `cal.search.class-anchor` | Rust engine | 0.0145× | 0.0143–0.0148× | 3.36× | SLOWER |
| Practice | `cal.match.prefix` | Python engine | 0.0233× | 0.0230–0.0235× | 3.87× | SLOWER |
| Practice | `cal.match.prefix` | Native C engine | 1.1246× | 1.1122–1.1366× | 0.07× | FASTER |
| Practice | `cal.match.prefix` | Rust engine | 0.0149× | 0.0147–0.0151× | 2.89× | SLOWER |
| Practice | `cal.fullmatch.structured` | Python engine | 0.0125× | 0.0123–0.0128× | 12.07× | SLOWER |
| Practice | `cal.fullmatch.structured` | Native C engine | 1.0156× | 1.0022–1.0359× | 0.07× | FASTER |
| Practice | `cal.fullmatch.structured` | Rust engine | 0.0180× | 0.0177–0.0184× | 3.04× | SLOWER |
| Practice | `cal.search.look-capture` | Python engine | 0.0075× | 0.0074–0.0077× | 17.28× | SLOWER |
| Practice | `cal.search.look-capture` | Native C engine | 1.1915× | 1.1675–1.2231× | 0.08× | FASTER |
| Practice | `cal.search.look-capture` | Rust engine | 0.0159× | 0.0156–0.0162× | 3.29× | SLOWER |
| Practice | `cal.findall.tokens` | Python engine | 0.0104× | 0.0099–0.0111× | 7.14× | SLOWER |
| Practice | `cal.findall.tokens` | Native C engine | 0.9837× | 0.9169–1.0659× | 0.28× | — |
| Practice | `cal.findall.tokens` | Rust engine | 0.0038× | 0.0036–0.0041× | 3.26× | SLOWER |
| Practice | `cal.finditer.groups` | Python engine | 0.0129× | 0.0124–0.0134× | 7.75× | SLOWER |
| Practice | `cal.finditer.groups` | Native C engine | 1.4796× | 1.3895–1.5758× | 0.39× | FASTER |
| Practice | `cal.finditer.groups` | Rust engine | 0.0097× | 0.0093–0.0102× | 1.91× | SLOWER |
| Practice | `cal.split.capture` | Python engine | 0.0099× | 0.0098–0.0101× | 11.37× | SLOWER |
| Practice | `cal.split.capture` | Native C engine | 1.7860× | 1.7629–1.8152× | 0.20× | FASTER |
| Practice | `cal.split.capture` | Rust engine | 0.0066× | 0.0064–0.0067× | 2.62× | SLOWER |
| Practice | `cal.sub.template` | Python engine | 0.0169× | 0.0161–0.0185× | 9.30× | SLOWER |
| Practice | `cal.sub.template` | Native C engine | 1.9245× | 1.8174–2.1181× | 0.12× | FASTER |
| Practice | `cal.sub.template` | Rust engine | 0.0155× | 0.0149–0.0165× | 2.39× | SLOWER |
| Practice | `cal.subn.callable` | Python engine | 0.0233× | 0.0230–0.0237× | 5.05× | SLOWER |
| Practice | `cal.subn.callable` | Native C engine | 1.0333× | 0.9747–1.0788× | 0.25× | — |
| Practice | `cal.subn.callable` | Rust engine | 0.0192× | 0.0190–0.0195× | 2.56× | SLOWER |
| Practice | `cal.bytes.tokens` | Python engine | 0.0076× | 0.0072–0.0082× | 8.29× | SLOWER |
| Practice | `cal.bytes.tokens` | Native C engine | 1.1435× | 1.0918–1.2224× | 0.12× | FASTER |
| Practice | `cal.bytes.tokens` | Rust engine | 0.0058× | 0.0056–0.0062× | 3.43× | SLOWER |
| Practice | `cal.unicode.words` | Python engine | 0.0061× | 0.0060–0.0062× | 6.52× | SLOWER |
| Practice | `cal.unicode.words` | Native C engine | 0.8825× | 0.7999–0.9330× | 0.20× | — |
| Practice | `cal.unicode.words` | Rust engine | 0.0096× | 0.0095–0.0097× | 2.69× | SLOWER |
| Practice | `cal.cold.compile-search` | Python engine | 0.2897× | 0.2783–0.2970× | 5.84× | SLOWER |
| Practice | `cal.cold.compile-search` | Native C engine | 0.7418× | 0.7363–0.7476× | 1.50× | SLOWER |
| Practice | `cal.cold.compile-search` | Rust engine | 0.7014× | 0.6923–0.7113× | 1.95× | SLOWER |
| Practice | `cal.module.warm` | Python engine | 0.0101× | 0.0098–0.0104× | 7.21× | SLOWER |
| Practice | `cal.module.warm` | Native C engine | 1.1893× | 1.1731–1.2057× | 0.07× | FASTER |
| Practice | `cal.module.warm` | Rust engine | 0.0306× | 0.0302–0.0310× | 3.39× | SLOWER |
| Practice | `cal.empty.finditer` | Python engine | 0.0101× | 0.0098–0.0106× | 8.09× | SLOWER |
| Practice | `cal.empty.finditer` | Native C engine | 0.6784× | 0.6372–0.7212× | 0.59× | SLOWER |
| Practice | `cal.empty.finditer` | Rust engine | 0.0215× | 0.0207–0.0225× | 1.67× | SLOWER |
| Practice | `cal.backref.fullmatch` | Python engine | 0.0179× | 0.0177–0.0180× | 6.99× | SLOWER |
| Practice | `cal.backref.fullmatch` | Native C engine | 0.9873× | 0.8944–1.0470× | 0.08× | — |
| Practice | `cal.backref.fullmatch` | Rust engine | 0.0176× | 0.0174–0.0178× | 3.04× | SLOWER |
| Practice | `cal.conditional.match` | Python engine | 0.0176× | 0.0174–0.0178× | 6.78× | SLOWER |
| Practice | `cal.conditional.match` | Native C engine | 1.1624× | 1.1417–1.1821× | 0.08× | FASTER |
| Practice | `cal.conditional.match` | Rust engine | 0.0159× | 0.0157–0.0161× | 2.97× | SLOWER |
| Practice | `cal.atomic.search` | Python engine | 0.0096× | 0.0095–0.0098× | 8.80× | SLOWER |
| Practice | `cal.atomic.search` | Native C engine | 1.0237× | 1.0124–1.0374× | 0.50× | FASTER |
| Practice | `cal.atomic.search` | Rust engine | 0.0186× | 0.0184–0.0188× | 3.14× | SLOWER |
| Practice | `cal.byteslike.findall` | Python engine | 0.0105× | 0.0104–0.0107× | 7.48× | SLOWER |
| Practice | `cal.byteslike.findall` | Native C engine | 1.8616× | 1.6677–1.9741× | 0.18× | FASTER |
| Practice | `cal.byteslike.findall` | Rust engine | 0.0077× | 0.0075–0.0079× | 2.93× | SLOWER |
| Practice | `cal.unicode-name.search` | Python engine | 0.0139× | 0.0134–0.0145× | 4.37× | SLOWER |
| Practice | `cal.unicode-name.search` | Native C engine | 1.3170× | 1.2871–1.3654× | 0.07× | FASTER |
| Practice | `cal.unicode-name.search` | Rust engine | 0.0190× | 0.0185–0.0196× | 3.14× | SLOWER |
| Practice | `cal.ignorecase.findall` | Python engine | 0.0072× | 0.0070–0.0077× | 5.14× | SLOWER |
| Practice | `cal.ignorecase.findall` | Native C engine | 1.3214× | 1.2782–1.4004× | 0.16× | FASTER |
| Practice | `cal.ignorecase.findall` | Rust engine | 0.0084× | 0.0082–0.0090× | 2.96× | SLOWER |
| Practice | `cal.many.split` | Python engine | 0.0118× | 0.0117–0.0119× | 8.86× | SLOWER |
| Practice | `cal.many.split` | Native C engine | 1.1637× | 1.1570–1.1698× | 0.20× | FASTER |
| Practice | `cal.many.split` | Rust engine | 0.0043× | 0.0043–0.0043× | 2.86× | SLOWER |
| Practice | `cal.escape.text` | Python engine | 0.9877× | 0.9651–1.0025× | 1.00× | — |
| Practice | `cal.escape.text` | Native C engine | 0.9988× | 0.9929–1.0053× | 1.00× | — |
| Practice | `cal.escape.text` | Rust engine | 0.9911× | 0.9814–0.9993× | 1.00× | — |
| Practice | `cal.compile.only` | Python engine | 2.1935× | 2.1310–2.2524× | 0.50× | FASTER |
| Practice | `cal.compile.only` | Native C engine | 1.6819× | 1.6470–1.7115× | 1.40× | FASTER |
| Practice | `cal.compile.only` | Rust engine | 1.7950× | 1.7688–1.8184× | 0.56× | FASTER |
| Practice | `cal.scanner.search` | Python engine | 0.0127× | 0.0125–0.0129× | 6.71× | SLOWER |
| Practice | `cal.scanner.search` | Native C engine | 1.0264× | 1.0133–1.0388× | 0.36× | FASTER |
| Practice | `cal.scanner.search` | Rust engine | 0.0086× | 0.0085–0.0087× | 1.98× | SLOWER |
| Practice | `cal.match.surface` | Python engine | 0.0145× | 0.0140–0.0151× | 12.88× | SLOWER |
| Practice | `cal.match.surface` | Native C engine | 1.2904× | 1.2220–1.3619× | 0.32× | FASTER |
| Practice | `cal.match.surface` | Rust engine | 0.0484× | 0.0472–0.0504× | 3.26× | SLOWER |
| Holdout | `hold.search.literal.hit` | Python engine | 0.0074× | 0.0073–0.0075× | 102.00× | SLOWER |
| Holdout | `hold.search.literal.hit` | Native C engine | 1.1150× | 1.0906–1.1361× | 0.73× | FASTER |
| Holdout | `hold.search.literal.hit` | Rust engine | 0.0091× | 0.0090–0.0092× | 33.96× | SLOWER |
| Holdout | `hold.search.literal.miss` | Python engine | 0.0024× | 0.0023–0.0024× | 14408.00× | SLOWER |
| Holdout | `hold.search.literal.miss` | Native C engine | 1.1727× | 1.1662–1.1795× | 0.00× | FASTER |
| Holdout | `hold.search.literal.miss` | Rust engine | 0.0056× | 0.0055–0.0057× | 4375.00× | SLOWER |
| Holdout | `hold.search.long-boundary` | Python engine | 0.0003× | 0.0003–0.0003× | 130.58× | SLOWER |
| Holdout | `hold.search.long-boundary` | Native C engine | 17.5959× | 15.7500–19.6431× | 0.07× | FASTER |
| Holdout | `hold.search.long-boundary` | Rust engine | 0.0010× | 0.0009–0.0011× | 218.22× | SLOWER |
| Holdout | `hold.search.class-anchor` | Python engine | 0.0100× | 0.0096–0.0109× | 11.17× | SLOWER |
| Holdout | `hold.search.class-anchor` | Native C engine | 1.0574× | 1.0046–1.1525× | 0.07× | FASTER |
| Holdout | `hold.search.class-anchor` | Rust engine | 0.0135× | 0.0128–0.0147× | 3.39× | SLOWER |
| Holdout | `hold.match.prefix` | Python engine | 0.0250× | 0.0237–0.0272× | 3.87× | SLOWER |
| Holdout | `hold.match.prefix` | Native C engine | 1.1717× | 1.1046–1.2849× | 0.07× | FASTER |
| Holdout | `hold.match.prefix` | Rust engine | 0.0163× | 0.0154–0.0178× | 2.87× | SLOWER |
| Holdout | `hold.fullmatch.structured` | Python engine | 0.0110× | 0.0108–0.0112× | 16.36× | SLOWER |
| Holdout | `hold.fullmatch.structured` | Native C engine | 0.9988× | 0.9849–1.0150× | 0.07× | — |
| Holdout | `hold.fullmatch.structured` | Rust engine | 0.0186× | 0.0181–0.0190× | 3.04× | SLOWER |
| Holdout | `hold.search.look-capture` | Python engine | 0.0098× | 0.0097–0.0100× | 17.64× | SLOWER |
| Holdout | `hold.search.look-capture` | Native C engine | 0.9187× | 0.9040–0.9351× | 0.17× | — |
| Holdout | `hold.search.look-capture` | Rust engine | 0.0167× | 0.0165–0.0171× | 3.26× | SLOWER |
| Holdout | `hold.findall.tokens` | Python engine | 0.0110× | 0.0106–0.0113× | 11.27× | SLOWER |
| Holdout | `hold.findall.tokens` | Native C engine | 1.4509× | 1.4161–1.4858× | 0.21× | FASTER |
| Holdout | `hold.findall.tokens` | Rust engine | 0.0060× | 0.0058–0.0062× | 3.10× | SLOWER |
| Holdout | `hold.finditer.groups` | Python engine | 0.0125× | 0.0122–0.0129× | 7.75× | SLOWER |
| Holdout | `hold.finditer.groups` | Native C engine | 1.4348× | 1.3899–1.4833× | 0.39× | FASTER |
| Holdout | `hold.finditer.groups` | Rust engine | 0.0088× | 0.0085–0.0091× | 1.93× | SLOWER |
| Holdout | `hold.split.capture` | Python engine | 0.0100× | 0.0097–0.0103× | 11.37× | SLOWER |
| Holdout | `hold.split.capture` | Native C engine | 1.7488× | 1.6787–1.8053× | 0.20× | FASTER |
| Holdout | `hold.split.capture` | Rust engine | 0.0068× | 0.0067–0.0069× | 2.62× | SLOWER |
| Holdout | `hold.sub.template` | Python engine | 0.0163× | 0.0158–0.0170× | 9.29× | SLOWER |
| Holdout | `hold.sub.template` | Native C engine | 1.8463× | 1.7355–1.9575× | 0.12× | FASTER |
| Holdout | `hold.sub.template` | Rust engine | 0.0145× | 0.0132–0.0156× | 2.39× | SLOWER |
| Holdout | `hold.subn.callable` | Python engine | 0.0272× | 0.0269–0.0275× | 4.58× | SLOWER |
| Holdout | `hold.subn.callable` | Native C engine | 1.0290× | 0.9639–1.0741× | 0.25× | — |
| Holdout | `hold.subn.callable` | Rust engine | 0.0218× | 0.0213–0.0222× | 2.53× | SLOWER |
| Holdout | `hold.bytes.tokens` | Python engine | 0.0097× | 0.0096–0.0098× | 8.71× | SLOWER |
| Holdout | `hold.bytes.tokens` | Native C engine | 1.9854× | 1.9646–2.0055× | 0.18× | FASTER |
| Holdout | `hold.bytes.tokens` | Rust engine | 0.0079× | 0.0078–0.0080× | 2.92× | SLOWER |
| Holdout | `hold.unicode.words` | Python engine | 0.0092× | 0.0086–0.0101× | 6.63× | SLOWER |
| Holdout | `hold.unicode.words` | Native C engine | 1.7179× | 1.5899–1.8903× | 0.20× | FASTER |
| Holdout | `hold.unicode.words` | Rust engine | 0.0122× | 0.0114–0.0131× | 2.67× | SLOWER |
| Holdout | `hold.cold.compile-search` | Python engine | 0.4822× | 0.4698–0.4935× | 5.95× | SLOWER |
| Holdout | `hold.cold.compile-search` | Native C engine | 0.7913× | 0.7801–0.8027× | 1.55× | SLOWER |
| Holdout | `hold.cold.compile-search` | Rust engine | 0.7329× | 0.7191–0.7475× | 1.93× | SLOWER |
| Holdout | `hold.module.warm` | Python engine | 0.0192× | 0.0190–0.0194× | 7.12× | SLOWER |
| Holdout | `hold.module.warm` | Native C engine | 1.0645× | 0.9820–1.1211× | 0.07× | — |
| Holdout | `hold.module.warm` | Rust engine | 0.0308× | 0.0305–0.0311× | 3.38× | SLOWER |
| Holdout | `hold.empty.finditer` | Python engine | 0.0088× | 0.0085–0.0091× | 8.52× | SLOWER |
| Holdout | `hold.empty.finditer` | Native C engine | 0.6400× | 0.6126–0.6677× | 0.61× | SLOWER |
| Holdout | `hold.empty.finditer` | Rust engine | 0.0203× | 0.0196–0.0211× | 1.62× | SLOWER |
| Holdout | `hold.backref.fullmatch` | Python engine | 0.0181× | 0.0178–0.0185× | 6.99× | SLOWER |
| Holdout | `hold.backref.fullmatch` | Native C engine | 1.0840× | 1.0688–1.1021× | 0.08× | FASTER |
| Holdout | `hold.backref.fullmatch` | Rust engine | 0.0188× | 0.0185–0.0191× | 3.04× | SLOWER |
| Holdout | `hold.conditional.match` | Python engine | 0.0192× | 0.0186–0.0198× | 6.78× | SLOWER |
| Holdout | `hold.conditional.match` | Native C engine | 1.2151× | 1.1921–1.2396× | 0.08× | FASTER |
| Holdout | `hold.conditional.match` | Rust engine | 0.0191× | 0.0187–0.0196× | 2.94× | SLOWER |
| Holdout | `hold.atomic.search` | Python engine | 0.0107× | 0.0106–0.0108× | 6.53× | SLOWER |
| Holdout | `hold.atomic.search` | Native C engine | 1.3078× | 1.2076–1.3749× | 0.07× | FASTER |
| Holdout | `hold.atomic.search` | Rust engine | 0.0222× | 0.0219–0.0224× | 3.13× | SLOWER |
| Holdout | `hold.byteslike.findall` | Python engine | 0.0112× | 0.0108–0.0116× | 7.39× | SLOWER |
| Holdout | `hold.byteslike.findall` | Native C engine | 2.0667× | 2.0389–2.1049× | 0.18× | FASTER |
| Holdout | `hold.byteslike.findall` | Rust engine | 0.0084× | 0.0082–0.0086× | 2.83× | SLOWER |
| Holdout | `hold.unicode-name.search` | Python engine | 0.0130× | 0.0128–0.0132× | 4.69× | SLOWER |
| Holdout | `hold.unicode-name.search` | Native C engine | 1.3192× | 1.2411–1.3739× | 0.07× | FASTER |
| Holdout | `hold.unicode-name.search` | Rust engine | 0.0194× | 0.0191–0.0198× | 3.14× | SLOWER |
| Holdout | `hold.ignorecase.findall` | Python engine | 0.0075× | 0.0074–0.0076× | 4.86× | SLOWER |
| Holdout | `hold.ignorecase.findall` | Native C engine | 1.3265× | 1.2650–1.3709× | 0.16× | FASTER |
| Holdout | `hold.ignorecase.findall` | Rust engine | 0.0091× | 0.0089–0.0093× | 2.94× | SLOWER |
| Holdout | `hold.many.split` | Python engine | 0.0129× | 0.0124–0.0135× | 8.86× | SLOWER |
| Holdout | `hold.many.split` | Native C engine | 1.2802× | 1.2331–1.3423× | 0.20× | FASTER |
| Holdout | `hold.many.split` | Rust engine | 0.0047× | 0.0045–0.0050× | 2.86× | SLOWER |
| Holdout | `hold.escape.bytes` | Python engine | 0.9984× | 0.9724–1.0144× | 0.68× | — |
| Holdout | `hold.escape.bytes` | Native C engine | 1.0002× | 0.9815–1.0131× | 0.68× | — |
| Holdout | `hold.escape.bytes` | Rust engine | 0.9923× | 0.9695–1.0071× | 0.68× | — |
| Holdout | `hold.compile.only` | Python engine | 1.9611× | 1.9223–1.9939× | 0.54× | FASTER |
| Holdout | `hold.compile.only` | Native C engine | 1.3792× | 1.3606–1.3954× | 1.91× | FASTER |
| Holdout | `hold.compile.only` | Rust engine | 1.6735× | 1.6460–1.6979× | 0.60× | FASTER |
| Holdout | `hold.scanner.search` | Python engine | 0.0135× | 0.0127–0.0148× | 6.71× | SLOWER |
| Holdout | `hold.scanner.search` | Native C engine | 1.0643× | 0.9786–1.1686× | 0.36× | — |
| Holdout | `hold.scanner.search` | Rust engine | 0.0090× | 0.0084–0.0098× | 1.98× | SLOWER |
| Holdout | `hold.match.surface` | Python engine | 0.0216× | 0.0211–0.0223× | 12.79× | SLOWER |
| Holdout | `hold.match.surface` | Native C engine | 1.0537× | 0.9975–1.1040× | 0.32× | — |
| Holdout | `hold.match.surface` | Rust engine | 0.0420× | 0.0410–0.0434× | 3.25× | SLOWER |
| Practice | `cal.real.log` | Python engine | 0.0029× | 0.0028–0.0030× | 27.33× | SLOWER |
| Practice | `cal.real.log` | Native C engine | 0.8782× | 0.8537–0.9058× | 0.33× | — |
| Practice | `cal.real.log` | Rust engine | 0.0058× | 0.0056–0.0060× | 3.19× | SLOWER |
| Practice | `cal.real.url` | Python engine | 0.0067× | 0.0062–0.0074× | 26.38× | SLOWER |
| Practice | `cal.real.url` | Native C engine | 0.8758× | 0.7576–1.0066× | 0.11× | — |
| Practice | `cal.real.url` | Rust engine | 0.0127× | 0.0118–0.0140× | 3.49× | SLOWER |
| Practice | `cal.real.email` | Python engine | 0.0054× | 0.0053–0.0055× | 9.90× | SLOWER |
| Practice | `cal.real.email` | Native C engine | 0.6348× | 0.6262–0.6429× | 0.12× | SLOWER |
| Practice | `cal.real.email` | Rust engine | 0.0061× | 0.0060–0.0062× | 3.85× | SLOWER |
| Practice | `cal.real.datetime` | Python engine | 0.0078× | 0.0075–0.0082× | 23.68× | SLOWER |
| Practice | `cal.real.datetime` | Native C engine | 0.9928× | 0.9398–1.0506× | 0.09× | — |
| Practice | `cal.real.datetime` | Rust engine | 0.0164× | 0.0159–0.0172× | 3.49× | SLOWER |
| Practice | `cal.real.version` | Python engine | 0.0107× | 0.0104–0.0110× | 22.95× | SLOWER |
| Practice | `cal.real.version` | Native C engine | 1.4213× | 1.3044–1.4908× | 0.00× | FASTER |
| Practice | `cal.real.version` | Rust engine | 0.0286× | 0.0283–0.0288× | 3.46× | SLOWER |
| Practice | `cal.real.uuid` | Python engine | 0.0063× | 0.0061–0.0064× | 18.66× | SLOWER |
| Practice | `cal.real.uuid` | Native C engine | 0.8058× | 0.7387–0.8500× | 0.07× | — |
| Practice | `cal.real.uuid` | Rust engine | 0.0132× | 0.0126–0.0137× | 3.96× | SLOWER |
| Practice | `cal.real.ip` | Python engine | 0.0080× | 0.0079–0.0081× | 29.12× | SLOWER |
| Practice | `cal.real.ip` | Native C engine | 0.9735× | 0.8777–1.0315× | 0.07× | — |
| Practice | `cal.real.ip` | Rust engine | 0.0259× | 0.0255–0.0263× | 3.02× | SLOWER |
| Practice | `cal.real.path` | Python engine | 0.0057× | 0.0057–0.0057× | 30.63× | SLOWER |
| Practice | `cal.real.path` | Native C engine | 0.8986× | 0.8694–0.9219× | 0.12× | — |
| Practice | `cal.real.path` | Rust engine | 0.0105× | 0.0104–0.0105× | 3.60× | SLOWER |
| Practice | `cal.real.config` | Python engine | 0.0084× | 0.0081–0.0088× | 16.04× | SLOWER |
| Practice | `cal.real.config` | Native C engine | 1.0404× | 1.0035–1.0834× | 0.35× | FASTER |
| Practice | `cal.real.config` | Rust engine | 0.0168× | 0.0164–0.0174× | 2.32× | SLOWER |
| Practice | `cal.real.comments` | Python engine | 0.0063× | 0.0060–0.0069× | 11.73× | SLOWER |
| Practice | `cal.real.comments` | Native C engine | 0.7031× | 0.6686–0.7699× | 0.14× | SLOWER |
| Practice | `cal.real.comments` | Rust engine | 0.0039× | 0.0037–0.0043× | 3.74× | SLOWER |
| Practice | `cal.real.whitespace` | Python engine | 0.0064× | 0.0063–0.0065× | 8.36× | SLOWER |
| Practice | `cal.real.whitespace` | Native C engine | 1.3341× | 1.3236–1.3438× | 0.14× | FASTER |
| Practice | `cal.real.whitespace` | Rust engine | 0.0073× | 0.0072–0.0073× | 2.79× | SLOWER |
| Practice | `cal.real.lines` | Python engine | 0.0094× | 0.0091–0.0099× | 14.09× | SLOWER |
| Practice | `cal.real.lines` | Native C engine | 1.5805× | 1.4471–1.7076× | 0.15× | FASTER |
| Practice | `cal.real.lines` | Rust engine | 0.0091× | 0.0087–0.0096× | 2.83× | SLOWER |
| Practice | `cal.real.markup` | Python engine | 0.0043× | 0.0042–0.0043× | 13.23× | SLOWER |
| Practice | `cal.real.markup` | Native C engine | 0.5511× | 0.5170–0.5716× | 0.10× | SLOWER |
| Practice | `cal.real.markup` | Rust engine | 0.0035× | 0.0035–0.0035× | 4.19× | SLOWER |
| Practice | `cal.real.quotes` | Python engine | 0.0041× | 0.0040–0.0041× | 18.83× | SLOWER |
| Practice | `cal.real.quotes` | Native C engine | 0.6469× | 0.6402–0.6538× | 0.10× | SLOWER |
| Practice | `cal.real.quotes` | Rust engine | 0.0071× | 0.0070–0.0071× | 3.83× | SLOWER |
| Practice | `cal.real.csv` | Python engine | 0.0047× | 0.0046–0.0047× | 19.83× | SLOWER |
| Practice | `cal.real.csv` | Native C engine | 0.3828× | 0.3770–0.3881× | 0.32× | SLOWER |
| Practice | `cal.real.csv` | Rust engine | 0.0102× | 0.0101–0.0104× | 2.97× | SLOWER |
| Practice | `cal.branch.prefix` | Python engine | 0.0096× | 0.0093–0.0099× | 12.65× | SLOWER |
| Practice | `cal.branch.prefix` | Native C engine | 0.8022× | 0.7437–0.8498× | 0.07× | — |
| Practice | `cal.branch.prefix` | Rust engine | 0.0134× | 0.0129–0.0139× | 3.37× | SLOWER |
| Practice | `cal.branch.miss` | Python engine | 0.0009× | 0.0009–0.0009× | 83.64× | SLOWER |
| Practice | `cal.branch.miss` | Native C engine | 0.4665× | 0.4565–0.4736× | 0.00× | SLOWER |
| Practice | `cal.branch.miss` | Rust engine | 0.0126× | 0.0125–0.0127× | 4.25× | SLOWER |
| Practice | `cal.repeat.nested` | Python engine | 0.0097× | 0.0089–0.0108× | 15.24× | SLOWER |
| Practice | `cal.repeat.nested` | Native C engine | 1.0987× | 0.9800–1.2462× | 0.64× | — |
| Practice | `cal.repeat.nested` | Rust engine | 0.0228× | 0.0207–0.0255× | 1.57× | SLOWER |
| Practice | `cal.lines.records` | Python engine | 0.0081× | 0.0078–0.0083× | 14.74× | SLOWER |
| Practice | `cal.lines.records` | Native C engine | 1.0245× | 0.9914–1.0576× | 0.36× | — |
| Practice | `cal.lines.records` | Rust engine | 0.0071× | 0.0069–0.0074× | 2.56× | SLOWER |
| Practice | `cal.block.dotall` | Python engine | 0.0069× | 0.0064–0.0075× | 17.13× | SLOWER |
| Practice | `cal.block.dotall` | Native C engine | 0.7015× | 0.6513–0.7691× | 0.08× | SLOWER |
| Practice | `cal.block.dotall` | Rust engine | 0.0136× | 0.0127–0.0149× | 3.97× | SLOWER |
| Practice | `cal.pattern.verbose` | Python engine | 0.0041× | 0.0038–0.0044× | 14.85× | SLOWER |
| Practice | `cal.pattern.verbose` | Native C engine | 0.6107× | 0.5302–0.6938× | 0.09× | SLOWER |
| Practice | `cal.pattern.verbose` | Rust engine | 0.0194× | 0.0176–0.0213× | 3.43× | SLOWER |
| Practice | `cal.mode.ascii` | Python engine | 0.0054× | 0.0053–0.0055× | 7.27× | SLOWER |
| Practice | `cal.mode.ascii` | Native C engine | 1.0322× | 1.0215–1.0422× | 0.13× | FASTER |
| Practice | `cal.mode.ascii` | Rust engine | 0.0094× | 0.0093–0.0094× | 3.04× | SLOWER |
| Practice | `cal.mode.casefold` | Python engine | 0.0078× | 0.0077–0.0080× | 5.52× | SLOWER |
| Practice | `cal.mode.casefold` | Native C engine | 1.2936× | 1.2308–1.3372× | 0.20× | FASTER |
| Practice | `cal.mode.casefold` | Rust engine | 0.0085× | 0.0083–0.0087× | 2.90× | SLOWER |
| Practice | `cal.mode.astral` | Python engine | 0.0096× | 0.0092–0.0104× | 7.05× | SLOWER |
| Practice | `cal.mode.astral` | Native C engine | 1.5642× | 1.4029–1.7293× | 0.25× | FASTER |
| Practice | `cal.mode.astral` | Rust engine | 0.0094× | 0.0090–0.0102× | 2.76× | SLOWER |
| Practice | `cal.look.negative-ahead` | Python engine | 0.0038× | 0.0035–0.0042× | 15.69× | SLOWER |
| Practice | `cal.look.negative-ahead` | Native C engine | 0.4313× | 0.3863–0.4714× | 0.53× | SLOWER |
| Practice | `cal.look.negative-ahead` | Rust engine | 0.0069× | 0.0063–0.0074× | 3.46× | SLOWER |
| Practice | `cal.look.negative-behind` | Python engine | 0.0065× | 0.0061–0.0071× | 12.65× | SLOWER |
| Practice | `cal.look.negative-behind` | Native C engine | 1.0763× | 0.9943–1.1758× | 0.10× | — |
| Practice | `cal.look.negative-behind` | Rust engine | 0.0101× | 0.0097–0.0107× | 3.19× | SLOWER |
| Practice | `cal.bytes.replace` | Python engine | 0.0165× | 0.0163–0.0168× | 9.71× | SLOWER |
| Practice | `cal.bytes.replace` | Native C engine | 1.0403× | 1.0071–1.0715× | 0.95× | FASTER |
| Practice | `cal.bytes.replace` | Rust engine | 0.0159× | 0.0157–0.0162× | 2.52× | SLOWER |
| Practice | `cal.bytes.scan` | Python engine | 0.0115× | 0.0114–0.0116× | 8.55× | SLOWER |
| Practice | `cal.bytes.scan` | Native C engine | 1.2698× | 1.2032–1.3136× | 0.38× | FASTER |
| Practice | `cal.bytes.scan` | Rust engine | 0.0093× | 0.0092–0.0094× | 1.87× | SLOWER |
| Practice | `cal.compile.complex` | Python engine | 1.7668× | 1.7497–1.7833× | 0.39× | FASTER |
| Practice | `cal.compile.complex` | Native C engine | 1.3819× | 1.3695–1.3937× | 1.64× | FASTER |
| Practice | `cal.compile.complex` | Rust engine | 1.7278× | 1.7117–1.7419× | 0.52× | FASTER |
| Practice | `cal.module.replace` | Python engine | 0.0208× | 0.0205–0.0211× | 10.12× | SLOWER |
| Practice | `cal.module.replace` | Native C engine | 1.1939× | 1.1589–1.2236× | 0.04× | FASTER |
| Practice | `cal.module.replace` | Rust engine | 0.0194× | 0.0190–0.0199× | 2.52× | SLOWER |
| Practice | `cal.zero.boundary` | Python engine | 0.0073× | 0.0072–0.0075× | 13.81× | SLOWER |
| Practice | `cal.zero.boundary` | Native C engine | 0.5313× | 0.5186–0.5422× | 0.62× | SLOWER |
| Practice | `cal.zero.boundary` | Rust engine | 0.0125× | 0.0122–0.0128× | 1.69× | SLOWER |
| Practice | `cal.dense.iter` | Python engine | 0.0157× | 0.0154–0.0159× | 4.92× | SLOWER |
| Practice | `cal.dense.iter` | Native C engine | 1.2907× | 1.2686–1.3192× | 0.51× | FASTER |
| Practice | `cal.dense.iter` | Rust engine | 0.0080× | 0.0079–0.0081× | 1.49× | SLOWER |
| Practice | `cal.capture.optional` | Python engine | 0.0100× | 0.0098–0.0101× | 14.26× | SLOWER |
| Practice | `cal.capture.optional` | Native C engine | 1.0856× | 1.0759–1.0964× | 0.18× | FASTER |
| Practice | `cal.capture.optional` | Rust engine | 0.0086× | 0.0085–0.0087× | 2.79× | SLOWER |
| Practice | `cal.split.limited` | Python engine | 0.0067× | 0.0066–0.0068× | 7.47× | SLOWER |
| Practice | `cal.split.limited` | Native C engine | 1.1037× | 0.9986–1.1727× | 0.19× | — |
| Practice | `cal.split.limited` | Rust engine | 0.0078× | 0.0077–0.0079× | 2.82× | SLOWER |
| Practice | `cal.replace.limited` | Python engine | 0.0129× | 0.0127–0.0132× | 6.04× | SLOWER |
| Practice | `cal.replace.limited` | Native C engine | 1.2729× | 1.2505–1.2973× | 0.15× | FASTER |
| Practice | `cal.replace.limited` | Rust engine | 0.0094× | 0.0093–0.0096× | 2.90× | SLOWER |
| Practice | `cal.bytes.view-long` | Python engine | 0.0067× | 0.0064–0.0072× | 48.64× | SLOWER |
| Practice | `cal.bytes.view-long` | Native C engine | 1.3137× | 1.2800–1.3428× | 0.60× | FASTER |
| Practice | `cal.bytes.view-long` | Rust engine | 0.0010× | 0.0009–0.0010× | 5.61× | SLOWER |
| Practice | `cal.window.search` | Python engine | 0.0191× | 0.0187–0.0194× | 4.40× | SLOWER |
| Practice | `cal.window.search` | Native C engine | 0.9488× | 0.9359–0.9628× | 0.18× | — |
| Practice | `cal.window.search` | Rust engine | 0.0155× | 0.0151–0.0159× | 3.30× | SLOWER |
| Practice | `cal.window.findall` | Python engine | 0.0171× | 0.0163–0.0182× | 4.02× | SLOWER |
| Practice | `cal.window.findall` | Native C engine | 1.0513× | 1.0193–1.0944× | 0.23× | FASTER |
| Practice | `cal.window.findall` | Rust engine | 0.0077× | 0.0074–0.0081× | 3.01× | SLOWER |
| Practice | `cal.window.scanner` | Python engine | 0.0175× | 0.0173–0.0177× | 4.46× | SLOWER |
| Practice | `cal.window.scanner` | Native C engine | 1.0327× | 1.0204–1.0452× | 0.30× | FASTER |
| Practice | `cal.window.scanner` | Rust engine | 0.0092× | 0.0091–0.0093× | 2.20× | SLOWER |
| Practice | `cal.window.match` | Python engine | 0.0367× | 0.0358–0.0376× | 3.55× | SLOWER |
| Practice | `cal.window.match` | Native C engine | 1.0087× | 0.9848–1.0340× | 0.18× | — |
| Practice | `cal.window.match` | Rust engine | 0.0186× | 0.0180–0.0191× | 2.45× | SLOWER |
| Practice | `cal.literal.replace` | Python engine | 0.0059× | 0.0057–0.0060× | 41.75× | SLOWER |
| Practice | `cal.literal.replace` | Native C engine | 1.2926× | 1.2702–1.3216× | 0.53× | FASTER |
| Practice | `cal.literal.replace` | Rust engine | 0.0051× | 0.0049–0.0052× | 10.40× | SLOWER |
| Practice | `cal.template.repeat` | Python engine | 0.0183× | 0.0181–0.0185× | 6.29× | SLOWER |
| Practice | `cal.template.repeat` | Native C engine | 1.4117× | 1.3962–1.4286× | 0.15× | FASTER |
| Practice | `cal.template.repeat` | Rust engine | 0.0127× | 0.0126–0.0129× | 2.29× | SLOWER |
| Practice | `cal.match.miss` | Python engine | 0.0272× | 0.0268–0.0277× | 5.02× | SLOWER |
| Practice | `cal.match.miss` | Native C engine | 1.1202× | 1.1051–1.1376× | 0.00× | FASTER |
| Practice | `cal.match.miss` | Rust engine | 0.0076× | 0.0074–0.0078× | 4.00× | SLOWER |
| Practice | `cal.fullmatch.miss` | Python engine | 0.0166× | 0.0159–0.0171× | 11.09× | SLOWER |
| Practice | `cal.fullmatch.miss` | Native C engine | 1.2962× | 1.2445–1.3343× | 0.00× | FASTER |
| Practice | `cal.fullmatch.miss` | Rust engine | 0.0216× | 0.0214–0.0219× | 3.32× | SLOWER |
| Holdout | `hold.real.log` | Python engine | 0.0027× | 0.0026–0.0029× | 36.41× | SLOWER |
| Holdout | `hold.real.log` | Native C engine | 0.8332× | 0.7999–0.8698× | 0.33× | — |
| Holdout | `hold.real.log` | Rust engine | 0.0054× | 0.0052–0.0057× | 3.23× | SLOWER |
| Holdout | `hold.real.url` | Python engine | 0.0053× | 0.0052–0.0055× | 26.93× | SLOWER |
| Holdout | `hold.real.url` | Native C engine | 0.7844× | 0.7704–0.8003× | 0.11× | SLOWER |
| Holdout | `hold.real.url` | Rust engine | 0.0104× | 0.0101–0.0106× | 3.79× | SLOWER |
| Holdout | `hold.real.email` | Python engine | 0.0041× | 0.0041–0.0042× | 12.09× | SLOWER |
| Holdout | `hold.real.email` | Native C engine | 0.8127× | 0.8077–0.8184× | 0.12× | — |
| Holdout | `hold.real.email` | Rust engine | 0.0068× | 0.0067–0.0068× | 3.88× | SLOWER |
| Holdout | `hold.real.datetime` | Python engine | 0.0073× | 0.0072–0.0073× | 27.33× | SLOWER |
| Holdout | `hold.real.datetime` | Native C engine | 1.0007× | 0.9578–1.0305× | 0.09× | — |
| Holdout | `hold.real.datetime` | Rust engine | 0.0168× | 0.0167–0.0169× | 3.42× | SLOWER |
| Holdout | `hold.real.version` | Python engine | 0.0093× | 0.0089–0.0099× | 23.70× | SLOWER |
| Holdout | `hold.real.version` | Native C engine | 1.0952× | 1.0544–1.1683× | 0.06× | FASTER |
| Holdout | `hold.real.version` | Rust engine | 0.0204× | 0.0192–0.0222× | 3.01× | SLOWER |
| Holdout | `hold.real.uuid` | Python engine | 0.0063× | 0.0061–0.0067× | 18.05× | SLOWER |
| Holdout | `hold.real.uuid` | Native C engine | 0.8215× | 0.7879–0.8706× | 0.07× | — |
| Holdout | `hold.real.uuid` | Rust engine | 0.0135× | 0.0130–0.0143× | 3.95× | SLOWER |
| Holdout | `hold.real.ip` | Python engine | 0.0088× | 0.0087–0.0089× | 30.05× | SLOWER |
| Holdout | `hold.real.ip` | Native C engine | 1.0872× | 1.0734–1.1020× | 0.07× | FASTER |
| Holdout | `hold.real.ip` | Rust engine | 0.0212× | 0.0210–0.0215× | 3.02× | SLOWER |
| Holdout | `hold.real.path` | Python engine | 0.0056× | 0.0055–0.0056× | 26.39× | SLOWER |
| Holdout | `hold.real.path` | Native C engine | 0.8369× | 0.8288–0.8455× | 0.12× | — |
| Holdout | `hold.real.path` | Rust engine | 0.0095× | 0.0094–0.0095× | 3.84× | SLOWER |
| Holdout | `hold.real.config` | Python engine | 0.0084× | 0.0082–0.0086× | 18.02× | SLOWER |
| Holdout | `hold.real.config` | Native C engine | 1.0164× | 0.9798–1.0491× | 0.35× | — |
| Holdout | `hold.real.config` | Rust engine | 0.0148× | 0.0145–0.0152× | 2.32× | SLOWER |
| Holdout | `hold.real.comments` | Python engine | 0.0047× | 0.0046–0.0047× | 16.97× | SLOWER |
| Holdout | `hold.real.comments` | Native C engine | 0.6792× | 0.6704–0.6889× | 0.14× | SLOWER |
| Holdout | `hold.real.comments` | Rust engine | 0.0032× | 0.0032–0.0032× | 4.05× | SLOWER |
| Holdout | `hold.real.whitespace` | Python engine | 0.0069× | 0.0068–0.0070× | 8.45× | SLOWER |
| Holdout | `hold.real.whitespace` | Native C engine | 1.3334× | 1.2035–1.4140× | 0.14× | FASTER |
| Holdout | `hold.real.whitespace` | Rust engine | 0.0072× | 0.0071–0.0072× | 2.74× | SLOWER |
| Holdout | `hold.real.lines` | Python engine | 0.0096× | 0.0093–0.0098× | 13.22× | SLOWER |
| Holdout | `hold.real.lines` | Native C engine | 1.5336× | 1.3855–1.6286× | 0.14× | FASTER |
| Holdout | `hold.real.lines` | Rust engine | 0.0094× | 0.0092–0.0095× | 2.82× | SLOWER |
| Holdout | `hold.real.markup` | Python engine | 0.0046× | 0.0045–0.0047× | 14.16× | SLOWER |
| Holdout | `hold.real.markup` | Native C engine | 0.6047× | 0.5982–0.6115× | 0.13× | SLOWER |
| Holdout | `hold.real.markup` | Rust engine | 0.0032× | 0.0031–0.0033× | 4.34× | SLOWER |
| Holdout | `hold.real.quotes` | Python engine | 0.0041× | 0.0040–0.0041× | 18.87× | SLOWER |
| Holdout | `hold.real.quotes` | Native C engine | 0.6801× | 0.6736–0.6866× | 0.10× | SLOWER |
| Holdout | `hold.real.quotes` | Rust engine | 0.0072× | 0.0071–0.0073× | 3.58× | SLOWER |
| Holdout | `hold.real.csv` | Python engine | 0.0042× | 0.0040–0.0044× | 18.08× | SLOWER |
| Holdout | `hold.real.csv` | Native C engine | 0.3437× | 0.3317–0.3594× | 0.32× | SLOWER |
| Holdout | `hold.real.csv` | Rust engine | 0.0097× | 0.0094–0.0102× | 3.21× | SLOWER |
| Holdout | `hold.branch.prefix` | Python engine | 0.0101× | 0.0099–0.0102× | 11.86× | SLOWER |
| Holdout | `hold.branch.prefix` | Native C engine | 0.8524× | 0.8362–0.8690× | 0.07× | — |
| Holdout | `hold.branch.prefix` | Rust engine | 0.0136× | 0.0133–0.0139× | 3.36× | SLOWER |
| Holdout | `hold.branch.miss` | Python engine | 0.0008× | 0.0008–0.0008× | 80.13× | SLOWER |
| Holdout | `hold.branch.miss` | Native C engine | 0.7477× | 0.7283–0.7788× | 0.00× | SLOWER |
| Holdout | `hold.branch.miss` | Rust engine | 0.0112× | 0.0109–0.0117× | 4.57× | SLOWER |
| Holdout | `hold.repeat.nested` | Python engine | 0.0103× | 0.0099–0.0110× | 15.24× | SLOWER |
| Holdout | `hold.repeat.nested` | Native C engine | 1.0585× | 1.0173–1.1314× | 0.64× | FASTER |
| Holdout | `hold.repeat.nested` | Rust engine | 0.0230× | 0.0222–0.0246× | 1.57× | SLOWER |
| Holdout | `hold.lines.records` | Python engine | 0.0084× | 0.0083–0.0085× | 14.74× | SLOWER |
| Holdout | `hold.lines.records` | Native C engine | 1.0193× | 0.9984–1.0382× | 0.36× | — |
| Holdout | `hold.lines.records` | Rust engine | 0.0074× | 0.0073–0.0076× | 2.55× | SLOWER |
| Holdout | `hold.block.dotall` | Python engine | 0.0064× | 0.0061–0.0068× | 18.13× | SLOWER |
| Holdout | `hold.block.dotall` | Native C engine | 0.6641× | 0.6399–0.7090× | 0.08× | SLOWER |
| Holdout | `hold.block.dotall` | Rust engine | 0.0133× | 0.0129–0.0141× | 4.00× | SLOWER |
| Holdout | `hold.pattern.verbose` | Python engine | 0.0036× | 0.0036–0.0037× | 15.91× | SLOWER |
| Holdout | `hold.pattern.verbose` | Native C engine | 0.6107× | 0.5854–0.6329× | 0.09× | SLOWER |
| Holdout | `hold.pattern.verbose` | Rust engine | 0.0253× | 0.0249–0.0258× | 3.45× | SLOWER |
| Holdout | `hold.mode.ascii` | Python engine | 0.0053× | 0.0049–0.0058× | 7.82× | SLOWER |
| Holdout | `hold.mode.ascii` | Native C engine | 1.0137× | 0.9105–1.1043× | 0.21× | — |
| Holdout | `hold.mode.ascii` | Rust engine | 0.0076× | 0.0069–0.0083× | 3.02× | SLOWER |
| Holdout | `hold.mode.casefold` | Python engine | 0.0081× | 0.0073–0.0091× | 5.44× | SLOWER |
| Holdout | `hold.mode.casefold` | Native C engine | 1.3875× | 1.2154–1.5911× | 0.18× | FASTER |
| Holdout | `hold.mode.casefold` | Rust engine | 0.0107× | 0.0099–0.0118× | 2.93× | SLOWER |
| Holdout | `hold.mode.astral` | Python engine | 0.0090× | 0.0089–0.0091× | 7.06× | SLOWER |
| Holdout | `hold.mode.astral` | Native C engine | 1.5380× | 1.5226–1.5539× | 0.25× | FASTER |
| Holdout | `hold.mode.astral` | Rust engine | 0.0091× | 0.0090–0.0091× | 2.77× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Python engine | 0.0036× | 0.0034–0.0038× | 16.30× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Native C engine | 0.4269× | 0.4066–0.4568× | 0.53× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Rust engine | 0.0072× | 0.0070–0.0077× | 3.47× | SLOWER |
| Holdout | `hold.look.negative-behind` | Python engine | 0.0067× | 0.0065–0.0072× | 12.65× | SLOWER |
| Holdout | `hold.look.negative-behind` | Native C engine | 1.0668× | 0.9766–1.1688× | 0.10× | — |
| Holdout | `hold.look.negative-behind` | Rust engine | 0.0102× | 0.0098–0.0110× | 3.19× | SLOWER |
| Holdout | `hold.bytes.replace` | Python engine | 0.0163× | 0.0161–0.0165× | 9.71× | SLOWER |
| Holdout | `hold.bytes.replace` | Native C engine | 1.1001× | 1.0700–1.1361× | 0.93× | FASTER |
| Holdout | `hold.bytes.replace` | Rust engine | 0.0161× | 0.0158–0.0164× | 2.52× | SLOWER |
| Holdout | `hold.bytes.scan` | Python engine | 0.0116× | 0.0112–0.0123× | 8.55× | SLOWER |
| Holdout | `hold.bytes.scan` | Native C engine | 1.2396× | 1.1270–1.3356× | 0.38× | FASTER |
| Holdout | `hold.bytes.scan` | Rust engine | 0.0093× | 0.0089–0.0098× | 1.87× | SLOWER |
| Holdout | `hold.compile.complex` | Python engine | 1.8507× | 1.8333–1.8693× | 0.37× | FASTER |
| Holdout | `hold.compile.complex` | Native C engine | 1.4260× | 1.4159–1.4364× | 1.67× | FASTER |
| Holdout | `hold.compile.complex` | Rust engine | 1.5684× | 1.5511–1.5861× | 0.55× | FASTER |
| Holdout | `hold.module.replace` | Python engine | 0.0214× | 0.0209–0.0222× | 10.12× | SLOWER |
| Holdout | `hold.module.replace` | Native C engine | 1.2349× | 1.2065–1.2829× | 0.04× | FASTER |
| Holdout | `hold.module.replace` | Rust engine | 0.0197× | 0.0191–0.0206× | 2.52× | SLOWER |
| Holdout | `hold.zero.boundary` | Python engine | 0.0078× | 0.0077–0.0079× | 8.20× | SLOWER |
| Holdout | `hold.zero.boundary` | Native C engine | 0.5188× | 0.4910–0.5460× | 0.62× | SLOWER |
| Holdout | `hold.zero.boundary` | Rust engine | 0.0134× | 0.0132–0.0137× | 1.67× | SLOWER |
| Holdout | `hold.dense.iter` | Python engine | 0.0158× | 0.0153–0.0165× | 4.92× | SLOWER |
| Holdout | `hold.dense.iter` | Native C engine | 1.3485× | 1.2808–1.4143× | 0.51× | FASTER |
| Holdout | `hold.dense.iter` | Rust engine | 0.0079× | 0.0077–0.0083× | 1.50× | SLOWER |
| Holdout | `hold.capture.optional` | Python engine | 0.0097× | 0.0095–0.0099× | 14.26× | SLOWER |
| Holdout | `hold.capture.optional` | Native C engine | 0.9774× | 0.8957–1.0291× | 0.18× | — |
| Holdout | `hold.capture.optional` | Rust engine | 0.0082× | 0.0080–0.0083× | 2.79× | SLOWER |
| Holdout | `hold.split.limited` | Python engine | 0.0061× | 0.0061–0.0062× | 7.46× | SLOWER |
| Holdout | `hold.split.limited` | Native C engine | 1.0458× | 0.9630–1.0941× | 0.19× | — |
| Holdout | `hold.split.limited` | Rust engine | 0.0071× | 0.0070–0.0071× | 2.83× | SLOWER |
| Holdout | `hold.replace.limited` | Python engine | 0.0132× | 0.0124–0.0143× | 6.04× | SLOWER |
| Holdout | `hold.replace.limited` | Native C engine | 1.1807× | 1.0878–1.3024× | 0.15× | FASTER |
| Holdout | `hold.replace.limited` | Rust engine | 0.0091× | 0.0086–0.0099× | 2.90× | SLOWER |
| Holdout | `hold.bytes.view-long` | Python engine | 0.0067× | 0.0066–0.0069× | 48.64× | SLOWER |
| Holdout | `hold.bytes.view-long` | Native C engine | 1.3564× | 1.3127–1.3976× | 0.60× | FASTER |
| Holdout | `hold.bytes.view-long` | Rust engine | 0.0010× | 0.0009–0.0010× | 5.61× | SLOWER |
| Holdout | `hold.window.search` | Python engine | 0.0192× | 0.0179–0.0211× | 4.40× | SLOWER |
| Holdout | `hold.window.search` | Native C engine | 0.9640× | 0.9155–1.0471× | 0.18× | — |
| Holdout | `hold.window.search` | Rust engine | 0.0154× | 0.0146–0.0167× | 3.32× | SLOWER |
| Holdout | `hold.window.findall` | Python engine | 0.0179× | 0.0172–0.0185× | 4.03× | SLOWER |
| Holdout | `hold.window.findall` | Native C engine | 0.9943× | 0.9674–1.0223× | 0.22× | — |
| Holdout | `hold.window.findall` | Rust engine | 0.0075× | 0.0073–0.0077× | 2.86× | SLOWER |
| Holdout | `hold.window.scanner` | Python engine | 0.0174× | 0.0166–0.0183× | 4.46× | SLOWER |
| Holdout | `hold.window.scanner` | Native C engine | 1.0403× | 0.9672–1.1074× | 0.30× | — |
| Holdout | `hold.window.scanner` | Rust engine | 0.0095× | 0.0092–0.0099× | 2.20× | SLOWER |
| Holdout | `hold.window.match` | Python engine | 0.0328× | 0.0324–0.0330× | 3.55× | SLOWER |
| Holdout | `hold.window.match` | Native C engine | 0.9263× | 0.8501–0.9733× | 0.18× | — |
| Holdout | `hold.window.match` | Rust engine | 0.0177× | 0.0175–0.0178× | 2.46× | SLOWER |
| Holdout | `hold.literal.replace` | Python engine | 0.0063× | 0.0061–0.0064× | 38.88× | SLOWER |
| Holdout | `hold.literal.replace` | Native C engine | 1.2583× | 1.2395–1.2796× | 0.52× | FASTER |
| Holdout | `hold.literal.replace` | Rust engine | 0.0055× | 0.0053–0.0056× | 10.36× | SLOWER |
| Holdout | `hold.template.repeat` | Python engine | 0.0206× | 0.0193–0.0221× | 6.32× | SLOWER |
| Holdout | `hold.template.repeat` | Native C engine | 1.5688× | 1.4725–1.6890× | 0.14× | FASTER |
| Holdout | `hold.template.repeat` | Rust engine | 0.0154× | 0.0145–0.0165× | 2.28× | SLOWER |
| Holdout | `hold.match.miss` | Python engine | 0.0277× | 0.0273–0.0282× | 5.02× | SLOWER |
| Holdout | `hold.match.miss` | Native C engine | 1.1476× | 1.1340–1.1655× | 0.00× | FASTER |
| Holdout | `hold.match.miss` | Rust engine | 0.0074× | 0.0073–0.0075× | 4.20× | SLOWER |
| Holdout | `hold.fullmatch.miss` | Python engine | 0.0174× | 0.0172–0.0177× | 11.09× | SLOWER |
| Holdout | `hold.fullmatch.miss` | Native C engine | 1.3638× | 1.3493–1.3786× | 0.00× | FASTER |
| Holdout | `hold.fullmatch.miss` | Rust engine | 0.0226× | 0.0224–0.0229× | 3.31× | SLOWER |

## Large slowdowns

- Python engine: `cal.search.literal.hit` (0.007×), `cal.search.literal.miss` (0.002×), `cal.search.long-boundary` (0.000×), `cal.search.class-anchor` (0.011×), `cal.match.prefix` (0.023×), `cal.fullmatch.structured` (0.013×), `cal.search.look-capture` (0.008×), `cal.findall.tokens` (0.010×), `cal.finditer.groups` (0.013×), `cal.split.capture` (0.010×), `cal.sub.template` (0.017×), `cal.subn.callable` (0.023×), `cal.bytes.tokens` (0.008×), `cal.unicode.words` (0.006×), `cal.cold.compile-search` (0.290×), `cal.module.warm` (0.010×), `cal.empty.finditer` (0.010×), `cal.backref.fullmatch` (0.018×), `cal.conditional.match` (0.018×), `cal.atomic.search` (0.010×), `cal.byteslike.findall` (0.011×), `cal.unicode-name.search` (0.014×), `cal.ignorecase.findall` (0.007×), `cal.many.split` (0.012×), `cal.scanner.search` (0.013×), `cal.match.surface` (0.014×), `hold.search.literal.hit` (0.007×), `hold.search.literal.miss` (0.002×), `hold.search.long-boundary` (0.000×), `hold.search.class-anchor` (0.010×), `hold.match.prefix` (0.025×), `hold.fullmatch.structured` (0.011×), `hold.search.look-capture` (0.010×), `hold.findall.tokens` (0.011×), `hold.finditer.groups` (0.013×), `hold.split.capture` (0.010×), `hold.sub.template` (0.016×), `hold.subn.callable` (0.027×), `hold.bytes.tokens` (0.010×), `hold.unicode.words` (0.009×), `hold.cold.compile-search` (0.482×), `hold.module.warm` (0.019×), `hold.empty.finditer` (0.009×), `hold.backref.fullmatch` (0.018×), `hold.conditional.match` (0.019×), `hold.atomic.search` (0.011×), `hold.byteslike.findall` (0.011×), `hold.unicode-name.search` (0.013×), `hold.ignorecase.findall` (0.007×), `hold.many.split` (0.013×), `hold.scanner.search` (0.014×), `hold.match.surface` (0.022×), `cal.real.log` (0.003×), `cal.real.url` (0.007×), `cal.real.email` (0.005×), `cal.real.datetime` (0.008×), `cal.real.version` (0.011×), `cal.real.uuid` (0.006×), `cal.real.ip` (0.008×), `cal.real.path` (0.006×), `cal.real.config` (0.008×), `cal.real.comments` (0.006×), `cal.real.whitespace` (0.006×), `cal.real.lines` (0.009×), `cal.real.markup` (0.004×), `cal.real.quotes` (0.004×), `cal.real.csv` (0.005×), `cal.branch.prefix` (0.010×), `cal.branch.miss` (0.001×), `cal.repeat.nested` (0.010×), `cal.lines.records` (0.008×), `cal.block.dotall` (0.007×), `cal.pattern.verbose` (0.004×), `cal.mode.ascii` (0.005×), `cal.mode.casefold` (0.008×), `cal.mode.astral` (0.010×), `cal.look.negative-ahead` (0.004×), `cal.look.negative-behind` (0.007×), `cal.bytes.replace` (0.017×), `cal.bytes.scan` (0.011×), `cal.module.replace` (0.021×), `cal.zero.boundary` (0.007×), `cal.dense.iter` (0.016×), `cal.capture.optional` (0.010×), `cal.split.limited` (0.007×), `cal.replace.limited` (0.013×), `cal.bytes.view-long` (0.007×), `cal.window.search` (0.019×), `cal.window.findall` (0.017×), `cal.window.scanner` (0.017×), `cal.window.match` (0.037×), `cal.literal.replace` (0.006×), `cal.template.repeat` (0.018×), `cal.match.miss` (0.027×), `cal.fullmatch.miss` (0.017×), `hold.real.log` (0.003×), `hold.real.url` (0.005×), `hold.real.email` (0.004×), `hold.real.datetime` (0.007×), `hold.real.version` (0.009×), `hold.real.uuid` (0.006×), `hold.real.ip` (0.009×), `hold.real.path` (0.006×), `hold.real.config` (0.008×), `hold.real.comments` (0.005×), `hold.real.whitespace` (0.007×), `hold.real.lines` (0.010×), `hold.real.markup` (0.005×), `hold.real.quotes` (0.004×), `hold.real.csv` (0.004×), `hold.branch.prefix` (0.010×), `hold.branch.miss` (0.001×), `hold.repeat.nested` (0.010×), `hold.lines.records` (0.008×), `hold.block.dotall` (0.006×), `hold.pattern.verbose` (0.004×), `hold.mode.ascii` (0.005×), `hold.mode.casefold` (0.008×), `hold.mode.astral` (0.009×), `hold.look.negative-ahead` (0.004×), `hold.look.negative-behind` (0.007×), `hold.bytes.replace` (0.016×), `hold.bytes.scan` (0.012×), `hold.module.replace` (0.021×), `hold.zero.boundary` (0.008×), `hold.dense.iter` (0.016×), `hold.capture.optional` (0.010×), `hold.split.limited` (0.006×), `hold.replace.limited` (0.013×), `hold.bytes.view-long` (0.007×), `hold.window.search` (0.019×), `hold.window.findall` (0.018×), `hold.window.scanner` (0.017×), `hold.window.match` (0.033×), `hold.literal.replace` (0.006×), `hold.template.repeat` (0.021×), `hold.match.miss` (0.028×), `hold.fullmatch.miss` (0.017×).
- Rust engine: `cal.search.literal.hit` (0.009×), `cal.search.literal.miss` (0.006×), `cal.search.long-boundary` (0.001×), `cal.search.class-anchor` (0.015×), `cal.match.prefix` (0.015×), `cal.fullmatch.structured` (0.018×), `cal.search.look-capture` (0.016×), `cal.findall.tokens` (0.004×), `cal.finditer.groups` (0.010×), `cal.split.capture` (0.007×), `cal.sub.template` (0.015×), `cal.subn.callable` (0.019×), `cal.bytes.tokens` (0.006×), `cal.unicode.words` (0.010×), `cal.cold.compile-search` (0.701×), `cal.module.warm` (0.031×), `cal.empty.finditer` (0.022×), `cal.backref.fullmatch` (0.018×), `cal.conditional.match` (0.016×), `cal.atomic.search` (0.019×), `cal.byteslike.findall` (0.008×), `cal.unicode-name.search` (0.019×), `cal.ignorecase.findall` (0.008×), `cal.many.split` (0.004×), `cal.scanner.search` (0.009×), `cal.match.surface` (0.048×), `hold.search.literal.hit` (0.009×), `hold.search.literal.miss` (0.006×), `hold.search.long-boundary` (0.001×), `hold.search.class-anchor` (0.014×), `hold.match.prefix` (0.016×), `hold.fullmatch.structured` (0.019×), `hold.search.look-capture` (0.017×), `hold.findall.tokens` (0.006×), `hold.finditer.groups` (0.009×), `hold.split.capture` (0.007×), `hold.sub.template` (0.015×), `hold.subn.callable` (0.022×), `hold.bytes.tokens` (0.008×), `hold.unicode.words` (0.012×), `hold.cold.compile-search` (0.733×), `hold.module.warm` (0.031×), `hold.empty.finditer` (0.020×), `hold.backref.fullmatch` (0.019×), `hold.conditional.match` (0.019×), `hold.atomic.search` (0.022×), `hold.byteslike.findall` (0.008×), `hold.unicode-name.search` (0.019×), `hold.ignorecase.findall` (0.009×), `hold.many.split` (0.005×), `hold.scanner.search` (0.009×), `hold.match.surface` (0.042×), `cal.real.log` (0.006×), `cal.real.url` (0.013×), `cal.real.email` (0.006×), `cal.real.datetime` (0.016×), `cal.real.version` (0.029×), `cal.real.uuid` (0.013×), `cal.real.ip` (0.026×), `cal.real.path` (0.010×), `cal.real.config` (0.017×), `cal.real.comments` (0.004×), `cal.real.whitespace` (0.007×), `cal.real.lines` (0.009×), `cal.real.markup` (0.004×), `cal.real.quotes` (0.007×), `cal.real.csv` (0.010×), `cal.branch.prefix` (0.013×), `cal.branch.miss` (0.013×), `cal.repeat.nested` (0.023×), `cal.lines.records` (0.007×), `cal.block.dotall` (0.014×), `cal.pattern.verbose` (0.019×), `cal.mode.ascii` (0.009×), `cal.mode.casefold` (0.009×), `cal.mode.astral` (0.009×), `cal.look.negative-ahead` (0.007×), `cal.look.negative-behind` (0.010×), `cal.bytes.replace` (0.016×), `cal.bytes.scan` (0.009×), `cal.module.replace` (0.019×), `cal.zero.boundary` (0.013×), `cal.dense.iter` (0.008×), `cal.capture.optional` (0.009×), `cal.split.limited` (0.008×), `cal.replace.limited` (0.009×), `cal.bytes.view-long` (0.001×), `cal.window.search` (0.016×), `cal.window.findall` (0.008×), `cal.window.scanner` (0.009×), `cal.window.match` (0.019×), `cal.literal.replace` (0.005×), `cal.template.repeat` (0.013×), `cal.match.miss` (0.008×), `cal.fullmatch.miss` (0.022×), `hold.real.log` (0.005×), `hold.real.url` (0.010×), `hold.real.email` (0.007×), `hold.real.datetime` (0.017×), `hold.real.version` (0.020×), `hold.real.uuid` (0.013×), `hold.real.ip` (0.021×), `hold.real.path` (0.009×), `hold.real.config` (0.015×), `hold.real.comments` (0.003×), `hold.real.whitespace` (0.007×), `hold.real.lines` (0.009×), `hold.real.markup` (0.003×), `hold.real.quotes` (0.007×), `hold.real.csv` (0.010×), `hold.branch.prefix` (0.014×), `hold.branch.miss` (0.011×), `hold.repeat.nested` (0.023×), `hold.lines.records` (0.007×), `hold.block.dotall` (0.013×), `hold.pattern.verbose` (0.025×), `hold.mode.ascii` (0.008×), `hold.mode.casefold` (0.011×), `hold.mode.astral` (0.009×), `hold.look.negative-ahead` (0.007×), `hold.look.negative-behind` (0.010×), `hold.bytes.replace` (0.016×), `hold.bytes.scan` (0.009×), `hold.module.replace` (0.020×), `hold.zero.boundary` (0.013×), `hold.dense.iter` (0.008×), `hold.capture.optional` (0.008×), `hold.split.limited` (0.007×), `hold.replace.limited` (0.009×), `hold.bytes.view-long` (0.001×), `hold.window.search` (0.015×), `hold.window.findall` (0.008×), `hold.window.scanner` (0.010×), `hold.window.match` (0.018×), `hold.literal.replace` (0.005×), `hold.template.repeat` (0.015×), `hold.match.miss` (0.007×), `hold.fullmatch.miss` (0.023×).
- Native C engine: `cal.cold.compile-search` (0.742×), `cal.empty.finditer` (0.678×), `hold.cold.compile-search` (0.791×), `hold.empty.finditer` (0.640×), `cal.real.email` (0.635×), `cal.real.comments` (0.703×), `cal.real.markup` (0.551×), `cal.real.quotes` (0.647×), `cal.real.csv` (0.383×), `cal.branch.miss` (0.467×), `cal.block.dotall` (0.701×), `cal.pattern.verbose` (0.611×), `cal.look.negative-ahead` (0.431×), `cal.zero.boundary` (0.531×), `hold.real.url` (0.784×), `hold.real.comments` (0.679×), `hold.real.markup` (0.605×), `hold.real.quotes` (0.680×), `hold.real.csv` (0.344×), `hold.branch.miss` (0.748×), `hold.block.dotall` (0.664×), `hold.pattern.verbose` (0.611×), `hold.look.negative-ahead` (0.427×), `hold.zero.boundary` (0.519×).

The Python engine performs matching work in Python, and the Rust engine repeatedly prepares data and crosses the Python/Rust boundary; both costs dominate short tasks. Native-C losses expose specific boundary and general-path costs:
- Empty matches and controlled branches use the general backtracking/iterator path and construct more match state.
- Everyday log, address, path, comment, markup, quote, and comma-separated-field tasks combine repeated classes, captures, or lookarounds; they take the general native backtracking path instead of its compact single-pass path.
- Searches across many alternative words still test the remaining branches when a possible prefix survives; the native one/two-character start filter removes impossible positions but does not build a full shared-prefix trie.
- Structured repeated paths, multi-line blocks, and readable formatted fields require general repeat/capture backtracking, which carries more state than the simple literal and single-character fast paths.
- Excluded-prefix and tagged-word searches evaluate a negative lookaround for each possible match, so the native executor repeats assertion work while scanning.
- Word/separator-position iteration and limited mixed-separator splits repeatedly use the general iterator or whitespace-backtracking path; each small match pays state and result-construction costs.

No loss is removed from the denominator or hidden from the charts.
