# Final benchmark did not open: missing standard-library import

**Incident: the first final command exited with status 1 before opening the sealed benchmark.** The immutable original final-measurement protocol referred to Python's standard-library `time` module without importing it. This failed while constructing the first timing worker, before starting a subprocess, creating an unseal marker, opening the blinded seed, reading a hidden case, or measuring a candidate.

This is **not** a consumed final attempt, a final-benchmark result, an irreversible retry, or permission to weaken the original protocol. The final benchmark remains **NOT ACCESSED** and **NOT MEASURED**.

## Exact original attempted command

The actual first attempt used the pinned CPython, all four frozen implementations, their exact independently qualified correctness proofs, the unchanged candidate freeze, and the original explicit unseal authorization:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  -m tools.rust_v9_holdout_protocol final \
  --manifest performance/v9/holdout-manifest.json \
  --module re \
  --module candidates.vm_candidate \
  --module candidates.rust_candidate \
  --module candidates.zig_candidate \
  --edge-oracle candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-21-singleton-split-memchr.json.gz \
  --edge-oracle candidates/evidence/rust-v7-edge-oracle-rust-owned-capture-init-hoist.json.gz \
  --edge-oracle candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-13.json.gz \
  --campaign-proof candidates/evidence/rust-v8-vm-stage-21-singleton-split-memchr-sealed-campaign.json \
  --campaign-proof candidates/evidence/rust-v8-rust-owned-capture-init-hoist-sealed-campaign.json \
  --campaign-proof candidates/evidence/rust-v8-zig-stage-13-sealed-campaign.json \
  --deep-proof candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-21-SINGLETON-SPLIT-MEMCHR.json.gz \
  --deep-proof candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-OWNED-CAPTURE-INIT-HOIST.json.gz \
  --deep-proof candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-13.json.gz \
  --from-scratch-audit candidates/audits/FROM-SCRATCH-AUDIT.json \
  --candidate-freeze performance/v9/evidence/V9-FINAL-CANDIDATE-SELECTION-FREEZE.json \
  --authorize-final-unseal UNSEAL-FROZEN-V9-HOLDOUT-AFTER-CANDIDATE-SELECTION \
  --raw performance/v9/evidence/V9-FINAL-HOLDOUT-24576-RAW.jsonl.gz \
  --memory performance/v9/evidence/V9-FINAL-HOLDOUT-24576-MEMORY.jsonl.gz \
  --output performance/v9/evidence/V9-FINAL-HOLDOUT-24576-SUMMARY.json \
  --unseal-marker performance/v9/evidence/V9-FINAL-HOLDOUT-24576-UNSEAL-MARKER.json
```

Its exit status was **1**, with the following recorded traceback:

```text
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/home/dev-user/src/rebar/tools/rust_v9_holdout_protocol.py", line 3183, in <module>
    raise SystemExit(main())
  File "/home/dev-user/src/rebar/tools/rust_v9_holdout_protocol.py", line 3152, in main
    print(json.dumps(final_measurement(args, document), allow_nan=False, sort_keys=True))
  File "/home/dev-user/src/rebar/tools/rust_v9_holdout_protocol.py", line 2053, in final_measurement
    worker = IsolatedWorker(module, "timing", CASE_TIMEOUT_SECONDS)
  File "/home/dev-user/src/rebar/tools/rust_v9_holdout_protocol.py", line 1818, in __init__
    started = time.perf_counter_ns()
              ^^^^
NameError: name 'time' is not defined. Did you forget to import 'time'?
```

## Why the final benchmark remains sealed

The frozen protocol constructs and validates all timing workers **before** calling the marker's `open` method or opening the blinded seed. The recorded exception happened at `time.perf_counter_ns()` inside the first worker's constructor, **before** `subprocess.Popen`. Therefore no candidate timing subprocess started, no unseal marker was created, no opening occurred, no hidden case was generated or read, and no final measurement began.

The separately recorded working-tree observation contained **no** final raw observations, final memory observations, final summary, or final unseal marker. This incident report does not inspect, stat, open, or create any of those destinations. The failed command cannot be counted as an irreversible final retry.

## Preserve the exact frozen protocol

The original protocol remains byte-for-byte unchanged. Its SHA-256 is `a699ce1e661ead447af0643584d69f080e72712059ad611fbd6b998f2ca19219`. The original frozen final manifest has SHA-256 `d747bfbca78e94b7dada3fdc24acd027fc8cd2e31a46a9441c328fb72153460f`; the exact candidate-selection freeze has SHA-256 `52066760bb4210a57f7b10f13e9ff73e36c53982a5b97aff40ead330c79edf41`. The complete passing four-family, five-native-library audit has SHA-256 `a790fe1a75c8748df7f8bb6f1e39d0be841636055358aaee94db0aa35523f326`. The immutable objective has SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`.

The stopping commit is `89e550923ede9cbd558c02f91b235aa17ffaff97`. The previously pushed candidate-freeze commit is `6986e536b8062a604672f1bb10bdf967f095b363`. This report does not change either commit, the protocol, any candidate, the frozen manifest, the blinded seed, an authorization condition, a correctness test, or the final measurement rules.

The narrowly bounded correction is an **additive, standard-library-only bootstrap**: independently verify the unchanged original protocol's exact SHA-256, import the genuine Python standard-library `time` module, and run the **same unmodified protocol source** through the genuine standard-library `runpy` mechanism with only `time` added to its initial globals. Keep the exact original arguments, pinned interpreter, frozen candidates, manifest, freeze, proofs, safeguards, authorization, and final measurement protocol. The bootstrap neither edits nor replaces the protocol and does not by itself access the final benchmark.

No corrected final command has been executed or claimed by this incident report.

Final **24,576-case** benchmark: **NOT ACCESSED**. Final performance: **NOT MEASURED**. Final winner: **NOT SELECTED**.
