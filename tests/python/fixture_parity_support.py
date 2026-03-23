from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
import pathlib
import re

import rebar
from rebar_harness.correctness import (
    FixtureCase,
    FixtureManifest,
    load_fixture_manifest,
)
from tests.conftest import duplicate_string_ids

_MISSING_GROUP_DEFAULT = object()
_MATCH_ACCESSOR_NAMES = ("group", "span", "start", "end", "getitem")
WRAPPER_PAIRS = (
    ("", ""),
    ("zz", ""),
    ("", "zz"),
    ("zz", "zz"),
)


class IndexLike:
    """Minimal ``__index__`` carrier for parity tests that coerce numeric inputs."""

    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        self.value = value

    def __index__(self) -> int:
        return self.value

    def __repr__(self) -> str:
        return f"IndexLike({self.value})"


class RecordingIndexLike:
    """Track ``__index__`` calls while optionally surfacing a caller-provided error."""

    __slots__ = ("value", "error", "calls")

    def __init__(
        self,
        value: int = 1,
        *,
        error: BaseException | None = None,
    ) -> None:
        self.value = value
        self.error = error
        self.calls = 0

    def __index__(self) -> int:
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.value


class IndexLikeBoomError(Exception):
    """Distinct ``__index__`` failure used by coercion parity tests."""


class RecordingNativeBoundary:
    def __init__(self, *, native_placeholder_messages: bool = False) -> None:
        self.calls: list[tuple[object, ...]] = []
        self._native_placeholder_messages = native_placeholder_messages

    def _dispatch(
        self,
        recorded_call: tuple[object, ...],
        handler_name: str,
        *handler_args: object,
    ) -> object:
        self.calls.append(recorded_call)
        try:
            handler = getattr(self, handler_name)
        except AttributeError as exc:
            raise AssertionError(f"unexpected {recorded_call[0]} call") from exc
        return handler(*handler_args)

    def boundary_compile(self, pattern: str | bytes, flags: int) -> tuple[str, int, bool]:
        return self._dispatch(("compile", pattern, flags), "compile_result", pattern, flags)

    def boundary_literal_match(
        self,
        pattern: str | bytes,
        flags: int,
        mode: str,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, int, int, tuple[int, int] | None]:
        return self._dispatch(
            ("match", pattern, flags, mode, string, pos, endpos),
            "literal_match_result",
            pattern,
            flags,
            mode,
            string,
            pos,
            endpos,
        )

    def boundary_literal_split(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        maxsplit: int,
    ) -> tuple[str, list[str] | list[bytes] | None]:
        return self._dispatch(
            ("split", pattern, flags, string, maxsplit),
            "literal_split_result",
            pattern,
            flags,
            string,
            maxsplit,
        )

    def boundary_literal_findall(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, list[str] | list[bytes] | None]:
        return self._dispatch(
            ("findall", pattern, flags, string, pos, endpos),
            "literal_findall_result",
            pattern,
            flags,
            string,
            pos,
            endpos,
        )

    def boundary_literal_finditer(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, int, int, list[tuple[int, int]]]:
        return self._dispatch(
            ("finditer", pattern, flags, string, pos, endpos),
            "literal_finditer_result",
            pattern,
            flags,
            string,
            pos,
            endpos,
        )

    def boundary_literal_subn(
        self,
        pattern: str | bytes,
        flags: int,
        repl: str | bytes,
        string: str | bytes,
        count: int,
    ) -> tuple[str, str | bytes | None, int]:
        return self._dispatch(
            ("subn", pattern, flags, repl, string, count),
            "literal_subn_result",
            pattern,
            flags,
            repl,
            string,
            count,
        )

    def boundary_escape(self, pattern: str | bytes) -> str | bytes:
        return self._dispatch(("escape", pattern), "escape_result", pattern)

    def scaffold_raise(self, helper_name: str) -> object:
        if self._native_placeholder_messages:
            raise NotImplementedError(f"native helper placeholder {helper_name}")
        raise NotImplementedError(rebar._placeholder_message(helper_name))

    def scaffold_pattern_raise(self, method_name: str) -> object:
        if self._native_placeholder_messages:
            raise NotImplementedError(f"native pattern placeholder {method_name}")
        raise NotImplementedError(rebar._pattern_placeholder_message(method_name))

    def scaffold_purge(self) -> None:
        self.calls.append(("purge",))


@dataclass(frozen=True)
class BoundedPatternCase:
    id: str
    pattern: str | bytes
    helper: str
    string: str | bytes
    bounds: tuple[int, int]


@dataclass(frozen=True)
class CaseIdBoundedPatternCase:
    id: str
    pattern_case_id: str
    helper: str
    string: str | bytes
    bounds: tuple[int, int]


@dataclass(frozen=True)
class PatternTraceCase:
    id: str
    pattern: str | bytes
    search_text: str | bytes
    fullmatch_text: str | bytes


@dataclass(frozen=True)
class FixtureBundle:
    manifest: FixtureManifest
    cases: tuple[FixtureCase, ...]
    expected_patterns: frozenset[str | bytes]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]
    expected_case_ids: frozenset[str] | None = None
    expected_text_models: frozenset[str] | None = None

    @property
    def expected_manifest_id(self) -> str:
        return self.manifest.manifest_id


def build_selected_fixture_bundle(
    fixture_path: pathlib.Path,
    *,
    selected_case_ids: tuple[str, ...] | None = None,
    pattern_extractor: Callable[[FixtureCase], str | bytes] | None = None,
    expected_case_ids: frozenset[str] | None = None,
    expected_text_models: frozenset[str] | None = None,
) -> FixtureBundle:
    if pattern_extractor is None:
        pattern_extractor = case_pattern

    manifest = load_fixture_manifest(fixture_path)
    loaded_cases = tuple(manifest.cases)
    duplicate_loaded_case_ids = duplicate_string_ids(
        tuple(case.case_id for case in loaded_cases)
    )
    if duplicate_loaded_case_ids:
        raise ValueError(
            f"{fixture_path.name} contains duplicate fixture case ids: "
            f"{duplicate_loaded_case_ids}"
        )

    bundle_cases = loaded_cases
    if selected_case_ids is not None:
        if not selected_case_ids:
            raise ValueError(f"{fixture_path.name} selected_case_ids must not be empty")

        duplicate_case_ids = duplicate_string_ids(selected_case_ids)
        if duplicate_case_ids:
            raise ValueError(
                f"{fixture_path.name} selected_case_ids contains duplicate ids: "
                f"{duplicate_case_ids}"
            )

        case_by_id = {case.case_id: case for case in loaded_cases}
        missing_case_ids = tuple(
            case_id for case_id in selected_case_ids if case_id not in case_by_id
        )
        if missing_case_ids:
            raise ValueError(
                f"{fixture_path.name} is missing expected fixture rows: "
                f"{missing_case_ids}"
            )

        bundle_cases = tuple(case_by_id[case_id] for case_id in selected_case_ids)
        if expected_case_ids is None:
            expected_case_ids = frozenset(selected_case_ids)
    if expected_text_models is None:
        expected_text_models = frozenset(
            case.text_model or "str" for case in bundle_cases
        )

    return FixtureBundle(
        manifest,
        bundle_cases,
        expected_patterns=frozenset(pattern_extractor(case) for case in bundle_cases),
        expected_operation_helper_counts=Counter(
            (case.operation, case.helper) for case in bundle_cases
        ),
        expected_case_ids=expected_case_ids,
        expected_text_models=expected_text_models,
    )


def case_pattern(case: FixtureCase) -> str | bytes:
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, (str, bytes))
    return pattern


def str_case_pattern(case: FixtureCase) -> str:
    pattern = case_pattern(case)
    assert isinstance(pattern, str)
    return pattern


def fixture_cases_for_operation(
    bundles: Iterable[FixtureBundle],
    operation: str,
) -> tuple[FixtureCase, ...]:
    return tuple(
        case
        for bundle in bundles
        for case in bundle.cases
        if case.operation == operation
    )


@dataclass(frozen=True)
class SupplementalCase:
    id: str
    pattern: bytes
    search_matches: tuple[bytes, ...] = ()
    search_misses: tuple[bytes, ...] = ()
    fullmatch_matches: tuple[bytes, ...] = ()
    fullmatch_misses: tuple[bytes, ...] = ()
    unsupported_backends: tuple[str, ...] = ()
    unsupported_backend_reason: str | None = None


@dataclass(frozen=True)
class SupplementalMissCase:
    id: str
    target: str
    pattern: str
    helper: str
    text: str


OPEN_ENDED_ALTERNATION_BYTES_CASES = (
    SupplementalCase(
        id="open-ended-grouped-alternation-numbered-bytes",
        pattern=rb"a(bc|de){1,}d",
        search_matches=(b"zzabcdzz", b"zzadedzz"),
        fullmatch_matches=(b"abcbcd", b"abcded", b"abcbcded"),
        fullmatch_misses=(b"ad", b"abed"),
    ),
    SupplementalCase(
        id="open-ended-grouped-alternation-named-bytes",
        pattern=rb"a(?P<word>bc|de){1,}d",
        search_matches=(b"zzabcdzz", b"zzadedzz"),
        fullmatch_matches=(b"abcded", b"abcbcded", b"adededed"),
        fullmatch_misses=(b"ad", b"abed"),
    ),
)
NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES = (
    SupplementalCase(
        id="nested-open-ended-grouped-alternation-numbered-bytes",
        pattern=rb"a((bc|de){1,})d",
        search_matches=(b"zzabcdzz", b"zzadedzz"),
        fullmatch_matches=(b"abcbcded", b"adededed"),
        fullmatch_misses=(b"ae", b"abcbcdede"),
    ),
    SupplementalCase(
        id="nested-open-ended-grouped-alternation-named-bytes",
        pattern=rb"a(?P<outer>(bc|de){1,})d",
        search_matches=(b"zzabcdzz", b"zzadedzz"),
        fullmatch_matches=(b"abcbcded", b"adededed"),
        fullmatch_misses=(b"ae", b"abcbcdede"),
    ),
)
OPEN_ENDED_CONDITIONAL_BYTES_CASES = (
    SupplementalCase(
        id="open-ended-grouped-conditional-numbered-bytes",
        pattern=rb"a((bc|de){1,})?(?(1)d|e)",
        search_matches=(b"zzaezz", b"zzabcdzz", b"zzabcbcdzz", b"zzadedzz"),
        fullmatch_matches=(b"abcded", b"abcbcded"),
        fullmatch_misses=(b"abcde",),
    ),
    SupplementalCase(
        id="open-ended-grouped-conditional-named-bytes",
        pattern=rb"a(?P<outer>(bc|de){1,})?(?(outer)d|e)",
        search_matches=(b"zzaezz", b"zzadedzz", b"zzadedededzz"),
        fullmatch_matches=(b"abcbcded",),
        fullmatch_misses=(b"ad",),
    ),
)
OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES = (
    SupplementalCase(
        id="open-ended-grouped-backtracking-heavy-numbered-bytes",
        pattern=rb"a((bc|b)c){1,}d",
        fullmatch_matches=(b"abccd", b"abcbcd", b"abcbccd"),
        fullmatch_misses=(b"abcccd",),
        search_matches=(b"zzabcdzz",),
    ),
    SupplementalCase(
        id="open-ended-grouped-backtracking-heavy-named-bytes",
        pattern=rb"a(?P<word>(bc|b)c){1,}d",
        search_matches=(b"zzabccdzz", b"zzabccbcdzz", b"zzabcbccbcdzz"),
        search_misses=(b"zzabccbdzz",),
        fullmatch_matches=(b"abcbcbcbcd",),
    ),
)
BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES = (
    SupplementalCase(
        id="broader-range-open-ended-grouped-alternation-numbered-bytes",
        pattern=rb"a(bc|de){2,}d",
        search_matches=(b"zzabcbcdzz", b"zzadededzz"),
        fullmatch_matches=(b"abcded", b"abcbcded", b"adededed"),
        fullmatch_misses=(b"abcd", b"ad"),
    ),
    SupplementalCase(
        id="broader-range-open-ended-grouped-alternation-named-bytes",
        pattern=rb"a(?P<word>bc|de){2,}d",
        search_matches=(b"zzabcbcdzz", b"zzadededzz"),
        fullmatch_matches=(b"abcded", b"abcbcded", b"adededed"),
        fullmatch_misses=(b"abcd", b"ad"),
    ),
)
BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES = (
    SupplementalCase(
        id="broader-range-open-ended-grouped-conditional-numbered-bytes",
        pattern=rb"a((bc|de){2,})?(?(1)d|e)",
        search_matches=(b"zzaezz", b"zzabcbcdzz", b"zzadededzz"),
        fullmatch_matches=(b"abcded", b"abcbcded"),
        fullmatch_misses=(b"abcdede", b"abcd"),
    ),
    SupplementalCase(
        id="broader-range-open-ended-grouped-conditional-named-bytes",
        pattern=rb"a(?P<outer>(bc|de){2,})?(?(outer)d|e)",
        search_matches=(b"zzaezz", b"zzadededzz", b"zzadedededzz"),
        fullmatch_matches=(b"abcbcded",),
        fullmatch_misses=(b"ad",),
    ),
)
BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES = (
    SupplementalCase(
        id="broader-range-open-ended-grouped-backtracking-heavy-numbered-bytes",
        pattern=rb"a((bc|b)c){2,}d",
        search_matches=(b"zzabcbcdzz", b"zzabcbccdzz"),
        fullmatch_matches=(b"abccbcd", b"abcbcbcbcd"),
        fullmatch_misses=(b"abcd", b"abccbd"),
    ),
    SupplementalCase(
        id="broader-range-open-ended-grouped-backtracking-heavy-named-bytes",
        pattern=rb"a(?P<word>(bc|b)c){2,}d",
        search_matches=(b"zzabcbccdzz", b"zzabccbcdzz", b"zzabcbcbcbcdzz"),
        search_misses=(b"zzabccbdzz",),
        fullmatch_matches=(b"abcbccd", b"abcbcbcbcd"),
        fullmatch_misses=(b"abcd",),
    ),
)


def partition_direct_bytes_follow_on_case_buckets(
    bundles: Iterable[FixtureBundle],
    direct_bytes_follow_on_bundles: Iterable[FixtureBundle],
) -> tuple[tuple[FixtureCase, ...], tuple[FixtureCase, ...], tuple[FixtureCase, ...]]:
    loaded_bundles = tuple(bundles)
    direct_bytes_follow_on_manifest_ids = frozenset(
        bundle.manifest.manifest_id for bundle in direct_bytes_follow_on_bundles
    )

    def _partition_operation(operation: str) -> tuple[FixtureCase, ...]:
        return tuple(
            case
            for case in fixture_cases_for_operation(loaded_bundles, operation)
            if case.text_model != "bytes"
            or case.manifest_id not in direct_bytes_follow_on_manifest_ids
        )

    return (
        _partition_operation("compile"),
        _partition_operation("module_call"),
        _partition_operation("pattern_call"),
    )


def direct_test_case_id_buckets_for_follow_on_bundles(
    *,
    compile_cases: Iterable[FixtureCase],
    module_cases: Iterable[FixtureCase],
    pattern_cases: Iterable[FixtureCase],
    module_bucket_label: str,
    pattern_bucket_label: str,
    follow_on_buckets: Iterable[tuple[str, FixtureBundle]],
) -> dict[str, frozenset[str]]:
    follow_on_bucket_entries = tuple(
        (
            bucket_label,
            frozenset(case.case_id for case in bundle.cases if case.text_model == "bytes"),
        )
        for bucket_label, bundle in follow_on_buckets
    )
    bucket_entries = (
        ("shared-compile", frozenset(case.case_id for case in compile_cases)),
        (module_bucket_label, frozenset(case.case_id for case in module_cases)),
        (pattern_bucket_label, frozenset(case.case_id for case in pattern_cases)),
        *follow_on_bucket_entries,
    )
    duplicate_bucket_labels = duplicate_string_ids(
        bucket_label for bucket_label, _ in bucket_entries
    )
    if duplicate_bucket_labels:
        raise AssertionError(
            "direct-test case-id buckets contain duplicate labels: "
            f"{duplicate_bucket_labels}"
        )
    return dict(bucket_entries)


def published_fixture_bundles_by_manifest_id(
    bundles: Iterable[FixtureBundle],
) -> dict[str, FixtureBundle]:
    indexed_bundles: dict[str, FixtureBundle] = {}
    for bundle in bundles:
        manifest_id = bundle.manifest.manifest_id
        if manifest_id in indexed_bundles:
            raise ValueError(
                f"published fixture bundles contain duplicate manifest_id {manifest_id!r}"
            )
        indexed_bundles[manifest_id] = bundle
    return indexed_bundles


def assert_fixture_bundle_contract(
    bundle: FixtureBundle,
    *,
    pattern_extractor: Callable[[FixtureCase], str | bytes],
    expected_fixture_path: pathlib.Path | None = None,
    expected_ordered_case_ids: tuple[str, ...] | None = None,
) -> None:
    if expected_fixture_path is not None:
        assert bundle.manifest.path == expected_fixture_path
    assert bundle.manifest.manifest_id == bundle.expected_manifest_id
    duplicate_case_ids = duplicate_string_ids(tuple(case.case_id for case in bundle.cases))
    assert not duplicate_case_ids, (
        f"{bundle.expected_manifest_id} bundle contains duplicate case ids: "
        f"{duplicate_case_ids}"
    )
    if bundle.expected_case_ids is None:
        assert len(bundle.cases) == sum(bundle.expected_operation_helper_counts.values())
    else:
        assert len(bundle.cases) == len(bundle.expected_case_ids)
        assert {case.case_id for case in bundle.cases} == bundle.expected_case_ids
    if expected_ordered_case_ids is not None:
        assert tuple(case.case_id for case in bundle.cases) == expected_ordered_case_ids
    assert {pattern_extractor(case) for case in bundle.cases} == bundle.expected_patterns
    if bundle.expected_text_models is not None:
        assert {case.text_model for case in bundle.cases} == bundle.expected_text_models
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        bundle.expected_operation_helper_counts
    )


def assert_mixed_text_model_case_pairs(
    bundle: FixtureBundle,
) -> tuple[tuple[FixtureCase, ...], tuple[FixtureCase, ...]]:
    manifest_id = bundle.expected_manifest_id
    actual_text_models = {case.text_model for case in bundle.cases}
    if actual_text_models != {"bytes", "str"}:
        raise AssertionError(
            f"{manifest_id} mixed-text-model contract requires str/bytes rows, got "
            f"{tuple(sorted(actual_text_models))}"
        )

    str_cases = tuple(case for case in bundle.cases if case.text_model == "str")
    bytes_cases = tuple(case for case in bundle.cases if case.text_model == "bytes")
    if len(str_cases) != len(bytes_cases):
        raise AssertionError(
            f"{manifest_id} mixed-text-model rows drifted; "
            f"str row count {len(str_cases)} != bytes row count {len(bytes_cases)}"
        )

    expected_bytes_case_ids = tuple(
        f"{case.case_id.removesuffix('-str')}-bytes" for case in str_cases
    )
    actual_bytes_case_ids = tuple(case.case_id for case in bytes_cases)
    if actual_bytes_case_ids != expected_bytes_case_ids:
        raise AssertionError(
            f"{manifest_id} mixed-text-model case id pairing drifted; "
            f"expected bytes case ids {expected_bytes_case_ids}, "
            f"got {actual_bytes_case_ids}"
        )

    def _normalize_mixed_text_payload(value: object) -> object:
        if isinstance(value, bytes):
            return value.decode("latin-1")
        if isinstance(value, list):
            return [_normalize_mixed_text_payload(item) for item in value]
        if isinstance(value, tuple):
            return tuple(_normalize_mixed_text_payload(item) for item in value)
        if isinstance(value, dict):
            if (
                value.get("type") == "bytes"
                and isinstance(value.get("encoding"), str)
                and isinstance(value.get("value"), str)
            ):
                return value["value"]
            return {
                key: _normalize_mixed_text_payload(item)
                for key, item in value.items()
            }
        return value

    drift_messages: list[str] = []
    for str_case, bytes_case in zip(str_cases, bytes_cases):
        if str_case.operation != bytes_case.operation:
            drift_messages.append(
                f"{str_case.case_id}/{bytes_case.case_id} operation drifted: "
                f"{str_case.operation!r} != {bytes_case.operation!r}"
            )
        if str_case.helper != bytes_case.helper:
            drift_messages.append(
                f"{str_case.case_id}/{bytes_case.case_id} helper drifted: "
                f"{str_case.helper!r} != {bytes_case.helper!r}"
            )
        if str_case.family != bytes_case.family:
            drift_messages.append(
                f"{str_case.case_id}/{bytes_case.case_id} family drifted: "
                f"{str_case.family!r} != {bytes_case.family!r}"
            )
        if str_case.pattern != bytes_case.pattern:
            drift_messages.append(
                f"{str_case.case_id}/{bytes_case.case_id} pattern drifted: "
                f"{str_case.pattern!r} != {bytes_case.pattern!r}"
            )
        if str_case.flags != bytes_case.flags:
            drift_messages.append(
                f"{str_case.case_id}/{bytes_case.case_id} flags drifted: "
                f"{str_case.flags!r} != {bytes_case.flags!r}"
            )
        if str_case.pattern_encoding != bytes_case.pattern_encoding:
            drift_messages.append(
                f"{str_case.case_id}/{bytes_case.case_id} pattern encoding drifted: "
                f"{str_case.pattern_encoding!r} != {bytes_case.pattern_encoding!r}"
            )
        if str_case.use_compiled_pattern != bytes_case.use_compiled_pattern:
            drift_messages.append(
                f"{str_case.case_id}/{bytes_case.case_id} compiled-pattern routing drifted"
            )
        if str_case.include_pattern_arg != bytes_case.include_pattern_arg:
            drift_messages.append(
                f"{str_case.case_id}/{bytes_case.case_id} include-pattern routing drifted"
            )
        if _normalize_mixed_text_payload(str_case.source_args) != _normalize_mixed_text_payload(
            bytes_case.source_args
        ):
            drift_messages.append(
                f"{str_case.case_id}/{bytes_case.case_id} source args drifted: "
                f"{str_case.source_args!r} != {bytes_case.source_args!r}"
            )
        if _normalize_mixed_text_payload(str_case.args) != _normalize_mixed_text_payload(
            bytes_case.args
        ):
            drift_messages.append(
                f"{str_case.case_id}/{bytes_case.case_id} args drifted: "
                f"{str_case.args!r} != {bytes_case.args!r}"
            )
        if str_case.kwargs != bytes_case.kwargs:
            drift_messages.append(
                f"{str_case.case_id}/{bytes_case.case_id} kwargs drifted: "
                f"{str_case.kwargs!r} != {bytes_case.kwargs!r}"
            )
        if str_case.source_kwargs != bytes_case.source_kwargs:
            drift_messages.append(
                f"{str_case.case_id}/{bytes_case.case_id} source kwargs drifted: "
                f"{str_case.source_kwargs!r} != {bytes_case.source_kwargs!r}"
            )

        str_categories = tuple(
            category for category in str_case.categories if category != "str"
        )
        bytes_categories = tuple(
            category for category in bytes_case.categories if category != "bytes"
        )
        if str_categories != bytes_categories:
            drift_messages.append(
                f"{str_case.case_id}/{bytes_case.case_id} categories drifted: "
                f"{str_categories!r} != {bytes_categories!r}"
            )

    if drift_messages:
        raise AssertionError(
            f"{manifest_id} mixed-text-model structural drifted; "
            + "; ".join(drift_messages)
        )

    return str_cases, bytes_cases


def assert_direct_bytes_follow_on_bundle_routing(
    bundle: FixtureBundle,
    *,
    compile_cases: Iterable[FixtureCase],
    module_cases: Iterable[FixtureCase],
    pattern_cases: Iterable[FixtureCase],
) -> tuple[tuple[FixtureCase, ...], tuple[FixtureCase, ...]]:
    manifest_id = bundle.manifest.manifest_id
    bundle_str_cases = tuple(case for case in bundle.cases if case.text_model == "str")
    bundle_bytes_cases = tuple(case for case in bundle.cases if case.text_model == "bytes")

    if not bundle_str_cases or not bundle_bytes_cases:
        raise AssertionError(
            f"{manifest_id} direct bytes follow-on routing requires both str and bytes rows"
        )

    bucket_inputs = (
        ("compile", tuple(compile_cases)),
        ("module_call", tuple(module_cases)),
        ("pattern_call", tuple(pattern_cases)),
    )
    drift_messages: list[str] = []

    for operation, bucket_cases in bucket_inputs:
        bucket_bytes_case_ids = frozenset(
            case.case_id
            for case in bucket_cases
            if case.manifest_id == manifest_id
            and case.text_model == "bytes"
            and case.operation == operation
        )
        if bucket_bytes_case_ids:
            drift_messages.append(
                f"{operation} bucket unexpectedly includes bytes case ids "
                f"{tuple(sorted(bucket_bytes_case_ids))}"
            )

        expected_str_case_ids = frozenset(
            case.case_id for case in bundle_str_cases if case.operation == operation
        )
        bucket_str_case_ids = frozenset(
            case.case_id
            for case in bucket_cases
            if case.manifest_id == manifest_id
            and case.text_model == "str"
            and case.operation == operation
        )
        missing_str_case_ids = tuple(sorted(expected_str_case_ids - bucket_str_case_ids))
        unexpected_str_case_ids = tuple(sorted(bucket_str_case_ids - expected_str_case_ids))
        if missing_str_case_ids or unexpected_str_case_ids:
            drift_messages.append(
                f"{operation} bucket str case ids drifted; "
                f"missing case ids: {missing_str_case_ids}; "
                f"unexpected case ids: {unexpected_str_case_ids}"
            )

    if drift_messages:
        raise AssertionError(
            f"{manifest_id} direct bytes follow-on routing drifted; "
            + "; ".join(drift_messages)
        )

    return bundle_str_cases, bundle_bytes_cases


def published_bytes_texts_by_pattern(
    bundle_bytes_cases: Iterable[FixtureCase],
) -> tuple[dict[bytes, frozenset[bytes]], dict[bytes, frozenset[bytes]]]:
    published_module_texts_by_pattern: dict[bytes, set[bytes]] = {}
    published_fullmatch_texts_by_pattern: dict[bytes, set[bytes]] = {}

    for case in bundle_bytes_cases:
        pattern = case_pattern(case)
        assert isinstance(pattern, bytes)
        if case.operation == "compile":
            continue
        if case.operation == "module_call":
            if case.helper != "search":
                raise AssertionError(
                    "published bytes texts expect module search rows, got "
                    f"{case.helper!r} for {pattern!r}"
                )
            text = case.args[0] if case.use_compiled_pattern else case.args[1]
            assert isinstance(text, bytes)
            published_module_texts_by_pattern.setdefault(pattern, set()).add(text)
            continue
        if case.operation == "pattern_call":
            if case.helper != "fullmatch":
                raise AssertionError(
                    "published bytes texts expect pattern fullmatch rows, got "
                    f"{case.helper!r} for {pattern!r}"
                )
            text = case.args[0]
            assert isinstance(text, bytes)
            published_fullmatch_texts_by_pattern.setdefault(pattern, set()).add(text)
            continue
        raise AssertionError(
            "published bytes texts encountered unsupported operation "
            f"{case.operation!r} for {pattern!r}"
        )

    return (
        {
            pattern: frozenset(texts)
            for pattern, texts in published_module_texts_by_pattern.items()
        },
        {
            pattern: frozenset(texts)
            for pattern, texts in published_fullmatch_texts_by_pattern.items()
        },
    )


def assert_fixture_bundle_tracks_published_case_frontier(
    bundle: FixtureBundle,
    *,
    selected_case_ids: Iterable[str],
    expected_uncovered_case_ids: Iterable[str] = (),
) -> None:
    ordered_selected_case_ids = tuple(selected_case_ids)
    ordered_expected_uncovered_case_ids = tuple(expected_uncovered_case_ids)
    if not ordered_selected_case_ids:
        raise AssertionError(
            f"{bundle.expected_manifest_id} selected_case_ids must not be empty"
        )

    duplicate_selected_case_ids = duplicate_string_ids(ordered_selected_case_ids)
    if duplicate_selected_case_ids:
        raise AssertionError(
            f"{bundle.expected_manifest_id} selected_case_ids contain duplicate ids: "
            f"{duplicate_selected_case_ids}"
        )

    duplicate_uncovered_case_ids = duplicate_string_ids(
        ordered_expected_uncovered_case_ids
    )
    if duplicate_uncovered_case_ids:
        raise AssertionError(
            f"{bundle.expected_manifest_id} expected_uncovered_case_ids contain "
            f"duplicate ids: {duplicate_uncovered_case_ids}"
        )

    selected_case_id_set = frozenset(ordered_selected_case_ids)

    overlapping_case_ids = tuple(
        case_id
        for case_id in ordered_expected_uncovered_case_ids
        if case_id in selected_case_id_set
    )
    if overlapping_case_ids:
        raise AssertionError(
            f"{bundle.expected_manifest_id} selected and uncovered case ids overlap: "
            f"{overlapping_case_ids}"
        )

    published_case_ids = tuple(case.case_id for case in bundle.manifest.cases)
    published_case_id_set = frozenset(published_case_ids)
    expected_case_id_set = selected_case_id_set | frozenset(
        ordered_expected_uncovered_case_ids
    )
    missing_case_ids = tuple(
        case_id
        for case_id in (*ordered_selected_case_ids, *ordered_expected_uncovered_case_ids)
        if case_id not in published_case_id_set
    )
    unexpected_case_ids = tuple(
        case_id for case_id in published_case_ids if case_id not in expected_case_id_set
    )
    if missing_case_ids or unexpected_case_ids:
        raise AssertionError(
            f"{bundle.expected_manifest_id} published frontier drifted; "
            f"missing published case ids: {missing_case_ids}; "
            f"unexpected published case ids: {unexpected_case_ids}"
        )

    ordered_uncovered_case_ids = tuple(
        case_id for case_id in published_case_ids if case_id not in selected_case_id_set
    )
    if ordered_uncovered_case_ids != ordered_expected_uncovered_case_ids:
        raise AssertionError(
            f"{bundle.expected_manifest_id} uncovered published case ids changed; "
            f"expected {ordered_expected_uncovered_case_ids}, "
            f"got {ordered_uncovered_case_ids}"
        )


def assert_direct_test_case_id_buckets_cover_selected_frontier(
    direct_test_case_id_buckets: Mapping[str, frozenset[str]] | Iterable[frozenset[str]],
    *,
    selected_case_ids: Iterable[str],
    coverage_label: str = "direct-test case-id buckets",
) -> None:
    ordered_selected_case_ids = tuple(selected_case_ids)
    if not ordered_selected_case_ids:
        raise AssertionError(
            f"{coverage_label} selected_case_ids must not be empty"
        )
    duplicate_selected_case_ids = duplicate_string_ids(ordered_selected_case_ids)
    if duplicate_selected_case_ids:
        raise AssertionError(
            f"{coverage_label} selected_case_ids contain duplicate ids: "
            f"{duplicate_selected_case_ids}"
        )

    selected_case_id_set = frozenset(ordered_selected_case_ids)

    if isinstance(direct_test_case_id_buckets, Mapping):
        bucket_entries = tuple(
            (str(bucket_label), frozenset(bucket_case_ids))
            for bucket_label, bucket_case_ids in direct_test_case_id_buckets.items()
        )
    else:
        bucket_entries = tuple(
            (f"bucket[{index}]", frozenset(bucket_case_ids))
            for index, bucket_case_ids in enumerate(direct_test_case_id_buckets)
        )

    bucket_labels_by_case_id: dict[str, list[str]] = {}
    for bucket_label, bucket_case_ids in bucket_entries:
        for case_id in bucket_case_ids:
            bucket_labels_by_case_id.setdefault(case_id, []).append(bucket_label)

    duplicate_case_ids = tuple(
        (case_id, tuple(bucket_labels_by_case_id[case_id]))
        for case_id in sorted(bucket_labels_by_case_id)
        if len(bucket_labels_by_case_id[case_id]) > 1
    )
    bucket_case_ids = frozenset(bucket_labels_by_case_id)
    missing_case_ids = tuple(
        case_id
        for case_id in ordered_selected_case_ids
        if case_id not in bucket_case_ids
    )
    unexpected_case_ids = tuple(
        case_id for case_id in sorted(bucket_case_ids) if case_id not in selected_case_id_set
    )
    if duplicate_case_ids or missing_case_ids or unexpected_case_ids:
        message_parts: list[str] = []
        if duplicate_case_ids:
            message_parts.append(f"duplicate case ids: {duplicate_case_ids}")
        if missing_case_ids or unexpected_case_ids:
            message_parts.append(f"missing case ids: {missing_case_ids}")
            message_parts.append(f"unexpected case ids: {unexpected_case_ids}")
        raise AssertionError(
            f"{coverage_label} drifted; " + "; ".join(message_parts)
        )


def case_replacement_argument(case: FixtureCase) -> object:
    if case.operation == "module_call":
        replacement_index = 0 if case.use_compiled_pattern else 1
        return case.args[replacement_index]
    if case.operation == "pattern_call":
        return case.args[0]
    raise AssertionError(f"unsupported case operation {case.operation!r}")


def case_text_argument(case: FixtureCase) -> str | bytes:
    if case.operation == "module_call":
        text_index = 1 if case.use_compiled_pattern else 2
        text = case.args[text_index]
    elif case.operation == "pattern_call":
        text = case.args[1]
    else:
        raise AssertionError(f"unsupported case operation {case.operation!r}")
    assert isinstance(text, (str, bytes))
    return text


def invoke_bounded_pattern_case(compiled_pattern: object, case: object) -> object:
    return getattr(compiled_pattern, getattr(case, "helper"))(
        getattr(case, "string"),
        *getattr(case, "bounds"),
    )


def compile_with_cpython_parity(
    backend_name: str,
    backend: object,
    pattern: str | bytes,
    flags: int = 0,
    *,
    check_cache_identity: bool = True,
) -> tuple[object, re.Pattern[str] | re.Pattern[bytes]]:
    observed = backend.compile(pattern, flags)
    expected = re.compile(pattern, flags)

    if check_cache_identity:
        assert observed is backend.compile(pattern, flags)
    assert_pattern_parity(backend_name, observed, expected)
    return observed, expected


def workflow_result_with_cpython_parity(
    backend_name: str,
    backend: object,
    case: FixtureCase,
) -> tuple[object, re.Match[str] | re.Match[bytes] | None]:
    assert case.helper is not None

    if case.operation == "module_call":
        if case.use_compiled_pattern:
            observed_pattern, expected_pattern = compile_with_cpython_parity(
                backend_name,
                backend,
                case_pattern(case),
                case.flags or 0,
            )
            observed = getattr(backend, case.helper)(
                *case.module_call_args(observed_pattern),
                **case.kwargs,
            )
            expected = getattr(re, case.helper)(
                *case.module_call_args(expected_pattern),
                **case.kwargs,
            )
            return observed, expected

        observed = getattr(backend, case.helper)(*case.module_call_args(), **case.kwargs)
        expected = getattr(re, case.helper)(*case.module_call_args(), **case.kwargs)
        return observed, expected

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)
    return observed, expected


def assert_pattern_parity(
    backend_name: str,
    observed: object,
    expected: re.Pattern[str] | re.Pattern[bytes],
) -> None:
    if backend_name == "rebar":
        assert type(observed) is rebar.Pattern
    else:
        assert type(observed) is type(expected)

    assert observed.pattern == expected.pattern
    assert observed.flags == expected.flags
    assert observed.groups == expected.groups
    assert observed.groupindex == expected.groupindex


def assert_match_parity(
    backend_name: str,
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
    *,
    check_regs: bool = False,
) -> None:
    if backend_name == "rebar":
        assert type(observed) is rebar.Match
    else:
        assert type(observed) is type(expected)

    group_indexes = tuple(range(expected.re.groups + 1))

    assert observed.group(0) == expected.group(0)
    assert observed.group(*group_indexes) == expected.group(*group_indexes)
    for group_index in range(1, expected.re.groups + 1):
        assert observed.group(group_index) == expected.group(group_index)
        assert observed.span(group_index) == expected.span(group_index)
        assert observed.start(group_index) == expected.start(group_index)
        assert observed.end(group_index) == expected.end(group_index)

    assert observed.groups() == expected.groups()
    assert observed.groups(_MISSING_GROUP_DEFAULT) == expected.groups(
        _MISSING_GROUP_DEFAULT
    )
    assert observed.groupdict() == expected.groupdict()
    assert observed.groupdict(_MISSING_GROUP_DEFAULT) == expected.groupdict(
        _MISSING_GROUP_DEFAULT
    )
    assert observed.string == expected.string
    assert observed.pos == expected.pos
    assert observed.endpos == expected.endpos
    assert observed.span() == expected.span()
    assert observed.start() == expected.start()
    assert observed.end() == expected.end()
    assert observed.lastindex == expected.lastindex
    assert observed.lastgroup == expected.lastgroup
    if check_regs:
        assert hasattr(observed, "regs") == hasattr(expected, "regs")
        if hasattr(expected, "regs"):
            assert tuple(observed.regs) == tuple(expected.regs)
    assert_pattern_parity(backend_name, observed.re, expected.re)

    for group_name in expected.re.groupindex:
        assert observed.group(group_name) == expected.group(group_name)
        assert observed.span(group_name) == expected.span(group_name)
        assert observed.start(group_name) == expected.start(group_name)
        assert observed.end(group_name) == expected.end(group_name)


def assert_match_result_parity(
    backend_name: str,
    observed: object,
    expected: re.Match[str] | re.Match[bytes] | None,
    *,
    check_regs: bool = False,
) -> None:
    if expected is None:
        assert observed is None
        return

    assert observed is not None
    assert_match_parity(
        backend_name,
        observed,
        expected,
        check_regs=check_regs,
    )


def assert_finditer_parity(
    backend_name: str,
    observed_iter: object,
    expected_iter: object,
    *,
    check_regs: bool = False,
    match_callback: Callable[[object, re.Match[str] | re.Match[bytes]], None]
    | None = None,
) -> None:
    assert iter(observed_iter) is observed_iter, (
        f"{backend_name} finditer result must be its own iterator"
    )
    assert iter(expected_iter) is expected_iter, (
        "CPython finditer result must be its own iterator"
    )

    sentinel = object()
    while True:
        observed = next(observed_iter, sentinel)
        expected = next(expected_iter, sentinel)

        assert (observed is sentinel) == (expected is sentinel), (
            f"{backend_name} finditer yielded a different number of matches than CPython"
        )
        if expected is sentinel:
            break

        assert_match_result_parity(
            backend_name,
            observed,
            expected,
            check_regs=check_regs,
        )
        if match_callback is not None:
            match_callback(observed, expected)

    assert next(observed_iter, None) is None
    assert next(expected_iter, None) is None


def assert_value_parity(
    observed: object,
    expected: object,
) -> None:
    assert type(observed) is type(expected)

    if isinstance(expected, Mapping):
        observed_items = list(observed.items())
        for expected_key, expected_value in expected.items():
            for index, (observed_key, observed_value) in enumerate(observed_items):
                if type(observed_key) is not type(expected_key):
                    continue
                if observed_key != expected_key:
                    continue
                break
            else:
                raise AssertionError(
                    f"missing mapping key parity for {expected_key!r}"
                )

            observed_items.pop(index)
            assert_value_parity(observed_key, expected_key)
            assert_value_parity(observed_value, expected_value)

        if observed_items:
            raise AssertionError(
                "unexpected mapping key parity for "
                f"{tuple(observed_key for observed_key, _ in observed_items)!r}"
            )
        return

    if isinstance(expected, (list, tuple)):
        assert len(observed) == len(expected)
        for observed_item, expected_item in zip(observed, expected):
            assert_value_parity(observed_item, expected_item)
        return

    assert observed == expected


def assert_match_convenience_api_parity(
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
) -> None:
    group_names = tuple(expected.re.groupindex)
    templates: list[str] = [r"<\g<0>>"]

    for group_index in range(expected.re.groups + 1):
        assert observed[group_index] == expected[group_index]

    for group_name in group_names:
        assert observed[group_name] == expected[group_name]

    if expected.re.groups >= 1:
        templates.append(
            "<"
            + "|".join(
                f"\\{group_index}" for group_index in range(1, expected.re.groups + 1)
            )
            + ">"
        )
        templates.append(
            "<"
            + "|".join(
                f"\\g<{group_index}>" for group_index in range(expected.re.groups + 1)
            )
            + ">"
        )
    if len(group_names) >= 2:
        templates.append(
            "<" + "|".join(fr"\g<{group_name}>" for group_name in group_names) + ">"
        )
    templates.extend(fr"<\g<{group_name}>>" for group_name in group_names)

    expanded_templates: tuple[str | bytes, ...]
    if isinstance(expected.re.pattern, bytes):
        expanded_templates = tuple(template.encode("ascii") for template in templates)
    else:
        expanded_templates = tuple(templates)

    for template in expanded_templates:
        assert observed.expand(template) == expected.expand(template)


def assert_valid_match_group_access_parity(
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
) -> None:
    def access(match: object, accessor_name: str, reference: object) -> object:
        if accessor_name == "getitem":
            return match[reference]
        return getattr(match, accessor_name)(reference)

    references: list[object] = list(range(expected.re.groups + 1))
    references.append(False)
    if expected.re.groups >= 1:
        references.append(True)
    references.extend(expected.re.groupindex)

    for reference in tuple(references):
        for accessor_name in _MATCH_ACCESSOR_NAMES:
            assert access(observed, accessor_name, reference) == access(
                expected,
                accessor_name,
                reference,
            )


def assert_invalid_match_group_access_parity(
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
) -> None:
    def capture_error(
        match: object,
        accessor_name: str,
        reference: object,
    ) -> BaseException:
        try:
            if accessor_name == "getitem":
                match[reference]
            else:
                getattr(match, accessor_name)(reference)
        except BaseException as error:  # noqa: BLE001 - parity helper compares exception details.
            return error
        raise AssertionError(
            f"expected {accessor_name}({reference!r}) to raise for {match.re.pattern!r}"
        )

    missing_name = "missing"
    while missing_name in expected.re.groupindex:
        missing_name += "_group"

    invalid_references = (
        -1,
        expected.re.groups + 1,
        None,
        (1,),
        1.0,
        b"missing",
        missing_name,
    )
    for reference in invalid_references:
        for accessor_name in _MATCH_ACCESSOR_NAMES:
            expected_error = capture_error(expected, accessor_name, reference)
            observed_error = capture_error(observed, accessor_name, reference)

            assert type(observed_error) is type(expected_error)
            assert observed_error.args == expected_error.args


def record_generated_match_failure(
    failures: list[str],
    *,
    label: str,
    backend_name: str,
    observed: object,
    expected: re.Match[str] | re.Match[bytes] | None,
) -> None:
    try:
        assert_match_result_parity(
            backend_name,
            observed,
            expected,
            check_regs=True,
        )
        if expected is None:
            return

        assert_match_convenience_api_parity(observed, expected)
        assert_valid_match_group_access_parity(observed, expected)
        assert_invalid_match_group_access_parity(observed, expected)
    except AssertionError as exc:
        failures.append(f"{label}: {exc}")


def assert_placeholder_message_contains(
    error: BaseException,
    expected_fragment: str,
) -> None:
    assert expected_fragment in str(error)


def assert_fixture_case_optional_match_parity(
    regex_backend: tuple[str, object],
    case: FixtureCase,
    *,
    expected_helper: str,
    compile_pattern: bool,
    check_regs: bool = False,
    check_convenience_api: bool = False,
    check_group_access: bool = False,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper == expected_helper

    if compile_pattern or case.use_compiled_pattern:
        observed_target, expected_target = compile_with_cpython_parity(
            backend_name,
            backend,
            case_pattern(case),
            case.flags or 0,
        )
        if case.operation == "module_call":
            observed = getattr(backend, expected_helper)(
                *case.module_call_args(observed_target),
                **case.kwargs,
            )
            expected = getattr(re, expected_helper)(
                *case.module_call_args(expected_target),
                **case.kwargs,
            )
        else:
            observed = getattr(observed_target, expected_helper)(
                *case.args,
                **case.kwargs,
            )
            expected = getattr(expected_target, expected_helper)(
                *case.args,
                **case.kwargs,
            )
    else:
        observed = getattr(backend, expected_helper)(*case.args, **case.kwargs)
        expected = getattr(re, expected_helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    if expected is None:
        return

    assert observed is not None
    assert_match_parity(
        backend_name,
        observed,
        expected,
        check_regs=check_regs,
    )
    if check_convenience_api:
        assert_match_convenience_api_parity(observed, expected)
    if check_group_access:
        assert_valid_match_group_access_parity(observed, expected)
        assert_invalid_match_group_access_parity(observed, expected)


def assert_bounded_pattern_case_match_parity(
    regex_backend: tuple[str, object],
    case: object,
    *,
    expect_match: bool = True,
    check_regs: bool = False,
    check_convenience_api: bool = False,
    check_group_access: bool = False,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        getattr(case, "pattern"),
    )
    observed = invoke_bounded_pattern_case(observed_pattern, case)
    expected = invoke_bounded_pattern_case(expected_pattern, case)

    assert_match_result_parity(
        backend_name,
        observed,
        expected,
        check_regs=check_regs,
    )
    if not expect_match:
        assert expected is None
        return

    assert expected is not None
    if check_convenience_api:
        assert_match_convenience_api_parity(observed, expected)
    if check_group_access:
        assert_valid_match_group_access_parity(observed, expected)
        assert_invalid_match_group_access_parity(observed, expected)
