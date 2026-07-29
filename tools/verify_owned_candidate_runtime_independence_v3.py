#!/usr/bin/env python3
"""Authenticate genuine CPython child execution without replacing the V2 guard."""

from __future__ import annotations

import _thread
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
SELF = "tools/verify_owned_candidate_runtime_independence_v3.py"
PROTOCOL = "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V3.md"
CONTRACT = "oracle/phase2/candidate-runtime-independence-v3.json"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
GOAL = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3756,
    31364044,
)
V2 = {
    "source": (
        "tools/verify_owned_candidate_runtime_independence_v2.py",
        "f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a",
        67097,
        431371,
    ),
    "protocol": (
        "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md",
        "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c",
        4437,
        524886,
    ),
    "contract": (
        "oracle/phase2/candidate-runtime-independence-v2.json",
        "813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473",
        7671,
        524887,
    ),
}
PRODUCER = {
    "source": (
        "tools/run_owned_six_family_original_p0_producer_v5.py",
        "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538",
        102286,
        431370,
    ),
    "protocol": (
        "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md",
        "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4",
        5270,
        524884,
    ),
    "contract": (
        "oracle/phase2/six-family-p0-producer-v5.json",
        "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53",
        21036,
        524885,
    ),
}
PROVIDER_PATH = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/concurrent/interpreters/__init__.py"
)
PROVIDER_SHA256 = (
    "040e47f07bdfb28c67798fa7764fac1d79e13fd0fc0db9c85ee5dae8e1edf249"
)
PROVIDER_DEVICE = 2049
PROVIDER_INODE = 9595896
PROVIDER_BYTES = 7707
CREATE_EVENT = "cpython.PyInterpreterState_New"
LEGACY_INTERPRETER_EVENTS = frozenset(
    {"_interpreters.create", "_interpreters.exec"}
)
NATIVE_OWNER_KEYS = frozenset(
    {
        "absolute_path",
        "bytes",
        "device",
        "family",
        "file_name",
        "inode",
        "mode",
        "native_loaded",
        "nlink",
        "relative",
        "role",
        "sha256",
        "size_bytes",
        "uid",
    }
)
EFFECT_KEYS = frozenset(
    {
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
        "subinterpreters_created",
        "subprocesses_started",
        "threads_started",
        "timing_trials_run",
    }
)
OPTION_ROLES = (
    ("source", "--source-sha256"),
    ("protocol", "--protocol-sha256"),
    ("contract", "--contract-sha256"),
    ("v2-source", "--v2-source-sha256"),
    ("v2-protocol", "--v2-protocol-sha256"),
    ("v2-contract", "--v2-contract-sha256"),
    ("producer-source", "--producer-source-sha256"),
    ("producer-protocol", "--producer-protocol-sha256"),
    ("producer-contract", "--producer-contract-sha256"),
)


class BootstrapError(Exception):
    """An independently pinned source or real interpreter boundary failed."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise BootstrapError(message)


def sha256_pin(value: object, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        "require a complete lower-case SHA-256: " + label,
    )
    assert isinstance(value, str)
    return value


def read_owner(item: tuple, label: str) -> bytes:
    relative, expected, expected_bytes, expected_inode = item
    require(
        type(relative) is str
        and relative
        and not relative.startswith("/")
        and ".." not in relative.split("/")
        and not relative.endswith((".gz", ".so"))
        and "holdout" not in relative.lower()
        and "benchmark" not in relative.lower(),
        "reject an escaped, private, compressed, native, or holdout owner: "
        + label,
    )
    sha256_pin(expected, label)
    require(
        type(expected_bytes) is int and 0 < expected_bytes <= 4_194_304,
        "reject an absent or excessive frozen plaintext source: " + label,
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
            "reject a substituted or shared frozen plaintext owner: " + label,
        )
        remaining = expected_bytes
        pieces: list[bytes] = []
        while remaining:
            piece = os.read(descriptor, min(remaining, 262144))
            require(bool(piece), "reject a truncated owner: " + label)
            pieces.append(piece)
            remaining -= len(piece)
        require(not os.read(descriptor, 1), "reject an extended owner: " + label)
        raw = b"".join(pieces)
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
            "reject a changed or incompletely authenticated owner: " + label,
        )
        return raw
    finally:
        os.close(descriptor)


def load_immutable_v2() -> types.ModuleType:
    require(
        "re" not in sys.modules
        and "_sre" not in sys.modules
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "authenticate the immutable V2 guard before any regex or candidate",
    )
    raw = read_owner(V2["source"], "immutable V2 operational source")
    module = types.ModuleType("_rebar_exact_frozen_runtime_guard_v2_for_v3")
    module.__file__ = ROOT + "/" + V2["source"][0]
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    require(
        module.SELF == V2["source"][0]
        and module.PROTOCOL == V2["protocol"][0]
        and module.CONTRACT == V2["contract"][0]
        and callable(module.RuntimePolicy.prepare_family)
        and module.RuntimePolicy.prepare_family.__globals__ is module.__dict__
        and module.RuntimePolicy.prepare_family.__code__.co_filename
        == ROOT + "/" + V2["source"][0]
        and callable(module.child_bootstrap_source)
        and callable(module.verify_child_contract)
        and "re" not in sys.modules
        and "_sre" not in sys.modules,
        "preserve the exact V2 policy function, globals, code, and child source",
    )
    return module


BASE = load_immutable_v2()
GuardError = BASE.GuardError
JsonReader = BASE.JsonReader
canonical = BASE.canonical
MAXGROUPS = BASE.MAXGROUPS
DENIED_EVENTS = BASE.DENIED_EVENTS
FAMILY_BRIDGES = BASE.FAMILY_BRIDGES
child_bootstrap_source = BASE.child_bootstrap_source


def owner_identity(item: tuple) -> dict:
    relative, digest, count, inode = item
    return {
        "bytes": count,
        "device": 2064,
        "inode": inode,
        "mode": "0600",
        "nlink": 1,
        "path": relative,
        "sha256": digest,
    }


def dynamic_owner(relative: str, digest: str, label: str) -> tuple:
    require(
        relative in (SELF, PROTOCOL, CONTRACT),
        "reject an unowned V3 plaintext path: " + label,
    )
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
            "reject a changed or shared V3 source owner: " + label,
        )
        return relative, digest, actual.st_size, actual.st_ino
    finally:
        os.close(descriptor)


def read_provider_source() -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(PROVIDER_PATH, flags)
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_dev == PROVIDER_DEVICE
            and before.st_ino == PROVIDER_INODE
            and before.st_size == PROVIDER_BYTES
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600,
            "reject a replaced pinned CPython public-interpreter source",
        )
        remaining = PROVIDER_BYTES
        pieces: list[bytes] = []
        while remaining:
            piece = os.read(descriptor, min(remaining, 16384))
            require(bool(piece), "reject truncated public interpreter source")
            pieces.append(piece)
            remaining -= len(piece)
        require(not os.read(descriptor, 1), "reject extended interpreter source")
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        require(
            hashlib.sha256(raw).hexdigest() == PROVIDER_SHA256
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
            "reject modified or incompletely authenticated CPython source",
        )
        return raw
    finally:
        os.close(descriptor)


def source_code(root: types.CodeType, qualname: str) -> types.CodeType:
    matches: list[types.CodeType] = []

    def visit(value: types.CodeType) -> None:
        if value.co_qualname == qualname:
            matches.append(value)
        for nested in value.co_consts:
            if type(nested) is types.CodeType:
                visit(nested)

    visit(root)
    require(len(matches) == 1, "reject absent or ambiguous source code: " + qualname)
    return matches[0]


def same_source_function(
    value: object,
    expected: types.CodeType,
    namespace: dict,
    qualname: str,
) -> bool:
    return (
        type(value) is types.FunctionType
        and value.__code__ == expected
        and value.__globals__ is namespace
        and value.__qualname__ == qualname
    )


def actual_source_code(
    value: object,
    expected: types.CodeType,
    namespace: dict,
    qualname: str,
) -> types.CodeType:
    require(
        same_source_function(value, expected, namespace, qualname),
        "reject an unauthenticated live source function: " + qualname,
    )
    assert isinstance(value, types.FunctionType)
    return value.__code__


class RuntimePolicy(BASE.RuntimePolicy):
    """Keep V2 isolation and authenticate only real CPython child operations."""

    def __init__(self) -> None:
        super().__init__()
        self._suite_thread: int | None = None
        self._provider: types.ModuleType | None = None
        self._original_provider_create: object = None
        self._v5_guarded_create: object = None
        self._guarded_create_wrapper: object = None
        self._original_interpreter_exec: object = None
        self._guarded_exec_wrapper: object = None
        self._provider_create_code: types.CodeType | None = None
        self._creating = False
        self._creation_events = 0
        self._pending_creation_events = 0
        self._verified_creation_ids: set[int] = set()
        self._initial_live_ids: set[int] = set()
        self._active_execution_ids: set[int] = set()

    def _deny_if_wrong_thread(self) -> None:
        if self._suite_thread != _thread.get_ident():
            self.deny("cross-thread-or-unscoped-child-interpreter")

    def _source_authenticated_provider(
        self,
    ) -> tuple[types.ModuleType, types.CodeType]:
        provider = sys.modules.get("concurrent.interpreters")
        if not (
            type(provider) is types.ModuleType
            and provider.__name__ == "concurrent.interpreters"
            and os.path.realpath(str(getattr(provider, "__file__", "")))
            == PROVIDER_PATH
        ):
            self.deny("unattested-real-interpreter-provider")
        assert isinstance(provider, types.ModuleType)
        raw = read_provider_source()
        compiled = compile(raw, PROVIDER_PATH, "exec", dont_inherit=True)
        list_code = source_code(compiled, "list_all")
        source_code(compiled, "create")
        exec_code = source_code(compiled, "Interpreter.exec")
        close_code = source_code(compiled, "Interpreter.close")
        public_class = provider.__dict__.get("Interpreter")
        internal = sys.modules.get("_interpreters")
        if not (
            same_source_function(
                provider.__dict__.get("list_all"),
                list_code,
                provider.__dict__,
                "list_all",
            )
            and type(public_class) is type
            and public_class.__module__ == "concurrent.interpreters"
            and same_source_function(
                public_class.__dict__.get("close"),
                close_code,
                provider.__dict__,
                "Interpreter.close",
            )
            and type(internal) is types.ModuleType
            and internal.__name__ == "_interpreters"
            and getattr(getattr(internal, "__spec__", None), "origin", None)
            == "built-in"
            and provider.__dict__.get("_interpreters") is internal
            and type(getattr(internal, "create", None))
            is types.BuiltinFunctionType
            and getattr(internal.create, "__self__", None) is internal
            and type(getattr(internal, "exec", None))
            is types.BuiltinFunctionType
            and getattr(internal.exec, "__self__", None) is internal
        ):
            self.deny("substituted-source-authenticated-interpreter-provider")
        actual_exec = public_class.__dict__.get("exec")
        if self._guarded_exec_wrapper is None:
            if not same_source_function(
                actual_exec, exec_code, provider.__dict__, "Interpreter.exec"
            ):
                self.deny("substituted-original-public-interpreter-exec")
        elif actual_exec is not self._guarded_exec_wrapper:
            self.deny("substituted-active-public-interpreter-exec")
        return provider, compiled

    def _verified_v5_create(
        self, provider: types.ModuleType, provider_compiled: types.CodeType
    ) -> tuple[object, types.FunctionType]:
        raw = read_owner(PRODUCER["source"], "immutable V5 producer source")
        v5_code = compile(
            raw, ROOT + "/" + PRODUCER["source"][0], "exec", dont_inherit=True
        )
        guarded = provider.__dict__.get("create")
        guarded_code = source_code(
            v5_code, "observe_subinterpreters.<locals>.guarded_create"
        )
        if not (
            type(guarded) is types.FunctionType
            and guarded.__code__ == guarded_code
            and guarded.__globals__.get("SOURCE_RELATIVE")
            == PRODUCER["source"][0]
            and guarded.__globals__.get("RUNTIME_GUARD_SOURCE")
            == V2["source"][0]
            and guarded.__globals__.get("RUNTIME_GUARD_PROTOCOL")
            == V2["protocol"][0]
            and guarded.__globals__.get("RUNTIME_GUARD_CONTRACT")
            == V2["contract"][0]
            and guarded.__closure__ is not None
            and len(guarded.__closure__) == len(guarded.__code__.co_freevars)
        ):
            self.deny("substituted-original-V5-guarded-provider-create")
        assert isinstance(guarded, types.FunctionType)
        closure = dict(
            zip(guarded.__code__.co_freevars, guarded.__closure__, strict=True)
        )
        if set(closure) != {"GuardedOriginalInterpreter", "previous_create"}:
            self.deny("substituted-V5-create-closure")
        try:
            interpreter_class = closure["GuardedOriginalInterpreter"].cell_contents
            previous_create = closure["previous_create"].cell_contents
        except (ValueError, AttributeError):
            self.deny("empty-or-substituted-V5-create-closure")
        real_create_code = source_code(provider_compiled, "create")
        if not same_source_function(
            previous_create, real_create_code, provider.__dict__, "create"
        ):
            self.deny("substituted-original-pinned-provider-create")
        self._provider_create_code = actual_source_code(
            previous_create, real_create_code, provider.__dict__, "create"
        )
        expected_exec = source_code(
            v5_code,
            "observe_subinterpreters.<locals>.GuardedOriginalInterpreter.exec",
        )
        if not (
            type(interpreter_class) is type
            and interpreter_class.__name__ == "GuardedOriginalInterpreter"
            and type(interpreter_class.__dict__.get("exec"))
            is types.FunctionType
            and interpreter_class.__dict__["exec"].__code__ == expected_exec
            and interpreter_class.__dict__["exec"].__globals__
            is guarded.__globals__
        ):
            self.deny("substituted-V5-authenticated-child-interpreter-wrapper")
        assert isinstance(previous_create, types.FunctionType)
        return guarded, previous_create

    def begin_subinterpreters(
        self,
        *,
        suite: str = "subinterpreter_v2",
        expected_created: int = 11,
        expected_exec: int = 394,
    ) -> None:
        super().begin_subinterpreters(
            suite=suite,
            expected_created=expected_created,
            expected_exec=expected_exec,
        )
        self._suite_thread = _thread.get_ident()
        provider: types.ModuleType | None = None
        try:
            provider, compiled = self._source_authenticated_provider()
            guarded_create, original_create = self._verified_v5_create(
                provider, compiled
            )
            _, live = super().live_interpreter_provider()
            public_class = provider.__dict__["Interpreter"]
            original_exec = public_class.__dict__["exec"]

            def guarded_provider_create(*arguments: object, **keywords: object):
                return self._real_provider_create(arguments, keywords)

            def guarded_interpreter_exec(interpreter: object, source: object, /):
                return self._real_interpreter_exec(interpreter, source)

            self._provider = provider
            self._original_provider_create = original_create
            self._v5_guarded_create = guarded_create
            self._guarded_create_wrapper = guarded_provider_create
            self._original_interpreter_exec = original_exec
            self._guarded_exec_wrapper = guarded_interpreter_exec
            self._initial_live_ids = set(live)
            self._verified_creation_ids = set()
            self._active_execution_ids = set()
            self._creation_events = 0
            self._pending_creation_events = 0
            public_class.exec = guarded_interpreter_exec
            provider.create = guarded_provider_create
            if not (
                public_class.__dict__.get("exec") is guarded_interpreter_exec
                and provider.__dict__.get("create") is guarded_provider_create
            ):
                self.deny("failed-to-install-real-interpreter-boundaries")
        except BaseException:
            self._restore_provider_boundaries(provider)
            self.interpreter_suite = None
            self._suite_thread = None
            raise

    def _real_provider_create(
        self, arguments: tuple, keywords: dict
    ) -> object:
        self._deny_if_wrong_thread()
        provider = self._provider
        if not (
            self.interpreter_suite == "subinterpreter_v2"
            and type(provider) is types.ModuleType
            and provider.__dict__.get("create") is self._guarded_create_wrapper
            and provider.__dict__["Interpreter"].__dict__.get("exec")
            is self._guarded_exec_wrapper
            and not arguments
            and not keywords
            and self._creating is False
            and self._pending_creation_events == 0
            and self.child_creations < self.expected_child_creations
            and sys.gettrace() is None
            and sys.getprofile() is None
        ):
            self.deny("unscoped-or-reentrant-authenticated-provider-create")
        _, before = super().live_interpreter_provider()
        if not self._initial_live_ids.issubset(before):
            self.deny("changed-preexisting-public-interpreter-live-set")
        self._creating = True
        try:
            result = self._v5_guarded_create()
        finally:
            self._creating = False
        _, after = super().live_interpreter_provider()
        actual = getattr(result, "interpreter", None)
        identity = getattr(actual, "id", None)
        if not (
            self._pending_creation_events == 1
            and type(identity) is int
            and identity >= 0
            and after - before == {identity}
            and before.issubset(after)
            and identity not in self._initial_live_ids
            and identity not in self._verified_creation_ids
            and type(actual) is provider.__dict__["Interpreter"]
            and getattr(result, "id", None) == identity
        ):
            self._pending_creation_events = 0
            self.deny("missing-or-fabricated-native-child-creation")
        self._pending_creation_events = 0
        self._verified_creation_ids.add(identity)
        self.child_creations += 1
        return result

    def _real_interpreter_exec(
        self, interpreter: object, source: object
    ) -> object:
        self._deny_if_wrong_thread()
        provider = self._provider
        identity = getattr(interpreter, "id", None)
        state = self.child_bootstraps.get(identity)
        if not (
            self.interpreter_suite == "subinterpreter_v2"
            and type(provider) is types.ModuleType
            and type(interpreter) is provider.__dict__["Interpreter"]
            and provider.__dict__["Interpreter"].__dict__.get("exec")
            is self._guarded_exec_wrapper
            and type(identity) is int
            and identity in self._verified_creation_ids
            and identity not in self._active_execution_ids
            and type(state) is dict
            and state.get("interpreter") is interpreter
            and type(source) is str
            and self.child_executions
            < self.expected_child_case_executions + 22
        ):
            self.deny("unregistered-or-fabricated-real-child-execution")
        _, live = super().live_interpreter_provider()
        if identity not in live:
            self.deny("execution-on-a-destroyed-child-interpreter")
        first = state["dispatched"] is False
        if first:
            if not (
                state["installed"] is False
                and hashlib.sha256(source.encode("utf-8")).hexdigest()
                == state["sha256"]
            ):
                self.deny("unguarded-or-substituted-real-first-child-execution")
            state["dispatched"] = True
        elif state["installed"] is not True:
            self.deny("real-child-execution-before-positive-pipe-attestation")
        self._active_execution_ids.add(identity)
        try:
            result = self._original_interpreter_exec(interpreter, source)
        except BaseException:
            if first:
                state["dispatched"] = False
            raise
        finally:
            self._active_execution_ids.discard(identity)
        self.child_executions += 1
        return result

    def _strict_child_owner(self, owner: object, family: str, role: str) -> dict:
        if not (type(owner) is dict and set(owner) == NATIVE_OWNER_KEYS):
            self.deny("missing-or-extra-child-native-owner-fields:" + role)
        assert isinstance(owner, dict)
        relative = owner.get("relative")
        count = owner.get("bytes")
        if not (
            family in FAMILY_BRIDGES
            and role in ("bridge", "engine")
            and owner.get("family") == family
            and owner.get("role") == role
            and type(relative) is str
            and relative.startswith("candidates/")
            and ".." not in relative.split("/")
            and owner.get("absolute_path") == ROOT + "/" + relative
            and owner.get("file_name") == relative.rsplit("/", 1)[-1]
            and type(count) is int
            and 0 < count <= 8 * 1024 * 1024
            and owner.get("size_bytes") == count
            and owner.get("device") == 2064
            and type(owner.get("inode")) is int
            and owner["inode"] > 0
            and owner.get("mode") == 0o600
            and owner.get("uid") == os.geteuid()
            and owner.get("nlink") == 1
            and owner.get("native_loaded") is False
        ):
            self.deny("substituted-fourteen-field-child-native-owner:" + role)
        try:
            sha256_pin(owner.get("sha256"), "actual child " + role)
        except BootstrapError:
            self.deny("substituted-child-native-owner-digest:" + role)
        if role == "bridge":
            expected = FAMILY_BRIDGES[family]["owned_bridge_module"].rsplit(
                ".", 1
            )[1]
            if not owner["file_name"].startswith(expected + "."):
                self.deny("cross-family-child-native-bridge")
        return owner

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
            and self._suite_thread == _thread.get_ident()
            and type(identity) is int
            and identity in self._verified_creation_ids
            and identity not in self.child_bootstraps
        ):
            self.deny("child-without-authenticated-real-provider-creation")
        checked_bridge = self._strict_child_owner(bridge_owner, family, "bridge")
        checked_engine = self._strict_child_owner(engine_owner, family, "engine")
        if not (
            self._strict_child_owner(self.bridge_owner, family, "bridge")
            == checked_bridge
            and self._strict_child_owner(self.engine_owner, family, "engine")
            == checked_engine
        ):
            self.deny("substituted-source-owned-child-native-identity")
        return super().register_child_bootstrap(
            interpreter,
            source,
            family=family,
            source_sha256=source_sha256,
            protocol_sha256=protocol_sha256,
            contract_sha256=contract_sha256,
            bridge_owner=checked_bridge,
            engine_owner=checked_engine,
            owner=owner,
            attestation_fd=attestation_fd,
            read_fd=read_fd,
            challenge=challenge,
        )

    def _restore_provider_boundaries(
        self, provider: types.ModuleType | None
    ) -> None:
        if type(provider) is not types.ModuleType:
            return
        public_class = provider.__dict__.get("Interpreter")
        if type(public_class) is type and (
            public_class.__dict__.get("exec") is self._guarded_exec_wrapper
            and callable(self._original_interpreter_exec)
        ):
            public_class.exec = self._original_interpreter_exec
        if (
            provider.__dict__.get("create") is self._guarded_create_wrapper
            and callable(self._original_provider_create)
        ):
            provider.create = self._original_provider_create

    def end_subinterpreters(self) -> None:
        self._deny_if_wrong_thread()
        provider = self._provider
        try:
            if not (
                type(provider) is types.ModuleType
                and self._creating is False
                and self._pending_creation_events == 0
                and self._creation_events == 11
                and len(self._verified_creation_ids) == 11
                and not self._active_execution_ids
                and provider.__dict__.get("create")
                in (self._original_provider_create, self._guarded_create_wrapper)
                and provider.__dict__["Interpreter"].__dict__.get("exec")
                is self._guarded_exec_wrapper
            ):
                self.deny("incomplete-or-substituted-real-child-boundaries")
            super().end_subinterpreters()
        finally:
            self._restore_provider_boundaries(provider)
            self._suite_thread = None
            self._creating = False
            self._pending_creation_events = 0

    def audit(self, event: str, args: tuple) -> None:
        if event == CREATE_EVENT:
            if not (
                self.interpreter_suite == "subinterpreter_v2"
                and self._suite_thread == _thread.get_ident()
                and self._creating is True
                and self._pending_creation_events == 0
                and self._creation_events < self.expected_child_creations
                and type(args) is tuple
            ):
                self.deny("unscoped-or-fabricated-native-interpreter-creation")
            try:
                caller = sys._getframe(1)
            except (ValueError, AttributeError):
                self.deny("unverifiable-native-interpreter-creation-frame")
            if not (
                caller.f_code is self._provider_create_code
                and self._provider is not None
                and caller.f_globals is self._provider.__dict__
            ):
                self.deny("forged-native-interpreter-creation-frame")
            self._pending_creation_events = 1
            self._creation_events += 1
            return
        if event in LEGACY_INTERPRETER_EVENTS:
            self.deny("fabricated-or-unemitted-legacy-interpreter-event:" + event)
        return super().audit(event, args)


def strict_document(raw: bytes, label: str) -> dict:
    value = JsonReader(raw).parse()
    require(type(value) is dict, "require a complete JSON document: " + label)
    assert isinstance(value, dict)
    return value


def parse_options(arguments: list[str]) -> dict:
    modes = {"--self-test", "--verify-frozen-context"}
    allowed = {flag for _, flag in OPTION_ROLES}
    result: dict[str, object] = {}
    position = 0
    while position < len(arguments):
        name = arguments[position]
        if name in modes:
            require("mode" not in result, "reject repeated V3 source operation")
            result["mode"] = name
            position += 1
            continue
        require(
            name in allowed
            and name not in result
            and position + 1 < len(arguments),
            "reject missing, duplicate, or unowned V2/V3/V5 SHA-256 authority",
        )
        result[name] = sha256_pin(arguments[position + 1], name)
        position += 2
    require(
        result.get("mode") in modes and len(result) == len(OPTION_ROLES) + 1,
        "require one source mode and all nine independent frozen owner pins",
    )
    return result


def expected_contract(options: dict, own_source: tuple, own_protocol: tuple) -> dict:
    return {
        "schema": "rebar-owned-candidate-runtime-independence-v3-source-freeze",
        "version": 3,
        "status": "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE",
        "goal_sha256": GOAL[1],
        "source": owner_identity(own_source),
        "protocol": owner_identity(own_protocol),
        "immutable_predecessor_v2": {
            "version": 2,
            "owners": {role: owner_identity(item) for role, item in V2.items()},
            "policy": "EXACT AUTHENTICATED V2 RUNTIME POLICY SUBCLASS",
            "prepare_family": "INHERITED EXACT V2 FUNCTION AND GLOBALS",
            "child_bootstrap": "UNCHANGED AUTHENTICATED V2 CHILD SOURCE",
            "status": "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE",
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "immutable_producer_v5": {
            "version": 5,
            "owners": {
                role: owner_identity(item) for role, item in PRODUCER.items()
            },
            "source_mutated": False,
            "child_guard_identity": "EXACT V2 PREPARE GLOBALS AND CHILD PINS",
            "create_boundary": "AUTHENTICATED V5 GUARDED CREATE CLOSURE",
            "status": "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED",
        },
        "pinned_cpython": {
            "implementation": "cpython",
            "version": "3.14.6",
            "executable": PINNED_PYTHON,
            "flags": ["-I", "-B", "-S"],
            "public_interpreter_source": {
                "absolute_path": PROVIDER_PATH,
                "sha256": PROVIDER_SHA256,
                "bytes": PROVIDER_BYTES,
                "device": PROVIDER_DEVICE,
                "inode": PROVIDER_INODE,
                "mode": "0600",
                "nlink": 1,
            },
        },
        "phase_one": {
            "version": 4,
            "owners": {
                role: owner_identity(item) for role, item in BASE.P0.items()
            },
            "status": "PASS",
            "original_case_execution_denominator": 31237,
            "original_suite_count": 13,
            "original_obligation_count": 73,
            "named_private_waiver_count": 13,
            "separate_supplemental_case_count": 8244,
            "supplemental_cases_counted_in_original_denominator": False,
        },
        "first_party_candidate_families": {
            family: spec["candidate_module"]
            for family, spec in FAMILY_BRIDGES.items()
        },
        "family_bridge_policy": FAMILY_BRIDGES,
        "native_owner_policy": {
            "required_field_count": 14,
            "required_fields": sorted(NATIVE_OWNER_KEYS),
            "extra_or_missing_fields": "FORBIDDEN",
            "native_loaded": False,
            "identity": "EXACT PREPARED FAMILY SOURCE-OWNED NATIVE ARTIFACT",
        },
        "subinterpreter_bootstrap": {
            "suite": "subinterpreter_v2",
            "original_case_count": 128,
            "expected_interpreters_created": 11,
            "expected_interpreters_destroyed": 11,
            "expected_case_interpreter_exec_calls": 394,
            "expected_bootstrap_interpreter_exec_calls": 11,
            "expected_cleanup_interpreter_exec_calls": 11,
            "expected_total_real_interpreter_exec_calls": 416,
            "creation_audit_event": CREATE_EVENT,
            "creation_audit_arguments": "NOT MEASURED",
            "creation_identity": "AUTHENTICATED NATIVE PROVIDER FRAME AND REAL LIVE-SET DELTA",
            "execution_boundary": "SOURCE-AUTHENTICATED concurrent.interpreters.Interpreter.exec",
            "first_execution": "UNCHANGED V2 CHALLENGE-BOUND CHILD GUARD",
            "positive_attestation": "REAL UNIQUE OPERATING-SYSTEM PIPE",
            "unrestricted_creation": False,
            "legacy_interpreter_audit_events": "FORBIDDEN; NOT EMITTED AS GENUINE EXECUTION",
            "actual_interpreters_created": 0,
            "actual_interpreters_destroyed": 0,
            "actual_case_interpreter_exec_calls": 0,
            "actual_bootstrap_interpreter_exec_calls": 0,
            "actual_cleanup_interpreter_exec_calls": 0,
            "actual_child_guards_installed": 0,
            "candidate_status": "NOT RUN",
        },
        "source_only_effects": {key: 0 for key in sorted(EFFECT_KEYS)},
        "runtime_isolation_policy": {
            "bootstrap": "CPython -I -B -S; audit hook before candidate import",
            "candidate_alias": "sys.modules['re'] is the attested candidate",
            "stdlib_re_engine": "FORBIDDEN",
            "stdlib_sre_engine": "FORBIDDEN",
            "external_regex_package": "FORBIDDEN",
            "cross_candidate_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "native_loader": "ONLY INDIVIDUALLY ATTESTED FAMILY ARTIFACTS",
            "guard_installed_before_candidate_import": True,
            "source_gate_interpreters": "NOT CREATED",
        },
        "candidate_matching": "NOT RUN",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }


def denied(policy: RuntimePolicy, operation: object, label: str) -> int:
    try:
        require(callable(operation), "require one executable hostile control")
        operation()
    except (
        BootstrapError,
        GuardError,
        ImportError,
        ModuleNotFoundError,
        OSError,
        TypeError,
        ValueError,
    ):
        return 1
    raise BootstrapError("accepted a hostile real-child guard control: " + label)


def synthetic_owner(family: str, role: str) -> dict:
    basename = (
        FAMILY_BRIDGES[family]["owned_bridge_module"].rsplit(".", 1)[1]
        + ".cpython-314-x86_64-linux-gnu.so"
        if role == "bridge"
        else "_" + family + "_synthetic_engine.so"
    )
    relative = "candidates/" + basename
    return {
        "absolute_path": ROOT + "/" + relative,
        "bytes": 4096,
        "device": 2064,
        "family": family,
        "file_name": basename,
        "inode": 17 if role == "bridge" else 19,
        "mode": 0o600,
        "native_loaded": False,
        "nlink": 1,
        "relative": relative,
        "role": role,
        "sha256": ("1" if role == "bridge" else "2") * 64,
        "size_bytes": 4096,
        "uid": os.geteuid(),
    }


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
                "unprepared first-party family: " + name,
            )
    for name in ("_sre", "regex", "re._compiler"):
        count += denied(
            policy,
            lambda item=name: __import__(item),
            "physically blocked regex engine: " + name,
        )
    for event in DENIED_EVENTS:
        count += denied(
            policy,
            lambda item=event: sys.audit(item, "forbidden"),
            "physically blocked process/network/native event: " + event,
        )
    for event in (
        "os.fork",
        "rebar.correctness.clock",
        CREATE_EVENT,
        "_interpreters.create",
        "_interpreters.exec",
    ):
        count += denied(
            policy,
            lambda item=event: sys.audit(item, 1729, "fabricated"),
            "unscoped or forged genuine/legacy interpreter event: " + event,
        )
    count += denied(
        policy,
        lambda: policy.prepare_family("rust", bridge_owner={}, engine_owner={}),
        "unattested native family preparation",
    )
    require(
        type(policy).prepare_family is BASE.RuntimePolicy.prepare_family
        and type(policy).prepare_family.__globals__ is BASE.__dict__
        and type(policy).prepare_family.__globals__["SELF"] == V2["source"][0]
        and type(policy).prepare_family.__globals__["PROTOCOL"]
        == V2["protocol"][0]
        and type(policy).prepare_family.__globals__["CONTRACT"]
        == V2["contract"][0]
        and type(policy).prepare_family.__code__.co_filename
        == ROOT + "/" + V2["source"][0]
        and child_bootstrap_source is BASE.child_bootstrap_source,
        "reject an inherited-V2 or immutable-producer compatibility regression",
    )
    identity_source = (
        "def _owned_synthetic_provider_create():\n"
        "    return 1729\n"
    )
    identity_path = "<source-only-owned-provider-code-identity-v3>"
    first_identity_code = compile(
        identity_source, identity_path, "exec", dont_inherit=True
    )
    second_identity_code = compile(
        identity_source, identity_path, "exec", dont_inherit=True
    )
    identity_module = types.ModuleType("_rebar_source_only_provider_identity_v3")
    exec(first_identity_code, identity_module.__dict__)
    identity_function = identity_module.__dict__["_owned_synthetic_provider_create"]
    expected_identity = source_code(
        second_identity_code, "_owned_synthetic_provider_create"
    )
    live_identity = actual_source_code(
        identity_function,
        expected_identity,
        identity_module.__dict__,
        "_owned_synthetic_provider_create",
    )
    require(
        live_identity is identity_function.__code__
        and live_identity == expected_identity
        and live_identity is not expected_identity,
        "use the real live provider code identity, not its recompiled equal",
    )
    count += denied(
        policy,
        lambda: actual_source_code(
            identity_function,
            expected_identity,
            {},
            "_owned_synthetic_provider_create",
        ),
        "reject source-equal function with forged live namespace",
    )
    count += denied(
        policy,
        lambda: actual_source_code(
            identity_function,
            expected_identity,
            identity_module.__dict__,
            "_forged_provider_create",
        ),
        "reject source-equal function with forged live identity",
    )
    bridge = synthetic_owner("rust", "bridge")
    engine = synthetic_owner("rust", "engine")
    require(
        policy._strict_child_owner(bridge, "rust", "bridge") is bridge
        and policy._strict_child_owner(engine, "rust", "engine") is engine,
        "reject source-only genuinely shaped V5 native identity controls",
    )
    for role, original in (("bridge", bridge), ("engine", engine)):
        for key in sorted(NATIVE_OWNER_KEYS):
            missing = dict(original)
            missing.pop(key)
            count += denied(
                policy,
                lambda item=missing, kind=role: policy._strict_child_owner(
                    item, "rust", kind
                ),
                "missing V5 child native field: " + role + "/" + key,
            )
        extra = dict(original)
        extra["unexpected_field"] = True
        count += denied(
            policy,
            lambda item=extra, kind=role: policy._strict_child_owner(
                item, "rust", kind
            ),
            "invented V5 child native field: " + role,
        )
        for key, replacement in (
            ("absolute_path", ROOT + "/candidates/substituted.so"),
            ("bytes", 4097),
            ("device", 2049),
            ("family", "zig"),
            ("file_name", "substituted.so"),
            ("inode", 0),
            ("mode", 0o644),
            ("native_loaded", True),
            ("nlink", 2),
            ("relative", "../substituted.so"),
            ("role", "engine" if role == "bridge" else "bridge"),
            ("sha256", "invalid"),
            ("size_bytes", 4097),
            ("uid", os.geteuid() + 1),
        ):
            forged = dict(original)
            forged[key] = replacement
            count += denied(
                policy,
                lambda item=forged, kind=role: policy._strict_child_owner(
                    item, "rust", kind
                ),
                "forged V5 child native field: " + role + "/" + key,
            )
    policy.prepared_family = "rust"
    policy.selected_family = FAMILY_BRIDGES["rust"]["candidate_module"]
    policy.approved_bridge_module = FAMILY_BRIDGES["rust"][
        "owned_bridge_module"
    ]
    policy.bridge_owner = bridge
    policy.engine_owner = engine
    policy.check_import("candidates")
    policy.check_import(FAMILY_BRIDGES["rust"]["candidate_module"])
    policy.check_import(FAMILY_BRIDGES["rust"]["owned_bridge_module"])
    for family, spec in FAMILY_BRIDGES.items():
        if family != "rust":
            for name in (spec["candidate_module"], spec["owned_bridge_module"]):
                count += denied(
                    policy,
                    lambda item=name: policy.check_import(item),
                    "cross-family candidate or bridge: " + name,
                )
    fake = types.ModuleType(FAMILY_BRIDGES["rust"]["candidate_module"])
    policy.bind_selected(fake, "rust")
    require(
        sys.modules.get("re") is fake
        and sys.modules.get("re._constants") is policy.constants
        and getattr(policy.constants, "MAXGROUPS", None) == MAXGROUPS
        and __import__("re") is fake,
        "preserve the synthetic selected alias and data-only V2 MAXGROUPS",
    )
    saved_alias = sys.modules["re"]
    sys.modules["re"] = types.ModuleType("_hostile_replacement")
    count += denied(policy, policy.check_modules, "substituted public re alias")
    sys.modules["re"] = saved_alias
    assert policy.constants is not None
    policy.constants.MAXGROUPS = MAXGROUPS + 1
    count += denied(
        policy,
        lambda: policy.check_import("re._constants"),
        "substituted exact data-only MAXGROUPS",
    )
    policy.constants.MAXGROUPS = MAXGROUPS
    count += denied(
        policy,
        lambda: policy.begin_subinterpreters(suite="invented_suite"),
        "unscoped original child suite",
    )
    policy.interpreter_suite = "subinterpreter_v2"
    policy.expected_child_creations = 11
    policy.expected_child_case_executions = 394
    policy._suite_thread = _thread.get_ident()
    fake_child = types.SimpleNamespace(id=1729, exec=lambda item: None)
    pins = {
        "family": "rust",
        "source_sha256": options["--v2-source-sha256"],
        "protocol_sha256": options["--v2-protocol-sha256"],
        "contract_sha256": options["--v2-contract-sha256"],
        "bridge_owner": bridge,
        "engine_owner": engine,
        "owner": "A",
        "attestation_fd": 999,
        "read_fd": 998,
        "challenge": "3" * 64,
    }
    canonical_child = child_bootstrap_source(
        family=pins["family"],
        source_sha256=pins["source_sha256"],
        protocol_sha256=pins["protocol_sha256"],
        contract_sha256=pins["contract_sha256"],
        bridge_owner=bridge,
        engine_owner=engine,
        owner="A",
        attestation_fd=999,
        challenge="3" * 64,
    )
    for source in ("pass", canonical_child):
        count += denied(
            policy,
            lambda item=source: policy.register_child_bootstrap(
                fake_child, item, **pins
            ),
            "forged child without real native creation or live public identity",
        )
        count += denied(
            policy,
            lambda item=source: policy._real_interpreter_exec(fake_child, item),
            "fabricated public Interpreter.exec source or identity",
        )
    for event in (CREATE_EVENT, *sorted(LEGACY_INTERPRETER_EVENTS)):
        count += denied(
            policy,
            lambda item=event: sys.audit(item, 1729, canonical_child),
            "synthetic audit cannot create or execute a real interpreter",
        )
    policy._creating = True
    policy._pending_creation_events = 0
    count += denied(
        policy,
        lambda: sys.audit(CREATE_EVENT),
        "synthetic creation audit lacks the genuine pinned-provider frame",
    )
    policy._creating = False
    count += denied(
        policy,
        lambda: policy._real_provider_create((), {}),
        "invented provider create without an authenticated V5 boundary",
    )
    count += denied(
        policy,
        lambda: policy.confirm_child_guard(fake_child),
        "fabricated real-pipe child confirmation",
    )
    count += denied(
        policy,
        policy.end_subinterpreters,
        "fabricated eleven-child/416-execution lifecycle",
    )
    policy.interpreter_suite = None
    policy._suite_thread = None
    policy.child_bootstraps = {}
    count += denied(
        policy,
        lambda: policy.begin_fork_case("invented.original.case"),
        "unscoped original public fork",
    )
    policy.begin_fork_case("ReTests.test_regression_gh94675")
    sys.audit("os.fork")
    count += denied(policy, lambda: sys.audit("os.fork"), "second scoped fork")
    policy.end_fork_case()
    count += denied(
        policy,
        lambda: policy.begin_correctness_clock("invented.original.case"),
        "unscoped original correctness clock",
    )
    policy.begin_correctness_clock("ReTests.test_search_anchor_at_beginning")
    sys.audit("rebar.correctness.clock")
    sys.audit("rebar.correctness.clock")
    count += denied(
        policy,
        lambda: sys.audit("rebar.correctness.clock"),
        "third original scoped correctness clock",
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
        count >= 120
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and "concurrent.interpreters" not in sys.modules
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "preserve all isolation controls without starting an actual child",
    )
    return count


def validate_frozen_producer(document: dict) -> None:
    require(
        document.get("schema")
        == "rebar-owned-six-family-original-p0-producer-v5-source-freeze"
        and document.get("version") == 5
        and document.get("status")
        == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
        and document.get("candidate_matching") == "NOT RUN"
        and document.get("runtime_non_delegation") == "NOT ESTABLISHED"
        and document.get("holdout") == "NOT OPENED"
        and document.get("qualified_candidate_count") == 0
        and document.get("winner_selected") is False,
        "reject a substituted or falsely qualified immutable V5 producer",
    )
    guard = document.get("runtime_guard_v2")
    require(
        type(guard) is dict
        and guard.get("status")
        == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
        and guard.get("runtime_non_delegation") == "NOT ESTABLISHED"
        and all(guard.get(role) == owner_identity(item) for role, item in V2.items()),
        "reject V5's exact original V2 child guard or frozen owner identity",
    )
    phase_one = document.get("phase_one_v4")
    nested = document.get("guarded_nested_lifecycle")
    require(
        type(phase_one) is dict
        and phase_one.get("status") == "PASS"
        and phase_one.get("original_case_execution_denominator") == 31237
        and phase_one.get("suite_count") == 13
        and phase_one.get("original_obligation_count") == 73
        and phase_one.get("named_private_waiver_count") == 13
        and phase_one.get("supplemental_case_count") == 8244
        and phase_one.get("supplemental_cases_counted_in_original_denominator")
        is False
        and type(nested) is dict
        and nested.get("suite") == "subinterpreter_v2"
        and nested.get("case_count") == 128
        and nested.get("case_execution_count") == 394
        and nested.get("created_interpreter_count") == 11
        and nested.get("destroyed_interpreter_count") == 11
        and nested.get("actual_case_execution_count") == 0
        and nested.get("actual_created_interpreter_count") == 0
        and nested.get("actual_child_guards_installed") == 0,
        "preserve all original cases without inventing an actual child run",
    )


def source_run(options: dict) -> dict:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.flags.dont_write_bytecode == 1
        and os.path.abspath(sys.executable) == PINNED_PYTHON
        and os.path.realpath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == ROOT + "/" + SELF
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and "concurrent.interpreters" not in sys.modules
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "require exact clean CPython 3.14.6 -I -B -S without an interpreter",
    )
    read_owner(GOAL, "immutable exact experiment objective")
    for role, item in V2.items():
        require(
            options["--v2-" + role + "-sha256"] == item[1],
            "require an independently supplied immutable V2 " + role + " pin",
        )
        read_owner(item, "exact immutable V2 guard " + role)
    BASE.verify_child_contract(
        options["--v2-source-sha256"],
        options["--v2-protocol-sha256"],
        options["--v2-contract-sha256"],
    )
    for role, item in PRODUCER.items():
        require(
            options["--producer-" + role + "-sha256"] == item[1],
            "require an independently supplied immutable V5 " + role + " pin",
        )
        read_owner(item, "exact immutable V5 producer " + role)
    producer = strict_document(
        read_owner(PRODUCER["contract"], "exact original V5 contract"),
        "exact original V5 contract",
    )
    validate_frozen_producer(producer)
    provider_raw = read_provider_source()
    compiled = compile(provider_raw, PROVIDER_PATH, "exec", dont_inherit=True)
    for qualname in ("create", "list_all", "Interpreter.exec", "Interpreter.close"):
        source_code(compiled, qualname)
    own_source = dynamic_owner(SELF, options["--source-sha256"], "V3 source")
    own_protocol = dynamic_owner(
        PROTOCOL, options["--protocol-sha256"], "V3 protocol"
    )
    own_contract = dynamic_owner(
        CONTRACT, options["--contract-sha256"], "V3 machine contract"
    )
    read_owner(own_source, "complete source-frozen V3 implementation")
    read_owner(own_protocol, "complete source-frozen V3 protocol")
    contract = strict_document(
        read_owner(own_contract, "complete source-frozen V3 contract"),
        "complete V3 machine contract",
    )
    expected = expected_contract(options, own_source, own_protocol)
    require(
        canonical(contract) == canonical(expected),
        "reject any missing, extra, substituted, or falsely measured V3 policy",
    )
    policy = RuntimePolicy()
    policy.install()
    rejected = hostile_controls(policy, options)
    return {
        "schema": "rebar-owned-candidate-runtime-independence-v3-source-"
        + (
            "self-test"
            if options["mode"] == "--self-test"
            else "frozen-context"
        ),
        "version": 3,
        "status": "PASS",
        "source_sha256": options["--source-sha256"],
        "protocol_sha256": options["--protocol-sha256"],
        "contract_sha256": options["--contract-sha256"],
        "immutable_v2_source_sha256": V2["source"][1],
        "immutable_v5_producer_source_sha256": PRODUCER["source"][1],
        "pinned_public_interpreter_source_sha256": PROVIDER_SHA256,
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "separate_supplemental_case_count": 8244,
        "candidate_family_count": 6,
        "required_native_owner_field_count": 14,
        "rejected_hostile_control_count": rejected,
        "physically_blocked_controls": dict(policy.blocked),
        "creation_audit_event": CREATE_EVENT,
        "actual_creation_audit_arguments": "NOT MEASURED",
        "expected_real_interpreters": 11,
        "expected_original_case_interpreter_exec_calls": 394,
        "expected_total_real_interpreter_exec_calls": 416,
        "actual_interpreters_created": 0,
        "actual_interpreters_destroyed": 0,
        "actual_child_guards_installed": 0,
        "actual_case_interpreter_exec_calls": 0,
        "actual_bootstrap_interpreter_exec_calls": 0,
        "actual_cleanup_interpreter_exec_calls": 0,
        "actual_candidate_imports": 0,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_native_loads": 0,
        "actual_native_root_opens": 0,
        "actual_archive_opens": 0,
        "actual_processes_started": 0,
        "actual_threads_started": 0,
        "actual_network_requests": 0,
        "actual_benchmark_clock_samples": 0,
        "actual_holdout_cases_read": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_matching": "NOT RUN",
        "qualified_candidate_count": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def main() -> int:
    try:
        options = parse_options(sys.argv[1:])
        sys.stdout.buffer.write(canonical(source_run(options)))
        return 0
    except Exception as error:
        sys.stderr.write("genuine CPython child guard rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
