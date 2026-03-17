MANIFEST = {
  "schema_version": 1,
  "manifest_id": "open-ended-quantified-group-alternation-backtracking-heavy-workflows",
  "layer": "match_behavior",
  "suite_id": "match.open_ended_quantified_group_alternation_backtracking_heavy",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
      "operation": "compile",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_numbered_compile_metadata",
      "pattern": "a((bc|b)c){1,}d",
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the numbered compile frontier for one bounded open-ended `{1,}` grouped alternation whose overlapping `(bc|b)c` branches force CPython-compatible backtracking choices without widening into conditionals, replacements, branch-local backreferences, nested grouped alternation, or broader counted ranges."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
      "operation": "module_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_numbered_module_lower_bound_short_branch_workflow",
      "helper": "search",
      "args": ["a((bc|b)c){1,}d", "zzabcdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "search", "module", "lower-bound", "short-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound success path on `abcd` so the scorecard keeps the one-repetition shorter `bc` branch explicit at the open-ended grouped frontier."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-lower-bound-long-branch-str",
      "operation": "pattern_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_numbered_pattern_lower_bound_long_branch_workflow",
      "pattern": "a((bc|b)c){1,}d",
      "helper": "fullmatch",
      "args": ["abccd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "fullmatch", "pattern", "lower-bound", "long-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound success path on `abccd` so the longer overlapping `bcc` branch is published alongside the shorter `bc` branch."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-short-str",
      "operation": "pattern_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_numbered_pattern_second_repetition_short_then_short_workflow",
      "pattern": "a((bc|b)c){1,}d",
      "helper": "fullmatch",
      "args": ["abcbcd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "fullmatch", "pattern", "second-repetition", "short-then-short", "str", "gap"],
      "notes": [
        "Documents the numbered second-repetition success path on `abcbcd` so the pack includes the repeated shorter-branch workflow beyond the lower bound."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-str",
      "operation": "pattern_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_numbered_pattern_second_repetition_short_then_long_workflow",
      "pattern": "a((bc|b)c){1,}d",
      "helper": "fullmatch",
      "args": ["abcbccd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "fullmatch", "pattern", "second-repetition", "short-then-long", "str", "gap"],
      "notes": [
        "Documents the numbered mixed-order second-repetition success path on `abcbccd` so the open-ended slice records one shorter branch followed by the longer overlapping branch."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-overlap-tail-str",
      "operation": "pattern_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_numbered_pattern_no_match_overlap_tail_workflow",
      "pattern": "a((bc|b)c){1,}d",
      "helper": "fullmatch",
      "args": ["abcccd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "fullmatch", "pattern", "no-match", "overlap-tail", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abcccd` so the scorecard stays explicit that a partial overlapping branch tail cannot satisfy the open-ended grouped alternation before the trailing `d`."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
      "operation": "compile",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_named_compile_metadata",
      "pattern": "a(?P<word>(bc|b)c){1,}d",
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named compile frontier for the same bounded open-ended `{1,}` grouped backtracking-heavy slice under one visible `word` capture."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-lower-bound-long-branch-str",
      "operation": "module_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_named_module_lower_bound_long_branch_workflow",
      "helper": "search",
      "args": ["a(?P<word>(bc|b)c){1,}d", "zzabccdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "search", "module", "lower-bound", "long-branch", "str", "gap"],
      "notes": [
        "Documents the named lower-bound success path on `abccd` so the visible `word` capture stays explicit when the longer overlapping branch wins."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-long-then-short-str",
      "operation": "module_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_named_module_second_repetition_long_then_short_workflow",
      "helper": "search",
      "args": ["a(?P<word>(bc|b)c){1,}d", "zzabccbcdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "search", "module", "second-repetition", "long-then-short", "str", "gap"],
      "notes": [
        "Documents the named mixed-order second-repetition success path on `abccbcd` so the visible capture comes from the final shorter branch after an earlier longer branch."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-third-repetition-mixed-str",
      "operation": "module_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_named_module_third_repetition_mixed_workflow",
      "helper": "search",
      "args": ["a(?P<word>(bc|b)c){1,}d", "zzabcbccbcdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "search", "module", "third-repetition", "mixed", "str", "gap"],
      "notes": [
        "Documents the named module-level third-repetition success path on `abcbccbcd` so the open-ended frontier records one bounded three-repetition mixed branch order."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-fourth-repetition-short-only-str",
      "operation": "pattern_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_named_pattern_fourth_repetition_short_only_workflow",
      "pattern": "a(?P<word>(bc|b)c){1,}d",
      "helper": "fullmatch",
      "args": ["abcbcbcbcd"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "fullmatch", "pattern", "fourth-repetition", "short-only", "str", "gap"],
      "notes": [
        "Documents the named compiled-pattern success path on `abcbcbcbcd` so the pack includes one bounded fourth-repetition workflow without pretending to exhaust arbitrary-length repetition."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-no-match-invalid-tail-str",
      "operation": "module_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_named_module_no_match_invalid_tail_workflow",
      "helper": "search",
      "args": ["a(?P<word>(bc|b)c){1,}d", "zzabccbdzz"],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "search", "module", "no-match", "invalid-tail", "str", "gap"],
      "notes": [
        "Documents the named no-match search path on `abccbd` so the scorecard records a haystack whose branch choices fail before the trailing `d`."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",
      "operation": "compile",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_numbered_compile_metadata",
      "pattern": "a((bc|b)c){1,}d",
      "text_model": "bytes",
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "compile", "metadata", "bytes", "gap"],
      "notes": [
        "Mirrors the numbered compile frontier for the same bounded open-ended `{1,}` grouped backtracking-heavy slice with bytes payloads."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-bytes",
      "operation": "module_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_numbered_module_lower_bound_short_branch_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a((bc|b)c){1,}d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzabcdzz"
        }
      ],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "search", "module", "lower-bound", "short-branch", "bytes", "gap"],
      "notes": [
        "Documents the numbered lower-bound success path on `abcd` with bytes payloads so the shorter open-ended branch stays explicit on the bytes publication path too."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-lower-bound-long-branch-bytes",
      "operation": "pattern_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_numbered_pattern_lower_bound_long_branch_workflow",
      "pattern": "a((bc|b)c){1,}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abccd"
        }
      ],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "fullmatch", "pattern", "lower-bound", "long-branch", "bytes", "gap"],
      "notes": [
        "Documents the numbered lower-bound success path on `abccd` with bytes payloads so the longer overlapping `bcc` branch stays published alongside the shorter branch."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-short-bytes",
      "operation": "pattern_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_numbered_pattern_second_repetition_short_then_short_workflow",
      "pattern": "a((bc|b)c){1,}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcbcd"
        }
      ],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "fullmatch", "pattern", "second-repetition", "short-then-short", "bytes", "gap"],
      "notes": [
        "Documents the numbered repeated shorter-branch success path on `abcbcd` with bytes payloads so the bounded two-repetition workflow stays explicit on the bytes surface too."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-bytes",
      "operation": "pattern_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_numbered_pattern_second_repetition_short_then_long_workflow",
      "pattern": "a((bc|b)c){1,}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcbccd"
        }
      ],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "fullmatch", "pattern", "second-repetition", "short-then-long", "bytes", "gap"],
      "notes": [
        "Documents the numbered mixed-order second-repetition success path on `abcbccd` with bytes payloads so the shorter-then-longer branch order stays explicit on the bytes publication path."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-overlap-tail-bytes",
      "operation": "pattern_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_numbered_pattern_no_match_overlap_tail_workflow",
      "pattern": "a((bc|b)c){1,}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcccd"
        }
      ],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "fullmatch", "pattern", "no-match", "overlap-tail", "bytes", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abcccd` with bytes payloads so the scorecard stays explicit that an overlapping branch tail still cannot satisfy the trailing `d` on the bytes path."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",
      "operation": "compile",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_named_compile_metadata",
      "pattern": "a(?P<word>(bc|b)c){1,}d",
      "text_model": "bytes",
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "compile", "metadata", "bytes", "gap"],
      "notes": [
        "Mirrors the named compile frontier for the same bounded open-ended `{1,}` grouped backtracking-heavy slice with bytes payloads while keeping the visible `word` capture explicit."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-lower-bound-long-branch-bytes",
      "operation": "module_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_named_module_lower_bound_long_branch_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a(?P<word>(bc|b)c){1,}d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzabccdzz"
        }
      ],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "search", "module", "lower-bound", "long-branch", "bytes", "gap"],
      "notes": [
        "Documents the named lower-bound success path on `abccd` with bytes payloads so the visible `word` capture stays explicit when the longer overlapping branch wins on the bytes surface too."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-long-then-short-bytes",
      "operation": "module_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_named_module_second_repetition_long_then_short_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a(?P<word>(bc|b)c){1,}d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzabccbcdzz"
        }
      ],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "search", "module", "second-repetition", "long-then-short", "bytes", "gap"],
      "notes": [
        "Documents the named mixed-order second-repetition success path on `abccbcd` with bytes payloads so the visible final capture after backtracking stays explicit on the bytes publication path."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-third-repetition-mixed-bytes",
      "operation": "module_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_named_module_third_repetition_mixed_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a(?P<word>(bc|b)c){1,}d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzabcbccbcdzz"
        }
      ],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "search", "module", "third-repetition", "mixed", "bytes", "gap"],
      "notes": [
        "Documents the named module-level third-repetition success path on `abcbccbcd` with bytes payloads so the open-ended mixed-branch workflow stays visible on the bytes publication path too."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-fourth-repetition-short-only-bytes",
      "operation": "pattern_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_named_pattern_fourth_repetition_short_only_workflow",
      "pattern": "a(?P<word>(bc|b)c){1,}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcbcbcbcd"
        }
      ],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "fullmatch", "pattern", "fourth-repetition", "short-only", "bytes", "gap"],
      "notes": [
        "Documents the named compiled-pattern success path on `abcbcbcbcd` with bytes payloads so the bounded fourth-repetition workflow stays published for bytes too."
      ]
    },
    {
      "id": "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-no-match-invalid-tail-bytes",
      "operation": "module_call",
      "family": "open_ended_quantified_group_alternation_backtracking_heavy_named_module_no_match_invalid_tail_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a(?P<word>(bc|b)c){1,}d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzabccbdzz"
        }
      ],
      "categories": ["grouped", "alternation", "overlapping-branches", "quantifier", "open-ended-repeat", "counted-repeat", "named-group", "search", "module", "no-match", "invalid-tail", "bytes", "gap"],
      "notes": [
        "Documents the named no-match search path on `abccbd` with bytes payloads so the scorecard records the failing tail choice on the bytes publication path too."
      ]
    }
  ]
}
