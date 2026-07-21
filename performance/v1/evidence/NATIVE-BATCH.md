# Native batching experiment

Raw SHA-256: `21c829b2e16e59eba3130a3fed014113f0391007f570a00d1385b55022be843c`. Rows: 1152. All 96 candidate/case results and all 90 regressions are shown below.

## Rankings

| Cohort | Candidate | Geomean | 95% CI | Faster cases | >20% regressions |
| --- | --- | ---: | ---: | ---: | ---: |
| calibration | ast | 0.0101x | 0.0099–0.0103x | 0/16 | 16 |
| calibration | vm | 0.3043x | 0.3000–0.3085x | 2/16 | 14 |
| calibration | rust | 0.0133x | 0.0131–0.0135x | 0/16 | 15 |
| holdout | ast | 0.0112x | 0.0111–0.0113x | 0/16 | 16 |
| holdout | vm | 0.3291x | 0.3251–0.3335x | 2/16 | 14 |
| holdout | rust | 0.0141x | 0.0140–0.0143x | 0/16 | 15 |
| all | ast | 0.0106x | 0.0105–0.0107x | 0/32 | 32 |
| all | vm | 0.3165x | 0.3136–0.3194x | 4/32 | 28 |
| all | rust | 0.0137x | 0.0136–0.0138x | 0/32 | 30 |

## Every case

`REGRESSION` means speedup below 0.8; `FASTER` means the lower confidence bound exceeds 1. Memory is median traced-peak candidate/baseline ratio.

| Cohort | Case | Candidate | Speedup | 95% CI | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| calibration | `cal.search.literal.hit` | ast | 0.0093x | 0.0083–0.0108x | 94.53x | REGRESSION |
| calibration | `cal.search.literal.hit` | vm | 0.1568x | 0.1398–0.1807x | 3.27x | REGRESSION |
| calibration | `cal.search.literal.hit` | rust | 0.0105x | 0.0093–0.0125x | 33.50x | REGRESSION |
| calibration | `cal.search.literal.miss` | ast | 0.0031x | 0.0026–0.0037x | 14152.00x | REGRESSION |
| calibration | `cal.search.literal.miss` | vm | 0.1755x | 0.1708–0.1792x | 392.00x | REGRESSION |
| calibration | `cal.search.literal.miss` | rust | 0.0074x | 0.0062–0.0087x | 4311.00x | REGRESSION |
| calibration | `cal.search.long-boundary` | ast | 0.0003x | 0.0003–0.0003x | 130.00x | REGRESSION |
| calibration | `cal.search.long-boundary` | vm | 2.1801x | 2.0479–2.3970x | 0.31x | FASTER |
| calibration | `cal.search.long-boundary` | rust | 0.0010x | 0.0009–0.0011x | 139.92x | REGRESSION |
| calibration | `cal.search.class-anchor` | ast | 0.0115x | 0.0114–0.0115x | 13.78x | REGRESSION |
| calibration | `cal.search.class-anchor` | vm | 0.2138x | 0.2088–0.2174x | 0.35x | REGRESSION |
| calibration | `cal.search.class-anchor` | rust | 0.0150x | 0.0149–0.0152x | 3.31x | REGRESSION |
| calibration | `cal.match.prefix` | ast | 0.0203x | 0.0195–0.0216x | 10.03x | REGRESSION |
| calibration | `cal.match.prefix` | vm | 0.2065x | 0.1843–0.2214x | 0.32x | REGRESSION |
| calibration | `cal.match.prefix` | rust | 0.0157x | 0.0151–0.0163x | 3.10x | REGRESSION |
| calibration | `cal.fullmatch.structured` | ast | 0.0105x | 0.0103–0.0107x | 24.65x | REGRESSION |
| calibration | `cal.fullmatch.structured` | vm | 0.1899x | 0.1836–0.1946x | 5.16x | REGRESSION |
| calibration | `cal.fullmatch.structured` | rust | 0.0184x | 0.0181–0.0187x | 2.99x | REGRESSION |
| calibration | `cal.search.look-capture` | ast | 0.0070x | 0.0069–0.0071x | 21.90x | REGRESSION |
| calibration | `cal.search.look-capture` | vm | 0.1675x | 0.1639–0.1696x | 2.20x | REGRESSION |
| calibration | `cal.search.look-capture` | rust | 0.0167x | 0.0165–0.0168x | 3.24x | REGRESSION |
| calibration | `cal.findall.tokens` | ast | 0.0095x | 0.0093–0.0096x | 11.40x | REGRESSION |
| calibration | `cal.findall.tokens` | vm | 0.3559x | 0.3504–0.3610x | 1.97x | REGRESSION |
| calibration | `cal.findall.tokens` | rust | 0.0040x | 0.0039–0.0040x | 3.12x | REGRESSION |
| calibration | `cal.finditer.groups` | ast | 0.0126x | 0.0122–0.0134x | 13.46x | REGRESSION |
| calibration | `cal.finditer.groups` | vm | 0.3064x | 0.2939–0.3261x | 2.04x | REGRESSION |
| calibration | `cal.finditer.groups` | rust | 0.0105x | 0.0101–0.0111x | 1.86x | REGRESSION |
| calibration | `cal.split.capture` | ast | 0.0110x | 0.0109–0.0111x | 11.00x | REGRESSION |
| calibration | `cal.split.capture` | vm | 0.5907x | 0.5862–0.5960x | 0.49x | REGRESSION |
| calibration | `cal.split.capture` | rust | 0.0071x | 0.0070–0.0072x | 2.47x | REGRESSION |
| calibration | `cal.sub.template` | ast | 0.0170x | 0.0168–0.0172x | 14.07x | REGRESSION |
| calibration | `cal.sub.template` | vm | 0.1027x | 0.1014–0.1042x | 1.87x | REGRESSION |
| calibration | `cal.sub.template` | rust | 0.0165x | 0.0162–0.0168x | 2.31x | REGRESSION |
| calibration | `cal.subn.callable` | ast | 0.0217x | 0.0215–0.0219x | 11.45x | REGRESSION |
| calibration | `cal.subn.callable` | vm | 0.2330x | 0.2310–0.2354x | 1.85x | REGRESSION |
| calibration | `cal.subn.callable` | rust | 0.0202x | 0.0200–0.0204x | 2.60x | REGRESSION |
| calibration | `cal.bytes.tokens` | ast | 0.0083x | 0.0079–0.0089x | 12.56x | REGRESSION |
| calibration | `cal.bytes.tokens` | vm | 0.3141x | 0.2936–0.3456x | 2.31x | REGRESSION |
| calibration | `cal.bytes.tokens` | rust | 0.0061x | 0.0058–0.0067x | 3.26x | REGRESSION |
| calibration | `cal.unicode.words` | ast | 0.0065x | 0.0064–0.0066x | 11.60x | REGRESSION |
| calibration | `cal.unicode.words` | vm | 0.4198x | 0.4074–0.4301x | 1.73x | REGRESSION |
| calibration | `cal.unicode.words` | rust | 0.0105x | 0.0103–0.0106x | 2.60x | REGRESSION |
| calibration | `cal.cold.compile-search` | ast | 0.2969x | 0.2944–0.2994x | 11.57x | REGRESSION |
| calibration | `cal.cold.compile-search` | vm | 1.3675x | 1.3502–1.3853x | 2.08x | FASTER |
| calibration | `cal.cold.compile-search` | rust | 0.8294x | 0.8235–0.8355x | 1.82x | — |
| calibration | `cal.module.warm` | ast | 0.0104x | 0.0101–0.0107x | 18.37x | REGRESSION |
| calibration | `cal.module.warm` | vm | 0.2313x | 0.2251–0.2384x | 3.19x | REGRESSION |
| calibration | `cal.module.warm` | rust | 0.0323x | 0.0318–0.0331x | 3.34x | REGRESSION |
| holdout | `hold.search.literal.hit` | ast | 0.0086x | 0.0085–0.0086x | 94.53x | REGRESSION |
| holdout | `hold.search.literal.hit` | vm | 0.1541x | 0.1524–0.1558x | 3.27x | REGRESSION |
| holdout | `hold.search.literal.hit` | rust | 0.0100x | 0.0099–0.0101x | 33.42x | REGRESSION |
| holdout | `hold.search.literal.miss` | ast | 0.0027x | 0.0027–0.0028x | 14152.00x | REGRESSION |
| holdout | `hold.search.literal.miss` | vm | 0.1923x | 0.1887–0.1946x | 400.00x | REGRESSION |
| holdout | `hold.search.literal.miss` | rust | 0.0064x | 0.0063–0.0065x | 4311.00x | REGRESSION |
| holdout | `hold.search.long-boundary` | ast | 0.0003x | 0.0003–0.0003x | 130.00x | REGRESSION |
| holdout | `hold.search.long-boundary` | vm | 2.5670x | 2.2114–2.8758x | 0.32x | FASTER |
| holdout | `hold.search.long-boundary` | rust | 0.0009x | 0.0009–0.0009x | 218.12x | REGRESSION |
| holdout | `hold.search.class-anchor` | ast | 0.0102x | 0.0100–0.0104x | 14.44x | REGRESSION |
| holdout | `hold.search.class-anchor` | vm | 0.2065x | 0.1927–0.2150x | 0.35x | REGRESSION |
| holdout | `hold.search.class-anchor` | rust | 0.0143x | 0.0142–0.0144x | 3.34x | REGRESSION |
| holdout | `hold.match.prefix` | ast | 0.0218x | 0.0217–0.0220x | 9.08x | REGRESSION |
| holdout | `hold.match.prefix` | vm | 0.2155x | 0.2143–0.2168x | 0.32x | REGRESSION |
| holdout | `hold.match.prefix` | rust | 0.0171x | 0.0169–0.0172x | 3.09x | REGRESSION |
| holdout | `hold.fullmatch.structured` | ast | 0.0106x | 0.0105–0.0107x | 24.88x | REGRESSION |
| holdout | `hold.fullmatch.structured` | vm | 0.2167x | 0.2126–0.2198x | 3.98x | REGRESSION |
| holdout | `hold.fullmatch.structured` | rust | 0.0197x | 0.0194–0.0201x | 2.99x | REGRESSION |
| holdout | `hold.search.look-capture` | ast | 0.0078x | 0.0077–0.0078x | 23.81x | REGRESSION |
| holdout | `hold.search.look-capture` | vm | 0.1652x | 0.1637–0.1666x | 1.93x | REGRESSION |
| holdout | `hold.search.look-capture` | rust | 0.0174x | 0.0174–0.0175x | 3.21x | REGRESSION |
| holdout | `hold.findall.tokens` | ast | 0.0095x | 0.0093–0.0097x | 20.57x | REGRESSION |
| holdout | `hold.findall.tokens` | vm | 0.3473x | 0.3408–0.3535x | 2.88x | REGRESSION |
| holdout | `hold.findall.tokens` | rust | 0.0060x | 0.0059–0.0060x | 2.99x | REGRESSION |
| holdout | `hold.finditer.groups` | ast | 0.0121x | 0.0114–0.0129x | 13.46x | REGRESSION |
| holdout | `hold.finditer.groups` | vm | 0.2946x | 0.2786–0.3120x | 2.04x | REGRESSION |
| holdout | `hold.finditer.groups` | rust | 0.0097x | 0.0093–0.0102x | 1.88x | REGRESSION |
| holdout | `hold.split.capture` | ast | 0.0108x | 0.0107–0.0110x | 11.00x | REGRESSION |
| holdout | `hold.split.capture` | vm | 0.5851x | 0.5727–0.5965x | 0.49x | REGRESSION |
| holdout | `hold.split.capture` | rust | 0.0070x | 0.0069–0.0071x | 2.47x | REGRESSION |
| holdout | `hold.sub.template` | ast | 0.0168x | 0.0164–0.0171x | 14.73x | REGRESSION |
| holdout | `hold.sub.template` | vm | 0.1025x | 0.1007–0.1046x | 2.15x | REGRESSION |
| holdout | `hold.sub.template` | rust | 0.0163x | 0.0160–0.0166x | 2.31x | REGRESSION |
| holdout | `hold.subn.callable` | ast | 0.0250x | 0.0247–0.0253x | 10.48x | REGRESSION |
| holdout | `hold.subn.callable` | vm | 0.2346x | 0.2316–0.2373x | 1.86x | REGRESSION |
| holdout | `hold.subn.callable` | rust | 0.0229x | 0.0226–0.0231x | 2.58x | REGRESSION |
| holdout | `hold.bytes.tokens` | ast | 0.0105x | 0.0103–0.0107x | 14.58x | REGRESSION |
| holdout | `hold.bytes.tokens` | vm | 0.4430x | 0.4310–0.4524x | 1.84x | REGRESSION |
| holdout | `hold.bytes.tokens` | rust | 0.0088x | 0.0086–0.0090x | 2.67x | REGRESSION |
| holdout | `hold.unicode.words` | ast | 0.0085x | 0.0084–0.0088x | 11.99x | REGRESSION |
| holdout | `hold.unicode.words` | vm | 0.4679x | 0.4570–0.4829x | 1.68x | REGRESSION |
| holdout | `hold.unicode.words` | rust | 0.0120x | 0.0118–0.0124x | 2.58x | REGRESSION |
| holdout | `hold.cold.compile-search` | ast | 0.5303x | 0.5243–0.5364x | 10.02x | REGRESSION |
| holdout | `hold.cold.compile-search` | vm | 1.4747x | 1.4386–1.5085x | 1.55x | FASTER |
| holdout | `hold.cold.compile-search` | rust | 0.8927x | 0.8725–0.9094x | 1.80x | — |
| holdout | `hold.module.warm` | ast | 0.0196x | 0.0178–0.0231x | 16.47x | REGRESSION |
| holdout | `hold.module.warm` | vm | 0.3561x | 0.3288–0.4012x | 2.53x | REGRESSION |
| holdout | `hold.module.warm` | rust | 0.0360x | 0.0331–0.0419x | 3.33x | REGRESSION |

## Regression explanation

All listed regressions are retained. The AST family pays Python generator/state-allocation and per-position scanning costs. The native VM improves cold compilation but pays state cloning, Python result construction, and wrapper/template costs. Rust pays per-call FFI conversion plus eager continuation allocation. Long misses amplify scanning/boundary work; `findall`, `finditer`, `split`, and substitutions amplify repeated match/result construction. These mechanisms explain the >20% losses shown above; the raw RSS/HWM and traced peaks remain available for inspection.
