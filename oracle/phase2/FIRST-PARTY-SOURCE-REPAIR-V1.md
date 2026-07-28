# First-party C source repair, version 1

This is a source freeze, not a passing candidate, a build, an activation, or a
performance result. The original 13-suite, 31,237-case CPython 3.14.6 correctness
oracle and its 13 named private exclusions remain unchanged. The 4,194,304-case
holdout remains unopened. Performance, memory, safety, and candidate correctness
for the proposed repair are **NOT MEASURED**.

## Exactly what changes

The checked-in C candidate remains byte-for-byte unchanged: its 218,185-byte
SHA-256 is
`bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55`.
Its independent checked-in Python adapter also remains unchanged.

The source-only tool freezes exactly one replacement within the existing
`pattern_substitute` function. For a non-callable replacement, it validates and
acquires the replacement template before acquiring the subject. This restores
the reference acquisition order without changing the existing `PyBUF_SIMPLE`
buffer flags, the argument/count-validation order, the template implementation,
the replacement engine, or another candidate. A template error returns before a
subject exists. A failed subject acquisition releases its compiled template once
and does not release the subject twice. Callable replacements still acquire the
subject first. Successful replacements retain the original single cleanup label.

The entire derived 218,308-byte C source has SHA-256
`f44694759174c1c3975423e07095ae91a853e66242c4e55d11836df03a730c4d`.
It is not written, built, activated, imported, or tested by a source-only gate.
The repair does not change `match.expand`; existing `match.expand` failures must
not be counted as repaired. Archived failures remain failures until a separately
authorized run of the original frozen correctness suites measures otherwise.

## Preserved evidence

The published version-19 overview still counts exactly 71 historical evidence
owners, six independent first-party language families, 25 original source
owners, five historically tested families, zero passing candidates, and zero
currently active targets. Its recorded Go campaign remains a failed run of all
13 original suites: 4,518 semantic mismatches, four infrastructure failures,
and a successful restoration. The gate separately authenticates all 76 distinct
digest-addressed historical file references published by the overview and its
inputs. That 76-file authentication closure is not the 71-owner evidence
denominator and does not replace it.

The gate verifies each of the original 25 source owners independently, the
unaltered original correctness manifest, the unchanged version-7 source freeze,
all four unchanged version-19 overview owners, all 76 referenced historical
files, and the exact unique old-to-new full-source transformation. Historical
renderers, archives, candidates, compilers, and performance code are never run.

## Explicit future application

Only an explicit `--apply --snapshot-root` may materialize the derived source.
The accepted root must be a fresh owner-only mode-0700 directory matching
`/tmp/rebar-phase2-native-build-v8-c-*/reference-a/source` or
`/tmp/rebar-phase2-native-build-v8-c-*/reference-b/source`. Both distinct,
owner-only phases must already exist. The `candidates` source directory must
also be owner-only. The tool creates only a previously nonexistent private
`candidates/_vm_native.c`, using no-follow, exclusive descriptor-relative
creation and mode 0600; verifies its unique inode and complete bytes; and
rechecks that the original checked-in C source remains unchanged. Relative,
workspace, existing, external, linked, aliased, or symlink-substituted targets
are rejected. Source freeze and context verification never invoke this mode.

Normal and empty-environment self-tests are source-only: their explicit effect
boundary blocks file access, file changes, candidate/stdlib imports, processes,
compiler execution, networks, clocks, temporary directories, and threads.
Read-only context checks authenticate the frozen files without running any
renderer, candidate, compiler, correctness suite, benchmark, or holdout.

No corrected-source correctness claim, qualified candidate, comparison, timing,
speedup, confidence interval, memory result, holdout access, or winner is
authorized or inferred by this freeze.
