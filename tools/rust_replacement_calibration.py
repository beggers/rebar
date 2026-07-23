#!/usr/bin/env python3
"""Reproduce and audit the frozen, calibration-only Rust replacement pilot."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "candidates" / "evidence"
MANIFEST = ROOT / "performance" / "v6" / "manifest.json"
EXPECTED_SHA256 = "c8e32e879cc7a134748f8f3f29fed49678895745fdecebe63ceec46b6a3b5335"
MODULES = ("re", "candidates.rust_candidate")
CATEGORIES = (
    "bytes-replace",
    "deeper-module-warm-sub",
    "deeper-shell-vars",
    "deeper-source-comments",
    "expanded-cold-module",
    "expanded-comment-strip",
    "expanded-newline-normalize",
    "expanded-replace-callback",
    "expanded-replace-redact",
    "expanded-replace-template",
    "expanded-whitespace-clean",
    "large-bytes-replace",
    "large-cleanup",
    "large-module-replace",
    "large-replace-callback",
    "large-replace-groups",
    "literal-replace",
    "module-replace",
    "real-lines",
    "real-whitespace",
    "replace-limited",
    "sub",
    "subn-callable",
    "template-repeat",
)
ARTIFACTS = {
    "before": {
        "summary": "rust-v6-native-replacement-before.json.gz",
        "summary_sha256": (
            "a4abded3516eff9c902e5fcbd3b74f8e715c0aab5adf75c1bea829d592683333"
        ),
        "raw": "rust-v6-native-replacement-before.jsonl.gz",
        "raw_sha256": (
            "6e73bda0cb4140c432f3e42dd08ea7b24aa0a5a8a4317fcd918197e563f4f595"
        ),
    },
    "after": {
        "summary": "rust-v6-native-replacement-after.json.gz",
        "summary_sha256": (
            "3e202b82ec41a8129baf7c76d457416924a8b8975fb5e5324993611e17c0047b"
        ),
        "raw": "rust-v6-native-replacement-after.jsonl.gz",
        "raw_sha256": (
            "3258380928054210d2853834b840510432dc46f9a0183bfc76b76eb5013b728a"
        ),
    },
}
CASES = 697
TRIALS = 3
MAX_OPERATIONS = 8
BOOTSTRAPS = 101
HISTORICAL_ARCHIVE_SLOW_THRESHOLD = 0.8
TRUE_OVER_20_PERCENT_SLOW_THRESHOLD = 5 / 6


def require(condition: bool, message: str) -> None:
    """Reject an incomplete, changed, mislabeled, or unpaired experiment."""
    if not condition:
        raise ValueError(message)


def close(actual: Any, expected: float, label: str) -> None:
    """Validate a reconstructed finite floating-point observation."""
    require(isinstance(actual, (float, int)), f"{label}: not a number")
    require(math.isfinite(actual), f"{label}: non-finite value")
    require(
        math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12),
        f"{label}: {actual!r} != {expected!r}",
    )


def read_gzip(path: Path) -> tuple[bytes, str]:
    """Read deterministic gzip without trusting its filename or timestamp."""
    compressed = path.read_bytes()
    require(len(compressed) >= 18, f"{path.name}: truncated gzip")
    require(compressed[:3] == b"\x1f\x8b\x08", f"{path.name}: invalid gzip")
    require(compressed[3] == 0, f"{path.name}: non-deterministic gzip flags")
    require(
        compressed[4:8] == b"\0\0\0\0",
        f"{path.name}: non-deterministic gzip timestamp",
    )
    return gzip.decompress(compressed), hashlib.sha256(compressed).hexdigest()


def frozen_manifest() -> dict[str, Any]:
    """Require the originally pinned performance fixture and protocol."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest["schema"] == "rebar-performance-v6", "v6 schema drift")
    require(
        manifest["expected_sha256"] == EXPECTED_SHA256,
        "frozen expected-answer digest drift",
    )
    require(manifest["cases"] == 12_432, "frozen case denominator drift")
    require(
        manifest["cohorts"] == {"calibration": 6_216, "holdout": 6_216},
        "frozen calibration/holdout denominator drift",
    )
    require(manifest["trials"] == 13, "frozen trial count drift")
    require(manifest["warmups"] == 4, "frozen warmup count drift")
    require(manifest["bootstraps"] == 2_000, "frozen bootstrap count drift")
    require(manifest["order_seed"] == 1_985_072_201, "paired order seed drift")
    require(
        manifest["bootstrap_seed"] == 1_985_072_202,
        "paired bootstrap seed drift",
    )
    return manifest


def interval(
    values: list[float], rng: random.Random, samples: int
) -> tuple[float, float]:
    """Reconstruct the runner's seeded, per-case paired confidence range."""
    draws = sorted(
        statistics.fmean(values[rng.randrange(len(values))] for _ in values)
        for _ in range(samples)
    )
    return (
        math.exp(draws[math.floor(0.025 * (samples - 1))]),
        math.exp(draws[math.floor(0.975 * (samples - 1))]),
    )


def verify_groups(
    label: str,
    summary: dict[str, Any],
    results: list[dict[str, Any]],
    paired_logs: dict[str, list[float]],
    rng: random.Random,
) -> None:
    """Reconstruct every reported denominator, slowdown, and confidence range."""
    dimensions = (
        ("families", ("cohort", "category")),
        ("apis", ("cohort", "api")),
        ("lifecycles", ("cohort", "lifecycle")),
        ("inputs", ("cohort", "input")),
        ("rankings", ("cohort",)),
    )
    for field, names in dimensions:
        grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
        for result in results:
            grouped[tuple(result[name] for name in names)].append(result)
        reported = summary[field]
        require(
            len(reported) == len(grouped),
            f"{label}/{field}: group denominator drift",
        )
        for actual, (key, members) in zip(
            reported, sorted(grouped.items()), strict=True
        ):
            prefix = f"{label}/{field}/{key!r}"
            require(
                tuple(actual[name] for name in names) == key,
                f"{prefix}: changed group identity or ordering",
            )
            require(actual["cases"] == len(members), f"{prefix}: case loss")
            require(
                actual["faster"]
                == sum(result["statistically_faster"] for result in members),
                f"{prefix}: incorrect faster-case count",
            )
            require(
                actual["slow"]
                == sum(result["regression_gt_20pct"] for result in members),
                f"{prefix}: changed historical archive slowdown flags",
            )
            logs = [math.log(result["speedup"]) for result in members]
            close(actual["speedup"], math.exp(statistics.fmean(logs)), prefix)
            close(
                actual["median_baseline_ns"],
                statistics.median(result["baseline_ns"] for result in members),
                f"{prefix}: baseline median",
            )
            close(
                actual["median_rust_ns"],
                statistics.median(result["rust_ns"] for result in members),
                f"{prefix}: Rust median",
            )
            close(
                actual["median_peak_traced_ratio"],
                statistics.median(
                    result["peak_traced_ratio"] for result in members
                ),
                f"{prefix}: traced-memory median",
            )
            denominator = sum(result["weight"] for result in members)
            require(denominator > 0, f"{prefix}: invalid weights")
            draws = sorted(
                sum(
                    statistics.fmean(
                        paired_logs[result["case"]][
                            rng.randrange(len(paired_logs[result["case"]]))
                        ]
                        for _ in paired_logs[result["case"]]
                    )
                    * result["weight"]
                    for result in members
                )
                / denominator
                for _ in range(BOOTSTRAPS)
            )
            close(
                actual["ci95_low"],
                math.exp(draws[math.floor(0.025 * (BOOTSTRAPS - 1))]),
                f"{prefix}: lower paired confidence bound",
            )
            close(
                actual["ci95_high"],
                math.exp(draws[math.floor(0.975 * (BOOTSTRAPS - 1))]),
                f"{prefix}: upper paired confidence bound",
            )


def verify_stage(
    label: str, manifest: dict[str, Any]
) -> tuple[dict[str, Any], set[str], dict[str, str]]:
    """Validate every original compressed summary and every paired raw row."""
    artifact = ARTIFACTS[label]
    summary_bytes, summary_compressed_sha = read_gzip(
        EVIDENCE / artifact["summary"]
    )
    require(
        hashlib.sha256(summary_bytes).hexdigest() == artifact["summary_sha256"],
        f"{label}: changed uncompressed summary",
    )
    summary = json.loads(summary_bytes)
    raw_bytes, raw_compressed_sha = read_gzip(EVIDENCE / artifact["raw"])
    raw_sha = hashlib.sha256(raw_bytes).hexdigest()
    require(raw_sha == artifact["raw_sha256"], f"{label}: changed raw rows")
    require(summary["raw_sha256"] == raw_sha, f"{label}: summary/raw mismatch")
    require(
        summary["schema"] == "rebar-rust-v6-loss-probe-v1",
        f"{label}: changed measurement schema",
    )
    require(
        summary["measurement"]
        == "diagnostic pilot; not a full frozen-holdout result",
        f"{label}: pilot incorrectly presented as a holdout result",
    )
    require(
        summary["cohort_selection"] == "calibration",
        f"{label}: holdout accessed or mislabeled",
    )
    require(
        summary["expected_sha256"] == manifest["expected_sha256"],
        f"{label}: frozen expected-answer digest drift",
    )
    require(summary["categories"] == list(CATEGORIES), f"{label}: category drift")
    require(tuple(summary["modules"]) == MODULES, f"{label}: module drift")
    require(summary["cases"] == CASES, f"{label}: selected-case drift")
    require(summary["trials"] == TRIALS, f"{label}: pilot trial drift")
    require(summary["max_operations"] == MAX_OPERATIONS, f"{label}: ops drift")
    require(summary["bootstraps"] == BOOTSTRAPS, f"{label}: bootstrap drift")
    require(
        summary["variants_per_family"] is None,
        f"{label}: family variants were silently capped",
    )
    require(summary["frozen_cases"] == manifest["cases"], f"{label}: v6 drift")
    require(
        summary["frozen_trials"] == manifest["trials"],
        f"{label}: frozen trial metadata drift",
    )
    require(summary["warmups"] == manifest["warmups"], f"{label}: warmup drift")
    require(
        summary["frozen_bootstraps"] == manifest["bootstraps"],
        f"{label}: frozen bootstrap metadata drift",
    )
    require(
        summary["order_seed"] == manifest["order_seed"]
        and summary["bootstrap_seed"] == manifest["bootstrap_seed"],
        f"{label}: frozen seed drift",
    )
    require(raw_bytes.endswith(b"\n"), f"{label}: unterminated raw rows")
    lines = raw_bytes.splitlines()
    expected_rows = CASES * TRIALS * len(MODULES)
    require(summary["rows"] == expected_rows, f"{label}: summary row drift")
    require(len(lines) == expected_rows, f"{label}: missing or extra raw rows")
    require(
        summary["correctness_checks"] == expected_rows * 3,
        f"{label}: correctness gates were silently skipped",
    )

    rows: dict[tuple[str, int, str], dict[str, Any]] = {}
    result_digests: dict[str, str] = {}
    orders: dict[tuple[str, int], set[int]] = defaultdict(set)
    for line_number, line in enumerate(lines, start=1):
        row = json.loads(line)
        prefix = f"{label}: raw row {line_number}"
        require(
            row["schema"] == "rebar-rust-v6-pilot-row-v1",
            f"{prefix}: changed row schema",
        )
        require(row["cohort"] == "calibration", f"{prefix}: holdout inclusion")
        require(row["module"] in MODULES, f"{prefix}: unrecognized engine")
        require(row["trial"] in range(TRIALS), f"{prefix}: trial drift")
        require(row["order"] in (0, 1), f"{prefix}: invalid paired order")
        require(
            isinstance(row["operations"], int)
            and 0 < row["operations"] <= MAX_OPERATIONS,
            f"{prefix}: invalid operation count",
        )
        require(row["elapsed_ns"] > 0, f"{prefix}: nonpositive timing")
        require(row["peak_traced_bytes"] >= 0, f"{prefix}: invalid memory")
        close(
            row["ns_per_op"],
            row["elapsed_ns"] / row["operations"],
            f"{prefix}: per-operation timing",
        )
        key = (row["case"], row["trial"], row["module"])
        require(key not in rows, f"{prefix}: duplicate paired observation")
        rows[key] = row
        orders[(row["case"], row["trial"])].add(row["order"])
        previous_digest = result_digests.setdefault(
            row["case"], row["expected_sha256"]
        )
        require(
            previous_digest == row["expected_sha256"],
            f"{prefix}: baseline/candidate expected-answer mismatch",
        )

    results = summary["case_results"]
    require(len(results) == CASES, f"{label}: missing case summaries")
    case_ids: set[str] = set()
    paired_logs: dict[str, list[float]] = {}
    rng = random.Random(manifest["bootstrap_seed"])
    for result in results:
        case_id = result["case"]
        prefix = f"{label}: {case_id}"
        require(case_id not in case_ids, f"{prefix}: duplicate case result")
        case_ids.add(case_id)
        require(result["cohort"] == "calibration", f"{prefix}: holdout result")
        require(result["category"] in CATEGORIES, f"{prefix}: category drift")
        require(result["candidate"] == MODULES[1], f"{prefix}: candidate drift")
        require(result["weight"] > 0, f"{prefix}: invalid case weight")
        baseline = []
        candidate = []
        for trial in range(TRIALS):
            require(
                orders.get((case_id, trial)) == {0, 1},
                f"{prefix}: incomplete paired trial {trial}",
            )
            left = rows.get((case_id, trial, MODULES[0]))
            right = rows.get((case_id, trial, MODULES[1]))
            require(left is not None and right is not None, f"{prefix}: lost pair")
            for row in (left, right):
                for field in ("category", "api", "lifecycle", "input"):
                    require(
                        row[field] == result[field],
                        f"{prefix}: inconsistent {field}",
                    )
            baseline.append(left)
            candidate.append(right)

        logs = [
            math.log(left["ns_per_op"] / right["ns_per_op"])
            for left, right in zip(baseline, candidate, strict=True)
        ]
        paired_logs[case_id] = logs
        speedup = math.exp(statistics.fmean(logs))
        low, high = interval(logs, rng, BOOTSTRAPS)
        close(result["speedup"], speedup, f"{prefix}: speed ratio")
        close(result["ci95_low"], low, f"{prefix}: lower confidence bound")
        close(result["ci95_high"], high, f"{prefix}: upper confidence bound")
        close(
            result["baseline_ns"],
            statistics.median(row["ns_per_op"] for row in baseline),
            f"{prefix}: baseline median",
        )
        close(
            result["rust_ns"],
            statistics.median(row["ns_per_op"] for row in candidate),
            f"{prefix}: Rust median",
        )
        close(
            result["peak_traced_ratio"],
            statistics.median(row["peak_traced_bytes"] for row in candidate)
            / max(
                1,
                statistics.median(row["peak_traced_bytes"] for row in baseline),
            ),
            f"{prefix}: traced-memory ratio",
        )
        require(
            result["statistically_faster"] is (low > 1),
            f"{prefix}: incorrect faster-case classification",
        )
        require(
            result["regression_gt_20pct"]
            is (speedup < HISTORICAL_ARCHIVE_SLOW_THRESHOLD),
            f"{prefix}: changed historical archive <0.8 classification",
        )

    require(
        set(result_digests) == case_ids,
        f"{label}: raw/summary case identities differ",
    )
    require(
        summary["regressions"]
        == [result for result in results if result["regression_gt_20pct"]],
        f"{label}: historical archive slowdown details were removed or changed",
    )
    verify_groups(label, summary, results, paired_logs, rng)
    require(
        {result["api"] for result in results}
        == {"search", "split", "sub", "subn"},
        f"{label}: replacement or neighboring guard operations missing",
    )

    ranking = summary["rankings"][0]
    corrected_regressions = [
        result
        for result in results
        if result["speedup"] < TRUE_OVER_20_PERCENT_SLOW_THRESHOLD
    ]
    report = {
        "stage": label,
        "cohort": "calibration",
        "cases": CASES,
        "families": len(CATEGORIES),
        "rows": expected_rows,
        "correctness_checks": summary["correctness_checks"],
        "speedup": ranking["speedup"],
        "ci95_low": ranking["ci95_low"],
        "ci95_high": ranking["ci95_high"],
        "statistically_faster": ranking["faster"],
        "regression_gt_20pct_speedup_threshold": (
            TRUE_OVER_20_PERCENT_SLOW_THRESHOLD
        ),
        "regressions_gt_20pct": len(corrected_regressions),
        "historical_archive_slow_speedup_threshold": (
            HISTORICAL_ARCHIVE_SLOW_THRESHOLD
        ),
        "historical_archive_slow_flags": ranking["slow"],
        "family_regressions_gt_20pct": [
            {
                "category": family["category"],
                "cases": family["cases"],
                "historical_archive_slow_flags": family["slow"],
                "regressions_gt_20pct": sum(
                    result["category"] == family["category"]
                    and result["speedup"]
                    < TRUE_OVER_20_PERCENT_SLOW_THRESHOLD
                    for result in results
                ),
            }
            for family in summary["families"]
        ],
        "summary_sha256": artifact["summary_sha256"],
        "summary_gzip_sha256": summary_compressed_sha,
        "raw_sha256": raw_sha,
        "raw_gzip_sha256": raw_compressed_sha,
    }
    return report, case_ids, result_digests


def self_test() -> dict[str, Any]:
    """Audit evidence integrity only; do not run or certify replacement code."""
    manifest = frozen_manifest()
    before, before_cases, before_digests = verify_stage("before", manifest)
    after, after_cases, after_digests = verify_stage("after", manifest)
    require(before_cases == after_cases, "before/after case selection drift")
    require(
        before_digests == after_digests,
        "before/after expected-answer digest drift",
    )
    return {
        "schema": "rebar-rust-v6-native-replacement-evidence-self-test-v1",
        "passed": True,
        "scope": "calibration evidence integrity only; not replacement correctness",
        "holdout_cases_accessed": 0,
        "expected_sha256": manifest["expected_sha256"],
        "frozen_cases": manifest["cases"],
        "frozen_trials": manifest["trials"],
        "frozen_bootstraps": manifest["bootstraps"],
        "pilot_trials": TRIALS,
        "pilot_bootstraps": BOOTSTRAPS,
        "before": before,
        "after": after,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    self_parser = commands.add_parser(
        "self-test",
        help="audit all committed practice-only evidence without benchmarking",
    )
    self_parser.add_argument(
        "--output",
        type=Path,
        help="write the deterministic evidence-integrity report",
    )
    measure_parser = commands.add_parser(
        "measure",
        help="rerun only the identical 697 frozen practice cases",
    )
    measure_parser.add_argument("--output", type=Path, required=True)
    measure_parser.add_argument("--raw", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "self-test":
        result = self_test()
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        print(json.dumps(result, sort_keys=True))
        return

    frozen_manifest()
    from tools.rust_v6_loss_probe import measure

    measure(
        argparse.Namespace(
            output=str(args.output),
            raw=str(args.raw),
            trials=TRIALS,
            max_ops=MAX_OPERATIONS,
            bootstraps=BOOTSTRAPS,
            category=list(CATEGORIES),
            all=False,
            cohort="calibration",
            variants_per_family=None,
        )
    )


if __name__ == "__main__":
    main()
