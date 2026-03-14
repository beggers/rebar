MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-fully-empty-workflows",
  "layer": "match_behavior",
  "suite_id": "match.conditional_group_exists_fully_empty",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "conditional-group-exists-fully-empty-compile-metadata-str",
      "operation": "compile",
      "family": "conditional_group_exists_fully_empty_compile_metadata",
      "pattern": "a(b)?c(?(1)|)",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "fully-empty", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes one bounded numbered group-exists conditional compile path where an already-open optional capture controls explicitly empty yes and else arms spelled `(?(1)|)`."
      ]
    },
    {
      "id": "conditional-group-exists-fully-empty-module-search-present-str",
      "operation": "module_call",
      "family": "conditional_group_exists_fully_empty_module_present_workflow",
      "helper": "search",
      "args": ["a(b)?c(?(1)|)", "zzabczz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "fully-empty", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the module-level numbered conditional search path when the optional capture is present so the scorecard records zero-width success for the explicit fully empty spelling while preserving the populated capture."
      ]
    },
    {
      "id": "conditional-group-exists-fully-empty-pattern-fullmatch-absent-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_fully_empty_pattern_absent_workflow",
      "pattern": "a(b)?c(?(1)|)",
      "helper": "fullmatch",
      "args": ["ac"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "fully-empty", "fullmatch", "pattern", "absent", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch numbered conditional path when the optional capture is omitted so the published scorecard keeps the None-valued group explicit even though both conditional arms are empty."
      ]
    },
    {
      "id": "named-conditional-group-exists-fully-empty-compile-metadata-str",
      "operation": "compile",
      "family": "named_conditional_group_exists_fully_empty_compile_metadata",
      "pattern": "a(?P<word>b)?c(?(word)|)",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "fully-empty", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named fully empty conditional compile frontier for the same bounded optional-capture shape."
      ]
    },
    {
      "id": "named-conditional-group-exists-fully-empty-module-search-present-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_fully_empty_module_present_workflow",
      "helper": "search",
      "args": ["a(?P<word>b)?c(?(word)|)", "zzabczz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "fully-empty", "named-group", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the module-level named conditional search path when the optional named capture is present so the published gap records the accepted fully empty spelling separately from the earlier empty-yes-arm slice."
      ]
    },
    {
      "id": "named-conditional-group-exists-fully-empty-pattern-fullmatch-absent-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_fully_empty_pattern_absent_workflow",
      "pattern": "a(?P<word>b)?c(?(word)|)",
      "helper": "fullmatch",
      "args": ["ac"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "fully-empty", "named-group", "fullmatch", "pattern", "absent", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch named conditional path when the optional capture is omitted so the named-group None payload remains explicit for the CPython-accepted fully empty spelling."
      ]
    }
  ]
}
