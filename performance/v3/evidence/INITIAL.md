# Broader performance: initial results

All 7488 raw timing rows, 432 engine/task results, and 329 large slowdowns are retained. Raw SHA-256: `da85b31715d0c460fb0e09a2357db147a72d9a3ec7765e99047d328cfdee99a2`.

## At a glance

The holdout tasks were kept separate from tuning. **1× means the same speed as Python `re`; higher is faster.** A result is clearly faster only when its measured range stays above 1×. A large slowdown means more than 20% slower.

| Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: | ---: |
| Native C engine | **0.8997×** | 0.8927–0.9068× | 30/72 | 25/72 |
| Rust engine | **0.0132×** | 0.0131–0.0133× | 2/72 | 70/72 |
| Python engine | **0.0115×** | 0.0115–0.0116× | 2/72 | 70/72 |

## Overall results

| Task set | Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |
| --- | --- | ---: | ---: | ---: | ---: |
| Practice | Python engine | 0.0114× | 0.0113–0.0114× | 2/72 | 70 |
| Practice | Native C engine | 0.8931× | 0.8866–0.8996× | 30/72 | 24 |
| Practice | Rust engine | 0.0132× | 0.0131–0.0133× | 2/72 | 70 |
| Holdout | Python engine | 0.0115× | 0.0115–0.0116× | 2/72 | 70 |
| Holdout | Native C engine | 0.8997× | 0.8927–0.9068× | 30/72 | 25 |
| Holdout | Rust engine | 0.0132× | 0.0131–0.0133× | 2/72 | 70 |
| All | Python engine | 0.0115× | 0.0114–0.0115× | 4/144 | 140 |
| All | Native C engine | 0.8964× | 0.8914–0.9013× | 60/144 | 49 |
| All | Rust engine | 0.0132× | 0.0132–0.0133× | 4/144 | 140 |

## Every task

`FASTER` means the measured range stays above 1×. `SLOWER` means more than 20% slower. Memory compares median traced Python memory with Python `re`.

| Task set | Task | Engine | Speed | Measured range | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Practice | `cal.search.literal.hit` | Python engine | 0.0076× | 0.0074–0.0078× | 102.00× | SLOWER |
| Practice | `cal.search.literal.hit` | Native C engine | 1.0225× | 0.9419–1.0970× | 0.73× | — |
| Practice | `cal.search.literal.hit` | Rust engine | 0.0087× | 0.0086–0.0089× | 34.03× | SLOWER |
| Practice | `cal.search.literal.miss` | Python engine | 0.0022× | 0.0020–0.0026× | 14408.00× | SLOWER |
| Practice | `cal.search.literal.miss` | Native C engine | 1.2483× | 1.1436–1.4146× | 0.00× | FASTER |
| Practice | `cal.search.literal.miss` | Rust engine | 0.0060× | 0.0054–0.0068× | 4375.00× | SLOWER |
| Practice | `cal.search.long-boundary` | Python engine | 0.0003× | 0.0003–0.0003× | 129.57× | SLOWER |
| Practice | `cal.search.long-boundary` | Native C engine | 12.3252× | 11.3122–13.7125× | 0.07× | FASTER |
| Practice | `cal.search.long-boundary` | Rust engine | 0.0009× | 0.0009–0.0010× | 140.03× | SLOWER |
| Practice | `cal.search.class-anchor` | Python engine | 0.0115× | 0.0109–0.0124× | 11.57× | SLOWER |
| Practice | `cal.search.class-anchor` | Native C engine | 1.1327× | 1.0766–1.2348× | 0.07× | FASTER |
| Practice | `cal.search.class-anchor` | Rust engine | 0.0147× | 0.0140–0.0158× | 3.36× | SLOWER |
| Practice | `cal.match.prefix` | Python engine | 0.0246× | 0.0237–0.0262× | 3.87× | SLOWER |
| Practice | `cal.match.prefix` | Native C engine | 1.0720× | 1.0364–1.1392× | 0.07× | FASTER |
| Practice | `cal.match.prefix` | Rust engine | 0.0154× | 0.0149–0.0164× | 2.89× | SLOWER |
| Practice | `cal.fullmatch.structured` | Python engine | 0.0128× | 0.0126–0.0130× | 12.07× | SLOWER |
| Practice | `cal.fullmatch.structured` | Native C engine | 0.9438× | 0.9329–0.9560× | 0.07× | — |
| Practice | `cal.fullmatch.structured` | Rust engine | 0.0180× | 0.0177–0.0183× | 3.04× | SLOWER |
| Practice | `cal.search.look-capture` | Python engine | 0.0076× | 0.0075–0.0077× | 17.28× | SLOWER |
| Practice | `cal.search.look-capture` | Native C engine | 1.2042× | 1.1909–1.2210× | 0.08× | FASTER |
| Practice | `cal.search.look-capture` | Rust engine | 0.0155× | 0.0154–0.0157× | 3.29× | SLOWER |
| Practice | `cal.findall.tokens` | Python engine | 0.0116× | 0.0111–0.0123× | 7.14× | SLOWER |
| Practice | `cal.findall.tokens` | Native C engine | 0.9617× | 0.9100–1.0189× | 0.28× | — |
| Practice | `cal.findall.tokens` | Rust engine | 0.0041× | 0.0039–0.0044× | 3.26× | SLOWER |
| Practice | `cal.finditer.groups` | Python engine | 0.0135× | 0.0131–0.0140× | 7.75× | SLOWER |
| Practice | `cal.finditer.groups` | Native C engine | 1.4970× | 1.4499–1.5466× | 0.39× | FASTER |
| Practice | `cal.finditer.groups` | Rust engine | 0.0101× | 0.0098–0.0104× | 1.91× | SLOWER |
| Practice | `cal.split.capture` | Python engine | 0.0101× | 0.0100–0.0102× | 11.37× | SLOWER |
| Practice | `cal.split.capture` | Native C engine | 1.5912× | 1.5793–1.6052× | 0.20× | FASTER |
| Practice | `cal.split.capture` | Rust engine | 0.0066× | 0.0066–0.0067× | 2.62× | SLOWER |
| Practice | `cal.sub.template` | Python engine | 0.0174× | 0.0168–0.0182× | 9.30× | SLOWER |
| Practice | `cal.sub.template` | Native C engine | 1.9847× | 1.9064–2.0703× | 0.12× | FASTER |
| Practice | `cal.sub.template` | Rust engine | 0.0155× | 0.0150–0.0162× | 2.39× | SLOWER |
| Practice | `cal.subn.callable` | Python engine | 0.0250× | 0.0235–0.0271× | 5.05× | SLOWER |
| Practice | `cal.subn.callable` | Native C engine | 1.1072× | 1.0246–1.1989× | 0.25× | FASTER |
| Practice | `cal.subn.callable` | Rust engine | 0.0201× | 0.0189–0.0217× | 2.56× | SLOWER |
| Practice | `cal.bytes.tokens` | Python engine | 0.0081× | 0.0075–0.0091× | 8.29× | SLOWER |
| Practice | `cal.bytes.tokens` | Native C engine | 0.8522× | 0.7332–0.9861× | 0.12× | — |
| Practice | `cal.bytes.tokens` | Rust engine | 0.0060× | 0.0055–0.0067× | 3.43× | SLOWER |
| Practice | `cal.unicode.words` | Python engine | 0.0067× | 0.0062–0.0077× | 6.52× | SLOWER |
| Practice | `cal.unicode.words` | Native C engine | 0.8272× | 0.7686–0.9356× | 0.20× | — |
| Practice | `cal.unicode.words` | Rust engine | 0.0107× | 0.0101–0.0121× | 2.69× | SLOWER |
| Practice | `cal.cold.compile-search` | Python engine | 0.2957× | 0.2900–0.3011× | 5.84× | SLOWER |
| Practice | `cal.cold.compile-search` | Native C engine | 1.5021× | 1.4766–1.5278× | 0.76× | FASTER |
| Practice | `cal.cold.compile-search` | Rust engine | 0.6949× | 0.6818–0.7091× | 1.95× | SLOWER |
| Practice | `cal.module.warm` | Python engine | 0.0107× | 0.0106–0.0108× | 7.21× | SLOWER |
| Practice | `cal.module.warm` | Native C engine | 1.1448× | 1.1305–1.1598× | 0.07× | FASTER |
| Practice | `cal.module.warm` | Rust engine | 0.0307× | 0.0304–0.0311× | 3.39× | SLOWER |
| Practice | `cal.empty.finditer` | Python engine | 0.0100× | 0.0097–0.0102× | 8.09× | SLOWER |
| Practice | `cal.empty.finditer` | Native C engine | 0.7366× | 0.7171–0.7516× | 0.59× | SLOWER |
| Practice | `cal.empty.finditer` | Rust engine | 0.0211× | 0.0206–0.0216× | 1.67× | SLOWER |
| Practice | `cal.backref.fullmatch` | Python engine | 0.0190× | 0.0185–0.0194× | 6.99× | SLOWER |
| Practice | `cal.backref.fullmatch` | Native C engine | 1.0667× | 1.0489–1.0847× | 0.08× | FASTER |
| Practice | `cal.backref.fullmatch` | Rust engine | 0.0187× | 0.0184–0.0190× | 3.04× | SLOWER |
| Practice | `cal.conditional.match` | Python engine | 0.0191× | 0.0182–0.0207× | 6.78× | SLOWER |
| Practice | `cal.conditional.match` | Native C engine | 1.1181× | 1.0669–1.2118× | 0.08× | FASTER |
| Practice | `cal.conditional.match` | Rust engine | 0.0166× | 0.0157–0.0180× | 2.97× | SLOWER |
| Practice | `cal.atomic.search` | Python engine | 0.0101× | 0.0100–0.0103× | 8.80× | SLOWER |
| Practice | `cal.atomic.search` | Native C engine | 0.5975× | 0.5916–0.6041× | 0.50× | SLOWER |
| Practice | `cal.atomic.search` | Rust engine | 0.0188× | 0.0185–0.0190× | 3.14× | SLOWER |
| Practice | `cal.byteslike.findall` | Python engine | 0.0113× | 0.0110–0.0119× | 7.48× | SLOWER |
| Practice | `cal.byteslike.findall` | Native C engine | 1.9702× | 1.9039–2.0755× | 0.18× | FASTER |
| Practice | `cal.byteslike.findall` | Rust engine | 0.0083× | 0.0081–0.0087× | 2.93× | SLOWER |
| Practice | `cal.unicode-name.search` | Python engine | 0.0152× | 0.0145–0.0165× | 4.37× | SLOWER |
| Practice | `cal.unicode-name.search` | Native C engine | 1.4706× | 1.4016–1.5992× | 0.07× | FASTER |
| Practice | `cal.unicode-name.search` | Rust engine | 0.0207× | 0.0197–0.0224× | 3.14× | SLOWER |
| Practice | `cal.ignorecase.findall` | Python engine | 0.0078× | 0.0076–0.0080× | 5.14× | SLOWER |
| Practice | `cal.ignorecase.findall` | Native C engine | 1.0793× | 0.9414–1.1917× | 0.16× | — |
| Practice | `cal.ignorecase.findall` | Rust engine | 0.0086× | 0.0084–0.0089× | 2.96× | SLOWER |
| Practice | `cal.many.split` | Python engine | 0.0124× | 0.0123–0.0126× | 8.86× | SLOWER |
| Practice | `cal.many.split` | Native C engine | 1.1109× | 1.1003–1.1267× | 0.20× | FASTER |
| Practice | `cal.many.split` | Rust engine | 0.0043× | 0.0043–0.0044× | 2.86× | SLOWER |
| Practice | `cal.escape.text` | Python engine | 0.2385× | 0.2302–0.2526× | 48.84× | SLOWER |
| Practice | `cal.escape.text` | Native C engine | 0.2352× | 0.2256–0.2495× | 48.84× | SLOWER |
| Practice | `cal.escape.text` | Rust engine | 0.2378× | 0.2294–0.2513× | 48.84× | SLOWER |
| Practice | `cal.compile.only` | Python engine | 2.1966× | 2.1335–2.2559× | 0.50× | FASTER |
| Practice | `cal.compile.only` | Native C engine | 1.6713× | 1.6339–1.7093× | 0.76× | FASTER |
| Practice | `cal.compile.only` | Rust engine | 1.7683× | 1.7198–1.8149× | 0.56× | FASTER |
| Practice | `cal.scanner.search` | Python engine | 0.0129× | 0.0128–0.0131× | 6.71× | SLOWER |
| Practice | `cal.scanner.search` | Native C engine | 0.4709× | 0.4311–0.5021× | 0.40× | SLOWER |
| Practice | `cal.scanner.search` | Rust engine | 0.0085× | 0.0083–0.0086× | 1.98× | SLOWER |
| Practice | `cal.match.surface` | Python engine | 0.0151× | 0.0150–0.0153× | 12.88× | SLOWER |
| Practice | `cal.match.surface` | Native C engine | 0.3273× | 0.3186–0.3338× | 1.28× | SLOWER |
| Practice | `cal.match.surface` | Rust engine | 0.0495× | 0.0490–0.0500× | 3.26× | SLOWER |
| Holdout | `hold.search.literal.hit` | Python engine | 0.0075× | 0.0074–0.0076× | 102.00× | SLOWER |
| Holdout | `hold.search.literal.hit` | Native C engine | 1.1165× | 1.1076–1.1259× | 0.73× | FASTER |
| Holdout | `hold.search.literal.hit` | Rust engine | 0.0088× | 0.0088–0.0089× | 33.96× | SLOWER |
| Holdout | `hold.search.literal.miss` | Python engine | 0.0024× | 0.0024–0.0025× | 14408.00× | SLOWER |
| Holdout | `hold.search.literal.miss` | Native C engine | 1.1632× | 1.1471–1.1759× | 0.00× | FASTER |
| Holdout | `hold.search.literal.miss` | Rust engine | 0.0056× | 0.0055–0.0056× | 4375.00× | SLOWER |
| Holdout | `hold.search.long-boundary` | Python engine | 0.0003× | 0.0003–0.0003× | 130.58× | SLOWER |
| Holdout | `hold.search.long-boundary` | Native C engine | 15.5117× | 14.3194–16.5744× | 0.07× | FASTER |
| Holdout | `hold.search.long-boundary` | Rust engine | 0.0009× | 0.0009–0.0009× | 218.22× | SLOWER |
| Holdout | `hold.search.class-anchor` | Python engine | 0.0102× | 0.0101–0.0102× | 11.17× | SLOWER |
| Holdout | `hold.search.class-anchor` | Native C engine | 1.0610× | 1.0519–1.0732× | 0.07× | FASTER |
| Holdout | `hold.search.class-anchor` | Rust engine | 0.0130× | 0.0125–0.0134× | 3.39× | SLOWER |
| Holdout | `hold.match.prefix` | Python engine | 0.0261× | 0.0252–0.0280× | 3.87× | SLOWER |
| Holdout | `hold.match.prefix` | Native C engine | 1.0154× | 0.9172–1.1026× | 0.07× | — |
| Holdout | `hold.match.prefix` | Rust engine | 0.0164× | 0.0158–0.0176× | 2.87× | SLOWER |
| Holdout | `hold.fullmatch.structured` | Python engine | 0.0129× | 0.0117–0.0146× | 16.36× | SLOWER |
| Holdout | `hold.fullmatch.structured` | Native C engine | 1.0570× | 0.9549–1.1980× | 0.07× | — |
| Holdout | `hold.fullmatch.structured` | Rust engine | 0.0213× | 0.0193–0.0241× | 3.04× | SLOWER |
| Holdout | `hold.search.look-capture` | Python engine | 0.0100× | 0.0099–0.0100× | 17.64× | SLOWER |
| Holdout | `hold.search.look-capture` | Native C engine | 0.8546× | 0.7845–0.9038× | 0.17× | — |
| Holdout | `hold.search.look-capture` | Rust engine | 0.0166× | 0.0165–0.0167× | 3.26× | SLOWER |
| Holdout | `hold.findall.tokens` | Python engine | 0.0114× | 0.0113–0.0116× | 11.27× | SLOWER |
| Holdout | `hold.findall.tokens` | Native C engine | 1.4314× | 1.4103–1.4528× | 0.21× | FASTER |
| Holdout | `hold.findall.tokens` | Rust engine | 0.0060× | 0.0060–0.0061× | 3.10× | SLOWER |
| Holdout | `hold.finditer.groups` | Python engine | 0.0130× | 0.0126–0.0134× | 7.75× | SLOWER |
| Holdout | `hold.finditer.groups` | Native C engine | 1.3182× | 1.1950–1.4275× | 0.39× | FASTER |
| Holdout | `hold.finditer.groups` | Rust engine | 0.0090× | 0.0087–0.0093× | 1.93× | SLOWER |
| Holdout | `hold.split.capture` | Python engine | 0.0104× | 0.0100–0.0110× | 11.37× | SLOWER |
| Holdout | `hold.split.capture` | Native C engine | 1.6606× | 1.5705–1.7604× | 0.20× | FASTER |
| Holdout | `hold.split.capture` | Rust engine | 0.0067× | 0.0065–0.0071× | 2.62× | SLOWER |
| Holdout | `hold.sub.template` | Python engine | 0.0164× | 0.0161–0.0168× | 9.29× | SLOWER |
| Holdout | `hold.sub.template` | Native C engine | 1.8429× | 1.7524–1.9195× | 0.12× | FASTER |
| Holdout | `hold.sub.template` | Rust engine | 0.0143× | 0.0141–0.0146× | 2.39× | SLOWER |
| Holdout | `hold.subn.callable` | Python engine | 0.0267× | 0.0256–0.0275× | 4.58× | SLOWER |
| Holdout | `hold.subn.callable` | Native C engine | 1.0735× | 1.0354–1.1043× | 0.25× | FASTER |
| Holdout | `hold.subn.callable` | Rust engine | 0.0212× | 0.0209–0.0215× | 2.53× | SLOWER |
| Holdout | `hold.bytes.tokens` | Python engine | 0.0099× | 0.0097–0.0101× | 8.71× | SLOWER |
| Holdout | `hold.bytes.tokens` | Native C engine | 1.8579× | 1.8347–1.8789× | 0.18× | FASTER |
| Holdout | `hold.bytes.tokens` | Rust engine | 0.0080× | 0.0080–0.0081× | 2.92× | SLOWER |
| Holdout | `hold.unicode.words` | Python engine | 0.0092× | 0.0085–0.0102× | 6.63× | SLOWER |
| Holdout | `hold.unicode.words` | Native C engine | 1.6112× | 1.4160–1.8237× | 0.20× | FASTER |
| Holdout | `hold.unicode.words` | Rust engine | 0.0124× | 0.0116–0.0137× | 2.67× | SLOWER |
| Holdout | `hold.cold.compile-search` | Python engine | 0.4760× | 0.4590–0.4887× | 5.95× | SLOWER |
| Holdout | `hold.cold.compile-search` | Native C engine | 1.4765× | 1.4434–1.5112× | 0.79× | FASTER |
| Holdout | `hold.cold.compile-search` | Rust engine | 0.7257× | 0.7106–0.7412× | 1.93× | SLOWER |
| Holdout | `hold.module.warm` | Python engine | 0.0196× | 0.0191–0.0202× | 7.12× | SLOWER |
| Holdout | `hold.module.warm` | Native C engine | 1.0423× | 1.0050–1.0808× | 0.07× | FASTER |
| Holdout | `hold.module.warm` | Rust engine | 0.0312× | 0.0304–0.0321× | 3.38× | SLOWER |
| Holdout | `hold.empty.finditer` | Python engine | 0.0094× | 0.0087–0.0103× | 8.52× | SLOWER |
| Holdout | `hold.empty.finditer` | Native C engine | 0.7187× | 0.6675–0.7919× | 0.61× | SLOWER |
| Holdout | `hold.empty.finditer` | Rust engine | 0.0217× | 0.0203–0.0237× | 1.62× | SLOWER |
| Holdout | `hold.backref.fullmatch` | Python engine | 0.0195× | 0.0182–0.0220× | 6.99× | SLOWER |
| Holdout | `hold.backref.fullmatch` | Native C engine | 1.1008× | 1.0315–1.2349× | 0.08× | FASTER |
| Holdout | `hold.backref.fullmatch` | Rust engine | 0.0202× | 0.0189–0.0227× | 3.04× | SLOWER |
| Holdout | `hold.conditional.match` | Python engine | 0.0200× | 0.0190–0.0217× | 6.78× | SLOWER |
| Holdout | `hold.conditional.match` | Native C engine | 1.0544× | 0.9441–1.1826× | 0.08× | — |
| Holdout | `hold.conditional.match` | Rust engine | 0.0192× | 0.0182–0.0208× | 2.94× | SLOWER |
| Holdout | `hold.atomic.search` | Python engine | 0.0107× | 0.0104–0.0111× | 6.53× | SLOWER |
| Holdout | `hold.atomic.search` | Native C engine | 0.8390× | 0.7267–0.9181× | 0.07× | — |
| Holdout | `hold.atomic.search` | Rust engine | 0.0217× | 0.0210–0.0226× | 3.13× | SLOWER |
| Holdout | `hold.byteslike.findall` | Python engine | 0.0114× | 0.0111–0.0118× | 7.39× | SLOWER |
| Holdout | `hold.byteslike.findall` | Native C engine | 1.8723× | 1.7139–1.9966× | 0.18× | FASTER |
| Holdout | `hold.byteslike.findall` | Rust engine | 0.0082× | 0.0080–0.0085× | 2.83× | SLOWER |
| Holdout | `hold.unicode-name.search` | Python engine | 0.0131× | 0.0129–0.0132× | 4.69× | SLOWER |
| Holdout | `hold.unicode-name.search` | Native C engine | 1.3841× | 1.3645–1.4031× | 0.07× | FASTER |
| Holdout | `hold.unicode-name.search` | Rust engine | 0.0193× | 0.0191–0.0196× | 3.14× | SLOWER |
| Holdout | `hold.ignorecase.findall` | Python engine | 0.0079× | 0.0078–0.0079× | 4.86× | SLOWER |
| Holdout | `hold.ignorecase.findall` | Native C engine | 1.0356× | 0.9538–1.0950× | 0.16× | — |
| Holdout | `hold.ignorecase.findall` | Rust engine | 0.0092× | 0.0091–0.0093× | 2.94× | SLOWER |
| Holdout | `hold.many.split` | Python engine | 0.0124× | 0.0120–0.0128× | 8.86× | SLOWER |
| Holdout | `hold.many.split` | Native C engine | 1.0523× | 0.9498–1.1131× | 0.20× | — |
| Holdout | `hold.many.split` | Rust engine | 0.0043× | 0.0042–0.0045× | 2.86× | SLOWER |
| Holdout | `hold.escape.bytes` | Python engine | 0.1810× | 0.1731–0.1908× | 24.36× | SLOWER |
| Holdout | `hold.escape.bytes` | Native C engine | 0.1843× | 0.1781–0.1939× | 24.36× | SLOWER |
| Holdout | `hold.escape.bytes` | Rust engine | 0.1787× | 0.1717–0.1885× | 24.36× | SLOWER |
| Holdout | `hold.compile.only` | Python engine | 1.9740× | 1.9347–2.0151× | 0.54× | FASTER |
| Holdout | `hold.compile.only` | Native C engine | 1.3888× | 1.3606–1.4183× | 0.92× | FASTER |
| Holdout | `hold.compile.only` | Rust engine | 1.6554× | 1.6262–1.6846× | 0.60× | FASTER |
| Holdout | `hold.scanner.search` | Python engine | 0.0135× | 0.0127–0.0148× | 6.71× | SLOWER |
| Holdout | `hold.scanner.search` | Native C engine | 0.5205× | 0.4878–0.5728× | 0.40× | SLOWER |
| Holdout | `hold.scanner.search` | Rust engine | 0.0088× | 0.0084–0.0094× | 1.98× | SLOWER |
| Holdout | `hold.match.surface` | Python engine | 0.0230× | 0.0228–0.0233× | 12.79× | SLOWER |
| Holdout | `hold.match.surface` | Native C engine | 0.2670× | 0.2618–0.2719× | 1.27× | SLOWER |
| Holdout | `hold.match.surface` | Rust engine | 0.0442× | 0.0438–0.0446× | 3.25× | SLOWER |
| Practice | `cal.real.log` | Python engine | 0.0029× | 0.0028–0.0030× | 27.33× | SLOWER |
| Practice | `cal.real.log` | Native C engine | 0.2834× | 0.2745–0.2937× | 0.33× | SLOWER |
| Practice | `cal.real.log` | Rust engine | 0.0058× | 0.0055–0.0060× | 3.19× | SLOWER |
| Practice | `cal.real.url` | Python engine | 0.0062× | 0.0062–0.0063× | 26.38× | SLOWER |
| Practice | `cal.real.url` | Native C engine | 0.6831× | 0.6574–0.7042× | 0.11× | SLOWER |
| Practice | `cal.real.url` | Rust engine | 0.0113× | 0.0112–0.0115× | 3.49× | SLOWER |
| Practice | `cal.real.email` | Python engine | 0.0057× | 0.0056–0.0057× | 9.90× | SLOWER |
| Practice | `cal.real.email` | Native C engine | 0.5124× | 0.4931–0.5274× | 0.12× | SLOWER |
| Practice | `cal.real.email` | Rust engine | 0.0060× | 0.0059–0.0060× | 3.85× | SLOWER |
| Practice | `cal.real.datetime` | Python engine | 0.0077× | 0.0077–0.0078× | 23.68× | SLOWER |
| Practice | `cal.real.datetime` | Native C engine | 0.8084× | 0.7608–0.8433× | 0.09× | — |
| Practice | `cal.real.datetime` | Rust engine | 0.0151× | 0.0150–0.0152× | 3.49× | SLOWER |
| Practice | `cal.real.version` | Python engine | 0.0113× | 0.0108–0.0118× | 22.95× | SLOWER |
| Practice | `cal.real.version` | Native C engine | 1.1249× | 1.0531–1.1939× | 0.00× | FASTER |
| Practice | `cal.real.version` | Rust engine | 0.0283× | 0.0275–0.0293× | 3.46× | SLOWER |
| Practice | `cal.real.uuid` | Python engine | 0.0063× | 0.0061–0.0064× | 18.66× | SLOWER |
| Practice | `cal.real.uuid` | Native C engine | 0.7463× | 0.7123–0.7730× | 0.07× | SLOWER |
| Practice | `cal.real.uuid` | Rust engine | 0.0127× | 0.0123–0.0129× | 3.96× | SLOWER |
| Practice | `cal.real.ip` | Python engine | 0.0081× | 0.0080–0.0083× | 29.12× | SLOWER |
| Practice | `cal.real.ip` | Native C engine | 0.8475× | 0.7555–0.9046× | 0.07× | — |
| Practice | `cal.real.ip` | Rust engine | 0.0253× | 0.0249–0.0258× | 3.02× | SLOWER |
| Practice | `cal.real.path` | Python engine | 0.0056× | 0.0056–0.0057× | 30.63× | SLOWER |
| Practice | `cal.real.path` | Native C engine | 0.7347× | 0.6974–0.7617× | 0.12× | SLOWER |
| Practice | `cal.real.path` | Rust engine | 0.0100× | 0.0098–0.0101× | 3.60× | SLOWER |
| Practice | `cal.real.config` | Python engine | 0.0081× | 0.0078–0.0083× | 16.04× | SLOWER |
| Practice | `cal.real.config` | Native C engine | 0.9742× | 0.9269–1.0079× | 0.35× | — |
| Practice | `cal.real.config` | Rust engine | 0.0163× | 0.0160–0.0166× | 2.32× | SLOWER |
| Practice | `cal.real.comments` | Python engine | 0.0066× | 0.0066–0.0067× | 11.73× | SLOWER |
| Practice | `cal.real.comments` | Native C engine | 0.7829× | 0.7733–0.7922× | 0.14× | SLOWER |
| Practice | `cal.real.comments` | Rust engine | 0.0038× | 0.0038–0.0039× | 3.74× | SLOWER |
| Practice | `cal.real.whitespace` | Python engine | 0.0070× | 0.0069–0.0071× | 8.36× | SLOWER |
| Practice | `cal.real.whitespace` | Native C engine | 1.3735× | 1.2894–1.4290× | 0.14× | FASTER |
| Practice | `cal.real.whitespace` | Rust engine | 0.0075× | 0.0074–0.0076× | 2.79× | SLOWER |
| Practice | `cal.real.lines` | Python engine | 0.0095× | 0.0093–0.0099× | 14.09× | SLOWER |
| Practice | `cal.real.lines` | Native C engine | 0.9157× | 0.8487–0.9789× | 0.15× | — |
| Practice | `cal.real.lines` | Rust engine | 0.0090× | 0.0087–0.0093× | 2.83× | SLOWER |
| Practice | `cal.real.markup` | Python engine | 0.0047× | 0.0047–0.0048× | 13.23× | SLOWER |
| Practice | `cal.real.markup` | Native C engine | 0.5624× | 0.5320–0.5882× | 0.10× | SLOWER |
| Practice | `cal.real.markup` | Rust engine | 0.0037× | 0.0036–0.0037× | 4.19× | SLOWER |
| Practice | `cal.real.quotes` | Python engine | 0.0042× | 0.0041–0.0042× | 18.83× | SLOWER |
| Practice | `cal.real.quotes` | Native C engine | 0.6293× | 0.6195–0.6376× | 0.10× | SLOWER |
| Practice | `cal.real.quotes` | Rust engine | 0.0069× | 0.0065–0.0071× | 3.83× | SLOWER |
| Practice | `cal.real.csv` | Python engine | 0.0050× | 0.0049–0.0051× | 19.83× | SLOWER |
| Practice | `cal.real.csv` | Native C engine | 0.3744× | 0.3510–0.3917× | 0.32× | SLOWER |
| Practice | `cal.real.csv` | Rust engine | 0.0102× | 0.0098–0.0106× | 2.97× | SLOWER |
| Practice | `cal.branch.prefix` | Python engine | 0.0090× | 0.0089–0.0092× | 12.65× | SLOWER |
| Practice | `cal.branch.prefix` | Native C engine | 0.6732× | 0.6014–0.7178× | 0.07× | SLOWER |
| Practice | `cal.branch.prefix` | Rust engine | 0.0124× | 0.0122–0.0126× | 3.37× | SLOWER |
| Practice | `cal.branch.miss` | Python engine | 0.0011× | 0.0009–0.0013× | 83.64× | SLOWER |
| Practice | `cal.branch.miss` | Native C engine | 0.0967× | 0.0837–0.1184× | 0.00× | SLOWER |
| Practice | `cal.branch.miss` | Rust engine | 0.0138× | 0.0124–0.0161× | 4.25× | SLOWER |
| Practice | `cal.repeat.nested` | Python engine | 0.0101× | 0.0098–0.0103× | 15.24× | SLOWER |
| Practice | `cal.repeat.nested` | Native C engine | 0.8296× | 0.8112–0.8483× | 0.64× | — |
| Practice | `cal.repeat.nested` | Rust engine | 0.0229× | 0.0224–0.0235× | 1.57× | SLOWER |
| Practice | `cal.lines.records` | Python engine | 0.0088× | 0.0083–0.0095× | 14.74× | SLOWER |
| Practice | `cal.lines.records` | Native C engine | 1.0284× | 0.9447–1.1252× | 0.36× | — |
| Practice | `cal.lines.records` | Rust engine | 0.0075× | 0.0071–0.0081× | 2.56× | SLOWER |
| Practice | `cal.block.dotall` | Python engine | 0.0065× | 0.0064–0.0067× | 17.13× | SLOWER |
| Practice | `cal.block.dotall` | Native C engine | 0.6807× | 0.6657–0.6967× | 0.08× | SLOWER |
| Practice | `cal.block.dotall` | Rust engine | 0.0127× | 0.0125–0.0130× | 3.97× | SLOWER |
| Practice | `cal.pattern.verbose` | Python engine | 0.0041× | 0.0041–0.0041× | 14.85× | SLOWER |
| Practice | `cal.pattern.verbose` | Native C engine | 0.5266× | 0.5213–0.5330× | 0.09× | SLOWER |
| Practice | `cal.pattern.verbose` | Rust engine | 0.0194× | 0.0193–0.0196× | 3.43× | SLOWER |
| Practice | `cal.mode.ascii` | Python engine | 0.0057× | 0.0056–0.0058× | 7.27× | SLOWER |
| Practice | `cal.mode.ascii` | Native C engine | 0.8730× | 0.8582–0.8938× | 0.13× | — |
| Practice | `cal.mode.ascii` | Rust engine | 0.0099× | 0.0098–0.0101× | 3.04× | SLOWER |
| Practice | `cal.mode.casefold` | Python engine | 0.0083× | 0.0082–0.0085× | 5.52× | SLOWER |
| Practice | `cal.mode.casefold` | Native C engine | 1.1970× | 1.1799–1.2154× | 0.20× | FASTER |
| Practice | `cal.mode.casefold` | Rust engine | 0.0090× | 0.0089–0.0092× | 2.90× | SLOWER |
| Practice | `cal.mode.astral` | Python engine | 0.0099× | 0.0098–0.0100× | 7.05× | SLOWER |
| Practice | `cal.mode.astral` | Native C engine | 1.6675× | 1.6551–1.6795× | 0.25× | FASTER |
| Practice | `cal.mode.astral` | Rust engine | 0.0096× | 0.0096–0.0097× | 2.76× | SLOWER |
| Practice | `cal.look.negative-ahead` | Python engine | 0.0038× | 0.0037–0.0038× | 15.69× | SLOWER |
| Practice | `cal.look.negative-ahead` | Native C engine | 0.3605× | 0.3466–0.3700× | 0.53× | SLOWER |
| Practice | `cal.look.negative-ahead` | Rust engine | 0.0073× | 0.0072–0.0073× | 3.46× | SLOWER |
| Practice | `cal.look.negative-behind` | Python engine | 0.0071× | 0.0068–0.0076× | 12.65× | SLOWER |
| Practice | `cal.look.negative-behind` | Native C engine | 0.6283× | 0.5749–0.6731× | 0.10× | SLOWER |
| Practice | `cal.look.negative-behind` | Rust engine | 0.0103× | 0.0099–0.0110× | 3.19× | SLOWER |
| Practice | `cal.bytes.replace` | Python engine | 0.0179× | 0.0168–0.0194× | 9.71× | SLOWER |
| Practice | `cal.bytes.replace` | Native C engine | 1.1662× | 1.0891–1.2698× | 0.95× | FASTER |
| Practice | `cal.bytes.replace` | Rust engine | 0.0171× | 0.0160–0.0184× | 2.52× | SLOWER |
| Practice | `cal.bytes.scan` | Python engine | 0.0117× | 0.0112–0.0126× | 8.55× | SLOWER |
| Practice | `cal.bytes.scan` | Native C engine | 0.5601× | 0.5044–0.6259× | 0.42× | SLOWER |
| Practice | `cal.bytes.scan` | Rust engine | 0.0093× | 0.0089–0.0100× | 1.87× | SLOWER |
| Practice | `cal.compile.complex` | Python engine | 1.7608× | 1.7086–1.8309× | 0.39× | FASTER |
| Practice | `cal.compile.complex` | Native C engine | 1.3683× | 1.3092–1.4300× | 0.98× | FASTER |
| Practice | `cal.compile.complex` | Rust engine | 1.6988× | 1.6480–1.7566× | 0.52× | FASTER |
| Practice | `cal.module.replace` | Python engine | 0.0212× | 0.0207–0.0221× | 10.12× | SLOWER |
| Practice | `cal.module.replace` | Native C engine | 1.2144× | 1.1782–1.2764× | 0.04× | FASTER |
| Practice | `cal.module.replace` | Rust engine | 0.0196× | 0.0191–0.0204× | 2.52× | SLOWER |
| Practice | `cal.zero.boundary` | Python engine | 0.0075× | 0.0074–0.0076× | 13.81× | SLOWER |
| Practice | `cal.zero.boundary` | Native C engine | 0.5198× | 0.5101–0.5296× | 0.62× | SLOWER |
| Practice | `cal.zero.boundary` | Rust engine | 0.0131× | 0.0128–0.0133× | 1.69× | SLOWER |
| Practice | `cal.dense.iter` | Python engine | 0.0156× | 0.0150–0.0163× | 4.92× | SLOWER |
| Practice | `cal.dense.iter` | Native C engine | 1.3010× | 1.2665–1.3414× | 0.51× | FASTER |
| Practice | `cal.dense.iter` | Rust engine | 0.0079× | 0.0077–0.0082× | 1.49× | SLOWER |
| Practice | `cal.capture.optional` | Python engine | 0.0110× | 0.0106–0.0115× | 14.26× | SLOWER |
| Practice | `cal.capture.optional` | Native C engine | 0.9657× | 0.9151–1.0206× | 0.18× | — |
| Practice | `cal.capture.optional` | Rust engine | 0.0091× | 0.0087–0.0095× | 2.79× | SLOWER |
| Practice | `cal.split.limited` | Python engine | 0.0066× | 0.0065–0.0068× | 7.47× | SLOWER |
| Practice | `cal.split.limited` | Native C engine | 0.7953× | 0.7135–0.8562× | 0.19× | SLOWER |
| Practice | `cal.split.limited` | Rust engine | 0.0075× | 0.0073–0.0077× | 2.82× | SLOWER |
| Practice | `cal.replace.limited` | Python engine | 0.0129× | 0.0128–0.0131× | 6.04× | SLOWER |
| Practice | `cal.replace.limited` | Native C engine | 1.2409× | 1.2271–1.2550× | 0.15× | FASTER |
| Practice | `cal.replace.limited` | Rust engine | 0.0090× | 0.0089–0.0091× | 2.90× | SLOWER |
| Practice | `cal.bytes.view-long` | Python engine | 0.0062× | 0.0061–0.0064× | 48.64× | SLOWER |
| Practice | `cal.bytes.view-long` | Native C engine | 1.0429× | 1.0197–1.0714× | 0.60× | FASTER |
| Practice | `cal.bytes.view-long` | Rust engine | 0.0009× | 0.0009–0.0009× | 5.61× | SLOWER |
| Practice | `cal.window.search` | Python engine | 0.0184× | 0.0181–0.0187× | 4.40× | SLOWER |
| Practice | `cal.window.search` | Native C engine | 0.8269× | 0.7493–0.8747× | 0.18× | — |
| Practice | `cal.window.search` | Rust engine | 0.0145× | 0.0143–0.0146× | 3.30× | SLOWER |
| Practice | `cal.window.findall` | Python engine | 0.0163× | 0.0162–0.0165× | 4.02× | SLOWER |
| Practice | `cal.window.findall` | Native C engine | 0.9805× | 0.9718–0.9895× | 0.23× | — |
| Practice | `cal.window.findall` | Rust engine | 0.0071× | 0.0070–0.0072× | 3.01× | SLOWER |
| Practice | `cal.window.scanner` | Python engine | 0.0170× | 0.0160–0.0184× | 4.46× | SLOWER |
| Practice | `cal.window.scanner` | Native C engine | 0.4569× | 0.4206–0.5030× | 0.35× | SLOWER |
| Practice | `cal.window.scanner` | Rust engine | 0.0088× | 0.0082–0.0096× | 2.20× | SLOWER |
| Practice | `cal.window.match` | Python engine | 0.0334× | 0.0331–0.0338× | 3.55× | SLOWER |
| Practice | `cal.window.match` | Native C engine | 0.8785× | 0.8722–0.8853× | 0.18× | — |
| Practice | `cal.window.match` | Rust engine | 0.0165× | 0.0163–0.0166× | 2.45× | SLOWER |
| Practice | `cal.literal.replace` | Python engine | 0.0064× | 0.0062–0.0067× | 41.75× | SLOWER |
| Practice | `cal.literal.replace` | Native C engine | 1.3475× | 1.2935–1.4244× | 0.53× | FASTER |
| Practice | `cal.literal.replace` | Rust engine | 0.0052× | 0.0051–0.0055× | 10.40× | SLOWER |
| Practice | `cal.template.repeat` | Python engine | 0.0177× | 0.0174–0.0182× | 6.29× | SLOWER |
| Practice | `cal.template.repeat` | Native C engine | 1.4408× | 1.4114–1.4891× | 0.15× | FASTER |
| Practice | `cal.template.repeat` | Rust engine | 0.0119× | 0.0116–0.0123× | 2.29× | SLOWER |
| Practice | `cal.match.miss` | Python engine | 0.0250× | 0.0245–0.0254× | 5.02× | SLOWER |
| Practice | `cal.match.miss` | Native C engine | 0.9638× | 0.9574–0.9722× | 0.00× | — |
| Practice | `cal.match.miss` | Rust engine | 0.0068× | 0.0068–0.0069× | 4.00× | SLOWER |
| Practice | `cal.fullmatch.miss` | Python engine | 0.0160× | 0.0155–0.0165× | 11.09× | SLOWER |
| Practice | `cal.fullmatch.miss` | Native C engine | 1.0739× | 1.0470–1.1129× | 0.00× | FASTER |
| Practice | `cal.fullmatch.miss` | Rust engine | 0.0203× | 0.0197–0.0210× | 3.32× | SLOWER |
| Holdout | `hold.real.log` | Python engine | 0.0027× | 0.0026–0.0030× | 36.41× | SLOWER |
| Holdout | `hold.real.log` | Native C engine | 0.2527× | 0.2290–0.2828× | 0.33× | SLOWER |
| Holdout | `hold.real.log` | Rust engine | 0.0055× | 0.0052–0.0061× | 3.23× | SLOWER |
| Holdout | `hold.real.url` | Python engine | 0.0055× | 0.0052–0.0058× | 26.93× | SLOWER |
| Holdout | `hold.real.url` | Native C engine | 0.4903× | 0.4531–0.5269× | 0.11× | SLOWER |
| Holdout | `hold.real.url` | Rust engine | 0.0102× | 0.0097–0.0108× | 3.79× | SLOWER |
| Holdout | `hold.real.email` | Python engine | 0.0044× | 0.0042–0.0049× | 12.09× | SLOWER |
| Holdout | `hold.real.email` | Native C engine | 0.6670× | 0.5744–0.7623× | 0.12× | SLOWER |
| Holdout | `hold.real.email` | Rust engine | 0.0069× | 0.0066–0.0075× | 3.88× | SLOWER |
| Holdout | `hold.real.datetime` | Python engine | 0.0078× | 0.0074–0.0084× | 27.33× | SLOWER |
| Holdout | `hold.real.datetime` | Native C engine | 0.9425× | 0.8976–1.0175× | 0.09× | — |
| Holdout | `hold.real.datetime` | Rust engine | 0.0172× | 0.0164–0.0186× | 3.42× | SLOWER |
| Holdout | `hold.real.version` | Python engine | 0.0093× | 0.0091–0.0096× | 23.70× | SLOWER |
| Holdout | `hold.real.version` | Native C engine | 0.7574× | 0.6691–0.8178× | 0.06× | SLOWER |
| Holdout | `hold.real.version` | Rust engine | 0.0205× | 0.0200–0.0212× | 3.01× | SLOWER |
| Holdout | `hold.real.uuid` | Python engine | 0.0062× | 0.0061–0.0063× | 18.05× | SLOWER |
| Holdout | `hold.real.uuid` | Native C engine | 0.6898× | 0.6849–0.6942× | 0.07× | SLOWER |
| Holdout | `hold.real.uuid` | Rust engine | 0.0126× | 0.0125–0.0127× | 3.95× | SLOWER |
| Holdout | `hold.real.ip` | Python engine | 0.0087× | 0.0086–0.0089× | 30.05× | SLOWER |
| Holdout | `hold.real.ip` | Native C engine | 0.9636× | 0.9479–0.9788× | 0.07× | — |
| Holdout | `hold.real.ip` | Rust engine | 0.0207× | 0.0203–0.0211× | 3.02× | SLOWER |
| Holdout | `hold.real.path` | Python engine | 0.0058× | 0.0056–0.0061× | 26.39× | SLOWER |
| Holdout | `hold.real.path` | Native C engine | 0.7576× | 0.7293–0.7926× | 0.12× | SLOWER |
| Holdout | `hold.real.path` | Rust engine | 0.0094× | 0.0091–0.0098× | 3.84× | SLOWER |
| Holdout | `hold.real.config` | Python engine | 0.0085× | 0.0083–0.0089× | 18.02× | SLOWER |
| Holdout | `hold.real.config` | Native C engine | 0.9914× | 0.9547–1.0429× | 0.35× | — |
| Holdout | `hold.real.config` | Rust engine | 0.0152× | 0.0147–0.0159× | 2.32× | SLOWER |
| Holdout | `hold.real.comments` | Python engine | 0.0049× | 0.0049–0.0050× | 16.97× | SLOWER |
| Holdout | `hold.real.comments` | Native C engine | 0.6940× | 0.6307–0.7323× | 0.14× | SLOWER |
| Holdout | `hold.real.comments` | Rust engine | 0.0032× | 0.0032–0.0032× | 4.05× | SLOWER |
| Holdout | `hold.real.whitespace` | Python engine | 0.0071× | 0.0069–0.0074× | 8.45× | SLOWER |
| Holdout | `hold.real.whitespace` | Native C engine | 1.4210× | 1.3869–1.4695× | 0.14× | FASTER |
| Holdout | `hold.real.whitespace` | Rust engine | 0.0069× | 0.0068–0.0072× | 2.74× | SLOWER |
| Holdout | `hold.real.lines` | Python engine | 0.0097× | 0.0092–0.0104× | 13.22× | SLOWER |
| Holdout | `hold.real.lines` | Native C engine | 0.9930× | 0.9459–1.0642× | 0.14× | — |
| Holdout | `hold.real.lines` | Rust engine | 0.0090× | 0.0085–0.0096× | 2.82× | SLOWER |
| Holdout | `hold.real.markup` | Python engine | 0.0047× | 0.0046–0.0047× | 14.16× | SLOWER |
| Holdout | `hold.real.markup` | Native C engine | 0.5738× | 0.5700–0.5775× | 0.13× | SLOWER |
| Holdout | `hold.real.markup` | Rust engine | 0.0031× | 0.0031–0.0031× | 4.34× | SLOWER |
| Holdout | `hold.real.quotes` | Python engine | 0.0042× | 0.0042–0.0042× | 18.87× | SLOWER |
| Holdout | `hold.real.quotes` | Native C engine | 0.6492× | 0.6442–0.6548× | 0.10× | SLOWER |
| Holdout | `hold.real.quotes` | Rust engine | 0.0071× | 0.0070–0.0071× | 3.58× | SLOWER |
| Holdout | `hold.real.csv` | Python engine | 0.0041× | 0.0041–0.0042× | 18.08× | SLOWER |
| Holdout | `hold.real.csv` | Native C engine | 0.3251× | 0.3170–0.3311× | 0.32× | SLOWER |
| Holdout | `hold.real.csv` | Rust engine | 0.0092× | 0.0091–0.0093× | 3.21× | SLOWER |
| Holdout | `hold.branch.prefix` | Python engine | 0.0099× | 0.0098–0.0102× | 11.86× | SLOWER |
| Holdout | `hold.branch.prefix` | Native C engine | 0.7579× | 0.7471–0.7758× | 0.07× | SLOWER |
| Holdout | `hold.branch.prefix` | Rust engine | 0.0130× | 0.0128–0.0133× | 3.36× | SLOWER |
| Holdout | `hold.branch.miss` | Python engine | 0.0008× | 0.0008–0.0008× | 80.13× | SLOWER |
| Holdout | `hold.branch.miss` | Native C engine | 0.0737× | 0.0727–0.0748× | 0.00× | SLOWER |
| Holdout | `hold.branch.miss` | Rust engine | 0.0109× | 0.0108–0.0110× | 4.57× | SLOWER |
| Holdout | `hold.repeat.nested` | Python engine | 0.0099× | 0.0096–0.0103× | 15.24× | SLOWER |
| Holdout | `hold.repeat.nested` | Native C engine | 0.6769× | 0.6403–0.7115× | 0.64× | SLOWER |
| Holdout | `hold.repeat.nested` | Rust engine | 0.0219× | 0.0212–0.0227× | 1.57× | SLOWER |
| Holdout | `hold.lines.records` | Python engine | 0.0085× | 0.0083–0.0088× | 14.74× | SLOWER |
| Holdout | `hold.lines.records` | Native C engine | 0.9977× | 0.9422–1.0389× | 0.36× | — |
| Holdout | `hold.lines.records` | Rust engine | 0.0075× | 0.0073–0.0077× | 2.55× | SLOWER |
| Holdout | `hold.block.dotall` | Python engine | 0.0064× | 0.0062–0.0068× | 18.13× | SLOWER |
| Holdout | `hold.block.dotall` | Native C engine | 0.6676× | 0.6416–0.7088× | 0.08× | SLOWER |
| Holdout | `hold.block.dotall` | Rust engine | 0.0128× | 0.0124–0.0135× | 4.00× | SLOWER |
| Holdout | `hold.pattern.verbose` | Python engine | 0.0036× | 0.0036–0.0037× | 15.91× | SLOWER |
| Holdout | `hold.pattern.verbose` | Native C engine | 0.4736× | 0.4427–0.4975× | 0.09× | SLOWER |
| Holdout | `hold.pattern.verbose` | Rust engine | 0.0244× | 0.0242–0.0247× | 3.45× | SLOWER |
| Holdout | `hold.mode.ascii` | Python engine | 0.0055× | 0.0052–0.0059× | 7.82× | SLOWER |
| Holdout | `hold.mode.ascii` | Native C engine | 0.8842× | 0.8671–0.9093× | 0.21× | — |
| Holdout | `hold.mode.ascii` | Rust engine | 0.0082× | 0.0078–0.0090× | 3.02× | SLOWER |
| Holdout | `hold.mode.casefold` | Python engine | 0.0085× | 0.0082–0.0091× | 5.44× | SLOWER |
| Holdout | `hold.mode.casefold` | Native C engine | 1.2017× | 1.1567–1.2822× | 0.18× | FASTER |
| Holdout | `hold.mode.casefold` | Rust engine | 0.0109× | 0.0105–0.0117× | 2.93× | SLOWER |
| Holdout | `hold.mode.astral` | Python engine | 0.0101× | 0.0092–0.0114× | 7.06× | SLOWER |
| Holdout | `hold.mode.astral` | Native C engine | 1.6787× | 1.5452–1.8735× | 0.25× | FASTER |
| Holdout | `hold.mode.astral` | Rust engine | 0.0101× | 0.0092–0.0114× | 2.77× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Python engine | 0.0036× | 0.0036–0.0037× | 16.30× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Native C engine | 0.3626× | 0.3594–0.3657× | 0.53× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Rust engine | 0.0071× | 0.0070–0.0072× | 3.47× | SLOWER |
| Holdout | `hold.look.negative-behind` | Python engine | 0.0069× | 0.0064–0.0072× | 12.65× | SLOWER |
| Holdout | `hold.look.negative-behind` | Native C engine | 0.5801× | 0.4791–0.6706× | 0.10× | SLOWER |
| Holdout | `hold.look.negative-behind` | Rust engine | 0.0100× | 0.0094–0.0104× | 3.19× | SLOWER |
| Holdout | `hold.bytes.replace` | Python engine | 0.0170× | 0.0167–0.0173× | 9.71× | SLOWER |
| Holdout | `hold.bytes.replace` | Native C engine | 1.1244× | 1.0879–1.1525× | 0.93× | FASTER |
| Holdout | `hold.bytes.replace` | Rust engine | 0.0161× | 0.0159–0.0164× | 2.52× | SLOWER |
| Holdout | `hold.bytes.scan` | Python engine | 0.0110× | 0.0108–0.0112× | 8.55× | SLOWER |
| Holdout | `hold.bytes.scan` | Native C engine | 0.5415× | 0.5200–0.5573× | 0.42× | SLOWER |
| Holdout | `hold.bytes.scan` | Rust engine | 0.0086× | 0.0085–0.0087× | 1.87× | SLOWER |
| Holdout | `hold.compile.complex` | Python engine | 1.8391× | 1.8180–1.8575× | 0.37× | FASTER |
| Holdout | `hold.compile.complex` | Native C engine | 1.4294× | 1.4112–1.4471× | 0.89× | FASTER |
| Holdout | `hold.compile.complex` | Rust engine | 1.5564× | 1.5398–1.5722× | 0.55× | FASTER |
| Holdout | `hold.module.replace` | Python engine | 0.0207× | 0.0204–0.0210× | 10.12× | SLOWER |
| Holdout | `hold.module.replace` | Native C engine | 1.1661× | 1.1273–1.1993× | 0.04× | FASTER |
| Holdout | `hold.module.replace` | Rust engine | 0.0190× | 0.0187–0.0193× | 2.52× | SLOWER |
| Holdout | `hold.zero.boundary` | Python engine | 0.0080× | 0.0078–0.0083× | 8.20× | SLOWER |
| Holdout | `hold.zero.boundary` | Native C engine | 0.5504× | 0.5279–0.5765× | 0.62× | SLOWER |
| Holdout | `hold.zero.boundary` | Rust engine | 0.0136× | 0.0132–0.0142× | 1.67× | SLOWER |
| Holdout | `hold.dense.iter` | Python engine | 0.0155× | 0.0149–0.0162× | 4.92× | SLOWER |
| Holdout | `hold.dense.iter` | Native C engine | 1.2206× | 1.1654–1.2848× | 0.51× | FASTER |
| Holdout | `hold.dense.iter` | Rust engine | 0.0077× | 0.0074–0.0081× | 1.50× | SLOWER |
| Holdout | `hold.capture.optional` | Python engine | 0.0108× | 0.0103–0.0118× | 14.26× | SLOWER |
| Holdout | `hold.capture.optional` | Native C engine | 0.9744× | 0.9026–1.0823× | 0.18× | — |
| Holdout | `hold.capture.optional` | Rust engine | 0.0086× | 0.0082–0.0095× | 2.79× | SLOWER |
| Holdout | `hold.split.limited` | Python engine | 0.0065× | 0.0061–0.0071× | 7.46× | SLOWER |
| Holdout | `hold.split.limited` | Native C engine | 0.7875× | 0.7017–0.8855× | 0.19× | SLOWER |
| Holdout | `hold.split.limited` | Rust engine | 0.0072× | 0.0069–0.0079× | 2.83× | SLOWER |
| Holdout | `hold.replace.limited` | Python engine | 0.0127× | 0.0126–0.0128× | 6.04× | SLOWER |
| Holdout | `hold.replace.limited` | Native C engine | 1.2261× | 1.2133–1.2392× | 0.15× | FASTER |
| Holdout | `hold.replace.limited` | Rust engine | 0.0084× | 0.0083–0.0085× | 2.90× | SLOWER |
| Holdout | `hold.bytes.view-long` | Python engine | 0.0067× | 0.0066–0.0069× | 48.64× | SLOWER |
| Holdout | `hold.bytes.view-long` | Native C engine | 1.1328× | 1.1014–1.1650× | 0.60× | FASTER |
| Holdout | `hold.bytes.view-long` | Rust engine | 0.0010× | 0.0009–0.0010× | 5.61× | SLOWER |
| Holdout | `hold.window.search` | Python engine | 0.0196× | 0.0184–0.0216× | 4.40× | SLOWER |
| Holdout | `hold.window.search` | Native C engine | 0.9363× | 0.8813–1.0343× | 0.18× | — |
| Holdout | `hold.window.search` | Rust engine | 0.0147× | 0.0139–0.0161× | 3.32× | SLOWER |
| Holdout | `hold.window.findall` | Python engine | 0.0184× | 0.0183–0.0186× | 4.03× | SLOWER |
| Holdout | `hold.window.findall` | Native C engine | 0.9986× | 0.9938–1.0033× | 0.22× | — |
| Holdout | `hold.window.findall` | Rust engine | 0.0075× | 0.0075–0.0076× | 2.86× | SLOWER |
| Holdout | `hold.window.scanner` | Python engine | 0.0180× | 0.0170–0.0196× | 4.46× | SLOWER |
| Holdout | `hold.window.scanner` | Native C engine | 0.5085× | 0.4771–0.5579× | 0.35× | SLOWER |
| Holdout | `hold.window.scanner` | Rust engine | 0.0093× | 0.0088–0.0102× | 2.20× | SLOWER |
| Holdout | `hold.window.match` | Python engine | 0.0337× | 0.0334–0.0340× | 3.55× | SLOWER |
| Holdout | `hold.window.match` | Native C engine | 0.9210× | 0.9143–0.9269× | 0.18× | — |
| Holdout | `hold.window.match` | Rust engine | 0.0171× | 0.0170–0.0172× | 2.46× | SLOWER |
| Holdout | `hold.literal.replace` | Python engine | 0.0065× | 0.0064–0.0066× | 38.88× | SLOWER |
| Holdout | `hold.literal.replace` | Native C engine | 1.2972× | 1.2701–1.3260× | 0.52× | FASTER |
| Holdout | `hold.literal.replace` | Rust engine | 0.0054× | 0.0053–0.0055× | 10.36× | SLOWER |
| Holdout | `hold.template.repeat` | Python engine | 0.0192× | 0.0190–0.0194× | 6.32× | SLOWER |
| Holdout | `hold.template.repeat` | Native C engine | 1.4774× | 1.3947–1.5496× | 0.14× | FASTER |
| Holdout | `hold.template.repeat` | Rust engine | 0.0138× | 0.0137–0.0140× | 2.28× | SLOWER |
| Holdout | `hold.match.miss` | Python engine | 0.0288× | 0.0280–0.0298× | 5.02× | SLOWER |
| Holdout | `hold.match.miss` | Native C engine | 1.1094× | 1.0864–1.1432× | 0.00× | FASTER |
| Holdout | `hold.match.miss` | Rust engine | 0.0073× | 0.0071–0.0075× | 4.20× | SLOWER |
| Holdout | `hold.fullmatch.miss` | Python engine | 0.0183× | 0.0175–0.0199× | 11.09× | SLOWER |
| Holdout | `hold.fullmatch.miss` | Native C engine | 1.1923× | 1.1369–1.2990× | 0.00× | FASTER |
| Holdout | `hold.fullmatch.miss` | Rust engine | 0.0234× | 0.0223–0.0256× | 3.31× | SLOWER |

## Large slowdowns

- Python engine: `cal.search.literal.hit` (0.008×), `cal.search.literal.miss` (0.002×), `cal.search.long-boundary` (0.000×), `cal.search.class-anchor` (0.011×), `cal.match.prefix` (0.025×), `cal.fullmatch.structured` (0.013×), `cal.search.look-capture` (0.008×), `cal.findall.tokens` (0.012×), `cal.finditer.groups` (0.014×), `cal.split.capture` (0.010×), `cal.sub.template` (0.017×), `cal.subn.callable` (0.025×), `cal.bytes.tokens` (0.008×), `cal.unicode.words` (0.007×), `cal.cold.compile-search` (0.296×), `cal.module.warm` (0.011×), `cal.empty.finditer` (0.010×), `cal.backref.fullmatch` (0.019×), `cal.conditional.match` (0.019×), `cal.atomic.search` (0.010×), `cal.byteslike.findall` (0.011×), `cal.unicode-name.search` (0.015×), `cal.ignorecase.findall` (0.008×), `cal.many.split` (0.012×), `cal.escape.text` (0.239×), `cal.scanner.search` (0.013×), `cal.match.surface` (0.015×), `hold.search.literal.hit` (0.007×), `hold.search.literal.miss` (0.002×), `hold.search.long-boundary` (0.000×), `hold.search.class-anchor` (0.010×), `hold.match.prefix` (0.026×), `hold.fullmatch.structured` (0.013×), `hold.search.look-capture` (0.010×), `hold.findall.tokens` (0.011×), `hold.finditer.groups` (0.013×), `hold.split.capture` (0.010×), `hold.sub.template` (0.016×), `hold.subn.callable` (0.027×), `hold.bytes.tokens` (0.010×), `hold.unicode.words` (0.009×), `hold.cold.compile-search` (0.476×), `hold.module.warm` (0.020×), `hold.empty.finditer` (0.009×), `hold.backref.fullmatch` (0.020×), `hold.conditional.match` (0.020×), `hold.atomic.search` (0.011×), `hold.byteslike.findall` (0.011×), `hold.unicode-name.search` (0.013×), `hold.ignorecase.findall` (0.008×), `hold.many.split` (0.012×), `hold.escape.bytes` (0.181×), `hold.scanner.search` (0.014×), `hold.match.surface` (0.023×), `cal.real.log` (0.003×), `cal.real.url` (0.006×), `cal.real.email` (0.006×), `cal.real.datetime` (0.008×), `cal.real.version` (0.011×), `cal.real.uuid` (0.006×), `cal.real.ip` (0.008×), `cal.real.path` (0.006×), `cal.real.config` (0.008×), `cal.real.comments` (0.007×), `cal.real.whitespace` (0.007×), `cal.real.lines` (0.010×), `cal.real.markup` (0.005×), `cal.real.quotes` (0.004×), `cal.real.csv` (0.005×), `cal.branch.prefix` (0.009×), `cal.branch.miss` (0.001×), `cal.repeat.nested` (0.010×), `cal.lines.records` (0.009×), `cal.block.dotall` (0.007×), `cal.pattern.verbose` (0.004×), `cal.mode.ascii` (0.006×), `cal.mode.casefold` (0.008×), `cal.mode.astral` (0.010×), `cal.look.negative-ahead` (0.004×), `cal.look.negative-behind` (0.007×), `cal.bytes.replace` (0.018×), `cal.bytes.scan` (0.012×), `cal.module.replace` (0.021×), `cal.zero.boundary` (0.007×), `cal.dense.iter` (0.016×), `cal.capture.optional` (0.011×), `cal.split.limited` (0.007×), `cal.replace.limited` (0.013×), `cal.bytes.view-long` (0.006×), `cal.window.search` (0.018×), `cal.window.findall` (0.016×), `cal.window.scanner` (0.017×), `cal.window.match` (0.033×), `cal.literal.replace` (0.006×), `cal.template.repeat` (0.018×), `cal.match.miss` (0.025×), `cal.fullmatch.miss` (0.016×), `hold.real.log` (0.003×), `hold.real.url` (0.005×), `hold.real.email` (0.004×), `hold.real.datetime` (0.008×), `hold.real.version` (0.009×), `hold.real.uuid` (0.006×), `hold.real.ip` (0.009×), `hold.real.path` (0.006×), `hold.real.config` (0.009×), `hold.real.comments` (0.005×), `hold.real.whitespace` (0.007×), `hold.real.lines` (0.010×), `hold.real.markup` (0.005×), `hold.real.quotes` (0.004×), `hold.real.csv` (0.004×), `hold.branch.prefix` (0.010×), `hold.branch.miss` (0.001×), `hold.repeat.nested` (0.010×), `hold.lines.records` (0.009×), `hold.block.dotall` (0.006×), `hold.pattern.verbose` (0.004×), `hold.mode.ascii` (0.005×), `hold.mode.casefold` (0.008×), `hold.mode.astral` (0.010×), `hold.look.negative-ahead` (0.004×), `hold.look.negative-behind` (0.007×), `hold.bytes.replace` (0.017×), `hold.bytes.scan` (0.011×), `hold.module.replace` (0.021×), `hold.zero.boundary` (0.008×), `hold.dense.iter` (0.015×), `hold.capture.optional` (0.011×), `hold.split.limited` (0.006×), `hold.replace.limited` (0.013×), `hold.bytes.view-long` (0.007×), `hold.window.search` (0.020×), `hold.window.findall` (0.018×), `hold.window.scanner` (0.018×), `hold.window.match` (0.034×), `hold.literal.replace` (0.007×), `hold.template.repeat` (0.019×), `hold.match.miss` (0.029×), `hold.fullmatch.miss` (0.018×).
- Rust engine: `cal.search.literal.hit` (0.009×), `cal.search.literal.miss` (0.006×), `cal.search.long-boundary` (0.001×), `cal.search.class-anchor` (0.015×), `cal.match.prefix` (0.015×), `cal.fullmatch.structured` (0.018×), `cal.search.look-capture` (0.016×), `cal.findall.tokens` (0.004×), `cal.finditer.groups` (0.010×), `cal.split.capture` (0.007×), `cal.sub.template` (0.016×), `cal.subn.callable` (0.020×), `cal.bytes.tokens` (0.006×), `cal.unicode.words` (0.011×), `cal.cold.compile-search` (0.695×), `cal.module.warm` (0.031×), `cal.empty.finditer` (0.021×), `cal.backref.fullmatch` (0.019×), `cal.conditional.match` (0.017×), `cal.atomic.search` (0.019×), `cal.byteslike.findall` (0.008×), `cal.unicode-name.search` (0.021×), `cal.ignorecase.findall` (0.009×), `cal.many.split` (0.004×), `cal.escape.text` (0.238×), `cal.scanner.search` (0.008×), `cal.match.surface` (0.050×), `hold.search.literal.hit` (0.009×), `hold.search.literal.miss` (0.006×), `hold.search.long-boundary` (0.001×), `hold.search.class-anchor` (0.013×), `hold.match.prefix` (0.016×), `hold.fullmatch.structured` (0.021×), `hold.search.look-capture` (0.017×), `hold.findall.tokens` (0.006×), `hold.finditer.groups` (0.009×), `hold.split.capture` (0.007×), `hold.sub.template` (0.014×), `hold.subn.callable` (0.021×), `hold.bytes.tokens` (0.008×), `hold.unicode.words` (0.012×), `hold.cold.compile-search` (0.726×), `hold.module.warm` (0.031×), `hold.empty.finditer` (0.022×), `hold.backref.fullmatch` (0.020×), `hold.conditional.match` (0.019×), `hold.atomic.search` (0.022×), `hold.byteslike.findall` (0.008×), `hold.unicode-name.search` (0.019×), `hold.ignorecase.findall` (0.009×), `hold.many.split` (0.004×), `hold.escape.bytes` (0.179×), `hold.scanner.search` (0.009×), `hold.match.surface` (0.044×), `cal.real.log` (0.006×), `cal.real.url` (0.011×), `cal.real.email` (0.006×), `cal.real.datetime` (0.015×), `cal.real.version` (0.028×), `cal.real.uuid` (0.013×), `cal.real.ip` (0.025×), `cal.real.path` (0.010×), `cal.real.config` (0.016×), `cal.real.comments` (0.004×), `cal.real.whitespace` (0.007×), `cal.real.lines` (0.009×), `cal.real.markup` (0.004×), `cal.real.quotes` (0.007×), `cal.real.csv` (0.010×), `cal.branch.prefix` (0.012×), `cal.branch.miss` (0.014×), `cal.repeat.nested` (0.023×), `cal.lines.records` (0.008×), `cal.block.dotall` (0.013×), `cal.pattern.verbose` (0.019×), `cal.mode.ascii` (0.010×), `cal.mode.casefold` (0.009×), `cal.mode.astral` (0.010×), `cal.look.negative-ahead` (0.007×), `cal.look.negative-behind` (0.010×), `cal.bytes.replace` (0.017×), `cal.bytes.scan` (0.009×), `cal.module.replace` (0.020×), `cal.zero.boundary` (0.013×), `cal.dense.iter` (0.008×), `cal.capture.optional` (0.009×), `cal.split.limited` (0.007×), `cal.replace.limited` (0.009×), `cal.bytes.view-long` (0.001×), `cal.window.search` (0.014×), `cal.window.findall` (0.007×), `cal.window.scanner` (0.009×), `cal.window.match` (0.016×), `cal.literal.replace` (0.005×), `cal.template.repeat` (0.012×), `cal.match.miss` (0.007×), `cal.fullmatch.miss` (0.020×), `hold.real.log` (0.006×), `hold.real.url` (0.010×), `hold.real.email` (0.007×), `hold.real.datetime` (0.017×), `hold.real.version` (0.021×), `hold.real.uuid` (0.013×), `hold.real.ip` (0.021×), `hold.real.path` (0.009×), `hold.real.config` (0.015×), `hold.real.comments` (0.003×), `hold.real.whitespace` (0.007×), `hold.real.lines` (0.009×), `hold.real.markup` (0.003×), `hold.real.quotes` (0.007×), `hold.real.csv` (0.009×), `hold.branch.prefix` (0.013×), `hold.branch.miss` (0.011×), `hold.repeat.nested` (0.022×), `hold.lines.records` (0.008×), `hold.block.dotall` (0.013×), `hold.pattern.verbose` (0.024×), `hold.mode.ascii` (0.008×), `hold.mode.casefold` (0.011×), `hold.mode.astral` (0.010×), `hold.look.negative-ahead` (0.007×), `hold.look.negative-behind` (0.010×), `hold.bytes.replace` (0.016×), `hold.bytes.scan` (0.009×), `hold.module.replace` (0.019×), `hold.zero.boundary` (0.014×), `hold.dense.iter` (0.008×), `hold.capture.optional` (0.009×), `hold.split.limited` (0.007×), `hold.replace.limited` (0.008×), `hold.bytes.view-long` (0.001×), `hold.window.search` (0.015×), `hold.window.findall` (0.008×), `hold.window.scanner` (0.009×), `hold.window.match` (0.017×), `hold.literal.replace` (0.005×), `hold.template.repeat` (0.014×), `hold.match.miss` (0.007×), `hold.fullmatch.miss` (0.023×).
- Native C engine: `cal.empty.finditer` (0.737×), `cal.atomic.search` (0.598×), `cal.escape.text` (0.235×), `cal.scanner.search` (0.471×), `cal.match.surface` (0.327×), `hold.empty.finditer` (0.719×), `hold.escape.bytes` (0.184×), `hold.scanner.search` (0.520×), `hold.match.surface` (0.267×), `cal.real.log` (0.283×), `cal.real.url` (0.683×), `cal.real.email` (0.512×), `cal.real.uuid` (0.746×), `cal.real.path` (0.735×), `cal.real.comments` (0.783×), `cal.real.markup` (0.562×), `cal.real.quotes` (0.629×), `cal.real.csv` (0.374×), `cal.branch.prefix` (0.673×), `cal.branch.miss` (0.097×), `cal.block.dotall` (0.681×), `cal.pattern.verbose` (0.527×), `cal.look.negative-ahead` (0.360×), `cal.look.negative-behind` (0.628×), `cal.bytes.scan` (0.560×), `cal.zero.boundary` (0.520×), `cal.split.limited` (0.795×), `cal.window.scanner` (0.457×), `hold.real.log` (0.253×), `hold.real.url` (0.490×), `hold.real.email` (0.667×), `hold.real.version` (0.757×), `hold.real.uuid` (0.690×), `hold.real.path` (0.758×), `hold.real.comments` (0.694×), `hold.real.markup` (0.574×), `hold.real.quotes` (0.649×), `hold.real.csv` (0.325×), `hold.branch.prefix` (0.758×), `hold.branch.miss` (0.074×), `hold.repeat.nested` (0.677×), `hold.block.dotall` (0.668×), `hold.pattern.verbose` (0.474×), `hold.look.negative-ahead` (0.363×), `hold.look.negative-behind` (0.580×), `hold.bytes.scan` (0.541×), `hold.zero.boundary` (0.550×), `hold.split.limited` (0.788×), `hold.window.scanner` (0.509×).

The Python engine performs matching work in Python, and the Rust engine repeatedly prepares data and crosses the Python/Rust boundary; both costs dominate short tasks. Native-C losses expose specific boundary and general-path costs:
- Empty matches and controlled branches use the general backtracking/iterator path and construct more match state.
- Escaping currently loops over every character in Python, explaining both the time and extra traced-memory cost.
- Scanning repeatedly returns through a small Python wrapper, so per-match boundary and object costs accumulate.
- Reading many groups and expanding a template makes several Python/C and Python-template calls for one match.
- Everyday log, address, path, comment, markup, quote, and comma-separated-field tasks combine repeated classes, captures, or lookarounds; they take the general native backtracking path instead of its compact single-pass path.
- Searches across many alternative words, especially a complete miss, try branches at successive positions because the native engine has no shared-prefix or start-character filter for these alternatives.
- Structured repeated paths, multi-line blocks, and readable formatted fields require general repeat/capture backtracking, which carries more state than the simple literal and single-character fast paths.
- Excluded-prefix and tagged-word searches evaluate a negative lookaround for each possible match, so the native executor repeats assertion work while scanning.
- Byte and windowed scanning also return through the per-match Python scanner wrapper, so repeated boundary/object costs dominate these short inputs.
- Word/separator-position iteration and limited mixed-separator splits repeatedly use the general iterator or whitespace-backtracking path; each small match pays state and result-construction costs.

No loss is removed from the denominator or hidden from the charts.
