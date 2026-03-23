MANIFEST = {
  "schema_version": 1,
  "manifest_id": "collection-replacement-workflows",
  "layer": "module_workflow",
  "suite_id": "collection.replacement.workflow",
  "defaults": {
    "flags": 0,
    "text_model": "str"
  },
  "cases": [
    {
      "id": "module-split-str-leading-trailing",
      "operation": "module_call",
      "family": "split_workflow",
      "helper": "split",
      "args": ["abc", "abczzabc"],
      "categories": ["workflow", "split", "literal", "str", "leading", "trailing", "repeated"],
      "notes": [
        "Pins module-level literal split behavior with repeated matches and both leading and trailing empty fields."
      ]
    },
    {
      "id": "module-split-str-no-match",
      "operation": "module_call",
      "family": "split_workflow",
      "helper": "split",
      "args": ["abc", "zzz"],
      "categories": ["workflow", "split", "literal", "str", "no-match"],
      "notes": [
        "Observes that module split returns the original string when no literal match is present."
      ]
    },
    {
      "id": "module-split-str-pattern-on-bytes-string",
      "operation": "module_call",
      "family": "split_workflow",
      "helper": "split",
      "args": [
        "abc",
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abc"
        }
      ],
      "categories": ["workflow", "split", "literal", "str", "wrong-text-model", "type-error"],
      "notes": [
        "Publishes the raw module-level split wrong-text-model TypeError on a bytes haystack so the collection surface no longer relies only on a bespoke direct test."
      ]
    },
    {
      "id": "pattern-split-str-no-match",
      "operation": "pattern_call",
      "family": "split_workflow",
      "pattern": "abc",
      "helper": "split",
      "args": ["zzz"],
      "categories": ["workflow", "split", "literal", "str", "no-match"],
      "notes": [
        "Publishes the direct Pattern.split str no-match path on the shared collection workflow frontier."
      ]
    },
    {
      "id": "pattern-split-str-repeated",
      "operation": "pattern_call",
      "family": "split_workflow",
      "pattern": "abc",
      "helper": "split",
      "args": ["abcabc"],
      "categories": ["workflow", "split", "literal", "str", "repeated"],
      "notes": [
        "Publishes the direct Pattern.split str repeated-match path on the shared collection workflow frontier."
      ]
    },
    {
      "id": "pattern-split-bytes-maxsplit",
      "operation": "pattern_call",
      "family": "split_workflow",
      "pattern": "abc",
      "text_model": "bytes",
      "helper": "split",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abczzabc"
        },
        1
      ],
      "categories": ["workflow", "split", "literal", "bytes", "maxsplit"],
      "notes": [
        "Carries bounded maxsplit behavior through the compiled bytes Pattern.split path."
      ]
    },
    {
      "id": "module-findall-bytes-repeated",
      "operation": "module_call",
      "family": "findall_workflow",
      "helper": "findall",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abc"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabc"
        }
      ],
      "categories": ["workflow", "findall", "literal", "bytes", "repeated"],
      "notes": [
        "Pins bytes-valued module findall behavior for repeated literal matches."
      ]
    },
    {
      "id": "module-findall-str-pattern-on-bytes-string",
      "operation": "module_call",
      "family": "findall_workflow",
      "helper": "findall",
      "args": [
        "abc",
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abc"
        }
      ],
      "categories": ["workflow", "findall", "literal", "str", "wrong-text-model", "type-error"],
      "notes": [
        "Publishes the raw module-level findall wrong-text-model TypeError on a bytes haystack so the collection frontier carries that public-module mismatch directly."
      ]
    },
    {
      "id": "pattern-findall-str-no-match",
      "operation": "pattern_call",
      "family": "findall_workflow",
      "pattern": "abc",
      "helper": "findall",
      "args": ["zzz"],
      "categories": ["workflow", "findall", "literal", "str", "no-match"],
      "notes": [
        "Observes that the bound Pattern.findall path returns an empty list when the literal does not occur."
      ]
    },
    {
      "id": "pattern-findall-str-bounded",
      "operation": "pattern_call",
      "family": "findall_workflow",
      "pattern": "abc",
      "helper": "findall",
      "args": ["zabcabcz", 1, 7],
      "categories": ["workflow", "findall", "literal", "str", "bounded"],
      "notes": [
        "Publishes the bounded Pattern.findall str path on the shared collection workflow frontier."
      ]
    },
    {
      "id": "pattern-findall-str-bounded-no-match",
      "operation": "pattern_call",
      "family": "findall_workflow",
      "pattern": "abc",
      "helper": "findall",
      "args": ["zabz", 1, 4],
      "categories": ["workflow", "findall", "literal", "str", "bounded", "no-match"],
      "notes": [
        "Publishes the bounded Pattern.findall str no-match window without widening beyond the direct helper slice."
      ]
    },
    {
      "id": "pattern-findall-bytes-bounded",
      "operation": "pattern_call",
      "family": "findall_workflow",
      "pattern": "abc",
      "text_model": "bytes",
      "helper": "findall",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabcz"
        },
        1,
        7
      ],
      "categories": ["workflow", "findall", "literal", "bytes", "bounded"],
      "notes": [
        "Publishes the bounded Pattern.findall bytes path on the shared collection workflow frontier."
      ]
    },
    {
      "id": "pattern-findall-bytes-pattern-on-str-string",
      "operation": "pattern_call",
      "family": "findall_workflow",
      "pattern": "abc",
      "text_model": "bytes",
      "helper": "findall",
      "args": ["abc"],
      "categories": ["workflow", "findall", "literal", "bytes", "wrong-text-model", "type-error"],
      "notes": [
        "Publishes the bound Pattern.findall wrong-text-model TypeError for a bytes pattern on a str haystack so the collection fixture covers the compiled helper mismatch too."
      ]
    },
    {
      "id": "module-finditer-str-repeated",
      "operation": "module_call",
      "family": "finditer_workflow",
      "helper": "finditer",
      "args": ["abc", "zabcabc"],
      "categories": ["workflow", "finditer", "literal", "str", "repeated", "iterator-exhaustion"],
      "notes": [
        "Materializes the module-level finditer result so the scorecard captures ordered matches and iterator exhaustion."
      ]
    },
    {
      "id": "pattern-finditer-str-bounded",
      "operation": "pattern_call",
      "family": "finditer_workflow",
      "pattern": "abc",
      "helper": "finditer",
      "args": ["zabcabcx", 1, 7],
      "categories": ["workflow", "finditer", "literal", "str", "bounded", "iterator-exhaustion"],
      "notes": [
        "Publishes the bounded compiled-pattern str finditer path, including its exhausted terminal state."
      ]
    },
    {
      "id": "pattern-finditer-str-bounded-no-match",
      "operation": "pattern_call",
      "family": "finditer_workflow",
      "pattern": "abc",
      "helper": "finditer",
      "args": ["zabz", 1, 4],
      "categories": ["workflow", "finditer", "literal", "str", "bounded", "no-match", "iterator-exhaustion"],
      "notes": [
        "Publishes the bounded compiled-pattern str finditer no-match window without widening beyond the direct helper slice."
      ]
    },
    {
      "id": "pattern-finditer-bytes-bounded",
      "operation": "pattern_call",
      "family": "finditer_workflow",
      "pattern": "abc",
      "text_model": "bytes",
      "helper": "finditer",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabcx"
        },
        1,
        7
      ],
      "categories": ["workflow", "finditer", "literal", "bytes", "bounded", "iterator-exhaustion"],
      "notes": [
        "Pins the bounded compiled-pattern bytes finditer path, including its exhausted terminal state."
      ]
    },
    {
      "id": "pattern-finditer-bytes-pattern-on-str-string",
      "operation": "pattern_call",
      "family": "finditer_workflow",
      "pattern": "abc",
      "text_model": "bytes",
      "helper": "finditer",
      "args": ["abc"],
      "categories": ["workflow", "finditer", "literal", "bytes", "wrong-text-model", "type-error"],
      "notes": [
        "Publishes the bound Pattern.finditer wrong-text-model TypeError for a bytes pattern on a str haystack so the fixture-backed iterator surface owns that mismatch as well."
      ]
    },
    {
      "id": "module-sub-str-no-match",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "sub",
      "args": ["abc", "x", "zzz"],
      "categories": ["workflow", "sub", "literal", "str", "no-match"],
      "notes": [
        "Publishes the raw str module sub helper outcome when no literal match is present."
      ]
    },
    {
      "id": "module-sub-str-single-match",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "sub",
      "args": ["abc", "x", "zabczz"],
      "categories": ["workflow", "sub", "literal", "str", "single-match"],
      "notes": [
        "Publishes the raw str module sub helper outcome for a single literal match."
      ]
    },
    {
      "id": "module-sub-str-repeated",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "sub",
      "args": ["abc", "x", "abcabc"],
      "categories": ["workflow", "sub", "literal", "str", "repeated"],
      "notes": [
        "Pins module-level literal replacement behavior for repeated str matches."
      ]
    },
    {
      "id": "module-sub-str-count-one",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "sub",
      "args": ["abc", "x", "abcabc", 1],
      "categories": ["workflow", "sub", "literal", "str", "count-one"],
      "notes": [
        "Publishes the raw str module sub helper outcome for the direct count-one singleton."
      ]
    },
    {
      "id": "module-sub-str-negative-count",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "sub",
      "args": ["abc", "x", "abcabc", -1],
      "categories": ["workflow", "sub", "literal", "str", "negative-count"],
      "notes": [
        "Publishes the raw str module sub helper outcome for the exact negative-count module workflow."
      ]
    },
    {
      "id": "module-subn-str-count",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "subn",
      "args": ["abc", "x", "abcabc", 1],
      "categories": ["workflow", "subn", "literal", "str", "count"],
      "notes": [
        "Publishes the raw str module subn helper outcome for a bounded replacement count."
      ]
    },
    {
      "id": "module-subn-str-repeated",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "subn",
      "args": ["abc", "x", "abcabc"],
      "categories": ["workflow", "subn", "literal", "str", "repeated"],
      "notes": [
        "Publishes the raw str module subn helper outcome for repeated literal matches."
      ]
    },
    {
      "id": "module-subn-str-negative-count",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "subn",
      "args": ["abc", "x", "abcabc", -1],
      "categories": ["workflow", "subn", "literal", "str", "negative-count"],
      "notes": [
        "Publishes the raw str module subn helper outcome for the exact negative-count module workflow."
      ]
    },
    {
      "id": "module-sub-bytes-no-match",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "sub",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abc"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzz"
        }
      ],
      "categories": ["workflow", "sub", "literal", "bytes", "no-match"],
      "notes": [
        "Publishes the raw bytes module sub helper outcome when no literal match is present."
      ]
    },
    {
      "id": "module-sub-bytes-repeated",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "sub",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abc"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabcabc"
        }
      ],
      "categories": ["workflow", "sub", "literal", "bytes", "repeated"],
      "notes": [
        "Publishes the raw bytes module sub helper outcome for repeated literal matches."
      ]
    },
    {
      "id": "module-sub-bytes-count-one",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "sub",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abc"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabc"
        },
        1
      ],
      "categories": ["workflow", "sub", "literal", "bytes", "count-one"],
      "notes": [
        "Publishes the raw bytes module sub helper outcome for a bounded replacement count."
      ]
    },
    {
      "id": "module-subn-bytes-count",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "subn",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abc"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abcabc"
        },
        1
      ],
      "categories": ["workflow", "subn", "literal", "bytes", "count"],
      "notes": [
        "Carries bounded replacement-count behavior through the bytes-valued module subn helper."
      ]
    },
    {
      "id": "module-subn-bytes-repeated",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "subn",
      "text_model": "bytes",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "abc"
        },
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
      "categories": ["workflow", "subn", "literal", "bytes", "repeated"],
      "notes": [
        "Publishes the raw bytes module subn helper outcome for repeated literal matches."
      ]
    },
    {
      "id": "pattern-sub-str-no-match",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "helper": "sub",
      "args": ["x", "zzz"],
      "categories": ["workflow", "sub", "literal", "str", "no-match"],
      "notes": [
        "Observes that the compiled-pattern replacement path leaves the string unchanged when no match exists."
      ]
    },
    {
      "id": "pattern-sub-str-single-match",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "helper": "sub",
      "args": ["x", "zabczz"],
      "categories": ["workflow", "sub", "literal", "str", "single-match"],
      "notes": [
        "Publishes the direct Pattern.sub str single-match path on the shared collection replacement frontier."
      ]
    },
    {
      "id": "pattern-sub-str-repeated",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "helper": "sub",
      "args": ["x", "abcabc"],
      "categories": ["workflow", "sub", "literal", "str", "repeated"],
      "notes": [
        "Publishes the direct Pattern.sub str repeated-match path on the shared collection replacement frontier."
      ]
    },
    {
      "id": "pattern-sub-str-count-one",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "helper": "sub",
      "args": ["x", "abcabc", 1],
      "categories": ["workflow", "sub", "literal", "str", "count-one"],
      "notes": [
        "Publishes the direct Pattern.sub str count-bounded path on the shared collection replacement frontier."
      ]
    },
    {
      "id": "pattern-sub-str-negative-count",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "helper": "sub",
      "args": ["x", "abcabc", -1],
      "categories": ["workflow", "sub", "literal", "str", "negative-count"],
      "notes": [
        "Publishes the direct Pattern.sub str negative-count path on the shared collection replacement frontier."
      ]
    },
    {
      "id": "pattern-subn-str-count",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "helper": "subn",
      "args": ["x", "abcabc", 1],
      "categories": ["workflow", "subn", "literal", "str", "count"],
      "notes": [
        "Pins the compiled-pattern str subn path for a bounded single replacement."
      ]
    },
    {
      "id": "pattern-subn-str-repeated",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "helper": "subn",
      "args": ["x", "abcabc"],
      "categories": ["workflow", "subn", "literal", "str", "repeated"],
      "notes": [
        "Publishes the direct Pattern.subn str repeated-match path on the shared collection replacement frontier."
      ]
    },
    {
      "id": "pattern-subn-str-negative-count",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "helper": "subn",
      "args": ["x", "abcabc", -1],
      "categories": ["workflow", "subn", "literal", "str", "negative-count"],
      "notes": [
        "Publishes the direct Pattern.subn str negative-count path on the shared collection replacement frontier."
      ]
    },
    {
      "id": "pattern-sub-bytes-no-match",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "text_model": "bytes",
      "helper": "sub",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zzz"
        }
      ],
      "categories": ["workflow", "sub", "literal", "bytes", "no-match"],
      "notes": [
        "Observes that the compiled-pattern bytes replacement path leaves the haystack unchanged when no match exists."
      ]
    },
    {
      "id": "pattern-sub-bytes-single-match",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "text_model": "bytes",
      "helper": "sub",
      "args": [
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "x"
        },
        {
          "type": "bytes",
          "encoding": "latin-1",
          "value": "zabczz"
        }
      ],
      "categories": ["workflow", "sub", "literal", "bytes", "single-match"],
      "notes": [
        "Publishes the direct Pattern.sub bytes single-match path on the shared collection replacement frontier."
      ]
    },
    {
      "id": "pattern-sub-bytes-repeated",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "text_model": "bytes",
      "helper": "sub",
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
      "categories": ["workflow", "sub", "literal", "bytes", "repeated"],
      "notes": [
        "Publishes the direct Pattern.sub bytes repeated-match path on the shared collection replacement frontier."
      ]
    },
    {
      "id": "pattern-sub-bytes-count-one",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "text_model": "bytes",
      "helper": "sub",
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
        },
        1
      ],
      "categories": ["workflow", "sub", "literal", "bytes", "count-one"],
      "notes": [
        "Pins the compiled-pattern bytes sub path for a bounded single replacement on the shared collection replacement frontier."
      ]
    },
    {
      "id": "pattern-sub-bytes-negative-count",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "text_model": "bytes",
      "helper": "sub",
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
        },
        -1
      ],
      "categories": ["workflow", "sub", "literal", "bytes", "negative-count"],
      "notes": [
        "Publishes the direct Pattern.sub bytes negative-count path on the shared collection replacement frontier."
      ]
    },
    {
      "id": "pattern-subn-bytes-count",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "text_model": "bytes",
      "helper": "subn",
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
        },
        1
      ],
      "categories": ["workflow", "subn", "literal", "bytes", "count"],
      "notes": [
        "Pins the compiled-pattern bytes subn path for a bounded single replacement."
      ]
    },
    {
      "id": "pattern-subn-bytes-repeated",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "text_model": "bytes",
      "helper": "subn",
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
      "categories": ["workflow", "subn", "literal", "bytes", "repeated"],
      "notes": [
        "Publishes the direct Pattern.subn bytes repeated-match path on the shared collection replacement frontier."
      ]
    },
    {
      "id": "pattern-subn-bytes-negative-count",
      "operation": "pattern_call",
      "family": "replacement_workflow",
      "pattern": "abc",
      "text_model": "bytes",
      "helper": "subn",
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
        },
        -1
      ],
      "categories": ["workflow", "subn", "literal", "bytes", "negative-count"],
      "notes": [
        "Publishes the direct Pattern.subn bytes negative-count path on the shared collection replacement frontier."
      ]
    },
    {
      "id": "module-sub-template-str",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "sub",
      "args": ["abc", "\\g<0>x", "abc"],
      "categories": ["workflow", "sub", "replacement-template", "str"],
      "notes": [
        "Pins the bounded whole-match replacement-template slice for a supported literal str pattern."
      ]
    },
    {
      "id": "module-sub-callable-str",
      "operation": "module_call",
      "family": "replacement_workflow",
      "helper": "sub",
      "args": [
        "abc",
        {
          "type": "callable_constant",
          "value": "x"
        },
        "abcabc"
      ],
      "categories": ["workflow", "sub", "callable-replacement", "str"],
      "notes": [
        "Pins the bounded callable replacement slice for a supported literal str pattern."
      ]
    },
    {
      "id": "module-sub-grouping-template",
      "operation": "module_call",
      "family": "grouped_template_replacement_workflow",
      "helper": "sub",
      "args": ["(abc)", "\\1x", "abc"],
      "categories": ["workflow", "sub", "replacement-template", "grouping-dependent", "str"],
      "notes": [
        "Pins the bounded grouped-literal replacement-template slice without broadening into general grouped-pattern or backreference support."
      ]
    },
    {
      "id": "module-findall-nonliteral-str",
      "operation": "module_call",
      "family": "bounded_wildcard_collection_workflow",
      "helper": "findall",
      "args": ["a.c", "abc"],
      "categories": ["workflow", "findall", "bounded-wildcard", "non-literal", "str"],
      "notes": [
        "Pins the bounded single-dot wildcard findall workflow without broadening into general metacharacter support."
      ]
    }
  ]
}
