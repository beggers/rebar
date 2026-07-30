# First-party Zig campaign with separated runtime authority, version 15

Status: SOURCE FREEZE ONLY. No candidate, native build, archive, benchmark,
recovery, or holdout is run or opened by this protocol.

## Preserve the measured V14 controller failure

Authenticate the entire 5,474-byte public evidence file
`zig-original-campaign-v14-setter-safe-prepublication-controller-failure.json`,
SHA-256 `2d1bad717e782b7ed3e0af856f8687e9a29abc93ebf1553adc6d65f668aa5c65`.
Preserve exactly one attempt, pipeline exit 4, its complete empty standard
output, all 211 bytes of captured standard error, and the actual message:

```text
actual three-role campaign/recovery failed: CampaignError:
source-only wall rejected unlisted, native, archive, holdout or write open
```

The controller failed before a recovery root, native staging, candidate result,
or result publication. Candidate process status, workers, completed groups,
passing checks, regular-expression differences, and corrected cleanup warnings
remain NOT MEASURED. No candidate success or failure archive or receipt was
created. Verify all three original source/native owners, including their exact
inodes and canonical `0600`/`0700` modes. Do not classify this prepublication
controller failure as an actual candidate run.

Authenticate all 23 independently supplied historical V14 authorities and the
complete frozen V14 source, protocol, and canonical contract:

```text
8757ff2fdda5e8e60ee694b0d803018ddf33ea7266b8d7a5eff6d52d0866569d
691ab654b88ed30f6cd0729d987415162708fdfb90c36d91bf41dcefdbb5fcef
1c7326dc2f63635f3e32ec0558b51f21c952d51480f336e3b0d4d49e38428a0a
```

## Exact root cause and narrow correction

The immutable V13 controller assigns `REAL_OPEN = os.open` as it is imported.
The V14 procedure authenticated and imported that controller while the V2
source-only deny-default wall had temporarily installed `os.open = wall.opened`.
Although exiting the wall correctly restored `os.open`, V13 retained the old
bound `wall.opened` as `REAL_OPEN`. The first authorized native-owner check
therefore called the stale source-only wall and stopped before activation.

Never relax the physical source wall, extend its allowlist to native files,
expose a raw opener during source verification, or globally disable a guard.
Instead require all of the following before any runtime authority is granted:

1. All 27 independent V15/V14/source/failure pins and the complete canonical
   V15 contract have already been verified.
2. The captured V13 opener is exactly the current wall's bound method.
3. The source wall has actually exited and is inactive.
4. The V2 module records no active wall.
5. The restored process `os.open` is exactly the independently authenticated
   V2 `REAL_OPEN`; both original Python open and import functions are restored.
6. Only the authenticated, owned V13 controller's `REAL_OPEN` is rebound to
   that exact restored opener, and only for explicit `--run`, `--worker`, or
   `--recover` authority.

Synthetic hostile checks must prove that the same rebinding is rejected while
the source wall is active and that all three originally failing owner calls are
denied before a native file is physically opened. The corrected runtime
operation is NOT RUN as part of a source freeze.

## Keep the unchanged Python reference and Zig implementation

Use official isolated CPython 3.14.6 with `-I -B -S`. Preserve the full
original 31,237-case, 13-group Python suite, all 73 obligations, 34 original
crosswalk entries, and exactly 13 named private waivers. The independently
verified 8,244 additional cases remain separate and are never added to the
original denominator.

Retain the exact original V13 Zig result: 13 distinct genuinely guarded
workers, seven passing groups and 4,607 verified cases, five complete mismatch
groups totaling at least 1,700 differences, and one failed original
subinterpreter group. Its actual failure proves zero successfully returned or
recorded child interpreters, zero recorded installed child guards, and zero
recorded child cases, initialization calls, or cleanup calls.

The authenticated V3 guard invokes the real provider's native creation before
checking its result and live-set postconditions. The older observer increments
its creation counter only after that call returns. Therefore a failed
postcondition can leave every recorded child counter at zero after a native
interpreter has already been created. Physical native creation, physical native
destruction, and restoration of the native live set are NOT MEASURED. Never
describe the recorded zero as proof that no transient interpreter existed.

Every V13 worker showed the finalizer error. The public excerpts contain at
least 143 visible warning occurrences; the full occurrence count is NOT
MEASURED.

The previously frozen setter correction changes exactly one independently
owned finalizer node. Derive its complete 67,335-byte adapter only in memory;
its SHA-256 is
`c16a6e4c9745eff3a55dcf85eb14c26ec84092d70ddbc40d5e841ab0140d3032`.
Do not materialize a candidate variant, reuse another regex engine, delegate
to Python `re` or `_sre`, add an external package, suppress a native cleanup
failure, or claim that corrected matching or warning removal has been
measured.

Preserve the real V3 runtime guard and exact inherited V2 policy, code, and
globals. Child-interpreter requirements of 11 created children, 394 case
calls, 11 bootstrap calls, and 11 cleanup calls are future requirements only.

## Recovery and publication are actual-run-only

A separately committed, pushed, and explicitly authorized `--run` may stage
only the already independently built native Zig/C owners and the in-memory
corrected first-party adapter. Use an exclusive V15-specific private recovery
root, `campaign-v15.lock`, V15 stage and backup names, and an fsynced three-role
journal. Restore the exact original adapter, bridge, and engine in reverse
order before publishing complete original evidence. A separately authorized
`--recover` requires the independently pinned recovery-journal digest. Run
every original group with its unchanged 120-second limit; preserve every
failure and all 13 genuine process identities. A publication `PASS` attests
durability only, never candidate compatibility.

## Source-only verification

Accept `--verify-source`, `--verify-frozen-context`, `--describe`, and
`--self-test` as source-only operations. Independently supply all 27 pinned
owner/failure/guard/build values and the complete V15 source, protocol, and
canonical contract hashes. Run source verification and self-tests in both the
ordinary isolated environment and
`env -i PATH=/usr/bin:/bin LC_ALL=C PYTHONDONTWRITEBYTECODE=1`.

Require every one of the 25 existing source-only side-effect counters to remain
zero. Exercise the entire inherited V2/V14 hostile-control set and new hostile
controls for stale bound openers, premature runtime authorization, forged
warnings or candidate results, all 23 original authority fields, all original
owner identities and modes, duplicated or incomplete pins, direct `_io` and
descriptor writes, archive/native/private/holdout opens, imports, real process
creation, missing evidence, false result archives, and fabricated
subinterpreters.

The expanded 14,155,776-case speed holdout is NOT FROZEN, NOT GENERATED, and
NOT OPENED. Corrected matching, cleanup behavior, runtime independence,
undefined behavior, speed, and memory are NOT RUN, NOT ESTABLISHED, or NOT
MEASURED. Qualified replacements: zero. Winner: none.
