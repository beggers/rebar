MANIFEST = {
  "schema_version": 1,
  "manifest_id": "nested-group-alternation-branch-local-backreference-workflows",
  "layer": "match_behavior",
  "suite_id": "match.nested_group_alternation_branch_local_backreference",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "nested-group-alternation-branch-local-numbered-backreference-compile-metadata-str",
      "operation": "compile",
      "family": "nested_group_alternation_branch_local_numbered_backreference_compile_metadata",
      "pattern": "a((b|c))\\2d",
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the bounded numbered compile frontier for one outer nested capture whose inner alternation must be replayed by a same-branch backreference before the trailing literal."
      ]
    },
    {
      "id": "nested-group-alternation-branch-local-numbered-backreference-module-search-b-branch-str",
      "operation": "module_call",
      "family": "nested_group_alternation_branch_local_numbered_backreference_module_b_branch_workflow",
      "helper": "search",
      "args": ["a((b|c))\\2d", "zzabbdzz"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "search", "module", "b-branch", "str", "gap"],
      "notes": [
        "Documents the module-level numbered success path on `abbd`, where the nested inner branch selects `b` and the later same-branch backreference resolves after the outer group closes."
      ]
    },
    {
      "id": "nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-c-branch-str",
      "operation": "pattern_call",
      "family": "nested_group_alternation_branch_local_numbered_backreference_pattern_c_branch_workflow",
      "pattern": "a((b|c))\\2d",
      "helper": "fullmatch",
      "args": ["accd"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "fullmatch", "pattern", "c-branch", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch numbered success path on `accd`, keeping the single nested c-branch capture and its same-branch backreference observable at the public API."
      ]
    },
    {
      "id": "nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str",
      "operation": "pattern_call",
      "family": "nested_group_alternation_branch_local_numbered_backreference_pattern_no_match_workflow",
      "pattern": "a((b|c))\\2d",
      "helper": "fullmatch",
      "args": ["abd"],
      "categories": ["grouped", "nested-group", "alternation", "numbered-backreference", "branch-local", "fullmatch", "pattern", "no-match", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abd`, so the published frontier shows that the nested alternation still has to satisfy the later same-branch backreference."
      ]
    },
    {
      "id": "nested-group-alternation-branch-local-named-backreference-compile-metadata-str",
      "operation": "compile",
      "family": "nested_group_alternation_branch_local_named_backreference_compile_metadata",
      "pattern": "a(?P<outer>(?P<inner>b|c))(?P=inner)d",
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named compile frontier where one named outer capture contains one named inner alternation site that is replayed through a same-branch named backreference."
      ]
    },
    {
      "id": "nested-group-alternation-branch-local-named-backreference-module-search-c-branch-str",
      "operation": "module_call",
      "family": "nested_group_alternation_branch_local_named_backreference_module_c_branch_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(?P<inner>b|c))(?P=inner)d", "zzaccdzz"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "search", "module", "c-branch", "str", "gap"],
      "notes": [
        "Documents the module-level named success path on `accd`, keeping both `outer` and `inner` captures observable when the nested alternation selects the c branch."
      ]
    },
    {
      "id": "nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-b-branch-str",
      "operation": "pattern_call",
      "family": "nested_group_alternation_branch_local_named_backreference_pattern_b_branch_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c))(?P=inner)d",
      "helper": "fullmatch",
      "args": ["abbd"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "fullmatch", "pattern", "b-branch", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch named success path on `abbd`, keeping both named captures visible under a successful same-branch backreference."
      ]
    },
    {
      "id": "nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str",
      "operation": "pattern_call",
      "family": "nested_group_alternation_branch_local_named_backreference_pattern_no_match_workflow",
      "pattern": "a(?P<outer>(?P<inner>b|c))(?P=inner)d",
      "helper": "fullmatch",
      "args": ["acd"],
      "categories": ["grouped", "nested-group", "alternation", "named-group", "named-backreference", "branch-local", "fullmatch", "pattern", "no-match", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `acd`, so the scorecard shows that the nested c branch still fails when the later named backreference is missing."
      ]
    }
  ]
}
