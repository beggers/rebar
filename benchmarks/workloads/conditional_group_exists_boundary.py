MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-boundary",
  "spec_refs": [
    "docs/benchmarks/plan.md",
    "docs/spec/drop-in-re-compatibility.md"
  ],
  "notes": [
    "Conditional group-exists boundary workloads keep one optional capture, one conditional site, and tiny haystacks so the scorecard measures helper-call overhead for the newly supported bounded two-arm conditional slice rather than regex throughput.",
    "Measured rows cover the bounded `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)` compile/search/fullmatch plus constant-replacement `sub()`/`subn()` paths through module and compiled-`Pattern` entrypoints, the numbered and named callable-replacement `sub()`/`subn()` paths through module and compiled-`Pattern` entrypoints via the existing `callable_match_group` helper for both `str` and bytes pattern-text-model workloads including the bounded `str` and bytes `count=-1` no-substitution companions on `abcdaceabcd` and the absent-capture `TypeError` companions on `zzacezz` with `count=1`, the numbered and named replacement-template `sub()`/`subn()` paths through module and compiled-`Pattern` entrypoints via `\\1x` and `\\g<word>x` for both `str` and bytes pattern-text-model workloads plus the bounded `str` and bytes `count=-1` no-substitution companions on `abcdaceabcd`, the bounded alternation-heavy replacement `a(b)?c(?(1)(de|df)|(eg|eh))` / `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))` `sub()`/`subn()` paths through module and compiled-`Pattern` entrypoints, the matching bounded alternation-heavy callable `sub()`/`subn()` probes for both `str` and bytes including the exact `count=-1` no-substitution companions on `zzabcdezz` and `zzacehzz`, the bounded nested two-arm `a(b)?c(?(1)(?(1)d|e)|f)` / `a(?P<word>b)?c(?(word)(?(word)d|e)|f)` module-search, Pattern.fullmatch, constant-replacement `sub()`/`subn()`, and `str` plus bytes callable-replacement `sub()`/`subn()` probes through module and compiled-`Pattern` entrypoints including the absent-capture `TypeError` companions on `zzacfzz` with `count=1`, the bounded no-match companions on `zzabcezz` and `zzacezz`, and the bounded `str` and bytes `count=-1` callable no-substitution companions on `zzabcdzz` and `zzacfzz`, one bounded quantified `{2}` Pattern.fullmatch companion for each numbered and named spelling, the bounded quantified two-arm replacement `a(b)?c(?(1)d|e){2}` / `a(?P<word>b)?c(?(word)d|e){2}` `sub()`/`subn()` paths through module and compiled-`Pattern` entrypoints, the bounded quantified `str` and bytes callable-replacement `sub()`/`subn()` probes for that same numbered and named pair including the bounded `count=-1` short-circuit companions on `zzabcddzz` and `zzaceezz`, the bounded no-match companions on `zzabcdezz` and `zzacedzz`, and the matching quantified `count=-1` no-match short-circuits on those same near-miss haystacks, and the bounded quantified alternation-heavy `a(b)?c(?(1)(de|df)|(eg|eh)){2}` / `a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}` module-search, Pattern.fullmatch, and constant-replacement `sub()`/`subn()` probes through module and compiled-`Pattern` entrypoints, while deeper nested replacement-conditioned shapes, branch-local-backreference-conditioned flows, and broader backtracking-heavy conditional shapes stay follow-on benchmark expansion or later slices instead of being silently omitted here."
  ],
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "module-compile-numbered-conditional-group-exists-cold-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(b)?c(?(1)d|e)",
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
        "cold-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "optional-groups",
        "conditionals"
      ],
      "notes": [
        "Cold module.compile benchmark for the bounded numbered conditional group-exists slice so compile metadata timing reaches the published benchmark report."
      ]
    },
    {
      "id": "module-search-numbered-conditional-group-exists-present-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(b)?c(?(1)d|e)",
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
        "Warm module.search helper path for the bounded numbered conditional workflow when the optional capture is present and the yes-arm literal suffix is selected."
      ]
    },
    {
      "id": "pattern-fullmatch-numbered-conditional-group-exists-absent-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "ace",
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
        "Purged-cache Pattern.fullmatch probe for the same bounded numbered conditional workflow when the optional capture is omitted and the no-arm literal suffix is selected."
      ]
    },
    {
      "id": "module-compile-named-conditional-group-exists-warm-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
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
        "Warm module.compile path for the bounded named conditional group-exists slice so named metadata timing reaches the benchmark report."
      ]
    },
    {
      "id": "module-search-named-conditional-group-exists-present-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
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
        "Warm module.search helper path for the bounded named conditional workflow when the optional named capture is present and the yes-arm literal suffix is selected."
      ]
    },
    {
      "id": "pattern-fullmatch-named-conditional-group-exists-absent-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "ace",
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
        "Smoke-sized Pattern.fullmatch probe for the bounded named conditional workflow when the optional capture is omitted so named-group None payload timing reaches the benchmark report."
      ]
    },
    {
      "id": "module-sub-numbered-conditional-group-exists-replacement-warm-gap",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e)",
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
        "replacement",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered two-arm conditional replacement workflow when the optional capture is present and the yes-arm literal `d` participates in the matched span."
      ]
    },
    {
      "id": "module-subn-numbered-conditional-group-exists-replacement-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzacezz",
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
        "replacement",
        "subn",
        "module",
        "absent",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded numbered two-arm conditional replacement count workflow when the optional capture is absent and the else-arm literal `e` participates in the matched span."
      ]
    },
    {
      "id": "pattern-sub-numbered-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e)",
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
        "replacement",
        "sub",
        "present",
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
        "Purged-cache Pattern.sub helper path for the bounded numbered two-arm conditional replacement workflow when the optional capture is present and the matched span ends with `d`."
      ]
    },
    {
      "id": "pattern-subn-numbered-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzacezz",
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
        "replacement",
        "subn",
        "absent",
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
        "Purged-cache Pattern.subn helper path for the bounded numbered two-arm conditional replacement count workflow when the optional capture is absent and the matched span instead ends with `e`."
      ]
    },
    {
      "id": "module-sub-named-conditional-group-exists-replacement-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
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
        "replacement",
        "named-group",
        "sub",
        "module",
        "present",
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
        "Warm module.sub helper path for the bounded named two-arm conditional replacement workflow when the optional named capture is present."
      ]
    },
    {
      "id": "module-subn-named-conditional-group-exists-replacement-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzacezz",
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
        "replacement",
        "named-group",
        "subn",
        "module",
        "absent",
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
        "Warm module.subn helper path for the bounded named two-arm conditional replacement count workflow when the optional named capture is absent and the else arm contributes `e`."
      ]
    },
    {
      "id": "pattern-sub-named-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
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
        "replacement",
        "named-group",
        "sub",
        "present",
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
        "Purged-cache Pattern.sub helper path for the bounded named two-arm conditional replacement workflow when the optional named capture is present."
      ]
    },
    {
      "id": "pattern-subn-named-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzacezz",
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
        "replacement",
        "named-group",
        "subn",
        "absent",
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
        "Purged-cache Pattern.subn helper path for the bounded named two-arm conditional replacement count workflow when the optional named capture is absent."
      ]
    },
    {
      "id": "module-sub-template-numbered-conditional-group-exists-replacement-warm-gap",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzabcdzz",
      "replacement": "\\1x",
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
        "replacement",
        "template",
        "numbered-group",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "replacement-template"
      ],
      "notes": [
        "This former replacement-template gap anchor now benchmarks the bounded numbered `module.sub()` present-capture workflow on `zzabcdzz`, so `\\1x` expands the captured `b` after the conditional yes-arm `d` closes the match alongside the complementary named module and numbered compiled-`Pattern` template companions."
      ]
    },
    {
      "id": "module-subn-template-numbered-conditional-group-exists-replacement-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzacezz",
      "replacement": "\\1x",
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
        "replacement",
        "template",
        "numbered-group",
        "subn",
        "module",
        "absent",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "replacement-template"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded numbered two-arm conditional replacement-template count workflow when the optional capture is absent, so the empty `\\1` expansion still leaves the literal `x` visible."
      ]
    },
    {
      "id": "pattern-sub-template-numbered-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzabcdzz",
      "replacement": "\\1x",
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
        "replacement",
        "template",
        "numbered-group",
        "sub",
        "present",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered two-arm conditional replacement-template workflow when the optional capture is present and `\\1x` expands to `bx`."
      ]
    },
    {
      "id": "pattern-subn-template-numbered-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzacezz",
      "replacement": "\\1x",
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
        "replacement",
        "template",
        "numbered-group",
        "subn",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded numbered two-arm conditional replacement-template count workflow when the optional capture is absent, so the empty `\\1` expansion still leaves the literal `x` visible."
      ]
    },
    {
      "id": "module-sub-template-numbered-conditional-group-exists-replacement-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzabcdzz",
      "replacement": "\\1x",
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "template",
        "numbered-group",
        "sub",
        "module",
        "present",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "replacement-template"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered two-arm conditional replacement-template workflow when the optional capture is present, so `\\1x` expands the captured `b` after the conditional yes-arm `d` closes the match on the bytes path."
      ]
    },
    {
      "id": "module-subn-template-numbered-conditional-group-exists-replacement-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzacezz",
      "replacement": "\\1x",
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "template",
        "numbered-group",
        "subn",
        "module",
        "absent",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "replacement-template"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded numbered two-arm conditional replacement-template count workflow when the optional capture is absent, so the empty `\\1` expansion still leaves the literal `x` visible on the bytes path."
      ]
    },
    {
      "id": "pattern-sub-template-numbered-conditional-group-exists-replacement-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzabcdzz",
      "replacement": "\\1x",
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "template",
        "numbered-group",
        "sub",
        "present",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered two-arm conditional replacement-template workflow when the optional capture is present and `\\1x` expands to `bx`."
      ]
    },
    {
      "id": "pattern-subn-template-numbered-conditional-group-exists-replacement-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzacezz",
      "replacement": "\\1x",
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "template",
        "numbered-group",
        "subn",
        "absent",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded numbered two-arm conditional replacement-template count workflow when the optional capture is absent, so the empty `\\1` expansion still leaves the literal `x` visible."
      ]
    },
    {
      "id": "module-sub-template-named-conditional-group-exists-replacement-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzabcdzz",
      "replacement": "\\g<word>x",
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
        "replacement",
        "template",
        "named-group",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "replacement-template"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded named two-arm conditional replacement-template workflow when the optional named capture is present and `\\g<word>x` expands to `bx`."
      ]
    },
    {
      "id": "module-subn-template-named-conditional-group-exists-replacement-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzacezz",
      "replacement": "\\g<word>x",
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
        "replacement",
        "template",
        "named-group",
        "subn",
        "module",
        "absent",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "replacement-template"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named two-arm conditional replacement-template count workflow when the optional named capture is absent, so the empty `\\g<word>` expansion still leaves the literal `x` visible."
      ]
    },
    {
      "id": "pattern-sub-template-named-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzabcdzz",
      "replacement": "\\g<word>x",
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
        "replacement",
        "template",
        "named-group",
        "sub",
        "present",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded named two-arm conditional replacement-template workflow when the optional named capture is present and `\\g<word>x` expands to `bx`."
      ]
    },
    {
      "id": "pattern-subn-template-named-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzacezz",
      "replacement": "\\g<word>x",
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
        "replacement",
        "template",
        "named-group",
        "subn",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named two-arm conditional replacement-template count workflow when the optional named capture is absent, so the empty `\\g<word>` expansion still leaves the literal `x` visible."
      ]
    },
    {
      "id": "module-sub-template-named-conditional-group-exists-replacement-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzabcdzz",
      "replacement": "\\g<word>x",
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "template",
        "named-group",
        "sub",
        "module",
        "present",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "replacement-template"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded named two-arm conditional replacement-template workflow when the optional named capture is present and `\\g<word>x` expands to `bx`."
      ]
    },
    {
      "id": "module-subn-template-named-conditional-group-exists-replacement-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzacezz",
      "replacement": "\\g<word>x",
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "template",
        "named-group",
        "subn",
        "module",
        "absent",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "replacement-template"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named two-arm conditional replacement-template count workflow when the optional named capture is absent, so the empty `\\g<word>` expansion still leaves the literal `x` visible."
      ]
    },
    {
      "id": "pattern-sub-template-named-conditional-group-exists-replacement-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzabcdzz",
      "replacement": "\\g<word>x",
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "template",
        "named-group",
        "sub",
        "present",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded named two-arm conditional replacement-template workflow when the optional named capture is present and `\\g<word>x` expands to `bx`."
      ]
    },
    {
      "id": "pattern-subn-template-named-conditional-group-exists-replacement-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzacezz",
      "replacement": "\\g<word>x",
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "template",
        "named-group",
        "subn",
        "absent",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named two-arm conditional replacement-template count workflow when the optional named capture is absent, so the empty `\\g<word>` expansion still leaves the literal `x` visible."
      ]
    },
    {
      "id": "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": "\\1x",
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "template",
        "numbered-group",
        "sub",
        "module",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "replacement-template"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered two-arm conditional replacement-template negative-count workflow, keeping CPython's exact `count=-1` no-substitution outcome explicit on `abcdaceabcd`."
      ]
    },
    {
      "id": "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": "\\g<word>x",
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "template",
        "named-group",
        "subn",
        "module",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "replacement-template"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named two-arm conditional replacement-template negative-count workflow, keeping the exact `count=-1` zero-replacement tuple outcome explicit on `abcdaceabcd`."
      ]
    },
    {
      "id": "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": "\\1x",
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "template",
        "numbered-group",
        "sub",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered two-arm conditional replacement-template negative-count workflow, keeping the same `count=-1` no-substitution outcome explicit on the compiled entrypoint."
      ]
    },
    {
      "id": "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": "\\g<word>x",
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "template",
        "named-group",
        "subn",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named two-arm conditional replacement-template negative-count workflow, keeping the same `count=-1` zero-replacement tuple outcome explicit on the compiled entrypoint."
      ]
    },
    {
      "id": "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": "\\1x",
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "template",
        "numbered-group",
        "sub",
        "module",
        "bytes",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "replacement-template"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered two-arm conditional replacement-template negative-count workflow, keeping CPython's exact `count=-1` no-substitution outcome explicit on `abcdaceabcd`."
      ]
    },
    {
      "id": "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": "\\g<word>x",
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "template",
        "named-group",
        "subn",
        "module",
        "bytes",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "replacement-template"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named two-arm conditional replacement-template negative-count workflow, keeping the exact `count=-1` zero-replacement tuple outcome explicit on `abcdaceabcd`."
      ]
    },
    {
      "id": "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": "\\1x",
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "template",
        "numbered-group",
        "sub",
        "bytes",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered two-arm conditional replacement-template negative-count workflow, keeping the same `count=-1` no-substitution outcome explicit on the compiled entrypoint."
      ]
    },
    {
      "id": "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": "\\g<word>x",
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "template",
        "named-group",
        "subn",
        "bytes",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "replacement-template",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named two-arm conditional replacement-template negative-count workflow, keeping the same `count=-1` zero-replacement tuple outcome explicit on the compiled entrypoint."
      ]
    },
    {
      "id": "module-sub-callable-numbered-conditional-group-exists-replacement-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
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
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered two-arm conditional callable replacement workflow when the optional capture is present and the callback reads `match.group(1)` after the yes-arm `d` extends the matched span."
      ]
    },
    {
      "id": "module-sub-callable-numbered-conditional-group-exists-replacement-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered two-arm conditional callable replacement workflow when the optional capture is present and the callback reads `match.group(1)` after the yes-arm `d` extends the matched span."
      ]
    },
    {
      "id": "module-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzabcdacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
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
        "replacement",
        "callable",
        "subn",
        "module",
        "first-match-only",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded numbered two-arm conditional callable replacement first-match-only companion on `zzabcdacezz`, so the leading present-capture match is measured while the later absent-capture match stays untouched under `count=1`."
      ]
    },
    {
      "id": "module-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzabcdacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "subn",
        "module",
        "first-match-only",
        "count",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded numbered two-arm conditional callable replacement first-match-only companion on `zzabcdacezz`, so the leading present-capture match is measured while the later absent-capture match stays untouched under `count=1`."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
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
        "replacement",
        "callable",
        "sub",
        "present",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered two-arm conditional callable replacement workflow when the optional capture is present and the callback reads `match.group(1)` after the yes-arm `d` extends the matched span."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-conditional-group-exists-replacement-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "sub",
        "present",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered two-arm conditional callable replacement workflow when the optional capture is present and the callback reads `match.group(1)` after the yes-arm `d` extends the matched span."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzabcdacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
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
        "replacement",
        "callable",
        "subn",
        "first-match-only",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded numbered two-arm conditional callable replacement first-match-only companion on `zzabcdacezz`, so the leading present-capture callback is measured while the later absent-capture match stays untouched under `count=1`."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzabcdacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "subn",
        "first-match-only",
        "count",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded numbered two-arm conditional callable replacement first-match-only companion on `zzabcdacezz`, so the leading present-capture callback is measured while the later absent-capture match stays untouched under `count=1`."
      ]
    },
    {
      "id": "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "sub",
        "module",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered two-arm conditional callable replacement negative-count workflow, keeping CPython's exact `count=-1` no-substitution and no-callback outcome explicit on `abcdaceabcd`."
      ]
    },
    {
      "id": "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "sub",
        "module",
        "negative-count",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered two-arm conditional callable replacement negative-count workflow, keeping CPython's exact `count=-1` no-substitution and no-callback outcome explicit on `abcdaceabcd`."
      ]
    },
    {
      "id": "module-sub-callable-named-conditional-group-exists-replacement-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
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
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded named two-arm conditional callable replacement workflow when the optional named capture is present and the callback reads `match.group(\"word\")` after the yes-arm `d` extends the matched span."
      ]
    },
    {
      "id": "module-sub-callable-named-conditional-group-exists-replacement-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded named two-arm conditional callable replacement workflow when the optional named capture is present and the callback reads `match.group(\"word\")` after the yes-arm `d` extends the matched span."
      ]
    },
    {
      "id": "module-subn-callable-named-conditional-group-exists-replacement-first-match-only-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzabcdacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
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
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "first-match-only",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named two-arm conditional callable replacement first-match-only companion on `zzabcdacezz`, so the leading present-capture callback is measured while the later absent-capture match stays untouched under `count=1`."
      ]
    },
    {
      "id": "module-subn-callable-named-conditional-group-exists-replacement-first-match-only-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzabcdacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "first-match-only",
        "count",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named two-arm conditional callable replacement first-match-only companion on `zzabcdacezz`, so the leading present-capture callback is measured while the later absent-capture match stays untouched under `count=1`."
      ]
    },
    {
      "id": "pattern-sub-callable-named-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
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
        "replacement",
        "callable",
        "named-group",
        "sub",
        "present",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded named two-arm conditional callable replacement workflow when the optional named capture is present and the callback reads `match.group(\"word\")`."
      ]
    },
    {
      "id": "pattern-sub-callable-named-conditional-group-exists-replacement-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "present",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded named two-arm conditional callable replacement workflow when the optional named capture is present and the callback reads `match.group(\"word\")`."
      ]
    },
    {
      "id": "pattern-subn-callable-named-conditional-group-exists-replacement-purged-gap",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzabcdacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
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
        "replacement",
        "callable",
        "named-group",
        "subn",
        "first-match-only",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "This former named compiled-entrypoint callable gap anchor now benchmarks the bounded first-match-only companion on `zzabcdacezz`, so the leading present-capture callback is measured while the later absent-capture match stays untouched under `count=1`."
      ]
    },
    {
      "id": "pattern-subn-callable-named-conditional-group-exists-replacement-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzabcdacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "first-match-only",
        "count",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named two-arm conditional callable replacement first-match-only companion on `zzabcdacezz`, so the leading present-capture callback is measured while the later absent-capture match stays untouched under `count=1`."
      ]
    },
    {
      "id": "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named two-arm conditional callable replacement negative-count workflow, keeping the exact `count=-1` zero-replacement tuple outcome explicit on `abcdaceabcd` without invoking the callback."
      ]
    },
    {
      "id": "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "negative-count",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named two-arm conditional callable replacement negative-count workflow, keeping the exact `count=-1` zero-replacement tuple outcome explicit on `abcdaceabcd` without invoking the callback."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "sub",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered two-arm conditional callable replacement negative-count workflow, keeping the same `count=-1` no-substitution outcome explicit on the compiled entrypoint."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "sub",
        "negative-count",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered two-arm conditional callable replacement negative-count workflow, keeping the same `count=-1` no-substitution outcome explicit on the compiled entrypoint."
      ]
    },
    {
      "id": "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named two-arm conditional callable replacement negative-count workflow, keeping the same `count=-1` zero-replacement tuple outcome explicit on the compiled entrypoint too."
      ]
    },
    {
      "id": "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "negative-count",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named two-arm conditional callable replacement negative-count workflow, keeping the same `count=-1` zero-replacement tuple outcome explicit on the compiled entrypoint too."
      ]
    },
    {
      "id": "module-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
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
        "replacement",
        "callable",
        "subn",
        "module",
        "absent",
        "count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded numbered two-arm conditional callable replacement absent-capture companion on `zzacezz`, keeping `callable_match_group` pinned to `match.group(1)` so the first bounded `TypeError` stays the thing being timed."
      ]
    },
    {
      "id": "module-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "subn",
        "module",
        "absent",
        "count",
        "exception",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded numbered two-arm conditional callable replacement absent-capture companion on `zzacezz`, keeping `callable_match_group` pinned to `match.group(1)` so the first bounded `TypeError` stays the thing being timed."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
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
        "replacement",
        "callable",
        "subn",
        "absent",
        "count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded numbered two-arm conditional callable replacement absent-capture companion on `zzacezz`, keeping `callable_match_group` pinned to `match.group(1)` so the compiled-entrypoint `TypeError` remains explicit too."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "subn",
        "absent",
        "count",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded numbered two-arm conditional callable replacement absent-capture companion on `zzacezz`, keeping `callable_match_group` pinned to `match.group(1)` so the compiled-entrypoint `TypeError` remains explicit too."
      ]
    },
    {
      "id": "module-subn-callable-named-conditional-group-exists-replacement-absent-exception-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
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
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named two-arm conditional callable replacement absent-capture companion on `zzacezz`, keeping `callable_match_group` pinned to `match.group(\"word\")` so the named `TypeError` remains the timed outcome."
      ]
    },
    {
      "id": "module-subn-callable-named-conditional-group-exists-replacement-absent-exception-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "count",
        "exception",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named two-arm conditional callable replacement absent-capture companion on `zzacezz`, keeping `callable_match_group` pinned to `match.group(\"word\")` so the named `TypeError` remains the timed outcome."
      ]
    },
    {
      "id": "pattern-subn-callable-named-conditional-group-exists-replacement-absent-exception-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
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
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named two-arm conditional callable replacement absent-capture companion on `zzacezz`, keeping `callable_match_group` pinned to `match.group(\"word\")` so the smallest compiled conditional callable `TypeError` is measured too."
      ]
    },
    {
      "id": "pattern-subn-callable-named-conditional-group-exists-replacement-absent-exception-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "count",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named two-arm conditional callable replacement absent-capture companion on `zzacezz`, keeping `callable_match_group` pinned to `match.group(\"word\")` so the smallest compiled conditional callable `TypeError` is measured too."
      ]
    },
    {
      "id": "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "count",
        "none-count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered two-arm conditional callable replacement present-capture `count=None` contract, keeping CPython's `TypeError` explicit before the callback can read `match.group(1)`."
      ]
    },
    {
      "id": "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "count",
        "none-count",
        "exception",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered two-arm conditional callable replacement present-capture `count=None` contract, keeping CPython's `TypeError` explicit before the callback can read `match.group(1)`."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "sub",
        "present",
        "count",
        "none-count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered two-arm conditional callable replacement present-capture `count=None` contract on the compiled entrypoint."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "sub",
        "present",
        "count",
        "none-count",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered two-arm conditional callable replacement present-capture `count=None` contract on the compiled entrypoint."
      ]
    },
    {
      "id": "module-sub-callable-named-conditional-group-exists-replacement-none-count-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "count",
        "none-count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded named two-arm conditional callable replacement present-capture `count=None` contract, keeping the callback pinned to `match.group(\"word\")` while CPython raises `TypeError` first."
      ]
    },
    {
      "id": "module-sub-callable-named-conditional-group-exists-replacement-none-count-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "count",
        "none-count",
        "exception",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded named two-arm conditional callable replacement present-capture `count=None` contract, keeping the callback pinned to `match.group(\"word\")` while CPython raises `TypeError` first."
      ]
    },
    {
      "id": "pattern-sub-callable-named-conditional-group-exists-replacement-none-count-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "present",
        "count",
        "none-count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded named two-arm conditional callable replacement present-capture `count=None` contract on the compiled entrypoint."
      ]
    },
    {
      "id": "pattern-sub-callable-named-conditional-group-exists-replacement-none-count-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "present",
        "count",
        "none-count",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded named two-arm conditional callable replacement present-capture `count=None` contract on the compiled entrypoint."
      ]
    },
    {
      "id": "module-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "subn",
        "module",
        "absent",
        "count",
        "none-count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded numbered two-arm conditional callable replacement absent-capture `count=None` contract on `zzacezz`."
      ]
    },
    {
      "id": "module-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "subn",
        "module",
        "absent",
        "count",
        "none-count",
        "exception",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded numbered two-arm conditional callable replacement absent-capture `count=None` contract on `zzacezz`."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "subn",
        "absent",
        "count",
        "none-count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded numbered two-arm conditional callable replacement absent-capture `count=None` contract on the compiled entrypoint."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "subn",
        "absent",
        "count",
        "none-count",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded numbered two-arm conditional callable replacement absent-capture `count=None` contract on the compiled entrypoint."
      ]
    },
    {
      "id": "module-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "count",
        "none-count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named two-arm conditional callable replacement absent-capture `count=None` contract on `zzacezz`."
      ]
    },
    {
      "id": "module-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "count",
        "none-count",
        "exception",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named two-arm conditional callable replacement absent-capture `count=None` contract on `zzacezz`."
      ]
    },
    {
      "id": "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "count",
        "none-count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named two-arm conditional callable replacement absent-capture `count=None` contract on the compiled entrypoint."
      ]
    },
    {
      "id": "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "count",
        "none-count",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named two-arm conditional callable replacement absent-capture `count=None` contract on the compiled entrypoint."
      ]
    },
    {
      "id": "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "sub",
        "module",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered two-arm conditional callable replacement `count=None` follow-on on `abcdaceabcd`, keeping the invalid-count `TypeError` explicit on the same haystack as the adjacent `count=-1` row."
      ]
    },
    {
      "id": "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "sub",
        "module",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered two-arm conditional callable replacement `count=None` follow-on on `abcdaceabcd`, keeping the invalid-count `TypeError` explicit on the same haystack as the adjacent `count=-1` row."
      ]
    },
    {
      "id": "module-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named two-arm conditional callable replacement `count=None` follow-on on `abcdaceabcd`."
      ]
    },
    {
      "id": "module-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named two-arm conditional callable replacement `count=None` follow-on on `abcdaceabcd`."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "sub",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered two-arm conditional callable replacement `count=None` follow-on on the same legacy negative-count haystack."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "sub",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered two-arm conditional callable replacement `count=None` follow-on on the same legacy negative-count haystack."
      ]
    },
    {
      "id": "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named two-arm conditional callable replacement `count=None` follow-on on the same legacy negative-count haystack."
      ]
    },
    {
      "id": "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "haystack": "abcdaceabcd",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named two-arm conditional callable replacement `count=None` follow-on on the same legacy negative-count haystack."
      ]
    },
    {
      "id": "module-sub-numbered-conditional-group-exists-alternation-heavy-replacement-warm-gap",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzabcdezz",
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
        "alternation-heavy",
        "replacement",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered alternation-heavy two-arm conditional replacement workflow when the optional capture is present and the yes-arm alternation takes its first `de` branch."
      ]
    },
    {
      "id": "module-subn-numbered-conditional-group-exists-alternation-heavy-replacement-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzabcdfzz",
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
        "alternation-heavy",
        "replacement",
        "subn",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded numbered alternation-heavy two-arm conditional replacement count workflow when the optional capture is present and the yes-arm alternation takes its second `df` branch."
      ]
    },
    {
      "id": "pattern-sub-numbered-conditional-group-exists-alternation-heavy-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzacegzz",
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
        "alternation-heavy",
        "replacement",
        "sub",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered alternation-heavy two-arm conditional replacement workflow when the optional capture is absent and the else-arm alternation takes its first `eg` branch."
      ]
    },
    {
      "id": "pattern-subn-numbered-conditional-group-exists-alternation-heavy-replacement-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzacehzz",
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
        "alternation-heavy",
        "replacement",
        "subn",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded numbered alternation-heavy two-arm conditional replacement count workflow when the optional capture is absent and the else-arm alternation takes its second `eh` branch."
      ]
    },
    {
      "id": "module-sub-named-conditional-group-exists-alternation-heavy-replacement-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzabcdezz",
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
        "alternation-heavy",
        "replacement",
        "named-group",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded named alternation-heavy two-arm conditional replacement workflow when the optional named capture is present and the yes-arm alternation takes its first `de` branch."
      ]
    },
    {
      "id": "module-subn-named-conditional-group-exists-alternation-heavy-replacement-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzabcdfzz",
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
        "alternation-heavy",
        "replacement",
        "named-group",
        "subn",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named alternation-heavy two-arm conditional replacement count workflow when the optional named capture is present and the yes-arm alternation takes its second `df` branch."
      ]
    },
    {
      "id": "pattern-sub-named-conditional-group-exists-alternation-heavy-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzacegzz",
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
        "alternation-heavy",
        "replacement",
        "named-group",
        "sub",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded named alternation-heavy two-arm conditional replacement workflow when the optional named capture is absent and the else-arm alternation takes its first `eg` branch."
      ]
    },
    {
      "id": "pattern-subn-named-conditional-group-exists-alternation-heavy-replacement-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzacehzz",
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
        "alternation-heavy",
        "replacement",
        "named-group",
        "subn",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named alternation-heavy two-arm conditional replacement count workflow when the optional named capture is absent and the else-arm alternation takes its second `eh` branch."
      ]
    },
    {
      "id": "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-gap",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
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
        "alternation-heavy",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered alternation-heavy two-arm conditional callable replacement workflow when the optional capture is present, the yes-arm alternation takes its first `de` branch, and the callback reads `match.group(1)`."
      ]
    },
    {
      "id": "module-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzabcdfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
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
        "alternation-heavy",
        "replacement",
        "callable",
        "subn",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded numbered alternation-heavy two-arm conditional callable replacement count workflow when the optional capture is present, the yes-arm alternation takes its second `df` branch, and the callback reads `match.group(1)`."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzacegzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
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
        "alternation-heavy",
        "replacement",
        "callable",
        "sub",
        "absent",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered alternation-heavy two-arm conditional callable replacement workflow when the optional capture is absent, the else-arm alternation takes its first `eg` branch, and `match.group(1)` raises the bounded callback `TypeError`."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzacehzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
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
        "alternation-heavy",
        "replacement",
        "callable",
        "subn",
        "absent",
        "count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded numbered alternation-heavy two-arm conditional callable replacement count workflow when the optional capture is absent, the else-arm alternation takes its second `eh` branch, and the callback `TypeError` stays explicit on the compiled entrypoint."
      ]
    },
    {
      "id": "module-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
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
        "alternation-heavy",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded named alternation-heavy two-arm conditional callable replacement workflow when the optional named capture is present, the yes-arm alternation takes its first `de` branch, and the callback reads `match.group(\"word\")`."
      ]
    },
    {
      "id": "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzabcdfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
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
        "alternation-heavy",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named alternation-heavy two-arm conditional callable replacement count workflow when the optional named capture is present, the yes-arm alternation takes its second `df` branch, and the callback reads `match.group(\"word\")`."
      ]
    },
    {
      "id": "pattern-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzacegzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
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
        "alternation-heavy",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "absent",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded named alternation-heavy two-arm conditional callable replacement workflow when the optional named capture is absent, the else-arm alternation takes its first `eg` branch, and `match.group(\"word\")` raises the bounded callback `TypeError`."
      ]
    },
    {
      "id": "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzacehzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
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
        "alternation-heavy",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named alternation-heavy two-arm conditional callable replacement count workflow when the optional named capture is absent, the else-arm alternation takes its second `eh` branch, and the callback `TypeError` stays explicit on the compiled named entrypoint."
      ]
    },
    {
      "id": "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered alternation-heavy two-arm conditional callable replacement workflow when the optional capture is present, the yes-arm alternation takes its first `de` branch, and the callback reads `match.group(1)`."
      ]
    },
    {
      "id": "module-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzabcdfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "subn",
        "module",
        "present",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded numbered alternation-heavy two-arm conditional callable replacement count workflow when the optional capture is present, the yes-arm alternation takes its second `df` branch, and the callback reads `match.group(1)`."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzacegzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "sub",
        "absent",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered alternation-heavy two-arm conditional callable replacement workflow when the optional capture is absent, the else-arm alternation takes its first `eg` branch, and `match.group(1)` raises the bounded callback `TypeError`."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzacehzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "prefix": "<",
        "suffix": ">"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "subn",
        "absent",
        "count",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded numbered alternation-heavy two-arm conditional callable replacement count workflow when the optional capture is absent, the else-arm alternation takes its second `eh` branch, and the callback `TypeError` stays explicit on the compiled entrypoint."
      ]
    },
    {
      "id": "module-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded named alternation-heavy two-arm conditional callable replacement workflow when the optional named capture is present, the yes-arm alternation takes its first `de` branch, and the callback reads `match.group(\"word\")`."
      ]
    },
    {
      "id": "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzabcdfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "present",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named alternation-heavy two-arm conditional callable replacement count workflow when the optional named capture is present, the yes-arm alternation takes its second `df` branch, and the callback reads `match.group(\"word\")`."
      ]
    },
    {
      "id": "pattern-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzacegzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "absent",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded named alternation-heavy two-arm conditional callable replacement workflow when the optional named capture is absent, the else-arm alternation takes its first `eg` branch, and `match.group(\"word\")` raises the bounded callback `TypeError`."
      ]
    },
    {
      "id": "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzacehzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "prefix": "<",
        "suffix": ">"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "count",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named alternation-heavy two-arm conditional callable replacement count workflow when the optional named capture is absent, the else-arm alternation takes its second `eh` branch, and the callback `TypeError` stays explicit on the compiled named entrypoint."
      ]
    },
    {
      "id": "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "sub",
        "module",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered alternation-heavy conditional callable replacement negative-count workflow, keeping CPython's exact `count=-1` no-substitution and no-callback outcome explicit when the yes-arm would otherwise take `de`."
      ]
    },
    {
      "id": "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "sub",
        "module",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered alternation-heavy conditional callable replacement `count=None` follow-on, keeping the invalid-count `TypeError` explicit on the same yes-arm `de` haystack as the adjacent `count=-1` row."
      ]
    },
    {
      "id": "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzacehzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named alternation-heavy conditional callable replacement negative-count workflow, keeping the exact `count=-1` zero-replacement tuple visible when the else-arm would otherwise take `eh`."
      ]
    },
    {
      "id": "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzacehzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named alternation-heavy conditional callable replacement `count=None` follow-on, keeping the invalid-count `TypeError` explicit on the same else-arm `eh` haystack as the adjacent `count=-1` tuple row."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "sub",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered alternation-heavy conditional callable replacement negative-count workflow, keeping the same `count=-1` no-substitution outcome explicit on the compiled entrypoint."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "sub",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered alternation-heavy conditional callable replacement `count=None` follow-on, keeping the invalid-count `TypeError` explicit on the compiled entrypoint for the same yes-arm `de` haystack."
      ]
    },
    {
      "id": "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzacehzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named alternation-heavy conditional callable replacement negative-count workflow so the compiled entrypoint keeps the same `count=-1` zero-replacement tuple explicit when the else-arm would otherwise take `eh`."
      ]
    },
    {
      "id": "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzacehzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named alternation-heavy conditional callable replacement `count=None` follow-on so the compiled entrypoint keeps the invalid-count `TypeError` explicit on the same else-arm `eh` haystack."
      ]
    },
    {
      "id": "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "sub",
        "module",
        "negative-count",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered alternation-heavy conditional callable replacement negative-count workflow, keeping CPython's exact `count=-1` no-substitution and no-callback outcome explicit when the yes-arm would otherwise take `de`."
      ]
    },
    {
      "id": "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "sub",
        "module",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered alternation-heavy conditional callable replacement `count=None` follow-on, keeping the invalid-count `TypeError` explicit on the same yes-arm `de` haystack as the adjacent `count=-1` row."
      ]
    },
    {
      "id": "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzacehzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "negative-count",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named alternation-heavy conditional callable replacement negative-count workflow, keeping the exact `count=-1` zero-replacement tuple visible when the else-arm would otherwise take `eh`."
      ]
    },
    {
      "id": "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzacehzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named alternation-heavy conditional callable replacement `count=None` follow-on, keeping the invalid-count `TypeError` explicit on the same else-arm `eh` haystack as the adjacent `count=-1` tuple row."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "sub",
        "negative-count",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered alternation-heavy conditional callable replacement negative-count workflow, keeping the same `count=-1` no-substitution outcome explicit on the compiled entrypoint."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "sub",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered alternation-heavy conditional callable replacement `count=None` follow-on, keeping the invalid-count `TypeError` explicit on the compiled entrypoint for the same yes-arm `de` haystack."
      ]
    },
    {
      "id": "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzacehzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "negative-count",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named alternation-heavy conditional callable replacement negative-count workflow so the compiled entrypoint keeps the same `count=-1` zero-replacement tuple explicit when the else-arm would otherwise take `eh`."
      ]
    },
    {
      "id": "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "haystack": "zzacehzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named alternation-heavy conditional callable replacement `count=None` follow-on so the compiled entrypoint keeps the invalid-count `TypeError` explicit on the same else-arm `eh` haystack."
      ]
    },
    {
      "id": "module-sub-numbered-nested-conditional-group-exists-replacement-warm-gap",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
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
        "nested-conditional",
        "replacement",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered nested two-arm conditional replacement workflow when the optional capture is present and the outer and inner yes arms both keep the trailing `d` inside the replaced span."
      ]
    },
    {
      "id": "module-subn-numbered-nested-conditional-group-exists-replacement-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzacfzz",
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
        "nested-conditional",
        "replacement",
        "subn",
        "module",
        "absent",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded numbered nested two-arm conditional replacement count workflow when the optional capture is absent and the outer else arm contributes the accepted trailing `f`."
      ]
    },
    {
      "id": "pattern-sub-numbered-nested-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
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
        "nested-conditional",
        "replacement",
        "sub",
        "present",
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
        "Purged-cache Pattern.sub helper path for the bounded numbered nested two-arm conditional replacement workflow when the optional capture is present and both nested yes arms still force the trailing `d`."
      ]
    },
    {
      "id": "pattern-subn-numbered-nested-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzacfzz",
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
        "nested-conditional",
        "replacement",
        "subn",
        "absent",
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
        "Purged-cache Pattern.subn helper path for the bounded numbered nested two-arm conditional replacement count workflow when the optional capture is absent and the outer else arm leaves the accepted trailing `f` inside the replaced span."
      ]
    },
    {
      "id": "module-sub-named-nested-conditional-group-exists-replacement-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
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
        "nested-conditional",
        "replacement",
        "named-group",
        "sub",
        "module",
        "present",
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
        "Warm module.sub helper path for the bounded named nested two-arm conditional replacement workflow when the optional named capture is present and the nested yes arm still requires the trailing `d`."
      ]
    },
    {
      "id": "module-subn-named-nested-conditional-group-exists-replacement-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacfzz",
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
        "nested-conditional",
        "replacement",
        "named-group",
        "subn",
        "module",
        "absent",
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
        "Warm module.subn helper path for the bounded named nested two-arm conditional replacement count workflow when the optional named capture is absent and the outer else arm contributes the accepted trailing `f`."
      ]
    },
    {
      "id": "pattern-sub-named-nested-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
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
        "nested-conditional",
        "replacement",
        "named-group",
        "sub",
        "present",
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
        "Purged-cache Pattern.sub helper path for the bounded named nested two-arm conditional replacement workflow when the optional named capture is present and the nested yes arm still keeps the trailing `d` explicit."
      ]
    },
    {
      "id": "pattern-subn-named-nested-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacfzz",
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
        "nested-conditional",
        "replacement",
        "named-group",
        "subn",
        "absent",
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
        "Purged-cache Pattern.subn helper path for the bounded named nested two-arm conditional replacement count workflow when the optional named capture is absent and the outer else arm contributes the accepted trailing `f`."
      ]
    },
    {
      "id": "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "nested-conditional",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered nested conditional callable replacement workflow when the optional capture is present, both yes arms keep the trailing `d`, and the callback reads `match.group(1)` before appending `x`."
      ]
    },
    {
      "id": "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzacfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
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
        "nested-conditional",
        "replacement",
        "callable",
        "subn",
        "module",
        "absent",
        "count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded numbered nested conditional callable replacement absent-capture workflow on `zzacfzz`, keeping `callable_match_group` pinned to `match.group(1)` so the bounded `TypeError` remains explicit."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "nested-conditional",
        "replacement",
        "callable",
        "sub",
        "present",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered nested conditional callable replacement workflow on the same present-capture haystack, keeping the callback on `match.group(1)` and appending `x` after the nested yes arms select `d`."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzacfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
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
        "nested-conditional",
        "replacement",
        "callable",
        "subn",
        "absent",
        "count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded numbered nested conditional callable replacement absent-capture workflow, keeping the compiled-entrypoint `TypeError` on `match.group(1) + \"x\"` explicit."
      ]
    },
    {
      "id": "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
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
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded named nested conditional callable replacement workflow when the optional named capture is present and the callback appends `x` to `match.group(\"word\")` after the nested yes arms retain `d`."
      ]
    },
    {
      "id": "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
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
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named nested conditional callable replacement absent-capture workflow, keeping the named `TypeError` from `match.group(\"word\") + \"x\"` explicit on the module entrypoint."
      ]
    },
    {
      "id": "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
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
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "present",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded named nested conditional callable replacement workflow on the same present-capture haystack, keeping `match.group(\"word\") + \"x\"` on the compiled entrypoint."
      ]
    },
    {
      "id": "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
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
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named nested conditional callable replacement absent-capture workflow so the smallest compiled named `TypeError` remains explicit too."
      ]
    },
    {
      "id": "module-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzabcezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "nested-conditional",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered nested conditional callable replacement near-miss workflow where the present capture still leaves the inner yes arm expecting `d`, so `zzabcezz` is returned unchanged without invoking `match.group(1)`."
      ]
    },
    {
      "id": "module-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "nested-conditional",
        "replacement",
        "callable",
        "subn",
        "module",
        "absent",
        "count",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded numbered nested conditional callable replacement near-miss count workflow where the absent capture falls through to `f`, so `subn(..., 1)` leaves `zzacezz` and the replacement count unchanged without invoking `match.group(1)`."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzabcezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "nested-conditional",
        "replacement",
        "callable",
        "sub",
        "present",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered nested conditional callable replacement near-miss workflow on the same present-capture haystack, keeping the compiled entrypoint unchanged because the callback never runs."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "nested-conditional",
        "replacement",
        "callable",
        "subn",
        "absent",
        "count",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded numbered nested conditional callable replacement near-miss count workflow where the absent-capture no-match keeps both the haystack and replacement count unchanged."
      ]
    },
    {
      "id": "module-sub-callable-named-nested-conditional-group-exists-replacement-no-match-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzabcezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
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
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded named nested conditional callable replacement near-miss workflow where the present named capture still leaves the inner yes arm demanding `d`, so the callback never runs on `zzabcezz`."
      ]
    },
    {
      "id": "module-subn-callable-named-nested-conditional-group-exists-replacement-no-match-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
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
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "count",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named nested conditional callable replacement near-miss count workflow where the absent named capture falls through to `f`, so `subn(..., 1)` returns `(\"zzacezz\", 0)` without touching `match.group(\"word\")`."
      ]
    },
    {
      "id": "pattern-sub-callable-named-nested-conditional-group-exists-replacement-no-match-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzabcezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
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
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "present",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded named nested conditional callable replacement near-miss workflow on the same present-capture haystack, keeping the compiled entrypoint unchanged because `match.group(\"word\")` is never read."
      ]
    },
    {
      "id": "pattern-subn-callable-named-nested-conditional-group-exists-replacement-no-match-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
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
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "count",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named nested conditional callable replacement near-miss count workflow where the absent named-capture no-match keeps both the haystack and replacement count unchanged."
      ]
    },
    {
      "id": "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered nested conditional callable replacement workflow when the optional capture is present, both yes arms keep the trailing `d`, and the callback reads `match.group(1)` before appending `x`."
      ]
    },
    {
      "id": "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzacfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "subn",
        "module",
        "absent",
        "count",
        "exception",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded numbered nested conditional callable replacement absent-capture workflow on `zzacfzz`, keeping `callable_match_group` pinned to `match.group(1)` so the bounded `TypeError` remains explicit."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "sub",
        "present",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered nested conditional callable replacement workflow on the same present-capture haystack, keeping the callback on `match.group(1)` and appending `x` after the nested yes arms select `d`."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzacfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "subn",
        "absent",
        "count",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded numbered nested conditional callable replacement absent-capture workflow, keeping the compiled-entrypoint `TypeError` on `match.group(1) + b\"x\"` explicit."
      ]
    },
    {
      "id": "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded named nested conditional callable replacement workflow when the optional named capture is present and the callback appends `x` to `match.group(\"word\")` after the nested yes arms retain `d`."
      ]
    },
    {
      "id": "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "count",
        "exception",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named nested conditional callable replacement absent-capture workflow, keeping the named `TypeError` from `match.group(\"word\") + b\"x\"` explicit on the module entrypoint."
      ]
    },
    {
      "id": "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "present",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded named nested conditional callable replacement workflow on the same present-capture haystack, keeping `match.group(\"word\") + b\"x\"` on the compiled entrypoint."
      ]
    },
    {
      "id": "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "count",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named nested conditional callable replacement absent-capture workflow so the smallest compiled named `TypeError` remains explicit too."
      ]
    },
    {
      "id": "module-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzabcezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "bytes",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered nested conditional callable replacement near-miss workflow where the present capture still leaves the inner yes arm expecting `d`, so `b\"zzabcezz\"` is returned unchanged without invoking `match.group(1)`."
      ]
    },
    {
      "id": "module-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "subn",
        "module",
        "absent",
        "count",
        "bytes",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded numbered nested conditional callable replacement near-miss count workflow where the absent capture falls through to `f`, so `subn(..., 1)` leaves `b\"zzacezz\"` and the replacement count unchanged without invoking `match.group(1)`."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzabcezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "sub",
        "present",
        "bytes",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered nested conditional callable replacement near-miss workflow on the same present-capture haystack, keeping the compiled entrypoint unchanged because the callback never runs."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "subn",
        "absent",
        "count",
        "bytes",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded numbered nested conditional callable replacement near-miss count workflow where the absent-capture no-match keeps both the haystack and replacement count unchanged."
      ]
    },
    {
      "id": "module-sub-callable-named-nested-conditional-group-exists-replacement-no-match-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzabcezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "bytes",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded named nested conditional callable replacement near-miss workflow where the present named capture still leaves the inner yes arm demanding `d`, so the callback never runs on `b\"zzabcezz\"`."
      ]
    },
    {
      "id": "module-subn-callable-named-nested-conditional-group-exists-replacement-no-match-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "count",
        "bytes",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named nested conditional callable replacement near-miss count workflow where the absent named capture falls through to `f`, so `subn(..., 1)` returns `(b\"zzacezz\", 0)` without touching `match.group(\"word\")`."
      ]
    },
    {
      "id": "pattern-sub-callable-named-nested-conditional-group-exists-replacement-no-match-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzabcezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "present",
        "bytes",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded named nested conditional callable replacement near-miss workflow on the same present-capture haystack, keeping the compiled entrypoint unchanged because `match.group(\"word\")` is never read."
      ]
    },
    {
      "id": "pattern-subn-callable-named-nested-conditional-group-exists-replacement-no-match-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "count",
        "bytes",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named nested conditional callable replacement near-miss count workflow where the absent named-capture no-match keeps both the haystack and replacement count unchanged."
      ]
    },
    {
      "id": "module-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered nested conditional callable replacement negative-count workflow, keeping the exact `count=-1` no-substitution outcome explicit on `zzabcdzz` without invoking `match.group(1)`."
      ]
    },
    {
      "id": "module-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named nested conditional callable replacement negative-count workflow, keeping the exact `count=-1` zero-replacement tuple outcome explicit on `zzacfzz` without invoking `match.group(\"word\")`."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "sub",
        "present",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered nested conditional callable replacement negative-count workflow, keeping the same `count=-1` no-substitution outcome explicit on the compiled entrypoint without invoking `match.group(1)`."
      ]
    },
    {
      "id": "pattern-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named nested conditional callable replacement negative-count workflow, keeping the same `count=-1` zero-replacement tuple outcome explicit on the compiled entrypoint without invoking `match.group(\"word\")`."
      ]
    },
    {
      "id": "module-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "bytes",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered nested conditional callable replacement negative-count workflow, keeping the exact `count=-1` no-substitution outcome explicit on `zzabcdzz` without invoking `match.group(1)`."
      ]
    },
    {
      "id": "module-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "bytes",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named nested conditional callable replacement negative-count workflow, keeping the exact `count=-1` zero-replacement tuple outcome explicit on `zzacfzz` without invoking `match.group(\"word\")`."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "sub",
        "present",
        "bytes",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered nested conditional callable replacement negative-count workflow, keeping the same `count=-1` no-substitution outcome explicit on the compiled entrypoint without invoking `match.group(1)`."
      ]
    },
    {
      "id": "pattern-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "bytes",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named nested conditional callable replacement negative-count workflow, keeping the same `count=-1` zero-replacement tuple outcome explicit on the compiled entrypoint without invoking `match.group(\"word\")`."
      ]
    },
    {
      "id": "module-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered nested conditional callable replacement `count=None` follow-on on `zzabcdzz`, keeping CPython's invalid-count `TypeError` explicit before the callback can read `match.group(1)`."
      ]
    },
    {
      "id": "module-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named nested conditional callable replacement `count=None` follow-on on `zzacfzz`, keeping the invalid-count `TypeError` explicit on the same owner-path haystack before `match.group(\"word\")` can run."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "sub",
        "present",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered nested conditional callable replacement `count=None` follow-on on the compiled entrypoint, keeping CPython's invalid-count `TypeError` explicit."
      ]
    },
    {
      "id": "pattern-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named nested conditional callable replacement `count=None` follow-on on the compiled entrypoint, keeping the invalid-count `TypeError` explicit before `match.group(\"word\")` can run."
      ]
    },
    {
      "id": "module-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "bytes",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered nested conditional callable replacement `count=None` follow-on on `zzabcdzz`, keeping CPython's invalid-count `TypeError` explicit before the callback can read `match.group(1)`."
      ]
    },
    {
      "id": "module-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "bytes",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named nested conditional callable replacement `count=None` follow-on on `zzacfzz`, keeping the invalid-count `TypeError` explicit on the same owner-path haystack before `match.group(\"word\")` can run."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "zzabcdzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "sub",
        "present",
        "bytes",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered nested conditional callable replacement `count=None` follow-on on the compiled entrypoint, keeping CPython's invalid-count `TypeError` explicit."
      ]
    },
    {
      "id": "pattern-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "zzacfzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": None,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "nested-conditional",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "bytes",
        "negative-count",
        "count",
        "none-count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named nested conditional callable replacement `count=None` follow-on on the compiled entrypoint, keeping the invalid-count `TypeError` explicit before `match.group(\"word\")` can run."
      ]
    },
    {
      "id": "module-sub-numbered-quantified-conditional-group-exists-replacement-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcddzz",
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
        "quantified",
        "replacement",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered quantified two-arm conditional replacement workflow when the optional capture is present and the repeated yes arm requires `dd` before replacement text is emitted."
      ]
    },
    {
      "id": "module-subn-numbered-quantified-conditional-group-exists-replacement-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzaceezz",
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
        "quantified",
        "replacement",
        "subn",
        "module",
        "absent",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded numbered quantified two-arm conditional replacement count workflow when the optional capture is absent and the repeated else arm contributes `ee`."
      ]
    },
    {
      "id": "pattern-sub-numbered-quantified-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcddzz",
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
        "quantified",
        "replacement",
        "sub",
        "present",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered quantified two-arm conditional replacement workflow when the optional capture is present and the matched span ends with repeated `dd`."
      ]
    },
    {
      "id": "pattern-subn-numbered-quantified-conditional-group-exists-replacement-purged-gap",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzaceezz",
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
        "quantified",
        "replacement",
        "subn",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded numbered quantified two-arm conditional replacement count workflow when the optional capture is absent and the matched span instead ends with repeated `ee`."
      ]
    },
    {
      "id": "module-sub-named-quantified-conditional-group-exists-replacement-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcddzz",
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
        "quantified",
        "replacement",
        "named-group",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded named quantified two-arm conditional replacement workflow when the optional named capture is present and the repeated yes arm still requires `dd`."
      ]
    },
    {
      "id": "module-subn-named-quantified-conditional-group-exists-replacement-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzaceezz",
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
        "quantified",
        "replacement",
        "named-group",
        "subn",
        "module",
        "absent",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named quantified two-arm conditional replacement count workflow when the optional named capture is absent and the repeated else arm contributes `ee`."
      ]
    },
    {
      "id": "pattern-sub-named-quantified-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcddzz",
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
        "quantified",
        "replacement",
        "named-group",
        "sub",
        "present",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded named quantified two-arm conditional replacement workflow when the optional named capture is present and the repeated yes arm still keeps `dd` explicit."
      ]
    },
    {
      "id": "pattern-subn-named-quantified-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzaceezz",
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
        "quantified",
        "replacement",
        "named-group",
        "subn",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named quantified two-arm conditional replacement count workflow when the optional named capture is absent and the matched span ends with repeated `ee`."
      ]
    },
    {
      "id": "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcddzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "quantified",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered quantified conditional callable replacement workflow where the present capture keeps both counted repetitions on the `d` arm before the callback reads `match.group(1)`."
      ]
    },
    {
      "id": "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcddzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered quantified conditional callable replacement workflow where the present capture keeps both counted repetitions on the `d` arm before the callback reads `match.group(1)`."
      ]
    },
    {
      "id": "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzaceezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
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
        "quantified",
        "replacement",
        "callable",
        "subn",
        "module",
        "absent",
        "count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded numbered quantified conditional callable replacement count workflow when the optional capture is absent and the repeated else arm leaves `match.group(1)` as `None`, preserving CPython's bounded `TypeError`."
      ]
    },
    {
      "id": "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzaceezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "subn",
        "module",
        "absent",
        "count",
        "exception",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded numbered quantified conditional callable replacement count workflow when the optional capture is absent and the repeated else arm leaves `match.group(1)` as `None`, preserving CPython's bounded `TypeError`."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcddzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "quantified",
        "replacement",
        "callable",
        "sub",
        "present",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered quantified conditional callable replacement path for the same present-capture workflow."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcddzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "sub",
        "present",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered quantified conditional callable replacement path for the same present-capture workflow."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzaceezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
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
        "quantified",
        "replacement",
        "callable",
        "subn",
        "absent",
        "count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded numbered quantified conditional callable replacement count workflow when the optional capture is absent so the compiled-entrypoint `TypeError` remains explicit too."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzaceezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "subn",
        "absent",
        "count",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded numbered quantified conditional callable replacement count workflow when the optional capture is absent so the compiled-entrypoint `TypeError` remains explicit too."
      ]
    },
    {
      "id": "module-sub-callable-named-quantified-conditional-group-exists-replacement-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcddzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
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
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded named quantified conditional callable replacement workflow where the repeated yes arm preserves `match.group(\"word\")` for the callback."
      ]
    },
    {
      "id": "module-sub-callable-named-quantified-conditional-group-exists-replacement-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcddzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded named quantified conditional callable replacement workflow where the repeated yes arm preserves `match.group(\"word\")` for the callback."
      ]
    },
    {
      "id": "module-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzaceezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
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
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "count",
        "exception",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named quantified conditional callable replacement count workflow when the named capture is absent, keeping the helper pinned to `match.group(\"word\")` so the bounded `TypeError` stays published."
      ]
    },
    {
      "id": "module-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzaceezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "count",
        "exception",
        "bytes",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named quantified conditional callable replacement count workflow when the named capture is absent, keeping the helper pinned to `match.group(\"word\")` so the bounded `TypeError` stays published."
      ]
    },
    {
      "id": "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcddzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
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
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "present",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded named quantified conditional callable replacement path for the same present-capture workflow."
      ]
    },
    {
      "id": "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcddzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "present",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded named quantified conditional callable replacement path for the same present-capture workflow."
      ]
    },
    {
      "id": "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzaceezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
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
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "count",
        "exception",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named quantified conditional callable replacement count path when the named capture is absent so the compiled named `TypeError` path stays explicit too."
      ]
    },
    {
      "id": "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzaceezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "NoneType"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "count",
        "exception",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named quantified conditional callable replacement count path when the named capture is absent so the compiled named `TypeError` path stays explicit too."
      ]
    },
    {
      "id": "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcddzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered quantified conditional callable replacement negative-count workflow, keeping the exact `count=-1` no-substitution outcome explicit on `zzabcddzz` without invoking `match.group(1)`."
      ]
    },
    {
      "id": "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzaceezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "subn",
        "module",
        "absent",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded numbered quantified conditional callable replacement negative-count workflow, keeping the exact `count=-1` zero-replacement tuple outcome explicit on `zzaceezz` without touching `match.group(1)`."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcddzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "sub",
        "present",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered quantified conditional callable replacement negative-count workflow, keeping the same `count=-1` no-substitution outcome explicit on the compiled entrypoint without invoking `match.group(1)`."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzaceezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "subn",
        "absent",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded numbered quantified conditional callable replacement negative-count workflow, keeping the same `count=-1` zero-replacement tuple outcome explicit on the compiled entrypoint without touching `match.group(1)`."
      ]
    },
    {
      "id": "module-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcddzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded named quantified conditional callable replacement negative-count workflow, keeping the shared `count=-1` short-circuit explicit on `zzabcddzz` without invoking `match.group(\"word\")`."
      ]
    },
    {
      "id": "module-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzaceezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named quantified conditional callable replacement negative-count workflow, keeping the exact `count=-1` zero-replacement tuple outcome explicit on `zzaceezz` without touching `match.group(\"word\")`."
      ]
    },
    {
      "id": "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcddzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "present",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded named quantified conditional callable replacement negative-count workflow, keeping the same `count=-1` no-substitution outcome explicit on the compiled entrypoint without invoking `match.group(\"word\")`."
      ]
    },
    {
      "id": "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzaceezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named quantified conditional callable replacement negative-count workflow, keeping the same `count=-1` zero-replacement tuple outcome explicit on the compiled entrypoint without touching `match.group(\"word\")`."
      ]
    },
    {
      "id": "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcddzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "bytes",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered quantified conditional callable replacement negative-count workflow, keeping the exact `count=-1` no-substitution outcome explicit on `b\"zzabcddzz\"` without invoking `match.group(1)`."
      ]
    },
    {
      "id": "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzaceezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "subn",
        "module",
        "absent",
        "bytes",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded numbered quantified conditional callable replacement negative-count workflow, keeping the exact `count=-1` zero-replacement tuple outcome explicit on `b\"zzaceezz\"` without touching `match.group(1)`."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcddzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "sub",
        "present",
        "bytes",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered quantified conditional callable replacement negative-count workflow, keeping the same `count=-1` no-substitution outcome explicit on the compiled entrypoint without invoking `match.group(1)`."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzaceezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "subn",
        "absent",
        "bytes",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded numbered quantified conditional callable replacement negative-count workflow, keeping the same `count=-1` zero-replacement tuple outcome explicit on the compiled entrypoint without touching `match.group(1)`."
      ]
    },
    {
      "id": "module-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcddzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "bytes",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded named quantified conditional callable replacement negative-count workflow, keeping the shared `count=-1` short-circuit explicit on `b\"zzabcddzz\"` without invoking `match.group(\"word\")`."
      ]
    },
    {
      "id": "module-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzaceezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "bytes",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named quantified conditional callable replacement negative-count workflow, keeping the exact `count=-1` zero-replacement tuple outcome explicit on `b\"zzaceezz\"` without touching `match.group(\"word\")`."
      ]
    },
    {
      "id": "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcddzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "present",
        "bytes",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded named quantified conditional callable replacement negative-count workflow, keeping the same `count=-1` no-substitution outcome explicit on the compiled entrypoint without invoking `match.group(\"word\")`."
      ]
    },
    {
      "id": "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzaceezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "bytes",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named quantified conditional callable replacement negative-count workflow, keeping the same `count=-1` zero-replacement tuple outcome explicit on the compiled entrypoint without touching `match.group(\"word\")`."
      ]
    },
    {
      "id": "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "no-match",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered quantified conditional callable replacement negative-count near-miss workflow, keeping `zzabcdezz` unchanged without invoking `match.group(1)` because `count=-1` and the quantified match never forms."
      ]
    },
    {
      "id": "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzacedzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "subn",
        "module",
        "absent",
        "no-match",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded numbered quantified conditional callable replacement negative-count near-miss workflow, keeping `(\"zzacedzz\", 0)` explicit without touching `match.group(1)` because the quantified match never forms."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "sub",
        "present",
        "no-match",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered quantified conditional callable replacement negative-count near-miss workflow, keeping the compiled entrypoint unchanged on `zzabcdezz` because the callback never runs."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzacedzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "subn",
        "absent",
        "no-match",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded numbered quantified conditional callable replacement negative-count near-miss workflow, keeping the compiled `(\"zzacedzz\", 0)` outcome explicit because the quantified match never forms."
      ]
    },
    {
      "id": "module-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "no-match",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded named quantified conditional callable replacement negative-count near-miss workflow, keeping `zzabcdezz` unchanged without invoking `match.group(\"word\")` because the quantified match never forms."
      ]
    },
    {
      "id": "module-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzacedzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "no-match",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named quantified conditional callable replacement negative-count near-miss workflow, keeping `(\"zzacedzz\", 0)` explicit without touching `match.group(\"word\")` because the quantified match never forms."
      ]
    },
    {
      "id": "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "present",
        "no-match",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded named quantified conditional callable replacement negative-count near-miss workflow, keeping the compiled entrypoint unchanged on `zzabcdezz` because `match.group(\"word\")` is never read."
      ]
    },
    {
      "id": "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzacedzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "no-match",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named quantified conditional callable replacement negative-count near-miss workflow, keeping the compiled `(\"zzacedzz\", 0)` outcome explicit because the quantified match never forms."
      ]
    },
    {
      "id": "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "bytes",
        "no-match",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered quantified conditional callable replacement negative-count near-miss workflow, keeping `b\"zzabcdezz\"` unchanged without invoking `match.group(1)` because `count=-1` and the quantified match never forms."
      ]
    },
    {
      "id": "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzacedzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "subn",
        "module",
        "absent",
        "bytes",
        "no-match",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded numbered quantified conditional callable replacement negative-count near-miss workflow, keeping `(b\"zzacedzz\", 0)` explicit without touching `match.group(1)` because the quantified match never forms."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "sub",
        "present",
        "bytes",
        "no-match",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered quantified conditional callable replacement negative-count near-miss workflow, keeping the compiled entrypoint unchanged on `b\"zzabcdezz\"` because the callback never runs."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzacedzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "subn",
        "absent",
        "bytes",
        "no-match",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded numbered quantified conditional callable replacement negative-count near-miss workflow, keeping the compiled `(b\"zzacedzz\", 0)` outcome explicit because the quantified match never forms."
      ]
    },
    {
      "id": "module-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "bytes",
        "no-match",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded named quantified conditional callable replacement negative-count near-miss workflow, keeping `b\"zzabcdezz\"` unchanged without invoking `match.group(\"word\")` because the quantified match never forms."
      ]
    },
    {
      "id": "module-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzacedzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "bytes",
        "no-match",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named quantified conditional callable replacement negative-count near-miss workflow, keeping `(b\"zzacedzz\", 0)` explicit without touching `match.group(\"word\")` because the quantified match never forms."
      ]
    },
    {
      "id": "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "present",
        "bytes",
        "no-match",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded named quantified conditional callable replacement negative-count near-miss workflow, keeping the compiled entrypoint unchanged on `b\"zzabcdezz\"` because `match.group(\"word\")` is never read."
      ]
    },
    {
      "id": "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzacedzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": -1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "bytes",
        "no-match",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named quantified conditional callable replacement negative-count near-miss workflow, keeping the compiled `(b\"zzacedzz\", 0)` outcome explicit because the quantified match never forms."
      ]
    },
    {
      "id": "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-no-match-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "quantified",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered quantified conditional callable replacement near-miss workflow where the present capture still leaves the repeated else arm unmatched, so `zzabcdezz` is returned unchanged without invoking `match.group(1)`."
      ]
    },
    {
      "id": "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-no-match-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzacedzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "quantified",
        "replacement",
        "callable",
        "subn",
        "module",
        "absent",
        "count",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded numbered quantified conditional callable replacement near-miss count workflow where the absent capture would take the repeated yes arm, so `subn(..., 1)` leaves `zzacedzz` and the replacement count unchanged without invoking `match.group(1)`."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-no-match-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "quantified",
        "replacement",
        "callable",
        "sub",
        "present",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered quantified conditional callable replacement near-miss workflow on the same present-capture haystack, keeping the compiled entrypoint unchanged because the callback never runs."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-no-match-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzacedzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
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
        "quantified",
        "replacement",
        "callable",
        "subn",
        "absent",
        "count",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded numbered quantified conditional callable replacement near-miss count workflow where the absent-capture no-match keeps both the haystack and replacement count unchanged."
      ]
    },
    {
      "id": "module-sub-callable-named-quantified-conditional-group-exists-replacement-no-match-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
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
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded named quantified conditional callable replacement near-miss workflow where the present named capture still leaves the repeated else arm unmatched, so the callback never runs on `zzabcdezz`."
      ]
    },
    {
      "id": "module-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzacedzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
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
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "count",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named quantified conditional callable replacement near-miss count workflow where the absent named capture would take the repeated yes arm, so `subn(..., 1)` returns `(\"zzacedzz\", 0)` without touching `match.group(\"word\")`."
      ]
    },
    {
      "id": "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-no-match-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
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
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "present",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded named quantified conditional callable replacement near-miss workflow on the same present-capture haystack, keeping the compiled entrypoint unchanged because `match.group(\"word\")` is never read."
      ]
    },
    {
      "id": "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzacedzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
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
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "count",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named quantified conditional callable replacement near-miss count workflow where the absent named-capture no-match keeps both the haystack and replacement count unchanged."
      ]
    },
    {
      "id": "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-no-match-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "sub",
        "module",
        "present",
        "bytes",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded numbered quantified conditional callable replacement near-miss workflow where the present capture still leaves the repeated else arm unmatched, so `b\"zzabcdezz\"` is returned unchanged without invoking `match.group(1)`."
      ]
    },
    {
      "id": "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-no-match-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzacedzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "subn",
        "module",
        "absent",
        "count",
        "bytes",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded numbered quantified conditional callable replacement near-miss count workflow where the absent capture would take the repeated yes arm, so `subn(..., 1)` leaves `b\"zzacedzz\"` and the replacement count unchanged without invoking `match.group(1)`."
      ]
    },
    {
      "id": "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "sub",
        "present",
        "bytes",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded numbered quantified conditional callable replacement near-miss workflow on the same present-capture haystack, keeping the compiled entrypoint unchanged because the callback never runs."
      ]
    },
    {
      "id": "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "zzacedzz",
      "replacement": {
        "type": "callable_match_group",
        "group": 1,
        "suffix": "x"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "subn",
        "absent",
        "count",
        "bytes",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded numbered quantified conditional callable replacement near-miss count workflow where the absent-capture no-match keeps both the haystack and replacement count unchanged."
      ]
    },
    {
      "id": "module-sub-callable-named-quantified-conditional-group-exists-replacement-no-match-warm-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "module",
        "present",
        "bytes",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.sub helper path for the bounded named quantified conditional callable replacement near-miss workflow where the present named capture still leaves the repeated else arm unmatched, so the callback never runs on `b\"zzabcdezz\"`."
      ]
    },
    {
      "id": "module-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzacedzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "module",
        "absent",
        "count",
        "bytes",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement"
      ],
      "notes": [
        "Warm bytes module.subn helper path for the bounded named quantified conditional callable replacement near-miss count workflow where the absent named capture would take the repeated yes arm, so `subn(..., 1)` returns `(b\"zzacedzz\", 0)` without touching `match.group(\"word\")`."
      ]
    },
    {
      "id": "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzabcdezz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "sub",
        "present",
        "bytes",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.sub helper path for the bounded named quantified conditional callable replacement near-miss workflow on the same present-capture haystack, keeping the compiled entrypoint unchanged because `match.group(\"word\")` is never read."
      ]
    },
    {
      "id": "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "zzacedzz",
      "replacement": {
        "type": "callable_match_group",
        "group": "word",
        "suffix": "x"
      },
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "quantified",
        "replacement",
        "callable",
        "named-group",
        "subn",
        "absent",
        "count",
        "bytes",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "quantifiers",
        "callable-replacement",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.subn helper path for the bounded named quantified conditional callable replacement near-miss count workflow where the absent named-capture no-match keeps both the haystack and replacement count unchanged."
      ]
    },
    {
      "id": "module-search-numbered-nested-conditional-group-exists-present-cold-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
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
        "Cold module.search helper path for the bounded numbered nested two-arm conditional workflow when the optional capture is present and both outer and inner yes arms select the trailing `d` suffix."
      ]
    },
    {
      "id": "pattern-fullmatch-numbered-nested-conditional-group-exists-absent-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "haystack": "acf",
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
        "Purged-cache Pattern.fullmatch probe for the bounded numbered nested two-arm conditional workflow when the optional capture is absent and the outer else arm contributes the accepted trailing `f`."
      ]
    },
    {
      "id": "module-search-named-nested-conditional-group-exists-present-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
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
        "Warm module.search helper path for the bounded named nested two-arm conditional workflow when the optional named capture is present and the nested yes arm still requires the trailing `d`."
      ]
    },
    {
      "id": "pattern-fullmatch-named-nested-conditional-group-exists-absent-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "haystack": "acf",
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
        "Purged-cache Pattern.fullmatch probe for the bounded named nested two-arm conditional workflow when the optional named capture is absent and the outer else arm keeps the accepted trailing `f` explicit."
      ]
    },
    {
      "id": "pattern-fullmatch-numbered-quantified-conditional-group-exists-purged-gap",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "haystack": "abcdd",
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
        "Purged-cache Pattern.fullmatch probe for the bounded numbered quantified conditional workflow when the optional capture is present and the repeated yes arm must supply exactly two trailing `d` literals."
      ]
    },
    {
      "id": "pattern-fullmatch-named-quantified-conditional-group-exists-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "haystack": "abcdd",
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
        "Purged-cache Pattern.fullmatch probe for the bounded named quantified conditional workflow when the optional named capture is present and the repeated yes arm must still supply exactly two trailing `d` literals."
      ]
    },
    {
      "id": "module-search-numbered-conditional-group-exists-quantified-alternation-heavy-present-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh)){2}",
      "haystack": "zzabcdedezz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
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
        "alternation",
        "quantifiers"
      ],
      "notes": [
        "Warm module.search helper path for the bounded numbered quantified alternation-heavy two-arm conditional workflow when the optional capture is present and the repeated yes arm selects its first literal branch twice."
      ]
    },
    {
      "id": "module-search-named-conditional-group-exists-quantified-alternation-heavy-absent-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
      "haystack": "zzacegegzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "optional-group",
        "conditional",
        "group-exists",
        "alternation-heavy",
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
        "conditionals",
        "named-groups",
        "alternation",
        "quantifiers"
      ],
      "notes": [
        "Warm module.search helper path for the bounded named quantified alternation-heavy two-arm conditional workflow when the optional named capture is absent and the repeated else arm selects its first literal branch twice."
      ]
    },
    {
      "id": "pattern-fullmatch-numbered-conditional-group-exists-quantified-alternation-heavy-absent-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh)){2}",
      "haystack": "aceheh",
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
        "alternation-heavy",
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
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the bounded numbered quantified alternation-heavy two-arm conditional workflow when the optional capture is absent and the repeated else arm backtracks to its second literal branch twice."
      ]
    },
    {
      "id": "pattern-fullmatch-named-conditional-group-exists-quantified-alternation-heavy-present-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
      "haystack": "abcdfdf",
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
        "alternation-heavy",
        "named-group",
        "fullmatch",
        "present",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch probe for the bounded named quantified alternation-heavy two-arm conditional workflow when the optional named capture is present and the repeated yes arm backtracks to its second literal branch twice."
      ]
    },
    {
      "id": "module-sub-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh)){2}",
      "haystack": "zzabcdedezz",
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
        "alternation-heavy",
        "quantified",
        "replacement",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "quantifiers"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded numbered quantified alternation-heavy two-arm conditional replacement workflow when the optional capture is present and the repeated yes-arm alternation takes its first `de` branch on both evaluations."
      ]
    },
    {
      "id": "module-subn-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh)){2}",
      "haystack": "zzabcdfdfzz",
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
        "alternation-heavy",
        "quantified",
        "replacement",
        "subn",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "quantifiers"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded numbered quantified alternation-heavy two-arm conditional replacement count workflow when the optional capture is present and the repeated yes-arm alternation takes its second `df` branch on both evaluations."
      ]
    },
    {
      "id": "pattern-sub-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh)){2}",
      "haystack": "zzacegegzz",
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
        "alternation-heavy",
        "quantified",
        "replacement",
        "sub",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded numbered quantified alternation-heavy two-arm conditional replacement workflow when the optional capture is absent and the repeated else-arm alternation takes its first `eg` branch on both evaluations."
      ]
    },
    {
      "id": "pattern-subn-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh)){2}",
      "haystack": "zzacehehzz",
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
        "alternation-heavy",
        "quantified",
        "replacement",
        "subn",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "alternation",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded numbered quantified alternation-heavy two-arm conditional replacement count workflow when the optional capture is absent and the repeated else-arm alternation takes its second `eh` branch on both evaluations."
      ]
    },
    {
      "id": "module-sub-named-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
      "haystack": "zzabcdedezz",
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
        "alternation-heavy",
        "quantified",
        "replacement",
        "named-group",
        "sub",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "quantifiers"
      ],
      "notes": [
        "Warm module.sub helper path for the bounded named quantified alternation-heavy two-arm conditional replacement workflow when the optional named capture is present and the repeated yes-arm alternation takes its first `de` branch on both evaluations."
      ]
    },
    {
      "id": "module-subn-named-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
      "haystack": "zzabcdfdfzz",
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
        "alternation-heavy",
        "quantified",
        "replacement",
        "named-group",
        "subn",
        "module",
        "present",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "quantifiers"
      ],
      "notes": [
        "Warm module.subn helper path for the bounded named quantified alternation-heavy two-arm conditional replacement count workflow when the optional named capture is present and the repeated yes-arm alternation takes its second `df` branch on both evaluations."
      ]
    },
    {
      "id": "pattern-sub-named-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
      "haystack": "zzacegegzz",
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
        "alternation-heavy",
        "quantified",
        "replacement",
        "named-group",
        "sub",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.sub helper path for the bounded named quantified alternation-heavy two-arm conditional replacement workflow when the optional named capture is absent and the repeated else-arm alternation takes its first `eg` branch on both evaluations."
      ]
    },
    {
      "id": "pattern-subn-named-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
      "haystack": "zzacehehzz",
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
        "alternation-heavy",
        "quantified",
        "replacement",
        "named-group",
        "subn",
        "absent",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "optional-groups",
        "conditionals",
        "named-groups",
        "alternation",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.subn helper path for the bounded named quantified alternation-heavy two-arm conditional replacement count workflow when the optional named capture is absent and the repeated else-arm alternation takes its second `eh` branch on both evaluations."
      ]
    }
  ]
}
