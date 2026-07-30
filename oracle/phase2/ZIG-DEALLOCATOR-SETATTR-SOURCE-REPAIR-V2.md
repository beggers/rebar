# First-party Zig finalizer setter repair V2

Status: SOURCE FREEZE ONLY. The proposed corrected candidate is not written,
built, imported, run, or qualified.

## The actual failure

Authenticate the complete, unchanged V1 finalizer-repair source, protocol and
canonical contract. Authenticate the separately frozen V13 Zig campaign source,
protocol and canonical contract. Read only its exact 78,911-byte plaintext
failure receipt,
`repaired-zig-original-campaign-v13-phase2-v13-zig-guard-clean-lifetime-v1-original-p0-v13-failures-publication-receipt.json`,
SHA-256 `b3443a647c638cbbbe7905a2c668a734770f38cb678f06a387af497917fc4bca`.
Never open its matching archive.

Reject the complete physical `open` audit unless its owner, access mode and
integer flags are all authenticated and strictly read-only. In particular,
direct `_io.open`, a saved builtin, `w`, `r+`, append, create, truncate,
noninteger flags and incomplete audit arguments cannot bypass the source wall.
Independently reject direct import audits and every `os.*` filesystem,
permission, timestamp, descriptor, directory, child-process or mutation audit.
Exercise these attacks with synthetic audit events only; never attempt a real
write to `GOAL.md`, a candidate, evidence or any other file.

All 13 actual, distinct, guarded V13 workers recorded the same shutdown
failure, including all seven genuinely passing test groups:

```text
Exception ignored while calling deallocator
line 1086, in __del__
line 1079, in __setattr__
TypeError: argument of type 'NoneType' is not a container or iterable
```

The V1 repair correctly saved the native release function and attribute lookup
before Python module teardown. However, `self._handle = None` still invokes
`Pattern.__setattr__`, which checks the module-global `_PATTERN_METHODS`.
Python has already cleared that global during shutdown. This is an observed
failure of our own first-party adapter, not an external package or regex engine.

The actual V13 run attempted 31,237 original checks in 13 groups. Seven groups
passed 4,607 checks. Five complete groups recorded 1,700 actual differences.
The remaining subinterpreter group did not complete: its genuinely guarded
child creation produced zero child interpreters, zero installed child guards,
and zero child matching calls. Do not label that failure a successful
interpreter or a semantic mismatch. Overall mismatches: NOT MEASURED.
Candidate result: FAIL. Receipt `PASS` means durable publication only.

## Exactly one in-memory source change

Authenticate every byte, original inode and physical identity of the actually
tested V1 lifetime input,
`candidates/zig/variants/scanner_phrase_guard_clean_lifetime_v1/zig_candidate.py`,
SHA-256 `e9e052fdd50bcec54145b828b1353cf082c6bc13869176486bcfa41d1624ab50`.
Prove that its unique exact finalizer is:

```python
def __del__(self, _free=_zig_bridge.free, _getattr=getattr):
    handle = _getattr(self, "_handle", None)
    if handle:
        self._handle = None
        _free(handle)
```

Derive exactly one prospective change, in memory only:

```python
def __del__(
    self, _free=_zig_bridge.free, _getattr=getattr,
    _setattr=object.__setattr__,
):
    handle = _getattr(self, "_handle", None)
    if handle:
        _setattr(self, "_handle", None)
        _free(handle)
```

The frozen implementation spells the signature on one line; the multiline
presentation above has identical Python meaning. The real frozen contract
contains the precise complete replacement block and resulting complete-source
SHA-256. The object setter, native release, and attribute lookup are all captured
when the class is defined. Consequently cleanup does not call the custom
setter, read `_PATTERN_METHODS`, or depend on module globals at shutdown.
Clear ownership before releasing so recursive cleanup cannot release twice;
allow missing handles, and propagate genuine native-release errors.

Require one unique `Pattern`, one unique finalizer, the exact original public
setter, unchanged imports, unchanged instance slots, and complete whole-file
AST identity except for the finalizer. Do not change a parser, compiler,
scanner, matcher, native engine, C bridge, test, other candidate, or runtime
guard. The proposed additive variant is NOT MATERIALIZED. In particular, this
freeze does not write `candidates/zig_candidate.py` or any candidate variant.

## Independently reproduce the shutdown behavior

Synthetic self-tests run only the authenticated finalizer in a locally created,
ordinary Python class. First reproduce the real V1 defect: set
`_PATTERN_METHODS = None`, observe the original setter's `TypeError`, and prove
the native release was not called. Then poison `_PATTERN_METHODS`,
`_zig_bridge`, `getattr`, and `object`; prove the V2 finalizer invokes the saved
object setter, clears ownership, calls exactly the saved native release once,
and never invokes the overridden public setter. Independently test repeated
cleanup, partial initialization, false handles, recursive release, rebound
module globals, and genuine release failures. Never suppress a release error.

## Preserve all boundaries

Verify the complete frozen original 31,237-case, 13-group, 73-obligation,
34-crosswalk reference with its exact 13 named private waivers. The separate
8,244 checks and two Python reference workers are not part of the original
denominator and are not candidate results. Verify the V1 and V13 canonical
contracts, genuinely inherited V2/V3 guard identity, exact public V13 receipt,
all 13 original stderr warnings, all five measured losses, and zero real child
executions. Verify the exact restored Zig source and native inode metadata
without opening either current native library.

The 14,155,776-case holdout remains NOT FROZEN, NOT GENERATED and NOT OPENED.
Never import `re`, `_sre`, an external regex package, a candidate or its native
bridge. Never open a private root, archive, holdout, canonical native library,
benchmark, or recovery journal. Never create a process, thread, interpreter,
timer, output file, source variant, build, or candidate. All 25 recorded
source-only effects must be zero. Candidate correctness, finalizer warnings in
a real corrected run, child behavior, independence, undefined behavior, memory,
and performance remain NOT MEASURED or NOT ESTABLISHED. Qualified engines: 0.

## Four independent source-only gates

Use the exact pinned CPython 3.14.6 executable with `-I -B -S`. Run
`--self-test` and `--verify-frozen-context` in both the ordinary isolated
environment and the empty environment
`env -i PATH=/usr/bin:/bin LC_ALL=C PYTHONDONTWRITEBYTECODE=1`.

Every invocation must independently supply the exact V2 source, protocol and
contract SHA-256 values, all three V1 source-freeze values, all three V13
source-freeze values, the actual V13 plaintext-receipt SHA-256, and the exact
V1 lifetime-input SHA-256. `--render-contract` omits only the not-yet-created V2
contract hash and emits canonical JSON to standard output without writing a
file. Reject `--run`, `--worker`, `--recover`, `--build`, `--apply`,
`--install`, `--benchmark`, `--generate`, and `--open-holdout`.
