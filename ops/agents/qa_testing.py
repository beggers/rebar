SPEC = {
    "name": "qa-testing",
    "kind": "quality_worker",
    "description": "Strengthens test coverage and brittleness resistance without changing the implementation.",
    "enabled": True,
    "cycle_order": 40,
    "prompt_path": "ops/agents/qa_testing.md",
    "dispatch": {
        "mode": "every_cycle",
        "allow_dirty_worktree": True,
        "timeout_seconds": 2700,
    },
    "codex": {
        "config": [
            'model_reasoning_effort="xhigh"',
        ],
    },
}
