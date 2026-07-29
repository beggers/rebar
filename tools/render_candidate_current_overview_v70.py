#!/usr/bin/env python3
"""Show the real Rust campaign freeze without pretending the engine can run."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v70.py"
OUTPUT = "docs/evidence/candidate-current-overview-v70"
SCHEMA = "rebar-candidate-current-overview-v70"
BLOCKED = "BLOCKED PENDING INDEPENDENTLY ATTESTED PRIVATE ROOT"

V69 = {
    "source": (
        "tools/render_candidate_current_overview_v69.py",
        "d5a074cba906402dc4f66e5127c88218e122a87743d713a3ce0f431c2994a7a2",
        261888, 430875,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v69.inputs.json",
        "75631c80b75bea22c713ea4c4f486e96deb85280161ff64000e5b78e4d5056c1",
        1085629, 430877,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v69.json",
        "c112d1629e134ffc42f262ca70b4212397d17b7e52914f4a36a14f72e9eec923",
        3032584, 430879,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v69.svg",
        "2cc3316348aec8d0f8f223ea3cb771779854d7eea86a1cd3d2c157f8de30869b",
        14597, 430880,
    ),
}
FEATURE = {
    "source": (
        "tools/run_owned_repaired_rust_original_campaign_v11.py",
        "27bf88358d5a45a5b487680e70f5fa5b5192a05f053f33f6ddb651c972c94f2d",
        310760, 430525,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V11.md",
        "a3a5b35701aa6b149ff0b4fbebb9f6722dd08436d2f7e4f600f3db12c8c6ac2b",
        7353, 524748,
    ),
    "contract": (
        "oracle/phase2/repaired-rust-original-campaign-v11.json",
        "e6cd2028e36d8ddac0937e6735132bf474327f2ff04855d44e6aa71f5f5c0f96",
        16783, 524749,
    ),
}

CONTRACT_JSON = (
    "{\"actual_first_party_c_v16_build\":{\"actual_compiler_process_count\":14,\"build_pass_means_"
    "candidate_correctness\":false,\"candidate_build_status\":\"PASS\",\"candidate_correctness\":\"NO"
    "T MEASURED\",\"candidate_workers_started\":0,\"compressed_archive_metadata_attested_only\":{\""
    "archive_opened\":false,\"bytes\":37795,\"device\":2064,\"inode\":524750,\"path\":\"oracle/phase2/e"
    "vidence/native-source-build-v16-c-phase2-v16-c-subject-buffer-original-p0.json.gz\",\"sha2"
    "56\":\"45cf839dd4fcb7615d70af79bc38b4695911159b109c9a79fd1d7d037b338f55\"},\"durable_success"
    "_receipt\":{\"device\":2064,\"inode\":524751,\"path\":\"oracle/phase2/evidence/native-source-bui"
    "ld-v16-c-phase2-v16-c-subject-buffer-original-p0-publication-receipt.json\",\"sha256\":\"167"
    "94f5b1487b76a909a176948f4bbac8ed3108768f3127e27c44f9f392ae3d6\",\"size_bytes\":2671},\"previ"
    "ous_candidate_matching_status\":\"FAIL\",\"previous_explicitly_verified_passing_case_count\":"
    "7325,\"previous_semantic_mismatch_count\":1230,\"source_freeze_loads_native\":false,\"source_"
    "freeze_opens_archive\":false},\"actual_first_party_v18_build\":{\"actual_compiler_process_co"
    "unt\":28,\"adapter_overlay_apply_count\":2,\"bridge_overlay_apply_count\":2,\"build_pass_means"
    "_candidate_correctness\":false,\"candidate_build_status\":\"PASS\",\"combined_bridge_bytes\":17"
    "9961,\"combined_bridge_sha256\":\"afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550"
    "634f740\",\"compressed_archive_metadata_attested_only\":{\"archive_opened\":false,\"bytes\":109"
    "345,\"device\":2064,\"inode\":524733,\"path\":\"oracle/phase2/evidence/native-source-build-v18-"
    "rust-phase2-v18-rust-buffer-shape-pickle-lifetime.json.gz\",\"sha256\":\"f59818e4aaea2999a5f"
    "ec608d4d8ed761d372e1725548e3c3ff57773d01dffdc\"},\"contract\":{\"device\":2064,\"inode\":524728"
    ",\"path\":\"oracle/phase2/rust-buffer-shape-source-build-v18.json\",\"sha256\":\"e57d67e1b16bb1"
    "3a3555c05c0b6b546b83ab3a6a7e63beec5c81896e01f92301\",\"size_bytes\":23099},\"corrected_adapt"
    "er_bytes\":31934,\"corrected_adapter_sha256\":\"d47a976771206da468168ec22683e6d0204905a0f5b7"
    "e9e328fc1234b38f210e\",\"durable_success_receipt\":{\"device\":2064,\"inode\":524747,\"path\":\"or"
    "acle/phase2/evidence/native-source-build-v18-rust-phase2-v18-rust-buffer-shape-pickle-li"
    "fetime-publication-receipt.json\",\"sha256\":\"32c422b9624a2565afd8d710700e377aa39aae4aa93d3"
    "742da483843869f2104\",\"size_bytes\":3486},\"expected_compiler_process_count\":28,\"independen"
    "t_phase_count\":2,\"independent_private_root_provenance\":\"NOT ESTABLISHED\",\"individual_nat"
    "ive_elf_hashes\":\"NOT MEASURED\",\"private_build_root\":\"NOT MEASURED\",\"private_root_disclos"
    "ed_by_public_receipt\":false,\"private_root_recoverable_from_sanitized_build_report\":false"
    ",\"process_roles_per_phase\":[\"readelf_version\",\"gcc_version\",\"rustc_version\",\"cargo_versi"
    "on\",\"build_rust_engine\",\"build_rust_bridge\",\"engine_dynamic\",\"engine_symbols\",\"bridge_dy"
    "namic\",\"bridge_symbols\",\"engine_sections\",\"engine_notes\",\"bridge_sections\",\"bridge_notes"
    "\"],\"protocol\":{\"device\":2064,\"inode\":524727,\"path\":\"oracle/phase2/RUST-BUFFER-SHAPE-SOUR"
    "CE-BUILD-V18.md\",\"sha256\":\"52513bb429416e182774558eebf2ae4e1d217e8656da673b9f765d4f3df75"
    "991\",\"size_bytes\":6523},\"source\":{\"device\":2064,\"inode\":428939,\"path\":\"tools/reproduce_o"
    "wned_rust_buffer_shape_source_build_v18.py\",\"sha256\":\"5a464fbd62ac375d236fa2debce14ae150"
    "7ce1bf494efb35695210199bdbef8c\",\"size_bytes\":128761},\"source_freeze_loads_native\":false,"
    "\"source_freeze_opens_archive\":false,\"uncompressed_bytes_attested_by_receipt\":762807,\"unc"
    "ompressed_sha256_attested_by_receipt\":\"644ac03e43d8ff495e5466264ca94e9356863b3201cf0a47c"
    "27211d1e83320bf\"},\"corrected_python_reference\":{\"cache_records_sha256\":\"587cf35555472940"
    "522d6ae3a73053fb7e98492befe581cc024444bed8e264ad\",\"full_reference_records_sha256\":\"6b26a"
    "c4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2\",\"public_type_cases_per_refe"
    "rence\":6912,\"reference_archive_opened_by_source_gate\":false,\"reference_process_ids\":[81,"
    "82],\"small_plaintext_receipt\":{\"path\":\"oracle/phase1/evidence/public-type-reference-cont"
    "ext-v1-cpython-3-14-6-candidate-context-p0-publication-receipt.json\",\"sha256\":\"ff8ddfaa1"
    "4ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966\",\"size_bytes\":2509},\"subclass_ca"
    "che_cases_per_reference\":96},\"current_pushed_graph\":{\"authenticated_evidence_owner_lower"
    "_bound\":230,\"authenticated_history_reference_lower_bound\":235,\"global_owner_census\":\"NOT"
    " MEASURED\",\"graph_is_current_pushed_predecessor\":true,\"new_source_owner_count\":3,\"owners"
    "\":[{\"device\":2064,\"inode\":430875,\"path\":\"tools/render_candidate_current_overview_v69.py\""
    ",\"sha256\":\"d5a074cba906402dc4f66e5127c88218e122a87743d713a3ce0f431c2994a7a2\",\"size_bytes"
    "\":261888},{\"device\":2064,\"inode\":430877,\"path\":\"docs/evidence/candidate-current-overview"
    "-v69.inputs.json\",\"sha256\":\"75631c80b75bea22c713ea4c4f486e96deb85280161ff64000e5b78e4d50"
    "56c1\",\"size_bytes\":1085629},{\"device\":2064,\"inode\":430879,\"path\":\"docs/evidence/candidat"
    "e-current-overview-v69.json\",\"sha256\":\"c112d1629e134ffc42f262ca70b4212397d17b7e52914f4a3"
    "6a14f72e9eec923\",\"size_bytes\":3032584},{\"device\":2064,\"inode\":430880,\"path\":\"docs/eviden"
    "ce/candidate-current-overview-v69.svg\",\"sha256\":\"2cc3316348aec8d0f8f223ea3cb771779854d7e"
    "ea86a1cd3d2c157f8de30869b\",\"size_bytes\":14597}],\"resulting_evidence_owner_lower_bound\":2"
    "33,\"resulting_history_reference_lower_bound\":238,\"version\":69},\"family\":\"rust\",\"first_pa"
    "rty_rust_ownership\":{\"candidate_worker_implemented_in_controller_source\":true,\"cpython_s"
    "re_matching_delegation\":\"FORBIDDEN\",\"cross_candidate_matching_delegation\":\"FORBIDDEN\",\"e"
    "xternal_regex_dependencies\":0,\"first_party_rust_source_owner_count\":9,\"historical_same_f"
    "ile_worker_source\":{\"device\":2064,\"inode\":432095,\"path\":\"tools/run_owned_repaired_rust_o"
    "riginal_campaign_v10.py\",\"sha256\":\"038870e88e9dfbe2f9d97892fb98558787d1142bb94559e306002"
    "3c8e562a81c\",\"size_bytes\":211733},\"matching_fallback\":\"FORBIDDEN\",\"preserved_pickle_feat"
    "ure\":[{\"path\":\"tools/apply_owned_rust_match_pickle_source_repair_v1.py\",\"sha256\":\"85383f"
    "4cdf93eef0130390e1114cbd1703edce154ca274d2427c6943e46b3517\",\"size_bytes\":81784},{\"path\":"
    "\"oracle/phase2/RUST-MATCH-PICKLE-SOURCE-REPAIR-V1.md\",\"sha256\":\"fad29fdcd3956ae99f9db40a"
    "fae33b51eb99fb743baf89540a4ee7aafb7ac1af\",\"size_bytes\":5105},{\"path\":\"oracle/phase2/rust"
    "-match-pickle-source-repair-v1.json\",\"sha256\":\"5456535223cb029d41e8739696bde30b2b7127995"
    "fd0ef30286ff0488b1ed133\",\"size_bytes\":15276}],\"separate_worker_source_required\":false,\"s"
    "tdlib_matching_delegation\":\"FORBIDDEN\",\"v2_buffer_feature\":[{\"path\":\"tools/apply_owned_r"
    "ust_buffer_shape_pickle_source_repair_v2.py\",\"sha256\":\"7f22016b20da990b0ddb85114bf76a187"
    "918612ef68aae97c94d81518d3eb322\",\"size_bytes\":47145},{\"path\":\"oracle/phase2/RUST-BUFFER-"
    "SHAPE-PICKLE-SOURCE-REPAIR-V2.md\",\"sha256\":\"79ad2b88f7542c791cdf48956d432e6d9f2dad00a485"
    "056972eea1664e41ff66\",\"size_bytes\":4060},{\"path\":\"oracle/phase2/rust-buffer-shape-pickle"
    "-source-repair-v2.json\",\"sha256\":\"0d5fe2ca190df54366b73850ce316a9d27f77c527bd5ddd8d5420d"
    "62dcb33be0\",\"size_bytes\":7486}]},\"future_authorized_build_inspection\":{\"actual_compresse"
    "d_archive_reads\":0,\"archive\":{\"bytes\":109345,\"device\":2064,\"inode\":524733,\"path\":\"oracle"
    "/phase2/evidence/native-source-build-v18-rust-phase2-v18-rust-buffer-shape-pickle-lifeti"
    "me.json.gz\",\"sha256\":\"f59818e4aaea2999a5fec608d4d8ed761d372e1725548e3c3ff57773d01dffdc\"}"
    ",\"build_receipt\":{\"device\":2064,\"inode\":524747,\"path\":\"oracle/phase2/evidence/native-sou"
    "rce-build-v18-rust-phase2-v18-rust-buffer-shape-pickle-lifetime-publication-receipt.json"
    "\",\"sha256\":\"32c422b9624a2565afd8d710700e377aa39aae4aa93d3742da483843869f2104\",\"size_byte"
    "s\":3486},\"caller_pins_private_root_device_inode\":true,\"candidate_matching\":\"NOT RUN\",\"ca"
    "ndidate_workers_started\":0,\"derive_elf_hash_from_c_source\":\"FORBIDDEN\",\"derive_root_from"
    "_sanitized_archive\":\"FORBIDDEN\",\"existing_v18_inspection_status\":\"BLOCKED PENDING INDEPE"
    "NDENTLY ATTESTED PRIVATE ROOT\",\"existing_v18_root_disclosed_by_public_evidence\":false,\"f"
    "resh_provenance_build_required_without_independent_root\":true,\"future_maximum_archive_re"
    "ads\":1,\"future_maximum_gzip_inflations\":1,\"guess_private_root\":\"FORBIDDEN\",\"mode\":\"--ins"
    "pect-build\",\"private_root_provenance\":\"NOT ESTABLISHED\",\"private_root_source\":\"INDEPENDE"
    "NT EXPLICIT CALLER AUTHORITY\",\"receipt_path\":\"oracle/phase2/evidence/repaired-rust-origi"
    "nal-campaign-v11-rust-phase2-v18-rust-buffer-shape-pickle-original-p0-v11-build-inspecti"
    "on-publication-receipt.json\",\"report_path\":\"oracle/phase2/evidence/repaired-rust-origina"
    "l-campaign-v11-rust-phase2-v18-rust-buffer-shape-pickle-original-p0-v11-build-inspection"
    ".json\",\"required_complete_native_role_count\":2,\"required_distinct_native_phase_inode_cou"
    "nt\":4,\"required_distinct_private_source_inode_count\":18,\"required_distinct_successful_pr"
    "ocess_count\":28,\"requires_separate_explicit_authorization\":true,\"scan_tmp\":\"FORBIDDEN\"},"
    "\"future_authorized_original_campaign\":{\"activate_only_first_party_rust\":true,\"case_execu"
    "tion_denominator\":31237,\"derive_verified_passes_by_subtraction\":false,\"individual_worker"
    "_mode\":\"--worker\",\"mode\":\"--run\",\"named_private_waiver_count\":13,\"reopen_build_archive\":"
    "\"FORBIDDEN\",\"requires_published_build_inspection\":true,\"requires_separate_explicit_autho"
    "rization\":true,\"runtime_non_delegation\":\"NOT ESTABLISHED\",\"self_hosted_worker_count\":13,"
    "\"semantic_mismatch_treatment\":\"PRESERVE ALL COMPLETE VECTORS\",\"suite_count\":13,\"suppleme"
    "ntal_8244_candidate_cases\":\"NOT RUN\",\"touch_other_candidate_families\":false,\"unique_actu"
    "al_worker_process_ids_required\":13},\"genuine_previous_v10_original_campaign\":{\"actual_ca"
    "ndidate_workers\":13,\"actual_completed_suite_count\":13,\"candidate_qualified\":false,\"candi"
    "date_status\":\"FAIL\",\"case_execution_denominator\":31237,\"complete_failure_forensics\":{\"de"
    "vice\":2064,\"inode\":525045,\"path\":\"oracle/phase2/evidence/repaired-rust-original-campaign"
    "-v10-rust-phase2-v16-rust-buffer-shape-pickle-original-p0-v10-failures-forensic-summary."
    "json\",\"sha256\":\"6e04771a48b4a460ad58ac9795ef91a697a33fa0aeae4671c9b3c9b35e4820cd\",\"size_"
    "bytes\":24701},\"contract\":{\"device\":2064,\"inode\":525034,\"path\":\"oracle/phase2/repaired-ru"
    "st-original-campaign-v10.json\",\"sha256\":\"57c36f414d052e798fc1f9ccfcd10aeddd5f6571d95679a"
    "995c6935d86f3dda7\",\"size_bytes\":17426},\"durable_failure_receipt\":{\"device\":2064,\"inode\":"
    "525044,\"path\":\"oracle/phase2/evidence/repaired-rust-original-campaign-v10-rust-phase2-v1"
    "6-rust-buffer-shape-pickle-original-p0-v10-failures-publication-receipt.json\",\"sha256\":\""
    "8735e5351f62de2a77369eb8401e225cebd31434b09f07db40e79550ba7cc7d2\",\"size_bytes\":6708},\"ex"
    "plicitly_verified_passing_case_count\":14853,\"protocol\":{\"device\":2064,\"inode\":525033,\"pa"
    "th\":\"oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V10.md\",\"sha256\":\"cf425c2517f7fa066a3"
    "0a340b830d8782e0000872efa3eaf00c764ce45ef0659\",\"size_bytes\":16618},\"semantic_mismatch_co"
    "unt\":1440,\"source\":{\"device\":2064,\"inode\":432095,\"path\":\"tools/run_owned_repaired_rust_o"
    "riginal_campaign_v10.py\",\"sha256\":\"038870e88e9dfbe2f9d97892fb98558787d1142bb94559e306002"
    "3c8e562a81c\",\"size_bytes\":211733},\"verified_passing_cases_derived_by_subtraction\":false}"
    ",\"label\":\"phase2-v18-rust-buffer-shape-pickle-original-p0-v11\",\"original_oracle\":{\"addit"
    "ional_waivers\":0,\"case_execution_denominator\":31237,\"named_private_waiver_count\":13,\"pro"
    "ducer\":[{\"path\":\"tools/run_owned_six_family_original_p0_producer_v4.py\",\"sha256\":\"e0bab3"
    "833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8\",\"size_bytes\":230782},{\"path\""
    ":\"oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md\",\"sha256\":\"e82b3469853406bf36812f016688aa3e"
    "6403b8d98d025a29fb9d0a9704ea2aa5\",\"size_bytes\":5981},{\"path\":\"oracle/phase2/six-family-p"
    "0-producer-v4.json\",\"sha256\":\"c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e76"
    "1fa1d5\",\"size_bytes\":30867}],\"producer_version\":4,\"source_ordered_suites\":[{\"case_execut"
    "ion_count\":151,\"id\":\"original_bounded_v5\"},{\"case_execution_count\":864,\"id\":\"public_v3\"}"
    ",{\"case_execution_count\":1024,\"id\":\"scanner_v3\"},{\"case_execution_count\":768,\"id\":\"buffe"
    "r_v3\"},{\"case_execution_count\":1024,\"id\":\"managed_v1\"},{\"case_execution_count\":2854,\"id\""
    ":\"scanner_verbose_v1\"},{\"case_execution_count\":6912,\"id\":\"public_types_v1\"},{\"case_execu"
    "tion_count\":5120,\"id\":\"substitution_v2\"},{\"case_execution_count\":10240,\"id\":\"shape_v2\"},"
    "{\"case_execution_count\":1376,\"id\":\"public_surface_v19\"},{\"case_execution_count\":128,\"id\""
    ":\"subinterpreter_v2\"},{\"case_execution_count\":264,\"id\":\"pep688_v4\"},{\"case_execution_cou"
    "nt\":512,\"id\":\"threaded_pattern_v1\"}],\"suite_count\":13,\"supplementary_cases_added_to_orig"
    "inal_denominator\":0},\"phase\":\"CANDIDATES\",\"phase1_v4_readiness\":{\"native_runtime_no_dele"
    "gation\":\"NOT ESTABLISHED\",\"owners\":[{\"device\":2064,\"inode\":428927,\"path\":\"tools/verify_o"
    "wned_p0_completeness_v4.py\",\"sha256\":\"8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160"
    "d841ce2ff7760d\",\"size_bytes\":29094},{\"device\":2064,\"inode\":524712,\"path\":\"oracle/phase1/"
    "P0-COMPLETENESS-V4.md\",\"sha256\":\"4a390db825fed994733390be8961a0f709d7f1f22195535e581e71c"
    "dea8111f2\",\"size_bytes\":4261},{\"device\":2064,\"inode\":524713,\"path\":\"oracle/phase1/p0-com"
    "pleteness-v4.json\",\"sha256\":\"aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc8"
    "5b3b1\",\"size_bytes\":34875}],\"qualified_candidate_count\":0,\"status\":\"PASS\",\"status_scope\""
    ":\"PHASE 1 PYTHON-ORACLE READINESS ONLY\",\"supplemental_candidate_status\":\"NOT RUN\",\"suppl"
    "emental_reference_case_count\":8244,\"supplemental_reference_workers\":2,\"version\":4},\"pinn"
    "ed_cpython\":{\"bytecode_writes\":false,\"isolated\":true,\"path\":\"/tmp/rebar-cpython/cpython-"
    "3.14.6-linux-x86_64-gnu/bin/python3.14\",\"sha256\":\"255e900f44ce87c630e83b637a79435f9ae777"
    "8dd72f6e2a2f18a486e501d016\",\"version\":\"3.14.6\"},\"protocol\":{\"path\":\"oracle/phase2/REPAIR"
    "ED-RUST-ORIGINAL-CAMPAIGN-V11.md\",\"sha256\":\"a3a5b35701aa6b149ff0b4fbebb9f6722dd08436d2f7"
    "e4f600f3db12c8c6ac2b\"},\"public_exact_inode_recovery\":{\"activation_root\":\"/tmp/rebar-phas"
    "e2-repaired-rust-original-campaign-v11-phase2-v18-rust-buffer-shape-pickle-original-p0\","
    "\"all_four_original_targets_restored\":\"NOT RUN\",\"exclusive_lock_required\":true,\"group_ato"
    "mic\":false,\"journal_required_before_activation\":true,\"mode\":\"--recover\",\"original_owners"
    "\":{\"adapter\":{\"bytes\":31151,\"device\":2064,\"inode\":428100,\"mode\":384,\"nlink\":1,\"relative\""
    ":\"candidates/rust_candidate.py\",\"sha256\":\"6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0e"
    "f3d5de7ec553a0351b\",\"uid\":1000},\"bridge\":{\"bytes\":144992,\"device\":2064,\"inode\":430629,\"m"
    "ode\":493,\"nlink\":1,\"relative\":\"candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so\","
    "\"sha256\":\"6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15\",\"uid\":1000},"
    "\"bridge_source\":{\"bytes\":175676,\"device\":2064,\"inode\":419054,\"mode\":384,\"nlink\":1,\"relat"
    "ive\":\"candidates/rust/py_bridge.c\",\"sha256\":\"f8a0918aaf8a78f363f6d755770636d26acd45fb83c"
    "9abcf997a6e052748ea8b\",\"uid\":1000},\"engine\":{\"bytes\":660440,\"device\":2064,\"inode\":430563"
    ",\"mode\":493,\"nlink\":1,\"relative\":\"candidates/_rust_engine.so\",\"sha256\":\"f8cd2e8ecac5ab6a"
    "12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4\",\"uid\":1000}},\"power_failure_automatica"
    "lly_recovered\":false,\"private_prefix\":\"rebar-phase2-repaired-rust-original-campaign-v11-"
    "\",\"restoration_order\":[\"bridge\",\"engine\",\"adapter\",\"bridge_source\"],\"restoration_verifie"
    "d_before_publication\":true,\"role_order\":[\"bridge_source\",\"adapter\",\"engine\",\"bridge\"],\"s"
    "igkill_automatically_recovered\":false},\"publication\":{\"expected_future_campaign_evidence"
    "_owner_count\":2,\"expected_new_source_owner_count\":3,\"fresh_label\":\"phase2-v18-rust-buffe"
    "r-shape-pickle-original-p0-v11\",\"preserve_success_and_failure\":true,\"publication_before_"
    "restoration\":\"FORBIDDEN\",\"source_status_is_candidate_correctness\":false},\"schema\":\"rebar"
    "-owned-repaired-rust-original-campaign-v11-recoverable-source-freeze\",\"source\":{\"path\":\""
    "tools/run_owned_repaired_rust_original_campaign_v11.py\",\"sha256\":\"27bf88358d5a45a5b48768"
    "0e70f5fa5b5192a05f053f33f6ddb651c972c94f2d\"},\"source_only_effects\":{\"actual_candidate_im"
    "ports\":0,\"actual_candidate_workers\":0,\"actual_compiler_processes\":0,\"actual_native_activ"
    "ations\":0,\"actual_native_library_loads\":0,\"actual_reference_workers\":0,\"actual_source_bu"
    "ilds\":0,\"benchmark_files_read\":0,\"build_private_root\":\"NOT MEASURED\",\"candidate_correctn"
    "ess\":\"NOT MEASURED\",\"candidate_matching\":\"NOT RUN\",\"candidate_qualified\":false,\"canonica"
    "l_target_reads\":0,\"canonical_target_replacements\":0,\"canonical_target_stats\":0,\"clock_sa"
    "mples\":0,\"confidence_intervals\":\"NOT MEASURED\",\"hidden_cases_read\":0,\"historical_build_a"
    "rchive_reads\":0,\"historical_matching_archive_reads\":0,\"holdout\":\"NOT OPENED\",\"memory\":\"N"
    "OT MEASURED\",\"native_artifact_hashes\":\"NOT MEASURED\",\"network_requests\":0,\"performance\":"
    "\"NOT MEASURED\",\"private_build_root_enumerations\":0,\"private_build_root_reads\":0,\"recover"
    "y_journals_created\":0,\"recovery_locks_acquired\":0,\"recovery_roots_created\":0,\"reference_"
    "archive_reads\":0,\"runtime_non_delegation\":\"NOT ESTABLISHED\",\"threads_started\":0,\"timing_"
    "trials_run\":0,\"undefined_behavior\":\"NOT MEASURED\",\"v18_build_archive_gzip_inflations\":0,"
    "\"v18_build_archive_reads\":0,\"winner_selected\":false,\"workspace_mutations\":0},\"status\":\"S"
    "OURCE FROZEN; ACTUAL V18 RUST CANDIDATE NOT RUN\",\"version\":11}"
)


def _read_exact(item: tuple, label: str) -> bytes:
    relative, fingerprint, size, inode = item
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / relative), flags)
    try:
        before = os.fstat(handle)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.geteuid()
            or before.st_dev != 2064
            or before.st_ino != inode
            or before.st_nlink != 1
            or stat.S_IMODE(before.st_mode) != 0o600
            or before.st_size != size
        ):
            raise ValueError("reject substituted private " + label)
        remaining = size
        chunks = []
        while remaining:
            chunk = os.read(handle, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated private " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(handle, 1):
            raise ValueError("reject extended private " + label)
        raw = b"".join(chunks)
        after = os.fstat(handle)
        if (
            hashlib.sha256(raw).hexdigest() != fingerprint
            or (
                before.st_dev, before.st_ino, before.st_size,
                before.st_nlink, before.st_mtime_ns, before.st_ctime_ns,
            ) != (
                after.st_dev, after.st_ino, after.st_size,
                after.st_nlink, after.st_mtime_ns, after.st_ctime_ns,
            )
        ):
            raise ValueError("reject changed private " + label)
        return raw
    finally:
        os.close(handle)


def load_v69() -> tuple:
    raw = _read_exact(V69["source"], "genuinely pushed V69 graph source")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v69")
    previous.__file__ = str(ROOT / V69["source"][0])
    previous.__package__ = ""
    exec(
        compile(raw, previous.__file__, "exec", dont_inherit=True),
        previous.__dict__,
    )
    modules = previous.load_v68()
    base = modules[-1]
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v69"
        and previous.SELF == V69["source"][0],
        "authenticate only the exact actually pushed V69 graph",
    )
    return previous, modules, base


def previous_options(
    previous: types.ModuleType, modules: tuple,
) -> argparse.Namespace:
    inherited = previous.previous_options(modules[0], modules[1])
    values = {
        "source_sha256": V69["source"][1],
        "source_bytes": V69["source"][2],
        "inputs_sha256": None,
        "summary_sha256": None,
        "svg_sha256": None,
    }
    for role, item in previous.V68.items():
        values["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.FEATURE.items():
        values["feature_" + role + "_sha256"] = item[1]
    for role in ("source", "protocol", "contract"):
        values["readiness_" + role + "_sha256"] = getattr(
            inherited, "readiness_" + role + "_sha256",
        )
    return argparse.Namespace(**values)


def synthetic_contract() -> dict:
    value = json.loads(CONTRACT_JSON)
    if type(value) is not dict:
        raise ValueError("reject omitted complete frozen Rust V11 contract")
    return value


def validate_contract(base: types.ModuleType, contract: object) -> None:
    expected = synthetic_contract()
    base.need(
        type(contract) is dict
        and set(contract) == set(expected)
        and contract == expected,
        "reject any changed, missing, or invented full Rust V11 contract field",
    )
    assert isinstance(contract, dict)
    effects = contract["source_only_effects"]
    graph = contract["current_pushed_graph"]
    inspect = contract["future_authorized_build_inspection"]
    campaign = contract["future_authorized_original_campaign"]
    rust = contract["actual_first_party_v18_build"]
    c = contract["actual_first_party_c_v16_build"]
    history = contract["genuine_previous_v10_original_campaign"]
    base.need(
        contract["schema"]
        == "rebar-owned-repaired-rust-original-campaign-v11-recoverable-source-freeze"
        and contract["version"] == 11
        and contract["phase"] == "CANDIDATES"
        and contract["family"] == "rust"
        and contract["status"]
        == "SOURCE FROZEN; ACTUAL V18 RUST CANDIDATE NOT RUN"
        and contract["source"]["sha256"] == FEATURE["source"][1]
        and contract["protocol"]["sha256"] == FEATURE["protocol"][1]
        and graph["version"] == 69
        and graph["authenticated_evidence_owner_lower_bound"] == 230
        and graph["authenticated_history_reference_lower_bound"] == 235
        and graph["resulting_evidence_owner_lower_bound"] == 233
        and graph["resulting_history_reference_lower_bound"] == 238
        and graph["new_source_owner_count"] == 3
        and rust["candidate_build_status"] == "PASS"
        and rust["actual_compiler_process_count"] == 28
        and rust["independent_private_root_provenance"] == "NOT ESTABLISHED"
        and rust["private_build_root"] == "NOT MEASURED"
        and rust["individual_native_elf_hashes"] == "NOT MEASURED"
        and rust["source_freeze_opens_archive"] is False
        and c["candidate_build_status"] == "PASS"
        and c["actual_compiler_process_count"] == 14
        and c["previous_candidate_matching_status"] == "FAIL"
        and c["previous_semantic_mismatch_count"] == 1230
        and c["previous_explicitly_verified_passing_case_count"] == 7325
        and c["source_freeze_opens_archive"] is False
        and history["candidate_status"] == "FAIL"
        and history["semantic_mismatch_count"] == 1440
        and history["explicitly_verified_passing_case_count"] == 14853
        and history["actual_candidate_workers"] == 13
        and inspect["existing_v18_inspection_status"] == BLOCKED
        and inspect["private_root_provenance"] == "NOT ESTABLISHED"
        and inspect["actual_compressed_archive_reads"] == 0
        and inspect["candidate_workers_started"] == 0
        and campaign["self_hosted_worker_count"] == 13
        and campaign["case_execution_denominator"] == 31237
        and campaign["suite_count"] == 13
        and campaign["requires_published_build_inspection"] is True
        and campaign["requires_separate_explicit_authorization"] is True
        and effects["actual_candidate_workers"] == 0
        and effects["actual_compiler_processes"] == 0
        and effects["actual_native_activations"] == 0
        and effects["actual_native_library_loads"] == 0
        and effects["build_private_root"] == "NOT MEASURED"
        and effects["native_artifact_hashes"] == "NOT MEASURED"
        and effects["private_build_root_enumerations"] == 0
        and effects["private_build_root_reads"] == 0
        and effects["v18_build_archive_reads"] == 0
        and effects["v18_build_archive_gzip_inflations"] == 0
        and effects["candidate_matching"] == "NOT RUN"
        and effects["candidate_correctness"] == "NOT MEASURED"
        and effects["candidate_qualified"] is False
        and effects["holdout"] == "NOT OPENED"
        and effects["performance"] == "NOT MEASURED"
        and effects["winner_selected"] is False,
        "reject candidate execution, native discovery, or invented correctness",
    )
    pins = [
        {
            "path": item[0], "sha256": item[1],
            "size_bytes": item[2], "device": 2064, "inode": item[3],
        }
        for item in V69.values()
    ]
    base.need(
        graph["owners"] == pins,
        "bind all four complete, genuinely pushed V69 predecessor owners",
    )


def feature_proof(
    base: types.ModuleType, owners: dict, contract: dict,
) -> dict:
    validate_contract(base, contract)
    return {
        "schema": SCHEMA + "-first-party-rust-original-campaign-v11",
        "version": 11,
        "family": "rust",
        "status": "SOURCE FROZEN",
        "owners": copy.deepcopy(owners),
        "complete_feature_contract": copy.deepcopy(contract),
        "independent_feature_source_owner_count": 3,
        "frozen_graph_version": 69,
        "frozen_graph_evidence_owner_lower_bound": 230,
        "frozen_graph_history_reference_lower_bound": 235,
        "candidate_execution_status": BLOCKED,
        "build_inspection_status": BLOCKED,
        "private_native_root_provenance": "NOT ESTABLISHED",
        "private_native_root": "NOT MEASURED",
        "native_artifact_hashes": "NOT MEASURED",
        "planned_candidate_worker_count": 13,
        "actual_candidate_worker_count": 0,
        "actual_reference_worker_count": 0,
        "actual_compiler_process_count": 0,
        "actual_native_activation_count": 0,
        "actual_compressed_archive_read_count": 0,
        "actual_archive_inflation_count": 0,
        "candidate_matching_status": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "supplemental_candidate_status": "NOT RUN",
        "historical_rust_matching_status": "FAIL",
        "historical_rust_semantic_mismatch_count": 1440,
        "historical_rust_verified_passing_case_count": 14853,
        "historical_c_matching_status": "FAIL",
        "historical_c_semantic_mismatch_count": 1230,
        "historical_c_verified_passing_case_count": 7325,
        "actual_previous_rust_build_status": "PASS",
        "actual_previous_rust_build_process_count": 28,
        "actual_previous_c_build_status": "PASS",
        "actual_previous_c_build_process_count": 14,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "source_only_effects": copy.deepcopy(contract["source_only_effects"]),
    }


def validate_proof(base: types.ModuleType, proof: object) -> None:
    base.need(
        type(proof) is dict,
        "reject missing complete source-only Rust V11 graph proof",
    )
    assert isinstance(proof, dict)
    contract = proof.get("complete_feature_contract")
    validate_contract(base, contract)
    assert isinstance(contract, dict)
    owners = {
        role: base.synthetic_owner(item[:3], item[3])
        for role, item in FEATURE.items()
    }
    expected = feature_proof(base, owners, contract)
    base.need(
        set(proof) == set(expected) and proof == expected,
        "reject fabricated Rust V11 execution, build root, or archived evidence",
    )


def authenticate_previous(
    previous: types.ModuleType,
    modules: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> tuple:
    for role, item in V69.items():
        supplied = getattr(options, "previous_" + role + "_sha256")
        base.need(
            base.checked(supplied, "exact pushed V69 " + role) == item[1],
            "reject substituted genuine V69 predecessor: " + role,
        )
    predecessor_options = previous_options(previous, modules)
    for role in ("source", "protocol", "contract"):
        supplied = getattr(options, "readiness_" + role + "_sha256")
        expected = getattr(
            predecessor_options, "readiness_" + role + "_sha256",
        )
        base.need(
            base.checked(supplied, "passing V4 oracle " + role) == expected,
            "reject substituted passing Python V4 correctness oracle",
        )
    raw = {
        role: _read_exact(item, "complete pushed V69 " + role)
        for role, item in V69.items()
    }
    old = base.document(raw["summary"], "complete actual V69 graph summary")
    old_inputs = base.document(raw["inputs"], "complete actual V69 graph inputs")
    reconstructed, pairs = previous.build(
        *modules, previous_options(previous, modules),
    )
    rendered = dict(pairs)
    previous.validate_snapshot(*modules, old.get("snapshot"))
    suites = old.get(
        "actual_rust_v10_complete_independently_authenticated_suite_results",
    )
    witnesses = old.get(
        "actual_rust_v10_earliest_genuine_mismatch_witnesses",
    )
    base.need(
        old.get("version") == 69
        and old.get("status") == "PASS"
        and old.get("actual_current_graph_predecessor_version") == 68
        and old.get("snapshot") == reconstructed
        and old.get("authenticated_evidence_owner_lower_bound") == 230
        and old.get("authenticated_history_reference_lower_bound") == 235
        and old.get("phase1_v4_oracle_readiness_status") == "PASS"
        and old.get("candidate_evaluation_authorized") is True
        and old.get("candidate_qualification_status") == "BLOCKED"
        and len(old.get("candidate_qualification_blockers", ())) == 7
        and old.get("rust_native_build_v17_authorization_status") == "BLOCKED"
        and old.get("rust_native_build_v18_status") == "PASS"
        and old.get("rust_native_build_v18_compiler_process_count") == 28
        and old.get("rust_native_build_v18_matching_status") == "NOT RUN"
        and old.get("c_native_build_v16_status") == "PASS"
        and old.get("c_native_build_v16_compiler_process_count") == 14
        and old.get("c_native_build_v16_matching_status") == "NOT RUN"
        and old.get("actual_rust_semantic_mismatch_count") == 1440
        and old.get("actual_rust_verified_passing_case_count") == 14853
        and old.get("actual_c_semantic_mismatch_count") == 1230
        and old.get("actual_c_verified_passing_case_count") == 7325
        and type(suites) is list
        and [len(row) for row in suites] == [12] + [11] * 12
        and type(witnesses) is list
        and [len(row) for row in witnesses] == [10, 10, 11, 11, 12, 12]
        and old_inputs.get(
            "actual_rust_v10_complete_independently_authenticated_suite_results"
        ) == suites
        and old_inputs.get(
            "actual_rust_v10_earliest_genuine_mismatch_witnesses"
        ) == witnesses
        and old["snapshot"].get(
            "actual_rust_v10_complete_independently_authenticated_suite_results"
        ) == suites
        and old["snapshot"].get(
            "actual_rust_v10_earliest_genuine_mismatch_witnesses"
        ) == witnesses
        and old.get("qualified_candidate_count") == 0
        and old.get("final_holdout_opened") is False
        and old.get("final_comparison_cases_generated") is False
        and all(raw[role] == rendered[item[0]] for role, item in V69.items()
                if role != "source"),
        "reproduce the complete V69 evidence without opening any archive",
    )
    return old, old_inputs, raw["svg"]


def authenticate_feature(
    base: types.ModuleType, options: argparse.Namespace,
) -> dict:
    for role, item in FEATURE.items():
        supplied = getattr(options, "feature_" + role + "_sha256")
        base.need(
            base.checked(supplied, "frozen Rust V11 " + role) == item[1],
            "reject substituted first-party Rust V11 source: " + role,
        )
    raw = {
        role: _read_exact(item, "frozen first-party Rust V11 " + role)
        for role, item in FEATURE.items()
    }
    contract = base.document(raw["contract"], "complete frozen Rust V11 contract")
    validate_contract(base, contract)
    owners = {
        role: base.synthetic_owner(item[:3], item[3])
        for role, item in FEATURE.items()
    }
    proof = feature_proof(base, owners, contract)
    validate_proof(base, proof)
    return proof


def updates(proof: dict) -> dict:
    return {
        "actual_current_graph_predecessor_version": 69,
        "authenticated_evidence_owner_lower_bound": 233,
        "authenticated_history_reference_lower_bound": 238,
        "rust_v11_original_campaign_source_freeze": copy.deepcopy(proof),
        "rust_v11_original_campaign_source_status": "SOURCE FROZEN",
        "rust_v11_original_campaign_execution_status": BLOCKED,
        "rust_v11_original_campaign_build_inspection_status": BLOCKED,
        "rust_v11_original_campaign_private_root_provenance": "NOT ESTABLISHED",
        "rust_v11_original_campaign_private_root": "NOT MEASURED",
        "rust_v11_original_campaign_native_artifact_hashes": "NOT MEASURED",
        "rust_v11_original_campaign_planned_worker_count": 13,
        "rust_v11_original_campaign_actual_worker_count": 0,
        "rust_v11_original_campaign_matching_status": "NOT RUN",
        "rust_v11_original_campaign_candidate_correctness": "NOT MEASURED",
        "rust_v11_original_campaign_candidate_qualified": False,
        "rust_v11_original_campaign_frozen_graph_version": 69,
        "rust_v11_original_campaign_frozen_graph_evidence_owner_lower_bound": 230,
        "rust_v11_original_campaign_frozen_graph_history_reference_lower_bound": 235,
        "rust_v11_original_campaign_independent_source_owner_count": 3,
        "rust_v11_original_campaign_actual_archive_reads": 0,
        "rust_v11_original_campaign_actual_archive_inflations": 0,
        "rust_v11_original_campaign_actual_native_activations": 0,
        "actual_feature_source_owners_read_by_graph": 3,
        "actual_reference_workers_started_by_graph": 0,
        "actual_candidate_imports_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_compiler_processes_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "actual_compressed_evidence_owners_opened_by_graph": 0,
        "actual_compressed_evidence_bytes_read_by_graph": 0,
        "actual_compressed_evidence_inflations_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }


def validate_snapshot(
    previous: types.ModuleType, modules: tuple,
    base: types.ModuleType, snapshot: object,
) -> None:
    base.need(
        type(snapshot) is dict,
        "reject missing full V70 Rust V11 source-freeze snapshot",
    )
    assert isinstance(snapshot, dict)
    proof = snapshot.get("rust_v11_original_campaign_source_freeze")
    validate_proof(base, proof)
    assert isinstance(proof, dict)
    changes = updates(proof)
    for key, value in changes.items():
        base.need(
            type(snapshot.get(key)) is type(value)
            and snapshot.get(key) == value,
            "reject invented Rust V11 activity or root: " + key,
        )
    replaced = snapshot.get("preserved_v69_replaced_snapshot_fields")
    base.need(
        type(replaced) is dict
        and set(replaced).issubset(changes)
        and replaced.get("actual_current_graph_predecessor_version") == 68
        and replaced.get("authenticated_evidence_owner_lower_bound") == 230
        and replaced.get("authenticated_history_reference_lower_bound") == 235,
        "preserve complete actual V69 history and evidence lower bounds",
    )
    assert isinstance(replaced, dict)
    original = copy.deepcopy(snapshot)
    original.pop("preserved_v69_replaced_snapshot_fields", None)
    for key in changes:
        if key in replaced:
            original[key] = copy.deepcopy(replaced[key])
        else:
            original.pop(key, None)
    previous.validate_snapshot(*modules, original)
    suites = snapshot.get(
        "actual_rust_v10_complete_independently_authenticated_suite_results",
    )
    witnesses = snapshot.get(
        "actual_rust_v10_earliest_genuine_mismatch_witnesses",
    )
    base.need(
        type(suites) is list
        and [len(row) for row in suites] == [12] + [11] * 12
        and type(witnesses) is list
        and [len(row) for row in witnesses] == [10, 10, 11, 11, 12, 12]
        and suites == original.get(
            "actual_rust_v10_complete_independently_authenticated_suite_results"
        )
        and witnesses == original.get(
            "actual_rust_v10_earliest_genuine_mismatch_witnesses"
        )
        and snapshot.get("actual_current_graph_predecessor_version") == 69
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 233
        and snapshot.get("authenticated_history_reference_lower_bound") == 238
        and snapshot.get("phase1_v4_oracle_readiness_status") == "PASS"
        and snapshot.get("candidate_evaluation_authorized") is True
        and snapshot.get("candidate_qualification_status") == "BLOCKED"
        and len(snapshot.get("candidate_qualification_blockers", ())) == 7
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("rust_native_build_v17_authorization_status") == "BLOCKED"
        and snapshot.get("rust_native_build_v18_status") == "PASS"
        and snapshot.get("rust_native_build_v18_compiler_process_count") == 28
        and snapshot.get("rust_native_build_v18_matching_status") == "NOT RUN"
        and snapshot.get("c_native_build_v16_status") == "PASS"
        and snapshot.get("c_native_build_v16_compiler_process_count") == 14
        and snapshot.get("c_native_build_v16_matching_status") == "NOT RUN"
        and snapshot.get("actual_rust_semantic_mismatch_count") == 1440
        and snapshot.get("actual_rust_verified_passing_case_count") == 14853
        and snapshot.get("actual_c_semantic_mismatch_count") == 1230
        and snapshot.get("actual_c_verified_passing_case_count") == 7325
        and snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("final_holdout_opened") is False
        and snapshot.get("final_comparison_cases_generated") is False,
        "preserve exact complete matching evidence, builds, blockers, and holdout",
    )


def make_svg(
    base: types.ModuleType, snapshot: dict, old_svg: bytes,
    source_sha: str, inputs_sha: str,
) -> bytes:
    base.need(
        b'aria-labelledby="v69-title v69-description"' in old_svg
        and b"1,230" in old_svg and b"1,440" in old_svg,
        "bind the actual accessible V69 comparison before updating the chart",
    )
    source_sha = base.checked(source_sha, "exact V70 graph renderer")
    inputs_sha = base.checked(inputs_sha, "exact V70 graph inputs")
    text = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1430" viewBox="0 0 1400 1430" role="img" aria-labelledby="v70-title v70-description">',
        '<title id="v70-title">Building a faster Python re: six original engines, no proven winner</title>',
        '<desc id="v70-description">Pinned Python 3.14.6 is the verified reference. Rust and C both compile from first-party source, but their latest real matching tests still fail. The new Rust compatibility campaign is source-frozen and blocked because the independently attested private native-build root is not established. Its 13 future workers have not run. All 31,237 original cases, 13 complete original result groups, and six complete mismatch events remain unchanged. No compressed archive or hidden 4,194,304-case holdout was opened. Speed, memory, runtime independence, and a winner are not measured.</desc>',
        '<style>.bg{fill:#f6f8fc}.card{fill:#fff;stroke:#d9e2ee;stroke-width:1}.title{font:700 31px system-ui,sans-serif;fill:#152536}.subtitle{font:16px system-ui,sans-serif;fill:#536578}.heading{font:700 19px system-ui,sans-serif;fill:#152536}.body{font:15px system-ui,sans-serif;fill:#26394b}.small{font:13px system-ui,sans-serif;fill:#536578}.foot{font:11px ui-monospace,monospace;fill:#536578}.good{fill:#137a48}.warn{fill:#9b6500}.fail{fill:#bf3548}.pillgood{fill:#e8f7ee}.pillwarn{fill:#fff3d7}.pillfail{fill:#ffebee}</style>',
        '<rect class="bg" width="1400" height="1430"/>',
        '<text x="54" y="72" class="title">Building a faster Python re</text>',
        '<text x="54" y="103" class="subtitle">Our own engines. Python is the reference. No candidate is proven compatible or faster.</text>',
        '<rect x="44" y="130" width="1312" height="118" rx="15" class="card"/>',
        '<text x="67" y="163" class="heading">Overall result compared with Python</text>',
        '<rect x="68" y="180" width="345" height="43" rx="10" class="pillfail"/>',
        '<text x="84" y="207" class="body fail">0 compatible candidates; speed NOT MEASURED</text>',
        '<text x="438" y="207" class="body">A successful native build does not mean the engine matches Python.</text>',
        '<rect x="44" y="264" width="1312" height="380" rx="15" class="card"/>',
        '<text x="67" y="298" class="heading">How the original, from-scratch engines are doing</text>',
        '<text x="68" y="327" class="small">The same frozen Python compatibility tests apply to every family. This is not a speed ranking.</text>',
        '<text x="70" y="370" class="body">Python reference</text>',
        '<text x="231" y="370" class="body good">Verified reference; stable CPython 3.14.6</text>',
        '<text x="70" y="415" class="body">Rust engine</text>',
        '<text x="231" y="415" class="body fail">Build PASS (28); matching FAIL: 1,440 differences; 14,853 independently verified passes</text>',
        '<text x="70" y="460" class="body">C engine</text>',
        '<text x="231" y="460" class="body fail">Build PASS (14); matching FAIL: 1,230 differences; 7,325 independently verified passes</text>',
        '<text x="70" y="505" class="body">Zig engine</text>',
        '<text x="231" y="505" class="body warn">Not correctness-qualified; performance NOT MEASURED</text>',
        '<text x="70" y="545" class="body">C++ engine</text>',
        '<text x="231" y="545" class="body warn">Not correctness-qualified; performance NOT MEASURED</text>',
        '<text x="70" y="585" class="body">Go engine</text>',
        '<text x="231" y="585" class="body warn">Not correctness-qualified; performance NOT MEASURED</text>',
        '<text x="70" y="625" class="body">Fortran engine</text>',
        '<text x="231" y="625" class="body warn">Not correctness-qualified; performance NOT MEASURED</text>',
        '<rect x="44" y="663" width="1312" height="208" rx="15" class="card"/>',
        '<text x="67" y="697" class="heading">Why the next Rust test is not running</text>',
        '<rect x="68" y="717" width="812" height="43" rx="10" class="pillwarn"/>',
        '<text x="83" y="744" class="body warn">BLOCKED PENDING INDEPENDENTLY ATTESTED PRIVATE ROOT</text>',
        '<text x="69" y="790" class="body">The Rust V11 original campaign is SOURCE FROZEN. Its 13 workers are planned; 0 have run.</text>',
        '<text x="69" y="820" class="body">Native build root and individual native artifact hashes: NOT ESTABLISHED / NOT MEASURED.</text>',
        '<text x="69" y="850" class="small">Future inspection requires separate authorization. This chart does not inspect, discover, or guess a root.</text>',
        '<rect x="44" y="888" width="1312" height="156" rx="15" class="card"/>',
        '<text x="67" y="921" class="heading">What has and has not been measured</text>',
        '<text x="69" y="956" class="body">Original compatibility cases: 31,237 across 13 complete groups; six complete failure events preserved.</text>',
        '<text x="69" y="986" class="body">Supplemental Python reference: 8,244 cases. New candidate matching: NOT RUN.</text>',
        '<text x="69" y="1016" class="body">Speed, memory, confidence intervals and runtime independence: NOT MEASURED / NOT ESTABLISHED.</text>',
        '<rect x="44" y="1062" width="1312" height="340" rx="15" class="card"/>',
        '<text x="67" y="1095" class="heading">Reproducible source and evidence</text>',
    ]
    footers = (
        ("Graph renderer SHA-256", source_sha),
        ("Graph inputs SHA-256", inputs_sha),
        ("Current V69 predecessor renderer SHA-256", V69["source"][1]),
        ("Current V69 predecessor summary SHA-256", V69["summary"][1]),
        ("First-party Rust V11 campaign source SHA-256", FEATURE["source"][1]),
        ("First-party Rust V11 campaign protocol SHA-256", FEATURE["protocol"][1]),
        ("First-party Rust V11 campaign contract SHA-256", FEATURE["contract"][1]),
        ("Passing first-party Rust V18 build receipt SHA-256",
         "32c422b9624a2565afd8d710700e377aa39aae4aa93d3742da483843869f2104"),
        ("Passing first-party C V16 build receipt SHA-256",
         "16794f5b1487b76a909a176948f4bbac8ed3108768f3127e27c44f9f392ae3d6"),
    )
    for index, (label, value) in enumerate(footers):
        text.append(
            f'<text x="68" y="{1120 + index * 18}" class="foot">'
            f'{label}: {value}</text>'
        )
    text.extend((
        '<text x="69" y="1305" class="small">Previous evidence lower bounds: 230 / 235; current source-only lower bounds: 233 / 238.</text>',
        '<text x="69" y="1330" class="small">Seven qualification blockers remain. Rust V17 remains BLOCKED. Qualified candidates: 0.</text>',
        '<text x="69" y="1355" class="small">Compressed build evidence: NOT OPENED. Hidden 4,194,304-case holdout: NOT GENERATED and NOT OPENED.</text>',
        '<text x="69" y="1380" class="small">Candidate workers, compiler launches, native activation, timing and hidden-case access by this graph: 0.</text>',
        '<!-- The graph authenticates only its three source owners and exact predecessor; it never opens compressed evidence, runs a candidate, guesses a native root, benchmarks, or opens the holdout. -->',
        '</svg>',
    ))
    raw = ("\n".join(text) + "\n").encode("utf-8")
    lower = raw.lower()
    for phrase in (
        b"building a faster python re", b"overall result compared with python",
        b"0 compatible candidates", b"speed not measured",
        b"rust", b"c engine", b"zig", b"c++", b"go engine", b"fortran",
        b"pass (28)", b"pass (14)", b"1,440", b"14,853", b"1,230",
        b"7,325", b"31,237", b"13 complete", b"six complete",
        b"blocked pending independently attested private root",
        b"source frozen", b"13 workers", b"0 have run",
        b"not established", b"not measured", b"not run",
        b"230 / 235", b"233 / 238", b"8,244", b"4,194,304",
        b"not generated", b"not opened", b"seven", b"rust v17",
    ):
        base.need(phrase in lower, "retain honest readable V70 evidence: " + repr(phrase))
    for falsehood in (
        b"candidate matching passed", b"rust matching passed",
        b"c matching passed", b"candidate qualified", b"private root discovered",
        b"private root established", b"holdout opened", b"holdout generated",
        b"benchmark speedup", b"winner selected", b"archive decompressed",
    ):
        base.need(
            falsehood not in lower,
            "reject invented native root, candidate result, or performance",
        )
    for label, value in footers:
        base.need(
            raw.count((label + ": " + value).encode("ascii")) == 1,
            "bind each exact V70 chart evidence footer only once",
        )
    base.need(snapshot["rust_v11_original_campaign_execution_status"] == BLOCKED,
              "chart must never call a blocked candidate runnable")
    return raw


def build(
    previous: types.ModuleType, modules: tuple,
    base: types.ModuleType, options: argparse.Namespace,
) -> tuple:
    source_sha = base.checked(options.source_sha256, "exact V70 graph source")
    base.need(
        type(options.source_bytes) is int
        and 0 < options.source_bytes <= base.OWNER_LIMIT,
        "bound the only authorized V70 graph source",
    )
    source_raw, _ = base.read_owner(
        SELF, source_sha, options.source_bytes, private=True,
    )
    old, old_inputs, old_svg = authenticate_previous(
        previous, modules, base, options,
    )
    proof = authenticate_feature(base, options)
    changes = updates(proof)
    original = old["snapshot"]
    snapshot = copy.deepcopy(original)
    snapshot.update(changes)
    snapshot["preserved_v69_replaced_snapshot_fields"] = {
        key: copy.deepcopy(original[key])
        for key in changes if key in original
    }
    validate_snapshot(previous, modules, base, snapshot)
    predecessor = {
        role: base.pin(*item[:3]) for role, item in V69.items()
    }
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 70,
        "python": "3.14.6",
        "renderer": base.pin(SELF, source_sha, len(source_raw)),
        "previous_overview": predecessor,
        **changes,
    })
    input_raw = base.canonical(inputs)
    svg = make_svg(base, snapshot, old_svg, source_sha, base.digest(input_raw))
    families = copy.deepcopy(old["families"])
    base.need(
        [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"],
        "preserve Python and all six independent from-scratch families",
    )
    for row in families:
        if row.get("family") != "python":
            row.update({
                "authenticated_evidence_owner_lower_bound": 233,
                "authenticated_history_reference_lower_bound": 238,
                "qualified": False,
                "performance": "NOT MEASURED",
            })
        if row.get("family") == "rust":
            row.update({
                "current_original_campaign_candidate_status": "FAIL",
                "current_original_campaign_semantic_mismatch_count": 1440,
                "current_original_campaign_verified_passing_case_count": 14853,
                "rust_native_build_v18_status": "PASS",
                "rust_native_build_v18_compiler_process_count": 28,
                "rust_v11_original_campaign_source_status": "SOURCE FROZEN",
                "rust_v11_original_campaign_execution_status": BLOCKED,
                "rust_v11_original_campaign_planned_worker_count": 13,
                "rust_v11_original_campaign_actual_worker_count": 0,
                "rust_v11_original_campaign_matching_status": "NOT RUN",
                "rust_v11_original_campaign_candidate_correctness":
                    "NOT MEASURED",
                "rust_v11_original_campaign_candidate_qualified": False,
                "rust_v11_original_campaign_source_freeze":
                    copy.deepcopy(proof),
            })
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 70,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, source_sha, len(source_raw)),
        "inputs": base.pin(
            OUTPUT + ".inputs.json", base.digest(input_raw), len(input_raw),
        ),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": predecessor,
        "snapshot": snapshot,
        "families": families,
        **changes,
    })
    suites = old[
        "actual_rust_v10_complete_independently_authenticated_suite_results"
    ]
    witnesses = old[
        "actual_rust_v10_earliest_genuine_mismatch_witnesses"
    ]
    for label, layer in (
        ("complete V70 inputs", inputs),
        ("complete V70 summary", summary),
        ("complete V70 snapshot", snapshot),
    ):
        base.need(
            layer.get(
                "actual_rust_v10_complete_independently_authenticated_suite_results"
            ) == suites
            and layer.get(
                "actual_rust_v10_earliest_genuine_mismatch_witnesses"
            ) == witnesses,
            "preserve every complete heterogeneous original result: " + label,
        )
    base.need(
        summary["actual_current_graph_predecessor_version"] == 69
        and snapshot["preserved_v69_replaced_snapshot_fields"]
            ["actual_current_graph_predecessor_version"] == 68
        and summary["authenticated_evidence_owner_lower_bound"] == 233
        and summary["authenticated_history_reference_lower_bound"] == 238
        and summary["rust_v11_original_campaign_execution_status"] == BLOCKED
        and summary["rust_v11_original_campaign_actual_worker_count"] == 0
        and summary["rust_native_build_v18_status"] == "PASS"
        and summary["rust_native_build_v18_compiler_process_count"] == 28
        and summary["c_native_build_v16_status"] == "PASS"
        and summary["c_native_build_v16_compiler_process_count"] == 14
        and summary["actual_rust_semantic_mismatch_count"] == 1440
        and summary["actual_c_semantic_mismatch_count"] == 1230
        and summary["qualified_candidate_count"] == 0
        and summary["final_holdout_opened"] is False,
        "separate genuine C and Rust builds from the blocked unrun V11 campaign",
    )
    summary_raw = base.canonical(summary)
    base.need(
        max(len(input_raw), len(summary_raw), len(svg)) <= base.OWNER_LIMIT,
        "bound exactly three authorized complete V70 graph assets",
    )
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", summary_raw),
        (OUTPUT + ".svg", svg),
    )


def forged(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + " [FORGED]"
    if type(value) is list:
        return [*value, {"__forged_v70__": True}]
    if type(value) is dict:
        return {**value, "__forged_v70__": True}
    if value is None:
        return "__forged_v70__"
    raise TypeError("unsupported forged Rust V11 value")


def reject_control(
    base: types.ModuleType, candidate: dict, label: str,
) -> int:
    try:
        validate_proof(base, candidate)
    except (ValueError, OSError, TypeError, KeyError, AttributeError,
            RecursionError, UnicodeError):
        return 1
    except Exception as error:
        if type(error).__name__ == "GraphError":
            return 1
        raise
    base.need(False, "accepts forged frozen Rust V11 control: " + label)
    return 0


def self_test(
    previous: types.ModuleType, modules: tuple, base: types.ModuleType,
) -> dict:
    prior = previous.self_test(*modules)
    base.need(
        prior.get("status") == "PASS"
        and prior.get("rejected_hostile_control_count") == 5931
        and prior.get("actual_current_graph_predecessor_version") == 68
        and prior.get("authenticated_evidence_owner_lower_bound") == 230
        and prior.get("authenticated_history_reference_lower_bound") == 235
        and prior.get("rust_native_build_v18_status") == "PASS"
        and prior.get("rust_native_build_v18_compiler_process_count") == 28
        and prior.get("c_native_build_v16_status") == "PASS"
        and prior.get("c_native_build_v16_compiler_process_count") == 14
        and prior.get("actual_rust_semantic_mismatch_count") == 1440
        and prior.get("actual_c_semantic_mismatch_count") == 1230,
        "preserve all 5,931 exact pushed V69 source-only hostile controls",
    )
    rejected = 0
    with base.SourceOnlyWall() as wall:
        owners = {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in FEATURE.items()
        }
        contract = synthetic_contract()
        proof = feature_proof(base, owners, contract)
        validate_proof(base, proof)
        for key, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[key] = forged(value)
            rejected += reject_control(base, hostile, "proof:" + key)
        for role, owner in owners.items():
            for key, value in owner.items():
                hostile = copy.deepcopy(proof)
                hostile["owners"][role][key] = forged(value)
                rejected += reject_control(
                    base, hostile, "owner:" + role + ":" + key,
                )
        for key, value in contract.items():
            hostile = copy.deepcopy(proof)
            hostile["complete_feature_contract"][key] = forged(value)
            rejected += reject_control(base, hostile, "contract:" + key)
        for group in (
            "source_only_effects", "current_pushed_graph",
            "future_authorized_build_inspection",
            "future_authorized_original_campaign",
            "actual_first_party_v18_build",
            "actual_first_party_c_v16_build",
            "genuine_previous_v10_original_campaign",
        ):
            for key, value in contract[group].items():
                hostile = copy.deepcopy(proof)
                hostile["complete_feature_contract"][group][key] = forged(value)
                rejected += reject_control(
                    base, hostile, "contract:" + group + ":" + key,
                )
        base.need(
            rejected >= 135,
            "require fail-closed whole-contract V11 source and root controls",
        )
        result = {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 70,
            "status": "PASS",
            "previous_v69_hostile_controls": 5931,
            "new_v70_hostile_controls": rejected,
            "rejected_hostile_control_count": 5931 + rejected,
            "source_only_controls_blocked_by_kind": dict(wall.blocked),
            "actual_current_graph_predecessor_version": 69,
            "authenticated_evidence_owner_lower_bound": 233,
            "authenticated_history_reference_lower_bound": 238,
            "actual_rust_semantic_mismatch_count": 1440,
            "actual_rust_verified_passing_case_count": 14853,
            "actual_c_semantic_mismatch_count": 1230,
            "actual_c_verified_passing_case_count": 7325,
            "phase1_v4_oracle_readiness_status": "PASS",
            "candidate_evaluation_authorized": True,
            "candidate_qualification_status": "BLOCKED",
            "candidate_qualification_blocker_count": 7,
            "rust_native_build_v17_authorization_status": "BLOCKED",
            "rust_native_build_v18_status": "PASS",
            "rust_native_build_v18_compiler_process_count": 28,
            "rust_native_build_v18_matching_status": "NOT RUN",
            "c_native_build_v16_status": "PASS",
            "c_native_build_v16_compiler_process_count": 14,
            "c_native_build_v16_matching_status": "NOT RUN",
            "rust_v11_original_campaign_source_status": "SOURCE FROZEN",
            "rust_v11_original_campaign_execution_status": BLOCKED,
            "rust_v11_original_campaign_build_inspection_status": BLOCKED,
            "rust_v11_original_campaign_private_root_provenance":
                "NOT ESTABLISHED",
            "rust_v11_original_campaign_private_root": "NOT MEASURED",
            "rust_v11_original_campaign_native_artifact_hashes":
                "NOT MEASURED",
            "rust_v11_original_campaign_planned_worker_count": 13,
            "rust_v11_original_campaign_actual_worker_count": 0,
            "rust_v11_original_campaign_matching_status": "NOT RUN",
            "rust_v11_original_campaign_frozen_graph_version": 69,
            "rust_v11_original_campaign_frozen_graph_evidence_owner_lower_bound":
                230,
            "rust_v11_original_campaign_frozen_graph_history_reference_lower_bound":
                235,
            "actual_feature_source_owners_read_by_self_test": 0,
            "actual_candidate_imports_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_compiler_processes_started_by_graph": 0,
            "actual_native_libraries_loaded_by_graph": 0,
            "actual_compressed_evidence_owners_opened_by_graph": 0,
            "actual_compressed_evidence_bytes_read_by_graph": 0,
            "actual_compressed_evidence_inflations_by_graph": 0,
            "actual_clock_samples_by_graph": 0,
            "actual_hidden_cases_read_by_graph": 0,
            "full_case_denominator": 31237,
            "suite_count": 13,
            "first_party_source_inventory_family_count": 6,
            "qualified_candidate_count": 0,
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "confidence_intervals": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "winner_selected": False,
        }
    return result


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {
            OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg",
        }
        and type(raw) is bytes
        and 0 < len(raw) <= base.OWNER_LIMIT,
        "publish only the three exclusively authorized V70 graph assets",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(
                type(count) is int and count > 0,
                "publish every exact exclusive V70 graph byte",
            )
            remaining = remaining[count:]
        os.fsync(handle)
        owner = os.fstat(handle)
        base.need(
            owner.st_uid == os.geteuid()
            and owner.st_dev == 2064
            and owner.st_nlink == 1
            and owner.st_size == len(raw)
            and stat.S_IMODE(owner.st_mode) == 0o600,
            "publish a complete privately owned exclusive V70 graph asset",
        )
    finally:
        os.close(handle)
    confirmed, _ = base.read_owner(
        path, base.digest(raw), len(raw), private=True,
    )
    base.need(confirmed == raw, "reauthenticate the complete new V70 graph asset")


def compact_result(
    base: types.ModuleType, snapshot: dict,
    outputs: dict, source_sha: str, written: bool,
) -> dict:
    fields = (
        "actual_current_graph_predecessor_version",
        "authenticated_evidence_owner_lower_bound",
        "authenticated_history_reference_lower_bound",
        "actual_rust_semantic_mismatch_count",
        "actual_rust_verified_passing_case_count",
        "actual_c_semantic_mismatch_count",
        "actual_c_verified_passing_case_count",
        "phase1_v4_oracle_readiness_status",
        "candidate_evaluation_authorized",
        "candidate_qualification_status",
        "candidate_qualification_blockers",
        "rust_native_build_v17_authorization_status",
        "rust_native_build_v17_status",
        "rust_native_build_v18_status",
        "rust_native_build_v18_reproducible_build_status",
        "rust_native_build_v18_compiler_process_count",
        "rust_native_build_v18_matching_status",
        "rust_native_build_v18_archive_opened_by_graph",
        "c_native_build_v16_status",
        "c_native_build_v16_reproducible_build_status",
        "c_native_build_v16_compiler_process_count",
        "c_native_build_v16_compiler_process_ids",
        "c_native_build_v16_individual_elf_artifact_hashes",
        "c_native_build_v16_matching_status",
        "c_native_build_v16_archive_opened_by_graph",
        "rust_v11_original_campaign_source_status",
        "rust_v11_original_campaign_execution_status",
        "rust_v11_original_campaign_build_inspection_status",
        "rust_v11_original_campaign_private_root_provenance",
        "rust_v11_original_campaign_private_root",
        "rust_v11_original_campaign_native_artifact_hashes",
        "rust_v11_original_campaign_planned_worker_count",
        "rust_v11_original_campaign_actual_worker_count",
        "rust_v11_original_campaign_matching_status",
        "rust_v11_original_campaign_candidate_correctness",
        "rust_v11_original_campaign_candidate_qualified",
        "rust_v11_original_campaign_frozen_graph_version",
        "rust_v11_original_campaign_frozen_graph_evidence_owner_lower_bound",
        "rust_v11_original_campaign_frozen_graph_history_reference_lower_bound",
        "rust_v11_original_campaign_independent_source_owner_count",
        "rust_v11_original_campaign_actual_archive_reads",
        "rust_v11_original_campaign_actual_archive_inflations",
        "rust_v11_original_campaign_actual_native_activations",
        "actual_feature_source_owners_read_by_graph",
        "actual_reference_workers_started_by_graph",
        "actual_candidate_imports_by_graph",
        "actual_candidate_workers_started_by_graph",
        "actual_compiler_processes_started_by_graph",
        "actual_native_libraries_loaded_by_graph",
        "actual_compressed_evidence_owners_opened_by_graph",
        "actual_compressed_evidence_bytes_read_by_graph",
        "actual_compressed_evidence_inflations_by_graph",
        "actual_clock_samples_by_graph",
        "actual_hidden_cases_read_by_graph",
        "full_case_denominator",
        "suite_count",
        "first_party_source_inventory_family_count",
        "qualified_candidate_count",
        "final_comparison_planned_case_count",
        "final_comparison_cases_generated",
        "final_holdout_opened",
        "runtime_no_delegation",
        "performance",
        "memory",
        "confidence_intervals",
        "undefined_behavior",
        "winner_selected",
    )
    return {
        "schema": SCHEMA + (
            "-published" if written else "-read-only-frozen-context"
        ),
        "version": 70,
        "status": "PASS",
        "source_sha256": source_sha,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 69,
        **{
            "previous_overview_" + role + "_sha256": item[1]
            for role, item in V69.items()
        },
        **{
            "feature_" + role + "_sha256": item[1]
            for role, item in FEATURE.items()
        },
        **{key: copy.deepcopy(snapshot[key]) for key in fields},
        "outputs_written": written,
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    for role in V69:
        parser.add_argument("--previous-" + role + "-sha256")
    for role in FEATURE:
        parser.add_argument("--feature-" + role + "-sha256")
    for role in ("source", "protocol", "contract"):
        parser.add_argument("--readiness-" + role + "-sha256")
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, modules, base = load_v69()
        if options.self_test:
            forbidden = [
                "source_sha256", "source_bytes", "inputs_sha256",
                "summary_sha256", "svg_sha256",
            ]
            forbidden += [
                "previous_" + role + "_sha256" for role in V69
            ]
            forbidden += [
                "feature_" + role + "_sha256" for role in FEATURE
            ]
            forbidden += [
                "readiness_" + role + "_sha256"
                for role in ("source", "protocol", "contract")
            ]
            base.need(
                all(getattr(options, key) is None for key in forbidden),
                "source-only V70 self-test never opens frozen V11 owners",
            )
            sys.stdout.buffer.write(
                base.canonical(self_test(previous, modules, base)),
            )
            return 0
        snapshot, pairs = build(previous, modules, base, options)
        outputs = dict(pairs)
        source_sha = base.checked(
            options.source_sha256, "exact exclusively authorized V70 source",
        )
        if options.render:
            base.need(
                options.inputs_sha256 is None
                and options.summary_sha256 is None
                and options.svg_sha256 is None,
                "publish exactly the three exclusively authorized V70 assets",
            )
            for path, raw in pairs:
                publish(base, path, raw)
            result = compact_result(
                base, snapshot, outputs, source_sha, True,
            )
        else:
            expected = {
                OUTPUT + ".inputs.json": base.checked(
                    options.inputs_sha256, "complete V70 graph inputs",
                ),
                OUTPUT + ".json": base.checked(
                    options.summary_sha256, "complete V70 graph summary",
                ),
                OUTPUT + ".svg": base.checked(
                    options.svg_sha256, "complete V70 graph chart",
                ),
            }
            for path, fingerprint in expected.items():
                raw, _ = base.read_owner(
                    path, fingerprint, len(outputs[path]), private=True,
                )
                base.need(
                    raw == outputs[path],
                    "reproduce the complete authorized V70 asset: " + path,
                )
            result = compact_result(
                base, snapshot, outputs, source_sha, False,
            )
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except (
        ValueError, OSError, TypeError, EOFError, KeyError,
        AttributeError, RecursionError, UnicodeError,
    ) as error:
        sys.stderr.write("current V70 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write(
                "current V70 overview rejected: " + str(error) + "\n",
            )
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
