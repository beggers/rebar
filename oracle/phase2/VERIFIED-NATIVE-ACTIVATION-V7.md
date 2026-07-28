# Zig native owner normalization V7

This is a narrowly scoped correction to the published V6 Zig activation. It
does not edit, rerun, or erase the V6 activation, the first attempted V1 Zig
correctness campaign, the unchanged original test suite, or either original
native file. Zig correctness and speed remain NOT MEASURED.

## Preserve the actual first failure

The once-only V1 Zig campaign actually failed before native activation and
before any original matching worker was started. The unchanged mature V2
file reader returned the seven fields relative, path, SHA-256, byte size,
device, inode, and permission mode. V6 correctly required the actual original
single-hardlink count and owner UID, but incorrectly expected those two
additional fields to already exist in the V2 return dictionary.

Consequently a genuine, unchanged original Zig engine was rejected during
pre-activation baseline authentication. The actual result is an infrastructure
failure: zero candidate workers, zero native activations, no matching outcome,
and no original campaign archive or receipt. The exact candidate mismatch
count, process PID, stdout size, stderr size, and number of target reads are
NOT RECORDED by this V7 source protocol. A separate independently owned
failure recorder preserves the real observed process. V7 never invents an
actual passing worker, removes the failure, or changes its meaning.

## Correct exactly one integration boundary

V7 loads the exact digest-pinned, unmodified V6 source and wraps only its
mature V2 file-reader boundary. The original reader first proves the complete
content, SHA-256, seven original ownership fields, and exact expected byte
size. V7 then independently reopens every parent and the same regular file
using no-follow descriptors.

It authenticates descriptor and named inode agreement; the exact same device,
inode, mode, size, and bytes returned by V2; the complete second SHA-256
readback; a stable device, inode, size, modification and change timestamps;
the actual descriptor-observed UID; and exactly one real hardlink. It rejects
symlinks, swapped or linked files, foreign owners, short reads, hidden suffix
bytes, changed content, false metadata, and time-of-check races.

Only after those checks does it return the original V2 fields plus the two
real observed fields. The single wrapper automatically covers actual original
targets, private source-build phase outputs, promoted native targets, and
reverse original-inode recovery. It does not weaken any V6 comparison, invent
metadata, rely on a path-only stat, alter the original matcher, add a package,
or touch another language.

## Preserve original source, build, and recovery history

The authoritative published V25 history remains 139 evidence owners and 144
authenticated references. Existing C retains its actual 13 workers, 7,325
passing executions, and 1,262 mismatches. Existing Rust retains 28 actual
compiler and inspection processes with two public and two bridge source
repairs. The original corrected V3 producer retains all 13 groups, 31,237
case executions, and 13 named private waivers.

The genuine Zig V11 build retains its actual 26 compiler and inspection
processes, both separately built first-party native roles, and its distinct
build-time snapshot of 135 evidence owners and 140 references. The original
user-owned engine inode is 431260 and the original bridge inode is 431274;
both are owner-only mode 0700 with a single hardlink. V7 source verification
never opens, hashes, reads, stats, links, stages, promotes, or replaces either
original native target.

Actual future activation, only when separately and explicitly authorized,
inherits V6 without semantic changes. The durable intention-first same-device
hardlinks, exact original device and inode, complete recovery journal, and
bridge-before-engine reportless recovery are preserved. Each file replacement
is individually atomic; a two-file group-atomic transaction is never claimed.
No C or Rust native file is accessed.

## Source-only gates

The synthetic gate runs under real blocked filesystem, native-loading,
subprocess, clock, thread, import, and network controls. It reproduces the
seven-field missing-UID-and-hardlink failure using wholly synthetic data,
accepts only actual descriptor-shaped nine-field metadata, and rejects altered
UIDs, extra hardlinks, false booleans, substituted bytes and inodes, erased
first-run failures, weakened hashes, and changed history.

The context gate independently authenticates the exact published V6 and V1
three-owner freezes, the mature V2 source, unchanged V3 producer, actual Zig
and Rust source-build evidence, all original cases, and truthful V25 history.
Run each gate with ordinary isolated CPython and genuinely sterile env -i.
Source-only gates never start a worker, activate a library, inspect a native
target, open a private activation root, publish evidence, read a benchmark,
sample a clock, or open the final holdout.

Never execute the actual V7 activation or recovery until this exact V7
source, protocol, and machine contract have been independently reviewed,
committed, and pushed.
