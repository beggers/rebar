MANIFEST = {
  "schema_version": 1,
  "manifest_id": "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows",
  "layer": "match_behavior",
  "suite_id": "match.broader_range_open_ended_quantified_group_alternation_backtracking_heavy",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
      "operation": "compile",
      "family": "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_numbered_compile_metadata",
      "pattern": "a((bc|b)c){2,}d",
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the numbered compile frontier for one broader-range open-ended `{2,}` grouped alternation whose overlapping `(bc|b)c` branches force CPython-compatible backtracking without widening into conditionals, replacements, branch-local backreferences, nested grouped alternation, or broader grouped backtracking."
      ]
    },
    {
      "id": "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
      "operation": "module_call",
      "family": "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_numbered_module_lower_bound_short_branch_workflow",
      "helper": "search",
      "args": ["a((bc|b)c){2,}d", "zzabcbcdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "search", "module", "lower-bound", "short-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound success path on `abcbcd` so the scorecard records the two-repetition shorter-branch workflow at the shifted `{2,}` lower bound."
      ]
    },
    {
      "id": "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-long-branch-str",
      "operation": "module_call",
      "family": "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_numbered_module_lower_bound_long_branch_workflow",
      "helper": "search",
      "args": ["a((bc|b)c){2,}d", "zzabcbccdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "search", "module", "lower-bound", "long-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound success path on `abcbccd` so the broader-range slice keeps the longer overlapping branch explicit too."
      ]
    },
    {
      "id": "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-long-then-short-str",
      "operation": "pattern_call",
      "family": "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_numbered_pattern_second_repetition_long_then_short_workflow",
      "pattern": "a((bc|b)c){2,}d",
      "helper": "fullmatch",
      "args": ["abccbcd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "second-repetition", "long-then-short", "str", "gap"],
      "notes": [
        "Documents the numbered mixed-branch success path on `abccbcd` so the broader-range frontier includes one bounded longer-then-shorter backtracking workflow."
      ]
    },
    {
      "id": "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-fourth-repetition-short-only-str",
      "operation": "pattern_call",
      "family": "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_numbered_pattern_fourth_repetition_short_only_workflow",
      "pattern": "a((bc|b)c){2,}d",
      "helper": "fullmatch",
      "args": ["abcbcbcbcd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "fourth-repetition", "short-only", "str", "gap"],
      "notes": [
        "Documents one bounded longer success path on `abcbcbcbcd` so the exact `{2,}` slice records a fourth repetition without pretending to exhaust arbitrary-length grouped backtracking."
      ]
    },
    {
      "id": "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-one-repetition-str",
      "operation": "pattern_call",
      "family": "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_numbered_pattern_no_match_one_repetition_workflow",
      "pattern": "a((bc|b)c){2,}d",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "no-match", "one-repetition", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abcd` so the scorecard stays explicit that the broader-range open-ended form rejects a single grouped repetition."
      ]
    },
    {
      "id": "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-invalid-tail-str",
      "operation": "pattern_call",
      "family": "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_numbered_pattern_no_match_invalid_tail_workflow",
      "pattern": "a((bc|b)c){2,}d",
      "helper": "fullmatch",
      "args": ["abccbd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "no-match", "invalid-tail", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abccbd` so the scorecard records a branch sequence that fails before the trailing `d`."
      ]
    },
    {
      "id": "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
      "operation": "compile",
      "family": "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_named_compile_metadata",
      "pattern": "a(?P<word>(bc|b)c){2,}d",
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the named compile frontier for the same broader-range `{2,}` grouped backtracking-heavy slice under one visible `word` capture."
      ]
    },
    {
      "id": "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-lower-bound-long-branch-str",
      "operation": "module_call",
      "family": "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_named_module_lower_bound_long_branch_workflow",
      "helper": "search",
      "args": ["a(?P<word>(bc|b)c){2,}d", "zzabcbccdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "named-group", "search", "module", "lower-bound", "long-branch", "str", "gap"],
      "notes": [
        "Documents the named lower-bound success path on `abcbccd` so the visible `word` capture stays explicit when the longer overlapping branch wins."
      ]
    },
    {
      "id": "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-long-then-short-str",
      "operation": "module_call",
      "family": "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_named_module_second_repetition_long_then_short_workflow",
      "helper": "search",
      "args": ["a(?P<word>(bc|b)c){2,}d", "zzabccbcdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "named-group", "search", "module", "second-repetition", "long-then-short", "str", "gap"],
      "notes": [
        "Documents the named mixed-branch success path on `abccbcd` so the published slice records the visible final capture after backtracking from the earlier longer branch."
      ]
    },
    {
      "id": "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-fourth-repetition-short-only-str",
      "operation": "module_call",
      "family": "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_named_module_fourth_repetition_short_only_workflow",
      "helper": "search",
      "args": ["a(?P<word>(bc|b)c){2,}d", "zzabcbcbcbcdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "named-group", "search", "module", "fourth-repetition", "short-only", "str", "gap"],
      "notes": [
        "Documents one bounded named fourth-repetition success path on `abcbcbcbcd` so the exact `{2,}` slice includes a longer workflow under the visible capture."
      ]
    },
    {
      "id": "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-short-then-long-str",
      "operation": "pattern_call",
      "family": "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_named_pattern_second_repetition_short_then_long_workflow",
      "pattern": "a(?P<word>(bc|b)c){2,}d",
      "helper": "fullmatch",
      "args": ["abcbccd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "named-group", "fullmatch", "pattern", "second-repetition", "short-then-long", "str", "gap"],
      "notes": [
        "Documents the named shorter-then-longer success path on `abcbccd` so the broader-range pack records the alternate mixed-order two-repetition branch choice too."
      ]
    },
    {
      "id": "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-one-repetition-str",
      "operation": "pattern_call",
      "family": "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_named_pattern_no_match_one_repetition_workflow",
      "pattern": "a(?P<word>(bc|b)c){2,}d",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "named-group", "fullmatch", "pattern", "no-match", "one-repetition", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `abcd` so the scorecard stays explicit that one grouped repetition is still below the shifted `{2,}` lower bound."
      ]
    },
    {
      "id": "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-no-match-invalid-tail-str",
      "operation": "module_call",
      "family": "broader_range_open_ended_quantified_group_alternation_backtracking_heavy_named_module_no_match_invalid_tail_workflow",
      "helper": "search",
      "args": ["a(?P<word>(bc|b)c){2,}d", "zzabccbdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "named-group", "search", "module", "no-match", "invalid-tail", "str", "gap"],
      "notes": [
        "Documents the named no-match search path on `abccbd` so the scorecard records a haystack whose branch choices fail before the trailing `d`."
      ]
    }
  ]
}
