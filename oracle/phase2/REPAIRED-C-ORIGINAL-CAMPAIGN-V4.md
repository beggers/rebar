# First-party C candidate: original-suite correctness campaign, version 4

This campaign checks the source-built C15 first-party regular-expression engine
against the unchanged, frozen CPython 3.14.6 correctness oracle. It does not run
or inspect the performance holdout. A passing source build is not a correctness
result: every one of the 13 original-suite workers must actually be run, and all
31,237 frozen obligations must remain accounted for.

The original C adapter and C source remain at their original paths and hashes.
Only the canonical compiled C extension is temporarily activated. The pinned
build lies on a different filesystem from the candidate. The controller reads
the exact C15 phase-A owner and copies it to a new exclusive, no-follow staging
file in the candidate directory; it never renames, moves, or links a build
output across filesystems. Before activation, it durably journals the original
native inode and preserves it using a same-directory hard link. It atomically
replaces only the staged native extension and restores the exact original inode
on normal completion, failure, interruption, or explicit recovery.

The exact journal-bound promotion intention is durable before the exclusive
staging file is created. The new staging inode is separately recorded and
fsynced before any native bytes are streamed. Its intention is first written,
verified, and fsynced under a private pending name, then atomically published;
a truncated final intention is never visible. If power loss occurs in the
unavoidable gap between file creation and recording its inode, public recovery
first restores the exact original inode. It then verifies the earlier durable
promotion intention, authenticates the original private C15 build output, and
opens only the reserved staging name through the locked candidate-directory
descriptor. Recovery checks the regular owner, exact device, fresh single-link
inode, allowed mode, bounded size, stable visible identity, and that every
staged byte is an exact prefix of the separately authenticated C15 binary.
Only that verified inode is unlinked, and the candidate directory is fsynced.
A missing intention, substituted owner, symlink, extra link, foreign prefix,
oversized stage, or changed inode fails closed.

The frozen original-suite producer provides observations, not its legacy
controller. Version 4 launches exactly 13 independently identified original
workers and calls the producer's unchanged original-suite observers with the
original C adapter and source pins. A complete failing observation is evidence
of a failing candidate, not an infrastructure error. Original subinterpreter
obligations, all mismatches, all worker exits, and bounded stdout and stderr
are retained.

Frozen support documents are bounded independently at 32 MiB. Actual original
worker output is accepted through its full declared 64 MiB bound; synthetic
size-bound checks do not allocate or generate large fake worker streams.

After restoration has been independently verified, the controller may stream
one new immutable C-specific evidence archive through the frozen publisher's
low-level descriptor-bound publication primitives. It does not use that
publisher's C++/Go-only family naming, freshness gate, or legacy activation
validator. Its exclusive no-follow receipt separates successful publication
from the candidate's actual correctness result.

`--self-test` and `--verify-frozen-context` are source-only inspection modes.
They do not create temporary files, install signal handlers, change a signal
mask, acquire a lock, inspect a candidate source or native extension, inspect a
private build root, import a candidate, run a worker, touch the holdout, or
publish evidence. Run both modes in the ordinary environment and in a sterile
`env -i` environment before any actual campaign.
