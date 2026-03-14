MANIFEST = {
  "schema_version": 1,
  "manifest_id": "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows",
  "layer": "match_behavior",
  "suite_id": "match.broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
      "operation": "compile",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_compile_metadata",
      "pattern": "a((bc|b)c){1,4}d",
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the numbered compile frontier for one broader `{1,4}` grouped alternation whose overlapping `(bc|b)c` branches force CPython-compatible backtracking choices without widening into open-ended repeats, grouped conditionals, replacement workflows, branch-local backreferences, nested grouped alternation, or broader grouped backtracking."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
      "operation": "module_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_module_lower_bound_short_branch_workflow",
      "helper": "search",
      "args": ["a((bc|b)c){1,4}d", "zzabcdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "search", "module", "lower-bound", "short-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound success path on `abcd` so the scorecard keeps the one-repetition shorter `bc` branch explicit inside the broader `{1,4}` envelope."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-long-branch-str",
      "operation": "module_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_module_lower_bound_long_branch_workflow",
      "helper": "search",
      "args": ["a((bc|b)c){1,4}d", "zzabccdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "search", "module", "lower-bound", "long-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound success path on `abccd` so the longer overlapping `bcc` branch is published alongside the shorter branch at the same `{1,4}` lower bound."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-str",
      "operation": "pattern_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_pattern_second_repetition_short_then_long_workflow",
      "pattern": "a((bc|b)c){1,4}d",
      "helper": "fullmatch",
      "args": ["abcbccd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "second-repetition", "short-then-long", "str", "gap"],
      "notes": [
        "Documents the numbered mixed-order second-repetition success path on `abcbccd` so the publication records one shorter branch followed by the longer overlapping branch."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-long-then-short-str",
      "operation": "pattern_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_pattern_second_repetition_long_then_short_workflow",
      "pattern": "a((bc|b)c){1,4}d",
      "helper": "fullmatch",
      "args": ["abccbcd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "second-repetition", "long-then-short", "str", "gap"],
      "notes": [
        "Documents the numbered mixed-order second-repetition success path on `abccbcd` so the broader slice records the alternate longer-then-shorter branch choice too."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-fourth-repetition-mixed-str",
      "operation": "pattern_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_pattern_fourth_repetition_mixed_workflow",
      "pattern": "a((bc|b)c){1,4}d",
      "helper": "fullmatch",
      "args": ["abcbccbccbcd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "fourth-repetition", "upper-bound", "mixed", "str", "gap"],
      "notes": [
        "Documents the numbered upper-bound success path on `abcbccbccbcd` so the broader `{1,4}` frontier includes one four-repetition mixed branch order before the trailing `d`."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-invalid-tail-str",
      "operation": "pattern_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_pattern_no_match_invalid_tail_workflow",
      "pattern": "a((bc|b)c){1,4}d",
      "helper": "fullmatch",
      "args": ["abccbd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "no-match", "invalid-tail", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abccbd` so the scorecard records a branch sequence that fails before the trailing `d` even though the broader counted-repeat envelope is otherwise in range."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
      "operation": "compile",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_compile_metadata",
      "pattern": "a(?P<word>(bc|b)c){1,4}d",
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named compile frontier for the same broader `{1,4}` grouped backtracking-heavy slice under one visible `word` capture."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-lower-bound-long-branch-str",
      "operation": "module_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_module_lower_bound_long_branch_workflow",
      "helper": "search",
      "args": ["a(?P<word>(bc|b)c){1,4}d", "zzabccdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "search", "module", "lower-bound", "long-branch", "str", "gap"],
      "notes": [
        "Documents the named lower-bound success path on `abccd` so the visible `word` capture stays explicit when the longer overlapping branch wins."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-short-then-long-str",
      "operation": "module_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_module_second_repetition_short_then_long_workflow",
      "helper": "search",
      "args": ["a(?P<word>(bc|b)c){1,4}d", "zzabcbccdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "search", "module", "second-repetition", "short-then-long", "str", "gap"],
      "notes": [
        "Documents the named mixed-order second-repetition success path on `abcbccd` so the visible capture remains explicit when the longer overlapping branch lands second."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-fourth-repetition-mixed-str",
      "operation": "module_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_module_fourth_repetition_mixed_workflow",
      "helper": "search",
      "args": ["a(?P<word>(bc|b)c){1,4}d", "zzabcbccbccbcdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "search", "module", "fourth-repetition", "upper-bound", "mixed", "str", "gap"],
      "notes": [
        "Documents the named upper-bound success path on `abcbccbccbcd` so the broader `{1,4}` slice records one four-repetition mixed branch order under the visible `word` capture."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-long-then-short-str",
      "operation": "pattern_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_pattern_second_repetition_long_then_short_workflow",
      "pattern": "a(?P<word>(bc|b)c){1,4}d",
      "helper": "fullmatch",
      "args": ["abccbcd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "fullmatch", "pattern", "second-repetition", "long-then-short", "str", "gap"],
      "notes": [
        "Documents the named mixed-order second-repetition success path on `abccbcd` so the visible capture comes from the final shorter branch after an earlier longer branch."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-invalid-tail-str",
      "operation": "pattern_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_pattern_no_match_invalid_tail_workflow",
      "pattern": "a(?P<word>(bc|b)c){1,4}d",
      "helper": "fullmatch",
      "args": ["abccbd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "fullmatch", "pattern", "no-match", "invalid-tail", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `abccbd` so the scorecard records a visible-capture workflow whose branch choices still fail before the trailing `d`."
      ]
    },
    {
      "id": "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-overflow-str",
      "operation": "pattern_call",
      "family": "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_pattern_no_match_overflow_workflow",
      "pattern": "a(?P<word>(bc|b)c){1,4}d",
      "helper": "fullmatch",
      "args": ["abcbcbcbcbcd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "named-group", "fullmatch", "pattern", "no-match", "overflow", "str", "gap"],
      "notes": [
        "Documents the named no-match overflow path on `abcbcbcbcbcd` so the scorecard records that a fifth grouped repetition still exceeds the bounded `{1,4}` envelope even when each overlapping branch choice is otherwise valid."
      ]
    }
  ]
}
