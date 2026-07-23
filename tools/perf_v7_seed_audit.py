#!/usr/bin/env python3
"""Reproduce the rejected v7 draft's misleading practice and holdout seeds."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

from performance.v7.suite import SEEDS, SPECS, VARIANTS
from tools.perf_v7 import semantic_key, stable_value


EXPECTED_COLLIDING_FAMILIES = (
    "binary-highbit-fields",
    "binary-template-subn",
    "bounded-greedy-code",
    "bracketed-ipv6-host",
    "cold-compile-lookaround",
    "cross-script-digits",
    "cyrillic-case-fold",
    "escape-literal-mixture",
    "highbit-negative-bytes",
    "jwt-token-segments",
    "long-tail-search-hit",
    "long-tail-search-miss",
    "mutable-buffer-captures",
    "named-byte-match-surface",
    "nul-separated-binary",
    "overlap-ordered-branches",
    "possessive-digit-run",
    "readonly-buffer-scanner",
    "windowed-binary-collect",
)


# The observed original templates, retained separately from the corrected suite.
ORIGINAL = {
    "jwt-token-segments": {
        "subject": (
            "prefix eyJhbGciOiJIUzI1NiJ9."
            "eyJzdWIiOiIxMjM0NTYifQ.abcdEFGHijklMNOP suffix"
        ),
    },
    "bracketed-ipv6-host": {
        "subject": "[2001:0db8:85a3::8a2e:0370:7334]:443",
    },
    "python-relative-import": {
        "pattern": (
            r"(?m)^\s*(?:from\s+"
            r"(?P<package>[.A-Za-z_][.A-Za-z0-9_]*)\s+import\s+"
            r"(?P<name>[A-Za-z_, ]+)|import\s+"
            r"(?P<direct>[.A-Za-z0-9_]+))"
        ),
        "subject": "from {word}.{other} import entry, value",
    },
    "rust-attribute": {"subject": "#[derive({word}, {other})]"},
    "rust-use-tree": {"subject": "use {word}::{other}::{value, item};"},
    "js-template-hole": {"subject": "${{word}.{other}}"},
    "git-unified-hunk": {"subject": "@@ -12,4 +18,6 @@ def {word}"},
    "greek-simple-fold": {"subject": "ΔΕΛΤΑ ΩΜΕΓΑ αλφα {word}"},
    "turkish-simple-fold": {"subject": "İstanbul ıstanbul Istanbul {word}"},
    "cyrillic-case-fold": {"subject": "СЛОВО ПрИмеР слово"},
    "combining-mark-run": {"subject": "{word}e\u0301 {other}a\u0308"},
    "astral-emoji-run": {"subject": "report 😀🌍✨ 🧪🚀 {word}"},
    "unicode-space-split": {
        "subject": "{word}\u2003{other}\u00a0next\u202fend",
    },
    "negative-delimiter-boundary": {
        "subject": "@{word} x@{other} @{other}_2",
    },
    "dual-lookaround-password": {"subject": "{word}42 {other}7"},
    "lookahead-empty-steps": {"subject": "{word}4,{other}8:"},
    "nested-local-flag": {"subject": "{word}AB {other}CD"},
    "conditional-angle-pair": {
        "pattern": r"(?P<open><)?(?P<word>[A-Za-z_]+)(?(open)>|:)",
        "subject": "<{word}>",
    },
    "bounded-greedy-code": {"subject": "AB-X7-RED CD-42"},
    "overlap-ordered-branches": {
        "subject": "renderer rendering render record recover",
    },
    "negative-class-columns": {"subject": '"{word},{other}",{word};end'},
    "nullable-branch-cursor": {"subject": "a:;,{word}:,b;"},
    "cold-compile-lookaround": {
        "pattern": r"(?<=id=)(?P<id>[A-Za-z0-9_-]+)(?=\b)",
    },
    "warm-module-sub": {"subject": "{word} {other}"},
    "warm-module-subn": {"subject": "{word} {other}"},
    "escape-literal-mixture": {"pattern": "a.b[0] (x)+ # {word}"},
    "long-tail-search-hit": {"subject": "END:AB42"},
    "long-tail-search-miss": {"subject": "NOT-A-MATCH"},
    "dense-literal-collection": {"subject": "#{word} #{other} #{word}"},
    "split-optional-captures": {"subject": "{word},;{other}:last"},
    "callable-capture-replace": {"subject": "{word} {other}"},
}


def original_render(value, word, other, number):
    if value is None or isinstance(value, bytes):
        return value
    return (
        value.replace("{word}", word)
        .replace("{other}", other)
        .replace("{number}", str(number))
    )


def original_case(cohort, index, variant):
    item = dict(SPECS[index])
    item.update(ORIGINAL.get(item["name"], {}))
    rng = random.Random(SEEDS[cohort] + index * 1009 + variant * 9181)
    names = (
        ("amber", "cedar", "delta", "ember", "maple", "north")
        if cohort == "holdout"
        else ("acorn", "birch", "copper", "drift", "elm", "fjord")
    )
    alternatives = (
        ("violet", "stable", "remote", "signal", "winter")
        if cohort == "holdout"
        else ("beacon", "direct", "grove", "harbor", "summer")
    )
    word = rng.choice(names)
    other = rng.choice(alternatives)
    number = 73 + index * 41 + variant * 37
    copies = (1, 2, 3, 4, 8, 12, 16, 24)[variant % 8]
    value = original_render(item["subject"], word, other, number)
    if item["repeat"] and value:
        separator = b" " if isinstance(value, bytes) else "\n"
        value = separator.join(value for _ in range(copies))
    if item["extra"].get("pad"):
        width = (32, 128, 512, 2048, 8192, 16384, 32768, 65536)[variant // 8]
        value = "x" * width + " " + value
    case = {
        "id": (
            f"{'hold' if cohort == 'holdout' else 'cal'}"
            f".broader.{item['name']}.{variant:02d}"
        ),
        "cohort": cohort,
        "category": f"broader-{item['name']}",
        "api": item["api"],
        "lifecycle": item["lifecycle"],
        "pattern": item["pattern"],
        "string": value,
        "ops": max(1, min(128, 96 // copies)),
        "weight": 1,
        "flags": list(item["flags"]),
        **{
            key: extra
            for key, extra in item["extra"].items()
            if key != "pad"
        },
    }
    if case["api"] == "compile":
        case["ops"] = max(2, 8 // copies)
    return case


def raw_key(case):
    return tuple(
        (key, stable_value(value))
        for key, value in sorted(case.items())
        if key not in {"id", "cohort", "category"}
    )


def audit():
    raw_collisions = Counter()
    effective_collisions = Counter()
    within = {}
    for index, item in enumerate(SPECS):
        family = item["name"]
        groups = {
            cohort: [original_case(cohort, index, variant) for variant in range(VARIANTS)]
            for cohort in ("calibration", "holdout")
        }
        for cohort, family_cases in groups.items():
            unique = {semantic_key(case) for case in family_cases}
            within[f"{cohort}:{family}"] = {
                "variants": len(family_cases),
                "unique_effective_operations": len(unique),
                "duplicate_effective_operations": len(family_cases) - len(unique),
            }
        for practice, unseen in zip(
            groups["calibration"], groups["holdout"], strict=True
        ):
            if raw_key(practice) == raw_key(unseen):
                raw_collisions[family] += 1
            if semantic_key(practice) == semantic_key(unseen):
                effective_collisions[family] += 1

    expected = {family: VARIANTS for family in EXPECTED_COLLIDING_FAMILIES}
    if dict(sorted(raw_collisions.items())) != expected:
        raise RuntimeError(
            "the rejected reconstruction does not reproduce all 1,216 observed collisions"
        )
    source = Path(__file__)
    return {
        "schema": "rebar-performance-v7-rejected-seed-collision-v1",
        "status": "REJECTED",
        "measurement": "Untimed reconstructed semantic-independence audit; not a performance result.",
        "prototype_source_sha256": "NOT MEASURED",
        "prototype_fixture_sha256": "NOT MEASURED",
        "reconstruction_runner_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "provenance": (
            "Reconstructed from the observed rejected templates. "
            "The original prototype source and fixture hashes were not captured."
        ),
        "compared_cohort_pairs": len(SPECS) * VARIANTS,
        "colliding_cohort_pairs": sum(raw_collisions.values()),
        "colliding_families": len(raw_collisions),
        "variants_per_affected_family": VARIANTS,
        "affected_families": dict(sorted(raw_collisions.items())),
        "effective_semantic_collisions": sum(effective_collisions.values()),
        "effective_colliding_families": dict(sorted(effective_collisions.items())),
        "within_family_effective_uniqueness": dict(sorted(within.items())),
        "total_within_family_duplicate_effective_operations": sum(
            item["duplicate_effective_operations"] for item in within.values()
        ),
        "finding": (
            "Separate random seeds do not create independent unseen inputs when a "
            "family never substitutes randomized values into its actual operation."
        ),
        "resolution": (
            "Render independently seeded text, bytes, and compile/escape patterns. "
            "Require 64 unique executable scenarios per family and disjoint "
            "practice and unseen semantic sets before freezing."
        ),
        "timing": "NOT MEASURED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", default="performance/v7/evidence/seed-collision-audit.json"
    )
    args = parser.parse_args()
    result = audit()
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "schema": result["schema"],
                "status": result["status"],
                "compared_cohort_pairs": result["compared_cohort_pairs"],
                "colliding_cohort_pairs": result["colliding_cohort_pairs"],
                "colliding_families": result["colliding_families"],
                "effective_semantic_collisions": result["effective_semantic_collisions"],
                "total_within_family_duplicate_effective_operations": result[
                    "total_within_family_duplicate_effective_operations"
                ],
                "output": str(destination),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
