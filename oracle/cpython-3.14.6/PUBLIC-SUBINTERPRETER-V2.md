# Real Python subinterpreter compatibility

Status: **FROZEN. TWO-REFERENCE ORACLE NOT RUN.** Candidate compatibility is
**NOT RUN**. Performance and memory are **NOT MEASURED**. The holdout is
**NOT ACCESSED**. Passing source-only controls never start an interpreter,
run Python's regular-expression engine, launch a worker, or qualify a candidate.

This category is additive. Keep every original **165** CPython methods:
**152** public methods, consisting of **151** runnable methods and the one
genuine uniformly applied debug-only skip, and exactly **13** explicitly named
private methods in `DebugTests` and `ImplementationTest`. Neither private
waiver exempts a public method. Keep all **1,376** independently frozen public
cases and all **43** cohorts. Preserve the immutable prospective predecessor:

```text
V1 subinterpreter protocol
oracle/cpython-3.14.6/PUBLIC-SUBINTERPRETER-V1.md
38bf2b1a5b93196370bb532d98124a3de7092a56b1233a6b1731411a3a595263

V1 subinterpreter controller
tools/python_re_subinterpreter_oracle_v1.py
88a3600908f7090fb384fe03559e231f820d6c6c141846b738c73e89c7a69563

Preserved V1 report
oracle/cpython-3.14.6/evidence/public-subinterpreter-v1-self-oracle.json
9a5501ac4a60f48f749c3d42216c08391b5ff03ed38f191e37588ed4fa747bfa

Preserved V1 publication receipt
oracle/cpython-3.14.6/evidence/public-subinterpreter-v1-self-oracle-publication-receipt.json
d4a3b94bc30747db44560eb052d809ee574f5b4083ff7649b05f18f91501418c

Original independent CPython double reference
oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle.json
1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf

Frozen full public validator
tools/python_re_public_surface_oracle_stage27.py
fd0ef1babdb5943d74ef443486805ef6586e46b06eb9d46e4f5b7b650045032b

Frozen full public protocol
oracle/cpython-3.14.6/PUBLIC-SURFACE-V27.md
c8cc917b52affbce8d61ae1ad217835c7c890fe1e1369d211475a7aaf443cd3f

Complete public two-reference report
oracle/cpython-3.14.6/evidence/public-surface-v19-self-oracle.json
a2ac2853a6551b9eb95564ee74731c9e7d44998f5ec32ad5aac2259b5b313ad8

Complete public reference record vector
c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef

Original public matrix
7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa

Original public stimuli
8c1a4fd434af5fb1ea0dcd1aa3faaa06b07e7d186ca52c1593575eff93b4d7da

Pinned stable CPython executable
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

Pinned re/__init__.py
741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35

Pinned concurrent/interpreters/__init__.py
040e47f07bdfb28c67798fa7764fac1d79e13fd0fc0db9c85ee5dae8e1edf249
```

Freeze the exact original **128** cases, **16** equally weighted categories,
and **8** variants per category. Preserve the complete base seed
**2026072501** and the unchanged matrix SHA-256
`edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3`.

1. Fresh interpreter creation and standard-library import.
2. Text compilation, matching, and full matching.
3. Bytes compilation, matching, and full matching.
4. Compiled-pattern and match-object ownership and identity.
5. Interpreter-local cache hits and public `purge()`.
6. Simultaneous cross-interpreter cache and state isolation.
7. ASCII, Unicode, inline, non-ASCII ignore-case, and multiline flags.
8. Bytes `LOCALE` without mutating process-global locale.
9. Named captures, backreferences, templates, and callbacks.
10. Empty matches, `finditer`, scanner progress, and exhaustion.
11. Malformed patterns, type errors, and subsequent recovery.
12. Interpreter-local modules and built-in state.
13. Repeated real creation, execution, and destruction.
14. Independently owned standard-library module reimport.
15. Contiguous bytes-like inputs and exporter lifetimes.
16. Interpreter teardown and independently verified worker cleanup.

Only use the genuine pinned CPython `concurrent.interpreters` public API:
`concurrent.interpreters.create()`, `Interpreter.exec()`, and
`Interpreter.close()`. Every isolated reference process keeps two distinct
non-main interpreters **A** and **B** alive at once. For each complete original
case, independently perform and retain **A → B → A**. Compare all complete
observations and verify both interpreters remain live. Create, execute, and
close eight additional independently identified interpreters while **A** and
**B** remain live. Actually close **B**, execute **A** again, close **A**,
create a distinct fresh **C**, execute **C**, and verify its public close.

Each genuine worker creates and destroys exactly **11** real interpreters and
performs exactly **394** real regular-expression matching executions. Two
distinct pinned-CPython `subprocess.Popen` workers must yield identical
complete original vectors and genuinely different, externally bound PIDs.
Their exact combined denominators are **22** creations, **22** verified closes,
**788** real matching executions, **256** complete case triples, and **768**
individual **A → B → A** phase records. Interpreter initialization is not a
regex execution. Preserve every role, original interpreter ID, process status,
signal, complete bounded stdout and stderr, callback, buffer, warning,
post-close record, teardown, error, and failing cleanup. No placeholder,
capability check, main-interpreter result, candidate, wrapper, reused worker,
or `NOT RUN` counts as an actual observation.

Authenticate the frozen original baseline by executing only the previously
frozen V6 `_original_reference_prerequisites()` and `_read_reference()`
chain. Authenticate all **1,376** public records exclusively through V27
`authenticate_reference()` and its pinned producer-owned duplicate-key-strict
JSON decoder. Preserve all **64** real locale cases and **192** transitions.
Never use `jq` or a guessed decoder on genuine lone-surrogate evidence.

Root alone may run `--self-oracle` after this exact protocol and controller
are independently reviewed, committed, and pushed. Explicitly supply the
independently frozen actual controller and protocol SHA-256 values. Do not
run the two-reference oracle, subinterpreters, candidates, or ownership
workers during source freeze.

The successful full report and the complete retained failure report use
**deterministic gzip**, level **9**, timestamp **0**, bounded compressed and
uncompressed sizes, exact original canonical bytes, and SHA-256-authenticated
readback. Each separately published canonical receipt records the precise
compressed and original lengths and hashes. Walk every parent component using
descriptor-relative `O_DIRECTORY | O_NOFOLLOW`; create only the four named
V2 report and receipt paths using `O_EXCL | O_NOFOLLOW`. Before each real
syscall append a pending, role-tagged event, and resolve every event to a
success or failure. Retain short writes, original bytes, descriptor identity,
file and parent `fsync`, process output, and every cleanup. Never overwrite
or unlink an existing basename. Remove a partial output only after proving it
was created by this attempt, that its descriptor and no-follow basename still
share the original device and inode, and that a subsequent parent-directory
`fsync` actually completes. Never publish a receipt for an incomplete report.

`--self-test` is source-only. It authenticates just this final protocol and
its own final controller, preserves the original matrix and accounting, and
runs deterministic named positive and hostile synthetic controls. It rejects
invented worker PIDs, missing A/B/A phases, hidden records, fake interpreter
IDs, alternate source/protocol hashes, false public waivers, source-only
matcher and interpreter calls, unsafe paths, duplicate and non-finite JSON,
truncated or concatenated gzip, forged hashes, nonzero side-effect counts,
incomplete descriptors, unsafe cleanup, and every partial publication.
Execute it both in the normal isolated environment and `env -i`. It never
starts a real interpreter, worker, candidate, thread, clock, matcher, locale
change, evidence reader, benchmark, or holdout.
