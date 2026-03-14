MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-empty-yes-else-quantified-workflows",
  "layer": "match_behavior",
  "suite_id": "match.conditional_group_exists_empty_yes_else_quantified",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "conditional-group-exists-empty-yes-else-quantified-compile-metadata-str",
      "operation": "compile",
      "family": "conditional_group_exists_empty_yes_else_quantified_compile_metadata",
      "pattern": "(?:a(b)?c(?(1)|e)){2}",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-yes", "else", "quantified", "exact-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes one bounded numbered quantified empty-yes-arm conditional compile path where a non-capturing repeated wrapper keeps the optional capture at group 1 while the accepted empty-yes-arm site is repeated exactly twice."
      ]
    },
    {
      "id": "conditional-group-exists-empty-yes-else-quantified-module-fullmatch-present-str",
      "operation": "module_call",
      "family": "conditional_group_exists_empty_yes_else_quantified_module_present_workflow",
      "helper": "fullmatch",
      "args": ["(?:a(b)?c(?(1)|e)){2}", "abcabc"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-yes", "else", "quantified", "exact-repeat", "fullmatch", "module", "present", "str", "gap"],
      "notes": [
        "Documents the numbered module-level quantified empty-yes-arm fullmatch path when both repetitions populate the optional capture, so the repeated conditional contributes no `e` suffix in either iteration."
      ]
    },
    {
      "id": "conditional-group-exists-empty-yes-else-quantified-module-fullmatch-absent-str",
      "operation": "module_call",
      "family": "conditional_group_exists_empty_yes_else_quantified_module_absent_workflow",
      "helper": "fullmatch",
      "args": ["(?:a(b)?c(?(1)|e)){2}", "aceace"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-yes", "else", "quantified", "exact-repeat", "fullmatch", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the numbered module-level quantified empty-yes-arm fullmatch path when both repetitions omit the optional capture, so the repeated else arm contributes `e` in both positions."
      ]
    },
    {
      "id": "conditional-group-exists-empty-yes-else-quantified-pattern-fullmatch-mixed-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_empty_yes_else_quantified_pattern_mixed_workflow",
      "pattern": "(?:a(b)?c(?(1)|e)){2}",
      "helper": "fullmatch",
      "args": ["aceabc"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-yes", "else", "quantified", "exact-repeat", "fullmatch", "pattern", "mixed", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch numbered mixed absent-then-present quantified path so the scorecard proves the repeated conditional is evaluated at each repetition instead of freezing to the first iteration's absent state."
      ]
    },
    {
      "id": "named-conditional-group-exists-empty-yes-else-quantified-compile-metadata-str",
      "operation": "compile",
      "family": "named_conditional_group_exists_empty_yes_else_quantified_compile_metadata",
      "pattern": "(?:a(?P<word>b)?c(?(word)|e)){2}",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-yes", "else", "quantified", "exact-repeat", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named quantified empty-yes-arm conditional compile frontier for the same exact `{2}` repeated site."
      ]
    },
    {
      "id": "named-conditional-group-exists-empty-yes-else-quantified-module-fullmatch-present-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_empty_yes_else_quantified_module_present_workflow",
      "helper": "fullmatch",
      "args": ["(?:a(?P<word>b)?c(?(word)|e)){2}", "abcabc"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-yes", "else", "quantified", "exact-repeat", "named-group", "fullmatch", "module", "present", "str", "gap"],
      "notes": [
        "Documents the named module-level quantified empty-yes-arm fullmatch path when both repetitions populate the named optional capture and both conditional sites therefore take the explicit empty yes arm."
      ]
    },
    {
      "id": "named-conditional-group-exists-empty-yes-else-quantified-module-fullmatch-absent-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_empty_yes_else_quantified_module_absent_workflow",
      "helper": "fullmatch",
      "args": ["(?:a(?P<word>b)?c(?(word)|e)){2}", "aceace"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-yes", "else", "quantified", "exact-repeat", "named-group", "fullmatch", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the named module-level quantified empty-yes-arm fullmatch path when both repetitions omit the named capture, keeping the doubled else-arm `e` contribution explicit in the published slice."
      ]
    },
    {
      "id": "named-conditional-group-exists-empty-yes-else-quantified-pattern-fullmatch-mixed-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_empty_yes_else_quantified_pattern_mixed_workflow",
      "pattern": "(?:a(?P<word>b)?c(?(word)|e)){2}",
      "helper": "fullmatch",
      "args": ["aceabc"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "empty-yes", "else", "quantified", "exact-repeat", "named-group", "fullmatch", "pattern", "mixed", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch named mixed absent-then-present quantified path so the repeated empty-yes-arm site is recorded as a per-repetition decision for the named capture too."
      ]
    }
  ]
}
