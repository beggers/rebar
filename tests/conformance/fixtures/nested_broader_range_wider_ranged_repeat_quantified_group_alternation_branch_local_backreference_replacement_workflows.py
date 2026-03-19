MANIFEST = {
    "schema_version": 1,
    "manifest_id": (
        "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-"
        "branch-local-backreference-replacement-workflows"
    ),
    "layer": "module_workflow",
    "suite_id": (
        "collection.replacement."
        "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_"
        "branch_local_backreference"
    ),
    "defaults": {
        "text_model": "str",
    },
    "cases": [
        {
            "id": (
                "module-sub-template-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "numbered-lower-bound-b-branch-str"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_numbered_outer_"
                "template_workflow"
            ),
            "helper": "sub",
            "args": [
                r"a((b|c){1,4})\2d",
                r"\1x",
                "abbd",
            ],
            "categories": [
                "workflow",
                "sub",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "numbered-backreference",
                "branch-local",
                "outer-capture",
                "lower-bound",
                "b-branch",
                "module",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` numbered module-level nested grouped-alternation plus same-branch backreference replacement-template lower-bound path on `abbd`, so the outer capture stays visible through `\\1x` without broadening into bytes, callable replacement, or open-ended repeats.",
            ],
        },
        {
            "id": (
                "module-subn-template-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "numbered-first-match-only-b-branch-str"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_numbered_inner_"
                "template_count_workflow"
            ),
            "helper": "subn",
            "args": [
                r"a((b|c){1,4})\2d",
                r"\2x",
                "abbbdaccd",
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "numbered-backreference",
                "branch-local",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "repeated-branch",
                "b-branch",
                "module",
                "str",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` numbered module-level replacement-template first-match-only path on `abbbdaccd`, so the leading repeated-branch match exposes the final inner `b` branch through `\\2x` while the trailing `c`-branch replay stays untouched.",
            ],
        },
        {
            "id": (
                "pattern-sub-template-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "numbered-mixed-branches-str"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_numbered_outer_"
                "template_workflow"
            ),
            "pattern": r"a((b|c){1,4})\2d",
            "helper": "sub",
            "args": [
                r"\1x",
                "zzabcbccdzz",
            ],
            "categories": [
                "workflow",
                "sub",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "numbered-backreference",
                "branch-local",
                "outer-capture",
                "mixed-branches",
                "pattern",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.sub numbered replacement-template mixed-branch path on `abcbccd`, so the outer capture expands across repeated `b` and `c` selections before the final `c` branch is replayed.",
            ],
        },
        {
            "id": (
                "pattern-subn-template-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "numbered-c-branch-first-match-only-str"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_numbered_inner_"
                "template_count_workflow"
            ),
            "pattern": r"a((b|c){1,4})\2d",
            "helper": "subn",
            "args": [
                r"\2x",
                "zzaccdabcbccdzz",
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "numbered-backreference",
                "branch-local",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "c-branch",
                "pattern",
                "str",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.subn numbered replacement-template first-match-only path on a leading `accd` match, keeping the final inner `c` branch observable while the later mixed-branch replay remains unchanged.",
            ],
        },
        {
            "id": (
                "module-sub-template-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "named-mixed-branches-str"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_named_outer_"
                "template_workflow"
            ),
            "helper": "sub",
            "args": [
                r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
                r"\g<outer>x",
                "abcbccd",
            ],
            "categories": [
                "workflow",
                "sub",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "named-group",
                "named-backreference",
                "branch-local",
                "outer-capture",
                "mixed-branches",
                "module",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` named module-level replacement-template mixed-branch path on `abcbccd`, so the visible `outer` capture stays observable through `\\g<outer>x` across a broader repeated branch selection.",
            ],
        },
        {
            "id": (
                "module-subn-template-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "named-first-match-only-b-branch-str"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_named_inner_"
                "template_count_workflow"
            ),
            "helper": "subn",
            "args": [
                r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
                r"\g<inner>x",
                "abbbdaccd",
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "named-group",
                "named-backreference",
                "branch-local",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "repeated-branch",
                "b-branch",
                "module",
                "str",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` named module-level replacement-template first-match-only path on `abbbdaccd`, so the leading repeated-branch match keeps the final `inner` value observable while the trailing `c`-branch replay stays untouched.",
            ],
        },
        {
            "id": (
                "pattern-sub-template-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "named-upper-bound-c-branch-str"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_named_outer_"
                "template_workflow"
            ),
            "pattern": r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
            "helper": "sub",
            "args": [
                r"\g<outer>x",
                "zzacccccdzz",
            ],
            "categories": [
                "workflow",
                "sub",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "named-group",
                "named-backreference",
                "branch-local",
                "outer-capture",
                "upper-bound",
                "c-branch",
                "pattern",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.sub named replacement-template upper-bound path on `acccccd`, so the visible `outer` capture remains explicit across four `c`-branch repetitions before the final replay.",
            ],
        },
        {
            "id": (
                "pattern-subn-template-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "named-c-branch-first-match-only-str"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_named_inner_"
                "template_count_workflow"
            ),
            "pattern": r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
            "helper": "subn",
            "args": [
                r"\g<inner>x",
                "zzacccccdabbbdzz",
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "named-group",
                "named-backreference",
                "branch-local",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "c-branch",
                "pattern",
                "str",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.subn named replacement-template first-match-only path on a leading `acccccd` match, keeping the final `inner` `c` branch observable while the later `b`-branch replay remains unchanged.",
            ],
        },
        {
            "id": (
                "module-sub-template-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "numbered-lower-bound-b-branch-bytes"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_numbered_outer_"
                "template_workflow"
            ),
            "helper": "sub",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"a((b|c){1,4})\2d",
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"\1x",
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "abbd",
                },
            ],
            "categories": [
                "workflow",
                "sub",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "numbered-backreference",
                "branch-local",
                "outer-capture",
                "lower-bound",
                "b-branch",
                "module",
                "bytes",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` numbered module-level nested grouped-alternation plus same-branch backreference replacement-template lower-bound path on `abbd` with bytes payloads, so the outer capture stays visible through `\\1x` on the shared mixed-text parity surface.",
            ],
        },
        {
            "id": (
                "module-subn-template-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "numbered-first-match-only-b-branch-bytes"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_numbered_inner_"
                "template_count_workflow"
            ),
            "helper": "subn",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"a((b|c){1,4})\2d",
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"\2x",
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "abbbdaccd",
                },
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "numbered-backreference",
                "branch-local",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "repeated-branch",
                "b-branch",
                "module",
                "bytes",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` numbered module-level replacement-template first-match-only path on `abbbdaccd` with bytes payloads, so the leading repeated-branch match exposes the final inner `b` branch through `\\2x` while the trailing `c`-branch replay stays untouched.",
            ],
        },
        {
            "id": (
                "pattern-sub-template-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "numbered-mixed-branches-bytes"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_numbered_outer_"
                "template_workflow"
            ),
            "pattern": r"a((b|c){1,4})\2d",
            "helper": "sub",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"\1x",
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "zzabcbccdzz",
                },
            ],
            "categories": [
                "workflow",
                "sub",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "numbered-backreference",
                "branch-local",
                "outer-capture",
                "mixed-branches",
                "pattern",
                "bytes",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.sub numbered replacement-template mixed-branch path on `abcbccd` with bytes payloads, so the outer capture stays explicit on the shared mixed-text parity surface.",
            ],
        },
        {
            "id": (
                "pattern-subn-template-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "numbered-c-branch-first-match-only-bytes"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_numbered_inner_"
                "template_count_workflow"
            ),
            "pattern": r"a((b|c){1,4})\2d",
            "helper": "subn",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"\2x",
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "zzaccdabcbccdzz",
                },
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "numbered-backreference",
                "branch-local",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "c-branch",
                "pattern",
                "bytes",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.subn numbered replacement-template first-match-only path on a leading `accd` match with bytes payloads, keeping the final inner `c` branch observable while the later mixed-branch replay remains unchanged.",
            ],
        },
        {
            "id": (
                "module-sub-template-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "named-mixed-branches-bytes"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_named_outer_"
                "template_workflow"
            ),
            "helper": "sub",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"\g<outer>x",
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "abcbccd",
                },
            ],
            "categories": [
                "workflow",
                "sub",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "named-group",
                "named-backreference",
                "branch-local",
                "outer-capture",
                "mixed-branches",
                "module",
                "bytes",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` named module-level replacement-template mixed-branch path on `abcbccd` with bytes payloads, so the visible `outer` capture stays observable through `\\g<outer>x` on the shared mixed-text parity surface.",
            ],
        },
        {
            "id": (
                "module-subn-template-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "named-first-match-only-b-branch-bytes"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_named_inner_"
                "template_count_workflow"
            ),
            "helper": "subn",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"\g<inner>x",
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "abbbdaccd",
                },
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "named-group",
                "named-backreference",
                "branch-local",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "repeated-branch",
                "b-branch",
                "module",
                "bytes",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` named module-level replacement-template first-match-only path on `abbbdaccd` with bytes payloads, so the leading repeated-branch match keeps the final `inner` value observable while the trailing `c`-branch replay stays untouched.",
            ],
        },
        {
            "id": (
                "pattern-sub-template-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "named-upper-bound-c-branch-bytes"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_named_outer_"
                "template_workflow"
            ),
            "pattern": r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
            "helper": "sub",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"\g<outer>x",
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "zzacccccdzz",
                },
            ],
            "categories": [
                "workflow",
                "sub",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "named-group",
                "named-backreference",
                "branch-local",
                "outer-capture",
                "upper-bound",
                "c-branch",
                "pattern",
                "bytes",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.sub named replacement-template upper-bound path on `acccccd` with bytes payloads, so the visible `outer` capture remains explicit across four `c`-branch repetitions before the final replay.",
            ],
        },
        {
            "id": (
                "pattern-subn-template-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "named-c-branch-first-match-only-bytes"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_named_inner_"
                "template_count_workflow"
            ),
            "pattern": r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
            "helper": "subn",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"\g<inner>x",
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "zzacccccdabbbdzz",
                },
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "named-group",
                "named-backreference",
                "branch-local",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "c-branch",
                "pattern",
                "bytes",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.subn named replacement-template first-match-only path on a leading `acccccd` match with bytes payloads, keeping the final `inner` `c` branch observable while the later `b`-branch replay remains unchanged.",
            ],
        },
    ],
}
