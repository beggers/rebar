# Expanded performance: initial results

All 2464 raw timing rows, 168 engine/task results, and 119 large slowdowns are retained. Raw SHA-256: `124cf755874b705ab8023d38c913b5624a592eba35ab08f33fbd2aa60fcc1286`.

## At a glance

The holdout tasks were kept separate from tuning. **1× means the same speed as Python `re`; higher is faster.** A result is clearly faster only when its measured range stays above 1×. A large slowdown means more than 20% slower.

| Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: | ---: |
| Native C engine | **1.1619×** | 1.1482–1.1758× | 19/28 | 4/28 |
| Rust engine | **0.0177×** | 0.0176–0.0179× | 1/28 | 27/28 |
| Python engine | **0.0144×** | 0.0143–0.0146× | 1/28 | 27/28 |

## Overall results

| Task set | Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |
| --- | --- | ---: | ---: | ---: | ---: |
| Practice | Python engine | 0.0138× | 0.0136–0.0139× | 1/28 | 27 |
| Practice | Native C engine | 1.1001× | 1.0850–1.1148× | 17/28 | 7 |
| Practice | Rust engine | 0.0173× | 0.0172–0.0175× | 1/28 | 27 |
| Holdout | Python engine | 0.0144× | 0.0143–0.0146× | 1/28 | 27 |
| Holdout | Native C engine | 1.1619× | 1.1482–1.1758× | 19/28 | 4 |
| Holdout | Rust engine | 0.0177× | 0.0176–0.0179× | 1/28 | 27 |
| All | Python engine | 0.0141× | 0.0140–0.0142× | 2/56 | 54 |
| All | Native C engine | 1.1306× | 1.1210–1.1408× | 36/56 | 11 |
| All | Rust engine | 0.0175× | 0.0174–0.0176× | 2/56 | 54 |

## Every task

`FASTER` means the measured range stays above 1×. `SLOWER` means more than 20% slower. Memory compares median traced Python memory with Python `re`.

| Task set | Task | Engine | Speed | Measured range | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Practice | `cal.search.literal.hit` | Python engine | 0.0083× | 0.0078–0.0090× | 94.53× | SLOWER |
| Practice | `cal.search.literal.hit` | Native C engine | 1.1766× | 1.1178–1.2782× | 0.73× | FASTER |
| Practice | `cal.search.literal.hit` | Rust engine | 0.0095× | 0.0090–0.0103× | 32.90× | SLOWER |
| Practice | `cal.search.literal.miss` | Python engine | 0.0023× | 0.0022–0.0023× | 14152.00× | SLOWER |
| Practice | `cal.search.literal.miss` | Native C engine | 1.1466× | 1.1146–1.1686× | 0.00× | FASTER |
| Practice | `cal.search.literal.miss` | Rust engine | 0.0059× | 0.0059–0.0059× | 4239.00× | SLOWER |
| Practice | `cal.search.long-boundary` | Python engine | 0.0003× | 0.0003–0.0003× | 129.68× | SLOWER |
| Practice | `cal.search.long-boundary` | Native C engine | 12.2409× | 11.4045–13.3009× | 0.07× | FASTER |
| Practice | `cal.search.long-boundary` | Rust engine | 0.0010× | 0.0009–0.0010× | 139.89× | SLOWER |
| Practice | `cal.search.class-anchor` | Python engine | 0.0105× | 0.0101–0.0110× | 13.78× | SLOWER |
| Practice | `cal.search.class-anchor` | Native C engine | 0.9354× | 0.7915–1.0498× | 0.07× | — |
| Practice | `cal.search.class-anchor` | Rust engine | 0.0143× | 0.0138–0.0150× | 3.25× | SLOWER |
| Practice | `cal.match.prefix` | Python engine | 0.0182× | 0.0181–0.0184× | 10.03× | SLOWER |
| Practice | `cal.match.prefix` | Native C engine | 1.1590× | 1.1486–1.1701× | 0.07× | FASTER |
| Practice | `cal.match.prefix` | Rust engine | 0.0150× | 0.0148–0.0151× | 3.04× | SLOWER |
| Practice | `cal.fullmatch.structured` | Python engine | 0.0101× | 0.0099–0.0103× | 24.65× | SLOWER |
| Practice | `cal.fullmatch.structured` | Native C engine | 0.9114× | 0.8983–0.9257× | 0.07× | — |
| Practice | `cal.fullmatch.structured` | Rust engine | 0.0179× | 0.0176–0.0182× | 2.94× | SLOWER |
| Practice | `cal.search.look-capture` | Python engine | 0.0067× | 0.0066–0.0069× | 21.90× | SLOWER |
| Practice | `cal.search.look-capture` | Native C engine | 1.2253× | 1.2067–1.2451× | 0.08× | FASTER |
| Practice | `cal.search.look-capture` | Rust engine | 0.0160× | 0.0157–0.0164× | 3.18× | SLOWER |
| Practice | `cal.findall.tokens` | Python engine | 0.0087× | 0.0080–0.0094× | 11.40× | SLOWER |
| Practice | `cal.findall.tokens` | Native C engine | 0.7701× | 0.6512–0.8791× | 0.28× | SLOWER |
| Practice | `cal.findall.tokens` | Rust engine | 0.0038× | 0.0036–0.0041× | 3.12× | SLOWER |
| Practice | `cal.finditer.groups` | Python engine | 0.0122× | 0.0114–0.0137× | 13.46× | SLOWER |
| Practice | `cal.finditer.groups` | Native C engine | 1.5210× | 1.4129–1.7225× | 0.35× | FASTER |
| Practice | `cal.finditer.groups` | Rust engine | 0.0101× | 0.0097–0.0108× | 1.84× | SLOWER |
| Practice | `cal.split.capture` | Python engine | 0.0102× | 0.0099–0.0106× | 11.00× | SLOWER |
| Practice | `cal.split.capture` | Native C engine | 1.8647× | 1.8221–1.9328× | 0.20× | FASTER |
| Practice | `cal.split.capture` | Rust engine | 0.0068× | 0.0067–0.0070× | 2.47× | SLOWER |
| Practice | `cal.sub.template` | Python engine | 0.0158× | 0.0157–0.0161× | 14.07× | SLOWER |
| Practice | `cal.sub.template` | Native C engine | 1.7763× | 1.5759–1.8977× | 0.12× | FASTER |
| Practice | `cal.sub.template` | Rust engine | 0.0156× | 0.0153–0.0159× | 2.29× | SLOWER |
| Practice | `cal.subn.callable` | Python engine | 0.0211× | 0.0204–0.0221× | 11.45× | SLOWER |
| Practice | `cal.subn.callable` | Native C engine | 1.1452× | 1.1084–1.2059× | 0.25× | FASTER |
| Practice | `cal.subn.callable` | Rust engine | 0.0198× | 0.0192–0.0209× | 2.45× | SLOWER |
| Practice | `cal.bytes.tokens` | Python engine | 0.0080× | 0.0073–0.0089× | 12.56× | SLOWER |
| Practice | `cal.bytes.tokens` | Native C engine | 0.9545× | 0.8672–1.0709× | 0.12× | — |
| Practice | `cal.bytes.tokens` | Rust engine | 0.0061× | 0.0055–0.0068× | 3.21× | SLOWER |
| Practice | `cal.unicode.words` | Python engine | 0.0060× | 0.0059–0.0061× | 11.60× | SLOWER |
| Practice | `cal.unicode.words` | Native C engine | 0.7308× | 0.7259–0.7354× | 0.20× | SLOWER |
| Practice | `cal.unicode.words` | Rust engine | 0.0097× | 0.0095–0.0098× | 2.56× | SLOWER |
| Practice | `cal.cold.compile-search` | Python engine | 0.2821× | 0.2730–0.2905× | 11.57× | SLOWER |
| Practice | `cal.cold.compile-search` | Native C engine | 1.5682× | 1.4659–1.6406× | 0.67× | FASTER |
| Practice | `cal.cold.compile-search` | Rust engine | 0.7092× | 0.6899–0.7305× | 1.80× | SLOWER |
| Practice | `cal.module.warm` | Python engine | 0.0096× | 0.0095–0.0097× | 18.37× | SLOWER |
| Practice | `cal.module.warm` | Native C engine | 1.1745× | 1.1626–1.1873× | 0.07× | FASTER |
| Practice | `cal.module.warm` | Rust engine | 0.0303× | 0.0296–0.0309× | 3.28× | SLOWER |
| Practice | `cal.empty.finditer` | Python engine | 0.0107× | 0.0103–0.0110× | 7.78× | SLOWER |
| Practice | `cal.empty.finditer` | Native C engine | 0.7067× | 0.6920–0.7217× | 0.55× | SLOWER |
| Practice | `cal.empty.finditer` | Rust engine | 0.0224× | 0.0219–0.0229× | 1.59× | SLOWER |
| Practice | `cal.backref.fullmatch` | Python engine | 0.0171× | 0.0159–0.0196× | 10.38× | SLOWER |
| Practice | `cal.backref.fullmatch` | Native C engine | 1.0872× | 1.0153–1.2330× | 0.08× | FASTER |
| Practice | `cal.backref.fullmatch` | Rust engine | 0.0193× | 0.0180–0.0220× | 2.93× | SLOWER |
| Practice | `cal.conditional.match` | Python engine | 0.0145× | 0.0137–0.0161× | 14.03× | SLOWER |
| Practice | `cal.conditional.match` | Native C engine | 0.9351× | 0.7953–1.0496× | 0.08× | — |
| Practice | `cal.conditional.match` | Rust engine | 0.0167× | 0.0157–0.0187× | 2.86× | SLOWER |
| Practice | `cal.atomic.search` | Python engine | 0.0096× | 0.0095–0.0097× | 10.37× | SLOWER |
| Practice | `cal.atomic.search` | Native C engine | 0.4949× | 0.4851–0.5039× | 0.50× | SLOWER |
| Practice | `cal.atomic.search` | Rust engine | 0.0189× | 0.0187–0.0191× | 3.02× | SLOWER |
| Practice | `cal.byteslike.findall` | Python engine | 0.0106× | 0.0102–0.0114× | 12.14× | SLOWER |
| Practice | `cal.byteslike.findall` | Native C engine | 2.0032× | 1.9315–2.1369× | 0.18× | FASTER |
| Practice | `cal.byteslike.findall` | Rust engine | 0.0084× | 0.0081–0.0090× | 2.69× | SLOWER |
| Practice | `cal.unicode-name.search` | Python engine | 0.0131× | 0.0128–0.0135× | 9.15× | SLOWER |
| Practice | `cal.unicode-name.search` | Native C engine | 1.2877× | 1.1981–1.3588× | 0.07× | FASTER |
| Practice | `cal.unicode-name.search` | Rust engine | 0.0199× | 0.0195–0.0206× | 3.02× | SLOWER |
| Practice | `cal.ignorecase.findall` | Python engine | 0.0070× | 0.0069–0.0070× | 11.35× | SLOWER |
| Practice | `cal.ignorecase.findall` | Native C engine | 1.0724× | 1.0613–1.0841× | 0.16× | FASTER |
| Practice | `cal.ignorecase.findall` | Rust engine | 0.0082× | 0.0081–0.0083× | 2.83× | SLOWER |
| Practice | `cal.many.split` | Python engine | 0.0122× | 0.0119–0.0127× | 8.67× | SLOWER |
| Practice | `cal.many.split` | Native C engine | 1.1776× | 1.1311–1.2347× | 0.20× | FASTER |
| Practice | `cal.many.split` | Rust engine | 0.0044× | 0.0043–0.0046× | 2.70× | SLOWER |
| Practice | `cal.escape.text` | Python engine | 0.2345× | 0.2282–0.2404× | 48.84× | SLOWER |
| Practice | `cal.escape.text` | Native C engine | 0.2390× | 0.2345–0.2435× | 48.84× | SLOWER |
| Practice | `cal.escape.text` | Rust engine | 0.2374× | 0.2286–0.2447× | 48.84× | SLOWER |
| Practice | `cal.compile.only` | Python engine | 2.3891× | 2.2913–2.4830× | 0.35× | FASTER |
| Practice | `cal.compile.only` | Native C engine | 1.7337× | 1.6481–1.8031× | 0.67× | FASTER |
| Practice | `cal.compile.only` | Rust engine | 1.8574× | 1.8233–1.8945× | 0.56× | FASTER |
| Practice | `cal.scanner.search` | Python engine | 0.0109× | 0.0106–0.0114× | 13.31× | SLOWER |
| Practice | `cal.scanner.search` | Native C engine | 0.7419× | 0.6909–0.7884× | 0.35× | SLOWER |
| Practice | `cal.scanner.search` | Rust engine | 0.0084× | 0.0082–0.0087× | 1.89× | SLOWER |
| Practice | `cal.match.surface` | Python engine | 0.0134× | 0.0133–0.0135× | 23.05× | SLOWER |
| Practice | `cal.match.surface` | Native C engine | 0.3563× | 0.3532–0.3589× | 0.98× | SLOWER |
| Practice | `cal.match.surface` | Rust engine | 0.0467× | 0.0462–0.0471× | 3.15× | SLOWER |
| Holdout | `hold.search.literal.hit` | Python engine | 0.0076× | 0.0076–0.0077× | 94.53× | SLOWER |
| Holdout | `hold.search.literal.hit` | Native C engine | 1.1001× | 1.0892–1.1105× | 0.73× | FASTER |
| Holdout | `hold.search.literal.hit` | Rust engine | 0.0090× | 0.0089–0.0091× | 32.83× | SLOWER |
| Holdout | `hold.search.literal.miss` | Python engine | 0.0024× | 0.0024–0.0024× | 14152.00× | SLOWER |
| Holdout | `hold.search.literal.miss` | Native C engine | 1.1509× | 1.1409–1.1609× | 0.00× | FASTER |
| Holdout | `hold.search.literal.miss` | Rust engine | 0.0058× | 0.0058–0.0058× | 4239.00× | SLOWER |
| Holdout | `hold.search.long-boundary` | Python engine | 0.0003× | 0.0003–0.0003× | 130.00× | SLOWER |
| Holdout | `hold.search.long-boundary` | Native C engine | 18.1913× | 16.7161–20.0554× | 0.07× | FASTER |
| Holdout | `hold.search.long-boundary` | Rust engine | 0.0010× | 0.0009–0.0011× | 218.09× | SLOWER |
| Holdout | `hold.search.class-anchor` | Python engine | 0.0118× | 0.0103–0.0136× | 14.44× | SLOWER |
| Holdout | `hold.search.class-anchor` | Native C engine | 1.1154× | 0.9345–1.3370× | 0.07× | — |
| Holdout | `hold.search.class-anchor` | Rust engine | 0.0165× | 0.0143–0.0191× | 3.28× | SLOWER |
| Holdout | `hold.match.prefix` | Python engine | 0.0197× | 0.0195–0.0199× | 9.08× | SLOWER |
| Holdout | `hold.match.prefix` | Native C engine | 1.1458× | 1.0776–1.1845× | 0.07× | FASTER |
| Holdout | `hold.match.prefix` | Rust engine | 0.0157× | 0.0156–0.0158× | 3.03× | SLOWER |
| Holdout | `hold.fullmatch.structured` | Python engine | 0.0102× | 0.0098–0.0108× | 24.88× | SLOWER |
| Holdout | `hold.fullmatch.structured` | Native C engine | 0.9155× | 0.8771–0.9707× | 0.07× | — |
| Holdout | `hold.fullmatch.structured` | Rust engine | 0.0195× | 0.0187–0.0206× | 2.93× | SLOWER |
| Holdout | `hold.search.look-capture` | Python engine | 0.0075× | 0.0073–0.0079× | 23.81× | SLOWER |
| Holdout | `hold.search.look-capture` | Native C engine | 1.0505× | 1.0183–1.1046× | 0.08× | FASTER |
| Holdout | `hold.search.look-capture` | Rust engine | 0.0168× | 0.0162–0.0178× | 3.15× | SLOWER |
| Holdout | `hold.findall.tokens` | Python engine | 0.0092× | 0.0089–0.0098× | 20.57× | SLOWER |
| Holdout | `hold.findall.tokens` | Native C engine | 1.3868× | 1.3324–1.4685× | 0.21× | FASTER |
| Holdout | `hold.findall.tokens` | Rust engine | 0.0058× | 0.0056–0.0062× | 2.96× | SLOWER |
| Holdout | `hold.finditer.groups` | Python engine | 0.0107× | 0.0104–0.0110× | 13.46× | SLOWER |
| Holdout | `hold.finditer.groups` | Native C engine | 1.3197× | 1.2968–1.3433× | 0.35× | FASTER |
| Holdout | `hold.finditer.groups` | Rust engine | 0.0087× | 0.0085–0.0088× | 1.86× | SLOWER |
| Holdout | `hold.split.capture` | Python engine | 0.0091× | 0.0089–0.0096× | 11.00× | SLOWER |
| Holdout | `hold.split.capture` | Native C engine | 1.6380× | 1.5689–1.7349× | 0.20× | FASTER |
| Holdout | `hold.split.capture` | Rust engine | 0.0061× | 0.0059–0.0063× | 2.47× | SLOWER |
| Holdout | `hold.sub.template` | Python engine | 0.0148× | 0.0146–0.0149× | 14.73× | SLOWER |
| Holdout | `hold.sub.template` | Native C engine | 1.6926× | 1.5745–1.7656× | 0.12× | FASTER |
| Holdout | `hold.sub.template` | Rust engine | 0.0146× | 0.0145–0.0148× | 2.29× | SLOWER |
| Holdout | `hold.subn.callable` | Python engine | 0.0225× | 0.0221–0.0229× | 10.48× | SLOWER |
| Holdout | `hold.subn.callable` | Native C engine | 1.0416× | 0.9744–1.0880× | 0.25× | — |
| Holdout | `hold.subn.callable` | Rust engine | 0.0208× | 0.0203–0.0213× | 2.43× | SLOWER |
| Holdout | `hold.bytes.tokens` | Python engine | 0.0090× | 0.0088–0.0093× | 14.58× | SLOWER |
| Holdout | `hold.bytes.tokens` | Native C engine | 1.7773× | 1.7439–1.8152× | 0.18× | FASTER |
| Holdout | `hold.bytes.tokens` | Rust engine | 0.0077× | 0.0076–0.0079× | 2.66× | SLOWER |
| Holdout | `hold.unicode.words` | Python engine | 0.0083× | 0.0082–0.0084× | 11.99× | SLOWER |
| Holdout | `hold.unicode.words` | Native C engine | 1.5742× | 1.4174–1.6652× | 0.20× | FASTER |
| Holdout | `hold.unicode.words` | Rust engine | 0.0114× | 0.0114–0.0115× | 2.54× | SLOWER |
| Holdout | `hold.cold.compile-search` | Python engine | 0.4848× | 0.4807–0.4893× | 10.02× | SLOWER |
| Holdout | `hold.cold.compile-search` | Native C engine | 1.5936× | 1.5822–1.6054× | 0.69× | FASTER |
| Holdout | `hold.cold.compile-search` | Rust engine | 0.7598× | 0.7526–0.7662× | 1.77× | SLOWER |
| Holdout | `hold.module.warm` | Python engine | 0.0176× | 0.0164–0.0197× | 16.47× | SLOWER |
| Holdout | `hold.module.warm` | Native C engine | 1.1135× | 1.0189–1.2557× | 0.07× | FASTER |
| Holdout | `hold.module.warm` | Rust engine | 0.0333× | 0.0316–0.0370× | 3.27× | SLOWER |
| Holdout | `hold.empty.finditer` | Python engine | 0.0099× | 0.0094–0.0106× | 8.22× | SLOWER |
| Holdout | `hold.empty.finditer` | Native C engine | 0.6610× | 0.6291–0.7036× | 0.57× | SLOWER |
| Holdout | `hold.empty.finditer` | Rust engine | 0.0223× | 0.0211–0.0239× | 1.52× | SLOWER |
| Holdout | `hold.backref.fullmatch` | Python engine | 0.0154× | 0.0153–0.0156× | 10.38× | SLOWER |
| Holdout | `hold.backref.fullmatch` | Native C engine | 0.9670× | 0.9562–0.9787× | 0.08× | — |
| Holdout | `hold.backref.fullmatch` | Rust engine | 0.0182× | 0.0181–0.0183× | 2.93× | SLOWER |
| Holdout | `hold.conditional.match` | Python engine | 0.0147× | 0.0141–0.0158× | 13.14× | SLOWER |
| Holdout | `hold.conditional.match` | Native C engine | 1.0793× | 1.0314–1.1616× | 0.08× | FASTER |
| Holdout | `hold.conditional.match` | Rust engine | 0.0187× | 0.0177–0.0202× | 2.83× | SLOWER |
| Holdout | `hold.atomic.search` | Python engine | 0.0099× | 0.0099–0.0100× | 11.71× | SLOWER |
| Holdout | `hold.atomic.search` | Native C engine | 0.8120× | 0.8048–0.8189× | 0.07× | — |
| Holdout | `hold.atomic.search` | Rust engine | 0.0213× | 0.0210–0.0215× | 3.02× | SLOWER |
| Holdout | `hold.byteslike.findall` | Python engine | 0.0102× | 0.0101–0.0103× | 12.14× | SLOWER |
| Holdout | `hold.byteslike.findall` | Native C engine | 1.8969× | 1.8790–1.9150× | 0.18× | FASTER |
| Holdout | `hold.byteslike.findall` | Rust engine | 0.0081× | 0.0080–0.0081× | 2.69× | SLOWER |
| Holdout | `hold.unicode-name.search` | Python engine | 0.0117× | 0.0116–0.0118× | 9.80× | SLOWER |
| Holdout | `hold.unicode-name.search` | Native C engine | 1.2361× | 1.1417–1.2909× | 0.07× | FASTER |
| Holdout | `hold.unicode-name.search` | Rust engine | 0.0190× | 0.0188–0.0191× | 3.03× | SLOWER |
| Holdout | `hold.ignorecase.findall` | Python engine | 0.0060× | 0.0059–0.0060× | 10.50× | SLOWER |
| Holdout | `hold.ignorecase.findall` | Native C engine | 1.0379× | 1.0306–1.0464× | 0.16× | FASTER |
| Holdout | `hold.ignorecase.findall` | Rust engine | 0.0087× | 0.0085–0.0088× | 2.81× | SLOWER |
| Holdout | `hold.many.split` | Python engine | 0.0126× | 0.0121–0.0134× | 8.67× | SLOWER |
| Holdout | `hold.many.split` | Native C engine | 1.2034× | 1.1409–1.2794× | 0.20× | FASTER |
| Holdout | `hold.many.split` | Rust engine | 0.0046× | 0.0044–0.0049× | 2.70× | SLOWER |
| Holdout | `hold.escape.bytes` | Python engine | 0.1696× | 0.1631–0.1795× | 24.36× | SLOWER |
| Holdout | `hold.escape.bytes` | Native C engine | 0.1699× | 0.1632–0.1808× | 24.36× | SLOWER |
| Holdout | `hold.escape.bytes` | Rust engine | 0.1690× | 0.1627–0.1790× | 24.36× | SLOWER |
| Holdout | `hold.compile.only` | Python engine | 2.1998× | 2.1593–2.2410× | 0.37× | FASTER |
| Holdout | `hold.compile.only` | Native C engine | 1.5135× | 1.4946–1.5330× | 0.83× | FASTER |
| Holdout | `hold.compile.only` | Rust engine | 1.7387× | 1.7025–1.7706× | 0.60× | FASTER |
| Holdout | `hold.scanner.search` | Python engine | 0.0106× | 0.0105–0.0107× | 13.31× | SLOWER |
| Holdout | `hold.scanner.search` | Native C engine | 0.7412× | 0.7319–0.7495× | 0.35× | SLOWER |
| Holdout | `hold.scanner.search` | Rust engine | 0.0082× | 0.0082–0.0083× | 1.89× | SLOWER |
| Holdout | `hold.match.surface` | Python engine | 0.0202× | 0.0200–0.0204× | 21.25× | SLOWER |
| Holdout | `hold.match.surface` | Native C engine | 0.2875× | 0.2849–0.2900× | 0.97× | SLOWER |
| Holdout | `hold.match.surface` | Rust engine | 0.0419× | 0.0416–0.0422× | 3.14× | SLOWER |

## Large slowdowns

- Python engine: `cal.search.literal.hit` (0.008×), `cal.search.literal.miss` (0.002×), `cal.search.long-boundary` (0.000×), `cal.search.class-anchor` (0.011×), `cal.match.prefix` (0.018×), `cal.fullmatch.structured` (0.010×), `cal.search.look-capture` (0.007×), `cal.findall.tokens` (0.009×), `cal.finditer.groups` (0.012×), `cal.split.capture` (0.010×), `cal.sub.template` (0.016×), `cal.subn.callable` (0.021×), `cal.bytes.tokens` (0.008×), `cal.unicode.words` (0.006×), `cal.cold.compile-search` (0.282×), `cal.module.warm` (0.010×), `cal.empty.finditer` (0.011×), `cal.backref.fullmatch` (0.017×), `cal.conditional.match` (0.014×), `cal.atomic.search` (0.010×), `cal.byteslike.findall` (0.011×), `cal.unicode-name.search` (0.013×), `cal.ignorecase.findall` (0.007×), `cal.many.split` (0.012×), `cal.escape.text` (0.234×), `cal.scanner.search` (0.011×), `cal.match.surface` (0.013×), `hold.search.literal.hit` (0.008×), `hold.search.literal.miss` (0.002×), `hold.search.long-boundary` (0.000×), `hold.search.class-anchor` (0.012×), `hold.match.prefix` (0.020×), `hold.fullmatch.structured` (0.010×), `hold.search.look-capture` (0.007×), `hold.findall.tokens` (0.009×), `hold.finditer.groups` (0.011×), `hold.split.capture` (0.009×), `hold.sub.template` (0.015×), `hold.subn.callable` (0.022×), `hold.bytes.tokens` (0.009×), `hold.unicode.words` (0.008×), `hold.cold.compile-search` (0.485×), `hold.module.warm` (0.018×), `hold.empty.finditer` (0.010×), `hold.backref.fullmatch` (0.015×), `hold.conditional.match` (0.015×), `hold.atomic.search` (0.010×), `hold.byteslike.findall` (0.010×), `hold.unicode-name.search` (0.012×), `hold.ignorecase.findall` (0.006×), `hold.many.split` (0.013×), `hold.escape.bytes` (0.170×), `hold.scanner.search` (0.011×), `hold.match.surface` (0.020×).
- Rust engine: `cal.search.literal.hit` (0.009×), `cal.search.literal.miss` (0.006×), `cal.search.long-boundary` (0.001×), `cal.search.class-anchor` (0.014×), `cal.match.prefix` (0.015×), `cal.fullmatch.structured` (0.018×), `cal.search.look-capture` (0.016×), `cal.findall.tokens` (0.004×), `cal.finditer.groups` (0.010×), `cal.split.capture` (0.007×), `cal.sub.template` (0.016×), `cal.subn.callable` (0.020×), `cal.bytes.tokens` (0.006×), `cal.unicode.words` (0.010×), `cal.cold.compile-search` (0.709×), `cal.module.warm` (0.030×), `cal.empty.finditer` (0.022×), `cal.backref.fullmatch` (0.019×), `cal.conditional.match` (0.017×), `cal.atomic.search` (0.019×), `cal.byteslike.findall` (0.008×), `cal.unicode-name.search` (0.020×), `cal.ignorecase.findall` (0.008×), `cal.many.split` (0.004×), `cal.escape.text` (0.237×), `cal.scanner.search` (0.008×), `cal.match.surface` (0.047×), `hold.search.literal.hit` (0.009×), `hold.search.literal.miss` (0.006×), `hold.search.long-boundary` (0.001×), `hold.search.class-anchor` (0.016×), `hold.match.prefix` (0.016×), `hold.fullmatch.structured` (0.019×), `hold.search.look-capture` (0.017×), `hold.findall.tokens` (0.006×), `hold.finditer.groups` (0.009×), `hold.split.capture` (0.006×), `hold.sub.template` (0.015×), `hold.subn.callable` (0.021×), `hold.bytes.tokens` (0.008×), `hold.unicode.words` (0.011×), `hold.cold.compile-search` (0.760×), `hold.module.warm` (0.033×), `hold.empty.finditer` (0.022×), `hold.backref.fullmatch` (0.018×), `hold.conditional.match` (0.019×), `hold.atomic.search` (0.021×), `hold.byteslike.findall` (0.008×), `hold.unicode-name.search` (0.019×), `hold.ignorecase.findall` (0.009×), `hold.many.split` (0.005×), `hold.escape.bytes` (0.169×), `hold.scanner.search` (0.008×), `hold.match.surface` (0.042×).
- Native C engine: `cal.findall.tokens` (0.770×), `cal.unicode.words` (0.731×), `cal.empty.finditer` (0.707×), `cal.atomic.search` (0.495×), `cal.escape.text` (0.239×), `cal.scanner.search` (0.742×), `cal.match.surface` (0.356×), `hold.empty.finditer` (0.661×), `hold.escape.bytes` (0.170×), `hold.scanner.search` (0.741×), `hold.match.surface` (0.288×).

The Python engine performs matching work in Python, and the Rust engine repeatedly prepares data and crosses the Python/Rust boundary; both costs dominate short tasks. Native-C losses expose specific boundary and general-path costs:
- Repeated text/Unicode matching needs character-category and word-boundary checks that cannot use the simplest one-pass scan.
- Empty matches and controlled branches use the general backtracking/iterator path and construct more match state.
- Escaping currently loops over every character in Python, explaining both the time and extra traced-memory cost.
- Scanning repeatedly returns through a small Python wrapper, so per-match boundary and object costs accumulate.
- Reading many groups and expanding a template makes several Python/C and Python-template calls for one match.

No loss is removed from the denominator or hidden from the charts.
