# Broad Python regex compatibility after the official failure fix

Status: **Prospective.** The source-only safeguards do not start a reference,
run a candidate, write results, or take a measurement. The new generic-alias
stage must pass before any real stage-fifteen process may start.

The pinned baseline is unmodified CPython 3.14.6. Each candidate is a
genuinely separate, from-scratch Rust, C, or Zig matching implementation.
Neither an old successful report nor an old candidate binary qualifies a
repaired implementation.

## Freeze all 3,584 real public obligations

Retain every original Python case, identifier, operation, input, scanner,
callback, warning, locale, Unicode edge, signature, buffer, and thread
group. Refresh only the deterministic cohort seed. The stage-fifteen seed is
`2026072479`, its domain is `rebar/python-re/public-contract/v15`, and the
full case matrix has SHA-256
`3e643ab0c455bc789e4939af2dba73af18abb033f2f34f003b49b1299b35eeeb`.

| Real Python behavior | Cases |
| --- | ---: |
| Exported functions, signatures, flags, and exceptions | 256 |
| Invalid patterns, warnings, and flag combinations | 256 |
| All bytes, both genuine locales, and changed active locales | 1,024 |
| Bytes, memory views, noncontiguous buffers, and released views | 256 |
| Patterns, matches, groups, copying, and weak references | 256 |
| Replacement callbacks, nested matching, and scanners | 256 |
| Real four- and eight-thread shared-pattern groups | 256 |
| Position limits, long inputs, Unicode, and lone surrogates | 1,024 |
| **Actual comparisons for each candidate** | **3,584** |

Collect genuine Python callable signatures only inside a separately guarded
metadata process. Never put the inspector, tokenizer, a cached Python
matcher, a metadata matcher capability, a foreign candidate, or a dynamic
library loader in a production matching process. Authenticate every real
signature against the correct candidate's actual native engine.

## Authenticate only genuinely current repaired engines

Require the independently completed source and no-delegation audits:

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

Independently rehash all 12 actual engine source files and all five mapped
native libraries. Require both audits to agree on every source, library,
family, dependency, real match representation, and all 48 genuine standard
pickle round trips. Keep the actual prior failed Rust official-test report;
never report unexecuted C or Zig tests as having passed.

Require the genuine, newly completed official test against Python and every
current candidate:

```text
tools/postfinal_cpython_locale_oracle_v3.py
28b98c8913ca89ec2ba600484205c3bcb63ae22a86e33d4f7cf3c6f1a68c8a58

oracle/cpython-3.14.6/POSTFINAL-LOCALE-V3.md
a1f77b1628c03d42b9d8e2650c9b501d9be4cec917d765539c91c750154bd6ac

oracle/cpython-3.14.6/evidence/postfinal-locale-v3-all.json
18a011a5ce6e47e52cd02e4cb0812c8f9f7919a069edd7d74e57631623b901b5
```

Verify all **146** original official test-method records separately for each
of the **four** real roles. Keep the upstream **403**-case corpus, all
**eight** named original exclusions, both real locales, all **six** actual
native match-display reproductions, and all **48** real pickle observations.

Require the new independently completed 128-case stage-fourteen public
generic-alias reference and all-candidate reports. Source, protocol,
two-reference evidence, and three-candidate evidence must each have an
actual published SHA-256. Until all four exist, every real stage-fifteen
command **fails closed without starting a worker**. Never infer current
correctness from the obsolete stage-twelve generic-alias evidence.

The corrected, genuinely published source, protocol, two-worker Python
reference, and independently completed three-family result are:

```text
tools/python_re_generic_alias_public_oracle_stage14.py
5caba6e5d92935a1877fb34bd3c1e266d07c67385f847477041312959104ec58

oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V14.md
b20b5b3876fba06cdf41b9a99825157d0ca6ba84b8bc7abfd71b49e44fdd7505

oracle/cpython-3.14.6/evidence/public-generic-alias-v14-self-oracle.json
7da9c6aa5fa1db4ef0dea593d8f9d501ecc952aa62ed7bf5a0f17d0b726b04bf

candidates/evidence/python-re-generic-alias-public-oracle-v14-all.json
f9243bd27a4d4ae24c0c3f0b24785e381440fc19c8911b52719cc6813bc1e8cc
```

Preserve both actual 128-row generic-alias Python arrays, both complete
isolated reference-worker reports, and all 384 actual native observations.
Require the independent stage-fourteen source validators and independently
recheck the full reference, candidates, identities, class origins, native
fingerprints, guards, and complete answer arrays.

## Preserve every real answer and every real failure

Retain **both** full Python reference arrays, not just their digests. Retain
both actual isolated Python worker reports and authenticate every worker's
own complete answer array.
Retain
all **3,584** actual returned observations from **each** of the three
candidate processes. Validate every case identity, warning, exception,
normalized answer, metadata receipt, native fingerprint, and actual
reference equivalence before writing a success. The three-candidate evidence
therefore contains **10,752** real candidate records and **7,168** real
reference records.

Only these six new one-use, no-follow evidence paths are authorized:

```text
oracle/cpython-3.14.6/evidence/public-contract-v15-self-oracle.json
oracle/cpython-3.14.6/evidence/public-contract-v15-self-oracle-failures.json
candidates/evidence/python-re-universal-public-oracle-v15-all.json
candidates/evidence/python-re-universal-public-oracle-v15-rust-failures.json
candidates/evidence/python-re-universal-public-oracle-v15-vm-failures.json
candidates/evidence/python-re-universal-public-oracle-v15-zig-failures.json
```

First run the completely candidate-free synthetic checks:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage15.py --self-test
```

Commit and push the exact source and this protocol before the root
controller starts two real references. Commit and push the complete
passing reference before running any candidate:

```sh
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage15.py --self-oracle

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage15.py --candidate all
```

This experiment does not access performance cases or a final test. Speed,
memory, rankings, and a winner remain **NOT MEASURED**.

The unchanged 3,584-case matrix does not, by itself, prove exact complete
`__all__`, cache identity and eviction, every scanner and replacement edge,
all public method combinations, or concurrent cache clearing. Freeze and
run a separate, additive full-surface experiment before claiming that any
Python `re` user can safely switch. Do not silently add cases to this matrix.
