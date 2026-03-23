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
      "id": "module-split-maxsplit-keyword-purged-bytes",
      "bucket": "module-split",
      "family": "module",
      "operation": "module.split",
      "pattern": "abc",
      "haystack": "zabczabc",
      "flags": 0,
      "kwargs": {
        "maxsplit": 1
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "split",
        "bytes",
        "maxsplit",
        "keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-split",
        "pattern-text-model",
        "cache-purge",
        "keyword-maxsplit"
      ],
      "notes": [
        "Bytes module.split helper path that keeps the bounded maxsplit= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-split-maxsplit-bool-keyword-purged-bytes",
      "bucket": "module-split",
      "family": "module",
      "operation": "module.split",
      "pattern": "abc",
      "haystack": "abcabc",
      "flags": 0,
      "kwargs": {
        "maxsplit": False
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "split",
        "bytes",
        "maxsplit",
        "keyword",
        "bool",
        "purged-cache"
      ],
      "syntax_features": [
        "module-split",
        "pattern-text-model",
        "cache-purge",
        "keyword-maxsplit"
      ],
      "notes": [
        "Bytes module.split helper path that keeps the bounded bool maxsplit= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-split-maxsplit-indexlike-keyword-purged-bytes",
      "bucket": "module-split",
      "family": "module",
      "operation": "module.split",
      "pattern": "abc",
      "haystack": "zabcabcabc",
      "flags": 0,
      "kwargs": {
        "maxsplit": {
          "type": "indexlike",
          "value": 2
        }
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "split",
        "bytes",
        "maxsplit",
        "indexlike",
        "keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-split",
        "pattern-text-model",
        "cache-purge",
        "indexlike",
        "keyword-maxsplit"
      ],
      "notes": [
        "Bytes module.split helper path that keeps the bounded keyword __index__ maxsplit workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-split-literal-warm-str-compiled-pattern",
      "bucket": "module-split",
      "family": "module",
      "operation": "module.split",
      "pattern": "abc",
      "haystack": "zzabczzabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "maxsplit": 1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "split",
        "literal",
        "compiled-pattern",
        "warm-cache"
      ],
      "syntax_features": [
        "module-split",
        "literal-text",
        "compiled-pattern-first-argument"
      ],
      "notes": [
        "Warm module.split helper path that keeps the bounded compiled-pattern-first-argument direct-success workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-split-maxsplit-keyword-purged-str-compiled-pattern",
      "bucket": "module-split",
      "family": "module",
      "operation": "module.split",
      "pattern": "abc",
      "haystack": "zabczabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "maxsplit": 1
      },
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "split",
        "literal",
        "compiled-pattern",
        "maxsplit",
        "keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-split",
        "literal-text",
        "compiled-pattern-first-argument",
        "keyword-maxsplit"
      ],
      "notes": [
        "Purged module.split helper path that keeps the bounded compiled-pattern-first-argument maxsplit= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern",
      "bucket": "module-split",
      "family": "module",
      "operation": "module.split",
      "pattern": "abc",
      "haystack": "zabcabcabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "maxsplit": {
          "type": "indexlike",
          "value": 2
        }
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "split",
        "bytes",
        "compiled-pattern",
        "maxsplit",
        "indexlike",
        "keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-split",
        "pattern-text-model",
        "compiled-pattern-first-argument",
        "indexlike",
        "keyword-maxsplit"
      ],
      "notes": [
        "Purged module.split helper path that keeps the bounded compiled-pattern-first-argument keyword __index__ maxsplit workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern",
      "bucket": "module-split",
      "family": "module",
      "operation": "module.split",
      "pattern": "abc",
      "haystack": "abcabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "maxsplit": False
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "split",
        "bytes",
        "compiled-pattern",
        "maxsplit",
        "keyword",
        "bool",
        "purged-cache"
      ],
      "syntax_features": [
        "module-split",
        "pattern-text-model",
        "compiled-pattern-first-argument",
        "keyword-maxsplit"
      ],
      "notes": [
        "Purged module.split helper path that keeps the bounded compiled-pattern-first-argument bool maxsplit= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-split-on-bytes-string-purged-str-compiled-pattern",
      "bucket": "module-split",
      "family": "module",
      "operation": "module.split",
      "pattern": "abc",
      "haystack": "zabczz",
      "flags": 0,
      "use_compiled_pattern": True,
      "maxsplit": 1,
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "cannot use a string pattern on a bytes-like object"
      },
      "text_model": "str",
      "haystack_text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "split",
        "literal",
        "compiled-pattern",
        "wrong-text-model",
        "purged-cache"
      ],
      "syntax_features": [
        "module-split",
        "literal-text",
        "compiled-pattern-first-argument",
        "wrong-text-model"
      ],
      "notes": [
        "Purged module.split helper path that keeps the bounded compiled-pattern-first-argument wrong-text-model TypeError on bytes haystacks on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-split-duplicate-maxsplit-keyword-purged-str",
      "bucket": "module-split",
      "family": "module",
      "operation": "module.split",
      "pattern": "abc",
      "haystack": "abc",
      "flags": 0,
      "maxsplit": 1,
      "kwargs": {
        "maxsplit": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "multiple values for argument 'maxsplit'"
      },
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "split",
        "literal",
        "maxsplit",
        "keyword",
        "duplicate-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-split",
        "literal-text",
        "keyword-maxsplit",
        "duplicate-keyword-error"
      ],
      "notes": [
        "Purged module.split helper path that keeps the bounded duplicate maxsplit= keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-split-unexpected-keyword-purged-str",
      "bucket": "module-split",
      "family": "module",
      "operation": "module.split",
      "pattern": "abc",
      "haystack": "abc",
      "flags": 0,
      "kwargs": {
        "missing": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "unexpected keyword argument 'missing'"
      },
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "split",
        "literal",
        "keyword",
        "unexpected-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-split",
        "literal-text",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Purged module.split helper path that keeps the bounded unexpected keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-split-unexpected-keyword-purged-bytes",
      "bucket": "module-split",
      "family": "module",
      "operation": "module.split",
      "pattern": "abc",
      "haystack": "abc",
      "flags": 0,
      "kwargs": {
        "missing": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "unexpected keyword argument 'missing'"
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "split",
        "bytes",
        "keyword",
        "unexpected-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-split",
        "pattern-text-model",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Purged module.split helper path that keeps the bounded unexpected keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern",
      "bucket": "module-split",
      "family": "module",
      "operation": "module.split",
      "pattern": "abc",
      "haystack": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "maxsplit": 1,
      "kwargs": {
        "maxsplit": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "multiple values for argument 'maxsplit'"
      },
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "split",
        "literal",
        "compiled-pattern",
        "maxsplit",
        "keyword",
        "duplicate-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-split",
        "literal-text",
        "compiled-pattern-first-argument",
        "keyword-maxsplit",
        "duplicate-keyword-error"
      ],
      "notes": [
        "Purged module.split helper path that keeps the bounded compiled-pattern-first-argument duplicate maxsplit= keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-split-unexpected-keyword-purged-bytes-compiled-pattern",
      "bucket": "module-split",
      "family": "module",
      "operation": "module.split",
      "pattern": "abc",
      "haystack": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "missing": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "unexpected keyword argument 'missing'"
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "split",
        "bytes",
        "compiled-pattern",
        "keyword",
        "unexpected-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-split",
        "pattern-text-model",
        "compiled-pattern-first-argument",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Purged module.split helper path that keeps the bounded compiled-pattern-first-argument unexpected keyword rejection on the shared collection/replacement benchmark surface."
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
      "id": "module-findall-literal-purged-bytes-compiled-pattern",
      "bucket": "module-findall",
      "family": "module",
      "operation": "module.findall",
      "pattern": "abc",
      "haystack": "zabcabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "findall",
        "bytes",
        "compiled-pattern",
        "purged-cache"
      ],
      "syntax_features": [
        "module-findall",
        "pattern-text-model",
        "compiled-pattern-first-argument"
      ],
      "notes": [
        "Purged bytes module.findall helper path that keeps the bounded compiled-pattern-first-argument direct-success workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-findall-on-str-string-purged-bytes-compiled-pattern",
      "bucket": "module-findall",
      "family": "module",
      "operation": "module.findall",
      "pattern": "abc",
      "haystack": "zabczz",
      "flags": 0,
      "use_compiled_pattern": True,
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "cannot use a bytes pattern on a string-like object"
      },
      "text_model": "bytes",
      "haystack_text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "findall",
        "bytes",
        "compiled-pattern",
        "wrong-text-model",
        "purged-cache"
      ],
      "syntax_features": [
        "module-findall",
        "pattern-text-model",
        "compiled-pattern-first-argument",
        "wrong-text-model"
      ],
      "notes": [
        "Purged module.findall helper path that keeps the bounded compiled-pattern-first-argument wrong-text-model TypeError on str haystacks on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-finditer-literal-warm-str-compiled-pattern",
      "bucket": "module-finditer",
      "family": "module",
      "operation": "module.finditer",
      "pattern": "abc",
      "haystack": "zabcabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "finditer",
        "literal",
        "compiled-pattern",
        "warm-cache"
      ],
      "syntax_features": [
        "module-finditer",
        "literal-text",
        "compiled-pattern-first-argument"
      ],
      "notes": [
        "Warm module.finditer helper path that keeps the bounded compiled-pattern-first-argument direct-success workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-finditer-on-bytes-string-warm-str-compiled-pattern",
      "bucket": "module-finditer",
      "family": "module",
      "operation": "module.finditer",
      "pattern": "abc",
      "haystack": "zabczz",
      "flags": 0,
      "use_compiled_pattern": True,
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "cannot use a string pattern on a bytes-like object"
      },
      "text_model": "str",
      "haystack_text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "collection",
        "finditer",
        "literal",
        "compiled-pattern",
        "wrong-text-model",
        "warm-cache"
      ],
      "syntax_features": [
        "module-finditer",
        "literal-text",
        "compiled-pattern-first-argument",
        "wrong-text-model"
      ],
      "notes": [
        "Warm module.finditer helper path that keeps the bounded compiled-pattern-first-argument wrong-text-model TypeError on bytes haystacks on the shared collection/replacement benchmark surface."
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
      "id": "module-sub-str-no-match-purged-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "zzz",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "cache-purge"
      ],
      "notes": [
        "Str module.sub helper path that keeps the raw no-match literal replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-str-single-match-purged-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "zabczz",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "single-match",
        "purged-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "cache-purge"
      ],
      "notes": [
        "Str module.sub helper path that keeps the raw single-match literal replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-str-repeated-purged-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "repeated",
        "purged-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "cache-purge"
      ],
      "notes": [
        "Str module.sub helper path that keeps the raw repeated-match literal replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-str-negative-count-purged-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "cache-purge"
      ],
      "notes": [
        "Str module.sub helper path that keeps the raw negative-count literal replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-str-count-purged-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "count": 1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "literal",
        "count",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "literal-text",
        "cache-purge"
      ],
      "notes": [
        "Str module.subn helper path that keeps the raw count-limited literal replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-str-repeated-purged-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "literal",
        "repeated",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "literal-text",
        "cache-purge"
      ],
      "notes": [
        "Str module.subn helper path that keeps the raw repeated-match literal replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-str-negative-count-purged-str",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "literal",
        "negative-count",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "literal-text",
        "cache-purge"
      ],
      "notes": [
        "Str module.subn helper path that keeps the raw negative-count literal replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-bytes-no-match-purged-bytes",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "zzz",
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "bytes",
        "no-match",
        "purged-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "cache-purge"
      ],
      "notes": [
        "Bytes module.sub helper path that keeps the raw no-match literal replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-bytes-count-purged-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "count",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "cache-purge"
      ],
      "notes": [
        "Bytes module.subn helper path that keeps the raw count-limited literal replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-bytes-repeated-purged-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "repeated",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "cache-purge"
      ],
      "notes": [
        "Bytes module.subn helper path that keeps the raw repeated-match literal replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-literal-warm-str-compiled-pattern",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "zabcabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "count": 1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "compiled-pattern",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "compiled-pattern-first-argument"
      ],
      "notes": [
        "Warm module.sub helper path that keeps the bounded compiled-pattern-first-argument direct-success workflow on the shared collection/replacement benchmark surface."
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
      "id": "module-sub-count-keyword-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "kwargs": {
        "count": 1
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "count",
        "keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "keyword-count"
      ],
      "notes": [
        "Warm module.sub helper path that keeps the bounded count= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-count-bool-keyword-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "kwargs": {
        "count": True
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "count",
        "keyword",
        "bool",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "keyword-count"
      ],
      "notes": [
        "Warm module.sub helper path that keeps the bounded bool count= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-count-bool-false-keyword-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "kwargs": {
        "count": False
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "count",
        "keyword",
        "bool",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "keyword-count"
      ],
      "notes": [
        "Warm module.sub helper path that keeps the bounded bool count= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-count-indexlike-keyword-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
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
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "count",
        "indexlike",
        "keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "indexlike",
        "keyword-count"
      ],
      "notes": [
        "Warm module.sub helper path that keeps the bounded keyword __index__ count workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-count-keyword-warm-str-compiled-pattern",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "count": 1
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "compiled-pattern",
        "count",
        "keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "compiled-pattern-first-argument",
        "keyword-count"
      ],
      "notes": [
        "Warm module.sub helper path that keeps the bounded compiled-pattern-first-argument count= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabcabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "count": {
          "type": "indexlike",
          "value": 2
        }
      },
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "bytes",
        "compiled-pattern",
        "count",
        "indexlike",
        "keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "pattern-text-model",
        "compiled-pattern-first-argument",
        "indexlike",
        "keyword-count"
      ],
      "notes": [
        "Warm module.sub helper path that keeps the bounded compiled-pattern-first-argument keyword __index__ count workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-count-bool-keyword-warm-str-compiled-pattern",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "count": True
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "compiled-pattern",
        "count",
        "keyword",
        "bool",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "compiled-pattern-first-argument",
        "keyword-count"
      ],
      "notes": [
        "Warm module.sub helper path that keeps the bounded compiled-pattern-first-argument bool count= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-count-bool-false-keyword-warm-str-compiled-pattern",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "count": False
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "compiled-pattern",
        "count",
        "keyword",
        "bool",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "compiled-pattern-first-argument",
        "keyword-count"
      ],
      "notes": [
        "Warm module.sub helper path that keeps the bounded compiled-pattern-first-argument bool count= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-on-bytes-string-warm-str-compiled-pattern",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "zabczz",
      "flags": 0,
      "use_compiled_pattern": True,
      "count": 1,
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "cannot use a string pattern on a bytes-like object"
      },
      "text_model": "str",
      "haystack_text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "compiled-pattern",
        "wrong-text-model",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "compiled-pattern-first-argument",
        "wrong-text-model"
      ],
      "notes": [
        "Warm module.sub helper path that keeps the bounded compiled-pattern-first-argument wrong-text-model TypeError on bytes haystacks on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-duplicate-count-keyword-warm-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "count": 1,
      "kwargs": {
        "count": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "multiple values for argument 'count'"
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "count",
        "keyword",
        "duplicate-keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "keyword-count",
        "duplicate-keyword-error"
      ],
      "notes": [
        "Warm module.sub helper path that keeps the bounded duplicate count= keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-unexpected-keyword-purged-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "kwargs": {
        "missing": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "unexpected keyword argument 'missing'"
      },
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "keyword",
        "unexpected-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Purged module.sub helper path that keeps the bounded unexpected keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-unexpected-keyword-after-positional-count-purged-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "count": 1,
      "kwargs": {
        "missing": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "unexpected keyword argument 'missing'"
      },
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "count",
        "keyword",
        "unexpected-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "positional-count",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Purged module.sub helper path that keeps the bounded positional count plus unexpected keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-count-alias-keyword-purged-str",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "kwargs": {
        "count_alias": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "unexpected keyword argument 'count_alias'"
      },
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "keyword",
        "unexpected-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Purged module.sub helper path that keeps the bounded count_alias keyword-name rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-duplicate-count-keyword-warm-str-compiled-pattern",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "count": 1,
      "kwargs": {
        "count": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "multiple values for argument 'count'"
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "compiled-pattern",
        "count",
        "keyword",
        "duplicate-keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "compiled-pattern-first-argument",
        "keyword-count",
        "duplicate-keyword-error"
      ],
      "notes": [
        "Warm module.sub helper path that keeps the bounded compiled-pattern-first-argument duplicate count= keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-unexpected-keyword-purged-str-compiled-pattern",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "missing": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "unexpected keyword argument 'missing'"
      },
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "compiled-pattern",
        "keyword",
        "unexpected-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "compiled-pattern-first-argument",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Purged module.sub helper path that keeps the bounded compiled-pattern-first-argument unexpected keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "count": 1,
      "kwargs": {
        "missing": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "unexpected keyword argument 'missing'"
      },
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "compiled-pattern",
        "count",
        "keyword",
        "unexpected-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "compiled-pattern-first-argument",
        "positional-count",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Purged module.sub helper path that keeps the bounded compiled-pattern-first-argument positional count plus unexpected keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-sub-count-alias-keyword-purged-str-compiled-pattern",
      "bucket": "module-sub",
      "family": "module",
      "operation": "module.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "count_alias": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "unexpected keyword argument 'count_alias'"
      },
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "sub",
        "literal",
        "compiled-pattern",
        "keyword",
        "unexpected-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-sub",
        "literal-text",
        "compiled-pattern-first-argument",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Purged module.sub helper path that keeps the bounded compiled-pattern-first-argument count_alias keyword-name rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-literal-purged-bytes-compiled-pattern",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "zabcabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "compiled-pattern",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "compiled-pattern-first-argument"
      ],
      "notes": [
        "Purged bytes module.subn helper path that keeps the bounded compiled-pattern-first-argument direct-success workflow on the shared collection/replacement benchmark surface."
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
      "id": "module-subn-count-keyword-purged-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "kwargs": {
        "count": 1
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "count",
        "keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "cache-purge",
        "keyword-count"
      ],
      "notes": [
        "Bytes module.subn helper path that keeps the bounded count= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-count-bool-keyword-purged-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "kwargs": {
        "count": False
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "count",
        "keyword",
        "bool",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "cache-purge",
        "keyword-count"
      ],
      "notes": [
        "Bytes module.subn helper path that keeps the bounded bool count= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-count-bool-true-keyword-purged-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "kwargs": {
        "count": True
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "count",
        "keyword",
        "bool",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "cache-purge",
        "keyword-count"
      ],
      "notes": [
        "Bytes module.subn helper path that keeps the bounded bool count= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-count-indexlike-keyword-purged-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
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
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "count",
        "indexlike",
        "keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "cache-purge",
        "indexlike",
        "keyword-count"
      ],
      "notes": [
        "Bytes module.subn helper path that keeps the bounded keyword __index__ count workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-duplicate-count-keyword-warm-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "count": 1,
      "kwargs": {
        "count": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "multiple values for argument 'count'"
      },
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "count",
        "keyword",
        "duplicate-keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "keyword-count",
        "duplicate-keyword-error"
      ],
      "notes": [
        "Warm module.subn helper path that keeps the bounded duplicate count= keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-unexpected-keyword-purged-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "kwargs": {
        "missing": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "unexpected keyword argument 'missing'"
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "keyword",
        "unexpected-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Purged module.subn helper path that keeps the bounded unexpected keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-unexpected-keyword-after-positional-count-purged-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "count": 1,
      "kwargs": {
        "missing": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "unexpected keyword argument 'missing'"
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "count",
        "keyword",
        "unexpected-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "positional-count",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Purged module.subn helper path that keeps the bounded positional count plus unexpected keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-count-alias-keyword-purged-bytes",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "kwargs": {
        "count_alias": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "unexpected keyword argument 'count_alias'"
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "keyword",
        "unexpected-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Purged module.subn helper path that keeps the bounded count_alias keyword-name rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-count-keyword-purged-bytes-compiled-pattern",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "count": 1
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "compiled-pattern",
        "count",
        "keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "compiled-pattern-first-argument",
        "keyword-count"
      ],
      "notes": [
        "Purged module.subn helper path that keeps the bounded compiled-pattern-first-argument count= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-count-indexlike-keyword-purged-str-compiled-pattern",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabcabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "count": {
          "type": "indexlike",
          "value": 2
        }
      },
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "literal",
        "compiled-pattern",
        "count",
        "indexlike",
        "keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "literal-text",
        "compiled-pattern-first-argument",
        "indexlike",
        "keyword-count"
      ],
      "notes": [
        "Purged module.subn helper path that keeps the bounded compiled-pattern-first-argument keyword __index__ count workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-count-bool-keyword-purged-bytes-compiled-pattern",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "count": False
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "compiled-pattern",
        "count",
        "keyword",
        "bool",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "compiled-pattern-first-argument",
        "keyword-count"
      ],
      "notes": [
        "Purged module.subn helper path that keeps the bounded compiled-pattern-first-argument bool count= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "count": True
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "compiled-pattern",
        "count",
        "keyword",
        "bool",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "compiled-pattern-first-argument",
        "keyword-count"
      ],
      "notes": [
        "Purged module.subn helper path that keeps the bounded compiled-pattern-first-argument bool count= keyword workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-on-str-string-purged-bytes-compiled-pattern",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "zabczz",
      "flags": 0,
      "use_compiled_pattern": True,
      "count": 1,
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "cannot use a bytes pattern on a string-like object"
      },
      "text_model": "bytes",
      "haystack_text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "compiled-pattern",
        "wrong-text-model",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "compiled-pattern-first-argument",
        "wrong-text-model"
      ],
      "notes": [
        "Purged module.subn helper path that keeps the bounded compiled-pattern-first-argument wrong-text-model TypeError on str haystacks on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "count": 1,
      "kwargs": {
        "count": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "multiple values for argument 'count'"
      },
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "compiled-pattern",
        "count",
        "keyword",
        "duplicate-keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "compiled-pattern-first-argument",
        "keyword-count",
        "duplicate-keyword-error"
      ],
      "notes": [
        "Warm module.subn helper path that keeps the bounded compiled-pattern-first-argument duplicate count= keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-unexpected-keyword-purged-bytes-compiled-pattern",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "missing": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "unexpected keyword argument 'missing'"
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "compiled-pattern",
        "keyword",
        "unexpected-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "compiled-pattern-first-argument",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Purged module.subn helper path that keeps the bounded compiled-pattern-first-argument unexpected keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "use_compiled_pattern": True,
      "count": 1,
      "kwargs": {
        "missing": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "unexpected keyword argument 'missing'"
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "compiled-pattern",
        "count",
        "keyword",
        "unexpected-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "compiled-pattern-first-argument",
        "positional-count",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Purged module.subn helper path that keeps the bounded compiled-pattern-first-argument positional count plus unexpected keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "module-subn-count-alias-keyword-purged-bytes-compiled-pattern",
      "bucket": "module-subn",
      "family": "module",
      "operation": "module.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "use_compiled_pattern": True,
      "kwargs": {
        "count_alias": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "unexpected keyword argument 'count_alias'"
      },
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "module-helper-call",
      "categories": [
        "replacement",
        "subn",
        "bytes",
        "compiled-pattern",
        "keyword",
        "unexpected-keyword",
        "purged-cache"
      ],
      "syntax_features": [
        "module-subn",
        "pattern-text-model",
        "compiled-pattern-first-argument",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Purged module.subn helper path that keeps the bounded compiled-pattern-first-argument count_alias keyword-name rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-findall-bounded-warm-str",
      "bucket": "pattern-findall",
      "family": "module",
      "operation": "pattern.findall",
      "pattern": "abc",
      "haystack": "zabcabcz",
      "flags": 0,
      "pos": 1,
      "endpos": 7,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "findall",
        "literal",
        "bounded",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-findall",
        "literal-text"
      ],
      "notes": [
        "Warm precompiled Pattern.findall helper path that keeps the bounded literal repeated-match workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-findall-bounded-no-match-warm-str",
      "bucket": "pattern-findall",
      "family": "module",
      "operation": "pattern.findall",
      "pattern": "abc",
      "haystack": "zabz",
      "flags": 0,
      "pos": 1,
      "endpos": 4,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "findall",
        "literal",
        "bounded",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-findall",
        "literal-text"
      ],
      "notes": [
        "Warm precompiled Pattern.findall helper path that keeps the bounded literal no-match workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-findall-bounded-purged-bytes",
      "bucket": "pattern-findall",
      "family": "module",
      "operation": "pattern.findall",
      "pattern": "abc",
      "haystack": "zabcabcz",
      "flags": 0,
      "pos": 1,
      "endpos": 7,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "findall",
        "bytes",
        "bounded",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-findall",
        "pattern-text-model",
        "cache-purge"
      ],
      "notes": [
        "Purged bytes Pattern.findall helper path that keeps the bounded literal repeated-match workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-finditer-bounded-warm-str",
      "bucket": "pattern-finditer",
      "family": "module",
      "operation": "pattern.finditer",
      "pattern": "abc",
      "haystack": "zabcabcx",
      "flags": 0,
      "pos": 1,
      "endpos": 7,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "finditer",
        "literal",
        "bounded",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-finditer",
        "literal-text"
      ],
      "notes": [
        "Warm precompiled Pattern.finditer helper path that keeps the bounded literal repeated-match workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-finditer-bounded-no-match-warm-str",
      "bucket": "pattern-finditer",
      "family": "module",
      "operation": "pattern.finditer",
      "pattern": "abc",
      "haystack": "zabz",
      "flags": 0,
      "pos": 1,
      "endpos": 4,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "finditer",
        "literal",
        "bounded",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-finditer",
        "literal-text"
      ],
      "notes": [
        "Warm precompiled Pattern.finditer helper path that keeps the bounded literal no-match workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-finditer-bounded-purged-bytes",
      "bucket": "pattern-finditer",
      "family": "module",
      "operation": "pattern.finditer",
      "pattern": "abc",
      "haystack": "zabcabcx",
      "flags": 0,
      "pos": 1,
      "endpos": 7,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "finditer",
        "bytes",
        "bounded",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-finditer",
        "pattern-text-model",
        "cache-purge"
      ],
      "notes": [
        "Purged bytes Pattern.finditer helper path that keeps the bounded literal repeated-match workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-split-no-match-warm-str",
      "bucket": "pattern-split",
      "family": "module",
      "operation": "pattern.split",
      "pattern": "abc",
      "haystack": "zzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "split",
        "literal",
        "no-match",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-split",
        "literal-text"
      ],
      "notes": [
        "Warm precompiled Pattern.split helper path that keeps the direct literal no-match workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-split-repeated-warm-str",
      "bucket": "pattern-split",
      "family": "module",
      "operation": "pattern.split",
      "pattern": "abc",
      "haystack": "abcabc",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "split",
        "literal",
        "repeated",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-split",
        "literal-text"
      ],
      "notes": [
        "Warm precompiled Pattern.split helper path that keeps the direct literal repeated-match workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-split-maxsplit-purged-bytes",
      "bucket": "pattern-split",
      "family": "module",
      "operation": "pattern.split",
      "pattern": "abc",
      "haystack": "abczzabc",
      "flags": 0,
      "maxsplit": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "split",
        "bytes",
        "maxsplit",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-split",
        "pattern-text-model",
        "cache-purge"
      ],
      "notes": [
        "Purged bytes Pattern.split helper path that keeps the direct bounded maxsplit workflow on the shared collection/replacement benchmark surface."
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
      "id": "pattern-split-duplicate-maxsplit-keyword-warm-str",
      "bucket": "pattern-split",
      "family": "module",
      "operation": "pattern.split",
      "pattern": "abc",
      "haystack": "abcabc",
      "flags": 0,
      "maxsplit": 1,
      "kwargs": {
        "maxsplit": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "split() takes at most 2 arguments (3 given)"
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
        "duplicate-keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-split",
        "literal-text",
        "keyword-maxsplit",
        "duplicate-keyword-error"
      ],
      "notes": [
        "Warm precompiled Pattern.split helper path that keeps the bounded duplicate maxsplit= keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-split-unexpected-keyword-warm-bytes",
      "bucket": "pattern-split",
      "family": "module",
      "operation": "pattern.split",
      "pattern": "abc",
      "haystack": "abcabc",
      "flags": 0,
      "kwargs": {
        "missing": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "'missing' is an invalid keyword argument for split()"
      },
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "split",
        "bytes",
        "keyword",
        "unexpected-keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-split",
        "pattern-text-model",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Bytes precompiled Pattern.split helper path that keeps the bounded unexpected keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-split-on-bytes-string-warm-str",
      "bucket": "pattern-split",
      "family": "module",
      "operation": "pattern.split",
      "pattern": "abc",
      "haystack": "zabczz",
      "flags": 0,
      "maxsplit": 0,
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "cannot use a string pattern on a bytes-like object"
      },
      "text_model": "str",
      "haystack_text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "collection",
        "split",
        "literal",
        "wrong-text-model",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-split",
        "literal-text",
        "wrong-text-model"
      ],
      "notes": [
        "Warm precompiled Pattern.split helper path that keeps the bounded wrong-text-model TypeError on bytes haystacks on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-sub-no-match-warm-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "zzz",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "sub",
        "literal",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "literal-text"
      ],
      "notes": [
        "Warm precompiled Pattern.sub helper path that keeps the bounded literal no-match replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-sub-single-match-warm-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "zabczz",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "sub",
        "literal",
        "single-match",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "literal-text"
      ],
      "notes": [
        "Warm precompiled Pattern.sub helper path that keeps the bounded literal single-match replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-sub-negative-count-warm-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "sub",
        "literal",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "literal-text",
        "positional-count"
      ],
      "notes": [
        "Warm precompiled Pattern.sub helper path that keeps the bounded negative-count literal replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-sub-bytes-no-match-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "zzz",
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "sub",
        "bytes",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "cache-purge"
      ],
      "notes": [
        "Purged bytes precompiled Pattern.sub helper path that keeps the bounded literal no-match replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-sub-bytes-single-match-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "zabczz",
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "sub",
        "bytes",
        "single-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "pattern-text-model",
        "cache-purge"
      ],
      "notes": [
        "Purged bytes precompiled Pattern.sub helper path that keeps the bounded literal single-match replacement workflow on the shared collection/replacement benchmark surface."
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
      "id": "pattern-sub-count-bool-true-keyword-purged-bytes",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "text_model": "bytes",
      "kwargs": {
        "count": True
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
        "Bytes precompiled Pattern.sub helper path that keeps the bounded bool-true count= keyword workflow on the shared collection/replacement benchmark surface."
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
      "id": "pattern-sub-duplicate-count-keyword-warm-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "count": 1,
      "kwargs": {
        "count": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "sub() takes at most 3 arguments (4 given)"
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "sub",
        "literal",
        "count",
        "keyword",
        "duplicate-keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "literal-text",
        "keyword-count",
        "duplicate-keyword-error"
      ],
      "notes": [
        "Warm precompiled Pattern.sub helper path that keeps the bounded duplicate count= keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-sub-unexpected-keyword-warm-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "kwargs": {
        "missing": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "'missing' is an invalid keyword argument for sub()"
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "sub",
        "literal",
        "keyword",
        "unexpected-keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "literal-text",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Warm precompiled Pattern.sub helper path that keeps the bounded unexpected keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-sub-unexpected-keyword-after-positional-count-warm-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "count": 1,
      "kwargs": {
        "missing": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "sub() takes at most 3 arguments (4 given)"
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "sub",
        "literal",
        "count",
        "keyword",
        "unexpected-keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "literal-text",
        "positional-count",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Warm precompiled Pattern.sub helper path that keeps the bounded positional count plus unexpected keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-sub-count-alias-keyword-warm-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "kwargs": {
        "count_alias": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "'count_alias' is an invalid keyword argument for sub()"
      },
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "sub",
        "literal",
        "keyword",
        "unexpected-keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "literal-text",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Warm precompiled Pattern.sub helper path that keeps the bounded count_alias keyword-name rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-sub-on-bytes-string-warm-str",
      "bucket": "pattern-sub",
      "family": "module",
      "operation": "pattern.sub",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "zabczz",
      "flags": 0,
      "count": 0,
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "cannot use a string pattern on a bytes-like object"
      },
      "text_model": "str",
      "haystack_text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "sub",
        "literal",
        "wrong-text-model",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-sub",
        "literal-text",
        "wrong-text-model"
      ],
      "notes": [
        "Warm precompiled Pattern.sub helper path that keeps the bounded wrong-text-model TypeError on bytes haystacks on the shared collection/replacement benchmark surface."
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
      "id": "pattern-subn-count-bool-false-keyword-warm-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "kwargs": {
        "count": False
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
        "Warm precompiled Pattern.subn helper path that keeps the bounded bool-false count= keyword workflow on the shared collection/replacement benchmark surface."
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
      "id": "pattern-subn-duplicate-count-keyword-warm-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "count": 1,
      "kwargs": {
        "count": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "subn() takes at most 3 arguments (4 given)"
      },
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "subn",
        "bytes",
        "count",
        "keyword",
        "duplicate-keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "keyword-count",
        "duplicate-keyword-error"
      ],
      "notes": [
        "Bytes precompiled Pattern.subn helper path that keeps the bounded duplicate count= keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-subn-unexpected-keyword-warm-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "kwargs": {
        "missing": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "'missing' is an invalid keyword argument for subn()"
      },
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "subn",
        "bytes",
        "keyword",
        "unexpected-keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Bytes precompiled Pattern.subn helper path that keeps the bounded unexpected keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-subn-unexpected-keyword-after-positional-count-warm-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abc",
      "flags": 0,
      "count": 1,
      "kwargs": {
        "missing": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "subn() takes at most 3 arguments (4 given)"
      },
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "subn",
        "bytes",
        "count",
        "keyword",
        "unexpected-keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "positional-count",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Bytes precompiled Pattern.subn helper path that keeps the bounded positional count plus unexpected keyword rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-subn-count-alias-keyword-warm-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "kwargs": {
        "count_alias": 1
      },
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "'count_alias' is an invalid keyword argument for subn()"
      },
      "text_model": "bytes",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "subn",
        "bytes",
        "keyword",
        "unexpected-keyword",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "unexpected-keyword-error"
      ],
      "notes": [
        "Bytes precompiled Pattern.subn helper path that keeps the bounded count_alias keyword-name rejection on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-subn-on-str-string-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "zabczz",
      "flags": 0,
      "count": 0,
      "expected_exception": {
        "type": "TypeError",
        "message_substring": "cannot use a bytes pattern on a string-like object"
      },
      "text_model": "bytes",
      "haystack_text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "subn",
        "bytes",
        "wrong-text-model",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "wrong-text-model"
      ],
      "notes": [
        "Purged precompiled Pattern.subn helper path that keeps the bounded wrong-text-model TypeError on str haystacks on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-subn-count-warm-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "count": 1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "subn",
        "literal",
        "count",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "literal-text",
        "positional-count"
      ],
      "notes": [
        "Warm precompiled Pattern.subn helper path that keeps the bounded literal single-replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-subn-repeated-warm-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "count": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "subn",
        "literal",
        "repeated-match",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "literal-text"
      ],
      "notes": [
        "Warm precompiled Pattern.subn helper path that keeps the bounded literal repeated-match replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-subn-negative-count-warm-str",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "count": -1,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "subn",
        "literal",
        "negative-count",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "literal-text",
        "positional-count"
      ],
      "notes": [
        "Warm precompiled Pattern.subn helper path that keeps the bounded negative-count literal replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-subn-bytes-count-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "count": 1,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "subn",
        "bytes",
        "count",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "cache-purge",
        "positional-count"
      ],
      "notes": [
        "Purged bytes precompiled Pattern.subn helper path that keeps the bounded literal single-replacement workflow on the shared collection/replacement benchmark surface."
      ]
    },
    {
      "id": "pattern-subn-bytes-repeated-purged-bytes",
      "bucket": "pattern-subn",
      "family": "module",
      "operation": "pattern.subn",
      "pattern": "abc",
      "replacement": "x",
      "haystack": "abcabc",
      "flags": 0,
      "count": 0,
      "text_model": "bytes",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "replacement",
        "subn",
        "bytes",
        "repeated-match",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-subn",
        "pattern-text-model",
        "cache-purge"
      ],
      "notes": [
        "Purged bytes precompiled Pattern.subn helper path that keeps the bounded literal repeated-match replacement workflow on the shared collection/replacement benchmark surface."
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
