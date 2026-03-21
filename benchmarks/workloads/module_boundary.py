MANIFEST = {
  "schema_version": 1,
  "manifest_id": "module-boundary",
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "import-module-cold",
      "bucket": "import",
      "family": "module",
      "operation": "import",
      "cache_mode": "cold",
      "timing_scope": "module-import",
      "text_model": "str",
      "categories": [
        "import",
        "cold-cache"
      ],
      "syntax_features": [
        "module-import"
      ],
      "notes": [
        "Cold import proxy that clears the target package from sys.modules before each sample."
      ]
    },
    {
      "id": "module-compile-literal-cold",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "^abc$",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "literal",
        "cold-cache"
      ],
      "syntax_features": [
        "module-compile",
        "literal-text"
      ],
      "notes": [
        "Cold module-level compile on a tiny literal to expose helper overhead above the parser proxy path."
      ]
    },
    {
      "id": "module-compile-literal-warm",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "^abc$",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "literal",
        "warm-cache"
      ],
      "syntax_features": [
        "module-compile",
        "literal-text"
      ],
      "notes": [
        "Warm module-level compile path after priming the cache with the same tiny literal."
      ]
    },
    {
      "id": "module-compile-literal-purged",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "^abc$",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "literal",
        "purged-cache"
      ],
      "syntax_features": [
        "module-compile",
        "literal-text",
        "cache-purge"
      ],
      "notes": [
        "Purged module-level compile path that forces cache reset around each sample."
      ]
    },
    {
      "id": "module-compile-literal-warm-str-compiled-pattern",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "literal",
        "warm-cache",
        "compiled-pattern"
      ],
      "syntax_features": [
        "module-compile",
        "literal-text",
        "compiled-pattern-first-argument"
      ],
      "notes": [
        "Warm module.compile helper path that keeps the bounded compiled-pattern-first-argument literal str success row on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-compile-literal-purged-bytes-compiled-pattern",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "literal",
        "purged-cache",
        "compiled-pattern",
        "bytes"
      ],
      "syntax_features": [
        "module-compile",
        "literal-text",
        "compiled-pattern-first-argument",
        "cache-purge"
      ],
      "notes": [
        "Purged module.compile helper path that keeps the bounded compiled-pattern-first-argument literal bytes success row on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-compile-named-group-warm-str-compiled-pattern",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "(?P<word>abc)",
      "flags": 0,
      "use_compiled_pattern": True,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "named-group",
        "warm-cache",
        "compiled-pattern"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "named-groups",
        "compiled-pattern-first-argument"
      ],
      "notes": [
        "Warm module.compile helper path that keeps the bounded compiled-pattern-first-argument named-group str success row on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-compile-named-group-purged-bytes-compiled-pattern",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "(?P<word>abc)",
      "flags": 0,
      "use_compiled_pattern": True,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "named-group",
        "purged-cache",
        "compiled-pattern",
        "bytes"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "named-groups",
        "compiled-pattern-first-argument",
        "cache-purge"
      ],
      "notes": [
        "Purged module.compile helper path that keeps the bounded compiled-pattern-first-argument named-group bytes success row on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-compile-flags-int-zero-warm-str-compiled-pattern-named-group",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "(?P<word>abc)",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": 0
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "named-group",
        "warm-cache",
        "compiled-pattern",
        "keyword",
        "flags"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "named-groups",
        "compiled-pattern-first-argument",
        "keyword-flags"
      ],
      "notes": [
        "Warm module.compile helper path that keeps the bounded compiled-pattern-first-argument named-group explicit integer-zero flags= keyword carrier on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "(?P<word>abc)",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": 0
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "named-group",
        "purged-cache",
        "compiled-pattern",
        "bytes",
        "keyword",
        "flags"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "named-groups",
        "compiled-pattern-first-argument",
        "keyword-flags",
        "cache-purge"
      ],
      "notes": [
        "Purged module.compile helper path that keeps the bounded compiled-pattern-first-argument named-group explicit integer-zero flags= keyword carrier on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-compile-flags-bool-false-warm-str-compiled-pattern-named-group",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "(?P<word>abc)",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": False
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "named-group",
        "warm-cache",
        "compiled-pattern",
        "keyword",
        "flags",
        "bool"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "named-groups",
        "compiled-pattern-first-argument",
        "keyword-flags"
      ],
      "notes": [
        "Warm module.compile helper path that keeps the bounded compiled-pattern-first-argument named-group explicit bool-false flags= keyword carrier on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "(?P<word>abc)",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": False
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "named-group",
        "purged-cache",
        "compiled-pattern",
        "bytes",
        "keyword",
        "flags",
        "bool"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "named-groups",
        "compiled-pattern-first-argument",
        "keyword-flags",
        "cache-purge"
      ],
      "notes": [
        "Purged module.compile helper path that keeps the bounded compiled-pattern-first-argument named-group explicit bool-false flags= keyword carrier on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-compile-flags-int-zero-warm-str-compiled-pattern",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": 0
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "literal",
        "warm-cache",
        "compiled-pattern",
        "keyword",
        "flags"
      ],
      "syntax_features": [
        "module-compile",
        "literal-text",
        "compiled-pattern-first-argument",
        "keyword-flags"
      ],
      "notes": [
        "Warm module.compile helper path that keeps the bounded compiled-pattern-first-argument explicit integer-zero flags= keyword carrier on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-compile-flags-int-zero-purged-bytes-compiled-pattern",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": 0
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "literal",
        "purged-cache",
        "compiled-pattern",
        "bytes",
        "keyword",
        "flags"
      ],
      "syntax_features": [
        "module-compile",
        "literal-text",
        "compiled-pattern-first-argument",
        "keyword-flags",
        "cache-purge"
      ],
      "notes": [
        "Purged module.compile helper path that keeps the bounded compiled-pattern-first-argument explicit integer-zero flags= keyword carrier on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-compile-flags-bool-false-warm-str-compiled-pattern",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": False
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "literal",
        "warm-cache",
        "compiled-pattern",
        "keyword",
        "flags",
        "bool"
      ],
      "syntax_features": [
        "module-compile",
        "literal-text",
        "compiled-pattern-first-argument",
        "keyword-flags"
      ],
      "notes": [
        "Warm module.compile helper path that keeps the bounded compiled-pattern-first-argument explicit bool-false flags= keyword carrier on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-compile-flags-bool-false-purged-bytes-compiled-pattern",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": False
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "literal",
        "purged-cache",
        "compiled-pattern",
        "bytes",
        "keyword",
        "flags",
        "bool"
      ],
      "syntax_features": [
        "module-compile",
        "literal-text",
        "compiled-pattern-first-argument",
        "keyword-flags",
        "cache-purge"
      ],
      "notes": [
        "Purged module.compile helper path that keeps the bounded compiled-pattern-first-argument explicit bool-false flags= keyword carrier on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-compile-flags-ignorecase-warm-str-compiled-pattern",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "abc",
      "expected_exception": {
        "type": "ValueError",
        "message_substring": "cannot process flags argument with a compiled pattern"
      },
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": 2
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "literal",
        "warm-cache",
        "compiled-pattern",
        "keyword",
        "flags",
        "ignorecase",
        "exception"
      ],
      "syntax_features": [
        "module-compile",
        "literal-text",
        "compiled-pattern-first-argument",
        "keyword-flags",
        "ignorecase-flag"
      ],
      "notes": [
        "Warm module.compile helper path that keeps the bounded compiled-pattern-first-argument explicit IGNORECASE flags= rejection on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-compile-flags-ignorecase-purged-bytes-compiled-pattern",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "abc",
      "expected_exception": {
        "type": "ValueError",
        "message_substring": "cannot process flags argument with a compiled pattern"
      },
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": 2
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "literal",
        "purged-cache",
        "compiled-pattern",
        "bytes",
        "keyword",
        "flags",
        "ignorecase",
        "exception"
      ],
      "syntax_features": [
        "module-compile",
        "literal-text",
        "compiled-pattern-first-argument",
        "keyword-flags",
        "ignorecase-flag",
        "cache-purge"
      ],
      "notes": [
        "Purged module.compile helper path that keeps the bounded compiled-pattern-first-argument explicit IGNORECASE flags= rejection on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-search-literal-warm-hit",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "abc",
      "haystack": "zzabczz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "search",
        "warm-cache",
        "single-match"
      ],
      "syntax_features": [
        "module-search",
        "literal-text"
      ],
      "notes": [
        "Warm search helper path with a tiny single-match haystack so timing stays near boundary overhead."
      ]
    },
    {
      "id": "module-search-literal-warm-hit-str-compiled-pattern",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "abc",
      "haystack": "zabczz",
      "flags": 0,
      "use_compiled_pattern": True,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "search",
        "literal",
        "warm-cache",
        "compiled-pattern",
        "single-match"
      ],
      "syntax_features": [
        "module-search",
        "literal-text",
        "compiled-pattern-first-argument"
      ],
      "notes": [
        "Warm module.search helper path that keeps the bounded compiled-pattern-first-argument success row on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "a.c",
      "haystack": "ABC",
      "flags": 2,
      "use_compiled_pattern": True,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "search",
        "wildcard",
        "bounded",
        "ignorecase",
        "warm-cache",
        "compiled-pattern",
        "single-match"
      ],
      "syntax_features": [
        "module-search",
        "wildcard-single-dot",
        "compiled-pattern-first-argument",
        "ignorecase-flag"
      ],
      "notes": [
        "Warm module.search helper path that keeps the bounded compiled-pattern-first-argument IGNORECASE single-dot success row on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-search-verbose-regression-warm-hit-bytes-compiled-pattern",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "haystack": "prefix\nENV_VAR=ABCD\nsuffix",
      "flags": 72,
      "use_compiled_pattern": True,
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "search",
        "verbose",
        "multiline",
        "bytes",
        "warm-cache",
        "compiled-pattern",
        "single-match"
      ],
      "syntax_features": [
        "module-search",
        "pattern-text-model",
        "verbose-mode-tokenization",
        "flag-syntax",
        "quantifiers",
        "compiled-pattern-first-argument"
      ],
      "notes": [
        "Warm bytes module.search helper path that keeps the bounded compiled-pattern-first-argument verbose-regression success row on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-search-flags-keyword-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "abc",
      "haystack": "zAbc",
      "kwargs": {
        "flags": 2
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "search",
        "literal",
        "warm-cache",
        "keyword",
        "flags",
        "single-match"
      ],
      "syntax_features": [
        "module-search",
        "literal-text",
        "keyword-flags"
      ],
      "notes": [
        "Warm module.search helper path that keeps the bounded flags= keyword carrier on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-search-duplicate-flags-keyword-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "abc",
      "haystack": "abc",
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "multiple values for argument 'flags'"
      },
      "flags": 0,
      "kwargs": {
        "flags": 0
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "search",
        "literal",
        "warm-cache",
        "keyword",
        "flags",
        "duplicate-keyword",
        "exception"
      ],
      "syntax_features": [
        "module-search",
        "literal-text",
        "keyword-flags"
      ],
      "notes": [
        "Warm module.search helper path that keeps the raw positional-plus-keyword flags= duplicate TypeError on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-search-grouped-literal-cold-hit",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "(abc)",
      "haystack": "zzabczz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "search",
        "grouped",
        "cold-cache",
        "single-match"
      ],
      "syntax_features": [
        "module-search",
        "literal-text",
        "grouping-forms"
      ],
      "notes": [
        "Cold grouped-literal module.search helper path so the post-parser capture-aware workflow reaches the benchmark surface."
      ]
    },
    {
      "id": "module-search-on-bytes-string-warm-str-compiled-pattern",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "abc",
      "haystack": "abc",
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "cannot use a string pattern on a bytes-like object"
      },
      "flags": 0,
      "use_compiled_pattern": True,
      "text_model": "str",
      "haystack_text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "search",
        "literal",
        "warm-cache",
        "compiled-pattern",
        "wrong-text-model",
        "exception"
      ],
      "syntax_features": [
        "module-search",
        "literal-text",
        "compiled-pattern-first-argument"
      ],
      "notes": [
        "Warm module.search helper path that keeps the bounded compiled-pattern-first-argument wrong-text-model TypeError on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-match-literal-warm-hit",
      "bucket": "module-match",
      "family": "module",
      "operation": "module.match",
      "pattern": "abc",
      "haystack": "abcdef",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "match",
        "warm-cache",
        "single-match"
      ],
      "syntax_features": [
        "module-match",
        "literal-text"
      ],
      "notes": [
        "Warm match helper path over a tiny prefix-match haystack."
      ]
    },
    {
      "id": "module-match-literal-warm-hit-str-compiled-pattern",
      "bucket": "module-match",
      "family": "module",
      "operation": "module.match",
      "pattern": "abc",
      "haystack": "abcdef",
      "flags": 0,
      "use_compiled_pattern": True,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "match",
        "literal",
        "warm-cache",
        "compiled-pattern",
        "single-match"
      ],
      "syntax_features": [
        "module-match",
        "literal-text",
        "compiled-pattern-first-argument"
      ],
      "notes": [
        "Warm module.match helper path that keeps the bounded compiled-pattern-first-argument success row on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-match-bounded-wildcard-warm-hit-str-compiled-pattern",
      "bucket": "module-match",
      "family": "module",
      "operation": "module.match",
      "pattern": "a.c",
      "haystack": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "match",
        "wildcard",
        "bounded",
        "warm-cache",
        "compiled-pattern",
        "single-match"
      ],
      "syntax_features": [
        "module-match",
        "wildcard-single-dot",
        "compiled-pattern-first-argument"
      ],
      "notes": [
        "Warm module.match helper path that keeps the bounded compiled-pattern-first-argument single-dot success row on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-match-flags-keyword-purged-bytes",
      "bucket": "module-match",
      "family": "module",
      "operation": "module.match",
      "pattern": "abc",
      "haystack": "Abc",
      "kwargs": {
        "flags": 2
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "match",
        "bytes",
        "purged-cache",
        "keyword",
        "flags",
        "single-match"
      ],
      "syntax_features": [
        "module-match",
        "pattern-text-model",
        "keyword-flags",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes module.match helper path that keeps the bounded flags= keyword carrier on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-match-on-str-string-purged-bytes-compiled-pattern",
      "bucket": "module-match",
      "family": "module",
      "operation": "module.match",
      "pattern": "abc",
      "haystack": "abc",
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "cannot use a bytes pattern on a string-like object"
      },
      "flags": 0,
      "use_compiled_pattern": True,
      "text_model": "bytes",
      "haystack_text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "match",
        "bytes",
        "purged-cache",
        "compiled-pattern",
        "wrong-text-model",
        "exception"
      ],
      "syntax_features": [
        "module-match",
        "pattern-text-model",
        "compiled-pattern-first-argument",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache module.match helper path that keeps the bounded compiled-pattern-first-argument wrong-text-model TypeError on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-fullmatch-literal-purged-hit-bytes-compiled-pattern",
      "bucket": "module-fullmatch",
      "family": "module",
      "operation": "module.fullmatch",
      "pattern": "abc",
      "haystack": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "fullmatch",
        "bytes",
        "purged-cache",
        "compiled-pattern",
        "single-match"
      ],
      "syntax_features": [
        "module-fullmatch",
        "pattern-text-model",
        "compiled-pattern-first-argument",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache module.fullmatch helper path that keeps the bounded compiled-pattern-first-argument success row on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern",
      "bucket": "module-fullmatch",
      "family": "module",
      "operation": "module.fullmatch",
      "pattern": "a.c",
      "haystack": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "fullmatch",
        "wildcard",
        "bounded",
        "purged-cache",
        "compiled-pattern",
        "single-match"
      ],
      "syntax_features": [
        "module-fullmatch",
        "wildcard-single-dot",
        "compiled-pattern-first-argument",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache module.fullmatch helper path that keeps the bounded compiled-pattern-first-argument single-dot success row on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern",
      "bucket": "module-fullmatch",
      "family": "module",
      "operation": "module.fullmatch",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "haystack": "ENV_VAR = 123",
      "flags": 72,
      "use_compiled_pattern": True,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "fullmatch",
        "verbose",
        "multiline",
        "bytes",
        "purged-cache",
        "compiled-pattern",
        "single-match"
      ],
      "syntax_features": [
        "module-fullmatch",
        "pattern-text-model",
        "verbose-mode-tokenization",
        "flag-syntax",
        "quantifiers",
        "compiled-pattern-first-argument",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache bytes module.fullmatch helper path that keeps the bounded compiled-pattern-first-argument verbose-regression success row on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-fullmatch-flags-keyword-warm-str",
      "bucket": "module-fullmatch",
      "family": "module",
      "operation": "module.fullmatch",
      "pattern": "abc",
      "haystack": "Abc",
      "kwargs": {
        "flags": 2
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "fullmatch",
        "literal",
        "warm-cache",
        "keyword",
        "flags",
        "single-match"
      ],
      "syntax_features": [
        "module-fullmatch",
        "literal-text",
        "keyword-flags"
      ],
      "notes": [
        "Warm module.fullmatch helper path that keeps the bounded flags= keyword carrier on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-fullmatch-unexpected-keyword-purged-str",
      "bucket": "module-fullmatch",
      "family": "module",
      "operation": "module.fullmatch",
      "pattern": "abc",
      "haystack": "abc",
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "unexpected keyword argument 'missing'"
      },
      "flags": 0,
      "kwargs": {
        "missing": 1
      },
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "fullmatch",
        "literal",
        "purged-cache",
        "keyword",
        "unexpected-keyword",
        "exception"
      ],
      "syntax_features": [
        "module-fullmatch",
        "literal-text",
        "keyword-errors",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache module.fullmatch helper path that keeps the raw unexpected keyword TypeError on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-fullmatch-on-bytes-string-warm-str-compiled-pattern",
      "bucket": "module-fullmatch",
      "family": "module",
      "operation": "module.fullmatch",
      "pattern": "abc",
      "haystack": "abc",
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "cannot use a string pattern on a bytes-like object"
      },
      "flags": 0,
      "use_compiled_pattern": True,
      "text_model": "str",
      "haystack_text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "fullmatch",
        "literal",
        "warm-cache",
        "compiled-pattern",
        "wrong-text-model",
        "exception"
      ],
      "syntax_features": [
        "module-fullmatch",
        "literal-text",
        "compiled-pattern-first-argument"
      ],
      "notes": [
        "Warm module.fullmatch helper path that keeps the bounded compiled-pattern-first-argument wrong-text-model TypeError on the shared module-boundary surface."
      ]
    },
    {
      "id": "module-search-bytes-cold-miss",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "abc",
      "haystack": "zzz",
      "flags": 0,
      "text_model": "bytes",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "search",
        "bytes",
        "cold-cache",
        "no-match"
      ],
      "syntax_features": [
        "module-search",
        "pattern-text-model"
      ],
      "notes": [
        "Mirrored bytes search path to keep text-model coverage visible in the module-boundary family."
      ]
    }
  ]
}
