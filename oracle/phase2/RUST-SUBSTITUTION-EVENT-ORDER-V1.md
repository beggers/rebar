# First-party Rust substitution event-order source freeze V1

This append-only Phase 2 freeze changes exactly one existing first-party C
function, `rust_substitute_core`, without building, importing, executing, or
qualifying a candidate. Its already materialized input combines the safe
changing-capture clamp and the removal of the native bridge's private external
introspection path:

```
candidates/rust/variants/no_external_introspection_v1/py_bridge.c
bytes: 177146
sha256: 2dd040dc0337f205134431ebeaafe56ee4fe63cc77c1bb6cb5434742549884b7
device: 2064
inode: 524811
mode: 0600
links: 1
```

The input is authenticated indirectly by the complete public, pushed
no-external-introspection application receipt, SHA-256
`57e28ad65b538db5189f264904d303f37f13506022eae07b12185a52f2624a43`.
Source verification and self-test do not open this candidate source. Only the
separately authorized root materialization may open it, exactly once.

The frozen predicted output is:

```
candidates/rust/variants/substitution_event_order_v1/py_bridge.c
bytes: 177335
sha256: c69e24a87c251a332b79c4f4b5ed1a9f232847e446518930473a2ec871f020ab
source delta: +189 bytes
changed function count: 1
exact reversible replacement sites inside that function: 4
```

The private getter and `inspect`/`functools` import chain remain absent. The
existing capture-clamp implementation, Python adapter, first-party matching
engine, replacement cache, `PyBUF_FULL_RO`, public descriptors, callable
replacement behavior, and `rust_match_expand` are byte-for-byte unchanged. No
regular-expression fallback, cross-family engine, external dependency, canonical
source mutation, or existing-variant mutation is authorized.

## Authentic complete predecessor failure

The complete, published V25 original-campaign failure receipt is authenticated
by SHA-256
`d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59`.
It reports a successful durable publication, an actual **candidate FAIL**, all
13 original workers and suites, all 31,237 original cases, 15,877 verified
passing cases, and 1,352 semantic mismatches:

```
substitution_v2:  240 / 5,120
shape_v2:       1,112 / 10,240
```

Its original compressed failure archive is identified exclusively by the
complete authenticated publication receipt:

```
archive sha256: dee05f06d473af52db5447b485265d886e66e5420cb3e814b5b972d8798a04a7
archive bytes: 3771743
archive inode: 524845
archive content opens: 0
archive inflations: 0
```

The complete V25 offline build publication receipt is separately authenticated
by SHA-256
`55cdccb1114e0cc7e4bdcecb8311b3c80c4e020dcfdabd1d8597cf3cececeefc`.
It documents 28 historical first-party compiler processes; this source-only
freeze starts none.

## Precisely scoped first-party correction

CPython validates a noncallable replacement before acquiring its subject. The
prior bridge instead opens the subject first. A failing replacement therefore
incorrectly touches its subject; a failing shape-changing replacement can also
lose its genuine `BufferError` and surface a later subject-side `TypeError`.

The replacement cache and Python `_cached_template` interface are unchanged.
For every noncallable replacement, call the existing `rust_replacement_cache`
before `rust_subject_open`, using validation length `0`. The existing adapter's
validate-only dummy `Match` never reads match bounds, so zero is sufficient and
does not inspect or acquire the subject. Replacement normalization, escaped
template parsing, cache hits, fixed custom hashes, unhashable templates,
`PyBUF_FULL_RO`, exception restoration, and failing exporter attempts remain in
the same order as before, but now occur before any subject event.

For successful deferred noncallback literal replacements, first copy the tail,
then release the subject, then call `PyBytes_Join`. This permits genuine
replacement exporter reacquisitions during the join to occur after subject
release, including on-release subject mutation. An explicit one-bit ownership
guard prevents duplicate release on both normal completion and errors after the
early release. Callable replacements retain their original subject lifetime,
callback order, matching semantics, and error handling.

The transform is exactly reversible at four unique sites, all confined to
`rust_substitute_core`: initial validation/acquisition order, the deferred
noncallback pre-join release, guarded successful cleanup, and guarded error
cleanup. All other function bytes remain identical.

The exhaustive source-only PEP-688 model enumerates all 240 historical
substitution failures: five cohorts of 48, or four substitution APIs of 60.
The five cohorts are stable nested exporters, mutating nested exporters,
stable fixed-hash templates, mutating unhashable templates, and failing
templates. The cases contain 128 successful escaped templates, 64 successful
literal templates, and 48 failing templates. For example:

```
escaped stable: replacement+0, replacement-, replacement+0, replacement-, subject+0
escaped fixed:  replacement+0, replacement-, hash, replacement+0, replacement-, subject+0
escaped unhash: replacement+0, replacement-, replacement+284, replacement-, subject+0
literal:        replacement+0, replacement-, subject+0, subject-, join replacement+
failing:        replacement-error0, replacement-error0, replacement-error284
```

No failing replacement acquires its subject. Every owner acquisition/release is
balanced. Fixed hashes remain singular and unhashable escaped templates retain
buffer flag `284` (`PyBUF_FULL_RO`).

The additional source-only shape model enumerates 1,024 historical substitution
evaluation-order inversions: 256 per substitution API and 256 per behavior
(`stable`, `mutate`, `fail-outer`, `fail-nested`). Its 512 failing cases retain
`BufferError` and never acquire the subject. Thus this correction targets
1,264 identified historical mismatch cases across the two original suites.

Three distinct follow-up categories are deliberately unchanged: 32
substitution cases missing an outer `__len__` probe, 24 `match.expand` cases
missing that probe, and 32 redundant `match.expand` subject reacquisitions.
Historical shape categories can overlap. Accordingly, neither an exact
post-correction remainder nor candidate correctness is claimed:

```
post-correction candidate mismatch count: NOT MEASURED
post-correction shape mismatch count: NOT MEASURED
candidate built: false
candidate imported: false
candidate matching: NOT RUN
candidate qualification: false
runtime non-delegation: NOT ESTABLISHED
```

## Physical source-only boundary and invalidated final holdout

```
final_holdout: INVALIDATED; REKEYED SUCCESSOR REQUIRED
```

The previous proposed final holdout is invalidated and cannot be reused. No
proposal content, proposed hidden cases, final cases, or final evidence is
opened, generated, evaluated, selected, or considered a valid holdout. A newly
rekeyed successor is required before any future final evaluation.

The deny-default audit-hook boundary is installed before the first owner read.
Every approved public plaintext tool, protocol, contract, or publication receipt
is independently pinned by its exact pathname, complete SHA-256, byte count,
device, inode, mode, owner, link count, and no-follow descriptor-relative
identity. Twenty frozen public predecessor owners plus the three current
source/protocol/contract owners are authenticated. The candidate source is not
an approved public owner. Archive and native contents, benchmark/timer files,
private roots, subprocesses, networks, Git metadata, clocks, final holdouts,
proposal contents, and workspace writes are forbidden in both source modes.

Use the pinned CPython 3.14.6 executable with `-I -B -S`. Run both ordinary
gates and repeat both under an empty environment:

```
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_substitution_event_order_v1.py --self-test

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_substitution_event_order_v1.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_substitution_event_order_v1.py --self-test

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_substitution_event_order_v1.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Only the root coordinator may run `--apply`, after committing and pushing this
exact three-file freeze. Root must supply `--root-authorized`, all three
independently frozen SHA-256 values, and identical complete 40-character
`--frozen-commit` and `--pushed-commit` values:

```
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_substitution_event_order_v1.py \
  --apply --root-authorized --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256 \
  --frozen-commit PUSHED_COMMIT --pushed-commit PUSHED_COMMIT
```

The new target directory must not exist. Root apply creates that directory once
with mode `0700`, then creates its sole `py_bridge.c` once with descriptor-
relative `O_CREAT | O_EXCL | O_NOFOLLOW`, mode `0600`, writes the predicted
complete bytes, fsyncs the file and directory, and verifies complete digest-
authenticated readback. It may not overwrite a source, mutate canonical files,
build, run, load, benchmark, open a final holdout, or select a winner.
