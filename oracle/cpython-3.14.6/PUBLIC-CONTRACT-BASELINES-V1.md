# Frozen public-contract baselines

This is a phase-one correctness experiment, not a candidate comparison.
It records one unchanged public Python `re` category at a time against two
separate, unmodified CPython 3.14.6 processes.

The frozen contract is `tools/independent_public_contract_v3.py` with
SHA-256 `9a831571c81e542d7d43ae56aea271f8e6c69550173d97ae1c9f8213eef40bf3`.
The upstream original V5 suite is pinned to
`8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce`.
The original public V2 is pinned to
`a0ae9621e06b760477a167705cc6e521cc7e9df4d44d126e39c614df89bd3e68`.

| Category | Original cases | Seed | Original case matrix SHA-256 | Original CPython observation SHA-256 |
| --- | ---: | --- | --- | --- |
| `public` | 864; 36 groups of 24; 432 text and 432 bytes | `0x52454241525f5031` | `367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e` | `0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c` |
| `scanner` | 1,024; 32 groups of 32 | `0x5343414e4e455231` | `83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c` | `37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d` |
| `buffer` | 768; 24 groups of 32 | `0x4d455850414e4431` | `b40fb92f42c7019a73eec72800077f262f1a6be516886a6ddda372e24807eb60` | `8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75` |

Only `tools/record_independent_public_contract_baselines_v1.py --self-test`
is source-only. Its entirely synthetic controls do not import the contract,
read or write the workspace, launch a reference or candidate, sample a clock,
or access a benchmark or holdout.

An actual baseline requires a separately and explicitly authorized `--record`
invocation under the exact pinned, isolated `python3.14 -I -B`, with one
category, a fresh label, the recorder's actual source SHA-256, the exact
contract SHA-256, and that category's exact matrix SHA-256. The controller
authenticates all original source owners before importing the V3 contract.
It preflights two fresh evidence paths before launching either worker. It then
runs only the original V3 `reference_a` and `reference_b` workers in genuinely
distinct CPython processes, validates their complete original ordered stimuli,
outcomes, warnings, exceptions, process streams, source owners, and PIDs, and
checks that both reproduce the separately frozen original observation hash.

For each independently authorized category, evidence is published as a fresh,
bounded deterministic gzip and a separate durable receipt under
`oracle/cpython-3.14.6/evidence/`:

- `public-contract-baseline-v1-CATEGORY-LABEL.json.gz`;
- `public-contract-baseline-v1-CATEGORY-LABEL-publication-receipt.json`.

Publication follows only descriptor-anchored, no-symlink directory paths,
exclusive no-overwrite temporaries and hard links, complete attempted-write
ledgers, file and directory syncs, complete compressed and decompressed
readback, and genuine descriptor-lifetime evidence. A failed reference is
recorded as failed; a process, write, close, or publication is never invented.
The receipt does not claim that its own publication completed before its
separate write, sync, and readback have actually succeeded.

Existing candidate-bound receipts remain historical candidate evidence. They
are not pure CPython phase-one baselines. This protocol does not qualify a
candidate, choose a winner, read a holdout, or measure performance.

Holdout: **NOT ACCESSED**. Performance: **NOT MEASURED**. Candidate
workers: **0**.
