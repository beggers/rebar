MANIFEST = {
  "schema_version": 1,
  "manifest_id": "numbered-backreference-boundary",
  "spec_refs": [
    "docs/benchmarks/plan.md",
    "docs/spec/drop-in-re-compatibility.md"
  ],
  "notes": [
    "Numbered-backreference boundary workloads keep grouped patterns and haystacks intentionally tiny so the scorecard measures helper-call overhead for the bounded `(ab)\\\\1` and grouped-segment numbered-backreference slices rather than regex throughput.",
    "The bounded compile plus module and Pattern search paths are measured directly here, including the legacy grouped-segment `(ab)x\\\\1` / `x(ab)\\\\1` workload ids now that the helper pair is supported."
  ],
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "module-compile-numbered-backreference-cold-str",
      "bucket": "module-compile",
      "family": "module",
      "operation": "module.compile",
      "pattern": "(ab)\\1",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "compile",
        "grouped",
        "numbered-backreference",
        "cold-cache"
      ],
      "syntax_features": [
        "module-compile",
        "grouping-forms",
        "numbered-backreferences"
      ],
      "notes": [
        "Cold module.compile benchmark for the bounded numbered-backreference literal slice so compile metadata timing reaches the published benchmark report."
      ]
    },
    {
      "id": "module-search-numbered-backreference-warm-str",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "(ab)\\1",
      "haystack": "zzababzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "warm",
      "timing_scope": "module-helper-call",
      "smoke": True,
      "categories": [
        "grouped",
        "numbered-backreference",
        "search",
        "module",
        "warm-cache",
        "smoke"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "numbered-backreferences"
      ],
      "notes": [
        "Warm module.search helper path for the bounded `(ab)\\\\1` literal workflow on a tiny haystack."
      ]
    },
    {
      "id": "pattern-search-numbered-backreference-purged-str",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "(ab)\\1",
      "haystack": "zzababzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "smoke": True,
      "categories": [
        "pattern",
        "grouped",
        "numbered-backreference",
        "search",
        "purged-cache",
        "smoke"
      ],
      "syntax_features": [
        "pattern-search",
        "grouping-forms",
        "numbered-backreferences",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.search helper path for the same bounded numbered-backreference literal workflow."
      ]
    },
    {
      "id": "module-search-numbered-backreference-segment-cold-gap",
      "bucket": "module-search",
      "family": "module",
      "operation": "module.search",
      "pattern": "(ab)x\\1",
      "haystack": "zzabxabzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "timing_scope": "module-helper-call",
      "categories": [
        "grouped",
        "numbered-backreference",
        "grouped-segment",
        "search",
        "module",
        "cold-cache"
      ],
      "syntax_features": [
        "module-search",
        "grouping-forms",
        "numbered-backreferences",
        "literal-segments"
      ],
      "notes": [
        "Cold module.search helper path for the now-supported grouped-segment numbered-backreference `(ab)x\\\\1` slice, keeping the legacy workload id while publishing a real timing."
      ]
    },
    {
      "id": "pattern-search-numbered-backreference-prefix-purged-gap",
      "bucket": "pattern-search",
      "family": "module",
      "operation": "pattern.search",
      "pattern": "x(ab)\\1",
      "haystack": "zzxababzz",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "timing_scope": "pattern-helper-call",
      "categories": [
        "pattern",
        "grouped",
        "numbered-backreference",
        "grouped-segment",
        "search",
        "purged-cache"
      ],
      "syntax_features": [
        "pattern-search",
        "grouping-forms",
        "numbered-backreferences",
        "literal-segments",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache Pattern.search helper path for the now-supported grouped-segment numbered-backreference `x(ab)\\\\1` slice, keeping the legacy workload id while publishing a real timing."
      ]
    }
  ]
}
