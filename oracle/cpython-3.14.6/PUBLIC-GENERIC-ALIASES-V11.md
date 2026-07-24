# Python regular-expression generic aliases

Status: **Prospective, additive correctness design.** The independently
started Python references and the three guarded candidate workers are
**NOT RUN**. Performance is **NOT MEASURED**.

Python 3.14.6 publicly supports `re.Pattern[str]`,
`re.Pattern[bytes]`, `re.Match[str]`, and `re.Match[bytes]`. Each
expression produces an actual `types.GenericAlias`, not a substitute
object. The 146 selected official regular-expression tests, the
external 403-case corpus, and the frozen 3,584-obligation stage-ten
suite do not directly exercise this documented runtime behavior.
This additive oracle closes that specific public-compatibility gap.
It does not alter, replace, or rerun those frozen suites.

## Freeze all 128 obligations before running an implementation

The domain is `rebar/python-re/public-generic-alias/v11`; its exact
seed is `2026072461`. The complete source-bound, canonical-ASCII
128-obligation matrix is frozen at
`7e5adbf2ca9c0f752a0c9dddaabe812a780cf58ca9b60efc178bafbaceee7e65`.
The origin order is `Pattern`, `Match`; normal type arguments are
`str`, `bytes`.
Loop order and all case identities are defined by the accompanying
source, not by randomized iteration or a runtime sample.

| Public behavior | Complete case construction | Cases |
| --- | --- | ---: |
| Ordinary aliases | 2 origins × 2 arguments × 10 observations | 40 |
| Less usual legal or rejected arguments | 2 origins × 8 arguments × 3 observations | 48 |
| Real `isinstance` and `issubclass` rejection | 2 origins × 2 arguments × 4 operations | 16 |
| Copying and serialization | 2 origins × 2 arguments × 6 operations | 24 |
| **Every required public observation** | | **128** |

The ten ordinary observations are actual `types.GenericAlias` type,
exact `__origin__`, exact `__args__`, exact `__parameters__`, actual
`typing.get_origin`, actual `typing.get_args`, public representation,
repeated-alias equality, unequal-origin or unequal-argument equality,
and the requirement that equal aliases have equal hashes. No
process-randomized raw hash is compared.

The eight diverse operands are `int`, `None`, `Ellipsis`, the empty
tuple, `(str, bytes)`, a real named `typing.TypeVar`, `list[str]`,
and `object`. Each origin observes actual construction, exact
arguments, and exact parameters and typing behavior. The frozen
standard-Python workers establish which operations return, raise, or
warn; the controller never guesses acceptable exceptions or suppresses
warnings.

For each normal alias the four rejection operations are
`isinstance(real_instance, alias)`, `isinstance(object(), alias)`,
`issubclass(real_origin, alias)`, and `issubclass(object, alias)`.
The real pattern and match instances come from the same independently
guarded candidate or standard-library module being evaluated.

The six lifecycle operations are `copy.copy`, `copy.deepcopy`, and an
actual `pickle.dumps`/`pickle.loads` round trip at protocols 0, 2, 4,
and the interpreter's genuine `pickle.HIGHEST_PROTOCOL`. Reports
compare the restored alias type, actual origin and arguments,
representation, equality, and the equal-hash relation; they never
compare pickle implementation bytes or randomized hashes. A public
representation is normalized only when its origin is exactly that
worker's actual `Pattern` or `Match` class. Every worker separately
records and verifies each real, unmodified origin module, public name,
qualified name, role, and native ownership. A false or foreign origin
cannot be normalized into `re.Pattern` or `re.Match`.

## Preserve all existing correctness and independence proof

Each real stage-eleven action first authenticates all four actual,
previously passing stage-ten artifacts:

```text
tools/python_re_universal_public_oracle_stage10.py
a24cfa72f44931c76b425ea3eb6568ff67dc87236c8d5fe930837a14c2f58f08

oracle/cpython-3.14.6/PUBLIC-CONTRACT-V10.md
c0194ee2ef1e32bd64dc646e2f395bee6036b9c053e31d95ebb3cfbc52b0a543

oracle/cpython-3.14.6/evidence/public-contract-v10-self-oracle.json
5207ca3829216b9482f0b5a2928b339261e2c51d673cce7d80da0f4f4622a8f9

candidates/evidence/python-re-universal-public-oracle-v10-all.json
0af512f940ce7c28e50c1977794e3fbb8a2c33206e77dd2379d4fa12b391fec7
```

The standard-library reference consists of two newly started,
isolated pinned-CPython processes. Neither may import a candidate.
Only actual complete agreement between all 128 records authorizes an
exclusively created passing Python-reference report.

The candidate action is not authorized until that exact passing
reference exists. It starts the current from-scratch Rust, C virtual
machine, and Zig families in three distinct, newly started isolated
processes. It inherits the exact stage-ten source and native-binary
fingerprints and the existing independently audited guard. The guard
blocks Python's `re`, `_sre`, all third-party regex packages, the two
other candidate families, cached aliases, and all five unowned native
loader entry points. `inspect`, `tokenize`, benchmark detection,
fallbacks, and candidate-to-candidate delegation are not permitted.

Any actual reference mismatch, worker crash, missing observation,
unexpected warning, serialization failure, guard failure, or candidate
mismatch is written to its exact failure path with `O_EXCL`; no prior
evidence or failed experiment can be overwritten or silently skipped.

```text
oracle/cpython-3.14.6/evidence/public-generic-alias-v11-self-oracle.json
oracle/cpython-3.14.6/evidence/public-generic-alias-v11-self-oracle-failures.json
candidates/evidence/python-re-generic-alias-public-oracle-v11-all.json
candidates/evidence/python-re-generic-alias-public-oracle-v11-rust-failures.json
candidates/evidence/python-re-generic-alias-public-oracle-v11-vm-failures.json
candidates/evidence/python-re-generic-alias-public-oracle-v11-zig-failures.json
```

Run only the candidate-free, entirely in-memory synthetic controls
before committing and pushing the source and this protocol:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_generic_alias_public_oracle_stage11.py --self-test
```

Only after that commit has been pushed may the root controller run the
two real Python workers and push their evidence. Only after that
passing evidence has been pushed may it run all three candidates:

```sh
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_generic_alias_public_oracle_stage11.py --self-oracle

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_generic_alias_public_oracle_stage11.py --candidate all
```

Neither action opens a performance fixture, a hidden test, a final
holdout, historical timings, or a benchmark. Speed, memory,
confidence intervals, rankings, and a winner remain **NOT MEASURED**.
