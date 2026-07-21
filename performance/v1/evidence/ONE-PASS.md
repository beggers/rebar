# One-pass native scanner experiment

Raw SHA-256: `68ae983e3ecb146216c11f910738ca4e17af774ba496390f6bd9266d62dc3455`. Rows: 1152. All 96 candidate/case results and all 63 regressions are shown below.

## Rankings

| Cohort | Candidate | Geomean | 95% CI | Faster cases | >20% regressions |
| --- | --- | ---: | ---: | ---: | ---: |
| calibration | ast | 0.0098x | 0.0097–0.0099x | 0/16 | 16 |
| calibration | vm | 1.3372x | 1.3249–1.3501x | 12/16 | 1 |
| calibration | rust | 0.0126x | 0.0125–0.0128x | 0/16 | 15 |
| holdout | ast | 0.0109x | 0.0108–0.0111x | 0/16 | 16 |
| holdout | vm | 1.4860x | 1.4603–1.5122x | 13/16 | 0 |
| holdout | rust | 0.0135x | 0.0133–0.0137x | 0/16 | 15 |
| all | ast | 0.0103x | 0.0102–0.0104x | 0/32 | 32 |
| all | vm | 1.4097x | 1.3957–1.4235x | 25/32 | 1 |
| all | rust | 0.0131x | 0.0129–0.0132x | 0/32 | 30 |

## Every case

`REGRESSION` means speedup below 0.8; `FASTER` means the lower confidence bound exceeds 1. Memory is median traced-peak candidate/baseline ratio.

| Cohort | Case | Candidate | Speedup | 95% CI | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| calibration | `cal.search.literal.hit` | ast | 0.0082x | 0.0080–0.0084x | 94.53x | REGRESSION |
| calibration | `cal.search.literal.hit` | vm | 1.1362x | 1.1277–1.1448x | 0.73x | FASTER |
| calibration | `cal.search.literal.hit` | rust | 0.0092x | 0.0091–0.0093x | 33.50x | REGRESSION |
| calibration | `cal.search.literal.miss` | ast | 0.0026x | 0.0025–0.0026x | 14152.00x | REGRESSION |
| calibration | `cal.search.literal.miss` | vm | 1.1828x | 1.1672–1.1996x | 0.00x | FASTER |
| calibration | `cal.search.literal.miss` | rust | 0.0062x | 0.0062–0.0063x | 4311.00x | REGRESSION |
| calibration | `cal.search.long-boundary` | ast | 0.0003x | 0.0003–0.0003x | 130.00x | REGRESSION |
| calibration | `cal.search.long-boundary` | vm | 11.8275x | 11.4131–12.3734x | 0.07x | FASTER |
| calibration | `cal.search.long-boundary` | rust | 0.0009x | 0.0009–0.0010x | 139.92x | REGRESSION |
| calibration | `cal.search.class-anchor` | ast | 0.0119x | 0.0115–0.0126x | 13.78x | REGRESSION |
| calibration | `cal.search.class-anchor` | vm | 1.0900x | 1.0490–1.1525x | 0.07x | FASTER |
| calibration | `cal.search.class-anchor` | rust | 0.0154x | 0.0148–0.0163x | 3.31x | REGRESSION |
| calibration | `cal.match.prefix` | ast | 0.0196x | 0.0194–0.0200x | 10.03x | REGRESSION |
| calibration | `cal.match.prefix` | vm | 1.1498x | 1.0872–1.1928x | 0.07x | FASTER |
| calibration | `cal.match.prefix` | rust | 0.0154x | 0.0152–0.0157x | 3.10x | REGRESSION |
| calibration | `cal.fullmatch.structured` | ast | 0.0106x | 0.0104–0.0109x | 24.65x | REGRESSION |
| calibration | `cal.fullmatch.structured` | vm | 0.8924x | 0.8726–0.9201x | 0.07x | — |
| calibration | `cal.fullmatch.structured` | rust | 0.0182x | 0.0178–0.0188x | 2.99x | REGRESSION |
| calibration | `cal.search.look-capture` | ast | 0.0068x | 0.0068–0.0068x | 21.90x | REGRESSION |
| calibration | `cal.search.look-capture` | vm | 1.2788x | 1.2657–1.2903x | 0.08x | FASTER |
| calibration | `cal.search.look-capture` | rust | 0.0162x | 0.0161–0.0163x | 3.24x | REGRESSION |
| calibration | `cal.findall.tokens` | ast | 0.0094x | 0.0092–0.0098x | 11.40x | REGRESSION |
| calibration | `cal.findall.tokens` | vm | 0.9358x | 0.8925–0.9776x | 0.28x | — |
| calibration | `cal.findall.tokens` | rust | 0.0039x | 0.0038–0.0040x | 3.12x | REGRESSION |
| calibration | `cal.finditer.groups` | ast | 0.0121x | 0.0117–0.0126x | 13.46x | REGRESSION |
| calibration | `cal.finditer.groups` | vm | 1.4242x | 1.3844–1.4786x | 0.35x | FASTER |
| calibration | `cal.finditer.groups` | rust | 0.0090x | 0.0086–0.0093x | 1.86x | REGRESSION |
| calibration | `cal.split.capture` | ast | 0.0109x | 0.0108–0.0111x | 11.00x | REGRESSION |
| calibration | `cal.split.capture` | vm | 1.1409x | 1.1249–1.1591x | 0.20x | FASTER |
| calibration | `cal.split.capture` | rust | 0.0069x | 0.0068–0.0070x | 2.47x | REGRESSION |
| calibration | `cal.sub.template` | ast | 0.0168x | 0.0166–0.0171x | 14.07x | REGRESSION |
| calibration | `cal.sub.template` | vm | 1.7851x | 1.7579–1.8128x | 0.12x | FASTER |
| calibration | `cal.sub.template` | rust | 0.0163x | 0.0160–0.0165x | 2.31x | REGRESSION |
| calibration | `cal.subn.callable` | ast | 0.0219x | 0.0211–0.0231x | 11.45x | REGRESSION |
| calibration | `cal.subn.callable` | vm | 1.1885x | 1.1491–1.2539x | 0.25x | FASTER |
| calibration | `cal.subn.callable` | rust | 0.0198x | 0.0191–0.0210x | 2.60x | REGRESSION |
| calibration | `cal.bytes.tokens` | ast | 0.0079x | 0.0078–0.0080x | 12.56x | REGRESSION |
| calibration | `cal.bytes.tokens` | vm | 0.8855x | 0.8606–0.9068x | 0.12x | — |
| calibration | `cal.bytes.tokens` | rust | 0.0056x | 0.0056–0.0057x | 3.26x | REGRESSION |
| calibration | `cal.unicode.words` | ast | 0.0063x | 0.0062–0.0063x | 11.60x | REGRESSION |
| calibration | `cal.unicode.words` | vm | 0.7451x | 0.7013–0.7731x | 0.20x | REGRESSION |
| calibration | `cal.unicode.words` | rust | 0.0098x | 0.0097–0.0099x | 2.60x | REGRESSION |
| calibration | `cal.cold.compile-search` | ast | 0.2889x | 0.2818–0.2937x | 11.57x | REGRESSION |
| calibration | `cal.cold.compile-search` | vm | 1.7659x | 1.7345–1.7984x | 0.60x | FASTER |
| calibration | `cal.cold.compile-search` | rust | 0.8030x | 0.7771–0.8193x | 1.82x | — |
| calibration | `cal.module.warm` | ast | 0.0103x | 0.0098–0.0112x | 18.37x | REGRESSION |
| calibration | `cal.module.warm` | vm | 1.2233x | 1.1676–1.3257x | 0.07x | FASTER |
| calibration | `cal.module.warm` | rust | 0.0328x | 0.0312–0.0356x | 3.34x | REGRESSION |
| holdout | `hold.search.literal.hit` | ast | 0.0088x | 0.0077–0.0101x | 94.53x | REGRESSION |
| holdout | `hold.search.literal.hit` | vm | 1.1864x | 0.9930–1.4168x | 0.73x | — |
| holdout | `hold.search.literal.hit` | rust | 0.0103x | 0.0092–0.0120x | 33.42x | REGRESSION |
| holdout | `hold.search.literal.miss` | ast | 0.0026x | 0.0025–0.0026x | 14152.00x | REGRESSION |
| holdout | `hold.search.literal.miss` | vm | 1.1740x | 1.1561–1.1893x | 0.00x | FASTER |
| holdout | `hold.search.literal.miss` | rust | 0.0060x | 0.0059–0.0061x | 4311.00x | REGRESSION |
| holdout | `hold.search.long-boundary` | ast | 0.0003x | 0.0003–0.0003x | 130.31x | REGRESSION |
| holdout | `hold.search.long-boundary` | vm | 15.9087x | 14.5000–17.5557x | 0.07x | FASTER |
| holdout | `hold.search.long-boundary` | rust | 0.0010x | 0.0009–0.0011x | 218.12x | REGRESSION |
| holdout | `hold.search.class-anchor` | ast | 0.0098x | 0.0097–0.0100x | 14.44x | REGRESSION |
| holdout | `hold.search.class-anchor` | vm | 0.9611x | 0.8924–1.0052x | 0.07x | — |
| holdout | `hold.search.class-anchor` | rust | 0.0134x | 0.0132–0.0136x | 3.34x | REGRESSION |
| holdout | `hold.match.prefix` | ast | 0.0214x | 0.0204–0.0234x | 9.08x | REGRESSION |
| holdout | `hold.match.prefix` | vm | 1.1863x | 1.1580–1.2273x | 0.07x | FASTER |
| holdout | `hold.match.prefix` | rust | 0.0164x | 0.0155–0.0180x | 3.09x | REGRESSION |
| holdout | `hold.fullmatch.structured` | ast | 0.0104x | 0.0100–0.0110x | 24.88x | REGRESSION |
| holdout | `hold.fullmatch.structured` | vm | 0.8580x | 0.7964–0.9273x | 0.07x | — |
| holdout | `hold.fullmatch.structured` | rust | 0.0190x | 0.0184–0.0201x | 2.99x | REGRESSION |
| holdout | `hold.search.look-capture` | ast | 0.0078x | 0.0074–0.0083x | 23.81x | REGRESSION |
| holdout | `hold.search.look-capture` | vm | 1.1437x | 1.0859–1.2352x | 0.08x | FASTER |
| holdout | `hold.search.look-capture` | rust | 0.0175x | 0.0166–0.0188x | 3.21x | REGRESSION |
| holdout | `hold.findall.tokens` | ast | 0.0090x | 0.0084–0.0097x | 20.57x | REGRESSION |
| holdout | `hold.findall.tokens` | vm | 1.2212x | 1.0786–1.3417x | 0.21x | FASTER |
| holdout | `hold.findall.tokens` | rust | 0.0056x | 0.0054–0.0058x | 2.99x | REGRESSION |
| holdout | `hold.finditer.groups` | ast | 0.0114x | 0.0112–0.0118x | 13.46x | REGRESSION |
| holdout | `hold.finditer.groups` | vm | 1.3715x | 1.3345–1.4075x | 0.35x | FASTER |
| holdout | `hold.finditer.groups` | rust | 0.0080x | 0.0078–0.0082x | 1.88x | REGRESSION |
| holdout | `hold.split.capture` | ast | 0.0103x | 0.0102–0.0105x | 11.00x | REGRESSION |
| holdout | `hold.split.capture` | vm | 1.0917x | 1.0767–1.1114x | 0.20x | FASTER |
| holdout | `hold.split.capture` | rust | 0.0065x | 0.0063–0.0066x | 2.47x | REGRESSION |
| holdout | `hold.sub.template` | ast | 0.0166x | 0.0164–0.0168x | 14.73x | REGRESSION |
| holdout | `hold.sub.template` | vm | 1.7868x | 1.7657–1.8107x | 0.12x | FASTER |
| holdout | `hold.sub.template` | rust | 0.0159x | 0.0158–0.0160x | 2.31x | REGRESSION |
| holdout | `hold.subn.callable` | ast | 0.0245x | 0.0242–0.0247x | 10.48x | REGRESSION |
| holdout | `hold.subn.callable` | vm | 1.1616x | 1.1294–1.1916x | 0.25x | FASTER |
| holdout | `hold.subn.callable` | rust | 0.0217x | 0.0213–0.0221x | 2.58x | REGRESSION |
| holdout | `hold.bytes.tokens` | ast | 0.0102x | 0.0097–0.0109x | 14.58x | REGRESSION |
| holdout | `hold.bytes.tokens` | vm | 1.9548x | 1.8763–2.0576x | 0.18x | FASTER |
| holdout | `hold.bytes.tokens` | rust | 0.0083x | 0.0079–0.0088x | 2.67x | REGRESSION |
| holdout | `hold.unicode.words` | ast | 0.0083x | 0.0082–0.0084x | 11.99x | REGRESSION |
| holdout | `hold.unicode.words` | vm | 1.5380x | 1.5264–1.5495x | 0.20x | FASTER |
| holdout | `hold.unicode.words` | rust | 0.0112x | 0.0111–0.0113x | 2.58x | REGRESSION |
| holdout | `hold.cold.compile-search` | ast | 0.5314x | 0.5119–0.5542x | 10.02x | REGRESSION |
| holdout | `hold.cold.compile-search` | vm | 1.8144x | 1.7690–1.8844x | 0.61x | FASTER |
| holdout | `hold.cold.compile-search` | rust | 0.8980x | 0.8749–0.9356x | 1.80x | — |
| holdout | `hold.module.warm` | ast | 0.0179x | 0.0176–0.0181x | 16.47x | REGRESSION |
| holdout | `hold.module.warm` | vm | 1.1018x | 1.0891–1.1176x | 0.07x | FASTER |
| holdout | `hold.module.warm` | rust | 0.0328x | 0.0325–0.0332x | 3.33x | REGRESSION |

## Regression explanation

All listed regressions are retained. The Python backtracker spends most of its time creating Python states and scanning one position at a time. The Rust engine repeatedly crosses the Python/Rust boundary and creates eager continuation state, which dominates these short calls. The native C engine has 1 large slowdown(s): `cal.unicode.words`. Its remaining Unicode-word case repeatedly checks Unicode word boundaries and character categories; this path cannot use the simpler one-pass token scan. Long misses amplify scanning, while find-all, iteration, splitting, and replacement amplify per-match work. The raw memory observations and every case remain available for inspection.
