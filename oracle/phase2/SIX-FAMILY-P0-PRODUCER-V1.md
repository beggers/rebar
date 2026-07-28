# Six independent, from-scratch Python regex engines: frozen correctness producer

The purpose is to discover whether a regex engine built from scratch can replace Python’s `re` without changing its behavior. This document freezes a producer that can eventually run the **same original 31,237 correctness cases** against six independently owned engines written in Rust, C, Zig, C++, Go, and Fortran. It does not count a Python adapter, foreign-function interface, external regex library, or second configuration of an engine as another candidate.

This is a source and evidence freeze, not a claim that six engines already pass. Historically, three engine families have been runnable on the original correctness gate. **Correctness-qualified candidates: 0. Speed: NOT MEASURED. Memory: NOT MEASURED. Holdout: NOT OPENED.** No winner has been chosen.

## Exactly the original correctness cases

The baseline is the pinned, unmodified, isolated CPython 3.14.6. The producer preserves every original suite, case count, source hash, case-matrix hash, original baseline-record hash, published full-width seed, and real execution method. It neither creates replacement cases nor reuses hardcoded answers.

| Original suite | Cases |
| --- | ---: |
| Original CPython upstream behavior | 151 |
| Public Python API | 864 |
| Scanners and callbacks | 1,024 |
| Buffer and memory-view handling | 768 |
| Managed buffer lifetimes | 1,024 |
| Verbose scanners and comments | 2,854 |
| Public type identity and serialization | 6,912 |
| Substitution and buffer semantics | 5,120 |
| Buffers that change shape | 10,240 |
| Complete public surface and locales | 1,376 |
| Independent Python interpreters | 128 |
| Python buffer exporters | 264 |
| Simultaneous shared-pattern threads | 512 |
| **Total: 13 original suites** | **31,237** |

The upstream inventory contains 152 original public records: 151 counted cases and one genuine debug-build skip. There are exactly 13 previously named private waivers and no new waivers. Locale tests preserve their actual 64 locale cases and 192 transitions. Thread tests preserve actual simultaneous workers and barriers. Buffer, callback, scanner, exception, type-identity, serialization, and lifetime cases retain their original evaluator and original baseline comparison.

For the successful interpreter-lifecycle obligation, **128 counted cases require 394 actual case-execution calls, 11 created and destroyed interpreters, 11 initialization and guard-cleanup calls, and 8 fresh temporary interpreters**. A separately recorded failed Zig run made 385 case-execution calls, created and destroyed only 3 interpreters, attempted 4 cleanup calls, and had 3 cleanup failures. Those 385 calls produced **zero passing nested-interpreter cases** and must never be represented as successful.

## Six genuinely separate implementations

The machine-readable freeze names and hashes all **25 distinct, first-party semantic source files**. Each family owns its parser, compiler, execution path, native code, and Python-facing adapter. No family may borrow another family’s engine, Python’s `re`, `_sre`, CPython’s regex engine, an external regex package, saved oracle answers, or a fallback implementation.

| Engine family | Independently owned source files | Native ownership |
| --- | ---: | --- |
| Rust | 9 | Separate Rust engine and owned Python bridge |
| C | 2 | One owned native C engine and bridge |
| Zig | 3 | Separate Zig engine and owned Python bridge |
| C++ | 4 | One owned native C++ engine and bridge; `Match` belongs to its Python adapter |
| Go | 4 | Separate Go engine and owned Python bridge |
| Fortran | 3 | Separate Fortran engine and owned Python bridge |
| **Total** | **25** | **No shared semantic source files** |

Combined engine-and-bridge ownership is valid for C and C++ only. Go uses its own native `compile` and `execute` interface. C++ and Fortran use their own `compile`, `subject`, and `run` interface. In particular, the C++ adapter owns its `Match` class; requiring the combined native bridge to own that class would falsely reject its genuine architecture. These distinctions describe frozen source ownership, not candidate correctness.

## Preserve every real failure

The current historical record has **61 independently verified, distinct evidence-file owners**: 51 previously frozen candidate-evidence owners, 6 genuine V4 source-build-evidence owners, and 4 real V5 Go and Fortran failure-evidence owners. The historical snapshot embedded inside the already-frozen V5 source-build document remains **57**. It describes its own earlier point in time and is not rewritten or presented as a 61-owner snapshot.

The actual V5 Go build failed after **5 of 26 expected compiler and inspection processes**, with **zero completed build phases**. Its Go engine built, but the separate C bridge failed on `SSIZE_MAX`. The complete bridge diagnostic is 2,640 bytes with SHA-256 `6477560bffdde31d9422ba4c8addbb1a733cb0becbd09b5815d51d837caf477a`. The signed compressed failure archive is 5,595 bytes with SHA-256 `ff92f5f182307b5e6e123ab883e630c6aca63f8c75318fa4ac083b1d72db6169`; its complete uncompressed report is 18,380 bytes with SHA-256 `7dfa02625cb532d2dd65491a65ca8a04848041fc6dc2fd5547bac2e3c8b7a685`. The genuine publication receipt is 2,903 bytes with SHA-256 `00a126f6c462913ad00ea9961334bbeb5aa2bfd1301d02d8f8c5d55c2e239db0`.

The actual V5 Fortran build ran **all 26 of 26 compiler and inspection processes successfully** and completed **both build phases**, but correctly failed because the independently rebuilt engine was not reproducible. Both engine files were 74,624 bytes; their respective SHA-256 values were `6f005b6f1ec68658857ee2ba9c21e21d65cd4c41aa8fd608d6060712db63164a` and `0d1f94c1b51e0cf6527ce742c092bffe9f0ae1207b0414bab6b5be56e9b7f092`. Both 37,424-byte bridges had the identical SHA-256 `0e4197e9b16df93f5d29333fcfda928d1d29c193c0449afb730146819229faf8`. The signed compressed failure archive is 26,274 bytes with SHA-256 `eadf8844a1bda48d2420c7b3311ced77de9fda7ccfb806f73764550080823e53`; its complete uncompressed report is 167,482 bytes with SHA-256 `4e3a8a2e9cb03fe12105f40499da6055b9adb3336667b9af801579106b991996`. The genuine publication receipt is 2,848 bytes with SHA-256 `f9bf0a652e9c10c949d7b5faabf261d3931681548d4f5d1af69f0accc6d742f2`.

For both failures, a receipt marked `PASS` means **the failure evidence was published successfully**. It does not mean that its source build passed, an engine was activated, a correctness suite ran, or a candidate qualified. The existing reversible activation authenticates successful frozen V4 builds only; no V5-aware activation has been frozen. Consequently V5 activation fails closed, and the producer cannot build, install, promote, activate, or silently substitute any native engine.

## Safe, reproducible verification

The following source-only checks execute no candidate, reference worker, build, activation, interpreter, thread, subprocess, timing trial, benchmark, or holdout. They perform no file writes:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/run_owned_six_family_original_p0_producer_v1.py --self-test

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/run_owned_six_family_original_p0_producer_v1.py --self-test
```

For full, read-only verification, replace each uppercase placeholder with the independently computed complete SHA-256 of the producer source, this prose protocol, and `oracle/phase2/six-family-p0-producer-v1.json`, respectively:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/run_owned_six_family_original_p0_producer_v1.py \
  --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --document-sha256 DOCUMENT_SHA256

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/run_owned_six_family_original_p0_producer_v1.py \
  --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --document-sha256 DOCUMENT_SHA256
```

The full verification authenticates the immutable original oracle, all 13 source suites, the exact six-family and 25-source contract, the independently frozen V7 candidate context, the frozen V5 source-build context, all 61 distinct signed historical evidence owners, and both complete actual V5 failure reports. Changed, omitted, duplicated, redirected, symlinked, or misrepresented owners are rejected. It reports **0 qualified candidates**, **NOT MEASURED** performance and memory, and **NOT OPENED** holdout.
