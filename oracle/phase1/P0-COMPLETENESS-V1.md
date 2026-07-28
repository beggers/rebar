# Complete Python regular-expression compatibility baseline

This document freezes the standard of compatibility for a replacement that can
be used as `import rebar as re`. It records what unchanged Python actually
does; it does **not** claim that Rust, C, Zig, or any other replacement already
passes or runs faster.

The machine-readable, canonical inventory is
[`p0-completeness-v1.json`](p0-completeness-v1.json). The immutable
[`GOAL.md`](../../GOAL.md) has SHA-256
`e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`.
Every reference uses CPython **3.14.6**, executable SHA-256
`255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016`.

## The complete correctness baseline

All **13** separately identified suites have actual passing Python reference
evidence. Together they contain **31,237** frozen suite-case executions.
This is an honest sum of suite executions, not a claim that every pattern is
semantically unique.

| Python behavior checked | Frozen cases | Actual Python baseline |
| --- | ---: | --- |
| Original runnable upstream public methods | 151 | PASS |
| Ordinary public matching on text and bytes | 864 | PASS |
| Scanners and scanner callbacks | 1,024 | PASS |
| Memory-view matching and expansion | 768 | PASS |
| Buffer ownership and object lifetime | 1,024 | PASS |
| Comments, verbose patterns, and scanner tokenization | 2,854 | PASS |
| Public types, copying, identity, and serialization | 6,912 | PASS |
| Substitution, callbacks, and buffer behavior | 5,120 | PASS |
| Changing-size buffer behavior | 10,240 | PASS |
| Broad Python public behavior and real locales | 1,376 | PASS |
| Genuine, isolated Python subinterpreters | 128 | PASS |
| Python-defined PEP 688 buffer exporters | 264 | PASS |
| Actual shared-pattern threads and module-version checks | 512 | PASS |
| **Total separately frozen suite-case executions** | **31,237** | **PASS** |

The **32** module-version checks are already inside the **512** thread
cases. Historical subinterpreter versions and repeated upstream test methods
are not counted twice. Full-resource reference histories also do not inflate
the counted suite total. Reference processes independently reproduce their
complete frozen case vectors; candidate outcomes are **NOT MEASURED**.

## Account for every original Python test

Python's original source contains **165** named test methods: **152** public
methods and exactly **13** genuine private-implementation methods. The pinned
release build passes **151** runnable public methods. The remaining public
method, `ReTests.test_memory_leaks`, has its real upstream
`requires debug build` skip. It is neither a passing method nor a waived
public test. Debug-build coverage is **NOT MEASURED**.

The only named private waivers, in upstream source order, are:

1. `DebugTests.test_debug_flag`
2. `DebugTests.test_atomic_group`
3. `DebugTests.test_possesive_repeat_one`
4. `DebugTests.test_possesive_repeat`
5. `ImplementationTest.test_immutable`
6. `ImplementationTest.test_overlap_table`
7. `ImplementationTest.test_signedness`
8. `ImplementationTest.test_disallow_instantiation`
9. `ImplementationTest.test_deprecated_modules`
10. `ImplementationTest.test_case_helpers`
11. `ImplementationTest.test_dealloc`
12. `ImplementationTest.test_repeat_minmax_overflow_maxrepeat`
13. `ImplementationTest.test_sre_template_invalid_group_index`

They inspect CPython's private opcodes, compiler, `_sre`, object
implementation, or deprecated private modules. No public method, mismatch,
error, warning, callback, scanner, buffer, or reference failure is waived.

The independently frozen
[upstream test-accounting protocol](../cpython-3.14.6/UPSTREAM-ACCOUNTING-V5.md),
[full source-accounting manifest](../cpython-3.14.6/manifest-v5.json), and
[read-only upstream verifier](../../tools/verify_original_cpython_accounting_v1.py)
also preserve all **403** actual upstream corpus cases, all **11** external
correctness fixtures, and the separately authenticated support files.

## Keep all four original evidence histories distinct

| Actual history | What the independently recorded Python evidence establishes |
| --- | --- |
| Bounded original-suite V5 | The **151** counted runnable original public methods use the explicitly bounded **5,147**-item candidate-facing exercise. This is not an actual 2 GiB candidate test. |
| Full-resource original-suite V5 | Both Python references receive the genuine **2,147,483,648**-item allocation with a **42,949,672,960**-byte resource allowance. This does not establish a candidate result. |
| Independent full-resource original-suite V6 | A separate, genuine Python reference preserves the same original public-method identities without adding another 152 cases. |
| Expanded public-surface V19 | Both references preserve **1,376** cases, **64** real locale cases and **192** transitions per reference. Its authenticated parent is full-resource V5, never full-resource V6 or the bounded controller. |

Source paths, complete report hashes, role vectors, actual resource limits,
and the original source-ordered method identities are pinned in the
machine-readable inventory. Historical process IDs that were not recorded
remain **NOT CAPTURED**; none is invented.

## Authenticate the actual Python reference evidence

The general, scanner, and buffer references each have their own separately
published, two-process report and durable receipt:

| Reference | Cases | Compressed report SHA-256 | Receipt SHA-256 |
| --- | ---: | --- | --- |
| General public matching | 864 | `44fb033b4ce771e218e798f8a4b4b3dc87a939c1545a87c11fb2e307964c612f` | `9d9fe750460179539b534c113354ddd8d9c64ad2a4bd3672fe2691d974f509ce` |
| Scanner behavior | 1,024 | `bc543a66cbf2ba3436ea15b2e663e46aeef8205fe3144d4563ab7065fc8ebca4` | `50291aaa6be4dd8f50041c7b2d91b92df7848dcddb18323900dbe1b4c92fe3ba` |
| Buffer behavior | 768 | `7c6013c47c7640279e2fabed2b322d754153a04551062b8bf1669696aacdf43d` | `8272806b2aa5ff944d083cdac1885e4be17df3c729bb2663c1c310117d0f7ac2` |
| Python buffer exporters | 264 | `9ac916c57941a38daeecb3c0a724cbbffdfd54227dc28e8e2c1b471e3de8f8c2` | `a76eb84394a653ebae4476fa61fd4493fc49dc3c6bad71a00995355605c0d807` |
| Real simultaneous threads | 512 | `7a39bafee6a5ac46ee53c379054d953814d2094589738963f3852da14c6ed834` | `3483d19465685f44e0cae128483406a50cd9bb86f44910b5d3b0404a4d17aa76` |

The three general-reference baselines each record two genuinely separate
Python processes and the original full-precision seed. The buffer-exporter
reference records **528** actual case executions across both processes,
**728** buffer acquisitions and **728** releases, all **32** holder phases,
and all **40** deliberate callback exceptions. The thread reference records
**64** genuine thread starts and joins, **2,048** thread-side executions,
and **4,352** matching operations across both reference processes. The
`re.__version__` checks observe the actual string `2.2.1`; they do not
require a replacement imported as `re` to have the module name `re`.

The historical managed-buffer receipt authenticates its actual original
`.json` publication. The separately committed
[lossless managed-buffer archive index](../../docs/evidence/managed-buffer-lifetime-baseline-v1.archive.json),
SHA-256
`514a22347d62340cf6a122ff14415cf6acbac8fc16039f25109911b840680c69`,
bridges that **108,978,141**-byte original report, SHA-256
`8c1acb346f476be4f05edd3e7afa73c9a4196bdafa19c2b6f90259ce6b622b68`,
to its frozen lossless compressed archive, SHA-256
`1840d5c5faf0422cfaaae0e277cf5d9bc5ed954fe50beca3d9794b9fd33e5fba`.
Its genuine original receipt has SHA-256
`adb34ba45089983ac1857639995c51bdc3ae81e0656fa4b89fd5c0f72420b3ba`.
The index uses its actual pretty-printed source bytes; it is not a compact
canonical JSON record. Verification streams the compressed evidence and does
not rely on an untracked copy of the original large report.

## Complete public-obligation crosswalk

The original [version-one public matrix](../v1/P0.md) and
[version-two public matrix](../v2/P0.md) contain **38** and **45**
obligations respectively; version two retains all version-one obligations.
The canonical inventory individually maps all **45** inherited obligations,
**28** additional named obligations, and **34** readable summary mappings to
their actual evidence. All **73** inherited and additional obligations are
mapped. The two full-resource upstream histories may substantiate a mapping,
but their already-counted original methods are not added to the denominator.

Mapping includes text and bytes; compiled patterns and match objects; flags;
all matching, iteration, scanning, splitting, and replacement operations;
Unicode and locale behavior; captures and backreferences; verbose comments;
exact public errors and warnings; generic types; copying, weak references,
serialization, cache behavior, real Python buffer ownership and release;
genuine subinterpreters; and genuine simultaneous access to one compiled
pattern.

## Reproduce and interpret the gate

Use the pinned Python interpreter and the exact current source, canonical
inventory, and explanation SHA-256 values:

```text
sha256sum tools/verify_p0_completeness_v1.py \
  oracle/phase1/p0-completeness-v1.json \
  oracle/phase1/P0-COMPLETENESS-V1.md

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/verify_p0_completeness_v1.py \
  --self-test

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/verify_p0_completeness_v1.py \
  --verify --source-sha256 SOURCE_SHA256 \
  --document-sha256 DOCUMENT_SHA256 \
  --explanation-sha256 EXPLANATION_SHA256
```

The synthetic self-test must not read real evidence, start a reference,
import or run a candidate, execute a matcher, create a thread, sample a
clock, or open a final case. The actual verification independently checks
only already-published reference records, source hashes, case vectors,
deterministic archives, publication receipts, waiver accounting and complete
obligation mappings. It starts no new reference process or thread.

**Phase-one reference status: PASS. Candidate correctness: NOT MEASURED.
Candidate speed and memory: NOT MEASURED. Final benchmark and expanded
holdout: NOT GENERATED and NOT OPENED. Winner: NOT SELECTED.** Completing
and publishing this Python-only correctness phase does not authorize opening
the final comparison.
