# Benchmark Plan

## Purpose

This document defines how `rebar` will measure performance against CPython once correctness is held constant. It turns the compatibility contract in [`docs/spec/drop-in-re-compatibility.md`](../spec/drop-in-re-compatibility.md) and the parser boundary in [`docs/spec/syntax-scope.md`](../spec/syntax-scope.md) into a reproducible benchmark methodology for compile-path, match-path, and module-boundary work so later implementation tasks can build without guessing what "faster" means.

The immediate goal is not broad regex-engine performance claims. The immediate goal is to measure:

- parser and compile-path cost
- small match-path and Python-facing module overhead for importable `re`-compatible entry points
- cold-versus-warm behavior where cache state changes the result

## Reference Boundary

- Initial baseline: CPython `3.12.x`, matching the syntax target in [`docs/spec/syntax-scope.md`](../spec/syntax-scope.md).
- Initial assumption: early benchmark runs may use one concrete `3.12.x` interpreter while the prose plan still names the `3.12.x` family.
- Required follow-up: record the exact CPython patch release, build flags, and platform metadata in benchmark artifacts; if patch-level drift materially changes timing-sensitive behavior, pin the benchmark oracle to that exact build instead of averaging multiple `3.12.x` variants together.
- Initial implementation shape: a Rust core exposed through CPython, with benchmarks entering through Python-facing surfaces when the measured question is user-visible module cost.

## Guiding Rules

- Correctness gates performance claims. Do not publish benchmark wins for behavior that is not yet proven compatible.
- Separate parser cost from public-module overhead so "parser got faster" is not confused with "drop-in `re` use got faster."
- Separate compile-path benchmarking from later regex execution benchmarking. Matching-engine speed is a later phase and should not be smuggled into parser claims.
- Prefer reproducible local-machine runs over elaborate infrastructure requirements. A developer should be able to reproduce the published suite from a normal checkout on a single host.
- Record enough environment metadata that future runs can explain variance instead of treating every result as comparable by default.
- Favor stable machine-readable outputs over prose-only benchmark summaries.

## Benchmark Questions

The benchmark harness should answer these questions explicitly:

1. How long does `rebar` take to parse and compile representative `re` patterns compared with CPython?
2. How much overhead does the Python-facing module boundary add for common entry points such as `compile`, `search`, and `match`?
3. How much do cache hits, cache misses, and first-import paths change the observed cost?
4. Are claimed wins consistent across `str` and `bytes` workloads, or are they narrowly concentrated in one text model?

If a benchmark does not answer one of those questions, it should probably be deferred.

## Benchmark Families

The suite should be split into two primary families plus one explicit deferred family.

### Family 1: Parser And Compile Benchmarks

These measure pattern parsing and compilation cost as directly as the implementation allows.

Primary workloads:

- cold compile of valid patterns, with cache effects disabled or neutralized
- repeated compile of the same valid patterns, reported separately so cache behavior is visible
- compile of representative invalid patterns when diagnostics are part of the measured code path
- parser metadata extraction cost, if `rebar` exposes an internal benchmark hook that isolates parse/compile from later module plumbing

Workload buckets:

- tiny literals and anchors
- medium mixed patterns using alternation, grouping, and character classes
- heavy parser-stress patterns using nested groups, lookarounds, possessive quantifiers, atomic groups, scoped flags, and backreferences
- mirrored `str` and `bytes` cases where the grammar differs in user-visible ways

Measurement target:

- primary metric: median time per compile operation
- derived metrics: operations per second, speedup ratio versus CPython, and spread statistics

Notes:

- Parser benchmarks should prefer a dedicated benchmark adapter or cache-neutral compile path once one exists.
- Until that adapter exists, cold `compile()` benchmarks are the acceptable proxy, but the scorecard should label them as compile-path rather than pure-parser measurements.

### Family 2: Python-Facing Module Benchmarks

These measure cost at the public `re` boundary where users actually call the replacement module.

Primary workloads:

- import cost for the `rebar` module surface versus standard-library `re`
- module-level `compile()` on cold and warm cache paths
- module-level `search()` and `match()` on tiny inputs chosen to keep matching work small relative to module overhead
- pattern-object `search()` and `match()` after precompilation, reported separately from module-level helpers
- cache-sensitive flows such as repeated `compile()` before and after `purge()`

Workload buckets:

- cheap literal or anchored patterns over tiny haystacks to expose boundary overhead
- small no-match and single-match cases so success and failure paths are both visible
- mirrored `str` and `bytes` cases

Measurement target:

- primary metric: median time per public API call
- derived metrics: import latency, steady-state latency, cold-versus-warm delta, and speedup ratio versus CPython

Important boundary:

- These benchmarks are allowed to include some matching cost because the public APIs do.
- They must use intentionally small workloads and label results as module-boundary benchmarks, not engine-throughput benchmarks.

### Deferred Family: Regex Execution Throughput

This family is intentionally out of scope for the first benchmark harness.

Deferred examples:

- large-haystack scan throughput
- replacement-heavy `sub` and `subn` workloads
- catastrophic-backtracking stress tests
- memory-allocation and peak-resident-set analysis for full matching workloads

Those measurements matter later, but they should be introduced only after parser and module-boundary benchmarking already exist and the project can distinguish compile cost from engine cost.

## Workload Design

Benchmark workloads should come from a small, versioned corpus rather than ad hoc snippets.

Recommended workload sources:

- construct-family examples derived from [`docs/spec/syntax-scope.md`](../spec/syntax-scope.md)
- module-surface operations derived from [`docs/spec/drop-in-re-compatibility.md`](../spec/drop-in-re-compatibility.md)
- regression workloads added when correctness or performance investigations uncover a stable hot path or cliff

Each workload record should capture at least:

- workload id
- family: `parser` or `module`
- operation, such as `compile`, `module.search`, or `pattern.match`
- pattern
- flags
- text model: `str` or `bytes`
- optional haystack or replacement payload
- cache mode: `cold`, `warm`, or `purged`
- short category labels, such as `literal`, `lookbehind`, `atomic`, or `bytes-class`

The initial corpus should stay intentionally small and representative. A benchmark plan that needs hundreds of workloads before it can run is too heavy for the current phase.

## Baseline Comparison Strategy

Every published benchmark should compare the same workload against:

1. baseline CPython `re`
2. `rebar` through its intended CPython-facing surface

Comparison rules:

- Use the same interpreter process model for both sides unless the benchmark explicitly measures import-startup differences.
- Use the same benchmark driver, workload data, and warmup policy for both sides.
- Report absolute timings for each side plus a relative speedup ratio.
- Treat CPython `re` as the baseline denominator for ratio calculations.
- Do not compare across machines, operating systems, or Python builds without making that environment change explicit in the scorecard metadata.

Parser-only comparisons may later use a narrower `rebar` parse hook and a CPython proxy compile path, but the scorecard should still declare that asymmetry clearly.

## Warmup, Noise, And Reproducibility

Benchmark noise handling must be explicit because the project is trying to make falsifiable performance claims.

Recommended policy:

- use a benchmark runner that supports repeated process runs and warmup, such as `pyperf`, or implement equivalent behavior deliberately
- run untimed warmup iterations before collecting measurements
- collect multiple timed samples per workload, not one long wall-clock total
- prefer median as the primary summary statistic
- also record spread data, such as standard deviation, interquartile range, or min/max sample bounds
- discard obviously broken runs only through documented runner rules, not by manual cherry-picking
- avoid running unrelated heavy workloads on the same machine during a publishable benchmark session
- capture CPU model, core-count visibility, OS, Python build, and benchmark runner version in the report metadata

Recommended local-run discipline:

- use the same power/performance governor and comparable machine load for baseline and implementation runs
- pin process affinity or use runner-supported CPU isolation when practical, but keep the default workflow usable without privileged machine tuning
- record whether the run happened on a developer workstation, CI host, or dedicated benchmark VM

## Cache And First-Use Policy

Cache behavior is part of the measurement plan because it materially changes user-visible cost.

The harness should report at least three states when relevant:

- `cold`: first compile or import path with no pre-existing cache entry
- `warm`: repeated call path where the same pattern and flags are already cached
- `purged`: call path immediately after invoking `purge()` or an equivalent cache reset fixture

Rules:

- never mix cold and warm samples into one aggregate metric
- clearly label whether an operation includes import cost, compile cost, cache lookup cost, or all three
- if cache semantics differ temporarily during implementation, publish that as a known gap rather than hiding it behind a blended benchmark

## Incremental Delivery Path

The benchmark harness should be built in stages that leave behind usable artifacts.

### Phase 0: Runner Skeleton

Deliver:

- a benchmark entry point
- a workload manifest format
- a CPython baseline adapter
- a placeholder `rebar` adapter
- a minimal scorecard writer for `reports/benchmarks/latest.py`

Exit criteria:

- one or more `compile()` workloads can run end to end against CPython and the placeholder adapter

### Phase 1: Compile-Path Suite

Deliver:

- cold and warm `compile()` workloads
- representative parser workload buckets tied to the syntax-scope document
- baseline-versus-implementation timing comparison
- environment metadata capture

Exit criteria:

- the scorecard publishes parser-family timings and speedup ratios

### Phase 2: Module-Boundary Suite

Deliver:

- import benchmarks
- module-level `compile`, `search`, and `match` workloads
- pattern-object `search` and `match` workloads
- cache-state reporting for cold, warm, and purged paths

Exit criteria:

- the scorecard distinguishes parser-family results from module-boundary results

### Phase 3: Regression And Stability Expansion

Deliver:

- curated regression workloads for performance cliffs
- trend-friendly comparison outputs
- optional CI smoke mode that runs a smaller subset without pretending to be the publishable benchmark

Exit criteria:

- the published scorecard can highlight both current timings and known unstable or regressed workloads

## Recommended Benchmark Runner Shape

The exact implementation language can be chosen later, but the harness should likely be thin Python around the CPython extension boundary.

Recommended pieces:

- a workload manifest module, preferably ordinary Python data checked into the repo
- a Python benchmark runner that can invoke CPython `re` and `rebar` symmetrically
- optional internal adapters for parser-only hooks once the Rust implementation exposes them
- a scorecard writer that emits stable machine-readable output

This keeps the harness close to the user-visible import boundary while still allowing narrower parser measurements later.

## Benchmark Scorecard Shape

`reports/benchmarks/latest.py` should publish a stable top-level shape even before every benchmark family exists. Temporary ad hoc runs can still target caller-selected `.json` paths when a scratch artifact is more convenient.

Recommended top-level fields:

- `schema_version`: integer version for future scorecard evolution
- `generated_at`: UTC timestamp for the report
- `baseline`: object describing the CPython oracle and version family
- `implementation`: object describing the tested `rebar` revision or build
- `environment`: object describing the host and benchmark runner
- `summary`: object with suite totals and headline comparisons
- `families`: object keyed by benchmark family name
- `workloads`: array of per-workload benchmark records
- `deferred`: array of benchmark areas intentionally not yet measured
- `artifacts`: object pointing to optional raw sample files or rendered summaries

Recommended contents for selected fields:

- `baseline`: `python_implementation`, `python_version`, `python_version_family`, `re_module`, and optional build metadata
- `implementation`: `git_commit`, `module_name`, `build_mode`, optional Rust crate/package version, and adapter name if a benchmark hook is used
- `environment`: `hostname`, `os`, `architecture`, `cpu_model`, `logical_cpus`, `runner`, and runner-version metadata
- `summary`: `total_workloads`, `parser_workloads`, `module_workloads`, `median_speedup_vs_cpython`, `parser_median_speedup_vs_cpython`, `module_median_speedup_vs_cpython`, and `known_gap_count`
- `families`: one object each for `parser` and `module`, each with workload counts, readiness notes, and aggregate timing summaries
- `workloads`: each entry should include at least `id`, `family`, `operation`, `cache_mode`, `text_model`, `baseline_ns`, `implementation_ns`, `speedup_vs_cpython`, and a compact variance summary
- `deferred`: each entry should include the omitted benchmark area, why it is deferred, and the follow-up task or milestone if known
- `artifacts`: optional paths to raw sample dumps, runner JSON, or markdown summaries

The scorecard should prefer stable machine-readable values over prose so the README and later dashboards can consume it directly.

## Practical Constraints For The First Harness

- Do not block the first useful benchmark harness on implementing a perfect parser-only hook.
- Do not claim regex-engine wins from tiny `search()` or `match()` module-boundary workloads.
- Do not mix incompatible environments into one scorecard as if the numbers were directly comparable.
- Do not hide unimplemented benchmark families; publish them under `deferred` or readiness notes.
- Prefer benchmark cases that are easy to rerun locally and easy to tie back to the tracked syntax and compatibility specs.

## Follow-Up Implementation Tasks This Plan Enables

- scaffold the benchmark runner and scorecard writer
- define the workload manifest schema and baseline/implementation adapters
- add the first compile-path workload corpus tied to the syntax-scope construct map
- add import and module-boundary smoke benchmarks for `compile`, `search`, and `match`
- publish the first placeholder `reports/benchmarks/latest.py`
- wire README/reporting consumption to the published benchmark scorecard once reports exist

## Open Questions To Settle During Implementation

- Which exact CPython `3.12.x` patch release and build flags will be the first pinned publishable benchmark baseline?
- Will parser-only measurement need a dedicated internal hook immediately, or is cold `compile()` sufficient for the first scorecard?
- Which runner should become the long-term default: `pyperf` directly or a thin wrapper that standardizes workload and scorecard output?
- When should memory metrics join the scorecard, if at all, without distracting from the parser-first objective?

Those questions should be answered by the benchmark harness and follow-up tasking, not left as vague performance goals.
