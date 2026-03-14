MANIFEST = {
  "schema_version": 1,
  "manifest_id": "optional-group-boundary",
  "spec_refs": [
    "docs/benchmarks/plan.md",
    "docs/spec/drop-in-re-compatibility.md"
  ],
  "notes": [
    "Optional-group boundary workloads keep captures, quantifiers, and haystacks intentionally tiny so the scorecard measures helper-call overhead for the newly supported bounded optional-group slice rather than regex throughput.",
    "Measured rows cover the bounded `a(b)?d` and `a(?P<word>b)?d` compile/search/fullmatch paths directly, while conditional combinations stay as explicit known-gap rows until the queued bounded conditional follow-on lands."
  ],
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "module-compile-optional-group-cold-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(b)?d",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "optional-group",
        "quantifier",
        "cold-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "optional-groups",
        "quantifiers"
      ],
      "notes": [
        "Cold module.compile benchmark for the bounded optional-group slice so compile metadata timing reaches the published benchmark report."
      ]
    },
    {
      "id": "module-search-optional-group-present-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(b)?d",
      "haystack": "zzabdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "smoke": True,
      "categories": [
        "grouped",
        "optional-group",
        "quantifier",
        "search",
        "module",
        "present",
        "warm-cache",
        "smoke"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "optional-groups",
        "quantifiers"
      ],
      "notes": [
        "Warm module.search helper path for the bounded numbered optional-group workflow when the capture is present on a tiny haystack."
      ]
    },
    {
      "id": "pattern-fullmatch-optional-group-absent-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(b)?d",
      "haystack": "ad",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "quantifier",
        "fullmatch",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "optional-groups",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the same bounded numbered optional-group workflow when the capture is omitted."
      ]
    },
    {
      "id": "module-compile-named-optional-group-warm-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(?P<word>b)?d",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "optional-group",
        "quantifier",
        "named-group",
        "warm-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "optional-groups",
        "quantifiers",
        "named-groups"
      ],
      "notes": [
        "Warm module.compile path for the bounded named optional-group slice so named metadata timing reaches the benchmark report."
      ]
    },
    {
      "id": "module-search-named-optional-group-absent-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<word>b)?d",
      "haystack": "zzadzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "quantifier",
        "named-group",
        "search",
        "module",
        "absent",
        "warm-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "optional-groups",
        "quantifiers",
        "named-groups"
      ],
      "notes": [
        "Warm module.search helper path for a tiny named optional-group capture when the group is omitted so named runtime workflows produce real timings."
      ]
    },
    {
      "id": "pattern-fullmatch-named-optional-group-present-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<word>b)?d",
      "haystack": "abd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "smoke": True,
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "quantifier",
        "named-group",
        "fullmatch",
        "present",
        "purged-cache",
        "smoke"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "optional-groups",
        "quantifiers",
        "named-groups",
        "cache-purge"
      ],
      "notes": [
        "Smoke-sized Pattern.fullmatch probe for the bounded named optional-group workflow when the capture is present with compile cost kept outside the timed loop."
      ]
    },
    {
      "id": "module-search-numbered-optional-group-conditional-cold-gap",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(b)?(?(1)c|d)e",
      "haystack": "zzabcezz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "quantifier",
        "optional-group",
        "conditional",
        "search",
        "module",
        "unsupported",
        "cold-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "optional-groups",
        "quantifiers",
        "conditionals"
      ],
      "notes": [
        "Explicit conditional gap row so optional-group group-exists workflows stay visible instead of disappearing before the queued bounded conditional follow-on lands."
      ]
    }
  ]
}
