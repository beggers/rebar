#!/usr/bin/env python3
"""Guard one owned regex engine, its own bridge, and each child interpreter."""

from __future__ import annotations

# A clean worker must never import argparse, json, pathlib, unittest, typing,
# dataclasses, or any other module which can preload re and _sre.
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
SELF = "tools/verify_owned_candidate_runtime_independence_v2.py"
PROTOCOL = "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md"
CONTRACT = "oracle/phase2/candidate-runtime-independence-v2.json"
GOAL = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3756,
    31364044,
)
V1 = {
    "source": (
        "tools/verify_owned_candidate_runtime_independence_v1.py",
        "c511d72053957aaebeafe23d57c7d5438c72c00307bcbfed167a776666d0baa9",
        35270,
        431283,
    ),
    "protocol": (
        "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V1.md",
        "7d0cd123f7306eb1468d65bf10ff224151752bc16d6e587576bb6a3ccb7a8795",
        3464,
        524839,
    ),
    "contract": (
        "oracle/phase2/candidate-runtime-independence-v1.json",
        "a784f0bc315a4cb946c09d160ed00387becd7fec9585a1e488d48a6c0f63f2fe",
        3987,
        524840,
    ),
}
P0 = {
    "source": (
        "tools/verify_owned_p0_completeness_v4.py",
        "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d",
        29094,
        428927,
    ),
    "protocol": (
        "oracle/phase1/P0-COMPLETENESS-V4.md",
        "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
        4261,
        524712,
    ),
    "contract": (
        "oracle/phase1/p0-completeness-v4.json",
        "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
        34875,
        524713,
    ),
}
V74 = {
    "source": (
        "tools/render_candidate_current_overview_v74.py",
        "7fecafe25316c98bd6c86d6f82779250abb54ca3451abc84e04e2d8bc505d21d",
        30742,
        431284,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v74.inputs.json",
        "aa54170b8e4c426de1210f90c47b16677af80482418fb3cdf3327c173542b425",
        1153735,
        431290,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v74.json",
        "006f402dd3f8ec8150b844f8584d17d22afcd2fae99434e745bf6dbf3682a283",
        3266545,
        431315,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v74.svg",
        "1fac5fe3540dc0493e49ce581a30a04e1b843a73beddef8a876b8a6ae45a8060",
        4699,
        431316,
    ),
}
BUILD_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v19-rust-phase2-v19-rust-buffer-shape-root-provenance-publication-receipt.json",
    "27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc",
    3486,
    524773,
)
ROOT_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v19-rust-phase2-v19-rust-buffer-shape-root-provenance-root-provenance-receipt.json",
    "de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99",
    4367,
    524774,
)
NESTED = {
    "source": (
        "tools/run_owned_candidate_subinterpreters_v2.py",
        "7dd5b4a5cdfecbe6dd674632bb5cee456ee877291de88ffc76ba60472d81408a",
        98245,
        432388,
    ),
    "protocol": (
        "oracle/phase2/candidate-subinterpreters-v2.json",
        "f740da205f8431898f0a1089df5419f01612c2384def78c7d9831748ecca1b24",
        7875,
        524503,
    ),
    "explanation": (
        "oracle/phase2/CANDIDATE-SUBINTERPRETERS-V2.md",
        "c7a501f4487dfbe547c2cf8f5844be5179da035e7ae5f5e89f803234f3bf32dc",
        5390,
        524502,
    ),
}
PINNED_INTERPRETERS = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/concurrent/interpreters/__init__.py"
)
PINNED_INTERPRETERS_SHA256 = (
    "040e47f07bdfb28c67798fa7764fac1d79e13fd0fc0db9c85ee5dae8e1edf249"
)
PINNED_INTERPRETERS_DEVICE = 2049
PINNED_INTERPRETERS_INODE = 9595896
PINNED_INTERPRETERS_BYTES = 7707
FAMILY_BRIDGES = {
    "rust": {
        "candidate_module": "candidates.rust_candidate",
        "owned_bridge_module": "candidates._rust_bridge",
    },
    "c": {
        "candidate_module": "candidates.vm_candidate",
        "owned_bridge_module": "candidates._vm_native",
    },
    "zig": {
        "candidate_module": "candidates.zig_candidate",
        "owned_bridge_module": "candidates._zig_bridge",
    },
    "cpp": {
        "candidate_module": "candidates.cpp_candidate",
        "owned_bridge_module": "candidates._cpp_bridge",
    },
    "go": {
        "candidate_module": "candidates.go_candidate",
        "owned_bridge_module": "candidates._go_bridge",
    },
    "fortran": {
        "candidate_module": "candidates.fortran_candidate",
        "owned_bridge_module": "candidates._fortran_bridge",
    },
}
EFFECT_KEYS = frozenset({
    "candidate_imports",
    "candidate_workers_started",
    "clock_samples",
    "compiler_processes_started",
    "compressed_archives_opened",
    "hidden_cases_read",
    "holdout_cases_opened",
    "native_libraries_loaded",
    "native_roots_opened",
    "network_requests",
    "reference_workers_started",
    "subprocesses_started",
    "timing_trials_run",
})
CONTRACT_KEYS = frozenset({
    "schema",
    "version",
    "status",
    "source",
    "protocol",
    "current_graph",
    "predecessor_v1",
    "phase1_v4_readiness",
    "first_party_candidate_families",
    "family_bridge_policy",
    "native_provenance",
    "subinterpreter_bootstrap",
    "original_public_test_exceptions",
    "supplemental_obligations",
    "source_only_effects",
    "runtime_isolation_policy",
    "runtime_non_delegation",
    "holdout",
    "performance",
    "memory",
    "undefined_behavior",
    "qualified_candidate_count",
    "winner_selected",
})


class BootstrapError(Exception):
    """The clean-start operational guard or its frozen provenance was invalid."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise BootstrapError(message)


def sha256_pin(value: object, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value),
        "require a complete lowercase SHA-256: " + label,
    )
    assert isinstance(value, str)
    return value


def read_owner(item: tuple[str, str, int, int], label: str) -> bytes:
    relative, expected, expected_bytes, expected_inode = item
    require(
        type(relative) is str
        and relative
        and not relative.startswith("/")
        and ".." not in relative.split("/")
        and not relative.endswith((".gz", ".so"))
        and "holdout" not in relative.lower()
        and "benchmark" not in relative.lower(),
        "reject an archive, native library, final case, or escaped owner: " + label,
    )
    sha256_pin(expected, label)
    require(
        type(expected_bytes) is int and 0 < expected_bytes <= 4_194_304,
        "reject an oversized or invented source owner: " + label,
    )
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(ROOT + "/" + relative, flags)
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_dev == 2064
            and before.st_ino == expected_inode
            and before.st_size == expected_bytes
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600,
            "reject a substituted exclusive owner: " + label,
        )
        parts: list[bytes] = []
        left = expected_bytes
        while left:
            block = os.read(descriptor, min(left, 262144))
            require(bool(block), "reject a truncated owner: " + label)
            parts.append(block)
            left -= len(block)
        require(not os.read(descriptor, 1), "reject an extended owner: " + label)
        raw = b"".join(parts)
        after = os.fstat(descriptor)
        require(
            hashlib.sha256(raw).hexdigest() == expected
            and (
                before.st_dev,
                before.st_ino,
                before.st_size,
                before.st_mtime_ns,
                before.st_ctime_ns,
                before.st_nlink,
            )
            == (
                after.st_dev,
                after.st_ino,
                after.st_size,
                after.st_mtime_ns,
                after.st_ctime_ns,
                after.st_nlink,
            ),
            "reject a changed complete owner: " + label,
        )
        return raw
    finally:
        os.close(descriptor)


def load_predecessor() -> types.ModuleType:
    require(
        "re" not in sys.modules
        and "_sre" not in sys.modules
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "load the immutable predecessor only in a genuinely clean interpreter",
    )
    raw = read_owner(V1["source"], "immutable first-generation guard source")
    module = types.ModuleType("_rebar_exact_first_party_runtime_guard_v1")
    module.__file__ = ROOT + "/" + V1["source"][0]
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    require(
        module.SELF == V1["source"][0]
        and module.PROTOCOL == V1["protocol"][0]
        and module.CONTRACT == V1["contract"][0]
        and callable(module.canonical)
        and callable(module.JsonReader)
        and "re" not in sys.modules
        and "_sre" not in sys.modules,
        "authenticate the matcher-free immutable first-party guard implementation",
    )
    return module


BASE = load_predecessor()
GuardError = BASE.GuardError
JsonReader = BASE.JsonReader
canonical = BASE.canonical
MAXGROUPS = BASE.MAXGROUPS
DENIED_EVENTS = BASE.DENIED_EVENTS


def owner_identity(item: tuple[str, str, int, int]) -> dict:
    relative, digest, count, inode = item
    return {
        "path": relative,
        "sha256": digest,
        "bytes": count,
        "device": 2064,
        "inode": inode,
        "mode": "0600",
        "nlink": 1,
    }


def dynamic_owner(relative: str, digest: str, label: str) -> tuple:
    sha256_pin(digest, label)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(ROOT + "/" + relative, flags)
    try:
        actual = os.fstat(descriptor)
        require(
            stat.S_ISREG(actual.st_mode)
            and actual.st_uid == os.geteuid()
            and actual.st_dev == 2064
            and actual.st_nlink == 1
            and stat.S_IMODE(actual.st_mode) == 0o600
            and 0 < actual.st_size <= 4_194_304,
            "reject a substituted operational guard " + label,
        )
        return relative, digest, actual.st_size, actual.st_ino
    finally:
        os.close(descriptor)


class RuntimePolicy(BASE.RuntimePolicy):
    """Permit exactly one authenticated first-party engine and its bridge."""

    def __init__(self):
        super().__init__()
        self.prepared_family: str | None = None
        self.approved_bridge_module: str | None = None
        self.bridge_owner: dict | None = None
        self.engine_owner: dict | None = None
        self.interpreter_suite: str | None = None
        self.expected_child_creations = 0
        self.expected_child_case_executions = 0
        self.child_creations = 0
        self.child_executions = 0
        self.child_bootstraps: dict[int, dict] = {}
        self.child_pipe_identities: set[tuple[int, int]] = set()
        self.fork_events = 0

    def live_interpreter_provider(self) -> tuple[types.ModuleType, set[int]]:
        provider = sys.modules.get("concurrent.interpreters")
        if not (
            type(provider) is types.ModuleType
            and provider.__name__ == "concurrent.interpreters"
            and os.path.realpath(str(getattr(provider, "__file__", "")))
            == PINNED_INTERPRETERS
            and callable(getattr(provider, "list_all", None))
        ):
            self.deny("unattested-real-interpreter-provider")
        assert isinstance(provider, types.ModuleType)
        flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(PINNED_INTERPRETERS, flags)
        try:
            before = os.fstat(descriptor)
            if not (
                stat.S_ISREG(before.st_mode)
                and before.st_uid == os.geteuid()
                and before.st_dev == PINNED_INTERPRETERS_DEVICE
                and before.st_ino == PINNED_INTERPRETERS_INODE
                and before.st_nlink == 1
                and before.st_size == PINNED_INTERPRETERS_BYTES
            ):
                self.deny("substituted-interpreter-provider-source")
            raw = b""
            while len(raw) <= PINNED_INTERPRETERS_BYTES:
                part = os.read(descriptor, 16384)
                if not part:
                    break
                raw += part
            after = os.fstat(descriptor)
            if not (
                len(raw) == PINNED_INTERPRETERS_BYTES
                and hashlib.sha256(raw).hexdigest()
                == PINNED_INTERPRETERS_SHA256
                and (
                    before.st_dev,
                    before.st_ino,
                    before.st_size,
                    before.st_mtime_ns,
                    before.st_ctime_ns,
                )
                == (
                    after.st_dev,
                    after.st_ino,
                    after.st_size,
                    after.st_mtime_ns,
                    after.st_ctime_ns,
                )
            ):
                self.deny("changed-real-interpreter-provider-source")
        finally:
            os.close(descriptor)
        internal = __import__("_interpreters")
        if not (
            type(internal) is types.ModuleType
            and getattr(getattr(internal, "__spec__", None), "origin", None)
            == "built-in"
            and callable(getattr(internal, "list_all", None))
        ):
            self.deny("substituted-native-interpreter-provider")
        direct = internal.list_all()
        if type(direct) is not list:
            self.deny("invalid-real-interpreter-lifecycle")
        direct_ids: set[int] = set()
        for item in direct:
            if not (
                type(item) is tuple
                and len(item) >= 1
                and type(item[0]) is int
                and item[0] >= 0
            ):
                self.deny("invalid-native-live-interpreter-identity")
            direct_ids.add(item[0])
        public = provider.list_all()
        if type(public) is not list:
            self.deny("invalid-public-live-interpreter-lifecycle")
        public_ids = {
            int(item.id)
            for item in public
            if hasattr(item, "id") and type(item.id) is int
        }
        if public_ids != direct_ids:
            self.deny("forged-public-interpreter-live-set")
        return provider, direct_ids

    def checked_native_owner(self, family: str, role: str, owner: object) -> dict:
        if type(owner) is not dict:
            self.deny("unattested-native-owner:" + role)
        assert isinstance(owner, dict)
        relative = owner.get("relative")
        absolute = owner.get("absolute_path")
        digest = owner.get("sha256")
        count = owner.get("bytes")
        if not (
            owner.get("family") == family
            and owner.get("role") == role
            and type(relative) is str
            and relative.startswith("candidates/")
            and ".." not in relative.split("/")
            and type(absolute) is str
            and absolute == ROOT + "/" + relative
            and type(count) is int
            and 0 < count <= 8 * 1024 * 1024
            and owner.get("device") == 2064
            and owner.get("nlink") == 1
            and owner.get("mode") == 0o600
        ):
            self.deny("unattested-native-owner:" + role)
        try:
            sha256_pin(digest, "attested " + family + " " + role)
        except BootstrapError:
            self.deny("unattested-native-digest:" + role)
        if role == "bridge":
            basename = FAMILY_BRIDGES[family]["owned_bridge_module"].rsplit(
                ".", 1
            )[1]
            if not os.path.basename(relative).startswith(basename + "."):
                self.deny("cross-family-native-bridge:" + relative)
        flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(absolute, flags)
        try:
            before = os.fstat(descriptor)
            if not (
                stat.S_ISREG(before.st_mode)
                and before.st_uid == os.geteuid()
                and before.st_dev == owner["device"]
                and before.st_ino == owner.get("inode")
                and before.st_nlink == 1
                and before.st_size == count
                and stat.S_IMODE(before.st_mode) == owner["mode"]
            ):
                self.deny("substituted-native-owner:" + role)
            fingerprint = hashlib.sha256()
            left = count
            while left:
                chunk = os.read(descriptor, min(left, 262144))
                if not chunk:
                    self.deny("truncated-native-owner:" + role)
                fingerprint.update(chunk)
                left -= len(chunk)
            if os.read(descriptor, 1):
                self.deny("extended-native-owner:" + role)
            after = os.fstat(descriptor)
            if not (
                fingerprint.hexdigest() == digest
                and (
                    before.st_dev,
                    before.st_ino,
                    before.st_size,
                    before.st_mtime_ns,
                    before.st_ctime_ns,
                    before.st_nlink,
                )
                == (
                    after.st_dev,
                    after.st_ino,
                    after.st_size,
                    after.st_mtime_ns,
                    after.st_ctime_ns,
                    after.st_nlink,
                )
            ):
                self.deny("changed-native-owner:" + role)
        finally:
            os.close(descriptor)
        return dict(owner)

    def prepare_family(
        self,
        family: str,
        *,
        bridge_owner: object,
        engine_owner: object,
    ) -> None:
        if not (
            self.installed
            and family in FAMILY_BRIDGES
            and self.selected is None
            and self.prepared_family is None
            and "re" not in sys.modules
            and "_sre" not in sys.modules
        ):
            self.deny("invalid-selected-family-preparation")
        checked_bridge = self.checked_native_owner(family, "bridge", bridge_owner)
        checked_engine = self.checked_native_owner(family, "engine", engine_owner)
        self.prepared_family = family
        self.selected_family = FAMILY_BRIDGES[family]["candidate_module"]
        self.approved_bridge_module = FAMILY_BRIDGES[family][
            "owned_bridge_module"
        ]
        self.bridge_owner = checked_bridge
        self.engine_owner = checked_engine
        self.check_modules()

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
            if (
                self.selected is None
                or self.constants is None
                or sys.modules.get("re") is not self.selected
                or sys.modules.get("re._constants") is not self.constants
                or getattr(self.constants, "MAXGROUPS", None) != MAXGROUPS
            ):
                self.deny("unattested-private-regex-constants")
        elif name.startswith("re."):
            self.deny("private-stdlib-regex:" + name)
        elif name == "candidates" or name.startswith("candidates."):
            if (
                self.prepared_family is None
                or name
                not in (
                    "candidates",
                    self.selected_family,
                    self.approved_bridge_module,
                )
            ):
                self.deny("cross-family-candidate:" + name)

    def check_modules(self) -> None:
        allowed = {self.selected_family, self.approved_bridge_module}
        for name, module in tuple(sys.modules.items()):
            if self.forbidden_module(name):
                self.deny("preloaded-regex:" + name)
            if name == "re" and module is not self.selected:
                self.deny("preloaded-stdlib-re")
            if name.startswith("re.") and name != "re._constants":
                self.deny("preloaded-private-regex:" + name)
            if name == "re._constants" and module is not self.constants:
                self.deny("preloaded-private-constants")
            if name.startswith("candidates.") and name not in allowed:
                self.deny("preloaded-cross-family:" + name)
            if name == self.approved_bridge_module and self.bridge_owner:
                origin = getattr(module, "__file__", None)
                if not (
                    type(origin) is str
                    and os.path.abspath(origin)
                    == self.bridge_owner["absolute_path"]
                ):
                    self.deny("substituted-selected-native-bridge")

    def bind_selected(self, module: types.ModuleType, family: str) -> None:
        if not (
            self.installed
            and self.selected is None
            and self.prepared_family == family
            and type(module) is types.ModuleType
            and module.__name__ == FAMILY_BRIDGES[family]["candidate_module"]
            and "_sre" not in sys.modules
            and "re" not in sys.modules
        ):
            self.deny("invalid-selected-candidate")
        self.selected = module
        self.selected_family = FAMILY_BRIDGES[family]["candidate_module"]
        sys.modules["re"] = module
        constants = types.ModuleType("re._constants")
        constants.MAXGROUPS = MAXGROUPS
        self.constants = constants
        sys.modules["re._constants"] = constants
        self.check_modules()

    def begin_subinterpreters(
        self,
        *,
        suite: str = "subinterpreter_v2",
        expected_created: int = 11,
        expected_exec: int = 394,
    ) -> None:
        if not (
            self.installed
            and self.selected is not None
            and self.prepared_family in FAMILY_BRIDGES
            and self.interpreter_suite is None
            and suite == "subinterpreter_v2"
            and expected_created == 11
            and expected_exec == 394
        ):
            self.deny("unscoped-subinterpreter-suite")
        self.interpreter_suite = suite
        self.expected_child_creations = expected_created
        self.expected_child_case_executions = expected_exec
        self.child_creations = 0
        self.child_executions = 0
        self.child_bootstraps = {}

    def register_child_bootstrap(
        self,
        interpreter: object,
        source: object,
        *,
        family: str,
        source_sha256: str,
        protocol_sha256: str,
        contract_sha256: str,
        bridge_owner: dict,
        engine_owner: dict,
        owner: str,
        attestation_fd: int,
        read_fd: int,
        challenge: str,
    ) -> None:
        identity = getattr(interpreter, "id", None)
        if not (
            self.interpreter_suite == "subinterpreter_v2"
            and type(identity) is int
            and identity >= 0
            and identity not in self.child_bootstraps
            and self.child_creations > len(self.child_bootstraps)
            and type(source) is str
            and 0 < len(source) <= 131072
            and self.prepared_family == family
            and self.bridge_owner == bridge_owner
            and self.engine_owner == engine_owner
            and type(attestation_fd) is int
            and attestation_fd >= 0
            and type(read_fd) is int
            and read_fd >= 0
            and read_fd != attestation_fd
            and type(challenge) is str
            and len(challenge) == 64
            and all(char in "0123456789abcdef" for char in challenge)
        ):
            self.deny("unattested-child-bootstrap")
        provider, live = self.live_interpreter_provider()
        if not (
            identity in live
            and type(interpreter).__module__.startswith("concurrent.interpreters")
            and callable(getattr(interpreter, "exec", None))
            and callable(getattr(interpreter, "close", None))
            and any(
                getattr(item, "id", None) == identity
                for item in provider.list_all()
            )
        ):
            self.deny("fabricated-live-child-interpreter")
        try:
            reader = os.fstat(read_fd)
            writer = os.fstat(attestation_fd)
        except OSError:
            self.deny("missing-real-child-attestation-pipe")
        if not (
            stat.S_ISFIFO(reader.st_mode)
            and stat.S_ISFIFO(writer.st_mode)
            and reader.st_dev == writer.st_dev
            and reader.st_ino == writer.st_ino
            and (reader.st_dev, reader.st_ino)
            not in self.child_pipe_identities
        ):
            self.deny("substituted-or-reused-child-attestation-pipe")
        assert isinstance(source, str)
        expected = child_bootstrap_source(
            family,
            source_sha256=source_sha256,
            protocol_sha256=protocol_sha256,
            contract_sha256=contract_sha256,
            bridge_owner=bridge_owner,
            engine_owner=engine_owner,
            owner=owner,
            attestation_fd=attestation_fd,
            challenge=challenge,
        )
        if source != expected:
            self.deny("substituted-canonical-child-bootstrap")
        token = hashlib.sha256(
            (
                source_sha256
                + ":"
                + protocol_sha256
                + ":"
                + contract_sha256
                + ":"
                + family
                + ":"
                + owner
                + ":"
                + challenge
                + ":"
                + bridge_owner["sha256"]
                + ":"
                + engine_owner["sha256"]
            ).encode("utf-8")
        ).hexdigest()
        self.child_bootstraps[identity] = {
            "sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            "token_sha256": hashlib.sha256(token.encode("ascii")).hexdigest(),
            "dispatched": False,
            "installed": False,
            "interpreter": interpreter,
            "read_fd": read_fd,
            "write_fd": attestation_fd,
            "pipe_device": reader.st_dev,
            "pipe_inode": reader.st_ino,
        }
        self.child_pipe_identities.add((reader.st_dev, reader.st_ino))

    def confirm_child_guard(self, interpreter: object) -> None:
        identity = getattr(interpreter, "id", None)
        state = self.child_bootstraps.get(identity)
        if not (
            self.interpreter_suite == "subinterpreter_v2"
            and type(identity) is int
            and type(state) is dict
            and state["dispatched"] is True
            and state["installed"] is False
            and state["interpreter"] is interpreter
        ):
            self.deny("missing-positive-child-guard-attestation")
        _, live = self.live_interpreter_provider()
        if identity not in live:
            self.deny("child-destroyed-before-positive-attestation")
        read_fd = state["read_fd"]
        write_fd = state["write_fd"]
        try:
            reader = os.fstat(read_fd)
            writer = os.fstat(write_fd)
            if not (
                stat.S_ISFIFO(reader.st_mode)
                and stat.S_ISFIFO(writer.st_mode)
                and reader.st_dev == state["pipe_device"]
                and writer.st_dev == state["pipe_device"]
                and reader.st_ino == state["pipe_inode"]
                and writer.st_ino == state["pipe_inode"]
            ):
                self.deny("changed-live-child-attestation-pipe")
            os.close(write_fd)
            state["write_fd"] = None
            attestation = os.read(read_fd, 65)
            if not (
                type(attestation) is bytes
                and len(attestation) == 64
                and not os.read(read_fd, 1)
                and hashlib.sha256(attestation).hexdigest()
                == state["token_sha256"]
            ):
                self.deny("forged-or-absent-real-child-pipe-attestation")
        finally:
            if type(state.get("write_fd")) is int:
                os.close(state["write_fd"])
                state["write_fd"] = None
            if type(state.get("read_fd")) is int:
                os.close(state["read_fd"])
                state["read_fd"] = None
        state["installed"] = True

    def end_subinterpreters(self) -> None:
        if not (
            self.interpreter_suite == "subinterpreter_v2"
            and self.child_creations == 11
            and self.child_executions == 394 + 2 * 11
            and len(self.child_bootstraps) == 11
            and all(
                item["dispatched"] is True and item["installed"] is True
                for item in self.child_bootstraps.values()
            )
        ):
            self.deny("incomplete-guarded-subinterpreter-suite")
        _, live = self.live_interpreter_provider()
        if set(self.child_bootstraps).intersection(live):
            self.deny("guarded-child-interpreter-was-not-destroyed")
        self.interpreter_suite = None

    def begin_fork_case(self, case: str) -> None:
        if not (
            self.installed
            and self.selected is not None
            and case == "ReTests.test_regression_gh94675"
            and self.fork_case is None
            and self.fork_events == 0
        ):
            self.deny("unscoped-fork-case")
        self.fork_case = case

    def end_fork_case(self) -> None:
        if not (
            self.fork_case == "ReTests.test_regression_gh94675"
            and self.fork_events <= 1
        ):
            self.deny("invalid-fork-scope")
        self.fork_case = None

    def begin_correctness_clock(self, case: str) -> None:
        if not (
            self.installed
            and self.selected is not None
            and case == "ReTests.test_search_anchor_at_beginning"
            and self.correctness_clock_case is None
        ):
            self.deny("unscoped-correctness-clock-case")
        self.correctness_clock_case = case

    def end_correctness_clock(self) -> None:
        if not (
            self.correctness_clock_case
            == "ReTests.test_search_anchor_at_beginning"
            and self.correctness_clock_events <= 2
        ):
            self.deny("invalid-correctness-clock-scope")
        self.correctness_clock_case = None

    def audit(self, event: str, args: tuple) -> None:
        if event == "import":
            self.check_import(args[0] if args else None)
        elif event == "os.fork":
            if (
                self.fork_case != "ReTests.test_regression_gh94675"
                or self.fork_events >= 1
            ):
                self.deny("unscoped-fork")
            self.fork_events += 1
        elif event.startswith("os.exec") or event.startswith("os.spawn"):
            self.deny("forbidden-native-process-network-loader:" + event)
        elif event in DENIED_EVENTS:
            self.deny("forbidden-native-process-network-loader:" + event)
        elif event == "rebar.correctness.clock":
            if (
                self.correctness_clock_case
                != "ReTests.test_search_anchor_at_beginning"
                or self.correctness_clock_events >= 2
            ):
                self.deny("unscoped-correctness-clock")
            self.correctness_clock_events += 1
        elif event == "_interpreters.create":
            if (
                self.interpreter_suite != "subinterpreter_v2"
                or self.child_creations >= self.expected_child_creations
            ):
                self.deny("unguarded-subinterpreter-create")
            self.child_creations += 1
        elif event == "_interpreters.exec":
            if self.interpreter_suite != "subinterpreter_v2":
                self.deny("unguarded-subinterpreter-exec")
            identity = next((value for value in args if type(value) is int), None)
            source = next((value for value in args if type(value) is str), None)
            state = self.child_bootstraps.get(identity)
            if type(state) is not dict:
                self.deny("unregistered-subinterpreter-exec")
            if state["dispatched"] is False:
                if not (
                    type(source) is str
                    and hashlib.sha256(source.encode("utf-8")).hexdigest()
                    == state["sha256"]
                ):
                    self.deny("unguarded-child-first-execution")
                state["dispatched"] = True
            elif state["installed"] is False:
                self.deny("unconfirmed-child-guard-execution")
            self.child_executions += 1
            if self.child_executions > self.expected_child_case_executions + 22:
                self.deny("excessive-subinterpreter-execution")


def child_bootstrap_source(
    family: str,
    *,
    source_sha256: str,
    protocol_sha256: str,
    contract_sha256: str,
    bridge_owner: dict,
    engine_owner: dict,
    owner: str,
    attestation_fd: int,
    challenge: str,
) -> str:
    """Create a clean child program installing its own guard before imports."""
    require(
        family in FAMILY_BRIDGES and owner in {"A", "B", "C", "temporary"},
        "bind one original nested-interpreter owner and selected family",
    )
    for value, name in (
        (source_sha256, "nested guard source"),
        (protocol_sha256, "nested guard protocol"),
        (contract_sha256, "nested guard contract"),
    ):
        sha256_pin(value, name)
    require(
        type(bridge_owner) is dict
        and type(engine_owner) is dict
        and type(attestation_fd) is int
        and attestation_fd >= 0
        and type(challenge) is str
        and len(challenge) == 64
        and all(char in "0123456789abcdef" for char in challenge)
        and bridge_owner.get("family") == family
        and bridge_owner.get("role") == "bridge"
        and engine_owner.get("family") == family
        and engine_owner.get("role") == "engine",
        "require exact separately authenticated nested native owners",
    )
    bridge_sha = sha256_pin(bridge_owner.get("sha256"), "nested bridge")
    engine_sha = sha256_pin(engine_owner.get("sha256"), "nested engine")
    token = hashlib.sha256(
        (
            source_sha256
            + ":"
            + protocol_sha256
            + ":"
            + contract_sha256
            + ":"
            + family
            + ":"
            + owner
            + ":"
            + challenge
            + ":"
            + bridge_sha
            + ":"
            + engine_sha
        ).encode("utf-8")
    ).hexdigest()
    source = (
        "import os as _owned_os\n"
        "import sys as _owned_sys\n"
        "import types as _owned_types\n"
        "import hashlib as _owned_hash\n"
        "assert 're' not in _owned_sys.modules and '_sre' not in _owned_sys.modules\n"
        "assert not any(n == 'candidates' or n.startswith('candidates.') for n in _owned_sys.modules)\n"
        "_owned_root = " + repr(ROOT) + "\n"
        "_owned_relative = " + repr(SELF) + "\n"
        "_owned_expected = " + repr(source_sha256) + "\n"
        "_owned_flags = _owned_os.O_RDONLY | getattr(_owned_os, 'O_CLOEXEC', 0) | getattr(_owned_os, 'O_NOFOLLOW', 0)\n"
        "_owned_fd = _owned_os.open(_owned_root + '/' + _owned_relative, _owned_flags)\n"
        "try:\n"
        "    _owned_raw = b''\n"
        "    while True:\n"
        "        _owned_part = _owned_os.read(_owned_fd, 131072)\n"
        "        if not _owned_part:\n"
        "            break\n"
        "        _owned_raw += _owned_part\n"
        "finally:\n"
        "    _owned_os.close(_owned_fd)\n"
        "assert _owned_hash.sha256(_owned_raw).hexdigest() == _owned_expected\n"
        "_owned_guard = _owned_types.ModuleType('_rebar_attested_runtime_guard_v2_child')\n"
        "_owned_guard.__file__ = _owned_root + '/' + _owned_relative\n"
        "exec(compile(_owned_raw, _owned_guard.__file__, 'exec', dont_inherit=True), _owned_guard.__dict__)\n"
        "_owned_guard.verify_child_contract(_owned_expected, "
        + repr(protocol_sha256)
        + ", "
        + repr(contract_sha256)
        + ")\n"
        "_owned_policy = _owned_guard.RuntimePolicy()\n"
        "_owned_policy.install()\n"
        "_owned_policy.prepare_family("
        + repr(family)
        + ", bridge_owner="
        + repr(bridge_owner)
        + ", engine_owner="
        + repr(engine_owner)
        + ")\n"
        "if not _owned_sys.path or _owned_sys.path[0] != _owned_root:\n"
        "    _owned_sys.path.insert(0, _owned_root)\n"
        "_owned_candidate = __import__("
        + repr(FAMILY_BRIDGES[family]["candidate_module"])
        + ", fromlist=['__name__'])\n"
        "_owned_policy.bind_selected(_owned_candidate, "
        + repr(family)
        + ")\n"
        "_owned_bridge = _owned_sys.modules.get("
        + repr(FAMILY_BRIDGES[family]["owned_bridge_module"])
        + ")\n"
        "assert type(_owned_bridge) is _owned_types.ModuleType\n"
        "assert _owned_os.path.abspath(str(_owned_bridge.__file__)) == "
        + repr(bridge_owner["absolute_path"])
        + "\n"
        "assert _owned_bridge.__spec__ is not None\n"
        "assert _owned_os.path.abspath(str(_owned_bridge.__spec__.origin)) == "
        + repr(bridge_owner["absolute_path"])
        + "\n"
        "import builtins as _owned_builtins\n"
        "class _OwnedChildClose:\n"
        "    def close(self):\n"
        "        assert _owned_sys.modules.get('re') is _owned_candidate\n"
        "        assert _owned_sys.modules.get("
        + repr(FAMILY_BRIDGES[family]["owned_bridge_module"])
        + ") is _owned_bridge\n"
        "        _owned_policy.check_modules()\n"
        "        assert _owned_sys.modules.get('re._constants') is _owned_policy.constants\n"
        "        _owned_sys.modules.pop('re._constants')\n"
        "        _owned_sys.modules.pop('re')\n"
        "        _owned_policy.constants = None\n"
        "        _owned_policy.selected = None\n"
        "        assert 're' not in _owned_sys.modules\n"
        "        assert '_sre' not in _owned_sys.modules\n"
        "        _owned_policy.check_modules()\n"
        "_owned_builtins._rebar_owned_candidate_subinterpreter_v1 = {\n"
        "    'candidate': _owned_candidate,\n"
        "    'adapter_module': "
        + repr(FAMILY_BRIDGES[family]["candidate_module"])
        + ",\n"
        "    'bridge_module': "
        + repr(FAMILY_BRIDGES[family]["owned_bridge_module"])
        + ",\n"
        "    'bridge': _owned_bridge,\n"
        "    'verify': _owned_policy.check_modules,\n"
        "    'stack': _OwnedChildClose(),\n"
        "    'original': None,\n"
        "    'candidate_origin_verified': True,\n"
        "    'candidate_import_count': 1,\n"
        "    'original_matcher_calls': 0,\n"
        "    'external_engine_imports': 0,\n"
        "    'cross_candidate_imports': 0,\n"
        "    'foreign_native_loads': 0,\n"
        "    'guard': _owned_policy,\n"
        "}\n"
        "_owned_builtins._rebar_subinterpreter_v2_owner = "
        + repr(owner)
        + "\n"
        "_owned_builtins._rebar_subinterpreter_v2_patterns = {}\n"
        "_owned_policy.check_modules()\n"
        "assert _owned_sys.modules['re'] is _owned_candidate\n"
        "assert '_sre' not in _owned_sys.modules\n"
        "_owned_attestation = "
        + repr(token.encode("ascii"))
        + "\n"
        "assert _owned_os.write("
        + repr(attestation_fd)
        + ", _owned_attestation) == len(_owned_attestation)\n"
    )
    compile(source, "<attested-first-party-guard-v2-child>", "exec")
    return source


def parse_options(arguments: list[str]) -> dict:
    result: dict[str, object] = {}
    modes = {"--self-test", "--verify-frozen-context"}
    allowed = {
        "--source-sha256",
        "--protocol-sha256",
        "--contract-sha256",
        "--graph-source-sha256",
        "--graph-inputs-sha256",
        "--graph-summary-sha256",
        "--graph-svg-sha256",
    }
    position = 0
    while position < len(arguments):
        name = arguments[position]
        if name in modes:
            require("mode" not in result, "reject repeated guard operation")
            result["mode"] = name
            position += 1
            continue
        require(
            name in allowed
            and name not in result
            and position + 1 < len(arguments),
            "reject unpinned, repeated, or omitted guard authority",
        )
        result[name] = sha256_pin(arguments[position + 1], name)
        position += 2
    require(
        result.get("mode") in modes and len(result) == 8,
        "require one source mode and all seven exact operational owner pins",
    )
    return result


def strict_document(raw: bytes, label: str) -> dict:
    document = JsonReader(raw).parse()
    require(type(document) is dict, "require one complete JSON owner: " + label)
    assert isinstance(document, dict)
    return document


def validate_contract(contract: object, options: dict, graph: dict, p0: dict) -> None:
    require(
        type(contract) is dict and set(contract) == CONTRACT_KEYS,
        "reject missing or substituted complete operational guard evidence",
    )
    assert isinstance(contract, dict)
    require(
        contract["schema"]
        == "rebar-owned-candidate-runtime-independence-v2-source-freeze"
        and contract["version"] == 2
        and contract["status"]
        == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
        and contract["runtime_non_delegation"] == "NOT ESTABLISHED"
        and contract["holdout"] == "NOT OPENED"
        and contract["performance"] == "NOT MEASURED"
        and contract["memory"] == "NOT MEASURED"
        and contract["undefined_behavior"] == "NOT MEASURED"
        and contract["qualified_candidate_count"] == 0
        and contract["winner_selected"] is False,
        "do not claim candidate matching, qualification, or runtime independence",
    )
    for role, relative in (("source", SELF), ("protocol", PROTOCOL)):
        owner = contract[role]
        require(
            type(owner) is dict
            and owner["path"] == relative
            and owner["sha256"] == options["--" + role + "-sha256"]
            and owner["device"] == 2064
            and owner["mode"] == "0600"
            and owner["nlink"] == 1,
            "reject substituted V2 guard " + role,
        )
    current = contract["current_graph"]
    require(
        type(current) is dict
        and current["version"] == 74
        and current["authenticated_evidence_owner_lower_bound"] == 246
        and current["authenticated_history_reference_lower_bound"] == 251
        and type(current["owners"]) is list
        and len(current["owners"]) == 4,
        "preserve every owner of the current genuinely pushed V74 graph",
    )
    indexed = {owner["path"]: owner for owner in current["owners"]}
    require(
        set(indexed) == {item[0] for item in V74.values()},
        "reject an omitted or fabricated published graph owner",
    )
    for role, item in V74.items():
        require(
            indexed[item[0]] == owner_identity(item)
            and options["--graph-" + role + "-sha256"] == item[1],
            "reject stale or substituted complete V74 " + role,
        )
    predecessor = contract["predecessor_v1"]
    require(
        type(predecessor) is dict
        and set(predecessor)
        == {"version", "status", "runtime_non_delegation", "owners"}
        and predecessor["version"] == 1
        and predecessor["status"]
        == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
        and predecessor["runtime_non_delegation"] == "NOT ESTABLISHED"
        and predecessor["owners"]
        == {role: owner_identity(item) for role, item in V1.items()},
        "preserve every immutable first guard owner and its unexecuted result",
    )
    require(
        contract["family_bridge_policy"] == FAMILY_BRIDGES
        and contract["first_party_candidate_families"]
        == {
            family: spec["candidate_module"]
            for family, spec in FAMILY_BRIDGES.items()
        },
        "allow exactly six first-party engines and each engine's own bridge",
    )
    readiness = contract["phase1_v4_readiness"]
    require(
        readiness
        == {
            "status": "PASS",
            "contract_sha256": P0["contract"][1],
            "original_case_execution_denominator": 31237,
            "original_suite_count": 13,
            "original_obligation_count": 73,
            "named_private_waiver_count": 13,
            "separate_supplemental_case_count": 8244,
        }
        and p0["status"] == "PASS"
        and p0["original_case_execution_denominator"] == 31237
        and p0["original_suite_count"] == 13
        and p0["original_obligation_count"] == 73
        and p0["original_named_private_waiver_count"] == 13,
        "never change, merge, waive, or weaken the exact original P0 suite",
    )
    expected_native = {
        "family": "rust",
        "build_version": 19,
        "build_receipt": owner_identity(BUILD_RECEIPT),
        "root_provenance_receipt": owner_identity(ROOT_RECEIPT),
        "root_device": 2049,
        "root_inode": 11673243,
        "actual_compiler_process_count": 28,
        "attested_bridge_sha256": (
            "7127b1b5d6e50947e34f39e6c33ff76e71a9f753473c6d5eac0f1bdf6b0e66d4"
        ),
        "attested_bridge_bytes": 148832,
        "attested_engine_sha256": (
            "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
        ),
        "attested_engine_bytes": 658344,
        "native_load_policy": "ONLY SELECTED FAMILY AND EXACT ATTESTED ARTIFACT",
        "source_mode_native_root_opens": 0,
        "source_mode_native_libraries_loaded": 0,
        "candidate_matching": "NOT RUN",
    }
    require(
        contract["native_provenance"] == expected_native,
        "preserve complete actual first-party native provenance without activation",
    )
    expected_nested = {
        "suite": "subinterpreter_v2",
        **{role: owner_identity(item) for role, item in NESTED.items()},
        "original_case_count": 128,
        "expected_interpreters_created": 11,
        "expected_interpreters_destroyed": 11,
        "expected_case_interpreter_exec_calls": 394,
        "require_child_guard_before_candidate_import": True,
        "unrestricted_creation": False,
        "actual_interpreters_created": 0,
        "actual_interpreters_destroyed": 0,
        "actual_case_interpreter_exec_calls": 0,
        "actual_child_guards_installed": 0,
        "candidate_status": "NOT RUN",
    }
    require(
        contract["subinterpreter_bootstrap"] == expected_nested,
        "require separately guarded original children without claiming execution",
    )
    exceptions = contract["original_public_test_exceptions"]
    require(
        type(exceptions) is dict
        and exceptions["data_only_MAXGROUPS"] == 1073741823
        and exceptions["MAXGROUPS_module"] == "re._constants"
        and exceptions["only_fork_case"]
        == "ReTests.test_regression_gh94675"
        and exceptions["only_correctness_clock_case"]
        == "ReTests.test_search_anchor_at_beginning"
        and exceptions["locale_fixture_origin"]
        == "SEPARATE ORACLE PROCESS ONLY"
        and exceptions["nested_interpreters"]
        == "EACH MUST INSTALL AN INDEPENDENT GUARD"
        and exceptions["fork_scope"]
        == {
            "case": "ReTests.test_regression_gh94675",
            "event": "os.fork",
            "max_events": 1,
            "scope": "EXACT ORIGINAL PUBLIC CASE",
            "child_guard_required": True,
        }
        and exceptions["correctness_clock_scope"]
        == {
            "case": "ReTests.test_search_anchor_at_beginning",
            "event": "rebar.correctness.clock",
            "max_events": 2,
            "scope": "EXACT ORIGINAL PUBLIC CASE",
            "benchmark_measurement": False,
        },
        "permit only the exact named original correctness exceptions",
    )
    require(
        contract["supplemental_obligations"]
        == {
            "callable_signature_case_count": 50,
            "candidate_supplemental_status": "NOT RUN",
            "large_input_original_cases": "NOT RUN",
            "separate_supplemental_case_count": 8244,
            "supplemental_merged_into_original": False,
        },
        "do not merge or invent supplemental, signature, or large-input results",
    )
    policy = contract["runtime_isolation_policy"]
    require(
        policy
        == {
            "bootstrap": "CPython -I -B -S; audit hook before candidate import",
            "candidate_alias": "sys.modules['re'] is the attested candidate",
            "stdlib_re_engine": "FORBIDDEN",
            "stdlib_sre_engine": "FORBIDDEN",
            "external_regex_package": "FORBIDDEN",
            "cross_candidate_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "native_loader": "ONLY INDIVIDUALLY ATTESTED FAMILY ARTIFACTS",
            "guard_installed_before_candidate_import": True,
        },
        "reject every fallback, external engine, sibling bridge, or weak startup",
    )
    effects = contract["source_only_effects"]
    require(
        type(effects) is dict
        and set(effects) == EFFECT_KEYS
        and all(type(value) is int and value == 0 for value in effects.values()),
        "reject source-mode candidate, native, root, process, clock, or holdout",
    )
    require(
        graph["version"] == 74
        and graph["authenticated_evidence_owner_lower_bound"] == 246
        and graph["authenticated_history_reference_lower_bound"] == 251
        and graph["actual_rust_semantic_mismatch_count"] == 1440
        and graph["actual_rust_verified_passing_case_count"] == 14853
        and graph["actual_c_semantic_mismatch_count"] == 1230
        and graph["actual_c_verified_passing_case_count"] == 7325
        and graph["actual_zig_semantic_mismatch_count"] == 1764
        and graph["rust_native_build_v19_status"] == "PASS"
        and graph["rust_native_build_v19_actual_compiler_process_count"] == 28
        and graph["runtime_no_delegation"] == "NOT ESTABLISHED"
        and graph["qualified_candidate_count"] == 0
        and graph["final_holdout_opened"] is False
        and graph["performance"] == "NOT MEASURED"
        and len(
            graph["actual_complete_rust_campaign"][
                "complete_independently_authenticated_suite_results"
            ]
        )
        == 13
        and len(
            graph["actual_complete_rust_campaign"][
                "earliest_genuine_mismatch_witnesses"
            ]
        )
        == 6,
        "preserve every actual candidate failure and every original witness",
    )


def verify_child_contract(
    source_sha256: str, protocol_sha256: str, contract_sha256: str
) -> None:
    options = {
        "--source-sha256": sha256_pin(source_sha256, "child guard source"),
        "--protocol-sha256": sha256_pin(protocol_sha256, "child guard protocol"),
        "--contract-sha256": sha256_pin(contract_sha256, "child guard contract"),
        **{
            "--graph-" + role + "-sha256": item[1]
            for role, item in V74.items()
        },
    }
    own = dynamic_owner(SELF, source_sha256, "child source")
    protocol = dynamic_owner(PROTOCOL, protocol_sha256, "child protocol")
    document = dynamic_owner(CONTRACT, contract_sha256, "child contract")
    source_raw = read_owner(own, "complete guarded child source")
    require(
        hashlib.sha256(source_raw).hexdigest() == source_sha256,
        "reject a substituted child runtime guard",
    )
    read_owner(protocol, "complete guarded child protocol")
    raw = read_owner(document, "complete guarded child contract")
    parsed = strict_document(raw, "guarded child contract")
    require(canonical(parsed) == raw, "reject noncanonical guarded child policy")
    graph = strict_document(
        read_owner(V74["summary"], "actual current graph"), "actual current graph"
    )
    p0 = strict_document(
        read_owner(P0["contract"], "actual original P0"), "actual original P0"
    )
    validate_contract(parsed, options, graph, p0)


def denied(policy: RuntimePolicy, operation: object, label: str) -> int:
    try:
        require(callable(operation), "require one real hostile operation")
        operation()
    except (
        BootstrapError,
        GuardError,
        ImportError,
        ModuleNotFoundError,
        OSError,
        ValueError,
        TypeError,
    ):
        return 1
    raise BootstrapError("accepted prohibited operational guard control: " + label)


def hostile_controls(policy: RuntimePolicy, options: dict) -> int:
    count = 0
    forbidden = (
        "re",
        "_sre",
        "re._compiler",
        "re._parser",
        "re._constants",
        "sre_compile",
        "sre_parse",
        "sre_constants",
        "regex",
        "regex._regex",
        "re2",
        "pcre",
        "pcre2",
        "oniguruma",
        "onig",
        "hyperscan",
    )
    for name in forbidden:
        count += denied(policy, lambda item=name: policy.check_import(item), name)
    for spec in FAMILY_BRIDGES.values():
        for name in (spec["candidate_module"], spec["owned_bridge_module"]):
            count += denied(
                policy,
                lambda item=name: policy.check_import(item),
                "unprepared first-party candidate " + name,
            )
    for name in ("_sre", "regex", "re._compiler"):
        count += denied(
            policy,
            lambda item=name: __import__(item),
            "physically imported forbidden engine " + name,
        )
    for event in DENIED_EVENTS:
        count += denied(
            policy,
            lambda item=event: sys.audit(item, "forbidden"),
            "physical denied event " + event,
        )
    for event in ("os.fork", "rebar.correctness.clock", "_interpreters.create"):
        count += denied(
            policy,
            lambda item=event: sys.audit(item, 999),
            "unscoped original public exception " + event,
        )
    count += denied(
        policy,
        lambda: sys.audit("_interpreters.exec", 999, "unguarded"),
        "unregistered child bootstrap",
    )
    count += denied(
        policy,
        lambda: policy.prepare_family(
            "rust", bridge_owner={}, engine_owner={}
        ),
        "unattested synthetic selected bridge",
    )
    require(
        "re" not in sys.modules
        and "_sre" not in sys.modules
        and not any(name.startswith("candidates.") for name in sys.modules),
        "do not import a matcher during hostile source-only controls",
    )
    policy.prepared_family = "rust"
    policy.selected_family = FAMILY_BRIDGES["rust"]["candidate_module"]
    policy.approved_bridge_module = FAMILY_BRIDGES["rust"][
        "owned_bridge_module"
    ]
    policy.bridge_owner = {
        "family": "rust",
        "role": "bridge",
        "relative": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "absolute_path": ROOT
        + "/candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "sha256": "1" * 64,
        "bytes": 148832,
        "device": 2064,
        "inode": 1,
        "mode": 0o600,
        "nlink": 1,
    }
    policy.engine_owner = {
        "family": "rust",
        "role": "engine",
        "relative": "candidates/_rust_engine.so",
        "absolute_path": ROOT + "/candidates/_rust_engine.so",
        "sha256": "2" * 64,
        "bytes": 658344,
        "device": 2064,
        "inode": 2,
        "mode": 0o600,
        "nlink": 1,
    }
    policy.check_import("candidates")
    policy.check_import(FAMILY_BRIDGES["rust"]["candidate_module"])
    policy.check_import(FAMILY_BRIDGES["rust"]["owned_bridge_module"])
    for family, spec in FAMILY_BRIDGES.items():
        if family != "rust":
            for name in (spec["candidate_module"], spec["owned_bridge_module"]):
                count += denied(
                    policy,
                    lambda item=name: policy.check_import(item),
                    "cross-family engine or bridge " + name,
                )
    fake = types.ModuleType(FAMILY_BRIDGES["rust"]["candidate_module"])
    policy.bind_selected(fake, "rust")
    require(
        sys.modules.get("re") is fake
        and sys.modules.get("re._constants") is policy.constants
        and getattr(policy.constants, "MAXGROUPS", None) == MAXGROUPS
        and __import__("re") is fake,
        "bind only the synthetic selected alias and exact data-only MAXGROUPS",
    )
    original = sys.modules["re"]
    sys.modules["re"] = types.ModuleType("_hostile_replacement")
    count += denied(policy, policy.check_modules, "substituted public alias")
    sys.modules["re"] = original
    assert policy.constants is not None
    policy.constants.MAXGROUPS = MAXGROUPS + 1
    count += denied(
        policy,
        lambda: policy.check_import("re._constants"),
        "substituted data-only public constant",
    )
    policy.constants.MAXGROUPS = MAXGROUPS
    count += denied(
        policy,
        lambda: policy.begin_subinterpreters(suite="incorrect_suite"),
        "unrestricted nested interpreter suite",
    )
    policy.begin_subinterpreters()
    count += denied(
        policy,
        lambda: sys.audit("_interpreters.exec", 999, "unguarded"),
        "unregistered nested interpreter",
    )
    challenge = "3" * 64
    pins = {
        "family": "rust",
        "source_sha256": options["--source-sha256"],
        "protocol_sha256": options["--protocol-sha256"],
        "contract_sha256": options["--contract-sha256"],
        "bridge_owner": policy.bridge_owner,
        "engine_owner": policy.engine_owner,
        "owner": "A",
        "attestation_fd": 999,
        "challenge": challenge,
    }
    forged_child = types.SimpleNamespace(
        id=1729,
        exec=lambda source: None,
        close=lambda: None,
    )
    count += denied(
        policy,
        lambda: policy.register_child_bootstrap(
            forged_child, "pass", read_fd=998, **pins
        ),
        "child registered before a real accounted creation",
    )
    sys.audit("_interpreters.create", 1729)
    count += denied(
        policy,
        lambda: policy.register_child_bootstrap(
            forged_child, "pass", read_fd=998, **pins
        ),
        "arbitrary pass accepted as child guard bootstrap",
    )
    canonical_source = child_bootstrap_source(**pins)
    count += denied(
        policy,
        lambda: policy.register_child_bootstrap(
            forged_child, canonical_source, read_fd=998, **pins
        ),
        "synthetic audit event forged a live public child and pipe",
    )
    count += denied(
        policy,
        lambda: sys.audit("_interpreters.exec", 1729, "pass"),
        "substituted first child execution",
    )
    count += denied(
        policy,
        lambda: policy.confirm_child_guard(forged_child),
        "forged positive child guard handshake",
    )
    count += denied(
        policy,
        lambda: sys.audit("_interpreters.exec", 1729, canonical_source),
        "canonical text without a real registered child or pipe",
    )
    count += denied(
        policy,
        policy.end_subinterpreters,
        "incomplete or unconfirmed eleven-child interpreter lifecycle",
    )
    policy.interpreter_suite = None
    policy.child_bootstraps = {}
    count += denied(
        policy,
        lambda: policy.begin_fork_case("incorrect.original.case"),
        "wrong original public fork case",
    )
    policy.begin_fork_case("ReTests.test_regression_gh94675")
    sys.audit("os.fork")
    count += denied(policy, lambda: sys.audit("os.fork"), "second public fork")
    policy.end_fork_case()
    count += denied(
        policy,
        lambda: policy.begin_correctness_clock("incorrect.original.case"),
        "wrong original correctness clock",
    )
    policy.begin_correctness_clock("ReTests.test_search_anchor_at_beginning")
    sys.audit("rebar.correctness.clock")
    sys.audit("rebar.correctness.clock")
    count += denied(
        policy,
        lambda: sys.audit("rebar.correctness.clock"),
        "third original correctness clock",
    )
    policy.end_correctness_clock()
    del sys.modules["re._constants"]
    del sys.modules["re"]
    policy.constants = None
    policy.selected = None
    policy.selected_family = None
    policy.approved_bridge_module = None
    policy.prepared_family = None
    policy.bridge_owner = None
    policy.engine_owner = None
    policy.check_modules()
    require(
        "re" not in sys.modules
        and "_sre" not in sys.modules
        and count >= 55,
        "require independently denied engines, bridges, native events, and children",
    )
    return count


def source_run(options: dict) -> dict:
    require(
        sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.flags.dont_write_bytecode == 1
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and "re" not in sys.modules
        and "_sre" not in sys.modules,
        "require exact clean CPython 3.14.6 -I -B -S before matcher isolation",
    )
    read_owner(GOAL, "immutable original experiment objective")
    for role, item in V1.items():
        read_owner(item, "immutable first-generation guard " + role)
    for role, item in P0.items():
        read_owner(item, "complete reference P0 " + role)
    for role, item in V74.items():
        require(
            options["--graph-" + role + "-sha256"] == item[1],
            "require the actual pushed V74 graph " + role,
        )
        read_owner(item, "actual complete V74 graph " + role)
    for role, item in NESTED.items():
        read_owner(item, "actual original nested interpreter " + role)
    build = strict_document(
        read_owner(BUILD_RECEIPT, "small attested V19 build receipt"),
        "small attested V19 build receipt",
    )
    root = strict_document(
        read_owner(ROOT_RECEIPT, "small attested V19 root receipt"),
        "small attested V19 root receipt",
    )
    require(
        build["status"] == "PASS"
        and build["actual_compiler_process_count"] == 28
        and root["status"] == "PASS"
        and root["root"]["device"] == 2049
        and root["root"]["inode"] == 11673243
        and root["native_libraries_loaded"] == 0,
        "authenticate exact first-party Rust receipts without opening its root",
    )
    source = dynamic_owner(SELF, options["--source-sha256"], "source")
    protocol = dynamic_owner(PROTOCOL, options["--protocol-sha256"], "protocol")
    document = dynamic_owner(CONTRACT, options["--contract-sha256"], "contract")
    read_owner(source, "complete exact guard V2 source")
    read_owner(protocol, "complete exact guard V2 protocol")
    raw = read_owner(document, "complete exact guard V2 contract")
    contract = strict_document(raw, "complete operational V2 policy")
    require(canonical(contract) == raw, "reject noncanonical V2 machine policy")
    graph = strict_document(
        read_owner(V74["summary"], "full current V74 summary"),
        "full current V74 summary",
    )
    p0 = strict_document(
        read_owner(P0["contract"], "full original P0 contract"),
        "full original P0 contract",
    )
    validate_contract(contract, options, graph, p0)
    policy = RuntimePolicy()
    policy.install()
    rejected = hostile_controls(policy, options)
    return {
        "schema": "rebar-owned-candidate-runtime-independence-v2-source-"
        + (
            "self-test"
            if options["mode"] == "--self-test"
            else "frozen-context"
        ),
        "version": 2,
        "status": "PASS",
        "source_sha256": options["--source-sha256"],
        "protocol_sha256": options["--protocol-sha256"],
        "contract_sha256": options["--contract-sha256"],
        "actual_current_graph_version": 74,
        "authenticated_evidence_owner_lower_bound": 246,
        "authenticated_history_reference_lower_bound": 251,
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "separate_supplemental_case_count": 8244,
        "candidate_family_count": 6,
        "owned_bridge_policy_count": 6,
        "rejected_hostile_control_count": rejected,
        "physically_blocked_controls": dict(policy.blocked),
        "synthetic_data_only_MAXGROUPS_control": MAXGROUPS,
        "synthetic_correctness_clock_event_count": 2,
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
        "actual_interpreters_created": 0,
        "actual_child_guards_installed": 0,
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
        sys.stderr.write("operational candidate guard rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
