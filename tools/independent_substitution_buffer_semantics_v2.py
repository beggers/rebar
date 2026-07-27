#!/usr/bin/env python3
"""Freeze complete, deterministic CPython replacement and buffer semantics.

The 64 equally weighted cohorts preserve module and compiled ``sub``/``subn``,
``Match.expand``, text, bytes, bytearrays, contiguous and strided memoryviews,
released replacements, real nested PEP-688 exporters, custom hashes, callbacks,
capture groups, zero-width matches, windows, exact exceptions, and every
ordered acquisition and release.  ``--self-test`` is synthetic and cannot run
an engine, read or write a file, start a process, sample a clock, or inspect a
benchmark.  Only an explicitly pinned later ``--baseline`` may start two
genuine isolated standard-CPython reference workers.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import copy
import gc
import hashlib
import importlib
import io
import json
import os
import random
import stat
import subprocess
import sys
import threading
import time
import types
import warnings
import zlib
from collections.abc import Callable, Mapping, Sequence
from typing import Any


ROOT = "/home/dev-user/src/rebar"
SOURCE_RELATIVE = "tools/independent_substitution_buffer_semantics_v2.py"
SOURCE_ABSOLUTE = ROOT + "/" + SOURCE_RELATIVE
SCHEMA = "rebar-independent-substitution-buffer-semantics-v2"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
PINNED_STDLIB_DIRECTORY = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/"
)
PINNED_STDLIB_SOURCES = types.MappingProxyType({
    "re": (
        "__init__.py",
        "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35",
    ),
    "re._compiler": (
        "_compiler.py",
        "d49f30cf9a1dbae33b200ed8befd9d0ce3ac612783a10ac35196536f98923e91",
    ),
    "re._parser": (
        "_parser.py",
        "e57bd194a2d42398355ae7c1ccc2ddfb78421dd431eb81e3809dbe8ca9057dc4",
    ),
    "re._constants": (
        "_constants.py",
        "42253b3181b81aad6c46392f44a0ab26dcfa31feea411296f43ba16616a1ab0b",
    ),
})
V5_GUARD_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
V5_GUARD_SHA256 = (
    "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
)
OWNERSHIP_AUDIT_RELATIVE = "tools/independent_from_scratch_audit_v3.py"
OWNERSHIP_AUDIT_SHA256 = (
    "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee"
)
ORACLE_CALLBACK_CANONICAL_MODULE = (
    "tools.independent_substitution_buffer_semantics_v2"
)
HISTORICAL_V1_STATUS = "FALSIFIED"
HISTORICAL_V1_ORACLE_RELATIVE = (
    "tools/independent_substitution_buffer_semantics_v1.py"
)
HISTORICAL_V1_ORACLE_SHA256 = (
    "a325528aa62f107969b9dfdf5dea2ae8f9426607887a317fe20fcf9a1b7fd445"
)
HISTORICAL_V1_RECORDER_RELATIVE = (
    "tools/record_independent_substitution_buffer_semantics_v2.py"
)
HISTORICAL_V1_RECORDER_SHA256 = (
    "a7cf45ce72a178fead7eb0d0789fd1f0f37ed63789fe086070eefa613e959a33"
)
HISTORICAL_V1_PREVIOUS_RECORDER_RELATIVE = (
    "tools/record_independent_substitution_buffer_semantics_v1.py"
)
HISTORICAL_V1_PREVIOUS_RECORDER_SHA256 = (
    "1dbb45e8950a0eceb966a56adcbe2f9d1da35ec04883458a780b6f08f5a4735d"
)
HISTORICAL_V1_EVIDENCE_DIRECTORY = "experiments/rust_public_practice_v1"
HISTORICAL_V1_PINNED_FILES = types.MappingProxyType({
    "v1_oracle": (
        HISTORICAL_V1_ORACLE_RELATIVE,
        HISTORICAL_V1_ORACLE_SHA256,
    ),
    "v1_recorder": (
        HISTORICAL_V1_RECORDER_RELATIVE,
        HISTORICAL_V1_RECORDER_SHA256,
    ),
    "v1_previous_recorder": (
        HISTORICAL_V1_PREVIOUS_RECORDER_RELATIVE,
        HISTORICAL_V1_PREVIOUS_RECORDER_SHA256,
    ),
    "v1_preserved_initial_failure": (
        HISTORICAL_V1_EVIDENCE_DIRECTORY
        + "/substitution-buffer-semantics-v1-shared-suite-v1-"
        "controller-failure-v1.json",
        "a80316f3d1fe87808c8f16cb651393d275132d408633303da16a5142f55ba807",
    ),
    "v1_baseline_archive": (
        HISTORICAL_V1_EVIDENCE_DIRECTORY
        + "/substitution-buffer-semantics-v1-shared-suite-v1.json.gz",
        "2e24e17862e75f4f2f778d15d67416f6e643eff01c0d110e750cea99b2550fab",
    ),
    "v1_baseline_receipt": (
        HISTORICAL_V1_EVIDENCE_DIRECTORY
        + "/substitution-buffer-semantics-v1-shared-suite-v1-"
        "publication-receipt.json",
        "9a707f4953b8ed23d1f3e0cb5f4f6fd6e2e104e675fe502a3e991ebb2e884cd2",
    ),
    "v1_c_failed_archive": (
        HISTORICAL_V1_EVIDENCE_DIRECTORY
        + "/c-substitution-buffer-semantics-v1-native-lifetime-repair-v1"
        ".json.gz",
        "b1545e5850caaf59fd9640358527dfaf160f90b3f48fc9f80accd5a49a305111",
    ),
    "v1_c_failed_receipt": (
        HISTORICAL_V1_EVIDENCE_DIRECTORY
        + "/c-substitution-buffer-semantics-v1-native-lifetime-repair-v1-"
        "publication-receipt.json",
        "933852815241f3b2c82f6e5a07a5624422c323c7d4f86cebeb3f6f700cefa5b2",
    ),
    "v1_zig_failed_archive": (
        HISTORICAL_V1_EVIDENCE_DIRECTORY
        + "/zig-substitution-buffer-semantics-v1-owned-safe-buffer-repair-v1"
        ".json.gz",
        "8adefae4fb5248d3a95cefc852bfafa9dfca39d0d868a0b424df6394eef9a402",
    ),
    "v1_zig_failed_receipt": (
        HISTORICAL_V1_EVIDENCE_DIRECTORY
        + "/zig-substitution-buffer-semantics-v1-owned-safe-buffer-repair-v1-"
        "publication-receipt.json",
        "89d5f12fb076b4152cf14a12d6fd22f18a0ba99c07a82a2a8efdb4d1ff12a03e",
    ),
})
HISTORICAL_V1_BASELINE_RECORDS_SHA256 = (
    "3e74498c0c6997bcb86fab81a4be2962809c77b49d7214837633c9539c42ad18"
)
HISTORICAL_V1_FAILURE_COUNTS = types.MappingProxyType({
    "c": 464,
    "zig": 192,
})
HISTORICAL_V1_ORACLE_ARTIFACT_COUNTS = types.MappingProxyType({
    "c": 128,
    "zig": 128,
})
HISTORICAL_V1_REAL_FAILURE_COUNTS = types.MappingProxyType({
    "c": 336,
    "zig": 64,
})

HISTORICAL_V1_SIGNED_WITNESS_COMPRESSED_BYTES = 120_215
HISTORICAL_V1_SIGNED_WITNESS_COMPRESSED_SHA256 = (
    "1b727c1c9aeaf1e1ffe696838711523d9fb4e73ffa1d1a8b5990f3b711a57316"
)
HISTORICAL_V1_SIGNED_WITNESS_BYTES = 4_111_279
HISTORICAL_V1_SIGNED_WITNESS_SHA256 = (
    "6ed5b60d5e207b062a94e150450301918760143af4e650c272a6da1a31fa0be8"
)
HISTORICAL_V1_SIGNED_WITNESS_MAXIMUM_BYTES = 5 * 1024 * 1024
HISTORICAL_V1_SIGNED_WITNESS_BASE64 = (
    "eNrsvV+PJEeS5PlVGnxuDkxNVU3V5m1xuAMOuKd7OmB2QaipmU3XLZvkkcXZmV3sdz/3ZHcNJzs7M4MVGRXMFRYrKzL+"
    "eHhEmIv8Qtxc/H98NeKn9e2H79Y3P678/sf50zc//Smqtq/+8SteJtI9S7bebeTwtmM4hYxVe6teepoN6dMqibM15uzK"
    "PaXGJP/qj79e+F4/ru9yffPDh/nTV//4T17/6Pxf/vhVHvf4Jr//+buPX/2jUi1//GrHnz98+2Edd/ofX+X5I378+GFH"
    "fvzr3aj6H7/604efPn7/44eMb7/J+G5+mPHxqZfQF5Mr9aQhjdOVqfAgydL73NpGN0ntGi2UC42YnRY/vNCxi3z1H57o"
    "zx9++nN8zD/9dUWkydO3r3/5MB9e7KcVmZNbq9RkzTk4sjvv3sh3GcpRU+se41jX7ZmizZio9LW957FGm/g/rshPH+Pj"
    "z8cb9NX/8Z/+z//ruOmvT3y+af90vGH58ef49uH9i2+/HZH/9Zfr17+sc7U/XXs88sN3c/3rV/94vO0PCzgfs76bP3z/"
    "8O5//Lcf1nH3D8eD/vjVv8S3Px+/sf3PP371zz9+//MPv7rHTx9//Pd7HIvf//nnUlaX+tVf7zw/5MfzAR8+rj+fK/NP"
    "f+ex3/3857F+PB72d24/F/lf/vj3Hv3fjk//7z/203odizhG3l/u87Bmf13Nn369ji8v5vm1/OttH3/+4dt1PsW38dPH"
    "59+6Ty//4b5/+XCe/iDqcacf4uPH9eN333z46Zv1rz+s/LjmV//48cef13HT3/8Iy/HIH9c/P3qtf/OqHz/m6RvaEy/0"
    "Ny9MfsPC5II1e+IzOd7/D9/982vG8h/G+hj2h3X8fijFH/7zz9NL+cNc334M/sOhFkalOema/77Y84P56efx/65z8J+f"
    "y/nOx4efzu304ddTAE8tOZTr//t5/fTw+R3b4i+b4OMrz633P27IP/zpUM9jbb+LP58re2zC68cP8e2H/76+PiTix48P"
    "b98r7pzf//l4Oz6u5+7//Q/rx/j44fvvnlg0BAWCAkG5B0F5zfb78IDnNvX8dsV3P//wK1k4Xuf611w/nI//Bcn++TUj"
    "e//4/X9f3/3hWONj7H38+Xz0H/6qFX/Y8eHbn398+k38r8dIPdf5x/nhu/jx377+4d8+/ulY8/Xjj9+fy//z+umn+OdX"
    "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"
    "xbe2oXBZ7w9PpC8qRQtWaaWX2gsRWYj3gmpVCopR6ZX2rNrQRqBh3BFYT3r9ZNQX6fxGV3GcwGWM0mGJ0O5ss8Dogasc"
    "p7vPuux0XusS48duxBCT5pw4Wkh7rXcKeUwhn9E+Z+JzJj4pQlKEpAjvJogHYj6gIVh62mn75cx6XtxcU5WtMt9eUnXy"
    "1wQDtU72Gl6Lqqx+RKvM20f6kRL0XGAaqFArGwZtjasJClp1zdkn+Zilt15W93lajw+UWZjHhFV7hfa2dpZudbKdd6/a"
    "VW3g4FJ3SPLaZXI36S3G3Wv1vceSPaqh9NDNytbXndr5ib3FkzAkpuQkeE6C582dhCkJ089NmF6tBE4rIQ3SnLBON/o3"
    "7ery/BQpqVXj+1QpYaF4dL7K2/jwo71Cbx/zWd3FuQ63VqFvjb00WGX2DWeluM9a7GoqLrIrETbnLWy4Wm3dFsIR5u+U"
    "gkNrTeqZlT7l4wIhRRja2NynaWyvpVRrwIMaAs6xJf4psrH1qd3vVOGSKjzDf85g5wx2cobkDMkZ7u8vHqM9oHHcy/2X"
    "6JjomCc786Kyveg7mHIcQz1LdeTl+/iIJvWj2oveMd6PTO+e2dTaCpus6cgTpzSFESpQZ/Nd+56uo/dZressp1qZ8FkI"
    "3Wu3/q0K+D+e3l2t4JKx56y+VXWhLIDQpzEGYB09NCyduWT0ULHatdmsOELpooxxp7CEJ3YYT/DMeJ7SMm+aJAFJAr4i"
    "CfguFaGkVMyMj8x/zoub6Ty/YU+JT6hpcepJcGU5zSdrtavJBFZ+QtPLm0d+WpPx2NdRqIzqU0Y3grm7oQEwsmrZw3xi"
    "WX2Ltrhdmo3GWzbNPlcBWO+sPB6bYA9fxGMq45pmZ1EzL4oTN0xp8JRSqe2+MQaCCeqt42LDGOBOeV1TXicmZf505k/n"
    "zZ2EKwlXEq5nEK5XI+MRXcYRSMmqkCa7yACcdkZe3CzRmT0y37T8KZDvNADhClfnSomvd0p0PqQcCl3P/6eRX4qj/OOS"
    "nD9WJY3MsE3zGXu6GDcGklvZpc6lNnTPJuil7zH3lDgNxqaz8LXHXXm+7VXM2RRYYe8CBUlx9eUlBpujdC48rA5fvmPz"
    "ZiiKrfHC+FvRbgr9Tq/iie3Gk1Mk7KRjkY5F3tzJqZJT/eqc6tWP0PQjMi8sM/EzCe83r1D6CY73KU1aInbj9dNCjZ7E"
    "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"
    "L4em6BpyPW67JuVOnf7EDqzJJBJskkmkTk8ukVzi1+USr+pbU31n8lUmL2fq1W9dHfATmr3ZtTpFrhUqfvCj1oji8LSC"
    "7/atVOCf9uGlTODLK+LRyzt8ZvdV3nUu3VSbeewlrpORHKcJpe2uKzStj8qrhNo0bgTaZ5tTtJxKh6v52yJ2x8mxBoN5"
    "97ZDwa65OpmWPtExlK2OYcMmTdXOAw24N117Oq2Btd0pYi1FbGJEAnJmQyckJyR/HUh+lYKP6L8qlPZp2qdpn+bFzSSn"
    "bHv2PuRKfJ1m5yQ1tnPV+K3W57U9k9PW7E9tzv/Yj+tvzu/XK+UzO7CGpK0nGVpXM63bii4m7jr3pi5DeuheCeUrMufs"
    "7jq16aii0Fsd8x0R3FWsQ+HRrVJRW9JaZZ29hbTWwrud/gVBDsQB4jdQL9zE5l6lkd5Zqsme2IE1qUiiVVKRnMlNMpJk"
    "JMnI+/rfIPV/Os85FZy+829XHvFT+8RFhI9n4XTeFqx2FZZ3qR/eJ+6PcdvV8/uPTt92PeLLhfbv7vPD05OP173NtMy5"
    "LWTrWm1RCQZCLErTSScqQN2ztF46xTEiOIt3PPnM+21RO4oySiu8TrcdhR1HM4DY4n24lVY3ewmkDS1dgtuIj73MRt+h"
    "oknxzmXEhilqM+QnvubMbiJsIuzHIeyrUntEP9a0R9MeTXs0L24uc8m+areUipSAumNGwqkLcaVGxV99QF+120f6kTLL"
    "WkDVwGGd7jdYugc9CN2pnbGNPZTKntRWCZ1a17RCPEc8X4I6ofV3+t+s7WsU57PwNWRuCWVLbdCYbXkvzWKz7o1cJs3p"
    "cb3LckfAFTcYNZA79ecT+7Ema0hgSdaQk6rJG5I3/CK84VVWc8rqNGhzAjTt2d+5DcFnrLs562xOycF6cnCwHse2VvjI"
    "BnG3j/msjqyqYIttj8HqtNmHcGuhFWHU3faZI50GeA60KZ4aSwB9lB3CUZFI32n8QxtbcI49fLaGcceprNJl1Eq2BijP"
    "BSiwmgqSsZv4RhsgzjJ43alIJRVpYkACbs6IJuQm5D4Rcl+13CN6sr7chAkuCS55sjPZJnvK3ZZrc3JdSuWKcoJ8bBX5"
    "5w2/90vV3zzej0wXuil3oTm69D5Puk/t0Lj6rDN2Yxi1Yqwmvdhe1w7PSoytdFx1vNOVtbfVpUrppW6gIeJzSxnVmo9R"
    "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"
    "7hvyyge/1SJP6t7NhI8mAKOZ8O3qS/1xtAJTF/By5d51r98vXx/V3NOHg3N+3oa3Y3OYqAWxMEZtQ6zMEqgPImnrl94o"
    "tNZGp5G0WCo0XPtYax2GyQwt5HeKHdQU15eJJ6ph6zS8/naLu0lzVk1DtXgsXRJ585ZSaLW3HGVIXbMIcmFsjl01Nufx"
    "LRtQ4GEWumuj4O8rLsDqA6sPrD6w+sDqA6sPrD6w+qA6DiwbsGzsa9l4jUkwxCR8IVxrq1q0Xt9eNWFe4ET2XcK13hwZ"
    "hXOQkYJ0I2zutcKWH/KSFh9uYY4V6w5oAA2gATSABtAAGkADaAANoAE0gAbQABpAA2gADaABNIAG0ACaB4AmPAE03yDD"
    "iZ6u/MnBqp9cwtXu7bQ+WvNkPfM678J8eu7Pua/X9K93rsfy8vr27Hq0juW0w7s2hc2txWiZ1iRr7ZP6VrR4pDrK5JlC"
    "KTymsvQ6SylZSouVp4/F3Gw193k+Tyo39yzmmQfVHtmCUGzrg7ZayOsFiz2wFZMxxTglpum9BJY8ok2rF+ZJJeRJIe4E"
    "QUXYXNQwfnBtAGoS1CTo1oAG0AAaQANoAA2gATSABtAAGkADaAANoAE0gAbQABpAA2gADaBBtBWirRBthWirXaOtXms3"
    "JdRu+nR9XDFey5+YtnZf63trAKZ7XP7OjXzX2k1rQuuqslF7LgDl53fdPaJm50nfLOwJi3242kaPesrHh1uYA+lWgAbQ"
    "ABpAA2gADaABNIAG0AAaQANoAA2gATSABtAAGkADaAANoAE0gAbQABpAc7e4vm+8NveK6wtXDOt7N1jiaqF7x+qseBk7"
    "V+ys+KUovvbncZSXI/kRuffyyNaj/OO538byfb5j4y811v44W2StsGrUmON0rc1yjyNz1h7jXBMNeU5KynUdPfdZxIsG"
    "DZklWyujlXy+yJpq8TyTl5HCiK1S4hZIhGbx0iKl1Nis5hwteV4rVavq+sSqXddqzQuLrDmKrCEgDdF/WOynF6ahZUDL"
    "gGoKaAANoAE0gAbQABpAA2gADaABNIAG0AAaQANoAA2gATSABtAAGkADaAANoEFYJMIiERaJsMiHCot8LYbolxVDDCiG"
    "+FpZc8Mvrnf52sit/ijxgpBlh1qwZ0a+WzFEffOqr373SLwvTO4mEXf3WLx4g8X79OT4o4LcPSYnv0yOjzM5/WVycuSV"
    "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"
    "wdEictGAtfZ8utrRDnzsaRWKPcnOMec029djTGu/wpVsxKsLD9bMjkhnIrMj0mCmwbwfg/mIuUti7mejDjo6dRbh+iD3"
    "SA/FJnaTJvYXRs7kiOSwk7R/B47hbLs9OYZTuUz6weIZZ3KtrttAZ6rUWNoNHQEr0X6/3akNnRhcawQ6VOqrNp8TebQp"
    "gi6ljuDpK0xXvcxFyHBcOkfFI/0CtPAIWHPP2Z7DtoYUnyyzjEXGUPcsG1BrGGF1mMOVXERNLiIzI/INZ2ZEOhLpSKQj"
    "cTOOpiZH82zU1o42nftZe20Ll2N9da/qLbTwLoycipJ54XelKHm2XZTcR6pZfaiEzeu2yamKP8AhlOaAylXXAMJwMWpV"
    "fL/Din1K7SLg7GXM6lrAGms/mkSYTXyC4kBc2PbH6gON1duc1WLxgNG0NnLvvl9oaQzvhSb2EmB7Bjv1aH4lxdGS4khV"
    "ybzwpA7SDqcdfmc7/EgQtOMO/Wn533741x9/3kf7+C8/PBiWf/mPzGU/87//+J8/7Y9ffow9G789iNT2Nf748y//+OnH"
    "bZd+eDSzP62x7+yf/2DEqfbOAlCM6rJ4mKteRwmyte0odmbsUGvHPVEhE8ljz2MdcTR/OkieP7zQ51eJRl9+fP3XY9rG"
    "vyslxQGL3XpfiH1BU6BFUiwMlIKxSlOC2HfsVOTlBNW0ok1xebD3f3ih3++r//1//j/+z2Pn/frC69Px8WXO5fGE+u23"
    "//L7Yux762GA428+2fHju1/X98eHm//XJeW6F+Y///SPf/7bH57x7w+q4fGf/gmwTOhffnvy/HHfMX844752yP39n//a"
    "H26hrzx+DPn//Iev/fX/u1f/63/7+3XtIR6Pxocr++0yv+Uc/sMwl6/yT4fv3/znXy5P3e9v/+G5vy7OlxeCjnP003Hz"
    "w48///DorP3y0z/XwxH7tb+E/3Hsus9tzp/e9ed/8+UHyhfe6LMHk2cMJldc2RfWZM//Ppu+5V7+S1+/eP3L2j8z4F/+"
    "0z9nA/jLXH/7xfkvvUfFfRajrvk47LEwvx2XD+tyzPxhCn7+9ccvudLw/Qi054GSB0oeKGc6UM4PWX47K14PpvzpFf4A"
    "TX75xz/+9vP/dOyDf9vH0oEm/vinP3ziT374nT/54b/io5/7fz2Cgf/115e4tUzfF2fx/34d3fqb3p43a+YC21OW7Q6P"
    "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"
    "63/7P//LP/2v/+3/B7Grkkc="
)

PUBLISHED_SEED = 0x5355_4253_4255_4631
VARIANTS_PER_COHORT = 80
COHORTS = (
    "text-literal",
    "text-escaped",
    "text-callback",
    "text-callback-error",
    "text-named-captures",
    "text-numeric-captures",
    "text-missing-capture",
    "text-invalid-escape",
    "text-zero-width-lookahead",
    "text-zero-width-empty",
    "text-count-limit",
    "text-window-pos-endpos",
    "text-lone-surrogate",
    "text-combining-mark",
    "text-precomposed-unicode",
    "text-cross-domain-bytes-template",
    "bytes-literal",
    "bytes-escaped",
    "bytes-callback",
    "bytes-callback-error",
    "bytes-named-captures",
    "bytes-numeric-captures",
    "bytes-missing-capture",
    "bytes-invalid-escape",
    "bytes-zero-width-lookahead",
    "bytes-zero-width-empty",
    "bytes-count-limit",
    "bytes-window-pos-endpos",
    "bytearray-subject-literal",
    "bytearray-subject-escaped",
    "bytearray-replacement-literal",
    "bytearray-replacement-escaped",
    "readonly-subject-memoryview",
    "writable-subject-memoryview",
    "readonly-strided-subject-memoryview",
    "writable-strided-subject-memoryview",
    "released-readonly-subject-memoryview",
    "released-writable-subject-memoryview",
    "readonly-template-memoryview",
    "writable-template-memoryview",
    "readonly-strided-template-memoryview",
    "writable-strided-template-memoryview",
    "released-readonly-template-memoryview",
    "released-writable-template-memoryview",
    "pep688-stable-subject",
    "pep688-mutating-subject",
    "pep688-failing-subject",
    "pep688-fixed-hash-subject",
    "pep688-unhashable-subject",
    "pep688-stable-template",
    "pep688-mutating-template",
    "pep688-failing-template",
    "pep688-fixed-hash-template",
    "pep688-unhashable-template",
    "pep688-failing-hash-template",
    "pep688-wrapped-readonly-subject",
    "pep688-wrapped-writable-subject",
    "nested-stable-subject-and-template",
    "nested-mutating-subject-and-template",
    "nested-stable-fixed-hash-template",
    "nested-mutating-unhashable-template",
    "nested-failing-template-after-subject",
    "match-expand-buffer-retention",
    "callback-capture-and-buffer-order",
)
CASE_COUNT = len(COHORTS) * VARIANTS_PER_COHORT
MATRIX_SHA256 = (
    "26f46fe7f1abc5135d1265a7882ccd4a2e2b45cdec80ba293520fda510235b54"
)
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 96 * 1024 * 1024
SIMPLE_BUFFER_FLAG = 0
FULL_READONLY_BUFFER_FLAG = 284
APIS = (
    "module.sub", "module.subn", "pattern.sub", "pattern.subn", "match.expand",
)
FLAGS = (0, 2, 256, 258)
COUNTS = (0, 1, 2, 7)
WINDOW_STARTS = (-4, -1, 0, 1, 2, 5, 99, 2_147_483_647)
WINDOW_ENDS = (0, 1, 3, 8, 16, 64, None, 2_147_483_647)
SUBJECT_KINDS = frozenset({
    "str", "bytes", "bytearray", "readonly-memoryview",
    "writable-memoryview", "readonly-strided-memoryview",
    "writable-strided-memoryview", "released-readonly-memoryview",
    "released-writable-memoryview", "pep688-stable", "pep688-mutating",
    "pep688-failing", "pep688-fixed-hash", "pep688-unhashable",
    "pep688-wrapped-readonly", "pep688-wrapped-writable",
})
REPLACEMENT_KINDS = frozenset({
    "str", "bytes", "bytearray", "readonly-memoryview",
    "writable-memoryview", "readonly-strided-memoryview",
    "writable-strided-memoryview", "released-readonly-memoryview",
    "released-writable-memoryview", "pep688-stable", "pep688-mutating",
    "pep688-failing", "pep688-fixed-hash", "pep688-unhashable",
    "pep688-failing-hash", "callable",
})
REPLACEMENT_STYLES = frozenset({
    "literal", "escaped-named", "escaped-numeric", "missing-capture",
    "invalid-escape", "callable", "callable-error",
})
BUFFER_BEHAVIORS = frozenset({"none", "stable", "mutate", "fail"})
HASH_BEHAVIORS = frozenset({"none", "fixed", "unhashable", "fail"})
FORBIDDEN_ENGINE_ROOTS = frozenset({
    "_regex", "candidates", "fancy_regex", "google_re2", "hyperscan",
    "onig", "oniguruma", "pcre", "pcre2", "re2", "regex", "rebar",
    "rust_regex", "sre_compile", "sre_constants", "sre_parse", "vectorscan",
})


class SubstitutionOracleError(Exception):
    """A complete frozen substitution obligation or reference was forged."""


class SourceOnlyError(SubstitutionOracleError):
    """A synthetic control attempted an external effect."""


class ReferenceWorkerFailure(SubstitutionOracleError):
    """Preserve a complete failing genuinely isolated reference worker."""

    def __init__(self, message: str, evidence: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.evidence = dict(evidence)


class ReplacementCallbackError(Exception):
    """A deterministic public replacement callback raised intentionally."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise SubstitutionOracleError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, OverflowError) as error:
        raise SubstitutionOracleError("substitution evidence is not complete canonical JSON") from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_digest(value: Any) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and len(set(value)) > 1
        and all(letter in "0123456789abcdef" for letter in value)
    )


def checked_digest(value: Any, label: str) -> str:
    require(valid_digest(value), "an exact prospectively frozen SHA-256 is required: " + label)
    return value


def unique_json_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result, "duplicate JSON fields hide a mismatch")
        result[key] = value
    return result


def decode_canonical(raw: Any, label: str) -> dict[str, Any]:
    require(
        type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
        "a complete bounded reference stream is mandatory: " + label,
    )

    def reject_constant(_: str) -> Any:
        raise SubstitutionOracleError("nonfinite substitution evidence is forbidden")

    try:
        result = json.loads(
            raw,
            object_pairs_hook=unique_json_object,
            parse_constant=reject_constant,
        )
    except (SubstitutionOracleError, TypeError, ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise SubstitutionOracleError("invalid complete reference evidence: " + label) from error
    require(
        type(result) is dict and canonical(result) == raw,
        "reference evidence was truncated, reordered, extended, or substituted",
    )
    return result


def encode_bytes(value: bytes) -> dict[str, str]:
    require(type(value) is bytes, "an exact bytes payload is mandatory")
    return {"kind": "bytes", "hex": value.hex()}


def encode_text(value: str) -> dict[str, str]:
    require(type(value) is str, "an exact Unicode payload is mandatory")
    return {"kind": "str", "value": value}


def validate_payload(value: Any) -> dict[str, str]:
    require(type(value) is dict, "an exact typed payload is mandatory")
    if value.get("kind") == "str":
        require(
            set(value) == {"kind", "value"} and type(value.get("value")) is str,
            "an original Unicode payload was forged",
        )
        return value
    require(
        set(value) == {"kind", "hex"}
        and value.get("kind") == "bytes"
        and type(value.get("hex")) is str,
        "an original bytes payload was forged",
    )
    try:
        raw = bytes.fromhex(value["hex"])
    except ValueError as error:
        raise SubstitutionOracleError("a substitution payload has invalid hexadecimal") from error
    require(raw.hex() == value["hex"], "a substitution payload is noncanonical")
    return value


def make_carrier(
    kind: str,
    payload: bytes | str,
    *,
    role: str,
) -> dict[str, Any]:
    approved = SUBJECT_KINDS if role == "subject" else REPLACEMENT_KINDS
    require(role in {"subject", "replacement"} and kind in approved, "an unfrozen carrier was selected")
    if type(payload) is str:
        require(kind in {"str", "callable"}, "a Unicode payload entered a binary carrier")
        encoded = encode_text(payload)
        length = len(payload)
    else:
        require(type(payload) is bytes and kind != "str", "an exact binary carrier is mandatory")
        encoded = encode_bytes(payload)
        length = len(payload)
    readonly = kind.startswith("readonly-") or kind.startswith("released-readonly-")
    if kind == "pep688-wrapped-readonly":
        readonly = True
    step = 2 if "strided" in kind else 1
    released = kind.startswith("released-")
    if kind.startswith("pep688-"):
        if "mutating" in kind:
            behavior = "mutate"
        elif kind == "pep688-failing":
            behavior = "fail"
        else:
            behavior = "stable"
        hash_behavior = (
            "fixed" if "fixed-hash" in kind
            else "unhashable" if "unhashable" in kind
            else "fail" if "failing-hash" in kind
            else "none"
        )
    else:
        behavior = "none"
        hash_behavior = "none"
    return {
        "kind": kind,
        "payload": encoded,
        "start": 0,
        "stop": length,
        "step": step,
        "readonly": readonly,
        "released": released,
        "behavior": behavior,
        "hash_behavior": hash_behavior,
        "wrapped": kind.startswith("pep688-wrapped-"),
    }


def validate_carrier(value: Any, *, role: str) -> dict[str, Any]:
    approved = SUBJECT_KINDS if role == "subject" else REPLACEMENT_KINDS
    require(
        role in {"subject", "replacement"}
        and type(value) is dict
        and set(value) == {
            "kind", "payload", "start", "stop", "step", "readonly",
            "released", "behavior", "hash_behavior", "wrapped",
        }
        and value.get("kind") in approved
        and type(value.get("start")) is int
        and type(value.get("stop")) is int
        and type(value.get("step")) is int
        and value["step"] in (1, 2)
        and type(value.get("readonly")) is bool
        and type(value.get("released")) is bool
        and type(value.get("wrapped")) is bool
        and value.get("behavior") in BUFFER_BEHAVIORS
        and value.get("hash_behavior") in HASH_BEHAVIORS,
        "a complete original carrier, exporter, shape, or ownership was forged: " + role,
    )
    payload = validate_payload(value["payload"])
    length = len(payload["value"]) if payload["kind"] == "str" else len(bytes.fromhex(payload["hex"]))
    require(
        0 <= value["start"] <= value["stop"] <= length,
        "a frozen carrier escaped its actual original storage bounds",
    )
    kind = value["kind"]
    require(
        (value["step"] == 2) is ("strided" in kind),
        "a real memoryview stride was concealed",
    )
    require(
        value["released"] is kind.startswith("released-"),
        "a real released memoryview was substituted",
    )
    require(
        value["wrapped"] is kind.startswith("pep688-wrapped-"),
        "a nested PEP-688 memoryview wrapper was substituted",
    )
    if kind.startswith("pep688-"):
        expected_behavior = (
            "mutate" if "mutating" in kind
            else "fail" if kind == "pep688-failing"
            else "stable"
        )
        expected_hash = (
            "fixed" if "fixed-hash" in kind
            else "unhashable" if "unhashable" in kind
            else "fail" if "failing-hash" in kind
            else "none"
        )
        require(
            value["behavior"] == expected_behavior
            and value["hash_behavior"] == expected_hash,
            "a genuine tracked exporter, buffer failure, or custom hash was forged",
        )
    else:
        require(
            value["behavior"] == "none" and value["hash_behavior"] == "none",
            "an ordinary carrier impersonated a tracked buffer exporter",
        )
    if kind == "str":
        require(payload["kind"] == "str", "a Unicode subject lost its exact string domain")
    elif kind != "callable":
        require(payload["kind"] == "bytes", "a binary carrier lost its exact bytes domain")
    return value


def build_matrix(seed: int = PUBLISHED_SEED) -> list[dict[str, Any]]:
    require(type(seed) is int and 0 <= seed < 1 << 64, "a genuine published 64-bit seed is required")
    seeded = random.Random(seed)
    cases: list[dict[str, Any]] = []
    for cohort in COHORTS:
        for variant in range(VARIANTS_PER_COHORT):
            suffix = "".join(seeded.choice("abcdef0123456789") for _ in range(12))
            text_domain = cohort.startswith("text-")
            if text_domain:
                source_text = "caf\u00e942 beta7 e\u0301 \ud800 delta3 " + suffix
                payload: bytes | str = source_text
                pattern: bytes | str = r"(?P<word>\w+?)(?P<number>[0-9]+)"
                literal: bytes | str = "X"
                named: bytes | str = r"<\g<word>:\g<number>>"
                numbered: bytes | str = r"<\1:\2>"
            else:
                payload = ("alpha42 beta7 gamma3 " + suffix).encode("ascii")
                pattern = rb"(?P<word>[A-Za-z]+)(?P<number>[0-9]*)"
                literal = b"X"
                named = rb"<\g<word>:\g<number>>"
                numbered = rb"<\1:\2>"

            subject_kind = "str" if text_domain else "bytes"
            replacement_kind = "str" if text_domain else "bytes"
            style = ("literal", "escaped-named", "escaped-numeric", "callable")[variant % 4]
            if "literal" in cohort:
                style = "literal"
            elif "callback-error" in cohort:
                style = "callable-error"
            elif "callback" in cohort:
                style = "callable"
            elif "missing-capture" in cohort:
                style = "missing-capture"
            elif "invalid-escape" in cohort:
                style = "invalid-escape"
            elif "numeric-captures" in cohort:
                style = "escaped-numeric"
            elif "escaped" in cohort or "named-captures" in cohort:
                style = "escaped-named"

            if "zero-width-lookahead" in cohort:
                pattern = r"(?=\w)" if text_domain else rb"(?=[A-Za-z])"
            elif "zero-width-empty" in cohort:
                pattern = r"" if text_domain else rb""
            elif "lone-surrogate" in cohort:
                pattern = "\ud800"
            elif "combining-mark" in cohort:
                pattern = "e\u0301"
            elif "precomposed-unicode" in cohort:
                pattern = "\u00e9"

            if cohort.startswith("bytearray-subject-"):
                subject_kind = "bytearray"
            elif cohort.startswith("bytearray-replacement-"):
                replacement_kind = "bytearray"
            elif "subject-memoryview" in cohort:
                subject_kind = cohort.removesuffix("-subject-memoryview") + "-memoryview"
            elif "template-memoryview" in cohort:
                replacement_kind = cohort.removesuffix("-template-memoryview") + "-memoryview"
            elif cohort.startswith("pep688-") and cohort.endswith("-subject"):
                subject_kind = cohort.removesuffix("-subject")
            elif cohort.startswith("pep688-") and cohort.endswith("-template"):
                replacement_kind = cohort.removesuffix("-template")

            if cohort == "nested-stable-subject-and-template":
                subject_kind, replacement_kind = "pep688-stable", "pep688-stable"
            elif cohort == "nested-mutating-subject-and-template":
                subject_kind, replacement_kind = "pep688-mutating", "pep688-mutating"
            elif cohort == "nested-stable-fixed-hash-template":
                subject_kind, replacement_kind = "pep688-stable", "pep688-fixed-hash"
            elif cohort == "nested-mutating-unhashable-template":
                subject_kind, replacement_kind = "pep688-mutating", "pep688-unhashable"
            elif cohort == "nested-failing-template-after-subject":
                subject_kind, replacement_kind = "pep688-stable", "pep688-failing"
            elif cohort == "match-expand-buffer-retention":
                subject_kind, replacement_kind = "writable-memoryview", "readonly-memoryview"
            elif cohort == "callback-capture-and-buffer-order":
                subject_kind, replacement_kind = "pep688-stable", "callable"
                style = "callable"

            if cohort == "text-cross-domain-bytes-template":
                replacement_kind = "bytes"
                replacement_payload: bytes | str = b"X"
            elif style == "literal":
                replacement_payload = literal
            elif style == "escaped-named":
                replacement_payload = named
            elif style == "escaped-numeric":
                replacement_payload = numbered
            elif style == "missing-capture":
                replacement_payload = r"\g<absent>" if text_domain else rb"\g<absent>"
            elif style == "invalid-escape":
                replacement_payload = r"\q" if text_domain else rb"\q"
            else:
                replacement_payload = literal

            if replacement_kind == "callable" or style.startswith("callable"):
                replacement_kind = "callable"
            api = APIS[variant % len(APIS)]
            if cohort == "match-expand-buffer-retention":
                api = "match.expand"
            replacement = make_carrier(
                replacement_kind,
                replacement_payload,
                role="replacement",
            )
            subject = make_carrier(subject_kind, payload, role="subject")
            case = {
                "case": "substitution-buffer-semantics.v1." + format(len(cases), "05d"),
                "cohort": cohort,
                "variant": variant,
                "seed": seed,
                "api": api,
                "flags": FLAGS[variant % len(FLAGS)],
                "count": COUNTS[(variant // len(APIS)) % len(COUNTS)],
                "pos": WINDOW_STARTS[variant % len(WINDOW_STARTS)],
                "endpos": WINDOW_ENDS[(variant // len(WINDOW_STARTS)) % len(WINDOW_ENDS)],
                "pattern": encode_text(pattern) if type(pattern) is str else encode_bytes(pattern),
                "subject": subject,
                "replacement": replacement,
                "replacement_style": style,
                "callback_raises": style == "callable-error",
            }
            cases.append(case)
    return cases


def validate_matrix(
    matrix: Any, expected_sha256: str = MATRIX_SHA256,
) -> str:
    checked_digest(expected_sha256, "prospectively frozen substitution case matrix")
    require(
        len(COHORTS) == 64
        and len(set(COHORTS)) == 64
        and VARIANTS_PER_COHORT == 80
        and CASE_COUNT == 5_120,
        "the balanced original substitution obligation denominator silently changed",
    )
    require(
        type(matrix) is list and len(matrix) == CASE_COUNT,
        "all 5,120 independently frozen replacement-buffer cases are mandatory",
    )
    actual = build_matrix()
    require(
        matrix == actual and digest(matrix) == expected_sha256,
        "the exact substitution seed, ordered case rows, or matrix digest changed",
    )
    coverage: dict[str, int] = {name: 0 for name in COHORTS}
    identifiers: set[str] = set()
    for index, row in enumerate(matrix):
        require(
            type(row) is dict
            and set(row) == {
                "case", "cohort", "variant", "seed", "api", "flags", "count",
                "pos", "endpos", "pattern", "subject", "replacement",
                "replacement_style", "callback_raises",
            }
            and row.get("case") == "substitution-buffer-semantics.v1." + format(index, "05d")
            and row["case"] not in identifiers
            and row.get("cohort") == COHORTS[index // VARIANTS_PER_COHORT]
            and type(row.get("variant")) is int
            and row["variant"] == index % VARIANTS_PER_COHORT
            and type(row.get("seed")) is int
            and row["seed"] == PUBLISHED_SEED
            and row.get("api") in APIS
            and type(row.get("flags")) is int
            and row["flags"] in FLAGS
            and type(row.get("count")) is int
            and row["count"] in COUNTS
            and type(row.get("pos")) is int
            and row["pos"] in WINDOW_STARTS
            and (row.get("endpos") is None or type(row.get("endpos")) is int)
            and row["endpos"] in WINDOW_ENDS
            and row.get("replacement_style") in REPLACEMENT_STYLES
            and type(row.get("callback_raises")) is bool,
            "a complete original replacement case was removed, reordered, or forged",
        )
        validate_payload(row["pattern"])
        validate_carrier(row["subject"], role="subject")
        validate_carrier(row["replacement"], role="replacement")
        require(
            row["callback_raises"] is (row["replacement_style"] == "callable-error"),
            "a genuine failing replacement callback was concealed",
        )
        identifiers.add(row["case"])
        coverage[row["cohort"]] += 1
    require(
        all(count == VARIANTS_PER_COHORT for count in coverage.values()),
        "an entire replacement-buffer cohort silently changed weight",
    )
    return expected_sha256


class TrackedExporter:
    """A PEP-688 exporter retaining exact nested acquisition and release order."""

    __slots__ = ("backing", "behavior", "events", "role", "active")

    def __init__(
        self,
        payload: bytes,
        behavior: str,
        events: list[dict[str, Any]],
        role: str,
    ) -> None:
        require(
            type(payload) is bytes
            and behavior in {"stable", "mutate", "fail"}
            and type(events) is list
            and role in {"subject", "replacement"},
            "a genuine PEP-688 replacement exporter was forged",
        )
        self.backing = bytearray(payload)
        self.behavior = behavior
        self.events = events
        self.role = role
        self.active = 0

    def __buffer__(self, flags: int) -> memoryview:
        require(
            type(flags) is int and flags >= 0,
            "a genuine exact CPython PEP-688 acquisition flag is mandatory",
        )
        before = bytes(self.backing).hex()
        if self.behavior == "fail":
            self.events.append({
                "event": "acquire-error",
                "role": self.role,
                "flags": flags,
                "active_before": self.active,
                "active_after": self.active,
                "backing_before_hex": before,
                "backing_after_hex": before,
                "behavior": self.behavior,
            })
            raise BufferError("frozen substitution " + self.role + " exporter failure")
        previous = self.active
        self.active += 1
        self.events.append({
            "event": "acquire",
            "role": self.role,
            "flags": flags,
            "active_before": previous,
            "active_after": self.active,
            "backing_before_hex": before,
            "backing_after_hex": before,
            "behavior": self.behavior,
        })
        return memoryview(self.backing)

    def __release_buffer__(self, view: memoryview) -> None:
        require(
            type(view) is memoryview and self.active > 0,
            "a PEP-688 export was released without its exact original view",
        )
        before = bytes(self.backing).hex()
        if self.behavior == "mutate":
            replacement = b"!" * len(self.backing)
            require(len(replacement) == len(self.backing), "release must not resize live storage")
            self.backing[:] = replacement
        previous = self.active
        self.active -= 1
        self.events.append({
            "event": "release",
            "role": self.role,
            "flags": None,
            "active_before": previous,
            "active_after": self.active,
            "backing_before_hex": before,
            "backing_after_hex": bytes(self.backing).hex(),
            "behavior": self.behavior,
        })


class FixedHashExporter(TrackedExporter):
    __slots__ = ()

    def __hash__(self) -> int:
        self.events.append({
            "event": "hash",
            "role": self.role,
            "flags": None,
            "active_before": self.active,
            "active_after": self.active,
            "backing_before_hex": bytes(self.backing).hex(),
            "backing_after_hex": bytes(self.backing).hex(),
            "behavior": self.behavior,
            "hash_result": 1729,
        })
        return 1729


class UnhashableExporter(TrackedExporter):
    __slots__ = ()
    __hash__ = None


class FailingHashExporter(TrackedExporter):
    __slots__ = ()

    def __hash__(self) -> int:
        self.events.append({
            "event": "hash-error",
            "role": self.role,
            "flags": None,
            "active_before": self.active,
            "active_after": self.active,
            "backing_before_hex": bytes(self.backing).hex(),
            "backing_after_hex": bytes(self.backing).hex(),
            "behavior": self.behavior,
        })
        raise TypeError("frozen substitution replacement exporter hash failure")


def decode_payload(value: Mapping[str, Any]) -> str | bytes:
    validate_payload(value)
    if value["kind"] == "str":
        return value["value"]
    return bytes.fromhex(value["hex"])


def decode_carrier(
    value: Mapping[str, Any],
    events: list[dict[str, Any]],
    *,
    role: str,
) -> tuple[Any, TrackedExporter | None, list[memoryview]]:
    validate_carrier(value, role=role)
    payload = decode_payload(value["payload"])
    kind = value["kind"]
    if kind == "str":
        return payload, None, []
    if kind == "callable":
        return payload, None, []
    require(type(payload) is bytes, "a binary replacement carrier was substituted")
    start, stop, step = value["start"], value["stop"], value["step"]
    if kind == "bytes":
        return payload[start:stop:step], None, []
    if kind == "bytearray":
        return bytearray(payload[start:stop:step]), None, []
    if "memoryview" in kind:
        backing: bytes | bytearray = payload if value["readonly"] else bytearray(payload)
        actual = memoryview(backing)[start:stop:step]
        if value["released"]:
            actual.release()
        return actual, None, [actual]
    if value["hash_behavior"] == "fixed":
        exporter: TrackedExporter = FixedHashExporter(payload, value["behavior"], events, role)
    elif value["hash_behavior"] == "unhashable":
        exporter = UnhashableExporter(payload, value["behavior"], events, role)
    elif value["hash_behavior"] == "fail":
        exporter = FailingHashExporter(payload, value["behavior"], events, role)
    else:
        exporter = TrackedExporter(payload, value["behavior"], events, role)
    if value["wrapped"]:
        actual = memoryview(exporter)
        if value["readonly"]:
            readonly = actual.toreadonly()
            actual.release()
            actual = readonly
        return actual, exporter, [actual]
    return exporter, exporter, []


def normalize_value(value: Any) -> dict[str, Any]:
    if value is None:
        return {"type": "none"}
    if type(value) is bool:
        return {"type": "bool", "value": value}
    if type(value) is int:
        return {"type": "int", "value": value}
    if type(value) is str:
        return {"type": "str", "value": value}
    if type(value) is bytes:
        return {"type": "bytes", "hex": value.hex()}
    if type(value) is bytearray:
        return {"type": "bytearray", "hex": bytes(value).hex()}
    if type(value) is memoryview:
        try:
            return {
                "type": "memoryview",
                "hex": value.tobytes().hex(),
                "readonly": value.readonly,
                "format": value.format,
                "itemsize": value.itemsize,
                "ndim": value.ndim,
                "shape": list(value.shape) if value.shape is not None else None,
                "strides": list(value.strides) if value.strides is not None else None,
                "contiguous": value.contiguous,
                "c_contiguous": value.c_contiguous,
                "f_contiguous": value.f_contiguous,
            }
        except ValueError as error:
            return {
                "type": "released-memoryview",
                "exception_module": type(error).__module__,
                "exception_type": type(error).__qualname__,
                "exception_args": normalize_value(error.args),
            }
    if isinstance(value, TrackedExporter):
        return {
            "type": "pep688-exporter",
            "role": value.role,
            "behavior": value.behavior,
            "backing_hex": bytes(value.backing).hex(),
            "active_exports": value.active,
            "hash_kind": (
                "fixed" if isinstance(value, FixedHashExporter)
                else "unhashable" if isinstance(value, UnhashableExporter)
                else "fail" if isinstance(value, FailingHashExporter)
                else "identity"
            ),
        }
    if type(value) in (tuple, list):
        return {
            "type": "tuple" if type(value) is tuple else "list",
            "items": [normalize_value(item) for item in value],
        }
    if type(value) is dict:
        pairs = [[normalize_value(key), normalize_value(item)] for key, item in value.items()]
        pairs.sort(key=lambda pair: canonical(pair[0]))
        return {"type": "dict", "items": pairs}
    raise SubstitutionOracleError(
        "a complete replacement-buffer value was omitted: " + type(value).__qualname__
    )


def validate_normalized_value(value: Any) -> None:
    require(type(value) is dict and type(value.get("type")) is str, "a strictly typed value is required")
    kind = value["type"]
    if kind == "none":
        require(set(value) == {"type"}, "a null substitution result was forged")
    elif kind in {"bool", "int", "str"}:
        exact = {"bool": bool, "int": int, "str": str}[kind]
        require(
            set(value) == {"type", "value"} and type(value.get("value")) is exact,
            "a substitution scalar lost its exact Python type",
        )
    elif kind in {"bytes", "bytearray"}:
        require(
            set(value) == {"type", "hex"} and type(value.get("hex")) is str,
            "a bytes replacement lost its original carrier type",
        )
        try:
            actual = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise SubstitutionOracleError("a substitution result hex is invalid") from error
        require(actual.hex() == value["hex"], "a substitution result hex is noncanonical")
    elif kind in {"tuple", "list"}:
        require(
            set(value) == {"type", "items"} and type(value.get("items")) is list,
            "a regex result lost its exact tuple/list type",
        )
        for item in value["items"]:
            validate_normalized_value(item)
    elif kind == "dict":
        require(
            set(value) == {"type", "items"} and type(value.get("items")) is list,
            "a substitution mapping was forged",
        )
        previous: bytes | None = None
        for pair in value["items"]:
            require(type(pair) is list and len(pair) == 2, "a mapping entry was omitted")
            validate_normalized_value(pair[0])
            validate_normalized_value(pair[1])
            current = canonical(pair[0])
            require(previous is None or previous < current, "a mapping key was repeated or reordered")
            previous = current
    elif kind == "memoryview":
        require(
            set(value) == {
                "type", "hex", "readonly", "format", "itemsize", "ndim",
                "shape", "strides", "contiguous", "c_contiguous", "f_contiguous",
            }
            and type(value.get("readonly")) is bool
            and type(value.get("format")) is str
            and type(value.get("itemsize")) is int
            and type(value.get("ndim")) is int
            and all(type(value.get(name)) is bool for name in (
                "contiguous", "c_contiguous", "f_contiguous",
            )),
            "a real memoryview shape, flags, or mutability was hidden",
        )
        require(type(value.get("hex")) is str, "a memoryview payload is mandatory")
        try:
            actual = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise SubstitutionOracleError("memoryview observation hex is invalid") from error
        require(actual.hex() == value["hex"], "memoryview observation hex is noncanonical")
        for name in ("shape", "strides"):
            current = value[name]
            require(
                current is None
                or (type(current) is list and all(type(part) is int for part in current)),
                "a genuine memoryview dimension was replaced",
            )
    elif kind == "released-memoryview":
        require(
            set(value) == {"type", "exception_module", "exception_type", "exception_args"}
            and type(value.get("exception_module")) is str
            and type(value.get("exception_type")) is str,
            "the exact genuine released-memoryview error was hidden",
        )
        validate_normalized_value(value["exception_args"])
    elif kind == "pep688-exporter":
        require(
            set(value) == {
                "type", "role", "behavior", "backing_hex", "active_exports", "hash_kind",
            }
            and value.get("role") in {"subject", "replacement"}
            and value.get("behavior") in {"stable", "mutate", "fail"}
            and value.get("hash_kind") in {"identity", "fixed", "unhashable", "fail"}
            and type(value.get("backing_hex")) is str
            and type(value.get("active_exports")) is int
            and value["active_exports"] >= 0,
            "a tracked substitution exporter was forged or leaked",
        )
        try:
            actual = bytes.fromhex(value["backing_hex"])
        except ValueError as error:
            raise SubstitutionOracleError("a tracked exporter payload is invalid") from error
        require(actual.hex() == value["backing_hex"], "a tracked exporter payload is noncanonical")
    else:
        raise SubstitutionOracleError("an unfrozen substitution result type was injected")


def normalize_error(error: BaseException, engine: Any) -> dict[str, Any]:
    public = getattr(engine, "error", None)
    if isinstance(public, type) and isinstance(error, public):
        return {
            "kind": "public-regex-error",
            "type": type(error).__qualname__,
            "args": normalize_value(error.args),
            "message": normalize_value(getattr(error, "msg", None)),
            "pattern": normalize_value(getattr(error, "pattern", None)),
            "position": normalize_value(getattr(error, "pos", None)),
            "line": normalize_value(getattr(error, "lineno", None)),
            "column": normalize_value(getattr(error, "colno", None)),
        }
    return {
        "kind": "ordinary-python-error",
        "module": (
            ORACLE_CALLBACK_CANONICAL_MODULE
            if type(error) is ReplacementCallbackError
            else type(error).__module__
        ),
        "type": type(error).__qualname__,
        "message": str(error),
        "args": normalize_value(error.args),
    }


def validate_error(value: Any) -> None:
    require(type(value) is dict, "an exact public replacement exception is mandatory")
    if value.get("kind") == "ordinary-python-error":
        require(
            set(value) == {"kind", "module", "type", "message", "args"}
            and type(value.get("module")) is str
            and type(value.get("type")) is str
            and type(value.get("message")) is str,
            "a genuine Python exception class or module was concealed",
        )
        validate_normalized_value(value["args"])
        return
    require(
        value.get("kind") == "public-regex-error"
        and set(value) == {
            "kind", "type", "args", "message", "pattern", "position", "line", "column",
        }
        and type(value.get("type")) is str,
        "a genuine Python PatternError and exact position were concealed",
    )
    for key in ("args", "message", "pattern", "position", "line", "column"):
        validate_normalized_value(value[key])


def normalize_match(match: Any, subject: Any, pattern: Any) -> dict[str, Any]:
    return {
        "pattern_is_expected": match.re is pattern,
        "string_is_subject": match.string is subject,
        "string": normalize_value(match.string),
        "group": normalize_value(match.group()),
        "groups": normalize_value(match.groups()),
        "groupdict": normalize_value(match.groupdict()),
        "regs": normalize_value(match.regs),
        "lastindex": normalize_value(match.lastindex),
        "lastgroup": normalize_value(match.lastgroup),
        "pos": normalize_value(match.pos),
        "endpos": normalize_value(match.endpos),
    }


def validate_match(value: Any) -> None:
    require(
        type(value) is dict
        and set(value) == {
            "pattern_is_expected", "string_is_subject", "string", "group", "groups",
            "groupdict", "regs", "lastindex", "lastgroup", "pos", "endpos",
        }
        and value.get("pattern_is_expected") is True
        and value.get("string_is_subject") is True,
        "a callback or retained match borrowed a foreign regex object",
    )
    for key in (
        "string", "group", "groups", "groupdict", "regs", "lastindex",
        "lastgroup", "pos", "endpos",
    ):
        validate_normalized_value(value[key])


def normalize_warnings(observed: Sequence[Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for item in observed:
        require(
            isinstance(item.category, type)
            and isinstance(item.message, item.category),
            "a genuine original Python warning was substituted",
        )
        result.append({
            "category_module": item.category.__module__,
            "category": item.category.__qualname__,
            "message": str(item.message),
        })
    return result


def validate_events(
    events: Any,
    *,
    require_balanced: bool = False,
    expected_acquisition_flags: tuple[int, ...] | None = None,
) -> list[dict[str, Any]]:
    require(type(events) is list, "a complete ordered PEP-688 event ledger is mandatory")
    active = {"subject": 0, "replacement": 0}
    ownership_stack: list[str] = []
    acquisition_flags: list[int] = []
    for record in events:
        require(
            type(record) is dict and type(record.get("event")) is str,
            "an exact ordered buffer acquisition event was hidden",
        )
        kind = record["event"]
        if kind == "phase":
            require(
                set(record) == {"event", "name"}
                and type(record.get("name")) is str
                and bool(record["name"]),
                "a genuine substitution phase was forged",
            )
            continue
        if kind == "callback":
            require(
                set(record) == {"event", "index", "match", "raises"}
                and type(record.get("index")) is int
                and record["index"] >= 0
                and type(record.get("raises")) is bool,
                "a genuine replacement callback and ordering was forged",
            )
            validate_match(record["match"])
            continue
        required = {
            "event", "role", "flags", "active_before", "active_after",
            "backing_before_hex", "backing_after_hex", "behavior",
        }
        expected_keys = required | ({"hash_result"} if kind == "hash" else set())
        require(
            kind in {"acquire", "acquire-error", "release", "hash", "hash-error"}
            and set(record) == expected_keys
            and record.get("role") in active
            and type(record.get("active_before")) is int
            and type(record.get("active_after")) is int
            and record["active_before"] >= 0
            and record["active_after"] >= 0
            and type(record.get("backing_before_hex")) is str
            and type(record.get("backing_after_hex")) is str
            and record.get("behavior") in {"stable", "mutate", "fail"},
            "a nested buffer flag, hash, storage, or exporter owner was forged",
        )
        for key in ("backing_before_hex", "backing_after_hex"):
            try:
                actual = bytes.fromhex(record[key])
            except ValueError as error:
                raise SubstitutionOracleError("a genuine buffer event contains invalid hex") from error
            require(actual.hex() == record[key], "a genuine buffer event hex is noncanonical")
        role = record["role"]
        require(record["active_before"] == active[role], "a nested exporter acquisition was reordered")
        if kind == "acquire":
            require(
                type(record.get("flags")) is int
                and record["flags"] in {SIMPLE_BUFFER_FLAG, FULL_READONLY_BUFFER_FLAG}
                and record["behavior"] != "fail"
                and record["active_after"] == active[role] + 1
                and record["backing_after_hex"] == record["backing_before_hex"],
                "a genuine SIMPLE or FULL buffer acquisition was forged",
            )
            ownership_stack.append(role)
            acquisition_flags.append(record["flags"])
            active[role] += 1
        elif kind == "acquire-error":
            require(
                type(record.get("flags")) is int
                and record["flags"] in {SIMPLE_BUFFER_FLAG, FULL_READONLY_BUFFER_FLAG}
                and record["behavior"] == "fail"
                and record["active_after"] == active[role]
                and record["backing_after_hex"] == record["backing_before_hex"],
                "a genuine failing PEP-688 acquisition was hidden",
            )
        elif kind == "release":
            require(
                record.get("flags") is None
                and active[role] > 0
                and record["active_after"] == active[role] - 1
                and bool(ownership_stack)
                and ownership_stack[-1] == role,
                "a nested buffer release was leaked, repeated, or reordered",
            )
            if record["behavior"] == "mutate":
                previous = bytes.fromhex(record["backing_before_hex"])
                require(
                    record["backing_after_hex"] == (b"!" * len(previous)).hex(),
                    "a mutating exporter did not preserve exact equal-length storage",
                )
            else:
                require(
                    record["backing_after_hex"] == record["backing_before_hex"],
                    "a stable exporter silently mutated original storage",
                )
            ownership_stack.pop()
            active[role] -= 1
        elif kind == "hash":
            require(
                record.get("flags") is None
                and record["active_after"] == active[role]
                and type(record.get("hash_result")) is int
                and record["hash_result"] == 1729,
                "an exact deterministic custom exporter hash was forged",
            )
        else:
            require(
                record.get("flags") is None
                and record["active_after"] == active[role],
                "a genuine custom hash exception was hidden",
            )
    require(type(require_balanced) is bool, "an exact buffer-balance policy is mandatory")
    if expected_acquisition_flags is not None:
        require(
            type(expected_acquisition_flags) is tuple
            and all(type(flag) is int for flag in expected_acquisition_flags)
            and tuple(acquisition_flags) == expected_acquisition_flags,
            "the exact nested SIMPLE, SIMPLE, FULL-READONLY acquisition flags changed",
        )
    if require_balanced:
        require(
            all(count == 0 for count in active.values()) and not ownership_stack,
            "a complete nested PEP-688 acquisition or release was omitted",
        )
    return events


def execute_case(case: Mapping[str, Any], engine: Any) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    callbacks: list[dict[str, Any]] = []
    views: list[memoryview] = []
    subject: Any = None
    replacement: Any = None
    subject_tracker: TrackedExporter | None = None
    replacement_tracker: TrackedExporter | None = None
    stage = "materialize"
    status = "raise"
    observed_value: dict[str, Any] | None = None
    observed_error: dict[str, Any] | None = None
    warning_results: list[dict[str, str]] = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            events.append({"event": "phase", "name": "materialize-start"})
            pattern = decode_payload(case["pattern"])
            subject, subject_tracker, subject_views = decode_carrier(
                case["subject"], events, role="subject",
            )
            views.extend(subject_views)
            replacement, replacement_tracker, template_views = decode_carrier(
                case["replacement"], events, role="replacement",
            )
            views.extend(template_views)
            events.append({"event": "phase", "name": "materialize-complete"})
            stage = "compile"
            compiled = engine.compile(pattern, case["flags"])

            def callback(match: Any) -> Any:
                observed = normalize_match(match, subject, compiled)
                entry = {
                    "event": "callback",
                    "index": len(callbacks),
                    "match": observed,
                    "raises": case["callback_raises"],
                }
                events.append(entry)
                callbacks.append(copy.deepcopy(entry))
                if case["callback_raises"]:
                    raise ReplacementCallbackError("frozen substitution callback failure")
                value = decode_payload(case["replacement"]["payload"])
                return value

            selected = callback if case["replacement_style"] in {"callable", "callable-error"} else replacement
            stage = case["api"]
            events.append({"event": "phase", "name": "operation-start"})
            if stage == "module.sub":
                actual = engine.sub(
                    pattern, selected, subject,
                    count=case["count"], flags=case["flags"],
                )
            elif stage == "module.subn":
                actual = engine.subn(
                    pattern, selected, subject,
                    count=case["count"], flags=case["flags"],
                )
            elif stage == "pattern.sub":
                actual = compiled.sub(selected, subject, count=case["count"])
            elif stage == "pattern.subn":
                actual = compiled.subn(selected, subject, count=case["count"])
            elif stage == "match.expand":
                if case["endpos"] is None:
                    match = compiled.search(subject, case["pos"])
                else:
                    match = compiled.search(subject, case["pos"], case["endpos"])
                actual = None if match is None else match.expand(selected)
            else:
                raise SubstitutionOracleError("an unfrozen substitution API was injected")
            observed_value = normalize_value(actual)
            status = "return"
            events.append({"event": "phase", "name": "operation-return"})
        except SubstitutionOracleError:
            raise
        except Exception as error:
            observed_error = normalize_error(error, engine)
            events.append({"event": "phase", "name": "operation-raise"})
        finally:
            for view in reversed(views):
                try:
                    view.release()
                except ValueError:
                    pass
            events.append({"event": "phase", "name": "cleanup-complete"})
            warning_results = normalize_warnings(caught)
    result = {
        "status": status,
        "stage": stage,
        "value": observed_value,
        "exception": observed_error,
        "events": copy.deepcopy(events),
        "callbacks": copy.deepcopy(callbacks),
        "warnings": warning_results,
        "subject_after": normalize_value(subject),
        "replacement_after": normalize_value(replacement),
        "subject_active_exports": subject_tracker.active if subject_tracker is not None else 0,
        "replacement_active_exports": replacement_tracker.active if replacement_tracker is not None else 0,
        "count_requested": case["count"],
        "pos_requested": case["pos"],
        "endpos_requested": case["endpos"],
    }
    validate_outcome(result)
    return result


def validate_outcome(value: Any) -> dict[str, Any]:
    require(
        type(value) is dict
        and set(value) == {
            "status", "stage", "value", "exception", "events", "callbacks",
            "warnings", "subject_after", "replacement_after",
            "subject_active_exports", "replacement_active_exports",
            "count_requested", "pos_requested", "endpos_requested",
        }
        and value.get("status") in {"return", "raise"}
        and type(value.get("stage")) is str
        and type(value.get("callbacks")) is list
        and type(value.get("warnings")) is list
        and type(value.get("subject_active_exports")) is int
        and value["subject_active_exports"] >= 0
        and type(value.get("replacement_active_exports")) is int
        and value["replacement_active_exports"] >= 0
        and type(value.get("count_requested")) is int
        and type(value.get("pos_requested")) is int
        and (value.get("endpos_requested") is None or type(value.get("endpos_requested")) is int),
        "a complete substitution value, error, buffer ledger, or boundary was omitted",
    )
    validate_events(value["events"])
    for role, key in (
        ("subject", "subject_active_exports"),
        ("replacement", "replacement_active_exports"),
    ):
        acquisitions = sum(
            1 for event in value["events"]
            if event.get("event") == "acquire" and event.get("role") == role
        )
        releases = sum(
            1 for event in value["events"]
            if event.get("event") == "release" and event.get("role") == role
        )
        require(
            value[key] == acquisitions - releases,
            "a live or released nested exporter was omitted: " + role,
        )
    validate_normalized_value(value["subject_after"])
    validate_normalized_value(value["replacement_after"])
    if value["status"] == "return":
        require(value["exception"] is None, "a successful replacement hides an exception")
        validate_normalized_value(value["value"])
    else:
        require(value["value"] is None, "a failed replacement hides a return value")
        validate_error(value["exception"])
    for callback in value["callbacks"]:
        require(
            type(callback) is dict
            and set(callback) == {"event", "index", "match", "raises"}
            and callback.get("event") == "callback"
            and type(callback.get("index")) is int
            and callback["index"] >= 0
            and type(callback.get("raises")) is bool,
            "a complete callback result or exception was omitted",
        )
        validate_match(callback["match"])
    require(
        [event for event in value["events"] if event.get("event") == "callback"]
        == value["callbacks"],
        "a replacement callback was removed from its exact buffer-event ordering",
    )
    for warning in value["warnings"]:
        require(
            type(warning) is dict
            and set(warning) == {"category_module", "category", "message"}
            and all(type(warning.get(key)) is str for key in warning),
            "a genuine substitution warning was omitted",
        )
    return value


def verify_runtime(*, synthetic: bool = False) -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == PINNED_PYTHON
        and os.path.abspath(__file__) == SOURCE_ABSOLUTE,
        "use only the exact isolated pinned CPython substitution oracle",
    )
    if not synthetic:
        require(
            os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.realpath(__file__) == SOURCE_ABSOLUTE,
            "the frozen replacement oracle or Python executable is a symlink",
        )


def read_pinned_file(
    absolute: str,
    expected: str,
    *,
    maximum: int,
    label: str,
) -> dict[str, Any]:
    checked_digest(expected, label)
    require(
        type(absolute) is str
        and os.path.isabs(absolute)
        and os.path.abspath(absolute) == absolute
        and os.path.realpath(absolute) == absolute
        and type(maximum) is int
        and 0 < maximum <= MAX_BINARY_BYTES,
        "an exact genuine pinned owner is mandatory: " + label,
    )
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(absolute, flags)
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode) and 0 < before.st_size <= maximum,
            "a genuine standard source is not an owned bounded regular file: " + label,
        )
        hasher = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk), "a pinned reference source was truncated")
            hasher.update(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "a pinned reference source has a hidden suffix")
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_size)
            == (after.st_dev, after.st_ino, after.st_size)
            and hasher.hexdigest() == expected,
            "a frozen original regex source or policy changed: " + label,
        )
        return {
            "path": absolute,
            "sha256": expected,
            "bytes": before.st_size,
            "device": before.st_dev,
            "inode": before.st_ino,
        }
    finally:
        os.close(descriptor)


def verify_standard_modules(modules: Mapping[str, Any] | None = None) -> None:
    actual = sys.modules if modules is None else modules
    require(isinstance(actual, Mapping), "the actual reference module graph is mandatory")
    for name in actual:
        require(
            type(name) is str and name.partition(".")[0] not in FORBIDDEN_ENGINE_ROOTS,
            "a candidate, sibling, or external regex entered the standard-only reference",
        )


def authenticate_standard_reference(
    source_pin: str,
) -> tuple[Any, dict[str, dict[str, Any]]]:
    verify_runtime()
    owners = {
        "oracle": read_pinned_file(
            SOURCE_ABSOLUTE,
            source_pin,
            maximum=MAX_SOURCE_BYTES,
            label="frozen replacement-buffer oracle",
        ),
        "python": read_pinned_file(
            PINNED_PYTHON,
            PINNED_PYTHON_SHA256,
            maximum=MAX_BINARY_BYTES,
            label="pinned stable CPython executable",
        ),
        "v5_guard": read_pinned_file(
            ROOT + "/" + V5_GUARD_RELATIVE,
            V5_GUARD_SHA256,
            maximum=MAX_SOURCE_BYTES,
            label="frozen original CPython V5 policy",
        ),
        "ownership_audit": read_pinned_file(
            ROOT + "/" + OWNERSHIP_AUDIT_RELATIVE,
            OWNERSHIP_AUDIT_SHA256,
            maximum=MAX_SOURCE_BYTES,
            label="frozen no-delegation V3 ownership audit",
        ),
    }
    for historical_name, (relative, source_hash) in (
        HISTORICAL_V1_PINNED_FILES.items()
    ):
        owners["historical_" + historical_name] = read_pinned_file(
            ROOT + "/" + relative,
            source_hash,
            maximum=(
                MAX_BINARY_BYTES
                if relative.endswith(".json.gz")
                else MAX_SOURCE_BYTES
            ),
            label="preserved falsified substitution evidence: "
            + historical_name,
        )
    engine = importlib.import_module("re")
    for name, (filename, source_hash) in PINNED_STDLIB_SOURCES.items():
        absolute = PINNED_STDLIB_DIRECTORY + filename
        module = importlib.import_module(name)
        require(
            isinstance(module, types.ModuleType)
            and module.__name__ == name
            and getattr(module, "__file__", None) == absolute
            and os.path.realpath(absolute) == absolute,
            "a genuine standard CPython regex module was substituted: " + name,
        )
        owners[name] = read_pinned_file(
            absolute,
            source_hash,
            maximum=MAX_SOURCE_BYTES,
            label=name,
        )
    builtin = sys.modules.get("_sre")
    require(
        isinstance(builtin, types.ModuleType)
        and getattr(getattr(builtin, "__spec__", None), "origin", None) == "built-in"
        and engine.__name__ == "re"
        and getattr(engine.compile, "__module__", None) == "re",
        "the isolated genuine standard CPython regex engine was substituted",
    )
    verify_standard_modules()
    return engine, owners


def validate_source_owners(value: Any, source_pin: str) -> dict[str, dict[str, Any]]:
    expected: dict[str, tuple[str, str]] = {
        "oracle": (SOURCE_ABSOLUTE, source_pin),
        "python": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
        "v5_guard": (ROOT + "/" + V5_GUARD_RELATIVE, V5_GUARD_SHA256),
        "ownership_audit": (
            ROOT + "/" + OWNERSHIP_AUDIT_RELATIVE,
            OWNERSHIP_AUDIT_SHA256,
        ),
    }
    expected.update({
        name: (PINNED_STDLIB_DIRECTORY + filename, source_hash)
        for name, (filename, source_hash) in PINNED_STDLIB_SOURCES.items()
    })
    expected.update({
        "historical_" + name: (ROOT + "/" + relative, source_hash)
        for name, (relative, source_hash)
        in HISTORICAL_V1_PINNED_FILES.items()
    })
    require(
        type(value) is dict and set(value) == set(expected),
        "the complete stable CPython, regex, original-suite, and V3 ownership closure is mandatory",
    )
    for name, (path, source_hash) in expected.items():
        owner = value[name]
        require(
            type(owner) is dict
            and set(owner) == {"path", "sha256", "bytes", "device", "inode"}
            and owner.get("path") == path
            and owner.get("sha256") == source_hash
            and type(owner.get("bytes")) is int
            and owner["bytes"] > 0
            and type(owner.get("device")) is int
            and owner["device"] >= 0
            and type(owner.get("inode")) is int
            and owner["inode"] > 0,
            "a genuine pinned substitution reference owner was forged: " + name,
        )
    return value


def make_reference_guard(checks: int) -> dict[str, Any]:
    return {
        "candidate_import_count": 0,
        "external_regex_import_count": 0,
        "actual_method_guard_checks": checks,
        "required_method_guard_checks": 2 * CASE_COUNT,
        "future_candidate_guard_relative": V5_GUARD_RELATIVE,
        "future_candidate_guard_sha256": V5_GUARD_SHA256,
        "future_ownership_audit_relative": OWNERSHIP_AUDIT_RELATIVE,
        "future_ownership_audit_sha256": OWNERSHIP_AUDIT_SHA256,
        "future_candidate_guard_installed": False,
    }


def validate_reference_guard(value: Any) -> dict[str, Any]:
    expected = make_reference_guard(2 * CASE_COUNT)
    require(
        type(value) is dict and value == expected,
        "a complete no-delegation substitution reference guard was forged",
    )
    return value


def validate_records(
    matrix: list[dict[str, Any]],
    records: Any,
    records_pin: str,
) -> list[dict[str, Any]]:
    checked_digest(records_pin, "complete replacement-buffer observation vector")
    require(
        type(records) is list and len(records) == CASE_COUNT,
        "all 5,120 original replacement and nested-buffer outcomes are mandatory",
    )
    for case, row in zip(matrix, records, strict=True):
        require(
            type(row) is dict
            and set(row) == {"case", "cohort", "api", "outcome"}
            and row.get("case") == case["case"]
            and row.get("cohort") == case["cohort"]
            and row.get("api") == case["api"],
            "an ordered original substitution outcome was omitted or relabeled",
        )
        validate_outcome(row["outcome"])
    require(
        digest(records) == records_pin,
        "a complete original replacement observation vector was substituted",
    )
    return records


def observe_reference_worker(role: str, source_pin: str) -> dict[str, Any]:
    require(role in {"reference_a", "reference_b"}, "only genuine isolated references may run")
    checked_digest(source_pin, "prospectively frozen substitution oracle source")
    matrix = build_matrix()
    validate_matrix(matrix)
    engine, before = authenticate_standard_reference(source_pin)
    records: list[dict[str, Any]] = []
    checks = 0
    for case in matrix:
        verify_standard_modules()
        checks += 1
        try:
            outcome = execute_case(case, engine)
        finally:
            verify_standard_modules()
            checks += 1
        records.append({
            "case": case["case"],
            "cohort": case["cohort"],
            "api": case["api"],
            "outcome": outcome,
        })
    records_sha256 = digest(records)
    validate_records(matrix, records, records_sha256)
    after = authenticate_standard_reference(source_pin)[1]
    require(before == after, "a genuine reference owner changed during observation")
    document = {
        "schema": SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "pid": os.getpid(),
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "case_count": CASE_COUNT,
        "records_sha256": records_sha256,
        "records": records,
        "source_owners": before,
        "reference_guard": make_reference_guard(checks),
        "actual_reference_workers": 1,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    return validate_reference_worker(
        document,
        role=role,
        source_pin=source_pin,
        matrix=matrix,
        expected_pid=document["pid"],
    )


def validate_reference_worker(
    value: Any,
    *,
    role: str,
    source_pin: str,
    matrix: list[dict[str, Any]],
    expected_pid: int,
) -> dict[str, Any]:
    require(
        role in {"reference_a", "reference_b"}
        and type(expected_pid) is int
        and expected_pid > 0,
        "a genuine independent substitution-reference role and PID are mandatory",
    )
    expected = {
        "schema": SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "pid": expected_pid,
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "case_count": CASE_COUNT,
        "actual_reference_workers": 1,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    require(
        type(value) is dict
        and set(value) == set(expected) | {
            "records_sha256", "records", "source_owners", "reference_guard",
        },
        "a complete genuine substitution-reference worker was forged",
    )
    for field, original in expected.items():
        require(
            value.get(field) == original and type(value.get(field)) is type(original),
            "a genuine original substitution worker field changed: " + field,
        )
    validate_source_owners(value["source_owners"], source_pin)
    validate_reference_guard(value["reference_guard"])
    validate_records(matrix, value["records"], value["records_sha256"])
    return value


def encode_stream(value: Any) -> dict[str, Any]:
    require(
        type(value) is bytes and len(value) <= MAX_PROCESS_BYTES,
        "a complete bounded substitution-reference stream is mandatory",
    )
    return {
        "base64": base64.b64encode(value).decode("ascii"),
        "bytes": len(value),
        "sha256": hashlib.sha256(value).hexdigest(),
        "complete": True,
    }


def decode_stream(value: Any, label: str) -> bytes:
    require(
        type(value) is dict
        and set(value) == {"base64", "bytes", "sha256", "complete"}
        and type(value.get("base64")) is str
        and type(value.get("bytes")) is int
        and 0 <= value["bytes"] <= MAX_PROCESS_BYTES
        and valid_digest(value.get("sha256"))
        and value.get("complete") is True,
        "a complete reversible substitution-reference stream was hidden: " + label,
    )
    try:
        actual = base64.b64decode(value["base64"].encode("ascii"), validate=True)
    except (TypeError, ValueError, UnicodeError) as error:
        raise SubstitutionOracleError("an isolated reference stream is invalid: " + label) from error
    require(
        len(actual) == value["bytes"]
        and hashlib.sha256(actual).hexdigest() == value["sha256"]
        and base64.b64encode(actual).decode("ascii") == value["base64"],
        "a complete isolated reference stream was truncated or substituted",
    )
    return actual


def validate_process_evidence(
    value: Any,
    worker: Mapping[str, Any],
    *,
    role: str,
) -> dict[str, Any]:
    require(
        type(value) is dict
        and set(value) == {"role", "pid", "returncode", "stdout", "stderr"}
        and value.get("role") == role
        and type(value.get("pid")) is int
        and value["pid"] > 0
        and value["pid"] == worker.get("pid")
        and type(value.get("returncode")) is int
        and value["returncode"] == 0,
        "a genuine isolated original substitution-reference process was forged",
    )
    stdout = decode_stream(value["stdout"], role + " stdout")
    stderr = decode_stream(value["stderr"], role + " stderr")
    require(
        stdout == canonical(dict(worker)) and stderr == b"",
        "a reference process stream differs from its complete original worker",
    )
    return value


def run_isolated_reference(
    role: str,
    source_pin: str,
    matrix: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(role in {"reference_a", "reference_b"}, "only an exact isolated standard reference may run")
    arguments = [
        PINNED_PYTHON,
        "-I",
        "-B",
        SOURCE_ABSOLUTE,
        "--internal-reference-worker",
        "--role",
        role,
        "--oracle-source-sha256",
        source_pin,
        "--matrix-sha256",
        MATRIX_SHA256,
    ]
    try:
        process = subprocess.Popen(
            arguments,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            cwd=ROOT,
            env={
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
                "LC_ALL": "C",
                "PATH": "/usr/bin:/bin",
            },
        )
        stdout, stderr = process.communicate()
    except (OSError, subprocess.SubprocessError) as error:
        raise ReferenceWorkerFailure(
            "a genuine isolated pinned CPython substitution reference could not start",
            {"role": role, "error_type": type(error).__qualname__, "error": str(error)},
        ) from error
    evidence = {
        "role": role,
        "pid": process.pid,
        "returncode": process.returncode,
        "stdout": encode_stream(stdout),
        "stderr": encode_stream(stderr),
    }
    if process.returncode != 0 or stderr:
        raise ReferenceWorkerFailure(
            "a genuine isolated original substitution reference failed",
            evidence,
        )
    try:
        worker = validate_reference_worker(
            decode_canonical(stdout, role),
            role=role,
            source_pin=source_pin,
            matrix=matrix,
            expected_pid=process.pid,
        )
        validate_process_evidence(evidence, worker, role=role)
    except (SubstitutionOracleError, TypeError, ValueError, KeyError) as error:
        evidence["validation_error"] = {
            "type": type(error).__qualname__,
            "message": str(error),
        }
        raise ReferenceWorkerFailure(
            "complete original substitution-reference evidence was rejected",
            evidence,
        ) from error
    return worker, evidence


def validate_reference_pair(
    first: Mapping[str, Any],
    second: Mapping[str, Any],
    first_process: Mapping[str, Any],
    second_process: Mapping[str, Any],
    *,
    source_pin: str,
    matrix: list[dict[str, Any]],
) -> str:
    validate_reference_worker(
        first,
        role="reference_a",
        source_pin=source_pin,
        matrix=matrix,
        expected_pid=first.get("pid"),
    )
    validate_reference_worker(
        second,
        role="reference_b",
        source_pin=source_pin,
        matrix=matrix,
        expected_pid=second.get("pid"),
    )
    validate_process_evidence(first_process, first, role="reference_a")
    validate_process_evidence(second_process, second, role="reference_b")
    require(
        first["pid"] != second["pid"]
        and first["source_owners"] == second["source_owners"]
        and first["records_sha256"] == second["records_sha256"]
        and first["records"] == second["records"],
        "two genuinely independent standard substitution references disagree",
    )
    return first["records_sha256"]


def run_baseline(source_pin: str, matrix_pin: str) -> dict[str, Any]:
    verify_runtime()
    checked_digest(source_pin, "prospectively frozen substitution oracle source")
    checked_digest(matrix_pin, "prospectively frozen substitution case matrix")
    require(matrix_pin == MATRIX_SHA256, "the frozen replacement matrix was substituted")
    matrix = build_matrix()
    validate_matrix(matrix, matrix_pin)
    _, before = authenticate_standard_reference(source_pin)
    first, first_process = run_isolated_reference("reference_a", source_pin, matrix)
    second, second_process = run_isolated_reference("reference_b", source_pin, matrix)
    records_sha256 = validate_reference_pair(
        first,
        second,
        first_process,
        second_process,
        source_pin=source_pin,
        matrix=matrix,
    )
    after = authenticate_standard_reference(source_pin)[1]
    require(
        before == after == first["source_owners"],
        "an exact original reference owner changed around substitution observation",
    )
    return {
        "schema": SCHEMA + "-two-reference-baseline",
        "status": "PASS",
        "python": "3.14.6",
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "baseline_records_sha256": records_sha256,
        "source_owners": before,
        "reference_a": dict(first),
        "reference_b": dict(second),
        "reference_a_process": dict(first_process),
        "reference_b_process": dict(second_process),
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def decode_historical_signed_witness(
    encoded: str = HISTORICAL_V1_SIGNED_WITNESS_BASE64,
    *,
    compressed_sha256: str = (
        HISTORICAL_V1_SIGNED_WITNESS_COMPRESSED_SHA256
    ),
    uncompressed_sha256: str = HISTORICAL_V1_SIGNED_WITNESS_SHA256,
    maximum_compressed_bytes: int = (
        HISTORICAL_V1_SIGNED_WITNESS_COMPRESSED_BYTES
    ),
    maximum_uncompressed_bytes: int = (
        HISTORICAL_V1_SIGNED_WITNESS_MAXIMUM_BYTES
    ),
) -> dict[str, Any]:
    """Restore only complete signed historical outcomes without file access."""
    require(
        type(encoded) is str
        and len(encoded) == 160_288
        and type(maximum_compressed_bytes) is int
        and 0 < maximum_compressed_bytes <= MAX_BINARY_BYTES
        and type(maximum_uncompressed_bytes) is int
        and 0 < maximum_uncompressed_bytes
        <= HISTORICAL_V1_SIGNED_WITNESS_MAXIMUM_BYTES,
        "a bounded complete signed V1 witness was concealed",
    )
    checked_digest(compressed_sha256, "signed original compressed witness")
    checked_digest(
        uncompressed_sha256,
        "signed original complete uncompressed witness",
    )
    try:
        compressed = base64.b64decode(
            encoded.encode("ascii"),
            validate=True,
        )
    except (TypeError, ValueError, UnicodeError) as error:
        raise SubstitutionOracleError(
            "the complete signed original witness is not canonical base64",
        ) from error
    require(
        len(compressed) == HISTORICAL_V1_SIGNED_WITNESS_COMPRESSED_BYTES
        and len(compressed) <= maximum_compressed_bytes
        and hashlib.sha256(compressed).hexdigest() == compressed_sha256
        and base64.b64encode(compressed).decode("ascii") == encoded,
        "the bounded signed original witness was truncated or substituted",
    )
    try:
        decompressor = zlib.decompressobj()
        restored = decompressor.decompress(
            compressed,
            maximum_uncompressed_bytes + 1,
        )
        require(
            len(restored) <= maximum_uncompressed_bytes
            and not decompressor.unconsumed_tail
            and decompressor.eof
            and not decompressor.unused_data,
            "the signed original witness exceeded its decompression bound",
        )
        suffix = decompressor.flush()
    except (ValueError, zlib.error) as error:
        raise SubstitutionOracleError(
            "the complete bounded original witness is not valid zlib",
        ) from error
    require(
        suffix == b""
        and len(restored) == HISTORICAL_V1_SIGNED_WITNESS_BYTES
        and hashlib.sha256(restored).hexdigest() == uncompressed_sha256,
        "the complete original failure outcomes were hidden or altered",
    )
    return decode_canonical(
        restored,
        "complete signed historical V1 outcomes",
    )


def _canonicalize_historical_owned_callback(
    outcome: Mapping[str, Any],
    *,
    expected_original_module: str,
) -> dict[str, Any]:
    """Normalize one authenticated V1 own callback observation only."""
    require(
        expected_original_module
        in {"__main__", "tools.independent_substitution_buffer_semantics_v1"},
        "a historical callback topology was not independently frozen",
    )
    require(
        type(outcome) is dict
        and outcome.get("status") == "raise"
        and type(outcome.get("exception")) is dict
        and outcome["exception"].get("kind") == "ordinary-python-error"
        and outcome["exception"].get("type") == "ReplacementCallbackError"
        and outcome["exception"].get("module") == expected_original_module
        and outcome["exception"].get("message")
        == "frozen substitution callback failure",
        "only the signed exact old own-callback observation is correctable",
    )
    validate_outcome(outcome)
    restored = copy.deepcopy(dict(outcome))
    restored["exception"]["module"] = ORACLE_CALLBACK_CANONICAL_MODULE
    validate_outcome(restored)
    return restored


def validate_historical_signed_witness(
    value: Any,
    matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    """Authenticate all 656 preserved V1 full outcomes and true failures."""
    top_fields = {
        "schema", "v1_status", "matrix_sha256", "published_seed",
        "case_count", "baseline_records_sha256",
        "baseline_reference_pids", "families",
    }
    require(
        type(value) is dict
        and set(value) == top_fields
        and value["schema"]
        == "rebar-independent-substitution-buffer-semantics-v2-signed-v1-witnesses"
        and value["v1_status"] == HISTORICAL_V1_STATUS
        and value["matrix_sha256"] == MATRIX_SHA256
        and type(value["published_seed"]) is int
        and value["published_seed"] == PUBLISHED_SEED
        and value["case_count"] == CASE_COUNT
        and value["baseline_records_sha256"]
        == HISTORICAL_V1_BASELINE_RECORDS_SHA256
        and value["baseline_reference_pids"] == [82, 83]
        and type(value["families"]) is dict
        and set(value["families"]) == {"c", "zig"},
        "the complete original signed failure provenance was substituted",
    )
    expected_candidate_pins = {
        "c": (
            "39e318519c1b463c853103b14c099df56b974c595a6a5301bad91e386fabbf04",
            "dd3662164eddb3ac983f9618f0b53a2c52fbbe31f8cc456731109ef89cad9f13",
        ),
        "zig": (
            "027bb34006927e9f86134b7c6f29ebf81b331b077b1133f4d12af6267cfb4a1b",
            "a01c0e3a9bbe11be08502e2469f9052f31748520fc5cd513ea20795719d4a48a",
        ),
    }
    artifact_apis = {
        "module.sub": 32,
        "module.subn": 32,
        "pattern.sub": 32,
        "pattern.subn": 32,
    }
    result: dict[str, Any] = {}
    for family in ("c", "zig"):
        observed = value["families"][family]
        require(
            type(observed) is dict
            and set(observed) == {
                "historical_status",
                "historical_mismatch_count",
                "historical_candidate_records_sha256",
                "historical_mismatch_evidence_sha256",
                "artifact_count",
                "real_mismatch_count",
                "mismatches",
            }
            and observed["historical_status"] == "FAIL"
            and observed["historical_mismatch_count"]
            == HISTORICAL_V1_FAILURE_COUNTS[family]
            and observed["historical_candidate_records_sha256"]
            == expected_candidate_pins[family][0]
            and observed["historical_mismatch_evidence_sha256"]
            == expected_candidate_pins[family][1]
            and observed["artifact_count"]
            == HISTORICAL_V1_ORACLE_ARTIFACT_COUNTS[family]
            and observed["real_mismatch_count"]
            == HISTORICAL_V1_REAL_FAILURE_COUNTS[family]
            and type(observed["mismatches"]) is list
            and len(observed["mismatches"])
            == HISTORICAL_V1_FAILURE_COUNTS[family],
            "a complete original signed native failure was concealed: "
            + family,
        )
        previous_index = -1
        artifacts = 0
        real_failures = 0
        artifact_by_api = {api: 0 for api in artifact_apis}
        real_by_api = {api: 0 for api in artifact_apis}
        real_by_cohort: dict[str, int] = {}
        for witness in observed["mismatches"]:
            require(
                type(witness) is dict
                and set(witness) == {
                    "index", "case", "cohort", "api",
                    "baseline_outcome_sha256",
                    "candidate_outcome_sha256",
                    "expected", "actual",
                }
                and type(witness["index"]) is int
                and previous_index < witness["index"] < CASE_COUNT
                and witness["api"] in artifact_apis,
                "a signed complete mismatch was omitted or reordered",
            )
            previous_index = witness["index"]
            original_case = matrix[previous_index]
            require(
                witness["case"] == original_case["case"]
                and witness["cohort"] == original_case["cohort"]
                and witness["api"] == original_case["api"],
                "a complete signed mismatch escaped its frozen input case",
            )
            expected = validate_outcome(witness["expected"])
            actual = validate_outcome(witness["actual"])
            require(
                digest(expected) == witness["baseline_outcome_sha256"]
                and digest(actual)
                == witness["candidate_outcome_sha256"]
                and expected != actual,
                "a complete exact original mismatch was forged",
            )
            if witness["cohort"] in {
                "text-callback-error",
                "bytes-callback-error",
            }:
                require(
                    _canonicalize_historical_owned_callback(
                        expected,
                        expected_original_module="__main__",
                    )
                    == _canonicalize_historical_owned_callback(
                        actual,
                        expected_original_module=(
                            "tools.independent_substitution_buffer_semantics_v1"
                        ),
                    ),
                    "a real callback difference was falsely waived",
                )
                artifacts += 1
                artifact_by_api[witness["api"]] += 1
            else:
                require(
                    expected != actual,
                    "a genuine signed buffer or hash failure was waived",
                )
                real_failures += 1
                real_by_api[witness["api"]] += 1
                real_by_cohort[witness["cohort"]] = (
                    real_by_cohort.get(witness["cohort"], 0) + 1
                )
        require(
            artifacts == HISTORICAL_V1_ORACLE_ARTIFACT_COUNTS[family]
            and real_failures == HISTORICAL_V1_REAL_FAILURE_COUNTS[family]
            and artifacts + real_failures
            == HISTORICAL_V1_FAILURE_COUNTS[family]
            and artifact_by_api == artifact_apis,
            "a complete source-ordered original denominator changed",
        )
        expected_real_api_count = 84 if family == "c" else 16
        require(
            real_by_api == {
                api: expected_real_api_count for api in artifact_apis
            },
            "a real original substitution API loss was omitted",
        )
        required_real_cohorts = (
            {
                "nested-failing-template-after-subject": 48,
                "nested-mutating-subject-and-template": 48,
                "nested-mutating-unhashable-template": 48,
                "nested-stable-fixed-hash-template": 48,
                "nested-stable-subject-and-template": 48,
                "pep688-failing-hash-template": 32,
                "pep688-fixed-hash-template": 32,
                "pep688-unhashable-template": 32,
            }
            if family == "c"
            else {
                "nested-mutating-subject-and-template": 16,
                "nested-mutating-unhashable-template": 16,
                "nested-stable-fixed-hash-template": 16,
                "nested-stable-subject-and-template": 16,
            }
        )
        require(
            real_by_cohort == required_real_cohorts,
            "a genuine original nested-buffer or hash cohort was erased",
        )
        result[family] = {
            "historical_status": "FAIL",
            "historical_mismatch_count": artifacts + real_failures,
            "oracle_artifact_count": artifacts,
            "real_mismatch_count": real_failures,
            "artifact_by_api": artifact_by_api,
            "real_by_api": real_by_api,
            "real_by_cohort": real_by_cohort,
        }
    return result


class SourceOnlyBoundary:
    """Reject actual filesystem, engines, workers, clocks, and randomness."""

    def __init__(self) -> None:
        self.originals: list[tuple[Any, str, Any]] = []
        self.blocked = {
            "file_reads": 0,
            "file_writes": 0,
            "processes": 0,
            "candidate_imports": 0,
            "dynamic_imports": 0,
            "clock_samples": 0,
            "threads": 0,
            "garbage_collections": 0,
            "randomness": 0,
            "standard_matcher_calls": 0,
            "oracle_case_executions": 0,
        }

    def install(self, owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)
        self.originals.append((owner, name, original))

        def denied(*args: Any, **kwargs: Any) -> Any:
            selected = category
            if category == "file_reads":
                mode = args[1] if len(args) > 1 else kwargs.get("mode", "r")
                if type(mode) is str and any(flag in mode for flag in "wax+"):
                    selected = "file_writes"
                elif type(mode) is int and mode & (
                    os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
                ):
                    selected = "file_writes"
            elif category == "dynamic_imports" and args:
                module = args[0]
                if type(module) is str and (
                    module == "candidates"
                    or module.startswith("candidates.")
                    or module.partition(".")[0] in FORBIDDEN_ENGINE_ROOTS
                ):
                    selected = "candidate_imports"
            self.blocked[selected] += 1
            raise SourceOnlyError("synthetic substitution controls cannot perform " + selected)

        setattr(owner, name, denied)

    def __enter__(self) -> SourceOnlyBoundary:
        protections = (
            (builtins, "open", "file_reads"),
            (io, "open", "file_reads"),
            (os, "open", "file_reads"),
            (os, "stat", "file_reads"),
            (os, "lstat", "file_reads"),
            (os, "fstat", "file_reads"),
            (os, "scandir", "file_reads"),
            (os, "listdir", "file_reads"),
            (os, "readlink", "file_reads"),
            (os, "write", "file_writes"),
            (os, "replace", "file_writes"),
            (os, "rename", "file_writes"),
            (os, "remove", "file_writes"),
            (os, "unlink", "file_writes"),
            (os, "mkdir", "file_writes"),
            (os, "makedirs", "file_writes"),
            (os, "fsync", "file_writes"),
            (os, "link", "file_writes"),
            (subprocess, "Popen", "processes"),
            (subprocess, "run", "processes"),
            (subprocess, "call", "processes"),
            (subprocess, "check_call", "processes"),
            (subprocess, "check_output", "processes"),
            (os, "system", "processes"),
            (os, "fork", "processes"),
            (os, "posix_spawn", "processes"),
            (threading.Thread, "start", "threads"),
            (time, "time", "clock_samples"),
            (time, "time_ns", "clock_samples"),
            (time, "monotonic", "clock_samples"),
            (time, "monotonic_ns", "clock_samples"),
            (time, "perf_counter", "clock_samples"),
            (time, "perf_counter_ns", "clock_samples"),
            (time, "process_time", "clock_samples"),
            (gc, "collect", "garbage_collections"),
            (os, "urandom", "randomness"),
            (importlib, "import_module", "dynamic_imports"),
            (builtins, "__import__", "dynamic_imports"),
        )
        for owner, name, category in protections:
            self.install(owner, name, category)
        for standard_module_name in ("re", "re._compiler", "_sre"):
            standard_module = sys.modules.get(standard_module_name)
            if standard_module is not None:
                for matcher_name in (
                    "compile", "_compile", "match", "fullmatch",
                    "search", "findall", "finditer", "split", "sub",
                    "subn", "template",
                ):
                    self.install(
                        standard_module,
                        matcher_name,
                        "standard_matcher_calls",
                    )
        current_oracle = sys.modules.get(__name__)
        if current_oracle is not None:
            self.install(
                current_oracle,
                "execute_case",
                "oracle_case_executions",
            )
        return self

    def __exit__(self, error_type: Any, error: Any, trace: Any) -> bool:
        del error_type, error, trace
        for owner, name, original in reversed(self.originals):
            setattr(owner, name, original)
        self.originals.clear()
        return False


def synthetic_source_owners(source_pin: str) -> dict[str, dict[str, Any]]:
    values: dict[str, tuple[str, str]] = {
        "oracle": (SOURCE_ABSOLUTE, source_pin),
        "python": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
        "v5_guard": (ROOT + "/" + V5_GUARD_RELATIVE, V5_GUARD_SHA256),
        "ownership_audit": (
            ROOT + "/" + OWNERSHIP_AUDIT_RELATIVE,
            OWNERSHIP_AUDIT_SHA256,
        ),
    }
    values.update({
        name: (PINNED_STDLIB_DIRECTORY + filename, source_hash)
        for name, (filename, source_hash) in PINNED_STDLIB_SOURCES.items()
    })
    values.update({
        "historical_" + name: (ROOT + "/" + relative, source_hash)
        for name, (relative, source_hash)
        in HISTORICAL_V1_PINNED_FILES.items()
    })
    return {
        name: {
            "path": path,
            "sha256": pinned,
            "bytes": 4096 + index,
            "device": 7,
            "inode": 1000 + index,
        }
        for index, (name, (path, pinned)) in enumerate(values.items())
    }


def synthetic_event(
    event: str,
    role: str,
    *,
    flags: int | None,
    before: int,
    after: int,
    payload: bytes,
    behavior: str = "stable",
) -> dict[str, Any]:
    next_payload = (
        b"!" * len(payload)
        if event == "release" and behavior == "mutate"
        else payload
    )
    result: dict[str, Any] = {
        "event": event,
        "role": role,
        "flags": flags,
        "active_before": before,
        "active_after": after,
        "backing_before_hex": payload.hex(),
        "backing_after_hex": next_payload.hex(),
        "behavior": behavior,
    }
    if event == "hash":
        result["hash_result"] = 1729
    return result


def synthetic_outcome(case: Mapping[str, Any]) -> dict[str, Any]:
    events = [
        {"event": "phase", "name": "materialize-start"},
        {"event": "phase", "name": "materialize-complete"},
        {"event": "phase", "name": "operation-start"},
        {"event": "phase", "name": "operation-return"},
        {"event": "phase", "name": "cleanup-complete"},
    ]
    result = {
        "status": "return",
        "stage": case["api"],
        "value": normalize_value(None),
        "exception": None,
        "events": events,
        "callbacks": [],
        "warnings": [],
        "subject_after": normalize_value(None),
        "replacement_after": normalize_value(None),
        "subject_active_exports": 0,
        "replacement_active_exports": 0,
        "count_requested": case["count"],
        "pos_requested": case["pos"],
        "endpos_requested": case["endpos"],
    }
    return validate_outcome(result)


def synthetic_records(matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "case": case["case"],
            "cohort": case["cohort"],
            "api": case["api"],
            "outcome": synthetic_outcome(case),
        }
        for case in matrix
    ]


def synthetic_reference(
    role: str,
    pid: int,
    source_pin: str,
    matrix: list[dict[str, Any]],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "pid": pid,
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "case_count": CASE_COUNT,
        "records_sha256": digest(records),
        "records": records,
        "source_owners": synthetic_source_owners(source_pin),
        "reference_guard": make_reference_guard(2 * CASE_COUNT),
        "actual_reference_workers": 1,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def synthetic_process(worker: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "role": worker["role"],
        "pid": worker["pid"],
        "returncode": 0,
        "stdout": encode_stream(canonical(dict(worker))),
        "stderr": encode_stream(b""),
    }


def validate_future_candidate_pins(value: Any) -> dict[str, str]:
    require(
        type(value) is dict
        and set(value) == {
            "family", "adapter_relative", "adapter_sha256", "engine_relative",
            "engine_sha256", "bridge_relative", "bridge_sha256",
            "v5_guard_relative", "v5_guard_sha256", "ownership_audit_relative",
            "ownership_audit_sha256",
        }
        and value.get("family") in {"rust", "c", "zig"},
        "a future independently owned candidate manifest was forged",
    )
    family = value["family"]
    adapters = {
        "rust": "candidates/rust_candidate.py",
        "c": "candidates/vm_candidate.py",
        "zig": "candidates/zig_candidate.py",
    }
    engines = {
        "rust": "candidates/_rust_engine.so",
        "c": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "zig": "candidates/_zig_probe.so",
    }
    bridges = {
        "rust": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "c": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "zig": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
    }
    require(
        value["adapter_relative"] == adapters[family]
        and value["engine_relative"] == engines[family]
        and value["bridge_relative"] == bridges[family]
        and value["v5_guard_relative"] == V5_GUARD_RELATIVE
        and value["v5_guard_sha256"] == V5_GUARD_SHA256
        and value["ownership_audit_relative"] == OWNERSHIP_AUDIT_RELATIVE
        and value["ownership_audit_sha256"] == OWNERSHIP_AUDIT_SHA256,
        "a sibling, external matcher, or stale ownership policy was substituted",
    )
    for key in ("adapter_sha256", "engine_sha256", "bridge_sha256"):
        checked_digest(value[key], "future independently owned candidate " + key)
    require(
        (value["engine_relative"] == value["bridge_relative"]) is (family == "c")
        and (value["engine_sha256"] == value["bridge_sha256"]) is (family == "c"),
        "only the owned C engine and bridge can share a native implementation",
    )
    return value


def synthetic_candidate_pins(family: str) -> dict[str, str]:
    adapters = {
        "rust": "candidates/rust_candidate.py",
        "c": "candidates/vm_candidate.py",
        "zig": "candidates/zig_candidate.py",
    }
    engines = {
        "rust": "candidates/_rust_engine.so",
        "c": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "zig": "candidates/_zig_probe.so",
    }
    bridges = {
        "rust": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "c": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "zig": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
    }
    require(family in adapters, "a genuine future candidate family is mandatory")
    result = {
        "family": family,
        "adapter_relative": adapters[family],
        "adapter_sha256": "12" * 32,
        "engine_relative": engines[family],
        "engine_sha256": "34" * 32,
        "bridge_relative": bridges[family],
        "bridge_sha256": "34" * 32 if family == "c" else "56" * 32,
        "v5_guard_relative": V5_GUARD_RELATIVE,
        "v5_guard_sha256": V5_GUARD_SHA256,
        "ownership_audit_relative": OWNERSHIP_AUDIT_RELATIVE,
        "ownership_audit_sha256": OWNERSHIP_AUDIT_SHA256,
    }
    return validate_future_candidate_pins(result)


def source_self_test() -> dict[str, Any]:
    verify_runtime(synthetic=True)
    accepted: list[str] = []
    rejected: list[str] = []
    with SourceOnlyBoundary() as boundary:

        def accept(label: str, condition: Any) -> None:
            require(condition, "synthetic replacement positive control failed: " + label)
            accepted.append(label)

        def reject(label: str, action: Callable[[], Any]) -> None:
            try:
                action()
            except (SubstitutionOracleError, OSError, TypeError, ValueError, KeyError, IndexError):
                rejected.append(label)
                return
            raise SubstitutionOracleError("synthetic forged substitution evidence was accepted: " + label)

        matrix = build_matrix()
        validate_matrix(matrix)
        accept("freeze-all-5120-complete-substitution-buffer-cases", len(matrix) == 5120)
        accept("freeze-exact-64-balanced-cohorts", len(COHORTS) == 64)
        accept("freeze-exact-80-variants-per-cohort", all(
            sum(row["cohort"] == cohort for row in matrix) == VARIANTS_PER_COHORT
            for cohort in COHORTS
        ))
        accept("freeze-original-unsigned-64-bit-seed", 0 <= PUBLISHED_SEED < 1 << 64)
        accept("freeze-canonical-ordered-matrix-digest", digest(matrix) == MATRIX_SHA256)
        accept("include-all-module-and-compiled-substitution-apis", {
            "module.sub", "module.subn", "pattern.sub", "pattern.subn",
        }.issubset({row["api"] for row in matrix}))
        accept("include-genuine-match-expand-windows", any(
            row["api"] == "match.expand"
            and (row["pos"] != 0 or row["endpos"] is not None)
            for row in matrix
        ))
        accept("include-literal-and-all-original-replacement-escapes", {
            "literal", "escaped-named", "escaped-numeric", "missing-capture", "invalid-escape",
        }.issubset({row["replacement_style"] for row in matrix}))
        accept("include-returning-and-failing-user-callbacks", {
            "callable", "callable-error",
        }.issubset({row["replacement_style"] for row in matrix}))
        accept("include-text-bytes-bytearray", {
            "str", "bytes", "bytearray",
        }.issubset({row["subject"]["kind"] for row in matrix}))
        accept("include-contiguous-and-strided-subject-views", {
            "readonly-memoryview", "writable-memoryview",
            "readonly-strided-memoryview", "writable-strided-memoryview",
        }.issubset({row["subject"]["kind"] for row in matrix}))
        accept("include-readonly-writable-released-subject-views", {
            "released-readonly-memoryview", "released-writable-memoryview",
        }.issubset({row["subject"]["kind"] for row in matrix}))
        accept("include-contiguous-strided-released-replacement-views", {
            "readonly-memoryview", "writable-memoryview",
            "readonly-strided-memoryview", "writable-strided-memoryview",
            "released-readonly-memoryview", "released-writable-memoryview",
        }.issubset({row["replacement"]["kind"] for row in matrix}))
        accept("include-stable-mutating-failing-subject-exporters", {
            "pep688-stable", "pep688-mutating", "pep688-failing",
        }.issubset({row["subject"]["kind"] for row in matrix}))
        accept("include-stable-mutating-failing-replacement-exporters", {
            "pep688-stable", "pep688-mutating", "pep688-failing",
        }.issubset({row["replacement"]["kind"] for row in matrix}))
        accept("include-deterministic-fixed-and-unhashable-subjects", {
            "pep688-fixed-hash", "pep688-unhashable",
        }.issubset({row["subject"]["kind"] for row in matrix}))
        accept("include-fixed-unhashable-and-failing-replacement-hashes", {
            "pep688-fixed-hash", "pep688-unhashable", "pep688-failing-hash",
        }.issubset({row["replacement"]["kind"] for row in matrix}))
        accept("include-nested-owned-pep688-memoryview-wrappers", {
            "pep688-wrapped-readonly", "pep688-wrapped-writable",
        }.issubset({row["subject"]["kind"] for row in matrix}))
        accept("include-zero-width-lookahead-and-empty-patterns", {
            "text-zero-width-lookahead", "text-zero-width-empty",
            "bytes-zero-width-lookahead", "bytes-zero-width-empty",
        }.issubset(COHORTS))
        accept("include-exact-count-and-window-boundaries", {
            "text-count-limit", "text-window-pos-endpos",
            "bytes-count-limit", "bytes-window-pos-endpos",
        }.issubset(COHORTS))
        accept("preserve-lone-surrogate-and-unicode-normalization", {
            "text-lone-surrogate", "text-combining-mark", "text-precomposed-unicode",
        }.issubset(COHORTS))
        accept("freeze-owned-v3-no-delegation-policy", OWNERSHIP_AUDIT_SHA256 == (
            "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee"
        ))

        nested_events = [
            synthetic_event("acquire", "subject", flags=0, before=0, after=1, payload=b"alpha"),
            synthetic_event("acquire", "subject", flags=0, before=1, after=2, payload=b"alpha"),
            synthetic_event("acquire", "replacement", flags=284, before=0, after=1, payload=b"X"),
            synthetic_event("release", "replacement", flags=None, before=1, after=0, payload=b"X"),
            synthetic_event("release", "subject", flags=None, before=2, after=1, payload=b"alpha"),
            synthetic_event("release", "subject", flags=None, before=1, after=0, payload=b"alpha"),
        ]
        accept("preserve-exact-nested-buffer-flags-0-0-284", [
            item["flags"] for item in nested_events if item["event"] == "acquire"
        ] == [0, 0, 284])
        accept(
            "preserve-exact-nested-lifo-acquisition-release",
            validate_events(
                nested_events,
                require_balanced=True,
                expected_acquisition_flags=(
                    SIMPLE_BUFFER_FLAG,
                    SIMPLE_BUFFER_FLAG,
                    FULL_READONLY_BUFFER_FLAG,
                ),
            ) is nested_events,
        )
        hash_events = [synthetic_event(
            "hash", "replacement", flags=None, before=0, after=0, payload=b"X",
        )]
        accept("preserve-exact-deterministic-custom-hash-event", validate_events(hash_events) is hash_events)
        mutating_events = [
            synthetic_event("acquire", "subject", flags=0, before=0, after=1, payload=b"alpha", behavior="mutate"),
            synthetic_event("release", "subject", flags=None, before=1, after=0, payload=b"alpha", behavior="mutate"),
        ]
        accept("preserve-exact-equal-length-poison-on-release", validate_events(mutating_events) is mutating_events)
        synthetic_error_engine = types.SimpleNamespace(error=None)
        for title, error, message in (
            (
                "released-subject-memoryview-type-error",
                TypeError("expected string or bytes-like object, got 'memoryview'"),
                "expected string or bytes-like object, got 'memoryview'",
            ),
            (
                "released-replacement-memoryview-value-error",
                ValueError("operation forbidden on released memoryview object"),
                "operation forbidden on released memoryview object",
            ),
            (
                "writable-replacement-memoryview-hash-error",
                ValueError("cannot hash writable memoryview object"),
                "cannot hash writable memoryview object",
            ),
            (
                "pep688-replacement-buffer-failure",
                BufferError("frozen substitution replacement exporter failure"),
                "frozen substitution replacement exporter failure",
            ),
            (
                "deterministic-failing-replacement-hash",
                TypeError("frozen substitution replacement exporter hash failure"),
                "frozen substitution replacement exporter hash failure",
            ),
            (
                "deterministic-failing-user-callback",
                ReplacementCallbackError("frozen substitution callback failure"),
                "frozen substitution callback failure",
            ),
        ):
            observed_error = normalize_error(error, synthetic_error_engine)
            accept(
                "preserve-exact-" + title,
                observed_error["message"] == message
                and observed_error["type"] == type(error).__qualname__
                and validate_error(observed_error) is None,
            )

        accept(
            "preserve-falsified-original-v1-oracle-without-overwriting-it",
            HISTORICAL_V1_STATUS == "FALSIFIED"
            and HISTORICAL_V1_ORACLE_SHA256
            == "a325528aa62f107969b9dfdf5dea2ae8f9426607887a317fe20fcf9a1b7fd445"
            and HISTORICAL_V1_RECORDER_SHA256
            == "a7cf45ce72a178fead7eb0d0789fd1f0f37ed63789fe086070eefa613e959a33"
            and len(HISTORICAL_V1_PINNED_FILES) == 10
            and all(
                type(relative) is str
                and not relative.startswith("/")
                and ".." not in relative.split("/")
                and valid_digest(pinned)
                for relative, pinned in HISTORICAL_V1_PINNED_FILES.values()
            ),
        )
        accept(
            "preserve-every-original-signed-failure-denominator",
            dict(HISTORICAL_V1_FAILURE_COUNTS) == {"c": 464, "zig": 192}
            and dict(HISTORICAL_V1_ORACLE_ARTIFACT_COUNTS)
            == {"c": 128, "zig": 128}
            and dict(HISTORICAL_V1_REAL_FAILURE_COUNTS)
            == {"c": 336, "zig": 64}
            and all(
                HISTORICAL_V1_FAILURE_COUNTS[family]
                == HISTORICAL_V1_ORACLE_ARTIFACT_COUNTS[family]
                + HISTORICAL_V1_REAL_FAILURE_COUNTS[family]
                for family in ("c", "zig")
            ),
        )
        callback_cases = [
            case for case in matrix
            if case["cohort"] in {
                "text-callback-error",
                "bytes-callback-error",
            }
            and case["api"] != "match.expand"
        ]
        accept(
            "preserve-all-128-historical-script-versus-import-callback-cases",
            len(callback_cases) == 128
            and {case["api"] for case in callback_cases} == {
                "module.sub", "module.subn",
                "pattern.sub", "pattern.subn",
            },
        )
        historical_witness = decode_historical_signed_witness()
        historical_results = validate_historical_signed_witness(
            historical_witness,
            matrix,
        )
        accept(
            "authenticate-all-656-full-original-signed-failure-outcomes",
            sum(
                value["historical_mismatch_count"]
                for value in historical_results.values()
            ) == 656
            and all(
                value["historical_status"] == "FAIL"
                for value in historical_results.values()
            ),
        )
        accept(
            "preserve-all-336-genuine-c-native-buffer-failures",
            historical_results["c"]["real_mismatch_count"] == 336
            and historical_results["c"]["historical_mismatch_count"]
            == 464,
        )
        accept(
            "preserve-all-64-genuine-zig-native-buffer-failures",
            historical_results["zig"]["real_mismatch_count"] == 64
            and historical_results["zig"]["historical_mismatch_count"]
            == 192,
        )
        accept(
            "prove-exact-old-callback-module-only-differences",
            historical_results["c"]["oracle_artifact_count"] == 128
            and historical_results["zig"]["oracle_artifact_count"] == 128
            and historical_results["c"]["artifact_by_api"]
            == historical_results["zig"]["artifact_by_api"]
            == {
                "module.sub": 32,
                "module.subn": 32,
                "pattern.sub": 32,
                "pattern.subn": 32,
            },
        )
        callback_topology_checks = 0
        synthetic_callback_engine = types.SimpleNamespace(error=None)
        original_callback_module = ReplacementCallbackError.__module__
        try:
            for callback_case in callback_cases:
                ReplacementCallbackError.__module__ = "__main__"
                script_error = ReplacementCallbackError(
                    "frozen substitution callback failure",
                )
                script_observation = normalize_error(
                    script_error,
                    synthetic_callback_engine,
                )
                ReplacementCallbackError.__module__ = (
                    ORACLE_CALLBACK_CANONICAL_MODULE
                )
                imported_error = ReplacementCallbackError(
                    "frozen substitution callback failure",
                )
                imported_observation = normalize_error(
                    imported_error,
                    synthetic_callback_engine,
                )
                require(
                    type(script_error) is ReplacementCallbackError
                    and type(imported_error)
                    is ReplacementCallbackError
                    and script_observation == imported_observation
                    and script_observation["kind"]
                    == "ordinary-python-error"
                    and script_observation["type"]
                    == "ReplacementCallbackError"
                    and script_observation["module"]
                    == ORACLE_CALLBACK_CANONICAL_MODULE
                    and script_observation["message"]
                    == "frozen substitution callback failure"
                    and script_observation["args"]
                    == normalize_value(script_error.args),
                    "an exact synthetic script/import callback "
                    "identity disagrees: "
                    + callback_case["case"],
                )
                callback_topology_checks += 1
        finally:
            ReplacementCallbackError.__module__ = (
                original_callback_module
            )
        accept(
            "prove-all-128-source-only-script-import-callback-pairs",
            callback_topology_checks == 128
            and ReplacementCallbackError.__module__
            == original_callback_module,
        )

        foreign_engine = types.SimpleNamespace(error=None)
        foreign_same_name = type(
            "ReplacementCallbackError",
            (Exception,),
            {"__module__": "__main__"},
        )
        foreign_same_module = type(
            "ReplacementCallbackError",
            (Exception,),
            {"__module__": ORACLE_CALLBACK_CANONICAL_MODULE},
        )
        own_subclass = type(
            "DerivedReplacementCallbackError",
            (ReplacementCallbackError,),
            {"__module__": "__main__"},
        )
        for label, foreign, expected_module in (
            ("same-name-foreign-user", foreign_same_name, "__main__"),
            (
                "same-name-and-module-foreign-user",
                foreign_same_module,
                ORACLE_CALLBACK_CANONICAL_MODULE,
            ),
            ("own-callback-subclass", own_subclass, "__main__"),
            ("ordinary-user-type-error", TypeError, "builtins"),
            ("ordinary-user-buffer-error", BufferError, "builtins"),
        ):
            instance = foreign("frozen substitution callback failure")
            observed = normalize_error(instance, foreign_engine)
            accept(
                "preserve-exact-user-exception-identity-" + label,
                type(instance) is not ReplacementCallbackError
                and observed["kind"] == "ordinary-python-error"
                and observed["module"] == expected_module
                and observed["type"] == type(instance).__qualname__
                and observed["message"] == str(instance)
                and observed["args"] == normalize_value(instance.args),
            )
        own_callback = ReplacementCallbackError(
            "frozen substitution callback failure",
        )
        own_observation = normalize_error(
            own_callback,
            foreign_engine,
        )
        accept(
            "canonicalize-only-exact-owned-callback-class-identity",
            type(own_callback) is ReplacementCallbackError
            and own_observation["module"]
            == ORACLE_CALLBACK_CANONICAL_MODULE
            and own_observation["type"] == "ReplacementCallbackError"
            and own_observation["args"]
            == normalize_value(own_callback.args),
        )

        for item in (
            None,
            True,
            False,
            0,
            1,
            "\ud800",
            "e\u0301",
            "\u00e9",
            b"\x00\xff",
            bytearray(b"ab"),
            (),
            ("a", 1),
            [],
            ["a", b"b"],
            {"a": 1, "b": b"x"},
        ):
            observed = normalize_value(item)
            accept("preserve-type-tagged-original-value-" + str(len(accepted)), validate_normalized_value(observed) is None)

        source_pin = hashlib.sha256(b"synthetic-substitution-oracle-source-v1").hexdigest()
        owners = synthetic_source_owners(source_pin)
        accept("authenticate-complete-synthetic-standard-source-closure", validate_source_owners(owners, source_pin) is owners)
        records = synthetic_records(matrix)
        records_sha256 = digest(records)
        accept("retain-every-complete-synthetic-outcome", validate_records(matrix, records, records_sha256) is records)
        first = synthetic_reference("reference_a", 7001, source_pin, matrix, records)
        second = synthetic_reference("reference_b", 7002, source_pin, matrix, records)
        first_process = synthetic_process(first)
        second_process = synthetic_process(second)
        accept("authenticate-synthetic-reference-a", validate_reference_worker(
            first, role="reference_a", source_pin=source_pin, matrix=matrix, expected_pid=7001,
        ) is first)
        accept("authenticate-synthetic-reference-b", validate_reference_worker(
            second, role="reference_b", source_pin=source_pin, matrix=matrix, expected_pid=7002,
        ) is second)
        accept("preserve-two-genuinely-distinct-synthetic-reference-pids", first["pid"] != second["pid"])
        accept("preserve-complete-reversible-reference-stdout", decode_stream(
            first_process["stdout"], "reference_a",
        ) == canonical(first))
        accept("preserve-complete-empty-reference-stderr", decode_stream(
            first_process["stderr"], "reference_a",
        ) == b"")
        accept("require-two-identical-independent-reference-vectors", validate_reference_pair(
            first, second, first_process, second_process, source_pin=source_pin, matrix=matrix,
        ) == records_sha256)

        for family in ("rust", "c", "zig"):
            future = synthetic_candidate_pins(family)
            accept(
                "preserve-future-independent-" + family + "-owned-engine",
                validate_future_candidate_pins(future) is future,
            )
            for field in (
                "family", "adapter_relative", "adapter_sha256", "engine_relative",
                "engine_sha256", "bridge_relative", "bridge_sha256",
                "v5_guard_relative", "v5_guard_sha256", "ownership_audit_relative",
                "ownership_audit_sha256",
            ):
                forged = dict(future)
                if field == "family":
                    forged[field] = "foreign"
                elif field in {"adapter_sha256", "engine_sha256", "bridge_sha256"}:
                    forged[field] = "0" * 64
                elif field.endswith("sha256"):
                    forged[field] = hashlib.sha256(("foreign:" + field).encode("ascii")).hexdigest()
                else:
                    forged[field] = "candidates/foreign-regex.so"
                reject(
                    "reject-" + family + "-foreign-" + field,
                    lambda forged=forged: validate_future_candidate_pins(forged),
                )

        for title, kwargs in (
            (
                "signed-witness-wrong-compressed-digest",
                {"compressed_sha256": "a1" * 32},
            ),
            (
                "signed-witness-wrong-uncompressed-digest",
                {"uncompressed_sha256": "b2" * 32},
            ),
            (
                "signed-witness-truncated-compressed-cap",
                {
                    "maximum_compressed_bytes":
                    HISTORICAL_V1_SIGNED_WITNESS_COMPRESSED_BYTES - 1,
                },
            ),
            (
                "signed-witness-too-small-uncompressed-cap",
                {
                    "maximum_uncompressed_bytes":
                    HISTORICAL_V1_SIGNED_WITNESS_BYTES - 1,
                },
            ),
            (
                "signed-witness-zero-compressed-cap",
                {"maximum_compressed_bytes": 0},
            ),
            (
                "signed-witness-boolean-uncompressed-cap",
                {"maximum_uncompressed_bytes": True},
            ),
        ):
            reject(
                "reject-" + title,
                lambda kwargs=kwargs: decode_historical_signed_witness(
                    **kwargs,
                ),
            )
        reject(
            "reject-truncated-signed-witness-base64",
            lambda: decode_historical_signed_witness(
                HISTORICAL_V1_SIGNED_WITNESS_BASE64[:-4],
            ),
        )
        forged_encoding = (
            ("A" if HISTORICAL_V1_SIGNED_WITNESS_BASE64[0] != "A" else "B")
            + HISTORICAL_V1_SIGNED_WITNESS_BASE64[1:]
        )
        reject(
            "reject-tampered-signed-witness-compressed-content",
            lambda: decode_historical_signed_witness(
                forged_encoding,
            ),
        )
        for historical_family in ("c", "zig"):
            historical_document = historical_witness
            original_family = historical_document["families"][
                historical_family
            ]
            for forged_label, transform in (
                (
                    "omitted-complete-outcome",
                    lambda values: values[:-1],
                ),
                (
                    "reordered-complete-outcome",
                    lambda values: [values[1], values[0], *values[2:]],
                ),
                (
                    "duplicated-complete-outcome",
                    lambda values: [values[0], values[0], *values[2:]],
                ),
            ):
                forged_family = {
                    **original_family,
                    "mismatches": transform(
                        original_family["mismatches"],
                    ),
                }
                forged = {
                    **historical_document,
                    "families": {
                        **historical_document["families"],
                        historical_family: forged_family,
                    },
                }
                reject(
                    "reject-" + historical_family + "-"
                    + forged_label,
                    lambda forged=forged: (
                        validate_historical_signed_witness(
                            forged,
                            matrix,
                        )
                    ),
                )
            real_position = next(
                position
                for position, item in enumerate(
                    original_family["mismatches"],
                )
                if item["cohort"]
                not in {"text-callback-error", "bytes-callback-error"}
            )
            real_entry = original_family["mismatches"][real_position]
            erased_entry = {
                **real_entry,
                "actual": real_entry["expected"],
            }
            erased = list(original_family["mismatches"])
            erased[real_position] = erased_entry
            erased_family = {
                **original_family,
                "mismatches": erased,
            }
            reject(
                "reject-erasing-genuine-" + historical_family
                + "-buffer-failure",
                lambda erased_family=erased_family: (
                    validate_historical_signed_witness(
                        {
                            **historical_document,
                            "families": {
                                **historical_document["families"],
                                historical_family: erased_family,
                            },
                        },
                        matrix,
                    )
                ),
            )

        for field in (
            "case", "cohort", "variant", "seed", "api", "flags", "count",
            "pos", "endpos", "pattern", "subject", "replacement",
            "replacement_style", "callback_raises",
        ):
            forged = list(matrix)
            row = dict(forged[0])
            del row[field]
            forged[0] = row
            reject(
                "reject-missing-frozen-case-" + field,
                lambda forged=forged: validate_matrix(forged),
            )
        for title, transform in (
            ("missing-first", lambda values: values.pop(0)),
            ("missing-last", lambda values: values.pop()),
            ("duplicate-case", lambda values: values.__setitem__(1, values[0])),
            ("reordered-case", lambda values: values.__setitem__(slice(0, 2), [values[1], values[0]])),
            ("added-case", lambda values: values.append(values[0])),
        ):
            forged = list(matrix)
            transform(forged)
            reject(
                "reject-" + title + "-complete-matrix",
                lambda forged=forged: validate_matrix(forged),
            )

        for field in (
            "schema", "status", "python", "role", "pid", "oracle_source_sha256",
            "matrix_sha256", "published_seed", "cohort_count", "variants_per_cohort",
            "case_count", "records_sha256", "records", "source_owners",
            "reference_guard", "actual_reference_workers", "actual_candidate_workers",
            "actual_candidate_imports", "clock_samples", "timing_trials_run",
            "workspace_files_written", "evidence_files_created", "benchmark_files_read",
            "hidden_cases_read", "performance", "candidate_qualified_for_hidden_benchmark",
            "final_winner_selected",
        ):
            forged = dict(first)
            del forged[field]
            reject(
                "reject-missing-reference-worker-" + field,
                lambda forged=forged: validate_reference_worker(
                    forged,
                    role="reference_a",
                    source_pin=source_pin,
                    matrix=matrix,
                    expected_pid=7001,
                ),
            )
        for field in first["reference_guard"]:
            forged = dict(first["reference_guard"])
            if type(forged[field]) is bool:
                forged[field] = not forged[field]
            elif type(forged[field]) is int:
                forged[field] += 1
            else:
                forged[field] = "foreign"
            reject(
                "reject-forged-reference-guard-" + field,
                lambda forged=forged: validate_reference_guard(forged),
            )
        for field in ("base64", "bytes", "sha256", "complete"):
            forged = dict(first_process["stdout"])
            if field == "base64":
                forged[field] = "e30="
            elif field == "bytes":
                forged[field] += 1
            elif field == "sha256":
                forged[field] = hashlib.sha256(b"forged").hexdigest()
            else:
                forged[field] = False
            reject(
                "reject-incomplete-process-" + field,
                lambda forged=forged: decode_stream(forged, "forged"),
            )
        for title, forged in (
            ("duplicate-fields", b'{"role":"a","role":"b"}\n'),
            ("nonfinite", b'{"value":NaN}\n'),
            ("truncated", b'{"role":"a"'),
            ("extra-suffix", b'{}\n{}\n'),
            ("noncanonical", b'{ "role": "a" }\n'),
        ):
            reject(
                "reject-" + title + "-worker-json",
                lambda forged=forged: decode_canonical(forged, title),
            )
        poisoned = list(nested_events)
        poisoned[0] = {**poisoned[0], "flags": True}
        reject("reject-boolean-simple-acquisition-flag", lambda: validate_events(poisoned))
        reordered = list(nested_events)
        reordered[0], reordered[1] = reordered[1], reordered[0]
        reject("reject-reordered-nested-simple-acquisitions", lambda: validate_events(reordered))
        missing_release = list(nested_events)
        missing_release.pop(3)
        reject(
            "reject-omitted-nested-template-release",
            lambda: validate_events(
                missing_release,
                require_balanced=True,
                expected_acquisition_flags=(
                    SIMPLE_BUFFER_FLAG,
                    SIMPLE_BUFFER_FLAG,
                    FULL_READONLY_BUFFER_FLAG,
                ),
            ),
        )
        forged_full_flag = copy.deepcopy(nested_events)
        forged_full_flag[2]["flags"] = SIMPLE_BUFFER_FLAG
        reject(
            "reject-substituted-exact-284-full-readonly-buffer-flag",
            lambda: validate_events(
                forged_full_flag,
                require_balanced=True,
                expected_acquisition_flags=(
                    SIMPLE_BUFFER_FLAG,
                    SIMPLE_BUFFER_FLAG,
                    FULL_READONLY_BUFFER_FLAG,
                ),
            ),
        )
        wrong_release_order = copy.deepcopy(nested_events)
        wrong_release_order[3], wrong_release_order[4] = (
            wrong_release_order[4],
            wrong_release_order[3],
        )
        reject(
            "reject-reordered-nested-subject-and-replacement-releases",
            lambda: validate_events(
                wrong_release_order,
                require_balanced=True,
                expected_acquisition_flags=(
                    SIMPLE_BUFFER_FLAG,
                    SIMPLE_BUFFER_FLAG,
                    FULL_READONLY_BUFFER_FLAG,
                ),
            ),
        )
        broken_mutation = copy.deepcopy(mutating_events)
        broken_mutation[1]["backing_after_hex"] = b"?".hex()
        reject("reject-resized-poison-on-release", lambda: validate_events(broken_mutation))

        for title, action in (
            ("file-read", lambda: builtins.open("synthetic-reference")),
            ("descriptor-read", lambda: os.open("synthetic-reference", os.O_RDONLY)),
            ("file-write", lambda: os.write(1, b"synthetic")),
            ("candidate-import", lambda: importlib.import_module("candidates.rust_candidate")),
            ("external-regex-import", lambda: builtins.__import__("regex")),
            ("dynamic-standard-import", lambda: importlib.import_module("math")),
            (
                "preloaded-standard-regex-compile",
                lambda: sys.modules["re"].compile("synthetic"),
            ),
            (
                "preloaded-standard-regex-substitution",
                lambda: sys.modules["re"].sub(
                    "synthetic",
                    "synthetic",
                    "synthetic",
                ),
            ),
            (
                "preloaded-standard-sre-compiler",
                lambda: sys.modules["_sre"].compile(),
            ),
            (
                "actual-oracle-case-execution",
                lambda: execute_case(
                    {},
                    types.SimpleNamespace(error=None),
                ),
            ),
            ("reference-worker", lambda: subprocess.Popen(["synthetic"])),
            ("process-delegation", lambda: os.system("synthetic")),
            ("background-thread", lambda: threading.Thread().start()),
            ("wall-clock", lambda: time.time()),
            ("monotonic-clock", lambda: time.monotonic()),
            ("performance-clock", lambda: time.perf_counter()),
            ("system-randomness", lambda: os.urandom(8)),
            ("garbage-collection", lambda: gc.collect()),
        ):
            reject("block-real-" + title, action)
        accept(
            "exercise-every-real-source-only-side-effect-guard",
            all(count > 0 for count in boundary.blocked.values()),
        )
        accept(
            "load-zero-native-candidates-or-external-regex",
            not any(
                name == "candidates" or name.startswith("candidates.")
                or name.partition(".")[0] in FORBIDDEN_ENGINE_ROOTS
                for name in sys.modules
            ),
        )

    verify_runtime(synthetic=True)
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": CASE_COUNT,
        "cohort_count": len(COHORTS),
        "variants_per_cohort": VARIANTS_PER_COHORT,
        "published_seed_decimal": str(PUBLISHED_SEED),
        "historical_v1_status": HISTORICAL_V1_STATUS,
        "historical_v1_oracle_relative": HISTORICAL_V1_ORACLE_RELATIVE,
        "historical_v1_oracle_sha256": HISTORICAL_V1_ORACLE_SHA256,
        "historical_v1_recorder_relative": HISTORICAL_V1_RECORDER_RELATIVE,
        "historical_v1_recorder_sha256": HISTORICAL_V1_RECORDER_SHA256,
        "historical_v1_pinned_file_count": len(HISTORICAL_V1_PINNED_FILES),
        "historical_v1_failure_counts": dict(
            HISTORICAL_V1_FAILURE_COUNTS,
        ),
        "historical_v1_oracle_artifact_counts": dict(
            HISTORICAL_V1_ORACLE_ARTIFACT_COUNTS,
        ),
        "historical_v1_real_failure_counts": dict(
            HISTORICAL_V1_REAL_FAILURE_COUNTS,
        ),
        "synthetic_script_import_callback_topology_pairs": (
            callback_topology_checks
        ),
        "actual_in_memory_cpython_callback_topology_pairs": 0,
        "actual_stdlib_matcher_calls": 0,
        "actual_oracle_case_executions": 0,
        "historical_signed_witness_compressed_bytes": (
            HISTORICAL_V1_SIGNED_WITNESS_COMPRESSED_BYTES
        ),
        "historical_signed_witness_compressed_sha256": (
            HISTORICAL_V1_SIGNED_WITNESS_COMPRESSED_SHA256
        ),
        "historical_signed_witness_bytes": (
            HISTORICAL_V1_SIGNED_WITNESS_BYTES
        ),
        "historical_signed_witness_sha256": (
            HISTORICAL_V1_SIGNED_WITNESS_SHA256
        ),
        "historical_signed_witness_case_count": 656,
        "historical_signed_witness_results": historical_results,
        "future_candidate_guard_relative": V5_GUARD_RELATIVE,
        "future_candidate_guard_sha256": V5_GUARD_SHA256,
        "future_ownership_audit_relative": OWNERSHIP_AUDIT_RELATIVE,
        "future_ownership_audit_sha256": OWNERSHIP_AUDIT_SHA256,
        "positive_control_count": len(accepted),
        "positive_controls": accepted,
        "negative_control_count": len(rejected),
        "negative_controls": rejected,
        "source_only_blocked_operations": dict(boundary.blocked),
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "source_to_binary_reproducibility": "NOT ESTABLISHED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze independently owned replacement and PEP-688 semantics",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--baseline", action="store_true")
    modes.add_argument("--internal-reference-worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--role", choices=("reference_a", "reference_b"))
    parser.add_argument("--oracle-source-sha256")
    parser.add_argument("--matrix-sha256")
    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            verify_runtime(synthetic=True)
            require(
                options.role is None
                and options.oracle_source_sha256 is None
                and options.matrix_sha256 is None,
                "a source-only control cannot select, pin, or run an actual reference",
            )
            result = source_self_test()
        else:
            verify_runtime()
            checked_digest(options.oracle_source_sha256, "explicitly frozen substitution oracle")
            checked_digest(options.matrix_sha256, "explicitly frozen substitution matrix")
            require(options.matrix_sha256 == MATRIX_SHA256, "the frozen substitution matrix changed")
            if options.internal_reference_worker:
                require(options.role in {"reference_a", "reference_b"}, "an exact reference role is mandatory")
                result = observe_reference_worker(options.role, options.oracle_source_sha256)
            else:
                require(options.baseline and options.role is None, "only an explicitly authorized two-reference baseline may run")
                result = run_baseline(options.oracle_source_sha256, options.matrix_sha256)
        sys.stdout.buffer.write(canonical(result))
        return 0
    except ReferenceWorkerFailure as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-failure",
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error": str(error),
            "complete_reference_worker_failure": error.evidence,
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_files_written": 0,
            "evidence_files_created": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
        }))
        return 1
    except (SubstitutionOracleError, OSError, TypeError, ValueError) as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-failure",
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error": str(error),
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_files_written": 0,
            "evidence_files_created": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
        }))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
