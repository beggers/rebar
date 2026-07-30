#!/usr/bin/env python3
"""Freeze a real from-scratch Rust V2 source, not a native build or match.

The complete first-party 1adb bridge genuinely exists as its own new variant.
Source modes authenticate it, its exact a0 predecessor, every unchanged Rust
source, the complete V23 failure history, and the reproducible offline build
design. Actual build modes fail before opening a file: a separately committed
and pushed root-authorized 28-process build has not happened.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("a first-party Rust source freeze must not load a matcher")

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
PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
DEVICE = 2064
SOURCE = "tools/reproduce_owned_rust_capture_shape_semantics_v2_source_build_v23.py"
PROTOCOL = "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V2-SOURCE-BUILD-V23.md"
CONTRACT = "oracle/phase2/rust-capture-shape-semantics-v2-source-build-v23.json"
SCHEMA = "rebar-phase2-owned-rust-capture-shape-semantics-v2-source-build-v23"
VERSION = 23
FAMILY = "rust"
NOT_MEASURED = "NOT MEASURED"
MAX_OWNER_BYTES = 1_048_576
GOAL_SHA = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
BUILD_LABEL = "phase2-v23-rust-capture-shape-v2-root-provenance"
A0_SHA = "a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a"
F9_SHA = "f9bd2d3c8406e4b2c703ce96f42964ee15941611e22447b12acc9b54fac98055"
VARIANT_SHA = "1adb6bcecfa0b2fa80403e1c2caf372916466e8b9d0516980e60aef6a9ac08f0"
VARIANT_BYTES = 178860
MATCHER_SHA = "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d"
ADAPTER_SHA = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
ADAPTER_BYTES = 31934
RUST_TOOLCHAIN = "/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu"
RUSTC = RUST_TOOLCHAIN + "/bin/rustc"
CARGO = RUST_TOOLCHAIN + "/bin/cargo"
GCC = "/usr/bin/x86_64-linux-gnu-gcc-13"
READELF = "/usr/bin/x86_64-linux-gnu-readelf"
PYTHON_INCLUDE = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14"
)
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols", "engine_sections",
    "engine_notes", "bridge_sections", "bridge_notes",
)
GCC_FLAGS = (
    "-pthread", "-std=c11", "-shared", "-fPIC", "-O3", "-Wall",
    "-Wextra", "-Werror", "-Wl,-z,noexecstack",
    "-Wl,--exclude-libs,ALL", "-Wl,--build-id=sha1",
)
BLOCKED_ACTUAL = (
    "actual V23 native build rejected: the frozen source must first be "
    "committed and pushed and a genuine root-authorized 28-process "
    "dual-phase build is not yet available"
)

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
    ("semantic_v1_source", "tools/apply_owned_rust_capture_shape_semantics_v1.py",
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
     "7013c42f6309d94e094dd89cc8e9f24fe245c0cba5ca4791d35ffe5fa2b7dad7",
     47336, 525371),
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

CAMPAIGN_V23_OWNERS = (
    ("campaign_v23_source", "tools/run_owned_repaired_rust_original_campaign_v23.py",
     "dfa8b2a4d2a8ecbadbe36097a7dc55ce92abfeda56bf6cd0a8f02ae72b544b29",
     66129, 431185),
    ("campaign_v23_protocol",
     "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V23.md",
     "289fb9f2ddd20d3f29749f0328894be2f540eaec8485ad0d7ba4d5e932eaf68e",
     7194, 525487),
    ("campaign_v23_contract",
     "oracle/phase2/repaired-rust-original-campaign-v23.json",
     "08cb3111855de792b2708db0c281c6d110735f79f3e85a3ef6c5de9944be5aa6",
     181093, 525488),
)

NATIVE_SOURCE_OWNERS = (
    ("native_v9_source", "tools/reproduce_owned_native_source_build_v9.py",
     "c4a4b85b92ef0d600528732c9e0acb8f8303b7b2fbfc320e84c9b9e2d384219f",
     81124, 429976),
    ("native_v9_protocol", "oracle/phase2/NATIVE-SOURCE-BUILD-V9.md",
     "18494d4b778a3c958b07903996e8a1b13f4466e08b2c9e72cd5d711957dbcecc",
     4960, 524423),
    ("native_v9_contract", "oracle/phase2/native-source-build-v9.json",
     "6a4aee7f0c639b2b338d1497c35a69d35939841cf55b0dbe38abe404cea404da",
     9134, 524424),
    ("native_v16_source", "tools/reproduce_owned_rust_buffer_shape_source_build_v16.py",
     "bcea8f23fc5e52af1e8062145d75ef1a6ed835cea3ac113a155cc8ebf3116a8a",
     134640, 431980),
    ("native_v16_protocol", "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V16.md",
     "315f0a24e64b50804565f86c6ca4187024c4a1db5a23ab2f57c8805ed37f51f5",
     6497, 524984),
    ("native_v16_contract", "oracle/phase2/rust-buffer-shape-source-build-v16.json",
     "4f82f88da3329c6bacac2092af19d915d379f90101dcd9840366274355cc92b7",
     18260, 524985),
)

ADAPTER_REPAIR_OWNERS = (
    ("adapter_v3_source", "tools/apply_owned_rust_public_contract_source_repair_v3.py",
     "5e57da2379e736bba75eacdb57f84710dc144c0d4088d5827b3139a6b71d8859",
     92060, 431033),
    ("adapter_v3_protocol",
     "oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V3.md",
     "2aeb81e55548b46011c75815465d2bc2fa461d57ba7b990fc7a7b87d2d687a34",
     6405, 524675),
    ("adapter_v3_contract",
     "oracle/phase2/rust-public-contract-source-repair-v3.json",
     "82bce0066181dd16f3de52d88f31e930f25706b5ff3da2ba18b10c8b31b4f6a1",
     14817, 524678),
)

CANONICAL_RUST_OWNERS = (
    ("canonical_cargo_lock", "candidates/rust/Cargo.lock",
     "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63",
     167, 428098),
    ("canonical_cargo_manifest", "candidates/rust/Cargo.toml",
     "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966",
     225, 428094),
    ("canonical_original_bridge", "candidates/rust/py_bridge.c",
     "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
     175676, 419054),
    ("canonical_matching_engine", "candidates/rust/src/lib.rs", MATCHER_SHA,
     177967, 428096),
    ("canonical_newline", "candidates/rust/src/newline.rs",
     "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b",
     14416, 427958),
    ("canonical_search", "candidates/rust/src/search.rs",
     "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe",
     14773, 429682),
    ("canonical_stack", "candidates/rust/src/stack.rs",
     "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e",
     7269, 428151),
    ("canonical_unicode_tables", "candidates/rust/src/unicode_tables.rs",
     "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af",
     471989, 428152),
    ("canonical_original_adapter", "candidates/rust_candidate.py",
     "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
     31151, 428100),
)

A0_OWNER = (
    "captured_findall_a0_base",
    "candidates/rust/variants/buffer_shape_pickle_findall_captures_v1/py_bridge.c",
    A0_SHA, 179520, 524770,
)
VARIANT_OWNER = (
    "materialized_capture_shape_semantics_v2_bridge",
    "candidates/rust/variants/"
    "buffer_shape_pickle_findall_captures_semantics_v2/py_bridge.c",
    VARIANT_SHA, VARIANT_BYTES, 525539,
)
PARENT_STATIC_OWNERS = CAPTURE_V2_OWNERS + PUBLIC_OWNERS + GUARD_OWNERS
STATIC_OWNERS = (
    PARENT_STATIC_OWNERS + CAMPAIGN_V23_OWNERS + NATIVE_SOURCE_OWNERS
    + ADAPTER_REPAIR_OWNERS + CANONICAL_RUST_OWNERS + (A0_OWNER, VARIANT_OWNER)
)

TOOLCHAIN_OWNERS = (
    {
        "path": RUSTC,
        "sha256": "bff349e72704ff70bc08a234a3847338e797065bbedde5e556808bc87b7bf7c6",
        "bytes": 644784, "device": DEVICE, "inode": 31359570,
        "mode": 493, "uid": 1000, "nlink": 1,
    },
    {
        "path": CARGO,
        "sha256": "841072d1d92f9e841d9ba5b0814182a0adf064acf4527cd120967b7bc49dcb66",
        "bytes": 42185192, "device": DEVICE, "inode": 31359488,
        "mode": 493, "uid": 1000, "nlink": 1,
    },
    {
        "path": GCC,
        "sha256": "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26",
        "bytes": 1023032, "device": 1048708, "inode": 10445975,
        "mode": 493, "uid": 65534, "nlink": 1,
    },
    {
        "path": READELF,
        "sha256": "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0",
        "bytes": 789280, "device": 1048708, "inode": 10446013,
        "mode": 493, "uid": 65534, "nlink": 1,
    },
)
SOURCE_MODES = ("--render-contract", "--verify-frozen-context", "--self-test")
ACTUAL_MODES = ("--run", "--build")


class BuildFreezeError(Exception):
    """Reject altered Rust owners or a build without real root authority."""


def require(value: object, label: str) -> None:
    if value is not True:
        raise BuildFreezeError(label)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete genuine source bytes")
    return hashlib.sha256(raw).hexdigest()


def hash_pin(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "independently pin the complete source owner: " + label)
    assert isinstance(value, str)
    return value


def no_matching_imports() -> None:
    forbidden = (
        "re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
        "ctypes", "candidates", "rebar", "subprocess", "socket",
        "concurrent.interpreters",
    )
    require(not any(
        module == root or module.startswith(root + ".")
        for module in sys.modules for root in forbidden
    ), "reject candidate imports, matching engines, native loads, and network")


class FirstPartySourceWall:
    """Permit only complete pinned first-party sources and public evidence."""

    def __init__(self) -> None:
        relatives = (SOURCE, PROTOCOL, CONTRACT) + tuple(
            row[1] for row in STATIC_OWNERS
        )
        require(len(relatives) == len(frozenset(relatives)),
                "reject duplicate or aliased first-party source owners")
        self.allowed = frozenset(ROOT + "/" + name for name in relatives)
        self.blocked: dict[str, int] = {}
        self.live: set[int] = set()
        self.installed = False
        self.error_type: type[Exception] = BuildFreezeError
        self.native_open = os.open
        self.native_read = os.read
        self.native_fstat = os.fstat
        self.native_close = os.close

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise self.error_type(
            "V23 first-party physical source wall rejected " + category,
        )

    def approved(self, path: object) -> bool:
        return (
            type(path) is str
            and path.startswith(ROOT + "/")
            and path == os.path.normpath(path)
            and not any(part in (".", "..") for part in path.split("/"))
            and path in self.allowed
            and not path.endswith((".so", ".gz"))
            and not path.startswith(ROOT + "/oracle/phase3/")
            and "holdout" not in path.lower()
            and "benchmark" not in path.lower()
        )

    def audit(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            mode = arguments[1] if len(arguments) > 1 else None
            flags = arguments[2] if len(arguments) > 2 else None
            destructive = (
                os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                | os.O_APPEND | getattr(os, "O_TMPFILE", 0)
            )
            if (
                not self.approved(path)
                or type(flags) is not int
                or flags & destructive
                or not flags & getattr(os, "O_NOFOLLOW", 0)
                or type(mode) is str and any(char in mode for char in "wax+")
            ):
                self.deny("unowned-direct-file-open")
            return
        if event in ("exec", "compile"):
            value = arguments[0] if arguments else None
            filename = (
                getattr(value, "co_filename", None)
                if event == "exec"
                else arguments[1] if len(arguments) > 1 else None
            )
            if not self.approved(filename):
                self.deny("unowned-dynamic-execution")
            return
        if (
            event in (
                "import", "marshal.loads", "os.system", "os.fork",
                "os.posix_spawn", "os.posix_spawnp", "os.rename",
                "os.replace", "os.remove", "os.unlink", "os.mkdir",
                "os.rmdir", "os.chmod", "os.chown", "os.urandom",
                "os.getrandom", "_interpreters.create", "_interpreters.exec",
                "cpython.PyInterpreterState_New",
            )
            or event.startswith((
                "subprocess.", "socket.", "ctypes.", "threading.",
                "multiprocessing.", "tempfile.", "time.", "os.exec",
                "os.spawn", "random.",
            ))
        ):
            self.deny("import-compiler-native-network-clock-or-mutation")

    def _forbidden(self, category: str):
        def denied(*_args: object, **_kwargs: object) -> object:
            self.deny(category)
        return denied

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
                "open only one real pinned first-party source descriptor")
        require(descriptor not in self.live,
                "reject an already live first-party source descriptor")
        self.live.add(descriptor)
        return descriptor

    def guarded_read(self, descriptor: object, count: object) -> bytes:
        if (
            type(descriptor) is not int or descriptor not in self.live
            or type(count) is not int or not 0 <= count <= MAX_OWNER_BYTES
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
        require(not self.installed,
                "install exactly one fresh first-party source wall")
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
            "fdopen", "dup", "dup2", "stat", "lstat", "readlink", "listdir",
            "scandir", "walk", "fwalk", "access", "fork", "posix_spawn",
            "posix_spawnp", "system", "mkdir", "makedirs", "remove",
            "unlink", "rename", "replace", "rmdir", "chmod", "chown",
            "urandom", "getrandom",
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


def secure_owner(wall: FirstPartySourceWall, row: tuple) -> bytes:
    require(type(row) is tuple and len(row) == 5,
            "require one entire independently pinned first-party owner")
    role, relative, expected, count, inode = row
    require(
        type(role) is str and type(relative) is str
        and not relative.startswith("/")
        and ".." not in relative.split("/")
        and type(count) is int and 0 < count <= MAX_OWNER_BYTES
        and type(inode) is int and inode > 0,
        "reject an unbounded or noncanonical first-party source owner",
    )
    hash_pin(expected, relative)
    absolute = ROOT + "/" + relative
    require(wall.installed and wall.approved(absolute),
            "install the source wall before the first predecessor byte")
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
            "reject a substituted complete first-party source: " + role,
        )
        remaining = count
        blocks: list[bytes] = []
        while remaining:
            block = os.read(descriptor, min(remaining, 65536))
            require(type(block) is bytes and bool(block),
                    "reject truncated complete first-party bytes: " + role)
            blocks.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"",
                "reject expanded complete first-party bytes: " + role)
        after = os.fstat(descriptor)
        require(all(
            getattr(before, field) == getattr(after, field)
            for field in (
                "st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns",
                "st_nlink",
            )
        ), "reject concurrent mutation of the first-party owner: " + role)
        raw = b"".join(blocks)
        require(digest(raw) == expected,
                "reject changed complete first-party source bytes: " + role)
        return raw
    finally:
        os.close(descriptor)


def dynamic_owner(
    wall: FirstPartySourceWall, role: str, relative: str, pin: str,
) -> tuple:
    require(relative in (SOURCE, PROTOCOL, CONTRACT),
            "reject unrelated dynamic V23 build-source ownership")
    hash_pin(pin, relative)
    absolute = ROOT + "/" + relative
    require(wall.installed and wall.approved(absolute),
            "authenticate a source owner only after the new physical wall")
    flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(absolute, flags)
    try:
        value = os.fstat(descriptor)
        require(
            stat.S_ISREG(value.st_mode)
            and stat.S_IMODE(value.st_mode) == 0o600
            and value.st_dev == DEVICE
            and value.st_uid == os.geteuid()
            and value.st_nlink == 1
            and 0 < value.st_size <= MAX_OWNER_BYTES,
            "reject an exchanged exact V23 source-build owner",
        )
        return role, relative, pin, value.st_size, value.st_ino
    finally:
        os.close(descriptor)


def owner_document(row: tuple, *, uid: bool = True) -> dict:
    result = {
        "role": row[0], "path": row[1], "sha256": row[2], "bytes": row[3],
        "device": DEVICE, "inode": row[4], "mode": "0600", "nlink": 1,
    }
    if uid:
        result["uid"] = os.geteuid()
    return result


def simple_owner(row: tuple) -> dict:
    return {"path": row[1], "sha256": row[2], "bytes": row[3]}


def decode_public(
    capture: types.ModuleType, semantic: types.ModuleType,
    raw: bytes, label: str,
) -> dict:
    value = semantic.StrictJSON(raw).decode()
    require(type(value) is dict,
            "decode one complete strict public JSON object: " + label)
    require(raw == capture.canonical_document(semantic, value),
            "reject a noncanonical or truncated public document: " + label)
    return value


def bootstrap_parent(wall: FirstPartySourceWall) -> types.ModuleType:
    row = CAMPAIGN_V23_OWNERS[0]
    raw = secure_owner(wall, row)
    module = types.ModuleType("_rebar_build_v23_exact_frozen_campaign_v23")
    module.__file__ = ROOT + "/" + row[1]
    exec(compile(raw, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    require(
        module.SOURCE == CAMPAIGN_V23_OWNERS[0][1]
        and module.PROTOCOL == CAMPAIGN_V23_OWNERS[1][1]
        and module.CONTRACT == CAMPAIGN_V23_OWNERS[2][1]
        and module.SCHEMA == "rebar-owned-repaired-rust-original-campaign-v23"
        and module.VERSION == 23
        and module.CAPTURE_V2_OWNERS == CAPTURE_V2_OWNERS
        and module.PUBLIC_OWNERS == PUBLIC_OWNERS
        and module.GUARD_OWNERS == GUARD_OWNERS
        and module.STATIC_OWNERS == PARENT_STATIC_OWNERS
        and callable(module.load_context)
        and callable(module.validate_exact_campaign)
        and callable(module.validate_exact_actual)
        and callable(module.validate_guard_v3),
        "reject a substituted factually corrected complete V23 source freeze",
    )
    no_matching_imports()
    return module


def verify_native_documents(v9: object, v16: object, adapter: object) -> None:
    require(
        type(v9) is dict
        and v9.get("schema")
        == "rebar-phase2-owned-native-source-build-v9-source-freeze"
        and v9.get("version") == 9
        and v9.get("family") == FAMILY,
        "authenticate the immutable first-party V9 offline compiler kernel",
    )
    package = v9.get("rust_package")
    policy = v9.get("future_build_policy")
    baseline = v9.get("source_baseline")
    require(
        type(package) is dict
        and package.get("name") == "rebar-rust-continuation"
        and package.get("version") == "0.1.0"
        and package.get("edition") == "2024"
        and package.get("rust_version") == "1.85"
        and package.get("crate_type") == ["cdylib"]
        and package.get("package_count") == 1
        and package.get("external_dependency_count") == 0
        and package.get("lock_format_version") == 4
        and package.get("publish") is False
        and package.get("release_opt_level") == 3
        and package.get("release_lto") is True
        and package.get("release_codegen_units") == 1
        and package.get("release_panic") == "abort"
        and package.get("network") == "FORBIDDEN",
        "reject an external Rust package, regex crate, or modified Cargo lock",
    )
    require(
        type(baseline) is dict
        and baseline.get("candidate_source_mutation") == "FORBIDDEN"
        and baseline.get("rust_source_owner_count") == 9
        and baseline.get("rust_sources")
        == [simple_owner(row) for row in CANONICAL_RUST_OWNERS],
        "preserve all nine original canonical Rust source owners exactly",
    )
    require(
        type(policy) is dict
        and policy.get("rustc") == RUSTC
        and policy.get("cargo") == CARGO
        and policy.get("compiler") == GCC
        and policy.get("elf_inspector") == READELF
        and policy.get("phase_names") == list(PHASES)
        and policy.get("process_names_per_phase") == list(PROCESS_NAMES)
        and policy.get("processes_per_phase") == 14
        and policy.get("total_future_processes") == 28
        and policy.get("cargo_net_offline") is True
        and policy.get("cargo_flags") == [
            "build", "--manifest-path", "--release", "--locked",
            "--offline", "--frozen", "--target-dir",
        ]
        and policy.get("gcc_flags") == list(GCC_FLAGS)
        and policy.get("external_cargo_dependencies") == "FORBIDDEN"
        and policy.get("external_engine") == "FORBIDDEN"
        and policy.get("fallback") == "FORBIDDEN"
        and policy.get("network") == "FORBIDDEN"
        and policy.get("engine_name") == "_rust_engine.so"
        and policy.get("bridge_name")
        == "_rust_bridge.cpython-314-x86_64-linux-gnu.so"
        and policy.get("bridge_runpath") == "$ORIGIN"
        and policy.get("python_include") == PYTHON_INCLUDE
        and policy.get("candidate_imports") == 0
        and policy.get("candidate_processes_started") == 0,
        "reject unpinned Rust 1.95 or a weakened reproducible offline build",
    )

    require(
        type(v16) is dict
        and v16.get("schema")
        == "rebar-phase2-owned-rust-buffer-shape-source-build-v16-source-freeze"
        and v16.get("version") == 16
        and v16.get("family") == FAMILY
        and v16.get("source", {}).get("sha256")
        == NATIVE_SOURCE_OWNERS[3][2]
        and v16.get("protocol", {}).get("sha256")
        == NATIVE_SOURCE_OWNERS[4][2],
        "authenticate the complete immutable first-party V16 build policy",
    )
    native = v16.get("future_offline_native_build")
    family = v16.get("first_party_source_family")
    history = v16.get("historical_first_party_source_derivation")
    require(
        type(native) is dict
        and native.get("toolchain") == list(TOOLCHAIN_OWNERS)
        and native.get("phase_count") == 2
        and native.get("processes_per_phase") == 14
        and native.get("total_successful_process_count") == 28
        and native.get("unique_successful_process_ids_required") is True
        and native.get("ordered_process_names_per_phase") == list(PROCESS_NAMES)
        and native.get("cargo_net_offline") is True
        and native.get("offline_cargo_flags") == [
            "--release", "--locked", "--offline", "--frozen", "--target-dir",
        ]
        and native.get("complete_raw_elf_comparison_required") is True
        and native.get("candidate_execution") == "FORBIDDEN"
        and native.get("native_library_loading") == "FORBIDDEN"
        and native.get("network_requests_allowed") == 0,
        "reject a substitute toolchain, candidate execution, or fabricated ELF",
    )
    require(
        type(family) is dict
        and family.get("canonical_rust_source_owner_count") == 9
        and family.get("canonical_rust_source_owners")
        == [simple_owner(row) for row in CANONICAL_RUST_OWNERS]
        and family.get("external_cargo_dependency_count") == 0
        and family.get("rust_cargo_package_count") == 1
        and family.get("stdlib_regular_expression_engine") == "FORBIDDEN"
        and family.get("cpython_sre_engine") == "FORBIDDEN"
        and family.get("external_regular_expression_engine") == "FORBIDDEN"
        and family.get("another_candidate_engine") == "FORBIDDEN"
        and family.get("production_matching_fallback") == "FORBIDDEN"
        and family.get("original_sources_modified") is False,
        "reject stdlib, external, cross-candidate, or fallback delegation",
    )
    require(
        type(history) is dict
        and history.get("corrected_public_adapter_sha256") == ADAPTER_SHA
        and history.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
        and history.get("canonical_original_modified") is False
        and history.get("adapter_repair_owners")
        == [simple_owner(row) for row in ADAPTER_REPAIR_OWNERS],
        "retain the independently reproducible first-party private adapter",
    )

    require(
        type(adapter) is dict
        and adapter.get("schema")
        == "rebar-phase2-owned-rust-public-contract-source-repair-v3-"
        "source-freeze"
        and adapter.get("version") == 3
        and adapter.get("source", {}).get("sha256")
        == ADAPTER_REPAIR_OWNERS[0][2]
        and adapter.get("protocol", {}).get("sha256")
        == ADAPTER_REPAIR_OWNERS[1][2],
        "authenticate the complete immutable first-party adapter repair",
    )
    repair = adapter.get("repair")
    source = adapter.get("rust_source")
    boundary = adapter.get("phase_boundary")
    require(
        type(repair) is dict
        and repair.get("original") == {
            "path": CANONICAL_RUST_OWNERS[8][1],
            "sha256": CANONICAL_RUST_OWNERS[8][2],
            "bytes": CANONICAL_RUST_OWNERS[8][3], "modified": False,
        }
        and repair.get("derived", {}).get("sha256") == ADAPTER_SHA
        and repair.get("derived", {}).get("bytes") == ADAPTER_BYTES
        and repair.get("derived", {}).get("materialized") is False
        and repair.get("cross_family_delegation_added") is False
        and repair.get("external_regex_engine_added") is False
        and repair.get("stdlib_regex_delegation_added") is False
        and type(source) is dict
        and source.get("cargo_lock_package_count") == 1
        and source.get("cross_family_dependency_count") == 0
        and source.get("external_regex_dependency_count") == 0
        and source.get("owners")
        == [simple_owner(row) for row in CANONICAL_RUST_OWNERS]
        and type(boundary) is dict
        and boundary.get("candidate_imports") == 0
        and boundary.get("candidate_workers_started") == 0
        and boundary.get("compiler_processes_started") == 0
        and boundary.get("holdout") == "NOT OPENED",
        "never import the adapter repair, its stdlib oracle, or a candidate",
    )


def verify_variant(
    semantic: types.ModuleType, baseline: bytes, materialized: bytes,
    matcher: bytes,
) -> dict:
    require(digest(baseline) == A0_SHA and len(baseline) == 179520,
            "authenticate the complete actual captured-findall a0 source")
    require(digest(materialized) == VARIANT_SHA
            and len(materialized) == VARIANT_BYTES,
            "authenticate the actually materialized complete 1adb V2 bridge")
    require(digest(matcher) == MATCHER_SHA and len(matcher) == 177967,
            "preserve the actual complete original first-party Rust matcher")

    outer = semantic.OUTER_LENGTH_REWRITE
    original = semantic.FAILED_REPLACEMENT_ORIGINAL
    failed = semantic.FAILED_REPLACEMENT_CORRECTED
    capture = semantic.CAPTURE_INSERTION
    require(
        type(outer) is bytes and len(outer) == 660
        and type(original) is bytes and len(original) == 97
        and type(failed) is bytes and len(failed) == 384
        and type(capture) is bytes
        and len(capture.splitlines()) == 17,
        "authenticate only complete frozen original first-party anchors",
    )
    helper_start = b"static int rust_restore_original_template_error("
    helper_follow = b"\nstatic int rust_replacement_cache("
    before, helper, after = semantic.split_function(
        baseline, helper_start, helper_follow,
        "one real captured-base error-position helper",
    )
    require(helper.count(outer) == 1 and baseline.count(outer) == 1,
            "remove exactly one frozen 660-byte original outer-length block")
    corrected_helper = helper.replace(outer, b"", 1)
    require(b"PyObject_Length(replacement)" not in corrected_helper,
            "reject reintroduced error-position exporter probing")
    derived = before + corrected_helper + after
    require(derived == materialized and digest(derived) == VARIANT_SHA,
            "prove the complete on-disk V2 variant from exact a0 source")

    cache_start = b"static int rust_replacement_cache("
    cache_follow = b"\nstatic PyObject *rust_normalize_expand_buffer("
    _left, original_cache, _right = semantic.split_function(
        baseline, cache_start, cache_follow,
        "the genuine 97-byte original replacement branch",
    )
    _left2, repaired_cache, _right2 = semantic.split_function(
        materialized, cache_start, cache_follow,
        "the byte-identical 97-byte repaired replacement branch",
    )
    require(
        original_cache == repaired_cache
        and original_cache.count(original) == 1
        and original_cache.count(failed) == 0
        and repaired_cache.count(failed) == 0,
        "reject the known-failing f9 early guard or any replacement-cache edit",
    )
    capture_start = b"static int rust_append_batched_findall("
    capture_follow = b"\nstatic PyObject *rust_batched_findall("
    _cl, original_capture, _cr = semantic.split_function(
        baseline, capture_start, capture_follow,
        "original captured first-party findall fast path",
    )
    _vl, final_capture, _vr = semantic.split_function(
        materialized, capture_start, capture_follow,
        "materialized captured first-party findall fast path",
    )
    require(
        original_capture == final_capture
        and original_capture.count(capture) == 1
        and final_capture.count(capture) == 1,
        "preserve all 17 genuine first-party two-capture fast-path lines",
    )
    forbidden_c = (
        b'PyImport_ImportModule("re")',
        b'PyImport_ImportModule("_sre")',
        b'PyImport_ImportModule("regex")',
        b"#include <regex.h>", b"#include <pcre", b"dlopen(",
        b"PyRun_",
    )
    forbidden_rust = (
        b"extern crate regex", b"extern crate regex_automata",
        b"extern crate pcre", b"extern crate onig",
        b"use regex::", b"use regex_automata::", b"use pcre2::",
        b"use onig::", b"use fancy_regex::",
    )
    require(not any(marker in materialized for marker in forbidden_c)
            and not any(marker in matcher for marker in forbidden_rust),
            "reject delegated stdlib, external-crate, or native matching")
    return {
        "base_sha256": A0_SHA,
        "base_bytes": 179520,
        "materialized_variant_sha256": VARIANT_SHA,
        "materialized_variant_bytes": VARIANT_BYTES,
        "outer_length_block_removed_count": 1,
        "outer_length_block_removed_bytes": 660,
        "original_replacement_anchor_bytes": 97,
        "known_failing_f9_replacement_anchor_bytes": 384,
        "known_failing_f9_guard_added": False,
        "replacement_cache_byte_identical": True,
        "captured_findall_fast_path_lines": 17,
        "captured_findall_byte_identical": True,
        "matching_engine_sha256": MATCHER_SHA,
        "matching_engine_bytes": 177967,
        "matching_engine_changed": False,
        "complete_variant_source_materialized": True,
        "complete_variant_source_authenticated": True,
        "canonical_original_bridge_modified": False,
        "canonical_original_adapter_modified": False,
        "native_engine_built": False,
        "native_bridge_built": False,
        "candidate_imported": False,
        "candidate_correctness": NOT_MEASURED,
    }


def native_build_plan() -> dict:
    require(len(BUILD_LABEL) == 48 and len(PHASES) == 2
            and len(PROCESS_NAMES) == 14,
            "reject an unsafe build label or incomplete dual-phase plan")
    return {
        "status": "NOT RUN",
        "label": BUILD_LABEL,
        "root_parent": "/tmp",
        "private_root": "NOT CREATED; NOT OPENED",
        "root_prefix": "rebar-phase2-native-build-v9-rust-",
        "phase_names": list(PHASES),
        "phase_count": 2,
        "process_names_per_phase": list(PROCESS_NAMES),
        "processes_per_phase": 14,
        "required_actual_distinct_compiler_process_count": 28,
        "actual_compiler_process_count": 0,
        "actual_process_ids": [],
        "toolchain": list(TOOLCHAIN_OWNERS),
        "cargo": CARGO,
        "rustc": RUSTC,
        "compiler": GCC,
        "elf_inspector": READELF,
        "cpython": PYTHON,
        "cpython_sha256": PYTHON_SHA256,
        "cpython_include": PYTHON_INCLUDE,
        "cargo_flags": [
            "build", "--manifest-path", "--release", "--locked",
            "--offline", "--frozen", "--target-dir",
        ],
        "gcc_flags": list(GCC_FLAGS),
        "phase_prefix_map_target": "/rebar-phase2-v6-owned-source",
        "rust_soname": "_rust_engine.so",
        "bridge_runpath": "$ORIGIN",
        "phase_environment": {
            "PATH": RUST_TOOLCHAIN + "/bin:/usr/bin:/bin",
            "LC_ALL": "C", "LANG": "C", "TZ": "UTC",
            "SOURCE_DATE_EPOCH": "1",
            "TMPDIR": "<FRESH_PRIVATE_PHASE>/temporary",
            "CARGO_HOME": "<FRESH_PRIVATE_PHASE>/cargo-home",
            "CARGO_NET_OFFLINE": "true",
            "CARGO_INCREMENTAL": "0",
            "CARGO_BUILD_JOBS": "1",
            "RUSTC": RUSTC,
            "RUSTFLAGS": (
                "--remap-path-prefix=<REFERENCE_A_SOURCE>="
                "/rebar-phase2-v6-owned-source "
                "--remap-path-prefix=<REFERENCE_B_SOURCE>="
                "/rebar-phase2-v6-owned-source "
                "-Clink-arg=-Wl,-soname,_rust_engine.so"
            ),
        },
        "canonical_source_owner_count": 9,
        "original_source_owners_per_phase": 7,
        "private_variant_overlay_count_per_phase": 1,
        "private_corrected_adapter_overlay_count_per_phase": 1,
        "private_variant_sha256": VARIANT_SHA,
        "private_variant_bytes": VARIANT_BYTES,
        "private_corrected_adapter_sha256": ADAPTER_SHA,
        "private_corrected_adapter_bytes": ADAPTER_BYTES,
        "cross_phase_complete_engine_elf_equality_required": True,
        "cross_phase_complete_bridge_elf_equality_required": True,
        "engine_sha256": NOT_MEASURED,
        "bridge_sha256": NOT_MEASURED,
        "engine_bytes": NOT_MEASURED,
        "bridge_bytes": NOT_MEASURED,
        "public_build_receipt_sha256": NOT_MEASURED,
        "public_root_receipt_sha256": NOT_MEASURED,
        "archives_opened": 0,
        "private_roots_opened": 0,
        "native_libraries_loaded": 0,
        "compiler_processes_started": 0,
        "network_requests": 0,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "stdlib_re_engine": "FORBIDDEN",
        "stdlib_sre_engine": "FORBIDDEN",
        "external_regex_engine": "FORBIDDEN",
        "external_cargo_dependency_count": 0,
        "cross_candidate_engine": "FORBIDDEN",
        "matching_fallback": "FORBIDDEN",
        "run_authorization": "BLOCKED; SEPARATE PUSHED ROOT-AUTHORIZED BUILD",
        "candidate_correctness": NOT_MEASURED,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
    }


def validate_native_build_plan(value: object) -> None:
    require(type(value) is dict and value == native_build_plan(),
            "reject omitted or weakened first-party dual-build requirements")


def block_actual(choice: object) -> None:
    require(type(choice) is dict and choice.get("mode") in ACTUAL_MODES,
            "reject unrelated V23 native-build activation")
    raise BuildFreezeError(BLOCKED_ACTUAL)


def load_context(
    wall: FirstPartySourceWall, pins: dict, rendering: bool,
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

    parent = bootstrap_parent(wall)
    parent_pins = {
        "--source-sha256": CAMPAIGN_V23_OWNERS[0][2],
        "--protocol-sha256": CAMPAIGN_V23_OWNERS[1][2],
        "--contract-sha256": CAMPAIGN_V23_OWNERS[2][2],
    }
    parent_frozen, parent_state = parent.load_context(wall, parent_pins, False)
    capture = parent_state["capture"]
    semantic = parent_state["semantic"]
    wall.error_type = type(
        "V23FirstPartySourceWallError",
        (BuildFreezeError, parent.FreezeError, capture.FreezeError),
        {},
    )
    require(
        parent_frozen.get("schema") == parent.SCHEMA
        and parent_frozen.get("version") == 23
        and parent_frozen.get("immutable_previous_v22_campaign", {}).get(
            "complete_current_contract_field_count",
        ) == 435
        and parent_frozen.get("immutable_previous_v22_campaign", {}).get(
            "complete_inherited_v21_contract_field_count",
        ) == 402
        and parent_frozen.get("immutable_actual_v22_failure", {}).get(
            "complete_receipt_field_count",
        ) == 96
        and parent_frozen.get("immutable_actual_v22_failure", {}).get(
            "candidate_status",
        ) == "FAIL"
        and parent_frozen.get("immutable_actual_v22_failure", {}).get(
            "actual_failing_worker_transient_native_child_creation",
        ) == NOT_MEASURED,
        "preserve the full factually correct V23 frozen failure boundary",
    )

    additional: dict[str, bytes] = {}
    for row in (
        NATIVE_SOURCE_OWNERS + ADAPTER_REPAIR_OWNERS
        + CANONICAL_RUST_OWNERS + (A0_OWNER, VARIANT_OWNER)
    ):
        additional[row[0]] = secure_owner(wall, row)
    native_v9 = decode_public(
        capture, semantic, additional["native_v9_contract"],
        "complete first-party V9 reproducibility kernel",
    )
    native_v16 = decode_public(
        capture, semantic, additional["native_v16_contract"],
        "complete first-party V16 toolchain and adapter policy",
    )
    adapter = decode_public(
        capture, semantic, additional["adapter_v3_contract"],
        "complete first-party public adapter repair",
    )
    verify_native_documents(native_v9, native_v16, adapter)
    proof = verify_variant(
        semantic,
        additional[A0_OWNER[0]],
        additional[VARIANT_OWNER[0]],
        additional["canonical_matching_engine"],
    )
    plan = native_build_plan()
    validate_native_build_plan(plan)
    capture.validate_originals(parent_state["actual"]["restored_original_targets"])
    require(not wall.live,
            "close all tracked canonical and first-party source descriptors")
    no_matching_imports()

    frozen = build_contract(
        source_row, protocol_row, parent_frozen, parent_state,
        native_v9, native_v16, adapter, proof, plan,
    )
    state = {
        "parent": parent, "parent_frozen": parent_frozen,
        "parent_state": parent_state, "capture": capture,
        "semantic": semantic, "additional": additional,
        "native_v9": native_v9, "native_v16": native_v16,
        "adapter": adapter, "variant_proof": proof, "native_plan": plan,
        "source_row": source_row, "protocol_row": protocol_row,
        "contract": frozen,
    }
    if not rendering:
        assert isinstance(contract_row, tuple)
        raw = secure_owner(wall, contract_row)
        require(raw == capture.canonical_document(semantic, frozen)
                and semantic.StrictJSON(raw).decode() == frozen,
                "reject any removed or changed complete V23 build obligation")
        state["contract_row"] = contract_row
    require(not wall.live, "close every tracked first-party source descriptor")
    no_matching_imports()
    return frozen, state


def build_contract(
    source_row: tuple, protocol_row: tuple, parent: dict,
    parent_state: dict, native_v9: dict, native_v16: dict,
    adapter: dict, proof: dict, plan: dict,
) -> dict:
    actual = parent_state["actual"]
    previous = parent["immutable_actual_v22_failure"]
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "status": (
            "COMPLETE FIRST-PARTY V2 SOURCE MATERIALIZED; "
            "NATIVE BUILD NOT RUN; CORRECTNESS NOT MEASURED"
        ),
        "phase": "PHASE 2: FIRST-PARTY RUST CANDIDATE CORRECTNESS",
        "family": FAMILY,
        "goal_sha256": GOAL_SHA,
        "source": owner_document(source_row),
        "protocol": owner_document(protocol_row),
        "materialized_first_party_variant": {
            "owner": owner_document(VARIANT_OWNER),
            "source_materialized": True,
            "complete_source_sha256": VARIANT_SHA,
            "complete_source_bytes": VARIANT_BYTES,
            "base_owner": owner_document(A0_OWNER),
            "derivation": proof,
            "native_build": "NOT RUN",
            "native_engine_sha256": NOT_MEASURED,
            "native_bridge_sha256": NOT_MEASURED,
            "candidate_imports": 0,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": NOT_MEASURED,
            "candidate_qualified": False,
        },
        "authenticated_first_party_source_owners": [
            owner_document(row) for row in CANONICAL_RUST_OWNERS
        ],
        "canonical_original_source_identity": {
            "owner_count": 9,
            "bridge_source": owner_document(CANONICAL_RUST_OWNERS[2]),
            "public_adapter": owner_document(CANONICAL_RUST_OWNERS[8]),
            "matching_engine": owner_document(CANONICAL_RUST_OWNERS[3]),
            "canonical_sources_modified": False,
            "installed_native_owners_opened": False,
            "installed_engine_sha256": (
                "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4"
            ),
            "installed_bridge_sha256": (
                "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15"
            ),
            "native_identity_scope": (
                "EXACT IMMUTABLE PUBLISHED V22 RECEIPT; "
                "NO NATIVE FILE OPEN OR METADATA PROBE"
            ),
        },
        "immutable_complete_v23_correctness_campaign": {
            "owners": [owner_document(row) for row in CAMPAIGN_V23_OWNERS],
            "complete_frozen_source_contract": parent,
            "corrected_candidate_run": "NOT RUN",
            "original_case_count": 31237,
            "original_suite_count": 13,
            "named_private_waiver_count": 13,
            "supplemental_differential_case_count": 8244,
            "supplemental_counted_in_original_denominator": False,
            "corrected_reference_case_count": 6912,
            "corrected_reference_counted_in_original_denominator": False,
        },
        "immutable_genuine_v22_failure": {
            "complete_receipt": actual,
            "complete_receipt_field_count": 96,
            "receipt_sha256": PUBLIC_OWNERS[17][2],
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": "FAIL",
            "original_case_denominator": 31237,
            "actual_worker_count": 13,
            "completed_suite_count": 12,
            "verified_passing_case_count": 14725,
            "fully_observed_mismatch_lower_bound": 2018,
            "fully_observed_suite_mismatch_counts": {
                "managed_v1": 42,
                "substitution_v2": 352,
                "shape_v2": 1624,
            },
            "global_semantic_mismatch_count": NOT_MEASURED,
            "failing_worker_pid": 188,
            "failing_worker_candidate_imports": 1,
            "failing_worker_native_library_loads": 2,
            "recorded_successfully_returned_child_interpreters": 0,
            "recorded_installed_child_guards": 0,
            "recorded_case_interpreter_exec_calls": 0,
            "transient_physical_native_child_creation": NOT_MEASURED,
            "remaining_interpreter_warning_count": 1,
            "destructor_warning_count": 16,
            "warning_scope": "ONLY ACTUAL SUBINTERPRETER WORKER PID 188",
            "old_f9_bridge_sha256": F9_SHA,
            "old_f9_bridge_bytes": 179147,
            "old_failed_f9_is_new_variant": False,
            "measured_values_taken_from_complete_receipt": True,
            "failing_worker_counter_scope": previous[
                "actual_failing_worker_counter_scope"
            ],
        },
        "immutable_complete_native_v9_kernel": {
            "owners": [owner_document(row) for row in NATIVE_SOURCE_OWNERS[:3]],
            "complete_frozen_source_contract": native_v9,
            "kernel_executed": False,
        },
        "immutable_complete_native_v16_toolchain": {
            "owners": [owner_document(row) for row in NATIVE_SOURCE_OWNERS[3:]],
            "complete_frozen_source_contract": native_v16,
            "controller_executed": False,
            "toolchain_binaries_opened": False,
        },
        "immutable_first_party_private_adapter_repair": {
            "owners": [owner_document(row) for row in ADAPTER_REPAIR_OWNERS],
            "complete_frozen_source_contract": adapter,
            "corrected_private_adapter_sha256": ADAPTER_SHA,
            "corrected_private_adapter_bytes": ADAPTER_BYTES,
            "canonical_original_adapter_modified": False,
            "adapter_repair_controller_executed": False,
            "adapter_oracle_stdlib_re_imported": False,
        },
        "frozen_offline_dual_phase_build": plan,
        "source_wall": {
            "policy": (
                "DENY DEFAULT; EXACT PUBLIC EVIDENCE AND PINNED "
                "FIRST-PARTY SOURCE OWNERS ONLY"
            ),
            "installed_before_first_predecessor_byte": True,
            "static_source_owner_count": len(STATIC_OWNERS),
            "new_controller_owner_count": 3,
            "actual_canonical_rust_source_owner_count": 9,
            "materialized_new_variant_owner_count": 1,
            "authentic_a0_base_owner_count": 1,
            "any_other_candidate_paths_allowed": 0,
            "native_library_paths_allowed": 0,
            "private_root_paths_allowed": 0,
            "archive_paths_allowed": 0,
            "phase_three_proposal_paths_allowed": 0,
            "foreign_descriptor_reads_allowed": 0,
            "direct_io_allowed": False,
            "direct_metadata_allowed": False,
            "timing_allowed": False,
            "entropy_allowed": False,
        },
        "source_only_effects": {
            "candidate_imports": 0,
            "candidate_workers_started": 0,
            "reference_workers_started": 0,
            "compiler_processes_started": 0,
            "native_libraries_loaded": 0,
            "native_binary_files_read": 0,
            "native_binary_metadata_probes": 0,
            "private_roots_created": 0,
            "private_roots_opened": 0,
            "compressed_archives_opened": 0,
            "compressed_archives_inflated": 0,
            "hidden_cases_read": 0,
            "holdout_cases_opened": 0,
            "phase_three_files_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "network_requests": 0,
            "subinterpreters_created": 0,
            "threads_started": 0,
            "canonical_source_mutations": 0,
            "adapter_repair_controllers_executed": 0,
            "native_build_controllers_executed": 0,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": NOT_MEASURED,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "expanded_holdout_proposal_case_count": 14155776,
            "expanded_holdout_cases": "NOT FROZEN; NOT GENERATED; NOT OPENED",
            "holdout": "NOT OPENED",
            "native_engine_sha256": NOT_MEASURED,
            "native_bridge_sha256": NOT_MEASURED,
            "native_build_receipt_sha256": NOT_MEASURED,
            "native_root_receipt_sha256": NOT_MEASURED,
            "performance": NOT_MEASURED,
            "memory": NOT_MEASURED,
            "confidence_intervals": NOT_MEASURED,
            "undefined_behavior": NOT_MEASURED,
            "qualified_candidate_count": 0,
            "winner_selected": False,
        },
    }


def reject(action: object, label: str, *types_: type) -> str:
    require(callable(action), "require one executed bounded hostile control")
    try:
        action()
    except (
        BuildFreezeError, OSError, ValueError, TypeError, KeyError,
        IndexError, UnicodeError, OverflowError, *types_,
    ):
        return label
    raise BuildFreezeError("accepted hostile first-party source control: " + label)


def validate_exact_document(
    capture: types.ModuleType, semantic: types.ModuleType,
    proposed: object, authentic: dict, label: str,
) -> None:
    require(type(proposed) is dict and set(proposed) == set(authentic),
            "reject missing or added complete immutable evidence: " + label)
    assert isinstance(proposed, dict)
    require(
        capture.canonical_document(semantic, proposed)
        == capture.canonical_document(semantic, authentic),
        "reject a changed complete immutable evidence value: " + label,
    )


def self_test(wall: FirstPartySourceWall, frozen: dict, state: dict) -> list[str]:
    parent = state["parent"]
    capture = state["capture"]
    semantic = state["semantic"]
    actual = state["parent_state"]["actual"]
    campaign = state["parent_state"]["campaign"]
    additional = state["additional"]
    baseline = additional[A0_OWNER[0]]
    materialized = additional[VARIANT_OWNER[0]]
    matcher = additional["canonical_matching_engine"]
    kinds = (parent.FreezeError, capture.FreezeError, semantic.FreezeError)
    checks: list[str] = []

    for key in sorted(campaign):
        missing = dict(campaign)
        missing.pop(key)
        checks.append(reject(
            lambda item=missing: parent.validate_exact_campaign(
                capture, semantic, item, campaign,
            ), "reject-missing-complete-v22-obligation-" + key, *kinds,
        ))
        altered = dict(campaign)
        altered[key] = {"__v23_source_build_forged_obligation__": key}
        checks.append(reject(
            lambda item=altered: parent.validate_exact_campaign(
                capture, semantic, item, campaign,
            ), "reject-changed-complete-v22-obligation-" + key, *kinds,
        ))

    for key in sorted(actual):
        missing = dict(actual)
        missing.pop(key)
        checks.append(reject(
            lambda item=missing: parent.validate_exact_actual(
                capture, semantic, item, actual,
            ), "reject-missing-complete-v22-failure-receipt-" + key, *kinds,
        ))
        altered = dict(actual)
        altered[key] = {"__v23_source_build_forged_actual_receipt__": key}
        checks.append(reject(
            lambda item=altered: parent.validate_exact_actual(
                capture, semantic, item, actual,
            ), "reject-changed-complete-v22-failure-receipt-" + key, *kinds,
        ))

    for section, authentic in (
        ("complete-v23-campaign", state["parent_frozen"]),
        ("complete-v9-compiler-kernel", state["native_v9"]),
        ("complete-v16-native-build", state["native_v16"]),
        ("complete-v3-adapter-repair", state["adapter"]),
    ):
        for key in sorted(authentic):
            missing = dict(authentic)
            missing.pop(key)
            checks.append(reject(
                lambda item=missing, exact=authentic, title=section:
                    validate_exact_document(
                        capture, semantic, item, exact, title,
                    ),
                "reject-missing-" + section + "-" + key, *kinds,
            ))

    outer = semantic.OUTER_LENGTH_REWRITE
    original = semantic.FAILED_REPLACEMENT_ORIGINAL
    failed = semantic.FAILED_REPLACEMENT_CORRECTED
    capture_anchor = semantic.CAPTURE_INSERTION
    _bl, cache, _br = semantic.split_function(
        materialized,
        b"static int rust_replacement_cache(",
        b"\nstatic PyObject *rust_normalize_expand_buffer(",
        "authentic materialized V2 replacement cache",
    )
    forged_f9_cache = cache.replace(original, failed, 1)
    left, _cache, right = semantic.split_function(
        materialized,
        b"static int rust_replacement_cache(",
        b"\nstatic PyObject *rust_normalize_expand_buffer(",
        "reject the actual failed V22 replacement guard",
    )
    forged_f9 = left + forged_f9_cache + right
    require(digest(forged_f9) == F9_SHA and len(forged_f9) == 179147,
            "derive the entire genuine failed f9 solely as a negative control")
    variants = (
        (baseline + b"\n", materialized, matcher, "changed-complete-a0-base"),
        (baseline, baseline, matcher, "uncorrected-a0-base-as-new-variant"),
        (baseline, forged_f9, matcher, "known-failing-f9-early-return-guard"),
        (baseline, materialized + b"\n", matcher,
         "changed-materialized-1adb-complete-bytes"),
        (baseline, materialized.replace(capture_anchor, b"", 1), matcher,
         "deleted-seventeen-line-captured-findall-path"),
        (baseline, materialized.replace(original, failed, 1), matcher,
         "replacement-cache-early-return-regression"),
        (baseline, materialized.replace(outer, b"", 1) + b"x", matcher,
         "forged-outer-length-source-derivation"),
        (baseline, materialized, matcher + b"\n",
         "changed-first-party-rust-matching-engine"),
    )
    for fake_base, fake_variant, fake_matcher, label in variants:
        checks.append(reject(
            lambda first=fake_base, second=fake_variant, engine=fake_matcher:
                verify_variant(semantic, first, second, engine),
            "reject-materialized-first-party-" + label, *kinds,
        ))

    for key in sorted(native_build_plan()):
        bad = dict(state["native_plan"])
        bad.pop(key)
        checks.append(reject(
            lambda item=bad: validate_native_build_plan(item),
            "reject-missing-complete-offline-build-obligation-" + key, *kinds,
        ))
    for key, value in (
        ("status", "PASS"),
        ("label", "phase2-v22-rust-capture-shape-root-provenance"),
        ("rustc", "/home/dev-user/.cargo/bin/rustc"),
        ("cargo", "/home/dev-user/.cargo/bin/cargo"),
        ("phase_count", 1),
        ("processes_per_phase", 13),
        ("required_actual_distinct_compiler_process_count", 27),
        ("actual_compiler_process_count", 28),
        ("actual_process_ids", [1]),
        ("private_variant_sha256", F9_SHA),
        ("private_variant_bytes", 179147),
        ("private_corrected_adapter_sha256", "0" * 64),
        ("engine_sha256", "0" * 64),
        ("bridge_sha256", "0" * 64),
        ("public_build_receipt_sha256", "0" * 64),
        ("public_root_receipt_sha256", "0" * 64),
        ("external_cargo_dependency_count", 1),
        ("stdlib_re_engine", "ALLOWED"),
        ("stdlib_sre_engine", "ALLOWED"),
        ("external_regex_engine", "ALLOWED"),
        ("cross_candidate_engine", "ALLOWED"),
        ("matching_fallback", "ALLOWED"),
        ("compiler_processes_started", 1),
        ("candidate_imports", 1),
        ("private_roots_opened", 1),
        ("network_requests", 1),
        ("holdout", "OPENED"),
    ):
        bad = dict(state["native_plan"])
        bad[key] = value
        checks.append(reject(
            lambda item=bad: validate_native_build_plan(item),
            "reject-forged-offline-dual-build-" + key, *kinds,
        ))

    for section, key, value, label in (
        ("immutable_genuine_v22_failure", "candidate_status", "PASS",
         "historical-failed-candidate-as-pass"),
        ("immutable_genuine_v22_failure", "global_semantic_mismatch_count",
         2018, "observed-lower-bound-as-complete-mismatch-count"),
        ("immutable_genuine_v22_failure",
         "transient_physical_native_child_creation", False,
         "false-absence-of-transient-native-child"),
        ("immutable_genuine_v22_failure",
         "transient_physical_native_child_creation", True,
         "false-confirmation-of-transient-native-child"),
        ("immutable_genuine_v22_failure",
         "recorded_successfully_returned_child_interpreters", 1,
         "fabricated-successful-historical-child"),
        ("immutable_genuine_v22_failure",
         "failing_worker_native_library_loads", 0,
         "erased-two-real-historical-worker-native-loads"),
        ("materialized_first_party_variant", "native_build", "PASS",
         "materialized-source-as-native-build"),
        ("materialized_first_party_variant", "candidate_correctness", "PASS",
         "source-only-candidate-correctness"),
        ("materialized_first_party_variant", "native_engine_sha256",
         "0" * 64, "fabricated-engine-binary"),
        ("source_only_effects", "candidate_imports", 1,
         "unauthorized-candidate-import"),
        ("source_only_effects", "compiler_processes_started", 1,
         "unauthorized-native-compilation"),
        ("source_only_effects", "holdout", "OPENED",
         "opened-sealed-holdout"),
        ("source_only_effects", "performance", "1.5x",
         "invented-source-only-speed"),
        ("source_only_effects", "winner_selected", True,
         "invented-source-only-winner"),
    ):
        bad = capture.clone(semantic, frozen)
        assert isinstance(bad, dict)
        bad[section][key] = value
        checks.append(reject(
            lambda item=bad: validate_exact_document(
                capture, semantic, item, frozen, "complete V23 build freeze",
            ), "reject-v23-build-" + label, *kinds,
        ))

    flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    forbidden_paths = (
        (ROOT + "/candidates/_rust_engine.so", "installed-native-engine"),
        (ROOT + "/candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
         "installed-native-bridge"),
        (ROOT + "/candidates/zig_candidate.py", "other-candidate-family"),
        (ROOT + "/candidates/cpp_candidate.py", "other-native-family"),
        (ROOT + "/candidates/rust/variants/unapproved/py_bridge.c",
         "unapproved-variant"),
        (ROOT + "/tools/../candidates/_rust_engine.so",
         "lexical-native-path-traversal"),
        (ROOT + "/tools/./../candidates/rust_candidate.py",
         "lexical-candidate-path-traversal"),
        (ROOT + "/oracle/phase2/../../candidates/_rust_engine.so",
         "oracle-native-path-traversal"),
        (ROOT + "/oracle/phase3/expanded-sealed-holdout-v1.json",
         "sealed-phase-three-holdout"),
        (ROOT + "/oracle/phase2/evidence/forbidden.json.gz",
         "compressed-historical-archive"),
        ("/tmp/rebar-phase2-native-build-v9-rust-forbidden",
         "private-native-build-root"),
        ("/tmp/rebar-hidden-holdout", "external-hidden-holdout"),
        ("/etc/hosts", "foreign-unowned-source"),
    )
    for path, label in forbidden_paths:
        checks.append(reject(
            lambda target=path: os.open(target, flags),
            "physical-source-wall-rejects-os-open-" + label, *kinds,
        ))
        checks.append(reject(
            lambda target=path: wall.native_open(target, flags),
            "physical-source-wall-rejects-native-open-" + label, *kinds,
        ))

    historical_native = ROOT + "/candidates/_rust_engine.so"
    for label, action in (
        ("builtins-open", lambda: builtins.open(historical_native, "rb")),
        ("direct-_io-open", lambda: _io.open(historical_native, "rb")),
        ("direct-_io-fileio", lambda: _io.FileIO(historical_native, "r")),
        ("direct-io-open", lambda: io.open(historical_native, "rb")),
        ("direct-io-fileio", lambda: io.FileIO(historical_native, "r")),
        ("unowned-descriptor-read", lambda: os.read(0, 1)),
        ("unowned-descriptor-stat", lambda: os.fstat(0)),
        ("unowned-descriptor-close", lambda: os.close(0)),
        ("unowned-descriptor-dup", lambda: os.dup(0)),
        ("unowned-descriptor-fdopen", lambda: os.fdopen(0)),
        ("candidate-stat", lambda: os.stat(historical_native)),
        ("candidate-lstat", lambda: os.lstat(historical_native)),
        ("candidate-readlink", lambda: os.readlink(historical_native)),
        ("candidate-access", lambda: os.access(historical_native, os.R_OK)),
        ("candidate-listdir", lambda: os.listdir(ROOT + "/candidates")),
        ("candidate-scandir", lambda: os.scandir(ROOT + "/candidates")),
        ("clock-time", lambda: time.time()),
        ("clock-monotonic", lambda: time.monotonic()),
        ("clock-perf-counter", lambda: time.perf_counter()),
        ("entropy-urandom", lambda: os.urandom(8)),
        ("source-write", lambda: builtins.open(ROOT + "/" + SOURCE, "w")),
        ("stdlib-matcher", lambda: sys.audit("import", "re", None)),
        ("stdlib-native-matcher", lambda: sys.audit("import", "_sre", None)),
        ("external-regex-engine", lambda: sys.audit("import", "regex", None)),
        ("native-dynamic-loader", lambda: sys.audit("ctypes.dlopen", "x")),
        ("rust-compiler-process",
         lambda: sys.audit("subprocess.Popen", "rustc")),
        ("native-child-creation",
         lambda: sys.audit("cpython.PyInterpreterState_New")),
        ("private-build-root",
         lambda: sys.audit("tempfile.mkdtemp", "x")),
        ("network", lambda: sys.audit("socket.connect", "x")),
        ("untrusted-dynamic-code", lambda: sys.audit("exec", "x")),
    ):
        checks.append(reject(
            action, "physical-source-wall-rejects-" + label, *kinds,
        ))
    checks.append(reject(
        lambda: os.open(ROOT + "/" + SOURCE, os.O_RDONLY),
        "physical-source-wall-rejects-approved-owner-without-no-follow",
        *kinds,
    ))
    checks.append(reject(
        lambda: os.open(ROOT + "/" + SOURCE, flags | os.O_WRONLY | os.O_TRUNC),
        "physical-source-wall-rejects-approved-source-destruction",
        *kinds,
    ))

    for mode in ACTUAL_MODES:
        live_before = len(wall.live)
        blocks_before = dict(wall.blocked)
        checks.append(reject(
            lambda selected=mode: block_actual({"mode": selected}),
            "reject-unpushed-unexecuted-native-build-"
            + mode.removeprefix("--"), *kinds,
        ))
        require(len(wall.live) == live_before and wall.blocked == blocks_before,
                "reject a synthetic build mode without private or candidate I/O")

    extra = dict(frozen)
    extra["__fabricated_v23_native_build_evidence__"] = True
    checks.append(reject(
        lambda: validate_exact_document(
            capture, semantic, extra, frozen, "complete V23 build freeze",
        ), "reject-fabricated-v23-native-build-evidence", *kinds,
    ))
    no_matching_imports()
    require(wall.installed and not wall.live and bool(wall.blocked)
            and len(checks) >= 1200,
            "require complete physically isolated genuine-source controls")
    return checks


def parse_arguments(arguments: list[str]) -> dict:
    require(bool(arguments), "select one exact first-party V23 source mode")
    mode = arguments[0]
    require(mode in SOURCE_MODES + ACTUAL_MODES,
            "reject unknown first-party source or native-build modes")
    required = ["--source-sha256", "--protocol-sha256"]
    if mode != "--render-contract":
        required.append("--contract-sha256")
    require(len(arguments) == 1 + 2 * len(required),
            "independently caller-pin all exact V23 source-build owners")
    pins: dict[str, str] = {}
    for index in range(1, len(arguments), 2):
        flag, value = arguments[index], arguments[index + 1]
        require(flag in required and flag not in pins,
                "reject repeated or unowned source-build authority")
        pins[flag] = hash_pin(value, flag)
    require(set(pins) == set(required),
            "reject missing independently pinned source-build authority")
    return {"mode": mode, "pins": pins}


def main(arguments: list[str] | None = None) -> int:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.executable == PYTHON
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True,
        "require exact independently pinned CPython 3.14.6 with -I -B -S",
    )
    no_matching_imports()
    choice = parse_arguments(
        list(sys.argv[1:] if arguments is None else arguments),
    )
    if choice["mode"] in ACTUAL_MODES:
        block_actual(choice)
        raise BuildFreezeError("unreachable unauthorized V23 native build")

    wall = FirstPartySourceWall()
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
        "public_source_wall_installed_before_predecessor": wall.installed,
        "public_source_wall_live_descriptors": len(wall.live),
        "authenticated_static_first_party_owner_count": len(STATIC_OWNERS),
        "authenticated_canonical_rust_source_owner_count": 9,
        "canonical_original_sources_modified": False,
        "canonical_native_binary_files_opened": 0,
        "canonical_native_metadata_probes": 0,
        "materialized_variant_path": VARIANT_OWNER[1],
        "materialized_variant_sha256": VARIANT_SHA,
        "materialized_variant_bytes": VARIANT_BYTES,
        "materialized_variant_device": DEVICE,
        "materialized_variant_inode": VARIANT_OWNER[4],
        "materialized_variant_mode": "0600",
        "materialized_variant_uid": os.geteuid(),
        "materialized_variant_nlink": 1,
        "actual_a0_base_sha256": A0_SHA,
        "actual_a0_base_bytes": 179520,
        "exact_outer_length_blocks_removed": 1,
        "exact_outer_length_bytes_removed": 660,
        "replacement_cache_byte_identical": True,
        "original_replacement_branch_bytes": 97,
        "known_failed_f9_guard_present": False,
        "captured_fast_path_lines": 17,
        "matching_engine_sha256": MATCHER_SHA,
        "matching_engine_changed": False,
        "operational_correctness_campaign_sha256": CAMPAIGN_V23_OWNERS[2][2],
        "complete_v22_original_contract_field_count": 435,
        "complete_v21_inherited_contract_field_count": 402,
        "complete_actual_v22_failure_receipt_field_count": 96,
        "actual_v22_failure_receipt_sha256": PUBLIC_OWNERS[17][2],
        "actual_v22_candidate_status": "FAIL",
        "actual_v22_verified_passing_case_count": 14725,
        "actual_v22_observed_mismatch_lower_bound": 2018,
        "actual_v22_global_semantic_mismatch_count": NOT_MEASURED,
        "actual_v22_failing_worker_pid": 188,
        "actual_v22_failing_worker_candidate_imports": 1,
        "actual_v22_failing_worker_native_library_loads": 2,
        "actual_v22_recorded_successfully_returned_child_interpreters": 0,
        "actual_v22_recorded_installed_child_guards": 0,
        "actual_v22_recorded_child_case_interpreter_exec_calls": 0,
        "actual_v22_transient_physical_native_child_creation": NOT_MEASURED,
        "actual_v22_remaining_interpreter_warnings": 1,
        "actual_v22_destructor_warnings": 16,
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_supplemental_differential_case_count": 8244,
        "separate_corrected_reference_case_count": 6912,
        "supplemental_counted_in_original_denominator": False,
        "reference_counted_in_original_denominator": False,
        "absolute_rustc": RUSTC,
        "absolute_cargo": CARGO,
        "pinned_rust_toolchain_version": "1.95.0",
        "external_cargo_dependency_count": 0,
        "future_phase_count": 2,
        "future_required_distinct_compiler_process_count": 28,
        "actual_compiler_process_count": 0,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "reference_workers_started": 0,
        "compiler_processes_started": 0,
        "native_libraries_loaded": 0,
        "private_roots_created": 0,
        "private_roots_opened": 0,
        "archive_opens": 0,
        "hidden_cases_read": 0,
        "holdout_cases_opened": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "network_requests": 0,
        "hostile_control_count": len(checks),
        "hostile_controls": checks,
        "physically_blocked_effects": dict(wall.blocked),
        "native_engine_sha256": NOT_MEASURED,
        "native_bridge_sha256": NOT_MEASURED,
        "native_build_receipt_sha256": NOT_MEASURED,
        "native_root_receipt_sha256": NOT_MEASURED,
        "native_build": "NOT RUN",
        "actual_build_modes": {"run": "BLOCKED", "build": "BLOCKED"},
        "candidate_matching": "NOT RUN",
        "candidate_correctness": NOT_MEASURED,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "expanded_holdout_proposal_case_count": 14155776,
        "expanded_holdout_cases": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "holdout": "NOT OPENED",
        "performance": NOT_MEASURED,
        "memory": NOT_MEASURED,
        "confidence_intervals": NOT_MEASURED,
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
    except BuildFreezeError as error:
        sys.stderr.write("V23 native source-build rejected: " + str(error) + "\n")
        raise SystemExit(2)
