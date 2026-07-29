# First-party Zig original correctness campaign, version 6

Status: SOURCE FROZEN; actual corrected Zig matching NOT RUN.

## What this freezes

The immutable CPython 3.14.6 reference remains exactly 31,237 original case
executions in all 13 frozen suites. The suite source, case order, seeds,
73 obligations, 34 crosswalks, and 13 named private waivers do not change.
The separate 8,244-case, two-reference differential corpus is not part of the
31,237 denominator and candidate matching against that corpus is NOT RUN.

This campaign independently authenticates every pushed version-5 source owner,
the complete immutable original-case producer, the version-2 runtime guard,
the actual two-phase version-13 Zig build and all 26 distinct build processes,
both first-party native source files, and the guard-clean Zig adapter. The
build receipts authenticate only the native engine and bridge; they do not
claim to build or independently attest the new Python adapter.

## Fixed exhaustive timeout

Each of all 13 original suites has its own fixed 120-second worker timeout.
The campaign attempts every frozen suite in the original order, even if any
earlier suite times out, crashes, or otherwise fails. The sum of the 13
worker timeout allowances is 1,560 seconds. Worker startup, output handling,
process termination, recovery, and publication are extra; this is not a
claim that the complete campaign finishes in exactly 26 minutes.

Timeouts and missing or invalid observations are infrastructure failures,
not passing cases. The complete stdout, stderr, exit status, worker process
identity, suite denominator, timeout classification, and any valid observed
failures are captured separately for each attempted suite. An incomplete
campaign reports the total semantic mismatch count as NOT MEASURED rather
than inferring results for unobserved cases. No suite, pattern, observation,
or original correctness obligation is removed, sampled, or abbreviated.

Both the durable plaintext publication receipt and actual-run standard output
repeat the timeout count, the exact timed-out, completed, and failed suite
names, infrastructure and observed mismatch counts, and all 13 ordered suite
diagnostics. These include actual process identities, exit statuses, reported
worker failure details, and authenticated complete stdout and stderr sizes and
hashes. The unchanged complete stream payloads and individual original case
observations remain in the separately authenticated archive. Identifying and
reproducing a failed suite does not require inflating that archive.

A complete original-suite pass still does not qualify the candidate: the
separate 8,244-case differential candidate campaign and strict runtime
independence remain required and are NOT RUN and NOT ESTABLISHED.

## Native ownership and recovery

Only an explicit separately pinned actual run can activate the exact
first-party native engine, bridge, and guard-clean adapter. Before changing
any canonical target it durably records three authenticated original inode
owners, saves adjacent same-device backups, and publishes a recovery journal.
It stages exact authenticated replacement bytes at owner-only mode 0600.
The immutable strict guard is installed before candidate import. It starts
one isolated pinned-CPython worker per original suite and restores all three
original inodes under signal-masked recovery before publishing a distinct
canonical evidence archive and receipt.

The original locale must already exist independently at:

    /tmp/rebar-official-locale-proof-0EdjeBJ1lS

The actual run requires that exact LOCPATH. Source-only modes do not open
that directory, any native library, the private build root, an archive, a
holdout, a benchmark, a clock, or a candidate. The campaign never creates
locale data, delegates matching to CPython, imports an external regular
expression package, uses another candidate, or adds a fallback.

## Holdout and honest project status

The expanded 14,155,776-case holdout is solely a sealed pre-phase-3 public
proposal. Its final protocol and generator are NOT FROZEN; its secret and
cases are NOT GENERATED; no holdout is opened or timed. The historical
4,194,304-case proposal remains authenticated. Three independently complete
and runtime-independent candidates are required; the current qualified
candidate count remains zero. Speed, memory, undefined behavior, and the
final winner are NOT MEASURED or NOT SELECTED.

## Source-only checks

Run each action under the pinned CPython 3.14.6 with -I -B -S, first in the
normal environment and again under env -i PATH=/usr/bin:/bin LC_ALL=C.
Pass the independently computed SHA-256 of this campaign source, protocol,
and canonical JSON as --source-sha256, --protocol-sha256, and
--contract-sha256 respectively. Both --self-test and --verify-frozen-context
must pass in both environments. Contract rendering accepts only
--render-contract and the source and protocol hashes; it has no actual-run
authority.

Only separately invoke --run with all independent exact family, label, build
receipt, root receipt, producer, runtime guard, and adapter SHA-256 pins,
the exact external LOCPATH, and the frozen version-6 JSON. Source freezing,
rendering, self-tests, and verification never invoke the actual run.
