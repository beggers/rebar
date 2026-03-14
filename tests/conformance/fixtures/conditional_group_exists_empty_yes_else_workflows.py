MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-empty-yes-else-workflows",
  "layer": "match_behavior",
  "suite_id": "match.conditional_group_exists_empty_yes_else",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "conditional-group-exists-empty-yes-else-compile-metadata-str",
      "operation": "compile",
      "family": "conditional_group_exists_empty_yes_else_compile_metadata",
      "pattern": "a(b)?c(?(1)|e)",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-yes", "else", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes one bounded numbered group-exists conditional compile path where an already-open optional capture controls an explicit empty yes arm and a literal else arm."
      ]
    },
    {
      "id": "conditional-group-exists-empty-yes-else-module-search-present-str",
      "operation": "module_call",
      "family": "conditional_group_exists_empty_yes_else_module_present_workflow",
      "helper": "search",
      "args": ["a(b)?c(?(1)|e)", "zzabczz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-yes", "else", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the module-level numbered conditional search path when the optional capture is present so the explicit empty yes arm succeeds at zero width and exposes the populated group value."
      ]
    },
    {
      "id": "conditional-group-exists-empty-yes-else-pattern-fullmatch-absent-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_empty_yes_else_pattern_absent_workflow",
      "pattern": "a(b)?c(?(1)|e)",
      "helper": "fullmatch",
      "args": ["ace"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-yes", "else", "fullmatch", "pattern", "absent", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch numbered conditional path when the optional capture is omitted so the else arm literal remains explicit in the published scorecard."
      ]
    },
    {
      "id": "named-conditional-group-exists-empty-yes-else-compile-metadata-str",
      "operation": "compile",
      "family": "named_conditional_group_exists_empty_yes_else_compile_metadata",
      "pattern": "a(?P<word>b)?c(?(word)|e)",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-yes", "else", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named empty-yes-arm conditional compile frontier for the same bounded optional-capture shape."
      ]
    },
    {
      "id": "named-conditional-group-exists-empty-yes-else-module-search-present-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_empty_yes_else_module_present_workflow",
      "helper": "search",
      "args": ["a(?P<word>b)?c(?(word)|e)", "zzabczz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-yes", "else", "named-group", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the module-level named conditional search path when the optional named capture is present so the published gap records the explicit empty yes arm separately from the fully empty conditional form."
      ]
    },
    {
      "id": "named-conditional-group-exists-empty-yes-else-pattern-fullmatch-absent-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_empty_yes_else_pattern_absent_workflow",
      "pattern": "a(?P<word>b)?c(?(word)|e)",
      "helper": "fullmatch",
      "args": ["ace"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-yes", "else", "named-group", "fullmatch", "pattern", "absent", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch named conditional path when the optional capture is omitted so the named-group None payload remains explicit for the CPython-accepted empty-yes-arm spelling."
      ]
    }
  ]
}
