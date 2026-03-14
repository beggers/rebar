MANIFEST = {
  "schema_version": 1,
  "manifest_id": "compile-matrix",
  "defaults": {
    "warmup_iterations": 2,
    "sample_iterations": 5,
    "timed_samples": 7
  },
  "workloads": [
    {
      "id": "compile-inline-locale-bytes-warm",
      "bucket": "bytes-inline-flags",
      "family": "parser",
      "operation": "compile",
      "pattern": "(?L:a)",
      "flags": 0,
      "text_model": "bytes",
      "cache_mode": "warm",
      "categories": [
        "bytes",
        "inline-flags",
        "warm-cache"
      ],
      "syntax_features": [
        "pattern-text-model",
        "flag-syntax",
        "grouping-forms"
      ],
      "notes": [
        "Warm bytes compile probe for the supported inline LOCALE flag case."
      ]
    },
    {
      "id": "compile-lookbehind-cold",
      "bucket": "lookbehind",
      "family": "parser",
      "operation": "compile",
      "pattern": "(?<=ab)c",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "categories": [
        "lookbehind",
        "cold-cache"
      ],
      "syntax_features": [
        "assertions-and-anchors"
      ],
      "notes": [
        "Cold compile probe for the supported fixed-width lookbehind success case."
      ]
    },
    {
      "id": "compile-character-class-ignorecase-warm",
      "bucket": "character-class-flags",
      "family": "parser",
      "operation": "compile",
      "pattern": "[A-Z_][a-z0-9_]+",
      "flags": 2,
      "text_model": "str",
      "cache_mode": "warm",
      "categories": [
        "character-class",
        "ignorecase",
        "warm-cache"
      ],
      "syntax_features": [
        "character-classes-and-sets",
        "flag-syntax"
      ],
      "notes": [
        "Warm compile probe for the supported bracket-class IGNORECASE parser path."
      ]
    },
    {
      "id": "compile-possessive-quantifier-cold",
      "bucket": "quantifiers",
      "family": "parser",
      "operation": "compile",
      "pattern": "a*+",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "categories": [
        "possessive-quantifier",
        "cold-cache"
      ],
      "syntax_features": [
        "quantifiers"
      ],
      "notes": [
        "Cold compile probe for the supported possessive quantifier parser path."
      ]
    },
    {
      "id": "compile-atomic-group-purged",
      "bucket": "atomic-group",
      "family": "parser",
      "operation": "compile",
      "pattern": "(?>ab|a)b",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "purged",
      "categories": [
        "atomic-group",
        "purged-cache"
      ],
      "syntax_features": [
        "grouping-forms",
        "cache-purge"
      ],
      "notes": [
        "Purged-cache compile probe for the supported atomic-group parser path."
      ]
    },
    {
      "id": "compile-parser-stress-cold",
      "bucket": "parser-stress",
      "family": "parser",
      "operation": "compile",
      "pattern": "(?i:(?P<lemma>[a-z]+))(?:_(?>[a-z]{2,4}+|\\d{2}))?(?:(?<=foo)bar)?(?P=lemma)",
      "flags": 0,
      "text_model": "str",
      "cache_mode": "cold",
      "categories": [
        "atomic-group",
        "possessive-quantifier",
        "lookbehind",
        "backreference",
        "cold-cache"
      ],
      "syntax_features": [
        "grouping-forms",
        "quantifiers",
        "assertions-and-anchors",
        "backreferences-and-conditionals",
        "flag-syntax"
      ],
      "notes": [
        "Heavier parser-stress compile proxy stays as an explicit known gap until grouped backreference workflows land."
      ]
    }
  ]
}
