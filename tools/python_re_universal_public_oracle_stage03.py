#!/usr/bin/env python3
"""Additive stage-03 output slots for the immutable universal public oracle."""

from __future__ import annotations

import sys
from pathlib import Path


WRAPPER = Path(__file__).resolve()
ROOT = WRAPPER.parent.parent
FROZEN_SOURCE = ROOT / "tools" / "python_re_universal_public_oracle_v1.py"
FROZEN_SOURCE_SHA256 = (
    "744876e5b8409b8d49982ccfb61d93a99f3e2d4fd64d0543b29b831bd26796a0"
)
OUTPUT_CANDIDATES = frozenset({"rust", "vm", "zig", "all"})

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import python_re_universal_public_oracle_v1 as frozen


frozen.candidate_free()
frozen.require(
    Path(frozen.__file__).resolve() == FROZEN_SOURCE.resolve(),
    "stage-03 did not import the exact immutable V1 universal public oracle",
)
frozen.require(
    frozen.sha256_path(FROZEN_SOURCE, frozen.MAX_SOURCE_BYTES)
    == FROZEN_SOURCE_SHA256,
    "the immutable V1 universal public oracle changed before stage-03",
)
frozen.require(
    frozen.SCHEMA == "rebar-python-re-universal-public-oracle-v1"
    and frozen.SEED == 2026072417
    and frozen.EXPECTED_CASES == 8_192
    and frozen.OBSERVATIONS_PER_CASE == 48
    and frozen.EXPECTED_OBSERVATIONS == 393_216,
    "stage-03 cannot change the frozen V1 schema, seed, case matrix, or controls",
)


def stage03_default_output(candidate: str) -> Path:
    frozen.require(
        candidate in OUTPUT_CANDIDATES,
        "stage-03 must select an exact independently audited candidate slot",
    )
    return (
        frozen.EVIDENCE_ROOT
        / f"python-re-universal-public-oracle-v3-{candidate}.json"
    )


frozen.RUNNER = WRAPPER
frozen.default_output = stage03_default_output


if __name__ == "__main__":
    raise SystemExit(frozen.main())
