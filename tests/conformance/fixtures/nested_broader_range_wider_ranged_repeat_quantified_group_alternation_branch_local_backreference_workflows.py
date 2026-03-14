MANIFEST = {
  "schema_version": 1,
  "manifest_id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-workflows",
  "layer": "match_behavior",
  "suite_id": "match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
      "operation": "compile",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_numbered_backreference_compile_metadata",
      "pattern": "a((b|c){1,4})\\2d",
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the numbered broader `{1,4}` nested grouped-alternation frontier where one outer capture encloses one counted inner branch site whose final branch must be replayed by a same-branch backreference."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
      "operation": "module_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_numbered_backreference_module_lower_bound_b_branch_workflow",
      "helper": "search",
      "args": ["a((b|c){1,4})\\2d", "zzabbdzz"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "search", "module", "lower-bound", "b-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound success path on `abbd`, where one inner `b` branch is captured inside the broader counted repeat and replayed through the later branch-local backreference."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-c-branch-str",
      "operation": "module_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_numbered_backreference_module_lower_bound_c_branch_workflow",
      "helper": "search",
      "args": ["a((b|c){1,4})\\2d", "zzaccdzz"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "search", "module", "lower-bound", "c-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound success path on `accd`, so both same-branch lower-bound captures remain explicit in the published pack."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-b-branch-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_numbered_backreference_pattern_second_iteration_b_branch_workflow",
      "pattern": "a((b|c){1,4})\\2d",
      "helper": "fullmatch",
      "args": ["abbbd"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "second-iteration", "b-branch", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the numbered repeated-branch success path on `abbbd`, where the outer capture widens to two repetitions and the final inner `b` branch still drives the later backreference."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-fourth-repetition-mixed-branches-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_numbered_backreference_pattern_fourth_repetition_mixed_branches_workflow",
      "pattern": "a((b|c){1,4})\\2d",
      "helper": "fullmatch",
      "args": ["abcbccd"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "fourth-repetition", "mixed-branches", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the numbered broader counted-repeat success path on `abcbccd`, so the publication includes a mixed four-iteration outer capture whose final inner `c` branch is replayed at the boundary."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-missing-replay-lower-bound-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_numbered_backreference_pattern_no_match_missing_replay_lower_bound_workflow",
      "pattern": "a((b|c){1,4})\\2d",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "no-match", "missing-replay", "lower-bound", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abcd`, so the lower-bound counted repeat still records that the later same-branch backreference must be present even when one inner branch matched."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-overflow-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_numbered_backreference_pattern_no_match_overflow_workflow",
      "pattern": "a((b|c){1,4})\\2d",
      "helper": "fullmatch",
      "args": ["abbbbbbd"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "no-match", "overflow", "str", "gap"],
      "notes": [
        "Documents the numbered no-match overflow path on `abbbbbbd`, proving the broader `{1,4}` envelope still rejects a fifth inner repetition before the replayed branch."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-compile-metadata-str",
      "operation": "compile",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_named_backreference_compile_metadata",
      "pattern": "a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named broader `{1,4}` frontier where one visible outer capture encloses one counted named inner branch site that is replayed through a same-branch named backreference."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
      "operation": "module_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_named_backreference_module_lower_bound_c_branch_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d", "zzaccdzz"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "search", "module", "lower-bound", "c-branch", "str", "gap"],
      "notes": [
        "Documents the named lower-bound success path on `accd`, keeping both `outer` and `inner` visible when the broader counted repeat closes on the `c` branch."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-b-branch-str",
      "operation": "module_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_named_backreference_module_lower_bound_b_branch_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d", "zzabbdzz"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "search", "module", "lower-bound", "b-branch", "str", "gap"],
      "notes": [
        "Documents the named lower-bound success path on `abbd`, so both lower-bound same-branch captures stay explicit under the named outer and inner groups."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-second-iteration-mixed-branches-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_named_backreference_pattern_second_iteration_mixed_branches_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
      "helper": "fullmatch",
      "args": ["abccd"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "second-iteration", "mixed-branches", "outer-capture", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the named mixed-branch repeated success path on `abccd`, so the broader counted-repeat pack records a visible `outer` capture plus final `inner` branch under repetition."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-upper-bound-all-c-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_named_backreference_pattern_upper_bound_all_c_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
      "helper": "fullmatch",
      "args": ["acccccd"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "upper-bound", "c-branch", "outer-capture", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the named upper-bound success path on `acccccd`, so the publication records the visible four-iteration `outer` capture plus final `inner` replay on the all-`c` branch."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-missing-replay-mixed-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_named_backreference_pattern_no_match_missing_replay_mixed_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
      "helper": "fullmatch",
      "args": ["abcbcd"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "no-match", "missing-replay", "mixed-branches", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `abcbcd`, so the scorecard keeps the repeated mixed-branch failure explicit when the final named replay no longer matches the last inner branch."
      ]
    },
    {
      "id": "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-overflow-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_named_backreference_pattern_no_match_overflow_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
      "helper": "fullmatch",
      "args": ["accccccd"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "ranged-repeat", "wider-range", "broader-range", "counted-repeat", "fullmatch", "pattern", "no-match", "overflow", "str", "gap"],
      "notes": [
        "Documents the named no-match overflow path on `accccccd`, proving the broader `{1,4}` counted-repeat envelope still rejects a fifth inner iteration before the named replay."
      ]
    }
  ]
}
