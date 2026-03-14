MANIFEST = {
  "schema_version": 1,
  "manifest_id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-workflows",
  "layer": "match_behavior",
  "suite_id": "match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-compile-metadata-str",
      "operation": "compile",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_numbered_compile_metadata",
      "pattern": "a((bc|de){1,4})d",
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the numbered nested broader `{1,4}` grouped-alternation compile frontier with one outer capture around one `(bc|de){1,4}` site and no grouped conditional, replacement, open-ended, or backtracking-heavy follow-ons."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
      "operation": "module_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_numbered_module_lower_bound_bc_workflow",
      "helper": "search",
      "args": ["a((bc|de){1,4})d", "zzabcdzz"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "search", "module", "lower-bound", "bc", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound nested grouped success path on `abcd` so the scorecard records one `bc` repetition captured through the outer group."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-module-search-lower-bound-de-str",
      "operation": "module_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_numbered_module_lower_bound_de_workflow",
      "helper": "search",
      "args": ["a((bc|de){1,4})d", "zzadedzz"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "search", "module", "lower-bound", "de", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound nested grouped success path on `aded` so the alternate single `de` branch stays explicit in the published pack."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_numbered_pattern_third_repetition_mixed_workflow",
      "pattern": "a((bc|de){1,4})d",
      "helper": "fullmatch",
      "args": ["abcbcded"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "third-repetition", "mixed", "str", "gap"],
      "notes": [
        "Documents the numbered compiled-pattern mixed-branch success path on `abcbcded` so the publication includes one three-repetition observation under the outer capture."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-pattern-fullmatch-upper-bound-all-de-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_numbered_pattern_upper_bound_all_de_workflow",
      "pattern": "a((bc|de){1,4})d",
      "helper": "fullmatch",
      "args": ["adedededed"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "upper-bound", "de", "str", "gap"],
      "notes": [
        "Documents the numbered compiled-pattern upper-bound success path on `adedededed` so the scorecard records one four-repetition all-`de` observation within the broader `{1,4}` envelope."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-pattern-fullmatch-no-match-short-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_numbered_pattern_no_match_short_workflow",
      "pattern": "a((bc|de){1,4})d",
      "helper": "fullmatch",
      "args": ["ae"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "no-match", "short", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `ae` so the nested broader counted repeat stays explicit about rejecting texts that never satisfy the inner grouped alternation."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-numbered-pattern-fullmatch-no-match-missing-trailing-d-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_numbered_pattern_no_match_missing_trailing_d_workflow",
      "pattern": "a((bc|de){1,4})d",
      "helper": "fullmatch",
      "args": ["abcbcdede"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "no-match", "missing-trailing-d", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path when the grouped body is present but the surrounding literal suffix never closes with the required trailing `d`."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-compile-metadata-str",
      "operation": "compile",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_named_compile_metadata",
      "pattern": "a(?P<outer>(bc|de){1,4})d",
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the named nested broader `{1,4}` grouped-alternation compile frontier with one visible outer capture around the repeated inner alternation."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-module-search-lower-bound-bc-str",
      "operation": "module_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_named_module_lower_bound_bc_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(bc|de){1,4})d", "zzabcdzz"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "search", "module", "lower-bound", "bc", "str", "gap"],
      "notes": [
        "Documents the named lower-bound nested grouped success path on `abcd` so the visible `outer` capture is explicit at the broadened counted-repeat frontier."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-module-search-lower-bound-de-str",
      "operation": "module_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_named_module_lower_bound_de_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(bc|de){1,4})d", "zzadedzz"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "search", "module", "lower-bound", "de", "str", "gap"],
      "notes": [
        "Documents the named lower-bound nested grouped success path on `aded` so the single `de` branch remains explicit under the outer named capture."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-pattern-fullmatch-third-repetition-mixed-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_named_pattern_third_repetition_mixed_workflow",
      "pattern": "a(?P<outer>(bc|de){1,4})d",
      "helper": "fullmatch",
      "args": ["abcbcded"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "fullmatch", "pattern", "third-repetition", "mixed", "str", "gap"],
      "notes": [
        "Documents the named compiled-pattern mixed-branch success path on `abcbcded` so one three-repetition nested grouped observation stays explicit under the visible outer capture."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-pattern-fullmatch-upper-bound-all-de-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_named_pattern_upper_bound_all_de_workflow",
      "pattern": "a(?P<outer>(bc|de){1,4})d",
      "helper": "fullmatch",
      "args": ["adedededed"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "fullmatch", "pattern", "upper-bound", "de", "str", "gap"],
      "notes": [
        "Documents the named compiled-pattern upper-bound success path on `adedededed` so the pack records the four-repetition all-`de` boundary with a visible outer capture."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-pattern-fullmatch-no-match-short-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_named_pattern_no_match_short_workflow",
      "pattern": "a(?P<outer>(bc|de){1,4})d",
      "helper": "fullmatch",
      "args": ["ae"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "fullmatch", "pattern", "no-match", "short", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `ae` so the same missing-repetition failure mode stays explicit under the visible outer capture."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-named-pattern-fullmatch-no-match-overflow-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_named_pattern_no_match_overflow_workflow",
      "pattern": "a(?P<outer>(bc|de){1,4})d",
      "helper": "fullmatch",
      "args": ["abcbcbcbcbcd"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "fullmatch", "pattern", "no-match", "overflow", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `abcbcbcbcbcd` so the published pack records that the broader `{1,4}` envelope still rejects a fifth inner grouped repetition."
      ]
    }
  ]
}
