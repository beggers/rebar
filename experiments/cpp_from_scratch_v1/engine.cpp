// An original parser, bytecode compiler, and ordered-backtracking executor.
// No system, C++, Python, or third-party regular-expression engine is used.

#include "engine.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <limits>
#include <utility>

namespace rebar::experimental::cpp_v1 {

PatternError::PatternError(std::string message, std::size_t offset,
                           std::size_t line, std::size_t column)
    : std::runtime_error(std::move(message)),
      offset_(offset),
      line_(line),
      column_(column) {}

namespace {

constexpr std::size_t unbounded = no_position;
constexpr std::uint32_t supported_flags =
    flag_template | flag_ignore_case | flag_locale | flag_multiline |
    flag_dotall | flag_unicode | flag_verbose | flag_debug | flag_ascii;

[[nodiscard]] constexpr bool ascii_digit(Rune rune) noexcept {
  return rune >= U'0' && rune <= U'9';
}

[[nodiscard]] constexpr bool ascii_letter(Rune rune) noexcept {
  return (rune >= U'a' && rune <= U'z') ||
         (rune >= U'A' && rune <= U'Z');
}

[[nodiscard]] constexpr bool ascii_word(Rune rune) noexcept {
  return ascii_digit(rune) || ascii_letter(rune) || rune == U'_';
}

[[nodiscard]] constexpr bool ascii_space(Rune rune) noexcept {
  return rune == U' ' || rune == U'\t' || rune == U'\n' ||
         rune == U'\r' || rune == U'\f' || rune == U'\v';
}

[[nodiscard]] constexpr Rune ascii_lower(Rune rune) noexcept {
  return rune >= U'A' && rune <= U'Z' ? rune + (U'a' - U'A') : rune;
}

[[nodiscard]] constexpr Rune ascii_upper(Rune rune) noexcept {
  return rune >= U'a' && rune <= U'z' ? rune - (U'a' - U'A') : rune;
}

[[nodiscard]] std::size_t add_width(std::size_t left,
                                    std::size_t right) noexcept {
  if (left == unbounded || right == unbounded ||
      left > unbounded - right) {
    return unbounded;
  }
  return left + right;
}

[[nodiscard]] std::size_t multiply_width(std::size_t width,
                                         std::size_t count) noexcept {
  if (width == 0 || count == 0) {
    return 0;
  }
  if (width == unbounded || count == unbounded ||
      width > unbounded / count) {
    return unbounded;
  }
  return width * count;
}

enum class NodeKind : std::uint8_t {
  empty,
  literal,
  any,
  character_class,
  beginning,
  absolute_beginning,
  end,
  absolute_end,
  word_boundary,
  not_word_boundary,
  sequence,
  alternative,
  capture,
  repeat,
  back_reference,
  conditional,
  look_ahead,
  negative_look_ahead,
  look_behind,
  negative_look_behind,
  atomic,
};

struct Node {
  NodeKind kind = NodeKind::empty;
  std::uint32_t flags = 0;
  Rune character = U'\0';
  std::size_t group = 0;
  std::size_t minimum = 0;
  std::size_t maximum = 0;
  std::size_t minimum_width = 0;
  std::size_t maximum_width = 0;
  bool greedy = true;
  bool possessive = false;
  std::shared_ptr<CharacterClass> character_class;
  std::vector<std::shared_ptr<Node>> children;
};

using NodePointer = std::shared_ptr<Node>;

[[nodiscard]] NodePointer node(NodeKind kind, std::uint32_t flags) {
  auto result = std::make_shared<Node>();
  result->kind = kind;
  result->flags = flags;
  return result;
}

[[nodiscard]] bool is_ascii_mode(std::uint32_t flags,
                                 Encoding encoding) noexcept {
  return encoding == Encoding::bytes || (flags & flag_ascii) != 0;
}

[[nodiscard]] bool locale_mode(std::uint32_t flags,
                              Encoding encoding) noexcept {
  return encoding == Encoding::bytes && (flags & flag_locale) != 0;
}

[[nodiscard]] bool category_matches(Category category, Rune character,
                                    std::uint32_t flags, Encoding encoding,
                                    const CharacterProperties& properties) {
  bool result = false;
  switch (category) {
    case Category::digit:
    case Category::not_digit:
      result = is_ascii_mode(flags, encoding)
                   ? ascii_digit(character)
                   : (properties.unicode_decimal &&
                      properties.unicode_decimal(character));
      return category == Category::digit ? result : !result;
    case Category::space:
    case Category::not_space:
      result = is_ascii_mode(flags, encoding)
                   ? ascii_space(character)
                   : (properties.unicode_space &&
                      properties.unicode_space(character));
      return category == Category::space ? result : !result;
    case Category::word:
    case Category::not_word:
      if (locale_mode(flags, encoding)) {
        result = character == U'_' ||
                 (character <= 0xff &&
                  std::isalnum(static_cast<unsigned char>(character)) != 0);
      } else if (is_ascii_mode(flags, encoding)) {
        result = ascii_word(character);
      } else {
        result = character == U'_' ||
                 (properties.unicode_alphanumeric &&
                  properties.unicode_alphanumeric(character));
      }
      return category == Category::word ? result : !result;
  }
  return false;
}

[[nodiscard]] Rune lower_character(Rune character, std::uint32_t flags,
                                   Encoding encoding,
                                   const CharacterProperties& properties) {
  if (locale_mode(flags, encoding) && character <= 0xff) {
    return static_cast<Rune>(
        std::tolower(static_cast<unsigned char>(character)));
  }
  if (is_ascii_mode(flags, encoding)) {
    return ascii_lower(character);
  }
  return properties.unicode_lower ? properties.unicode_lower(character)
                                  : ascii_lower(character);
}

[[nodiscard]] Rune upper_character(Rune character, std::uint32_t flags,
                                   Encoding encoding,
                                   const CharacterProperties& properties) {
  if (locale_mode(flags, encoding) && character <= 0xff) {
    return static_cast<Rune>(
        std::toupper(static_cast<unsigned char>(character)));
  }
  if (is_ascii_mode(flags, encoding)) {
    return ascii_upper(character);
  }
  return properties.unicode_upper ? properties.unicode_upper(character)
                                  : ascii_upper(character);
}

[[nodiscard]] bool equal_character(Rune left, Rune right,
                                   std::uint32_t flags, Encoding encoding,
                                   const CharacterProperties& properties) {
  if (left == right) {
    return true;
  }
  if ((flags & flag_ignore_case) == 0) {
    return false;
  }
  return lower_character(left, flags, encoding, properties) ==
             lower_character(right, flags, encoding, properties) ||
         upper_character(left, flags, encoding, properties) ==
             upper_character(right, flags, encoding, properties);
}

[[nodiscard]] bool class_matches(const CharacterClass& character_class,
                                 Rune character, std::uint32_t flags,
                                 Encoding encoding,
                                 const CharacterProperties& properties) {
  bool matched = false;
  const Rune lower = lower_character(character, flags, encoding, properties);
  const Rune upper = upper_character(character, flags, encoding, properties);
  for (const CharacterRange& range : character_class.ranges) {
    if ((range.first <= character && character <= range.last) ||
        ((flags & flag_ignore_case) != 0 &&
         ((range.first <= lower && lower <= range.last) ||
          (range.first <= upper && upper <= range.last)))) {
      matched = true;
      break;
    }
  }
  if (!matched) {
    for (Category category : character_class.categories) {
      if (category_matches(category, character, flags, encoding,
                           properties)) {
        matched = true;
        break;
      }
    }
  }
  return character_class.negated ? !matched : matched;
}

class Parser final {
 public:
  Parser(TextView pattern, Encoding encoding, std::uint32_t flags,
         const CharacterProperties& properties)
      : pattern_(pattern),
        encoding_(encoding),
        flags_(flags),
        properties_(properties) {}

  [[nodiscard]] NodePointer parse() {
    if ((flags_ & ~supported_flags) != 0) {
      fail("unrecognised regular-expression flag", 0);
    }
    if ((flags_ & flag_template) != 0) {
      fail("template regular-expression mode is not implemented", 0);
    }
    if ((flags_ & flag_locale) != 0 && encoding_ != Encoding::bytes) {
      fail("cannot use LOCALE flag with a str pattern", 0);
    }
    if ((flags_ & flag_unicode) != 0 && encoding_ == Encoding::bytes) {
      fail("cannot use UNICODE flag with a bytes pattern", 0);
    }
    if ((flags_ & flag_ascii) != 0 && (flags_ & flag_locale) != 0) {
      fail("ASCII and LOCALE flags are incompatible", 0);
    }
    if (encoding_ == Encoding::unicode &&
        (flags_ & flag_ascii) == 0) {
      flags_ |= flag_unicode;
    }
    NodePointer result = parse_alternation();
    skip_verbose();
    if (!at_end()) {
      fail(peek() == U')' ? "unbalanced parenthesis"
                         : "unexpected regular-expression character",
           position_);
    }
    return result;
  }

  [[nodiscard]] std::size_t group_count() const noexcept {
    return group_count_;
  }
  [[nodiscard]] std::uint32_t flags() const noexcept { return flags_; }
  [[nodiscard]] const std::unordered_map<std::string, std::size_t>&
  group_names() const noexcept {
    return group_names_;
  }

 private:
  [[nodiscard]] bool at_end() const noexcept {
    return position_ >= pattern_.size();
  }

  [[nodiscard]] Rune peek(std::size_t ahead = 0) const noexcept {
    return ahead < pattern_.size() -
                       std::min(position_, pattern_.size())
               ? pattern_[position_ + ahead]
               : U'\0';
  }

  [[nodiscard]] bool consume(Rune expected) noexcept {
    if (!at_end() && pattern_[position_] == expected) {
      ++position_;
      return true;
    }
    return false;
  }

  [[noreturn]] void fail(std::string message, std::size_t offset) const {
    std::size_t line = 1;
    std::size_t column = 1;
    for (std::size_t index = 0;
         index < std::min(offset, pattern_.size()); ++index) {
      if (pattern_[index] == U'\n') {
        ++line;
        column = 1;
      } else {
        ++column;
      }
    }
    throw PatternError(std::move(message), offset, line, column);
  }

  void skip_verbose() {
    if ((flags_ & flag_verbose) == 0) {
      return;
    }
    for (;;) {
      while (!at_end() && ascii_space(peek())) {
        ++position_;
      }
      if (at_end() || peek() != U'#') {
        return;
      }
      while (!at_end() && peek() != U'\n') {
        ++position_;
      }
    }
  }

  [[nodiscard]] NodePointer parse_alternation() {
    const std::uint32_t entry_flags = flags_;
    std::vector<NodePointer> branches;
    branches.push_back(parse_sequence());
    while (consume(U'|')) {
      branches.push_back(parse_sequence());
    }
    if (branches.size() == 1) {
      return branches.front();
    }
    NodePointer result = node(NodeKind::alternative, entry_flags);
    result->minimum_width = unbounded;
    for (const NodePointer& branch : branches) {
      result->minimum_width =
          std::min(result->minimum_width, branch->minimum_width);
      result->maximum_width =
          std::max(result->maximum_width, branch->maximum_width);
      result->children.push_back(branch);
    }
    return result;
  }

  [[nodiscard]] NodePointer parse_sequence() {
    NodePointer result = node(NodeKind::sequence, flags_);
    for (;;) {
      skip_verbose();
      if (at_end() || peek() == U')' || peek() == U'|') {
        break;
      }
      if (peek() == U'*' || peek() == U'+' || peek() == U'?') {
        fail("nothing to repeat", position_);
      }
      NodePointer item = parse_quantified();
      result->minimum_width =
          add_width(result->minimum_width, item->minimum_width);
      result->maximum_width =
          add_width(result->maximum_width, item->maximum_width);
      result->children.push_back(std::move(item));
    }
    if (result->children.empty()) {
      return node(NodeKind::empty, flags_);
    }
    if (result->children.size() == 1) {
      return result->children.front();
    }
    return result;
  }

  [[nodiscard]] std::size_t parse_decimal(std::size_t offset) {
    std::size_t value = 0;
    bool found = false;
    while (!at_end() && ascii_digit(peek())) {
      found = true;
      const std::size_t digit = static_cast<std::size_t>(peek() - U'0');
      if (value > (unbounded - digit) / 10) {
        fail("regular-expression number is too large", offset);
      }
      value = value * 10 + digit;
      ++position_;
    }
    if (!found) {
      fail("expected a regular-expression number", offset);
    }
    return value;
  }

  [[nodiscard]] NodePointer parse_quantified() {
    NodePointer atom = parse_atom();
    skip_verbose();
    if (at_end()) {
      return atom;
    }

    std::size_t minimum = 0;
    std::size_t maximum = 0;
    const std::size_t offset = position_;
    if (consume(U'*')) {
      maximum = unbounded;
    } else if (consume(U'+')) {
      minimum = 1;
      maximum = unbounded;
    } else if (consume(U'?')) {
      maximum = 1;
    } else if (consume(U'{')) {
      if (!ascii_digit(peek()) && peek() != U',') {
        position_ = offset;
        return atom;
      }
      if (ascii_digit(peek())) {
        minimum = parse_decimal(offset);
      }
      if (consume(U',')) {
        maximum = ascii_digit(peek()) ? parse_decimal(offset) : unbounded;
      } else {
        maximum = minimum;
      }
      if (!consume(U'}')) {
        position_ = offset;
        return atom;
      }
      if (maximum != unbounded && minimum > maximum) {
        fail("min repeat greater than max repeat", offset);
      }
    } else {
      return atom;
    }

    NodePointer result = node(NodeKind::repeat, atom->flags);
    result->children.push_back(std::move(atom));
    result->minimum = minimum;
    result->maximum = maximum;
    result->minimum_width =
        multiply_width(result->children[0]->minimum_width, minimum);
    result->maximum_width =
        multiply_width(result->children[0]->maximum_width, maximum);
    if (consume(U'?')) {
      result->greedy = false;
    } else if (consume(U'+')) {
      result->possessive = true;
    }
    if (peek() == U'*' || peek() == U'+' || peek() == U'?' ||
        peek() == U'{') {
      fail("multiple repeat", position_);
    }
    return result;
  }

  [[nodiscard]] NodePointer literal_node(Rune character,
                                         std::uint32_t flags) const {
    NodePointer result = node(NodeKind::literal, flags);
    result->character = character;
    result->minimum_width = 1;
    result->maximum_width = 1;
    return result;
  }

  [[nodiscard]] NodePointer parse_atom() {
    const std::size_t offset = position_;
    if (at_end()) {
      fail("unexpected end of regular expression", offset);
    }
    const Rune character = pattern_[position_++];
    switch (character) {
      case U'.': {
        NodePointer result = node(NodeKind::any, flags_);
        result->minimum_width = result->maximum_width = 1;
        return result;
      }
      case U'^':
        return node(NodeKind::beginning, flags_);
      case U'$':
        return node(NodeKind::end, flags_);
      case U'[':
        return parse_character_class(offset);
      case U'(':
        return parse_group(offset);
      case U'\\':
        return parse_escape(offset, false);
      default:
        return literal_node(character, flags_);
    }
  }

  [[nodiscard]] Rune parse_hex(std::size_t count, std::size_t offset) {
    std::uint32_t value = 0;
    for (std::size_t index = 0; index < count; ++index) {
      if (at_end()) {
        fail("incomplete hexadecimal escape", offset);
      }
      const Rune character = pattern_[position_++];
      std::uint32_t digit = 0;
      if (ascii_digit(character)) {
        digit = static_cast<std::uint32_t>(character - U'0');
      } else if (character >= U'a' && character <= U'f') {
        digit = static_cast<std::uint32_t>(character - U'a' + 10);
      } else if (character >= U'A' && character <= U'F') {
        digit = static_cast<std::uint32_t>(character - U'A' + 10);
      } else {
        fail("incomplete hexadecimal escape", offset);
      }
      value = (value << 4) | digit;
    }
    if (value > 0x10ffff ||
        (encoding_ == Encoding::bytes && value > 0xff)) {
      fail("bad hexadecimal character escape", offset);
    }
    return static_cast<Rune>(value);
  }

  [[nodiscard]] NodePointer category_node(Category category) {
    NodePointer result = node(NodeKind::character_class, flags_);
    result->character_class = std::make_shared<CharacterClass>();
    result->character_class->categories.push_back(category);
    result->minimum_width = result->maximum_width = 1;
    return result;
  }

  [[nodiscard]] std::string parse_name(Rune terminal,
                                       std::size_t offset) {
    std::string result;
    while (!at_end() && peek() != terminal) {
      const Rune character = pattern_[position_++];
      if (character > 0x7f ||
          !(ascii_word(character) &&
            (!result.empty() || !ascii_digit(character)))) {
        fail("bad character in group name", offset);
      }
      result.push_back(static_cast<char>(character));
    }
    if (result.empty() || !consume(terminal)) {
      fail("missing or unterminated group name", offset);
    }
    return result;
  }

  [[nodiscard]] NodePointer parse_escape(std::size_t offset,
                                         bool in_class) {
    if (at_end()) {
      fail("bad escape (end of pattern)", offset);
    }
    const Rune escaped = pattern_[position_++];
    switch (escaped) {
      case U'a':
        return literal_node(U'\a', flags_);
      case U'b':
        return in_class ? literal_node(U'\b', flags_)
                        : node(NodeKind::word_boundary, flags_);
      case U'B':
        if (in_class) {
          fail("bad escape \\B in character class", offset);
        }
        return node(NodeKind::not_word_boundary, flags_);
      case U'f':
        return literal_node(U'\f', flags_);
      case U'n':
        return literal_node(U'\n', flags_);
      case U'r':
        return literal_node(U'\r', flags_);
      case U't':
        return literal_node(U'\t', flags_);
      case U'v':
        return literal_node(U'\v', flags_);
      case U'd':
        return category_node(Category::digit);
      case U'D':
        return category_node(Category::not_digit);
      case U's':
        return category_node(Category::space);
      case U'S':
        return category_node(Category::not_space);
      case U'w':
        return category_node(Category::word);
      case U'W':
        return category_node(Category::not_word);
      case U'A':
        if (in_class) {
          fail("bad escape \\A in character class", offset);
        }
        return node(NodeKind::absolute_beginning, flags_);
      case U'Z':
      case U'z':
        if (in_class) {
          fail("bad absolute-end escape in character class", offset);
        }
        return node(NodeKind::absolute_end, flags_);
      case U'x':
        return literal_node(parse_hex(2, offset), flags_);
      case U'u':
        if (encoding_ == Encoding::bytes) {
          fail("bad escape \\u in bytes pattern", offset);
        }
        return literal_node(parse_hex(4, offset), flags_);
      case U'U':
        if (encoding_ == Encoding::bytes) {
          fail("bad escape \\U in bytes pattern", offset);
        }
        return literal_node(parse_hex(8, offset), flags_);
      case U'N': {
        if (encoding_ == Encoding::bytes || !consume(U'{')) {
          fail("missing { in Unicode character name", offset);
        }
        std::string name;
        while (!at_end() && peek() != U'}') {
          if (peek() > 0x7f) {
            fail("undefined Unicode character name", offset);
          }
          name.push_back(static_cast<char>(pattern_[position_++]));
        }
        if (name.empty() || !consume(U'}') ||
            !properties_.unicode_name) {
          fail("undefined Unicode character name", offset);
        }
        const std::optional<Rune> named = properties_.unicode_name(name);
        if (!named.has_value()) {
          fail("undefined Unicode character name", offset);
        }
        return literal_node(*named, flags_);
      }
      default:
        break;
    }

    if (escaped == U'0' ||
        (in_class && escaped >= U'0' && escaped <= U'7')) {
      std::uint32_t value = static_cast<std::uint32_t>(escaped - U'0');
      for (std::size_t index = 1;
           index < 3 && peek() >= U'0' && peek() <= U'7'; ++index) {
        value = value * 8 +
                static_cast<std::uint32_t>(pattern_[position_++] - U'0');
      }
      if (value > 0xff) {
        fail("octal escape value outside range 0-0o377", offset);
      }
      return literal_node(static_cast<Rune>(value), flags_);
    }

    if (!in_class && escaped >= U'1' && escaped <= U'9') {
      const std::size_t number_start = position_ - 1;
      if (escaped <= U'7' && peek() >= U'0' && peek() <= U'7' &&
          peek(1) >= U'0' && peek(1) <= U'7') {
        const std::uint32_t value =
            static_cast<std::uint32_t>(escaped - U'0') * 64 +
            static_cast<std::uint32_t>(pattern_[position_++] - U'0') * 8 +
            static_cast<std::uint32_t>(pattern_[position_++] - U'0');
        if (value > 0xff) {
          fail("octal escape value outside range 0-0o377", offset);
        }
        return literal_node(static_cast<Rune>(value), flags_);
      }
      position_ = number_start;
      const std::size_t group = parse_decimal(offset);
      if (group == 0 || group > group_count_ ||
          std::find(open_groups_.begin(), open_groups_.end(), group) !=
              open_groups_.end()) {
        fail("invalid group reference", offset);
      }
      NodePointer reference = node(NodeKind::back_reference, flags_);
      reference->group = group;
      reference->maximum_width = unbounded;
      return reference;
    }

    if (ascii_letter(escaped)) {
      fail("bad escape in regular-expression pattern", offset);
    }
    return literal_node(escaped, flags_);
  }

  [[nodiscard]] NodePointer parse_character_class(std::size_t offset) {
    NodePointer result = node(NodeKind::character_class, flags_);
    result->character_class = std::make_shared<CharacterClass>();
    result->minimum_width = result->maximum_width = 1;
    result->character_class->negated = consume(U'^');
    bool first = true;
    bool closed = false;
    while (!at_end()) {
      if (peek() == U']' && !first) {
        ++position_;
        closed = true;
        break;
      }
      first = false;
      NodePointer begin =
          consume(U'\\') ? parse_escape(position_ - 1, true)
                         : literal_node(pattern_[position_++], flags_);
      if (begin->kind == NodeKind::character_class) {
        for (Category category : begin->character_class->categories) {
          result->character_class->categories.push_back(category);
        }
        if (peek() == U'-' && peek(1) != U']') {
          fail("bad character range", position_);
        }
        continue;
      }
      if (peek() == U'-' && peek(1) != U']' && peek(1) != U'\0') {
        ++position_;
        NodePointer end =
            consume(U'\\') ? parse_escape(position_ - 1, true)
                           : literal_node(pattern_[position_++], flags_);
        if (end->kind != NodeKind::literal ||
            begin->character > end->character) {
          fail("bad character range", offset);
        }
        result->character_class->ranges.push_back(
            {begin->character, end->character});
      } else {
        result->character_class->ranges.push_back(
            {begin->character, begin->character});
      }
    }
    if (!closed) {
      fail("unterminated character set", offset);
    }
    return result;
  }

  [[nodiscard]] std::uint32_t flag_for(Rune character,
                                       std::size_t offset) const {
    switch (character) {
      case U'a':
        return flag_ascii;
      case U'i':
        return flag_ignore_case;
      case U'L':
        return flag_locale;
      case U'm':
        return flag_multiline;
      case U's':
        return flag_dotall;
      case U'u':
        return flag_unicode;
      case U'x':
        return flag_verbose;
      default:
        fail("unknown inline regular-expression flag", offset);
    }
  }

  [[nodiscard]] NodePointer parse_inline_flags(std::size_t offset) {
    std::uint32_t added = 0;
    std::uint32_t removed = 0;
    bool subtracting = false;
    while (!at_end() && peek() != U':' && peek() != U')') {
      if (consume(U'-')) {
        if (subtracting) {
          fail("bad inline flags", offset);
        }
        subtracting = true;
        continue;
      }
      const std::uint32_t bit = flag_for(pattern_[position_++], offset);
      std::uint32_t& target = subtracting ? removed : added;
      if ((target & bit) != 0) {
        fail("repeated inline flag", offset);
      }
      target |= bit;
    }
    if ((removed & (flag_ascii | flag_locale | flag_unicode)) != 0 ||
        (added & removed) != 0) {
      fail("bad inline flags", offset);
    }
    if ((added & flag_locale) != 0 && encoding_ != Encoding::bytes) {
      fail("cannot use LOCALE flag with a str pattern", offset);
    }
    if ((added & flag_unicode) != 0 && encoding_ == Encoding::bytes) {
      fail("cannot use UNICODE flag with a bytes pattern", offset);
    }
    const std::uint32_t type_bits = flag_ascii | flag_locale | flag_unicode;
    if ((added & type_bits) != 0 &&
        (added & type_bits & ((added & type_bits) - 1)) != 0) {
      fail("ASCII, LOCALE and UNICODE flags are incompatible", offset);
    }
    std::uint32_t scoped = (flags_ | added) & ~removed;
    if ((added & type_bits) != 0) {
      scoped = (scoped & ~type_bits) | (added & type_bits);
    }
    if (consume(U')')) {
      if (offset != 0 || subtracting) {
        fail("global flags not at the start of the expression", offset);
      }
      flags_ = scoped;
      return node(NodeKind::empty, flags_);
    }
    if (!consume(U':')) {
      fail("missing : in inline flags", offset);
    }
    const std::uint32_t previous = std::exchange(flags_, scoped);
    NodePointer result = parse_alternation();
    flags_ = previous;
    if (!consume(U')')) {
      fail("missing ), unterminated subpattern", offset);
    }
    return result;
  }

  [[nodiscard]] NodePointer parse_capturing_group(std::size_t offset,
                                                   std::string name) {
    const std::size_t group = ++group_count_;
    if (!name.empty() && !group_names_.emplace(name, group).second) {
      fail("redefinition of group name", offset);
    }
    open_groups_.push_back(group);
    NodePointer content = parse_alternation();
    if (!consume(U')')) {
      fail("missing ), unterminated subpattern", offset);
    }
    open_groups_.pop_back();
    NodePointer result = node(NodeKind::capture, content->flags);
    result->group = group;
    result->minimum_width = content->minimum_width;
    result->maximum_width = content->maximum_width;
    result->children.push_back(std::move(content));
    return result;
  }

  [[nodiscard]] NodePointer parse_assertion(NodeKind kind,
                                             std::size_t offset) {
    NodePointer body = parse_alternation();
    if (!consume(U')')) {
      fail("missing ), unterminated assertion", offset);
    }
    if ((kind == NodeKind::look_behind ||
         kind == NodeKind::negative_look_behind) &&
        (body->minimum_width != body->maximum_width ||
         body->maximum_width == unbounded)) {
      fail("look-behind requires fixed-width pattern", offset);
    }
    NodePointer result = node(kind, flags_);
    result->minimum = body->minimum_width;
    result->children.push_back(std::move(body));
    return result;
  }

  [[nodiscard]] NodePointer parse_conditional(std::size_t offset) {
    std::size_t group = 0;
    if (ascii_digit(peek())) {
      group = parse_decimal(offset);
      if (!consume(U')')) {
        fail("missing ), unterminated group reference", offset);
      }
    } else {
      const std::string name = parse_name(U')', offset);
      const auto found = group_names_.find(name);
      if (found == group_names_.end()) {
        fail("unknown group name in conditional", offset);
      }
      group = found->second;
    }
    if (group == 0 || group > group_count_) {
      fail("invalid group reference in conditional", offset);
    }
    NodePointer yes = parse_sequence();
    NodePointer no = node(NodeKind::empty, flags_);
    if (consume(U'|')) {
      no = parse_sequence();
      if (peek() == U'|') {
        fail("conditional backref with more than two branches", offset);
      }
    }
    if (!consume(U')')) {
      fail("missing ), unterminated conditional", offset);
    }
    NodePointer result = node(NodeKind::conditional, flags_);
    result->group = group;
    result->minimum_width = std::min(yes->minimum_width, no->minimum_width);
    result->maximum_width = std::max(yes->maximum_width, no->maximum_width);
    result->children.push_back(std::move(yes));
    result->children.push_back(std::move(no));
    return result;
  }

  [[nodiscard]] NodePointer parse_group(std::size_t offset) {
    if (!consume(U'?')) {
      return parse_capturing_group(offset, {});
    }
    if (consume(U'#')) {
      while (!at_end() && peek() != U')') {
        ++position_;
      }
      if (!consume(U')')) {
        fail("missing ), unterminated comment", offset);
      }
      return node(NodeKind::empty, flags_);
    }
    if (consume(U':')) {
      NodePointer content = parse_alternation();
      if (!consume(U')')) {
        fail("missing ), unterminated subpattern", offset);
      }
      return content;
    }
    if (consume(U'=')) {
      return parse_assertion(NodeKind::look_ahead, offset);
    }
    if (consume(U'!')) {
      return parse_assertion(NodeKind::negative_look_ahead, offset);
    }
    if (consume(U'>')) {
      NodePointer content = parse_alternation();
      if (!consume(U')')) {
        fail("missing ), unterminated atomic group", offset);
      }
      NodePointer result = node(NodeKind::atomic, content->flags);
      result->minimum_width = content->minimum_width;
      result->maximum_width = content->maximum_width;
      result->children.push_back(std::move(content));
      return result;
    }
    if (consume(U'<')) {
      if (consume(U'=')) {
        return parse_assertion(NodeKind::look_behind, offset);
      }
      if (consume(U'!')) {
        return parse_assertion(NodeKind::negative_look_behind, offset);
      }
      fail("unknown extension", offset);
    }
    if (consume(U'P')) {
      if (consume(U'<')) {
        return parse_capturing_group(offset, parse_name(U'>', offset));
      }
      if (consume(U'=')) {
        const std::string name = parse_name(U')', offset);
        const auto found = group_names_.find(name);
        if (found == group_names_.end() ||
            std::find(open_groups_.begin(), open_groups_.end(),
                      found->second) != open_groups_.end()) {
          fail("unknown group name", offset);
        }
        NodePointer reference = node(NodeKind::back_reference, flags_);
        reference->group = found->second;
        reference->maximum_width = unbounded;
        return reference;
      }
      fail("unknown extension ?P", offset);
    }
    if (consume(U'(')) {
      return parse_conditional(offset);
    }
    if (ascii_letter(peek()) || peek() == U'-') {
      return parse_inline_flags(offset);
    }
    fail("unknown regular-expression extension", offset);
  }

  TextView pattern_;
  Encoding encoding_;
  std::uint32_t flags_;
  const CharacterProperties& properties_;
  std::size_t position_ = 0;
  std::size_t group_count_ = 0;
  std::unordered_map<std::string, std::size_t> group_names_;
  std::vector<std::size_t> open_groups_;
};

class Emitter final {
 public:
  explicit Emitter(Program& program) : program_(program) {}

  void emit_root(const NodePointer& root) {
    emit(root);
    append(Opcode::accept, root->flags);
  }

 private:
  [[nodiscard]] std::size_t append(Opcode opcode, std::uint32_t flags) {
    Instruction instruction;
    instruction.opcode = opcode;
    instruction.flags = flags;
    program_.instructions_.push_back(std::move(instruction));
    return program_.instructions_.size() - 1;
  }

  void emit_alternative(const NodePointer& source,
                        std::size_t index = 0) {
    if (index + 1 == source->children.size()) {
      emit(source->children[index]);
      return;
    }
    const std::size_t split = append(Opcode::split, source->flags);
    program_.instructions_[split].first = program_.instructions_.size();
    emit(source->children[index]);
    const std::size_t jump = append(Opcode::jump, source->flags);
    program_.instructions_[split].second = program_.instructions_.size();
    emit_alternative(source, index + 1);
    program_.instructions_[jump].first = program_.instructions_.size();
  }

  void emit_repeat(const NodePointer& source) {
    if (source->possessive) {
      append(Opcode::atomic_enter, source->flags);
    }
    const std::size_t repeat_slot = program_.progress_count_++;
    const std::size_t enter = append(Opcode::repeat_enter, source->flags);
    program_.instructions_[enter].argument = repeat_slot;
    const std::size_t branch = append(Opcode::repeat_branch, source->flags);
    program_.instructions_[branch].argument = repeat_slot;
    program_.instructions_[branch].minimum = source->minimum;
    program_.instructions_[branch].maximum = source->maximum;
    program_.instructions_[branch].prefer_first = source->greedy;
    program_.instructions_[branch].first = program_.instructions_.size();
    emit(source->children[0]);
    const std::size_t advance =
        append(Opcode::repeat_advance, source->flags);
    program_.instructions_[advance].argument = repeat_slot;
    program_.instructions_[advance].first = branch;
    program_.instructions_[branch].second = program_.instructions_.size();
    if (source->possessive) {
      append(Opcode::atomic_leave, source->flags);
    }
  }

  void emit_look(const NodePointer& source, Opcode opcode) {
    auto assertion = std::make_shared<Program>();
    assertion->group_count_ = program_.group_count_;
    assertion->group_names_ = program_.group_names_;
    assertion->properties_ = program_.properties_;
    assertion->flags_ = source->flags;
    assertion->encoding_ = program_.encoding_;
    assertion->minimum_width_ = source->children[0]->minimum_width;
    assertion->maximum_width_ = source->children[0]->maximum_width;
    Emitter nested(*assertion);
    nested.emit_root(source->children[0]);
    const std::size_t index = append(opcode, source->flags);
    program_.instructions_[index].assertion = std::move(assertion);
    program_.instructions_[index].argument = source->minimum;
  }

  void emit(const NodePointer& source) {
    switch (source->kind) {
      case NodeKind::empty:
        return;
      case NodeKind::literal: {
        const auto index = append(Opcode::literal, source->flags);
        program_.instructions_[index].character = source->character;
        return;
      }
      case NodeKind::any:
        append(Opcode::any, source->flags);
        return;
      case NodeKind::character_class: {
        const auto index = append(Opcode::character_class, source->flags);
        program_.instructions_[index].character_class =
            source->character_class;
        return;
      }
      case NodeKind::beginning:
        append(Opcode::assert_beginning, source->flags);
        return;
      case NodeKind::absolute_beginning:
        append(Opcode::assert_absolute_beginning, source->flags);
        return;
      case NodeKind::end:
        append(Opcode::assert_end, source->flags);
        return;
      case NodeKind::absolute_end:
        append(Opcode::assert_absolute_end, source->flags);
        return;
      case NodeKind::word_boundary:
        append(Opcode::assert_word_boundary, source->flags);
        return;
      case NodeKind::not_word_boundary:
        append(Opcode::assert_not_word_boundary, source->flags);
        return;
      case NodeKind::sequence:
        for (const NodePointer& child : source->children) {
          emit(child);
        }
        return;
      case NodeKind::alternative:
        emit_alternative(source);
        return;
      case NodeKind::capture: {
        const auto begin = append(Opcode::save, source->flags);
        program_.instructions_[begin].argument = source->group * 2;
        emit(source->children[0]);
        const auto end = append(Opcode::save, source->flags);
        program_.instructions_[end].argument = source->group * 2 + 1;
        return;
      }
      case NodeKind::repeat:
        emit_repeat(source);
        return;
      case NodeKind::back_reference: {
        const auto index = append(Opcode::back_reference, source->flags);
        program_.instructions_[index].argument = source->group;
        return;
      }
      case NodeKind::conditional: {
        const auto branch = append(Opcode::conditional, source->flags);
        program_.instructions_[branch].argument = source->group;
        program_.instructions_[branch].first = program_.instructions_.size();
        emit(source->children[0]);
        const auto jump = append(Opcode::jump, source->flags);
        program_.instructions_[branch].second =
            program_.instructions_.size();
        emit(source->children[1]);
        program_.instructions_[jump].first = program_.instructions_.size();
        return;
      }
      case NodeKind::look_ahead:
        emit_look(source, Opcode::look_ahead);
        return;
      case NodeKind::negative_look_ahead:
        emit_look(source, Opcode::negative_look_ahead);
        return;
      case NodeKind::look_behind:
        emit_look(source, Opcode::look_behind);
        return;
      case NodeKind::negative_look_behind:
        emit_look(source, Opcode::negative_look_behind);
        return;
      case NodeKind::atomic:
        append(Opcode::atomic_enter, source->flags);
        emit(source->children[0]);
        append(Opcode::atomic_leave, source->flags);
        return;
    }
  }

  Program& program_;
};

struct Frame {
  std::size_t instruction = 0;
  std::size_t position = 0;
  std::vector<Span> captures;
  std::vector<std::size_t> repeat_counts;
  std::vector<std::size_t> repeat_positions;
  std::vector<std::size_t> atomic_boundaries;
  std::size_t last_group = 0;
};

[[nodiscard]] std::optional<Result> execute_program(
    const Program& program, TextView subject, std::size_t position,
    std::size_t end_position, bool require_full, const Limits& limits,
    bool reject_empty = false,
    const std::vector<Span>* inherited = nullptr) {
  if (position > end_position || end_position > subject.size()) {
    return std::nullopt;
  }

  Frame state;
  state.position = position;
  state.captures = inherited == nullptr
                       ? std::vector<Span>(program.group_count() + 1)
                       : *inherited;
  if (state.captures.size() != program.group_count() + 1) {
    throw ResourceError("assertion capture state has the wrong size");
  }
  state.captures[0].begin = position;
  state.repeat_counts.assign(program.progress_count(), 0);
  state.repeat_positions.assign(program.progress_count(), no_position);
  std::vector<Frame> alternatives;
  std::size_t steps = 0;

  auto push = [&](Frame alternative) {
    if (alternatives.size() >= limits.maximum_backtracking_frames) {
      throw ResourceError("regular-expression backtracking limit exceeded");
    }
    alternatives.push_back(std::move(alternative));
  };

  auto backtrack = [&]() -> bool {
    if (alternatives.empty()) {
      return false;
    }
    state = std::move(alternatives.back());
    alternatives.pop_back();
    return true;
  };

  for (;;) {
    if (steps == limits.maximum_steps) {
      throw ResourceError("regular-expression instruction limit exceeded");
    }
    ++steps;
    if (state.instruction >= program.instructions().size()) {
      throw ResourceError("regular-expression instruction escaped its program");
    }
    const Instruction& operation =
        program.instructions()[state.instruction];
    bool failed = false;

    switch (operation.opcode) {
      case Opcode::literal:
        if (state.position == end_position ||
            !equal_character(subject[state.position], operation.character,
                             operation.flags, program.encoding(),
                             program.properties())) {
          failed = true;
        } else {
          ++state.position;
          ++state.instruction;
        }
        break;

      case Opcode::any:
        if (state.position == end_position ||
            ((operation.flags & flag_dotall) == 0 &&
             subject[state.position] == U'\n')) {
          failed = true;
        } else {
          ++state.position;
          ++state.instruction;
        }
        break;

      case Opcode::character_class:
        if (state.position == end_position ||
            !operation.character_class ||
            !class_matches(*operation.character_class,
                           subject[state.position], operation.flags,
                           program.encoding(), program.properties())) {
          failed = true;
        } else {
          ++state.position;
          ++state.instruction;
        }
        break;

      case Opcode::assert_beginning:
        if (state.position != 0 &&
            ((operation.flags & flag_multiline) == 0 ||
             subject[state.position - 1] != U'\n')) {
          failed = true;
        } else {
          ++state.instruction;
        }
        break;

      case Opcode::assert_absolute_beginning:
        if (state.position != 0) {
          failed = true;
        } else {
          ++state.instruction;
        }
        break;

      case Opcode::assert_end: {
        const bool at_final_newline =
            state.position + 1 == end_position &&
            subject[state.position] == U'\n';
        const bool at_line_end =
            state.position < end_position &&
            (operation.flags & flag_multiline) != 0 &&
            subject[state.position] == U'\n';
        if (state.position != end_position && !at_final_newline &&
            !at_line_end) {
          failed = true;
        } else {
          ++state.instruction;
        }
        break;
      }

      case Opcode::assert_absolute_end:
        if (state.position != end_position) {
          failed = true;
        } else {
          ++state.instruction;
        }
        break;

      case Opcode::assert_word_boundary:
      case Opcode::assert_not_word_boundary: {
        const bool before =
            state.position != 0 &&
            category_matches(Category::word,
                             subject[state.position - 1], operation.flags,
                             program.encoding(), program.properties());
        const bool after =
            state.position < end_position &&
            category_matches(Category::word, subject[state.position],
                             operation.flags, program.encoding(),
                             program.properties());
        const bool boundary = before != after;
        if (boundary !=
            (operation.opcode == Opcode::assert_word_boundary)) {
          failed = true;
        } else {
          ++state.instruction;
        }
        break;
      }

      case Opcode::save: {
        const std::size_t group = operation.argument / 2;
        if (group >= state.captures.size()) {
          throw ResourceError("capture instruction escaped its group table");
        }
        if ((operation.argument & 1U) == 0) {
          state.captures[group].begin = state.position;
          state.captures[group].end = no_position;
        } else {
          state.captures[group].end = state.position;
          state.last_group = group;
        }
        ++state.instruction;
        break;
      }

      case Opcode::split: {
        Frame alternative = state;
        alternative.instruction = operation.second;
        push(std::move(alternative));
        state.instruction = operation.first;
        break;
      }

      case Opcode::jump:
        state.instruction = operation.first;
        break;

      case Opcode::progress:
        if (operation.argument >= state.repeat_positions.size()) {
          throw ResourceError("progress instruction escaped its state table");
        }
        if (state.repeat_positions[operation.argument] == state.position) {
          failed = true;
        } else {
          state.repeat_positions[operation.argument] = state.position;
          ++state.instruction;
        }
        break;

      case Opcode::repeat_enter:
        if (operation.argument >= state.repeat_counts.size()) {
          throw ResourceError("repeat instruction escaped its state table");
        }
        state.repeat_counts[operation.argument] = 0;
        state.repeat_positions[operation.argument] = no_position;
        ++state.instruction;
        break;

      case Opcode::repeat_branch: {
        if (operation.argument >= state.repeat_counts.size()) {
          throw ResourceError("repeat branch escaped its state table");
        }
        const std::size_t count = state.repeat_counts[operation.argument];
        const bool can_exit = count >= operation.minimum;
        const bool progressed = count == 0 ||
                                state.repeat_positions[operation.argument] !=
                                    state.position ||
                                count < operation.minimum;
        const bool can_enter =
            count < operation.maximum && progressed;
        if (!can_enter && !can_exit) {
          failed = true;
          break;
        }
        if (can_enter && can_exit) {
          Frame alternative = state;
          if (operation.prefer_first) {
            alternative.instruction = operation.second;
            push(std::move(alternative));
            state.repeat_positions[operation.argument] = state.position;
            state.instruction = operation.first;
          } else {
            alternative.repeat_positions[operation.argument] = state.position;
            alternative.instruction = operation.first;
            push(std::move(alternative));
            state.instruction = operation.second;
          }
        } else if (can_enter) {
          state.repeat_positions[operation.argument] = state.position;
          state.instruction = operation.first;
        } else {
          state.instruction = operation.second;
        }
        break;
      }

      case Opcode::repeat_advance:
        if (operation.argument >= state.repeat_counts.size() ||
            state.repeat_counts[operation.argument] == unbounded) {
          throw ResourceError("repeat count escaped its state table");
        }
        ++state.repeat_counts[operation.argument];
        state.instruction = operation.first;
        break;

      case Opcode::back_reference: {
        if (operation.argument >= state.captures.size()) {
          throw ResourceError("back reference escaped its group table");
        }
        const Span& capture = state.captures[operation.argument];
        if (!capture.matched() || capture.end < capture.begin ||
            capture.end - capture.begin > end_position - state.position) {
          failed = true;
          break;
        }
        const std::size_t length = capture.end - capture.begin;
        for (std::size_t index = 0; index < length; ++index) {
          if (!equal_character(subject[capture.begin + index],
                               subject[state.position + index],
                               operation.flags, program.encoding(),
                               program.properties())) {
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

      case Opcode::conditional:
        if (operation.argument >= state.captures.size()) {
          throw ResourceError("conditional escaped its group table");
        }
        state.instruction = state.captures[operation.argument].matched()
                                ? operation.first
                                : operation.second;
        break;

      case Opcode::look_ahead:
      case Opcode::negative_look_ahead:
      case Opcode::look_behind:
      case Opcode::negative_look_behind: {
        if (!operation.assertion) {
          throw ResourceError("assertion does not own a compiled subprogram");
        }
        const bool behind = operation.opcode == Opcode::look_behind ||
                            operation.opcode == Opcode::negative_look_behind;
        const bool positive = operation.opcode == Opcode::look_ahead ||
                              operation.opcode == Opcode::look_behind;
        std::optional<Result> asserted;
        if (!behind || state.position >= operation.argument) {
          asserted = execute_program(
              *operation.assertion, subject,
              behind ? state.position - operation.argument : state.position,
              behind ? state.position : end_position, behind, limits, false,
              &state.captures);
        }
        if (asserted.has_value() != positive) {
          failed = true;
        } else {
          if (positive) {
            state.captures = std::move(asserted->groups);
            state.captures[0].begin = position;
            state.captures[0].end = no_position;
            state.last_group = asserted->last_group;
          }
          ++state.instruction;
        }
        break;
      }

      case Opcode::atomic_enter:
        state.atomic_boundaries.push_back(alternatives.size());
        ++state.instruction;
        break;

      case Opcode::atomic_leave:
        if (state.atomic_boundaries.empty() ||
            state.atomic_boundaries.back() > alternatives.size()) {
          throw ResourceError("atomic group escaped its backtracking stack");
        }
        alternatives.resize(state.atomic_boundaries.back());
        state.atomic_boundaries.pop_back();
        ++state.instruction;
        break;

      case Opcode::accept:
        if ((require_full && state.position != end_position) ||
            (reject_empty && state.position == position)) {
          failed = true;
        } else {
          state.captures[0].begin = position;
          state.captures[0].end = state.position;
          return Result{std::move(state.captures), state.last_group};
        }
        break;
    }

    if (failed && !backtrack()) {
      return std::nullopt;
    }
  }
}

[[nodiscard]] std::optional<Rune> template_escape(Rune escaped) {
  switch (escaped) {
    case U'a':
      return U'\a';
    case U'b':
      return U'\b';
    case U'f':
      return U'\f';
    case U'n':
      return U'\n';
    case U'r':
      return U'\r';
    case U't':
      return U'\t';
    case U'v':
      return U'\v';
    case U'\\':
      return U'\\';
    default:
      return std::nullopt;
  }
}

}  // namespace

Compiler::Compiler(CharacterProperties properties)
    : properties_(std::move(properties)) {}

Program Compiler::compile(TextView pattern, Encoding encoding,
                          std::uint32_t flags) const {
  Parser parser(pattern, encoding, flags, properties_);
  NodePointer root = parser.parse();
  Program result;
  result.properties_ = properties_;
  result.pattern_.assign(pattern);
  result.encoding_ = encoding;
  result.flags_ = parser.flags();
  result.group_count_ = parser.group_count();
  result.group_names_ = parser.group_names();
  result.minimum_width_ = root->minimum_width;
  result.maximum_width_ = root->maximum_width;
  Emitter emitter(result);
  emitter.emit_root(root);
  return result;
}

std::optional<Result> Machine::run_at(const Program& program,
                                      TextView subject,
                                      std::size_t position,
                                      std::size_t end_position,
                                      bool require_full,
                                      bool reject_empty) const {
  return execute_program(program, subject, position, end_position,
                         require_full, limits_, reject_empty);
}

std::optional<Result> Machine::run(const Program& program, TextView subject,
                                   std::size_t position,
                                   std::size_t end_position,
                                   MatchMode mode,
                                   bool reject_empty) const {
  end_position = std::min(end_position, subject.size());
  position = std::min(position, subject.size());
  if (position > end_position) {
    return std::nullopt;
  }
  if (mode != MatchMode::search) {
    return run_at(program, subject, position, end_position,
                  mode == MatchMode::fullmatch, reject_empty);
  }
  for (std::size_t candidate = position;; ++candidate) {
    if (program.minimum_width() > end_position - candidate) {
      return std::nullopt;
    }
    if (std::optional<Result> matched =
            run_at(program, subject, candidate, end_position, false,
                   reject_empty)) {
      return matched;
    }
    if (candidate == end_position) {
      return std::nullopt;
    }
  }
}

std::vector<TemplatePart> parse_template(TextView replacement,
                                         const Program& program) {
  std::vector<TemplatePart> result;
  Text current;
  const auto flush = [&]() {
    if (!current.empty()) {
      result.push_back(TemplatePart{TemplateKind::literal,
                                    std::exchange(current, Text{}), 0});
    }
  };
  for (std::size_t position = 0; position < replacement.size(); ++position) {
    const Rune character = replacement[position];
    if (character != U'\\') {
      current.push_back(character);
      continue;
    }
    if (++position == replacement.size()) {
      throw PatternError("bad escape (end of replacement)", position - 1);
    }
    const Rune escaped = replacement[position];
    if (const auto simple = template_escape(escaped)) {
      current.push_back(*simple);
      continue;
    }
    if (escaped == U'g') {
      if (++position == replacement.size() || replacement[position] != U'<') {
        throw PatternError("missing < in group name", position);
      }
      const std::size_t start = ++position;
      while (position < replacement.size() && replacement[position] != U'>') {
        ++position;
      }
      if (position == replacement.size() || position == start) {
        throw PatternError("missing or unterminated group name", start);
      }
      const TextView name = replacement.substr(start, position - start);
      std::size_t group = 0;
      if (std::all_of(name.begin(), name.end(), ascii_digit)) {
        for (Rune digit : name) {
          const auto value = static_cast<std::size_t>(digit - U'0');
          if (group > (unbounded - value) / 10) {
            throw PatternError("invalid group reference", start);
          }
          group = group * 10 + value;
        }
      } else {
        std::string narrow;
        for (Rune letter : name) {
          if (letter > 0x7f) {
            throw PatternError("bad character in group name", start);
          }
          narrow.push_back(static_cast<char>(letter));
        }
        const auto found = program.group_names().find(narrow);
        if (found == program.group_names().end()) {
          throw PatternError("unknown group name", start);
        }
        group = found->second;
      }
      if (group > program.group_count()) {
        throw PatternError("invalid group reference", start);
      }
      flush();
      result.push_back(TemplatePart{TemplateKind::group, {}, group});
      continue;
    }
    if (ascii_digit(escaped)) {
      if (escaped == U'0') {
        std::uint32_t value = 0;
        for (std::size_t index = 0;
             index < 2 && position + 1 < replacement.size() &&
             replacement[position + 1] >= U'0' &&
             replacement[position + 1] <= U'7'; ++index) {
          value = value * 8 +
                  static_cast<std::uint32_t>(replacement[++position] - U'0');
        }
        current.push_back(static_cast<Rune>(value));
        continue;
      }
      std::size_t group = static_cast<std::size_t>(escaped - U'0');
      if (position + 1 < replacement.size() &&
          ascii_digit(replacement[position + 1])) {
        group = group * 10 +
                static_cast<std::size_t>(replacement[++position] - U'0');
      }
      if (group > program.group_count()) {
        throw PatternError("invalid group reference", position);
      }
      flush();
      result.push_back(TemplatePart{TemplateKind::group, {}, group});
      continue;
    }
    if (ascii_letter(escaped)) {
      throw PatternError("bad escape in replacement", position - 1);
    }
    current.push_back(U'\\');
    current.push_back(escaped);
  }
  flush();
  return result;
}

Text expand_template(const std::vector<TemplatePart>& parts,
                     const Result& match, TextView subject) {
  Text result;
  for (const TemplatePart& part : parts) {
    if (part.kind == TemplateKind::literal) {
      result += part.literal;
      continue;
    }
    if (part.group >= match.groups.size()) {
      throw ResourceError("replacement escaped its capture table");
    }
    const Span& captured = match.groups[part.group];
    if (captured.matched()) {
      if (captured.end < captured.begin || captured.end > subject.size()) {
        throw ResourceError("replacement capture escaped its subject");
      }
      result.append(subject.substr(captured.begin,
                                   captured.end - captured.begin));
    }
  }
  return result;
}

Text escape_pattern(TextView source) {
  constexpr std::array<Rune, 24> escaped = {
      U'#', U'$', U'&', U'(', U')', U'*', U'+', U'-', U'.', U'?',
      U'[', U'\\', U']', U'^', U'{', U'|', U'}', U'~', U' ', U'\t',
      U'\n', U'\r', U'\v', U'\f',
  };
  Text result;
  result.reserve(source.size());
  for (Rune character : source) {
    if (std::find(escaped.begin(), escaped.end(), character) !=
        escaped.end()) {
      result.push_back(U'\\');
    }
    result.push_back(character);
  }
  return result;
}

}  // namespace rebar::experimental::cpp_v1
