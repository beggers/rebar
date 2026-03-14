MANIFEST = {
  "schema_version": 1,
  "manifest_id": "numbered-backreference-workflows",
  "layer": "match_behavior",
  "suite_id": "match.numbered_backreference",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "numbered-backreference-compile-metadata-str",
      "operation": "compile",
      "family": "numbered_backreference_compile_metadata",
      "pattern": "(ab)\\1",
      "categories": ["grouped", "numbered-backreference", "compile", "metadata", "str"],
      "notes": [
        "Publishes the tiny numbered-backreference compile path so the next grouped-reference frontier stays visible in the combined scorecard."
      ]
    },
    {
      "id": "numbered-backreference-module-search-str",
      "operation": "module_call",
      "family": "numbered_backreference_module_workflow",
      "helper": "search",
      "args": ["(ab)\\1", "zzababzz"],
      "categories": ["grouped", "numbered-backreference", "search", "module", "str"],
      "notes": [
        "Captures the bounded module-level numbered-backreference match path for a tiny literal workflow without broadening into nested references, alternation, or conditional groups."
      ]
    },
    {
      "id": "numbered-backreference-pattern-search-str",
      "operation": "pattern_call",
      "family": "numbered_backreference_pattern_workflow",
      "pattern": "(ab)\\1",
      "helper": "search",
      "args": ["zzababzz"],
      "categories": ["grouped", "numbered-backreference", "search", "pattern", "str"],
      "notes": [
        "Captures the bounded Pattern.search numbered-backreference path for the same tiny literal workflow while leaving broader grouped execution out of scope."
      ]
    }
  ]
}
