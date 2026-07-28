# Safely recover all four original files after testing repaired Rust

Status: SOURCE FROZEN. The Rust candidate, recovery controller,
signal handlers, public lock, recovery journal, and native files have not been
run, installed, created, read, or activated.

Use stable CPython 3.14.6 and all 31,237 unchanged original tests. Preserve
all 13 original test groups, all 13 named private exceptions, every genuine
matching result, and all original nested interpreter events. An unrun or
failed implementation is never a passing candidate.

## Keep the current evidence and prior controller unchanged

The current, separately frozen V27 overview has 143 independently recorded
evidence owners and 148 authenticated references. Keep the actual prior V26
history of 141 owners and 146 references. The first Zig preflight started no
candidate. The genuinely completed repaired Zig campaign started 13 original
workers, found 2,172 mismatches, verified 2,847 passing cases, and had no
infrastructure failures. Preserve both failures separately without expanding
the 198,178,404-byte archived matching stream. C has 1,262 real mismatches
and 7,325 verified passing cases. Repaired Rust matching is NOT MEASURED.

Keep the entire committed V2 Rust source, protocol, and machine contract
unchanged. Its hashes are respectively
a6ffce3eb9ff09f27f3e35f84b35b9d1aba6e29dae225c56c036de85e089b7b3,
9b9a246a08c0e89667899a6317df41424320617f7c4ac6cb84ef210fabee1ca0,
and bc100f6a7a3d4ec2640e131211ecea202172846daa10c93d73cbf58ea74ed547.
Reuse its 13 original isolated workers only. Never run its unsafe controller
or its nonpublic activation routine.

## Make recovery visible before touching anything

One future, explicitly authorized run has exactly one public root:

`/tmp/rebar-phase2-repaired-rust-original-campaign-v2-safe-v3-phase2-v11-rust-dual-overlay-original-p0`

Create this exact directory exclusively with owner-only `0700` permissions.
Create an owner-only `0600` lock and acquire an exclusive, nonblocking
operating-system lock. Never share an active journal with another controller.
If the root already exists, refuse to activate; explicitly recover the
existing attempt instead.

Before replacing any file, durably create and read back
`recovery-journal.json`. Announce the exact root and complete journal SHA-256
on standard error. Independently pin all four original device numbers,
inodes, owners, permissions, link counts, sizes, and complete hashes:

- Rust bridge source: inode 419054, mode `0600`, SHA-256
  f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b.
- Public Python adapter: inode 428100, mode `0600`, SHA-256
  6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b.
- Matching engine: inode 430563, mode `0755`, SHA-256
  f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4.
- CPython bridge: inode 430629, mode `0755`, SHA-256
  6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15.

All four actual originals have device 2064, owner 1000, and one link. Back
up each actual original inode as a no-follow hardlink in its own directory;
never substitute a copy. Durably record every individual hardlink,
promotion, and reverse-recovery intention before its corresponding action.
Four individually atomic replacements are not one group-atomic operation.

## Handle real interruptions honestly

Only the explicitly requested future controller installs `SIGINT`,
`SIGTERM`, and `SIGHUP` handlers. Block those signals during each durable
journal, hardlink, replacement, and recovery critical section. Graceful
signals cause exact reverse restoration and an honestly failed campaign;
neither Python `KeyboardInterrupt` nor `SystemExit` is swallowed.

`SIGKILL`, operating-system termination, and power failure are not catchable.
Do not claim they automatically run cleanup. Their independently durable
journal makes exact recovery possible through a separately caller-pinned
public `--recover --activation-root ROOT --recovery-journal-sha256 HASH`
command. Recheck the frozen V3 controller, V2 worker, current V27 overview,
and all explicit caller-pinned original provenance before recovery. Open
only descriptor-bound, owner-only journal and lock files. Reject unknown,
changed, or foreign targets. Restore the actual original bridge, engine,
adapter, and bridge source, in that exact reverse order, and recheck their
complete original bytes. The same authenticated recovery can be safely
repeated.

## Freeze the source without activating Rust

Render one canonical machine contract from the exact V3 source and protocol.
Run both `--self-test` and `--verify-frozen-context` twice: ordinarily and
under a genuinely sterile `env -i PATH=/usr/bin:/bin`. Use the exact isolated
CPython executable, `-I -B`, and independently pinned source, protocol, and
contract hashes.

Every gate must install zero signal handlers, acquire zero recovery locks,
create zero directories or journals, read or stat zero original files, start
zero candidate or reference workers, load zero candidate native libraries,
sample zero clocks, and open zero final-holdout cases. Test hostile synthetic
signal, lock, filesystem, subprocess, import, and recovery claims without
performing the corresponding effect.

Only a separately authorized actual campaign may run the exact frozen V2
worker processes. Preserve all original worker output and all mismatches.
Publish an exclusive, fully reread, single-member zero-time gzip archive and a
separate durable receipt only after all four original inodes are proven
restored. A publication receipt verifies publication; it does not convert a
failing candidate into a passing candidate. Performance, undefined behavior,
memory, and the final holdout remain NOT MEASURED or NOT OPENED.
