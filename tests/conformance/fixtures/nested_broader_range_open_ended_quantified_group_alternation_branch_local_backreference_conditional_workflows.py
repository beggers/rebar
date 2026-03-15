MANIFEST = {
  "schema_version": 1,
  "manifest_id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-workflows",
  "layer": "match_behavior",
  "suite_id": "match.nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-compile-metadata-str",
      "operation": "compile",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_numbered_compile_metadata",
      "pattern": "a((b|c){2,})\\2(?(2)d|e)",
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "conditional", "group-exists", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the numbered broader-range open-ended `{2,}` nested grouped-alternation frontier where one final same-branch replay is followed immediately by a later conditional on that inner capture slot."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-module-search-lower-bound-b-branch-workflow-str",
      "operation": "module_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_numbered_module_lower_bound_b_branch_workflow",
      "helper": "search",
      "args": ["a((b|c){2,})\\2(?(2)d|e)", "zzabbbdzz"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "conditional", "group-exists", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "search", "module", "lower-bound", "b-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound search success path on `abbbd`, where two inner `b` repetitions satisfy the broader `{2,}` floor before the replayed branch and trailing conditional yes-arm `d` both match."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-lower-bound-c-branch-workflow-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_numbered_pattern_lower_bound_c_branch_workflow",
      "pattern": "a((b|c){2,})\\2(?(2)d|e)",
      "helper": "fullmatch",
      "args": ["acccd"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "conditional", "group-exists", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "lower-bound", "c-branch", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the numbered compiled-pattern lower-bound success path on `acccd`, keeping the minimum accepted `c`-branch replay plus later conditional yes arm explicit at the public API."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-mixed-branches-workflow-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_numbered_pattern_mixed_branches_workflow",
      "pattern": "a((b|c){2,})\\2(?(2)d|e)",
      "helper": "fullmatch",
      "args": ["abcbccd"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "conditional", "group-exists", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "mixed-branches", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the numbered mixed-branch broader-range success path on `abcbccd`, so the publication includes one longer nested alternation whose final selected `c` branch is replayed before the trailing conditional `d`."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-pattern-fullmatch-no-match-missing-conditional-d-workflow-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_numbered_pattern_no_match_missing_conditional_d_workflow",
      "pattern": "a((b|c){2,})\\2(?(2)d|e)",
      "helper": "fullmatch",
      "args": ["abcbcc"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "conditional", "group-exists", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "no-match", "missing-conditional-d", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abcbcc`, proving the later conditional yes arm still requires a trailing `d` after the replayed final branch instead of rescuing the broader-range match."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-compile-metadata-str",
      "operation": "compile",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_named_compile_metadata",
      "pattern": "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "conditional", "group-exists", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named broader-range open-ended `{2,}` frontier where the visible `outer` capture encloses one counted inner branch site that is replayed and then checked by a later group-exists conditional."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-module-search-lower-bound-c-branch-workflow-str",
      "operation": "module_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_named_module_lower_bound_c_branch_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)", "zzacccdzz"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "conditional", "group-exists", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "search", "module", "lower-bound", "c-branch", "outer-capture", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the named lower-bound search success path on `acccd`, keeping both `outer` and `inner` observable when the minimum accepted `c`-branch replay is followed by the conditional yes-arm `d`."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-lower-bound-b-branch-workflow-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_named_pattern_lower_bound_b_branch_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
      "helper": "fullmatch",
      "args": ["abbbd"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "conditional", "group-exists", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "lower-bound", "b-branch", "outer-capture", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the named compiled-pattern lower-bound success path on `abbbd`, keeping the visible `outer` capture and final selected `inner` branch observable at the minimum accepted `{2,}` width."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-mixed-branches-workflow-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_named_pattern_mixed_branches_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
      "helper": "fullmatch",
      "args": ["abcbccd"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "conditional", "group-exists", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "mixed-branches", "outer-capture", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the named mixed-branch broader-range success path on `abcbccd`, so the visible `outer` capture and final selected `inner` branch stay explicit under the open-ended `{2,}` repeat."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-pattern-fullmatch-no-match-below-lower-bound-workflow-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_named_pattern_no_match_below_lower_bound_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
      "helper": "fullmatch",
      "args": ["abbd"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "conditional", "group-exists", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "no-match", "below-repeat-floor", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `abbd`, keeping the broader-range `{2,}` floor honest because only one inner repetition is available before the replayed final branch and later conditional yes arm."
      ]
    }
  ]
}
