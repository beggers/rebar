MANIFEST = {
  "schema_version": 1,
  "manifest_id": "quantified-alternation-backtracking-heavy-workflows",
  "layer": "match_behavior",
  "suite_id": "match.quantified_alternation_backtracking_heavy",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "quantified-alternation-backtracking-heavy-numbered-compile-metadata-str",
      "operation": "compile",
      "family": "quantified_alternation_backtracking_heavy_numbered_compile_metadata",
      "pattern": "a(b|bc){1,2}d",
      "categories": ["grouped", "alternation", "overlapping-branches", "quantified", "bounded-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the bounded numbered compile frontier for one {1,2} quantified alternation whose overlapping `b|bc` branches force CPython-compatible backtracking choices."
      ]
    },
    {
      "id": "quantified-alternation-backtracking-heavy-numbered-module-search-lower-bound-b-branch-str",
      "operation": "module_call",
      "family": "quantified_alternation_backtracking_heavy_numbered_module_lower_bound_b_branch_workflow",
      "helper": "search",
      "args": ["a(b|bc){1,2}d", "zzabdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantified", "bounded-repeat", "search", "module", "lower-bound", "b-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound module success path on `abd` so the scorecard keeps the one-repetition `b` branch explicit before broader counted ranges reopen."
      ]
    },
    {
      "id": "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-lower-bound-bc-branch-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_backtracking_heavy_numbered_pattern_lower_bound_bc_branch_workflow",
      "pattern": "a(b|bc){1,2}d",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantified", "bounded-repeat", "fullmatch", "pattern", "lower-bound", "bc-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound compiled-pattern success path on `abcd` so the overlapping `bc` branch stays explicit alongside the shorter `b` branch."
      ]
    },
    {
      "id": "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-b-then-bc-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_backtracking_heavy_numbered_pattern_second_repetition_b_then_bc_workflow",
      "pattern": "a(b|bc){1,2}d",
      "helper": "fullmatch",
      "args": ["abbcd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantified", "bounded-repeat", "fullmatch", "pattern", "second-repetition", "b-then-bc", "str", "gap"],
      "notes": [
        "Documents the numbered second-repetition success path on `abbcd` so the frontier records one short-branch repetition followed by one longer overlapping branch."
      ]
    },
    {
      "id": "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-bc-then-b-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_backtracking_heavy_numbered_pattern_second_repetition_bc_then_b_workflow",
      "pattern": "a(b|bc){1,2}d",
      "helper": "fullmatch",
      "args": ["abcbd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantified", "bounded-repeat", "fullmatch", "pattern", "second-repetition", "bc-then-b", "str", "gap"],
      "notes": [
        "Documents the numbered mixed-order second-repetition success path on `abcbd` so the scorecard shows that backtracking can still settle on the longer branch before the shorter branch."
      ]
    },
    {
      "id": "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-bc-then-bc-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_backtracking_heavy_numbered_pattern_second_repetition_bc_then_bc_workflow",
      "pattern": "a(b|bc){1,2}d",
      "helper": "fullmatch",
      "args": ["abcbcd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantified", "bounded-repeat", "fullmatch", "pattern", "second-repetition", "bc-then-bc", "str", "gap"],
      "notes": [
        "Documents the numbered second-repetition success path on `abcbcd` so the frontier includes the two-long-branch case within the exact `{1,2}` envelope."
      ]
    },
    {
      "id": "quantified-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_backtracking_heavy_numbered_pattern_no_match_workflow",
      "pattern": "a(b|bc){1,2}d",
      "helper": "fullmatch",
      "args": ["abccd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantified", "bounded-repeat", "fullmatch", "pattern", "no-match", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abccd` so the scorecard stays explicit that one `bc` branch plus a trailing `c` cannot satisfy the bounded overlapping alternation."
      ]
    },
    {
      "id": "quantified-alternation-backtracking-heavy-named-compile-metadata-str",
      "operation": "compile",
      "family": "quantified_alternation_backtracking_heavy_named_compile_metadata",
      "pattern": "a(?P<word>b|bc){1,2}d",
      "categories": ["grouped", "alternation", "overlapping-branches", "quantified", "bounded-repeat", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named compile frontier for the same bounded quantified overlapping alternation under one visible `word` capture."
      ]
    },
    {
      "id": "quantified-alternation-backtracking-heavy-named-module-search-lower-bound-bc-branch-str",
      "operation": "module_call",
      "family": "quantified_alternation_backtracking_heavy_named_module_lower_bound_bc_branch_workflow",
      "helper": "search",
      "args": ["a(?P<word>b|bc){1,2}d", "zzabcdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantified", "bounded-repeat", "named-group", "search", "module", "lower-bound", "bc-branch", "str", "gap"],
      "notes": [
        "Documents the named lower-bound module success path on `abcd` so the published frontier records the visible named capture when the longer overlapping branch wins."
      ]
    },
    {
      "id": "quantified-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-b-then-b-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_backtracking_heavy_named_pattern_second_repetition_b_then_b_workflow",
      "pattern": "a(?P<word>b|bc){1,2}d",
      "helper": "fullmatch",
      "args": ["abbd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantified", "bounded-repeat", "named-group", "fullmatch", "pattern", "second-repetition", "b-then-b", "str", "gap"],
      "notes": [
        "Documents the named second-repetition success path on `abbd` so the scorecard keeps the two-short-branch case explicit on the compiled-pattern path."
      ]
    },
    {
      "id": "quantified-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-bc-then-b-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_backtracking_heavy_named_pattern_second_repetition_bc_then_b_workflow",
      "pattern": "a(?P<word>b|bc){1,2}d",
      "helper": "fullmatch",
      "args": ["abcbd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantified", "bounded-repeat", "named-group", "fullmatch", "pattern", "second-repetition", "bc-then-b", "str", "gap"],
      "notes": [
        "Documents the named mixed-order second-repetition success path on `abcbd` so the visible named capture comes from the final shorter branch after an earlier longer branch."
      ]
    },
    {
      "id": "quantified-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_backtracking_heavy_named_pattern_no_match_workflow",
      "pattern": "a(?P<word>b|bc){1,2}d",
      "helper": "fullmatch",
      "args": ["abccd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantified", "bounded-repeat", "named-group", "fullmatch", "pattern", "no-match", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `abccd` so the scorecard stays explicit that the overlapping quantified alternation still rejects the extra `c` even when a named capture is involved."
      ]
    }
  ]
}
