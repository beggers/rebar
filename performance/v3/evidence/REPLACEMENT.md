# Replacement-compatibility follow-up: full paired result

All 7488 raw timing rows, 432 engine/task results, and 300 large slowdowns are retained. Raw SHA-256: `7409a9a2c4a36448285f956200bd83afc36966a81598e3401ed186a3cb7e3322`.

## At a glance

The holdout tasks were kept separate from tuning. **1× means the same speed as Python `re`; higher is faster.** A result is clearly faster only when its measured range stays above 1×. A large slowdown means more than 20% slower.

| Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: | ---: |
| Native C engine | **1.1132×** | 1.1054–1.1206× | 46/72 | 11/72 |
| Rust engine | **0.0139×** | 0.0138–0.0140× | 3/72 | 69/72 |
| Python engine | **0.0119×** | 0.0118–0.0119× | 3/72 | 69/72 |

## Overall results

| Task set | Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |
| --- | --- | ---: | ---: | ---: | ---: |
| Practice | Python engine | 0.0116× | 0.0115–0.0117× | 2/72 | 69 |
| Practice | Native C engine | 1.0922× | 1.0848–1.1004× | 49/72 | 13 |
| Practice | Rust engine | 0.0139× | 0.0138–0.0140× | 2/72 | 69 |
| Holdout | Python engine | 0.0119× | 0.0118–0.0119× | 3/72 | 69 |
| Holdout | Native C engine | 1.1132× | 1.1054–1.1206× | 46/72 | 11 |
| Holdout | Rust engine | 0.0139× | 0.0138–0.0140× | 3/72 | 69 |
| All | Python engine | 0.0117× | 0.0117–0.0118× | 5/144 | 138 |
| All | Native C engine | 1.1027× | 1.0974–1.1083× | 95/144 | 24 |
| All | Rust engine | 0.0139× | 0.0138–0.0139× | 5/144 | 138 |

## Every task

`FASTER` means the measured range stays above 1×. `SLOWER` means more than 20% slower. Memory compares median traced Python memory with Python `re`.

| Task set | Task | Engine | Speed | Measured range | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Practice | `cal.search.literal.hit` | Python engine | 0.0074× | 0.0072–0.0075× | 102.00× | SLOWER |
| Practice | `cal.search.literal.hit` | Native C engine | 1.1116× | 1.1059–1.1170× | 0.73× | FASTER |
| Practice | `cal.search.literal.hit` | Rust engine | 0.0086× | 0.0085–0.0087× | 34.03× | SLOWER |
| Practice | `cal.search.literal.miss` | Python engine | 0.0022× | 0.0022–0.0022× | 14408.00× | SLOWER |
| Practice | `cal.search.literal.miss` | Native C engine | 1.1493× | 1.1421–1.1564× | 0.00× | FASTER |
| Practice | `cal.search.literal.miss` | Rust engine | 0.0056× | 0.0056–0.0057× | 4375.00× | SLOWER |
| Practice | `cal.search.long-boundary` | Python engine | 0.0003× | 0.0003–0.0003× | 129.57× | SLOWER |
| Practice | `cal.search.long-boundary` | Native C engine | 12.2807× | 11.2904–13.5403× | 0.07× | FASTER |
| Practice | `cal.search.long-boundary` | Rust engine | 0.0010× | 0.0009–0.0011× | 140.03× | SLOWER |
| Practice | `cal.search.class-anchor` | Python engine | 0.0112× | 0.0110–0.0115× | 11.57× | SLOWER |
| Practice | `cal.search.class-anchor` | Native C engine | 1.0548× | 1.0300–1.0822× | 0.07× | FASTER |
| Practice | `cal.search.class-anchor` | Rust engine | 0.0146× | 0.0143–0.0150× | 3.36× | SLOWER |
| Practice | `cal.match.prefix` | Python engine | 0.0249× | 0.0245–0.0253× | 3.87× | SLOWER |
| Practice | `cal.match.prefix` | Native C engine | 1.2103× | 1.1962–1.2227× | 0.07× | FASTER |
| Practice | `cal.match.prefix` | Rust engine | 0.0162× | 0.0160–0.0164× | 2.89× | SLOWER |
| Practice | `cal.fullmatch.structured` | Python engine | 0.0132× | 0.0127–0.0135× | 12.07× | SLOWER |
| Practice | `cal.fullmatch.structured` | Native C engine | 1.1804× | 1.1416–1.2177× | 0.07× | FASTER |
| Practice | `cal.fullmatch.structured` | Rust engine | 0.0188× | 0.0176–0.0197× | 3.04× | SLOWER |
| Practice | `cal.search.look-capture` | Python engine | 0.0077× | 0.0074–0.0082× | 17.28× | SLOWER |
| Practice | `cal.search.look-capture` | Native C engine | 1.2721× | 1.2190–1.3668× | 0.08× | FASTER |
| Practice | `cal.search.look-capture` | Rust engine | 0.0164× | 0.0157–0.0176× | 3.29× | SLOWER |
| Practice | `cal.findall.tokens` | Python engine | 0.0106× | 0.0101–0.0115× | 7.14× | SLOWER |
| Practice | `cal.findall.tokens` | Native C engine | 1.0580× | 1.0107–1.1383× | 0.28× | FASTER |
| Practice | `cal.findall.tokens` | Rust engine | 0.0039× | 0.0037–0.0042× | 3.26× | SLOWER |
| Practice | `cal.finditer.groups` | Python engine | 0.0128× | 0.0124–0.0132× | 7.75× | SLOWER |
| Practice | `cal.finditer.groups` | Native C engine | 1.4220× | 1.2917–1.5138× | 0.39× | FASTER |
| Practice | `cal.finditer.groups` | Rust engine | 0.0097× | 0.0095–0.0100× | 1.91× | SLOWER |
| Practice | `cal.split.capture` | Python engine | 0.0099× | 0.0094–0.0109× | 11.37× | SLOWER |
| Practice | `cal.split.capture` | Native C engine | 1.8273× | 1.6873–2.0378× | 0.20× | FASTER |
| Practice | `cal.split.capture` | Rust engine | 0.0067× | 0.0063–0.0075× | 2.62× | SLOWER |
| Practice | `cal.sub.template` | Python engine | 0.0159× | 0.0158–0.0162× | 9.30× | SLOWER |
| Practice | `cal.sub.template` | Native C engine | 1.7740× | 1.7189–1.8118× | 0.12× | FASTER |
| Practice | `cal.sub.template` | Rust engine | 0.0150× | 0.0148–0.0152× | 2.39× | SLOWER |
| Practice | `cal.subn.callable` | Python engine | 0.0239× | 0.0234–0.0244× | 5.05× | SLOWER |
| Practice | `cal.subn.callable` | Native C engine | 1.0982× | 1.0685–1.1252× | 0.25× | FASTER |
| Practice | `cal.subn.callable` | Rust engine | 0.0198× | 0.0195–0.0202× | 2.56× | SLOWER |
| Practice | `cal.bytes.tokens` | Python engine | 0.0073× | 0.0073–0.0073× | 8.29× | SLOWER |
| Practice | `cal.bytes.tokens` | Native C engine | 1.0468× | 1.0418–1.0516× | 0.12× | FASTER |
| Practice | `cal.bytes.tokens` | Rust engine | 0.0054× | 0.0054–0.0054× | 3.43× | SLOWER |
| Practice | `cal.unicode.words` | Python engine | 0.0061× | 0.0060–0.0061× | 6.52× | SLOWER |
| Practice | `cal.unicode.words` | Native C engine | 0.8630× | 0.8173–0.8908× | 0.20× | — |
| Practice | `cal.unicode.words` | Rust engine | 0.0096× | 0.0096–0.0097× | 2.69× | SLOWER |
| Practice | `cal.cold.compile-search` | Python engine | 0.2931× | 0.2903–0.2961× | 5.84× | SLOWER |
| Practice | `cal.cold.compile-search` | Native C engine | 0.7493× | 0.7428–0.7569× | 1.50× | SLOWER |
| Practice | `cal.cold.compile-search` | Rust engine | 0.7087× | 0.7016–0.7160× | 1.95× | SLOWER |
| Practice | `cal.module.warm` | Python engine | 0.0105× | 0.0104–0.0107× | 7.21× | SLOWER |
| Practice | `cal.module.warm` | Native C engine | 1.2362× | 1.2207–1.2561× | 0.07× | FASTER |
| Practice | `cal.module.warm` | Rust engine | 0.0310× | 0.0306–0.0315× | 3.39× | SLOWER |
| Practice | `cal.empty.finditer` | Python engine | 0.0099× | 0.0097–0.0102× | 8.09× | SLOWER |
| Practice | `cal.empty.finditer` | Native C engine | 0.6669× | 0.6370–0.6942× | 0.59× | SLOWER |
| Practice | `cal.empty.finditer` | Rust engine | 0.0211× | 0.0207–0.0216× | 1.67× | SLOWER |
| Practice | `cal.backref.fullmatch` | Python engine | 0.0187× | 0.0185–0.0191× | 6.99× | SLOWER |
| Practice | `cal.backref.fullmatch` | Native C engine | 1.0882× | 1.0699–1.1092× | 0.08× | FASTER |
| Practice | `cal.backref.fullmatch` | Rust engine | 0.0185× | 0.0182–0.0189× | 3.04× | SLOWER |
| Practice | `cal.conditional.match` | Python engine | 0.0177× | 0.0172–0.0184× | 6.78× | SLOWER |
| Practice | `cal.conditional.match` | Native C engine | 1.1932× | 1.1628–1.2379× | 0.08× | FASTER |
| Practice | `cal.conditional.match` | Rust engine | 0.0163× | 0.0157–0.0171× | 2.97× | SLOWER |
| Practice | `cal.atomic.search` | Python engine | 0.0098× | 0.0097–0.0099× | 8.80× | SLOWER |
| Practice | `cal.atomic.search` | Native C engine | 0.9935× | 0.9767–1.0088× | 0.50× | — |
| Practice | `cal.atomic.search` | Rust engine | 0.0187× | 0.0185–0.0190× | 3.14× | SLOWER |
| Practice | `cal.byteslike.findall` | Python engine | 0.0108× | 0.0106–0.0109× | 7.48× | SLOWER |
| Practice | `cal.byteslike.findall` | Native C engine | 1.8615× | 1.8380–1.8899× | 0.18× | FASTER |
| Practice | `cal.byteslike.findall` | Rust engine | 0.0080× | 0.0079–0.0081× | 2.93× | SLOWER |
| Practice | `cal.unicode-name.search` | Python engine | 0.0148× | 0.0148–0.0149× | 4.37× | SLOWER |
| Practice | `cal.unicode-name.search` | Native C engine | 1.3134× | 1.3004–1.3267× | 0.07× | FASTER |
| Practice | `cal.unicode-name.search` | Rust engine | 0.0202× | 0.0201–0.0204× | 3.14× | SLOWER |
| Practice | `cal.ignorecase.findall` | Python engine | 0.0075× | 0.0073–0.0079× | 5.14× | SLOWER |
| Practice | `cal.ignorecase.findall` | Native C engine | 1.3689× | 1.3299–1.4342× | 0.16× | FASTER |
| Practice | `cal.ignorecase.findall` | Rust engine | 0.0085× | 0.0083–0.0089× | 2.96× | SLOWER |
| Practice | `cal.many.split` | Python engine | 0.0119× | 0.0116–0.0122× | 8.86× | SLOWER |
| Practice | `cal.many.split` | Native C engine | 1.1840× | 1.1674–1.2115× | 0.20× | FASTER |
| Practice | `cal.many.split` | Rust engine | 0.0044× | 0.0043–0.0045× | 2.86× | SLOWER |
| Practice | `cal.escape.text` | Python engine | 0.9963× | 0.9928–0.9994× | 1.00× | — |
| Practice | `cal.escape.text` | Native C engine | 0.9765× | 0.9494–0.9942× | 1.00× | — |
| Practice | `cal.escape.text` | Rust engine | 0.9739× | 0.9436–0.9970× | 1.00× | — |
| Practice | `cal.compile.only` | Python engine | 2.2061× | 2.1703–2.2417× | 0.50× | FASTER |
| Practice | `cal.compile.only` | Native C engine | 1.6383× | 1.6069–1.6655× | 1.40× | FASTER |
| Practice | `cal.compile.only` | Rust engine | 1.7689× | 1.7305–1.8030× | 0.56× | FASTER |
| Practice | `cal.scanner.search` | Python engine | 0.0131× | 0.0129–0.0133× | 6.71× | SLOWER |
| Practice | `cal.scanner.search` | Native C engine | 1.0644× | 1.0529–1.0756× | 0.36× | FASTER |
| Practice | `cal.scanner.search` | Rust engine | 0.0089× | 0.0088–0.0091× | 1.98× | SLOWER |
| Practice | `cal.match.surface` | Python engine | 0.0144× | 0.0141–0.0148× | 12.88× | SLOWER |
| Practice | `cal.match.surface` | Native C engine | 1.2114× | 1.1634–1.2502× | 0.42× | FASTER |
| Practice | `cal.match.surface` | Rust engine | 0.0490× | 0.0480–0.0501× | 3.26× | SLOWER |
| Holdout | `hold.search.literal.hit` | Python engine | 0.0075× | 0.0074–0.0075× | 102.00× | SLOWER |
| Holdout | `hold.search.literal.hit` | Native C engine | 1.1309× | 1.1233–1.1381× | 0.73× | FASTER |
| Holdout | `hold.search.literal.hit` | Rust engine | 0.0090× | 0.0088–0.0091× | 33.96× | SLOWER |
| Holdout | `hold.search.literal.miss` | Python engine | 0.0024× | 0.0023–0.0024× | 14408.00× | SLOWER |
| Holdout | `hold.search.literal.miss` | Native C engine | 1.1769× | 1.1664–1.1872× | 0.00× | FASTER |
| Holdout | `hold.search.literal.miss` | Rust engine | 0.0056× | 0.0056–0.0057× | 4375.00× | SLOWER |
| Holdout | `hold.search.long-boundary` | Python engine | 0.0003× | 0.0003–0.0003× | 130.58× | SLOWER |
| Holdout | `hold.search.long-boundary` | Native C engine | 15.1786× | 11.3665–18.6426× | 0.07× | FASTER |
| Holdout | `hold.search.long-boundary` | Rust engine | 0.0010× | 0.0009–0.0010× | 218.22× | SLOWER |
| Holdout | `hold.search.class-anchor` | Python engine | 0.0100× | 0.0098–0.0101× | 11.17× | SLOWER |
| Holdout | `hold.search.class-anchor` | Native C engine | 1.0264× | 1.0158–1.0371× | 0.07× | FASTER |
| Holdout | `hold.search.class-anchor` | Rust engine | 0.0132× | 0.0128–0.0135× | 3.39× | SLOWER |
| Holdout | `hold.match.prefix` | Python engine | 0.0243× | 0.0241–0.0244× | 3.87× | SLOWER |
| Holdout | `hold.match.prefix` | Native C engine | 1.1212× | 1.0680–1.1509× | 0.07× | FASTER |
| Holdout | `hold.match.prefix` | Rust engine | 0.0157× | 0.0157–0.0158× | 2.87× | SLOWER |
| Holdout | `hold.fullmatch.structured` | Python engine | 0.0119× | 0.0117–0.0121× | 16.36× | SLOWER |
| Holdout | `hold.fullmatch.structured` | Native C engine | 1.1752× | 1.1581–1.1911× | 0.07× | FASTER |
| Holdout | `hold.fullmatch.structured` | Rust engine | 0.0201× | 0.0198–0.0204× | 3.04× | SLOWER |
| Holdout | `hold.search.look-capture` | Python engine | 0.0105× | 0.0103–0.0106× | 17.64× | SLOWER |
| Holdout | `hold.search.look-capture` | Native C engine | 0.9875× | 0.9692–1.0064× | 0.17× | — |
| Holdout | `hold.search.look-capture` | Rust engine | 0.0180× | 0.0177–0.0182× | 3.26× | SLOWER |
| Holdout | `hold.findall.tokens` | Python engine | 0.0107× | 0.0105–0.0109× | 11.27× | SLOWER |
| Holdout | `hold.findall.tokens` | Native C engine | 1.5438× | 1.5189–1.5762× | 0.21× | FASTER |
| Holdout | `hold.findall.tokens` | Rust engine | 0.0058× | 0.0057–0.0060× | 3.10× | SLOWER |
| Holdout | `hold.finditer.groups` | Python engine | 0.0130× | 0.0126–0.0136× | 7.75× | SLOWER |
| Holdout | `hold.finditer.groups` | Native C engine | 1.3906× | 1.3478–1.4448× | 0.39× | FASTER |
| Holdout | `hold.finditer.groups` | Rust engine | 0.0091× | 0.0088–0.0095× | 1.93× | SLOWER |
| Holdout | `hold.split.capture` | Python engine | 0.0103× | 0.0100–0.0105× | 11.37× | SLOWER |
| Holdout | `hold.split.capture` | Native C engine | 1.8436× | 1.7300–1.9252× | 0.20× | FASTER |
| Holdout | `hold.split.capture` | Rust engine | 0.0068× | 0.0065–0.0070× | 2.62× | SLOWER |
| Holdout | `hold.sub.template` | Python engine | 0.0163× | 0.0161–0.0166× | 9.29× | SLOWER |
| Holdout | `hold.sub.template` | Native C engine | 1.7738× | 1.6981–1.8380× | 0.12× | FASTER |
| Holdout | `hold.sub.template` | Rust engine | 0.0149× | 0.0147–0.0151× | 2.39× | SLOWER |
| Holdout | `hold.subn.callable` | Python engine | 0.0275× | 0.0271–0.0279× | 4.58× | SLOWER |
| Holdout | `hold.subn.callable` | Native C engine | 1.0960× | 1.0706–1.1179× | 0.25× | FASTER |
| Holdout | `hold.subn.callable` | Rust engine | 0.0221× | 0.0217–0.0225× | 2.53× | SLOWER |
| Holdout | `hold.bytes.tokens` | Python engine | 0.0103× | 0.0102–0.0105× | 8.71× | SLOWER |
| Holdout | `hold.bytes.tokens` | Native C engine | 2.0790× | 2.0551–2.1055× | 0.18× | FASTER |
| Holdout | `hold.bytes.tokens` | Rust engine | 0.0084× | 0.0083–0.0085× | 2.92× | SLOWER |
| Holdout | `hold.unicode.words` | Python engine | 0.0089× | 0.0085–0.0096× | 6.63× | SLOWER |
| Holdout | `hold.unicode.words` | Native C engine | 1.5580× | 1.4141–1.7095× | 0.20× | FASTER |
| Holdout | `hold.unicode.words` | Rust engine | 0.0116× | 0.0113–0.0121× | 2.67× | SLOWER |
| Holdout | `hold.cold.compile-search` | Python engine | 0.4922× | 0.4848–0.5004× | 5.95× | SLOWER |
| Holdout | `hold.cold.compile-search` | Native C engine | 0.8201× | 0.8064–0.8361× | 1.55× | — |
| Holdout | `hold.cold.compile-search` | Rust engine | 0.7524× | 0.7440–0.7626× | 1.93× | SLOWER |
| Holdout | `hold.module.warm` | Python engine | 0.0197× | 0.0194–0.0202× | 7.12× | SLOWER |
| Holdout | `hold.module.warm` | Native C engine | 1.1679× | 1.1481–1.1990× | 0.07× | FASTER |
| Holdout | `hold.module.warm` | Rust engine | 0.0316× | 0.0308–0.0323× | 3.38× | SLOWER |
| Holdout | `hold.empty.finditer` | Python engine | 0.0093× | 0.0092–0.0095× | 8.52× | SLOWER |
| Holdout | `hold.empty.finditer` | Native C engine | 0.6562× | 0.6431–0.6676× | 0.61× | SLOWER |
| Holdout | `hold.empty.finditer` | Rust engine | 0.0217× | 0.0214–0.0221× | 1.62× | SLOWER |
| Holdout | `hold.backref.fullmatch` | Python engine | 0.0184× | 0.0183–0.0186× | 6.99× | SLOWER |
| Holdout | `hold.backref.fullmatch` | Native C engine | 1.0974× | 1.0866–1.1073× | 0.08× | FASTER |
| Holdout | `hold.backref.fullmatch` | Rust engine | 0.0194× | 0.0192–0.0196× | 3.04× | SLOWER |
| Holdout | `hold.conditional.match` | Python engine | 0.0193× | 0.0191–0.0196× | 6.78× | SLOWER |
| Holdout | `hold.conditional.match` | Native C engine | 1.1794× | 1.1607–1.2039× | 0.08× | FASTER |
| Holdout | `hold.conditional.match` | Rust engine | 0.0190× | 0.0188–0.0193× | 2.94× | SLOWER |
| Holdout | `hold.atomic.search` | Python engine | 0.0113× | 0.0111–0.0115× | 6.53× | SLOWER |
| Holdout | `hold.atomic.search` | Native C engine | 1.3430× | 1.2400–1.4157× | 0.07× | FASTER |
| Holdout | `hold.atomic.search` | Rust engine | 0.0234× | 0.0230–0.0238× | 3.13× | SLOWER |
| Holdout | `hold.byteslike.findall` | Python engine | 0.0117× | 0.0116–0.0118× | 7.39× | SLOWER |
| Holdout | `hold.byteslike.findall` | Native C engine | 1.9957× | 1.8828–2.0609× | 0.18× | FASTER |
| Holdout | `hold.byteslike.findall` | Rust engine | 0.0085× | 0.0085–0.0086× | 2.83× | SLOWER |
| Holdout | `hold.unicode-name.search` | Python engine | 0.0139× | 0.0137–0.0141× | 4.69× | SLOWER |
| Holdout | `hold.unicode-name.search` | Native C engine | 1.3135× | 1.2048–1.3843× | 0.07× | FASTER |
| Holdout | `hold.unicode-name.search` | Rust engine | 0.0210× | 0.0207–0.0213× | 3.14× | SLOWER |
| Holdout | `hold.ignorecase.findall` | Python engine | 0.0079× | 0.0078–0.0080× | 4.86× | SLOWER |
| Holdout | `hold.ignorecase.findall` | Native C engine | 1.4401× | 1.4314–1.4488× | 0.16× | FASTER |
| Holdout | `hold.ignorecase.findall` | Rust engine | 0.0095× | 0.0094–0.0097× | 2.94× | SLOWER |
| Holdout | `hold.many.split` | Python engine | 0.0129× | 0.0127–0.0130× | 8.86× | SLOWER |
| Holdout | `hold.many.split` | Native C engine | 1.2740× | 1.2617–1.2890× | 0.20× | FASTER |
| Holdout | `hold.many.split` | Rust engine | 0.0047× | 0.0047–0.0048× | 2.86× | SLOWER |
| Holdout | `hold.escape.bytes` | Python engine | 1.0209× | 1.0076–1.0441× | 0.68× | FASTER |
| Holdout | `hold.escape.bytes` | Native C engine | 1.0072× | 0.9847–1.0372× | 0.68× | — |
| Holdout | `hold.escape.bytes` | Rust engine | 1.0209× | 1.0068–1.0461× | 0.68× | FASTER |
| Holdout | `hold.compile.only` | Python engine | 2.0016× | 1.9739–2.0307× | 0.54× | FASTER |
| Holdout | `hold.compile.only` | Native C engine | 1.3863× | 1.3605–1.4118× | 1.91× | FASTER |
| Holdout | `hold.compile.only` | Rust engine | 1.6857× | 1.6592–1.7113× | 0.60× | FASTER |
| Holdout | `hold.scanner.search` | Python engine | 0.0141× | 0.0135–0.0150× | 6.71× | SLOWER |
| Holdout | `hold.scanner.search` | Native C engine | 1.1341× | 1.0755–1.2127× | 0.36× | FASTER |
| Holdout | `hold.scanner.search` | Rust engine | 0.0096× | 0.0091–0.0102× | 1.98× | SLOWER |
| Holdout | `hold.match.surface` | Python engine | 0.0220× | 0.0217–0.0223× | 12.79× | SLOWER |
| Holdout | `hold.match.surface` | Native C engine | 1.0082× | 0.9755–1.0362× | 0.41× | — |
| Holdout | `hold.match.surface` | Rust engine | 0.0428× | 0.0419–0.0436× | 3.25× | SLOWER |
| Practice | `cal.real.log` | Python engine | 0.0031× | 0.0029–0.0033× | 27.33× | SLOWER |
| Practice | `cal.real.log` | Native C engine | 0.8653× | 0.7977–0.9247× | 0.33× | — |
| Practice | `cal.real.log` | Rust engine | 0.0062× | 0.0058–0.0067× | 3.19× | SLOWER |
| Practice | `cal.real.url` | Python engine | 0.0065× | 0.0064–0.0066× | 26.38× | SLOWER |
| Practice | `cal.real.url` | Native C engine | 0.9263× | 0.9003–0.9477× | 0.11× | — |
| Practice | `cal.real.url` | Rust engine | 0.0123× | 0.0120–0.0126× | 3.49× | SLOWER |
| Practice | `cal.real.email` | Python engine | 0.0056× | 0.0055–0.0056× | 9.90× | SLOWER |
| Practice | `cal.real.email` | Native C engine | 0.6902× | 0.6819–0.6998× | 0.12× | SLOWER |
| Practice | `cal.real.email` | Rust engine | 0.0062× | 0.0061–0.0062× | 3.85× | SLOWER |
| Practice | `cal.real.datetime` | Python engine | 0.0079× | 0.0077–0.0081× | 23.68× | SLOWER |
| Practice | `cal.real.datetime` | Native C engine | 0.9356× | 0.8650–1.0009× | 0.09× | — |
| Practice | `cal.real.datetime` | Rust engine | 0.0164× | 0.0161–0.0168× | 3.49× | SLOWER |
| Practice | `cal.real.version` | Python engine | 0.0110× | 0.0109–0.0110× | 22.95× | SLOWER |
| Practice | `cal.real.version` | Native C engine | 1.3910× | 1.2108–1.5300× | 0.00× | FASTER |
| Practice | `cal.real.version` | Rust engine | 0.0286× | 0.0282–0.0290× | 3.46× | SLOWER |
| Practice | `cal.real.uuid` | Python engine | 0.0065× | 0.0064–0.0066× | 18.66× | SLOWER |
| Practice | `cal.real.uuid` | Native C engine | 0.8827× | 0.8743–0.8907× | 0.07× | — |
| Practice | `cal.real.uuid` | Rust engine | 0.0138× | 0.0137–0.0139× | 3.96× | SLOWER |
| Practice | `cal.real.ip` | Python engine | 0.0083× | 0.0082–0.0084× | 29.12× | SLOWER |
| Practice | `cal.real.ip` | Native C engine | 1.0434× | 1.0311–1.0558× | 0.07× | FASTER |
| Practice | `cal.real.ip` | Rust engine | 0.0270× | 0.0267–0.0273× | 3.02× | SLOWER |
| Practice | `cal.real.path` | Python engine | 0.0058× | 0.0058–0.0060× | 30.63× | SLOWER |
| Practice | `cal.real.path` | Native C engine | 0.9602× | 0.9224–0.9947× | 0.12× | — |
| Practice | `cal.real.path` | Rust engine | 0.0109× | 0.0107–0.0111× | 3.60× | SLOWER |
| Practice | `cal.real.config` | Python engine | 0.0087× | 0.0085–0.0088× | 16.04× | SLOWER |
| Practice | `cal.real.config` | Native C engine | 1.0870× | 1.0425–1.1244× | 0.35× | FASTER |
| Practice | `cal.real.config` | Rust engine | 0.0174× | 0.0170–0.0178× | 2.32× | SLOWER |
| Practice | `cal.real.comments` | Python engine | 0.0065× | 0.0062–0.0069× | 11.73× | SLOWER |
| Practice | `cal.real.comments` | Native C engine | 0.7396× | 0.7242–0.7618× | 0.14× | SLOWER |
| Practice | `cal.real.comments` | Rust engine | 0.0040× | 0.0038–0.0043× | 3.74× | SLOWER |
| Practice | `cal.real.whitespace` | Python engine | 0.0070× | 0.0069–0.0072× | 8.36× | SLOWER |
| Practice | `cal.real.whitespace` | Native C engine | 1.2784× | 1.1456–1.3582× | 0.14× | FASTER |
| Practice | `cal.real.whitespace` | Rust engine | 0.0078× | 0.0076–0.0080× | 2.79× | SLOWER |
| Practice | `cal.real.lines` | Python engine | 0.0093× | 0.0091–0.0095× | 14.09× | SLOWER |
| Practice | `cal.real.lines` | Native C engine | 1.5545× | 1.5297–1.5824× | 0.15× | FASTER |
| Practice | `cal.real.lines` | Rust engine | 0.0092× | 0.0090–0.0094× | 2.83× | SLOWER |
| Practice | `cal.real.markup` | Python engine | 0.0045× | 0.0045–0.0046× | 13.23× | SLOWER |
| Practice | `cal.real.markup` | Native C engine | 0.6273× | 0.6242–0.6305× | 0.10× | SLOWER |
| Practice | `cal.real.markup` | Rust engine | 0.0038× | 0.0037–0.0038× | 4.19× | SLOWER |
| Practice | `cal.real.quotes` | Python engine | 0.0042× | 0.0041–0.0042× | 18.83× | SLOWER |
| Practice | `cal.real.quotes` | Native C engine | 0.6732× | 0.6391–0.6947× | 0.10× | SLOWER |
| Practice | `cal.real.quotes` | Rust engine | 0.0073× | 0.0073–0.0074× | 3.83× | SLOWER |
| Practice | `cal.real.csv` | Python engine | 0.0050× | 0.0048–0.0052× | 19.83× | SLOWER |
| Practice | `cal.real.csv` | Native C engine | 0.4013× | 0.3720–0.4354× | 0.32× | SLOWER |
| Practice | `cal.real.csv` | Rust engine | 0.0109× | 0.0106–0.0116× | 2.97× | SLOWER |
| Practice | `cal.branch.prefix` | Python engine | 0.0093× | 0.0092–0.0094× | 12.65× | SLOWER |
| Practice | `cal.branch.prefix` | Native C engine | 0.7923× | 0.7852–0.7991× | 0.07× | SLOWER |
| Practice | `cal.branch.prefix` | Rust engine | 0.0131× | 0.0130–0.0133× | 3.37× | SLOWER |
| Practice | `cal.branch.miss` | Python engine | 0.0009× | 0.0009–0.0009× | 83.64× | SLOWER |
| Practice | `cal.branch.miss` | Native C engine | 0.4349× | 0.4278–0.4408× | 0.00× | SLOWER |
| Practice | `cal.branch.miss` | Rust engine | 0.0126× | 0.0125–0.0128× | 4.25× | SLOWER |
| Practice | `cal.repeat.nested` | Python engine | 0.0100× | 0.0099–0.0102× | 15.24× | SLOWER |
| Practice | `cal.repeat.nested` | Native C engine | 1.1488× | 1.1270–1.1696× | 0.64× | FASTER |
| Practice | `cal.repeat.nested` | Rust engine | 0.0236× | 0.0232–0.0239× | 1.57× | SLOWER |
| Practice | `cal.lines.records` | Python engine | 0.0088× | 0.0084–0.0094× | 14.74× | SLOWER |
| Practice | `cal.lines.records` | Native C engine | 1.0557× | 1.0086–1.1253× | 0.36× | FASTER |
| Practice | `cal.lines.records` | Rust engine | 0.0076× | 0.0073–0.0081× | 2.56× | SLOWER |
| Practice | `cal.block.dotall` | Python engine | 0.0067× | 0.0066–0.0069× | 17.13× | SLOWER |
| Practice | `cal.block.dotall` | Native C engine | 0.6672× | 0.6211–0.7036× | 0.08× | SLOWER |
| Practice | `cal.block.dotall` | Rust engine | 0.0136× | 0.0133–0.0140× | 3.97× | SLOWER |
| Practice | `cal.pattern.verbose` | Python engine | 0.0042× | 0.0041–0.0044× | 14.85× | SLOWER |
| Practice | `cal.pattern.verbose` | Native C engine | 0.6753× | 0.6245–0.7226× | 0.09× | SLOWER |
| Practice | `cal.pattern.verbose` | Rust engine | 0.0207× | 0.0200–0.0218× | 3.43× | SLOWER |
| Practice | `cal.mode.ascii` | Python engine | 0.0057× | 0.0055–0.0060× | 7.27× | SLOWER |
| Practice | `cal.mode.ascii` | Native C engine | 1.0858× | 1.0505–1.1457× | 0.13× | FASTER |
| Practice | `cal.mode.ascii` | Rust engine | 0.0099× | 0.0095–0.0105× | 3.04× | SLOWER |
| Practice | `cal.mode.casefold` | Python engine | 0.0082× | 0.0082–0.0083× | 5.52× | SLOWER |
| Practice | `cal.mode.casefold` | Native C engine | 1.3780× | 1.3610–1.3963× | 0.20× | FASTER |
| Practice | `cal.mode.casefold` | Rust engine | 0.0088× | 0.0087–0.0089× | 2.90× | SLOWER |
| Practice | `cal.mode.astral` | Python engine | 0.0095× | 0.0094–0.0096× | 7.05× | SLOWER |
| Practice | `cal.mode.astral` | Native C engine | 1.6256× | 1.6065–1.6512× | 0.25× | FASTER |
| Practice | `cal.mode.astral` | Rust engine | 0.0093× | 0.0091–0.0094× | 2.76× | SLOWER |
| Practice | `cal.look.negative-ahead` | Python engine | 0.0037× | 0.0037–0.0037× | 15.69× | SLOWER |
| Practice | `cal.look.negative-ahead` | Native C engine | 0.4230× | 0.4013–0.4408× | 0.53× | SLOWER |
| Practice | `cal.look.negative-ahead` | Rust engine | 0.0073× | 0.0072–0.0073× | 3.46× | SLOWER |
| Practice | `cal.look.negative-behind` | Python engine | 0.0068× | 0.0067–0.0071× | 12.65× | SLOWER |
| Practice | `cal.look.negative-behind` | Native C engine | 1.1112× | 1.0758–1.1355× | 0.10× | FASTER |
| Practice | `cal.look.negative-behind` | Rust engine | 0.0103× | 0.0101–0.0107× | 3.19× | SLOWER |
| Practice | `cal.bytes.replace` | Python engine | 0.0165× | 0.0164–0.0167× | 9.71× | SLOWER |
| Practice | `cal.bytes.replace` | Native C engine | 1.0180× | 1.0048–1.0314× | 1.18× | FASTER |
| Practice | `cal.bytes.replace` | Rust engine | 0.0158× | 0.0155–0.0161× | 2.52× | SLOWER |
| Practice | `cal.bytes.scan` | Python engine | 0.0119× | 0.0116–0.0124× | 8.55× | SLOWER |
| Practice | `cal.bytes.scan` | Native C engine | 1.2557× | 1.1545–1.3513× | 0.38× | FASTER |
| Practice | `cal.bytes.scan` | Rust engine | 0.0095× | 0.0093–0.0099× | 1.87× | SLOWER |
| Practice | `cal.compile.complex` | Python engine | 1.7591× | 1.6927–1.8211× | 0.39× | FASTER |
| Practice | `cal.compile.complex` | Native C engine | 1.4047× | 1.3743–1.4393× | 1.64× | FASTER |
| Practice | `cal.compile.complex` | Rust engine | 1.7266× | 1.6731–1.7762× | 0.52× | FASTER |
| Practice | `cal.module.replace` | Python engine | 0.0212× | 0.0204–0.0219× | 10.12× | SLOWER |
| Practice | `cal.module.replace` | Native C engine | 1.2498× | 1.2205–1.2906× | 0.04× | FASTER |
| Practice | `cal.module.replace` | Rust engine | 0.0202× | 0.0193–0.0210× | 2.52× | SLOWER |
| Practice | `cal.zero.boundary` | Python engine | 0.0077× | 0.0075–0.0079× | 13.81× | SLOWER |
| Practice | `cal.zero.boundary` | Native C engine | 0.5133× | 0.4939–0.5341× | 0.62× | SLOWER |
| Practice | `cal.zero.boundary` | Rust engine | 0.0134× | 0.0131–0.0138× | 1.69× | SLOWER |
| Practice | `cal.dense.iter` | Python engine | 0.0161× | 0.0158–0.0165× | 4.92× | SLOWER |
| Practice | `cal.dense.iter` | Native C engine | 1.3749× | 1.3280–1.4223× | 0.51× | FASTER |
| Practice | `cal.dense.iter` | Rust engine | 0.0083× | 0.0081–0.0084× | 1.49× | SLOWER |
| Practice | `cal.capture.optional` | Python engine | 0.0105× | 0.0101–0.0109× | 14.26× | SLOWER |
| Practice | `cal.capture.optional` | Native C engine | 1.1921× | 1.1624–1.2395× | 0.18× | FASTER |
| Practice | `cal.capture.optional` | Rust engine | 0.0091× | 0.0089–0.0094× | 2.79× | SLOWER |
| Practice | `cal.split.limited` | Python engine | 0.0066× | 0.0064–0.0067× | 7.47× | SLOWER |
| Practice | `cal.split.limited` | Native C engine | 1.1596× | 1.1417–1.1766× | 0.19× | FASTER |
| Practice | `cal.split.limited` | Rust engine | 0.0076× | 0.0075–0.0078× | 2.82× | SLOWER |
| Practice | `cal.replace.limited` | Python engine | 0.0136× | 0.0134–0.0138× | 6.04× | SLOWER |
| Practice | `cal.replace.limited` | Native C engine | 1.2767× | 1.2608–1.2934× | 0.15× | FASTER |
| Practice | `cal.replace.limited` | Rust engine | 0.0099× | 0.0097–0.0100× | 2.90× | SLOWER |
| Practice | `cal.bytes.view-long` | Python engine | 0.0066× | 0.0065–0.0067× | 48.64× | SLOWER |
| Practice | `cal.bytes.view-long` | Native C engine | 1.3653× | 1.3374–1.3880× | 0.60× | FASTER |
| Practice | `cal.bytes.view-long` | Rust engine | 0.0009× | 0.0009–0.0010× | 5.61× | SLOWER |
| Practice | `cal.window.search` | Python engine | 0.0199× | 0.0194–0.0204× | 4.40× | SLOWER |
| Practice | `cal.window.search` | Native C engine | 1.0027× | 0.9832–1.0240× | 0.18× | — |
| Practice | `cal.window.search` | Rust engine | 0.0164× | 0.0161–0.0168× | 3.30× | SLOWER |
| Practice | `cal.window.findall` | Python engine | 0.0176× | 0.0170–0.0184× | 4.02× | SLOWER |
| Practice | `cal.window.findall` | Native C engine | 1.0854× | 1.0312–1.1466× | 0.23× | FASTER |
| Practice | `cal.window.findall` | Rust engine | 0.0081× | 0.0078–0.0084× | 3.01× | SLOWER |
| Practice | `cal.window.scanner` | Python engine | 0.0204× | 0.0164–0.0298× | 4.46× | SLOWER |
| Practice | `cal.window.scanner` | Native C engine | 1.2713× | 1.0586–1.8054× | 0.30× | FASTER |
| Practice | `cal.window.scanner` | Rust engine | 0.0115× | 0.0094–0.0165× | 2.20× | SLOWER |
| Practice | `cal.window.match` | Python engine | 0.0397× | 0.0365–0.0447× | 3.55× | SLOWER |
| Practice | `cal.window.match` | Native C engine | 1.0556× | 0.9310–1.2133× | 0.18× | — |
| Practice | `cal.window.match` | Rust engine | 0.0203× | 0.0187–0.0229× | 2.45× | SLOWER |
| Practice | `cal.literal.replace` | Python engine | 0.0063× | 0.0059–0.0068× | 41.75× | SLOWER |
| Practice | `cal.literal.replace` | Native C engine | 1.2663× | 1.1926–1.4085× | 0.53× | FASTER |
| Practice | `cal.literal.replace` | Rust engine | 0.0054× | 0.0051–0.0058× | 10.40× | SLOWER |
| Practice | `cal.template.repeat` | Python engine | 0.0183× | 0.0180–0.0188× | 6.29× | SLOWER |
| Practice | `cal.template.repeat` | Native C engine | 1.4362× | 1.4133–1.4684× | 0.15× | FASTER |
| Practice | `cal.template.repeat` | Rust engine | 0.0128× | 0.0126–0.0131× | 2.29× | SLOWER |
| Practice | `cal.match.miss` | Python engine | 0.0295× | 0.0289–0.0303× | 5.02× | SLOWER |
| Practice | `cal.match.miss` | Native C engine | 1.2300× | 1.2048–1.2644× | 0.00× | FASTER |
| Practice | `cal.match.miss` | Rust engine | 0.0084× | 0.0083–0.0087× | 4.00× | SLOWER |
| Practice | `cal.fullmatch.miss` | Python engine | 0.0173× | 0.0171–0.0174× | 11.09× | SLOWER |
| Practice | `cal.fullmatch.miss` | Native C engine | 1.3084× | 1.1912–1.3777× | 0.00× | FASTER |
| Practice | `cal.fullmatch.miss` | Rust engine | 0.0226× | 0.0224–0.0228× | 3.32× | SLOWER |
| Holdout | `hold.real.log` | Python engine | 0.0029× | 0.0028–0.0030× | 36.41× | SLOWER |
| Holdout | `hold.real.log` | Native C engine | 0.8494× | 0.7746–0.9146× | 0.33× | — |
| Holdout | `hold.real.log` | Rust engine | 0.0059× | 0.0056–0.0062× | 3.23× | SLOWER |
| Holdout | `hold.real.url` | Python engine | 0.0054× | 0.0053–0.0055× | 26.93× | SLOWER |
| Holdout | `hold.real.url` | Native C engine | 0.7969× | 0.7884–0.8053× | 0.11× | SLOWER |
| Holdout | `hold.real.url` | Rust engine | 0.0105× | 0.0104–0.0106× | 3.79× | SLOWER |
| Holdout | `hold.real.email` | Python engine | 0.0043× | 0.0042–0.0043× | 12.09× | SLOWER |
| Holdout | `hold.real.email` | Native C engine | 0.8488× | 0.8034–0.8936× | 0.12× | — |
| Holdout | `hold.real.email` | Rust engine | 0.0069× | 0.0069–0.0070× | 3.88× | SLOWER |
| Holdout | `hold.real.datetime` | Python engine | 0.0075× | 0.0074–0.0076× | 27.33× | SLOWER |
| Holdout | `hold.real.datetime` | Native C engine | 0.9667× | 0.8533–1.0557× | 0.09× | — |
| Holdout | `hold.real.datetime` | Rust engine | 0.0170× | 0.0166–0.0173× | 3.42× | SLOWER |
| Holdout | `hold.real.version` | Python engine | 0.0098× | 0.0094–0.0104× | 23.70× | SLOWER |
| Holdout | `hold.real.version` | Native C engine | 1.1640× | 1.1224–1.2398× | 0.06× | FASTER |
| Holdout | `hold.real.version` | Rust engine | 0.0220× | 0.0213–0.0233× | 3.01× | SLOWER |
| Holdout | `hold.real.uuid` | Python engine | 0.0064× | 0.0062–0.0067× | 18.05× | SLOWER |
| Holdout | `hold.real.uuid` | Native C engine | 0.8445× | 0.8159–0.8912× | 0.07× | — |
| Holdout | `hold.real.uuid` | Rust engine | 0.0136× | 0.0132–0.0143× | 3.95× | SLOWER |
| Holdout | `hold.real.ip` | Python engine | 0.0088× | 0.0087–0.0089× | 30.05× | SLOWER |
| Holdout | `hold.real.ip` | Native C engine | 1.0683× | 1.0487–1.0897× | 0.07× | FASTER |
| Holdout | `hold.real.ip` | Rust engine | 0.0217× | 0.0213–0.0221× | 3.02× | SLOWER |
| Holdout | `hold.real.path` | Python engine | 0.0056× | 0.0056–0.0057× | 26.39× | SLOWER |
| Holdout | `hold.real.path` | Native C engine | 0.8868× | 0.8220–0.9370× | 0.12× | — |
| Holdout | `hold.real.path` | Rust engine | 0.0095× | 0.0093–0.0096× | 3.84× | SLOWER |
| Holdout | `hold.real.config` | Python engine | 0.0089× | 0.0087–0.0092× | 18.02× | SLOWER |
| Holdout | `hold.real.config` | Native C engine | 1.0883× | 1.0716–1.1081× | 0.35× | FASTER |
| Holdout | `hold.real.config` | Rust engine | 0.0156× | 0.0153–0.0161× | 2.32× | SLOWER |
| Holdout | `hold.real.comments` | Python engine | 0.0050× | 0.0048–0.0055× | 16.97× | SLOWER |
| Holdout | `hold.real.comments` | Native C engine | 0.7114× | 0.6783–0.7758× | 0.14× | SLOWER |
| Holdout | `hold.real.comments` | Rust engine | 0.0034× | 0.0033–0.0037× | 4.05× | SLOWER |
| Holdout | `hold.real.whitespace` | Python engine | 0.0074× | 0.0073–0.0076× | 8.45× | SLOWER |
| Holdout | `hold.real.whitespace` | Native C engine | 1.4155× | 1.3823–1.4527× | 0.14× | FASTER |
| Holdout | `hold.real.whitespace` | Rust engine | 0.0075× | 0.0073–0.0076× | 2.74× | SLOWER |
| Holdout | `hold.real.lines` | Python engine | 0.0100× | 0.0091–0.0112× | 13.22× | SLOWER |
| Holdout | `hold.real.lines` | Native C engine | 1.4232× | 1.2700–1.5534× | 0.14× | FASTER |
| Holdout | `hold.real.lines` | Rust engine | 0.0097× | 0.0093–0.0103× | 2.82× | SLOWER |
| Holdout | `hold.real.markup` | Python engine | 0.0052× | 0.0046–0.0062× | 14.16× | SLOWER |
| Holdout | `hold.real.markup` | Native C engine | 0.6910× | 0.6105–0.8145× | 0.13× | SLOWER |
| Holdout | `hold.real.markup` | Rust engine | 0.0034× | 0.0031–0.0037× | 4.34× | SLOWER |
| Holdout | `hold.real.quotes` | Python engine | 0.0041× | 0.0040–0.0041× | 18.87× | SLOWER |
| Holdout | `hold.real.quotes` | Native C engine | 0.6811× | 0.6742–0.6887× | 0.10× | SLOWER |
| Holdout | `hold.real.quotes` | Rust engine | 0.0071× | 0.0071–0.0072× | 3.58× | SLOWER |
| Holdout | `hold.real.csv` | Python engine | 0.0041× | 0.0040–0.0043× | 18.08× | SLOWER |
| Holdout | `hold.real.csv` | Native C engine | 0.3561× | 0.3496–0.3657× | 0.32× | SLOWER |
| Holdout | `hold.real.csv` | Rust engine | 0.0095× | 0.0093–0.0099× | 3.21× | SLOWER |
| Holdout | `hold.branch.prefix` | Python engine | 0.0102× | 0.0101–0.0103× | 11.86× | SLOWER |
| Holdout | `hold.branch.prefix` | Native C engine | 0.8425× | 0.8314–0.8525× | 0.07× | — |
| Holdout | `hold.branch.prefix` | Rust engine | 0.0139× | 0.0137–0.0140× | 3.36× | SLOWER |
| Holdout | `hold.branch.miss` | Python engine | 0.0008× | 0.0008–0.0008× | 80.13× | SLOWER |
| Holdout | `hold.branch.miss` | Native C engine | 0.7097× | 0.6891–0.7245× | 0.00× | SLOWER |
| Holdout | `hold.branch.miss` | Rust engine | 0.0113× | 0.0112–0.0114× | 4.57× | SLOWER |
| Holdout | `hold.repeat.nested` | Python engine | 0.0102× | 0.0098–0.0110× | 15.24× | SLOWER |
| Holdout | `hold.repeat.nested` | Native C engine | 1.0765× | 1.0203–1.1663× | 0.64× | FASTER |
| Holdout | `hold.repeat.nested` | Rust engine | 0.0228× | 0.0217–0.0247× | 1.57× | SLOWER |
| Holdout | `hold.lines.records` | Python engine | 0.0083× | 0.0080–0.0086× | 14.74× | SLOWER |
| Holdout | `hold.lines.records` | Native C engine | 0.9871× | 0.9515–1.0229× | 0.36× | — |
| Holdout | `hold.lines.records` | Rust engine | 0.0073× | 0.0070–0.0076× | 2.55× | SLOWER |
| Holdout | `hold.block.dotall` | Python engine | 0.0064× | 0.0062–0.0065× | 18.13× | SLOWER |
| Holdout | `hold.block.dotall` | Native C engine | 0.6575× | 0.6532–0.6627× | 0.08× | SLOWER |
| Holdout | `hold.block.dotall` | Rust engine | 0.0133× | 0.0132–0.0134× | 4.00× | SLOWER |
| Holdout | `hold.pattern.verbose` | Python engine | 0.0038× | 0.0036–0.0041× | 15.91× | SLOWER |
| Holdout | `hold.pattern.verbose` | Native C engine | 0.6704× | 0.6277–0.7363× | 0.09× | SLOWER |
| Holdout | `hold.pattern.verbose` | Rust engine | 0.0267× | 0.0252–0.0292× | 3.45× | SLOWER |
| Holdout | `hold.mode.ascii` | Python engine | 0.0053× | 0.0052–0.0054× | 7.82× | SLOWER |
| Holdout | `hold.mode.ascii` | Native C engine | 1.0641× | 1.0227–1.1037× | 0.21× | FASTER |
| Holdout | `hold.mode.ascii` | Rust engine | 0.0078× | 0.0076–0.0080× | 3.02× | SLOWER |
| Holdout | `hold.mode.casefold` | Python engine | 0.0083× | 0.0077–0.0090× | 5.44× | SLOWER |
| Holdout | `hold.mode.casefold` | Native C engine | 1.3532× | 1.2310–1.4278× | 0.18× | FASTER |
| Holdout | `hold.mode.casefold` | Rust engine | 0.0107× | 0.0103–0.0115× | 2.93× | SLOWER |
| Holdout | `hold.mode.astral` | Python engine | 0.0096× | 0.0091–0.0105× | 7.06× | SLOWER |
| Holdout | `hold.mode.astral` | Native C engine | 1.4182× | 1.1995–1.5957× | 0.25× | FASTER |
| Holdout | `hold.mode.astral` | Rust engine | 0.0095× | 0.0091–0.0104× | 2.77× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Python engine | 0.0035× | 0.0035–0.0036× | 16.30× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Native C engine | 0.4193× | 0.4174–0.4215× | 0.53× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Rust engine | 0.0071× | 0.0070–0.0072× | 3.47× | SLOWER |
| Holdout | `hold.look.negative-behind` | Python engine | 0.0068× | 0.0067–0.0069× | 12.65× | SLOWER |
| Holdout | `hold.look.negative-behind` | Native C engine | 1.1410× | 1.1250–1.1646× | 0.10× | FASTER |
| Holdout | `hold.look.negative-behind` | Rust engine | 0.0103× | 0.0102–0.0105× | 3.19× | SLOWER |
| Holdout | `hold.bytes.replace` | Python engine | 0.0161× | 0.0159–0.0163× | 9.71× | SLOWER |
| Holdout | `hold.bytes.replace` | Native C engine | 1.0032× | 0.9815–1.0269× | 1.16× | — |
| Holdout | `hold.bytes.replace` | Rust engine | 0.0153× | 0.0149–0.0156× | 2.52× | SLOWER |
| Holdout | `hold.bytes.scan` | Python engine | 0.0119× | 0.0116–0.0125× | 8.55× | SLOWER |
| Holdout | `hold.bytes.scan` | Native C engine | 1.2655× | 1.2288–1.3250× | 0.38× | FASTER |
| Holdout | `hold.bytes.scan` | Rust engine | 0.0094× | 0.0091–0.0098× | 1.87× | SLOWER |
| Holdout | `hold.compile.complex` | Python engine | 1.8496× | 1.8311–1.8698× | 0.37× | FASTER |
| Holdout | `hold.compile.complex` | Native C engine | 1.4306× | 1.4160–1.4444× | 1.67× | FASTER |
| Holdout | `hold.compile.complex` | Rust engine | 1.5746× | 1.5589–1.5914× | 0.55× | FASTER |
| Holdout | `hold.module.replace` | Python engine | 0.0214× | 0.0211–0.0216× | 10.12× | SLOWER |
| Holdout | `hold.module.replace` | Native C engine | 1.2126× | 1.1990–1.2284× | 0.04× | FASTER |
| Holdout | `hold.module.replace` | Rust engine | 0.0198× | 0.0190–0.0204× | 2.52× | SLOWER |
| Holdout | `hold.zero.boundary` | Python engine | 0.0084× | 0.0082–0.0088× | 8.20× | SLOWER |
| Holdout | `hold.zero.boundary` | Native C engine | 0.5572× | 0.5457–0.5703× | 0.62× | SLOWER |
| Holdout | `hold.zero.boundary` | Rust engine | 0.0144× | 0.0140–0.0151× | 1.67× | SLOWER |
| Holdout | `hold.dense.iter` | Python engine | 0.0160× | 0.0156–0.0165× | 4.92× | SLOWER |
| Holdout | `hold.dense.iter` | Native C engine | 1.3624× | 1.3293–1.3978× | 0.51× | FASTER |
| Holdout | `hold.dense.iter` | Rust engine | 0.0082× | 0.0080–0.0084× | 1.50× | SLOWER |
| Holdout | `hold.capture.optional` | Python engine | 0.0102× | 0.0100–0.0105× | 14.26× | SLOWER |
| Holdout | `hold.capture.optional` | Native C engine | 1.1104× | 1.0853–1.1464× | 0.18× | FASTER |
| Holdout | `hold.capture.optional` | Rust engine | 0.0086× | 0.0084–0.0088× | 2.79× | SLOWER |
| Holdout | `hold.split.limited` | Python engine | 0.0062× | 0.0061–0.0063× | 7.46× | SLOWER |
| Holdout | `hold.split.limited` | Native C engine | 1.1343× | 1.1073–1.1558× | 0.19× | FASTER |
| Holdout | `hold.split.limited` | Rust engine | 0.0072× | 0.0071–0.0073× | 2.83× | SLOWER |
| Holdout | `hold.replace.limited` | Python engine | 0.0130× | 0.0128–0.0132× | 6.04× | SLOWER |
| Holdout | `hold.replace.limited` | Native C engine | 1.1494× | 1.1297–1.1648× | 0.15× | FASTER |
| Holdout | `hold.replace.limited` | Rust engine | 0.0090× | 0.0089–0.0091× | 2.90× | SLOWER |
| Holdout | `hold.bytes.view-long` | Python engine | 0.0066× | 0.0065–0.0068× | 48.64× | SLOWER |
| Holdout | `hold.bytes.view-long` | Native C engine | 1.3711× | 1.3255–1.4132× | 0.60× | FASTER |
| Holdout | `hold.bytes.view-long` | Rust engine | 0.0009× | 0.0009–0.0010× | 5.61× | SLOWER |
| Holdout | `hold.window.search` | Python engine | 0.0196× | 0.0190–0.0204× | 4.40× | SLOWER |
| Holdout | `hold.window.search` | Native C engine | 1.0035× | 0.9710–1.0467× | 0.18× | — |
| Holdout | `hold.window.search` | Rust engine | 0.0154× | 0.0149–0.0161× | 3.32× | SLOWER |
| Holdout | `hold.window.findall` | Python engine | 0.0175× | 0.0173–0.0176× | 4.03× | SLOWER |
| Holdout | `hold.window.findall` | Native C engine | 0.9664× | 0.9499–0.9834× | 0.22× | — |
| Holdout | `hold.window.findall` | Rust engine | 0.0074× | 0.0072–0.0075× | 2.86× | SLOWER |
| Holdout | `hold.window.scanner` | Python engine | 0.0177× | 0.0173–0.0180× | 4.46× | SLOWER |
| Holdout | `hold.window.scanner` | Native C engine | 1.0796× | 1.0576–1.1012× | 0.30× | FASTER |
| Holdout | `hold.window.scanner` | Rust engine | 0.0094× | 0.0091–0.0096× | 2.20× | SLOWER |
| Holdout | `hold.window.match` | Python engine | 0.0342× | 0.0337–0.0347× | 3.55× | SLOWER |
| Holdout | `hold.window.match` | Native C engine | 0.9814× | 0.9548–1.0041× | 0.18× | — |
| Holdout | `hold.window.match` | Rust engine | 0.0181× | 0.0175–0.0186× | 2.46× | SLOWER |
| Holdout | `hold.literal.replace` | Python engine | 0.0066× | 0.0062–0.0071× | 38.88× | SLOWER |
| Holdout | `hold.literal.replace` | Native C engine | 1.2287× | 1.1577–1.3266× | 0.52× | FASTER |
| Holdout | `hold.literal.replace` | Rust engine | 0.0057× | 0.0054–0.0062× | 10.36× | SLOWER |
| Holdout | `hold.template.repeat` | Python engine | 0.0185× | 0.0184–0.0186× | 6.32× | SLOWER |
| Holdout | `hold.template.repeat` | Native C engine | 1.4345× | 1.4245–1.4436× | 0.14× | FASTER |
| Holdout | `hold.template.repeat` | Rust engine | 0.0137× | 0.0136–0.0138× | 2.28× | SLOWER |
| Holdout | `hold.match.miss` | Python engine | 0.0293× | 0.0290–0.0297× | 5.02× | SLOWER |
| Holdout | `hold.match.miss` | Native C engine | 1.2002× | 1.1729–1.2208× | 0.00× | FASTER |
| Holdout | `hold.match.miss` | Rust engine | 0.0078× | 0.0077–0.0078× | 4.20× | SLOWER |
| Holdout | `hold.fullmatch.miss` | Python engine | 0.0190× | 0.0180–0.0208× | 11.09× | SLOWER |
| Holdout | `hold.fullmatch.miss` | Native C engine | 1.5001× | 1.4276–1.6393× | 0.00× | FASTER |
| Holdout | `hold.fullmatch.miss` | Rust engine | 0.0246× | 0.0228–0.0272× | 3.31× | SLOWER |

## Large slowdowns

- Python engine: `cal.search.literal.hit` (0.007×), `cal.search.literal.miss` (0.002×), `cal.search.long-boundary` (0.000×), `cal.search.class-anchor` (0.011×), `cal.match.prefix` (0.025×), `cal.fullmatch.structured` (0.013×), `cal.search.look-capture` (0.008×), `cal.findall.tokens` (0.011×), `cal.finditer.groups` (0.013×), `cal.split.capture` (0.010×), `cal.sub.template` (0.016×), `cal.subn.callable` (0.024×), `cal.bytes.tokens` (0.007×), `cal.unicode.words` (0.006×), `cal.cold.compile-search` (0.293×), `cal.module.warm` (0.011×), `cal.empty.finditer` (0.010×), `cal.backref.fullmatch` (0.019×), `cal.conditional.match` (0.018×), `cal.atomic.search` (0.010×), `cal.byteslike.findall` (0.011×), `cal.unicode-name.search` (0.015×), `cal.ignorecase.findall` (0.008×), `cal.many.split` (0.012×), `cal.scanner.search` (0.013×), `cal.match.surface` (0.014×), `hold.search.literal.hit` (0.007×), `hold.search.literal.miss` (0.002×), `hold.search.long-boundary` (0.000×), `hold.search.class-anchor` (0.010×), `hold.match.prefix` (0.024×), `hold.fullmatch.structured` (0.012×), `hold.search.look-capture` (0.010×), `hold.findall.tokens` (0.011×), `hold.finditer.groups` (0.013×), `hold.split.capture` (0.010×), `hold.sub.template` (0.016×), `hold.subn.callable` (0.028×), `hold.bytes.tokens` (0.010×), `hold.unicode.words` (0.009×), `hold.cold.compile-search` (0.492×), `hold.module.warm` (0.020×), `hold.empty.finditer` (0.009×), `hold.backref.fullmatch` (0.018×), `hold.conditional.match` (0.019×), `hold.atomic.search` (0.011×), `hold.byteslike.findall` (0.012×), `hold.unicode-name.search` (0.014×), `hold.ignorecase.findall` (0.008×), `hold.many.split` (0.013×), `hold.scanner.search` (0.014×), `hold.match.surface` (0.022×), `cal.real.log` (0.003×), `cal.real.url` (0.007×), `cal.real.email` (0.006×), `cal.real.datetime` (0.008×), `cal.real.version` (0.011×), `cal.real.uuid` (0.007×), `cal.real.ip` (0.008×), `cal.real.path` (0.006×), `cal.real.config` (0.009×), `cal.real.comments` (0.006×), `cal.real.whitespace` (0.007×), `cal.real.lines` (0.009×), `cal.real.markup` (0.005×), `cal.real.quotes` (0.004×), `cal.real.csv` (0.005×), `cal.branch.prefix` (0.009×), `cal.branch.miss` (0.001×), `cal.repeat.nested` (0.010×), `cal.lines.records` (0.009×), `cal.block.dotall` (0.007×), `cal.pattern.verbose` (0.004×), `cal.mode.ascii` (0.006×), `cal.mode.casefold` (0.008×), `cal.mode.astral` (0.009×), `cal.look.negative-ahead` (0.004×), `cal.look.negative-behind` (0.007×), `cal.bytes.replace` (0.017×), `cal.bytes.scan` (0.012×), `cal.module.replace` (0.021×), `cal.zero.boundary` (0.008×), `cal.dense.iter` (0.016×), `cal.capture.optional` (0.010×), `cal.split.limited` (0.007×), `cal.replace.limited` (0.014×), `cal.bytes.view-long` (0.007×), `cal.window.search` (0.020×), `cal.window.findall` (0.018×), `cal.window.scanner` (0.020×), `cal.window.match` (0.040×), `cal.literal.replace` (0.006×), `cal.template.repeat` (0.018×), `cal.match.miss` (0.030×), `cal.fullmatch.miss` (0.017×), `hold.real.log` (0.003×), `hold.real.url` (0.005×), `hold.real.email` (0.004×), `hold.real.datetime` (0.007×), `hold.real.version` (0.010×), `hold.real.uuid` (0.006×), `hold.real.ip` (0.009×), `hold.real.path` (0.006×), `hold.real.config` (0.009×), `hold.real.comments` (0.005×), `hold.real.whitespace` (0.007×), `hold.real.lines` (0.010×), `hold.real.markup` (0.005×), `hold.real.quotes` (0.004×), `hold.real.csv` (0.004×), `hold.branch.prefix` (0.010×), `hold.branch.miss` (0.001×), `hold.repeat.nested` (0.010×), `hold.lines.records` (0.008×), `hold.block.dotall` (0.006×), `hold.pattern.verbose` (0.004×), `hold.mode.ascii` (0.005×), `hold.mode.casefold` (0.008×), `hold.mode.astral` (0.010×), `hold.look.negative-ahead` (0.004×), `hold.look.negative-behind` (0.007×), `hold.bytes.replace` (0.016×), `hold.bytes.scan` (0.012×), `hold.module.replace` (0.021×), `hold.zero.boundary` (0.008×), `hold.dense.iter` (0.016×), `hold.capture.optional` (0.010×), `hold.split.limited` (0.006×), `hold.replace.limited` (0.013×), `hold.bytes.view-long` (0.007×), `hold.window.search` (0.020×), `hold.window.findall` (0.017×), `hold.window.scanner` (0.018×), `hold.window.match` (0.034×), `hold.literal.replace` (0.007×), `hold.template.repeat` (0.019×), `hold.match.miss` (0.029×), `hold.fullmatch.miss` (0.019×).
- Rust engine: `cal.search.literal.hit` (0.009×), `cal.search.literal.miss` (0.006×), `cal.search.long-boundary` (0.001×), `cal.search.class-anchor` (0.015×), `cal.match.prefix` (0.016×), `cal.fullmatch.structured` (0.019×), `cal.search.look-capture` (0.016×), `cal.findall.tokens` (0.004×), `cal.finditer.groups` (0.010×), `cal.split.capture` (0.007×), `cal.sub.template` (0.015×), `cal.subn.callable` (0.020×), `cal.bytes.tokens` (0.005×), `cal.unicode.words` (0.010×), `cal.cold.compile-search` (0.709×), `cal.module.warm` (0.031×), `cal.empty.finditer` (0.021×), `cal.backref.fullmatch` (0.019×), `cal.conditional.match` (0.016×), `cal.atomic.search` (0.019×), `cal.byteslike.findall` (0.008×), `cal.unicode-name.search` (0.020×), `cal.ignorecase.findall` (0.009×), `cal.many.split` (0.004×), `cal.scanner.search` (0.009×), `cal.match.surface` (0.049×), `hold.search.literal.hit` (0.009×), `hold.search.literal.miss` (0.006×), `hold.search.long-boundary` (0.001×), `hold.search.class-anchor` (0.013×), `hold.match.prefix` (0.016×), `hold.fullmatch.structured` (0.020×), `hold.search.look-capture` (0.018×), `hold.findall.tokens` (0.006×), `hold.finditer.groups` (0.009×), `hold.split.capture` (0.007×), `hold.sub.template` (0.015×), `hold.subn.callable` (0.022×), `hold.bytes.tokens` (0.008×), `hold.unicode.words` (0.012×), `hold.cold.compile-search` (0.752×), `hold.module.warm` (0.032×), `hold.empty.finditer` (0.022×), `hold.backref.fullmatch` (0.019×), `hold.conditional.match` (0.019×), `hold.atomic.search` (0.023×), `hold.byteslike.findall` (0.009×), `hold.unicode-name.search` (0.021×), `hold.ignorecase.findall` (0.010×), `hold.many.split` (0.005×), `hold.scanner.search` (0.010×), `hold.match.surface` (0.043×), `cal.real.log` (0.006×), `cal.real.url` (0.012×), `cal.real.email` (0.006×), `cal.real.datetime` (0.016×), `cal.real.version` (0.029×), `cal.real.uuid` (0.014×), `cal.real.ip` (0.027×), `cal.real.path` (0.011×), `cal.real.config` (0.017×), `cal.real.comments` (0.004×), `cal.real.whitespace` (0.008×), `cal.real.lines` (0.009×), `cal.real.markup` (0.004×), `cal.real.quotes` (0.007×), `cal.real.csv` (0.011×), `cal.branch.prefix` (0.013×), `cal.branch.miss` (0.013×), `cal.repeat.nested` (0.024×), `cal.lines.records` (0.008×), `cal.block.dotall` (0.014×), `cal.pattern.verbose` (0.021×), `cal.mode.ascii` (0.010×), `cal.mode.casefold` (0.009×), `cal.mode.astral` (0.009×), `cal.look.negative-ahead` (0.007×), `cal.look.negative-behind` (0.010×), `cal.bytes.replace` (0.016×), `cal.bytes.scan` (0.010×), `cal.module.replace` (0.020×), `cal.zero.boundary` (0.013×), `cal.dense.iter` (0.008×), `cal.capture.optional` (0.009×), `cal.split.limited` (0.008×), `cal.replace.limited` (0.010×), `cal.bytes.view-long` (0.001×), `cal.window.search` (0.016×), `cal.window.findall` (0.008×), `cal.window.scanner` (0.012×), `cal.window.match` (0.020×), `cal.literal.replace` (0.005×), `cal.template.repeat` (0.013×), `cal.match.miss` (0.008×), `cal.fullmatch.miss` (0.023×), `hold.real.log` (0.006×), `hold.real.url` (0.010×), `hold.real.email` (0.007×), `hold.real.datetime` (0.017×), `hold.real.version` (0.022×), `hold.real.uuid` (0.014×), `hold.real.ip` (0.022×), `hold.real.path` (0.009×), `hold.real.config` (0.016×), `hold.real.comments` (0.003×), `hold.real.whitespace` (0.007×), `hold.real.lines` (0.010×), `hold.real.markup` (0.003×), `hold.real.quotes` (0.007×), `hold.real.csv` (0.010×), `hold.branch.prefix` (0.014×), `hold.branch.miss` (0.011×), `hold.repeat.nested` (0.023×), `hold.lines.records` (0.007×), `hold.block.dotall` (0.013×), `hold.pattern.verbose` (0.027×), `hold.mode.ascii` (0.008×), `hold.mode.casefold` (0.011×), `hold.mode.astral` (0.010×), `hold.look.negative-ahead` (0.007×), `hold.look.negative-behind` (0.010×), `hold.bytes.replace` (0.015×), `hold.bytes.scan` (0.009×), `hold.module.replace` (0.020×), `hold.zero.boundary` (0.014×), `hold.dense.iter` (0.008×), `hold.capture.optional` (0.009×), `hold.split.limited` (0.007×), `hold.replace.limited` (0.009×), `hold.bytes.view-long` (0.001×), `hold.window.search` (0.015×), `hold.window.findall` (0.007×), `hold.window.scanner` (0.009×), `hold.window.match` (0.018×), `hold.literal.replace` (0.006×), `hold.template.repeat` (0.014×), `hold.match.miss` (0.008×), `hold.fullmatch.miss` (0.025×).
- Native C engine: `cal.cold.compile-search` (0.749×), `cal.empty.finditer` (0.667×), `hold.empty.finditer` (0.656×), `cal.real.email` (0.690×), `cal.real.comments` (0.740×), `cal.real.markup` (0.627×), `cal.real.quotes` (0.673×), `cal.real.csv` (0.401×), `cal.branch.prefix` (0.792×), `cal.branch.miss` (0.435×), `cal.block.dotall` (0.667×), `cal.pattern.verbose` (0.675×), `cal.look.negative-ahead` (0.423×), `cal.zero.boundary` (0.513×), `hold.real.url` (0.797×), `hold.real.comments` (0.711×), `hold.real.markup` (0.691×), `hold.real.quotes` (0.681×), `hold.real.csv` (0.356×), `hold.branch.miss` (0.710×), `hold.block.dotall` (0.657×), `hold.pattern.verbose` (0.670×), `hold.look.negative-ahead` (0.419×), `hold.zero.boundary` (0.557×).

The Python engine performs matching work in Python, and the Rust engine repeatedly prepares data and crosses the Python/Rust boundary; both costs dominate short tasks. Native-C losses expose specific boundary and general-path costs:
- Empty matches and controlled branches use the general backtracking/iterator path and construct more match state.
- Everyday log, address, path, comment, markup, quote, and comma-separated-field tasks combine repeated classes, captures, or lookarounds; they take the general native backtracking path instead of its compact single-pass path.
- Searches across many alternative words still test the remaining branches when a possible prefix survives; the native one/two-character start filter removes impossible positions but does not build a full shared-prefix trie.
- Structured repeated paths, multi-line blocks, and readable formatted fields require general repeat/capture backtracking, which carries more state than the simple literal and single-character fast paths.
- Excluded-prefix and tagged-word searches evaluate a negative lookaround for each possible match, so the native executor repeats assertion work while scanning.
- Word/separator-position iteration and limited mixed-separator splits repeatedly use the general iterator or whitespace-backtracking path; each small match pays state and result-construction costs.

No loss is removed from the denominator or hidden from the charts.
