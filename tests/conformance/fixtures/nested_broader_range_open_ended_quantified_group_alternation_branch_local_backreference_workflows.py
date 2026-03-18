MANIFEST = {
  "schema_version": 1,
  "manifest_id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-workflows",
  "layer": "match_behavior",
  "suite_id": "match.nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
      "operation": "compile",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_numbered_backreference_compile_metadata",
      "pattern": "a((b|c){2,})\\2d",
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the numbered broader-range open-ended `{2,}` nested grouped-alternation frontier where one outer capture encloses one counted inner branch site whose final branch is replayed by a same-branch backreference."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
      "operation": "module_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_numbered_backreference_module_lower_bound_b_branch_workflow",
      "helper": "search",
      "args": ["a((b|c){2,})\\2d", "zzabbbdzz"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "search", "module", "lower-bound", "b-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound search success path on `abbbd`, where two inner `b` repetitions satisfy the broader `{2,}` floor before the final same-branch replay."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_numbered_backreference_pattern_lower_bound_c_branch_workflow",
      "pattern": "a((b|c){2,})\\2d",
      "helper": "fullmatch",
      "args": ["acccd"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "lower-bound", "c-branch", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the numbered compiled-pattern lower-bound success path on `acccd`, keeping the two-step `c` branch plus replayed final inner capture explicit at the public API."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-fourth-repetition-mixed-branches-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_numbered_backreference_pattern_fourth_repetition_mixed_branches_workflow",
      "pattern": "a((b|c){2,})\\2d",
      "helper": "fullmatch",
      "args": ["abcbccd"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "fourth-repetition", "mixed-branches", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the numbered mixed-branch broader-range success path on `abcbccd`, so the publication includes a repeated outer capture whose final inner `c` branch is replayed at the boundary."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-one-repetition-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_numbered_backreference_pattern_no_match_one_repetition_workflow",
      "pattern": "a((b|c){2,})\\2d",
      "helper": "fullmatch",
      "args": ["abbd"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "no-match", "one-repetition", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abbd`, proving one inner repetition is still too few before the final same-branch backreference under the broader `{2,}` floor."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-compile-metadata-str",
      "operation": "compile",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_named_backreference_compile_metadata",
      "pattern": "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named broader-range open-ended `{2,}` frontier where one visible outer capture encloses one counted named inner branch site that is replayed through a same-branch named backreference."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
      "operation": "module_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_named_backreference_module_lower_bound_c_branch_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d", "zzacccdzz"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "search", "module", "lower-bound", "c-branch", "outer-capture", "str", "gap"],
      "notes": [
        "Documents the named lower-bound search success path on `acccd`, keeping both `outer` and `inner` observable when the broader `{2,}` floor closes on the `c` branch."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-lower-bound-b-branch-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_named_backreference_pattern_lower_bound_b_branch_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
      "helper": "fullmatch",
      "args": ["abbbd"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "lower-bound", "b-branch", "outer-capture", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the named compiled-pattern lower-bound success path on `abbbd`, keeping the visible `outer` and final `inner` captures observable at the minimum accepted `{2,}` width."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-third-repetition-mixed-branches-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_named_backreference_pattern_third_repetition_mixed_branches_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
      "helper": "fullmatch",
      "args": ["abcccd"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "third-repetition", "mixed-branches", "outer-capture", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the named mixed-branch broader-range success path on `abcccd`, so the publication keeps the repeated visible `outer` capture plus final selected `inner` branch explicit under the open-ended `{2,}` repeat."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-one-repetition-str",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_named_backreference_pattern_no_match_one_repetition_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
      "helper": "fullmatch",
      "args": ["accd"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "no-match", "one-repetition", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `accd`, keeping the broader-range `{2,}` floor honest when only one inner repetition appears before the final named replay."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-compile-metadata-bytes",
      "operation": "compile",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_numbered_backreference_compile_metadata",
      "pattern": "a((b|c){2,})\\2d",
      "text_model": "bytes",
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "compile", "metadata", "bytes", "gap"],
      "notes": [
        "Publishes the same numbered broader-range open-ended `{2,}` nested grouped-alternation compile frontier for bytes payloads while keeping the branch-local-backreference bytes parity gap explicit until the follow-on parity task lands."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-bytes",
      "operation": "module_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_numbered_backreference_module_lower_bound_b_branch_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a((b|c){2,})\\2d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzabbbdzz"
        }
      ],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "search", "module", "lower-bound", "b-branch", "bytes", "gap"],
      "notes": [
        "Documents the numbered lower-bound search success path on `abbbd` with bytes payloads, where two inner `b` repetitions satisfy the broader `{2,}` floor before the final same-branch replay."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-bytes",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_numbered_backreference_pattern_lower_bound_c_branch_workflow",
      "pattern": "a((b|c){2,})\\2d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "acccd"
        }
      ],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "lower-bound", "c-branch", "final-inner-capture", "bytes", "gap"],
      "notes": [
        "Documents the numbered compiled-pattern lower-bound success path on `acccd` with bytes payloads, keeping the two-step `c` branch plus replayed final inner capture explicit at the public API."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-fourth-repetition-mixed-branches-bytes",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_numbered_backreference_pattern_fourth_repetition_mixed_branches_workflow",
      "pattern": "a((b|c){2,})\\2d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcbccd"
        }
      ],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "fourth-repetition", "mixed-branches", "final-inner-capture", "bytes", "gap"],
      "notes": [
        "Documents the numbered mixed-branch broader-range success path on `abcbccd` with bytes payloads, so the publication includes a repeated outer capture whose final inner `c` branch is replayed at the boundary."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-one-repetition-bytes",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_numbered_backreference_pattern_no_match_one_repetition_workflow",
      "pattern": "a((b|c){2,})\\2d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abbd"
        }
      ],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "no-match", "one-repetition", "bytes", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abbd` with bytes payloads, proving one inner repetition is still too few before the final same-branch backreference under the broader `{2,}` floor."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-compile-metadata-bytes",
      "operation": "compile",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_named_backreference_compile_metadata",
      "pattern": "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
      "text_model": "bytes",
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "compile", "metadata", "bytes", "gap"],
      "notes": [
        "Publishes the matching named broader-range open-ended `{2,}` compile frontier for bytes payloads while keeping the branch-local-backreference bytes parity gap explicit until the follow-on parity task lands."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-bytes",
      "operation": "module_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_named_backreference_module_lower_bound_c_branch_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzacccdzz"
        }
      ],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "search", "module", "lower-bound", "c-branch", "outer-capture", "bytes", "gap"],
      "notes": [
        "Documents the named lower-bound search success path on `acccd` with bytes payloads, keeping both `outer` and `inner` observable when the broader `{2,}` floor closes on the `c` branch."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-lower-bound-b-branch-bytes",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_named_backreference_pattern_lower_bound_b_branch_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abbbd"
        }
      ],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "lower-bound", "b-branch", "outer-capture", "final-inner-capture", "bytes", "gap"],
      "notes": [
        "Documents the named compiled-pattern lower-bound success path on `abbbd` with bytes payloads, keeping the visible `outer` and final `inner` captures observable at the minimum accepted `{2,}` width."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-third-repetition-mixed-branches-bytes",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_named_backreference_pattern_third_repetition_mixed_branches_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcccd"
        }
      ],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "third-repetition", "mixed-branches", "outer-capture", "final-inner-capture", "bytes", "gap"],
      "notes": [
        "Documents the named mixed-branch broader-range success path on `abcccd` with bytes payloads, so the publication keeps the repeated visible `outer` capture plus final selected `inner` branch explicit under the open-ended `{2,}` repeat."
      ]
    },
    {
      "id": "nested-broader-range-open-ended-quantified-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-one-repetition-bytes",
      "operation": "pattern_call",
      "family": "nested_broader_range_open_ended_quantified_group_alternation_branch_local_named_backreference_pattern_no_match_one_repetition_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "accd"
        }
      ],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "open-ended-repeat", "broader-range", "counted-repeat", "fullmatch", "pattern", "no-match", "one-repetition", "bytes", "gap"],
      "notes": [
        "Documents the named no-match path on `accd` with bytes payloads, keeping the broader-range `{2,}` floor honest when only one inner repetition appears before the final named replay."
      ]
    }
  ]
}
