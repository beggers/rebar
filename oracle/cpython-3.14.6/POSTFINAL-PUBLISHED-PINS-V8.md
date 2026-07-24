# Published correctness-report pins: V8

This additive launcher resolves a sequencing problem without editing any
previously frozen source file. It does not run a benchmark, inspect a holdout,
change a matching engine, install an external regex package, replace a Python
module, bypass a no-delegation guard, or guess an audit result.

## Frozen sources and protocols

Authenticate the complete actual bytes before importing any controller:

| Immutable input | SHA-256 |
| --- | --- |
| `tools/postfinal_from_scratch_audit_v8.py` | `14b8daeebfb620eafa778529f6bf11e1a4f48256dd010b25621f4e94666692c6` |
| `tools/postfinal_no_delegation_audit_v8.py` | `bb22b1983c11a896d3639077050dfaac746876ccbb9e4909518fb33d19987c01` |
| `tools/postfinal_current_build_proofs_v8.py` | `0f9e12847855797669206ea89de94948da66c29742d64820a625ce5a6570b313` |
| `candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V8.md` | `5c60e6ce63ff1e4c5593eaafe29971cb3557b1a0389dcd5cf41cfb00647bc399` |
| `oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V8.md` | `76e66c091ae06ad56b8f4e22c76f4db44810cdb512b839201c9cc7cb83f4cfa0` |

Also authenticate immutable `GOAL.md`, the original complete 223,198-observation,
49-category edge producer, the unchanged 393-observation, 64-seeded-case deep
suite and its genuine multi-candidate producer. The actual launcher source is
frozen separately; do not attempt an impossible source self-hash.

## Actual publication order

1. Freeze and push the immutable V8 source-audit controller. Generate its
   exclusive native-ownership report only through the original controller.
   A real failure stays a failure; no later stage may run.
2. Independently observe the SHA-256 of the actual complete passing
   `candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V8.json`.
3. Pass that observed digest explicitly to `--strict-audit
   --base-report-sha256`. Before starting a candidate, validate the exact base
   report bytes, all three actual native-owner results, all 12 owned source
   files, five native ELF roles, all 48 genuine ordinary pickle observations,
   all six actual match representations, all 13 persistent matching guards per
   engine, and the preserved original Rust 16, C 33, and Zig 16 edge failures.
4. Temporarily set only the already-declared
   `postfinal_no_delegation_audit_v8.BASE_REPORT_SHA256` to that authenticated
   actual report digest. Invoke the unchanged frozen strict controller's
   `main(["--audit"])`. Restore the original `None` when it returns. The
   original controller exclusively creates the only authorized strict report.
5. Independently observe the SHA-256 of the complete actual passing
   `candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V8.json`.
6. For each genuine `--qualified-edge` or `--qualified-deep`, provide both
   actual report digests and the exact independent candidate module. Fully
   authenticate and independently validate both original all-family reports
   before any candidate worker. Set only the two originally absent
   `postfinal_current_build_proofs_v8.V8_SOURCE_REPORT_SHA256` and
   `postfinal_current_build_proofs_v8.V8_STRICT_REPORT_SHA256` values in memory;
   invoke the original `main` with its unchanged qualified mode and restore the
   original `None` values afterwards.

The launcher never edits frozen source, invents report fingerprints, changes a
Python module binding, weakens a matcher, changes a regex entry point or poison
guard, reuses a previous family, or substitutes production evidence. All report
validation runs before any original worker. Refuse an existing exact output,
failure, crash, or invalidation target before starting a native owner. The
original controllers continue to exclusively own report and evidence writes.

The official complete CPython V5 correctness oracle follows these real V8
source, strict, original-edge, and original-deep results. No historical or new
campaign report is a prerequisite; a new campaign may start only after the
complete official correctness gates pass.

## Candidate-free control

Run:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/postfinal_published_pins_v8.py --self-test
```

The source-only control reads no report or candidate evidence; imports no
candidate or native engine; starts no worker; writes no file; reads no holdout;
and samples no clock. It authenticates frozen non-evidence source bytes and
this independently pinned protocol, blocks both built-in and `importlib`
candidate imports, exercises more than 100 in-memory poison controls, and
proves that missing, fake, repeated, cross-family, and unobserved report pins
cannot authorize production. Synthetic controls never become evidence.

Performance: **NOT MEASURED**. Holdout: **NOT ACCESSED**.
