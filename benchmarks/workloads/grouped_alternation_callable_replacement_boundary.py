MANIFEST = {
  "schema_version": 1,
  "manifest_id": "grouped-alternation-callable-replacement-boundary",
  "spec_refs": [
    "docs/benchmarks/plan.md",
    "docs/spec/drop-in-re-compatibility.md"
  ],
  "notes": [
    "Grouped-alternation callable-replacement boundary workloads keep callbacks, captures, and haystacks intentionally tiny so the scorecard measures helper-call overhead for the newly supported grouped-branch callback slice rather than regex throughput.",
    "Measured rows cover the bounded `a(b|c)d` and `a(?P<word>b|c)d` `sub()`/`subn()` callable flows through module and compiled-`Pattern` entrypoints, while nested grouped callback shapes stay as explicit known-gap rows until the nested-group follow-ons land."
  ],
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "module-sub-callable-grouped-alternation-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b|c)d",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "callable",
        "sub",
        "module",
        "warm-cache",
        "smoke"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded grouped-alternation callable replacement workflow."
      ]
    },
    {
      "id": "module-subn-callable-grouped-alternation-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b|c)d",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "callable",
        "subn",
        "module",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded grouped-alternation callable replacement count workflow."
      ]
    },
    {
      "id": "pattern-sub-callable-grouped-alternation-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b|c)d",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "callable",
        "sub",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the same bounded grouped-alternation callable replacement workflow."
      ]
    },
    {
      "id": "pattern-subn-callable-grouped-alternation-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b|c)d",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "callable",
        "subn",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded grouped-alternation callable replacement count workflow."
      ]
    },
    {
      "id": "module-sub-callable-named-grouped-alternation-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b|c)d",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
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
        "callable",
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
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded named grouped-alternation callable replacement workflow."
      ]
    },
    {
      "id": "module-subn-callable-named-grouped-alternation-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b|c)d",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
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
        "callable",
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
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named grouped-alternation callable replacement count workflow."
      ]
    },
    {
      "id": "pattern-sub-callable-named-grouped-alternation-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b|c)d",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
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
        "callable",
        "named-group",
        "sub",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "alternation",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded named grouped-alternation callable replacement workflow."
      ]
    },
    {
      "id": "pattern-subn-callable-named-grouped-alternation-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b|c)d",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
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
        "callable",
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
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named grouped-alternation callable replacement count workflow."
      ]
    },
    {
      "id": "module-sub-callable-nested-grouped-alternation-cold-gap",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a((b|c))d",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "callable",
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
        "callable-replacement"
      ],
      "notes": [
        "Explicit nested-group grouped-alternation callable replacement gap row so broader grouped callback shapes stay visible while nested-group work is still queued."
      ]
    },
    {
      "id": "pattern-subn-callable-named-nested-grouped-alternation-purged-gap",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<outer>(b|c))d",
      "replacement": {
        "type": "callable_match_group",
        "group": "outer",
        "suffix": "x"
      },
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
        "callable",
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
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Explicit named nested-group grouped-alternation callable replacement gap row so broader alternation-and-callback shapes stay visible instead of disappearing until the nested-group follow-ons land."
      ]
    }
  ]
}
