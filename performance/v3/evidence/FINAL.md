# Final correctness-gated performance result

All 7488 raw timing rows, 432 engine/task results, and 276 large slowdowns are retained. Raw SHA-256: `7e8872eec672c5cf2a285ec97dc21dae04a5b3372016c7404cf3c70517c2f6e3`.

## At a glance

The holdout tasks were kept separate from tuning. **1× means the same speed as Python `re`; higher is faster.** A result is clearly faster only when its measured range stays above 1×. A large slowdown means more than 20% slower.

| Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: | ---: |
| Native C engine | **1.5572×** | 1.5475–1.5670× | 70/72 | 0/72 |
| Rust engine | **0.0136×** | 0.0136–0.0137× | 2/72 | 69/72 |
| Python engine | **0.0115×** | 0.0114–0.0115× | 2/72 | 69/72 |

## Overall results

| Task set | Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |
| --- | --- | ---: | ---: | ---: | ---: |
| Practice | Python engine | 0.0113× | 0.0113–0.0114× | 2/72 | 69 |
| Practice | Native C engine | 1.4954× | 1.4867–1.5043× | 66/72 | 0 |
| Practice | Rust engine | 0.0137× | 0.0136–0.0137× | 2/72 | 69 |
| Holdout | Python engine | 0.0115× | 0.0114–0.0115× | 2/72 | 69 |
| Holdout | Native C engine | 1.5572× | 1.5475–1.5670× | 70/72 | 0 |
| Holdout | Rust engine | 0.0136× | 0.0136–0.0137× | 2/72 | 69 |
| All | Python engine | 0.0114× | 0.0114–0.0114× | 4/144 | 138 |
| All | Native C engine | 1.5260× | 1.5195–1.5330× | 136/144 | 0 |
| All | Rust engine | 0.0136× | 0.0136–0.0137× | 4/144 | 138 |

## Every task

`FASTER` means the measured range stays above 1×. `SLOWER` means more than 20% slower. Memory compares median traced Python memory with Python `re`.

| Task set | Task | Engine | Speed | Measured range | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Practice | `cal.search.literal.hit` | Python engine | 0.0075× | 0.0073–0.0079× | 102.00× | SLOWER |
| Practice | `cal.search.literal.hit` | Native C engine | 1.1380× | 1.0931–1.2238× | 0.73× | FASTER |
| Practice | `cal.search.literal.hit` | Rust engine | 0.0089× | 0.0086–0.0096× | 34.03× | SLOWER |
| Practice | `cal.search.literal.miss` | Python engine | 0.0021× | 0.0021–0.0022× | 14408.00× | SLOWER |
| Practice | `cal.search.literal.miss` | Native C engine | 1.1117× | 1.0326–1.1576× | 0.00× | FASTER |
| Practice | `cal.search.literal.miss` | Rust engine | 0.0056× | 0.0055–0.0057× | 4375.00× | SLOWER |
| Practice | `cal.search.long-boundary` | Python engine | 0.0003× | 0.0003–0.0003× | 129.57× | SLOWER |
| Practice | `cal.search.long-boundary` | Native C engine | 12.4010× | 11.5165–13.4905× | 0.07× | FASTER |
| Practice | `cal.search.long-boundary` | Rust engine | 0.0010× | 0.0009–0.0010× | 140.03× | SLOWER |
| Practice | `cal.search.class-anchor` | Python engine | 0.0109× | 0.0107–0.0112× | 11.57× | SLOWER |
| Practice | `cal.search.class-anchor` | Native C engine | 1.2961× | 1.2775–1.3231× | 0.07× | FASTER |
| Practice | `cal.search.class-anchor` | Rust engine | 0.0143× | 0.0141–0.0147× | 3.36× | SLOWER |
| Practice | `cal.match.prefix` | Python engine | 0.0227× | 0.0224–0.0229× | 3.87× | SLOWER |
| Practice | `cal.match.prefix` | Native C engine | 1.2997× | 1.2886–1.3117× | 0.07× | FASTER |
| Practice | `cal.match.prefix` | Rust engine | 0.0146× | 0.0141–0.0149× | 2.89× | SLOWER |
| Practice | `cal.fullmatch.structured` | Python engine | 0.0123× | 0.0122–0.0124× | 12.07× | SLOWER |
| Practice | `cal.fullmatch.structured` | Native C engine | 1.5722× | 1.5506–1.5935× | 0.07× | FASTER |
| Practice | `cal.fullmatch.structured` | Rust engine | 0.0182× | 0.0180–0.0185× | 3.04× | SLOWER |
| Practice | `cal.search.look-capture` | Python engine | 0.0075× | 0.0074–0.0076× | 17.28× | SLOWER |
| Practice | `cal.search.look-capture` | Native C engine | 1.4817× | 1.4698–1.4932× | 0.08× | FASTER |
| Practice | `cal.search.look-capture` | Rust engine | 0.0160× | 0.0158–0.0162× | 3.29× | SLOWER |
| Practice | `cal.findall.tokens` | Python engine | 0.0104× | 0.0101–0.0109× | 7.14× | SLOWER |
| Practice | `cal.findall.tokens` | Native C engine | 1.3573× | 1.3116–1.4114× | 0.28× | FASTER |
| Practice | `cal.findall.tokens` | Rust engine | 0.0039× | 0.0038–0.0040× | 3.26× | SLOWER |
| Practice | `cal.finditer.groups` | Python engine | 0.0132× | 0.0127–0.0139× | 7.75× | SLOWER |
| Practice | `cal.finditer.groups` | Native C engine | 2.0735× | 1.9850–2.1721× | 0.41× | FASTER |
| Practice | `cal.finditer.groups` | Rust engine | 0.0100× | 0.0096–0.0105× | 1.91× | SLOWER |
| Practice | `cal.split.capture` | Python engine | 0.0098× | 0.0097–0.0100× | 11.37× | SLOWER |
| Practice | `cal.split.capture` | Native C engine | 1.8926× | 1.8638–1.9272× | 0.20× | FASTER |
| Practice | `cal.split.capture` | Rust engine | 0.0067× | 0.0066–0.0068× | 2.62× | SLOWER |
| Practice | `cal.sub.template` | Python engine | 0.0158× | 0.0156–0.0160× | 9.30× | SLOWER |
| Practice | `cal.sub.template` | Native C engine | 1.9870× | 1.7877–2.1059× | 0.12× | FASTER |
| Practice | `cal.sub.template` | Rust engine | 0.0147× | 0.0145–0.0149× | 2.39× | SLOWER |
| Practice | `cal.subn.callable` | Python engine | 0.0240× | 0.0222–0.0265× | 5.05× | SLOWER |
| Practice | `cal.subn.callable` | Native C engine | 1.1268× | 1.0305–1.1872× | 0.25× | FASTER |
| Practice | `cal.subn.callable` | Rust engine | 0.0198× | 0.0184–0.0217× | 2.56× | SLOWER |
| Practice | `cal.bytes.tokens` | Python engine | 0.0070× | 0.0069–0.0072× | 8.29× | SLOWER |
| Practice | `cal.bytes.tokens` | Native C engine | 1.1516× | 1.1432–1.1604× | 0.12× | FASTER |
| Practice | `cal.bytes.tokens` | Rust engine | 0.0053× | 0.0052–0.0054× | 3.43× | SLOWER |
| Practice | `cal.unicode.words` | Python engine | 0.0061× | 0.0061–0.0062× | 6.52× | SLOWER |
| Practice | `cal.unicode.words` | Native C engine | 0.9299× | 0.9098–0.9442× | 0.20× | — |
| Practice | `cal.unicode.words` | Rust engine | 0.0097× | 0.0096–0.0098× | 2.69× | SLOWER |
| Practice | `cal.cold.compile-search` | Python engine | 0.2978× | 0.2924–0.3068× | 5.84× | SLOWER |
| Practice | `cal.cold.compile-search` | Native C engine | 1.3739× | 1.3240–1.4326× | 1.71× | FASTER |
| Practice | `cal.cold.compile-search` | Rust engine | 0.7119× | 0.7018–0.7232× | 1.95× | SLOWER |
| Practice | `cal.module.warm` | Python engine | 0.0105× | 0.0104–0.0107× | 7.21× | SLOWER |
| Practice | `cal.module.warm` | Native C engine | 1.4737× | 1.4501–1.5018× | 0.07× | FASTER |
| Practice | `cal.module.warm` | Rust engine | 0.0323× | 0.0319–0.0328× | 3.39× | SLOWER |
| Practice | `cal.empty.finditer` | Python engine | 0.0102× | 0.0099–0.0105× | 8.09× | SLOWER |
| Practice | `cal.empty.finditer` | Native C engine | 2.3075× | 2.2482–2.3747× | 0.36× | FASTER |
| Practice | `cal.empty.finditer` | Rust engine | 0.0218× | 0.0213–0.0224× | 1.67× | SLOWER |
| Practice | `cal.backref.fullmatch` | Python engine | 0.0192× | 0.0188–0.0197× | 6.99× | SLOWER |
| Practice | `cal.backref.fullmatch` | Native C engine | 1.4160× | 1.3813–1.4563× | 0.08× | FASTER |
| Practice | `cal.backref.fullmatch` | Rust engine | 0.0194× | 0.0189–0.0199× | 3.04× | SLOWER |
| Practice | `cal.conditional.match` | Python engine | 0.0182× | 0.0179–0.0186× | 6.78× | SLOWER |
| Practice | `cal.conditional.match` | Native C engine | 1.3505× | 1.2362–1.4302× | 0.08× | FASTER |
| Practice | `cal.conditional.match` | Rust engine | 0.0166× | 0.0164–0.0169× | 2.97× | SLOWER |
| Practice | `cal.atomic.search` | Python engine | 0.0100× | 0.0098–0.0103× | 8.80× | SLOWER |
| Practice | `cal.atomic.search` | Native C engine | 1.1376× | 1.1177–1.1574× | 0.50× | FASTER |
| Practice | `cal.atomic.search` | Rust engine | 0.0196× | 0.0190–0.0201× | 3.14× | SLOWER |
| Practice | `cal.byteslike.findall` | Python engine | 0.0112× | 0.0110–0.0116× | 7.48× | SLOWER |
| Practice | `cal.byteslike.findall` | Native C engine | 2.4480× | 2.2613–2.6005× | 0.18× | FASTER |
| Practice | `cal.byteslike.findall` | Rust engine | 0.0084× | 0.0082–0.0086× | 2.93× | SLOWER |
| Practice | `cal.unicode-name.search` | Python engine | 0.0141× | 0.0139–0.0142× | 4.37× | SLOWER |
| Practice | `cal.unicode-name.search` | Native C engine | 1.4787× | 1.4625–1.4955× | 0.07× | FASTER |
| Practice | `cal.unicode-name.search` | Rust engine | 0.0193× | 0.0191–0.0194× | 3.14× | SLOWER |
| Practice | `cal.ignorecase.findall` | Python engine | 0.0074× | 0.0073–0.0074× | 5.14× | SLOWER |
| Practice | `cal.ignorecase.findall` | Native C engine | 1.7445× | 1.7260–1.7639× | 0.16× | FASTER |
| Practice | `cal.ignorecase.findall` | Rust engine | 0.0084× | 0.0084–0.0085× | 2.96× | SLOWER |
| Practice | `cal.many.split` | Python engine | 0.0126× | 0.0123–0.0128× | 8.86× | SLOWER |
| Practice | `cal.many.split` | Native C engine | 1.3161× | 1.2832–1.3551× | 0.20× | FASTER |
| Practice | `cal.many.split` | Rust engine | 0.0047× | 0.0046–0.0048× | 2.86× | SLOWER |
| Practice | `cal.escape.text` | Python engine | 0.9638× | 0.9245–0.9928× | 1.00× | — |
| Practice | `cal.escape.text` | Native C engine | 3.2240× | 3.1956–3.2469× | 1.00× | FASTER |
| Practice | `cal.escape.text` | Rust engine | 0.9922× | 0.9875–0.9969× | 1.00× | — |
| Practice | `cal.compile.only` | Python engine | 2.2032× | 2.1749–2.2308× | 0.50× | FASTER |
| Practice | `cal.compile.only` | Native C engine | 1.6457× | 1.6191–1.6726× | 1.59× | FASTER |
| Practice | `cal.compile.only` | Rust engine | 1.7889× | 1.7693–1.8070× | 0.56× | FASTER |
| Practice | `cal.scanner.search` | Python engine | 0.0130× | 0.0128–0.0131× | 6.71× | SLOWER |
| Practice | `cal.scanner.search` | Native C engine | 1.3367× | 1.3152–1.3546× | 0.38× | FASTER |
| Practice | `cal.scanner.search` | Rust engine | 0.0089× | 0.0088–0.0090× | 1.98× | SLOWER |
| Practice | `cal.match.surface` | Python engine | 0.0139× | 0.0137–0.0141× | 12.88× | SLOWER |
| Practice | `cal.match.surface` | Native C engine | 1.4071× | 1.3627–1.4436× | 0.32× | FASTER |
| Practice | `cal.match.surface` | Rust engine | 0.0473× | 0.0466–0.0480× | 3.26× | SLOWER |
| Holdout | `hold.search.literal.hit` | Python engine | 0.0074× | 0.0073–0.0074× | 102.00× | SLOWER |
| Holdout | `hold.search.literal.hit` | Native C engine | 1.0941× | 1.0578–1.1183× | 0.73× | FASTER |
| Holdout | `hold.search.literal.hit` | Rust engine | 0.0090× | 0.0090–0.0091× | 33.96× | SLOWER |
| Holdout | `hold.search.literal.miss` | Python engine | 0.0024× | 0.0023–0.0024× | 14408.00× | SLOWER |
| Holdout | `hold.search.literal.miss` | Native C engine | 1.1727× | 1.1629–1.1874× | 0.00× | FASTER |
| Holdout | `hold.search.literal.miss` | Rust engine | 0.0057× | 0.0057–0.0058× | 4375.00× | SLOWER |
| Holdout | `hold.search.long-boundary` | Python engine | 0.0003× | 0.0003–0.0003× | 130.58× | SLOWER |
| Holdout | `hold.search.long-boundary` | Native C engine | 17.9102× | 16.3447–19.6975× | 0.07× | FASTER |
| Holdout | `hold.search.long-boundary` | Rust engine | 0.0010× | 0.0009–0.0011× | 218.22× | SLOWER |
| Holdout | `hold.search.class-anchor` | Python engine | 0.0100× | 0.0099–0.0102× | 11.17× | SLOWER |
| Holdout | `hold.search.class-anchor` | Native C engine | 1.3053× | 1.1657–1.4000× | 0.07× | FASTER |
| Holdout | `hold.search.class-anchor` | Rust engine | 0.0131× | 0.0125–0.0136× | 3.39× | SLOWER |
| Holdout | `hold.match.prefix` | Python engine | 0.0258× | 0.0245–0.0280× | 3.87× | SLOWER |
| Holdout | `hold.match.prefix` | Native C engine | 1.2275× | 1.1212–1.3120× | 0.07× | FASTER |
| Holdout | `hold.match.prefix` | Rust engine | 0.0163× | 0.0160–0.0167× | 2.87× | SLOWER |
| Holdout | `hold.fullmatch.structured` | Python engine | 0.0113× | 0.0110–0.0118× | 16.36× | SLOWER |
| Holdout | `hold.fullmatch.structured` | Native C engine | 1.4615× | 1.4313–1.5127× | 0.07× | FASTER |
| Holdout | `hold.fullmatch.structured` | Rust engine | 0.0201× | 0.0189–0.0226× | 3.04× | SLOWER |
| Holdout | `hold.search.look-capture` | Python engine | 0.0108× | 0.0096–0.0124× | 17.64× | SLOWER |
| Holdout | `hold.search.look-capture` | Native C engine | 1.3344× | 1.1894–1.5298× | 0.08× | FASTER |
| Holdout | `hold.search.look-capture` | Rust engine | 0.0182× | 0.0167–0.0202× | 3.26× | SLOWER |
| Holdout | `hold.findall.tokens` | Python engine | 0.0105× | 0.0104–0.0106× | 11.27× | SLOWER |
| Holdout | `hold.findall.tokens` | Native C engine | 2.1999× | 2.0263–2.3119× | 0.21× | FASTER |
| Holdout | `hold.findall.tokens` | Rust engine | 0.0058× | 0.0058–0.0059× | 3.10× | SLOWER |
| Holdout | `hold.finditer.groups` | Python engine | 0.0132× | 0.0127–0.0137× | 7.75× | SLOWER |
| Holdout | `hold.finditer.groups` | Native C engine | 2.1546× | 2.0270–2.2671× | 0.41× | FASTER |
| Holdout | `hold.finditer.groups` | Rust engine | 0.0094× | 0.0091–0.0097× | 1.93× | SLOWER |
| Holdout | `hold.split.capture` | Python engine | 0.0097× | 0.0096–0.0098× | 11.37× | SLOWER |
| Holdout | `hold.split.capture` | Native C engine | 1.8538× | 1.8401–1.8667× | 0.20× | FASTER |
| Holdout | `hold.split.capture` | Rust engine | 0.0066× | 0.0064–0.0067× | 2.62× | SLOWER |
| Holdout | `hold.sub.template` | Python engine | 0.0153× | 0.0144–0.0158× | 9.29× | SLOWER |
| Holdout | `hold.sub.template` | Native C engine | 1.9024× | 1.6571–2.0961× | 0.12× | FASTER |
| Holdout | `hold.sub.template` | Rust engine | 0.0145× | 0.0144–0.0147× | 2.39× | SLOWER |
| Holdout | `hold.subn.callable` | Python engine | 0.0269× | 0.0265–0.0272× | 4.58× | SLOWER |
| Holdout | `hold.subn.callable` | Native C engine | 1.1551× | 1.1226–1.1839× | 0.25× | FASTER |
| Holdout | `hold.subn.callable` | Rust engine | 0.0222× | 0.0220–0.0224× | 2.53× | SLOWER |
| Holdout | `hold.bytes.tokens` | Python engine | 0.0105× | 0.0101–0.0112× | 8.71× | SLOWER |
| Holdout | `hold.bytes.tokens` | Native C engine | 2.6619× | 2.5528–2.8384× | 0.18× | FASTER |
| Holdout | `hold.bytes.tokens` | Rust engine | 0.0087× | 0.0083–0.0092× | 2.92× | SLOWER |
| Holdout | `hold.unicode.words` | Python engine | 0.0086× | 0.0086–0.0086× | 6.63× | SLOWER |
| Holdout | `hold.unicode.words` | Native C engine | 1.5753× | 1.4624–1.6426× | 0.20× | FASTER |
| Holdout | `hold.unicode.words` | Rust engine | 0.0114× | 0.0112–0.0116× | 2.67× | SLOWER |
| Holdout | `hold.cold.compile-search` | Python engine | 0.4809× | 0.4765–0.4850× | 5.95× | SLOWER |
| Holdout | `hold.cold.compile-search` | Native C engine | 1.3329× | 1.3156–1.3500× | 1.77× | FASTER |
| Holdout | `hold.cold.compile-search` | Rust engine | 0.7426× | 0.7353–0.7498× | 1.93× | SLOWER |
| Holdout | `hold.module.warm` | Python engine | 0.0187× | 0.0186–0.0188× | 7.12× | SLOWER |
| Holdout | `hold.module.warm` | Native C engine | 1.2797× | 1.2411–1.3046× | 0.07× | FASTER |
| Holdout | `hold.module.warm` | Rust engine | 0.0312× | 0.0311–0.0313× | 3.38× | SLOWER |
| Holdout | `hold.empty.finditer` | Python engine | 0.0090× | 0.0088–0.0092× | 8.52× | SLOWER |
| Holdout | `hold.empty.finditer` | Native C engine | 2.4208× | 2.3601–2.4856× | 0.38× | FASTER |
| Holdout | `hold.empty.finditer` | Rust engine | 0.0209× | 0.0205–0.0214× | 1.62× | SLOWER |
| Holdout | `hold.backref.fullmatch` | Python engine | 0.0184× | 0.0176–0.0200× | 6.99× | SLOWER |
| Holdout | `hold.backref.fullmatch` | Native C engine | 1.3986× | 1.3316–1.5176× | 0.08× | FASTER |
| Holdout | `hold.backref.fullmatch` | Rust engine | 0.0195× | 0.0186–0.0212× | 3.04× | SLOWER |
| Holdout | `hold.conditional.match` | Python engine | 0.0186× | 0.0185–0.0188× | 6.78× | SLOWER |
| Holdout | `hold.conditional.match` | Native C engine | 1.2854× | 1.2624–1.3050× | 0.08× | FASTER |
| Holdout | `hold.conditional.match` | Rust engine | 0.0184× | 0.0182–0.0186× | 2.94× | SLOWER |
| Holdout | `hold.atomic.search` | Python engine | 0.0107× | 0.0100–0.0119× | 6.53× | SLOWER |
| Holdout | `hold.atomic.search` | Native C engine | 1.5607× | 1.4672–1.7399× | 0.07× | FASTER |
| Holdout | `hold.atomic.search` | Rust engine | 0.0219× | 0.0205–0.0241× | 3.13× | SLOWER |
| Holdout | `hold.byteslike.findall` | Python engine | 0.0113× | 0.0112–0.0113× | 7.39× | SLOWER |
| Holdout | `hold.byteslike.findall` | Native C engine | 2.4848× | 2.4537–2.5071× | 0.18× | FASTER |
| Holdout | `hold.byteslike.findall` | Rust engine | 0.0083× | 0.0082–0.0083× | 2.83× | SLOWER |
| Holdout | `hold.unicode-name.search` | Python engine | 0.0130× | 0.0128–0.0131× | 4.69× | SLOWER |
| Holdout | `hold.unicode-name.search` | Native C engine | 1.5469× | 1.5230–1.5703× | 0.07× | FASTER |
| Holdout | `hold.unicode-name.search` | Rust engine | 0.0195× | 0.0193–0.0198× | 3.14× | SLOWER |
| Holdout | `hold.ignorecase.findall` | Python engine | 0.0078× | 0.0075–0.0082× | 4.86× | SLOWER |
| Holdout | `hold.ignorecase.findall` | Native C engine | 1.7635× | 1.6944–1.8576× | 0.16× | FASTER |
| Holdout | `hold.ignorecase.findall` | Rust engine | 0.0094× | 0.0090–0.0100× | 2.94× | SLOWER |
| Holdout | `hold.many.split` | Python engine | 0.0125× | 0.0122–0.0129× | 8.86× | SLOWER |
| Holdout | `hold.many.split` | Native C engine | 1.3055× | 1.2695–1.3541× | 0.20× | FASTER |
| Holdout | `hold.many.split` | Rust engine | 0.0046× | 0.0045–0.0048× | 2.86× | SLOWER |
| Holdout | `hold.escape.bytes` | Python engine | 1.0103× | 0.9678–1.0474× | 0.68× | — |
| Holdout | `hold.escape.bytes` | Native C engine | 4.6463× | 4.5365–4.7750× | 0.32× | FASTER |
| Holdout | `hold.escape.bytes` | Rust engine | 1.0178× | 0.9778–1.0527× | 0.68× | — |
| Holdout | `hold.compile.only` | Python engine | 1.9696× | 1.9291–2.0096× | 0.54× | FASTER |
| Holdout | `hold.compile.only` | Native C engine | 1.3883× | 1.3511–1.4202× | 2.11× | FASTER |
| Holdout | `hold.compile.only` | Rust engine | 1.6906× | 1.6533–1.7263× | 0.60× | FASTER |
| Holdout | `hold.scanner.search` | Python engine | 0.0126× | 0.0125–0.0127× | 6.71× | SLOWER |
| Holdout | `hold.scanner.search` | Native C engine | 1.3263× | 1.3062–1.3484× | 0.38× | FASTER |
| Holdout | `hold.scanner.search` | Rust engine | 0.0087× | 0.0086–0.0088× | 1.98× | SLOWER |
| Holdout | `hold.match.surface` | Python engine | 0.0209× | 0.0202–0.0220× | 12.79× | SLOWER |
| Holdout | `hold.match.surface` | Native C engine | 1.1376× | 1.1006–1.1947× | 0.32× | FASTER |
| Holdout | `hold.match.surface` | Rust engine | 0.0412× | 0.0397–0.0433× | 3.25× | SLOWER |
| Practice | `cal.real.log` | Python engine | 0.0031× | 0.0029–0.0032× | 27.33× | SLOWER |
| Practice | `cal.real.log` | Native C engine | 1.3306× | 1.2720–1.3884× | 0.35× | FASTER |
| Practice | `cal.real.log` | Rust engine | 0.0062× | 0.0059–0.0065× | 3.19× | SLOWER |
| Practice | `cal.real.url` | Python engine | 0.0064× | 0.0062–0.0067× | 26.38× | SLOWER |
| Practice | `cal.real.url` | Native C engine | 1.4714× | 1.3617–1.5809× | 0.11× | FASTER |
| Practice | `cal.real.url` | Rust engine | 0.0121× | 0.0117–0.0126× | 3.49× | SLOWER |
| Practice | `cal.real.email` | Python engine | 0.0053× | 0.0053–0.0054× | 9.90× | SLOWER |
| Practice | `cal.real.email` | Native C engine | 1.0166× | 0.9671–1.0528× | 0.12× | — |
| Practice | `cal.real.email` | Rust engine | 0.0060× | 0.0059–0.0061× | 3.85× | SLOWER |
| Practice | `cal.real.datetime` | Python engine | 0.0076× | 0.0075–0.0078× | 23.68× | SLOWER |
| Practice | `cal.real.datetime` | Native C engine | 1.2323× | 1.2140–1.2571× | 0.09× | FASTER |
| Practice | `cal.real.datetime` | Rust engine | 0.0157× | 0.0154–0.0160× | 3.49× | SLOWER |
| Practice | `cal.real.version` | Python engine | 0.0108× | 0.0107–0.0110× | 22.95× | SLOWER |
| Practice | `cal.real.version` | Native C engine | 2.1309× | 2.1151–2.1463× | 0.00× | FASTER |
| Practice | `cal.real.version` | Rust engine | 0.0288× | 0.0285–0.0291× | 3.46× | SLOWER |
| Practice | `cal.real.uuid` | Python engine | 0.0062× | 0.0061–0.0063× | 18.66× | SLOWER |
| Practice | `cal.real.uuid` | Native C engine | 1.5697× | 1.4660–1.6411× | 0.07× | FASTER |
| Practice | `cal.real.uuid` | Rust engine | 0.0133× | 0.0133–0.0134× | 3.96× | SLOWER |
| Practice | `cal.real.ip` | Python engine | 0.0077× | 0.0076–0.0078× | 29.12× | SLOWER |
| Practice | `cal.real.ip` | Native C engine | 1.1017× | 1.0864–1.1157× | 0.07× | FASTER |
| Practice | `cal.real.ip` | Rust engine | 0.0252× | 0.0248–0.0257× | 3.02× | SLOWER |
| Practice | `cal.real.path` | Python engine | 0.0055× | 0.0054–0.0056× | 30.63× | SLOWER |
| Practice | `cal.real.path` | Native C engine | 1.3486× | 1.3372–1.3617× | 0.12× | FASTER |
| Practice | `cal.real.path` | Rust engine | 0.0105× | 0.0104–0.0105× | 3.60× | SLOWER |
| Practice | `cal.real.config` | Python engine | 0.0087× | 0.0083–0.0095× | 16.04× | SLOWER |
| Practice | `cal.real.config` | Native C engine | 3.2019× | 3.0418–3.4684× | 0.37× | FASTER |
| Practice | `cal.real.config` | Rust engine | 0.0176× | 0.0168–0.0191× | 2.32× | SLOWER |
| Practice | `cal.real.comments` | Python engine | 0.0062× | 0.0061–0.0064× | 11.73× | SLOWER |
| Practice | `cal.real.comments` | Native C engine | 1.4227× | 1.3022–1.5274× | 0.14× | FASTER |
| Practice | `cal.real.comments` | Rust engine | 0.0039× | 0.0037–0.0040× | 3.74× | SLOWER |
| Practice | `cal.real.whitespace` | Python engine | 0.0069× | 0.0068–0.0070× | 8.36× | SLOWER |
| Practice | `cal.real.whitespace` | Native C engine | 1.3259× | 1.2757–1.3648× | 0.14× | FASTER |
| Practice | `cal.real.whitespace` | Rust engine | 0.0077× | 0.0076–0.0079× | 2.79× | SLOWER |
| Practice | `cal.real.lines` | Python engine | 0.0096× | 0.0092–0.0100× | 14.09× | SLOWER |
| Practice | `cal.real.lines` | Native C engine | 1.9041× | 1.8483–1.9688× | 0.15× | FASTER |
| Practice | `cal.real.lines` | Rust engine | 0.0096× | 0.0093–0.0099× | 2.83× | SLOWER |
| Practice | `cal.real.markup` | Python engine | 0.0044× | 0.0044–0.0044× | 13.23× | SLOWER |
| Practice | `cal.real.markup` | Native C engine | 1.2194× | 1.2053–1.2318× | 0.10× | FASTER |
| Practice | `cal.real.markup` | Rust engine | 0.0036× | 0.0036–0.0036× | 4.19× | SLOWER |
| Practice | `cal.real.quotes` | Python engine | 0.0041× | 0.0041–0.0041× | 18.83× | SLOWER |
| Practice | `cal.real.quotes` | Native C engine | 1.5490× | 1.5330–1.5672× | 0.10× | FASTER |
| Practice | `cal.real.quotes` | Rust engine | 0.0072× | 0.0071–0.0073× | 3.83× | SLOWER |
| Practice | `cal.real.csv` | Python engine | 0.0048× | 0.0047–0.0049× | 19.83× | SLOWER |
| Practice | `cal.real.csv` | Native C engine | 2.5405× | 2.4690–2.6310× | 0.29× | FASTER |
| Practice | `cal.real.csv` | Rust engine | 0.0107× | 0.0104–0.0110× | 2.97× | SLOWER |
| Practice | `cal.branch.prefix` | Python engine | 0.0091× | 0.0089–0.0092× | 12.65× | SLOWER |
| Practice | `cal.branch.prefix` | Native C engine | 1.2633× | 1.2460–1.2803× | 0.07× | FASTER |
| Practice | `cal.branch.prefix` | Rust engine | 0.0129× | 0.0127–0.0130× | 3.37× | SLOWER |
| Practice | `cal.branch.miss` | Python engine | 0.0009× | 0.0009–0.0010× | 83.64× | SLOWER |
| Practice | `cal.branch.miss` | Native C engine | 0.8693× | 0.8209–0.9338× | 0.00× | — |
| Practice | `cal.branch.miss` | Rust engine | 0.0129× | 0.0125–0.0136× | 4.25× | SLOWER |
| Practice | `cal.repeat.nested` | Python engine | 0.0097× | 0.0096–0.0098× | 15.24× | SLOWER |
| Practice | `cal.repeat.nested` | Native C engine | 1.4455× | 1.4259–1.4617× | 0.64× | FASTER |
| Practice | `cal.repeat.nested` | Rust engine | 0.0233× | 0.0230–0.0236× | 1.57× | SLOWER |
| Practice | `cal.lines.records` | Python engine | 0.0085× | 0.0084–0.0086× | 14.74× | SLOWER |
| Practice | `cal.lines.records` | Native C engine | 1.3754× | 1.3576–1.3955× | 0.38× | FASTER |
| Practice | `cal.lines.records` | Rust engine | 0.0075× | 0.0074–0.0076× | 2.56× | SLOWER |
| Practice | `cal.block.dotall` | Python engine | 0.0069× | 0.0063–0.0078× | 17.13× | SLOWER |
| Practice | `cal.block.dotall` | Native C engine | 1.5164× | 1.3643–1.6745× | 0.08× | FASTER |
| Practice | `cal.block.dotall` | Rust engine | 0.0140× | 0.0129–0.0157× | 3.97× | SLOWER |
| Practice | `cal.pattern.verbose` | Python engine | 0.0041× | 0.0039–0.0043× | 14.85× | SLOWER |
| Practice | `cal.pattern.verbose` | Native C engine | 2.3581× | 2.2798–2.4987× | 0.09× | FASTER |
| Practice | `cal.pattern.verbose` | Rust engine | 0.0202× | 0.0196–0.0214× | 3.43× | SLOWER |
| Practice | `cal.mode.ascii` | Python engine | 0.0054× | 0.0052–0.0056× | 7.27× | SLOWER |
| Practice | `cal.mode.ascii` | Native C engine | 1.1206× | 1.0940–1.1670× | 0.13× | FASTER |
| Practice | `cal.mode.ascii` | Rust engine | 0.0095× | 0.0093–0.0099× | 3.04× | SLOWER |
| Practice | `cal.mode.casefold` | Python engine | 0.0080× | 0.0079–0.0082× | 5.52× | SLOWER |
| Practice | `cal.mode.casefold` | Native C engine | 1.4081× | 1.3829–1.4302× | 0.20× | FASTER |
| Practice | `cal.mode.casefold` | Rust engine | 0.0086× | 0.0083–0.0088× | 2.90× | SLOWER |
| Practice | `cal.mode.astral` | Python engine | 0.0093× | 0.0092–0.0093× | 7.05× | SLOWER |
| Practice | `cal.mode.astral` | Native C engine | 1.6373× | 1.6232–1.6515× | 0.25× | FASTER |
| Practice | `cal.mode.astral` | Rust engine | 0.0091× | 0.0091–0.0092× | 2.76× | SLOWER |
| Practice | `cal.look.negative-ahead` | Python engine | 0.0036× | 0.0036–0.0036× | 15.69× | SLOWER |
| Practice | `cal.look.negative-ahead` | Native C engine | 1.0633× | 1.0232–1.0879× | 0.14× | FASTER |
| Practice | `cal.look.negative-ahead` | Rust engine | 0.0071× | 0.0071–0.0072× | 3.46× | SLOWER |
| Practice | `cal.look.negative-behind` | Python engine | 0.0066× | 0.0064–0.0068× | 12.65× | SLOWER |
| Practice | `cal.look.negative-behind` | Native C engine | 1.3817× | 1.3500–1.4346× | 0.10× | FASTER |
| Practice | `cal.look.negative-behind` | Rust engine | 0.0101× | 0.0098–0.0105× | 3.19× | SLOWER |
| Practice | `cal.bytes.replace` | Python engine | 0.0168× | 0.0164–0.0174× | 9.71× | SLOWER |
| Practice | `cal.bytes.replace` | Native C engine | 1.1051× | 1.0678–1.1444× | 1.18× | FASTER |
| Practice | `cal.bytes.replace` | Rust engine | 0.0163× | 0.0159–0.0168× | 2.52× | SLOWER |
| Practice | `cal.bytes.scan` | Python engine | 0.0119× | 0.0112–0.0131× | 8.55× | SLOWER |
| Practice | `cal.bytes.scan` | Native C engine | 1.6641× | 1.5634–1.8321× | 0.40× | FASTER |
| Practice | `cal.bytes.scan` | Rust engine | 0.0098× | 0.0092–0.0109× | 1.87× | SLOWER |
| Practice | `cal.compile.complex` | Python engine | 1.8485× | 1.7480–2.0540× | 0.39× | FASTER |
| Practice | `cal.compile.complex` | Native C engine | 1.4158× | 1.2953–1.6025× | 1.75× | FASTER |
| Practice | `cal.compile.complex` | Rust engine | 1.7303× | 1.6003–1.9485× | 0.52× | FASTER |
| Practice | `cal.module.replace` | Python engine | 0.0208× | 0.0206–0.0211× | 10.12× | SLOWER |
| Practice | `cal.module.replace` | Native C engine | 1.2444× | 1.1230–1.3376× | 0.04× | FASTER |
| Practice | `cal.module.replace` | Rust engine | 0.0201× | 0.0197–0.0207× | 2.52× | SLOWER |
| Practice | `cal.zero.boundary` | Python engine | 0.0075× | 0.0071–0.0083× | 13.81× | SLOWER |
| Practice | `cal.zero.boundary` | Native C engine | 2.1773× | 1.9543–2.4597× | 0.43× | FASTER |
| Practice | `cal.zero.boundary` | Rust engine | 0.0133× | 0.0125–0.0146× | 1.69× | SLOWER |
| Practice | `cal.dense.iter` | Python engine | 0.0151× | 0.0149–0.0153× | 4.92× | SLOWER |
| Practice | `cal.dense.iter` | Native C engine | 1.5831× | 1.5670–1.6000× | 0.52× | FASTER |
| Practice | `cal.dense.iter` | Rust engine | 0.0079× | 0.0078–0.0079× | 1.49× | SLOWER |
| Practice | `cal.capture.optional` | Python engine | 0.0099× | 0.0095–0.0104× | 14.26× | SLOWER |
| Practice | `cal.capture.optional` | Native C engine | 1.3208× | 1.2380–1.4038× | 0.18× | FASTER |
| Practice | `cal.capture.optional` | Rust engine | 0.0088× | 0.0085–0.0092× | 2.79× | SLOWER |
| Practice | `cal.split.limited` | Python engine | 0.0065× | 0.0064–0.0065× | 7.47× | SLOWER |
| Practice | `cal.split.limited` | Native C engine | 1.5698× | 1.5513–1.5898× | 0.19× | FASTER |
| Practice | `cal.split.limited` | Rust engine | 0.0076× | 0.0075–0.0077× | 2.82× | SLOWER |
| Practice | `cal.replace.limited` | Python engine | 0.0130× | 0.0128–0.0132× | 6.04× | SLOWER |
| Practice | `cal.replace.limited` | Native C engine | 1.4729× | 1.3732–1.5351× | 0.15× | FASTER |
| Practice | `cal.replace.limited` | Rust engine | 0.0095× | 0.0094–0.0096× | 2.90× | SLOWER |
| Practice | `cal.bytes.view-long` | Python engine | 0.0066× | 0.0065–0.0066× | 48.64× | SLOWER |
| Practice | `cal.bytes.view-long` | Native C engine | 1.3340× | 1.3247–1.3446× | 0.60× | FASTER |
| Practice | `cal.bytes.view-long` | Rust engine | 0.0009× | 0.0009–0.0009× | 5.61× | SLOWER |
| Practice | `cal.window.search` | Python engine | 0.0195× | 0.0185–0.0213× | 4.40× | SLOWER |
| Practice | `cal.window.search` | Native C engine | 0.9817× | 0.9326–1.0701× | 0.18× | — |
| Practice | `cal.window.search` | Rust engine | 0.0160× | 0.0151–0.0176× | 3.30× | SLOWER |
| Practice | `cal.window.findall` | Python engine | 0.0173× | 0.0168–0.0179× | 4.02× | SLOWER |
| Practice | `cal.window.findall` | Native C engine | 1.2637× | 1.2242–1.3036× | 0.23× | FASTER |
| Practice | `cal.window.findall` | Rust engine | 0.0080× | 0.0078–0.0083× | 3.01× | SLOWER |
| Practice | `cal.window.scanner` | Python engine | 0.0166× | 0.0161–0.0170× | 4.46× | SLOWER |
| Practice | `cal.window.scanner` | Native C engine | 1.2118× | 1.1552–1.2488× | 0.33× | FASTER |
| Practice | `cal.window.scanner` | Rust engine | 0.0091× | 0.0090–0.0092× | 2.20× | SLOWER |
| Practice | `cal.window.match` | Python engine | 0.0346× | 0.0342–0.0351× | 3.55× | SLOWER |
| Practice | `cal.window.match` | Native C engine | 0.9882× | 0.9745–0.9999× | 0.18× | — |
| Practice | `cal.window.match` | Rust engine | 0.0179× | 0.0177–0.0181× | 2.45× | SLOWER |
| Practice | `cal.literal.replace` | Python engine | 0.0061× | 0.0057–0.0065× | 41.75× | SLOWER |
| Practice | `cal.literal.replace` | Native C engine | 1.4704× | 1.4213–1.5315× | 0.51× | FASTER |
| Practice | `cal.literal.replace` | Rust engine | 0.0054× | 0.0052–0.0056× | 10.40× | SLOWER |
| Practice | `cal.template.repeat` | Python engine | 0.0175× | 0.0156–0.0191× | 6.29× | SLOWER |
| Practice | `cal.template.repeat` | Native C engine | 1.6889× | 1.5023–1.8174× | 0.15× | FASTER |
| Practice | `cal.template.repeat` | Rust engine | 0.0124× | 0.0114–0.0132× | 2.29× | SLOWER |
| Practice | `cal.match.miss` | Python engine | 0.0278× | 0.0275–0.0282× | 5.02× | SLOWER |
| Practice | `cal.match.miss` | Native C engine | 1.0946× | 0.9659–1.1759× | 0.00× | — |
| Practice | `cal.match.miss` | Rust engine | 0.0078× | 0.0077–0.0080× | 4.00× | SLOWER |
| Practice | `cal.fullmatch.miss` | Python engine | 0.0164× | 0.0163–0.0166× | 11.09× | SLOWER |
| Practice | `cal.fullmatch.miss` | Native C engine | 1.5767× | 1.4196–1.6691× | 0.00× | FASTER |
| Practice | `cal.fullmatch.miss` | Rust engine | 0.0217× | 0.0216–0.0219× | 3.32× | SLOWER |
| Holdout | `hold.real.log` | Python engine | 0.0027× | 0.0026–0.0028× | 36.41× | SLOWER |
| Holdout | `hold.real.log` | Native C engine | 1.1530× | 1.0802–1.2160× | 0.35× | FASTER |
| Holdout | `hold.real.log` | Rust engine | 0.0054× | 0.0052–0.0056× | 3.23× | SLOWER |
| Holdout | `hold.real.url` | Python engine | 0.0051× | 0.0046–0.0056× | 26.93× | SLOWER |
| Holdout | `hold.real.url` | Native C engine | 1.4200× | 1.2817–1.5702× | 0.11× | FASTER |
| Holdout | `hold.real.url` | Rust engine | 0.0100× | 0.0090–0.0110× | 3.79× | SLOWER |
| Holdout | `hold.real.email` | Python engine | 0.0041× | 0.0040–0.0041× | 12.09× | SLOWER |
| Holdout | `hold.real.email` | Native C engine | 1.3117× | 1.2994–1.3244× | 0.12× | FASTER |
| Holdout | `hold.real.email` | Rust engine | 0.0068× | 0.0067–0.0068× | 3.88× | SLOWER |
| Holdout | `hold.real.datetime` | Python engine | 0.0075× | 0.0072–0.0081× | 27.33× | SLOWER |
| Holdout | `hold.real.datetime` | Native C engine | 1.3112× | 1.2622–1.4072× | 0.09× | FASTER |
| Holdout | `hold.real.datetime` | Rust engine | 0.0176× | 0.0168–0.0189× | 3.42× | SLOWER |
| Holdout | `hold.real.version` | Python engine | 0.0091× | 0.0090–0.0093× | 23.70× | SLOWER |
| Holdout | `hold.real.version` | Native C engine | 1.5066× | 1.4837–1.5310× | 0.06× | FASTER |
| Holdout | `hold.real.version` | Rust engine | 0.0209× | 0.0207–0.0211× | 3.01× | SLOWER |
| Holdout | `hold.real.uuid` | Python engine | 0.0060× | 0.0059–0.0061× | 18.05× | SLOWER |
| Holdout | `hold.real.uuid` | Native C engine | 1.4943× | 1.3513–1.5784× | 0.07× | FASTER |
| Holdout | `hold.real.uuid` | Rust engine | 0.0127× | 0.0123–0.0130× | 3.95× | SLOWER |
| Holdout | `hold.real.ip` | Python engine | 0.0086× | 0.0085–0.0088× | 30.05× | SLOWER |
| Holdout | `hold.real.ip` | Native C engine | 1.1884× | 1.1655–1.2109× | 0.07× | FASTER |
| Holdout | `hold.real.ip` | Rust engine | 0.0210× | 0.0207–0.0214× | 3.02× | SLOWER |
| Holdout | `hold.real.path` | Python engine | 0.0057× | 0.0055–0.0060× | 26.39× | SLOWER |
| Holdout | `hold.real.path` | Native C engine | 3.2966× | 3.1628–3.5136× | 0.12× | FASTER |
| Holdout | `hold.real.path` | Rust engine | 0.0097× | 0.0094–0.0103× | 3.84× | SLOWER |
| Holdout | `hold.real.config` | Python engine | 0.0086× | 0.0084–0.0088× | 18.02× | SLOWER |
| Holdout | `hold.real.config` | Native C engine | 2.9846× | 2.8880–3.0705× | 0.37× | FASTER |
| Holdout | `hold.real.config` | Rust engine | 0.0153× | 0.0150–0.0157× | 2.32× | SLOWER |
| Holdout | `hold.real.comments` | Python engine | 0.0047× | 0.0046–0.0048× | 16.97× | SLOWER |
| Holdout | `hold.real.comments` | Native C engine | 1.1331× | 1.0180–1.2174× | 0.14× | FASTER |
| Holdout | `hold.real.comments` | Rust engine | 0.0032× | 0.0032–0.0033× | 4.05× | SLOWER |
| Holdout | `hold.real.whitespace` | Python engine | 0.0069× | 0.0068–0.0070× | 8.45× | SLOWER |
| Holdout | `hold.real.whitespace` | Native C engine | 1.3589× | 1.3497–1.3695× | 0.14× | FASTER |
| Holdout | `hold.real.whitespace` | Rust engine | 0.0071× | 0.0070–0.0072× | 2.74× | SLOWER |
| Holdout | `hold.real.lines` | Python engine | 0.0094× | 0.0093–0.0097× | 13.22× | SLOWER |
| Holdout | `hold.real.lines` | Native C engine | 1.6541× | 1.5213–1.7682× | 0.14× | FASTER |
| Holdout | `hold.real.lines` | Rust engine | 0.0093× | 0.0091–0.0095× | 2.82× | SLOWER |
| Holdout | `hold.real.markup` | Python engine | 0.0046× | 0.0045–0.0048× | 14.16× | SLOWER |
| Holdout | `hold.real.markup` | Native C engine | 1.3233× | 1.2447–1.4705× | 0.13× | FASTER |
| Holdout | `hold.real.markup` | Rust engine | 0.0033× | 0.0032–0.0037× | 4.34× | SLOWER |
| Holdout | `hold.real.quotes` | Python engine | 0.0040× | 0.0039–0.0042× | 18.87× | SLOWER |
| Holdout | `hold.real.quotes` | Native C engine | 1.4499× | 1.3031–1.5456× | 0.10× | FASTER |
| Holdout | `hold.real.quotes` | Rust engine | 0.0070× | 0.0064–0.0074× | 3.58× | SLOWER |
| Holdout | `hold.real.csv` | Python engine | 0.0039× | 0.0038–0.0039× | 18.08× | SLOWER |
| Holdout | `hold.real.csv` | Native C engine | 2.4044× | 2.3792–2.4284× | 0.30× | FASTER |
| Holdout | `hold.real.csv` | Rust engine | 0.0093× | 0.0092–0.0093× | 3.21× | SLOWER |
| Holdout | `hold.branch.prefix` | Python engine | 0.0095× | 0.0094–0.0095× | 11.86× | SLOWER |
| Holdout | `hold.branch.prefix` | Native C engine | 1.1385× | 1.1244–1.1527× | 0.07× | FASTER |
| Holdout | `hold.branch.prefix` | Rust engine | 0.0126× | 0.0124–0.0128× | 3.36× | SLOWER |
| Holdout | `hold.branch.miss` | Python engine | 0.0008× | 0.0008–0.0008× | 80.13× | SLOWER |
| Holdout | `hold.branch.miss` | Native C engine | 1.0614× | 1.0100–1.1140× | 0.00× | FASTER |
| Holdout | `hold.branch.miss` | Rust engine | 0.0112× | 0.0108–0.0116× | 4.57× | SLOWER |
| Holdout | `hold.repeat.nested` | Python engine | 0.0095× | 0.0093–0.0096× | 15.24× | SLOWER |
| Holdout | `hold.repeat.nested` | Native C engine | 1.2802× | 1.2627–1.2965× | 0.64× | FASTER |
| Holdout | `hold.repeat.nested` | Rust engine | 0.0217× | 0.0215–0.0219× | 1.57× | SLOWER |
| Holdout | `hold.lines.records` | Python engine | 0.0083× | 0.0081–0.0084× | 14.74× | SLOWER |
| Holdout | `hold.lines.records` | Native C engine | 1.7709× | 1.6555–1.8522× | 0.38× | FASTER |
| Holdout | `hold.lines.records` | Rust engine | 0.0074× | 0.0072–0.0075× | 2.55× | SLOWER |
| Holdout | `hold.block.dotall` | Python engine | 0.0063× | 0.0062–0.0063× | 18.13× | SLOWER |
| Holdout | `hold.block.dotall` | Native C engine | 1.5569× | 1.5458–1.5676× | 0.08× | FASTER |
| Holdout | `hold.block.dotall` | Rust engine | 0.0131× | 0.0129–0.0132× | 4.00× | SLOWER |
| Holdout | `hold.pattern.verbose` | Python engine | 0.0036× | 0.0035–0.0036× | 15.91× | SLOWER |
| Holdout | `hold.pattern.verbose` | Native C engine | 3.1895× | 3.1468–3.2369× | 0.09× | FASTER |
| Holdout | `hold.pattern.verbose` | Rust engine | 0.0247× | 0.0245–0.0249× | 3.45× | SLOWER |
| Holdout | `hold.mode.ascii` | Python engine | 0.0052× | 0.0051–0.0053× | 7.82× | SLOWER |
| Holdout | `hold.mode.ascii` | Native C engine | 1.1168× | 1.0714–1.1537× | 0.21× | FASTER |
| Holdout | `hold.mode.ascii` | Rust engine | 0.0078× | 0.0077–0.0079× | 3.02× | SLOWER |
| Holdout | `hold.mode.casefold` | Python engine | 0.0081× | 0.0080–0.0082× | 5.44× | SLOWER |
| Holdout | `hold.mode.casefold` | Native C engine | 1.5223× | 1.5004–1.5481× | 0.18× | FASTER |
| Holdout | `hold.mode.casefold` | Rust engine | 0.0104× | 0.0103–0.0106× | 2.93× | SLOWER |
| Holdout | `hold.mode.astral` | Python engine | 0.0095× | 0.0092–0.0100× | 7.06× | SLOWER |
| Holdout | `hold.mode.astral` | Native C engine | 1.6860× | 1.6203–1.7684× | 0.25× | FASTER |
| Holdout | `hold.mode.astral` | Rust engine | 0.0096× | 0.0092–0.0101× | 2.77× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Python engine | 0.0035× | 0.0034–0.0035× | 16.30× | SLOWER |
| Holdout | `hold.look.negative-ahead` | Native C engine | 1.1147× | 1.1073–1.1247× | 0.14× | FASTER |
| Holdout | `hold.look.negative-ahead` | Rust engine | 0.0071× | 0.0069–0.0072× | 3.47× | SLOWER |
| Holdout | `hold.look.negative-behind` | Python engine | 0.0067× | 0.0063–0.0072× | 12.65× | SLOWER |
| Holdout | `hold.look.negative-behind` | Native C engine | 1.4133× | 1.3317–1.5356× | 0.10× | FASTER |
| Holdout | `hold.look.negative-behind` | Rust engine | 0.0102× | 0.0097–0.0111× | 3.19× | SLOWER |
| Holdout | `hold.bytes.replace` | Python engine | 0.0161× | 0.0155–0.0168× | 9.71× | SLOWER |
| Holdout | `hold.bytes.replace` | Native C engine | 1.0463× | 1.0064–1.0831× | 1.16× | FASTER |
| Holdout | `hold.bytes.replace` | Rust engine | 0.0157× | 0.0153–0.0162× | 2.52× | SLOWER |
| Holdout | `hold.bytes.scan` | Python engine | 0.0112× | 0.0110–0.0114× | 8.55× | SLOWER |
| Holdout | `hold.bytes.scan` | Native C engine | 1.4937× | 1.4704–1.5218× | 0.40× | FASTER |
| Holdout | `hold.bytes.scan` | Rust engine | 0.0089× | 0.0088–0.0091× | 1.87× | SLOWER |
| Holdout | `hold.compile.complex` | Python engine | 1.8490× | 1.7563–1.9504× | 0.37× | FASTER |
| Holdout | `hold.compile.complex` | Native C engine | 1.4617× | 1.4095–1.5494× | 1.77× | FASTER |
| Holdout | `hold.compile.complex` | Rust engine | 1.6343× | 1.5666–1.7362× | 0.55× | FASTER |
| Holdout | `hold.module.replace` | Python engine | 0.0209× | 0.0204–0.0216× | 10.12× | SLOWER |
| Holdout | `hold.module.replace` | Native C engine | 1.2638× | 1.2120–1.3038× | 0.04× | FASTER |
| Holdout | `hold.module.replace` | Rust engine | 0.0201× | 0.0197–0.0208× | 2.52× | SLOWER |
| Holdout | `hold.zero.boundary` | Python engine | 0.0083× | 0.0078–0.0091× | 8.20× | SLOWER |
| Holdout | `hold.zero.boundary` | Native C engine | 2.2986× | 2.0192–2.6028× | 0.43× | FASTER |
| Holdout | `hold.zero.boundary` | Rust engine | 0.0139× | 0.0126–0.0155× | 1.67× | SLOWER |
| Holdout | `hold.dense.iter` | Python engine | 0.0154× | 0.0152–0.0158× | 4.92× | SLOWER |
| Holdout | `hold.dense.iter` | Native C engine | 1.5689× | 1.5106–1.6239× | 0.52× | FASTER |
| Holdout | `hold.dense.iter` | Rust engine | 0.0078× | 0.0077–0.0081× | 1.50× | SLOWER |
| Holdout | `hold.capture.optional` | Python engine | 0.0098× | 0.0097–0.0099× | 14.26× | SLOWER |
| Holdout | `hold.capture.optional` | Native C engine | 1.2814× | 1.2614–1.3017× | 0.18× | FASTER |
| Holdout | `hold.capture.optional` | Rust engine | 0.0083× | 0.0081–0.0084× | 2.79× | SLOWER |
| Holdout | `hold.split.limited` | Python engine | 0.0062× | 0.0061–0.0063× | 7.46× | SLOWER |
| Holdout | `hold.split.limited` | Native C engine | 1.5535× | 1.5343–1.5745× | 0.19× | FASTER |
| Holdout | `hold.split.limited` | Rust engine | 0.0072× | 0.0071–0.0073× | 2.83× | SLOWER |
| Holdout | `hold.replace.limited` | Python engine | 0.0131× | 0.0129–0.0135× | 6.04× | SLOWER |
| Holdout | `hold.replace.limited` | Native C engine | 1.4043× | 1.3190–1.4753× | 0.15× | FASTER |
| Holdout | `hold.replace.limited` | Rust engine | 0.0091× | 0.0090–0.0094× | 2.90× | SLOWER |
| Holdout | `hold.bytes.view-long` | Python engine | 0.0066× | 0.0065–0.0066× | 48.64× | SLOWER |
| Holdout | `hold.bytes.view-long` | Native C engine | 1.3306× | 1.3066–1.3486× | 0.60× | FASTER |
| Holdout | `hold.bytes.view-long` | Rust engine | 0.0009× | 0.0009–0.0009× | 5.61× | SLOWER |
| Holdout | `hold.window.search` | Python engine | 0.0185× | 0.0172–0.0199× | 4.40× | SLOWER |
| Holdout | `hold.window.search` | Native C engine | 0.9784× | 0.9499–1.0257× | 0.18× | — |
| Holdout | `hold.window.search` | Rust engine | 0.0158× | 0.0145–0.0175× | 3.32× | SLOWER |
| Holdout | `hold.window.findall` | Python engine | 0.0170× | 0.0168–0.0172× | 4.03× | SLOWER |
| Holdout | `hold.window.findall` | Native C engine | 1.0890× | 1.0783–1.1039× | 0.22× | FASTER |
| Holdout | `hold.window.findall` | Rust engine | 0.0073× | 0.0072–0.0073× | 2.86× | SLOWER |
| Holdout | `hold.window.scanner` | Python engine | 0.0172× | 0.0169–0.0174× | 4.46× | SLOWER |
| Holdout | `hold.window.scanner` | Native C engine | 1.2486× | 1.2277–1.2716× | 0.33× | FASTER |
| Holdout | `hold.window.scanner` | Rust engine | 0.0092× | 0.0090–0.0094× | 2.20× | SLOWER |
| Holdout | `hold.window.match` | Python engine | 0.0325× | 0.0319–0.0330× | 3.55× | SLOWER |
| Holdout | `hold.window.match` | Native C engine | 1.0050× | 0.9884–1.0214× | 0.18× | — |
| Holdout | `hold.window.match` | Rust engine | 0.0174× | 0.0169–0.0177× | 2.46× | SLOWER |
| Holdout | `hold.literal.replace` | Python engine | 0.0065× | 0.0063–0.0068× | 38.88× | SLOWER |
| Holdout | `hold.literal.replace` | Native C engine | 1.3820× | 1.3513–1.4300× | 0.51× | FASTER |
| Holdout | `hold.literal.replace` | Rust engine | 0.0057× | 0.0056–0.0059× | 10.36× | SLOWER |
| Holdout | `hold.template.repeat` | Python engine | 0.0189× | 0.0184–0.0194× | 6.32× | SLOWER |
| Holdout | `hold.template.repeat` | Native C engine | 1.7447× | 1.7056–1.8043× | 0.14× | FASTER |
| Holdout | `hold.template.repeat` | Rust engine | 0.0141× | 0.0138–0.0145× | 2.28× | SLOWER |
| Holdout | `hold.match.miss` | Python engine | 0.0274× | 0.0268–0.0281× | 5.02× | SLOWER |
| Holdout | `hold.match.miss` | Native C engine | 1.1084× | 1.0148–1.1702× | 0.00× | FASTER |
| Holdout | `hold.match.miss` | Rust engine | 0.0072× | 0.0071–0.0073× | 4.20× | SLOWER |
| Holdout | `hold.fullmatch.miss` | Python engine | 0.0171× | 0.0169–0.0173× | 11.09× | SLOWER |
| Holdout | `hold.fullmatch.miss` | Native C engine | 1.6406× | 1.6230–1.6576× | 0.00× | FASTER |
| Holdout | `hold.fullmatch.miss` | Rust engine | 0.0226× | 0.0223–0.0229× | 3.31× | SLOWER |

## Large slowdowns

- Python engine: `cal.search.literal.hit` (0.008×), `cal.search.literal.miss` (0.002×), `cal.search.long-boundary` (0.000×), `cal.search.class-anchor` (0.011×), `cal.match.prefix` (0.023×), `cal.fullmatch.structured` (0.012×), `cal.search.look-capture` (0.007×), `cal.findall.tokens` (0.010×), `cal.finditer.groups` (0.013×), `cal.split.capture` (0.010×), `cal.sub.template` (0.016×), `cal.subn.callable` (0.024×), `cal.bytes.tokens` (0.007×), `cal.unicode.words` (0.006×), `cal.cold.compile-search` (0.298×), `cal.module.warm` (0.011×), `cal.empty.finditer` (0.010×), `cal.backref.fullmatch` (0.019×), `cal.conditional.match` (0.018×), `cal.atomic.search` (0.010×), `cal.byteslike.findall` (0.011×), `cal.unicode-name.search` (0.014×), `cal.ignorecase.findall` (0.007×), `cal.many.split` (0.013×), `cal.scanner.search` (0.013×), `cal.match.surface` (0.014×), `hold.search.literal.hit` (0.007×), `hold.search.literal.miss` (0.002×), `hold.search.long-boundary` (0.000×), `hold.search.class-anchor` (0.010×), `hold.match.prefix` (0.026×), `hold.fullmatch.structured` (0.011×), `hold.search.look-capture` (0.011×), `hold.findall.tokens` (0.011×), `hold.finditer.groups` (0.013×), `hold.split.capture` (0.010×), `hold.sub.template` (0.015×), `hold.subn.callable` (0.027×), `hold.bytes.tokens` (0.011×), `hold.unicode.words` (0.009×), `hold.cold.compile-search` (0.481×), `hold.module.warm` (0.019×), `hold.empty.finditer` (0.009×), `hold.backref.fullmatch` (0.018×), `hold.conditional.match` (0.019×), `hold.atomic.search` (0.011×), `hold.byteslike.findall` (0.011×), `hold.unicode-name.search` (0.013×), `hold.ignorecase.findall` (0.008×), `hold.many.split` (0.013×), `hold.scanner.search` (0.013×), `hold.match.surface` (0.021×), `cal.real.log` (0.003×), `cal.real.url` (0.006×), `cal.real.email` (0.005×), `cal.real.datetime` (0.008×), `cal.real.version` (0.011×), `cal.real.uuid` (0.006×), `cal.real.ip` (0.008×), `cal.real.path` (0.006×), `cal.real.config` (0.009×), `cal.real.comments` (0.006×), `cal.real.whitespace` (0.007×), `cal.real.lines` (0.010×), `cal.real.markup` (0.004×), `cal.real.quotes` (0.004×), `cal.real.csv` (0.005×), `cal.branch.prefix` (0.009×), `cal.branch.miss` (0.001×), `cal.repeat.nested` (0.010×), `cal.lines.records` (0.008×), `cal.block.dotall` (0.007×), `cal.pattern.verbose` (0.004×), `cal.mode.ascii` (0.005×), `cal.mode.casefold` (0.008×), `cal.mode.astral` (0.009×), `cal.look.negative-ahead` (0.004×), `cal.look.negative-behind` (0.007×), `cal.bytes.replace` (0.017×), `cal.bytes.scan` (0.012×), `cal.module.replace` (0.021×), `cal.zero.boundary` (0.008×), `cal.dense.iter` (0.015×), `cal.capture.optional` (0.010×), `cal.split.limited` (0.006×), `cal.replace.limited` (0.013×), `cal.bytes.view-long` (0.007×), `cal.window.search` (0.019×), `cal.window.findall` (0.017×), `cal.window.scanner` (0.017×), `cal.window.match` (0.035×), `cal.literal.replace` (0.006×), `cal.template.repeat` (0.017×), `cal.match.miss` (0.028×), `cal.fullmatch.miss` (0.016×), `hold.real.log` (0.003×), `hold.real.url` (0.005×), `hold.real.email` (0.004×), `hold.real.datetime` (0.008×), `hold.real.version` (0.009×), `hold.real.uuid` (0.006×), `hold.real.ip` (0.009×), `hold.real.path` (0.006×), `hold.real.config` (0.009×), `hold.real.comments` (0.005×), `hold.real.whitespace` (0.007×), `hold.real.lines` (0.009×), `hold.real.markup` (0.005×), `hold.real.quotes` (0.004×), `hold.real.csv` (0.004×), `hold.branch.prefix` (0.009×), `hold.branch.miss` (0.001×), `hold.repeat.nested` (0.009×), `hold.lines.records` (0.008×), `hold.block.dotall` (0.006×), `hold.pattern.verbose` (0.004×), `hold.mode.ascii` (0.005×), `hold.mode.casefold` (0.008×), `hold.mode.astral` (0.010×), `hold.look.negative-ahead` (0.003×), `hold.look.negative-behind` (0.007×), `hold.bytes.replace` (0.016×), `hold.bytes.scan` (0.011×), `hold.module.replace` (0.021×), `hold.zero.boundary` (0.008×), `hold.dense.iter` (0.015×), `hold.capture.optional` (0.010×), `hold.split.limited` (0.006×), `hold.replace.limited` (0.013×), `hold.bytes.view-long` (0.007×), `hold.window.search` (0.019×), `hold.window.findall` (0.017×), `hold.window.scanner` (0.017×), `hold.window.match` (0.032×), `hold.literal.replace` (0.007×), `hold.template.repeat` (0.019×), `hold.match.miss` (0.027×), `hold.fullmatch.miss` (0.017×).
- Rust engine: `cal.search.literal.hit` (0.009×), `cal.search.literal.miss` (0.006×), `cal.search.long-boundary` (0.001×), `cal.search.class-anchor` (0.014×), `cal.match.prefix` (0.015×), `cal.fullmatch.structured` (0.018×), `cal.search.look-capture` (0.016×), `cal.findall.tokens` (0.004×), `cal.finditer.groups` (0.010×), `cal.split.capture` (0.007×), `cal.sub.template` (0.015×), `cal.subn.callable` (0.020×), `cal.bytes.tokens` (0.005×), `cal.unicode.words` (0.010×), `cal.cold.compile-search` (0.712×), `cal.module.warm` (0.032×), `cal.empty.finditer` (0.022×), `cal.backref.fullmatch` (0.019×), `cal.conditional.match` (0.017×), `cal.atomic.search` (0.020×), `cal.byteslike.findall` (0.008×), `cal.unicode-name.search` (0.019×), `cal.ignorecase.findall` (0.008×), `cal.many.split` (0.005×), `cal.scanner.search` (0.009×), `cal.match.surface` (0.047×), `hold.search.literal.hit` (0.009×), `hold.search.literal.miss` (0.006×), `hold.search.long-boundary` (0.001×), `hold.search.class-anchor` (0.013×), `hold.match.prefix` (0.016×), `hold.fullmatch.structured` (0.020×), `hold.search.look-capture` (0.018×), `hold.findall.tokens` (0.006×), `hold.finditer.groups` (0.009×), `hold.split.capture` (0.007×), `hold.sub.template` (0.015×), `hold.subn.callable` (0.022×), `hold.bytes.tokens` (0.009×), `hold.unicode.words` (0.011×), `hold.cold.compile-search` (0.743×), `hold.module.warm` (0.031×), `hold.empty.finditer` (0.021×), `hold.backref.fullmatch` (0.019×), `hold.conditional.match` (0.018×), `hold.atomic.search` (0.022×), `hold.byteslike.findall` (0.008×), `hold.unicode-name.search` (0.020×), `hold.ignorecase.findall` (0.009×), `hold.many.split` (0.005×), `hold.scanner.search` (0.009×), `hold.match.surface` (0.041×), `cal.real.log` (0.006×), `cal.real.url` (0.012×), `cal.real.email` (0.006×), `cal.real.datetime` (0.016×), `cal.real.version` (0.029×), `cal.real.uuid` (0.013×), `cal.real.ip` (0.025×), `cal.real.path` (0.010×), `cal.real.config` (0.018×), `cal.real.comments` (0.004×), `cal.real.whitespace` (0.008×), `cal.real.lines` (0.010×), `cal.real.markup` (0.004×), `cal.real.quotes` (0.007×), `cal.real.csv` (0.011×), `cal.branch.prefix` (0.013×), `cal.branch.miss` (0.013×), `cal.repeat.nested` (0.023×), `cal.lines.records` (0.007×), `cal.block.dotall` (0.014×), `cal.pattern.verbose` (0.020×), `cal.mode.ascii` (0.010×), `cal.mode.casefold` (0.009×), `cal.mode.astral` (0.009×), `cal.look.negative-ahead` (0.007×), `cal.look.negative-behind` (0.010×), `cal.bytes.replace` (0.016×), `cal.bytes.scan` (0.010×), `cal.module.replace` (0.020×), `cal.zero.boundary` (0.013×), `cal.dense.iter` (0.008×), `cal.capture.optional` (0.009×), `cal.split.limited` (0.008×), `cal.replace.limited` (0.010×), `cal.bytes.view-long` (0.001×), `cal.window.search` (0.016×), `cal.window.findall` (0.008×), `cal.window.scanner` (0.009×), `cal.window.match` (0.018×), `cal.literal.replace` (0.005×), `cal.template.repeat` (0.012×), `cal.match.miss` (0.008×), `cal.fullmatch.miss` (0.022×), `hold.real.log` (0.005×), `hold.real.url` (0.010×), `hold.real.email` (0.007×), `hold.real.datetime` (0.018×), `hold.real.version` (0.021×), `hold.real.uuid` (0.013×), `hold.real.ip` (0.021×), `hold.real.path` (0.010×), `hold.real.config` (0.015×), `hold.real.comments` (0.003×), `hold.real.whitespace` (0.007×), `hold.real.lines` (0.009×), `hold.real.markup` (0.003×), `hold.real.quotes` (0.007×), `hold.real.csv` (0.009×), `hold.branch.prefix` (0.013×), `hold.branch.miss` (0.011×), `hold.repeat.nested` (0.022×), `hold.lines.records` (0.007×), `hold.block.dotall` (0.013×), `hold.pattern.verbose` (0.025×), `hold.mode.ascii` (0.008×), `hold.mode.casefold` (0.010×), `hold.mode.astral` (0.010×), `hold.look.negative-ahead` (0.007×), `hold.look.negative-behind` (0.010×), `hold.bytes.replace` (0.016×), `hold.bytes.scan` (0.009×), `hold.module.replace` (0.020×), `hold.zero.boundary` (0.014×), `hold.dense.iter` (0.008×), `hold.capture.optional` (0.008×), `hold.split.limited` (0.007×), `hold.replace.limited` (0.009×), `hold.bytes.view-long` (0.001×), `hold.window.search` (0.016×), `hold.window.findall` (0.007×), `hold.window.scanner` (0.009×), `hold.window.match` (0.017×), `hold.literal.replace` (0.006×), `hold.template.repeat` (0.014×), `hold.match.miss` (0.007×), `hold.fullmatch.miss` (0.023×).

The Python engine performs matching work in Python, and the Rust engine repeatedly prepares data and crosses the Python/Rust boundary; both costs dominate short tasks. Native-C losses expose specific boundary and general-path costs:

No loss is removed from the denominator or hidden from the charts.
