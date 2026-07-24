# Prove that cached Python regex internals cannot power an engine

Status: **PROSPECTIVE. VERSION-TEN OWNERSHIP AUDITS NOT RUN.** Real
candidate matching, refreshed correctness, holdout speed, memory comparison,
and a winner are **NOT MEASURED**.

## Preserve the real Python baseline and both real failures

The authenticated, independently run two-reference CPython 3.14.6 baseline is
`oracle/cpython-3.14.6/evidence/postfinal-locale-v5-self-oracle.json`, SHA-256
`3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916`.
Both reference roles retain all 152 unchanged original public methods, 151
applicable passes, the one genuine named private-debug skip, the complete
26-file original upstream support tree, 403 original corpus cases, 11 external
fixtures, real two-gibibyte methods, the 40-GiB resource limit, the original
CPU and multiprocessing assertions, and real private locales.

The real first version-eight cached-foreign-sentinel owner failure is
`candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v8-diagnostic-native-owner-failure.json.gz`,
SHA-256 `2f8bfcba726d729865cb8411a25ef1c3e0633e80c70af8895e5875a71f15ed7b`.
The real first version-nine owner failure is
`candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v9-diagnostic-native-owner-failure.json.gz`,
SHA-256 `04e52f831534458e9af50ad3ab962d78ad43e6a8725cbfccfee37bf9c234f07c`.
The latter genuinely exited 1, produced zero stdout and 203 stderr bytes, and
reported `a V8 public owner can reach a Python matcher: re._compiler` before
any original edge case or candidate matching began. Both are **FAIL**. Keep
both complete genuine immutable compressed reports and stream fingerprints.

Also preserve all three full 223,198-check, 49-category historical Rust, C and
Zig edge failures, including their exact original 16, 33, and 16 real failed
rows. No historical failure qualifies a current engine.

## Fix the actual cached-internal-module escape

Freeze the unchanged original guard:

```text
tools/python_re_universal_public_oracle_stage07.py
150abcfc597658f48d64c04053889bd4b299c75ad7413bc1cafa5f864e9e7c25
```

Immediately after its authentic `_install_family_guard`, capture the one real
Stage 07 poison and its exact original class. Enumerate **every actually
cached** `sys.modules` module whose name begins with `re.`, including
`re._compiler` and `re._parser`. Retain the exact original module objects and
every already cached module-dictionary reference to them. Call the real,
unchanged upstream guard helper:

```text
stage07._poison_cached_module_aliases(
    sys.modules, tuple(actual_cached_regex_internal_modules), exact_stage07_poison
)
```

Then bind each enumerated internal module entry to that **same exact poison**.
Do not create a new sentinel, use an instance lookalike, remove the matcher
checks, import a replacement engine, or alter the Stage 07 guard. Require all
cached aliases and all `re.*` entries to hold the exact original blocker
before matching and again after matching. Prove that the original sentinel
class is unchanged, that `type(poison) is` that exact class, that cached
imports return that exact object, that original live descendant objects and
aliases cannot return, and that all genuine external and cross-family imports
remain blocked.

Preserve and execute all original 13 Python matching guards and all five
native-loader guards before and after genuine independently owned matching.
Every Rust, C, and Zig worker must preserve all 12 current owned source
files, five independently owned mapped native ELF roles, exact native
ownership and Python public `Pattern`/`Match`, actual string and bytes
matching, and all 16 ordinary Python generic-alias/pickle cases per family.
Do not weaken or omit any real guard.

## Freeze first and keep actual failures separate

Commit and push these additive files before executing a version-ten engine:

```text
tools/postfinal_from_scratch_audit_v10.py
tools/postfinal_no_delegation_audit_v10.py
candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V10.md
```

The four only permitted exclusive output files are:

```text
candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V10.json
candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V10-FAILURES.json
candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V10.json
candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V10-FAILURES.json
```

Reject an existing passing or failure path before starting a worker. Write
actual complete results only once with `O_EXCL`, `O_NOFOLLOW`, bounded
canonical bytes, durable file and directory writes, and unchanged real
partial records, stderr, stdout, signal and timeout details. A failure never
creates a passing report.

The independent strict audit must receive the actual passing version-ten base
report SHA-256 as mandatory external `--base-report-sha256`. Authenticate its
complete canonical real bytes and exact frozen owner source, protocol,
all-three genuine corrected owner workers and all 12 source/five native ELF
hashes **before** reading historical, reference, or other evidence or starting
any worker. Never insert an unknown report hash into a frozen source.

## Direct candidate-free controls

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/postfinal_from_scratch_audit_v10.py --self-test
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/postfinal_no_delegation_audit_v10.py --self-test
```

Both direct commands must also pass under
`env -i PATH=/usr/bin:/bin`. Each must run at least 150 genuinely
source-only poison controls, with zero candidate imports, process starts,
file reads, file writes, clocks, timing, or holdout access. Source-only checks
are never candidate compatibility or benchmark measurements.
