from __future__ import annotations

import re

import rebar


MISSING_GROUP_DEFAULT = "<missing-group>"


def _callback_match_snapshot(
    match: re.Match[str] | re.Match[bytes] | rebar.Match,
    *,
    group_names: tuple[str, ...] = (),
) -> dict[str, object]:
    templates = [r"<\g<0>>"]
    if match.re.groups >= 1:
        templates.append(r"<\1>")
    if match.re.groups >= 2:
        templates.append(r"<\1:\2>")
    if group_names:
        templates.append(
            "<" + ":".join(fr"\g<{group_name}>" for group_name in group_names) + ">"
        )

    snapshot: dict[str, object] = {
        "string": match.string,
        "pattern": match.re.pattern,
        "pattern_flags": match.re.flags,
        "pattern_groups": match.re.groups,
        "pattern_groupindex": dict(match.re.groupindex),
        "group0": match.group(0),
        "getitem0": match[0],
        "groups": match.groups(),
        "groups_default": match.groups(MISSING_GROUP_DEFAULT),
        "groupdict": match.groupdict(),
        "groupdict_default": match.groupdict(MISSING_GROUP_DEFAULT),
        "span": match.span(),
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
        "pos": match.pos,
        "endpos": match.endpos,
        "has_regs": hasattr(match, "regs"),
        "regs": tuple(match.regs) if hasattr(match, "regs") else None,
        "expand": {
            template: match.expand(template)
            for template in templates
        },
    }

    for group_index in range(1, match.re.groups + 1):
        snapshot[f"group{group_index}"] = match.group(group_index)
        snapshot[f"getitem{group_index}"] = match[group_index]
        snapshot[f"span{group_index}"] = match.span(group_index)
        snapshot[f"start{group_index}"] = match.start(group_index)
        snapshot[f"end{group_index}"] = match.end(group_index)

    for group_name in group_names:
        snapshot[f"group:{group_name}"] = match.group(group_name)
        snapshot[f"getitem:{group_name}"] = match[group_name]
        snapshot[f"span:{group_name}"] = match.span(group_name)
        snapshot[f"start:{group_name}"] = match.start(group_name)
        snapshot[f"end:{group_name}"] = match.end(group_name)

    return snapshot


def assert_callable_replacement_match_parity(
    *,
    backend_name: str,
    backend: object,
    helper: str,
    pattern: str,
    string: str,
    count: int,
    group_names: tuple[str, ...] = (),
    use_compiled_pattern: bool = False,
) -> None:
    observed_matches: list[dict[str, object]] = []
    expected_matches: list[dict[str, object]] = []

    def observed_replacement(match: object) -> str:
        if backend_name == "rebar":
            assert type(match) is rebar.Match
        else:
            assert type(match) is re.Match
        observed_matches.append(
            _callback_match_snapshot(match, group_names=group_names)
        )
        return "X"

    def expected_replacement(match: re.Match[str]) -> str:
        assert type(match) is re.Match
        expected_matches.append(
            _callback_match_snapshot(match, group_names=group_names)
        )
        return "X"

    if use_compiled_pattern:
        observed_target = backend.compile(pattern)
        expected_target = re.compile(pattern)
        observed = getattr(observed_target, helper)(
            observed_replacement,
            string,
            count=count,
        )
        expected = getattr(expected_target, helper)(
            expected_replacement,
            string,
            count=count,
        )
    else:
        observed = getattr(backend, helper)(
            pattern,
            observed_replacement,
            string,
            count=count,
        )
        expected = getattr(re, helper)(
            pattern,
            expected_replacement,
            string,
            count=count,
        )

    assert observed == expected
    assert observed_matches == expected_matches
