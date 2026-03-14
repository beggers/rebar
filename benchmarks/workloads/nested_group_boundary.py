MANIFEST = {
  "schema_version": 1,
  "manifest_id": "nested-group-boundary",
  "spec_refs": [
    "docs/benchmarks/plan.md",
    "docs/spec/drop-in-re-compatibility.md"
  ],
  "notes": [
    "Nested-group boundary workloads keep captures, names, and haystacks intentionally tiny so the scorecard measures helper-call overhead for the newly supported bounded nesting slice rather than regex throughput.",
    "Measured rows cover the bounded `a((b))d` and `a(?P<outer>(?P<inner>b))d` compile/search/fullmatch paths directly, while deeper nesting and quantified nested-group shapes stay as explicit known-gap rows and the supported bounded nested alternation slice now lives in the dedicated nested-group alternation manifest."
  ],
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "module-compile-nested-group-cold-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a((b))d",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "nested-group",
        "cold-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "nested-groups"
      ],
      "notes": [
        "Cold module.compile benchmark for the bounded nested-group slice so compile metadata timing reaches the published benchmark report."
      ]
    },
    {
      "id": "module-search-nested-group-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a((b))d",
      "haystack": "zzabdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "smoke": True,
      "categories": [
        "grouped",
        "nested-group",
        "search",
        "module",
        "warm-cache",
        "smoke"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "nested-groups"
      ],
      "notes": [
        "Warm module.search helper path for the bounded nested-group workflow on a tiny haystack."
      ]
    },
    {
      "id": "pattern-fullmatch-nested-group-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a((b))d",
      "haystack": "abd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "nested-group",
        "fullmatch",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "nested-groups",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the same bounded nested-group workflow."
      ]
    },
    {
      "id": "module-compile-named-nested-group-warm-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(?P<outer>(?P<inner>b))d",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "nested-group",
        "named-group",
        "warm-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "nested-groups",
        "named-groups"
      ],
      "notes": [
        "Warm module.compile path for the bounded named nested-group slice so named metadata timing reaches the benchmark report."
      ]
    },
    {
      "id": "module-search-named-nested-group-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<outer>(?P<inner>b))d",
      "haystack": "zzabdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "nested-group",
        "named-group",
        "search",
        "module",
        "warm-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "nested-groups",
        "named-groups"
      ],
      "notes": [
        "Warm module.search helper path for a tiny named nested-group capture so named runtime workflows produce real timings."
      ]
    },
    {
      "id": "pattern-fullmatch-named-nested-group-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<outer>(?P<inner>b))d",
      "haystack": "abd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "smoke": True,
      "categories": [
        "pattern",
        "grouped",
        "nested-group",
        "named-group",
        "fullmatch",
        "purged-cache",
        "smoke"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "nested-groups",
        "named-groups",
        "cache-purge"
      ],
      "notes": [
        "Smoke-sized Pattern.fullmatch probe for the bounded named nested-group workflow with compile cost kept outside the timed loop."
      ]
    },
    {
      "id": "module-search-triple-nested-group-cold-gap",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(((b)))d",
      "haystack": "zzabdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "nested-group",
        "deeper-nesting",
        "search",
        "module",
        "cold-cache",
        "gap"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "nested-groups",
        "deeper-nesting"
      ],
      "notes": [
        "Explicit triple-nested group gap row so deeper nesting stays visible instead of disappearing while the queue focuses on bounded nested alternation and nearby grouped execution slices."
      ]
    },
    {
      "id": "pattern-fullmatch-named-quantified-nested-group-purged-gap",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<outer>(?P<inner>bc)+)d",
      "haystack": "abcbcd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "nested-group",
        "named-group",
        "quantified",
        "fullmatch",
        "purged-cache",
        "gap"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "nested-groups",
        "named-groups",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Explicit quantified nested-group gap row so one repeated inner capture stays on the benchmark surface instead of disappearing until the broader grouped execution frontier lands."
      ]
    }
  ]
}
