#include "engine.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <limits>
#include <memory>
#include <utility>

namespace rebar_cpp {

CompileError::CompileError(std::string message, std::size_t position)
    : std::runtime_error(std::move(message)), position_(position) {}

std::size_t CompileError::position() const noexcept { return position_; }

Interrupted::Interrupted() : std::runtime_error("regular-expression execution interrupted") {}

char32_t Subject::read(std::size_t offset) const noexcept {
    if (kind == 1) {
        return static_cast<const std::uint8_t*>(data)[offset];
    }
    if (kind == 2) {
        return static_cast<const std::uint16_t*>(data)[offset];
    }
    return static_cast<const std::uint32_t*>(data)[offset];
}

bool Capture::matched() const noexcept {
    return first != no_position && last != no_position;
}

namespace {

struct Token {
    char32_t value = U'\0';
    std::size_t position = 0;
    bool escaped = false;
    bool end = false;
};

bool ascii_letter(char32_t value) noexcept {
    return (value >= U'a' && value <= U'z') ||
           (value >= U'A' && value <= U'Z');
}

bool ascii_digit(char32_t value) noexcept {
    return value >= U'0' && value <= U'9';
}

bool ascii_identifier_start(char32_t value) noexcept {
    return ascii_letter(value) || value == U'_';
}

bool ascii_identifier_part(char32_t value) noexcept {
    return ascii_identifier_start(value) || ascii_digit(value);
}

bool verbose_space(char32_t value) noexcept {
    return value == U' ' || value == U'\t' || value == U'\n' ||
           value == U'\r' || value == U'\v' || value == U'\f';
}

std::string ascii_display(char32_t value) {
    if (value <= 0x7f) {
        return std::string(1, static_cast<char>(value));
    }
    return "?";
}

std::string ascii_name(std::u32string_view value) {
    std::string result;
    result.reserve(value.size());
    for (char32_t item : value) {
        result.push_back(item <= 0x7f ? static_cast<char>(item) : '?');
    }
    return result;
}

class Lexer final {
public:
    explicit Lexer(const std::u32string& source) : source_(source) {}

    [[nodiscard]] std::size_t position() const noexcept { return position_; }
    [[nodiscard]] std::size_t size() const noexcept { return source_.size(); }

    void reset(std::size_t position) noexcept { position_ = position; }

    [[nodiscard]] char32_t raw(std::size_t offset = 0) const noexcept {
        const std::size_t index = position_ + offset;
        return index < source_.size() ? source_[index] : U'\0';
    }

    char32_t take_raw() {
        if (position_ == source_.size()) {
            throw CompileError("unexpected end of pattern", position_);
        }
        return source_[position_++];
    }

    [[nodiscard]] Token peek(std::uint32_t flags) {
        skip_ignored(flags);
        const std::size_t saved = position_;
        const Token token = raw_token();
        position_ = saved;
        return token;
    }

    Token next(std::uint32_t flags) {
        skip_ignored(flags);
        return raw_token();
    }

private:
    Token raw_token() {
        if (position_ >= source_.size()) {
            return Token{U'\0', position_, false, true};
        }
        const std::size_t begin = position_;
        const char32_t first = source_[position_++];
        if (first != U'\\') {
            return Token{first, begin, false, false};
        }
        if (position_ >= source_.size()) {
            throw CompileError("bad escape (end of pattern)", begin);
        }
        return Token{source_[position_++], begin, true, false};
    }

    void skip_ignored(std::uint32_t flags) {
        if ((flags & flag_verbose) == 0) {
            return;
        }
        while (position_ < source_.size()) {
            const char32_t value = source_[position_];
            if (verbose_space(value)) {
                ++position_;
                continue;
            }
            if (value != U'#') {
                break;
            }
            ++position_;
            while (position_ < source_.size()) {
                const Token comment_token = raw_token();
                if (!comment_token.escaped && comment_token.value == U'\n') {
                    break;
                }
            }
        }
    }

    const std::u32string& source_;
    std::size_t position_ = 0;
};

enum class NodeKind : std::uint8_t {
    empty,
    literal,
    dot,
    character_class,
    begin_line,
    end_line,
    begin_subject,
    end_subject,
    word_boundary,
    not_word_boundary,
    sequence,
    alternation,
    capture,
    backreference,
    repeat,
    assert_ahead,
    assert_not_ahead,
    assert_behind,
    assert_not_behind,
    atomic,
    conditional,
};

struct Node {
    NodeKind kind = NodeKind::empty;
    std::vector<Node> children;
    char32_t character = U'\0';
    std::size_t index = 0;
    std::size_t minimum = 0;
    std::size_t maximum = no_position;
    std::uint32_t flags = 0;
    bool lazy = false;
    bool possessive = false;
    std::size_t position = 0;
};

struct Width {
    std::size_t minimum = 0;
    std::size_t maximum = 0;
};

std::size_t saturating_add(std::size_t first, std::size_t second) noexcept {
    if (first == no_position || second == no_position ||
        first > no_position - second) {
        return no_position;
    }
    return first + second;
}

std::size_t saturating_multiply(std::size_t first, std::size_t second) noexcept {
    if (first == 0 || second == 0) {
        return 0;
    }
    if (first == no_position || second == no_position ||
        first > no_position / second) {
        return no_position;
    }
    return first * second;
}

class Parser final {
public:
    Parser(Program& program, const std::u32string& source)
        : program_(program), lexer_(source) {}

    [[nodiscard]] Node parse() {
        std::uint32_t flags = program_.flags;
        Node root = alternation(flags);
        const Token remaining = lexer_.peek(flags);
        if (!remaining.end) {
            if (!remaining.escaped && remaining.value == U')') {
                fail("unbalanced parenthesis", remaining.position);
            }
            fail("unexpected regular-expression token", remaining.position);
        }
        program_.flags = flags;
        return root;
    }

private:
    [[noreturn]] static void fail(std::string message, std::size_t position) {
        throw CompileError(std::move(message), position);
    }

    struct RecursionGuard {
        explicit RecursionGuard(const CharacterTraits& traits) : traits_(traits) {
            if (traits_.enter_recursion != nullptr &&
                !traits_.enter_recursion(traits_.context)) {
                throw Interrupted();
            }
            active_ = traits_.enter_recursion != nullptr;
        }
        ~RecursionGuard() {
            if (active_ && traits_.leave_recursion != nullptr) {
                traits_.leave_recursion(traits_.context);
            }
        }
        RecursionGuard(const RecursionGuard&) = delete;
        RecursionGuard& operator=(const RecursionGuard&) = delete;

    private:
        const CharacterTraits& traits_;
        bool active_ = false;
    };

    static Node single(NodeKind kind, std::uint32_t flags, std::size_t position) {
        Node node;
        node.kind = kind;
        node.flags = flags;
        node.position = position;
        return node;
    }

    static Node combine(NodeKind kind, std::vector<Node> nodes) {
        if (nodes.empty()) {
            return Node{};
        }
        if (nodes.size() == 1) {
            return std::move(nodes.front());
        }
        Node result;
        result.kind = kind;
        result.children = std::move(nodes);
        return result;
    }

    [[nodiscard]] Node alternation(std::uint32_t& flags) {
        std::vector<Node> branches;
        branches.push_back(sequence(flags));
        while (true) {
            const Token token = lexer_.peek(flags);
            if (token.end || token.escaped || token.value != U'|') {
                break;
            }
            static_cast<void>(lexer_.next(flags));
            branches.push_back(sequence(flags));
        }
        return combine(NodeKind::alternation, std::move(branches));
    }

    [[nodiscard]] Node sequence(std::uint32_t& flags) {
        std::vector<Node> items;
        while (true) {
            const Token token = lexer_.peek(flags);
            if (token.end || (!token.escaped &&
                              (token.value == U'|' || token.value == U')'))) {
                break;
            }
            if (!token.escaped &&
                (token.value == U'*' || token.value == U'+' || token.value == U'?')) {
                fail("nothing to repeat", token.position);
            }
            Node item = atom(flags);
            if (item.kind != NodeKind::empty) {
                items.push_back(repetition(std::move(item), flags));
            }
        }
        return combine(NodeKind::sequence, std::move(items));
    }

    [[nodiscard]] Node atom(std::uint32_t& flags) {
        const Token token = lexer_.next(flags);
        if (token.end) {
            return Node{};
        }
        if (token.escaped) {
            return escaped(token, flags, false);
        }
        switch (token.value) {
            case U'.': return single(NodeKind::dot, flags, token.position);
            case U'^': return single(NodeKind::begin_line, flags, token.position);
            case U'$': return single(NodeKind::end_line, flags, token.position);
            case U'[': return character_class(flags, token.position);
            case U'(': return group(flags, token.position);
            default: {
                Node literal = single(NodeKind::literal, flags, token.position);
                literal.character = token.value;
                return literal;
            }
        }
    }

    [[nodiscard]] char32_t hexadecimal(std::size_t count, std::size_t position) {
        char32_t value = 0;
        for (std::size_t index = 0; index < count; ++index) {
            const char32_t digit = lexer_.raw();
            std::uint32_t part = 0;
            if (digit >= U'0' && digit <= U'9') {
                part = static_cast<std::uint32_t>(digit - U'0');
            } else if (digit >= U'a' && digit <= U'f') {
                part = static_cast<std::uint32_t>(digit - U'a') + 10;
            } else if (digit >= U'A' && digit <= U'F') {
                part = static_cast<std::uint32_t>(digit - U'A') + 10;
            } else {
                fail("incomplete escape", position);
            }
            static_cast<void>(lexer_.take_raw());
            value = static_cast<char32_t>((value << 4) | part);
        }
        if (value > 0x10ffff) {
            fail("bad escape", position);
        }
        return value;
    }

    [[nodiscard]] Node escaped(Token token, std::uint32_t flags, bool inside_class) {
        if (!inside_class) {
            switch (token.value) {
                case U'A': return single(NodeKind::begin_subject, flags, token.position);
                case U'Z':
                case U'z': return single(NodeKind::end_subject, flags, token.position);
                case U'b': return single(NodeKind::word_boundary, flags, token.position);
                case U'B': return single(NodeKind::not_word_boundary, flags, token.position);
                default: break;
            }
        }

        if (token.value == U'd' || token.value == U'D' ||
            token.value == U's' || token.value == U'S' ||
            token.value == U'w' || token.value == U'W') {
            CharacterClass klass;
            const char32_t lower =
                token.value >= U'A' && token.value <= U'Z'
                    ? token.value + (U'a' - U'A')
                    : token.value;
            const Category category = lower == U'd'
                ? Category::digit
                : lower == U's' ? Category::space : Category::word;
            klass.categories.push_back(CategoryEntry{
                category, token.value >= U'A' && token.value <= U'Z'
            });
            const std::size_t index = program_.classes.size();
            program_.classes.push_back(std::move(klass));
            Node node = single(NodeKind::character_class, flags, token.position);
            node.index = index;
            return node;
        }

        char32_t value = token.value;
        switch (token.value) {
            case U'a': value = U'\a'; break;
            case U'b': value = U'\b'; break;
            case U'f': value = U'\f'; break;
            case U'n': value = U'\n'; break;
            case U'r': value = U'\r'; break;
            case U't': value = U'\t'; break;
            case U'v': value = U'\v'; break;
            case U'x': value = hexadecimal(2, token.position); break;
            case U'u':
                if (program_.bytes) {
                    fail("bad escape \\u", token.position);
                }
                value = hexadecimal(4, token.position);
                break;
            case U'U':
                if (program_.bytes) {
                    fail("bad escape \\U", token.position);
                }
                value = hexadecimal(8, token.position);
                break;
            case U'N': {
                if (program_.bytes || lexer_.raw() != U'{') {
                    fail("bad escape \\N", token.position);
                }
                static_cast<void>(lexer_.take_raw());
                std::u32string name;
                while (lexer_.raw() != U'}') {
                    if (lexer_.position() == lexer_.size()) {
                        fail("missing }, unterminated name", token.position + 3);
                    }
                    name.push_back(lexer_.take_raw());
                }
                static_cast<void>(lexer_.take_raw());
                if (name.empty()) {
                    fail("missing character name", token.position + 3);
                }
                if (program_.traits.lookup_name == nullptr ||
                    !program_.traits.lookup_name(program_.traits.context, name, &value)) {
                    if (program_.traits.check_interrupt != nullptr &&
                        !program_.traits.check_interrupt(program_.traits.context)) {
                        throw Interrupted();
                    }
                    fail("undefined character name '" + ascii_name(name) + "'", token.position);
                }
                break;
            }
            default:
                if (ascii_digit(token.value)) {
                    return numeric_escape(token, flags, inside_class);
                }
                if (ascii_letter(token.value)) {
                    fail("bad escape \\" + ascii_display(token.value), token.position);
                }
                break;
        }

        Node literal = single(NodeKind::literal, flags, token.position);
        literal.character = value;
        return literal;
    }

    [[nodiscard]] Node numeric_escape(Token token, std::uint32_t flags, bool inside_class) {
        if (inside_class || token.value == U'0') {
            char32_t value = token.value - U'0';
            for (int count = 0; count < 2; ++count) {
                const char32_t digit = lexer_.raw();
                if (digit < U'0' || digit > U'7') {
                    break;
                }
                value = static_cast<char32_t>((value << 3) + digit - U'0');
                static_cast<void>(lexer_.take_raw());
            }
            if (value > 0xff) {
                fail("octal escape value outside of range 0-0o377", token.position);
            }
            Node literal = single(NodeKind::literal, flags, token.position);
            literal.character = value;
            return literal;
        }

        const std::size_t checkpoint = lexer_.position();
        if (token.value <= U'7' && lexer_.raw() >= U'0' && lexer_.raw() <= U'7' &&
            lexer_.raw(1) >= U'0' && lexer_.raw(1) <= U'7') {
            char32_t value = token.value - U'0';
            value = static_cast<char32_t>((value << 3) + lexer_.take_raw() - U'0');
            value = static_cast<char32_t>((value << 3) + lexer_.take_raw() - U'0');
            if (value > 0xff) {
                fail("octal escape value outside of range 0-0o377", token.position);
            }
            Node literal = single(NodeKind::literal, flags, token.position);
            literal.character = value;
            return literal;
        }

        std::size_t number = static_cast<std::size_t>(token.value - U'0');
        if (ascii_digit(lexer_.raw())) {
            number = number * 10 + static_cast<std::size_t>(lexer_.take_raw() - U'0');
        }
        if (number == 0 || number > program_.group_count) {
            lexer_.reset(checkpoint);
            fail("invalid group reference " + std::to_string(number), token.position + 1);
        }
        if (number < open_groups_.size() && open_groups_[number]) {
            fail("cannot refer to an open group", token.position + 1);
        }
        Node reference = single(NodeKind::backreference, flags, token.position);
        reference.index = number;
        return reference;
    }

    struct ClassItem {
        bool category = false;
        Category category_value = Category::digit;
        bool complement = false;
        char32_t character = U'\0';
        std::size_t position = 0;
    };

    [[nodiscard]] ClassItem class_item() {
        const Token token = lexer_.next(0);
        if (token.end) {
            fail("unterminated character set", lexer_.position());
        }
        if (token.escaped &&
            (token.value == U'd' || token.value == U'D' ||
             token.value == U's' || token.value == U'S' ||
             token.value == U'w' || token.value == U'W')) {
            const char32_t lower = token.value >= U'A' && token.value <= U'Z'
                ? token.value + (U'a' - U'A') : token.value;
            return ClassItem{
                true,
                lower == U'd' ? Category::digit : lower == U's' ? Category::space : Category::word,
                token.value >= U'A' && token.value <= U'Z',
                U'\0',
                token.position,
            };
        }
        if (token.escaped) {
            Node literal = escaped(token, 0, true);
            if (literal.kind != NodeKind::literal) {
                fail("bad character in character set", token.position);
            }
            return ClassItem{false, Category::digit, false, literal.character, token.position};
        }
        return ClassItem{false, Category::digit, false, token.value, token.position};
    }

    [[nodiscard]] Node character_class(std::uint32_t flags, std::size_t opening) {
        CharacterClass klass;
        if (lexer_.raw() == U'^') {
            static_cast<void>(lexer_.take_raw());
            klass.complement = true;
        }
        bool first = true;
        while (lexer_.position() < lexer_.size()) {
            if (lexer_.raw() == U']' && !first) {
                static_cast<void>(lexer_.take_raw());
                Node result = single(NodeKind::character_class, flags, opening);
                result.index = program_.classes.size();
                program_.classes.push_back(std::move(klass));
                return result;
            }
            first = false;
            ClassItem left = class_item();
            if (!left.category && lexer_.raw() == U'-' &&
                lexer_.raw(1) != U']' && lexer_.raw(1) != U'\0') {
                static_cast<void>(lexer_.take_raw());
                ClassItem right = class_item();
                if (right.category || right.character < left.character) {
                    fail("bad character range", left.position);
                }
                klass.ranges.push_back(CharacterRange{left.character, right.character});
            } else if (left.category) {
                klass.categories.push_back(CategoryEntry{
                    left.category_value, left.complement
                });
            } else {
                klass.ranges.push_back(CharacterRange{left.character, left.character});
            }
        }
        fail("unterminated character set", opening);
    }

    [[nodiscard]] std::u32string group_name(char32_t terminator, std::size_t opening) {
        std::u32string name;
        while (lexer_.position() < lexer_.size() && lexer_.raw() != terminator) {
            name.push_back(lexer_.take_raw());
        }
        if (lexer_.position() >= lexer_.size()) {
            fail("missing group name", opening);
        }
        static_cast<void>(lexer_.take_raw());
        if (name.empty()) {
            fail("bad character in group name", opening);
        }
        if (program_.traits.valid_group_name != nullptr) {
            if (!program_.traits.valid_group_name(
                    program_.traits.context,
                    name,
                    program_.bytes
                )) {
                if (program_.traits.check_interrupt != nullptr &&
                    !program_.traits.check_interrupt(program_.traits.context)) {
                    throw Interrupted();
                }
                fail("bad character in group name", opening);
            }
        } else {
            if (!ascii_identifier_start(name.front())) {
                fail("bad character in group name", opening);
            }
            for (char32_t character : name) {
                if (!ascii_identifier_part(character)) {
                    fail("bad character in group name", opening);
                }
            }
        }
        return name;
    }

    [[nodiscard]] std::uint32_t inline_flag(char32_t value, std::size_t position) const {
        switch (value) {
            case U'i': return flag_ignorecase;
            case U'L': return flag_locale;
            case U'm': return flag_multiline;
            case U's': return flag_dotall;
            case U'u': return flag_unicode;
            case U'x': return flag_verbose;
            case U'a': return flag_ascii;
            default: throw CompileError("unknown extension ?" + ascii_display(value), position);
        }
    }

    void validate_flags(std::uint32_t flags, std::size_t position) const {
        if (program_.bytes && (flags & flag_unicode) != 0) {
            fail("cannot use UNICODE flag with a bytes pattern", position);
        }
        if (!program_.bytes && (flags & flag_locale) != 0) {
            fail("cannot use LOCALE flag with a str pattern", position);
        }
        if ((flags & flag_ascii) != 0 && (flags & flag_locale) != 0) {
            fail("ASCII and LOCALE flags are incompatible", position);
        }
        if ((flags & flag_ascii) != 0 && (flags & flag_unicode) != 0) {
            fail("ASCII and UNICODE flags are incompatible", position);
        }
    }

    [[nodiscard]] Node flagged_group(std::uint32_t& enclosing, std::size_t opening) {
        std::uint32_t add = 0;
        std::uint32_t remove = 0;
        bool removing = false;
        while (lexer_.position() < lexer_.size()) {
            const char32_t value = lexer_.raw();
            if (value == U'-') {
                if (removing) {
                    fail("missing flag", lexer_.position());
                }
                removing = true;
                static_cast<void>(lexer_.take_raw());
                continue;
            }
            if (value == U':' || value == U')') {
                break;
            }
            const std::uint32_t bit = inline_flag(value, lexer_.position());
            static_cast<void>(lexer_.take_raw());
            if (removing) {
                if ((bit & (flag_ascii | flag_locale | flag_unicode)) != 0) {
                    fail("bad inline flags: cannot turn off flags 'a', 'u' and 'L'", opening);
                }
                remove |= bit;
            } else {
                add |= bit;
            }
        }
        if ((add & remove) != 0) {
            fail("bad inline flags: flag turned on and off", opening);
        }
        const std::uint32_t exclusive = flag_ascii | flag_locale | flag_unicode;
        std::uint32_t scoped = enclosing;
        if ((add & exclusive) != 0) {
            scoped &= ~exclusive;
        }
        scoped = (scoped | add) & ~remove;
        validate_flags(scoped, opening);
        if (lexer_.raw() == U')') {
            if (opening != 0 || removing) {
                fail("global flags not at the start of the expression", opening);
            }
            static_cast<void>(lexer_.take_raw());
            enclosing = scoped;
            program_.flags = scoped;
            return Node{};
        }
        if (lexer_.raw() != U':') {
            fail("missing -, : or )", lexer_.position());
        }
        static_cast<void>(lexer_.take_raw());
        return enclosed(scoped, opening);
    }

    [[nodiscard]] Node enclosed(std::uint32_t flags, std::size_t opening) {
        RecursionGuard guard(program_.traits);
        Node body = alternation(flags);
        const Token close = lexer_.next(flags);
        if (close.end || close.escaped || close.value != U')') {
            fail("missing ), unterminated subpattern", opening);
        }
        return body;
    }

    [[nodiscard]] Node capture_group(
        std::uint32_t flags,
        std::size_t opening,
        std::optional<std::u32string> name
    ) {
        const std::size_t number = ++program_.group_count;
        if (open_groups_.size() <= number) {
            open_groups_.resize(number + 1, false);
        }
        if (name.has_value()) {
            auto [entry, inserted] = program_.group_names.emplace(*name, number);
            if (!inserted) {
                fail("redefinition of group name '" + ascii_name(*name) + "'", opening);
            }
        }
        Node result = single(NodeKind::capture, flags, opening);
        result.index = number;
        open_groups_[number] = true;
        result.children.push_back(enclosed(flags, opening));
        open_groups_[number] = false;
        if (group_widths_.size() <= number) {
            group_widths_.resize(number + 1);
        }
        group_widths_[number] = width(result.children.front());
        return result;
    }

    [[nodiscard]] Node condition_group(std::uint32_t flags, std::size_t opening) {
        std::u32string name;
        while (lexer_.position() < lexer_.size() && lexer_.raw() != U')') {
            name.push_back(lexer_.take_raw());
        }
        if (lexer_.raw() != U')' || name.empty()) {
            fail("bad character in group name", opening);
        }
        static_cast<void>(lexer_.take_raw());
        std::size_t number = 0;
        if (ascii_digit(name.front())) {
            for (char32_t value : name) {
                if (!ascii_digit(value) ||
                    number > (no_position - 9) / 10) {
                    fail("bad character in group name", opening);
                }
                number = number * 10 + static_cast<std::size_t>(value - U'0');
            }
        } else {
            const auto found = program_.group_names.find(name);
            if (found == program_.group_names.end()) {
                fail("unknown group name '" + ascii_name(name) + "'", opening);
            }
            number = found->second;
        }
        if (number == 0 || number > program_.group_count) {
            fail("invalid group reference " + std::to_string(number), opening);
        }
        RecursionGuard guard(program_.traits);
        Node result = single(NodeKind::conditional, flags, opening);
        result.index = number;
        result.children.push_back(sequence(flags));
        Token divider = lexer_.peek(flags);
        if (!divider.end && !divider.escaped && divider.value == U'|') {
            static_cast<void>(lexer_.next(flags));
            result.children.push_back(sequence(flags));
            divider = lexer_.peek(flags);
            if (!divider.end && !divider.escaped && divider.value == U'|') {
                fail("conditional backref with more than two branches", divider.position);
            }
        } else {
            result.children.push_back(Node{});
        }
        const Token close = lexer_.next(flags);
        if (close.end || close.escaped || close.value != U')') {
            fail("missing ), unterminated subpattern", opening);
        }
        return result;
    }

    [[nodiscard]] Node group(std::uint32_t& flags, std::size_t opening) {
        if (lexer_.raw() != U'?') {
            return capture_group(flags, opening, std::nullopt);
        }
        static_cast<void>(lexer_.take_raw());
        const char32_t extension = lexer_.raw();
        if (extension == U':') {
            static_cast<void>(lexer_.take_raw());
            return enclosed(flags, opening);
        }
        if (extension == U'#') {
            static_cast<void>(lexer_.take_raw());
            while (true) {
                const Token comment = lexer_.next(0);
                if (comment.end) {
                    fail("missing ), unterminated comment", opening);
                }
                if (!comment.escaped && comment.value == U')') {
                    break;
                }
            }
            return Node{};
        }
        if (extension == U'P') {
            static_cast<void>(lexer_.take_raw());
            if (lexer_.raw() == U'<') {
                static_cast<void>(lexer_.take_raw());
                return capture_group(flags, opening, group_name(U'>', opening));
            }
            if (lexer_.raw() == U'=') {
                static_cast<void>(lexer_.take_raw());
                const std::u32string name = group_name(U')', opening);
                const auto found = program_.group_names.find(name);
                if (found == program_.group_names.end()) {
                    fail("unknown group name '" + ascii_name(name) + "'", opening);
                }
                if (found->second < open_groups_.size() &&
                    open_groups_[found->second]) {
                    fail("cannot refer to an open group", opening);
                }
                Node result = single(NodeKind::backreference, flags, opening);
                result.index = found->second;
                return result;
            }
            fail("unknown extension ?P" + ascii_display(lexer_.raw()), opening);
        }
        if (extension == U'=' || extension == U'!') {
            static_cast<void>(lexer_.take_raw());
            Node result = single(
                extension == U'=' ? NodeKind::assert_ahead : NodeKind::assert_not_ahead,
                flags,
                opening
            );
            result.children.push_back(enclosed(flags, opening));
            return result;
        }
        if (extension == U'<') {
            static_cast<void>(lexer_.take_raw());
            const char32_t direction = lexer_.raw();
            if (direction != U'=' && direction != U'!') {
                fail("unknown extension ?<" + ascii_display(direction), opening);
            }
            static_cast<void>(lexer_.take_raw());
            Node result = single(
                direction == U'=' ? NodeKind::assert_behind : NodeKind::assert_not_behind,
                flags,
                opening
            );
            result.children.push_back(enclosed(flags, opening));
            const Width look_width = width(result.children.front());
            if (look_width.minimum != look_width.maximum ||
                look_width.maximum == no_position) {
                fail("look-behind requires fixed-width pattern", opening);
            }
            result.minimum = look_width.minimum;
            return result;
        }
        if (extension == U'>') {
            static_cast<void>(lexer_.take_raw());
            Node result = single(NodeKind::atomic, flags, opening);
            result.children.push_back(enclosed(flags, opening));
            return result;
        }
        if (extension == U'(') {
            static_cast<void>(lexer_.take_raw());
            return condition_group(flags, opening);
        }
        return flagged_group(flags, opening);
    }

    [[nodiscard]] bool decimal_bound(std::size_t& value) {
        if (!ascii_digit(lexer_.raw())) {
            return false;
        }
        value = 0;
        while (ascii_digit(lexer_.raw())) {
            const std::size_t digit = static_cast<std::size_t>(lexer_.take_raw() - U'0');
            if (value > (std::numeric_limits<std::uint32_t>::max() - digit) / 10) {
                fail("the repetition number is too large", lexer_.position() - 1);
            }
            value = value * 10 + digit;
        }
        return true;
    }

    [[nodiscard]] Node repetition(Node child, std::uint32_t flags) {
        const Token token = lexer_.peek(flags);
        if (token.end || token.escaped) {
            return child;
        }
        std::size_t minimum = 0;
        std::size_t maximum = no_position;
        if (token.value == U'*') {
            static_cast<void>(lexer_.next(flags));
        } else if (token.value == U'+') {
            static_cast<void>(lexer_.next(flags));
            minimum = 1;
        } else if (token.value == U'?') {
            static_cast<void>(lexer_.next(flags));
            maximum = 1;
        } else if (token.value == U'{') {
            const std::size_t saved = lexer_.position();
            static_cast<void>(lexer_.next(flags));
            if (!decimal_bound(minimum)) {
                lexer_.reset(saved);
                return child;
            }
            if (lexer_.raw() == U'}') {
                maximum = minimum;
            } else if (lexer_.raw() == U',') {
                static_cast<void>(lexer_.take_raw());
                if (!decimal_bound(maximum)) {
                    maximum = no_position;
                }
            } else {
                lexer_.reset(saved);
                return child;
            }
            if (lexer_.raw() != U'}') {
                lexer_.reset(saved);
                return child;
            }
            static_cast<void>(lexer_.take_raw());
            if (maximum != no_position && minimum > maximum) {
                fail("min repeat greater than max repeat", token.position);
            }
        } else {
            return child;
        }

        Node result = single(NodeKind::repeat, flags, token.position);
        result.minimum = minimum;
        result.maximum = maximum;
        result.children.push_back(std::move(child));
        const Token modifier = lexer_.peek(flags);
        if (!modifier.end && !modifier.escaped &&
            (modifier.value == U'?' || modifier.value == U'+')) {
            static_cast<void>(lexer_.next(flags));
            result.lazy = modifier.value == U'?';
            result.possessive = modifier.value == U'+';
        }
        const Token duplicate = lexer_.peek(flags);
        if (!duplicate.end && !duplicate.escaped &&
            (duplicate.value == U'*' || duplicate.value == U'+' ||
             duplicate.value == U'?')) {
            fail("multiple repeat", duplicate.position);
        }
        return result;
    }

    [[nodiscard]] Width width(const Node& node) const {
        switch (node.kind) {
            case NodeKind::empty:
            case NodeKind::begin_line:
            case NodeKind::end_line:
            case NodeKind::begin_subject:
            case NodeKind::end_subject:
            case NodeKind::word_boundary:
            case NodeKind::not_word_boundary:
            case NodeKind::assert_ahead:
            case NodeKind::assert_not_ahead:
            case NodeKind::assert_behind:
            case NodeKind::assert_not_behind:
                return Width{};
            case NodeKind::literal:
            case NodeKind::dot:
            case NodeKind::character_class:
                return Width{1, 1};
            case NodeKind::capture:
            case NodeKind::atomic:
                return width(node.children.front());
            case NodeKind::backreference:
                if (node.index < group_widths_.size()) {
                    return group_widths_[node.index];
                }
                return Width{0, no_position};
            case NodeKind::sequence: {
                Width result;
                for (const Node& item : node.children) {
                    const Width child = width(item);
                    result.minimum = saturating_add(result.minimum, child.minimum);
                    result.maximum = saturating_add(result.maximum, child.maximum);
                }
                return result;
            }
            case NodeKind::alternation:
            case NodeKind::conditional: {
                Width result{no_position, 0};
                for (const Node& item : node.children) {
                    const Width child = width(item);
                    result.minimum = std::min(result.minimum, child.minimum);
                    result.maximum = std::max(result.maximum, child.maximum);
                }
                if (result.minimum == no_position) {
                    result.minimum = 0;
                }
                return result;
            }
            case NodeKind::repeat: {
                const Width child = width(node.children.front());
                return Width{
                    saturating_multiply(child.minimum, node.minimum),
                    saturating_multiply(child.maximum, node.maximum),
                };
            }
        }
        return Width{0, no_position};
    }

    Program& program_;
    Lexer lexer_;
    std::vector<Width> group_widths_;
    std::vector<bool> open_groups_;
};

class Compiler final {
public:
    Compiler(Program& program, std::vector<Instruction>& destination)
        : program_(program), destination_(destination) {}

    void append(const Node& node) {
        switch (node.kind) {
            case NodeKind::empty: return;
            case NodeKind::literal:
                add(Opcode::character, 0, 0, node.flags, node.character);
                return;
            case NodeKind::dot:
                add(Opcode::any, 0, 0, node.flags);
                return;
            case NodeKind::character_class:
                add(Opcode::character_class, checked(node.index), 0, node.flags);
                return;
            case NodeKind::begin_line:
                add(Opcode::begin_line, 0, 0, node.flags);
                return;
            case NodeKind::end_line:
                add(Opcode::end_line, 0, 0, node.flags);
                return;
            case NodeKind::begin_subject:
                add(Opcode::begin_subject);
                return;
            case NodeKind::end_subject:
                add(Opcode::end_subject);
                return;
            case NodeKind::word_boundary:
                add(Opcode::word_boundary, 0, 0, node.flags);
                return;
            case NodeKind::not_word_boundary:
                add(Opcode::not_word_boundary, 0, 0, node.flags);
                return;
            case NodeKind::sequence:
                for (const Node& child : node.children) {
                    append(child);
                }
                return;
            case NodeKind::alternation:
                compile_alternation(node);
                return;
            case NodeKind::capture:
                add(Opcode::save, checked(node.index * 2));
                append(node.children.front());
                add(Opcode::save, checked(node.index * 2 + 1));
                return;
            case NodeKind::backreference:
                add(Opcode::backreference, checked(node.index), 0, node.flags);
                return;
            case NodeKind::repeat:
                compile_repeat(node);
                return;
            case NodeKind::assert_ahead:
            case NodeKind::assert_not_ahead:
            case NodeKind::assert_behind:
            case NodeKind::assert_not_behind:
                compile_assertion(node);
                return;
            case NodeKind::atomic:
                add(Opcode::atomic_begin);
                append(node.children.front());
                add(Opcode::atomic_end);
                return;
            case NodeKind::conditional:
                compile_conditional(node);
                return;
        }
    }

    void finish() { add(Opcode::accept); }

private:
    [[nodiscard]] static std::uint32_t checked(std::size_t value) {
        if (value > std::numeric_limits<std::uint32_t>::max()) {
            throw CompileError("regular expression code size limit exceeded", no_position);
        }
        return static_cast<std::uint32_t>(value);
    }

    std::size_t add(
        Opcode opcode,
        std::uint32_t first = 0,
        std::uint32_t second = 0,
        std::uint32_t flags = 0,
        char32_t character = U'\0'
    ) {
        const std::size_t position = destination_.size();
        destination_.push_back(Instruction{
            opcode, first, second, flags, character
        });
        return position;
    }

    void compile_alternation(const Node& node) {
        std::vector<std::size_t> exits;
        for (std::size_t index = 0; index + 1 < node.children.size(); ++index) {
            const std::size_t choice = add(Opcode::split);
            destination_[choice].first = checked(destination_.size());
            append(node.children[index]);
            exits.push_back(add(Opcode::jump));
            destination_[choice].second = checked(destination_.size());
        }
        append(node.children.back());
        const std::uint32_t end = checked(destination_.size());
        for (std::size_t exit : exits) {
            destination_[exit].first = end;
        }
    }

    void compile_repeat(const Node& node) {
        if (node.possessive) {
            add(Opcode::atomic_begin);
        }
        const std::size_t repeat_index = program_.repeats.size();
        program_.repeats.push_back(Repeat{
            node.minimum, node.maximum, node.lazy
        });
        const std::size_t begin = add(
            Opcode::repeat_begin, checked(repeat_index)
        );
        append(node.children.front());
        add(Opcode::repeat_end, checked(repeat_index), checked(begin));
        destination_[begin].second = checked(destination_.size());
        if (node.possessive) {
            add(Opcode::atomic_end);
        }
    }

    void compile_assertion(const Node& node) {
        const std::size_t index = program_.assertions.size();
        program_.assertions.emplace_back();
        std::vector<Instruction> body;
        Compiler nested(program_, body);
        nested.append(node.children.front());
        nested.finish();
        program_.assertions[index].instructions = std::move(body);
        program_.assertions[index].width = node.minimum;
        Opcode opcode = Opcode::assert_ahead;
        if (node.kind == NodeKind::assert_not_ahead) {
            opcode = Opcode::assert_not_ahead;
        } else if (node.kind == NodeKind::assert_behind) {
            opcode = Opcode::assert_behind;
        } else if (node.kind == NodeKind::assert_not_behind) {
            opcode = Opcode::assert_not_behind;
        }
        add(opcode, checked(index), 0, node.flags);
    }

    void compile_conditional(const Node& node) {
        const std::size_t branch = add(Opcode::conditional, checked(node.index));
        append(node.children[0]);
        const std::size_t exit = add(Opcode::jump);
        destination_[branch].second = checked(destination_.size());
        append(node.children[1]);
        destination_[exit].first = checked(destination_.size());
    }

    Program& program_;
    std::vector<Instruction>& destination_;
};

bool classify(
    const Program& program,
    Category category,
    char32_t character,
    std::uint32_t flags
) {
    if (program.traits.classify != nullptr) {
        return program.traits.classify(
            program.traits.context, category, character, flags, program.bytes
        );
    }
    switch (category) {
        case Category::digit:
            return character >= U'0' && character <= U'9';
        case Category::space:
            return verbose_space(character);
        case Category::word:
            return ascii_identifier_part(character);
    }
    return false;
}

char32_t lowered(
    const Program& program,
    char32_t character,
    std::uint32_t flags
) {
    if (program.traits.lower != nullptr) {
        return program.traits.lower(
            program.traits.context, character, flags, program.bytes
        );
    }
    if (character >= U'A' && character <= U'Z') {
        return character + (U'a' - U'A');
    }
    return character;
}

bool equal(
    const Program& program,
    char32_t first,
    char32_t second,
    std::uint32_t flags
) {
    if (first == second) {
        return true;
    }
    return (flags & flag_ignorecase) != 0 &&
           lowered(program, first, flags) == lowered(program, second, flags);
}

bool contains(
    const Program& program,
    const CharacterClass& klass,
    char32_t character,
    std::uint32_t flags
) {
    bool found = false;
    for (const CharacterRange& range : klass.ranges) {
        if (character >= range.first && character <= range.last) {
            found = true;
            break;
        }
        if ((flags & flag_ignorecase) != 0) {
            const char32_t folded = lowered(program, character, flags);
            if ((folded >= range.first && folded <= range.last) ||
                (folded >= lowered(program, range.first, flags) &&
                 folded <= lowered(program, range.last, flags))) {
                found = true;
                break;
            }
        }
    }
    if (!found) {
        for (const CategoryEntry& entry : klass.categories) {
            const bool result = classify(program, entry.category, character, flags);
            if (result != entry.complement) {
                found = true;
                break;
            }
        }
    }
    return klass.complement ? !found : found;
}

struct RepeatState {
    std::size_t count = 0;
    std::size_t position = no_position;
    bool active = false;
    bool stalled = false;
};

struct Frame {
    std::size_t instruction = 0;
    std::size_t position = 0;
    std::vector<Capture> captures;
    std::vector<RepeatState> repeats;
    std::vector<std::size_t> atomic_barriers;
    std::optional<std::size_t> last_index;
};

class ExecutionRecursionGuard final {
public:
    explicit ExecutionRecursionGuard(const CharacterTraits& traits)
        : traits_(traits) {
        if (traits_.enter_recursion != nullptr) {
            if (!traits_.enter_recursion(traits_.context)) {
                throw Interrupted();
            }
            active_ = true;
        }
    }

    ~ExecutionRecursionGuard() {
        if (active_ && traits_.leave_recursion != nullptr) {
            traits_.leave_recursion(traits_.context);
        }
    }

    ExecutionRecursionGuard(const ExecutionRecursionGuard&) = delete;
    ExecutionRecursionGuard& operator=(const ExecutionRecursionGuard&) = delete;

private:
    const CharacterTraits& traits_;
    bool active_ = false;
};

std::optional<Match> execute(
    const Program& program,
    const std::vector<Instruction>& code,
    const Subject& subject,
    std::size_t start,
    std::size_t end,
    bool full,
    bool nonempty,
    const std::vector<Capture>* inherited
) {
    if (start > end || end > subject.length) {
        return std::nullopt;
    }
    Frame state;
    state.position = start;
    state.captures = inherited != nullptr
        ? *inherited : std::vector<Capture>(program.group_count + 1);
    state.repeats.resize(program.repeats.size());
    if (state.captures.empty()) {
        state.captures.resize(program.group_count + 1);
    }
    state.captures[0].first = start;

    std::vector<Frame> alternatives;
    std::size_t interrupt_counter = 0;

    auto backtrack = [&]() -> bool {
        if (alternatives.empty()) {
            return false;
        }
        state = std::move(alternatives.back());
        alternatives.pop_back();
        return true;
    };

    while (true) {
        if ((++interrupt_counter & 0x3ffU) == 0 &&
            program.traits.check_interrupt != nullptr &&
            !program.traits.check_interrupt(program.traits.context)) {
            throw Interrupted();
        }
        if (state.instruction >= code.size()) {
            if (!backtrack()) {
                return std::nullopt;
            }
            continue;
        }
        const Instruction& instruction = code[state.instruction];
        bool failed = false;
        switch (instruction.opcode) {
            case Opcode::character:
                if (state.position >= end ||
                    !equal(
                        program,
                        subject.read(state.position),
                        instruction.character,
                        instruction.flags
                    )) {
                    failed = true;
                } else {
                    ++state.position;
                    ++state.instruction;
                }
                break;
            case Opcode::any:
                if (state.position >= end ||
                    ((instruction.flags & flag_dotall) == 0 &&
                     subject.read(state.position) == U'\n')) {
                    failed = true;
                } else {
                    ++state.position;
                    ++state.instruction;
                }
                break;
            case Opcode::character_class:
                if (state.position >= end ||
                    instruction.first >= program.classes.size() ||
                    !contains(
                        program,
                        program.classes[instruction.first],
                        subject.read(state.position),
                        instruction.flags
                    )) {
                    failed = true;
                } else {
                    ++state.position;
                    ++state.instruction;
                }
                break;
            case Opcode::begin_line:
                if (state.position != 0 &&
                    ((instruction.flags & flag_multiline) == 0 ||
                     subject.read(state.position - 1) != U'\n')) {
                    failed = true;
                } else {
                    ++state.instruction;
                }
                break;
            case Opcode::end_line:
                if (state.position == end ||
                    (state.position < end &&
                     subject.read(state.position) == U'\n' &&
                     ((instruction.flags & flag_multiline) != 0 ||
                      state.position + 1 == end))) {
                    ++state.instruction;
                } else {
                    failed = true;
                }
                break;
            case Opcode::begin_subject:
                if (state.position == 0) {
                    ++state.instruction;
                } else {
                    failed = true;
                }
                break;
            case Opcode::end_subject:
                if (state.position == end) {
                    ++state.instruction;
                } else {
                    failed = true;
                }
                break;
            case Opcode::word_boundary:
            case Opcode::not_word_boundary: {
                const bool before = state.position != 0 &&
                    classify(
                        program,
                        Category::word,
                        subject.read(state.position - 1),
                        instruction.flags
                    );
                const bool after = state.position < end &&
                    classify(
                        program,
                        Category::word,
                        subject.read(state.position),
                        instruction.flags
                    );
                const bool boundary = before != after;
                const bool wanted = instruction.opcode == Opcode::word_boundary;
                if (boundary == wanted) {
                    ++state.instruction;
                } else {
                    failed = true;
                }
                break;
            }
            case Opcode::jump:
                state.instruction = instruction.first;
                break;
            case Opcode::split: {
                Frame alternate = state;
                alternate.instruction = instruction.second;
                alternatives.push_back(std::move(alternate));
                state.instruction = instruction.first;
                break;
            }
            case Opcode::save: {
                const std::size_t group = instruction.first / 2;
                if (group >= state.captures.size()) {
                    failed = true;
                    break;
                }
                if ((instruction.first & 1U) == 0) {
                    state.captures[group].first = state.position;
                    state.captures[group].last = no_position;
                } else {
                    state.captures[group].last = state.position;
                    if (group != 0) {
                        state.last_index = group;
                    }
                }
                ++state.instruction;
                break;
            }
            case Opcode::backreference: {
                if (instruction.first >= state.captures.size()) {
                    failed = true;
                    break;
                }
                const Capture capture = state.captures[instruction.first];
                if (!capture.matched()) {
                    failed = true;
                    break;
                }
                const std::size_t length = capture.last - capture.first;
                if (length > end - state.position) {
                    failed = true;
                    break;
                }
                for (std::size_t index = 0; index < length; ++index) {
                    if (!equal(
                            program,
                            subject.read(capture.first + index),
                            subject.read(state.position + index),
                            instruction.flags
                        )) {
                        failed = true;
                        break;
                    }
                }
                if (!failed) {
                    state.position += length;
                    ++state.instruction;
                }
                break;
            }
            case Opcode::repeat_begin: {
                if (instruction.first >= program.repeats.size()) {
                    failed = true;
                    break;
                }
                RepeatState& current = state.repeats[instruction.first];
                if (!current.active) {
                    current = RepeatState{};
                    current.active = true;
                }
                const Repeat& repeat = program.repeats[instruction.first];
                const bool can_exit = current.count >= repeat.minimum;
                const bool below_maximum = current.count < repeat.maximum;
                const bool can_continue = below_maximum &&
                    (!current.stalled || current.count < repeat.minimum);
                if (!can_continue && !can_exit) {
                    failed = true;
                    break;
                }
                if (can_continue && can_exit) {
                    Frame alternate = state;
                    if (repeat.lazy) {
                        alternate.instruction = state.instruction + 1;
                        alternate.repeats[instruction.first].position = state.position;
                        alternatives.push_back(std::move(alternate));
                        state.repeats[instruction.first] = RepeatState{};
                        state.instruction = instruction.second;
                    } else {
                        alternate.repeats[instruction.first] = RepeatState{};
                        alternate.instruction = instruction.second;
                        alternatives.push_back(std::move(alternate));
                        state.repeats[instruction.first].position = state.position;
                        ++state.instruction;
                    }
                } else if (can_continue) {
                    current.position = state.position;
                    ++state.instruction;
                } else {
                    current = RepeatState{};
                    state.instruction = instruction.second;
                }
                break;
            }
            case Opcode::repeat_end: {
                if (instruction.first >= state.repeats.size()) {
                    failed = true;
                    break;
                }
                RepeatState& current = state.repeats[instruction.first];
                current.stalled = current.position == state.position;
                ++current.count;
                state.instruction = instruction.second;
                break;
            }
            case Opcode::assert_ahead:
            case Opcode::assert_not_ahead:
            case Opcode::assert_behind:
            case Opcode::assert_not_behind: {
                if (instruction.first >= program.assertions.size()) {
                    failed = true;
                    break;
                }
                const Assertion& assertion = program.assertions[instruction.first];
                const bool behind =
                    instruction.opcode == Opcode::assert_behind ||
                    instruction.opcode == Opcode::assert_not_behind;
                const bool positive =
                    instruction.opcode == Opcode::assert_ahead ||
                    instruction.opcode == Opcode::assert_behind;
                std::optional<Match> result;
                if (!behind || state.position >= assertion.width) {
                    ExecutionRecursionGuard guard(program.traits);
                    const std::size_t begin = behind
                        ? state.position - assertion.width : state.position;
                    const std::size_t limit = behind ? state.position : end;
                    result = execute(
                        program,
                        assertion.instructions,
                        subject,
                        begin,
                        limit,
                        behind,
                        false,
                        &state.captures
                    );
                }
                if (result.has_value() != positive) {
                    failed = true;
                } else {
                    if (positive && result.has_value()) {
                        const Capture overall = state.captures[0];
                        state.captures = std::move(result->captures);
                        state.captures[0] = overall;
                        if (result->last_index.has_value()) {
                            state.last_index = result->last_index;
                        }
                    }
                    ++state.instruction;
                }
                break;
            }
            case Opcode::atomic_begin:
                state.atomic_barriers.push_back(alternatives.size());
                ++state.instruction;
                break;
            case Opcode::atomic_end:
                if (state.atomic_barriers.empty()) {
                    failed = true;
                } else {
                    alternatives.resize(state.atomic_barriers.back());
                    state.atomic_barriers.pop_back();
                    ++state.instruction;
                }
                break;
            case Opcode::conditional:
                if (instruction.first >= state.captures.size()) {
                    failed = true;
                } else if (state.captures[instruction.first].matched()) {
                    ++state.instruction;
                } else {
                    state.instruction = instruction.second;
                }
                break;
            case Opcode::accept:
                if ((full && state.position != end) ||
                    (nonempty && state.position == start)) {
                    failed = true;
                } else {
                    state.captures[0].last = state.position;
                    return Match{
                        std::move(state.captures), state.last_index
                    };
                }
                break;
        }
        if (failed && !backtrack()) {
            return std::nullopt;
        }
    }
}

}  // namespace

Program compile(
    std::u32string pattern,
    bool bytes,
    std::uint32_t flags,
    CharacterTraits traits
) {
    Program program;
    program.pattern = std::move(pattern);
    program.bytes = bytes;
    program.flags = flags;
    program.traits = traits;
    Parser parser(program, program.pattern);
    Node root = parser.parse();
    Compiler compiler(program, program.instructions);
    compiler.append(root);
    compiler.finish();
    return program;
}

std::optional<Match> match_at(
    const Program& program,
    const Subject& subject,
    std::size_t start,
    std::size_t end,
    bool full,
    bool nonempty
) {
    return execute(
        program,
        program.instructions,
        subject,
        start,
        std::min(end, subject.length),
        full,
        nonempty,
        nullptr
    );
}

std::optional<Match> search(
    const Program& program,
    const Subject& subject,
    std::size_t start,
    std::size_t end,
    bool nonempty
) {
    const std::size_t limit = std::min(end, subject.length);
    if (start > limit) {
        return std::nullopt;
    }
    for (std::size_t position = start;; ++position) {
        std::optional<Match> result = match_at(
            program,
            subject,
            position,
            limit,
            false,
            nonempty && position == start
        );
        if (result.has_value()) {
            return result;
        }
        if (position == limit) {
            return std::nullopt;
        }
        if ((position & 0x3ffU) == 0 &&
            program.traits.check_interrupt != nullptr &&
            !program.traits.check_interrupt(program.traits.context)) {
            throw Interrupted();
        }
    }
}

}  // namespace rebar_cpp
