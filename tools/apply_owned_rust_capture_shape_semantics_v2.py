#!/usr/bin/env python3
"""Freeze a public-evidence-only, symbolic first-party Rust bridge correction.

No candidate source, native library, private build, archive, benchmark, or
holdout is read.  The complete proposed bridge is not available in permitted
public plaintext: its whole-source hash, execution, and correctness must
remain NOT MEASURED.  Authenticate the actual V22 failure and the immutable
V1 source anchors; prove exactly one proposed replacement in memory.
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
SOURCE = "tools/apply_owned_rust_capture_shape_semantics_v2.py"
PROTOCOL = "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V2.md"
CONTRACT = "oracle/phase2/rust-capture-shape-semantics-v2.json"
SCHEMA = "rebar-owned-rust-capture-shape-semantics-v2-source-freeze"
VERSION = 2
NOT_MEASURED = "NOT MEASURED"
MAX_OWNER_BYTES = 1_048_576
MAX_DIAGNOSTIC_BYTES = 65_536
BASE64 = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
BASE64_VALUES = {value: index for index, value in enumerate(BASE64)}
GOAL_SHA = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
ACTUAL_SHA = "7013c42f6309d94e094dd89cc8e9f24fe245c0cba5ca4791d35ffe5fa2b7dad7"
A0_SHA = "a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a"
F9_SHA = "f9bd2d3c8406e4b2c703ce96f42964ee15941611e22447b12acc9b54fac98055"
ENGINE_SOURCE_SHA = "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d"
BUILD_SOURCE_SHA = "0ce73b2168c5143e2f95256d454ffe131bdc2c5736d91176509cc651819f58d4"
BUILD_PROTOCOL_SHA = "31467e166ecc83ef49c43ca51bb97b7699a696068a4267dcd013c64078b3050a"
BUILD_CONTRACT_SHA = "b43f1a1f5f7c5c72990f4d8c3c9e321e53d7970b3ceaa4b0afdb82a08fa4b308"
CAMPAIGN_SOURCE_SHA = "e88f242835781e9b70efa18e68a7b06b0b9368e91320ed596995ef0e16370c61"
CAMPAIGN_PROTOCOL_SHA = "c6a2a5db9c9c27974c29af01b3d7f7042bae73e254c638fe27813505ef11f396"
CAMPAIGN_CONTRACT_SHA = "f1c021049e4bb173be8d47339920354e02c8c0194aead877b8474a128b5e158a"
SEMANTIC_SOURCE_SHA = "d3213d43bd09b1216f618a3a14472ff0fe290b13852c403a0d1c0ecd8a0408b2"
SEMANTIC_PROTOCOL_SHA = "edbeb811483b39f094dbead1237e912e20af07609474c7256db75fce45887f54"
SEMANTIC_CONTRACT_SHA = "5e262226341a7554943a7ae21fad616009555231e855ea23b7eb715c94317b63"

# Every tuple is public plaintext only: role, relative path, SHA-256, bytes,
# and the independently verified device-2064 inode.  No candidates are allowed.
PUBLIC_OWNERS = (
    ("goal", "GOAL.md", GOAL_SHA, 3756, 31364044),
    ("original_oracle", "oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
     34875, 524713),
    ("supplemental_oracle", "oracle/phase1/p0-differential-fuzz-reference-v3.json",
     "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff",
     5288, 525082),
    ("substitution_oracle", "tools/independent_substitution_buffer_semantics_v2.py",
     "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573",
     317541, 432058),
    ("shape_oracle", "tools/independent_shape_changing_buffer_semantics_v2.py",
     "0262807f793a818307f2c8c6ecfd84bf970264a6ef5d656acf30c9d3606f0e2c",
     137527, 432070),
    ("semantic_v1_source", "tools/apply_owned_rust_capture_shape_semantics_v1.py",
     SEMANTIC_SOURCE_SHA, 53555, 431487),
    ("semantic_v1_protocol", "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V1.md",
     SEMANTIC_PROTOCOL_SHA, 4883, 525377),
    ("semantic_v1_contract", "oracle/phase2/rust-capture-shape-semantics-v1.json",
     SEMANTIC_CONTRACT_SHA, 6524, 525378),
    ("native_v22_source",
     "tools/reproduce_owned_rust_capture_shape_semantics_source_build_v22.py",
     BUILD_SOURCE_SHA, 65949, 430180),
    ("native_v22_protocol",
     "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-SOURCE-BUILD-V22.md",
     BUILD_PROTOCOL_SHA, 5372, 524832),
    ("native_v22_contract",
     "oracle/phase2/rust-capture-shape-semantics-source-build-v22.json",
     BUILD_CONTRACT_SHA, 10067, 524833),
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
     CAMPAIGN_SOURCE_SHA, 61761, 430995),
    ("campaign_v22_protocol",
     "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V22.md",
     CAMPAIGN_PROTOCOL_SHA, 6038, 525307),
    ("campaign_v22_contract",
     "oracle/phase2/repaired-rust-original-campaign-v22.json",
     CAMPAIGN_CONTRACT_SHA, 42352, 525314),
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

SUITES_V22 = (
    ("original_bounded_v5", 151, True, 0, 151, "PASS", 81, 0,
     "c62495b7562e3fe9ee7b5718e840cd527fd5d455ba4c90475b44bdb159e36cc9"),
    ("public_v3", 864, True, 0, 864, "PASS", 83, 0,
     "3a9f52000cb1395b29e0dd5e80be02c08052ef6117c71327ad43ef1541426a1f"),
    ("scanner_v3", 1024, True, 0, 1024, "PASS", 84, 0,
     "46286308cc402a7f5242799e2933ac669301d7762673649d49fe45216bf2b25d"),
    ("buffer_v3", 768, True, 0, 768, "PASS", 85, 0,
     "0235f4e8dda286945498077ec113f51b6299ff3085ba973921b4b309d4fac3d3"),
    ("managed_v1", 1024, True, 42, 0, "SEMANTIC MISMATCH", 86, 1,
     "a2a10abfd8cbac37711ec9e9ba8449d1fec9f4a8a84aba31cd81f0858240023c"),
    ("scanner_verbose_v1", 2854, True, 0, 2854, "PASS", 87, 0,
     "fa319638a8a293e3fbed5ccfe1bfe4e3f9cb8d2b9d8672fec4119dd2b7b228ff"),
    ("public_types_v1", 6912, True, 0, 6912, "PASS", 88, 0,
     "2eccbfd8f0c77e67f59d5dc6172a16ac78a9b466fe554fd0e99b642ffacd14ea"),
    ("substitution_v2", 5120, True, 352, 0, "SEMANTIC MISMATCH", 89, 1,
     "c81076c70583a3307d563271c6aea6417fff69150dff2b1f713c88030796c546"),
    ("shape_v2", 10240, True, 1624, 0, "SEMANTIC MISMATCH", 90, 1,
     "1d49921f6d3bb468161c5d216b2d75366b8137e99d90470f05cd667414b76447"),
    ("public_surface_v19", 1376, True, 0, 1376, "PASS", 91, 0,
     "41e4cc287839fc321861f5767f2023774efd75e59c9fdf8a85b3261e4abad67c"),
    ("subinterpreter_v2", 128, False, NOT_MEASURED, 0,
     "INFRASTRUCTURE FAILURE", 188, 2,
     "0a763bf5aaaff32766e3dbb56a7ec42354bb585143a309674b7c8a9724dc0335"),
    ("pep688_v4", 264, True, 0, 264, "PASS", 189, 0,
     "d6f67cec3b1df33e11791370289ddd62a2b98b17c257875f0d23acfb099ee10d"),
    ("threaded_pattern_v1", 512, True, 0, 512, "PASS", 190, 0,
     "913de4de372ec2ce50304d8c56ff1a45bd7b5f9ac98c269ce9256f3d0dcebc90"),
)
SUITES_V20 = (
    ("original_bounded_v5", 151, True, 0, 151, "PASS", 81, 0,
     "c48d47f8a8b93489467dc0d0cca71091f9a176f69d5174b9929834fb004365e1"),
    ("public_v3", 864, True, 0, 864, "PASS", 83, 0,
     "239cd82a735b6e97b768ef9e9b8acd7960c7caed81189b22bc97cea75ff3b0f9"),
    ("scanner_v3", 1024, True, 0, 1024, "PASS", 84, 0,
     "49cfd0908d9279527d2484d0d54a1790f3d15f87645beaf1f3754118bc8f4a47"),
    ("buffer_v3", 768, True, 0, 768, "PASS", 85, 0,
     "a9596fabcd2a8e04bc57a9efbe3aed82f9d4b1a86e6d5bbd9183955ef7ca34b1"),
    ("managed_v1", 1024, True, 0, 1024, "PASS", 86, 0,
     "237ab27d03e720abb70962542707557bfdaaa5c2457eb6cf3b6866d0fb14a7e2"),
    ("scanner_verbose_v1", 2854, True, 0, 2854, "PASS", 87, 0,
     "00259aa07b1e4c87b5782a97aa43b6e452fff6df6874f641b066513b4c8ce165"),
    ("public_types_v1", 6912, True, 0, 6912, "PASS", 88, 0,
     "bb2e64d29c429613c5b8c515d15afd214d936f90f3d4a415c1a29cf3400a7696"),
    ("substitution_v2", 5120, True, 240, 0, "SEMANTIC MISMATCH", 89, 1,
     "2fc6d6b133d40ac1c8972aa7fd6e39d1f5eb0144f49f5ef7cefc611c437bcac1"),
    ("shape_v2", 10240, True, 1056, 0, "SEMANTIC MISMATCH", 90, 1,
     "e6b271bec48665b29c0c33d2a6ecf9a8dc43880b6bbd0595569aaa34e166c43b"),
    ("public_surface_v19", 1376, True, 0, 1376, "PASS", 91, 0,
     "261561bfad94f6ac7c03924b8d8170be09c00bb117c850f31cd78faf702a6451"),
    ("subinterpreter_v2", 128, False, NOT_MEASURED, 0,
     "INFRASTRUCTURE FAILURE", 188, 2,
     "8a304f6a3b27a5c88b7f7a1e6e0f72e5d4dff6bc2c21a689a2819058b377a344"),
    ("pep688_v4", 264, True, 0, 264, "PASS", 189, 0,
     "340167a5e6936c23fa4345ab1da1ad980cf33ed2c6da7157904faccbda63781e"),
    ("threaded_pattern_v1", 512, True, 0, 512, "PASS", 190, 0,
     "a37a0e5ef6ea19ee2e7a78f76fbeb7920aabe4b1a127bfa89d329b91c8fbc519"),
)


class FreezeError(Exception):
    """Public evidence, source isolation, or symbolic anchors changed."""


def require(value: object, label: str) -> None:
    if value is not True:
        raise FreezeError(label)


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only genuine complete plaintext bytes")
    return hashlib.sha256(raw).hexdigest()


def digest_pin(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require one complete independently pinned SHA-256: " + label)
    assert isinstance(value, str)
    return value


def no_matching_imports() -> None:
    roots = ("re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
             "ctypes", "candidates", "rebar", "subprocess", "socket",
             "concurrent.interpreters")
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in roots),
            "reject matcher, candidate, external engine, native, or network")


class PublicSourceWall:
    """Irreversibly allow only named public plaintext and owned descriptors."""

    def __init__(self) -> None:
        self.allowed = frozenset(
            (ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL,
             ROOT + "/" + CONTRACT)
            + tuple(ROOT + "/" + row[1] for row in PUBLIC_OWNERS)
        )
        self.blocked: dict[str, int] = {}
        self.live: set[int] = set()
        self.installed = False
        self.native_open = os.open
        self.native_read = os.read
        self.native_fstat = os.fstat
        self.native_close = os.close

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise FreezeError("public-only physical source wall rejected " + category)

    def approved(self, path: object) -> bool:
        return (type(path) is str and path.startswith(ROOT + "/")
                and path == os.path.normpath(path)
                and not any(part in (".", "..") for part in path.split("/"))
                and path in self.allowed
                and not path.endswith((".so", ".gz"))
                and not path.startswith(ROOT + "/candidates/")
                and not path.startswith(ROOT + "/oracle/phase3/")
                and "holdout" not in path.lower()
                and "benchmark" not in path.lower())

    def audit(self, event: str, args: tuple) -> None:
        if event == "open":
            path = args[0] if args else None
            mode = args[1] if len(args) > 1 else None
            flags = args[2] if len(args) > 2 else None
            destructive = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                           | os.O_APPEND | getattr(os, "O_TMPFILE", 0))
            if (not self.approved(path) or type(flags) is not int
                    or flags & destructive
                    or not flags & getattr(os, "O_NOFOLLOW", 0)
                    or type(mode) is str and any(item in mode for item in "wax+")):
                self.deny("unowned-direct-file-open")
            return
        if event in ("exec", "compile"):
            value = args[0] if args else None
            filename = (getattr(value, "co_filename", None)
                        if event == "exec"
                        else args[1] if len(args) > 1 else None)
            if not self.approved(filename):
                self.deny("unowned-dynamic-execution")
            return
        if (event == "import" or event == "marshal.loads"
                or event in ("os.system", "os.fork", "os.posix_spawn",
                             "os.posix_spawnp", "os.rename", "os.replace",
                             "os.remove", "os.unlink", "os.mkdir", "os.rmdir",
                             "os.chmod", "os.chown", "os.urandom",
                             "os.getrandom", "_interpreters.create",
                             "_interpreters.exec", "cpython.PyInterpreterState_New")
                or event.startswith(("subprocess.", "socket.", "ctypes.",
                                     "threading.", "multiprocessing.",
                                     "tempfile.", "time.", "os.exec",
                                     "os.spawn", "random."))):
            self.deny("import-process-native-network-clock-or-mutation")

    def _forbidden(self, category: str):
        def blocked(*_args: object, **_kwargs: object) -> object:
            self.deny(category)
        return blocked

    def guarded_open(self, path: object, flags: object,
                     mode: int = 0o777, *, dir_fd: object = None) -> int:
        destructive = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                       | os.O_APPEND | getattr(os, "O_TMPFILE", 0)
                       | getattr(os, "O_DIRECTORY", 0))
        if (not self.approved(path) or type(flags) is not int
                or flags & destructive
                or not flags & getattr(os, "O_NOFOLLOW", 0)
                or dir_fd is not None):
            self.deny("unowned-os-open-or-directory-descriptor")
        assert isinstance(path, str)
        descriptor = self.native_open(path, flags, mode)
        require(type(descriptor) is int and descriptor >= 0,
                "require one real approved public plaintext descriptor")
        require(descriptor not in self.live,
                "reject a reused live public plaintext descriptor")
        self.live.add(descriptor)
        return descriptor

    def guarded_read(self, descriptor: object, count: object) -> bytes:
        if (type(descriptor) is not int or descriptor not in self.live
                or type(count) is not int
                or count < 0 or count > MAX_OWNER_BYTES):
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
        require(self.installed is False, "reject reused public-only audit wall")
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
        for name in ("fdopen", "dup", "dup2", "stat", "lstat", "readlink",
                     "listdir", "scandir", "walk", "fwalk", "access",
                     "fork", "posix_spawn", "posix_spawnp", "system",
                     "mkdir", "makedirs", "remove", "unlink", "rename",
                     "replace", "rmdir", "chmod", "chown", "urandom",
                     "getrandom"):
            if hasattr(os, name):
                setattr(os, name, self._forbidden("direct-os-" + name))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns",
                     "clock_gettime", "clock_gettime_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self._forbidden("clock-" + name))
        self.installed = True


def secure_owner(wall: PublicSourceWall, row: tuple) -> bytes:
    require(type(row) is tuple and len(row) == 5,
            "require one complete independently pinned public owner")
    role, relative, expected, count, inode = row
    require(type(role) is str and type(relative) is str
            and not relative.startswith("/")
            and ".." not in relative.split("/")
            and type(count) is int and 0 < count <= MAX_OWNER_BYTES
            and type(inode) is int and inode > 0,
            "reject unbounded or non-public plaintext owner")
    digest_pin(expected, relative)
    absolute = ROOT + "/" + relative
    require(wall.installed and wall.approved(absolute),
            "install the exact deny-default public wall before owner reads")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(absolute, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_ino == inode
                and before.st_size == count and before.st_uid == os.geteuid()
                and before.st_nlink == 1,
                "reject substituted whole public evidence owner: " + role)
        left = count
        pieces: list[bytes] = []
        while left:
            piece = os.read(descriptor, min(left, 65536))
            require(type(piece) is bytes and bool(piece),
                    "reject truncated complete public owner: " + role)
            pieces.append(piece)
            left -= len(piece)
        require(os.read(descriptor, 1) == b"",
                "reject expanded complete public owner: " + role)
        after = os.fstat(descriptor)
        require(all(getattr(before, item) == getattr(after, item)
                    for item in ("st_dev", "st_ino", "st_size", "st_mtime_ns",
                                 "st_ctime_ns", "st_nlink")),
                "reject concurrently changed public owner: " + role)
        raw = b"".join(pieces)
        require(sha256(raw) == expected,
                "reject changed complete public owner bytes: " + role)
        return raw
    finally:
        os.close(descriptor)


def dynamic_owner(wall: PublicSourceWall, role: str, relative: str,
                  fingerprint: str) -> tuple:
    require(relative in (SOURCE, PROTOCOL, CONTRACT),
            "reject unrelated live V2 source-freeze owner")
    digest_pin(fingerprint, relative)
    absolute = ROOT + "/" + relative
    require(wall.approved(absolute), "reject unlisted live V2 owner")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(absolute, flags)
    try:
        found = os.fstat(descriptor)
        require(stat.S_ISREG(found.st_mode)
                and stat.S_IMODE(found.st_mode) == 0o600
                and found.st_dev == DEVICE and found.st_uid == os.geteuid()
                and found.st_nlink == 1
                and 0 < found.st_size <= MAX_OWNER_BYTES,
                "reject exchanged live V2 source owner")
        return role, relative, fingerprint, found.st_size, found.st_ino
    finally:
        os.close(descriptor)


def decode_base64(value: object, maximum: int,
                  label: str) -> bytes:
    require(type(value) is str and bool(value)
            and len(value) <= ((maximum + 2) // 3) * 4
            and len(value) % 4 == 0 and value.isascii(),
            "reject truncated or unbounded public diagnostic base64: " + label)
    text = value.encode("ascii")
    padding = len(text) - len(text.rstrip(b"="))
    require(padding in (0, 1, 2) and b"=" not in text[:-padding or None],
            "reject noncanonical public diagnostic padding: " + label)
    result = bytearray()
    for offset in range(0, len(text), 4):
        block = text[offset:offset + 4]
        require(all(char in BASE64_VALUES or char == 61 for char in block),
                "reject non-base64 public diagnostic: " + label)
        values = [BASE64_VALUES.get(char, 0) for char in block]
        packed = ((values[0] << 18) | (values[1] << 12)
                  | (values[2] << 6) | values[3])
        result.append((packed >> 16) & 255)
        if block[2] != 61:
            result.append((packed >> 8) & 255)
        if block[3] != 61:
            result.append(packed & 255)
    require(len(result) <= maximum,
            "reject oversized decoded actual diagnostic: " + label)
    if padding == 1:
        require(BASE64_VALUES[text[-2]] & 3 == 0,
                "reject noncanonical final base64 padding bits")
    if padding == 2:
        require(BASE64_VALUES[text[-3]] & 15 == 0,
                "reject noncanonical final base64 padding bits")
    return bytes(result)


def bootstrap_semantic(wall: PublicSourceWall,
                       raw: bytes) -> types.ModuleType:
    row = PUBLIC_OWNERS[5]
    require(sha256(raw) == SEMANTIC_SOURCE_SHA and len(raw) == row[3],
            "authenticate entire immutable public V1 source before execution")
    module = types.ModuleType("_rebar_capture_shape_v2_exact_public_v1")
    module.__file__ = ROOT + "/" + row[1]
    exec(compile(raw, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    require(module.SOURCE == row[1]
            and module.PROTOCOL == PUBLIC_OWNERS[6][1]
            and module.CONTRACT == PUBLIC_OWNERS[7][1]
            and module.SCHEMA
            == "rebar-owned-rust-capture-shape-semantics-v1-source-freeze"
            and module.DERIVED_BRIDGE_SHA256 == F9_SHA
            and module.DERIVED_BRIDGE_BYTES == 179147
            and callable(module.StrictJSON) and callable(module.canonical)
            and callable(module.validate_ledger)
            and callable(module.validate_oracle_sources),
            "reject substituted public V1 literals or strict evidence parser")
    no_matching_imports()
    return module


def decode_json(semantic: types.ModuleType, raw: bytes,
                label: str) -> dict:
    value = semantic.StrictJSON(raw).decode()
    require(type(value) is dict,
            "require one complete strict public JSON object: " + label)
    return value


def verify_rows(value: object, suites: tuple, title: str) -> None:
    require(type(value) is list and len(value) == 13,
            "require all 13 complete published original rows: " + title)
    pids: set[int] = set()
    for row, expected in zip(value, suites, strict=True):
        require(type(row) is dict and set(row) == {
            "suite", "case_execution_denominator", "fully_observed",
            "mismatch_count", "verified_passing_case_count", "failure_class",
            "pid", "returncode", "actual_worker_started", "worker_attempted",
            "complete_original_row_sha256",
        }, "reject omitted or extra published suite fields: " + title)
        actual = (row.get("suite"), row.get("case_execution_denominator"),
                  row.get("fully_observed"), row.get("mismatch_count"),
                  row.get("verified_passing_case_count"),
                  row.get("failure_class"), row.get("pid"),
                  row.get("returncode"),
                  row.get("complete_original_row_sha256"))
        require(actual == expected
                and row.get("actual_worker_started") is True
                and row.get("worker_attempted") is True
                and row["pid"] not in pids,
                "reject forged, borrowed, or reordered original row: "
                + expected[0])
        pids.add(row["pid"])
    require(sum(row[1] for row in suites) == 31237 and len(pids) == 13,
            "reject altered original denominator or real worker identities")


def validate_originals(value: object) -> None:
    expected = {
        "bridge_source": (
            "candidates/rust/py_bridge.c",
            "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
            175676, 419054, 0o600),
        "adapter": (
            "candidates/rust_candidate.py",
            "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
            31151, 428100, 0o600),
        "engine": (
            "candidates/_rust_engine.so",
            "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4",
            660440, 430563, 0o755),
        "bridge": (
            "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
            "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15",
            144992, 430629, 0o755),
    }
    require(type(value) is dict and set(value) == set(expected),
            "require all four genuine receipt-attested original owners")
    for role, (relative, fingerprint, count, inode, mode) in expected.items():
        owner = value[role]
        require(type(owner) is dict and set(owner) == {
            "relative", "path", "sha256", "bytes", "size_bytes", "device",
            "inode", "mode", "uid", "nlink",
        } and owner == {
            "relative": relative, "path": ROOT + "/" + relative,
            "sha256": fingerprint, "bytes": count, "size_bytes": count,
            "device": DEVICE, "inode": inode, "mode": mode,
            "uid": os.geteuid(), "nlink": 1,
        }, "reject forged receipt-only original Rust identity: " + role)


def validate_prior_v20(value: dict) -> None:
    expected = {
        "schema": "rebar-owned-repaired-rust-original-campaign-v20-"
                  "durable-publication-receipt",
        "status": "PASS", "publication_status": "PASS",
        "candidate_status": "FAIL", "candidate_qualified": False,
        "family": "rust",
        "label": "phase2-v21-rust-captured-findall-root-provenance-"
                 "original-p0-v20",
        "combined_bridge_source_sha256": A0_SHA,
        "combined_bridge_source_bytes": 179520,
        "case_execution_denominator": 31237, "suite_count": 13,
        "named_private_waiver_count": 13,
        "attempted_suite_count": 13, "started_suite_count": 13,
        "completed_suite_count": 12, "actual_candidate_workers": 13,
        "distinct_worker_process_id_count": 13,
        "verified_passing_case_count": 15749,
        "semantic_mismatch_count": NOT_MEASURED,
        "infrastructure_failure_count": 1,
        "all_original_observation_vectors_complete": False,
        "all_four_original_targets_restored": True,
        "worker_failure_capture_count": 1,
        "holdout": "NOT OPENED", "performance": NOT_MEASURED,
    }
    require(all(value.get(key) == expected_value
                for key, expected_value in expected.items()),
            "reject genuine measured prior a0 Rust V20 campaign evidence")
    verify_rows(value.get("suite_integrity"), SUITES_V20, "actual prior V20")
    require(sum(row[4] for row in SUITES_V20) == 15749
            and SUITES_V20[7][3] == 240 and SUITES_V20[8][3] == 1056,
            "reject observed-only prior 240/1056 original mismatch groups")


ACTUAL_KEYS = frozenset((
    "actual_candidate_workers", "actual_v22_build_archive_gzip_inflation_count",
    "actual_v22_build_archive_read_count", "actual_v22_build_archive_sha256",
    "actual_v22_build_contract_sha256", "actual_v22_build_private_root",
    "actual_v22_build_private_root_device", "actual_v22_build_private_root_inode",
    "actual_v22_build_protocol_sha256", "actual_v22_build_receipt_sha256",
    "actual_v22_build_source_sha256", "actual_v22_compiler_process_count",
    "actual_worker_process_ids", "all_four_original_targets_restored",
    "all_original_observation_vectors_complete",
    "all_original_suite_rows_validated_before_publication",
    "all_worker_failure_capture_count", "all_worker_failure_capture_scope",
    "all_worker_failure_captures", "archive", "attempted_suite_count",
    "benchmark_files_read", "campaign_contract_sha256",
    "campaign_protocol_sha256", "campaign_source_sha256",
    "candidate_qualified", "candidate_run_uses_both_complete_reference_vectors",
    "candidate_status", "case_execution_denominator", "clock_samples",
    "combined_bridge_source_bytes", "combined_bridge_source_sha256",
    "completed_suite_count", "corrected_public_adapter_bytes",
    "corrected_public_adapter_sha256", "corrected_reference_cache_records_sha256",
    "corrected_reference_case_count", "corrected_reference_process_ids",
    "corrected_reference_receipt_sha256", "corrected_reference_records_sha256",
    "current_overview_version", "distinct_worker_process_id_count",
    "duplicate_worker_process_id_count", "family", "group_atomic",
    "hidden_cases_read", "historical_authenticated_reference_count_before_publication",
    "historical_evidence_owner_count_before_publication", "holdout",
    "infrastructure_failure_count", "label", "memory",
    "missing_worker_process_id_count", "named_private_waiver_count",
    "native_bridge_bytes", "native_bridge_sha256", "native_engine_bytes",
    "native_engine_sha256", "new_repository_evidence_owner_count",
    "original_v5_producer_contract_sha256", "original_v5_producer_protocol_sha256",
    "original_v5_producer_source_sha256", "original_v5_producer_version",
    "performance", "power_failure_automatically_recovered",
    "preserved_previous_rust_semantic_mismatch_count",
    "preserved_previous_rust_verified_passing_case_count", "public_recovery_root",
    "publication_pass_means", "publication_status",
    "published_current_v86_inputs_sha256", "published_current_v86_source_sha256",
    "published_current_v86_summary_sha256", "published_current_v86_svg_sha256",
    "recovery_journal_sha256", "restoration_verified_before_publication",
    "restored_original_targets", "resulting_authenticated_reference_count",
    "resulting_repository_evidence_owner_count", "schema", "semantic_mismatch_count",
    "sigkill_automatically_recovered", "started_suite_count", "status",
    "suite_count", "suite_integrity", "timing_trials_run", "uncompressed_bytes",
    "uncompressed_chunk_count", "uncompressed_sha256", "undefined_behavior",
    "verified_passing_case_count", "winner_selected", "worker_failure_capture",
    "worker_failure_capture_complete", "worker_failure_capture_count",
))


def decode_stream(semantic: types.ModuleType, item: object,
                  expected_sha: str, expected_count: int,
                  label: str) -> bytes:
    require(type(item) is dict and item.get("available") is True
            and item.get("complete") is True
            and item.get("source_sha256") == expected_sha
            and item.get("source_size_bytes") == expected_count
            and item.get("captured_size_bytes") == expected_count,
            "reject incomplete published one-worker " + label)
    raw = decode_base64(item.get("base64"), MAX_DIAGNOSTIC_BYTES, label)
    require(len(raw) == expected_count and sha256(raw) == expected_sha,
            "reject altered complete bounded worker " + label)
    return raw


def validate_actual_failure(semantic: types.ModuleType,
                            value: dict) -> dict:
    require(type(value) is dict and len(ACTUAL_KEYS) == 96
            and set(value) == ACTUAL_KEYS,
            "reject omitted or invented complete 96-field actual V22 receipt")
    expected = {
        "schema": "rebar-owned-repaired-rust-original-campaign-v22-"
                  "durable-publication-receipt",
        "status": "PASS", "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": "FAIL", "candidate_qualified": False,
        "family": "rust",
        "label": "phase2-v22-rust-capture-shape-root-provenance-original-p0-v22",
        "campaign_source_sha256": CAMPAIGN_SOURCE_SHA,
        "campaign_protocol_sha256": CAMPAIGN_PROTOCOL_SHA,
        "campaign_contract_sha256": CAMPAIGN_CONTRACT_SHA,
        "case_execution_denominator": 31237, "suite_count": 13,
        "named_private_waiver_count": 13,
        "attempted_suite_count": 13, "started_suite_count": 13,
        "completed_suite_count": 12, "actual_candidate_workers": 13,
        "distinct_worker_process_id_count": 13,
        "duplicate_worker_process_id_count": 0,
        "missing_worker_process_id_count": 0,
        "verified_passing_case_count": 14725,
        "semantic_mismatch_count": NOT_MEASURED,
        "infrastructure_failure_count": 1,
        "all_original_observation_vectors_complete": False,
        "all_original_suite_rows_validated_before_publication": True,
        "all_four_original_targets_restored": True,
        "restoration_verified_before_publication": True,
        "combined_bridge_source_sha256": F9_SHA,
        "combined_bridge_source_bytes": 179147,
        "actual_v22_build_source_sha256": BUILD_SOURCE_SHA,
        "actual_v22_build_protocol_sha256": BUILD_PROTOCOL_SHA,
        "actual_v22_build_contract_sha256": BUILD_CONTRACT_SHA,
        "actual_v22_build_receipt_sha256": PUBLIC_OWNERS[11][2],
        "actual_v22_build_archive_read_count": 0,
        "actual_v22_build_archive_gzip_inflation_count": 0,
        "actual_v22_compiler_process_count": 28,
        "corrected_reference_case_count": 6912,
        "corrected_reference_process_ids": [81, 82],
        "candidate_run_uses_both_complete_reference_vectors": True,
        "original_v5_producer_version": 5,
        "worker_failure_capture_count": 1,
        "all_worker_failure_capture_count": 1,
        "worker_failure_capture_complete": True,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "holdout": "NOT OPENED", "performance": NOT_MEASURED,
        "memory": NOT_MEASURED, "undefined_behavior": NOT_MEASURED,
        "winner_selected": False,
    }
    require(all(value.get(key) == expected_value
                for key, expected_value in expected.items()),
            "never convert durable V22 failure publication into candidate success")
    verify_rows(value.get("suite_integrity"), SUITES_V22,
                "genuine actual first-party Rust V22")
    require(sum(row[4] for row in SUITES_V22) == 14725
            and sum(row[3] for row in SUITES_V22
                    if type(row[3]) is int) == 2018
            and SUITES_V22[4][3] == 42 and SUITES_V22[7][3] == 352
            and SUITES_V22[8][3] == 1624
            and SUITES_V22[10][3] == NOT_MEASURED,
            "preserve exactly observed 42/352/1624 and unfinished child")
    require(value.get("actual_worker_process_ids")
            == [row[6] for row in SUITES_V22],
            "preserve all 13 exact independent actual Rust process identities")
    validate_originals(value.get("restored_original_targets"))
    capture = value.get("worker_failure_capture")
    require(type(capture) is dict and capture.get("actual_failure_count") == 1
            and capture.get("all_failure_metadata_preserved") is True
            and capture.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v22-"
            "complete-bounded-worker-failure-capture",
            "preserve the one actual incomplete worker and its diagnostics")
    first = capture.get("first_worker_failure")
    require(type(first) is dict and first.get("suite") == "subinterpreter_v2"
            and first.get("pid") == 188 and first.get("returncode") == 2
            and first.get("error_type") == "CampaignError"
            and first.get("stdout_complete") is True
            and first.get("stderr_complete") is True
            and first.get("traceback_complete") is True,
            "reject fabricated or suppressed one-worker guard failure")
    stdout = decode_stream(
        semantic, first.get("stdout"),
        "981d63efa1b23af1227a797aaa6d1857fb3b2c6c15c680c8e4ede054cefeed7e",
        1052, "stdout",
    )
    stderr = decode_stream(
        semantic, first.get("stderr"),
        "96858958d5329b881acc0581f548aeea5cee5b6429f4f10fc6a28419f676ee0b",
        10183, "stderr",
    )
    actual_worker = decode_json(semantic, stdout, "authentic actual V22 worker")
    require(actual_worker.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v22-"
            "actual-original-suite-worker-failure"
            and actual_worker.get("status") == "FAIL"
            and actual_worker.get("failure_class") == "INFRASTRUCTURE FAILURE"
            and actual_worker.get("suite") == "subinterpreter_v2"
            and actual_worker.get("actual_candidate_workers") == 1
            and actual_worker.get("actual_candidate_imports") == 1
            and actual_worker.get("actual_native_libraries_loaded") == 2
            and actual_worker.get("runtime_guard_installed_before_candidate_import")
            is True
            and actual_worker.get("semantic_mismatch_count") == NOT_MEASURED,
            "preserve actual loaded candidate, guard, native owners and failure")
    marker = b"REBAR-V16-AUTHENTIC-PRODUCER-FAILURE "
    require(stderr.count(marker) == 1
            and stderr.count(b"remaining subinterpreters") == 1
            and stderr.count(
                b"AttributeError: 'NoneType' object has no attribute 'free'"
            ) == 16,
            "scope exactly one interpreter and 16 destructor warnings to PID188")
    line = stderr.split(b"\n", 1)[0]
    require(line.startswith(marker),
            "preserve the one complete authentic actual producer diagnostic")
    diagnostic = decode_json(semantic, line[len(marker):],
                             "authentic actual V22 producer failure")
    chain = diagnostic.get("authentic_exception_chain")
    require(diagnostic.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v22-"
            "authenticated-original-producer-failure"
            and diagnostic.get("status") == "FAIL"
            and diagnostic.get("diagnostic_only") is True
            and diagnostic.get("suite") == "subinterpreter_v2"
            and diagnostic.get("completed_candidate_case_count") == 0
            and type(chain) is list and len(chain) == 3
            and [item.get("exception_type") for item in chain]
            == ["ActualSuiteFailure", "ActualSuiteFailure", "GuardError"]
            and chain[-1].get("message", {}).get("text")
            == "runtime guard blocked missing-or-fabricated-native-child-creation",
            "never invent a successful native child or exact case root cause")
    record = diagnostic.get("complete_canonical_failure_details")
    require(type(record) is dict and record.get("complete") is True
            and record.get("source_sha256")
            == "244b82a3f2ea842d2e154214b5094b08b8ec7fa3ea17b54a3a86734d3f1d442c"
            and record.get("source_size_bytes") == 1911,
            "reject discarded actual nested child lifecycle evidence")
    nested_raw = decode_base64(record.get("base64"), 16384,
                               "complete actual child lifecycle")
    require(len(nested_raw) == 1911
            and sha256(nested_raw) == record["source_sha256"],
            "reject changed complete actual child failure bytes")
    nested = decode_json(semantic, nested_raw,
                         "complete authentic original V5 child failure")
    detail = nested.get("complete_original_failure_details")
    require(nested.get("schema")
            == "rebar-owned-six-family-original-p0-producer-v5-"
            "genuine-nested-failure"
            and nested.get("status") == "FAIL"
            and nested.get("actual_child_guards_installed") == 0
            and nested.get("expected_interpreters_created") == 11
            and nested.get("expected_case_interpreter_exec_calls") == 394
            and type(detail) is dict
            and detail.get("active_phase")
            == "create-genuine-owned-interpreter-A"
            and detail.get("actual_interpreters_created") == 0
            and detail.get("actual_interpreters_destroyed") == 0
            and detail.get("actual_prepared_interpreter_ids") == []
            and detail.get("actual_initialization_interpreter_exec_calls") == 0
            and detail.get("actual_case_interpreter_exec_calls") == 0
            and detail.get("actual_guard_cleanup_interpreter_exec_calls") == 0
            and detail.get("error_type") == "GuardError"
            and detail.get("error_message")
            == "runtime guard blocked missing-or-fabricated-native-child-creation",
            "never count an unattested, generated, or missing child as genuine")
    failures = value.get("all_worker_failure_captures")
    require(type(failures) is list and len(failures) == 1
            and failures[0].get("suite") == "subinterpreter_v2"
            and failures[0].get("pid") == 188,
            "never silently omit or multiply genuine worker warnings")
    return {"warning_scope": "ONLY ACTUAL SUBINTERPRETER WORKER PID 188",
            "remaining_interpreter_warnings": 1,
            "destructor_warnings": 16,
            "actual_interpreters_created": 0,
            "actual_interpreters_destroyed": 0,
            "actual_case_interpreter_exec_calls": 0,
            "nested_failure_sha256": record["source_sha256"]}


def validate_campaign(value: dict) -> None:
    require(type(value) is dict and len(value) == 435
            and value.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v22-"
            "recoverable-source-freeze"
            and value.get("status")
            == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
            and value.get("version") == 22
            and value.get("goal_sha256") == GOAL_SHA
            and value.get("source_sha256") == CAMPAIGN_SOURCE_SHA
            and value.get("protocol_sha256") == CAMPAIGN_PROTOCOL_SHA
            and value.get("previous_v21_frozen_contract_field_count") == 402
            and value.get("case_execution_denominator") == 31237
            and value.get("suite_count") == 13
            and value.get("private_waiver_count") == 13
            and value.get("supplemental_case_count") == 8244
            and value.get("supplemental_cases_counted_in_original_denominator")
            is False
            and value.get("expanded_holdout_proposal_case_count") == 14155776
            and value.get("expanded_holdout_cases_generated") == 0
            and value.get("expanded_holdout_cases_opened") == 0
            and value.get("actual_v22_build_source_sha256") == BUILD_SOURCE_SHA
            and value.get("actual_v22_build_protocol_sha256")
            == BUILD_PROTOCOL_SHA
            and value.get("actual_v22_build_contract_sha256")
            == BUILD_CONTRACT_SHA
            and value.get("actual_v22_corrected_bridge_source_sha256") == F9_SHA
            and value.get("actual_v22_corrected_bridge_source_bytes") == 179147
            and value.get("operational_guard_version") == 3
            and value.get("required_native_owner_field_count") == 14
            and value.get("expected_real_child_interpreters") == 11
            and value.get("expected_original_case_interpreter_exec_calls") == 394
            and value.get("expected_total_real_interpreter_exec_calls") == 416
            and value.get("candidate_correctness") == NOT_MEASURED
            and value.get("qualified_candidate_count") == 0
            and value.get("holdout") == "NOT OPENED"
            and value.get("performance") == NOT_MEASURED
            and value.get("winner_selected") is False,
            "preserve all 435 genuine current and 402 inherited obligations")


def validate_native_build(semantic: dict, receipt: dict,
                          root: dict) -> None:
    require(type(semantic) is dict
            and semantic.get("schema")
            == "rebar-phase2-owned-rust-capture-shape-semantics-"
            "source-build-v22-source-freeze"
            and semantic.get("version") == 22
            and semantic.get("family") == "rust"
            and semantic.get("source", {}).get("sha256") == BUILD_SOURCE_SHA
            and semantic.get("protocol", {}).get("sha256") == BUILD_PROTOCOL_SHA,
            "reject stale public V22 first-party build source freeze")
    feature = semantic.get("independently_frozen_semantic_correction")
    family = semantic.get("owned_first_party_rust_family")
    bounds = semantic.get("frozen_python_correctness")
    require(type(feature) is dict and feature.get("base_bridge_sha256") == A0_SHA
            and feature.get("base_bridge_bytes") == 179520
            and feature.get("derived_bridge_sha256") == F9_SHA
            and feature.get("derived_bridge_bytes") == 179147
            and feature.get("changed_functions") == [
                "rust_restore_original_template_error",
                "rust_replacement_cache",
            ] and feature.get("preserved_two_capture_fast_path_lines") == 17
            and feature.get("unchanged_original_rust_matching_engine") is True
            and feature.get("new_external_package") is False
            and feature.get("new_matching_fallback") is False
            and type(family) is dict
            and family.get("canonical_source_count") == 9
            and family.get("external_cargo_dependency_count") == 0
            and family.get("stdlib_regex_engine") == "FORBIDDEN"
            and family.get("external_regular_expression_engine") == "FORBIDDEN"
            and family.get("cross_candidate_engine") == "FORBIDDEN"
            and family.get("matching_fallback") == "FORBIDDEN"
            and type(bounds) is dict
            and bounds.get("original_case_count") == 31237
            and bounds.get("original_suite_count") == 13
            and bounds.get("separate_supplemental_reference_case_count") == 8244
            and bounds.get("supplemental_counted_in_original_denominator")
            is False,
            "reject genuine first-party f9/a0, capture, engine, or P0 evidence")
    require(type(receipt) is dict
            and receipt.get("schema")
            == "rebar-phase2-owned-rust-capture-shape-semantics-"
            "source-build-v22-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("source_sha256") == BUILD_SOURCE_SHA
            and receipt.get("protocol_sha256") == BUILD_PROTOCOL_SHA
            and receipt.get("contract_sha256") == BUILD_CONTRACT_SHA
            and receipt.get("actual_compiler_process_count") == 28
            and receipt.get("combined_bridge_sha256") == F9_SHA
            and receipt.get("combined_bridge_bytes") == 179147
            and receipt.get("candidate_matching") == "NOT RUN"
            and receipt.get("candidate_qualified") is False,
            "reject genuine public-only offline f9 native-build receipt")
    require(type(root) is dict
            and root.get("schema")
            == "rebar-phase2-owned-rust-capture-shape-semantics-"
            "source-build-v22-durable-root-provenance-receipt"
            and root.get("status") == "PASS"
            and root.get("source_sha256") == BUILD_SOURCE_SHA
            and root.get("protocol_sha256") == BUILD_PROTOCOL_SHA
            and root.get("contract_sha256") == BUILD_CONTRACT_SHA
            and root.get("canonical_build_receipt_sha256")
            == PUBLIC_OWNERS[11][2]
            and root.get("actual_compiler_process_count") == 28
            and root.get("actual_source_phase_count") == 2,
            "reject publicly attested V22 root without opening private root")


def validate_v1_contract(value: dict) -> None:
    require(type(value) is dict
            and value.get("schema")
            == "rebar-owned-rust-capture-shape-semantics-v1-source-freeze"
            and value.get("version") == 1
            and value.get("source", {}).get("sha256") == SEMANTIC_SOURCE_SHA
            and value.get("protocol", {}).get("sha256")
            == SEMANTIC_PROTOCOL_SHA,
            "preserve the full immutable V1 public source contract")
    bridge = value.get("derived_first_party_bridge")
    require(type(bridge) is dict
            and bridge.get("source_base_sha256") == A0_SHA
            and bridge.get("source_base_bytes") == 179520
            and bridge.get("sha256") == F9_SHA and bridge.get("bytes") == 179147
            and bridge.get("outer_length_probe_removed") is True
            and bridge.get("preserved_matcher_engine_source_sha256")
            == ENGINE_SOURCE_SHA
            and bridge.get("preserved_two_capture_insert_lines") == 17
            and bridge.get("subject_subject_replacement_flags") == [0, 0, 284]
            and bridge.get("new_external_regex_dependencies") == 0,
            "preserve the authentic first-party V1 a0-to-f9 source evidence")


def symbolic_reversal(semantic: types.ModuleType) -> dict:
    original = semantic.FAILED_REPLACEMENT_ORIGINAL
    corrected = semantic.FAILED_REPLACEMENT_CORRECTED
    outer = semantic.OUTER_LENGTH_REWRITE
    capture = semantic.CAPTURE_INSERTION
    require(type(original) is bytes and len(original) == 97
            and type(corrected) is bytes and len(corrected) == 384
            and type(outer) is bytes and len(outer) == 660
            and type(capture) is bytes
            and len(capture.splitlines()) == 17
            and capture.startswith(b"    if (groups == 2) {\n")
            and capture.count(b"rust_findall_item(") == 2
            and capture.count(b"PyTuple_SET_ITEM(") == 2,
            "authenticate exact complete V1 C-source anchors only")
    prefix = b"        } else {\n"
    require(original.startswith(prefix) and corrected.startswith(prefix),
            "require identical exact replacement function anchors")
    suffix = original[len(prefix):]
    require(bool(suffix) and corrected.endswith(suffix),
            "require original failed replacement tail without substitutions")
    guard = corrected[len(prefix):len(corrected) - len(suffix)]
    require(len(guard) == 287 and corrected.count(guard) == 1
            and corrected.replace(guard, b"", 1) == original
            and original.count(guard) == 0
            and original.count(b"PyObject_GetBuffer(")
            == corrected.count(b"PyObject_GetBuffer(")
            and original.count(b"PyBuffer_Release(")
            == corrected.count(b"PyBuffer_Release(")
            and original.count(b"PyObject_Hash(")
            == corrected.count(b"PyObject_Hash(")
            and b"PyObject_Length(replacement)" in outer
            and 179520 - len(outer) + len(guard) == 179147
            and 179147 - len(guard) == 178860
            and 179520 - len(outer) == 178860,
            "prove one conditional f9-to-a0 branch reversal without C reads")
    forbidden = (b'PyImport_ImportModule("re")',
                 b'PyImport_ImportModule("_sre")',
                 b'PyImport_ImportModule("regex")', b"#include <regex.h>",
                 b"#include <pcre", b"dlopen(", b"system(", b"PyRun_",
                 b"subprocess", b"fallback")
    require(not any(item in original or item in corrected for item in forbidden),
            "reject delegated matching or native additions in one-site anchors")
    events = semantic.validate_ledger(semantic.EXPECTED_LEDGER)
    require(events == semantic.EXPECTED_LEDGER
            and tuple(row[2] for row in events if row[0] == "acquire")
            == (0, 0, 284)
            and tuple(row[1] for row in events if row[0] == "release")
            == ("replacement", "subject", "subject"),
            "prove solely synthetic 0,0,284 acquisition and LIFO release")
    return {
        "mode": "EXACT SYMBOLIC PUBLIC-SOURCE ANCHORS; FULL SOURCE NOT READ",
        "measured_predecessor_bridge_sha256": A0_SHA,
        "measured_predecessor_bridge_bytes": 179520,
        "measured_actual_bridge_sha256": F9_SHA,
        "measured_actual_bridge_bytes": 179147,
        "original_replacement_anchor_bytes": len(original),
        "actual_replacement_anchor_bytes": len(corrected),
        "removed_early_replacement_guard_bytes": len(guard),
        "preserved_removed_outer_length_block_bytes": len(outer),
        "expected_complete_variant_bytes_from_anchor_arithmetic": 178860,
        "complete_variant_bytes_observed": NOT_MEASURED,
        "complete_variant_sha256": NOT_MEASURED,
        "complete_variant_materialized": False,
        "candidate_source_files_read": 0,
        "matching_engine_source_read": 0,
        "native_libraries_loaded": 0,
        "changed_function_count": 1,
        "changed_functions": ["rust_replacement_cache"],
        "replacement_site_count": 1,
        "outer_length_correction_retained": "PROVEN BY ANCHOR ARITHMETIC ONLY",
        "two_capture_fast_path": "UNCHANGED; AUTHENTICATED PUBLIC V1 METADATA",
        "match_engine": "UNCHANGED; AUTHENTICATED PUBLIC V1 METADATA",
        "matching_engine_source_sha256": ENGINE_SOURCE_SHA,
        "replacement_exporter_exception": NOT_MEASURED,
        "replacement_memoryview_exception": NOT_MEASURED,
        "actual_case_root_cause": NOT_MEASURED,
        "actual_corrected_case_outcome": NOT_MEASURED,
        "additional_buffer_acquisitions": 0,
        "additional_buffer_releases": 0,
        "additional_hash_probes": 0,
        "synthetic_acquisition_flags": [0, 0, 284],
        "synthetic_release_roles": ["replacement", "subject", "subject"],
        "synthetic_ledger": [list(row) for row in events],
        "synthetic_ledger_is_actual_matching": False,
        "external_regex_packages": 0,
        "stdlib_matching_delegation": False,
        "other_candidate_delegation": False,
        "fallback": False,
        "build": "NOT RUN", "matching": "NOT RUN",
        "correctness": NOT_MEASURED, "qualification": "NOT ESTABLISHED",
    }


def build_contract(source_row: tuple, protocol_row: tuple,
                   symbol: dict, diagnostics: dict) -> dict:
    return {
        "schema": SCHEMA, "version": VERSION,
        "status": "SOURCE FROZEN; NOT BUILT; NOT RUN; NOT BENCHMARKED",
        "phase": "PHASE 2: FIRST-PARTY CANDIDATE CORRECTNESS",
        "family": "rust",
        "source": {"path": source_row[1], "sha256": source_row[2],
                   "bytes": source_row[3]},
        "protocol": {"path": protocol_row[1], "sha256": protocol_row[2],
                     "bytes": protocol_row[3]},
        "authenticated_public_plaintext_owners": [
            {"role": role, "path": path, "sha256": fingerprint,
             "bytes": count, "device": DEVICE, "inode": inode,
             "mode": "0600", "uid": os.geteuid(), "nlink": 1}
            for role, path, fingerprint, count, inode in PUBLIC_OWNERS
        ],
        "source_wall": {
            "policy": "DENY DEFAULT; EXACT PUBLIC PLAINTEXT OWNERS ONLY",
            "installed_before_predecessor": True,
            "candidate_paths_allowed": 0,
            "historical_candidate_paths_allowed": 0,
            "phase3_proposal_paths_allowed": 0,
            "private_root_paths_allowed": 0,
            "compressed_archive_paths_allowed": 0,
            "foreign_descriptors_allowed": 0,
            "direct_io_allowed": False,
            "direct_os_metadata_allowed": False,
            "timing_allowed": False,
            "entropy_allowed": False,
        },
        "immutable_v1_semantic_source": {
            "source_sha256": SEMANTIC_SOURCE_SHA,
            "protocol_sha256": SEMANTIC_PROTOCOL_SHA,
            "contract_sha256": SEMANTIC_CONTRACT_SHA,
            "load_context_executed": False,
            "candidate_source_read": False,
        },
        "immutable_native_v22_build": {
            "source_sha256": BUILD_SOURCE_SHA,
            "protocol_sha256": BUILD_PROTOCOL_SHA,
            "contract_sha256": BUILD_CONTRACT_SHA,
            "public_build_receipt_sha256": PUBLIC_OWNERS[11][2],
            "public_root_receipt_sha256": PUBLIC_OWNERS[12][2],
            "actual_compiler_process_count": 28,
            "individual_compiler_process_ids": "NOT PUBLISHED",
            "private_root_opened": False,
            "native_loaded_by_source_freeze": False,
            "build_controller_executed": False,
        },
        "immutable_actual_v22_campaign": {
            "source_sha256": CAMPAIGN_SOURCE_SHA,
            "protocol_sha256": CAMPAIGN_PROTOCOL_SHA,
            "contract_sha256": CAMPAIGN_CONTRACT_SHA,
            "complete_current_contract_field_count": 435,
            "complete_inherited_v21_contract_field_count": 402,
            "campaign_controller_executed": False,
            "actual_failure_receipt_sha256": ACTUAL_SHA,
            "actual_failure_receipt_bytes": 47336,
            "actual_failure_receipt_device": DEVICE,
            "actual_failure_receipt_inode": 525371,
        },
        "measured_actual_v22_rust": {
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": "FAIL", "candidate_qualified": False,
            "original_case_denominator": 31237,
            "original_suite_count": 13,
            "named_private_waiver_count": 13,
            "attempted_worker_count": 13,
            "distinct_worker_process_count": 13,
            "completed_suite_count": 12,
            "fully_passing_suite_count": 9,
            "verified_passing_case_count": 14725,
            "fully_observed_mismatch_lower_bound": 2018,
            "fully_observed_suite_mismatch_counts": {
                "managed_v1": 42, "substitution_v2": 352,
                "shape_v2": 1624,
            },
            "passed_cases_in_failing_groups": "NOT CLAIMED",
            "global_semantic_mismatch_count": NOT_MEASURED,
            "infrastructure_failure_count": 1,
            "incomplete_suite": "subinterpreter_v2",
            "incomplete_suite_denominator": 128,
            "all_four_original_targets_restored": True,
            "all_original_suite_row_sha256": [row[8] for row in SUITES_V22],
            "actual_worker_process_ids": [row[6] for row in SUITES_V22],
            "separate_corrected_reference_case_count": 6912,
            "separate_corrected_reference_process_ids": [81, 82],
            "corrected_reference_counted_in_original_denominator": False,
        },
        "measured_prior_v20_rust": {
            "receipt_sha256": PUBLIC_OWNERS[16][2],
            "candidate_status": "FAIL", "candidate_qualified": False,
            "measured_bridge_sha256": A0_SHA,
            "measured_bridge_bytes": 179520,
            "original_case_denominator": 31237,
            "original_suite_count": 13,
            "completed_suite_count": 12,
            "verified_passing_case_count": 15749,
            "fully_observed_suite_mismatch_counts": {
                "substitution_v2": 240, "shape_v2": 1056,
            },
            "global_semantic_mismatch_count": NOT_MEASURED,
            "infrastructure_failure_count": 1,
            "all_four_original_targets_restored": True,
            "all_original_suite_row_sha256": [row[8] for row in SUITES_V20],
        },
        "actual_one_worker_child_diagnostics": diagnostics,
        "proposed_symbolic_first_party_correction": symbol,
        "frozen_correctness_boundaries": {
            "cpython": "3.14.6",
            "original_case_count": 31237,
            "original_suite_count": 13,
            "named_private_waivers": 13,
            "supplemental_differential_case_count": 8244,
            "supplemental_counted_in_original_denominator": False,
            "corrected_reference_vector_case_count": 6912,
            "corrected_reference_counted_in_original_denominator": False,
            "qualified_independent_candidate_count": 0,
        },
        "source_only_effects": {
            "candidate_source_files_read": 0,
            "historical_capture_files_read": 0,
            "phase3_proposal_files_read": 0,
            "candidate_imports": 0,
            "candidate_workers_started": 0,
            "compiler_processes_started": 0,
            "native_libraries_loaded": 0,
            "private_root_opens": 0,
            "archive_opens": 0,
            "archive_inflations": 0,
            "foreign_descriptor_reads": 0,
            "metadata_probes": 0,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "variant_source_materialized": False,
            "variant_build": "NOT RUN",
            "variant_matching": "NOT RUN",
            "variant_correctness": NOT_MEASURED,
            "variant_qualified": False,
            "whole_variant_sha256": NOT_MEASURED,
            "expanded_holdout_proposal_case_count": 14155776,
            "expanded_holdout_cases": "NOT FROZEN; NOT GENERATED; NOT OPENED",
            "holdout": "NOT OPENED",
            "performance": NOT_MEASURED,
            "memory": NOT_MEASURED,
            "confidence_intervals": NOT_MEASURED,
            "undefined_behavior": NOT_MEASURED,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "qualified_candidate_count": 0,
            "winner_selected": False,
        },
    }


def canonical_document(semantic: types.ModuleType, value: object) -> bytes:
    return (semantic.canonical(value) + "\n").encode("utf-8")


def clone(semantic: types.ModuleType, value: object) -> object:
    return semantic.StrictJSON(canonical_document(semantic, value)).decode()


def reject(action: object, label: str, *kinds: type) -> str:
    require(callable(action), "require executable hostile source-only control")
    try:
        action()
    except (FreezeError, OSError, ValueError, TypeError, KeyError,
            IndexError, UnicodeError, OverflowError, *kinds):
        return label
    raise FreezeError("accepted hostile public-only source control: " + label)


def self_test(wall: PublicSourceWall, semantic: types.ModuleType,
              context: dict, state: dict) -> list[str]:
    checks: list[str] = []
    kinds = (semantic.FreezeError,)
    actual = state["actual"]
    prior = state["prior"]
    symbol = state["symbolic"]
    require(type(symbol) is dict
            and symbol.get("complete_variant_sha256") == NOT_MEASURED
            and symbol.get("complete_variant_materialized") is False,
            "never infer full variant bytes from public metadata")

    for key in sorted(ACTUAL_KEYS):
        forged = clone(semantic, actual)
        require(type(forged) is dict, "clone the complete actual V22 receipt")
        forged.pop(key)
        checks.append(reject(
            lambda item=forged: validate_actual_failure(semantic, item),
            "reject-missing-actual-v22-receipt-field-" + key, *kinds,
        ))
    for key, value in (
            ("candidate_status", "PASS"), ("candidate_qualified", True),
            ("publication_pass_means", "CANDIDATE PASSED"),
            ("case_execution_denominator", 31236), ("suite_count", 12),
            ("completed_suite_count", 13), ("actual_candidate_workers", 12),
            ("distinct_worker_process_id_count", 12),
            ("verified_passing_case_count", 29219),
            ("semantic_mismatch_count", 2018),
            ("all_original_observation_vectors_complete", True),
            ("infrastructure_failure_count", 0),
            ("combined_bridge_source_sha256", A0_SHA),
            ("corrected_reference_case_count", 8244),
            ("hidden_cases_read", 1), ("clock_samples", 1),
            ("holdout", "OPENED"), ("performance", "1.5x"),
            ("winner_selected", True)):
        forged = clone(semantic, actual)
        assert isinstance(forged, dict)
        forged[key] = value
        checks.append(reject(
            lambda item=forged: validate_actual_failure(semantic, item),
            "reject-forged-actual-v22-" + key, *kinds,
        ))
    extra = clone(semantic, actual)
    assert isinstance(extra, dict)
    extra["__unpublished_synthetic_field__"] = True
    checks.append(reject(
        lambda: validate_actual_failure(semantic, extra),
        "reject-extra-actual-v22-receipt-field", *kinds,
    ))
    for index, (name, *_rest) in enumerate(SUITES_V22):
        for field, forged_value in (
                ("pid", 0), ("complete_original_row_sha256", "0" * 64),
                ("case_execution_denominator", 0)):
            bad = clone(semantic, actual)
            assert isinstance(bad, dict)
            bad["suite_integrity"][index][field] = forged_value
            checks.append(reject(
                lambda item=bad: validate_actual_failure(semantic, item),
                "reject-forged-actual-v22-row-" + name + "-" + field,
                *kinds,
            ))
    for index, value in ((4, 0), (7, 0), (8, 0), (10, 0)):
        bad = clone(semantic, actual)
        assert isinstance(bad, dict)
        bad["suite_integrity"][index]["mismatch_count"] = value
        checks.append(reject(
            lambda item=bad: validate_actual_failure(semantic, item),
            "reject-hidden-managed-substitution-shape-or-child-"
            + SUITES_V22[index][0], *kinds,
        ))
    for role in ("bridge_source", "adapter", "engine", "bridge"):
        bad = clone(semantic, actual)
        assert isinstance(bad, dict)
        bad["restored_original_targets"][role]["inode"] = 1
        checks.append(reject(
            lambda item=bad: validate_actual_failure(semantic, item),
            "reject-forged-receipt-only-restored-original-" + role, *kinds,
        ))
    for stream in ("stdout", "stderr"):
        bad = clone(semantic, actual)
        assert isinstance(bad, dict)
        bad["worker_failure_capture"]["first_worker_failure"][stream][
            "source_sha256"
        ] = "0" * 64
        checks.append(reject(
            lambda item=bad: validate_actual_failure(semantic, item),
            "reject-forged-complete-actual-worker-" + stream, *kinds,
        ))
    for key, value in (
            ("candidate_status", "PASS"),
            ("verified_passing_case_count", 31237),
            ("semantic_mismatch_count", 1296),
            ("combined_bridge_source_sha256", F9_SHA),
            ("completed_suite_count", 13)):
        bad = clone(semantic, prior)
        assert isinstance(bad, dict)
        bad[key] = value
        checks.append(reject(
            lambda item=bad: validate_prior_v20(item),
            "reject-forged-genuine-prior-a0-v20-" + key, *kinds,
        ))

    original = semantic.FAILED_REPLACEMENT_ORIGINAL
    corrected = semantic.FAILED_REPLACEMENT_CORRECTED
    for attr, value, label in (
            ("FAILED_REPLACEMENT_ORIGINAL", original + b"\n", "original-anchor"),
            ("FAILED_REPLACEMENT_CORRECTED", corrected + b"\n", "actual-anchor"),
            ("OUTER_LENGTH_REWRITE", semantic.OUTER_LENGTH_REWRITE + b"\n",
             "outer-length-removal"),
            ("CAPTURE_INSERTION", b"forged", "captured-findall-anchor")):
        old = getattr(semantic, attr)
        setattr(semantic, attr, value)
        try:
            checks.append(reject(
                lambda: symbolic_reversal(semantic),
                "reject-forged-symbolic-one-site-" + label, *kinds,
            ))
        finally:
            setattr(semantic, attr, old)
    for offset, replacement in (
            (0, ("acquire", "replacement", 0, 0, 1)),
            (1, ("acquire", "subject", 0, 0, 1)),
            (2, ("acquire", "replacement", 0, 0, 1)),
            (3, ("release", "subject", None, 2, 1)),
            (4, ("release", "replacement", None, 1, 0)),
            (5, ("release", "subject", None, 2, 1))):
        forged = list(semantic.EXPECTED_LEDGER)
        forged[offset] = replacement
        checks.append(reject(
            lambda item=forged: semantic.validate_ledger(item),
            "reject-forged-synthetic-buffer-role-flags-lifo-" + str(offset),
            *kinds,
        ))

    historical = (ROOT + "/candidates/rust/variants/"
                  "buffer_shape_pickle_findall_captures_v1/py_bridge.c")
    paths = (
        (historical, "historical-candidate-capture"),
        (ROOT + "/candidates/rust_candidate.py", "current-candidate"),
        (ROOT + "/candidates/rust/py_bridge.c", "current-candidate-bridge"),
        (ROOT + "/candidates/_rust_engine.so", "current-native-engine"),
        (ROOT + "/oracle/phase3/expanded-sealed-holdout-v1.json",
         "phase3-holdout-proposal"),
        (ROOT + "/tools/verify_expanded_sealed_holdout_v1.py",
         "phase3-verifier-proposal"),
        (ROOT + "/tools/../candidates/rust_candidate.py",
         "lexical-candidate-traversal"),
        (ROOT + "/tools/./../candidates/rust_candidate.py",
         "lexical-dot-candidate-traversal"),
        (ROOT + "/tools//../candidates/_rust_engine.so",
         "lexical-double-separator-native-traversal"),
        (ROOT + "/oracle/phase2/../../candidates/rust_candidate.py",
         "lexical-oracle-candidate-traversal"),
        (ROOT + "/oracle/phase2/evidence/forbidden.json.gz",
         "compressed-private-archive"),
        ("/tmp/rebar-phase2-native-build-v9-rust-y87f8wof",
         "private-native-build-root"),
        ("/tmp/rebar-hidden-holdout", "hidden-holdout"),
        ("/etc/hosts", "foreign-unowned-host-file"),
    )
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    for path, label in paths:
        checks.append(reject(
            lambda target=path: os.open(target, flags),
            "public-wall-rejects-real-os-open-" + label, *kinds,
        ))
        checks.append(reject(
            lambda target=path: wall.native_open(target, flags),
            "public-wall-rejects-native-descriptor-bypass-" + label, *kinds,
        ))
    for label, action in (
            ("builtins-open", lambda: builtins.open(historical, "rb")),
            ("direct-_io-open", lambda: _io.open(historical, "rb")),
            ("direct-_io-fileio", lambda: _io.FileIO(historical, "r")),
            ("direct-io-open", lambda: io.open(historical, "rb")),
            ("direct-io-fileio", lambda: io.FileIO(historical, "r")),
            ("unowned-descriptor-read", lambda: os.read(0, 1)),
            ("unowned-descriptor-stat", lambda: os.fstat(0)),
            ("unowned-descriptor-close", lambda: os.close(0)),
            ("unowned-descriptor-dup", lambda: os.dup(0)),
            ("unowned-descriptor-fdopen", lambda: os.fdopen(0)),
            ("candidate-stat", lambda: os.stat(historical)),
            ("candidate-lstat", lambda: os.lstat(historical)),
            ("candidate-readlink", lambda: os.readlink(historical)),
            ("candidate-access", lambda: os.access(historical, os.R_OK)),
            ("candidate-listdir", lambda: os.listdir(ROOT + "/candidates")),
            ("candidate-scandir", lambda: os.scandir(ROOT + "/candidates")),
            ("clock-time", lambda: time.time()),
            ("clock-monotonic", lambda: time.monotonic()),
            ("clock-perf-counter", lambda: time.perf_counter()),
            ("entropy-urandom", lambda: os.urandom(8)),
            ("source-write", lambda: builtins.open(ROOT + "/" + SOURCE, "w")),
            ("stdlib-matcher", lambda: sys.audit("import", "re", None)),
            ("stdlib-native-engine", lambda: sys.audit("import", "_sre", None)),
            ("external-regex-package", lambda: sys.audit("import", "regex", None)),
            ("native-dynamic-loader", lambda: sys.audit("ctypes.dlopen", "x")),
            ("compiler-process", lambda: sys.audit("subprocess.Popen", "rustc")),
            ("real-child-creation",
             lambda: sys.audit("cpython.PyInterpreterState_New")),
            ("private-temporary-root", lambda: sys.audit("tempfile.mkdtemp", "x")),
            ("network", lambda: sys.audit("socket.connect", "x")),
            ("untrusted-dynamic-code", lambda: sys.audit("exec", "x"))):
        checks.append(reject(action,
                             "public-wall-physically-rejects-" + label, *kinds))
    checks.append(reject(
        lambda: os.open(ROOT + "/" + SOURCE, os.O_RDONLY),
        "public-wall-rejects-approved-owner-without-no-follow", *kinds,
    ))
    checks.append(reject(
        lambda: os.open(ROOT + "/" + SOURCE,
                        flags | os.O_WRONLY | os.O_TRUNC),
        "public-wall-rejects-approved-source-destructive-flags", *kinds,
    ))
    no_matching_imports()
    require(wall.installed and not wall.live and bool(wall.blocked)
            and len(checks) >= 200,
            "require physical public-only controls without real candidate I/O")
    return checks


def parse_arguments(arguments: list[str]) -> dict:
    require(bool(arguments), "select exactly one source-only V2 mode")
    mode = arguments[0]
    require(mode in ("--render-contract", "--self-test",
                     "--verify-frozen-context"),
            "reject actual execution, candidate activation, and build modes")
    required = ["--source-sha256", "--protocol-sha256"]
    if mode != "--render-contract":
        required.append("--contract-sha256")
    require(len(arguments) == 1 + 2 * len(required),
            "require precisely independently pinned public source authority")
    pins: dict[str, str] = {}
    for index in range(1, len(arguments), 2):
        key, value = arguments[index], arguments[index + 1]
        require(key in required and key not in pins,
                "reject repeated or unrelated source-only caller authority")
        pins[key] = digest_pin(value, key)
    require(set(pins) == set(required),
            "reject omitted independent public source authority")
    return {"mode": mode, "pins": pins}


def load_context(wall: PublicSourceWall, pins: dict,
                 rendering: bool) -> tuple[dict, dict]:
    source_row = dynamic_owner(wall, "source", SOURCE, pins["--source-sha256"])
    protocol_row = dynamic_owner(wall, "protocol", PROTOCOL,
                                 pins["--protocol-sha256"])
    source = secure_owner(wall, source_row)
    protocol = secure_owner(wall, protocol_row)
    if not rendering:
        contract_row = dynamic_owner(wall, "contract", CONTRACT,
                                     pins["--contract-sha256"])
    public: dict[str, bytes] = {}
    for row in PUBLIC_OWNERS:
        public[row[0]] = secure_owner(wall, row)
    semantic = bootstrap_semantic(wall, public["semantic_v1_source"])
    original = decode_json(semantic, public["original_oracle"], "frozen P0")
    supplemental = decode_json(semantic, public["supplemental_oracle"],
                               "separate 8,244-case public reference")
    semantic.validate_original_oracle(original)
    semantic.validate_supplemental_oracle(supplemental)
    semantic.validate_oracle_sources(public["substitution_oracle"],
                                     public["shape_oracle"])
    prior_feature = decode_json(semantic, public["semantic_v1_contract"],
                                "immutable public V1 source freeze")
    validate_v1_contract(prior_feature)
    build = decode_json(semantic, public["native_v22_contract"],
                        "immutable public V22 source-build freeze")
    build_receipt = decode_json(semantic, public["native_v22_publication"],
                                "actual public V22 build receipt")
    root_receipt = decode_json(semantic, public["native_v22_root_receipt"],
                               "public-only V22 native-root receipt")
    validate_native_build(build, build_receipt, root_receipt)
    campaign = decode_json(semantic, public["campaign_v22_contract"],
                           "complete immutable 435-field V22 source contract")
    validate_campaign(campaign)
    prior = decode_json(semantic, public["prior_actual_v20"],
                        "actual complete measured prior a0 campaign")
    validate_prior_v20(prior)
    actual = decode_json(semantic, public["actual_v22"],
                         "actual complete measured f9 campaign")
    diagnostics = validate_actual_failure(semantic, actual)
    symbol = symbolic_reversal(semantic)
    frozen = build_contract(source_row, protocol_row, symbol, diagnostics)
    state = {
        "semantic": semantic, "actual": actual, "prior": prior,
        "campaign": campaign, "symbolic": symbol, "contract": frozen,
        "source_row": source_row, "protocol_row": protocol_row,
    }
    if not rendering:
        raw = secure_owner(wall, contract_row)
        require(raw == canonical_document(semantic, frozen)
                and decode_json(semantic, raw, "complete V2 contract") == frozen,
                "reject altered, missing, or extra frozen V2 obligations")
        state["contract_row"] = contract_row
    require(not wall.live, "close every single authorized public descriptor")
    no_matching_imports()
    return frozen, state


def main(arguments: list[str] | None = None) -> int:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.executable == PYTHON
            and sys.flags.isolated == 1 and sys.flags.no_site == 1
            and sys.dont_write_bytecode is True,
            "require exact pinned CPython 3.14.6 with -I -B -S")
    no_matching_imports()
    choice = parse_arguments(list(sys.argv[1:] if arguments is None
                                  else arguments))
    wall = PublicSourceWall()
    wall.install()
    frozen, state = load_context(wall, choice["pins"],
                                 choice["mode"] == "--render-contract")
    semantic = state["semantic"]
    if choice["mode"] == "--render-contract":
        sys.stdout.buffer.write(canonical_document(semantic, frozen))
        sys.stdout.buffer.flush()
        return 0
    checks = (self_test(wall, semantic, frozen, state)
              if choice["mode"] == "--self-test" else [])
    result = {
        "schema": SCHEMA + "-source-only-gate",
        "status": "PASS", "version": VERSION,
        "mode": choice["mode"].removeprefix("--"),
        "source_sha256": choice["pins"]["--source-sha256"],
        "protocol_sha256": choice["pins"]["--protocol-sha256"],
        "contract_sha256": choice["pins"]["--contract-sha256"],
        "authenticated_public_plaintext_owner_count": len(PUBLIC_OWNERS) + 3,
        "public_only_wall_installed_before_predecessor": wall.installed,
        "public_only_wall_live_descriptors": len(wall.live),
        "candidate_source_files_read": 0,
        "historical_capture_files_read": 0,
        "phase3_proposal_files_read": 0,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "native_libraries_loaded": 0,
        "private_root_opens": 0,
        "archive_opens": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "hostile_control_count": len(checks),
        "hostile_controls": checks,
        "physically_blocked_effects": dict(wall.blocked),
        "complete_current_v22_contract_field_count": 435,
        "complete_inherited_v21_contract_field_count": 402,
        "actual_v22_failure_receipt_sha256": ACTUAL_SHA,
        "actual_v22_candidate_status": "FAIL",
        "actual_v22_publication_status": "PASS",
        "actual_v22_publication_pass_means": "DURABLE PUBLICATION ONLY",
        "actual_v22_original_case_denominator": 31237,
        "actual_v22_distinct_worker_count": 13,
        "actual_v22_completed_suite_count": 12,
        "actual_v22_verified_passing_case_count": 14725,
        "actual_v22_observed_mismatch_lower_bound": 2018,
        "actual_v22_observed_suite_mismatch_counts": {
            "managed_v1": 42, "substitution_v2": 352, "shape_v2": 1624,
        },
        "actual_v22_global_mismatch_count": NOT_MEASURED,
        "actual_v22_child_interpreters_created": 0,
        "actual_v22_child_interpreters_destroyed": 0,
        "actual_v22_warning_scope": "ONLY ACTUAL SUBINTERPRETER WORKER PID 188",
        "actual_v22_remaining_interpreter_warning_count": 1,
        "actual_v22_worker_destructor_warning_count": 16,
        "actual_prior_v20_bridge_sha256": A0_SHA,
        "actual_prior_v20_verified_passing_case_count": 15749,
        "actual_prior_v20_observed_suite_mismatch_counts": {
            "substitution_v2": 240, "shape_v2": 1056,
        },
        "supplemental_differential_case_count": 8244,
        "supplemental_counted_in_original_denominator": False,
        "corrected_reference_vector_case_count": 6912,
        "corrected_reference_counted_in_original_denominator": False,
        "proposed_variant_materialized": False,
        "proposed_variant_expected_bytes": 178860,
        "proposed_variant_observed_bytes": NOT_MEASURED,
        "proposed_variant_sha256": NOT_MEASURED,
        "proposed_variant_build": "NOT RUN",
        "proposed_variant_correctness": NOT_MEASURED,
        "qualified_candidate_count": 0,
        "expanded_holdout_proposal_case_count": 14155776,
        "holdout": "NOT OPENED",
        "performance": NOT_MEASURED,
        "memory": NOT_MEASURED,
        "undefined_behavior": NOT_MEASURED,
        "winner_selected": False,
    }
    no_matching_imports()
    require(not wall.live, "never leak an approved public evidence descriptor")
    sys.stdout.buffer.write(canonical_document(semantic, result))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FreezeError, OSError, UnicodeError, ValueError, TypeError,
            KeyError, IndexError, OverflowError) as error:
        sys.stderr.write("Rust capture-shape V2 source freeze rejected: "
                         + str(error)[:8192] + "\n")
        raise SystemExit(1)
