# First-party Zig deallocator lifetime source repair V1

Status: SOURCE FREEZE ONLY. The repaired candidate has not been built, imported, run, or qualified.

## Purpose

The actually published V12 Zig campaign contains 13 distinct, guarded candidate workers. Its unchanged clean adapter reports the same real `Exception ignored while calling deallocator` and `AttributeError: 'NoneType' object has no attribute 'free'` in the actual stderr excerpt of every worker, including each genuinely passing suite. Freeze one narrowly bounded, first-party-only source repair for the exact observed `Pattern.__del__` lifetime defect. Do not describe the separate actual subinterpreter failure, semantic mismatches, or candidate correctness as repaired.

## Immutable predecessor and actual results

Authenticate `tools/run_owned_repaired_zig_original_campaign_v12.py`, its V12 protocol and canonical contract, and its actual, durable plaintext publication `oracle/phase2/evidence/repaired-zig-original-campaign-v12-phase2-v13-zig-guard-clean-v1-original-p0-v12-failures-publication-receipt.json` by exact SHA-256, complete byte count, original device, inode, ownership, mode, and single-link identity. Never open or inflate its matching archive.

The real V12 run attempted the unchanged 31,237 original cases in 13 suites using 13 distinct, guard-proven candidate workers. Twelve suites completed. Seven suites passed: `original_bounded_v5` (151), `public_v3` (864), `scanner_v3` (1,024), `buffer_v3` (768), `managed_v1` (1,024), `pep688_v4` (264), and `threaded_pattern_v1` (512), totaling 4,607 actually passing cases. Five completed suites establish a measured lower bound of 1,700 actual semantic mismatches: `scanner_verbose_v1` (620), `public_types_v1` (248), `substitution_v2` (64), `shape_v2` (672), and `public_surface_v19` (96). Overall mismatch count: NOT MEASURED.

The thirteenth, `subinterpreter_v2`, is a genuine, separately preserved original-suite infrastructure failure. Its activation stage is `OBSERVE_COMPLETE_ORIGINAL_SUBINTERPRETER_SUITE`; its outer and nested error types are `ActualSuiteFailure`. Although the nested wrapper reports `actual_child_guards_installed = 1`, its preserved original failure independently proves `active_phase = install-original-private-guard-A`, `actual_prepared_interpreter_ids = []`, `actual_case_interpreter_exec_calls = 0`, and `GuardError: runtime guard blocked unattested-child-bootstrap`. Therefore the reported count does not prove that a child guard was installed or that a regex case ran. The frozen suite expects 11 interpreters and 394 interpreter-execution calls; whether this separate producer/guard bootstrap defect improves with the deallocator repair is NOT ESTABLISHED. The immutable producer, strict runtime guard, private-interpreter lifecycle, and native bridge must not be altered or weakened.

## Exactly one source change

Read the immutable clean input `candidates/zig/variants/scanner_phrase_guard_clean_v1/zig_candidate.py` (`e8a023a388d94369d3eab38260390e853cd8c38394713aef49856875cfd4ac11`; 67,262 bytes; inode 429081). Materialize a new additive source variant only at `candidates/zig/variants/scanner_phrase_guard_clean_lifetime_v1/zig_candidate.py`. Require exactly one old block:

```python
    def __del__(self):
        handle = getattr(self, "_handle", None)
        if handle:
            _zig_bridge.free(handle)
            self._handle = None
```

Require its sole exact replacement:

```python
    def __del__(self, _free=_zig_bridge.free, _getattr=getattr):
        handle = _getattr(self, "_handle", None)
        if handle:
            self._handle = None
            _free(handle)
```

The function defaults capture the actual first-party extension `free` callable and built-in attribute lookup at class definition, before module teardown. The pinned CPython 3.14.6 itself uses this exact lifetime principle in `/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/concurrent/interpreters/__init__.py:152`: its comment explains that module globals can already be destroyed, and `_decref(..., _interp_decref=_interpreters.decref)` retains the actual release callable in a definition-time default. The Zig extension callable likewise keeps its first-party module state alive; it is not an external engine or fallback. Clearing `_handle` before calling it makes reentrant cleanup at-most-once, tolerates partially initialized objects, and propagates real release errors. It adds no instance slot and changes no matching, parser, compiler, scanner, bridge, imports, or another candidate.

Prove both exact whole-file bytes and complete source-tree equivalence after replacing only the authenticated `Pattern.__del__` node. Require that `Pattern` and the destructor are unique and that defaults, statement order, first-party call, absence of swallowing, imports, slots, and every other AST node are exact.

## First-party provenance and frozen boundaries

Verify the frozen P0 completeness and differential-reference owners; exact V5 producer/13-suite/73-obligation/34-crosswalk metadata; the 8,244-case supplemental reference without treating it as candidate matching; the sealed 14,155,776-case holdout proposal without opening or generating a case; and the actual two independently built V13 Zig/C phases strictly through their authenticated public plaintext receipts. Validate all 26 genuine distinct prior build processes, six distinct source snapshots, reproducible first-party outputs, and zero borrowed, external, or CPython regex engines. Do not open private native roots or snapshots.

## Fail-closed source-only controls

Use only the pinned isolated CPython 3.14.6 with `-I -B -S`. Before reading any owner, enclose verification in the physical source wall: reject candidate/`re`/`_sre`/regex/native-loader/process/timing/network imports; unlisted files, holdout, native libraries, private roots, matching archives, writes, subprocesses, and dynamic loading. Load only the hash-authenticated immutable V5 manual canonical JSON parser; never load a candidate or a JSON/regex engine.

Pure synthetic controls must actually execute only the authenticated destructor AST in a locally manufactured ordinary Python model, never import a candidate or native bridge. Prove global-teardown survival, exact callable identity, built-in-lookup survival, one normal release, half initialization, absent/falsy handle, repeated calls, reentrant release, and real propagated release errors with ownership cleared before the failing release. Reject changed defaults, reordered cleanup, swallowed errors, a second destructor, changed slots/imports, any unrelated source change, owner substitution, all execution/build/recovery modes, and every forbidden physical effect.

## Reproduction gates

After freezing canonical source, protocol, and contract SHA-256 values, run all four gates using only `tools/apply_owned_zig_deallocator_lifetime_source_repair_v1.py`: native-environment `--self-test`, native-environment `--verify-frozen-context`, and repeat both under `env -i PATH=/usr/bin:/bin LC_ALL=C PYTHONDONTWRITEBYTECODE=1`. Pass each independently supplied `--source-sha256`, `--protocol-sha256`, and `--contract-sha256`; require canonical byte-for-byte frozen contract identity. `--render-contract` accepts only independent source/protocol hashes and writes nothing. `--run`, `--worker`, `--recover`, `--build`, and `--apply` must be rejected.

All actual candidate imports, candidate/reference workers, native loads or activations, matching archives, private roots, benchmarks, holdout cases, clocks, timing, compiler/candidate processes, network, writes, recovery roots, and canonical-source mutations must remain exactly zero. Repaired correctness, runtime independence, subinterpreter behavior, disappearance of warnings, undefined behavior, memory, and speed: NOT MEASURED. Qualified candidates: 0. No winner.
