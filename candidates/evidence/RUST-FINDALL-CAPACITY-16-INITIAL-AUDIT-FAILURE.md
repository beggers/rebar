# First smaller-buffer campaign audit failure

This record preserves the first real attempt to qualify the one-line Rust `findall` buffer experiment. It does not weaken, replace, or edit the frozen correctness campaign.

The tested bridge source was `83afb5a709a6d0ea1701dfd64db30644edbf2cb0276c2db731a8119cfd52d8ed`; its built native bridge was `1f072e81ba9339a8b2e52a7e93b7bcde791c4d518620b6bd760af67c7c89af34`. The unchanged original independent audit had first produced the passing report `af69f41966a26d9ec1892e34b16f1bc02eb095c41767899d0a3deb612591d8fc`. The unchanged original matching, deep public-contract, and observation tests had already passed **223,198**, **393**, and **479** checks respectively. These preliminary results were not treated as a complete campaign.

The first exact complete-campaign command was:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -B \
  tools/rust_v8_multi_candidate_campaign.py \
  --module candidates.rust_candidate \
  --edge-oracle candidates/evidence/rust-v7-edge-oracle-rust-findall-capacity-16.json.gz \
  --deep-proof candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-FINDALL-CAPACITY-16.json.gz \
  --output candidates/evidence/rust-v8-rust-findall-capacity-16-sealed-campaign.json \
  --memory-mib 2048
```

Its actual exit status was **1**. The unchanged frozen runner reported:

```text
Traceback (most recent call last):
  File "/home/dev-user/src/rebar/tools/rust_v8_multi_candidate_campaign.py", line 1439, in <module>
    raise SystemExit(main())
  File "/home/dev-user/src/rebar/tools/rust_v8_multi_candidate_campaign.py", line 1427, in main
    result = run_campaign(
  File "/home/dev-user/src/rebar/tools/rust_v8_multi_candidate_campaign.py", line 1024, in run_campaign
    audit = static_family_audit(module, edge)
  File "/home/dev-user/src/rebar/tools/rust_v8_multi_candidate_campaign.py", line 415, in static_family_audit
    require(evidence.get("passed") is True, "complete from-scratch audit failed")
  File "/home/dev-user/src/rebar/tools/rust_v8_multi_candidate_campaign.py", line 79, in require
    raise AssertionError(message)
AssertionError: complete from-scratch audit failed
```

This failure happened before a passing 22-stage report was created. Its immediate cause was the actual campaign's new in-process `scratch.run_audit()` returning a nonpassing result. The original exception does not retain that audit result, so the exact reason for that individual nonpassing result is **NOT ESTABLISHED**. The failure is not described as a regex mismatch, a memory-safety error, or a successfully completed correctness run.

A separate diagnostic imported the unchanged real campaign module, installed its original performance-exclusion seal, and directly invoked the same `campaign.scratch.run_audit()` without timing or accessing the final benchmark. Its actual exit status was **0**. It reported a **PASS** for all four independent implementations, all five native libraries and their actual mappings, all 76 malicious controls, and every source check, with no input or mapping issues. That later diagnostic does not erase or establish the cause of the first failed attempt. A passing report is accepted only if the unchanged complete 22-stage campaign is subsequently run again and really passes.

## Result of the unchanged complete retry

After concurrent work was stopped, the exact original command shown above was rerun without changing the correctness runner, candidate source, compiled bridge, independent audit, inputs, limits, or failure criteria. Its actual exit status was **0**. The complete [source-bound 22-stage report](rust-v8-rust-findall-capacity-16-sealed-campaign.json) has SHA-256 `89793a597ac74551742d05bdf1c5af61f1121d89466e00ac2902c8942aaeef4d`. All **22** real stages passed, including all **4,494,555** Unicode comparisons, replacements, callbacks, and isolated safety checks; `holdout_accessed` and `timing_performed` are both `false`. The successful retry does not remove, explain, or conceal the first failure.

Final benchmark: **NOT ACCESSED**. Performance: **NOT MEASURED**.
