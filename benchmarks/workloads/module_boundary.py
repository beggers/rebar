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
