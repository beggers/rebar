MANIFEST = {
  "schema_version": 1,
  "manifest_id": "optional-group-alternation-workflows",
  "layer": "match_behavior",
  "suite_id": "match.optional_group_alternation",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "optional-group-alternation-compile-metadata-str",
      "operation": "compile",
      "family": "optional_group_alternation_compile_metadata",
      "pattern": "a(b|c)?d",
      "categories": ["grouped", "optional-group", "alternation", "quantifier", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the bounded compile frontier for one optional numbered capture whose body contains exactly one literal alternation site between literal prefix and suffix text."
      ]
    },
    {
      "id": "optional-group-alternation-module-search-present-str",
      "operation": "module_call",
      "family": "optional_group_alternation_module_present_workflow",
      "helper": "search",
      "args": ["a(b|c)?d", "zzacdzz"],
      "categories": ["grouped", "optional-group", "alternation", "quantifier", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the module-level numbered optional-group alternation search path when the optional capture is present and the alternation selects the c branch."
      ]
    },
    {
      "id": "optional-group-alternation-pattern-fullmatch-absent-str",
      "operation": "pattern_call",
      "family": "optional_group_alternation_pattern_absent_workflow",
      "pattern": "a(b|c)?d",
      "helper": "fullmatch",
      "args": ["ad"],
      "categories": ["grouped", "optional-group", "alternation", "quantifier", "fullmatch", "pattern", "absent", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch numbered optional-group alternation path when the capture is omitted so the published scorecard records the observable None-valued group outcome."
      ]
    },
    {
      "id": "named-optional-group-alternation-compile-metadata-str",
      "operation": "compile",
      "family": "named_optional_group_alternation_compile_metadata",
      "pattern": "a(?P<word>b|c)?d",
      "categories": ["grouped", "optional-group", "alternation", "quantifier", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named optional-group alternation compile frontier for the same bounded quantified-branch shape."
      ]
    },
    {
      "id": "named-optional-group-alternation-module-search-present-str",
      "operation": "module_call",
      "family": "named_optional_group_alternation_module_present_workflow",
      "helper": "search",
      "args": ["a(?P<word>b|c)?d", "zzabdzz"],
      "categories": ["grouped", "optional-group", "alternation", "quantifier", "named-group", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the module-level named optional-group alternation search path when the optional capture is present and the alternation selects the b branch."
      ]
    },
    {
      "id": "named-optional-group-alternation-pattern-fullmatch-absent-str",
      "operation": "pattern_call",
      "family": "named_optional_group_alternation_pattern_absent_workflow",
      "pattern": "a(?P<word>b|c)?d",
      "helper": "fullmatch",
      "args": ["ad"],
      "categories": ["grouped", "optional-group", "alternation", "quantifier", "named-group", "fullmatch", "pattern", "absent", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch named optional-group alternation path when the capture is omitted so the named-group None payload stays explicit in the published gap."
      ]
    }
  ]
}
