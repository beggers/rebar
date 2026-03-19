MANIFEST = {
    "schema_version": 1,
    "manifest_id": (
        "nested-broader-range-open-ended-quantified-group-alternation-"
        "backtracking-heavy-callable-replacement-workflows"
    ),
    "layer": "module_workflow",
    "suite_id": (
        "collection.replacement.nested_broader_range_open_ended_"
        "quantified_group_alternation_backtracking_heavy.callable"
    ),
    "defaults": {
        "text_model": "str",
    },
    "cases": [
        {
            "id": (
                "module-sub-callable-nested-broader-range-open-ended-"
                "quantified-group-alternation-backtracking-heavy-numbered-"
                "lower-bound-short-branch-str"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_open_ended_quantified_group_alternation_"
                "backtracking_heavy_numbered_outer_callable_workflow"
            ),
            "helper": "sub",
            "args": [
                r"a(((bc|b)c){2,})d",
                {
                    "type": "callable_match_group",
                    "group": 1,
                    "suffix": "x",
                },
                "abcbcd",
            ],
            "categories": [
                "workflow",
                "sub",
                "callable-replacement",
                "grouped",
                "nested-group",
                "alternation",
                "overlapping-branches",
                "quantified",
                "open-ended-repeat",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "outer-capture",
                "lower-bound",
                "short-branch",
                "module",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the bounded broader-range open-ended `{2,}` numbered module-level nested grouped backtracking-heavy callable replacement lower-bound path on `abcbcd`, so the outer capture stays visible through `match.group(1)` without widening into bytes coverage, Rust-backed parity, or other grouped follow-ons."
            ],
        },
        {
            "id": (
                "module-subn-callable-nested-broader-range-open-ended-"
                "quantified-group-alternation-backtracking-heavy-numbered-"
                "first-match-only-long-branch-str"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_open_ended_quantified_group_alternation_"
                "backtracking_heavy_numbered_inner_callable_count_workflow"
            ),
            "helper": "subn",
            "args": [
                r"a(((bc|b)c){2,})d",
                {
                    "type": "callable_match_group",
                    "group": 3,
                    "prefix": "<",
                    "suffix": ">",
                },
                "abccbccdabcbcd",
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "callable-replacement",
                "grouped",
                "nested-group",
                "alternation",
                "overlapping-branches",
                "quantified",
                "open-ended-repeat",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "long-branch",
                "module",
                "str",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the bounded broader-range open-ended `{2,}` numbered module-level callable replacement first-match-only path on `abccbccdabcbcd`, so the leading long-branch match exposes the final overlapping alternation choice through `match.group(3)` while the trailing lower-bound match remains unchanged."
            ],
        },
        {
            "id": (
                "pattern-sub-callable-nested-broader-range-open-ended-"
                "quantified-group-alternation-backtracking-heavy-numbered-"
                "mixed-branches-str"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_open_ended_quantified_group_alternation_"
                "backtracking_heavy_numbered_outer_callable_workflow"
            ),
            "pattern": r"a(((bc|b)c){2,})d",
            "helper": "sub",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": 1,
                    "suffix": "x",
                },
                "zzabccbcdzz",
            ],
            "categories": [
                "workflow",
                "sub",
                "callable-replacement",
                "grouped",
                "nested-group",
                "alternation",
                "overlapping-branches",
                "quantified",
                "open-ended-repeat",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "outer-capture",
                "mixed-branches",
                "pattern",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the bounded broader-range open-ended `{2,}` Pattern.sub numbered callable replacement mixed-branch path on `abccbcd`, so the outer capture expands across one long `bcc` branch followed by one short `bc` branch under the same open-ended nested site."
            ],
        },
        {
            "id": (
                "pattern-subn-callable-nested-broader-range-open-ended-"
                "quantified-group-alternation-backtracking-heavy-numbered-"
                "fourth-repetition-b-branch-first-match-only-str"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_open_ended_quantified_group_alternation_"
                "backtracking_heavy_numbered_inner_callable_count_workflow"
            ),
            "pattern": r"a(((bc|b)c){2,})d",
            "helper": "subn",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": 3,
                    "prefix": "<",
                    "suffix": ">",
                },
                "zzabcbcbcbcdabccbccdzz",
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "callable-replacement",
                "grouped",
                "nested-group",
                "alternation",
                "overlapping-branches",
                "quantified",
                "open-ended-repeat",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "fourth-repetition",
                "b-branch",
                "pattern",
                "str",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the bounded broader-range open-ended `{2,}` Pattern.subn numbered callable replacement first-match-only path on a leading four-repetition short-branch match, keeping the final `b` choice observable through `match.group(3)` while the later long-branch match remains unchanged."
            ],
        },
        {
            "id": (
                "module-sub-callable-nested-broader-range-open-ended-"
                "quantified-group-alternation-backtracking-heavy-named-"
                "mixed-branches-str"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_open_ended_quantified_group_alternation_"
                "backtracking_heavy_named_outer_callable_workflow"
            ),
            "helper": "sub",
            "args": [
                r"a(?P<outer>(?:(?P<inner>bc|b)c){2,})d",
                {
                    "type": "callable_match_group",
                    "group": "outer",
                    "suffix": "x",
                },
                "abccbcd",
            ],
            "categories": [
                "workflow",
                "sub",
                "callable-replacement",
                "grouped",
                "nested-group",
                "alternation",
                "overlapping-branches",
                "quantified",
                "open-ended-repeat",
                "broader-range",
                "counted-repeat",
                "named-group",
                "outer-capture",
                "mixed-branches",
                "module",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the bounded broader-range open-ended `{2,}` named module-level callable replacement mixed-branch path on `abccbcd`, so the visible `outer` capture remains observable through `match.group(\"outer\")` across one long branch followed by one short branch."
            ],
        },
        {
            "id": (
                "module-subn-callable-nested-broader-range-open-ended-"
                "quantified-group-alternation-backtracking-heavy-named-"
                "first-match-only-long-branch-str"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_open_ended_quantified_group_alternation_"
                "backtracking_heavy_named_inner_callable_count_workflow"
            ),
            "helper": "subn",
            "args": [
                r"a(?P<outer>(?:(?P<inner>bc|b)c){2,})d",
                {
                    "type": "callable_match_group",
                    "group": "inner",
                    "prefix": "<",
                    "suffix": ">",
                },
                "abccbccdabcbcd",
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "callable-replacement",
                "grouped",
                "nested-group",
                "alternation",
                "overlapping-branches",
                "quantified",
                "open-ended-repeat",
                "broader-range",
                "counted-repeat",
                "named-group",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "long-branch",
                "module",
                "str",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the bounded broader-range open-ended `{2,}` named module-level callable replacement first-match-only path on `abccbccdabcbcd`, so the leading long-branch match keeps the final `inner` value visible while the trailing lower-bound match stays untouched."
            ],
        },
        {
            "id": (
                "pattern-sub-callable-nested-broader-range-open-ended-"
                "quantified-group-alternation-backtracking-heavy-named-"
                "fourth-repetition-short-only-str"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_open_ended_quantified_group_alternation_"
                "backtracking_heavy_named_outer_callable_workflow"
            ),
            "pattern": r"a(?P<outer>(?:(?P<inner>bc|b)c){2,})d",
            "helper": "sub",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": "outer",
                    "suffix": "x",
                },
                "zzabcbcbcbcdzz",
            ],
            "categories": [
                "workflow",
                "sub",
                "callable-replacement",
                "grouped",
                "nested-group",
                "alternation",
                "overlapping-branches",
                "quantified",
                "open-ended-repeat",
                "broader-range",
                "counted-repeat",
                "named-group",
                "outer-capture",
                "fourth-repetition",
                "short-only",
                "pattern",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the bounded broader-range open-ended `{2,}` Pattern.sub named callable replacement four-repetition short-branch path on `abcbcbcbcd`, so the visible `outer` capture spans four valid short branches without pretending to exhaust arbitrary-length grouped backtracking."
            ],
        },
        {
            "id": (
                "pattern-subn-callable-nested-broader-range-open-ended-"
                "quantified-group-alternation-backtracking-heavy-named-"
                "b-branch-first-match-only-str"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_open_ended_quantified_group_alternation_"
                "backtracking_heavy_named_inner_callable_count_workflow"
            ),
            "pattern": r"a(?P<outer>(?:(?P<inner>bc|b)c){2,})d",
            "helper": "subn",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": "inner",
                    "prefix": "<",
                    "suffix": ">",
                },
                "zzabcbcbcbcdabccbccdzz",
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "callable-replacement",
                "grouped",
                "nested-group",
                "alternation",
                "overlapping-branches",
                "quantified",
                "open-ended-repeat",
                "broader-range",
                "counted-repeat",
                "named-group",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "b-branch",
                "pattern",
                "str",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the bounded broader-range open-ended `{2,}` Pattern.subn named callable replacement first-match-only path on a leading four-repetition short-branch match, keeping the final `inner` branch observable while the later long-branch match remains unchanged."
            ],
        },
    ],
}
