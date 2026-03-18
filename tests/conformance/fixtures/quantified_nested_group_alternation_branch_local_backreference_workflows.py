MANIFEST = {
  "schema_version": 1,
  "manifest_id": "quantified-nested-group-alternation-branch-local-backreference-workflows",
  "layer": "match_behavior",
  "suite_id": "match.quantified_nested_group_alternation_branch_local_backreference",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "quantified-nested-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
      "operation": "compile",
      "family": "quantified_nested_group_alternation_branch_local_numbered_backreference_compile_metadata",
      "pattern": "a((b|c)+)\\2d",
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the bounded numbered compile frontier for one outer nested capture whose inner alternation is `+` quantified before a same-branch backreference replays the final inner branch."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
      "operation": "module_call",
      "family": "quantified_nested_group_alternation_branch_local_numbered_backreference_module_lower_bound_b_branch_workflow",
      "helper": "search",
      "args": ["a((b|c)+)\\2d", "zzabbdzz"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "search", "module", "lower-bound", "b-branch", "str", "gap"],
      "notes": [
        "Documents the numbered module-level lower-bound success path on `abbd`, where one b-branch iteration is enough for the later same-branch backreference to succeed."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-str",
      "operation": "pattern_call",
      "family": "quantified_nested_group_alternation_branch_local_numbered_backreference_pattern_lower_bound_c_branch_workflow",
      "pattern": "a((b|c)+)\\2d",
      "helper": "fullmatch",
      "args": ["accd"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "fullmatch", "pattern", "lower-bound", "c-branch", "str", "gap"],
      "notes": [
        "Documents the bounded Pattern.fullmatch numbered lower-bound success path on `accd`, keeping the one-branch c capture plus replayed final inner branch explicit at the public API."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-b-branch-str",
      "operation": "pattern_call",
      "family": "quantified_nested_group_alternation_branch_local_numbered_backreference_pattern_second_iteration_b_branch_workflow",
      "pattern": "a((b|c)+)\\2d",
      "helper": "fullmatch",
      "args": ["abbbd"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "fullmatch", "pattern", "second-iteration", "b-branch", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the numbered repeated-branch success path on `abbbd`, so the outer capture grows across repetition while the final inner b branch still drives the later backreference."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str",
      "operation": "pattern_call",
      "family": "quantified_nested_group_alternation_branch_local_numbered_backreference_pattern_no_match_workflow",
      "pattern": "a((b|c)+)\\2d",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "fullmatch", "pattern", "no-match", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abcd`, so the published frontier shows that the quantified inner alternation still has to leave a branch value available for the final same-branch backreference."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-named-backreference-compile-metadata-str",
      "operation": "compile",
      "family": "quantified_nested_group_alternation_branch_local_named_backreference_compile_metadata",
      "pattern": "a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named compile frontier for one named outer capture containing one `+` quantified named inner alternation site that is replayed by a same-branch named backreference."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
      "operation": "module_call",
      "family": "quantified_nested_group_alternation_branch_local_named_backreference_module_lower_bound_c_branch_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(?P<inner>b|c)+)(?P=inner)d", "zzaccdzz"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "search", "module", "lower-bound", "c-branch", "str", "gap"],
      "notes": [
        "Documents the named module-level lower-bound success path on `accd`, keeping both `outer` and `inner` visible when one c branch is captured and replayed."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-lower-bound-b-branch-str",
      "operation": "pattern_call",
      "family": "quantified_nested_group_alternation_branch_local_named_backreference_pattern_lower_bound_b_branch_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
      "helper": "fullmatch",
      "args": ["abbd"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "fullmatch", "pattern", "lower-bound", "b-branch", "str", "gap"],
      "notes": [
        "Documents the named Pattern.fullmatch lower-bound success path on `abbd`, keeping the single-branch `outer` and `inner` captures observable without widening into broader counted repeats."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-second-iteration-mixed-branches-str",
      "operation": "pattern_call",
      "family": "quantified_nested_group_alternation_branch_local_named_backreference_pattern_second_iteration_mixed_branches_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
      "helper": "fullmatch",
      "args": ["abccd"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "fullmatch", "pattern", "second-iteration", "mixed-branches", "outer-capture", "final-inner-capture", "str", "gap"],
      "notes": [
        "Documents the named repeated mixed-branch success path on `abccd`, so the published slice keeps the repeated `outer` capture plus final `inner` branch observable under repetition."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str",
      "operation": "pattern_call",
      "family": "quantified_nested_group_alternation_branch_local_named_backreference_pattern_no_match_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
      "helper": "fullmatch",
      "args": ["acbd"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "fullmatch", "pattern", "no-match", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `acbd`, so the scorecard shows that the final named backreference still fails when the quantified inner alternation ends on the wrong branch."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-numbered-backreference-compile-metadata-bytes",
      "operation": "compile",
      "family": "quantified_nested_group_alternation_branch_local_numbered_backreference_compile_metadata",
      "pattern": "a((b|c)+)\\2d",
      "text_model": "bytes",
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "compile", "metadata", "bytes", "gap"],
      "notes": [
        "Publishes the same bounded numbered compile frontier for bytes payloads while keeping the quantified nested-group branch-local-backreference bytes parity gap explicit until the follow-on parity task lands."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-bytes",
      "operation": "module_call",
      "family": "quantified_nested_group_alternation_branch_local_numbered_backreference_module_lower_bound_b_branch_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a((b|c)+)\\2d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzabbdzz"
        }
      ],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "search", "module", "lower-bound", "b-branch", "bytes", "gap"],
      "notes": [
        "Documents the numbered module-level lower-bound success path on `abbd` with bytes payloads so the bytes follow-on frontier keeps the one-branch b capture explicit."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-bytes",
      "operation": "pattern_call",
      "family": "quantified_nested_group_alternation_branch_local_numbered_backreference_pattern_lower_bound_c_branch_workflow",
      "pattern": "a((b|c)+)\\2d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "accd"
        }
      ],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "fullmatch", "pattern", "lower-bound", "c-branch", "bytes", "gap"],
      "notes": [
        "Documents the bounded Pattern.fullmatch numbered lower-bound success path on `accd` with bytes payloads while keeping the one-branch c replay explicit at the public API."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-b-branch-bytes",
      "operation": "pattern_call",
      "family": "quantified_nested_group_alternation_branch_local_numbered_backreference_pattern_second_iteration_b_branch_workflow",
      "pattern": "a((b|c)+)\\2d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abbbd"
        }
      ],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "fullmatch", "pattern", "second-iteration", "b-branch", "final-inner-capture", "bytes", "gap"],
      "notes": [
        "Documents the numbered repeated-branch success path on `abbbd` with bytes payloads so the publication still records that the final inner b branch drives the later backreference."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-bytes",
      "operation": "pattern_call",
      "family": "quantified_nested_group_alternation_branch_local_numbered_backreference_pattern_no_match_workflow",
      "pattern": "a((b|c)+)\\2d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcd"
        }
      ],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "quantifier", "fullmatch", "pattern", "no-match", "bytes", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abcd` with bytes payloads so the published frontier stays explicit that the quantified inner alternation still has to leave a branch value available for the final same-branch backreference."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-named-backreference-compile-metadata-bytes",
      "operation": "compile",
      "family": "quantified_nested_group_alternation_branch_local_named_backreference_compile_metadata",
      "pattern": "a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
      "text_model": "bytes",
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "compile", "metadata", "bytes", "gap"],
      "notes": [
        "Publishes the matching named compile frontier for bytes payloads while keeping the same bounded named branch-local-backreference bytes parity gap explicit until the follow-on parity task lands."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-bytes",
      "operation": "module_call",
      "family": "quantified_nested_group_alternation_branch_local_named_backreference_module_lower_bound_c_branch_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a(?P<outer>(?P<inner>b|c)+)(?P=inner)d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzaccdzz"
        }
      ],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "search", "module", "lower-bound", "c-branch", "bytes", "gap"],
      "notes": [
        "Documents the named module-level lower-bound success path on `accd` with bytes payloads so the bytes follow-on frontier keeps the outer and inner named captures visible after one c branch."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-lower-bound-b-branch-bytes",
      "operation": "pattern_call",
      "family": "quantified_nested_group_alternation_branch_local_named_backreference_pattern_lower_bound_b_branch_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abbd"
        }
      ],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "fullmatch", "pattern", "lower-bound", "b-branch", "bytes", "gap"],
      "notes": [
        "Documents the named Pattern.fullmatch lower-bound success path on `abbd` with bytes payloads so the single-branch `outer` and `inner` captures stay observable on the bytes parity surface."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-second-iteration-mixed-branches-bytes",
      "operation": "pattern_call",
      "family": "quantified_nested_group_alternation_branch_local_named_backreference_pattern_second_iteration_mixed_branches_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abccd"
        }
      ],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "fullmatch", "pattern", "second-iteration", "mixed-branches", "outer-capture", "final-inner-capture", "bytes", "gap"],
      "notes": [
        "Documents the named repeated mixed-branch success path on `abccd` with bytes payloads so the publication keeps the repeated `outer` capture plus final `inner` branch observable under repetition."
      ]
    },
    {
      "id": "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-bytes",
      "operation": "pattern_call",
      "family": "quantified_nested_group_alternation_branch_local_named_backreference_pattern_no_match_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "acbd"
        }
      ],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "quantifier", "fullmatch", "pattern", "no-match", "bytes", "gap"],
      "notes": [
        "Documents the named no-match path on `acbd` with bytes payloads so the scorecard stays explicit that the final named backreference still fails when the quantified inner alternation ends on the wrong branch."
      ]
    }
  ]
}
