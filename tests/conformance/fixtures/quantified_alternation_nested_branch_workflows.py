MANIFEST = {
  "schema_version": 1,
  "manifest_id": "quantified-alternation-nested-branch-workflows",
  "layer": "match_behavior",
  "suite_id": "match.quantified_alternation_nested_branch",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "quantified-alternation-nested-branch-numbered-compile-metadata-str",
      "operation": "compile",
      "family": "quantified_alternation_nested_branch_numbered_compile_metadata",
      "pattern": "a((b|c)|de){1,2}d",
      "categories": ["grouped", "alternation", "nested-alternation", "quantified", "bounded-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the bounded numbered compile frontier for one outer {1,2} quantified alternation whose first branch nests one inner `b|c` site beside one literal `de` sibling branch."
      ]
    },
    {
      "id": "quantified-alternation-nested-branch-numbered-module-search-lower-bound-inner-branch-str",
      "operation": "module_call",
      "family": "quantified_alternation_nested_branch_numbered_module_lower_bound_inner_branch_workflow",
      "helper": "search",
      "args": ["a((b|c)|de){1,2}d", "zzabdzz"],
      "categories": ["grouped", "alternation", "nested-alternation", "quantified", "bounded-repeat", "search", "module", "lower-bound", "inner-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound module success path on `abd` so the scorecard records that one inner `b|c` branch repetition still feeds the outer capture before the trailing literal `d` matches."
      ]
    },
    {
      "id": "quantified-alternation-nested-branch-numbered-pattern-fullmatch-lower-bound-literal-branch-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_nested_branch_numbered_pattern_lower_bound_literal_branch_workflow",
      "pattern": "a((b|c)|de){1,2}d",
      "helper": "fullmatch",
      "args": ["aded"],
      "categories": ["grouped", "alternation", "nested-alternation", "quantified", "bounded-repeat", "fullmatch", "pattern", "lower-bound", "literal-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound Pattern.fullmatch success path on `aded` so the frontier keeps the sibling `de` branch explicit without widening beyond the exact `{1,2}` envelope."
      ]
    },
    {
      "id": "quantified-alternation-nested-branch-numbered-pattern-fullmatch-second-repetition-mixed-branches-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_nested_branch_numbered_pattern_second_repetition_mixed_branches_workflow",
      "pattern": "a((b|c)|de){1,2}d",
      "helper": "fullmatch",
      "args": ["abded"],
      "categories": ["grouped", "alternation", "nested-alternation", "quantified", "bounded-repeat", "fullmatch", "pattern", "second-repetition", "mixed-branches", "str", "gap"],
      "notes": [
        "Documents the numbered mixed-branch second-repetition success path on `abded` so the published frontier captures one inner-branch repetition followed by one sibling `de` branch within the same bounded repeat."
      ]
    },
    {
      "id": "quantified-alternation-nested-branch-numbered-pattern-fullmatch-no-match-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_nested_branch_numbered_pattern_no_match_workflow",
      "pattern": "a((b|c)|de){1,2}d",
      "helper": "fullmatch",
      "args": ["abde"],
      "categories": ["grouped", "alternation", "nested-alternation", "quantified", "bounded-repeat", "fullmatch", "pattern", "no-match", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abde` so the scorecard stays explicit that the trailing literal `d` sits outside the quantified group even after mixed branch selections consume `b` then `de`."
      ]
    },
    {
      "id": "quantified-alternation-nested-branch-named-compile-metadata-str",
      "operation": "compile",
      "family": "quantified_alternation_nested_branch_named_compile_metadata",
      "pattern": "a(?P<word>(b|c)|de){1,2}d",
      "categories": ["grouped", "alternation", "nested-alternation", "quantified", "bounded-repeat", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named compile frontier for the same bounded quantified outer alternation with one nested `b|c` branch and one sibling literal branch."
      ]
    },
    {
      "id": "quantified-alternation-nested-branch-named-module-search-lower-bound-literal-branch-str",
      "operation": "module_call",
      "family": "quantified_alternation_nested_branch_named_module_lower_bound_literal_branch_workflow",
      "helper": "search",
      "args": ["a(?P<word>(b|c)|de){1,2}d", "zzadedzz"],
      "categories": ["grouped", "alternation", "nested-alternation", "quantified", "bounded-repeat", "named-group", "search", "module", "lower-bound", "literal-branch", "str", "gap"],
      "notes": [
        "Documents the named lower-bound module success path on `aded` so the scorecard records the named outer capture when the sibling `de` branch is the only quantified repetition."
      ]
    },
    {
      "id": "quantified-alternation-nested-branch-named-pattern-fullmatch-lower-bound-inner-branch-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_nested_branch_named_pattern_lower_bound_inner_branch_workflow",
      "pattern": "a(?P<word>(b|c)|de){1,2}d",
      "helper": "fullmatch",
      "args": ["acd"],
      "categories": ["grouped", "alternation", "nested-alternation", "quantified", "bounded-repeat", "named-group", "fullmatch", "pattern", "lower-bound", "inner-branch", "str", "gap"],
      "notes": [
        "Documents the named lower-bound Pattern.fullmatch success path on `acd` so the frontier keeps one inner `b|c` branch success explicit on the compiled-pattern path."
      ]
    },
    {
      "id": "quantified-alternation-nested-branch-named-pattern-fullmatch-second-repetition-mixed-branches-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_nested_branch_named_pattern_second_repetition_mixed_branches_workflow",
      "pattern": "a(?P<word>(b|c)|de){1,2}d",
      "helper": "fullmatch",
      "args": ["adebd"],
      "categories": ["grouped", "alternation", "nested-alternation", "quantified", "bounded-repeat", "named-group", "fullmatch", "pattern", "second-repetition", "mixed-branches", "str", "gap"],
      "notes": [
        "Documents the named mixed-branch second-repetition success path on `adebd` so the visible named capture comes from the last inner-branch repetition after one earlier `de` branch."
      ]
    },
    {
      "id": "quantified-alternation-nested-branch-named-pattern-fullmatch-no-match-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_nested_branch_named_pattern_no_match_workflow",
      "pattern": "a(?P<word>(b|c)|de){1,2}d",
      "helper": "fullmatch",
      "args": ["adeb"],
      "categories": ["grouped", "alternation", "nested-alternation", "quantified", "bounded-repeat", "named-group", "fullmatch", "pattern", "no-match", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `adeb` so the scorecard stays explicit that consuming `de` then `b` still leaves the required trailing literal `d` outside the quantified group."
      ]
    }
  ]
}
