MANIFEST = {
  "schema_version": 1,
  "manifest_id": "grouped-alternation-replacement-boundary",
  "spec_refs": [
    "docs/benchmarks/plan.md",
    "docs/spec/drop-in-re-compatibility.md"
  ],
  "notes": [
    "Grouped-alternation replacement boundary workloads keep replacements and haystacks intentionally tiny so the scorecard measures helper-call overhead for the newly supported grouped-branch replacement-template slice rather than regex throughput.",
    "Measured rows cover the bounded `a(b|c)d` plus `\\\\1x` and `a(?P<word>b|c)d` plus `\\\\g<word>x` `sub()`/`subn()` flows through module and compiled-`Pattern` entrypoints, while nested grouped replacement-template shapes stay as explicit known-gap rows until the nested-group follow-ons land."
  ],
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "module-sub-template-grouped-alternation-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b|c)d",
      "replacement": "\\1x",
      "haystack": "abdacd",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "smoke": True,
      "categories": [
        "grouped",
        "alternation",
        "replacement",
        "template",
        "sub",
        "module",
        "warm-cache",
        "smoke"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "alternation",
        "replacement-template"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded grouped-alternation replacement-template workflow."
      ]
    },
    {
      "id": "module-subn-template-grouped-alternation-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b|c)d",
      "replacement": "\\1x",
      "haystack": "abdacd",
      "flags": 0,
      "count": 1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "alternation",
        "replacement",
        "template",
        "subn",
        "module",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "alternation",
        "replacement-template"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded grouped-alternation replacement-template count workflow."
      ]
    },
    {
      "id": "pattern-sub-template-grouped-alternation-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b|c)d",
      "replacement": "\\1x",
      "haystack": "acdabd",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "alternation",
        "replacement",
        "template",
        "sub",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "alternation",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the same bounded grouped-alternation replacement-template workflow."
      ]
    },
    {
      "id": "pattern-subn-template-grouped-alternation-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b|c)d",
      "replacement": "\\1x",
      "haystack": "acdabd",
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
        "subn",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "alternation",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded grouped-alternation replacement-template count workflow."
      ]
    },
    {
      "id": "module-sub-template-named-grouped-alternation-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b|c)d",
      "replacement": "\\g<word>x",
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
        "named-group",
        "sub",
        "module",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "alternation",
        "named-groups",
        "replacement-template"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded named grouped-alternation replacement-template workflow."
      ]
    },
    {
      "id": "module-subn-template-named-grouped-alternation-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b|c)d",
      "replacement": "\\g<word>x",
      "haystack": "abdacd",
      "flags": 0,
      "count": 1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "alternation",
        "replacement",
        "template",
        "named-group",
        "subn",
        "module",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "alternation",
        "named-groups",
        "replacement-template"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named grouped-alternation replacement-template count workflow."
      ]
    },
    {
      "id": "pattern-sub-template-named-grouped-alternation-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b|c)d",
      "replacement": "\\g<word>x",
      "haystack": "acdabd",
      "flags": 0,
      "count": 0,
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
        "sub",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "alternation",
        "named-groups",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded named grouped-alternation replacement-template workflow."
      ]
    },
    {
      "id": "pattern-subn-template-named-grouped-alternation-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b|c)d",
      "replacement": "\\g<word>x",
      "haystack": "acdabd",
      "flags": 0,
      "count": 1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "smoke": True,
      "categories": [
        "pattern",
        "grouped",
        "alternation",
        "replacement",
        "template",
        "named-group",
        "subn",
        "purged-cache",
        "smoke"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "alternation",
        "named-groups",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named grouped-alternation replacement-template count workflow."
      ]
    },
    {
      "id": "module-sub-template-nested-grouped-alternation-cold-gap",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a((b|c))d",
      "replacement": "\\1x",
      "haystack": "abdacd",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "alternation",
        "replacement",
        "template",
        "nested-groups",
        "sub",
        "module",
        "cold-cache",
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
        "Explicit nested-group grouped-alternation replacement-template gap row so broader grouped replacement shapes stay visible while nested-group work is still queued."
      ]
    },
    {
      "id": "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<outer>(b|c))d",
      "replacement": "\\g<outer>x",
      "haystack": "acdabd",
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
        "Explicit named nested-group grouped-alternation replacement-template gap row so broader alternation-and-replacement shapes stay visible instead of disappearing until the nested-group follow-ons land."
      ]
    }
  ]
}
