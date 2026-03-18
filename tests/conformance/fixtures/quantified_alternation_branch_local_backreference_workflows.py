MANIFEST = {
  "schema_version": 1,
  "manifest_id": "quantified-alternation-branch-local-backreference-workflows",
  "layer": "match_behavior",
  "suite_id": "match.quantified_alternation_branch_local_backreference",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "quantified-alternation-branch-local-numbered-backreference-compile-metadata-str",
      "operation": "compile",
      "family": "quantified_alternation_branch_local_numbered_backreference_compile_metadata",
      "pattern": "a((b|c)\\2){1,2}d",
      "categories": ["grouped", "alternation", "numbered-backreference", "branch-local", "quantified", "bounded-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the bounded numbered compile frontier for one {1,2} quantified alternation whose same-branch backreference must still resolve inside each repetition."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str",
      "operation": "module_call",
      "family": "quantified_alternation_branch_local_numbered_backreference_module_lower_bound_b_branch_workflow",
      "helper": "search",
      "args": ["a((b|c)\\2){1,2}d", "zzabbdzz"],
      "categories": ["grouped", "alternation", "numbered-backreference", "branch-local", "quantified", "bounded-repeat", "search", "module", "lower-bound", "b-branch", "str", "gap"],
      "notes": [
        "Documents the module-level numbered lower-bound success path on `abbd` so the scorecard records that one quantified repetition can satisfy the same-branch backreference through the b branch."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_branch_local_numbered_backreference_pattern_lower_bound_c_branch_workflow",
      "pattern": "a((b|c)\\2){1,2}d",
      "helper": "fullmatch",
      "args": ["accd"],
      "categories": ["grouped", "alternation", "numbered-backreference", "branch-local", "quantified", "bounded-repeat", "fullmatch", "pattern", "lower-bound", "c-branch", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch numbered lower-bound success path on `accd` for the c branch without widening into larger counted ranges."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-repetition-b-branch-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_branch_local_numbered_backreference_pattern_second_repetition_b_branch_workflow",
      "pattern": "a((b|c)\\2){1,2}d",
      "helper": "fullmatch",
      "args": ["abbbbd"],
      "categories": ["grouped", "alternation", "numbered-backreference", "branch-local", "quantified", "bounded-repeat", "fullmatch", "pattern", "second-repetition", "b-branch", "str", "gap"],
      "notes": [
        "Documents the numbered second-repetition success path on `abbbbd` so the published frontier captures that the later backreference still resolves against the final branch-local capture after two repetitions."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_branch_local_numbered_backreference_pattern_no_match_workflow",
      "pattern": "a((b|c)\\2){1,2}d",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "alternation", "numbered-backreference", "branch-local", "quantified", "bounded-repeat", "fullmatch", "pattern", "no-match", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abcd` so the scorecard shows that each quantified repetition still has to satisfy the same-branch backreference."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-named-backreference-compile-metadata-str",
      "operation": "compile",
      "family": "quantified_alternation_branch_local_named_backreference_compile_metadata",
      "pattern": "a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
      "categories": ["grouped", "alternation", "named-group", "named-backreference", "branch-local", "quantified", "bounded-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named compile frontier for one bounded quantified alternation whose branch-local `inner` capture must still feed a same-branch named backreference."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str",
      "operation": "module_call",
      "family": "quantified_alternation_branch_local_named_backreference_module_lower_bound_c_branch_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d", "zzaccdzz"],
      "categories": ["grouped", "alternation", "named-group", "named-backreference", "branch-local", "quantified", "bounded-repeat", "search", "module", "lower-bound", "c-branch", "str", "gap"],
      "notes": [
        "Documents the module-level named lower-bound success path on `accd` so the published frontier records the named outer and inner captures after one c-branch repetition."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-c-branch-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_branch_local_named_backreference_pattern_second_repetition_c_branch_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
      "helper": "fullmatch",
      "args": ["accccd"],
      "categories": ["grouped", "alternation", "named-group", "named-backreference", "branch-local", "quantified", "bounded-repeat", "fullmatch", "pattern", "second-repetition", "c-branch", "str", "gap"],
      "notes": [
        "Documents the named second-repetition success path on `accccd` so the scorecard records the final named captures after two c-branch repetitions settle."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-mixed-branches-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_branch_local_named_backreference_pattern_second_repetition_mixed_branches_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
      "helper": "fullmatch",
      "args": ["abbccd"],
      "categories": ["grouped", "alternation", "named-group", "named-backreference", "branch-local", "quantified", "bounded-repeat", "fullmatch", "pattern", "second-repetition", "mixed-branches", "str", "gap"],
      "notes": [
        "Documents the named mixed-branch second-repetition success path on `abbccd` so the published frontier shows that the last repetition still determines the visible branch-local capture."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_branch_local_named_backreference_pattern_no_match_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "alternation", "named-group", "named-backreference", "branch-local", "quantified", "bounded-repeat", "fullmatch", "pattern", "no-match", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `abcd` so the scorecard makes it explicit that the bounded quantified repetition still fails when the same-branch named backreference is not satisfied."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-numbered-backreference-compile-metadata-bytes",
      "operation": "compile",
      "family": "quantified_alternation_branch_local_numbered_backreference_compile_metadata",
      "pattern": "a((b|c)\\2){1,2}d",
      "text_model": "bytes",
      "categories": ["grouped", "alternation", "numbered-backreference", "branch-local", "quantified", "bounded-repeat", "compile", "metadata", "bytes", "gap"],
      "notes": [
        "Publishes the same bounded numbered compile frontier for bytes payloads while keeping the quantified-alternation branch-local-backreference bytes parity gap explicit until the follow-on parity task lands."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-bytes",
      "operation": "module_call",
      "family": "quantified_alternation_branch_local_numbered_backreference_module_lower_bound_b_branch_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a((b|c)\\2){1,2}d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzabbdzz"
        }
      ],
      "categories": ["grouped", "alternation", "numbered-backreference", "branch-local", "quantified", "bounded-repeat", "search", "module", "lower-bound", "b-branch", "bytes", "gap"],
      "notes": [
        "Documents the module-level numbered lower-bound success path on `abbd` with bytes payloads so the bytes follow-on frontier keeps the one-repetition b branch explicit."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_branch_local_numbered_backreference_pattern_lower_bound_c_branch_workflow",
      "pattern": "a((b|c)\\2){1,2}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "accd"
        }
      ],
      "categories": ["grouped", "alternation", "numbered-backreference", "branch-local", "quantified", "bounded-repeat", "fullmatch", "pattern", "lower-bound", "c-branch", "bytes", "gap"],
      "notes": [
        "Documents the bounded Pattern.fullmatch numbered lower-bound c-branch success path on `accd` with bytes payloads without widening beyond the exact `{1,2}` frontier."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-repetition-b-branch-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_branch_local_numbered_backreference_pattern_second_repetition_b_branch_workflow",
      "pattern": "a((b|c)\\2){1,2}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abbbbd"
        }
      ],
      "categories": ["grouped", "alternation", "numbered-backreference", "branch-local", "quantified", "bounded-repeat", "fullmatch", "pattern", "second-repetition", "b-branch", "bytes", "gap"],
      "notes": [
        "Documents the numbered second-repetition success path on `abbbbd` with bytes payloads so the bytes publication records that the later backreference still resolves against the final branch-local b capture after two repetitions."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_branch_local_numbered_backreference_pattern_no_match_workflow",
      "pattern": "a((b|c)\\2){1,2}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcd"
        }
      ],
      "categories": ["grouped", "alternation", "numbered-backreference", "branch-local", "quantified", "bounded-repeat", "fullmatch", "pattern", "no-match", "bytes", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abcd` with bytes payloads so the scorecard stays explicit that each quantified repetition still has to satisfy the same-branch backreference."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-named-backreference-compile-metadata-bytes",
      "operation": "compile",
      "family": "quantified_alternation_branch_local_named_backreference_compile_metadata",
      "pattern": "a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
      "text_model": "bytes",
      "categories": ["grouped", "alternation", "named-group", "named-backreference", "branch-local", "quantified", "bounded-repeat", "compile", "metadata", "bytes", "gap"],
      "notes": [
        "Publishes the matching named compile frontier for bytes payloads while keeping the branch-local named-backreference bytes parity gap explicit until the follow-on parity task lands."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-bytes",
      "operation": "module_call",
      "family": "quantified_alternation_branch_local_named_backreference_module_lower_bound_c_branch_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzaccdzz"
        }
      ],
      "categories": ["grouped", "alternation", "named-group", "named-backreference", "branch-local", "quantified", "bounded-repeat", "search", "module", "lower-bound", "c-branch", "bytes", "gap"],
      "notes": [
        "Documents the module-level named lower-bound success path on `accd` with bytes payloads so the bytes follow-on frontier records the named outer and inner captures after one c-branch repetition."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-c-branch-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_branch_local_named_backreference_pattern_second_repetition_c_branch_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "accccd"
        }
      ],
      "categories": ["grouped", "alternation", "named-group", "named-backreference", "branch-local", "quantified", "bounded-repeat", "fullmatch", "pattern", "second-repetition", "c-branch", "bytes", "gap"],
      "notes": [
        "Documents the named second-repetition success path on `accccd` with bytes payloads so the bytes frontier records the final named captures after two c-branch repetitions settle."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-second-repetition-mixed-branches-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_branch_local_named_backreference_pattern_second_repetition_mixed_branches_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abbccd"
        }
      ],
      "categories": ["grouped", "alternation", "named-group", "named-backreference", "branch-local", "quantified", "bounded-repeat", "fullmatch", "pattern", "second-repetition", "mixed-branches", "bytes", "gap"],
      "notes": [
        "Documents the named mixed-branch second-repetition success path on `abbccd` with bytes payloads so the bytes publication shows that the last repetition still determines the visible branch-local capture."
      ]
    },
    {
      "id": "quantified-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_branch_local_named_backreference_pattern_no_match_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcd"
        }
      ],
      "categories": ["grouped", "alternation", "named-group", "named-backreference", "branch-local", "quantified", "bounded-repeat", "fullmatch", "pattern", "no-match", "bytes", "gap"],
      "notes": [
        "Documents the named no-match path on `abcd` with bytes payloads so the scorecard keeps it explicit that the bounded quantified repetition still fails when the same-branch named backreference is not satisfied."
      ]
    }
  ]
}
