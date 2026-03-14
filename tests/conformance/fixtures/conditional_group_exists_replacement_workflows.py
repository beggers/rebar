MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-replacement-workflows",
  "layer": "module_workflow",
  "suite_id": "collection.replacement.conditional_group_exists",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "module-sub-conditional-group-exists-replacement-present-str",
      "operation": "module_call",
      "family": "conditional_group_exists_replacement_present_workflow",
      "helper": "sub",
      "args": [
        "a(b)?c(?(1)d|e)",
        "X",
        "zzabcdzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "module", "present", "str", "gap"],
      "notes": [
        "Publishes one bounded module-level two-arm conditional replacement path where the optional numbered capture is present and the yes-arm literal `d` extends the matched span before a constant replacement is applied."
      ]
    },
    {
      "id": "module-subn-conditional-group-exists-replacement-absent-str",
      "operation": "module_call",
      "family": "conditional_group_exists_replacement_absent_count_workflow",
      "helper": "subn",
      "args": [
        "a(b)?c(?(1)d|e)",
        "X",
        "zzacezz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "module", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the matching module-level two-arm conditional replacement count path when the numbered capture is absent and the else-arm literal `e` instead contributes to the matched span, without broadening into replacement templates, callbacks, alternation-heavy arms, or nested conditionals."
      ]
    },
    {
      "id": "pattern-sub-conditional-group-exists-replacement-present-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_replacement_present_workflow",
      "pattern": "a(b)?c(?(1)d|e)",
      "helper": "sub",
      "args": [
        "X",
        "zzabcdzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "pattern", "present", "str", "gap"],
      "notes": [
        "Publishes the bound Pattern.sub two-arm conditional replacement path for the same numbered present-capture workflow."
      ]
    },
    {
      "id": "pattern-subn-conditional-group-exists-replacement-absent-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_replacement_absent_count_workflow",
      "pattern": "a(b)?c(?(1)d|e)",
      "helper": "subn",
      "args": [
        "X",
        "zzacezz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "pattern", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the bound Pattern.subn two-arm conditional replacement count path when the numbered capture is absent so the compiled-entrypoint gap for the `d|e` branch split stays visible too."
      ]
    },
    {
      "id": "module-sub-named-conditional-group-exists-replacement-present-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_replacement_present_workflow",
      "helper": "sub",
      "args": [
        "a(?P<word>b)?c(?(word)d|e)",
        "X",
        "zzabcdzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "named-group", "module", "present", "str", "gap"],
      "notes": [
        "Publishes the bounded module-level named two-arm conditional replacement path for the same tiny optional-capture shape."
      ]
    },
    {
      "id": "module-subn-named-conditional-group-exists-replacement-absent-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_replacement_absent_count_workflow",
      "helper": "subn",
      "args": [
        "a(?P<word>b)?c(?(word)d|e)",
        "X",
        "zzacezz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "named-group", "module", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the matching module-level named two-arm conditional replacement count path when the named capture is absent and the else arm contributes `e`, without broadening into named templates or callable replacement semantics."
      ]
    },
    {
      "id": "pattern-sub-named-conditional-group-exists-replacement-present-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_replacement_present_workflow",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "helper": "sub",
      "args": [
        "X",
        "zzabcdzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "named-group", "pattern", "present", "str", "gap"],
      "notes": [
        "Publishes the bound Pattern.sub named two-arm conditional replacement path for the same present-capture workflow."
      ]
    },
    {
      "id": "pattern-subn-named-conditional-group-exists-replacement-absent-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_replacement_absent_count_workflow",
      "pattern": "a(?P<word>b)?c(?(word)d|e)",
      "helper": "subn",
      "args": [
        "X",
        "zzacezz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "named-group", "pattern", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the bound Pattern.subn named two-arm conditional replacement count path when the named capture is absent so the smallest compiled conditional-replacement gap for the `d|e` branch split stays explicit in the scorecard."
      ]
    }
  ]
}
