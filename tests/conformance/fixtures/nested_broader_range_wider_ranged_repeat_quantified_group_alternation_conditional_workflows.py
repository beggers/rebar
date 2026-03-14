MANIFEST = {
  "schema_version": 1,
  "manifest_id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows",
  "layer": "match_behavior",
  "suite_id": "match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-compile-metadata-str",
      "operation": "compile",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_numbered_compile_metadata",
      "pattern": "a(((bc|de){1,4})d)?(?(1)e|f)",
      "categories": ["grouped", "nested-group", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the numbered nested broader `{1,4}` grouped-alternation-plus-conditional compile frontier with one optional outer capture around the already-landed nested grouped body and one later group-exists branch."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-absent-workflow-str",
      "operation": "module_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_numbered_module_absent_workflow",
      "helper": "search",
      "args": ["a(((bc|de){1,4})d)?(?(1)e|f)", "zzafzz"],
      "categories": ["grouped", "nested-group", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "search", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the numbered absent-group success path on `af` so the scorecard records that the conditional else arm still accepts when the optional nested grouped body is skipped entirely."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-str",
      "operation": "module_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_numbered_module_lower_bound_bc_workflow",
      "helper": "search",
      "args": ["a(((bc|de){1,4})d)?(?(1)e|f)", "zzabcdezz"],
      "categories": ["grouped", "nested-group", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "search", "module", "present", "lower-bound", "bc-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound present success path on `abcde` so one `bc` repetition inside the nested grouped body stays explicit before the surrounding `d` and later conditional `e` both match."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-lower-bound-de-workflow-str",
      "operation": "module_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_numbered_module_lower_bound_de_workflow",
      "helper": "search",
      "args": ["a(((bc|de){1,4})d)?(?(1)e|f)", "zzadedezz"],
      "categories": ["grouped", "nested-group", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "search", "module", "present", "lower-bound", "de-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound present success path on `adede` so the single `de` branch variant is published for the same nested grouped-conditional shape."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-mixed-workflow-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_numbered_pattern_mixed_workflow",
      "pattern": "a(((bc|de){1,4})d)?(?(1)e|f)",
      "helper": "fullmatch",
      "args": ["abcbcdede"],
      "categories": ["grouped", "nested-group", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "fullmatch", "pattern", "present", "mixed-branches", "str", "gap"],
      "notes": [
        "Documents the numbered mixed-branch success path on `abcbcdede` so the publication includes one present-group workflow where the nested grouped alternation spans `bc`, `bc`, then `de` before the later conditional yes arm matches `e`."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-missing-conditional-e-workflow-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_numbered_pattern_no_match_missing_conditional_e_workflow",
      "pattern": "a(((bc|de){1,4})d)?(?(1)e|f)",
      "helper": "fullmatch",
      "args": ["abcbcded"],
      "categories": ["grouped", "nested-group", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "fullmatch", "pattern", "present", "no-match", "missing-conditional-e", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abcbcded` so the scorecard stays explicit that a present outer group still requires the later conditional yes arm to consume the final `e`."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-short-workflow-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_numbered_pattern_no_match_short_workflow",
      "pattern": "a(((bc|de){1,4})d)?(?(1)e|f)",
      "helper": "fullmatch",
      "args": ["ae"],
      "categories": ["grouped", "nested-group", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "fullmatch", "pattern", "no-match", "short", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `ae` so the publication records that the absent-group branch requires `f`, not `e`, when the optional nested grouped body is skipped."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-compile-metadata-str",
      "operation": "compile",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_named_compile_metadata",
      "pattern": "a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)",
      "categories": ["grouped", "nested-group", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the named compile frontier for the same nested broader `{1,4}` grouped-alternation-plus-conditional slice under one visible `outer` capture."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-absent-workflow-str",
      "operation": "module_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_named_module_absent_workflow",
      "helper": "search",
      "args": ["a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)", "zzafzz"],
      "categories": ["grouped", "nested-group", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "named-group", "search", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the named absent-group success path on `af` so the else-arm acceptance stays explicit when the optional named outer capture is skipped."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-lower-bound-de-workflow-str",
      "operation": "module_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_named_module_lower_bound_de_workflow",
      "helper": "search",
      "args": ["a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)", "zzadedezz"],
      "categories": ["grouped", "nested-group", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "named-group", "search", "module", "present", "lower-bound", "de-branch", "str", "gap"],
      "notes": [
        "Documents the named lower-bound present success path on `adede` so the visible `outer` capture remains explicit for the single `de` branch variant."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-upper-bound-all-de-workflow-str",
      "operation": "module_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_named_module_upper_bound_all_de_workflow",
      "helper": "search",
      "args": ["a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)", "zzadededededezz"],
      "categories": ["grouped", "nested-group", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "named-group", "search", "module", "present", "upper-bound", "all-de", "str", "gap"],
      "notes": [
        "Documents the named upper-bound success path on `adedededede` so the scorecard includes the four-repetition all-`de` nested grouped body before the later conditional yes arm matches."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-mixed-workflow-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_named_pattern_mixed_workflow",
      "pattern": "a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)",
      "helper": "fullmatch",
      "args": ["abcbcdede"],
      "categories": ["grouped", "nested-group", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "named-group", "fullmatch", "pattern", "present", "mixed-branches", "str", "gap"],
      "notes": [
        "Documents the named mixed-branch success path on `abcbcdede` so the visible `outer` capture stays explicit when the nested grouped alternation spans three repetitions before the conditional yes arm consumes `e`."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-short-workflow-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_named_pattern_no_match_short_workflow",
      "pattern": "a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)",
      "helper": "fullmatch",
      "args": ["ae"],
      "categories": ["grouped", "nested-group", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "named-group", "fullmatch", "pattern", "no-match", "short", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `ae` so the same absent-group `f` requirement stays explicit under the visible outer capture."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-overflow-workflow-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_named_pattern_no_match_overflow_workflow",
      "pattern": "a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)",
      "helper": "fullmatch",
      "args": ["abcbcbcbcbcde"],
      "categories": ["grouped", "nested-group", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "named-group", "fullmatch", "pattern", "no-match", "overflow", "str", "gap"],
      "notes": [
        "Documents the named no-match overflow path on `abcbcbcbcbcde` so the publication records that a fifth grouped repetition still exceeds the bounded `{1,4}` envelope before the later conditional can match `e`."
      ]
    }
  ]
}
