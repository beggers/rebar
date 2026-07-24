# Fresh compatibility check for Python regular-expression types

Status: **Prospective, frozen correctness experiment.** Both independently
produced fresh version-seven source and no-delegation audits have actually
**PASSED**, and all four real producer and report fingerprints are pinned.
The previous 16-case failure, the later 256 standard-Python checks and 384
passing candidate checks, and the real upstream match-display failure remain
historical facts. The newly repaired engines have now actually **PASSED all
584 original upstream checks**: Python, Rust, C, and Zig each independently
passed all 146 selected methods. Version-fourteen Python reference: **NOT RUN**.
Version-fourteen Rust, C virtual machine, and Zig candidates: **NOT RUN**.
Speed, memory, and the hidden performance cases: **NOT MEASURED**.

Python's standard regular-expression library exposes real generic types such
as `re.Pattern[str]`, `re.Pattern[bytes]`, `re.Match[str]`, and
`re.Match[bytes]`. A replacement cannot just return approximately similar
objects. Their public identity, arguments, ordinary Python copying, typing,
warnings, exceptions, and unmodified standard pickle must actually agree with
Python 3.14.6. In particular, its public classes must genuinely belong to
its own importable native engine; claiming that a different class belongs to
`re` breaks ordinary pickle and can forge the displayed owner of a match.

## Freeze all 128 public behaviors

Seed: `2026072481`. Independent seed domain:
`rebar/python-re/public-generic-alias/v14`. The exact canonical matrix is
`3d57a2eae1e880df934043856cf6d5ed32944908b7642611a3f060406453f1ab`.
Every old public case and its order remain intact; only their independently
generated, version-fourteen cohort seeds change.

| Actual standard-Python behavior | Complete construction | Cases |
| --- | --- | ---: |
| Generic type, true origin, arguments, typing, displayed form, equality, and hash | 2 public classes × 2 input types × 10 checks | 40 |
| Unusual type arguments, parameters, and warnings | 2 public classes × 8 arguments × 3 checks | 48 |
| Correct `isinstance` and `issubclass` rejection | 2 public classes × 2 input types × 4 checks | 16 |
| Real copying and unmodified ordinary pickle | 2 public classes × 2 input types × 6 checks | 24 |
| **Complete unchanged public contract** | | **128** |

The four ordinary pickle protocols are 0, 2, 4, and Python's actual highest
protocol. The remaining two lifecycle cases use real shallow and deep copy.
The unusual arguments include `None`, `Ellipsis`, an empty tuple, multiple
type arguments, a real typing type variable, nested generic types, `int`,
and `object`. Standard `pickle.dumps` and `pickle.loads` are not overridden;
no fake `re` module, custom pickle reducer, altered answer, or fallback is
permitted.

## Keep actual previous results unchanged

Version eleven actually found **16 Rust failures out of 128**. Rust ran; the
C and Zig workers did not. The exact original Python reference and failure
are preserved and authenticated:

```text
oracle/cpython-3.14.6/evidence/public-generic-alias-v11-self-oracle.json
31245bf7864ae76e46e676a3a35d0fae399d1f6446af482db9f7aa47b5426f8a

candidates/evidence/python-re-generic-alias-public-oracle-v11-rust-failures.json
5d0fce04b95a6d15e4aaff28d2c59337136660a248616672928f7aa85f7efa36
```

Version twelve actually passed **256 independently produced Python reference
checks** and **384 checks across all three then-current candidates**. These
are genuine historical results, not proofs for subsequently repaired native
source files:

```text
tools/python_re_generic_alias_public_oracle_stage12.py
361e080a0475f5ee7fd7d5da0386a4e2443775069aadca84e053bac357554aaa

oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V12.md
1cec5253aabb5464c16d0de461bdd11463ddf11fafea9da6347b8a0af3d30cb1

oracle/cpython-3.14.6/evidence/public-generic-alias-v12-self-oracle.json
b235bd68afbbfa9b8e7e046d0e007385617c976c6e5a5f5b614cc7d93b891aff

candidates/evidence/python-re-generic-alias-public-oracle-v12-all.json
6b0188e22f80a64e79252660d6b308d16d7a38ec01c45013bf67484b8d49be8c
```

The subsequently attempted genuine upstream Python suite actually stopped
because Rust failed `ReTests.test_match_repr`: **145 of 146 passed; one
failed**. Python's baseline was executed but its individual results were
**NOT RECORDED**. C and Zig were **NOT RUN**. No passing baseline, C run,
Zig run, complete upstream report, or rerun may be invented:

```text
tools/postfinal_cpython_locale_oracle_v2.py
e6858d00747645c6f81cad66e2d6ca957c374e88718abc356fc5367b5be100e1

oracle/cpython-3.14.6/POSTFINAL-LOCALE-V2.md
a515d2a81d8d02df523316d8315ca3617fe3f4330d33745f536ed15917ff20c5

tools/postfinal_cpython_locale_v2_failure.py
42069714991730daff44351eb76ef2fe44478720eb0c51d76b9ea162600b96a5

oracle/cpython-3.14.6/POSTFINAL-LOCALE-V2-FAILURE.md
75e9a2709c7755de96ae23106db536a38bfd97a80fb37c5ea3f6a98139e26818

oracle/cpython-3.14.6/evidence/postfinal-locale-v2-rust-failures.json
a77f47cbfb992aa9ae3ced5394bffb75575e6f305f0d2bd0fe2677092517654f
```

The fresh version-three upstream suite then actually ran after the native
engines were independently repaired and audited. Python's unchanged
reference and each from-scratch Rust, C, and Zig engine separately passed
**146 of 146 original official methods: 584 of 584**, with no failures,
skips, crashes, substituted tests, or extra waivers. All four complete
per-method observation arrays, both genuine isolated locale checks, the
403-case upstream corpus, the same eight named exclusions, the actual
version-seven native fingerprints, and the preserved version-two failure
are authenticated by the real frozen artifacts:

```text
tools/postfinal_cpython_locale_oracle_v3.py
28b98c8913ca89ec2ba600484205c3bcb63ae22a86e33d4f7cf3c6f1a68c8a58

oracle/cpython-3.14.6/POSTFINAL-LOCALE-V3.md
a1f77b1628c03d42b9d8e2650c9b501d9be4cec917d765539c91c750154bd6ac

oracle/cpython-3.14.6/evidence/postfinal-locale-v3-all.json
18a011a5ce6e47e52cd02e4cb0812c8f9f7919a069edd7d74e57631623b901b5
```

This genuinely passing later suite does not rewrite or rerun the prior
failure. Nor does it count as the new, separately frozen 128-case
generic-alias reference or the new 384 candidate observations; those remain
**NOT RUN** until their root-authorized commands actually execute.

## Authorize only real, freshly audited native engines

Both genuine version-seven producers and their separately created, actually
passing reports are pinned:

```text
tools/postfinal_from_scratch_audit_v7.py
defa306e47a0d325af7d4c7fabb54324f6cb6d4653a494c46846838f5e2cf487

candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json
efae1f94fb06a1eabbab352794410c4d8e20a78202dcbf769b08ff9c7cee130a

tools/postfinal_no_delegation_audit_v7.py
9283457064f32658747b449c4ee6ebd20ca7cc7dc442ce03ece6b02896cff4e4

candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json
1f71caac01bffdffbf7ffdc2e21a9aa8d6936c452051cbdaa4c90ac67010fd34
```

A missing, stale, guessed, historical, or synthetic fingerprint **cannot
authorize any worker**. Each producer must match the fingerprint recorded in
its own independently produced report; the strict report must in turn name
the exact passing from-scratch producer and report.

Both actual reports must agree on all **12 owned source files**, all **five
owned native binary paths and fingerprints**, **48 ordinary standard-pickle
round trips**, and all **six genuinely matched string and bytes
representations**. They must prove three separate Rust, C virtual-machine,
and Zig matching engines; deny standard-library matching, CPython `_sre`,
external regex packages, other candidates, and all five foreign native-loader
entry points. The preserved upstream failure must stay a failure, and version
twelve must remain historical. No previously passing audit may certify a
subsequently modified engine.

## Exact execution order and complete evidence

First run the candidate-free, clock-free, file-free, process-free synthetic
controls against the genuinely passing and pinned version-seven audits:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_generic_alias_public_oracle_stage14.py --self-test
```

Commit and push the complete design and both actual version-seven reports
before starting fresh standard-Python reference workers:

```sh
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_generic_alias_public_oracle_stage14.py --self-oracle
```

Each of the two independently started Python workers must actually return
all 128 ordered public observations. The exclusive reference must retain
**both actual 128-row arrays**, both separate content fingerprints, and
both complete, source-bound worker reports. A second fingerprint without
its actual second observation array is not a passing reference. The two
complete observations must agree on every case; omitted, duplicated,
changed, reordered, or substituted observations fail closed.

Commit and push that actually complete **256-check** two-Python reference
before starting all three independently guarded candidates:

```sh
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_generic_alias_public_oracle_stage14.py --candidate all
```

Unlike the historical summary, new successful candidate evidence must embed
**both complete 128-row Python reference observations (256 actual reference
records) and all 384 complete candidate observations**. The first and second
references retain separate fingerprints and the exact exclusive self-report
fingerprint. Each candidate retains all 128 actually observed rows, in the
original frozen order. No digest, copied counter, or first reference may
stand in for the second independent execution. Any crash, mismatch, or
incomplete execution retains the actually completed reference workers and
candidate observations. Only these six exact destinations are writable;
every report is created once using `O_EXCL`:

```text
oracle/cpython-3.14.6/evidence/public-generic-alias-v14-self-oracle.json
oracle/cpython-3.14.6/evidence/public-generic-alias-v14-self-oracle-failures.json
candidates/evidence/python-re-generic-alias-public-oracle-v14-all.json
candidates/evidence/python-re-generic-alias-public-oracle-v14-rust-failures.json
candidates/evidence/python-re-generic-alias-public-oracle-v14-vm-failures.json
candidates/evidence/python-re-generic-alias-public-oracle-v14-zig-failures.json
```

No command in this correctness protocol runs a benchmark, opens hidden
performance cases, samples time, measures memory, reports a speedup,
chooses a winner, or releases software. Performance remains **NOT MEASURED**.
