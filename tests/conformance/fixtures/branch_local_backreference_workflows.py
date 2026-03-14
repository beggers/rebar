MANIFEST = {
    "schema_version": 1,
    "manifest_id": "branch-local-backreference-workflows",
    "layer": "match_behavior",
    "suite_id": "match.branch_local_backreference",
    "defaults": {
        "text_model": "str",
    },
    "cases": [
        {
            "id": "branch-local-numbered-backreference-compile-metadata-str",
            "operation": "compile",
            "family": "branch_local_numbered_backreference_compile_metadata",
            "pattern": "a((b)|c)\\2d",
            "categories": [
                "grouped",
                "alternation",
                "numbered-backreference",
                "branch-local",
                "compile",
                "metadata",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the bounded numbered branch-local backreference compile frontier for one alternation whose second capture only exists on one branch and is referenced after the branch closes."
            ],
        },
        {
            "id": "branch-local-numbered-backreference-module-search-str",
            "operation": "module_call",
            "family": "branch_local_numbered_backreference_module_workflow",
            "helper": "search",
            "args": ["a((b)|c)\\2d", "zzabbdzz"],
            "categories": [
                "grouped",
                "alternation",
                "numbered-backreference",
                "branch-local",
                "search",
                "module",
                "str",
                "gap",
            ],
            "notes": [
                "Documents the module-level numbered branch-local backreference search path for the same tiny literal workflow without broadening into replacement, quantified branches, or broader backtracking."
            ],
        },
        {
            "id": "branch-local-numbered-backreference-pattern-fullmatch-str",
            "operation": "pattern_call",
            "family": "branch_local_numbered_backreference_pattern_workflow",
            "pattern": "a((b)|c)\\2d",
            "helper": "fullmatch",
            "args": ["abbd"],
            "categories": [
                "grouped",
                "alternation",
                "numbered-backreference",
                "branch-local",
                "fullmatch",
                "pattern",
                "str",
                "gap",
            ],
            "notes": [
                "Documents the bound Pattern.fullmatch numbered branch-local backreference path for the same single alternation site wrapped by literal prefix and suffix text."
            ],
        },
        {
            "id": "branch-local-named-backreference-compile-metadata-str",
            "operation": "compile",
            "family": "branch_local_named_backreference_compile_metadata",
            "pattern": "a(?P<outer>(?P<inner>b)|c)(?P=inner)d",
            "categories": [
                "grouped",
                "alternation",
                "named-group",
                "named-backreference",
                "branch-local",
                "compile",
                "metadata",
                "str",
                "gap",
            ],
            "notes": [
                "Publishes the matching named branch-local backreference compile frontier where one named inner capture exists only on one alternation branch and is referenced after the branch."
            ],
        },
        {
            "id": "branch-local-named-backreference-module-search-str",
            "operation": "module_call",
            "family": "branch_local_named_backreference_module_workflow",
            "helper": "search",
            "args": [
                "a(?P<outer>(?P<inner>b)|c)(?P=inner)d",
                "zzabbdzz",
            ],
            "categories": [
                "grouped",
                "alternation",
                "named-group",
                "named-backreference",
                "branch-local",
                "search",
                "module",
                "str",
                "gap",
            ],
            "notes": [
                "Documents the module-level named branch-local backreference search path so the next combined alternation-and-reference gap is explicit in the published scorecard."
            ],
        },
        {
            "id": "branch-local-named-backreference-pattern-fullmatch-str",
            "operation": "pattern_call",
            "family": "branch_local_named_backreference_pattern_workflow",
            "pattern": "a(?P<outer>(?P<inner>b)|c)(?P=inner)d",
            "helper": "fullmatch",
            "args": ["abbd"],
            "categories": [
                "grouped",
                "alternation",
                "named-group",
                "named-backreference",
                "branch-local",
                "fullmatch",
                "pattern",
                "str",
                "gap",
            ],
            "notes": [
                "Documents the bound Pattern.fullmatch named branch-local backreference path without claiming replacement, callable replacement, quantified branches, or conditionals."
            ],
        },
    ],
}
