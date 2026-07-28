# Complete original-correctness campaign, version 1

This freeze prepares a fair, complete test of a genuinely first-party regular
expression engine. It does not run a test, compile an engine, activate native
code, measure performance, or open the final holdout. The baseline remains
the separately pinned stable CPython 3.14.6.

The exact original correctness test has 13 suites and 31,237 cases. Its
upstream test contains 152 original public records, one genuine debug-build
skip, and exactly 13 previously named private waivers. Every original suite,
source, case order, full-width seed, matrix, reference hash, record, and
evaluator is unchanged. Real Python buffer exporters, real shared-pattern
threads, the 64 locale cases and 192 real locale transitions remain in scope.
The original subinterpreter test still requires 128 cases, 394 case calls,
11 temporary interpreters, and eight genuinely fresh interpreters. The old
385-call Zig failure is not a pass.

All six independently written language families and all 25 disjoint
first-party semantic source owners remain frozen. The complete 65-owner
historical evidence graph and all 169 genuinely observed historical compiler
processes are retained. Five families have successful source builds; only
C, Rust, and Zig have existing original-suite runs. A build or activation
receipt never proves correctness.

This particular complete-campaign runner honestly supports only the two
additional families for which the frozen version-4 activator can prove an
actual passing two-phase source build: version-4 C++ and version-6 Go. C++ has
one combined native engine and Python bridge. Go has a separately owned engine
and bridge; its compiler-generated header is build evidence only and must
never be promoted. Unsupported Fortran, failed source builds, wrappers,
stdlib matching, borrowed engines, fabricated records, and guessed outcomes
are rejected.

Only an explicit `--run` may first verify the real published build and then
call the pinned first-party version-4 activation. It starts exactly one
isolated, shell-free, pinned Python process for each of the 13 unchanged
version-2 original-producer suites, in their frozen order. A mismatch,
nonzero semantic exit, crash, timeout, malformed output, or partial failure
does not skip the remaining suites. Complete bounded standard output,
standard error, exact return codes, every original record, every mismatch,
and each genuine failure traceback are preserved. Canonical JSON uses ASCII
escaping so original lone Unicode surrogates are not normalized or lost.

Once an actual activation succeeds, restoration is attempted in `finally`
before any result is published. Full report-based restoration is attempted
first. Its separately authenticated recovery journal allows a reportless
fallback if needed. No campaign may pass or publish if the original canonical
native owners are not genuinely restored. Promotion is individually atomic,
not group-atomic.

A complete restored result is published as a fresh deterministic gzip archive
and a separate fresh canonical receipt. Both are exclusive, mode-0600,
no-follow, independently file-synchronized, exact-byte read back, and
directory-synchronized. A successful publication receipt records the true
candidate result; it does not relabel a candidate failure as a pass. Exactly
13 successful original suites and all 31,237 original cases are required to
qualify. Partial, mismatching, crashing, or un-restored candidates never
qualify.

`--self-test` is fully synthetic, blocks filesystem access, subprocesses,
threads, clocks, networking, temporary files, and imports, and attacks
omissions, duplicate and reordered suites, false zero mismatches, crashes,
timeouts, forged owners, false restoration, wrappers, and holdout access.
`--verify-frozen-context` is strictly read-only; it authenticates the complete
version-2 producer freeze, the exact version-4 activation freeze, every
historical owner, and both actual passing source-build records. Neither mode
starts a campaign or changes a file.

There are zero correctness-qualified candidates. Speed, memory, rankings,
confidence intervals, and regressions are **NOT MEASURED**. The holdout is
**NOT OPENED**. No winner has been selected.
