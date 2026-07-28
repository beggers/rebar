#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <ctype.h>
#include <limits.h>
#include <stdint.h>
#include <string.h>

_Static_assert(
    sizeof(void (*)(void)) == sizeof(uintptr_t),
    "the pinned Python extension ABI requires address-sized function pointers"
);

#define FORTRAN_FUNCTION_SLOT(function) ((void *)(uintptr_t)(function))

enum {
    FORTRAN_FLAG_LOCALE = 4,
    FORTRAN_TRAIT_UNICODE_DIGIT = 1,
    FORTRAN_TRAIT_UNICODE_SPACE = 2,
    FORTRAN_TRAIT_UNICODE_WORD = 4,
    FORTRAN_TRAIT_ASCII_DIGIT = 8,
    FORTRAN_TRAIT_ASCII_SPACE = 16,
    FORTRAN_TRAIT_ASCII_WORD = 32,
    FORTRAN_TRAIT_LOCALE_WORD = 64
};

extern void *rebar_fortran_compile(
    const int32_t *characters,
    const int32_t *lowercase,
    const int8_t *traits,
    size_t length,
    int32_t flags,
    int byte_mode,
    int64_t *error_position,
    int *error_code
);
extern void rebar_fortran_destroy(void *handle);
extern int32_t rebar_fortran_group_count(void *handle);
extern int32_t rebar_fortran_effective_flags(void *handle);
extern int32_t rebar_fortran_name_count(void *handle);
extern int32_t rebar_fortran_name_length(void *handle, int32_t index);
extern int32_t rebar_fortran_name_group(void *handle, int32_t index);
extern int rebar_fortran_copy_name(
    void *handle,
    int32_t index,
    void *destination,
    size_t capacity
);
extern int rebar_fortran_execute(
    void *handle,
    const int32_t *characters,
    const int32_t *lowercase,
    const int8_t *traits,
    size_t length,
    int64_t start,
    int64_t end,
    int mode,
    int nonempty,
    void *spans,
    size_t span_count,
    int64_t *last_group
);

typedef struct {
    PyObject *syntax_error;
    PyObject *program_type;
    PyObject *subject_type;
} FortranModuleState;

typedef struct {
    PyObject_HEAD
    void *handle;
} FortranProgram;

typedef struct {
    PyObject_HEAD
    PyObject *owner;
    Py_buffer buffer;
    int32_t *characters;
    int32_t *lowercase;
    int8_t *traits;
    Py_ssize_t length;
    int bytes;
} FortranSubject;

typedef struct {
    int32_t *characters;
    int32_t *lowercase;
    int8_t *traits;
    Py_ssize_t length;
} CharacterArrays;

static FortranModuleState *fortran_module_state(PyObject *module) {
    return (FortranModuleState *)PyModule_GetState(module);
}

static int is_ascii_digit(Py_UCS4 value) {
    return value >= (Py_UCS4)'0' && value <= (Py_UCS4)'9';
}

static int is_ascii_space(Py_UCS4 value) {
    return value == (Py_UCS4)' ' ||
           (value >= (Py_UCS4)'\t' && value <= (Py_UCS4)'\r');
}

static int is_ascii_word(Py_UCS4 value) {
    return is_ascii_digit(value) ||
           (value >= (Py_UCS4)'A' && value <= (Py_UCS4)'Z') ||
           (value >= (Py_UCS4)'a' && value <= (Py_UCS4)'z') ||
           value == (Py_UCS4)'_';
}

int32_t rebar_fortran_unicode_case_key(int32_t value) {
    Py_UCS4 lowered;
    if (value < 0 || (uint32_t)value > UINT32_C(0x10ffff)) {
        return value;
    }
    lowered = Py_UNICODE_TOLOWER((Py_UCS4)value);
    return (int32_t)Py_UNICODE_TOLOWER(Py_UNICODE_TOUPPER(lowered));
}

int32_t rebar_fortran_locale_case_key(int32_t value) {
    if (value < 0 || value > UCHAR_MAX) {
        return value;
    }
    return (int32_t)tolower((unsigned char)value);
}

int32_t rebar_fortran_locale_is_word(int32_t value) {
    if (value < 0 || value > UCHAR_MAX) {
        return 0;
    }
    return value == (int32_t)'_' || isalnum((unsigned char)value) != 0;
}

static int8_t python_character_traits(Py_UCS4 value, int byte_mode) {
    uint8_t bits = 0;
    if (Py_UNICODE_ISDECIMAL(value)) {
        bits |= FORTRAN_TRAIT_UNICODE_DIGIT;
    }
    if (Py_UNICODE_ISSPACE(value)) {
        bits |= FORTRAN_TRAIT_UNICODE_SPACE;
    }
    if (value == (Py_UCS4)'_' || Py_UNICODE_ISALNUM(value)) {
        bits |= FORTRAN_TRAIT_UNICODE_WORD;
    }
    if (is_ascii_digit(value)) {
        bits |= FORTRAN_TRAIT_ASCII_DIGIT;
    }
    if (is_ascii_space(value)) {
        bits |= FORTRAN_TRAIT_ASCII_SPACE;
    }
    if (is_ascii_word(value)) {
        bits |= FORTRAN_TRAIT_ASCII_WORD;
    }
    if (byte_mode && value <= (Py_UCS4)UCHAR_MAX &&
        (value == (Py_UCS4)'_' || isalnum((unsigned char)value))) {
        bits |= FORTRAN_TRAIT_LOCALE_WORD;
    }
    return (int8_t)bits;
}

static Py_UCS4 python_simple_lower(Py_UCS4 value, int byte_mode) {
    if (byte_mode) {
        return (Py_UCS4)tolower((unsigned char)value);
    }
    return (Py_UCS4)rebar_fortran_unicode_case_key((int32_t)value);
}

static void clear_character_arrays(CharacterArrays *arrays) {
    PyMem_Free(arrays->characters);
    PyMem_Free(arrays->lowercase);
    PyMem_Free(arrays->traits);
    arrays->characters = NULL;
    arrays->lowercase = NULL;
    arrays->traits = NULL;
    arrays->length = 0;
}

static int allocate_character_arrays(CharacterArrays *arrays, Py_ssize_t length) {
    size_t count;
    arrays->characters = NULL;
    arrays->lowercase = NULL;
    arrays->traits = NULL;
    arrays->length = 0;
    if (length < 0 || (uint64_t)length > (uint64_t)SIZE_MAX / sizeof(int32_t)) {
        PyErr_SetString(PyExc_OverflowError, "regular-expression subject is too large");
        return -1;
    }
    count = length == 0 ? 1u : (size_t)length;
    arrays->characters = (int32_t *)PyMem_Calloc(count, sizeof(int32_t));
    arrays->lowercase = (int32_t *)PyMem_Calloc(count, sizeof(int32_t));
    arrays->traits = (int8_t *)PyMem_Calloc(count, sizeof(int8_t));
    if (arrays->characters == NULL || arrays->lowercase == NULL ||
        arrays->traits == NULL) {
        clear_character_arrays(arrays);
        PyErr_NoMemory();
        return -1;
    }
    arrays->length = length;
    return 0;
}

static int fill_unicode_arrays(PyObject *value, CharacterArrays *arrays) {
    Py_ssize_t index;
    int kind;
    const void *data;
    Py_ssize_t length = PyUnicode_GET_LENGTH(value);
    if (allocate_character_arrays(arrays, length) < 0) {
        return -1;
    }
    kind = PyUnicode_KIND(value);
    data = PyUnicode_DATA(value);
    for (index = 0; index < length; ++index) {
        Py_UCS4 character = PyUnicode_READ(kind, data, index);
        arrays->characters[index] = (int32_t)character;
        arrays->lowercase[index] = (int32_t)python_simple_lower(character, 0);
        arrays->traits[index] = python_character_traits(character, 0);
    }
    return 0;
}

static int fill_bytes_arrays(
    const unsigned char *data,
    Py_ssize_t length,
    CharacterArrays *arrays
) {
    Py_ssize_t index;
    if (allocate_character_arrays(arrays, length) < 0) {
        return -1;
    }
    for (index = 0; index < length; ++index) {
        Py_UCS4 character = (Py_UCS4)data[index];
        arrays->characters[index] = (int32_t)character;
        arrays->lowercase[index] = (int32_t)python_simple_lower(character, 1);
        arrays->traits[index] = python_character_traits(character, 1);
    }
    return 0;
}

static const char *syntax_error_message(int code) {
    switch (code) {
        case 1: return "unable to allocate a regular-expression program";
        case 2: return "bad escape (end of pattern)";
        case 3: return "missing ), unterminated subpattern";
        case 4: return "unterminated character set or bad character range";
        case 5: return "nothing to repeat or invalid repetition bounds";
        case 6: return "invalid group name or group reference";
        case 7: return "unknown extension or invalid inline flags";
        case 8: return "missing ), unterminated comment";
        case 9: return "regular-expression size or repeat bound is too large";
        case 10: return "regular-expression feature is not implemented by this Fortran candidate";
        default: return "invalid Fortran regular-expression program";
    }
}

static PyObject *raise_fortran_syntax(
    FortranModuleState *state,
    int code,
    int64_t position
) {
    PyObject *message;
    PyObject *index;
    PyObject *arguments;
    PyObject *exception;
    if (code == 1) {
        return PyErr_NoMemory();
    }
    message = PyUnicode_FromString(syntax_error_message(code));
    index = position < 0 ? Py_NewRef(Py_None) : PyLong_FromLongLong(position);
    if (message == NULL || index == NULL) {
        Py_XDECREF(message);
        Py_XDECREF(index);
        return NULL;
    }
    arguments = PyTuple_Pack(2, message, index);
    Py_DECREF(message);
    Py_DECREF(index);
    if (arguments == NULL) {
        return NULL;
    }
    exception = PyObject_CallObject(state->syntax_error, arguments);
    Py_DECREF(arguments);
    if (exception == NULL) {
        return NULL;
    }
    PyErr_SetObject(state->syntax_error, exception);
    Py_DECREF(exception);
    return NULL;
}

static void program_dealloc(PyObject *object) {
    FortranProgram *program = (FortranProgram *)object;
    PyTypeObject *type = Py_TYPE(object);
    if (program->handle != NULL) {
        rebar_fortran_destroy(program->handle);
        program->handle = NULL;
    }
    type->tp_free(object);
    Py_DECREF(type);
}

static int subject_traverse(PyObject *object, visitproc visit, void *arg) {
    FortranSubject *subject = (FortranSubject *)object;
    Py_VISIT(Py_TYPE(object));
    Py_VISIT(subject->owner);
    return 0;
}

static int subject_clear(PyObject *object) {
    FortranSubject *subject = (FortranSubject *)object;
    CharacterArrays arrays;
    if (subject->buffer.obj != NULL) {
        PyBuffer_Release(&subject->buffer);
    }
    arrays.characters = subject->characters;
    arrays.lowercase = subject->lowercase;
    arrays.traits = subject->traits;
    arrays.length = subject->length;
    clear_character_arrays(&arrays);
    subject->characters = NULL;
    subject->lowercase = NULL;
    subject->traits = NULL;
    subject->length = 0;
    Py_CLEAR(subject->owner);
    return 0;
}

static void subject_dealloc(PyObject *object) {
    PyTypeObject *type = Py_TYPE(object);
    if (PyObject_GC_IsTracked(object)) {
        PyObject_GC_UnTrack(object);
    }
    (void)subject_clear(object);
    type->tp_free(object);
    Py_DECREF(type);
}

static PyObject *subject_length(PyObject *object, void *closure) {
    const FortranSubject *subject = (const FortranSubject *)object;
    (void)closure;
    return PyLong_FromSsize_t(subject->length);
}

static PyObject *subject_string(PyObject *object, void *closure) {
    const FortranSubject *subject = (const FortranSubject *)object;
    (void)closure;
    if (subject->owner == NULL) {
        Py_RETURN_NONE;
    }
    return Py_NewRef(subject->owner);
}

static PyObject *subject_is_bytes(PyObject *object, void *closure) {
    const FortranSubject *subject = (const FortranSubject *)object;
    (void)closure;
    return PyBool_FromLong((long)subject->bytes);
}

static PyGetSetDef subject_getters[] = {
    {"length", subject_length, NULL, "Number of Python subject positions.", NULL},
    {"string", subject_string, NULL, "Retained original Python subject.", NULL},
    {"bytes", subject_is_bytes, NULL, "Whether this is a bytes subject.", NULL},
    {NULL, NULL, NULL, NULL, NULL}
};

static PyType_Slot program_slots[] = {
    {Py_tp_dealloc, FORTRAN_FUNCTION_SLOT(program_dealloc)},
    {0, NULL}
};

static PyType_Spec program_spec = {
    "candidates._fortran_bridge.Program",
    (int)sizeof(FortranProgram),
    0,
    Py_TPFLAGS_DEFAULT,
    program_slots
};

static PyType_Slot subject_slots[] = {
    {Py_tp_dealloc, FORTRAN_FUNCTION_SLOT(subject_dealloc)},
    {Py_tp_traverse, FORTRAN_FUNCTION_SLOT(subject_traverse)},
    {Py_tp_clear, FORTRAN_FUNCTION_SLOT(subject_clear)},
    {Py_tp_getset, subject_getters},
    {0, NULL}
};

static PyType_Spec subject_spec = {
    "candidates._fortran_bridge.Subject",
    (int)sizeof(FortranSubject),
    0,
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    subject_slots
};

static PyObject *collect_group_names(void *handle) {
    PyObject *mapping;
    int32_t count;
    int32_t index;
    mapping = PyDict_New();
    if (mapping == NULL) {
        return NULL;
    }
    count = rebar_fortran_name_count(handle);
    for (index = 0; index < count; ++index) {
        int32_t length = rebar_fortran_name_length(handle, index);
        int32_t number = rebar_fortran_name_group(handle, index);
        int32_t *characters;
        PyObject *name;
        PyObject *group;
        size_t capacity;
        if (length < 0 || number <= 0) {
            Py_DECREF(mapping);
            PyErr_SetString(PyExc_RuntimeError, "invalid owned Fortran group metadata");
            return NULL;
        }
        capacity = length == 0 ? 1u : (size_t)length;
        characters = (int32_t *)PyMem_Calloc(capacity, sizeof(int32_t));
        if (characters == NULL) {
            Py_DECREF(mapping);
            return PyErr_NoMemory();
        }
        if (rebar_fortran_copy_name(handle, index, characters, capacity) != 0) {
            PyMem_Free(characters);
            Py_DECREF(mapping);
            PyErr_SetString(PyExc_RuntimeError, "unable to copy owned Fortran group metadata");
            return NULL;
        }
        name = PyUnicode_FromKindAndData(
            PyUnicode_4BYTE_KIND,
            characters,
            (Py_ssize_t)length
        );
        PyMem_Free(characters);
        group = PyLong_FromLong((long)number);
        if (name == NULL || group == NULL || PyDict_SetItem(mapping, name, group) < 0) {
            Py_XDECREF(name);
            Py_XDECREF(group);
            Py_DECREF(mapping);
            return NULL;
        }
        Py_DECREF(name);
        Py_DECREF(group);
    }
    return mapping;
}

static PyObject *fortran_compile(
    PyObject *module,
    PyObject *const *arguments,
    Py_ssize_t count
) {
    FortranModuleState *state = fortran_module_state(module);
    CharacterArrays arrays;
    PyObject *pattern;
    unsigned long flags;
    int byte_mode;
    int error_code;
    int64_t error_position;
    void *handle;
    FortranProgram *program;
    PyObject *names;
    PyObject *groups;
    PyObject *effective;
    PyObject *result;

    if (count != 2) {
        PyErr_Format(PyExc_TypeError, "compile expected 2 arguments, got %zd", count);
        return NULL;
    }
    flags = PyLong_AsUnsignedLong(arguments[1]);
    if (flags == ULONG_MAX && PyErr_Occurred() != NULL) {
        return NULL;
    }
    if (flags > (unsigned long)INT32_MAX) {
        PyErr_SetString(PyExc_OverflowError, "regular-expression flags exceed 31 bits");
        return NULL;
    }
    pattern = arguments[0];
    if (PyUnicode_Check(pattern)) {
        byte_mode = 0;
        if (fill_unicode_arrays(pattern, &arrays) < 0) {
            return NULL;
        }
    } else if (PyBytes_Check(pattern)) {
        char *bytes;
        Py_ssize_t length;
        byte_mode = 1;
        if (PyBytes_AsStringAndSize(pattern, &bytes, &length) < 0 ||
            fill_bytes_arrays((const unsigned char *)bytes, length, &arrays) < 0) {
            return NULL;
        }
    } else {
        PyErr_SetString(PyExc_TypeError, "first argument must be string or compiled pattern");
        return NULL;
    }

    error_position = -1;
    error_code = 0;
    handle = rebar_fortran_compile(
        arrays.characters,
        arrays.lowercase,
        arrays.traits,
        (size_t)arrays.length,
        (int32_t)flags,
        byte_mode,
        &error_position,
        &error_code
    );
    clear_character_arrays(&arrays);
    if (handle == NULL) {
        return raise_fortran_syntax(state, error_code, error_position);
    }
    program = (FortranProgram *)((PyTypeObject *)state->program_type)->tp_alloc(
        (PyTypeObject *)state->program_type,
        0
    );
    if (program == NULL) {
        rebar_fortran_destroy(handle);
        return NULL;
    }
    program->handle = handle;
    names = collect_group_names(handle);
    groups = PyLong_FromLong((long)rebar_fortran_group_count(handle));
    effective = PyLong_FromLong((long)rebar_fortran_effective_flags(handle));
    if (names == NULL || groups == NULL || effective == NULL) {
        Py_XDECREF(names);
        Py_XDECREF(groups);
        Py_XDECREF(effective);
        Py_DECREF((PyObject *)program);
        return NULL;
    }
    result = PyTuple_New(4);
    if (result == NULL) {
        Py_DECREF(names);
        Py_DECREF(groups);
        Py_DECREF(effective);
        Py_DECREF((PyObject *)program);
        return NULL;
    }
    PyTuple_SET_ITEM(result, 0, (PyObject *)program);
    PyTuple_SET_ITEM(result, 1, groups);
    PyTuple_SET_ITEM(result, 2, names);
    PyTuple_SET_ITEM(result, 3, effective);
    return result;
}

static PyObject *fortran_subject(
    PyObject *module,
    PyObject *const *arguments,
    Py_ssize_t count
) {
    FortranModuleState *state = fortran_module_state(module);
    FortranSubject *subject;
    CharacterArrays arrays;
    PyObject *value;
    int byte_mode;

    if (count != 2) {
        PyErr_Format(PyExc_TypeError, "subject expected 2 arguments, got %zd", count);
        return NULL;
    }
    byte_mode = PyObject_IsTrue(arguments[1]);
    if (byte_mode < 0) {
        return NULL;
    }
    value = arguments[0];
    if (!byte_mode && !PyUnicode_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "cannot use a string pattern on a bytes-like object");
        return NULL;
    }
    if (byte_mode && PyUnicode_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "cannot use a bytes pattern on a string-like object");
        return NULL;
    }
    subject = (FortranSubject *)((PyTypeObject *)state->subject_type)->tp_alloc(
        (PyTypeObject *)state->subject_type,
        0
    );
    if (subject == NULL) {
        return NULL;
    }
    subject->owner = NULL;
    memset(&subject->buffer, 0, sizeof(subject->buffer));
    subject->characters = NULL;
    subject->lowercase = NULL;
    subject->traits = NULL;
    subject->length = 0;
    subject->bytes = byte_mode;
    subject->owner = Py_NewRef(value);

    if (!byte_mode) {
        if (fill_unicode_arrays(value, &arrays) < 0) {
            Py_DECREF((PyObject *)subject);
            return NULL;
        }
    } else {
        if (PyObject_GetBuffer(value, &subject->buffer, PyBUF_SIMPLE) < 0) {
            Py_DECREF((PyObject *)subject);
            return NULL;
        }
        if (fill_bytes_arrays(
                (const unsigned char *)subject->buffer.buf,
                subject->buffer.len,
                &arrays
            ) < 0) {
            Py_DECREF((PyObject *)subject);
            return NULL;
        }
    }

    subject->characters = arrays.characters;
    subject->lowercase = arrays.lowercase;
    subject->traits = arrays.traits;
    subject->length = arrays.length;
    if (!PyObject_GC_IsTracked((PyObject *)subject)) {
        PyObject_GC_Track((PyObject *)subject);
    }
    return (PyObject *)subject;
}

static PyObject *build_fortran_match(
    const int64_t *spans,
    size_t span_count,
    int64_t last_group
) {
    PyObject *groups;
    PyObject *last;
    PyObject *result;
    size_t index;
    if (span_count > (size_t)PY_SSIZE_T_MAX / 2u) {
        PyErr_SetString(PyExc_OverflowError, "too many regular-expression spans");
        return NULL;
    }
    groups = PyTuple_New((Py_ssize_t)(span_count / 2u));
    if (groups == NULL) {
        return NULL;
    }
    for (index = 0; index < span_count; index += 2u) {
        PyObject *first = PyLong_FromLongLong(spans[index]);
        PyObject *end = PyLong_FromLongLong(spans[index + 1u]);
        PyObject *pair;
        if (first == NULL || end == NULL) {
            Py_XDECREF(first);
            Py_XDECREF(end);
            Py_DECREF(groups);
            return NULL;
        }
        pair = PyTuple_Pack(2, first, end);
        Py_DECREF(first);
        Py_DECREF(end);
        if (pair == NULL) {
            Py_DECREF(groups);
            return NULL;
        }
        PyTuple_SET_ITEM(groups, (Py_ssize_t)(index / 2u), pair);
    }
    last = last_group < 0 ? Py_NewRef(Py_None) : PyLong_FromLongLong(last_group);
    if (last == NULL) {
        Py_DECREF(groups);
        return NULL;
    }
    result = PyTuple_Pack(2, groups, last);
    Py_DECREF(groups);
    Py_DECREF(last);
    return result;
}

static PyObject *fortran_run(
    PyObject *module,
    PyObject *const *arguments,
    Py_ssize_t count
) {
    FortranModuleState *state = fortran_module_state(module);
    FortranProgram *program;
    FortranSubject *subject;
    Py_ssize_t start;
    Py_ssize_t end;
    long mode;
    int nonempty;
    int outcome;
    int32_t groups;
    size_t span_count;
    int64_t *spans;
    int64_t last_group;
    PyObject *result;

    if (count != 6) {
        PyErr_Format(PyExc_TypeError, "run expected 6 arguments, got %zd", count);
        return NULL;
    }
    if (!PyObject_TypeCheck(arguments[0], (PyTypeObject *)state->program_type) ||
        !PyObject_TypeCheck(arguments[1], (PyTypeObject *)state->subject_type)) {
        PyErr_SetString(PyExc_TypeError, "run requires an owned Fortran program and subject");
        return NULL;
    }
    program = (FortranProgram *)arguments[0];
    subject = (FortranSubject *)arguments[1];
    start = PyLong_AsSsize_t(arguments[2]);
    if (start == -1 && PyErr_Occurred() != NULL) {
        return NULL;
    }
    end = PyLong_AsSsize_t(arguments[3]);
    if (end == -1 && PyErr_Occurred() != NULL) {
        return NULL;
    }
    mode = PyLong_AsLong(arguments[4]);
    if (mode == -1 && PyErr_Occurred() != NULL) {
        return NULL;
    }
    nonempty = PyObject_IsTrue(arguments[5]);
    if (nonempty < 0) {
        return NULL;
    }
    if (program->handle == NULL || subject->owner == NULL ||
        subject->characters == NULL || subject->lowercase == NULL ||
        subject->traits == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "the owned Fortran matching state was cleared");
        return NULL;
    }
    if (mode < 0 || mode > 2) {
        PyErr_SetString(PyExc_ValueError, "invalid Fortran regular-expression match mode");
        return NULL;
    }
    if (start < 0) start = 0;
    if (end < 0) end = 0;
    if (start > subject->length) start = subject->length;
    if (end > subject->length) end = subject->length;
    groups = rebar_fortran_group_count(program->handle);
    if (groups < 0 || (uint64_t)groups + 1u > SIZE_MAX / (2u * sizeof(int64_t))) {
        PyErr_SetString(PyExc_OverflowError, "too many Fortran regular-expression groups");
        return NULL;
    }
    span_count = 2u * ((size_t)groups + 1u);
    spans = (int64_t *)PyMem_Calloc(span_count, sizeof(int64_t));
    if (spans == NULL) {
        return PyErr_NoMemory();
    }
    last_group = -1;
    outcome = rebar_fortran_execute(
        program->handle,
        subject->characters,
        subject->lowercase,
        subject->traits,
        (size_t)subject->length,
        (int64_t)start,
        (int64_t)end,
        (int)mode,
        nonempty,
        spans,
        span_count,
        &last_group
    );
    if (outcome < 0) {
        PyMem_Free(spans);
        PyErr_SetString(PyExc_RuntimeError, "owned Fortran regular-expression execution failed");
        return NULL;
    }
    if (outcome == 0) {
        PyMem_Free(spans);
        Py_RETURN_NONE;
    }
    result = build_fortran_match(spans, span_count, last_group);
    PyMem_Free(spans);
    return result;
}

static PyMethodDef fortran_methods[] = {
    {
        "compile",
        _PyCFunction_CAST(fortran_compile),
        METH_FASTCALL,
        "Compile a pattern using the independently owned Fortran engine."
    },
    {
        "subject",
        _PyCFunction_CAST(fortran_subject),
        METH_FASTCALL,
        "Acquire a subject and derive its exact Python Unicode traits."
    },
    {
        "run",
        _PyCFunction_CAST(fortran_run),
        METH_FASTCALL,
        "Execute an independently owned Fortran regular-expression program."
    },
    {NULL, NULL, 0, NULL}
};

static int fortran_module_traverse(PyObject *module, visitproc visit, void *arg) {
    FortranModuleState *state = fortran_module_state(module);
    if (state == NULL) {
        return 0;
    }
    Py_VISIT(state->syntax_error);
    Py_VISIT(state->program_type);
    Py_VISIT(state->subject_type);
    return 0;
}

static int fortran_module_clear(PyObject *module) {
    FortranModuleState *state = fortran_module_state(module);
    if (state != NULL) {
        Py_CLEAR(state->syntax_error);
        Py_CLEAR(state->program_type);
        Py_CLEAR(state->subject_type);
    }
    return 0;
}

static void fortran_module_free(void *module) {
    (void)fortran_module_clear((PyObject *)module);
}

static int fortran_module_exec(PyObject *module) {
    FortranModuleState *state = fortran_module_state(module);
    if (state == NULL) {
        PyErr_SetString(PyExc_SystemError, "the Fortran module has no interpreter state");
        return -1;
    }
    state->syntax_error = PyErr_NewException(
        "candidates._fortran_bridge.PatternSyntaxError",
        PyExc_ValueError,
        NULL
    );
    if (state->syntax_error == NULL ||
        PyModule_AddObjectRef(module, "PatternSyntaxError", state->syntax_error) < 0) {
        return -1;
    }
    state->program_type = PyType_FromModuleAndSpec(module, &program_spec, NULL);
    if (state->program_type == NULL ||
        PyModule_AddObjectRef(module, "Program", state->program_type) < 0) {
        return -1;
    }
    state->subject_type = PyType_FromModuleAndSpec(module, &subject_spec, NULL);
    if (state->subject_type == NULL ||
        PyModule_AddObjectRef(module, "Subject", state->subject_type) < 0) {
        return -1;
    }
    return 0;
}

static PyModuleDef_Slot fortran_module_slots[] = {
    {Py_mod_exec, FORTRAN_FUNCTION_SLOT(fortran_module_exec)},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {Py_mod_gil, Py_MOD_GIL_USED},
    {0, NULL}
};

static struct PyModuleDef fortran_module = {
    PyModuleDef_HEAD_INIT,
    "candidates._fortran_bridge",
    "Independently owned Fortran regular-expression engine and Python bridge.",
    (Py_ssize_t)sizeof(FortranModuleState),
    fortran_methods,
    fortran_module_slots,
    fortran_module_traverse,
    fortran_module_clear,
    fortran_module_free
};

PyMODINIT_FUNC PyInit__fortran_bridge(void) {
    return PyModuleDef_Init(&fortran_module);
}
