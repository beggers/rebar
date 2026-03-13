from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "rebar_ops.py"


def load_rebar_ops_module():
    spec = importlib.util.spec_from_file_location("rebar_ops_harness_tests", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def completed_process(*args: str, returncode: int = 0, stdout: str = "", stderr: str = ""):
    return subprocess.CompletedProcess(args=args, returncode=returncode, stdout=stdout, stderr=stderr)


class OpsHarnessTest(unittest.TestCase):
    def test_architecture_cleanup_and_qa_agents_run_every_cycle(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        agents = {agent.name: agent for agent in rebar_ops.load_agent_specs(config)}

        for name in ("architecture", "cleanup", "qa-testing"):
            self.assertIn(name, agents)
            self.assertEqual(agents[name].dispatch["mode"], "every_cycle")
            self.assertNotIn("interval_seconds", agents[name].dispatch)

    def test_architecture_implementation_agent_is_owner_routed_task_worker(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        agents = {agent.name: agent for agent in rebar_ops.load_agent_specs(config)}

        self.assertIn("architecture-implementation", agents)
        architecture_worker = agents["architecture-implementation"]
        self.assertEqual(architecture_worker.kind, "task_worker")
        self.assertEqual(architecture_worker.dispatch["mode"], "task_queue")
        self.assertEqual(
            architecture_worker.dispatch["accepted_owners"],
            ["architecture-implementation"],
        )

    def test_all_agents_use_xhigh_reasoning(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        agents = rebar_ops.load_agent_specs(config)

        for agent in agents:
            self.assertIn('model_reasoning_effort="xhigh"', agent.codex["config"])

    def test_render_prompt_includes_generated_commit_policy(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        agents = {agent.name: agent for agent in rebar_ops.load_agent_specs(config)}

        prompt = rebar_ops.render_prompt(agents["cleanup"], config)

        self.assertIn("Commit policy:", prompt)
        self.assertIn(
            "the harness will commit them immediately after your run",
            prompt,
        )
        self.assertIn("<agent-name>: <brief description>", prompt)

    def test_owner_routed_task_claims_select_only_matching_owner(self) -> None:
        rebar_ops = load_rebar_ops_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            task_root = pathlib.Path(temp_dir)
            for status in ("ready", "in_progress", "done", "blocked"):
                (task_root / status).mkdir(parents=True, exist_ok=True)

            architecture_task = task_root / "ready" / "A-architecture.md"
            architecture_task.write_text(
                "# A\n\nStatus: ready\nOwner: architecture-implementation\n",
                encoding="utf-8",
            )
            feature_task = task_root / "ready" / "B-feature.md"
            feature_task.write_text(
                "# B\n\nStatus: ready\nOwner: feature-implementation\n",
                encoding="utf-8",
            )

            with mock.patch.object(rebar_ops, "TASK_ROOT", task_root):
                claimed = rebar_ops.claim_tasks(
                    "ready",
                    "in_progress",
                    1,
                    {"architecture-implementation"},
                )

            self.assertEqual([path.name for path in claimed], ["A-architecture.md"])
            self.assertFalse(architecture_task.exists())
            self.assertTrue((task_root / "in_progress" / "A-architecture.md").exists())
            self.assertTrue(feature_task.exists())

    def test_maybe_commit_agent_changes_uses_agent_named_subject_and_detailed_body(self) -> None:
        rebar_ops = load_rebar_ops_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = pathlib.Path(temp_dir)
            (run_dir / "last_message.md").write_text(
                "Removed one JSON blob and simplified the benchmark loader.\n\n"
                "Verification passed for the touched benchmark tests.\n",
                encoding="utf-8",
            )
            agent = rebar_ops.AgentSpec(
                name="cleanup",
                kind="cleanup_worker",
                description="",
                enabled=True,
                cycle_order=60,
                spec_path=REPO_ROOT / "ops" / "agents" / "cleanup.json",
                prompt_path=REPO_ROOT / "ops" / "agents" / "cleanup.md",
                dispatch={},
                codex={},
            )
            result = rebar_ops.RunResult(
                agent_name="cleanup",
                agent_kind="cleanup_worker",
                run_id="run-1",
                exit_code=0,
                timed_out=False,
                run_dir=run_dir,
                task_initial_path=pathlib.Path("ops/tasks/in_progress/RBR-9999-cleanup.md"),
                task_final_path=pathlib.Path("ops/tasks/done/RBR-9999-cleanup.md"),
                task_final_status="done",
            )

            commit_messages: list[str] = []

            def fake_git_run(*args: str, **kwargs):
                if args == ("add", "-A"):
                    return completed_process(*args)
                if args == ("commit", "-F", "-"):
                    commit_messages.append(kwargs["input_text"])
                    return completed_process(*args)
                raise AssertionError(f"Unexpected git invocation: {args}")

            with mock.patch.object(rebar_ops, "git_worktree_dirty", return_value=True), mock.patch.object(
                rebar_ops, "git_run", side_effect=fake_git_run
            ), mock.patch.object(
                rebar_ops, "git_stdout", return_value="python/rebar_harness/benchmarks.py\n"
            ), mock.patch.object(rebar_ops, "git_head", return_value="abc123"):
                action = rebar_ops.maybe_commit_agent_changes(
                    {"git_policy": {"command_timeout_seconds": 30}},
                    agent,
                    [result],
                    [],
                )

            self.assertIsNotNone(action)
            assert action is not None
            self.assertTrue(action["commit_created"])
            self.assertEqual(action["commit_sha"], "abc123")
            self.assertEqual(action["subject"], "cleanup: Removed one JSON blob and simplified the benchmark loader")
            self.assertEqual(len(commit_messages), 1)
            self.assertIn("Agent: cleanup", commit_messages[0])
            self.assertIn("Changed files:", commit_messages[0])
            self.assertIn("python/rebar_harness/benchmarks.py", commit_messages[0])
            self.assertIn("Details:", commit_messages[0])
            self.assertIn("Verification passed for the touched benchmark tests.", commit_messages[0])

    def test_maybe_commit_and_push_merges_upstream_before_push_when_diverged(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = {
            "git_policy": {
                "auto_push": True,
                "push_remote": "origin",
                "push_branch": "main",
                "command_timeout_seconds": 30,
                "push_timeout_seconds": 120,
            }
        }

        counts = iter(((2, 1), (3, 0)))
        git_calls: list[tuple[str, ...]] = []

        def fake_git_run(*args: str, **kwargs):
            del kwargs
            git_calls.append(args)
            if args == ("fetch", "origin", "main"):
                return completed_process(*args)
            if args == ("merge", "--no-edit", "origin/main"):
                return completed_process(*args, stdout="Merge made by the 'ort' strategy.\n")
            if args == ("push", "origin", "main"):
                return completed_process(*args)
            raise AssertionError(f"Unexpected git invocation: {args}")

        with mock.patch.object(rebar_ops, "git_run", side_effect=fake_git_run), mock.patch.object(
            rebar_ops, "git_worktree_dirty", return_value=False
        ), mock.patch.object(
            rebar_ops, "git_ahead_behind_counts", side_effect=lambda _config: next(counts)
        ), mock.patch.object(rebar_ops, "git_head", return_value="deadbeef"):
            action = rebar_ops.maybe_commit_and_push(config)

        self.assertEqual(
            git_calls,
            [
                ("fetch", "origin", "main"),
                ("merge", "--no-edit", "origin/main"),
                ("push", "origin", "main"),
            ],
        )
        self.assertTrue(action["fetch_attempted"])
        self.assertTrue(action["fetch_succeeded"])
        self.assertTrue(action["merge_attempted"])
        self.assertTrue(action["merge_succeeded"])
        self.assertEqual(action["ahead_before_push"], 2)
        self.assertEqual(action["behind_before_push"], 1)
        self.assertEqual(action["ahead_after_merge"], 3)
        self.assertEqual(action["behind_after_merge"], 0)
        self.assertTrue(action["push_attempted"])
        self.assertTrue(action["push_succeeded"])
        self.assertEqual(action["errors"], [])


if __name__ == "__main__":
    unittest.main()
