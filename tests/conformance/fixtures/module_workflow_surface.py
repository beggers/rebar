class _IndexLike:
    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        self.value = value

    def __index__(self) -> int:
        return self.value

    def __repr__(self) -> str:
        return f"IndexLike({self.value})"


_INDEX_TWO = _IndexLike(2)


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
