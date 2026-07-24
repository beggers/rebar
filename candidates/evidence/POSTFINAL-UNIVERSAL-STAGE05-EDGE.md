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

The separate public-object, tracing, and complete Unicode campaign proofs
must still be regenerated for the current source. Expanded public speed,
native memory, and the **65,536-case** holdout remain **NOT MEASURED**.
