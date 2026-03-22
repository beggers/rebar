from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from rebar_harness import benchmarks, correctness, scorecard_io
import tests.conftest as test_support
from tests.conftest import REPO_ROOT, run_harness_cli, run_harness_scorecard


def completed_process(*args: str, returncode: int = 0, stdout: str = "", stderr: str = ""):
    return subprocess.CompletedProcess(args=args, returncode=returncode, stdout=stdout, stderr=stderr)


REBAR_OPS_MODULE_PATH = REPO_ROOT / "scripts" / "rebar_ops.py"


def load_rebar_ops_module(module_name: str = "rebar_ops_for_tests") -> object:
    spec = importlib.util.spec_from_file_location(module_name, REBAR_OPS_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {REBAR_OPS_MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARSER_FIXTURES_PATH = REPO_ROOT / "tests" / "conformance" / "fixtures" / "parser_matrix.py"
COMPILE_MATRIX_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
)
README_PATH = REPO_ROOT / "README.md"
CURRENT_STATUS_PATH = REPO_ROOT / "ops" / "state" / "current_status.md"
CORRECTNESS_REPORT_PATH = correctness.SCORECARD_REPORT.published_path
LEGACY_CORRECTNESS_REPORT_PATH = CORRECTNESS_REPORT_PATH.with_suffix(".json")
BENCHMARK_REPORT_PATH = benchmarks.SCORECARD_REPORT.published_path
LEGACY_BENCHMARK_REPORT_PATH = BENCHMARK_REPORT_PATH.with_suffix(".json")


DELIVERY_ESTIMATE_PATTERN = re.compile(
    r"Published correctness covers "
    r"(?P<correctness_cases>\d+) cases across "
    r"(?P<correctness_manifests>\d+) manifests, with all "
    r"(?P<correctness_passed>\d+) passing in the current slice; "
    r"the benchmark publication covers "
    r"(?P<benchmark_measured>\d+)/(?P<benchmark_total>\d+) measured workloads across "
    r"(?P<benchmark_manifests>\d+) manifests with "
    r"(?P<benchmark_known_gaps>\d+) known gap(?:s)?,"
)
COMPATIBILITY_HEURISTIC_PATTERN = re.compile(
    r"The published correctness slice now covers "
    r"(?P<correctness_cases>\d+) cases across "
    r"(?P<correctness_manifests>\d+) manifests, all passing, and "
    r"(?P<benchmark_measured>\d+) benchmark workloads are measured"
)


def _match_summary_line(pattern: re.Pattern[str], line: str) -> dict[str, int]:
    match = pattern.search(line)
    if match is None:
        raise AssertionError(f"summary line did not match expected shape: {line!r}")
    return {key: int(value) for key, value in match.groupdict().items()}


class OpsHarnessTest(unittest.TestCase):
    def test_dispatch_policies_match_the_current_specialist_mix(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        agents = {agent.name: agent for agent in rebar_ops.load_agent_specs(config)}

        for name, interval_seconds in (
            ("reporting", 3600),
            ("implementation-faithfulness", 21600),
        ):
            self.assertIn(name, agents)
            self.assertEqual(agents[name].dispatch["mode"], "interval")
            self.assertEqual(agents[name].dispatch["interval_seconds"], interval_seconds)

        for name in (
            "supervisor",
            "architecture",
            "feature-planning",
            "qa-testing",
            "cleanup",
        ):
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

    def test_enabled_agents_keep_single_supervisor_first_and_in_documented_order(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        agents = rebar_ops.load_agent_specs(config)

        self.assertEqual(
            tuple(agent.name for agent in agents),
            (
                "supervisor",
                "architecture",
                "architecture-implementation",
                "feature-planning",
                "feature-implementation",
                "qa-testing",
                "implementation-faithfulness",
                "cleanup",
                "reporting",
            ),
        )
        self.assertEqual(
            tuple(agent.cycle_order for agent in agents),
            (0, 20, 22, 25, 35, 40, 50, 60, 70),
        )
        self.assertEqual(
            [agent.name for agent in agents if agent.kind == "supervisor"],
            ["supervisor"],
        )

    def test_load_agent_specs_requires_exactly_one_enabled_supervisor(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        load_python_dict_attribute = rebar_ops.load_python_dict_attribute

        def mutate_specs(mode: str):
            def side_effect(
                spec_path: pathlib.Path,
                *,
                attribute: str,
                label: str,
            ) -> dict[str, object]:
                raw = dict(
                    load_python_dict_attribute(
                        spec_path,
                        attribute=attribute,
                        label=label,
                    )
                )
                if mode == "missing-enabled-supervisor" and spec_path.name == "supervisor.py":
                    raw["enabled"] = False
                if mode == "duplicate-enabled-supervisor" and spec_path.name == "architecture.py":
                    raw["kind"] = "supervisor"
                return raw

            return side_effect

        for mode in ("missing-enabled-supervisor", "duplicate-enabled-supervisor"):
            with self.subTest(mode=mode):
                with mock.patch.object(
                    rebar_ops,
                    "load_python_dict_attribute",
                    side_effect=mutate_specs(mode),
                ):
                    with self.assertRaisesRegex(
                        RuntimeError,
                        re.escape("Exactly one enabled supervisor agent spec is required."),
                    ):
                        rebar_ops.load_agent_specs(config)

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

    def test_all_agents_declare_supported_reasoning_effort(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        agents = rebar_ops.load_agent_specs(config)

        for agent in agents:
            with self.subTest(agent=agent.name):
                reasoning_settings = [
                    entry
                    for entry in agent.codex.get("config", [])
                    if entry.startswith('model_reasoning_effort="') and entry.endswith('"')
                ]
                self.assertEqual(len(reasoning_settings), 1)
                reasoning_effort = reasoning_settings[0].removeprefix(
                    'model_reasoning_effort="'
                ).removesuffix('"')
                self.assertIn(reasoning_effort, {"high", "xhigh"})

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

    def test_readme_reporting_capability_tracks_reference_live_repo_evidence_and_tasks(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        reporting_cfg = rebar_ops.load_readme_reporting_config(config)
        task_index = rebar_ops.task_queue_index()
        capability_tracks = reporting_cfg["capability_tracks"]

        self.assertEqual(len(capability_tracks), len({track["label"] for track in capability_tracks}))

        for track in capability_tracks:
            with self.subTest(track=track["label"]):
                self.assertTrue(track["label"].strip())
                self.assertTrue(track["description"].strip())
                self.assertTrue(track.get("paths_any") or track.get("globs_any"))

                for key in ("paths_any", "globs_any"):
                    for value in track.get(key, []):
                        self.assertIsInstance(value, str)
                        self.assertTrue(value)
                        self.assertFalse(pathlib.Path(value).is_absolute())

                matches = rebar_ops.matching_repo_paths(track)
                self.assertTrue(matches)
                self.assertTrue(all(path.is_file() for path in matches))
                self.assertTrue(all(path.is_relative_to(REPO_ROOT) for path in matches))

                task_name = track.get("task")
                self.assertIsInstance(task_name, str)
                self.assertIn(task_name, task_index)

    def test_matching_repo_paths_preserves_unique_order_across_paths_and_globs(self) -> None:
        rebar_ops = load_rebar_ops_module()

        entry = {
            "paths_any": [
                "README.md",
                "README.md",
                "missing-file-does-not-exist.md",
            ],
            "globs_any": [
                "README.md",
                "ops/reporting/readme.py",
                "README.md",
                "ops/reporting/*.py",
            ],
        }

        matches = rebar_ops.matching_repo_paths(entry)

        self.assertEqual(
            matches,
            [
                REPO_ROOT / "README.md",
                REPO_ROOT / "ops" / "reporting" / "readme.py",
            ],
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

    def test_commit_summary_text_summarizes_leading_absolute_repo_path(self) -> None:
        rebar_ops = load_rebar_ops_module()

        summary = rebar_ops.commit_summary_text(
            f"""**Changed**
- {REPO_ROOT / "tests" / "python" / "test_fixture_parity_support_contract.py"} no longer defines `_declared_nondefault_correctness_fixture_selectors()`.

**Verified**
- `pytest -q`
"""
        )

        self.assertEqual(
            summary,
            "Fixture parity support contract no longer defines _declared_nondefault_correctness_fixture_selectors()",
        )

    def test_commit_summary_text_summarizes_inline_absolute_repo_paths(self) -> None:
        rebar_ops = load_rebar_ops_module()

        summary = rebar_ops.commit_summary_text(
            f"Updated {REPO_ROOT / 'README.md'} and {REPO_ROOT / 'ops' / 'state' / 'current_status.md'} for one reporting coherence fix."
        )

        self.assertEqual(
            summary,
            "Updated README and Current status for one reporting coherence fix",
        )

    def test_commit_summary_text_prefers_first_sentence_of_action_line(self) -> None:
        rebar_ops = load_rebar_ops_module()

        summary = rebar_ops.commit_summary_text(
            f"""Updated {REPO_ROOT / 'README.md'} and {REPO_ROOT / 'ops' / 'state' / 'current_status.md'} to fix one reporting coherence drift. The published correctness totals now read 1522 cases across 114 manifests with 1522 passing.

Verified with `pytest -q`.
"""
        )

        self.assertEqual(
            summary,
            "Updated README and Current status to fix one reporting coherence drift",
        )

    def test_truncate_commit_subject_prefers_word_boundary(self) -> None:
        rebar_ops = load_rebar_ops_module()

        self.assertEqual(
            rebar_ops.truncate_commit_subject(
                "reporting: Updated README and Current status to fix one reporting coherence drift"
            ),
            "reporting: Updated README and Current status to fix one reporting...",
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

    def test_reroute_misplaced_user_asks_moves_queue_entries_into_supervisor_owned_dirs(
        self,
    ) -> None:
        rebar_ops = load_rebar_ops_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = pathlib.Path(temp_dir)
            task_root = repo_root / "ops" / "tasks"
            user_ask_root = repo_root / "ops" / "user_asks"
            for status in ("ready", "in_progress", "done", "blocked"):
                (task_root / status).mkdir(parents=True, exist_ok=True)
            for status in ("inbox", "done"):
                (user_ask_root / status).mkdir(parents=True, exist_ok=True)

            routed_files = {
                ("ready", "USER-ASK-1.md"): "needs supervisor intake\n",
                ("in_progress", "USER-ASK-2.md"): "still a supervisor ask\n",
                ("done", "USER-ASK-3.md"): "already handled\n",
                ("blocked", "USER-ASK-4.md"): "blocked user ask\n",
            }
            for (status, name), content in routed_files.items():
                (task_root / status / name).write_text(content, encoding="utf-8")

            ordinary_task = task_root / "ready" / "RBR-0001.md"
            ordinary_task.write_text("# Task\n\nStatus: ready\n", encoding="utf-8")

            with mock.patch.object(rebar_ops, "REPO_ROOT", repo_root), mock.patch.object(
                rebar_ops,
                "TASK_ROOT",
                task_root,
            ), mock.patch.object(rebar_ops, "USER_ASK_ROOT", user_ask_root):
                actions = rebar_ops.reroute_misplaced_user_asks()

            self.assertTrue(ordinary_task.exists())
            self.assertFalse((task_root / "ready" / "USER-ASK-1.md").exists())
            self.assertFalse((task_root / "in_progress" / "USER-ASK-2.md").exists())
            self.assertFalse((task_root / "done" / "USER-ASK-3.md").exists())
            self.assertFalse((task_root / "blocked" / "USER-ASK-4.md").exists())

            inbox_paths = (
                user_ask_root / "inbox" / "USER-ASK-1.md",
                user_ask_root / "inbox" / "USER-ASK-2.md",
            )
            done_paths = (
                user_ask_root / "done" / "USER-ASK-3.md",
                user_ask_root / "done" / "USER-ASK-4.md",
            )
            for path, expected_content in zip(
                (*inbox_paths, *done_paths),
                routed_files.values(),
                strict=True,
            ):
                self.assertTrue(path.exists())
                self.assertEqual(path.read_text(encoding="utf-8"), expected_content)

            self.assertEqual(
                actions,
                [
                    {
                        "task_name": "USER-ASK-1.md",
                        "action": "rerouted_misplaced_user_ask",
                        "severity": "warning",
                        "final_status": "inbox",
                        "path": "ops/user_asks/inbox/USER-ASK-1.md",
                    },
                    {
                        "task_name": "USER-ASK-2.md",
                        "action": "rerouted_misplaced_user_ask",
                        "severity": "warning",
                        "final_status": "inbox",
                        "path": "ops/user_asks/inbox/USER-ASK-2.md",
                    },
                    {
                        "task_name": "USER-ASK-3.md",
                        "action": "rerouted_misplaced_user_ask",
                        "severity": "warning",
                        "final_status": "done",
                        "path": "ops/user_asks/done/USER-ASK-3.md",
                    },
                    {
                        "task_name": "USER-ASK-4.md",
                        "action": "rerouted_misplaced_user_ask",
                        "severity": "warning",
                        "final_status": "done",
                        "path": "ops/user_asks/done/USER-ASK-4.md",
                    },
                ],
            )

    def test_reroute_misplaced_user_asks_deduplicates_existing_destination_names(self) -> None:
        rebar_ops = load_rebar_ops_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = pathlib.Path(temp_dir)
            task_root = repo_root / "ops" / "tasks"
            user_ask_root = repo_root / "ops" / "user_asks"
            for status in ("ready", "in_progress", "done", "blocked"):
                (task_root / status).mkdir(parents=True, exist_ok=True)
            for status in ("inbox", "done"):
                (user_ask_root / status).mkdir(parents=True, exist_ok=True)

            incoming = task_root / "ready" / "USER-ASK-7.md"
            incoming.write_text("fresh inbox note\n", encoding="utf-8")
            for existing_name in (
                "USER-ASK-7.md",
                "USER-ASK-7.md.from-ready",
                "USER-ASK-7.md.from-ready-2",
            ):
                (user_ask_root / "inbox" / existing_name).write_text(
                    f"{existing_name}\n",
                    encoding="utf-8",
                )

            with mock.patch.object(rebar_ops, "REPO_ROOT", repo_root), mock.patch.object(
                rebar_ops,
                "TASK_ROOT",
                task_root,
            ), mock.patch.object(rebar_ops, "USER_ASK_ROOT", user_ask_root):
                actions = rebar_ops.reroute_misplaced_user_asks()

            expected_path = user_ask_root / "inbox" / "USER-ASK-7.md.from-ready-3"
            self.assertFalse(incoming.exists())
            self.assertTrue(expected_path.exists())
            self.assertEqual(expected_path.read_text(encoding="utf-8"), "fresh inbox note\n")
            self.assertEqual(
                actions,
                [
                    {
                        "task_name": "USER-ASK-7.md",
                        "action": "rerouted_misplaced_user_ask",
                        "severity": "warning",
                        "final_status": "inbox",
                        "path": "ops/user_asks/inbox/USER-ASK-7.md.from-ready-3",
                    }
                ],
            )

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

    def test_reporting_same_cycle_refresh_skips_task_heavy_cycles(self) -> None:
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
        task_result = rebar_ops.RunResult(
            agent_name="feature-implementation",
            agent_kind="task_worker",
            run_id="run-1",
            exit_code=0,
            timed_out=False,
            run_dir=REPO_ROOT,
            task_initial_path="ops/tasks/in_progress/example.md",
            task_final_path="ops/tasks/done/example.md",
            task_final_status="done",
        )

        self.assertFalse(
            rebar_ops.reporting_needs_same_cycle_refresh(
                reporting,
                [{"changed_files": ["reports/correctness/latest.py"]}],
                [task_result],
            )
        )

    def test_reporting_same_cycle_refresh_keeps_quiet_cycle_report_sync(self) -> None:
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

        self.assertTrue(
            rebar_ops.reporting_needs_same_cycle_refresh(
                reporting,
                [{"changed_files": ["reports/correctness/latest.py"]}],
                [],
            )
        )


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

    def test_scorecard_build_cpython_baseline_reports_current_interpreter_shape(
        self,
    ) -> None:
        baseline = scorecard_io.build_cpython_baseline(version_family="3.12.x")

        self.assertEqual(baseline["python_version_family"], "3.12.x")
        self.assertEqual(
            baseline["python_implementation"].lower(),
            sys.implementation.name,
        )
        self.assertEqual(baseline["python_version"], sys.version.split()[0])
        self.assertEqual(set(baseline["python_build"]), {"name", "date"})
        self.assertIsInstance(baseline["python_build"]["name"], str)
        self.assertIsInstance(baseline["python_build"]["date"], str)
        self.assertIsInstance(baseline["python_compiler"], str)
        self.assertIsInstance(baseline["platform"], str)
        self.assertEqual(baseline["executable"], sys.executable)
        self.assertEqual(baseline["re_module"], "re")

    def test_scorecard_materialize_descriptor_value_materializes_nested_bytes_payloads(
        self,
    ) -> None:
        payload = {
            1: "alpha",
            "items": [
                "beta",
                {
                    "type": "bytes",
                    "encoding": "latin-1",
                    "value": "gamma",
                },
                {"nested": "delta"},
            ],
        }

        self.assertEqual(
            scorecard_io.materialize_descriptor_value(payload, text_model="bytes"),
            {
                "1": b"alpha",
                "items": [
                    b"beta",
                    b"gamma",
                    {"nested": b"delta"},
                ],
            },
        )

    def test_scorecard_materialize_descriptor_value_builds_indexlike_carriers(
        self,
    ) -> None:
        value = scorecard_io.materialize_descriptor_value(
            {"type": "indexlike", "value": 2}
        )

        self.assertEqual(type(value).__name__, "_IndexLike")
        self.assertEqual(value.__index__(), 2)
        self.assertEqual(repr(value), "IndexLike(2)")

    def test_scorecard_materialize_descriptor_value_rejects_invalid_indexlike_carriers(
        self,
    ) -> None:
        for invalid_value in (True, "2", 2.0, None):
            with self.subTest(value=invalid_value):
                with self.assertRaisesRegex(
                    ValueError,
                    re.escape("indexlike descriptor requires an integer `value`"),
                ):
                    scorecard_io.materialize_descriptor_value(
                        {"type": "indexlike", "value": invalid_value}
                    )

    def test_scorecard_materialize_descriptor_value_builds_tagged_callable_helpers(
        self,
    ) -> None:
        constant = scorecard_io.materialize_descriptor_value(
            {
                "type": "callable_constant",
                "value": "CONST",
            },
            text_model="bytes",
            callback_module_name="scorecard.contract",
        )
        match_group = scorecard_io.materialize_descriptor_value(
            {
                "type": "callable_match_group",
                "group": "word",
                "prefix": "<",
                "suffix": ">",
            },
            text_model="bytes",
            callback_module_name="scorecard.contract",
        )

        self.assertTrue(callable(constant))
        self.assertEqual(constant.__module__, "scorecard.contract")
        self.assertEqual(constant.__name__, "callable_constant")
        self.assertEqual(constant.__qualname__, "callable_constant")
        self.assertTrue(callable(match_group))
        self.assertEqual(match_group.__module__, "scorecard.contract")
        self.assertEqual(match_group.__name__, "callable_match_group")
        self.assertEqual(match_group.__qualname__, "callable_match_group")

        match = re.search(br"(?P<word>abc)", b"abc")
        self.assertIsNotNone(match)
        self.assertEqual(constant(match), b"CONST")
        self.assertEqual(match_group(match), b"<abc>")

    def test_scorecard_materialize_descriptor_value_defaults_callable_match_group_to_whole_match(
        self,
    ) -> None:
        match_group = scorecard_io.materialize_descriptor_value(
            {"type": "callable_match_group"},
            text_model="bytes",
        )
        match = re.search(br"abc", b"zzabczz")

        self.assertIsNotNone(match)
        self.assertEqual(match_group(match), b"abc")

    def test_scorecard_materialize_descriptor_value_rejects_unsupported_text_model(
        self,
    ) -> None:
        with self.assertRaisesRegex(ValueError, r"unsupported text model 'utf-16'"):
            scorecard_io.materialize_descriptor_value("abc", text_model="utf-16")

    def test_scorecard_format_python_module_round_trips_through_python_loader(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            scorecard = {
                "schema_version": "1.0",
                "totals": {"cases": 3, "passed": 3},
                "manifests": [{"manifest_id": "fixture-pack", "count": 3}],
            }
            report_path = temp_path / "latest.py"
            report_path.write_text(
                scorecard_io.format_python_scorecard_module(
                    scorecard,
                    report_attribute="REPORT",
                ),
                encoding="utf-8",
            )

            self.assertTrue(
                report_path.read_text(encoding="utf-8").startswith("REPORT = ")
            )
            self.assertEqual(
                scorecard_io.load_python_dict_attribute(
                    report_path,
                    module_name_prefix="_scorecard_io_contract",
                    attribute_name="REPORT",
                    load_error_label="Python correctness scorecard",
                    missing_error_label="Python correctness scorecard module",
                    type_error_label="correctness scorecard",
                ),
                scorecard,
            )

    def test_scorecard_report_round_trips_for_supported_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            scorecard = {
                "schema_version": "1.0",
                "environment": {"python": "3.12.3"},
                "totals": {"cases": 4, "passed": 4},
            }
            descriptor = scorecard_io.build_scorecard_report_descriptor(
                published_path=temp_path / "tracked.py",
                scorecard_kind="correctness",
            )

            for suffix in (".py", ".json"):
                with self.subTest(suffix=suffix):
                    report_path = temp_path / f"latest{suffix}"
                    descriptor.write(scorecard, report_path)

                    if suffix == ".json":
                        self.assertEqual(
                            json.loads(report_path.read_text(encoding="utf-8")),
                            scorecard,
                        )
                    else:
                        self.assertTrue(
                            report_path.read_text(encoding="utf-8").startswith(
                                "REPORT = "
                            )
                        )

                    self.assertEqual(
                        descriptor.load(report_path),
                        scorecard,
                    )

    def test_scorecard_load_unique_record_collection_preserves_record_order(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            manifest_a = temp_path / "manifest_a.py"
            manifest_b = temp_path / "manifest_b.py"
            records_by_path = {
                manifest_a: {
                    "id": "manifest-a",
                    "path": temp_path / "published_manifest_a.py",
                    "case_ids": ("case-a-1", "case-a-2"),
                },
                manifest_b: {
                    "id": "manifest-b",
                    "path": temp_path / "published_manifest_b.py",
                    "case_ids": ("case-b-1",),
                },
            }

            records = scorecard_io.load_unique_record_collection(
                (manifest_a, manifest_b),
                load_record=lambda path: dict(records_by_path[path]),
                record_id=lambda record: str(record["id"]),
                record_path=lambda record: pathlib.Path(str(record["path"])),
                duplicate_record_error=lambda record_id, first_path, second_path: (
                    f"duplicate record {record_id}: {first_path} vs {second_path}"
                ),
                nested_ids=lambda record: tuple(str(case_id) for case_id in record["case_ids"]),
                duplicate_nested_error=lambda nested_id, first_path, second_path: (
                    f"duplicate nested {nested_id}: {first_path} vs {second_path}"
                ),
            )

            self.assertEqual(
                [record["id"] for record in records],
                ["manifest-a", "manifest-b"],
            )
            self.assertEqual(
                [record["path"] for record in records],
                [
                    temp_path / "published_manifest_a.py",
                    temp_path / "published_manifest_b.py",
                ],
            )

    def test_scorecard_load_unique_record_collection_rejects_duplicate_record_ids(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            manifest_a = temp_path / "manifest_a.py"
            manifest_b = temp_path / "manifest_b.py"
            published_a = temp_path / "published_manifest_a.py"
            published_b = temp_path / "published_manifest_b.py"
            records_by_path = {
                manifest_a: {
                    "id": "duplicate-manifest",
                    "path": published_a,
                    "case_ids": ("case-a-1",),
                },
                manifest_b: {
                    "id": "duplicate-manifest",
                    "path": published_b,
                    "case_ids": ("case-b-1",),
                },
            }

            with self.assertRaisesRegex(
                ValueError,
                re.escape(
                    f"duplicate record duplicate-manifest: {published_a} vs {published_b}"
                ),
            ):
                scorecard_io.load_unique_record_collection(
                    (manifest_a, manifest_b),
                    load_record=lambda path: dict(records_by_path[path]),
                    record_id=lambda record: str(record["id"]),
                    record_path=lambda record: pathlib.Path(str(record["path"])),
                    duplicate_record_error=lambda record_id, first_path, second_path: (
                        f"duplicate record {record_id}: {first_path} vs {second_path}"
                    ),
                    nested_ids=lambda record: tuple(
                        str(case_id) for case_id in record["case_ids"]
                    ),
                    duplicate_nested_error=lambda nested_id, first_path, second_path: (
                        f"duplicate nested {nested_id}: {first_path} vs {second_path}"
                    ),
                )

    def test_scorecard_load_unique_record_collection_rejects_duplicate_nested_ids(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            manifest_a = temp_path / "manifest_a.py"
            manifest_b = temp_path / "manifest_b.py"
            published_a = temp_path / "published_manifest_a.py"
            published_b = temp_path / "published_manifest_b.py"
            records_by_path = {
                manifest_a: {
                    "id": "manifest-a",
                    "path": published_a,
                    "case_ids": ("shared-case",),
                },
                manifest_b: {
                    "id": "manifest-b",
                    "path": published_b,
                    "case_ids": ("shared-case",),
                },
            }

            with self.assertRaisesRegex(
                ValueError,
                re.escape(f"duplicate nested shared-case: {published_a} vs {published_b}"),
            ):
                scorecard_io.load_unique_record_collection(
                    (manifest_a, manifest_b),
                    load_record=lambda path: dict(records_by_path[path]),
                    record_id=lambda record: str(record["id"]),
                    record_path=lambda record: pathlib.Path(str(record["path"])),
                    duplicate_record_error=lambda record_id, first_path, second_path: (
                        f"duplicate record {record_id}: {first_path} vs {second_path}"
                    ),
                    nested_ids=lambda record: tuple(
                        str(case_id) for case_id in record["case_ids"]
                    ),
                    duplicate_nested_error=lambda nested_id, first_path, second_path: (
                        f"duplicate nested {nested_id}: {first_path} vs {second_path}"
                    ),
                )

    def test_run_harness_scorecard_loads_python_correctness_reports(self) -> None:
        summary, scorecard = run_harness_scorecard(
            "rebar_harness.correctness",
            [
                "--fixtures",
                str(PARSER_FIXTURES_PATH),
            ],
            report_name="parser-only.py",
        )

        self.assertEqual(scorecard["suite"], "correctness")
        self.assertEqual(
            scorecard["fixtures"]["path"],
            str(PARSER_FIXTURES_PATH.relative_to(REPO_ROOT)),
        )
        self.assertEqual(scorecard["fixtures"]["manifest_id"], "parser-matrix")
        self.assertEqual(scorecard["summary"], summary)

    def test_run_harness_scorecard_loads_python_benchmark_reports(self) -> None:
        summary, scorecard = run_harness_scorecard(
            "rebar_harness.benchmarks",
            [
                "--manifest",
                str(COMPILE_MATRIX_MANIFEST_PATH),
            ],
            report_name="compile-matrix.py",
        )

        self.assertEqual(scorecard["suite"], "benchmarks")
        self.assertEqual(
            scorecard["artifacts"]["manifest"],
            str(COMPILE_MATRIX_MANIFEST_PATH.relative_to(REPO_ROOT)),
        )
        self.assertEqual(scorecard["artifacts"]["manifest_id"], "compile-matrix")
        self.assertEqual(
            {key: scorecard["summary"][key] for key in summary},
            summary,
        )

    def test_run_harness_scorecard_loads_json_reports_for_generic_modules(self) -> None:
        summary_payload = {"suite": "custom", "status": "ok"}
        scorecard_payload = {
            "suite": "custom",
            "summary": summary_payload,
            "details": {"workloads": 3},
        }
        observed_cli_args: tuple[str, ...] | None = None

        def fake_run_harness_cli(
            module_name: str,
            cli_args: list[str],
            *,
            check: bool = True,
        ) -> subprocess.CompletedProcess[str]:
            nonlocal observed_cli_args

            self.assertEqual(module_name, "custom.scorecard.module")
            self.assertTrue(check)
            observed_cli_args = tuple(cli_args)
            report_index = observed_cli_args.index("--report")
            report_path = pathlib.Path(observed_cli_args[report_index + 1])
            report_path.write_text(json.dumps(scorecard_payload), encoding="utf-8")
            return completed_process(
                module_name,
                *observed_cli_args,
                stdout=json.dumps(summary_payload),
            )

        with mock.patch.object(
            test_support,
            "run_harness_cli",
            side_effect=fake_run_harness_cli,
        ):
            summary, scorecard = run_harness_scorecard(
                "custom.scorecard.module",
                ["--selector", "focused"],
                report_name="custom-scorecard.json",
            )

        self.assertEqual(summary, summary_payload)
        self.assertEqual(scorecard, scorecard_payload)
        assert observed_cli_args is not None
        self.assertEqual(observed_cli_args[:2], ("--selector", "focused"))
        self.assertEqual(observed_cli_args[2], "--report")
        self.assertTrue(observed_cli_args[3].endswith("custom-scorecard.json"))

    def test_run_harness_scorecard_rejects_non_json_reports_for_unknown_modules(
        self,
    ) -> None:
        summary_payload = {"suite": "custom", "status": "ok"}

        def fake_run_harness_cli(
            module_name: str,
            cli_args: list[str],
            *,
            check: bool = True,
        ) -> subprocess.CompletedProcess[str]:
            self.assertEqual(module_name, "custom.scorecard.module")
            self.assertTrue(check)
            observed_cli_args = tuple(cli_args)
            report_index = observed_cli_args.index("--report")
            report_path = pathlib.Path(observed_cli_args[report_index + 1])
            report_path.write_text("REPORT = {'suite': 'custom'}\n", encoding="utf-8")
            return completed_process(
                module_name,
                *observed_cli_args,
                stdout=json.dumps(summary_payload),
            )

        with mock.patch.object(
            test_support,
            "run_harness_cli",
            side_effect=fake_run_harness_cli,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "run_harness_scorecard cannot load a non-JSON report for "
                "'custom.scorecard.module'",
            ):
                run_harness_scorecard(
                    "custom.scorecard.module",
                    ["--selector", "focused"],
                    report_name="custom-scorecard.py",
                )

    def test_scorecard_report_loaders_and_writers_reject_malformed_inputs(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            descriptor = scorecard_io.build_scorecard_report_descriptor(
                published_path=temp_path / "tracked.py",
                scorecard_kind="correctness",
            )
            missing_attribute_path = temp_path / "missing.py"
            missing_attribute_path.write_text("NOT_REPORT = {}\n", encoding="utf-8")
            wrong_type_python_path = temp_path / "wrong_type.py"
            wrong_type_python_path.write_text("REPORT = []\n", encoding="utf-8")
            wrong_type_json_path = temp_path / "wrong_type.json"
            wrong_type_json_path.write_text('["not-a-dict"]\n', encoding="utf-8")
            unsupported_input_path = temp_path / "latest.txt"
            unsupported_input_path.write_text("REPORT = {}\n", encoding="utf-8")
            unsupported_output_path = temp_path / "written.txt"

            with self.assertRaises(ValueError) as missing_attribute_raised:
                descriptor.load(missing_attribute_path)
            self.assertEqual(
                str(missing_attribute_raised.exception),
                f"Python correctness scorecard module {missing_attribute_path} is missing a REPORT value",
            )

            with self.assertRaises(ValueError) as wrong_type_python_raised:
                descriptor.load(wrong_type_python_path)
            self.assertEqual(
                str(wrong_type_python_raised.exception),
                f"correctness scorecard in {wrong_type_python_path} must be a dict",
            )

            with self.assertRaises(ValueError) as wrong_type_json_raised:
                descriptor.load(wrong_type_json_path)
            self.assertEqual(
                str(wrong_type_json_raised.exception),
                f"correctness scorecard in {wrong_type_json_path} must be a dict",
            )

            with self.assertRaises(ValueError) as unsupported_input_raised:
                descriptor.load(unsupported_input_path)
            self.assertEqual(
                str(unsupported_input_raised.exception),
                f"unsupported correctness scorecard extension '.txt' for {unsupported_input_path}",
            )

            with self.assertRaises(ValueError) as unsupported_output_raised:
                descriptor.write({"schema_version": "1.0"}, unsupported_output_path)
            self.assertEqual(
                str(unsupported_output_raised.exception),
                f"unsupported correctness scorecard extension '.txt' for {unsupported_output_path}",
            )

    def test_scorecard_report_descriptor_resolves_optional_paths_and_rejects_retired_path(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            reports_root = temp_path / "reports" / "correctness"
            reports_root.mkdir(parents=True)
            published_path = reports_root / "latest.py"
            legacy_report_path = published_path.with_suffix(".json")
            descriptor = scorecard_io.build_scorecard_report_descriptor(
                published_path=published_path,
                scorecard_kind="correctness",
            )

            with mock.patch.object(pathlib.Path, "cwd", return_value=temp_path):
                self.assertEqual(descriptor.report_attribute, "REPORT")
                self.assertEqual(
                    descriptor.module_name_prefix,
                    "_rebar_correctness_scorecard",
                )
                self.assertIsNone(descriptor.resolve_optional_path(None))
                self.assertEqual(
                    descriptor.resolve_optional_path(
                        pathlib.Path("reports/correctness/latest.py")
                    ),
                    published_path.resolve(),
                )

                with self.assertRaises(ValueError) as retired_path_raised:
                    descriptor.resolve_optional_path(
                        pathlib.Path("reports/correctness/latest.json")
                    )
                self.assertEqual(
                    str(retired_path_raised.exception),
                    "reports/correctness/latest.json is a retired legacy published scorecard path; "
                    "use reports/correctness/latest.py for the tracked published scorecard or a "
                    "non-tracked temporary .json path for scratch output.",
                )

                self.assertEqual(
                    descriptor.validate_path(pathlib.Path("reports/correctness/latest.py")),
                    published_path.resolve(),
                )
            self.assertEqual(legacy_report_path, reports_root / "latest.json")

    def test_scorecard_report_descriptor_accepts_non_retired_json_scratch_paths(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            reports_root = temp_path / "reports" / "correctness"
            reports_root.mkdir(parents=True)
            published_path = reports_root / "latest.py"
            descriptor = scorecard_io.build_scorecard_report_descriptor(
                published_path=published_path,
                scorecard_kind="correctness",
            )
            sibling_scratch_path = reports_root / "latest.scratch.json"
            nested_scratch_path = reports_root / "scratch" / "run.json"

            with mock.patch.object(pathlib.Path, "cwd", return_value=temp_path):
                self.assertEqual(
                    descriptor.resolve_optional_path(
                        pathlib.Path("reports/correctness/latest.scratch.json")
                    ),
                    sibling_scratch_path.resolve(),
                )
                self.assertEqual(
                    descriptor.resolve_optional_path(
                        pathlib.Path("reports/correctness/scratch/run.json")
                    ),
                    nested_scratch_path.resolve(),
                )

    def test_scorecard_report_descriptor_honors_custom_attribute_and_module_prefix(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            reports_root = temp_path / "reports" / "benchmarks"
            reports_root.mkdir(parents=True)
            published_path = reports_root / "latest.py"
            descriptor = scorecard_io.build_scorecard_report_descriptor(
                published_path=published_path,
                scorecard_kind="benchmark",
                report_attribute="BENCHMARK_REPORT",
                module_name_prefix="_custom_benchmark_scorecard",
            )
            scorecard = {
                "schema_version": "1.0",
                "summary": {"workloads": 3},
            }

            descriptor.write(scorecard, published_path.resolve())

            self.assertEqual(descriptor.report_attribute, "BENCHMARK_REPORT")
            self.assertEqual(
                descriptor.module_name_prefix,
                "_custom_benchmark_scorecard",
            )
            self.assertTrue(
                published_path.read_text(encoding="utf-8").startswith(
                    "BENCHMARK_REPORT = "
                )
            )
            self.assertEqual(descriptor.load(published_path), scorecard)

    def test_scorecard_report_descriptor_normalizes_string_and_user_paths(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            reports_root = temp_path / "reports" / "benchmarks"
            reports_root.mkdir(parents=True)
            published_path = reports_root / "latest.py"
            descriptor = scorecard_io.build_scorecard_report_descriptor(
                published_path=published_path,
                scorecard_kind="benchmark",
            )

            with mock.patch.object(pathlib.Path, "cwd", return_value=temp_path):
                with mock.patch.dict("os.environ", {"HOME": str(temp_path)}):
                    self.assertEqual(
                        descriptor.validate_path("reports/benchmarks/latest.py"),
                        published_path.resolve(),
                    )
                    self.assertEqual(
                        descriptor.validate_path("~/scratch/run.json"),
                        (temp_path / "scratch" / "run.json").resolve(),
                    )
                    with self.assertRaises(ValueError) as retired_path_raised:
                        descriptor.validate_path("~/reports/benchmarks/latest.json")

            self.assertEqual(
                str(retired_path_raised.exception),
                "reports/benchmarks/latest.json is a retired legacy published "
                "scorecard path; use reports/benchmarks/latest.py for the tracked "
                "published scorecard or a non-tracked temporary .json path for "
                "scratch output.",
            )

    def test_scorecard_report_descriptor_writes_reports_without_touching_legacy_json_sibling(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            reports_root = temp_path / "reports" / "correctness"
            reports_root.mkdir(parents=True)
            published_path = reports_root / "latest.py"
            legacy_report_path = published_path.with_suffix(".json")
            scratch_path = temp_path / "scratch-scorecard.json"
            descriptor = scorecard_io.build_scorecard_report_descriptor(
                published_path=published_path,
                scorecard_kind="correctness",
            )
            scorecard = {
                "schema_version": "1.0",
                "totals": {"cases": 2, "passed": 2},
            }

            legacy_payload = "{}\n"
            legacy_report_path.write_text(legacy_payload, encoding="utf-8")
            descriptor.write(scorecard, scratch_path.resolve())

            self.assertTrue(scratch_path.is_file())
            self.assertEqual(descriptor.load(scratch_path), scorecard)
            self.assertTrue(legacy_report_path.is_file())
            self.assertEqual(
                legacy_report_path.read_text(encoding="utf-8"),
                legacy_payload,
            )

            descriptor.write(scorecard, published_path.resolve())

            self.assertEqual(descriptor.load(published_path), scorecard)
            self.assertTrue(legacy_report_path.exists())
            self.assertEqual(
                legacy_report_path.read_text(encoding="utf-8"),
                legacy_payload,
            )

    def test_scorecard_report_descriptor_preserves_non_retired_json_siblings_when_publishing(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            reports_root = temp_path / "reports" / "correctness"
            reports_root.mkdir(parents=True)
            published_path = reports_root / "latest.py"
            legacy_report_path = published_path.with_suffix(".json")
            scratch_sibling_path = reports_root / "latest.scratch.json"
            descriptor = scorecard_io.build_scorecard_report_descriptor(
                published_path=published_path,
                scorecard_kind="correctness",
            )
            scorecard = {
                "schema_version": "1.0",
                "totals": {"cases": 2, "passed": 2},
            }

            legacy_report_path.write_text("{}\n", encoding="utf-8")
            scratch_sibling_path.write_text(
                json.dumps({"scratch": True}, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            descriptor.write(scorecard, published_path.resolve())

            self.assertEqual(descriptor.load(published_path), scorecard)
            self.assertTrue(legacy_report_path.exists())
            self.assertTrue(scratch_sibling_path.is_file())
            self.assertEqual(
                json.loads(scratch_sibling_path.read_text(encoding="utf-8")),
                {"scratch": True},
            )

    def test_refresh_published_correctness_scorecard_ignores_legacy_json_sidecar_when_current(
        self,
    ) -> None:
        rebar_ops = load_rebar_ops_module()
        original_payload = CORRECTNESS_REPORT_PATH.read_text(encoding="utf-8")

        try:
            correctness_harness = rebar_ops.load_correctness_harness_module()
            legacy_payload = json.dumps({"legacy": True}, indent=2, sort_keys=True) + "\n"
            LEGACY_CORRECTNESS_REPORT_PATH.write_text(
                legacy_payload,
                encoding="utf-8",
            )

            self.assertFalse(
                rebar_ops.published_correctness_report_needs_refresh(correctness_harness)
            )

            refreshed = rebar_ops.refresh_published_correctness_scorecard()

            self.assertIsNone(refreshed)
            self.assertTrue(LEGACY_CORRECTNESS_REPORT_PATH.exists())
            self.assertEqual(
                LEGACY_CORRECTNESS_REPORT_PATH.read_text(encoding="utf-8"),
                legacy_payload,
            )
            self.assertEqual(
                CORRECTNESS_REPORT_PATH.read_text(encoding="utf-8"),
                original_payload,
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
        self.assertIn(
            f"| Honest gaps (`unimplemented`) | `{expected_unimplemented}` |",
            rendered,
        )
        self.assertIn("Overall delivery estimate:", rendered)
        self.assertIn("These correctness counts cover only the published slice.", rendered)
        self.assertIn("| Timing path | `source-tree-shim` |", rendered)
        self.assertIn(
            "strict built-native smoke and full-suite modes remain available",
            rendered,
        )
        self.assertIn("`--native-smoke`", rendered)
        self.assertIn("`--native-full`", rendered)
        self.assertIn("explicit `--report` path", rendered)
        self.assertNotIn("native_smoke.json", rendered)
        self.assertNotIn("native_full.json", rendered)

    def test_current_status_readme_summaries_do_not_overstate_live_scorecard_counts(
        self,
    ) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        status_sections = rebar_ops.markdown_sections(CURRENT_STATUS_PATH)
        rendered_status = rebar_ops.render_readme_status(config)
        correctness_scorecard = rebar_ops.scorecard_from_config(
            config,
            "correctness_scorecard",
            "Correctness Scorecard",
            "reports/correctness/latest.py",
        )
        benchmark_payload = benchmarks.SCORECARD_REPORT.load(BENCHMARK_REPORT_PATH)
        benchmark_summary = benchmark_payload["summary"]
        benchmark_manifest_count = len(benchmark_payload["manifests"])

        delivery_estimate = rebar_ops.first_nonempty_line(
            status_sections["README Delivery Estimate"]
        )
        delivery_counts = _match_summary_line(DELIVERY_ESTIMATE_PATTERN, delivery_estimate)
        self.assertLessEqual(
            delivery_counts["correctness_cases"], correctness_scorecard["cases_total"]
        )
        self.assertLessEqual(
            delivery_counts["correctness_manifests"],
            correctness_scorecard["case_manifest_count"],
        )
        self.assertLessEqual(
            delivery_counts["correctness_passed"], correctness_scorecard["cases_passed"]
        )
        self.assertLessEqual(
            delivery_counts["correctness_passed"], delivery_counts["correctness_cases"]
        )
        self.assertLessEqual(
            delivery_counts["benchmark_measured"], benchmark_summary["measured_workloads"]
        )
        self.assertLessEqual(
            delivery_counts["benchmark_total"], benchmark_summary["total_workloads"]
        )
        self.assertLessEqual(
            delivery_counts["benchmark_manifests"], benchmark_manifest_count
        )
        self.assertGreaterEqual(
            delivery_counts["benchmark_known_gaps"], benchmark_summary["known_gap_count"]
        )
        self.assertLessEqual(
            delivery_counts["benchmark_measured"], delivery_counts["benchmark_total"]
        )

        rendered_delivery_match = re.search(
            DELIVERY_ESTIMATE_PATTERN,
            rendered_status,
        )
        self.assertIsNotNone(rendered_delivery_match)
        rendered_delivery_counts = {
            key: int(value)
            for key, value in rendered_delivery_match.groupdict().items()
        }
        self.assertLessEqual(
            rendered_delivery_counts["correctness_cases"],
            correctness_scorecard["cases_total"],
        )
        self.assertLessEqual(
            rendered_delivery_counts["correctness_manifests"],
            correctness_scorecard["case_manifest_count"],
        )
        self.assertLessEqual(
            rendered_delivery_counts["correctness_passed"],
            correctness_scorecard["cases_passed"],
        )
        self.assertLessEqual(
            rendered_delivery_counts["benchmark_measured"],
            benchmark_summary["measured_workloads"],
        )
        self.assertLessEqual(
            rendered_delivery_counts["benchmark_total"],
            benchmark_summary["total_workloads"],
        )
        self.assertLessEqual(
            rendered_delivery_counts["benchmark_manifests"],
            benchmark_manifest_count,
        )
        self.assertGreaterEqual(
            rendered_delivery_counts["benchmark_known_gaps"],
            benchmark_summary["known_gap_count"],
        )
        self.assertLessEqual(
            rendered_delivery_counts["benchmark_measured"],
            rendered_delivery_counts["benchmark_total"],
        )

        compatibility_heuristic = rebar_ops.first_nonempty_line(
            status_sections["Compatibility Heuristic"]
        )
        compatibility_counts = _match_summary_line(
            COMPATIBILITY_HEURISTIC_PATTERN,
            compatibility_heuristic,
        )
        self.assertLessEqual(
            compatibility_counts["correctness_cases"], correctness_scorecard["cases_total"]
        )
        self.assertLessEqual(
            compatibility_counts["correctness_manifests"],
            correctness_scorecard["case_manifest_count"],
        )
        self.assertLessEqual(
            compatibility_counts["benchmark_measured"], benchmark_summary["measured_workloads"]
        )

    def test_checked_in_readme_status_block_keeps_expected_section_scaffold(self) -> None:
        rebar_ops = load_rebar_ops_module()
        current = README_PATH.read_text(encoding="utf-8")
        self.assertEqual(current.count(rebar_ops.README_STATUS_START), 1)
        self.assertEqual(current.count(rebar_ops.README_STATUS_END), 1)

        _, remainder = current.split(rebar_ops.README_STATUS_START, 1)
        status_block, _ = remainder.split(rebar_ops.README_STATUS_END, 1)

        self.assertIn("## Current State", status_block)
        self.assertIn("### Correctness Snapshot", status_block)
        self.assertIn("### Benchmark Snapshot", status_block)
        self.assertIn("### Immediate Next Steps", status_block)
        self.assertIn("### Current Risks", status_block)
        self.assertIn("reports/correctness/latest.py", status_block)
        self.assertIn("reports/benchmarks/latest.py", status_block)
        self.assertNotIn("reports/correctness/latest.json", status_block)
        self.assertNotIn("reports/benchmarks/latest.json", status_block)

    def test_replace_markdown_block_only_mutates_the_delimited_readme_status_region(
        self,
    ) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        current = README_PATH.read_text(encoding="utf-8")
        rendered_status = rebar_ops.render_readme_status(config)
        expected = rebar_ops.replace_markdown_block(
            current,
            rebar_ops.README_STATUS_START,
            rebar_ops.README_STATUS_END,
            rendered_status,
        )

        current_prefix, current_remainder = current.split(rebar_ops.README_STATUS_START, 1)
        _, current_suffix = current_remainder.split(rebar_ops.README_STATUS_END, 1)
        expected_prefix, expected_remainder = expected.split(rebar_ops.README_STATUS_START, 1)
        expected_block, expected_suffix = expected_remainder.split(
            rebar_ops.README_STATUS_END, 1
        )
        normalized_rendered_status = rendered_status.rstrip("\n")

        self.assertEqual(expected_prefix, current_prefix)
        self.assertEqual(expected_suffix, current_suffix)
        self.assertEqual(expected_block, f"\n{normalized_rendered_status}\n")

    def test_benchmark_scorecard_uses_tracked_summary_shape(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        payload = benchmarks.SCORECARD_REPORT.load(BENCHMARK_REPORT_PATH)

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
