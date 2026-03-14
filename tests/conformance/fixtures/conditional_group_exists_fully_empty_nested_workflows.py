MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-fully-empty-nested-workflows",
  "layer": "match_behavior",
  "suite_id": "match.conditional_group_exists_fully_empty_nested",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "conditional-group-exists-fully-empty-nested-compile-metadata-str",
      "operation": "compile",
      "family": "conditional_group_exists_fully_empty_nested_compile_metadata",
      "pattern": "a(b)?c(?(1)|(?(1)|))",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "fully-empty", "nested", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes one bounded numbered nested fully-empty conditional compile path whose outer else arm contains a single nested fully-empty conditional site so the accepted `|(?(1)|)` spelling stays explicit in the scorecard."
      ]
    },
    {
      "id": "conditional-group-exists-fully-empty-nested-module-search-present-str",
      "operation": "module_call",
      "family": "conditional_group_exists_fully_empty_nested_module_present_workflow",
      "helper": "search",
      "args": ["a(b)?c(?(1)|(?(1)|))", "zzabczz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "fully-empty", "nested", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the numbered module-level nested fully-empty search path when the optional capture is present so the outer yes arm succeeds at zero width and the nested site is bypassed."
      ]
    },
    {
      "id": "conditional-group-exists-fully-empty-nested-module-fullmatch-absent-str",
      "operation": "module_call",
      "family": "conditional_group_exists_fully_empty_nested_module_absent_workflow",
      "helper": "fullmatch",
      "args": ["a(b)?c(?(1)|(?(1)|))", "ac"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "fully-empty", "nested", "fullmatch", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the numbered module-level nested fully-empty fullmatch path when the optional capture is absent so the outer else arm selects the nested conditional and its fully empty absent branch contributes no suffix."
      ]
    },
    {
      "id": "conditional-group-exists-fully-empty-nested-pattern-fullmatch-extra-suffix-failure-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_fully_empty_nested_pattern_extra_suffix_failure_workflow",
      "pattern": "a(b)?c(?(1)|(?(1)|))",
      "helper": "fullmatch",
      "args": ["acf"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "fully-empty", "nested", "fullmatch", "pattern", "absent", "failure", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch numbered nested fully-empty failure path when the optional capture is absent so the scorecard proves this slice does not silently broaden into the earlier nested empty-yes-arm spelling."
      ]
    },
    {
      "id": "named-conditional-group-exists-fully-empty-nested-compile-metadata-str",
      "operation": "compile",
      "family": "named_conditional_group_exists_fully_empty_nested_compile_metadata",
      "pattern": "a(?P<word>b)?c(?(word)|(?(word)|))",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "fully-empty", "nested", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named nested fully-empty conditional compile frontier for the same bounded single-site nested shape."
      ]
    },
    {
      "id": "named-conditional-group-exists-fully-empty-nested-module-search-present-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_fully_empty_nested_module_present_workflow",
      "helper": "search",
      "args": ["a(?P<word>b)?c(?(word)|(?(word)|))", "zzabczz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "fully-empty", "nested", "named-group", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the named module-level nested fully-empty search path when the optional named capture is present so the accepted zero-width outer yes arm remains explicit."
      ]
    },
    {
      "id": "named-conditional-group-exists-fully-empty-nested-module-fullmatch-absent-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_fully_empty_nested_module_absent_workflow",
      "helper": "fullmatch",
      "args": ["a(?P<word>b)?c(?(word)|(?(word)|))", "ac"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "fully-empty", "nested", "named-group", "fullmatch", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the named module-level nested fully-empty fullmatch path when the optional named capture is absent so the nested fully-empty site contributes no suffix and the `ac` acceptance stays explicit."
      ]
    },
    {
      "id": "named-conditional-group-exists-fully-empty-nested-pattern-fullmatch-extra-suffix-failure-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_fully_empty_nested_pattern_extra_suffix_failure_workflow",
      "pattern": "a(?P<word>b)?c(?(word)|(?(word)|))",
      "helper": "fullmatch",
      "args": ["ace"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "fully-empty", "nested", "named-group", "fullmatch", "pattern", "absent", "failure", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch named nested fully-empty failure path when the optional named capture is omitted so the scorecard keeps the rejected extra-suffix variant separate from nested empty-yes-arm behavior."
      ]
    }
  ]
}
