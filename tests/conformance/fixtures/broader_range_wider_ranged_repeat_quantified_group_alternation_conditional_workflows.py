MANIFEST = {
  "schema_version": 1,
  "manifest_id": "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows",
  "layer": "match_behavior",
  "suite_id": "match.broader_range_wider_ranged_repeat_quantified_group_alternation_conditional",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-compile-metadata-str",
      "operation": "compile",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_numbered_compile_metadata",
      "pattern": "a((bc|de){1,4})?(?(1)d|e)",
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the numbered compile frontier for one optional grouped `{1,4}` alternation followed by one later group-exists conditional without widening into open-ended repeats, replacements, nested grouped conditionals, branch-local backreferences, or broader grouped backtracking."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-absent-workflow-str",
      "operation": "module_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_numbered_module_absent_workflow",
      "helper": "search",
      "args": ["a((bc|de){1,4})?(?(1)d|e)", "zzaezz"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "search", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the numbered absent-group success path on `ae` so the scorecard records that the conditional else arm still accepts when the optional grouped alternation is skipped entirely."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-str",
      "operation": "module_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_numbered_module_lower_bound_bc_workflow",
      "helper": "search",
      "args": ["a((bc|de){1,4})?(?(1)d|e)", "zzabcdzz"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "search", "module", "present", "lower-bound", "bc-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound present success path on `abcd` so the broadened frontier shows that one `bc` repetition is enough to force the later yes arm to consume `d`."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-lower-bound-de-workflow-str",
      "operation": "module_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_numbered_module_lower_bound_de_workflow",
      "helper": "search",
      "args": ["a((bc|de){1,4})?(?(1)d|e)", "zzadedzz"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "search", "module", "present", "lower-bound", "de-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound present success path on `aded` so the same broader counted-repeat slice stays explicit for the single `de` branch variant."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",
      "operation": "pattern_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_numbered_pattern_third_repetition_mixed_workflow",
      "pattern": "a((bc|de){1,4})?(?(1)d|e)",
      "helper": "fullmatch",
      "args": ["abcbcded"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "fullmatch", "pattern", "present", "third-repetition", "mixed-branches", "str", "gap"],
      "notes": [
        "Documents the numbered mixed-branch success path on `abcbcded` so the publication captures one present-group workflow where the grouped alternation spans `bc`, `bc`, then `de` before the conditional yes arm matches."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-missing-trailing-d-workflow-str",
      "operation": "pattern_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_numbered_pattern_no_match_missing_trailing_d_workflow",
      "pattern": "a((bc|de){1,4})?(?(1)d|e)",
      "helper": "fullmatch",
      "args": ["abcdede"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "fullmatch", "pattern", "present", "no-match", "missing-trailing-d", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abcdede` so the scorecard stays explicit that the conditional yes arm still rejects a present-group branch when the required trailing `d` is missing after the grouped repetitions already fit inside the broader `{1,4}` envelope."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-short-workflow-str",
      "operation": "pattern_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_numbered_pattern_no_match_short_workflow",
      "pattern": "a((bc|de){1,4})?(?(1)d|e)",
      "helper": "fullmatch",
      "args": ["ad"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "fullmatch", "pattern", "no-match", "below-repeat-count", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `ad` so the scorecard stays explicit that the broadened grouped alternation still needs at least one repetition before the yes arm can apply."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-compile-metadata-str",
      "operation": "compile",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_named_compile_metadata",
      "pattern": "a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the named compile frontier for the same optional grouped `{1,4}` alternation with one later named group-exists conditional."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-absent-workflow-str",
      "operation": "module_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_named_module_absent_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(bc|de){1,4})?(?(outer)d|e)", "zzaezz"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "named-group", "search", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the named absent-group success path on `ae` so the published frontier records the else-arm acceptance when the optional named outer capture is skipped."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-lower-bound-de-workflow-str",
      "operation": "module_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_named_module_lower_bound_de_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(bc|de){1,4})?(?(outer)d|e)", "zzadedzz"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "named-group", "search", "module", "present", "lower-bound", "de-branch", "str", "gap"],
      "notes": [
        "Documents the named lower-bound present success path on `aded` so the scorecard records the visible `outer` capture on the single `de` branch variant too."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-upper-bound-mixed-workflow-str",
      "operation": "module_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_named_module_upper_bound_mixed_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(bc|de){1,4})?(?(outer)d|e)", "zzabcdedededzz"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "named-group", "search", "module", "present", "upper-bound", "mixed-branches", "str", "gap"],
      "notes": [
        "Documents the named upper-bound success path on `abcdededed` so the scorecard includes one four-repetition grouped alternation at the top of the broader `{1,4}` envelope before the conditional yes arm consumes the final `d`."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",
      "operation": "pattern_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_named_pattern_third_repetition_mixed_workflow",
      "pattern": "a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
      "helper": "fullmatch",
      "args": ["abcbcded"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "named-group", "fullmatch", "pattern", "present", "third-repetition", "mixed-branches", "str", "gap"],
      "notes": [
        "Documents the named mixed-branch success path on `abcbcded` so the visible `outer` capture remains explicit when the broadened grouped alternation spans three repetitions before the yes arm matches."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-short-workflow-str",
      "operation": "pattern_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_named_pattern_no_match_short_workflow",
      "pattern": "a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
      "helper": "fullmatch",
      "args": ["ad"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "named-group", "fullmatch", "pattern", "no-match", "below-repeat-count", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `ad` so the scorecard stays explicit that the broadened grouped alternation still needs at least one repetition before the yes arm can apply."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-overflow-workflow-str",
      "operation": "pattern_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_named_pattern_no_match_overflow_workflow",
      "pattern": "a(?P<outer>(bc|de){1,4})?(?(outer)d|e)",
      "helper": "fullmatch",
      "args": ["abcbcbcbcbcd"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "broader-range", "counted-repeat", "conditional", "group-exists", "optional-group", "named-group", "fullmatch", "pattern", "no-match", "overflow", "str", "gap"],
      "notes": [
        "Documents the named no-match overflow path on `abcbcbcbcbcd` so the scorecard records that a fifth grouped repetition still exceeds the bounded `{1,4}` envelope even when the trailing conditional yes arm would otherwise be satisfiable."
      ]
    }
  ]
}
