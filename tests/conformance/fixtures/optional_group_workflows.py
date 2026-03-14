MANIFEST = {
  "schema_version": 1,
  "manifest_id": "optional-group-workflows",
  "layer": "match_behavior",
  "suite_id": "match.optional_group",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "optional-group-compile-metadata-str",
      "operation": "compile",
      "family": "optional_group_compile_metadata",
      "pattern": "a(b)?d",
      "categories": ["grouped", "optional-group", "quantifier", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the bounded optional-group compile frontier for one numbered capture made optional with a single trailing question-mark quantifier inside literal prefix and suffix text."
      ]
    },
    {
      "id": "optional-group-module-search-present-str",
      "operation": "module_call",
      "family": "optional_group_module_present_workflow",
      "helper": "search",
      "args": ["a(b)?d", "zzabdzz"],
      "categories": ["grouped", "optional-group", "quantifier", "search", "module", "present", "str", "gap"],
      "notes": [
        "Documents the module-level numbered optional-group search path when the optional capture is present and contributes a visible group value."
      ]
    },
    {
      "id": "optional-group-pattern-fullmatch-absent-str",
      "operation": "pattern_call",
      "family": "optional_group_pattern_absent_workflow",
      "pattern": "a(b)?d",
      "helper": "fullmatch",
      "args": ["ad"],
      "categories": ["grouped", "optional-group", "quantifier", "fullmatch", "pattern", "absent", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch numbered optional-group path when the capture is omitted so the scorecard records the observable None-valued group outcome."
      ]
    },
    {
      "id": "named-optional-group-compile-metadata-str",
      "operation": "compile",
      "family": "named_optional_group_compile_metadata",
      "pattern": "a(?P<word>b)?d",
      "categories": ["grouped", "optional-group", "quantifier", "named-group", "compile", "metadata", "str", "gap"],
      "notes": [
        "Publishes the matching named optional-group compile frontier for one named capture made optional with the same bounded question-mark quantifier shape."
      ]
    },
    {
      "id": "named-optional-group-module-search-absent-str",
      "operation": "module_call",
      "family": "named_optional_group_module_absent_workflow",
      "helper": "search",
      "args": ["a(?P<word>b)?d", "zzadzz"],
      "categories": ["grouped", "optional-group", "quantifier", "named-group", "search", "module", "absent", "str", "gap"],
      "notes": [
        "Documents the module-level named optional-group search path when the capture is omitted so the named-group None payload remains explicit in the published gap."
      ]
    },
    {
      "id": "named-optional-group-pattern-fullmatch-present-str",
      "operation": "pattern_call",
      "family": "named_optional_group_pattern_present_workflow",
      "pattern": "a(?P<word>b)?d",
      "helper": "fullmatch",
      "args": ["abd"],
      "categories": ["grouped", "optional-group", "quantifier", "named-group", "fullmatch", "pattern", "present", "str", "gap"],
      "notes": [
        "Documents the bound Pattern.fullmatch named optional-group path when the capture is present without broadening into counted repeats, quantified alternation, replacement semantics, or conditionals."
      ]
    },
    {
      "id": "systematic-optional-group-numbered-compile-metadata-str",
      "family": "systematic_optional_group_numbered_compile_metadata",
      "operation": "compile",
      "notes": [
        "Covers the landed optional-group capture slice across numbered and named compile, module, and Pattern observations so capture behavior does not rely only on hand-written fixtures.",
        "Uses the bounded numbered optional-group slice that already passes through the Rust boundary.",
        "Publishes the compile metadata observation for the optional-group slice."
      ],
      "categories": [
        "systematic",
        "grouped",
        "optional-group",
        "capture-oriented",
        "landed-slice",
        "numbered-capture",
        "compile",
        "metadata"
      ],
      "text_model": "str",
      "pattern": "a(b)?d"
    },
    {
      "id": "systematic-optional-group-numbered-module-search-present-str",
      "family": "systematic_optional_group_numbered_module_present_workflow",
      "operation": "module_call",
      "notes": [
        "Covers the landed optional-group capture slice across numbered and named compile, module, and Pattern observations so capture behavior does not rely only on hand-written fixtures.",
        "Uses the bounded numbered optional-group slice that already passes through the Rust boundary.",
        "Exercises the module-level path where the optional capture participates in the match."
      ],
      "categories": [
        "systematic",
        "grouped",
        "optional-group",
        "capture-oriented",
        "landed-slice",
        "numbered-capture",
        "module",
        "search",
        "present"
      ],
      "text_model": "str",
      "helper": "search",
      "args": [
        "a(b)?d",
        "zzabdzz"
      ]
    },
    {
      "id": "systematic-optional-group-numbered-module-search-absent-str",
      "family": "systematic_optional_group_numbered_module_absent_workflow",
      "operation": "module_call",
      "notes": [
        "Covers the landed optional-group capture slice across numbered and named compile, module, and Pattern observations so capture behavior does not rely only on hand-written fixtures.",
        "Uses the bounded numbered optional-group slice that already passes through the Rust boundary.",
        "Exercises the module-level path where the optional capture is skipped and the observed group payload must stay aligned with CPython."
      ],
      "categories": [
        "systematic",
        "grouped",
        "optional-group",
        "capture-oriented",
        "landed-slice",
        "numbered-capture",
        "module",
        "search",
        "absent"
      ],
      "text_model": "str",
      "helper": "search",
      "args": [
        "a(b)?d",
        "zzadzz"
      ]
    },
    {
      "id": "systematic-optional-group-numbered-pattern-fullmatch-present-str",
      "family": "systematic_optional_group_numbered_pattern_present_workflow",
      "operation": "pattern_call",
      "notes": [
        "Covers the landed optional-group capture slice across numbered and named compile, module, and Pattern observations so capture behavior does not rely only on hand-written fixtures.",
        "Uses the bounded numbered optional-group slice that already passes through the Rust boundary.",
        "Exercises the compiled Pattern path where the optional capture is present."
      ],
      "categories": [
        "systematic",
        "grouped",
        "optional-group",
        "capture-oriented",
        "landed-slice",
        "numbered-capture",
        "pattern",
        "fullmatch",
        "present"
      ],
      "text_model": "str",
      "helper": "fullmatch",
      "pattern": "a(b)?d",
      "args": [
        "abd"
      ]
    },
    {
      "id": "systematic-optional-group-numbered-pattern-fullmatch-absent-str",
      "family": "systematic_optional_group_numbered_pattern_absent_workflow",
      "operation": "pattern_call",
      "notes": [
        "Covers the landed optional-group capture slice across numbered and named compile, module, and Pattern observations so capture behavior does not rely only on hand-written fixtures.",
        "Uses the bounded numbered optional-group slice that already passes through the Rust boundary.",
        "Exercises the compiled Pattern path where the optional capture is omitted."
      ],
      "categories": [
        "systematic",
        "grouped",
        "optional-group",
        "capture-oriented",
        "landed-slice",
        "numbered-capture",
        "pattern",
        "fullmatch",
        "absent"
      ],
      "text_model": "str",
      "helper": "fullmatch",
      "pattern": "a(b)?d",
      "args": [
        "ad"
      ]
    },
    {
      "id": "systematic-optional-group-named-compile-metadata-str",
      "family": "systematic_optional_group_named_compile_metadata",
      "operation": "compile",
      "notes": [
        "Covers the landed optional-group capture slice across numbered and named compile, module, and Pattern observations so capture behavior does not rely only on hand-written fixtures.",
        "Uses the matching named optional-group slice so the corpus covers both capture addressing modes.",
        "Publishes the compile metadata observation for the optional-group slice."
      ],
      "categories": [
        "systematic",
        "grouped",
        "optional-group",
        "capture-oriented",
        "landed-slice",
        "named-group",
        "compile",
        "metadata"
      ],
      "text_model": "str",
      "pattern": "a(?P<word>b)?d"
    },
    {
      "id": "systematic-optional-group-named-module-search-present-str",
      "family": "systematic_optional_group_named_module_present_workflow",
      "operation": "module_call",
      "notes": [
        "Covers the landed optional-group capture slice across numbered and named compile, module, and Pattern observations so capture behavior does not rely only on hand-written fixtures.",
        "Uses the matching named optional-group slice so the corpus covers both capture addressing modes.",
        "Exercises the module-level path where the optional capture participates in the match."
      ],
      "categories": [
        "systematic",
        "grouped",
        "optional-group",
        "capture-oriented",
        "landed-slice",
        "named-group",
        "module",
        "search",
        "present"
      ],
      "text_model": "str",
      "helper": "search",
      "args": [
        "a(?P<word>b)?d",
        "zzabdzz"
      ]
    },
    {
      "id": "systematic-optional-group-named-module-search-absent-str",
      "family": "systematic_optional_group_named_module_absent_workflow",
      "operation": "module_call",
      "notes": [
        "Covers the landed optional-group capture slice across numbered and named compile, module, and Pattern observations so capture behavior does not rely only on hand-written fixtures.",
        "Uses the matching named optional-group slice so the corpus covers both capture addressing modes.",
        "Exercises the module-level path where the optional capture is skipped and the observed group payload must stay aligned with CPython."
      ],
      "categories": [
        "systematic",
        "grouped",
        "optional-group",
        "capture-oriented",
        "landed-slice",
        "named-group",
        "module",
        "search",
        "absent"
      ],
      "text_model": "str",
      "helper": "search",
      "args": [
        "a(?P<word>b)?d",
        "zzadzz"
      ]
    },
    {
      "id": "systematic-optional-group-named-pattern-fullmatch-present-str",
      "family": "systematic_optional_group_named_pattern_present_workflow",
      "operation": "pattern_call",
      "notes": [
        "Covers the landed optional-group capture slice across numbered and named compile, module, and Pattern observations so capture behavior does not rely only on hand-written fixtures.",
        "Uses the matching named optional-group slice so the corpus covers both capture addressing modes.",
        "Exercises the compiled Pattern path where the optional capture is present."
      ],
      "categories": [
        "systematic",
        "grouped",
        "optional-group",
        "capture-oriented",
        "landed-slice",
        "named-group",
        "pattern",
        "fullmatch",
        "present"
      ],
      "text_model": "str",
      "helper": "fullmatch",
      "pattern": "a(?P<word>b)?d",
      "args": [
        "abd"
      ]
    },
    {
      "id": "systematic-optional-group-named-pattern-fullmatch-absent-str",
      "family": "systematic_optional_group_named_pattern_absent_workflow",
      "operation": "pattern_call",
      "notes": [
        "Covers the landed optional-group capture slice across numbered and named compile, module, and Pattern observations so capture behavior does not rely only on hand-written fixtures.",
        "Uses the matching named optional-group slice so the corpus covers both capture addressing modes.",
        "Exercises the compiled Pattern path where the optional capture is omitted."
      ],
      "categories": [
        "systematic",
        "grouped",
        "optional-group",
        "capture-oriented",
        "landed-slice",
        "named-group",
        "pattern",
        "fullmatch",
        "absent"
      ],
      "text_model": "str",
      "helper": "fullmatch",
      "pattern": "a(?P<word>b)?d",
      "args": [
        "ad"
      ]
    }
  ]
}
