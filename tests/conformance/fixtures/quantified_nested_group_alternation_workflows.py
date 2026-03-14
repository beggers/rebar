MANIFEST = {
  "schema_version": 1,
  "manifest_id": "quantified-nested-group-alternation-workflows",
  "layer": "match_behavior",
  "suite_id": "match.quantified_nested_group_alternation",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "quantified-nested-group-alternation-numbered-compile-metadata-str",
      "operation": "compile",
      "family": "quantified_nested_group_alternation_numbered_compile_metadata",
      "pattern": "a((b|c)+)d",
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "bounded-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the numbered quantified nested-group alternation compile frontier with one outer capture containing one `+`-quantified inner literal alternation and no broader counted-repeat, replacement, backreference, or conditional follow-ons."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-numbered-module-search-lower-bound-b-str",
      "operation": "module_call",
      "family": "quantified_nested_group_alternation_numbered_module_search_lower_bound_b_workflow",
      "helper": "search",
      "args": ["a((b|c)+)d", "zzabdzz"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "bounded-repeat", "search", "module", "lower-bound", "b-branch", "str", "gap"],
      "notes": [
        "Documents the numbered module-level quantified nested-group alternation lower-bound success path on `abd`, so the scorecard records the one-branch outer capture and final inner branch without widening into broader grouped execution."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-numbered-pattern-fullmatch-repeated-mixed-str",
      "operation": "pattern_call",
      "family": "quantified_nested_group_alternation_numbered_pattern_fullmatch_repeated_mixed_workflow",
      "pattern": "a((b|c)+)d",
      "helper": "fullmatch",
      "args": ["acbbd"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "bounded-repeat", "fullmatch", "pattern", "repeated-branch", "mixed", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the numbered compiled-pattern repeated-branch success path on `acbbd`, so the quantified outer capture expands across repetition while the final inner branch remains observable at the public API."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-named-compile-metadata-str",
      "operation": "compile",
      "family": "quantified_nested_group_alternation_named_compile_metadata",
      "pattern": "a(?P<outer>(?P<inner>b|c)+)d",
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "bounded-repeat", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the named quantified nested-group alternation compile frontier for the same bounded `+`-quantified inner branch-selection site with visible `outer` and `inner` captures."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-named-module-search-lower-bound-c-str",
      "operation": "module_call",
      "family": "quantified_nested_group_alternation_named_module_search_lower_bound_c_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(?P<inner>b|c)+)d", "zzacdzz"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "bounded-repeat", "named-group", "search", "module", "lower-bound", "c-branch", "str", "gap"],
      "notes": [
        "Documents the named module-level quantified nested-group alternation lower-bound success path on `acd`, so the visible named captures stay explicit at the one-branch boundary."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-named-pattern-fullmatch-repeated-mixed-str",
      "operation": "pattern_call",
      "family": "quantified_nested_group_alternation_named_pattern_fullmatch_repeated_mixed_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c)+)d",
      "helper": "fullmatch",
      "args": ["abccd"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "bounded-repeat", "named-group", "fullmatch", "pattern", "repeated-branch", "mixed", "outer-capture", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the named compiled-pattern repeated-branch success path on `abccd`, so the published slice keeps the repeated `outer` capture plus final `inner` branch observable under repetition."
      ]
    }
  ]
}
