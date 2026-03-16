from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable
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


FIXTURES_DIR = CORRECTNESS_FIXTURES_ROOT

_MISSING_GROUP_DEFAULT = object()
_MATCH_ACCESSOR_NAMES = ("group", "span", "start", "end", "getitem")

# These published correctness cases are covered by a sibling parity suite
# instead of the manifest's primary suite.
LITERAL_FLAG_DELEGATED_CASE_IDS: tuple[str, ...] = (
    "flag-unsupported-nonliteral-ignorecase-search",
)


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
    expected_manifest_id: str
    expected_patterns: frozenset[str | bytes]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]
    expected_case_ids: frozenset[str] | None = None
    expected_text_models: frozenset[str] | None = None


@dataclass(frozen=True)
class FixtureBundleSpec:
    fixture_name: str
    expected_manifest_id: str
    expected_patterns: frozenset[str | bytes]
    expected_operation_helper_counts: Counter[tuple[str, str | None]]
    selected_case_ids: tuple[str, ...] | None = None
    expected_case_ids: frozenset[str] | None = None
    expected_text_models: frozenset[str] | None = None


def load_fixture_bundles(
    specs: Iterable[FixtureBundleSpec],
) -> tuple[FixtureBundle, ...]:
    bundles: list[FixtureBundle] = []
    for spec in specs:
        manifest, cases = load_fixture_manifest(FIXTURES_DIR / spec.fixture_name)
        loaded_cases = tuple(cases)
        if spec.selected_case_ids is None:
            bundle_cases = loaded_cases
        else:
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

        bundle_text_models = spec.expected_text_models
        if bundle_text_models is None and spec.selected_case_ids is None:
            bundle_text_models = frozenset({"str"})
        bundle_case_ids = spec.expected_case_ids
        if bundle_case_ids is None and spec.selected_case_ids is not None:
            bundle_case_ids = frozenset(spec.selected_case_ids)

        bundles.append(
            FixtureBundle(
                manifest=manifest,
                cases=bundle_cases,
                expected_manifest_id=spec.expected_manifest_id,
                expected_patterns=spec.expected_patterns,
                expected_operation_helper_counts=spec.expected_operation_helper_counts,
                expected_case_ids=bundle_case_ids,
                expected_text_models=bundle_text_models,
            )
        )
    return tuple(bundles)


def fixture_cases_from_bundles(
    bundles: Iterable[FixtureBundle],
) -> tuple[FixtureCase, ...]:
    return tuple(case for bundle in bundles for case in bundle.cases)


def fixture_cases_for_operation(
    bundles: Iterable[FixtureBundle],
    operation: str,
) -> tuple[FixtureCase, ...]:
    return tuple(
        case for case in fixture_cases_from_bundles(bundles) if case.operation == operation
    )


def load_published_fixture_bundles(
    fixture_paths: Iterable[pathlib.Path],
) -> tuple[FixtureBundle, ...]:
    bundles: list[FixtureBundle] = []

    for path in fixture_paths:
        manifest, cases = load_fixture_manifest(path)
        loaded_cases = tuple(cases)
        bundles.append(
            FixtureBundle(
                manifest=manifest,
                cases=loaded_cases,
                expected_manifest_id=manifest.manifest_id,
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


def published_fixture_paths_from_bundles(
    bundles: Iterable[FixtureBundle],
) -> tuple[pathlib.Path, ...]:
    return tuple(sorted((bundle.manifest.path for bundle in bundles), key=lambda path: path.name))


def _manifest_raw_cases(bundle: FixtureBundle) -> tuple[dict[str, object], ...]:
    raw_cases = bundle.manifest.raw.get("cases", [])
    if not isinstance(raw_cases, list):
        raise ValueError(
            f"fixture manifest {bundle.manifest.manifest_id!r} raw cases must be a list"
        )
    return tuple(
        raw_case
        for raw_case in raw_cases
        if isinstance(raw_case, dict) and "id" in raw_case
    )


def manifest_case_ids(bundle: FixtureBundle) -> tuple[str, ...]:
    return tuple(str(raw_case["id"]) for raw_case in _manifest_raw_cases(bundle))


def bundle_patterns(
    bundle: FixtureBundle,
    *,
    pattern_extractor: Callable[[FixtureCase], str | bytes],
) -> frozenset[str | bytes]:
    return frozenset(pattern_extractor(case) for case in bundle.cases)


def raw_fixture_cases_by_id(bundle: FixtureBundle) -> dict[str, dict[str, object]]:
    selected_case_ids = {case.case_id for case in bundle.cases}

    return {
        str(raw_case["id"]): raw_case
        for raw_case in _manifest_raw_cases(bundle)
        if str(raw_case["id"]) in selected_case_ids
    }


def ordered_manifest_cases_from_bundles(
    bundles: Iterable[FixtureBundle],
    case_ids: Iterable[str],
    *,
    error_label: str,
) -> tuple[FixtureCase, ...]:
    ordered_case_ids = tuple(case_ids)
    selected_case_ids = frozenset(ordered_case_ids)
    case_by_id: dict[str, FixtureCase] = {}
    duplicate_case_ids: set[str] = set()

    for bundle in bundles:
        for raw_case in _manifest_raw_cases(bundle):
            case_id = str(raw_case["id"])
            if case_id not in selected_case_ids:
                continue
            if case_id in case_by_id:
                duplicate_case_ids.add(case_id)
                continue
            case_by_id[case_id] = FixtureCase.from_dict(bundle.manifest, raw_case)

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

    for group_index in range(expected.re.groups + 1):
        assert observed[group_index] == expected[group_index]

    for group_name in group_names:
        assert observed[group_name] == expected[group_name]

    for template in _match_api_templates(
        expected.re.pattern,
        group_count=expected.re.groups,
        group_names=group_names,
    ):
        assert observed.expand(template) == expected.expand(template)


def assert_valid_match_group_access_parity(
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
) -> None:
    for reference in _valid_match_group_references(expected):
        for accessor_name in _MATCH_ACCESSOR_NAMES:
            assert _apply_match_accessor(observed, accessor_name, reference) == (
                _apply_match_accessor(expected, accessor_name, reference)
            )


def assert_invalid_match_group_access_parity(
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
) -> None:
    for reference in _invalid_match_group_references(expected):
        for accessor_name in _MATCH_ACCESSOR_NAMES:
            expected_error = _capture_match_accessor_error(expected, accessor_name, reference)
            observed_error = _capture_match_accessor_error(observed, accessor_name, reference)

            assert type(observed_error) is type(expected_error)
            assert observed_error.args == expected_error.args


def _match_api_templates(
    pattern: str | bytes,
    *,
    group_count: int,
    group_names: tuple[str, ...],
) -> tuple[str | bytes, ...]:
    templates = [r"<\g<0>>"]
    if group_count >= 1:
        templates.append(
            "<" + "|".join(f"\\{group_index}" for group_index in range(1, group_count + 1)) + ">"
        )
        templates.append(
            "<"
            + "|".join(f"\\g<{group_index}>" for group_index in range(group_count + 1))
            + ">"
        )
    if len(group_names) >= 2:
        templates.append(
            "<" + "|".join(fr"\g<{group_name}>" for group_name in group_names) + ">"
        )
    for group_name in group_names:
        templates.append(fr"<\g<{group_name}>>")

    if isinstance(pattern, bytes):
        return tuple(template.encode("ascii") for template in templates)
    return tuple(templates)


def _valid_match_group_references(
    expected: re.Match[str] | re.Match[bytes],
) -> tuple[object, ...]:
    references: list[object] = list(range(expected.re.groups + 1))
    # CPython accepts bools here because they are int subclasses.
    references.append(False)
    if expected.re.groups >= 1:
        references.append(True)
    references.extend(expected.re.groupindex)
    return tuple(references)


def _invalid_match_group_references(
    expected: re.Match[str] | re.Match[bytes],
) -> tuple[object, ...]:
    missing_name = "missing"
    while missing_name in expected.re.groupindex:
        missing_name += "_group"
    return (-1, expected.re.groups + 1, None, (1,), 1.0, b"missing", missing_name)


def _apply_match_accessor(
    match: object,
    accessor_name: str,
    reference: object,
) -> object:
    if accessor_name == "group":
        return match.group(reference)
    if accessor_name == "span":
        return match.span(reference)
    if accessor_name == "start":
        return match.start(reference)
    if accessor_name == "end":
        return match.end(reference)
    if accessor_name == "getitem":
        return match[reference]
    raise AssertionError(f"unknown accessor {accessor_name!r}")


def _capture_match_accessor_error(
    match: object,
    accessor_name: str,
    reference: object,
) -> BaseException:
    try:
        _apply_match_accessor(match, accessor_name, reference)
    except BaseException as error:  # noqa: BLE001 - parity helper compares exception details.
        return error
    raise AssertionError(
        f"expected {accessor_name}({reference!r}) to raise for {match.re.pattern!r}"
    )
