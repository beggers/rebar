// A direct CPython C-API bridge for the independently written C++ experiment.
// It never imports re, _sre, another candidate, or a regex package.

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "engine.hpp"

#include <algorithm>
#include <cstdint>
#include <exception>
#include <limits>
#include <memory>
#include <new>
#include <optional>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace {

namespace rx = rebar::experimental::cpp_v1;

class Owned final {
 public:
  explicit Owned(PyObject* object = nullptr) noexcept : object_(object) {}
  ~Owned() { Py_XDECREF(object_); }
  Owned(const Owned&) = delete;
  Owned& operator=(const Owned&) = delete;
  Owned(Owned&& other) noexcept
      : object_(std::exchange(other.object_, nullptr)) {}
  Owned& operator=(Owned&& other) noexcept {
    if (this != &other) {
      Py_XDECREF(object_);
      object_ = std::exchange(other.object_, nullptr);
    }
    return *this;
  }

  [[nodiscard]] PyObject* get() const noexcept { return object_; }
  [[nodiscard]] PyObject* release() noexcept {
    return std::exchange(object_, nullptr);
  }
  [[nodiscard]] explicit operator bool() const noexcept {
    return object_ != nullptr;
  }

 private:
  PyObject* object_;
};

struct PatternObject {
  PyObject_HEAD
  rx::Program* program;
  PyObject* original;
};

struct MatchObject {
  PyObject_HEAD
  PatternObject* pattern;
  PyObject* subject;
  rx::Result* result;
  Py_ssize_t position;
  Py_ssize_t end_position;
};

struct Cursor {
  std::size_t position = 0;
  std::size_t end_position = 0;
  bool retry_nonempty = false;
  bool exhausted = false;
};

struct IteratorObject {
  PyObject_HEAD
  PatternObject* pattern;
  PyObject* subject;
  rx::Text* decoded;
  Cursor* cursor;
};

struct ScannerObject {
  PyObject_HEAD
  PatternObject* pattern;
  PyObject* subject;
  rx::Text* decoded;
  Cursor* cursor;
};

PyTypeObject* pattern_type = nullptr;
PyTypeObject* match_type = nullptr;
PyTypeObject* iterator_type = nullptr;
PyTypeObject* scanner_type = nullptr;
PyObject* pattern_error_type = nullptr;
PyObject* compilation_cache = nullptr;

[[nodiscard]] PyObject* translate_exception() noexcept {
  try {
    throw;
  } catch (const rx::PatternError& error) {
    PyObject* exception_type =
        pattern_error_type != nullptr ? pattern_error_type : PyExc_ValueError;
    Owned exception(PyObject_CallFunction(exception_type, "s", error.what()));
    if (!exception) {
      return nullptr;
    }
    Owned position(PyLong_FromSize_t(error.offset()));
    Owned line(PyLong_FromSize_t(error.line()));
    Owned column(PyLong_FromSize_t(error.column()));
    Owned message(PyUnicode_FromString(error.what()));
    if (!position || !line || !column || !message ||
        PyObject_SetAttrString(exception.get(), "pos", position.get()) < 0 ||
        PyObject_SetAttrString(exception.get(), "lineno", line.get()) < 0 ||
        PyObject_SetAttrString(exception.get(), "colno", column.get()) < 0 ||
        PyObject_SetAttrString(exception.get(), "msg", message.get()) < 0) {
      return nullptr;
    }
    PyErr_SetObject(exception_type, exception.get());
    return nullptr;
  } catch (const rx::ResourceError& error) {
    PyErr_SetString(PyExc_RecursionError, error.what());
    return nullptr;
  } catch (const std::bad_alloc&) {
    return PyErr_NoMemory();
  } catch (const std::exception& error) {
    PyErr_SetString(PyExc_RuntimeError, error.what());
    return nullptr;
  } catch (...) {
    PyErr_SetString(PyExc_RuntimeError,
                    "unknown error in the independent C++ regex engine");
    return nullptr;
  }
}

[[nodiscard]] bool decode_value(PyObject* object,
                                std::optional<rx::Encoding> expected,
                                rx::Text& result,
                                rx::Encoding& observed) {
  result.clear();
  if (PyUnicode_Check(object)) {
    observed = rx::Encoding::unicode;
    if (expected.has_value() && *expected != observed) {
      PyErr_SetString(PyExc_TypeError,
                      "cannot use a bytes pattern on a string-like object");
      return false;
    }
    const Py_ssize_t length = PyUnicode_GET_LENGTH(object);
    result.reserve(static_cast<std::size_t>(length));
    for (Py_ssize_t index = 0; index < length; ++index) {
      result.push_back(static_cast<rx::Rune>(PyUnicode_READ_CHAR(object, index)));
    }
    return true;
  }

  if (expected.has_value() && *expected != rx::Encoding::bytes) {
    PyErr_SetString(PyExc_TypeError,
                    "cannot use a string pattern on a bytes-like object");
    return false;
  }

  Py_buffer view{};
  if (PyObject_GetBuffer(object, &view, PyBUF_SIMPLE) < 0) {
    if (PyErr_ExceptionMatches(PyExc_TypeError)) {
      PyErr_SetString(PyExc_TypeError,
                      "expected a string or contiguous bytes-like object");
    }
    return false;
  }
  if (PyBuffer_IsContiguous(&view, 'C') == 0) {
    PyBuffer_Release(&view);
    PyErr_SetString(PyExc_BufferError,
                    "the bytes-like object must be contiguous");
    return false;
  }
  observed = rx::Encoding::bytes;
  const auto* bytes = static_cast<const unsigned char*>(view.buf);
  try {
    result.reserve(static_cast<std::size_t>(view.len));
    for (Py_ssize_t index = 0; index < view.len; ++index) {
      result.push_back(static_cast<rx::Rune>(bytes[index]));
    }
  } catch (...) {
    PyBuffer_Release(&view);
    throw;
  }
  PyBuffer_Release(&view);
  return true;
}

[[nodiscard]] PyObject* encode_value(rx::TextView value,
                                     rx::Encoding encoding) {
  if (value.size() > static_cast<std::size_t>(PY_SSIZE_T_MAX)) {
    PyErr_SetString(PyExc_OverflowError, "regular-expression result is too large");
    return nullptr;
  }
  if (encoding == rx::Encoding::unicode) {
    static_assert(sizeof(rx::Rune) == sizeof(Py_UCS4));
    return PyUnicode_FromKindAndData(
        PyUnicode_4BYTE_KIND, value.data(),
        static_cast<Py_ssize_t>(value.size()));
  }
  std::string bytes;
  bytes.reserve(value.size());
  for (rx::Rune character : value) {
    if (character > 0xff) {
      PyErr_SetString(PyExc_ValueError,
                      "a bytes regular-expression result escaped 0..255");
      return nullptr;
    }
    bytes.push_back(static_cast<char>(character));
  }
  return PyBytes_FromStringAndSize(bytes.data(),
                                   static_cast<Py_ssize_t>(bytes.size()));
}

[[nodiscard]] rx::CharacterProperties python_character_properties() {
  rx::CharacterProperties properties;
  properties.unicode_decimal = [](rx::Rune rune) {
    return Py_UNICODE_ISDECIMAL(static_cast<Py_UCS4>(rune)) != 0;
  };
  properties.unicode_space = [](rx::Rune rune) {
    return Py_UNICODE_ISSPACE(static_cast<Py_UCS4>(rune)) != 0;
  };
  properties.unicode_alphanumeric = [](rx::Rune rune) {
    return Py_UNICODE_ISALNUM(static_cast<Py_UCS4>(rune)) != 0;
  };
  properties.unicode_lower = [](rx::Rune rune) {
    return static_cast<rx::Rune>(
        Py_UNICODE_TOLOWER(static_cast<Py_UCS4>(rune)));
  };
  properties.unicode_upper = [](rx::Rune rune) {
    return static_cast<rx::Rune>(
        Py_UNICODE_TOUPPER(static_cast<Py_UCS4>(rune)));
  };
  properties.unicode_name = [](std::string_view name)
      -> std::optional<rx::Rune> {
    std::string escaped("\\N{");
    escaped.append(name);
    escaped.push_back('}');
    Owned decoded(PyUnicode_DecodeUnicodeEscape(
        escaped.data(), static_cast<Py_ssize_t>(escaped.size()), "strict"));
    if (!decoded) {
      PyErr_Clear();
      return std::nullopt;
    }
    if (PyUnicode_GET_LENGTH(decoded.get()) != 1) {
      return std::nullopt;
    }
    return static_cast<rx::Rune>(PyUnicode_READ_CHAR(decoded.get(), 0));
  };
  return properties;
}

[[nodiscard]] bool parse_flags(PyObject* object, std::uint32_t& flags) {
  if (object == nullptr || object == Py_None) {
    flags = 0;
    return true;
  }
  Owned indexed(PyNumber_Index(object));
  if (!indexed) {
    return false;
  }
  const unsigned long value = PyLong_AsUnsignedLong(indexed.get());
  if (value == static_cast<unsigned long>(-1) && PyErr_Occurred()) {
    return false;
  }
  if (value > std::numeric_limits<std::uint32_t>::max()) {
    PyErr_SetString(PyExc_OverflowError, "regular-expression flags are too large");
    return false;
  }
  flags = static_cast<std::uint32_t>(value);
  return true;
}

[[nodiscard]] bool clamp_index(PyObject* object, std::size_t length,
                               std::size_t default_value,
                               std::size_t& result) {
  if (object == nullptr || object == Py_None) {
    result = default_value;
    return true;
  }
  Owned indexed(PyNumber_Index(object));
  if (!indexed) {
    return false;
  }
  const Py_ssize_t value = PyLong_AsSsize_t(indexed.get());
  if (value == -1 && PyErr_Occurred()) {
    if (!PyErr_ExceptionMatches(PyExc_OverflowError)) {
      return false;
    }
    PyErr_Clear();
    Owned zero(PyLong_FromLong(0));
    if (!zero) {
      return false;
    }
    const int negative =
        PyObject_RichCompareBool(indexed.get(), zero.get(), Py_LT);
    if (negative < 0) {
      return false;
    }
    result = negative ? 0 : length;
    return true;
  }
  result = value < 0
               ? 0
               : std::min(static_cast<std::size_t>(value), length);
  return true;
}

[[nodiscard]] PyObject* build_groupindex(const rx::Program& program) {
  Owned result(PyDict_New());
  if (!result) {
    return nullptr;
  }
  for (const auto& [name, number] : program.group_names()) {
    Owned value(PyLong_FromSize_t(number));
    if (!value ||
        PyDict_SetItemString(result.get(), name.c_str(), value.get()) < 0) {
      return nullptr;
    }
  }
  return result.release();
}

[[nodiscard]] PyObject* make_pattern(rx::Program program,
                                     PyObject* original) {
  if (pattern_type == nullptr) {
    PyErr_SetString(PyExc_RuntimeError, "the pattern type is not initialized");
    return nullptr;
  }
  auto* result = reinterpret_cast<PatternObject*>(
      pattern_type->tp_alloc(pattern_type, 0));
  if (result == nullptr) {
    return nullptr;
  }
  result->program = nullptr;
  result->original = nullptr;
  try {
    result->program = new rx::Program(std::move(program));
  } catch (...) {
    Py_DECREF(reinterpret_cast<PyObject*>(result));
    return translate_exception();
  }
  Py_INCREF(original);
  result->original = original;
  return reinterpret_cast<PyObject*>(result);
}

[[nodiscard]] PyObject* compile_uncached(PyObject* pattern,
                                         std::uint32_t flags) {
  if (pattern_type != nullptr &&
      PyObject_TypeCheck(pattern, pattern_type) != 0) {
    if (flags != 0) {
      PyErr_SetString(PyExc_ValueError,
                      "cannot process flags argument with a compiled pattern");
      return nullptr;
    }
    return Py_NewRef(pattern);
  }
  if (!PyUnicode_Check(pattern) && !PyBytes_Check(pattern)) {
    PyErr_SetString(PyExc_TypeError,
                    "first argument must be string or compiled pattern");
    return nullptr;
  }
  rx::Text decoded;
  rx::Encoding encoding = rx::Encoding::unicode;
  try {
    if (!decode_value(pattern, std::nullopt, decoded, encoding)) {
      return nullptr;
    }
    rx::Compiler compiler(python_character_properties());
    return make_pattern(compiler.compile(decoded, encoding, flags), pattern);
  } catch (...) {
    return translate_exception();
  }
}

[[nodiscard]] PyObject* compile_cached(PyObject* pattern,
                                       std::uint32_t flags) {
  if (pattern_type != nullptr &&
      PyObject_TypeCheck(pattern, pattern_type) != 0) {
    return compile_uncached(pattern, flags);
  }
  if (compilation_cache == nullptr) {
    return compile_uncached(pattern, flags);
  }
  Owned flag_object(PyLong_FromUnsignedLong(flags));
  if (!flag_object) {
    return nullptr;
  }
  Owned key(PyTuple_Pack(3, reinterpret_cast<PyObject*>(Py_TYPE(pattern)),
                         pattern, flag_object.get()));
  if (!key) {
    return nullptr;
  }
  PyObject* cached = PyDict_GetItemWithError(compilation_cache, key.get());
  if (cached != nullptr) {
    return Py_NewRef(cached);
  }
  if (PyErr_Occurred()) {
    return nullptr;
  }
  Owned compiled(compile_uncached(pattern, flags));
  if (!compiled) {
    return nullptr;
  }
  if (PyDict_Size(compilation_cache) >= 512) {
    Owned iterator(PyObject_GetIter(compilation_cache));
    if (!iterator) {
      return nullptr;
    }
    Owned oldest(PyIter_Next(iterator.get()));
    if (!oldest) {
      if (!PyErr_Occurred()) {
        PyErr_SetString(PyExc_RuntimeError,
                        "regular-expression cache unexpectedly became empty");
      }
      return nullptr;
    }
    if (PyDict_DelItem(compilation_cache, oldest.get()) < 0) {
      return nullptr;
    }
  }
  if (PyDict_SetItem(compilation_cache, key.get(), compiled.get()) < 0) {
    return nullptr;
  }
  return compiled.release();
}

[[nodiscard]] PyObject* make_match(PatternObject* pattern, PyObject* subject,
                                   rx::Result result,
                                   std::size_t position,
                                   std::size_t end_position) {
  if (position > static_cast<std::size_t>(PY_SSIZE_T_MAX) ||
      end_position > static_cast<std::size_t>(PY_SSIZE_T_MAX)) {
    PyErr_SetString(PyExc_OverflowError, "regular-expression index is too large");
    return nullptr;
  }
  auto* match = reinterpret_cast<MatchObject*>(
      match_type->tp_alloc(match_type, 0));
  if (match == nullptr) {
    return nullptr;
  }
  match->pattern = nullptr;
  match->subject = nullptr;
  match->result = nullptr;
  try {
    match->result = new rx::Result(std::move(result));
  } catch (...) {
    Py_DECREF(reinterpret_cast<PyObject*>(match));
    return translate_exception();
  }
  match->pattern = reinterpret_cast<PatternObject*>(
      Py_NewRef(reinterpret_cast<PyObject*>(pattern)));
  match->subject = Py_NewRef(subject);
  match->position = static_cast<Py_ssize_t>(position);
  match->end_position = static_cast<Py_ssize_t>(end_position);
  return reinterpret_cast<PyObject*>(match);
}

[[nodiscard]] bool resolve_group(MatchObject* self, PyObject* group,
                                 std::size_t& result) {
  if (group == nullptr) {
    result = 0;
    return true;
  }
  if (PyUnicode_Check(group)) {
    Py_ssize_t length = 0;
    const char* name = PyUnicode_AsUTF8AndSize(group, &length);
    if (name == nullptr) {
      return false;
    }
    const auto found = self->pattern->program->group_names().find(
        std::string(name, static_cast<std::size_t>(length)));
    if (found == self->pattern->program->group_names().end()) {
      PyErr_SetString(PyExc_IndexError, "no such group");
      return false;
    }
    result = found->second;
    return true;
  }
  Owned index(PyNumber_Index(group));
  if (!index) {
    PyErr_Clear();
    PyErr_SetString(PyExc_IndexError, "no such group");
    return false;
  }
  const Py_ssize_t number = PyLong_AsSsize_t(index.get());
  if ((number == -1 && PyErr_Occurred()) || number < 0 ||
      static_cast<std::size_t>(number) >= self->result->groups.size()) {
    PyErr_Clear();
    PyErr_SetString(PyExc_IndexError, "no such group");
    return false;
  }
  result = static_cast<std::size_t>(number);
  return true;
}

[[nodiscard]] PyObject* matched_group(MatchObject* self,
                                      std::size_t group,
                                      PyObject* unmatched = Py_None) {
  const rx::Span& span = self->result->groups[group];
  if (!span.matched()) {
    return Py_NewRef(unmatched);
  }
  if (self->pattern->program->encoding() == rx::Encoding::unicode) {
    return PyUnicode_Substring(self->subject,
                               static_cast<Py_ssize_t>(span.begin),
                               static_cast<Py_ssize_t>(span.end));
  }
  rx::Text decoded;
  rx::Encoding observed = rx::Encoding::bytes;
  if (!decode_value(self->subject, rx::Encoding::bytes, decoded, observed)) {
    return nullptr;
  }
  return encode_value(
      rx::TextView(decoded).substr(span.begin, span.end - span.begin),
      rx::Encoding::bytes);
}

[[nodiscard]] std::optional<rx::Result> cursor_next(
    const rx::Program& program, rx::TextView subject, Cursor& cursor,
    rx::MatchMode mode = rx::MatchMode::search) {
  if (cursor.exhausted) {
    return std::nullopt;
  }
  rx::Machine machine;
  std::optional<rx::Result> result;
  if (cursor.retry_nonempty) {
    result = machine.run(program, subject, cursor.position,
                         cursor.end_position, rx::MatchMode::match, true);
    if (!result) {
      if (cursor.position == cursor.end_position) {
        cursor.exhausted = true;
        return std::nullopt;
      }
      ++cursor.position;
    }
    cursor.retry_nonempty = false;
  }
  if (!result) {
    result = machine.run(program, subject, cursor.position,
                         cursor.end_position, mode);
  }
  if (!result) {
    cursor.exhausted = true;
    return std::nullopt;
  }
  cursor.position = result->whole().end;
  cursor.retry_nonempty = result->whole().begin == result->whole().end;
  return result;
}

void pattern_dealloc(PyObject* object) noexcept {
  auto* self = reinterpret_cast<PatternObject*>(object);
  delete self->program;
  Py_XDECREF(self->original);
  Py_TYPE(object)->tp_free(object);
}

void match_dealloc(PyObject* object) noexcept {
  auto* self = reinterpret_cast<MatchObject*>(object);
  delete self->result;
  Py_XDECREF(reinterpret_cast<PyObject*>(self->pattern));
  Py_XDECREF(self->subject);
  Py_TYPE(object)->tp_free(object);
}

void iterator_dealloc(PyObject* object) noexcept {
  auto* self = reinterpret_cast<IteratorObject*>(object);
  delete self->decoded;
  delete self->cursor;
  Py_XDECREF(reinterpret_cast<PyObject*>(self->pattern));
  Py_XDECREF(self->subject);
  Py_TYPE(object)->tp_free(object);
}

void scanner_dealloc(PyObject* object) noexcept {
  auto* self = reinterpret_cast<ScannerObject*>(object);
  delete self->decoded;
  delete self->cursor;
  Py_XDECREF(reinterpret_cast<PyObject*>(self->pattern));
  Py_XDECREF(self->subject);
  Py_TYPE(object)->tp_free(object);
}

[[nodiscard]] PyObject* pattern_execute(PatternObject* self, PyObject* args,
                                        PyObject* keywords,
                                        rx::MatchMode mode,
                                        const char* method_name) {
  static const char* names[] = {"string", "pos", "endpos", nullptr};
  PyObject* subject = nullptr;
  PyObject* start_object = nullptr;
  PyObject* end_object = nullptr;
  if (!PyArg_ParseTupleAndKeywords(
          args, keywords, "O|OO", const_cast<char**>(names), &subject,
          &start_object, &end_object)) {
    return nullptr;
  }
  try {
    rx::Text decoded;
    rx::Encoding observed = self->program->encoding();
    if (!decode_value(subject, self->program->encoding(), decoded, observed)) {
      return nullptr;
    }
    std::size_t position = 0;
    std::size_t end_position = decoded.size();
    if (!clamp_index(start_object, decoded.size(), 0, position) ||
        !clamp_index(end_object, decoded.size(), decoded.size(),
                     end_position)) {
      return nullptr;
    }
    rx::Machine machine;
    std::optional<rx::Result> result =
        machine.run(*self->program, decoded, position, end_position, mode);
    if (!result) {
      Py_RETURN_NONE;
    }
    return make_match(self, subject, std::move(*result), position,
                      end_position);
  } catch (...) {
    static_cast<void>(method_name);
    return translate_exception();
  }
}

PyObject* pattern_search(PyObject* object, PyObject* args,
                         PyObject* keywords) {
  return pattern_execute(reinterpret_cast<PatternObject*>(object), args,
                         keywords, rx::MatchMode::search, "search");
}

PyObject* pattern_match(PyObject* object, PyObject* args,
                        PyObject* keywords) {
  return pattern_execute(reinterpret_cast<PatternObject*>(object), args,
                         keywords, rx::MatchMode::match, "match");
}

PyObject* pattern_fullmatch(PyObject* object, PyObject* args,
                            PyObject* keywords) {
  return pattern_execute(reinterpret_cast<PatternObject*>(object), args,
                         keywords, rx::MatchMode::fullmatch, "fullmatch");
}

template <class CursorObject>
[[nodiscard]] PyObject* create_cursor_object(PyTypeObject* type,
                                             PatternObject* pattern,
                                             PyObject* subject,
                                             std::size_t position,
                                             std::size_t end_position,
                                             rx::Text decoded) {
  auto* base = reinterpret_cast<CursorObject*>(type->tp_alloc(type, 0));
  if (base == nullptr) {
    return nullptr;
  }
  base->pattern = nullptr;
  base->subject = nullptr;
  base->decoded = nullptr;
  base->cursor = nullptr;
  try {
    base->decoded = new rx::Text(std::move(decoded));
    base->cursor = new Cursor{position, end_position, false,
                              position > end_position};
  } catch (...) {
    Py_DECREF(reinterpret_cast<PyObject*>(base));
    return translate_exception();
  }
  base->pattern = reinterpret_cast<PatternObject*>(
      Py_NewRef(reinterpret_cast<PyObject*>(pattern)));
  base->subject = Py_NewRef(subject);
  return reinterpret_cast<PyObject*>(base);
}

[[nodiscard]] PyObject* pattern_make_cursor(PatternObject* self,
                                            PyObject* args,
                                            PyObject* keywords,
                                            PyTypeObject* type) {
  static const char* names[] = {"string", "pos", "endpos", nullptr};
  PyObject* subject = nullptr;
  PyObject* start_object = nullptr;
  PyObject* end_object = nullptr;
  if (!PyArg_ParseTupleAndKeywords(args, keywords, "O|OO",
                                  const_cast<char**>(names), &subject,
                                  &start_object, &end_object)) {
    return nullptr;
  }
  try {
    rx::Text decoded;
    rx::Encoding observed = self->program->encoding();
    if (!decode_value(subject, self->program->encoding(), decoded, observed)) {
      return nullptr;
    }
    std::size_t position = 0;
    std::size_t end_position = decoded.size();
    if (!clamp_index(start_object, decoded.size(), 0, position) ||
        !clamp_index(end_object, decoded.size(), decoded.size(),
                     end_position)) {
      return nullptr;
    }
    if (type == iterator_type) {
      return create_cursor_object<IteratorObject>(
          type, self, subject, position, end_position, std::move(decoded));
    }
    if (type == scanner_type) {
      return create_cursor_object<ScannerObject>(
          type, self, subject, position, end_position, std::move(decoded));
    }
    PyErr_SetString(PyExc_RuntimeError,
                    "unknown independent regular-expression cursor type");
    return nullptr;
  } catch (...) {
    return translate_exception();
  }
}

PyObject* pattern_finditer(PyObject* object, PyObject* args,
                           PyObject* keywords) {
  return pattern_make_cursor(reinterpret_cast<PatternObject*>(object), args,
                             keywords, iterator_type);
}

PyObject* pattern_scanner(PyObject* object, PyObject* args,
                          PyObject* keywords) {
  return pattern_make_cursor(reinterpret_cast<PatternObject*>(object), args,
                             keywords, scanner_type);
}

PyObject* iterator_next(PyObject* object) {
  auto* self = reinterpret_cast<IteratorObject*>(object);
  try {
    const std::size_t original_position = self->cursor->position;
    std::optional<rx::Result> next = cursor_next(
        *self->pattern->program, *self->decoded, *self->cursor);
    if (!next) {
      return nullptr;
    }
    return make_match(self->pattern, self->subject, std::move(*next),
                      original_position, self->cursor->end_position);
  } catch (...) {
    return translate_exception();
  }
}

PyObject* scanner_take(PyObject* object, rx::MatchMode mode) {
  auto* self = reinterpret_cast<ScannerObject*>(object);
  try {
    const std::size_t original_position = self->cursor->position;
    std::optional<rx::Result> next = cursor_next(
        *self->pattern->program, *self->decoded, *self->cursor, mode);
    if (!next) {
      Py_RETURN_NONE;
    }
    return make_match(self->pattern, self->subject, std::move(*next),
                      original_position, self->cursor->end_position);
  } catch (...) {
    return translate_exception();
  }
}

PyObject* scanner_search(PyObject* object, PyObject*) {
  return scanner_take(object, rx::MatchMode::search);
}

PyObject* scanner_match(PyObject* object, PyObject*) {
  return scanner_take(object, rx::MatchMode::match);
}

[[nodiscard]] PyObject* findall_item(PatternObject* pattern,
                                     PyObject* subject,
                                     const rx::Result& result,
                                     const rx::Text& decoded) {
  const std::size_t groups = pattern->program->group_count();
  auto value_for = [&](std::size_t number) -> PyObject* {
    const rx::Span& span = result.groups[number];
    if (!span.matched()) {
      return encode_value({}, pattern->program->encoding());
    }
    if (pattern->program->encoding() == rx::Encoding::unicode) {
      return PyUnicode_Substring(subject, static_cast<Py_ssize_t>(span.begin),
                                 static_cast<Py_ssize_t>(span.end));
    }
    return encode_value(
        rx::TextView(decoded).substr(span.begin, span.end - span.begin),
        rx::Encoding::bytes);
  };
  if (groups == 0) {
    return value_for(0);
  }
  if (groups == 1) {
    return value_for(1);
  }
  Owned tuple(PyTuple_New(static_cast<Py_ssize_t>(groups)));
  if (!tuple) {
    return nullptr;
  }
  for (std::size_t group = 1; group <= groups; ++group) {
    PyObject* value = value_for(group);
    if (value == nullptr) {
      return nullptr;
    }
    PyTuple_SET_ITEM(tuple.get(), static_cast<Py_ssize_t>(group - 1), value);
  }
  return tuple.release();
}

PyObject* pattern_findall(PyObject* object, PyObject* args,
                          PyObject* keywords) {
  auto* self = reinterpret_cast<PatternObject*>(object);
  static const char* names[] = {"string", "pos", "endpos", nullptr};
  PyObject* subject = nullptr;
  PyObject* start_object = nullptr;
  PyObject* end_object = nullptr;
  if (!PyArg_ParseTupleAndKeywords(args, keywords, "O|OO",
                                  const_cast<char**>(names), &subject,
                                  &start_object, &end_object)) {
    return nullptr;
  }
  try {
    rx::Text decoded;
    rx::Encoding observed = self->program->encoding();
    if (!decode_value(subject, self->program->encoding(), decoded, observed)) {
      return nullptr;
    }
    std::size_t position = 0;
    std::size_t end_position = decoded.size();
    if (!clamp_index(start_object, decoded.size(), 0, position) ||
        !clamp_index(end_object, decoded.size(), decoded.size(),
                     end_position)) {
      return nullptr;
    }
    Cursor cursor{position, end_position, false, position > end_position};
    Owned result(PyList_New(0));
    if (!result) {
      return nullptr;
    }
    while (std::optional<rx::Result> match =
               cursor_next(*self->program, decoded, cursor)) {
      Owned item(findall_item(self, subject, *match, decoded));
      if (!item || PyList_Append(result.get(), item.get()) < 0) {
        return nullptr;
      }
    }
    return result.release();
  } catch (...) {
    return translate_exception();
  }
}

[[nodiscard]] bool parse_count(PyObject* object, std::size_t& result) {
  if (object == nullptr || object == Py_None) {
    result = 0;
    return true;
  }
  Owned indexed(PyNumber_Index(object));
  if (!indexed) {
    return false;
  }
  const Py_ssize_t count = PyLong_AsSsize_t(indexed.get());
  if (count == -1 && PyErr_Occurred()) {
    return false;
  }
  result = count < 0 ? 0 : static_cast<std::size_t>(count);
  return true;
}

[[nodiscard]] PyObject* slice_decoded(PatternObject* pattern,
                                      PyObject* subject,
                                      const rx::Text& decoded,
                                      std::size_t begin,
                                      std::size_t end) {
  if (pattern->program->encoding() == rx::Encoding::unicode) {
    return PyUnicode_Substring(subject, static_cast<Py_ssize_t>(begin),
                               static_cast<Py_ssize_t>(end));
  }
  return encode_value(rx::TextView(decoded).substr(begin, end - begin),
                      rx::Encoding::bytes);
}

PyObject* pattern_split(PyObject* object, PyObject* args,
                        PyObject* keywords) {
  auto* self = reinterpret_cast<PatternObject*>(object);
  static const char* names[] = {"string", "maxsplit", nullptr};
  PyObject* subject = nullptr;
  PyObject* count_object = nullptr;
  if (!PyArg_ParseTupleAndKeywords(args, keywords, "O|O",
                                  const_cast<char**>(names), &subject,
                                  &count_object)) {
    return nullptr;
  }
  try {
    rx::Text decoded;
    rx::Encoding observed = self->program->encoding();
    std::size_t maximum = 0;
    if (!decode_value(subject, self->program->encoding(), decoded, observed) ||
        !parse_count(count_object, maximum)) {
      return nullptr;
    }
    Cursor cursor{0, decoded.size(), false, false};
    Owned result(PyList_New(0));
    if (!result) {
      return nullptr;
    }
    std::size_t previous = 0;
    std::size_t count = 0;
    while (maximum == 0 || count < maximum) {
      std::optional<rx::Result> match =
          cursor_next(*self->program, decoded, cursor);
      if (!match) {
        break;
      }
      Owned preceding(slice_decoded(self, subject, decoded, previous,
                                    match->whole().begin));
      if (!preceding || PyList_Append(result.get(), preceding.get()) < 0) {
        return nullptr;
      }
      for (std::size_t group = 1; group < match->groups.size(); ++group) {
        const rx::Span& capture = match->groups[group];
        Owned captured(capture.matched()
                           ? slice_decoded(self, subject, decoded,
                                           capture.begin, capture.end)
                           : Py_NewRef(Py_None));
        if (!captured || PyList_Append(result.get(), captured.get()) < 0) {
          return nullptr;
        }
      }
      previous = match->whole().end;
      ++count;
    }
    Owned tail(slice_decoded(self, subject, decoded, previous,
                             decoded.size()));
    if (!tail || PyList_Append(result.get(), tail.get()) < 0) {
      return nullptr;
    }
    return result.release();
  } catch (...) {
    return translate_exception();
  }
}

[[nodiscard]] PyObject* pattern_substitute(PatternObject* self,
                                           PyObject* args,
                                           PyObject* keywords,
                                           bool include_count) {
  static const char* names[] = {"repl", "string", "count", nullptr};
  PyObject* replacement = nullptr;
  PyObject* subject = nullptr;
  PyObject* count_object = nullptr;
  if (!PyArg_ParseTupleAndKeywords(args, keywords, "OO|O",
                                  const_cast<char**>(names), &replacement,
                                  &subject, &count_object)) {
    return nullptr;
  }
  try {
    rx::Text decoded;
    rx::Encoding observed = self->program->encoding();
    std::size_t maximum = 0;
    if (!decode_value(subject, self->program->encoding(), decoded, observed) ||
        !parse_count(count_object, maximum)) {
      return nullptr;
    }
    const bool callable = PyCallable_Check(replacement) != 0;
    std::vector<rx::TemplatePart> template_parts;
    if (!callable) {
      rx::Text replacement_text;
      rx::Encoding replacement_encoding = self->program->encoding();
      if (!decode_value(replacement, self->program->encoding(),
                        replacement_text, replacement_encoding)) {
        return nullptr;
      }
      template_parts = rx::parse_template(replacement_text, *self->program);
    }

    Cursor cursor{0, decoded.size(), false, false};
    rx::Text output;
    std::size_t previous = 0;
    std::size_t count = 0;
    while (maximum == 0 || count < maximum) {
      std::optional<rx::Result> match =
          cursor_next(*self->program, decoded, cursor);
      if (!match) {
        break;
      }
      output.append(rx::TextView(decoded).substr(
          previous, match->whole().begin - previous));
      if (callable) {
        Owned argument(make_match(self, subject, *match, 0, decoded.size()));
        if (!argument) {
          return nullptr;
        }
        Owned returned(PyObject_CallOneArg(replacement, argument.get()));
        if (!returned) {
          return nullptr;
        }
        rx::Text addition;
        rx::Encoding addition_encoding = self->program->encoding();
        if (!decode_value(returned.get(), self->program->encoding(),
                          addition, addition_encoding)) {
          return nullptr;
        }
        output += addition;
      } else {
        output += rx::expand_template(template_parts, *match, decoded);
      }
      previous = match->whole().end;
      ++count;
    }
    output.append(rx::TextView(decoded).substr(previous));
    Owned replaced(encode_value(output, self->program->encoding()));
    if (!replaced) {
      return nullptr;
    }
    if (!include_count) {
      return replaced.release();
    }
    Owned changes(PyLong_FromSize_t(count));
    if (!changes) {
      return nullptr;
    }
    return PyTuple_Pack(2, replaced.get(), changes.get());
  } catch (...) {
    return translate_exception();
  }
}

PyObject* pattern_sub(PyObject* object, PyObject* args,
                      PyObject* keywords) {
  return pattern_substitute(reinterpret_cast<PatternObject*>(object), args,
                            keywords, false);
}

PyObject* pattern_subn(PyObject* object, PyObject* args,
                       PyObject* keywords) {
  return pattern_substitute(reinterpret_cast<PatternObject*>(object), args,
                            keywords, true);
}

PyObject* pattern_copy(PyObject* object, PyObject*) {
  return Py_NewRef(object);
}

PyObject* pattern_deepcopy(PyObject* object, PyObject*) {
  return Py_NewRef(object);
}

PyObject* pattern_repr(PyObject* object) {
  auto* self = reinterpret_cast<PatternObject*>(object);
  return PyUnicode_FromFormat("rebar_cpp_from_scratch_v1.compile(%R, flags=%u)",
                              self->original, self->program->flags());
}

PyObject* pattern_get_pattern(PyObject* object, void*) {
  return Py_NewRef(reinterpret_cast<PatternObject*>(object)->original);
}

PyObject* pattern_get_flags(PyObject* object, void*) {
  return PyLong_FromUnsignedLong(
      reinterpret_cast<PatternObject*>(object)->program->flags());
}

PyObject* pattern_get_groups(PyObject* object, void*) {
  return PyLong_FromSize_t(
      reinterpret_cast<PatternObject*>(object)->program->group_count());
}

PyObject* pattern_get_groupindex(PyObject* object, void*) {
  return build_groupindex(
      *reinterpret_cast<PatternObject*>(object)->program);
}

PyObject* match_group(PyObject* object, PyObject* args) {
  auto* self = reinterpret_cast<MatchObject*>(object);
  const Py_ssize_t count = PyTuple_GET_SIZE(args);
  if (count == 0) {
    return matched_group(self, 0);
  }
  if (count == 1) {
    std::size_t group = 0;
    if (!resolve_group(self, PyTuple_GET_ITEM(args, 0), group)) {
      return nullptr;
    }
    return matched_group(self, group);
  }
  Owned result(PyTuple_New(count));
  if (!result) {
    return nullptr;
  }
  for (Py_ssize_t index = 0; index < count; ++index) {
    std::size_t group = 0;
    if (!resolve_group(self, PyTuple_GET_ITEM(args, index), group)) {
      return nullptr;
    }
    PyObject* value = matched_group(self, group);
    if (value == nullptr) {
      return nullptr;
    }
    PyTuple_SET_ITEM(result.get(), index, value);
  }
  return result.release();
}

PyObject* match_groups(PyObject* object, PyObject* args,
                       PyObject* keywords) {
  auto* self = reinterpret_cast<MatchObject*>(object);
  static const char* names[] = {"default", nullptr};
  PyObject* unmatched = Py_None;
  if (!PyArg_ParseTupleAndKeywords(args, keywords, "|O",
                                  const_cast<char**>(names), &unmatched)) {
    return nullptr;
  }
  const std::size_t count = self->pattern->program->group_count();
  Owned result(PyTuple_New(static_cast<Py_ssize_t>(count)));
  if (!result) {
    return nullptr;
  }
  for (std::size_t group = 1; group <= count; ++group) {
    PyObject* value = matched_group(self, group, unmatched);
    if (value == nullptr) {
      return nullptr;
    }
    PyTuple_SET_ITEM(result.get(), static_cast<Py_ssize_t>(group - 1), value);
  }
  return result.release();
}

PyObject* match_groupdict(PyObject* object, PyObject* args,
                          PyObject* keywords) {
  auto* self = reinterpret_cast<MatchObject*>(object);
  static const char* names[] = {"default", nullptr};
  PyObject* unmatched = Py_None;
  if (!PyArg_ParseTupleAndKeywords(args, keywords, "|O",
                                  const_cast<char**>(names), &unmatched)) {
    return nullptr;
  }
  Owned result(PyDict_New());
  if (!result) {
    return nullptr;
  }
  for (const auto& [name, group] : self->pattern->program->group_names()) {
    Owned value(matched_group(self, group, unmatched));
    if (!value ||
        PyDict_SetItemString(result.get(), name.c_str(), value.get()) < 0) {
      return nullptr;
    }
  }
  return result.release();
}

[[nodiscard]] PyObject* match_position(PyObject* object, PyObject* args,
                                       int part) {
  auto* self = reinterpret_cast<MatchObject*>(object);
  PyObject* group_object = nullptr;
  if (!PyArg_ParseTuple(args, "|O", &group_object)) {
    return nullptr;
  }
  std::size_t group = 0;
  if (!resolve_group(self, group_object, group)) {
    return nullptr;
  }
  const rx::Span& span = self->result->groups[group];
  if (part == 0) {
    return span.matched() ? PyLong_FromSize_t(span.begin)
                          : PyLong_FromLong(-1);
  }
  if (part == 1) {
    return span.matched() ? PyLong_FromSize_t(span.end)
                          : PyLong_FromLong(-1);
  }
  Owned begin(span.matched() ? PyLong_FromSize_t(span.begin)
                             : PyLong_FromLong(-1));
  Owned end(span.matched() ? PyLong_FromSize_t(span.end)
                           : PyLong_FromLong(-1));
  if (!begin || !end) {
    return nullptr;
  }
  return PyTuple_Pack(2, begin.get(), end.get());
}

PyObject* match_start(PyObject* object, PyObject* args) {
  return match_position(object, args, 0);
}

PyObject* match_end(PyObject* object, PyObject* args) {
  return match_position(object, args, 1);
}

PyObject* match_span(PyObject* object, PyObject* args) {
  return match_position(object, args, 2);
}

PyObject* match_subscript(PyObject* object, PyObject* key) {
  auto* self = reinterpret_cast<MatchObject*>(object);
  std::size_t group = 0;
  if (!resolve_group(self, key, group)) {
    return nullptr;
  }
  return matched_group(self, group);
}

PyObject* match_expand(PyObject* object, PyObject* replacement) {
  auto* self = reinterpret_cast<MatchObject*>(object);
  try {
    rx::Text decoded_replacement;
    rx::Encoding replacement_encoding = self->pattern->program->encoding();
    if (!decode_value(replacement, self->pattern->program->encoding(),
                      decoded_replacement, replacement_encoding)) {
      return nullptr;
    }
    rx::Text decoded_subject;
    rx::Encoding subject_encoding = self->pattern->program->encoding();
    if (!decode_value(self->subject, self->pattern->program->encoding(),
                      decoded_subject, subject_encoding)) {
      return nullptr;
    }
    const std::vector<rx::TemplatePart> parts = rx::parse_template(
        decoded_replacement, *self->pattern->program);
    return encode_value(rx::expand_template(parts, *self->result,
                                            decoded_subject),
                        self->pattern->program->encoding());
  } catch (...) {
    return translate_exception();
  }
}

PyObject* match_get_re(PyObject* object, void*) {
  return Py_NewRef(reinterpret_cast<PyObject*>(
      reinterpret_cast<MatchObject*>(object)->pattern));
}

PyObject* match_get_string(PyObject* object, void*) {
  return Py_NewRef(reinterpret_cast<MatchObject*>(object)->subject);
}

PyObject* match_get_pos(PyObject* object, void*) {
  return PyLong_FromSsize_t(
      reinterpret_cast<MatchObject*>(object)->position);
}

PyObject* match_get_endpos(PyObject* object, void*) {
  return PyLong_FromSsize_t(
      reinterpret_cast<MatchObject*>(object)->end_position);
}

PyObject* match_get_lastindex(PyObject* object, void*) {
  const std::size_t group =
      reinterpret_cast<MatchObject*>(object)->result->last_group;
  if (group == 0) {
    Py_RETURN_NONE;
  }
  return PyLong_FromSize_t(group);
}

PyObject* match_get_lastgroup(PyObject* object, void*) {
  auto* self = reinterpret_cast<MatchObject*>(object);
  const std::size_t group = self->result->last_group;
  if (group == 0) {
    Py_RETURN_NONE;
  }
  for (const auto& [name, number] : self->pattern->program->group_names()) {
    if (number == group) {
      return PyUnicode_FromStringAndSize(
          name.data(), static_cast<Py_ssize_t>(name.size()));
    }
  }
  Py_RETURN_NONE;
}

PyObject* match_get_regs(PyObject* object, void*) {
  auto* self = reinterpret_cast<MatchObject*>(object);
  Owned rows(PyTuple_New(static_cast<Py_ssize_t>(self->result->groups.size())));
  if (!rows) {
    return nullptr;
  }
  for (std::size_t index = 0; index < self->result->groups.size(); ++index) {
    const rx::Span& span = self->result->groups[index];
    Owned begin(span.matched() ? PyLong_FromSize_t(span.begin)
                               : PyLong_FromLong(-1));
    Owned end(span.matched() ? PyLong_FromSize_t(span.end)
                             : PyLong_FromLong(-1));
    if (!begin || !end) {
      return nullptr;
    }
    PyObject* pair = PyTuple_Pack(2, begin.get(), end.get());
    if (pair == nullptr) {
      return nullptr;
    }
    PyTuple_SET_ITEM(rows.get(), static_cast<Py_ssize_t>(index), pair);
  }
  return rows.release();
}

PyObject* match_repr(PyObject* object) {
  auto* self = reinterpret_cast<MatchObject*>(object);
  Owned group(matched_group(self, 0));
  if (!group) {
    return nullptr;
  }
  const rx::Span& span = self->result->whole();
  return PyUnicode_FromFormat(
      "<rebar_cpp_from_scratch_v1.Match object; span=(%zu, %zu), match=%R>",
      span.begin, span.end, group.get());
}

PyObject* module_compile(PyObject*, PyObject* args, PyObject* keywords) {
  static const char* names[] = {"pattern", "flags", nullptr};
  PyObject* pattern = nullptr;
  PyObject* flag_object = nullptr;
  if (!PyArg_ParseTupleAndKeywords(args, keywords, "O|O",
                                  const_cast<char**>(names), &pattern,
                                  &flag_object)) {
    return nullptr;
  }
  std::uint32_t flags = 0;
  if (!parse_flags(flag_object, flags)) {
    return nullptr;
  }
  try {
    return compile_cached(pattern, flags);
  } catch (...) {
    return translate_exception();
  }
}

[[nodiscard]] PyObject* module_match_like(PyObject* args,
                                          PyObject* keywords,
                                          const char* method) {
  static const char* names[] = {"pattern", "string", "flags", nullptr};
  PyObject* pattern = nullptr;
  PyObject* subject = nullptr;
  PyObject* flag_object = nullptr;
  if (!PyArg_ParseTupleAndKeywords(args, keywords, "OO|O",
                                  const_cast<char**>(names), &pattern,
                                  &subject, &flag_object)) {
    return nullptr;
  }
  std::uint32_t flags = 0;
  if (!parse_flags(flag_object, flags)) {
    return nullptr;
  }
  try {
    Owned compiled(compile_cached(pattern, flags));
    if (!compiled) {
      return nullptr;
    }
    return PyObject_CallMethod(compiled.get(), method, "O", subject);
  } catch (...) {
    return translate_exception();
  }
}

PyObject* module_search(PyObject*, PyObject* args, PyObject* keywords) {
  return module_match_like(args, keywords, "search");
}

PyObject* module_match(PyObject*, PyObject* args, PyObject* keywords) {
  return module_match_like(args, keywords, "match");
}

PyObject* module_fullmatch(PyObject*, PyObject* args, PyObject* keywords) {
  return module_match_like(args, keywords, "fullmatch");
}

PyObject* module_finditer(PyObject*, PyObject* args, PyObject* keywords) {
  return module_match_like(args, keywords, "finditer");
}

PyObject* module_findall(PyObject*, PyObject* args, PyObject* keywords) {
  return module_match_like(args, keywords, "findall");
}

PyObject* module_split(PyObject*, PyObject* args, PyObject* keywords) {
  static const char* names[] = {"pattern", "string", "maxsplit", "flags",
                                nullptr};
  PyObject* pattern = nullptr;
  PyObject* subject = nullptr;
  PyObject* count = nullptr;
  PyObject* flag_object = nullptr;
  if (!PyArg_ParseTupleAndKeywords(args, keywords, "OO|OO",
                                  const_cast<char**>(names), &pattern,
                                  &subject, &count, &flag_object)) {
    return nullptr;
  }
  std::uint32_t flags = 0;
  if (!parse_flags(flag_object, flags)) {
    return nullptr;
  }
  try {
    Owned compiled(compile_cached(pattern, flags));
    if (!compiled) {
      return nullptr;
    }
    if (count != nullptr) {
      return PyObject_CallMethod(compiled.get(), "split", "OO", subject,
                                 count);
    }
    return PyObject_CallMethod(compiled.get(), "split", "O", subject);
  } catch (...) {
    return translate_exception();
  }
}

[[nodiscard]] PyObject* module_substitute(PyObject* args,
                                          PyObject* keywords,
                                          const char* method) {
  static const char* names[] = {"pattern", "repl", "string", "count",
                                "flags", nullptr};
  PyObject* pattern = nullptr;
  PyObject* replacement = nullptr;
  PyObject* subject = nullptr;
  PyObject* count = nullptr;
  PyObject* flag_object = nullptr;
  if (!PyArg_ParseTupleAndKeywords(args, keywords, "OOO|OO",
                                  const_cast<char**>(names), &pattern,
                                  &replacement, &subject, &count,
                                  &flag_object)) {
    return nullptr;
  }
  std::uint32_t flags = 0;
  if (!parse_flags(flag_object, flags)) {
    return nullptr;
  }
  try {
    Owned compiled(compile_cached(pattern, flags));
    if (!compiled) {
      return nullptr;
    }
    if (count != nullptr) {
      return PyObject_CallMethod(compiled.get(), method, "OOO", replacement,
                                 subject, count);
    }
    return PyObject_CallMethod(compiled.get(), method, "OO", replacement,
                               subject);
  } catch (...) {
    return translate_exception();
  }
}

PyObject* module_sub(PyObject*, PyObject* args, PyObject* keywords) {
  return module_substitute(args, keywords, "sub");
}

PyObject* module_subn(PyObject*, PyObject* args, PyObject* keywords) {
  return module_substitute(args, keywords, "subn");
}

PyObject* module_escape(PyObject*, PyObject* argument) {
  try {
    rx::Text decoded;
    rx::Encoding encoding = rx::Encoding::unicode;
    if (!decode_value(argument, std::nullopt, decoded, encoding)) {
      return nullptr;
    }
    return encode_value(rx::escape_pattern(decoded), encoding);
  } catch (...) {
    return translate_exception();
  }
}

PyObject* module_purge(PyObject*, PyObject*) {
  if (compilation_cache != nullptr) {
    PyDict_Clear(compilation_cache);
  }
  Py_RETURN_NONE;
}

PyMethodDef pattern_methods[] = {
    {"search", reinterpret_cast<PyCFunction>(pattern_search),
     METH_VARARGS | METH_KEYWORDS, "Search with the independently owned engine."},
    {"match", reinterpret_cast<PyCFunction>(pattern_match),
     METH_VARARGS | METH_KEYWORDS, "Match at the supplied start position."},
    {"fullmatch", reinterpret_cast<PyCFunction>(pattern_fullmatch),
     METH_VARARGS | METH_KEYWORDS, "Match the complete supplied slice."},
    {"finditer", reinterpret_cast<PyCFunction>(pattern_finditer),
     METH_VARARGS | METH_KEYWORDS, "Return an independently owned iterator."},
    {"findall", reinterpret_cast<PyCFunction>(pattern_findall),
     METH_VARARGS | METH_KEYWORDS, "Collect independently produced matches."},
    {"split", reinterpret_cast<PyCFunction>(pattern_split),
     METH_VARARGS | METH_KEYWORDS, "Split with independently owned captures."},
    {"sub", reinterpret_cast<PyCFunction>(pattern_sub),
     METH_VARARGS | METH_KEYWORDS, "Perform an owned replacement."},
    {"subn", reinterpret_cast<PyCFunction>(pattern_subn),
     METH_VARARGS | METH_KEYWORDS, "Return replacement and change count."},
    {"scanner", reinterpret_cast<PyCFunction>(pattern_scanner),
     METH_VARARGS | METH_KEYWORDS, "Create an independently owned scanner."},
    {"__copy__", pattern_copy, METH_NOARGS, "Compiled patterns are immutable."},
    {"__deepcopy__", pattern_deepcopy, METH_O,
     "Compiled patterns are immutable."},
    {"__class_getitem__", reinterpret_cast<PyCFunction>(Py_GenericAlias),
     METH_O | METH_CLASS, "Create a standard Python generic alias."},
    {nullptr, nullptr, 0, nullptr},
};

PyGetSetDef pattern_properties[] = {
    {const_cast<char*>("pattern"), pattern_get_pattern, nullptr, nullptr,
     nullptr},
    {const_cast<char*>("flags"), pattern_get_flags, nullptr, nullptr, nullptr},
    {const_cast<char*>("groups"), pattern_get_groups, nullptr, nullptr,
     nullptr},
    {const_cast<char*>("groupindex"), pattern_get_groupindex, nullptr,
     nullptr, nullptr},
    {nullptr, nullptr, nullptr, nullptr, nullptr},
};

PyMethodDef match_methods[] = {
    {"group", match_group, METH_VARARGS, "Read one or more captured groups."},
    {"groups", reinterpret_cast<PyCFunction>(match_groups),
     METH_VARARGS | METH_KEYWORDS, "Read all numbered captured groups."},
    {"groupdict", reinterpret_cast<PyCFunction>(match_groupdict),
     METH_VARARGS | METH_KEYWORDS, "Read all named captured groups."},
    {"start", match_start, METH_VARARGS, "Return a group's starting offset."},
    {"end", match_end, METH_VARARGS, "Return a group's ending offset."},
    {"span", match_span, METH_VARARGS, "Return a group's half-open span."},
    {"expand", match_expand, METH_O, "Expand a native-owned replacement."},
    {"__class_getitem__", reinterpret_cast<PyCFunction>(Py_GenericAlias),
     METH_O | METH_CLASS, "Create a standard Python generic alias."},
    {nullptr, nullptr, 0, nullptr},
};

PyGetSetDef match_properties[] = {
    {const_cast<char*>("re"), match_get_re, nullptr, nullptr, nullptr},
    {const_cast<char*>("string"), match_get_string, nullptr, nullptr,
     nullptr},
    {const_cast<char*>("pos"), match_get_pos, nullptr, nullptr, nullptr},
    {const_cast<char*>("endpos"), match_get_endpos, nullptr, nullptr,
     nullptr},
    {const_cast<char*>("lastindex"), match_get_lastindex, nullptr, nullptr,
     nullptr},
    {const_cast<char*>("lastgroup"), match_get_lastgroup, nullptr, nullptr,
     nullptr},
    {const_cast<char*>("regs"), match_get_regs, nullptr, nullptr, nullptr},
    {nullptr, nullptr, nullptr, nullptr, nullptr},
};

PyMethodDef scanner_methods[] = {
    {"search", scanner_search, METH_NOARGS, "Find the next scanner match."},
    {"match", scanner_match, METH_NOARGS, "Match at the scanner position."},
    {nullptr, nullptr, 0, nullptr},
};

PyType_Slot pattern_slots[] = {
    {Py_tp_dealloc, reinterpret_cast<void*>(pattern_dealloc)},
    {Py_tp_methods, pattern_methods},
    {Py_tp_getset, pattern_properties},
    {Py_tp_repr, reinterpret_cast<void*>(pattern_repr)},
    {0, nullptr},
};

PyType_Slot match_slots[] = {
    {Py_tp_dealloc, reinterpret_cast<void*>(match_dealloc)},
    {Py_tp_methods, match_methods},
    {Py_tp_getset, match_properties},
    {Py_tp_repr, reinterpret_cast<void*>(match_repr)},
    {Py_mp_subscript, reinterpret_cast<void*>(match_subscript)},
    {0, nullptr},
};

PyType_Slot iterator_slots[] = {
    {Py_tp_dealloc, reinterpret_cast<void*>(iterator_dealloc)},
    {Py_tp_iter, reinterpret_cast<void*>(PyObject_SelfIter)},
    {Py_tp_iternext, reinterpret_cast<void*>(iterator_next)},
    {0, nullptr},
};

PyType_Slot scanner_slots[] = {
    {Py_tp_dealloc, reinterpret_cast<void*>(scanner_dealloc)},
    {Py_tp_methods, scanner_methods},
    {0, nullptr},
};

PyType_Spec pattern_spec = {
    "rebar_cpp_from_scratch_v1.Pattern",
    static_cast<int>(sizeof(PatternObject)),
    0,
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IMMUTABLETYPE,
    pattern_slots,
};

PyType_Spec match_spec = {
    "rebar_cpp_from_scratch_v1.Match",
    static_cast<int>(sizeof(MatchObject)),
    0,
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IMMUTABLETYPE,
    match_slots,
};

PyType_Spec iterator_spec = {
    "rebar_cpp_from_scratch_v1.MatchIterator",
    static_cast<int>(sizeof(IteratorObject)),
    0,
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IMMUTABLETYPE,
    iterator_slots,
};

PyType_Spec scanner_spec = {
    "rebar_cpp_from_scratch_v1.PatternScanner",
    static_cast<int>(sizeof(ScannerObject)),
    0,
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IMMUTABLETYPE,
    scanner_slots,
};

PyMethodDef module_methods[] = {
    {"compile", reinterpret_cast<PyCFunction>(module_compile),
     METH_VARARGS | METH_KEYWORDS, "Compile using the independent C++ parser."},
    {"search", reinterpret_cast<PyCFunction>(module_search),
     METH_VARARGS | METH_KEYWORDS, "Search using the independent C++ machine."},
    {"match", reinterpret_cast<PyCFunction>(module_match),
     METH_VARARGS | METH_KEYWORDS, "Match using the independent C++ machine."},
    {"fullmatch", reinterpret_cast<PyCFunction>(module_fullmatch),
     METH_VARARGS | METH_KEYWORDS, "Run an independent complete match."},
    {"finditer", reinterpret_cast<PyCFunction>(module_finditer),
     METH_VARARGS | METH_KEYWORDS, "Create an independently owned iterator."},
    {"findall", reinterpret_cast<PyCFunction>(module_findall),
     METH_VARARGS | METH_KEYWORDS, "Collect independently produced matches."},
    {"split", reinterpret_cast<PyCFunction>(module_split),
     METH_VARARGS | METH_KEYWORDS, "Split using independently owned captures."},
    {"sub", reinterpret_cast<PyCFunction>(module_sub),
     METH_VARARGS | METH_KEYWORDS, "Substitute with the independent engine."},
    {"subn", reinterpret_cast<PyCFunction>(module_subn),
     METH_VARARGS | METH_KEYWORDS, "Return independent substitution counts."},
    {"escape", module_escape, METH_O, "Escape regular-expression punctuation."},
    {"purge", module_purge, METH_NOARGS, "Empty the owned compilation cache."},
    {nullptr, nullptr, 0, nullptr},
};

PyModuleDef module_definition = {
    PyModuleDef_HEAD_INIT,
    "rebar_cpp_from_scratch_v1",
    "An unqualified, source-first, independently implemented C++ regex experiment.",
    -1,
    module_methods,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};

[[nodiscard]] int expose_type(PyObject* module, const char* name,
                              PyType_Spec& spec,
                              PyTypeObject*& destination) {
  Owned type(PyType_FromSpec(&spec));
  if (!type) {
    return -1;
  }
  destination = reinterpret_cast<PyTypeObject*>(type.get());
  if (PyModule_AddObjectRef(module, name, type.get()) < 0) {
    destination = nullptr;
    return -1;
  }
  type.release();
  return 0;
}

}  // namespace

extern "C" PyMODINIT_FUNC PyInit_rebar_cpp_from_scratch_v1() {
  try {
    Owned module(PyModule_Create(&module_definition));
    if (!module) {
      return nullptr;
    }
    if (expose_type(module.get(), "Pattern", pattern_spec, pattern_type) < 0 ||
        expose_type(module.get(), "Match", match_spec, match_type) < 0 ||
        expose_type(module.get(), "MatchIterator", iterator_spec,
                    iterator_type) < 0 ||
        expose_type(module.get(), "PatternScanner", scanner_spec,
                    scanner_type) < 0) {
      return nullptr;
    }

    Owned error(PyErr_NewException(
        "rebar_cpp_from_scratch_v1.PatternError", PyExc_ValueError, nullptr));
    if (!error ||
        PyModule_AddObjectRef(module.get(), "PatternError", error.get()) < 0 ||
        PyModule_AddObjectRef(module.get(), "error", error.get()) < 0) {
      return nullptr;
    }
    pattern_error_type = error.release();

    Owned cache(PyDict_New());
    if (!cache) {
      return nullptr;
    }
    compilation_cache = cache.release();

    const std::pair<const char*, std::uint32_t> flags[] = {
        {"NOFLAG", 0},
        {"T", rx::flag_template},
        {"TEMPLATE", rx::flag_template},
        {"I", rx::flag_ignore_case},
        {"IGNORECASE", rx::flag_ignore_case},
        {"L", rx::flag_locale},
        {"LOCALE", rx::flag_locale},
        {"M", rx::flag_multiline},
        {"MULTILINE", rx::flag_multiline},
        {"S", rx::flag_dotall},
        {"DOTALL", rx::flag_dotall},
        {"U", rx::flag_unicode},
        {"UNICODE", rx::flag_unicode},
        {"X", rx::flag_verbose},
        {"VERBOSE", rx::flag_verbose},
        {"DEBUG", rx::flag_debug},
        {"A", rx::flag_ascii},
        {"ASCII", rx::flag_ascii},
    };
    for (const auto& [name, value] : flags) {
      if (PyModule_AddIntConstant(module.get(), name,
                                  static_cast<long>(value)) < 0) {
        return nullptr;
      }
    }

    constexpr const char* exported_names[] = {
        "match", "fullmatch", "search", "sub", "subn", "split",
        "findall", "finditer", "compile", "purge", "escape", "error",
        "Pattern", "Match", "A", "ASCII", "I", "IGNORECASE", "L",
        "LOCALE", "M", "MULTILINE", "S", "DOTALL", "X", "VERBOSE",
        "NOFLAG",
    };
    Owned exported(PyList_New(0));
    if (!exported) {
      return nullptr;
    }
    for (const char* name : exported_names) {
      Owned entry(PyUnicode_FromString(name));
      if (!entry || PyList_Append(exported.get(), entry.get()) < 0) {
        return nullptr;
      }
    }
    if (PyModule_AddObjectRef(module.get(), "__all__", exported.get()) < 0) {
      return nullptr;
    }
    return module.release();
  } catch (...) {
    return translate_exception();
  }
}
