SPEC = {
    "name": "architecture",
    "kind": "analysis_worker",
    "description": "Analyzes architecture and information flow, then queues bounded simplification and rearchitecture tasks.",
    "enabled": True,
    "cycle_order": 20,
    "prompt_path": "ops/agents/architecture.md",
    "dispatch": {
        "mode": "interval",
        "interval_seconds": 3600,
        "timeout_seconds": 2700,
    },
    "codex": {
        "config": [
            'model_reasoning_effort="xhigh"',
        ],
    },
}
