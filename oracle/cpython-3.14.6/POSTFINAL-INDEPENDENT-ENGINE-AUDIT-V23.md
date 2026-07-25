# Independent native-engine audit V23

Status: prospective source and protocol only. No candidate, current graph,
native owner, audit report, receipt, correctness result, or performance result
is qualified by publishing or testing this document. Production execution is
not authorized until this source and protocol have been independently reviewed,
committed, and pushed.

## Purpose

Independently re-audit all three from-scratch Python `re` replacements after
candidate-source changes. Rust, the C virtual machine, and Zig each need a real,
separately run native owner. The complete denominator is exactly twelve owned
source files and five owned native binaries. The original guarded owner must
actually exercise its family, the Stage 07 sentinel and cached matcher guards,
all thirteen matching guards, all five loader guards, and sixteen ordinary
pickle observations. Standard-library matching, `_sre`, third-party matchers,
foreign native libraries, and cross-family parsing, matching, or FFI must stay
blocked before and after real matching.

The pinned oracle is isolated CPython 3.14.6. Benchmarking, profiling, timing,
locales, holdouts, case fixtures, and correctness-suite execution are outside
this audit. Their status remains `NOT MEASURED` or `NOT ACCESSED`.

## Historical evidence is not a current proof

The canonical V21 base and strict reports, their complete recorded owner
observations, original Stage 07 controls, preserved older ownership incidents,
and their original source/native graph are immutable historical evidence. They
must be authenticated using externally supplied historical report hashes. Never
run V21's live-graph qualification against changed candidate sources. Never
assert that its old graph equals the new graph. A changed owned source or
native binary requires independently executed V23 base and strict owners.

Preserve and independently authenticate both frozen CPython baselines and the
actual V15 Rust failure, its production summary, forensic, and fully durable
receipt. The original matrix contains all 165 upstream methods: 152 public
methods and thirteen separately accounted private methods. No public method is
waived. The authentic private-class waivers are an exact dictionary, not a list:
`DebugTests` has four methods because of `CPython-only textual disassembly of
private matching opcodes`; `ImplementationTest` has nine because of `private
CPython regex compiler, _sre, type internals, and deprecated private
implementation modules`. Each frozen V6 reference has 151 passing public
methods and one exact named private-debug condition. The real skipped record
has `skip_kind` equal to `named-private-debug-condition` and has no
`classification` field. Each role retains all 152 complete original method
dictionaries, their exact source-AST identities, `records_sha256`, and the
independently recomputed full reference status-vector hash.

The actual V15 upstream failure completed all 152 public methods: 139 passed,
eleven had test-harness
interference errors, one had a missing private `_compile` error, and one had
the same named private debug-build skip. Both per-method guard denominators
are 304. The original failure SHA-256 is
`fcd83830b36afd94dee6b926764a6300eaf048d5fa81404563d7e8afea2482c2`.
This is not the earlier, distinct V15 ownership-controller incident with
SHA-256 `a3695f1fd847e9ad882783d18c519b551d7791c5327f55964e202a31ade818ff`.
None of this historical evidence qualifies an edited candidate or a future
upstream run.

## Two independently executed audits

The base audit uses schema `rebar-postfinal-from-scratch-audit-v23`. It first
authenticates this source, this protocol, the preserved inputs, and the original
guarded-worker source. It performs the real complete fresh static source audit,
hashes all twelve sources and five ELF binaries, separately runs all three
guarded native-owner subprocesses, records their actual complete stdout and
stderr, and then independently rehashes the complete graph. Any real worker,
source, native binary, guard, or publication failure is reported exactly once;
partial observations are retained rather than completed synthetically.

The strict audit uses schema `rebar-postfinal-no-delegation-audit-v23`. Its V23
base-report SHA-256 must be supplied externally; it is never predicted or read
from an unauthenticated summary. It authenticates the exact canonical V23 base
bytes, validates all three actual base-owner transcripts, and independently
performs another full static source audit and another three real guarded owner
subprocesses. Both audits must bind the exact same freshly rehashed twelve-source
and five-binary graph. A current graph is never inferred from V21 history.

The only authorized result destinations are:

- `candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V23.json`.
- `candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V23-FAILURES.json`.
- `candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V23.json`.
- `candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V23-FAILURES.json`.

Each result has a separate, equally exclusive
`-PUBLICATION-RECEIPT.json` or `-FAILURES-PUBLICATION-RECEIPT.json`. Reports
and receipts must be canonical strict finite JSON, published using a real
directory-relative `O_EXCL | O_NOFOLLOW` creation, complete observed writes,
file and directory `fsync`, and a complete no-follow reread. Success is possible
only after independently observed successful closes of the writer, reread, and
parent-directory descriptors. A real operating system may reuse the writer's
descriptor number for the reader after the writer has closed. V23 therefore
validates the complete ordered, role-tagged open and close event history; it
permits sequential numeric reuse and rejects simultaneous live aliases,
repeated close attempts, missing transitions, and invented roles. Existing
evidence is never replaced or repaired. Publication failures retain the first
real error, the actual partial-write ledger, and every separately observed
cleanup-close failure. Each live descriptor is consumed and closed at most
once; a cleanup error never masks the first failure or prevents the remaining
cleanup attempts.

## Candidate-free source gate

`--self-test` is strictly source-only. It may read only the V23 source and this
protocol before entering the existing independently guarded source-only
boundary. It must not open evidence, candidates, native binaries, correctness
fixtures, reports, receipts, or holdouts; start workers; import candidates or
foreign engines; write files; or sample a clock. In-memory adversaries must
demonstrate rejection of stale historical graphs, changed sources and ELF
hashes, wrong report schemas and hashes, cross-family matcher and FFI ownership,
weakened Stage 07 guards, incomplete or forged process stdout, invented
observations, unsafe destination paths, missing exclusive/no-follow flags,
incomplete writes, missing file or directory durability, false rereads,
genuine writer-to-reader descriptor reuse, simultaneous live descriptor
aliases, writer, reader, and parent close failures, combinations of genuine
primary and cleanup failures, and repeated or invented close observations.
Synthetic controls also reject fake private-waiver lists, changed authentic
private-class mappings, classification-only skips, forged full-record hashes,
and changed original reference vectors. Synthetic controls never qualify a
candidate. Source-only output is one complete JSON object and records zero
production effects.

## Production entry points

Use the exact isolated pinned CPython, with `PYTHONDONTWRITEBYTECODE=1`,
`PYTHONHASHSEED=0`, and the canonical repository root as `PYTHONPATH`.

`--ownership-audit --historical-v21-base-sha256 HASH
--historical-v21-strict-sha256 HASH` produces only a fresh V23 base result and
its durable receipt.

`--strict-audit --base-report-sha256 HASH
--historical-v21-base-sha256 HASH
--historical-v21-strict-sha256 HASH` independently produces only a fresh V23
strict result and its durable receipt.

Running a source-only gate is not running either audit. Until the two complete
production reports and receipts exist, independently authenticate, and describe
the identical current graph, V23 remains `NOT RUN` and no candidate qualifies.
