const c = @cImport({
    @cInclude("regex.h");
});

pub export fn rebar_zig_posix_search(pattern: [*:0]const u8, subject: [*:0]const u8, ignore_case: c_int, start: *c_int, end: *c_int) c_int {
    var storage: [2048]u8 align(@alignOf(usize)) = undefined;
    const compiled: *c.regex_t = @ptrCast(&storage);
    const flags: c_int = c.REG_EXTENDED | (if (ignore_case != 0) c.REG_ICASE else 0);
    const compile_result = c.regcomp(compiled, pattern, flags);
    if (compile_result != 0) return -compile_result;
    defer c.regfree(compiled);
    var spans: [1]c.regmatch_t = undefined;
    const result = c.regexec(compiled, subject, spans.len, &spans, 0);
    if (result == c.REG_NOMATCH) return 0;
    if (result != 0) return -result;
    start.* = @intCast(spans[0].rm_so);
    end.* = @intCast(spans[0].rm_eo);
    return 1;
}
