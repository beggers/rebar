const std = @import("std");

const max_nodes = 4096;
const max_classes = 128;
const max_positions = 512;
const max_code = 16384;
const max_stack = 8192;
const max_groups = 128;
const max_undo = 65536;
const unbounded = std.math.maxInt(usize);

const Pair = struct { left: u16, right: u16 };
const Repeat = struct { child: u16, minimum: usize, maximum: usize, lazy: bool };
const Group = struct { child: u16, number: u16 };
const Node = union(enum) {
    empty,
    literal: u8,
    dot,
    class: u16,
    begin,
    end,
    boundary: bool,
    sequence: Pair,
    alternative: Pair,
    repeat: Repeat,
    group: Group,
};
const CharClass = struct { bits: [32]u8 = [_]u8{0} ** 32, negative: bool = false };
const Op = enum(u8) { literal, dot, class, begin, end, boundary, split, jump, save_begin, save_end, accept };
const Instruction = struct { op: Op, left: u16 = 0, right: u16 = 0, value: u8 = 0 };
const Program = struct {
    nodes: [max_nodes]Node = undefined,
    node_count: u16 = 0,
    classes: [max_classes]CharClass = undefined,
    class_count: u16 = 0,
    root: u16 = 0,
    flags: u32 = 0,
    code: [max_code]Instruction = undefined,
    code_count: u16 = 0,
    starts: [256]u8 = [_]u8{0} ** 256,
    single: [256]u8 = [_]u8{0} ** 256,
    pairs: [8192]u8 = [_]u8{0} ** 8192,
    nullable: bool = false,
    groups: u16 = 0,
};

const ParseError = error{ TooManyNodes, TooManyClasses, InvalidPattern, Unsupported };
const Parser = struct {
    source: []const u8,
    at: usize = 0,
    program: *Program,

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

    fn category(self: *Parser, code: u8) ParseError!u16 {
        if (self.program.class_count >= max_classes) return error.TooManyClasses;
        const index = self.program.class_count;
        self.program.class_count += 1;
        var class = CharClass{};
        const lower = std.ascii.toLower(code);
        for (0..256) |raw| {
            const value: u8 = @intCast(raw);
            const found = switch (lower) {
                'd' => value >= '0' and value <= '9',
                's' => value == ' ' or value == '\t' or value == '\n' or value == '\r' or value == 11 or value == 12,
                'w' => std.ascii.isAlphanumeric(value) or value == '_',
                else => false,
            };
            if (found) setBit(&class, value);
        }
        class.negative = std.ascii.isUpper(code);
        self.program.classes[index] = class;
        return self.add(.{ .class = index });
    }

    fn parseClass(self: *Parser) ParseError!u16 {
        if (self.program.class_count >= max_classes) return error.TooManyClasses;
        const index = self.program.class_count;
        self.program.class_count += 1;
        var class = CharClass{};
        if (self.at < self.source.len and self.source[self.at] == '^') {
            class.negative = true;
            self.at += 1;
        }
        var first = true;
        while (self.at < self.source.len) {
            if (self.source[self.at] == ']' and !first) {
                self.at += 1;
                self.program.classes[index] = class;
                return self.add(.{ .class = index });
            }
            first = false;
            var left = self.source[self.at];
            self.at += 1;
            if (left == '\\') {
                if (self.at >= self.source.len) return error.InvalidPattern;
                left = self.source[self.at];
                self.at += 1;
                if (left == 'd' or left == 'D' or left == 's' or left == 'S' or left == 'w' or left == 'W') {
                    const lower = std.ascii.toLower(left);
                    for (0..256) |raw| {
                        const value: u8 = @intCast(raw);
                        const found = switch (lower) {
                            'd' => value >= '0' and value <= '9',
                            's' => value == ' ' or value == '\t' or value == '\n' or value == '\r' or value == 11 or value == 12,
                            else => std.ascii.isAlphanumeric(value) or value == '_',
                        };
                        if (found != std.ascii.isUpper(left)) setBit(&class, value);
                    }
                    continue;
                }
                left = switch (left) {
                    'n' => '\n',
                    'r' => '\r',
                    't' => '\t',
                    else => left,
                };
            }
            if (self.at + 1 < self.source.len and self.source[self.at] == '-' and self.source[self.at + 1] != ']') {
                self.at += 1;
                var right = self.source[self.at];
                self.at += 1;
                if (right == '\\') {
                    if (self.at >= self.source.len) return error.InvalidPattern;
                    right = self.source[self.at];
                    self.at += 1;
                }
                if (right < left) return error.InvalidPattern;
                for (@as(usize, left)..@as(usize, right) + 1) |raw| setBit(&class, @intCast(raw));
            } else setBit(&class, left);
        }
        return error.InvalidPattern;
    }

    fn atom(self: *Parser) ParseError!u16 {
        if (self.at >= self.source.len) return error.InvalidPattern;
        const value = self.source[self.at];
        self.at += 1;
        return switch (value) {
            '.' => self.add(.dot),
            '^' => self.add(.begin),
            '$' => self.add(.end),
            '[' => self.parseClass(),
            '(' => blk: {
                var capturing = true;
                if (self.at < self.source.len and self.source[self.at] == '?') {
                    if (self.at + 1 >= self.source.len or self.source[self.at + 1] != ':') return error.Unsupported;
                    self.at += 2;
                    capturing = false;
                }
                var group_number: u16 = 0;
                if (capturing) {
                    if (self.program.groups >= max_groups) return error.Unsupported;
                    self.program.groups += 1;
                    group_number = self.program.groups;
                }
                const child = try self.alternative();
                if (self.at >= self.source.len or self.source[self.at] != ')') return error.InvalidPattern;
                self.at += 1;
                break :blk if (capturing) try self.add(.{ .group = .{ .child = child, .number = group_number } }) else child;
            },
            '\\' => blk: {
                if (self.at >= self.source.len) return error.InvalidPattern;
                const code = self.source[self.at];
                self.at += 1;
                if (code == 'd' or code == 'D' or code == 's' or code == 'S' or code == 'w' or code == 'W') break :blk self.category(code);
                if (code == 'A') break :blk self.add(.begin);
                if (code == 'Z' or code == 'z') break :blk self.add(.end);
                if (code == 'b' or code == 'B') break :blk self.add(.{ .boundary = code == 'b' });
                break :blk self.add(.{ .literal = switch (code) {
                    'n' => '\n',
                    'r' => '\r',
                    't' => '\t',
                    else => code,
                } });
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

    fn repeated(self: *Parser) ParseError!u16 {
        const child = try self.atom();
        if (self.at >= self.source.len) return child;
        const mark = self.source[self.at];
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
        if (self.at < self.source.len and self.source[self.at] == '?') {
            lazy = true;
            self.at += 1;
        }
        if (self.at < self.source.len and self.source[self.at] == '+') return error.Unsupported;
        return self.add(.{ .repeat = .{ .child = child, .minimum = minimum, .maximum = maximum, .lazy = lazy } });
    }

    fn sequence(self: *Parser) ParseError!u16 {
        var value: ?u16 = null;
        while (self.at < self.source.len and self.source[self.at] != '|' and self.source[self.at] != ')') {
            const next = try self.repeated();
            value = if (value) |left| try self.add(.{ .sequence = .{ .left = left, .right = next } }) else next;
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

fn equal(left: u8, right: u8, flags: u32) bool {
    if (flags & 2 == 0) return left == right;
    return std.ascii.toLower(left) == std.ascii.toLower(right);
}

fn classMatch(class: CharClass, value: u8, flags: u32) bool {
    var found = class.bits[value >> 3] & (@as(u8, 1) << @intCast(value & 7)) != 0;
    if (!found and flags & 2 != 0) {
        const other = if (std.ascii.isLower(value)) std.ascii.toUpper(value) else std.ascii.toLower(value);
        found = class.bits[other >> 3] & (@as(u8, 1) << @intCast(other & 7)) != 0;
    }
    return if (class.negative) !found else found;
}

fn word(value: u8) bool {
    return std.ascii.isAlphanumeric(value) or value == '_';
}

fn repeatWalk(program: *const Program, repeat: Repeat, text: []const u8, endpos: usize, pos: usize, count: usize, maximum: usize, out: *Positions, depth: usize) void {
    if (depth > 512) return;
    if (repeat.lazy and count >= repeat.minimum) out.add(pos);
    if (count < maximum) {
        var next = Positions{};
        eval(program, repeat.child, text, endpos, pos, &next, depth + 1);
        for (next.values[0..next.count]) |value| {
            if (value == pos) {
                if (count + 1 >= repeat.minimum) out.add(value);
                continue;
            }
            repeatWalk(program, repeat, text, endpos, value, count + 1, maximum, out, depth + 1);
        }
    }
    if (!repeat.lazy and count >= repeat.minimum) out.add(pos);
}

fn eval(program: *const Program, node_index: u16, text: []const u8, endpos: usize, pos: usize, out: *Positions, depth: usize) void {
    if (depth > 512) return;
    switch (program.nodes[node_index]) {
        .empty => out.add(pos),
        .literal => |value| if (pos < endpos and equal(value, text[pos], program.flags)) out.add(pos + 1),
        .dot => if (pos < endpos and (program.flags & 16 != 0 or text[pos] != '\n')) out.add(pos + 1),
        .class => |index| if (pos < endpos and classMatch(program.classes[index], text[pos], program.flags)) out.add(pos + 1),
        .begin => if (pos == 0 or (program.flags & 8 != 0 and pos > 0 and text[pos - 1] == '\n')) out.add(pos),
        .end => if (pos == endpos or (pos + 1 == endpos and text[pos] == '\n') or (program.flags & 8 != 0 and pos < endpos and text[pos] == '\n')) out.add(pos),
        .boundary => |want| {
            const left = pos > 0 and word(text[pos - 1]);
            const right = pos < endpos and word(text[pos]);
            if ((left != right) == want) out.add(pos);
        },
        .alternative => |pair| {
            eval(program, pair.left, text, endpos, pos, out, depth + 1);
            eval(program, pair.right, text, endpos, pos, out, depth + 1);
        },
        .sequence => |pair| {
            var left = Positions{};
            eval(program, pair.left, text, endpos, pos, &left, depth + 1);
            for (left.values[0..left.count]) |value| eval(program, pair.right, text, endpos, value, out, depth + 1);
        },
        .repeat => |repeat| {
            var maximum = repeat.maximum;
            if (maximum == unbounded or maximum > endpos - pos + repeat.minimum + 1) maximum = endpos - pos + repeat.minimum + 1;
            repeatWalk(program, repeat, text, endpos, pos, 0, maximum, out, depth + 1);
        },
        .group => |group| eval(program, group.child, text, endpos, pos, out, depth + 1),
    }
}

const CompileError = error{ TooMuchCode, UnsupportedRepeat };
const Compiler = struct {
    program: *Program,

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
                _ = try self.emit(.{ .op = .literal, .value = value });
            },
            .dot => {
                _ = try self.emit(.{ .op = .dot });
            },
            .class => |value| {
                _ = try self.emit(.{ .op = .class, .left = value });
            },
            .begin => {
                _ = try self.emit(.{ .op = .begin });
            },
            .end => {
                _ = try self.emit(.{ .op = .end });
            },
            .boundary => |want| {
                _ = try self.emit(.{ .op = .boundary, .value = if (want) 1 else 0 });
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
                if (repeat.minimum > 128 or (repeat.maximum != unbounded and repeat.maximum > 128)) return error.UnsupportedRepeat;
                for (0..repeat.minimum) |_| try self.node(repeat.child);
                if (repeat.maximum == unbounded) {
                    const split = try self.emit(.{ .op = .split });
                    const body = self.program.code_count;
                    try self.node(repeat.child);
                    _ = try self.emit(.{ .op = .jump, .left = split });
                    const finish = self.program.code_count;
                    self.program.code[split].left = if (repeat.lazy) finish else body;
                    self.program.code[split].right = if (repeat.lazy) body else finish;
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
            },
            .group => |group| {
                _ = try self.emit(.{ .op = .save_begin, .left = group.number });
                try self.node(group.child);
                _ = try self.emit(.{ .op = .save_end, .left = group.number });
            },
        }
    }
};

fn addStarts(program: *const Program, index: u16, starts: *[256]u8) bool {
    return switch (program.nodes[index]) {
        .empty, .begin, .end, .boundary => true,
        .literal => |value| blk: {
            starts[value] = 1;
            if (program.flags & 2 != 0) {
                starts[std.ascii.toLower(value)] = 1;
                starts[std.ascii.toUpper(value)] = 1;
            }
            break :blk false;
        },
        .dot => blk: {
            for (0..256) |raw| {
                if (program.flags & 16 != 0 or raw != '\n') starts[raw] = 1;
            }
            break :blk false;
        },
        .class => |value| blk: {
            for (0..256) |raw| {
                if (classMatch(program.classes[value], @intCast(raw), program.flags)) starts[raw] = 1;
            }
            break :blk false;
        },
        .alternative => |pair| blk: {
            const left_empty = addStarts(program, pair.left, starts);
            const right_empty = addStarts(program, pair.right, starts);
            break :blk left_empty or right_empty;
        },
        .sequence => |pair| blk: {
            const left_empty = addStarts(program, pair.left, starts);
            if (!left_empty) break :blk false;
            break :blk addStarts(program, pair.right, starts);
        },
        .repeat => |repeat| blk: {
            const child_empty = addStarts(program, repeat.child, starts);
            break :blk repeat.minimum == 0 or child_empty;
        },
        .group => |group| addStarts(program, group.child, starts),
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

fn prefixes(program: *const Program, index: u16) Prefix {
    return switch (program.nodes[index]) {
        .empty, .begin, .end, .boundary => Prefix{ .empty = true },
        .literal => |value| blk: {
            var result = Prefix{};
            result.first[value] = 1;
            result.single[value] = 1;
            if (program.flags & 2 != 0) {
                result.first[std.ascii.toLower(value)] = 1;
                result.first[std.ascii.toUpper(value)] = 1;
                result.single[std.ascii.toLower(value)] = 1;
                result.single[std.ascii.toUpper(value)] = 1;
            }
            break :blk result;
        },
        .dot => blk: {
            var result = Prefix{};
            for (0..256) |raw| if (program.flags & 16 != 0 or raw != '\n') {
                result.first[raw] = 1;
                result.single[raw] = 1;
            };
            break :blk result;
        },
        .class => |value| blk: {
            var result = Prefix{};
            for (0..256) |raw| if (classMatch(program.classes[value], @intCast(raw), program.flags)) {
                result.first[raw] = 1;
                result.single[raw] = 1;
            };
            break :blk result;
        },
        .alternative => |pair| blk: {
            var result = prefixes(program, pair.left);
            const right = prefixes(program, pair.right);
            mergePrefix(&result, &right);
            break :blk result;
        },
        .sequence => |pair| blk: {
            const left = prefixes(program, pair.left);
            const right = prefixes(program, pair.right);
            break :blk joinPrefix(&left, &right);
        },
        .repeat => |repeat| blk: {
            const child = prefixes(program, repeat.child);
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
        .group => |group| prefixes(program, group.child),
    };
}

const State = struct { pc: u16, pos: usize };

fn runBytecode(program: *const Program, text: []const u8, endpos: usize, start: usize, full: bool) isize {
    var stack: [max_stack]State = undefined;
    var stack_count: usize = 0;
    var pc: u16 = 0;
    var pos = start;
    while (true) {
        const instruction = program.code[pc];
        switch (instruction.op) {
            .literal => if (pos < endpos and equal(instruction.value, text[pos], program.flags)) {
                pos += 1;
                pc += 1;
                continue;
            },
            .dot => if (pos < endpos and (program.flags & 16 != 0 or text[pos] != '\n')) {
                pos += 1;
                pc += 1;
                continue;
            },
            .class => if (pos < endpos and classMatch(program.classes[instruction.left], text[pos], program.flags)) {
                pos += 1;
                pc += 1;
                continue;
            },
            .begin => if (pos == 0 or (program.flags & 8 != 0 and pos > 0 and text[pos - 1] == '\n')) {
                pc += 1;
                continue;
            },
            .end => if (pos == endpos or (pos + 1 == endpos and text[pos] == '\n') or (program.flags & 8 != 0 and pos < endpos and text[pos] == '\n')) {
                pc += 1;
                continue;
            },
            .boundary => {
                const left = pos > 0 and word(text[pos - 1]);
                const right = pos < endpos and word(text[pos]);
                if ((left != right) == (instruction.value != 0)) {
                    pc += 1;
                    continue;
                }
            },
            .split => {
                if (stack_count >= max_stack) return -2;
                stack[stack_count] = .{ .pc = instruction.right, .pos = pos };
                stack_count += 1;
                pc = instruction.left;
                continue;
            },
            .jump => {
                pc = instruction.left;
                continue;
            },
            .save_begin, .save_end => {
                pc += 1;
                continue;
            },
            .accept => if (!full or pos == endpos) return @intCast(pos),
        }
        if (stack_count == 0) return -1;
        stack_count -= 1;
        pc = stack[stack_count].pc;
        pos = stack[stack_count].pos;
    }
}

const CaptureState = struct { pc: u16, pos: usize, undo: usize };
const Undo = struct { slot: u16, previous: isize, last: isize };

fn runCaptured(program: *const Program, text: []const u8, endpos: usize, start: usize, full: bool, captures: *[max_groups * 2]isize, last: *isize) isize {
    var stack: [max_stack]CaptureState = undefined;
    var stack_count: usize = 0;
    var undo: [max_undo]Undo = undefined;
    var undo_count: usize = 0;
    @memset(captures, -1);
    last.* = -1;
    var pc: u16 = 0;
    var pos = start;
    while (true) {
        const instruction = program.code[pc];
        switch (instruction.op) {
            .literal => if (pos < endpos and equal(instruction.value, text[pos], program.flags)) {
                pos += 1;
                pc += 1;
                continue;
            },
            .dot => if (pos < endpos and (program.flags & 16 != 0 or text[pos] != '\n')) {
                pos += 1;
                pc += 1;
                continue;
            },
            .class => if (pos < endpos and classMatch(program.classes[instruction.left], text[pos], program.flags)) {
                pos += 1;
                pc += 1;
                continue;
            },
            .begin => if (pos == 0 or (program.flags & 8 != 0 and pos > 0 and text[pos - 1] == '\n')) {
                pc += 1;
                continue;
            },
            .end => if (pos == endpos or (pos + 1 == endpos and text[pos] == '\n') or (program.flags & 8 != 0 and pos < endpos and text[pos] == '\n')) {
                pc += 1;
                continue;
            },
            .boundary => {
                const left = pos > 0 and word(text[pos - 1]);
                const right = pos < endpos and word(text[pos]);
                if ((left != right) == (instruction.value != 0)) {
                    pc += 1;
                    continue;
                }
            },
            .split => {
                if (stack_count >= max_stack) return -2;
                stack[stack_count] = .{ .pc = instruction.right, .pos = pos, .undo = undo_count };
                stack_count += 1;
                pc = instruction.left;
                continue;
            },
            .jump => {
                pc = instruction.left;
                continue;
            },
            .save_begin, .save_end => {
                if (undo_count >= max_undo or instruction.left == 0 or instruction.left > max_groups) return -2;
                const slot: u16 = (instruction.left - 1) * 2 + (if (instruction.op == .save_end) @as(u16, 1) else @as(u16, 0));
                undo[undo_count] = .{ .slot = slot, .previous = captures[slot], .last = last.* };
                undo_count += 1;
                captures[slot] = @intCast(pos);
                if (instruction.op == .save_end) last.* = instruction.left;
                pc += 1;
                continue;
            },
            .accept => if (!full or pos == endpos) return @intCast(pos),
        }
        if (stack_count == 0) return -1;
        stack_count -= 1;
        const state = stack[stack_count];
        while (undo_count > state.undo) {
            undo_count -= 1;
            const item = undo[undo_count];
            captures[item.slot] = item.previous;
            last.* = item.last;
        }
        pc = state.pc;
        pos = state.pos;
    }
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
    var compiler = Compiler{ .program = program };
    compiler.node(program.root) catch {
        std.heap.c_allocator.destroy(program);
        return null;
    };
    _ = compiler.emit(.{ .op = .accept }) catch {
        std.heap.c_allocator.destroy(program);
        return null;
    };
    program.nullable = addStarts(program, program.root, &program.starts);
    const start_prefix = prefixes(program, program.root);
    program.single = start_prefix.single;
    program.pairs = start_prefix.pairs;
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

pub export fn rebar_zig_match_tree(program_value: ?*const Program, text_value: [*]const u8, length: usize, pos: usize, endpos_value: usize, mode: u8, begin: *isize, finish: *isize) c_int {
    const program = program_value orelse return -1;
    const endpos = @min(length, endpos_value);
    if (pos > endpos) return 0;
    const text = text_value[0..length];
    const last = if (mode == 0) endpos else pos;
    var start = pos;
    while (start <= last) : (start += 1) {
        var out = Positions{};
        eval(program, program.root, text, endpos, start, &out, 0);
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
    const program = program_value orelse return -1;
    const endpos = @min(length, endpos_value);
    if (pos > endpos) return 0;
    const text = text_value[0..length];
    const last = if (mode == 0) endpos else pos;
    var start = pos;
    while (start <= last) : (start += 1) {
        if (mode == 0 and !program.nullable and start < endpos and program.starts[text[start]] == 0) continue;
        if (mode == 0 and !program.nullable and start + 1 < endpos and program.single[text[start]] == 0 and !hasPair(&program.pairs, text[start], text[start + 1])) continue;
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

pub export fn rebar_zig_match_captures(program_value: ?*const Program, text_value: [*]const u8, length: usize, pos: usize, endpos_value: usize, mode: u8, begins: [*]isize, ends: [*]isize, last: *isize) c_int {
    const program = program_value orelse return -1;
    const endpos = @min(length, endpos_value);
    if (pos > endpos) return 0;
    const text = text_value[0..length];
    const final_start = if (mode == 0) endpos else pos;
    var start = pos;
    var captures: [max_groups * 2]isize = undefined;
    while (start <= final_start) : (start += 1) {
        if (mode == 0 and !program.nullable and start < endpos and program.starts[text[start]] == 0) continue;
        if (mode == 0 and !program.nullable and start + 1 < endpos and program.single[text[start]] == 0 and !hasPair(&program.pairs, text[start], text[start + 1])) continue;
        const finish = runCaptured(program, text, endpos, start, mode == 2, &captures, last);
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
