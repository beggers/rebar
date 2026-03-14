CONFIG = {
    "readme_path": "README.md",
    "capability_tracks": [
        {
            "label": "Drop-in `re` compatibility contract",
            "description": "Rust and CPython-extension target for bug-for-bug public API compatibility.",
            "paths_any": [
                "docs/spec/drop-in-re-compatibility.md",
            ],
            "task": "RBR-0000-rust-drop-in-target.md",
        },
        {
            "label": "Syntax compatibility scope",
            "description": "Initial parser compatibility document for regex syntax support.",
            "paths_any": [
                "docs/spec/syntax-scope.md",
            ],
            "task": "RBR-0001-initial-syntax-scope.md",
        },
        {
            "label": "Correctness plan",
            "description": "Plan for differential tests, fixtures, and parser assertions.",
            "paths_any": [
                "docs/testing/correctness-plan.md",
            ],
            "task": "RBR-0002-correctness-harness-plan.md",
        },
        {
            "label": "Benchmark methodology",
            "description": "Plan for compile, match, and module-boundary performance measurement against CPython.",
            "paths_any": [
                "docs/benchmarks/plan.md",
            ],
            "task": "RBR-0003-benchmark-plan.md",
        },
        {
            "label": "Rust parser crate scaffold",
            "description": "First tracked Rust crate or module tree for the parser.",
            "paths_any": [
                "crates/rebar-core/src/lib.rs",
            ],
            "task": "RBR-0005-rust-workspace-scaffold.md",
        },
        {
            "label": "CPython extension scaffold",
            "description": "Tracked extension module or Python packaging layer for importing as a replacement `re` implementation.",
            "paths_any": [
                "crates/rebar-cpython/src/lib.rs",
                "python/rebar/__init__.py",
                "pyproject.toml",
            ],
            "task": "RBR-0006-cpython-extension-scaffold.md",
        },
        {
            "label": "Automated conformance harness",
            "description": "Tracked correctness tests for parser behavior.",
            "paths_any": [
                "python/rebar_harness/correctness.py",
                "tests/conformance/test_correctness_smoke.py",
            ],
            "task": "RBR-0007-conformance-harness-scaffold.md",
        },
        {
            "label": "Automated benchmark harness",
            "description": "Tracked benchmark runner and workload manifest for parser and module-boundary measurements.",
            "paths_any": [
                "python/rebar_harness/benchmarks.py",
                "benchmarks/workloads/compile_smoke.py",
            ],
            "task": "RBR-0008-benchmark-harness-scaffold.md",
        },
        {
            "label": "Published correctness scorecard",
            "description": "Committed summary of correctness coverage and parity.",
            "paths_any": [
                "reports/correctness/latest.py",
            ],
            "task": "RBR-0007-conformance-harness-scaffold.md",
        },
        {
            "label": "Published benchmark scorecard",
            "description": "Committed summary of parser benchmark results.",
            "paths_any": [
                "reports/benchmarks/latest.py",
            ],
            "task": "RBR-0008-benchmark-harness-scaffold.md",
        },
    ],
    "correctness_scorecard": {
        "title": "Correctness Snapshot",
        "path": "reports/correctness/latest.py",
    },
    "benchmark_scorecard": {
        "title": "Benchmark Snapshot",
        "path": "reports/benchmarks/latest.py",
    },
    "status_sections": {
        "phase": "README Phase Summary",
        "delivery_estimate": "README Delivery Estimate",
        "next_steps": "README Next Steps",
        "risks": "README Risks",
    },
    "readme_limits": {
        "next_steps": 2,
        "risks": 2,
    },
}
