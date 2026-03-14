MANIFEST = {
  "schema_version": 1,
  "manifest_id": "literal-flag-boundary",
  "spec_refs": [
    "docs/benchmarks/plan.md",
    "docs/spec/drop-in-re-compatibility.md"
  ],
  "notes": [
    "Literal-flag boundary workloads keep patterns and haystacks intentionally tiny so the timings expose bounded flag-sensitive helper-call overhead instead of regex throughput.",
    "Supported API-level IGNORECASE, inline-flag, and bytes-LOCALE helpers are measured directly, while unsupported flag combinations stay in the same pack as explicit known-gap rows rather than disappearing from the scorecard."
  ],
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "module-search-inline-flag-warm-str-hit",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "(?i)abc",
      "haystack": "zzaBczz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "smoke": True,
      "categories": [
        "flag",
        "inline-flag",
        "search",
        "literal",
        "warm-cache",
        "smoke"
      ],
      "syntax_features": [
        "module-search",
        "literal-text",
        "inline-flags"
      ],
      "notes": [
        "Warm module.search inline-flag helper path over a tiny str haystack with a single bounded literal hit."
      ]
    },
    {
      "id": "module-search-locale-purged-bytes-hit",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "abc",
      "haystack": "zzabczz",
      "flags": 4,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "flag",
        "locale",
        "search",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "module-search",
        "pattern-text-model",
        "bytes-locale",
        "cache-purge"
      ],
      "notes": [
        "Bytes module.search LOCALE path that keeps purge provenance visible without broadening into haystack-throughput timing."
      ]
    },
    {
      "id": "module-match-ignorecase-warm-str-hit",
      "bucket": "module-match",
      "family": "module",
      "operation": "module.match",
      "pattern": "AbC",
      "haystack": "aBcdef",
      "flags": 2,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "flag",
        "ignorecase",
        "match",
        "literal",
        "warm-cache"
      ],
      "syntax_features": [
        "module-match",
        "literal-text",
        "api-level-ignorecase"
      ],
      "notes": [
        "Warm module.match IGNORECASE helper path on a tiny prefix-match str haystack."
      ]
    },
    {
      "id": "module-match-ignorecase-purged-bytes-hit",
      "bucket": "module-match",
      "family": "module",
      "operation": "module.match",
      "pattern": "AbC",
      "haystack": "aBcdef",
      "flags": 2,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "flag",
        "ignorecase",
        "match",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "module-match",
        "pattern-text-model",
        "api-level-ignorecase",
        "cache-purge"
      ],
      "notes": [
        "Bytes module.match IGNORECASE path that keeps cache-reset provenance visible while staying in the tiny helper-boundary regime."
      ]
    },
    {
      "id": "pattern-search-inline-flag-warm-str-hit",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "(?i)abc",
      "haystack": "zzaBczz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "flag",
        "inline-flag",
        "search",
        "literal",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-search",
        "literal-text",
        "inline-flags"
      ],
      "notes": [
        "Warm precompiled Pattern.search inline-flag path on str input so compile cost stays outside the timed loop."
      ]
    },
    {
      "id": "pattern-search-locale-purged-bytes-hit",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "abc",
      "haystack": "zzabczz",
      "flags": 4,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "flag",
        "locale",
        "search",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-search",
        "pattern-text-model",
        "bytes-locale",
        "cache-purge"
      ],
      "notes": [
        "Bytes precompiled Pattern.search LOCALE path that keeps purge provenance visible while isolating bound-method overhead."
      ]
    },
    {
      "id": "pattern-fullmatch-ignorecase-warm-str-hit",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "AbC",
      "haystack": "aBc",
      "flags": 2,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "flag",
        "ignorecase",
        "fullmatch",
        "literal",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "literal-text",
        "api-level-ignorecase"
      ],
      "notes": [
        "Warm precompiled Pattern.fullmatch IGNORECASE path on a tiny exact-match str haystack."
      ]
    },
    {
      "id": "pattern-fullmatch-ignorecase-purged-bytes-hit",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "AbC",
      "haystack": "aBc",
      "flags": 2,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "smoke": True,
      "categories": [
        "pattern",
        "flag",
        "ignorecase",
        "fullmatch",
        "bytes",
        "purged-cache",
        "smoke"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "pattern-text-model",
        "api-level-ignorecase",
        "cache-purge"
      ],
      "notes": [
        "Smoke-sized bytes Pattern.fullmatch IGNORECASE probe that keeps bound helper timing and purge provenance easy to rerun."
      ]
    },
    {
      "id": "module-search-ignorecase-ascii-cold-gap",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "abc",
      "haystack": "ABC",
      "flags": 258,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "flag",
        "unsupported",
        "ignorecase",
        "ascii",
        "cold-cache"
      ],
      "syntax_features": [
        "module-search",
        "literal-text",
        "api-level-ignorecase",
        "flag-combination"
      ],
      "notes": [
        "Explicit known-gap row for the current unsupported module-level IGNORECASE|ASCII literal helper combination."
      ]
    },
    {
      "id": "pattern-search-ignorecase-ascii-warm-gap",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "abc",
      "haystack": "ABC",
      "flags": 258,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "flag",
        "unsupported",
        "ignorecase",
        "ascii",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-search",
        "literal-text",
        "api-level-ignorecase",
        "flag-combination"
      ],
      "notes": [
        "Explicit known-gap row for the current unsupported precompiled IGNORECASE|ASCII pattern helper combination."
      ]
    }
  ]
}
