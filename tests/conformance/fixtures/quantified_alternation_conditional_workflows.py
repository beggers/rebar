MANIFEST = {
  "schema_version": 1,
  "manifest_id": "quantified-alternation-conditional-workflows",
  "layer": "match_behavior",
  "suite_id": "match.quantified_alternation_conditional",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "quantified-alternation-conditional-numbered-compile-metadata-str",
      "operation": "compile",
      "family": "quantified_alternation_conditional_numbered_compile_metadata",
      "pattern": "a((b|c){1,2})?(?(1)d|e)",
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the bounded numbered compile frontier for one optional capture around one {1,2} quantified alternation followed by one later group-exists conditional."
      ]
    },
    {
      "id": "quantified-alternation-conditional-numbered-module-search-absent-workflow-str",
      "operation": "module_call",
      "family": "quantified_alternation_conditional_numbered_module_absent_workflow",
      "helper": "search",
      "args": ["a((b|c){1,2})?(?(1)d|e)", "zzaezz"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "search", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the numbered absent-group success path on `ae` so the scorecard records that the else arm still accepts when the optional quantified alternation is skipped entirely."
      ]
    },
    {
      "id": "quantified-alternation-conditional-numbered-module-search-lower-bound-b-workflow-str",
      "operation": "module_call",
      "family": "quantified_alternation_conditional_numbered_module_lower_bound_b_workflow",
      "helper": "search",
      "args": ["a((b|c){1,2})?(?(1)d|e)", "zzabdzz"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "search", "module", "present", "lower-bound", "b-branch", "str", "gap"],
      "notes": [
        "Documents the numbered lower-bound present success path on `abd` so the published frontier shows that one b-branch repetition is enough to force the later yes arm to require `d`."
      ]
    },
    {
      "id": "quantified-alternation-conditional-numbered-pattern-fullmatch-second-repetition-b-workflow-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_conditional_numbered_pattern_second_repetition_b_workflow",
      "pattern": "a((b|c){1,2})?(?(1)d|e)",
      "helper": "fullmatch",
      "args": ["abbd"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "fullmatch", "pattern", "present", "second-repetition", "b-branch", "str", "gap"],
      "notes": [
        "Documents the numbered second-repetition success path on `abbd` so the scorecard captures that two b-branch repetitions still leave the conditional satisfied by the yes arm."
      ]
    },
    {
      "id": "quantified-alternation-conditional-numbered-pattern-fullmatch-second-repetition-mixed-workflow-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_conditional_numbered_pattern_second_repetition_mixed_workflow",
      "pattern": "a((b|c){1,2})?(?(1)d|e)",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "fullmatch", "pattern", "present", "second-repetition", "mixed-branches", "str", "gap"],
      "notes": [
        "Documents the numbered mixed-branch second-repetition success path on `abcd` so the frontier records that the later yes arm still requires `d` after one b-branch plus one c-branch repetition."
      ]
    },
    {
      "id": "quantified-alternation-conditional-numbered-pattern-fullmatch-no-match-workflow-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_conditional_numbered_pattern_no_match_workflow",
      "pattern": "a((b|c){1,2})?(?(1)d|e)",
      "helper": "fullmatch",
      "args": ["abe"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "fullmatch", "pattern", "present", "no-match", "str", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abe` so the scorecard makes it explicit that the conditional yes arm does not accept `e` once the optional quantified alternation participated."
      ]
    },
    {
      "id": "quantified-alternation-conditional-named-compile-metadata-str",
      "operation": "compile",
      "family": "quantified_alternation_conditional_named_compile_metadata",
      "pattern": "a(?P<outer>(b|c){1,2})?(?(outer)d|e)",
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named compile frontier for one optional named capture around one bounded quantified alternation with one later named group-exists conditional."
      ]
    },
    {
      "id": "quantified-alternation-conditional-named-module-search-absent-workflow-str",
      "operation": "module_call",
      "family": "quantified_alternation_conditional_named_module_absent_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(b|c){1,2})?(?(outer)d|e)", "zzaezz"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "named-group", "search", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the named absent-group success path on `ae` so the published frontier records the else-arm acceptance when the optional named quantified alternation is skipped."
      ]
    },
    {
      "id": "quantified-alternation-conditional-named-module-search-lower-bound-c-workflow-str",
      "operation": "module_call",
      "family": "quantified_alternation_conditional_named_module_lower_bound_c_workflow",
      "helper": "search",
      "args": ["a(?P<outer>(b|c){1,2})?(?(outer)d|e)", "zzacdzz"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "named-group", "search", "module", "present", "lower-bound", "c-branch", "str", "gap"],
      "notes": [
        "Documents the named lower-bound present success path on `acd` so the scorecard shows that one c-branch repetition is enough to select the later yes arm."
      ]
    },
    {
      "id": "quantified-alternation-conditional-named-pattern-fullmatch-second-repetition-c-workflow-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_conditional_named_pattern_second_repetition_c_workflow",
      "pattern": "a(?P<outer>(b|c){1,2})?(?(outer)d|e)",
      "helper": "fullmatch",
      "args": ["accd"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "named-group", "fullmatch", "pattern", "present", "second-repetition", "c-branch", "str", "gap"],
      "notes": [
        "Documents the named second-repetition success path on `accd` so the frontier captures the final named outer capture after two c-branch repetitions before the conditional yes arm consumes `d`."
      ]
    },
    {
      "id": "quantified-alternation-conditional-named-pattern-fullmatch-second-repetition-mixed-workflow-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_conditional_named_pattern_second_repetition_mixed_workflow",
      "pattern": "a(?P<outer>(b|c){1,2})?(?(outer)d|e)",
      "helper": "fullmatch",
      "args": ["abcd"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "named-group", "fullmatch", "pattern", "present", "second-repetition", "mixed-branches", "str", "gap"],
      "notes": [
        "Documents the named mixed-branch second-repetition success path on `abcd` so the published frontier shows that the visible named outer capture still reflects the final bounded alternation span before the yes arm matches."
      ]
    },
    {
      "id": "quantified-alternation-conditional-named-pattern-fullmatch-no-match-workflow-str",
      "operation": "pattern_call",
      "family": "quantified_alternation_conditional_named_pattern_no_match_workflow",
      "pattern": "a(?P<outer>(b|c){1,2})?(?(outer)d|e)",
      "helper": "fullmatch",
      "args": ["acce"],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "named-group", "fullmatch", "pattern", "present", "no-match", "str", "gap"],
      "notes": [
        "Documents the named no-match path on `acce` so the scorecard stays explicit that the named conditional yes arm still rejects `e` after the optional quantified alternation participated."
      ]
    },
    {
      "id": "quantified-alternation-conditional-numbered-compile-metadata-bytes",
      "operation": "compile",
      "family": "quantified_alternation_conditional_numbered_compile_metadata",
      "pattern": "a((b|c){1,2})?(?(1)d|e)",
      "text_model": "bytes",
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "compile", "metadata", "bytes", "gap"],
      "notes": [
        "Publishes the bounded numbered compile frontier for the same optional quantified alternation plus later group-exists conditional with bytes payloads while keeping the bytes parity gap explicit."
      ]
    },
    {
      "id": "quantified-alternation-conditional-numbered-module-search-absent-workflow-bytes",
      "operation": "module_call",
      "family": "quantified_alternation_conditional_numbered_module_absent_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a((b|c){1,2})?(?(1)d|e)"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzaezz"
        }
      ],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "search", "module", "absent", "bytes", "gap"],
      "notes": [
        "Documents the numbered absent-group success path on `ae` with bytes payloads so the published bytes frontier keeps the else-arm acceptance visible when the optional quantified alternation is skipped."
      ]
    },
    {
      "id": "quantified-alternation-conditional-numbered-module-search-lower-bound-b-workflow-bytes",
      "operation": "module_call",
      "family": "quantified_alternation_conditional_numbered_module_lower_bound_b_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a((b|c){1,2})?(?(1)d|e)"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzabdzz"
        }
      ],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "search", "module", "present", "lower-bound", "b-branch", "bytes", "gap"],
      "notes": [
        "Documents the numbered lower-bound present success path on `abd` with bytes payloads so the published bytes frontier shows that one b-branch repetition is enough to force the yes arm to require `d`."
      ]
    },
    {
      "id": "quantified-alternation-conditional-numbered-pattern-fullmatch-second-repetition-b-workflow-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_conditional_numbered_pattern_second_repetition_b_workflow",
      "pattern": "a((b|c){1,2})?(?(1)d|e)",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abbd"
        }
      ],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "fullmatch", "pattern", "present", "second-repetition", "b-branch", "bytes", "gap"],
      "notes": [
        "Documents the numbered second-repetition success path on `abbd` with bytes payloads so the scorecard captures that two b-branch repetitions still leave the conditional satisfied by the yes arm."
      ]
    },
    {
      "id": "quantified-alternation-conditional-numbered-pattern-fullmatch-second-repetition-mixed-workflow-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_conditional_numbered_pattern_second_repetition_mixed_workflow",
      "pattern": "a((b|c){1,2})?(?(1)d|e)",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcd"
        }
      ],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "fullmatch", "pattern", "present", "second-repetition", "mixed-branches", "bytes", "gap"],
      "notes": [
        "Documents the numbered mixed-branch second-repetition success path on `abcd` with bytes payloads so the published frontier records that the later yes arm still requires `d` after one b-branch plus one c-branch repetition."
      ]
    },
    {
      "id": "quantified-alternation-conditional-numbered-pattern-fullmatch-no-match-workflow-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_conditional_numbered_pattern_no_match_workflow",
      "pattern": "a((b|c){1,2})?(?(1)d|e)",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abe"
        }
      ],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "fullmatch", "pattern", "present", "no-match", "bytes", "gap"],
      "notes": [
        "Documents the numbered no-match path on `abe` with bytes payloads so the scorecard stays explicit that the conditional yes arm does not accept `e` once the optional quantified alternation participated."
      ]
    },
    {
      "id": "quantified-alternation-conditional-named-compile-metadata-bytes",
      "operation": "compile",
      "family": "quantified_alternation_conditional_named_compile_metadata",
      "pattern": "a(?P<outer>(b|c){1,2})?(?(outer)d|e)",
      "text_model": "bytes",
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "named-group", "compile", "metadata", "bytes", "gap"],
      "notes": [
        "Publishes the matching named compile frontier for the same optional named quantified alternation plus later named conditional with bytes payloads while keeping the bytes parity gap explicit."
      ]
    },
    {
      "id": "quantified-alternation-conditional-named-module-search-absent-workflow-bytes",
      "operation": "module_call",
      "family": "quantified_alternation_conditional_named_module_absent_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a(?P<outer>(b|c){1,2})?(?(outer)d|e)"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzaezz"
        }
      ],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "named-group", "search", "module", "absent", "bytes", "gap"],
      "notes": [
        "Documents the named absent-group success path on `ae` with bytes payloads so the published bytes frontier records the else-arm acceptance when the optional named quantified alternation is skipped."
      ]
    },
    {
      "id": "quantified-alternation-conditional-named-module-search-lower-bound-c-workflow-bytes",
      "operation": "module_call",
      "family": "quantified_alternation_conditional_named_module_lower_bound_c_workflow",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a(?P<outer>(b|c){1,2})?(?(outer)d|e)"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzacdzz"
        }
      ],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "named-group", "search", "module", "present", "lower-bound", "c-branch", "bytes", "gap"],
      "notes": [
        "Documents the named lower-bound present success path on `acd` with bytes payloads so the published bytes frontier shows that one c-branch repetition is enough to select the later yes arm."
      ]
    },
    {
      "id": "quantified-alternation-conditional-named-pattern-fullmatch-second-repetition-c-workflow-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_conditional_named_pattern_second_repetition_c_workflow",
      "pattern": "a(?P<outer>(b|c){1,2})?(?(outer)d|e)",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "accd"
        }
      ],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "named-group", "fullmatch", "pattern", "present", "second-repetition", "c-branch", "bytes", "gap"],
      "notes": [
        "Documents the named second-repetition success path on `accd` with bytes payloads so the frontier captures the final named outer capture after two c-branch repetitions before the conditional yes arm consumes `d`."
      ]
    },
    {
      "id": "quantified-alternation-conditional-named-pattern-fullmatch-second-repetition-mixed-workflow-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_conditional_named_pattern_second_repetition_mixed_workflow",
      "pattern": "a(?P<outer>(b|c){1,2})?(?(outer)d|e)",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcd"
        }
      ],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "named-group", "fullmatch", "pattern", "present", "second-repetition", "mixed-branches", "bytes", "gap"],
      "notes": [
        "Documents the named mixed-branch second-repetition success path on `abcd` with bytes payloads so the published frontier shows that the visible named outer capture still reflects the final bounded alternation span before the yes arm matches."
      ]
    },
    {
      "id": "quantified-alternation-conditional-named-pattern-fullmatch-no-match-workflow-bytes",
      "operation": "pattern_call",
      "family": "quantified_alternation_conditional_named_pattern_no_match_workflow",
      "pattern": "a(?P<outer>(b|c){1,2})?(?(outer)d|e)",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "acce"
        }
      ],
      "categories": ["grouped", "alternation", "quantified", "bounded-repeat", "conditional", "group-exists", "optional-group", "named-group", "fullmatch", "pattern", "present", "no-match", "bytes", "gap"],
      "notes": [
        "Documents the named no-match path on `acce` with bytes payloads so the scorecard stays explicit that the named conditional yes arm still rejects `e` after the optional quantified alternation participated."
      ]
    }
  ]
}
