# Two independent Python callable-signature references

Status: **SOURCE FREEZE ONLY. The 50 additional reference checks have NOT
RUN. No candidate, speed comparison, memory result, or final holdout has
been run or opened.**

Python's regular-expression module exposes not just matching behavior, but
also the public function and method signatures used by normal Python tools.
The already-frozen version-1 signature matrix covers exactly **50** such
observations: 11 public module functions, 18 compiled-pattern methods,
14 match methods, and seven scanner methods. They are additional checks;
they do not change the original **31,237** cases, **13** test groups, or
**13** named private waivers.

This version freezes a separately reproducible, recovery-safe way to obtain
the missing actual Python-versus-Python reference. It does not perform the
reference itself.

## Exact original oracle

The only permitted Python executable is:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016
```

The exact original worker, protocol, machine contract, and case vector are:

```text
tools/verify_python_re_callable_introspection_v1.py
5a64fb4546bdccd13b6d8d9ba32a7472b01cb86dd0d9f2c643678e6bbf919653

oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md
1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8

oracle/phase1/p0-callable-introspection-v1.json
e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349

50-case vector
89ff9e5197ac0fee63a5b7f3880d9d66083f7e25255d0d062e14ff84ab5c884b
```

A later explicitly authorized `--run-reference` starts exactly two direct,
isolated processes of that original worker. It requires the two named
roles, two genuinely different process IDs, all 50 original observations
from each worker, exact matching complete case vectors, and every byte of
both original output and error streams. It starts no extra reference
orchestrator and never imports or starts a candidate.

## Preserve history and later results

The frozen version-1 signature contract correctly preserves its own
historical snapshot: **151** evidence owners, **156** history references,
and the historical Rust result of **1,087** differences. Those historical
numbers are not the current results.

The independently authenticated version-33 graph proves a historical lower
bound of **155** evidence owners and **160** history references. Its Rust
result has **1,036**
differences and **8,965** verified passing checks; C has **1,230**
differences. The last fully tested Zig implementation has **2,172**
differences. The corrected, independently implemented Zig source has
completed **26** build processes across two independent builds. At that
specific version-33 snapshot, corrected Zig matching was **NOT MEASURED**.
That graph is not asserted to remain the latest result.

If the separately frozen corrected Zig campaign subsequently publishes its
actual complete 13-group matching result, this verifier authenticates the
new, separate receipt and preserves its actual passing count, mismatch
count, worker count, restored native files, and genuine **PASS** or **FAIL**.
If an actual infrastructure failure prevents all 13 workers from starting,
preserve the real smaller worker count and the original **NOT MEASURED**
mismatch status; never invent missing matching results.
It never opens or decompresses the large matching archive. That later
publication proves lower bounds of **157** owners and **162** references.
Other concurrent evidence may make the true totals higher; never present an
older lower bound as the latest total or hide a later matching result.

All four current graph owners and the actual corrected Zig archive and
receipt are individually authenticated. The compressed Zig build is
verified only as exact compressed bytes; it is never decompressed. No
candidate-matching archive is opened.

## Future durable publication

Only an explicit reference run may create the private evidence directory.
A successful actual comparison will publish exactly two new, distinct
owners:

```text
oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6.json.gz
oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6-publication-receipt.json
```

An actual failure uses the corresponding `-failures.json.gz` and
`-failures-publication-receipt.json` names. Never reuse, overwrite, follow
a symlink to, or silently replace any existing successful or failed
evidence. Create each owner using `O_CREAT | O_EXCL | O_NOFOLLOW`, private
mode `0600`, full same-inode readback, and both file and parent-directory
`fsync`. Compression is reproducible with gzip modification time zero.

The receipt's publication status means only that evidence was durably
recorded. Its independent reference status must retain the actual **PASS**
or **FAIL** and preserve every worker failure. Starting from the pinned
version-33 snapshot, two genuinely new evidence owners imply at least
**157** owners and **162** references; these are lower bounds, not guesses
about other concurrently published experiments.

No performance data is collected. The planned 4,194,304-example final
comparison remains **NOT FROZEN**, **NOT GENERATED**, and **NOT OPENED**.

## Verify this source freeze

Independently compute and supply all three version-2 owner hashes:

```text
sha256sum tools/run_owned_callable_introspection_reference_v2.py \
  oracle/phase1/CALLABLE-INTROSPECTION-REFERENCE-V2.md \
  oracle/phase1/callable-introspection-reference-v2.json
```

For each of the following modes, supply `SOURCE_SHA256`,
`PROTOCOL_SHA256`, and `CONTRACT_SHA256` from that command:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/run_owned_callable_introspection_reference_v2.py --self-test \
  --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/run_owned_callable_introspection_reference_v2.py --self-test \
  --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/run_owned_callable_introspection_reference_v2.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/run_owned_callable_introspection_reference_v2.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

The self-test uses synthetic complete reference vectors. Physical effect
barriers prove that it does not start a worker, write evidence, start a
candidate, load native code, access the network, inspect a holdout,
inflate an archive, or measure a clock. Read-only context verification
independently authenticates the original frozen matrix, unchanged core,
version-33 graph, and corrected Zig publication.

Only after this source freeze, protocol, and contract have been committed
and pushed may an explicitly authorized `--run-reference` actually run the
two Python references. That result is a separate focused chunk. It does
not qualify any candidate or permit benchmarking.
