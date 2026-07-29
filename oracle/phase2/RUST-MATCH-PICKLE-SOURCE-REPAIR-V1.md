# First-party Rust match-serialization source repair V1

This is a frozen, source-only improvement to the existing from-scratch Rust
candidate. It is not a new regular-expression engine, a candidate run, a
benchmark, or a correctness qualification.

## Honest starting point

The actually completed 13-suite Rust campaign remains **FAIL**: 928 observed
compatibility differences and 8,965 explicitly verified passing checks. All 13
distinct candidate workers completed without infrastructure failures. The
original oracle remains exactly 31,237 cases, 13 suites, and 13 named private
waivers. Public-import, giant-input, and callable-introspection supplements
remain separate and do not increase that denominator. The expanded
4,194,304-case holdout remains **NOT OPENED** and ungenerated. Performance,
full native memory safety, undefined behavior, and runtime non-delegation remain
**NOT MEASURED** or **NOT ESTABLISHED**, as appropriate. No winner is selected.

The genuine, actually tested Rust bridge is
`4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257`
(176,118 bytes), and the genuinely tested public adapter is
`d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e`
(31,934 bytes). The historical plain-text failure-publication receipt is
`b87ff02f10103c1c8e7da7ed7ef77cd58936af2fe9e9b3c47448e8a449b01943`.
A successful publication receipt means durable publication; it never means the
candidate passed. The verifier does not open, decompress, or hash the failure
archive or read mutable documentation.

## Append-only combined native bridge

The preceding independently frozen buffer and replacement source is
`candidates/rust/variants/buffer_shape_v1/py_bridge.c`, SHA-256
`29421096dc81759ca11c53080b7f838cc29ad16baa7e379c18c8417d35ab37b3`
(180,436 bytes). Its dedicated verifier, protocol, and contract are pinned
individually, as are the four immutable pushed V49 graph owners. That source
was never a passing matching run.

The new complete variant is
`candidates/rust/variants/buffer_shape_pickle_v1/py_bridge.c`, SHA-256
`00271ad5fff71e2f2e30cda6b446a61d0c300cb91eec2091b8ada17662d9a335`
(181,004 bytes). Exactly three uniquely verified source transformations retain
every preceding buffer, error, callback, and capture fix. They extract the
existing scanner's first-party `copyreg._reconstructor` tuple into a shared
native helper; use that same helper for match serialization; and install a
distinct native `__reduce_ex__` using the pinned CPython signed-C-int
`PyLong_AsInt` behavior. Protocols below two use the existing reconstruction;
protocols two and above retain the Python `TypeError`. Invalid protocol
arguments and integer overflow propagate naturally. Existing scanner
serialization, `__copy__`, `__deepcopy__`, the custom native Match
constructor, and the actual public adapter remain intact.

The single existing lazy `copyreg` import remains confined to serialization;
no import is added to matching. No external regular-expression package, Python
`re`, `_sre`, other candidate, or CPython regular-expression engine is
called. Source inspection is not a proof of runtime non-delegation. This is
the same first-party Rust family, not another candidate.

The historically observed 32 low-protocol match-serialization differences
are separate from 896 buffer and shape differences. This source freeze neither
reruns those cases nor claims any were repaired. The only actual campaign
result remains 928 differences and 8,965 verified passing cases.

## Reproduction and safety boundary

Use `/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14`.
Supply independently computed exact source, protocol, and contract SHA-256
values:

```text
python3.14 -I -B tools/apply_owned_rust_match_pickle_source_repair_v1.py \\
  --self-test --source-sha256 SOURCE --protocol-sha256 PROTOCOL \\
  --contract-sha256 CONTRACT

python3.14 -I -B tools/apply_owned_rust_match_pickle_source_repair_v1.py \\
  --verify-frozen-context --source-sha256 SOURCE \\
  --protocol-sha256 PROTOCOL --contract-sha256 CONTRACT
```

Repeat both commands with the absolute interpreter under
`env -i PATH=/usr/bin:/bin LC_ALL=C`. All four gates must pass. A
clean-bootstrap, irrevocable Python audit wall permits only exactly pinned,
bounded, immutable plain-text owners and historical source ASTs. It physically
blocks regex and candidate imports, native loading, clocks, networks, writes,
processes, all compressed archives, the holdout, and unlisted files. Duplicate
JSON keys and unpaired Unicode surrogates are rejected. Hostile self-tests
cover all preceding buffer protections, each native pickle transformation,
the signed protocol boundary, scanner and constructor preservation, fabricated
passing results, and genuine physically blocked events. Neither this protocol
nor either verification mode starts a candidate, runs a compiler, loads a
native bridge, measures speed, or reads a mutable experiment log.

Combined bridge: **NOT BUILT**. Candidate matching: **NOT RUN**. Correctness:
**NOT MEASURED**. Performance: **NOT MEASURED**. Holdout: **NOT OPENED**.
