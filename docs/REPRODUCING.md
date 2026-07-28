# Reproducing the frozen rebar experiment

This guide preserves the complete, source-pinned verification commands and
evidence inventory that were previously kept in the main README. All checks
below are source-only or read-only unless a command explicitly says otherwise.
The current results and charts remain in [the project README](../README.md);
experiment history remains in [the experiment log](EXPERIMENT-LOG.md).

## Evidence and reproduction

- [Frozen Python compatibility tests](../oracle/phase1/P0-COMPLETENESS-V1.md), [all 31,237 test cases](../oracle/phase1/p0-completeness-v1.json), and [independent test verifier](../tools/verify_p0_completeness_v1.py).
- [Separately frozen public callable signature checks](../oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md), [all 50 additional function, pattern, match, and scanner cases](../oracle/phase1/p0-callable-introspection-v1.json), and [independent source-only verifier](../tools/verify_python_re_callable_introspection_v1.py); the original **31,237** cases are unchanged, and the new independent-reference and candidate runs have **NOT YET RUN**.
- [First-party engine ownership and no-wrapping audit](../oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md), [exact source inventory](../oracle/phase2/candidate-independence-v2.json), and [source verifier](../tools/audit_candidate_independence_v2.py).
- [Independent Zig scanner-capture repair](../oracle/phase2/ZIG-SCANNER-CAPTURE-SOURCE-REPAIR-V1.md), [single-block private-snapshot contract](../oracle/phase2/zig-scanner-capture-source-repair-v1.json), and [source-pinned first-party repair tool](../tools/apply_owned_zig_scanner_capture_source_repair_v1.py); the repair was independently applied to both private native builds.
- [Source-only correction for the actual Zig whole-branch scanner failure](../oracle/phase2/ZIG-SCANNER-CAPTURE-SOURCE-REPAIR-V2.md), [exact corrected private-bridge contract](../oracle/phase2/zig-scanner-capture-source-repair-v2.json), and [independently owned source verifier](../tools/apply_owned_zig_scanner_capture_source_repair_v2.py); the source fix restores the original `alpha42` span without changing the previous **2,172** measured differences. A new Zig build and its compatibility remain **NOT MEASURED**.
- [Previous reproducible independent Zig build protocol](../oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V11.md), [exact private two-build contract](../oracle/phase2/zig-scanner-source-build-v11.json), and [first-party Zig build verifier](../tools/reproduce_owned_zig_scanner_source_build_v11.py); both previous native outputs build identically. Their later complete matching test recorded **2,172** differences.
- [Current corrected from-scratch Zig build protocol](../oracle/phase2/ZIG-SCANNER-SOURCE-BUILD-V12.md), [exact independent private-build contract](../oracle/phase2/zig-scanner-source-build-v12.json), and [source-pinned first-party Zig build verifier](../tools/reproduce_owned_zig_scanner_source_build_v12.py); the corrected bridge and two independent future builds are frozen, but compiling and compatibility testing have **NOT RUN**.
- [Original two-file Zig activation and exact-inode recovery](../oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V6.md), [frozen dual-role safety contract](../oracle/phase2/verified-native-activation-v6.json), and [original Zig loading and recovery tool](../tools/activate_verified_native_candidate_v6.py); its nine-field safety check rejected genuine seven-field records for the unchanged original files before any engine loaded or matching test ran.
- [Corrected Zig file-owner verification and safe recovery](../oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V7.md), [exact descriptor-verification contract](../oracle/phase2/verified-native-activation-v7.json), and [independently verified first-party activation source](../tools/activate_verified_native_candidate_v7.py); the actual corrected campaign restored both original engine-file inodes before publishing its matching failures.
- [Complete original Python tests for repaired Zig](../oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V1.md), [exact 13-group original-suite and safe-restoration contract](../oracle/phase2/repaired-zig-original-campaign-v1.json), and [independent repaired-Zig original-suite controller](../tools/run_owned_repaired_zig_original_campaign_v1.py); all 31,237 original checks remain frozen, and the first controller attempt stopped during setup before any candidate test started.
- [Corrected complete original Python tests for repaired Zig](../oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V2.md), [exact original-suite and preserved-failure contract](../oracle/phase2/repaired-zig-original-campaign-v2.json), and [corrected first-party Zig correctness controller](../tools/run_owned_repaired_zig_original_campaign_v2.py); all **13** groups actually ran, revealing **2,172** matching differences and **zero** infrastructure failures. The [complete lossless matching-failure archive](../oracle/phase2/evidence/repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-original-p0-failures.json.gz) and [separate durable publication receipt](../oracle/phase2/evidence/repaired-zig-original-campaign-v2-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json) preserve every worker and both restored original files.
- [First repaired-Zig setup failure](../oracle/phase2/ZIG-CAMPAIGN-PREFLIGHT-FAILURE-V1.md), [complete pinned traceback and failure contract](../oracle/phase2/zig-campaign-preflight-failure-v1.json), and [failure preservation verifier](../tools/preserve_owned_zig_campaign_preflight_failure_v1.py); one controller exited 1 before any Zig test worker began. Its exact traceback is preserved in the [compressed original-failure archive](../oracle/phase2/evidence/zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-original-p0-failures.json.gz) and [separate durable publication receipt](../oracle/phase2/evidence/zig-campaign-preflight-failure-v1-zig-phase2-v11-zig-scanner-original-p0-failures-publication-receipt.json). Receipt success verifies preservation, not a successful Zig test.
- [Corrected original Python test producer](../tools/run_owned_six_family_original_p0_producer_v3.py), [unchanged original-test and first-party ownership protocol](../oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md), and [exact source-pinned contract](../oracle/phase2/six-family-p0-producer-v3.json); both real Python reference processes and all 31,237 cases are preserved.
- [Corrected complete original-suite protocol](../oracle/phase2/P0-CANDIDATE-PROTOCOL-V9.md), [exact case and worker inventory](../oracle/phase2/p0-candidate-protocol-v9.json), [corrected isolated-suite worker](../tools/run_frozen_p0_candidate_worker_v7.py), and [complete 13-suite runner](../tools/run_frozen_p0_candidate_v9.py); all 13 repaired C candidate workers ran and preserved their complete results.
- [Frozen correction for the original C test coordinator](../oracle/phase2/P0-V9-LIVE-CONTEXT-ADAPTER-V1.md), [exact immutable original-worker adapter contract](../oracle/phase2/p0-v9-live-context-adapter-v1.json), and [independently verified original-worker adapter](../tools/run_owned_frozen_p0_v9_live_context_adapter_v1.py); all original corrected-suite worker records are preserved.
- [Recovery-safe corrected C campaign rules](../oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V2.md), [exact restoration and full-test contract](../oracle/phase2/repaired-c-original-campaign-v2.json), and [complete recovery-safe original-suite controller](../tools/run_owned_repaired_c_original_campaign_v2.py); its one genuine runner failure and exact restoration are independently preserved.
- [Complete repaired C original-suite rerun rules](../oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V3.md), [exact original-worker and recovery contract](../oracle/phase2/repaired-c-original-campaign-v3.json), and [safe complete-suite controller](../tools/run_owned_repaired_c_original_campaign_v3.py); all 13 original workers completed with 1,262 preserved semantic mismatches and zero infrastructure failures.
- [Recovery-safe original Python tests for the rebuilt C engine](../oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V4.md), [frozen 31,237-check C test and recovery contract](../oracle/phase2/repaired-c-original-campaign-v4.json), and [independently pinned complete-suite controller](../tools/run_owned_repaired_c_original_campaign_v4.py); all **13** real workers completed, revealing **1,230** matching differences with **zero** infrastructure failures and exact original-file restoration.
- [Complete rebuilt C original-suite failure archive](../oracle/phase2/evidence/repaired-c-original-campaign-v4-c-phase2-v15-c-pickle-original-p0-failures.json.gz) and [separate durable C matching and recovery receipt](../oracle/phase2/evidence/repaired-c-original-campaign-v4-c-phase2-v15-c-pickle-original-p0-failures-publication-receipt.json); the receipt independently proves all **13** completed original groups, **1,230** actual differences, **7,325** verified passing checks, the restored original native file, and **zero** worker or execution failures. Receipt success means successful preservation of a failed candidate.
- [Frozen first-party C repair](../oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V1.md), [exact repair and preserved evidence](../oracle/phase2/first-party-source-repair-v1.json), and [private-snapshot-only repair tool](../tools/apply_owned_first_party_source_repair_v1.py); the original checked-in engine, all historical results, and the sealed final comparison remain unchanged.
- [Evidence-backed C match-pickling repair](../oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V2.md), [exact private-source and original-evidence contract](../oracle/phase2/first-party-source-repair-v2.json), and [first-party C source-repair verifier](../tools/apply_owned_first_party_source_repair_v2.py); all 32 observed protocol-0/1 failures and all 64 higher-protocol observations are preserved. The later V15 experiment builds the repaired source twice; its matching remains **NOT MEASURED**.
- [Separate first-party Rust repair](../oracle/phase2/RUST-SOURCE-REPAIR-V1.md), [exact Rust repair and preserved evidence](../oracle/phase2/rust-source-repair-v1.json), and [private Rust-snapshot-only repair tool](../tools/apply_owned_rust_source_repair_v1.py); the existing Rust engine and all its previous failures remain unchanged.
- [Independent Rust public-compatibility repair](../oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V1.md), [exact three-block private-source contract](../oracle/phase2/rust-public-contract-source-repair-v1.json), and [first-party Rust public-source verifier](../tools/apply_owned_rust_public_contract_source_repair_v1.py); the repaired source was independently applied to both private builds. Its later complete compatibility test found **1,087** differences.
- [Source-only correction for the observed Rust flag-display failure](../oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V2.md), [exact private-source and genuine-Python flag contract](../oracle/phase2/rust-public-contract-source-repair-v2.json), and [independently written Rust repair verifier](../tools/apply_owned_rust_public_contract_source_repair_v2.py); all six upstream assertions and **5,128** Python flag values agree. A rebuilt engine and its complete compatibility remain **NOT MEASURED**.
- [Independently reproducible corrected Rust build rules](../oracle/phase2/RUST-FLAG-SOURCE-BUILD-V12.md), [exact first-party toolchain and two-phase build contract](../oracle/phase2/rust-flag-source-build-v12.json), and [offline corrected Rust build verifier](../tools/reproduce_owned_rust_flag_source_build_v12.py); both independent builds and all **28** real compiler and inspection processes succeeded. A separately recorded full matching run finds **1,036** differences.
- [Actual corrected Rust two-build evidence](../oracle/phase2/evidence/native-source-build-v12-rust-phase2-v12-rust-flag-original-p0.json.gz) and [separately durable corrected-build receipt](../oracle/phase2/evidence/native-source-build-v12-rust-phase2-v12-rust-flag-original-p0-publication-receipt.json); the receipt proves **28** real processes, two identical first-party builds, the corrected adapter, no outside matcher, and **zero** candidate tests. Its **PASS** means the build succeeded, not that the replacement passes Python's tests.
- [Reproducible first-party C build rules](../oracle/phase2/NATIVE-SOURCE-BUILD-V8.md), [exact build inventory](../oracle/phase2/native-source-build-v8.json), and [independent two-build verifier](../tools/reproduce_owned_native_source_build_v8.py).
- [Reproducible offline build rules for both C repairs](../oracle/phase2/C-PICKLE-SOURCE-BUILD-V12.md), [exact two-phase source-build contract](../oracle/phase2/c-pickle-source-build-v12.json), and [independent repaired C native-build verifier](../tools/reproduce_owned_c_pickle_source_build_v12.py); its 14 compiler and inspection steps have not yet run.
- [Independently verified C build rules](../oracle/phase2/C-PICKLE-SOURCE-BUILD-V13.md), [exact historical-evidence and two-build contract](../oracle/phase2/c-pickle-source-build-v13.json), and [first-party repaired C build verifier](../tools/reproduce_owned_c_pickle_source_build_v13.py); the frozen two-build, 14-process experiment preserves its original 141-file evidence history but has **NOT YET RUN**.
- [Current independently verified C build rules](../oracle/phase2/C-PICKLE-SOURCE-BUILD-V14.md), [exact 143-file evidence and two-build contract](../oracle/phase2/c-pickle-source-build-v14.json), and [first-party corrected C build verifier](../tools/reproduce_owned_c_pickle_source_build_v14.py); both independent source builds and all 14 compiler steps have **NOT YET RUN**.
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
- [Complete Go result-recording failure](../oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-go-phase2-v1-publication-failure-evidence.json.gz), [independent evidence receipt](../oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-go-phase2-v1-publication-failure-evidence-publication-receipt.json), and [reproducible failure-preservation tool](../tools/preserve_owned_go_campaign_publication_failure_v1.py). This is not a Go compatibility result.
- [Complete corrected C runner failure](../oracle/phase2/evidence/repaired-c-original-campaign-v2-c-phase2-v9-original-p0-failures.json.gz) and [independent durable failure and restoration receipt](../oracle/phase2/evidence/repaired-c-original-campaign-v2-c-phase2-v9-original-p0-failures-publication-receipt.json); the genuine runner error occurred before any matching test started.
- [Complete repaired C compatibility evidence](../oracle/phase2/evidence/repaired-c-original-campaign-v3-c-phase2-v10-live-original-p0-failures.json.gz), [independent safe-restoration receipt](../oracle/phase2/evidence/repaired-c-original-campaign-v3-c-phase2-v10-live-original-p0-failures-publication-receipt.json), [all 13 original worker reports](../oracle/phase2/evidence/frozen-p0-candidate-v9-c-phase2-v10-live-original-p0-failures.json.gz), and [original-suite aggregate receipt](../oracle/phase2/evidence/frozen-p0-candidate-v9-c-phase2-v10-live-original-p0-failures-publication-receipt.json); eight complete groups pass, five retain 1,262 genuine differences, and no infrastructure failure occurred.
- [Actual independent repaired Zig builds](../oracle/phase2/evidence/native-source-build-v11-zig-phase2-v11-zig-scanner.json.gz) and [complete native build and durable publication receipt](../oracle/phase2/evidence/native-source-build-v11-zig-phase2-v11-zig-scanner-publication-receipt.json); exactly 26 genuine processes produce two identical first-party engine and bridge binaries without testing matching or measuring speed.
- [Actual independent repaired Rust builds](../oracle/phase2/evidence/native-source-build-v11-rust-phase2-v11-rust-dual-overlay.json.gz) and [complete offline-build and durable publication receipt](../oracle/phase2/evidence/native-source-build-v11-rust-phase2-v11-rust-dual-overlay-publication-receipt.json); exactly 28 genuine processes produce two identical dependency-free Rust engines and bridges without testing matching or measuring speed.
- [Current headline graph inputs](../docs/evidence/candidate-current-overview-v32.inputs.json), [complete machine-readable Python baseline and independently measured candidate failures](../docs/evidence/candidate-current-overview-v32.json), and [reproducible graph generator](../tools/render_candidate_current_overview_v32.py); the graph authenticates all **153** evidence files and **158** references. It shows the corrected Rust engine's **1,036** genuine differences and **8,965** passing checks, the previous **1,087** Rust differences, **1,230** C differences, and **2,172** Zig differences. The previous C result and unrun additional signature checks remain separately visible.
- [Full experiment log, build reports, previous graphs, failures, and rejected designs](../docs/EXPERIMENT-LOG.md).
- [Proposed 4,194,304-case final comparison](../docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md); examples remain **NOT GENERATED** and **NOT OPENED**.
- [Original objective](../GOAL.md), SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`; [later clarifications](../AMENDMENTS.md).

Run the source-only safety checks without opening the final comparison:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

"$PY" -I -B tools/verify_p0_completeness_v1.py --self-test
"$PY" -I -B tools/verify_python_re_callable_introspection_v1.py \
  --self-test \
  --source-sha256 5a64fb4546bdccd13b6d8d9ba32a7472b01cb86dd0d9f2c643678e6bbf919653 \
  --protocol-sha256 1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8 \
  --contract-sha256 e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349
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
"$PY" -I -B tools/reproduce_owned_rust_flag_source_build_v12.py \
  --self-test \
  --source-sha256 1b3f8333f36a6262e962647719ed99b00dd1519a704bf7f07a5d1f1d56377db6 \
  --protocol-sha256 822857ed434cf1273c0d5eaf14f540d0398c744fee8e14b7b7734238dc2d9950 \
  --contract-sha256 c1c68590a1b45005fb709dc00a6a5f86e6564ed494e179fff9480ea5bed7b592
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

Verify the current headline graph without rerunning a candidate or
opening a benchmark:

```sh
"$PY" -I -B tools/render_candidate_current_overview_v32.py \
  --verify-frozen-context \
  --source-sha256 998c8589cd1fb5a2d309603991e4b377c75cfb3dc85057ea597c6b08e9045df7 \
  --campaign-archive-sha256 2ab266d193728e1297382ed233a813c7ef62c0aa407355cf44fef6aaeffa134f \
  --campaign-receipt-sha256 201b7edc94d54f9ea2054f2eab98a68c83850def841ceade6a14c8db7d05cdd3 \
  --inputs-sha256 1739b0c1b785b93f9f47522a22bc844e9ce5c898bd6580ec01157ce7bdd9a82d \
  --summary-sha256 394ba794ce6bcad9d04da271d45f4465adcada8c4e00e3a75138ae9c257c71d2 \
  --svg-sha256 6366260bf300fab10893d9be20f1b5a2e181acb64db9776ee9e0fce3fcb699aa

"$PY" -I -B tools/verify_python_re_callable_introspection_v1.py \
  --verify-frozen-context \
  --source-sha256 5a64fb4546bdccd13b6d8d9ba32a7472b01cb86dd0d9f2c643678e6bbf919653 \
  --protocol-sha256 1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8 \
  --contract-sha256 e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349

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

"$PY" -I -B tools/reproduce_owned_rust_flag_source_build_v12.py \
  --verify-frozen-context \
  --source-sha256 1b3f8333f36a6262e962647719ed99b00dd1519a704bf7f07a5d1f1d56377db6 \
  --protocol-sha256 822857ed434cf1273c0d5eaf14f540d0398c744fee8e14b7b7734238dc2d9950 \
  --contract-sha256 c1c68590a1b45005fb709dc00a6a5f86e6564ed494e179fff9480ea5bed7b592

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
it is not a verification of the current **153** evidence files and
**158** authenticated references.

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
