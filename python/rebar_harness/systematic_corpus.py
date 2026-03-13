"""Deterministic expansion helpers for compact correctness corpus specs."""

from __future__ import annotations

from typing import Any


GENERATOR_ID = "systematic_feature_corpus"
GENERATOR_VERSION = 1


def expand_systematic_manifest(raw_manifest: dict[str, Any]) -> dict[str, Any]:
    generator = raw_manifest.get("generator")
    if generator is None:
        return raw_manifest
    if not isinstance(generator, dict):
        raise ValueError("fixture manifest generator must be an object")
    if str(generator.get("id")) != GENERATOR_ID:
        raise ValueError(f"unsupported fixture generator {generator.get('id')!r}")
    if int(generator.get("version", 0)) != GENERATOR_VERSION:
        raise ValueError(
            f"unsupported {GENERATOR_ID} generator version {generator.get('version')!r}; "
            f"expected {GENERATOR_VERSION}"
        )

    feature_specs = raw_manifest.get("feature_specs")
    if not isinstance(feature_specs, list) or not feature_specs:
        raise ValueError("systematic corpus manifests require a non-empty feature_specs list")
    if raw_manifest.get("cases"):
        raise ValueError("systematic corpus manifests must not define literal cases")

    expanded_manifest = dict(raw_manifest)
    expanded_manifest["cases"] = [
        case
        for feature_spec in feature_specs
        for case in _expand_feature_spec(feature_spec, defaults=raw_manifest.get("defaults", {}))
    ]
    return expanded_manifest


def _expand_feature_spec(feature_spec: dict[str, Any], *, defaults: dict[str, Any]) -> list[dict[str, Any]]:
    feature_id = str(feature_spec["id"])
    family_prefix = str(feature_spec.get("family_prefix", feature_id.replace("-", "_")))
    variants = feature_spec.get("variants")
    expansions = feature_spec.get("expansions")
    if not isinstance(variants, list) or not variants:
        raise ValueError(f"feature spec {feature_id!r} requires a non-empty variants list")
    if not isinstance(expansions, list) or not expansions:
        raise ValueError(f"feature spec {feature_id!r} requires a non-empty expansions list")

    feature_categories = _string_list(feature_spec.get("categories", []))
    feature_notes = _string_list(feature_spec.get("notes", []))
    cases: list[dict[str, Any]] = []
    for variant in variants:
        variant_id = str(variant["id"])
        context = {
            "feature_id": feature_id,
            "variant_id": variant_id,
            "pattern": str(variant["pattern"]),
            "group_name": str(variant.get("group_name", "")),
            "text_model": str(variant.get("text_model", defaults.get("text_model", "str"))),
        }
        variant_categories = _string_list(variant.get("categories", []))
        variant_notes = _string_list(variant.get("notes", []))
        for expansion in expansions:
            expansion_id = str(expansion["id"])
            text_model = str(expansion.get("text_model", context["text_model"]))
            case_context = {**context, "text_model": text_model}
            case_payload = {
                "id": (
                    f"systematic-{feature_id}-{variant_id}-{expansion_id}-{text_model}"
                ),
                "family": (
                    f"{family_prefix}_{variant_id}_"
                    f"{str(expansion.get('family_suffix', expansion_id.replace('-', '_')))}"
                ),
                "operation": str(expansion["operation"]),
                "notes": [
                    *feature_notes,
                    *variant_notes,
                    *_string_list(expansion.get("notes", [])),
                ],
                "categories": [
                    "systematic",
                    *feature_categories,
                    *variant_categories,
                    *_string_list(expansion.get("categories", [])),
                ],
                "text_model": text_model,
            }
            if "helper" in expansion:
                case_payload["helper"] = _render_template(expansion["helper"], case_context)
            if expansion.get("include_pattern", expansion["operation"] != "module_call"):
                case_payload["pattern"] = case_context["pattern"]
            if "flags" in expansion:
                case_payload["flags"] = int(expansion["flags"])
            if "args" in expansion:
                case_payload["args"] = _render_template(expansion["args"], case_context)
            if "kwargs" in expansion:
                case_payload["kwargs"] = _render_template(expansion["kwargs"], case_context)
            cases.append(case_payload)
    return cases


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"expected a list of strings, got {type(value).__name__}")
    return [str(item) for item in value]


def _render_template(value: Any, context: dict[str, str]) -> Any:
    if isinstance(value, str):
        try:
            return value.format_map(context)
        except KeyError as exc:  # pragma: no cover - exercised by malformed fixtures
            raise ValueError(f"missing template key {exc.args[0]!r}") from exc
    if isinstance(value, list):
        return [_render_template(item, context) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _render_template(item_value, context)
            for key, item_value in value.items()
        }
    return value
