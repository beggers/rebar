#!/usr/bin/env python3
"""Run the frozen quote oracle against the stage-04 Rust engine only.

The stage-03 generator and its standard-library comparison remain unchanged.
This additive entry point binds their 83,968 observations to a new schema,
the current Rust source and native artifacts, and an exclusively created
stage-04 evidence path.  Its worker, including workers started with ``-I``,
never reads a performance fixture or any hidden benchmark.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import rust_postfinal_quote_parity_stage03_oracle as frozen


frozen.SCHEMA = "rebar-rust-postfinal-quote-parity-oracle-v4"
frozen.RUNNER = Path(__file__).resolve()
frozen.DEFAULT_OUTPUT = (
    ROOT
    / "candidates"
    / "evidence"
    / "rust-postfinal-quote-parity-stage-04-deterministic-oracle.json"
)


if __name__ == "__main__":
    raise SystemExit(frozen.main())
