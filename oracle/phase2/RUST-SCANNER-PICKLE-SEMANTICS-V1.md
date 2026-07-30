# First-party Rust scanner pickle-protocol semantics V1

Status: **SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN.**

This append-only Phase 2 source freeze corrects exactly one existing first-party
C function, `rust_scanner_reduce_ex`. Its pinned predecessor already retains the
safe changing-capture clamp and removes private external introspection:

```text
input   candidates/rust/variants/no_external_introspection_v1/py_bridge.c
SHA-256 2dd040dc0337f205134431ebeaafe56ee4fe63cc77c1bb6cb5434742549884b7
bytes   177146
device  2064
inode   524811
mode    0600
```

Frozen verification authenticates that predecessor indirectly through the
complete, committed no-external-introspection application receipt:

```text
oracle/phase2/evidence/rust-no-external-introspection-v1-application.json
SHA-256 57e28ad65b538db5189f264904d303f37f13506022eae07b12185a52f2624a43
bytes   1774
device  2064
inode   524813
```

Neither source verification nor self-test opens the candidate bridge. Only an
independently authorized root-only application after the immutable source freeze
is committed and pushed may open it, exactly once.

## Exact owned correction

The existing `rust_match_reduce_ex` already implements the correct CPython
protocol convention. The scanner must mirror it byte-for-byte except for its
owned object type:

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

`-1` is a valid low protocol when no Python error is set. Protocols below two,
including negative integers, `False`, `True`, integer subclasses, and successful
`__index__` objects, reuse the already-owned
`rust_owned_pickle_reconstruction`. Invalid protocol types and out-of-range
integers preserve the exact `TypeError`, `OverflowError`, or original `__index__`
exception raised by `PyLong_AsInt`. Protocols two and five retain the existing
scanner-specific cannot-pickle `TypeError` unchanged.

No new standard-library pickle package is imported. The existing scanner
`__reduce__`, existing match `__reduce_ex__`, existing `copyreg` reconstruction
helper, scanner descriptors, capture clamp, and no-external-introspection source
remain byte-for-byte unchanged. No external matching package, standard-library
matching delegation, new engine, canonical edit, or existing variant mutation
is authorized.

The exact immutable successor is:

```text
target  candidates/rust/variants/scanner_pickle_semantics_v1/py_bridge.c
SHA-256 e074be7b4a6882f2ac004f027f941240a373c85eb9267c59da4d5d354b8f4bfc
bytes   177348
delta   +202 bytes at exactly one reversible first-party function
```

## Authenticated public comparison receipts, not raw artifacts

The committed V26 and V27 public publication receipts are independently
authenticated in full:

```text
V26 receipt oracle/phase2/evidence/rust-native-architecture-public-gate-v2-v26-anchor-public-run-001-publication-receipt.json
SHA-256     23baf96a92f4fd2bf2809730bed056606de0c9c350ed46eea31fa9bdff6a8d80
bytes       40906
device      2064
inode       525333

V27 receipt oracle/phase2/evidence/rust-native-architecture-public-gate-v2-v27-compiler-public-run-001-publication-receipt.json
SHA-256     a825c358434fb44ab9d52eb8021271115b12e41c58b26243c7770faf4d533449
bytes       68330
device      2064
inode       525426
```

Both receipts attest the same public **10,434-case** comparison, the same
**1,145 actual public mismatches**, and the identical raw comparison digest:

```text
raw comparison SHA-256 7fc4c743e35bbe4f57ed0e3a872b9a9646b2603feedb9ae2c24421afed5430aa
raw comparison bytes   1428906
raw comparison opens   0
```

The raw comparison, stdlib observation files, candidate observation files,
timing files, and all native files are never opened. The 94 ordered public
dataset identities and seven scanner operations are authenticated from the
committed plaintext public matrix producer only:

```text
source  tools/rust_public_practice_benchmark_v2.py
SHA-256 a3d7e70343d231bf433fbad6a6669025a970d83691c49cb9f434a186aef3d9e6
bytes   112729
device  2064
inode   429259
source imported or executed: false
```

Exactly five scanner operations differ from the uncorrected bridge for every
public dataset:

```text
pattern.scanner.reduce_ex.negative  94
pattern.scanner.reduce_ex.zero      94
pattern.scanner.reduce_ex.one       94
pattern.scanner.reduce_ex.string    94
pattern.scanner.reduce_ex.overflow  94
gross scanner-profile rows          470
```

Three text datasets also have an independent first-party lexer failure because a
named Unicode character appears inside an ignored comment:

```text
text.comment.inline_unknown_named_unicode
text.comment.global_verbose_unknown_named_unicode
text.comment.scoped_verbose_unknown_named_unicode
```

All five targeted scanner operations overlap those three datasets: **15 rows**
cannot improve until the lexer is independently corrected. Therefore the
standalone scanner-only effect is **455 independent modeled rows**, not 470.
This is source-only accounting, not a measured candidate outcome.

The remaining operations `pattern.scanner.reduce_ex.two` and
`pattern.scanner.reduce_ex.five` are explicitly preserved for all 94 datasets.
Their three preexisting lexer-comment failures apiece, six rows total, remain
unchanged. Twenty-nine additional synthetic protocol controls cover the C-int
boundaries, valid `-1`, booleans, integer subclasses, `__index__` objects,
strings, bytes, `None`, floats, positive/negative overflows, and exceptions
raised by `__index__`.

## Complete original failure accounting

The complete immutable original V25 publication receipt is authenticated without
opening its compressed failure archive:

```text
oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-original-p0-v25-failures-publication-receipt.json
SHA-256 d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59
bytes   11832
device  2064
inode   524846
```

Publication succeeded; the candidate failed. All 13 original suites and the
complete 31,237-case denominator remain visible: 1,352 total semantic
mismatches, including 240 `substitution_v2` and 1,112 `shape_v2` rows, with
15,877 verified passing cases and no infrastructure failures. This scanner
correction has a distinct public profile and claims no measured reduction in
that original denominator.

The existing compressed archive is identified only by its receipt:

```text
archive SHA-256 dee05f06d473af52db5447b485265d886e66e5420cb3e814b5b972d8798a04a7
archive bytes   3771743
archive inode   524845
archive opens   0
inflations      0
```

## Physical source isolation and root-only application

The deny-default audit and descriptor-relative `O_NOFOLLOW` wall is installed
before every owner read. Self-test opens no workspace file. Frozen verification
opens only its own three source owners, four immutable plaintext receipts, and
the public dataset producer. Candidate sources, candidate variants, native
artifacts, raw comparisons, archives, proposals, final/holdout content, hidden
directories, process creation, compiler launches, network, clocks, and writes
are physically rejected. The script includes direct hostile controls for each.

Run both checks under the normal isolated pinned interpreter and again with a
sterile environment:

```text
python3.14 -I -B -S tools/apply_owned_rust_scanner_pickle_semantics_v1.py --self-test
python3.14 -I -B -S tools/apply_owned_rust_scanner_pickle_semantics_v1.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
env -i PATH=/usr/bin:/bin python3.14 -I -B -S tools/apply_owned_rust_scanner_pickle_semantics_v1.py --self-test
env -i PATH=/usr/bin:/bin python3.14 -I -B -S tools/apply_owned_rust_scanner_pickle_semantics_v1.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Only the root coordinator may apply the already-frozen change after committing
and pushing exactly the three owned source-freeze files. Explicit root
authorization and identical full 40-character frozen/pushed commits are
mandatory:

```text
python3.14 -I -B -S tools/apply_owned_rust_scanner_pickle_semantics_v1.py \
  --apply --root-authorized --frozen-commit PUSHED_FROZEN_COMMIT \
  --pushed-commit PUSHED_FROZEN_COMMIT --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Root-only application exclusively creates the new `0700` target directory and
the new `0600` bridge with descriptor-relative `O_NOFOLLOW | O_CREAT | O_EXCL`,
fsyncs the file and directory, and validates the complete durable readback.
Existing targets are rejected. No candidate is built, imported, executed,
benchmarked, qualified, or selected. Correctness and performance remain
**NOT MEASURED**. The former final holdout remains **INVALIDATED; REKEYED
SUCCESSOR REQUIRED** and is never opened.
