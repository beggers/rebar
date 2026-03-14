MANIFEST = {
    "schema_version": 1,
    "manifest_id": "nested-group-callable-replacement-workflows",
    "layer": "module_workflow",
    "suite_id": "collection.replacement.nested_group.callable",
    "defaults": {
        "text_model": "str",
    },
    "cases": [
        {
            "id": "module-sub-callable-nested-group-numbered-str",
            "operation": "module_call",
            "family": "nested_group_callable_replacement_workflow",
            "helper": "sub",
            "args": [
                "a((b))d",
                {
                    "type": "callable_match_group",
                    "group": 1,
                    "suffix": "x",
                },
                "abdabd",
            ],
            "categories": [
                "workflow",
                "sub",
                "callable-replacement",
                "nested-group",
                "numbered-group",
                "module",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the bounded module-level nested-group callable replacement path for one outer numbered capture containing one inner numbered capture."
            ],
        },
        {
            "id": "module-subn-callable-nested-group-numbered-str",
            "operation": "module_call",
            "family": "nested_group_callable_replacement_workflow",
            "helper": "subn",
            "args": [
                "a((b))d",
                {
                    "type": "callable_match_group",
                    "group": 2,
                    "suffix": "x",
                },
                "abdabd",
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "callable-replacement",
                "nested-group",
                "numbered-group",
                "module",
                "str",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the bounded module-level nested-group callable replacement count path using the inner numbered capture without broadening into alternation, quantifiers, or branch-local references."
            ],
        },
        {
            "id": "pattern-sub-callable-nested-group-numbered-str",
            "operation": "pattern_call",
            "family": "nested_group_callable_replacement_workflow",
            "pattern": "a((b))d",
            "helper": "sub",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": 1,
                    "suffix": "x",
                },
                "abdabd",
            ],
            "categories": [
                "workflow",
                "sub",
                "callable-replacement",
                "nested-group",
                "numbered-group",
                "pattern",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the bound Pattern.sub nested-group callable replacement path for the same one-site numbered nested capture shape."
            ],
        },
        {
            "id": "pattern-subn-callable-nested-group-numbered-str",
            "operation": "pattern_call",
            "family": "nested_group_callable_replacement_workflow",
            "pattern": "a((b))d",
            "helper": "subn",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": 2,
                    "suffix": "x",
                },
                "abdabd",
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "callable-replacement",
                "nested-group",
                "numbered-group",
                "pattern",
                "str",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the bound Pattern.subn nested-group callable replacement count path while broader callback semantics remain out of scope."
            ],
        },
        {
            "id": "module-sub-callable-nested-group-named-str",
            "operation": "module_call",
            "family": "named_nested_group_callable_replacement_workflow",
            "helper": "sub",
            "args": [
                "a(?P<outer>(?P<inner>b))d",
                {
                    "type": "callable_match_group",
                    "group": "outer",
                    "suffix": "x",
                },
                "abdabd",
            ],
            "categories": [
                "workflow",
                "sub",
                "callable-replacement",
                "nested-group",
                "named-group",
                "module",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the bounded module-level named nested-group callable replacement path for one named outer capture containing one named inner capture."
            ],
        },
        {
            "id": "module-subn-callable-nested-group-named-str",
            "operation": "module_call",
            "family": "named_nested_group_callable_replacement_workflow",
            "helper": "subn",
            "args": [
                "a(?P<outer>(?P<inner>b))d",
                {
                    "type": "callable_match_group",
                    "group": "inner",
                    "suffix": "x",
                },
                "abdabd",
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "callable-replacement",
                "nested-group",
                "named-group",
                "module",
                "str",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the bounded module-level named nested-group callable replacement count path for the inner named capture without claiming support for nested alternation or quantified groups."
            ],
        },
        {
            "id": "pattern-sub-callable-nested-group-named-str",
            "operation": "pattern_call",
            "family": "named_nested_group_callable_replacement_workflow",
            "pattern": "a(?P<outer>(?P<inner>b))d",
            "helper": "sub",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": "outer",
                    "suffix": "x",
                },
                "abdabd",
            ],
            "categories": [
                "workflow",
                "sub",
                "callable-replacement",
                "nested-group",
                "named-group",
                "pattern",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the bound Pattern.sub named nested-group callable replacement path for the same one-site named nested capture shape."
            ],
        },
        {
            "id": "pattern-subn-callable-nested-group-named-str",
            "operation": "pattern_call",
            "family": "named_nested_group_callable_replacement_workflow",
            "pattern": "a(?P<outer>(?P<inner>b))d",
            "helper": "subn",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": "inner",
                    "suffix": "x",
                },
                "abdabd",
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "callable-replacement",
                "nested-group",
                "named-group",
                "pattern",
                "str",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the bound Pattern.subn named nested-group callable replacement count path while broader callback helpers, alternation, and branch-local references remain out of scope."
            ],
        },
    ],
}
