from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
import unittest
from unittest import mock

from rebar_harness import benchmarks, correctness, scorecard_io
from tests.harness_cli_test_support import (
    REPO_ROOT,
    load_rebar_ops_module,
    run_harness_cli,
    run_harness_scorecard,
)


def completed_process(*args: str, returncode: int = 0, stdout: str = "", stderr: str = ""):
    return subprocess.CompletedProcess(args=args, returncode=returncode, stdout=stdout, stderr=stderr)


PARSER_FIXTURES_PATH = REPO_ROOT / "tests" / "conformance" / "fixtures" / "parser_matrix.py"
CORRECTNESS_REPORT_PATH = correctness.SCORECARD_REPORT.published_path
LEGACY_CORRECTNESS_REPORT_PATH = scorecard_io.retired_published_scorecard_sidecar_path(
    CORRECTNESS_REPORT_PATH
)
BENCHMARK_REPORT_PATH = benchmarks.SCORECARD_REPORT.published_path
LEGACY_BENCHMARK_REPORT_PATH = scorecard_io.retired_published_scorecard_sidecar_path(
    BENCHMARK_REPORT_PATH
)


class OpsHarnessTest(unittest.TestCase):
    def test_dispatch_policies_match_the_current_specialist_mix(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        agents = {agent.name: agent for agent in rebar_ops.load_agent_specs(config)}

        for name, interval_seconds in (
            ("cleanup", 7200),
            ("reporting", 3600),
            ("implementation-faithfulness", 10800),
        ):
            self.assertIn(name, agents)
            self.assertEqual(agents[name].dispatch["mode"], "interval")
            self.assertEqual(agents[name].dispatch["interval_seconds"], interval_seconds)

        for name in ("supervisor", "architecture", "feature-planning", "qa-testing"):
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

    def test_dirty_worktree_dispatch_is_limited_to_qa_and_cleanup(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        agents = {agent.name: agent for agent in rebar_ops.load_agent_specs(config)}

        for name in ("qa-testing", "cleanup"):
            with self.subTest(agent=name):
                self.assertTrue(agents[name].dispatch.get("allow_dirty_worktree"))
                self.assertTrue(rebar_ops.agent_may_dispatch_on_dirty_worktree(agents[name]))

        for name in (
            "architecture",
            "architecture-implementation",
            "feature-planning",
            "feature-implementation",
            "implementation-faithfulness",
            "reporting",
        ):
            with self.subTest(agent=name):
                self.assertFalse(agents[name].dispatch.get("allow_dirty_worktree", False))
                self.assertFalse(rebar_ops.agent_may_dispatch_on_dirty_worktree(agents[name]))

    def test_all_agents_use_xhigh_reasoning(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        agents = rebar_ops.load_agent_specs(config)

        for agent in agents:
            self.assertIn('model_reasoning_effort="xhigh"', agent.codex["config"])

    def test_loaded_agents_use_python_spec_modules(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        agents = rebar_ops.load_agent_specs(config)

        for agent in agents:
            with self.subTest(agent=agent.name):
                self.assertEqual(agent.spec_path.suffix, ".py")
                self.assertTrue(agent.spec_path.exists())

    def test_loop_and_readme_configs_load_from_python_modules(self) -> None:
        rebar_ops = load_rebar_ops_module()

        with mock.patch.object(
            rebar_ops,
            "read_json",
            side_effect=AssertionError("ops config should not use JSON parsing"),
        ):
            config = rebar_ops.load_config()
            reporting_cfg = rebar_ops.load_readme_reporting_config(config)

        self.assertEqual(rebar_ops.CONFIG_PATH.suffix, ".py")
        self.assertEqual(rebar_ops.README_REPORTING_CONFIG_PATH.suffix, ".py")
        self.assertEqual(config["reporting"]["readme_config_path"], "ops/reporting/readme.py")
        self.assertEqual(reporting_cfg["readme_path"], "README.md")
        self.assertEqual(
            rebar_ops.load_python_dict_attribute(
                rebar_ops.CONFIG_PATH,
                attribute="CONFIG",
                label="ops config",
            ),
            config,
        )
        self.assertEqual(
            rebar_ops.load_python_dict_attribute(
                rebar_ops.README_REPORTING_CONFIG_PATH,
                attribute="CONFIG",
                label="README reporting config",
            ),
            reporting_cfg,
        )

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

    def test_commit_summary_text_skips_leading_preamble_when_action_line_follows(self) -> None:
        rebar_ops = load_rebar_ops_module()

        summary = rebar_ops.commit_summary_text(
            """No tracked `.venv/` or `site-packages` tree was present, so I used this run on one bounded duplicate-plumbing cleanup instead.

I consolidated the duplicated scorecard read/write helpers into [scorecard_io.py](/tmp/scorecard_io.py).

Verified with `python -m unittest`.
"""
        )

        self.assertEqual(
            summary,
            "I consolidated the duplicated scorecard read/write helpers into scorecard_io.py",
        )

    def test_commit_summary_text_skips_markdown_section_heading(self) -> None:
        rebar_ops = load_rebar_ops_module()

        summary = rebar_ops.commit_summary_text(
            """**Changes**
- Seeded [RBR-0350](#/tmp/RBR-0350.md) as the next feature-implementation task.

**Verified**
- Queue state after the edit: `2` ready.
"""
        )

        self.assertEqual(
            summary,
            "Seeded RBR-0350 as the next feature-implementation task",
        )

    def test_commit_summary_text_skips_what_changed_heading_variant(self) -> None:
        rebar_ops = load_rebar_ops_module()

        summary = rebar_ops.commit_summary_text(
            """**What Changed**
- Added the wider ranged-repeat correctness manifest.

**Verified**
- `pytest -q`
"""
        )

        self.assertEqual(
            summary,
            "Added the wider ranged-repeat correctness manifest",
        )

    def test_commit_summary_text_skips_changed_heading_variant(self) -> None:
        rebar_ops = load_rebar_ops_module()

        summary = rebar_ops.commit_summary_text(
            """**Changed**
Centralized correctness fixture selection in [correctness.py](/tmp/correctness.py).

**Verification**
- `pytest -q`
"""
        )

        self.assertEqual(
            summary,
            "Centralized correctness fixture selection in correctness.py",
        )

    def test_commit_summary_text_keeps_bolded_action_line(self) -> None:
        rebar_ops = load_rebar_ops_module()

        summary = rebar_ops.commit_summary_text(
            """**Removed one JSON blob and simplified the benchmark loader.**

Verified with `python -m unittest`.
"""
        )

        self.assertEqual(
            summary,
            "Removed one JSON blob and simplified the benchmark loader",
        )

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
                spec_path=REPO_ROOT / "ops" / "agents" / "cleanup.py",
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

    def test_maybe_checkpoint_inherited_dirty_worktree_requires_prior_stall(self) -> None:
        rebar_ops = load_rebar_ops_module()
        supervisor = rebar_ops.AgentSpec(
            name="supervisor",
            kind="supervisor",
            description="",
            enabled=True,
            cycle_order=0,
            spec_path=REPO_ROOT / "ops" / "agents" / "supervisor.py",
            prompt_path=REPO_ROOT / "ops" / "agents" / "supervisor.md",
            dispatch={},
            codex={},
        )

        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.object(
            rebar_ops, "git_worktree_dirty", return_value=True
        ), mock.patch.object(rebar_ops, "git_run") as git_run_mock:
            action = rebar_ops.maybe_checkpoint_inherited_dirty_worktree(
                {"runtime": {"artifact_dir": temp_dir}},
                supervisor,
                {"last_cycle_anomalies": []},
            )

        self.assertIsNone(action)
        git_run_mock.assert_not_called()

    def test_maybe_checkpoint_inherited_dirty_worktree_commits_supervisor_recovery(self) -> None:
        rebar_ops = load_rebar_ops_module()
        supervisor = rebar_ops.AgentSpec(
            name="supervisor",
            kind="supervisor",
            description="",
            enabled=True,
            cycle_order=0,
            spec_path=REPO_ROOT / "ops" / "agents" / "supervisor.py",
            prompt_path=REPO_ROOT / "ops" / "agents" / "supervisor.md",
            dispatch={},
            codex={},
        )
        commit_messages: list[str] = []

        def fake_git_run(*args: str, **kwargs):
            if args == ("add", "-A"):
                return completed_process(*args)
            if args == ("commit", "-F", "-"):
                commit_messages.append(kwargs["input_text"])
                return completed_process(*args)
            raise AssertionError(f"Unexpected git invocation: {args}")

        loop_state = {
            "last_cycle_anomalies": [
                {
                    "type": "git_sync_error",
                    "message": (
                        "Skipped non-supervisor agent dispatch because the worktree was already "
                        "dirty before this cycle started and remained dirty before these agents "
                        "would have run: architecture, feature-implementation."
                    ),
                }
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.object(
            rebar_ops, "git_worktree_dirty", return_value=True
        ), mock.patch.object(
            rebar_ops, "git_run", side_effect=fake_git_run
        ), mock.patch.object(
            rebar_ops,
            "git_stdout",
            return_value="ops/tasks/done/RBR-0308.md\npython/rebar_harness/benchmarks.py\n",
        ), mock.patch.object(rebar_ops, "git_head", return_value="deadbeef"):
            action = rebar_ops.maybe_checkpoint_inherited_dirty_worktree(
                {
                    "runtime": {"artifact_dir": temp_dir},
                    "git_policy": {"command_timeout_seconds": 30},
                },
                supervisor,
                loop_state,
            )

        self.assertIsNotNone(action)
        assert action is not None
        self.assertTrue(action["commit_created"])
        self.assertEqual(action["commit_sha"], "deadbeef")
        self.assertEqual(
            action["subject"],
            rebar_ops.truncate_commit_subject(
                "supervisor: Checkpointed the inherited dirty worktree to unblock queue dispatch"
            ),
        )
        self.assertEqual(
            action["changed_files"],
            ["ops/tasks/done/RBR-0308.md", "python/rebar_harness/benchmarks.py"],
        )
        self.assertEqual(len(commit_messages), 1)
        self.assertIn("Agent: supervisor", commit_messages[0])
        self.assertIn("before the next dispatch attempt", commit_messages[0])
        self.assertIn("ops/tasks/done/RBR-0308.md", commit_messages[0])

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

    def test_update_loop_state_uses_live_agent_registry_after_supervisor_retune(self) -> None:
        rebar_ops = load_rebar_ops_module()
        supervisor = rebar_ops.AgentSpec(
            name="supervisor",
            kind="supervisor",
            description="",
            enabled=True,
            cycle_order=0,
            spec_path=REPO_ROOT / "ops" / "agents" / "supervisor.py",
            prompt_path=REPO_ROOT / "ops" / "agents" / "supervisor.md",
            dispatch={"mode": "every_cycle"},
            codex={},
        )
        reporting_cycle_start = rebar_ops.AgentSpec(
            name="reporting",
            kind="reporting_worker",
            description="",
            enabled=True,
            cycle_order=70,
            spec_path=REPO_ROOT / "ops" / "agents" / "reporting.py",
            prompt_path=REPO_ROOT / "ops" / "agents" / "reporting.md",
            dispatch={"mode": "every_cycle"},
            codex={},
        )
        reporting_live = rebar_ops.AgentSpec(
            name="reporting",
            kind="reporting_worker",
            description="",
            enabled=True,
            cycle_order=70,
            spec_path=REPO_ROOT / "ops" / "agents" / "reporting.py",
            prompt_path=REPO_ROOT / "ops" / "agents" / "reporting.md",
            dispatch={"mode": "interval", "interval_seconds": 3600},
            codex={},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"runtime": {"artifact_dir": temp_dir}}
            with mock.patch.object(
                rebar_ops,
                "load_agent_specs",
                return_value=[supervisor, reporting_live],
            ), mock.patch.object(
                rebar_ops,
                "queue_counts",
                return_value={"ready": 1, "in_progress": 0, "done": 374, "blocked": 0},
            ), mock.patch.object(
                rebar_ops,
                "tracked_json_blob_count",
                return_value=0,
            ), mock.patch.object(
                rebar_ops,
                "build_anomalies",
                return_value=[],
            ), mock.patch.object(
                rebar_ops,
                "utcnow",
                return_value="2026-03-15T08:00:00+00:00",
            ):
                state = rebar_ops.update_loop_state(
                    config,
                    [supervisor, reporting_cycle_start],
                    [],
                    [],
                    [],
                    {},
                    {},
                )

        registry = {item["name"]: item for item in state["agent_registry"]}
        self.assertEqual(registry["reporting"]["dispatch_mode"], "interval")

    def test_update_loop_state_progress_persists_interval_finished_at_for_partial_cycles(self) -> None:
        rebar_ops = load_rebar_ops_module()
        reporting = rebar_ops.AgentSpec(
            name="reporting",
            kind="reporting_worker",
            description="",
            enabled=True,
            cycle_order=70,
            spec_path=REPO_ROOT / "ops" / "agents" / "reporting.py",
            prompt_path=REPO_ROOT / "ops" / "agents" / "reporting.md",
            dispatch={"mode": "interval", "interval_seconds": 3600},
            codex={},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = pathlib.Path(temp_dir) / "runs" / "run-1"
            run_dir.mkdir(parents=True, exist_ok=True)
            result = rebar_ops.RunResult(
                agent_name="reporting",
                agent_kind="reporting_worker",
                run_id="run-1",
                exit_code=0,
                timed_out=False,
                run_dir=run_dir,
                task_initial_path=None,
                task_final_path=None,
                task_final_status=None,
            )

            with mock.patch.object(
                rebar_ops,
                "load_agent_specs",
                return_value=[reporting],
            ), mock.patch.object(
                rebar_ops,
                "queue_counts",
                return_value={"ready": 0, "in_progress": 0, "done": 504, "blocked": 0},
            ), mock.patch.object(
                rebar_ops,
                "utcnow",
                return_value="2999-01-01T00:00:00+00:00",
            ):
                state = rebar_ops.update_loop_state_progress(
                    {"runtime": {"artifact_dir": temp_dir}},
                    [result],
                )

        self.assertEqual(state["agents"]["reporting"]["run_id"], "run-1")
        self.assertEqual(state["agent_registry"][0]["dispatch_mode"], "interval")
        self.assertEqual(state["queue_counts"]["done"], 504)
        self.assertFalse(rebar_ops.agent_is_due(reporting, state))


class ReadmeReportingTest(unittest.TestCase):
    def test_correctness_cli_rejects_legacy_tracked_json_path(self) -> None:
        result = run_harness_cli(
            "rebar_harness.correctness",
            [
                "--fixtures",
                str(PARSER_FIXTURES_PATH),
                "--report",
                str(LEGACY_CORRECTNESS_REPORT_PATH),
            ],
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("reports/correctness/latest.json is a retired legacy", result.stderr)
        self.assertIn("reports/correctness/latest.py", result.stderr)
        self.assertIn("non-tracked temporary .json path", result.stderr)
        self.assertFalse(LEGACY_CORRECTNESS_REPORT_PATH.exists())

    def test_benchmark_cli_rejects_legacy_tracked_json_path(self) -> None:
        result = run_harness_cli(
            "rebar_harness.benchmarks",
            [
                "--report",
                str(LEGACY_BENCHMARK_REPORT_PATH),
            ],
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("reports/benchmarks/latest.json is a retired legacy", result.stderr)
        self.assertIn("reports/benchmarks/latest.py", result.stderr)
        self.assertIn("non-tracked temporary .json path", result.stderr)
        self.assertFalse(LEGACY_BENCHMARK_REPORT_PATH.exists())

    def test_refresh_published_correctness_scorecard_deletes_legacy_json_sidecar(self) -> None:
        rebar_ops = load_rebar_ops_module()
        original_payload = CORRECTNESS_REPORT_PATH.read_text(encoding="utf-8")

        try:
            LEGACY_CORRECTNESS_REPORT_PATH.write_text(
                json.dumps({"legacy": True}, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            refreshed = rebar_ops.refresh_published_correctness_scorecard()

            self.assertIsInstance(refreshed, dict)
            self.assertFalse(LEGACY_CORRECTNESS_REPORT_PATH.exists())

            repaired_payload = correctness.SCORECARD_REPORT.load(CORRECTNESS_REPORT_PATH)
            correctness_harness = rebar_ops.load_correctness_harness_module()
            expected_manifest_ids = [
                manifest.manifest_id
                for manifest in correctness_harness.published_fixture_manifests()
            ]
            self.assertEqual(
                repaired_payload["fixtures"]["manifest_count"],
                len(expected_manifest_ids),
            )
            self.assertEqual(
                repaired_payload["fixtures"]["manifest_ids"],
                expected_manifest_ids,
            )
        finally:
            CORRECTNESS_REPORT_PATH.write_text(original_payload, encoding="utf-8")
            LEGACY_CORRECTNESS_REPORT_PATH.unlink(missing_ok=True)

    def test_refresh_published_correctness_scorecard_repairs_narrowed_report(self) -> None:
        rebar_ops = load_rebar_ops_module()
        original_payload = CORRECTNESS_REPORT_PATH.read_text(encoding="utf-8")

        try:
            _, narrowed_scorecard = run_harness_scorecard(
                "rebar_harness.correctness",
                [
                    "--fixtures",
                    str(PARSER_FIXTURES_PATH),
                ],
                report_name="parser-only.json",
            )

            correctness.SCORECARD_REPORT.write(narrowed_scorecard, CORRECTNESS_REPORT_PATH)

            refreshed = rebar_ops.refresh_published_correctness_scorecard()
            self.assertIsInstance(refreshed, dict)

            repaired_payload = correctness.SCORECARD_REPORT.load(CORRECTNESS_REPORT_PATH)
            correctness_harness = rebar_ops.load_correctness_harness_module()
            expected_manifest_ids = [
                manifest.manifest_id
                for manifest in correctness_harness.published_fixture_manifests()
            ]
            self.assertEqual(
                repaired_payload["fixtures"]["manifest_count"],
                len(expected_manifest_ids),
            )
            self.assertEqual(
                repaired_payload["fixtures"]["manifest_ids"],
                expected_manifest_ids,
            )
            self.assertEqual(repaired_payload["summary"], refreshed["summary"])
        finally:
            CORRECTNESS_REPORT_PATH.write_text(original_payload, encoding="utf-8")

    def test_correctness_scorecard_uses_tracked_summary_shape(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        payload = correctness.SCORECARD_REPORT.load(CORRECTNESS_REPORT_PATH)
        summary = payload["summary"]

        expected_total = summary.get("cases_total", summary.get("total_cases"))
        expected_passed = summary.get(
            "cases_passed",
            summary.get("passed_cases", summary.get("passed")),
        )

        scorecard = rebar_ops.scorecard_from_config(
            config,
            "correctness_scorecard",
            "Correctness Scorecard",
            "reports/correctness/latest.py",
        )

        self.assertTrue(scorecard["available"])
        self.assertEqual(scorecard["cases_total"], expected_total)
        self.assertEqual(scorecard["cases_passed"], expected_passed)
        self.assertEqual(scorecard["candidate"], payload["baseline"]["target_module"])

        rendered = rebar_ops.render_readme_status(config)
        self.assertIn(f"| Published cases | `{expected_total}` |", rendered)
        self.assertIn(f"| Passing in published slice | `{expected_passed}` |", rendered)
        expected_unimplemented = summary.get(
            "cases_unimplemented",
            summary.get("unimplemented_cases", summary.get("unimplemented")),
        )
        self.assertIn(f"| Honest gaps (`unimplemented`) | `{expected_unimplemented}` |", rendered)
        self.assertIn("Overall delivery estimate:", rendered)
        self.assertIn("These correctness counts cover only the published slice.", rendered)
        self.assertIn("| Timing path | `source-tree-shim` |", rendered)
        self.assertIn("strict built-native smoke and full-suite modes remain available", rendered)
        self.assertIn("`--native-smoke`", rendered)
        self.assertIn("`--native-full`", rendered)
        self.assertIn("explicit `--report` path", rendered)
        self.assertNotIn("native_smoke.json", rendered)
        self.assertNotIn("native_full.json", rendered)

    def test_benchmark_scorecard_uses_tracked_summary_shape(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        payload = rebar_ops.read_structured_dict(
            BENCHMARK_REPORT_PATH,
            default=None,
            label="benchmark scorecard",
        )

        self.assertIsInstance(payload, dict)
        summary = payload["summary"]
        implementation = payload["implementation"]

        scorecard = rebar_ops.scorecard_from_config(
            config,
            "benchmark_scorecard",
            "Benchmark Snapshot",
            "reports/benchmarks/latest.py",
        )

        self.assertTrue(scorecard["available"])
        self.assertEqual(scorecard["workload_count"], summary["total_workloads"])
        self.assertEqual(scorecard["measured_workloads"], summary["measured_workloads"])
        self.assertEqual(scorecard["known_gap_count"], summary["known_gap_count"])
        self.assertEqual(scorecard["candidate"], implementation["module_name"])

        rendered = rebar_ops.render_readme_status(config)
        self.assertIn(f"| Published workloads | `{summary['total_workloads']}` |", rendered)
        self.assertIn(
            f"| Workloads with real `rebar` timings | `{summary['measured_workloads']}` |",
            rendered,
        )
        self.assertIn("reports/benchmarks/latest.py", rendered)
        self.assertNotIn("reports/benchmarks/latest.json", rendered)

    def test_benchmark_harness_loads_tracked_python_scorecard(self) -> None:
        payload = benchmarks.SCORECARD_REPORT.load(BENCHMARK_REPORT_PATH)

        self.assertIsInstance(payload, dict)
        self.assertEqual(payload["suite"], "benchmarks")
        self.assertEqual(payload["implementation"]["module_name"], "rebar")


if __name__ == "__main__":
    unittest.main()
