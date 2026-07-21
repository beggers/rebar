# Initial paired performance results

Raw SHA-256: `d5e85ad874e47c05aaa9bcfa5ca72547d1143a931f45675ad9a5e23246e87ae7`. Rows: 1152. All 96 candidate/case results and all 92 regressions are shown below.

## Rankings

| Cohort | Candidate | Geomean | 95% CI | Faster cases | >20% regressions |
| --- | --- | ---: | ---: | ---: | ---: |
| calibration | ast | 0.0099x | 0.0098–0.0100x | 0/16 | 16 |
| calibration | vm | 0.1070x | 0.1059–0.1082x | 1/16 | 15 |
| calibration | rust | 0.0130x | 0.0129–0.0131x | 0/16 | 15 |
| holdout | ast | 0.0111x | 0.0110–0.0112x | 0/16 | 16 |
| holdout | vm | 0.1141x | 0.1131–0.1151x | 1/16 | 15 |
| holdout | rust | 0.0140x | 0.0138–0.0141x | 0/16 | 15 |
| all | ast | 0.0105x | 0.0104–0.0105x | 0/32 | 32 |
| all | vm | 0.1105x | 0.1097–0.1112x | 2/32 | 30 |
| all | rust | 0.0135x | 0.0134–0.0136x | 0/32 | 30 |

## Every case

`REGRESSION` means speedup below 0.8; `FASTER` means the lower confidence bound exceeds 1. Memory is median traced-peak candidate/baseline ratio.

| Cohort | Case | Candidate | Speedup | 95% CI | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| calibration | `cal.search.literal.hit` | ast | 0.0086x | 0.0083–0.0089x | 94.53x | REGRESSION |
| calibration | `cal.search.literal.hit` | vm | 0.1216x | 0.1180–0.1262x | 3.27x | REGRESSION |
| calibration | `cal.search.literal.hit` | rust | 0.0097x | 0.0095–0.0100x | 33.50x | REGRESSION |
| calibration | `cal.search.literal.miss` | ast | 0.0025x | 0.0025–0.0026x | 14152.00x | REGRESSION |
| calibration | `cal.search.literal.miss` | vm | 0.0648x | 0.0587–0.0686x | 392.00x | REGRESSION |
| calibration | `cal.search.literal.miss` | rust | 0.0062x | 0.0061–0.0063x | 4311.00x | REGRESSION |
| calibration | `cal.search.long-boundary` | ast | 0.0003x | 0.0003–0.0004x | 130.00x | REGRESSION |
| calibration | `cal.search.long-boundary` | vm | 0.0129x | 0.0117–0.0143x | 0.31x | REGRESSION |
| calibration | `cal.search.long-boundary` | rust | 0.0011x | 0.0010–0.0012x | 139.92x | REGRESSION |
| calibration | `cal.search.class-anchor` | ast | 0.0114x | 0.0113–0.0115x | 13.78x | REGRESSION |
| calibration | `cal.search.class-anchor` | vm | 0.1943x | 0.1926–0.1960x | 0.35x | REGRESSION |
| calibration | `cal.search.class-anchor` | rust | 0.0148x | 0.0147–0.0149x | 3.31x | REGRESSION |
| calibration | `cal.match.prefix` | ast | 0.0199x | 0.0197–0.0201x | 10.03x | REGRESSION |
| calibration | `cal.match.prefix` | vm | 0.1982x | 0.1907–0.2041x | 0.32x | REGRESSION |
| calibration | `cal.match.prefix` | rust | 0.0158x | 0.0156–0.0159x | 3.10x | REGRESSION |
| calibration | `cal.fullmatch.structured` | ast | 0.0105x | 0.0104–0.0106x | 24.65x | REGRESSION |
| calibration | `cal.fullmatch.structured` | vm | 0.1511x | 0.1476–0.1547x | 5.16x | REGRESSION |
| calibration | `cal.fullmatch.structured` | rust | 0.0180x | 0.0178–0.0183x | 2.99x | REGRESSION |
| calibration | `cal.search.look-capture` | ast | 0.0069x | 0.0069–0.0070x | 21.90x | REGRESSION |
| calibration | `cal.search.look-capture` | vm | 0.1169x | 0.1142–0.1193x | 2.20x | REGRESSION |
| calibration | `cal.search.look-capture` | rust | 0.0163x | 0.0162–0.0164x | 3.24x | REGRESSION |
| calibration | `cal.findall.tokens` | ast | 0.0093x | 0.0092–0.0094x | 11.40x | REGRESSION |
| calibration | `cal.findall.tokens` | vm | 0.0568x | 0.0563–0.0573x | 2.26x | REGRESSION |
| calibration | `cal.findall.tokens` | rust | 0.0038x | 0.0038–0.0039x | 3.12x | REGRESSION |
| calibration | `cal.finditer.groups` | ast | 0.0120x | 0.0117–0.0125x | 13.46x | REGRESSION |
| calibration | `cal.finditer.groups` | vm | 0.1228x | 0.1189–0.1288x | 2.10x | REGRESSION |
| calibration | `cal.finditer.groups` | rust | 0.0099x | 0.0096–0.0103x | 1.86x | REGRESSION |
| calibration | `cal.split.capture` | ast | 0.0104x | 0.0100–0.0107x | 11.00x | REGRESSION |
| calibration | `cal.split.capture` | vm | 0.0461x | 0.0457–0.0465x | 0.86x | REGRESSION |
| calibration | `cal.split.capture` | rust | 0.0068x | 0.0068–0.0069x | 2.47x | REGRESSION |
| calibration | `cal.sub.template` | ast | 0.0165x | 0.0163–0.0167x | 14.07x | REGRESSION |
| calibration | `cal.sub.template` | vm | 0.0761x | 0.0751–0.0772x | 1.95x | REGRESSION |
| calibration | `cal.sub.template` | rust | 0.0163x | 0.0162–0.0165x | 2.31x | REGRESSION |
| calibration | `cal.subn.callable` | ast | 0.0214x | 0.0211–0.0217x | 11.45x | REGRESSION |
| calibration | `cal.subn.callable` | vm | 0.1430x | 0.1399–0.1459x | 1.99x | REGRESSION |
| calibration | `cal.subn.callable` | rust | 0.0197x | 0.0194–0.0199x | 2.60x | REGRESSION |
| calibration | `cal.bytes.tokens` | ast | 0.0091x | 0.0089–0.0091x | 12.56x | REGRESSION |
| calibration | `cal.bytes.tokens` | vm | 0.0713x | 0.0704–0.0723x | 2.65x | REGRESSION |
| calibration | `cal.bytes.tokens` | rust | 0.0066x | 0.0066–0.0066x | 3.26x | REGRESSION |
| calibration | `cal.unicode.words` | ast | 0.0062x | 0.0061–0.0063x | 11.60x | REGRESSION |
| calibration | `cal.unicode.words` | vm | 0.0806x | 0.0745–0.0844x | 2.05x | REGRESSION |
| calibration | `cal.unicode.words` | rust | 0.0099x | 0.0098–0.0100x | 2.60x | REGRESSION |
| calibration | `cal.cold.compile-search` | ast | 0.2964x | 0.2930–0.2997x | 11.57x | REGRESSION |
| calibration | `cal.cold.compile-search` | vm | 1.3072x | 1.2892–1.3279x | 2.08x | FASTER |
| calibration | `cal.cold.compile-search` | rust | 0.8353x | 0.8236–0.8479x | 1.82x | — |
| calibration | `cal.module.warm` | ast | 0.0103x | 0.0102–0.0105x | 18.37x | REGRESSION |
| calibration | `cal.module.warm` | vm | 0.1621x | 0.1602–0.1640x | 3.19x | REGRESSION |
| calibration | `cal.module.warm` | rust | 0.0322x | 0.0317–0.0327x | 3.34x | REGRESSION |
| holdout | `hold.search.literal.hit` | ast | 0.0085x | 0.0085–0.0086x | 94.53x | REGRESSION |
| holdout | `hold.search.literal.hit` | vm | 0.1133x | 0.1117–0.1150x | 3.27x | REGRESSION |
| holdout | `hold.search.literal.hit` | rust | 0.0098x | 0.0096–0.0099x | 33.42x | REGRESSION |
| holdout | `hold.search.literal.miss` | ast | 0.0027x | 0.0027–0.0027x | 14152.00x | REGRESSION |
| holdout | `hold.search.literal.miss` | vm | 0.0656x | 0.0632–0.0677x | 400.00x | REGRESSION |
| holdout | `hold.search.literal.miss` | rust | 0.0063x | 0.0063–0.0064x | 4311.00x | REGRESSION |
| holdout | `hold.search.long-boundary` | ast | 0.0003x | 0.0003–0.0003x | 130.00x | REGRESSION |
| holdout | `hold.search.long-boundary` | vm | 0.0101x | 0.0093–0.0112x | 0.32x | REGRESSION |
| holdout | `hold.search.long-boundary` | rust | 0.0010x | 0.0009–0.0011x | 218.12x | REGRESSION |
| holdout | `hold.search.class-anchor` | ast | 0.0100x | 0.0099–0.0101x | 14.44x | REGRESSION |
| holdout | `hold.search.class-anchor` | vm | 0.1815x | 0.1785–0.1837x | 0.35x | REGRESSION |
| holdout | `hold.search.class-anchor` | rust | 0.0138x | 0.0137–0.0139x | 3.34x | REGRESSION |
| holdout | `hold.match.prefix` | ast | 0.0212x | 0.0210–0.0213x | 9.08x | REGRESSION |
| holdout | `hold.match.prefix` | vm | 0.1966x | 0.1921–0.2005x | 0.32x | REGRESSION |
| holdout | `hold.match.prefix` | rust | 0.0165x | 0.0165–0.0166x | 3.09x | REGRESSION |
| holdout | `hold.fullmatch.structured` | ast | 0.0104x | 0.0102–0.0105x | 24.88x | REGRESSION |
| holdout | `hold.fullmatch.structured` | vm | 0.1624x | 0.1594–0.1653x | 3.98x | REGRESSION |
| holdout | `hold.fullmatch.structured` | rust | 0.0195x | 0.0193–0.0197x | 2.99x | REGRESSION |
| holdout | `hold.search.look-capture` | ast | 0.0077x | 0.0077–0.0077x | 23.81x | REGRESSION |
| holdout | `hold.search.look-capture` | vm | 0.1453x | 0.1418–0.1482x | 1.93x | REGRESSION |
| holdout | `hold.search.look-capture` | rust | 0.0172x | 0.0171–0.0173x | 3.21x | REGRESSION |
| holdout | `hold.findall.tokens` | ast | 0.0095x | 0.0093–0.0096x | 20.57x | REGRESSION |
| holdout | `hold.findall.tokens` | vm | 0.0745x | 0.0734–0.0757x | 3.18x | REGRESSION |
| holdout | `hold.findall.tokens` | rust | 0.0059x | 0.0057–0.0060x | 2.99x | REGRESSION |
| holdout | `hold.finditer.groups` | ast | 0.0118x | 0.0115–0.0121x | 13.46x | REGRESSION |
| holdout | `hold.finditer.groups` | vm | 0.1259x | 0.1225–0.1300x | 2.10x | REGRESSION |
| holdout | `hold.finditer.groups` | rust | 0.0094x | 0.0091–0.0097x | 1.88x | REGRESSION |
| holdout | `hold.split.capture` | ast | 0.0106x | 0.0105–0.0107x | 11.00x | REGRESSION |
| holdout | `hold.split.capture` | vm | 0.0460x | 0.0454–0.0466x | 0.86x | REGRESSION |
| holdout | `hold.split.capture` | rust | 0.0068x | 0.0068–0.0069x | 2.47x | REGRESSION |
| holdout | `hold.sub.template` | ast | 0.0169x | 0.0167–0.0172x | 14.73x | REGRESSION |
| holdout | `hold.sub.template` | vm | 0.0777x | 0.0762–0.0792x | 2.22x | REGRESSION |
| holdout | `hold.sub.template` | rust | 0.0164x | 0.0161–0.0168x | 2.31x | REGRESSION |
| holdout | `hold.subn.callable` | ast | 0.0267x | 0.0245–0.0305x | 10.48x | REGRESSION |
| holdout | `hold.subn.callable` | vm | 0.1552x | 0.1485–0.1644x | 1.99x | REGRESSION |
| holdout | `hold.subn.callable` | rust | 0.0245x | 0.0228–0.0277x | 2.58x | REGRESSION |
| holdout | `hold.bytes.tokens` | ast | 0.0104x | 0.0102–0.0106x | 14.58x | REGRESSION |
| holdout | `hold.bytes.tokens` | vm | 0.0697x | 0.0689–0.0705x | 2.16x | REGRESSION |
| holdout | `hold.bytes.tokens` | rust | 0.0085x | 0.0084–0.0085x | 2.67x | REGRESSION |
| holdout | `hold.unicode.words` | ast | 0.0086x | 0.0084–0.0091x | 11.99x | REGRESSION |
| holdout | `hold.unicode.words` | vm | 0.0948x | 0.0922–0.0996x | 1.94x | REGRESSION |
| holdout | `hold.unicode.words` | rust | 0.0118x | 0.0114–0.0124x | 2.58x | REGRESSION |
| holdout | `hold.cold.compile-search` | ast | 0.5248x | 0.5176–0.5324x | 10.02x | REGRESSION |
| holdout | `hold.cold.compile-search` | vm | 1.4584x | 1.4448–1.4708x | 1.55x | FASTER |
| holdout | `hold.cold.compile-search` | rust | 0.9062x | 0.8992–0.9129x | 1.80x | — |
| holdout | `hold.module.warm` | ast | 0.0187x | 0.0183–0.0192x | 16.47x | REGRESSION |
| holdout | `hold.module.warm` | vm | 0.2595x | 0.2556–0.2652x | 2.53x | REGRESSION |
| holdout | `hold.module.warm` | rust | 0.0338x | 0.0333–0.0348x | 3.33x | REGRESSION |

## Regression explanation

All listed regressions are retained. The AST family pays Python generator/state-allocation and per-position scanning costs. The native VM improves cold compilation but pays state cloning, Python result construction, and wrapper/template costs. Rust pays per-call FFI conversion plus eager continuation allocation. Long misses amplify scanning/boundary work; `findall`, `finditer`, `split`, and substitutions amplify repeated match/result construction. These mechanisms explain the >20% losses shown above; the raw RSS/HWM and traced peaks remain available for inspection.
