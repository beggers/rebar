MANIFEST = {
    "schema_version": 1,
    "manifest_id": "nested-group-alternation-wrapper-replacement-workflows",
    "layer": "module_workflow",
    "suite_id": "collection.replacement.nested_group_alternation.wrapper",
    "defaults": {
        "text_model": "str",
    },
    "cases": [
        {
            "id": "module-sub-template-nested-group-alternation-numbered-wrapper-str",
            "operation": "module_call",
            "family": "nested_group_alternation_wrapper_replacement_workflow",
            "helper": "sub",
            "args": ["a((b|c))d", "<\\1>", "abdacd"],
            "categories": [
                "workflow",
                "sub",
                "replacement-template",
                "wrapper-template",
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
                "Publishes the bounded module-level nested grouped-alternation wrapper-template path on `abdacd`, so the numbered outer capture stays visible inside `<\\\\1>` without widening into `\\\\1x`, inner captures, or callable replacements."
            ],
        },
        {
            "id": "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
            "operation": "pattern_call",
            "family": "named_nested_group_alternation_wrapper_replacement_workflow",
            "pattern": "a(?P<outer>(b|c))d",
            "helper": "subn",
            "args": ["<\\g<outer>>", "abdacd", 1],
            "categories": [
                "workflow",
                "subn",
                "replacement-template",
                "wrapper-template",
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
                "Publishes the bounded Pattern.subn named nested grouped-alternation wrapper-template first-match-only path on `abdacd`, so the named outer capture stays visible inside `<\\\\g<outer>>` while the later match remains untouched."
            ],
        },
    ],
}
