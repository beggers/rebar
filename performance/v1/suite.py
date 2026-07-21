"""Frozen balanced performance matrix for the rebar experiment."""

MODULES = ["re", "candidates.ast_candidate", "candidates.vm_candidate", "candidates.rust_candidate"]
TRIALS = 9
WARMUPS = 2
ORDER_SEED = 1979120921
BOOTSTRAP_SEED = 1979120922
BOOTSTRAPS = 2000


def C(case_id, cohort, category, api, lifecycle, pattern, string, ops, **values):
    return {"id": case_id, "cohort": cohort, "category": category, "api": api, "lifecycle": lifecycle, "pattern": pattern, "string": string, "ops": ops, "weight": 1, "flags": values.pop("flags", []), **values}


CASES = [
    C("cal.search.literal.hit", "calibration", "search-hit", "search", "compiled", "needle", "prefix needle suffix", 256),
    C("cal.search.literal.miss", "calibration", "search-miss", "search", "compiled", "absent", "ordinary text without the token", 256),
    C("cal.search.long-boundary", "calibration", "search-boundary", "search", "compiled", "END$", "x" * 4096 + "END", 48),
    C("cal.search.class-anchor", "calibration", "search-class", "search", "compiled", r"^item-[0-9]{3}$", "skip\nitem-204\nitem-x", 192, flags=["M"]),
    C("cal.match.prefix", "calibration", "match", "match", "compiled", r"[A-Z]{2}[0-9]{4}", "AB2048 trailing", 224),
    C("cal.fullmatch.structured", "calibration", "fullmatch", "fullmatch", "compiled", r"[a-z]+(?:_[a-z]+)*", "alpha_beta_gamma", 224),
    C("cal.search.look-capture", "calibration", "capture-look", "search", "compiled", r"(?<=id=)(?P<id>[0-9]+)(?=;)", "name=a;id=48291;ok=yes", 160),
    C("cal.findall.tokens", "calibration", "findall", "findall", "compiled", r"[A-Za-z_][A-Za-z0-9_]*", "alpha=one beta_2=two gamma3=three delta=four", 120),
    C("cal.finditer.groups", "calibration", "finditer", "finditer", "compiled", r"(?P<key>[a-z]+)=(?P<value>[0-9]+)", "a=1 bb=22 ccc=333 dddd=4444", 100),
    C("cal.split.capture", "calibration", "split", "split", "compiled", r"([,:])", "a,b:c,d:e,f:g,h", 144),
    C("cal.sub.template", "calibration", "sub", "sub", "compiled", r"(?P<word>[a-z]+)-(?P<num>[0-9]+)", "ab-12 cd-3 ef-456", 128, repl=r"\g<num>:\g<word>"),
    C("cal.subn.callable", "calibration", "subn-callable", "subn", "compiled", r"[a-z]+", "alpha 12 beta 34 gamma", 112, repl={"callable": "upper_bracket"}, count=2),
    C("cal.bytes.tokens", "calibration", "bytes", "findall", "compiled", rb"[A-Za-z_][A-Za-z0-9_]*", b"alpha=1 beta_2=2 \xff gamma=3", 112),
    C("cal.unicode.words", "calibration", "unicode", "findall", "compiled", r"\b\w+\b", "Aé_٣ 雪 and İıſK", 112),
    C("cal.cold.compile-search", "calibration", "cold", "search", "cold", r"(?P<name>[A-Za-z]+)-[0-9]{2,4}", "prefix widget-2048 suffix", 36),
    C("cal.module.warm", "calibration", "module", "search", "module", r"[a-z]+-[0-9]+", "prefix alpha-2048 suffix", 224),
    C("hold.search.literal.hit", "holdout", "search-hit", "search", "compiled", "marker", "before marker after", 256),
    C("hold.search.literal.miss", "holdout", "search-miss", "search", "compiled", "missing", "all the usual words are present", 256),
    C("hold.search.long-boundary", "holdout", "search-boundary", "search", "compiled", "DONE$", "q" * 6144 + "DONE", 32),
    C("hold.search.class-anchor", "holdout", "search-class", "search", "compiled", r"^row_[A-F0-9]{4}$", "ignore\nrow_B17F\nrow_zzzz", 192, flags=["M"]),
    C("hold.match.prefix", "holdout", "match", "match", "compiled", r"[a-z]{3}[0-9]{2}", "abc42 remains", 224),
    C("hold.fullmatch.structured", "holdout", "fullmatch", "fullmatch", "compiled", r"(?:[A-Z][a-z]+)(?:-[A-Z][a-z]+)*", "North-East-West", 224),
    C("hold.search.look-capture", "holdout", "capture-look", "search", "compiled", r"(?<=code:)(?P<code>[A-Z]{2}[0-9]+)(?=,)", "x,code:ZX9021,next", 160),
    C("hold.findall.tokens", "holdout", "findall", "findall", "compiled", r"[a-z]+(?:_[0-9]+)?", "red_1 blue green_22 yellow black_333", 120),
    C("hold.finditer.groups", "holdout", "finditer", "finditer", "compiled", r"(?P<word>[a-z]+):(?P<num>[0-9]+)", "one:1 two:22 three:333 four:4444", 100),
    C("hold.split.capture", "holdout", "split", "split", "compiled", r"([;|])", "a;b|c;d|e;f|g;h", 144),
    C("hold.sub.template", "holdout", "sub", "sub", "compiled", r"(?P<left>[A-Z]+)_(?P<right>[0-9]+)", "AA_1 BB_22 CCC_333", 128, repl=r"\g<right>-\g<left>"),
    C("hold.subn.callable", "holdout", "subn-callable", "subn", "compiled", r"[A-Z]+", "ONE 1 TWO 2 THREE", 112, repl={"callable": "lower_bracket"}, count=2),
    C("hold.bytes.tokens", "holdout", "bytes", "findall", "compiled", rb"[0-9]+|[A-Za-z]+", b"ab12 cd345 \x80 EF7", 112),
    C("hold.unicode.words", "holdout", "unicode", "findall", "compiled", r"\d+|\w+", "café ٣٣ 雪_2 İı", 112),
    C("hold.cold.compile-search", "holdout", "cold", "search", "cold", r"(?P<tag>[A-Z]+)_[0-9]{1,3}", "prefix TAG_127 suffix", 36),
    C("hold.module.warm", "holdout", "module", "search", "module", r"[A-Z]+_[0-9]+", "prefix ITEM_730 suffix", 224),
]


def cases():
    return list(CASES)
