MANIFEST = {
    "schema_version": 1,
    "manifest_id": (
        "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-"
        "backtracking-heavy-callable-replacement-workflows"
    ),
    "layer": "module_workflow",
    "suite_id": (
        "collection.replacement.nested_broader_range_wider_ranged_repeat_"
        "quantified_group_alternation_backtracking_heavy.callable"
    ),
    "defaults": {
        "text_model": "str",
    },
    "cases": [
        {
            "id": (
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-backtracking-heavy-numbered-"
                "lower-bound-short-branch-str"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_backtracking_heavy_numbered_outer_callable_workflow"
            ),
            "helper": "sub",
            "args": [
                r"a(((bc|b)c){1,4})d",
                {
                    "type": "callable_match_group",
                    "group": 1,
                    "suffix": "x",
                },
                "abcd",
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
                "ranged-repeat",
                "wider-range",
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
                "Publishes the broader `{1,4}` numbered module-level nested grouped backtracking-heavy callable replacement lower-bound path on `abcd`, so the outer capture stays visible through `match.group(1)` without widening into branch-local backreferences, bytes coverage, or general callback behavior."
            ],
        },
        {
            "id": (
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-backtracking-heavy-numbered-"
                "first-match-only-long-branch-str"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_backtracking_heavy_numbered_inner_callable_count_"
                "workflow"
            ),
            "helper": "subn",
            "args": [
                r"a(((bc|b)c){1,4})d",
                {
                    "type": "callable_match_group",
                    "group": 3,
                    "prefix": "<",
                    "suffix": ">",
                },
                "abccdabcbccd",
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
                "ranged-repeat",
                "wider-range",
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
                "Publishes the broader `{1,4}` numbered module-level callable replacement first-match-only path on `abccdabcbccd`, so the leading long-branch `abccd` match exposes the final overlapping alternation choice through `match.group(3)` while the trailing mixed-branch match remains untouched."
            ],
        },
        {
            "id": (
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-backtracking-heavy-numbered-"
                "mixed-branches-str"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_backtracking_heavy_numbered_outer_callable_workflow"
            ),
            "pattern": r"a(((bc|b)c){1,4})d",
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
                "ranged-repeat",
                "wider-range",
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
                "Publishes the broader `{1,4}` Pattern.sub numbered callable replacement mixed-branch path on `abccbcd`, so the outer capture expands across one long `bcc` branch followed by one short `bc` branch under the same bounded nested site."
            ],
        },
        {
            "id": (
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-backtracking-heavy-numbered-"
                "upper-bound-b-branch-first-match-only-str"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_backtracking_heavy_numbered_inner_callable_count_"
                "workflow"
            ),
            "pattern": r"a(((bc|b)c){1,4})d",
            "helper": "subn",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": 3,
                    "prefix": "<",
                    "suffix": ">",
                },
                "zzabcbccbccbcdabccdzz",
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
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "upper-bound",
                "b-branch",
                "pattern",
                "str",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.subn numbered callable replacement first-match-only path on a leading four-repetition mixed match, keeping the final short-branch choice observable through `match.group(3)` while the later long-branch match remains unchanged."
            ],
        },
        {
            "id": (
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-backtracking-heavy-named-"
                "mixed-branches-str"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_backtracking_heavy_named_outer_callable_workflow"
            ),
            "helper": "sub",
            "args": [
                r"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d",
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
                "ranged-repeat",
                "wider-range",
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
                "Publishes the broader `{1,4}` named module-level callable replacement mixed-branch path on `abccbcd`, so the visible `outer` capture remains observable through `match.group(\"outer\")` across the overlapping long-then-short branch choice."
            ],
        },
        {
            "id": (
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-backtracking-heavy-named-"
                "first-match-only-long-branch-str"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_backtracking_heavy_named_inner_callable_count_"
                "workflow"
            ),
            "helper": "subn",
            "args": [
                r"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d",
                {
                    "type": "callable_match_group",
                    "group": "inner",
                    "prefix": "<",
                    "suffix": ">",
                },
                "abccdabcbccd",
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
                "ranged-repeat",
                "wider-range",
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
                "Publishes the broader `{1,4}` named module-level callable replacement first-match-only path on `abccdabcbccd`, so the leading long-branch `abccd` match keeps the final `inner` value visible while the trailing mixed-branch match remains untouched."
            ],
        },
        {
            "id": (
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-backtracking-heavy-named-"
                "upper-bound-mixed-str"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_backtracking_heavy_named_outer_callable_workflow"
            ),
            "pattern": r"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d",
            "helper": "sub",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": "outer",
                    "suffix": "x",
                },
                "zzabcbccbccbcdzz",
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
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "named-group",
                "outer-capture",
                "upper-bound",
                "mixed-branches",
                "pattern",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.sub named callable replacement upper-bound path on `abcbccbccbcd`, so the visible `outer` capture spans four bounded repetitions with mixed overlapping branch choices."
            ],
        },
        {
            "id": (
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-backtracking-heavy-named-"
                "b-branch-first-match-only-str"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_backtracking_heavy_named_inner_callable_count_"
                "workflow"
            ),
            "pattern": r"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d",
            "helper": "subn",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": "inner",
                    "prefix": "<",
                    "suffix": ">",
                },
                "zzabccbcdabccdzz",
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
                "ranged-repeat",
                "wider-range",
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
                "Publishes the broader `{1,4}` Pattern.subn named callable replacement first-match-only path on a leading mixed-branch match, keeping the final short `inner` branch observable while the trailing long-branch match remains unchanged."
            ],
        },
        {
            "id": (
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-backtracking-heavy-numbered-"
                "lower-bound-short-branch-bytes"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_backtracking_heavy_numbered_outer_callable_workflow"
            ),
            "helper": "sub",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"a(((bc|b)c){1,4})d",
                },
                {
                    "type": "callable_match_group",
                    "group": 1,
                    "prefix": {
                        "type": "bytes",
                        "encoding": "latin-1",
                        "value": "",
                    },
                    "suffix": {
                        "type": "bytes",
                        "encoding": "latin-1",
                        "value": "x",
                    },
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "abcd",
                },
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
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "outer-capture",
                "lower-bound",
                "short-branch",
                "module",
                "bytes",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` numbered module-level nested grouped backtracking-heavy callable replacement lower-bound path on `abcd` with bytes payloads, so the outer capture stays visible through `match.group(1)` while the bytes callable parity follow-on stays explicit."
            ],
        },
        {
            "id": (
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-backtracking-heavy-numbered-"
                "first-match-only-long-branch-bytes"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_backtracking_heavy_numbered_inner_callable_count_"
                "workflow"
            ),
            "helper": "subn",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"a(((bc|b)c){1,4})d",
                },
                {
                    "type": "callable_match_group",
                    "group": 3,
                    "prefix": {
                        "type": "bytes",
                        "encoding": "latin-1",
                        "value": "<",
                    },
                    "suffix": {
                        "type": "bytes",
                        "encoding": "latin-1",
                        "value": ">",
                    },
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "abccdabcbccd",
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
                "overlapping-branches",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "long-branch",
                "module",
                "bytes",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` numbered module-level callable replacement first-match-only path on `abccdabcbccd` with bytes payloads, so the leading long-branch `abccd` match exposes the final overlapping alternation choice through `match.group(3)` while the bytes callable parity follow-on stays explicit."
            ],
        },
        {
            "id": (
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-backtracking-heavy-numbered-"
                "mixed-branches-bytes"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_backtracking_heavy_numbered_outer_callable_workflow"
            ),
            "pattern": r"a(((bc|b)c){1,4})d",
            "helper": "sub",
            "text_model": "bytes",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": 1,
                    "prefix": {
                        "type": "bytes",
                        "encoding": "latin-1",
                        "value": "",
                    },
                    "suffix": {
                        "type": "bytes",
                        "encoding": "latin-1",
                        "value": "x",
                    },
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "zzabccbcdzz",
                },
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
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "outer-capture",
                "mixed-branches",
                "pattern",
                "bytes",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.sub numbered callable replacement mixed-branch path on `abccbcd` with bytes payloads, so the outer capture stays visible on the shared bytes publication surface while the bytes callable parity follow-on stays explicit."
            ],
        },
        {
            "id": (
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-backtracking-heavy-numbered-"
                "upper-bound-b-branch-first-match-only-bytes"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_backtracking_heavy_numbered_inner_callable_count_"
                "workflow"
            ),
            "pattern": r"a(((bc|b)c){1,4})d",
            "helper": "subn",
            "text_model": "bytes",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": 3,
                    "prefix": {
                        "type": "bytes",
                        "encoding": "latin-1",
                        "value": "<",
                    },
                    "suffix": {
                        "type": "bytes",
                        "encoding": "latin-1",
                        "value": ">",
                    },
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "zzabcbccbccbcdabccdzz",
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
                "overlapping-branches",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "numbered-group",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "upper-bound",
                "b-branch",
                "pattern",
                "bytes",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.subn numbered callable replacement first-match-only path on a leading four-repetition mixed match with bytes payloads, keeping the final short-branch choice observable through `match.group(3)` while the bytes callable parity follow-on stays explicit."
            ],
        },
        {
            "id": (
                "module-sub-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-backtracking-heavy-named-"
                "mixed-branches-bytes"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_backtracking_heavy_named_outer_callable_workflow"
            ),
            "helper": "sub",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d",
                },
                {
                    "type": "callable_match_group",
                    "group": "outer",
                    "prefix": {
                        "type": "bytes",
                        "encoding": "latin-1",
                        "value": "",
                    },
                    "suffix": {
                        "type": "bytes",
                        "encoding": "latin-1",
                        "value": "x",
                    },
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "abccbcd",
                },
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
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "named-group",
                "outer-capture",
                "mixed-branches",
                "module",
                "bytes",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` named module-level callable replacement mixed-branch path on `abccbcd` with bytes payloads, so the visible `outer` capture stays observable through `match.group(\"outer\")` while the bytes callable parity follow-on stays explicit."
            ],
        },
        {
            "id": (
                "module-subn-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-backtracking-heavy-named-"
                "first-match-only-long-branch-bytes"
            ),
            "operation": "module_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_backtracking_heavy_named_inner_callable_count_"
                "workflow"
            ),
            "helper": "subn",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d",
                },
                {
                    "type": "callable_match_group",
                    "group": "inner",
                    "prefix": {
                        "type": "bytes",
                        "encoding": "latin-1",
                        "value": "<",
                    },
                    "suffix": {
                        "type": "bytes",
                        "encoding": "latin-1",
                        "value": ">",
                    },
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "abccdabcbccd",
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
                "overlapping-branches",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "named-group",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "long-branch",
                "module",
                "bytes",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` named module-level callable replacement first-match-only path on `abccdabcbccd` with bytes payloads, so the leading long-branch `abccd` match keeps the final `inner` value visible while the bytes callable parity follow-on stays explicit."
            ],
        },
        {
            "id": (
                "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-backtracking-heavy-named-"
                "upper-bound-mixed-bytes"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_backtracking_heavy_named_outer_callable_workflow"
            ),
            "pattern": r"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d",
            "helper": "sub",
            "text_model": "bytes",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": "outer",
                    "prefix": {
                        "type": "bytes",
                        "encoding": "latin-1",
                        "value": "",
                    },
                    "suffix": {
                        "type": "bytes",
                        "encoding": "latin-1",
                        "value": "x",
                    },
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "zzabcbccbccbcdzz",
                },
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
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "named-group",
                "outer-capture",
                "upper-bound",
                "mixed-branches",
                "pattern",
                "bytes",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.sub named callable replacement upper-bound path on `abcbccbccbcd` with bytes payloads, so the visible `outer` capture spans four bounded repetitions with mixed overlapping branch choices while the bytes callable parity follow-on stays explicit."
            ],
        },
        {
            "id": (
                "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-"
                "quantified-group-alternation-backtracking-heavy-named-"
                "b-branch-first-match-only-bytes"
            ),
            "operation": "pattern_call",
            "family": (
                "nested_broader_range_wider_ranged_repeat_quantified_group_"
                "alternation_backtracking_heavy_named_inner_callable_count_"
                "workflow"
            ),
            "pattern": r"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d",
            "helper": "subn",
            "text_model": "bytes",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": "inner",
                    "prefix": {
                        "type": "bytes",
                        "encoding": "latin-1",
                        "value": "<",
                    },
                    "suffix": {
                        "type": "bytes",
                        "encoding": "latin-1",
                        "value": ">",
                    },
                },
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "zzabccbcdabccdzz",
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
                "overlapping-branches",
                "quantified",
                "ranged-repeat",
                "wider-range",
                "broader-range",
                "counted-repeat",
                "named-group",
                "final-inner-capture",
                "count-limited",
                "first-match-only",
                "b-branch",
                "pattern",
                "bytes",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the broader `{1,4}` Pattern.subn named callable replacement first-match-only path on a leading mixed-branch match with bytes payloads, keeping the final short `inner` branch observable while the bytes callable parity follow-on stays explicit."
            ],
        },
    ],
}
