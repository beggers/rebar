# Corrected from-scratch Rust baseline

The original Rust implementation differed from Python on 24,462 of the 223,198 independently frozen compatibility checks. This change fixes the Rust parser, matching engine, native Python bindings, and public Python interface without wrapping an external regular-expression implementation.

| Frozen check | Original Rust differences | Corrected Rust differences |
| --- | ---: | ---: |
| Complete compatibility, 223,198 checks | 24,462 | 0 |
| Independent pattern grammar, 20,480 checks | 5,535 | 0 |
| Independent Python object behavior, 14,783 checks | 507 | 0 |

The corrected engine additionally passes all 4,494,555 full-Unicode checks; all 8,244 original v2 and 44,084 original v3 correctness cases; Python's 144 runnable upstream methods; 190 official and 1,198 extended public-interface checks; 8,862 ordinary and 11,266 deep replacement checks; and the independently isolated native boundary, invalid-name, crash, and recursion-safety checks. The two skipped upstream methods require an operating-system locale that is not installed; they are explicitly recorded rather than presented as passes.

The five exact artifacts checked by the complete compatibility oracle are:

| Artifact | SHA-256 |
| --- | --- |
| Public Python interface | `1111a419d65d44775d1f4b0cb6a728dea8de44a592597341596533351c16018e` |
| Loaded native Python bridge | `eedcd253ab9ec6bab9a9ac9242d04d3fc6c808bf1b8de342bb5a5b9fd8528272` |
| Loaded Rust engine | `890f9e34e966244067a3dc173c2276043ae15d4830a05228fb37ec2571aa17cd` |
| Rust engine source | `a2fa04912bb1f6957f833560446f4d3d1c5d13df8b5efac992fa63e28803668b` |
| Native bridge source | `8900b120ddb85a74aedf584b960ff878aa47020c910c0ce749dae51eb304f3c2` |

The Rust lockfile contains one locally implemented package and zero external dependencies. Both native libraries are independently checked for linkage to Python's regex engine or third-party regular-expression libraries; none is present. The loaded Python bridge links directly to the from-scratch Rust engine.

Complete records:

- [Reproducible six-engine compatibility graph](rust-v7-correctness.svg).
- [Complete 223,198-case compatibility report](rust-v7-edge-oracle-rust-corrected-v4.json.gz).
- [Complete 20,480-pattern grammar report](rust-v7-grammar-rust-corrected-v4.json.gz).
- [Complete 14,783-case Python object report](rust-v7-corrected-v4/rust-v7-object-rust.json.gz).
- [Entire Unicode-plane report](rust-v7-corrected-v4/unicode.json).
- [Official Python upstream tests](rust-v7-corrected-v4/cpython.json).
- [Complete holdout-safe correctness and safety campaign](rust-v7-corrected-v4/campaign.json).
- [All individual correctness and safety evidence](rust-v7-corrected-v4/).

The campaign explicitly excludes all older and current performance suites while the final 10,312-case holdout remains sealed. A poisoned-input self-test proves that it cannot start, import, or read an excluded benchmark. Its 17 required correctness and safety checks remain mandatory.

Rebuild and verify with the pinned interpreter:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_rust.sh
PYTHONPATH=. "$PY" tools/rust_v7_edge_oracle.py \
  --module candidates.rust_candidate --output /tmp/rebar-rust-v7-corrected-edge.json.gz
PYTHONPATH=. "$PY" tools/rust_v7_correctness_chart.py --self-test
PYTHONPATH=. "$PY" tools/rust_v7_grammar_oracle.py gate \
  --module candidates.rust_candidate --require-pass
PYTHONPATH=. "$PY" tools/rust_campaign_gate.py --sealed-practice-self-test
PYTHONPATH=. "$PY" tools/rust_campaign_gate.py --sealed-practice-only \
  --output /tmp/rebar-rust-v7-corrected-campaign.json
```

Corrected Rust speed: **NOT MEASURED**. Final performance holdout: **NOT ACCESSED**.
