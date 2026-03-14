MANIFEST = {
    "schema_version": 1,
    "manifest_id": "literal-alternation-workflows",
    "layer": "match_behavior",
    "suite_id": "match.literal_alternation",
    "defaults": {
        "text_model": "str",
    },
    "cases": [
        {
            "id": "literal-alternation-compile-metadata-str",
            "operation": "compile",
            "family": "literal_alternation_compile_metadata",
            "pattern": "ab|ac",
            "categories": [
                "alternation",
                "literal",
                "compile",
                "metadata",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the next top-level branch-selection frontier for a tiny literal alternation shape without broadening into grouping, nested branches, or quantified alternation."
            ],
        },
        {
            "id": "literal-alternation-module-search-str",
            "operation": "module_call",
            "family": "literal_alternation_module_workflow",
            "helper": "search",
            "args": ["ab|ac", "zzaczz"],
            "categories": [
                "alternation",
                "literal",
                "search",
                "module",
                "str",
                "gap",
            ],
            "notes": [
                "Documents the module-level search path for the same bounded literal alternation so the next branch-selection execution gap is explicit in the published scorecard."
            ],
        },
        {
            "id": "literal-alternation-pattern-fullmatch-str",
            "operation": "pattern_call",
            "family": "literal_alternation_pattern_workflow",
            "pattern": "ab|ac",
            "helper": "fullmatch",
            "args": ["ac"],
            "categories": [
                "alternation",
                "literal",
                "fullmatch",
                "pattern",
                "str",
                "gap",
            ],
            "notes": [
                "Documents the bound Pattern.fullmatch path for tiny top-level literal alternation while leaving grouped alternation, nested branches, and broader backtracking out of scope."
            ],
        },
    ],
}
