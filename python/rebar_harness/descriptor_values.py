from __future__ import annotations

from typing import Any


def _tag_descriptor_callable(
    callback: Any,
    *,
    callback_name: str,
    callback_module_name: str | None,
) -> Any:
    if callback_module_name is not None:
        callback.__module__ = callback_module_name
    callback.__name__ = callback_name
    callback.__qualname__ = callback_name
    return callback


def materialize_descriptor_value(
    value: Any,
    *,
    text_model: str | None = None,
    callback_module_name: str | None = None,
) -> Any:
    if isinstance(value, str):
        if text_model in (None, "str"):
            return value
        if text_model == "bytes":
            return value.encode("utf-8")
        raise ValueError(f"unsupported text model {text_model!r}")
    if isinstance(value, list):
        return [
            materialize_descriptor_value(
                item,
                text_model=text_model,
                callback_module_name=callback_module_name,
            )
            for item in value
        ]
    if isinstance(value, dict):
        value_type = value.get("type")
        if value_type == "bytes":
            encoding = str(value.get("encoding", "latin-1"))
            return str(value["value"]).encode(encoding)
        if value_type == "callable_constant":
            constant_value = materialize_descriptor_value(
                value.get("value"),
                text_model=text_model,
                callback_module_name=callback_module_name,
            )

            def _callable_constant(_match: Any, *, _value: Any = constant_value) -> Any:
                return _value

            return _tag_descriptor_callable(
                _callable_constant,
                callback_name="callable_constant",
                callback_module_name=callback_module_name,
            )
        if value_type == "callable_match_group":
            group_reference = value.get("group", 0)
            prefix = materialize_descriptor_value(
                value.get("prefix", ""),
                text_model=text_model,
                callback_module_name=callback_module_name,
            )
            suffix = materialize_descriptor_value(
                value.get("suffix", ""),
                text_model=text_model,
                callback_module_name=callback_module_name,
            )

            def _callable_match_group(
                match: Any,
                *,
                _group_reference: Any = group_reference,
                _prefix: Any = prefix,
                _suffix: Any = suffix,
            ) -> Any:
                return _prefix + match.group(_group_reference) + _suffix

            return _tag_descriptor_callable(
                _callable_match_group,
                callback_name="callable_match_group",
                callback_module_name=callback_module_name,
            )
        return {
            str(key): materialize_descriptor_value(
                item_value,
                text_model=text_model,
                callback_module_name=callback_module_name,
            )
            for key, item_value in value.items()
        }
    return value
