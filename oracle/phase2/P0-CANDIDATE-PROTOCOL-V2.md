# Full Python `re` compatibility gate, version 2

This protocol tests each independently written Rust, C, and Zig engine against the same pinned CPython 3.14.6 correctness standard. A candidate passes only after its own freshly source-built native engine actually passes every original test.

This is a correctness protocol. Performance, memory, the expanded final holdout, and a winner are **NOT MEASURED**. Freezing or passing this protocol does not authorize a benchmark.

## What cannot change

The immutable objective is SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`. The complete published phase-one inventory is SHA-256 `cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f`. Preserve the published version-one candidate runner, its protocol, all 73 public obligations, all 34 obligation mappings, all 13 individually named private waivers, and the sole genuine debug-build skip.

| Frozen Python correctness category | Counted actual candidate cases |
| --- | ---: |
| Original CPython test methods | 151 |
| Public Python API | 864 |
| Stateful scanning | 1,024 |
| Memory views and expansion | 768 |
| Managed buffer lifetime | 1,024 |
| Verbose expressions and comments | 2,854 |
| Public types, identity, and serialization | 6,912 |
| Substitution and buffer semantics | 5,120 |
| Shape-changing buffer semantics | 10,240 |
| Public flags, errors, and genuine locales | 1,376 |
| Real isolated Python subinterpreters | 128 |
| Real Python buffer exporters | 264 |
| Real simultaneous shared-pattern threads | 512 |
| **Total** | **31,237** |

The original CPython worker must retain all 152 public result records: 151 actual runnable cases and exactly one real `ReTests.test_memory_leaks` debug skip. It must also retain all 13 original named private waivers. Do not count the skip as a pass or quietly drop its record.

The machine-readable inventory fixes every original suite owner, recorder owner, matrix hash, source-ordered reference-vector hash, exact case count, comparison, and execution route. In particular, the managed-buffer candidate recorder is `record_independent_managed_buffer_candidates_v1.py`; the managed baseline-only recorder cannot execute a candidate. Substitution version 2 uses its separately frozen version-3 candidate recorder. Preserve each genuine producer's own baseline label, receipt, canonical JSON, archive format, escaped Unicode, and digest convention.

## Require an actual, independently reproduced native engine

Require the published version-2 native source-build controller, SHA-256 `e822e22cf6a5bbbdc2b634209c6e185ca74ebc55d86828ebea77bb5d44ce3796`, and its protocol, SHA-256 `f383c2ca419c18cf77451c855b53593bb97ea7fa83c90d5d133a80de043aa603`. Verify the complete caller-pinned genuine archive and durable receipt, both separately executed fresh source-build phases, identical native bytes, complete family source closure, exact ELF symbols, and the actual native Python bridge.

A pre-existing binary, historical version-one build, sibling engine, external regex package, Python's `re`, `_sre`, guessed build root, or unproved adapter is never a source-build result.

Before any candidate import, require the separately published canonical native activation controller and protocol. The caller must independently pin their exact actual published SHA-256 values, the complete actual activation report, and its durable receipt. An intermediate or previously falsified activation source is never a published authorization.

Require an owner-only mode-0700 recovery root, complete original-binary backups, an independently authenticated recovery journal, adjacent atomic native promotion, same-inode and exact-byte readback, file and directory synchronization, the exact two-source-build output, and a complete reversible rollback. Import the actual candidate only from the unchanged canonical project root.

**Never copy an original matcher guard, change any frozen guard's `ROOT`, replace a Python source file, or bypass the original warning and object-identity quarantine.** All 13 suites must use the unchanged original continuous version-5 guard before and after matching operations. Activation alone is not a candidate correctness pass.

## Run the original producers

Run each original source-owned producer in its own pinned isolated CPython process. Use the original version-five isolated candidate worker for upstream CPython methods and the unchanged common version-three controller for public, scanner, and buffer categories. Use each of the five original candidate recorders and its own frozen baseline archive, receipt, source, genuine audit, and durable output. Do not make the incompatible recorder interfaces interchangeable.

Execute the actual PEP 688 exporter and buffer-release callbacks. For public-surface compatibility use the real version-17 evaluator, version-19 cycle-safe normalizer, independently generated ISO-8859-1 and UTF-8 locales, all 64 original locale cases, all 192 genuine locale transitions, and complete locale restoration.

Execute all 512 thread cases in the original simultaneous cohorts. Require 32 genuine thread starts and joins, 1,024 actual thread-side case executions, 2,176 real regex calls, all barriers, complete failure and lifecycle records, and the exact warning vector `f28af6781328eacabdbe96460e8c54cba1e7802f6a052cefb4a7c59f30ce4413`.

Run only the separately published genuine candidate subinterpreter recorder; explicitly pin its exact source, machine protocol, and explanation. Require 11 actually created and destroyed interpreters, all 394 actual source-owned A/B/A and fresh-case observation executions, 11 genuine guard initialization calls, 11 cleanup calls, real descriptor end-of-file, exact locale restoration, and the complete original frozen case identities.

Preserve every matching observation. Remove only the Python-reference-only `candidate_imports` and `stdlib_origin_verified` root fields; replace them with actual independently authenticated native ownership. Rename exactly the following implementation-identity fields without changing their values:

| Python reference observation | Actual independent candidate observation |
| --- | --- |
| `actual_stdlib_reimport` | `actual_engine_reimport` |
| `match_is_stdlib_match` | `match_is_engine_match` |
| `module_identity` | `engine_sysmodules_identity_verified` |
| `pattern_is_stdlib_pattern` | `pattern_is_engine_pattern` |
| `reimported_origin_verified` | `engine_reimported_origin_verified` |
| `stdlib_owner` | `engine_sysmodules_owner_verified` |
| `stdlib_re_module` | `engine_module_name_verified` |

The exact compact, no-trailing-newline, losslessly projected original vector is SHA-256 `cf5633c8dc1038d650603eee421371285d0e32f6446190ce728590f1f5c55021`. Reject changed observations, owner collisions, main-interpreter replay, false reference ownership, cross-family imports, and any omitted actual interpreter lifecycle.

## Preserve results and failures

Publish complete success and failure evidence exclusively to new, no-follow paths:

```text
oracle/phase2/evidence/frozen-p0-candidate-v2-FAMILY-LABEL.json.gz
oracle/phase2/evidence/frozen-p0-candidate-v2-FAMILY-LABEL-publication-receipt.json
oracle/phase2/evidence/frozen-p0-candidate-v2-FAMILY-LABEL-failures.json.gz
oracle/phase2/evidence/frozen-p0-candidate-v2-FAMILY-LABEL-failures-publication-receipt.json
```

Retain the complete per-suite candidate records or each genuine recorder's independently authenticated complete archive and receipt. Keep full process stdout and stderr, real process identities, all mismatches, crashes, signals, timeouts, actual producer failures, real thread failures, and subinterpreter cleanup failures. Never overwrite an old archive, conceal stderr, retry a failed case as a pass, or claim qualification unless all 13 actual suites and all 31,237 counted cases pass.

## Reproduce the source-only checks

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/run_frozen_p0_candidate_v2.py --self-test

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/run_frozen_p0_candidate_v2.py --self-test
```

Both tests are synthetic: no file reads or writes, real candidate imports, builds, native promotion, guard changes, reference workers, candidate workers, interpreters, threads, garbage collection, clocks, hidden cases, performance files, or holdout access.

The first version of this source-only test genuinely failed in both environments: `reject-forged-interpreter-rust-candidate_import_count`. Its original draft SHA-256 was **NOT CAPTURED**. The initial hostile fixture incorrectly treated changing a valid import count from 1 to 2 as a failure. The actual requirement is at least one genuine candidate import. The corrected hostile control tests the truly invalid count of zero. Preserve this falsification; do not describe the initial run as a pass.

This source and protocol freeze neither executes nor qualifies any candidate. Until separately published version-two source-build, canonical-activation, real-subinterpreter, and complete 13-suite evidence exists, candidate correctness remains **NOT MEASURED**.
