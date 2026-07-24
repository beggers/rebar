# Regular-expression generic aliases after the real pickle failure

Status: **Prospective, additive correctness design.** Both rebuilt-engine
source and no-delegation audits have actually **PASSED**. The two new
independent Python reference workers and all three version-twelve
candidate workers are **NOT RUN**. Speed and memory are
**NOT MEASURED**.

Python 3.14.6 must support real `types.GenericAlias` objects for
`Pattern[str]`, `Pattern[bytes]`, `Match[str]`, and `Match[bytes]`.
Ordinary Python copying and `pickle.dumps`/`pickle.loads` must work.
The previous version actually disproved Rust compatibility: **16 of
128** observations failed, exactly the four pickle protocols for both
public classes and both input types. That failure is preserved rather
than repaired, removed, or attributed to the safety guard:

```text
candidates/evidence/python-re-generic-alias-public-oracle-v11-rust-failures.json
5d0fce04b95a6d15e4aaff28d2c59337136660a248616672928f7aa85f7efa36
```

The root cause is a genuine candidate class claiming to belong to
standard Python's `re` module. Standard pickle resolves the declared
module and checks exact object identity. A distinct class cannot be
pickled as `re.Pattern` or `re.Match`. Version twelve requires each
rebuilt candidate to use its genuinely importable, native-owned class.
It does not install a fake `re` module, relax the matching guard,
override pickle, register a global reducer, change standard-library
answers, or accept a missing or stale native binary.

## Freeze the same complete public contract

Seed: `2026072471`. Independent domain:
`rebar/python-re/public-generic-alias/v12`. The exact source-bound
canonical matrix is
`65c93cfbbc337ecd762a6b201bacc77e35eb72d201a9e8bc222d730714885aef`.
The complete **128** obligations retain the previous order and
semantics; only their independently bound cohort seeds change.

| Public behavior | Complete obligation construction | Cases |
| --- | --- | ---: |
| Real generic alias, origin, arguments, typing, representation, and hash relations | 2 origins × 2 arguments × 10 observations | 40 |
| Real diverse arguments, exact construction, parameters, and warnings | 2 origins × 8 arguments × 3 observations | 48 |
| Real `isinstance` and `issubclass` rejection | 2 origins × 2 arguments × 4 observations | 16 |
| Real copying and standard pickle protocols | 2 origins × 2 arguments × 6 observations | 24 |
| **Complete standard Python compatibility** | | **128** |

All eight unusual type arguments, a genuine `typing.TypeVar`, both
public origins, both `str` and `bytes`, captured warnings and real
exception details remain unchanged. The lifecycle retains true shallow
and deep copies and unchanged ordinary `pickle.dumps`/`pickle.loads`
at protocols 0, 2, 4, and `pickle.HIGHEST_PROTOCOL`. Normalization is
allowed only for the exact already authenticated public class from
that worker. Its actual module, qualified name, native owner, and
object identity remain independently visible and strictly verified.

## Authenticate the rebuilt engines, not the failed ones

The previous exact source, protocol, passing two-Python baseline, and
failed Rust evidence are independently verified:

```text
tools/python_re_generic_alias_public_oracle_stage11.py
2d8b0417e837d830c3b01495657305536a9d14e289aeb61d503278f5944b16f3

oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V11.md
b9d93b2ee18d33ad3e474c7e7d9bf7f94cd612526e39982fec0c2a0d0a4d096e

oracle/cpython-3.14.6/evidence/public-generic-alias-v11-self-oracle.json
31245bf7864ae76e46e676a3a35d0fae399d1f6446af482db9f7aa47b5426f8a

candidates/evidence/python-re-generic-alias-public-oracle-v11-rust-failures.json
5d0fce04b95a6d15e4aaff28d2c59337136660a248616672928f7aa85f7efa36
```

The previous V5 source and no-delegation audits are **historical**;
their fingerprints cannot certify modified candidate sources or newly
built native libraries. Both new V6 audits have actually **PASSED**.
Their genuine producers and exclusive reports are pinned separately;
together they authenticate every one of the **12** current candidate
source files and **five** current native binaries:

```text
tools/postfinal_from_scratch_audit_v6.py
77e7ea97f96280019b3be9abfeeb8fc6ff27ca6ecd13189e611586af5719c18f

candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V6.json
0314e3e5de3386d7c9c1e7f8fa4648554ff53cb53e3aafcecc4cb8e4923ddcbb

tools/postfinal_no_delegation_audit_v6.py
a936abe91d67169ea361b6770404ffe7bc925fdb3275aef854fbe12fe68a8649

candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V6.json
93f174f0861b0ee6e9feadf6e49bf222f0766b393ff74179219e65452b03d84f
```

Every V6 report schema, audit producer, current source fingerprint,
owned native path, native hash, and cross-audit relationship is
independently verified. A missing, guessed, historical, partial, or
synthetic audit fails closed and cannot start a worker. All three
rebuilt families retain independently owned parser/compiler/execution
pipelines, deny Python's `re` and `_sre`, deny external engines and
other families, and block the same five unowned native-loader entry
points. Do not open final or historical performance data.

## One-time evidence and execution order

```text
oracle/cpython-3.14.6/evidence/public-generic-alias-v12-self-oracle.json
oracle/cpython-3.14.6/evidence/public-generic-alias-v12-self-oracle-failures.json
candidates/evidence/python-re-generic-alias-public-oracle-v12-all.json
candidates/evidence/python-re-generic-alias-public-oracle-v12-rust-failures.json
candidates/evidence/python-re-generic-alias-public-oracle-v12-vm-failures.json
candidates/evidence/python-re-generic-alias-public-oracle-v12-zig-failures.json
```

Every success and failure uses its approved exact destination and
exclusive `O_EXCL` creation. The candidate-free synthetic test must
execute no workers, import no candidate, inspect no production
matcher, open or write no file, and read no clock:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_generic_alias_public_oracle_stage12.py --self-test
```

Commit and push both passing V6 reports and the complete
version-twelve source and protocol. Only then run and push two newly
started, isolated standard-Python references:

```sh
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_generic_alias_public_oracle_stage12.py --self-oracle
```

Only the exact genuinely passing and pushed two-Python evidence may
authorize the three independent guarded rebuilt candidates:

```sh
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_generic_alias_public_oracle_stage12.py --candidate all
```

No benchmark, hidden case, final test, timing, memory measurement,
speedup, or winner is produced by any correctness command.
