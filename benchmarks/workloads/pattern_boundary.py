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
