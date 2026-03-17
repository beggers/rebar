MANIFEST = {
  "schema_version": 1,
  "manifest_id": "quantified-alternation-workflows",
  "layer": "match_behavior",
  "suite_id": "match.quantified_alternation",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "quantified-alternation-numbered-compile-metadata-str",
      "operation": "compile",
      "family": "quantified_alternation_numbered_compile_metadata",
      "pattern": "a(b|c){1,2}d",
      "categories": ["grouped", "alternation", "quantifier", "bounded-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes one bounded numbered quantified-alternation compile slice for a single literal alternation site repeated across the exact {1,2} envelope between literal prefix and suffix text."
      ]
    },
    {
      "id": "quantified-alternation-numbered-module-search-lower-bound-str",
      "operation": "module_call",
      "family": "quantified_alternation_numbered_module_search_lower_bound_workflow",
      "helper": "search",
      "args": ["a(b|c){1,2}d", "zzacdz"],
      "categories": ["grouped", "alternation", "quantifier", "bounded-repeat", "search", "module", "lower-bound", "str", "gap"],
      "notes": [
        "Documents the module-level numbered quantified-alternation search path at the lower bound so the scorecard records the visible final capture value after a single alternation repetition completes."
      ]
    },
    {
      "id": "quantified-alternation-numbered-pattern-fullmatch-second-repetition-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_numbered_pattern_fullmatch_second_repetition_workflow",
      "pattern": "a(b|c){1,2}d",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "alternation", "quantifier", "bounded-repeat", "fullmatch", "pattern", "second-repetition", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch numbered quantified-alternation path at the second repetition so the published gap exposes the final capture value from the last repeated branch."
      ]
    },
    {
      "id": "quantified-alternation-named-compile-metadata-str",
      "operation": "compile",
      "family": "quantified_alternation_named_compile_metadata",
      "pattern": "a(?P<word>b|c){1,2}d",
      "categories": ["grouped", "alternation", "quantifier", "bounded-repeat", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named quantified-alternation compile slice for the same exact {1,2} frontier without broadening into wider envelopes or broader backtracking."
      ]
    },
    {
      "id": "quantified-alternation-named-module-search-second-repetition-str",
      "operation": "module_call",
      "family": "quantified_alternation_named_module_search_second_repetition_workflow",
      "helper": "search",
      "args": ["a(?P<word>b|c){1,2}d", "zzacbdzz"],
      "categories": ["grouped", "alternation", "quantifier", "bounded-repeat", "named-group", "search", "module", "second-repetition", "str", "gap"],
      "notes": [
        "Documents the module-level named quantified-alternation search path at the second repetition so the scorecard records the final named capture exposed after the repeated alternation finishes."
      ]
    },
    {
      "id": "quantified-alternation-named-pattern-fullmatch-lower-bound-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_named_pattern_fullmatch_lower_bound_workflow",
      "pattern": "a(?P<word>b|c){1,2}d",
      "helper": "fullmatch",
      "args": ["abd"],
      "categories": ["grouped", "alternation", "quantifier", "bounded-repeat", "named-group", "fullmatch", "pattern", "lower-bound", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch named quantified-alternation path at the lower bound while leaving wider counted ranges, replacement semantics, branch-local backreferences, conditionals, and broader backtracking out of scope."
      ]
    },
    {
      "id": "quantified-alternation-numbered-compile-metadata-bytes",
      "operation": "compile",
      "family": "quantified_alternation_numbered_compile_metadata",
      "pattern": "a(b|c){1,2}d",
      "text_model": "bytes",
      "categories": ["grouped", "alternation", "quantifier", "bounded-repeat", "compile", "metadata", "bytes", "gap"],
      "notes": [
        "Publishes the same bounded numbered quantified-alternation compile slice for bytes payloads while keeping the bytes parity gap explicit until the follow-on bytes parity task lands."
      ]
    },
    {
      "id": "quantified-alternation-numbered-module-search-lower-bound-bytes",
      "operation": "module_call",
      "family": "quantified_alternation_numbered_module_search_lower_bound_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a(b|c){1,2}d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzacdz"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "bounded-repeat", "search", "module", "lower-bound", "bytes", "gap"],
      "notes": [
        "Documents the module-level numbered quantified-alternation search path at the lower bound with bytes payloads so the scorecard keeps the final capture from one visible `c` repetition explicit on the bytes frontier."
      ]
    },
    {
      "id": "quantified-alternation-numbered-pattern-fullmatch-second-repetition-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_numbered_pattern_fullmatch_second_repetition_workflow",
      "pattern": "a(b|c){1,2}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcd"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "bounded-repeat", "fullmatch", "pattern", "second-repetition", "bytes", "gap"],
      "notes": [
        "Documents the bounded Pattern.fullmatch numbered quantified-alternation path at the second repetition with bytes payloads so the published bytes gap exposes the final capture value from the last repeated branch."
      ]
    },
    {
      "id": "quantified-alternation-named-compile-metadata-bytes",
      "operation": "compile",
      "family": "quantified_alternation_named_compile_metadata",
      "pattern": "a(?P<word>b|c){1,2}d",
      "text_model": "bytes",
      "categories": ["grouped", "alternation", "quantifier", "bounded-repeat", "named-group", "compile", "metadata", "bytes", "gap"],
      "notes": [
        "Publishes the matching named quantified-alternation compile slice for the same exact `{1,2}` frontier with bytes payloads under one visible `word` capture while keeping the bytes parity gap explicit."
      ]
    },
    {
      "id": "quantified-alternation-named-module-search-second-repetition-bytes",
      "operation": "module_call",
      "family": "quantified_alternation_named_module_search_second_repetition_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a(?P<word>b|c){1,2}d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzacbdzz"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "bounded-repeat", "named-group", "search", "module", "second-repetition", "bytes", "gap"],
      "notes": [
        "Documents the module-level named quantified-alternation search path at the second repetition with bytes payloads so the scorecard records the final named capture exposed after the repeated alternation finishes on the bytes frontier."
      ]
    },
    {
      "id": "quantified-alternation-named-pattern-fullmatch-lower-bound-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_named_pattern_fullmatch_lower_bound_workflow",
      "pattern": "a(?P<word>b|c){1,2}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abd"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "bounded-repeat", "named-group", "fullmatch", "pattern", "lower-bound", "bytes", "gap"],
      "notes": [
        "Documents the bounded Pattern.fullmatch named quantified-alternation path at the lower bound with bytes payloads while leaving bytes parity, wider counted ranges, replacement semantics, branch-local backreferences, conditionals, and broader backtracking out of scope."
      ]
    }
  ]
}
