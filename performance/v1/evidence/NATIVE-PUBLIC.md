# Native public API experiment

Raw SHA-256: `3dd652ee1364546bc2f0e75be7d7b1af895903edab4330a587a70a668a7bf8ab`. Rows: 1152. All 96 candidate/case results and all 72 regressions are shown below.

## Rankings

| Cohort | Candidate | Geomean | 95% CI | Faster cases | >20% regressions |
| --- | --- | ---: | ---: | ---: | ---: |
| calibration | ast | 0.0101x | 0.0100–0.0103x | 0/16 | 16 |
| calibration | vm | 1.0923x | 1.0786–1.1065x | 8/16 | 6 |
| calibration | rust | 0.0134x | 0.0132–0.0136x | 0/16 | 15 |
| holdout | ast | 0.0113x | 0.0112–0.0115x | 0/16 | 16 |
| holdout | vm | 1.1178x | 1.1016–1.1355x | 8/16 | 4 |
| holdout | rust | 0.0145x | 0.0143–0.0147x | 0/16 | 15 |
| all | ast | 0.0107x | 0.0106–0.0108x | 0/32 | 32 |
| all | vm | 1.1050x | 1.0940–1.1159x | 16/32 | 10 |
| all | rust | 0.0139x | 0.0138–0.0141x | 0/32 | 30 |

## Every case

`REGRESSION` means speedup below 0.8; `FASTER` means the lower confidence bound exceeds 1. Memory is median traced-peak candidate/baseline ratio.

| Cohort | Case | Candidate | Speedup | 95% CI | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| calibration | `cal.search.literal.hit` | ast | 0.0095x | 0.0084–0.0111x | 94.53x | REGRESSION |
| calibration | `cal.search.literal.hit` | vm | 0.7975x | 0.7424–0.8956x | 0.73x | REGRESSION |
| calibration | `cal.search.literal.hit` | rust | 0.0106x | 0.0093–0.0126x | 33.50x | REGRESSION |
| calibration | `cal.search.literal.miss` | ast | 0.0026x | 0.0025–0.0026x | 14152.00x | REGRESSION |
| calibration | `cal.search.literal.miss` | vm | 0.5089x | 0.5064–0.5115x | 0.00x | REGRESSION |
| calibration | `cal.search.literal.miss` | rust | 0.0065x | 0.0065–0.0066x | 4311.00x | REGRESSION |
| calibration | `cal.search.long-boundary` | ast | 0.0003x | 0.0003–0.0003x | 130.00x | REGRESSION |
| calibration | `cal.search.long-boundary` | vm | 12.1003x | 11.5465–12.5799x | 0.07x | FASTER |
| calibration | `cal.search.long-boundary` | rust | 0.0010x | 0.0009–0.0010x | 139.92x | REGRESSION |
| calibration | `cal.search.class-anchor` | ast | 0.0118x | 0.0116–0.0120x | 13.78x | REGRESSION |
| calibration | `cal.search.class-anchor` | vm | 1.1142x | 1.0978–1.1311x | 0.07x | FASTER |
| calibration | `cal.search.class-anchor` | rust | 0.0155x | 0.0152–0.0158x | 3.31x | REGRESSION |
| calibration | `cal.match.prefix` | ast | 0.0205x | 0.0203–0.0207x | 10.03x | REGRESSION |
| calibration | `cal.match.prefix` | vm | 1.2331x | 1.2228–1.2436x | 0.07x | FASTER |
| calibration | `cal.match.prefix` | rust | 0.0167x | 0.0166–0.0168x | 3.10x | REGRESSION |
| calibration | `cal.fullmatch.structured` | ast | 0.0107x | 0.0107–0.0108x | 24.65x | REGRESSION |
| calibration | `cal.fullmatch.structured` | vm | 0.7567x | 0.7441–0.7649x | 0.68x | REGRESSION |
| calibration | `cal.fullmatch.structured` | rust | 0.0189x | 0.0188–0.0190x | 2.99x | REGRESSION |
| calibration | `cal.search.look-capture` | ast | 0.0071x | 0.0071–0.0071x | 21.90x | REGRESSION |
| calibration | `cal.search.look-capture` | vm | 0.4237x | 0.4209–0.4269x | 0.15x | REGRESSION |
| calibration | `cal.search.look-capture` | rust | 0.0167x | 0.0166–0.0167x | 3.24x | REGRESSION |
| calibration | `cal.findall.tokens` | ast | 0.0109x | 0.0096–0.0128x | 11.40x | REGRESSION |
| calibration | `cal.findall.tokens` | vm | 1.0747x | 0.9428–1.2871x | 0.28x | — |
| calibration | `cal.findall.tokens` | rust | 0.0042x | 0.0040–0.0045x | 3.12x | REGRESSION |
| calibration | `cal.finditer.groups` | ast | 0.0129x | 0.0115–0.0141x | 13.46x | REGRESSION |
| calibration | `cal.finditer.groups` | vm | 1.5308x | 1.4442–1.6235x | 0.35x | FASTER |
| calibration | `cal.finditer.groups` | rust | 0.0110x | 0.0092–0.0125x | 1.86x | REGRESSION |
| calibration | `cal.split.capture` | ast | 0.0112x | 0.0111–0.0113x | 11.00x | REGRESSION |
| calibration | `cal.split.capture` | vm | 1.1073x | 1.0869–1.1285x | 0.20x | FASTER |
| calibration | `cal.split.capture` | rust | 0.0073x | 0.0072–0.0074x | 2.47x | REGRESSION |
| calibration | `cal.sub.template` | ast | 0.0173x | 0.0170–0.0177x | 14.07x | REGRESSION |
| calibration | `cal.sub.template` | vm | 1.2661x | 1.2167–1.3118x | 0.33x | FASTER |
| calibration | `cal.sub.template` | rust | 0.0170x | 0.0167–0.0173x | 2.31x | REGRESSION |
| calibration | `cal.subn.callable` | ast | 0.0213x | 0.0210–0.0216x | 11.45x | REGRESSION |
| calibration | `cal.subn.callable` | vm | 1.0319x | 1.0144–1.0489x | 0.30x | FASTER |
| calibration | `cal.subn.callable` | rust | 0.0201x | 0.0199–0.0204x | 2.60x | REGRESSION |
| calibration | `cal.bytes.tokens` | ast | 0.0081x | 0.0080–0.0083x | 12.56x | REGRESSION |
| calibration | `cal.bytes.tokens` | vm | 0.9539x | 0.9098–0.9878x | 0.12x | — |
| calibration | `cal.bytes.tokens` | rust | 0.0060x | 0.0059–0.0061x | 3.26x | REGRESSION |
| calibration | `cal.unicode.words` | ast | 0.0065x | 0.0064–0.0065x | 11.60x | REGRESSION |
| calibration | `cal.unicode.words` | vm | 0.6875x | 0.6785–0.6960x | 0.52x | REGRESSION |
| calibration | `cal.unicode.words` | rust | 0.0105x | 0.0104–0.0106x | 2.60x | REGRESSION |
| calibration | `cal.cold.compile-search` | ast | 0.2979x | 0.2923–0.3043x | 11.57x | REGRESSION |
| calibration | `cal.cold.compile-search` | vm | 1.8637x | 1.8232–1.9099x | 0.58x | FASTER |
| calibration | `cal.cold.compile-search` | rust | 0.8362x | 0.8199–0.8575x | 1.84x | — |
| calibration | `cal.module.warm` | ast | 0.0100x | 0.0095–0.0103x | 18.37x | REGRESSION |
| calibration | `cal.module.warm` | vm | 0.6531x | 0.6455–0.6606x | 0.07x | REGRESSION |
| calibration | `cal.module.warm` | rust | 0.0319x | 0.0316–0.0323x | 3.34x | REGRESSION |
| holdout | `hold.search.literal.hit` | ast | 0.0087x | 0.0086–0.0088x | 94.53x | REGRESSION |
| holdout | `hold.search.literal.hit` | vm | 0.7654x | 0.7315–0.7928x | 0.73x | REGRESSION |
| holdout | `hold.search.literal.hit` | rust | 0.0103x | 0.0101–0.0105x | 33.42x | REGRESSION |
| holdout | `hold.search.literal.miss` | ast | 0.0027x | 0.0027–0.0028x | 14152.00x | REGRESSION |
| holdout | `hold.search.literal.miss` | vm | 0.5116x | 0.4755–0.5331x | 0.00x | REGRESSION |
| holdout | `hold.search.literal.miss` | rust | 0.0065x | 0.0065–0.0066x | 4311.00x | REGRESSION |
| holdout | `hold.search.long-boundary` | ast | 0.0003x | 0.0003–0.0003x | 130.31x | REGRESSION |
| holdout | `hold.search.long-boundary` | vm | 14.6071x | 12.3140–17.0941x | 0.07x | FASTER |
| holdout | `hold.search.long-boundary` | rust | 0.0010x | 0.0009–0.0011x | 218.12x | REGRESSION |
| holdout | `hold.search.class-anchor` | ast | 0.0102x | 0.0100–0.0103x | 14.44x | REGRESSION |
| holdout | `hold.search.class-anchor` | vm | 1.0655x | 1.0566–1.0747x | 0.07x | FASTER |
| holdout | `hold.search.class-anchor` | rust | 0.0143x | 0.0142–0.0144x | 3.34x | REGRESSION |
| holdout | `hold.match.prefix` | ast | 0.0222x | 0.0213–0.0240x | 9.08x | REGRESSION |
| holdout | `hold.match.prefix` | vm | 1.2761x | 1.2217–1.3786x | 0.07x | FASTER |
| holdout | `hold.match.prefix` | rust | 0.0178x | 0.0171–0.0192x | 3.09x | REGRESSION |
| holdout | `hold.fullmatch.structured` | ast | 0.0106x | 0.0103–0.0109x | 24.88x | REGRESSION |
| holdout | `hold.fullmatch.structured` | vm | 0.7640x | 0.7352–0.7918x | 0.74x | REGRESSION |
| holdout | `hold.fullmatch.structured` | rust | 0.0204x | 0.0196–0.0212x | 2.99x | REGRESSION |
| holdout | `hold.search.look-capture` | ast | 0.0082x | 0.0078–0.0089x | 23.81x | REGRESSION |
| holdout | `hold.search.look-capture` | vm | 0.5479x | 0.5257–0.5910x | 0.17x | REGRESSION |
| holdout | `hold.search.look-capture` | rust | 0.0186x | 0.0179–0.0200x | 3.21x | REGRESSION |
| holdout | `hold.findall.tokens` | ast | 0.0101x | 0.0099–0.0103x | 20.57x | REGRESSION |
| holdout | `hold.findall.tokens` | vm | 0.8328x | 0.7885–0.8679x | 0.53x | — |
| holdout | `hold.findall.tokens` | rust | 0.0063x | 0.0062–0.0064x | 2.99x | REGRESSION |
| holdout | `hold.finditer.groups` | ast | 0.0122x | 0.0118–0.0126x | 13.46x | REGRESSION |
| holdout | `hold.finditer.groups` | vm | 1.3754x | 1.3349–1.4182x | 0.35x | FASTER |
| holdout | `hold.finditer.groups` | rust | 0.0097x | 0.0094–0.0100x | 1.88x | REGRESSION |
| holdout | `hold.split.capture` | ast | 0.0110x | 0.0109–0.0111x | 11.00x | REGRESSION |
| holdout | `hold.split.capture` | vm | 1.1039x | 1.0946–1.1132x | 0.20x | FASTER |
| holdout | `hold.split.capture` | rust | 0.0072x | 0.0072–0.0073x | 2.47x | REGRESSION |
| holdout | `hold.sub.template` | ast | 0.0169x | 0.0167–0.0170x | 14.73x | REGRESSION |
| holdout | `hold.sub.template` | vm | 1.2688x | 1.2371–1.2946x | 0.33x | FASTER |
| holdout | `hold.sub.template` | rust | 0.0166x | 0.0165–0.0167x | 2.31x | REGRESSION |
| holdout | `hold.subn.callable` | ast | 0.0250x | 0.0247–0.0254x | 10.48x | REGRESSION |
| holdout | `hold.subn.callable` | vm | 1.0534x | 1.0357–1.0747x | 0.30x | FASTER |
| holdout | `hold.subn.callable` | rust | 0.0231x | 0.0226–0.0235x | 2.58x | REGRESSION |
| holdout | `hold.bytes.tokens` | ast | 0.0109x | 0.0106–0.0112x | 14.58x | REGRESSION |
| holdout | `hold.bytes.tokens` | vm | 0.8286x | 0.8063–0.8546x | 0.59x | — |
| holdout | `hold.bytes.tokens` | rust | 0.0091x | 0.0089–0.0094x | 2.67x | REGRESSION |
| holdout | `hold.unicode.words` | ast | 0.0086x | 0.0086–0.0087x | 11.99x | REGRESSION |
| holdout | `hold.unicode.words` | vm | 0.8094x | 0.7689–0.8344x | 0.60x | — |
| holdout | `hold.unicode.words` | rust | 0.0122x | 0.0122–0.0123x | 2.58x | REGRESSION |
| holdout | `hold.cold.compile-search` | ast | 0.5205x | 0.5140–0.5265x | 10.02x | REGRESSION |
| holdout | `hold.cold.compile-search` | vm | 1.8260x | 1.7905–1.8568x | 0.60x | FASTER |
| holdout | `hold.cold.compile-search` | rust | 0.9038x | 0.8922–0.9167x | 1.82x | — |
| holdout | `hold.module.warm` | ast | 0.0193x | 0.0181–0.0218x | 16.47x | REGRESSION |
| holdout | `hold.module.warm` | vm | 0.8819x | 0.8396–0.9655x | 0.07x | — |
| holdout | `hold.module.warm` | rust | 0.0357x | 0.0334–0.0405x | 3.33x | REGRESSION |

## Regression explanation

All listed regressions are retained. The AST family pays Python generator/state-allocation and per-position scanning costs. The native VM improves cold compilation but pays state cloning, Python result construction, and wrapper/template costs. Rust pays per-call FFI conversion plus eager continuation allocation. Long misses amplify scanning/boundary work; `findall`, `finditer`, `split`, and substitutions amplify repeated match/result construction. These mechanisms explain the >20% losses shown above; the raw RSS/HWM and traced peaks remain available for inspection.
