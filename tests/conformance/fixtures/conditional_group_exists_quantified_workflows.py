MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-quantified-workflows",
  "layer": "match_behavior",
  "suite_id": "match.conditional_group_exists_quantified",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "conditional-group-exists-quantified-compile-metadata-str",
      "operation": "compile",
      "family": "conditional_group_exists_quantified_compile_metadata",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "quantified", "exact-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes one bounded numbered quantified-conditional compile path whose two-arm group-exists site is repeated exactly twice with CPython-supported `{2}` syntax."
      ]
    },
    {
      "id": "conditional-group-exists-quantified-module-search-present-str",
      "operation": "module_call",
      "family": "conditional_group_exists_quantified_module_present_workflow",
      "helper": "search",
      "args": ["a(b)?c(?(1)d|e){2}", "zzabcddzz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "quantified", "exact-repeat", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the numbered module-level quantified conditional search path when the optional capture is present so the repeated yes arm requires `dd` rather than a single `d`."
      ]
    },
    {
      "id": "conditional-group-exists-quantified-module-fullmatch-absent-str",
      "operation": "module_call",
      "family": "conditional_group_exists_quantified_module_absent_workflow",
      "helper": "fullmatch",
      "args": ["a(b)?c(?(1)d|e){2}", "acee"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "quantified", "exact-repeat", "fullmatch", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the numbered module-level quantified conditional fullmatch path when the optional capture is absent so the repeated else arm requires `ee`."
      ]
    },
    {
      "id": "conditional-group-exists-quantified-pattern-fullmatch-missing-repeat-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_quantified_pattern_missing_repeat_workflow",
      "pattern": "a(b)?c(?(1)d|e){2}",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "quantified", "exact-repeat", "fullmatch", "pattern", "present", "failure", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch numbered quantified conditional failure path when the capture is present but only one repeated yes-arm `d` is supplied instead of the required `{2}` count."
      ]
    },
    {
      "id": "named-conditional-group-exists-quantified-compile-metadata-str",
      "operation": "compile",
      "family": "named_conditional_group_exists_quantified_compile_metadata",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "quantified", "exact-repeat", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named quantified-conditional compile frontier for the same bounded `{2}` repeated conditional shape."
      ]
    },
    {
      "id": "named-conditional-group-exists-quantified-module-search-present-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_quantified_module_present_workflow",
      "helper": "search",
      "args": ["a(?P<word>b)?c(?(word)d|e){2}", "zzabcddzz"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "quantified", "exact-repeat", "named-group", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the named module-level quantified conditional search path when the optional named capture is present so the repeated yes arm still requires the doubled `d` suffix."
      ]
    },
    {
      "id": "named-conditional-group-exists-quantified-module-fullmatch-absent-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_quantified_module_absent_workflow",
      "helper": "fullmatch",
      "args": ["a(?P<word>b)?c(?(word)d|e){2}", "acee"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "quantified", "exact-repeat", "named-group", "fullmatch", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the named module-level quantified conditional fullmatch path when the optional named capture is absent so the repeated else arm requires `ee`."
      ]
    },
    {
      "id": "named-conditional-group-exists-quantified-pattern-fullmatch-missing-repeat-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_quantified_pattern_missing_repeat_workflow",
      "pattern": "a(?P<word>b)?c(?(word)d|e){2}",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "optional-group", "conditional", "group-exists", "quantified", "exact-repeat", "named-group", "fullmatch", "pattern", "present", "failure", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch named quantified conditional failure path when the optional named capture is present but the repeated yes arm is only supplied once."
      ]
    }
  ]
}
