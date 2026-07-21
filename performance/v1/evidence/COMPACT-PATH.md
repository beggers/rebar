# Compact native path experiment

Raw SHA-256: `2a7e6aad669d4f33c054ca5e7c5b895bff333e696920db1c2c922d985d33226c`. Rows: 1152. All 96 candidate/case results and all 64 regressions are shown below.

## Rankings

| Cohort | Candidate | Geomean | 95% CI | Faster cases | >20% regressions |
| --- | --- | ---: | ---: | ---: | ---: |
| calibration | ast | 0.0094x | 0.0093–0.0095x | 0/16 | 16 |
| calibration | vm | 1.1950x | 1.1717–1.2159x | 8/16 | 2 |
| calibration | rust | 0.0125x | 0.0123–0.0126x | 0/16 | 15 |
| holdout | ast | 0.0109x | 0.0108–0.0110x | 0/16 | 16 |
| holdout | vm | 1.3067x | 1.2897–1.3242x | 10/16 | 0 |
| holdout | rust | 0.0139x | 0.0138–0.0141x | 0/16 | 15 |
| all | ast | 0.0101x | 0.0100–0.0102x | 0/32 | 32 |
| all | vm | 1.2496x | 1.2352–1.2628x | 18/32 | 2 |
| all | rust | 0.0132x | 0.0131–0.0133x | 0/32 | 30 |

## Every case

`REGRESSION` means speedup below 0.8; `FASTER` means the lower confidence bound exceeds 1. Memory is median traced-peak candidate/baseline ratio.

| Cohort | Case | Candidate | Speedup | 95% CI | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| calibration | `cal.search.literal.hit` | ast | 0.0084x | 0.0082–0.0086x | 94.53x | REGRESSION |
| calibration | `cal.search.literal.hit` | vm | 1.1417x | 1.1258–1.1593x | 0.73x | FASTER |
| calibration | `cal.search.literal.hit` | rust | 0.0096x | 0.0095–0.0098x | 33.50x | REGRESSION |
| calibration | `cal.search.literal.miss` | ast | 0.0025x | 0.0025–0.0026x | 14152.00x | REGRESSION |
| calibration | `cal.search.literal.miss` | vm | 1.1661x | 1.1427–1.2015x | 0.00x | FASTER |
| calibration | `cal.search.literal.miss` | rust | 0.0064x | 0.0063–0.0067x | 4311.00x | REGRESSION |
| calibration | `cal.search.long-boundary` | ast | 0.0003x | 0.0003–0.0003x | 130.00x | REGRESSION |
| calibration | `cal.search.long-boundary` | vm | 12.8766x | 11.8545–14.1017x | 0.07x | FASTER |
| calibration | `cal.search.long-boundary` | rust | 0.0010x | 0.0009–0.0011x | 139.92x | REGRESSION |
| calibration | `cal.search.class-anchor` | ast | 0.0111x | 0.0108–0.0115x | 13.78x | REGRESSION |
| calibration | `cal.search.class-anchor` | vm | 0.9084x | 0.7956–1.0278x | 0.07x | — |
| calibration | `cal.search.class-anchor` | rust | 0.0145x | 0.0140–0.0151x | 3.31x | REGRESSION |
| calibration | `cal.match.prefix` | ast | 0.0193x | 0.0190–0.0195x | 10.03x | REGRESSION |
| calibration | `cal.match.prefix` | vm | 1.1172x | 1.0135–1.1799x | 0.07x | FASTER |
| calibration | `cal.match.prefix` | rust | 0.0156x | 0.0154–0.0158x | 3.10x | REGRESSION |
| calibration | `cal.fullmatch.structured` | ast | 0.0103x | 0.0097–0.0113x | 24.65x | REGRESSION |
| calibration | `cal.fullmatch.structured` | vm | 0.8286x | 0.7482–0.9368x | 0.07x | — |
| calibration | `cal.fullmatch.structured` | rust | 0.0182x | 0.0172–0.0201x | 2.99x | REGRESSION |
| calibration | `cal.search.look-capture` | ast | 0.0068x | 0.0064–0.0076x | 21.90x | REGRESSION |
| calibration | `cal.search.look-capture` | vm | 0.9005x | 0.8785–0.9396x | 0.08x | — |
| calibration | `cal.search.look-capture` | rust | 0.0162x | 0.0152–0.0182x | 3.24x | REGRESSION |
| calibration | `cal.findall.tokens` | ast | 0.0081x | 0.0080–0.0083x | 11.40x | REGRESSION |
| calibration | `cal.findall.tokens` | vm | 0.7754x | 0.7099–0.8120x | 0.28x | REGRESSION |
| calibration | `cal.findall.tokens` | rust | 0.0034x | 0.0033–0.0034x | 3.12x | REGRESSION |
| calibration | `cal.finditer.groups` | ast | 0.0121x | 0.0113–0.0132x | 13.46x | REGRESSION |
| calibration | `cal.finditer.groups` | vm | 1.3856x | 1.3036–1.4911x | 0.35x | FASTER |
| calibration | `cal.finditer.groups` | rust | 0.0103x | 0.0097–0.0111x | 1.86x | REGRESSION |
| calibration | `cal.split.capture` | ast | 0.0098x | 0.0095–0.0101x | 11.00x | REGRESSION |
| calibration | `cal.split.capture` | vm | 1.0220x | 1.0001–1.0535x | 0.20x | FASTER |
| calibration | `cal.split.capture` | rust | 0.0063x | 0.0062–0.0066x | 2.47x | REGRESSION |
| calibration | `cal.sub.template` | ast | 0.0157x | 0.0152–0.0160x | 14.07x | REGRESSION |
| calibration | `cal.sub.template` | vm | 1.1663x | 1.1115–1.2000x | 0.33x | FASTER |
| calibration | `cal.sub.template` | rust | 0.0157x | 0.0156–0.0158x | 2.31x | REGRESSION |
| calibration | `cal.subn.callable` | ast | 0.0204x | 0.0202–0.0207x | 11.45x | REGRESSION |
| calibration | `cal.subn.callable` | vm | 0.9985x | 0.9853–1.0139x | 0.30x | — |
| calibration | `cal.subn.callable` | rust | 0.0190x | 0.0188–0.0193x | 2.60x | REGRESSION |
| calibration | `cal.bytes.tokens` | ast | 0.0072x | 0.0071–0.0072x | 12.56x | REGRESSION |
| calibration | `cal.bytes.tokens` | vm | 0.8151x | 0.8118–0.8182x | 0.12x | — |
| calibration | `cal.bytes.tokens` | rust | 0.0053x | 0.0052–0.0053x | 3.26x | REGRESSION |
| calibration | `cal.unicode.words` | ast | 0.0056x | 0.0056–0.0057x | 11.60x | REGRESSION |
| calibration | `cal.unicode.words` | vm | 0.6736x | 0.6469–0.6910x | 0.20x | REGRESSION |
| calibration | `cal.unicode.words` | rust | 0.0090x | 0.0090–0.0091x | 2.60x | REGRESSION |
| calibration | `cal.cold.compile-search` | ast | 0.2973x | 0.2939–0.3006x | 11.57x | REGRESSION |
| calibration | `cal.cold.compile-search` | vm | 1.8077x | 1.7820–1.8336x | 0.59x | FASTER |
| calibration | `cal.cold.compile-search` | rust | 0.8287x | 0.8177–0.8400x | 1.82x | — |
| calibration | `cal.module.warm` | ast | 0.0101x | 0.0099–0.0102x | 18.37x | REGRESSION |
| calibration | `cal.module.warm` | vm | 1.0491x | 0.8988–1.1663x | 0.07x | — |
| calibration | `cal.module.warm` | rust | 0.0312x | 0.0307–0.0316x | 3.34x | REGRESSION |
| holdout | `hold.search.literal.hit` | ast | 0.0087x | 0.0085–0.0088x | 94.53x | REGRESSION |
| holdout | `hold.search.literal.hit` | vm | 1.1533x | 1.1402–1.1709x | 0.73x | FASTER |
| holdout | `hold.search.literal.hit` | rust | 0.0102x | 0.0100–0.0104x | 33.42x | REGRESSION |
| holdout | `hold.search.literal.miss` | ast | 0.0027x | 0.0026–0.0027x | 14152.00x | REGRESSION |
| holdout | `hold.search.literal.miss` | vm | 1.1893x | 1.1774–1.2000x | 0.00x | FASTER |
| holdout | `hold.search.literal.miss` | rust | 0.0063x | 0.0063–0.0064x | 4311.00x | REGRESSION |
| holdout | `hold.search.long-boundary` | ast | 0.0003x | 0.0003–0.0003x | 130.31x | REGRESSION |
| holdout | `hold.search.long-boundary` | vm | 14.3140x | 12.5423–16.2622x | 0.07x | FASTER |
| holdout | `hold.search.long-boundary` | rust | 0.0009x | 0.0009–0.0010x | 218.12x | REGRESSION |
| holdout | `hold.search.class-anchor` | ast | 0.0094x | 0.0093–0.0095x | 14.44x | REGRESSION |
| holdout | `hold.search.class-anchor` | vm | 0.9553x | 0.9476–0.9639x | 0.07x | — |
| holdout | `hold.search.class-anchor` | rust | 0.0132x | 0.0131–0.0133x | 3.34x | REGRESSION |
| holdout | `hold.match.prefix` | ast | 0.0207x | 0.0197–0.0226x | 9.08x | REGRESSION |
| holdout | `hold.match.prefix` | vm | 1.1716x | 1.1150–1.2788x | 0.07x | FASTER |
| holdout | `hold.match.prefix` | rust | 0.0164x | 0.0156–0.0179x | 3.09x | REGRESSION |
| holdout | `hold.fullmatch.structured` | ast | 0.0105x | 0.0101–0.0111x | 24.88x | REGRESSION |
| holdout | `hold.fullmatch.structured` | vm | 0.8650x | 0.8370–0.9095x | 0.07x | — |
| holdout | `hold.fullmatch.structured` | rust | 0.0200x | 0.0193–0.0210x | 2.99x | REGRESSION |
| holdout | `hold.search.look-capture` | ast | 0.0076x | 0.0075–0.0077x | 23.81x | REGRESSION |
| holdout | `hold.search.look-capture` | vm | 0.8979x | 0.8912–0.9047x | 0.08x | — |
| holdout | `hold.search.look-capture` | rust | 0.0173x | 0.0172–0.0174x | 3.21x | REGRESSION |
| holdout | `hold.findall.tokens` | ast | 0.0092x | 0.0091–0.0093x | 20.57x | REGRESSION |
| holdout | `hold.findall.tokens` | vm | 0.9268x | 0.9203–0.9331x | 0.21x | — |
| holdout | `hold.findall.tokens` | rust | 0.0058x | 0.0057–0.0058x | 2.99x | REGRESSION |
| holdout | `hold.finditer.groups` | ast | 0.0123x | 0.0118–0.0128x | 13.46x | REGRESSION |
| holdout | `hold.finditer.groups` | vm | 1.4014x | 1.3511–1.4574x | 0.35x | FASTER |
| holdout | `hold.finditer.groups` | rust | 0.0097x | 0.0093–0.0101x | 1.88x | REGRESSION |
| holdout | `hold.split.capture` | ast | 0.0105x | 0.0104–0.0106x | 11.00x | REGRESSION |
| holdout | `hold.split.capture` | vm | 1.0458x | 0.9697–1.1079x | 0.20x | — |
| holdout | `hold.split.capture` | rust | 0.0068x | 0.0068–0.0068x | 2.47x | REGRESSION |
| holdout | `hold.sub.template` | ast | 0.0171x | 0.0166–0.0178x | 14.73x | REGRESSION |
| holdout | `hold.sub.template` | vm | 1.3202x | 1.2770–1.3818x | 0.33x | FASTER |
| holdout | `hold.sub.template` | rust | 0.0166x | 0.0161–0.0172x | 2.31x | REGRESSION |
| holdout | `hold.subn.callable` | ast | 0.0256x | 0.0248–0.0267x | 10.48x | REGRESSION |
| holdout | `hold.subn.callable` | vm | 1.0894x | 1.0552–1.1337x | 0.30x | FASTER |
| holdout | `hold.subn.callable` | rust | 0.0235x | 0.0227–0.0245x | 2.58x | REGRESSION |
| holdout | `hold.bytes.tokens` | ast | 0.0100x | 0.0094–0.0107x | 14.58x | REGRESSION |
| holdout | `hold.bytes.tokens` | vm | 1.0413x | 0.9551–1.1197x | 0.18x | — |
| holdout | `hold.bytes.tokens` | rust | 0.0086x | 0.0082–0.0090x | 2.67x | REGRESSION |
| holdout | `hold.unicode.words` | ast | 0.0084x | 0.0083–0.0084x | 11.99x | REGRESSION |
| holdout | `hold.unicode.words` | vm | 1.0200x | 1.0122–1.0270x | 0.20x | FASTER |
| holdout | `hold.unicode.words` | rust | 0.0116x | 0.0114–0.0117x | 2.58x | REGRESSION |
| holdout | `hold.cold.compile-search` | ast | 0.5085x | 0.4930–0.5216x | 10.02x | REGRESSION |
| holdout | `hold.cold.compile-search` | vm | 1.8739x | 1.7987–1.9852x | 0.60x | FASTER |
| holdout | `hold.cold.compile-search` | rust | 0.9231x | 0.8869–0.9822x | 1.80x | — |
| holdout | `hold.module.warm` | ast | 0.0182x | 0.0180–0.0185x | 16.47x | REGRESSION |
| holdout | `hold.module.warm` | vm | 1.0883x | 1.0524–1.1171x | 0.07x | FASTER |
| holdout | `hold.module.warm` | rust | 0.0328x | 0.0323–0.0334x | 3.33x | REGRESSION |

## Regression explanation

All listed regressions are retained. The AST family pays Python generator/state-allocation and per-position scanning costs. The native VM improves cold compilation but pays state cloning, Python result construction, and wrapper/template costs. Rust pays per-call FFI conversion plus eager continuation allocation. Long misses amplify scanning/boundary work; `findall`, `finditer`, `split`, and substitutions amplify repeated match/result construction. These mechanisms explain the >20% losses shown above; the raw RSS/HWM and traced peaks remain available for inspection.
