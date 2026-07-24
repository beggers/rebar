# Independently guarded Python regex compatibility

Status: **FROZEN SOURCE; REFERENCE NOT RUN; CANDIDATES NOT RUN.**
Speed, memory, benchmark and holdout performance, and a winner
are **NOT MEASURED**.

This additive correctness protocol asks whether three genuinely
independent engines actually reproduce Python's complete public regex
behavior while their native no-delegation guard is live in the exact
same Python process. A source-only test, a compressed original
archive, another process's guard, or a printed summary is not a
candidate pass.

## Preserve the exact frozen Python behavior

Use the unchanged, independently reviewed public contract:

```text
tools/python_re_public_surface_oracle_stage17.py
cc36700fd5e43ed409472423a74b7da686804b09c92511d90bec863026c25bf8

oracle/cpython-3.14.6/PUBLIC-SURFACE-V17.md
a703805d1cc711488f84bf4d5a4596de8ef194fd47a2116162ec6a490a3da0e5
```

Preserve every one of the real **1,376 distinct behavioral inputs**,
**43** cohorts, **32** distinct variants per cohort, **640**
source-local base cases, and **736** independently seeded extended
cases. The genuine full case matrix is:

```text
7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa
```

The actual full behavioral-stimulus fingerprint is:

```text
8c1a4fd434af5fb1ea0dcd1aa3faaa06b07e7d186ca52c1593575eff93b4d7da
```

Never modify the V17 source, remove a case, reuse an expression or
subject, change warning locations, weaken flags, skip buffers, avoid
ordinary pattern or generic pickle, replace true callback traces, or
fake an ISO-8859-1 locale. Preserve all 31 real ordered exports, all
13 public pattern members, and all 14 public match members.

Authenticate the actual complete upstream two-reference Python 3.14.6
V5 reference,
`3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916`,
using the complete immutable original V17 baseline validator. Retain
all 152 original public test identities, 151 applicable passes, the
sole genuine private-debug conditional skip, the original 403-case
corpus, all 11 real external fixture checks, genuine 26-file support,
real two-gibibyte tests, and original CPU and fork records.

Before any candidate audit or native implementation is opened, run
two actual, separately started, pinned `python3.14 -I -B`
standard-library workers against all **1,376** unchanged public
cases. Both workers must independently pass all **736** additive
probes and all **64** actual fresh-locale cases, with **192** genuine
ISO-8859-1 → UTF-8 → ISO-8859-1 transitions, measured same-pattern
identity, and full restoration. Preserve both entire streams and
independently authenticate their real source, protocol, each original
row and error, and matching canonical record digest.

The Python baseline cannot depend on an owner audit, candidate,
candidate proof, prior campaign, or guessed report hash. Until the
real V18 reference report exists, candidate execution is **BLOCKED**.

## Require complete current native ownership

Use only the actual, exact frozen owner sources:

```text
tools/postfinal_from_scratch_audit_v10.py
0c4d3f07bb51b0ce5ddc148810cb157d21067ddb07b578d3a793aaac5c671505

tools/postfinal_no_delegation_audit_v10.py
885168bd6df92ac9cabc8fc78a8389ee487f0be8d3c7fe67a393e984011b8d95

candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V10.md
902bc095d08331089dcc1d1d11233747438a0cacb0cf1057ae41a2474bde2fa6

tools/postfinal_current_build_proofs_v11.py
2895dd28b3dc69985cc0f6f8575398e8b8b10f58141f0612645a687478da9f04

oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V11.md
334405521f2f945cc58cabf246cf8f784e8a6a5be7091a20587b0daf428412af
```

Supply both actual complete all-family V10 report hashes explicitly.
Validate both complete reports with the original strict
`validate_base_report` and actual V11 `audit_v11_reports`. Require
all **three** genuine owner workers, **12** independently owned
source files, **five** native binary roles, all 13 Python matcher
guards, all five dynamic-loader guards, all ordinary pickle results,
and the exact real current-family source and native snapshots.

For **each** of Rust, C, and Zig, separately supply **four** actual
externally observed V11 hashes: the qualified original edge archive,
its complete durable owner proof, the qualified original deep
archive, and its complete durable owner proof. The only accepted
artifact shapes are:

```text
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v11-qualified-pass.json.gz
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v11-qualified-pass-proof.json

candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V11-PASS.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V11-PASS-PROOF.json
```

Bound and independently hash every actual regular, no-symlink file.
Use the original frozen full edge and deep validators, not a gzip
header. The edge must actually preserve all **223,198** cases and
**49** categories. The deep archive must preserve all **393** public
checks. For both archives reconstruct the original complete producer
streams, actual return code, the exact current family source/native
snapshot, and complete actual V10 native owner observations before
and after. Validate the complete original canonical durable document
using the genuine unchanged V11 `validate_durable_wrapper`. Deep
proofs must also bind that same family's actual qualified edge
archive and its durable owner proof.

Never accept the old raw-only V10 Rust success, a diagnostic, an
archive without its durable owner proof, another family's report,
guessed report hashes, stdout as proof, or a substituted native
binary. Authenticate all **12** artifacts before any candidate is
imported.

## Match inside the same genuine guarded process

A separate native ownership check before or after public matching is
not sufficient. Reuse the exact actual immutable
`owner.NATIVE_OWNER_WORKER` and its exact original hash. Preload the
frozen V17 and V18 evaluators before the worker poisons every cached
standard-library matcher. Insert the real public observation exactly
once, **after** the genuine guarded candidate is imported and
**before** the same worker performs its real unchanged post-matching
matcher, native-loader, external-engine, cross-family, and cached
`re._compiler`/`re._parser` checks.

Obtain the sole candidate using the existing guarded entry in
`sys.modules`; do not import it a second time. Preserve the original
complete V10 owner schema and all real sentinel, cached-alias,
13-matcher, five-loader, native mapping, standard pickle, and
before/after records. Add the full **1,376** actual public results to
that same original owner record. Independently validate both the
augmented and unaugmented real owner with the original exact V10
validator, compare every result with both genuine Python references,
and confirm the current native snapshot.

In addition to the same-process matching guard, start and validate a
fresh isolated complete V10 native owner immediately before and
immediately after each candidate worker. Preserve both complete
actual records. Any real cross-family import, standard-library
delegate, foreign regex engine, loader escape, error, timeout,
failure, swapped native binary, or missing locale is **FAIL**.

Use only distinct, exact V18 passing/failure destinations. Preflight
all destinations; create reports only with `O_EXCL` and `O_NOFOLLOW`,
complete bounded canonical JSON, file `fsync`, and directory `fsync`.
Preserve all genuine completed records, failure streams, return code,
and active public case. Never overwrite, replace, fabricate, or
release a report.

## Source-only verification

Run these controls only:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/python_re_public_surface_oracle_stage18.py --self-test
env -i PATH=/usr/bin:/bin /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/python_re_public_surface_oracle_stage18.py --self-test
```

Before its measurement boundary, the control explicitly authenticates
the **two declared immutable V17 source and protocol files** and
executes all genuine inherited V17 source-only controls. Within the
reversible measurement boundary it runs at least **250** separately
named source-only poison checks. It never reads candidate sources,
reports, original archives, durable proofs, evidence, benchmarks, or
holdouts. It performs no regular-expression match, candidate import,
reference worker, native worker, clock sample, entropy draw, thread,
locale change, or file write.

Reference: **NOT RUN**. Candidate: **NOT RUN**. Separate interpreter:
**NOT RUN**. Speed and memory: **NOT MEASURED**.
