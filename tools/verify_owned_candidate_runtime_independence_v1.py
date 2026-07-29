#!/usr/bin/env python3
"""Freeze and self-test a sterile, first-party regex-candidate runtime guard."""

from __future__ import annotations

# Keep this bootstrap free of argparse, json, inspect, unittest, pathlib and
# dataclasses. Importing any of those before the guard can import re and _sre.
import ast
import hashlib
import marshal
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
SELF = "tools/verify_owned_candidate_runtime_independence_v1.py"
PROTOCOL = "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V1.md"
CONTRACT = "oracle/phase2/candidate-runtime-independence-v1.json"
GOAL_SHA = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
MAXGROUPS = 1073741823
P0 = {
    "source": ("tools/verify_owned_p0_completeness_v4.py", "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d", 29094, 428927),
    "protocol": ("oracle/phase1/P0-COMPLETENESS-V4.md", "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2", 4261, 524712),
    "contract": ("oracle/phase1/p0-completeness-v4.json", "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
}
V73 = {
    "source": ("tools/render_candidate_current_overview_v73.py", "484878fe7045f4fea8cf6e03cf99c6dce5e2216f28a1bfb9b10fb48b1d7fdead", 34407, 431239),
    "inputs": ("docs/evidence/candidate-current-overview-v73.inputs.json", "a83eb8d1eaf1dd70cc33df7e2664ccaf52dc93f508da048c2efe4c8f14901fc2", 1148124, 431240),
    "summary": ("docs/evidence/candidate-current-overview-v73.json", "5a44336584886dfe1ef97ad81e810407fe0df772437238918cc3ba1714bc7618", 3221471, 431241),
    "svg": ("docs/evidence/candidate-current-overview-v73.svg", "cdcdc323dddd4d3d5b77a5d75cd93e826c6cb6e480c5db5aab9d6555abfa5a31", 4769, 431245),
}
V19_BUILD = (
    "oracle/phase2/evidence/native-source-build-v19-rust-phase2-v19-rust-buffer-shape-root-provenance-publication-receipt.json",
    "27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc", 3486, 524773,
)
V19_ROOT = (
    "oracle/phase2/evidence/native-source-build-v19-rust-phase2-v19-rust-buffer-shape-root-provenance-root-provenance-receipt.json",
    "de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99", 4367, 524774,
)
FAMILIES = {
    "rust": "candidates.rust_candidate",
    "c": "candidates.vm_candidate",
    "zig": "candidates.zig_candidate",
    "cpp": "candidates.cpp_candidate",
    "go": "candidates.go_candidate",
    "fortran": "candidates.fortran_candidate",
}
DENIED_PREFIXES = (
    "_sre", "sre_compile", "sre_parse", "sre_constants", "regex", "re2",
    "pcre", "pcre2", "oniguruma", "onig", "hyperscan",
)
DENIED_EVENTS = (
    "subprocess.Popen", "os.system", "os.spawn", "os.exec", "socket.connect",
    "socket.bind", "socket.__new__", "ctypes.dlopen", "ctypes.dlsym",
    "urllib.Request", "http.client.connect",
)


class GuardError(Exception):
    """A pinned owner, clean bootstrap, or candidate-isolation check failed."""


def need(condition: bool, message: str) -> None:
    if condition is not True:
        raise GuardError(message)


def read_owner(item: tuple[str, str, int, int], label: str) -> bytes:
    path, expected, size, inode = item
    need(type(path) is str and not path.startswith("/")
         and ".." not in path.split("/"), "reject escaped owner: " + label)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(ROOT + "/" + path, flags)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode)
             and before.st_uid == os.geteuid() and before.st_dev == 2064
             and before.st_ino == inode and before.st_size == size
             and before.st_nlink == 1 and stat.S_IMODE(before.st_mode) == 0o600,
             "reject substituted private owner: " + label)
        parts: list[bytes] = []
        left = size
        while left:
            block = os.read(fd, min(left, 262144))
            need(bool(block), "reject truncated owner: " + label)
            parts.append(block)
            left -= len(block)
        need(not os.read(fd, 1), "reject extended owner: " + label)
        raw = b"".join(parts)
        after = os.fstat(fd)
        need(hashlib.sha256(raw).hexdigest() == expected
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject modified owner: " + label)
        return raw
    finally:
        os.close(fd)


def quote(value: str) -> str:
    result = ['"']
    mapping = {"\\": "\\\\", '"': '\\"', "\b": "\\b", "\f": "\\f",
               "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    for character in value:
        if character in mapping:
            result.append(mapping[character])
        elif ord(character) < 32:
            result.append("\\u" + format(ord(character), "04x"))
        else:
            result.append(character)
    result.append('"')
    return "".join(result)


def canonical(value: object) -> bytes:
    def encode(item: object, depth: int = 0) -> str:
        need(depth <= 48, "reject excessive JSON nesting")
        if item is None:
            return "null"
        if item is True:
            return "true"
        if item is False:
            return "false"
        if type(item) is str:
            return quote(item)
        if type(item) is int:
            return str(item)
        if type(item) is list:
            return "[" + ",".join(encode(entry, depth + 1) for entry in item) + "]"
        if type(item) is dict:
            need(all(type(key) is str for key in item), "reject non-string JSON keys")
            return "{" + ",".join(quote(key) + ":" + encode(item[key], depth + 1)
                                   for key in sorted(item)) + "}"
        raise GuardError("reject unsupported JSON type")
    return (encode(value) + "\n").encode("utf-8")


class JsonReader:
    """Small bounded JSON decoder that never imports the stdlib re module."""

    def __init__(self, raw: bytes):
        need(type(raw) is bytes and 0 < len(raw) <= 4_194_304,
             "reject absent or oversized frozen JSON")
        self.text = raw.decode("utf-8", "strict")
        self.index = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        need(self.index < len(self.text) and self.text[self.index] == '"',
             "require an actual JSON string")
        self.index += 1
        pieces: list[str] = []
        mapping = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
                   "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            char = self.text[self.index]
            self.index += 1
            if char == '"':
                return "".join(pieces)
            need(ord(char) >= 32, "reject literal JSON control character")
            if char != "\\":
                pieces.append(char)
            else:
                need(self.index < len(self.text), "reject truncated JSON escape")
                esc = self.text[self.index]
                self.index += 1
                if esc == "u":
                    digits = self.text[self.index:self.index + 4]
                    need(len(digits) == 4
                         and all(x in "0123456789abcdefABCDEF" for x in digits),
                         "reject invalid JSON unicode escape")
                    self.index += 4
                    pieces.append(chr(int(digits, 16)))
                else:
                    need(esc in mapping, "reject invalid JSON string escape")
                    pieces.append(mapping[esc])
        raise GuardError("reject unterminated JSON string")

    def value(self, depth: int = 0) -> object:
        need(depth <= 48, "reject excessive frozen JSON depth")
        self.whitespace()
        need(self.index < len(self.text), "reject missing JSON value")
        char = self.text[self.index]
        if char == '"':
            return self.string()
        if char == "{":
            self.index += 1
            result: dict[str, object] = {}
            self.whitespace()
            if self.index < len(self.text) and self.text[self.index] == "}":
                self.index += 1
                return result
            while True:
                self.whitespace()
                key = self.string()
                need(key not in result, "reject duplicate JSON owner: " + key)
                self.whitespace()
                need(self.index < len(self.text) and self.text[self.index] == ":",
                     "reject missing JSON object separator")
                self.index += 1
                result[key] = self.value(depth + 1)
                self.whitespace()
                need(self.index < len(self.text), "reject unterminated JSON object")
                char = self.text[self.index]
                self.index += 1
                if char == "}":
                    return result
                need(char == ",", "reject invalid JSON object separator")
        if char == "[":
            self.index += 1
            result_list: list[object] = []
            self.whitespace()
            if self.index < len(self.text) and self.text[self.index] == "]":
                self.index += 1
                return result_list
            while True:
                result_list.append(self.value(depth + 1))
                self.whitespace()
                need(self.index < len(self.text), "reject unterminated JSON array")
                char = self.text[self.index]
                self.index += 1
                if char == "]":
                    return result_list
                need(char == ",", "reject invalid JSON array separator")
        for word, replacement in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(word, self.index):
                self.index += len(word)
                return replacement
        start = self.index
        if char == "-":
            self.index += 1
        need(self.index < len(self.text) and self.text[self.index].isdigit(),
             "reject unsupported or invalid frozen JSON number")
        while self.index < len(self.text) and self.text[self.index].isdigit():
            self.index += 1
        return int(self.text[start:self.index])

    def parse(self) -> object:
        result = self.value()
        self.whitespace()
        need(self.index == len(self.text), "reject trailing frozen JSON data")
        return result


class RuntimePolicy:
    """Fail-closed guard installed before an independently selected engine."""

    def __init__(self):
        self.selected: types.ModuleType | None = None
        self.selected_family: str | None = None
        self.constants: types.ModuleType | None = None
        self.fork_case: str | None = None
        self.correctness_clock_case: str | None = None
        self.blocked: dict[str, int] = {}
        self.correctness_clock_events = 0
        self.installed = False

    def deny(self, reason: str) -> None:
        self.blocked[reason] = self.blocked.get(reason, 0) + 1
        raise GuardError("runtime guard blocked " + reason)

    def forbidden_module(self, name: str) -> bool:
        return name == "re._compiler" or name.startswith("re._compiler.") \
            or name == "re._parser" or name.startswith("re._parser.") \
            or name == "_sre" or name.startswith("_sre.") \
            or any(name == item or name.startswith(item + ".")
                   for item in DENIED_PREFIXES)

    def check_import(self, name: object) -> None:
        if type(name) is not str:
            self.deny("invalid-import")
        assert isinstance(name, str)
        if self.forbidden_module(name):
            self.deny("forbidden-regex:" + name)
        if name == "re":
            if self.selected is None or sys.modules.get("re") is not self.selected:
                self.deny("unattested-stdlib-re")
        elif name == "re._constants":
            if self.selected is None or self.constants is None \
                    or sys.modules.get("re") is not self.selected \
                    or sys.modules.get("re._constants") is not self.constants \
                    or getattr(self.constants, "MAXGROUPS", None) != MAXGROUPS:
                self.deny("unattested-private-regex-constants")
        elif name.startswith("re."):
            self.deny("private-stdlib-regex:" + name)
        elif name == "candidates" or name.startswith("candidates."):
            allowed = self.selected_family
            if allowed is None or name not in ("candidates", allowed):
                self.deny("cross-family-candidate:" + name)

    def check_modules(self) -> None:
        for name in tuple(sys.modules):
            if self.forbidden_module(name):
                self.deny("preloaded-regex:" + name)
            if name == "re" and sys.modules.get(name) is not self.selected:
                self.deny("preloaded-stdlib-re")
            if name.startswith("re.") and name != "re._constants":
                self.deny("preloaded-private-regex:" + name)
            if name == "re._constants" and sys.modules.get(name) is not self.constants:
                self.deny("preloaded-private-constants")
            if name.startswith("candidates.") and name != self.selected_family:
                self.deny("preloaded-cross-family:" + name)

    def audit(self, event: str, args: tuple) -> None:
        if event == "import":
            self.check_import(args[0] if args else None)
        elif event == "os.fork":
            if self.fork_case != "ReTests.test_regression_gh94675":
                self.deny("unscoped-fork")
        elif event.startswith("os.exec") or event.startswith("os.spawn") \
                or event in DENIED_EVENTS:
            self.deny("forbidden-native-process-network-loader:" + event)
        elif event == "rebar.correctness.clock":
            if self.correctness_clock_case != "ReTests.test_search_anchor_at_beginning":
                self.deny("unscoped-correctness-clock")
            self.correctness_clock_events += 1
        elif event in ("_interpreters.create", "_interpreters.exec"):
            self.deny("unguarded-subinterpreter")

    def find_spec(self, fullname: str, path: object = None,
                  target: object = None) -> None:
        self.check_import(fullname)
        return None

    def install(self) -> None:
        need(not self.installed, "reject duplicate guard installation")
        self.check_modules()
        sys.addaudithook(self.audit)
        sys.meta_path.insert(0, self)
        self.installed = True
        self.check_modules()

    def bind_selected(self, module: types.ModuleType, family: str) -> None:
        need(self.installed and self.selected is None and type(module) is types.ModuleType,
             "require one actual module after physical guard installation")
        need(family in FAMILIES and family not in sys.modules
             and "_sre" not in sys.modules and "re" not in sys.modules,
             "reject preloaded stdlib or alternate candidate")
        self.selected = module
        self.selected_family = FAMILIES[family]
        sys.modules["re"] = module
        constants = types.ModuleType("re._constants")
        constants.MAXGROUPS = MAXGROUPS
        self.constants = constants
        sys.modules["re._constants"] = constants
        self.check_modules()


def verify_p0(value: object) -> None:
    need(type(value) is dict, "reject missing complete phase-one oracle")
    assert isinstance(value, dict)
    need(value["schema"] == "rebar-cpython-re-p0-completeness-v4"
         and value["version"] == 4 and value["status"] == "PASS"
         and value["original_case_execution_denominator"] == 31237
         and value["original_suite_count"] == 13
         and value["original_obligation_count"] == 73
         and value["original_named_private_waiver_count"] == 13
         and value["first_party_candidate_family_count"] == 6
         and value["qualified_candidate_count"] == 0
         and value["holdout"] == "NOT OPENED",
         "authenticate the passing frozen reference, not an invented candidate")
    supplemental = value["actual_supplemental_two_reference"]
    need(supplemental["actual_reference_worker_count"] == 2,
         "require the exact separate two-reference supplemental gate")


def verify_baseline(graph: object, build_receipt: object,
                    provenance: object) -> None:
    need(type(graph) is dict and type(build_receipt) is dict
         and type(provenance) is dict,
         "require complete actual graph and both first-party build receipts")
    assert isinstance(graph, dict) and isinstance(build_receipt, dict)
    assert isinstance(provenance, dict)
    need(graph["version"] == 73
         and graph["authenticated_evidence_owner_lower_bound"] == 243
         and graph["authenticated_history_reference_lower_bound"] == 248
         and graph["actual_rust_semantic_mismatch_count"] == 1440
         and graph["actual_rust_verified_passing_case_count"] == 14853
         and graph["actual_c_semantic_mismatch_count"] == 1230
         and graph["actual_c_verified_passing_case_count"] == 7325
         and graph["actual_zig_semantic_mismatch_count"] == 1764
         and graph["rust_native_build_v19_status"] == "PASS"
         and graph["rust_native_build_v19_actual_compiler_process_count"] == 28
         and graph["rust_native_build_v19_private_root_device"] == 2049
         and graph["runtime_no_delegation"] == "NOT ESTABLISHED"
         and graph["qualified_candidate_count"] == 0
         and graph["final_holdout_opened"] is False
         and graph["performance"] == "NOT MEASURED",
         "do not weaken actual pushed graph, runtime blocker, or candidate failures")
    campaign = graph["actual_complete_rust_campaign"]
    need(len(campaign["complete_independently_authenticated_suite_results"]) == 13
         and len(campaign["earliest_genuine_mismatch_witnesses"]) == 6,
         "preserve every independently verified original result")
    need(build_receipt["status"] == "PASS"
         and build_receipt["actual_compiler_process_count"] == 28
         and build_receipt["current_graph_version"] == 70
         and build_receipt["historical_actual_rust_mismatch_count"] == 928
         and build_receipt["historical_actual_rust_verified_passing_case_count"] == 8965
         and provenance["status"] == "PASS"
         and provenance["actual_compiler_process_count"] == 28
         and provenance["root"]["device"] == 2049
         and provenance["root"]["inode"] == 11673243
         and provenance["native_libraries_loaded"] == 0,
         "preserve genuine root provenance without confusing historical Rust results")


def denied(policy: RuntimePolicy, operation: object, label: str) -> int:
    try:
        assert callable(operation)
        operation()
    except (GuardError, ImportError, ModuleNotFoundError, ValueError, TypeError):
        return 1
    raise GuardError("accepted forbidden runtime control: " + label)


def hostile_controls(policy: RuntimePolicy) -> int:
    rejected = 0
    module_names = (
        "re", "_sre", "re._compiler", "re._parser", "re._constants",
        "sre_compile", "sre_parse", "sre_constants", "regex", "regex._regex",
        "re2", "pcre", "pcre2", "oniguruma", "onig", "hyperscan",
        "candidates.rust_candidate", "candidates.vm_candidate",
        "candidates.zig_candidate", "candidates.cpp_candidate",
        "candidates.go_candidate", "candidates.fortran_candidate",
    )
    for name in module_names:
        rejected += denied(policy, lambda item=name: policy.check_import(item), name)
    for name in ("_sre", "regex", "re._compiler", "candidates.rust_candidate"):
        rejected += denied(policy, lambda item=name: __import__(item), "physical import " + name)
    for event in DENIED_EVENTS:
        rejected += denied(policy, lambda item=event: sys.audit(item, "forbidden"), event)
    rejected += denied(policy, lambda: sys.audit("os.fork"), "unscoped fork")
    rejected += denied(policy, lambda: sys.audit("rebar.correctness.clock"),
                       "benchmark disguised as a correctness clock")
    rejected += denied(policy, lambda: sys.audit("_interpreters.create", 1),
                       "unguarded subinterpreter")
    need("_sre" not in sys.modules and "re" not in sys.modules,
         "reject candidate or stdlib matcher imported during hostile controls")
    fake = types.ModuleType("_rebar_synthetic_guard_positive_control")
    policy.bind_selected(fake, "rust")
    need(sys.modules["re"] is fake
         and sys.modules["re._constants"] is policy.constants
         and policy.constants is not None
         and policy.constants.MAXGROUPS == MAXGROUPS,
         "bind only the same module and data-only public-test constant")
    need(__import__("re") is fake,
         "allow only the selected exact module under the re public alias")
    before = dict(sys.modules)
    sys.modules["re"] = types.ModuleType("_forged_replacement")
    rejected += denied(policy, policy.check_modules, "forged public alias")
    sys.modules["re"] = fake
    constants = policy.constants
    assert constants is not None
    original_maxgroups = constants.MAXGROUPS
    constants.MAXGROUPS = MAXGROUPS + 1
    rejected += denied(policy, lambda: policy.check_import("re._constants"),
                       "forged MAXGROUPS")
    constants.MAXGROUPS = original_maxgroups
    policy.fork_case = "wrong.original.case"
    rejected += denied(policy, lambda: sys.audit("os.fork"), "wrong original fork case")
    policy.fork_case = "ReTests.test_regression_gh94675"
    sys.audit("os.fork")
    policy.fork_case = None
    policy.correctness_clock_case = "wrong.original.case"
    rejected += denied(policy, lambda: sys.audit("rebar.correctness.clock"),
                       "wrong original correctness clock case")
    policy.correctness_clock_case = "ReTests.test_search_anchor_at_beginning"
    sys.audit("rebar.correctness.clock")
    policy.correctness_clock_case = None
    need(policy.correctness_clock_events == 1,
         "record correctness clocks separately from performance measurements")
    payload = marshal.dumps({"case": "source-only", "original_cases": 31237})
    decoded = marshal.loads(payload, allow_code=False)
    need(decoded == {"case": "source-only", "original_cases": 31237},
         "preserve bounded, code-free original-suite communication")
    code = compile("1", "<hostile-guard-code>", "eval")
    rejected += denied(policy,
                       lambda: marshal.loads(marshal.dumps(code), allow_code=False),
                       "marshalled executable code")
    del sys.modules["re._constants"]
    del sys.modules["re"]
    policy.constants = None
    policy.selected = None
    policy.selected_family = None
    policy.check_modules()
    need("re" not in sys.modules and "_sre" not in sys.modules
         and rejected >= 38,
         "require physical first-party runtime isolation and hostile controls")
    del before
    return rejected


def parse_options(arguments: list[str]) -> dict[str, object]:
    result: dict[str, object] = {}
    modes = {"--self-test", "--verify-frozen-context"}
    allowed = {
        "--source-sha256", "--protocol-sha256", "--contract-sha256",
        "--graph-source-sha256", "--graph-inputs-sha256",
        "--graph-summary-sha256", "--graph-svg-sha256",
    }
    i = 0
    while i < len(arguments):
        name = arguments[i]
        if name in modes:
            need("mode" not in result, "reject duplicate or conflicting guard modes")
            result["mode"] = name
            i += 1
            continue
        need(name in allowed, "reject unapproved guard command-line authority")
        need(name not in result and i + 1 < len(arguments),
             "reject duplicate or missing guard owner pin")
        value = arguments[i + 1]
        need(len(value) == 64 and all(ch in "0123456789abcdef" for ch in value),
             "reject invalid pinned SHA-256")
        result[name] = value
        i += 2
    need(result.get("mode") in modes and len(result) == 8,
         "require exactly one guard mode and all seven pinned source/graph owners")
    return result


def validate_contract(contract: object, options: dict[str, object],
                      graph: dict, p0: dict) -> None:
    need(type(contract) is dict, "require complete canonical guard contract")
    assert isinstance(contract, dict)
    required = {
        "schema", "version", "status", "source", "protocol", "current_graph",
        "phase1_v4_readiness", "first_party_candidate_families",
        "runtime_isolation_policy", "original_public_test_exceptions",
        "supplemental_obligations", "first_party_rust_native_provenance",
        "source_only_effects", "runtime_non_delegation", "holdout", "performance",
        "memory", "undefined_behavior", "qualified_candidate_count", "winner_selected",
    }
    need(set(contract) == required and contract["schema"]
         == "rebar-owned-candidate-runtime-independence-v1-source-freeze"
         and contract["version"] == 1
         and contract["status"] == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
         and contract["runtime_non_delegation"] == "NOT ESTABLISHED"
         and contract["holdout"] == "NOT OPENED"
         and contract["performance"] == "NOT MEASURED"
         and contract["qualified_candidate_count"] == 0
         and contract["winner_selected"] is False,
         "never mistake a guard source freeze for actual runtime independence")
    source = contract["source"]
    protocol = contract["protocol"]
    need(source["path"] == SELF
         and source["sha256"] == options["--source-sha256"]
         and protocol["path"] == PROTOCOL
         and protocol["sha256"] == options["--protocol-sha256"],
         "reject a fabricated guard source or protocol")
    current = contract["current_graph"]
    need(current["version"] == 73
         and current["authenticated_evidence_owner_lower_bound"] == 243
         and current["authenticated_history_reference_lower_bound"] == 248
         and len(current["owners"]) == 4,
         "bind the whole actually pushed V73 graph")
    indexed = {item["path"]: item for item in current["owners"]}
    need(set(indexed) == {item[0] for item in V73.values()},
         "reject omitted V73 graph owners")
    for role, item in V73.items():
        owner = indexed[item[0]]
        need(owner["sha256"] == item[1] and owner["bytes"] == item[2]
             and owner["inode"] == item[3] and owner["device"] == 2064
             and options["--graph-" + role + "-sha256"] == item[1],
             "reject substituted V73 graph " + role)
    need(contract["first_party_candidate_families"] == FAMILIES,
         "reject a wrapped, omitted, or cross-family regex engine")
    policy = contract["runtime_isolation_policy"]
    need(policy["bootstrap"] == "CPython -I -B -S; audit hook before candidate import"
         and policy["candidate_alias"] == "sys.modules['re'] is the attested candidate"
         and policy["stdlib_re_engine"] == "FORBIDDEN"
         and policy["stdlib_sre_engine"] == "FORBIDDEN"
         and policy["external_regex_package"] == "FORBIDDEN"
         and policy["cross_candidate_engine"] == "FORBIDDEN"
         and policy["matching_fallback"] == "FORBIDDEN"
         and policy["native_loader"] == "ONLY INDIVIDUALLY ATTESTED FAMILY ARTIFACTS"
         and policy["guard_installed_before_candidate_import"] is True,
         "require irreversible, sterile, first-party runtime denial")
    original = contract["original_public_test_exceptions"]
    need(original["data_only_MAXGROUPS"] == MAXGROUPS
         and original["MAXGROUPS_module"] == "re._constants"
         and original["only_fork_case"] == "ReTests.test_regression_gh94675"
         and original["only_correctness_clock_case"]
             == "ReTests.test_search_anchor_at_beginning"
         and original["locale_fixture_origin"] == "SEPARATE ORACLE PROCESS ONLY"
         and original["nested_interpreters"] == "EACH MUST INSTALL AN INDEPENDENT GUARD",
         "preserve original public CPython tests without creating runtime loopholes")
    readiness = contract["phase1_v4_readiness"]
    need(readiness["status"] == "PASS"
         and readiness["contract_sha256"] == P0["contract"][1]
         and readiness["original_case_execution_denominator"] == 31237
         and readiness["original_suite_count"] == 13
         and readiness["original_obligation_count"] == 73
         and readiness["named_private_waiver_count"] == 13
         and readiness["separate_supplemental_case_count"] == 8244,
         "preserve frozen comprehensive P0 without merged denominators")
    rust = contract["first_party_rust_native_provenance"]
    need(rust["build_receipt_sha256"] == V19_BUILD[1]
         and rust["root_provenance_receipt_sha256"] == V19_ROOT[1]
         and rust["root_device"] == 2049 and rust["root_inode"] == 11673243
         and rust["actual_compiler_process_count"] == 28
         and rust["candidate_matching"] == "NOT RUN",
         "authenticate existing native provenance without loading a candidate")
    effects = contract["source_only_effects"]
    need(all(value == 0 for value in effects.values()),
         "reject source-mode candidate, native, reference, archive, clock, or holdout")
    need(graph["version"] == current["version"]
         and p0["original_case_execution_denominator"]
             == readiness["original_case_execution_denominator"],
         "cross-check real P0 and actually current V73 graph")


def source_run(options: dict[str, object]) -> dict:
    need(sys.flags.isolated == 1 and sys.flags.no_site == 1
         and sys.flags.dont_write_bytecode == 1,
         "require the genuinely sterile pinned Python -I -B -S startup")
    need("re" not in sys.modules and "_sre" not in sys.modules,
         "stdlib regex was imported before the runtime guard")
    source_fd = os.open(ROOT + "/" + SELF,
                        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                        | getattr(os, "O_NOFOLLOW", 0))
    try:
        source_meta = os.fstat(source_fd)
        need(stat.S_ISREG(source_meta.st_mode) and source_meta.st_dev == 2064
             and source_meta.st_uid == os.geteuid() and source_meta.st_nlink == 1
             and stat.S_IMODE(source_meta.st_mode) == 0o600,
             "reject substituted guard verifier")
        source_raw = b""
        while True:
            block = os.read(source_fd, 131072)
            if not block:
                break
            source_raw += block
        need(hashlib.sha256(source_raw).hexdigest() == options["--source-sha256"],
             "reject caller's wrong final guard verifier digest")
    finally:
        os.close(source_fd)
    for role, item in P0.items():
        read_owner(item, "passing frozen P0 " + role)
    for role, item in V73.items():
        need(options["--graph-" + role + "-sha256"] == item[1],
             "reject non-current pinned graph " + role)
        read_owner(item, "current pushed V73 " + role)
    p0 = JsonReader(read_owner(P0["contract"], "complete passing P0 contract")).parse()
    graph = JsonReader(read_owner(V73["summary"], "complete current V73 summary")).parse()
    verify_p0(p0)
    build_receipt = JsonReader(read_owner(V19_BUILD, "tiny actual V19 build receipt")).parse()
    root_receipt = JsonReader(read_owner(V19_ROOT, "tiny actual V19 provenance receipt")).parse()
    verify_baseline(graph, build_receipt, root_receipt)
    protocol_meta = os.stat(ROOT + "/" + PROTOCOL, follow_symlinks=False)
    need(stat.S_ISREG(protocol_meta.st_mode) and protocol_meta.st_dev == 2064
         and protocol_meta.st_uid == os.geteuid() and protocol_meta.st_nlink == 1
         and stat.S_IMODE(protocol_meta.st_mode) == 0o600,
         "reject substituted actual guard protocol")
    protocol = read_owner((PROTOCOL, options["--protocol-sha256"],
                           protocol_meta.st_size, protocol_meta.st_ino),
                          "actual guard protocol")
    need(protocol.endswith(b"\n"), "require complete stable guard protocol")
    contract_meta = os.stat(ROOT + "/" + CONTRACT, follow_symlinks=False)
    need(stat.S_ISREG(contract_meta.st_mode) and contract_meta.st_dev == 2064
         and contract_meta.st_uid == os.geteuid() and contract_meta.st_nlink == 1
         and stat.S_IMODE(contract_meta.st_mode) == 0o600,
         "reject substituted actual guard machine contract")
    contract_raw = read_owner((CONTRACT, options["--contract-sha256"],
                               contract_meta.st_size, contract_meta.st_ino),
                              "complete actual guard machine contract")
    contract = JsonReader(contract_raw).parse()
    need(canonical(contract) == contract_raw,
         "reject noncanonical or duplicate-key guard machine contract")
    assert isinstance(graph, dict) and isinstance(p0, dict)
    validate_contract(contract, options, graph, p0)
    policy = RuntimePolicy()
    policy.install()
    rejected = hostile_controls(policy)
    return {
        "schema": "rebar-owned-candidate-runtime-independence-v1-source-"
                  + ("self-test" if options["mode"] == "--self-test" else "frozen-context"),
        "version": 1, "status": "PASS",
        "source_sha256": options["--source-sha256"],
        "protocol_sha256": options["--protocol-sha256"],
        "contract_sha256": options["--contract-sha256"],
        "actual_current_graph_version": 73,
        "authenticated_evidence_owner_lower_bound": 243,
        "authenticated_history_reference_lower_bound": 248,
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "separate_supplemental_case_count": 8244,
        "candidate_family_count": 6,
        "rejected_hostile_control_count": rejected,
        "physically_blocked_controls": dict(policy.blocked),
        "synthetic_data_only_MAXGROUPS_control": MAXGROUPS,
        "synthetic_correctness_clock_event_count": 1,
        "actual_correctness_clocks_sampled": 0,
        "actual_benchmark_clock_samples": 0,
        "actual_candidate_imports": 0,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_native_loads": 0,
        "actual_native_root_opens": 0,
        "actual_archive_opens": 0,
        "actual_processes_started": 0,
        "actual_network_requests": 0,
        "actual_holdout_cases_read": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
    }


def main() -> int:
    try:
        options = parse_options(sys.argv[1:])
        sys.stdout.buffer.write(canonical(source_run(options)))
        return 0
    except Exception as error:
        sys.stderr.write("candidate runtime guard rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
