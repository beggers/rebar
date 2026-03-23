MANIFEST = {
  "schema_version": 1,
  "manifest_id": "named-group-replacement-workflows",
  "layer": "module_workflow",
  "suite_id": "collection.replacement.named_group",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "module-sub-template-named-group-str",
      "operation": "module_call",
      "family": "named_group_replacement_workflow",
      "helper": "sub",
      "args": [
        "(?P<word>abc)",
        "<\\g<word>>",
        "abcabc"
      ],
      "categories": ["workflow", "sub", "replacement-template", "named-group", "module", "str"],
      "notes": [
        "Publishes the bounded module-level named-group replacement-template path for a tiny literal capture without broadening into named backreferences."
      ]
    },
    {
      "id": "module-subn-template-named-group-str",
      "operation": "module_call",
      "family": "named_group_replacement_workflow",
      "helper": "subn",
      "args": [
        "(?P<word>abc)",
        "<\\g<word>>",
        "abcabc",
        1
      ],
      "categories": ["workflow", "subn", "replacement-template", "named-group", "module", "str", "count"],
      "notes": [
        "Publishes the bounded module-level named-group replacement-template count path for the same tiny literal capture."
      ]
    },
    {
      "id": "pattern-sub-template-named-group-str",
      "operation": "pattern_call",
      "family": "named_group_replacement_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "sub",
      "args": [
        "<\\g<word>>",
        "abcabc"
      ],
      "categories": ["workflow", "sub", "replacement-template", "named-group", "pattern", "str"],
      "notes": [
        "Publishes the bound Pattern.sub named-group replacement-template path for the same tiny literal capture."
      ]
    },
    {
      "id": "pattern-subn-template-named-group-str",
      "operation": "pattern_call",
      "family": "named_group_replacement_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "subn",
      "args": [
        "<\\g<word>>",
        "abcabc",
        1
      ],
      "categories": ["workflow", "subn", "replacement-template", "named-group", "pattern", "str", "count"],
      "notes": [
        "Publishes the bound Pattern.subn named-group replacement-template count path without claiming named-template support is implemented."
      ]
    },
    {
      "id": "pattern-sub-callable-named-grouped-str",
      "operation": "pattern_call",
      "family": "named_group_callable_replacement_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "sub",
      "args": [
        {
          "type": "callable_match_group",
          "group": "word",
          "prefix": "<",
          "suffix": ">"
        },
        "abcabc"
      ],
      "categories": ["workflow", "sub", "callable-replacement", "named-group", "pattern", "str"],
      "notes": [
        "Publishes the bounded Pattern.sub named-group callable replacement path for the tiny `word` capture already covered by direct parity tests."
      ]
    },
    {
      "id": "pattern-subn-callable-named-grouped-str",
      "operation": "pattern_call",
      "family": "named_group_callable_replacement_count_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "subn",
      "args": [
        {
          "type": "callable_match_group",
          "group": "word",
          "prefix": "<",
          "suffix": ">"
        },
        "abcabc",
        1
      ],
      "categories": ["workflow", "subn", "callable-replacement", "named-group", "pattern", "str", "count"],
      "notes": [
        "Publishes the bounded Pattern.subn named-group callable replacement first-match-only path so the compiled named grouped callback slice is explicit in the shared correctness surface."
      ]
    },
    {
      "id": "pattern-sub-callable-named-grouped-bytes",
      "operation": "pattern_call",
      "family": "named_group_callable_replacement_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "sub",
      "text_model": "bytes",
      "args": [
        {
          "type": "callable_match_group",
          "group": "word",
          "prefix": {
            "type": "bytes",
            "encoding": "latin-1",
            "value": "<"
          },
          "suffix": {
            "type": "bytes",
            "encoding": "latin-1",
            "value": ">"
          }
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabc"
        }
      ],
      "categories": ["workflow", "sub", "callable-replacement", "named-group", "pattern", "bytes"],
      "notes": [
        "Publishes the bounded Pattern.sub named-group callable replacement bytes path for the tiny `word` capture already covered by direct parity tests."
      ]
    },
    {
      "id": "pattern-subn-callable-named-grouped-bytes",
      "operation": "pattern_call",
      "family": "named_group_callable_replacement_count_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "subn",
      "text_model": "bytes",
      "args": [
        {
          "type": "callable_match_group",
          "group": "word",
          "prefix": {
            "type": "bytes",
            "encoding": "latin-1",
            "value": "<"
          },
          "suffix": {
            "type": "bytes",
            "encoding": "latin-1",
            "value": ">"
          }
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabc"
        },
        1
      ],
      "categories": ["workflow", "subn", "callable-replacement", "named-group", "pattern", "bytes", "count"],
      "notes": [
        "Publishes the bounded Pattern.subn named-group callable replacement first-match-only bytes path so the compiled named grouped callback bytes slice is explicit in the shared correctness surface."
      ]
    }
  ]
}
