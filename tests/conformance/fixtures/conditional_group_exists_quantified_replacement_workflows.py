MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-quantified-replacement-workflows",
  "layer": "module_workflow",
  "suite_id": "collection.replacement.conditional_group_exists_quantified",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "module-sub-conditional-group-exists-quantified-replacement-present-str",
      "operation": "module_call",
      "family": "conditional_group_exists_quantified_replacement_present_workflow",
      "helper": "sub",
      "args": [
        "a(b)?c(?(1)d|e){2}",
        "X",
        "zzabcddzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "quantified", "exact-repeat", "module", "present", "str", "gap"],
      "notes": [
        "Publishes one bounded numbered module-level quantified two-arm conditional replacement path where the optional capture is present and the repeated yes arm requires `dd` before constant replacement text is emitted."
      ]
    },
    {
      "id": "module-subn-conditional-group-exists-quantified-replacement-absent-str",
      "operation": "module_call",
      "family": "conditional_group_exists_quantified_replacement_absent_count_workflow",
      "helper": "subn",
      "args": [
        "a(b)?c(?(1)d|e){2}",
        "X",
        "zzaceezz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "quantified", "exact-repeat", "module", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the matching numbered module-level quantified conditional replacement count path when the optional capture is absent and the repeated else arm requires `ee`, without broadening into capture-reading templates, callbacks, alternation-heavy arms, or wider repeats."
      ]
    },
    {
      "id": "pattern-sub-conditional-group-exists-quantified-replacement-present-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_quantified_replacement_present_workflow",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "helper": "sub",
      "args": [
        "X",
        "zzabcddzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "quantified", "exact-repeat", "pattern", "present", "str", "gap"],
      "notes": [
        "Publishes the bounded Pattern.sub numbered quantified two-arm conditional replacement path for the same present-capture `dd` workflow."
      ]
    },
    {
      "id": "pattern-subn-conditional-group-exists-quantified-replacement-absent-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_quantified_replacement_absent_count_workflow",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "helper": "subn",
      "args": [
        "X",
        "zzaceezz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "quantified", "exact-repeat", "pattern", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the bounded Pattern.subn numbered quantified two-arm conditional replacement count path when the optional capture is absent so the compiled quantified replacement gap stays explicit too."
      ]
    },
    {
      "id": "module-sub-named-conditional-group-exists-quantified-replacement-present-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_quantified_replacement_present_workflow",
      "helper": "sub",
      "args": [
        "a(?P<word>b)?c(?(word)d|e){2}",
        "X",
        "zzabcddzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "quantified", "exact-repeat", "named-group", "module", "present", "str", "gap"],
      "notes": [
        "Publishes the bounded named module-level quantified two-arm conditional replacement path for the same tiny exact-repeat shape."
      ]
    },
    {
      "id": "module-subn-named-conditional-group-exists-quantified-replacement-absent-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_quantified_replacement_absent_count_workflow",
      "helper": "subn",
      "args": [
        "a(?P<word>b)?c(?(word)d|e){2}",
        "X",
        "zzaceezz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "quantified", "exact-repeat", "named-group", "module", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the matching named module-level quantified conditional replacement count path when the named capture is absent and the repeated else arm contributes `ee`, without broadening into named replacement templates or callable replacement semantics."
      ]
    },
    {
      "id": "pattern-sub-named-conditional-group-exists-quantified-replacement-present-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_quantified_replacement_present_workflow",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "helper": "sub",
      "args": [
        "X",
        "zzabcddzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "quantified", "exact-repeat", "named-group", "pattern", "present", "str", "gap"],
      "notes": [
        "Publishes the bounded Pattern.sub named quantified two-arm conditional replacement path for the same present-capture `dd` workflow."
      ]
    },
    {
      "id": "pattern-subn-named-conditional-group-exists-quantified-replacement-absent-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_quantified_replacement_absent_count_workflow",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "helper": "subn",
      "args": [
        "X",
        "zzaceezz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "quantified", "exact-repeat", "named-group", "pattern", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the bounded Pattern.subn named quantified two-arm conditional replacement count path when the named capture is absent so the smallest compiled quantified replacement gap remains visible in the scorecard."
      ]
    }
  ]
}
