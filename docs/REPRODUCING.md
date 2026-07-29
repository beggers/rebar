# Reproducing the frozen rebar experiment

This guide preserves the complete, source-pinned verification commands and
evidence inventory that were previously kept in the main README. All checks
below are source-only or read-only unless a command explicitly says otherwise.
The current results and charts remain in [the project README](../README.md);
experiment history remains in [the experiment log](EXPERIMENT-LOG.md).

## Evidence and reproduction

- [From-scratch Rust match-serialization source repair](../oracle/phase2/RUST-MATCH-PICKLE-SOURCE-REPAIR-V1.md), [complete combined-variant source contract](../oracle/phase2/rust-match-pickle-source-repair-v1.json), [complete first-party buffer-and-serialization Rust bridge](../candidates/rust/variants/buffer_shape_pickle_v1/py_bridge.c), and [archive-free serialization source verifier](../tools/apply_owned_rust_match_pickle_source_repair_v1.py); the same Rust family remains **NOT BUILT**, **NOT RUN**, and **NOT MEASURED**. The actual original-suite result is still **928** differences and **8,965** verified passes. Both ordinary and empty-environment gates pass without opening an archive or running an engine.
- [From-scratch Rust buffer and replacement source repair](../oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-REPAIR-V1.md), [complete frozen source-repair contract](../oracle/phase2/rust-buffer-shape-source-repair-v1.json), [full first-party Rust bridge variant](../candidates/rust/variants/buffer_shape_v1/py_bridge.c), and [archive-free repair verifier](../tools/apply_owned_rust_buffer_shape_source_repair_v1.py); the same Rust engine family remains **NOT BUILT**, **NOT RUN**, and **NOT MEASURED**. The last complete test still records **928** differences and **8,965** explicitly verified passes. Both ordinary and empty-environment source gates pass without reading mutable documentation, failure archives, or hidden tests.
- [Frozen Python compatibility tests](../oracle/phase1/P0-COMPLETENESS-V1.md), [all 31,237 test cases](../oracle/phase1/p0-completeness-v1.json), and [independent test verifier](../tools/verify_p0_completeness_v1.py).
- [Python's original two-billion-character test protocol](../oracle/phase1/P0-LARGE-INPUT-INDEXING-V1.md), [all 32 separately counted large-input source observations](../oracle/phase1/p0-large-input-indexing-v1.json), and [physically isolated upstream large-input verifier](../tools/verify_large_input_indexing_v1.py); both actual upstream methods require **2,147,483,648** characters, with the substitution returning **2,147,483,649** replacements. Historical Python references were allowed **42,949,672,960** bytes, but this source verifier allocates no large text and does not run a reference. The actual candidate-test limit is **5,147** characters, so both full-size candidate checks remain **NOT RUN**. All **330** safety controls pass and **28** prohibited effects are physically blocked. The separate **32** source observations are not added to the original **31,237**, the **50** signatures, or the other **32** public-import observations.
- [Frozen actual-public-import protocol](../oracle/phase1/P0-PUBLIC-ENTRYPOINT-IMPORT-V1.md), [all 32 separately counted public-module observations](../oracle/phase1/p0-public-entrypoint-import-v1.json), and [physically isolated public-entrypoint verifier](../tools/verify_public_entrypoint_import_v1.py); the real Zig-backed entrypoint remains **FAIL**, its missing `__version__` is preserved, **191** safety controls pass, **33** forbidden effects are physically blocked, and no candidate, Python regular-expression engine, native library, or holdout is loaded. These **32** observations are not added to either the original **31,237** or the separate **50** signature checks.
- [Separately frozen public callable signature checks](../oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md), [all 50 additional function, pattern, match, and scanner cases](../oracle/phase1/p0-callable-introspection-v1.json), and [independent source-only verifier](../tools/verify_python_re_callable_introspection_v1.py); the original **31,237** cases are unchanged, and **two** separate Python reference processes passed all **50** additional checks. Candidate signature checks have **NOT RUN**.
- [Actual 96-case candidate-context Python reference falsification](../oracle/phase1/evidence/public-type-candidate-context-falsification-v1.json); the original public-type helper produces `__main__` when run as a script and its qualified module name when imported by a candidate worker. Pinned Python alone reproduces all **96** differences. Preserve all **31,237** original cases, the genuine C subclass-equality failure, and every recorded Zig failure.
- [Frozen recovery-safe same-context Python reference](../oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md), [complete corrected-reference contract](../oracle/phase1/p0-public-type-reference-context-v1.json), and [independently verified two-worker reference controller](../tools/verify_owned_public_type_reference_context_v1.py); two actual Python workers each pass all **6,912** unchanged public-type cases and preserve all **96** original case IDs. Existing replacement runners still bind the rejected original reference and remain **BLOCKED** until a separately frozen successor consumes the corrected reference.
- [Complete corrected two-process Python reference](../oracle/phase1/evidence/public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0.json.gz) and [independently durable corrected-reference receipt](../oracle/phase1/evidence/public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0-publication-receipt.json); both actual workers pass every one of the **6,912** cases, produce the identical full-reference SHA-256 `6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2`, and retain all **96** previously falsified cases. Reference **PASS** and publication **PASS** are checked separately. No candidate or holdout ran.
- [Corrected shared six-family test producer](../oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md), [complete corrected producer contract](../oracle/phase2/six-family-p0-producer-v4.json), and [independent original-suite test producer](../tools/run_owned_six_family_original_p0_producer_v4.py); preserve all **31,237** original cases, both Python reference digests, and the **six** independently written engine designs with their **25** separate source files. This source inventory is not a claim that six engines can run the suite.
- [Corrected C-only original-suite protocol](../oracle/phase2/P0-CANDIDATE-PROTOCOL-V10.md), [complete source-pinned C-only contract](../oracle/phase2/p0-candidate-protocol-v10.json), [isolated C-only worker](../tools/run_frozen_p0_candidate_worker_v8.py), and [corrected C-only runner](../tools/run_frozen_p0_candidate_v10.py); the source accepts exactly **one** family, preserves all **31,237** original cases and the corrected Python reference, but has not safely activated the new C engine. Actual C matching has **NOT RUN**. Rust, Zig, C++, Go, and Fortran cannot run through this C-only worker.
- [Recovery-safe Rust-only original-suite protocol](../oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V7.md), [complete frozen Rust-only contract](../oracle/phase2/repaired-rust-original-campaign-v7.json), and [independently repaired Rust-only runner](../tools/run_owned_repaired_rust_original_campaign_v7.py); all **13** genuine workers actually completed the unchanged **31,237** original cases, preserving **928** actual compatibility differences, **8,965** verified passing checks, **zero** infrastructure failures, and all four restored original file identities. The runner's version-43 graph is its historical source-freeze anchor; it is not the current graph. Candidate correctness: **FAIL**.
- [Actual complete corrected Rust failure archive](../oracle/phase2/evidence/repaired-rust-original-campaign-v7-rust-phase2-v13-rust-pattern-repr-original-p0-failures.json.gz) and [separately durable full-campaign and four-file recovery receipt](../oracle/phase2/evidence/repaired-rust-original-campaign-v7-rust-phase2-v13-rust-pattern-repr-original-p0-failures-publication-receipt.json); the result has **13** distinct completed worker processes, **928** real differences, and **zero** runner failures. Receipt **PASS** means only durable publication of the candidate **FAIL**. The two independently durable result files raise authenticated evidence and history lower bounds to **168 / 173**; the full-size candidate tests, runtime non-delegation, and speed remain unproven.
- [Independent Zig-only original-suite protocol](../oracle/phase2/ZIG-ORIGINAL-P0-CANDIDATE-PROTOCOL-V1.md), [complete Zig-only worker and compiler contract](../oracle/phase2/zig-original-p0-candidate-protocol-v1.json), [isolated first-party Zig worker](../tools/run_frozen_zig_original_p0_candidate_worker_v1.py), and [separate first-party Zig controller](../tools/run_frozen_zig_original_p0_candidate_v1.py); all eight source-only gates authenticate the independent Zig parser, C bridge, official compiler, the unchanged **31,237** original cases, both corrected Python references, and the **32** separate public-import checks. The compiler has **NOT RUN**, the engine has **NOT BEEN ACTIVATED**, and actual Zig matching has **NOT RUN**.
- [Preserved previous Rust-only original-suite protocol](../oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V6.md), [preserved source-pinned Rust contract](../oracle/phase2/repaired-rust-original-campaign-v6.json), and [preserved first Rust-only runner](../tools/run_owned_repaired_rust_original_campaign_v6.py); its actual one-time helper failure and unreported historical build-archive access remain unchanged.
- [Actual first corrected Rust controller failure](../oracle/phase2/evidence/repaired-rust-original-campaign-v6-rust-phase2-v13-rust-pattern-repr-original-p0-entry-failure.json) and [independent actual build-archive and helper-mismatch observation](../oracle/phase2/evidence/repaired-rust-original-campaign-v6-rust-phase2-v13-rust-pattern-repr-original-p0-entry-failure-observation.json); exactly **one** historical version-6 controller invocation fails before any candidate worker, native change, recovery journal, matching archive, or receipt. It does inflate **one** historical Rust build archive, which the frozen controller omits from its effect ledger. Matching and case differences for this historical version-6 attempt remain **NOT MEASURED**; they are not the separately recorded version-7 result.
- [Unapplied first-party Zig scanner correction](../oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-REPAIR-V3.md), [complete frozen Zig correction contract](../oracle/phase2/zig-scanner-phrase-source-repair-v3.json), and [source-only Zig correction verifier](../tools/apply_owned_zig_scanner_phrase_source_repair_v3.py); precisely **64** of the original **1,024** scanner cases identify the construction defect. The corrected Zig source has **NOT BEEN APPLIED**, its matching has **NOT RUN**, and its performance is **NOT MEASURED**.
- [Independently reproduced two-process Python signature reference](../oracle/phase1/CALLABLE-INTROSPECTION-REFERENCE-V2.md), [exact independently isolated reference and publication contract](../oracle/phase1/callable-introspection-reference-v2.json), and [source-pinned Python reference controller](../tools/run_owned_callable_introspection_reference_v2.py); both actual reference workers passed and independently produced the same complete **50**-observation result.
- [Complete actual Python signature-reference archive](../oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6.json.gz) and [separately durable two-worker reference receipt](../oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6-publication-receipt.json); reference **PASS** means both actual Python workers agreed on every additional check. The separate durable publication also passed.
- [First-party engine ownership and no-wrapping source audit](../oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md), [exact six-family source inventory](../oracle/phase2/candidate-independence-v2.json), and [source verifier](../tools/audit_candidate_independence_v2.py); independent matching-engine ownership passes, but a complete execution-time no-delegation audit remains **NOT ESTABLISHED**.
- [Independent Zig scanner-capture repair](../oracle/phase2/ZIG-SCANNER-CAPTURE-SOURCE-REPAIR-V1.md), [single-block private-snapshot contract](../oracle/phase2/zig-scanner-capture-source-repair-v1.json), and [source-pinned first-party repair tool](../tools/apply_owned_zig_scanner_capture_source_repair_v1.py); the repair was independently applied to both private native builds.
- [First-party correction for the observed Zig scanner failure](../oracle/phase2/ZIG-SCANNER-CAPTURE-SOURCE-REPAIR-V2.md), [exact corrected private-bridge contract](../oracle/phase2/zig-scanner-capture-source-repair-v2.json), and [independently owned source verifier](../tools/apply_owned_zig_scanner_capture_source_repair_v2.py); the corrected engine was independently built twice and its subsequent complete test reduced observed Zig differences from **2,172** to **1,764**.
- [Previous reproducible independent Zig build protocol](../oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V11.md), [exact private two-build contract](../oracle/phase2/zig-scanner-source-build-v11.json), and [first-party Zig build verifier](../tools/reproduce_owned_zig_scanner_source_build_v11.py); both previous native outputs build identically. Their later complete matching test recorded **2,172** differences.
- [Current corrected from-scratch Zig build protocol](../oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V12.md), [exact independent private-build contract](../oracle/phase2/zig-scanner-source-build-v12.json), and [source-pinned first-party Zig build verifier](../tools/reproduce_owned_zig_scanner_source_build_v12.py); two independent, identical corrected builds and all **26** actual compiler and inspection processes succeeded. The subsequent complete compatibility test recorded **1,764** differences.
- [Complete actual corrected first-party Zig build evidence](../oracle/phase2/evidence/native-source-build-v12-zig-phase2-v12-zig-scanner-v2.json.gz) and [separately durable corrected Zig build receipt](../oracle/phase2/evidence/native-source-build-v12-zig-phase2-v12-zig-scanner-v2-publication-receipt.json); two distinct private phases produce identical matching engines and bridges without external packages or candidate matching tests.
- [Original two-file Zig activation and exact-inode recovery](../oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V6.md), [frozen dual-role safety contract](../oracle/phase2/verified-native-activation-v6.json), and [original Zig loading and recovery tool](../tools/activate_verified_native_candidate_v6.py); its nine-field safety check rejected genuine seven-field records for the unchanged original files before any engine loaded or matching test ran.
- [Corrected Zig file-owner verification and safe recovery](../oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V7.md), [exact descriptor-verification contract](../oracle/phase2/verified-native-activation-v7.json), and [independently verified first-party activation source](../tools/activate_verified_native_candidate_v7.py); the actual corrected campaign restored both original engine-file inodes before publishing its matching failures.
- [Complete original Python tests for repaired Zig](../oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V1.md), [exact 13-group original-suite and safe-restoration contract](../oracle/phase2/repaired-zig-original-campaign-v1.json), and [independent repaired-Zig original-suite controller](../tools/run_owned_repaired_zig_original_campaign_v1.py); all 31,237 original checks remain frozen, and the first controller attempt stopped during setup before any candidate test started.
- [Corrected complete original Python tests for repaired Zig](../oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V2.md), [exact original-suite and preserved-failure contract](../oracle/phase2/repaired-zig-original-campaign-v2.json), and [corrected first-party Zig correctness controller](../tools/run_owned_repaired_zig_original_campaign_v2.py); all **13** groups actually ran, revealing **2,172** matching differences and **zero** infrastructure failures. The [complete lossless matching-failure archive](../oracle/phase2/evidence/repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-original-p0-failures.json.gz) and [separate durable publication receipt](../oracle/phase2/evidence/repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json) preserve every worker and both restored original files.
- [Recovery-safe full Python test for the newly built first-party Zig engine](../oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V3.md), [exact actual-build, original-case, and safe-restoration contract](../oracle/phase2/repaired-zig-original-campaign-v3.json), and [independently frozen corrected Zig original-suite controller](../tools/run_owned_repaired_zig_original_campaign_v3.py); all **13** actual workers completed the unchanged **31,237** checks, preserving **1,764** genuine differences, **3,711** verified passing checks, and **zero** infrastructure failures.
- [Complete corrected Zig matching-failure archive](../oracle/phase2/evidence/repaired-zig-original-campaign-v3-zig-phase2-v12-zig-scanner-v2-original-p0-failures.json.gz) and [separate durable matching and exact-recovery receipt](../oracle/phase2/evidence/repaired-zig-original-campaign-v3-zig-phase2-v12-zig-scanner-v2-original-p0-failures-publication-receipt.json); receipt **PASS** verifies durable preservation and restoration of both original native-file inodes. The candidate itself remains **FAIL**.
- [First repaired-Zig setup failure](../oracle/phase2/ZIG-CAMPAIGN-PREFLIGHT-FAILURE-V1.md), [complete pinned traceback and failure contract](../oracle/phase2/zig-campaign-preflight-failure-v1.json), and [failure preservation verifier](../tools/preserve_owned_zig_campaign_preflight_failure_v1.py); one controller exited 1 before any Zig test worker began. Its exact traceback is preserved in the [compressed original-failure archive](../oracle/phase2/evidence/zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-original-p0-failures.json.gz) and [separate durable publication receipt](../oracle/phase2/evidence/zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json). Receipt success verifies preservation, not a successful Zig test.
- [Corrected original Python test producer](../tools/run_owned_six_family_original_p0_producer_v3.py), [unchanged original-test and first-party ownership protocol](../oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md), and [exact source-pinned contract](../oracle/phase2/six-family-p0-producer-v3.json); both real Python reference processes and all 31,237 cases are preserved.
- [Corrected complete original-suite protocol](../oracle/phase2/P0-CANDIDATE-PROTOCOL-V9.md), [exact case and worker inventory](../oracle/phase2/p0-candidate-protocol-v9.json), [corrected isolated-suite worker](../tools/run_frozen_p0_candidate_worker_v7.py), and [complete 13-suite runner](../tools/run_frozen_p0_candidate_v9.py); all 13 repaired C candidate workers ran and preserved their complete results.
- [Frozen correction for the original C test coordinator](../oracle/phase2/P0-V9-LIVE-CONTEXT-ADAPTER-V1.md), [exact immutable original-worker adapter contract](../oracle/phase2/p0-v9-live-context-adapter-v1.json), and [independently verified original-worker adapter](../tools/run_owned_frozen_p0_v9_live_context_adapter_v1.py); all original corrected-suite worker records are preserved.
- [Recovery-safe corrected C campaign rules](../oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V2.md), [exact restoration and full-test contract](../oracle/phase2/repaired-c-original-campaign-v2.json), and [complete recovery-safe original-suite controller](../tools/run_owned_repaired_c_original_campaign_v2.py); its one genuine runner failure and exact restoration are independently preserved.
- [Complete repaired C original-suite rerun rules](../oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V3.md), [exact original-worker and recovery contract](../oracle/phase2/repaired-c-original-campaign-v3.json), and [safe complete-suite controller](../tools/run_owned_repaired_c_original_campaign_v3.py); all 13 original workers completed with 1,262 preserved semantic mismatches and zero infrastructure failures.
- [Recovery-safe original Python tests for the rebuilt C engine](../oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V4.md), [frozen 31,237-check C test and recovery contract](../oracle/phase2/repaired-c-original-campaign-v4.json), and [independently pinned complete-suite controller](../tools/run_owned_repaired_c_original_campaign_v4.py); all **13** real workers completed, revealing **1,230** matching differences with **zero** infrastructure failures and exact original-file restoration.
- [Complete rebuilt C original-suite failure archive](../oracle/phase2/evidence/repaired-c-original-campaign-v4-c-phase2-v15-c-pickle-original-p0-failures.json.gz) and [separate durable C matching and recovery receipt](../oracle/phase2/evidence/repaired-c-original-campaign-v4-c-phase2-v15-c-pickle-original-p0-failures-publication-receipt.json); the receipt independently proves all **13** completed original groups, **1,230** actual differences, **7,325** verified passing checks, the restored original native file, and **zero** worker or execution failures. Receipt success means successful preservation of a failed candidate.
- [Frozen first-party C repair](../oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V1.md), [exact repair and preserved evidence](../oracle/phase2/first-party-source-repair-v1.json), and [private-snapshot-only repair tool](../tools/apply_owned_first_party_source_repair_v1.py); the original checked-in engine, all historical results, and the sealed final comparison remain unchanged.
- [Evidence-backed C match-pickling repair](../oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V2.md), [exact private-source and original-evidence contract](../oracle/phase2/first-party-source-repair-v2.json), and [first-party C source-repair verifier](../tools/apply_owned_first_party_source_repair_v2.py); all 32 observed protocol-0/1 failures and all 64 higher-protocol observations are preserved. The later V15 experiment built the repaired source twice; its complete matching test recorded **1,230** differences.
- [Separate first-party Rust repair](../oracle/phase2/RUST-SOURCE-REPAIR-V1.md), [exact Rust repair and preserved evidence](../oracle/phase2/rust-source-repair-v1.json), and [private Rust-snapshot-only repair tool](../tools/apply_owned_rust_source_repair_v1.py); the existing Rust engine and all its previous failures remain unchanged.
- [Independent Rust public-compatibility repair](../oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V1.md), [exact three-block private-source contract](../oracle/phase2/rust-public-contract-source-repair-v1.json), and [first-party Rust public-source verifier](../tools/apply_owned_rust_public_contract_source_repair_v1.py); the repaired source was independently applied to both private builds. Its later complete compatibility test found **1,087** differences.
- [First-party correction for the observed Rust flag-display failure](../oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V2.md), [exact private-source and genuine-Python flag contract](../oracle/phase2/rust-public-contract-source-repair-v2.json), and [independently written Rust repair verifier](../tools/apply_owned_rust_public_contract_source_repair_v2.py); all six upstream assertions and **5,128** Python flag values agree. Its independently rebuilt engine completed all **13** compatibility groups and recorded **1,036** differences.
- [First actual remaining Rust compiled-pattern representation correction](../oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V3.md), [exact actual mismatch and preserved standalone-flag contract](../oracle/phase2/rust-public-contract-source-repair-v3.json), and [source-pinned first-party Rust representation verifier](../tools/apply_owned_rust_public_contract_source_repair_v3.py); the corrected adapter has been privately applied in both actual independent Rust builds while all **5,128** standalone flag observations remain unchanged. Corrected matching has **NOT RUN**.
- [Independently reproduced builds of the next corrected first-party Rust engine](../oracle/phase2/RUST-PATTERN-REPR-SOURCE-BUILD-V13.md), [exact nine-source, two-phase, offline build contract](../oracle/phase2/rust-pattern-repr-source-build-v13.json), and [source-pinned first-party Rust build controller](../tools/reproduce_owned_rust_pattern_repr_source_build_v13.py); all **28** real compiler and inspection processes completed, and both separate native engines and bridges are byte-identical. The corrected matching test has **NOT RUN**.
- [Complete actual corrected first-party Rust build archive](../oracle/phase2/evidence/native-source-build-v13-rust-phase2-v13-rust-pattern-repr-original-p0.json.gz) and [separate durable two-phase Rust build receipt](../oracle/phase2/evidence/native-source-build-v13-rust-phase2-v13-rust-pattern-repr-original-p0-publication-receipt.json); actual build **PASS** establishes two reproducible offline first-party builds, not a passing candidate.
- [Independently reproducible corrected Rust build rules](../oracle/phase2/RUST-FLAG-SOURCE-BUILD-V12.md), [exact first-party toolchain and two-phase build contract](../oracle/phase2/rust-flag-source-build-v12.json), and [offline corrected Rust build verifier](../tools/reproduce_owned_rust_flag_source_build_v12.py); both independent builds and all **28** real compiler and inspection processes succeeded. A separately recorded full matching run finds **1,036** differences.
- [Actual corrected Rust two-build evidence](../oracle/phase2/evidence/native-source-build-v12-rust-phase2-v12-rust-flag-original-p0.json.gz) and [separately durable corrected-build receipt](../oracle/phase2/evidence/native-source-build-v12-rust-phase2-v12-rust-flag-original-p0-publication-receipt.json); the receipt proves **28** real processes, two identical first-party builds, the corrected adapter, no outside matcher, and **zero** candidate tests. Its **PASS** means the build succeeded, not that the replacement passes Python's tests.
- [Reproducible first-party C build rules](../oracle/phase2/NATIVE-SOURCE-BUILD-V8.md), [exact build inventory](../oracle/phase2/native-source-build-v8.json), and [independent two-build verifier](../tools/reproduce_owned_native_source_build_v8.py).
- [Reproducible offline build rules for both C repairs](../oracle/phase2/C-PICKLE-SOURCE-BUILD-V12.md), [exact two-phase source-build contract](../oracle/phase2/c-pickle-source-build-v12.json), and [independent repaired C native-build verifier](../tools/reproduce_owned_c_pickle_source_build_v12.py); its 14 compiler and inspection steps have not yet run.
- [Independently verified C build rules](../oracle/phase2/C-PICKLE-SOURCE-BUILD-V13.md), [exact historical-evidence and two-build contract](../oracle/phase2/c-pickle-source-build-v13.json), and [first-party repaired C build verifier](../tools/reproduce_owned_c_pickle_source_build_v13.py); the frozen two-build, 14-process experiment preserves its original 141-file evidence history but has **NOT YET RUN**.
- [Historical independently verified C build rules](../oracle/phase2/C-PICKLE-SOURCE-BUILD-V14.md), [exact 143-file evidence and two-build contract](../oracle/phase2/c-pickle-source-build-v14.json), and [first-party corrected C build verifier](../tools/reproduce_owned_c_pickle_source_build_v14.py); this specific historical two-build, 14-step experiment has **NOT RUN**. The later V15 C build and its **1,230**-difference test are recorded separately.
- [Current C build including both Rust and Zig results](../oracle/phase2/C-PICKLE-SOURCE-BUILD-V15.md), [exact 145-file historical evidence and two-build contract](../oracle/phase2/c-pickle-source-build-v15.json), and [independent first-party C source builder](../tools/reproduce_owned_c_pickle_source_build_v15.py); both builds and all **14** real compiler and inspection steps completed and produced identical native engines. Their subsequent original matching test found **1,230** differences.
- [Complete actual first-party C15 build evidence](../oracle/phase2/evidence/native-source-build-v15-c-phase2-v15-c-pickle-original-p0.json.gz) and [independently durable C15 build receipt](../oracle/phase2/evidence/native-source-build-v15-c-phase2-v15-c-pickle-original-p0-publication-receipt.json); two distinct private builds produce the same native C engine without an external regular-expression package. A successful build is not a passing compatibility result.
- [Actual matching first-party C builds](../oracle/phase2/evidence/native-source-build-v8-c-phase2-v8.json.gz) and [independent build receipt](../oracle/phase2/evidence/native-source-build-v8-c-phase2-v8-publication-receipt.json); two private builds produced identical native binaries.
- [Current reproducible independent Rust build rules](../oracle/phase2/NATIVE-SOURCE-BUILD-V11.md), [exact dual-repair Rust build inventory](../oracle/phase2/native-source-build-v11.json), and [offline two-build verifier](../tools/reproduce_owned_native_source_build_v11.py); both first-party repaired builds match exactly and use no external regex package. Their later complete matching test recorded **1,087** differences.
- [Complete original Python tests for repaired Rust](../oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V2.md), [exact four-file recovery and original-suite contract](../oracle/phase2/repaired-rust-original-campaign-v2.json), and [first-party Rust correctness controller](../tools/run_owned_repaired_rust_original_campaign_v2.py); all 13 groups and 31,237 checks are frozen against the actual repaired Rust implementation. The matching campaign has **NOT YET RUN**.
- [Safely recoverable complete Rust tests](../oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V3.md), [exact recovery and original-suite contract](../oracle/phase2/repaired-rust-original-campaign-v3.json), and [first-party recoverable Rust controller](../tools/run_owned_repaired_rust_original_campaign_v3.py); all **13** workers actually completed and found **1,087** differences with **zero** infrastructure failures. The [complete compressed Rust matching-failure archive](../oracle/phase2/evidence/repaired-rust-original-campaign-v3-rust-phase2-v11-rust-dual-overlay-original-p0-failures.json.gz) and [separate durable recovery and publication receipt](../oracle/phase2/evidence/repaired-rust-original-campaign-v3-rust-phase2-v11-rust-dual-overlay-original-p0-failures-publication-receipt.json) prove restoration of all four original files.
- [Complete original Python test for the newly rebuilt Rust engine](../oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V4.md), [exact corrected-source, 31,237-case, and four-file recovery contract](../oracle/phase2/repaired-rust-original-campaign-v4.json), and [independent recovery-safe corrected Rust controller](../tools/run_owned_repaired_rust_original_campaign_v4.py); all **13** original workers actually completed with **1,036** differences, **8,965** verified passing checks, **zero** infrastructure failures, and exact restoration of all four original files.
- [Complete corrected Rust matching-failure archive](../oracle/phase2/evidence/repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-original-p0-failures.json.gz) and [separately durable full-test and recovery receipt](../oracle/phase2/evidence/repaired-rust-original-campaign-v4-rust-phase2-v12-rust-flag-original-p0-failures-publication-receipt.json); receipt **PASS** records durable publication of the actual Rust matching **FAIL** and exact original-file restoration.
- [Safe reversible C-engine loading rules](../oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V5.md), [exact recovery and build checks](../oracle/phase2/verified-native-activation-v5.json), and [first-party engine recovery tool](../tools/activate_verified_native_candidate_v5.py); the original native file was restored exactly.
- [Complete repaired-engine Python test rules](../oracle/phase2/P0-CANDIDATE-PROTOCOL-V8.md), [all original groups and seeds](../oracle/phase2/p0-candidate-protocol-v8.json), [isolated original-test worker](../tools/run_frozen_p0_candidate_worker_v6.py), and [complete test and recovery recorder](../tools/run_frozen_p0_candidate_v8.py); all **31,237** original cases remain unchanged.
- [Fail-safe full C test rules](../oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V1.md), [exact recovery and test contract](../oracle/phase2/repaired-c-original-campaign-v1.json), and [recovered original-test runner](../tools/run_owned_repaired_c_original_campaign_v1.py); the original native file was restored before the genuine failure was recorded.
- [All 13 repaired C test-runner failures](../oracle/phase2/evidence/frozen-p0-candidate-v8-c-phase2-v8-original-p0-failures.json.gz) and [complete original-test receipt](../oracle/phase2/evidence/frozen-p0-candidate-v8-c-phase2-v8-original-p0-failures-publication-receipt.json); **12** groups rejected genuine Python-compatible public type names and **1** could not decode its archived reference.
- [Independently recovered C failure and original-file proof](../oracle/phase2/evidence/repaired-c-original-campaign-v1-c-phase2-v8-original-p0-failures.json.gz) and [separate durable recovery receipt](../oracle/phase2/evidence/repaired-c-original-campaign-v1-c-phase2-v8-original-p0-failures-publication-receipt.json); matching was **NOT MEASURED**.
- [Complete original-test rules](../oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V1.md), [frozen test inventory](../oracle/phase2/six-family-p0-campaign-v1.json), and [reproducible candidate test runner](../tools/run_owned_six_family_original_p0_campaign_v1.py).
- [Lossless original-test recording rules](../oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V2.md), [frozen streaming-test inventory](../oracle/phase2/six-family-p0-campaign-v2.json), and [complete streaming test recorder](../tools/run_owned_six_family_original_p0_campaign_v2.py); the original tests, first-party engines, and preserved Go failure remain unchanged.
- [Complete first-party C++ failure](../oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-cpp-phase2-v1-failures.json.gz) and [independent publication and recovery receipt](../oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-cpp-phase2-v1-failures-publication-receipt.json).
- [Observed first-party C++ public-argument correction](../oracle/phase2/CPP-PUBLIC-ARGUMENT-SOURCE-REPAIR-V1.md), [exact original and corrected public-adapter contract](../oracle/phase2/cpp-public-argument-source-repair-v1.json), and [independent source-only argument verifier](../tools/apply_owned_cpp_public_argument_source_repair_v1.py); all **336** Python argument examples and **three** signatures are preserved, but corrected compilation and matching have **NOT RUN**.
- [Complete first-party Go matching failure](../oracle/phase2/evidence/owned-six-family-original-p0-campaign-v2-go-phase2-v2-failures.json.gz) and [independent streamed-result and native-recovery receipt](../oracle/phase2/evidence/owned-six-family-original-p0-campaign-v2-go-phase2-v2-failures-publication-receipt.json); all **13** groups, **4,518** genuine differences, **4** separate worker failures, and both restored native files are preserved.
- [Observed first-party Go Unicode group-name correction](../oracle/phase2/GO-UNICODE-NAME-SOURCE-REPAIR-V1.md), [exact byte-accurate original and corrected Go source contract](../oracle/phase2/go-unicode-name-source-repair-v1.json), and [independent source-only Go repair verifier](../tools/apply_owned_go_unicode_name_source_repair_v1.py); the corrected source is derived only in memory, and its build and compatibility have **NOT RUN**.
- [Rejected historical corrected-Go build rules](../oracle/phase2/GO-UNICODE-SOURCE-BUILD-V13.md), [preserved V13 private-source contract](../oracle/phase2/go-unicode-source-build-v13.json), and [unexecuted V13 Go build controller](../tools/reproduce_owned_go_unicode_source_build_v13.py); source-only verification passed, but independent review rejected its lossy failed-process accounting and missing actual process IDs. Do not execute the V13 build; corrected Go compilation and matching have **NOT RUN**.
- [Independently recorded Go V13 process-accounting rejection](../docs/evidence/go-v13-process-accounting-rejection-v1.json); preserves the exact immutable V13 source and failure-site excerpt hashes without running a Go build.
- [Complete Go result-recording failure](../oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-go-phase2-v1-publication-failure-evidence.json.gz), [independent evidence receipt](../oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-go-phase2-v1-publication-failure-evidence-publication-receipt.json), and [reproducible failure-preservation tool](../tools/preserve_owned_go_campaign_publication_failure_v1.py). This is not a Go compatibility result.
- [Complete corrected C runner failure](../oracle/phase2/evidence/repaired-c-original-campaign-v2-c-phase2-v9-original-p0-failures.json.gz) and [independent durable failure and restoration receipt](../oracle/phase2/evidence/repaired-c-original-campaign-v2-c-phase2-v9-original-p0-failures-publication-receipt.json); the genuine runner error occurred before any matching test started.
- [Complete repaired C compatibility evidence](../oracle/phase2/evidence/repaired-c-original-campaign-v3-c-phase2-v10-live-original-p0-failures.json.gz), [independent safe-restoration receipt](../oracle/phase2/evidence/repaired-c-original-campaign-v3-c-phase2-v10-live-original-p0-failures-publication-receipt.json), [all 13 original worker reports](../oracle/phase2/evidence/frozen-p0-candidate-v9-c-phase2-v10-live-original-p0-failures.json.gz), and [original-suite aggregate receipt](../oracle/phase2/evidence/frozen-p0-candidate-v9-c-phase2-v10-live-original-p0-failures-publication-receipt.json); eight complete groups pass, five retain 1,262 genuine differences, and no infrastructure failure occurred.
- [Actual independent repaired Zig builds](../oracle/phase2/evidence/native-source-build-v11-zig-phase2-v11-zig-scanner.json.gz) and [complete native build and durable publication receipt](../oracle/phase2/evidence/native-source-build-v11-zig-phase2-v11-zig-scanner-publication-receipt.json); exactly 26 genuine processes produce two identical first-party engine and bridge binaries without testing matching or measuring speed.
- [Actual independent repaired Rust builds](../oracle/phase2/evidence/native-source-build-v11-rust-phase2-v11-rust-dual-overlay.json.gz) and [complete offline-build and durable publication receipt](../oracle/phase2/evidence/native-source-build-v11-rust-phase2-v11-rust-dual-overlay-publication-receipt.json); exactly 28 genuine processes produce two identical dependency-free Rust engines and bridges without testing matching or measuring speed.
- [Current compact overall-results graph](../docs/evidence/candidate-current-overview-v50.svg), [complete current graph inputs](../docs/evidence/candidate-current-overview-v50.inputs.json), [current machine-readable candidate results](../docs/evidence/candidate-current-overview-v50.json), and [reproducible current graph generator](../tools/render_candidate_current_overview_v50.py); the actual Rust result remains **928** differences and **8,965** explicitly verified passes across **13** completed groups. Its combined buffer-and-serialization source remains **NOT BUILT** and **NOT RUN**. Six from-scratch designs, the original **31,237** cases, separately counted **50**, **32**, and **32** checks, and the unopened **4,194,304**-case final comparison remain visible. No replacement is qualified; speed is **NOT MEASURED**.
- [Historical version-49 compact results graph](../docs/evidence/candidate-current-overview-v49.svg), [historical version-49 graph inputs](../docs/evidence/candidate-current-overview-v49.inputs.json), [historical version-49 machine-readable results](../docs/evidence/candidate-current-overview-v49.json), and [historical reproducible graph generator](../tools/render_candidate_current_overview_v49.py); the actual Rust result was **928** differences and **8,965** explicitly verified passes, and the separately frozen buffer variant had not been built or run.
- [Historical Rust-failure and overall-results graph](../docs/evidence/candidate-current-overview-v48.svg), [historical version-48 graph inputs](../docs/evidence/candidate-current-overview-v48.inputs.json), [historical machine-readable full-suite Rust and candidate results](../docs/evidence/candidate-current-overview-v48.json), and [historical graph generator](../tools/render_candidate_current_overview_v48.py); the actual Rust engine fails **928** of its observed comparisons across **13** completed original groups, with **zero** worker failures. Both genuine full-size Python requirements and **32** boundary-source observations remain separate from the **31,237** original cases, **50** signature cases, and **32** public-import observations. No candidate is qualified, the final comparison is unopened, and speed is **NOT MEASURED**.
- [Historical two-billion-character and overall-results graph](../docs/evidence/candidate-current-overview-v47.svg), [historical version-47 graph inputs](../docs/evidence/candidate-current-overview-v47.inputs.json), [historical machine-readable boundary and candidate results](../docs/evidence/candidate-current-overview-v47.json), and [historical graph generator](../tools/render_candidate_current_overview_v47.py); the **two** genuine full-size Python requirements and **32** boundary-source observations remain separate from the **31,237** original cases, **50** signature cases, and **32** public-import observations. Three separately frozen C, Rust, and Zig runner sources do not imply any passing candidate.
- [Historical independently written Zig and overall-results graph](../docs/evidence/candidate-current-overview-v46.svg), [historical version-46 graph inputs](../docs/evidence/candidate-current-overview-v46.inputs.json), [historical machine-readable candidate and public-import results](../docs/evidence/candidate-current-overview-v46.json), and [historical graph generator](../tools/render_candidate_current_overview_v46.py); **three** separately frozen C, Rust, and Zig runner-source paths do not imply a runnable, matching, or qualified engine. Preserve all **31,237** original cases, the separate **50** and **32** public checks, the historical Zig and Rust failures, **zero** qualified replacements, and the expanded unopened comparison. Speed: **NOT MEASURED**.
- [Historical independently audited public-import and candidate graph](../docs/evidence/candidate-current-overview-v45.svg), [historical graph inputs](../docs/evidence/candidate-current-overview-v45.inputs.json), [historical machine-readable public and candidate results](../docs/evidence/candidate-current-overview-v45.json), and [historical graph generator](../tools/render_candidate_current_overview_v45.py); preserve all **32** separately counted public observations, the unchanged **31,237** original cases, the separate **50** signature cases, every previous candidate failure, and the expanded unopened final comparison.
- [Historical recovery-safe Rust and public-entrypoint graph](../docs/evidence/candidate-current-overview-v44.svg), [historical graph inputs](../docs/evidence/candidate-current-overview-v44.inputs.json), [historical machine-readable results](../docs/evidence/candidate-current-overview-v44.json), and [historical graph generator](../tools/render_candidate_current_overview_v44.py); preserve the repaired Rust runner before its actual campaign, the unqualified Zig-backed public import, the historical Rust failure and build-archive effect, and all original evidence unchanged.
- [Historical first Rust-failure and overall-results graph](../docs/evidence/candidate-current-overview-v43.svg), [historical independently authenticated graph inputs](../docs/evidence/candidate-current-overview-v43.inputs.json), [historical machine-readable results](../docs/evidence/candidate-current-overview-v43.json), and [historical graph generator](../tools/render_candidate_current_overview_v43.py); one actual Rust controller attempt fails before candidate matching. It reads one historical source-build archive but **zero** matching or Python-reference archives; the frozen controller omitted the build-archive effect. All original cases and historical failures remain unchanged.
- [Historical C and Rust runner source-freeze graph](../docs/evidence/candidate-current-overview-v42.svg), [historical graph inputs](../docs/evidence/candidate-current-overview-v42.inputs.json), [historical machine-readable results](../docs/evidence/candidate-current-overview-v42.json), and [historical graph generator](../tools/render_candidate_current_overview_v42.py); this preserves the exact independently frozen state before the real Rust controller failure.
- [Historical C-only test runner and overall-results graph](../docs/evidence/candidate-current-overview-v41.svg), [historical C-only graph inputs](../docs/evidence/candidate-current-overview-v41.inputs.json), [historical machine-readable results](../docs/evidence/candidate-current-overview-v41.json), and [historical graph generator](../tools/render_candidate_current_overview_v41.py); this preserves the authentic state before the separate Rust-only runner was frozen.
- [Historical Zig-correction and six-family source-inventory graph](../docs/evidence/candidate-current-overview-v40.svg), [historical graph inputs](../docs/evidence/candidate-current-overview-v40.inputs.json), [historical machine-readable results](../docs/evidence/candidate-current-overview-v40.json), and [historical graph generator](../tools/render_candidate_current_overview_v40.py); this authenticates the exact actual state before the corrected C-only runner was frozen. Preserve the unapplied **64** of **1,024** Zig scanner cases, historical **1,764** Zig differences, the corrected Python reference, and at least **164** evidence owners and **169** references.
- [Historical six-family test-producer graph](../docs/evidence/candidate-current-overview-v39.svg), [historical test-producer graph inputs](../docs/evidence/candidate-current-overview-v39.inputs.json), [historical machine-readable results](../docs/evidence/candidate-current-overview-v39.json), and [historical graph generator](../tools/render_candidate_current_overview_v39.py); preserve the corrected Python baseline, frozen six-family producer, and matching-blocked state from before the Zig scanner correction was frozen.
- [Historical corrected-Python-reference graph](../docs/evidence/candidate-current-overview-v38.svg), [historical corrected-reference graph inputs](../docs/evidence/candidate-current-overview-v38.inputs.json), [historical machine-readable results](../docs/evidence/candidate-current-overview-v38.json), and [historical graph generator](../tools/render_candidate_current_overview_v38.py); preserve the actual passing two-process reference and the previous state before the corrected six-family producer was frozen.
- [Historical Python-reference falsification graph](../docs/evidence/candidate-current-overview-v37.svg), [historical falsification graph inputs](../docs/evidence/candidate-current-overview-v37.inputs.json), [historical machine-readable results](../docs/evidence/candidate-current-overview-v37.json), and [historical graph generator](../tools/render_candidate_current_overview_v37.py); preserve the **96** actual Python-context failures, **162** authenticated evidence owners, and **167** references from before the corrected two-worker reference passed.
- [Historical candidate and corrected-Rust build graph](../docs/evidence/candidate-current-overview-v36.svg), [historical graph inputs](../docs/evidence/candidate-current-overview-v36.inputs.json), [historical machine-readable results](../docs/evidence/candidate-current-overview-v36.json), and [historical graph generator](../tools/render_candidate_current_overview_v36.py); this preserved snapshot predates the candidate-context falsification. It authenticates the corrected Rust build's **28** real processes, **161** evidence owners, and **166** references. Its Rust, C, and Zig matching results are historical, not corrected-reference results.
- [Historical Python-versus-candidates and signature-reference graph](../docs/evidence/candidate-current-overview-v35.svg), [historical independently authenticated graph inputs](../docs/evidence/candidate-current-overview-v35.inputs.json), [historical machine-readable reference and candidate evidence](../docs/evidence/candidate-current-overview-v35.json), and [historical graph generator](../tools/render_candidate_current_overview_v35.py); preserve the two Python workers passing all **50** additional checks and the **159**-owner, **164**-reference evidence snapshot from before the corrected Rust build was recorded.
- [Historical corrected-Zig graph](../docs/evidence/candidate-current-overview-v34.svg), [historical corrected-Zig graph inputs](../docs/evidence/candidate-current-overview-v34.inputs.json), [historical full candidate results](../docs/evidence/candidate-current-overview-v34.json), and [historical graph generator](../tools/render_candidate_current_overview_v34.py); this preserved **157**-owner, **162**-reference snapshot recorded Rust's **1,036** differences, C's **1,230**, and corrected Zig's **1,764** before the separate signature-reference evidence was published.
- [Historical pre-test graph inputs](../docs/evidence/candidate-current-overview-v33.inputs.json), [historical machine-readable Python baseline, matching results, and independently verified Zig build](../docs/evidence/candidate-current-overview-v33.json), and [historical graph generator](../tools/render_candidate_current_overview_v33.py); this preserved snapshot authenticates the **155** evidence files and **160** references available before the corrected Zig matching test. It records Rust's **1,036** differences, C's **1,230**, and the previous Zig engine's **2,172** differences. It does not include the later corrected Zig result.
- [Preserved historical Rust-only graph](../docs/evidence/candidate-current-overview-v32.svg), [historical source inputs](../docs/evidence/candidate-current-overview-v32.inputs.json), and [historical graph generator](../tools/render_candidate_current_overview_v32.py); its **153** owners and **158** references describe the genuine state before the corrected Zig source-build evidence was published.
- [Full experiment log, build reports, previous graphs, failures, and rejected designs](../docs/EXPERIMENT-LOG.md).
- [Proposed 4,194,304-case final comparison](../docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md); examples remain **NOT GENERATED** and **NOT OPENED**.
- [Original objective](../GOAL.md), SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`; [later clarifications](../AMENDMENTS.md).

## Verify the actual Rust result without rerunning it

The following commands read the published Rust result, not the final
performance comparison. The compressed report expands to exactly
**5,295,588** bytes with SHA-256
`86f903168ef0d7e07a07c8a4341a146313cdd9d87b4c326316e0a89744aeb41b`.
The report contains the genuine complete **13**-group result; the
receipt's passing status authenticates durable publication of a failing
candidate. Do not rerun or overwrite the already-used campaign label.

```sh
REBAR_RUST_FAILURE=oracle/phase2/evidence/repaired-rust-original-campaign-v7-rust-phase2-v13-rust-pattern-repr-original-p0-failures.json.gz
REBAR_RUST_RECEIPT=oracle/phase2/evidence/repaired-rust-original-campaign-v7-rust-phase2-v13-rust-pattern-repr-original-p0-failures-publication-receipt.json

sha256sum "$REBAR_RUST_FAILURE" "$REBAR_RUST_RECEIPT"

jq -e '
  select(
    .status == "PASS"
    and .publication_status == "PASS"
    and .publication_pass_means == "DURABLE PUBLICATION ONLY"
    and .candidate_status == "FAIL"
    and .candidate_qualified == false
    and .case_execution_denominator == 31237
    and .suite_count == 13
    and .completed_suite_count == 13
    and .distinct_worker_process_id_count == 13
    and .semantic_mismatch_count == 928
    and .verified_passing_case_count == 8965
    and .infrastructure_failure_count == 0
    and .all_four_original_targets_restored == true
    and .resulting_repository_evidence_owner_count == 168
    and .resulting_authenticated_reference_count == 173
    and .holdout == "NOT OPENED"
    and .winner_selected == false
  ) | {
    candidate_status, publication_pass_means, completed_suite_count,
    semantic_mismatch_count, verified_passing_case_count,
    infrastructure_failure_count, all_four_original_targets_restored
  }
' "$REBAR_RUST_RECEIPT"

gzip -dc "$REBAR_RUST_FAILURE" | jq '{
  status,
  case_execution_denominator,
  failed_groups: [
    .suite_results[] | select(.mismatch_count != 0) |
    {suite, case_execution_denominator, mismatch_count, fully_observed}
  ],
  total_mismatches: ([.suite_results[].mismatch_count] | add),
  total_original_cases: ([.suite_results[].case_execution_denominator] | add)
}'

gzip -dc "$REBAR_RUST_FAILURE" | sha256sum
```

## Run the source-only safety checks

Run these checks without opening the final performance comparison:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

"$PY" -I -B tools/verify_p0_completeness_v1.py --self-test
"$PY" -I -B tools/verify_large_input_indexing_v1.py \
  --self-test \
  --source-sha256 57a9e0d0e456b854cb46dfadb2b23db244597f01904fcf93587b1f5d8a5e4544 \
  --protocol-sha256 0a640ee044c52394fa897d0221d51dfc3d85e9abb95608367698f11fba8ca879 \
  --contract-sha256 23601fe4947c70979081d8248ee9891287e3fa618b554b97a8ee56024823bacf
"$PY" -I -B tools/render_candidate_current_overview_v48.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v47.py --self-test
"$PY" -I -B tools/run_frozen_zig_original_p0_candidate_worker_v1.py --self-test
"$PY" -I -B tools/run_frozen_zig_original_p0_candidate_v1.py --self-test
"$PY" -I -B tools/verify_public_entrypoint_import_v1.py \
  --self-test \
  --source-sha256 c0a61c4cf520e82bf0c327a17c06daf64f57a1dcfd20b37c6e9f7b84177108b4 \
  --protocol-sha256 01ace52c6285142733bdcb2b4556feb43226e01c8b181b84019b8fa8c42697c0 \
  --contract-sha256 b80ba35a6af481f0dd1c5b9141e2995f7b0ffd12f8ffa7060bab50344ddbda47
"$PY" -I -B tools/run_owned_six_family_original_p0_producer_v4.py --self-test
"$PY" -I -B tools/run_owned_repaired_rust_original_campaign_v7.py \
  --self-test \
  --source-sha256 eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104 \
  --protocol-sha256 0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840 \
  --contract-sha256 9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5
"$PY" -I -B tools/apply_owned_zig_scanner_phrase_source_repair_v3.py \
  --self-test \
  --source-sha256 9b5cf55b9d66729b84b91470f8ba5906208ccee09312b43c329acaab2ff34010 \
  --protocol-sha256 78fccd7fffd33e5ecd9a9033d8225c294d82ee07f391eb46ccd621a08e0d38e1 \
  --contract-sha256 4eee672b4fe6f25f7481c34a34928f00d34a45a9e0675e024238a8ee5576fade
"$PY" -I -B tools/verify_owned_public_type_reference_context_v1.py \
  --self-test \
  --source-sha256 bff95e5630e875e1b389eeb4555810a112728dbed5f2cc7c43e1ec83d0817ddc \
  --protocol-sha256 11ca046ccd5087b2212b8ad8496896fb1fd60e408a193e038bae4b19fb360018 \
  --contract-sha256 dd0ea680e9a73345f7c323e278ba7ccebd5a3bb26cb606a9bdbecf7c3fb8298b
"$PY" -I -B tools/verify_python_re_callable_introspection_v1.py \
  --self-test \
  --source-sha256 5a64fb4546bdccd13b6d8d9ba32a7472b01cb86dd0d9f2c643678e6bbf919653 \
  --protocol-sha256 1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8 \
  --contract-sha256 e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349
"$PY" -I -B tools/run_owned_callable_introspection_reference_v2.py \
  --self-test \
  --source-sha256 00c543077bfbe38e5c48e9970f7881119d21cb32cf91e838d21587f8f820ada4 \
  --protocol-sha256 1e316b848e5d7a44b83a8f44605f08370faacb33074c2b79c042c76d9390a59f \
  --contract-sha256 0f87ef8926771cfe39e33d95b3b871f03c9f1c44fe932615f7067d391eb68f42
"$PY" -I -B tools/run_frozen_p0_candidate_worker_v4.py --self-test
"$PY" -I -B tools/run_frozen_p0_candidate_v6.py --self-test
"$PY" -I -B tools/run_frozen_p0_candidate_worker_v5.py --self-test
"$PY" -I -B tools/run_frozen_p0_candidate_v7.py --self-test
"$PY" -I -B tools/run_frozen_p0_candidate_worker_v6.py --self-test
"$PY" -I -B tools/run_frozen_p0_candidate_v8.py --self-test
"$PY" -I -B tools/run_owned_repaired_c_original_campaign_v1.py --self-test
"$PY" -I -B tools/run_owned_six_family_original_p0_producer_v1.py --self-test
"$PY" -I -B tools/run_owned_six_family_original_p0_producer_v2.py --self-test
"$PY" -I -B tools/run_owned_six_family_original_p0_producer_v3.py --self-test
"$PY" -I -B tools/run_frozen_p0_candidate_worker_v7.py --self-test
"$PY" -I -B tools/run_frozen_p0_candidate_v9.py --self-test
"$PY" -I -B tools/run_owned_frozen_p0_v9_live_context_adapter_v1.py --self-test
"$PY" -I -B tools/run_owned_repaired_c_original_campaign_v2.py --self-test
"$PY" -I -B tools/run_owned_repaired_c_original_campaign_v3.py --self-test
"$PY" -I -B tools/run_owned_repaired_c_original_campaign_v4.py --self-test \
  --source-sha256 e1730319db687828e7a283574cfd3daa8fb41c936025965c140b5b9de12978a5 \
  --protocol-sha256 79f5f81aedd85b9a59c121b0a3ae96ca3fc3307a34c1427464762ae569f4d473 \
  --contract-sha256 83a00d475acb9e5e103ed9ed6f4a58e116da47db462322f4bb05bd406b4c09f4
"$PY" -I -B tools/apply_owned_rust_public_contract_source_repair_v1.py --self-test
"$PY" -I -B tools/apply_owned_rust_public_contract_source_repair_v2.py \
  --self-test \
  --source-sha256 d0f90145195e9978482a7797956ef916adb1d0612118c2fc6343c4f38b823fa8 \
  --protocol-sha256 3f469ca7298b08cc1d50d18aff5029ae17a3f4f318c4fc7a2d8f8f45cc16e239 \
  --contract-sha256 b87c876e16041b0e08619aec0a86a069598b54478a1fa55cc9baa220c2c1f53b
"$PY" -I -B tools/apply_owned_rust_public_contract_source_repair_v3.py \
  --self-test \
  --source-sha256 5e57da2379e736bba75eacdb57f84710dc144c0d4088d5827b3139a6b71d8859 \
  --protocol-sha256 2aeb81e55548b46011c75815465d2bc2fa461d57ba7b990fc7a7b87d2d687a34 \
  --contract-sha256 82bce0066181dd16f3de52d88f31e930f25706b5ff3da2ba18b10c8b31b4f6a1
"$PY" -I -B tools/reproduce_owned_rust_flag_source_build_v12.py \
  --self-test \
  --source-sha256 1b3f8333f36a6262e962647719ed99b00dd1519a704bf7f07a5d1f1d56377db6 \
  --protocol-sha256 822857ed434cf1273c0d5eaf14f540d0398c744fee8e14b7b7734238dc2d9950 \
  --contract-sha256 c1c68590a1b45005fb709dc00a6a5f86e6564ed494e179fff9480ea5bed7b592
"$PY" -I -B tools/reproduce_owned_rust_pattern_repr_source_build_v13.py \
  --self-test \
  --source-sha256 2ec050c9902cbb3a239ed3a2dce3258344300b40546e37aea374cf18a9c8b797 \
  --protocol-sha256 3c486fdb63041b4f6060a6147186dd93c8339cbdff5f8060f597ab156ff05701 \
  --contract-sha256 15023a0a484715f2d97ae5ea9649bb16fe3d30781d601635bda40c246c5906aa
"$PY" -I -B tools/reproduce_owned_native_source_build_v11.py --self-test
"$PY" -I -B tools/run_owned_six_family_original_p0_campaign_v1.py --self-test
"$PY" -I -B tools/run_owned_six_family_original_p0_campaign_v2.py --self-test
"$PY" -I -B tools/apply_owned_cpp_public_argument_source_repair_v1.py --self-test \
  --source-sha256 05681d65d080ff7c67d9afbf8dd22275123dbd0542afa8079121c4134c542d65 \
  --protocol-sha256 3d97db34bbbe41ee7a841bb9e5eef7737415749bbc5645a6ab90f70f42a24271 \
  --contract-sha256 ff3918853438e80778f1179057ebdf3618b395f999fe6a88494d3575b03be765
"$PY" -I -B tools/apply_owned_go_unicode_name_source_repair_v1.py --self-test \
  --source-sha256 a32f1062ef507903edc3a7cb5d0462853528e57582dd61e24e97fd1cc7737561 \
  --protocol-sha256 fa738f2365a087d07d3860b23278fb20da00300e0d3eb3df09b6d3584f3b4c95 \
  --contract-sha256 b48d52c712288b037f2b2f88a69e658d8a389fd9ab469fb1999f80debc582d33
"$PY" -I -B tools/reproduce_owned_go_unicode_source_build_v13.py --self-test \
  --source-sha256 0c5319b7cfe6400cf7cd577efd36d8d574ee6a8674cd28987295402ce6020b06 \
  --protocol-sha256 60edb693ec2b57cf2a03c7aca7c863320563b12a18f6daecd5ab080aded0fc11 \
  --contract-sha256 a04b93a857d5ad71105479385bc9141b15c1f5303fb2a7059539b0266515f743
"$PY" -I -B tools/preserve_owned_go_campaign_publication_failure_v1.py --self-test
"$PY" -I -B tools/run_owned_candidate_subinterpreters_v3.py --self-test
"$PY" -I -B tools/reproduce_owned_native_source_build_v4.py --self-test
"$PY" -I -B tools/reproduce_owned_native_source_build_v4.py --verify-context
"$PY" -I -B tools/reproduce_owned_native_source_build_v5.py --self-test
"$PY" -I -B tools/reproduce_owned_native_source_build_v5.py --verify-context
"$PY" -I -B tools/reproduce_owned_native_source_build_v6.py --self-test
"$PY" -I -B tools/reproduce_owned_native_source_build_v6.py --verify-context
"$PY" -I -B tools/reproduce_owned_native_source_build_v7.py --self-test
"$PY" -I -B tools/reproduce_owned_native_source_build_v8.py --self-test
"$PY" -I -B tools/reproduce_owned_native_source_build_v9.py --self-test
"$PY" -I -B tools/activate_verified_native_candidate_v2.py --self-test
"$PY" -I -B tools/activate_verified_native_candidate_v3.py --self-test
"$PY" -I -B tools/activate_verified_native_candidate_v3.py --verify-frozen-context
"$PY" -I -B tools/activate_verified_native_candidate_v4.py --self-test
"$PY" -I -B tools/activate_verified_native_candidate_v4.py --verify-frozen-context
"$PY" -I -B tools/activate_verified_native_candidate_v5.py --self-test
"$PY" -I -B tools/audit_candidate_independence_v2.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v19.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v20.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v21.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v22.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v23.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v24.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v25.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v26.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v27.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v28.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v29.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v30.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v31.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v32.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v33.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v34.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v35.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v36.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v37.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v38.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v39.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v40.py --self-test
"$PY" -I -B tools/run_frozen_p0_candidate_worker_v8.py --self-test
"$PY" -I -B tools/run_frozen_p0_candidate_v10.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v41.py --self-test
"$PY" -I -B tools/run_owned_repaired_rust_original_campaign_v6.py \
  --self-test \
  --source-sha256 c25cbdf3674fc3e054c388e53de3ed38d4b1dab0a820808c42848e1803909f5e \
  --protocol-sha256 ddc5c212d3e188bc1d1cdde992bf872a38962e64d3b07d6ec7c275ba4f55f13c \
  --contract-sha256 ce044f18be388ab0608d0bd3bb68751e6970973f8e6ef758971e75e6d6b584a5
"$PY" -I -B tools/render_candidate_current_overview_v42.py --self-test
"$PY" -I -B tools/render_candidate_current_overview_v43.py --self-test
"$PY" -I -B tools/activate_verified_native_candidate_v6.py --self-test \
  --source-sha256 d3a9b08c1bf7e3408719a0e92b8c1965aa6160dd2e18ab1501bb8662aaf8e4a1 \
  --protocol-sha256 0e736d575835fa22388841a527e22b62eef1ddf39eac9415bd7c518ba985b1d0 \
  --contract-sha256 e0d486cc6d621e963f8af5db1c4f7a47d590ad679837db1f53e11d05b670332e
"$PY" -I -B tools/activate_verified_native_candidate_v7.py --self-test \
  --source-sha256 98002a0a283ffec24670bcb9f35546c5720d2a7a1d098257729d244918022f8e \
  --protocol-sha256 f333b50f9810cf246ae659c6d07eb4c63b8e2114d07b485b50d570ab272f22f8 \
  --contract-sha256 62375f7d013b7b02a160b9492e5aa249b7af556041f2c86f20e7bfd5ad6885b1
"$PY" -I -B tools/run_owned_repaired_zig_original_campaign_v1.py --self-test \
  --source-sha256 ff4bc83173930c193de5984659aa6e8aca1848496d06f3d3dca3c28294c37c90 \
  --protocol-sha256 974c1cc09511c7a119a2ea0f59fab8c39e8d1887c948df19657de2458b5b9d67 \
  --contract-sha256 f3f1bdfea41b8b4d5bce22b2b236c76f653e97268e500b951fbef262052718f0
"$PY" -I -B tools/run_owned_repaired_zig_original_campaign_v2.py --self-test \
  --source-sha256 a9f62061f709583c60a4d0b72ba1150931132a66b80b6eed1081e017fd389795 \
  --protocol-sha256 fe17a8fc4e5fb5638ff92caa6e1b6d625e93dfb27ced02ba7b1490b830356db3 \
  --contract-sha256 0112748e8dbca769625ea2643643fad81ced069e20ed87a458bebe0a922d2851
"$PY" -I -B tools/run_owned_repaired_zig_original_campaign_v3.py --self-test \
  --source-sha256 e4efad7dfbe921bec9f7160cd33dbbed0376b1373037a78de8bcaabdcd2ece98 \
  --protocol-sha256 0463e23aaed9de6e1b50db7f106a1f175b504eefdbf868fa1f03ed5b313776d1 \
  --contract-sha256 4d20518685e2db7b80c9a1936f4ae480cff85c2a3b672562f6d4fded20b8328d
"$PY" -I -B tools/run_owned_repaired_rust_original_campaign_v2.py --self-test \
  --source-sha256 a6ffce3eb9ff09f27f3e35f84b35b9d1aba6e29dae225c56c036de85e089b7b3 \
  --protocol-sha256 9b9a246a08c0e89667899a6317df41424320617f7c4ac6cb84ef210fabee1ca0 \
  --contract-sha256 bc100f6a7a3d4ec2640e131211ecea202172846daa10c93d73cbf58ea74ed547
"$PY" -I -B tools/run_owned_repaired_rust_original_campaign_v3.py --self-test \
  --source-sha256 23819da6e6bb1ce8b27144a5d974b4bb0ecac845c844cb6fadae2ba01b2ef3d2 \
  --protocol-sha256 c29edb7751045da17cce2052e028b92530d8eab5ba6b8adafc21135a746f7883 \
  --contract-sha256 ab4b424570254201865394330e025850b4626dfe2eaacd4ec82f41d2e99b0980
"$PY" -I -B tools/run_owned_repaired_rust_original_campaign_v4.py \
  --self-test \
  --source-sha256 7d63b397deddd5c23af075754fcb50f7b3bdfb44390269383aae7903d46b4dd0 \
  --protocol-sha256 5296b7ed7c3ba37ce4e299924e9e9edae849bebcd0e92e828977ae9ac6c9e26b \
  --contract-sha256 26e86429e1e437fc791401197fb8c6dd9cf399bb025bd027af5f9c2554d6f60b
"$PY" -I -B tools/preserve_owned_zig_campaign_preflight_failure_v1.py --self-test \
  --source-sha256 4a401ea42b4446535d51d1c7c65c688196185a0bb9fa2e15aebdb3bfebb85498 \
  --protocol-sha256 a3c005c95c61a68a5683125f7805564f4749ea9e82350f2d883da9e29b2817c5 \
  --contract-sha256 534a3cde3084c12a4124f5dea057ddb80b53fa4c591c8c72e26931bc277735f0
"$PY" -I -B tools/apply_owned_first_party_source_repair_v2.py --self-test \
  --source-sha256 1bb4f21cca20928b1c8993b3646825ac04ad46a231633105e5cb2469fd8434c0 \
  --protocol-sha256 a91fd1615d25597109c11605fdbeadd1673137cdd819b326bfff5dfb5699b611
"$PY" -I -B tools/reproduce_owned_c_pickle_source_build_v12.py --self-test \
  --source-sha256 654e4dea29b9f687a27b53fa18b2f345e29042a03ea4b507594e87fa3e4a161f \
  --protocol-sha256 aecb2cacfc5397a46e2d123767d4b7bf39935d1bda95d3b0d0cf8058614769ac
"$PY" -I -B tools/reproduce_owned_c_pickle_source_build_v13.py --self-test \
  --source-sha256 697b0959acf12ae779553f6c2654663d0358cd8c834f59b39850aad2b1fd683c \
  --protocol-sha256 2b8cdfcfa3274b2ebcf6eac29fd3680fa9c748efe2084cd65b0edd780ab2d387
"$PY" -I -B tools/reproduce_owned_c_pickle_source_build_v14.py --self-test \
  --source-sha256 60af4a7351ab8b9afec4e0863c281c452bfcd95193c2fdf46e1be3fed99854c0 \
  --protocol-sha256 be7872faf61547b4485f90a913fe44819a885d30020a135d80a4aafe6b5c97cc
"$PY" -I -B tools/reproduce_owned_c_pickle_source_build_v15.py --self-test \
  --source-sha256 91bc1985ac1edad757a3b027840db3f08aa97a781df1542e33b39d39f04aa7d8 \
  --protocol-sha256 fab2219a4c4a0cf78acfe8adbb039aba591a450409d9cc75347d552d9d0e4727
"$PY" -I -B tools/apply_owned_first_party_source_repair_v1.py --self-test \
  --source-sha256 c04bbc8e7bc45bdbe1fb9eb93942286f5b32b39aef554db15b8b1acd9cc8cd99 \
  --protocol-sha256 1a2e83caaca5cb43fc82445c2a4fc3097bc3d51bdfc568783b8815797b8c63f5 \
  --contract-sha256 8f1a5676bbef5f2ef560d03fef910bf4ed3a4df029ecc0c638e3fa971206dab5
"$PY" -I -B tools/apply_owned_rust_source_repair_v1.py --self-test \
  --source-sha256 1d5d9b5e3fecb278fdcb97ef21dadff9134cdd779cb6751c42d4931096796851 \
  --protocol-sha256 df9ce744660a4328a2b83151a3320aca64a7ad1606e14a4509f50f638a4afc7b \
  --contract-sha256 1ef69922310cb40166896685c75004c9f423a78e5bb96341a545d4dc75a1cf9b
"$PY" -I -B tools/apply_owned_zig_scanner_capture_source_repair_v1.py --self-test \
  --source-sha256 963f306373753b9fef84c9a9784668f42067cb905b84347a0bcc99e1e8692515 \
  --protocol-sha256 7a40b58bcc69744fc6b749368ec307be7d05d742de3d921410fd2753a4f5c8d0 \
  --contract-sha256 c48fcd9cb40cbe15442c2dd197627d7f4ccc341b3edfbbe0c645405015c8ea87
"$PY" -I -B tools/apply_owned_zig_scanner_capture_source_repair_v2.py \
  --self-test \
  --source-sha256 87a4cf8895b5d52c346213ef8277c17b66af44eba695bc37fac5198e0169b6ff \
  --protocol-sha256 eb71f594968a497ddeef5aaf0ab9f221d46153be47e69402a1f0090fa6597879 \
  --contract-sha256 3afc80a62a50ee55d059b6a19fc74915ca0a8cbdeddd9efa723722b2629ee85e
"$PY" -I -B tools/reproduce_owned_zig_scanner_source_build_v11.py --self-test \
  --source-sha256 b908f12d14fb8ebc5f17c62dfc00d48a1a5ee3717a3144aed437059e21c0f097 \
  --protocol-sha256 15fd222876407be72d36c0b9cf2ce581d8b73a954358df192c2a083a08973539 \
  --contract-sha256 92979e4bfacd6d23e7f54f4fdce7a7707cc54dba2512753029fdcd479150464c
"$PY" -I -B tools/reproduce_owned_zig_scanner_source_build_v12.py --self-test \
  --source-sha256 5192fa35dd0b13cb3bdddfc8f24c37d7e797d0b8463d000c4692c8131f33d1b6 \
  --protocol-sha256 f80743d8109402e5876792b6713237b1ab770e3286874dd5ae47fb56381131b1 \
  --contract-sha256 5abb6f60c7a9672e32d6f2980a109ccb15b7ef56e5cc3a81abda458109552c1a
```

Verify the completed Python reference without starting another Python
process or opening the final comparison:

```sh
sha256sum \
  oracle/phase1/evidence/public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0.json.gz \
  oracle/phase1/evidence/public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0-publication-receipt.json

jq -e '
  .schema == "rebar-phase1-owned-public-type-reference-context-v1-durable-publication-receipt"
  and .status == "PASS"
  and .reference_status == "PASS"
  and .publication_status == "PASS"
  and .actual_distinct_reference_process_ids == [81, 82]
  and .actual_reference_worker_count == 2
  and .attempted_reference_worker_count == 2
  and .actual_started_reference_worker_count == 2
  and .completed_reference_worker_count == 2
  and .validated_reference_worker_count == 2
  and .public_case_count_per_reference == 6912
  and .original_case_execution_denominator == 31237
  and .full_reference_records_sha256 == "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
  and .cache_records_sha256 == "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
  and .archive.sha256 == "c4906928850329fa3576576221e713ce653adae17a02a4de4bac4cb006389e05"
  and .archive.bytes == 1374913
  and .candidate_workers_started == 0
  and .holdout == "NOT OPENED"
' oracle/phase1/evidence/public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0-publication-receipt.json
```

Verify the current headline graph without rerunning a candidate,
decompressing a matching archive, or opening the final comparison:

```sh
# Verify the corrected Python-reference freeze without starting a worker.
"$PY" -I -B tools/verify_owned_public_type_reference_context_v1.py \
  --verify-frozen-context \
  --source-sha256 bff95e5630e875e1b389eeb4555810a112728dbed5f2cc7c43e1ec83d0817ddc \
  --protocol-sha256 11ca046ccd5087b2212b8ad8496896fb1fd60e408a193e038bae4b19fb360018 \
  --contract-sha256 dd0ea680e9a73345f7c323e278ba7ccebd5a3bb26cb606a9bdbecf7c3fb8298b

# Verify the corrected six-family producer without running a candidate.
"$PY" -I -B tools/run_owned_six_family_original_p0_producer_v4.py \
  --verify-frozen-context \
  --source-sha256 e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8 \
  --protocol-sha256 e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5 \
  --document-sha256 c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5

# Verify the frozen Zig correction without applying or building it.
"$PY" -I -B tools/apply_owned_zig_scanner_phrase_source_repair_v3.py \
  --verify-frozen-context \
  --source-sha256 9b5cf55b9d66729b84b91470f8ba5906208ccee09312b43c329acaab2ff34010 \
  --protocol-sha256 78fccd7fffd33e5ecd9a9033d8225c294d82ee07f391eb46ccd621a08e0d38e1 \
  --contract-sha256 4eee672b4fe6f25f7481c34a34928f00d34a45a9e0675e024238a8ee5576fade

# Verify the corrected C-only worker without running a candidate.
"$PY" -I -B tools/run_frozen_p0_candidate_worker_v8.py \
  --verify-frozen-context \
  --source-sha256 78634bbcb5f55c560ea4b38c81ca395f4d4d5385c285bd0a3c25b395e3dd5ee1 \
  --runner-source-sha256 c114b578ac7ebfe28b45aa3b3407b81d05333f4470fa3047fd338ed3541c185a \
  --protocol-sha256 2d773fc55fe7c0a61e044a0e7deef81c8e36ffa0a9a744f4e60901f7a953c2ae \
  --document-sha256 8eb72f1d94af85db1f1b282dda4d6ce1839f51f492ed2c7436c666d792f9b737 \
  --producer-source-sha256 e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8 \
  --producer-protocol-sha256 e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5 \
  --producer-document-sha256 c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5

# Verify the corrected C-only runner without running a candidate.
"$PY" -I -B tools/run_frozen_p0_candidate_v10.py \
  --verify-frozen-context \
  --source-sha256 c114b578ac7ebfe28b45aa3b3407b81d05333f4470fa3047fd338ed3541c185a \
  --worker-source-sha256 78634bbcb5f55c560ea4b38c81ca395f4d4d5385c285bd0a3c25b395e3dd5ee1 \
  --protocol-sha256 2d773fc55fe7c0a61e044a0e7deef81c8e36ffa0a9a744f4e60901f7a953c2ae \
  --document-sha256 8eb72f1d94af85db1f1b282dda4d6ce1839f51f492ed2c7436c666d792f9b737 \
  --producer-source-sha256 e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8 \
  --producer-protocol-sha256 e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5 \
  --producer-document-sha256 c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5

# Verify the current recovered Rust-only runner without running a candidate.
"$PY" -I -B tools/run_owned_repaired_rust_original_campaign_v7.py \
  --verify-frozen-context \
  --source-sha256 eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104 \
  --protocol-sha256 0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840 \
  --contract-sha256 9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5

# Verify the preserved historical Rust-only runner without running a candidate.
"$PY" -I -B tools/run_owned_repaired_rust_original_campaign_v6.py \
  --verify-frozen-context \
  --source-sha256 c25cbdf3674fc3e054c388e53de3ed38d4b1dab0a820808c42848e1803909f5e \
  --protocol-sha256 ddc5c212d3e188bc1d1cdde992bf872a38962e64d3b07d6ec7c275ba4f55f13c \
  --contract-sha256 ce044f18be388ab0608d0bd3bb68751e6970973f8e6ef758971e75e6d6b584a5

# Verify the separately frozen Zig worker without loading its native engine.
"$PY" -I -B tools/run_frozen_zig_original_p0_candidate_worker_v1.py \
  --verify-frozen-context \
  --source-sha256 ddafdc5b1fe06dbfa6449cbfde768d7fee6d16953b3c769c1e30aa600e3c62f9 \
  --source-size-bytes 123801 \
  --runner-source-sha256 8c9be13232fdbab7ff01b2313a816fd80e033fb5b6d0bf3d8cb07444eeba4856 \
  --runner-source-size-bytes 55722 \
  --protocol-sha256 294dfb6bc8e286d8415b329f8b2918b856ab3b2d1afb8261e3e04663028fda3c \
  --protocol-size-bytes 9040 \
  --document-sha256 1ff289540457ecba4e91b3b9491b3c42872a5db09b95815b8f58fcdc34315470 \
  --document-size-bytes 19592 \
  --producer-source-sha256 e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8 \
  --producer-protocol-sha256 e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5 \
  --producer-document-sha256 c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5

# Verify the independent Zig controller without compiling or matching.
"$PY" -I -B tools/run_frozen_zig_original_p0_candidate_v1.py \
  --verify-frozen-context \
  --source-sha256 8c9be13232fdbab7ff01b2313a816fd80e033fb5b6d0bf3d8cb07444eeba4856 \
  --source-size-bytes 55722 \
  --worker-source-sha256 ddafdc5b1fe06dbfa6449cbfde768d7fee6d16953b3c769c1e30aa600e3c62f9 \
  --worker-source-size-bytes 123801 \
  --protocol-sha256 294dfb6bc8e286d8415b329f8b2918b856ab3b2d1afb8261e3e04663028fda3c \
  --protocol-size-bytes 9040 \
  --document-sha256 1ff289540457ecba4e91b3b9491b3c42872a5db09b95815b8f58fcdc34315470 \
  --document-size-bytes 19592 \
  --producer-source-sha256 e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8 \
  --producer-protocol-sha256 e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5 \
  --producer-document-sha256 c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5

# Verify the public-entrypoint freeze without importing rebar or any engine.
"$PY" -I -B tools/verify_public_entrypoint_import_v1.py \
  --verify-frozen-context \
  --source-sha256 c0a61c4cf520e82bf0c327a17c06daf64f57a1dcfd20b37c6e9f7b84177108b4 \
  --protocol-sha256 01ace52c6285142733bdcb2b4556feb43226e01c8b181b84019b8fa8c42697c0 \
  --contract-sha256 b80ba35a6af481f0dd1c5b9141e2995f7b0ffd12f8ffa7060bab50344ddbda47

# Authenticate Python's genuine large-input methods without creating large text.
"$PY" -I -B tools/verify_large_input_indexing_v1.py \
  --verify-frozen-context \
  --source-sha256 57a9e0d0e456b854cb46dfadb2b23db244597f01904fcf93587b1f5d8a5e4544 \
  --protocol-sha256 0a640ee044c52394fa897d0221d51dfc3d85e9abb95608367698f11fba8ca879 \
  --contract-sha256 23601fe4947c70979081d8248ee9891287e3fa618b554b97a8ee56024823bacf

# Verify the combined Rust serialization source without building or running it.
"$PY" -I -B tools/apply_owned_rust_match_pickle_source_repair_v1.py \
  --self-test \
  --source-sha256 85383f4cdf93eef0130390e1114cbd1703edce154ca274d2427c6943e46b3517 \
  --protocol-sha256 fad29fdcd3956ae99f9db40afae33b51eb99fb743baf89540a4ee7aafb7ac1af \
  --contract-sha256 5456535223cb029d41e8739696bde30b2b7127995fd0ef30286ff0488b1ed133

# Verify both frozen source repairs without starting a native Rust worker.
"$PY" -I -B tools/apply_owned_rust_match_pickle_source_repair_v1.py \
  --verify-frozen-context \
  --source-sha256 85383f4cdf93eef0130390e1114cbd1703edce154ca274d2427c6943e46b3517 \
  --protocol-sha256 fad29fdcd3956ae99f9db40afae33b51eb99fb743baf89540a4ee7aafb7ac1af \
  --contract-sha256 5456535223cb029d41e8739696bde30b2b7127995fd0ef30286ff0488b1ed133

# Verify the preserved buffer-only Rust source without building or running it.
"$PY" -I -B tools/apply_owned_rust_buffer_shape_source_repair_v1.py \
  --self-test \
  --source-sha256 9c2a3642f2cda9fc85fd391baf4e0d57b25117f444d3a831592e8b62de3a627b \
  --protocol-sha256 67ba62acc8e51a6868404ea3faeb1aaaacb1d053cc1c915bef0c397edf5ac408 \
  --contract-sha256 ffa76d1724396fae5816cf96e0ae2104bcce8fc5eb246b8306d4441db0fe4a1b

# Verify the exact source, previously tested bridge, and frozen current context.
"$PY" -I -B tools/apply_owned_rust_buffer_shape_source_repair_v1.py \
  --verify-frozen-context \
  --source-sha256 9c2a3642f2cda9fc85fd391baf4e0d57b25117f444d3a831592e8b62de3a627b \
  --protocol-sha256 67ba62acc8e51a6868404ea3faeb1aaaacb1d053cc1c915bef0c397edf5ac408 \
  --contract-sha256 ffa76d1724396fae5816cf96e0ae2104bcce8fc5eb246b8306d4441db0fe4a1b

# Verify the current combined-source graph's 2,434 safety controls.
"$PY" -I -B tools/render_candidate_current_overview_v50.py --self-test

# Verify the current graph without building, matching, or opening an archive.
"$PY" -I -B tools/render_candidate_current_overview_v50.py \
  --verify-frozen-context \
  --source-sha256 4077fbf6703e98325c4b4eacea95d27608a3bb21a93143024094154385787f45 \
  --source-bytes 60235 \
  --previous-source-sha256 03ae29acb80817de9cfbd512e919702cea1a761f2bfa69c638b4644f179304b0 \
  --previous-inputs-sha256 0d78d45480bfd701024b733d33c43651a6ae29c760ac8f88c9404ee061d5bc76 \
  --previous-summary-sha256 1b5dad9574883e45b6bad5b2c9ec69f59a77e2ab079d7ed23a226280a4a4f4a4 \
  --previous-svg-sha256 761d1303e617827b79f0dd3ee24ab062d1282ea5cf568c4ca89c65a8ae19b75c \
  --variant-source-sha256 00271ad5fff71e2f2e30cda6b446a61d0c300cb91eec2091b8ada17662d9a335 \
  --variant-source-bytes 181004 \
  --feature-verifier-sha256 85383f4cdf93eef0130390e1114cbd1703edce154ca274d2427c6943e46b3517 \
  --feature-verifier-bytes 81784 \
  --feature-protocol-sha256 fad29fdcd3956ae99f9db40afae33b51eb99fb743baf89540a4ee7aafb7ac1af \
  --feature-protocol-bytes 5105 \
  --feature-contract-sha256 5456535223cb029d41e8739696bde30b2b7127995fd0ef30286ff0488b1ed133 \
  --feature-contract-bytes 15276 \
  --inputs-sha256 8506587243c98fa75a14dfc74cfc918772a74eadebc3f2728772d1d0d94bd726 \
  --summary-sha256 60f0648be19016e5d8ebfa01f93c2c50c32aa4fb981fc0d518902b8b9985005e \
  --svg-sha256 a114a7b813c4c1fc470950639adc50ffb7118dd91a31d9f63dee6ba46e04f8b9

# Verify the historical version-49 compact graph's 2,347 safety controls.
"$PY" -I -B tools/render_candidate_current_overview_v49.py --self-test

# Verify the historical version-49 graph without building or opening an archive.
"$PY" -I -B tools/render_candidate_current_overview_v49.py \
  --verify-frozen-context \
  --source-sha256 03ae29acb80817de9cfbd512e919702cea1a761f2bfa69c638b4644f179304b0 \
  --source-bytes 74565 \
  --previous-source-sha256 29604bd560dcba08f95ca8bcc792bf277c43a4680d94a82990fd341a1b0f6394 \
  --previous-inputs-sha256 d1bc5998012a8f174788a4c28fad7fa1116078a3cbb859b0f952eb65777e33da \
  --previous-summary-sha256 bfd591aebf6aea805c8f6a4b5665d87ceca6b2574513bb5cdfb8331b36176305 \
  --previous-svg-sha256 cf8955199d714854faeea4d5c0cabf4431010949a7b7d5ed81d5b65f14b74903 \
  --variant-source-sha256 29421096dc81759ca11c53080b7f838cc29ad16baa7e379c18c8417d35ab37b3 \
  --variant-source-bytes 180436 \
  --feature-verifier-sha256 9c2a3642f2cda9fc85fd391baf4e0d57b25117f444d3a831592e8b62de3a627b \
  --feature-verifier-bytes 64345 \
  --feature-protocol-sha256 67ba62acc8e51a6868404ea3faeb1aaaacb1d053cc1c915bef0c397edf5ac408 \
  --feature-protocol-bytes 5033 \
  --feature-contract-sha256 ffa76d1724396fae5816cf96e0ae2104bcce8fc5eb246b8306d4441db0fe4a1b \
  --feature-contract-bytes 11454 \
  --inputs-sha256 0d78d45480bfd701024b733d33c43651a6ae29c760ac8f88c9404ee061d5bc76 \
  --summary-sha256 1b5dad9574883e45b6bad5b2c9ec69f59a77e2ab079d7ed23a226280a4a4f4a4 \
  --svg-sha256 761d1303e617827b79f0dd3ee24ab062d1282ea5cf568c4ca89c65a8ae19b75c

# Verify the historical version-48 Rust-result graph's safety controls.
"$PY" -I -B tools/render_candidate_current_overview_v48.py --self-test

# Verify the historical version-48 graph without rerunning Rust or opening its archive.
"$PY" -I -B tools/render_candidate_current_overview_v48.py \
  --verify-frozen-context \
  --source-sha256 29604bd560dcba08f95ca8bcc792bf277c43a4680d94a82990fd341a1b0f6394 \
  --source-bytes 89718 \
  --previous-source-sha256 6deb2ffa07d50c1db2526afbea997bce3ebc1e518f569e4c8e3296c1351e5b43 \
  --previous-inputs-sha256 e68b649124623525120af790d01939ea75adee6ac249d38a55b5a6d57fd72dbf \
  --previous-summary-sha256 64fd1ad62eeb6c43748a4da19a66f869c93d3eafd9202375032c6214d79df05a \
  --previous-svg-sha256 0c39d603f9bfeb2d2a2be41654653368405b25da9910b1fe18854350c4338b3c \
  --campaign-source-sha256 eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104 \
  --campaign-protocol-sha256 0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840 \
  --campaign-contract-sha256 9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5 \
  --receipt-sha256 b87ff02f10103c1c8e7da7ed7ef77cd58936af2fe9e9b3c47448e8a449b01943 \
  --receipt-bytes 8450 \
  --receipt-inode 524938 \
  --receipt-device 2064 \
  --archive-sha256 4112b4e6372f4f94d59eece2e514bda21001f0828d686162e18b631911fc2c99 \
  --archive-bytes 3668825 \
  --archive-inode 524937 \
  --archive-device 2064 \
  --journal-sha256 034c10076147677c775674643f06c3c1362f0ace47c45bc40fd4fe11df4ec843 \
  --inputs-sha256 d1bc5998012a8f174788a4c28fad7fa1116078a3cbb859b0f952eb65777e33da \
  --summary-sha256 bfd591aebf6aea805c8f6a4b5665d87ceca6b2574513bb5cdfb8331b36176305 \
  --svg-sha256 cf8955199d714854faeea4d5c0cabf4431010949a7b7d5ed81d5b65f14b74903

# Verify the historical version-47 large-input chart without running an engine.
"$PY" -I -B tools/render_candidate_current_overview_v47.py \
  --verify-frozen-context \
  --source-sha256 6deb2ffa07d50c1db2526afbea997bce3ebc1e518f569e4c8e3296c1351e5b43 \
  --source-bytes 81068 \
  --previous-source-sha256 ddb25b70d9f87ad3b6eabbc7c2917a434739931ad2f5b5d194b5cb25706a9334 \
  --previous-inputs-sha256 c0633ec12f5aad3d0e0fb8fe29f143ccb6801ec63d5960c85afd47d982c4653d \
  --previous-summary-sha256 ec5ecbbcb765bb845a133ad81d02312eb29e6b18718d5e4b346ff10e74c10b3f \
  --previous-svg-sha256 913f8af0eae80bc48640551b589556a685f81b69f218783afc04e8d7e3746c14 \
  --large-source-sha256 57a9e0d0e456b854cb46dfadb2b23db244597f01904fcf93587b1f5d8a5e4544 \
  --large-protocol-sha256 0a640ee044c52394fa897d0221d51dfc3d85e9abb95608367698f11fba8ca879 \
  --large-contract-sha256 23601fe4947c70979081d8248ee9891287e3fa618b554b97a8ee56024823bacf \
  --inputs-sha256 e68b649124623525120af790d01939ea75adee6ac249d38a55b5a6d57fd72dbf \
  --summary-sha256 64fd1ad62eeb6c43748a4da19a66f869c93d3eafd9202375032c6214d79df05a \
  --svg-sha256 0c39d603f9bfeb2d2a2be41654653368405b25da9910b1fe18854350c4338b3c

# Verify the historical version-46 Zig graph's synthetic safety checks.
"$PY" -I -B tools/render_candidate_current_overview_v46.py --self-test

# Verify the historical version-46 graph without building or running Zig.
"$PY" -I -B tools/render_candidate_current_overview_v46.py \
  --verify-frozen-context \
  --source-sha256 ddb25b70d9f87ad3b6eabbc7c2917a434739931ad2f5b5d194b5cb25706a9334 \
  --source-bytes 78101 \
  --previous-source-sha256 07a7e1b6c96434e66e852e0eb784326816d340edb338d2e89de4f1d6918bb586 \
  --previous-inputs-sha256 cbc1b861fe59067e64adf396493630360f6bf616fe1f51598220aabafadea4a5 \
  --previous-summary-sha256 1086a7bd72116b590d00f5216835534ec745265a0f249d3cd5eb05a3701ff840 \
  --previous-svg-sha256 1c9d56fd4b8480bab9cedc2e95b6449a414cb68a02ee447963454db5b4242b2b \
  --zig-worker-sha256 ddafdc5b1fe06dbfa6449cbfde768d7fee6d16953b3c769c1e30aa600e3c62f9 \
  --zig-runner-sha256 8c9be13232fdbab7ff01b2313a816fd80e033fb5b6d0bf3d8cb07444eeba4856 \
  --zig-protocol-sha256 294dfb6bc8e286d8415b329f8b2918b856ab3b2d1afb8261e3e04663028fda3c \
  --zig-contract-sha256 1ff289540457ecba4e91b3b9491b3c42872a5db09b95815b8f58fcdc34315470 \
  --inputs-sha256 c0633ec12f5aad3d0e0fb8fe29f143ccb6801ec63d5960c85afd47d982c4653d \
  --summary-sha256 ec5ecbbcb765bb845a133ad81d02312eb29e6b18718d5e4b346ff10e74c10b3f \
  --svg-sha256 913f8af0eae80bc48640551b589556a685f81b69f218783afc04e8d7e3746c14

# Verify the historical version-45 public-import graph's safety checks.
"$PY" -I -B tools/render_candidate_current_overview_v45.py --self-test

# Verify the historical version-45 separately counted public-import graph.
"$PY" -I -B tools/render_candidate_current_overview_v45.py \
  --verify-frozen-context \
  --source-sha256 07a7e1b6c96434e66e852e0eb784326816d340edb338d2e89de4f1d6918bb586 \
  --source-bytes 68616 \
  --previous-source-sha256 10b64e05336485445b5199acdf4626854812c16df6c8248371860a764450324d \
  --previous-inputs-sha256 7b51e6fa89d7b1d3ccc043e0268f405fe072999d22bd6067aaf2f20ab43e0d94 \
  --previous-summary-sha256 5fa65d50eb041b0e12384846c5a7de548581cbc5f9183b1f72bc5f3d703a41c9 \
  --previous-svg-sha256 b23c43fab061df0cf192b9c5c869aee8854ad794397dc3c9512aa6f946150ab8 \
  --failure-sha256 88367fd41665bbeafb0645e3b03130ca97c1c54729863372d422e693169420d7 \
  --observation-sha256 51846c742aafbfc2c42ddad75836310bba518b3a76d0f8fa1548a55128852ad6 \
  --rust-source-sha256 eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104 \
  --rust-protocol-sha256 0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840 \
  --rust-contract-sha256 9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5 \
  --public-module-sha256 289769bd637ea525ae7e71d263377e15c0f394ba20619c11b98e266f57fcc34f \
  --public-module-bytes 212 \
  --public-project-sha256 7d50e8c6c2bc76a0e3ddcac6b5f157b013bcfd76944fdeb2c1c81e0181ae7825 \
  --public-project-bytes 224 \
  --public-oracle-source-sha256 c0a61c4cf520e82bf0c327a17c06daf64f57a1dcfd20b37c6e9f7b84177108b4 \
  --public-oracle-protocol-sha256 01ace52c6285142733bdcb2b4556feb43226e01c8b181b84019b8fa8c42697c0 \
  --public-oracle-contract-sha256 b80ba35a6af481f0dd1c5b9141e2995f7b0ffd12f8ffa7060bab50344ddbda47 \
  --public-case-matrix-sha256 f67f8d4d62f9939c94250ad2e4df55b14df013df7212aa66930ecc3a772d2a58 \
  --inputs-sha256 cbc1b861fe59067e64adf396493630360f6bf616fe1f51598220aabafadea4a5 \
  --summary-sha256 1086a7bd72116b590d00f5216835534ec745265a0f249d3cd5eb05a3701ff840 \
  --svg-sha256 1c9d56fd4b8480bab9cedc2e95b6449a414cb68a02ee447963454db5b4242b2b

# Verify the historical version-44 graph's synthetic safety checks.
"$PY" -I -B tools/render_candidate_current_overview_v44.py --self-test

# Verify the historical Rust-recovery graph without running an engine.
"$PY" -I -B tools/render_candidate_current_overview_v44.py \
  --verify-frozen-context \
  --source-sha256 10b64e05336485445b5199acdf4626854812c16df6c8248371860a764450324d \
  --source-bytes 85131 \
  --previous-source-sha256 3b3647a2090fd98e89ea421b2d2a3018983e1014adecf9f0b30731b54ca51e8b \
  --previous-inputs-sha256 394fb27e12b9a48fbd8bdd353930084891c09118e0cfa49fc90f596124e15017 \
  --previous-summary-sha256 1c5ea146e6d40f0e81f2fe274f2a1a50fe01efdd074ca7ea5b36cca420d16bf0 \
  --previous-svg-sha256 bee43e78aa59a806927a50e1e807181c62a3f6497d75add1834de2c75fdc546b \
  --failure-sha256 88367fd41665bbeafb0645e3b03130ca97c1c54729863372d422e693169420d7 \
  --observation-sha256 51846c742aafbfc2c42ddad75836310bba518b3a76d0f8fa1548a55128852ad6 \
  --rust-source-sha256 eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104 \
  --rust-protocol-sha256 0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840 \
  --rust-contract-sha256 9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5 \
  --public-module-sha256 289769bd637ea525ae7e71d263377e15c0f394ba20619c11b98e266f57fcc34f \
  --public-module-bytes 212 \
  --public-project-sha256 7d50e8c6c2bc76a0e3ddcac6b5f157b013bcfd76944fdeb2c1c81e0181ae7825 \
  --public-project-bytes 224 \
  --inputs-sha256 7b51e6fa89d7b1d3ccc043e0268f405fe072999d22bd6067aaf2f20ab43e0d94 \
  --summary-sha256 5fa65d50eb041b0e12384846c5a7de548581cbc5f9183b1f72bc5f3d703a41c9 \
  --svg-sha256 b23c43fab061df0cf192b9c5c869aee8854ad794397dc3c9512aa6f946150ab8

# Verify the preserved first Rust failure without opening a matching or build archive.
"$PY" -I -B tools/render_candidate_current_overview_v43.py \
  --verify-frozen-context \
  --source-sha256 3b3647a2090fd98e89ea421b2d2a3018983e1014adecf9f0b30731b54ca51e8b \
  --source-bytes 67805 \
  --failure-sha256 88367fd41665bbeafb0645e3b03130ca97c1c54729863372d422e693169420d7 \
  --observation-sha256 51846c742aafbfc2c42ddad75836310bba518b3a76d0f8fa1548a55128852ad6 \
  --inputs-sha256 394fb27e12b9a48fbd8bdd353930084891c09118e0cfa49fc90f596124e15017 \
  --summary-sha256 1c5ea146e6d40f0e81f2fe274f2a1a50fe01efdd074ca7ea5b36cca420d16bf0 \
  --svg-sha256 bee43e78aa59a806927a50e1e807181c62a3f6497d75add1834de2c75fdc546b

# Verify the historical independent C and Rust runner source-freeze graph.
"$PY" -I -B tools/render_candidate_current_overview_v42.py \
  --verify-frozen-context \
  --source-sha256 8e4783f7c61340ce8f291f84e2dfa802189a66353edd7a89026934d9863d1ce2 \
  --source-bytes 51652 \
  --archive-sha256 c4906928850329fa3576576221e713ce653adae17a02a4de4bac4cb006389e05 \
  --receipt-sha256 ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966 \
  --producer-source-sha256 e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8 \
  --producer-protocol-sha256 e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5 \
  --producer-contract-sha256 c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5 \
  --runner-source-sha256 c114b578ac7ebfe28b45aa3b3407b81d05333f4470fa3047fd338ed3541c185a \
  --worker-source-sha256 78634bbcb5f55c560ea4b38c81ca395f4d4d5385c285bd0a3c25b395e3dd5ee1 \
  --runner-protocol-sha256 2d773fc55fe7c0a61e044a0e7deef81c8e36ffa0a9a744f4e60901f7a953c2ae \
  --runner-contract-sha256 8eb72f1d94af85db1f1b282dda4d6ce1839f51f492ed2c7436c666d792f9b737 \
  --rust-source-sha256 c25cbdf3674fc3e054c388e53de3ed38d4b1dab0a820808c42848e1803909f5e \
  --rust-protocol-sha256 ddc5c212d3e188bc1d1cdde992bf872a38962e64d3b07d6ec7c275ba4f55f13c \
  --rust-contract-sha256 ce044f18be388ab0608d0bd3bb68751e6970973f8e6ef758971e75e6d6b584a5 \
  --inputs-sha256 ca11b1d4d7e7cd483a8ebf81fe12f36037a22608cf8ab459ce9d97d16f86dda2 \
  --summary-sha256 30b7ba546209796f950ea6720a19acb16972bf8d984841f74d45c00d4c639838 \
  --svg-sha256 3d1f05706861d662f3113dc7340ceb09731c66b137df99637819a3e8b4cbd781

# Verify the historical C-only runner and overall-results graph.
"$PY" -I -B tools/render_candidate_current_overview_v41.py \
  --verify-frozen-context \
  --source-sha256 c0ab9b19acd895a122a171ca1d9df9010de0ec732b81b0f52f29b96cbc88f87a \
  --source-bytes 50242 \
  --archive-sha256 c4906928850329fa3576576221e713ce653adae17a02a4de4bac4cb006389e05 \
  --receipt-sha256 ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966 \
  --producer-source-sha256 e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8 \
  --producer-protocol-sha256 e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5 \
  --producer-contract-sha256 c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5 \
  --runner-source-sha256 c114b578ac7ebfe28b45aa3b3407b81d05333f4470fa3047fd338ed3541c185a \
  --worker-source-sha256 78634bbcb5f55c560ea4b38c81ca395f4d4d5385c285bd0a3c25b395e3dd5ee1 \
  --runner-protocol-sha256 2d773fc55fe7c0a61e044a0e7deef81c8e36ffa0a9a744f4e60901f7a953c2ae \
  --runner-contract-sha256 8eb72f1d94af85db1f1b282dda4d6ce1839f51f492ed2c7436c666d792f9b737 \
  --inputs-sha256 3abaa207a8d25f03c59bd9f7443dcd0bfb5fd6934c7f1fa388e2abf636893fc4 \
  --summary-sha256 e2835917d55d654a6d4c167298737c51f5f3b299ab7e2bc2c2eba60f9bff4f9f \
  --svg-sha256 882e8ddb4e233a1c569c0330bbbf618f65f54bcf3d0bb59dc1c99542677dd2b7

# Verify the historical Zig-feature and six-family source-inventory graph.
"$PY" -I -B tools/render_candidate_current_overview_v40.py \
  --verify-frozen-context \
  --source-sha256 15dc12f2d6a3c329d326f8d5b53bd2b1db7e82d01bb7c55e1178bd4ec0587c14 \
  --source-bytes 50218 \
  --archive-sha256 c4906928850329fa3576576221e713ce653adae17a02a4de4bac4cb006389e05 \
  --receipt-sha256 ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966 \
  --producer-source-sha256 e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8 \
  --producer-protocol-sha256 e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5 \
  --producer-contract-sha256 c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5 \
  --zig-source-sha256 9b5cf55b9d66729b84b91470f8ba5906208ccee09312b43c329acaab2ff34010 \
  --zig-protocol-sha256 78fccd7fffd33e5ecd9a9033d8225c294d82ee07f391eb46ccd621a08e0d38e1 \
  --zig-contract-sha256 4eee672b4fe6f25f7481c34a34928f00d34a45a9e0675e024238a8ee5576fade \
  --inputs-sha256 a05ee04da984b618781bc31fe0deba6d1daf7c44256d7804e539ddd1392a2ffd \
  --summary-sha256 5e9f2216fc2a0ab4742d36a1aa49c422880a8ae17e3e1534da9b362ca0eeda92 \
  --svg-sha256 7e9189fb06410903b9f5d851648893e7984b8ecd1ba7d42c73329c1f985857e3

# Verify the historical six-family graph from before the Zig feature.
"$PY" -I -B tools/render_candidate_current_overview_v39.py \
  --verify-frozen-context \
  --source-sha256 8adb7202644da2d19a4d2f50fe191de8d84007ce9b654a427a61fb4ea883c6b5 \
  --source-bytes 115526 \
  --archive-sha256 c4906928850329fa3576576221e713ce653adae17a02a4de4bac4cb006389e05 \
  --receipt-sha256 ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966 \
  --producer-source-sha256 e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8 \
  --producer-protocol-sha256 e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5 \
  --producer-contract-sha256 c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5 \
  --inputs-sha256 22e740d2f7a22e4bd485c5d6e83204bfd2c529f1b87dd041d4ed604849b69d6b \
  --summary-sha256 d25c486e36d82069c718f82a1f6281295d539606dcd72a0a6c2c295f5a4e4ca6 \
  --svg-sha256 eecc366a7e14e3bee67a801cbf4b07e848af3659a82cc0715a90525c05652a9a

# Verify the historical corrected-reference graph from before the V4 producer.
"$PY" -I -B tools/render_candidate_current_overview_v38.py \
  --verify-frozen-context \
  --source-sha256 8d6b83cd31cdb8d1b02d94946a4f4583e818fb649010a38f35e02ff9c66eac37 \
  --source-bytes 98509 \
  --archive-sha256 c4906928850329fa3576576221e713ce653adae17a02a4de4bac4cb006389e05 \
  --receipt-sha256 ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966 \
  --inputs-sha256 754dca58a8423255fb00eb6869894b2bb79017afb59e36081b6d62b88d00ff89 \
  --summary-sha256 c8b1c018a018e4e3e26fb35c0901179945cf363d868019283f31689a8d5d411c \
  --svg-sha256 7559d6ab328420d0b59741d38e003aafc4348bf7d3932c6e51b945c3069d7eaf

# Verify the historical graph that recorded the false reference.
"$PY" -I -B tools/render_candidate_current_overview_v37.py \
  --verify-frozen-context \
  --source-sha256 4dcd5c14a63adeb159e11c86802bb4080eea82dec9240afb2f910da7bd39ef07 \
  --source-bytes 73032 \
  --falsification-sha256 319f0f75aaaea16fd1f41d814785d67060c57060852893349366cc3b482c4670 \
  --inputs-sha256 c89e9c3a2250807e10b27abf33a9e2632344edaefb821a97d317b50944cd398b \
  --summary-sha256 c2cfbec3fb096b001e7642dee1a7dcc4bdbb4dc7710b5027295b9e1a8340d4ee \
  --svg-sha256 db371864df0d2148d49be0f007195ab741b097a8c880505a8297ce383bda7ac8

# Verify the historical graph from before the reference was falsified.
"$PY" -I -B tools/render_candidate_current_overview_v36.py \
  --verify-frozen-context \
  --source-sha256 1163df648d3fc3fb6b8f07abe260955958ea3b19826fafd09ee20b6fd5ba0cb1 \
  --build-archive-sha256 c201c014f55a51454baab77d2148dc39d6024bae3273242d6eb1f1b43f419f6a \
  --build-receipt-sha256 4d4c927640c6e8c1b1e02c53350e1517b98255284218f49c2cefb53d647e9805 \
  --inputs-sha256 0b5587a1b9790ee33ca00f6234efe162a79019618334b2726e2b239a425c230c \
  --summary-sha256 a082592fbb9aa29e9c577aac32c5f4b9db0e2bd503e149df0f1a39ee44b0cad6 \
  --svg-sha256 a94a73b62ac356acf54bcf3e066857b2160176d7f63c0cd44597641d1739d764

# Verify the historical graph from before the corrected Rust build.
"$PY" -I -B tools/render_candidate_current_overview_v35.py \
  --verify-frozen-context \
  --source-sha256 390373ef8d196c54301ba6917b15b847708359dd27724f7463d9497e706aa618 \
  --reference-archive-sha256 7875f249a6cec7910e31800566ef5ccb1ee7398a29a403f307c5de88e647736c \
  --reference-receipt-sha256 29b4a389e1b99cce15f07069ee1a0895f193e13400f944a037a4f42832619334 \
  --inputs-sha256 e90ba3ac5bce1b4c73e1005e740d36c1d24d94a065f71d154ae50075895cf73a \
  --summary-sha256 5cf793bbd79a65720b4081809c53333b028f133f51143ee22acb3ce43b805367 \
  --svg-sha256 bc4ec953b521973d4f2ee69db36e75d4e9ec539b4025e1cef3ad90a7c18315a3

# Verify the historical graph from before the extra Python reference.
"$PY" -I -B tools/render_candidate_current_overview_v34.py \
  --verify-frozen-context \
  --source-sha256 cf4f7b0749d0e3aa6c15d4e5444762441265773fbb90c1ebbceff0f65e3e841f \
  --campaign-archive-sha256 ab857c82369ea0c1a443d2d140c8009d7f4b5216b5ee6a0bb4e9280000cb9d6b \
  --campaign-receipt-sha256 40be94851ae23d8c4a9d2ac759d28231605247a499b0703e727c757d25b2fb96 \
  --inputs-sha256 d191ad36dd230b97c3d017f0d775a185c0a7f449adb27f7412c54c4d4308c8fc \
  --summary-sha256 09236e77646160009b322bb02f60652eeb0b13f2b1f9440bfef2e176644e9df4 \
  --svg-sha256 59ff6affa120980c8d25206a71d2b2377619e93796a6ca0f15a65229a87dffce

# Verify the separately preserved historical graph from before the Zig test.
"$PY" -I -B tools/render_candidate_current_overview_v33.py \
  --verify-frozen-context \
  --source-sha256 e81a1c032c550475c4a4ece9ae11b903d105d62e8666ce46b69138b260ca91d5 \
  --build-archive-sha256 3e0ccc41de392c17eaec64100776eacecafb3f0bb3355e18ef4d65fcdc79ea8d \
  --build-receipt-sha256 6269fb49b67919e772ffbcdd211c696aae871971ab524bc0b1612a797d4c2f9b \
  --inputs-sha256 1f98790a6a31d8cdf298bf5fd13c6d4d14cfb44785e1e445d791c83557de921e \
  --summary-sha256 b56b5f0e09ff3aa3990b210934e1d73d1989bd03c6bb479a8a7abd66eb93a9a6 \
  --svg-sha256 203c15b16b74cf1dd8be3308677ddd67fa94a7a8411e5de38b43186647ccf858

"$PY" -I -B tools/verify_python_re_callable_introspection_v1.py \
  --verify-frozen-context \
  --source-sha256 5a64fb4546bdccd13b6d8d9ba32a7472b01cb86dd0d9f2c643678e6bbf919653 \
  --protocol-sha256 1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8 \
  --contract-sha256 e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349

"$PY" -I -B tools/run_owned_callable_introspection_reference_v2.py \
  --verify-frozen-context \
  --source-sha256 00c543077bfbe38e5c48e9970f7881119d21cb32cf91e838d21587f8f820ada4 \
  --protocol-sha256 1e316b848e5d7a44b83a8f44605f08370faacb33074c2b79c042c76d9390a59f \
  --contract-sha256 0f87ef8926771cfe39e33d95b3b871f03c9f1c44fe932615f7067d391eb68f42

"$PY" -I -B tools/apply_owned_zig_scanner_capture_source_repair_v2.py \
  --verify-frozen-context \
  --source-sha256 87a4cf8895b5d52c346213ef8277c17b66af44eba695bc37fac5198e0169b6ff \
  --protocol-sha256 eb71f594968a497ddeef5aaf0ab9f221d46153be47e69402a1f0090fa6597879 \
  --contract-sha256 3afc80a62a50ee55d059b6a19fc74915ca0a8cbdeddd9efa723722b2629ee85e

"$PY" -I -B tools/reproduce_owned_zig_scanner_source_build_v12.py \
  --verify-frozen-context \
  --source-sha256 5192fa35dd0b13cb3bdddfc8f24c37d7e797d0b8463d000c4692c8131f33d1b6 \
  --protocol-sha256 f80743d8109402e5876792b6713237b1ab770e3286874dd5ae47fb56381131b1 \
  --contract-sha256 5abb6f60c7a9672e32d6f2980a109ccb15b7ef56e5cc3a81abda458109552c1a

"$PY" -I -B tools/apply_owned_go_unicode_name_source_repair_v1.py \
  --verify-frozen-context \
  --source-sha256 a32f1062ef507903edc3a7cb5d0462853528e57582dd61e24e97fd1cc7737561 \
  --protocol-sha256 fa738f2365a087d07d3860b23278fb20da00300e0d3eb3df09b6d3584f3b4c95 \
  --contract-sha256 b48d52c712288b037f2b2f88a69e658d8a389fd9ab469fb1999f80debc582d33

"$PY" -I -B tools/apply_owned_cpp_public_argument_source_repair_v1.py \
  --verify-frozen-context \
  --source-sha256 05681d65d080ff7c67d9afbf8dd22275123dbd0542afa8079121c4134c542d65 \
  --protocol-sha256 3d97db34bbbe41ee7a841bb9e5eef7737415749bbc5645a6ab90f70f42a24271 \
  --contract-sha256 ff3918853438e80778f1179057ebdf3618b395f999fe6a88494d3575b03be765

"$PY" -I -B tools/run_owned_repaired_rust_original_campaign_v4.py \
  --verify-frozen-context \
  --source-sha256 7d63b397deddd5c23af075754fcb50f7b3bdfb44390269383aae7903d46b4dd0 \
  --protocol-sha256 5296b7ed7c3ba37ce4e299924e9e9edae849bebcd0e92e828977ae9ac6c9e26b \
  --contract-sha256 26e86429e1e437fc791401197fb8c6dd9cf399bb025bd027af5f9c2554d6f60b

"$PY" -I -B tools/apply_owned_rust_public_contract_source_repair_v2.py \
  --verify-frozen-context \
  --source-sha256 d0f90145195e9978482a7797956ef916adb1d0612118c2fc6343c4f38b823fa8 \
  --protocol-sha256 3f469ca7298b08cc1d50d18aff5029ae17a3f4f318c4fc7a2d8f8f45cc16e239 \
  --contract-sha256 b87c876e16041b0e08619aec0a86a069598b54478a1fa55cc9baa220c2c1f53b

"$PY" -I -B tools/apply_owned_rust_public_contract_source_repair_v3.py \
  --verify-frozen-context \
  --source-sha256 5e57da2379e736bba75eacdb57f84710dc144c0d4088d5827b3139a6b71d8859 \
  --protocol-sha256 2aeb81e55548b46011c75815465d2bc2fa461d57ba7b990fc7a7b87d2d687a34 \
  --contract-sha256 82bce0066181dd16f3de52d88f31e930f25706b5ff3da2ba18b10c8b31b4f6a1

"$PY" -I -B tools/reproduce_owned_rust_flag_source_build_v12.py \
  --verify-frozen-context \
  --source-sha256 1b3f8333f36a6262e962647719ed99b00dd1519a704bf7f07a5d1f1d56377db6 \
  --protocol-sha256 822857ed434cf1273c0d5eaf14f540d0398c744fee8e14b7b7734238dc2d9950 \
  --contract-sha256 c1c68590a1b45005fb709dc00a6a5f86e6564ed494e179fff9480ea5bed7b592

"$PY" -I -B tools/reproduce_owned_rust_pattern_repr_source_build_v13.py \
  --verify-frozen-context \
  --source-sha256 2ec050c9902cbb3a239ed3a2dce3258344300b40546e37aea374cf18a9c8b797 \
  --protocol-sha256 3c486fdb63041b4f6060a6147186dd93c8339cbdff5f8060f597ab156ff05701 \
  --contract-sha256 15023a0a484715f2d97ae5ea9649bb16fe3d30781d601635bda40c246c5906aa

"$PY" -I -B tools/run_owned_repaired_c_original_campaign_v4.py \
  --verify-frozen-context \
  --source-sha256 e1730319db687828e7a283574cfd3daa8fb41c936025965c140b5b9de12978a5 \
  --protocol-sha256 79f5f81aedd85b9a59c121b0a3ae96ca3fc3307a34c1427464762ae569f4d473 \
  --contract-sha256 83a00d475acb9e5e103ed9ed6f4a58e116da47db462322f4bb05bd406b4c09f4

"$PY" -I -B tools/activate_verified_native_candidate_v6.py \
  --verify-frozen-context \
  --source-sha256 d3a9b08c1bf7e3408719a0e92b8c1965aa6160dd2e18ab1501bb8662aaf8e4a1 \
  --protocol-sha256 0e736d575835fa22388841a527e22b62eef1ddf39eac9415bd7c518ba985b1d0 \
  --contract-sha256 e0d486cc6d621e963f8af5db1c4f7a47d590ad679837db1f53e11d05b670332e

"$PY" -I -B tools/activate_verified_native_candidate_v7.py \
  --verify-frozen-context \
  --source-sha256 98002a0a283ffec24670bcb9f35546c5720d2a7a1d098257729d244918022f8e \
  --protocol-sha256 f333b50f9810cf246ae659c6d07eb4c63b8e2114d07b485b50d570ab272f22f8 \
  --contract-sha256 62375f7d013b7b02a160b9492e5aa249b7af556041f2c86f20e7bfd5ad6885b1

"$PY" -I -B tools/run_owned_repaired_zig_original_campaign_v1.py \
  --verify-frozen-context \
  --source-sha256 ff4bc83173930c193de5984659aa6e8aca1848496d06f3d3dca3c28294c37c90 \
  --protocol-sha256 974c1cc09511c7a119a2ea0f59fab8c39e8d1887c948df19657de2458b5b9d67 \
  --contract-sha256 f3f1bdfea41b8b4d5bce22b2b236c76f653e97268e500b951fbef262052718f0

"$PY" -I -B tools/run_owned_repaired_zig_original_campaign_v2.py \
  --verify-frozen-context \
  --source-sha256 a9f62061f709583c60a4d0b72ba1150931132a66b80b6eed1081e017fd389795 \
  --protocol-sha256 fe17a8fc4e5fb5638ff92caa6e1b6d625e93dfb27ced02ba7b1490b830356db3 \
  --contract-sha256 0112748e8dbca769625ea2643643fad81ced069e20ed87a458bebe0a922d2851

"$PY" -I -B tools/run_owned_repaired_zig_original_campaign_v3.py \
  --verify-frozen-context \
  --source-sha256 e4efad7dfbe921bec9f7160cd33dbbed0376b1373037a78de8bcaabdcd2ece98 \
  --protocol-sha256 0463e23aaed9de6e1b50db7f106a1f175b504eefdbf868fa1f03ed5b313776d1 \
  --contract-sha256 4d20518685e2db7b80c9a1936f4ae480cff85c2a3b672562f6d4fded20b8328d

"$PY" -I -B tools/run_owned_repaired_rust_original_campaign_v2.py \
  --verify-frozen-context \
  --source-sha256 a6ffce3eb9ff09f27f3e35f84b35b9d1aba6e29dae225c56c036de85e089b7b3 \
  --protocol-sha256 9b9a246a08c0e89667899a6317df41424320617f7c4ac6cb84ef210fabee1ca0 \
  --contract-sha256 bc100f6a7a3d4ec2640e131211ecea202172846daa10c93d73cbf58ea74ed547

"$PY" -I -B tools/run_owned_repaired_rust_original_campaign_v3.py \
  --verify-frozen-context \
  --source-sha256 23819da6e6bb1ce8b27144a5d974b4bb0ecac845c844cb6fadae2ba01b2ef3d2 \
  --protocol-sha256 c29edb7751045da17cce2052e028b92530d8eab5ba6b8adafc21135a746f7883 \
  --contract-sha256 ab4b424570254201865394330e025850b4626dfe2eaacd4ec82f41d2e99b0980

"$PY" -I -B tools/preserve_owned_zig_campaign_preflight_failure_v1.py \
  --verify-frozen-context \
  --source-sha256 4a401ea42b4446535d51d1c7c65c688196185a0bb9fa2e15aebdb3bfebb85498 \
  --protocol-sha256 a3c005c95c61a68a5683125f7805564f4749ea9e82350f2d883da9e29b2817c5 \
  --contract-sha256 534a3cde3084c12a4124f5dea057ddb80b53fa4c591c8c72e26931bc277735f0

"$PY" -I -B tools/apply_owned_first_party_source_repair_v2.py \
  --verify-frozen-context \
  --source-sha256 1bb4f21cca20928b1c8993b3646825ac04ad46a231633105e5cb2469fd8434c0 \
  --protocol-sha256 a91fd1615d25597109c11605fdbeadd1673137cdd819b326bfff5dfb5699b611 \
  --contract-sha256 875b9402f535b94a1391bc3a1821ac347f67f09b2341c9a7a489a79b7dd9cf48

"$PY" -I -B tools/reproduce_owned_c_pickle_source_build_v12.py \
  --verify-frozen-context \
  --source-sha256 654e4dea29b9f687a27b53fa18b2f345e29042a03ea4b507594e87fa3e4a161f \
  --protocol-sha256 aecb2cacfc5397a46e2d123767d4b7bf39935d1bda95d3b0d0cf8058614769ac \
  --contract-sha256 5c3bc3487962c9b66cd63155a0ca0d7fc18aa4debac47ee9a75123a678d800b3

"$PY" -I -B tools/reproduce_owned_c_pickle_source_build_v13.py \
  --verify-frozen-context \
  --source-sha256 697b0959acf12ae779553f6c2654663d0358cd8c834f59b39850aad2b1fd683c \
  --protocol-sha256 2b8cdfcfa3274b2ebcf6eac29fd3680fa9c748efe2084cd65b0edd780ab2d387 \
  --contract-sha256 29a8afd92b7d3b533b8c0ba804946d31d107ebecef7ca27993eb1b8b9d1abc7d

"$PY" -I -B tools/reproduce_owned_c_pickle_source_build_v14.py \
  --verify-frozen-context \
  --source-sha256 60af4a7351ab8b9afec4e0863c281c452bfcd95193c2fdf46e1be3fed99854c0 \
  --protocol-sha256 be7872faf61547b4485f90a913fe44819a885d30020a135d80a4aafe6b5c97cc \
  --contract-sha256 dcef5ca8d97c638fb82221d1898e0dbb7ed10cfe4ecd0ae1d5923f8d271c3ec8

"$PY" -I -B tools/reproduce_owned_c_pickle_source_build_v15.py \
  --verify-frozen-context \
  --source-sha256 91bc1985ac1edad757a3b027840db3f08aa97a781df1542e33b39d39f04aa7d8 \
  --protocol-sha256 fab2219a4c4a0cf78acfe8adbb039aba591a450409d9cc75347d552d9d0e4727 \
  --contract-sha256 7fb1409eb228deb034626efb9b5bb1781c1cd139343d18e87acdac6deab97285
```

The earlier pinned context checks below reproduce historical source freezes.
Each intentionally authenticates the exact evidence inventory that existed
when it was committed. Run one against its corresponding historical commit;
it is not a verification of the current lower bounds of **164** evidence
owners and **169** authenticated references.

```sh

"$PY" -I -B tools/render_candidate_current_overview_v24.py \
  --verify-frozen-context \
  --source-sha256 a639a39a2b476777e47aecb6850617213491d99698b391a4f905dc1653f25b4e \
  --zig-build-archive-sha256 e4a1f369b647f588ac5b12585f7d0e30c4ee3409adc88f660081fb7a59a8df5c \
  --zig-build-receipt-sha256 d53766d0dad571f8b72288cece15fb1ad0892db32c3b3b6b512027db94ca4fcc \
  --inputs-sha256 9a01881fca3d090d0b0a95b392b73d2941b330a5acd5144ffaf6a865e5f0cc34 \
  --summary-sha256 719a3dec863e5f7c78c1c2bc37f7ee06057f9de0ed9cefca74dee0c6dceeceac \
  --svg-sha256 44f56757ca5c908412668c7679006dab288655ab0a419da59ac9265e7cb3aed1

"$PY" -I -B tools/reproduce_owned_native_source_build_v11.py \
  --verify-context \
  --source-sha256 3fb0ca1b6914617eb8a6f491072fcb40b15a364afacbaec2d4caac1e9b6f5d10 \
  --protocol-sha256 bd6bce6b14bebe55691900e4a48bb8acf89197660e1d5ebd4c8c38e979c05fe6 \
  --contract-sha256 7b1f8941444e942a85eb9f9df9dc23244112763ca92381fe22f76fd87c95a87a

"$PY" -I -B tools/reproduce_owned_zig_scanner_source_build_v11.py \
  --verify-context \
  --source-sha256 b908f12d14fb8ebc5f17c62dfc00d48a1a5ee3717a3144aed437059e21c0f097 \
  --protocol-sha256 15fd222876407be72d36c0b9cf2ce581d8b73a954358df192c2a083a08973539 \
  --contract-sha256 92979e4bfacd6d23e7f54f4fdce7a7707cc54dba2512753029fdcd479150464c

"$PY" -I -B tools/reproduce_owned_native_source_build_v10.py \
  --verify-context \
  --source-sha256 e2e9163968aa8c07dfa2cd5d05451e580eab1a1641edc4c53fd804ba51840d7b \
  --protocol-sha256 1edd8ebf3705cd58d27b78b9ff14a751ae0efe4471f1eb2ad25895380448485a \
  --contract-sha256 0ba4cf203f876cd9c75a5d76b88186e571c8963eba83f6ccecad3f03d662e7f4
"$PY" -I -B tools/run_owned_frozen_p0_v9_live_context_adapter_v1.py \
  --verify-frozen-context \
  --adapter-source-sha256 82d9ba024400b73ec8d99866609241871ba6e4b057a4c2c0fcd9ebf225b621cb \
  --adapter-protocol-sha256 51f9cede20828da51f127ee9e34c814d306c52252804f77d5c2e95ced2bf4f2c \
  --adapter-contract-sha256 a404db028e2d5bd1ea246e58c11e5a40af2d990909a8d69fac9dbb881bf169b8

"$PY" -I -B tools/run_owned_repaired_c_original_campaign_v3.py \
  --verify-frozen-context \
  --source-sha256 bdf846bca02c80d15e37db8d26fad45d7dacd3f3dee7ec94ce4151315423994f \
  --protocol-sha256 d4aa6a11d6c1398109de454f3d23e5e20d488913a00b37adfd05b47f9f53522e \
  --contract-sha256 1150def4ccc3e3c64773d3bdf854e0f6b04d5b6560a6dc04deeba38c8049da16

"$PY" -I -B tools/apply_owned_rust_public_contract_source_repair_v1.py \
  --verify-frozen-context \
  --source-sha256 ac98ad24c6a4962fb38535cbaa470ae5cd4983643e7e8962e9fc9a1b6a0e12a0 \
  --protocol-sha256 a297cbccfe4d4a2a321e7f8fe518662f451fd84f90e17bf86c62cf579875955f \
  --contract-sha256 a3b4670c3e321cefd6a1ec65ba80b9aa1a06534a73e30ba56654cc75f6f11431

"$PY" -I -B tools/reproduce_owned_zig_scanner_source_build_v10.py \
  --verify-context \
  --source-sha256 4d2bf61385c310bc95fc353492ad3b9a4a1687ee1cd46c5822cf2a8eb6d61578 \
  --protocol-sha256 99d8144cd083663145f2924ae96a285b32fffb05a11a37d35ec81c81142c9148 \
  --contract-sha256 7192419e64dd460f78977bd92afea0bfe7871bd10788500de699d7d89b2961c7

"$PY" -I -B tools/apply_owned_zig_scanner_capture_source_repair_v1.py \
  --verify-frozen-context \
  --source-sha256 963f306373753b9fef84c9a9784668f42067cb905b84347a0bcc99e1e8692515 \
  --protocol-sha256 7a40b58bcc69744fc6b749368ec307be7d05d742de3d921410fd2753a4f5c8d0 \
  --contract-sha256 c48fcd9cb40cbe15442c2dd197627d7f4ccc341b3edfbbe0c645405015c8ea87

"$PY" -I -B tools/run_owned_six_family_original_p0_producer_v3.py \
  --verify-frozen-context \
  --source-sha256 7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c \
  --protocol-sha256 88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76 \
  --document-sha256 47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1

"$PY" -I -B tools/run_frozen_p0_candidate_worker_v7.py \
  --verify-frozen-context \
  --source-sha256 855c59acdc0b5270493ece8fc39548a89e0febf94d6b186ac9f0e5a50754f68f \
  --runner-source-sha256 1511dac06dab5ce319b4dd09cb6f8c5a12160c48cc0dbbdfa7e7fe3f0d426702 \
  --protocol-sha256 afbb933eb022efaca7cb9604bc1614d3d2de7e3faf33f446234f725cd331771f \
  --document-sha256 a9609b0576aab4e0ea7ff6f9ae2a466c0d77d0af134a7f0bddf83ed01f61d631 \
  --producer-source-sha256 7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c \
  --producer-protocol-sha256 88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76 \
  --producer-document-sha256 47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1

"$PY" -I -B tools/run_frozen_p0_candidate_v9.py \
  --verify-frozen-context \
  --source-sha256 1511dac06dab5ce319b4dd09cb6f8c5a12160c48cc0dbbdfa7e7fe3f0d426702 \
  --worker-source-sha256 855c59acdc0b5270493ece8fc39548a89e0febf94d6b186ac9f0e5a50754f68f \
  --protocol-sha256 afbb933eb022efaca7cb9604bc1614d3d2de7e3faf33f446234f725cd331771f \
  --document-sha256 a9609b0576aab4e0ea7ff6f9ae2a466c0d77d0af134a7f0bddf83ed01f61d631 \
  --producer-source-sha256 7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c \
  --producer-protocol-sha256 88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76 \
  --producer-document-sha256 47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1

"$PY" -I -B tools/run_owned_repaired_c_original_campaign_v2.py \
  --verify-frozen-context \
  --source-sha256 047eb7acb5a9febd8172f386061a20de5f17be36e9798d55c1c1e30e813594ab \
  --protocol-sha256 bd89b3e09b1268a65475ad992b2858e2167368a82ee97d1b90b1fa36b32438b0 \
  --contract-sha256 b3c16de03165b5e95529923a2475c73c51fce9a48a871aa61804b97fcca782de

"$PY" -I -B tools/run_owned_repaired_c_original_campaign_v1.py \
  --verify-frozen-context \
  --source-sha256 51caee9c71ab2f7c2007ecd3ea9c9ced590f3f0c9d3ac1ee8bc8e2ae2574bff0 \
  --protocol-sha256 de88fe5506107d88130bd6caca56f9d41114516649b3ed3398bbd7b4979b3108 \
  --contract-sha256 c88d02cd0f6a6785ee2b907148e2a1691ff7e55f7da006ede0d01c2abcf62d9b

"$PY" -I -B tools/run_frozen_p0_candidate_worker_v6.py \
  --verify-frozen-context \
  --source-sha256 4fbe0885e78797ca9c46d81477229252fb7e2e85801cfe35304457cd39d141c1 \
  --runner-source-sha256 3081c956f5933e03b42ca2d33c9801c58cde6a05ff332b9ef6560e00afc73b60 \
  --protocol-sha256 db0741f73f08602e92de435333201c9010e6eab123733e21d33f30dcac2cdf96 \
  --document-sha256 3bdbbe85d0c823b2cf2142d686ca581ef51cef439c4fc880d56bf0bc2cae32cc

"$PY" -I -B tools/run_frozen_p0_candidate_v8.py \
  --verify-frozen-context \
  --source-sha256 3081c956f5933e03b42ca2d33c9801c58cde6a05ff332b9ef6560e00afc73b60 \
  --worker-source-sha256 4fbe0885e78797ca9c46d81477229252fb7e2e85801cfe35304457cd39d141c1 \
  --protocol-sha256 db0741f73f08602e92de435333201c9010e6eab123733e21d33f30dcac2cdf96 \
  --document-sha256 3bdbbe85d0c823b2cf2142d686ca581ef51cef439c4fc880d56bf0bc2cae32cc

"$PY" -I -B tools/reproduce_owned_native_source_build_v9.py \
  --verify-context \
  --source-sha256 c4a4b85b92ef0d600528732c9e0acb8f8303b7b2fbfc320e84c9b9e2d384219f \
  --protocol-sha256 18494d4b778a3c958b07903996e8a1b13f4466e08b2c9e72cd5d711957dbcecc \
  --contract-sha256 6a4aee7f0c639b2b338d1497c35a69d35939841cf55b0dbe38abe404cea404da

"$PY" -I -B tools/activate_verified_native_candidate_v5.py \
  --verify-frozen-context \
  --activation-source-sha256 bdfcb93e4ac3f436474cf82725165c92b61c8982efff0bf113900cbce3e8aff5 \
  --activation-protocol-sha256 4693558f9796a0fbf38326fda3a86b2cf19348598b21eab60610df6ee7f241bc \
  --activation-contract-sha256 a580c6b745c867a69f1f017506c1feec8310aa3070bfd58abd006740b01948da \
  --build-source-sha256 afc4f8070cb3c1bccf312b77b019cbb6d71f8dcf976f4a2e921e18cc7c063dd4 \
  --build-protocol-sha256 376aae2bdcbeb0c399369c2a15e7e39efb2b1bcce53129a20c229fbbb995cda2 \
  --build-contract-sha256 7f463b70367156d65e73b561629bd1e14ae265b2273afae9b0a984608492019b

"$PY" -I -B tools/apply_owned_rust_source_repair_v1.py \
  --verify-frozen-context \
  --source-sha256 1d5d9b5e3fecb278fdcb97ef21dadff9134cdd779cb6751c42d4931096796851 \
  --protocol-sha256 df9ce744660a4328a2b83151a3320aca64a7ad1606e14a4509f50f638a4afc7b \
  --contract-sha256 1ef69922310cb40166896685c75004c9f423a78e5bb96341a545d4dc75a1cf9b

"$PY" -I -B tools/reproduce_owned_native_source_build_v8.py \
  --verify-context \
  --source-sha256 afc4f8070cb3c1bccf312b77b019cbb6d71f8dcf976f4a2e921e18cc7c063dd4 \
  --protocol-sha256 376aae2bdcbeb0c399369c2a15e7e39efb2b1bcce53129a20c229fbbb995cda2 \
  --contract-sha256 7f463b70367156d65e73b561629bd1e14ae265b2273afae9b0a984608492019b

"$PY" -I -B tools/apply_owned_first_party_source_repair_v1.py \
  --verify-frozen-context \
  --source-sha256 c04bbc8e7bc45bdbe1fb9eb93942286f5b32b39aef554db15b8b1acd9cc8cd99 \
  --protocol-sha256 1a2e83caaca5cb43fc82445c2a4fc3097bc3d51bdfc568783b8815797b8c63f5 \
  --contract-sha256 8f1a5676bbef5f2ef560d03fef910bf4ed3a4df029ecc0c638e3fa971206dab5

"$PY" -I -B tools/run_frozen_p0_candidate_v7.py --verify-frozen-context \
  --source-sha256 08ab73a0d42a2bb3bb658cf6924786a7ba396aacd229957a710866572e178690 \
  --worker-source-sha256 66f869e71e1aaf77944f4b7115e91ab34f6bc9b06fb4d17f097ea26c97c9c780 \
  --protocol-sha256 ed595cbb3d5f040454da7efff3d8330befb09dda2ac6eebc681b630b96f32733 \
  --document-sha256 16f24a46113e0a120fc5cf7fea2122d78e76445665959a9553b610a27b8843b1

"$PY" -I -B tools/run_owned_six_family_original_p0_producer_v1.py \
  --verify-frozen-context \
  --source-sha256 36451c10221857cca8c77fad7533382f4e3969a20a5cdf73c055beea1d315d33 \
  --protocol-sha256 1e7ed2cbd63e080c563dd49b4ea2a2be284d831d75739c47edecfae50373ce17 \
  --document-sha256 5206bcc097cd399cddd91a8d0356fd780b44ef7c173d70605d28a175dac71c0b

"$PY" -I -B tools/run_owned_six_family_original_p0_producer_v2.py \
  --verify-frozen-context \
  --source-sha256 fe6e82306852517580dcb90f289c643a55db8c01421230a4d7d05d6df365f9c1 \
  --protocol-sha256 3add264a113550d141379229a333d19e375f66429c2b7eb47dc3193a67f7b598 \
  --document-sha256 a210e9cac8d06b47cfc745019e4f4ab3a0c465ff63a38add0bc2b83b1cd986e3

"$PY" -I -B tools/run_owned_six_family_original_p0_campaign_v1.py \
  --verify-frozen-context \
  --source-sha256 50ac9f549739bb6b540f1762177f25b46c1fa345dce717ea7163e15d98ae7e88 \
  --protocol-sha256 01d5908b9c1c3c356059a21cd0b418a7278559843d465e9062155b68f6497422 \
  --document-sha256 c619e63dd18b8242bfc1af9e01030eff60e8d17128a83de216992b5cdc619801

"$PY" -I -B tools/run_owned_six_family_original_p0_campaign_v2.py \
  --verify-frozen-context \
  --source-sha256 6b06931ff64c5fe5b6bbbc3e970e56c0a94a24c28dfa6d3aa6140fc4d8fb54a1 \
  --protocol-sha256 e47cce8a6f60971bd3c18a4bfe248039ed9abd5b4144ec4355a77825a1435d4e \
  --document-sha256 e44960e46c590cb5ab482ef323f3ae8598900f144b53a2377f62b3bb827935d7

"$PY" -I -B tools/preserve_owned_go_campaign_publication_failure_v1.py \
  --verify-frozen-context \
  --source-sha256 105b7e730eae779396840ccaca13152554244ea615e5403930e0adbd2344f5ba \
  --protocol-sha256 5e067f3d71c0997be69cd5e3eb246c2e1c9387cd40616230e806ddf561994f4f \
  --contract-sha256 f095f94f74255432b0ceff7eb1239e28d6e4e4effeab19d4f2fed86156b2925b

"$PY" -I -B tools/reproduce_owned_native_source_build_v7.py \
  --verify-context \
  --source-sha256 20d8e43a9c70f585049f81d38f9085661b50e4bf754320a6abcd95d566d854a7 \
  --protocol-sha256 a7a5ce16bb7a98dfd6e0e4f9f3777912687aa09259cc1669c5e0932da2287313 \
  --contract-sha256 cfc774cfce1a0c4298f01e298d7ffaa982300375ba117e316bff2ebbf0be7819

"$PY" -I -B tools/render_candidate_current_overview_v19.py --verify \
  --source-sha256 8144272f7c91e3821306a4d3963c8e201c68b275cecacf80d5000dd98c502494 \
  --go-bridge-sha256 52101f0afe29a568e3c2e22a06d47c89c051e08a0e2024ad4891c5ae2d60fb6a \
  --manifest-sha256 8f1eb51ff477f0b59934ee503d9bf795f472fd6674180e2af244c7ad4504560c
```

## Reproduce the corrected Rust build

The following is the exact pinned command used for the recorded build. It
creates two private snapshots and exclusively publishes the named evidence
files. Run it only in a fresh checkout where those result files do not
already exist; it does not overwrite published results, activate a
candidate, benchmark the engine, or test compatibility.

```sh
"$PY" -I -B tools/reproduce_owned_rust_flag_source_build_v12.py \
  --build \
  --source-sha256 1b3f8333f36a6262e962647719ed99b00dd1519a704bf7f07a5d1f1d56377db6 \
  --protocol-sha256 822857ed434cf1273c0d5eaf14f540d0398c744fee8e14b7b7734238dc2d9950 \
  --contract-sha256 c1c68590a1b45005fb709dc00a6a5f86e6564ed494e179fff9480ea5bed7b592 \
  --label phase2-v12-rust-flag-original-p0 \
  --bridge-derived-sha256 4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257 \
  --bridge-derived-bytes 176118 \
  --public-derived-sha256 f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5 \
  --public-derived-bytes 31464 \
  --owned-source-sha256 candidates/rust/Cargo.lock=267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63 \
  --owned-source-sha256 candidates/rust/Cargo.toml=2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966 \
  --owned-source-sha256 candidates/rust/py_bridge.c=f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b \
  --owned-source-sha256 candidates/rust/src/lib.rs=c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d \
  --owned-source-sha256 candidates/rust/src/newline.rs=13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b \
  --owned-source-sha256 candidates/rust/src/search.rs=4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe \
  --owned-source-sha256 candidates/rust/src/stack.rs=5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e \
  --owned-source-sha256 candidates/rust/src/unicode_tables.rs=f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af \
  --owned-source-sha256 candidates/rust_candidate.py=6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b
```

## Reproduce the complete corrected Rust compatibility test

This exact command temporarily activates four Rust files and creates a
durable recovery journal before the first replacement. Run it only in a
fresh environment where its recovery root and evidence do not already
exist. It runs the original **31,237** checks, restores all four original
inodes, and reports an unsuccessful candidate truthfully; an exit status
of **1** means the matching test found real differences.

```sh
"$PY" -I -B tools/run_owned_repaired_rust_original_campaign_v4.py \
  --run \
  --source-sha256 7d63b397deddd5c23af075754fcb50f7b3bdfb44390269383aae7903d46b4dd0 \
  --protocol-sha256 5296b7ed7c3ba37ce4e299924e9e9edae849bebcd0e92e828977ae9ac6c9e26b \
  --contract-sha256 26e86429e1e437fc791401197fb8c6dd9cf399bb025bd027af5f9c2554d6f60b \
  --family rust \
  --label phase2-v12-rust-flag-original-p0 \
  --activation-root /tmp/rebar-phase2-repaired-rust-original-campaign-v2-safe-v4-phase2-v12-rust-flag-original-p0 \
  --producer-source-sha256 7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c \
  --producer-protocol-sha256 88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76 \
  --producer-contract-sha256 47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1 \
  --build-source-sha256 1b3f8333f36a6262e962647719ed99b00dd1519a704bf7f07a5d1f1d56377db6 \
  --build-protocol-sha256 822857ed434cf1273c0d5eaf14f540d0398c744fee8e14b7b7734238dc2d9950 \
  --build-contract-sha256 c1c68590a1b45005fb709dc00a6a5f86e6564ed494e179fff9480ea5bed7b592 \
  --build-archive-sha256 840a6403699fec44d4f725f737fc9538c997b818a48d167398ad1b95cbb9828d \
  --build-receipt-sha256 1cd7e538098711ddac017ee3375d302d4b1ba4e6da52d10d2a524103db500a2f \
  --native-engine-sha256 5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f \
  --native-bridge-sha256 7f5dfb587fc7f53ce3a7b6cfa568a6e49c009a4d0015929b4dada28cb5425c54 \
  --native-engine-bytes 658344 \
  --native-bridge-bytes 148656
```

The [complete compatibility standard](../oracle/phase1/P0-COMPLETENESS-V1.md)
contains the source-pinned, read-only full-verification command.

## Reproduce the complete corrected Zig compatibility test

The exact command below already ran once against the independently rebuilt
Zig engine and corrected bridge. All **13** workers completed the original
**31,237** checks; the engine failed with **1,764** differences and both
original native-file inodes were restored. Exit status **1** represented a
genuine candidate failure, not a failed evidence publication. Do not rerun
the already-used label or overwrite its durable recovery and result files.
Independent reproduction requires a separately frozen, unused result label
and recovery directory.

```sh
"$PY" -I -B tools/run_owned_repaired_zig_original_campaign_v3.py \
  --run \
  --source-sha256 e4efad7dfbe921bec9f7160cd33dbbed0376b1373037a78de8bcaabdcd2ece98 \
  --protocol-sha256 0463e23aaed9de6e1b50db7f106a1f175b504eefdbf868fa1f03ed5b313776d1 \
  --contract-sha256 4d20518685e2db7b80c9a1936f4ae480cff85c2a3b672562f6d4fded20b8328d \
  --family zig \
  --label phase2-v12-zig-scanner-v2-original-p0 \
  --normalized-activation-source-sha256 98002a0a283ffec24670bcb9f35546c5720d2a7a1d098257729d244918022f8e \
  --normalized-activation-protocol-sha256 f333b50f9810cf246ae659c6d07eb4c63b8e2114d07b485b50d570ab272f22f8 \
  --normalized-activation-contract-sha256 62375f7d013b7b02a160b9492e5aa249b7af556041f2c86f20e7bfd5ad6885b1 \
  --activation-source-sha256 d3a9b08c1bf7e3408719a0e92b8c1965aa6160dd2e18ab1501bb8662aaf8e4a1 \
  --activation-protocol-sha256 0e736d575835fa22388841a527e22b62eef1ddf39eac9415bd7c518ba985b1d0 \
  --activation-contract-sha256 e0d486cc6d621e963f8af5db1c4f7a47d590ad679837db1f53e11d05b670332e \
  --producer-source-sha256 7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c \
  --producer-protocol-sha256 88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76 \
  --producer-contract-sha256 47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1 \
  --publication-source-sha256 6b06931ff64c5fe5b6bbbc3e970e56c0a94a24c28dfa6d3aa6140fc4d8fb54a1 \
  --publication-protocol-sha256 e47cce8a6f60971bd3c18a4bfe248039ed9abd5b4144ec4355a77825a1435d4e \
  --publication-contract-sha256 e44960e46c590cb5ab482ef323f3ae8598900f144b53a2377f62b3bb827935d7 \
  --build-source-sha256 5192fa35dd0b13cb3bdddfc8f24c37d7e797d0b8463d000c4692c8131f33d1b6 \
  --build-protocol-sha256 f80743d8109402e5876792b6713237b1ab770e3286874dd5ae47fb56381131b1 \
  --build-contract-sha256 5abb6f60c7a9672e32d6f2980a109ccb15b7ef56e5cc3a81abda458109552c1a \
  --build-archive-sha256 3e0ccc41de392c17eaec64100776eacecafb3f0bb3355e18ef4d65fcdc79ea8d \
  --build-receipt-sha256 6269fb49b67919e772ffbcdd211c696aae871971ab524bc0b1612a797d4c2f9b \
  --native-engine-sha256 caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071 \
  --native-bridge-sha256 e5809566a166f469e7f95fc1a43e814a3beeeffa2a6e848c00a3a48215ee6726 \
  --native-engine-bytes 108888 \
  --native-bridge-bytes 133656
```

## Reproduce the candidate-context Python reference failure

This command runs only pinned Python's own `re` through the exact
candidate-facing public-type observer. It verifies the immutable
observer, candidate gate, original producer, and small reference
receipt. It imports no candidate and does not open a compressed
matching or reference archive. The command must report **96** original
cases: **48** text and **48** bytes, differing only in the fixture
class's module name. Do not run any candidate until a separately
frozen replacement runner consumes the passing same-context Python
reference.

```sh
"$PY" -I -B -c '
import collections
import copy
import hashlib
import importlib
import json
import pathlib
import re
import sys

root = pathlib.Path("/home/dev-user/src/rebar")
owners = {
    "tools/run_frozen_p0_candidate_v1.py": "c8378cd59a3b4dfaf75609c5b06f5a5ec20114d428e8e06ccc0f12ceec2076b8",
    "tools/independent_public_type_identity_serialization_v1.py": "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20",
    "tools/run_owned_six_family_original_p0_producer_v3.py": "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c",
    "experiments/rust_public_practice_v1/public-type-identity-serialization-v1-shared-suite-v1-publication-receipt.json": "6a8ce4334d0b605483e0f78a909f620a8bcdd0e5ad8cdb4fae4960fc237132fd",
}
for relative, expected in owners.items():
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected

sys.path.insert(0, str(root))
before = {name for name in sys.modules if name == "candidates" or name.startswith("candidates.")}
gate = importlib.import_module("tools.run_frozen_p0_candidate_v1")
source = gate.import_suite_source(gate.suite_spec("public_types_v1"))
support = source.preload_support_modules()
cases = [case for case in source.build_matrix()
         if case["cohort"] == "cache-pattern-type-separation"]
actual = [source.observe_case(case, re, support) for case in cases]
expected = copy.deepcopy(actual)
for record in expected:
    record["outcome"]["value"]["items"][2]["module"] = "__main__"

def sha256(value):
    raw = json.dumps(value, ensure_ascii=True, allow_nan=False,
                     sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n"
    return hashlib.sha256(raw).hexdigest()

assert len(cases) == 96
assert dict(collections.Counter(case["domain"] for case in cases)) == {"str": 48, "bytes": 48}
assert sha256(cases) == "09b5d7cb665af227b8d6c733c795d68f9a1e22c62956b9d64105a9234af6abca"
assert sha256([case["case"] for case in cases]) == "df43bd52adb112c0fde2bfe24a45200ca2ac30a9c41dfdc5716e3e81cbe19ce0"
assert sha256(expected) == "df849727d5aa74cbec19950c2d56764bd592404b76c49abe87418bccd3a5013a"
assert sha256(actual) == "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
after = {name for name in sys.modules if name == "candidates" or name.startswith("candidates.")}
assert not before and not after
print(json.dumps({"status": "FALSIFIED", "case_count": len(cases),
                  "candidate_imports": 0,
                  "original_denominator": 31237,
                  "named_context_sha256": sha256(actual),
                  "holdout": "NOT OPENED"}, sort_keys=True))
'
```

## Verify the corrected first-party Go source freeze

These commands reproduce the rejected historical V13 source-only
checks. They verify the independent Go sources but do not exercise the
build recorder's failed-process accounting. Do not run V13 `--build`:
independent review established that it would omit failed-process
diagnostics and cannot prove distinct process IDs. Neither command
compiles, runs Go matching, starts a reference, or opens the final
comparison. Both also pass with `env -i PATH=/usr/bin:/bin LC_ALL=C`
before `"$PY"`.

```sh
"$PY" -I -B tools/reproduce_owned_go_unicode_source_build_v13.py \
  --self-test \
  --source-sha256 0c5319b7cfe6400cf7cd577efd36d8d574ee6a8674cd28987295402ce6020b06 \
  --protocol-sha256 60edb693ec2b57cf2a03c7aca7c863320563b12a18f6daecd5ab080aded0fc11 \
  --contract-sha256 a04b93a857d5ad71105479385bc9141b15c1f5303fb2a7059539b0266515f743

"$PY" -I -B tools/reproduce_owned_go_unicode_source_build_v13.py \
  --verify-frozen-context \
  --source-sha256 0c5319b7cfe6400cf7cd577efd36d8d574ee6a8674cd28987295402ce6020b06 \
  --protocol-sha256 60edb693ec2b57cf2a03c7aca7c863320563b12a18f6daecd5ab080aded0fc11 \
  --contract-sha256 a04b93a857d5ad71105479385bc9141b15c1f5303fb2a7059539b0266515f743
```

## Reproduce the separate Python signature reference

The exact command below already ran once after its independently reviewed
source freeze was committed and pushed. Exactly **two** isolated Python
reference workers independently passed all **50** separately frozen
signature checks. The original **31,237** checks did not change; no
candidate, benchmark, or holdout ran. Do not rerun the already-used command
or overwrite its published reference archive and receipt.

```sh
"$PY" -I -B tools/run_owned_callable_introspection_reference_v2.py \
  --run-reference \
  --source-sha256 00c543077bfbe38e5c48e9970f7881119d21cb32cf91e838d21587f8f820ada4 \
  --protocol-sha256 1e316b848e5d7a44b83a8f44605f08370faacb33074c2b79c042c76d9390a59f \
  --contract-sha256 0f87ef8926771cfe39e33d95b3b871f03c9f1c44fe932615f7067d391eb68f42
```

## Reproduce the corrected first-party Rust source builds

The exact frozen build below has already run once after its three source
owners were independently reviewed, committed, and pushed. Both private
source trees were independently built, all **28** real offline compiler
and binary-inspection processes succeeded, and both native outputs matched.
No Rust matching test ran; successful compilation does not qualify a
candidate. Do not rerun this already-used evidence label or overwrite the
published build archive and receipt.

```sh
"$PY" -I -B tools/reproduce_owned_rust_pattern_repr_source_build_v13.py \
  --build \
  --source-sha256 2ec050c9902cbb3a239ed3a2dce3258344300b40546e37aea374cf18a9c8b797 \
  --protocol-sha256 3c486fdb63041b4f6060a6147186dd93c8339cbdff5f8060f597ab156ff05701 \
  --contract-sha256 15023a0a484715f2d97ae5ea9649bb16fe3d30781d601635bda40c246c5906aa \
  --label phase2-v13-rust-pattern-repr-original-p0 \
  --owned-source-sha256 candidates/rust/Cargo.lock=267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63 \
  --owned-source-sha256 candidates/rust/Cargo.toml=2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966 \
  --owned-source-sha256 candidates/rust/py_bridge.c=f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b \
  --owned-source-sha256 candidates/rust/src/lib.rs=c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d \
  --owned-source-sha256 candidates/rust/src/newline.rs=13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b \
  --owned-source-sha256 candidates/rust/src/search.rs=4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe \
  --owned-source-sha256 candidates/rust/src/stack.rs=5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e \
  --owned-source-sha256 candidates/rust/src/unicode_tables.rs=f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af \
  --owned-source-sha256 candidates/rust_candidate.py=6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b \
  --bridge-derived-sha256 4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257 \
  --bridge-derived-bytes 176118 \
  --public-derived-sha256 d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e \
  --public-derived-bytes 31934
```
