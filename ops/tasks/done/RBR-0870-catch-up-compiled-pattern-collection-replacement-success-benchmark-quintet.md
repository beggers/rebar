# RBR-0870: Catch up the compiled-pattern collection/replacement success benchmark quintet

Status: done
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the adjacent compiled-pattern-first-argument direct-success `split()` / `findall()` / `finditer()` / `sub()` / `subn()` quintet that the shared `module-workflow-surface` correctness path already publishes, reusing the bounded compiled-pattern module-helper timing path already present on the shared collection/replacement owner route instead of widening the benchmark runner or opening another manifest family.

## Pattern Pair
- `re.compile("abc")` through `split(re.compile("abc"), "zzabczzabc", 1)`, `finditer(re.compile("abc"), "zabcabc")`, and `sub(re.compile("abc"), "x", "zabcabc", 1)`
- `re.compile(b"abc")` through `findall(re.compile(b"abc"), b"zabcabc")` and `subn(re.compile(b"abc"), b"x", b"zabcabc", 1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly five compiled-pattern-first-argument direct-success workloads:
  - add `module-split-literal-warm-str-compiled-pattern`;
  - add `module-findall-literal-purged-bytes-compiled-pattern`;
  - add `module-finditer-literal-warm-str-compiled-pattern`;
  - add `module-sub-literal-warm-str-compiled-pattern`; and
  - add `module-subn-literal-purged-bytes-compiled-pattern`.
- Keep those five workloads pinned to the exact already-published module-workflow compiled-pattern anchors rather than inventing a broader helper family:
  - `module-split-literal-warm-str-compiled-pattern` uses `operation == "module.split"`, `pattern == "abc"`, `haystack == "zzabczzabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, `maxsplit == 1`, and no `expected_exception`;
  - `module-findall-literal-purged-bytes-compiled-pattern` uses `operation == "module.findall"`, `pattern == "abc"`, `haystack == "zabcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - `module-finditer-literal-warm-str-compiled-pattern` uses `operation == "module.finditer"`, `pattern == "abc"`, `haystack == "zabcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - `module-sub-literal-warm-str-compiled-pattern` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zabcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, `count == 1`, and no `expected_exception`; and
  - `module-subn-literal-purged-bytes-compiled-pattern` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zabcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, `count == 1`, and no `expected_exception`.
- Keep this quintet on the shared collection/replacement owner path and do not broaden beyond the exact adjacent compiled-pattern direct-success slice:
  - anchor the five workloads to `workflow-module-split-str-compiled-pattern`, `workflow-module-findall-bytes-compiled-pattern`, `workflow-module-finditer-str-compiled-pattern`, `workflow-module-sub-str-compiled-pattern`, and `workflow-module-subn-bytes-compiled-pattern`;
  - keep the shared `collection_replacement_boundary.py` manifest as the only benchmark manifest for this slice;
  - keep all existing raw-module, compiled-pattern keyword, compiled-pattern wrong-text-model, and direct-`Pattern` collection/replacement rows unchanged; and
  - do not widen into keyword carriers, keyword errors, wrong-text-model rows, replacement-template variants, another benchmark suite, or unrelated benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another compiled-pattern collection/replacement benchmark suite:
  - add focused contract coverage for the compiled-pattern direct-success `split()` / `findall()` / `finditer()` / `sub()` / `subn()` quintet, proving the rows round-trip through manifest loading, callback construction, internal probe execution, and correctness-anchor mapping without recompiling inside the timed callback;
  - reuse the bounded compiled-pattern module-helper timing support already present on the shared collection/replacement owner path instead of widening `python/rebar_harness/benchmarks.py` again in this run;
  - update the collection-replacement manifest expectations from `57` measured workloads to `62`, still with `0` known gaps on that manifest once `RBR-0868` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and wire the five new workloads to the exact correctness case ids listed above;
  - update the combined publication totals from `847` total / `847` measured / `0` known gaps across `30` manifests to `852` / `852` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `839` to `844`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 57`, `measured_workloads == 57`, and `known_gap_count == 0` to `62`, `62`, and `0`;
  - the five new compiled-pattern-first-argument direct-success workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection/replacement benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0870-compiled-pattern-collection-replacement-success.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger collection/replacement family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern collection/replacement benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0870` is the next available feature task id in the current checkout:
  - `RBR-0868` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0869` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0868` on the same `module-workflow-surface` frontier so the adjacent compiled-pattern-first-argument collection/replacement direct-success quintet catches up on the existing Python-path `collection_replacement_boundary.py` surface before broader compiled-pattern collection/replacement publication or another helper family reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and depends only on the bounded benchmark-path expansion already queued in `RBR-0868`:
  - `tests/conformance/fixtures/module_workflow_surface.py` already publishes the exact adjacent correctness anchors `workflow-module-split-str-compiled-pattern`, `workflow-module-findall-bytes-compiled-pattern`, `workflow-module-finditer-str-compiled-pattern`, `workflow-module-sub-str-compiled-pattern`, and `workflow-module-subn-bytes-compiled-pattern`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern and (split or findall or finditer or sub or subn) and not keyword and not unexpected and not duplicate and not on_'` passed in this run (`20 passed, 1194 deselected`), so no Rust or Python regex-behavior prerequisite is missing for this bounded direct-success slice;
  - `benchmarks/workloads/collection_replacement_boundary.py` currently publishes no compiled-pattern direct-success rows on the shared collection/replacement benchmark surface even though the correctness owner already publishes the full adjacent quintet;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently carries compiled-pattern keyword and wrong-text-model collection/replacement coverage but no direct-success anchor-contract definition on that owner path; and
  - the acceptance counts above are intentionally written against the immediate post-`RBR-0868` state of `847` total / `847` measured / `0` known gaps overall with `REPORT["summary"]["module_workloads"] == 839` and `REPORT["manifests"]["collection-replacement-boundary"]` at `57` selected / `57` measured / `0` known gaps.

## Completion
- 2026-03-21: Added the five compiled-pattern-first-argument direct-success `split()` / `findall()` / `finditer()` / `sub()` / `subn()` workloads to `benchmarks/workloads/collection_replacement_boundary.py`, extended `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with the matching shared owner-path anchor/probe/precompile contract, and republished `reports/benchmarks/latest.py`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0870-compiled-pattern-collection-replacement-success.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
- The tracked published benchmark artifact now shows `REPORT["manifests"]["collection-replacement-boundary"]` at `62` selected / `62` measured / `0` known gaps and the combined summary at `852` total / `852` measured / `0` known gaps with `REPORT["summary"]["module_workloads"] == 844`.
