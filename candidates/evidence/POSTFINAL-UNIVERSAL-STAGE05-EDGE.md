# Repaired engines pass the full frozen matching test

Status: **PASS** for the current independently authored Rust, C, and Zig
engines. This is a matching and parser correctness test, not a performance
measurement.

Each engine runs the unchanged CPython **3.14.6** oracle against exactly
**223,198** matching, byte, Unicode, scanner, object, and parser
checks. That total includes a separately generated **14,783-case** public
object suite and a **20,480-case** parser and grammar suite. All three
produce the same complete observation digest as Python:

`b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526`.

| Engine | Correct checks | Failures | Evidence SHA-256 |
| --- | ---: | ---: | --- |
| Rust | 223,198 | 0 | `7d58cb2ed8acbcad71e04a9e2c4ef3fa95a3afae76edfadf654fc4f39c82e32f` |
| C | 223,198 | 0 | `05941ba203d777ec81e97ef8b97d0b27fe64a961a1ac12e8e470053fc23e52e4` |
| Zig | 223,198 | 0 | `e348d7cfa16ee32c0ed202691bf65d0862fbc8b5da23065fdfe3dc1c857a7327` |

The deterministic compressed reports bind each actual Python source and
loaded native library to its SHA-256. They preserve the frozen seed
`2026072329`, CPython **3.14.6**, and Unicode **16.0.0**. No performance
fixture or hidden case is accessed.

```sh
for engine in rust vm zig; do
  gzip -dc \
    "candidates/evidence/rust-v7-edge-oracle-${engine}-post-final-stage-05-universal-parity.json.gz" |
    jq '{module, correctness_checks, failed, expected_sha256, actual_sha256,
         performance, holdout}'
done
```

## Separate pattern and match object test

A separately frozen **393-case** test compares Python's actual pattern and
match objects, signatures, exceptions, captures, and visible lifecycle.
Two independently run Python references agree on every observation. The
current source for each candidate passes, with **13** forbidden-regex checks
and **10** cross-engine isolation checks.

| Engine | Correct checks | Public differences | Evidence SHA-256 |
| --- | ---: | ---: | --- |
| Rust | 393 | 0 | `e7df2331ab821f6fe60353410d2f74045c31ef840b057dc363d4214894bcda8a` |
| C | 393 | 0 | `b1606a8076630650cd6092abbc3916c2755f4f0af071bc8861ff87a89b9e7207` |
| Zig | 393 | 0 | `0c18b9c8222b0b642a95ebc3793cc48f3eb135842f35c4b370fd05bb45da1a41` |

The C candidate's frozen proof correctly uses the engine family name `C`,
even though its Python module is named `vm_candidate`. The report is
`RUST-V8-DEEP-CONTRACT-C-POST-FINAL-STAGE-05-UNIVERSAL-PARITY.json.gz`;
substituting `VM` fails before creating evidence.

## Separate callbacks, scanners, and observable argument behavior

A frozen **479-check** suite independently compares callbacks, warning and
exception details, scanner exhaustion, changing buffers, Python's observable
argument order, and pattern and match lifetimes. Each engine also passes
**34** native argument-binding controls. All three produce the exact Python
observation digest
`6e3593b963036e2381569475cac390ccbb7bc6dbc8358acda578fcbcb7e0642e`.

| Engine | Correct checks | Differences | Evidence SHA-256 |
| --- | ---: | ---: | --- |
| Rust | 479 | 0 | `735795ca5c83ccb315db3cfbd10559575f801f2f12da4b26dbee0931ed5fed7d` |
| C | 479 | 0 | `ff5c563614900437375068b763aa40bf6557a943d4990bc5d86d3a94faa5255c` |
| Zig | 479 | 0 | `4e31f020a3def0f125562af9010bbb54cd299ddf81fde33dff61219fd7d6c0c3` |

Each compressed proof independently verifies the candidate's passing object
contract, full matching proof, actual source, and native libraries. The
complete **22-stage** Unicode campaign must still be rerun on current
source. Expanded public speed, native memory, and the **65,536-case**
holdout remain **NOT MEASURED**.
