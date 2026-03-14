MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-alternation-workflows",
  "layer": "match_behavior",
  "suite_id": "match.conditional_group_exists_alternation",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "conditional-group-exists-alternation-compile-metadata-str",
      "operation": "compile",
      "family": "conditional_group_exists_alternation_compile_metadata",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes one bounded numbered two-arm conditional compile path whose yes and else arms each contain one literal alternation site so the first alternation-heavy two-arm spelling becomes explicit in the scorecard."
      ]
    },
    {
      "id": "conditional-group-exists-alternation-module-search-present-first-arm-str",
      "operation": "module_call",
      "family": "conditional_group_exists_alternation_module_present_first_arm_workflow",
      "helper": "search",
      "args": ["a(b)?c(?(1)(de|df)|(eg|eh))", "zzabcdezz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "search", "module", "present", "first-arm", "str", "gap"],
      "notes": [
        "Documents the numbered module-level two-arm conditional search path when the optional capture is present and the yes-arm alternation selects its first literal branch."
      ]
    },
    {
      "id": "conditional-group-exists-alternation-pattern-fullmatch-present-second-arm-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_alternation_pattern_present_second_arm_workflow",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "helper": "fullmatch",
      "args": ["abcdf"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "fullmatch", "pattern", "present", "second-arm", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch numbered conditional path when the optional capture is present and the yes-arm alternation backtracks to its second literal branch."
      ]
    },
    {
      "id": "conditional-group-exists-alternation-module-search-absent-first-arm-str",
      "operation": "module_call",
      "family": "conditional_group_exists_alternation_module_absent_first_arm_workflow",
      "helper": "search",
      "args": ["a(b)?c(?(1)(de|df)|(eg|eh))", "zzacegzz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "search", "module", "absent", "first-arm", "str", "gap"],
      "notes": [
        "Documents the numbered module-level two-arm conditional search path when the optional capture is absent and the else-arm alternation selects its first literal branch."
      ]
    },
    {
      "id": "conditional-group-exists-alternation-pattern-fullmatch-absent-second-arm-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_alternation_pattern_absent_second_arm_workflow",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh))",
      "helper": "fullmatch",
      "args": ["aceh"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "fullmatch", "pattern", "absent", "second-arm", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch numbered conditional path when the optional capture is absent and the else-arm alternation takes its second literal branch."
      ]
    },
    {
      "id": "named-conditional-group-exists-alternation-compile-metadata-str",
      "operation": "compile",
      "family": "named_conditional_group_exists_alternation_compile_metadata",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named two-arm conditional compile frontier for the same single-site per-arm alternation shape."
      ]
    },
    {
      "id": "named-conditional-group-exists-alternation-module-search-present-first-arm-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_alternation_module_present_first_arm_workflow",
      "helper": "search",
      "args": ["a(?P<word>b)?c(?(word)(de|df)|(eg|eh))", "zzabcdezz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "named-group", "search", "module", "present", "first-arm", "str", "gap"],
      "notes": [
        "Documents the named module-level two-arm conditional search path when the optional named capture is present and the yes-arm alternation selects its first literal branch."
      ]
    },
    {
      "id": "named-conditional-group-exists-alternation-pattern-fullmatch-present-second-arm-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_alternation_pattern_present_second_arm_workflow",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "helper": "fullmatch",
      "args": ["abcdf"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "named-group", "fullmatch", "pattern", "present", "second-arm", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch named conditional path when the optional named capture is present and the yes-arm alternation takes its second literal branch."
      ]
    },
    {
      "id": "named-conditional-group-exists-alternation-module-search-absent-first-arm-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_alternation_module_absent_first_arm_workflow",
      "helper": "search",
      "args": ["a(?P<word>b)?c(?(word)(de|df)|(eg|eh))", "zzacegzz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "named-group", "search", "module", "absent", "first-arm", "str", "gap"],
      "notes": [
        "Documents the named module-level two-arm conditional search path when the optional named capture is absent and the else-arm alternation selects its first literal branch."
      ]
    },
    {
      "id": "named-conditional-group-exists-alternation-pattern-fullmatch-absent-second-arm-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_alternation_pattern_absent_second_arm_workflow",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
      "helper": "fullmatch",
      "args": ["aceh"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "named-group", "fullmatch", "pattern", "absent", "second-arm", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch named conditional path when the optional named capture is absent and the else-arm alternation takes its second literal branch."
      ]
    }
  ]
}
