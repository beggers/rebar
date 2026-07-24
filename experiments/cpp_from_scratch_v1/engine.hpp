// An independently written regular-expression experiment.
// This file intentionally has no dependency on an existing regex engine.
#ifndef REBAR_EXPERIMENTS_CPP_FROM_SCRATCH_V1_ENGINE_HPP
#define REBAR_EXPERIMENTS_CPP_FROM_SCRATCH_V1_ENGINE_HPP

#include <cstddef>
#include <cstdint>
#include <functional>
#include <limits>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <unordered_map>
#include <utility>
#include <vector>

namespace rebar::experimental::cpp_v1 {

using Rune = char32_t;
using Text = std::u32string;
using TextView = std::u32string_view;

inline constexpr std::size_t no_position =
    std::numeric_limits<std::size_t>::max();

// These values are Python's public re.RegexFlag integer values. They do not
// require importing Python's regular-expression implementation.
enum Flag : std::uint32_t {
  flag_template = 0x001,
  flag_ignore_case = 0x002,
  flag_locale = 0x004,
  flag_multiline = 0x008,
  flag_dotall = 0x010,
  flag_unicode = 0x020,
  flag_verbose = 0x040,
  flag_debug = 0x080,
  flag_ascii = 0x100,
};

enum class Encoding : std::uint8_t { unicode, bytes };

class PatternError final : public std::runtime_error {
 public:
  PatternError(std::string message, std::size_t offset,
               std::size_t line = 1, std::size_t column = 1);

  [[nodiscard]] std::size_t offset() const noexcept { return offset_; }
  [[nodiscard]] std::size_t line() const noexcept { return line_; }
  [[nodiscard]] std::size_t column() const noexcept { return column_; }

 private:
  std::size_t offset_;
  std::size_t line_;
  std::size_t column_;
};

class ResourceError final : public std::runtime_error {
 public:
  using std::runtime_error::runtime_error;
};

// Public Python Unicode classification can be supplied by the direct Python
// bridge. These functions classify characters; they do not perform matching.
struct CharacterProperties {
  std::function<bool(Rune)> unicode_decimal;
  std::function<bool(Rune)> unicode_space;
  std::function<bool(Rune)> unicode_alphanumeric;
  std::function<Rune(Rune)> unicode_lower;
  std::function<Rune(Rune)> unicode_upper;
  std::function<std::optional<Rune>(std::string_view)> unicode_name;
};

enum class Category : std::uint8_t {
  digit,
  not_digit,
  space,
  not_space,
  word,
  not_word,
};

struct CharacterRange {
  Rune first{};
  Rune last{};
};

struct CharacterClass {
  bool negated = false;
  std::vector<CharacterRange> ranges;
  std::vector<Category> categories;
};

struct Span {
  std::size_t begin = no_position;
  std::size_t end = no_position;

  [[nodiscard]] bool matched() const noexcept {
    return begin != no_position && end != no_position;
  }

  friend bool operator==(const Span&, const Span&) = default;
};

struct Result {
  std::vector<Span> groups;
  std::size_t last_group = 0;

  [[nodiscard]] const Span& whole() const noexcept { return groups[0]; }
};

enum class Opcode : std::uint8_t {
  literal,
  any,
  character_class,
  assert_beginning,
  assert_absolute_beginning,
  assert_end,
  assert_absolute_end,
  assert_word_boundary,
  assert_not_word_boundary,
  save,
  split,
  jump,
  progress,
  repeat_enter,
  repeat_branch,
  repeat_advance,
  back_reference,
  conditional,
  look_ahead,
  negative_look_ahead,
  look_behind,
  negative_look_behind,
  atomic_enter,
  atomic_leave,
  accept,
};

class Program;

struct Instruction {
  Opcode opcode = Opcode::accept;
  std::uint32_t flags = 0;
  Rune character = U'\0';
  std::size_t first = no_position;
  std::size_t second = no_position;
  std::size_t argument = 0;
  std::size_t minimum = 0;
  std::size_t maximum = 0;
  bool prefer_first = true;
  std::shared_ptr<const CharacterClass> character_class;
  std::shared_ptr<const Program> assertion;
};

struct Limits {
  std::size_t maximum_steps = std::numeric_limits<std::size_t>::max();
  std::size_t maximum_backtracking_frames =
      std::numeric_limits<std::size_t>::max();
};

class Program final {
 public:
  Program() = default;

  [[nodiscard]] const std::vector<Instruction>& instructions()
      const noexcept {
    return instructions_;
  }
  [[nodiscard]] std::size_t group_count() const noexcept {
    return group_count_;
  }
  [[nodiscard]] std::size_t progress_count() const noexcept {
    return progress_count_;
  }
  [[nodiscard]] std::size_t minimum_width() const noexcept {
    return minimum_width_;
  }
  [[nodiscard]] std::size_t maximum_width() const noexcept {
    return maximum_width_;
  }
  [[nodiscard]] std::uint32_t flags() const noexcept { return flags_; }
  [[nodiscard]] Encoding encoding() const noexcept { return encoding_; }
  [[nodiscard]] const Text& pattern() const noexcept { return pattern_; }
  [[nodiscard]] const std::unordered_map<std::string, std::size_t>&
  group_names() const noexcept {
    return group_names_;
  }
  [[nodiscard]] const CharacterProperties& properties() const noexcept {
    return properties_;
  }

 public:
  // Exposed only as this experiment's own bytecode format. The Python bridge
  // never accepts or loads bytecode supplied by a different implementation.
  friend class Compiler;

  std::vector<Instruction> instructions_;
  std::unordered_map<std::string, std::size_t> group_names_;
  CharacterProperties properties_;
  Text pattern_;
  std::size_t group_count_ = 0;
  std::size_t progress_count_ = 0;
  std::size_t minimum_width_ = 0;
  std::size_t maximum_width_ = 0;
  std::uint32_t flags_ = 0;
  Encoding encoding_ = Encoding::unicode;
};

class Compiler final {
 public:
  explicit Compiler(CharacterProperties properties = {});

  [[nodiscard]] Program compile(TextView pattern, Encoding encoding,
                                std::uint32_t flags = 0) const;

 private:
  CharacterProperties properties_;
};

enum class MatchMode : std::uint8_t { search, match, fullmatch };

class Machine final {
 public:
  explicit Machine(Limits limits = {}) noexcept : limits_(limits) {}

  [[nodiscard]] std::optional<Result> run(const Program& program,
                                          TextView subject,
                                          std::size_t position,
                                          std::size_t end_position,
                                          MatchMode mode,
                                          bool reject_empty = false) const;

 private:
  [[nodiscard]] std::optional<Result> run_at(const Program& program,
                                             TextView subject,
                                             std::size_t position,
                                             std::size_t end_position,
                                             bool require_full,
                                             bool reject_empty = false) const;

  Limits limits_;
};

enum class TemplateKind : std::uint8_t { literal, group };

struct TemplatePart {
  TemplateKind kind = TemplateKind::literal;
  Text literal;
  std::size_t group = 0;
};

[[nodiscard]] std::vector<TemplatePart> parse_template(
    TextView replacement, const Program& program);

[[nodiscard]] Text expand_template(const std::vector<TemplatePart>& parts,
                                   const Result& match, TextView subject);

[[nodiscard]] Text escape_pattern(TextView source);

}  // namespace rebar::experimental::cpp_v1

#endif  // REBAR_EXPERIMENTS_CPP_FROM_SCRATCH_V1_ENGINE_HPP
