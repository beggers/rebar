MANIFEST = {
  "schema_version": 1,
  "manifest_id": "ranged-repeat-quantified-group-boundary",
  "spec_refs": [
    "docs/benchmarks/plan.md",
    "docs/spec/drop-in-re-compatibility.md"
  ],
  "notes": [
    "Ranged-repeat quantified-group boundary workloads keep captures, counted ranges, and haystacks intentionally tiny so the scorecard measures helper-call overhead for the newly supported bounded counted-range slice rather than regex throughput.",
    "Measured rows cover the bounded `a(bc){1,2}d` and `a(?P<word>bc){1,2}d` compile/search/fullmatch paths directly, while broader counted ranges and quantified alternation inside ranged repeats stay as explicit known-gap rows until queued follow-on slices land."
  ],
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "module-compile-numbered-ranged-repeat-group-cold-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(bc){1,2}d",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "quantifier",
        "ranged-repeat",
        "counted-repeat",
        "cold-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "quantifiers",
        "counted-repeats",
        "ranged-repeats"
      ],
      "notes": [
        "Cold module.compile benchmark for the bounded numbered ranged-repeat quantified-group slice so compile metadata timing reaches the published benchmark report."
      ]
    },
    {
      "id": "module-search-numbered-ranged-repeat-group-lower-bound-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(bc){1,2}d",
      "haystack": "zzabcdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "smoke": True,
      "categories": [
        "grouped",
        "quantifier",
        "ranged-repeat",
        "counted-repeat",
        "search",
        "module",
        "lower-bound",
        "warm-cache",
        "smoke"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "quantifiers",
        "counted-repeats",
        "ranged-repeats"
      ],
      "notes": [
        "Warm module.search helper path for the bounded numbered ranged-repeat workflow on a tiny lower-bound haystack."
      ]
    },
    {
      "id": "pattern-fullmatch-numbered-ranged-repeat-group-upper-bound-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(bc){1,2}d",
      "haystack": "abcbcd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "quantifier",
        "ranged-repeat",
        "counted-repeat",
        "fullmatch",
        "upper-bound",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "quantifiers",
        "counted-repeats",
        "ranged-repeats",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the same bounded numbered ranged-repeat workflow at the supported upper bound."
      ]
    },
    {
      "id": "module-compile-named-ranged-repeat-group-warm-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(?P<word>bc){1,2}d",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "quantifier",
        "ranged-repeat",
        "counted-repeat",
        "named-group",
        "warm-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "quantifiers",
        "counted-repeats",
        "ranged-repeats",
        "named-groups"
      ],
      "notes": [
        "Warm module.compile path for the bounded named ranged-repeat slice so named metadata timing reaches the benchmark report."
      ]
    },
    {
      "id": "module-search-named-ranged-repeat-group-upper-bound-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<word>bc){1,2}d",
      "haystack": "zzabcbcdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "quantifier",
        "ranged-repeat",
        "counted-repeat",
        "named-group",
        "search",
        "module",
        "upper-bound",
        "warm-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "quantifiers",
        "counted-repeats",
        "ranged-repeats",
        "named-groups"
      ],
      "notes": [
        "Warm module.search helper path for a tiny named ranged-repeat capture at the supported upper bound so named runtime workflows produce real timings."
      ]
    },
    {
      "id": "pattern-fullmatch-named-ranged-repeat-group-lower-bound-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<word>bc){1,2}d",
      "haystack": "abcd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "smoke": True,
      "categories": [
        "pattern",
        "grouped",
        "quantifier",
        "ranged-repeat",
        "counted-repeat",
        "named-group",
        "fullmatch",
        "lower-bound",
        "purged-cache",
        "smoke"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "quantifiers",
        "counted-repeats",
        "ranged-repeats",
        "named-groups",
        "cache-purge"
      ],
      "notes": [
        "Smoke-sized Pattern.fullmatch probe for the bounded named ranged-repeat workflow at the supported lower bound with compile cost kept outside the timed loop."
      ]
    },
    {
      "id": "module-search-numbered-ranged-repeat-group-wider-range-cold-gap",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(bc){1,4}d",
      "haystack": "zzabcbcbcbcdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "quantifier",
        "ranged-repeat",
        "counted-repeat",
        "search",
        "module",
        "unsupported",
        "cold-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "quantifiers",
        "counted-repeats",
        "ranged-repeats"
      ],
      "notes": [
        "Explicit wider-range known-gap row so counted repeats beyond the bounded `{1,2}` frontier stay visible without duplicating the now-supported `{1,3}` slice."
      ]
    },
    {
      "id": "pattern-fullmatch-named-ranged-repeat-group-alternation-purged-gap",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<word>bc|de){1,2}d",
      "haystack": "abcbcd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "quantifier",
        "ranged-repeat",
        "counted-repeat",
        "alternation",
        "named-group",
        "fullmatch",
        "unsupported",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "quantifiers",
        "counted-repeats",
        "ranged-repeats",
        "alternation",
        "named-groups",
        "cache-purge"
      ],
      "notes": [
        "Explicit quantified-alternation known-gap row so alternation inside ranged repeats stays on the benchmark surface instead of disappearing."
      ]
    }
  ]
}
