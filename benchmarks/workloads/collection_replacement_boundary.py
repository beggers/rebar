MANIFEST = {
  "schema_version": 1,
  "manifest_id": "collection-replacement-boundary",
  "spec_refs": [
    "docs/benchmarks/plan.md",
    "docs/spec/drop-in-re-compatibility.md"
  ],
  "notes": [
    "Collection/replacement boundary workloads keep patterns and haystacks intentionally tiny so the timings stay about helper-call overhead instead of regex throughput, even when they exercise bounded wildcard or replacement-template behavior.",
    "Cache labels describe module compile-cache state or precompiled Pattern provenance rather than replacement-template complexity, capture-group breadth, or large-haystack scanning cost."
  ],
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "module-split-literal-warm-str",
      "bucket": "module-split",
      "family": "module",
      "operation": "module.split",
      "pattern": ":",
      "haystack": "a:b:c",
      "flags": 0,
      "maxsplit": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "smoke": True,
      "categories": [
        "collection",
        "split",
        "literal",
        "warm-cache",
        "smoke"
      ],
      "syntax_features": [
        "module-split",
        "literal-text"
      ],
      "notes": [
        "Warm module.split helper path over a tiny literal separator with the default maxsplit."
      ]
    },
    {
      "id": "module-split-literal-purged-bytes",
      "bucket": "module-split",
      "family": "module",
      "operation": "module.split",
      "pattern": ":",
      "haystack": "a:b:c",
      "flags": 0,
      "maxsplit": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "split",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "module-split",
        "pattern-text-model",
        "cache-purge"
      ],
      "notes": [
        "Bytes module.split helper path with a one-split limit so cache-purge provenance stays visible."
      ]
    },
    {
      "id": "module-split-maxsplit-indexlike-positional-purged-bytes",
      "bucket": "module-split",
      "family": "module",
      "operation": "module.split",
      "pattern": "abc",
      "haystack": "zabcabcabc",
      "flags": 0,
      "maxsplit": {
        "type": "indexlike",
        "value": 2
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "split",
        "bytes",
        "indexlike",
        "positional",
        "purged-cache"
      ],
      "syntax_features": [
        "module-split",
        "pattern-text-model",
        "cache-purge",
        "positional-indexlike"
      ],
      "notes": [
        "Bytes module.split helper path that keeps the bounded positional __index__ maxsplit workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-findall-single-dot-warm-str",
      "bucket": "module-findall",
      "family": "module",
      "operation": "module.findall",
      "pattern": "a.c",
      "haystack": "zzabcyyaxc",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "findall",
        "single-dot",
        "warm-cache"
      ],
      "syntax_features": [
        "module-findall",
        "wildcard-single-dot"
      ],
      "notes": [
        "Warm module.findall helper path over the bounded single-dot workflow so wildcard support is timed alongside the earlier literal-only collection rows."
      ]
    },
    {
      "id": "module-findall-literal-purged-bytes",
      "bucket": "module-findall",
      "family": "module",
      "operation": "module.findall",
      "pattern": "ab",
      "haystack": "zzabyyab",
      "flags": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "findall",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "module-findall",
        "pattern-text-model",
        "cache-purge"
      ],
      "notes": [
        "Bytes module.findall helper path that keeps repeated-match behavior visible without broadening into throughput claims."
      ]
    },
    {
      "id": "module-sub-template-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "\\g<0>x",
      "haystack": "zzabcyyabc",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "template",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "replacement-template"
      ],
      "notes": [
        "Warm module.sub helper path with a whole-match replacement template so the Rust-backed template workflow reaches the benchmark scorecard."
      ]
    },
    {
      "id": "module-sub-literal-purged-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "ab",
      "replacement": "XY",
      "haystack": "zzabyyab",
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "cache-purge"
      ],
      "notes": [
        "Bytes module.sub helper path with a single replacement count so replacement-boundary overhead stays easy to isolate."
      ]
    },
    {
      "id": "module-sub-count-indexlike-positional-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabcabc",
      "flags": 0,
      "count": {
        "type": "indexlike",
        "value": 2
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "count",
        "indexlike",
        "positional",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "positional-indexlike"
      ],
      "notes": [
        "Warm module.sub helper path that keeps the bounded positional __index__ count workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-count-indexlike-positional-purged-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabcabc",
      "flags": 0,
      "count": {
        "type": "indexlike",
        "value": 2
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "count",
        "indexlike",
        "positional",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "cache-purge",
        "positional-indexlike"
      ],
      "notes": [
        "Bytes module.subn helper path that keeps the bounded positional __index__ count workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-split-maxsplit-indexlike-positional-warm-str",
      "bucket": "pattern-split",
      "family": "module",
      "operation": "pattern.split",
      "pattern": "abc",
      "haystack": "zabcabcabc",
      "flags": 0,
      "maxsplit": {
        "type": "indexlike",
        "value": 2
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "split",
        "literal",
        "maxsplit",
        "indexlike",
        "positional",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-split",
        "literal-text",
        "positional-indexlike"
      ],
      "notes": [
        "Warm precompiled Pattern.split helper path that keeps the bounded positional __index__ maxsplit workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-split-maxsplit-keyword-warm-str",
      "bucket": "pattern-split",
      "family": "module",
      "operation": "pattern.split",
      "pattern": "abc",
      "haystack": "zabczabc",
      "flags": 0,
      "kwargs": {
        "maxsplit": 1
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "split",
        "literal",
        "maxsplit",
        "keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-split",
        "literal-text",
        "keyword-maxsplit"
      ],
      "notes": [
        "Warm precompiled Pattern.split helper path that keeps the bounded maxsplit= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-split-maxsplit-bool-keyword-warm-str",
      "bucket": "pattern-split",
      "family": "module",
      "operation": "pattern.split",
      "pattern": "abc",
      "haystack": "zabczabc",
      "flags": 0,
      "kwargs": {
        "maxsplit": True
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "split",
        "literal",
        "maxsplit",
        "keyword",
        "bool",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-split",
        "literal-text",
        "keyword-maxsplit"
      ],
      "notes": [
        "Warm precompiled Pattern.split helper path that keeps the bounded bool maxsplit= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-split-maxsplit-indexlike-keyword-warm-str",
      "bucket": "pattern-split",
      "family": "module",
      "operation": "pattern.split",
      "pattern": "abc",
      "haystack": "zabcabcabc",
      "flags": 0,
      "kwargs": {
        "maxsplit": {
          "type": "indexlike",
          "value": 2
        }
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "split",
        "literal",
        "maxsplit",
        "keyword",
        "indexlike",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-split",
        "literal-text",
        "keyword-maxsplit"
      ],
      "notes": [
        "Warm precompiled Pattern.split helper path that keeps the bounded keyword __index__ maxsplit workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-finditer-literal-warm-str",
      "bucket": "pattern-finditer",
      "family": "module",
      "operation": "pattern.finditer",
      "pattern": "ab",
      "haystack": "zzabyyab",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "finditer",
        "literal",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-finditer",
        "literal-text"
      ],
      "notes": [
        "Warm precompiled Pattern.finditer helper path with eager iterator consumption over a tiny haystack."
      ]
    },
    {
      "id": "pattern-finditer-literal-purged-bytes",
      "bucket": "pattern-finditer",
      "family": "module",
      "operation": "pattern.finditer",
      "pattern": "ab",
      "haystack": "zzabyyab",
      "flags": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "finditer",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-finditer",
        "pattern-text-model",
        "cache-purge"
      ],
      "notes": [
        "Bytes precompiled Pattern.finditer helper path that keeps purge provenance visible while still consuming the tiny iterator output."
      ]
    },
    {
      "id": "pattern-sub-count-indexlike-positional-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabcabc",
      "flags": 0,
      "count": {
        "type": "indexlike",
        "value": 2
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "sub",
        "bytes",
        "count",
        "indexlike",
        "positional",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "cache-purge",
        "positional-indexlike"
      ],
      "notes": [
        "Bytes precompiled Pattern.sub helper path that keeps the bounded positional __index__ count workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-sub-count-keyword-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "text_model": "bytes",
      "kwargs": {
        "count": 1
      },
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "sub",
        "bytes",
        "count",
        "keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "cache-purge",
        "keyword-count"
      ],
      "notes": [
        "Bytes precompiled Pattern.sub helper path that keeps the bounded count= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-sub-count-bool-keyword-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "text_model": "bytes",
      "kwargs": {
        "count": False
      },
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "sub",
        "bytes",
        "count",
        "keyword",
        "bool",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "cache-purge",
        "keyword-count"
      ],
      "notes": [
        "Bytes precompiled Pattern.sub helper path that keeps the bounded bool count= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-sub-count-indexlike-keyword-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabcabc",
      "flags": 0,
      "text_model": "bytes",
      "kwargs": {
        "count": {
          "type": "indexlike",
          "value": 2
        }
      },
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "sub",
        "bytes",
        "count",
        "keyword",
        "indexlike",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "cache-purge",
        "keyword-count"
      ],
      "notes": [
        "Bytes precompiled Pattern.sub helper path that keeps the bounded keyword __index__ count workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-subn-count-indexlike-positional-warm-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabcabc",
      "flags": 0,
      "count": {
        "type": "indexlike",
        "value": 2
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "subn",
        "literal",
        "count",
        "indexlike",
        "positional",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "literal-text",
        "positional-indexlike"
      ],
      "notes": [
        "Warm precompiled Pattern.subn helper path that keeps the bounded positional __index__ count workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-subn-count-keyword-warm-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "kwargs": {
        "count": 1
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "subn",
        "literal",
        "count",
        "keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "literal-text",
        "keyword-count"
      ],
      "notes": [
        "Warm precompiled Pattern.subn helper path that keeps the bounded count= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-subn-count-bool-keyword-warm-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "kwargs": {
        "count": True
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "subn",
        "literal",
        "count",
        "keyword",
        "bool",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "literal-text",
        "keyword-count"
      ],
      "notes": [
        "Warm precompiled Pattern.subn helper path that keeps the bounded bool count= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-subn-count-indexlike-keyword-warm-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabcabc",
      "flags": 0,
      "kwargs": {
        "count": {
          "type": "indexlike",
          "value": 2
        }
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "subn",
        "literal",
        "count",
        "keyword",
        "indexlike",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "literal-text",
        "keyword-count"
      ],
      "notes": [
        "Warm precompiled Pattern.subn helper path that keeps the bounded keyword __index__ count workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-subn-grouped-template-warm-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "(abc)",
      "replacement": "\\1x",
      "haystack": "zzabcyyabc",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "subn",
        "grouped",
        "template",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "grouping-forms",
        "replacement-template"
      ],
      "notes": [
        "Warm precompiled Pattern.subn helper path with a grouped-literal replacement template so capture-aware replacement timing is published explicitly."
      ]
    },
    {
      "id": "pattern-subn-literal-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "ab",
      "replacement": "XY",
      "haystack": "zzabyyab",
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "smoke": True,
      "categories": [
        "pattern",
        "replacement",
        "subn",
        "bytes",
        "purged-cache",
        "smoke"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "cache-purge"
      ],
      "notes": [
        "Smoke-sized bytes Pattern.subn helper path with a single replacement count and explicit purge provenance."
      ]
    }
  ]
}
