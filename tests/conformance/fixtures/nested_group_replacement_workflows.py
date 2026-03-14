MANIFEST = {
  "schema_version": 1,
  "manifest_id": "nested-group-replacement-workflows",
  "layer": "module_workflow",
  "suite_id": "collection.replacement.nested_group",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "module-sub-template-nested-group-numbered-str",
      "operation": "module_call",
      "family": "nested_group_replacement_workflow",
      "helper": "sub",
      "args": [
        "a((b))d",
        "\\1x",
        "abdabd"
      ],
      "categories": ["workflow", "sub", "replacement-template", "nested-group", "numbered-group", "module", "str", "gap"],
      "notes": [
        "Publishes the bounded module-level nested-group replacement-template path for one capture nested inside another using a numbered outer-group template."
      ]
    },
    {
      "id": "module-subn-template-nested-group-numbered-str",
      "operation": "module_call",
      "family": "nested_group_replacement_workflow",
      "helper": "subn",
      "args": [
        "a((b))d",
        "\\2x",
        "abdabd",
        1
      ],
      "categories": ["workflow", "subn", "replacement-template", "nested-group", "numbered-group", "module", "str", "count", "gap"],
      "notes": [
        "Publishes the bounded module-level nested-group replacement-template count path for the same single nested capture site using the inner numbered group."
      ]
    },
    {
      "id": "pattern-sub-template-nested-group-numbered-str",
      "operation": "pattern_call",
      "family": "nested_group_replacement_workflow",
      "pattern": "a((b))d",
      "helper": "sub",
      "args": [
        "\\1x",
        "abdabd"
      ],
      "categories": ["workflow", "sub", "replacement-template", "nested-group", "numbered-group", "pattern", "str", "gap"],
      "notes": [
        "Publishes the bound Pattern.sub nested-group replacement-template path for the same one-site numbered nested capture shape."
      ]
    },
    {
      "id": "pattern-subn-template-nested-group-numbered-str",
      "operation": "pattern_call",
      "family": "nested_group_replacement_workflow",
      "pattern": "a((b))d",
      "helper": "subn",
      "args": [
        "\\2x",
        "abdabd",
        1
      ],
      "categories": ["workflow", "subn", "replacement-template", "nested-group", "numbered-group", "pattern", "str", "count", "gap"],
      "notes": [
        "Publishes the bound Pattern.subn nested-group replacement-template count path while keeping callable replacement, alternation, and broader template parsing out of scope."
      ]
    },
    {
      "id": "module-sub-template-nested-group-named-str",
      "operation": "module_call",
      "family": "named_nested_group_replacement_workflow",
      "helper": "sub",
      "args": [
        "a(?P<outer>(?P<inner>b))d",
        "\\g<outer>x",
        "abdabd"
      ],
      "categories": ["workflow", "sub", "replacement-template", "nested-group", "named-group", "module", "str", "gap"],
      "notes": [
        "Publishes the bounded module-level named nested-group replacement-template path for one named outer capture containing one named inner capture."
      ]
    },
    {
      "id": "module-subn-template-nested-group-named-str",
      "operation": "module_call",
      "family": "named_nested_group_replacement_workflow",
      "helper": "subn",
      "args": [
        "a(?P<outer>(?P<inner>b))d",
        "\\g<inner>x",
        "abdabd",
        1
      ],
      "categories": ["workflow", "subn", "replacement-template", "nested-group", "named-group", "module", "str", "count", "gap"],
      "notes": [
        "Publishes the bounded module-level named nested-group replacement-template count path for the inner named group without broadening into nested alternation or branch-local references."
      ]
    },
    {
      "id": "pattern-sub-template-nested-group-named-str",
      "operation": "pattern_call",
      "family": "named_nested_group_replacement_workflow",
      "pattern": "a(?P<outer>(?P<inner>b))d",
      "helper": "sub",
      "args": [
        "\\g<outer>x",
        "abdabd"
      ],
      "categories": ["workflow", "sub", "replacement-template", "nested-group", "named-group", "pattern", "str", "gap"],
      "notes": [
        "Publishes the bound Pattern.sub named nested-group replacement-template path for the same one-site named nested capture shape."
      ]
    },
    {
      "id": "pattern-subn-template-nested-group-named-str",
      "operation": "pattern_call",
      "family": "named_nested_group_replacement_workflow",
      "pattern": "a(?P<outer>(?P<inner>b))d",
      "helper": "subn",
      "args": [
        "\\g<inner>x",
        "abdabd",
        1
      ],
      "categories": ["workflow", "subn", "replacement-template", "nested-group", "named-group", "pattern", "str", "count", "gap"],
      "notes": [
        "Publishes the bound Pattern.subn named nested-group replacement-template count path while leaving callable replacement, alternation, and broader backtracking out of scope."
      ]
    }
  ]
}
