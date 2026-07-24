# Run every original Python regex test without borrowing a regex engine

Status: **PROSPECTIVE. VERSION-SIX REFERENCES AND CANDIDATES NOT RUN.**
Speed, memory use, holdout results, and a winner are **NOT MEASURED**.
A candidate-free source self-test is not a reference or candidate test run.

## Keep the complete real Python baseline

Keep CPython 3.14.6, its exact original `Lib/test/test_re.py`, all **152**
original public methods in source order, and all **13** separately accounted
private methods. The frozen public-method matrix is
`5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a`.
Do not replace an original method, rewrite original source, provide a public
waiver, or recreate an upstream fixture.

The already independently executed genuine two-reference baseline is
`oracle/cpython-3.14.6/evidence/postfinal-locale-v5-self-oracle.json`,
SHA-256
`3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916`.
Authenticate its full original canonical bytes and use the exact frozen V5
reference validator. Both actual isolated CPython roles must retain exactly
**151** real passes and exactly one `requires debug build` skip for
`ReTests.test_memory_leaks`, classified as
`named-private-debug-condition`. Debug-build coverage is **NOT RUN**; no
public obligation is waived.

V6 may also publish its own separate self-oracle by actually running the
same full upstream suite in **two new, isolated, independent** standard
library processes. Those processes require only the independently published
V6 source and this V6 protocol, plus the inherited exact V5/V4 authentic
original-upstream source graph. They never import or authenticate V10/V11
candidate audit or proof sources, old campaigns, benchmarks, or holdouts.
A source-only
test, copied V5 summary, or in-memory result never stands in for either real
V6 reference process.

Every actual role retains the exact upstream support tree of **26** files,
all **403** original corpus cases, all **11** external fixture assertions,
the two genuinely delivered at-least-**2 GiB** original methods, the real
**40 GiB** resource configuration, CPU assertion, genuine forked-process
regression, and freshly generated private ISO-8859-1 and UTF-8 locales.
Insufficient memory or unavailable real locale support blocks the run; it
never changes a test or denominator.

## Authenticate a real, independently implemented candidate first

Freeze and retain these exact audited sources:

```text
tools/postfinal_cpython_locale_oracle_v5.py
9a4f2ac53617fb91e498ae2935bde622417921415af255e390668f69ba908730

oracle/cpython-3.14.6/POSTFINAL-LOCALE-V5.md
1329cf9c8e36391af134b2fb2b212e71067ace736b282dacd2a6c90233384840

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

Require the actual independently published V10 all-family ownership-report
and strict-report hashes as separate command-line inputs. Authenticate the
complete original canonical reports, all **12** independently owned source
files, all **five** actual native binaries, all three genuine family workers,
all **13** matching guards, all **five** loader guards, all **48**
ordinary public pickle observations. Reject missing, guessed, repeated,
diagnostic, historical, failed, incomplete, or substituted evidence before
launching an official candidate worker.

For each selected family separately, require **four** additional externally
published hashes: its passing V11 qualified original edge archive, its
complete durable edge ownership proof, its passing V11 qualified original
deep archive, and its complete durable deep ownership proof. Reopen and
authenticate all four complete artifacts. Validate the exact original
**223,198** edge observations and **49** categories, all **393** deep
observations and **64** seeded cases, both actual before-and-after V10
owners, the exact V10-audited **content SHA-256 of every current family
source**, every current native binary, complete producer streams,
both real V10 report hashes, and the deep proof's binding to the very same
authenticated edge archive-and-proof pair. An archive, compact summary,
stdout, historical result, or diagnostic alone cannot qualify any family.

The actual isolated official candidate worker independently reauthenticates
this complete graph before candidate import. Run a real V10 native owner
immediately before and immediately after the exact original upstream suite.
Inside the candidate's original-method context, find the exact authentic
Stage 07 sentinel, use the unchanged
`stage07._poison_cached_module_aliases` helper on **every** genuinely cached
`re.` descendant and original holder alias, and verify the same sentinel,
`re._compiler`, `re._parser`, and all aliases immediately before and
immediately after **each** of the **152** original public methods: **304**
actual method-adjacent cache checks. The genuine holder-alias count may be
zero; negative values,
booleans, substitution, restoration, stdlib `_sre`, foreign packages, or
another candidate must fail closed. Revalidate unchanged current source and
native fingerprints after the suite.

## Preserve complete results once

Use separate exact V6 allowlisted names for its self-oracle, each candidate
pass, each candidate failure, the all-family passing report, and the actual
all-family failure report
`oracle/cpython-3.14.6/evidence/postfinal-locale-v6-all-failures.json`.
Before starting a
worker, reject any existing pass or failure destination, symlink, traversal,
historical destination, or unsafe parent. Create a real report exactly once
with `O_EXCL`, `O_NOFOLLOW`, bounded canonical JSON, a durable file `fsync`,
and a durable directory `fsync`. Preserve genuine partial method records,
active method, stdout, stderr, return code, signal, timeout, and real
before-and-after owner failures. Never replace or retry existing evidence.

## Reproduce candidate-free source checks

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/postfinal_cpython_locale_oracle_v6.py --self-test
env -i PATH=/usr/bin:/bin /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/postfinal_cpython_locale_oracle_v6.py --self-test
```

Both commands must use only in-memory deterministic controls. They must
start zero candidate or reference workers, import zero candidates, read or
write zero evidence, sample zero clocks, generate zero locales, and access
zero benchmark, performance, fixture, or holdout data. Neither command
qualifies an actual candidate or measures performance.

Commit and push this protocol and its V6 controller before any real V6
reference or candidate run. Supply actual V6 source/protocol hashes
externally. For an actual candidate, also supply
`--reference-sha256`, `--base-report-sha256`,
`--strict-report-sha256`, and, for every selected family,
`--FAMILY-edge-archive-sha256`, `--FAMILY-edge-proof-sha256`,
`--FAMILY-deep-archive-sha256`, and `--FAMILY-deep-proof-sha256`.
Until all genuine externally published prerequisites exist, candidate
correctness is **NOT RUN**, performance is **NOT MEASURED**, and the
holdout is **NOT ACCESSED**.
