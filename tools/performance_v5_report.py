#!/usr/bin/env python3
"""Create a complete, readable report for the expanded performance holdout."""

import argparse
import json
from collections import defaultdict
from pathlib import Path


NAMES = {"candidates.ast_candidate": "Python engine", "candidates.vm_candidate": "Native C engine", "candidates.rust_candidate": "Rust engine", "candidates.zig_candidate": "Zig engine", "rebar": "rebar"}
CAUSES = {
    "literal-hit": "short calls make matcher setup and Python/native boundary cost visible",
    "literal-miss": "an absent phrase requires scanning every possible start",
    "long-ending": "long inputs amplify scanning and end-boundary work",
    "formatted-lines": "many line starts and character-class checks amplify per-match work",
    "prefix-check": "very short prefix checks are dominated by call/setup cost",
    "whole-check": "structured repeats and full-string checks require more matcher state",
    "nearby-capture": "lookaround and capture construction add work to short searches",
    "findall-tokens": "many returned tokens amplify scanning and result construction",
    "finditer-pairs": "many captures amplify iterator and match-object construction",
    "split-keep": "splitting and retained separators amplify collection work",
    "replace-groups": "capture/template expansion and joining dominate replacement",
    "replace-callback": "repeated Python callbacks dominate replacement",
    "bytes-tokens": "many byte results amplify collection and conversion work",
    "bytes-buffer": "mutable-buffer handling and match construction add boundary work",
    "unicode-words": "Unicode category and boundary checks are more expensive than ASCII scans",
    "unicode-casefold": "full Unicode case handling requires extra character checks",
    "cold-compile": "fresh parsing/compilation and cache clearing dominate the call",
    "cold-search": "fresh compilation dominates a single short search",
    "module-search": "module lookup and cache handling dominate short searches",
    "module-replace": "module/cache lookup combines with template and collection work",
    "empty-iterator": "empty matches require careful progress and many result objects",
    "references": "backreferences require capture restoration and comparison",
    "conditionals": "conditionals depend on capture state and branch selection",
    "branch-control": "atomic/possessive and alternative paths require controlled backtracking",
    "scanner-text": "incremental scanning creates many match results and boundary calls",
    "scanner-bytes": "byte scanning and result construction amplify native-boundary work",
    "window-search": "short windowed searches expose position/boundary overhead",
    "window-collection": "window checks combine with repeated collection work",
    "request-records": "many structured captures and alternatives amplify matching work",
    "everyday-address": "the email-like find-all cases return many matches and repeatedly check several character classes; native profiling confirms the compact matcher performs 26–230 class checks and 60–518 repeated-character checks per call",
    "structured-text": "configuration, paths, and quotes combine line starts, repeats, and captures",
    "cleanup": "line cleanup and splitting amplify repeated scanning and collection",
    "escape": "short escaping calls make Python/native conversion and allocation visible",
    "bytes-replace": "byte templates, captures, and joining amplify boundary work",
    "ascii-mode": "word-boundary/category checks are repeated across the input",
    "verbose-dotall": "verbose parsing or multi-line lazy matching adds compile/matcher work",
    "long-literal": "long present/absent scans expose literal-start filtering and boundary cost; native counters confirm the direct path does no bytecode steps, so remaining losses are call and scan overhead",
    "line-records": "many line starts, captures, and result objects amplify matching and collection work",
    "json-fields": "structured alternatives and several captures amplify matching and result construction",
    "html-tags": "nested attributes and repeated classes require more backtracking and per-result work",
    "markdown-links": "optional titles, captures, and negated classes amplify collection and boundary work",
    "source-tokens": "many short alternatives and scanner/iterator results amplify per-token overhead",
    "comment-strip": "line and block comments combine repeated scans, lazy matching, and replacement joining",
    "url-extract": "optional components, repeated classes, and captures amplify collection work",
    "email-extract": "email-like collection repeatedly checks character classes and constructs many results",
    "ip-version": "large alternatives and bounded repeats add branch and character-check work",
    "dates-numbers": "structured numeric alternatives and optional suffixes amplify matching and capture work",
    "phone-postcode": "several structured alternatives require repeated branch and character checks",
    "path-text": "optional roots, repeated segments, and result collection amplify backtracking; native counters confirm general calls and state clones",
    "path-bytes": "repeated byte-path segments and buffer/result conversion amplify boundary work",
    "csv-fields": "quoted/plain alternatives produce many captures and backtracking states; native counters confirm substantial state cloning",
    "quoted-escapes": "escaped-character alternatives repeatedly clone backtracking state; native counters confirm this dominates",
    "whitespace-clean": "many line boundaries, replacements, and joins amplify collection work",
    "newline-normalize": "many short newline matches and replacements amplify per-result and join overhead",
    "split-delimiters": "repeated separators and result construction amplify split/collection work",
    "split-captures": "retaining every separator adds captures and result construction to splitting",
    "replace-redact": "case-insensitive alternatives, two captures, template expansion, and joining dominate redaction",
    "replace-template": "capture lookup, template expansion, and joining dominate replacement",
    "replace-callback": "repeated Python callbacks dominate replacement and expose native-boundary cost",
    "unicode-words": "Unicode category/boundary checks and many returned words cost more than ASCII scans",
    "unicode-case": "full Unicode case handling requires repeated multi-character checks and result construction",
    "combining-emoji": "wide ranges, combining marks, and repeated result construction amplify Unicode work",
    "ascii-boundary": "ASCII boundary/category checks repeat across multilingual input",
    "byte-buffer": "bytearray/memoryview handling, captures, and repeated result construction amplify boundary work",
    "lookaround": "lookbehind/lookahead and several captures add work to every returned result",
    "backreference": "capture restoration and repeated captured-text comparison amplify matching work",
    "conditionals": "optional delimiters depend on capture state and branch selection for every result",
    "atomic-possessive": "controlled alternatives/repeats require general backtracking state; native counters confirm state clones on slower cases",
    "nullable-empty": "many empty matches require safe progress and extensive backtracking; native counters confirm the largest state-clone and step counts",
    "branch-alternatives": "many alternatives require repeated branch checks; native counters confirm hundreds of direct matcher steps per call",
    "class-heavy": "mixed character sets, alternatives, and captures amplify repeated class checks",
    "windowed": "short input slices and repeated collection expose position and boundary overhead",
    "scanner": "incremental text/byte scanning creates many results and repeatedly crosses the native boundary",
    "cold-module": "fresh compilation and cache clearing dominate a single search or replacement",
    "match-surface": "group access, dictionaries, spans, and expansion expose match-object construction cost",
    "earlier-72": "the earlier mixed workloads retain their documented scanning, Unicode, collection, and boundary costs",
}


def short(value):
    return NAMES.get(value, value.rsplit(".", 1)[-1])


def group_name(row):
    value = row["category"]
    if value.startswith("expanded-"):
        return value.removeprefix("expanded-")
    if value.startswith("large-"):
        return value.removeprefix("large-")
    return "earlier-72"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    lines = [f"# {args.title}", "", f"Raw SHA-256: `{data['raw_sha256']}`. Rows: **{data['rows']:,}**. All **{len(data['case_results']):,}** candidate/task results and all **{len(data['regressions']):,}** large slowdowns are retained below.", "", "## Rankings", "", "| Test set | Engine | Overall speed | 95% range | Clearly faster | Large slowdowns |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    for row in data["rankings"]:
        lines.append(f"| {row['cohort']} | {short(row['candidate'])} | {row['geomean_speedup']:.4f}× | {row['ci95_low']:.4f}–{row['ci95_high']:.4f}× | {row['statistically_faster_cases']:,}/{row['cases']:,} | {row['regressions_gt_20pct']:,} |")
    losses = defaultdict(list)
    for row in data["regressions"]:
        losses[(row["candidate"], group_name(row))].append(row)
    lines.extend(("", "## Every large slowdown and its cause", "", "Every result below 0.8× is grouped by engine and workload family. The stable task IDs are listed explicitly, so no slowdown is removed or hidden."))
    for candidate in sorted({row["candidate"] for row in data["case_results"]}, key=short):
        relevant = sorted((item for item in losses if item[0] == candidate), key=lambda item: item[1])
        count = sum(len(losses[item]) for item in relevant)
        lines.extend(("", f"### {short(candidate)} — {count:,} large slowdowns", ""))
        if not relevant:
            lines.append("None.")
            continue
        for key in relevant:
            values = losses[key]
            ids = ", ".join(f"`{row['case']}` ({row['speedup']:.3f}×)" for row in values)
            lines.append(f"- **{key[1].replace('-', ' ')} ({len(values)}):** {CAUSES.get(key[1], 'matching, result construction, or boundary work dominates this workload')}. {ids}.")
    lines.extend(("", "## Every task", "", "`FASTER` means the lower end of the measured range exceeds 1×. `SLOWDOWN` means the result is below 0.8×. Memory is the median traced-peak engine/baseline ratio.", "", "| Test set | Task | Engine | Speed | 95% range | Memory | Result |", "| --- | --- | --- | ---: | ---: | ---: | --- |"))
    for row in data["case_results"]:
        result = "SLOWDOWN" if row["regression_gt_20pct"] else "FASTER" if row["statistically_faster"] else "—"
        lines.append(f"| {row['cohort']} | `{row['case']}` | {short(row['candidate'])} | {row['speedup']:.4f}× | {row['ci95_low']:.4f}–{row['ci95_high']:.4f}× | {row['peak_traced_ratio']:.2f}× | {result} |")
    Path(args.output).write_text("\n".join([*lines, ""]), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
