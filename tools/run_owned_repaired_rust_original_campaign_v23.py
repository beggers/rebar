#!/usr/bin/env python3
"""Freeze the next honest original Rust campaign without running a candidate.

The complete corrected V2 bridge and its native build do not exist as pinned
public owners. Actual run, worker, and recovery modes therefore fail before
opening any file. Source modes authenticate only exactly owned public
plaintext under a fresh, deny-default physical wall.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("a public-only source freeze must not import a matcher")

import _io
import builtins
import hashlib
import io
import os
import stat
import time
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
DEVICE = 2064
SOURCE = "tools/run_owned_repaired_rust_original_campaign_v23.py"
PROTOCOL = "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V23.md"
CONTRACT = "oracle/phase2/repaired-rust-original-campaign-v23.json"
SCHEMA = "rebar-owned-repaired-rust-original-campaign-v23"
VERSION = 23
NOT_MEASURED = "NOT MEASURED"
MAX_OWNER_BYTES = 1_048_576
GOAL_SHA = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
ACTUAL_SHA = "7013c42f6309d94e094dd89cc8e9f24fe245c0cba5ca4791d35ffe5fa2b7dad7"
A0_SHA = "a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a"
F9_SHA = "f9bd2d3c8406e4b2c703ce96f42964ee15941611e22447b12acc9b54fac98055"
BLOCKED_ACTUAL = (
    "actual V23 rejected: corrected V2 native build and authenticated "
    "root receipt not yet available"
)

# Every owner is complete public plaintext. In particular, none is a
# candidate, native artifact, private build root, archive, or holdout.
CAPTURE_V2_OWNERS = (
    ("capture_v2_source", "tools/apply_owned_rust_capture_shape_semantics_v2.py",
     "e285d0c39950f7ffc5929f0c5f5a0708b8c3e8878b655255cb29e1b0725233c2",
     83214, 431144),
    ("capture_v2_protocol",
     "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V2.md",
     "999e8cdf9f7a7b0fbaca67759d8c0a13f49c7ca10c753539010d11681a1aaa8d",
     5289, 525411),
    ("capture_v2_contract",
     "oracle/phase2/rust-capture-shape-semantics-v2.json",
     "cafb121e38ed738c51d30978a22ddf788eafd729b2a145a8f3564ea97412e673",
     14661, 525421),
)

PUBLIC_OWNERS = (
    ("goal", "GOAL.md", GOAL_SHA, 3756, 31364044),
    ("original_oracle", "oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
     34875, 524713),
    ("supplemental_oracle",
     "oracle/phase1/p0-differential-fuzz-reference-v3.json",
     "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff",
     5288, 525082),
    ("substitution_oracle",
     "tools/independent_substitution_buffer_semantics_v2.py",
     "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573",
     317541, 432058),
    ("shape_oracle", "tools/independent_shape_changing_buffer_semantics_v2.py",
     "0262807f793a818307f2c8c6ecfd84bf970264a6ef5d656acf30c9d3606f0e2c",
     137527, 432070),
    ("semantic_v1_source",
     "tools/apply_owned_rust_capture_shape_semantics_v1.py",
     "d3213d43bd09b1216f618a3a14472ff0fe290b13852c403a0d1c0ecd8a0408b2",
     53555, 431487),
    ("semantic_v1_protocol",
     "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V1.md",
     "edbeb811483b39f094dbead1237e912e20af07609474c7256db75fce45887f54",
     4883, 525377),
    ("semantic_v1_contract",
     "oracle/phase2/rust-capture-shape-semantics-v1.json",
     "5e262226341a7554943a7ae21fad616009555231e855ea23b7eb715c94317b63",
     6524, 525378),
    ("native_v22_source",
     "tools/reproduce_owned_rust_capture_shape_semantics_source_build_v22.py",
     "0ce73b2168c5143e2f95256d454ffe131bdc2c5736d91176509cc651819f58d4",
     65949, 430180),
    ("native_v22_protocol",
     "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-SOURCE-BUILD-V22.md",
     "31467e166ecc83ef49c43ca51bb97b7699a696068a4267dcd013c64078b3050a",
     5372, 524832),
    ("native_v22_contract",
     "oracle/phase2/rust-capture-shape-semantics-source-build-v22.json",
     "b43f1a1f5f7c5c72990f4d8c3c9e321e53d7970b3ceaa4b0afdb82a08fa4b308",
     10067, 524833),
    ("native_v22_publication",
     "oracle/phase2/evidence/native-source-build-v22-rust-"
     "phase2-v22-rust-capture-shape-root-provenance-publication-receipt.json",
     "851c7c6fd8546ee59f8107ea3687d0150d0ada0bf6764b040019b083776701b2",
     3500, 524926),
    ("native_v22_root_receipt",
     "oracle/phase2/evidence/native-source-build-v22-rust-"
     "phase2-v22-rust-capture-shape-root-provenance-root-provenance-receipt.json",
     "93cb91b186faaf32522a11caeb564829cd4504751bc88aebf955c36d19e572a3",
     5607, 524930),
    ("campaign_v22_source", "tools/run_owned_repaired_rust_original_campaign_v22.py",
     "e88f242835781e9b70efa18e68a7b06b0b9368e91320ed596995ef0e16370c61",
     61761, 430995),
    ("campaign_v22_protocol",
     "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V22.md",
     "c6a2a5db9c9c27974c29af01b3d7f7042bae73e254c638fe27813505ef11f396",
     6038, 525307),
    ("campaign_v22_contract",
     "oracle/phase2/repaired-rust-original-campaign-v22.json",
     "f1c021049e4bb173be8d47339920354e02c8c0194aead877b8474a128b5e158a",
     42352, 525314),
    ("prior_actual_v20",
     "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
     "phase2-v21-rust-captured-findall-root-provenance-"
     "original-p0-v20-failures-publication-receipt.json",
     "ad9e04aa3595a4e44a5bbc12b6413fde08b926c9e73b23aa6b3eedacd35e4a36",
     45973, 524829),
    ("actual_v22",
     "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
     "phase2-v22-rust-capture-shape-root-provenance-"
     "original-p0-v22-failures-publication-receipt.json",
     ACTUAL_SHA, 47336, 525371),
)

GUARD_OWNERS = (
    ("guard_v3_source", "tools/verify_owned_candidate_runtime_independence_v3.py",
     "03f051e428ee31bb671d8ced82f02d7a9fe3520f24191aba78d2e8a0697202c2",
     59765, 430856),
    ("guard_v3_protocol", "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V3.md",
     "d3437b642d322ccccf12851981555cb596ff7f9c5a12e0a6a389d6b80b5a068a",
     5297, 525096),
    ("guard_v3_contract", "oracle/phase2/candidate-runtime-independence-v3.json",
     "31e9a5d2754b5b4b273d4fc30d6a27967e495b57684fdd1e9306bbac3b2caaa7",
     9157, 525114),
    ("guard_v2_source", "tools/verify_owned_candidate_runtime_independence_v2.py",
     "f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a",
     67097, 431371),
    ("guard_v2_protocol", "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md",
     "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c",
     4437, 524886),
    ("guard_v2_contract", "oracle/phase2/candidate-runtime-independence-v2.json",
     "813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473",
     7671, 524887),
    ("producer_v5_source", "tools/run_owned_six_family_original_p0_producer_v5.py",
     "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538",
     102286, 431370),
    ("producer_v5_protocol", "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md",
     "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4",
     5270, 524884),
    ("producer_v5_contract", "oracle/phase2/six-family-p0-producer-v5.json",
     "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53",
     21036, 524885),
)

STATIC_OWNERS = CAPTURE_V2_OWNERS + PUBLIC_OWNERS + GUARD_OWNERS
SOURCE_MODES = ("--render-contract", "--self-test", "--verify-frozen-context")
ACTUAL_MODES = ("--run", "--worker", "--recover")
NATIVE_OWNER_FIELDS = (
    "absolute_path", "bytes", "device", "family", "file_name", "inode",
    "mode", "native_loaded", "nlink", "relative", "role", "sha256",
    "size_bytes", "uid",
)
GUARD_KEYS = frozenset((
    "schema", "version", "status", "goal_sha256", "source", "protocol",
    "immutable_predecessor_v2", "immutable_producer_v5", "pinned_cpython",
    "phase_one", "first_party_candidate_families", "family_bridge_policy",
    "native_owner_policy", "subinterpreter_bootstrap", "source_only_effects",
    "runtime_isolation_policy", "candidate_matching", "runtime_non_delegation",
    "holdout", "performance", "memory", "undefined_behavior",
    "qualified_candidate_count", "winner_selected",
))


class FreezeError(Exception):
    """A public owner, correctness boundary, or activation gate was changed."""


def require(value: object, label: str) -> None:
    if value is not True:
        raise FreezeError(label)


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only exact complete public bytes")
    return hashlib.sha256(raw).hexdigest()


def digest_pin(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require one complete independent SHA-256: " + label)
    assert isinstance(value, str)
    return value


def no_matching_imports() -> None:
    roots = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
             "ctypes", "candidates", "rebar", "subprocess", "socket",
             "concurrent.interpreters")
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in roots),
            "reject matching engines, candidates, native loading, and network")


class PublicSourceWall:
    """Allow only exact canonical public plaintext and tracked descriptors."""

    def __init__(self) -> None:
        relatives = (SOURCE, PROTOCOL, CONTRACT) + tuple(
            row[1] for row in STATIC_OWNERS
        )
        require(len(relatives) == len(frozenset(relatives)),
                "reject duplicate or aliased V23 public-only owners")
        self.allowed = frozenset(ROOT + "/" + path for path in relatives)
        self.blocked: dict[str, int] = {}
        self.live: set[int] = set()
        self.installed = False
        self.error_type: type[Exception] = FreezeError
        self.native_open = os.open
        self.native_read = os.read
        self.native_fstat = os.fstat
        self.native_close = os.close

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise self.error_type(
            "V23 public-only physical wall rejected " + category,
        )

    def approved(self, path: object) -> bool:
        return (
            type(path) is str
            and path.startswith(ROOT + "/")
            and path == os.path.normpath(path)
            and not any(part in (".", "..") for part in path.split("/"))
            and path in self.allowed
            and not path.endswith((".so", ".gz"))
            and not path.startswith(ROOT + "/candidates/")
            and not path.startswith(ROOT + "/oracle/phase3/")
            and "holdout" not in path.lower()
            and "benchmark" not in path.lower()
        )

    def audit(self, event: str, args: tuple) -> None:
        if event == "open":
            path = args[0] if args else None
            mode = args[1] if len(args) > 1 else None
            flags = args[2] if len(args) > 2 else None
            destructive = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                           | os.O_APPEND | getattr(os, "O_TMPFILE", 0))
            if (
                not self.approved(path)
                or type(flags) is not int
                or flags & destructive
                or not flags & getattr(os, "O_NOFOLLOW", 0)
                or type(mode) is str and any(item in mode for item in "wax+")
            ):
                self.deny("unowned-direct-file-open")
            return
        if event in ("exec", "compile"):
            value = args[0] if args else None
            filename = (
                getattr(value, "co_filename", None)
                if event == "exec"
                else args[1] if len(args) > 1 else None
            )
            if not self.approved(filename):
                self.deny("unowned-dynamic-execution")
            return
        if (
            event == "import"
            or event == "marshal.loads"
            or event in (
                "os.system", "os.fork", "os.posix_spawn", "os.posix_spawnp",
                "os.rename", "os.replace", "os.remove", "os.unlink",
                "os.mkdir", "os.rmdir", "os.chmod", "os.chown",
                "os.urandom", "os.getrandom", "_interpreters.create",
                "_interpreters.exec", "cpython.PyInterpreterState_New",
            )
            or event.startswith((
                "subprocess.", "socket.", "ctypes.", "threading.",
                "multiprocessing.", "tempfile.", "time.", "os.exec",
                "os.spawn", "random.",
            ))
        ):
            self.deny("import-process-native-network-clock-or-mutation")

    def _forbidden(self, category: str):
        def blocked(*_args: object, **_kwargs: object) -> object:
            self.deny(category)
        return blocked

    def guarded_open(
        self, path: object, flags: object, mode: int = 0o777,
        *, dir_fd: object = None,
    ) -> int:
        destructive = (
            os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
            | getattr(os, "O_TMPFILE", 0) | getattr(os, "O_DIRECTORY", 0)
        )
        if (
            not self.approved(path)
            or type(flags) is not int
            or flags & destructive
            or not flags & getattr(os, "O_NOFOLLOW", 0)
            or dir_fd is not None
        ):
            self.deny("unowned-os-open-or-directory-descriptor")
        assert isinstance(path, str)
        descriptor = self.native_open(path, flags, mode)
        require(type(descriptor) is int and descriptor >= 0,
                "require one genuine approved public descriptor")
        require(descriptor not in self.live,
                "reject a reused live public descriptor")
        self.live.add(descriptor)
        return descriptor

    def guarded_read(self, descriptor: object, count: object) -> bytes:
        if (
            type(descriptor) is not int or descriptor not in self.live
            or type(count) is not int or count < 0 or count > MAX_OWNER_BYTES
        ):
            self.deny("unowned-or-unbounded-direct-descriptor-read")
        assert isinstance(descriptor, int) and isinstance(count, int)
        return self.native_read(descriptor, count)

    def guarded_fstat(self, descriptor: object) -> os.stat_result:
        if type(descriptor) is not int or descriptor not in self.live:
            self.deny("unowned-direct-descriptor-stat")
        assert isinstance(descriptor, int)
        return self.native_fstat(descriptor)

    def guarded_close(self, descriptor: object) -> None:
        if type(descriptor) is not int or descriptor not in self.live:
            self.deny("unowned-direct-descriptor-close")
        assert isinstance(descriptor, int)
        self.live.remove(descriptor)
        self.native_close(descriptor)

    def install(self) -> None:
        require(self.installed is False,
                "reject a reused V23 public-only physical wall")
        sys.addaudithook(self.audit)
        builtins.open = self._forbidden("builtins-open")
        _io.open = self._forbidden("direct-_io-open")
        _io.FileIO = self._forbidden("direct-_io-fileio")
        io.open = self._forbidden("direct-io-open")
        io.FileIO = self._forbidden("direct-io-fileio")
        if hasattr(_io, "open_code"):
            _io.open_code = self._forbidden("direct-_io-open-code")
        if hasattr(io, "open_code"):
            io.open_code = self._forbidden("direct-io-open-code")
        os.open = self.guarded_open
        os.read = self.guarded_read
        os.fstat = self.guarded_fstat
        os.close = self.guarded_close
        for name in (
            "fdopen", "dup", "dup2", "stat", "lstat", "readlink",
            "listdir", "scandir", "walk", "fwalk", "access", "fork",
            "posix_spawn", "posix_spawnp", "system", "mkdir", "makedirs",
            "remove", "unlink", "rename", "replace", "rmdir", "chmod",
            "chown", "urandom", "getrandom",
        ):
            if hasattr(os, name):
                setattr(os, name, self._forbidden("direct-os-" + name))
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
            "perf_counter_ns", "process_time", "process_time_ns",
            "thread_time", "thread_time_ns", "clock_gettime",
            "clock_gettime_ns", "sleep",
        ):
            if hasattr(time, name):
                setattr(time, name, self._forbidden("clock-" + name))
        self.installed = True


def secure_owner(wall: PublicSourceWall, row: tuple) -> bytes:
    require(type(row) is tuple and len(row) == 5,
            "require one complete independently pinned V23 public owner")
    role, relative, expected, count, inode = row
    require(
        type(role) is str and type(relative) is str
        and not relative.startswith("/")
        and ".." not in relative.split("/")
        and type(count) is int and 0 < count <= MAX_OWNER_BYTES
        and type(inode) is int and inode > 0,
        "reject an unbounded or non-public V23 evidence owner",
    )
    digest_pin(expected, relative)
    absolute = ROOT + "/" + relative
    require(wall.installed and wall.approved(absolute),
            "install the exact V23 wall before the first predecessor byte")
    flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(absolute, flags)
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode)
            and stat.S_IMODE(before.st_mode) == 0o600
            and before.st_dev == DEVICE
            and before.st_ino == inode
            and before.st_size == count
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1,
            "reject a substituted whole public V23 owner: " + role,
        )
        left = count
        pieces: list[bytes] = []
        while left:
            piece = os.read(descriptor, min(left, 65536))
            require(type(piece) is bytes and bool(piece),
                    "reject truncated complete public bytes: " + role)
            pieces.append(piece)
            left -= len(piece)
        require(os.read(descriptor, 1) == b"",
                "reject expanded complete public bytes: " + role)
        after = os.fstat(descriptor)
        require(all(
            getattr(before, item) == getattr(after, item)
            for item in (
                "st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns",
                "st_nlink",
            )
        ), "reject concurrently modified V23 public bytes: " + role)
        raw = b"".join(pieces)
        require(sha256(raw) == expected,
                "reject changed complete V23 public owner: " + role)
        return raw
    finally:
        os.close(descriptor)


def dynamic_owner(
    wall: PublicSourceWall, role: str, relative: str, fingerprint: str,
) -> tuple:
    require(relative in (SOURCE, PROTOCOL, CONTRACT),
            "reject an unowned dynamic V23 source-freeze path")
    digest_pin(fingerprint, relative)
    absolute = ROOT + "/" + relative
    require(wall.installed and wall.approved(absolute),
            "reject a dynamic owner before the V23 public wall")
    flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(absolute, flags)
    try:
        found = os.fstat(descriptor)
        require(
            stat.S_ISREG(found.st_mode)
            and stat.S_IMODE(found.st_mode) == 0o600
            and found.st_dev == DEVICE
            and found.st_uid == os.geteuid()
            and found.st_nlink == 1
            and 0 < found.st_size <= MAX_OWNER_BYTES,
            "reject an exchanged live V23 source owner",
        )
        return role, relative, fingerprint, found.st_size, found.st_ino
    finally:
        os.close(descriptor)


def owner_document(row: tuple, *, uid: bool = False) -> dict:
    result = {
        "path": row[1], "sha256": row[2], "bytes": row[3],
        "device": DEVICE, "inode": row[4], "mode": "0600", "nlink": 1,
    }
    if uid:
        result["uid"] = os.geteuid()
    return result


def bootstrap_capture_v2(wall: PublicSourceWall) -> types.ModuleType:
    row = CAPTURE_V2_OWNERS[0]
    raw = secure_owner(wall, row)
    module = types.ModuleType("_rebar_v23_exact_public_capture_semantics_v2")
    module.__file__ = ROOT + "/" + row[1]
    exec(compile(raw, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    require(
        module.SOURCE == CAPTURE_V2_OWNERS[0][1]
        and module.PROTOCOL == CAPTURE_V2_OWNERS[1][1]
        and module.CONTRACT == CAPTURE_V2_OWNERS[2][1]
        and module.SCHEMA
        == "rebar-owned-rust-capture-shape-semantics-v2-source-freeze"
        and module.VERSION == 2
        and module.PUBLIC_OWNERS == PUBLIC_OWNERS
        and callable(module.load_context)
        and callable(module.self_test)
        and callable(module.validate_campaign)
        and callable(module.validate_actual_failure)
        and callable(module.validate_prior_v20)
        and callable(module.canonical_document)
        and callable(module.clone),
        "reject substituted complete public V2 controller or 18 owner pins",
    )
    require(isinstance(module.FreezeError, type)
            and issubclass(module.FreezeError, Exception),
            "authenticate the inherited V2 hostile-control exception")
    wall.error_type = type(
        "V23AuthenticatedCaptureWallError",
        (FreezeError, module.FreezeError),
        {},
    )
    no_matching_imports()
    return module


def validate_exact_campaign(
    capture: types.ModuleType, semantic: types.ModuleType,
    value: object, reference: dict,
) -> None:
    require(type(reference) is dict and len(reference) == 435,
            "require all 435 immutable V22 original-campaign obligations")
    require(type(value) is dict and len(value) == 435
            and set(value) == set(reference),
            "reject an omitted or extra complete V22 campaign obligation")
    assert isinstance(value, dict)
    capture.validate_campaign(value)
    require(
        capture.canonical_document(semantic, value)
        == capture.canonical_document(semantic, reference),
        "reject a changed value in any complete V22 campaign obligation",
    )


def validate_exact_actual(
    capture: types.ModuleType, semantic: types.ModuleType,
    value: object, reference: dict,
) -> dict:
    require(type(reference) is dict and len(reference) == 96,
            "require the complete genuine 96-field actual V22 failure")
    require(type(value) is dict and len(value) == 96
            and set(value) == set(reference),
            "reject an omitted or extra actual V22 failure field")
    assert isinstance(value, dict)
    require(
        capture.canonical_document(semantic, value)
        == capture.canonical_document(semantic, reference),
        "reject a changed value in any genuine V22 failure field",
    )
    return capture.validate_actual_failure(semantic, value)


def validate_guard_v3(value: object) -> None:
    require(type(value) is dict and set(value) == GUARD_KEYS,
            "reject missing or extra complete public runtime-guard fields")
    assert isinstance(value, dict)
    require(
        value.get("schema")
        == "rebar-owned-candidate-runtime-independence-v3-source-freeze"
        and value.get("version") == 3
        and value.get("status")
        == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
        and value.get("goal_sha256") == GOAL_SHA
        and value.get("source") == owner_document(GUARD_OWNERS[0])
        and value.get("protocol") == owner_document(GUARD_OWNERS[1]),
        "reject the exact operational V3 guard source or public owner",
    )

    previous = value.get("immutable_predecessor_v2")
    producer = value.get("immutable_producer_v5")
    require(
        type(previous) is dict
        and previous.get("version") == 2
        and previous.get("owners") == {
            "source": owner_document(GUARD_OWNERS[3]),
            "protocol": owner_document(GUARD_OWNERS[4]),
            "contract": owner_document(GUARD_OWNERS[5]),
        }
        and previous.get("policy")
        == "EXACT AUTHENTICATED V2 RUNTIME POLICY SUBCLASS"
        and previous.get("prepare_family")
        == "INHERITED EXACT V2 FUNCTION AND GLOBALS"
        and previous.get("child_bootstrap")
        == "UNCHANGED AUTHENTICATED V2 CHILD SOURCE"
        and previous.get("status")
        == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
        and previous.get("runtime_non_delegation") == "NOT ESTABLISHED",
        "reject the exact immutable V2 policy, globals, or child source",
    )
    require(
        type(producer) is dict
        and producer.get("version") == 5
        and producer.get("owners") == {
            "source": owner_document(GUARD_OWNERS[6]),
            "protocol": owner_document(GUARD_OWNERS[7]),
            "contract": owner_document(GUARD_OWNERS[8]),
        }
        and producer.get("source_mutated") is False
        and producer.get("child_guard_identity")
        == "EXACT V2 PREPARE GLOBALS AND CHILD PINS"
        and producer.get("create_boundary")
        == "AUTHENTICATED V5 GUARDED CREATE CLOSURE"
        and producer.get("status")
        == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED",
        "reject the genuine frozen first-party V5 producer ownership",
    )

    native = value.get("native_owner_policy")
    require(
        type(native) is dict
        and native.get("required_field_count") == 14
        and native.get("required_fields") == list(NATIVE_OWNER_FIELDS)
        and native.get("extra_or_missing_fields") == "FORBIDDEN"
        and native.get("native_loaded") is False
        and native.get("identity")
        == "EXACT PREPARED FAMILY SOURCE-OWNED NATIVE ARTIFACT",
        "reject omitted, fabricated, or preloaded native owner identity",
    )
    bootstrap = value.get("subinterpreter_bootstrap")
    require(
        type(bootstrap) is dict
        and bootstrap.get("suite") == "subinterpreter_v2"
        and bootstrap.get("original_case_count") == 128
        and bootstrap.get("expected_interpreters_created") == 11
        and bootstrap.get("expected_interpreters_destroyed") == 11
        and bootstrap.get("expected_case_interpreter_exec_calls") == 394
        and bootstrap.get("expected_bootstrap_interpreter_exec_calls") == 11
        and bootstrap.get("expected_cleanup_interpreter_exec_calls") == 11
        and bootstrap.get("expected_total_real_interpreter_exec_calls") == 416
        and bootstrap.get("creation_audit_event")
        == "cpython.PyInterpreterState_New"
        and bootstrap.get("creation_audit_arguments") == NOT_MEASURED
        and bootstrap.get("creation_identity")
        == "AUTHENTICATED NATIVE PROVIDER FRAME AND REAL LIVE-SET DELTA"
        and bootstrap.get("first_execution")
        == "UNCHANGED V2 CHALLENGE-BOUND CHILD GUARD"
        and bootstrap.get("unrestricted_creation") is False
        and bootstrap.get("legacy_interpreter_audit_events")
        == "FORBIDDEN; NOT EMITTED AS GENUINE EXECUTION"
        and all(bootstrap.get(key) == 0 for key in (
            "actual_interpreters_created", "actual_interpreters_destroyed",
            "actual_case_interpreter_exec_calls",
            "actual_bootstrap_interpreter_exec_calls",
            "actual_cleanup_interpreter_exec_calls",
            "actual_child_guards_installed",
        ))
        and bootstrap.get("candidate_status") == "NOT RUN",
        "reject false native creation, child guard, or 11/394/416 accounting",
    )
    policy = value.get("runtime_isolation_policy")
    require(
        type(policy) is dict
        and policy.get("bootstrap")
        == "CPython -I -B -S; audit hook before candidate import"
        and policy.get("candidate_alias")
        == "sys.modules['re'] is the attested candidate"
        and all(policy.get(key) == "FORBIDDEN" for key in (
            "stdlib_re_engine", "stdlib_sre_engine",
            "external_regex_package", "cross_candidate_engine",
            "matching_fallback",
        ))
        and policy.get("native_loader")
        == "ONLY INDIVIDUALLY ATTESTED FAMILY ARTIFACTS"
        and policy.get("guard_installed_before_candidate_import") is True
        and policy.get("source_gate_interpreters") == "NOT CREATED",
        "reject stdlib, external, cross-candidate, fallback, or late guards",
    )
    effects = value.get("source_only_effects")
    require(type(effects) is dict and bool(effects)
            and all(type(item) is int and item == 0
                    for item in effects.values()),
            "reject actual execution in the immutable guard source freeze")
    require(
        value.get("candidate_matching") == "NOT RUN"
        and value.get("runtime_non_delegation") == "NOT ESTABLISHED"
        and value.get("holdout") == "NOT OPENED"
        and value.get("performance") == NOT_MEASURED
        and value.get("memory") == NOT_MEASURED
        and value.get("undefined_behavior") == NOT_MEASURED
        and value.get("qualified_candidate_count") == 0
        and value.get("winner_selected") is False,
        "never infer guard execution, candidate qualification, or performance",
    )


def block_actual_mode(choice: object) -> None:
    require(type(choice) is dict and choice.get("mode") in ACTUAL_MODES,
            "reject an unrelated prospective actual V23 dispatch")
    raise FreezeError(BLOCKED_ACTUAL)


def load_context(
    wall: PublicSourceWall, pins: dict, rendering: bool,
) -> tuple[dict, dict]:
    source_row = dynamic_owner(wall, "source", SOURCE, pins["--source-sha256"])
    protocol_row = dynamic_owner(
        wall, "protocol", PROTOCOL, pins["--protocol-sha256"],
    )
    secure_owner(wall, source_row)
    secure_owner(wall, protocol_row)
    contract_row = None
    if not rendering:
        contract_row = dynamic_owner(
            wall, "contract", CONTRACT, pins["--contract-sha256"],
        )

    capture = bootstrap_capture_v2(wall)
    capture_pins = {
        "--source-sha256": CAPTURE_V2_OWNERS[0][2],
        "--protocol-sha256": CAPTURE_V2_OWNERS[1][2],
        "--contract-sha256": CAPTURE_V2_OWNERS[2][2],
    }
    v2_frozen, v2_state = capture.load_context(wall, capture_pins, False)
    semantic = v2_state["semantic"]
    capture_raw = secure_owner(wall, CAPTURE_V2_OWNERS[2])
    require(
        capture_raw == capture.canonical_document(semantic, v2_frozen)
        and semantic.StrictJSON(capture_raw).decode() == v2_frozen
        and v2_frozen.get("schema") == capture.SCHEMA
        and v2_frozen.get("version") == 2
        and v2_frozen.get("source", {}).get("sha256")
        == CAPTURE_V2_OWNERS[0][2]
        and v2_frozen.get("protocol", {}).get("sha256")
        == CAPTURE_V2_OWNERS[1][2]
        and v2_frozen.get("source_only_effects", {}).get("holdout")
        == "NOT OPENED",
        "reject a normalized, partial, or changed complete V2 source freeze",
    )
    campaign = v2_state["campaign"]
    actual = v2_state["actual"]
    prior = v2_state["prior"]
    symbol = v2_state["symbolic"]
    validate_exact_campaign(capture, semantic, campaign, campaign)
    diagnostics = validate_exact_actual(capture, semantic, actual, actual)
    capture.validate_prior_v20(prior)
    require(
        type(symbol) is dict
        and symbol.get("measured_actual_bridge_sha256") == F9_SHA
        and symbol.get("measured_predecessor_bridge_sha256") == A0_SHA
        and symbol.get("expected_complete_variant_bytes_from_anchor_arithmetic")
        == 178860
        and symbol.get("complete_variant_bytes_observed") == NOT_MEASURED
        and symbol.get("complete_variant_sha256") == NOT_MEASURED
        and symbol.get("complete_variant_materialized") is False
        and symbol.get("build") == "NOT RUN"
        and symbol.get("matching") == "NOT RUN"
        and symbol.get("correctness") == NOT_MEASURED,
        "never confuse the measured f9 bridge with the unbuilt V2 proposal",
    )

    guard_public: dict[str, bytes] = {}
    for row in GUARD_OWNERS:
        guard_public[row[0]] = secure_owner(wall, row)
    guard = semantic.StrictJSON(guard_public["guard_v3_contract"]).decode()
    validate_guard_v3(guard)
    require(not wall.live and len(campaign) == 435 and len(actual) == 96,
            "close descriptors and preserve every historical obligation")

    frozen = build_contract(
        source_row, protocol_row, v2_frozen, campaign, actual, prior,
        guard, symbol, diagnostics,
    )
    state = {
        "capture": capture, "semantic": semantic,
        "capture_v2_frozen": v2_frozen, "capture_v2_state": v2_state,
        "campaign": campaign, "actual": actual, "prior": prior,
        "symbolic": symbol, "guard": guard, "diagnostics": diagnostics,
        "source_row": source_row, "protocol_row": protocol_row,
        "contract": frozen,
    }
    if not rendering:
        assert isinstance(contract_row, tuple)
        raw = secure_owner(wall, contract_row)
        require(
            raw == capture.canonical_document(semantic, frozen)
            and semantic.StrictJSON(raw).decode() == frozen,
            "reject any omitted, extra, or altered complete V23 obligation",
        )
        state["contract_row"] = contract_row
    require(not wall.live,
            "close every approved tracked V23 public evidence descriptor")
    no_matching_imports()
    return frozen, state


def build_contract(
    source_row: tuple, protocol_row: tuple, capture_v2: dict,
    campaign: dict, actual: dict, prior: dict, guard: dict,
    symbol: dict, diagnostics: dict,
) -> dict:
    suites = [
        {
            "id": row[0],
            "case_execution_denominator": row[1],
            "candidate_status": "NOT RUN",
            "candidate_workers_started": 0,
            "semantic_mismatch_count": NOT_MEASURED,
            "immutable_v22_original_row_sha256": row[2],
        }
        for row in bootstrap_suites()
    ]
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "status": (
            "SOURCE FROZEN; CORRECTED BUILD AND ORIGINAL CAMPAIGN NOT RUN"
        ),
        "phase": "PHASE 2: FIRST-PARTY ORIGINAL CANDIDATE CORRECTNESS",
        "family": "rust",
        "goal_sha256": GOAL_SHA,
        "source": owner_document(source_row, uid=True),
        "protocol": owner_document(protocol_row, uid=True),
        "public_source_wall": {
            "policy": "DENY DEFAULT; EXACT AUTHENTICATED PUBLIC PLAINTEXT ONLY",
            "installed_before_first_predecessor_byte": True,
            "permitted_static_public_owner_count": len(STATIC_OWNERS),
            "permitted_current_source_owner_count": 3,
            "candidate_paths_allowed": 0,
            "historical_candidate_paths_allowed": 0,
            "private_build_root_paths_allowed": 0,
            "native_library_paths_allowed": 0,
            "phase_three_or_proposal_paths_allowed": 0,
            "compressed_archive_paths_allowed": 0,
            "hidden_holdout_paths_allowed": 0,
            "foreign_descriptor_reads_allowed": 0,
            "direct_io_allowed": False,
            "direct_metadata_allowed": False,
            "timing_allowed": False,
            "entropy_allowed": False,
            "previous_v22_source_wall_instantiated": False,
            "previous_v22_controller_executed": False,
            "guard_v3_controller_executed": False,
            "guard_v2_controller_executed": False,
            "producer_v5_controller_executed": False,
        },
        "authenticated_public_plaintext_owners": [
            {"role": row[0], **owner_document(row, uid=True)}
            for row in STATIC_OWNERS
        ],
        "immutable_capture_shape_semantics_v2": {
            "source_sha256": CAPTURE_V2_OWNERS[0][2],
            "protocol_sha256": CAPTURE_V2_OWNERS[1][2],
            "contract_sha256": CAPTURE_V2_OWNERS[2][2],
            "complete_frozen_source_contract": capture_v2,
            "controller_executed_under_fresh_v23_public_wall": True,
            "historical_candidate_source_read": False,
            "variant_materialized": False,
            "variant_build": "NOT RUN",
        },
        "immutable_previous_v22_campaign": {
            "source_sha256": PUBLIC_OWNERS[13][2],
            "protocol_sha256": PUBLIC_OWNERS[14][2],
            "contract_sha256": PUBLIC_OWNERS[15][2],
            "complete_current_contract_field_count": 435,
            "complete_inherited_v21_contract_field_count": 402,
            "complete_frozen_source_contract": campaign,
            "controller_executed": False,
        },
        "immutable_actual_v22_failure": {
            "receipt_sha256": ACTUAL_SHA,
            "receipt_bytes": 47336,
            "receipt_device": DEVICE,
            "receipt_inode": 525371,
            "complete_receipt_field_count": 96,
            "complete_durable_publication_receipt": actual,
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": "FAIL",
            "candidate_qualified": False,
            "original_case_denominator": 31237,
            "original_suite_count": 13,
            "actual_worker_count": 13,
            "distinct_actual_worker_count": 13,
            "completed_suite_count": 12,
            "fully_passing_suite_count": 9,
            "verified_passing_case_count": 14725,
            "fully_observed_mismatch_lower_bound": 2018,
            "fully_observed_suite_mismatch_counts": {
                "managed_v1": 42,
                "substitution_v2": 352,
                "shape_v2": 1624,
            },
            "global_semantic_mismatch_count": NOT_MEASURED,
            "incomplete_suite": "subinterpreter_v2",
            "incomplete_suite_case_count": 128,
            "actual_failing_worker_pid": 188,
            "actual_failing_worker_candidate_imports": 1,
            "actual_failing_worker_native_library_loads": 2,
            "actual_failing_worker_counter_scope": (
                "SUCCESSFULLY RETURNED OR RECORDED ONLY; "
                "TRANSIENT PHYSICAL NATIVE CREATION NOT MEASURED"
            ),
            "actual_failing_worker_successfully_returned_child_interpreters": 0,
            "actual_failing_worker_recorded_destroyed_child_interpreters": 0,
            "actual_failing_worker_installed_child_guards": 0,
            "actual_failing_worker_recorded_case_interpreter_exec_calls": 0,
            "actual_failing_worker_transient_native_child_creation": (
                NOT_MEASURED
            ),
            "actual_failing_worker_warning_scope": (
                "ONLY ACTUAL SUBINTERPRETER WORKER PID 188"
            ),
            "actual_failing_worker_remaining_interpreter_warnings": 1,
            "actual_failing_worker_destructor_warnings": 16,
            "actual_failing_worker_nested_diagnostics": diagnostics,
        },
        "immutable_actual_v20_failure": {
            "receipt_sha256": PUBLIC_OWNERS[16][2],
            "complete_durable_publication_receipt": prior,
            "candidate_status": "FAIL",
            "candidate_qualified": False,
            "original_case_denominator": 31237,
            "completed_suite_count": 12,
            "verified_passing_case_count": 15749,
            "fully_observed_suite_mismatch_counts": {
                "substitution_v2": 240,
                "shape_v2": 1056,
            },
            "global_semantic_mismatch_count": NOT_MEASURED,
            "measured_bridge_sha256": A0_SHA,
            "measured_bridge_bytes": 179520,
        },
        "immutable_runtime_independence_guard_v3": {
            "source_sha256": GUARD_OWNERS[0][2],
            "protocol_sha256": GUARD_OWNERS[1][2],
            "contract_sha256": GUARD_OWNERS[2][2],
            "complete_frozen_source_contract": guard,
            "guard_controller_executed": False,
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "prospective_first_party_correction": {
            "kind": "EXACT SYMBOLIC PUBLIC-SOURCE V2 ANCHOR ONLY",
            "complete_immutable_symbolic_evidence": symbol,
            "measured_prior_a0_bridge_sha256": A0_SHA,
            "measured_prior_a0_bridge_bytes": 179520,
            "measured_failed_f9_bridge_sha256": F9_SHA,
            "measured_failed_f9_bridge_bytes": 179147,
            "measured_original_replacement_anchor_bytes": 97,
            "measured_failed_replacement_anchor_bytes": 384,
            "conditional_removed_guard_bytes": 287,
            "retained_outer_length_removal_bytes": 660,
            "conditional_source_anchor_arithmetic_bytes": 178860,
            "conditional_arithmetic_is_observed_complete_source": False,
            "corrected_complete_source_sha256": NOT_MEASURED,
            "corrected_complete_source_bytes_observed": NOT_MEASURED,
            "corrected_source_materialized": False,
            "corrected_native_engine_sha256": NOT_MEASURED,
            "corrected_native_bridge_sha256": NOT_MEASURED,
            "corrected_build_source_sha256": NOT_MEASURED,
            "corrected_build_protocol_sha256": NOT_MEASURED,
            "corrected_build_contract_sha256": NOT_MEASURED,
            "corrected_build_publication_receipt_sha256": NOT_MEASURED,
            "corrected_build_root_receipt_sha256": NOT_MEASURED,
            "corrected_native_build": "NOT RUN",
            "corrected_candidate_matching": "NOT RUN",
            "corrected_candidate_correctness": NOT_MEASURED,
            "corrected_candidate_qualified": False,
            "old_failed_f9_accepted_as_corrected": False,
            "stdlib_regex_matching": "FORBIDDEN",
            "stdlib_sre_matching": "FORBIDDEN",
            "external_regex_matching": "FORBIDDEN",
            "cross_candidate_matching": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
        },
        "frozen_original_correctness": {
            "cpython_version": "3.14.6",
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "private_waiver_count": 13,
            "suites": suites,
            "supplemental_differential_reference_case_count": 8244,
            "supplemental_counted_in_original_denominator": False,
            "separate_corrected_reference_vector_case_count": 6912,
            "corrected_reference_counted_in_original_denominator": False,
            "corrected_candidate_status": "NOT RUN",
            "corrected_candidate_mismatch_count": NOT_MEASURED,
            "corrected_candidate_verified_passing_case_count": NOT_MEASURED,
            "qualified_independent_candidate_count": 0,
        },
        "future_genuine_subinterpreter_requirements": {
            "suite": "subinterpreter_v2",
            "expected_interpreters_created": 11,
            "expected_interpreters_destroyed": 11,
            "expected_case_interpreter_exec_calls": 394,
            "expected_bootstrap_interpreter_exec_calls": 11,
            "expected_cleanup_interpreter_exec_calls": 11,
            "expected_total_real_interpreter_exec_calls": 416,
            "actual_v23_interpreters_created": 0,
            "actual_v23_interpreters_destroyed": 0,
            "actual_v23_case_interpreter_exec_calls": 0,
            "actual_v23_bootstrap_interpreter_exec_calls": 0,
            "actual_v23_cleanup_interpreter_exec_calls": 0,
            "actual_v23_total_real_interpreter_exec_calls": 0,
            "candidate_status": "NOT RUN",
        },
        "actual_mode_activation": {
            "run": "BLOCKED",
            "worker": "BLOCKED",
            "recover": "BLOCKED",
            "reason": BLOCKED_ACTUAL,
            "requires_separately_committed_corrected_complete_source": True,
            "requires_independently_pinned_genuine_native_build": True,
            "requires_independently_pinned_genuine_root_receipt": True,
            "future_build_source_sha256": NOT_MEASURED,
            "future_build_protocol_sha256": NOT_MEASURED,
            "future_build_contract_sha256": NOT_MEASURED,
            "future_publication_receipt_sha256": NOT_MEASURED,
            "future_root_receipt_sha256": NOT_MEASURED,
            "future_native_engine_sha256": NOT_MEASURED,
            "future_native_bridge_sha256": NOT_MEASURED,
            "future_build_label": "NOT FROZEN",
            "actual_mode_installs_public_source_wall": False,
            "actual_mode_opens_any_owner_before_rejection": False,
            "allow_old_failed_f9_as_repaired": False,
            "automatic_recovery_without_corrected_build": False,
        },
        "source_only_effects": {
            "candidate_source_files_read": 0,
            "historical_candidate_source_files_read": 0,
            "phase_three_proposal_files_read": 0,
            "candidate_imports": 0,
            "candidate_workers_started": 0,
            "reference_workers_started": 0,
            "compiler_processes_started": 0,
            "native_libraries_loaded": 0,
            "native_or_private_roots_opened": 0,
            "compressed_archives_opened": 0,
            "compressed_archives_inflated": 0,
            "foreign_descriptor_reads": 0,
            "candidate_metadata_probes": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "threads_started": 0,
            "network_requests": 0,
            "v23_interpreters_created": 0,
            "corrected_complete_source_materialized": False,
            "corrected_native_build": "NOT RUN",
            "corrected_original_campaign": "NOT RUN",
            "corrected_candidate_correctness": NOT_MEASURED,
            "corrected_candidate_qualified": False,
            "corrected_runtime_non_delegation": "NOT ESTABLISHED",
            "expanded_holdout_proposal_case_count": 14155776,
            "expanded_holdout_cases": "NOT FROZEN; NOT GENERATED; NOT OPENED",
            "holdout": "NOT OPENED",
            "performance": NOT_MEASURED,
            "memory": NOT_MEASURED,
            "confidence_intervals": NOT_MEASURED,
            "undefined_behavior": NOT_MEASURED,
            "qualified_candidate_count": 0,
            "winner_selected": False,
        },
    }


def bootstrap_suites() -> tuple:
    return (
        ("original_bounded_v5", 151, "c62495b7562e3fe9ee7b5718e840cd527fd5d455ba4c90475b44bdb159e36cc9"),
        ("public_v3", 864, "3a9f52000cb1395b29e0dd5e80be02c08052ef6117c71327ad43ef1541426a1f"),
        ("scanner_v3", 1024, "46286308cc402a7f5242799e2933ac669301d7762673649d49fe45216bf2b25d"),
        ("buffer_v3", 768, "0235f4e8dda286945498077ec113f51b6299ff3085ba973921b4b309d4fac3d3"),
        ("managed_v1", 1024, "a2a10abfd8cbac37711ec9e9ba8449d1fec9f4a8a84aba31cd81f0858240023c"),
        ("scanner_verbose_v1", 2854, "fa319638a8a293e3fbed5ccfe1bfe4e3f9cb8d2b9d8672fec4119dd2b7b228ff"),
        ("public_types_v1", 6912, "2eccbfd8f0c77e67f59d5dc6172a16ac78a9b466fe554fd0e99b642ffacd14ea"),
        ("substitution_v2", 5120, "c81076c70583a3307d563271c6aea6417fff69150dff2b1f713c88030796c546"),
        ("shape_v2", 10240, "1d49921f6d3bb468161c5d216b2d75366b8137e99d90470f05cd667414b76447"),
        ("public_surface_v19", 1376, "41e4cc287839fc321861f5767f2023774efd75e59c9fdf8a85b3261e4abad67c"),
        ("subinterpreter_v2", 128, "0a763bf5aaaff32766e3dbb56a7ec42354bb585143a309674b7c8a9724dc0335"),
        ("pep688_v4", 264, "d6f67cec3b1df33e11791370289ddd62a2b98b17c257875f0d23acfb099ee10d"),
        ("threaded_pattern_v1", 512, "913de4de372ec2ce50304d8c56ff1a45bd7b5f9ac98c269ce9256f3d0dcebc90"),
    )


def reject(action: object, label: str, *kinds: type) -> str:
    require(callable(action), "require a real public-only hostile control")
    try:
        action()
    except (FreezeError, OSError, ValueError, TypeError, KeyError, IndexError,
            UnicodeError, OverflowError, *kinds):
        return label
    raise FreezeError("accepted hostile V23 public-only control: " + label)


def validate_frozen_document(
    capture: types.ModuleType, semantic: types.ModuleType,
    candidate: object, expected: dict,
) -> None:
    require(type(candidate) is dict and set(candidate) == set(expected),
            "reject missing or additional complete V23 top-level obligations")
    assert isinstance(candidate, dict)
    require(
        capture.canonical_document(semantic, candidate)
        == capture.canonical_document(semantic, expected),
        "reject an altered complete prospective V23 campaign obligation",
    )


def self_test(wall: PublicSourceWall, context: dict, state: dict) -> list[str]:
    capture = state["capture"]
    semantic = state["semantic"]
    campaign = state["campaign"]
    actual = state["actual"]
    guard = state["guard"]
    kinds = (capture.FreezeError, semantic.FreezeError)

    inherited = capture.self_test(
        wall, semantic, state["capture_v2_frozen"], state["capture_v2_state"],
    )
    require(type(inherited) is list and len(inherited) == 240,
            "preserve every one of the 240 independently frozen V2 controls")
    checks = list(inherited)

    for key in sorted(campaign):
        missing = dict(campaign)
        missing.pop(key)
        checks.append(reject(
            lambda item=missing: validate_exact_campaign(
                capture, semantic, item, campaign,
            ), "reject-missing-complete-v22-obligation-" + key, *kinds,
        ))
        changed = dict(campaign)
        changed[key] = {"__v23_hostile_changed_obligation__": key}
        checks.append(reject(
            lambda item=changed: validate_exact_campaign(
                capture, semantic, item, campaign,
            ), "reject-changed-complete-v22-obligation-" + key, *kinds,
        ))

    for key in sorted(actual):
        changed = dict(actual)
        changed[key] = {"__v23_hostile_changed_actual_receipt__": key}
        checks.append(reject(
            lambda item=changed: validate_exact_actual(
                capture, semantic, item, actual,
            ), "reject-changed-complete-actual-v22-receipt-" + key, *kinds,
        ))

    for key in sorted(GUARD_KEYS):
        missing = dict(guard)
        missing.pop(key)
        checks.append(reject(
            lambda item=missing: validate_guard_v3(item),
            "reject-missing-complete-operational-v3-guard-" + key, *kinds,
        ))

    for offset, role in ((0, "source"), (1, "protocol")):
        forged = capture.clone(semantic, guard)
        assert isinstance(forged, dict)
        forged[role]["sha256"] = "0" * 64
        checks.append(reject(
            lambda item=forged: validate_guard_v3(item),
            "reject-forged-operational-v3-" + str(offset) + "-" + role,
            *kinds,
        ))
    for section, index, label in (
        ("immutable_predecessor_v2", 3, "guard-v2"),
        ("immutable_producer_v5", 6, "producer-v5"),
    ):
        for offset, role in enumerate(("source", "protocol", "contract")):
            forged = capture.clone(semantic, guard)
            assert isinstance(forged, dict)
            forged[section]["owners"][role]["sha256"] = "0" * 64
            checks.append(reject(
                lambda item=forged: validate_guard_v3(item),
                "reject-forged-" + label + "-" + role + "-"
                + str(index + offset), *kinds,
            ))
    for key, value in (
        ("expected_interpreters_created", 10),
        ("expected_interpreters_destroyed", 10),
        ("expected_case_interpreter_exec_calls", 393),
        ("expected_bootstrap_interpreter_exec_calls", 10),
        ("expected_cleanup_interpreter_exec_calls", 10),
        ("expected_total_real_interpreter_exec_calls", 415),
        ("actual_interpreters_created", 1),
        ("actual_interpreters_destroyed", 1),
        ("actual_case_interpreter_exec_calls", 1),
        ("actual_bootstrap_interpreter_exec_calls", 1),
        ("actual_cleanup_interpreter_exec_calls", 1),
        ("actual_child_guards_installed", 1),
        ("candidate_status", "PASS"),
    ):
        forged = capture.clone(semantic, guard)
        assert isinstance(forged, dict)
        forged["subinterpreter_bootstrap"][key] = value
        checks.append(reject(
            lambda item=forged: validate_guard_v3(item),
            "reject-forged-operational-v3-child-" + key, *kinds,
        ))
    for key, value in (
        ("required_field_count", 13),
        ("required_fields", list(NATIVE_OWNER_FIELDS[:-1])),
        ("extra_or_missing_fields", "PERMITTED"),
        ("native_loaded", True),
        ("identity", "FABRICATED FAMILY OWNER"),
    ):
        forged = capture.clone(semantic, guard)
        assert isinstance(forged, dict)
        forged["native_owner_policy"][key] = value
        checks.append(reject(
            lambda item=forged: validate_guard_v3(item),
            "reject-forged-operational-v3-native-" + key, *kinds,
        ))
    for key in (
        "stdlib_re_engine", "stdlib_sre_engine", "external_regex_package",
        "cross_candidate_engine", "matching_fallback",
    ):
        forged = capture.clone(semantic, guard)
        assert isinstance(forged, dict)
        forged["runtime_isolation_policy"][key] = "ALLOWED"
        checks.append(reject(
            lambda item=forged: validate_guard_v3(item),
            "reject-forged-operational-v3-delegation-" + key, *kinds,
        ))

    for key in sorted(context):
        missing = dict(context)
        missing.pop(key)
        checks.append(reject(
            lambda item=missing: validate_frozen_document(
                capture, semantic, item, context,
            ), "reject-missing-complete-v23-obligation-" + key, *kinds,
        ))

    for section, key, value, label in (
        ("prospective_first_party_correction",
         "corrected_complete_source_sha256", F9_SHA, "old-f9-source"),
        ("prospective_first_party_correction",
         "corrected_complete_source_bytes_observed", 178860,
         "arithmetic-presented-as-observed"),
        ("prospective_first_party_correction",
         "corrected_source_materialized", True, "materialized-source"),
        ("prospective_first_party_correction",
         "corrected_native_bridge_sha256", F9_SHA, "old-f9-native"),
        ("prospective_first_party_correction",
         "corrected_native_build", "PASS", "unbuilt-native-pass"),
        ("prospective_first_party_correction",
         "corrected_candidate_correctness", "PASS", "unrun-candidate-pass"),
        ("prospective_first_party_correction",
         "corrected_candidate_qualified", True, "unqualified-candidate"),
        ("actual_mode_activation", "run", "AVAILABLE", "run-without-build"),
        ("actual_mode_activation", "worker", "AVAILABLE",
         "worker-without-build"),
        ("actual_mode_activation", "recover", "AVAILABLE",
         "recovery-without-build"),
        ("actual_mode_activation", "allow_old_failed_f9_as_repaired", True,
         "reactivate-known-failing-f9"),
        ("actual_mode_activation", "automatic_recovery_without_corrected_build",
         True, "invented-recovery"),
        ("source_only_effects", "holdout", "OPENED", "holdout-opened"),
        ("source_only_effects", "hidden_cases_read", 1, "hidden-cases"),
        ("source_only_effects", "performance", "1.5x", "invented-speed"),
        ("source_only_effects", "winner_selected", True, "invented-winner"),
        ("immutable_actual_v22_failure", "candidate_status", "PASS",
         "convert-historical-failure-into-pass"),
        ("immutable_actual_v22_failure", "global_semantic_mismatch_count", 2018,
         "turn-lower-bound-into-total"),
        ("immutable_actual_v22_failure",
         "actual_failing_worker_candidate_imports", 0,
         "erase-historical-worker-candidate"),
        ("immutable_actual_v22_failure",
         "actual_failing_worker_native_library_loads", 0,
         "erase-historical-worker-native-loads"),
        ("immutable_actual_v22_failure",
         "actual_failing_worker_successfully_returned_child_interpreters", 1,
         "invent-recorded-successfully-returned-child"),
        ("immutable_actual_v22_failure",
         "actual_failing_worker_installed_child_guards", 1,
         "invent-recorded-installed-child-guard"),
        ("immutable_actual_v22_failure",
         "actual_failing_worker_recorded_case_interpreter_exec_calls", 1,
         "invent-recorded-child-case-execution"),
        ("immutable_actual_v22_failure",
         "actual_failing_worker_transient_native_child_creation", False,
         "invent-absence-of-transient-native-child"),
        ("immutable_actual_v22_failure",
         "actual_failing_worker_transient_native_child_creation", True,
         "invent-confirmation-of-transient-native-child"),
    ):
        forged = capture.clone(semantic, context)
        assert isinstance(forged, dict)
        forged[section][key] = value
        checks.append(reject(
            lambda item=forged: validate_frozen_document(
                capture, semantic, item, context,
            ), "reject-v23-" + label, *kinds,
        ))

    for mode in ACTUAL_MODES:
        before_live = len(wall.live)
        before_blocked = dict(wall.blocked)
        checks.append(reject(
            lambda item=mode: block_actual_mode({"mode": item}),
            "reject-unbuilt-prospective-v23-" + mode.removeprefix("--"),
            *kinds,
        ))
        require(len(wall.live) == before_live and wall.blocked == before_blocked,
                "reject actual-mode synthetic control without any owner I/O")

    extra = dict(context)
    extra["__v23_fabricated_unpublished_evidence__"] = True
    checks.append(reject(
        lambda: validate_frozen_document(capture, semantic, extra, context),
        "reject-extra-unpublished-v23-evidence", *kinds,
    ))
    no_matching_imports()
    require(
        wall.installed and not wall.live and bool(wall.blocked)
        and len(inherited) == 240 and len(checks) >= 1280,
        "require inherited, complete, physically isolated V23 hostile controls",
    )
    return checks


def parse_arguments(arguments: list[str]) -> dict:
    require(bool(arguments), "select one exact frozen V23 campaign mode")
    mode = arguments[0]
    require(mode in SOURCE_MODES + ACTUAL_MODES,
            "reject an unrecognized V23 source or actual campaign mode")
    required = ["--source-sha256", "--protocol-sha256"]
    if mode != "--render-contract":
        required.append("--contract-sha256")
    require(len(arguments) == 1 + 2 * len(required),
            "require precisely independent V23 public source authority")
    pins: dict[str, str] = {}
    for index in range(1, len(arguments), 2):
        key, value = arguments[index], arguments[index + 1]
        require(key in required and key not in pins,
                "reject repeated or unrelated V23 caller authority")
        pins[key] = digest_pin(value, key)
    require(set(pins) == set(required),
            "reject omitted independent V23 caller source authority")
    return {"mode": mode, "pins": pins}


def main(arguments: list[str] | None = None) -> int:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.executable == PYTHON
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True,
        "require exact pinned CPython 3.14.6 with -I -B -S",
    )
    no_matching_imports()
    choice = parse_arguments(
        list(sys.argv[1:] if arguments is None else arguments),
    )
    if choice["mode"] in ACTUAL_MODES:
        block_actual_mode(choice)
        raise FreezeError("unreachable actual V23 campaign dispatch")

    wall = PublicSourceWall()
    wall.install()
    frozen, state = load_context(
        wall, choice["pins"], choice["mode"] == "--render-contract",
    )
    capture = state["capture"]
    semantic = state["semantic"]
    if choice["mode"] == "--render-contract":
        sys.stdout.buffer.write(capture.canonical_document(semantic, frozen))
        sys.stdout.buffer.flush()
        return 0

    checks = (
        self_test(wall, frozen, state)
        if choice["mode"] == "--self-test" else []
    )
    result = {
        "schema": SCHEMA + "-source-only-gate",
        "status": "PASS",
        "version": VERSION,
        "mode": choice["mode"].removeprefix("--"),
        "source_sha256": choice["pins"]["--source-sha256"],
        "protocol_sha256": choice["pins"]["--protocol-sha256"],
        "contract_sha256": choice["pins"]["--contract-sha256"],
        "authenticated_static_public_plaintext_owner_count": len(STATIC_OWNERS),
        "authenticated_current_public_source_owner_count": 3,
        "public_only_wall_installed_before_first_predecessor_byte": (
            wall.installed
        ),
        "public_only_wall_live_descriptors": len(wall.live),
        "previous_v22_source_wall_instantiated": False,
        "previous_v22_controller_executed": False,
        "guard_v3_controller_executed": False,
        "guard_v2_controller_executed": False,
        "producer_v5_controller_executed": False,
        "candidate_source_files_read": 0,
        "historical_candidate_source_files_read": 0,
        "phase_three_proposal_files_read": 0,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "compiler_processes_started": 0,
        "native_libraries_loaded": 0,
        "private_root_opens": 0,
        "archive_opens": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "inherited_v2_hostile_control_count": (
            240 if choice["mode"] == "--self-test" else 0
        ),
        "hostile_control_count": len(checks),
        "hostile_controls": checks,
        "physically_blocked_effects": dict(wall.blocked),
        "complete_current_v22_contract_field_count": 435,
        "complete_inherited_v21_contract_field_count": 402,
        "complete_actual_v22_failure_receipt_field_count": 96,
        "actual_v22_failure_receipt_sha256": ACTUAL_SHA,
        "actual_v22_publication_status": "PASS",
        "actual_v22_publication_pass_means": "DURABLE PUBLICATION ONLY",
        "actual_v22_candidate_status": "FAIL",
        "actual_v22_original_case_denominator": 31237,
        "actual_v22_original_suite_count": 13,
        "actual_v22_distinct_worker_count": 13,
        "actual_v22_completed_suite_count": 12,
        "actual_v22_fully_passing_suite_count": 9,
        "actual_v22_verified_passing_case_count": 14725,
        "actual_v22_observed_mismatch_lower_bound": 2018,
        "actual_v22_observed_suite_mismatch_counts": {
            "managed_v1": 42,
            "substitution_v2": 352,
            "shape_v2": 1624,
        },
        "actual_v22_global_mismatch_count": NOT_MEASURED,
        "actual_v22_failing_worker_pid": 188,
        "actual_v22_failing_worker_candidate_imports": 1,
        "actual_v22_failing_worker_native_library_loads": 2,
        "actual_v22_failing_worker_counter_scope": (
            "SUCCESSFULLY RETURNED OR RECORDED ONLY; "
            "TRANSIENT PHYSICAL NATIVE CREATION NOT MEASURED"
        ),
        "actual_v22_successfully_returned_child_interpreters": 0,
        "actual_v22_recorded_destroyed_child_interpreters": 0,
        "actual_v22_installed_child_guards": 0,
        "actual_v22_recorded_child_case_interpreter_exec_calls": 0,
        "actual_v22_transient_native_child_creation": NOT_MEASURED,
        "actual_v22_warning_scope": (
            "ONLY ACTUAL SUBINTERPRETER WORKER PID 188"
        ),
        "actual_v22_remaining_interpreter_warning_count": 1,
        "actual_v22_worker_destructor_warning_count": 16,
        "actual_prior_v20_bridge_sha256": A0_SHA,
        "actual_prior_v20_verified_passing_case_count": 15749,
        "actual_prior_v20_observed_suite_mismatch_counts": {
            "substitution_v2": 240,
            "shape_v2": 1056,
        },
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "supplemental_differential_case_count": 8244,
        "supplemental_counted_in_original_denominator": False,
        "corrected_reference_vector_case_count": 6912,
        "corrected_reference_counted_in_original_denominator": False,
        "corrected_complete_source_sha256": NOT_MEASURED,
        "corrected_complete_source_bytes_observed": NOT_MEASURED,
        "conditional_source_anchor_arithmetic_bytes": 178860,
        "conditional_arithmetic_is_observed_complete_source": False,
        "corrected_native_engine_sha256": NOT_MEASURED,
        "corrected_native_bridge_sha256": NOT_MEASURED,
        "corrected_build": "NOT RUN",
        "corrected_candidate": "NOT RUN",
        "corrected_candidate_correctness": NOT_MEASURED,
        "actual_modes": {
            "run": "BLOCKED", "worker": "BLOCKED", "recover": "BLOCKED",
        },
        "allow_old_failed_f9_as_repaired": False,
        "expanded_holdout_proposal_case_count": 14155776,
        "expanded_holdout_cases": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "holdout": "NOT OPENED",
        "performance": NOT_MEASURED,
        "memory": NOT_MEASURED,
        "undefined_behavior": NOT_MEASURED,
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    sys.stdout.buffer.write(capture.canonical_document(semantic, result))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FreezeError as error:
        sys.stderr.write("V23 campaign rejected: " + str(error) + "\n")
        raise SystemExit(2)
