MANIFEST = {
  "schema_version": 1,
  "manifest_id": "optional-group-conditional-workflows",
  "layer": "match_behavior",
  "suite_id": "match.optional_group_conditional",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "optional-group-conditional-compile-metadata-str",
      "operation": "compile",
      "family": "optional_group_conditional_compile_metadata",
      "pattern": "a(b)?(?(1)c|d)e",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes one bounded numbered optional-group conditional compile path where the presence of the optional capture chooses between two single-literal branches before the trailing literal suffix."
      ]
    },
    {
      "id": "optional-group-conditional-module-search-present-str",
      "operation": "module_call",
      "family": "optional_group_conditional_module_present_workflow",
      "helper": "search",
      "args": ["a(b)?(?(1)c|d)e", "zzabcezz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the module-level numbered optional-group conditional search path when the capture is present so the conditional takes the yes-arm and exposes the populated group value."
      ]
    },
    {
      "id": "optional-group-conditional-pattern-fullmatch-absent-str",
      "operation": "pattern_call",
      "family": "optional_group_conditional_pattern_absent_workflow",
      "pattern": "a(b)?(?(1)c|d)e",
      "helper": "fullmatch",
      "args": ["ade"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "fullmatch", "pattern", "absent", "str", "gap"],
      "notes": [
        "Documents the bounded Pattern.fullmatch numbered optional-group conditional path when the capture is omitted so the scorecard records the observable None-valued group outcome and the no-arm literal branch."
      ]
    },
    {
      "id": "named-optional-group-conditional-compile-metadata-str",
      "operation": "compile",
      "family": "named_optional_group_conditional_compile_metadata",
      "pattern": "a(?P<word>b)?(?(word)c|d)e",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named optional-group conditional compile frontier for the same bounded capture-aware branch-selection shape."
      ]
    },
    {
      "id": "named-optional-group-conditional-module-search-present-str",
      "operation": "module_call",
      "family": "named_optional_group_conditional_module_present_workflow",
      "helper": "search",
      "args": ["a(?P<word>b)?(?(word)c|d)e", "zzabcezz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "named-group", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the module-level named optional-group conditional search path when the optional named capture is present so the yes-arm executes and the named group remains observable."
      ]
    },
    {
      "id": "named-optional-group-conditional-pattern-fullmatch-absent-str",
      "operation": "pattern_call",
      "family": "named_optional_group_conditional_pattern_absent_workflow",
      "pattern": "a(?P<word>b)?(?(word)c|d)e",
      "helper": "fullmatch",
      "args": ["ade"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "named-group", "fullmatch", "pattern", "absent", "str", "gap"],
      "notes": [
        "Documents the bounded Pattern.fullmatch named optional-group conditional path when the capture is omitted so the named-group None payload stays explicit in the published gap."
      ]
    }
  ]
}
