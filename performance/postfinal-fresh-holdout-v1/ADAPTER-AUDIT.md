# Four-channel final-test adapter: public verification only

Status: **PASS on public cases. The 65,536-case final test is NOT OPENED.**

The proposed final test requires four independently checked kinds of Python
behavior: compiled-pattern metadata; actual results and captures; exception
details; and callback, converter, warning, and scanner behavior. The new
adapter reconstructs each kind separately in four permanently isolated
workers: unmodified Python, independently written Rust, independently
written C, and independently written Zig. It never substitutes another
candidate or an external regular-expression package.

## What actually passed

The [independent source and native audit](../../candidates/audits/POSTFINAL-FRESH-HOLDOUT-ADAPTER-AUDIT-V2.json)
verifies:

- All **63** direct anti-delegation and source-isolation controls.
- The existing **76-control** from-scratch audit and **32-control** isolated
  native-engine audit.
- All **16** explicitly owned production source files.
- All **five** actual Rust, C, and Zig native libraries.
- All **four** independently named Python-observation channels.
- Exact reconstruction of the original guarded worker at **three** unique
  insertion points, preserving its original protections byte for byte.
- No candidate import, worker startup, production secret, final test, or
  timing while auditing.

The [actual four-worker public verification](../../candidates/audits/POSTFINAL-FRESH-HOLDOUT-ADAPTER-SMOKE-V2.json)
uses only the publicly specified nonproduction key `bytes(range(32))`.
It completes:

- **2,176** publicly generated cases.
- All **16** pattern families and all **16** input categories.
- All **nine** supported search, iteration, splitting, replacement, and
  scanner operations.
- Python text, bytes, mutable bytes, and memory views.
- **8,704** snapshots from the four actual isolated workers.
- **26,112** independently compared candidate behavior channels.
- **17,416** before-and-after native-library and worker checks.
- **Zero** mismatches, production cases, final-test access, or timings.

The separate native statistics helper is implemented from scratch in C. Its
**38** passing synthetic controls verify the **19-trial**, **2,000-draw**
paired confidence protocol. It is not a regex engine and does not import or
run an external regex package. The adapter holds only **608 bytes** of
per-case timing values; neither final runtime nor final memory is inferred.

## Exact source and evidence

| Public input or proof | SHA-256 |
| --- | --- |
| Four-channel adapter | `cc29f089344e2ccfb85765689d36938f01ee2e26289c525bafd7aec629cbdba0` |
| Independent adapter auditor | `eb1db6b4985cf10364997477f9ca318a409e7d04e38ba7a947763b419aef138b` |
| Fixed-public-case verifier | `6a66917a5a7ef647c3794d76340d014bf8f8d5f12c26c0fa1197058ebb8771c9` |
| From-scratch native statistics source | `d9950b54c140e4739e3edae09c07a68e588a4bbc5f3680ceb7576941d75fe0a8` |
| Passing independent adapter audit | `4c5e9e495409625da00387fe0e9011821fbddf783da501ba0d143fd2ea31cd3d` |
| Passing four-worker public verification | `456ce602e7b59173513737970d5a624a2d2964f60835af3d142676f3eb0d8f62` |

The original [version-one audit](../../candidates/audits/POSTFINAL-FRESH-HOLDOUT-ADAPTER-AUDIT-V1.json)
and [version-one public run](../../candidates/audits/POSTFINAL-FRESH-HOLDOUT-ADAPTER-SMOKE-V1.json)
are preserved unchanged. A single trailing space in the original native
statistics source failed the repository's formatting gate. Correcting it
changed the source fingerprint, so both checks were run again and written to
new version-two evidence files. The version-two audit independently checks
the fingerprints of both preserved original reports; neither result was
overwritten or silently rebound to the corrected source.

## Reproduce public-only controls

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_fresh_holdout_adapter_v1.py --self-test

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_fresh_holdout_adapter_smoke_v1.py --self-test

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -I -B -c \
  'import resource,runpy,sys; n=192*1024*1024; resource.setrlimit(resource.RLIMIT_AS,(n,n)); sys.argv=["tools/postfinal_fresh_holdout_adapter_audit_v1.py","--validate"]; runpy.run_path(sys.argv[0],run_name="__main__")'

cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic \
  tools/postfinal_fresh_holdout_bootstrap_v1.c -lm \
  -o /tmp/rebar-postfinal-fresh-holdout-bootstrap-v1-root-self-test
/tmp/rebar-postfinal-fresh-holdout-bootstrap-v1-root-self-test --self-test

jq '{status, cases, failed, worker_snapshots,
     independent_channel_comparisons, runtime_guard_checks,
     guard_accessed, production_cases_materialized,
     benchmark_or_timing_executed}' \
  candidates/audits/POSTFINAL-FRESH-HOLDOUT-ADAPTER-SMOKE-V2.json
```

The fixed-public verification is not the final test. The adapter and helper
have **not** been integrated into the prospective final controller or sealed
in a one-use final manifest. No final key, case, timing, confidence
interval, speed result, memory result, or winner exists.
