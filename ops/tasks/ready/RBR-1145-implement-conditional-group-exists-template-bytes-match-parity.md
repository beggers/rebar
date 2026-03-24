# RBR-1145: Implement conditional group-exists template bytes match parity

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the exact deferred follow-on on the shared conditional replacement owner path by converting the bounded bytes match-object slice for `conditional-group-exists-replacement-template-workflows` from scaffold placeholders to Rust-backed parity, so the shared replacement parity suite stops staging those bytes match snapshots and `Match.expand()` checks behind the existing bytes `search()` boundary.

## Pattern Pair
- `rebar.search(rb"a(b)?c(?(1)d|e)", b"zzabcdzz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").search(b"zzacezz")`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- Land the missing bytes match-object runtime support for the exact two-arm conditional replacement-template owner path in Rust, with Python changes limited to argument normalization, wrapper plumbing, and FFI calls:
  - `rebar.search(rb"a(b)?c(?(1)d|e)", b"zzabcdzz")` and `rebar.search(rb"a(b)?c(?(1)d|e)", b"zzacezz")` stop raising the scaffold placeholder and instead return `re.Match`-shaped `rebar.Match` objects whose spans, `groups()`, `lastindex`, `lastgroup`, `regs`, and convenience APIs match CPython for the bounded present-capture and absent-capture workflows;
  - `rebar.compile(rb"a(b)?c(?(1)d|e)").search(...)` matches the same bounded numbered bytes workflows through the compiled-pattern entrypoint instead of raising `rebar.Pattern.search()` scaffold `NotImplementedError`;
  - `rebar.search(rb"a(?P<word>b)?c(?(word)d|e)", b"zzabcdzz")` and `rebar.search(rb"a(?P<word>b)?c(?(word)d|e)", b"zzacezz")` now match CPython for the bounded named bytes workflows, including `groupdict()` and the absent named-capture `None` payload; and
  - the matching compiled-pattern named bytes searches behave the same way, and `Match.expand(rb"\\1x")` / `Match.expand(rb"\\g<word>x")` on those exact bytes matches now agrees with CPython instead of staying gated behind placeholder-only match acquisition.
- Keep the work on the existing shared replacement owner path in `tests/python/test_fixture_backed_replacement_parity_suite.py` rather than creating a detached parity module, correctness fixture manifest, or benchmark workload:
  - remove the `pending_bytes_match_object_manifest_ids` staging for `conditional-group-exists-replacement-template-workflows`;
  - update the direct frontier assertions so the manifest's match-snapshot and template-expand selections require the full mixed `str`/`bytes` numbered and named module/pattern matrix for this exact bounded slice; and
  - keep the already-landed `str` match-snapshot behavior plus the surrounding conditional replacement, grouped replacement, and broader nested replacement surfaces green on the same file.
- Preserve the existing unsupported boundaries outside this exact slice:
  - do not widen into correctness publication, benchmark manifests, README text, or tracked ops state prose in this run; and
  - leave broader bytes `search()` follow-ons on other owner paths, callable replacements, alternation-heavy conditionals, nested conditionals, quantified conditionals, and non-template replacement work for later tasks.

## Verification
- `cargo build -p rebar-cpython`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'replacement_match_snapshot_matches_cpython or replacement_template_match_expand_matches_cpython or conditional_replacement_template'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'conditional_replacement_template and bytes'`

## Constraints
- Keep the implementation bounded to the exact bytes two-arm conditional replacement-template match-object slice above. Leave correctness publication, benchmark catch-up, broader bytes helper execution, and other conditional follow-ons for later tasks.
- New compatibility behavior belongs in Rust. Do not solve this by delegating the new bytes match behavior to stdlib `re` or by expanding Python-only fallback execution beyond the existing wrapper and bridge responsibilities.
- Preserve the already-landed bytes template replacement result parity from `RBR-1130`, `RBR-1141`, `RBR-1133`, and `RBR-1135` while widening only the missing bytes match-object surface that those runs explicitly left deferred.

## Notes
- `RBR-1145` is the next available unreserved feature task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1144`; and
  - `rg -n 'RBR-1145|RBR-1146|RBR-1147|RBR-1148' ops/tasks ops/state -g '*.md'` matched only historical notes inside completed task files in this run, not a live reserved future task.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The narrow same-family owner-path check in this run confirms that an implementation prerequisite, not another publication-only task, is the surviving post-drain slice:
  - `ops/tasks/done/RBR-1133-publish-conditional-group-exists-template-bytes-workflows.md` explicitly leaves the manifest's match-object-derived bytes checks gated behind the existing bytes `search()` placeholder boundary;
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` still carries `pending_bytes_match_object_manifest_ids=frozenset({"conditional-group-exists-replacement-template-workflows"})` and the direct guard `test_conditional_replacement_template_keeps_bytes_match_snapshots_pending`, so the shared parity surface is still deliberately staging this exact bytes slice;
  - direct public-path probes in this run showed both `rebar.search(rb"a(b)?c(?(1)d|e)", b"zzabcdzz")` and `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").search(b"zzacezz")` still raising scaffold `NotImplementedError`; and
  - `reports/correctness/latest.py` and `reports/benchmarks/latest.py` already reflect the adjacent bytes publication and benchmark catch-up for this owner family, so queuing another publication-only or benchmark-only slice here would skip past a still-missing runtime prerequisite.
