MANIFEST = {
  "schema_version": 1,
  "manifest_id": "grouped-match-workflows",
  "layer": "match_behavior",
  "suite_id": "match.grouped",
  "defaults": {
    "text_model": "str"
  },
  "cases": [
    {
      "id": "grouped-module-search-single-capture-str",
      "operation": "module_call",
      "family": "single_capture_module_workflow",
      "helper": "search",
      "args": ["(abc)", "zzabczz"],
      "categories": ["grouped", "search", "capture", "module", "str"],
      "notes": [
        "Pins grouped literal module search capture metadata including group(1), groups(), span(1), and lastindex."
      ]
    },
    {
      "id": "grouped-module-fullmatch-single-capture-str",
      "operation": "module_call",
      "family": "single_capture_module_workflow",
      "helper": "fullmatch",
      "args": ["(abc)", "abc"],
      "categories": ["grouped", "fullmatch", "capture", "module", "str"],
      "notes": [
        "Mirrors the grouped single-capture module path on an exact fullmatch."
      ]
    },
    {
      "id": "grouped-pattern-search-single-capture-str",
      "operation": "pattern_call",
      "family": "single_capture_pattern_workflow",
      "pattern": "(abc)",
      "helper": "search",
      "args": ["zzabczz"],
      "categories": ["grouped", "search", "capture", "pattern", "str"],
      "notes": [
        "Pins the bound Pattern.search grouped capture payload for the supported single-capture literal slice."
      ]
    },
    {
      "id": "grouped-pattern-match-single-capture-str",
      "operation": "pattern_call",
      "family": "single_capture_pattern_workflow",
      "pattern": "(abc)",
      "helper": "match",
      "args": ["abczz"],
      "categories": ["grouped", "match", "capture", "pattern", "str"],
      "notes": [
        "Pins the anchored Pattern.match grouped capture payload for the supported single-capture literal slice."
      ]
    },
    {
      "id": "grouped-module-fullmatch-two-capture-gap-str",
      "operation": "module_call",
      "family": "numbered_capture_gap_workflow",
      "helper": "fullmatch",
      "args": ["(ab)(c)", "abc"],
      "categories": ["grouped", "fullmatch", "capture", "module", "str", "gap"],
      "notes": [
        "Documents the first numbered multi-capture module gap as an honest unimplemented case instead of leaving it unpublished."
      ]
    },
    {
      "id": "grouped-pattern-fullmatch-two-capture-gap-str",
      "operation": "pattern_call",
      "family": "numbered_capture_gap_workflow",
      "pattern": "(ab)(c)",
      "helper": "fullmatch",
      "args": ["abc"],
      "categories": ["grouped", "fullmatch", "capture", "pattern", "str", "gap"],
      "notes": [
        "Documents the matching bound Pattern multi-capture gap before broader grouped-numbered behavior work lands."
      ]
    }
  ]
}
