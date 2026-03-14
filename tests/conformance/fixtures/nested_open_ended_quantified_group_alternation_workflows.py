MANIFEST = {
  "schema_version": 1,
  "manifest_id": "nested-open-ended-quantified-group-alternation-workflows",
  "layer": "match_behavior",
  "suite_id": "match.nested_open_ended_quantified_group_alternation",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "nested-open-ended-quantified-group-alternation-numbered-compile-metadata-str",
      "operation": "compile",
      "family": "nested_open_ended_quantified_group_alternation_numbered_compile_metadata",
      "pattern": "a((bc|de){1,})d",
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "open-ended-repeat", "counted-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the numbered nested open-ended grouped-alternation compile frontier with one outer capture around one `(bc|de){1,}` site and no broader grouped conditional, replacement, or backtracking-heavy follow-ons."
      ]
    },
    {
      "id": "nested-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
      "operation": "module_call",
      "family": "nested_open_ended_quantified_group_alternation_numbered_module_lower_bound_bc_workflow",
      "helper": "search",
      "args": ["a((bc|de){1,})d", "zzabcdzz"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "open-ended-repeat", "counted-repeat", "search", "module", "lower-bound", "bc", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound nested grouped success path on `abcd` so the scorecard records the single `bc` branch under one outer capture."
      ]
    },
    {
      "id": "nested-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-de-str",
      "operation": "module_call",
      "family": "nested_open_ended_quantified_group_alternation_numbered_module_lower_bound_de_workflow",
      "helper": "search",
      "args": ["a((bc|de){1,})d", "zzadedzz"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "open-ended-repeat", "counted-repeat", "search", "module", "lower-bound", "de", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound nested grouped success path on `aded` so the alternate single `de` branch stays explicit in the new pack."
      ]
    },
    {
      "id": "nested-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",
      "operation": "pattern_call",
      "family": "nested_open_ended_quantified_group_alternation_numbered_pattern_third_repetition_mixed_workflow",
      "pattern": "a((bc|de){1,})d",
      "helper": "fullmatch",
      "args": ["abcbcded"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "open-ended-repeat", "counted-repeat", "fullmatch", "pattern", "third-repetition", "mixed", "str", "gap"],
      "notes": [
        "Documents the numbered compiled-pattern mixed-branch success path on `abcbcded` so the nested open-ended pack includes one bounded repeated workflow beyond the lower bound."
      ]
    },
    {
      "id": "nested-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-fourth-repetition-de-str",
      "operation": "pattern_call",
      "family": "nested_open_ended_quantified_group_alternation_numbered_pattern_fourth_repetition_de_workflow",
      "pattern": "a((bc|de){1,})d",
      "helper": "fullmatch",
      "args": ["adededed"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "open-ended-repeat", "counted-repeat", "fullmatch", "pattern", "fourth-repetition", "de", "str", "gap"],
      "notes": [
        "Documents the numbered compiled-pattern all-`de` success path on `adededed` so the pack records one longer bounded repetition under the same outer capture."
      ]
    },
    {
      "id": "nested-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-no-match-short-str",
      "operation": "pattern_call",
      "family": "nested_open_ended_quantified_group_alternation_numbered_pattern_no_match_short_workflow",
      "pattern": "a((bc|de){1,})d",
      "helper": "fullmatch",
      "args": ["ae"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "open-ended-repeat", "counted-repeat", "fullmatch", "pattern", "no-match", "short", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `ae` so the new nested grouped form stays explicit about rejecting texts that never satisfy the repeated inner alternation."
      ]
    },
    {
      "id": "nested-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-no-match-missing-trailing-d-str",
      "operation": "pattern_call",
      "family": "nested_open_ended_quantified_group_alternation_numbered_pattern_no_match_missing_trailing_d_workflow",
      "pattern": "a((bc|de){1,})d",
      "helper": "fullmatch",
      "args": ["abcbcdede"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "open-ended-repeat", "counted-repeat", "fullmatch", "pattern", "no-match", "missing-trailing-d", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path when the grouped repetition is present but the surrounding literal suffix does not close with the required trailing `d`."
      ]
    },
    {
      "id": "nested-open-ended-quantified-group-alternation-named-compile-metadata-str",
      "operation": "compile",
      "family": "nested_open_ended_quantified_group_alternation_named_compile_metadata",
      "pattern": "a(?P<outer>(bc|de){1,})d",
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the named nested open-ended grouped-alternation compile frontier with one visible outer capture around the repeated inner alternation."
      ]
    },
    {
      "id": "nested-open-ended-quantified-group-alternation-named-module-search-lower-bound-bc-str",
      "operation": "module_call",
      "family": "nested_open_ended_quantified_group_alternation_named_module_lower_bound_bc_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(bc|de){1,})d", "zzabcdzz"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "search", "module", "lower-bound", "bc", "str", "gap"],
      "notes": [
        "Documents the named lower-bound nested grouped success path on `abcd` so the visible `outer` capture is present at the first reopened post-consolidation frontier."
      ]
    },
    {
      "id": "nested-open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",
      "operation": "module_call",
      "family": "nested_open_ended_quantified_group_alternation_named_module_lower_bound_de_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(bc|de){1,})d", "zzadedzz"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "search", "module", "lower-bound", "de", "str", "gap"],
      "notes": [
        "Documents the named lower-bound nested grouped success path on `aded` so the single `de` branch remains explicit under the outer named capture."
      ]
    },
    {
      "id": "nested-open-ended-quantified-group-alternation-named-pattern-fullmatch-third-repetition-mixed-str",
      "operation": "pattern_call",
      "family": "nested_open_ended_quantified_group_alternation_named_pattern_third_repetition_mixed_workflow",
      "pattern": "a(?P<outer>(bc|de){1,})d",
      "helper": "fullmatch",
      "args": ["abcbcded"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "fullmatch", "pattern", "third-repetition", "mixed", "str", "gap"],
      "notes": [
        "Documents the named compiled-pattern mixed-branch success path on `abcbcded` so one bounded longer workflow stays explicit under the visible outer capture."
      ]
    },
    {
      "id": "nested-open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",
      "operation": "pattern_call",
      "family": "nested_open_ended_quantified_group_alternation_named_pattern_fourth_repetition_de_workflow",
      "pattern": "a(?P<outer>(bc|de){1,})d",
      "helper": "fullmatch",
      "args": ["adededed"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "fullmatch", "pattern", "fourth-repetition", "de", "str", "gap"],
      "notes": [
        "Documents the named compiled-pattern all-`de` success path on `adededed` so the pack captures one bounded longer repetition with a visible outer capture."
      ]
    },
    {
      "id": "nested-open-ended-quantified-group-alternation-named-pattern-fullmatch-no-match-short-str",
      "operation": "pattern_call",
      "family": "nested_open_ended_quantified_group_alternation_named_pattern_no_match_short_workflow",
      "pattern": "a(?P<outer>(bc|de){1,})d",
      "helper": "fullmatch",
      "args": ["ae"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "fullmatch", "pattern", "no-match", "short", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `ae` so the scorecard records the same missing-repetition failure mode with one visible outer capture."
      ]
    },
    {
      "id": "nested-open-ended-quantified-group-alternation-named-pattern-fullmatch-no-match-missing-trailing-d-str",
      "operation": "pattern_call",
      "family": "nested_open_ended_quantified_group_alternation_named_pattern_no_match_missing_trailing_d_workflow",
      "pattern": "a(?P<outer>(bc|de){1,})d",
      "helper": "fullmatch",
      "args": ["abcbcdede"],
      "categories": ["grouped", "nested-group", "alternation", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "fullmatch", "pattern", "no-match", "missing-trailing-d", "str", "gap"],
      "notes": [
        "Documents the named no-match path when the grouped repetition is present but the surrounding literal suffix never satisfies the trailing `d`."
      ]
    }
  ]
}
