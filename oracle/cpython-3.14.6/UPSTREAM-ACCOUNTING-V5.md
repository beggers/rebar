# Account for every original Python regex test

Status: **The frozen CPython 3.14.6 source and existing Python-only reference
evidence are verified. Candidate compatibility and performance are NOT
MEASURED. No winner is selected.**

This additive document corrects the historical accounting without modifying
the old source, manifest, evidence, or README. The authoritative complete
[manifest-v5.json](manifest-v5.json) has SHA-256
`41b598475a6f756bf63dcd71141d602da05ebb7a810525c45b6c07635b78c0d7`.
It individually maps every original source-ordered test and method-body hash.

## Every original test

The unchanged [test_re.py](test_re.py) has SHA-256
`879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2`.
The unchanged [re_tests.py](re_tests.py) has SHA-256
`ec04a2b2a77338d20b37d931693c7e588a2896d3c73c7b4b47973e24c13b5aab`.

| Original class | Tests | Meaning |
| --- | ---: | --- |
| `ReTests` | 139 | Required public behavior. |
| `PatternReprTests` | 11 | Required public behavior. |
| `ExternalTests` | 2 | Required public behavior. |
| `DebugTests` | 4 | Named CPython-only private implementation tests. |
| `ImplementationTest` | 9 | Named CPython-only private implementation tests. |
| Total | 165 | 152 required public tests and 13 named private tests. |

The **165-method** source matrix is
`93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240`.
The separate **152-public-method** source matrix is
`5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a`.
These have genuinely different denominators and canonical codecs.

No public test is waived. `ReTests.test_memory_leaks` is a required public
method. Its genuine upstream decorator records `requires debug build` because
a release build lacks `re.Pattern._fail_after`. The truthful release-build
result is therefore **151 passes and one named private-debug-condition skip
out of 152 public methods**. Debug-build coverage is **NOT RUN**. It is not
a public waiver or a 152nd pass.

The only 13 private waivers, in actual original source order, are:

- `DebugTests.test_debug_flag`
- `DebugTests.test_atomic_group`
- `DebugTests.test_possesive_repeat_one`
- `DebugTests.test_possesive_repeat`
- `ImplementationTest.test_immutable`
- `ImplementationTest.test_overlap_table`
- `ImplementationTest.test_signedness`
- `ImplementationTest.test_disallow_instantiation`
- `ImplementationTest.test_deprecated_modules`
- `ImplementationTest.test_case_helpers`
- `ImplementationTest.test_dealloc`
- `ImplementationTest.test_repeat_minmax_overflow_maxrepeat`
- `ImplementationTest.test_sre_template_invalid_group_index`

These inspect CPython's private opcode text, compiler, `_sre`, internal
object implementation, or deprecated private modules. None excludes public
matching behavior.

## Keep the four genuine histories separate

| History | Authenticated evidence | What it establishes |
| --- | --- | --- |
| Bounded candidate-facing V5 | Source `8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce`; 165-method matrix `93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240`; frozen vector `b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276`. | The preserved candidate harness explicitly uses a **5,147-item dry run**. It does not prove a candidate passed either real 2 GiB method. |
| Full-resource Python V5 | Source `9a4f2ac53617fb91e498ae2935bde622417921415af255e390668f69ba908730`; protocol `1329cf9c8e36391af134b2fb2b212e71067ace736b282dacd2a6c90233384840`; signed report `3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916`; per-role vector `28226e851b225d0e9564e3765dbbd4e1ad86381168ab05f52fccaa0632332a1a`. | Two original Python reference roles each record all **152** public methods, **151** passes and the actual debug skip. Both genuine large-memory methods received **2,147,483,648** items under the actual **40 GiB** upstream resource configuration. |
| Separate full-resource Python V6 | Source `b1522b55b37de2e004b029c128e2e75c3020cda34165bcf0de07cb5ebb3136cb`; protocol `8e43ceaa61f6e70e2e1193de71bde8583c101cdbe40bc78d862ae789531aff57`; signed report `1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf`. | A genuinely separate full-resource history. Its Python results agree with V5, but it is **not** V19's prerequisite. |
| Expanded public Python V19 | Source `fda386f3c00be660a41e92d8005fc287706d9dc050967cf2b708cb6f8aba113e`; protocol `53a415c7257222602ae69870c0e4343d85f77e1a2963f508d18d227038abc2ea`; signed report `a2ac2853a6551b9eb95564ee74731c9e7d44998f5ec32ad5aac2259b5b313ad8`; vector `c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef`. | Both signed reference roles preserve **1,376** cases: **43** categories of **32**. Each has **64** real locale cases and **192** ISO-8859-1 → UTF-8 → ISO-8859-1 transitions. Its authenticated parent is full-resource Python **V5**, not V6 or bounded candidate V5. |

These are existing signed source and Python-reference records. They do not
qualify a candidate or transfer Python's full-memory result to a candidate.
No distinct process IDs are claimed where the original report stores roles
and complete streams but does not record PIDs.

The original corpus contains **400** initial cases and **3** authentic
extensions, for **403** total. Its **11** benchmark-named upstream fixtures
are correctness assertions; reading their original source does not run a
benchmark. All **26** original `test.support` source modules are physically
authenticated. The full V5/V6 original 2 GiB records, the real 40 GiB limit,
the original ten-million-character CPU assertion, genuine fork record, and
fresh ISO-8859-1 and UTF-8 locale evidence are verified as evidence. None
is rerun by this accounting verifier.

The original V19 report genuinely contains supplementary Unicode and lone
surrogates. Decode it with pinned CPython's bounded, duplicate-key-strict
JSON parser. Preserve its exact producer bytes and both complete role
stdout/stderr streams. Never use `jq`, reject valid regex-data surrogates,
normalize the full evidence, or substitute one producer's newline codec
for another.

## Preserve the old result as history

The original [manifest.json](manifest.json), SHA-256
`2c89ce37e474cb6f59d61f86ad810662b50b83bbdce3610c04523fe092688597`,
[evidence/self.json](evidence/self.json), SHA-256
`d5d3ce72f1e0b788d2aca05fa7d0f5233023d123945ad3b342625e30b3543b84`,
and original [README.md](README.md), SHA-256
`676414247d8ac8f6daafedcce134897535c094b47a8f7e8dccd106428b839091`,
remain byte-for-byte unchanged.

That real history selected **146** methods, passed **144**, skipped two
unavailable locale tests, and recorded **8** named exclusions. It is
**HISTORICAL** and does not establish full public compatibility.

All six formerly excluded public methods are mandatory:

- `ReTests.test_re_groupref_overflow`
- `ReTests.test_large_search`
- `ReTests.test_large_subn`
- `ReTests.test_search_anchor_at_beginning`
- `ReTests.test_regression_gh94675`
- `ReTests.test_memory_leaks`

Neither original locale method is waived. Both genuinely pass in the
separately signed full-resource Python V5 and V6 reports.

## Reproduce without running a candidate

The read-only verifier is `tools/verify_original_cpython_accounting_v1.py`,
SHA-256
`f562ab8c998197880590487fa6e78f511db5c01596ab35731185ca8caead454c`.
Its source-only self-test has exactly **740** unique in-memory controls:
**7** positive checks and **733** independently rejected attacks. All
**23** filesystem, candidate-import, process, thread, locale, clock, entropy,
and network attempts are actually blocked.

~~~text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/verify_original_cpython_accounting_v1.py --self-test --source-sha256 f562ab8c998197880590487fa6e78f511db5c01596ab35731185ca8caead454c

env -i PATH=/usr/bin:/bin /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/verify_original_cpython_accounting_v1.py --self-test --source-sha256 f562ab8c998197880590487fa6e78f511db5c01596ab35731185ca8caead454c
~~~

Authenticate all exact original source, all 26 support modules, signed
V5/V6/V19 Python records, full V19 process streams, locale transitions, and
unchanged historical artifacts using the read-only mode:

~~~text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/verify_original_cpython_accounting_v1.py --verify --source-sha256 f562ab8c998197880590487fa6e78f511db5c01596ab35731185ca8caead454c --manifest-sha256 41b598475a6f756bf63dcd71141d602da05ebb7a810525c45b6c07635b78c0d7

env -i PATH=/usr/bin:/bin /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/verify_original_cpython_accounting_v1.py --verify --source-sha256 f562ab8c998197880590487fa6e78f511db5c01596ab35731185ca8caead454c --manifest-sha256 41b598475a6f756bf63dcd71141d602da05ebb7a810525c45b6c07635b78c0d7
~~~

Both modes start zero actual reference or candidate workers and write no
files. Complete source accounting and existing Python-only evidence are
**PASS**. Candidate full-resource qualification, memory use, performance,
the expanded holdout, and a faster replacement remain **NOT MEASURED**.
