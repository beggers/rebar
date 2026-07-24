# Preserve the first failed official Python test

Status: **FAIL.** The genuinely frozen version-two official compatibility
run stopped when Rust passed **145 of 146** original CPython tests and
failed ReTests.test_match_repr.

C and Zig official tests are **NOT RUN**. The Python baseline ran before
Rust, but its original per-method records were not retained. No passing
baseline record, C result, Zig result, or complete version-two official
success report is inferred or invented.

## The actual mismatch

The unchanged CPython test constructs its expected display using the
genuine module of the match object's type:

    Expected regular expression:
    <(candidates._rust_bridge\.)?Match object; span=\(1, 12\), match='abracadabra'>

    Actually displayed:
    <re.Match object; span=(1, 12), match='abracadabra'>

    Failed official method:
    ReTests.test_match_repr

    Actual original runner summary:
    146 selected methods; 145 passed; 1 failed
    0 skips; 0 crashes; 0 timeouts

The failure is a faithful semantic transcription of the JSON actually
reported by the first official controller run. Original stdout or
stderr bytes and an original-stream hash are **NOT RECORDED**. The
normalized transcription hash is not a raw-output hash. Recording does
not rerun a test or matching engine.

## Preserve the exact actual proof chain

The frozen failed official source and protocol:

    tools/postfinal_cpython_locale_oracle_v2.py
    e6858d00747645c6f81cad66e2d6ca957c374e88718abc356fc5367b5be100e1

    oracle/cpython-3.14.6/POSTFINAL-LOCALE-V2.md
    a515d2a81d8d02df523316d8315ca3617fe3f4330d33745f536ed15917ff20c5

The actual version-six source and strict independence proofs:

    tools/postfinal_from_scratch_audit_v6.py
    77e7ea97f96280019b3be9abfeeb8fc6ff27ca6ecd13189e611586af5719c18f

    candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V6.json
    0314e3e5de3386d7c9c1e7f8fa4648554ff53cb53e3aafcecc4cb8e4923ddcbb

    tools/postfinal_no_delegation_audit_v6.py
    a936abe91d67169ea361b6770404ffe7bc925fdb3275aef854fbe12fe68a8649

    candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V6.json
    93f174f0861b0ee6e9feadf6e49bf222f0766b393ff74179219e65452b03d84f

The genuinely passing, separately frozen generic-alias results:

    tools/python_re_generic_alias_public_oracle_stage12.py
    361e080a0475f5ee7fd7d5da0386a4e2443775069aadca84e053bac357554aaa

    oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V12.md
    1cec5253aabb5464c16d0de461bdd11463ddf11fafea9da6347b8a0af3d30cb1

    oracle/cpython-3.14.6/evidence/public-generic-alias-v12-self-oracle.json
    b235bd68afbbfa9b8e7e046d0e007385617c976c6e5a5f5b614cc7d93b891aff

    candidates/evidence/python-re-generic-alias-public-oracle-v12-all.json
    6b0188e22f80a64e79252660d6b308d16d7a38ec01c45013bf67484b8d49be8c

The actual source proofs cover all 12 candidate source files and five
native binaries. The generic-alias reference passes 256 observations,
and the three independent candidates pass 384 generic-alias checks.
Neither result substitutes for the failed official compatibility gate.
All 403 upstream corpus cases, 146 selected test methods, eight named
waivers, and immutable official Python sources remain unchanged.

## Safe synthetic checks

The sole failure recorder is
[postfinal_cpython_locale_v2_failure.py](../../tools/postfinal_cpython_locale_v2_failure.py).
Its self-test imports no candidates, opens no files, writes no evidence,
starts no worker, compiles no locale, reads no performance input, and
samples no clock:

    PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
    PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
      tools/postfinal_cpython_locale_v2_failure.py --self-test

The root agent alone may preserve the existing failure after committing
and pushing this source and document:

    PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
      tools/postfinal_cpython_locale_v2_failure.py --record

The one and only permitted, exclusively created output is:

    oracle/cpython-3.14.6/evidence/postfinal-locale-v2-rust-failures.json

The recorder never reruns the failed official command, overwrites an
earlier result, invents baseline or unrun engine records, or changes a
candidate. Current runtime and memory remain **NOT MEASURED**. There is
no qualified winner.
