#!/usr/bin/env python3
"""Freeze one evidence-backed, source-only first-party C Match correction."""

from __future__ import annotations

import ast
import builtins
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/apply_owned_c_original_match_semantics_v1.py"
PROTOCOL = "oracle/phase2/C-ORIGINAL-MATCH-SEMANTICS-V1.md"
CONTRACT = "oracle/phase2/c-original-match-semantics-v1.json"
SCHEMA = "rebar-owned-c-original-match-semantics-v1"
LABEL = "phase2-c-original-match-pickle-semantics-v1"
DEVICE = 2064
MAX_OWNER = 8 * 1024 * 1024
ORIGINAL_CASE_COUNT = 31237
REFERENCE_CASE_COUNT = 8244
PRIVATE_WAIVER_COUNT = 13
PROPOSED_HOLDOUT_CASE_COUNT = 14155776

V6 = (
    ("tools/run_owned_repaired_c_original_campaign_v6.py",
     "2f259e81c56e6ba8e3264709ae36187c7e0659020a5c398c68b0a7bf1d2be999",
     97043, 431024),
    ("oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V6.md",
     "a0e856f4fa94369340f0794f9ae34355aca6cdc7f4cb5ab13ec56e9c91b04778",
     7278, 525103),
    ("oracle/phase2/repaired-c-original-campaign-v6.json",
     "124e6ef03136aec2249809f09a57185813c86fc1c78c8b1063971af0a34ccf64",
     15623, 525104),
)
V7 = (
    ("tools/run_owned_repaired_c_original_campaign_v7.py",
     "42d27c321a54cbe2a730ce20967f786bc354340c35501e9d2a4cd37b4948884e",
     56985, 431138),
    ("oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V7.md",
     "99b3321a54cc36ad065f0d4178e34e0baf60349b4c85fb22794dbf26b33b9b0a",
     5485, 525186),
    ("oracle/phase2/repaired-c-original-campaign-v7.json",
     "ce59aa6e7b900095dad4875d6e911dd9983fa6834c7d810f2e8c729c1c880811",
     18786, 525195),
)
ACTUAL_FAILURE = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v7-c-phase2-v18-"
    "c-subject-buffer-root-provenance-original-p0-v7-failures-"
    "publication-receipt.json",
    "bba4b8498a37db0bf9651c0bb040deaf96f9eef363ba6f2e2c923379d7fa5080",
    7375, 525199,
)
SUITE_SOURCES = (
    ("tools/independent_managed_buffer_lifetime_v1.py",
     "cedbab1227ea58a97d407cb339d2959a9f9be58a2085ce3106b65bb3385de489",
     123890, 430528),
    ("tools/independent_public_type_identity_serialization_v1.py",
     "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20",
     150015, 432032),
    ("tools/python_re_buffer_exporter_oracle_v4.py",
     "8da0b8e5c5519e7335cd1b53ceb7042f1da1f902c486ad8ac35ddf53d8a04490",
     162181, 432192),
    ("tools/independent_substitution_buffer_semantics_v2.py",
     "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573",
     317541, 432058),
    ("tools/python_re_public_surface_oracle_stage19.py",
     "fda386f3c00be660a41e92d8005fc287706d9dc050967cf2b708cb6f8aba113e",
     199366, 430521),
    ("tools/python_re_threaded_pattern_oracle_v1.py",
     "05226e59736d8721a975eda8afa10247213999690c2766a7b3235c567b9f8276",
     146417, 432206),
)
EXPECTED_ROWS = (
    ("original_bounded_v5", 151, 81, "FAIL", "CANDIDATE EXECUTION FAILURE",
     "NOT MEASURED", "ActualSuiteFailure", "OBSERVE COMPLETE ORIGINAL SUITE"),
    ("public_v3", 864, 82, "FAIL", "CANDIDATE EXECUTION FAILURE",
     "NOT MEASURED", "ActualSuiteFailure", "OBSERVE COMPLETE ORIGINAL SUITE"),
    ("scanner_v3", 1024, 83, "FAIL", "CANDIDATE EXECUTION FAILURE",
     "NOT MEASURED", "ActualSuiteFailure", "OBSERVE COMPLETE ORIGINAL SUITE"),
    ("buffer_v3", 768, 84, "FAIL", "CANDIDATE EXECUTION FAILURE",
     "NOT MEASURED", "ActualSuiteFailure", "OBSERVE COMPLETE ORIGINAL SUITE"),
    ("managed_v1", 1024, 85, "FAIL", "SEMANTIC MISMATCH", 16,
     "NOT APPLICABLE", "OBSERVE COMPLETE ORIGINAL SUITE"),
    ("scanner_verbose_v1", 2854, 86, "PASS", "PASS", 0,
     "NOT APPLICABLE", "NOT APPLICABLE"),
    ("public_types_v1", 6912, 87, "FAIL", "SEMANTIC MISMATCH", 216,
     "NOT APPLICABLE", "OBSERVE COMPLETE ORIGINAL SUITE"),
    ("substitution_v2", 5120, 88, "FAIL", "WORKER INFRASTRUCTURE FAILURE",
     "NOT MEASURED", "CampaignError", "ENCODE COMPLETE GUARDED RESULT"),
    ("shape_v2", 10240, 89, "PASS", "PASS", 0,
     "NOT APPLICABLE", "NOT APPLICABLE"),
    ("public_surface_v19", 1376, 90, "FAIL", "CANDIDATE EXECUTION FAILURE",
     "NOT MEASURED", "ProducerError", "INSTALL FIRST-PARTY GUARD"),
    ("subinterpreter_v2", 128, 187, "FAIL", "CANDIDATE EXECUTION FAILURE",
     "NOT MEASURED", "ActualSuiteFailure", "OBSERVE COMPLETE ORIGINAL SUITE"),
    ("pep688_v4", 264, 188, "FAIL", "SEMANTIC MISMATCH", 4,
     "NOT APPLICABLE", "OBSERVE COMPLETE ORIGINAL SUITE"),
    ("threaded_pattern_v1", 512, 189, "FAIL", "CANDIDATE EXECUTION FAILURE",
     "NOT MEASURED", "CampaignError", "INSTALL FIRST-PARTY GUARD"),
)

OLD_REDUCERS = b'''static PyObject *match_reduce(MatchObject *match, PyObject *ignored) {
    (void)ignored;
    VMModuleState *state=vm_type_state(Py_TYPE(match));
    if (!state) return NULL;
    if (!state->scanner_reconstructor || !state->match_type) {
        PyErr_SetString(PyExc_RuntimeError,
                        "native match reconstruction is not configured");
        return NULL;
    }
    PyObject *arguments=PyTuple_Pack(3,state->match_type,
                                     (PyObject *)&PyBaseObject_Type,Py_None);
    if (!arguments) return NULL;
    PyObject *result=PyTuple_Pack(2,state->scanner_reconstructor,arguments);
    Py_DECREF(arguments);
    return result;
}

static PyObject *match_reduce_ex(MatchObject *match, PyObject *protocol) {
    PyObject *index=PyNumber_Index(protocol);
    if (!index) return NULL;
    Py_ssize_t version=PyLong_AsSsize_t(index);
    Py_DECREF(index);
    if (version == -1 && PyErr_Occurred()) return NULL;
    if (version < 2) return match_reduce(match,NULL);
    PyErr_SetString(PyExc_TypeError,"cannot pickle 're.Match' object");
    return NULL;
}
'''
NEW_REDUCERS = b'''static PyObject *match_reduce(MatchObject *match, PyObject *ignored) {
    (void)match;
    (void)ignored;
    PyErr_SetString(PyExc_TypeError,"cannot pickle 're.Match' object");
    return NULL;
}

static PyObject *match_reduce_ex(MatchObject *match, PyObject *protocol) {
    PyObject *index=PyNumber_Index(protocol);
    if (!index) return NULL;
    Py_ssize_t version=PyLong_AsSsize_t(index);
    Py_DECREF(index);
    if (version == -1 && PyErr_Occurred()) return NULL;
    (void)version;
    return match_reduce(match,NULL);
}
'''
COPY_ANCHOR = (
    b"static PyObject *match_copy(MatchObject *match, PyObject *ignored) "
    b"{ (void)ignored; return Py_NewRef(match); }\n"
    b"static PyObject *match_deepcopy(MatchObject *match, PyObject *memo) "
    b"{ (void)memo; return Py_NewRef(match); }\n"
)
CAPTURE_ANCHOR = b'''static PyObject *subject_capture_slice(const Subject *subject,
                                       Py_ssize_t begin,
                                       Py_ssize_t end) {
    if (!subject->has_view) return subject_slice(subject,begin,end);

    Subject capture;
    if (!subject_init(&capture,subject->obj)) return NULL;
    PyObject *result=subject_slice(&capture,begin,end);
    subject_clear(&capture);
    return result;
}
'''
SUBJECT_FAILURE_ANCHOR = b'''    if (PyObject_GetBuffer(string,&subject->view,PyBUF_SIMPLE)<0) {
        PyErr_Clear();
        PyErr_Format(PyExc_TypeError,
                     "expected string or bytes-like object, got '%.80s'",
                     Py_TYPE(string)->tp_name);
        return 0;
    }
'''
FORBIDDEN_C = (
    b'PyImport_ImportModule("re")',
    b'PyImport_ImportModule("_sre")',
    b'PyImport_ImportModule("regex")',
    b'PyImport_ImportModule("re2")',
    b"#include <regex.h>",
    b"#include <pcre",
    b"pcre2_",
    b"onig_",
    b"PyRun_String(",
    b"PyRun_SimpleString(",
    b"system(",
)


class SourceError(Exception):
    """An exact frozen owner, source wall, or semantic proof failed."""


def need(condition: object, reason: str) -> None:
    if not condition:
        raise SourceError(reason)


def exact_digest(value: object, role: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(item in "0123456789abcdef" for item in value),
         "require an independently pinned SHA-256: " + role)
    return value


def clean_runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and os.path.abspath(sys.executable) == PYTHON
         and sys.flags.isolated == 1 and sys.flags.no_site == 1
         and sys.dont_write_bytecode is True,
         "require pinned CPython 3.14.6 -I -B -S")
    need("re" not in sys.modules and "_sre" not in sys.modules
         and "ctypes" not in sys.modules
         and not any(name == "candidates" or name.startswith("candidates.")
                     for name in sys.modules),
         "reject a preloaded candidate, regex engine, native loader, or fallback")


def read_bootstrap(owner: tuple) -> bytes:
    relative, fingerprint, count, inode = owner
    need(type(relative) is str and not relative.startswith("/")
         and ".." not in relative.split("/")
         and "holdout" not in relative.lower()
         and "benchmark" not in relative.lower()
         and not relative.endswith((".so", ".gz", ".zip", ".tar", ".xz"))
         and type(count) is int and 0 < count <= MAX_OWNER
         and type(inode) is int and inode > 0,
         "reject a candidate, archive, private root, or unbounded source owner")
    exact_digest(fingerprint, relative)
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
             and before.st_ino == inode and before.st_size == count
             and before.st_uid == os.geteuid() and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o600,
             "reject a substituted first-party source owner: " + relative)
        parts = []
        remaining = count
        while remaining:
            block = os.read(descriptor, min(remaining, 262144))
            need(bool(block), "reject a truncated source owner: " + relative)
            parts.append(block)
            remaining -= len(block)
        need(not os.read(descriptor, 1),
             "reject trailing source-owner bytes: " + relative)
        payload = b"".join(parts)
        after = os.fstat(descriptor)
        need(hashlib.sha256(payload).hexdigest() == fingerprint
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject a changed complete source owner: " + relative)
        return payload
    finally:
        os.close(descriptor)


def bootstrap_wall() -> tuple[types.ModuleType, tuple]:
    clean_runtime()
    raw = read_bootstrap(V6[0])
    legacy = types.ModuleType("_rebar_c_match_semantics_frozen_source_wall_v6")
    legacy.__file__ = ROOT + "/" + V6[0][0]
    legacy.__package__ = ""
    exec(compile(raw, legacy.__file__, "exec", dont_inherit=True),
         legacy.__dict__)
    need(legacy.SCHEMA == "rebar-owned-repaired-c-original-campaign-v6"
         and legacy.ORIGINAL_CASE_COUNT == ORIGINAL_CASE_COUNT
         and legacy.SEPARATE_REFERENCE_CASE_COUNT == REFERENCE_CASE_COUNT
         and legacy.EXPANDED_PROPOSED_CASE_COUNT == PROPOSED_HOLDOUT_CASE_COUNT
         and tuple((name, count) for name, count in legacy.SUITES)
         == tuple((row[0], row[1]) for row in EXPECTED_ROWS),
         "reject the independently frozen matcher-free C V6 source wall")
    legacy.SOURCE, legacy.PROTOCOL, legacy.CONTRACT = SOURCE, PROTOCOL, CONTRACT
    old = legacy.bootstrap_previous()
    static_owners = (
        (old.GOAL,) + old.P0 + old.PRODUCER + old.GUARD
        + legacy.OLD + (legacy.V1_MANIFEST, legacy.CORRECTED_SOURCE)
        + V6 + V7 + (ACTUAL_FAILURE,) + SUITE_SOURCES
    )
    paths = tuple(owner[0] for owner in static_owners)
    need(len(paths) == len(frozenset(paths)),
         "reject duplicate or shadowed frozen source-owner paths")
    old.STATIC_OWNERS = static_owners
    old.OWNED_PATHS = frozenset(paths) | {SOURCE, PROTOCOL, CONTRACT}
    need(not any("holdout" in path.lower() or "benchmark" in path.lower()
                 or path.endswith((".so", ".gz", ".zip", ".tar", ".xz"))
                 or path == "candidates/_vm_native.c"
                 or path == "candidates/vm_candidate.py"
                 or path.startswith("docs/evidence/")
                 for path in old.OWNED_PATHS),
         "the physical source wall must exclude live candidates, graphs, "
         "holdouts, archives, native extensions, and private roots")
    clean_runtime()
    return old, static_owners


def document(producer: types.ModuleType, raw: bytes, role: str) -> dict:
    try:
        value = producer.JsonReader(raw).parse()
    except Exception as error:
        raise SourceError("reject malformed source-only " + role + ": "
                          + str(error)) from error
    need(type(value) is dict, "require an exact machine document: " + role)
    return value


def record(owner: tuple) -> dict:
    return {"path": owner[0], "sha256": owner[1], "bytes": owner[2],
            "device": DEVICE, "inode": owner[3], "mode": "0600", "nlink": 1}


def validate_receipt(value: dict) -> dict:
    need(value.get("schema")
         == "rebar-owned-repaired-c-original-campaign-v7-durable-publication-receipt"
         and value.get("version") == 7 and value.get("family") == "c"
         and value.get("label")
         == "phase2-v18-c-subject-buffer-root-provenance-original-p0-v7"
         and value.get("status") == "PASS"
         and value.get("publication_status") == "PASS"
         and value.get("publication_pass_means")
         == "DURABLE CORRECTNESS PUBLICATION ONLY"
         and value.get("candidate_status") == "FAIL"
         and value.get("candidate_qualified") is False
         and value.get("source_sha256") == V7[0][1]
         and value.get("protocol_sha256") == V7[1][1]
         and value.get("contract_sha256") == V7[2][1]
         and value.get("corrected_source_sha256")
         == "8131aea768a122308716b8a67903794aa03f2fed2e2022f53bb6aa7b7e10e962"
         and value.get("actual_c18_build_receipt_sha256")
         == "4070feca7129fdcf3dc9762fae853649c68c722940af6157ecdcfa59d23e65ae"
         and value.get("actual_c18_root_receipt_sha256")
         == "a231eec31b29ca796c75cee03b702a3e35a9195e74675c8f56209419dfeb03c8"
         and value.get("native_engine_sha256")
         == "f3794f963819a9af3798c1d97f32edcbc2a117f9ed20c56ec554a605de82eeae"
         and value.get("native_bridge_sha256")
         == "f3794f963819a9af3798c1d97f32edcbc2a117f9ed20c56ec554a605de82eeae"
         and value.get("suite_count") == len(EXPECTED_ROWS)
         and value.get("attempted_suite_count") == len(EXPECTED_ROWS)
         and value.get("completed_suite_count") == 5
         and value.get("case_execution_denominator") == ORIGINAL_CASE_COUNT
         and value.get("separate_reference_case_count") == REFERENCE_CASE_COUNT
         and value.get("separate_reference_cases_counted_as_candidate_cases")
         is False and value.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
         and value.get("observed_semantic_mismatch_lower_bound") == 236
         and value.get("semantic_mismatch_count") == "NOT MEASURED"
         and value.get("verified_passing_case_count") == 13094
         and value.get("infrastructure_failure_count") == 1
         and value.get("candidate_execution_failure_count") == 7
         and value.get("actual_candidate_workers") == len(EXPECTED_ROWS)
         and value.get("actual_worker_process_ids_are_distinct") is True
         and value.get("original_native_inode_restored") is True
         and value.get("worker_timeout_count") == 0
         and value.get("original_source_targets_modified") == 0
         and value.get("hidden_cases_read") == 0
         and value.get("benchmark_files_read") == 0
         and value.get("clock_samples") == 0
         and value.get("timing_trials_run") == 0
         and value.get("expanded_holdout_proposed_case_count")
         == PROPOSED_HOLDOUT_CASE_COUNT
         and value.get("holdout") == "NOT OPENED"
         and value.get("performance") == "NOT MEASURED"
         and value.get("memory") == "NOT MEASURED"
         and value.get("winner_selected") is False,
         "reject the actual C V7 failure, denominator, publication scope, "
         "distinct workers, exact source provenance, or measurement boundary")
    rows = value.get("suite_outcomes")
    need(type(rows) is list and len(rows) == len(EXPECTED_ROWS),
         "require all 13 actual, source-ordered original suite outcomes")
    pids = []
    observed_lower_bound = 0
    passing_cases = 0
    completed = 0
    execution = 0
    infrastructure = 0
    for actual, expected in zip(rows, EXPECTED_ROWS, strict=True):
        name, count, pid, status, failure, mismatches, error, phase = expected
        need(type(actual) is dict and actual.get("suite") == name
             and actual.get("case_execution_denominator") == count
             and actual.get("worker_process_id") == pid
             and actual.get("actual_candidate_workers") == 1
             and actual.get("status") == status
             and actual.get("failure_class") == failure
             and actual.get("mismatch_count") == mismatches
             and actual.get("error_type") == error
             and actual.get("failure_phase") == phase,
             "reject an omitted, reordered, reclassified, or invented actual "
             "C V7 outcome: " + name)
        pids.append(pid)
        if type(mismatches) is int:
            completed += 1
            observed_lower_bound += mismatches
            if status == "PASS":
                passing_cases += count
        execution += failure == "CANDIDATE EXECUTION FAILURE"
        infrastructure += failure == "WORKER INFRASTRUCTURE FAILURE"
    need(sum(row[1] for row in EXPECTED_ROWS) == ORIGINAL_CASE_COUNT
         and pids == value.get("actual_worker_process_ids")
         and len(pids) == len(set(pids))
         and observed_lower_bound == 236 and passing_cases == 13094
         and completed == 5 and execution == 7 and infrastructure == 1,
         "reject false C V7 totals, duplicate worker identities, or denominator")
    by_name = {row["suite"]: row for row in rows}
    need("unpaired JSON high surrogate"
         in by_name["substitution_v2"].get("plain_failure_diagnostic", "")
         and "_NormalizedEnvelope"
         in by_name["public_surface_v19"].get("plain_failure_diagnostic", "")
         and "complete digest does not match observation"
         in by_name["threaded_pattern_v1"].get("plain_failure_diagnostic", ""),
         "preserve the three actually reported result-transport failures")
    return value


def validate_suite_sources(raw: dict) -> None:
    public = raw[SUITE_SOURCES[1][0]]
    substitution = raw[SUITE_SOURCES[3][0]]
    surface = raw[SUITE_SOURCES[4][0]]
    threaded = raw[SUITE_SOURCES[5][0]]
    producer = raw["tools/run_owned_six_family_original_p0_producer_v5.py"]
    campaign = raw[V7[0][0]]
    need(b"PICKLE_PROTOCOLS = (0, 1, 2, 3, 4, 5)" in public
         and b'cohort == "pickle-match-rejection"' in public
         and b"pickle_module.dumps(match, protocol=protocol)" in public,
         "require the unchanged original six-protocol Match rejection oracle")
    need(b"preserve-exact-nested-buffer-flags-0-0-284" in substitution
         and b"preserve-exact-nested-lifo-acquisition-release" in substitution
         and b"released-subject-memoryview-type-error" in substitution
         and b"text-lone-surrogate" in substitution,
         "preserve exact nested PEP-688 flags, LIFO, released-view behavior, "
         "and original lone-surrogate cases")
    need(b"class _NormalizedEnvelope(dict):" in surface
         and b"_AUTHENTIC_NORMALIZED_ENVELOPES" in surface
         and b"_AUTHENTIC_NORMALIZED_ENVELOPES.get(id(current))" in surface
         and b" is current" in surface,
         "require factory-authenticated envelope identity, not a dict subclass")
    need(b"def canonical(value:" in threaded
         and b').encode("ascii")' in threaded
         and b'ensure_ascii=True, allow_nan=False' in threaded
         and b"def canonical_vector(" in campaign
         and b"def protected_worker(" in campaign
         and b'"INSTALL FIRST-PARTY GUARD"' in campaign,
         "preserve authentic no-newline threaded digest framing and diagnose "
         "the exact reporting-stage misclassification")
    need(b"class JsonReader:" in producer
         and b"reject unpaired JSON high surrogate" in producer
         and b'character.encode("utf-16-be", "surrogatepass")' in producer
         and b"if type(item) is dict:" in producer,
         "preserve the actual first-party transport, strict decoder, and "
         "exact-dict normalization evidence")


def derive_variant(base: bytes, expected_sha: str) -> bytes:
    need(type(base) is bytes
         and hashlib.sha256(base).hexdigest() == expected_sha
         and expected_sha
         == "8131aea768a122308716b8a67903794aa03f2fed2e2022f53bb6aa7b7e10e962"
         and len(base) == 222212,
         "require the independently frozen complete first-party C source")
    need(base.count(OLD_REDUCERS) == 1 and NEW_REDUCERS not in base,
         "require exactly one unchanged original Match reduction block")
    need(base.count(COPY_ANCHOR) == 1
         and base.count(CAPTURE_ANCHOR) == 1
         and base.count(SUBJECT_FAILURE_ANCHOR) == 1,
         "require exact frozen copy, deepcopy, nested acquisition, and "
         "released-buffer behavior before deriving any correction")
    position = base.index(OLD_REDUCERS)
    derived = (base[:position] + NEW_REDUCERS
               + base[position + len(OLD_REDUCERS):])
    need(derived != base and derived.count(NEW_REDUCERS) == 1
         and OLD_REDUCERS not in derived
         and derived[:position] == base[:position]
         and derived[position + len(NEW_REDUCERS):]
         == base[position + len(OLD_REDUCERS):]
         and derived.count(COPY_ANCHOR) == 1
         and derived.count(CAPTURE_ANCHOR) == 1
         and derived.count(SUBJECT_FAILURE_ANCHOR) == 1
         and b"if (version < 2) return match_reduce(match,NULL);" not in derived
         and NEW_REDUCERS.count(b"PyNumber_Index(protocol)") == 1
         and NEW_REDUCERS.count(b"PyLong_AsSsize_t(index)") == 1
         and NEW_REDUCERS.count(
             b'PyErr_SetString(PyExc_TypeError,"cannot pickle \'re.Match\' object");'
         ) == 1
         and NEW_REDUCERS.count(b"return match_reduce(match,NULL);") == 1,
         "derive exactly one all-protocol Match rejection while preserving "
         "protocol validation, copy identity, and all buffer source bytes")
    for token in FORBIDDEN_C:
        need(token not in base and token not in derived,
             "reject C delegation, external engine, interpreter fallback, "
             "or process execution: " + token.decode("ascii"))
    return derived


def validate_context(old: types.ModuleType, raw: dict,
                     producer: types.ModuleType) -> tuple[dict, bytes]:
    p0 = document(producer, raw[old.P0[2][0]], "frozen complete original P0")
    producer.validate_p0(p0)
    guard = document(producer, raw[old.GUARD[2][0]], "frozen first-party guard")
    producer.validate_runtime_guard_v2(guard)
    original = document(producer, raw[old.PRODUCER[2][0]],
                        "frozen original-suite producer")
    need(original.get("schema")
         == "rebar-owned-six-family-original-p0-producer-v5-source-freeze"
         and original.get("version") == 5
         and original.get("case_execution_denominator") == ORIGINAL_CASE_COUNT
         and original.get("suite_count") == len(EXPECTED_ROWS)
         and original.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
         and original.get("family_count") == 6
         and original.get("supplemental_case_count") == REFERENCE_CASE_COUNT
         and original.get("supplemental_cases_counted_in_original_denominator")
         is False and original.get("qualified_candidate_count") == 0
         and original.get("holdout") == "NOT OPENED",
         "reject or weaken the original 31,237-case six-family producer")
    original_suites = original.get("suites")
    need(type(original_suites) is list
         and len(original_suites) == len(EXPECTED_ROWS),
         "require all 13 frozen source-ordered original suites")
    for observed, expected in zip(original_suites, EXPECTED_ROWS, strict=True):
        need(type(observed) is dict and observed.get("id") == expected[0]
             and observed.get("case_execution_count") == expected[1],
             "reject an altered frozen original suite: " + expected[0])
    manifest = document(producer,
                        raw["oracle/phase1/p0-completeness-v1.json"],
                        "original source-owned suite manifest")
    denominator = manifest.get("denominator")
    need(manifest.get("schema") == "rebar-cpython-re-p0-completeness-v1"
         and manifest.get("version") == 1
         and type(denominator) is dict
         and denominator.get("final_required_case_execution_denominator")
         == ORIGINAL_CASE_COUNT
         and denominator.get("counted_suite_ids")
         == [item[0] for item in EXPECTED_ROWS],
         "preserve the exact source-owned P0 case identities and denominator")
    v6 = document(producer, raw[V6[2][0]], "immutable C V6 source freeze")
    v7 = document(producer, raw[V7[2][0]], "immutable C V7 source freeze")
    need(v6.get("schema")
         == "rebar-owned-repaired-c-original-campaign-v6-source-freeze"
         and v6.get("version") == 6
         and v6.get("source", {}).get("sha256") == V6[0][1]
         and v6.get("protocol", {}).get("sha256") == V6[1][1]
         and v6.get("performance") == "NOT MEASURED"
         and v6.get("qualified_candidate_count") == 0,
         "preserve immutable C V6 without inspecting a live candidate")
    need(v7.get("schema")
         == "rebar-owned-repaired-c-original-campaign-v7-source-freeze"
         and v7.get("version") == 7
         and v7.get("source", {}).get("sha256") == V7[0][1]
         and v7.get("protocol", {}).get("sha256") == V7[1][1]
         and v7.get("performance") == "NOT MEASURED"
         and v7.get("qualified_candidate_count") == 0,
         "preserve immutable C V7 without inspecting a live candidate")
    receipt = validate_receipt(
        document(producer, raw[ACTUAL_FAILURE[0]], "actual C V7 small receipt")
    )
    validate_suite_sources(raw)
    base = raw["candidates/c/variants/subject_buffer_ownership_v1/vm_native.c"]
    derived = derive_variant(base, receipt["corrected_source_sha256"])
    clean_runtime()
    return receipt, derived


def contract_document(old: types.ModuleType, receipt: dict, derived: bytes,
                      owners: tuple, source_sha: str, protocol_sha: str) -> dict:
    outcomes = []
    for row in receipt["suite_outcomes"]:
        outcomes.append({
            "suite": row["suite"],
            "case_execution_denominator": row["case_execution_denominator"],
            "worker_process_id": row["worker_process_id"],
            "status": row["status"],
            "failure_class": row["failure_class"],
            "mismatch_count": row["mismatch_count"],
            "error_type": row["error_type"],
            "reported_failure_phase": row["failure_phase"],
        })
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": 1,
        "phase": "PHASE 2: CANDIDATES",
        "status": "SOURCE FROZEN; DERIVED C SEMANTIC VARIANT NOT "
                  "MATERIALIZED, BUILT, OR RUN",
        "status_scope": "ONE FIRST-PARTY C SOURCE CORRECTION ONLY; "
                        "NOT A CANDIDATE CORRECTNESS RESULT",
        "family": "c",
        "label": LABEL,
        "goal_sha256": old.GOAL[1],
        "source": {"path": SOURCE, "sha256": source_sha},
        "protocol": {"path": PROTOCOL, "sha256": protocol_sha},
        "pinned_cpython": {
            "path": PYTHON, "version": "3.14.6",
            "required_flags": ["-I", "-B", "-S"],
        },
        "phase_one": {
            "status": "PASS",
            "original_case_execution_denominator": ORIGINAL_CASE_COUNT,
            "original_suite_count": len(EXPECTED_ROWS),
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "separate_reference_case_count": REFERENCE_CASE_COUNT,
            "separate_reference_cases_counted_in_original_denominator": False,
            "owners": [record(item) for item in old.P0],
            "original_manifest": record(
                next(item for item in owners
                     if item[0] == "oracle/phase1/p0-completeness-v1.json")
            ),
        },
        "original_producer": {
            "version": 5,
            "case_execution_denominator": ORIGINAL_CASE_COUNT,
            "suite_count": len(EXPECTED_ROWS),
            "family_count": 6,
            "owners": [record(item) for item in old.PRODUCER],
        },
        "first_party_runtime_guard": {
            "version": 2,
            "owners": [record(item) for item in old.GUARD],
            "candidate_imported": False,
            "runtime_guard_installed": False,
            "runtime_non_delegation": "NOT ESTABLISHED; CANDIDATE NOT RUN",
            "standard_library_re": "FORBIDDEN",
            "cpython_sre_engine": "FORBIDDEN",
            "external_regex_package": "FORBIDDEN",
            "another_candidate": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
        },
        "immutable_previous_source_freezes": {
            "c_v6": [record(item) for item in V6],
            "c_v7": [record(item) for item in V7],
        },
        "actual_previous_c_result": {
            "receipt": record(ACTUAL_FAILURE),
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE CORRECTNESS PUBLICATION ONLY",
            "candidate_status": "FAIL",
            "candidate_qualified": False,
            "attempted_suite_count": 13,
            "completed_suite_count": 5,
            "case_execution_denominator": ORIGINAL_CASE_COUNT,
            "actual_candidate_workers": 13,
            "actual_worker_process_ids": receipt["actual_worker_process_ids"],
            "actual_worker_process_ids_are_distinct": True,
            "verified_passing_case_count": 13094,
            "passing_suites": [
                {"suite": "scanner_verbose_v1", "case_execution_count": 2854},
                {"suite": "shape_v2", "case_execution_count": 10240},
            ],
            "observed_semantic_mismatch_lower_bound": 236,
            "semantic_mismatch_count": "NOT MEASURED",
            "observed_semantic_mismatch_suites": [
                {"suite": "managed_v1", "observed_mismatch_count": 16},
                {"suite": "public_types_v1", "observed_mismatch_count": 216},
                {"suite": "pep688_v4", "observed_mismatch_count": 4},
            ],
            "infrastructure_failure_count": 1,
            "candidate_execution_failure_count": 7,
            "worker_timeout_count": 0,
            "original_native_inode_restored": True,
            "suite_outcomes": outcomes,
        },
        "source_correction": {
            "id": "match-pickle-rejection-all-protocols",
            "status": "EXACT C SOURCE TRANSFORMATION PROVED; "
                      "DERIVED C FILE NOT MATERIALIZED",
            "original_variant": record(
                next(item for item in owners if item[0]
                     == "candidates/c/variants/subject_buffer_ownership_v1/"
                        "vm_native.c")
            ),
            "derived_variant_sha256": hashlib.sha256(derived).hexdigest(),
            "derived_variant_bytes": len(derived),
            "prospective_variant_path":
                "candidates/c/variants/original_match_semantics_v1/vm_native.c",
            "derived_variant_materialized": False,
            "derived_variant_built": False,
            "derived_variant_run": False,
            "exact_changed_block_count": 1,
            "original_reducer_sha256": hashlib.sha256(OLD_REDUCERS).hexdigest(),
            "corrected_reducer_sha256": hashlib.sha256(NEW_REDUCERS).hexdigest(),
            "pickle_protocols": [0, 1, 2, 3, 4, 5],
            "all_protocols_raise_original_match_type_error":
                "SOURCE STRUCTURE ONLY; ACTUAL CANDIDATE NOT RUN",
            "numeric_protocol_validation_preserved": True,
            "match_copy_identity_source_preserved": True,
            "match_deepcopy_identity_source_preserved": True,
            "subject_capture_slice_source_preserved": True,
            "subject_init_failure_source_preserved": True,
            "nested_exporter_acquisition_flags_preserved": [0, 0, 284],
            "nested_exporter_release_order_preserved": "LIFO",
            "managed_buffer_mismatches_repaired": "NOT MEASURED",
            "pep688_buffer_mismatches_repaired": "NOT MEASURED",
            "public_type_mismatch_reduction": "NOT MEASURED",
            "total_mismatch_reduction": "NOT MEASURED",
            "public_type_failures_attributable_to_pickling": "NOT MEASURED",
            "candidate_correctness": "NOT MEASURED",
        },
        "independently_frozen_suite_source_owners": [
            record(item) for item in SUITE_SOURCES
        ],
        "distinct_historical_result_transport_defects": [
            {
                "id": "substitution-lone-surrogate-report-transport",
                "suite": "substitution_v2",
                "actual_failure_class": "WORKER INFRASTRUCTURE FAILURE",
                "actual_reported_stage": "ENCODE COMPLETE GUARDED RESULT",
                "evidence": "V5 canonical encoding emits a lone surrogate "
                            "that its own strict JSON reader rejects",
                "future_report_boundary": "round-trip a distinctly tagged "
                                          "UTF-16 code unit; retain every "
                                          "original test and strict reader",
                "candidate_matcher_mismatch": "NOT ESTABLISHED",
                "fixed_by_this_source_freeze": False,
            },
            {
                "id": "public-envelope-report-identity",
                "suite": "public_surface_v19",
                "actual_failure_class": "CANDIDATE EXECUTION FAILURE",
                "actual_reported_stage": "INSTALL FIRST-PARTY GUARD",
                "actual_failure_evidence": "_NormalizedEnvelope",
                "reported_stage_is_accurate": False,
                "future_report_boundary": "accept only exact "
                    "factory-authenticated _NormalizedEnvelope identity; "
                    "never trust an arbitrary dict subclass",
                "candidate_matcher_mismatch": "NOT ESTABLISHED",
                "fixed_by_this_source_freeze": False,
            },
            {
                "id": "threaded-report-digest-framing",
                "suite": "threaded_pattern_v1",
                "actual_failure_class": "CANDIDATE EXECUTION FAILURE",
                "actual_reported_stage": "INSTALL FIRST-PARTY GUARD",
                "reported_stage_is_accurate": False,
                "future_report_boundary": "preserve the original "
                    "no-trailing-newline threaded-vector digest framing",
                "candidate_matcher_mismatch": "NOT ESTABLISHED",
                "fixed_by_this_source_freeze": False,
            },
        ],
        "source_only_effects": {
            "actual_candidate_imports": 0,
            "actual_candidate_workers": 0,
            "actual_reference_workers": 0,
            "actual_native_libraries_loaded": 0,
            "actual_compiler_processes": 0,
            "actual_archives_opened": 0,
            "actual_private_roots_opened": 0,
            "actual_graph_owners_opened": 0,
            "actual_canonical_candidate_owners_opened": 0,
            "actual_guard_installations": 0,
            "actual_holdout_cases_read": 0,
            "actual_benchmark_files_read": 0,
            "actual_clock_samples": 0,
            "actual_network_requests": 0,
            "actual_workspace_mutations": 0,
        },
        "expanded_holdout": {
            "proposed_case_count": PROPOSED_HOLDOUT_CASE_COUNT,
            "case_status": "NOT GENERATED; NOT OPENED",
            "proposal_owner_opened": False,
            "final_protocol_status": "NOT FROZEN",
            "holdout_opened": False,
        },
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualification": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def reject_control(label: str, action: object) -> str:
    try:
        action()
    except Exception as error:
        need(type(error).__name__ in
             ("SourceError", "CampaignError", "ProducerError"),
             "unexpected source-only hostile control exception: " + label)
        return label
    raise SourceError("accepted a forbidden semantic-source control: " + label)


def semantic_controls(old: types.ModuleType, wall: object,
                      producer: types.ModuleType, receipt: dict,
                      base: bytes) -> list:
    controls = list(old.hostile_controls(wall))
    no_newline = b"[1,2,3]"
    need(hashlib.sha256(no_newline).hexdigest()
         != hashlib.sha256(no_newline + b"\n").hexdigest(),
         "distinguish authentic no-newline threaded digest framing")
    surrogate = "\ud800"
    tagged = {"encoding": "utf16-code-unit-surrogatepass",
              "hex": ord(surrogate).to_bytes(2, "big").hex()}
    roundtrip = document(producer, producer.canonical(tagged),
                         "synthetic tagged lone-surrogate transport")
    need(roundtrip == tagged
         and chr(int.from_bytes(bytes.fromhex(roundtrip["hex"]), "big"))
         == surrogate,
         "require exact source-only synthetic lone-surrogate report round-trip")
    need(tuple((item[0], item[1]) for item in EXPECTED_ROWS)
         == tuple((name, count) for name, count, _ in old.SUITES),
         "preserve every source-owned original suite and its case denominator")

    def mutated_receipt(**changes: object) -> None:
        altered = dict(receipt)
        altered.update(changes)
        validate_receipt(altered)

    def duplicate_worker() -> None:
        altered = dict(receipt)
        rows = [dict(item) for item in receipt["suite_outcomes"]]
        rows[1]["worker_process_id"] = rows[0]["worker_process_id"]
        altered["suite_outcomes"] = rows
        validate_receipt(altered)

    def changed_reducer() -> None:
        derive_variant(base.replace(OLD_REDUCERS, NEW_REDUCERS, 1),
                       hashlib.sha256(base).hexdigest())

    def changed_capture() -> None:
        derive_variant(base.replace(CAPTURE_ANCHOR,
                                    CAPTURE_ANCHOR.replace(
                                        b"subject_clear(&capture);\n", b"", 1),
                                    1), hashlib.sha256(base).hexdigest())

    def changed_subject_failure() -> None:
        derive_variant(base.replace(SUBJECT_FAILURE_ANCHOR,
                                    SUBJECT_FAILURE_ANCHOR.replace(
                                        b"        PyErr_Clear();\n", b"", 1),
                                    1), hashlib.sha256(base).hexdigest())

    def changed_copy() -> None:
        derive_variant(base.replace(COPY_ANCHOR,
                                    COPY_ANCHOR.replace(
                                        b"return Py_NewRef(match);",
                                        b"return Py_NewRef(Py_None);", 1),
                                    1), hashlib.sha256(base).hexdigest())

    extras = (
        ("reject strict lone-surrogate report decoding",
         lambda: producer.JsonReader(b'{"value":"\\ud800"}').parse()),
        ("reject modified original Match reducers", changed_reducer),
        ("reject modified nested subject acquisition", changed_capture),
        ("reject modified released-subject TypeError", changed_subject_failure),
        ("reject modified original Match copy identity", changed_copy),
        ("reject a forged completed suite count",
         lambda: mutated_receipt(completed_suite_count=13)),
        ("reject a forged exact semantic mismatch total",
         lambda: mutated_receipt(semantic_mismatch_count=236)),
        ("reject a falsely successful historical candidate",
         lambda: mutated_receipt(candidate_status="PASS")),
        ("reject a replaced case-execution denominator",
         lambda: mutated_receipt(case_execution_denominator=31236)),
        ("reject duplicate actual original worker identities", duplicate_worker),
        ("reject a falsely opened historical holdout",
         lambda: mutated_receipt(holdout="OPENED")),
        ("reject a falsely measured historical speedup",
         lambda: mutated_receipt(performance="FASTER")),
        ("reject an external regex candidate import",
         lambda: builtins.__import__("regex")),
        ("reject direct CPython regex engine import",
         lambda: builtins.__import__("_sre")),
        ("reject live canonical C source access",
         lambda: os.open(ROOT + "/candidates/_vm_native.c",
                         os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("reject installed native extension access",
         lambda: os.open(
             ROOT + "/candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
             os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("reject the actual C failure archive without opening it",
         lambda: os.open(ROOT + "/oracle/phase2/evidence/"
                         "repaired-c-original-campaign-v7-c-phase2-v18-"
                         "c-subject-buffer-root-provenance-original-p0-v7-"
                         "failures.json.gz",
                         os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("reject candidate build or worker processes",
         lambda: os.system("false")),
        ("reject a proposed holdout owner",
         lambda: os.open(
             ROOT + "/oracle/phase3/expanded-sealed-holdout-v1.json",
             os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("reject a clock or performance observation", lambda: os.times()),
    )
    controls.extend(reject_control(label, action)
                    for label, action in extras)
    need(len(controls) >= 50 and len(wall.blocked) >= 10
         and sum(wall.blocked.values()) >= 30,
         "require complete physically denied engine, native, graph, archive, "
         "holdout, process, clock, and altered-semantics controls")
    clean_runtime()
    return controls


def parse_options(arguments: list) -> dict:
    modes = ("--render-contract", "--self-test", "--verify-frozen-context",
             "--render-variant")
    need(bool(arguments) and arguments[0] in modes,
         "only explicitly pinned source-only render, self-test, or verification "
         "is authorized; build, run, workers, recovery, and activation are denied")
    options = {"mode": arguments[0]}
    allowed = ("--source-sha256", "--protocol-sha256", "--contract-sha256")
    index = 1
    while index < len(arguments):
        key = arguments[index]
        need(key in allowed and key not in options
             and index + 1 < len(arguments),
             "reject unpinned, duplicate, native, candidate, root, or worker arguments")
        options[key] = exact_digest(arguments[index + 1], key)
        index += 2
    need("--source-sha256" in options and "--protocol-sha256" in options,
         "independently pin the exact source and readable protocol")
    if options["mode"] == "--render-contract":
        need("--contract-sha256" not in options,
             "initial contract rendering must not invent a machine-owner pin")
    else:
        need("--contract-sha256" in options,
             "independently pin the exact complete machine contract")
    return options


def source_operation(options: dict) -> tuple[bytes, dict]:
    old, owners = bootstrap_wall()
    with old.SourceWall() as wall:
        own_source = old.read_dynamic(SOURCE, options["--source-sha256"])
        protocol = old.read_dynamic(PROTOCOL, options["--protocol-sha256"])
        need(hashlib.sha256(own_source).hexdigest()
             == options["--source-sha256"]
             and hashlib.sha256(protocol).hexdigest()
             == options["--protocol-sha256"],
             "reject substituted semantic source or protocol")
        parsed_ast = ast.parse(own_source, filename=SOURCE)
        import_names = []
        for node in parsed_ast.body:
            if isinstance(node, ast.Import):
                import_names.extend(item.name for item in node.names)
            if isinstance(node, ast.ImportFrom) and node.module != "__future__":
                raise SourceError("reject top-level semantic source dependency")
        need(tuple(import_names)
             == ("ast", "builtins", "hashlib", "os", "stat", "sys", "types"),
             "require exclusively matcher-free semantic-source imports")
        raw = {owner[0]: old.read_owner(owner) for owner in owners}
        producer = old.load_producer(raw[old.PRODUCER[0][0]])
        receipt, derived = validate_context(old, raw, producer)
        expected = contract_document(old, receipt, derived, owners,
                                     options["--source-sha256"],
                                     options["--protocol-sha256"])
        if options["mode"] != "--render-contract":
            contract_raw = old.read_dynamic(CONTRACT,
                                            options["--contract-sha256"])
            actual = document(producer, contract_raw,
                              "independently frozen Match-semantic contract")
            need(producer.canonical(actual) == contract_raw
                 and actual == expected,
                 "reject a changed, noncanonical, misattributed, or "
                 "falsely qualifying Match-semantic machine contract")
        controls = semantic_controls(
            old, wall, producer, receipt,
            raw["candidates/c/variants/subject_buffer_ownership_v1/vm_native.c"],
        )
        effects = expected["source_only_effects"]
        need(all(type(count) is int and count == 0
                 for count in effects.values()),
             "a semantic source mode must have exactly zero candidate effects")
        observed = {
            "schema": SCHEMA + (
                "-self-test" if options["mode"] == "--self-test"
                else "-frozen-context"
            ),
            "status": "PASS",
            "source_sha256": options["--source-sha256"],
            "protocol_sha256": options["--protocol-sha256"],
            "contract_sha256": options.get("--contract-sha256"),
            "authenticated_source_owner_count": len(owners),
            "original_case_execution_denominator": ORIGINAL_CASE_COUNT,
            "original_suite_count": len(EXPECTED_ROWS),
            "separate_reference_case_count": REFERENCE_CASE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "actual_previous_candidate_status": "FAIL",
            "actual_previous_observed_semantic_mismatch_lower_bound": 236,
            "actual_previous_semantic_mismatch_count": "NOT MEASURED",
            "actual_previous_completed_suite_count": 5,
            "actual_previous_actual_candidate_workers": 13,
            "historical_report_transport_defect_count": 3,
            "corrected_match_pickle_protocols": [0, 1, 2, 3, 4, 5],
            "source_semantic_change_count": 1,
            "derived_variant_sha256": hashlib.sha256(derived).hexdigest(),
            "derived_variant_materialized": False,
            "candidate_correctness": "NOT MEASURED",
            "hostile_controls": len(controls),
            "blocked_physical_operations": sum(wall.blocked.values()),
            "effects": effects,
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
        if options["mode"] == "--render-contract":
            return producer.canonical(expected), observed
        if options["mode"] == "--render-variant":
            return derived, observed
        return producer.canonical(observed), observed


def main() -> int:
    try:
        clean_runtime()
        options = parse_options(sys.argv[1:])
        output, _ = source_operation(options)
        sys.stdout.buffer.write(output)
        sys.stdout.buffer.flush()
        clean_runtime()
        return 0
    except Exception as error:
        sys.stderr.write("C original Match semantics V1: FAIL: "
                         + type(error).__name__ + ": " + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
