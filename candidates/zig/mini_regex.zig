const std = @import("std");

const max_positions = 512;
const max_stack = 32;
const max_undo = 64;
const max_guards = 32;
const inline_capture_words = 64;
const inline_capture_layouts = 32;
const unbounded = std.math.maxInt(usize);
const text_pattern_flag: u32 = 0x80000000;
const GroupId = u32;
const RecursionEnter = *const fn (?*anyopaque) callconv(.c) c_int;
const RecursionLeave = *const fn (?*anyopaque) callconv(.c) void;

extern fn _PyUnicode_IsAlpha(u32) c_int;
extern fn _PyUnicode_IsDecimalDigit(u32) c_int;
extern fn _PyUnicode_IsDigit(u32) c_int;
extern fn _PyUnicode_IsNumeric(u32) c_int;
extern fn _PyUnicode_IsWhitespace(u32) c_int;
extern fn _PyUnicode_ToLowercase(u32) u32;
extern fn _PyUnicode_ToUppercase(u32) u32;
extern "c" fn tolower(c_int) c_int;
extern "c" fn isalnum(c_int) c_int;

const Pair = struct { left: u32, right: u32 };
const Repeat = struct { child: u32, minimum: usize, maximum: usize, lazy: bool, possessive: bool };
const Group = struct { child: u32, number: GroupId };
const Conditional = struct { number: GroupId, yes: u32, no: u32 };
const Look = struct { child: u32, behind: bool, positive: bool, width: u32 };
const Scoped = struct { child: u32, flags: u32 };
const Name = struct { bytes: []const u8, group: GroupId };
const Node = union(enum) {
    empty,
    literal: u32,
    dot,
    class: u32,
    begin,
    end,
    absolute_begin,
    absolute_end,
    boundary: bool,
    sequence: Pair,
    alternative: Pair,
    repeat: Repeat,
    group: Group,
    backref: GroupId,
    conditional: Conditional,
    atomic: u32,
    look: Look,
    scoped: Scoped,
};
const ClassRange = struct { left: u32, right: u32 };
const CharClass = struct {
    bits: [32]u8 = [_]u8{0} ** 32,
    match_bits: [32]u8 = [_]u8{0} ** 32,
    match_flags: u32 = std.math.maxInt(u32),
    range_start: u32 = 0,
    range_count: u32 = 0,
    categories: u8 = 0,
    negative: bool = false,
    locale_multi: bool = false,
};
const Op = enum(u8) { literal, dot, class, begin, end, absolute_begin, absolute_end, boundary, boundary_peek, split, start_split, jump, save_begin, save_end, backref, conditional, atomic_begin, atomic_end, look, peek, peek_text, peek_run, peek_even, run, lazy_dot, accept };
const Instruction = struct { op: Op, left: u32 = 0, right: u32 = 0, extra: u32 = 0, value: u32 = 0 };
const CaptureLayout = struct { number: GroupId, begin: usize, end: usize };
const Run = struct { atom: u32, flags: u32, width: usize, minimum: usize, maximum: usize, lazy: bool, possessive: bool, layout_start: u32, layout_count: u32 };
const Program = struct {
    arena: std.heap.ArenaAllocator,
    nodes: std.ArrayList(Node) = .empty,
    classes: std.ArrayList(CharClass) = .empty,
    ranges: std.ArrayList(ClassRange) = .empty,
    code: std.ArrayList(Instruction) = .empty,
    runs: std.ArrayList(Run) = .empty,
    layouts: std.ArrayList(CaptureLayout) = .empty,
    names: std.ArrayList(Name) = .empty,
    root: u32 = 0,
    flags: u32 = 0,
    starts: [256]u8 = [_]u8{0} ** 256,
    single: [256]u8 = [_]u8{0} ** 256,
    seconds: [32]u8 = [_]u8{0} ** 32,
    nullable: bool = false,
    single_start: u16 = 256,
    scoped_prefix: u32 = std.math.maxInt(u32),
    prefix_run: u32 = std.math.maxInt(u32),
    groups: GroupId = 0,
    references: bool = false,
    nullable_loops: bool = false,
};

const ParseError = std.mem.Allocator.Error || error{ TooManyNodes, TooManyClasses, TooManyGroups, InvalidPattern, Unsupported, RecursionLimit };
const Parser = struct {
    source: []const u8,
    at: usize = 0,
    program: *Program,
    recursion_enter: ?RecursionEnter = null,
    recursion_leave: ?RecursionLeave = null,
    recursion_context: ?*anyopaque = null,
    open_groups: std.ArrayList(bool) = .empty,
    lookbehind_bases: std.ArrayList(GroupId) = .empty,

    fn add(self: *Parser, node: Node) ParseError!u32 {
        if (self.program.nodes.items.len >= std.math.maxInt(u32)) return error.TooManyNodes;
        const index: u32 = @intCast(self.program.nodes.items.len);
        try self.program.nodes.append(self.program.arena.allocator(), node);
        return index;
    }

    fn setBit(class: *CharClass, value: u8) void {
        class.bits[value >> 3] |= @as(u8, 1) << @intCast(value & 7);
    }

    fn skip(self: *Parser) ParseError!void {
        while (self.at < self.source.len) {
            if (self.at + 2 < self.source.len and self.source[self.at] == '(' and self.source[self.at + 1] == '?' and self.source[self.at + 2] == '#') {
                self.at += 3;
                var closed = false;
                while (self.at < self.source.len) {
                    switch (self.source[self.at]) {
                        '\\' => {
                            self.at += 1;
                            if (self.at >= self.source.len) return error.InvalidPattern;
                            _ = try self.codepoint();
                        },
                        ')' => {
                            self.at += 1;
                            closed = true;
                            break;
                        },
                        else => self.at += 1,
                    }
                }
                if (!closed) return error.InvalidPattern;
                continue;
            }
            if (self.program.flags & 64 == 0) return;
            const value = self.source[self.at];
            if (value == ' ' or value == '\t' or value == '\n' or value == '\r' or value == 11 or value == 12) {
                self.at += 1;
                continue;
            }
            if (value == '#') {
                self.at += 1;
                while (self.at < self.source.len) {
                    switch (self.source[self.at]) {
                        '\\' => {
                            self.at += 1;
                            if (self.at >= self.source.len) return error.InvalidPattern;
                            _ = try self.codepoint();
                        },
                        '\n' => {
                            self.at += 1;
                            break;
                        },
                        else => self.at += 1,
                    }
                }
                continue;
            }
            break;
        }
    }

    fn codepoint(self: *Parser) ParseError!u32 {
        if (self.at >= self.source.len) return error.InvalidPattern;
        const first = self.source[self.at];
        self.at += 1;
        if (first < 0x80 or self.program.flags & text_pattern_flag == 0) return first;
        const width: usize = if (first & 0xe0 == 0xc0) 2 else if (first & 0xf0 == 0xe0) 3 else if (first & 0xf8 == 0xf0) 4 else return error.InvalidPattern;
        if (self.at + width - 1 > self.source.len) return error.InvalidPattern;
        var value: u32 = first & (@as(u8, 0x7f) >> @intCast(width));
        for (0..width - 1) |_| {
            const next = self.source[self.at];
            if (next & 0xc0 != 0x80) return error.InvalidPattern;
            self.at += 1;
            value = value << 6 | (next & 0x3f);
        }
        return value;
    }

    fn escaped(self: *Parser, code: u8, in_class: bool) ParseError!u32 {
        return switch (code) {
            'a' => 7,
            'b' => if (in_class) 8 else 'b',
            'f' => 12,
            'n' => '\n',
            'r' => '\r',
            't' => '\t',
            'v' => 11,
            'x' => blk: {
                if (self.at + 1 >= self.source.len) return error.InvalidPattern;
                const left = std.fmt.charToDigit(self.source[self.at], 16) catch return error.InvalidPattern;
                const right = std.fmt.charToDigit(self.source[self.at + 1], 16) catch return error.InvalidPattern;
                self.at += 2;
                break :blk @intCast(left * 16 + right);
            },
            'u', 'U' => blk: {
                if (self.program.flags & text_pattern_flag == 0) return error.InvalidPattern;
                const width: usize = if (code == 'u') 4 else 8;
                if (self.at + width > self.source.len) return error.InvalidPattern;
                var value: u32 = 0;
                for (0..width) |_| {
                    const digit = std.fmt.charToDigit(self.source[self.at], 16) catch return error.InvalidPattern;
                    self.at += 1;
                    value = value << 4 | @as(u32, @intCast(digit));
                }
                if (value > 0x10ffff) return error.InvalidPattern;
                break :blk value;
            },
            '0'...'7' => blk: {
                var value: usize = code - '0';
                var consumed: usize = 1;
                while (consumed < 3 and self.at < self.source.len and self.source[self.at] >= '0' and self.source[self.at] <= '7') : (consumed += 1) {
                    value = value * 8 + self.source[self.at] - '0';
                    self.at += 1;
                }
                if (value > 255) return error.InvalidPattern;
                break :blk @intCast(value);
            },
            else => if (std.ascii.isAlphabetic(code)) error.InvalidPattern else code,
        };
    }

    fn category(self: *Parser, code: u8) ParseError!u32 {
        if (self.program.classes.items.len >= std.math.maxInt(u32)) return error.TooManyClasses;
        const index: u32 = @intCast(self.program.classes.items.len);
        var class = CharClass{};
        class.range_start = @intCast(self.program.ranges.items.len);
        class.categories = categoryBit(code);
        try self.program.classes.append(self.program.arena.allocator(), class);
        return self.add(.{ .class = index });
    }

    fn parseClass(self: *Parser) ParseError!u32 {
        if (self.program.classes.items.len >= std.math.maxInt(u32)) return error.TooManyClasses;
        const index: u32 = @intCast(self.program.classes.items.len);
        var class = CharClass{};
        class.range_start = @intCast(self.program.ranges.items.len);
        if (self.at < self.source.len and self.source[self.at] == '^') {
            class.negative = true;
            self.at += 1;
        }
        var first = true;
        while (self.at < self.source.len) {
            if (self.source[self.at] == ']' and !first) {
                self.at += 1;
                var literals: usize = 0;
                for (class.bits) |byte| literals += @popCount(byte);
                class.locale_multi = class.range_count != 0 or class.categories != 0 or literals != 1;
                try self.program.classes.append(self.program.arena.allocator(), class);
                return self.add(.{ .class = index });
            }
            first = false;
            var left = try self.codepoint();
            if (left == '\\') {
                if (self.at >= self.source.len) return error.InvalidPattern;
                const code = try self.codepoint();
                if (code < 0x80) {
                    const ascii: u8 = @intCast(code);
                    if (ascii == 'd' or ascii == 'D' or ascii == 's' or ascii == 'S' or ascii == 'w' or ascii == 'W') {
                        class.categories |= categoryBit(ascii);
                        continue;
                    }
                    left = try self.escaped(ascii, true);
                } else left = code;
            }
            if (self.at + 1 < self.source.len and self.source[self.at] == '-' and self.source[self.at + 1] != ']') {
                self.at += 1;
                var right = try self.codepoint();
                if (right == '\\') {
                    if (self.at >= self.source.len) return error.InvalidPattern;
                    const code = try self.codepoint();
                    right = if (code < 0x80) try self.escaped(@intCast(code), true) else code;
                }
                if (right < left) return error.InvalidPattern;
                if (left < 256) {
                    const stop = @min(right, 255);
                    for (@as(usize, left)..@as(usize, stop) + 1) |raw| setBit(&class, @intCast(raw));
                }
                if (right >= 256) {
                    if (self.program.ranges.items.len >= std.math.maxInt(u32)) return error.Unsupported;
                    try self.program.ranges.append(self.program.arena.allocator(), .{ .left = @max(left, 256), .right = right });
                    class.range_count += 1;
                }
            } else if (left < 256) setBit(&class, @intCast(left)) else {
                if (self.program.ranges.items.len >= std.math.maxInt(u32)) return error.Unsupported;
                try self.program.ranges.append(self.program.arena.allocator(), .{ .left = left, .right = left });
                class.range_count += 1;
            }
        }
        return error.InvalidPattern;
    }

    fn atom(self: *Parser) ParseError!u32 {
        if (self.at >= self.source.len) return error.InvalidPattern;
        const value = try self.codepoint();
        return switch (value) {
            '.' => self.add(.dot),
            '^' => self.add(.begin),
            '$' => self.add(.end),
            '[' => self.parseClass(),
            '(' => blk: {
                var capturing = true;
                var group_name: ?[]const u8 = null;
                if (self.at < self.source.len and self.source[self.at] == '?') {
                    if (self.at + 1 >= self.source.len) return error.Unsupported;
                    if (self.source[self.at + 1] == ':') {
                        self.at += 2;
                        capturing = false;
                    } else if (self.source[self.at + 1] == '>') {
                        self.at += 2;
                        const child = try self.alternative();
                        if (self.at >= self.source.len or self.source[self.at] != ')') return error.InvalidPattern;
                        self.at += 1;
                        break :blk self.add(.{ .atomic = child });
                    } else if (self.source[self.at + 1] == '=' or self.source[self.at + 1] == '!') {
                        const positive = self.source[self.at + 1] == '=';
                        self.at += 2;
                        const child = try self.alternative();
                        if (self.at >= self.source.len or self.source[self.at] != ')') return error.InvalidPattern;
                        self.at += 1;
                        self.program.references = true;
                        break :blk self.add(.{ .look = .{ .child = child, .behind = false, .positive = positive, .width = 0 } });
                    } else if (self.at + 2 < self.source.len and self.source[self.at + 1] == '<' and (self.source[self.at + 2] == '=' or self.source[self.at + 2] == '!')) {
                        const positive = self.source[self.at + 2] == '=';
                        self.at += 3;
                        try self.lookbehind_bases.append(self.program.arena.allocator(), self.program.groups);
                        const child = self.alternative() catch |err| {
                            self.lookbehind_bases.items.len -= 1;
                            return err;
                        };
                        self.lookbehind_bases.items.len -= 1;
                        if (self.at >= self.source.len or self.source[self.at] != ')') return error.InvalidPattern;
                        self.at += 1;
                        const look_width = fixedWidth(self.program, child) orelse return error.Unsupported;
                        if (look_width > std.math.maxInt(u32)) return error.Unsupported;
                        self.program.references = true;
                        break :blk self.add(.{ .look = .{ .child = child, .behind = true, .positive = positive, .width = @intCast(look_width) } });
                    } else if (self.source[self.at + 1] == '(') {
                        self.at += 2;
                        const reference_number = try self.reference();
                        if (reference_number == 0 or reference_number > std.math.maxInt(GroupId) or self.at >= self.source.len or self.source[self.at] != ')') return error.Unsupported;
                        if (self.lookbehind_bases.items.len != 0 and reference_number > self.lookbehind_bases.items[0]) return error.InvalidPattern;
                        self.at += 1;
                        const yes = try self.sequence();
                        var no = try self.add(.empty);
                        if (self.at < self.source.len and self.source[self.at] == '|') {
                            self.at += 1;
                            no = try self.sequence();
                        }
                        if (self.at >= self.source.len or self.source[self.at] != ')') return error.InvalidPattern;
                        self.at += 1;
                        self.program.references = true;
                        break :blk self.add(.{ .conditional = .{ .number = @intCast(reference_number), .yes = yes, .no = no } });
                    } else if (self.at + 2 < self.source.len and self.source[self.at + 1] == 'P' and self.source[self.at + 2] == '<') {
                        self.at += 3;
                        group_name = try self.identifier('>');
                    } else if (self.at + 2 < self.source.len and self.source[self.at + 1] == 'P' and self.source[self.at + 2] == '=') {
                        self.at += 3;
                        if (self.at < self.source.len and std.ascii.isDigit(self.source[self.at])) return error.InvalidPattern;
                        const reference_number = try self.reference();
                        if (reference_number < self.open_groups.items.len and self.open_groups.items[reference_number]) return error.InvalidPattern;
                        if (self.lookbehind_bases.items.len != 0 and reference_number > self.lookbehind_bases.items[0]) return error.InvalidPattern;
                        if (self.at >= self.source.len or self.source[self.at] != ')') return error.InvalidPattern;
                        self.at += 1;
                        self.program.references = true;
                        break :blk self.add(.{ .backref = @intCast(reference_number) });
                    } else if (self.source[self.at + 1] == 'i' or self.source[self.at + 1] == 'm' or self.source[self.at + 1] == 's' or self.source[self.at + 1] == 'x' or self.source[self.at + 1] == 'a' or self.source[self.at + 1] == 'u' or self.source[self.at + 1] == 'L' or self.source[self.at + 1] == '-') {
                        self.at += 1;
                        var flags: u32 = self.program.flags;
                        var removing = false;
                        var saw_flag = false;
                        while (self.at < self.source.len and self.source[self.at] != ')' and self.source[self.at] != ':') : (self.at += 1) {
                            const mark = self.source[self.at];
                            if (mark == '-') {
                                if (removing) return error.InvalidPattern;
                                removing = true;
                                continue;
                            }
                            const bit: u32 = switch (mark) {
                                'i' => 2,
                                'L' => 4,
                                'm' => 8,
                                's' => 16,
                                'x' => 64,
                                'a' => 256,
                                'u' => 32,
                                else => return error.Unsupported,
                            };
                            if (removing and bit & (4 | 32 | 256) != 0) return error.InvalidPattern;
                            if (!removing and bit & (4 | 32 | 256) != 0) flags &= ~@as(u32, 4 | 32 | 256);
                            if (removing) flags &= ~bit else flags |= bit;
                            saw_flag = true;
                        }
                        if (!saw_flag or self.at >= self.source.len) return error.InvalidPattern;
                        if (self.source[self.at] == ':') {
                            self.at += 1;
                            const previous = self.program.flags;
                            self.program.flags = flags;
                            const child = self.alternative() catch |err| {
                                self.program.flags = previous;
                                return err;
                            };
                            if (self.at >= self.source.len or self.source[self.at] != ')') {
                                self.program.flags = previous;
                                return error.InvalidPattern;
                            }
                            self.at += 1;
                            self.program.flags = previous;
                            break :blk self.add(.{ .scoped = .{ .child = child, .flags = flags } });
                        }
                        self.at += 1;
                        self.program.flags = flags;
                        break :blk self.add(.empty);
                    } else return error.Unsupported;
                }
                var group_number: GroupId = 0;
                if (capturing) {
                    group_number = std.math.add(GroupId, self.program.groups, 1) catch return error.TooManyGroups;
                    if (@as(u64, group_number) > std.math.maxInt(isize)) return error.TooManyGroups;
                    try self.open_groups.append(self.program.arena.allocator(), true);
                    self.program.groups = group_number;
                    if (group_name) |name| try self.addName(name, group_number);
                }
                const child = try self.alternative();
                if (capturing) self.open_groups.items[group_number] = false;
                if (self.at >= self.source.len or self.source[self.at] != ')') return error.InvalidPattern;
                self.at += 1;
                break :blk if (capturing) try self.add(.{ .group = .{ .child = child, .number = group_number } }) else child;
            },
            '\\' => blk: {
                if (self.at >= self.source.len) return error.InvalidPattern;
                const scalar = try self.codepoint();
                if (scalar >= 0x80) break :blk self.add(.{ .literal = scalar });
                const code: u8 = @intCast(scalar);
                if (code == 'd' or code == 'D' or code == 's' or code == 'S' or code == 'w' or code == 'W') break :blk self.category(code);
                if (code == 'A') break :blk self.add(.absolute_begin);
                if (code == 'Z' or code == 'z') break :blk self.add(.absolute_end);
                if (code == 'b' or code == 'B') break :blk self.add(.{ .boundary = code == 'b' });
                if (code >= '1' and code <= '9') {
                    if (code <= '7' and self.at + 1 < self.source.len and self.source[self.at] >= '0' and self.source[self.at] <= '7' and self.source[self.at + 1] >= '0' and self.source[self.at + 1] <= '7') {
                        const octal: u32 = @as(u32, code - '0') * 64 + @as(u32, self.source[self.at] - '0') * 8 + @as(u32, self.source[self.at + 1] - '0');
                        if (octal > 255) return error.InvalidPattern;
                        self.at += 2;
                        break :blk self.add(.{ .literal = octal });
                    }
                    var reference_number: usize = code - '0';
                    if (self.at < self.source.len and std.ascii.isDigit(self.source[self.at])) {
                        reference_number = reference_number * 10 + self.source[self.at] - '0';
                        self.at += 1;
                    }
                    if (reference_number > self.program.groups) return error.Unsupported;
                    if (reference_number < self.open_groups.items.len and self.open_groups.items[reference_number]) return error.InvalidPattern;
                    if (self.lookbehind_bases.items.len != 0 and reference_number > self.lookbehind_bases.items[0]) return error.InvalidPattern;
                    self.program.references = true;
                    break :blk self.add(.{ .backref = @intCast(reference_number) });
                }
                break :blk self.add(.{ .literal = try self.escaped(code, false) });
            },
            '*', '+', '?', ')' => error.InvalidPattern,
            else => self.add(.{ .literal = value }),
        };
    }

    fn number(self: *Parser) ParseError!usize {
        const begin = self.at;
        var value: usize = 0;
        while (self.at < self.source.len and std.ascii.isDigit(self.source[self.at])) : (self.at += 1) {
            value = std.math.mul(usize, value, 10) catch return error.InvalidPattern;
            value = std.math.add(usize, value, self.source[self.at] - '0') catch return error.InvalidPattern;
            if (value >= std.math.maxInt(u32)) return error.InvalidPattern;
        }
        if (self.at == begin) return error.InvalidPattern;
        return value;
    }

    fn identifier(self: *Parser, close: u8) ParseError![]const u8 {
        const begin = self.at;
        while (self.at < self.source.len and self.source[self.at] != close) : (self.at += 1) {}
        if (self.at >= self.source.len or self.at == begin) return error.InvalidPattern;
        const value = self.source[begin..self.at];
        const text_mode = self.program.flags & text_pattern_flag != 0;
        if (!(std.ascii.isAlphabetic(value[0]) or value[0] == '_' or text_mode and value[0] >= 0x80)) return error.InvalidPattern;
        for (value[1..]) |item| if (!(std.ascii.isAlphanumeric(item) or item == '_' or text_mode and item >= 0x80)) return error.InvalidPattern;
        self.at += 1;
        return value;
    }

    fn addName(self: *Parser, name: []const u8, group: GroupId) ParseError!void {
        for (self.program.names.items) |value| {
            if (std.mem.eql(u8, value.bytes, name)) return error.InvalidPattern;
        }
        const allocator = self.program.arena.allocator();
        const owned = try allocator.dupe(u8, name);
        try self.program.names.append(allocator, .{ .bytes = owned, .group = group });
    }

    fn reference(self: *Parser) ParseError!usize {
        if (self.at < self.source.len and std.ascii.isDigit(self.source[self.at])) return self.number();
        const begin = self.at;
        while (self.at < self.source.len and self.source[self.at] != ')') : (self.at += 1) {}
        if (self.at == begin) return error.InvalidPattern;
        const name = self.source[begin..self.at];
        for (self.program.names.items) |value| {
            if (std.mem.eql(u8, value.bytes, name)) return value.group;
        }
        return error.Unsupported;
    }

    fn repeated(self: *Parser) ParseError!u32 {
        const child = try self.atom();
        try self.skip();
        if (self.at >= self.source.len) return child;
        const mark = self.source[self.at];
        if (mark == '{' and !self.braceRepeat()) return child;
        if (mark == '*' or mark == '+' or mark == '?' or mark == '{') {
            switch (self.program.nodes.items[child]) {
                .begin, .end, .absolute_begin, .absolute_end, .boundary => return error.InvalidPattern,
                else => {},
            }
        }
        var minimum: usize = 0;
        var maximum: usize = 0;
        switch (mark) {
            '*' => {
                minimum = 0;
                maximum = unbounded;
                self.at += 1;
            },
            '+' => {
                minimum = 1;
                maximum = unbounded;
                self.at += 1;
            },
            '?' => {
                minimum = 0;
                maximum = 1;
                self.at += 1;
            },
            '{' => {
                self.at += 1;
                minimum = if (self.at < self.source.len and self.source[self.at] == ',') 0 else try self.number();
                if (self.at < self.source.len and self.source[self.at] == ',') {
                    self.at += 1;
                    maximum = if (self.at < self.source.len and self.source[self.at] == '}') unbounded else try self.number();
                } else maximum = minimum;
                if (self.at >= self.source.len or self.source[self.at] != '}' or maximum < minimum) return error.InvalidPattern;
                self.at += 1;
            },
            else => return child,
        }
        var lazy = false;
        var possessive = false;
        if (self.at < self.source.len and self.source[self.at] == '?') {
            lazy = true;
            self.at += 1;
        }
        if (self.at < self.source.len and self.source[self.at] == '+') {
            if (lazy) return error.InvalidPattern;
            possessive = true;
            self.at += 1;
        }
        if (self.at < self.source.len and (self.source[self.at] == '*' or self.source[self.at] == '+' or self.source[self.at] == '?' or self.source[self.at] == '{' and self.braceRepeat())) return error.InvalidPattern;
        return self.add(.{ .repeat = .{ .child = child, .minimum = minimum, .maximum = maximum, .lazy = lazy, .possessive = possessive } });
    }

    fn braceRepeat(self: *const Parser) bool {
        if (self.at >= self.source.len or self.source[self.at] != '{') return false;
        var cursor = self.at + 1;
        const left = cursor;
        while (cursor < self.source.len and std.ascii.isDigit(self.source[cursor])) : (cursor += 1) {}
        const has_left = cursor != left;
        var has_comma = false;
        if (cursor < self.source.len and self.source[cursor] == ',') {
            has_comma = true;
            cursor += 1;
            while (cursor < self.source.len and std.ascii.isDigit(self.source[cursor])) : (cursor += 1) {}
        }
        return (has_left or has_comma) and cursor < self.source.len and self.source[cursor] == '}';
    }

    fn balanced(self: *Parser, values: []const u32, alternative_node: bool) ParseError!u32 {
        if (values.len == 1) return values[0];
        const middle = values.len / 2;
        const left = try self.balanced(values[0..middle], alternative_node);
        const right = try self.balanced(values[middle..], alternative_node);
        return if (alternative_node) self.add(.{ .alternative = .{ .left = left, .right = right } }) else self.add(.{ .sequence = .{ .left = left, .right = right } });
    }

    fn sequence(self: *Parser) ParseError!u32 {
        var values: std.ArrayList(u32) = .empty;
        try self.skip();
        while (self.at < self.source.len and self.source[self.at] != '|' and self.source[self.at] != ')') {
            try values.append(self.program.arena.allocator(), try self.repeated());
            try self.skip();
        }
        return if (values.items.len == 0) self.add(.empty) else self.balanced(values.items, false);
    }

    fn alternative(self: *Parser) ParseError!u32 {
        if (self.recursion_enter) |enter| {
            if (enter(self.recursion_context) != 0) return error.RecursionLimit;
        }
        defer if (self.recursion_leave) |leave| leave(self.recursion_context);
        if (self.recursion_enter) |enter| {
            if (enter(self.recursion_context) != 0) return error.RecursionLimit;
        }
        defer if (self.recursion_leave) |leave| leave(self.recursion_context);
        var values: std.ArrayList(u32) = .empty;
        try values.append(self.program.arena.allocator(), try self.sequence());
        while (self.at < self.source.len and self.source[self.at] == '|') {
            self.at += 1;
            try values.append(self.program.arena.allocator(), try self.sequence());
        }
        return self.balanced(values.items, true);
    }
};

fn fixedWidth(program: *const Program, index: u32) ?usize {
    return switch (program.nodes.items[index]) {
        .empty, .begin, .end, .absolute_begin, .absolute_end, .boundary, .look => 0,
        .literal, .dot, .class => 1,
        .sequence => |pair| blk: {
            const left = fixedWidth(program, pair.left) orelse break :blk null;
            const right = fixedWidth(program, pair.right) orelse break :blk null;
            break :blk std.math.add(usize, left, right) catch null;
        },
        .alternative => |pair| blk: {
            const left = fixedWidth(program, pair.left) orelse break :blk null;
            const right = fixedWidth(program, pair.right) orelse break :blk null;
            break :blk if (left == right) left else null;
        },
        .repeat => |repeat| blk: {
            if (repeat.minimum != repeat.maximum) break :blk null;
            const child = fixedWidth(program, repeat.child) orelse break :blk null;
            break :blk std.math.mul(usize, child, repeat.minimum) catch null;
        },
        .group => |group| fixedWidth(program, group.child),
        .atomic => |child| fixedWidth(program, child),
        .scoped => |scoped| fixedWidth(program, scoped.child),
        .conditional => |conditional| blk: {
            const yes = fixedWidth(program, conditional.yes) orelse break :blk null;
            const no = fixedWidth(program, conditional.no) orelse break :blk null;
            break :blk if (yes == no) yes else null;
        },
        .backref => |number| blk: {
            for (program.nodes.items) |node| {
                switch (node) {
                    .group => |group| if (group.number == number) break :blk fixedWidth(program, group.child),
                    else => {},
                }
            }
            break :blk null;
        },
    };
}

const Positions = struct {
    values: [max_positions]usize = undefined,
    count: usize = 0,
    fn add(self: *Positions, value: usize) void {
        if (self.count < max_positions) {
            self.values[self.count] = value;
            self.count += 1;
        }
    }
};

const Subject = struct {
    data: [*]const u8,
    length: usize,
    kind: u8,

    fn at(self: Subject, index: usize) u32 {
        return switch (self.kind) {
            1 => self.data[index],
            2 => blk: {
                const values: [*]align(1) const u16 = @ptrCast(self.data);
                break :blk values[index];
            },
            4 => blk: {
                const values: [*]align(1) const u32 = @ptrCast(self.data);
                break :blk values[index];
            },
            else => 0,
        };
    }
};

fn asciiMode(flags: u32) bool {
    return flags & 32 == 0 or flags & (4 | 256) != 0;
}

fn localeByteFlags(flags: u32) bool {
    return flags & 4 != 0 and flags & text_pattern_flag == 0;
}

fn localeByteLower(value: u32) u32 {
    if (value > 255) return value;
    const lowered = tolower(@as(c_int, @intCast(value)));
    return if (lowered >= 0 and lowered <= 255) @intCast(lowered) else value;
}

fn localeByteOther(value: u32) u32 {
    if (value > 255) return value;
    const lowered = localeByteLower(value);
    if (lowered != value) return lowered;
    for (0..256) |candidate| {
        const other: u32 = @intCast(candidate);
        if (other != value and localeByteLower(other) == lowered) return other;
    }
    return value;
}

fn localeByteAlnum(value: u32) bool {
    return value <= 255 and isalnum(@as(c_int, @intCast(value))) != 0;
}

fn folded(value: u32, ascii_only: bool) u32 {
    if (ascii_only) return if (value >= 'A' and value <= 'Z') value + 32 else value;
    const lower = _PyUnicode_ToLowercase(value);
    return switch (lower) {
        0x69, 0x131 => 0x69,
        0x73, 0x17f => 0x73,
        0xb5, 0x3bc => 0xb5,
        0x345, 0x3b9, 0x1fbe => 0x345,
        0x390, 0x1fd3 => 0x390,
        0x3b0, 0x1fe3 => 0x3b0,
        0x3b2, 0x3d0 => 0x3b2,
        0x3b5, 0x3f5 => 0x3b5,
        0x3b8, 0x3d1 => 0x3b8,
        0x3ba, 0x3f0 => 0x3ba,
        0x3c0, 0x3d6 => 0x3c0,
        0x3c1, 0x3f1 => 0x3c1,
        0x3c2, 0x3c3 => 0x3c2,
        0x3c6, 0x3d5 => 0x3c6,
        0x432, 0x1c80 => 0x432,
        0x434, 0x1c81 => 0x434,
        0x43e, 0x1c82 => 0x43e,
        0x441, 0x1c83 => 0x441,
        0x442, 0x1c84, 0x1c85 => 0x442,
        0x44a, 0x1c86 => 0x44a,
        0x463, 0x1c87 => 0x463,
        0xa64b, 0x1c88 => 0xa64b,
        0x1e61, 0x1e9b => 0x1e61,
        0xfb05, 0xfb06 => 0xfb05,
        else => lower,
    };
}

fn equal(left: u32, right: u32, flags: u32) bool {
    if (left == right) return true;
    if (flags & 2 == 0) return false;
    if (localeByteFlags(flags)) return localeByteLower(left) == localeByteLower(right);
    if (left < 128 and right < 128) return std.ascii.toLower(@as(u8, @intCast(left))) == std.ascii.toLower(@as(u8, @intCast(right)));
    const ascii_only = asciiMode(flags);
    return folded(left, ascii_only) == folded(right, ascii_only);
}

fn backrefEqual(left: u32, right: u32, flags: u32) bool {
    if (left == right) return true;
    if (flags & 2 == 0) return false;
    if (localeByteFlags(flags)) return localeByteLower(left) == localeByteLower(right);
    if (asciiMode(flags)) {
        const lower_left = if (left >= 'A' and left <= 'Z') left + 32 else left;
        const lower_right = if (right >= 'A' and right <= 'Z') right + 32 else right;
        return lower_left == lower_right;
    }
    return _PyUnicode_ToLowercase(left) == _PyUnicode_ToLowercase(right);
}

fn categoryBit(code: u8) u8 {
    return switch (code) {
        'd' => 1,
        'D' => 2,
        's' => 4,
        'S' => 8,
        'w' => 16,
        'W' => 32,
        else => 0,
    };
}

fn category(code: u8, value: u32, flags: u32) bool {
    const ascii_only = asciiMode(flags);
    const found = switch (std.ascii.toLower(code)) {
        'd' => if (ascii_only or value < 128) value >= '0' and value <= '9' else _PyUnicode_IsDecimalDigit(value) != 0,
        's' => if (ascii_only or value < 128) value == ' ' or value == '\t' or value == '\n' or value == '\r' or value == 11 or value == 12 or (!ascii_only and value >= 0x1c and value <= 0x1f) else _PyUnicode_IsWhitespace(value) != 0,
        'w' => if (localeByteFlags(flags)) localeByteAlnum(value) or value == '_' else if (ascii_only or value < 128) value < 128 and (std.ascii.isAlphanumeric(@intCast(value)) or value == '_') else value == '_' or _PyUnicode_IsAlpha(value) != 0 or _PyUnicode_IsDecimalDigit(value) != 0 or _PyUnicode_IsDigit(value) != 0 or _PyUnicode_IsNumeric(value) != 0,
        else => false,
    };
    return if (std.ascii.isUpper(code)) !found else found;
}

fn rangeCase(left: u32, right: u32, value: u32, flags: u32) bool {
    if (value >= left and value <= right) return true;
    if (localeByteFlags(flags)) {
        if (value > 255 or left > 255) return false;
        const lowered = localeByteLower(value);
        const stop = @min(right, 255);
        for (@as(usize, @intCast(left))..@as(usize, @intCast(stop)) + 1) |candidate| {
            if (localeByteLower(@intCast(candidate)) == lowered) return true;
        }
        return false;
    }
    const ascii_only = asciiMode(flags);
    if (ascii_only) {
        const lower = if (value >= 'A' and value <= 'Z') value + 32 else value;
        const upper = if (value >= 'a' and value <= 'z') value - 32 else value;
        return lower >= left and lower <= right or upper >= left and upper <= right;
    }
    const lower = _PyUnicode_ToLowercase(value);
    const upper = if (multiUpper(value)) value else _PyUnicode_ToUppercase(value);
    const fold = folded(value, false);
    if (lower >= left and lower <= right or upper >= left and upper <= right or fold >= left and fold <= right) return true;
    const variants = [_][4]u32{
        .{ 'I', 'i', 0x130, 0x131 },
        .{ 'S', 's', 0x17f, 0x17f },
        .{ 'K', 'k', 0x212a, 0x212a },
        .{ 0x412, 0x432, 0x1c80, 0x1c80 },
        .{ 0xfb05, 0xfb06, 0xfb05, 0xfb06 },
        .{ 0xdf, 0x1e9e, 0xdf, 0x1e9e },
        .{ 0xb5, 0x3bc, 0xb5, 0x3bc },
        .{ 0x399, 0x3b9, 0x345, 0x1fbe },
        .{ 0x390, 0x1fd3, 0x390, 0x1fd3 },
        .{ 0x3b0, 0x1fe3, 0x3b0, 0x1fe3 },
        .{ 0x392, 0x3b2, 0x3d0, 0x392 },
        .{ 0x395, 0x3b5, 0x3f5, 0x395 },
        .{ 0x398, 0x3b8, 0x3d1, 0x3f4 },
        .{ 0x39a, 0x3ba, 0x3f0, 0x39a },
        .{ 0x3a0, 0x3c0, 0x3d6, 0x3a0 },
        .{ 0x3a1, 0x3c1, 0x3f1, 0x3a1 },
        .{ 0x3a3, 0x3c2, 0x3c3, 0x3a3 },
        .{ 0x3a6, 0x3c6, 0x3d5, 0x3a6 },
        .{ 0x3a9, 0x3c9, 0x2126, 0x3a9 },
        .{ 0x414, 0x434, 0x1c81, 0x414 },
        .{ 0x41e, 0x43e, 0x1c82, 0x41e },
        .{ 0x421, 0x441, 0x1c83, 0x421 },
        .{ 0x422, 0x442, 0x1c84, 0x1c85 },
        .{ 0x42a, 0x44a, 0x1c86, 0x42a },
        .{ 0x462, 0x463, 0x1c87, 0x462 },
        .{ 0xa64a, 0xa64b, 0x1c88, 0xa64a },
        .{ 0x1e60, 0x1e61, 0x1e9b, 0x1e60 },
    };
    for (variants) |set| {
        var member = false;
        var included = false;
        for (set) |item| {
            member = member or value == item;
            included = included or item >= left and item <= right;
        }
        if (member and included) return true;
    }
    return false;
}

fn multiUpper(value: u32) bool {
    return switch (value) {
        0xdf, 0x149, 0x1f0, 0x390, 0x3b0, 0x587,
        0x1e96...0x1e9a,
        0x1f50, 0x1f52, 0x1f54, 0x1f56,
        0x1f80...0x1faf,
        0x1fb2...0x1fb4, 0x1fb6, 0x1fb7, 0x1fbc,
        0x1fc2...0x1fc4, 0x1fc6, 0x1fc7, 0x1fcc,
        0x1fd2, 0x1fd3, 0x1fd6, 0x1fd7,
        0x1fe2...0x1fe4, 0x1fe6, 0x1fe7,
        0x1ff2...0x1ff4, 0x1ff6, 0x1ff7, 0x1ffc,
        0xfb00...0xfb06, 0xfb13...0xfb17,
        => true,
        else => false,
    };
}

fn classBit(class: *const CharClass, value: u32) bool {
    return value < 256 and class.bits[@as(usize, @intCast(value)) >> 3] & (@as(u8, 1) << @intCast(value & 7)) != 0;
}

fn classRaw(program: *const Program, class: *const CharClass, value: u32, flags: u32) bool {
    if (classBit(class, value)) return true;
    for (program.ranges.items[class.range_start..@as(usize, class.range_start) + class.range_count]) |range| if (value >= range.left and value <= range.right) return true;
    if (class.categories != 0) {
        const codes = [_]u8{ 'd', 'D', 's', 'S', 'w', 'W' };
        for (codes) |code| if (class.categories & categoryBit(code) != 0 and category(code, value, flags)) return true;
    }
    return false;
}

fn classMatch(program: *const Program, class: *const CharClass, value: u32, flags: u32) bool {
    const locale_bytes = localeByteFlags(flags);
    if (!locale_bytes and value < 256 and class.match_flags == flags & 0xffff) return class.match_bits[@as(usize, @intCast(value)) >> 3] & (@as(u8, 1) << @intCast(value & 7)) != 0;
    if (class.negative and class.locale_multi and flags & 2 != 0 and locale_bytes) {
        const other = localeByteOther(value);
        return !classRaw(program, class, value, flags) or !classRaw(program, class, other, flags);
    }
    var found = classBit(class, value);
    if (found) return !class.negative;
    if (!found and flags & 2 != 0) {
        if (locale_bytes) {
            const lowered = localeByteLower(value);
            for (0..256) |candidate| {
                const other: u32 = @intCast(candidate);
                if (classBit(class, other) and localeByteLower(other) == lowered) {
                    found = true;
                    break;
                }
            }
        } else {
            const ascii_only = asciiMode(flags);
            const lower: u32 = if (ascii_only) (if (value >= 'A' and value <= 'Z') value + 32 else value) else _PyUnicode_ToLowercase(value);
            const upper: u32 = if (ascii_only) (if (value >= 'a' and value <= 'z') value - 32 else value) else if (multiUpper(value)) value else _PyUnicode_ToUppercase(value);
            const upper_lower: u32 = if (ascii_only or multiUpper(lower)) lower else _PyUnicode_ToUppercase(lower);
            found = classBit(class, lower) or classBit(class, upper) or classBit(class, upper_lower) or classBit(class, folded(value, ascii_only));
        }
    }
    if (!found and flags & 2 != 0 and !asciiMode(flags)) {
        const specials = [_]u32{ 'I', 'i', 0x130, 0x131, 'S', 's', 0x17f, 'K', 'k', 0x212a, 0x412, 0x432, 0x1c80, 0xfb05, 0xfb06, 0xdf, 0x1e9e };
        for (specials) |other| {
            if (folded(other, false) == folded(value, false) and other < 256 and class.bits[@as(usize, @intCast(other)) >> 3] & (@as(u8, 1) << @intCast(other & 7)) != 0) {
                found = true;
                break;
            }
        }
    }
    for (program.ranges.items[class.range_start..@as(usize, class.range_start) + class.range_count]) |range| {
        if (if (flags & 2 != 0) rangeCase(range.left, range.right, value, flags) else value >= range.left and value <= range.right) {
            found = true;
            break;
        }
    }
    if (!found and class.categories != 0) {
        const codes = [_]u8{ 'd', 'D', 's', 'S', 'w', 'W' };
        for (codes) |code| if (class.categories & categoryBit(code) != 0 and category(code, value, flags)) {
            found = true;
            break;
        };
    }
    return if (class.negative) !found else found;
}

fn prepareClasses(program: *Program, index: u32, flags: u32) void {
    switch (program.nodes.items[index]) {
        .class => |class_index| {
            const class = &program.classes.items[class_index];
            if (flags & 4 != 0 or class.match_flags != std.math.maxInt(u32)) return;
            var bits = [_]u8{0} ** 32;
            if (flags & 2 == 0 and class.categories == 0) {
                bits = class.bits;
                if (class.negative) {
                    for (&bits) |*byte| byte.* = ~byte.*;
                }
            } else {
                for (0..256) |value| {
                    if (classMatch(program, class, @intCast(value), flags)) bits[value >> 3] |= @as(u8, 1) << @intCast(value & 7);
                }
            }
            class.match_bits = bits;
            class.match_flags = flags & 0xffff;
        },
        .sequence, .alternative => |pair| {
            prepareClasses(program, pair.left, flags);
            prepareClasses(program, pair.right, flags);
        },
        .repeat => |repeat| prepareClasses(program, repeat.child, flags),
        .group => |group| prepareClasses(program, group.child, flags),
        .conditional => |conditional| {
            prepareClasses(program, conditional.yes, flags);
            prepareClasses(program, conditional.no, flags);
        },
        .atomic => |child| prepareClasses(program, child, flags),
        .look => |look| prepareClasses(program, look.child, flags),
        .scoped => |scoped| prepareClasses(program, scoped.child, scoped.flags),
        else => {},
    }
}

fn runLength(program: *const Program, run: Run, text: Subject, pos: usize, maximum: usize) usize {
    var length: usize = 0;
    switch (program.nodes.items[run.atom]) {
        .literal => |want| {
            if (text.kind == 1 and run.flags & 2 == 0 and want < 256) {
                while (length < maximum and text.data[pos + length] == want) : (length += 1) {}
            } else while (length < maximum and equal(want, text.at(pos + length), run.flags)) : (length += 1) {}
        },
        .dot => {
            if (run.flags & 16 != 0) return maximum;
            if (text.kind == 1) {
                while (length < maximum and text.data[pos + length] != '\n') : (length += 1) {}
            } else while (length < maximum and text.at(pos + length) != '\n') : (length += 1) {}
        },
        .class => |class_index| {
            const class = &program.classes.items[class_index];
            if (text.kind == 1 and class.match_flags == run.flags & 0xffff) {
                while (length < maximum) : (length += 1) {
                    const value = text.data[pos + length];
                    if (class.match_bits[value >> 3] & (@as(u8, 1) << @intCast(value & 7)) == 0) break;
                }
            } else if (text.kind == 2 and class.match_flags == run.flags & 0xffff) {
                const values: [*]align(1) const u16 = @ptrCast(text.data);
                while (length < maximum) : (length += 1) {
                    const value: u32 = values[pos + length];
                    if (value < 256) {
                        if (class.match_bits[@as(usize, value) >> 3] & (@as(u8, 1) << @intCast(value & 7)) == 0) break;
                    } else if (!classMatch(program, class, value, run.flags)) break;
                }
            } else if (text.kind == 4 and class.match_flags == run.flags & 0xffff) {
                const values: [*]align(1) const u32 = @ptrCast(text.data);
                while (length < maximum) : (length += 1) {
                    const value = values[pos + length];
                    if (value < 256) {
                        if (class.match_bits[@as(usize, value) >> 3] & (@as(u8, 1) << @intCast(value & 7)) == 0) break;
                    } else if (!classMatch(program, class, value, run.flags)) break;
                }
            } else while (length < maximum and classMatch(program, class, text.at(pos + length), run.flags)) : (length += 1) {}
        },
        .sequence, .repeat, .group, .atomic, .scoped => {
            const endpos = std.math.add(usize, pos, maximum) catch return length;
            while (length < maximum) {
                const begin = std.math.add(usize, pos, length) catch break;
                var at = begin;
                if (!literalTextMatches(program, run.atom, text, endpos, &at, run.flags)) break;
                const consumed = at - begin;
                if (consumed != run.width) break;
                length = std.math.add(usize, length, consumed) catch break;
            }
        },
        else => while (length < maximum and atomMatch(program, run.atom, text.at(pos + length), run.flags)) : (length += 1) {},
    }
    return length;
}

fn atomMatch(program: *const Program, index: u32, value: u32, flags: u32) bool {
    return switch (program.nodes.items[index]) {
        .literal => |want| equal(want, value, flags),
        .dot => flags & 16 != 0 or value != '\n',
        .class => |class| classMatch(program, &program.classes.items[class], value, flags),
        .alternative => |pair| atomMatch(program, pair.left, value, flags) or atomMatch(program, pair.right, value, flags),
        .group => |group| atomMatch(program, group.child, value, flags),
        .atomic => |child| atomMatch(program, child, value, flags),
        .scoped => |scoped| atomMatch(program, scoped.child, value, scoped.flags),
        else => false,
    };
}

fn word(value: u32, flags: u32) bool {
    return category('w', value, flags);
}

fn repeatWalk(program: *const Program, repeat: Repeat, text: Subject, endpos: usize, pos: usize, count: usize, maximum: usize, out: *Positions, depth: usize, flags: u32) void {
    if (depth > 512) return;
    if (repeat.lazy and count >= repeat.minimum) out.add(pos);
    if (count < maximum) {
        var next = Positions{};
        eval(program, repeat.child, text, endpos, pos, &next, depth + 1, flags);
        for (next.values[0..next.count]) |value| {
            if (value == pos) {
                if (count + 1 >= repeat.minimum) out.add(value);
                continue;
            }
            repeatWalk(program, repeat, text, endpos, value, count + 1, maximum, out, depth + 1, flags);
        }
    }
    if (!repeat.lazy and count >= repeat.minimum) out.add(pos);
}

fn eval(program: *const Program, node_index: u32, text: Subject, endpos: usize, pos: usize, out: *Positions, depth: usize, flags: u32) void {
    if (depth > 512) return;
    switch (program.nodes.items[node_index]) {
        .empty => out.add(pos),
        .literal => |value| if (pos < endpos and equal(value, text.at(pos), flags)) out.add(pos + 1),
        .dot => if (pos < endpos and (flags & 16 != 0 or text.at(pos) != '\n')) out.add(pos + 1),
        .class => |index| if (pos < endpos and classMatch(program, &program.classes.items[index], text.at(pos), flags)) out.add(pos + 1),
        .begin => if (pos == 0 or (flags & 8 != 0 and pos > 0 and text.at(pos - 1) == '\n')) out.add(pos),
        .end => if (pos == endpos or (pos + 1 == endpos and text.at(pos) == '\n') or (flags & 8 != 0 and pos < endpos and text.at(pos) == '\n')) out.add(pos),
        .absolute_begin => if (pos == 0) out.add(pos),
        .absolute_end => if (pos == endpos) out.add(pos),
        .boundary => |want| {
            const left = pos > 0 and word(text.at(pos - 1), flags);
            const right = pos < endpos and word(text.at(pos), flags);
            if ((left != right) == want) out.add(pos);
        },
        .alternative => |pair| {
            eval(program, pair.left, text, endpos, pos, out, depth + 1, flags);
            eval(program, pair.right, text, endpos, pos, out, depth + 1, flags);
        },
        .sequence => |pair| {
            var left = Positions{};
            eval(program, pair.left, text, endpos, pos, &left, depth + 1, flags);
            for (left.values[0..left.count]) |value| eval(program, pair.right, text, endpos, value, out, depth + 1, flags);
        },
        .repeat => |repeat| {
            var maximum = repeat.maximum;
            if (maximum == unbounded or maximum > endpos - pos + repeat.minimum + 1) maximum = endpos - pos + repeat.minimum + 1;
            if (repeat.possessive) {
                var positions = Positions{};
                repeatWalk(program, repeat, text, endpos, pos, 0, maximum, &positions, depth + 1, flags);
                if (positions.count > 0) out.add(positions.values[0]);
            } else repeatWalk(program, repeat, text, endpos, pos, 0, maximum, out, depth + 1, flags);
        },
        .group => |group| eval(program, group.child, text, endpos, pos, out, depth + 1, flags),
        .backref, .conditional => {},
        .atomic => |child| {
            var positions = Positions{};
            eval(program, child, text, endpos, pos, &positions, depth + 1, flags);
            if (positions.count > 0) out.add(positions.values[0]);
        },
        .look => |look| {
            var positions = Positions{};
            const begin = if (look.behind) blk: {
                if (pos < look.width) break :blk null;
                break :blk pos - look.width;
            } else pos;
            if (begin) |value| eval(program, look.child, text, if (look.behind) pos else endpos, value, &positions, depth + 1, flags);
            var found = false;
            for (positions.values[0..positions.count]) |value| {
                if (!look.behind or value == pos) {
                    found = true;
                    break;
                }
            }
            if (found == look.positive) out.add(pos);
        },
        .scoped => |scoped| eval(program, scoped.child, text, endpos, pos, out, depth + 1, scoped.flags),
    }
}

const CompileError = std.mem.Allocator.Error || error{ TooMuchCode, UnsupportedRepeat };

const Flat = struct {
    atom: ?u32 = null,
    flags: u32 = 0,
    layouts: []CaptureLayout,
    layout_count: usize = 0,
};

fn sameAtom(program: *const Program, left: u32, right: u32) bool {
    const first = program.nodes.items[left];
    const second = program.nodes.items[right];
    return switch (first) {
        .literal => |value| switch (second) { .literal => |other| value == other, else => false },
        .dot => switch (second) { .dot => true, else => false },
        .class => |value| switch (second) { .class => |other| value == other, else => false },
        .alternative => |pair| switch (second) { .alternative => |other| sameAtom(program, pair.left, other.left) and sameAtom(program, pair.right, other.right), else => false },
        else => false,
    };
}

fn capturesIn(program: *const Program, index: u32) bool {
    return switch (program.nodes.items[index]) {
        .group => true,
        .sequence, .alternative => |pair| capturesIn(program, pair.left) or capturesIn(program, pair.right),
        .repeat => |repeat| capturesIn(program, repeat.child),
        .atomic => |child| capturesIn(program, child),
        .scoped => |scoped| capturesIn(program, scoped.child),
        else => false,
    };
}

fn isAtom(program: *const Program, index: u32) bool {
    return switch (program.nodes.items[index]) {
        .literal, .dot, .class => true,
        .alternative => |pair| isAtom(program, pair.left) and isAtom(program, pair.right),
        else => false,
    };
}

fn isLiteralText(program: *const Program, index: u32) bool {
    return switch (program.nodes.items[index]) {
        .empty, .literal => true,
        .sequence => |pair| isLiteralText(program, pair.left) and isLiteralText(program, pair.right),
        .atomic => |child| isLiteralText(program, child),
        .scoped => |scoped| isLiteralText(program, scoped.child),
        else => false,
    };
}

fn literalTextMatches(program: *const Program, index: u32, text: Subject, endpos: usize, at: *usize, flags: u32) bool {
    return switch (program.nodes.items[index]) {
        .empty => true,
        .literal => |value| blk: {
            if (at.* >= endpos or !equal(value, text.at(at.*), flags)) break :blk false;
            at.* += 1;
            break :blk true;
        },
        .dot => blk: {
            if (at.* >= endpos or (flags & 16 == 0 and text.at(at.*) == '\n')) break :blk false;
            at.* += 1;
            break :blk true;
        },
        .class => |class| blk: {
            if (at.* >= endpos or !classMatch(program, &program.classes.items[class], text.at(at.*), flags)) break :blk false;
            at.* += 1;
            break :blk true;
        },
        .sequence => |pair| literalTextMatches(program, pair.left, text, endpos, at, flags) and literalTextMatches(program, pair.right, text, endpos, at, flags),
        .repeat => |repeat| blk: {
            if (repeat.minimum != repeat.maximum) break :blk false;
            var count: usize = 0;
            while (count < repeat.minimum) : (count += 1) {
                const before = at.*;
                if (!literalTextMatches(program, repeat.child, text, endpos, at, flags)) break :blk false;
                if (at.* == before) break :blk true;
            }
            break :blk true;
        },
        .group => |group| literalTextMatches(program, group.child, text, endpos, at, flags),
        .atomic => |child| literalTextMatches(program, child, text, endpos, at, flags),
        .scoped => |scoped| literalTextMatches(program, scoped.child, text, endpos, at, scoped.flags),
        else => false,
    };
}

fn addFlatAtom(program: *const Program, index: u32, flags: u32, flat: *Flat) ?usize {
    if (flat.atom) |atom| {
        if (flat.flags != flags or !sameAtom(program, atom, index)) return null;
    } else {
        flat.atom = index;
        flat.flags = flags;
    }
    return 1;
}

fn flatten(program: *const Program, index: u32, flags: u32, base: usize, flat: *Flat) ?usize {
    return switch (program.nodes.items[index]) {
        .literal, .dot, .class => addFlatAtom(program, index, flags, flat),
        .alternative => if (!capturesIn(program, index) and fixedWidth(program, index) == 1 and isAtom(program, index)) addFlatAtom(program, index, flags, flat) else null,
        .sequence => |pair| blk: {
            const left = flatten(program, pair.left, flags, base, flat) orelse break :blk null;
            const next = std.math.add(usize, base, left) catch break :blk null;
            const right = flatten(program, pair.right, flags, next, flat) orelse break :blk null;
            break :blk std.math.add(usize, left, right) catch null;
        },
        .repeat => |repeat| blk: {
            if (repeat.minimum != repeat.maximum) break :blk null;
            const first_layout = flat.layout_count;
            const child = flatten(program, repeat.child, flags, base, flat) orelse break :blk null;
            if (repeat.minimum == 0) {
                flat.layout_count = first_layout;
                break :blk 0;
            }
            const shift = std.math.mul(usize, child, repeat.minimum - 1) catch break :blk null;
            for (flat.layouts[first_layout..flat.layout_count]) |*layout| {
                layout.begin = std.math.add(usize, layout.begin, shift) catch break :blk null;
                layout.end = std.math.add(usize, layout.end, shift) catch break :blk null;
            }
            break :blk std.math.mul(usize, child, repeat.minimum) catch null;
        },
        .group => |group| blk: {
            const width = flatten(program, group.child, flags, base, flat) orelse break :blk null;
            if (flat.layout_count >= flat.layouts.len) break :blk null;
            const end = std.math.add(usize, base, width) catch break :blk null;
            flat.layouts[flat.layout_count] = .{ .number = group.number, .begin = base, .end = end };
            flat.layout_count += 1;
            break :blk width;
        },
        .atomic => |child| flatten(program, child, flags, base, flat),
        .scoped => |scoped| flatten(program, scoped.child, scoped.flags, base, flat),
        else => null,
    };
}

fn flattenRepeatMotif(program: *const Program, index: u32, base: usize, flat: *Flat) ?usize {
    return switch (program.nodes.items[index]) {
        .empty => 0,
        .literal, .dot, .class => 1,
        .sequence => |pair| blk: {
            const left = flattenRepeatMotif(program, pair.left, base, flat) orelse break :blk null;
            const next = std.math.add(usize, base, left) catch break :blk null;
            const right = flattenRepeatMotif(program, pair.right, next, flat) orelse break :blk null;
            break :blk std.math.add(usize, left, right) catch null;
        },
        .repeat => |repeat| blk: {
            if (repeat.minimum != repeat.maximum) break :blk null;
            const first_layout = flat.layout_count;
            const child = flattenRepeatMotif(program, repeat.child, base, flat) orelse break :blk null;
            if (repeat.minimum == 0) {
                flat.layout_count = first_layout;
                break :blk 0;
            }
            const shift = std.math.mul(usize, child, repeat.minimum - 1) catch break :blk null;
            for (flat.layouts[first_layout..flat.layout_count]) |*layout| {
                layout.begin = std.math.add(usize, layout.begin, shift) catch break :blk null;
                layout.end = std.math.add(usize, layout.end, shift) catch break :blk null;
            }
            break :blk std.math.mul(usize, child, repeat.minimum) catch null;
        },
        .group => |group| blk: {
            const width = flattenRepeatMotif(program, group.child, base, flat) orelse break :blk null;
            if (flat.layout_count >= flat.layouts.len) break :blk null;
            const end = std.math.add(usize, base, width) catch break :blk null;
            flat.layouts[flat.layout_count] = .{ .number = group.number, .begin = base, .end = end };
            flat.layout_count += 1;
            break :blk width;
        },
        .atomic => |child| flattenRepeatMotif(program, child, base, flat),
        .scoped => |scoped| flattenRepeatMotif(program, scoped.child, base, flat),
        else => null,
    };
}

fn canBeEmpty(program: *const Program, index: u32) bool {
    return switch (program.nodes.items[index]) {
        .empty, .begin, .end, .absolute_begin, .absolute_end, .boundary, .look, .backref => true,
        .literal, .dot, .class => false,
        .sequence => |pair| canBeEmpty(program, pair.left) and canBeEmpty(program, pair.right),
        .alternative => |pair| canBeEmpty(program, pair.left) or canBeEmpty(program, pair.right),
        .repeat => |repeat| repeat.minimum == 0 or canBeEmpty(program, repeat.child),
        .group => |group| canBeEmpty(program, group.child),
        .conditional => |conditional| canBeEmpty(program, conditional.yes) or canBeEmpty(program, conditional.no),
        .atomic => |child| canBeEmpty(program, child),
        .scoped => |scoped| canBeEmpty(program, scoped.child),
    };
}

fn plainLiteralLength(program: *const Program, index: u32) ?usize {
    return switch (program.nodes.items[index]) {
        .empty => 0,
        .literal => 1,
        .sequence => |pair| blk: {
            const left = plainLiteralLength(program, pair.left) orelse break :blk null;
            const right = plainLiteralLength(program, pair.right) orelse break :blk null;
            break :blk std.math.add(usize, left, right) catch null;
        },
        else => null,
    };
}

fn plainLiteralAt(program: *const Program, index: u32, offset: usize) u32 {
    return switch (program.nodes.items[index]) {
        .literal => |value| value,
        .sequence => |pair| blk: {
            const left = plainLiteralLength(program, pair.left).?;
            break :blk if (offset < left) plainLiteralAt(program, pair.left, offset) else plainLiteralAt(program, pair.right, offset - left);
        },
        else => unreachable,
    };
}

fn gatherLiteralBranches(program: *const Program, index: u32, branches: *[256]u32, count: *usize) bool {
    return switch (program.nodes.items[index]) {
        .alternative => |pair| gatherLiteralBranches(program, pair.left, branches, count) and gatherLiteralBranches(program, pair.right, branches, count),
        else => blk: {
            if (plainLiteralLength(program, index) == null or count.* == branches.len) break :blk false;
            branches[count.*] = index;
            count.* += 1;
            break :blk true;
        },
    };
}

fn literalValueMask(value: u32, flags: u32) ?u32 {
    if (flags & 2 == 0) return @as(u32, 1) << @intCast(value & 31);
    if (value >= 128) return null;
    const byte: u8 = @intCast(value);
    const lower = std.ascii.toLower(byte);
    var mask = (@as(u32, 1) << @intCast(lower & 31)) | (@as(u32, 1) << @intCast(std.ascii.toUpper(byte) & 31));
    if (!asciiMode(flags)) switch (lower) {
        'i' => mask |= (@as(u32, 1) << @intCast(0x130 & 31)) | (@as(u32, 1) << @intCast(0x131 & 31)),
        's' => mask |= @as(u32, 1) << @intCast(0x17f & 31),
        'k' => mask |= @as(u32, 1) << @intCast(0x212a & 31),
        else => {},
    };
    return mask;
}

fn literalPrefixMask(program: *const Program, index: u32, flags: u32) ?u32 {
    return switch (program.nodes.items[index]) {
        .literal => |value| literalValueMask(value, flags),
        .class => |class_index| blk: {
            const class = &program.classes.items[class_index];
            if (class.negative or class.categories != 0 or (flags & 2 != 0 and !asciiMode(flags) and class.range_count != 0)) break :blk null;
            var mask: u32 = 0;
            for (0..256) |raw| {
                if (classMatch(program, class, @intCast(raw), flags)) mask |= @as(u32, 1) << @intCast(raw & 31);
            }
            if (flags & 2 != 0 and !asciiMode(flags)) {
                for ([_]u32{ 0x130, 0x131, 0x17f, 0x212a }) |value| {
                    if (classMatch(program, class, value, flags)) mask |= @as(u32, 1) << @intCast(value & 31);
                }
            }
            for (program.ranges.items[class.range_start..@as(usize, class.range_start) + class.range_count]) |range| {
                if (range.right - range.left >= 31) break :blk std.math.maxInt(u32);
                var value = range.left;
                while (value <= range.right) : (value += 1) mask |= @as(u32, 1) << @intCast(value & 31);
            }
            break :blk mask;
        },
        .sequence => |pair| literalPrefixMask(program, pair.left, flags),
        .alternative => |pair| blk: {
            const left = literalPrefixMask(program, pair.left, flags) orelse break :blk null;
            const right = literalPrefixMask(program, pair.right, flags) orelse break :blk null;
            break :blk left | right;
        },
        .repeat => |repeat| if (repeat.minimum == 0) null else literalPrefixMask(program, repeat.child, flags),
        .group => |group| literalPrefixMask(program, group.child, flags),
        .atomic => |child| literalPrefixMask(program, child, flags),
        .scoped => |scoped| literalPrefixMask(program, scoped.child, scoped.flags),
        else => null,
    };
}

fn prefixRunAccepts(program: *const Program, instruction_index: u32, value: u32) bool {
    const instruction = program.code.items[instruction_index];
    return switch (instruction.op) {
        .run => blk: {
            const run = program.runs.items[instruction.value];
            break :blk atomMatch(program, run.atom, value, run.flags);
        },
        .class => classMatch(program, &program.classes.items[instruction.left], value, instruction.extra),
        else => false,
    };
}

fn excludesOnly(program: *const Program, run_index: u32, value: u32, flags: u32) bool {
    if (run_index >= program.runs.items.len or value >= 256) return false;
    const run = program.runs.items[run_index];
    if (run.width != 1 or run.minimum != 0 or run.maximum != unbounded or run.possessive or run.flags & ~text_pattern_flag != flags) return false;
    const atom = program.nodes.items[run.atom];
    if (atom != .class) return false;
    const class = &program.classes.items[atom.class];
    if (!class.negative or class.categories != 0 or class.range_count != 0) return false;
    for (class.bits, 0..) |byte, index| {
        const wanted: u8 = if (index == value >> 3) @as(u8, 1) << @intCast(value & 7) else 0;
        if (byte != wanted) return false;
    }
    return true;
}

const Compiler = struct {
    program: *Program,
    flags: u32,

    fn emit(self: *Compiler, instruction: Instruction) CompileError!u32 {
        if (self.program.code.items.len >= std.math.maxInt(u32)) return error.TooMuchCode;
        const index: u32 = @intCast(self.program.code.items.len);
        try self.program.code.append(self.program.arena.allocator(), instruction);
        return index;
    }

    fn emitRun(self: *Compiler, repeat: Repeat) CompileError!void {
        var inline_layouts: [inline_capture_layouts]CaptureLayout = undefined;
        const group_count: usize = self.program.groups;
        const layouts: []CaptureLayout = if (group_count <= inline_layouts.len)
            inline_layouts[0..group_count]
        else
            try self.program.arena.allocator().alloc(CaptureLayout, group_count);
        var flat = Flat{ .layouts = layouts };
        var child = repeat.child;
        if (repeat.lazy and !repeat.possessive and repeat.minimum == 0 and repeat.maximum == unbounded and !capturesIn(self.program, child)) {
            switch (self.program.nodes.items[child]) {
                .alternative => |pair| {
                    if (self.program.nodes.items[pair.left] == .empty and fixedWidth(self.program, pair.right) == 1 and isAtom(self.program, pair.right)) child = pair.right;
                    if (self.program.nodes.items[pair.right] == .empty and fixedWidth(self.program, pair.left) == 1 and isAtom(self.program, pair.left)) child = pair.left;
                },
                else => {},
            }
        }
        const width = flatten(self.program, child, self.flags, 0, &flat) orelse blk: {
            flat = Flat{ .layouts = layouts };
            const motif_width = flattenRepeatMotif(self.program, child, 0, &flat) orelse return error.UnsupportedRepeat;
            if (motif_width <= 1 or
                (repeat.minimum <= 128 and
                    (repeat.maximum == unbounded or repeat.maximum <= 256)))
            {
                return error.UnsupportedRepeat;
            }
            flat.atom = child;
            flat.flags = self.flags;
            break :blk motif_width;
        };
        if (width == 0 or flat.atom == null or self.program.runs.items.len >= std.math.maxInt(u32) or self.program.layouts.items.len >= std.math.maxInt(u32) or flat.layout_count > std.math.maxInt(u32)) return error.UnsupportedRepeat;
        const total_layouts = std.math.add(usize, self.program.layouts.items.len, flat.layout_count) catch return error.UnsupportedRepeat;
        if (total_layouts > std.math.maxInt(u32)) return error.UnsupportedRepeat;
        const layout_start: u32 = @intCast(self.program.layouts.items.len);
        try self.program.layouts.appendSlice(self.program.arena.allocator(), flat.layouts[0..flat.layout_count]);
        const run_index: u32 = @intCast(self.program.runs.items.len);
        try self.program.runs.append(self.program.arena.allocator(), .{ .atom = flat.atom.?, .flags = flat.flags, .width = width, .minimum = repeat.minimum, .maximum = repeat.maximum, .lazy = repeat.lazy, .possessive = repeat.possessive, .layout_start = layout_start, .layout_count = @intCast(flat.layout_count) });
        _ = try self.emit(.{ .op = .run, .value = run_index });
    }

    fn emitRepeatChild(self: *Compiler, child: u32, possessive: bool) CompileError!void {
        if (possessive) _ = try self.emit(.{ .op = .atomic_begin });
        try self.node(child);
        if (possessive) _ = try self.emit(.{ .op = .atomic_end });
    }

    noinline fn tryLiteralBranches(self: *Compiler, index: u32) CompileError!bool {
        var branches: [256]u32 = undefined;
        var branch_count: usize = 0;
        if (!gatherLiteralBranches(self.program, index, &branches, &branch_count) or branch_count <= 1) return false;

        var common = plainLiteralLength(self.program, branches[0]).?;
        for (branches[1..branch_count]) |branch| {
            const length = plainLiteralLength(self.program, branch).?;
            common = @min(common, length);
            var at: usize = 0;
            while (at < common and plainLiteralAt(self.program, branches[0], at) == plainLiteralAt(self.program, branch, at)) : (at += 1) {}
            common = at;
        }
        if (common < 2) return false;

        for (0..common) |at| _ = try self.emit(.{ .op = .literal, .value = plainLiteralAt(self.program, branches[0], at), .extra = @intCast(self.flags & 0xffff) });
        var starts: [256]u32 = undefined;
        var splits: [255]u32 = undefined;
        var jumps: [255]u32 = undefined;
        for (branches[0..branch_count], 0..) |branch, branch_index| {
            if (branch_index + 1 < branch_count) splits[branch_index] = try self.emit(.{ .op = .split });
            starts[branch_index] = @intCast(self.program.code.items.len);
            const length = plainLiteralLength(self.program, branch).?;
            for (common..length) |at| _ = try self.emit(.{ .op = .literal, .value = plainLiteralAt(self.program, branch, at), .extra = @intCast(self.flags & 0xffff) });
            if (branch_index + 1 < branch_count) jumps[branch_index] = try self.emit(.{ .op = .jump });
        }
        const finish: u32 = @intCast(self.program.code.items.len);
        for (0..branch_count - 1) |branch_index| {
            const split_index = splits[branch_index];
            self.program.code.items[split_index].left = starts[branch_index];
            self.program.code.items[split_index].right = starts[branch_index + 1] - @as(u32, if (branch_index + 2 < branch_count) 1 else 0);
            const left_length = plainLiteralLength(self.program, branches[branch_index]).?;
            if (left_length > common) if (literalValueMask(plainLiteralAt(self.program, branches[branch_index], common), self.flags)) |left_mask| {
                var right_mask: u32 = 0;
                var complete = true;
                for (branches[branch_index + 1 .. branch_count]) |other| {
                    const right_length = plainLiteralLength(self.program, other).?;
                    if (right_length == common) {
                        complete = false;
                        break;
                    }
                    right_mask |= literalValueMask(plainLiteralAt(self.program, other, common), self.flags) orelse {
                        complete = false;
                        break;
                    };
                }
                if (complete) {
                    self.program.code.items[split_index].op = .start_split;
                    self.program.code.items[split_index].extra = left_mask;
                    self.program.code.items[split_index].value = right_mask;
                }
            };
            self.program.code.items[jumps[branch_index]].left = finish;
        }
        return true;
    }

    fn node(self: *Compiler, index: u32) CompileError!void {
        switch (self.program.nodes.items[index]) {
            .empty => {},
            .literal => |value| {
                _ = try self.emit(.{ .op = .literal, .value = value, .extra = @intCast(self.flags & 0xffff) });
            },
            .dot => {
                _ = try self.emit(.{ .op = .dot, .extra = @intCast(self.flags & 0xffff) });
            },
            .class => |value| {
                _ = try self.emit(.{ .op = .class, .left = value, .extra = @intCast(self.flags & 0xffff) });
            },
            .begin => {
                _ = try self.emit(.{ .op = .begin, .extra = @intCast(self.flags & 0xffff) });
            },
            .end => {
                _ = try self.emit(.{ .op = .end, .extra = @intCast(self.flags & 0xffff) });
            },
            .absolute_begin => {
                _ = try self.emit(.{ .op = .absolute_begin });
            },
            .absolute_end => {
                _ = try self.emit(.{ .op = .absolute_end });
            },
            .boundary => |want| {
                _ = try self.emit(.{ .op = .boundary, .value = if (want) 1 else 0, .extra = @intCast(self.flags & 0xffff) });
            },
            .sequence => |pair| {
                try self.node(pair.left);
                try self.node(pair.right);
            },
            .alternative => |pair| {
                const first_node = self.program.nodes.items[pair.left];
                const second_node = self.program.nodes.items[pair.right];
                const boundary_value: ?bool = switch (first_node) { .boundary => |value| value, else => switch (second_node) { .boundary => |value| value, else => null } };
                const peek_value: ?Look = switch (first_node) { .look => |value| value, else => switch (second_node) { .look => |value| value, else => null } };
                if (boundary_value != null and peek_value != null and !capturesIn(self.program, peek_value.?.child) and fixedWidth(self.program, peek_value.?.child) == 1 and isAtom(self.program, peek_value.?.child)) {
                    const peek = peek_value.?;
                    _ = try self.emit(.{ .op = .boundary_peek, .left = peek.child, .extra = @intCast(self.flags & 0xffff), .value = @as(u8, if (boundary_value.?) 1 else 0) | @as(u8, if (peek.positive) 2 else 0) | @as(u8, if (peek.behind) 4 else 0) });
                    return;
                }
                if (try self.tryLiteralBranches(index)) return;
                const split = try self.emit(.{ .op = .split });
                const first: u32 = @intCast(self.program.code.items.len);
                try self.node(pair.left);
                const jump = try self.emit(.{ .op = .jump });
                const second: u32 = @intCast(self.program.code.items.len);
                try self.node(pair.right);
                const finish: u32 = @intCast(self.program.code.items.len);
                self.program.code.items[split].left = first;
                self.program.code.items[split].right = second;
                if (literalPrefixMask(self.program, pair.left, self.flags)) |mask| {
                    self.program.code.items[split].op = .start_split;
                    self.program.code.items[split].extra = mask;
                    self.program.code.items[split].value = literalPrefixMask(self.program, pair.right, self.flags) orelse std.math.maxInt(u32);
                }
                self.program.code.items[jump].left = finish;
            },
            .repeat => |repeat| {
                var compact = true;
                self.emitRun(repeat) catch |err| {
                    if (err != error.UnsupportedRepeat or repeat.minimum > 128 or (repeat.maximum != unbounded and repeat.maximum > 256)) return err;
                    compact = false;
                };
                if (compact) return;
                if (repeat.possessive) _ = try self.emit(.{ .op = .atomic_begin });
                for (0..repeat.minimum) |_| try self.emitRepeatChild(repeat.child, repeat.possessive);
                if (repeat.maximum == unbounded) {
                    const guarded = canBeEmpty(self.program, repeat.child);
                    const split = try self.emit(.{ .op = .split });
                    const body: u32 = @intCast(self.program.code.items.len);
                    try self.emitRepeatChild(repeat.child, repeat.possessive);
                    _ = try self.emit(.{ .op = .jump, .left = split });
                    const finish: u32 = @intCast(self.program.code.items.len);
                    self.program.code.items[split].left = if (repeat.lazy) finish else body;
                    self.program.code.items[split].right = if (repeat.lazy) body else finish;
                    if (guarded) {
                        self.program.code.items[split].value = finish;
                        self.program.nullable_loops = true;
                    }
                } else {
                    for (0..repeat.maximum - repeat.minimum) |_| {
                        const split = try self.emit(.{ .op = .split });
                        const body: u32 = @intCast(self.program.code.items.len);
                        try self.emitRepeatChild(repeat.child, repeat.possessive);
                        const finish: u32 = @intCast(self.program.code.items.len);
                        self.program.code.items[split].left = if (repeat.lazy) finish else body;
                        self.program.code.items[split].right = if (repeat.lazy) body else finish;
                    }
                }
                if (repeat.possessive) _ = try self.emit(.{ .op = .atomic_end });
            },
            .group => |group| {
                _ = try self.emit(.{ .op = .save_begin, .left = group.number });
                try self.node(group.child);
                _ = try self.emit(.{ .op = .save_end, .left = group.number });
            },
            .backref => |number| {
                _ = try self.emit(.{ .op = .backref, .left = number, .extra = @intCast(self.flags & 0xffff) });
            },
            .conditional => |conditional| {
                const branch = try self.emit(.{ .op = .conditional, .value = @intCast(conditional.number) });
                const yes: u32 = @intCast(self.program.code.items.len);
                try self.node(conditional.yes);
                const jump = try self.emit(.{ .op = .jump });
                const no: u32 = @intCast(self.program.code.items.len);
                try self.node(conditional.no);
                const finish: u32 = @intCast(self.program.code.items.len);
                self.program.code.items[branch].left = yes;
                self.program.code.items[branch].right = no;
                self.program.code.items[jump].left = finish;
            },
            .atomic => |child| {
                _ = try self.emit(.{ .op = .atomic_begin });
                try self.node(child);
                _ = try self.emit(.{ .op = .atomic_end });
            },
            .look => |look| {
                if (!capturesIn(self.program, look.child) and fixedWidth(self.program, look.child) == 1 and isAtom(self.program, look.child)) {
                    _ = try self.emit(.{ .op = .peek, .left = look.child, .extra = @intCast(self.flags & 0xffff), .value = @as(u8, if (look.positive) 1 else 0) | @as(u8, if (look.behind) 2 else 0) });
                    return;
                }
                if (!capturesIn(self.program, look.child) and isLiteralText(self.program, look.child)) {
                    _ = try self.emit(.{ .op = .peek_text, .left = look.child, .right = look.width, .extra = @intCast(self.flags & 0xffff), .value = @as(u8, if (look.positive) 1 else 0) | @as(u8, if (look.behind) 2 else 0) });
                    return;
                }
                if (!look.behind and !capturesIn(self.program, look.child)) switch (self.program.nodes.items[look.child]) {
                    .sequence => |pair| switch (self.program.nodes.items[pair.left]) {
                        .repeat => |repeat| {
                            var flat = Flat{ .layouts = &.{} };
                            if (!repeat.possessive and flatten(self.program, repeat.child, self.flags, 0, &flat) == 1 and flat.layout_count == 0 and isAtom(self.program, pair.right) and self.program.runs.items.len < std.math.maxInt(u32)) {
                                const run_index: u32 = @intCast(self.program.runs.items.len);
                                try self.program.runs.append(self.program.arena.allocator(), .{ .atom = flat.atom.?, .flags = flat.flags, .width = 1, .minimum = repeat.minimum, .maximum = repeat.maximum, .lazy = repeat.lazy, .possessive = false, .layout_start = 0, .layout_count = 0 });
                                _ = try self.emit(.{ .op = .peek_run, .left = run_index, .right = pair.right, .extra = @intCast(self.flags & 0xffff), .value = if (look.positive) 1 else 0 });
                                return;
                            }
                        },
                        else => {},
                    },
                    else => {},
                };
                const instruction = try self.emit(.{ .op = .look, .extra = look.width, .value = @as(u8, if (look.positive) 1 else 0) | @as(u8, if (look.behind) 2 else 0) });
                const entry: u32 = @intCast(self.program.code.items.len);
                try self.node(look.child);
                _ = try self.emit(.{ .op = .accept });
                const finish: u32 = @intCast(self.program.code.items.len);
                self.program.code.items[instruction].left = entry;
                self.program.code.items[instruction].right = finish;
            },
            .scoped => |scoped| {
                const previous = self.flags;
                self.flags = scoped.flags;
                self.node(scoped.child) catch |err| {
                    self.flags = previous;
                    return err;
                };
                self.flags = previous;
            },
        }
    }
};

fn addLiteralStarts(starts: *[256]u8, value: u32, flags: u32) void {
    if (flags & 2 == 0) {
        if (value < 256) starts[value] = 1;
        return;
    }
    for (0..256) |raw| {
        if (equal(value, @intCast(raw), flags)) starts[raw] = 1;
    }
}

fn addStarts(program: *const Program, index: u32, starts: *[256]u8, flags: u32) bool {
    return switch (program.nodes.items[index]) {
        .empty, .begin, .end, .absolute_begin, .absolute_end, .boundary => true,
        .literal => |value| blk: {
            addLiteralStarts(starts, value, flags);
            break :blk false;
        },
        .dot => blk: {
            for (0..256) |raw| {
                if (flags & 16 != 0 or raw != '\n') starts[raw] = 1;
            }
            break :blk false;
        },
        .class => |value| blk: {
            for (0..256) |raw| {
                if (classMatch(program, &program.classes.items[value], @intCast(raw), flags)) starts[raw] = 1;
            }
            break :blk false;
        },
        .alternative => |pair| blk: {
            const left_empty = addStarts(program, pair.left, starts, flags);
            const right_empty = addStarts(program, pair.right, starts, flags);
            break :blk left_empty or right_empty;
        },
        .sequence => |pair| blk: {
            const left_empty = addStarts(program, pair.left, starts, flags);
            if (!left_empty) break :blk false;
            break :blk addStarts(program, pair.right, starts, flags);
        },
        .repeat => |repeat| blk: {
            const child_empty = addStarts(program, repeat.child, starts, flags);
            break :blk repeat.minimum == 0 or child_empty;
        },
        .group => |group| addStarts(program, group.child, starts, flags),
        .backref => true,
        .conditional => |conditional| blk: {
            const yes = addStarts(program, conditional.yes, starts, flags);
            const no = addStarts(program, conditional.no, starts, flags);
            break :blk yes or no;
        },
        .atomic => |child| addStarts(program, child, starts, flags),
        .look => true,
        .scoped => |scoped| addStarts(program, scoped.child, starts, scoped.flags),
    };
}

fn scopedCategoryPrefix(program: *const Program, index: u32, switched: bool) ?u32 {
    return switch (program.nodes.items[index]) {
        .class => |class| if (switched and program.classes.items[class].categories != 0) class else null,
        .sequence => |pair| scopedCategoryPrefix(program, pair.left, switched),
        .group => |group| scopedCategoryPrefix(program, group.child, switched),
        .scoped => |scoped| scopedCategoryPrefix(program, scoped.child, switched or scoped.flags & (4 | 32 | 256) != program.flags & (4 | 32 | 256)),
        else => null,
    };
}

const QuickPrefix = struct {
    empty: bool = false,
    first: [256]u8 = [_]u8{0} ** 256,
    single: [256]u8 = [_]u8{0} ** 256,
    second: [256]u8 = [_]u8{0} ** 256,
};

fn hasSecond(seconds: *const [32]u8, value: usize) bool {
    return seconds[value >> 3] & (@as(u8, 1) << @intCast(value & 7)) != 0;
}
fn mergeQuickPrefix(target: *QuickPrefix, other: *const QuickPrefix) void {
    target.empty = target.empty or other.empty;
    for (0..256) |index| {
        target.first[index] |= other.first[index];
        target.single[index] |= other.single[index];
        target.second[index] |= other.second[index];
    }
}

fn joinQuickPrefix(left: *const QuickPrefix, right: *const QuickPrefix) QuickPrefix {
    var result = QuickPrefix{ .empty = left.empty and right.empty };
    var left_single = false;
    for (left.single) |value| left_single = left_single or value != 0;
    for (0..256) |index| {
        result.first[index] = left.first[index] | (if (left.empty) right.first[index] else 0);
        result.single[index] = (if (right.empty) left.single[index] else 0) | (if (left.empty) right.single[index] else 0);
        result.second[index] = left.second[index] | (if (left.empty) right.second[index] else 0) | (if (left_single) right.first[index] else 0);
    }
    return result;
}

fn quickPrefix(program: *const Program, index: u32, flags: u32) QuickPrefix {
    return switch (program.nodes.items[index]) {
        .empty, .begin, .end, .absolute_begin, .absolute_end, .boundary => QuickPrefix{ .empty = true },
        .literal => |value| blk: {
            var result = QuickPrefix{};
            addLiteralStarts(&result.first, value, flags);
            result.single = result.first;
            break :blk result;
        },
        .dot => blk: {
            var result = QuickPrefix{};
            for (0..256) |raw| if (flags & 16 != 0 or raw != '\n') {
                result.first[raw] = 1;
                result.single[raw] = 1;
            };
            break :blk result;
        },
        .class => |value| blk: {
            var result = QuickPrefix{};
            for (0..256) |raw| if (classMatch(program, &program.classes.items[value], @intCast(raw), flags)) {
                result.first[raw] = 1;
                result.single[raw] = 1;
            };
            break :blk result;
        },
        .alternative => |pair| blk: {
            var result = quickPrefix(program, pair.left, flags);
            const right = quickPrefix(program, pair.right, flags);
            mergeQuickPrefix(&result, &right);
            break :blk result;
        },
        .sequence => |pair| blk: {
            const left = quickPrefix(program, pair.left, flags);
            const right = quickPrefix(program, pair.right, flags);
            break :blk joinQuickPrefix(&left, &right);
        },
        .repeat => |repeat| blk: {
            const child = quickPrefix(program, repeat.child, flags);
            var current = QuickPrefix{ .empty = true };
            for (0..@min(repeat.minimum, 2)) |_| current = joinQuickPrefix(&current, &child);
            var result = current;
            if (repeat.maximum > repeat.minimum) {
                current = joinQuickPrefix(&current, &child);
                mergeQuickPrefix(&result, &current);
                if (repeat.maximum == unbounded or repeat.maximum > repeat.minimum + 1) {
                    current = joinQuickPrefix(&current, &child);
                    mergeQuickPrefix(&result, &current);
                }
            }
            break :blk result;
        },
        .group => |group| quickPrefix(program, group.child, flags),
        .backref => blk: {
            var result = QuickPrefix{ .empty = true };
            @memset(&result.first, 1);
            @memset(&result.single, 1);
            @memset(&result.second, 1);
            break :blk result;
        },
        .conditional => |conditional| blk: {
            var result = quickPrefix(program, conditional.yes, flags);
            const no = quickPrefix(program, conditional.no, flags);
            mergeQuickPrefix(&result, &no);
            break :blk result;
        },
        .atomic => |child| quickPrefix(program, child, flags),
        .look => QuickPrefix{ .empty = true },
        .scoped => |scoped| quickPrefix(program, scoped.child, scoped.flags),
    };
}

const GuardUndo = struct { pc: u32, previous: isize };
const State = struct { pos: usize, run_limit: usize = unbounded, run_max: usize = 0, pc: u32, atomic: usize };

fn growAtomicStack(stack: *[]usize, heap: *?[]usize, used: usize) bool {
    const capacity = std.math.mul(usize, stack.*.len, 2) catch return false;
    const grown = std.heap.c_allocator.alloc(usize, capacity) catch return false;
    @memcpy(grown[0..used], stack.*[0..used]);
    if (heap.*) |previous| std.heap.c_allocator.free(previous);
    heap.* = grown;
    stack.* = grown;
    return true;
}

fn runBytecode(program: *const Program, text: Subject, endpos: usize, start: usize, full: bool, nonempty: bool) isize {
    var stack_local: [max_stack]State = undefined;
    var stack: []State = &stack_local;
    var stack_heap: ?[]State = null;
    defer if (stack_heap) |items| std.heap.c_allocator.free(items);
    var marks_local: [max_stack]usize = undefined;
    var guard_marks: []usize = &marks_local;
    var marks_heap: ?[]usize = null;
    defer if (marks_heap) |items| std.heap.c_allocator.free(items);
    var stack_count: usize = 0;
    var atomic_local: [max_stack]usize = undefined;
    var atomic_stack: []usize = &atomic_local;
    var atomic_heap: ?[]usize = null;
    defer if (atomic_heap) |items| std.heap.c_allocator.free(items);
    var atomic_depth: usize = 0;
    var guards_local: [max_guards]isize = undefined;
    var guards: []isize = &.{};
    var guards_heap: ?[]isize = null;
    defer if (guards_heap) |items| std.heap.c_allocator.free(items);
    var guard_local: [max_stack]GuardUndo = undefined;
    var guard_undo: []GuardUndo = &guard_local;
    var guard_heap: ?[]GuardUndo = null;
    defer if (guard_heap) |items| std.heap.c_allocator.free(items);
    var guard_count: usize = 0;
    if (program.nullable_loops) {
        if (program.code.items.len <= guards_local.len) guards = guards_local[0..program.code.items.len] else {
            guards_heap = std.heap.c_allocator.alloc(isize, program.code.items.len) catch return -2;
            guards = guards_heap.?;
        }
        @memset(guards, -1);
    }
    var pc: u32 = 0;
    var pos = start;
    var resumed_limit: usize = unbounded;
    var resumed_max: usize = 0;
    while (true) {
        const instruction = program.code.items[pc];
        switch (instruction.op) {
            .literal => if (pos < endpos and equal(instruction.value, text.at(pos), instruction.extra)) {
                pos += 1;
                pc += 1;
                continue;
            },
            .dot => if (pos < endpos and (instruction.extra & 16 != 0 or text.at(pos) != '\n')) {
                pos += 1;
                pc += 1;
                continue;
            },
            .class => if (pos < endpos and classMatch(program, &program.classes.items[instruction.left], text.at(pos), instruction.extra)) {
                pos += 1;
                pc += 1;
                continue;
            },
            .begin => if (pos == 0 or (instruction.extra & 8 != 0 and pos > 0 and text.at(pos - 1) == '\n')) {
                pc += 1;
                continue;
            },
            .end => if (pos == endpos or (pos + 1 == endpos and text.at(pos) == '\n') or (instruction.extra & 8 != 0 and pos < endpos and text.at(pos) == '\n')) {
                pc += 1;
                continue;
            },
            .absolute_begin => if (pos == 0) {
                pc += 1;
                continue;
            },
            .absolute_end => if (pos == endpos) {
                pc += 1;
                continue;
            },
            .boundary => {
                const left = pos > 0 and word(text.at(pos - 1), instruction.extra);
                const right = pos < endpos and word(text.at(pos), instruction.extra);
                if ((left != right) == (instruction.value != 0)) {
                    pc += 1;
                    continue;
                }
            },
            .boundary_peek => {
                const left_word = pos > 0 and word(text.at(pos - 1), instruction.extra);
                const right_word = pos < endpos and word(text.at(pos), instruction.extra);
                const boundary_found = (left_word != right_word) == (instruction.value & 1 != 0);
                const behind = instruction.value & 4 != 0;
                const peek_found = if (behind) pos > 0 and atomMatch(program, instruction.left, text.at(pos - 1), instruction.extra) else pos < endpos and atomMatch(program, instruction.left, text.at(pos), instruction.extra);
                if (boundary_found or peek_found == (instruction.value & 2 != 0)) {
                    pc += 1;
                    continue;
                }
            },
            .split => {
                if (stack_count >= stack.len) {
                    const capacity = std.math.mul(usize, stack.len, 2) catch return -2;
                    const grown = std.heap.c_allocator.alloc(State, capacity) catch return -2;
                    @memcpy(grown[0..stack_count], stack[0..stack_count]);
                    if (stack_heap) |items| std.heap.c_allocator.free(items);
                    stack_heap = grown;
                    stack = grown;
                    if (program.nullable_loops) {
                        const grown_marks = std.heap.c_allocator.alloc(usize, capacity) catch return -2;
                        @memcpy(grown_marks[0..stack_count], guard_marks[0..stack_count]);
                        if (marks_heap) |items| std.heap.c_allocator.free(items);
                        marks_heap = grown_marks;
                        guard_marks = grown_marks;
                    }
                }
                if (instruction.value != 0) {
                    if (guard_count >= guard_undo.len) {
                        const capacity = std.math.mul(usize, guard_undo.len, 2) catch return -2;
                        const grown = std.heap.c_allocator.alloc(GuardUndo, capacity) catch return -2;
                        @memcpy(grown[0..guard_count], guard_undo[0..guard_count]);
                        if (guard_heap) |items| std.heap.c_allocator.free(items);
                        guard_heap = grown;
                        guard_undo = grown;
                    }
                    guard_undo[guard_count] = .{ .pc = pc, .previous = guards[pc] };
                    guard_count += 1;
                    guards[pc] = @intCast(pos);
                }
                if (program.nullable_loops) guard_marks[stack_count] = guard_count;
                stack[stack_count] = .{ .pc = instruction.right, .pos = pos, .atomic = atomic_depth };
                stack_count += 1;
                pc = instruction.left;
                continue;
            },
            .start_split => {
                if (pos >= endpos) {
                    pc = instruction.right;
                    continue;
                }
                const bit = @as(u32, 1) << @intCast(text.at(pos) & 31);
                if (instruction.extra & bit == 0) {
                    pc = instruction.right;
                    continue;
                }
                if (instruction.value & bit == 0) {
                    pc = instruction.left;
                    continue;
                }
                if (stack_count >= stack.len) {
                    const capacity = std.math.mul(usize, stack.len, 2) catch return -2;
                    const grown = std.heap.c_allocator.alloc(State, capacity) catch return -2;
                    @memcpy(grown[0..stack_count], stack[0..stack_count]);
                    if (stack_heap) |items| std.heap.c_allocator.free(items);
                    stack_heap = grown;
                    stack = grown;
                    if (program.nullable_loops) {
                        const grown_marks = std.heap.c_allocator.alloc(usize, capacity) catch return -2;
                        @memcpy(grown_marks[0..stack_count], guard_marks[0..stack_count]);
                        if (marks_heap) |items| std.heap.c_allocator.free(items);
                        marks_heap = grown_marks;
                        guard_marks = grown_marks;
                    }
                }
                if (program.nullable_loops) guard_marks[stack_count] = guard_count;
                stack[stack_count] = .{ .pc = instruction.right, .pos = pos, .atomic = atomic_depth };
                stack_count += 1;
                pc = instruction.left;
                continue;
            },
            .jump => {
                const target = program.code.items[instruction.left];
                if (target.op == .split and target.value != 0 and guards[instruction.left] == @as(isize, @intCast(pos))) {
                    pc = @intCast(target.value);
                    continue;
                }
                pc = instruction.left;
                continue;
            },
            .save_begin, .save_end => {
                pc += 1;
                continue;
            },
            .run => blk: {
                const run = program.runs.items[instruction.value];
                const room = endpos - pos;
                const allowed = if (run.maximum == unbounded) room / run.width else @min(run.maximum, room / run.width);
                var available = resumed_max;
                if (resumed_limit == unbounded) {
                    available = 0;
                    const maximum = allowed * run.width;
                    available = runLength(program, run, text, pos, maximum);
                    available /= run.width;
                }
                if (available < run.minimum) break :blk;
                const chosen = if (resumed_limit != unbounded) resumed_limit else if (run.lazy) run.minimum else available;
                resumed_limit = unbounded;
                resumed_max = 0;
                if (!run.possessive) {
                    const alternate: ?usize = if (run.lazy) (if (chosen < available) chosen + 1 else null) else if (chosen > run.minimum) chosen - 1 else null;
                    if (alternate) |limit| {
                        if (stack_count >= stack.len) {
                            const capacity = std.math.mul(usize, stack.len, 2) catch return -2;
                            const grown = std.heap.c_allocator.alloc(State, capacity) catch return -2;
                            @memcpy(grown[0..stack_count], stack[0..stack_count]);
                            if (stack_heap) |items| std.heap.c_allocator.free(items);
                            stack_heap = grown;
                            stack = grown;
                            if (program.nullable_loops) {
                                const grown_marks = std.heap.c_allocator.alloc(usize, capacity) catch return -2;
                                @memcpy(grown_marks[0..stack_count], guard_marks[0..stack_count]);
                                if (marks_heap) |items| std.heap.c_allocator.free(items);
                                marks_heap = grown_marks;
                                guard_marks = grown_marks;
                            }
                        }
                        if (program.nullable_loops) guard_marks[stack_count] = guard_count;
                        stack[stack_count] = .{ .pc = pc, .pos = pos, .atomic = atomic_depth, .run_limit = limit, .run_max = available };
                        stack_count += 1;
                    }
                }
                pos += chosen * run.width;
                pc += 1;
                continue;
            },
            .lazy_dot => blk: {
                const run = program.runs.items[instruction.value];
                const room = endpos - pos;
                const allowed = if (run.maximum == unbounded) room else @min(run.maximum, room);
                const from = if (resumed_limit != unbounded) resumed_limit else run.minimum;
                resumed_limit = unbounded;
                resumed_max = 0;
                if (from > allowed) break :blk;
                const want = instruction.extra;
                const candidate: ?usize = if (text.kind == 1 and want < 256)
                    if (pos + from < endpos) std.mem.indexOfScalarPos(u8, text.data[0..@min(endpos, pos + allowed +| 1)], pos + from, @intCast(want)) else null
                else blk_find: {
                    var at = pos + from;
                    const finish = @min(endpos, pos + allowed +| 1);
                    while (at < finish) : (at += 1) {
                        if (text.at(at) == want) break :blk_find at;
                    }
                    break :blk_find null;
                };
                const found = candidate orelse break :blk;
                const chosen = found - pos;
                if (chosen < allowed) {
                    if (stack_count >= stack.len) {
                        const capacity = std.math.mul(usize, stack.len, 2) catch return -2;
                        const grown = std.heap.c_allocator.alloc(State, capacity) catch return -2;
                        @memcpy(grown[0..stack_count], stack[0..stack_count]);
                        if (stack_heap) |items| std.heap.c_allocator.free(items);
                        stack_heap = grown;
                        stack = grown;
                        if (program.nullable_loops) {
                            const grown_marks = std.heap.c_allocator.alloc(usize, capacity) catch return -2;
                            @memcpy(grown_marks[0..stack_count], guard_marks[0..stack_count]);
                            if (marks_heap) |items| std.heap.c_allocator.free(items);
                            marks_heap = grown_marks;
                            guard_marks = grown_marks;
                        }
                    }
                    if (program.nullable_loops) guard_marks[stack_count] = guard_count;
                    stack[stack_count] = .{ .pc = pc, .pos = pos, .atomic = atomic_depth, .run_limit = chosen + 1, .run_max = allowed };
                    stack_count += 1;
                }
                pos += chosen;
                pc += 1;
                continue;
            },
            .peek => {
                const behind = instruction.value & 2 != 0;
                const found = if (behind) pos > 0 and atomMatch(program, instruction.left, text.at(pos - 1), instruction.extra) else pos < endpos and atomMatch(program, instruction.left, text.at(pos), instruction.extra);
                if (found == (instruction.value & 1 != 0)) {
                    pc += 1;
                    continue;
                }
            },
            .peek_text => {
                const behind = instruction.value & 2 != 0;
                var at = if (behind) (if (pos >= instruction.right) pos - instruction.right else endpos) else pos;
                const found = (!behind or pos >= instruction.right) and literalTextMatches(program, instruction.left, text, if (behind) pos else endpos, &at, instruction.extra);
                if (found == (instruction.value & 1 != 0)) {
                    pc += 1;
                    continue;
                }
            },
            .peek_run => {
                const run = program.runs.items[instruction.left];
                const room = endpos - pos;
                const maximum = if (run.maximum == unbounded) room else @min(run.maximum, room);
                const available = runLength(program, run, text, pos, maximum);
                var found = false;
                if (available >= run.minimum) {
                    var count = run.minimum;
                    while (count <= available) : (count += 1) {
                        if (pos + count < endpos and atomMatch(program, instruction.right, text.at(pos + count), instruction.extra)) {
                            found = true;
                            break;
                        }
                    }
                }
                if (found == (instruction.value != 0)) {
                    pc += 1;
                    continue;
                }
            },
            .peek_even => {
                var even = true;
                var at = pos;
                while (at < endpos) : (at += 1) {
                    if (text.at(at) == instruction.extra) even = !even;
                }
                if (even == (instruction.value & 1 != 0)) {
                    pc = instruction.right;
                    continue;
                }
            },
            .backref, .conditional, .look => return -2,
            .atomic_begin => {
                if (atomic_depth >= atomic_stack.len and !growAtomicStack(&atomic_stack, &atomic_heap, atomic_depth)) return -2;
                atomic_stack[atomic_depth] = stack_count;
                atomic_depth += 1;
                pc += 1;
                continue;
            },
            .atomic_end => {
                if (atomic_depth == 0) return -2;
                atomic_depth -= 1;
                stack_count = atomic_stack[atomic_depth];
                pc += 1;
                continue;
            },
            .accept => if ((!full or pos == endpos) and !(nonempty and pos == start)) return @intCast(pos),
        }
        if (stack_count == 0) return -1;
        stack_count -= 1;
        const state = stack[stack_count];
        while (program.nullable_loops and guard_count > guard_marks[stack_count]) {
            guard_count -= 1;
            const item = guard_undo[guard_count];
            guards[item.pc] = item.previous;
        }
        pc = state.pc;
        pos = state.pos;
        atomic_depth = state.atomic;
        resumed_limit = state.run_limit;
        resumed_max = state.run_max;
    }
}

const CaptureState = struct { pos: usize, undo: usize, run_limit: usize = unbounded, run_max: usize = 0, pc: u32, atomic: usize };
const Undo = struct { previous: isize, slot: usize, last: isize };
const no_capture_slot = std.math.maxInt(usize);

const CaptureScratch = struct {
    local: [inline_capture_words]isize = undefined,
    heap: ?[]isize = null,
    length: usize = 0,

    fn init(self: *CaptureScratch, length: usize) bool {
        self.length = length;
        if (length > self.local.len) {
            self.heap = std.heap.c_allocator.alloc(isize, length) catch return false;
        }
        return true;
    }

    fn items(self: *CaptureScratch) []isize {
        return if (self.heap) |values| values else self.local[0..self.length];
    }

    fn deinit(self: *CaptureScratch) void {
        if (self.heap) |values| std.heap.c_allocator.free(values);
        self.heap = null;
    }
};

fn captureWordCount(program: *const Program) ?usize {
    return std.math.mul(usize, @as(usize, program.groups), 2) catch null;
}

fn captureSlot(number: GroupId, ending: bool) ?usize {
    if (number == 0) return null;
    const base = std.math.mul(usize, @as(usize, number - 1), 2) catch return null;
    return std.math.add(usize, base, @intFromBool(ending)) catch null;
}

fn runCapturedAt(program: *const Program, text: Subject, endpos: usize, logical_endpos: usize, start: usize, entry: u32, full: bool, captures: []isize, last: *isize, reset: bool, nonempty: bool) isize {
    const capture_words = captureWordCount(program) orelse return -2;
    if (captures.len < capture_words) return -2;
    var stack_local: [max_stack]CaptureState = undefined;
    var stack: []CaptureState = &stack_local;
    var stack_heap: ?[]CaptureState = null;
    defer if (stack_heap) |items| std.heap.c_allocator.free(items);
    var marks_local: [max_stack]usize = undefined;
    var guard_marks: []usize = &marks_local;
    var marks_heap: ?[]usize = null;
    defer if (marks_heap) |items| std.heap.c_allocator.free(items);
    var stack_count: usize = 0;
    var undo_local: [max_undo]Undo = undefined;
    var undo: []Undo = &undo_local;
    var undo_heap: ?[]Undo = null;
    defer if (undo_heap) |items| std.heap.c_allocator.free(items);
    var undo_count: usize = 0;
    var atomic_local: [max_stack]usize = undefined;
    var atomic_stack: []usize = &atomic_local;
    var atomic_heap: ?[]usize = null;
    defer if (atomic_heap) |items| std.heap.c_allocator.free(items);
    var atomic_depth: usize = 0;
    var guards_local: [max_guards]isize = undefined;
    var guards: []isize = &.{};
    var guards_heap: ?[]isize = null;
    defer if (guards_heap) |items| std.heap.c_allocator.free(items);
    var guard_local: [max_stack]GuardUndo = undefined;
    var guard_undo: []GuardUndo = &guard_local;
    var guard_heap: ?[]GuardUndo = null;
    defer if (guard_heap) |items| std.heap.c_allocator.free(items);
    var guard_count: usize = 0;
    if (program.nullable_loops) {
        if (program.code.items.len <= guards_local.len) guards = guards_local[0..program.code.items.len] else {
            guards_heap = std.heap.c_allocator.alloc(isize, program.code.items.len) catch return -2;
            guards = guards_heap.?;
        }
        @memset(guards, -1);
    }
    if (reset) {
        @memset(captures[0..capture_words], -1);
        last.* = -1;
    }
    var pc: u32 = entry;
    var pos = start;
    var resumed_limit: usize = unbounded;
    var resumed_max: usize = 0;
    while (true) {
        const instruction = program.code.items[pc];
        switch (instruction.op) {
            .literal => if (pos < endpos and equal(instruction.value, text.at(pos), instruction.extra)) {
                pos += 1;
                pc += 1;
                continue;
            },
            .dot => if (pos < endpos and (instruction.extra & 16 != 0 or text.at(pos) != '\n')) {
                pos += 1;
                pc += 1;
                continue;
            },
            .class => if (pos < endpos and classMatch(program, &program.classes.items[instruction.left], text.at(pos), instruction.extra)) {
                pos += 1;
                pc += 1;
                continue;
            },
            .begin => if (pos == 0 or (instruction.extra & 8 != 0 and pos > 0 and text.at(pos - 1) == '\n')) {
                pc += 1;
                continue;
            },
            .end => if (pos == logical_endpos or
                (pos + 1 == logical_endpos and pos < text.length and text.at(pos) == '\n') or
                (instruction.extra & 8 != 0 and pos < text.length and text.at(pos) == '\n')) {
                pc += 1;
                continue;
            },
            .absolute_begin => if (pos == 0) {
                pc += 1;
                continue;
            },
            .absolute_end => if (pos == logical_endpos) {
                pc += 1;
                continue;
            },
            .boundary => {
                const left = pos > 0 and word(text.at(pos - 1), instruction.extra);
                const right = pos < logical_endpos and word(text.at(pos), instruction.extra);
                if ((left != right) == (instruction.value != 0)) {
                    pc += 1;
                    continue;
                }
            },
            .boundary_peek => {
                const left_word = pos > 0 and word(text.at(pos - 1), instruction.extra);
                const right_word = pos < logical_endpos and word(text.at(pos), instruction.extra);
                const boundary_found = (left_word != right_word) == (instruction.value & 1 != 0);
                const behind = instruction.value & 4 != 0;
                const peek_found = if (behind)
                    pos <= logical_endpos and pos > 0 and
                        atomMatch(program, instruction.left, text.at(pos - 1), instruction.extra)
                else pos < logical_endpos and
                    atomMatch(program, instruction.left, text.at(pos), instruction.extra);
                if (boundary_found or peek_found == (instruction.value & 2 != 0)) {
                    pc += 1;
                    continue;
                }
            },
            .split => {
                if (stack_count >= stack.len) {
                    const capacity = std.math.mul(usize, stack.len, 2) catch return -2;
                    const grown = std.heap.c_allocator.alloc(CaptureState, capacity) catch return -2;
                    @memcpy(grown[0..stack_count], stack[0..stack_count]);
                    if (stack_heap) |items| std.heap.c_allocator.free(items);
                    stack_heap = grown;
                    stack = grown;
                    if (program.nullable_loops) {
                        const grown_marks = std.heap.c_allocator.alloc(usize, capacity) catch return -2;
                        @memcpy(grown_marks[0..stack_count], guard_marks[0..stack_count]);
                        if (marks_heap) |items| std.heap.c_allocator.free(items);
                        marks_heap = grown_marks;
                        guard_marks = grown_marks;
                    }
                }
                if (instruction.value != 0) {
                    if (guard_count >= guard_undo.len) {
                        const capacity = std.math.mul(usize, guard_undo.len, 2) catch return -2;
                        const grown = std.heap.c_allocator.alloc(GuardUndo, capacity) catch return -2;
                        @memcpy(grown[0..guard_count], guard_undo[0..guard_count]);
                        if (guard_heap) |items| std.heap.c_allocator.free(items);
                        guard_heap = grown;
                        guard_undo = grown;
                    }
                    guard_undo[guard_count] = .{ .pc = pc, .previous = guards[pc] };
                    guard_count += 1;
                    guards[pc] = @intCast(pos);
                }
                if (program.nullable_loops) guard_marks[stack_count] = guard_count;
                stack[stack_count] = .{ .pc = instruction.right, .pos = pos, .undo = undo_count, .atomic = atomic_depth };
                stack_count += 1;
                pc = instruction.left;
                continue;
            },
            .start_split => {
                if (pos >= endpos) {
                    pc = instruction.right;
                    continue;
                }
                const bit = @as(u32, 1) << @intCast(text.at(pos) & 31);
                if (instruction.extra & bit == 0) {
                    pc = instruction.right;
                    continue;
                }
                if (instruction.value & bit == 0) {
                    pc = instruction.left;
                    continue;
                }
                if (stack_count >= stack.len) {
                    const capacity = std.math.mul(usize, stack.len, 2) catch return -2;
                    const grown = std.heap.c_allocator.alloc(CaptureState, capacity) catch return -2;
                    @memcpy(grown[0..stack_count], stack[0..stack_count]);
                    if (stack_heap) |items| std.heap.c_allocator.free(items);
                    stack_heap = grown;
                    stack = grown;
                    if (program.nullable_loops) {
                        const grown_marks = std.heap.c_allocator.alloc(usize, capacity) catch return -2;
                        @memcpy(grown_marks[0..stack_count], guard_marks[0..stack_count]);
                        if (marks_heap) |items| std.heap.c_allocator.free(items);
                        marks_heap = grown_marks;
                        guard_marks = grown_marks;
                    }
                }
                if (program.nullable_loops) guard_marks[stack_count] = guard_count;
                stack[stack_count] = .{ .pc = instruction.right, .pos = pos, .undo = undo_count, .atomic = atomic_depth };
                stack_count += 1;
                pc = instruction.left;
                continue;
            },
            .jump => {
                const target = program.code.items[instruction.left];
                if (target.op == .split and target.value != 0 and guards[instruction.left] == @as(isize, @intCast(pos))) {
                    pc = @intCast(target.value);
                    continue;
                }
                pc = instruction.left;
                continue;
            },
            .save_begin, .save_end => {
                if (instruction.left == 0 or instruction.left > program.groups) return -2;
                if (undo_count >= undo.len) {
                    const capacity = std.math.mul(usize, undo.len, 2) catch return -2;
                    const grown = std.heap.c_allocator.alloc(Undo, capacity) catch return -2;
                    @memcpy(grown[0..undo_count], undo[0..undo_count]);
                    if (undo_heap) |items| std.heap.c_allocator.free(items);
                    undo_heap = grown;
                    undo = grown;
                }
                const slot = captureSlot(instruction.left, instruction.op == .save_end) orelse return -2;
                if (slot >= capture_words) return -2;
                undo[undo_count] = .{ .slot = slot, .previous = captures[slot], .last = last.* };
                undo_count += 1;
                captures[slot] = @intCast(pos);
                if (instruction.op == .save_end) last.* = instruction.left;
                pc += 1;
                continue;
            },
            .backref => {
                if (instruction.left == 0 or instruction.left > program.groups) return -2;
                const base = captureSlot(instruction.left, false) orelse return -2;
                const finish_slot = std.math.add(usize, base, 1) catch return -2;
                if (finish_slot >= capture_words) return -2;
                const begin = captures[base];
                const finish = captures[finish_slot];
                if (begin >= 0 and finish >= begin) {
                    const width: usize = @intCast(finish - begin);
                    if (width <= endpos - pos) {
                        var matched = true;
                        for (0..width) |offset| {
                            if (!backrefEqual(text.at(@as(usize, @intCast(begin)) + offset), text.at(pos + offset), instruction.extra)) {
                                matched = false;
                                break;
                            }
                        }
                        if (matched) {
                            pos += width;
                            pc += 1;
                            continue;
                        }
                    }
                }
            },
            .conditional => {
                if (instruction.value == 0 or instruction.value > program.groups) return -2;
                const base = captureSlot(instruction.value, false) orelse return -2;
                const finish_slot = std.math.add(usize, base, 1) catch return -2;
                if (finish_slot >= capture_words) return -2;
                pc = if (captures[base] >= 0 and captures[finish_slot] >= captures[base]) instruction.left else instruction.right;
                continue;
            },
            .atomic_begin => {
                if (atomic_depth >= atomic_stack.len and !growAtomicStack(&atomic_stack, &atomic_heap, atomic_depth)) return -2;
                atomic_stack[atomic_depth] = stack_count;
                atomic_depth += 1;
                pc += 1;
                continue;
            },
            .atomic_end => {
                if (atomic_depth == 0) return -2;
                atomic_depth -= 1;
                stack_count = atomic_stack[atomic_depth];
                pc += 1;
                continue;
            },
            .look => {
                const behind = instruction.value & 2 != 0;
                const positive = instruction.value & 1 != 0;
                const begin: ?usize = if (behind) (if (pos > logical_endpos or pos < instruction.extra) null else pos - instruction.extra) else pos;
                var looked_scratch = CaptureScratch{};
                if (!looked_scratch.init(capture_words)) return -2;
                defer looked_scratch.deinit();
                const looked = looked_scratch.items();
                @memcpy(looked, captures[0..capture_words]);
                var look_last = last.*;
                const result = if (begin) |value| runCapturedAt(program, text, if (behind) pos else endpos, if (behind) pos else logical_endpos, value, instruction.left, behind, looked, &look_last, false, false) else -1;
                if (result == -2) return -2;
                const found = result >= 0;
                if (found == positive) {
                    if (positive) {
                        if (look_last != last.*) {
                            if (undo_count >= undo.len) {
                                const capacity = std.math.mul(usize, undo.len, 2) catch return -2;
                                const grown = std.heap.c_allocator.alloc(Undo, capacity) catch return -2;
                                @memcpy(grown[0..undo_count], undo[0..undo_count]);
                                if (undo_heap) |items| std.heap.c_allocator.free(items);
                                undo_heap = grown;
                                undo = grown;
                            }
                            undo[undo_count] = .{ .slot = no_capture_slot, .previous = 0, .last = last.* };
                            undo_count += 1;
                        }
                        for (0..capture_words) |slot| {
                            if (captures[slot] != looked[slot]) {
                                if (undo_count >= undo.len) {
                                    const capacity = std.math.mul(usize, undo.len, 2) catch return -2;
                                    const grown = std.heap.c_allocator.alloc(Undo, capacity) catch return -2;
                                    @memcpy(grown[0..undo_count], undo[0..undo_count]);
                                    if (undo_heap) |items| std.heap.c_allocator.free(items);
                                    undo_heap = grown;
                                    undo = grown;
                                }
                                undo[undo_count] = .{ .slot = slot, .previous = captures[slot], .last = last.* };
                                undo_count += 1;
                                captures[slot] = looked[slot];
                            }
                        }
                        last.* = look_last;
                    }
                    pc = instruction.right;
                    continue;
                }
            },
            .run => blk: {
                const run = program.runs.items[instruction.value];
                if (pos > logical_endpos) {
                    const repeated_motif = switch (program.nodes.items[run.atom]) {
                        .sequence, .repeat, .group, .atomic, .scoped => true,
                        else => false,
                    };
                    if (repeated_motif) {
                        if (run.minimum != 0) break :blk;
                        pc += 1;
                        continue;
                    }
                }
                if (pos > logical_endpos and run.layout_count == 0) break :blk;
                const room = endpos - pos;
                const allowed = if (run.maximum == unbounded) room / run.width else @min(run.maximum, room / run.width);
                var available = resumed_max;
                if (resumed_limit == unbounded) {
                    available = 0;
                    const maximum = allowed * run.width;
                    available = runLength(program, run, text, pos, maximum);
                    available /= run.width;
                }
                if (available < run.minimum) break :blk;
                const chosen = if (resumed_limit != unbounded) resumed_limit else if (run.lazy) run.minimum else available;
                resumed_limit = unbounded;
                resumed_max = 0;
                if (!run.possessive) {
                    const alternate: ?usize = if (run.lazy) (if (chosen < available) chosen + 1 else null) else if (chosen > run.minimum) chosen - 1 else null;
                    if (alternate) |limit| {
                        if (stack_count >= stack.len) {
                            const capacity = std.math.mul(usize, stack.len, 2) catch return -2;
                            const grown = std.heap.c_allocator.alloc(CaptureState, capacity) catch return -2;
                            @memcpy(grown[0..stack_count], stack[0..stack_count]);
                            if (stack_heap) |items| std.heap.c_allocator.free(items);
                            stack_heap = grown;
                            stack = grown;
                            if (program.nullable_loops) {
                                const grown_marks = std.heap.c_allocator.alloc(usize, capacity) catch return -2;
                                @memcpy(grown_marks[0..stack_count], guard_marks[0..stack_count]);
                                if (marks_heap) |items| std.heap.c_allocator.free(items);
                                marks_heap = grown_marks;
                                guard_marks = grown_marks;
                            }
                        }
                        if (program.nullable_loops) guard_marks[stack_count] = guard_count;
                        stack[stack_count] = .{ .pc = pc, .pos = pos, .undo = undo_count, .atomic = atomic_depth, .run_limit = limit, .run_max = available };
                        stack_count += 1;
                    }
                }
                if (chosen != 0 and run.layout_count != 0) {
                    const base = pos + (chosen - 1) * run.width;
                    const layout_end = std.math.add(usize, @as(usize, run.layout_start), @as(usize, run.layout_count)) catch return -2;
                    if (layout_end > program.layouts.items.len) return -2;
                    const layouts = program.layouts.items[run.layout_start..layout_end];
                    for (layouts) |layout| {
                        if (layout.number == 0 or layout.number > program.groups) return -2;
                        const slot = captureSlot(layout.number, false) orelse return -2;
                        const finish_slot = std.math.add(usize, slot, 1) catch return -2;
                        if (finish_slot >= capture_words) return -2;
                        for ([_]usize{ slot, finish_slot }) |item| {
                            if (undo_count >= undo.len) {
                                const capacity = std.math.mul(usize, undo.len, 2) catch return -2;
                                const grown = std.heap.c_allocator.alloc(Undo, capacity) catch return -2;
                                @memcpy(grown[0..undo_count], undo[0..undo_count]);
                                if (undo_heap) |items| std.heap.c_allocator.free(items);
                                undo_heap = grown;
                                undo = grown;
                            }
                            undo[undo_count] = .{ .slot = item, .previous = captures[item], .last = last.* };
                            undo_count += 1;
                        }
                        captures[slot] = @intCast(base + layout.begin);
                        captures[finish_slot] = @intCast(base + layout.end);
                        last.* = layout.number;
                    }
                }
                pos += chosen * run.width;
                pc += 1;
                continue;
            },
            .lazy_dot => blk: {
                const run = program.runs.items[instruction.value];
                if (pos > logical_endpos) break :blk;
                const room = endpos - pos;
                const allowed = if (run.maximum == unbounded) room else @min(run.maximum, room);
                const from = if (resumed_limit != unbounded) resumed_limit else run.minimum;
                resumed_limit = unbounded;
                resumed_max = 0;
                if (from > allowed) break :blk;
                const want = instruction.extra;
                const candidate: ?usize = if (text.kind == 1 and want < 256)
                    if (pos + from < endpos) std.mem.indexOfScalarPos(u8, text.data[0..@min(endpos, pos + allowed +| 1)], pos + from, @intCast(want)) else null
                else blk_find: {
                    var at = pos + from;
                    const finish = @min(endpos, pos + allowed +| 1);
                    while (at < finish) : (at += 1) {
                        if (text.at(at) == want) break :blk_find at;
                    }
                    break :blk_find null;
                };
                const found = candidate orelse break :blk;
                const chosen = found - pos;
                if (chosen < allowed) {
                    if (stack_count >= stack.len) {
                        const capacity = std.math.mul(usize, stack.len, 2) catch return -2;
                        const grown = std.heap.c_allocator.alloc(CaptureState, capacity) catch return -2;
                        @memcpy(grown[0..stack_count], stack[0..stack_count]);
                        if (stack_heap) |items| std.heap.c_allocator.free(items);
                        stack_heap = grown;
                        stack = grown;
                        if (program.nullable_loops) {
                            const grown_marks = std.heap.c_allocator.alloc(usize, capacity) catch return -2;
                            @memcpy(grown_marks[0..stack_count], guard_marks[0..stack_count]);
                            if (marks_heap) |items| std.heap.c_allocator.free(items);
                            marks_heap = grown_marks;
                            guard_marks = grown_marks;
                        }
                    }
                    if (program.nullable_loops) guard_marks[stack_count] = guard_count;
                    stack[stack_count] = .{ .pc = pc, .pos = pos, .undo = undo_count, .atomic = atomic_depth, .run_limit = chosen + 1, .run_max = allowed };
                    stack_count += 1;
                }
                pos += chosen;
                pc += 1;
                continue;
            },
            .peek => {
                const behind = instruction.value & 2 != 0;
                const found = if (behind)
                    pos <= logical_endpos and pos > 0 and
                        atomMatch(program, instruction.left, text.at(pos - 1), instruction.extra)
                else pos < logical_endpos and
                    atomMatch(program, instruction.left, text.at(pos), instruction.extra);
                if (found == (instruction.value & 1 != 0)) {
                    pc += 1;
                    continue;
                }
            },
            .peek_text => {
                const behind = instruction.value & 2 != 0;
                var at = if (behind) (if (pos >= instruction.right) pos - instruction.right else endpos) else pos;
                const found = (!behind or
                    (pos <= logical_endpos and pos >= instruction.right)) and
                    literalTextMatches(program, instruction.left, text,
                        if (behind) pos else endpos, &at, instruction.extra);
                if (found == (instruction.value & 1 != 0)) {
                    pc += 1;
                    continue;
                }
            },
            .peek_run => {
                const run = program.runs.items[instruction.left];
                const room = endpos - pos;
                const maximum = if (run.maximum == unbounded) room else @min(run.maximum, room);
                const available = runLength(program, run, text, pos, maximum);
                var found = false;
                if (available >= run.minimum) {
                    var count = run.minimum;
                    while (count <= available) : (count += 1) {
                        if (pos + count < endpos and atomMatch(program, instruction.right, text.at(pos + count), instruction.extra)) {
                            found = true;
                            break;
                        }
                    }
                }
                if (found == (instruction.value != 0)) {
                    pc += 1;
                    continue;
                }
            },
            .peek_even => {
                var even = true;
                var at = pos;
                while (at < endpos) : (at += 1) {
                    if (text.at(at) == instruction.extra) even = !even;
                }
                if (even == (instruction.value & 1 != 0)) {
                    pc = instruction.right;
                    continue;
                }
            },
            .accept => if ((!full or pos == endpos) and !(nonempty and pos == start)) return @intCast(pos),
        }
        if (stack_count == 0) return -1;
        stack_count -= 1;
        const state = stack[stack_count];
        while (program.nullable_loops and guard_count > guard_marks[stack_count]) {
            guard_count -= 1;
            const item = guard_undo[guard_count];
            guards[item.pc] = item.previous;
        }
        while (undo_count > state.undo) {
            undo_count -= 1;
            const item = undo[undo_count];
            if (item.slot != no_capture_slot) captures[item.slot] = item.previous;
            last.* = item.last;
        }
        pc = state.pc;
        pos = state.pos;
        atomic_depth = state.atomic;
        resumed_limit = state.run_limit;
        resumed_max = state.run_max;
    }
}

fn runCaptured(program: *const Program, text: Subject, endpos: usize, start: usize, full: bool, captures: []isize, last: *isize, nonempty: bool) isize {
    return runCapturedAt(program, text, endpos, endpos, start, 0, full, captures, last, true, nonempty);
}

fn destroyProgram(program: *Program) void {
    program.arena.deinit();
    std.heap.c_allocator.destroy(program);
}

fn compileOwned(pattern: [*]const u8, length: usize, flags: u32, recursion_enter: ?RecursionEnter, recursion_leave: ?RecursionLeave, recursion_context: ?*anyopaque) ?*Program {
    if ((recursion_enter == null) != (recursion_leave == null)) return null;
    const program = std.heap.c_allocator.create(Program) catch return null;
    program.* = Program{ .flags = flags, .arena = std.heap.ArenaAllocator.init(std.heap.c_allocator) };
    var parser = Parser{
        .source = pattern[0..length],
        .program = program,
        .recursion_enter = recursion_enter,
        .recursion_leave = recursion_leave,
        .recursion_context = recursion_context,
    };
    parser.open_groups.append(program.arena.allocator(), false) catch {
        destroyProgram(program);
        return null;
    };
    program.root = parser.alternative() catch {
        destroyProgram(program);
        return null;
    };
    if (parser.at != parser.source.len) {
        destroyProgram(program);
        return null;
    }
    for (program.nodes.items) |node| {
        switch (node) {
            .conditional => |conditional| if (conditional.number > program.groups) {
                destroyProgram(program);
                return null;
            },
            else => {},
        }
    }
    var compiler = Compiler{ .program = program, .flags = program.flags };
    compiler.node(program.root) catch {
        destroyProgram(program);
        return null;
    };
    _ = compiler.emit(.{ .op = .accept }) catch {
        destroyProgram(program);
        return null;
    };
    for (program.code.items) |*instruction| {
        if (instruction.op != .look or instruction.value & 2 != 0) continue;
        const entry: usize = instruction.left;
        if (entry + 8 >= program.code.items.len or instruction.right != entry + 9) continue;
        const split = program.code.items[entry];
        const first_run = program.code.items[entry + 1];
        const first_quote = program.code.items[entry + 2];
        const second_run = program.code.items[entry + 3];
        const second_quote = program.code.items[entry + 4];
        const jump = program.code.items[entry + 5];
        const final_run = program.code.items[entry + 6];
        const ending = program.code.items[entry + 7];
        const accept = program.code.items[entry + 8];
        if (split.op != .split or split.left != entry + 1 or split.right != entry + 6 or jump.op != .jump or jump.left != entry or first_run.op != .run or second_run.op != .run or final_run.op != .run or first_quote.op != .literal or second_quote.op != .literal or first_quote.value != second_quote.value or first_quote.extra != second_quote.extra or first_quote.extra & (2 | 8) != 0 or ending.op != .end or ending.extra & 8 != 0 or accept.op != .accept) continue;
        const quote = first_quote.value;
        if (quote == '\n') continue;
        if (!excludesOnly(program, first_run.value, quote, first_quote.extra) or !excludesOnly(program, second_run.value, quote, first_quote.extra) or !excludesOnly(program, final_run.value, quote, first_quote.extra)) continue;
        instruction.op = .peek_even;
        instruction.extra = quote;
    }
    program.references = false;
    for (program.code.items) |instruction| {
        switch (instruction.op) {
            .backref, .conditional, .look => {
                program.references = true;
                break;
            },
            else => {},
        }
    }
    prepareClasses(program, program.root, program.flags);
    for (program.code.items, 0..) |*instruction, pc| {
        if (instruction.op != .run) continue;
        const run = program.runs.items[instruction.value];
        if (!run.lazy or run.possessive or run.width != 1 or run.layout_count != 0 or run.flags & 16 == 0 or program.nodes.items[run.atom] != .dot) continue;
        var next = pc + 1;
        while (next < program.code.items.len and program.code.items[next].op == .save_end) : (next += 1) {}
        if (next >= program.code.items.len or program.code.items[next].op != .literal or program.code.items[next].extra & 2 != 0) continue;
        instruction.op = .lazy_dot;
        instruction.extra = program.code.items[next].value;
    }
    if (!program.references and program.groups != 0) {
        var first: usize = 0;
        while (first < program.code.items.len and program.code.items[first].op == .save_begin) : (first += 1) {}
        if (first < program.code.items.len and program.code.items[first].op == .run) {
            const run_index = program.code.items[first].value;
            const run = program.runs.items[run_index];
            if (run.width == 1 and run.minimum != 0 and run.maximum == unbounded) program.prefix_run = @intCast(first);
        } else if (first + 1 < program.code.items.len and program.code.items[first].op == .class and program.code.items[first + 1].op == .run) {
            const head = program.code.items[first];
            const class = &program.classes.items[head.left];
            const run = program.runs.items[program.code.items[first + 1].value];
            if (head.extra & 2 == 0 and !class.negative and class.categories == 0 and class.range_count == 0 and run.width == 1 and run.maximum == unbounded and run.flags == head.extra) {
                var subset = true;
                for (0..256) |raw| {
                    if (classMatch(program, class, @intCast(raw), head.extra) and !atomMatch(program, run.atom, @intCast(raw), run.flags)) {
                        subset = false;
                        break;
                    }
                }
                if (subset) program.prefix_run = @intCast(first);
            }
        }
    }
    var locale_sensitive = localeByteFlags(program.flags);
    if (!locale_sensitive) {
        for (program.nodes.items) |node| {
            switch (node) {
                .scoped => |scoped| {
                    if (localeByteFlags(scoped.flags)) locale_sensitive = true;
                },
                else => {},
            }
        }
    }
    program.nullable = addStarts(program, program.root, &program.starts, program.flags);
    if (locale_sensitive) {
        @memset(&program.starts, 1);
        @memset(&program.single, 1);
        @memset(&program.seconds, 0xff);
        program.single_start = 256;
        program.scoped_prefix = std.math.maxInt(u32);
        program.prefix_run = std.math.maxInt(u32);
        if (!program.nullable and !localeByteFlags(program.flags)) {
            if (scopedCategoryPrefix(program, program.root, false)) |class| {
                program.scoped_prefix = class;
            }
        }
    } else {
        if (!program.nullable) {
            var count: usize = 0;
            for (program.starts, 0..) |value, index| if (value != 0) {
                count += 1;
                program.single_start = @intCast(index);
            };
            if (count != 1) program.single_start = 256;
            if (scopedCategoryPrefix(program, program.root, false)) |class| program.scoped_prefix = class;
        }
        if (program.groups == 0 and program.nodes.items.len <= 20) {
            const start_prefix = quickPrefix(program, program.root, program.flags);
            program.single = start_prefix.single;
            for (start_prefix.second, 0..) |value, index| {
                if (value != 0) program.seconds[index >> 3] |= @as(u8, 1) << @intCast(index & 7);
            }
        } else program.single = [_]u8{1} ** 256;
    }
    return program;
}

pub export fn rebar_zig_compile(pattern: [*]const u8, length: usize, flags: u32) ?*Program {
    return compileOwned(pattern, length, flags, null, null, null);
}

pub export fn rebar_zig_compile_guarded(
    pattern: [*]const u8,
    length: usize,
    flags: u32,
    recursion_enter: ?RecursionEnter,
    recursion_leave: ?RecursionLeave,
    recursion_context: ?*anyopaque,
) ?*Program {
    return compileOwned(pattern, length, flags, recursion_enter, recursion_leave, recursion_context);
}

pub export fn rebar_zig_free(program: ?*Program) void {
    if (program) |value| destroyProgram(value);
}
pub export fn rebar_zig_program_size() usize {
    return @sizeOf(Program);
}

pub export fn rebar_zig_program_memory(program: ?*const Program) usize {
    const value = program orelse return 0;
    return @sizeOf(Program) + value.arena.queryCapacity();
}
pub export fn rebar_zig_groups(program: ?*const Program) usize {
    return if (program) |value| value.groups else 0;
}

pub export fn rebar_zig_flags(program: ?*const Program) u32 {
    return if (program) |value| value.flags & ~text_pattern_flag else 0;
}

pub export fn rebar_zig_name_count(program: ?*const Program) usize {
    return if (program) |value| value.names.items.len else 0;
}

pub export fn rebar_zig_name_length(program: ?*const Program, index: usize) usize {
    const value = program orelse return 0;
    return if (index < value.names.items.len) value.names.items[index].bytes.len else 0;
}

pub export fn rebar_zig_name_group(program: ?*const Program, index: usize) usize {
    const value = program orelse return 0;
    return if (index < value.names.items.len) value.names.items[index].group else 0;
}

pub export fn rebar_zig_name_copy(program: ?*const Program, index: usize, output: [*]u8, length: usize) usize {
    const value = program orelse return 0;
    if (index >= value.names.items.len) return 0;
    const name = value.names.items[index].bytes;
    const count = @min(length, name.len);
    @memcpy(output[0..count], name[0..count]);
    return count;
}

pub export fn rebar_zig_match_tree(program_value: ?*const Program, text_value: [*]const u8, length: usize, pos: usize, endpos_value: usize, mode: u8, begin: *isize, finish: *isize) c_int {
    const program = program_value orelse return -1;
    const endpos = @min(length, endpos_value);
    if (pos > endpos) return 0;
    const text = Subject{ .data = text_value, .length = length, .kind = 1 };
    const last = if (mode == 0) endpos else pos;
    var start = pos;
    while (start <= last) : (start += 1) {
        if (mode == 0 and program.single_start < 256 and text.kind == 1 and start < endpos) {
            start = std.mem.indexOfScalarPos(u8, text.data[0..endpos], start, @intCast(program.single_start)) orelse break;
        }
        var out = Positions{};
        eval(program, program.root, text, endpos, start, &out, 0, program.flags);
        for (out.values[0..out.count]) |value| {
            if (mode == 2 and value != endpos) continue;
            begin.* = @intCast(start);
            finish.* = @intCast(value);
            return 1;
        }
    }
    return 0;
}

pub export fn rebar_zig_match(program_value: ?*const Program, text_value: [*]const u8, length: usize, pos: usize, endpos_value: usize, mode: u8, begin: *isize, finish: *isize) c_int {
    return rebar_zig_match_wide(program_value, text_value, length, 1, pos, endpos_value, mode, begin, finish);
}

pub export fn rebar_zig_match_wide(program_value: ?*const Program, text_value: [*]const u8, length: usize, kind: u8, pos: usize, endpos_value: usize, mode: u8, begin: *isize, finish: *isize) c_int {
    return rebar_zig_match_nonempty_wide(program_value, text_value, length, kind, pos, endpos_value, mode, 0, begin, finish);
}

pub export fn rebar_zig_match_nonempty_wide(program_value: ?*const Program, text_value: [*]const u8, length: usize, kind: u8, pos: usize, endpos_value: usize, mode: u8, nonempty: u8, begin: *isize, finish: *isize) c_int {
    const program = program_value orelse return -1;
    if (kind != 1 and kind != 2 and kind != 4) return -1;
    const endpos = @min(length, endpos_value);
    if (pos > endpos) return 0;
    const text = Subject{ .data = text_value, .length = length, .kind = kind };
    if (program.code.items.len == 2 and program.code.items[0].op == .boundary_peek and !program.references) {
        if (mode == 2 and pos != endpos) return 0;
        const instruction = program.code.items[0];
        const last = if (mode == 0) endpos else pos;
        var start = pos + @as(usize, if (nonempty != 0) 1 else 0);
        while (start <= last) : (start += 1) {
            const left_word = start > 0 and word(text.at(start - 1), instruction.extra);
            const right_word = start < endpos and word(text.at(start), instruction.extra);
            const boundary_found = (left_word != right_word) == (instruction.value & 1 != 0);
            const behind = instruction.value & 4 != 0;
            const peek_found = if (behind) start > 0 and atomMatch(program, instruction.left, text.at(start - 1), instruction.extra) else start < endpos and atomMatch(program, instruction.left, text.at(start), instruction.extra);
            if (boundary_found or peek_found == (instruction.value & 2 != 0)) {
                begin.* = @intCast(start);
                finish.* = @intCast(start);
                return 1;
            }
        }
        return 0;
    }
    if (mode == 0 and !program.references and program.groups == 0 and program.code.items.len == 6) {
        const left_edge = program.code.items[0];
        const excluded = program.code.items[1];
        const first = program.code.items[2];
        const repeated = program.code.items[3];
        const right_edge = program.code.items[4];
        const accept = program.code.items[5];
        if (left_edge.op == .boundary and left_edge.value != 0 and excluded.op == .peek_text and excluded.value == 0 and first.op == .class and repeated.op == .run and right_edge.op == .boundary and right_edge.value != 0 and accept.op == .accept and isLiteralText(program, excluded.left)) {
            const run = program.runs.items[repeated.value];
            if (run.width == 1 and run.minimum == 0 and run.maximum == unbounded and !run.lazy and !run.possessive) {
                var start = pos;
                while (start < endpos) : (start += 1) {
                    const left_word = start > 0 and word(text.at(start - 1), left_edge.extra);
                    const right_word = word(text.at(start), left_edge.extra);
                    if (left_word == right_word or !classMatch(program, &program.classes.items[first.left], text.at(start), first.extra)) continue;
                    var check = start;
                    if (literalTextMatches(program, excluded.left, text, endpos, &check, excluded.extra)) continue;
                    const length_rest = runLength(program, run, text, start + 1, endpos - start - 1);
                    const token_end = start + 1 + length_rest;
                    const end_left = word(text.at(token_end - 1), right_edge.extra);
                    const end_right = token_end < endpos and word(text.at(token_end), right_edge.extra);
                    if (end_left == end_right) continue;
                    begin.* = @intCast(start);
                    finish.* = @intCast(token_end);
                    return 1;
                }
                return 0;
            }
        }
    }
    if (mode == 0 and !program.references and program.groups == 0 and (program.code.items.len == 4 or program.code.items.len == 6)) {
        const first = program.code.items[0];
        const first_separator = program.code.items[1];
        const second = program.code.items[2];
        const accept_index = program.code.items.len - 1;
        const accept = program.code.items[accept_index];
        if (first.op == .run and first_separator.op == .literal and second.op == .run and accept.op == .accept) {
            const first_run = program.runs.items[first.value];
            const second_run = program.runs.items[second.value];
            if (first_run.width == 1 and second_run.width == 1 and first_run.minimum != 0 and second_run.minimum != 0 and first_run.layout_count == 0 and second_run.layout_count == 0 and !first_run.possessive and !second_run.possessive and !atomMatch(program, first_run.atom, first_separator.value, first_run.flags)) {
                if (program.code.items.len == 4) {
                    var start = pos;
                    while (start < endpos) : (start += 1) {
                        if (!atomMatch(program, first_run.atom, text.at(start), first_run.flags)) continue;
                        const first_maximum = @min(first_run.maximum, endpos - start);
                        const first_length = runLength(program, first_run, text, start, first_maximum);
                        const separator_at = start + first_length;
                        if (first_length < first_run.minimum or separator_at >= endpos or !equal(first_separator.value, text.at(separator_at), first_separator.extra)) continue;
                        const second_start = separator_at + 1;
                        const second_maximum = @min(second_run.maximum, endpos - second_start);
                        const second_available = runLength(program, second_run, text, second_start, second_maximum);
                        if (second_available < second_run.minimum) continue;
                        const second_length = if (second_run.lazy) second_run.minimum else second_available;
                        begin.* = @intCast(start);
                        finish.* = @intCast(second_start + second_length);
                        return 1;
                    }
                    return 0;
                }
                const second_separator = program.code.items[3];
                const third = program.code.items[4];
                if (second_separator.op == .literal and third.op == .run) {
                    const third_run = program.runs.items[third.value];
                    if (third_run.width == 1 and third_run.minimum != 0 and third_run.layout_count == 0 and !third_run.possessive) {
                        var start = pos;
                        while (start < endpos) : (start += 1) {
                            if (!atomMatch(program, first_run.atom, text.at(start), first_run.flags)) continue;
                            const first_maximum = @min(first_run.maximum, endpos - start);
                            const first_length = runLength(program, first_run, text, start, first_maximum);
                            const first_separator_at = start + first_length;
                            if (first_length < first_run.minimum or first_separator_at >= endpos or !equal(first_separator.value, text.at(first_separator_at), first_separator.extra)) continue;
                            const second_start = first_separator_at + 1;
                            const second_maximum = @min(second_run.maximum, endpos - second_start);
                            const second_available = runLength(program, second_run, text, second_start, second_maximum);
                            if (second_available < second_run.minimum) continue;
                            var second_length = if (second_run.lazy) second_run.minimum else second_available;
                            while (true) {
                                const second_separator_at = second_start + second_length;
                                if (second_separator_at < endpos and equal(second_separator.value, text.at(second_separator_at), second_separator.extra)) {
                                    const third_start = second_separator_at + 1;
                                    const third_maximum = @min(third_run.maximum, endpos - third_start);
                                    const third_available = runLength(program, third_run, text, third_start, third_maximum);
                                    if (third_available >= third_run.minimum) {
                                        const third_length = if (third_run.lazy) third_run.minimum else third_available;
                                        begin.* = @intCast(start);
                                        finish.* = @intCast(third_start + third_length);
                                        return 1;
                                    }
                                }
                                if (second_run.lazy) {
                                    if (second_length == second_available) break;
                                    second_length += 1;
                                } else {
                                    if (second_length == second_run.minimum) break;
                                    second_length -= 1;
                                }
                            }
                        }
                        return 0;
                    }
                }
            }
        }
    }
    if (program.references) {
        const stride = std.math.add(usize, @as(usize, program.groups), 1) catch return -1;
        const word_count = std.math.mul(usize, stride, 2) catch return -1;
        var reference_scratch = CaptureScratch{};
        if (!reference_scratch.init(word_count)) return -1;
        defer reference_scratch.deinit();
        const spans = reference_scratch.items();
        const begins = spans[0..stride];
        const ends = spans[stride..word_count];
        var last: isize = -1;
        const result = rebar_zig_match_captures_wide(program_value, text_value, length, kind, pos, endpos_value, mode, nonempty, begins.ptr, ends.ptr, &last);
        if (result == 1) {
            begin.* = begins[0];
            finish.* = ends[0];
        }
        return result;
    }
    const last = if (mode == 0) endpos else pos;
    var start = pos;
    while (start <= last) : (start += 1) {
        if (mode == 0 and program.code.items.len != 0 and program.code.items[0].op == .begin) {
            const beginning = program.code.items[0];
            if (start != 0 and (beginning.extra & 8 == 0 or text.at(start - 1) != '\n')) {
                if (beginning.extra & 8 == 0) break;
                var newline = start;
                if (text.kind == 1) {
                    newline = std.mem.indexOfScalarPos(u8, text.data[0..endpos], start, '\n') orelse break;
                } else while (newline < endpos and text.at(newline) != '\n') : (newline += 1) {}
                if (newline >= endpos) break;
                start = newline + 1;
            }
        }
        if (mode == 0 and program.single_start < 256 and text.kind == 1 and start < endpos) {
            start = std.mem.indexOfScalarPos(u8, text.data[0..endpos], start, @intCast(program.single_start)) orelse break;
        }
        if (mode == 0 and !program.nullable and start < endpos) {
            const first = text.at(start);
            if (first < 256 and program.starts[first] == 0) continue;
            if (program.scoped_prefix != std.math.maxInt(u32) and !classMatch(program, &program.classes.items[program.scoped_prefix], first, program.flags)) continue;
            if (first < 256 and start + 1 < endpos) {
                const second = text.at(start + 1);
                if (second < 256 and program.single[first] == 0 and !hasSecond(&program.seconds, second)) continue;
            }
        }
        const found = runBytecode(program, text, endpos, start, mode == 2, nonempty != 0 and start == pos);
        if (found == -2) return -1;
        if (found < 0) continue;
        begin.* = @intCast(start);
        finish.* = found;
        return 1;
    }
    return 0;
}

pub export fn rebar_zig_batch(program: ?*const Program, text: [*]const u8, length: usize, pos: usize, endpos: usize, mode: u8, iterations: usize, begin: *isize, finish: *isize) c_int {
    var result: c_int = 0;
    for (0..iterations) |_| {
        result = rebar_zig_match(program, text, length, pos, endpos, mode, begin, finish);
        std.mem.doNotOptimizeAway(result);
        std.mem.doNotOptimizeAway(begin.*);
        std.mem.doNotOptimizeAway(finish.*);
    }
    return result;
}

pub export fn rebar_zig_match_captures(program_value: ?*const Program, text_value: [*]const u8, length: usize, pos: usize, endpos_value: usize, mode: u8, nonempty: u8, begins: [*]isize, ends: [*]isize, last: *isize) c_int {
    return rebar_zig_match_captures_wide(program_value, text_value, length, 1, pos, endpos_value, mode, nonempty, begins, ends, last);
}

pub export fn rebar_zig_match_captures_wide(program_value: ?*const Program, text_value: [*]const u8, length: usize, kind: u8, pos: usize, endpos_value: usize, mode: u8, nonempty: u8, begins: [*]isize, ends: [*]isize, last: *isize) c_int {
    const program = program_value orelse return -1;
    if (kind != 1 and kind != 2 and kind != 4) return -1;
    const endpos = @min(length, endpos_value);
    if (pos > endpos) return 0;
    const text = Subject{ .data = text_value, .length = length, .kind = kind };
    if (mode == 0 and !program.references and program.groups == 3 and program.code.items.len == 12) {
        const first_begin = program.code.items[0];
        const first = program.code.items[1];
        const first_end = program.code.items[2];
        const first_separator = program.code.items[3];
        const second_begin = program.code.items[4];
        const second = program.code.items[5];
        const second_end = program.code.items[6];
        const second_separator = program.code.items[7];
        const third_begin = program.code.items[8];
        const third = program.code.items[9];
        const third_end = program.code.items[10];
        const accept = program.code.items[11];
        if (first_begin.op == .save_begin and first.op == .run and first_end.op == .save_end and first_begin.left == first_end.left and first_separator.op == .literal and second_begin.op == .save_begin and second.op == .run and second_end.op == .save_end and second_begin.left == second_end.left and second_separator.op == .literal and third_begin.op == .save_begin and third.op == .run and third_end.op == .save_end and third_begin.left == third_end.left and accept.op == .accept) {
            const first_run = program.runs.items[first.value];
            const second_run = program.runs.items[second.value];
            const third_run = program.runs.items[third.value];
            if (first_run.width == 1 and second_run.width == 1 and third_run.width == 1 and first_run.minimum != 0 and second_run.minimum != 0 and third_run.minimum != 0 and first_run.layout_count == 0 and second_run.layout_count == 0 and third_run.layout_count == 0 and !first_run.possessive and !second_run.possessive and !third_run.possessive) {
                var start = pos;
                while (start < endpos) : (start += 1) {
                    if (!atomMatch(program, first_run.atom, text.at(start), first_run.flags)) continue;
                    const first_maximum = @min(first_run.maximum, endpos - start);
                    const first_available = runLength(program, first_run, text, start, first_maximum);
                    if (first_available < first_run.minimum) continue;
                    var first_length = if (first_run.lazy) first_run.minimum else first_available;
                    while (true) {
                        const first_separator_at = start + first_length;
                        if (first_separator_at < endpos and equal(first_separator.value, text.at(first_separator_at), first_separator.extra)) {
                            const second_start = first_separator_at + 1;
                            const second_maximum = @min(second_run.maximum, endpos - second_start);
                            const second_available = runLength(program, second_run, text, second_start, second_maximum);
                            if (second_available >= second_run.minimum) {
                                var second_length = if (second_run.lazy) second_run.minimum else second_available;
                                while (true) {
                                    const second_separator_at = second_start + second_length;
                                    if (second_separator_at < endpos and equal(second_separator.value, text.at(second_separator_at), second_separator.extra)) {
                                        const third_start = second_separator_at + 1;
                                        const third_maximum = @min(third_run.maximum, endpos - third_start);
                                        const third_available = runLength(program, third_run, text, third_start, third_maximum);
                                        if (third_available >= third_run.minimum) {
                                            const third_length = if (third_run.lazy) third_run.minimum else third_available;
                                            begins[0] = @intCast(start);
                                            ends[0] = @intCast(third_start + third_length);
                                            begins[first_begin.left] = @intCast(start);
                                            ends[first_begin.left] = @intCast(first_separator_at);
                                            begins[second_begin.left] = @intCast(second_start);
                                            ends[second_begin.left] = @intCast(second_separator_at);
                                            begins[third_begin.left] = @intCast(third_start);
                                            ends[third_begin.left] = @intCast(third_start + third_length);
                                            last.* = third_begin.left;
                                            return 1;
                                        }
                                    }
                                    if (second_run.lazy) {
                                        if (second_length == second_available) break;
                                        second_length += 1;
                                    } else {
                                        if (second_length == second_run.minimum) break;
                                        second_length -= 1;
                                    }
                                }
                            }
                        }
                        if (first_run.lazy) {
                            if (first_length == first_available) break;
                            first_length += 1;
                        } else {
                            if (first_length == first_run.minimum) break;
                            first_length -= 1;
                        }
                    }
                }
                return 0;
            }
        }
    }
    if (mode == 0 and !program.references and program.groups == 2 and program.code.items.len == 11) {
        const key_begin = program.code.items[0];
        const key_first = program.code.items[1];
        const key_rest = program.code.items[2];
        const key_end = program.code.items[3];
        const before = program.code.items[4];
        const separator = program.code.items[5];
        const after = program.code.items[6];
        const value_begin = program.code.items[7];
        const value = program.code.items[8];
        const value_end = program.code.items[9];
        const accept = program.code.items[10];
        if (key_begin.op == .save_begin and key_first.op == .class and key_rest.op == .run and key_end.op == .save_end and key_begin.left == key_end.left and before.op == .run and separator.op == .literal and after.op == .run and value_begin.op == .save_begin and value.op == .run and value_end.op == .save_end and value_begin.left == value_end.left and accept.op == .accept) {
            const rest_run = program.runs.items[key_rest.value];
            const before_run = program.runs.items[before.value];
            const after_run = program.runs.items[after.value];
            const value_run = program.runs.items[value.value];
            if (rest_run.width == 1 and before_run.width == 1 and after_run.width == 1 and value_run.width == 1 and rest_run.minimum == 0 and before_run.minimum == 0 and after_run.minimum == 0 and value_run.minimum != 0 and rest_run.maximum == unbounded and before_run.maximum == unbounded and after_run.maximum == unbounded and value_run.maximum == unbounded and !rest_run.lazy and !before_run.lazy and !after_run.lazy and !value_run.lazy and !rest_run.possessive and !before_run.possessive and !after_run.possessive and !value_run.possessive and rest_run.layout_count == 0 and before_run.layout_count == 0 and after_run.layout_count == 0 and value_run.layout_count == 0 and !atomMatch(program, rest_run.atom, separator.value, rest_run.flags) and !atomMatch(program, before_run.atom, separator.value, before_run.flags)) {
                var start = pos;
                while (start < endpos) : (start += 1) {
                    if (!classMatch(program, &program.classes.items[key_first.left], text.at(start), key_first.extra)) continue;
                    const key_finish = start + 1 + runLength(program, rest_run, text, start + 1, endpos - start - 1);
                    var cursor = key_finish + runLength(program, before_run, text, key_finish, endpos - key_finish);
                    if (cursor >= endpos or !equal(separator.value, text.at(cursor), separator.extra)) {
                        start = key_finish - 1;
                        continue;
                    }
                    cursor += 1;
                    var spaces = runLength(program, after_run, text, cursor, endpos - cursor);
                    while (true) {
                        const value_start = cursor + spaces;
                        const value_length = runLength(program, value_run, text, value_start, endpos - value_start);
                        if (value_length >= value_run.minimum) {
                            begins[0] = @intCast(start);
                            ends[0] = @intCast(value_start + value_length);
                            begins[key_begin.left] = @intCast(start);
                            ends[key_begin.left] = @intCast(key_finish);
                            begins[value_begin.left] = @intCast(value_start);
                            ends[value_begin.left] = @intCast(value_start + value_length);
                            last.* = value_begin.left;
                            return 1;
                        }
                        if (spaces == 0) break;
                        spaces -= 1;
                    }
                    start = key_finish - 1;
                }
                return 0;
            }
        }
    }
    if (mode == 0 and program.groups == 2 and program.code.items.len == 8) {
        const open_begin = program.code.items[0];
        const opening = program.code.items[1];
        const open_end = program.code.items[2];
        const body_begin = program.code.items[3];
        const repeated = program.code.items[4];
        const body_end = program.code.items[5];
        const closing = program.code.items[6];
        const accept = program.code.items[7];
        if (open_begin.op == .save_begin and opening.op == .class and open_end.op == .save_end and open_begin.left == open_end.left and body_begin.op == .save_begin and repeated.op == .run and body_end.op == .save_end and body_begin.left == body_end.left and closing.op == .backref and closing.left == open_begin.left and accept.op == .accept) {
            const run = program.runs.items[repeated.value];
            if (run.lazy and !run.possessive and run.width == 1 and run.minimum == 0 and run.maximum == unbounded and run.layout_count == 0 and program.nodes.items[run.atom] == .dot) {
                var opening_at = pos;
                while (opening_at < endpos) : (opening_at += 1) {
                    const opener = text.at(opening_at);
                    if (!classMatch(program, &program.classes.items[opening.left], opener, opening.extra)) continue;
                    var closing_at = opening_at + 1;
                    while (closing_at < endpos) : (closing_at += 1) {
                        const value = text.at(closing_at);
                        if (run.flags & 16 == 0 and value == '\n') break;
                        if (!backrefEqual(opener, value, closing.extra)) continue;
                        begins[0] = @intCast(opening_at);
                        ends[0] = @intCast(closing_at + 1);
                        begins[open_begin.left] = @intCast(opening_at);
                        ends[open_begin.left] = @intCast(opening_at + 1);
                        begins[body_begin.left] = @intCast(opening_at + 1);
                        ends[body_begin.left] = @intCast(closing_at);
                        last.* = body_begin.left;
                        return 1;
                    }
                }
                return 0;
            }
        } else if (!program.references and open_begin.op == .save_begin and opening.op == .run and open_end.op == .save_end and open_begin.left == open_end.left and body_begin.op == .literal and repeated.op == .save_begin and body_end.op == .run and closing.op == .save_end and repeated.left == closing.left and accept.op == .accept) {
            const first_run = program.runs.items[opening.value];
            const second_run = program.runs.items[body_end.value];
            if (first_run.width == 1 and second_run.width == 1 and first_run.minimum != 0 and second_run.minimum != 0 and first_run.layout_count == 0 and second_run.layout_count == 0 and !first_run.possessive and !second_run.possessive and !atomMatch(program, first_run.atom, body_begin.value, first_run.flags)) {
                var start = pos;
                while (start < endpos) : (start += 1) {
                    if (!atomMatch(program, first_run.atom, text.at(start), first_run.flags)) continue;
                    const first_maximum = @min(first_run.maximum, endpos - start);
                    const first_length = runLength(program, first_run, text, start, first_maximum);
                    const separator_at = start + first_length;
                    if (first_length < first_run.minimum or separator_at >= endpos or !equal(body_begin.value, text.at(separator_at), body_begin.extra)) continue;
                    const value_at = separator_at + 1;
                    const second_maximum = @min(second_run.maximum, endpos - value_at);
                    const available = runLength(program, second_run, text, value_at, second_maximum);
                    if (available < second_run.minimum) continue;
                    const second_length = if (second_run.lazy) second_run.minimum else available;
                    begins[0] = @intCast(start);
                    ends[0] = @intCast(value_at + second_length);
                    begins[open_begin.left] = @intCast(start);
                    ends[open_begin.left] = @intCast(separator_at);
                    begins[repeated.left] = @intCast(value_at);
                    ends[repeated.left] = @intCast(value_at + second_length);
                    last.* = repeated.left;
                    return 1;
                }
                return 0;
            }
        }
    }
    const final_start = if (mode == 0) endpos else pos;
    var start = pos;
    const word_count = captureWordCount(program) orelse return -1;
    var capture_scratch = CaptureScratch{};
    if (!capture_scratch.init(word_count)) return -1;
    defer capture_scratch.deinit();
    const captures = capture_scratch.items();
    while (start <= final_start) : (start += 1) {
        if (mode == 0 and program.code.items.len != 0 and program.code.items[0].op == .begin) {
            const beginning = program.code.items[0];
            if (start != 0 and (beginning.extra & 8 == 0 or text.at(start - 1) != '\n')) {
                if (beginning.extra & 8 == 0) break;
                var newline = start;
                if (text.kind == 1) {
                    newline = std.mem.indexOfScalarPos(u8, text.data[0..endpos], start, '\n') orelse break;
                } else while (newline < endpos and text.at(newline) != '\n') : (newline += 1) {}
                if (newline >= endpos) break;
                start = newline + 1;
            }
        }
        if (mode == 0 and program.single_start < 256 and text.kind == 1 and start < endpos) {
            start = std.mem.indexOfScalarPos(u8, text.data[0..endpos], start, @intCast(program.single_start)) orelse break;
        }
        if (mode == 0 and !program.nullable and start < endpos) {
            const first = text.at(start);
            if (first < 256 and program.starts[first] == 0) continue;
            if (program.scoped_prefix != std.math.maxInt(u32) and !classMatch(program, &program.classes.items[program.scoped_prefix], first, program.flags)) continue;
            if (first < 256 and start + 1 < endpos) {
                const second = text.at(start + 1);
                if (second < 256 and program.single[first] == 0 and !hasSecond(&program.seconds, second)) continue;
            }
            if (program.prefix_run != std.math.maxInt(u32) and start > pos) {
                if (prefixRunAccepts(program, program.prefix_run, text.at(start - 1))) continue;
            }
        }
        const finish = runCaptured(program, text, endpos, start, mode == 2, captures, last, nonempty != 0 and start == pos);
        if (finish == -2) return -1;
        if (finish < 0) continue;
        begins[0] = @intCast(start);
        ends[0] = finish;
        for (0..program.groups) |index| {
            begins[index + 1] = captures[index * 2];
            ends[index + 1] = captures[index * 2 + 1];
        }
        return 1;
    }
    return 0;
}

pub export fn rebar_zig_match_inverted_wide(
    program_value: ?*const Program,
    text_value: [*]const u8,
    length: usize,
    kind: u8,
    pos: usize,
    endpos_value: usize,
    nonempty: u8,
    begins: [*]isize,
    ends: [*]isize,
    last: *isize,
) c_int {
    const program = program_value orelse return -1;
    if (kind != 1 and kind != 2 and kind != 4) return -1;
    const logical_endpos = @min(length, endpos_value);
    if (pos <= logical_endpos or pos > length) return 0;
    const text = Subject{ .data = text_value, .length = length, .kind = kind };
    const word_count = captureWordCount(program) orelse return -1;
    var capture_scratch = CaptureScratch{};
    if (!capture_scratch.init(word_count)) return -1;
    defer capture_scratch.deinit();
    const captures = capture_scratch.items();
    const finish = runCapturedAt(program, text, pos, logical_endpos, pos, 0,
        false, captures, last, true, nonempty != 0);
    if (finish == -2) return -1;
    if (finish < 0) return 0;
    begins[0] = @intCast(pos);
    ends[0] = finish;
    for (0..program.groups) |index| {
        begins[index + 1] = captures[index * 2];
        ends[index + 1] = captures[index * 2 + 1];
    }
    return 1;
}

pub export fn rebar_zig_collect_captures(program_value: ?*const Program, text_value: [*]const u8, length: usize, pos: usize, endpos_value: usize, capacity: usize, begins: [*]isize, ends: [*]isize, lasts: [*]isize) isize {
    const program = program_value orelse return -1;
    const endpos = @min(length, endpos_value);
    if (pos > endpos) return 0;
    if (capacity > std.math.maxInt(isize)) return -1;

    const stride = std.math.add(usize, @as(usize, program.groups), 1) catch return -1;
    var current = pos;
    var nonempty: u8 = 0;
    var count: usize = 0;
    while (current <= endpos and count < capacity) {
        const base = std.math.mul(usize, count, stride) catch return -1;
        const matched = rebar_zig_match_captures(program, text_value, length, current, endpos, 0, nonempty, begins + base, ends + base, &lasts[count]);
        if (matched < 0) return -1;
        if (matched == 0) break;
        const begin: usize = @intCast(begins[base]);
        const finish: usize = @intCast(ends[base]);
        count += 1;
        if (begin == finish) {
            current = begin;
            nonempty = 1;
        } else {
            current = finish;
            nonempty = 0;
        }
    }
    return @intCast(count);
}

pub export fn rebar_zig_collect_records(program_value: ?*const Program, text_value: [*]const u8, length: usize, endpos_value: usize, capacity: usize, records: [*]isize, cursor: *usize, retry_nonempty: *u8) isize {
    return rebar_zig_collect_records_wide(program_value, text_value, length, 1, endpos_value, capacity, records, cursor, retry_nonempty);
}

pub export fn rebar_zig_collect_records_wide(program_value: ?*const Program, text_value: [*]const u8, length: usize, kind: u8, endpos_value: usize, capacity: usize, records: [*]isize, cursor: *usize, retry_nonempty: *u8) isize {
    const program = program_value orelse return -1;
    const endpos = @min(length, endpos_value);
    if (capacity > std.math.maxInt(isize)) return -1;
    const groups = std.math.add(usize, @as(usize, program.groups), 1) catch return -1;
    const capture_words = std.math.mul(usize, groups, 2) catch return -1;
    const width = std.math.add(usize, capture_words, 1) catch return -1;
    var current = cursor.*;
    var nonempty = retry_nonempty.*;
    var count: usize = 0;
    if (groups == 1 and program.code.items.len >= 3 and program.code.items[0].op == .literal and program.code.items[1].op == .peek_even and program.code.items[0].extra & 2 == 0 and program.code.items[0].value != program.code.items[1].extra) {
        const separator = program.code.items[0].value;
        const quote = program.code.items[1].extra;
        const positive = program.code.items[1].value & 1 != 0;
        const text = Subject{ .data = text_value, .length = length, .kind = kind };
        var even = true;
        var scan = current;
        while (scan < endpos) : (scan += 1) {
            if (text.at(scan) == quote) even = !even;
        }
        var prefix = true;
        scan = current;
        while (scan < endpos and count < capacity) : (scan += 1) {
            const value = text.at(scan);
            if (value == quote) {
                prefix = !prefix;
                continue;
            }
            if (value != separator or (prefix == even) != positive) continue;
            const base = std.math.mul(usize, count, width) catch return -1;
            records[base] = @intCast(scan);
            records[base + 1] = @intCast(scan + 1);
            records[base + 2] = -1;
            count += 1;
            current = scan + 1;
            nonempty = 0;
        }
        cursor.* = current;
        retry_nonempty.* = nonempty;
        return @intCast(count);
    }
    while (current <= endpos and count < capacity) {
        const base = std.math.mul(usize, count, width) catch return -1;
        const begins = records + base;
        const ends = begins + groups;
        const last = ends + groups;
        const matched = if (groups == 1) blk: {
            last[0] = -1;
            break :blk rebar_zig_match_nonempty_wide(program, text_value, length, kind, current, endpos, 0, nonempty, &begins[0], &ends[0]);
        } else rebar_zig_match_captures_wide(program, text_value, length, kind, current, endpos, 0, nonempty, begins, ends, &last[0]);
        if (matched < 0) return -1;
        if (matched == 0) break;
        const begin: usize = @intCast(begins[0]);
        const finish: usize = @intCast(ends[0]);
        count += 1;
        if (finish == begin) {
            current = begin;
            nonempty = 1;
        } else {
            current = finish;
            nonempty = 0;
        }
    }
    cursor.* = current;
    retry_nonempty.* = nonempty;
    return @intCast(count);
}
