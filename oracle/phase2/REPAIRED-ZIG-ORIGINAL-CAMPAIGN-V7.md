# First-party Zig original correctness campaign, version 7

Status: SOURCE FROZEN; actual version-7 matching NOT RUN.

## Evidence from the previous actual run

The pushed version-6 campaign actually attempted all 13 original suites in
13 distinct workers, with process identifiers 81 through 93. Its authenticated
plaintext receipt records exit status 1, zero standard-output bytes, and
106 standard-error bytes with the same SHA-256 for every worker:

    0eae62828a696afbaaaa1212c0979f0b86afe95f59d1870f3ad0dea7fe2c08b7

No original suite completed. All 13 results were infrastructure failures;
semantic mismatches were NOT MEASURED. All three original files were
restored. A PASS on that receipt means durable publication, not candidate
correctness. The actual exception message and cause are NOT ESTABLISHED:
version 6 published only the error hash, and this version never opens or
inflates its archived matching evidence.

## Complete bootstrap failure reporting

Version 7 puts the entire worker bootstrap and original observer inside one
outer BaseException boundary. Named stages cover active-context verification,
worker authority, the three original-owner checks and recovery journal,
guard construction and installation, first-party native-family preparation,
candidate import, immutable family selection, and original observation.
Every real exception is returned as a genuine infrastructure failure with
its actual exception class, bounded original message, bounded literal
traceback and frames, exact activation stage, and guard/import state.

Worker failure JSON is encoded by a small first-party canonical encoder
before any additional post-guard module is loaded. Source-only tests prove
its output matches the pinned immutable correctness producer byte for byte.
No external regular-expression engine, Python regex engine, other candidate,
package wrapper, ctypes fallback, test answer, or benchmark detector is used.

## Literal standard error and exhaustive workers

The complete real captured standard-error stream remains retained and
authenticated in the original result archive. Its first 4,096 actual bytes,
the complete stream size and SHA-256, and whether truncation occurred are
also copied into both the plaintext publication receipt and actual-run
standard output for each of all 13 suites. If a process cannot be started
or its output cannot be captured, the public result explicitly says NOT
AVAILABLE and NOT MEASURED; it never invents standard-error contents.

Each original suite still receives its own 120-second allowance. The sum
of the 13 allowances is 1,560 seconds, excluding process startup, stream
handling, safe recovery, and publication. Every suite is attempted after
any timeout, process-start exception, native bootstrap failure, or semantic
failure. A timeout or bootstrap failure never becomes a semantic pass.

## Immutable correctness and recovery boundaries

The reference remains CPython 3.14.6 and exactly 31,237 observations in
all 13 original suites, with all 73 obligations, 34 crosswalks, and 13
named private waivers unchanged. The distinct 8,244-case differential
candidate run is NOT RUN and is never added to the original denominator.

The native inputs remain the independently verified, first-party version-13
Zig engine and bridge, their 26 actual build processes, the immutable
strict version-2 runtime guard, and the exact guard-clean first-party
adapter. An explicit fully pinned actual run alone can use them. The
durable three-role recovery journal, adjacent exact-inode backups, mode
0600 staging, signal-masked recovery, and restoration of every original
inode before publishing remain mandatory.

Original locale data must be prepared independently and the actual run
accepts only this exact existing LOCPATH:

    /tmp/rebar-official-locale-proof-0EdjeBJ1lS

Source-only verification never opens locale data, a native library, a
private build root, a matching archive, a benchmark, a holdout, or a
clock. It never starts a worker or runs any candidate.

## Holdout and honest qualification

The expanded 14,155,776-case performance holdout remains a pre-phase-3
proposal: NOT FROZEN, NOT GENERATED, and NOT OPENED. The earlier
4,194,304-case proposal is preserved. At least three fully correct,
independent candidates are required; the qualified count is still zero.
Performance, memory, undefined behavior, and a winner are NOT MEASURED
or NOT SELECTED.

## Source-only hostile controls

The pinned campaign must pass --self-test and --verify-frozen-context in
both the normal environment and env -i PATH=/usr/bin:/bin LC_ALL=C under
CPython 3.14.6 with -I -B -S and all three independent version-7 hashes.
The self-test actually injects a synthetic exception before active-context
verification, confirms that no candidate or native library was touched,
and checks the resulting stage, real class, bounded traceback, and exact
producer-compatible worker JSON.

It separately constructs 13 explicitly synthetic infrastructure results,
passes their genuine synthetic stderr through the same public-diagnostics
code used by actual publication, and confirms that literal stderr is
present in canonical forms of both public outputs. Source-only fixtures
are labelled synthetic, start zero workers, create no results, and never
qualify a candidate. Crossed stderr owners and oversized excerpts are
rejected or demonstrably bounded.

Only a separately authorized, fully pinned --run may execute version 7.
Rendering, self-testing, and source verification never run that campaign.
