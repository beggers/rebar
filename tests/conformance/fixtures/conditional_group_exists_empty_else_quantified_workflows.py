MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-empty-else-quantified-workflows",
  "layer": "match_behavior",
  "suite_id": "match.conditional_group_exists_empty_else_quantified",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "conditional-group-exists-empty-else-quantified-compile-metadata-str",
      "operation": "compile",
      "family": "conditional_group_exists_empty_else_quantified_compile_metadata",
      "pattern": "a(b)?c(?(1)d|){2}",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-else", "quantified", "exact-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes one bounded numbered quantified explicit-empty-else conditional compile path whose accepted `{2}` repeated site keeps the `|)` spelling explicit instead of collapsing into the already-published omitted-no-arm form."
      ]
    },
    {
      "id": "conditional-group-exists-empty-else-quantified-module-search-present-str",
      "operation": "module_call",
      "family": "conditional_group_exists_empty_else_quantified_module_present_workflow",
      "helper": "search",
      "args": ["a(b)?c(?(1)d|){2}", "zzabcddzz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-else", "quantified", "exact-repeat", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the numbered module-level quantified explicit-empty-else search path when the optional capture is present so the repeated yes arm still requires the doubled `d` suffix."
      ]
    },
    {
      "id": "conditional-group-exists-empty-else-quantified-module-fullmatch-absent-str",
      "operation": "module_call",
      "family": "conditional_group_exists_empty_else_quantified_module_absent_workflow",
      "helper": "fullmatch",
      "args": ["a(b)?c(?(1)d|){2}", "ac"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-else", "quantified", "exact-repeat", "fullmatch", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the numbered module-level quantified explicit-empty-else fullmatch path when the optional capture is absent so both explicit empty else branches stay zero-width and `ac` still succeeds."
      ]
    },
    {
      "id": "conditional-group-exists-empty-else-quantified-pattern-fullmatch-missing-repeat-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_empty_else_quantified_pattern_missing_repeat_workflow",
      "pattern": "a(b)?c(?(1)d|){2}",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-else", "quantified", "exact-repeat", "fullmatch", "pattern", "present", "failure", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch numbered quantified explicit-empty-else failure path when the capture is present but only one repeated yes-arm `d` is supplied instead of the required `{2}` count."
      ]
    },
    {
      "id": "named-conditional-group-exists-empty-else-quantified-compile-metadata-str",
      "operation": "compile",
      "family": "named_conditional_group_exists_empty_else_quantified_compile_metadata",
      "pattern": "a(?P<word>b)?c(?(word)d|){2}",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-else", "quantified", "exact-repeat", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named quantified explicit-empty-else conditional compile frontier for the same bounded `{2}` repeated site."
      ]
    },
    {
      "id": "named-conditional-group-exists-empty-else-quantified-module-search-present-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_empty_else_quantified_module_present_workflow",
      "helper": "search",
      "args": ["a(?P<word>b)?c(?(word)d|){2}", "zzabcddzz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-else", "quantified", "exact-repeat", "named-group", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the named module-level quantified explicit-empty-else search path when the optional named capture is present so the repeated yes arm still requires the doubled `d` suffix."
      ]
    },
    {
      "id": "named-conditional-group-exists-empty-else-quantified-module-fullmatch-absent-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_empty_else_quantified_module_absent_workflow",
      "helper": "fullmatch",
      "args": ["a(?P<word>b)?c(?(word)d|){2}", "ac"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-else", "quantified", "exact-repeat", "named-group", "fullmatch", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the named module-level quantified explicit-empty-else fullmatch path when the optional named capture is absent so both explicit empty else branches stay zero-width."
      ]
    },
    {
      "id": "named-conditional-group-exists-empty-else-quantified-pattern-fullmatch-missing-repeat-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_empty_else_quantified_pattern_missing_repeat_workflow",
      "pattern": "a(?P<word>b)?c(?(word)d|){2}",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-else", "quantified", "exact-repeat", "named-group", "fullmatch", "pattern", "present", "failure", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch named quantified explicit-empty-else failure path when the optional named capture is present but the repeated yes arm is supplied only once."
      ]
    }
  ]
}
