MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-no-else-workflows",
  "layer": "match_behavior",
  "suite_id": "match.conditional_group_exists_no_else",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "conditional-group-exists-no-else-compile-metadata-str",
      "operation": "compile",
      "family": "conditional_group_exists_no_else_compile_metadata",
      "pattern": "a(b)?c(?(1)d)",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "no-else", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes one bounded numbered group-exists conditional compile path where an already-open optional capture controls a literal yes-arm with no explicit else branch."
      ]
    },
    {
      "id": "conditional-group-exists-no-else-module-search-present-str",
      "operation": "module_call",
      "family": "conditional_group_exists_no_else_module_present_workflow",
      "helper": "search",
      "args": ["a(b)?c(?(1)d)", "zzabcdzz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "no-else", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the module-level numbered conditional search path when the optional capture is present so the no-else conditional still consumes the yes-arm literal suffix."
      ]
    },
    {
      "id": "conditional-group-exists-no-else-pattern-fullmatch-absent-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_no_else_pattern_absent_workflow",
      "pattern": "a(b)?c(?(1)d)",
      "helper": "fullmatch",
      "args": ["ac"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "no-else", "fullmatch", "pattern", "absent", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch numbered conditional path when the optional capture is omitted so the published scorecard keeps the None-valued capture and omitted else-arm behavior explicit."
      ]
    },
    {
      "id": "named-conditional-group-exists-no-else-compile-metadata-str",
      "operation": "compile",
      "family": "named_conditional_group_exists_no_else_compile_metadata",
      "pattern": "a(?P<word>b)?c(?(word)d)",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "no-else", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named omitted-no-arm conditional compile frontier for the same bounded optional-capture shape."
      ]
    },
    {
      "id": "named-conditional-group-exists-no-else-module-search-present-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_no_else_module_present_workflow",
      "helper": "search",
      "args": ["a(?P<word>b)?c(?(word)d)", "zzabcdzz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "no-else", "named-group", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the module-level named conditional search path when the optional named capture is present so the published gap records the yes-arm execution without an explicit else branch."
      ]
    },
    {
      "id": "named-conditional-group-exists-no-else-pattern-fullmatch-absent-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_no_else_pattern_absent_workflow",
      "pattern": "a(?P<word>b)?c(?(word)d)",
      "helper": "fullmatch",
      "args": ["ac"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "no-else", "named-group", "fullmatch", "pattern", "absent", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch named conditional path when the optional capture is omitted so the named-group None payload remains explicit in the published omitted-no-arm gap."
      ]
    }
  ]
}
