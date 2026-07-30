# First-party C public adapter compatibility correction V1

Status: **SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN.**

The independently written C candidate consists of its own Python parser and
compiler plus its own native C matching engine. This experiment changes only
its Python-facing adapter. It does not import Python's regular-expression
module, use another candidate, wrap an outside matching package, alter an
oracle, change a denominator, or claim that a correction has already worked.

## Preserve the actual C result

Authenticate the immutable latest completed C publication:

    oracle/phase2/evidence/repaired-c-original-campaign-v12-c-phase2-v21-c-original-match-semantics-original-p0-v12-failures-publication-receipt.json
    SHA-256  a3f4b90b8f289df9dfe49f776266e3c290edb2c21c62713137f501a5f997c21b
    bytes    10943
    device   2064
    inode    525645

Publication passed, but the candidate failed. Twelve of thirteen original test
groups completed; **16,413** checks were verified out of the unchanged
**31,237** original denominator. Exactly **606 observed failures** were all
individually preserved. The remaining interpreter-isolation group did not
complete. Its failure is real, and the total number of differences across all
thirteen groups is therefore **NOT MEASURED**.

The complete recorded partition is:

    managed buffer lifetime       16
    public object behavior       248
    substitution behavior        224
    public module behavior       114
    retained scanner lifetime      4
    total observed               606

The public-module records are not discarded as recording artifacts: their
authenticated transport wrappers can be removed read-only, and all **114**
still exhibit genuine underlying public-behavior differences.

Also authenticate both published owner-only C21 build records:

    oracle/phase2/evidence/native-source-build-v21-c-phase2-v21-c-original-match-semantics-publication-receipt.json
    SHA-256  9475dd0c441a0440136f12425f94e6a4244e4cdc52d49f803e891f6663a647df
    bytes    11878
    device   2064
    inode    524817

    oracle/phase2/evidence/native-source-build-v21-c-phase2-v21-c-original-match-semantics-root-provenance-receipt.json
    SHA-256  8f913d623bf5bb4aec3669e9b3daa882df16aad6f2f1bc3db1f02f4988a8afa2
    bytes    10837
    device   2064
    inode    524818

Those records establish two separate, byte-identical builds of the existing
first-party C engine. Its exact source SHA-256 is
`fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2`;
its exact native SHA-256 is
`7a5f8db27154cdcbd4203d727e02c0828ba1f9bf3fa2fdc1a86223ee57825f60`.
Neither native file, private build root, engine source, compressed archive,
original oracle, final-test proposal, or holdout is opened by a source gate.

The immutable canonical Python adapter is:

    candidates/vm_candidate.py
    SHA-256  b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096
    bytes    60707
    device   2064
    inode    428074
    mode     0600

Source gates authenticate this adapter's complete identity through both
published C21 receipts without opening the adapter. Only separately authorized
root materialization after a committed and pushed source freeze can read it.

## Seven reversible first-party adapter changes

1. Add the genuine zero-valued `NOFLAG` member and all seven genuine public
   class aliases `RegexFlag.A`, `.I`, `.L`, `.M`, `.S`, `.X`, and `.U`.
   Preserve CPython's exact class-member order, public flag names, numeric bit
   order, hexadecimal mixed unknown bits, and `re.RegexFlag(number)` for flags
   containing only unknown bits.
2. Publish the first-party `PatternError` class as belonging to `re`, while
   preserving its implementation, exception text, positions, and `error`
   alias.
3. Publish the owned public `RegexFlag` class as belonging to `re` only after
   the first-party native engine has finished its exact owner-attestation
   handshake; the genuine C-owned matching engine remains unchanged.
4. Declare separate bounded, first-party compile caches: **512** least-recently
   used entries and **256** first-in-first-out entries.
5. Cache exact `(type(pattern), pattern, flags)` keys, preserving distinct
   built-in and subclass identities and the standard two-cache lookup policy.
6. Never cache `DEBUG` compilations: compile and emit debug output every time;
   bound and evict normal cache entries using CPython's published policy.
7. Make the public `purge()` operation clear both caches.

The adapter continues to call its existing `_vm_native` parser/compiler/matcher
exclusively. Pattern parsing, bytecode generation, replacement expansion,
memory ownership, the native matching engine, scanner implementation, frozen
oracles, reference records, and all named private waivers remain untouched.

The exact observed, disjoint adapter-only correction targets are:

    public object behavior
      public PatternError module             96
      pattern-subclass cache identity        96
      unknown public flag representation     12
      compiled-pattern flag order            12
      subtotal                              216

    public module behavior
      unknown public flag representation     96
      DEBUG always recompiles                 8
      bounded cache eviction                 10
      subtotal                              114

    total modeled adapter corrections       330

The remaining **32** match-pickling differences in the same public object
group are native-code behavior and are explicitly not claimed as corrected.
The **16** buffer-lifetime, **224** substitution, and **4** scanner-lifetime
differences and the unfinished interpreter-isolation group remain genuine,
separate, and unresolved. The 330-row total is a source-only prediction from
preserved actual witnesses; it is not a measured rerun or a qualification.
The seven independently checked public flag-class aliases and the public flag
type's module identity are additional genuine API obligations, not invented
extra records added to the fixed 330-case observed partition.

The predicted immutable successor is:

    candidates/c/variants/public_adapter_semantics_v1/vm_candidate.py
    SHA-256  4a62cb318592600d53e5ed6b9f8b9edf4edf2068fb2453892ca2130bb203410a
    bytes    61663
    delta    +956 bytes across seven exact, independently reversible sites

## Source-only gates

Every gate uses isolated, bytecode-disabled, pinned CPython 3.14.6. A deny-by-
default descriptor wall and Python audit hook are installed before any owner
read. Verification reads only this experiment's three frozen owners and the
three authenticated plaintext C12/C21 receipts. Self-test reads no workspace
file at all.

Both modes forbid candidate imports, candidate execution, native libraries,
compressed archives, private roots, final-test files, oracle execution,
process creation, dynamic code, network, clocks, and workspace mutations.
Independent source-only semantic controls cover flag names and ordering,
unknown bits, text and byte subclasses, both cache capacities, eviction, purge,
and repeated uncached `DEBUG` compilations.

Run both ordinary source-only checks:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_c_public_adapter_semantics_v1.py --self-test

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_c_public_adapter_semantics_v1.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Repeat the exact same two commands under:

```text
env -i PATH=/usr/bin:/bin LC_ALL=C
```

After the exact three-owner freeze has been committed and pushed, only the root
coordinator may request one exclusive, descriptor-relative materialization:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_c_public_adapter_semantics_v1.py \
  --apply --root-authorized \
  --frozen-commit PUSHED_FROZEN_COMMIT \
  --pushed-commit PUSHED_FROZEN_COMMIT \
  --source-sha256 SOURCE_SHA256 --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

Materialization creates only a new `0700` variant directory and one new `0600`
adapter file using `O_NOFOLLOW | O_CREAT | O_EXCL`; it fsyncs and verifies
the exact predicted SHA-256. It never modifies a canonical candidate, existing
variant, native source, native binary, README, prior record, original oracle,
or evaluation data.

Corrected C compatibility is **NOT MEASURED**. Runtime non-delegation is
**NOT ESTABLISHED**. No build, candidate run, timing trial, final evaluation,
qualification, or winner selection is authorized by this source freeze.
