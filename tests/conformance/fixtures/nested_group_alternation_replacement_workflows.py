MANIFEST = {
    "schema_version": 1,
    "manifest_id": "nested-group-alternation-replacement-workflows",
    "layer": "module_workflow",
    "suite_id": "collection.replacement.nested_group_alternation",
    "defaults": {
        "text_model": "str",
    },
    "cases": [
        {
            "id": "module-sub-template-nested-group-alternation-numbered-outer-str",
            "operation": "module_call",
            "family": "nested_group_alternation_replacement_workflow",
            "helper": "sub",
            "args": ["a((b|c))d", "\\1x", "abdacd"],
            "categories": [
                "workflow",
                "sub",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "numbered-group",
                "outer-capture",
                "module",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the bounded module-level nested grouped-alternation replacement-template path on `abdacd`, so the numbered outer capture stays visible through `\\\\1x` without widening into wrapper templates, inner captures, or quantified branches."
            ],
        },
        {
            "id": "pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str",
            "operation": "pattern_call",
            "family": "named_nested_group_alternation_replacement_workflow",
            "pattern": "a(?P<outer>(b|c))d",
            "helper": "subn",
            "args": ["\\g<outer>x", "acdabd", 1],
            "categories": [
                "workflow",
                "subn",
                "replacement-template",
                "grouped",
                "nested-group",
                "alternation",
                "named-group",
                "outer-capture",
                "first-match-only",
                "pattern",
                "str",
                "count",
                "gap",
            ],
            "notes": [
                "Publishes the bounded Pattern.subn named nested grouped-alternation replacement-template first-match-only path on `acdabd`, so the named outer capture stays visible through `\\\\g<outer>x` while the later match remains untouched."
            ],
        },
    ],
}
