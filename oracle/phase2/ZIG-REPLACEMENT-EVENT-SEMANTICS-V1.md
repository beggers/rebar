# First-party Zig replacement events and errors, version 1

Status: SOURCE FREEZE ONLY. The independently written Zig engine and binding
are not built, imported, activated, run, or benchmarked by this experiment.

## Preserve every observed original failure

The complete original Python suite has **31,237** checks in **13** groups.
The previous actual Zig campaign verified **4,607** checks and preserved
**1,700** measured differences. Its **128** interpreter-isolation checks did
not finish, so the complete candidate mismatch count remains **NOT MEASURED**.

Previously frozen, separately authored source corrections model **964** fixed
differences: **620** scanner captures, **312** public Python semantics, and
**32** legacy match-pickling cases. Exactly **736** observed cases remain:

- **64** ordinary replacement cases and **112** shape-changing buffer cases
  return the right answer but release the subject exporter too late.
- **560** malformed shape-changing replacement cases raise the candidate's
  `PatternError` instead of Python's genuine `AttributeError` from calling the
  missing `count` method on the *original* replacement exporter.
- **88** of those malformed cases additionally require an exact original-
  exporter length probe for a dangling final backslash.

The pinned official CPython parser retains the original replacement object in
its tokenizer and uses its actual length for that one dangling-escape error.
Its source is authenticated as reference evidence only; it is never imported,
copied into, or called by the independent production candidate.

## Compose narrowly scoped, independently owned native corrections

Authenticate the original first-party C bridge and independently derive both
previously frozen native corrections entirely in memory. Their exact source
digests are:

```text
scanner: a5ab490d0cfcbba295b68f3f738a1c6371ef3314e9a6c01cdcc0bb5978e3b148
pickle:  b2866780c627035d596eb4190247446efa46e91235152dac1d92fb333d53e915
```

Do not require, open, build, or run their prospective variant files. On top
of the authenticated composed source, add exactly these owned C behaviors:

1. When both subject and literal replacement are custom buffer exporters,
   copy the subject's visible bytes into owned storage before releasing the
   subject. Release it before replacement exporters are acquired by joining.
   Keep the safe snapshot alive throughout the independent Zig match. Apply
   this only to literal custom exporters; escaped replacements, tokenized
   templates, ordinary bytes, memory views, and other passing paths retain
   their current buffer lifetimes.
2. Preserve the actual replacement exporter when a malformed template reaches
   either `Pattern.sub`/`Pattern.subn` or `Match.expand`. Reconstruct the
   candidate's own `PatternError` using that original object. Its ordinary
   Python constructor naturally raises the same missing-`count`
   `AttributeError` as CPython; the answer is neither forged nor hardcoded.
3. Only for the genuine dangling-final-backslash parser message, request the
   original exporter's actual length before reconstruction. This restores the
   exact `length-probe` event and original position. Preserve unrelated errors,
   built-in carriers, missing-group exceptions, and every Python reference.

No Python `re`, `_sre`, CPython matcher, external regex package, other
candidate, fallback, or hardcoded matching answer is used. The independently
written Zig parser, compiler, executor, and engine remain unchanged.

The composed native correction plus the separately frozen public adapter is
modeled to explain all **1,700** previously measured original differences.
This is a source-level prediction, **not a successful candidate run**. The
unfinished interpreter-isolation checks remain **NOT MEASURED**.

## Frozen source-only checks

Use pinned official isolated CPython 3.14.6 with `-I -B -S`. Authenticate this
source, protocol, complete contract, original C bridge, Zig engine, previous
actual Zig receipt, all nine source/protocol/contract owners from the public,
scanner, and match-pickling corrections, both independent frozen replacement
oracles, and the exact read-only official CPython parser source.

Run `--verify-frozen-context` and `--self-test` in the ordinary isolated
environment and the empty environment
`env -i PATH=/usr/bin:/bin LC_ALL=C PYTHONDONTWRITEBYTECODE=1`. Synthetic
PEP-688 exporters verify exact subject-before-replacement release order,
safe snapshot ownership, release-time mutation, original-object error
construction, dangling length probes, exporters that legitimately implement
`count`, unchanged built-in carriers, and unrelated exceptions. Hostile source
controls preserve the scanner, legacy pickle, narrow replacement guard, and
both public error paths. No candidate, native library, native compiler, final
test, compressed archive, timer, or child interpreter is touched.

The prospective destination
`candidates/zig/variants/replacement_event_semantics_v1/py_bridge.c` must
remain absent in every source-only gate. A separately authorized, completely
pinned, root-only `--apply` may exclusively create that single new C source;
canonical candidate files and previous variants are never changed.

Build: **NOT RUN**. Correctness: **NOT RUN**. Runtime non-delegation:
**NOT ESTABLISHED**. Performance and memory: **NOT MEASURED**. Final test:
**NOT OPENED**. Qualifying candidates: zero. Winner: none.
