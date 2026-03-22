import re

_INDEX_ONE = {"type": "indexlike", "value": 1}
_INDEX_TWO = {"type": "indexlike", "value": 2}
_INDEX_FOUR = {"type": "indexlike", "value": 4}
_INDEX_SEVEN = {"type": "indexlike", "value": 7}


MANIFEST = {
  "schema_version": 1,
  "manifest_id": "module-workflow-surface",
  "layer": "module_workflow",
  "suite_id": "module.workflow",
  "defaults": {
    "flags": 0,
    "text_model": "str"
  },
  "cases": [
    {
      "id": "workflow-compile-str-literal",
      "operation": "compile",
      "family": "compile_workflow",
      "pattern": "abc",
      "categories": ["workflow", "compile", "literal", "str"],
      "notes": [
        "Pins the literal-only module compile workflow on a supported str pattern."
      ]
    },
    {
      "id": "workflow-compile-str-anchored-literal",
      "operation": "compile",
      "family": "compile_workflow",
      "pattern": "^abc$",
      "categories": ["workflow", "compile", "literal", "anchored", "str"],
      "notes": [
        "Publishes the exact anchored module compile workflow that still blocks the adjacent module-boundary compile benchmark rows."
      ]
    },
    {
      "id": "workflow-compile-str-bounded-wildcard",
      "operation": "compile",
      "family": "compile_workflow",
      "pattern": "a.c",
      "categories": ["workflow", "compile", "wildcard", "bounded", "str"],
      "notes": [
        "Publishes the exact bounded wildcard default compile workflow already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-compile-str-bounded-wildcard-ignorecase",
      "operation": "compile",
      "family": "compile_workflow",
      "pattern": "a.c",
      "flags": 2,
      "categories": ["workflow", "compile", "wildcard", "bounded", "ignorecase", "str"],
      "notes": [
        "Publishes the exact bounded wildcard IGNORECASE compile workflow already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-compile-str-verbose-regression",
      "operation": "compile",
      "family": "compile_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 72,
      "categories": ["workflow", "compile", "verbose", "multiline", "regression", "str"],
      "notes": [
        "Publishes the exact verbose module compile workflow that anchors the adjacent regression benchmark row without broadening into cache-state coverage."
      ]
    },
    {
      "id": "workflow-compile-str-multiline-regression",
      "operation": "compile",
      "family": "compile_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 8,
      "categories": ["workflow", "compile", "multiline", "regression", "str"],
      "notes": [
        "Publishes the exact multiline-only module compile neighbor beside the shared verbose regression rows without broadening into execution or cache-state coverage."
      ]
    },
    {
      "id": "workflow-compile-bytes-verbose-regression",
      "operation": "compile",
      "family": "compile_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 72,
      "text_model": "bytes",
      "categories": ["workflow", "compile", "verbose", "multiline", "regression", "bytes"],
      "notes": [
        "Publishes the bytes sibling of the exact verbose module compile workflow without broadening into additional bytes-only variants."
      ]
    },
    {
      "id": "workflow-compile-bytes-multiline-regression",
      "operation": "compile",
      "family": "compile_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 8,
      "text_model": "bytes",
      "categories": ["workflow", "compile", "multiline", "regression", "bytes"],
      "notes": [
        "Publishes the bytes multiline-only compile neighbor beside the shared regression rows without broadening into execution or cache-state coverage."
      ]
    },
    {
      "id": "workflow-compile-bytes-literal",
      "operation": "compile",
      "family": "compile_workflow",
      "pattern": "abc",
      "text_model": "bytes",
      "categories": ["workflow", "compile", "literal", "bytes"],
      "notes": [
        "Mirrors the supported compile workflow for bytes payloads."
      ]
    },
    {
      "id": "workflow-pattern-search-str-bounded-wildcard-ignorecase",
      "operation": "pattern_call",
      "family": "bound_search_workflow",
      "pattern": "a.c",
      "flags": 2,
      "helper": "search",
      "args": ["zaBczz", 1, 5],
      "categories": ["workflow", "search", "wildcard", "bounded", "ignorecase", "str"],
      "notes": [
        "Publishes the exact bound Pattern.search IGNORECASE workflow already anchored on the shared bounded wildcard owner path."
      ]
    },
    {
      "id": "workflow-pattern-match-str-bounded-wildcard",
      "operation": "pattern_call",
      "family": "bound_match_workflow",
      "pattern": "a.c",
      "helper": "match",
      "args": ["zabcaxc", 1, 4],
      "categories": ["workflow", "match", "wildcard", "bounded", "str"],
      "notes": [
        "Publishes the exact bound Pattern.match workflow already anchored on the shared bounded wildcard owner path."
      ]
    },
    {
      "id": "workflow-pattern-fullmatch-str-bounded-wildcard",
      "operation": "pattern_call",
      "family": "bound_fullmatch_workflow",
      "pattern": "a.c",
      "helper": "fullmatch",
      "args": ["zaxcz", 1, 4],
      "categories": ["workflow", "fullmatch", "wildcard", "bounded", "str"],
      "notes": [
        "Publishes the exact bound Pattern.fullmatch workflow already anchored on the shared bounded wildcard owner path."
      ]
    },
    {
      "id": "workflow-pattern-findall-str-bounded-wildcard",
      "operation": "pattern_call",
      "family": "bound_findall_workflow",
      "pattern": "a.c",
      "helper": "findall",
      "args": ["zabcaxcz", 1, 7],
      "categories": ["workflow", "findall", "wildcard", "bounded", "str"],
      "notes": [
        "Publishes the exact bound Pattern.findall workflow already anchored on the shared bounded wildcard owner path."
      ]
    },
    {
      "id": "workflow-pattern-finditer-str-bounded-wildcard",
      "operation": "pattern_call",
      "family": "bound_finditer_workflow",
      "pattern": "a.c",
      "helper": "finditer",
      "args": ["zabcaxcx", 1, 7],
      "categories": ["workflow", "finditer", "wildcard", "bounded", "str"],
      "notes": [
        "Publishes the exact bound Pattern.finditer workflow already anchored on the shared bounded wildcard owner path."
      ]
    },
    {
      "id": "workflow-pattern-search-str-bounded-wildcard-endpos-miss",
      "operation": "pattern_call",
      "family": "bound_search_workflow",
      "pattern": "a.c",
      "helper": "search",
      "args": ["zabc", 1, 3],
      "categories": ["workflow", "search", "wildcard", "bounded", "str", "miss"],
      "notes": [
        "Publishes the exact bounded endpos miss Pattern.search workflow already anchored on the shared bounded wildcard owner path."
      ]
    },
    {
      "id": "workflow-pattern-search-str-verbose-regression",
      "operation": "pattern_call",
      "family": "bound_search_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 72,
      "helper": "search",
      "args": ["prefix\nENV_VAR=ABCD\nsuffix"],
      "categories": ["workflow", "search", "verbose", "multiline", "regression", "str"],
      "notes": [
        "Publishes the bound Pattern.search regression workflow anchored to the shared verbose compile family."
      ]
    },
    {
      "id": "workflow-pattern-search-str-verbose-regression-digits",
      "operation": "pattern_call",
      "family": "bound_search_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 72,
      "helper": "search",
      "args": ["prefix\nENV_VAR = 123\nsuffix"],
      "categories": ["workflow", "search", "verbose", "multiline", "regression", "str"],
      "notes": [
        "Publishes the remaining positive bound Pattern.search verbose regression workflow anchored to the shared verbose compile family."
      ]
    },
    {
      "id": "workflow-pattern-search-str-verbose-regression-too-many-digits",
      "operation": "pattern_call",
      "family": "bound_search_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 72,
      "helper": "search",
      "args": ["prefix\nENV_VAR = 12345\nsuffix"],
      "categories": ["workflow", "search", "verbose", "multiline", "regression", "str", "miss"],
      "notes": [
        "Publishes the remaining miss-path bound Pattern.search verbose regression workflow anchored to the shared verbose compile family."
      ]
    },
    {
      "id": "workflow-pattern-search-bytes-verbose-regression",
      "operation": "pattern_call",
      "family": "bound_search_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 72,
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "prefix\nENV_VAR=ABCD\nsuffix"
        }
      ],
      "categories": ["workflow", "search", "verbose", "multiline", "regression", "bytes"],
      "notes": [
        "Publishes the positive bytes bound Pattern.search verbose regression workflow anchored to the shared verbose compile family."
      ]
    },
    {
      "id": "workflow-pattern-search-bytes-verbose-regression-digits",
      "operation": "pattern_call",
      "family": "bound_search_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 72,
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "prefix\nENV_VAR = 123\nsuffix"
        }
      ],
      "categories": ["workflow", "search", "verbose", "multiline", "regression", "bytes"],
      "notes": [
        "Publishes the remaining positive bytes bound Pattern.search verbose regression workflow anchored to the shared verbose compile family."
      ]
    },
    {
      "id": "workflow-pattern-search-bytes-verbose-regression-too-many-digits",
      "operation": "pattern_call",
      "family": "bound_search_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 72,
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "prefix\nENV_VAR = 12345\nsuffix"
        }
      ],
      "categories": ["workflow", "search", "verbose", "multiline", "regression", "bytes", "miss"],
      "notes": [
        "Publishes the remaining miss-path bytes bound Pattern.search verbose regression workflow anchored to the shared verbose compile family."
      ]
    },
    {
      "id": "workflow-pattern-fullmatch-str-verbose-regression",
      "operation": "pattern_call",
      "family": "bound_fullmatch_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 72,
      "helper": "fullmatch",
      "args": ["ENV_VAR = 123"],
      "categories": ["workflow", "fullmatch", "verbose", "multiline", "regression", "str"],
      "notes": [
        "Publishes the bound Pattern.fullmatch regression workflow anchored to the shared verbose compile family."
      ]
    },
    {
      "id": "workflow-pattern-fullmatch-str-verbose-regression-alpha",
      "operation": "pattern_call",
      "family": "bound_fullmatch_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 72,
      "helper": "fullmatch",
      "args": ["ENV_VAR   =   ABCD"],
      "categories": ["workflow", "fullmatch", "verbose", "multiline", "regression", "str"],
      "notes": [
        "Publishes the remaining positive bound Pattern.fullmatch verbose regression workflow anchored to the shared verbose compile family."
      ]
    },
    {
      "id": "workflow-pattern-fullmatch-str-verbose-regression-lowercase-key",
      "operation": "pattern_call",
      "family": "bound_fullmatch_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 72,
      "helper": "fullmatch",
      "args": ["env_var = 123"],
      "categories": ["workflow", "fullmatch", "verbose", "multiline", "regression", "str", "miss"],
      "notes": [
        "Publishes the remaining miss-path bound Pattern.fullmatch verbose regression workflow anchored to the shared verbose compile family."
      ]
    },
    {
      "id": "workflow-pattern-fullmatch-bytes-verbose-regression",
      "operation": "pattern_call",
      "family": "bound_fullmatch_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 72,
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "ENV_VAR = 123"
        }
      ],
      "categories": ["workflow", "fullmatch", "verbose", "multiline", "regression", "bytes"],
      "notes": [
        "Publishes the positive bytes bound Pattern.fullmatch verbose regression workflow anchored to the shared verbose compile family."
      ]
    },
    {
      "id": "workflow-pattern-fullmatch-bytes-verbose-regression-alpha",
      "operation": "pattern_call",
      "family": "bound_fullmatch_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 72,
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "ENV_VAR   =   ABCD"
        }
      ],
      "categories": ["workflow", "fullmatch", "verbose", "multiline", "regression", "bytes"],
      "notes": [
        "Publishes the remaining positive bytes bound Pattern.fullmatch verbose regression workflow anchored to the shared verbose compile family."
      ]
    },
    {
      "id": "workflow-pattern-fullmatch-bytes-verbose-regression-lowercase-key",
      "operation": "pattern_call",
      "family": "bound_fullmatch_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 72,
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "env_var = 123"
        }
      ],
      "categories": ["workflow", "fullmatch", "verbose", "multiline", "regression", "bytes", "miss"],
      "notes": [
        "Publishes the remaining miss-path bytes bound Pattern.fullmatch verbose regression workflow anchored to the shared verbose compile family."
      ]
    },
    {
      "id": "workflow-pattern-search-str",
      "operation": "pattern_call",
      "family": "bound_search_workflow",
      "pattern": "abc",
      "helper": "search",
      "args": ["zzabczz"],
      "categories": ["workflow", "search", "literal", "str"],
      "notes": [
        "Compiles through the module entry point and exercises the bound Pattern.search path."
      ]
    },
    {
      "id": "workflow-pattern-match-str",
      "operation": "pattern_call",
      "family": "bound_match_workflow",
      "pattern": "abc",
      "helper": "match",
      "args": ["abcdef"],
      "categories": ["workflow", "match", "literal", "str"],
      "notes": [
        "Pins the anchored bound Pattern.match workflow for supported literal input."
      ]
    },
    {
      "id": "workflow-pattern-fullmatch-bytes",
      "operation": "pattern_call",
      "family": "bound_fullmatch_workflow",
      "pattern": "123",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "123"
        }
      ],
      "categories": ["workflow", "fullmatch", "literal", "bytes"],
      "notes": [
        "Mirrors the end-to-end fullmatch workflow with bytes payloads."
      ]
    },
    {
      "id": "workflow-pattern-search-str-pos-keyword",
      "operation": "pattern_call",
      "family": "bound_search_workflow",
      "pattern": "abc",
      "helper": "search",
      "args": ["zabcabc"],
      "kwargs": {
        "pos": 2
      },
      "categories": ["workflow", "search", "literal", "keyword", "pos", "str"],
      "notes": [
        "Publishes the representative bound Pattern.search pos= keyword workflow without widening into bool or __index__ variants."
      ]
    },
    {
      "id": "workflow-pattern-search-str-bool-endpos-keyword",
      "operation": "pattern_call",
      "family": "bound_search_workflow",
      "pattern": "z",
      "helper": "search",
      "args": ["zabcabc"],
      "kwargs": {
        "endpos": True
      },
      "categories": ["workflow", "search", "literal", "keyword", "endpos", "bool", "str"],
      "notes": [
        "Publishes the adjacent bound Pattern.search endpos= bool workflow without widening into match/fullmatch or collection keyword variants."
      ]
    },
    {
      "id": "workflow-pattern-search-bytes-endpos-keyword",
      "operation": "pattern_call",
      "family": "bound_search_workflow",
      "pattern": "abc",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabc"
        }
      ],
      "kwargs": {
        "endpos": 4
      },
      "categories": ["workflow", "search", "literal", "keyword", "endpos", "bytes"],
      "notes": [
        "Publishes the adjacent bound Pattern.search endpos= keyword workflow on bytes payloads without widening into other bytes keyword variants."
      ]
    },
    {
      "id": "workflow-pattern-search-str-pos-indexlike",
      "operation": "pattern_call",
      "family": "bound_search_workflow",
      "pattern": "abc",
      "helper": "search",
      "args": ["zabcabc"],
      "kwargs": {
        "pos": _INDEX_TWO
      },
      "categories": ["workflow", "search", "literal", "keyword", "pos", "indexlike", "str"],
      "notes": [
        "Publishes the adjacent bound Pattern.search pos= __index__ workflow without widening into the remaining Pattern.search window keyword rows."
      ]
    },
    {
      "id": "workflow-pattern-search-bytes-endpos-indexlike",
      "operation": "pattern_call",
      "family": "bound_search_workflow",
      "pattern": "abc",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabc"
        }
      ],
      "kwargs": {
        "endpos": _INDEX_FOUR
      },
      "categories": ["workflow", "search", "literal", "keyword", "endpos", "indexlike", "bytes"],
      "notes": [
        "Publishes the adjacent bound Pattern.search endpos= __index__ workflow on bytes payloads without widening into the remaining Pattern.search window keyword rows."
      ]
    },
    {
      "id": "workflow-pattern-match-str-pos-keyword",
      "operation": "pattern_call",
      "family": "bound_match_workflow",
      "pattern": "abc",
      "helper": "match",
      "args": ["zabcabc"],
      "kwargs": {
        "pos": 1
      },
      "categories": ["workflow", "match", "literal", "keyword", "pos", "str"],
      "notes": [
        "Publishes the representative bound Pattern.match pos= keyword workflow without widening into bool or __index__ variants."
      ]
    },
    {
      "id": "workflow-pattern-match-str-bool-pos-keyword",
      "operation": "pattern_call",
      "family": "bound_match_workflow",
      "pattern": "abc",
      "helper": "match",
      "args": ["zabcabc"],
      "kwargs": {
        "pos": True
      },
      "categories": ["workflow", "match", "literal", "keyword", "pos", "bool", "str"],
      "notes": [
        "Publishes the adjacent bound Pattern.match pos= bool workflow without widening into the remaining Pattern.match keyword rows."
      ]
    },
    {
      "id": "workflow-pattern-match-bytes-window-indexlike",
      "operation": "pattern_call",
      "family": "bound_match_workflow",
      "pattern": "abc",
      "helper": "match",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabc"
        }
      ],
      "kwargs": {
        "pos": _INDEX_ONE,
        "endpos": _INDEX_FOUR
      },
      "categories": ["workflow", "match", "literal", "keyword", "window", "indexlike", "bytes"],
      "notes": [
        "Publishes the remaining bound Pattern.match pos=/endpos= __index__ workflow on bytes payloads without widening into the already published str keyword rows or neighboring bound helper slices."
      ]
    },
    {
      "id": "workflow-pattern-fullmatch-bytes-window-keyword",
      "operation": "pattern_call",
      "family": "bound_fullmatch_workflow",
      "pattern": "abc",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabc"
        }
      ],
      "kwargs": {
        "pos": 1,
        "endpos": 4
      },
      "categories": ["workflow", "fullmatch", "literal", "keyword", "window", "bytes"],
      "notes": [
        "Publishes the representative bound Pattern.fullmatch pos=/endpos= keyword workflow on bytes payloads without widening into bool or __index__ variants."
      ]
    },
    {
      "id": "workflow-pattern-fullmatch-bytes-window-indexlike",
      "operation": "pattern_call",
      "family": "bound_fullmatch_workflow",
      "pattern": "abc",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabc"
        }
      ],
      "kwargs": {
        "pos": _INDEX_ONE,
        "endpos": _INDEX_FOUR
      },
      "categories": ["workflow", "fullmatch", "literal", "keyword", "window", "indexlike", "bytes"],
      "notes": [
        "Publishes the adjacent bound Pattern.fullmatch pos=/endpos= __index__ workflow on bytes payloads without widening into the remaining Pattern.fullmatch keyword rows."
      ]
    },
    {
      "id": "workflow-pattern-findall-str-window-keyword",
      "operation": "pattern_call",
      "family": "bound_findall_workflow",
      "pattern": "abc",
      "helper": "findall",
      "args": ["zabcabcz"],
      "kwargs": {
        "pos": 1,
        "endpos": 7
      },
      "categories": ["workflow", "findall", "literal", "keyword", "window", "str"],
      "notes": [
        "Publishes the representative bound Pattern.findall pos=/endpos= keyword workflow without widening into bool or __index__ variants."
      ]
    },
    {
      "id": "workflow-pattern-findall-str-window-indexlike",
      "operation": "pattern_call",
      "family": "bound_findall_workflow",
      "pattern": "abc",
      "helper": "findall",
      "args": ["zabcabcabcz"],
      "kwargs": {
        "pos": _INDEX_ONE,
        "endpos": _INDEX_SEVEN
      },
      "categories": ["workflow", "findall", "literal", "keyword", "window", "indexlike", "str"],
      "notes": [
        "Publishes the adjacent bound Pattern.findall pos=/endpos= __index__ workflow without widening into the remaining Pattern.findall keyword rows."
      ]
    },
    {
      "id": "workflow-pattern-findall-str-bool-window-keyword",
      "operation": "pattern_call",
      "family": "bound_findall_workflow",
      "pattern": "abc",
      "helper": "findall",
      "args": ["zabcabcz"],
      "kwargs": {
        "pos": True,
        "endpos": 7
      },
      "categories": ["workflow", "findall", "literal", "keyword", "window", "bool", "str"],
      "notes": [
        "Publishes the adjacent bound Pattern.findall bool pos=/endpos= keyword workflow without widening into Pattern.split or replacement keyword rows."
      ]
    },
    {
      "id": "workflow-pattern-finditer-bytes-window-keyword",
      "operation": "pattern_call",
      "family": "bound_finditer_workflow",
      "pattern": "abc",
      "helper": "finditer",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabcz"
        }
      ],
      "kwargs": {
        "pos": 1,
        "endpos": 7
      },
      "categories": ["workflow", "finditer", "literal", "keyword", "window", "bytes"],
      "notes": [
        "Publishes the representative bound Pattern.finditer pos=/endpos= keyword workflow on bytes payloads without widening into bool or __index__ variants."
      ]
    },
    {
      "id": "workflow-pattern-finditer-bytes-window-indexlike",
      "operation": "pattern_call",
      "family": "bound_finditer_workflow",
      "pattern": "abc",
      "helper": "finditer",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabcabcz"
        }
      ],
      "kwargs": {
        "pos": _INDEX_ONE,
        "endpos": _INDEX_SEVEN
      },
      "categories": ["workflow", "finditer", "literal", "keyword", "window", "indexlike", "bytes"],
      "notes": [
        "Publishes the adjacent bound Pattern.finditer pos=/endpos= __index__ workflow on bytes payloads without widening into the remaining Pattern.finditer keyword rows."
      ]
    },
    {
      "id": "workflow-pattern-finditer-bytes-bool-window-keyword",
      "operation": "pattern_call",
      "family": "bound_finditer_workflow",
      "pattern": "abc",
      "helper": "finditer",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabcz"
        }
      ],
      "kwargs": {
        "pos": True,
        "endpos": 7
      },
      "categories": ["workflow", "finditer", "literal", "keyword", "window", "bool", "bytes"],
      "notes": [
        "Publishes the adjacent bound Pattern.finditer bool pos=/endpos= keyword workflow on bytes payloads without widening into Pattern.split or replacement keyword rows."
      ]
    },
    {
      "id": "workflow-pattern-split-str-maxsplit-keyword",
      "operation": "pattern_call",
      "family": "bound_split_workflow",
      "pattern": "abc",
      "helper": "split",
      "args": ["zabczabc"],
      "kwargs": {
        "maxsplit": 1
      },
      "categories": ["workflow", "split", "literal", "keyword", "maxsplit", "str"],
      "notes": [
        "Publishes the representative bound Pattern.split maxsplit= keyword workflow without widening into __index__ or replacement keyword rows."
      ]
    },
    {
      "id": "workflow-pattern-split-str-maxsplit-indexlike",
      "operation": "pattern_call",
      "family": "bound_split_workflow",
      "pattern": "abc",
      "helper": "split",
      "args": ["zabcabcabc"],
      "kwargs": {
        "maxsplit": _INDEX_TWO
      },
      "categories": ["workflow", "split", "literal", "keyword", "maxsplit", "indexlike", "str"],
      "notes": [
        "Publishes the adjacent bound Pattern.split maxsplit=__index__ workflow without widening into the remaining Pattern replacement keyword rows."
      ]
    },
    {
      "id": "workflow-pattern-split-str-maxsplit-bool-true",
      "operation": "pattern_call",
      "family": "bound_split_workflow",
      "pattern": "abc",
      "helper": "split",
      "args": ["zabczabc"],
      "kwargs": {
        "maxsplit": True
      },
      "categories": ["workflow", "split", "literal", "keyword", "maxsplit", "bool", "str"],
      "notes": [
        "Publishes the bounded Pattern.split maxsplit=True workflow alongside the adjacent replacement bool keyword rows."
      ]
    },
    {
      "id": "workflow-pattern-sub-count-keyword-bytes",
      "operation": "pattern_call",
      "family": "bound_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabc"
        }
      ],
      "kwargs": {
        "count": 1
      },
      "categories": ["workflow", "sub", "literal", "keyword", "count", "bytes"],
      "notes": [
        "Publishes the representative bound Pattern.sub count= keyword workflow on bytes payloads without widening into __index__ or Pattern.subn keyword rows."
      ]
    },
    {
      "id": "workflow-pattern-sub-count-indexlike-bytes",
      "operation": "pattern_call",
      "family": "bound_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabcabc"
        }
      ],
      "kwargs": {
        "count": _INDEX_TWO
      },
      "categories": ["workflow", "sub", "literal", "keyword", "count", "indexlike", "bytes"],
      "notes": [
        "Publishes the adjacent bound Pattern.sub count=__index__ workflow on bytes payloads without widening into the remaining Pattern replacement keyword rows."
      ]
    },
    {
      "id": "workflow-pattern-sub-count-bool-false-bytes",
      "operation": "pattern_call",
      "family": "bound_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabc"
        }
      ],
      "kwargs": {
        "count": False
      },
      "categories": ["workflow", "sub", "literal", "keyword", "count", "bool", "bytes"],
      "notes": [
        "Publishes the bounded Pattern.sub count=False workflow on bytes payloads alongside the adjacent Pattern.subn bool keyword row."
      ]
    },
    {
      "id": "workflow-pattern-subn-count-keyword-str",
      "operation": "pattern_call",
      "family": "bound_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "args": ["x", "abcabc"],
      "kwargs": {
        "count": 1
      },
      "categories": ["workflow", "subn", "literal", "keyword", "count", "str"],
      "notes": [
        "Publishes the representative bound Pattern.subn count= keyword workflow on str payloads without widening into __index__ neighbors beyond this quartet."
      ]
    },
    {
      "id": "workflow-pattern-subn-count-indexlike-str",
      "operation": "pattern_call",
      "family": "bound_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "args": ["x", "abcabcabc"],
      "kwargs": {
        "count": _INDEX_TWO
      },
      "categories": ["workflow", "subn", "literal", "keyword", "count", "indexlike", "str"],
      "notes": [
        "Publishes the adjacent bound Pattern.subn count=__index__ workflow on str payloads without widening into compiled-pattern module keyword rows."
      ]
    },
    {
      "id": "workflow-pattern-subn-count-bool-true-str",
      "operation": "pattern_call",
      "family": "bound_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "args": ["x", "abcabc"],
      "kwargs": {
        "count": True
      },
      "categories": ["workflow", "subn", "literal", "keyword", "count", "bool", "str"],
      "notes": [
        "Publishes the bounded Pattern.subn count=True workflow on str payloads alongside the adjacent Pattern.sub bool keyword row."
      ]
    },
    {
      "id": "workflow-pattern-search-str-pos-indexlike-positional",
      "operation": "pattern_call",
      "family": "bound_search_workflow",
      "pattern": "abc",
      "helper": "search",
      "args": ["zabcabc", _INDEX_TWO],
      "categories": ["workflow", "search", "literal", "pos", "str"],
      "notes": [
        "Publishes the bound Pattern.search positional __index__ workflow already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-pattern-search-bytes-endpos-indexlike-positional",
      "operation": "pattern_call",
      "family": "bound_search_workflow",
      "pattern": "abc",
      "helper": "search",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabc"
        },
        0,
        _INDEX_FOUR
      ],
      "categories": ["workflow", "search", "literal", "endpos", "bytes"],
      "notes": [
        "Publishes the bytes bound Pattern.search positional endpos __index__ workflow already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-pattern-match-bytes-window-indexlike-positional",
      "operation": "pattern_call",
      "family": "bound_match_workflow",
      "pattern": "abc",
      "helper": "match",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabc"
        },
        _INDEX_ONE,
        _INDEX_FOUR
      ],
      "categories": ["workflow", "match", "literal", "window", "bytes"],
      "notes": [
        "Publishes the bound Pattern.match positional pos/endpos __index__ workflow on bytes payloads already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-pattern-fullmatch-bytes-window-indexlike-positional",
      "operation": "pattern_call",
      "family": "bound_fullmatch_workflow",
      "pattern": "abc",
      "helper": "fullmatch",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabc"
        },
        _INDEX_ONE,
        _INDEX_FOUR
      ],
      "categories": ["workflow", "fullmatch", "literal", "window", "bytes"],
      "notes": [
        "Publishes the bound Pattern.fullmatch positional pos/endpos __index__ workflow on bytes payloads already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-pattern-findall-str-window-indexlike-positional",
      "operation": "pattern_call",
      "family": "bound_findall_workflow",
      "pattern": "abc",
      "helper": "findall",
      "args": ["zabcabcabcz", _INDEX_ONE, _INDEX_SEVEN],
      "categories": ["workflow", "findall", "literal", "window", "str"],
      "notes": [
        "Publishes the bound Pattern.findall positional pos/endpos __index__ workflow already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-pattern-finditer-bytes-window-indexlike-positional",
      "operation": "pattern_call",
      "family": "bound_finditer_workflow",
      "pattern": "abc",
      "helper": "finditer",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabcabcz"
        },
        _INDEX_ONE,
        _INDEX_SEVEN
      ],
      "categories": ["workflow", "finditer", "literal", "window", "bytes"],
      "notes": [
        "Publishes the bound Pattern.finditer positional pos/endpos __index__ workflow on bytes payloads already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-pattern-split-str-maxsplit-indexlike-positional",
      "operation": "pattern_call",
      "family": "bound_split_workflow",
      "pattern": "abc",
      "helper": "split",
      "args": ["zabcabcabc", _INDEX_TWO],
      "categories": ["workflow", "split", "literal", "maxsplit", "str"],
      "notes": [
        "Publishes the bound Pattern.split positional maxsplit __index__ workflow already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-pattern-sub-count-indexlike-positional-bytes",
      "operation": "pattern_call",
      "family": "bound_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabcabc"
        },
        _INDEX_TWO
      ],
      "categories": ["workflow", "sub", "literal", "count", "bytes"],
      "notes": [
        "Publishes the bound Pattern.sub positional count __index__ workflow on bytes payloads already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-pattern-subn-count-indexlike-positional-str",
      "operation": "pattern_call",
      "family": "bound_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "args": ["x", "abcabcabc", _INDEX_TWO],
      "categories": ["workflow", "subn", "literal", "count", "str"],
      "notes": [
        "Publishes the bound Pattern.subn positional count __index__ workflow already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-cache-hit-str",
      "operation": "cache_workflow",
      "family": "cache_workflow",
      "pattern": "cache-me",
      "categories": ["workflow", "cache", "str"],
      "notes": [
        "Observes that repeated supported compile() calls reuse the cached compiled object."
      ]
    },
    {
      "id": "workflow-cache-hit-bytes",
      "operation": "cache_workflow",
      "family": "cache_workflow",
      "pattern": "cache-me",
      "text_model": "bytes",
      "categories": ["workflow", "cache", "bytes"],
      "notes": [
        "Mirrors the compile cache-hit observation for supported bytes patterns."
      ]
    },
    {
      "id": "workflow-purge-reset-str",
      "operation": "purge_workflow",
      "family": "purge_workflow",
      "pattern": "purge-me",
      "categories": ["workflow", "cache", "purge", "str"],
      "notes": [
        "Pins that purge() clears the observable compile cache before the next supported compile."
      ]
    },
    {
      "id": "workflow-module-search-str-bounded-wildcard-ignorecase",
      "operation": "module_call",
      "family": "module_search_workflow",
      "pattern": "a.c",
      "flags": 2,
      "helper": "search",
      "args": ["ABC"],
      "categories": ["workflow", "search", "wildcard", "bounded", "ignorecase", "str"],
      "notes": [
        "Publishes the exact raw module-level search() IGNORECASE workflow already anchored on the shared bounded wildcard owner path."
      ]
    },
    {
      "id": "workflow-module-match-str-bounded-wildcard-miss",
      "operation": "module_call",
      "family": "module_match_workflow",
      "pattern": "a.c",
      "helper": "match",
      "args": ["zabc"],
      "categories": ["workflow", "match", "wildcard", "bounded", "str", "miss"],
      "notes": [
        "Publishes the exact raw module-level match() miss workflow already anchored on the shared bounded wildcard owner path."
      ]
    },
    {
      "id": "workflow-module-fullmatch-str-bounded-wildcard",
      "operation": "module_call",
      "family": "module_fullmatch_workflow",
      "pattern": "a.c",
      "helper": "fullmatch",
      "args": ["abc"],
      "categories": ["workflow", "fullmatch", "wildcard", "bounded", "str"],
      "notes": [
        "Publishes the exact raw module-level fullmatch() workflow already anchored on the shared bounded wildcard owner path."
      ]
    },
    {
      "id": "workflow-module-search-flags-keyword-str",
      "operation": "module_call",
      "family": "module_search_workflow",
      "pattern": "abc",
      "helper": "search",
      "args": ["zAbc"],
      "kwargs": {
        "flags": 2
      },
      "categories": ["workflow", "flag", "ignorecase", "literal", "search", "str"],
      "notes": [
        "Publishes the first raw module-level search() flags= keyword workflow already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-match-flags-keyword-bytes",
      "operation": "module_call",
      "family": "module_match_workflow",
      "pattern": "abc",
      "helper": "match",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "Abc"
        }
      ],
      "kwargs": {
        "flags": 2
      },
      "categories": ["workflow", "flag", "ignorecase", "literal", "match", "bytes"],
      "notes": [
        "Publishes the first raw module-level match() flags= keyword workflow on bytes payloads without widening into the remaining module keyword helper ladder."
      ]
    },
    {
      "id": "workflow-module-fullmatch-flags-keyword-str",
      "operation": "module_call",
      "family": "module_fullmatch_workflow",
      "pattern": "abc",
      "helper": "fullmatch",
      "args": ["Abc"],
      "kwargs": {
        "flags": 2
      },
      "categories": ["workflow", "flag", "ignorecase", "literal", "fullmatch", "str"],
      "notes": [
        "Publishes the adjacent raw module-level fullmatch() flags= keyword workflow already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-split-maxsplit-keyword-bytes",
      "operation": "module_call",
      "family": "module_split_workflow",
      "pattern": "abc",
      "helper": "split",
      "include_pattern_arg": True,
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabczabc"
        }
      ],
      "kwargs": {
        "maxsplit": 1
      },
      "categories": ["workflow", "split", "literal", "bytes", "maxsplit"],
      "notes": [
        "Publishes the adjacent raw module-level split() maxsplit= keyword workflow on bytes payloads without widening into the remaining module keyword helper ladder."
      ]
    },
    {
      "id": "workflow-module-split-maxsplit-indexlike-bytes",
      "operation": "module_call",
      "family": "module_split_workflow",
      "pattern": "abc",
      "helper": "split",
      "include_pattern_arg": True,
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabcabc"
        }
      ],
      "kwargs": {
        "maxsplit": _INDEX_TWO
      },
      "categories": ["workflow", "split", "literal", "bytes", "maxsplit"],
      "notes": [
        "Publishes the remaining raw module-level split() maxsplit=__index__ keyword workflow on bytes payloads already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-split-maxsplit-bool-false-bytes",
      "operation": "module_call",
      "family": "module_split_workflow",
      "pattern": "abc",
      "helper": "split",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabc"
        }
      ],
      "kwargs": {
        "maxsplit": False
      },
      "categories": ["workflow", "split", "literal", "bytes", "maxsplit", "bool"],
      "notes": [
        "Publishes the bounded raw module-level split() maxsplit=False keyword workflow on bytes payloads alongside the adjacent raw module replacement bool rows."
      ]
    },
    {
      "id": "workflow-module-sub-count-keyword-str",
      "operation": "module_call",
      "family": "module_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "args": ["x", "abcabc"],
      "kwargs": {
        "count": 1
      },
      "categories": ["workflow", "sub", "literal", "str", "count"],
      "notes": [
        "Publishes the adjacent raw module-level sub() count= keyword workflow already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-sub-count-indexlike-str",
      "operation": "module_call",
      "family": "module_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "args": ["x", "abcabcabc"],
      "kwargs": {
        "count": _INDEX_TWO
      },
      "categories": ["workflow", "sub", "literal", "str", "count"],
      "notes": [
        "Publishes the adjacent raw module-level sub() count=__index__ keyword workflow already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-sub-count-bool-false-str",
      "operation": "module_call",
      "family": "module_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "args": ["x", "abcabc"],
      "kwargs": {
        "count": False
      },
      "categories": ["workflow", "sub", "literal", "str", "count", "bool"],
      "notes": [
        "Publishes the raw module-level sub() count=False keyword complement beside the already published count=True spelling on the shared module-workflow owner path without dumping the broader coercion matrix."
      ]
    },
    {
      "id": "workflow-module-sub-count-bool-true-str",
      "operation": "module_call",
      "family": "module_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "args": ["x", "abcabc"],
      "kwargs": {
        "count": True
      },
      "categories": ["workflow", "sub", "literal", "str", "count", "bool"],
      "notes": [
        "Publishes the bounded raw module-level sub() count=True keyword workflow alongside the adjacent raw module bool-normalization rows."
      ]
    },
    {
      "id": "workflow-module-subn-count-keyword-bytes",
      "operation": "module_call",
      "family": "module_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabc"
        }
      ],
      "kwargs": {
        "count": 1
      },
      "categories": ["workflow", "subn", "literal", "bytes", "count"],
      "notes": [
        "Publishes the adjacent raw module-level subn() count= keyword workflow on bytes payloads without widening into the remaining module keyword helper ladder."
      ]
    },
    {
      "id": "workflow-module-subn-count-indexlike-bytes",
      "operation": "module_call",
      "family": "module_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabcabc"
        }
      ],
      "kwargs": {
        "count": _INDEX_TWO
      },
      "categories": ["workflow", "subn", "literal", "bytes", "count"],
      "notes": [
        "Publishes the adjacent raw module-level subn() count=__index__ keyword workflow on bytes payloads without widening into the remaining module keyword helper ladder."
      ]
    },
    {
      "id": "workflow-module-subn-count-bool-false-bytes",
      "operation": "module_call",
      "family": "module_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabc"
        }
      ],
      "kwargs": {
        "count": False
      },
      "categories": ["workflow", "subn", "literal", "bytes", "count", "bool"],
      "notes": [
        "Publishes the bounded raw module-level subn() count=False keyword workflow on bytes payloads alongside the adjacent raw module bool-normalization rows."
      ]
    },
    {
      "id": "workflow-module-subn-count-bool-true-bytes",
      "operation": "module_call",
      "family": "module_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabc"
        }
      ],
      "kwargs": {
        "count": True
      },
      "categories": ["workflow", "subn", "literal", "bytes", "count", "bool"],
      "notes": [
        "Publishes the raw module-level subn() count=True keyword complement beside the already published count=False spelling on the shared module-workflow owner path without dumping the broader coercion matrix."
      ]
    },
    {
      "id": "workflow-module-split-maxsplit-indexlike-positional-bytes",
      "operation": "module_call",
      "family": "module_split_workflow",
      "pattern": "abc",
      "helper": "split",
      "include_pattern_arg": True,
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabcabc"
        },
        _INDEX_TWO
      ],
      "categories": ["workflow", "split", "literal", "bytes", "maxsplit"],
      "notes": [
        "Publishes the raw module-level split() positional __index__ workflow on bytes payloads already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-sub-count-indexlike-positional-str",
      "operation": "module_call",
      "family": "module_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "include_pattern_arg": True,
      "args": ["x", "abcabcabc", _INDEX_TWO],
      "categories": ["workflow", "sub", "literal", "str", "count"],
      "notes": [
        "Publishes the raw module-level sub() positional __index__ workflow already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-subn-count-indexlike-positional-bytes",
      "operation": "module_call",
      "family": "module_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "include_pattern_arg": True,
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabcabc"
        },
        _INDEX_TWO
      ],
      "categories": ["workflow", "subn", "literal", "bytes", "count"],
      "notes": [
        "Publishes the raw module-level subn() positional __index__ workflow on bytes payloads already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-search-duplicate-flags-keyword",
      "operation": "module_call",
      "family": "module_search_workflow",
      "pattern": "abc",
      "helper": "search",
      "include_pattern_arg": True,
      "args": ["abc", 0],
      "kwargs": {
        "flags": 0
      },
      "categories": ["workflow", "search", "literal", "str", "flags", "duplicate-keyword"],
      "notes": [
        "Publishes the first raw module-level search() duplicate flags= keyword rejection already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-split-duplicate-maxsplit-keyword",
      "operation": "module_call",
      "family": "module_split_workflow",
      "pattern": "abc",
      "helper": "split",
      "include_pattern_arg": True,
      "args": ["abc", 1],
      "kwargs": {
        "maxsplit": 1
      },
      "categories": ["workflow", "split", "literal", "str", "maxsplit", "duplicate-keyword"],
      "notes": [
        "Publishes the first raw module-level split() duplicate maxsplit= keyword rejection already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-sub-duplicate-count-keyword",
      "operation": "module_call",
      "family": "module_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "include_pattern_arg": True,
      "args": ["x", "abc", 1],
      "kwargs": {
        "count": 1
      },
      "categories": ["workflow", "sub", "literal", "str", "count", "duplicate-keyword"],
      "notes": [
        "Publishes the first raw module-level sub() duplicate count= keyword rejection already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-fullmatch-unexpected-keyword",
      "operation": "module_call",
      "family": "module_fullmatch_workflow",
      "pattern": "abc",
      "helper": "fullmatch",
      "include_pattern_arg": True,
      "args": ["abc"],
      "kwargs": {
        "missing": 1
      },
      "categories": ["workflow", "fullmatch", "literal", "str", "unexpected-keyword"],
      "notes": [
        "Publishes the adjacent raw module-level fullmatch() unexpected keyword rejection already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-sub-unexpected-keyword",
      "operation": "module_call",
      "family": "module_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "include_pattern_arg": True,
      "args": ["x", "abc"],
      "kwargs": {
        "missing": 1
      },
      "categories": ["workflow", "sub", "literal", "str", "unexpected-keyword"],
      "notes": [
        "Publishes the adjacent raw module-level sub() unexpected keyword rejection already anchored on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-compile-str-compiled-pattern",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "abc",
      "helper": "compile",
      "use_compiled_pattern": True,
      "categories": ["workflow", "compile", "literal", "str", "compiled-pattern"],
      "notes": [
        "Publishes the exact literal str module-level compile() helper workflow that accepts a compiled pattern on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-compile-flags-noflag-str-compiled-pattern",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "abc",
      "helper": "compile",
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": re.NOFLAG
      },
      "categories": ["workflow", "compile", "literal", "str", "compiled-pattern", "flags", "noflag"],
      "notes": [
        "Publishes the compiled-pattern module-level literal str compile() explicit NOFLAG spelling on the shared owner path without broadening into the default, integer-zero, bool-false, named-group, or nonzero-flag rejection slices."
      ]
    },
    {
      "id": "workflow-module-compile-flags-int-zero-str-compiled-pattern",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "abc",
      "helper": "compile",
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": 0
      },
      "categories": ["workflow", "compile", "literal", "str", "compiled-pattern", "flags", "int-zero"],
      "notes": [
        "Publishes the explicit integer-zero compiled-pattern module-level compile() keyword neighbor on the shared module-workflow owner path without broadening into False or NOFLAG spellings."
      ]
    },
    {
      "id": "workflow-module-compile-flags-bool-false-str-compiled-pattern",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "abc",
      "helper": "compile",
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": False
      },
      "categories": ["workflow", "compile", "literal", "str", "compiled-pattern", "flags", "bool-false"],
      "notes": [
        "Publishes the explicit bool-false compiled-pattern module-level compile() keyword neighbor on the shared module-workflow owner path without broadening into integer-zero or NOFLAG spellings."
      ]
    },
    {
      "id": "workflow-module-compile-flags-ignorecase-str-compiled-pattern",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "abc",
      "helper": "compile",
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": 2
      },
      "categories": ["workflow", "compile", "literal", "str", "compiled-pattern", "flags", "ignorecase", "rejection"],
      "notes": [
        "Publishes the str literal explicit IGNORECASE compiled-pattern module-level compile() keyword rejection singleton on the shared module-workflow owner path without broadening into the default, integer-zero, bool-false, NOFLAG, bytes-side, or named-group rejection slices."
      ]
    },
    {
      "id": "workflow-module-compile-str-compiled-pattern-named-group",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "compile",
      "use_compiled_pattern": True,
      "categories": ["workflow", "compile", "named-group", "str", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent named-group str module-level compile() helper workflow that accepts a compiled pattern on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-compile-flags-noflag-str-compiled-pattern-named-group",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "compile",
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": re.NOFLAG
      },
      "categories": ["workflow", "compile", "named-group", "str", "compiled-pattern", "flags", "noflag"],
      "notes": [
        "Publishes the compiled-pattern module-level named-group compile() explicit NOFLAG spelling on the shared owner path without broadening into the default, integer-zero, bool-false, or nonzero-flag rejection slices."
      ]
    },
    {
      "id": "workflow-module-compile-flags-int-zero-str-compiled-pattern-named-group",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "compile",
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": 0
      },
      "categories": ["workflow", "compile", "named-group", "str", "compiled-pattern", "flags", "int-zero"],
      "notes": [
        "Publishes the compiled-pattern module-level named-group compile() explicit integer-zero flag singleton on the shared owner path without broadening into the default, bool-false, or NOFLAG spellings."
      ]
    },
    {
      "id": "workflow-module-compile-flags-bool-false-str-compiled-pattern-named-group",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "compile",
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": False
      },
      "categories": ["workflow", "compile", "named-group", "str", "compiled-pattern", "flags", "bool-false"],
      "notes": [
        "Publishes the compiled-pattern module-level named-group compile() explicit bool-false flag singleton on the shared owner path without broadening into the default, integer-zero, or NOFLAG spellings."
      ]
    },
    {
      "id": "workflow-module-compile-flags-ignorecase-str-compiled-pattern-named-group",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "compile",
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": 2
      },
      "categories": ["workflow", "compile", "named-group", "str", "compiled-pattern", "flags", "ignorecase", "rejection"],
      "notes": [
        "Publishes the str named-group explicit IGNORECASE compiled-pattern module-level compile() keyword rejection singleton on the shared module-workflow owner path without broadening into the default, integer-zero, bool-false, NOFLAG, or bytes-side rejection slices."
      ]
    },
    {
      "id": "workflow-module-search-str-compiled-pattern",
      "operation": "module_call",
      "family": "module_search_workflow",
      "pattern": "abc",
      "helper": "search",
      "use_compiled_pattern": True,
      "args": ["zabczz"],
      "categories": ["workflow", "search", "literal", "str", "compiled-pattern"],
      "notes": [
        "Publishes the first literal str module-level search() helper workflow that accepts a compiled pattern on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-search-str-compiled-pattern-on-bytes-string",
      "operation": "module_call",
      "family": "module_search_workflow",
      "pattern": "abc",
      "helper": "search",
      "text_model": "str",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abc"
        }
      ],
      "categories": ["workflow", "search", "literal", "str", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern search() wrong-text-model TypeError on the shared module-workflow owner path without widening into other helper mismatches."
      ]
    },
    {
      "id": "workflow-module-match-str-compiled-pattern",
      "operation": "module_call",
      "family": "module_match_workflow",
      "pattern": "abc",
      "helper": "match",
      "use_compiled_pattern": True,
      "args": ["abcdef"],
      "categories": ["workflow", "match", "literal", "str", "compiled-pattern"],
      "notes": [
        "Publishes the first literal str module-level match() helper workflow that accepts a compiled pattern on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-compile-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "abc",
      "helper": "compile",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "categories": ["workflow", "compile", "literal", "bytes", "compiled-pattern"],
      "notes": [
        "Publishes the exact literal bytes module-level compile() helper workflow that accepts a compiled pattern on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-compile-flags-noflag-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "abc",
      "helper": "compile",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": re.NOFLAG
      },
      "categories": ["workflow", "compile", "literal", "bytes", "compiled-pattern", "flags", "noflag"],
      "notes": [
        "Publishes the compiled-pattern module-level literal bytes compile() explicit NOFLAG spelling on the shared owner path without broadening into the default, integer-zero, bool-false, named-group, or nonzero-flag rejection slices."
      ]
    },
    {
      "id": "workflow-module-compile-flags-int-zero-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "abc",
      "helper": "compile",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": 0
      },
      "categories": ["workflow", "compile", "literal", "bytes", "compiled-pattern", "flags", "int-zero"],
      "notes": [
        "Publishes the bytes explicit integer-zero compiled-pattern module-level compile() keyword neighbor on the shared module-workflow owner path without broadening into False or NOFLAG spellings."
      ]
    },
    {
      "id": "workflow-module-compile-flags-bool-false-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "abc",
      "helper": "compile",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": False
      },
      "categories": ["workflow", "compile", "literal", "bytes", "compiled-pattern", "flags", "bool-false"],
      "notes": [
        "Publishes the bytes explicit bool-false compiled-pattern module-level compile() keyword neighbor on the shared module-workflow owner path without broadening into integer-zero or NOFLAG spellings."
      ]
    },
    {
      "id": "workflow-module-compile-flags-ignorecase-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "abc",
      "helper": "compile",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": 2
      },
      "categories": ["workflow", "compile", "literal", "bytes", "compiled-pattern", "flags", "ignorecase", "rejection"],
      "notes": [
        "Publishes the compiled-pattern module-level bytes literal explicit IGNORECASE rejection singleton on the shared module-workflow owner path without broadening into the default, integer-zero, bool-false, NOFLAG, str-side, or named-group rejection slices."
      ]
    },
    {
      "id": "workflow-module-compile-bytes-compiled-pattern-named-group",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "compile",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "categories": ["workflow", "compile", "named-group", "bytes", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent bytes named-group module-level compile() helper workflow that accepts a compiled pattern on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-compile-flags-noflag-bytes-compiled-pattern-named-group",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "compile",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": re.NOFLAG
      },
      "categories": ["workflow", "compile", "named-group", "bytes", "compiled-pattern", "flags", "noflag"],
      "notes": [
        "Publishes the bytes named-group explicit NOFLAG compiled-pattern module-level compile() keyword singleton on the shared module-workflow owner path without broadening into the default, integer-zero, bool-false, or nonzero-flag rejection slices."
      ]
    },
    {
      "id": "workflow-module-compile-flags-int-zero-bytes-compiled-pattern-named-group",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "compile",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": 0
      },
      "categories": ["workflow", "compile", "named-group", "bytes", "compiled-pattern", "flags", "int-zero"],
      "notes": [
        "Publishes the bytes named-group explicit integer-zero compiled-pattern module-level compile() keyword singleton on the shared module-workflow owner path without broadening into the default, False, or NOFLAG spellings."
      ]
    },
    {
      "id": "workflow-module-compile-flags-bool-false-bytes-compiled-pattern-named-group",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "compile",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": False
      },
      "categories": ["workflow", "compile", "named-group", "bytes", "compiled-pattern", "flags", "bool-false"],
      "notes": [
        "Publishes the bytes named-group explicit bool-false compiled-pattern module-level compile() keyword singleton on the shared module-workflow owner path without broadening into the default, integer-zero, NOFLAG, or nonzero-flag rejection slices."
      ]
    },
    {
      "id": "workflow-module-compile-flags-ignorecase-bytes-compiled-pattern-named-group",
      "operation": "module_call",
      "family": "compile_workflow",
      "pattern": "(?P<word>abc)",
      "helper": "compile",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "kwargs": {
        "flags": 2
      },
      "categories": ["workflow", "compile", "named-group", "bytes", "compiled-pattern", "flags", "ignorecase", "rejection"],
      "notes": [
        "Publishes the bytes named-group explicit IGNORECASE compiled-pattern module-level compile() keyword rejection singleton on the shared module-workflow owner path without broadening into the default, integer-zero, bool-false, NOFLAG, or str-side rejection slices."
      ]
    },
    {
      "id": "workflow-module-fullmatch-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "module_fullmatch_workflow",
      "pattern": "abc",
      "helper": "fullmatch",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abc"
        }
      ],
      "categories": ["workflow", "fullmatch", "literal", "bytes", "compiled-pattern"],
      "notes": [
        "Publishes the exact bytes literal module-level fullmatch() helper workflow that accepts a compiled pattern on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-match-bytes-compiled-pattern-on-str-string",
      "operation": "module_call",
      "family": "module_match_workflow",
      "pattern": "abc",
      "helper": "match",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": ["abc"],
      "categories": ["workflow", "match", "literal", "bytes", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern match() wrong-text-model TypeError on the shared module-workflow owner path without widening into other helper mismatches."
      ]
    },
    {
      "id": "workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern",
      "operation": "module_call",
      "family": "module_search_workflow",
      "pattern": "a.c",
      "flags": 2,
      "helper": "search",
      "use_compiled_pattern": True,
      "args": ["ABC"],
      "categories": ["workflow", "search", "wildcard", "bounded", "ignorecase", "str", "compiled-pattern"],
      "notes": [
        "Publishes the exact compiled-pattern module-level search() IGNORECASE workflow already anchored on the shared bounded wildcard owner path."
      ]
    },
    {
      "id": "workflow-module-match-str-bounded-wildcard-compiled-pattern",
      "operation": "module_call",
      "family": "module_match_workflow",
      "pattern": "a.c",
      "helper": "match",
      "use_compiled_pattern": True,
      "args": ["abc"],
      "categories": ["workflow", "match", "wildcard", "bounded", "str", "compiled-pattern"],
      "notes": [
        "Publishes the exact compiled-pattern module-level match() workflow already anchored on the shared bounded wildcard owner path."
      ]
    },
    {
      "id": "workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern",
      "operation": "module_call",
      "family": "module_fullmatch_workflow",
      "pattern": "a.c",
      "helper": "fullmatch",
      "use_compiled_pattern": True,
      "args": ["abc"],
      "categories": ["workflow", "fullmatch", "wildcard", "bounded", "str", "compiled-pattern"],
      "notes": [
        "Publishes the exact compiled-pattern module-level fullmatch() workflow already anchored on the shared bounded wildcard owner path."
      ]
    },
    {
      "id": "workflow-module-fullmatch-str-compiled-pattern-on-bytes-string",
      "operation": "module_call",
      "family": "module_fullmatch_workflow",
      "pattern": "abc",
      "helper": "fullmatch",
      "text_model": "str",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abc"
        }
      ],
      "categories": ["workflow", "fullmatch", "literal", "str", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern fullmatch() wrong-text-model TypeError on the shared module-workflow owner path without widening into other helper mismatches."
      ]
    },
    {
      "id": "workflow-module-search-bytes-verbose-regression-compiled-pattern",
      "operation": "module_call",
      "family": "module_search_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 72,
      "helper": "search",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "prefix\nENV_VAR=ABCD\nsuffix"
        }
      ],
      "categories": ["workflow", "search", "verbose", "multiline", "regression", "bytes", "compiled-pattern"],
      "notes": [
        "Publishes the first bytes module-level search() helper workflow that accepts a compiled verbose regression pattern on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern",
      "operation": "module_call",
      "family": "module_fullmatch_workflow",
      "pattern": "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
      "flags": 72,
      "helper": "fullmatch",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "ENV_VAR = 123"
        }
      ],
      "categories": ["workflow", "fullmatch", "verbose", "multiline", "regression", "bytes", "compiled-pattern"],
      "notes": [
        "Publishes the first bytes module-level fullmatch() helper workflow that accepts a compiled verbose regression pattern on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-split-str-compiled-pattern",
      "operation": "module_call",
      "family": "module_split_workflow",
      "pattern": "abc",
      "helper": "split",
      "use_compiled_pattern": True,
      "args": ["zzabczzabc", 1],
      "categories": ["workflow", "split", "literal", "str", "compiled-pattern"],
      "notes": [
        "Publishes the first literal str module-level split() helper workflow that accepts a compiled pattern on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-split-maxsplit-keyword-str-compiled-pattern",
      "operation": "module_call",
      "family": "module_split_workflow",
      "pattern": "abc",
      "helper": "split",
      "use_compiled_pattern": True,
      "args": ["zabczabc"],
      "kwargs": {
        "maxsplit": 1
      },
      "categories": ["workflow", "split", "literal", "keyword", "maxsplit", "str", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern module-level split() maxsplit= keyword workflow on str payloads without widening into compiled-pattern replacement keyword rows."
      ]
    },
    {
      "id": "workflow-module-split-maxsplit-indexlike-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "module_split_workflow",
      "pattern": "abc",
      "helper": "split",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabcabc"
        }
      ],
      "kwargs": {
        "maxsplit": _INDEX_TWO
      },
      "categories": ["workflow", "split", "literal", "keyword", "maxsplit", "indexlike", "bytes", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern module-level split() maxsplit=__index__ keyword workflow on bytes payloads without widening into compiled-pattern replacement keyword rows."
      ]
    },
    {
      "id": "workflow-module-split-maxsplit-bool-false-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "module_split_workflow",
      "pattern": "abc",
      "helper": "split",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabc"
        }
      ],
      "kwargs": {
        "maxsplit": False
      },
      "categories": ["workflow", "split", "literal", "keyword", "maxsplit", "bool", "bytes", "compiled-pattern"],
      "notes": [
        "Publishes the bounded compiled-pattern module-level split() maxsplit=False keyword workflow on bytes payloads alongside the adjacent compiled-pattern replacement bool rows."
      ]
    },
    {
      "id": "workflow-module-split-duplicate-maxsplit-keyword-str-compiled-pattern",
      "operation": "module_call",
      "family": "module_split_workflow",
      "pattern": "abc",
      "helper": "split",
      "use_compiled_pattern": True,
      "args": ["abc", 1],
      "kwargs": {
        "maxsplit": 1
      },
      "categories": ["workflow", "split", "literal", "str", "maxsplit", "duplicate-keyword", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern module-level split() duplicate maxsplit= keyword rejection on str payloads without widening into the remaining compiled-pattern keyword-error ladder."
      ]
    },
    {
      "id": "workflow-module-split-unexpected-keyword-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "module_split_workflow",
      "pattern": "abc",
      "helper": "split",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abc"
        }
      ],
      "kwargs": {
        "missing": 1
      },
      "categories": ["workflow", "split", "literal", "bytes", "unexpected-keyword", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern module-level split() unexpected keyword rejection on bytes payloads without widening into the remaining compiled-pattern keyword-error ladder."
      ]
    },
    {
      "id": "workflow-module-split-str-compiled-pattern-on-bytes-string",
      "operation": "module_call",
      "family": "module_split_workflow",
      "pattern": "abc",
      "helper": "split",
      "text_model": "str",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabczz"
        },
        1
      ],
      "categories": ["workflow", "split", "literal", "str", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern split() wrong-text-model TypeError on the shared module-workflow owner path without widening into other helper mismatches."
      ]
    },
    {
      "id": "workflow-module-findall-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "module_findall_workflow",
      "pattern": "abc",
      "helper": "findall",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabc"
        }
      ],
      "categories": ["workflow", "findall", "literal", "bytes", "compiled-pattern"],
      "notes": [
        "Publishes the first bytes module-level findall() helper workflow that accepts a compiled literal pattern on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-findall-bytes-compiled-pattern-on-str-string",
      "operation": "module_call",
      "family": "module_findall_workflow",
      "pattern": "abc",
      "helper": "findall",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": ["zabczz"],
      "categories": ["workflow", "findall", "literal", "bytes", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern findall() wrong-text-model TypeError on the shared module-workflow owner path without widening into other helper mismatches."
      ]
    },
    {
      "id": "workflow-module-finditer-str-compiled-pattern",
      "operation": "module_call",
      "family": "module_finditer_workflow",
      "pattern": "abc",
      "helper": "finditer",
      "use_compiled_pattern": True,
      "args": ["zabcabc"],
      "categories": ["workflow", "finditer", "literal", "str", "compiled-pattern"],
      "notes": [
        "Publishes the first literal str module-level finditer() helper workflow that accepts a compiled pattern on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-finditer-str-compiled-pattern-on-bytes-string",
      "operation": "module_call",
      "family": "module_finditer_workflow",
      "pattern": "abc",
      "helper": "finditer",
      "text_model": "str",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabczz"
        }
      ],
      "categories": ["workflow", "finditer", "literal", "str", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern finditer() wrong-text-model TypeError on the shared module-workflow owner path without widening into other helper mismatches."
      ]
    },
    {
      "id": "workflow-module-sub-str-compiled-pattern",
      "operation": "module_call",
      "family": "module_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "use_compiled_pattern": True,
      "args": ["x", "zabcabc", 1],
      "categories": ["workflow", "sub", "literal", "str", "compiled-pattern"],
      "notes": [
        "Publishes the first literal str module-level sub() helper workflow that accepts a compiled pattern on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-sub-count-keyword-str-compiled-pattern",
      "operation": "module_call",
      "family": "module_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "use_compiled_pattern": True,
      "args": ["x", "abcabc"],
      "kwargs": {
        "count": 1
      },
      "categories": ["workflow", "sub", "literal", "keyword", "count", "str", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern module-level sub() count= keyword workflow on str payloads without widening into compiled-pattern keyword-error rows."
      ]
    },
    {
      "id": "workflow-module-sub-count-indexlike-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "module_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabcabc"
        }
      ],
      "kwargs": {
        "count": _INDEX_TWO
      },
      "categories": ["workflow", "sub", "literal", "keyword", "count", "indexlike", "bytes", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern module-level sub() count=__index__ keyword workflow on bytes payloads without widening into compiled-pattern keyword-error rows."
      ]
    },
    {
      "id": "workflow-module-sub-count-bool-true-str-compiled-pattern",
      "operation": "module_call",
      "family": "module_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "use_compiled_pattern": True,
      "args": ["x", "abcabc"],
      "kwargs": {
        "count": True
      },
      "categories": ["workflow", "sub", "literal", "keyword", "count", "bool", "str", "compiled-pattern"],
      "notes": [
        "Publishes the bounded compiled-pattern module-level sub() count=True keyword workflow on str payloads alongside the adjacent compiled-pattern replacement bool rows."
      ]
    },
    {
      "id": "workflow-module-sub-count-bool-false-str-compiled-pattern",
      "operation": "module_call",
      "family": "module_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "use_compiled_pattern": True,
      "args": ["x", "abcabc"],
      "kwargs": {
        "count": False
      },
      "categories": ["workflow", "sub", "literal", "keyword", "count", "bool", "str", "compiled-pattern"],
      "notes": [
        "Publishes the bool-count complement spelling beside the already published compiled-pattern module-level sub() count=True keyword workflow on str payloads without widening into the remaining compiled-pattern keyword matrix."
      ]
    },
    {
      "id": "workflow-module-sub-duplicate-count-keyword-str-compiled-pattern",
      "operation": "module_call",
      "family": "module_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "use_compiled_pattern": True,
      "args": ["x", "abc", 1],
      "kwargs": {
        "count": 1
      },
      "categories": ["workflow", "sub", "literal", "str", "count", "duplicate-keyword", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern module-level sub() duplicate count= keyword rejection on str payloads without widening into the remaining compiled-pattern keyword-error ladder."
      ]
    },
    {
      "id": "workflow-module-sub-unexpected-keyword-str-compiled-pattern",
      "operation": "module_call",
      "family": "module_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "use_compiled_pattern": True,
      "args": ["x", "abc"],
      "kwargs": {
        "missing": 1
      },
      "categories": ["workflow", "sub", "literal", "str", "unexpected-keyword", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern module-level sub() unexpected keyword rejection on str payloads without widening into the remaining compiled-pattern keyword-error ladder."
      ]
    },
    {
      "id": "workflow-module-sub-str-compiled-pattern-on-bytes-string",
      "operation": "module_call",
      "family": "module_sub_workflow",
      "pattern": "abc",
      "helper": "sub",
      "text_model": "str",
      "use_compiled_pattern": True,
      "args": [
        "x",
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabczz"
        },
        1
      ],
      "categories": ["workflow", "sub", "literal", "str", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern sub() wrong-text-model TypeError on the shared module-workflow owner path without widening into other helper mismatches."
      ]
    },
    {
      "id": "workflow-module-subn-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "module_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabc"
        },
        1
      ],
      "categories": ["workflow", "subn", "literal", "bytes", "compiled-pattern"],
      "notes": [
        "Publishes the first bytes module-level subn() helper workflow that accepts a compiled literal pattern on the shared module-workflow owner path."
      ]
    },
    {
      "id": "workflow-module-subn-count-keyword-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "module_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabc"
        }
      ],
      "kwargs": {
        "count": 1
      },
      "categories": ["workflow", "subn", "literal", "keyword", "count", "bytes", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern module-level subn() count= keyword workflow on bytes payloads without widening into compiled-pattern keyword-error rows."
      ]
    },
    {
      "id": "workflow-module-subn-count-indexlike-str-compiled-pattern",
      "operation": "module_call",
      "family": "module_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "use_compiled_pattern": True,
      "args": ["x", "abcabcabc"],
      "kwargs": {
        "count": _INDEX_TWO
      },
      "categories": ["workflow", "subn", "literal", "keyword", "count", "indexlike", "str", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern module-level subn() count=__index__ keyword workflow on str payloads without widening into compiled-pattern keyword-error rows."
      ]
    },
    {
      "id": "workflow-module-subn-count-bool-false-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "module_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabc"
        }
      ],
      "kwargs": {
        "count": False
      },
      "categories": ["workflow", "subn", "literal", "keyword", "count", "bool", "bytes", "compiled-pattern"],
      "notes": [
        "Publishes the bounded compiled-pattern module-level subn() count=False keyword workflow on bytes payloads alongside the adjacent compiled-pattern replacement bool rows."
      ]
    },
    {
      "id": "workflow-module-subn-count-bool-true-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "module_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabc"
        }
      ],
      "kwargs": {
        "count": True
      },
      "categories": ["workflow", "subn", "literal", "keyword", "count", "bool", "bytes", "compiled-pattern"],
      "notes": [
        "Publishes the bool-count complement spelling beside the already published compiled-pattern module-level subn() count=False keyword workflow on bytes payloads without widening into the remaining compiled-pattern keyword matrix."
      ]
    },
    {
      "id": "workflow-module-subn-duplicate-count-keyword-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "module_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abc"
        },
        1
      ],
      "kwargs": {
        "count": 1
      },
      "categories": ["workflow", "subn", "literal", "bytes", "count", "duplicate-keyword", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern module-level subn() duplicate count= keyword rejection on bytes payloads without widening into the remaining compiled-pattern keyword-error ladder."
      ]
    },
    {
      "id": "workflow-module-subn-unexpected-keyword-bytes-compiled-pattern",
      "operation": "module_call",
      "family": "module_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abc"
        }
      ],
      "kwargs": {
        "missing": 1
      },
      "categories": ["workflow", "subn", "literal", "bytes", "unexpected-keyword", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern module-level subn() unexpected keyword rejection on bytes payloads without widening into the remaining compiled-pattern keyword-error ladder."
      ]
    },
    {
      "id": "workflow-module-subn-bytes-compiled-pattern-on-str-string",
      "operation": "module_call",
      "family": "module_subn_workflow",
      "pattern": "abc",
      "helper": "subn",
      "text_model": "bytes",
      "use_compiled_pattern": True,
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        "zabczz",
        1
      ],
      "categories": ["workflow", "subn", "literal", "bytes", "compiled-pattern"],
      "notes": [
        "Publishes the adjacent compiled-pattern subn() wrong-text-model TypeError on the shared module-workflow owner path without widening into other helper mismatches."
      ]
    },
    {
      "id": "workflow-escape-str",
      "operation": "module_call",
      "family": "escape_workflow",
      "helper": "escape",
      "args": ["a-b.c"],
      "categories": ["workflow", "escape", "str"],
      "notes": [
        "Carries the local escape() helper into the module-workflow scorecard for str payloads."
      ]
    },
    {
      "id": "workflow-escape-bytes",
      "operation": "module_call",
      "family": "escape_workflow",
      "helper": "escape",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "a-b.c"
        }
      ],
      "categories": ["workflow", "escape", "bytes"],
      "notes": [
        "Mirrors escape() parity for bytes payloads in the workflow pack."
      ]
    }
  ]
}
