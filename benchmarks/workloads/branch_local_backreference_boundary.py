MANIFEST = {
  "schema_version": 1,
  "manifest_id": "branch-local-backreference-boundary",
  "spec_refs": [
    "docs/benchmarks/plan.md",
    "docs/spec/drop-in-re-compatibility.md"
  ],
  "notes": [
    "Branch-local backreference boundary workloads keep captures, alternation sites, and haystacks intentionally tiny so the scorecard measures helper-call overhead for the newly supported bounded branch-local reference slice rather than regex throughput.",
    "Measured rows cover the bounded `a((b)|c)\\\\2d`, `a(?P<outer>(?P<inner>b)|c)(?P=inner)d`, `a((b)+|c)\\\\2d`, `a(?P<outer>(?P<inner>b)+|c)(?P=inner)d`, `a((b)|c)\\\\2(?(2)d|e)`, and `a(?P<outer>(?P<inner>b)|c)(?P=inner)(?(inner)d|e)` compile/search/fullmatch paths directly, plus one broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional follow-on for `a((b|c){2,})\\\\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)`, while replacement semantics, nested alternation-plus-backreference shapes, and broader backtracking-heavy grouped combinations stay explicit known-gap rows in adjacent manifests."
  ],
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "module-compile-numbered-branch-local-backreference-cold-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a((b)|c)\\2d",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "alternation",
        "numbered-backreference",
        "branch-local",
        "cold-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "alternation",
        "numbered-backreferences",
        "branch-local-backreferences"
      ],
      "notes": [
        "Cold module.compile benchmark for the bounded numbered branch-local backreference slice so compile metadata timing reaches the published benchmark report."
      ]
    },
    {
      "id": "module-search-numbered-branch-local-backreference-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a((b)|c)\\2d",
      "haystack": "zzabbdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "smoke": True,
      "categories": [
        "grouped",
        "alternation",
        "numbered-backreference",
        "branch-local",
        "search",
        "module",
        "warm-cache",
        "smoke"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "alternation",
        "numbered-backreferences",
        "branch-local-backreferences"
      ],
      "notes": [
        "Warm module.search helper path for the bounded numbered branch-local backreference workflow on a tiny haystack."
      ]
    },
    {
      "id": "pattern-fullmatch-numbered-branch-local-backreference-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a((b)|c)\\2d",
      "haystack": "abbd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "alternation",
        "numbered-backreference",
        "branch-local",
        "fullmatch",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "alternation",
        "numbered-backreferences",
        "branch-local-backreferences",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the same bounded numbered branch-local backreference workflow."
      ]
    },
    {
      "id": "module-compile-named-branch-local-backreference-warm-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(?P<outer>(?P<inner>b)|c)(?P=inner)d",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "alternation",
        "named-group",
        "named-backreference",
        "branch-local",
        "warm-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "alternation",
        "named-groups",
        "named-backreferences",
        "branch-local-backreferences"
      ],
      "notes": [
        "Warm module.compile path for the bounded named branch-local backreference slice so named metadata timing reaches the benchmark report."
      ]
    },
    {
      "id": "module-search-named-branch-local-backreference-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<outer>(?P<inner>b)|c)(?P=inner)d",
      "haystack": "zzabbdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "alternation",
        "named-group",
        "named-backreference",
        "branch-local",
        "search",
        "module",
        "warm-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "alternation",
        "named-groups",
        "named-backreferences",
        "branch-local-backreferences"
      ],
      "notes": [
        "Warm module.search helper path for a tiny named branch-local backreference capture so named runtime workflows produce real timings."
      ]
    },
    {
      "id": "pattern-fullmatch-named-branch-local-backreference-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<outer>(?P<inner>b)|c)(?P=inner)d",
      "haystack": "abbd",
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
        "named-backreference",
        "branch-local",
        "fullmatch",
        "purged-cache",
        "smoke"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "alternation",
        "named-groups",
        "named-backreferences",
        "branch-local-backreferences",
        "cache-purge"
      ],
      "notes": [
        "Smoke-sized Pattern.fullmatch probe for the bounded named branch-local backreference workflow with compile cost kept outside the timed loop."
      ]
    },
    {
      "id": "module-search-numbered-quantified-branch-local-backreference-cold-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a((b)+|c)\\2d",
      "haystack": "zzabbdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "alternation",
        "numbered-backreference",
        "branch-local",
        "quantified",
        "search",
        "module",
        "cold-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "alternation",
        "numbered-backreferences",
        "branch-local-backreferences",
        "quantifiers"
      ],
      "notes": [
        "Cold module.search helper path for the bounded numbered quantified branch-local backreference lower-bound success case so the new Rust-backed slice reaches the published benchmark report without reusing the single-pass workload IDs."
      ]
    },
    {
      "id": "module-compile-numbered-quantified-branch-local-backreference-cold-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a((b)+|c)\\2d",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "alternation",
        "numbered-backreference",
        "branch-local",
        "quantified",
        "cold-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "alternation",
        "numbered-backreferences",
        "branch-local-backreferences",
        "quantifiers"
      ],
      "notes": [
        "Cold module.compile benchmark for the bounded numbered quantified branch-local backreference slice so compile metadata timing lands alongside the new runtime rows."
      ]
    },
    {
      "id": "pattern-fullmatch-numbered-quantified-branch-local-backreference-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a((b)+|c)\\2d",
      "haystack": "abbbd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "alternation",
        "numbered-backreference",
        "branch-local",
        "quantified",
        "fullmatch",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "alternation",
        "numbered-backreferences",
        "branch-local-backreferences",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the bounded numbered quantified branch-local backreference second-iteration success path."
      ]
    },
    {
      "id": "module-compile-named-quantified-branch-local-backreference-warm-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(?P<outer>(?P<inner>b)+|c)(?P=inner)d",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "alternation",
        "named-group",
        "named-backreference",
        "branch-local",
        "quantified",
        "warm-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "alternation",
        "named-groups",
        "named-backreferences",
        "branch-local-backreferences",
        "quantifiers"
      ],
      "notes": [
        "Warm module.compile path for the bounded named quantified branch-local backreference slice so named compile metadata joins the benchmark report."
      ]
    },
    {
      "id": "module-search-named-quantified-branch-local-backreference-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<outer>(?P<inner>b)+|c)(?P=inner)d",
      "haystack": "zzabbdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "alternation",
        "named-group",
        "named-backreference",
        "branch-local",
        "quantified",
        "search",
        "module",
        "warm-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "alternation",
        "named-groups",
        "named-backreferences",
        "branch-local-backreferences",
        "quantifiers"
      ],
      "notes": [
        "Warm module.search helper path for the bounded named quantified branch-local backreference lower-bound success case."
      ]
    },
    {
      "id": "pattern-fullmatch-named-quantified-branch-local-backreference-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<outer>(?P<inner>b)+|c)(?P=inner)d",
      "haystack": "abbbd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "alternation",
        "named-group",
        "named-backreference",
        "branch-local",
        "quantified",
        "fullmatch",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "alternation",
        "named-groups",
        "named-backreferences",
        "branch-local-backreferences",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the bounded named quantified branch-local backreference second-iteration success path."
      ]
    },
    {
      "id": "module-compile-numbered-conditional-branch-local-backreference-cold-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a((b)|c)\\2(?(2)d|e)",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "alternation",
        "numbered-backreference",
        "branch-local",
        "conditional",
        "cold-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "alternation",
        "numbered-backreferences",
        "branch-local-backreferences",
        "conditionals"
      ],
      "notes": [
        "Cold module.compile benchmark for the bounded numbered branch-local backreference plus conditional slice so the newly supported compile metadata path reaches the published report."
      ]
    },
    {
      "id": "module-search-numbered-conditional-branch-local-backreference-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a((b)|c)\\2(?(2)d|e)",
      "haystack": "zzabbdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "alternation",
        "numbered-backreference",
        "branch-local",
        "conditional",
        "search",
        "module",
        "warm-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "alternation",
        "numbered-backreferences",
        "branch-local-backreferences",
        "conditionals"
      ],
      "notes": [
        "Warm module.search helper path for the bounded numbered branch-local backreference plus conditional success case on a tiny haystack."
      ]
    },
    {
      "id": "pattern-fullmatch-numbered-conditional-branch-local-backreference-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a((b)|c)\\2(?(2)d|e)",
      "haystack": "abbd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "alternation",
        "numbered-backreference",
        "branch-local",
        "conditional",
        "fullmatch",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "alternation",
        "numbered-backreferences",
        "branch-local-backreferences",
        "conditionals",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the numbered conditional-plus-branch-local backreference success path."
      ]
    },
    {
      "id": "module-compile-named-conditional-branch-local-backreference-warm-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(?P<outer>(?P<inner>b)|c)(?P=inner)(?(inner)d|e)",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "alternation",
        "named-group",
        "named-backreference",
        "branch-local",
        "conditional",
        "warm-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "alternation",
        "named-groups",
        "named-backreferences",
        "branch-local-backreferences",
        "conditionals"
      ],
      "notes": [
        "Warm module.compile path for the bounded named branch-local backreference plus conditional slice so named compile metadata joins the benchmark report."
      ]
    },
    {
      "id": "module-search-named-conditional-branch-local-backreference-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<outer>(?P<inner>b)|c)(?P=inner)(?(inner)d|e)",
      "haystack": "zzabbdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "alternation",
        "named-group",
        "named-backreference",
        "branch-local",
        "conditional",
        "search",
        "module",
        "warm-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "alternation",
        "named-groups",
        "named-backreferences",
        "branch-local-backreferences",
        "conditionals"
      ],
      "notes": [
        "Warm module.search helper path for the bounded named branch-local backreference plus conditional success case."
      ]
    },
    {
      "id": "pattern-fullmatch-named-conditional-branch-local-backreference-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<outer>(?P<inner>b)|c)(?P=inner)(?(inner)d|e)",
      "haystack": "abbd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "alternation",
        "named-group",
        "named-backreference",
        "branch-local",
        "conditional",
        "fullmatch",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "alternation",
        "named-groups",
        "named-backreferences",
        "branch-local-backreferences",
        "conditionals",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the bounded named conditional-plus-branch-local backreference success path, reusing the existing conditional anchor row now that `RBR-0205` landed parity."
      ]
    },
    {
      "id": "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a((b|c){2,})\\2(?(2)d|e)",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "nested-group",
        "alternation",
        "numbered-backreference",
        "branch-local",
        "conditional",
        "quantified",
        "counted-repeat",
        "open-ended-repeat",
        "broader-range",
        "cold-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "nested-groups",
        "alternation",
        "numbered-backreferences",
        "branch-local-backreferences",
        "quantifiers",
        "counted-repeats",
        "conditionals"
      ],
      "notes": [
        "Cold module.compile benchmark for the broader-range open-ended `{2,}` numbered nested-group alternation branch-local backreference plus conditional slice so shifted-floor compile metadata joins the shared branch-local benchmark report."
      ]
    },
    {
      "id": "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a((b|c){2,})\\2(?(2)d|e)",
      "haystack": "zzabbbdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "nested-group",
        "alternation",
        "numbered-backreference",
        "branch-local",
        "conditional",
        "quantified",
        "counted-repeat",
        "open-ended-repeat",
        "broader-range",
        "search",
        "module",
        "lower-bound",
        "b-branch",
        "warm-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "nested-groups",
        "alternation",
        "numbered-backreferences",
        "branch-local-backreferences",
        "quantifiers",
        "counted-repeats",
        "conditionals"
      ],
      "notes": [
        "Warm module.search helper path for the broader-range open-ended `{2,}` numbered nested-group alternation branch-local backreference plus conditional lower-bound success case on `abbbd`, so the shifted two-repetition floor, final same-branch replay, and trailing conditional yes arm stay on the shared benchmark surface."
      ]
    },
    {
      "id": "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a((b|c){2,})\\2(?(2)d|e)",
      "haystack": "abcbccd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "nested-group",
        "alternation",
        "numbered-backreference",
        "branch-local",
        "conditional",
        "quantified",
        "counted-repeat",
        "open-ended-repeat",
        "broader-range",
        "fullmatch",
        "mixed-branches",
        "final-inner-capture",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "nested-groups",
        "alternation",
        "numbered-backreferences",
        "branch-local-backreferences",
        "quantifiers",
        "counted-repeats",
        "conditionals",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the broader-range open-ended `{2,}` numbered nested-group alternation branch-local backreference plus conditional mixed-branch success path on `abcbccd`, so the final selected `c` branch replay stays observable before the trailing yes arm accepts `d`."
      ]
    },
    {
      "id": "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "nested-group",
        "alternation",
        "named-group",
        "named-backreference",
        "branch-local",
        "conditional",
        "quantified",
        "counted-repeat",
        "open-ended-repeat",
        "broader-range",
        "warm-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "nested-groups",
        "alternation",
        "named-groups",
        "named-backreferences",
        "branch-local-backreferences",
        "quantifiers",
        "counted-repeats",
        "conditionals"
      ],
      "notes": [
        "Warm module.compile path for the broader-range open-ended named `{2,}` nested-group alternation branch-local backreference plus conditional slice so named shifted-floor compile metadata lands beside the new runtime rows."
      ]
    },
    {
      "id": "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
      "haystack": "zzacccdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "nested-group",
        "alternation",
        "named-group",
        "named-backreference",
        "branch-local",
        "conditional",
        "quantified",
        "counted-repeat",
        "open-ended-repeat",
        "broader-range",
        "search",
        "module",
        "lower-bound",
        "c-branch",
        "outer-capture",
        "final-inner-capture",
        "warm-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "nested-groups",
        "alternation",
        "named-groups",
        "named-backreferences",
        "branch-local-backreferences",
        "quantifiers",
        "counted-repeats",
        "conditionals"
      ],
      "notes": [
        "Warm module.search helper path for the broader-range open-ended named `{2,}` nested-group alternation branch-local backreference plus conditional lower-bound `c`-branch success on `acccd`, so the visible `outer` capture and final `inner` branch stay observable through the public module helper."
      ]
    },
    {
      "id": "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
      "haystack": "abbbd",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "nested-group",
        "alternation",
        "named-group",
        "named-backreference",
        "branch-local",
        "conditional",
        "quantified",
        "counted-repeat",
        "open-ended-repeat",
        "broader-range",
        "fullmatch",
        "lower-bound",
        "b-branch",
        "outer-capture",
        "final-inner-capture",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "nested-groups",
        "alternation",
        "named-groups",
        "named-backreferences",
        "branch-local-backreferences",
        "quantifiers",
        "counted-repeats",
        "conditionals",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the broader-range open-ended named `{2,}` nested-group alternation branch-local backreference plus conditional lower-bound `b`-branch success path on `abbbd`, so the visible `outer` capture and final selected `inner` branch stay explicit at the shifted two-repetition floor."
      ]
    }
  ]
}
