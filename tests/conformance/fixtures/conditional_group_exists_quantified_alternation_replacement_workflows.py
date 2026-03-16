MANIFEST = {
  "schema_version": 1,
  "manifest_id": "conditional-group-exists-quantified-alternation-replacement-workflows",
  "layer": "module_workflow",
  "suite_id": "collection.replacement.conditional_group_exists_quantified_alternation",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "module-sub-conditional-group-exists-quantified-alternation-replacement-present-first-arm-str",
      "operation": "module_call",
      "family": "conditional_group_exists_quantified_alternation_replacement_present_first_arm_workflow",
      "helper": "sub",
      "args": [
        "a(b)?c(?(1)(de|df)|(eg|eh)){2}",
        "X",
        "zzabcdedezz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "quantified", "exact-repeat", "module", "present", "first-arm", "str", "gap"],
      "notes": [
        "Publishes the bounded numbered module-level quantified alternation-heavy conditional replacement path when the optional capture is present and both repeated yes-arm evaluations take the first `de` branch before constant replacement text is emitted."
      ]
    },
    {
      "id": "module-subn-conditional-group-exists-quantified-alternation-replacement-present-second-arm-str",
      "operation": "module_call",
      "family": "conditional_group_exists_quantified_alternation_replacement_present_second_arm_count_workflow",
      "helper": "subn",
      "args": [
        "a(b)?c(?(1)(de|df)|(eg|eh)){2}",
        "X",
        "zzabcdfdfzz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "quantified", "exact-repeat", "module", "present", "second-arm", "str", "count", "gap"],
      "notes": [
        "Publishes the matching numbered module-level replacement count path when the bounded yes arm instead takes `df` on both repeated alternation evaluations, keeping the second present-branch quantified outcome explicit without widening the slice."
      ]
    },
    {
      "id": "pattern-sub-conditional-group-exists-quantified-alternation-replacement-absent-first-arm-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_quantified_alternation_replacement_absent_first_arm_workflow",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh)){2}",
      "helper": "sub",
      "args": [
        "X",
        "zzacegegzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "quantified", "exact-repeat", "pattern", "absent", "first-arm", "str", "gap"],
      "notes": [
        "Publishes the bound Pattern.sub numbered conditional replacement path when the optional capture is absent and both repeated else-arm evaluations take the first `eg` branch before replacement text is applied."
      ]
    },
    {
      "id": "pattern-subn-conditional-group-exists-quantified-alternation-replacement-absent-second-arm-str",
      "operation": "pattern_call",
      "family": "conditional_group_exists_quantified_alternation_replacement_absent_second_arm_count_workflow",
      "pattern": "a(b)?c(?(1)(de|df)|(eg|eh)){2}",
      "helper": "subn",
      "args": [
        "X",
        "zzacehehzz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "quantified", "exact-repeat", "pattern", "absent", "second-arm", "str", "count", "gap"],
      "notes": [
        "Publishes the bound Pattern.subn numbered conditional replacement count path when the repeated else arm instead takes `eh`, so both absent-capture quantified alternation branches remain explicit in the scorecard."
      ]
    },
    {
      "id": "module-sub-named-conditional-group-exists-quantified-alternation-replacement-present-first-arm-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_quantified_alternation_replacement_present_first_arm_workflow",
      "helper": "sub",
      "args": [
        "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
        "X",
        "zzabcdedezz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "quantified", "exact-repeat", "named-group", "module", "present", "first-arm", "str", "gap"],
      "notes": [
        "Publishes the matching named module-level quantified alternation-heavy conditional replacement path when the optional named capture is present and both repeated yes-arm evaluations take the first `de` branch."
      ]
    },
    {
      "id": "module-subn-named-conditional-group-exists-quantified-alternation-replacement-present-second-arm-str",
      "operation": "module_call",
      "family": "named_conditional_group_exists_quantified_alternation_replacement_present_second_arm_count_workflow",
      "helper": "subn",
      "args": [
        "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
        "X",
        "zzabcdfdfzz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "quantified", "exact-repeat", "named-group", "module", "present", "second-arm", "str", "count", "gap"],
      "notes": [
        "Publishes the matching named module-level replacement count path when the bounded yes arm takes its repeated second `df` branch."
      ]
    },
    {
      "id": "pattern-sub-named-conditional-group-exists-quantified-alternation-replacement-absent-first-arm-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_quantified_alternation_replacement_absent_first_arm_workflow",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
      "helper": "sub",
      "args": [
        "X",
        "zzacegegzz"
      ],
      "categories": ["workflow", "sub", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "quantified", "exact-repeat", "named-group", "pattern", "absent", "first-arm", "str", "gap"],
      "notes": [
        "Publishes the bound Pattern.sub named conditional replacement path when the named capture is absent and the repeated else arm contributes `eg` on both evaluations."
      ]
    },
    {
      "id": "pattern-subn-named-conditional-group-exists-quantified-alternation-replacement-absent-second-arm-str",
      "operation": "pattern_call",
      "family": "named_conditional_group_exists_quantified_alternation_replacement_absent_second_arm_count_workflow",
      "pattern": "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
      "helper": "subn",
      "args": [
        "X",
        "zzacehehzz",
        1
      ],
      "categories": ["workflow", "subn", "replacement", "constant-replacement", "grouped", "optional-group", "conditional", "group-exists", "two-arm", "alternation", "quantified", "exact-repeat", "named-group", "pattern", "absent", "second-arm", "str", "count", "gap"],
      "notes": [
        "Publishes the bound Pattern.subn named conditional replacement count path when the bounded else-arm alternation takes its repeated second `eh` branch, keeping the smallest named quantified alternation-heavy replacement gap explicit."
      ]
    }
  ]
}
