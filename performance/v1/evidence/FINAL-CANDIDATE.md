# Final native candidate performance results

Raw SHA-256: `fad61050ce6a211f7d15a1a1e655cd27c4f6e3e6ade2b5ca2822a0d9c98eb563`. Rows: 1152. All 96 candidate/case results and all 64 regressions are shown below.

## Rankings

| Cohort | Candidate | Geomean | 95% CI | Faster cases | >20% regressions |
| --- | --- | ---: | ---: | ---: | ---: |
| calibration | ast | 0.0099x | 0.0098–0.0100x | 0/16 | 16 |
| calibration | vm | 1.3542x | 1.3256–1.3817x | 10/16 | 1 |
| calibration | rust | 0.0131x | 0.0129–0.0133x | 0/16 | 16 |
| holdout | ast | 0.0112x | 0.0111–0.0114x | 0/16 | 16 |
| holdout | vm | 1.5597x | 1.5363–1.5840x | 14/16 | 0 |
| holdout | rust | 0.0142x | 0.0140–0.0143x | 0/16 | 15 |
| all | ast | 0.0106x | 0.0105–0.0106x | 0/32 | 32 |
| all | vm | 1.4533x | 1.4357–1.4709x | 24/32 | 1 |
| all | rust | 0.0136x | 0.0135–0.0137x | 0/32 | 31 |

## Every case

`REGRESSION` means speedup below 0.8; `FASTER` means the lower confidence bound exceeds 1. Memory is median traced-peak candidate/baseline ratio.

| Cohort | Case | Candidate | Speedup | 95% CI | Memory | Result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| calibration | `cal.search.literal.hit` | ast | 0.0082x | 0.0077–0.0086x | 94.53x | REGRESSION |
| calibration | `cal.search.literal.hit` | vm | 1.1341x | 1.1195–1.1493x | 0.73x | FASTER |
| calibration | `cal.search.literal.hit` | rust | 0.0097x | 0.0096–0.0098x | 33.50x | REGRESSION |
| calibration | `cal.search.literal.miss` | ast | 0.0025x | 0.0024–0.0025x | 14152.00x | REGRESSION |
| calibration | `cal.search.literal.miss` | vm | 1.1180x | 0.9975–1.1878x | 0.00x | — |
| calibration | `cal.search.literal.miss` | rust | 0.0062x | 0.0058–0.0064x | 4311.00x | REGRESSION |
| calibration | `cal.search.long-boundary` | ast | 0.0003x | 0.0003–0.0003x | 130.00x | REGRESSION |
| calibration | `cal.search.long-boundary` | vm | 13.0448x | 12.1692–14.1969x | 0.07x | FASTER |
| calibration | `cal.search.long-boundary` | rust | 0.0010x | 0.0010–0.0011x | 139.92x | REGRESSION |
| calibration | `cal.search.class-anchor` | ast | 0.0114x | 0.0113–0.0114x | 13.78x | REGRESSION |
| calibration | `cal.search.class-anchor` | vm | 0.9898x | 0.9147–1.0509x | 0.07x | — |
| calibration | `cal.search.class-anchor` | rust | 0.0152x | 0.0151–0.0153x | 3.31x | REGRESSION |
| calibration | `cal.match.prefix` | ast | 0.0194x | 0.0185–0.0199x | 10.03x | REGRESSION |
| calibration | `cal.match.prefix` | vm | 1.1233x | 1.0055–1.1922x | 0.07x | FASTER |
| calibration | `cal.match.prefix` | rust | 0.0158x | 0.0157–0.0159x | 3.10x | REGRESSION |
| calibration | `cal.fullmatch.structured` | ast | 0.0105x | 0.0105–0.0106x | 24.65x | REGRESSION |
| calibration | `cal.fullmatch.structured` | vm | 0.9503x | 0.9349–0.9625x | 0.07x | — |
| calibration | `cal.fullmatch.structured` | rust | 0.0186x | 0.0184–0.0188x | 2.99x | REGRESSION |
| calibration | `cal.search.look-capture` | ast | 0.0069x | 0.0068–0.0070x | 21.90x | REGRESSION |
| calibration | `cal.search.look-capture` | vm | 1.2283x | 1.2188–1.2392x | 0.08x | FASTER |
| calibration | `cal.search.look-capture` | rust | 0.0164x | 0.0162–0.0165x | 3.24x | REGRESSION |
| calibration | `cal.findall.tokens` | ast | 0.0093x | 0.0092–0.0095x | 11.40x | REGRESSION |
| calibration | `cal.findall.tokens` | vm | 0.8399x | 0.8178–0.8590x | 0.28x | — |
| calibration | `cal.findall.tokens` | rust | 0.0038x | 0.0037–0.0039x | 3.12x | REGRESSION |
| calibration | `cal.finditer.groups` | ast | 0.0126x | 0.0121–0.0134x | 13.46x | REGRESSION |
| calibration | `cal.finditer.groups` | vm | 1.4953x | 1.4137–1.6118x | 0.35x | FASTER |
| calibration | `cal.finditer.groups` | rust | 0.0108x | 0.0102–0.0116x | 1.86x | REGRESSION |
| calibration | `cal.split.capture` | ast | 0.0116x | 0.0108–0.0128x | 11.00x | REGRESSION |
| calibration | `cal.split.capture` | vm | 1.6956x | 1.3929–2.0539x | 0.20x | FASTER |
| calibration | `cal.split.capture` | rust | 0.0071x | 0.0060–0.0085x | 2.47x | REGRESSION |
| calibration | `cal.sub.template` | ast | 0.0171x | 0.0168–0.0175x | 14.07x | REGRESSION |
| calibration | `cal.sub.template` | vm | 1.8090x | 1.7794–1.8319x | 0.12x | FASTER |
| calibration | `cal.sub.template` | rust | 0.0166x | 0.0162–0.0170x | 2.31x | REGRESSION |
| calibration | `cal.subn.callable` | ast | 0.0220x | 0.0214–0.0227x | 11.45x | REGRESSION |
| calibration | `cal.subn.callable` | vm | 1.1591x | 1.1188–1.2109x | 0.25x | FASTER |
| calibration | `cal.subn.callable` | rust | 0.0201x | 0.0193–0.0210x | 2.60x | REGRESSION |
| calibration | `cal.bytes.tokens` | ast | 0.0078x | 0.0074–0.0081x | 12.56x | REGRESSION |
| calibration | `cal.bytes.tokens` | vm | 0.8447x | 0.7991–0.8765x | 0.12x | — |
| calibration | `cal.bytes.tokens` | rust | 0.0059x | 0.0058–0.0059x | 3.26x | REGRESSION |
| calibration | `cal.unicode.words` | ast | 0.0067x | 0.0063–0.0072x | 11.60x | REGRESSION |
| calibration | `cal.unicode.words` | vm | 0.7325x | 0.6874–0.7943x | 0.20x | REGRESSION |
| calibration | `cal.unicode.words` | rust | 0.0106x | 0.0099–0.0114x | 2.60x | REGRESSION |
| calibration | `cal.cold.compile-search` | ast | 0.2956x | 0.2938–0.2974x | 11.57x | REGRESSION |
| calibration | `cal.cold.compile-search` | vm | 1.8125x | 1.7803–1.8411x | 0.60x | FASTER |
| calibration | `cal.cold.compile-search` | rust | 0.7842x | 0.7679–0.7973x | 1.82x | REGRESSION |
| calibration | `cal.module.warm` | ast | 0.0109x | 0.0102–0.0123x | 18.37x | REGRESSION |
| calibration | `cal.module.warm` | vm | 1.1903x | 1.1140–1.3367x | 0.07x | FASTER |
| calibration | `cal.module.warm` | rust | 0.0341x | 0.0319–0.0383x | 3.34x | REGRESSION |
| holdout | `hold.search.literal.hit` | ast | 0.0085x | 0.0084–0.0086x | 94.53x | REGRESSION |
| holdout | `hold.search.literal.hit` | vm | 1.1607x | 1.1406–1.1854x | 0.73x | FASTER |
| holdout | `hold.search.literal.hit` | rust | 0.0098x | 0.0096–0.0099x | 33.42x | REGRESSION |
| holdout | `hold.search.literal.miss` | ast | 0.0029x | 0.0027–0.0032x | 14152.00x | REGRESSION |
| holdout | `hold.search.literal.miss` | vm | 1.2692x | 1.1950–1.3955x | 0.00x | FASTER |
| holdout | `hold.search.literal.miss` | rust | 0.0066x | 0.0062–0.0073x | 4311.00x | REGRESSION |
| holdout | `hold.search.long-boundary` | ast | 0.0003x | 0.0003–0.0003x | 130.31x | REGRESSION |
| holdout | `hold.search.long-boundary` | vm | 16.9352x | 14.7352–19.5789x | 0.07x | FASTER |
| holdout | `hold.search.long-boundary` | rust | 0.0010x | 0.0009–0.0011x | 218.12x | REGRESSION |
| holdout | `hold.search.class-anchor` | ast | 0.0104x | 0.0103–0.0105x | 14.44x | REGRESSION |
| holdout | `hold.search.class-anchor` | vm | 1.0126x | 0.9793–1.0360x | 0.07x | — |
| holdout | `hold.search.class-anchor` | rust | 0.0145x | 0.0144–0.0147x | 3.34x | REGRESSION |
| holdout | `hold.match.prefix` | ast | 0.0221x | 0.0218–0.0225x | 9.08x | REGRESSION |
| holdout | `hold.match.prefix` | vm | 1.2622x | 1.2431–1.2794x | 0.07x | FASTER |
| holdout | `hold.match.prefix` | rust | 0.0173x | 0.0171–0.0175x | 3.09x | REGRESSION |
| holdout | `hold.fullmatch.structured` | ast | 0.0105x | 0.0104–0.0106x | 24.88x | REGRESSION |
| holdout | `hold.fullmatch.structured` | vm | 0.9575x | 0.9482–0.9665x | 0.07x | — |
| holdout | `hold.fullmatch.structured` | rust | 0.0200x | 0.0198–0.0202x | 2.99x | REGRESSION |
| holdout | `hold.search.look-capture` | ast | 0.0078x | 0.0077–0.0079x | 23.81x | REGRESSION |
| holdout | `hold.search.look-capture` | vm | 1.0669x | 1.0446–1.0872x | 0.08x | FASTER |
| holdout | `hold.search.look-capture` | rust | 0.0177x | 0.0176–0.0178x | 3.21x | REGRESSION |
| holdout | `hold.findall.tokens` | ast | 0.0095x | 0.0093–0.0097x | 20.57x | REGRESSION |
| holdout | `hold.findall.tokens` | vm | 1.3010x | 1.2763–1.3248x | 0.21x | FASTER |
| holdout | `hold.findall.tokens` | rust | 0.0058x | 0.0057–0.0059x | 2.99x | REGRESSION |
| holdout | `hold.finditer.groups` | ast | 0.0118x | 0.0114–0.0123x | 13.46x | REGRESSION |
| holdout | `hold.finditer.groups` | vm | 1.4238x | 1.3823–1.4684x | 0.35x | FASTER |
| holdout | `hold.finditer.groups` | rust | 0.0095x | 0.0092–0.0099x | 1.88x | REGRESSION |
| holdout | `hold.split.capture` | ast | 0.0110x | 0.0106–0.0116x | 11.00x | REGRESSION |
| holdout | `hold.split.capture` | vm | 1.7685x | 1.6872–1.8497x | 0.20x | FASTER |
| holdout | `hold.split.capture` | rust | 0.0071x | 0.0069–0.0075x | 2.47x | REGRESSION |
| holdout | `hold.sub.template` | ast | 0.0169x | 0.0166–0.0172x | 14.73x | REGRESSION |
| holdout | `hold.sub.template` | vm | 1.8289x | 1.8016–1.8582x | 0.12x | FASTER |
| holdout | `hold.sub.template` | rust | 0.0165x | 0.0163–0.0167x | 2.31x | REGRESSION |
| holdout | `hold.subn.callable` | ast | 0.0254x | 0.0240–0.0275x | 10.48x | REGRESSION |
| holdout | `hold.subn.callable` | vm | 1.1741x | 1.0708–1.3050x | 0.25x | FASTER |
| holdout | `hold.subn.callable` | rust | 0.0237x | 0.0224–0.0256x | 2.58x | REGRESSION |
| holdout | `hold.bytes.tokens` | ast | 0.0107x | 0.0102–0.0112x | 14.58x | REGRESSION |
| holdout | `hold.bytes.tokens` | vm | 1.9014x | 1.6645–2.0790x | 0.18x | FASTER |
| holdout | `hold.bytes.tokens` | rust | 0.0089x | 0.0086–0.0093x | 2.67x | REGRESSION |
| holdout | `hold.unicode.words` | ast | 0.0084x | 0.0084–0.0085x | 11.99x | REGRESSION |
| holdout | `hold.unicode.words` | vm | 1.4906x | 1.4790–1.5028x | 0.20x | FASTER |
| holdout | `hold.unicode.words` | rust | 0.0117x | 0.0116–0.0118x | 2.58x | REGRESSION |
| holdout | `hold.cold.compile-search` | ast | 0.5107x | 0.4951–0.5217x | 10.02x | REGRESSION |
| holdout | `hold.cold.compile-search` | vm | 1.8074x | 1.7785–1.8363x | 0.61x | FASTER |
| holdout | `hold.cold.compile-search` | rust | 0.8446x | 0.8331–0.8550x | 1.80x | — |
| holdout | `hold.module.warm` | ast | 0.0186x | 0.0182–0.0191x | 16.47x | REGRESSION |
| holdout | `hold.module.warm` | vm | 1.0450x | 1.0113–1.0770x | 0.07x | FASTER |
| holdout | `hold.module.warm` | rust | 0.0335x | 0.0330–0.0344x | 3.33x | REGRESSION |

## Regression explanation

All listed regressions are retained. The Python backtracker spends most of its time creating Python states and scanning one position at a time. The Rust engine repeatedly crosses the Python/Rust boundary and creates eager continuation state, which dominates these short calls. The native C engine has 1 large slowdown(s): `cal.unicode.words`. Its remaining Unicode-word case repeatedly checks Unicode word boundaries and character categories; this path cannot use the simpler one-pass token scan. Long misses amplify scanning, while find-all, iteration, splitting, and replacement amplify per-match work. The raw memory observations and every case remain available for inspection.
