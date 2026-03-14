CONFIG = {
    "runtime": {
        "artifact_dir": ".rebar/runtime",
        "queue_refill_sleep_seconds": 5,
        "sleep_seconds": 300,
        "failure_backoff_seconds": 30,
        "default_timeout_seconds": 1800,
        "keep_run_dirs": 200,
    },
    "task_recovery": {
        "state_path": ".rebar/runtime/task_state.json",
        "max_requeues": 2,
        "block_on_clean_exit_without_terminal_state": True,
    },
    "git_policy": {
        "auto_push": True,
        "push_remote": "origin",
        "push_branch": "main",
        "command_timeout_seconds": 30,
        "push_timeout_seconds": 120,
    },
    "reporting": {
        "status_json_path": ".rebar/runtime/dashboard.json",
        "status_markdown_path": ".rebar/runtime/dashboard.md",
        "readme_config_path": "ops/reporting/readme.py",
        "recent_runs": 12,
        "recent_tasks": 10,
        "recent_commits": 10,
    },
    "agents": {
        "directory": "ops/agents",
    },
    "codex_defaults": {
        "bin": "codex",
        "codex_home": "~/.codex",
        "dangerously_bypass_approvals_and_sandbox": True,
        "sandbox": "danger-full-access",
        "ask_for_approval": "never",
        "common_config": [
            "suppress_unstable_features_warning=true",
        ],
        "extra_env": {
            "CODEX_NO_UPDATE": "1",
        },
    },
}
