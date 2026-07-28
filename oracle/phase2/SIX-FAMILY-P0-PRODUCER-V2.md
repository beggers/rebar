# Frozen original P0 producer, version 2

This freeze extends the independently pinned version-1 producer without
changing a single original correctness test. Its only new execution capability
is to verify an already completed, reversible version-4 native activation.
Verification does not build, activate, promote, import a candidate, execute a
reference, start a timer, read a benchmark, or open the holdout.

The baseline is the separately pinned, stable CPython 3.14.6. The denominator
remains exactly 13 original test suites and 31,237 original cases. The original
152 upstream records contain one genuine debug-only skip and 151 runnable
public cases; exactly 13 named private waivers remain. Every original source,
matrix, expected result, full-width seed, evaluator, and suite order is pinned
in the accompanying canonical machine contract. No extra case replaces an
original obligation.

The real subinterpreter test still runs all 128 original cases using 394 case
calls across 11 genuinely created and destroyed temporary interpreters,
including eight fresh interpreters. Its child continues to authenticate the
original version-1 producer; substituting the version-2 hash would break the
frozen child. The historical failed Zig run made only 385 calls and remains a
failure. Real buffer exporters, real shared-pattern threads and barriers, all
64 locale cases, and all 192 locale transitions are preserved.

There are six independently owned source families: C, Rust, Zig, C++, Go, and
Fortran. Their 25 semantic source owners are disjoint. C and C++ each have one
combined native engine and bridge. Go has genuinely separate native engine and
Python bridge outputs. Its compiler-generated header is verified as build-only
and must never be promoted as a third matching target. No engine may call
Python's matching engine, wrap a third-party matching package, borrow another
candidate, silently fall back, or substitute prerecorded results.

The freeze retains all 65 genuinely distinct owner-only historical evidence
files: 51 candidate owners, six version-4 source-build owners, four version-5
source-build owners, and four version-6 source-build owners. The historical
compiler-process ledger is exactly 39 original version-2 processes, 15 Zig
version-3 processes, 32 version-4 processes, 31 version-5 processes, and 52
version-6 processes: 169 in total. Process identifiers are asserted unique
only within each actual report.

C, Rust, Zig, C++, and Go have genuinely successful source builds. Only C,
Rust, and Zig have historically runnable frozen-original-suite evidence.
C++ may become runnable only after its actual passing version-4 build and a
version-3 or version-4 recoverable activation are independently authenticated.
Go may become runnable only after its actual passing version-6 build and a
version-4 recoverable activation are independently authenticated. A real
activation must provide matching, owner-only report, receipt, recovery journal,
every promotion intention, the exact original build evidence, both independent
build phases, and every current canonical native device and inode. No producer
mode creates an activation. Every version-5-only or failed Fortran build
remains ineligible.

Exactly zero candidates have passed all original correctness obligations.
Neither an actual source-build PASS nor an activation PASS implies a candidate
correctness PASS. Speed, memory, confidence intervals, regressions, and the
expanded holdout are **NOT MEASURED**. The holdout is **NOT OPENED**. No winner
has been selected.

`--self-test` uses only explicitly synthetic, guarded in-memory controls; it
cannot read files or import a candidate. `--verify-frozen-context` is strictly
read-only and independently authenticates the original version-1 producer,
the version-4 activation triple, all 13 suites, all 25 first-party sources,
all 65 history owners, and the exact 169-process ledger. Only explicit `--run`
can reuse the original version-1 suite evaluator, and only after proving the
selected family's genuine, already completed, version-correct activation.
