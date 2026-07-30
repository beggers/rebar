#!/usr/bin/env python3
"""Authenticate real interpreter boundaries without inventing audit events."""

from __future__ import annotations

import _thread
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
SELF = "tools/verify_owned_candidate_runtime_independence_v4.py"
PROTOCOL = "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V4.md"
CONTRACT = "oracle/phase2/candidate-runtime-independence-v4.json"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
V3_OWNERS = {
    "source": (
        "tools/verify_owned_candidate_runtime_independence_v3.py",
        "03f051e428ee31bb671d8ced82f02d7a9fe3520f24191aba78d2e8a0697202c2",
        59765,
        430856,
    ),
    "protocol": (
        "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V3.md",
        "d3437b642d322ccccf12851981555cb596ff7f9c5a12e0a6a389d6b80b5a068a",
        5297,
        525096,
    ),
    "contract": (
        "oracle/phase2/candidate-runtime-independence-v3.json",
        "31e9a5d2754b5b4b273d4fc30d6a27967e495b57684fdd1e9306bbac3b2caaa7",
        9157,
        525114,
    ),
}
OPTION_ROLES = (
    ("source", "--source-sha256"),
    ("protocol", "--protocol-sha256"),
    ("contract", "--contract-sha256"),
    ("v3-source", "--v3-source-sha256"),
    ("v3-protocol", "--v3-protocol-sha256"),
    ("v3-contract", "--v3-contract-sha256"),
    ("v2-source", "--v2-source-sha256"),
    ("v2-protocol", "--v2-protocol-sha256"),
    ("v2-contract", "--v2-contract-sha256"),
    ("producer-source", "--producer-source-sha256"),
    ("producer-protocol", "--producer-protocol-sha256"),
    ("producer-contract", "--producer-contract-sha256"),
)


class BootstrapError(Exception):
    """An immutable source or authentic interpreter boundary was rejected."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise BootstrapError(message)


def sha256_pin(value: object, label: str) -> str:
    require(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        "require a complete independent lowercase SHA-256: " + label,
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
        "reject an absent or oversized frozen plaintext owner: " + label,
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
            "reject a substituted, shared, or unauthenticated owner: " + label,
        )
        remaining = expected_bytes
        pieces: list[bytes] = []
        while remaining:
            piece = os.read(descriptor, min(remaining, 262144))
            require(bool(piece), "reject a truncated frozen owner: " + label)
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


def load_immutable_v3() -> types.ModuleType:
    require(
        "re" not in sys.modules
        and "_sre" not in sys.modules
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "authenticate immutable V3 before a candidate or regex engine",
    )
    raw = read_owner(V3_OWNERS["source"], "immutable V3 operational source")
    module = types.ModuleType("_rebar_exact_frozen_runtime_guard_v3_for_v4")
    module.__file__ = ROOT + "/" + V3_OWNERS["source"][0]
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    require(
        module.SELF == V3_OWNERS["source"][0]
        and module.PROTOCOL == V3_OWNERS["protocol"][0]
        and module.CONTRACT == V3_OWNERS["contract"][0]
        and module.RuntimePolicy.prepare_family
        is module.BASE.RuntimePolicy.prepare_family
        and module.RuntimePolicy.prepare_family.__globals__
        is module.BASE.__dict__
        and module.RuntimePolicy.prepare_family.__code__.co_filename
        == ROOT + "/" + module.V2["source"][0]
        and module.child_bootstrap_source is module.BASE.child_bootstrap_source
        and callable(module.BASE.verify_child_contract)
        and "re" not in sys.modules
        and "_sre" not in sys.modules,
        "preserve immutable V3 and the exact immutable V2 producer identity",
    )
    return module


PREVIOUS = load_immutable_v3()
BASE = PREVIOUS.BASE
V2 = PREVIOUS.V2
PRODUCER = PREVIOUS.PRODUCER
GOAL = PREVIOUS.GOAL
GuardError = BASE.GuardError
JsonReader = BASE.JsonReader
canonical = BASE.canonical
MAXGROUPS = BASE.MAXGROUPS
DENIED_EVENTS = BASE.DENIED_EVENTS
FAMILY_BRIDGES = BASE.FAMILY_BRIDGES
NATIVE_OWNER_KEYS = PREVIOUS.NATIVE_OWNER_KEYS
EFFECT_KEYS = PREVIOUS.EFFECT_KEYS
child_bootstrap_source = BASE.child_bootstrap_source
verify_child_contract = BASE.verify_child_contract
CREATE_EVENT = PREVIOUS.CREATE_EVENT
FORGED_INTERPRETER_EVENTS = frozenset(
    {CREATE_EVENT, *PREVIOUS.LEGACY_INTERPRETER_EVENTS}
)


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
        "reject an unowned V4 plaintext path: " + label,
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
            "reject a shared or substituted V4 owner: " + label,
        )
        return relative, digest, actual.st_size, actual.st_ino
    finally:
        os.close(descriptor)


class RuntimePolicy(PREVIOUS.RuntimePolicy):
    """Guard genuine builtin boundaries; Python audit names are never proof."""

    def __init__(self) -> None:
        super().__init__()
        self._internal_provider: types.ModuleType | None = None
        self._native_originals: dict[str, object] = {}
        self._native_wrappers: dict[str, object] = {}
        self._provider_exec_code: types.CodeType | None = None
        self._provider_close_code: types.CodeType | None = None
        self._native_create_calls = 0
        self._native_exec_calls = 0
        self._native_destroy_calls = 0
        self._pending_native_identity: int | None = None
        self._destroyed_creation_ids: set[int] = set()

    def _native_boundaries_intact(self) -> bool:
        internal = self._internal_provider
        return (
            type(internal) is types.ModuleType
            and set(self._native_originals) == {"create", "exec", "destroy"}
            and set(self._native_wrappers) == {"create", "exec", "destroy"}
            and all(
                getattr(internal, role, None) is self._native_wrappers[role]
                for role in self._native_wrappers
            )
        )

    def _provider_caller(self, expected: types.CodeType | None) -> bool:
        try:
            caller = sys._getframe(3)
        except (ValueError, AttributeError):
            return False
        return (
            expected is not None
            and caller.f_code is expected
            and self._provider is not None
            and caller.f_globals is self._provider.__dict__
        )

    def _restore_native_boundaries(self) -> None:
        internal = self._internal_provider
        if type(internal) is not types.ModuleType:
            return
        for role, original in self._native_originals.items():
            if getattr(internal, role, None) is self._native_wrappers.get(role):
                setattr(internal, role, original)

    def _native_live_ids(self) -> set[int]:
        internal = self._internal_provider
        listing = getattr(internal, "list_all", None)
        if not (
            type(internal) is types.ModuleType
            and type(listing) is types.BuiltinFunctionType
            and getattr(listing, "__self__", None) is internal
            and getattr(listing, "__name__", None) == "list_all"
        ):
            self.deny("substituted-genuine-native-live-interpreter-list")
        values = listing()
        if type(values) is not list:
            self.deny("fabricated-genuine-native-live-interpreter-list")
        identities: set[int] = set()
        for value in values:
            if not (
                type(value) is tuple
                and len(value) >= 1
                and type(value[0]) is int
                and value[0] >= 0
                and value[0] not in identities
            ):
                self.deny("fabricated-genuine-native-live-interpreter-identity")
            identities.add(value[0])
        return identities

    def _install_native_boundaries(self) -> None:
        provider = self._provider
        if type(provider) is not types.ModuleType:
            self.deny("missing-source-authenticated-native-provider")
        internal = provider.__dict__.get("_interpreters")
        if not (
            type(internal) is types.ModuleType
            and internal is sys.modules.get("_interpreters")
            and getattr(getattr(internal, "__spec__", None), "origin", None)
            == "built-in"
        ):
            self.deny("substituted-native-interpreter-module")
        assert isinstance(internal, types.ModuleType)
        originals: dict[str, object] = {}
        for role in ("create", "exec", "destroy"):
            original = getattr(internal, role, None)
            if not (
                type(original) is types.BuiltinFunctionType
                and getattr(original, "__self__", None) is internal
                and getattr(original, "__name__", None) == role
            ):
                self.deny("substituted-authenticated-native-builtin:" + role)
            originals[role] = original

        raw = PREVIOUS.read_provider_source()
        compiled = compile(
            raw, PREVIOUS.PROVIDER_PATH, "exec", dont_inherit=True
        )
        original_exec = self._original_interpreter_exec
        public_class = provider.__dict__.get("Interpreter")
        expected_exec = PREVIOUS.source_code(compiled, "Interpreter.exec")
        expected_close = PREVIOUS.source_code(compiled, "Interpreter.close")
        if not (
            type(public_class) is type
            and PREVIOUS.same_source_function(
                original_exec,
                expected_exec,
                provider.__dict__,
                "Interpreter.exec",
            )
            and PREVIOUS.same_source_function(
                public_class.__dict__.get("close"),
                expected_close,
                provider.__dict__,
                "Interpreter.close",
            )
        ):
            self.deny("substituted-authenticated-native-provider-descriptor")
        assert isinstance(original_exec, types.FunctionType)
        close = public_class.__dict__["close"]
        assert isinstance(close, types.FunctionType)
        self._provider_exec_code = original_exec.__code__
        self._provider_close_code = close.__code__
        self._internal_provider = internal
        self._native_originals = originals

        def native_create(*arguments: object, **keywords: object):
            return self._authenticated_native_create(arguments, keywords)

        def native_exec(*arguments: object, **keywords: object):
            return self._authenticated_native_exec(arguments, keywords)

        def native_destroy(*arguments: object, **keywords: object):
            return self._authenticated_native_destroy(arguments, keywords)

        self._native_wrappers = {
            "create": native_create,
            "exec": native_exec,
            "destroy": native_destroy,
        }
        try:
            for role, wrapper in self._native_wrappers.items():
                setattr(internal, role, wrapper)
            if not self._native_boundaries_intact():
                self.deny("failed-to-install-first-party-native-boundaries")
        except BaseException:
            self._restore_native_boundaries()
            raise

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
        self._native_create_calls = 0
        self._native_exec_calls = 0
        self._native_destroy_calls = 0
        self._pending_native_identity = None
        self._destroyed_creation_ids = set()
        try:
            self._install_native_boundaries()
        except BaseException:
            self._restore_native_boundaries()
            self._restore_provider_boundaries(self._provider)
            self.interpreter_suite = None
            self._suite_thread = None
            raise

    def _authenticated_native_create(
        self, arguments: tuple, keywords: dict
    ) -> object:
        self._deny_if_wrong_thread()
        if not (
            self.interpreter_suite == "subinterpreter_v2"
            and self._creating is True
            and self._native_boundaries_intact()
            and self._provider_caller(self._provider_create_code)
            and arguments == ()
            and keywords == {"reqrefs": True}
            and self._pending_native_identity is None
            and self._native_create_calls == self.child_creations
            and self._native_create_calls < self.expected_child_creations
        ):
            self.deny("direct-or-fabricated-native-interpreter-create")
        before = self._native_live_ids()
        original = self._native_originals["create"]
        result = original(*arguments, **keywords)
        after = self._native_live_ids()
        if not (
            type(result) is int
            and result >= 0
            and after - before == {result}
            and before.issubset(after)
            and self._initial_live_ids.issubset(before)
            and result not in self._initial_live_ids
            and result not in self._verified_creation_ids
        ):
            self.deny("missing-or-fabricated-genuine-native-live-set-delta")
        self._pending_native_identity = result
        self._native_create_calls += 1
        return result

    def _authenticated_native_exec(
        self, arguments: tuple, keywords: dict
    ) -> object:
        self._deny_if_wrong_thread()
        identity = arguments[0] if len(arguments) >= 1 else None
        source = arguments[1] if len(arguments) >= 2 else None
        if not (
            self.interpreter_suite == "subinterpreter_v2"
            and self._native_boundaries_intact()
            and self._provider_caller(self._provider_exec_code)
            and len(arguments) == 2
            and type(identity) is int
            and identity in self._verified_creation_ids
            and identity not in self._destroyed_creation_ids
            and identity in self._active_execution_ids
            and type(source) is str
            and keywords == {"restrict": True}
            and self._native_exec_calls < self.expected_child_case_executions + 22
        ):
            self.deny("direct-or-fabricated-native-interpreter-exec")
        _, live = BASE.RuntimePolicy.live_interpreter_provider(self)
        if identity not in live:
            self.deny("native-execution-on-destroyed-child-interpreter")
        original = self._native_originals["exec"]
        result = original(*arguments, **keywords)
        if result is None:
            self._native_exec_calls += 1
        return result

    def _authenticated_native_destroy(
        self, arguments: tuple, keywords: dict
    ) -> object:
        self._deny_if_wrong_thread()
        identity = arguments[0] if len(arguments) == 1 else None
        if not (
            self.interpreter_suite == "subinterpreter_v2"
            and self._native_boundaries_intact()
            and self._provider_caller(self._provider_close_code)
            and len(arguments) == 1
            and type(identity) is int
            and identity in self._verified_creation_ids
            and identity not in self._destroyed_creation_ids
            and identity not in self._active_execution_ids
            and keywords == {"restrict": True}
            and self._native_destroy_calls < self.expected_child_creations
        ):
            self.deny("direct-or-fabricated-native-interpreter-destroy")
        _, before = BASE.RuntimePolicy.live_interpreter_provider(self)
        original = self._native_originals["destroy"]
        result = original(*arguments, **keywords)
        _, after = BASE.RuntimePolicy.live_interpreter_provider(self)
        if not (
            result is None
            and identity in before
            and before - after == {identity}
            and after.issubset(before)
            and self._initial_live_ids.issubset(after)
        ):
            self.deny("missing-or-fabricated-genuine-native-child-destruction")
        self._destroyed_creation_ids.add(identity)
        self._native_destroy_calls += 1
        return result

    def _creation_evidence(
        self,
        before: set[int],
        after: set[int],
        identity: object,
        actual: object,
        result: object,
        public_class: object,
    ) -> bool:
        return (
            self._pending_creation_events == 0
            and self._creation_events == 0
            and type(identity) is int
            and identity >= 0
            and after - before == {identity}
            and before.issubset(after)
            and self._initial_live_ids.issubset(before)
            and identity not in self._initial_live_ids
            and identity not in self._verified_creation_ids
            and self._pending_native_identity == identity
            and self._native_create_calls == self.child_creations + 1
            and type(actual) is public_class
            and getattr(result, "id", None) == identity
        )

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
            and self._native_boundaries_intact()
            and not arguments
            and not keywords
            and self._creating is False
            and self._pending_creation_events == 0
            and self._pending_native_identity is None
            and self.child_creations < self.expected_child_creations
            and sys.gettrace() is None
            and sys.getprofile() is None
        ):
            self.deny("unscoped-or-reentrant-authenticated-provider-create")
        _, before = BASE.RuntimePolicy.live_interpreter_provider(self)
        if not self._initial_live_ids.issubset(before):
            self.deny("changed-preexisting-public-interpreter-live-set")
        self._creating = True
        try:
            result = self._v5_guarded_create()
        finally:
            self._creating = False
        _, after = BASE.RuntimePolicy.live_interpreter_provider(self)
        actual = getattr(result, "interpreter", None)
        identity = getattr(actual, "id", None)
        if not self._creation_evidence(
            before,
            after,
            identity,
            actual,
            result,
            provider.__dict__["Interpreter"],
        ):
            self._pending_native_identity = None
            self.deny("missing-or-fabricated-authenticated-native-child-creation")
        assert isinstance(identity, int)
        self._pending_native_identity = None
        self._verified_creation_ids.add(identity)
        self.child_creations += 1
        return result

    def end_subinterpreters(self) -> None:
        self._deny_if_wrong_thread()
        provider = self._provider
        try:
            if not (
                type(provider) is types.ModuleType
                and self._native_boundaries_intact()
                and self._creating is False
                and self._pending_creation_events == 0
                and self._creation_events == 0
                and self._pending_native_identity is None
                and self._native_create_calls == 11
                and self._native_exec_calls == 416
                and self._native_destroy_calls == 11
                and len(self._verified_creation_ids) == 11
                and self._destroyed_creation_ids == self._verified_creation_ids
                and not self._active_execution_ids
                and provider.__dict__.get("create")
                in (self._original_provider_create, self._guarded_create_wrapper)
                and provider.__dict__["Interpreter"].__dict__.get("exec")
                is self._guarded_exec_wrapper
            ):
                self.deny("incomplete-or-substituted-real-native-child-boundaries")
            _, live = BASE.RuntimePolicy.live_interpreter_provider(self)
            if live != self._initial_live_ids:
                self.deny("preexisting-interpreter-live-set-not-restored")
            BASE.RuntimePolicy.end_subinterpreters(self)
        finally:
            self._restore_native_boundaries()
            self._restore_provider_boundaries(provider)
            self._suite_thread = None
            self._creating = False
            self._pending_creation_events = 0
            self._pending_native_identity = None

    def audit(self, event: str, args: tuple) -> None:
        if event in FORGED_INTERPRETER_EVENTS:
            self.deny("fabricated-or-unemitted-parent-interpreter-event:" + event)
        return BASE.RuntimePolicy.audit(self, event, args)


def strict_document(raw: bytes, label: str) -> dict:
    value = JsonReader(raw).parse()
    require(type(value) is dict, "require a complete JSON document: " + label)
    assert isinstance(value, dict)
    return value


def parse_options(arguments: list[str]) -> dict:
    modes = {"--self-test", "--verify-frozen-context", "--prove-provider"}
    allowed = {flag for _, flag in OPTION_ROLES}
    result: dict[str, object] = {}
    position = 0
    while position < len(arguments):
        name = arguments[position]
        if name in modes:
            require("mode" not in result, "reject repeated V4 operation mode")
            result["mode"] = name
            position += 1
            continue
        require(
            name in allowed
            and name not in result
            and position + 1 < len(arguments),
            "reject missing, duplicated, or unowned V2/V3/V4/V5 pin",
        )
        result[name] = sha256_pin(arguments[position + 1], name)
        position += 2
    require(
        result.get("mode") in modes and len(result) == len(OPTION_ROLES) + 1,
        "require one explicit V4 mode and all twelve independent owner pins",
    )
    return result


def predecessor_options(options: dict) -> dict:
    return {
        "mode": "--verify-frozen-context",
        "--source-sha256": options["--v3-source-sha256"],
        "--protocol-sha256": options["--v3-protocol-sha256"],
        "--contract-sha256": options["--v3-contract-sha256"],
        "--v2-source-sha256": options["--v2-source-sha256"],
        "--v2-protocol-sha256": options["--v2-protocol-sha256"],
        "--v2-contract-sha256": options["--v2-contract-sha256"],
        "--producer-source-sha256": options["--producer-source-sha256"],
        "--producer-protocol-sha256": options["--producer-protocol-sha256"],
        "--producer-contract-sha256": options["--producer-contract-sha256"],
    }


def expected_contract(
    options: dict, own_source: tuple, own_protocol: tuple
) -> dict:
    inherited = PREVIOUS.expected_contract(
        predecessor_options(options),
        V3_OWNERS["source"],
        V3_OWNERS["protocol"],
    )
    document = dict(inherited)
    document.update(
        {
            "schema": "rebar-owned-candidate-runtime-independence-v4-source-freeze",
            "version": 4,
            "status": "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE",
            "source": owner_identity(own_source),
            "protocol": owner_identity(own_protocol),
            "immutable_predecessor_v3": {
                "version": 3,
                "owners": {
                    role: owner_identity(item)
                    for role, item in V3_OWNERS.items()
                },
                "policy": "EXACT AUTHENTICATED V3 POLICY SUBCLASS",
                "prepare_family": "UNCHANGED EXACT V2 FUNCTION AND GLOBALS",
                "child_bootstrap": "UNCHANGED AUTHENTICATED V2 CHILD SOURCE",
                "known_false_positive": (
                    "PARENT PYTHON AUDIT HOOK RECEIVES NO INTERPRETER "
                    "CREATION EVENT ON PINNED CPYTHON 3.14.6"
                ),
                "source_mutated": False,
                "runtime_non_delegation": "NOT ESTABLISHED",
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
                "creation_audit_event": (
                    "NOT EMITTED TO PARENT PYTHON AUDIT HOOK"
                ),
                "creation_audit_event_names_rejected": sorted(
                    FORGED_INTERPRETER_EVENTS
                ),
                "actual_creation_audit_events": 0,
                "creation_identity": (
                    "SOURCE-AUTHENTICATED PROVIDER CALLER; GENUINE BUILTIN "
                    "RETURNED ID; INDEPENDENT NATIVE AND PUBLIC LIVE-SET DELTA"
                ),
                "native_create_boundary": (
                    "SCOPED GENUINE _interpreters.create; reqrefs=True; "
                    "EXACT PINNED PROVIDER CALLER FRAME"
                ),
                "native_exec_boundary": (
                    "SCOPED GENUINE _interpreters.exec; restrict=True; "
                    "EXACT PINNED Interpreter.exec CALLER FRAME"
                ),
                "native_destroy_boundary": (
                    "SCOPED GENUINE _interpreters.destroy; restrict=True; "
                    "EXACT PINNED Interpreter.close CALLER FRAME"
                ),
                "execution_boundary": (
                    "SOURCE-AUTHENTICATED concurrent.interpreters.Interpreter.exec"
                ),
                "first_execution": "UNCHANGED V2 CHALLENGE-BOUND CHILD GUARD",
                "positive_attestation": "REAL UNIQUE OPERATING-SYSTEM PIPE",
                "unrestricted_creation": False,
                "unrestricted_execution": False,
                "unrestricted_destruction": False,
                "preexisting_live_set_restored": "REQUIRED AT ACTUAL SUITE END",
                "actual_interpreters_created": 0,
                "actual_interpreters_destroyed": 0,
                "actual_case_interpreter_exec_calls": 0,
                "actual_bootstrap_interpreter_exec_calls": 0,
                "actual_cleanup_interpreter_exec_calls": 0,
                "actual_child_guards_installed": 0,
                "candidate_status": "NOT RUN",
            },
            "provider_proof": {
                "mode": "--prove-provider",
                "authorization": "EXPLICIT MODE AND TWELVE INDEPENDENT PINS",
                "source_gate_invokes_proof": False,
                "status": "NOT RUN",
                "creates_real_interpreters_when_explicitly_invoked": 1,
                "destroys_real_interpreters_when_explicitly_invoked": 1,
                "candidate_imports": 0,
                "candidate_native_libraries_loaded": 0,
                "private_build_roots_opened": 0,
                "compressed_archives_opened": 0,
                "holdout": "NOT OPENED",
            },
            "source_only_effects": {
                key: 0 for key in sorted(EFFECT_KEYS)
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
    )
    return document


def validate_frozen_context(options: dict) -> tuple[tuple, tuple]:
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
        "require exact clean CPython 3.14.6 -I -B -S without any candidate",
    )
    read_owner(GOAL, "immutable exact experiment objective")
    for role, item in V3_OWNERS.items():
        require(
            options["--v3-" + role + "-sha256"] == item[1],
            "require an independently supplied immutable V3 " + role + " pin",
        )
        read_owner(item, "exact immutable V3 " + role)
    for role, item in V2.items():
        require(
            options["--v2-" + role + "-sha256"] == item[1],
            "require an independently supplied immutable V2 " + role + " pin",
        )
        read_owner(item, "exact immutable V2 " + role)
    verify_child_contract(
        options["--v2-source-sha256"],
        options["--v2-protocol-sha256"],
        options["--v2-contract-sha256"],
    )
    for role, item in PRODUCER.items():
        require(
            options["--producer-" + role + "-sha256"] == item[1],
            "require an independently supplied immutable V5 " + role + " pin",
        )
        read_owner(item, "exact immutable V5 " + role)
    producer = strict_document(
        read_owner(PRODUCER["contract"], "complete immutable V5 contract"),
        "complete immutable V5 contract",
    )
    PREVIOUS.validate_frozen_producer(producer)
    previous_contract = strict_document(
        read_owner(V3_OWNERS["contract"], "complete immutable V3 contract"),
        "complete immutable V3 contract",
    )
    previous_expected = PREVIOUS.expected_contract(
        predecessor_options(options),
        V3_OWNERS["source"],
        V3_OWNERS["protocol"],
    )
    require(
        canonical(previous_contract) == canonical(previous_expected),
        "reject a substituted or falsely measured immutable V3 policy",
    )
    provider_raw = PREVIOUS.read_provider_source()
    compiled = compile(
        provider_raw, PREVIOUS.PROVIDER_PATH, "exec", dont_inherit=True
    )
    for qualname in (
        "create",
        "list_all",
        "Interpreter.exec",
        "Interpreter.close",
    ):
        PREVIOUS.source_code(compiled, qualname)
    own_source = dynamic_owner(SELF, options["--source-sha256"], "V4 source")
    own_protocol = dynamic_owner(
        PROTOCOL, options["--protocol-sha256"], "V4 protocol"
    )
    own_contract = dynamic_owner(
        CONTRACT, options["--contract-sha256"], "V4 machine contract"
    )
    read_owner(own_source, "complete source-frozen V4 implementation")
    read_owner(own_protocol, "complete source-frozen V4 protocol")
    contract = strict_document(
        read_owner(own_contract, "complete source-frozen V4 contract"),
        "complete source-frozen V4 contract",
    )
    require(
        canonical(contract)
        == canonical(expected_contract(options, own_source, own_protocol)),
        "reject any missing, extra, substituted, or falsely measured V4 policy",
    )
    return own_source, own_protocol


def v4_hostile_controls(policy: RuntimePolicy, options: dict) -> int:
    count = PREVIOUS.hostile_controls(policy, options)
    require(
        RuntimePolicy.prepare_family is BASE.RuntimePolicy.prepare_family
        and RuntimePolicy.prepare_family.__globals__ is BASE.__dict__
        and child_bootstrap_source is BASE.child_bootstrap_source
        and verify_child_contract is BASE.verify_child_contract,
        "preserve exact immutable V2 producer and child-guard identities",
    )
    native_create_names = RuntimePolicy._authenticated_native_create.__code__.co_names
    native_listing_names = RuntimePolicy._native_live_ids.__code__.co_names
    outer_create_names = RuntimePolicy._real_provider_create.__code__.co_names
    require(
        "_native_live_ids" in native_create_names
        and "live_interpreter_provider" not in native_create_names
        and "list_all" in RuntimePolicy._native_live_ids.__code__.co_consts
        and "live_interpreter_provider" not in native_listing_names
        and "live_interpreter_provider" in outer_create_names,
        "reject premature public list_all before the new owning Interpreter exists",
    )
    count += 1
    policy._suite_thread = _thread.get_ident()
    policy.interpreter_suite = "subinterpreter_v2"
    for role, operation in (
        (
            "direct-native-create",
            lambda: policy._authenticated_native_create(
                (), {"reqrefs": True}
            ),
        ),
        (
            "direct-native-exec",
            lambda: policy._authenticated_native_exec(
                (1729, "pass"), {"restrict": True}
            ),
        ),
        (
            "direct-native-destroy",
            lambda: policy._authenticated_native_destroy(
                (1729,), {"restrict": True}
            ),
        ),
    ):
        count += PREVIOUS.denied(policy, operation, role)
    policy._initial_live_ids = {0}
    policy._verified_creation_ids = set()
    policy._pending_creation_events = 0
    policy._creation_events = 0
    policy._pending_native_identity = 1729
    policy._native_create_calls = 1
    policy.child_creations = 0
    source_class = type("_V4SourceOnlyInterpreter", (), {})
    actual = source_class()
    actual.id = 1729
    result = types.SimpleNamespace(interpreter=actual, id=1729)
    require(
        policy._creation_evidence(
            {0}, {0, 1729}, 1729, actual, result, source_class
        ),
        "reject a genuine-shaped event-free creation live-set conjunction",
    )
    negatives = (
        ({0}, {0}, 1729, actual, result, source_class),
        ({0}, {0, 1729, 1730}, 1729, actual, result, source_class),
        ({0}, {0, 1729}, "1729", actual, result, source_class),
        ({0}, {0, 1729}, -1, actual, result, source_class),
        ({0}, {0, 1729}, 1729, object(), result, source_class),
        (
            {0},
            {0, 1729},
            1729,
            actual,
            types.SimpleNamespace(id=1730),
            source_class,
        ),
    )
    for evidence in negatives:
        require(
            not policy._creation_evidence(*evidence),
            "accept a fabricated source-only native creation conjunction",
        )
        count += 1
    for mutation, reset in (
        (
            lambda: setattr(policy, "_pending_native_identity", 1730),
            lambda: setattr(policy, "_pending_native_identity", 1729),
        ),
        (
            lambda: setattr(policy, "_native_create_calls", 0),
            lambda: setattr(policy, "_native_create_calls", 1),
        ),
        (
            lambda: setattr(policy, "_verified_creation_ids", {1729}),
            lambda: setattr(policy, "_verified_creation_ids", set()),
        ),
        (
            lambda: setattr(policy, "_initial_live_ids", {0, 1729}),
            lambda: setattr(policy, "_initial_live_ids", {0}),
        ),
    ):
        mutation()
        require(
            not policy._creation_evidence(
                {0}, {0, 1729}, 1729, actual, result, source_class
            ),
            "accept a replayed, stale, or unverified source-only child",
        )
        reset()
        count += 1
    frame_module = types.ModuleType("_rebar_v4_source_only_provider_frames")

    def frame_authenticated() -> bool:
        return policy._provider_caller(frame_module.provider.__code__)

    frame_module.frame_authenticated = frame_authenticated
    exec(
        compile(
            "def provider():\n"
            "    return native_wrapper()\n"
            "def native_wrapper():\n"
            "    return frame_authenticated()\n",
            "<source-only-v4-authenticated-provider-frame-depth>",
            "exec",
            dont_inherit=True,
        ),
        frame_module.__dict__,
    )
    policy._provider = frame_module
    require(
        frame_module.provider() is True,
        "reject exact provider/native-wrapper/authenticator frame depth three",
    )
    require(
        frame_authenticated() is False,
        "accept a direct caller without the authenticated provider frame",
    )
    policy._provider = None
    count += 2
    policy._pending_native_identity = None
    policy.interpreter_suite = None
    policy._suite_thread = None
    require(
        "concurrent.interpreters" not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "preserve source-only isolation without creating an interpreter",
    )
    return count


def source_run(options: dict) -> dict:
    validate_frozen_context(options)
    policy = RuntimePolicy()
    policy.install()
    rejected = v4_hostile_controls(policy, options)
    return {
        "schema": "rebar-owned-candidate-runtime-independence-v4-source-"
        + (
            "self-test"
            if options["mode"] == "--self-test"
            else "frozen-context"
        ),
        "version": 4,
        "status": "PASS",
        "source_sha256": options["--source-sha256"],
        "protocol_sha256": options["--protocol-sha256"],
        "contract_sha256": options["--contract-sha256"],
        "immutable_v3_source_sha256": V3_OWNERS["source"][1],
        "immutable_v2_source_sha256": V2["source"][1],
        "immutable_v5_producer_source_sha256": PRODUCER["source"][1],
        "pinned_public_interpreter_source_sha256": PREVIOUS.PROVIDER_SHA256,
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "separate_supplemental_case_count": 8244,
        "candidate_family_count": 6,
        "required_native_owner_field_count": 14,
        "rejected_hostile_control_count": rejected,
        "physically_blocked_controls": dict(policy.blocked),
        "creation_audit_event": "NOT EMITTED TO PARENT PYTHON AUDIT HOOK",
        "actual_creation_audit_events": 0,
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
        "provider_proof": "NOT RUN",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_matching": "NOT RUN",
        "qualified_candidate_count": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def prove_provider(options: dict) -> dict:
    """Only explicit authorization runs this one candidate-free real child."""
    validate_frozen_context(options)
    internal = __import__("_interpreters")
    require(
        type(internal) is types.ModuleType
        and getattr(getattr(internal, "__spec__", None), "origin", None)
        == "built-in",
        "require the pinned built-in interpreter provider",
    )
    original_create = getattr(internal, "create", None)
    original_destroy = getattr(internal, "destroy", None)
    require(
        type(original_create) is types.BuiltinFunctionType
        and original_create.__self__ is internal
        and type(original_destroy) is types.BuiltinFunctionType
        and original_destroy.__self__ is internal,
        "reject a substituted pinned native proof provider",
    )
    compiled = compile(
        PREVIOUS.read_provider_source(),
        PREVIOUS.PROVIDER_PATH,
        "exec",
        dont_inherit=True,
    )
    create_code = PREVIOUS.source_code(compiled, "create")
    proof_namespace = types.ModuleType(
        "_rebar_v4_explicit_pinned_builtin_provider_proof"
    )
    proof_namespace._interpreters = internal

    class ProofInterpreter:
        def __init__(self, identity: int, *, _ownsref: bool) -> None:
            require(type(identity) is int and _ownsref is True, "invalid child")
            internal.incref(identity)
            self.id = identity

        def close(self) -> None:
            original_destroy(self.id, restrict=True)

    proof_namespace.Interpreter = ProofInterpreter
    proof_namespace.create = types.FunctionType(
        create_code, proof_namespace.__dict__, "create"
    )
    events: list[str] = []

    def observe(event: str, arguments: tuple) -> None:
        if event in FORGED_INTERPRETER_EVENTS:
            events.append(event)

    sys.addaudithook(observe)
    before = {item[0] for item in internal.list_all()}
    returned: list[int] = []

    def authenticated_create(*arguments: object, **keywords: object):
        caller = sys._getframe(1)
        require(
            caller.f_code is proof_namespace.create.__code__
            and caller.f_globals is proof_namespace.__dict__
            and arguments == ()
            and keywords == {"reqrefs": True}
            and not returned,
            "reject a fabricated explicit pinned-provider proof frame",
        )
        identity = original_create(*arguments, **keywords)
        require(type(identity) is int, "reject a fabricated native child ID")
        returned.append(identity)
        return identity

    child: ProofInterpreter | None = None
    internal.create = authenticated_create
    try:
        child = proof_namespace.create()
        after = {item[0] for item in internal.list_all()}
        require(
            len(returned) == 1
            and type(child) is ProofInterpreter
            and child.id == returned[0]
            and after - before == {child.id}
            and before.issubset(after),
            "reject absent genuine pinned builtin proof live-set evidence",
        )
    finally:
        internal.create = original_create
    try:
        require(child is not None, "reject an absent explicit proof child")
        child.close()
    finally:
        child = None
    restored = {item[0] for item in internal.list_all()}
    require(
        restored == before
        and not events
        and "concurrent.interpreters" not in sys.modules
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        )
        and not any(
            str(getattr(getattr(module, "__spec__", None), "origin", ""))
            .endswith(".so")
            for module in sys.modules.values()
        ),
        "reject an unclosed, audited, delegated, or native-loaded provider proof",
    )
    return {
        "schema": "rebar-owned-candidate-runtime-independence-v4-explicit-provider-proof",
        "version": 4,
        "status": "PASS",
        "source_sha256": options["--source-sha256"],
        "protocol_sha256": options["--protocol-sha256"],
        "contract_sha256": options["--contract-sha256"],
        "actual_interpreters_created": 1,
        "actual_interpreters_destroyed": 1,
        "actual_creation_audit_events": 0,
        "authentic_builtin_call_count": 1,
        "returned_interpreter_identity": returned[0],
        "public_provider_imported": False,
        "provider_frame": (
            "EXACT PINNED PUBLIC-PROVIDER CODE; EXPLICIT FIRST-PARTY "
            "CANDIDATE-FREE PROOF NAMESPACE"
        ),
        "native_and_public_provider_suite_executed": False,
        "initial_live_set_restored": True,
        "candidate_imports": 0,
        "candidate_native_libraries_loaded": 0,
        "private_build_roots_opened": 0,
        "compressed_archives_opened": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }


def main() -> int:
    try:
        options = parse_options(sys.argv[1:])
        result = (
            prove_provider(options)
            if options["mode"] == "--prove-provider"
            else source_run(options)
        )
        sys.stdout.buffer.write(canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write(
            "authentic builtin child guard rejected: " + str(error) + "\n"
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
