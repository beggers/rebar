MANIFEST = {
  "schema_version": 1,
  "manifest_id": "quantified-alternation-open-ended-workflows",
  "layer": "match_behavior",
  "suite_id": "match.quantified_alternation_open_ended",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "quantified-alternation-open-ended-numbered-compile-metadata-str",
      "operation": "compile",
      "family": "quantified_alternation_open_ended_numbered_compile_metadata",
      "pattern": "a(b|c){1,}d",
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the numbered compile frontier for one exact open-ended `{1,}` quantified alternation without widening into nested alternation, branch-local backreferences, conditionals, replacement workflows, or broader overlapping-branch backtracking."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-numbered-module-search-lower-bound-b-str",
      "operation": "module_call",
      "family": "quantified_alternation_open_ended_numbered_module_lower_bound_b_workflow",
      "helper": "search",
      "args": ["a(b|c){1,}d", "zzabdzz"],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "search", "module", "lower-bound", "b-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound module success path on `abd` so the first open-ended follow-on keeps the one-repetition `b` branch explicit."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-numbered-module-search-lower-bound-c-str",
      "operation": "module_call",
      "family": "quantified_alternation_open_ended_numbered_module_lower_bound_c_workflow",
      "helper": "search",
      "args": ["a(b|c){1,}d", "zzacdzz"],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "search", "module", "lower-bound", "c-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound module success path on `acd` so the alternate lower-bound branch stays visible at the exact `{1,}` frontier."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-numbered-pattern-fullmatch-second-repetition-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_numbered_pattern_second_repetition_workflow",
      "pattern": "a(b|c){1,}d",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "fullmatch", "pattern", "second-repetition", "str", "gap"],
      "notes": [
        "Documents the numbered Pattern.fullmatch success path on `abcd` so the scorecard keeps one bounded longer success beyond the lower bound explicit."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-numbered-pattern-fullmatch-third-repetition-bcc-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_numbered_pattern_third_repetition_bcc_workflow",
      "pattern": "a(b|c){1,}d",
      "helper": "fullmatch",
      "args": ["abccd"],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "fullmatch", "pattern", "third-repetition", "bcc", "str", "gap"],
      "notes": [
        "Documents the numbered Pattern.fullmatch success path on `abccd` so the open-ended slice records one bounded third-repetition case that ends on `c`."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-numbered-pattern-fullmatch-fourth-repetition-bcbc-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_numbered_pattern_fourth_repetition_bcbc_workflow",
      "pattern": "a(b|c){1,}d",
      "helper": "fullmatch",
      "args": ["abcbcd"],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "fullmatch", "pattern", "fourth-repetition", "bcbc", "str", "gap"],
      "notes": [
        "Documents the numbered Pattern.fullmatch success path on `abcbcd` so the exact `{1,}` slice shows one bounded fourth-repetition mixed-branch workflow without pretending to exhaust arbitrary-length repetition."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-numbered-pattern-fullmatch-no-match-below-lower-bound-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_numbered_pattern_no_match_below_lower_bound_workflow",
      "pattern": "a(b|c){1,}d",
      "helper": "fullmatch",
      "args": ["ad"],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "fullmatch", "pattern", "no-match", "below-lower-bound", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `ad` so the scorecard stays explicit that the open-ended form still enforces the one-repetition lower bound."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-numbered-pattern-fullmatch-no-match-invalid-branch-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_numbered_pattern_no_match_invalid_branch_workflow",
      "pattern": "a(b|c){1,}d",
      "helper": "fullmatch",
      "args": ["abed"],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "fullmatch", "pattern", "no-match", "invalid-branch", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abed` so the open-ended slice records that the repeated site still rejects non-`b|c` branch text."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-named-compile-metadata-str",
      "operation": "compile",
      "family": "quantified_alternation_open_ended_named_compile_metadata",
      "pattern": "a(?P<word>b|c){1,}d",
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the named compile frontier for the same exact open-ended `{1,}` quantified alternation under one visible `word` capture."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-named-module-search-lower-bound-b-str",
      "operation": "module_call",
      "family": "quantified_alternation_open_ended_named_module_lower_bound_b_workflow",
      "helper": "search",
      "args": ["a(?P<word>b|c){1,}d", "zzabdzz"],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "named-group", "search", "module", "lower-bound", "b-branch", "str", "gap"],
      "notes": [
        "Documents the named lower-bound module success path on `abd` so the visible `word` capture stays explicit at the first open-ended frontier."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-named-module-search-lower-bound-c-str",
      "operation": "module_call",
      "family": "quantified_alternation_open_ended_named_module_lower_bound_c_workflow",
      "helper": "search",
      "args": ["a(?P<word>b|c){1,}d", "zzacdzz"],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "named-group", "search", "module", "lower-bound", "c-branch", "str", "gap"],
      "notes": [
        "Documents the named lower-bound module success path on `acd` so the alternate lower-bound branch remains explicit under the visible `word` capture."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-named-pattern-fullmatch-second-repetition-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_named_pattern_second_repetition_workflow",
      "pattern": "a(?P<word>b|c){1,}d",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "named-group", "fullmatch", "pattern", "second-repetition", "str", "gap"],
      "notes": [
        "Documents the named Pattern.fullmatch success path on `abcd` so one bounded longer success beyond the lower bound stays explicit under the named capture."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-named-pattern-fullmatch-third-repetition-bcc-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_named_pattern_third_repetition_bcc_workflow",
      "pattern": "a(?P<word>b|c){1,}d",
      "helper": "fullmatch",
      "args": ["abccd"],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "named-group", "fullmatch", "pattern", "third-repetition", "bcc", "str", "gap"],
      "notes": [
        "Documents the named Pattern.fullmatch success path on `abccd` so the scorecard records one bounded third-repetition case that ends on `c`."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-named-pattern-fullmatch-fourth-repetition-bcbc-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_named_pattern_fourth_repetition_bcbc_workflow",
      "pattern": "a(?P<word>b|c){1,}d",
      "helper": "fullmatch",
      "args": ["abcbcd"],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "named-group", "fullmatch", "pattern", "fourth-repetition", "bcbc", "str", "gap"],
      "notes": [
        "Documents the named Pattern.fullmatch success path on `abcbcd` so the exact `{1,}` slice includes one bounded fourth-repetition mixed-branch workflow with a visible final named capture."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-named-pattern-fullmatch-no-match-below-lower-bound-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_named_pattern_no_match_below_lower_bound_workflow",
      "pattern": "a(?P<word>b|c){1,}d",
      "helper": "fullmatch",
      "args": ["ad"],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "named-group", "fullmatch", "pattern", "no-match", "below-lower-bound", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `ad` so the open-ended form still enforces the one-repetition lower bound even with a visible named capture."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-named-pattern-fullmatch-no-match-invalid-branch-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_named_pattern_no_match_invalid_branch_workflow",
      "pattern": "a(?P<word>b|c){1,}d",
      "helper": "fullmatch",
      "args": ["abed"],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "named-group", "fullmatch", "pattern", "no-match", "invalid-branch", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `abed` so the repeated alternation site still rejects non-`b|c` text under the visible `word` capture."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-numbered-compile-metadata-bytes",
      "operation": "compile",
      "family": "quantified_alternation_open_ended_numbered_compile_metadata",
      "pattern": "a(b|c){1,}d",
      "text_model": "bytes",
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "compile", "metadata", "bytes", "gap"],
      "notes": [
        "Publishes the numbered compile frontier for the same open-ended `{1,}` quantified alternation with bytes payloads while keeping the bytes parity gap explicit until RBR-0561 lands."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-numbered-module-search-lower-bound-b-bytes",
      "operation": "module_call",
      "family": "quantified_alternation_open_ended_numbered_module_lower_bound_b_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a(b|c){1,}d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzabdzz"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "search", "module", "lower-bound", "b-branch", "bytes", "gap"],
      "notes": [
        "Documents the numbered lower-bound module success path on `abd` with bytes payloads so the first open-ended bytes follow-on keeps the one-repetition `b` branch explicit."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-numbered-module-search-lower-bound-c-bytes",
      "operation": "module_call",
      "family": "quantified_alternation_open_ended_numbered_module_lower_bound_c_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a(b|c){1,}d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzacdzz"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "search", "module", "lower-bound", "c-branch", "bytes", "gap"],
      "notes": [
        "Documents the numbered lower-bound module success path on `acd` with bytes payloads so the alternate lower-bound branch stays visible at the exact `{1,}` bytes frontier."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-numbered-pattern-fullmatch-second-repetition-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_numbered_pattern_second_repetition_workflow",
      "pattern": "a(b|c){1,}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcd"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "fullmatch", "pattern", "second-repetition", "bytes", "gap"],
      "notes": [
        "Documents the numbered Pattern.fullmatch success path on `abcd` with bytes payloads so the scorecard keeps one bounded longer bytes success beyond the lower bound explicit."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-numbered-pattern-fullmatch-third-repetition-bcc-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_numbered_pattern_third_repetition_bcc_workflow",
      "pattern": "a(b|c){1,}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abccd"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "fullmatch", "pattern", "third-repetition", "bcc", "bytes", "gap"],
      "notes": [
        "Documents the numbered Pattern.fullmatch success path on `abccd` with bytes payloads so the open-ended slice records one bounded third-repetition bytes case that ends on `c`."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-numbered-pattern-fullmatch-fourth-repetition-bcbc-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_numbered_pattern_fourth_repetition_bcbc_workflow",
      "pattern": "a(b|c){1,}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcbcd"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "fullmatch", "pattern", "fourth-repetition", "bcbc", "bytes", "gap"],
      "notes": [
        "Documents the numbered Pattern.fullmatch success path on `abcbcd` with bytes payloads so the exact `{1,}` bytes slice shows one bounded fourth-repetition mixed-branch workflow."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-numbered-pattern-fullmatch-no-match-below-lower-bound-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_numbered_pattern_no_match_below_lower_bound_workflow",
      "pattern": "a(b|c){1,}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "ad"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "fullmatch", "pattern", "no-match", "below-lower-bound", "bytes", "gap"],
      "notes": [
        "Documents the numbered no-match path on `ad` with bytes payloads so the bytes publication stays explicit that the open-ended form still enforces the one-repetition lower bound."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-numbered-pattern-fullmatch-no-match-invalid-branch-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_numbered_pattern_no_match_invalid_branch_workflow",
      "pattern": "a(b|c){1,}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abed"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "fullmatch", "pattern", "no-match", "invalid-branch", "bytes", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abed` with bytes payloads so the repeated site still rejects non-`b|c` branch text on the bytes frontier."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-named-compile-metadata-bytes",
      "operation": "compile",
      "family": "quantified_alternation_open_ended_named_compile_metadata",
      "pattern": "a(?P<word>b|c){1,}d",
      "text_model": "bytes",
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "named-group", "compile", "metadata", "bytes", "gap"],
      "notes": [
        "Publishes the named compile frontier for the same exact open-ended `{1,}` quantified alternation with bytes payloads under one visible `word` capture while keeping the bytes parity gap explicit until RBR-0561 lands."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-named-module-search-lower-bound-b-bytes",
      "operation": "module_call",
      "family": "quantified_alternation_open_ended_named_module_lower_bound_b_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a(?P<word>b|c){1,}d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzabdzz"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "named-group", "search", "module", "lower-bound", "b-branch", "bytes", "gap"],
      "notes": [
        "Documents the named lower-bound module success path on `abd` with bytes payloads so the visible `word` capture stays explicit at the first open-ended bytes frontier."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-named-module-search-lower-bound-c-bytes",
      "operation": "module_call",
      "family": "quantified_alternation_open_ended_named_module_lower_bound_c_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a(?P<word>b|c){1,}d"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzacdzz"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "named-group", "search", "module", "lower-bound", "c-branch", "bytes", "gap"],
      "notes": [
        "Documents the named lower-bound module success path on `acd` with bytes payloads so the alternate lower-bound branch remains explicit under the visible `word` capture on the bytes frontier."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-named-pattern-fullmatch-second-repetition-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_named_pattern_second_repetition_workflow",
      "pattern": "a(?P<word>b|c){1,}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcd"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "named-group", "fullmatch", "pattern", "second-repetition", "bytes", "gap"],
      "notes": [
        "Documents the named Pattern.fullmatch success path on `abcd` with bytes payloads so one bounded longer bytes success beyond the lower bound stays explicit under the named capture."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-named-pattern-fullmatch-third-repetition-bcc-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_named_pattern_third_repetition_bcc_workflow",
      "pattern": "a(?P<word>b|c){1,}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abccd"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "named-group", "fullmatch", "pattern", "third-repetition", "bcc", "bytes", "gap"],
      "notes": [
        "Documents the named Pattern.fullmatch success path on `abccd` with bytes payloads so the scorecard records one bounded third-repetition bytes case that ends on `c`."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-named-pattern-fullmatch-fourth-repetition-bcbc-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_named_pattern_fourth_repetition_bcbc_workflow",
      "pattern": "a(?P<word>b|c){1,}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcbcd"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "named-group", "fullmatch", "pattern", "fourth-repetition", "bcbc", "bytes", "gap"],
      "notes": [
        "Documents the named Pattern.fullmatch success path on `abcbcd` with bytes payloads so the exact `{1,}` bytes slice includes one bounded fourth-repetition mixed-branch workflow with a visible final capture."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-named-pattern-fullmatch-no-match-below-lower-bound-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_named_pattern_no_match_below_lower_bound_workflow",
      "pattern": "a(?P<word>b|c){1,}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "ad"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "named-group", "fullmatch", "pattern", "no-match", "below-lower-bound", "bytes", "gap"],
      "notes": [
        "Documents the named no-match path on `ad` with bytes payloads so the open-ended form still enforces the one-repetition lower bound even with a visible named capture on the bytes frontier."
      ]
    },
    {
      "id": "quantified-alternation-open-ended-named-pattern-fullmatch-no-match-invalid-branch-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_open_ended_named_pattern_no_match_invalid_branch_workflow",
      "pattern": "a(?P<word>b|c){1,}d",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abed"
        }
      ],
      "categories": ["grouped", "alternation", "quantifier", "open-ended-repeat", "named-group", "fullmatch", "pattern", "no-match", "invalid-branch", "bytes", "gap"],
      "notes": [
        "Documents the named no-match path on `abed` with bytes payloads so the repeated alternation site still rejects non-`b|c` text under the visible `word` capture on the bytes frontier."
      ]
    }
  ]
}
