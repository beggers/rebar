# Run the complete original Python compatibility campaign

Status: **NOT RUN.** The rebuilt Rust, C, and Zig engines have passed the
current independent source, native-ownership, original upstream Python,
corrected generic-alias, and corrected durable full-public checks. They
have not passed this new complete, separately recorded 22-stage
campaign. The genuine first full-public reference failure remains
preserved and cannot qualify any candidate. Performance, memory,
holdout results, rankings, and a winner are **NOT MEASURED**.

## Actual passing prerequisites

The independently rebuilt source and strict no-delegation audits are:

```text
tools/postfinal_from_scratch_audit_v7.py
defa306e47a0d325af7d4c7fabb54324f6cb6d4653a494c46846838f5e2cf487

candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json
efae1f94fb06a1eabbab352794410c4d8e20a78202dcbf769b08ff9c7cee130a

tools/postfinal_no_delegation_audit_v7.py
9283457064f32658747b449c4ee6ebd20ca7cc7dc442ce03ece6b02896cff4e4

candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json
1f71caac01bffdffbf7ffdc2e21a9aa8d6936c452051cbdaa4c90ac67010fd34
```

These prove 12 genuinely owned source files, five rebuilt native
binaries, three independent native matching families, four distinct
source pipelines, all 48 real ordinary pickle round trips, six real
native-owned string and bytes match representations, and the exact
anti-delegation and native-loader guards. Python's `re`, `_sre`, another
candidate, external regex packages, and replaced binaries cannot do a
candidate's matching.

All four engines genuinely passed 146/146 unchanged selected Python
3.14.6 upstream methods, including the original 403-case corpus, two
freshly compiled real locales, and only the eight frozen named waivers:

```text
tools/postfinal_cpython_locale_oracle_v3.py
28b98c8913ca89ec2ba600484205c3bcb63ae22a86e33d4f7cf3c6f1a68c8a58

oracle/cpython-3.14.6/POSTFINAL-LOCALE-V3.md
a1f77b1628c03d42b9d8e2650c9b501d9be4cec917d765539c91c750154bd6ac

oracle/cpython-3.14.6/evidence/postfinal-locale-v3-all.json
18a011a5ce6e47e52cd02e4cb0812c8f9f7919a069edd7d74e57631623b901b5
```

The genuine earlier 145/146 Rust failure remains preserved as a failed
experiment, never relabeled as a pass:

```text
oracle/cpython-3.14.6/evidence/postfinal-locale-v2-rust-failures.json
a77f47cbfb992aa9ae3ced5394bffb75575e6f305f0d2bd0fe2677092517654f
```

## Actual passing public checks and preserved failed experiment

Before any complete family campaign, root must freeze, push, execute,
and exclusively preserve both genuinely passing public experiments
against the exact V7 binaries. The actual earlier failed reference must
remain visible. The one bounded Stage17 evidence reader must also be
source-frozen; missing reader fingerprints stop the campaign before
any production file is read or a worker can start.

Stage 14 must retain both complete, independently produced 128-row
Python-reference arrays, all 256 original two-reference observations,
both complete reference arrays in the final comparison, and all 384
individual candidate observations for public generic aliases:

```text
tools/python_re_generic_alias_public_oracle_stage14.py
oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V14.md
oracle/cpython-3.14.6/evidence/public-generic-alias-v14-self-oracle.json
candidates/evidence/python-re-generic-alias-public-oracle-v14-all.json
```

Stage17 genuinely passes all eight full-public and fuzz groups. It
retains both complete, independently produced 3,584-row Python
reference arrays, both actual reference worker reports, all 7,168
Python-reference observations, and all 10,752 actual Rust, C, and Zig
candidate records. Its new seed is `2026072485`, and its frozen matrix
is `e1c6ccf6cbb057f3e3cb708c1b4efe2a175bc77d6eda5e127cae18e5455cfa47`:

```text
tools/python_re_universal_public_oracle_stage17.py
9e5ca448ecc6a6de8745b0c84cf5b4ae5d92cd098914731a4047d45e6ce1b6d4

oracle/cpython-3.14.6/PUBLIC-CONTRACT-V17.md
8773d4fd2d0b9f04808b2a22358a233b44abfd892862aaaf224cd0d607081520

oracle/cpython-3.14.6/evidence/public-contract-v17-self-oracle.json
de1272f7c3681402b8787ea2a53de8228ef0341760505dc052c52b023e3d3c3d

candidates/evidence/python-re-universal-public-oracle-v17-all.json
255644709afe8fa8ce41cefcfd029b7f865bbcd0314d528902bb5a56d52aa288
```

The complete Stage17 all-candidate report occupies 20,220,593 bytes.
Consume it exclusively through this independently frozen, exact-path,
no-follow, 32 MiB evidence reader:

```text
tools/python_re_universal_public_oracle_stage17_evidence.py
fbaebec7bcfad26c94154dce2024ece8349ea54479fda6831d5331f4195fd4cb

oracle/cpython-3.14.6/PUBLIC-CONTRACT-V17-EVIDENCE.md
c6b4a3b037ca79f7ccef0c7248ac5d7dbbb1a8f339155b277f8c36ad3c14191d
```

Do not truncate this report, weaken a case, silently raise a global
file limit, or substitute an ordinary 16 MiB reader.

Stage15 is **FALSIFIED**, not a passing alternative. Its actual
original reference and independently preserved first-failure record
remain unchanged:

```text
oracle/cpython-3.14.6/evidence/public-contract-v15-self-oracle.json
755cb818f59259bb5adb05a93782afc3eef12e001c41a976ba4b9258ae54ac01

tools/python_re_universal_public_oracle_stage15_failure.py
07a522f263cd9e0baad022f91988d034b3cde3013b143bd1f9a77174fa0b58b6

oracle/cpython-3.14.6/PUBLIC-CONTRACT-V15-FAILURE.md
6aa2b8e5bcd6867af60c570d19508a67e0094eedca4ab815266e0f91e2c83b03

oracle/cpython-3.14.6/evidence/public-contract-v15-reference-failures.json
cb71e1a44549c7c76c3bf08900e6107d2b49e789e5002afc725d1e9df0c92880

ordinary durable JSON transport digest
0d6a74b1f923436c14569bfdd84431e4251f3bb8dd3129fbbcaf82a47f906b94

distinct immutable Stage15 validator digest
7a3bed83093800085fe1bd084820108142929f60e37632b3c24a02c6a4584d72
```

Both original validator contexts genuinely reject the first reference;
its native candidates were **NOT RUN**. Every campaign must bind
`sealed_stage17_provenance` and `sealed_stage15_failure_provenance`
inside its actual `from-scratch-static-audit` stage. Neither older
Stage12 evidence, the falsified Stage15, a synthetic check, nor an old
V5/V6 campaign qualifies the newly rebuilt engines.

## Execute all 22 original correctness stages

The complete source-bound controller is
[`rust_v8_multi_candidate_campaign_postfinal_v7.py`](../../tools/rust_v8_multi_candidate_campaign_postfinal_v7.py).
Each family independently reruns the original immutable correctness
scripts, property and fuzz seeds, reference records, native boundaries,
and exact denominators. The 22 individual genuine step reports must
include:

- 223,198 frozen edge observations across 49 categories, 393 deep
  public cases, and the original `2026072347` seed.
- Four independently guarded native-boundary stages and the 479-case
  cross-family observation suite with its original `2026072343` seed.
- The 8,244-case and 44,084-case original correctness suites.
- All 146 original upstream Python methods with newly compiled genuine
  ISO-8859-1 and UTF-8 locales.
- The 190-case upstream public API, owned public API, Unicode group
  errors, and unchanged extended Python behavior.
- The 8,862 replacement/callback checks and 11,266 deeper callback
  checks.
- All 254 crash/resource checks, 348 depth/overflow checks, and all
  4,494,555 full-plane Unicode comparisons.

Compile and independently verify new real private locales for each
complete family campaign; bind the unchanged official-test child to
that actual temporary locale directory. Preserve each actual step,
real failure record, evidence fingerprint, candidate identity, native
mapping, and original property/fuzz seed. Never use a historical
temporary locale, historical report, external matcher, approximation,
holdout, performance fixture, timer, or reduced denominator.

The only permitted new, exclusively created results are:

```text
candidates/evidence/rust-v8-rust-postfinal-locale-v7-sealed-campaign.json
candidates/evidence/rust-v8-vm-postfinal-locale-v7-sealed-campaign.json
candidates/evidence/rust-v8-zig-postfinal-locale-v7-sealed-campaign.json
```

## Verify the controller without running candidates

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/rust_v8_multi_candidate_campaign_postfinal_v7.py --self-test
```

The controller checks must be fully synthetic and in-memory. They
inherit the original malicious-input defenses, block every production
file, candidate worker, source audit, temporary locale, clock, and
performance or holdout input. A passing controller self-test is not a
passing family campaign.

Root may run one complete family only after freezing, committing, and
pushing this exact campaign source and protocol, the source-bound
32 MiB reader, the real passing Stage14 and Stage17 results, and the
genuine preserved Stage15 failure. Preserve and push each independent
passing family result separately. Until all three complete 22-stage
family results genuinely pass, full compatibility is **NOT QUALIFIED**,
and performance remains **NOT MEASURED**.
