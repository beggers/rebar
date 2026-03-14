MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-nested-replacement-workflows",
  "layer": "module_workflow",
  "suite_id": "collection.replacement.conditional_group_exists_nested",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "module-sub-conditional-group-exists-nested-replacement-present-str",
      "operation": "module_call",
      "family": "conditional_group_exists_nested_replacement_present_workflow",
      "helper": "sub",
      "args": [
        "a(b)?c(?(1)(?(1)d|e)|f)",
        "X",
        "zzabcdzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "nested", "module", "present", "str", "gap"],
      "notes": [
        "Publishes one bounded numbered module-level nested two-arm conditional replacement path where the outer yes arm stays taken, the inner nested yes arm still requires `d`, and only then is constant replacement text emitted."
      ]
    },
    {
      "id": "module-subn-conditional-group-exists-nested-replacement-absent-str",
      "operation": "module_call",
      "family": "conditional_group_exists_nested_replacement_absent_count_workflow",
      "helper": "subn",
      "args": [
        "a(b)?c(?(1)(?(1)d|e)|f)",
        "X",
        "zzacfzz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "nested", "module", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the matching numbered module-level nested replacement count path when the optional capture is absent and the outer else arm contributes `f`, keeping the smallest absent-capture nested replacement outcome explicit without widening to deeper nesting or quantified repeats."
      ]
    },
    {
      "id": "pattern-sub-conditional-group-exists-nested-replacement-present-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_nested_replacement_present_workflow",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "helper": "sub",
      "args": [
        "X",
        "zzabcdzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "nested", "pattern", "present", "str", "gap"],
      "notes": [
        "Publishes the bound Pattern.sub numbered nested two-arm conditional replacement path for the same present-capture workflow."
      ]
    },
    {
      "id": "pattern-subn-conditional-group-exists-nested-replacement-absent-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_nested_replacement_absent_count_workflow",
      "pattern": "a(b)?c(?(1)(?(1)d|e)|f)",
      "helper": "subn",
      "args": [
        "X",
        "zzacfzz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "nested", "pattern", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the bound Pattern.subn numbered nested two-arm conditional replacement count path when the optional capture is absent and the outer else arm contributes `f`."
      ]
    },
    {
      "id": "module-sub-named-conditional-group-exists-nested-replacement-present-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_nested_replacement_present_workflow",
      "helper": "sub",
      "args": [
        "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
        "X",
        "zzabcdzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "nested", "named-group", "module", "present", "str", "gap"],
      "notes": [
        "Publishes the matching named module-level nested two-arm conditional replacement path where the named outer and inner yes arms both stay on the `d`-requiring branch before replacement."
      ]
    },
    {
      "id": "module-subn-named-conditional-group-exists-nested-replacement-absent-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_nested_replacement_absent_count_workflow",
      "helper": "subn",
      "args": [
        "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
        "X",
        "zzacfzz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "nested", "named-group", "module", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the matching named module-level nested replacement count path when the named capture is absent and the outer else arm contributes `f`."
      ]
    },
    {
      "id": "pattern-sub-named-conditional-group-exists-nested-replacement-present-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_nested_replacement_present_workflow",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "helper": "sub",
      "args": [
        "X",
        "zzabcdzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "nested", "named-group", "pattern", "present", "str", "gap"],
      "notes": [
        "Publishes the bound Pattern.sub named nested two-arm conditional replacement path for the same present-capture workflow."
      ]
    },
    {
      "id": "pattern-subn-named-conditional-group-exists-nested-replacement-absent-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_nested_replacement_absent_count_workflow",
      "pattern": "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
      "helper": "subn",
      "args": [
        "X",
        "zzacfzz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "nested", "named-group", "pattern", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the bound Pattern.subn named nested two-arm conditional replacement count path when the named capture is absent so the smallest named nested replacement gap remains visible in the scorecard."
      ]
    }
  ]
}
