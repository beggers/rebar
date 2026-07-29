# Original Python regular-expression compatibility, version 10

This is a new compatibility experiment for the independently written C
regular-expression engine. It retains every original Python 3.14.6 check and
installs a separately authenticated guard that verifies real Python child
interpreters. It does not wrap or fall back to Python's regular-expression
engine, an external regex package, or another candidate.

Freezing or checking this experiment does not run the C engine. Correctness,
speed, memory, and safety remain **NOT MEASURED** until a separately authorized
complete run. The holdout remains **NOT OPENED**.

## Preserve what actually happened

The previous real C run has small public receipt
`54b690fa487670dd0cb18cbc35e36f684666d7fb547c1aa30c48b244788effb6`.
It started 13 different workers and attempted all 31,237 original cases. Seven
groups completed: three passed 13,606 cases, and four proved at least 492 real
differences. Those differences were 16 managed-pattern cases, 248 public-type
cases, 224 substitution cases, and four Python buffer cases. Six other groups
failed to finish. The total mismatch count is **NOT MEASURED**.

One real failure said exactly:

> reject a forged function whose filename imitates frozen source:
> tools.python_re_public_surface_oracle_stage19.digest

The original digest function was legitimate. Compiling its complete,
SHA-256-authenticated original module, without executing that module, produces
different Python bytecode from compiling its function in isolation. Version 10
verifies the unique original top-level function against its complete original
module, including its real globals, filename, line, and complete code identity.
It never replaces the digest, runs the original module in a source check, or
accepts lookalike functions. The real previous failure is retained unchanged;
this correction does not establish candidate correctness.

The previous child-interpreter group genuinely failed. Its receipt does not
establish which child or which operation failed, so no extra details are
claimed. The original C extension was restored to its exact original inode.

## Every original Python check

| Original group | Original cases |
| --- | ---: |
| `original_bounded_v5` | 151 |
| `public_v3` | 864 |
| `scanner_v3` | 1,024 |
| `buffer_v3` | 768 |
| `managed_v1` | 1,024 |
| `scanner_verbose_v1` | 2,854 |
| `public_types_v1` | 6,912 |
| `substitution_v2` | 5,120 |
| `shape_v2` | 10,240 |
| `public_surface_v19` | 1,376 |
| `subinterpreter_v2` | 128 |
| `pep688_v4` | 264 |
| `threaded_pattern_v1` | 512 |
| Total | 31,237 |

The 8,244 separately prepared reference checks are never added to this total.
The 13 explicitly named private waivers are unchanged. All 13 candidate groups
must actually finish before an exact mismatch total or compatibility can be
claimed.

## Genuine child interpreters

The version-3 child-interpreter guard is independently frozen as source
`03f051e428ee31bb671d8ced82f02d7a9fe3520f24191aba78d2e8a0697202c2`,
protocol `d3437b642d322ccccf12851981555cb596ff7f9c5a12e0a6a389d6b80b5a068a`,
and contract `31e9a5d2754b5b4b273d4fc30d6a27967e495b57684fdd1e9306bbac3b2caaa7`.
It preserves the original version-2 guard and unchanged version-5 original
test producer. The guard is installed before the candidate is imported.

The original interpreter group requires 11 real child creations, 11
destructions, 394 original case executions, 11 first guard installations, and
11 cleanups: 416 actual interpreter executions. Creation must be authenticated
by the genuine `cpython.PyInterpreterState_New` event, the exact original
provider code and globals, an actual before-and-after live-interpreter change,
and a real operating-system challenge pipe. Synthetic events, generated
programs, and counter updates are not child-interpreter evidence.

Both C native roles must independently retain all 14 exact source-owned native
fields, including the corrected file, actual inode, byte count, user, and
unloaded state. The actual first-party corrected extension remains
`7a5f8db27154cdcbd4203d727e02c0828ba1f9bf3fa2fdc1a86223ee57825f60`.
The corrected C source remains
`fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2`.
No candidate file is created by source verification.

## Check the frozen experiment

Use only pinned CPython 3.14.6 with `-I -B -S`. Run both commands under the
normal environment and under `env -i PATH=/usr/bin:/bin LC_ALL=C`, replacing
the three placeholders with the independently computed owner hashes:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/run_owned_repaired_c_original_campaign_v10.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/run_owned_repaired_c_original_campaign_v10.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Every source check physically rejects candidate files, native libraries,
private roots, compressed evidence, benchmark files, timing, cryptographic
entropy, and the unopened holdout. Every actual-effect counter must remain
zero. Contract rendering prints canonical JSON and never creates a file.

A real campaign is permitted only after the three owners have been reviewed,
committed, and pushed. It must explicitly pin the complete historical and
actual C21 build evidence, both immutable guard versions, the original
producer, the exact version-9 failure receipt, the exact C native roles, and
the complete original 13-suite test. It must restore the exact original C
extension before publishing every actual result. Until that happens, version-10
candidate correctness, interpreter execution, performance, and safety are
**NOT MEASURED**, and no candidate or winner is qualified.
