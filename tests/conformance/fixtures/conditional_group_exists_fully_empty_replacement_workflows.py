MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-fully-empty-replacement-workflows",
  "layer": "module_workflow",
  "suite_id": "collection.replacement.conditional_group_exists_fully_empty",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "module-sub-conditional-group-exists-fully-empty-replacement-present-str",
      "operation": "module_call",
      "family": "conditional_group_exists_fully_empty_replacement_present_workflow",
      "helper": "sub",
      "args": [
        "a(b)?c(?(1)|)",
        "X",
        "zzabczz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "fully-empty", "module", "present", "str", "gap"],
      "notes": [
        "Publishes one bounded module-level fully-empty conditional replacement path where the optional numbered capture is present and the accepted `(?(1)|)` spelling keeps the matched span at `abc` before a constant replacement is applied."
      ]
    },
    {
      "id": "module-subn-conditional-group-exists-fully-empty-replacement-absent-str",
      "operation": "module_call",
      "family": "conditional_group_exists_fully_empty_replacement_absent_count_workflow",
      "helper": "subn",
      "args": [
        "a(b)?c(?(1)|)",
        "X",
        "zzaczz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "fully-empty", "module", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the matching module-level fully-empty conditional replacement count path when the numbered capture is absent, keeping the accepted empty-arm spelling explicit without broadening into templates, callbacks, nested conditionals, or wider backtracking."
      ]
    },
    {
      "id": "pattern-sub-conditional-group-exists-fully-empty-replacement-present-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_fully_empty_replacement_present_workflow",
      "pattern": "a(b)?c(?(1)|)",
      "helper": "sub",
      "args": [
        "X",
        "zzabczz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "fully-empty", "pattern", "present", "str", "gap"],
      "notes": [
        "Publishes the bound Pattern.sub fully-empty conditional replacement path for the same numbered present-capture workflow."
      ]
    },
    {
      "id": "pattern-subn-conditional-group-exists-fully-empty-replacement-absent-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_fully_empty_replacement_absent_count_workflow",
      "pattern": "a(b)?c(?(1)|)",
      "helper": "subn",
      "args": [
        "X",
        "zzaczz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "fully-empty", "pattern", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the bound Pattern.subn fully-empty conditional replacement count path when the numbered capture is absent so the compiled-entrypoint gap stays visible too."
      ]
    },
    {
      "id": "module-sub-named-conditional-group-exists-fully-empty-replacement-present-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_fully_empty_replacement_present_workflow",
      "helper": "sub",
      "args": [
        "a(?P<word>b)?c(?(word)|)",
        "X",
        "zzabczz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "fully-empty", "named-group", "module", "present", "str", "gap"],
      "notes": [
        "Publishes the bounded module-level named fully-empty conditional replacement path for the same tiny optional-capture shape."
      ]
    },
    {
      "id": "module-subn-named-conditional-group-exists-fully-empty-replacement-absent-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_fully_empty_replacement_absent_count_workflow",
      "helper": "subn",
      "args": [
        "a(?P<word>b)?c(?(word)|)",
        "X",
        "zzaczz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "fully-empty", "named-group", "module", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the matching module-level named fully-empty conditional replacement count path when the named capture is absent without broadening into named templates or callable replacement semantics."
      ]
    },
    {
      "id": "pattern-sub-named-conditional-group-exists-fully-empty-replacement-present-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_fully_empty_replacement_present_workflow",
      "pattern": "a(?P<word>b)?c(?(word)|)",
      "helper": "sub",
      "args": [
        "X",
        "zzabczz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "fully-empty", "named-group", "pattern", "present", "str", "gap"],
      "notes": [
        "Publishes the bound Pattern.sub named fully-empty conditional replacement path for the same present-capture workflow."
      ]
    },
    {
      "id": "pattern-subn-named-conditional-group-exists-fully-empty-replacement-absent-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_fully_empty_replacement_absent_count_workflow",
      "pattern": "a(?P<word>b)?c(?(word)|)",
      "helper": "subn",
      "args": [
        "X",
        "zzaczz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "fully-empty", "named-group", "pattern", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the bound Pattern.subn named fully-empty conditional replacement count path when the named capture is absent so the smallest compiled fully-empty conditional-replacement gap stays explicit in the scorecard."
      ]
    }
  ]
}
