MANIFEST = {
  "schema_version": 1,
  "manifest_id": "match-behavior-smoke",
  "layer": "match_behavior",
  "suite_id": "match.behavior",
  "defaults": {
    "operation": "module_call",
    "text_model": "str"
  },
  "cases": [
    {
      "id": "search-str-success-literal",
      "family": "search_result_shape",
      "helper": "search",
      "args": ["abc", "zzabczz"],
      "categories": ["search", "success", "literal", "str"],
      "notes": [
        "Captures a successful module-level literal search result with the first concrete Match scaffold."
      ]
    },
    {
      "id": "search-str-no-match",
      "family": "search_result_shape",
      "helper": "search",
      "args": ["abc", "zzz"],
      "categories": ["search", "no-match", "str"],
      "notes": [
        "Pins the no-match module-level search path as a None result."
      ]
    },
    {
      "id": "match-str-success-literal",
      "family": "match_result_shape",
      "helper": "match",
      "args": ["ab", "abbb"],
      "categories": ["match", "success", "literal", "str"],
      "notes": [
        "Captures a successful anchored literal match result."
      ]
    },
    {
      "id": "match-str-no-match",
      "family": "match_result_shape",
      "helper": "match",
      "args": ["abc", "zabc"],
      "categories": ["match", "no-match", "str"],
      "notes": [
        "Pins the no-match behavior for module-level match when the string starts later."
      ]
    },
    {
      "id": "fullmatch-str-success-literal",
      "family": "fullmatch_result_shape",
      "helper": "fullmatch",
      "args": ["123", "123"],
      "categories": ["fullmatch", "success", "literal", "str"],
      "notes": [
        "Exercises fullmatch truthiness and the minimal literal Match payload for str results."
      ]
    },
    {
      "id": "fullmatch-bytes-success-literal",
      "family": "fullmatch_result_shape",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "123"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "123"
        }
      ],
      "categories": ["fullmatch", "success", "literal", "bytes", "mirror"],
      "notes": [
        "Mirrors the str literal fullmatch success case with bytes payloads and bytes-typed group(0)."
      ]
    }
  ]
}
