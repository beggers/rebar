MANIFEST = {
    "schema_version": 1,
    "manifest_id": (
        "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-"
        "branch-local-backreference-conditional-callable-replacement-workflows"
    ),
    "layer": "module_workflow",
    "suite_id": (
        "collection.replacement."
        "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_"
        "branch_local_backreference_conditional.callable"
    ),
    "defaults": {
        "text_model": "str",
    },
    "cases": [
        {
            "id": (
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "conditional-numbered-lower-bound-b-branch-str"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_conditional_numbered_"
                "outer_callable_workflow"
            ),
            "helper": "sub",
            "args": [
                r"a((b|c){1,4})\2(?(2)d|e)",
                {
                    "type": "callable_match_group",
                    "group": 1,
                    "suffix": "x",
                },
                "abbd",
            ],
            "categories": [
                "workflow",
                "sub",
                "callable-replacement",
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
                "conditional",
                "group-exists",
                "outer-capture",
                "lower-bound",
                "b-branch",
                "module",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` numbered module-level nested grouped-alternation plus same-branch backreference conditional callable replacement lower-bound path on `abbd`, so the outer capture stays visible through `match.group(1)` while the conditional yes-arm remains fixed on `d`."
            ],
        },
        {
            "id": (
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "conditional-numbered-first-match-only-b-branch-str"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_conditional_numbered_"
                "inner_callable_count_workflow"
            ),
            "helper": "subn",
            "args": [
                r"a((b|c){1,4})\2(?(2)d|e)",
                {
                    "type": "callable_match_group",
                    "group": 2,
                    "prefix": "<",
                    "suffix": ">",
                },
                "abbbdaccd",
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "callable-replacement",
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
                "conditional",
                "group-exists",
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
                "Publishes the broader `{1,4}` numbered module-level conditional callable replacement first-match-only path on `abbbdaccd`, so the leading repeated-branch match exposes the final inner `b` branch through `match.group(2)` while the trailing `c`-branch replay stays untouched."
            ],
        },
        {
            "id": (
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "conditional-numbered-mixed-branches-str"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_conditional_numbered_"
                "outer_callable_workflow"
            ),
            "pattern": r"a((b|c){1,4})\2(?(2)d|e)",
            "helper": "sub",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": 1,
                    "suffix": "x",
                },
                "zzabcbccdzz",
            ],
            "categories": [
                "workflow",
                "sub",
                "callable-replacement",
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
                "conditional",
                "group-exists",
                "outer-capture",
                "mixed-branches",
                "pattern",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.sub numbered conditional callable replacement mixed-branch path on `abcbccd`, so the outer capture expands across repeated `b` and `c` selections before the final `c` branch is replayed and the conditional yes-arm closes on `d`."
            ],
        },
        {
            "id": (
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "conditional-numbered-c-branch-first-match-only-str"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_conditional_numbered_"
                "inner_callable_count_workflow"
            ),
            "pattern": r"a((b|c){1,4})\2(?(2)d|e)",
            "helper": "subn",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": 2,
                    "prefix": "<",
                    "suffix": ">",
                },
                "zzaccdabcbccdzz",
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "callable-replacement",
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
                "conditional",
                "group-exists",
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
                "Publishes the broader `{1,4}` Pattern.subn numbered conditional callable replacement first-match-only path on a leading `accd` match, keeping the final inner `c` branch observable while the later mixed-branch replay remains unchanged."
            ],
        },
        {
            "id": (
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "conditional-named-mixed-branches-str"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_conditional_named_"
                "outer_callable_workflow"
            ),
            "helper": "sub",
            "args": [
                r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)",
                {
                    "type": "callable_match_group",
                    "group": "outer",
                    "suffix": "x",
                },
                "abcbccd",
            ],
            "categories": [
                "workflow",
                "sub",
                "callable-replacement",
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
                "conditional",
                "group-exists",
                "outer-capture",
                "mixed-branches",
                "module",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` named module-level conditional callable replacement mixed-branch path on `abcbccd`, so the visible `outer` capture stays observable through `match.group(\"outer\")` across a broader repeated branch selection."
            ],
        },
        {
            "id": (
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "conditional-named-first-match-only-b-branch-str"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_conditional_named_"
                "inner_callable_count_workflow"
            ),
            "helper": "subn",
            "args": [
                r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)",
                {
                    "type": "callable_match_group",
                    "group": "inner",
                    "prefix": "<",
                    "suffix": ">",
                },
                "abbbdaccd",
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "callable-replacement",
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
                "conditional",
                "group-exists",
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
                "Publishes the broader `{1,4}` named module-level conditional callable replacement first-match-only path on `abbbdaccd`, so the leading repeated-branch match keeps the final `inner` value observable while the trailing `c`-branch replay stays untouched."
            ],
        },
        {
            "id": (
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "conditional-named-upper-bound-c-branch-str"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_conditional_named_"
                "outer_callable_workflow"
            ),
            "pattern": r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)",
            "helper": "sub",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": "outer",
                    "suffix": "x",
                },
                "zzacccccdzz",
            ],
            "categories": [
                "workflow",
                "sub",
                "callable-replacement",
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
                "conditional",
                "group-exists",
                "outer-capture",
                "upper-bound",
                "c-branch",
                "pattern",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.sub named conditional callable replacement upper-bound path on `acccccd`, so the visible `outer` capture remains explicit across four repeated `c` branches before the replayed `inner` branch and conditional yes-arm close the match."
            ],
        },
        {
            "id": (
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "conditional-named-c-branch-first-match-only-str"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_conditional_named_"
                "inner_callable_count_workflow"
            ),
            "pattern": r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)",
            "helper": "subn",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": "inner",
                    "prefix": "<",
                    "suffix": ">",
                },
                "zzacccccdabbbdzz",
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "callable-replacement",
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
                "conditional",
                "group-exists",
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
                "Publishes the broader `{1,4}` Pattern.subn named conditional callable replacement first-match-only path on a leading upper-bound `c`-branch match, keeping the final selected `inner` branch observable while the later `b`-branch replay remains unchanged."
            ],
        },
        {
            "id": (
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "conditional-numbered-lower-bound-b-branch-bytes"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_conditional_numbered_"
                "outer_callable_workflow"
            ),
            "helper": "sub",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"a((b|c){1,4})\2(?(2)d|e)",
                },
                {
                    "type": "callable_match_group",
                    "group": 1,
                    "suffix": "x",
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
                "callable-replacement",
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
                "conditional",
                "group-exists",
                "outer-capture",
                "lower-bound",
                "b-branch",
                "module",
                "bytes",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` numbered module-level nested grouped-alternation plus same-branch backreference conditional callable replacement lower-bound path on `abbd` with bytes payloads, so the outer capture stays visible through `match.group(1)` while bytes callable parity remains explicit."
            ],
        },
        {
            "id": (
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "conditional-numbered-first-match-only-b-branch-bytes"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_conditional_numbered_"
                "inner_callable_count_workflow"
            ),
            "helper": "subn",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"a((b|c){1,4})\2(?(2)d|e)",
                },
                {
                    "type": "callable_match_group",
                    "group": 2,
                    "prefix": "<",
                    "suffix": ">",
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
                "callable-replacement",
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
                "conditional",
                "group-exists",
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
                "Publishes the broader `{1,4}` numbered module-level conditional callable replacement first-match-only path on `abbbdaccd` with bytes payloads, so the leading repeated-branch match exposes the final inner `b` branch through `match.group(2)` while the bytes callable follow-on stays honest."
            ],
        },
        {
            "id": (
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "conditional-numbered-mixed-branches-bytes"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_conditional_numbered_"
                "outer_callable_workflow"
            ),
            "pattern": r"a((b|c){1,4})\2(?(2)d|e)",
            "helper": "sub",
            "text_model": "bytes",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": 1,
                    "suffix": "x",
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
                "callable-replacement",
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
                "conditional",
                "group-exists",
                "outer-capture",
                "mixed-branches",
                "pattern",
                "bytes",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.sub numbered conditional callable replacement mixed-branch path on `abcbccd` with bytes payloads, so the outer capture stays explicit on the shared bytes publication surface while runtime callable parity remains a follow-on."
            ],
        },
        {
            "id": (
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "conditional-numbered-c-branch-first-match-only-bytes"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_conditional_numbered_"
                "inner_callable_count_workflow"
            ),
            "pattern": r"a((b|c){1,4})\2(?(2)d|e)",
            "helper": "subn",
            "text_model": "bytes",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": 2,
                    "prefix": "<",
                    "suffix": ">",
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
                "callable-replacement",
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
                "conditional",
                "group-exists",
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
                "Publishes the broader `{1,4}` Pattern.subn numbered conditional callable replacement first-match-only path on a leading `accd` match with bytes payloads, keeping the final inner `c` branch observable while the later mixed-branch replay remains unchanged."
            ],
        },
        {
            "id": (
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "conditional-named-mixed-branches-bytes"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_conditional_named_"
                "outer_callable_workflow"
            ),
            "helper": "sub",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)",
                },
                {
                    "type": "callable_match_group",
                    "group": "outer",
                    "suffix": "x",
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
                "callable-replacement",
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
                "conditional",
                "group-exists",
                "outer-capture",
                "mixed-branches",
                "module",
                "bytes",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` named module-level conditional callable replacement mixed-branch path on `abcbccd` with bytes payloads, so the visible `outer` capture stays observable through `match.group(\"outer\")` while bytes parity remains queued behind this publication."
            ],
        },
        {
            "id": (
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "conditional-named-first-match-only-b-branch-bytes"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_conditional_named_"
                "inner_callable_count_workflow"
            ),
            "helper": "subn",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)",
                },
                {
                    "type": "callable_match_group",
                    "group": "inner",
                    "prefix": "<",
                    "suffix": ">",
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
                "callable-replacement",
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
                "conditional",
                "group-exists",
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
                "Publishes the broader `{1,4}` named module-level conditional callable replacement first-match-only path on `abbbdaccd` with bytes payloads, so the leading repeated-branch match keeps the final `inner` value observable while the trailing `c`-branch replay stays untouched."
            ],
        },
        {
            "id": (
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "conditional-named-upper-bound-c-branch-bytes"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_conditional_named_"
                "outer_callable_workflow"
            ),
            "pattern": r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)",
            "helper": "sub",
            "text_model": "bytes",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": "outer",
                    "suffix": "x",
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
                "callable-replacement",
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
                "conditional",
                "group-exists",
                "outer-capture",
                "upper-bound",
                "c-branch",
                "pattern",
                "bytes",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.sub named conditional callable replacement upper-bound path on `acccccd` with bytes payloads, so the visible `outer` capture remains explicit across four repeated `c` branches while native bytes callable replacement stays unimplemented."
            ],
        },
        {
            "id": (
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-branch-local-backreference-"
                "conditional-named-c-branch-first-match-only-bytes"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_branch_local_backreference_conditional_named_"
                "inner_callable_count_workflow"
            ),
            "pattern": r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)",
            "helper": "subn",
            "text_model": "bytes",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": "inner",
                    "prefix": "<",
                    "suffix": ">",
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
                "callable-replacement",
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
                "conditional",
                "group-exists",
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
                "Publishes the broader `{1,4}` Pattern.subn named conditional callable replacement first-match-only path on a leading upper-bound `c`-branch match with bytes payloads, keeping the final selected `inner` branch observable while the later `b`-branch replay remains unchanged."
            ],
        },
    ],
}
