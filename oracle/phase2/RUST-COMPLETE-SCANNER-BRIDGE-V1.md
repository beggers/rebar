# First-party complete-original and scanner-protocol Rust bridge V1

Status: **SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN.**

This append-only Phase 2 freeze composes two genuinely materialized, committed
first-party bridge corrections. Its normal and sterile source gates authenticate
both immutable source/protocol/contract/application quadruples and the complete
public V25, V26, V27, and V28 receipts. They never open either existing
candidate bridge, a native object, a raw comparison, an archive, Git metadata,
an invalidated final, a clock, or a matching/introspection package.

## Two actual, independently authenticated predecessor bridges

The complete original-compatibility predecessor is the committed, root-applied
`complete_semantic_correction_v2` bridge:

```text
path     candidates/rust/variants/complete_semantic_correction_v2/py_bridge.c
SHA-256  254a8cea354556789496ce9dbfe70b4fed73ed9ee8e3b7f1c107dfe8662d7f55
bytes    178270
device   2064
inode    526052
mode     0600

source       dd80de72a2104703d8c36269cbef56e67231add6f31a7a8c8f7bf05aa5f0e807
protocol     aae4793c84f1f4d93806f2484047d3b1e2a7f544c25d02b08551f2d9f07f2936
contract     25ae3e1a35fae2ace9533b14fdaf771c0270b50b5b93b5b702d683906ca2dbe3
application  304396bb08709d63d0cb89e08d40e369a754f9e4352015955a33ab6fb99113cb
```

The independent scanner-only predecessor is the committed, root-applied
`scanner_pickle_semantics_v2` bridge:

```text
path     candidates/rust/variants/scanner_pickle_semantics_v2/py_bridge.c
SHA-256  e074be7b4a6882f2ac004f027f941240a373c85eb9267c59da4d5d354b8f4bfc
bytes    177348
device   2064
inode    526082
mode     0600

source       0a61db87974b1801e0af598440af1b4d30e71cd9a8c63e1b250d5676f078d5b8
protocol     a078bb4563cad5616ab668cdbde4ac735d42dcabc44501259ac8143667ece7f7
contract     14786ce9b80fb353af728019c8734c2a9b7022387257729ee0b520f4557a5422
application  c76760a4f738a7843cab4a5604c991776652b50307f671df9209b506178df99a
```

Application receipts authenticate the actual committed candidate bytes without
opening either candidate during a source-only gate. The standalone scanner
candidate remains unopened even during eventual authorized application.

## Exact commuting source composition

The complete predecessor already owns both existing `Match.expand`/trailing
probe correction sites and all four reversible replacement/exporter-order sites
inside `rust_substitute_core`. The scanner-only correction owns exactly one
different function, `rust_scanner_reduce_ex`, before that substitution core.
Its exact replacement is:

```c
static PyObject *rust_scanner_reduce_ex(RustIterator *iterator, PyObject *protocol) {
    int protocol_number = PyLong_AsInt(protocol);
    if (protocol_number == -1 && PyErr_Occurred()) return NULL;
    if (protocol_number < 2) {
        return rust_owned_pickle_reconstruction((PyObject *)iterator);
    }
    return PyErr_Format(
        PyExc_TypeError,
        "cannot pickle '%.200s' object",
        Py_TYPE(iterator)->tp_name
    );
}
```

The replacement validates low, negative, boolean, subclass, and `__index__`
protocols with `PyLong_AsInt`, retaining original type/overflow/index errors.
Protocols two and five remain unchanged. The match exemplar, owned scanner
reconstructor, scanner descriptors, two genuine generic finish clamps, unique
safe capture-clamp context, no-external-introspection correction, complete
replacement validation/release ordering, guarded cleanup, trailing escape probe,
and `Match.expand` forward declaration/full definition are preserved.

The scanner and substitution regions are explicitly disjoint and reversible;
the entire corrected substitution core and all bytes after it remain identical.
No private `inspect`/`functools`, stdlib matching delegation, external regex
package, canonical source edit, prior variant edit, build, import, execution,
qualification, performance result, or winner is authorized.

```text
target  candidates/rust/variants/complete_scanner_bridge_v1/py_bridge.c
SHA-256 f6253fbecc76b64750a22dc9393180d3ea6e3f2e29aace006c0479543e94342e
bytes   178472
delta   +202 bytes relative to the complete original-correction predecessor
sites   2 preserved expansion + 4 preserved substitution + 1 new scanner
```

## Complete original accounting and independent public scanner accounting

The complete original V25 publication receipt is authenticated in full without
opening its failure archive:

```text
receipt  oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-original-p0-v25-failures-publication-receipt.json
SHA-256  d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59
bytes    11832
inode    524846

original suites                 13
original case denominator    31237
actual verified passing      15877
actual original mismatches    1352
substitution_v2 mismatches     240
shape_v2 mismatches           1112

disjoint original correction:
  240  substitution exporter ordering
 1024  shape-changing substitution exporter ordering
   56  trailing-escape outer-length probes
   32  malformed named-template Match.expand validation
 ----
 1352  complete modeled original mismatch denominator

separate ordering/probe overlap witnesses: 32; not added to 1352
```

The three independently committed public publication receipts all identify the
same **10,434-case**, **1,145-mismatch** raw public comparison by receipt only:

```text
V26 SHA-256 23baf96a92f4fd2bf2809730bed056606de0c9c350ed46eea31fa9bdff6a8d80
V26 bytes   40906
V26 inode   525333

V27 SHA-256 a825c358434fb44ab9d52eb8021271115b12e41c58b26243c7770faf4d533449
V27 bytes   68330
V27 inode   525426

V28 SHA-256 c786b1216a58c4ac6a29363ce87d7741fb55fbb85f30665f795875bef244becb
V28 bytes   40372
V28 inode   525923

raw comparison SHA-256 7fc4c743e35bbe4f57ed0e3a872b9a9646b2603feedb9ae2c24421afed5430aa
raw comparison bytes   1428906
raw comparison opens   0
```

The frozen public dataset producer supplies 94 ordered datasets and five
targeted scanner operations. This yields 470 gross scanner-profile rows. Three
named-Unicode comment datasets independently fail lexing and overlap all five
targeted operations, so 15 rows cannot improve until their separate lexer
failure is repaired. The standalone scanner effect is therefore exactly **455
independent modeled public rows**; protocols two and five preserve 188 rows,
including six preexisting comment failures. These public rows are a different
ledger from the original 1,352 modeled cases and must not be combined into a
single measured correctness result.

No composed candidate has been built, imported, executed, audited, qualified, or
benchmarked. Actual candidate correctness, mismatch count, native safety, memory,
runtime non-delegation, and performance remain **NOT MEASURED** or **NOT
ESTABLISHED**. The final holdout remains **INVALIDATED; REKEYED SUCCESSOR
REQUIRED**.

## Physical source isolation and four mandatory gates

The irreversible descriptor-relative `O_NOFOLLOW` wall is installed before the
first approved owner read. Self-test reads no workspace owner. Source
verification opens exactly its current source/protocol/contract triple, both
committed predecessor source/protocol/contract/application quadruples, the
complete V25 receipt, the V26/V27/V28 public receipts, and the frozen plaintext
dataset producer: 16 public owners total. Candidate sources, native binaries,
raw public artifacts, compressed archives, proposals, final content, hidden
roots, `.git`, process launches, network, clocks, and workspace writes are
physically rejected.

Run all four gates with the pinned project CPython and separately calculated
complete lowercase owner SHA-256 pins:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_complete_scanner_bridge_v1.py --self-test

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_complete_scanner_bridge_v1.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_complete_scanner_bridge_v1.py --self-test

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_complete_scanner_bridge_v1.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Only the root coordinator may materialize the frozen successor after committing
and pushing exactly this source/protocol/contract triple. The complete
40-character frozen and pushed commit IDs must match, all three independent
owner digests must match, and explicit root authorization is mandatory:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_complete_scanner_bridge_v1.py \
  --apply --root-authorized --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256 \
  --frozen-commit PUSHED_COMMIT --pushed-commit PUSHED_COMMIT
```

The wall keeps both committed candidates forbidden through all owner
authentication and every hostile control, including in actual apply mode. Only
after those checks does a one-shot authorization admit the complete predecessor
for exactly one pinned candidate-source read. Root exclusively creates the new
`0700` variant directory and one `0600` `py_bridge.c` using
`O_CREAT | O_EXCL | O_NOFOLLOW`, fsyncs file and directory, and verifies the
complete durable readback digest. The standalone scanner candidate remains
unopened, existing paths remain untouched, and no candidate execution occurs.
