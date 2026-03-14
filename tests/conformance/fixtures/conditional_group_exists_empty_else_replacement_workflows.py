MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-empty-else-replacement-workflows",
  "layer": "module_workflow",
  "suite_id": "collection.replacement.conditional_group_exists_empty_else",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "module-sub-conditional-group-exists-empty-else-replacement-present-str",
      "operation": "module_call",
      "family": "conditional_group_exists_empty_else_replacement_present_workflow",
      "helper": "sub",
      "args": [
        "a(b)?c(?(1)d|)",
        "X",
        "zzabcdzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "empty-else", "module", "present", "str", "gap"],
      "notes": [
        "Publishes one bounded module-level explicit-empty-else conditional replacement path where the optional numbered capture is present and the literal yes arm participates in the matched span before a constant replacement is applied."
      ]
    },
    {
      "id": "module-subn-conditional-group-exists-empty-else-replacement-absent-str",
      "operation": "module_call",
      "family": "conditional_group_exists_empty_else_replacement_absent_count_workflow",
      "helper": "subn",
      "args": [
        "a(b)?c(?(1)d|)",
        "X",
        "zzaczz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "empty-else", "module", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the matching module-level explicit-empty-else conditional replacement count path when the numbered capture is absent, keeping the accepted `|)` spelling explicit without broadening into replacement templates, callbacks, or nested conditionals."
      ]
    },
    {
      "id": "pattern-sub-conditional-group-exists-empty-else-replacement-present-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_empty_else_replacement_present_workflow",
      "pattern": "a(b)?c(?(1)d|)",
      "helper": "sub",
      "args": [
        "X",
        "zzabcdzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "empty-else", "pattern", "present", "str", "gap"],
      "notes": [
        "Publishes the bound Pattern.sub explicit-empty-else conditional replacement path for the same numbered present-capture workflow."
      ]
    },
    {
      "id": "pattern-subn-conditional-group-exists-empty-else-replacement-absent-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_empty_else_replacement_absent_count_workflow",
      "pattern": "a(b)?c(?(1)d|)",
      "helper": "subn",
      "args": [
        "X",
        "zzaczz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "empty-else", "pattern", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the bound Pattern.subn explicit-empty-else conditional replacement count path when the numbered capture is absent so the compiled-entrypoint gap stays visible too."
      ]
    },
    {
      "id": "module-sub-named-conditional-group-exists-empty-else-replacement-present-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_empty_else_replacement_present_workflow",
      "helper": "sub",
      "args": [
        "a(?P<word>b)?c(?(word)d|)",
        "X",
        "zzabcdzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "empty-else", "named-group", "module", "present", "str", "gap"],
      "notes": [
        "Publishes the bounded module-level named explicit-empty-else conditional replacement path for the same tiny optional-capture shape."
      ]
    },
    {
      "id": "module-subn-named-conditional-group-exists-empty-else-replacement-absent-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_empty_else_replacement_absent_count_workflow",
      "helper": "subn",
      "args": [
        "a(?P<word>b)?c(?(word)d|)",
        "X",
        "zzaczz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "empty-else", "named-group", "module", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the matching module-level named explicit-empty-else conditional replacement count path when the named capture is absent without broadening into named templates or callable replacement semantics."
      ]
    },
    {
      "id": "pattern-sub-named-conditional-group-exists-empty-else-replacement-present-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_empty_else_replacement_present_workflow",
      "pattern": "a(?P<word>b)?c(?(word)d|)",
      "helper": "sub",
      "args": [
        "X",
        "zzabcdzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "empty-else", "named-group", "pattern", "present", "str", "gap"],
      "notes": [
        "Publishes the bound Pattern.sub named explicit-empty-else conditional replacement path for the same present-capture workflow."
      ]
    },
    {
      "id": "pattern-subn-named-conditional-group-exists-empty-else-replacement-absent-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_empty_else_replacement_absent_count_workflow",
      "pattern": "a(?P<word>b)?c(?(word)d|)",
      "helper": "subn",
      "args": [
        "X",
        "zzaczz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "empty-else", "named-group", "pattern", "absent", "str", "count", "gap"],
      "notes": [
        "Publishes the bound Pattern.subn named explicit-empty-else conditional replacement count path when the named capture is absent so the smallest compiled conditional-replacement gap for the accepted `|)` spelling stays explicit in the scorecard."
      ]
    }
  ]
}
