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
        {
            "id": "module-sub-callable-nested-group-numbered-bytes",
            "operation": "module_call",
            "family": "nested_group_callable_replacement_workflow",
            "helper": "sub",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"a((b))d",
                },
                {
                    "type": "callable_match_group",
                    "group": 1,
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
                    "value": "abdabd",
                },
            ],
            "categories": [
                "workflow",
                "sub",
                "callable-replacement",
                "nested-group",
                "numbered-group",
                "module",
                "bytes",
                "gap",
            ],
            "notes": [
                "Publishes the bounded module-level nested-group callable replacement path for one outer numbered capture containing one inner numbered capture with bytes payloads."
            ],
        },
        {
            "id": "module-subn-callable-nested-group-numbered-bytes",
            "operation": "module_call",
            "family": "nested_group_callable_replacement_workflow",
            "helper": "subn",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"a((b))d",
                },
                {
                    "type": "callable_match_group",
                    "group": 2,
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
                    "value": "abdabd",
                },
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "callable-replacement",
                "nested-group",
                "numbered-group",
                "module",
                "bytes",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the bounded module-level nested-group callable replacement count path using the inner numbered capture on bytes inputs without widening into broader callback semantics."
            ],
        },
        {
            "id": "pattern-sub-callable-nested-group-numbered-bytes",
            "operation": "pattern_call",
            "family": "nested_group_callable_replacement_workflow",
            "pattern": r"a((b))d",
            "helper": "sub",
            "text_model": "bytes",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": 1,
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
                    "value": "abdabd",
                },
            ],
            "categories": [
                "workflow",
                "sub",
                "callable-replacement",
                "nested-group",
                "numbered-group",
                "pattern",
                "bytes",
                "gap",
            ],
            "notes": [
                "Publishes the bound Pattern.sub nested-group callable replacement path for the same one-site numbered nested capture shape on bytes payloads."
            ],
        },
        {
            "id": "pattern-subn-callable-nested-group-numbered-bytes",
            "operation": "pattern_call",
            "family": "nested_group_callable_replacement_workflow",
            "pattern": r"a((b))d",
            "helper": "subn",
            "text_model": "bytes",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": 2,
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
                    "value": "abdabd",
                },
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "callable-replacement",
                "nested-group",
                "numbered-group",
                "pattern",
                "bytes",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the bound Pattern.subn nested-group callable replacement count path on the same bytes-numbered nested capture slice while broader callback helpers remain out of scope."
            ],
        },
        {
            "id": "module-sub-callable-nested-group-named-bytes",
            "operation": "module_call",
            "family": "named_nested_group_callable_replacement_workflow",
            "helper": "sub",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"a(?P<outer>(?P<inner>b))d",
                },
                {
                    "type": "callable_match_group",
                    "group": "outer",
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
                    "value": "abdabd",
                },
            ],
            "categories": [
                "workflow",
                "sub",
                "callable-replacement",
                "nested-group",
                "named-group",
                "module",
                "bytes",
                "gap",
            ],
            "notes": [
                "Publishes the bounded module-level named nested-group callable replacement path for one named outer capture containing one named inner capture with bytes payloads."
            ],
        },
        {
            "id": "module-subn-callable-nested-group-named-bytes",
            "operation": "module_call",
            "family": "named_nested_group_callable_replacement_workflow",
            "helper": "subn",
            "text_model": "bytes",
            "args": [
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": r"a(?P<outer>(?P<inner>b))d",
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
                    "value": "abdabd",
                },
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "callable-replacement",
                "nested-group",
                "named-group",
                "module",
                "bytes",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the bounded module-level named nested-group callable replacement count path for the inner named capture on bytes inputs without broadening into alternation or quantified groups."
            ],
        },
        {
            "id": "pattern-sub-callable-nested-group-named-bytes",
            "operation": "pattern_call",
            "family": "named_nested_group_callable_replacement_workflow",
            "pattern": r"a(?P<outer>(?P<inner>b))d",
            "helper": "sub",
            "text_model": "bytes",
            "args": [
                {
                    "type": "callable_match_group",
                    "group": "outer",
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
                    "value": "abdabd",
                },
            ],
            "categories": [
                "workflow",
                "sub",
                "callable-replacement",
                "nested-group",
                "named-group",
                "pattern",
                "bytes",
                "gap",
            ],
            "notes": [
                "Publishes the bound Pattern.sub named nested-group callable replacement path for the same one-site named nested capture shape on bytes payloads."
            ],
        },
        {
            "id": "pattern-subn-callable-nested-group-named-bytes",
            "operation": "pattern_call",
            "family": "named_nested_group_callable_replacement_workflow",
            "pattern": r"a(?P<outer>(?P<inner>b))d",
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
                    "value": "abdabd",
                },
                1,
            ],
            "categories": [
                "workflow",
                "subn",
                "callable-replacement",
                "nested-group",
                "named-group",
                "pattern",
                "bytes",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the bound Pattern.subn named nested-group callable replacement count path on the same bytes-named nested capture slice while broader callback helpers, alternation, and branch-local references remain out of scope."
            ],
        },
    ],
}
