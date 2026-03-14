SPEC = {
    "name": "architecture-implementation",
    "kind": "task_worker",
    "description": "Consumes architecture-owned refactor tasks from the shared ready queue, one at a time.",
    "enabled": True,
    "cycle_order": 22,
    "prompt_path": "ops/agents/architecture_implementation.md",
    "dispatch": {
        "mode": "task_queue",
        "queue": "ready",
        "claim_to": "in_progress",
        "accepted_owners": [
            "architecture-implementation",
        ],
        "max_runs_per_cycle": 1,
        "require_write_probe": True,
        "environment_issue_backoff_seconds": 300,
        "probe_timeout_seconds": 120,
        "timeout_seconds": 2400,
    },
    "codex": {
        "config": [
            'model_reasoning_effort="xhigh"',
        ],
    },
}
