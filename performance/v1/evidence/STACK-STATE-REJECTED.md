# Rejected stack-state executor experiment

Raw SHA-256: `f41144f1ffad4290e0e576ae2f8aab1a6e5bb2f9ea0ec19cf648e3d6c1e7024e`. Rows: 1152. All 96 candidate/case results and all 90 regressions are shown below.

## Rankings

| Cohort | Candidate | Geomean | 95% CI | Faster cases | >20% regressions |
| --- | --- | ---: | ---: | ---: | ---: |
| calibration | ast | 0.0100x | 0.0099–0.0102x | 0/16 | 16 |
| calibration | vm | 0.2243x | 0.2204–0.2285x | 2/16 | 14 |
| calibration | rust | 0.0134x | 0.0132–0.0136x | 0/16 | 15 |
| holdout | ast | 0.0113x | 0.0111–0.0114x | 0/16 | 16 |
| holdout | vm | 0.2435x | 0.2405–0.2465x | 2/16 | 14 |
| holdout | rust | 0.0142x | 0.0141–0.0144x | 0/16 | 15 |
| all | ast | 0.0106x | 0.0105–0.0107x | 0/32 | 32 |
| all | vm | 0.2337x | 0.2313–0.2365x | 4/32 | 28 |
| all | rust | 0.0138x | 0.0137–0.0140x | 0/32 | 30 |

## Every case

`REGRESSION` means speedup below 0.8; `FASTER` means the lower confidence bound exceeds 1. Memory is median traced-peak candidate/baseline ratio.

| Cohort | Case | Candidate | Speedup | 95% CI | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| calibration | `cal.search.literal.hit` | ast | 0.0090x | 0.0084–0.0101x | 94.53x | REGRESSION |
| calibration | `cal.search.literal.hit` | vm | 0.1476x | 0.1387–0.1646x | 0.73x | REGRESSION |
| calibration | `cal.search.literal.hit` | rust | 0.0103x | 0.0097–0.0115x | 33.50x | REGRESSION |
| calibration | `cal.search.literal.miss` | ast | 0.0026x | 0.0025–0.0026x | 14152.00x | REGRESSION |
| calibration | `cal.search.literal.miss` | vm | 0.1313x | 0.1290–0.1331x | 16.00x | REGRESSION |
| calibration | `cal.search.literal.miss` | rust | 0.0064x | 0.0064–0.0065x | 4311.00x | REGRESSION |
| calibration | `cal.search.long-boundary` | ast | 0.0003x | 0.0003–0.0003x | 130.00x | REGRESSION |
| calibration | `cal.search.long-boundary` | vm | 1.8916x | 1.8348–1.9833x | 0.07x | FASTER |
| calibration | `cal.search.long-boundary` | rust | 0.0009x | 0.0009–0.0010x | 139.92x | REGRESSION |
| calibration | `cal.search.class-anchor` | ast | 0.0126x | 0.0117–0.0142x | 13.78x | REGRESSION |
| calibration | `cal.search.class-anchor` | vm | 0.1228x | 0.1175–0.1290x | 0.07x | REGRESSION |
| calibration | `cal.search.class-anchor` | rust | 0.0163x | 0.0153–0.0176x | 3.31x | REGRESSION |
| calibration | `cal.match.prefix` | ast | 0.0192x | 0.0175–0.0202x | 10.03x | REGRESSION |
| calibration | `cal.match.prefix` | vm | 0.1962x | 0.1902–0.2023x | 0.07x | REGRESSION |
| calibration | `cal.match.prefix` | rust | 0.0167x | 0.0164–0.0171x | 3.10x | REGRESSION |
| calibration | `cal.fullmatch.structured` | ast | 0.0110x | 0.0101–0.0125x | 24.65x | REGRESSION |
| calibration | `cal.fullmatch.structured` | vm | 0.2005x | 0.1965–0.2071x | 0.07x | REGRESSION |
| calibration | `cal.fullmatch.structured` | rust | 0.0194x | 0.0182–0.0217x | 2.99x | REGRESSION |
| calibration | `cal.search.look-capture` | ast | 0.0068x | 0.0061–0.0075x | 21.90x | REGRESSION |
| calibration | `cal.search.look-capture` | vm | 0.0708x | 0.0623–0.0820x | 0.08x | REGRESSION |
| calibration | `cal.search.look-capture` | rust | 0.0180x | 0.0159–0.0206x | 3.24x | REGRESSION |
| calibration | `cal.findall.tokens` | ast | 0.0097x | 0.0088–0.0108x | 11.40x | REGRESSION |
| calibration | `cal.findall.tokens` | vm | 0.2598x | 0.2274–0.3019x | 0.29x | REGRESSION |
| calibration | `cal.findall.tokens` | rust | 0.0040x | 0.0038–0.0042x | 3.12x | REGRESSION |
| calibration | `cal.finditer.groups` | ast | 0.0126x | 0.0116–0.0139x | 13.46x | REGRESSION |
| calibration | `cal.finditer.groups` | vm | 0.2346x | 0.2168–0.2544x | 0.39x | REGRESSION |
| calibration | `cal.finditer.groups` | rust | 0.0110x | 0.0101–0.0120x | 1.86x | REGRESSION |
| calibration | `cal.split.capture` | ast | 0.0108x | 0.0107–0.0108x | 11.00x | REGRESSION |
| calibration | `cal.split.capture` | vm | 0.1945x | 0.1930–0.1959x | 0.22x | REGRESSION |
| calibration | `cal.split.capture` | rust | 0.0069x | 0.0069–0.0070x | 2.47x | REGRESSION |
| calibration | `cal.sub.template` | ast | 0.0168x | 0.0166–0.0171x | 14.07x | REGRESSION |
| calibration | `cal.sub.template` | vm | 0.0949x | 0.0933–0.0967x | 0.72x | REGRESSION |
| calibration | `cal.sub.template` | rust | 0.0166x | 0.0164–0.0169x | 2.31x | REGRESSION |
| calibration | `cal.subn.callable` | ast | 0.0226x | 0.0217–0.0237x | 11.45x | REGRESSION |
| calibration | `cal.subn.callable` | vm | 0.2183x | 0.2074–0.2314x | 0.53x | REGRESSION |
| calibration | `cal.subn.callable` | rust | 0.0211x | 0.0201–0.0221x | 2.60x | REGRESSION |
| calibration | `cal.bytes.tokens` | ast | 0.0081x | 0.0080–0.0082x | 12.56x | REGRESSION |
| calibration | `cal.bytes.tokens` | vm | 0.2324x | 0.2302–0.2349x | 0.13x | REGRESSION |
| calibration | `cal.bytes.tokens` | rust | 0.0059x | 0.0058–0.0060x | 3.26x | REGRESSION |
| calibration | `cal.unicode.words` | ast | 0.0069x | 0.0063–0.0076x | 11.60x | REGRESSION |
| calibration | `cal.unicode.words` | vm | 0.2586x | 0.2295–0.2925x | 0.21x | REGRESSION |
| calibration | `cal.unicode.words` | rust | 0.0109x | 0.0100–0.0121x | 2.60x | REGRESSION |
| calibration | `cal.cold.compile-search` | ast | 0.2960x | 0.2912–0.3016x | 11.57x | REGRESSION |
| calibration | `cal.cold.compile-search` | vm | 1.2975x | 1.2507–1.3398x | 0.90x | FASTER |
| calibration | `cal.cold.compile-search` | rust | 0.8214x | 0.8059–0.8400x | 1.82x | — |
| calibration | `cal.module.warm` | ast | 0.0106x | 0.0102–0.0114x | 18.37x | REGRESSION |
| calibration | `cal.module.warm` | vm | 0.1710x | 0.1628–0.1852x | 0.07x | REGRESSION |
| calibration | `cal.module.warm` | rust | 0.0329x | 0.0314–0.0355x | 3.34x | REGRESSION |
| holdout | `hold.search.literal.hit` | ast | 0.0087x | 0.0087–0.0088x | 94.53x | REGRESSION |
| holdout | `hold.search.literal.hit` | vm | 0.1397x | 0.1386–0.1409x | 0.73x | REGRESSION |
| holdout | `hold.search.literal.hit` | rust | 0.0101x | 0.0100–0.0102x | 33.42x | REGRESSION |
| holdout | `hold.search.literal.miss` | ast | 0.0028x | 0.0027–0.0028x | 14152.00x | REGRESSION |
| holdout | `hold.search.literal.miss` | vm | 0.1563x | 0.1536–0.1581x | 16.00x | REGRESSION |
| holdout | `hold.search.literal.miss` | rust | 0.0064x | 0.0064–0.0065x | 4311.00x | REGRESSION |
| holdout | `hold.search.long-boundary` | ast | 0.0003x | 0.0003–0.0003x | 130.31x | REGRESSION |
| holdout | `hold.search.long-boundary` | vm | 2.3981x | 2.0825–2.7551x | 0.07x | FASTER |
| holdout | `hold.search.long-boundary` | rust | 0.0009x | 0.0009–0.0010x | 218.12x | REGRESSION |
| holdout | `hold.search.class-anchor` | ast | 0.0102x | 0.0096–0.0109x | 14.44x | REGRESSION |
| holdout | `hold.search.class-anchor` | vm | 0.1029x | 0.0990–0.1076x | 0.07x | REGRESSION |
| holdout | `hold.search.class-anchor` | rust | 0.0143x | 0.0135–0.0150x | 3.34x | REGRESSION |
| holdout | `hold.match.prefix` | ast | 0.0216x | 0.0208–0.0221x | 9.08x | REGRESSION |
| holdout | `hold.match.prefix` | vm | 0.1859x | 0.1727–0.1965x | 0.07x | REGRESSION |
| holdout | `hold.match.prefix` | rust | 0.0173x | 0.0167–0.0177x | 3.09x | REGRESSION |
| holdout | `hold.fullmatch.structured` | ast | 0.0107x | 0.0105–0.0110x | 24.88x | REGRESSION |
| holdout | `hold.fullmatch.structured` | vm | 0.2102x | 0.1997–0.2217x | 0.07x | REGRESSION |
| holdout | `hold.fullmatch.structured` | rust | 0.0199x | 0.0189–0.0211x | 2.99x | REGRESSION |
| holdout | `hold.search.look-capture` | ast | 0.0079x | 0.0078–0.0080x | 23.81x | REGRESSION |
| holdout | `hold.search.look-capture` | vm | 0.0848x | 0.0839–0.0858x | 0.08x | REGRESSION |
| holdout | `hold.search.look-capture` | rust | 0.0176x | 0.0173–0.0178x | 3.21x | REGRESSION |
| holdout | `hold.findall.tokens` | ast | 0.0098x | 0.0096–0.0100x | 20.57x | REGRESSION |
| holdout | `hold.findall.tokens` | vm | 0.2872x | 0.2784–0.2977x | 0.22x | REGRESSION |
| holdout | `hold.findall.tokens` | rust | 0.0060x | 0.0059–0.0063x | 2.99x | REGRESSION |
| holdout | `hold.finditer.groups` | ast | 0.0124x | 0.0118–0.0130x | 13.46x | REGRESSION |
| holdout | `hold.finditer.groups` | vm | 0.2337x | 0.2261–0.2426x | 0.39x | REGRESSION |
| holdout | `hold.finditer.groups` | rust | 0.0098x | 0.0094–0.0102x | 1.88x | REGRESSION |
| holdout | `hold.split.capture` | ast | 0.0111x | 0.0110–0.0112x | 11.00x | REGRESSION |
| holdout | `hold.split.capture` | vm | 0.2124x | 0.2065–0.2160x | 0.22x | REGRESSION |
| holdout | `hold.split.capture` | rust | 0.0071x | 0.0071–0.0072x | 2.47x | REGRESSION |
| holdout | `hold.sub.template` | ast | 0.0169x | 0.0166–0.0172x | 14.73x | REGRESSION |
| holdout | `hold.sub.template` | vm | 0.0970x | 0.0951–0.0989x | 0.72x | REGRESSION |
| holdout | `hold.sub.template` | rust | 0.0165x | 0.0161–0.0169x | 2.31x | REGRESSION |
| holdout | `hold.subn.callable` | ast | 0.0249x | 0.0238–0.0260x | 10.48x | REGRESSION |
| holdout | `hold.subn.callable` | vm | 0.2108x | 0.2066–0.2166x | 0.53x | REGRESSION |
| holdout | `hold.subn.callable` | rust | 0.0231x | 0.0226–0.0239x | 2.58x | REGRESSION |
| holdout | `hold.bytes.tokens` | ast | 0.0104x | 0.0101–0.0106x | 14.58x | REGRESSION |
| holdout | `hold.bytes.tokens` | vm | 0.2356x | 0.2287–0.2408x | 0.19x | REGRESSION |
| holdout | `hold.bytes.tokens` | rust | 0.0088x | 0.0087–0.0089x | 2.67x | REGRESSION |
| holdout | `hold.unicode.words` | ast | 0.0091x | 0.0084–0.0102x | 11.99x | REGRESSION |
| holdout | `hold.unicode.words` | vm | 0.2784x | 0.2668–0.2961x | 0.22x | REGRESSION |
| holdout | `hold.unicode.words` | rust | 0.0124x | 0.0118–0.0134x | 2.58x | REGRESSION |
| holdout | `hold.cold.compile-search` | ast | 0.5202x | 0.5122–0.5289x | 10.02x | REGRESSION |
| holdout | `hold.cold.compile-search` | vm | 1.3769x | 1.3527–1.4006x | 0.87x | FASTER |
| holdout | `hold.cold.compile-search` | rust | 0.8697x | 0.8431–0.8924x | 1.80x | — |
| holdout | `hold.module.warm` | ast | 0.0184x | 0.0168–0.0202x | 16.47x | REGRESSION |
| holdout | `hold.module.warm` | vm | 0.3256x | 0.3110–0.3494x | 0.07x | REGRESSION |
| holdout | `hold.module.warm` | rust | 0.0345x | 0.0326–0.0372x | 3.33x | REGRESSION |

## Regression explanation

All listed regressions are retained. The AST family pays Python generator/state-allocation and per-position scanning costs. The native VM improves cold compilation but pays state cloning, Python result construction, and wrapper/template costs. Rust pays per-call FFI conversion plus eager continuation allocation. Long misses amplify scanning/boundary work; `findall`, `finditer`, `split`, and substitutions amplify repeated match/result construction. These mechanisms explain the >20% losses shown above; the raw RSS/HWM and traced peaks remain available for inspection.
