# Run the unchanged Python regex tests

Status: **PROSPECTIVE; REFERENCES NOT RUN; CANDIDATES NOT RUN.**
Speed, memory measurements, holdout performance, and a winner are **NOT
MEASURED**. An in-memory self-test or a preflight is not an official test run.

## First, check Python against itself

Use the pinned, isolated, bytecode-free CPython 3.14.6 release. Independently
run the exact, unchanged upstream `Lib/test/test_re.py` twice in two genuinely
separate Python processes. Neither process may import a candidate, consult a
candidate audit, run an edge proof, require an old campaign, read benchmark or
holdout data, or substitute a locally recreated upstream test. The only
publication prerequisites are the actual externally frozen SHA-256 hashes of
this version-five protocol and its version-five controller.

Preserve all actual individual outcomes from **both** reference processes.
Require each to have the same 152 original public methods in the same source
order, 151 actual passes, and exactly one actual `requires debug build` skip for
`ReTests.test_memory_leaks`. Classify that one original decorator honestly as
`named-private-debug-condition`; debug-build coverage is **NOT RUN**. Require
the complete two status vectors, method-body hashes, fixtures, and observed
resource records to agree. No public method is waived.

## Preserve the original test, fixtures, and limits

These are the already frozen, unchanged CPython inputs:

| Input | SHA-256 |
| --- | --- |
| Original `test_re.py` | `879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2` |
| Original `re_tests.py` | `ec04a2b2a77338d20b37d931693c7e588a2896d3c73c7b4b47973e24c13b5aab` |
| Original Python 3.14.6 source archive | `143b1dddefaec3bd2e21e3b839b34a2b7fb9842272883c576420d605e9f30c63` |
| All 26 genuine upstream `test.support` source files | `6cd13337b46bd6a53a32ac0c557da79b0ddd536ac82be885cc57be77e80f1632` |
| Exact original 152-method source and AST matrix | `5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a` |
| Immutable complete version-four controller | `9f39e055922daf9b2a5f4a93048d97df6dcd4164eb9b6017bf4a20c3dcbb0652` |
| Immutable complete version-four protocol | `54a4e397860ddab092dd9386a3a8cf3521d96b1fcf4d7d35bcbe55118d8a7a76` |

Retain all 139 original `ReTests`, all 11 `PatternReprTests`, and both
`ExternalTests`; independently account for the 13 methods in the two named
private-only classes without counting them as public tests. Execute the literal
original external-corpus tests, including all 400 initial tuples, all three
originally appended tuples, and all 11 real external correctness fixtures.
This includes the genuine original scanner, large repeats, group references,
unknown flags, structural pattern equality and hash behavior, Unicode names,
warning cases, and every other method of the original matrix.

Run both original two-gibibyte tests with their actually observed original
`2**31` sizes and real upstream `test.support.set_memlimit("40G")`; retain
`test_large_subn`'s genuine `18 * 2**31` (36 GiB) requirement. Never accept
the upstream decorator's 5,147-item dry run. Use one exclusive large-memory
worker. Retain genuine fresh ISO-8859-1 and UTF-8 private locales, the original
CPU resource, ten-million-character subject, real `Stopwatch` and 0.1-second
assertion, the original `fork` regression, genuine multiprocessing,
`SHORT_TIMEOUT`, and actual unchanged `re._constants.MAXGROUPS` import. A
real resource failure, timeout, crash, missing locale, disabled CPU resource,
changed fixture, captured stderr, or genuine test failure cannot be renamed a
pass.

## Then require independently built engines

A candidate run is a separate, fail-closed mode. Before importing **any**
candidate or starting a candidate worker, authenticate the exclusively
published, passing two-reference version-five report against its exact actual
SHA-256. Separately authenticate the actual passing all-three-family V8
from-scratch audit and actual passing all-three-family V8 no-delegation audit,
their exact independently frozen source hashes
`14b8daeebfb620eafa778529f6bf11e1a4f48256dd010b25621f4e94666692c6` and
`bb22b1983c11a896d3639077050dfaac746876ccbb9e4909518fb33d19987c01`,
and the exact current owned Python source and five native ELF hashes. The
immutable native-ownership protocol is
`5c60e6ce63ff1e4c5593eaafe29971cb3557b1a0389dcd5cf41cfb00647bc399`.

Require the already published proof controller
`tools/postfinal_current_build_proofs_v8.py` with SHA-256
`0f9e12847855797669206ea89de94948da66c29742d64820a625ce5a6570b313`
and its already published protocol with SHA-256
`76e66c091ae06ad56b8f4e22c76f4db44810cdb512b839201c9cc7cb83f4cfa0`.
For **each** Rust, C, and Zig family, authenticate its own actual, passing,
qualified complete original 223,198-check/49-category edge archive and its own
actual, passing, qualified complete original 393-check deep-contract archive.
Bind all six exact archive hashes to the same actually audited current source
and native ELF. Diagnostics, synthetic records, historical V7 results, a
different family's proof, unqualified passes, and failed archives do not
qualify. Preserve all three actual historical edge failures as failures.

Supply independently generated audit and proof fingerprints explicitly to the
candidate command. An absent, guessed, duplicated, or historical fingerprint
blocks execution **before** candidate import. External runtime pins keep this
protocol, its controller, and the already produced reference byte-for-byte
unchanged. There is no circular prerequisite from the Python-only self-oracle
to a candidate, audit, proof, or old V7 campaign.

Actual report hashes are not known until their genuinely passing reports exist.
Supply only those genuinely observed hashes through an independently frozen,
source-authenticating runtime-pin launcher. The launcher may set only the
documented report-hash constants in the exact already frozen `bb22…` strict
controller and `0f9…` proof controller immediately before their genuine
entry points. It may not change a source file, test, matching implementation,
reference record, candidate, ownership check, or output. This keeps all exact
controller hashes, the two-reference report, and the candidate gates acyclic.

Run every candidate in its own isolated Python process with the same unchanged
152 original methods and real upstream fixtures as both references. Keep
stdlib, `_sre`, foreign-engine, cross-family, and native-loader guards active;
hash the actual independently owned mapped native binaries before and after.
Allow only the isolated original `MAXGROUPS` constant needed by the unchanged
public upstream import; it may not provide matching. Require the exact same
151 passes, one named private debug skip, and public outcome vector as **both**
actual reference processes.

Every evidence destination has a separate exact version-five allowlisted name.
Create it once using exclusive, no-symlink, bounded, durable writes. A real
failure retains actual partial records, active method, available worker
stdout/stderr, return code, signal, and timeout details; never overwrite or
retry existing evidence. No benchmark, timing, holdout, release, or deployment
is part of this correctness protocol.

## Reproduce

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/postfinal_cpython_locale_oracle_v5.py --self-test
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/postfinal_cpython_locale_oracle_v5.py --preflight
```

Run these commands from the repository root. The directly executed controller
adds only its own resolved repository root to Python's isolated import path;
it does not rely on `PYTHONPATH`, the current directory's implicit import
behavior, or a special `-c` launcher. Internally, each genuinely isolated
official worker retains its separately authenticated, absolute-root
bootstrap.

Both controls also work from an explicitly emptied environment:

```text
env -i PATH=/usr/bin:/bin /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/postfinal_cpython_locale_oracle_v5.py --self-test
env -i PATH=/usr/bin:/bin /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B tools/postfinal_cpython_locale_oracle_v5.py --preflight
```

After the actual controller and this protocol have been committed and pushed,
pass their real SHA-256 values to `--self-oracle --source-sha256 HASH
--protocol-sha256 HASH`. This starts exactly two genuine standard-library
workers, one after the other. Candidate execution additionally requires
`--candidate all`, the actual reference SHA-256, all four actual V8 audit
source/report hashes, and all six actual per-family passing archive hashes.
Until those real artifacts exist, candidates are **NOT RUN** and performance is
**NOT MEASURED**.
