# Real Python subinterpreter compatibility

Status: **PROSPECTIVE. NO REFERENCE, CANDIDATE, OR SUBINTERPRETER RUN.**
Performance and memory are **NOT MEASURED**. The holdout is **NOT ACCESSED**.
A passing source-only control does not start an interpreter or qualify a regex.

This is an additive correctness category. It does not replace, remove, rerun,
or reinterpret any of the original 165 CPython tests or the 1,376 separately
frozen public cases. CPython 3.14.6's original baseline is:

```text
oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle.json
1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf

tools/python_re_public_surface_oracle_stage27.py
fd0ef1babdb5943d74ef443486805ef6586e46b06eb9d46e4f5b7b650045032b

oracle/cpython-3.14.6/PUBLIC-SURFACE-V27.md
c8cc917b52affbce8d61ae1ad217835c7c890fe1e1369d211475a7aaf443cd3f

oracle/cpython-3.14.6/evidence/public-surface-v19-self-oracle.json
a2ac2853a6551b9eb95564ee74731c9e7d44998f5ec32ad5aac2259b5b313ad8

Complete authentic V19 public-reference record vector
c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef

Pinned CPython 3.14.6 executable
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

Pinned public standard-library re/__init__.py
741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35

Pinned public concurrent/interpreters/__init__.py
040e47f07bdfb28c67798fa7764fac1d79e13fd0fc0db9c85ee5dae8e1edf249
```

Keep all **165** original methods: **152** public methods and exactly **13**
named private methods in `DebugTests` and `ImplementationTest`. Neither class
waiver is a public-method waiver. Keep all **1,376** existing public cases,
all **43** cohorts, the existing matrix
`7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa`,
and the existing stimuli
`8c1a4fd434af5fb1ea0dcd1aa3faaa06b07e7d186ca52c1593575eff93b4d7da`.

## Additional frozen cases

Use exactly **128** real cases: **16** categories, **8** deterministic
variants each. The additive matrix SHA-256 is
`edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3`.

1. Fresh interpreter creation and standard-library import.
2. Text-pattern compilation, matching, and full matching.
3. Bytes-pattern compilation, matching, and full matching.
4. Compiled-pattern and match-object identity and ownership.
5. Same-interpreter cache hits and public `purge()`.
6. Simultaneous cross-interpreter cache and state isolation.
7. ASCII, Unicode, inline, non-ASCII ignore-case, and multiline flags.
8. Bytes `LOCALE` behavior without changing the process-global locale.
9. Named captures, backreferences, substitutions, and callbacks.
10. Empty matches, `finditer`, scanner progress, and exhaustion.
11. Malformed patterns, type errors, and subsequent recovery.
12. Interpreter-local modules and built-in state.
13. Repeated interpreter creation, execution, and destruction.
14. Independent standard-library module reimport.
15. Contiguous bytes-like inputs and exported-buffer lifetimes.
16. Interpreter teardown and independently observed worker cleanup.

Use the actual pinned public CPython API: import
`concurrent.interpreters`, call `concurrent.interpreters.create()`, and use
each genuine `Interpreter.exec()` and `Interpreter.close()`. A placeholder,
an unauthenticated guessed API, a reported capability, a main-interpreter
regex result, or `NOT RUN` never counts as an executed subinterpreter case.

Each actual isolated reference worker keeps two distinct interpreters **A**
and **B** alive together. For every original additive case it executes
**A → B → A** and compares all three complete semantic observations. It then
closes **B**, actually executes **A** again, closes **A**, creates a fresh
**C**, executes **C**, and closes **C**. Repeated fresh creation and real
public close calls are separately counted. Record original process status,
signal, complete bounded stdout and stderr, interpreter creation, execution,
identity, isolation, recovery, and verified teardown. The two reference
workers must have genuinely different PIDs and identical complete semantic
vectors; PIDs and actual interpreter IDs are provenance, not matching answers.
Independently bind each actual worker's reported PID to the observed
`subprocess.Popen.pid`. Preserve every original A, B, and repeated-A record,
the post-close-A record, the fresh-C record, and all distinct actual interpreter
IDs. Create, execute, and close eight additional fresh interpreters in each
reference worker while the original A/B pair remains live.

Count actual regex-matching executions separately from interpreter setup.
Each real worker must create and close exactly **11** interpreters and run
exactly **394** matching executions: **128 × 3** A/B/A observations,
**8** independently fresh observations, **1** post-B-close observation,
and **1** fresh-C observation. Across both actual reference workers, report
exactly **22** creations, **22** verified closes, **788** matching executions,
**256** complete A/B/A case triples, and **768** individual A/B/A phase
records. Never label 256 triples as 768 records or count setup-only calls as
matching. No count is an observed result before the real oracle runs.

Authenticate the original baseline by executing the frozen V6 validator's
actual `_original_reference_prerequisites()` and `_read_reference()` chain.
Authenticate the complete V19 two-reference public baseline by executing the
exact frozen V27 `authenticate_reference()` and retaining the genuine 1,376
records, both original process transcripts, and all 64 real locale cases and
192 transitions. Reading source constants or merely parsing report summaries
is never baseline authentication. Decode authentic Unicode, including escaped
surrogates, exclusively using pinned CPython's bounded JSON decoder.

Do not import a candidate, access an external regex engine, inspect a native
binary, launch an ownership worker, change a locale, access a benchmark,
sample a clock, or inspect the holdout. Candidate subinterpreter compatibility
remains **NOT RUN** until an independently frozen current graph, native owner,
and future guarded candidate protocol authorize a real run.

## Candidate-free source checks

`--self-test` reads only this protocol and its own controller. Its frozen
denominator is exactly **988 genuinely distinct named source-only controls**;
the controller requires both the exact count and unique control identities.
One of those controls additionally rejects **25 independently disclosed**
forged publication receipts in memory; those 25 are not renamed or added to
the 988-control denominator. Its complete in-memory cases reject a capability
placeholder, an invented interpreter, a
missing A/B/A execution, an undeleted interpreter, a changed source matrix,
changed original 165/152/13 accounting, a changed public 1,376-case matrix,
forged worker identity, guessed API, omitted bytes or Unicode cases, altered
flags, changed standard-library identity, incomplete streams, duplicate JSON
keys, non-finite numbers, unsafe paths, and any invented candidate result.
It starts zero interpreters, reference or candidate workers, threads, or
native owners; writes zero files; takes zero clock samples; and reads zero
evidence, native artifacts, benchmarks, or holdout cases.

Run these controls with both the normal isolated pinned interpreter and a
minimal empty environment, as both CLI and direct API calls. Only root may run
the prospective `--self-oracle` after this controller and protocol have been
independently reviewed, committed, and pushed. Supply both exact actual source
and protocol SHA-256 values externally. A real report or failure and its
separate publication receipt use exclusively created, no-follow canonical
files. Open every parent component independently with descriptor-relative
`O_DIRECTORY | O_NOFOLLOW`; record the actual parent and exclusively created
file device and inode. Append a `PENDING` ledger entry before every open,
stat, write, read, `fsync`, close, and owned-partial cleanup. Preserve
returned bytes, short writes, syscall errors, bounded exact readback, the
first primary failure, and every cleanup failure. Remove a partial basename
only if this attempt exclusively created it and no-follow parent-relative
`stat` still proves the exact original file device and inode; record that
unlink and a real subsequent parent-directory `fsync`. Never remove an
existing or replaced file. Existing complete evidence is never overwritten
or retried.
