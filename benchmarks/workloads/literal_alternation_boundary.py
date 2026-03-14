MANIFEST = {
  "schema_version": 1,
  "manifest_id": "literal-alternation-boundary",
  "spec_refs": [
    "docs/benchmarks/plan.md",
    "docs/spec/drop-in-re-compatibility.md"
  ],
  "notes": [
    "Literal-alternation boundary workloads keep patterns and haystacks intentionally tiny so the scorecard measures helper-call overhead for the newly supported top-level `ab|ac` branch-selection slice rather than regex throughput.",
    "The bounded compile plus module and Pattern match paths are measured directly here, while nested grouped-branch shapes stay as explicit known-gap rows until the nested-group follow-on lands."
  ],
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "module-compile-literal-alternation-cold-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "ab|ac",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "alternation",
        "literal",
        "cold-cache"
      ],
      "syntax_features": [
        "module-compile",
        "alternation",
        "literal-branches"
      ],
      "notes": [
        "Cold module.compile benchmark for the bounded top-level literal-alternation slice so compile metadata timing reaches the published benchmark report."
      ]
    },
    {
      "id": "module-search-literal-alternation-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "ab|ac",
      "haystack": "zzaczz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "smoke": True,
      "categories": [
        "alternation",
        "literal",
        "search",
        "module",
        "warm-cache",
        "smoke"
      ],
      "syntax_features": [
        "module-search",
        "alternation",
        "literal-branches"
      ],
      "notes": [
        "Warm module.search helper path for the bounded top-level literal-alternation workflow on a tiny haystack."
      ]
    },
    {
      "id": "pattern-fullmatch-literal-alternation-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "ab|ac",
      "haystack": "ac",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "smoke": True,
      "categories": [
        "pattern",
        "alternation",
        "literal",
        "fullmatch",
        "purged-cache",
        "smoke"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "alternation",
        "literal-branches",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the same bounded top-level literal-alternation workflow."
      ]
    },
    {
      "id": "module-search-nested-grouped-branch-from-literal-frontier-cold-gap",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a((b|c))d",
      "haystack": "zzabdz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "alternation",
        "grouped",
        "search",
        "module",
        "cold-cache",
        "gap"
      ],
      "syntax_features": [
        "module-search",
        "alternation",
        "grouping-forms",
        "nested-groups"
      ],
      "notes": [
        "Explicit nested-group gap row so branch selection inside an extra grouped layer stays visible on the benchmark surface while nested-group work is still queued."
      ]
    },
    {
      "id": "pattern-fullmatch-named-nested-grouped-branch-from-literal-frontier-purged-gap",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<outer>(b|c))d",
      "haystack": "abd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "alternation",
        "grouped",
        "named-group",
        "fullmatch",
        "purged-cache",
        "gap"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "alternation",
        "grouping-forms",
        "named-groups",
        "nested-groups",
        "cache-purge"
      ],
      "notes": [
        "Explicit named nested-group gap row so branch selection inside a named outer group stays visible instead of disappearing until the nested-group follow-on lands."
      ]
    }
  ]
}
