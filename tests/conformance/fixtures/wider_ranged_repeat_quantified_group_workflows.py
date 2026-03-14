MANIFEST = {
  "schema_version": 1,
  "manifest_id": "wider-ranged-repeat-quantified-group-workflows",
  "layer": "match_behavior",
  "suite_id": "match.wider_ranged_repeat_quantified_group",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "wider-ranged-repeat-numbered-group-compile-metadata-str",
      "operation": "compile",
      "family": "wider_ranged_repeat_numbered_group_compile_metadata",
      "pattern": "a(bc){1,3}d",
      "categories": ["grouped", "quantifier", "ranged-repeat", "wider-range", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes one slightly wider numbered ranged-repeat compile slice so the correctness scorecard records the exact {1,3} frontier without broadening into open-ended or alternation-heavy repetition."
      ]
    },
    {
      "id": "wider-ranged-repeat-numbered-group-module-search-lower-bound-str",
      "operation": "module_call",
      "family": "wider_ranged_repeat_numbered_group_module_search_lower_bound_workflow",
      "helper": "search",
      "args": ["a(bc){1,3}d", "zzabcdzz"],
      "categories": ["grouped", "quantifier", "ranged-repeat", "wider-range", "search", "module", "lower-bound", "str", "gap"],
      "notes": [
        "Documents the module-level numbered {1,3} search path at the lower bound so the published scorecard still records the visible final capture value after one repetition completes."
      ]
    },
    {
      "id": "wider-ranged-repeat-numbered-group-pattern-fullmatch-upper-bound-str",
      "operation": "pattern_call",
      "family": "wider_ranged_repeat_numbered_group_pattern_fullmatch_upper_bound_workflow",
      "pattern": "a(bc){1,3}d",
      "helper": "fullmatch",
      "args": ["abcbcbcd"],
      "categories": ["grouped", "quantifier", "ranged-repeat", "wider-range", "fullmatch", "pattern", "upper-bound", "str", "gap"],
      "notes": [
        "Documents the bounded Pattern.fullmatch numbered {1,3} path at the new third-repetition upper bound so the scorecard exposes the final capture value and span after the quantified group completes."
      ]
    },
    {
      "id": "wider-ranged-repeat-named-group-compile-metadata-str",
      "operation": "compile",
      "family": "wider_ranged_repeat_named_group_compile_metadata",
      "pattern": "a(?P<word>bc){1,3}d",
      "categories": ["grouped", "quantifier", "ranged-repeat", "wider-range", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named-group compile frontier for the same bounded {1,3} slice so the manifest stays explicit about both numbered and named capture metadata."
      ]
    },
    {
      "id": "wider-ranged-repeat-named-group-module-search-upper-bound-str",
      "operation": "module_call",
      "family": "wider_ranged_repeat_named_group_module_search_upper_bound_workflow",
      "helper": "search",
      "args": ["a(?P<word>bc){1,3}d", "zzabcbcbcdzz"],
      "categories": ["grouped", "quantifier", "ranged-repeat", "wider-range", "named-group", "search", "module", "upper-bound", "str", "gap"],
      "notes": [
        "Documents the module-level named {1,3} search path at the new upper bound so the published gap records the final named-group payload after the third repetition completes."
      ]
    },
    {
      "id": "wider-ranged-repeat-named-group-pattern-fullmatch-lower-bound-str",
      "operation": "pattern_call",
      "family": "wider_ranged_repeat_named_group_pattern_fullmatch_lower_bound_workflow",
      "pattern": "a(?P<word>bc){1,3}d",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "quantifier", "ranged-repeat", "wider-range", "named-group", "fullmatch", "pattern", "lower-bound", "str", "gap"],
      "notes": [
        "Documents the bounded Pattern.fullmatch named {1,3} path at the lower bound without broadening into wider envelopes, quantified alternation, replacements, or other backtracking-heavy composition."
      ]
    }
  ]
}
