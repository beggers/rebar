# Original CPython 2-GiB regular-expression tests, version 1

This source-only oracle records an important open compatibility question: can a
from-scratch replacement for Python's `re` handle the two original CPython tests
that use strings of exactly 2,147,483,648 characters? It answers that question
honestly: the pinned CPython reference already has recorded passing results;
**no candidate has run either full-size test**.

The baseline is the exact, pinned CPython 3.14.6 Linux x86-64 release
interpreter and its untouched `oracle/cpython-3.14.6/test_re.py`. The verifier
authenticates the original source and checks the actual syntax trees of both
original `ReTests` methods. It never imports or executes that test module.

- `test_large_search` must construct `'a' * _2G`, search for `$`, obtain a
  non-null match, and observe both its start and end at 2,147,483,648.
- `test_large_subn` must construct the same exact-size subject, run
  `re.subn('', '', subject)`, return the original subject unchanged, and report
  exactly 2,147,483,649 replacements.
- The exact upstream memory decorators are
  `bigmemtest(size=_2G, memuse=1)` and
  `bigmemtest(size=_2G, memuse=16 + 2)`. Replacing them with small inputs,
  approximations, different patterns, or synthetic matcher answers fails the
  source gate.

## What actually ran

The independently pinned upstream accounting records two distinct **historical
CPython reference** processes. Both really delivered both 2-GiB subjects, each
passed 151 public original methods, and neither had a failure. Their original
real memory allowance was 42,949,672,960 bytes (40 GiB). The single release
debug-build-only skip remains an honest `SKIP`; it is not a public waiver.

This oracle verifies that accounting from its exact manifest only. It does not
read the large reference report, run another reference, or allocate a 2-GiB
string. A recorded standard-library reference result is not a candidate result.

The existing independently pinned candidate-facing original controller uses
`original_bigmem_dry_run = true` and caps subjects at 5,147 characters.
Consequently:

- Candidate full-size search: `NOT RUN`.
- Candidate full-size substitution: `NOT RUN`.
- Candidate full-size compatibility: `NOT ESTABLISHED`.

The exact current published version-46 evidence also pins all four first-party
Zig version-1 worker, controller, protocol, and contract sources. Three
candidate-family sources (`c`, `rust`, and `zig`) are frozen. **Zero candidate
families are actually runnable or correctness-qualified.** Freezing Zig source
does not execute Zig, run either large input, or make the public prototype a
winner.

These observations add no cases to the frozen 31,237 original cases, 13 suites,
or 13 named private waivers. The 50 additional callable checks and 32
public-import observations remain separate. The actual failed public import
and failed historical Rust attempt remain visible; neither is quietly promoted
to a pass.

## Future full-size execution

Actually testing a candidate requires a separately frozen first-party worker,
its independently authenticated source, an isolated pinned-CPython subprocess,
a real explicit host-memory admission **strictly greater than 40 GiB**, a
bounded independent worker memory limit and timeout, and complete stdout,
stderr, exit, and result records for both exact original methods.

A reference subprocess alone may use the pinned standard-library engine. A
candidate subprocess must use its own proven first-party engine: no `re`,
`_sre`, external regex package, another candidate, or fallback. Unavailable
memory produces `NOT RUN; INSUFFICIENT RESOURCES`, never `PASS` or a waiver.

This source-only oracle deliberately implements no execution, subprocess,
memory-query, benchmark, or holdout mode. Its synthetic admission self-tests do
not start workers and are not candidate evidence.

## Reproduce the frozen source gates

Run both `--self-test` and `--verify-frozen-context` with the exact pinned
interpreter and all three independently measured owner hashes:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/verify_large_input_indexing_v1.py --self-test \
  --source-sha256 <actual-sha256-of-verifier> \
  --protocol-sha256 <actual-sha256-of-this-document> \
  --contract-sha256 <actual-sha256-of-frozen-json>

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/verify_large_input_indexing_v1.py --verify-frozen-context \
  --source-sha256 <actual-sha256-of-verifier> \
  --protocol-sha256 <actual-sha256-of-this-document> \
  --contract-sha256 <actual-sha256-of-frozen-json>
```

Repeat both commands with `env -i PATH=/usr/bin:/bin LC_ALL=C`. The ordinary
and sterile results must be byte-identical. A physical Python audit hook blocks
unapproved reads, imports, candidate and native activation, archives, clocks,
network, process creation, writes, and holdout access. The self-test attempts
real blocked effects and proves that each was rejected.

The separate 32-row source-observation matrix is authenticated by SHA-256
`a105aea287d093ff977819dda8971f592c3ed396eabd3133e5c52838ce8e2f65`.
It is not a new original,
signature, benchmark, or holdout denominator. Candidate speed, native memory,
and undefined behavior remain `NOT MEASURED`; no winner is selected.
