MANIFEST = {
  "schema_version": 1,
  "manifest_id": "collection-replacement-workflows",
  "layer": "module_workflow",
  "suite_id": "collection.replacement.workflow",
  "defaults": {
    "flags": 0,
    "text_model": "str"
  },
  "cases": [
    {
      "id": "module-split-str-leading-trailing",
      "operation": "module_call",
      "family": "split_workflow",
      "helper": "split",
      "args": ["abc", "abczzabc"],
      "categories": ["workflow", "split", "literal", "str", "leading", "trailing", "repeated"],
      "notes": [
        "Pins module-level literal split behavior with repeated matches and both leading and trailing empty fields."
      ]
    },
    {
      "id": "module-split-str-no-match",
      "operation": "module_call",
      "family": "split_workflow",
      "helper": "split",
      "args": ["abc", "zzz"],
      "categories": ["workflow", "split", "literal", "str", "no-match"],
      "notes": [
        "Observes that module split returns the original string when no literal match is present."
      ]
    },
    {
      "id": "pattern-split-bytes-maxsplit",
      "operation": "pattern_call",
      "family": "split_workflow",
      "pattern": "abc",
      "text_model": "bytes",
      "helper": "split",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abczzabc"
        },
        1
      ],
      "categories": ["workflow", "split", "literal", "bytes", "maxsplit"],
      "notes": [
        "Carries bounded maxsplit behavior through the compiled bytes Pattern.split path."
      ]
    },
    {
      "id": "module-findall-bytes-repeated",
      "operation": "module_call",
      "family": "findall_workflow",
      "helper": "findall",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abc"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabc"
        }
      ],
      "categories": ["workflow", "findall", "literal", "bytes", "repeated"],
      "notes": [
        "Pins bytes-valued module findall behavior for repeated literal matches."
      ]
    },
    {
      "id": "pattern-findall-str-no-match",
      "operation": "pattern_call",
      "family": "findall_workflow",
      "pattern": "abc",
      "helper": "findall",
      "args": ["zzz"],
      "categories": ["workflow", "findall", "literal", "str", "no-match"],
      "notes": [
        "Observes that the bound Pattern.findall path returns an empty list when the literal does not occur."
      ]
    },
    {
      "id": "module-finditer-str-repeated",
      "operation": "module_call",
      "family": "finditer_workflow",
      "helper": "finditer",
      "args": ["abc", "zabcabc"],
      "categories": ["workflow", "finditer", "literal", "str", "repeated", "iterator-exhaustion"],
      "notes": [
        "Materializes the module-level finditer result so the scorecard captures ordered matches and iterator exhaustion."
      ]
    },
    {
      "id": "pattern-finditer-bytes-bounded",
      "operation": "pattern_call",
      "family": "finditer_workflow",
      "pattern": "abc",
      "text_model": "bytes",
      "helper": "finditer",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabcx"
        },
        1,
        7
      ],
      "categories": ["workflow", "finditer", "literal", "bytes", "bounded", "iterator-exhaustion"],
      "notes": [
        "Pins the bounded compiled-pattern bytes finditer path, including its exhausted terminal state."
      ]
    },
    {
      "id": "module-sub-str-repeated",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "sub",
      "args": ["abc", "x", "abcabc"],
      "categories": ["workflow", "sub", "literal", "str", "repeated"],
      "notes": [
        "Pins module-level literal replacement behavior for repeated str matches."
      ]
    },
    {
      "id": "module-subn-bytes-count",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "subn",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abc"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabc"
        },
        1
      ],
      "categories": ["workflow", "subn", "literal", "bytes", "count"],
      "notes": [
        "Carries bounded replacement-count behavior through the bytes-valued module subn helper."
      ]
    },
    {
      "id": "pattern-sub-str-no-match",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "helper": "sub",
      "args": ["x", "zzz"],
      "categories": ["workflow", "sub", "literal", "str", "no-match"],
      "notes": [
        "Observes that the compiled-pattern replacement path leaves the string unchanged when no match exists."
      ]
    },
    {
      "id": "pattern-subn-str-count",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "helper": "subn",
      "args": ["x", "abcabc", 1],
      "categories": ["workflow", "subn", "literal", "str", "count"],
      "notes": [
        "Pins the compiled-pattern str subn path for a bounded single replacement."
      ]
    },
    {
      "id": "module-sub-template-str",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "sub",
      "args": ["abc", "\\g<0>x", "abc"],
      "categories": ["workflow", "sub", "replacement-template", "str"],
      "notes": [
        "Pins the bounded whole-match replacement-template slice for a supported literal str pattern."
      ]
    },
    {
      "id": "module-sub-callable-str",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "sub",
      "args": [
        "abc",
        {
          "type": "callable_constant",
          "value": "x"
        },
        "abcabc"
      ],
      "categories": ["workflow", "sub", "callable-replacement", "str"],
      "notes": [
        "Pins the bounded callable replacement slice for a supported literal str pattern."
      ]
    },
    {
      "id": "module-sub-grouping-template",
      "operation": "module_call",
      "family": "grouped_template_replacement_workflow",
      "helper": "sub",
      "args": ["(abc)", "\\1x", "abc"],
      "categories": ["workflow", "sub", "replacement-template", "grouping-dependent", "str"],
      "notes": [
        "Pins the bounded grouped-literal replacement-template slice without broadening into general grouped-pattern or backreference support."
      ]
    },
    {
      "id": "module-findall-nonliteral-str",
      "operation": "module_call",
      "family": "bounded_wildcard_collection_workflow",
      "helper": "findall",
      "args": ["a.c", "abc"],
      "categories": ["workflow", "findall", "bounded-wildcard", "non-literal", "str"],
      "notes": [
        "Pins the bounded single-dot wildcard findall workflow without broadening into general metacharacter support."
      ]
    }
  ]
}
