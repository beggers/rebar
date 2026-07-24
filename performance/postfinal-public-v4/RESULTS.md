# Expanded public comparison: interrupted, not a result

Status: **FAIL**. The frozen comparison stopped before completing its
**8,192** required cases. Do not calculate an overall speed, ranking,
confidence interval, graph, or winner from the partial run.

| Frozen accounting | Planned | Actually preserved |
| --- | ---: | ---: |
| Complete four-engine cases | 8,192 | 5,975 |
| Paired timing observations | 425,984 | 310,700 |
| Completed summary reports | 1 | 0 |
| Independently verified result reports | 1 | 0 |

Every completed case contains all **13** paired trials for Python, Rust, C,
and Zig: `5,975 × 13 × 4 = 310,700` original observations. The deterministic
gzip stream is valid and preserved at
`evidence/postfinal-public-practice-v4-raw.jsonl.gz`.

The first unmeasured public case is
`cal.broader.astral-emoji-run.00`, selected case index **5,975**, in the
`findall` / `broader-astral-emoji-run` category. Its frozen descriptor
contains an unpaired Unicode surrogate. The runner encodes worker requests
with `ensure_ascii=False` over a strict UTF-8 pipe, so all four independently
started participants fail before running the regex operation:

```text
UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800':
surrogates not allowed
```

Python, Rust, C, and Zig exhibit the same transport failure. This is a
benchmark defect, not a candidate mismatch. The source-bound, prepare-only
diagnostic invokes no timing. Its readable, Unicode-safe report is
`evidence/postfinal-public-practice-v4-interrupted-diagnostic-v2.json`.
The original report remains preserved unchanged as
`evidence/postfinal-public-practice-v4-interrupted-diagnostic.json`.

| Preserved input | SHA-256 |
| --- | --- |
| Frozen manifest | `15789a8ab6ab35ea97b657fed2ae4be0e944da6300067bc7cb3e8222c7c5ea55` |
| Frozen benchmark source | `69d42bf668b60145520ac54873966ccf52c42d624bab809e484e239229256600` |
| Complete partial timing stream | `4132e485b605f924fbc4edf09324987f09361f0562a9884fd0ceb06e09544f8a` |
| Original diagnostic source | `7a031fb7655cd287096c5b1401c4670bce89c42b22e0cc008fb3968578e4ca9c` |
| Original preserved diagnostic | `de46581ef793c3128d9bcd56348ca81a40ca2657c6f443dd61d4c6a2a9732bad` |
| Unicode-safe diagnostic source | `bb6e6d3c39253719d73b6968b2014f8c23a37443ab2014bf698a9bfa50c88bb8` |
| Unicode-safe diagnostic report | `850ec8db3045819e0670dd1449b8991b464abb5bf0941ccbcd0f1b986cb3e734` |

```sh
gzip -t performance/postfinal-public-v4/evidence/postfinal-public-practice-v4-raw.jsonl.gz
gzip -dc performance/postfinal-public-v4/evidence/postfinal-public-practice-v4-raw.jsonl.gz |
  wc -l
sha256sum performance/postfinal-public-v4/manifest.json \
  tools/postfinal_public_practice_v4.py \
  tools/postfinal_public_practice_v4_failure_diagnostic.py \
  tools/postfinal_public_practice_v4_failure_diagnostic_v2.py \
  performance/postfinal-public-v4/evidence/postfinal-public-practice-v4-raw.jsonl.gz \
  performance/postfinal-public-v4/evidence/postfinal-public-practice-v4-interrupted-diagnostic.json \
  performance/postfinal-public-v4/evidence/postfinal-public-practice-v4-interrupted-diagnostic-v2.json
jq '{status, measurement_status,
     classification: .classification.classification,
     completed_public_cases, completed_public_rows,
     worker_count: (.guarded_workers | length),
     identical_unicode_encoding_failure: .classification.identical_unicode_encoding_failure,
     candidate_correctness_mismatch: .classification.candidate_correctness_mismatch,
     observe_requests, timing_performed, holdout_accessed}' \
  performance/postfinal-public-v4/evidence/postfinal-public-practice-v4-interrupted-diagnostic-v2.json
```

The frozen source, denominator, selected cases, partial results, manifest,
and failed timing slot are never replaced. The separate **65,536-case**
one-use holdout remains **NOT OPENED**. A Unicode-safe complete public
comparison remains **NOT MEASURED**.
