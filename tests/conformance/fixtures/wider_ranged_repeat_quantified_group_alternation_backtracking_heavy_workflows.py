MANIFEST = {
  "schema_version": 1,
  "manifest_id": "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows",
  "layer": "match_behavior",
  "suite_id": "match.wider_ranged_repeat_quantified_group_alternation_backtracking_heavy",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
      "operation": "compile",
      "family": "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_compile_metadata",
      "pattern": "a((bc|b)c){1,3}d",
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "counted-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the numbered compile frontier for one wider `{1,3}` grouped alternation whose overlapping `(bc|b)c` branches force CPython-compatible backtracking choices without widening into open-ended repeats, conditionals, replacement workflows, nested grouped alternation, or branch-local backreferences."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
      "operation": "module_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_module_lower_bound_short_branch_workflow",
      "helper": "search",
      "args": ["a((bc|b)c){1,3}d", "zzabcdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "counted-repeat", "search", "module", "lower-bound", "short-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound success path on `abcd` so the scorecard keeps the one-repetition shorter `bc` branch explicit."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-lower-bound-long-branch-str",
      "operation": "pattern_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_pattern_lower_bound_long_branch_workflow",
      "pattern": "a((bc|b)c){1,3}d",
      "helper": "fullmatch",
      "args": ["abccd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "counted-repeat", "fullmatch", "pattern", "lower-bound", "long-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound success path on `abccd` so the longer overlapping `bcc` branch is published alongside the shorter `bc` branch."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-short-str",
      "operation": "pattern_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_pattern_second_repetition_short_then_short_workflow",
      "pattern": "a((bc|b)c){1,3}d",
      "helper": "fullmatch",
      "args": ["abcbcd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "counted-repeat", "fullmatch", "pattern", "second-repetition", "short-then-short", "str", "gap"],
      "notes": [
        "Documents the numbered second-repetition success path on `abcbcd` so the wider counted-repeat frontier includes the two-short-branch case."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-str",
      "operation": "pattern_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_pattern_second_repetition_short_then_long_workflow",
      "pattern": "a((bc|b)c){1,3}d",
      "helper": "fullmatch",
      "args": ["abcbccd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "counted-repeat", "fullmatch", "pattern", "second-repetition", "short-then-long", "str", "gap"],
      "notes": [
        "Documents the numbered mixed-order second-repetition success path on `abcbccd` so the publication records one shorter branch followed by the longer overlapping branch."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-overlap-tail-str",
      "operation": "pattern_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_pattern_no_match_overlap_tail_workflow",
      "pattern": "a((bc|b)c){1,3}d",
      "helper": "fullmatch",
      "args": ["abcccd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "counted-repeat", "fullmatch", "pattern", "no-match", "overlap-tail", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abcccd` so the scorecard stays explicit that a partial overlapping branch tail cannot satisfy the widened grouped alternation before the trailing `d`."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
      "operation": "compile",
      "family": "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_compile_metadata",
      "pattern": "a(?P<word>(bc|b)c){1,3}d",
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "counted-repeat", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named compile frontier for the same wider `{1,3}` grouped backtracking-heavy slice under one visible `word` capture."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-lower-bound-long-branch-str",
      "operation": "module_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_module_lower_bound_long_branch_workflow",
      "helper": "search",
      "args": ["a(?P<word>(bc|b)c){1,3}d", "zzabccdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "counted-repeat", "named-group", "search", "module", "lower-bound", "long-branch", "str", "gap"],
      "notes": [
        "Documents the named lower-bound success path on `abccd` so the visible `word` capture stays explicit when the longer overlapping branch wins."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-third-repetition-mixed-str",
      "operation": "module_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_module_third_repetition_mixed_workflow",
      "helper": "search",
      "args": ["a(?P<word>(bc|b)c){1,3}d", "zzabcbccbccdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "counted-repeat", "named-group", "search", "module", "third-repetition", "mixed", "str", "gap"],
      "notes": [
        "Documents the named module-level third-repetition success path on `abcbccbccd` so the widened frontier records one bounded three-repetition mixed branch order."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-long-then-short-str",
      "operation": "pattern_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_pattern_second_repetition_long_then_short_workflow",
      "pattern": "a(?P<word>(bc|b)c){1,3}d",
      "helper": "fullmatch",
      "args": ["abccbcd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "counted-repeat", "named-group", "fullmatch", "pattern", "second-repetition", "long-then-short", "str", "gap"],
      "notes": [
        "Documents the named mixed-order second-repetition success path on `abccbcd` so the visible capture comes from the final shorter branch after an earlier longer branch."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-third-repetition-short-short-long-str",
      "operation": "pattern_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_pattern_third_repetition_short_short_long_workflow",
      "pattern": "a(?P<word>(bc|b)c){1,3}d",
      "helper": "fullmatch",
      "args": ["abcbcbccd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "counted-repeat", "named-group", "fullmatch", "pattern", "third-repetition", "short-short-long", "str", "gap"],
      "notes": [
        "Documents the named third-repetition success path on `abcbcbccd` so the pack includes one bounded upper-edge success where the longer overlapping branch lands last."
      ]
    },
    {
      "id": "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-no-match-invalid-tail-str",
      "operation": "module_call",
      "family": "wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_module_no_match_invalid_tail_workflow",
      "helper": "search",
      "args": ["a(?P<word>(bc|b)c){1,3}d", "zzabcccezz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "counted-repeat", "named-group", "search", "module", "no-match", "invalid-tail", "str", "gap"],
      "notes": [
        "Documents the named no-match search path on `abccce` so the scorecard records a haystack whose overlapping branch choices fail before the trailing `d`."
      ]
    }
  ]
}
