# RBR-0666: Collapse the detached harness CLI test support onto its owner suites

Status: ready
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Delete `tests/harness_cli_test_support.py` by moving its tiny `rebar_ops` loader plus harness CLI/scorecard helpers onto the three suites that actually consume them, so harness CLI coverage lives with its owner tests instead of a detached wrapper module beside those owners.

## Deliverables
- `tests/python/test_ops_harness.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- Delete `tests/harness_cli_test_support.py`

## Acceptance Criteria
- `tests/python/test_ops_harness.py` becomes the sole owner for the direct ops-harness helper surface currently imported from `tests/harness_cli_test_support.py`:
  - keep `REPO_ROOT`, any file-local Python-source or `scripts/rebar_ops.py` path constants, `load_rebar_ops_module(...)`, `run_harness_cli(...)`, and `run_harness_scorecard(...)` defined directly on `tests/python/test_ops_harness.py`;
  - preserve the current helper behavior exactly:
    - `load_rebar_ops_module(...)` still loads `scripts/rebar_ops.py` through `importlib.util.spec_from_file_location(...)`;
    - `run_harness_cli(...)` still shells out through `sys.executable -m <module>`, runs with `cwd=REPO_ROOT`, and passes `env={"PYTHONPATH": str(PYTHON_SOURCE)}`;
    - `run_harness_scorecard(...)` still writes an explicit temporary report path, parses the CLI stdout summary as JSON, and loads the emitted scorecard JSON from disk; and
    - the owner file no longer imports anything from `tests.harness_cli_test_support`.
- `tests/conformance/test_combined_correctness_scorecards.py` becomes the sole owner for its harness-rerun helper currently imported from `tests/harness_cli_test_support.py`:
  - keep a file-local `run_harness_scorecard(...)` helper on the correctness owner, plus only the tiniest local `run_harness_cli(...)` or temp-report helper needed to support it;
  - preserve the current helper contract for the correctness CLI reruns that regenerate temporary scorecards for this suite's assertions; and
  - the owner file no longer imports anything from `tests.harness_cli_test_support`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` becomes the sole owner for its harness-rerun helper currently imported from `tests/harness_cli_test_support.py`:
  - keep a file-local `run_harness_scorecard(...)` helper on the benchmark owner, plus only the tiniest local `run_harness_cli(...)` or temp-report helper needed to support it;
  - preserve the current helper contract for the benchmark CLI reruns that regenerate temporary scorecards for this suite's assertions; and
  - the owner file no longer imports anything from `tests.harness_cli_test_support`.
- `tests/harness_cli_test_support.py` is deleted outright:
  - do not leave an import-only wrapper, compatibility shell, new `*_support.py` replacement, or a migrated helper layer in `tests/conftest.py` or `tests/python/conftest.py`;
  - do not make the combined correctness or benchmark owners import these helpers from `tests/python/test_ops_harness.py`; keep any tiny helper each owner needs file-local instead.
- Keep scope structural only:
  - do not change `python/rebar_harness/correctness.py`, `python/rebar_harness/benchmarks.py`, `python/rebar_harness/scorecard_io.py`, `scripts/rebar_ops.py`, published reports, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_ops_harness.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

ops = Path("tests/python/test_ops_harness.py").read_text(encoding="utf-8")
correctness = Path("tests/conformance/test_combined_correctness_scorecards.py").read_text(
    encoding="utf-8"
)
benchmarks = Path(
    "tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"
).read_text(encoding="utf-8")

for needle in (
    "def load_rebar_ops_module(",
    "def run_harness_cli(",
    "def run_harness_scorecard(",
):
    assert needle in ops, needle
assert "from tests.harness_cli_test_support import" not in ops

for label, source in (
    ("correctness", correctness),
    ("benchmarks", benchmarks),
):
    assert "def run_harness_scorecard(" in source, label
    assert "from tests.harness_cli_test_support import" not in source, label
print("ok")
PY`
  - `bash -lc "! rg -n 'from tests\\.harness_cli_test_support import' tests -g '*.py'"`
  - `bash -lc "! rg --files tests | rg 'harness_cli_test_support\\.py$'"`

## Constraints
- Keep this cleanup structural only. The point is to delete a detached helper module, not to reinterpret CLI scorecard behavior, subprocess wiring, temp-file handling, or report semantics.
- Prefer the three existing owner suites and tiny file-local helpers over another shared support layer.
- Do not move this helper surface into runtime code under `python/rebar_harness/` or `scripts/rebar_ops.py`; it stays test-only.
- Preserve the current subprocess environment, temp-report naming flow, and stdout-summary parsing behavior exactly.

## Notes
- `RBR-0666` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0666|RBR-0667|RBR-0668|RBR-0669|RBR-0670" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returns only historical mentions inside done-task notes, with no reserved future id or live queued task in that range; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0665*' -o -name 'RBR-0666*' -o -name 'RBR-0667*' -o -name 'RBR-0668*' -o -name 'RBR-0669*' -o -name 'RBR-0670*' \) | sort` currently returns only `ops/tasks/ready/RBR-0665-nested-broader-range-wider-ranged-repeat-branch-local-backreference-callable-replacement-bytes-benchmark-catch-up.md`.
- No blocked architecture task exists to reopen first, and rule 10 does not currently block another architecture cleanup:
  - `ops/tasks/blocked/` currently contains only `.gitkeep`;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the dashboard `HEAD` (`80ab76c834fb00c61302ab4acfd94bafbab219e4`) matches `git rev-parse HEAD`, so the runtime view is not lagging behind this checkout.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `.rebar/runtime/loop_state.json` reports `tracked_json_blob_count: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached helper layer is concrete and bounded in the current checkout:
  - `wc -l tests/harness_cli_test_support.py tests/python/test_ops_harness.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` reports `60` lines for the detached helper module, `1057` lines for the ops-harness owner, `3667` lines for the combined correctness owner, and `4423` lines for the combined benchmark owner;
  - `rg -n "from tests\\.harness_cli_test_support import" tests -g '*.py'` currently matches only `tests/python/test_ops_harness.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_ops_harness.py` currently passes (`32 passed, 19 subtests passed in 1.85s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently passes (`58 passed, 2924 subtests passed in 54.72s`);
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: def load_rebar_ops_module(` because the owner files do not yet carry the absorbed helper definitions and still import `tests.harness_cli_test_support`; and
  - both `bash -lc "! rg -n 'from tests\\.harness_cli_test_support import' tests -g '*.py'"` and `bash -lc "! rg --files tests | rg 'harness_cli_test_support\\.py$'"` currently fail exactly on this cleanup because the detached helper module and its imports still exist.
- The ownership simplification matches the current info-flow boundaries:
  - `tests/python/test_ops_harness.py` already owns direct `scripts/rebar_ops.py` loading and the harness/report CLI contract;
  - `tests/conformance/test_combined_correctness_scorecards.py` already owns correctness scorecard reruns and tracked correctness publication assertions; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already owns source-tree benchmark scorecard reruns and tracked benchmark publication assertions.
