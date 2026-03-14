MANIFEST = {
  "schema_version": 1,
  "manifest_id": "wider-ranged-repeat-quantified-group-alternation-conditional-workflows",
  "layer": "match_behavior",
  "suite_id": "match.wider_ranged_repeat_quantified_group_alternation_conditional",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-conditional-numbered-compile-metadata-str",
      "operation": "compile",
      "family": "wider_ranged_repeat_quantified_group_alternation_conditional_numbered_compile_metadata",
      "pattern": "a((bc|de){1,3})?(?(1)d|e)",
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "conditional", "group-exists", "optional-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the numbered compile frontier for one optional grouped `{1,3}` alternation followed by one later group-exists conditional without widening into open-ended repeats, replacements, nested grouped conditionals, or branch-local backreferences."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-absent-workflow-str",
      "operation": "module_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_conditional_numbered_module_absent_workflow",
      "helper": "search",
      "args": ["a((bc|de){1,3})?(?(1)d|e)", "zzaezz"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "conditional", "group-exists", "optional-group", "search", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the numbered absent-group success path on `ae` so the scorecard records that the conditional else arm still accepts when the optional grouped alternation is skipped entirely."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-str",
      "operation": "module_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_conditional_numbered_module_lower_bound_bc_workflow",
      "helper": "search",
      "args": ["a((bc|de){1,3})?(?(1)d|e)", "zzabcdzz"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "conditional", "group-exists", "optional-group", "search", "module", "present", "lower-bound", "bc-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound present success path on `abcd` so the frontier shows that one `bc` repetition is enough to force the later yes arm to consume `d`."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-conditional-numbered-module-search-lower-bound-de-workflow-str",
      "operation": "module_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_conditional_numbered_module_lower_bound_de_workflow",
      "helper": "search",
      "args": ["a((bc|de){1,3})?(?(1)d|e)", "zzadedzz"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "conditional", "group-exists", "optional-group", "search", "module", "present", "lower-bound", "de-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound present success path on `aded` so the same bounded slice stays explicit for the single `de` branch variant."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-mixed-workflow-str",
      "operation": "pattern_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_conditional_numbered_pattern_mixed_workflow",
      "pattern": "a((bc|de){1,3})?(?(1)d|e)",
      "helper": "fullmatch",
      "args": ["abcded"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "conditional", "group-exists", "optional-group", "fullmatch", "pattern", "present", "mixed-branches", "str", "gap"],
      "notes": [
        "Documents the numbered mixed-branch success path on `abcded` so the publication captures one present-group workflow where the grouped alternation spans `bc` then `de` before the conditional yes arm matches."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-missing-trailing-d-workflow-str",
      "operation": "pattern_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_conditional_numbered_pattern_no_match_missing_trailing_d_workflow",
      "pattern": "a((bc|de){1,3})?(?(1)d|e)",
      "helper": "fullmatch",
      "args": ["abcde"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "conditional", "group-exists", "optional-group", "fullmatch", "pattern", "present", "no-match", "missing-trailing-d", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abcde` so the scorecard stays explicit that the conditional yes arm still rejects a present-group branch when the required trailing `d` is missing."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-conditional-named-compile-metadata-str",
      "operation": "compile",
      "family": "wider_ranged_repeat_quantified_group_alternation_conditional_named_compile_metadata",
      "pattern": "a(?P<outer>(bc|de){1,3})?(?(outer)d|e)",
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "conditional", "group-exists", "optional-group", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the named compile frontier for the same optional grouped `{1,3}` alternation with one later named group-exists conditional."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-absent-workflow-str",
      "operation": "module_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_conditional_named_module_absent_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(bc|de){1,3})?(?(outer)d|e)", "zzaezz"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "conditional", "group-exists", "optional-group", "named-group", "search", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the named absent-group success path on `ae` so the published frontier records the else-arm acceptance when the optional named outer capture is skipped."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-lower-bound-de-workflow-str",
      "operation": "module_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_conditional_named_module_lower_bound_de_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(bc|de){1,3})?(?(outer)d|e)", "zzadedzz"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "conditional", "group-exists", "optional-group", "named-group", "search", "module", "present", "lower-bound", "de-branch", "str", "gap"],
      "notes": [
        "Documents the named lower-bound present success path on `aded` so the scorecard records the named outer capture on the single `de` branch variant too."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-conditional-named-module-search-upper-bound-mixed-workflow-str",
      "operation": "module_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_conditional_named_module_upper_bound_mixed_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(bc|de){1,3})?(?(outer)d|e)", "zzabcbcdedzz"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "conditional", "group-exists", "optional-group", "named-group", "search", "module", "present", "upper-bound", "mixed-branches", "str", "gap"],
      "notes": [
        "Documents the named upper-bound success path on `abcbcded` so the scorecard includes one three-repetition grouped alternation before the conditional yes arm consumes the final `d`."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-mixed-workflow-str",
      "operation": "pattern_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_conditional_named_pattern_mixed_workflow",
      "pattern": "a(?P<outer>(bc|de){1,3})?(?(outer)d|e)",
      "helper": "fullmatch",
      "args": ["abcded"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "conditional", "group-exists", "optional-group", "named-group", "fullmatch", "pattern", "present", "mixed-branches", "str", "gap"],
      "notes": [
        "Documents the named mixed-branch success path on `abcded` so the visible `outer` capture remains explicit when the bounded grouped alternation spans `bcde` before the yes arm matches."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-short-workflow-str",
      "operation": "pattern_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_conditional_named_pattern_no_match_short_workflow",
      "pattern": "a(?P<outer>(bc|de){1,3})?(?(outer)d|e)",
      "helper": "fullmatch",
      "args": ["ad"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "wider-range", "conditional", "group-exists", "optional-group", "named-group", "fullmatch", "pattern", "no-match", "below-repeat-count", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `ad` so the scorecard stays explicit that the bounded grouped alternation still needs at least one repetition before the yes arm can apply."
      ]
    }
  ]
}
