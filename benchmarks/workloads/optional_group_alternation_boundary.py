MANIFEST = {
  "schema_version": 1,
  "manifest_id": "optional-group-alternation-boundary",
  "spec_refs": [
    "docs/benchmarks/plan.md",
    "docs/spec/drop-in-re-compatibility.md"
  ],
  "notes": [
    "Optional-group alternation boundary workloads keep captures, one literal alternation site, and haystacks intentionally tiny so the scorecard measures helper-call overhead for the newly supported bounded optional-group alternation slices rather than regex throughput.",
    "Measured rows cover the bounded `a(b|c)?d`, `a(?P<word>b|c)?d`, `a((b|c)\\2)?d`, and `a(?P<outer>(?P<inner>b|c)(?P=inner))?d` compile/search/fullmatch paths directly, while broader counted quantified alternation, quantified alternation with inner branch-local backreferences, and broader backtracking-heavy grouped shapes stay as explicit known-gap rows until later counted-repeat follow-ons land."
  ],
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "module-compile-numbered-optional-group-alternation-cold-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(b|c)?d",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "optional-group",
        "quantifier",
        "alternation",
        "cold-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "optional-groups",
        "quantifiers",
        "alternation"
      ],
      "notes": [
        "Cold module.compile benchmark for the bounded numbered optional-group alternation slice so compile metadata timing reaches the published benchmark report."
      ]
    },
    {
      "id": "module-search-numbered-optional-group-alternation-c-branch-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(b|c)?d",
      "haystack": "zzacdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "smoke": True,
      "categories": [
        "grouped",
        "optional-group",
        "quantifier",
        "alternation",
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
        "quantifiers",
        "alternation"
      ],
      "notes": [
        "Warm module.search helper path for the bounded numbered optional-group alternation workflow when the optional capture is present and the alternation selects the c branch."
      ]
    },
    {
      "id": "pattern-fullmatch-numbered-optional-group-alternation-absent-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(b|c)?d",
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
        "alternation",
        "fullmatch",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "optional-groups",
        "quantifiers",
        "alternation",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the same bounded numbered optional-group alternation workflow when the capture is omitted."
      ]
    },
    {
      "id": "module-compile-named-optional-group-alternation-warm-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(?P<word>b|c)?d",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "optional-group",
        "quantifier",
        "alternation",
        "named-group",
        "warm-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "optional-groups",
        "quantifiers",
        "alternation",
        "named-groups"
      ],
      "notes": [
        "Warm module.compile path for the bounded named optional-group alternation slice so named metadata timing reaches the benchmark report."
      ]
    },
    {
      "id": "module-search-named-optional-group-alternation-b-branch-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<word>b|c)?d",
      "haystack": "zzabdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "quantifier",
        "alternation",
        "named-group",
        "search",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "optional-groups",
        "quantifiers",
        "alternation",
        "named-groups"
      ],
      "notes": [
        "Warm module.search helper path for the bounded named optional-group alternation workflow when the optional capture is present and the alternation selects the b branch."
      ]
    },
    {
      "id": "pattern-fullmatch-named-optional-group-alternation-absent-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<word>b|c)?d",
      "haystack": "ad",
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
        "alternation",
        "named-group",
        "fullmatch",
        "absent",
        "purged-cache",
        "smoke"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "optional-groups",
        "quantifiers",
        "alternation",
        "named-groups",
        "cache-purge"
      ],
      "notes": [
        "Smoke-sized Pattern.fullmatch probe for the bounded named optional-group alternation workflow when the capture is omitted so named-group None payload timing reaches the benchmark report."
      ]
    },
    {
      "id": "module-compile-numbered-optional-group-alternation-branch-backref-cold-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a((b|c)\\2)?d",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "optional-group",
        "quantifier",
        "alternation",
        "numbered-backreference",
        "branch-local",
        "cold-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "optional-groups",
        "quantifiers",
        "alternation",
        "numbered-backreferences",
        "branch-local-backreferences"
      ],
      "notes": [
        "Cold module.compile benchmark for the bounded numbered optional-group alternation branch-local backreference slice so compile metadata timing reaches the published benchmark report."
      ]
    },
    {
      "id": "module-search-numbered-optional-group-alternation-branch-backref-b-branch-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a((b|c)\\2)?d",
      "haystack": "zzabbdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "quantifier",
        "alternation",
        "numbered-backreference",
        "branch-local",
        "search",
        "module",
        "present",
        "b-branch",
        "warm-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "optional-groups",
        "quantifiers",
        "alternation",
        "numbered-backreferences",
        "branch-local-backreferences"
      ],
      "notes": [
        "Warm module.search helper path for the bounded numbered optional-group alternation branch-local backreference workflow when the optional group is present and the alternation selects the b branch."
      ]
    },
    {
      "id": "pattern-fullmatch-numbered-optional-group-alternation-branch-backref-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a((b|c)\\2)?d",
      "haystack": "abbd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "quantifier",
        "alternation",
        "numbered-backreference",
        "branch-local-backreference",
        "fullmatch",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "optional-groups",
        "quantifiers",
        "alternation",
        "numbered-backreferences",
        "branch-local-backreferences",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the bounded numbered optional-group alternation branch-local backreference workflow when the optional group is present and the alternation selects the b branch."
      ]
    },
    {
      "id": "module-compile-named-optional-group-alternation-branch-backref-warm-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(?P<outer>(?P<inner>b|c)(?P=inner))?d",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "optional-group",
        "quantifier",
        "alternation",
        "named-group",
        "named-backreference",
        "branch-local",
        "warm-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "optional-groups",
        "quantifiers",
        "alternation",
        "named-groups",
        "named-backreferences",
        "branch-local-backreferences"
      ],
      "notes": [
        "Warm module.compile path for the bounded named optional-group alternation branch-local backreference slice so named metadata timing reaches the benchmark report."
      ]
    },
    {
      "id": "module-search-named-optional-group-alternation-branch-backref-c-branch-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<outer>(?P<inner>b|c)(?P=inner))?d",
      "haystack": "zzaccdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "quantifier",
        "alternation",
        "named-group",
        "named-backreference",
        "branch-local",
        "search",
        "module",
        "present",
        "c-branch",
        "warm-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "optional-groups",
        "quantifiers",
        "alternation",
        "named-groups",
        "named-backreferences",
        "branch-local-backreferences"
      ],
      "notes": [
        "Warm module.search helper path for the bounded named optional-group alternation branch-local backreference workflow when the optional group is present and the alternation selects the c branch."
      ]
    },
    {
      "id": "pattern-fullmatch-named-optional-group-alternation-branch-backref-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<outer>(?P<inner>b|c)(?P=inner))?d",
      "haystack": "abbd",
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
        "alternation",
        "named-group",
        "named-backreference",
        "branch-local",
        "fullmatch",
        "purged-cache",
        "smoke"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "optional-groups",
        "quantifiers",
        "alternation",
        "named-groups",
        "named-backreferences",
        "branch-local-backreferences",
        "cache-purge"
      ],
      "notes": [
        "Smoke-sized Pattern.fullmatch probe for the bounded named optional-group alternation branch-local backreference workflow when the optional group is present and the alternation selects the b branch."
      ]
    },
    {
      "id": "module-search-numbered-broader-range-alternation-cold-gap",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(b|c){1,3}d",
      "haystack": "zzabccdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "quantifier",
        "alternation",
        "counted-repeat",
        "wider-range",
        "search",
        "module",
        "unsupported",
        "cold-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "quantifiers",
        "alternation",
        "counted-repeats"
      ],
      "notes": [
        "Explicit broader-range quantified-alternation gap row so counted alternation beyond the bounded `{1,2}` frontier stays visible now that the optional-group alternation slice has real timings."
      ]
    }
  ]
}
