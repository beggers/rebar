MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-empty-else-workflows",
  "layer": "match_behavior",
  "suite_id": "match.conditional_group_exists_empty_else",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "conditional-group-exists-empty-else-compile-metadata-str",
      "operation": "compile",
      "family": "conditional_group_exists_empty_else_compile_metadata",
      "pattern": "a(b)?c(?(1)d|)",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-else", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes one bounded numbered group-exists conditional compile path where an already-open optional capture controls a literal yes-arm with an explicit empty else arm spelled `|)`."
      ]
    },
    {
      "id": "conditional-group-exists-empty-else-module-search-present-str",
      "operation": "module_call",
      "family": "conditional_group_exists_empty_else_module_present_workflow",
      "helper": "search",
      "args": ["a(b)?c(?(1)d|)", "zzabcdzz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-else", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the module-level numbered conditional search path when the optional capture is present so the explicit-empty-else syntax still takes the yes-arm and exposes the populated group value."
      ]
    },
    {
      "id": "conditional-group-exists-empty-else-pattern-fullmatch-absent-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_empty_else_pattern_absent_workflow",
      "pattern": "a(b)?c(?(1)d|)",
      "helper": "fullmatch",
      "args": ["ac"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-else", "fullmatch", "pattern", "absent", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch numbered conditional path when the optional capture is omitted so the published scorecard keeps the None-valued capture explicit even though the else arm is empty."
      ]
    },
    {
      "id": "named-conditional-group-exists-empty-else-compile-metadata-str",
      "operation": "compile",
      "family": "named_conditional_group_exists_empty_else_compile_metadata",
      "pattern": "a(?P<word>b)?c(?(word)d|)",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-else", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named explicit-empty-else conditional compile frontier for the same bounded optional-capture shape."
      ]
    },
    {
      "id": "named-conditional-group-exists-empty-else-module-search-present-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_empty_else_module_present_workflow",
      "helper": "search",
      "args": ["a(?P<word>b)?c(?(word)d|)", "zzabcdzz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-else", "named-group", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the module-level named conditional search path when the optional named capture is present so the published gap records the explicit `|)` spelling separately from the omitted-no-arm slice."
      ]
    },
    {
      "id": "named-conditional-group-exists-empty-else-pattern-fullmatch-absent-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_empty_else_pattern_absent_workflow",
      "pattern": "a(?P<word>b)?c(?(word)d|)",
      "helper": "fullmatch",
      "args": ["ac"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-else", "named-group", "fullmatch", "pattern", "absent", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch named conditional path when the optional capture is omitted so the named-group None payload remains explicit for the CPython-accepted explicit-empty-else spelling."
      ]
    }
  ]
}
