SPEC = {
    "name": "reporting",
    "kind": "reporting_worker",
    "description": "Keeps the README accurate, high-level, and aligned with the project’s actual stage.",
    "enabled": True,
    "cycle_order": 70,
    "prompt_path": "ops/agents/reporting.md",
    "dispatch": {
        "mode": "interval",
        "interval_seconds": 3600,
        "allow_dirty_worktree": True,
        "timeout_seconds": 1800,
    },
    "codex": {
        "config": [
            'model_reasoning_effort="xhigh"',
        ],
    },
}
