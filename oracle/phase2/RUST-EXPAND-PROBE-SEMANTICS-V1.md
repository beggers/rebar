# First-party Rust trailing-escape probes and exporter Match.expand validation V1

Status: **SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN.**

The sole authenticated historical evidence owner is the complete immutable
original V25 publication receipt:

    oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-original-p0-v25-failures-publication-receipt.json
    SHA-256  d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59
    bytes    11832
    device   2064
    inode    524846

Publication succeeded; the candidate failed. All 13 original suites and their
31,237-case denominator remain visible: 1,352 total semantic mismatches, 240 in
`substitution_v2`, 1,112 in `shape_v2`, 15,877 cases in completely passing
suites, and 13 unchanged named private waivers. No partial pass is invented for
either failing suite. The existing compressed archive and all native files are
never opened by this source freeze.

The independently pinned, already-safe predecessor is:

    input   candidates/rust/variants/no_external_introspection_v1/py_bridge.c
    SHA-256 2dd040dc0337f205134431ebeaafe56ee4fe63cc77c1bb6cb5434742549884b7
    bytes   177146
    device  2064
    inode   524811
    mode    0600

Frozen verification authenticates that identity without opening the predecessor.
Only separately authorized root-only materialization may read it, exactly once,
after the immutable freeze commit has been pushed.

There are exactly two byte-anchored first-party C corrections.

First, `rust_restore_original_template_error` saves the original `msg` and
nested `pos`, then immediately before reconstructing the owned `PatternError`
performs this exact-message-only probe:

```c
int trailing_escape = PyUnicode_CompareWithASCIIString(
    message, "bad escape (end of pattern)"
);
if (trailing_escape < 0 && PyErr_Occurred()) {
    Py_DECREF(position);
    Py_DECREF(message);
    Py_DECREF(raised);
    return -1;
}
if (trailing_escape == 0 && PyObject_Length(replacement) < 0) {
    Py_DECREF(position);
    Py_DECREF(message);
    Py_DECREF(raised);
    return -1;
}
```

A failed length probe supersedes the saved pattern error. A successful probe is
discarded and the original nested position is preserved. Every other error
message performs **zero** replacement length probes; an unconditional probe
would introduce 32 new malformed-template mismatches.

Second, only the non-bytes buffer-exporter branch of `Match.expand` validates
the complete normalized template before its ordinary two-argument expansion:

```c
PyObject *validation_arguments[3] = {
    normalized, (PyObject *)match, Py_True
};
PyObject *validated = PyObject_Vectorcall(
    state->template_helper, validation_arguments, 3, NULL
);
if (validated == NULL) {
    Py_DECREF(normalized);
    (void)rust_restore_original_template_error(template);
    return NULL;
}
Py_DECREF(validated);
```

The existing owned template helper's third `Py_True` argument requests
validation only: malformed input cannot call `match.group`, reacquire the
subject buffer, or reorder those events before its error. Existing normalization
retains `PyBUF_SIMPLE`, releases the original exporter before validation, and
preserves all successful-expansion buffer lifetimes. No production stdlib
matcher, external engine, private introspection, or matching delegation is
introduced; safe capture clamping remains unchanged.

Exactly **88 disjoint original shape records** are modeled without opening any
candidate, archive, native object, or holdout:

* 32 stable template-only-direct substitution rows missing
  `length-probe:template:outer`.
* 24 `Match.expand` trailing-backslash rows: eight template-only stable, eight
  both-direct stable, and eight template-only mutate.
* 32 malformed named-template `Match.expand` rows: the exact visible templates
  `<\g<word>:\g<` and `<\g<word>:\g<number`, lengths 13 and 19; each has
  eight stable and eight mutate witnesses. Every row requires zero replacement
  length probes, zero capture lookup, and zero subject-buffer reacquisition.

A further **32 both-direct substitution rows** overlap the independent
substitution-ordering correction. That A32 overlap is explicitly modeled and
reported separately; it is not included in this correction's 88-record B56+C32
denominator, and this transformer does not alter substitution ordering.

The exact predicted immutable successor is:

    target  candidates/rust/variants/expand_probe_semantics_v1/py_bridge.c
    SHA-256 d0f0422a08592390619138d072cb831d6d446f38e2b67750798a221e7693d822
    bytes   178081
    delta   +935 bytes at exactly two reversible owned sites

Self-test reads no workspace files. Frozen verification authenticates only its
own source, protocol, and contract plus the single original V25 plaintext
ledger receipt. Its deny-default audit and descriptor wall is installed before
all owner reads; candidate sources, `.git`, native objects, compressed
archives, private roots, subprocesses, network, clocks, final artifacts, and
holdout contents are physically forbidden. It performs zero workspace writes.

The former final V2 holdout proposal is **INVALIDATED; REKEYED SUCCESSOR
REQUIRED**. Its contents are never opened and no qualification, benchmarking,
performance result, runtime non-delegation proof, or winner is claimed.

Use the isolated pinned project interpreter:

```text
python3.14 -I -B -S tools/apply_owned_rust_expand_probe_semantics_v1.py --self-test
python3.14 -I -B -S tools/apply_owned_rust_expand_probe_semantics_v1.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Only the root coordinator may materialize the source after freezing, committing,
and pushing all three owned files. The identical full 40-character frozen and
pushed commits and explicit root authorization are mandatory:

```text
python3.14 -I -B -S tools/apply_owned_rust_expand_probe_semantics_v1.py \
  --apply --root-authorized --frozen-commit PUSHED_FROZEN_COMMIT \
  --pushed-commit PUSHED_FROZEN_COMMIT --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Root-only application creates exactly the new `0700` variant directory and its
exclusive `0600` `py_bridge.c` using descriptor-relative `O_NOFOLLOW | O_CREAT |
O_EXCL`, fsyncs both, and validates the complete durable readback. Existing
targets are rejected; canonical sources and predecessor variants are untouched.
