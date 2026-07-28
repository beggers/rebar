# First-party C Match pickle repair, version 2

This is a source freeze, not a candidate run, passing replacement, native build,
speed result, or opened holdout. The original CPython 3.14.6 correctness oracle
still has 13 groups, 31,237 counted checks, and exactly 13 previously named
private exclusions. Existing C results remain **FAIL: 1,262 semantic
mismatches**. Correctness for the proposed repair is **NOT MEASURED**.

The complete published 6,912-case C public-types archive contains 248 real
differences. Exactly 32 are Match pickling: the reference successfully pickles
16 matches with protocol 0 and 16 with protocol 1, while the tested C candidate
incorrectly raises `TypeError`. The same complete evidence contains 16 correctly
rejected matches for each of protocols 2, 3, 4, and 5. The misleading cohort
name `pickle-match-rejection` is not permission to reject protocols 0 and 1 or
to allow protocols 2 and above.

The checked-in C source, Python adapter, and restored native library remain
untouched. The repair first independently reproduces the entire frozen V1 C
source, including its existing replacement-buffer ordering correction. It then
changes only the uniquely anchored native `Match` reduction and its
`__reduce_ex__` method entry. Protocols 0 and 1 use the existing authenticated
native `VMModuleState.scanner_reconstructor`, the candidate's own
`VMModuleState.match_type`, `PyBaseObject_Type`, and `None`. Protocols 2 and
above retain the original `cannot pickle 're.Match' object` exception. The
scanner, substitution engine, buffer flags, callable dispatch, original source
bytes, and every other candidate remain unchanged.

All four already published version-25 graph owners are independently pinned.
The source-only gate reproduces the complete graph snapshot and its chart
without inspecting a private Rust or Zig build root. It preserves the real 139
evidence owners and 144 authenticated references, all 30 original C campaign
evidence owners and 13 actual candidate workers, the 1,262 existing C
mismatches, and the actual 28-process Rust and 26-process Zig builds. Neither
build proves candidate correctness. The actual C public-types archive, its
separate durable receipt, every one of its 6,912 records and 248 differences,
and all 96 Match-pickling observations must agree before this repair is
accepted.

Only an explicit `--apply --snapshot-root` may materialize a derived compiler
input. The application uses the exact same two-phase, owner-only private C
build-root convention as the existing V1 source builder. It requires both
distinct `reference-a` and `reference-b` phases, owner-only 0700 source
directories, and a previously nonexistent `candidates/_vm_native.c`. It
creates that single file with no-follow, exclusive, descriptor-relative 0600
ownership, checks the exact bytes and inode, synchronizes it, and rechecks the
unchanged repository sources. Verification and self-tests never enter apply
mode.

Ordinary and empty-environment self-tests explicitly block filesystem access
and writes, candidate and standard-library regex imports, compiler or candidate
processes, threads, networks, private roots, all performance clocks, and waits.
Read-only verification independently authenticates the full frozen source,
published graph, prior V1 repair, and original signed evidence. No repaired
correctness result, speedup, comparison, confidence interval, memory result,
qualified candidate, activated native library, future winner, or holdout result
is authorized or inferred.
