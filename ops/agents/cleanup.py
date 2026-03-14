SPEC = {
    "name": "cleanup",
    "kind": "cleanup_worker",
    "description": "Removes duplicated or unnecessary code while preserving the repo's current behavioral state.",
    "enabled": True,
    "cycle_order": 60,
    "prompt_path": "ops/agents/cleanup.md",
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
