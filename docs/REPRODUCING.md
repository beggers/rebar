# Reproducing the frozen rebar experiment

This guide preserves the complete, source-pinned verification commands and
evidence inventory that were previously kept in the main README. All checks
below are source-only or read-only unless a command explicitly says otherwise.
The current results and charts remain in [the project README](../README.md);
experiment history remains in [the experiment log](EXPERIMENT-LOG.md).

## Evidence and reproduction

- [Frozen Python compatibility tests](../oracle/phase1/P0-COMPLETENESS-V1.md), [all 31,237 test cases](../oracle/phase1/p0-completeness-v1.json), and [independent test verifier](../tools/verify_p0_completeness_v1.py).
- [First-party engine ownership and no-wrapping audit](../oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md), [exact source inventory](../oracle/phase2/candidate-independence-v2.json), and [source verifier](../tools/audit_candidate_independence_v2.py).
- [Independent Zig scanner-capture repair](../oracle/phase2/ZIG-SCANNER-CAPTURE-SOURCE-REPAIR-V1.md), [single-block private-snapshot contract](../oracle/phase2/zig-scanner-capture-source-repair-v1.json), and [source-pinned first-party repair tool](../tools/apply_owned_zig_scanner_capture_source_repair_v1.py); the candidate has not been rebuilt or retested.
- [Corrected original Python test producer](../tools/run_owned_six_family_original_p0_producer_v3.py), [unchanged original-test and first-party ownership protocol](../oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md), and [exact source-pinned contract](../oracle/phase2/six-family-p0-producer-v3.json); both real Python reference processes and all 31,237 cases are preserved.
- [Corrected complete original-suite protocol](../oracle/phase2/P0-CANDIDATE-PROTOCOL-V9.md), [exact case and worker inventory](../oracle/phase2/p0-candidate-protocol-v9.json), [corrected isolated-suite worker](../tools/run_frozen_p0_candidate_worker_v7.py), and [complete 13-suite runner](../tools/run_frozen_p0_candidate_v9.py); source frozen only, with no repaired candidate result.
- [Frozen first-party C repair](../oracle/phase2/FIRST-PARTY-SOURCE-REPAIR-V1.md), [exact repair and preserved evidence](../oracle/phase2/first-party-source-repair-v1.json), and [private-snapshot-only repair tool](../tools/apply_owned_first_party_source_repair_v1.py); no original engine, matching result, or final comparison has been changed.
- [Separate first-party Rust repair](../oracle/phase2/RUST-SOURCE-REPAIR-V1.md), [exact Rust repair and preserved evidence](../oracle/phase2/rust-source-repair-v1.json), and [private Rust-snapshot-only repair tool](../tools/apply_owned_rust_source_repair_v1.py); the existing Rust engine and all its previous failures remain unchanged.
- [Reproducible first-party C build rules](../oracle/phase2/NATIVE-SOURCE-BUILD-V8.md), [exact build inventory](../oracle/phase2/native-source-build-v8.json), and [independent two-build verifier](../tools/reproduce_owned_native_source_build_v8.py).
- [Actual matching first-party C builds](../oracle/phase2/evidence/native-source-build-v8-c-phase2-v8.json.gz) and [independent build receipt](../oracle/phase2/evidence/native-source-build-v8-c-phase2-v8-publication-receipt.json); two private builds produced identical native binaries.
- [Reproducible independent Rust build rules](../oracle/phase2/NATIVE-SOURCE-BUILD-V9.md), [exact Rust build inventory](../oracle/phase2/native-source-build-v9.json), and [offline two-build verifier](../tools/reproduce_owned_native_source_build_v9.py); the repaired Rust engine has no external regex dependency and has not yet been built or retested.
- [Safe reversible C-engine loading rules](../oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V5.md), [exact recovery and build checks](../oracle/phase2/verified-native-activation-v5.json), and [first-party engine recovery tool](../tools/activate_verified_native_candidate_v5.py); the original native file was restored exactly.
- [Complete repaired-engine Python test rules](../oracle/phase2/P0-CANDIDATE-PROTOCOL-V8.md), [all original groups and seeds](../oracle/phase2/p0-candidate-protocol-v8.json), [isolated original-test worker](../tools/run_frozen_p0_candidate_worker_v6.py), and [complete test and recovery recorder](../tools/run_frozen_p0_candidate_v8.py); all **31,237** original cases remain unchanged.
- [Fail-safe full C test rules](../oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V1.md), [exact recovery and test contract](../oracle/phase2/repaired-c-original-campaign-v1.json), and [recovered original-test runner](../tools/run_owned_repaired_c_original_campaign_v1.py); the original native file was restored before the genuine failure was recorded.
- [All 13 repaired C test-runner failures](../oracle/phase2/evidence/frozen-p0-candidate-v8-c-phase2-v8-original-p0-failures.json.gz) and [complete original-test receipt](../oracle/phase2/evidence/frozen-p0-candidate-v8-c-phase2-v8-original-p0-failures-publication-receipt.json); **12** groups rejected genuine Python-compatible public type names and **1** could not decode its archived reference.
- [Independently recovered C failure and original-file proof](../oracle/phase2/evidence/repaired-c-original-campaign-v1-c-phase2-v8-original-p0-failures.json.gz) and [separate durable recovery receipt](../oracle/phase2/evidence/repaired-c-original-campaign-v1-c-phase2-v8-original-p0-failures-publication-receipt.json); matching was **NOT MEASURED**.
- [Complete original-test rules](../oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V1.md), [frozen test inventory](../oracle/phase2/six-family-p0-campaign-v1.json), and [reproducible candidate test runner](../tools/run_owned_six_family_original_p0_campaign_v1.py).
- [Lossless original-test recording rules](../oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V2.md), [frozen streaming-test inventory](../oracle/phase2/six-family-p0-campaign-v2.json), and [complete streaming test recorder](../tools/run_owned_six_family_original_p0_campaign_v2.py); the original tests, first-party engines, and preserved Go failure remain unchanged.
- [Complete first-party C++ failure](../oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-cpp-phase2-v1-failures.json.gz) and [independent publication and recovery receipt](../oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-cpp-phase2-v1-failures-publication-receipt.json).
- [Complete first-party Go matching failure](../oracle/phase2/evidence/owned-six-family-original-p0-campaign-v2-go-phase2-v2-failures.json.gz) and [independent streamed-result and native-recovery receipt](../oracle/phase2/evidence/owned-six-family-original-p0-campaign-v2-go-phase2-v2-failures-publication-receipt.json); all **13** groups, **4,518** genuine differences, **4** separate worker failures, and both restored native files are preserved.
- [Complete Go result-recording failure](../oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-go-phase2-v1-publication-failure-evidence.json.gz), [independent evidence receipt](../oracle/phase2/evidence/owned-six-family-original-p0-campaign-v1-go-phase2-v1-publication-failure-evidence-publication-receipt.json), and [reproducible failure-preservation tool](../tools/preserve_owned_go_campaign_publication_failure_v1.py). This is not a Go compatibility result.
- [Current headline graph inputs](../docs/evidence/candidate-current-overview-v21.inputs.json), [complete machine-readable Python baseline and candidate failures](../docs/evidence/candidate-current-overview-v21.json), and [reproducible graph generator](../tools/render_candidate_current_overview_v21.py).
- [Full experiment log, build reports, previous graphs, failures, and rejected designs](../docs/EXPERIMENT-LOG.md).
- [Proposed 4,194,304-case final comparison](../docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md); examples remain **NOT GENERATED** and **NOT OPENED**.
- [Original objective](../GOAL.md), SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`; [later clarifications](../AMENDMENTS.md).

Run the source-only safety checks without opening the final comparison:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

"$PY" -I -B tools/verify_p0_completeness_v1.py --self-test
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
"$PY" -I -B tools/run_owned_six_family_original_p0_campaign_v1.py --self-test
"$PY" -I -B tools/run_owned_six_family_original_p0_campaign_v2.py --self-test
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
```

Verify the current headline graph without rerunning a candidate or
opening a benchmark:

```sh
"$PY" -I -B tools/render_candidate_current_overview_v21.py --verify \
  --source-sha256 617a64691bf9da7730e44bfed96fe20dbd9c8e38b575e0daf8a3432dbf2625e9 \
  --campaign-archive-sha256 a8319a686c2486e27374bfb9c6ada4e4ec104c27c1cafdbc2205c98f40fa9fb7 \
  --campaign-receipt-sha256 034207331f8d61ef69f510cb42b9babe921b85570c571198ea8eb310c75ffecd \
  --manifest-sha256 704b2e07e32260ac741b0a914e2ae04a3deb583de317ba170432f85126af5139

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

The [complete compatibility standard](../oracle/phase1/P0-COMPLETENESS-V1.md)
contains the source-pinned, read-only full-verification command.
