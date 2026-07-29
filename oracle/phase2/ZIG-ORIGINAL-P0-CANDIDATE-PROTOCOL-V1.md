# First-party Zig candidate: original Python `re` test-runner freeze V1

## What this does and does not establish

This freezes a separate test controller and suite worker for the project's own
Zig regular-expression implementation. It binds both to the original, unchanged
Python 3.14.6 correctness tests. It does not execute the candidate, build or
activate a native library, qualify an implementation, inspect the sealed
performance holdout, measure speed, or establish absence of undefined behavior.

Current result: **source frozen; Zig candidate not run**. The dedicated Zig
runner has zero currently authorized runnable candidates. A previously
successful Zig build is historical evidence, not proof that its resulting code
is currently installed, verified, or passing. Missing independent verification
of the active native Zig implementation stops execution.

## Immutable input and original test cases

The goal remains SHA-256
`e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`.
The Python reference remains the isolated, pinned CPython 3.14.6 executable,
SHA-256
`255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016`.

The sole authorized original-test producer is the corrected six-family V4
source, protocol, and complete contract, respectively:

```text
e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8
e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5
c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5
```

All 13 suites remain included, in their original order:

| Original suite | Cases |
| --- | ---: |
| Original upstream methods | 151 |
| Public operations | 864 |
| Scanners and callbacks | 1,024 |
| Buffer inputs | 768 |
| Managed buffer lifetimes | 1,024 |
| Verbose scanner syntax | 2,854 |
| Public pattern and match types | 6,912 |
| Substitution | 5,120 |
| Changing buffer shapes | 10,240 |
| Public API surface | 1,376 |
| Independent Python interpreters | 128 |
| Python buffer exporters | 264 |
| Shared patterns across threads | 512 |
| Total | 31,237 |

The original 13 explicitly named private waivers are preserved. No case is
added, omitted, guessed, replaced, or silently waived.

## Actual candidate-facing Python reference

Two previously observed, distinct Python reference workers, process IDs `81`
and `82`, each produced the complete 6,912-case public-type vector. Their total
is 13,824 actual case observations. The correct complete vector is
`6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2`.
The 96-case cache/type separation vector is
`587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad`.
The actual small publication receipt is
`ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966`.

The previously disproved script-context vector
`0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21`
is historical evidence only. Source verification authenticates the small
receipt and complete frozen contracts; it never opens either compressed
reference evidence or candidate-matching evidence and starts no new reference
process.

## Implemented from scratch; no wrapped regex package

The candidate owns its Zig parser, syntax tree, bytecode compiler, executor, and
C-compatible interface in `candidates/zig/mini_regex.zig`, SHA-256
`a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28`.
Its owned Python C bridge is `candidates/zig/py_bridge.c`, SHA-256
`67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b`.
Its owned Python adapter is `candidates/zig_candidate.py`, SHA-256
`2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862`.

The bridge's CPython-compatible `_sre.SRE_Scanner` display name is metadata,
not an import or use of CPython's regex engine. The adapter may load only its
own Zig engine through its own bridge. Python `re`, `_sre`, external regex
packages, other candidate engines, matching fallbacks, and hardcoded answers
are forbidden. A source audit is not a runtime non-delegation audit; runtime
non-delegation remains **NOT ESTABLISHED**.

## Precisely preserved history

The coordinator committed and pushed current overview V45 at commit
`6dad94c5`. The exact current V45 renderer, inputs, summary, and chart
SHA-256 values are respectively:

```text
07a7e1b6c96434e66e852e0eb784326816d340edb338d2e89de4f1d6918bb586
cbc1b861fe59067e64adf396493630360f6bf616fe1f51598220aabafadea4a5
1086a7bd72116b590d00f5216835534ec745265a0f249d3cd5eb05a3701ff840
1c9d56fd4b8480bab9cedc2e95b6449a414cb68a02ee447963454db5b4242b2b
```

The actual evidence lower bounds are 166 owners and 171 independently
authenticated references. The earlier Rust V6 attempt genuinely failed
before starting any candidate or reference worker. Its controller read and
inflated one historical 108,985-byte build archive. The actual failure and
independent observation are respectively:

```text
88367fd41665bbeafb0645e3b03130ca97c1c54729863372d422e693169420d7
51846c742aafbfc2c42ddad75836310bba518b3a76d0f8fa1548a55128852ad6
```

That one past archive effect is historical evidence: this Zig source freeze
does not open or inflate any archive. The separately corrected, publication-
safe Rust V7 source, protocol, and contract are respectively:

```text
eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104
0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840
9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5
```

Rust V7 is a source freeze, not an executed or qualified Rust candidate. The
official stable Zig 0.16.0 compiler is independently locked and authenticated
at `/tmp/zig-x86_64-linux-0.16.0/zig`, 172,641,672 bytes, SHA-256
`2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c`.
Source checks stream its exact bytes but never execute it. The historical V12
build publication genuinely records 26 compiler processes and two applied
build-time changes, with no candidate workers and no native libraries loaded.
It is not a live activation.

The separately frozen real-world public import oracle has 32 checks. Its matrix
SHA-256 is
`f67f8d4d62f9939c94250ad2e4df55b14df013df7212aa66930ecc3a772d2a58`:
17 pass, seven fail, six are **NOT MEASURED**, one is **NOT ESTABLISHED**, and
the performance holdout remains **NOT OPENED**. The checked public entrypoint
selects the historically failing Zig prototype. Its public status is **FAIL**;
it is not an installed, compatible, qualified, or winning replacement. These
32 public checks and the separate 50 signature checks never silently change the
original 31,237-case denominator. The actual public oracle source, protocol,
and contract are:

```text
c0a61c4cf520e82bf0c327a17c06daf64f57a1dcfd20b37c6e9f7b84177108b4
01ace52c6285142733bdcb2b4556feb43226e01c8b181b84019b8fa8c42697c0
b80ba35a6af481f0dd1c5b9141e2995f7b0ffd12f8ffa7060bab50344ddbda47
```

The previously run Zig campaign used the now-stale V3 producer and genuinely
failed: 1,764 semantic mismatches, 3,711 verified passing cases, and zero
infrastructure failures. Its publication `PASS` means durable publication
only, not passing candidate matching. The source-only 64-case scanner repair is
not applied: 960 of 1,024 scanner cases are outside that construction change,
and the 620 previously observed verbose-scanner losses remain unrepaired. No
per-suite historical mismatch breakdown is invented from a small receipt.

## Future complete execution and publication rules

Actual matching first requires a separately frozen and independently verified
live activation of the exact first-party Zig engine and bridge. The worker and
controller must reject execution until that evidence exists. Only a later,
separately authorized execution may start one real, distinct worker per
original suite. Each must retain its actual process ID, complete case records,
all mismatches, timeouts, exit status, and full, retained-head, and retained-tail
SHA-256 hashes of standard output and error. A missing worker, case, stream,
or failed durable publication is a failure, not a passing or unmeasured case.

Candidate correctness, speed, memory, confidence intervals, regressions,
undefined behavior, and runtime non-delegation remain **NOT MEASURED** or
**NOT ESTABLISHED**. The final holdout remains **NOT OPENED**. No winner is
selected.

## Reproduce the source-only controls

Use the pinned interpreter with isolated mode and bytecode writes disabled:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/run_frozen_zig_original_p0_candidate_worker_v1.py --self-test
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/run_frozen_zig_original_p0_candidate_v1.py --self-test
```

Frozen-context verification additionally requires the explicit complete
SHA-256 and byte count for each of the worker, controller, protocol, and
canonical contract, together with all three exact V4 producer hashes. No
source-only mode accepts a candidate selection, build, native activation,
benchmark, compressed archive, or hidden holdout.
