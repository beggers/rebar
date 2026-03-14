MANIFEST = {
  "schema_version": 1,
  "manifest_id": "quantified-nested-group-replacement-workflows",
  "layer": "module_workflow",
  "suite_id": "collection.replacement.quantified_nested_group",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "module-sub-template-quantified-nested-group-numbered-lower-bound-str",
      "operation": "module_call",
      "family": "quantified_nested_group_numbered_outer_template_workflow",
      "helper": "sub",
      "args": [
        r"a((bc)+)d",
        r"\1x",
        "zzabcdzz"
      ],
      "categories": ["workflow", "sub", "replacement-template", "grouped", "nested-group", "quantified", "numbered-group", "outer-capture", "lower-bound", "module", "str", "gap"],
      "notes": [
        "Publishes the bounded numbered module-level quantified nested-group replacement-template lower-bound path on `abcd`, so the one-repetition outer capture stays visible without widening into broader counted repeats, alternation, or callable replacement."
      ]
    },
    {
      "id": "module-subn-template-quantified-nested-group-numbered-first-match-only-str",
      "operation": "module_call",
      "family": "quantified_nested_group_numbered_inner_template_count_workflow",
      "helper": "subn",
      "args": [
        r"a((bc)+)d",
        r"\2x",
        "zzabcbcdabcbcdzz",
        1
      ],
      "categories": ["workflow", "subn", "replacement-template", "grouped", "nested-group", "quantified", "numbered-group", "final-inner-capture", "count-limited", "module", "str", "count", "gap"],
      "notes": [
        "Publishes the numbered module-level quantified nested-group replacement-template first-match-only path on `abcbcdabcbcd`, so the final inner capture from the first quantified match stays visible while the second match remains untouched."
      ]
    },
    {
      "id": "pattern-sub-template-quantified-nested-group-numbered-repeated-outer-capture-str",
      "operation": "pattern_call",
      "family": "quantified_nested_group_numbered_outer_template_workflow",
      "pattern": r"a((bc)+)d",
      "helper": "sub",
      "args": [
        r"\1x",
        "zzabcbcdzz"
      ],
      "categories": ["workflow", "sub", "replacement-template", "grouped", "nested-group", "quantified", "numbered-group", "outer-capture", "repeated-inner-capture", "pattern", "str", "gap"],
      "notes": [
        "Publishes the bounded Pattern.sub numbered quantified nested-group replacement-template repeated path on `abcbcd`, so the outer capture expands to the repeated `bcbc` payload under quantification."
      ]
    },
    {
      "id": "pattern-subn-template-quantified-nested-group-numbered-first-match-only-str",
      "operation": "pattern_call",
      "family": "quantified_nested_group_numbered_inner_template_count_workflow",
      "pattern": r"a((bc)+)d",
      "helper": "subn",
      "args": [
        r"\2x",
        "zzabcbcdabcbcdzz",
        1
      ],
      "categories": ["workflow", "subn", "replacement-template", "grouped", "nested-group", "quantified", "numbered-group", "final-inner-capture", "count-limited", "pattern", "str", "count", "gap"],
      "notes": [
        "Publishes the bounded Pattern.subn numbered quantified nested-group replacement-template first-match-only path for the same repeated inner-capture slice."
      ]
    },
    {
      "id": "module-sub-template-quantified-nested-group-named-lower-bound-str",
      "operation": "module_call",
      "family": "named_quantified_nested_group_outer_template_workflow",
      "helper": "sub",
      "args": [
        r"a(?P<outer>(?P<inner>bc)+)d",
        r"\g<outer>x",
        "zzabcdzz"
      ],
      "categories": ["workflow", "sub", "replacement-template", "grouped", "nested-group", "quantified", "named-group", "outer-capture", "lower-bound", "module", "str", "gap"],
      "notes": [
        "Publishes the bounded named module-level quantified nested-group replacement-template lower-bound path on `abcd`, so the one-repetition named outer capture stays explicit without claiming callable replacement, alternation, or broader counted-repeat support."
      ]
    },
    {
      "id": "module-subn-template-quantified-nested-group-named-first-match-only-str",
      "operation": "module_call",
      "family": "named_quantified_nested_group_inner_template_count_workflow",
      "helper": "subn",
      "args": [
        r"a(?P<outer>(?P<inner>bc)+)d",
        r"\g<inner>x",
        "zzabcbcdabcbcdzz",
        1
      ],
      "categories": ["workflow", "subn", "replacement-template", "grouped", "nested-group", "quantified", "named-group", "final-inner-capture", "count-limited", "module", "str", "count", "gap"],
      "notes": [
        "Publishes the named module-level quantified nested-group replacement-template first-match-only path on `abcbcdabcbcd`, so the final inner named capture from the first quantified match stays visible while the second match remains untouched."
      ]
    },
    {
      "id": "pattern-sub-template-quantified-nested-group-named-repeated-outer-capture-str",
      "operation": "pattern_call",
      "family": "named_quantified_nested_group_outer_template_workflow",
      "pattern": r"a(?P<outer>(?P<inner>bc)+)d",
      "helper": "sub",
      "args": [
        r"\g<outer>x",
        "zzabcbcdzz"
      ],
      "categories": ["workflow", "sub", "replacement-template", "grouped", "nested-group", "quantified", "named-group", "outer-capture", "repeated-inner-capture", "pattern", "str", "gap"],
      "notes": [
        "Publishes the bounded Pattern.sub named quantified nested-group replacement-template repeated path on `abcbcd`, so the named outer capture still expands to the repeated `bcbc` payload under quantification."
      ]
    },
    {
      "id": "pattern-subn-template-quantified-nested-group-named-first-match-only-str",
      "operation": "pattern_call",
      "family": "named_quantified_nested_group_inner_template_count_workflow",
      "pattern": r"a(?P<outer>(?P<inner>bc)+)d",
      "helper": "subn",
      "args": [
        r"\g<inner>x",
        "zzabcbcdabcbcdzz",
        1
      ],
      "categories": ["workflow", "subn", "replacement-template", "grouped", "nested-group", "quantified", "named-group", "final-inner-capture", "count-limited", "pattern", "str", "count", "gap"],
      "notes": [
        "Publishes the bounded Pattern.subn named quantified nested-group replacement-template first-match-only path for the same repeated inner-capture slice."
      ]
    }
  ]
}
