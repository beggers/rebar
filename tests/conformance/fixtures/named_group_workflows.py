MANIFEST = {
  "schema_version": 1,
  "manifest_id": "named-group-workflows",
  "layer": "match_behavior",
  "suite_id": "match.named",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "named-group-compile-metadata-str",
      "operation": "compile",
      "family": "named_group_compile_metadata",
      "pattern": "(?P<word>abc)",
      "categories": ["grouped", "named-group", "compile", "metadata", "str"],
      "notes": [
        "Pins named-group compile metadata through the public compile path, including groupindex for a tiny literal capture."
      ]
    },
    {
      "id": "named-group-module-search-metadata-str",
      "operation": "module_call",
      "family": "named_group_module_workflow",
      "helper": "search",
      "args": ["(?P<word>abc)", "zzabczz"],
      "categories": ["grouped", "named-group", "search", "module", "str"],
      "notes": [
        "Captures named-group module-search metadata including groupdict(), group(\"word\"), span(\"word\"), and lastgroup."
      ]
    },
    {
      "id": "named-group-pattern-search-metadata-str",
      "operation": "pattern_call",
      "family": "named_group_pattern_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "search",
      "args": ["zzabczz"],
      "categories": ["grouped", "named-group", "search", "pattern", "str"],
      "notes": [
        "Pins the bound Pattern.search named-group metadata for the same tiny literal capture path."
      ]
    }
  ]
}
