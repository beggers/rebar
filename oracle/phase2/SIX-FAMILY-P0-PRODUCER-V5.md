# Run the real Python regex tests without using Python's regex engine

Status: **SOURCE FROZEN ONLY. NO REPLACEMENT HAS RUN OR PASSED.**

The original Python 3.14.6 correctness reference contains **31,237** checks
in **13** groups. A separate **8,244**-case collection is independently
verified and is never added to that total. The original upstream test file
contains **165** methods: **152** public records and exactly **13** named
private exclusions. One public record is the original debug-build skip;
**151** public methods actually run. No additional method may be skipped.

The older version-four producer is preserved, with its complete six families,
25 independently authored source files, original results, and original case
order. Its original-test observer cannot prove candidate independence: it
loads Python's own `re` and `_sre` inside the candidate worker. Its
subinterpreter bootstrap also restores the original matcher. Neither old
observer is a valid candidate test under the fail-closed runtime guard.

Version five starts pinned Python with `-I -B -S` and initially imports only
modules that cannot silently import a regular-expression engine. A separately
authenticated runtime guard must be physically installed **before** importing
exactly one independently authored candidate. The selected candidate must be
the exact object exposed by `sys.modules['re']`; `re._constants` may contain
only the original data-only `MAXGROUPS` constant. Python's matching engine,
other candidates, external regex packages, fallback, and approximate answers
are forbidden. The legacy evaluator is authenticated as historical evidence
and can be loaded only after the selected alias is bound.

The original observer reads the digest-authenticated upstream `test_re.py`,
rebuilds and verifies all 165 unchanged source-ordered methods, executes all
152 original public records against the selected candidate, verifies the
candidate identity before and after every method, and compares the entire
result vector to the independently frozen Python reference. Every actual
failure is preserved. The original fork-based test is allowed only for its
exact upstream method using guarded `begin_fork_case` and `end_fork_case`
operations. Real ISO-8859-1 and UTF-8 locale fixtures must be
prepared by a separate, reference-only process before a candidate starts.
The candidate verifies and restores those actual private fixtures without
starting `localedef`, a subprocess, a reference matcher, or another engine.

All **13** original suite identities, all **31,237** case executions, all six
first-party families, all **25** semantic source files, and both independently
observed candidate-context public-type references remain unchanged. The
128-case subinterpreter group uses the authenticated version-two guard's
actual child bootstrap. It brackets real interpreter creation with
`begin_subinterpreters` and `end_subinterpreters`, installs the guard before
the selected engine is imported in each child, runs the unchanged
source-owned program through genuine operating-system pipes, and requires all
**394** original case executions in exactly **11** genuinely created and
destroyed interpreters. Each child receives a fresh 256-bit challenge and a
distinct real pipe. The guard independently verifies the actual live
interpreter, authenticates its exact bootstrap, reads the child's positive
response from the guard-owned pipe, and closes both descriptors. Neither a
made-up interpreter identity nor a caller-supplied response can install a
child guard. The immutable original cleanup removes the selected aliases and
never restores Python's original matcher.
Missing guards, omitted cases, open pipes, incomplete cleanup, and actual
candidate mismatches fail closed. This executable candidate path is frozen,
but **has not run**.

Fingerprint all three version-five owners before running the ordinary and
sterile source-only gates:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/run_owned_six_family_original_p0_producer_v5.py --self-test

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/run_owned_six_family_original_p0_producer_v5.py --self-test

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/run_owned_six_family_original_p0_producer_v5.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/run_owned_six_family_original_p0_producer_v5.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

These gates start no candidate, reference, compiler, child interpreter,
thread, timer, or benchmark. They do not open compressed archives, native
libraries, private build roots, or hidden final cases.

Candidate matching: **NOT RUN**. Compatibility: **NOT ESTABLISHED**.
Runtime independence: **NOT ESTABLISHED**. Speed, memory, uncertainty,
and undefined behavior: **NOT MEASURED**. Holdout: **NOT OPENED**.
Winner: **NONE**.
