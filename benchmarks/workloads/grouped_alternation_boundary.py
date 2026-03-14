MANIFEST = {
  "schema_version": 1,
  "manifest_id": "grouped-alternation-boundary",
  "spec_refs": [
    "docs/benchmarks/plan.md",
    "docs/spec/drop-in-re-compatibility.md"
  ],
  "notes": [
    "Grouped-alternation boundary workloads keep captures, branches, replacements, and haystacks intentionally tiny so the scorecard measures helper-call overhead for the newly supported grouped-branch slice rather than regex throughput.",
    "Measured rows cover the bounded `a(b|c)d` and `a(?P<word>b|c)d` compile/search/fullmatch paths directly, while broader nested grouped replacement-template shapes stay as explicit known-gap rows and the supported bounded replacement slice now lives in the dedicated grouped-alternation replacement manifest."
  ],
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "module-compile-grouped-alternation-cold-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(b|c)d",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "alternation",
        "cold-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "alternation"
      ],
      "notes": [
        "Cold module.compile benchmark for the bounded grouped-alternation slice so compile metadata timing reaches the published benchmark report."
      ]
    },
    {
      "id": "module-search-grouped-alternation-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(b|c)d",
      "haystack": "zzacdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "smoke": True,
      "categories": [
        "grouped",
        "alternation",
        "search",
        "module",
        "warm-cache",
        "smoke"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "alternation"
      ],
      "notes": [
        "Warm module.search helper path for the bounded grouped-alternation workflow on a tiny haystack."
      ]
    },
    {
      "id": "pattern-fullmatch-grouped-alternation-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(b|c)d",
      "haystack": "abd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "alternation",
        "fullmatch",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "alternation",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the same bounded grouped-alternation workflow."
      ]
    },
    {
      "id": "module-compile-named-grouped-alternation-warm-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(?P<word>b|c)d",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "alternation",
        "named-group",
        "warm-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "alternation",
        "named-groups"
      ],
      "notes": [
        "Warm module.compile path for the bounded named grouped-alternation slice so named metadata timing reaches the benchmark report."
      ]
    },
    {
      "id": "module-search-named-grouped-alternation-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<word>b|c)d",
      "haystack": "zzabdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "alternation",
        "named-group",
        "search",
        "module",
        "warm-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "alternation",
        "named-groups"
      ],
      "notes": [
        "Warm module.search helper path for a tiny named grouped-alternation capture so named runtime workflows produce real timings."
      ]
    },
    {
      "id": "pattern-fullmatch-named-grouped-alternation-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<word>b|c)d",
      "haystack": "acd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "smoke": True,
      "categories": [
        "pattern",
        "grouped",
        "alternation",
        "named-group",
        "fullmatch",
        "purged-cache",
        "smoke"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "alternation",
        "named-groups",
        "cache-purge"
      ],
      "notes": [
        "Smoke-sized Pattern.fullmatch probe for the bounded named grouped-alternation workflow with compile cost kept outside the timed loop."
      ]
    },
    {
      "id": "module-sub-template-nested-grouped-alternation-warm-gap",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a((b|c))d",
      "replacement": "<\\1>",
      "haystack": "abdacd",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "alternation",
        "replacement",
        "template",
        "nested-groups",
        "sub",
        "warm-cache",
        "gap"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "alternation",
        "nested-groups",
        "replacement-template"
      ],
      "notes": [
        "Explicit nested grouped-alternation replacement-template gap row so broader grouped replacement shapes stay visible while nested-group work is still queued."
      ]
    },
    {
      "id": "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<outer>(b|c))d",
      "replacement": "<\\g<outer>>",
      "haystack": "abdacd",
      "flags": 0,
      "count": 1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "alternation",
        "replacement",
        "template",
        "named-group",
        "nested-groups",
        "subn",
        "purged-cache",
        "gap"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "alternation",
        "named-groups",
        "nested-groups",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Explicit named nested grouped-alternation replacement-template gap row so broader alternation-and-replacement shapes stay visible instead of disappearing until the nested-group follow-ons land."
      ]
    }
  ]
}
