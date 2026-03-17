MANIFEST = {
  "schema_version": 1,
  "manifest_id": "broader-range-wider-ranged-repeat-quantified-group-workflows",
  "layer": "match_behavior",
  "suite_id": "match.broader_range_wider_ranged_repeat_quantified_group",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "broader-range-wider-ranged-repeat-numbered-group-compile-metadata-str",
      "operation": "compile",
      "family": "broader_range_wider_ranged_repeat_numbered_group_compile_metadata",
      "pattern": "a(bc){1,4}d",
      "categories": ["grouped", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the numbered compile frontier for one broader `{1,4}` counted-repeat grouped slice without widening into grouped alternation, grouped conditionals, open-ended repeats, replacement workflows, or other broader execution shapes."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
      "operation": "module_call",
      "family": "broader_range_wider_ranged_repeat_numbered_group_module_search_upper_bound_workflow",
      "helper": "search",
      "args": ["a(bc){1,4}d", "zzabcbcbcbcdzz"],
      "categories": ["grouped", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "search", "module", "upper-bound", "str", "gap"],
      "notes": [
        "Documents the numbered module-level upper-bound success path on `abcbcbcbcd` so the published scorecard records the exact four-repetition frontier already anchored by the adjacent benchmark gap ids."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-numbered-group-pattern-fullmatch-lower-bound-str",
      "operation": "pattern_call",
      "family": "broader_range_wider_ranged_repeat_numbered_group_pattern_fullmatch_lower_bound_workflow",
      "pattern": "a(bc){1,4}d",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "lower-bound", "str", "gap"],
      "notes": [
        "Documents the numbered compiled-pattern lower-bound success path on `abcd` so the broader `{1,4}` slice stays explicit at the single-repetition minimum too."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-named-group-compile-metadata-str",
      "operation": "compile",
      "family": "broader_range_wider_ranged_repeat_named_group_compile_metadata",
      "pattern": "a(?P<word>bc){1,4}d",
      "categories": ["grouped", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named-group compile frontier for the same broader `{1,4}` counted-repeat grouped slice under one visible `word` capture."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-named-group-module-search-upper-bound-str",
      "operation": "module_call",
      "family": "broader_range_wider_ranged_repeat_named_group_module_search_upper_bound_workflow",
      "helper": "search",
      "args": ["a(?P<word>bc){1,4}d", "zzabcbcbcbcdzz"],
      "categories": ["grouped", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "search", "module", "upper-bound", "str", "gap"],
      "notes": [
        "Documents the named module-level upper-bound success path on `abcbcbcbcd` so the visible `word` capture stays explicit across the full four-repetition envelope."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-named-group-pattern-fullmatch-lower-bound-str",
      "operation": "pattern_call",
      "family": "broader_range_wider_ranged_repeat_named_group_pattern_fullmatch_lower_bound_workflow",
      "pattern": "a(?P<word>bc){1,4}d",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "fullmatch", "pattern", "lower-bound", "str", "gap"],
      "notes": [
        "Documents the named compiled-pattern lower-bound success path on `abcd` without broadening into grouped alternation, grouped conditionals, open-ended repeats, or unrelated harness cleanup."
      ]
    }
  ]
}
