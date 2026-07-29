# First-party C Match compatibility correction, version 1

Status: source frozen only. The proposed C variant has not been written,
built, imported, or tested. Candidate correctness, performance, memory, and
undefined behavior are NOT MEASURED. The hidden holdout is NOT OPENED.

This small, independently reproducible source experiment makes exactly one
first-party correction to the previously frozen C implementation. It does not
wrap, import, or delegate to Python `re`, `_sre`, another candidate, or an
external regular-expression package.

## Original evidence and unchanged denominator

The oracle is the already frozen official CPython 3.14.6 P0 matrix: exactly
31,237 original case executions, 13 original suites, and 13 individually named
private waivers. The separate 8,244 reference cases are not added to the
candidate denominator. CPython must run with `-I -B -S`.

The independently authenticated small C V7 failure receipt recorded 13 real,
distinct original-suite workers. Its publication passed only as a durable
record; the candidate itself failed. Five suites completed; the two passing
suites cover 13,094 cases. Three completed failing suites establish a lower
bound of 236 mismatches: 16 managed-buffer mismatches, 216 public-type
mismatches, and four Python 3.14 PEP-688 buffer mismatches. Seven suite
execution failures and one reporting infrastructure failure mean the complete
number of mismatches is NOT MEASURED.

The receipt contains aggregate public-type results, not individual failure
vectors. Therefore this protocol does not claim that all 216 public-type
mismatches, or any particular number of them, were caused by Match pickling.

## Exactly one source correction

The original, independently frozen public-type oracle requires `re.Match`
pickling to fail for each pickle protocol 0, 1, 2, 3, 4, and 5. The frozen C
source instead reconstructs a Match for protocols 0 and 1. Derive a variant
in memory by replacing exactly the two adjacent Match reduction functions with
functions that reject all six protocols using the original `TypeError` text.
Preserve `PyNumber_Index` and integer protocol validation.

The variant must preserve the original Match copy and deep-copy identity
functions byte for byte. It must also preserve the complete subject capture
and buffer error paths byte for byte. In particular, the frozen substitution
oracle explicitly requires nested buffer acquisitions with flags `(0, 0, 284)`,
last-in-first-out release, and the original `TypeError` for a released subject
memoryview. Simplifying nested capture or blindly preserving every buffer
acquisition exception would break the unchanged original oracle.

The 16 managed-buffer mismatches and four PEP-688 mismatches are not repaired
by this source freeze. Whether any of the 216 public-type mismatches are
repaired is NOT MEASURED until the derived variant is actually built and run
against the original frozen suite with the unchanged runtime guard.

## Three distinct result-reporting defects

The existing small receipt and frozen first-party suite sources establish
three separate reporting problems. None is evidence of a matcher mismatch,
and none is repaired or hidden by modifying a test case, runtime guard, or C
engine in this source-only experiment.

1. The substitution suite exercises authentic lone-surrogate subjects. The
   historical producer emits a lone surrogate that its own strict evidence
   reader rejects. A later report-transport fix must round-trip a separately
   tagged UTF-16 code unit and preserve both the original suite and the strict
   reader.
2. The public-surface oracle authenticates the exact identity of its own
   `_NormalizedEnvelope`. The historical report encoder rejects that genuine
   value. A later reporting fix must accept only the factory-authenticated
   identity and must not trust an arbitrary `dict` subclass. The receipt's
   guard-installation stage is not the real stage of this report failure.
3. The threaded oracle hashes canonical bytes without a trailing newline. The
   historical report encoder applies newline-terminated framing and rejects
   the genuine digest. A later reporting fix must preserve the exact original
   no-newline digest. The receipt's guard-installation stage is not the real
   stage of this report failure.

## Physical source-only gate

The controller bootstraps the independently pinned C V6 and C V5 source walls
and immediately restricts the allowlist to the three new owners, the exact
immutable original C variant, the small 7,375-byte failure receipt, and the
named frozen phase-one, producer, guard, historical source-freeze, and suite
text owners. It never authorizes the current canonical candidate, Python
adapter, compiled extension, failure archive, private build root, overview
graphs, holdout proposal, benchmark, worker, compiler, network, or clock.

Self-tests prove that unauthorized operations and synthetic changes to Match
copying, nested buffer acquisition, released-buffer handling, published suite
counts, worker identities, the mismatch lower bound, and the measurement
boundary fail closed. They also demonstrate that a tagged surrogate
round-trips and that changing threaded digest framing changes the digest.
These are source-only checks, not candidate executions.

The proposed 14,155,776-case expanded holdout remains NOT GENERATED and NOT
OPENED. This freeze neither authorizes phase three nor establishes a faster
or fully compatible candidate.

Run the following commands using the exact independently calculated SHA-256
of each of the three new owners:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S \
  tools/apply_owned_c_original_match_semantics_v1.py --self-test \
  --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S \
  tools/apply_owned_c_original_match_semantics_v1.py --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

Repeat both with `env -i PATH=/usr/bin:/bin` to demonstrate independence from
the caller's environment. No source-only command builds, materializes,
activates, or measures the proposed C matcher.
