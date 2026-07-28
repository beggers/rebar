#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "engine.hpp"

#include <cctype>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <limits>
#include <memory>
#include <new>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>

namespace {

using rebar_cpp::Capture;
using rebar_cpp::Category;
using rebar_cpp::CharacterTraits;
using rebar_cpp::CompileError;
using rebar_cpp::Interrupted;
using rebar_cpp::Match;
using rebar_cpp::Program;
using rebar_cpp::Subject;

struct ModuleState {
    PyObject* syntax_error = nullptr;
    PyObject* program_type = nullptr;
    PyObject* subject_type = nullptr;
    PyObject* unicode_module = nullptr;
};

struct ProgramObject {
    PyObject_HEAD
    Program* program;
};

struct SubjectObject {
    PyObject_HEAD
    PyObject* owner;
    Py_buffer buffer;
    Subject subject;
};

ModuleState* module_state(PyObject* module) noexcept {
    return static_cast<ModuleState*>(PyModule_GetState(module));
}

bool ascii_digit(char32_t value) noexcept {
    return value >= U'0' && value <= U'9';
}

bool ascii_space(char32_t value) noexcept {
    return value == U' ' || value == U'\t' || value == U'\n' ||
           value == U'\r' || value == U'\v' || value == U'\f';
}

bool ascii_word(char32_t value) noexcept {
    return ascii_digit(value) ||
           (value >= U'a' && value <= U'z') ||
           (value >= U'A' && value <= U'Z') ||
           value == U'_';
}

bool native_category(
    void*,
    Category category,
    char32_t value,
    std::uint32_t flags,
    bool bytes
) noexcept {
    const bool ascii = bytes || (flags & rebar_cpp::flag_ascii) != 0;
    switch (category) {
        case Category::digit:
            return ascii
                ? ascii_digit(value)
                : Py_UNICODE_ISDECIMAL(static_cast<Py_UCS4>(value)) != 0;
        case Category::space:
            return ascii
                ? ascii_space(value)
                : Py_UNICODE_ISSPACE(static_cast<Py_UCS4>(value)) != 0;
        case Category::word:
            if (bytes && (flags & rebar_cpp::flag_locale) != 0) {
                return value == U'_' ||
                       (value <= 0xff &&
                        std::isalnum(static_cast<unsigned char>(value)) != 0);
            }
            return ascii
                ? ascii_word(value)
                : value == U'_' ||
                  Py_UNICODE_ISALNUM(static_cast<Py_UCS4>(value)) != 0;
    }
    return false;
}

char32_t native_lower(
    void*,
    char32_t value,
    std::uint32_t flags,
    bool bytes
) noexcept {
    if (bytes && (flags & rebar_cpp::flag_locale) != 0 && value <= 0xff) {
        return static_cast<char32_t>(
            std::tolower(static_cast<unsigned char>(value))
        );
    }
    if (bytes || (flags & rebar_cpp::flag_ascii) != 0) {
        return value >= U'A' && value <= U'Z'
            ? value + (U'a' - U'A') : value;
    }
    if (value == U'\u0130' || value == U'\u0131') {
        return U'i';
    }
    if (value == U'\u017f') {
        return U's';
    }
    return static_cast<char32_t>(
        Py_UNICODE_TOLOWER(static_cast<Py_UCS4>(value))
    );
}

bool native_valid_group_name(
    void*,
    std::u32string_view name,
    bool bytes
) {
    if (name.empty() || name.size() > static_cast<std::size_t>(PY_SSIZE_T_MAX)) {
        return false;
    }
    if (bytes) {
        const char32_t first = name.front();
        if (!(first == U'_' ||
              (first >= U'a' && first <= U'z') ||
              (first >= U'A' && first <= U'Z'))) {
            return false;
        }
        for (char32_t value : name) {
            if (!ascii_word(value)) {
                return false;
            }
        }
        return true;
    }
    PyObject* python_name = PyUnicode_FromKindAndData(
        PyUnicode_4BYTE_KIND,
        name.data(),
        static_cast<Py_ssize_t>(name.size())
    );
    if (python_name == nullptr) {
        return false;
    }
    const int valid = PyUnicode_IsIdentifier(python_name);
    Py_DECREF(python_name);
    return valid != 0;
}

bool native_lookup_name(
    void* context,
    std::u32string_view name,
    char32_t* destination
) {
    auto* state = static_cast<ModuleState*>(context);
    if (name.size() > static_cast<std::size_t>(PY_SSIZE_T_MAX)) {
        PyErr_SetString(PyExc_OverflowError, "Unicode character name is too long");
        return false;
    }
    if (state->unicode_module == nullptr) {
        state->unicode_module = PyImport_ImportModule("unicodedata");
        if (state->unicode_module == nullptr) {
            return false;
        }
    }
    PyObject* python_name = PyUnicode_FromKindAndData(
        PyUnicode_4BYTE_KIND,
        name.data(),
        static_cast<Py_ssize_t>(name.size())
    );
    if (python_name == nullptr) {
        return false;
    }
    PyObject* value = PyObject_CallMethod(
        state->unicode_module,
        "lookup",
        "O",
        python_name
    );
    Py_DECREF(python_name);
    if (value == nullptr) {
        if (PyErr_ExceptionMatches(PyExc_KeyError)) {
            PyErr_Clear();
        }
        return false;
    }
    if (!PyUnicode_Check(value) || PyUnicode_GET_LENGTH(value) != 1) {
        Py_DECREF(value);
        PyErr_SetString(PyExc_ValueError, "Unicode name did not resolve to one character");
        return false;
    }
    *destination = static_cast<char32_t>(PyUnicode_READ_CHAR(value, 0));
    Py_DECREF(value);
    return true;
}

bool native_check_interrupt(void*) noexcept {
    return PyErr_Occurred() == nullptr && PyErr_CheckSignals() == 0;
}

bool native_enter_recursion(void*) noexcept {
    return Py_EnterRecursiveCall(" while compiling a regular expression") == 0;
}

void native_leave_recursion(void*) noexcept {
    Py_LeaveRecursiveCall();
}

CharacterTraits make_traits(ModuleState* state) noexcept {
    return CharacterTraits{
        state,
        native_category,
        native_lower,
        native_lookup_name,
        native_valid_group_name,
        native_check_interrupt,
        native_enter_recursion,
        native_leave_recursion,
    };
}

PyObject* translate_cpp_error(ModuleState* state) noexcept {
    try {
        throw;
    } catch (const CompileError& error) {
        if (PyErr_Occurred() != nullptr) {
            return nullptr;
        }
        PyObject* position = error.position() == rebar_cpp::no_position
            ? Py_NewRef(Py_None)
            : PyLong_FromSize_t(error.position());
        if (position == nullptr) {
            return nullptr;
        }
        PyObject* message = PyUnicode_FromString(error.what());
        if (message == nullptr) {
            Py_DECREF(position);
            return nullptr;
        }
        PyObject* arguments = PyTuple_Pack(2, message, position);
        Py_DECREF(message);
        Py_DECREF(position);
        if (arguments == nullptr) {
            return nullptr;
        }
        PyObject* instance = PyObject_CallObject(state->syntax_error, arguments);
        Py_DECREF(arguments);
        if (instance == nullptr) {
            return nullptr;
        }
        PyErr_SetObject(state->syntax_error, instance);
        Py_DECREF(instance);
    } catch (const Interrupted&) {
        if (PyErr_Occurred() == nullptr) {
            PyErr_SetString(PyExc_RuntimeError, "regular-expression operation interrupted");
        }
    } catch (const std::bad_alloc&) {
        PyErr_NoMemory();
    } catch (const std::length_error& error) {
        PyErr_SetString(PyExc_OverflowError, error.what());
    } catch (const std::exception& error) {
        PyErr_SetString(PyExc_RuntimeError, error.what());
    } catch (...) {
        PyErr_SetString(PyExc_RuntimeError, "unexpected C++ regular-expression failure");
    }
    return nullptr;
}

void program_dealloc(PyObject* value) noexcept {
    auto* program = reinterpret_cast<ProgramObject*>(value);
    PyTypeObject* type = Py_TYPE(value);
    delete program->program;
    program->program = nullptr;
    type->tp_free(value);
    Py_DECREF(type);
}

int subject_traverse(PyObject* value, visitproc visit, void* arg) noexcept {
    auto* subject = reinterpret_cast<SubjectObject*>(value);
    Py_VISIT(Py_TYPE(value));
    Py_VISIT(subject->owner);
    return 0;
}

int subject_clear(PyObject* value) noexcept {
    auto* subject = reinterpret_cast<SubjectObject*>(value);
    if (subject->buffer.obj != nullptr) {
        PyBuffer_Release(&subject->buffer);
    }
    subject->subject = Subject{};
    Py_CLEAR(subject->owner);
    return 0;
}

void subject_dealloc(PyObject* value) noexcept {
    PyTypeObject* type = Py_TYPE(value);
    if (PyObject_GC_IsTracked(value) != 0) {
        PyObject_GC_UnTrack(value);
    }
    static_cast<void>(subject_clear(value));
    type->tp_free(value);
    Py_DECREF(type);
}

PyObject* subject_length(PyObject* value, void*) noexcept {
    const auto* subject = reinterpret_cast<const SubjectObject*>(value);
    return PyLong_FromSize_t(subject->subject.length);
}

PyObject* subject_string(PyObject* value, void*) noexcept {
    const auto* subject = reinterpret_cast<const SubjectObject*>(value);
    if (subject->owner == nullptr) {
        Py_RETURN_NONE;
    }
    return Py_NewRef(subject->owner);
}

PyObject* subject_bytes(PyObject* value, void*) noexcept {
    const auto* subject = reinterpret_cast<const SubjectObject*>(value);
    return PyBool_FromLong(subject->subject.bytes ? 1 : 0);
}

PyGetSetDef subject_getters[] = {
    {"length", subject_length, nullptr, "Subject length in Python positions.", nullptr},
    {"string", subject_string, nullptr, "The original retained Python subject.", nullptr},
    {"bytes", subject_bytes, nullptr, "Whether the subject is byte-oriented.", nullptr},
    {nullptr, nullptr, nullptr, nullptr, nullptr},
};

PyType_Slot program_slots[] = {
    {Py_tp_dealloc, reinterpret_cast<void*>(program_dealloc)},
    {0, nullptr},
};

PyType_Spec program_spec = {
    "candidates._cpp_bridge.Program",
    static_cast<int>(sizeof(ProgramObject)),
    0,
    Py_TPFLAGS_DEFAULT,
    program_slots,
};

PyType_Slot subject_slots[] = {
    {Py_tp_dealloc, reinterpret_cast<void*>(subject_dealloc)},
    {Py_tp_traverse, reinterpret_cast<void*>(subject_traverse)},
    {Py_tp_clear, reinterpret_cast<void*>(subject_clear)},
    {Py_tp_getset, subject_getters},
    {0, nullptr},
};

PyType_Spec subject_spec = {
    "candidates._cpp_bridge.Subject",
    static_cast<int>(sizeof(SubjectObject)),
    0,
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    subject_slots,
};

std::u32string read_pattern(PyObject* pattern, bool& bytes) {
    std::u32string result;
    if (PyUnicode_Check(pattern) != 0) {
        bytes = false;
        const Py_ssize_t length = PyUnicode_GET_LENGTH(pattern);
        result.reserve(static_cast<std::size_t>(length));
        const int kind = PyUnicode_KIND(pattern);
        const void* data = PyUnicode_DATA(pattern);
        for (Py_ssize_t index = 0; index < length; ++index) {
            result.push_back(static_cast<char32_t>(
                PyUnicode_READ(kind, data, index)
            ));
        }
        return result;
    }
    if (PyBytes_Check(pattern) == 0) {
        PyErr_SetString(PyExc_TypeError, "first argument must be string or compiled pattern");
        throw Interrupted();
    }
    bytes = true;
    char* data = nullptr;
    Py_ssize_t length = 0;
    if (PyBytes_AsStringAndSize(pattern, &data, &length) < 0) {
        throw Interrupted();
    }
    result.reserve(static_cast<std::size_t>(length));
    for (Py_ssize_t index = 0; index < length; ++index) {
        result.push_back(static_cast<unsigned char>(data[index]));
    }
    return result;
}

PyObject* build_group_names(const Program& program) {
    PyObject* names = PyDict_New();
    if (names == nullptr) {
        return nullptr;
    }
    for (const auto& entry : program.group_names) {
        if (entry.first.size() > static_cast<std::size_t>(PY_SSIZE_T_MAX)) {
            Py_DECREF(names);
            PyErr_SetString(PyExc_OverflowError, "regular-expression group name is too long");
            return nullptr;
        }
        PyObject* name = PyUnicode_FromKindAndData(
            PyUnicode_4BYTE_KIND,
            entry.first.data(),
            static_cast<Py_ssize_t>(entry.first.size())
        );
        if (name == nullptr) {
            Py_DECREF(names);
            return nullptr;
        }
        PyObject* index = PyLong_FromSize_t(entry.second);
        if (index == nullptr || PyDict_SetItem(names, name, index) < 0) {
            Py_XDECREF(index);
            Py_DECREF(name);
            Py_DECREF(names);
            return nullptr;
        }
        Py_DECREF(index);
        Py_DECREF(name);
    }
    return names;
}

PyObject* cpp_compile(
    PyObject* module,
    PyObject* const* arguments,
    Py_ssize_t count
) noexcept {
    ModuleState* state = module_state(module);
    if (count != 2) {
        PyErr_Format(PyExc_TypeError, "compile expected 2 arguments, got %zd", count);
        return nullptr;
    }
    try {
        const unsigned long requested = PyLong_AsUnsignedLong(arguments[1]);
        if (requested == static_cast<unsigned long>(-1) && PyErr_Occurred() != nullptr) {
            return nullptr;
        }
        if (requested > std::numeric_limits<std::uint32_t>::max()) {
            PyErr_SetString(PyExc_OverflowError, "regular-expression flags exceed 32 bits");
            return nullptr;
        }
        bool bytes = false;
        std::u32string pattern = read_pattern(arguments[0], bytes);
        Program compiled = rebar_cpp::compile(
            std::move(pattern),
            bytes,
            static_cast<std::uint32_t>(requested),
            make_traits(state)
        );
        auto* type = reinterpret_cast<PyTypeObject*>(state->program_type);
        auto* owner = reinterpret_cast<ProgramObject*>(type->tp_alloc(type, 0));
        if (owner == nullptr) {
            return nullptr;
        }
        owner->program = nullptr;
        try {
            owner->program = new Program(std::move(compiled));
        } catch (...) {
            Py_DECREF(reinterpret_cast<PyObject*>(owner));
            throw;
        }
        PyObject* names = build_group_names(*owner->program);
        PyObject* groups = PyLong_FromSize_t(owner->program->group_count);
        PyObject* flags = PyLong_FromUnsignedLong(owner->program->flags);
        if (names == nullptr || groups == nullptr || flags == nullptr) {
            Py_XDECREF(names);
            Py_XDECREF(groups);
            Py_XDECREF(flags);
            Py_DECREF(reinterpret_cast<PyObject*>(owner));
            return nullptr;
        }
        PyObject* result = PyTuple_New(4);
        if (result == nullptr) {
            Py_DECREF(names);
            Py_DECREF(groups);
            Py_DECREF(flags);
            Py_DECREF(reinterpret_cast<PyObject*>(owner));
            return nullptr;
        }
        PyTuple_SET_ITEM(result, 0, reinterpret_cast<PyObject*>(owner));
        PyTuple_SET_ITEM(result, 1, groups);
        PyTuple_SET_ITEM(result, 2, names);
        PyTuple_SET_ITEM(result, 3, flags);
        return result;
    } catch (...) {
        return translate_cpp_error(state);
    }
}

PyObject* cpp_subject(
    PyObject* module,
    PyObject* const* arguments,
    Py_ssize_t count
) noexcept {
    ModuleState* state = module_state(module);
    if (count != 2) {
        PyErr_Format(PyExc_TypeError, "subject expected 2 arguments, got %zd", count);
        return nullptr;
    }
    try {
        const int bytes_mode = PyObject_IsTrue(arguments[1]);
        if (bytes_mode < 0) {
            return nullptr;
        }
        PyObject* value = arguments[0];
        if (bytes_mode == 0 && PyUnicode_Check(value) == 0) {
            PyErr_SetString(
                PyExc_TypeError,
                "cannot use a string pattern on a bytes-like object"
            );
            return nullptr;
        }
        if (bytes_mode != 0 && PyUnicode_Check(value) != 0) {
            PyErr_SetString(
                PyExc_TypeError,
                "cannot use a bytes pattern on a string-like object"
            );
            return nullptr;
        }
        auto* type = reinterpret_cast<PyTypeObject*>(state->subject_type);
        auto* subject = reinterpret_cast<SubjectObject*>(type->tp_alloc(type, 0));
        if (subject == nullptr) {
            return nullptr;
        }
        subject->owner = nullptr;
        subject->buffer = Py_buffer{};
        subject->subject = Subject{};
        subject->owner = Py_NewRef(value);

        if (bytes_mode == 0) {
            subject->subject.data = PyUnicode_DATA(value);
            subject->subject.length = static_cast<std::size_t>(
                PyUnicode_GET_LENGTH(value)
            );
            subject->subject.kind = static_cast<std::uint8_t>(PyUnicode_KIND(value));
            subject->subject.bytes = false;
        } else {
            if (PyObject_GetBuffer(value, &subject->buffer, PyBUF_SIMPLE) < 0) {
                Py_DECREF(reinterpret_cast<PyObject*>(subject));
                return nullptr;
            }
            subject->subject.data = subject->buffer.buf;
            subject->subject.length = static_cast<std::size_t>(subject->buffer.len);
            subject->subject.kind = 1;
            subject->subject.bytes = true;
        }
        PyObject* result = reinterpret_cast<PyObject*>(subject);
        if (PyObject_GC_IsTracked(result) == 0) {
            PyObject_GC_Track(result);
        }
        return result;
    } catch (...) {
        return translate_cpp_error(state);
    }
}

PyObject* python_index(std::size_t value) {
    if (value == rebar_cpp::no_position) {
        return PyLong_FromLong(-1);
    }
    return PyLong_FromSize_t(value);
}

PyObject* build_match(const Match& match) {
    if (match.captures.size() > static_cast<std::size_t>(PY_SSIZE_T_MAX)) {
        PyErr_SetString(PyExc_OverflowError, "too many regular-expression groups");
        return nullptr;
    }
    PyObject* spans = PyTuple_New(static_cast<Py_ssize_t>(match.captures.size()));
    if (spans == nullptr) {
        return nullptr;
    }
    for (std::size_t offset = 0; offset < match.captures.size(); ++offset) {
        const Capture& capture = match.captures[offset];
        PyObject* first = python_index(capture.first);
        PyObject* last = python_index(capture.last);
        if (first == nullptr || last == nullptr) {
            Py_XDECREF(first);
            Py_XDECREF(last);
            Py_DECREF(spans);
            return nullptr;
        }
        PyObject* pair = PyTuple_Pack(2, first, last);
        Py_DECREF(first);
        Py_DECREF(last);
        if (pair == nullptr) {
            Py_DECREF(spans);
            return nullptr;
        }
        PyTuple_SET_ITEM(spans, static_cast<Py_ssize_t>(offset), pair);
    }
    PyObject* last_index = match.last_index.has_value()
        ? PyLong_FromSize_t(*match.last_index)
        : Py_NewRef(Py_None);
    if (last_index == nullptr) {
        Py_DECREF(spans);
        return nullptr;
    }
    PyObject* result = PyTuple_Pack(2, spans, last_index);
    Py_DECREF(spans);
    Py_DECREF(last_index);
    return result;
}

PyObject* cpp_run(
    PyObject* module,
    PyObject* const* arguments,
    Py_ssize_t count
) noexcept {
    ModuleState* state = module_state(module);
    if (count != 6) {
        PyErr_Format(PyExc_TypeError, "run expected 6 arguments, got %zd", count);
        return nullptr;
    }
    try {
        auto* program_type = reinterpret_cast<PyTypeObject*>(state->program_type);
        auto* subject_type = reinterpret_cast<PyTypeObject*>(state->subject_type);
        if (PyObject_TypeCheck(arguments[0], program_type) == 0 ||
            PyObject_TypeCheck(arguments[1], subject_type) == 0) {
            PyErr_SetString(PyExc_TypeError, "run requires an owned C++ program and subject");
            return nullptr;
        }
        auto* handle = reinterpret_cast<ProgramObject*>(arguments[0]);
        auto* subject = reinterpret_cast<SubjectObject*>(arguments[1]);
        const Py_ssize_t raw_start = PyLong_AsSsize_t(arguments[2]);
        if (raw_start == -1 && PyErr_Occurred() != nullptr) {
            return nullptr;
        }
        const Py_ssize_t raw_end = PyLong_AsSsize_t(arguments[3]);
        if (raw_end == -1 && PyErr_Occurred() != nullptr) {
            return nullptr;
        }
        const long mode = PyLong_AsLong(arguments[4]);
        if (mode == -1 && PyErr_Occurred() != nullptr) {
            return nullptr;
        }
        const int nonempty = PyObject_IsTrue(arguments[5]);
        if (nonempty < 0) {
            return nullptr;
        }
        if (handle->program == nullptr || subject->owner == nullptr) {
            PyErr_SetString(PyExc_RuntimeError, "C++ regular-expression owner has been cleared");
            return nullptr;
        }
        const std::size_t length = subject->subject.length;
        const std::size_t start = raw_start < 0
            ? 0 : std::min(static_cast<std::size_t>(raw_start), length);
        const std::size_t end = raw_end < 0
            ? 0 : std::min(static_cast<std::size_t>(raw_end), length);
        std::optional<Match> result;
        if (mode == 0) {
            result = rebar_cpp::search(
                *handle->program,
                subject->subject,
                start,
                end,
                nonempty != 0
            );
        } else if (mode == 1 || mode == 2) {
            result = rebar_cpp::match_at(
                *handle->program,
                subject->subject,
                start,
                end,
                mode == 2,
                nonempty != 0
            );
        } else {
            PyErr_SetString(PyExc_ValueError, "invalid C++ regular-expression match mode");
            return nullptr;
        }
        if (!result.has_value()) {
            Py_RETURN_NONE;
        }
        return build_match(*result);
    } catch (...) {
        return translate_cpp_error(state);
    }
}

PyMethodDef module_methods[] = {
    {
        "compile",
        _PyCFunction_CAST(cpp_compile),
        METH_FASTCALL,
        "Compile a pattern with the independently owned C++ engine."
    },
    {
        "subject",
        _PyCFunction_CAST(cpp_subject),
        METH_FASTCALL,
        "Retain one Python subject and, when necessary, its exact buffer."
    },
    {
        "run",
        _PyCFunction_CAST(cpp_run),
        METH_FASTCALL,
        "Execute one owned C++ program against one retained subject."
    },
    {nullptr, nullptr, 0, nullptr},
};

int module_traverse(PyObject* module, visitproc visit, void* arg) noexcept {
    ModuleState* state = module_state(module);
    if (state == nullptr) {
        return 0;
    }
    Py_VISIT(state->syntax_error);
    Py_VISIT(state->program_type);
    Py_VISIT(state->subject_type);
    Py_VISIT(state->unicode_module);
    return 0;
}

int module_clear(PyObject* module) noexcept {
    ModuleState* state = module_state(module);
    if (state != nullptr) {
        Py_CLEAR(state->syntax_error);
        Py_CLEAR(state->program_type);
        Py_CLEAR(state->subject_type);
        Py_CLEAR(state->unicode_module);
    }
    return 0;
}

void module_free(void* module) noexcept {
    static_cast<void>(module_clear(static_cast<PyObject*>(module)));
}

int module_exec(PyObject* module) noexcept {
    ModuleState* state = module_state(module);
    if (state == nullptr) {
        PyErr_SetString(PyExc_SystemError, "C++ regular-expression module has no state");
        return -1;
    }
    state->syntax_error = PyErr_NewException(
        "candidates._cpp_bridge.PatternSyntaxError",
        PyExc_ValueError,
        nullptr
    );
    if (state->syntax_error == nullptr ||
        PyModule_AddObjectRef(module, "PatternSyntaxError", state->syntax_error) < 0) {
        return -1;
    }
    state->program_type = PyType_FromModuleAndSpec(module, &program_spec, nullptr);
    if (state->program_type == nullptr ||
        PyModule_AddObjectRef(module, "Program", state->program_type) < 0) {
        return -1;
    }
    state->subject_type = PyType_FromModuleAndSpec(module, &subject_spec, nullptr);
    if (state->subject_type == nullptr ||
        PyModule_AddObjectRef(module, "Subject", state->subject_type) < 0) {
        return -1;
    }
    return 0;
}

PyModuleDef_Slot module_slots[] = {
    {Py_mod_exec, reinterpret_cast<void*>(module_exec)},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {Py_mod_gil, Py_MOD_GIL_USED},
    {0, nullptr},
};

PyModuleDef module_definition = {
    PyModuleDef_HEAD_INIT,
    "candidates._cpp_bridge",
    "An independently owned C++ regular-expression engine and Python bridge.",
    static_cast<Py_ssize_t>(sizeof(ModuleState)),
    module_methods,
    module_slots,
    module_traverse,
    module_clear,
    module_free,
};

}  // namespace

PyMODINIT_FUNC PyInit__cpp_bridge(void) {
    return PyModuleDef_Init(&module_definition);
}
