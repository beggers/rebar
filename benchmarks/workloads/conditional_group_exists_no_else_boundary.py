MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-no-else-boundary",
  "spec_refs": [
    "docs/benchmarks/plan.md",
    "docs/spec/drop-in-re-compatibility.md"
  ],
  "notes": [
    "Conditional group-exists no-else boundary workloads keep one optional capture, one conditional site, and tiny haystacks so the scorecard measures helper-call overhead for the newly supported bounded omitted-no-arm conditional slice rather than regex throughput.",
    "Measured rows cover the bounded `a(b)?c(?(1)d)` and `a(?P<word>b)?c(?(word)d)` compile/search/fullmatch plus constant-replacement `sub()`/`subn()` paths through module and compiled-`Pattern` entrypoints, the carry-forward explicit-empty-else search row now also measures real timings, the bounded omitted-no-arm alternation-heavy slice now times module and compiled-`Pattern` helpers across representative first-arm, second-arm, and absent no-match haystacks, the bounded nested omitted-no-arm slice now times module and compiled-`Pattern` helpers across representative capture-present and capture-absent haystacks, and the bounded quantified omitted-no-arm slice now times module and compiled-`Pattern` helpers across representative capture-present and capture-absent haystacks while explicit-empty-else, empty-arm, alternation-heavy repeated, nested quantified, and broader counted conditional variants stay as later follow-ons.",
    "Assertion-conditioned branches remain outside this benchmark manifest because CPython rejects them and the current benchmark harness only publishes timing rows for accepted syntax."
  ],
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "module-compile-numbered-conditional-group-exists-no-else-cold-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(b)?c(?(1)d)",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "cold-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "optional-groups",
        "conditionals"
      ],
      "notes": [
        "Cold module.compile benchmark for the bounded numbered omitted-no-arm conditional slice so compile metadata timing reaches the published benchmark report."
      ]
    },
    {
      "id": "module-search-numbered-conditional-group-exists-no-else-present-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(b)?c(?(1)d)",
      "haystack": "zzabcdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "smoke": True,
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
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
        "conditionals"
      ],
      "notes": [
        "Warm module.search helper path for the bounded numbered omitted-no-arm conditional workflow when the optional capture is present and the yes-arm literal suffix is required."
      ]
    },
    {
      "id": "pattern-fullmatch-numbered-conditional-group-exists-no-else-absent-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(b)?c(?(1)d)",
      "haystack": "ac",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "fullmatch",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the bounded numbered omitted-no-arm conditional workflow when the optional capture is omitted and the pattern terminates at the conditional site."
      ]
    },
    {
      "id": "module-compile-named-conditional-group-exists-no-else-warm-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(?P<word>b)?c(?(word)d)",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "named-group",
        "warm-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups"
      ],
      "notes": [
        "Warm module.compile path for the bounded named omitted-no-arm conditional slice so named metadata timing reaches the benchmark report."
      ]
    },
    {
      "id": "module-search-named-conditional-group-exists-no-else-present-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<word>b)?c(?(word)d)",
      "haystack": "zzabcdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
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
        "conditionals",
        "named-groups"
      ],
      "notes": [
        "Warm module.search helper path for the bounded named omitted-no-arm conditional workflow when the optional named capture is present and the yes-arm literal suffix is required."
      ]
    },
    {
      "id": "pattern-fullmatch-named-conditional-group-exists-no-else-absent-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<word>b)?c(?(word)d)",
      "haystack": "ac",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "smoke": True,
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
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
        "conditionals",
        "named-groups",
        "cache-purge"
      ],
      "notes": [
        "Smoke-sized Pattern.fullmatch probe for the bounded named omitted-no-arm conditional workflow when the optional capture is omitted so named-group None payload timing reaches the benchmark report."
      ]
    },
    {
      "id": "module-search-numbered-conditional-group-exists-explicit-empty-else-cold-gap",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(b)?c(?(1)d|)",
      "haystack": "zzaczz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "explicit-empty-else",
        "search",
        "module",
        "unsupported",
        "cold-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "optional-groups",
        "conditionals"
      ],
      "notes": [
        "Carry-forward explicit-empty-else row so `(?(1)yes|)` and `(?(name)yes|)` stay visible alongside the omitted-no-arm slice after the accepted syntax reaches real benchmark timings."
      ]
    },
    {
      "id": "module-search-numbered-nested-conditional-group-exists-no-else-present-cold-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(b)?c(?(1)(?(1)d))",
      "haystack": "zzabcdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "nested-conditional",
        "search",
        "module",
        "present",
        "cold-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "optional-groups",
        "conditionals"
      ],
      "notes": [
        "Cold module.search helper path for the bounded numbered nested omitted-no-arm conditional workflow when the optional capture is present and both the outer and nested yes-arms require the trailing `d`."
      ]
    },
    {
      "id": "pattern-fullmatch-numbered-nested-conditional-group-exists-no-else-absent-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(b)?c(?(1)(?(1)d))",
      "haystack": "ac",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "nested-conditional",
        "fullmatch",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the bounded numbered nested omitted-no-arm conditional workflow when the optional capture is absent so the outer no-else arm contributes nothing and the nested conditional is skipped."
      ]
    },
    {
      "id": "module-search-named-nested-conditional-group-exists-no-else-present-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d))",
      "haystack": "zzabcdzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "nested-conditional",
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
        "conditionals",
        "named-groups"
      ],
      "notes": [
        "Warm module.search helper path for the bounded named nested omitted-no-arm conditional workflow when the optional named capture is present and both nested yes-arms require the trailing `d`."
      ]
    },
    {
      "id": "pattern-fullmatch-named-nested-conditional-group-exists-no-else-absent-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d))",
      "haystack": "ac",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "nested-conditional",
        "named-group",
        "fullmatch",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the bounded named nested omitted-no-arm conditional workflow when the optional named capture is absent so the outer no-else arm contributes nothing and the nested conditional is skipped."
      ]
    },
    {
      "id": "module-search-numbered-quantified-conditional-group-exists-no-else-present-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(b)?c(?(1)d){2}",
      "haystack": "zzabcddzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "quantified",
        "search",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers"
      ],
      "notes": [
        "Warm module.search helper path for the bounded numbered quantified omitted-no-arm conditional workflow when the optional capture is present and the repeated yes arm must contribute both trailing `d` literals."
      ]
    },
    {
      "id": "pattern-fullmatch-numbered-quantified-conditional-group-exists-no-else-purged-gap",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(b)?c(?(1)d){2}",
      "haystack": "ac",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "quantified",
        "fullmatch",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the bounded numbered quantified omitted-no-arm conditional workflow when the optional capture is absent so both repeated omitted no-else arms contribute nothing and the haystack still succeeds as `ac`."
      ]
    },
    {
      "id": "module-search-named-quantified-conditional-group-exists-no-else-present-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<word>b)?c(?(word)d){2}",
      "haystack": "zzabcddzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "quantified",
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
        "conditionals",
        "quantifiers",
        "named-groups"
      ],
      "notes": [
        "Warm module.search helper path for the bounded named quantified omitted-no-arm conditional workflow when the optional named capture is present and the repeated yes arm still requires the doubled `d` suffix."
      ]
    },
    {
      "id": "pattern-fullmatch-named-quantified-conditional-group-exists-no-else-absent-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<word>b)?c(?(word)d){2}",
      "haystack": "ac",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "quantified",
        "named-group",
        "fullmatch",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "named-groups",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the bounded named quantified omitted-no-arm conditional workflow when the optional named capture is absent so both repeated omitted no-else arms stay zero-width and the haystack still succeeds as `ac`."
      ]
    },
    {
      "id": "module-sub-numbered-conditional-group-exists-no-else-replacement-warm-gap",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d)",
      "haystack": "zzabcd ac zz",
      "replacement": "X",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "replacement",
        "module",
        "unsupported",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals"
      ],
      "notes": [
        "Explicit conditional replacement gap row so omitted-no-arm `sub()` helper behavior stays visible instead of being mistaken for the already-supported search/fullmatch slice."
      ]
    },
    {
      "id": "module-subn-numbered-conditional-group-exists-no-else-replacement-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d)",
      "haystack": "zzaczz",
      "replacement": "X",
      "flags": 0,
      "count": 1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "replacement",
        "subn",
        "module",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded omitted-no-arm conditional replacement count workflow when the optional numbered capture is absent."
      ]
    },
    {
      "id": "pattern-sub-numbered-conditional-group-exists-no-else-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d)",
      "haystack": "zzabcdzz",
      "replacement": "X",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "replacement",
        "sub",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered omitted-no-arm conditional replacement workflow when the yes-arm participates in the matched span."
      ]
    },
    {
      "id": "pattern-subn-numbered-conditional-group-exists-no-else-replacement-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d)",
      "haystack": "zzaczz",
      "replacement": "X",
      "flags": 0,
      "count": 1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "replacement",
        "subn",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded numbered omitted-no-arm conditional replacement count workflow when the optional capture is absent."
      ]
    },
    {
      "id": "module-sub-named-conditional-group-exists-no-else-replacement-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d)",
      "haystack": "zzabcdzz",
      "replacement": "X",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "replacement",
        "named-group",
        "sub",
        "module",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded named omitted-no-arm conditional replacement workflow."
      ]
    },
    {
      "id": "module-subn-named-conditional-group-exists-no-else-replacement-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d)",
      "haystack": "zzaczz",
      "replacement": "X",
      "flags": 0,
      "count": 1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "replacement",
        "named-group",
        "subn",
        "module",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named omitted-no-arm conditional replacement count workflow when the optional capture is absent."
      ]
    },
    {
      "id": "pattern-sub-named-conditional-group-exists-no-else-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d)",
      "haystack": "zzabcdzz",
      "replacement": "X",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "replacement",
        "named-group",
        "sub",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded named omitted-no-arm conditional replacement workflow."
      ]
    },
    {
      "id": "pattern-subn-named-conditional-group-exists-no-else-replacement-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d)",
      "haystack": "zzaczz",
      "replacement": "X",
      "flags": 0,
      "count": 1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "replacement",
        "named-group",
        "subn",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named omitted-no-arm conditional replacement count workflow when the optional capture is absent."
      ]
    },
    {
      "id": "module-search-numbered-conditional-group-exists-no-else-alternation-heavy-warm-gap",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(b)?c(?(1)(de|df))",
      "haystack": "zzabcdfzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "alternation",
        "backtracking-heavy",
        "search",
        "module",
        "warm-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation"
      ],
      "notes": [
        "Warm module.search helper path for the bounded numbered omitted-no-arm alternation workflow when the optional capture is present and the yes arm backtracks to its second literal branch."
      ]
    },
    {
      "id": "module-search-named-conditional-group-exists-no-else-alternation-heavy-present-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<word>b)?c(?(word)(de|df))",
      "haystack": "zzabcdezz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "alternation",
        "backtracking-heavy",
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
        "conditionals",
        "named-groups",
        "alternation"
      ],
      "notes": [
        "Warm module.search helper path for the bounded named omitted-no-arm alternation workflow when the optional named capture is present and the yes arm selects its first literal branch."
      ]
    },
    {
      "id": "pattern-fullmatch-numbered-conditional-group-exists-no-else-alternation-heavy-absent-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(b)?c(?(1)(de|df))",
      "haystack": "acde",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "alternation",
        "backtracking-heavy",
        "fullmatch",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the bounded numbered omitted-no-arm alternation workflow when the optional capture is omitted and a first-arm suffix remains unmatched because no else arm exists."
      ]
    },
    {
      "id": "pattern-fullmatch-named-conditional-group-exists-no-else-alternation-heavy-absent-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<word>b)?c(?(word)(de|df))",
      "haystack": "acdf",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "no-else",
        "alternation",
        "backtracking-heavy",
        "named-group",
        "fullmatch",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the bounded named omitted-no-arm alternation workflow when the optional named capture is omitted and a second-arm suffix remains unmatched because no else arm exists."
      ]
    }
  ]
}
