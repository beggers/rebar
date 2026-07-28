#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <ctype.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

_Static_assert(
    sizeof(void (*)(void)) == sizeof(uintptr_t),
    "the pinned Python extension ABI requires address-sized function pointers"
);

#define GO_FUNCTION_SLOT(function) ((void *)(uintptr_t)(function))

/*
 * This module owns the Python boundary for candidates/go/engine.go. Its
 * module state, exception, Unicode helper, and heap type are separately
 * allocated in every CPython interpreter. Only opaque, Go-owned cgo handles
 * cross the native boundary; Python objects never enter the Go handle table.
 */

enum {
    GO_FLAG_IGNORECASE = 2,
    GO_FLAG_LOCALE = 4,
    GO_FLAG_ASCII = 256,
    GO_TRAIT_ASCII_DIGIT = 1 << 0,
    GO_TRAIT_ASCII_SPACE = 1 << 1,
    GO_TRAIT_ASCII_WORD = 1 << 2,
    GO_TRAIT_UNICODE_DIGIT = 1 << 3,
    GO_TRAIT_UNICODE_SPACE = 1 << 4,
    GO_TRAIT_UNICODE_WORD = 1 << 5,
    GO_TRAIT_LOCALE_WORD = 1 << 6,
    GO_FAILURE_PATTERN = 1,
    GO_FAILURE_UNICODE_NAME = 2,
    GO_FAILURE_LIMIT = 3,
    GO_UNICODE_SCALAR_COUNT = 0x110000,
    GO_UNICODE_CASE_SEQUENCE = 3,
};

extern uint64_t rebar_go_compile(
    uint32_t *source,
    size_t length,
    uint32_t flags,
    uint8_t byte_mode,
    uint32_t *unicode_simple,
    uint32_t *unicode_expanded,
    size_t unicode_count,
    uint8_t *identifier_starts,
    uint8_t *identifier_continues,
    size_t *named_positions,
    uint32_t *named_values,
    size_t named_count,
    char **error_message,
    int64_t *error_position,
    int *error_kind
);
extern int rebar_go_release(uint64_t handle);
extern size_t rebar_go_group_count(uint64_t handle);
extern uint32_t rebar_go_flags(uint64_t handle);
extern size_t rebar_go_name_count(uint64_t handle);
extern size_t rebar_go_name_group(uint64_t handle, size_t index);
extern size_t rebar_go_name_length(uint64_t handle, size_t index);
extern size_t rebar_go_copy_name(
    uint64_t handle,
    size_t index,
    uint8_t *destination,
    size_t capacity
);
extern int rebar_go_execute(
    uint64_t handle,
    uint32_t *characters,
    uint32_t *lowercase,
    uint32_t *locale_lower,
    uint8_t *traits,
    size_t length,
    size_t beginning,
    size_t end,
    uint8_t anchored,
    uint8_t fullmatch,
    uint8_t reject_first_empty,
    int64_t *spans,
    size_t span_count,
    int64_t *last_index
);

typedef struct {
    PyObject *program_type;
    PyObject *syntax_error;
    PyObject *unicode_module;
    uint32_t *unicode_simple;
    uint32_t *unicode_expanded;
    size_t unicode_count;
} GoModuleState;

typedef struct {
    uint32_t codepoint;
    uint32_t fold[GO_UNICODE_CASE_SEQUENCE];
    uint32_t uppercase[GO_UNICODE_CASE_SEQUENCE];
    uint8_t fold_length;
    uint8_t uppercase_length;
} GoUnicodeCase;

typedef struct {
    PyObject_HEAD
    uint64_t handle;
    PyObject *groupindex;
    Py_ssize_t groups;
    uint32_t flags;
    int byte_mode;
} GoProgramObject;

typedef struct {
    uint32_t *characters;
    uint32_t *lowercase;
    uint8_t *traits;
    Py_ssize_t length;
    Py_buffer buffer;
    int has_buffer;
} GoSubject;

static GoModuleState *go_module_state(PyObject *module) {
    GoModuleState *state = (GoModuleState *)PyModule_GetState(module);
    if (state == NULL && !PyErr_Occurred()) {
        PyErr_SetString(
            PyExc_SystemError,
            "Go regular-expression bridge has no interpreter-local state"
        );
    }
    return state;
}

static void *go_allocate(Py_ssize_t count, size_t item_size) {
    if (count < 0 || (size_t)count > SIZE_MAX / item_size) {
        PyErr_NoMemory();
        return NULL;
    }
    if (count == 0) {
        return NULL;
    }
    void *result = PyMem_Malloc((size_t)count * item_size);
    if (result == NULL) {
        PyErr_NoMemory();
    }
    return result;
}

static uint32_t go_unicode_component(
    uint32_t *components,
    uint32_t value
) {
    uint32_t root = value;
    while (components[root] != root) {
        root = components[root];
    }
    while (components[value] != value) {
        uint32_t parent = components[value];
        components[value] = root;
        value = parent;
    }
    return root;
}

static void go_unicode_join(
    uint32_t *components,
    uint32_t first,
    uint32_t second
) {
    uint32_t first_root = go_unicode_component(components, first);
    uint32_t second_root = go_unicode_component(components, second);
    if (first_root < second_root) {
        components[second_root] = first_root;
    } else if (second_root < first_root) {
        components[first_root] = second_root;
    }
}

static int go_unicode_sequence(
    PyObject *character,
    const char *method,
    uint32_t output[GO_UNICODE_CASE_SEQUENCE],
    uint8_t *length
) {
    PyObject *converted = PyObject_CallMethod(
        character,
        method,
        NULL
    );
    if (converted == NULL) {
        return -1;
    }
    if (!PyUnicode_Check(converted)) {
        Py_DECREF(converted);
        PyErr_SetString(
            PyExc_SystemError,
            "Python Unicode character mapping returned a non-string"
        );
        return -1;
    }
    Py_ssize_t count = PyUnicode_GET_LENGTH(converted);
    if (count < 1 || count > GO_UNICODE_CASE_SEQUENCE) {
        Py_DECREF(converted);
        PyErr_SetString(
            PyExc_SystemError,
            "Python Unicode character mapping exceeded its frozen scalar width"
        );
        return -1;
    }
    int kind = PyUnicode_KIND(converted);
    const void *data = PyUnicode_DATA(converted);
    for (Py_ssize_t index = 0; index < count; index++) {
        output[index] = (uint32_t)PyUnicode_READ(
            kind,
            data,
            index
        );
    }
    for (
        Py_ssize_t index = count;
        index < GO_UNICODE_CASE_SEQUENCE;
        index++
    ) {
        output[index] = 0;
    }
    *length = (uint8_t)count;
    Py_DECREF(converted);
    return 0;
}

/*
 * Derive the entire Unicode equivalence relation from Python character data.
 * No matching engine, Unicode-15 Go table, frozen pattern, or sampled case
 * participates. Scalar lower is intentionally kept separate: backreferences
 * use it, while literal and class instructions use the transitive relation.
 */
static int go_prepare_unicode_tables(GoModuleState *state) {
    if (state->unicode_count == GO_UNICODE_SCALAR_COUNT &&
        state->unicode_simple != NULL &&
        state->unicode_expanded != NULL) {
        return 0;
    }
    if (state->unicode_count != 0 ||
        state->unicode_simple != NULL ||
        state->unicode_expanded != NULL) {
        PyErr_SetString(
            PyExc_SystemError,
            "interpreter-local Unicode metadata was incompletely initialized"
        );
        return -1;
    }
    uint32_t *simple = go_allocate(
        GO_UNICODE_SCALAR_COUNT,
        sizeof(*simple)
    );
    if (simple == NULL) {
        return -1;
    }
    uint32_t *expanded = go_allocate(
        GO_UNICODE_SCALAR_COUNT,
        sizeof(*expanded)
    );
    if (expanded == NULL) {
        PyMem_Free(simple);
        return -1;
    }
    for (uint32_t codepoint = 0;
        codepoint < GO_UNICODE_SCALAR_COUNT;
        codepoint++) {
        expanded[codepoint] = codepoint;
    }

    GoUnicodeCase *active = NULL;
    size_t active_count = 0;
    size_t capacity = 0;
    for (uint32_t codepoint = 0;
        codepoint < GO_UNICODE_SCALAR_COUNT;
        codepoint++) {
        Py_UCS4 lower = Py_UNICODE_TOLOWER((Py_UCS4)codepoint);
        Py_UCS4 upper = Py_UNICODE_TOUPPER((Py_UCS4)codepoint);
        if (lower >= GO_UNICODE_SCALAR_COUNT ||
            upper >= GO_UNICODE_SCALAR_COUNT) {
            PyErr_SetString(
                PyExc_SystemError,
                "Python Unicode scalar mapping exceeded the Unicode range"
            );
            goto failure;
        }
        simple[codepoint] = (uint32_t)lower;
        go_unicode_join(expanded, codepoint, (uint32_t)lower);
        if ((uint32_t)lower == codepoint &&
            (uint32_t)upper == codepoint) {
            continue;
        }
        if (active_count == capacity) {
            size_t next = capacity == 0 ? 64 : capacity * 2;
            if (next < capacity ||
                next > SIZE_MAX / sizeof(*active)) {
                PyErr_NoMemory();
                goto failure;
            }
            GoUnicodeCase *grown = PyMem_Realloc(
                active,
                next * sizeof(*active)
            );
            if (grown == NULL) {
                PyErr_NoMemory();
                goto failure;
            }
            active = grown;
            capacity = next;
        }
        PyObject *character = PyUnicode_FromOrdinal(
            (int)codepoint
        );
        if (character == NULL) {
            goto failure;
        }
        GoUnicodeCase *entry = &active[active_count];
        entry->codepoint = codepoint;
        int folded = go_unicode_sequence(
            character,
            "casefold",
            entry->fold,
            &entry->fold_length
        );
        int uppercase = folded < 0
            ? -1
            : go_unicode_sequence(
                character,
                "upper",
                entry->uppercase,
                &entry->uppercase_length
            );
        Py_DECREF(character);
        if (folded < 0 || uppercase < 0) {
            goto failure;
        }
        active_count++;
    }

    for (size_t first = 0; first < active_count; first++) {
        const GoUnicodeCase *left = &active[first];
        for (size_t second = 0; second < first; second++) {
            const GoUnicodeCase *right = &active[second];
            int same_fold =
                left->fold_length == right->fold_length &&
                memcmp(
                    left->fold,
                    right->fold,
                    (size_t)left->fold_length * sizeof(left->fold[0])
                ) == 0;
            int same_single_upper =
                left->uppercase_length == 1 &&
                right->uppercase_length == 1 &&
                left->uppercase[0] == right->uppercase[0];
            if (same_fold || same_single_upper) {
                go_unicode_join(
                    expanded,
                    left->codepoint,
                    right->codepoint
                );
            }
        }
    }
    for (uint32_t codepoint = 0;
        codepoint < GO_UNICODE_SCALAR_COUNT;
        codepoint++) {
        expanded[codepoint] = go_unicode_component(
            expanded,
            codepoint
        );
    }
    PyMem_Free(active);
    state->unicode_simple = simple;
    state->unicode_expanded = expanded;
    state->unicode_count = GO_UNICODE_SCALAR_COUNT;
    return 0;

failure:
    PyMem_Free(active);
    PyMem_Free(simple);
    PyMem_Free(expanded);
    return -1;
}

static int go_prepare_identifier_traits(
    const uint32_t *source,
    Py_ssize_t length,
    int byte_mode,
    uint8_t **starts,
    uint8_t **continues
) {
    *starts = NULL;
    *continues = NULL;
    if (length == 0) {
        return 0;
    }
    uint8_t *start_traits = go_allocate(
        length,
        sizeof(*start_traits)
    );
    if (start_traits == NULL) {
        return -1;
    }
    uint8_t *continue_traits = go_allocate(
        length,
        sizeof(*continue_traits)
    );
    if (continue_traits == NULL) {
        PyMem_Free(start_traits);
        return -1;
    }
    for (Py_ssize_t index = 0; index < length; index++) {
        Py_UCS4 value = (Py_UCS4)source[index];
        int ascii_start =
            value == '_' ||
            (value >= 'A' && value <= 'Z') ||
            (value >= 'a' && value <= 'z');
        int ascii_continue = ascii_start ||
            (value >= '0' && value <= '9');
        if (byte_mode || value <= 0x7f) {
            start_traits[index] = (uint8_t)ascii_start;
            continue_traits[index] = (uint8_t)ascii_continue;
            continue;
        }

        PyObject *character = PyUnicode_FromOrdinal(
            (int)value
        );
        if (character == NULL) {
            goto failure;
        }
        int start = PyUnicode_IsIdentifier(character);
        Py_DECREF(character);
        if (start < 0 || PyErr_Occurred()) {
            goto failure;
        }
        start_traits[index] = (uint8_t)(start != 0);
        if (start != 0) {
            continue_traits[index] = 1;
            continue;
        }
        Py_UCS4 prefixed[2] = {'_', value};
        PyObject *continued = PyUnicode_FromKindAndData(
            PyUnicode_4BYTE_KIND,
            prefixed,
            2
        );
        if (continued == NULL) {
            goto failure;
        }
        int continuation = PyUnicode_IsIdentifier(continued);
        Py_DECREF(continued);
        if (continuation < 0 || PyErr_Occurred()) {
            goto failure;
        }
        continue_traits[index] = (uint8_t)(continuation != 0);
    }
    *starts = start_traits;
    *continues = continue_traits;
    return 0;

failure:
    PyMem_Free(start_traits);
    PyMem_Free(continue_traits);
    return -1;
}

static int go_program_traverse(
    GoProgramObject *program,
    visitproc visit,
    void *arg
) {
    Py_VISIT(Py_TYPE(program));
    Py_VISIT(program->groupindex);
    return 0;
}

static int go_program_clear(GoProgramObject *program) {
    Py_CLEAR(program->groupindex);
    return 0;
}

static void go_program_dealloc(GoProgramObject *program) {
    PyTypeObject *type = Py_TYPE(program);
    PyObject_GC_UnTrack(program);
    if (program->handle != 0) {
        (void)rebar_go_release(program->handle);
        program->handle = 0;
    }
    (void)go_program_clear(program);
    type->tp_free((PyObject *)program);
    Py_DECREF(type);
}

static PyObject *go_program_groups(
    GoProgramObject *program,
    void *closure
) {
    (void)closure;
    return PyLong_FromSsize_t(program->groups);
}

static PyObject *go_program_flags(
    GoProgramObject *program,
    void *closure
) {
    (void)closure;
    return PyLong_FromUnsignedLong((unsigned long)program->flags);
}

static PyObject *go_program_groupindex(
    GoProgramObject *program,
    void *closure
) {
    (void)closure;
    return Py_NewRef(program->groupindex);
}

static PyObject *go_program_byte_mode(
    GoProgramObject *program,
    void *closure
) {
    (void)closure;
    return PyBool_FromLong(program->byte_mode);
}

static PyGetSetDef go_program_getsets[] = {
    {
        "groups",
        (getter)go_program_groups,
        NULL,
        "The number of independently parsed capture groups.",
        NULL,
    },
    {
        "flags",
        (getter)go_program_flags,
        NULL,
        "The effective Python-compatible pattern flags.",
        NULL,
    },
    {
        "groupindex",
        (getter)go_program_groupindex,
        NULL,
        "The independently parsed named capture groups.",
        NULL,
    },
    {
        "is_bytes",
        (getter)go_program_byte_mode,
        NULL,
        "Whether the owned program matches bytes.",
        NULL,
    },
    {NULL, NULL, NULL, NULL, NULL},
};

static PyType_Slot go_program_slots[] = {
    {Py_tp_dealloc, GO_FUNCTION_SLOT(go_program_dealloc)},
    {Py_tp_traverse, GO_FUNCTION_SLOT(go_program_traverse)},
    {Py_tp_clear, GO_FUNCTION_SLOT(go_program_clear)},
    {Py_tp_getset, (void *)go_program_getsets},
    {0, NULL},
};

static PyType_Spec go_program_spec = {
    .name = "candidates._go_bridge.Program",
    .basicsize = (int)sizeof(GoProgramObject),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT |
        Py_TPFLAGS_HAVE_GC |
        Py_TPFLAGS_IMMUTABLETYPE |
        Py_TPFLAGS_DISALLOW_INSTANTIATION,
    .slots = go_program_slots,
};

static int go_raise_pattern_error(
    GoModuleState *state,
    const char *message,
    int64_t position
) {
    PyObject *arguments = Py_BuildValue(
        "(sL)",
        message == NULL ? "invalid regular expression" : message,
        (long long)position
    );
    if (arguments == NULL) {
        return -1;
    }
    PyObject *exception = PyObject_CallObject(state->syntax_error, arguments);
    Py_DECREF(arguments);
    if (exception == NULL) {
        return -1;
    }
    PyErr_SetObject(state->syntax_error, exception);
    Py_DECREF(exception);
    return -1;
}

static int go_extract_pattern(
    PyObject *pattern,
    uint32_t **destination,
    Py_ssize_t *length,
    int *byte_mode
) {
    *destination = NULL;
    *length = 0;
    *byte_mode = 0;
    if (PyUnicode_Check(pattern)) {
        *length = PyUnicode_GET_LENGTH(pattern);
    } else if (PyBytes_Check(pattern)) {
        *length = PyBytes_GET_SIZE(pattern);
        *byte_mode = 1;
    } else {
        PyErr_SetString(
            PyExc_TypeError,
            "first argument must be string or compiled pattern"
        );
        return -1;
    }
    if (*length == 0) {
        return 0;
    }
    uint32_t *characters = go_allocate(*length, sizeof(*characters));
    if (characters == NULL) {
        return -1;
    }
    if (*byte_mode) {
        const unsigned char *source =
            (const unsigned char *)PyBytes_AS_STRING(pattern);
        for (Py_ssize_t index = 0; index < *length; index++) {
            characters[index] = (uint32_t)source[index];
        }
    } else {
        int kind = PyUnicode_KIND(pattern);
        const void *source = PyUnicode_DATA(pattern);
        for (Py_ssize_t index = 0; index < *length; index++) {
            characters[index] = (uint32_t)PyUnicode_READ(
                kind,
                source,
                index
            );
        }
    }
    *destination = characters;
    return 0;
}

static int go_resolve_unicode_name(
    GoModuleState *state,
    const char *name,
    int64_t position,
    size_t **positions,
    uint32_t **values,
    size_t *count,
    Py_ssize_t source_length
) {
    if (position < 0 ||
        (uint64_t)position >= (uint64_t)source_length ||
        *count >= (size_t)source_length) {
        PyErr_SetString(
            PyExc_SystemError,
            "Go compiler requested an invalid Unicode character name"
        );
        return -1;
    }
    if (state->unicode_module == NULL) {
        state->unicode_module = PyImport_ImportModule("unicodedata");
        if (state->unicode_module == NULL) {
            return -1;
        }
    }
    PyObject *python_name = PyUnicode_DecodeUTF8(
        name,
        (Py_ssize_t)strlen(name),
        "strict"
    );
    if (python_name == NULL) {
        return -1;
    }
    PyObject *character = PyObject_CallMethod(
        state->unicode_module,
        "lookup",
        "O",
        python_name
    );
    Py_DECREF(python_name);
    if (character == NULL) {
        if (PyErr_ExceptionMatches(PyExc_KeyError)) {
            PyErr_Clear();
            PyObject *explanation = PyUnicode_FromFormat(
                "undefined character name '%s'",
                name
            );
            if (explanation == NULL) {
                return -1;
            }
            const char *text = PyUnicode_AsUTF8(explanation);
            if (text == NULL) {
                Py_DECREF(explanation);
                return -1;
            }
            int result = go_raise_pattern_error(state, text, position);
            Py_DECREF(explanation);
            return result;
        }
        return -1;
    }
    if (!PyUnicode_Check(character) ||
        PyUnicode_GET_LENGTH(character) != 1) {
        Py_DECREF(character);
        PyErr_SetString(
            PyExc_ValueError,
            "Unicode name did not resolve to one character"
        );
        return -1;
    }
    Py_UCS4 codepoint = PyUnicode_READ_CHAR(character, 0);
    Py_DECREF(character);
    if (*count == SIZE_MAX / sizeof(**positions) ||
        *count == SIZE_MAX / sizeof(**values)) {
        PyErr_NoMemory();
        return -1;
    }
    size_t next_count = *count + 1;
    size_t *next_positions = PyMem_Realloc(
        *positions,
        next_count * sizeof(**positions)
    );
    if (next_positions == NULL) {
        PyErr_NoMemory();
        return -1;
    }
    *positions = next_positions;
    uint32_t *next_values = PyMem_Realloc(
        *values,
        next_count * sizeof(**values)
    );
    if (next_values == NULL) {
        PyErr_NoMemory();
        return -1;
    }
    *values = next_values;
    (*positions)[*count] = (size_t)position;
    (*values)[*count] = (uint32_t)codepoint;
    *count = next_count;
    return 0;
}

static PyObject *go_collect_groupindex(uint64_t handle) {
    size_t count = rebar_go_name_count(handle);
    PyObject *groups = PyDict_New();
    if (groups == NULL) {
        return NULL;
    }
    for (size_t index = 0; index < count; index++) {
        size_t length = rebar_go_name_length(handle, index);
        if (length > (size_t)PY_SSIZE_T_MAX) {
            Py_DECREF(groups);
            PyErr_SetString(
                PyExc_OverflowError,
                "named capture is too large"
            );
            return NULL;
        }
        uint8_t *spelling = NULL;
        if (length != 0) {
            spelling = go_allocate(
                (Py_ssize_t)length,
                sizeof(*spelling)
            );
            if (spelling == NULL) {
                Py_DECREF(groups);
                return NULL;
            }
        }
        size_t copied = rebar_go_copy_name(
            handle,
            index,
            spelling,
            length
        );
        if (copied != length || length == 0) {
            PyMem_Free(spelling);
            Py_DECREF(groups);
            PyErr_SetString(
                PyExc_SystemError,
                "Go regular-expression engine returned an invalid group name"
            );
            return NULL;
        }
        PyObject *name = PyUnicode_DecodeUTF8(
            (const char *)spelling,
            (Py_ssize_t)length,
            "strict"
        );
        PyMem_Free(spelling);
        if (name == NULL) {
            Py_DECREF(groups);
            return NULL;
        }
        PyObject *number = PyLong_FromSize_t(
            rebar_go_name_group(handle, index)
        );
        if (number == NULL || PyDict_SetItem(groups, name, number) < 0) {
            Py_XDECREF(number);
            Py_DECREF(name);
            Py_DECREF(groups);
            return NULL;
        }
        Py_DECREF(number);
        Py_DECREF(name);
    }
    return groups;
}

static PyObject *go_compile(
    PyObject *module,
    PyObject *const *arguments,
    Py_ssize_t count
) {
    if (count != 2) {
        PyErr_Format(
            PyExc_TypeError,
            "compile() takes exactly 2 arguments (%zd given)",
            count
        );
        return NULL;
    }
    GoModuleState *state = go_module_state(module);
    if (state == NULL) {
        return NULL;
    }
    unsigned long flag_value = PyLong_AsUnsignedLong(arguments[1]);
    if ((flag_value == (unsigned long)-1 && PyErr_Occurred()) ||
        flag_value > UINT32_MAX) {
        if (!PyErr_Occurred()) {
            PyErr_SetString(
                PyExc_OverflowError,
                "regular-expression flags exceed 32 bits"
            );
        }
        return NULL;
    }
    uint32_t *source = NULL;
    Py_ssize_t length = 0;
    int byte_mode = 0;
    if (go_extract_pattern(
            arguments[0],
            &source,
            &length,
            &byte_mode
        ) < 0) {
        return NULL;
    }
    if (!byte_mode && go_prepare_unicode_tables(state) < 0) {
        PyMem_Free(source);
        return NULL;
    }
    uint8_t *identifier_starts = NULL;
    uint8_t *identifier_continues = NULL;
    if (go_prepare_identifier_traits(
            source,
            length,
            byte_mode,
            &identifier_starts,
            &identifier_continues
        ) < 0) {
        PyMem_Free(source);
        return NULL;
    }

    size_t *named_positions = NULL;
    uint32_t *named_values = NULL;
    size_t named_count = 0;
    uint64_t handle = 0;
    while (handle == 0) {
        char *message = NULL;
        int64_t position = 0;
        int kind = GO_FAILURE_PATTERN;
        handle = rebar_go_compile(
            source,
            (size_t)length,
            (uint32_t)flag_value,
            (uint8_t)byte_mode,
            state->unicode_simple,
            state->unicode_expanded,
            state->unicode_count,
            identifier_starts,
            identifier_continues,
            named_positions,
            named_values,
            named_count,
            &message,
            &position,
            &kind
        );
        if (handle != 0) {
            free(message);
            break;
        }
        if (PyErr_Occurred()) {
            free(message);
            PyMem_Free(source);
            PyMem_Free(identifier_starts);
            PyMem_Free(identifier_continues);
            PyMem_Free(named_positions);
            PyMem_Free(named_values);
            return NULL;
        }
        if (kind == GO_FAILURE_UNICODE_NAME && message != NULL) {
            int resolved = go_resolve_unicode_name(
                state,
                message,
                position,
                &named_positions,
                &named_values,
                &named_count,
                length
            );
            free(message);
            if (resolved == 0) {
                continue;
            }
        } else if (kind == GO_FAILURE_LIMIT) {
            const char *text = message == NULL
                ? "Go regular-expression compiler exceeded a safe limit"
                : message;
            PyObject *type = strcmp(
                text,
                "maximum recursion depth exceeded"
            ) == 0 ? PyExc_RecursionError : PyExc_OverflowError;
            PyErr_SetString(type, text);
            free(message);
        } else {
            (void)go_raise_pattern_error(state, message, position);
            free(message);
        }
        PyMem_Free(source);
        PyMem_Free(identifier_starts);
        PyMem_Free(identifier_continues);
        PyMem_Free(named_positions);
        PyMem_Free(named_values);
        return NULL;
    }
    PyMem_Free(source);
    PyMem_Free(identifier_starts);
    PyMem_Free(identifier_continues);
    PyMem_Free(named_positions);
    PyMem_Free(named_values);

    size_t group_count = rebar_go_group_count(handle);
    if (group_count > (size_t)PY_SSIZE_T_MAX) {
        (void)rebar_go_release(handle);
        PyErr_SetString(
            PyExc_OverflowError,
            "regular expression has too many capture groups"
        );
        return NULL;
    }
    PyObject *groupindex = go_collect_groupindex(handle);
    if (groupindex == NULL) {
        (void)rebar_go_release(handle);
        return NULL;
    }
    PyTypeObject *type = (PyTypeObject *)state->program_type;
    GoProgramObject *program = PyObject_GC_New(
        GoProgramObject,
        type
    );
    if (program == NULL) {
        Py_DECREF(groupindex);
        (void)rebar_go_release(handle);
        return NULL;
    }
    program->handle = handle;
    program->groupindex = groupindex;
    program->groups = (Py_ssize_t)group_count;
    program->flags = rebar_go_flags(handle);
    program->byte_mode = byte_mode;
    PyObject_GC_Track(program);
    return (PyObject *)program;
}

static int go_ascii_digit(Py_UCS4 value) {
    return value >= '0' && value <= '9';
}

static int go_ascii_space(Py_UCS4 value) {
    return value == ' ' ||
        value == '\t' ||
        value == '\n' ||
        value == '\r' ||
        value == '\v' ||
        value == '\f';
}

static int go_ascii_word(Py_UCS4 value) {
    return go_ascii_digit(value) ||
        (value >= 'A' && value <= 'Z') ||
        (value >= 'a' && value <= 'z') ||
        value == '_';
}

static void go_subject_release(GoSubject *subject) {
    if (subject->has_buffer) {
        PyBuffer_Release(&subject->buffer);
        subject->has_buffer = 0;
    }
    PyMem_Free(subject->characters);
    PyMem_Free(subject->lowercase);
    PyMem_Free(subject->traits);
    subject->characters = NULL;
    subject->lowercase = NULL;
    subject->traits = NULL;
    subject->length = 0;
}

static int go_subject_prepare(
    GoProgramObject *program,
    PyObject *source,
    GoSubject *subject
) {
    memset(subject, 0, sizeof(*subject));
    if (program->byte_mode) {
        if (PyUnicode_Check(source)) {
            PyErr_SetString(
                PyExc_TypeError,
                "cannot use a bytes pattern on a string-like object"
            );
            return -1;
        }
        if (PyObject_GetBuffer(
                source,
                &subject->buffer,
                PyBUF_SIMPLE
            ) < 0) {
            return -1;
        }
        subject->has_buffer = 1;
        subject->length = subject->buffer.len;
    } else {
        if (!PyUnicode_Check(source)) {
            PyErr_SetString(
                PyExc_TypeError,
                "cannot use a string pattern on a bytes-like object"
            );
            return -1;
        }
        subject->length = PyUnicode_GET_LENGTH(source);
    }
    if (subject->length == 0) {
        return 0;
    }
    subject->characters = go_allocate(
        subject->length,
        sizeof(*subject->characters)
    );
    subject->lowercase = go_allocate(
        subject->length,
        sizeof(*subject->lowercase)
    );
    subject->traits = go_allocate(
        subject->length,
        sizeof(*subject->traits)
    );
    if (subject->characters == NULL ||
        subject->lowercase == NULL ||
        subject->traits == NULL) {
        go_subject_release(subject);
        return -1;
    }

    const unsigned char *bytes = program->byte_mode
        ? (const unsigned char *)subject->buffer.buf
        : NULL;
    int unicode_kind = program->byte_mode ? 0 : PyUnicode_KIND(source);
    const void *unicode_data = program->byte_mode
        ? NULL
        : PyUnicode_DATA(source);
    for (Py_ssize_t index = 0; index < subject->length; index++) {
        Py_UCS4 value = program->byte_mode
            ? (Py_UCS4)bytes[index]
            : PyUnicode_READ(unicode_kind, unicode_data, index);
        uint8_t traits = 0;
        if (go_ascii_digit(value)) {
            traits |= GO_TRAIT_ASCII_DIGIT;
        }
        if (go_ascii_space(value)) {
            traits |= GO_TRAIT_ASCII_SPACE;
        }
        if (go_ascii_word(value)) {
            traits |= GO_TRAIT_ASCII_WORD;
        }
        if (Py_UNICODE_ISDECIMAL(value)) {
            traits |= GO_TRAIT_UNICODE_DIGIT;
        }
        if (Py_UNICODE_ISSPACE(value)) {
            traits |= GO_TRAIT_UNICODE_SPACE;
        }
        if (value == '_' || Py_UNICODE_ISALNUM(value)) {
            traits |= GO_TRAIT_UNICODE_WORD;
        }
        if (value == '_' ||
            (value <= UINT8_MAX && isalnum((unsigned char)value))) {
            traits |= GO_TRAIT_LOCALE_WORD;
        }
        Py_UCS4 lower;
        if (program->byte_mode) {
            lower = (Py_UCS4)tolower((unsigned char)value);
        } else {
            lower = (Py_UCS4)Py_UNICODE_TOLOWER(value);
        }
        subject->characters[index] = (uint32_t)value;
        subject->lowercase[index] = (uint32_t)lower;
        subject->traits[index] = traits;
    }
    return 0;
}

static int go_bound(
    PyObject *value,
    Py_ssize_t length,
    Py_ssize_t *destination
) {
    Py_ssize_t result = PyLong_AsSsize_t(value);
    if (result == -1 && PyErr_Occurred()) {
        return -1;
    }
    if (result < 0) {
        result = 0;
    } else if (result > length) {
        result = length;
    }
    *destination = result;
    return 0;
}

static PyObject *go_pack_result(
    const int64_t *spans,
    Py_ssize_t groups,
    int64_t last_index,
    Py_ssize_t beginning,
    Py_ssize_t end
) {
    PyObject *captures = PyTuple_New(groups + 1);
    if (captures == NULL) {
        return NULL;
    }
    for (Py_ssize_t index = 0; index <= groups; index++) {
        PyObject *span = Py_BuildValue(
            "(LL)",
            (long long)spans[index * 2],
            (long long)spans[index * 2 + 1]
        );
        if (span == NULL) {
            Py_DECREF(captures);
            return NULL;
        }
        PyTuple_SET_ITEM(captures, index, span);
    }
    PyObject *last = last_index < 0
        ? Py_NewRef(Py_None)
        : PyLong_FromLongLong((long long)last_index);
    if (last == NULL) {
        Py_DECREF(captures);
        return NULL;
    }
    PyObject *python_beginning = PyLong_FromSsize_t(beginning);
    PyObject *python_end = PyLong_FromSsize_t(end);
    if (python_beginning == NULL || python_end == NULL) {
        Py_DECREF(captures);
        Py_DECREF(last);
        Py_XDECREF(python_beginning);
        Py_XDECREF(python_end);
        return NULL;
    }
    PyObject *result = PyTuple_Pack(
        4,
        captures,
        last,
        python_beginning,
        python_end
    );
    Py_DECREF(captures);
    Py_DECREF(last);
    Py_DECREF(python_beginning);
    Py_DECREF(python_end);
    return result;
}

static PyObject *go_execute(
    PyObject *module,
    PyObject *const *arguments,
    Py_ssize_t count
) {
    if (count != 7) {
        PyErr_Format(
            PyExc_TypeError,
            "execute() takes exactly 7 arguments (%zd given)",
            count
        );
        return NULL;
    }
    GoModuleState *state = go_module_state(module);
    if (state == NULL) {
        return NULL;
    }
    if (!PyObject_TypeCheck(
            arguments[0],
            (PyTypeObject *)state->program_type
        )) {
        PyErr_SetString(
            PyExc_TypeError,
            "first argument must be an interpreter-local Go program"
        );
        return NULL;
    }
    GoProgramObject *program = (GoProgramObject *)arguments[0];
    if (program->handle == 0) {
        PyErr_SetString(
            PyExc_RuntimeError,
            "Go regular-expression program has already been released"
        );
        return NULL;
    }
    int anchored = PyObject_IsTrue(arguments[4]);
    int fullmatch = PyObject_IsTrue(arguments[5]);
    int reject_empty = PyObject_IsTrue(arguments[6]);
    if (anchored < 0 || fullmatch < 0 || reject_empty < 0) {
        return NULL;
    }
    GoSubject subject;
    if (go_subject_prepare(program, arguments[1], &subject) < 0) {
        return NULL;
    }
    Py_ssize_t beginning = 0;
    Py_ssize_t end = 0;
    if (go_bound(arguments[2], subject.length, &beginning) < 0 ||
        go_bound(arguments[3], subject.length, &end) < 0) {
        go_subject_release(&subject);
        return NULL;
    }
    if (program->groups > (PY_SSIZE_T_MAX - 2) / 2) {
        go_subject_release(&subject);
        PyErr_SetString(
            PyExc_OverflowError,
            "regular expression has too many capture groups"
        );
        return NULL;
    }
    Py_ssize_t span_count = (program->groups + 1) * 2;
    int64_t *spans = go_allocate(span_count, sizeof(*spans));
    if (spans == NULL) {
        go_subject_release(&subject);
        return NULL;
    }
    uint32_t locale_lower[256];
    if (program->byte_mode) {
        for (size_t index = 0; index < 256; index++) {
            locale_lower[index] = (uint32_t)tolower(
                (unsigned char)index
            );
        }
    }
    int64_t last_index = -1;
    int outcome = rebar_go_execute(
        program->handle,
        subject.characters,
        subject.lowercase,
        program->byte_mode ? locale_lower : NULL,
        subject.traits,
        (size_t)subject.length,
        (size_t)beginning,
        (size_t)end,
        (uint8_t)anchored,
        (uint8_t)fullmatch,
        (uint8_t)reject_empty,
        spans,
        (size_t)span_count,
        &last_index
    );
    PyObject *result = NULL;
    if (outcome == 1) {
        result = go_pack_result(
            spans,
            program->groups,
            last_index,
            beginning,
            end
        );
    } else if (outcome == 0) {
        result = Py_NewRef(Py_None);
    } else if (outcome == -2) {
        PyErr_SetString(
            PyExc_RuntimeError,
            "Go regular-expression execution failed safely"
        );
    } else {
        PyErr_SetString(
            PyExc_SystemError,
            "Go regular-expression execution rejected its native arguments"
        );
    }
    PyMem_Free(spans);
    go_subject_release(&subject);
    return result;
}

static PyMethodDef go_module_methods[] = {
    {
        "compile",
        _PyCFunction_CAST(go_compile),
        METH_FASTCALL,
        "Compile a pattern using the independently owned Go engine.",
    },
    {
        "execute",
        _PyCFunction_CAST(go_execute),
        METH_FASTCALL,
        "Execute an interpreter-local, independently owned Go program.",
    },
    {NULL, NULL, 0, NULL},
};

static int go_module_traverse(
    PyObject *module,
    visitproc visit,
    void *arg
) {
    GoModuleState *state = (GoModuleState *)PyModule_GetState(module);
    if (state == NULL) {
        return 0;
    }
    Py_VISIT(state->program_type);
    Py_VISIT(state->syntax_error);
    Py_VISIT(state->unicode_module);
    return 0;
}

static int go_module_clear(PyObject *module) {
    GoModuleState *state = (GoModuleState *)PyModule_GetState(module);
    if (state != NULL) {
        PyMem_Free(state->unicode_simple);
        PyMem_Free(state->unicode_expanded);
        state->unicode_simple = NULL;
        state->unicode_expanded = NULL;
        state->unicode_count = 0;
        Py_CLEAR(state->program_type);
        Py_CLEAR(state->syntax_error);
        Py_CLEAR(state->unicode_module);
    }
    return 0;
}

static void go_module_free(void *module) {
    (void)go_module_clear((PyObject *)module);
}

static int go_module_exec(PyObject *module) {
    GoModuleState *state = go_module_state(module);
    if (state == NULL) {
        return -1;
    }
    state->syntax_error = PyErr_NewException(
        "candidates._go_bridge.NativePatternError",
        PyExc_ValueError,
        NULL
    );
    if (state->syntax_error == NULL ||
        PyModule_AddObjectRef(
            module,
            "NativePatternError",
            state->syntax_error
        ) < 0) {
        return -1;
    }
    state->program_type = PyType_FromModuleAndSpec(
        module,
        &go_program_spec,
        NULL
    );
    if (state->program_type == NULL ||
        PyModule_AddObjectRef(
            module,
            "Program",
            state->program_type
        ) < 0) {
        return -1;
    }
    return 0;
}

static PyModuleDef_Slot go_module_slots[] = {
    {Py_mod_exec, GO_FUNCTION_SLOT(go_module_exec)},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {Py_mod_gil, Py_MOD_GIL_USED},
    {0, NULL},
};

static struct PyModuleDef go_module_definition = {
    PyModuleDef_HEAD_INIT,
    .m_name = "candidates._go_bridge",
    .m_doc = "Interpreter-local Python bridge for the owned Go regex engine.",
    .m_size = (Py_ssize_t)sizeof(GoModuleState),
    .m_methods = go_module_methods,
    .m_slots = go_module_slots,
    .m_traverse = go_module_traverse,
    .m_clear = go_module_clear,
    .m_free = go_module_free,
};

PyMODINIT_FUNC PyInit__go_bridge(void) {
    return PyModuleDef_Init(&go_module_definition);
}
