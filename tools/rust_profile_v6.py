#!/usr/bin/env python3
"""Correctness-gated, isolated Rust engine and bridge counters for frozen v6."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

from candidates import _rust_bridge
from candidates import rust_candidate as rust
from tools.perf_v6 import correctness_gate, frozen, operation, snapshot


ENGINE_FIELDS = (
    "compile_calls",
    "unicode_native_match_calls",
    "ascii_native_match_calls",
    "native_collection_calls",
    "run_match_calls",
    "search_starts_considered",
    "search_starts_skipped",
    "expression_evaluations",
    "capture_state_clones",
    "sequence_evaluations",
    "alternative_evaluations",
    "capture_group_evaluations",
    "repeat_evaluations",
    "simple_repeat_evaluations",
    "general_repeat_evaluations",
    "literal_comparisons",
    "character_class_checks",
    "category_checks",
    "cached_character_class_checks",
    "native_allocations",
    "native_deallocations",
    "native_reallocations",
    "native_allocated_bytes",
    "native_reallocated_bytes",
    "vm_run_calls",
    "repeat_layout_checks",
    "start_table_preparations",
    "character_class_preparations",
    "lookaround_evaluations",
    "backreference_evaluations",
    "vm_instructions",
    "vm_split_instructions",
    "vm_repeat_instructions",
    "vm_lookaround_instructions",
    "vm_backtracks",
    "vm_choice_pushes",
    "vm_inline_stack_overflows",
    "vm_capture_undo_records",
    "vm_guard_undo_records",
    "vm_look_capture_snapshots",
    "vm_accept_instructions",
    "vm_character_class_instructions",
    "vm_literal_instructions",
    "vm_category_instructions",
    "vm_backreference_instructions",
    "vm_search_starts",
    "vm_filtered_search_starts",
    "legacy_match_calls",
    "vm_jump_instructions",
    "vm_boundary_instructions",
    "vm_anchor_instructions",
    "vm_atomic_entries",
    "vm_atomic_exits",
    "vm_conditional_instructions",
    "vm_repeated_character_checks",
    "vm_guard_allocations",
    "vm_compile_calls",
    "vm_code_emissions",
    "vm_compiled_simple_repeats",
)

BRIDGE_FIELDS = (
    "bridge_run_calls",
    "bridge_collection_calls",
    "bridge_findall_calls",
    "unicode_subject_preparations",
    "unicode_codepoints_prepared",
    "ascii_or_buffer_native_calls",
    "reserved_bridge",
    "unicode_batch_rejections",
    "batched_result_records",
    "allocated_collection_capacity",
    "bridge_allocated_bytes",
    "bridge_storage_allocations",
    "bridge_compile_calls",
    "borrowed_subject_opens",
    "streamed_collection_calls",
    "streamed_native_match_calls",
    "direct_pattern_match_calls",
    "direct_bound_search_calls",
    "direct_bound_match_calls",
    "direct_bound_fullmatch_calls",
    "direct_bound_findall_calls",
    "direct_bound_literal_findall_calls",
    "native_match_objects",
    "subject_buffer_opens",
    "bridge_index_conversions",
    "result_list_growth_calls",
    "direct_template_calls",
    "nonascii_streamed_collections",
    "direct_literal_hits",
    "native_capture_overflow_allocations",
)


def native_counters():
    engine = ctypes.CDLL(str(Path(rust.__file__).with_name("_rust_engine.so").resolve()))
    bridge = ctypes.CDLL(str(Path(_rust_bridge.__file__).resolve()))
    for library, prefix in (
        (engine, "rebar_rust_profile"),
        (bridge, "rebar_rust_bridge_profile"),
    ):
        try:
            reset = getattr(library, f"{prefix}_reset")
            get = getattr(library, f"{prefix}_get")
        except AttributeError as error:
            raise RuntimeError(
                "the active Rust candidate is not an isolated profile build; "
                "run tools/build_rust_profile_v6.sh and use its PYTHONPATH"
            ) from error
        reset.argtypes = []
        reset.restype = None
        get.argtypes = [ctypes.c_size_t]
        get.restype = ctypes.c_uint64
    return engine, bridge


def capture(engine, bridge):
    row = {
        name: int(engine.rebar_rust_profile_get(index))
        for index, name in enumerate(ENGINE_FIELDS)
    }
    row.update(
        {
            name: int(bridge.rebar_rust_bridge_profile_get(index))
            for index, name in enumerate(BRIDGE_FIELDS)
            if name != "reserved_bridge"
        }
    )
    return row


def selected_cases(cases, expected, args):
    wanted = set(args.category or ())
    wanted_ids = set(args.case or ())
    rows = []
    counts: dict[tuple[str, str], int] = defaultdict(int)
    found_categories: set[str] = set()
    found_ids: set[str] = set()
    for case, want in zip(cases, expected, strict=True):
        if args.cohort != "all" and case["cohort"] != args.cohort:
            continue
        if wanted and case["category"] not in wanted:
            continue
        if wanted_ids and case["id"] not in wanted_ids:
            continue
        key = case["cohort"], case["category"]
        if args.limit_per_family is not None and counts[key] >= args.limit_per_family:
            continue
        counts[key] += 1
        found_categories.add(case["category"])
        found_ids.add(case["id"])
        rows.append((case, want))
    if wanted - found_categories:
        raise RuntimeError(f"unknown or excluded categories: {sorted(wanted - found_categories)}")
    if wanted_ids - found_ids:
        raise RuntimeError(f"unknown or excluded cases: {sorted(wanted_ids - found_ids)}")
    if not rows:
        raise RuntimeError("no frozen performance cases selected")
    return rows


def summarize(rows):
    groups: dict[tuple[str, str, str, bool], list[dict]] = defaultdict(list)
    for row in rows:
        groups[
            (
                row["cohort"],
                row["category"],
                row["api"],
                "I" in row["flags"],
            )
        ].append(row)
    fields = tuple(
        field
        for field in (*ENGINE_FIELDS, *BRIDGE_FIELDS)
        if field != "reserved_bridge"
    )
    families = []
    for (cohort, category, api, ignore_case), members in sorted(groups.items()):
        summary = {
            "cohort": cohort,
            "category": category,
            "api": api,
            "ignore_case": ignore_case,
            "cases": len(members),
        }
        for field in fields:
            values = [member[field] for member in members]
            summary[f"{field}_median"] = statistics.median(values)
            summary[f"{field}_maximum"] = max(values)
        families.append(summary)
    return families


def sha256(path):
    return hashlib.file_digest(Path(path).open("rb"), "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--category", action="append")
    parser.add_argument("--case", action="append")
    parser.add_argument("--cohort", choices=("calibration", "holdout", "all"), default="all")
    parser.add_argument("--limit-per-family", type=int)
    args = parser.parse_args()
    if args.limit_per_family is not None and args.limit_per_family < 1:
        parser.error("--limit-per-family must be positive")

    _, cases, expected, manifest = frozen()
    chosen = selected_cases(cases, expected, args)
    engine, bridge = native_counters()
    rows = []
    for index, (case, want) in enumerate(chosen, 1):
        correctness_gate(rust, case, want)
        action = operation(rust, case)
        bridge.rebar_rust_bridge_profile_reset()
        engine.rebar_rust_profile_reset()
        result = action()
        counters = capture(engine, bridge)
        if snapshot(result) != want["result"]:
            raise RuntimeError(f"post-profile correctness mismatch: {case['id']}")
        row = {
            "case": case["id"],
            "cohort": case["cohort"],
            "category": case["category"],
            "api": case["api"],
            "lifecycle": case["lifecycle"],
            "flags": list(case.get("flags", [])),
            "pattern_length": len(case["pattern"]),
            "subject_length": len(case.get("string") or ""),
            "result_count": len(result) if isinstance(result, (list, tuple)) else int(result is not None),
        }
        row.update(counters)
        rows.append(row)
        if index % 128 == 0:
            print(f"profiled {index}/{len(chosen)} frozen Rust workloads", flush=True)

    families = summarize(rows)
    result = {
        "schema": "rebar-rust-profile-v6",
        "counter_version": 2,
        "expected_sha256": manifest["expected_sha256"],
        "engine_sha256": sha256(Path(rust.__file__).with_name("_rust_engine.so")),
        "bridge_sha256": sha256(_rust_bridge.__file__),
        "isolated_engine": str(Path(rust.__file__).with_name("_rust_engine.so")),
        "isolated_bridge": str(Path(_rust_bridge.__file__)),
        "cohort": args.cohort,
        "categories": sorted({row["category"] for row in rows}),
        "cases": len(rows),
        "correctness_checks": len(rows) * 2,
        "engine_fields": list(ENGINE_FIELDS),
        "bridge_fields": [name for name in BRIDGE_FIELDS if name != "reserved_bridge"],
        "families": families,
        "rows": rows,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for family in families:
        if family["cohort"] != "holdout":
            continue
        print(
            f"{family['category']:<37} "
            f"api={family['api']:<11} "
            f"I={str(family['ignore_case']):<5} "
            f"n={family['cases']:<3} "
            f"starts={family['search_starts_considered_median']:<9g} "
            f"eval={family['expression_evaluations_median']:<9g} "
            f"clones={family['capture_state_clones_median']:<9g} "
            f"alloc={family['native_allocations_median']:<9g} "
            f"bytes={family['native_allocated_bytes_median']:<11g} "
            f"vm={family['vm_instructions_median']:<9g} "
            f"backtracks={family['vm_backtracks_median']:<9g} "
            f"overflow={family['vm_inline_stack_overflows_median']:<7g} "
            f"legacy={family['legacy_match_calls_median']:<5g} "
            f"unicode={family['unicode_codepoints_prepared_median']:<9g} "
            f"batch={family['allocated_collection_capacity_median']:<9g}",
            flush=True,
        )
    print(
        json.dumps(
            {
                key: value
                for key, value in result.items()
                if key not in {"families", "rows"}
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
