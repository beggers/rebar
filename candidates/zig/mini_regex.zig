const std = @import("std");

const max_nodes = 4096;
const max_classes = 128;
const max_positions = 512;
const max_code = 16384;
const max_stack = 8192;
const max_groups = 256;
const max_undo = 65536;
const max_name_length = 63;
const max_class_ranges = 8192;
const unbounded = std.math.maxInt(usize);
const text_pattern_flag: u32 = 0x80000000;

extern fn _PyUnicode_IsAlpha(u32) c_int;
extern fn _PyUnicode_IsDecimalDigit(u32) c_int;
extern fn _PyUnicode_IsDigit(u32) c_int;
extern fn _PyUnicode_IsNumeric(u32) c_int;
extern fn _PyUnicode_IsWhitespace(u32) c_int;
extern fn _PyUnicode_ToLowercase(u32) u32;
extern fn _PyUnicode_ToUppercase(u32) u32;

const Pair = struct { left: u16, right: u16 };
const Repeat = struct { child: u16, minimum: usize, maximum: usize, lazy: bool, possessive: bool };
const Group = struct { child: u16, number: u16 };
const Conditional = struct { number: u16, yes: u16, no: u16 };
const Look = struct { child: u16, behind: bool, positive: bool, width: u16 };
const Scoped = struct { child: u16, flags: u32 };
const Name = struct { bytes: [max_name_length]u8 = undefined, length: u8 = 0, group: u16 = 0 };
const Node = union(enum) {
    empty,
    literal: u32,
    dot,
    class: u16,
    begin,
    end,
    absolute_begin,
    absolute_end,
    boundary: bool,
    sequence: Pair,
    alternative: Pair,
    repeat: Repeat,
    group: Group,
    backref: u16,
    conditional: Conditional,
    atomic: u16,
    look: Look,
    scoped: Scoped,
};
const ClassRange = struct { left: u32, right: u32 };
const CharClass = struct {
    bits: [32]u8 = [_]u8{0} ** 32,
    range_start: u16 = 0,
    range_count: u16 = 0,
    categories: u8 = 0,
    negative: bool = false,
    locale_multi: bool = false,
};
const Op = enum(u8) { literal, dot, class, begin, end, absolute_begin, absolute_end, boundary, split, jump, save_begin, save_end, backref, conditional, atomic_begin, atomic_end, look, accept };
const Instruction = struct { op: Op, left: u16 = 0, right: u16 = 0, extra: u16 = 0, value: u32 = 0 };
const Program = struct {
    nodes: [max_nodes]Node = undefined,
    node_count: u16 = 0,
    classes: [max_classes]CharClass = undefined,
    class_count: u16 = 0,
    ranges: [max_class_ranges]ClassRange = undefined,
    range_count: u16 = 0,
    root: u16 = 0,
    flags: u32 = 0,
    code: [max_code]Instruction = undefined,
    code_count: u16 = 0,
    starts: [256]u8 = [_]u8{0} ** 256,
    single: [256]u8 = [_]u8{0} ** 256,
    pairs: [8192]u8 = [_]u8{0} ** 8192,
    nullable: bool = false,
    scoped_prefix: u16 = std.math.maxInt(u16),
    groups: u16 = 0,
    references: bool = false,
    nullable_loops: bool = false,
    names: [max_groups]Name = undefined,
    name_count: u16 = 0,
};

const ParseError = error{ TooManyNodes, TooManyClasses, InvalidPattern, Unsupported };
const Parser = struct {
    source: []const u8,
    at: usize = 0,
    program: *Program,
    open_groups: [max_groups + 1]bool = [_]bool{false} ** (max_groups + 1),
    lookbehind_bases: [256]u16 = undefined,
    lookbehind_depth: usize = 0,

    fn add(self: *Parser, node: Node) ParseError!u16 {
        if (self.program.node_count >= max_nodes) return error.TooManyNodes;
        const index = self.program.node_count;
        self.program.nodes[index] = node;
        self.program.node_count += 1;
        return index;
    }

    fn setBit(class: *CharClass, value: u8) void {
        class.bits[value >> 3] |= @as(u8, 1) << @intCast(value & 7);
    }

    fn skip(self: *Parser) void {
        while (self.at < self.source.len) {
            if (self.at + 2 < self.source.len and self.source[self.at] == '(' and self.source[self.at + 1] == '?' and self.source[self.at + 2] == '#') {
                const close = std.mem.indexOfScalarPos(u8, self.source, self.at + 3, ')') orelse return;
                self.at = close + 1;
                continue;
            }
            if (self.program.flags & 64 == 0) return;
            const value = self.source[self.at];
            if (value == ' ' or value == '\t' or value == '\n' or value == '\r' or value == 11 or value == 12) {
                self.at += 1;
                continue;
            }
            if (value == '#') {
                while (self.at < self.source.len and self.source[self.at] != '\n') : (self.at += 1) {}
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

    fn category(self: *Parser, code: u8) ParseError!u16 {
        if (self.program.class_count >= max_classes) return error.TooManyClasses;
        const index = self.program.class_count;
        self.program.class_count += 1;
        var class = CharClass{};
        class.range_start = self.program.range_count;
        class.categories = categoryBit(code);
        self.program.classes[index] = class;
        return self.add(.{ .class = index });
    }

    fn parseClass(self: *Parser) ParseError!u16 {
        if (self.program.class_count >= max_classes) return error.TooManyClasses;
        const index = self.program.class_count;
        self.program.class_count += 1;
        var class = CharClass{};
        class.range_start = self.program.range_count;
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
                self.program.classes[index] = class;
                return self.add(.{ .class = index });
            }
            first = false;
            var left = try self.codepoint();
            if (left == '\\') {
                if (self.at >= self.source.len) return error.InvalidPattern;
                const code = self.source[self.at];
                self.at += 1;
                if (code == 'd' or code == 'D' or code == 's' or code == 'S' or code == 'w' or code == 'W') {
                    class.categories |= categoryBit(code);
                    continue;
                }
                left = try self.escaped(code, true);
            }
            if (self.at + 1 < self.source.len and self.source[self.at] == '-' and self.source[self.at + 1] != ']') {
                self.at += 1;
                var right = try self.codepoint();
                if (right == '\\') {
                    if (self.at >= self.source.len) return error.InvalidPattern;
                    const code = self.source[self.at];
                    self.at += 1;
                    right = try self.escaped(code, true);
                }
                if (right < left) return error.InvalidPattern;
                if (left < 256) {
                    const stop = @min(right, 255);
                    for (@as(usize, left)..@as(usize, stop) + 1) |raw| setBit(&class, @intCast(raw));
                }
                if (right >= 256) {
                    if (self.program.range_count >= max_class_ranges) return error.Unsupported;
                    self.program.ranges[self.program.range_count] = .{ .left = @max(left, 256), .right = right };
                    self.program.range_count += 1;
                    class.range_count += 1;
                }
            } else if (left < 256) setBit(&class, @intCast(left)) else {
                if (self.program.range_count >= max_class_ranges) return error.Unsupported;
                self.program.ranges[self.program.range_count] = .{ .left = left, .right = left };
                self.program.range_count += 1;
                class.range_count += 1;
            }
        }
        return error.InvalidPattern;
    }

    fn atom(self: *Parser) ParseError!u16 {
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
                        if (self.lookbehind_depth >= self.lookbehind_bases.len) return error.Unsupported;
                        self.lookbehind_bases[self.lookbehind_depth] = self.program.groups;
                        self.lookbehind_depth += 1;
                        const child = self.alternative() catch |err| {
                            self.lookbehind_depth -= 1;
                            return err;
                        };
                        self.lookbehind_depth -= 1;
                        if (self.at >= self.source.len or self.source[self.at] != ')') return error.InvalidPattern;
                        self.at += 1;
                        const look_width = fixedWidth(self.program, child) orelse return error.Unsupported;
                        if (look_width > std.math.maxInt(u16)) return error.Unsupported;
                        self.program.references = true;
                        break :blk self.add(.{ .look = .{ .child = child, .behind = true, .positive = positive, .width = @intCast(look_width) } });
                    } else if (self.source[self.at + 1] == '(') {
                        self.at += 2;
                        const reference_number = try self.reference();
                        if (reference_number == 0 or reference_number > max_groups or self.at >= self.source.len or self.source[self.at] != ')') return error.Unsupported;
                        if (self.lookbehind_depth != 0 and reference_number > self.lookbehind_bases[0]) return error.InvalidPattern;
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
                        if (reference_number <= max_groups and self.open_groups[reference_number]) return error.InvalidPattern;
                        if (self.lookbehind_depth != 0 and reference_number > self.lookbehind_bases[0]) return error.InvalidPattern;
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
                var group_number: u16 = 0;
                if (capturing) {
                    if (self.program.groups >= max_groups) return error.Unsupported;
                    self.program.groups += 1;
                    group_number = self.program.groups;
                    if (group_name) |name| try self.addName(name, group_number);
                    self.open_groups[group_number] = true;
                }
                const child = try self.alternative();
                if (capturing) self.open_groups[group_number] = false;
                if (self.at >= self.source.len or self.source[self.at] != ')') return error.InvalidPattern;
                self.at += 1;
                break :blk if (capturing) try self.add(.{ .group = .{ .child = child, .number = group_number } }) else child;
            },
            '\\' => blk: {
                if (self.at >= self.source.len) return error.InvalidPattern;
                const code = self.source[self.at];
                self.at += 1;
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
                    if (reference_number <= max_groups and self.open_groups[reference_number]) return error.InvalidPattern;
                    if (self.lookbehind_depth != 0 and reference_number > self.lookbehind_bases[0]) return error.InvalidPattern;
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
        }
        if (self.at == begin) return error.InvalidPattern;
        return value;
    }

    fn identifier(self: *Parser, close: u8) ParseError![]const u8 {
        const begin = self.at;
        while (self.at < self.source.len and self.source[self.at] != close) : (self.at += 1) {}
        if (self.at >= self.source.len or self.at == begin or self.at - begin > max_name_length) return error.InvalidPattern;
        const value = self.source[begin..self.at];
        const text_mode = self.program.flags & text_pattern_flag != 0;
        if (!(std.ascii.isAlphabetic(value[0]) or value[0] == '_' or text_mode and value[0] >= 0x80)) return error.InvalidPattern;
        for (value[1..]) |item| if (!(std.ascii.isAlphanumeric(item) or item == '_' or text_mode and item >= 0x80)) return error.InvalidPattern;
        self.at += 1;
        return value;
    }

    fn addName(self: *Parser, name: []const u8, group: u16) ParseError!void {
        if (self.program.name_count >= max_groups) return error.Unsupported;
        for (self.program.names[0..self.program.name_count]) |value| {
            if (std.mem.eql(u8, value.bytes[0..value.length], name)) return error.InvalidPattern;
        }
        const index = self.program.name_count;
        self.program.name_count += 1;
        self.program.names[index].length = @intCast(name.len);
        self.program.names[index].group = group;
        @memcpy(self.program.names[index].bytes[0..name.len], name);
    }

    fn reference(self: *Parser) ParseError!usize {
        if (self.at < self.source.len and std.ascii.isDigit(self.source[self.at])) return self.number();
        const begin = self.at;
        while (self.at < self.source.len and self.source[self.at] != ')') : (self.at += 1) {}
        if (self.at == begin) return error.InvalidPattern;
        const name = self.source[begin..self.at];
        for (self.program.names[0..self.program.name_count]) |value| {
            if (std.mem.eql(u8, value.bytes[0..value.length], name)) return value.group;
        }
        return error.Unsupported;
    }

    fn repeated(self: *Parser) ParseError!u16 {
        const child = try self.atom();
        if (self.at >= self.source.len) return child;
        const mark = self.source[self.at];
        if (mark == '{' and !self.braceRepeat()) return child;
        if (mark == '*' or mark == '+' or mark == '?' or mark == '{') {
            switch (self.program.nodes[child]) {
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

    fn sequence(self: *Parser) ParseError!u16 {
        var value: ?u16 = null;
        self.skip();
        while (self.at < self.source.len and self.source[self.at] != '|' and self.source[self.at] != ')') {
            const next = try self.repeated();
            value = if (value) |left| try self.add(.{ .sequence = .{ .left = left, .right = next } }) else next;
            self.skip();
        }
        return value orelse self.add(.empty);
    }

    fn alternative(self: *Parser) ParseError!u16 {
        var value = try self.sequence();
        while (self.at < self.source.len and self.source[self.at] == '|') {
            self.at += 1;
            value = try self.add(.{ .alternative = .{ .left = value, .right = try self.sequence() } });
        }
        return value;
    }
};

fn fixedWidth(program: *const Program, index: u16) ?usize {
    return switch (program.nodes[index]) {
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
            for (program.nodes[0..program.node_count]) |node| {
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
    if (flags & 2 == 0) return left == right;
    const ascii_only = asciiMode(flags);
    return folded(left, ascii_only) == folded(right, ascii_only);
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
        'd' => if (ascii_only) value >= '0' and value <= '9' else _PyUnicode_IsDecimalDigit(value) != 0,
        's' => if (ascii_only) value == ' ' or value == '\t' or value == '\n' or value == '\r' or value == 11 or value == 12 else _PyUnicode_IsWhitespace(value) != 0,
        'w' => if (ascii_only) value < 128 and (std.ascii.isAlphanumeric(@intCast(value)) or value == '_') else value == '_' or _PyUnicode_IsAlpha(value) != 0 or _PyUnicode_IsDecimalDigit(value) != 0 or _PyUnicode_IsDigit(value) != 0 or _PyUnicode_IsNumeric(value) != 0,
        else => false,
    };
    return if (std.ascii.isUpper(code)) !found else found;
}

fn rangeCase(left: u32, right: u32, value: u32, flags: u32) bool {
    if (value >= left and value <= right) return true;
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
        .{ 0x345, 0x3b9, 0x1fbe, 0x345 },
        .{ 0x390, 0x1fd3, 0x390, 0x1fd3 },
        .{ 0x3b0, 0x1fe3, 0x3b0, 0x1fe3 },
        .{ 0x3b2, 0x3d0, 0x3b2, 0x3d0 },
        .{ 0x3b5, 0x3f5, 0x3b5, 0x3f5 },
        .{ 0x3b8, 0x3d1, 0x3b8, 0x3d1 },
        .{ 0x3ba, 0x3f0, 0x3ba, 0x3f0 },
        .{ 0x3c0, 0x3d6, 0x3c0, 0x3d6 },
        .{ 0x3c1, 0x3f1, 0x3c1, 0x3f1 },
        .{ 0x3c2, 0x3c3, 0x3c2, 0x3c3 },
        .{ 0x3c6, 0x3d5, 0x3c6, 0x3d5 },
        .{ 0x434, 0x1c81, 0x434, 0x1c81 },
        .{ 0x43e, 0x1c82, 0x43e, 0x1c82 },
        .{ 0x441, 0x1c83, 0x441, 0x1c83 },
        .{ 0x442, 0x1c84, 0x1c85, 0x442 },
        .{ 0x44a, 0x1c86, 0x44a, 0x1c86 },
        .{ 0x463, 0x1c87, 0x463, 0x1c87 },
        .{ 0xa64b, 0x1c88, 0xa64b, 0x1c88 },
        .{ 0x1e61, 0x1e9b, 0x1e61, 0x1e9b },
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
    for (program.ranges[class.range_start..@as(usize, class.range_start) + class.range_count]) |range| if (value >= range.left and value <= range.right) return true;
    if (class.categories != 0) {
        const codes = [_]u8{ 'd', 'D', 's', 'S', 'w', 'W' };
        for (codes) |code| if (class.categories & categoryBit(code) != 0 and category(code, value, flags)) return true;
    }
    return false;
}

fn classMatch(program: *const Program, class: *const CharClass, value: u32, flags: u32) bool {
    if (class.negative and class.locale_multi and flags & 6 == 6 and flags & text_pattern_flag == 0) {
        const lower: u32 = if (value >= 'A' and value <= 'Z') value + 32 else value;
        const upper: u32 = if (value >= 'a' and value <= 'z') value - 32 else value;
        return !classRaw(program, class, value, flags) or !classRaw(program, class, lower, flags) or !classRaw(program, class, upper, flags);
    }
    var found = classBit(class, value);
    if (!found and flags & 2 != 0) {
        const ascii_only = asciiMode(flags);
        const lower: u32 = if (ascii_only) (if (value >= 'A' and value <= 'Z') value + 32 else value) else _PyUnicode_ToLowercase(value);
        const upper: u32 = if (ascii_only) (if (value >= 'a' and value <= 'z') value - 32 else value) else if (multiUpper(value)) value else _PyUnicode_ToUppercase(value);
        const upper_lower: u32 = if (ascii_only or multiUpper(lower)) lower else _PyUnicode_ToUppercase(lower);
        found = classBit(class, lower) or classBit(class, upper) or classBit(class, upper_lower) or classBit(class, folded(value, ascii_only));
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
    for (program.ranges[class.range_start..@as(usize, class.range_start) + class.range_count]) |range| {
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

fn eval(program: *const Program, node_index: u16, text: Subject, endpos: usize, pos: usize, out: *Positions, depth: usize, flags: u32) void {
    if (depth > 512) return;
    switch (program.nodes[node_index]) {
        .empty => out.add(pos),
        .literal => |value| if (pos < endpos and equal(value, text.at(pos), flags)) out.add(pos + 1),
        .dot => if (pos < endpos and (flags & 16 != 0 or text.at(pos) != '\n')) out.add(pos + 1),
        .class => |index| if (pos < endpos and classMatch(program, &program.classes[index], text.at(pos), flags)) out.add(pos + 1),
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

const CompileError = error{ TooMuchCode, UnsupportedRepeat };

fn canBeEmpty(program: *const Program, index: u16) bool {
    return switch (program.nodes[index]) {
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
const Compiler = struct {
    program: *Program,
    flags: u32,

    fn emit(self: *Compiler, instruction: Instruction) CompileError!u16 {
        if (self.program.code_count >= max_code) return error.TooMuchCode;
        const index = self.program.code_count;
        self.program.code[index] = instruction;
        self.program.code_count += 1;
        return index;
    }

    fn node(self: *Compiler, index: u16) CompileError!void {
        switch (self.program.nodes[index]) {
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
                const split = try self.emit(.{ .op = .split });
                const first = self.program.code_count;
                try self.node(pair.left);
                const jump = try self.emit(.{ .op = .jump });
                const second = self.program.code_count;
                try self.node(pair.right);
                const finish = self.program.code_count;
                self.program.code[split].left = first;
                self.program.code[split].right = second;
                self.program.code[jump].left = finish;
            },
            .repeat => |repeat| {
                if (repeat.possessive) _ = try self.emit(.{ .op = .atomic_begin });
                if (repeat.minimum > 128 or (repeat.maximum != unbounded and repeat.maximum > 128)) return error.UnsupportedRepeat;
                for (0..repeat.minimum) |_| try self.node(repeat.child);
                if (repeat.maximum == unbounded) {
                    const guarded = canBeEmpty(self.program, repeat.child);
                    const split = try self.emit(.{ .op = .split });
                    const body = self.program.code_count;
                    try self.node(repeat.child);
                    _ = try self.emit(.{ .op = .jump, .left = split });
                    const finish = self.program.code_count;
                    self.program.code[split].left = if (repeat.lazy) finish else body;
                    self.program.code[split].right = if (repeat.lazy) body else finish;
                    if (guarded) {
                        self.program.code[split].value = finish;
                        self.program.nullable_loops = true;
                    }
                } else {
                    for (0..repeat.maximum - repeat.minimum) |_| {
                        const split = try self.emit(.{ .op = .split });
                        const body = self.program.code_count;
                        try self.node(repeat.child);
                        const finish = self.program.code_count;
                        self.program.code[split].left = if (repeat.lazy) finish else body;
                        self.program.code[split].right = if (repeat.lazy) body else finish;
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
                const yes = self.program.code_count;
                try self.node(conditional.yes);
                const jump = try self.emit(.{ .op = .jump });
                const no = self.program.code_count;
                try self.node(conditional.no);
                const finish = self.program.code_count;
                self.program.code[branch].left = yes;
                self.program.code[branch].right = no;
                self.program.code[jump].left = finish;
            },
            .atomic => |child| {
                _ = try self.emit(.{ .op = .atomic_begin });
                try self.node(child);
                _ = try self.emit(.{ .op = .atomic_end });
            },
            .look => |look| {
                const instruction = try self.emit(.{ .op = .look, .extra = look.width, .value = @as(u8, if (look.positive) 1 else 0) | @as(u8, if (look.behind) 2 else 0) });
                const entry = self.program.code_count;
                try self.node(look.child);
                _ = try self.emit(.{ .op = .accept });
                const finish = self.program.code_count;
                self.program.code[instruction].left = entry;
                self.program.code[instruction].right = finish;
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

fn addStarts(program: *const Program, index: u16, starts: *[256]u8, flags: u32) bool {
    return switch (program.nodes[index]) {
        .empty, .begin, .end, .absolute_begin, .absolute_end, .boundary => true,
        .literal => |value| blk: {
            if (value < 256) {
                const byte: u8 = @intCast(value);
                starts[value] = 1;
                if (flags & 2 != 0) {
                    starts[std.ascii.toLower(byte)] = 1;
                    starts[std.ascii.toUpper(byte)] = 1;
                }
            }
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
                if (classMatch(program, &program.classes[value], @intCast(raw), flags)) starts[raw] = 1;
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

fn scopedCategoryPrefix(program: *const Program, index: u16, switched: bool) ?u16 {
    return switch (program.nodes[index]) {
        .class => |class| if (switched and program.classes[class].categories != 0) class else null,
        .sequence => |pair| scopedCategoryPrefix(program, pair.left, switched),
        .group => |group| scopedCategoryPrefix(program, group.child, switched),
        .scoped => |scoped| scopedCategoryPrefix(program, scoped.child, switched or scoped.flags & (4 | 32 | 256) != program.flags & (4 | 32 | 256)),
        else => null,
    };
}

const Prefix = struct {
    empty: bool = false,
    first: [256]u8 = [_]u8{0} ** 256,
    single: [256]u8 = [_]u8{0} ** 256,
    pairs: [8192]u8 = [_]u8{0} ** 8192,
};

fn pairIndex(first: usize, second: usize) usize {
    return first * 256 + second;
}
fn hasPair(pairs: *const [8192]u8, first: usize, second: usize) bool {
    const index = pairIndex(first, second);
    return pairs[index >> 3] & (@as(u8, 1) << @intCast(index & 7)) != 0;
}
fn putPair(pairs: *[8192]u8, first: usize, second: usize) void {
    const index = pairIndex(first, second);
    pairs[index >> 3] |= @as(u8, 1) << @intCast(index & 7);
}

fn mergePrefix(target: *Prefix, other: *const Prefix) void {
    target.empty = target.empty or other.empty;
    for (0..256) |index| {
        target.first[index] |= other.first[index];
        target.single[index] |= other.single[index];
    }
    for (0..8192) |index| target.pairs[index] |= other.pairs[index];
}

fn joinPrefix(left: *const Prefix, right: *const Prefix) Prefix {
    var result = Prefix{ .empty = left.empty and right.empty };
    for (0..256) |first| {
        result.first[first] = left.first[first] | (if (left.empty) right.first[first] else 0);
        result.single[first] = (if (right.empty) left.single[first] else 0) | (if (left.empty) right.single[first] else 0);
        if (left.single[first] != 0) {
            for (0..256) |second| if (right.first[second] != 0) putPair(&result.pairs, first, second);
        }
    }
    for (0..8192) |index| result.pairs[index] |= left.pairs[index] | (if (left.empty) right.pairs[index] else 0);
    return result;
}

fn prefixes(program: *const Program, index: u16, flags: u32) Prefix {
    return switch (program.nodes[index]) {
        .empty, .begin, .end, .absolute_begin, .absolute_end, .boundary => Prefix{ .empty = true },
        .literal => |value| blk: {
            var result = Prefix{};
            if (value < 256) {
                const byte: u8 = @intCast(value);
                result.first[value] = 1;
                result.single[value] = 1;
                if (flags & 2 != 0) {
                    result.first[std.ascii.toLower(byte)] = 1;
                    result.first[std.ascii.toUpper(byte)] = 1;
                    result.single[std.ascii.toLower(byte)] = 1;
                    result.single[std.ascii.toUpper(byte)] = 1;
                }
            }
            break :blk result;
        },
        .dot => blk: {
            var result = Prefix{};
            for (0..256) |raw| if (flags & 16 != 0 or raw != '\n') {
                result.first[raw] = 1;
                result.single[raw] = 1;
            };
            break :blk result;
        },
        .class => |value| blk: {
            var result = Prefix{};
            for (0..256) |raw| if (classMatch(program, &program.classes[value], @intCast(raw), flags)) {
                result.first[raw] = 1;
                result.single[raw] = 1;
            };
            break :blk result;
        },
        .alternative => |pair| blk: {
            var result = prefixes(program, pair.left, flags);
            const right = prefixes(program, pair.right, flags);
            mergePrefix(&result, &right);
            break :blk result;
        },
        .sequence => |pair| blk: {
            const left = prefixes(program, pair.left, flags);
            const right = prefixes(program, pair.right, flags);
            break :blk joinPrefix(&left, &right);
        },
        .repeat => |repeat| blk: {
            const child = prefixes(program, repeat.child, flags);
            var current = Prefix{ .empty = true };
            for (0..repeat.minimum) |_| current = joinPrefix(&current, &child);
            var result = current;
            if (repeat.maximum > repeat.minimum) {
                current = joinPrefix(&current, &child);
                mergePrefix(&result, &current);
                if (repeat.maximum == unbounded or repeat.maximum > repeat.minimum + 1) {
                    current = joinPrefix(&current, &child);
                    mergePrefix(&result, &current);
                }
            }
            break :blk result;
        },
        .group => |group| prefixes(program, group.child, flags),
        .backref => blk: {
            var result = Prefix{ .empty = true };
            @memset(&result.first, 1);
            @memset(&result.single, 1);
            @memset(&result.pairs, 0xff);
            break :blk result;
        },
        .conditional => |conditional| blk: {
            var result = prefixes(program, conditional.yes, flags);
            const no = prefixes(program, conditional.no, flags);
            mergePrefix(&result, &no);
            break :blk result;
        },
        .atomic => |child| prefixes(program, child, flags),
        .look => Prefix{ .empty = true },
        .scoped => |scoped| prefixes(program, scoped.child, scoped.flags),
    };
}

const GuardUndo = struct { pc: u16, previous: isize };
const State = struct { pc: u16, pos: usize, atomic: usize };

fn runBytecode(program: *const Program, text: Subject, endpos: usize, start: usize, full: bool) isize {
    var stack_local: [max_stack]State = undefined;
    var stack: []State = &stack_local;
    var stack_heap: ?[]State = null;
    defer if (stack_heap) |items| std.heap.c_allocator.free(items);
    var marks_local: [max_stack]usize = undefined;
    var guard_marks: []usize = &marks_local;
    var marks_heap: ?[]usize = null;
    defer if (marks_heap) |items| std.heap.c_allocator.free(items);
    var stack_count: usize = 0;
    var atomic_stack: [256]usize = undefined;
    var atomic_depth: usize = 0;
    var guards: [max_code]isize = undefined;
    var guard_local: [max_stack]GuardUndo = undefined;
    var guard_undo: []GuardUndo = &guard_local;
    var guard_heap: ?[]GuardUndo = null;
    defer if (guard_heap) |items| std.heap.c_allocator.free(items);
    var guard_count: usize = 0;
    if (program.nullable_loops) @memset(&guards, -1);
    var pc: u16 = 0;
    var pos = start;
    while (true) {
        const instruction = program.code[pc];
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
            .class => if (pos < endpos and classMatch(program, &program.classes[instruction.left], text.at(pos), instruction.extra)) {
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
            .jump => {
                const target = program.code[instruction.left];
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
            .backref, .conditional, .look => return -2,
            .atomic_begin => {
                if (atomic_depth >= atomic_stack.len) return -2;
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
            .accept => if (!full or pos == endpos) return @intCast(pos),
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
    }
}

const CaptureState = struct { pc: u16, pos: usize, undo: usize, atomic: usize };
const Undo = struct { slot: u16, previous: isize, last: isize };

fn runCapturedAt(program: *const Program, text: Subject, endpos: usize, start: usize, entry: u16, full: bool, captures: *[max_groups * 2]isize, last: *isize, reset: bool, nonempty: bool) isize {
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
    var atomic_stack: [256]usize = undefined;
    var atomic_depth: usize = 0;
    var guards: [max_code]isize = undefined;
    var guard_local: [max_stack]GuardUndo = undefined;
    var guard_undo: []GuardUndo = &guard_local;
    var guard_heap: ?[]GuardUndo = null;
    defer if (guard_heap) |items| std.heap.c_allocator.free(items);
    var guard_count: usize = 0;
    if (program.nullable_loops) @memset(&guards, -1);
    if (reset) {
        @memset(captures, -1);
        last.* = -1;
    }
    var pc: u16 = entry;
    var pos = start;
    while (true) {
        const instruction = program.code[pc];
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
            .class => if (pos < endpos and classMatch(program, &program.classes[instruction.left], text.at(pos), instruction.extra)) {
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
            .jump => {
                const target = program.code[instruction.left];
                if (target.op == .split and target.value != 0 and guards[instruction.left] == @as(isize, @intCast(pos))) {
                    pc = @intCast(target.value);
                    continue;
                }
                pc = instruction.left;
                continue;
            },
            .save_begin, .save_end => {
                if (instruction.left == 0 or instruction.left > max_groups) return -2;
                if (undo_count >= undo.len) {
                    const capacity = std.math.mul(usize, undo.len, 2) catch return -2;
                    const grown = std.heap.c_allocator.alloc(Undo, capacity) catch return -2;
                    @memcpy(grown[0..undo_count], undo[0..undo_count]);
                    if (undo_heap) |items| std.heap.c_allocator.free(items);
                    undo_heap = grown;
                    undo = grown;
                }
                const slot: u16 = (instruction.left - 1) * 2 + (if (instruction.op == .save_end) @as(u16, 1) else @as(u16, 0));
                undo[undo_count] = .{ .slot = slot, .previous = captures[slot], .last = last.* };
                undo_count += 1;
                captures[slot] = @intCast(pos);
                if (instruction.op == .save_end) last.* = instruction.left;
                pc += 1;
                continue;
            },
            .backref => {
                if (instruction.left == 0 or instruction.left > program.groups) return -2;
                const base: usize = (instruction.left - 1) * 2;
                const begin = captures[base];
                const finish = captures[base + 1];
                if (begin >= 0 and finish >= begin) {
                    const width: usize = @intCast(finish - begin);
                    if (width <= endpos - pos) {
                        var matched = true;
                        for (0..width) |offset| {
                            if (!equal(text.at(@as(usize, @intCast(begin)) + offset), text.at(pos + offset), instruction.extra)) {
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
                const base: usize = (instruction.value - 1) * 2;
                pc = if (captures[base] >= 0 and captures[base + 1] >= captures[base]) instruction.left else instruction.right;
                continue;
            },
            .atomic_begin => {
                if (atomic_depth >= atomic_stack.len) return -2;
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
                const begin: ?usize = if (behind) (if (pos < instruction.extra) null else pos - instruction.extra) else pos;
                var looked = captures.*;
                var look_last = last.*;
                const result = if (begin) |value| runCapturedAt(program, text, if (behind) pos else endpos, value, instruction.left, behind, &looked, &look_last, false, false) else -1;
                if (result == -2) return -2;
                const found = result >= 0;
                if (found == positive) {
                    if (positive) {
                        for (0..program.groups * 2) |slot| {
                            if (captures[slot] != looked[slot]) {
                                if (undo_count >= undo.len) {
                                    const capacity = std.math.mul(usize, undo.len, 2) catch return -2;
                                    const grown = std.heap.c_allocator.alloc(Undo, capacity) catch return -2;
                                    @memcpy(grown[0..undo_count], undo[0..undo_count]);
                                    if (undo_heap) |items| std.heap.c_allocator.free(items);
                                    undo_heap = grown;
                                    undo = grown;
                                }
                                undo[undo_count] = .{ .slot = @intCast(slot), .previous = captures[slot], .last = last.* };
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
            captures[item.slot] = item.previous;
            last.* = item.last;
        }
        pc = state.pc;
        pos = state.pos;
        atomic_depth = state.atomic;
    }
}

fn runCaptured(program: *const Program, text: Subject, endpos: usize, start: usize, full: bool, captures: *[max_groups * 2]isize, last: *isize, nonempty: bool) isize {
    return runCapturedAt(program, text, endpos, start, 0, full, captures, last, true, nonempty);
}

pub export fn rebar_zig_compile(pattern: [*]const u8, length: usize, flags: u32) ?*Program {
    const program = std.heap.c_allocator.create(Program) catch return null;
    program.* = Program{ .flags = flags };
    var parser = Parser{ .source = pattern[0..length], .program = program };
    program.root = parser.alternative() catch {
        std.heap.c_allocator.destroy(program);
        return null;
    };
    if (parser.at != parser.source.len) {
        std.heap.c_allocator.destroy(program);
        return null;
    }
    for (program.nodes[0..program.node_count]) |node| {
        switch (node) {
            .conditional => |conditional| if (conditional.number > program.groups) {
                std.heap.c_allocator.destroy(program);
                return null;
            },
            else => {},
        }
    }
    var compiler = Compiler{ .program = program, .flags = program.flags };
    compiler.node(program.root) catch {
        std.heap.c_allocator.destroy(program);
        return null;
    };
    _ = compiler.emit(.{ .op = .accept }) catch {
        std.heap.c_allocator.destroy(program);
        return null;
    };
    program.nullable = addStarts(program, program.root, &program.starts, program.flags);
    if (!program.nullable) {
        if (scopedCategoryPrefix(program, program.root, false)) |class| program.scoped_prefix = class;
    }
    if (program.node_count <= 20) {
        const start_prefix = prefixes(program, program.root, program.flags);
        program.single = start_prefix.single;
        program.pairs = start_prefix.pairs;
    } else {
        program.single = [_]u8{1} ** 256;
    }
    return program;
}

pub export fn rebar_zig_free(program: ?*Program) void {
    if (program) |value| std.heap.c_allocator.destroy(value);
}
pub export fn rebar_zig_program_size() usize {
    return @sizeOf(Program);
}
pub export fn rebar_zig_groups(program: ?*const Program) usize {
    return if (program) |value| value.groups else 0;
}

pub export fn rebar_zig_flags(program: ?*const Program) u32 {
    return if (program) |value| value.flags & ~text_pattern_flag else 0;
}

pub export fn rebar_zig_name_count(program: ?*const Program) usize {
    return if (program) |value| value.name_count else 0;
}

pub export fn rebar_zig_name_length(program: ?*const Program, index: usize) usize {
    const value = program orelse return 0;
    return if (index < value.name_count) value.names[index].length else 0;
}

pub export fn rebar_zig_name_group(program: ?*const Program, index: usize) usize {
    const value = program orelse return 0;
    return if (index < value.name_count) value.names[index].group else 0;
}

pub export fn rebar_zig_name_copy(program: ?*const Program, index: usize, output: [*]u8, length: usize) usize {
    const value = program orelse return 0;
    if (index >= value.name_count) return 0;
    const count = @min(length, value.names[index].length);
    @memcpy(output[0..count], value.names[index].bytes[0..count]);
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
    const program = program_value orelse return -1;
    if (kind != 1 and kind != 2 and kind != 4) return -1;
    const endpos = @min(length, endpos_value);
    if (pos > endpos) return 0;
    const text = Subject{ .data = text_value, .length = length, .kind = kind };
    if (program.references) {
        var begins: [max_groups + 1]isize = undefined;
        var ends: [max_groups + 1]isize = undefined;
        var last: isize = -1;
        const result = rebar_zig_match_captures_wide(program_value, text_value, length, kind, pos, endpos_value, mode, 0, &begins, &ends, &last);
        if (result == 1) {
            begin.* = begins[0];
            finish.* = ends[0];
        }
        return result;
    }
    const last = if (mode == 0) endpos else pos;
    var start = pos;
    while (start <= last) : (start += 1) {
        if (mode == 0 and !program.nullable and start < endpos) {
            const first = text.at(start);
            if (first < 256 and program.starts[first] == 0) continue;
            if (program.scoped_prefix != std.math.maxInt(u16) and !classMatch(program, &program.classes[program.scoped_prefix], first, program.flags)) continue;
            if (first < 256 and start + 1 < endpos) {
                const second = text.at(start + 1);
                if (second < 256 and program.single[first] == 0 and !hasPair(&program.pairs, first, second)) continue;
            }
        }
        const found = runBytecode(program, text, endpos, start, mode == 2);
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
    const final_start = if (mode == 0) endpos else pos;
    var start = pos;
    var captures: [max_groups * 2]isize = undefined;
    while (start <= final_start) : (start += 1) {
        if (mode == 0 and !program.nullable and start < endpos) {
            const first = text.at(start);
            if (first < 256 and program.starts[first] == 0) continue;
            if (program.scoped_prefix != std.math.maxInt(u16) and !classMatch(program, &program.classes[program.scoped_prefix], first, program.flags)) continue;
            if (first < 256 and start + 1 < endpos) {
                const second = text.at(start + 1);
                if (second < 256 and program.single[first] == 0 and !hasPair(&program.pairs, first, second)) continue;
            }
        }
        const finish = runCaptured(program, text, endpos, start, mode == 2, &captures, last, nonempty != 0 and start == pos);
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

pub export fn rebar_zig_collect_captures(program_value: ?*const Program, text_value: [*]const u8, length: usize, pos: usize, endpos_value: usize, capacity: usize, begins: [*]isize, ends: [*]isize, lasts: [*]isize) isize {
    const program = program_value orelse return -1;
    const endpos = @min(length, endpos_value);
    if (pos > endpos) return 0;
    if (capacity > std.math.maxInt(isize)) return -1;

    const stride = program.groups + 1;
    var current = pos;
    var nonempty: u8 = 0;
    var count: usize = 0;
    while (current <= endpos and count < capacity) {
        const base = count * stride;
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
    const groups = program.groups + 1;
    const width = groups * 2 + 1;
    var current = cursor.*;
    var nonempty = retry_nonempty.*;
    var count: usize = 0;
    while (current <= endpos and count < capacity) {
        const base = count * width;
        const begins = records + base;
        const ends = begins + groups;
        const last = ends + groups;
        const matched = rebar_zig_match_captures_wide(program, text_value, length, kind, current, endpos, 0, nonempty, begins, ends, &last[0]);
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
