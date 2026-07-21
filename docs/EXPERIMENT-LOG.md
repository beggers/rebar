# Experiment log

This log preserves the chronological work behind the concise [README](../README.md). Every linked report keeps its raw measurements, generated charts, losses, and reproduction details.

## Correctness

- The [original matrix](../oracle/v1/P0.md) freezes 2,048 CPython 3.14.6 cases and 38 obligations. The original fixture SHA-256 is `983885ee6411fd806edf3d72efbcc989f9b9f7775a6d127dc7c865673eeb0fed`.
- The [expanded matrix](../oracle/v2/P0.md) freezes 8,244 cases and 45 obligations, adding bytes-like inputs, standard object behavior, warnings/errors, lookbehind references, and deeper seeded cases. Fixture SHA-256 is `ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2`.
- The [initial expanded check](../oracle/v2/evidence/INITIAL.md) preserves the 42 native/Python and 386 Rust gaps it exposed. The [native](../oracle/v2/evidence/NATIVE-QUALIFIED.md), [Python](../oracle/v2/evidence/AST-QUALIFIED.md), and [Rust](../oracle/v2/evidence/RUST-QUALIFIED.md) qualification reports close every gap. Both native engines pass sanitizer checks; all three pass the no-delegation audit.
- The [official CPython 3.14.6 `re` test gate](../oracle/cpython-3.14.6/README.md) adds 146 public test methods, 403 historical patterns, and 11 upstream benchmark patterns. Stdlib self-check is clean (144 pass, two locale skips). Initial results reveal 46 native, 50 Python, and 50 Rust failures, including two native timeouts and three Rust crashes. This invalidates a general drop-in claim until buffer behavior, Unicode/error edge cases, `Scanner`, overflow safety, and historical regressions are fixed.

## Candidate discovery

The [discovery report](../candidates/evidence/DISCOVERY.md) preserves rejected binding experiments and their raw losses. The three independent families are the [Python backtracker](../candidates/AST.md), [native bytecode/C engine](../candidates/VM.md), and [Rust continuation/FFI engine](../candidates/RUST.md). Their parsers and executors are independent.

The broader [engine and language survey](../candidates/evidence/ENGINE-SURVEY.md) records 32 focused semantic checks and all 403 official historical patterns across PCRE2, Oniguruma, ICU, POSIX through Zig, Go/RE2, Node, and Perl, plus separate checks of the Python `regex` package. Current PCRE2 comes closest on spans/syntax (399/403) but still differs on important Python rules; Zig/POSIX is incompatible (212/403). These are discovery-only probes: the clarified scope requires every production candidate, including Zig, to implement its parser/compiler/executor from scratch.

## Original performance experiments

The [original protocol](../performance/v1/PROTOCOL.md) freezes 16 practice and 16 holdout tasks. Each experiment retains all 1,152 paired rows and every loss.

| Experiment | Result and evidence |
| --- | --- |
| Discovery pilot | [Pilot](../performance/v1/evidence/PILOT.md) exposes repeated Python/native boundary cost; [native-search follow-up](../performance/v1/evidence/PILOT-NATIVE-SEARCH.md) measures moving the search into C. |
| First paired run | [Initial results](../performance/v1/evidence/INITIAL-RESULTS.md): native C is 0.1141× overall on holdout and clearly faster on 1/16; Python and Rust are much slower. |
| Native batching | [Native batch](../performance/v1/evidence/NATIVE-BATCH.md): repeated calls cross into C once; native C improves to 0.3291× and 2/16 clearly faster. |
| Rejected stack state | [Rejected experiment](../performance/v1/evidence/STACK-STATE-REJECTED.md): correctness-clean but slower at 0.2435×; the slower executor is removed and the result is preserved. |
| Native public API | [Native public API](../performance/v1/evidence/NATIVE-PUBLIC.md): result construction and common paths move to C; 1.1178× overall, 8/16 clearly faster, four large slowdowns. |
| Compact native paths | [Compact paths](../performance/v1/evidence/COMPACT-PATH.md): 1.3067× overall, 10/16 clearly faster, no large holdout slowdown. |
| One-pass and structured loop | [One-pass](../performance/v1/evidence/ONE-PASS.md) and [structured-loop](../performance/v1/evidence/ONE-PASS-LOOP.md) preserve two near misses. |
| Final original run | [Final result](../performance/v1/evidence/FINAL-CANDIDATE.md): native C reaches **1.5597×** holdout speed (1.5363–1.5840× measured range), clearly faster on **14/16**, with **zero** large holdout slowdowns. One practice slowdown is Unicode word-boundary scanning. |

## Expanded performance oracle

The [expanded protocol](../performance/v2/PROTOCOL.md) freezes 28 practice and 28 distinct holdout tasks, covering more APIs, inputs, compilation, scanning, empty matches, backreferences, conditionals, and Python/native boundary costs. Its fixture SHA-256 is `ec2f7194e8bfb4f5438a61abc3d893e18e5fcada13d2de583801b7e28e7b8f1a`.

The [initial expanded result](../performance/v2/evidence/INITIAL.md) retains all 2,464 correctness-gated rows and 119 large slowdowns. Native C is **1.1619×** overall on holdout (1.1482–1.1758× measured range), clearly faster on **19/28**, with four holdout slowdowns: empty-position iteration, escaping bytes, scanning, and repeated match-object access/expansion. Practice adds general token/Unicode matching and controlled branches. Python and Rust are clearly faster only on cold compilation and are much slower on matching calls. These measurements motivate profiling the native boundaries and general paths before the next run.

The [broader v3 protocol](../performance/v3/PROTOCOL.md) expands coverage to **72 practice + 72 holdout tasks**, preserving the first 56 records exactly and adding realistic logs/URLs/configuration/text-cleanup/input/API/window cases. It increases paired trials to 13 and bootstrap samples to 5,000. The frozen fixture SHA-256 is `f3ab490e351648118e522035c8624976203c777d9c1a7f7d44ad98233f2056bf`. Its first correctness gate passes 568/576 comparisons and exposes six unsupported windowed-scanner calls plus two native multiline first-line misses; raw failures are preserved. v3 performance is **NOT MEASURED** until those and the official-suite gaps are resolved.

The [window and multiline follow-up](../performance/v3/evidence/WINDOW-QUALIFIED.md) closes all eight new cases and passes **576/576** pre-timing comparisons. It adds documented compiled-pattern keyword/window handling to all engines and corrects an unsafe native multiline shortcut. Full official-suite reruns improve native to 99/144 and Python/Rust to 95/144 runnable methods; remaining failures, crashes, and timeouts are preserved and continue to block timing.
