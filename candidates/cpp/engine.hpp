#ifndef REBAR_CPP_ENGINE_HPP
#define REBAR_CPP_ENGINE_HPP

#include <cstddef>
#include <cstdint>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <unordered_map>
#include <utility>
#include <vector>

namespace rebar_cpp {

inline constexpr std::uint32_t flag_ignorecase = 2;
inline constexpr std::uint32_t flag_locale = 4;
inline constexpr std::uint32_t flag_multiline = 8;
inline constexpr std::uint32_t flag_dotall = 16;
inline constexpr std::uint32_t flag_unicode = 32;
inline constexpr std::uint32_t flag_verbose = 64;
inline constexpr std::uint32_t flag_debug = 128;
inline constexpr std::uint32_t flag_ascii = 256;
inline constexpr std::size_t no_position =
    std::numeric_limits<std::size_t>::max();

enum class Category : std::uint8_t { digit, space, word };

struct CharacterTraits {
    void* context = nullptr;
    bool (*classify)(void*, Category, char32_t, std::uint32_t, bool) = nullptr;
    char32_t (*lower)(void*, char32_t, std::uint32_t, bool) = nullptr;
    bool (*lookup_name)(void*, std::u32string_view, char32_t*) = nullptr;
    bool (*valid_group_name)(void*, std::u32string_view, bool) = nullptr;
    bool (*check_interrupt)(void*) = nullptr;
    bool (*enter_recursion)(void*) = nullptr;
    void (*leave_recursion)(void*) = nullptr;
};

class CompileError final : public std::runtime_error {
public:
    CompileError(std::string message, std::size_t position);

    [[nodiscard]] std::size_t position() const noexcept;

private:
    std::size_t position_;
};

class Interrupted final : public std::runtime_error {
public:
    Interrupted();
};

struct CharacterRange {
    char32_t first = 0;
    char32_t last = 0;
};

struct CategoryEntry {
    Category category = Category::digit;
    bool complement = false;
};

struct CharacterClass {
    bool complement = false;
    std::vector<CharacterRange> ranges;
    std::vector<CategoryEntry> categories;
};

enum class Opcode : std::uint8_t {
    character,
    any,
    character_class,
    begin_line,
    end_line,
    begin_subject,
    end_subject,
    word_boundary,
    not_word_boundary,
    jump,
    split,
    save,
    backreference,
    repeat_begin,
    repeat_end,
    assert_ahead,
    assert_not_ahead,
    assert_behind,
    assert_not_behind,
    atomic_begin,
    atomic_end,
    conditional,
    accept,
};

struct Instruction {
    Opcode opcode = Opcode::accept;
    std::uint32_t first = 0;
    std::uint32_t second = 0;
    std::uint32_t flags = 0;
    char32_t character = U'\0';
};

struct Repeat {
    std::size_t minimum = 0;
    std::size_t maximum = no_position;
    bool lazy = false;
};

struct Assertion {
    std::vector<Instruction> instructions;
    std::size_t width = 0;
};

struct Program {
    std::u32string pattern;
    bool bytes = false;
    std::uint32_t flags = 0;
    std::size_t group_count = 0;
    std::unordered_map<std::u32string, std::size_t> group_names;
    std::vector<CharacterClass> classes;
    std::vector<Repeat> repeats;
    std::vector<Assertion> assertions;
    std::vector<Instruction> instructions;
    CharacterTraits traits;
};

struct Subject {
    const void* data = nullptr;
    std::size_t length = 0;
    std::uint8_t kind = 1;
    bool bytes = false;

    [[nodiscard]] char32_t read(std::size_t offset) const noexcept;
};

struct Capture {
    std::size_t first = no_position;
    std::size_t last = no_position;

    [[nodiscard]] bool matched() const noexcept;
};

struct Match {
    std::vector<Capture> captures;
    std::optional<std::size_t> last_index;
};

[[nodiscard]] Program compile(
    std::u32string pattern,
    bool bytes,
    std::uint32_t flags,
    CharacterTraits traits
);

[[nodiscard]] std::optional<Match> match_at(
    const Program& program,
    const Subject& subject,
    std::size_t start,
    std::size_t end,
    bool full,
    bool nonempty
);

[[nodiscard]] std::optional<Match> search(
    const Program& program,
    const Subject& subject,
    std::size_t start,
    std::size_t end,
    bool nonempty
);

}  // namespace rebar_cpp

#endif
