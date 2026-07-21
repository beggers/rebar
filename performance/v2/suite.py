"""Expanded, balanced performance matrix for the rebar experiment."""

MODULES = ["re", "candidates.ast_candidate", "candidates.vm_candidate", "candidates.rust_candidate"]
TRIALS = 11
WARMUPS = 3
ORDER_SEED = 1979121303
BOOTSTRAP_SEED = 1979121304
BOOTSTRAPS = 3000
CASES_PER_COHORT = 28


def C(case_id, cohort, category, api, lifecycle, pattern, string, ops, **values):
    return {"id": case_id, "cohort": cohort, "category": category, "api": api, "lifecycle": lifecycle, "pattern": pattern, "string": string, "ops": ops, "weight": 1, "flags": values.pop("flags", []), **values}


CASES = [
    C("cal.search.literal.hit", "calibration", "search-hit", "search", "compiled", "needle", "prefix needle suffix", 320),
    C("cal.search.literal.miss", "calibration", "search-miss", "search", "compiled", "absent", "ordinary text without the token", 320),
    C("cal.search.long-boundary", "calibration", "search-boundary", "search", "compiled", "END$", "x" * 4096 + "END", 48),
    C("cal.search.class-anchor", "calibration", "search-class", "search", "compiled", r"^item-[0-9]{3}$", "skip\nitem-204\nitem-x", 224, flags=["M"]),
    C("cal.match.prefix", "calibration", "match", "match", "compiled", r"[A-Z]{2}[0-9]{4}", "AB2048 trailing", 256),
    C("cal.fullmatch.structured", "calibration", "fullmatch", "fullmatch", "compiled", r"[a-z]+(?:_[a-z]+)*", "alpha_beta_gamma", 224),
    C("cal.search.look-capture", "calibration", "capture-look", "search", "compiled", r"(?<=id=)(?P<id>[0-9]+)(?=;)", "name=a;id=48291;ok=yes", 192),
    C("cal.findall.tokens", "calibration", "findall", "findall", "compiled", r"[A-Za-z_][A-Za-z0-9_]*", "alpha=one beta_2=two gamma3=three delta=four", 144),
    C("cal.finditer.groups", "calibration", "finditer", "finditer", "compiled", r"(?P<key>[a-z]+)=(?P<value>[0-9]+)", "a=1 bb=22 ccc=333 dddd=4444", 120),
    C("cal.split.capture", "calibration", "split", "split", "compiled", r"([,:])", "a,b:c,d:e,f:g,h", 160),
    C("cal.sub.template", "calibration", "sub", "sub", "compiled", r"(?P<word>[a-z]+)-(?P<num>[0-9]+)", "ab-12 cd-3 ef-456", 144, repl=r"\g<num>:\g<word>"),
    C("cal.subn.callable", "calibration", "subn-callable", "subn", "compiled", r"[a-z]+", "alpha 12 beta 34 gamma", 128, repl={"callable": "upper_bracket"}, count=2),
    C("cal.bytes.tokens", "calibration", "bytes", "findall", "compiled", rb"[A-Za-z_][A-Za-z0-9_]*", b"alpha=1 beta_2=2 \xff gamma=3", 128),
    C("cal.unicode.words", "calibration", "unicode", "findall", "compiled", r"\b\w+\b", "Aé_٣ 雪 and İıſK", 128),
    C("cal.cold.compile-search", "calibration", "cold", "search", "cold", r"(?P<name>[A-Za-z]+)-[0-9]{2,4}", "prefix widget-2048 suffix", 40),
    C("cal.module.warm", "calibration", "module", "search", "module", r"[a-z]+-[0-9]+", "prefix alpha-2048 suffix", 256),
    C("cal.empty.finditer", "calibration", "empty", "finditer", "compiled", r"\B|(?=,)", "ab,cd ef", 96),
    C("cal.backref.fullmatch", "calibration", "backref", "fullmatch", "compiled", r"([a-z]{2,4})-\1", "echo-echo", 128),
    C("cal.conditional.match", "calibration", "conditional", "match", "compiled", r"(<)?[A-Za-z]+(?(1)>|!)", "<alpha> trailing", 128),
    C("cal.atomic.search", "calibration", "branch-control", "search", "compiled", r"(?>ab|a)b+", "xx abbbbb yy", 128),
    C("cal.byteslike.findall", "calibration", "bytes-like", "findall", "compiled", rb"[A-Z]+|[0-9]+", b"AA12 BB345 CC7", 112, subject_kind="bytearray"),
    C("cal.unicode-name.search", "calibration", "unicode-name", "search", "compiled", r"\N{SNOWMAN}+", "text ☃☃☃ end", 128),
    C("cal.ignorecase.findall", "calibration", "ignore-case", "findall", "compiled", r"[a-z]+", "Alpha BETA gamma Delta", 128, flags=["I"]),
    C("cal.many.split", "calibration", "many-results", "split", "compiled", r"[,;]", "a,b;c,d;e,f;g,h;i,j;k,l", 112),
    C("cal.escape.text", "calibration", "escape", "escape", "module", "a+b [x] # tag\\tail", None, 224),
    C("cal.compile.only", "calibration", "compile", "compile", "cold", r"(?P<word>[A-Za-z_]+)(?:-[0-9]{1,4})?", None, 32),
    C("cal.scanner.search", "calibration", "scanner", "scanner", "compiled", r"(?P<word>[a-z]+)=[0-9]+", "a=1 bb=22 ccc=333 dddd=4444", 96),
    C("cal.match.surface", "calibration", "match-surface", "match-surface", "compiled", r"(?P<word>[A-Za-z]+)-(?P<num>[0-9]+)", "prefix alpha-2048 suffix", 144, expand=r"\g<num>:\g<word>"),

    C("hold.search.literal.hit", "holdout", "search-hit", "search", "compiled", "marker", "before marker after", 320),
    C("hold.search.literal.miss", "holdout", "search-miss", "search", "compiled", "missing", "all the usual words are present", 320),
    C("hold.search.long-boundary", "holdout", "search-boundary", "search", "compiled", "DONE$", "q" * 6144 + "DONE", 40),
    C("hold.search.class-anchor", "holdout", "search-class", "search", "compiled", r"^row_[A-F0-9]{4}$", "ignore\nrow_B17F\nrow_zzzz", 224, flags=["M"]),
    C("hold.match.prefix", "holdout", "match", "match", "compiled", r"[a-z]{3}[0-9]{2}", "abc42 remains", 256),
    C("hold.fullmatch.structured", "holdout", "fullmatch", "fullmatch", "compiled", r"(?:[A-Z][a-z]+)(?:-[A-Z][a-z]+)*", "North-East-West", 224),
    C("hold.search.look-capture", "holdout", "capture-look", "search", "compiled", r"(?<=code:)(?P<code>[A-Z]{2}[0-9]+)(?=,)", "x,code:ZX9021,next", 192),
    C("hold.findall.tokens", "holdout", "findall", "findall", "compiled", r"[a-z]+(?:_[0-9]+)?", "red_1 blue green_22 yellow black_333", 144),
    C("hold.finditer.groups", "holdout", "finditer", "finditer", "compiled", r"(?P<word>[a-z]+):(?P<num>[0-9]+)", "one:1 two:22 three:333 four:4444", 120),
    C("hold.split.capture", "holdout", "split", "split", "compiled", r"([;|])", "a;b|c;d|e;f|g;h", 160),
    C("hold.sub.template", "holdout", "sub", "sub", "compiled", r"(?P<left>[A-Z]+)_(?P<right>[0-9]+)", "AA_1 BB_22 CCC_333", 144, repl=r"\g<right>-\g<left>"),
    C("hold.subn.callable", "holdout", "subn-callable", "subn", "compiled", r"[A-Z]+", "ONE 1 TWO 2 THREE", 128, repl={"callable": "lower_bracket"}, count=2),
    C("hold.bytes.tokens", "holdout", "bytes", "findall", "compiled", rb"[0-9]+|[A-Za-z]+", b"ab12 cd345 \x80 EF7", 128),
    C("hold.unicode.words", "holdout", "unicode", "findall", "compiled", r"\d+|\w+", "café ٣٣ 雪_2 İı", 128),
    C("hold.cold.compile-search", "holdout", "cold", "search", "cold", r"(?P<tag>[A-Z]+)_[0-9]{1,3}", "prefix TAG_127 suffix", 40),
    C("hold.module.warm", "holdout", "module", "search", "module", r"[A-Z]+_[0-9]+", "prefix ITEM_730 suffix", 256),
    C("hold.empty.finditer", "holdout", "empty", "finditer", "compiled", r"(?=\s)|\B", "xy zt uv", 96),
    C("hold.backref.fullmatch", "holdout", "backref", "fullmatch", "compiled", r"([A-Z]{2,5}):\1", "ECHO:ECHO", 128),
    C("hold.conditional.match", "holdout", "conditional", "match", "compiled", r"(\[)?[0-9]+(?(1)\]|;)", "[2048] rest", 128),
    C("hold.atomic.search", "holdout", "branch-control", "search", "compiled", r"a*+b|cd+", "xx cdddd yy", 128),
    C("hold.byteslike.findall", "holdout", "bytes-like", "findall", "compiled", rb"[a-z]+|[0-9]+", b"ab12 cd345 ef7", 112, subject_kind="memoryview"),
    C("hold.unicode-name.search", "holdout", "unicode-name", "search", "compiled", r"\N{BLACK STAR}{2,4}", "begin ★★★ end", 128),
    C("hold.ignorecase.findall", "holdout", "ignore-case", "findall", "compiled", r"[a-z]+", "ONE Two THREE four", 128, flags=["I"]),
    C("hold.many.split", "holdout", "many-results", "split", "compiled", r"[|:]", "a|b:c|d:e|f:g|h:i|j:k|l", 112),
    C("hold.escape.bytes", "holdout", "escape", "escape", "module", b"A+B [x] # tag\\tail", None, 224),
    C("hold.compile.only", "holdout", "compile", "compile", "cold", r"(?P<tag>[A-Z]{2,8})(?:_[0-9]{1,3})+", None, 32),
    C("hold.scanner.search", "holdout", "scanner", "scanner", "compiled", r"(?P<word>[A-Z]+):[0-9]+", "A:1 BB:22 CCC:333 DDDD:4444", 96),
    C("hold.match.surface", "holdout", "match-surface", "match-surface", "compiled", r"(?P<left>[A-Z]+)_(?P<right>[0-9]+)", "prefix ITEM_730 suffix", 144, expand=r"\g<right>-\g<left>"),
]


def cases():
    return list(CASES)
