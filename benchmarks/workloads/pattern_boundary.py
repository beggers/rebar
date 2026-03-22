MANIFEST = {
  "schema_version": 1,
  "manifest_id": "pattern-boundary",
  "spec_refs": [
    "docs/benchmarks/plan.md",
    "docs/spec/drop-in-re-compatibility.md"
  ],
  "notes": [
    "Phase 2 pattern-boundary workloads keep compilation outside the timed loop so the scorecard isolates precompiled Pattern helper overhead from module helper dispatch and parser cost.",
    "Cache labels describe the provenance of the precompiled pattern object, not large-haystack throughput or blended compile-plus-match behavior."
  ],
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "pattern-search-literal-warm-hit",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "abc",
      "haystack": "zzabczz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "smoke": True,
      "categories": [
        "pattern",
        "search",
        "literal",
        "warm-cache",
        "single-match",
        "smoke"
      ],
      "syntax_features": [
        "pattern-search",
        "literal-text"
      ],
      "notes": [
        "Warm precompiled search helper path over a tiny haystack so the timed loop stays focused on Pattern.search boundary cost."
      ]
    },
    {
      "id": "pattern-match-literal-warm-hit",
      "bucket": "pattern-match",
      "family": "module",
      "operation": "pattern.match",
      "pattern": "abc",
      "haystack": "abcdef",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "match",
        "literal",
        "warm-cache",
        "single-match"
      ],
      "syntax_features": [
        "pattern-match",
        "literal-text"
      ],
      "notes": [
        "Warm precompiled match helper path on a tiny prefix-match haystack."
      ]
    },
    {
      "id": "pattern-fullmatch-literal-purged-hit",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "abc",
      "haystack": "abc",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "fullmatch",
        "literal",
        "purged-cache",
        "single-match"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "literal-text",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache provenance check showing that a precompiled Pattern.fullmatch call still runs after module cache reset."
      ]
    },
    {
      "id": "pattern-search-bytes-purged-miss",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "abc",
      "haystack": "zzz",
      "flags": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "bytes",
        "purged-cache",
        "no-match"
      ],
      "syntax_features": [
        "pattern-search",
        "pattern-text-model",
        "cache-purge"
      ],
      "notes": [
        "Bytes precompiled search miss that keeps no-match behavior visible without turning into a throughput benchmark."
      ]
    },
    {
      "id": "pattern-match-bytes-warm-hit",
      "bucket": "pattern-match",
      "family": "module",
      "operation": "pattern.match",
      "pattern": "abc",
      "haystack": "abcdef",
      "flags": 0,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "match",
        "bytes",
        "warm-cache",
        "single-match"
      ],
      "syntax_features": [
        "pattern-match",
        "pattern-text-model"
      ],
      "notes": [
        "Bytes precompiled match helper path to keep text-model coverage visible in the pattern-boundary pack."
      ]
    },
    {
      "id": "pattern-fullmatch-bytes-purged-hit",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "abc",
      "haystack": "abc",
      "flags": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "smoke": True,
      "categories": [
        "pattern",
        "fullmatch",
        "bytes",
        "purged-cache",
        "single-match",
        "smoke"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "pattern-text-model",
        "cache-purge"
      ],
      "notes": [
        "Smoke-sized bytes fullmatch probe that keeps precompiled helper behavior and purge provenance easy to rerun."
      ]
    },
    {
      "id": "pattern-search-bounded-wildcard-ignorecase-warm-str",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "a.c",
      "haystack": "zaBczz",
      "flags": 2,
      "text_model": "str",
      "pos": 1,
      "endpos": 5,
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "wildcard",
        "bounded",
        "ignorecase",
        "warm-cache",
        "single-match"
      ],
      "syntax_features": [
        "pattern-search",
        "wildcard-single-dot",
        "ignorecase-flag"
      ],
      "notes": [
        "Warm precompiled Pattern.search helper path that keeps the bounded IGNORECASE single-dot windowed success row on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-match-bounded-wildcard-warm-str",
      "bucket": "pattern-match",
      "family": "module",
      "operation": "pattern.match",
      "pattern": "a.c",
      "haystack": "zabcaxc",
      "flags": 0,
      "text_model": "str",
      "pos": 1,
      "endpos": 4,
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "match",
        "wildcard",
        "bounded",
        "warm-cache",
        "single-match"
      ],
      "syntax_features": [
        "pattern-match",
        "wildcard-single-dot"
      ],
      "notes": [
        "Warm precompiled Pattern.match helper path that keeps the bounded single-dot windowed success row on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-fullmatch-bounded-wildcard-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "a.c",
      "haystack": "zaxcz",
      "flags": 0,
      "text_model": "str",
      "pos": 1,
      "endpos": 4,
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "fullmatch",
        "wildcard",
        "bounded",
        "purged-cache",
        "single-match"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "wildcard-single-dot",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch helper path that keeps the bounded single-dot windowed success row on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-findall-bounded-wildcard-warm-str",
      "bucket": "pattern-findall",
      "family": "module",
      "operation": "pattern.findall",
      "pattern": "a.c",
      "haystack": "zabcaxcz",
      "flags": 0,
      "text_model": "str",
      "pos": 1,
      "endpos": 7,
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "findall",
        "wildcard",
        "bounded",
        "warm-cache",
        "single-match"
      ],
      "syntax_features": [
        "pattern-findall",
        "wildcard-single-dot"
      ],
      "notes": [
        "Warm precompiled Pattern.findall helper path that keeps the bounded single-dot windowed success row on the shared pattern-boundary manifest."
      ]
    },
    {
      "id": "pattern-finditer-bounded-wildcard-purged-str",
      "bucket": "pattern-finditer",
      "family": "module",
      "operation": "pattern.finditer",
      "pattern": "a.c",
      "haystack": "zabcaxcx",
      "flags": 0,
      "text_model": "str",
      "pos": 1,
      "endpos": 7,
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "finditer",
        "wildcard",
        "bounded",
        "purged-cache",
        "single-match"
      ],
      "syntax_features": [
        "pattern-finditer",
        "wildcard-single-dot",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.finditer helper path that keeps the bounded single-dot windowed success row on the shared pattern-boundary manifest."
      ]
    },
    {
      "id": "pattern-search-bounded-wildcard-endpos-miss-purged-str",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "a.c",
      "haystack": "zabc",
      "flags": 0,
      "text_model": "str",
      "pos": 1,
      "endpos": 3,
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "wildcard",
        "bounded",
        "purged-cache",
        "no-match"
      ],
      "syntax_features": [
        "pattern-search",
        "wildcard-single-dot",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.search helper path that keeps the bounded single-dot endpos miss row on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-search-verbose-regression-warm-str",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "haystack": "prefix\nENV_VAR=ABCD\nsuffix",
      "flags": 72,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "verbose",
        "multiline",
        "warm-cache",
        "single-match"
      ],
      "syntax_features": [
        "pattern-search",
        "verbose-mode-tokenization",
        "flag-syntax",
        "quantifiers"
      ],
      "notes": [
        "Warm precompiled Pattern.search helper path that keeps the bounded verbose-regression success row on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-search-verbose-regression-digits-warm-str",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "haystack": "prefix\nENV_VAR = 123\nsuffix",
      "flags": 72,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "verbose",
        "multiline",
        "warm-cache",
        "single-match"
      ],
      "syntax_features": [
        "pattern-search",
        "verbose-mode-tokenization",
        "flag-syntax",
        "quantifiers"
      ],
      "notes": [
        "Warm precompiled Pattern.search helper path that keeps the bounded verbose-regression digit success row on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-search-verbose-regression-too-many-digits-purged-str",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "haystack": "prefix\nENV_VAR = 12345\nsuffix",
      "flags": 72,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "verbose",
        "multiline",
        "purged-cache",
        "no-match"
      ],
      "syntax_features": [
        "pattern-search",
        "verbose-mode-tokenization",
        "flag-syntax",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.search helper path that keeps the bounded verbose-regression too-many-digits miss row on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-search-verbose-regression-warm-bytes",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "haystack": "prefix\nENV_VAR=ABCD\nsuffix",
      "flags": 72,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "verbose",
        "multiline",
        "bytes",
        "warm-cache",
        "single-match"
      ],
      "syntax_features": [
        "pattern-search",
        "pattern-text-model",
        "verbose-mode-tokenization",
        "flag-syntax",
        "quantifiers"
      ],
      "notes": [
        "Warm bytes precompiled Pattern.search helper path that keeps the bounded verbose-regression success row on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-search-verbose-regression-digits-warm-bytes",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "haystack": "prefix\nENV_VAR = 123\nsuffix",
      "flags": 72,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "verbose",
        "multiline",
        "bytes",
        "warm-cache",
        "single-match"
      ],
      "syntax_features": [
        "pattern-search",
        "pattern-text-model",
        "verbose-mode-tokenization",
        "flag-syntax",
        "quantifiers"
      ],
      "notes": [
        "Warm bytes precompiled Pattern.search helper path that keeps the bounded verbose-regression digit success row on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-search-verbose-regression-too-many-digits-purged-bytes",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "haystack": "prefix\nENV_VAR = 12345\nsuffix",
      "flags": 72,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "verbose",
        "multiline",
        "bytes",
        "purged-cache",
        "no-match"
      ],
      "syntax_features": [
        "pattern-search",
        "pattern-text-model",
        "verbose-mode-tokenization",
        "flag-syntax",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.search helper path that keeps the bounded verbose-regression too-many-digits miss row on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-fullmatch-verbose-regression-warm-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "haystack": "ENV_VAR = 123",
      "flags": 72,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "fullmatch",
        "verbose",
        "multiline",
        "warm-cache",
        "single-match"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "verbose-mode-tokenization",
        "flag-syntax",
        "quantifiers"
      ],
      "notes": [
        "Warm precompiled Pattern.fullmatch helper path that keeps the bounded verbose-regression digit success row on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-fullmatch-verbose-regression-alpha-warm-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "haystack": "ENV_VAR   =   ABCD",
      "flags": 72,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "fullmatch",
        "verbose",
        "multiline",
        "warm-cache",
        "single-match"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "verbose-mode-tokenization",
        "flag-syntax",
        "quantifiers"
      ],
      "notes": [
        "Warm precompiled Pattern.fullmatch helper path that keeps the bounded verbose-regression alpha success row on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-fullmatch-verbose-regression-lowercase-key-purged-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "haystack": "env_var = 123",
      "flags": 72,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "fullmatch",
        "verbose",
        "multiline",
        "purged-cache",
        "no-match"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "verbose-mode-tokenization",
        "flag-syntax",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.fullmatch helper path that keeps the bounded verbose-regression lowercase-key miss row on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-fullmatch-verbose-regression-warm-bytes",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "haystack": "ENV_VAR = 123",
      "flags": 72,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "fullmatch",
        "verbose",
        "multiline",
        "bytes",
        "warm-cache",
        "single-match"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "pattern-text-model",
        "verbose-mode-tokenization",
        "flag-syntax",
        "quantifiers"
      ],
      "notes": [
        "Warm precompiled bytes Pattern.fullmatch helper path that keeps the bounded verbose-regression digit success row on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-fullmatch-verbose-regression-alpha-warm-bytes",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "haystack": "ENV_VAR   =   ABCD",
      "flags": 72,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "fullmatch",
        "verbose",
        "multiline",
        "bytes",
        "warm-cache",
        "single-match"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "pattern-text-model",
        "verbose-mode-tokenization",
        "flag-syntax",
        "quantifiers"
      ],
      "notes": [
        "Warm precompiled bytes Pattern.fullmatch helper path that keeps the bounded verbose-regression alpha success row on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-fullmatch-verbose-regression-lowercase-key-purged-bytes",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "haystack": "env_var = 123",
      "flags": 72,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "fullmatch",
        "verbose",
        "multiline",
        "bytes",
        "purged-cache",
        "no-match"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "pattern-text-model",
        "verbose-mode-tokenization",
        "flag-syntax",
        "quantifiers",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.fullmatch helper path that keeps the bounded verbose-regression lowercase-key miss row on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-search-on-bytes-string-warm-str",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "abc",
      "haystack": "abc",
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "cannot use a string pattern on a bytes-like object"
      },
      "flags": 0,
      "text_model": "str",
      "haystack_text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "literal",
        "wrong-text-model",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-search",
        "literal-text",
        "wrong-text-model"
      ],
      "notes": [
        "Warm precompiled Pattern.search helper path that keeps the bounded wrong-text-model TypeError on bytes haystacks on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-match-on-str-string-purged-bytes",
      "bucket": "pattern-match",
      "family": "module",
      "operation": "pattern.match",
      "pattern": "abc",
      "haystack": "abc",
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "cannot use a bytes pattern on a string-like object"
      },
      "flags": 0,
      "text_model": "bytes",
      "haystack_text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "match",
        "bytes",
        "wrong-text-model",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-match",
        "pattern-text-model",
        "wrong-text-model",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes Pattern.match helper path that keeps the bounded wrong-text-model TypeError on str haystacks on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-fullmatch-on-bytes-string-warm-str",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "abc",
      "haystack": "abc",
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "cannot use a string pattern on a bytes-like object"
      },
      "flags": 0,
      "text_model": "str",
      "haystack_text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "fullmatch",
        "literal",
        "wrong-text-model",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "literal-text",
        "wrong-text-model"
      ],
      "notes": [
        "Warm precompiled Pattern.fullmatch helper path that keeps the bounded wrong-text-model TypeError on bytes haystacks on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-search-pos-keyword-warm-str",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "abc",
      "haystack": "zabcabc",
      "flags": 0,
      "kwargs": {
        "pos": 2
      },
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "literal",
        "warm-cache",
        "keyword",
        "pos",
        "single-match"
      ],
      "syntax_features": [
        "pattern-search",
        "literal-text",
        "pattern-window-pos"
      ],
      "notes": [
        "Warm precompiled search helper path that keeps the Pattern.search pos= keyword carrier on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-search-bool-endpos-keyword-warm-str",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "z",
      "haystack": "zabcabc",
      "flags": 0,
      "text_model": "str",
      "kwargs": {
        "endpos": True
      },
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "literal",
        "warm-cache",
        "keyword",
        "endpos",
        "bool",
        "single-match"
      ],
      "syntax_features": [
        "pattern-search",
        "literal-text",
        "pattern-window-endpos"
      ],
      "notes": [
        "Warm precompiled search helper path that keeps the bool-backed Pattern.search endpos= keyword carrier on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-search-endpos-keyword-purged-bytes",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "abc",
      "haystack": "zabcabc",
      "flags": 0,
      "text_model": "bytes",
      "kwargs": {
        "endpos": 4
      },
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "bytes",
        "purged-cache",
        "keyword",
        "endpos",
        "single-match"
      ],
      "syntax_features": [
        "pattern-search",
        "pattern-text-model",
        "pattern-window-endpos",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes search helper path that keeps the Pattern.search endpos= keyword carrier on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-search-pos-indexlike-keyword-warm-str",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "abc",
      "haystack": "zabcabc",
      "flags": 0,
      "text_model": "str",
      "kwargs": {
        "pos": {
          "type": "indexlike",
          "value": 2
        }
      },
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "literal",
        "warm-cache",
        "keyword",
        "pos",
        "indexlike",
        "single-match"
      ],
      "syntax_features": [
        "pattern-search",
        "literal-text",
        "pattern-window-pos"
      ],
      "notes": [
        "Warm precompiled search helper path that keeps the Pattern.search pos= __index__ keyword carrier on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-search-endpos-indexlike-keyword-purged-bytes",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "abc",
      "haystack": "zabcabc",
      "flags": 0,
      "text_model": "bytes",
      "kwargs": {
        "endpos": {
          "type": "indexlike",
          "value": 4
        }
      },
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "bytes",
        "purged-cache",
        "keyword",
        "endpos",
        "indexlike",
        "single-match"
      ],
      "syntax_features": [
        "pattern-search",
        "pattern-text-model",
        "pattern-window-endpos",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes search helper path that keeps the Pattern.search endpos= __index__ keyword carrier on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-match-pos-keyword-purged-str",
      "bucket": "pattern-match",
      "family": "module",
      "operation": "pattern.match",
      "pattern": "abc",
      "haystack": "zabcabc",
      "flags": 0,
      "kwargs": {
        "pos": 1
      },
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "match",
        "literal",
        "purged-cache",
        "keyword",
        "pos",
        "single-match"
      ],
      "syntax_features": [
        "pattern-match",
        "literal-text",
        "pattern-window-pos",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache match helper path that keeps the Pattern.match pos= keyword carrier on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-match-bool-pos-keyword-purged-str",
      "bucket": "pattern-match",
      "family": "module",
      "operation": "pattern.match",
      "pattern": "abc",
      "haystack": "zabcabc",
      "flags": 0,
      "text_model": "str",
      "kwargs": {
        "pos": True
      },
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "match",
        "literal",
        "purged-cache",
        "keyword",
        "pos",
        "bool",
        "single-match"
      ],
      "syntax_features": [
        "pattern-match",
        "literal-text",
        "pattern-window-pos",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache match helper path that keeps the bool-backed Pattern.match pos= keyword carrier on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-match-window-indexlike-purged-bytes",
      "bucket": "pattern-match",
      "family": "module",
      "operation": "pattern.match",
      "pattern": "abc",
      "haystack": "zabc",
      "flags": 0,
      "text_model": "bytes",
      "kwargs": {
        "pos": {
          "type": "indexlike",
          "value": 1
        },
        "endpos": {
          "type": "indexlike",
          "value": 4
        }
      },
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "match",
        "bytes",
        "purged-cache",
        "keyword",
        "window",
        "indexlike",
        "single-match"
      ],
      "syntax_features": [
        "pattern-match",
        "pattern-text-model",
        "pattern-window-pos",
        "pattern-window-endpos",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes match helper path that keeps the Pattern.match pos=/endpos= __index__ keyword carriers on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-fullmatch-window-keyword-purged-bytes",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "abc",
      "haystack": "zabc",
      "flags": 0,
      "text_model": "bytes",
      "kwargs": {
        "pos": 1,
        "endpos": 4
      },
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "fullmatch",
        "bytes",
        "purged-cache",
        "keyword",
        "window",
        "single-match"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "pattern-text-model",
        "pattern-window-pos",
        "pattern-window-endpos",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes fullmatch helper path that keeps the Pattern.fullmatch pos=/endpos= keyword carriers on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-fullmatch-window-indexlike-keyword-purged-bytes",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "abc",
      "haystack": "zabc",
      "flags": 0,
      "text_model": "bytes",
      "kwargs": {
        "pos": {
          "type": "indexlike",
          "value": 1
        },
        "endpos": {
          "type": "indexlike",
          "value": 4
        }
      },
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "fullmatch",
        "bytes",
        "purged-cache",
        "keyword",
        "window",
        "indexlike",
        "single-match"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "pattern-text-model",
        "pattern-window-pos",
        "pattern-window-endpos",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes fullmatch helper path that keeps the Pattern.fullmatch pos=/endpos= __index__ keyword carriers on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-findall-window-keyword-warm-str",
      "bucket": "pattern-findall",
      "family": "module",
      "operation": "pattern.findall",
      "pattern": "abc",
      "haystack": "zabcabcz",
      "flags": 0,
      "kwargs": {
        "pos": 1,
        "endpos": 7
      },
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "findall",
        "literal",
        "warm-cache",
        "keyword",
        "window",
        "collection"
      ],
      "syntax_features": [
        "pattern-findall",
        "literal-text",
        "pattern-window-pos",
        "pattern-window-endpos"
      ],
      "notes": [
        "Warm precompiled findall helper path that keeps the Pattern.findall pos=/endpos= keyword carriers on the shared pattern-boundary manifest."
      ]
    },
    {
      "id": "pattern-findall-window-indexlike-keyword-warm-str",
      "bucket": "pattern-findall",
      "family": "module",
      "operation": "pattern.findall",
      "pattern": "abc",
      "haystack": "zabcabcabcz",
      "flags": 0,
      "kwargs": {
        "pos": {
          "type": "indexlike",
          "value": 1
        },
        "endpos": {
          "type": "indexlike",
          "value": 7
        }
      },
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "findall",
        "literal",
        "warm-cache",
        "keyword",
        "window",
        "indexlike",
        "collection"
      ],
      "syntax_features": [
        "pattern-findall",
        "literal-text",
        "pattern-window-pos",
        "pattern-window-endpos"
      ],
      "notes": [
        "Warm precompiled findall helper path that keeps the Pattern.findall pos=/endpos= __index__ keyword carriers on the shared pattern-boundary manifest."
      ]
    },
    {
      "id": "pattern-findall-bool-window-keyword-warm-str",
      "bucket": "pattern-findall",
      "family": "module",
      "operation": "pattern.findall",
      "pattern": "abc",
      "haystack": "zabcabcz",
      "flags": 0,
      "kwargs": {
        "pos": True,
        "endpos": 7
      },
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "findall",
        "literal",
        "warm-cache",
        "keyword",
        "window",
        "bool",
        "collection"
      ],
      "syntax_features": [
        "pattern-findall",
        "literal-text",
        "pattern-window-pos",
        "pattern-window-endpos"
      ],
      "notes": [
        "Warm precompiled findall helper path that keeps the bool-backed Pattern.findall pos=/endpos= keyword carriers on the shared pattern-boundary manifest."
      ]
    },
    {
      "id": "pattern-finditer-window-keyword-purged-bytes",
      "bucket": "pattern-finditer",
      "family": "module",
      "operation": "pattern.finditer",
      "pattern": "abc",
      "haystack": "zabcabcz",
      "flags": 0,
      "text_model": "bytes",
      "kwargs": {
        "pos": 1,
        "endpos": 7
      },
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "finditer",
        "bytes",
        "purged-cache",
        "keyword",
        "window",
        "single-match"
      ],
      "syntax_features": [
        "pattern-finditer",
        "pattern-text-model",
        "pattern-window-pos",
        "pattern-window-endpos",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes finditer helper path that keeps the Pattern.finditer pos=/endpos= keyword carriers on the shared pattern-boundary manifest."
      ]
    },
    {
      "id": "pattern-finditer-window-indexlike-purged-bytes",
      "bucket": "pattern-finditer",
      "family": "module",
      "operation": "pattern.finditer",
      "pattern": "abc",
      "haystack": "zabcabcabcz",
      "flags": 0,
      "text_model": "bytes",
      "kwargs": {
        "pos": {
          "type": "indexlike",
          "value": 1
        },
        "endpos": {
          "type": "indexlike",
          "value": 7
        }
      },
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "finditer",
        "bytes",
        "purged-cache",
        "keyword",
        "window",
        "indexlike",
        "single-match"
      ],
      "syntax_features": [
        "pattern-finditer",
        "pattern-text-model",
        "pattern-window-pos",
        "pattern-window-endpos",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes finditer helper path that keeps the Pattern.finditer pos=/endpos= __index__ keyword carriers on the shared pattern-boundary manifest."
      ]
    },
    {
      "id": "pattern-finditer-bool-window-keyword-purged-bytes",
      "bucket": "pattern-finditer",
      "family": "module",
      "operation": "pattern.finditer",
      "pattern": "abc",
      "haystack": "zabcabcz",
      "flags": 0,
      "text_model": "bytes",
      "kwargs": {
        "pos": True,
        "endpos": 7
      },
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "finditer",
        "bytes",
        "purged-cache",
        "keyword",
        "window",
        "bool",
        "single-match"
      ],
      "syntax_features": [
        "pattern-finditer",
        "pattern-text-model",
        "pattern-window-pos",
        "pattern-window-endpos",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes finditer helper path that keeps the bool-backed Pattern.finditer pos=/endpos= keyword carriers on the shared pattern-boundary manifest."
      ]
    },
    {
      "id": "pattern-search-pos-indexlike-positional-warm-str",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "abc",
      "haystack": "zabcabc",
      "flags": 0,
      "pos": {
        "type": "indexlike",
        "value": 2
      },
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "literal",
        "warm-cache",
        "positional-window",
        "indexlike",
        "single-match"
      ],
      "syntax_features": [
        "pattern-search",
        "literal-text",
        "pattern-window-pos"
      ],
      "notes": [
        "Warm precompiled search helper path that keeps the Pattern.search positional __index__ boundary on the shared pattern-boundary surface."
      ]
    },
    {
      "id": "pattern-search-endpos-indexlike-positional-purged-bytes",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "abc",
      "haystack": "zabcabc",
      "flags": 0,
      "pos": 0,
      "endpos": {
        "type": "indexlike",
        "value": 4
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "search",
        "bytes",
        "purged-cache",
        "positional-window",
        "indexlike",
        "single-match"
      ],
      "syntax_features": [
        "pattern-search",
        "pattern-text-model",
        "pattern-window-endpos",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes search helper path that keeps endpos-backed positional __index__ timing on the shared Pattern.search benchmark surface."
      ]
    },
    {
      "id": "pattern-match-window-indexlike-positional-purged-bytes",
      "bucket": "pattern-match",
      "family": "module",
      "operation": "pattern.match",
      "pattern": "abc",
      "haystack": "zabc",
      "flags": 0,
      "pos": {
        "type": "indexlike",
        "value": 1
      },
      "endpos": {
        "type": "indexlike",
        "value": 4
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "match",
        "bytes",
        "purged-cache",
        "positional-window",
        "indexlike",
        "single-match"
      ],
      "syntax_features": [
        "pattern-match",
        "pattern-text-model",
        "pattern-window-pos",
        "pattern-window-endpos",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes match helper path that keeps Pattern.match positional pos/endpos __index__ timing on the shared boundary surface."
      ]
    },
    {
      "id": "pattern-fullmatch-window-indexlike-positional-purged-bytes",
      "bucket": "pattern-fullmatch",
      "family": "module",
      "operation": "pattern.fullmatch",
      "pattern": "abc",
      "haystack": "zabc",
      "flags": 0,
      "pos": {
        "type": "indexlike",
        "value": 1
      },
      "endpos": {
        "type": "indexlike",
        "value": 4
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "fullmatch",
        "bytes",
        "purged-cache",
        "positional-window",
        "indexlike",
        "single-match"
      ],
      "syntax_features": [
        "pattern-fullmatch",
        "pattern-text-model",
        "pattern-window-pos",
        "pattern-window-endpos",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes fullmatch helper path that keeps Pattern.fullmatch positional pos/endpos __index__ timing on the shared boundary surface."
      ]
    },
    {
      "id": "pattern-findall-window-indexlike-positional-warm-str",
      "bucket": "pattern-findall",
      "family": "module",
      "operation": "pattern.findall",
      "pattern": "abc",
      "haystack": "zabcabcabcz",
      "flags": 0,
      "pos": {
        "type": "indexlike",
        "value": 1
      },
      "endpos": {
        "type": "indexlike",
        "value": 7
      },
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "findall",
        "literal",
        "warm-cache",
        "positional-window",
        "indexlike",
        "collection"
      ],
      "syntax_features": [
        "pattern-findall",
        "literal-text",
        "pattern-window-pos",
        "pattern-window-endpos"
      ],
      "notes": [
        "Warm precompiled findall helper path that keeps Pattern.findall positional pos/endpos __index__ timing on the shared pattern-boundary manifest."
      ]
    },
    {
      "id": "pattern-finditer-window-indexlike-positional-purged-bytes",
      "bucket": "pattern-finditer",
      "family": "module",
      "operation": "pattern.finditer",
      "pattern": "abc",
      "haystack": "zabcabcabcz",
      "flags": 0,
      "pos": {
        "type": "indexlike",
        "value": 1
      },
      "endpos": {
        "type": "indexlike",
        "value": 7
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "finditer",
        "bytes",
        "purged-cache",
        "positional-window",
        "indexlike",
        "single-match"
      ],
      "syntax_features": [
        "pattern-finditer",
        "pattern-text-model",
        "pattern-window-pos",
        "pattern-window-endpos",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes finditer helper path that keeps Pattern.finditer positional pos/endpos __index__ timing on the shared pattern-boundary manifest."
      ]
    }
  ]
}
