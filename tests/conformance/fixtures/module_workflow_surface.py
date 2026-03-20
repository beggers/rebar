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
