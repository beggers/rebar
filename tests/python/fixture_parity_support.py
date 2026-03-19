from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
import pathlib
import re

import rebar
from rebar_harness.correctness import (
    CORRECTNESS_FIXTURES_ROOT,
    FixtureCase,
    FixtureManifest,
    load_fixture_manifest,
)

_MISSING_GROUP_DEFAULT = object()
_MATCH_ACCESSOR_NAMES = ("group", "span", "start", "end", "getitem")


def _duplicate_string_ids(ids: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(case_id for case_id, count in Counter(ids).items() if count > 1)


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


@dataclass(frozen=True)
class FixtureBundleSpec:
    fixture_name: str
    expected_manifest_id: str
    expected_patterns: frozenset[str | bytes]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]
    selected_case_ids: tuple[str, ...] | None = None
    expected_case_ids: frozenset[str] | None = None
    expected_text_models: frozenset[str] | None = None


def _build_fixture_bundle(
    manifest: FixtureManifest,
    cases: tuple[FixtureCase, ...],
    *,
    expected_manifest_id: str | None = None,
    expected_patterns: frozenset[str | bytes],
    expected_operation_helper_counts: Counter[tuple[str, str | None]],
    selected_case_ids: tuple[str, ...] | None = None,
    expected_case_ids: frozenset[str] | None = None,
    expected_text_models: frozenset[str] | None = None,
) -> FixtureBundle:
    if expected_manifest_id is not None and manifest.manifest_id != expected_manifest_id:
        raise ValueError(
            f"{manifest.path.name} expected_manifest_id {expected_manifest_id!r} "
            f"does not match loaded manifest_id {manifest.manifest_id!r}"
        )

    bundle_text_models = expected_text_models
    if bundle_text_models is None and selected_case_ids is None:
        bundle_text_models = frozenset({"str"})

    bundle_case_ids = expected_case_ids
    if bundle_case_ids is None and selected_case_ids is not None:
        bundle_case_ids = frozenset(selected_case_ids)

    return FixtureBundle(
        manifest=manifest,
        cases=cases,
        expected_patterns=expected_patterns,
        expected_operation_helper_counts=expected_operation_helper_counts,
        expected_case_ids=bundle_case_ids,
        expected_text_models=bundle_text_models,
    )


def load_fixture_bundles(
    specs: Iterable[FixtureBundleSpec],
) -> tuple[FixtureBundle, ...]:
    bundles: list[FixtureBundle] = []
    for spec in specs:
        manifest = load_fixture_manifest(
            CORRECTNESS_FIXTURES_ROOT / spec.fixture_name
        )
        loaded_cases = tuple(manifest.cases)
        if spec.selected_case_ids is None:
            bundle_cases = loaded_cases
        else:
            if not spec.selected_case_ids:
                raise ValueError(
                    f"{spec.fixture_name} selected_case_ids must not be empty"
                )
            duplicate_case_ids = tuple(
                case_id
                for case_id, count in Counter(spec.selected_case_ids).items()
                if count > 1
            )
            if duplicate_case_ids:
                raise ValueError(
                    f"{spec.fixture_name} selected_case_ids contains duplicate ids: "
                    f"{duplicate_case_ids}"
                )
            case_by_id = {case.case_id: case for case in loaded_cases}
            missing_case_ids = tuple(
                case_id
                for case_id in spec.selected_case_ids
                if case_id not in case_by_id
            )
            if missing_case_ids:
                raise ValueError(
                    f"{spec.fixture_name} is missing expected fixture rows: {missing_case_ids}"
                )
            bundle_cases = tuple(
                case_by_id[case_id] for case_id in spec.selected_case_ids
            )
        bundles.append(
            _build_fixture_bundle(
                manifest,
                bundle_cases,
                expected_manifest_id=spec.expected_manifest_id,
                expected_patterns=spec.expected_patterns,
                expected_operation_helper_counts=spec.expected_operation_helper_counts,
                selected_case_ids=spec.selected_case_ids,
                expected_case_ids=spec.expected_case_ids,
                expected_text_models=spec.expected_text_models,
            )
        )
    return tuple(bundles)


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


def load_published_fixture_bundles(
    fixture_paths: Iterable[pathlib.Path],
) -> tuple[FixtureBundle, ...]:
    bundles: list[FixtureBundle] = []

    for path in fixture_paths:
        manifest = load_fixture_manifest(path)
        loaded_cases = tuple(manifest.cases)
        bundles.append(
            _build_fixture_bundle(
                manifest,
                loaded_cases,
                expected_patterns=frozenset(
                    case_pattern(case) for case in loaded_cases
                ),
                expected_operation_helper_counts=Counter(
                    (case.operation, case.helper) for case in loaded_cases
                ),
                expected_text_models=frozenset(
                    case.text_model for case in loaded_cases
                ),
            )
        )

    return tuple(bundles)


def published_fixture_bundle_by_manifest_id(
    bundles: Iterable[FixtureBundle],
    manifest_id: str,
) -> FixtureBundle:
    loaded_bundles = tuple(bundles)
    matching_bundles = tuple(
        bundle for bundle in loaded_bundles if bundle.manifest.manifest_id == manifest_id
    )
    if not matching_bundles:
        raise ValueError(
            f"published fixture bundles do not contain manifest_id {manifest_id!r}"
        )
    if len(matching_bundles) > 1:
        raise ValueError(
            f"published fixture bundles contain duplicate manifest_id {manifest_id!r}"
        )
    return matching_bundles[0]


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


def _manifest_bucket_case_ids(
    cases: Iterable[FixtureCase],
    *,
    manifest_id: str,
    text_model: str,
    operation: str,
) -> frozenset[str]:
    return frozenset(
        case.case_id
        for case in cases
        if case.manifest_id == manifest_id
        and case.text_model == text_model
        and case.operation == operation
    )


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
        bucket_bytes_case_ids = _manifest_bucket_case_ids(
            bucket_cases,
            manifest_id=manifest_id,
            text_model="bytes",
            operation=operation,
        )
        if bucket_bytes_case_ids:
            drift_messages.append(
                f"{operation} bucket unexpectedly includes bytes case ids "
                f"{tuple(sorted(bucket_bytes_case_ids))}"
            )

        expected_str_case_ids = frozenset(
            case.case_id for case in bundle_str_cases if case.operation == operation
        )
        bucket_str_case_ids = _manifest_bucket_case_ids(
            bucket_cases,
            manifest_id=manifest_id,
            text_model="str",
            operation=operation,
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
        if case.operation == "module_call":
            text = case.args[1]
            assert isinstance(text, bytes)
            published_module_texts_by_pattern.setdefault(pattern, set()).add(text)
        elif case.operation == "pattern_call":
            text = case.args[0]
            assert isinstance(text, bytes)
            published_fullmatch_texts_by_pattern.setdefault(pattern, set()).add(text)

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


def assert_mixed_text_model_bundles_have_direct_bytes_follow_on_routing(
    bundles: Iterable[FixtureBundle],
    *,
    direct_bytes_follow_on_bundles: Iterable[FixtureBundle],
    coverage_label: str,
) -> None:
    loaded_bundles = tuple(bundles)
    loaded_direct_bundles = tuple(direct_bytes_follow_on_bundles)
    ordered_mixed_manifest_ids = tuple(
        bundle.manifest.manifest_id
        for bundle in loaded_bundles
        if {case.text_model for case in bundle.cases} == {"bytes", "str"}
    )
    ordered_direct_manifest_ids = tuple(
        bundle.manifest.manifest_id for bundle in loaded_direct_bundles
    )
    if ordered_mixed_manifest_ids == ordered_direct_manifest_ids:
        return

    mixed_manifest_id_set = frozenset(ordered_mixed_manifest_ids)
    direct_manifest_id_set = frozenset(ordered_direct_manifest_ids)
    missing_mixed_manifest_ids = tuple(
        manifest_id
        for manifest_id in ordered_mixed_manifest_ids
        if manifest_id not in direct_manifest_id_set
    )
    unexpected_direct_manifest_ids = tuple(
        manifest_id
        for manifest_id in ordered_direct_manifest_ids
        if manifest_id not in mixed_manifest_id_set
    )
    if missing_mixed_manifest_ids or unexpected_direct_manifest_ids:
        raise AssertionError(
            f"{coverage_label} direct bytes follow-on manifest routing drifted; "
            f"missing mixed manifests: {missing_mixed_manifest_ids}; "
            f"unexpected direct manifests: {unexpected_direct_manifest_ids}"
        )

    raise AssertionError(
        f"{coverage_label} direct bytes follow-on manifest order drifted; "
        f"expected {ordered_mixed_manifest_ids}, got {ordered_direct_manifest_ids}"
    )


def assert_fixture_bundle_tracks_published_case_frontier(
    bundle: FixtureBundle,
    *,
    selected_case_ids: Iterable[str],
    expected_uncovered_case_ids: Iterable[str] = (),
) -> None:
    ordered_selected_case_ids = tuple(selected_case_ids)
    ordered_expected_uncovered_case_ids = tuple(expected_uncovered_case_ids)
    duplicate_selected_case_ids = _duplicate_string_ids(ordered_selected_case_ids)
    if duplicate_selected_case_ids:
        raise AssertionError(
            f"{bundle.expected_manifest_id} selected_case_ids contain duplicate ids: "
            f"{duplicate_selected_case_ids}"
        )

    duplicate_uncovered_case_ids = _duplicate_string_ids(
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
    duplicate_selected_case_ids = _duplicate_string_ids(ordered_selected_case_ids)
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


def ordered_manifest_cases_from_bundles(
    bundles: Iterable[FixtureBundle],
    case_ids: Iterable[str],
    *,
    error_label: str,
) -> tuple[FixtureCase, ...]:
    ordered_case_ids = tuple(case_ids)
    duplicate_requested_case_ids = _duplicate_string_ids(ordered_case_ids)
    if duplicate_requested_case_ids:
        raise AssertionError(
            f"{error_label} contain duplicate requested case ids: "
            f"{duplicate_requested_case_ids}"
        )
    selected_case_ids = frozenset(ordered_case_ids)
    case_by_id: dict[str, FixtureCase] = {}
    duplicate_case_ids: set[str] = set()

    for bundle in bundles:
        for case in bundle.manifest.cases:
            case_id = case.case_id
            if case_id not in selected_case_ids:
                continue
            if case_id in case_by_id:
                duplicate_case_ids.add(case_id)
                continue
            case_by_id[case_id] = case

    ordered_duplicate_case_ids = tuple(
        case_id for case_id in ordered_case_ids if case_id in duplicate_case_ids
    )
    if ordered_duplicate_case_ids:
        raise AssertionError(
            f"{error_label} contain duplicate case ids: {ordered_duplicate_case_ids}"
        )

    missing_case_ids = tuple(
        case_id for case_id in ordered_case_ids if case_id not in case_by_id
    )
    if missing_case_ids:
        raise AssertionError(
            f"{error_label} are missing case ids: {missing_case_ids}"
        )

    return tuple(case_by_id[case_id] for case_id in ordered_case_ids)


def case_pattern(case: FixtureCase) -> str | bytes:
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, (str, bytes))
    return pattern


def str_case_pattern(case: FixtureCase) -> str:
    pattern = case_pattern(case)
    assert isinstance(pattern, str)
    return pattern


def _case_argument_by_operation(
    case: FixtureCase,
    *,
    module_index: int,
    pattern_index: int,
) -> object:
    if case.operation == "module_call":
        return case.args[module_index]
    if case.operation == "pattern_call":
        return case.args[pattern_index]
    raise AssertionError(f"unsupported case operation {case.operation!r}")


def case_replacement_argument(case: FixtureCase) -> object:
    return _case_argument_by_operation(case, module_index=1, pattern_index=0)


def case_text_argument(case: FixtureCase) -> str | bytes:
    text = _case_argument_by_operation(case, module_index=2, pattern_index=1)
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
) -> tuple[object, re.Pattern[str] | re.Pattern[bytes]]:
    observed = backend.compile(pattern, flags)
    expected = re.compile(pattern, flags)

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
        observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
        expected = getattr(re, case.helper)(*case.args, **case.kwargs)
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
) -> None:
    observed_matches = list(observed_iter)
    expected_matches = list(expected_iter)

    assert len(observed_matches) == len(expected_matches)
    for observed, expected in zip(observed_matches, expected_matches):
        assert_match_result_parity(
            backend_name,
            observed,
            expected,
            check_regs=check_regs,
        )

    assert next(observed_iter, None) is None
    assert next(expected_iter, None) is None


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


def assert_match_group_access_parity(
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
) -> None:
    assert_valid_match_group_access_parity(observed, expected)
    assert_invalid_match_group_access_parity(observed, expected)


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


def _assert_optional_match_case_parity(
    backend_name: str,
    observed: object,
    expected: re.Match[str] | re.Match[bytes] | None,
    *,
    check_regs: bool = False,
    check_convenience_api: bool = False,
    check_group_access: bool = False,
) -> None:
    if expected is None:
        assert observed is None
        return

    assert observed is not None
    if not check_convenience_api and not check_group_access:
        assert_match_parity(
            backend_name,
            observed,
            expected,
            check_regs=check_regs,
        )
        return

    if check_convenience_api:
        assert_match_convenience_api_parity(observed, expected)
    if check_group_access:
        assert_match_group_access_parity(observed, expected)


def assert_module_search_case_parity(
    regex_backend: tuple[str, object],
    case: FixtureCase,
    *,
    check_regs: bool = False,
    check_convenience_api: bool = False,
    check_group_access: bool = False,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper == "search"

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    _assert_optional_match_case_parity(
        backend_name,
        observed,
        expected,
        check_regs=check_regs,
        check_convenience_api=check_convenience_api,
        check_group_access=check_group_access,
    )


def assert_pattern_fullmatch_case_parity(
    regex_backend: tuple[str, object],
    case: FixtureCase,
    *,
    check_regs: bool = False,
    check_convenience_api: bool = False,
    check_group_access: bool = False,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper == "fullmatch"

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert (observed is None) == (expected is None)
    _assert_optional_match_case_parity(
        backend_name,
        observed,
        expected,
        check_regs=check_regs,
        check_convenience_api=check_convenience_api,
        check_group_access=check_group_access,
    )


def assert_bounded_pattern_case_match_parity(
    regex_backend: tuple[str, object],
    case: object,
    *,
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
    assert expected is not None
    if check_convenience_api:
        assert_match_convenience_api_parity(observed, expected)
    if check_group_access:
        assert_match_group_access_parity(observed, expected)


def assert_bounded_pattern_case_no_match_parity(
    regex_backend: tuple[str, object],
    case: object,
    *,
    check_regs: bool = False,
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
