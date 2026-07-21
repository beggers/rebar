# One-pass native scanner with structured-loop experiment

Raw SHA-256: `ee3156f4620f51a7862c09c6375d436fc506f7f39806425fae4feafb3ba18062`. Rows: 1152. All 96 candidate/case results and all 63 regressions are shown below.

## Rankings

| Cohort | Candidate | Geomean | 95% CI | Faster cases | >20% regressions |
| --- | --- | ---: | ---: | ---: | ---: |
| calibration | ast | 0.0100x | 0.0098–0.0102x | 0/16 | 16 |
| calibration | vm | 1.3400x | 1.3061–1.3724x | 11/16 | 1 |
| calibration | rust | 0.0128x | 0.0126–0.0131x | 0/16 | 15 |
| holdout | ast | 0.0111x | 0.0109–0.0112x | 0/16 | 16 |
| holdout | vm | 1.4697x | 1.4478–1.4941x | 14/16 | 0 |
| holdout | rust | 0.0137x | 0.0135–0.0139x | 0/16 | 15 |
| all | ast | 0.0105x | 0.0104–0.0106x | 0/32 | 32 |
| all | vm | 1.4034x | 1.3832–1.4241x | 25/32 | 1 |
| all | rust | 0.0133x | 0.0131–0.0134x | 0/32 | 30 |

## Every case

`REGRESSION` means speedup below 0.8; `FASTER` means the lower confidence bound exceeds 1. Memory is median traced-peak candidate/baseline ratio.

| Cohort | Case | Candidate | Speedup | 95% CI | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| calibration | `cal.search.literal.hit` | ast | 0.0084x | 0.0080–0.0089x | 94.53x | REGRESSION |
| calibration | `cal.search.literal.hit` | vm | 1.1494x | 1.1214–1.1876x | 0.73x | FASTER |
| calibration | `cal.search.literal.hit` | rust | 0.0095x | 0.0093–0.0098x | 33.50x | REGRESSION |
| calibration | `cal.search.literal.miss` | ast | 0.0026x | 0.0025–0.0029x | 14152.00x | REGRESSION |
| calibration | `cal.search.literal.miss` | vm | 1.2396x | 1.1827–1.3437x | 0.00x | FASTER |
| calibration | `cal.search.literal.miss` | rust | 0.0065x | 0.0061–0.0070x | 4311.00x | REGRESSION |
| calibration | `cal.search.long-boundary` | ast | 0.0003x | 0.0003–0.0003x | 130.00x | REGRESSION |
| calibration | `cal.search.long-boundary` | vm | 13.1183x | 12.0613–14.6463x | 0.07x | FASTER |
| calibration | `cal.search.long-boundary` | rust | 0.0010x | 0.0010–0.0012x | 139.92x | REGRESSION |
| calibration | `cal.search.class-anchor` | ast | 0.0116x | 0.0114–0.0119x | 13.78x | REGRESSION |
| calibration | `cal.search.class-anchor` | vm | 1.0651x | 1.0441–1.0910x | 0.07x | FASTER |
| calibration | `cal.search.class-anchor` | rust | 0.0149x | 0.0147–0.0152x | 3.31x | REGRESSION |
| calibration | `cal.match.prefix` | ast | 0.0203x | 0.0198–0.0209x | 10.03x | REGRESSION |
| calibration | `cal.match.prefix` | vm | 1.2370x | 1.2059–1.2727x | 0.07x | FASTER |
| calibration | `cal.match.prefix` | rust | 0.0159x | 0.0156–0.0164x | 3.10x | REGRESSION |
| calibration | `cal.fullmatch.structured` | ast | 0.0107x | 0.0105–0.0108x | 24.65x | REGRESSION |
| calibration | `cal.fullmatch.structured` | vm | 0.9767x | 0.9587–0.9938x | 0.07x | — |
| calibration | `cal.fullmatch.structured` | rust | 0.0176x | 0.0166–0.0185x | 2.99x | REGRESSION |
| calibration | `cal.search.look-capture` | ast | 0.0073x | 0.0069–0.0080x | 21.90x | REGRESSION |
| calibration | `cal.search.look-capture` | vm | 1.3157x | 1.2465–1.4409x | 0.08x | FASTER |
| calibration | `cal.search.look-capture` | rust | 0.0168x | 0.0158–0.0183x | 3.24x | REGRESSION |
| calibration | `cal.findall.tokens` | ast | 0.0094x | 0.0089–0.0097x | 11.40x | REGRESSION |
| calibration | `cal.findall.tokens` | vm | 0.8696x | 0.7620–0.9358x | 0.28x | — |
| calibration | `cal.findall.tokens` | rust | 0.0039x | 0.0037–0.0040x | 3.12x | REGRESSION |
| calibration | `cal.finditer.groups` | ast | 0.0124x | 0.0119–0.0130x | 13.46x | REGRESSION |
| calibration | `cal.finditer.groups` | vm | 1.4117x | 1.3631–1.4729x | 0.35x | FASTER |
| calibration | `cal.finditer.groups` | rust | 0.0100x | 0.0097–0.0105x | 1.86x | REGRESSION |
| calibration | `cal.split.capture` | ast | 0.0108x | 0.0107–0.0109x | 11.00x | REGRESSION |
| calibration | `cal.split.capture` | vm | 1.1132x | 1.0820–1.1376x | 0.20x | FASTER |
| calibration | `cal.split.capture` | rust | 0.0068x | 0.0067–0.0068x | 2.47x | REGRESSION |
| calibration | `cal.sub.template` | ast | 0.0163x | 0.0148–0.0172x | 14.07x | REGRESSION |
| calibration | `cal.sub.template` | vm | 1.5705x | 1.2303–1.8089x | 0.12x | FASTER |
| calibration | `cal.sub.template` | rust | 0.0158x | 0.0151–0.0164x | 2.31x | REGRESSION |
| calibration | `cal.subn.callable` | ast | 0.0244x | 0.0215–0.0310x | 11.45x | REGRESSION |
| calibration | `cal.subn.callable` | vm | 1.1717x | 0.9345–1.5429x | 0.25x | — |
| calibration | `cal.subn.callable` | rust | 0.0212x | 0.0172–0.0282x | 2.60x | REGRESSION |
| calibration | `cal.bytes.tokens` | ast | 0.0077x | 0.0075–0.0079x | 12.56x | REGRESSION |
| calibration | `cal.bytes.tokens` | vm | 0.8904x | 0.8830–0.8970x | 0.12x | — |
| calibration | `cal.bytes.tokens` | rust | 0.0055x | 0.0051–0.0057x | 3.26x | REGRESSION |
| calibration | `cal.unicode.words` | ast | 0.0064x | 0.0062–0.0068x | 11.60x | REGRESSION |
| calibration | `cal.unicode.words` | vm | 0.7402x | 0.7143–0.7796x | 0.20x | REGRESSION |
| calibration | `cal.unicode.words` | rust | 0.0101x | 0.0098–0.0105x | 2.60x | REGRESSION |
| calibration | `cal.cold.compile-search` | ast | 0.2964x | 0.2917–0.3013x | 11.57x | REGRESSION |
| calibration | `cal.cold.compile-search` | vm | 1.8117x | 1.7676–1.8444x | 0.60x | FASTER |
| calibration | `cal.cold.compile-search` | rust | 0.8152x | 0.8017–0.8282x | 1.82x | — |
| calibration | `cal.module.warm` | ast | 0.0101x | 0.0099–0.0102x | 18.37x | REGRESSION |
| calibration | `cal.module.warm` | vm | 1.1370x | 1.0657–1.1855x | 0.07x | FASTER |
| calibration | `cal.module.warm` | rust | 0.0309x | 0.0304–0.0313x | 3.34x | REGRESSION |
| holdout | `hold.search.literal.hit` | ast | 0.0085x | 0.0084–0.0086x | 94.53x | REGRESSION |
| holdout | `hold.search.literal.hit` | vm | 1.1082x | 1.0245–1.1619x | 0.73x | FASTER |
| holdout | `hold.search.literal.hit` | rust | 0.0097x | 0.0096–0.0098x | 33.42x | REGRESSION |
| holdout | `hold.search.literal.miss` | ast | 0.0028x | 0.0026–0.0031x | 14152.00x | REGRESSION |
| holdout | `hold.search.literal.miss` | vm | 1.2795x | 1.1565–1.4626x | 0.00x | FASTER |
| holdout | `hold.search.literal.miss` | rust | 0.0067x | 0.0061–0.0075x | 4311.00x | REGRESSION |
| holdout | `hold.search.long-boundary` | ast | 0.0003x | 0.0003–0.0003x | 130.31x | REGRESSION |
| holdout | `hold.search.long-boundary` | vm | 15.9479x | 14.4716–17.6701x | 0.07x | FASTER |
| holdout | `hold.search.long-boundary` | rust | 0.0010x | 0.0009–0.0011x | 218.12x | REGRESSION |
| holdout | `hold.search.class-anchor` | ast | 0.0101x | 0.0098–0.0106x | 14.44x | REGRESSION |
| holdout | `hold.search.class-anchor` | vm | 1.0188x | 0.9891–1.0661x | 0.07x | — |
| holdout | `hold.search.class-anchor` | rust | 0.0138x | 0.0135–0.0144x | 3.34x | REGRESSION |
| holdout | `hold.match.prefix` | ast | 0.0238x | 0.0211–0.0282x | 9.08x | REGRESSION |
| holdout | `hold.match.prefix` | vm | 1.1917x | 1.1635–1.2105x | 0.07x | FASTER |
| holdout | `hold.match.prefix` | rust | 0.0172x | 0.0164–0.0186x | 3.09x | REGRESSION |
| holdout | `hold.fullmatch.structured` | ast | 0.0102x | 0.0101–0.0103x | 24.88x | REGRESSION |
| holdout | `hold.fullmatch.structured` | vm | 0.9007x | 0.8629–0.9312x | 0.07x | — |
| holdout | `hold.fullmatch.structured` | rust | 0.0186x | 0.0183–0.0189x | 2.99x | REGRESSION |
| holdout | `hold.search.look-capture` | ast | 0.0076x | 0.0076–0.0077x | 23.81x | REGRESSION |
| holdout | `hold.search.look-capture` | vm | 1.0634x | 1.0543–1.0724x | 0.08x | FASTER |
| holdout | `hold.search.look-capture` | rust | 0.0168x | 0.0167–0.0168x | 3.21x | REGRESSION |
| holdout | `hold.findall.tokens` | ast | 0.0090x | 0.0089–0.0091x | 20.57x | REGRESSION |
| holdout | `hold.findall.tokens` | vm | 1.1991x | 1.1552–1.2288x | 0.21x | FASTER |
| holdout | `hold.findall.tokens` | rust | 0.0055x | 0.0055–0.0056x | 2.99x | REGRESSION |
| holdout | `hold.finditer.groups` | ast | 0.0122x | 0.0112–0.0139x | 13.46x | REGRESSION |
| holdout | `hold.finditer.groups` | vm | 1.2726x | 1.0871–1.4731x | 0.35x | FASTER |
| holdout | `hold.finditer.groups` | rust | 0.0093x | 0.0086–0.0106x | 1.88x | REGRESSION |
| holdout | `hold.split.capture` | ast | 0.0102x | 0.0100–0.0104x | 11.00x | REGRESSION |
| holdout | `hold.split.capture` | vm | 1.0808x | 1.0713–1.0908x | 0.20x | FASTER |
| holdout | `hold.split.capture` | rust | 0.0065x | 0.0064–0.0066x | 2.47x | REGRESSION |
| holdout | `hold.sub.template` | ast | 0.0166x | 0.0162–0.0169x | 14.73x | REGRESSION |
| holdout | `hold.sub.template` | vm | 1.7407x | 1.7038–1.7695x | 0.12x | FASTER |
| holdout | `hold.sub.template` | rust | 0.0157x | 0.0153–0.0160x | 2.31x | REGRESSION |
| holdout | `hold.subn.callable` | ast | 0.0246x | 0.0243–0.0249x | 10.48x | REGRESSION |
| holdout | `hold.subn.callable` | vm | 1.0873x | 1.0327–1.1338x | 0.25x | FASTER |
| holdout | `hold.subn.callable` | rust | 0.0221x | 0.0220–0.0223x | 2.58x | REGRESSION |
| holdout | `hold.bytes.tokens` | ast | 0.0102x | 0.0101–0.0103x | 14.58x | REGRESSION |
| holdout | `hold.bytes.tokens` | vm | 1.8493x | 1.7278–1.9316x | 0.18x | FASTER |
| holdout | `hold.bytes.tokens` | rust | 0.0082x | 0.0081–0.0082x | 2.67x | REGRESSION |
| holdout | `hold.unicode.words` | ast | 0.0085x | 0.0084–0.0086x | 11.99x | REGRESSION |
| holdout | `hold.unicode.words` | vm | 1.5445x | 1.5348–1.5556x | 0.20x | FASTER |
| holdout | `hold.unicode.words` | rust | 0.0115x | 0.0114–0.0116x | 2.58x | REGRESSION |
| holdout | `hold.cold.compile-search` | ast | 0.5180x | 0.5108–0.5253x | 10.02x | REGRESSION |
| holdout | `hold.cold.compile-search` | vm | 1.8035x | 1.7876–1.8203x | 0.61x | FASTER |
| holdout | `hold.cold.compile-search` | rust | 0.8743x | 0.8647–0.8841x | 1.80x | — |
| holdout | `hold.module.warm` | ast | 0.0184x | 0.0180–0.0190x | 16.47x | REGRESSION |
| holdout | `hold.module.warm` | vm | 1.1211x | 1.0965–1.1585x | 0.07x | FASTER |
| holdout | `hold.module.warm` | rust | 0.0326x | 0.0320–0.0336x | 3.33x | REGRESSION |

## Regression explanation

All listed regressions are retained. The Python backtracker spends most of its time creating Python states and scanning one position at a time. The Rust engine repeatedly crosses the Python/Rust boundary and creates eager continuation state, which dominates these short calls. The native C engine has 1 large slowdown(s): `cal.unicode.words`. Its remaining Unicode-word case repeatedly checks Unicode word boundaries and character categories; this path cannot use the simpler one-pass token scan. Long misses amplify scanning, while find-all, iteration, splitting, and replacement amplify per-match work. The raw memory observations and every case remain available for inspection.
