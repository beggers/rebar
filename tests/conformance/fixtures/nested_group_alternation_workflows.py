MANIFEST = {
  "schema_version": 1,
  "manifest_id": "nested-group-alternation-workflows",
  "layer": "match_behavior",
  "suite_id": "match.nested_group_alternation",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "nested-group-alternation-compile-metadata-str",
      "operation": "compile",
      "family": "nested_group_alternation_compile_metadata",
      "pattern": "a((b|c))d",
      "categories": ["grouped", "nested-group", "alternation", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the next bounded nested-group alternation compile frontier with one outer capture containing one inner literal alternation wrapped by literal prefix and suffix text."
      ]
    },
    {
      "id": "nested-group-alternation-module-search-str",
      "operation": "module_call",
      "family": "nested_group_alternation_module_workflow",
      "helper": "search",
      "args": ["a((b|c))d", "zzacdzz"],
      "categories": ["grouped", "nested-group", "alternation", "search", "module", "str", "gap"],
      "notes": [
        "Documents the module-level nested-group alternation search path for one nested capture site whose inner group contains a single literal alternation."
      ]
    },
    {
      "id": "nested-group-alternation-pattern-fullmatch-str",
      "operation": "pattern_call",
      "family": "nested_group_alternation_pattern_workflow",
      "pattern": "a((b|c))d",
      "helper": "fullmatch",
      "args": ["abd"],
      "categories": ["grouped", "nested-group", "alternation", "fullmatch", "pattern", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch path for the same nested-group alternation shape while leaving replacement, callable replacement, quantified branches, and branch-local references out of scope."
      ]
    },
    {
      "id": "named-nested-group-alternation-compile-metadata-str",
      "operation": "compile",
      "family": "named_nested_group_alternation_compile_metadata",
      "pattern": "a(?P<outer>(?P<inner>b|c))d",
      "categories": ["grouped", "nested-group", "alternation", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named nested-group alternation compile frontier for one named outer capture containing one named inner alternation site."
      ]
    },
    {
      "id": "named-nested-group-alternation-module-search-str",
      "operation": "module_call",
      "family": "named_nested_group_alternation_module_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(?P<inner>b|c))d", "zzabdzz"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "search", "module", "str", "gap"],
      "notes": [
        "Documents the module-level named nested-group alternation search path so the next combined nesting-and-branch-selection gap is explicit in the scorecard."
      ]
    },
    {
      "id": "named-nested-group-alternation-pattern-fullmatch-str",
      "operation": "pattern_call",
      "family": "named_nested_group_alternation_pattern_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c))d",
      "helper": "fullmatch",
      "args": ["acd"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "fullmatch", "pattern", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch path for the same named nested-group alternation shape without claiming support for replacement workflows, branch-local backreferences, or broader backtracking."
      ]
    }
  ]
}
