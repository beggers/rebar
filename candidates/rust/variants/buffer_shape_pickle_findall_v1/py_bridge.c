#define _GNU_SOURCE
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

typedef struct {
    const uint32_t *source;
    size_t length;
    const size_t *named_positions;
    const uint32_t *named_values;
    size_t named_count;
    uint8_t byte_mode;
} RustScannerPhrase;

extern void *rebar_compile(const uint32_t *, size_t, uint32_t, uint8_t, const size_t *, const uint32_t *, size_t);
extern void *rebar_compile_scanner(const RustScannerPhrase *, size_t, uint32_t, size_t *);
extern void rebar_free(void *);
extern size_t rebar_groups(const void *);
extern uint32_t rebar_flags(const void *);
extern size_t rebar_name_count(const void *);
extern size_t rebar_name_len(const void *, size_t);
extern size_t rebar_name_group(const void *, size_t);
extern size_t rebar_name_copy(const void *, size_t, uint8_t *, size_t);
extern size_t rebar_error_len(void);
extern intptr_t rebar_error_pos(void);
extern uint8_t rebar_error_include(void);
extern size_t rebar_error_copy(uint8_t *, size_t);
extern int rebar_match(const void *, const uint32_t *, const uint32_t *, const uint8_t *, size_t, size_t, size_t, uint8_t, uint8_t, intptr_t *, intptr_t *, intptr_t *);
extern int rebar_match_ascii(const void *, const uint8_t *, size_t, size_t, size_t, uint8_t, uint8_t, intptr_t *, intptr_t *, intptr_t *);
extern intptr_t rebar_collect_ascii(const void *, const uint8_t *, size_t, size_t, size_t, size_t, intptr_t *, intptr_t *, intptr_t *);
#if defined(__GNUC__) || defined(__clang__)
#define RUST_OPTIONAL_SYMBOL __attribute__((weak))
#else
#define RUST_OPTIONAL_SYMBOL
#endif
extern int rebar_match_wide(const void *, const uint8_t *, size_t, uint8_t, size_t, size_t, uint8_t, uint8_t, intptr_t *, intptr_t *, intptr_t *) RUST_OPTIONAL_SYMBOL;
extern intptr_t rebar_collect_wide(const void *, const uint8_t *, size_t, uint8_t, size_t, size_t, size_t, intptr_t *, intptr_t *, intptr_t *) RUST_OPTIONAL_SYMBOL;

#define RUST_LOCAL_PATTERN_WORDS 256
#define RUST_LOCAL_NAME_WORDS 16
#define RUST_LOCAL_CAPTURE_WORDS 64
#define RUST_ITERATOR_CAPTURE_WORDS 16
#define RUST_LOCAL_BOUND_ARGS 24
#define RUST_FINDALL_BATCH_CAPACITY 16
#define RUST_FINDALL_INLINE_STRIDE 4

typedef struct {
    PyObject_VAR_HEAD
    PyObject *pattern;
    PyObject *string;
    PyObject *groupindex;
    PyObject *regs;
    Py_ssize_t groups;
    Py_ssize_t pos;
    Py_ssize_t endpos;
    intptr_t lastindex;
    intptr_t spans[];
} RustMatch;

typedef struct {
    PyObject_VAR_HEAD
    PyObject *function;
    PyObject *pattern;
    PyObject *signature;
    vectorcallfunc vectorcall;
    PyObject *prefix[];
} RustBoundMethod;

typedef enum {
    RUST_PATTERN_ATTRIBUTE_HANDLE,
    RUST_PATTERN_ATTRIBUTE_GROUPINDEX,
    RUST_PATTERN_ATTRIBUTE_PATTERN,
    RUST_PATTERN_ATTRIBUTE_LITERAL,
    RUST_PATTERN_ATTRIBUTE_TEMPLATES,
    RUST_PATTERN_ATTRIBUTE_GROUPS,
    RUST_PATTERN_ATTRIBUTE_COUNT,
} RustPatternAttribute;

static const char *const rust_pattern_attribute_spellings[
    RUST_PATTERN_ATTRIBUTE_COUNT
] = {
    "_handle",
    "_groupindex",
    "pattern",
    "_literal",
    "_templates",
    "groups",
};

#ifndef Py_GIL_DISABLED
typedef struct {
    PyTypeObject *type;
    unsigned int version;
    Py_ssize_t offsets[RUST_PATTERN_ATTRIBUTE_COUNT];
    uint8_t eligible[RUST_PATTERN_ATTRIBUTE_COUNT];
} RustPatternSlotCache;
#endif

typedef struct {
    PyTypeObject *match_type;
    PyTypeObject *iterator_type;
    PyTypeObject *scanner_type;
    PyTypeObject *bound_method_type;
    PyObject *template_helper;
    PyObject *generic_alias_factory;
    PyObject *pattern_attribute_names[RUST_PATTERN_ATTRIBUTE_COUNT];
#ifndef Py_GIL_DISABLED
    PyTypeObject *primary_pattern_type;
    RustPatternSlotCache pattern_slot_cache;
#endif
} RustBridgeState;

static struct PyModuleDef bridge_module;

static RustBridgeState *rust_bridge_state_from_module(PyObject *module) {
    if (module == NULL) {
        PyErr_SetString(PyExc_SystemError, "Rust regex bridge has no owning module");
        return NULL;
    }
    RustBridgeState *state = (RustBridgeState *)PyModule_GetState(module);
    if (state == NULL && !PyErr_Occurred()) {
        PyErr_SetString(PyExc_SystemError, "Rust regex bridge has no interpreter-local state");
    }
    return state;
}

static RustBridgeState *rust_bridge_state_from_type(PyTypeObject *type) {
    PyObject *module = PyType_GetModuleByDef(type, &bridge_module);
    if (module == NULL) return NULL;
    return rust_bridge_state_from_module(module);
}

#ifndef Py_GIL_DISABLED
static int rust_pattern_refresh_slot_cache(
    RustBridgeState *state,
    PyTypeObject *type,
    unsigned int version
) {
    PyObject *mro = type->tp_mro;
    if (!PyTuple_CheckExact(mro)) return 0;
    if (type->tp_basicsize < (Py_ssize_t)sizeof(PyObject *)) return 0;

    Py_ssize_t offsets[RUST_PATTERN_ATTRIBUTE_COUNT] = {0};
    uint8_t eligible[RUST_PATTERN_ATTRIBUTE_COUNT] = {0};
    Py_ssize_t count = PyTuple_GET_SIZE(mro);

    for (
        size_t attribute = 0;
        attribute < RUST_PATTERN_ATTRIBUTE_COUNT;
        attribute++
    ) {
        for (Py_ssize_t index = 0; index < count; index++) {
            PyObject *base_object = PyTuple_GET_ITEM(mro, index);
            if (!PyType_Check(base_object)) return 0;

            PyTypeObject *base = (PyTypeObject *)base_object;
            PyObject *dict = base->tp_dict;
            if (dict == NULL || !PyDict_CheckExact(dict)) return 0;

            PyObject *descriptor = PyDict_GetItemWithError(
                dict,
                state->pattern_attribute_names[attribute]
            );
            if (descriptor == NULL) {
                if (PyErr_Occurred()) return -1;
                continue;
            }

            if (
                Py_TYPE(descriptor) == &PyMemberDescr_Type
                && PyDescr_TYPE(descriptor) == base
            ) {
                PyMemberDescrObject *member =
                    (PyMemberDescrObject *)descriptor;
                PyMemberDef *definition = member->d_member;
                if (
                    definition != NULL
                    && definition->type == Py_T_OBJECT_EX
                    && (
                        definition->flags
                        & (Py_AUDIT_READ | Py_RELATIVE_OFFSET)
                    ) == 0
                    && definition->offset >= 0
                    && definition->offset
                        <= type->tp_basicsize
                            - (Py_ssize_t)sizeof(PyObject *)
                ) {
                    offsets[attribute] = definition->offset;
                    eligible[attribute] = 1;
                }
            }

            /* Never bypass the first descriptor in the actual MRO. */
            break;
        }
    }

    if (
        type->tp_version_tag != version
        || type->tp_getattro != PyObject_GenericGetAttr
    ) {
        return 0;
    }

    memcpy(
        state->pattern_slot_cache.offsets,
        offsets,
        sizeof(offsets)
    );
    memcpy(
        state->pattern_slot_cache.eligible,
        eligible,
        sizeof(eligible)
    );
    state->pattern_slot_cache.type = type;
    state->pattern_slot_cache.version = version;
    return 1;
}
#endif

static PyObject *rust_pattern_get_attribute(
    PyObject *pattern,
    RustPatternAttribute attribute
) {
    RustBridgeState *state = rust_bridge_state_from_type(Py_TYPE(pattern));
    if (state == NULL) return NULL;
#ifndef Py_GIL_DISABLED
    PyTypeObject *type = Py_TYPE(pattern);
    unsigned int version = type->tp_version_tag;

    if (
        type == state->primary_pattern_type
        && version != 0
        && (type->tp_flags & Py_TPFLAGS_HEAPTYPE)
        && type->tp_itemsize == 0
        && type->tp_getattro == PyObject_GenericGetAttr
    ) {
        if (
            state->pattern_slot_cache.type != type
            || state->pattern_slot_cache.version != version
        ) {
            int refreshed = rust_pattern_refresh_slot_cache(
                state,
                type,
                version
            );
            if (refreshed < 0) return NULL;
            if (refreshed == 0) {
                return PyObject_GetAttr(
                    pattern,
                    state->pattern_attribute_names[attribute]
                );
            }
        }

        if (state->pattern_slot_cache.eligible[attribute]) {
            PyObject *value = *(PyObject **)(
                (char *)pattern
                + state->pattern_slot_cache.offsets[attribute]
            );
            if (value != NULL) return Py_NewRef(value);
        }
    }
#endif

    return PyObject_GetAttr(
        pattern,
        state->pattern_attribute_names[attribute]
    );
}

static int rust_initialize_pattern_attribute_names(RustBridgeState *state) {
    for (size_t index = 0; index < RUST_PATTERN_ATTRIBUTE_COUNT; index++) {
        if (state->pattern_attribute_names[index] != NULL) continue;
        PyObject *name = PyUnicode_InternFromString(
            rust_pattern_attribute_spellings[index]
        );
        if (name == NULL) return -1;
        state->pattern_attribute_names[index] = name;
    }
    return 0;
}

static PyObject *rust_span(intptr_t begin, intptr_t end) {
    PyObject *pair = PyTuple_New(2);
    if (pair == NULL) return NULL;
    PyObject *first = PyLong_FromSsize_t((Py_ssize_t)begin);
    PyObject *second = PyLong_FromSsize_t((Py_ssize_t)end);
    if (first == NULL || second == NULL) {
        Py_XDECREF(first);
        Py_XDECREF(second);
        Py_DECREF(pair);
        return NULL;
    }
    PyTuple_SET_ITEM(pair, 0, first);
    PyTuple_SET_ITEM(pair, 1, second);
    return pair;
}

static RustMatch *rust_match_allocate(PyObject *pattern, PyObject *string, PyObject *groupindex, size_t groups, Py_ssize_t pos, Py_ssize_t endpos) {
    if (groups > (size_t)PY_SSIZE_T_MAX / 2 - 1) {
        PyErr_NoMemory();
        return NULL;
    }
    RustBridgeState *state = rust_bridge_state_from_type(Py_TYPE(pattern));
    if (state == NULL) return NULL;
    size_t stride = groups + 1;
    RustMatch *match = (RustMatch *)PyType_GenericAlloc(
        state->match_type, (Py_ssize_t)(stride * 2)
    );
    if (match == NULL) return NULL;
    match->pattern = Py_NewRef(pattern);
    match->string = Py_NewRef(string);
    match->groupindex = Py_NewRef(groupindex);
    match->regs = NULL;
    match->groups = (Py_ssize_t)groups;
    match->pos = pos;
    match->endpos = endpos;
    match->lastindex = -1;
    return match;
}

static int rust_match_group_number(RustMatch *match, PyObject *value, Py_ssize_t *number) {
    if (PyLong_CheckExact(value)) {
        *number = PyLong_AsSsize_t(value);
    } else if (PyIndex_Check(value)) {
        PyObject *index = PyNumber_Index(value);
        if (index == NULL) return 0;
        *number = PyLong_AsSsize_t(index);
        Py_DECREF(index);
    } else {
        int borrowed = PyDict_Check(match->groupindex);
        Py_ssize_t names = borrowed ? PyDict_GET_SIZE(match->groupindex) : PyMapping_Size(match->groupindex);
        if (names < 0) return 0;
        if (names == 0) {
            PyErr_SetString(PyExc_IndexError, "no such group");
            return 0;
        }
        PyObject *item = borrowed ? PyDict_GetItemWithError(match->groupindex, value) : PyObject_GetItem(match->groupindex, value);
        if (item == NULL) {
            if (PyErr_Occurred() && !PyErr_ExceptionMatches(PyExc_KeyError)) return 0;
            PyErr_Clear();
            PyErr_SetString(PyExc_IndexError, "no such group");
            return 0;
        }
        *number = PyLong_AsSsize_t(item);
        if (!borrowed) Py_DECREF(item);
    }
    if (PyErr_Occurred() || *number < 0 || *number > match->groups) {
        PyErr_Clear();
        PyErr_SetString(PyExc_IndexError, "no such group");
        return 0;
    }
    return 1;
}

static PyObject *rust_match_piece(RustMatch *match, Py_ssize_t group, PyObject *missing) {
    size_t stride = (size_t)match->groups + 1;
    intptr_t begin = match->spans[group];
    intptr_t end = match->spans[stride + (size_t)group];
    if (begin < 0) return Py_NewRef(missing);
    if (PyUnicode_Check(match->string)) return PyUnicode_Substring(match->string, (Py_ssize_t)begin, (Py_ssize_t)end);
    if (PyBytes_CheckExact(match->string)) {
        if (begin == 0 && end == (intptr_t)PyBytes_GET_SIZE(match->string)) {
            return Py_NewRef(match->string);
        }
        return PyBytes_FromStringAndSize(
            PyBytes_AS_STRING(match->string) + begin,
            (Py_ssize_t)(end - begin)
        );
    }
    Py_buffer view = {0};
    if (PyObject_GetBuffer(match->string, &view, PyBUF_SIMPLE) != 0) {
        PyErr_Clear();
        PyErr_Format(
            PyExc_TypeError,
            "expected string or bytes-like object, got '%.200s'",
            Py_TYPE(match->string)->tp_name
        );
        return NULL;
    }
    Py_ssize_t first = begin < 0 ? 0 : (Py_ssize_t)begin;
    Py_ssize_t finish = end < 0 ? 0 : (Py_ssize_t)end;
    if (first > view.len) first = view.len;
    if (finish > view.len) finish = view.len;
    if (finish < first) finish = first;
    PyObject *piece = PyBytes_FromStringAndSize((const char *)view.buf + first, finish - first);
    PyBuffer_Release(&view);
    return piece;
}

static PyObject *rust_match_group(RustMatch *match, PyObject *const *args, Py_ssize_t nargs) {
    if (nargs == 0) return rust_match_piece(match, 0, Py_None);
    if (nargs == 1) {
        Py_ssize_t group;
        return rust_match_group_number(match, args[0], &group) ? rust_match_piece(match, group, Py_None) : NULL;
    }
    PyObject *result = PyTuple_New(nargs);
    if (result == NULL) return NULL;
    for (Py_ssize_t index = 0; index < nargs; index++) {
        Py_ssize_t group;
        if (!rust_match_group_number(match, args[index], &group)) {
            Py_DECREF(result);
            return NULL;
        }
        PyObject *piece = rust_match_piece(match, group, Py_None);
        if (piece == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        PyTuple_SET_ITEM(result, index, piece);
    }
    return result;
}

static int rust_default_arg(PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames, PyObject **missing, const char *method) {
    Py_ssize_t count = kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    *missing = Py_None;
    if (count > 1) {
        PyErr_Format(PyExc_TypeError, "%s() takes at most 1 keyword argument (%zd given)", method, count);
        return 0;
    }
    if (nargs + count > 1) {
        PyErr_Format(PyExc_TypeError, "%s() takes at most 1 argument (%zd given)", method, nargs + count);
        return 0;
    }
    if (count != 0) {
        PyObject *name = PyTuple_GET_ITEM(kwnames, 0);
        if (PyUnicode_CompareWithASCIIString(name, "default") != 0) {
            if (!PyErr_Occurred()) PyErr_Format(PyExc_TypeError, "%s() got an unexpected keyword argument '%U'", method, name);
            return 0;
        }
        *missing = args[nargs];
    } else if (nargs != 0) {
        *missing = args[0];
    }
    return 1;
}

static PyObject *rust_match_groups(RustMatch *match, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    PyObject *missing;
    if (!rust_default_arg(args, nargs, kwnames, &missing, "groups")) return NULL;
    PyObject *result = PyTuple_New(match->groups);
    if (result == NULL) return NULL;
    for (Py_ssize_t group = 1; group <= match->groups; group++) {
        PyObject *piece = rust_match_piece(match, group, missing);
        if (piece == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        PyTuple_SET_ITEM(result, group - 1, piece);
    }
    return result;
}

static PyObject *rust_match_groupdict(RustMatch *match, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    PyObject *missing;
    if (!rust_default_arg(args, nargs, kwnames, &missing, "groupdict")) return NULL;
    PyObject *result = PyDict_New();
    if (result == NULL) return NULL;
    if (PyDict_Check(match->groupindex)) {
        PyObject *name;
        PyObject *number;
        Py_ssize_t cursor = 0;
        while (PyDict_Next(match->groupindex, &cursor, &name, &number)) {
            Py_ssize_t group = PyLong_AsSsize_t(number);
            PyObject *piece = PyErr_Occurred() ? NULL : rust_match_piece(match, group, missing);
            if (piece == NULL || PyDict_SetItem(result, name, piece) != 0) {
                Py_XDECREF(piece);
                Py_DECREF(result);
                return NULL;
            }
            Py_DECREF(piece);
        }
        return result;
    }
    PyObject *items = PyMapping_Items(match->groupindex);
    if (items == NULL) {
        Py_DECREF(result);
        return NULL;
    }
    for (Py_ssize_t index = 0; index < PyList_GET_SIZE(items); index++) {
        PyObject *pair = PyList_GET_ITEM(items, index);
        PyObject *name = PyTuple_GET_ITEM(pair, 0);
        Py_ssize_t group = PyLong_AsSsize_t(PyTuple_GET_ITEM(pair, 1));
        PyObject *piece = PyErr_Occurred() ? NULL : rust_match_piece(match, group, missing);
        if (piece == NULL || PyDict_SetItem(result, name, piece) != 0) {
            Py_XDECREF(piece);
            Py_DECREF(items);
            Py_DECREF(result);
            return NULL;
        }
        Py_DECREF(piece);
    }
    Py_DECREF(items);
    return result;
}

static PyObject *rust_match_bound(RustMatch *match, PyObject *const *args, Py_ssize_t nargs, int mode, const char *method) {
    Py_ssize_t group = 0;
    if (nargs > 1) {
        PyErr_Format(PyExc_TypeError, "%s expected at most 1 argument, got %zd", method, nargs);
        return NULL;
    }
    if (nargs == 1 && !rust_match_group_number(match, args[0], &group)) return NULL;
    size_t stride = (size_t)match->groups + 1;
    intptr_t begin = match->spans[group];
    intptr_t end = match->spans[stride + (size_t)group];
    if (begin < 0) begin = end = -1;
    if (mode == 0) return PyLong_FromSsize_t((Py_ssize_t)begin);
    if (mode == 1) return PyLong_FromSsize_t((Py_ssize_t)end);
    return rust_span(begin, end);
}

static PyObject *rust_match_start(RustMatch *match, PyObject *const *args, Py_ssize_t nargs) { return rust_match_bound(match, args, nargs, 0, "start"); }
static PyObject *rust_match_end(RustMatch *match, PyObject *const *args, Py_ssize_t nargs) { return rust_match_bound(match, args, nargs, 1, "end"); }
static PyObject *rust_match_span_method(RustMatch *match, PyObject *const *args, Py_ssize_t nargs) { return rust_match_bound(match, args, nargs, 2, "span"); }

static PyObject *rust_match_expand_fallback(RustMatch *match, PyObject *template) {
    RustBridgeState *state = rust_bridge_state_from_type(Py_TYPE(match));
    if (state == NULL) return NULL;
    if (state->template_helper == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Rust match template helper is not configured");
        return NULL;
    }
    PyObject *args[2] = {template, (PyObject *)match};
    return PyObject_Vectorcall(state->template_helper, args, 2, NULL);
}

static PyObject *rust_match_expand(RustMatch *match, PyObject *template);

static PyObject *rust_match_copy(RustMatch *match, PyObject *ignored) {
    (void)ignored;
    return Py_NewRef(match);
}

static PyObject *rust_match_deepcopy(RustMatch *match, PyObject *memo) {
    (void)memo;
    return Py_NewRef(match);
}

static PyObject *rust_owned_pickle_reconstruction(PyObject *value) {
    PyObject *copyreg = PyImport_ImportModule("copyreg");
    if (copyreg == NULL) return NULL;
    PyObject *reconstructor = PyObject_GetAttrString(copyreg, "_reconstructor");
    Py_DECREF(copyreg);
    if (reconstructor == NULL) return NULL;
    PyObject *arguments = PyTuple_Pack(
        3,
        (PyObject *)Py_TYPE(value),
        (PyObject *)&PyBaseObject_Type,
        Py_None
    );
    if (arguments == NULL) {
        Py_DECREF(reconstructor);
        return NULL;
    }
    PyObject *result = PyTuple_Pack(2, reconstructor, arguments);
    Py_DECREF(arguments);
    Py_DECREF(reconstructor);
    return result;
}

static PyObject *rust_match_reduce(RustMatch *match, PyObject *ignored) {
    (void)ignored;
    return rust_owned_pickle_reconstruction((PyObject *)match);
}

static PyObject *rust_match_reduce_ex(RustMatch *match, PyObject *protocol) {
    int protocol_number = PyLong_AsInt(protocol);
    if (protocol_number == -1 && PyErr_Occurred()) return NULL;
    if (protocol_number < 2) {
        return rust_owned_pickle_reconstruction((PyObject *)match);
    }
    return PyErr_Format(
        PyExc_TypeError,
        "cannot pickle '%.200s' object",
        Py_TYPE(match)->tp_name
    );
}

static PyObject *rust_match_class_getitem(PyObject *type, PyObject *item) {
    if (!PyType_Check(type)) {
        PyErr_SetString(PyExc_TypeError, "Rust match aliases require an owned match type");
        return NULL;
    }
    RustBridgeState *state = rust_bridge_state_from_type((PyTypeObject *)type);
    if (state == NULL) return NULL;
    if (state->generic_alias_factory == NULL) {
        PyErr_SetString(
            PyExc_RuntimeError,
            "owned Rust generic-alias factory is not configured"
        );
        return NULL;
    }
    return PyObject_CallFunctionObjArgs(
        state->generic_alias_factory, type, item, NULL
    );
}

static PyObject *rust_match_repr(RustMatch *match) {
    PyObject *piece = rust_match_piece(match, 0, Py_None);
    if (piece == NULL) return NULL;
    size_t stride = (size_t)match->groups + 1;
    PyObject *result = PyUnicode_FromFormat(
        "<%s object; span=(%zd, %zd), match=%.50R>",
        Py_TYPE(match)->tp_name,
        (Py_ssize_t)match->spans[0],
        (Py_ssize_t)match->spans[stride],
        piece
    );
    Py_DECREF(piece);
    return result;
}

static PyObject *rust_match_subscript(PyObject *value, PyObject *key) {
    RustMatch *match = (RustMatch *)value;
    Py_ssize_t group;
    return rust_match_group_number(match, key, &group) ? rust_match_piece(match, group, Py_None) : NULL;
}

static PyObject *rust_match_get_pattern(RustMatch *match, void *closure) { (void)closure; return Py_NewRef(match->pattern); }
static PyObject *rust_match_get_string(RustMatch *match, void *closure) { (void)closure; return Py_NewRef(match->string); }
static PyObject *rust_match_get_pos(RustMatch *match, void *closure) { (void)closure; return PyLong_FromSsize_t(match->pos); }
static PyObject *rust_match_get_endpos(RustMatch *match, void *closure) { (void)closure; return PyLong_FromSsize_t(match->endpos); }
static PyObject *rust_match_get_lastindex(RustMatch *match, void *closure) { (void)closure; return match->lastindex < 0 ? Py_NewRef(Py_None) : PyLong_FromSsize_t((Py_ssize_t)match->lastindex); }

static PyObject *rust_match_get_lastgroup(RustMatch *match, void *closure) {
    (void)closure;
    if (match->lastindex < 0) Py_RETURN_NONE;
    if (PyDict_Check(match->groupindex)) {
        PyObject *name;
        PyObject *number;
        Py_ssize_t cursor = 0;
        while (PyDict_Next(match->groupindex, &cursor, &name, &number)) {
            Py_ssize_t value = PyLong_AsSsize_t(number);
            if (PyErr_Occurred()) return NULL;
            if (value == match->lastindex) return Py_NewRef(name);
        }
        Py_RETURN_NONE;
    }
    PyObject *items = PyMapping_Items(match->groupindex);
    if (items == NULL) return NULL;
    for (Py_ssize_t index = 0; index < PyList_GET_SIZE(items); index++) {
        PyObject *pair = PyList_GET_ITEM(items, index);
        Py_ssize_t value = PyLong_AsSsize_t(PyTuple_GET_ITEM(pair, 1));
        if (PyErr_Occurred()) {
            Py_DECREF(items);
            return NULL;
        }
        if (value == match->lastindex) {
            PyObject *result = Py_NewRef(PyTuple_GET_ITEM(pair, 0));
            Py_DECREF(items);
            return result;
        }
    }
    Py_DECREF(items);
    Py_RETURN_NONE;
}

static PyObject *rust_match_build_spans(RustMatch *match, int missing_none) {
    size_t stride = (size_t)match->groups + 1;
    PyObject *result = PyTuple_New((Py_ssize_t)stride);
    if (result == NULL) return NULL;
    for (size_t index = 0; index < stride; index++) {
        intptr_t begin = match->spans[index];
        intptr_t end = match->spans[stride + index];
        PyObject *item = begin < 0 && missing_none ? Py_NewRef(Py_None) : rust_span(begin < 0 ? -1 : begin, begin < 0 ? -1 : end);
        if (item == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        PyTuple_SET_ITEM(result, (Py_ssize_t)index, item);
    }
    return result;
}

static PyObject *rust_match_get_regs(RustMatch *match, void *closure) {
    (void)closure;
    if (match->regs == NULL) {
        match->regs = rust_match_build_spans(match, 0);
        if (match->regs == NULL) return NULL;
    }
    return Py_NewRef(match->regs);
}

static PyObject *rust_match_get_private_spans(RustMatch *match, void *closure) {
    (void)closure;
    return rust_match_build_spans(match, 1);
}

static int rust_match_traverse(RustMatch *match, visitproc visit, void *arg) {
    Py_VISIT(Py_TYPE(match));
    Py_VISIT(match->string);
    Py_VISIT(match->pattern);
    Py_VISIT(match->groupindex);
    Py_VISIT(match->regs);
    return 0;
}

static int rust_match_clear(RustMatch *match) {
    Py_CLEAR(match->string);
    Py_CLEAR(match->pattern);
    Py_CLEAR(match->groupindex);
    Py_CLEAR(match->regs);
    return 0;
}

static void rust_match_dealloc(RustMatch *match) {
    PyTypeObject *type = Py_TYPE(match);
    PyObject_GC_UnTrack(match);
    rust_match_clear(match);
    type->tp_free((PyObject *)match);
    Py_DECREF(type);
}

static PyObject *rust_match_new(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)type;
    if (kwargs != NULL && PyDict_GET_SIZE(kwargs) != 0) {
        PyErr_SetString(PyExc_TypeError, "re.Match() does not accept keyword arguments");
        return NULL;
    }
    PyObject *pattern;
    PyObject *string;
    PyObject *spans_value;
    PyObject *last_value;
    Py_ssize_t pos;
    Py_ssize_t endpos;
    if (!PyArg_ParseTuple(args, "OOOOnn:Match", &pattern, &string, &spans_value, &last_value, &pos, &endpos)) return NULL;
    PyObject *spans = PySequence_Fast(spans_value, "Rust match spans must be a sequence");
    if (spans == NULL) return NULL;
    Py_ssize_t stride = PySequence_Fast_GET_SIZE(spans);
    if (stride <= 0) {
        Py_DECREF(spans);
        PyErr_SetString(PyExc_ValueError, "Rust match requires a complete-match span");
        return NULL;
    }
    PyObject *groupindex = PyObject_GetAttrString(pattern, "groupindex");
    if (groupindex == NULL) {
        Py_DECREF(spans);
        return NULL;
    }
    RustMatch *match = rust_match_allocate(pattern, string, groupindex, (size_t)(stride - 1), pos, endpos);
    Py_DECREF(groupindex);
    if (match == NULL) {
        Py_DECREF(spans);
        return NULL;
    }
    for (Py_ssize_t index = 0; index < stride; index++) {
        PyObject *value = PySequence_Fast_GET_ITEM(spans, index);
        if (value == Py_None) {
            match->spans[index] = -1;
            match->spans[stride + index] = -1;
            continue;
        }
        PyObject *pair = PySequence_Fast(value, "Rust match span must be a pair");
        if (pair == NULL || PySequence_Fast_GET_SIZE(pair) != 2) {
            if (pair != NULL) {
                Py_DECREF(pair);
                PyErr_SetString(PyExc_ValueError, "Rust match span must have exactly two offsets");
            }
            Py_DECREF(spans);
            Py_DECREF(match);
            return NULL;
        }
        match->spans[index] = PyLong_AsSsize_t(PySequence_Fast_GET_ITEM(pair, 0));
        match->spans[stride + index] = PyLong_AsSsize_t(PySequence_Fast_GET_ITEM(pair, 1));
        Py_DECREF(pair);
        if (PyErr_Occurred()) {
            Py_DECREF(spans);
            Py_DECREF(match);
            return NULL;
        }
    }
    if (last_value != Py_None) {
        match->lastindex = PyLong_AsSsize_t(last_value);
        if (PyErr_Occurred()) {
            Py_DECREF(spans);
            Py_DECREF(match);
            return NULL;
        }
    }
    Py_DECREF(spans);
    return (PyObject *)match;
}

static PyMethodDef rust_match_methods[] = {
    {"group", (PyCFunction)(void (*)(void))rust_match_group, METH_FASTCALL,
     "group([group1, ...]) -> str or tuple.\n"
     "    Return subgroup(s) of the match by indices or names.\n"
     "    For 0 returns the entire match."},
    {"groups", (PyCFunction)(void (*)(void))rust_match_groups, METH_FASTCALL | METH_KEYWORDS,
     "groups($self, /, default=None)\n--\n\n"
     "Return a tuple containing all the subgroups of the match, from 1.\n\n"
     "  default\n"
     "    Is used for groups that did not participate in the match."},
    {"groupdict", (PyCFunction)(void (*)(void))rust_match_groupdict, METH_FASTCALL | METH_KEYWORDS,
     "groupdict($self, /, default=None)\n--\n\n"
     "Return a dictionary containing all the named subgroups of the match, "
     "keyed by the subgroup name.\n\n"
     "  default\n"
     "    Is used for groups that did not participate in the match."},
    {"start", (PyCFunction)(void (*)(void))rust_match_start, METH_FASTCALL,
     "start($self, group=0, /)\n--\n\n"
     "Return index of the start of the substring matched by group."},
    {"end", (PyCFunction)(void (*)(void))rust_match_end, METH_FASTCALL,
     "end($self, group=0, /)\n--\n\n"
     "Return index of the end of the substring matched by group."},
    {"span", (PyCFunction)(void (*)(void))rust_match_span_method, METH_FASTCALL,
     "span($self, group=0, /)\n--\n\n"
     "For match object m, return the 2-tuple "
     "(m.start(group), m.end(group))."},
    {"expand", (PyCFunction)rust_match_expand, METH_O,
     "expand($self, /, template)\n--\n\n"
     "Return the string obtained by doing backslash substitution on "
     "the string template, as done by the sub() method."},
    {"__copy__", (PyCFunction)rust_match_copy, METH_NOARGS, "Return this immutable match."},
    {"__deepcopy__", (PyCFunction)rust_match_deepcopy, METH_O, "Return this immutable match."},
    {"__reduce__", (PyCFunction)rust_match_reduce, METH_NOARGS, "Return the low-protocol match reconstruction."},
    {"__reduce_ex__", (PyCFunction)rust_match_reduce_ex, METH_O, "Reduce a match for the requested pickle protocol."},
    {"__class_getitem__", (PyCFunction)rust_match_class_getitem, METH_O | METH_CLASS, "Return a generic match alias."},
    {NULL, NULL, 0, NULL},
};

static int rust_match_set_readonly(
    PyObject *match, PyObject *value, void *closure
) {
    (void)match;
    (void)value;
    (void)closure;
    PyErr_SetString(PyExc_AttributeError, "readonly attribute");
    return -1;
}

static PyGetSetDef rust_match_getsets[] = {
    {"re", (getter)rust_match_get_pattern, rust_match_set_readonly, "Compiled regular expression.", NULL},
    {"string", (getter)rust_match_get_string, rust_match_set_readonly, "Original search subject.", NULL},
    {"pos", (getter)rust_match_get_pos, rust_match_set_readonly, "Original search start.", NULL},
    {"endpos", (getter)rust_match_get_endpos, rust_match_set_readonly, "Clipped search end.", NULL},
    {"lastindex", (getter)rust_match_get_lastindex, NULL, "Last captured group index.", NULL},
    {"lastgroup", (getter)rust_match_get_lastgroup, NULL, "Last captured group name.", NULL},
    {"regs", (getter)rust_match_get_regs, NULL, "All captured offsets.", NULL},
    {"_spans", (getter)rust_match_get_private_spans, NULL, "Internal capture offsets.", NULL},
    {"_lastindex", (getter)rust_match_get_lastindex, NULL, "Internal last group index.", NULL},
    {"_pattern", (getter)rust_match_get_pattern, NULL, "Internal compiled pattern.", NULL},
    {"_string", (getter)rust_match_get_string, NULL, "Internal search subject.", NULL},
    {NULL, NULL, NULL, NULL, NULL},
};

static PyType_Slot rust_match_slots[] = {
    {Py_tp_dealloc, (void *)rust_match_dealloc},
    {Py_tp_repr, (void *)rust_match_repr},
    {Py_mp_subscript, (void *)rust_match_subscript},
    {Py_tp_doc, "Native match from the from-scratch Rust regular-expression engine."},
    {Py_tp_methods, rust_match_methods},
    {Py_tp_getset, rust_match_getsets},
    {Py_tp_traverse, (void *)rust_match_traverse},
    {Py_tp_clear, (void *)rust_match_clear},
    {Py_tp_new, (void *)rust_match_new},
    {0, NULL},
};

static PyType_Spec rust_match_spec = {
    .name = "re.Match",
    .basicsize = (int)offsetof(RustMatch, spans),
    .itemsize = (int)sizeof(intptr_t),
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = rust_match_slots,
};

static PyObject *bridge_set_template(PyObject *module, PyObject *value) {
    RustBridgeState *state = rust_bridge_state_from_module(module);
    if (state == NULL) return NULL;
    if (!PyFunction_Check(value)) {
        PyErr_SetString(
            PyExc_TypeError,
            "Rust match template helper must be an owned Python function"
        );
        return NULL;
    }

    PyObject *globals = PyFunction_GetGlobals(value);
    if (globals == NULL || !PyDict_Check(globals)) {
        PyErr_SetString(
            PyExc_TypeError,
            "Rust match template helper has no owned module globals"
        );
        return NULL;
    }

    PyObject *owner = PyDict_GetItemString(globals, "__name__");
    PyObject *owned_template = PyDict_GetItemString(globals, "_template");
    PyObject *factory = PyDict_GetItemString(globals, "_OwnedGenericAlias");
    PyObject *resolver = PyDict_GetItemString(
        globals, "_restore_owned_generic_alias"
    );
    PyObject *pattern = PyDict_GetItemString(globals, "Pattern");
    PyObject *match = PyDict_GetItemString(globals, "Match");
    if (
        owner == NULL
        || !PyUnicode_Check(owner)
        || PyUnicode_CompareWithASCIIString(
            owner, "candidates.rust_candidate"
        ) != 0
        || owned_template != value
        || factory == NULL
        || !PyType_Check(factory)
        || resolver == NULL
        || !PyFunction_Check(resolver)
        || PyFunction_GetGlobals(resolver) != globals
        || pattern == NULL
        || !PyType_Check(pattern)
        || match != (PyObject *)state->match_type
    ) {
        if (!PyErr_Occurred()) {
            PyErr_SetString(
                PyExc_TypeError,
                "Rust template and generic aliases must originate from the owned candidate"
            );
        }
        return NULL;
    }

#ifndef Py_GIL_DISABLED
    if (
        state->primary_pattern_type == NULL
        || pattern != (PyObject *)state->primary_pattern_type
    ) {
        PyErr_SetString(
            PyExc_TypeError,
            "Rust generic aliases require the final owned native Pattern type"
        );
        return NULL;
    }
#endif

    PyObject *factory_module = PyObject_GetAttrString(
        factory, "__module__"
    );
    if (factory_module == NULL) return NULL;
    PyObject *factory_name = PyObject_GetAttrString(
        factory, "__qualname__"
    );
    if (factory_name == NULL) {
        Py_DECREF(factory_module);
        return NULL;
    }
    PyObject *pattern_module = PyObject_GetAttrString(
        pattern, "__module__"
    );
    if (pattern_module == NULL) {
        Py_DECREF(factory_name);
        Py_DECREF(factory_module);
        return NULL;
    }
    PyObject *pattern_name = PyObject_GetAttrString(
        pattern, "__qualname__"
    );
    if (pattern_name == NULL) {
        Py_DECREF(pattern_module);
        Py_DECREF(factory_name);
        Py_DECREF(factory_module);
        return NULL;
    }

    int owned_public_types =
        PyUnicode_Check(factory_module)
        && PyUnicode_Check(factory_name)
        && PyUnicode_Check(pattern_module)
        && PyUnicode_Check(pattern_name)
        && PyUnicode_CompareWithASCIIString(
            factory_module, "candidates.rust_candidate"
        ) == 0
        && PyUnicode_CompareWithASCIIString(
            factory_name, "_OwnedGenericAlias"
        ) == 0
        && PyUnicode_CompareWithASCIIString(pattern_module, "re") == 0
        && PyUnicode_CompareWithASCIIString(pattern_name, "Pattern") == 0;
    Py_DECREF(pattern_name);
    Py_DECREF(pattern_module);
    Py_DECREF(factory_name);
    Py_DECREF(factory_module);
    if (!owned_public_types) {
        if (!PyErr_Occurred()) {
            PyErr_SetString(
                PyExc_TypeError,
                "Rust generic aliases must retain their owned factory and re.Pattern"
            );
        }
        return NULL;
    }

    Py_XSETREF(state->generic_alias_factory, Py_NewRef(factory));
    Py_XSETREF(state->template_helper, Py_NewRef(value));
    Py_RETURN_NONE;
}

static PyObject *rust_owned_tuple4(PyObject *first, PyObject *second, PyObject *third, PyObject *fourth) {
    if (first == NULL || second == NULL || third == NULL || fourth == NULL) {
        Py_XDECREF(first);
        Py_XDECREF(second);
        Py_XDECREF(third);
        Py_XDECREF(fourth);
        return NULL;
    }
    PyObject *result = PyTuple_New(4);
    if (result == NULL) {
        Py_DECREF(first);
        Py_DECREF(second);
        Py_DECREF(third);
        Py_DECREF(fourth);
        return NULL;
    }
    PyTuple_SET_ITEM(result, 0, first);
    PyTuple_SET_ITEM(result, 1, second);
    PyTuple_SET_ITEM(result, 2, third);
    PyTuple_SET_ITEM(result, 3, fourth);
    return result;
}

static PyObject *bridge_compile(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 4) {
        PyErr_Format(PyExc_TypeError, "compile() takes exactly 4 arguments (%zd given)", nargs);
        return NULL;
    }
    PyObject *pattern = args[0];
    int byte_mode = PyBytes_Check(pattern);
    if (!byte_mode && !PyUnicode_Check(pattern)) {
        PyErr_SetString(PyExc_TypeError, "Rust compiler expects a string or bytes pattern");
        return NULL;
    }
    unsigned long flags = PyLong_AsUnsignedLong(args[1]);
    if (PyErr_Occurred() || flags > UINT32_MAX) {
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_OverflowError, "Rust regex flags exceed 32 bits");
        return NULL;
    }
    if (!PyTuple_Check(args[2]) || !PyTuple_Check(args[3])) {
        PyErr_SetString(PyExc_TypeError, "Rust named escapes must be tuples");
        return NULL;
    }
    Py_ssize_t count = PyTuple_GET_SIZE(args[2]);
    if (count != PyTuple_GET_SIZE(args[3])) {
        PyErr_SetString(PyExc_ValueError, "Rust named-escape positions and values differ in length");
        return NULL;
    }
    uint32_t local_pattern[RUST_LOCAL_PATTERN_WORDS];
    uint32_t *owned_pattern = NULL;
    const uint32_t *source = local_pattern;
    Py_ssize_t length = byte_mode ? PyBytes_GET_SIZE(pattern) : PyUnicode_GET_LENGTH(pattern);
    if (!byte_mode && PyUnicode_KIND(pattern) == PyUnicode_4BYTE_KIND && length != 0) {
        source = (const uint32_t *)PyUnicode_4BYTE_DATA(pattern);
    } else {
        if ((size_t)length > SIZE_MAX / sizeof(uint32_t)) return PyErr_NoMemory();
        if (length > RUST_LOCAL_PATTERN_WORDS) {
            owned_pattern = PyMem_Malloc((size_t)length * sizeof(uint32_t));
            if (owned_pattern == NULL) return PyErr_NoMemory();
            source = owned_pattern;
        }
        if (byte_mode) {
            const uint8_t *data = (const uint8_t *)PyBytes_AS_STRING(pattern);
            for (Py_ssize_t index = 0; index < length; index++) ((uint32_t *)source)[index] = data[index];
        } else {
            int kind = PyUnicode_KIND(pattern);
            const void *data = PyUnicode_DATA(pattern);
            for (Py_ssize_t index = 0; index < length; index++) ((uint32_t *)source)[index] = PyUnicode_READ(kind, data, index);
        }
    }
    size_t local_positions[RUST_LOCAL_NAME_WORDS];
    uint32_t local_values[RUST_LOCAL_NAME_WORDS];
    size_t *positions = local_positions;
    uint32_t *values = local_values;
    void *owned_names = NULL;
    if (count > RUST_LOCAL_NAME_WORDS) {
        if ((size_t)count > SIZE_MAX / (sizeof(size_t) + sizeof(uint32_t))) {
            PyMem_Free(owned_pattern);
            return PyErr_NoMemory();
        }
        owned_names = PyMem_Malloc((size_t)count * (sizeof(size_t) + sizeof(uint32_t)));
        if (owned_names == NULL) {
            PyMem_Free(owned_pattern);
            return PyErr_NoMemory();
        }
        positions = owned_names;
        values = (uint32_t *)(positions + count);
    }
    for (Py_ssize_t index = 0; index < count; index++) {
        positions[index] = PyLong_AsSize_t(PyTuple_GET_ITEM(args[2], index));
        unsigned long value = PyLong_AsUnsignedLong(PyTuple_GET_ITEM(args[3], index));
        if (PyErr_Occurred() || value > UINT32_MAX) {
            if (!PyErr_Occurred()) PyErr_SetString(PyExc_OverflowError, "Rust named escape exceeds 32 bits");
            PyMem_Free(owned_names);
            PyMem_Free(owned_pattern);
            return NULL;
        }
        values[index] = (uint32_t)value;
    }
    void *handle = rebar_compile(source, (size_t)length, (uint32_t)flags, (uint8_t)byte_mode, positions, values, (size_t)count);
    PyMem_Free(owned_names);
    PyMem_Free(owned_pattern);
    if (handle == NULL) Py_RETURN_NONE;

    PyObject *names = PyDict_New();
    if (names == NULL) {
        rebar_free(handle);
        return NULL;
    }
    size_t name_count = rebar_name_count(handle);
    for (size_t index = 0; index < name_count; index++) {
        size_t width = rebar_name_len(handle, index);
        if (width > (size_t)PY_SSIZE_T_MAX) {
            PyErr_SetString(PyExc_OverflowError, "Rust regex group name is too large");
            Py_DECREF(names);
            rebar_free(handle);
            return NULL;
        }
        uint8_t local_name[256];
        uint8_t *name = local_name;
        if (width > sizeof(local_name)) {
            name = PyMem_Malloc(width);
            if (name == NULL) {
                Py_DECREF(names);
                rebar_free(handle);
                return PyErr_NoMemory();
            }
        }
        size_t copied = rebar_name_copy(handle, index, name, width);
        PyObject *key = copied == width ? PyUnicode_DecodeUTF8((const char *)name, (Py_ssize_t)width, "strict") : NULL;
        if (copied != width && !PyErr_Occurred()) PyErr_SetString(PyExc_RuntimeError, "Rust regex group-name copy failed");
        if (name != local_name) PyMem_Free(name);
        PyObject *number = key == NULL ? NULL : PyLong_FromSize_t(rebar_name_group(handle, index));
        if (key == NULL || number == NULL || PyDict_SetItem(names, key, number) < 0) {
            Py_XDECREF(key);
            Py_XDECREF(number);
            Py_DECREF(names);
            rebar_free(handle);
            return NULL;
        }
        Py_DECREF(key);
        Py_DECREF(number);
    }
    PyObject *result = rust_owned_tuple4(PyLong_FromVoidPtr(handle), PyLong_FromSize_t(rebar_groups(handle)), PyLong_FromUnsignedLong(rebar_flags(handle)), names);
    if (result == NULL) rebar_free(handle);
    return result;
}

static PyObject *bridge_compile_scanner(
    PyObject *module,
    PyObject *const *args,
    Py_ssize_t nargs
) {
    (void)module;
    if (nargs != 4) {
        PyErr_Format(
            PyExc_TypeError,
            "compile_scanner() takes exactly 4 arguments (%zd given)",
            nargs
        );
        return NULL;
    }
    if (
        !PyTuple_Check(args[0])
        || !PyTuple_Check(args[2])
        || !PyTuple_Check(args[3])
    ) {
        PyErr_SetString(
            PyExc_TypeError,
            "Rust scanner phrases and named escapes must be tuples"
        );
        return NULL;
    }

    unsigned long flags = PyLong_AsUnsignedLong(args[1]);
    if (PyErr_Occurred() || flags > UINT32_MAX) {
        if (!PyErr_Occurred()) {
            PyErr_SetString(
                PyExc_OverflowError,
                "Rust regex flags exceed 32 bits"
            );
        }
        return NULL;
    }

    Py_ssize_t phrase_count = PyTuple_GET_SIZE(args[0]);
    if (
        PyTuple_GET_SIZE(args[2]) != phrase_count
        || PyTuple_GET_SIZE(args[3]) != phrase_count
    ) {
        PyErr_SetString(
            PyExc_ValueError,
            "Rust scanner phrase and named-escape counts differ"
        );
        return NULL;
    }
    size_t count = (size_t)phrase_count;
    if (
        count > SIZE_MAX / sizeof(RustScannerPhrase)
        || count > SIZE_MAX / sizeof(uint32_t *)
        || count > SIZE_MAX / sizeof(void *)
    ) {
        return PyErr_NoMemory();
    }

    RustScannerPhrase *phrases = NULL;
    uint32_t **owned_sources = NULL;
    void **owned_names = NULL;
    PyObject *result = NULL;
    void *handle = NULL;
    if (count != 0) {
        phrases = PyMem_Calloc(count, sizeof(*phrases));
        owned_sources = PyMem_Calloc(count, sizeof(*owned_sources));
        owned_names = PyMem_Calloc(count, sizeof(*owned_names));
        if (
            phrases == NULL
            || owned_sources == NULL
            || owned_names == NULL
        ) {
            PyErr_NoMemory();
            goto cleanup;
        }
    }

    for (size_t index = 0; index < count; index++) {
        PyObject *pattern = PyTuple_GET_ITEM(args[0], (Py_ssize_t)index);
        int byte_mode = PyBytes_Check(pattern);
        if (!byte_mode && !PyUnicode_Check(pattern)) {
            PyErr_SetString(
                PyExc_TypeError,
                "Rust scanner expects string or bytes phrases"
            );
            goto cleanup;
        }
        Py_ssize_t length = byte_mode
            ? PyBytes_GET_SIZE(pattern)
            : PyUnicode_GET_LENGTH(pattern);
        size_t words = length == 0 ? 1 : (size_t)length;
        if (words > SIZE_MAX / sizeof(uint32_t)) {
            PyErr_NoMemory();
            goto cleanup;
        }
        owned_sources[index] = PyMem_Malloc(words * sizeof(uint32_t));
        if (owned_sources[index] == NULL) {
            PyErr_NoMemory();
            goto cleanup;
        }
        if (byte_mode) {
            const uint8_t *source =
                (const uint8_t *)PyBytes_AS_STRING(pattern);
            for (Py_ssize_t at = 0; at < length; at++) {
                owned_sources[index][at] = source[at];
            }
        } else {
            int kind = PyUnicode_KIND(pattern);
            const void *source = PyUnicode_DATA(pattern);
            for (Py_ssize_t at = 0; at < length; at++) {
                owned_sources[index][at] = PyUnicode_READ(kind, source, at);
            }
        }

        PyObject *positions =
            PyTuple_GET_ITEM(args[2], (Py_ssize_t)index);
        PyObject *values =
            PyTuple_GET_ITEM(args[3], (Py_ssize_t)index);
        if (!PyTuple_Check(positions) || !PyTuple_Check(values)) {
            PyErr_SetString(
                PyExc_TypeError,
                "Rust scanner named escapes must be tuples"
            );
            goto cleanup;
        }
        Py_ssize_t named_count = PyTuple_GET_SIZE(positions);
        if (named_count != PyTuple_GET_SIZE(values)) {
            PyErr_SetString(
                PyExc_ValueError,
                "Rust named-escape positions and values differ in length"
            );
            goto cleanup;
        }
        size_t *native_positions = NULL;
        uint32_t *native_values = NULL;
        if (named_count != 0) {
            size_t total_names = (size_t)named_count;
            if (
                total_names
                > SIZE_MAX / (sizeof(size_t) + sizeof(uint32_t))
            ) {
                PyErr_NoMemory();
                goto cleanup;
            }
            owned_names[index] = PyMem_Malloc(
                total_names * (sizeof(size_t) + sizeof(uint32_t))
            );
            if (owned_names[index] == NULL) {
                PyErr_NoMemory();
                goto cleanup;
            }
            native_positions = owned_names[index];
            native_values = (uint32_t *)(native_positions + total_names);
            for (Py_ssize_t at = 0; at < named_count; at++) {
                native_positions[at] =
                    PyLong_AsSize_t(PyTuple_GET_ITEM(positions, at));
                unsigned long value =
                    PyLong_AsUnsignedLong(PyTuple_GET_ITEM(values, at));
                if (PyErr_Occurred() || value > UINT32_MAX) {
                    if (!PyErr_Occurred()) {
                        PyErr_SetString(
                            PyExc_OverflowError,
                            "Rust named escape exceeds 32 bits"
                        );
                    }
                    goto cleanup;
                }
                native_values[at] = (uint32_t)value;
            }
        }

        phrases[index].source = owned_sources[index];
        phrases[index].length = (size_t)length;
        phrases[index].named_positions = native_positions;
        phrases[index].named_values = native_values;
        phrases[index].named_count = (size_t)named_count;
        phrases[index].byte_mode = (uint8_t)byte_mode;
    }

    size_t failed_index = SIZE_MAX;
    handle = rebar_compile_scanner(
        phrases,
        count,
        (uint32_t)flags,
        &failed_index
    );
    if (handle == NULL) {
        PyObject *index = PyLong_FromSize_t(
            failed_index < count ? failed_index : 0
        );
        if (index != NULL) {
            result = PyTuple_Pack(2, Py_None, index);
            Py_DECREF(index);
        }
        goto cleanup;
    }

    result = rust_owned_tuple4(
        PyLong_FromVoidPtr(handle),
        PyLong_FromSize_t(rebar_groups(handle)),
        PyLong_FromUnsignedLong(rebar_flags(handle)),
        PyDict_New()
    );
    if (result == NULL) {
        rebar_free(handle);
    }

cleanup:
    if (owned_sources != NULL) {
        for (size_t index = 0; index < count; index++) {
            PyMem_Free(owned_sources[index]);
        }
    }
    if (owned_names != NULL) {
        for (size_t index = 0; index < count; index++) {
            PyMem_Free(owned_names[index]);
        }
    }
    PyMem_Free(owned_sources);
    PyMem_Free(owned_names);
    PyMem_Free(phrases);
    return result;
}

static PyObject *bridge_free(PyObject *module, PyObject *value) {
    (void)module;
    void *handle = PyLong_AsVoidPtr(value);
    if (PyErr_Occurred()) return NULL;
    rebar_free(handle);
    Py_RETURN_NONE;
}

static PyObject *bridge_error(PyObject *module, PyObject *ignored) {
    (void)module;
    (void)ignored;
    size_t width = rebar_error_len();
    if (width > (size_t)PY_SSIZE_T_MAX) {
        PyErr_SetString(PyExc_OverflowError, "Rust regex error is too large");
        return NULL;
    }
    uint8_t local_message[256];
    uint8_t *message = local_message;
    if (width > sizeof(local_message)) {
        message = PyMem_Malloc(width);
        if (message == NULL) return PyErr_NoMemory();
    }
    size_t copied = rebar_error_copy(message, width);
    PyObject *text = copied == width ? PyUnicode_DecodeUTF8((const char *)message, (Py_ssize_t)width, "strict") : NULL;
    if (message != local_message) PyMem_Free(message);
    if (copied != width && !PyErr_Occurred()) PyErr_SetString(PyExc_RuntimeError, "Rust regex error copy failed");
    if (text == NULL) return NULL;
    intptr_t position = rebar_error_pos();
    PyObject *result = PyTuple_New(3);
    if (result == NULL) {
        Py_DECREF(text);
        return NULL;
    }
    PyObject *position_value = position < 0 ? Py_NewRef(Py_None) : PyLong_FromSsize_t((Py_ssize_t)position);
    PyObject *include = PyBool_FromLong(rebar_error_include() != 0);
    if (position_value == NULL || include == NULL) {
        Py_DECREF(text);
        Py_XDECREF(position_value);
        Py_XDECREF(include);
        Py_DECREF(result);
        return NULL;
    }
    PyTuple_SET_ITEM(result, 0, text);
    PyTuple_SET_ITEM(result, 1, position_value);
    PyTuple_SET_ITEM(result, 2, include);
    return result;
}

static uint32_t simple_fold(Py_UCS4 value) {
    switch (value) {
        case 0x0130: case 0x0131: return 'i';
        case 0x017f: return 's';
        case 0x212a: return 'k';
        case 0x1c80: return 0x0432;
        case 0xfb05: case 0xfb06: return 0xfb05;
        case 0x00df: case 0x1e9e: return 0x00df;
        default: return Py_UNICODE_TOLOWER(value);
    }
}

typedef struct {
    PyObject *object;
    Py_buffer view;
    const uint8_t *data;
    uint32_t *storage;
    const uint32_t *chars;
    const uint32_t *folds;
    const uint8_t *masks;
    size_t length;
    uint8_t kind;
    uint8_t text;
} RustSubject;

typedef struct {
    PyObject_HEAD
    PyObject *pattern;
    PyObject *string;
    PyObject *groupindex;
    const void *handle;
    RustSubject subject;
    size_t groups;
    size_t cursor;
    size_t end;
    size_t original;
    intptr_t local_begins[RUST_ITERATOR_CAPTURE_WORDS];
    intptr_t local_ends[RUST_ITERATOR_CAPTURE_WORDS];
    intptr_t *heap;
    uint8_t nonempty;
    uint8_t done;
} RustIterator;

static void rust_subject_release(RustSubject *subject) {
    if (subject->view.obj != NULL) PyBuffer_Release(&subject->view);
    PyMem_Free(subject->storage);
    subject->storage = NULL;
}

static int rust_index_arg(PyObject *value, Py_ssize_t *result) {
    if (PyLong_CheckExact(value)) {
        *result = PyLong_AsSsize_t(value);
        return !PyErr_Occurred();
    }
    PyObject *number = PyNumber_Index(value);
    if (number == NULL) return 0;
    *result = PyLong_AsSsize_t(number);
    Py_DECREF(number);
    return !PyErr_Occurred();
}

static int rust_subject_open(RustSubject *subject, PyObject *pattern_value, PyObject *value, int prepare) {
    memset(subject, 0, sizeof(*subject));
    subject->object = value;
    if (PyUnicode_Check(value)) {
        if (pattern_value != NULL && PyBytes_Check(pattern_value)) {
            PyErr_SetString(PyExc_TypeError, "cannot use a bytes pattern on a string-like object");
            return 0;
        }
        subject->text = 1;
        subject->kind = (uint8_t)PyUnicode_KIND(value);
        subject->length = (size_t)PyUnicode_GET_LENGTH(value);
        subject->data = (const uint8_t *)PyUnicode_DATA(value);
        if (PyUnicode_IS_ASCII(value) || !prepare || rebar_match_wide != NULL) return 1;
        if (subject->length > SIZE_MAX / (sizeof(uint32_t) * 2 + sizeof(uint8_t))) {
            PyErr_NoMemory();
            return 0;
        }
        subject->storage = PyMem_Malloc(subject->length * (sizeof(uint32_t) * 2 + sizeof(uint8_t)));
        if (subject->storage == NULL && subject->length != 0) {
            PyErr_NoMemory();
            return 0;
        }
        subject->chars = subject->storage;
        subject->folds = subject->storage + subject->length;
        subject->masks = (const uint8_t *)(subject->storage + subject->length * 2);
        for (size_t index = 0; index < subject->length; index++) {
            Py_UCS4 value_at = PyUnicode_READ(subject->kind, subject->data, (Py_ssize_t)index);
            subject->storage[index] = value_at;
            subject->storage[subject->length + index] = simple_fold(value_at);
            ((uint8_t *)subject->masks)[index] = (uint8_t)(Py_UNICODE_ISDECIMAL(value_at) | (Py_UNICODE_ISSPACE(value_at) << 1) | (Py_UNICODE_ISALNUM(value_at) << 2));
        }
        return 1;
    }
    if (PyBytes_CheckExact(value)) {
        if (pattern_value != NULL && PyUnicode_Check(pattern_value)) {
            PyErr_SetString(PyExc_TypeError, "cannot use a string pattern on a bytes-like object");
            return 0;
        }
        subject->kind = 1;
        subject->data = (const uint8_t *)PyBytes_AS_STRING(value);
        subject->length = (size_t)PyBytes_GET_SIZE(value);
        return 1;
    }
    if (PyObject_GetBuffer(value, &subject->view, PyBUF_SIMPLE) != 0) {
        PyErr_Clear();
        PyErr_Format(PyExc_TypeError, "expected string or bytes-like object, got '%.200s'", Py_TYPE(value)->tp_name);
        return 0;
    }
    if (pattern_value != NULL && PyUnicode_Check(pattern_value)) {
        PyBuffer_Release(&subject->view);
        memset(&subject->view, 0, sizeof(subject->view));
        PyErr_SetString(PyExc_TypeError, "cannot use a string pattern on a bytes-like object");
        return 0;
    }
    subject->kind = 1;
    subject->data = subject->view.buf;
    subject->length = (size_t)subject->view.len;
    return 1;
}

static int rust_subject_match(const void *handle, const RustSubject *subject, size_t pos, size_t endpos, uint8_t mode, uint8_t nonempty, intptr_t *begins, intptr_t *ends, intptr_t *last) {
    if (rebar_match_wide != NULL) {
        return rebar_match_wide(handle, subject->data, subject->length, subject->kind, pos, endpos, mode, nonempty, begins, ends, last);
    }
    if (subject->storage != NULL) {
        return rebar_match(handle, subject->chars, subject->folds, subject->masks, subject->length, pos, endpos, mode, nonempty, begins, ends, last);
    }
    return rebar_match_ascii(handle, subject->data, subject->length, pos, endpos, mode, nonempty, begins, ends, last);
}

static PyObject *rust_findall_item(const RustSubject *subject, intptr_t begin, intptr_t end) {
    if (begin < 0) {
        if (subject->text) return PyUnicode_New(0, 127);
        return PyBytes_FromStringAndSize("", 0);
    }
    if (subject->text) return PyUnicode_Substring(subject->object, (Py_ssize_t)begin, (Py_ssize_t)end);
    if (
        begin == 0
        && (size_t)end == subject->length
        && PyBytes_CheckExact(subject->object)
    ) {
        return Py_NewRef(subject->object);
    }
    return PyBytes_FromStringAndSize((const char *)subject->data + begin, (Py_ssize_t)(end - begin));
}

static int rust_list_append_owned(PyObject *list, PyObject *value) {
    if (value == NULL) return -1;
    PyListObject *items = (PyListObject *)list;
    Py_ssize_t used = PyList_GET_SIZE(list);
    if (used < items->allocated) {
        PyList_SET_ITEM(list, used, value);
        Py_SET_SIZE(list, used + 1);
        return 0;
    }
    int result = PyList_Append(list, value);
    Py_DECREF(value);
    return result;
}

static PyObject *rust_stream_collection(const void *handle, const RustSubject *subject, size_t groups, size_t pos, size_t end, int findall) {
    size_t stride = groups + 1;
    if (stride == 0 || stride > SIZE_MAX / (sizeof(intptr_t) * 2)) return PyErr_NoMemory();
    intptr_t local_begins[RUST_LOCAL_CAPTURE_WORDS];
    intptr_t local_ends[RUST_LOCAL_CAPTURE_WORDS];
    intptr_t *begins = local_begins;
    intptr_t *ends = local_ends;
    if (stride > RUST_LOCAL_CAPTURE_WORDS) {
        begins = PyMem_Malloc(stride * sizeof(intptr_t) * 2);
        if (begins == NULL) return PyErr_NoMemory();
        ends = begins + stride;
    }
    PyObject *result = PyList_New(0);
    if (result == NULL) {
        if (begins != local_begins) PyMem_Free(begins);
        return NULL;
    }
    size_t current = pos;
    uint8_t nonempty = 0;
    while (current <= end) {
        intptr_t last = -1;
        int found = rust_subject_match(handle, subject, current, end, 0, nonempty, begins, ends, &last);
        if (found < 0) {
            PyErr_SetString(PyExc_RuntimeError, "Rust continuation engine rejected the collection bridge call");
            goto stream_error;
        }
        if (found == 0) break;
        PyObject *item;
        if (findall) {
            size_t first = groups == 0 ? 0 : 1;
            size_t count = groups <= 1 ? 1 : groups;
            if (count == 1) {
                item = rust_findall_item(subject, begins[first], ends[first]);
            } else {
                item = PyTuple_New((Py_ssize_t)count);
                if (item != NULL) {
                    for (size_t index = 0; index < count; index++) {
                        PyObject *piece = rust_findall_item(subject, begins[first + index], ends[first + index]);
                        if (piece == NULL) {
                            Py_CLEAR(item);
                            break;
                        }
                        PyTuple_SET_ITEM(item, (Py_ssize_t)index, piece);
                    }
                }
            }
        } else {
            PyObject *spans = PyTuple_New((Py_ssize_t)stride);
            if (spans == NULL) goto stream_error;
            for (size_t group = 0; group < stride; group++) {
                PyObject *span = begins[group] < 0 ? Py_NewRef(Py_None) : rust_span(begins[group], ends[group]);
                if (span == NULL) {
                    Py_DECREF(spans);
                    goto stream_error;
                }
                PyTuple_SET_ITEM(spans, (Py_ssize_t)group, span);
            }
            PyObject *last_value = last < 0 ? Py_NewRef(Py_None) : PyLong_FromSsize_t((Py_ssize_t)last);
            if (last_value == NULL) {
                Py_DECREF(spans);
                goto stream_error;
            }
            item = PyTuple_New(2);
            if (item == NULL) {
                Py_DECREF(spans);
                Py_DECREF(last_value);
                goto stream_error;
            }
            PyTuple_SET_ITEM(item, 0, spans);
            PyTuple_SET_ITEM(item, 1, last_value);
        }
        if (rust_list_append_owned(result, item) != 0) goto stream_error;
        if (begins[0] == ends[0]) {
            current = (size_t)begins[0];
            nonempty = 1;
        } else {
            current = (size_t)ends[0];
            nonempty = 0;
        }
    }
    if (begins != local_begins) PyMem_Free(begins);
    return result;

stream_error:
    if (begins != local_begins) PyMem_Free(begins);
    Py_DECREF(result);
    return NULL;
}

static int rust_append_batched_findall(PyObject *result, const RustSubject *subject, size_t groups, const intptr_t *begins, const intptr_t *ends) {
    size_t first = groups == 0 ? 0 : 1;
    size_t values = groups <= 1 ? 1 : groups;
    if (values == 1) {
        return rust_list_append_owned(result, rust_findall_item(subject, begins[first], ends[first]));
    }
    if (values > (size_t)PY_SSIZE_T_MAX) {
        PyErr_NoMemory();
        return -1;
    }
    PyObject *row = PyTuple_New((Py_ssize_t)values);
    if (row == NULL) return -1;
    for (size_t index = 0; index < values; index++) {
        size_t group = first + index;
        PyObject *piece = rust_findall_item(subject, begins[group], ends[group]);
        if (piece == NULL) {
            Py_DECREF(row);
            return -1;
        }
        PyTuple_SET_ITEM(row, (Py_ssize_t)index, piece);
    }
    return rust_list_append_owned(result, row);
}

static PyObject *rust_batched_findall(const void *handle, const RustSubject *subject, size_t groups, size_t start, size_t end) {
    size_t stride = groups + 1;
    if (stride == 0 || stride > (SIZE_MAX / RUST_FINDALL_BATCH_CAPACITY - 1) / 2) {
        return PyErr_NoMemory();
    }
    size_t words = RUST_FINDALL_BATCH_CAPACITY * (stride * 2 + 1);
    if (words > SIZE_MAX / sizeof(intptr_t)) return PyErr_NoMemory();
    intptr_t local[RUST_FINDALL_BATCH_CAPACITY * (RUST_FINDALL_INLINE_STRIDE * 2 + 1)];
    intptr_t *storage = words <= sizeof(local) / sizeof(local[0])
        ? local
        : PyMem_Malloc(words * sizeof(intptr_t));
    if (storage == NULL) return PyErr_NoMemory();
    intptr_t *begins = storage;
    intptr_t *ends = begins + RUST_FINDALL_BATCH_CAPACITY * stride;
    intptr_t *lasts = ends + RUST_FINDALL_BATCH_CAPACITY * stride;
    PyObject *result = PyList_New(0);
    if (result == NULL) {
        if (storage != local) PyMem_Free(storage);
        return NULL;
    }

    size_t current = start;
    uint8_t pending_nonempty = 0;
    while (current <= end) {
        if (pending_nonempty) {
            intptr_t last = -1;
            int found = rust_subject_match(handle, subject, current, end, 1, 1, begins, ends, &last);
            if (found < 0) {
                PyErr_SetString(PyExc_RuntimeError, "Rust batched collector rejected a nonempty continuation");
                goto batch_error;
            }
            if (found > 0) {
                if (begins[0] == ends[0]) {
                    PyErr_SetString(PyExc_RuntimeError, "Rust nonempty continuation produced an empty match");
                    goto batch_error;
                }
                if (rust_append_batched_findall(result, subject, groups, begins, ends) < 0) goto batch_error;
                current = (size_t)ends[0];
            } else {
                if (current == end) break;
                current++;
            }
            pending_nonempty = 0;
            continue;
        }

        intptr_t count;
        if (subject->text) {
            if (rebar_collect_wide == NULL) {
                PyErr_SetString(PyExc_RuntimeError, "Rust batched collector requires the native wide-character entry point");
                goto batch_error;
            }
            count = rebar_collect_wide(
                handle, subject->data, subject->length, subject->kind,
                current, end, RUST_FINDALL_BATCH_CAPACITY, begins, ends, lasts
            );
        } else {
            count = rebar_collect_ascii(
                handle, subject->data, subject->length,
                current, end, RUST_FINDALL_BATCH_CAPACITY, begins, ends, lasts
            );
        }
        if (count < 0 || count > RUST_FINDALL_BATCH_CAPACITY) {
            PyErr_SetString(PyExc_RuntimeError, "Rust batched collector returned an invalid result count");
            goto batch_error;
        }
        if (count == 0) break;
        for (intptr_t match = 0; match < count; match++) {
            size_t offset = (size_t)match * stride;
            if (rust_append_batched_findall(result, subject, groups, begins + offset, ends + offset) < 0) {
                goto batch_error;
            }
        }
        size_t last_offset = (size_t)(count - 1) * stride;
        current = (size_t)ends[last_offset];
        pending_nonempty = begins[last_offset] == ends[last_offset];
        if (count < RUST_FINDALL_BATCH_CAPACITY) break;
    }

    if (storage != local) PyMem_Free(storage);
    return result;

batch_error:
    if (storage != local) PyMem_Free(storage);
    Py_DECREF(result);
    return NULL;
}

static PyObject *bridge_run(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 7) {
        PyErr_Format(PyExc_TypeError, "run() takes exactly 7 arguments (%zd given)", nargs);
        return NULL;
    }
    void *handle = PyLong_AsVoidPtr(args[0]);
    size_t groups = PyLong_AsSize_t(args[2]);
    size_t pos = PyLong_AsSize_t(args[3]);
    size_t endpos = PyLong_AsSize_t(args[4]);
    unsigned long mode = PyLong_AsUnsignedLong(args[5]);
    int nonempty = PyObject_IsTrue(args[6]);
    if (PyErr_Occurred() || nonempty < 0 || groups == SIZE_MAX || mode > UINT8_MAX) {
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_OverflowError, "invalid Rust regex bridge argument");
        return NULL;
    }
    size_t stride = groups + 1;
    intptr_t local_begins[64];
    intptr_t local_ends[64];
    intptr_t *begins = local_begins;
    intptr_t *ends = local_ends;
    if (stride > 64) {
        if (stride > SIZE_MAX / (sizeof(intptr_t) * 2)) return PyErr_NoMemory();
        begins = PyMem_Malloc(stride * sizeof(intptr_t) * 2);
        if (begins == NULL) return PyErr_NoMemory();
        ends = begins + stride;
    }

    PyObject *subject = args[1];
    Py_buffer view = {0};
    uint32_t *storage = NULL;
    intptr_t last = -1;
    int matched = -1;
    if (PyUnicode_Check(subject)) {
        Py_ssize_t count = PyUnicode_GET_LENGTH(subject);
        if (count < 0) goto done;
        if (rebar_match_wide != NULL) {
            matched = rebar_match_wide(handle, (const uint8_t *)PyUnicode_DATA(subject), (size_t)count, (uint8_t)PyUnicode_KIND(subject), pos, endpos, (uint8_t)mode, (uint8_t)nonempty, begins, ends, &last);
        } else if (PyUnicode_IS_ASCII(subject)) {
            matched = rebar_match_ascii(handle, PyUnicode_1BYTE_DATA(subject), (size_t)count, pos, endpos, (uint8_t)mode, (uint8_t)nonempty, begins, ends, &last);
        } else {
            if ((size_t)count > SIZE_MAX / (sizeof(uint32_t) * 2 + sizeof(uint8_t))) {
                PyErr_NoMemory();
                goto done;
            }
            size_t length = (size_t)count;
            storage = PyMem_Malloc(length * (sizeof(uint32_t) * 2 + sizeof(uint8_t)));
            if (storage == NULL && length != 0) {
                PyErr_NoMemory();
                goto done;
            }
            uint32_t *chars = storage;
            uint32_t *folds = chars + length;
            uint8_t *masks = (uint8_t *)(folds + length);
            int kind = PyUnicode_KIND(subject);
            const void *data = PyUnicode_DATA(subject);
            for (size_t index = 0; index < length; index++) {
                Py_UCS4 value = PyUnicode_READ(kind, data, (Py_ssize_t)index);
                chars[index] = value;
                folds[index] = simple_fold(value);
                masks[index] = (uint8_t)(Py_UNICODE_ISDECIMAL(value) | (Py_UNICODE_ISSPACE(value) << 1) | (Py_UNICODE_ISALNUM(value) << 2));
            }
            matched = rebar_match(handle, chars, folds, masks, length, pos, endpos, (uint8_t)mode, (uint8_t)nonempty, begins, ends, &last);
        }
    } else {
        if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) goto done;
        if (rebar_match_wide != NULL) matched = rebar_match_wide(handle, view.buf, (size_t)view.len, 1, pos, endpos, (uint8_t)mode, (uint8_t)nonempty, begins, ends, &last);
        else matched = rebar_match_ascii(handle, view.buf, (size_t)view.len, pos, endpos, (uint8_t)mode, (uint8_t)nonempty, begins, ends, &last);
    }

done:
    if (view.obj != NULL) PyBuffer_Release(&view);
    PyMem_Free(storage);
    if (matched < 0) {
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_RuntimeError, "Rust continuation engine rejected the bridge call");
        if (begins != local_begins) PyMem_Free(begins);
        return NULL;
    }
    if (matched == 0) {
        if (begins != local_begins) PyMem_Free(begins);
        Py_RETURN_NONE;
    }
    PyObject *spans = PyTuple_New((Py_ssize_t)stride);
    if (spans == NULL) {
        if (begins != local_begins) PyMem_Free(begins);
        return NULL;
    }
    for (size_t index = 0; index < stride; index++) {
        PyObject *item;
        if (begins[index] < 0) {
            item = Py_NewRef(Py_None);
        } else {
            item = rust_span(begins[index], ends[index]);
            if (item == NULL) {
                Py_DECREF(spans);
                if (begins != local_begins) PyMem_Free(begins);
                return NULL;
            }
        }
        PyTuple_SET_ITEM(spans, (Py_ssize_t)index, item);
    }
    if (begins != local_begins) PyMem_Free(begins);
    PyObject *last_value = last < 0 ? Py_NewRef(Py_None) : PyLong_FromSsize_t((Py_ssize_t)last);
    if (last_value == NULL) {
        Py_DECREF(spans);
        return NULL;
    }
    PyObject *result = PyTuple_New(2);
    if (result == NULL) {
        Py_DECREF(spans);
        Py_DECREF(last_value);
        return NULL;
    }
    PyTuple_SET_ITEM(result, 0, spans);
    PyTuple_SET_ITEM(result, 1, last_value);
    return result;
}

static PyObject *bridge_collect(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 5) {
        PyErr_Format(PyExc_TypeError, "collect() takes exactly 5 arguments (%zd given)", nargs);
        return NULL;
    }
    void *handle = PyLong_AsVoidPtr(args[0]);
    size_t groups = PyLong_AsSize_t(args[2]);
    size_t pos = PyLong_AsSize_t(args[3]);
    size_t endpos = PyLong_AsSize_t(args[4]);
    if (PyErr_Occurred() || groups == SIZE_MAX || endpos < pos) {
        if (endpos < pos && !PyErr_Occurred()) return PyList_New(0);
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_OverflowError, "invalid Rust regex collection argument");
        return NULL;
    }
    PyObject *subject = args[1];
    if (PyUnicode_Check(subject) && !PyUnicode_IS_ASCII(subject)) {
        RustSubject prepared;
        if (!rust_subject_open(&prepared, NULL, subject, 1)) return NULL;
        size_t end = endpos < prepared.length ? endpos : prepared.length;
        PyObject *records = pos > end ? PyList_New(0) : rust_stream_collection(handle, &prepared, groups, pos, end, 0);
        rust_subject_release(&prepared);
        return records;
    }
    Py_buffer view = {0};
    const uint8_t *data;
    size_t length;
    if (PyUnicode_Check(subject)) {
        if (!PyUnicode_IS_ASCII(subject)) Py_RETURN_NONE;
        data = PyUnicode_1BYTE_DATA(subject);
        length = (size_t)PyUnicode_GET_LENGTH(subject);
    } else {
        if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) return NULL;
        data = view.buf;
        length = (size_t)view.len;
    }
    size_t end = endpos < length ? endpos : length;
    size_t range = end >= pos ? end - pos : 0;
    if (range > (SIZE_MAX - 1) / 2) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        return PyErr_NoMemory();
    }
    size_t capacity = range * 2 + 1;
    size_t stride = groups + 1;
    if (capacity > SIZE_MAX / stride || capacity * stride > (SIZE_MAX / sizeof(intptr_t) - capacity) / 2) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        return PyErr_NoMemory();
    }
    size_t total = capacity * stride;
    intptr_t *storage = PyMem_Malloc((total * 2 + capacity) * sizeof(intptr_t));
    if (storage == NULL) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        return PyErr_NoMemory();
    }
    intptr_t *begins = storage;
    intptr_t *ends = begins + total;
    intptr_t *lasts = ends + total;
    intptr_t count = rebar_collect_ascii(handle, data, length, pos, end, capacity, begins, ends, lasts);
    if (view.obj != NULL) PyBuffer_Release(&view);
    if (count < 0) {
        PyMem_Free(storage);
        PyErr_SetString(PyExc_RuntimeError, "Rust continuation engine rejected the collection bridge call");
        return NULL;
    }
    PyObject *records = PyList_New((Py_ssize_t)count);
    if (records == NULL) {
        PyMem_Free(storage);
        return NULL;
    }
    for (intptr_t match = 0; match < count; match++) {
        PyObject *spans = PyTuple_New((Py_ssize_t)stride);
        if (spans == NULL) goto collect_error;
        size_t base = (size_t)match * stride;
        for (size_t group = 0; group < stride; group++) {
            PyObject *item;
            if (begins[base + group] < 0) item = Py_NewRef(Py_None);
            else item = rust_span(begins[base + group], ends[base + group]);
            if (item == NULL) {
                Py_DECREF(spans);
                goto collect_error;
            }
            PyTuple_SET_ITEM(spans, (Py_ssize_t)group, item);
        }
        PyObject *last = lasts[match] < 0 ? Py_NewRef(Py_None) : PyLong_FromSsize_t((Py_ssize_t)lasts[match]);
        if (last == NULL) {
            Py_DECREF(spans);
            goto collect_error;
        }
        PyObject *record = PyTuple_New(2);
        if (record == NULL) {
            Py_DECREF(spans);
            Py_DECREF(last);
            goto collect_error;
        }
        PyTuple_SET_ITEM(record, 0, spans);
        PyTuple_SET_ITEM(record, 1, last);
        PyList_SET_ITEM(records, (Py_ssize_t)match, record);
    }
    PyMem_Free(storage);
    return records;

collect_error:
    Py_DECREF(records);
    PyMem_Free(storage);
    return NULL;
}

static PyObject *bridge_findall(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 5) {
        PyErr_Format(PyExc_TypeError, "findall() takes exactly 5 arguments (%zd given)", nargs);
        return NULL;
    }
    void *handle = PyLong_AsVoidPtr(args[0]);
    size_t groups = PyLong_AsSize_t(args[2]);
    size_t pos = PyLong_AsSize_t(args[3]);
    size_t endpos = PyLong_AsSize_t(args[4]);
    if (PyErr_Occurred() || groups == SIZE_MAX || endpos < pos) {
        if (endpos < pos && !PyErr_Occurred()) return PyList_New(0);
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_OverflowError, "invalid Rust regex findall argument");
        return NULL;
    }
    PyObject *subject = args[1];
    if (PyUnicode_Check(subject) && !PyUnicode_IS_ASCII(subject)) {
        RustSubject prepared;
        if (!rust_subject_open(&prepared, NULL, subject, 1)) return NULL;
        size_t end = endpos < prepared.length ? endpos : prepared.length;
        PyObject *result = pos > end ? PyList_New(0) : rust_stream_collection(handle, &prepared, groups, pos, end, 1);
        rust_subject_release(&prepared);
        return result;
    }
    Py_buffer view = {0};
    const uint8_t *data;
    size_t length;
    int text_mode = PyUnicode_Check(subject);
    if (text_mode) {
        if (!PyUnicode_IS_ASCII(subject)) Py_RETURN_NONE;
        data = PyUnicode_1BYTE_DATA(subject);
        length = (size_t)PyUnicode_GET_LENGTH(subject);
    } else {
        if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) return NULL;
        data = view.buf;
        length = (size_t)view.len;
    }
    size_t end = endpos < length ? endpos : length;
    size_t range = end >= pos ? end - pos : 0;
    if (range > (SIZE_MAX - 1) / 2) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        return PyErr_NoMemory();
    }
    size_t capacity = range * 2 + 1;
    size_t stride = groups + 1;
    if (capacity > SIZE_MAX / stride || capacity * stride > (SIZE_MAX / sizeof(intptr_t) - capacity) / 2) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        return PyErr_NoMemory();
    }
    size_t total = capacity * stride;
    intptr_t *storage = PyMem_Malloc((total * 2 + capacity) * sizeof(intptr_t));
    if (storage == NULL) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        return PyErr_NoMemory();
    }
    intptr_t *begins = storage;
    intptr_t *ends = begins + total;
    intptr_t *lasts = ends + total;
    intptr_t count = rebar_collect_ascii(handle, data, length, pos, end, capacity, begins, ends, lasts);
    if (count < 0) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        PyMem_Free(storage);
        PyErr_SetString(PyExc_RuntimeError, "Rust continuation engine rejected the findall bridge call");
        return NULL;
    }
    PyObject *result = PyList_New((Py_ssize_t)count);
    if (result == NULL) goto findall_error;
    for (intptr_t match = 0; match < count; match++) {
        size_t base = (size_t)match * stride;
        size_t first = groups == 0 ? 0 : 1;
        size_t values = groups <= 1 ? 1 : groups;
        PyObject *row = values == 1 ? NULL : PyTuple_New((Py_ssize_t)values);
        if (values != 1 && row == NULL) goto findall_error;
        for (size_t index = 0; index < values; index++) {
            size_t group = first + index;
            intptr_t begin = begins[base + group];
            intptr_t finish = ends[base + group];
            PyObject *item;
            if (begin < 0) {
                item = text_mode ? PyUnicode_New(0, 127) : PyBytes_FromStringAndSize("", 0);
            } else if (text_mode) {
                item = PyUnicode_Substring(subject, (Py_ssize_t)begin, (Py_ssize_t)finish);
            } else if (
                begin == 0
                && (size_t)finish == length
                && PyBytes_CheckExact(subject)
            ) {
                item = Py_NewRef(subject);
            } else {
                item = PyBytes_FromStringAndSize((const char *)data + begin, (Py_ssize_t)(finish - begin));
            }
            if (item == NULL) {
                Py_XDECREF(row);
                goto findall_error;
            }
            if (values == 1) {
                row = item;
            } else {
                PyTuple_SET_ITEM(row, (Py_ssize_t)index, item);
            }
        }
        PyList_SET_ITEM(result, (Py_ssize_t)match, row);
    }
    if (view.obj != NULL) PyBuffer_Release(&view);
    PyMem_Free(storage);
    return result;

findall_error:
    if (view.obj != NULL) PyBuffer_Release(&view);
    PyMem_Free(storage);
    Py_XDECREF(result);
    return NULL;
}

static int rust_window_indices(
    PyObject *pos_value,
    PyObject *end_value,
    Py_ssize_t *requested_pos,
    Py_ssize_t *requested_end
) {
    *requested_pos = 0;
    *requested_end = PY_SSIZE_T_MAX;
    if (pos_value != NULL && !rust_index_arg(pos_value, requested_pos)) return 0;
    if (end_value != NULL && !rust_index_arg(end_value, requested_end)) return 0;
    return 1;
}

static void rust_subject_clamp_window(
    const RustSubject *subject,
    Py_ssize_t requested_pos,
    Py_ssize_t requested_end,
    size_t *start,
    size_t *end
) {
    if (requested_pos < 0) requested_pos = 0;
    if ((size_t)requested_pos > subject->length) requested_pos = (Py_ssize_t)subject->length;
    if (requested_end < 0) requested_end = 0;
    if ((size_t)requested_end > subject->length) requested_end = (Py_ssize_t)subject->length;
    *start = (size_t)requested_pos;
    *end = (size_t)requested_end;
}

static PyObject *rust_pattern_direct(PyObject *pattern, void *handle, PyObject *groupindex, PyObject *pattern_value, PyObject *literal, PyObject *value, PyObject *pos_value, PyObject *end_value, uint8_t mode) {
    Py_ssize_t requested_pos;
    Py_ssize_t requested_end;
    if (!rust_window_indices(pos_value, end_value, &requested_pos, &requested_end)) return NULL;
    RustSubject subject;
    if (!rust_subject_open(&subject, pattern_value, value, literal == NULL || literal == Py_None)) return NULL;
    size_t start;
    size_t end;
    rust_subject_clamp_window(&subject, requested_pos, requested_end, &start, &end);
    if (start > end && mode != 1) {
        rust_subject_release(&subject);
        Py_RETURN_NONE;
    }
    size_t groups = rebar_groups(handle);
    size_t stride = groups + 1;
    if (stride == 0 || stride > SIZE_MAX / (sizeof(intptr_t) * 2)) {
        rust_subject_release(&subject);
        return PyErr_NoMemory();
    }
    intptr_t local_begins[RUST_LOCAL_CAPTURE_WORDS];
    intptr_t local_ends[RUST_LOCAL_CAPTURE_WORDS];
    intptr_t *begins = local_begins;
    intptr_t *ends = local_ends;
    if (stride > RUST_LOCAL_CAPTURE_WORDS) {
        begins = PyMem_Malloc(stride * sizeof(intptr_t) * 2);
        if (begins == NULL) {
            rust_subject_release(&subject);
            return PyErr_NoMemory();
        }
        ends = begins + stride;
    }
    intptr_t last = -1;
    int found = 0;
    if (literal != NULL && literal != Py_None && groups == 0) {
        Py_ssize_t width = subject.text ? PyUnicode_GET_LENGTH(literal) : PyBytes_GET_SIZE(literal);
        Py_ssize_t at = -1;
        if (start <= end && width <= (Py_ssize_t)(end - start)) {
            if (mode == 0) {
                if (subject.text) {
                    at = PyUnicode_Find(value, literal, (Py_ssize_t)start, (Py_ssize_t)end, 1);
                    if (at == -2) found = -1;
                } else {
                    const uint8_t *needle = (const uint8_t *)PyBytes_AS_STRING(literal);
                    const uint8_t *hit = memmem(subject.data + start, end - start, needle, (size_t)width);
                    if (hit != NULL) at = (Py_ssize_t)(hit - subject.data);
                }
            } else if (mode != 2 || (size_t)width == end - start) {
                if (subject.text) {
                    Py_ssize_t equal = PyUnicode_Tailmatch(value, literal, (Py_ssize_t)start, (Py_ssize_t)end, -1);
                    if (equal < 0) found = -1;
                    else if (equal) at = (Py_ssize_t)start;
                } else if (memcmp(subject.data + start, PyBytes_AS_STRING(literal), (size_t)width) == 0) {
                    at = (Py_ssize_t)start;
                }
            }
        }
        if (found >= 0 && at >= 0) {
            begins[0] = at;
            ends[0] = at + width;
            found = 1;
        }
    } else {
        found = rust_subject_match(handle, &subject, start, end, mode, 0, begins, ends, &last);
    }
    if (found < 0) {
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_RuntimeError, "Rust continuation engine rejected the native pattern call");
        if (begins != local_begins) PyMem_Free(begins);
        rust_subject_release(&subject);
        return NULL;
    }
    if (found == 0) {
        if (begins != local_begins) PyMem_Free(begins);
        rust_subject_release(&subject);
        Py_RETURN_NONE;
    }
    RustMatch *result = rust_match_allocate(pattern, value, groupindex, groups, (Py_ssize_t)start, (Py_ssize_t)end);
    if (result != NULL) {
        memcpy(result->spans, begins, stride * sizeof(intptr_t));
        memcpy(result->spans + stride, ends, stride * sizeof(intptr_t));
        result->lastindex = last;
    }
    if (begins != local_begins) PyMem_Free(begins);
    rust_subject_release(&subject);
    return (PyObject *)result;
}

static PyObject *bridge_pattern_match(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 9) {
        PyErr_Format(PyExc_TypeError, "pattern_match() takes exactly 9 arguments (%zd given)", nargs);
        return NULL;
    }
    void *handle = PyLong_AsVoidPtr(args[1]);
    unsigned long mode = PyLong_AsUnsignedLong(args[8]);
    if (PyErr_Occurred() || mode > 2) {
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_ValueError, "Rust regex match mode must be search, match, or fullmatch");
        return NULL;
    }
    return rust_pattern_direct(args[0], handle, args[2], args[3], args[4], args[5], args[6], args[7], (uint8_t)mode);
}

static int rust_bound_window(PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames, Py_ssize_t prefix, const char *method, PyObject **subject, PyObject **pos, PyObject **endpos) {
    Py_ssize_t count = kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    if (nargs < prefix || nargs - prefix + count > 3) {
        PyErr_Format(PyExc_TypeError, "%s() takes at most 3 arguments (%zd given)", method, nargs < prefix ? 0 : nargs - prefix + count);
        return 0;
    }
    *subject = nargs > prefix ? args[prefix] : NULL;
    *pos = nargs > prefix + 1 ? args[prefix + 1] : NULL;
    *endpos = nargs > prefix + 2 ? args[prefix + 2] : NULL;
    if (*subject == NULL) {
        int supplied = 0;
        for (Py_ssize_t index = 0; index < count; index++) {
            int equal = PyUnicode_CompareWithASCIIString(PyTuple_GET_ITEM(kwnames, index), "string");
            if (equal == 0) {
                supplied = 1;
                break;
            }
            if (equal == -1 && PyErr_Occurred()) return 0;
        }
        if (!supplied) {
            PyErr_Format(PyExc_TypeError, "%s() missing required argument 'string' (pos 1)", method);
            return 0;
        }
    }
    for (Py_ssize_t index = 0; index < count; index++) {
        PyObject *name = PyTuple_GET_ITEM(kwnames, index);
        if (PyUnicode_CompareWithASCIIString(name, "string") == 0) {
            if (*subject != NULL) {
                PyErr_Format(PyExc_TypeError, "argument for %s() given by name ('string') and position (1)", method);
                return 0;
            }
            *subject = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "pos") == 0) {
            if (*pos != NULL) {
                PyErr_Format(PyExc_TypeError, "argument for %s() given by name ('pos') and position (2)", method);
                return 0;
            }
            *pos = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "endpos") == 0) {
            if (*endpos != NULL) {
                PyErr_Format(PyExc_TypeError, "argument for %s() given by name ('endpos') and position (3)", method);
                return 0;
            }
            *endpos = args[nargs + index];
        } else {
            if (!PyErr_Occurred()) PyErr_Format(PyExc_TypeError, "%s() got an unexpected keyword argument '%U'", method, name);
            return 0;
        }
    }
    if (*subject == NULL) {
        PyErr_Format(PyExc_TypeError, "%s() missing required argument 'string' (pos 1)", method);
        return 0;
    }
    return 1;
}

static PyObject *rust_bound_pattern(PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames, const char *method, uint8_t mode) {
    PyObject *subject;
    PyObject *pos;
    PyObject *endpos;
    if (!rust_bound_window(args, nargs, kwnames, 5, method, &subject, &pos, &endpos)) return NULL;
    void *handle = PyLong_AsVoidPtr(args[1]);
    if (PyErr_Occurred()) return NULL;
    return rust_pattern_direct(args[0], handle, args[2], args[3], args[4], subject, pos, endpos, mode);
}

static PyObject *bridge_bound_search(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    (void)module;
    return rust_bound_pattern(args, nargs, kwnames, "search", 0);
}

static PyObject *bridge_bound_match(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    (void)module;
    return rust_bound_pattern(args, nargs, kwnames, "match", 1);
}

static PyObject *bridge_bound_fullmatch(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    (void)module;
    return rust_bound_pattern(args, nargs, kwnames, "fullmatch", 2);
}

static PyObject *rust_pattern_findall_direct(
    PyObject *handle_value,
    PyObject *pattern_value,
    PyObject *groups_value,
    PyObject *value,
    PyObject *pos,
    PyObject *endpos
) {
    void *handle = PyLong_AsVoidPtr(handle_value);
    size_t groups = PyLong_AsSize_t(groups_value);
    if (PyErr_Occurred()) return NULL;
    if (groups != rebar_groups(handle)) {
        PyErr_SetString(PyExc_ValueError, "Rust regex group count does not match the compiled program");
        return NULL;
    }
    Py_ssize_t requested_pos;
    Py_ssize_t requested_end;
    if (!rust_window_indices(pos, endpos, &requested_pos, &requested_end)) return NULL;
    RustSubject subject;
    if (!rust_subject_open(&subject, pattern_value, value, 1)) return NULL;
    size_t start;
    size_t end;
    rust_subject_clamp_window(&subject, requested_pos, requested_end, &start, &end);
    PyObject *result = start > end
        ? PyList_New(0)
        : rust_batched_findall(handle, &subject, groups, start, end);
    rust_subject_release(&subject);
    return result;
}

static PyObject *bridge_bound_findall(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    (void)module;
    PyObject *value;
    PyObject *pos;
    PyObject *endpos;
    if (!rust_bound_window(args, nargs, kwnames, 3, "findall", &value, &pos, &endpos)) return NULL;
    return rust_pattern_findall_direct(args[0], args[1], args[2], value, pos, endpos);
}

static PyObject *rust_pattern_literal_findall_direct(
    PyObject *literal,
    PyObject *value,
    PyObject *pos,
    PyObject *endpos
) {
    Py_ssize_t requested_pos;
    Py_ssize_t requested_end;
    if (!rust_window_indices(pos, endpos, &requested_pos, &requested_end)) return NULL;
    RustSubject subject;
    if (!rust_subject_open(&subject, literal, value, 0)) return NULL;
    size_t start;
    size_t end;
    rust_subject_clamp_window(&subject, requested_pos, requested_end, &start, &end);
    if (start > end) {
        rust_subject_release(&subject);
        return PyList_New(0);
    }
    size_t width = subject.text ? (size_t)PyUnicode_GET_LENGTH(literal) : (size_t)PyBytes_GET_SIZE(literal);
    if (width == 0) {
        rust_subject_release(&subject);
        return PyList_New(0);
    }
    PyObject *result = PyList_New(0);
    if (result == NULL) {
        rust_subject_release(&subject);
        return NULL;
    }
    const uint8_t *needle = subject.text
        ? NULL
        : (const uint8_t *)PyBytes_AS_STRING(literal);
    Py_UCS4 character = subject.text && width == 1
        ? PyUnicode_READ_CHAR(literal, 0)
        : 0;
    size_t cursor = start;
    while (cursor <= end && width <= end - cursor) {
        size_t begin;
        if (subject.text) {
            Py_ssize_t hit = width == 1
                ? PyUnicode_FindChar(value, character, (Py_ssize_t)cursor, (Py_ssize_t)end, 1)
                : PyUnicode_Find(value, literal, (Py_ssize_t)cursor, (Py_ssize_t)end, 1);
            if (hit < 0) {
                if (PyErr_Occurred()) {
                    Py_DECREF(result);
                    rust_subject_release(&subject);
                    return NULL;
                }
                break;
            }
            begin = (size_t)hit;
        } else {
            const uint8_t *hit = memmem(
                subject.data + cursor, end - cursor, needle, width
            );
            if (hit == NULL) break;
            begin = (size_t)(hit - subject.data);
        }
        size_t finish = begin + width;
        if (
            rust_list_append_owned(
                result,
                rust_findall_item(&subject, (intptr_t)begin, (intptr_t)finish)
            ) != 0
        ) {
            Py_DECREF(result);
            rust_subject_release(&subject);
            return NULL;
        }
        cursor = finish;
    }
    rust_subject_release(&subject);
    return result;
}

static PyObject *bridge_bound_literal_findall(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    (void)module;
    PyObject *value;
    PyObject *pos;
    PyObject *endpos;
    if (!rust_bound_window(args, nargs, kwnames, 1, "findall", &value, &pos, &endpos)) return NULL;
    return rust_pattern_literal_findall_direct(args[0], value, pos, endpos);
}

static int rust_iterator_traverse(RustIterator *iterator, visitproc visit, void *arg) {
    RustBridgeState *state = rust_bridge_state_from_type(Py_TYPE(iterator));
    if (state == NULL) return -1;
    Py_VISIT(Py_TYPE(iterator));
    if (Py_TYPE(iterator) != state->scanner_type) Py_VISIT(iterator->string);
    Py_VISIT(iterator->pattern);
    Py_VISIT(iterator->groupindex);
    return 0;
}

static int rust_iterator_clear(RustIterator *iterator) {
    rust_subject_release(&iterator->subject);
    PyMem_Free(iterator->heap);
    iterator->heap = NULL;
    iterator->done = 1;
    iterator->subject.object = NULL;
    Py_CLEAR(iterator->string);
    Py_CLEAR(iterator->pattern);
    Py_CLEAR(iterator->groupindex);
    return 0;
}

static void rust_iterator_dealloc(RustIterator *iterator) {
    PyTypeObject *type = Py_TYPE(iterator);
    PyObject_GC_UnTrack(iterator);
    rust_iterator_clear(iterator);
    type->tp_free((PyObject *)iterator);
    Py_DECREF(type);
}

static PyObject *rust_iterator_get_pattern(RustIterator *iterator, void *closure) {
    (void)closure;
    return Py_NewRef(iterator->pattern);
}

static PyObject *rust_iterator_take(RustIterator *iterator, uint8_t mode) {
    if (iterator->done || (iterator->cursor > iterator->end && mode != 1)) {
        iterator->done = 1;
        return NULL;
    }
    size_t stride = iterator->groups + 1;
    intptr_t *begins = iterator->heap == NULL ? iterator->local_begins : iterator->heap;
    intptr_t *ends = iterator->heap == NULL ? iterator->local_ends : iterator->heap + stride;
    intptr_t last = -1;
    int found = rust_subject_match(iterator->handle, &iterator->subject, iterator->cursor, iterator->end, mode, iterator->nonempty, begins, ends, &last);
    if (found < 0) {
        iterator->done = 1;
        PyErr_SetString(PyExc_RuntimeError, "Rust continuation engine rejected the native iterator call");
        return NULL;
    }
    if (found == 0) {
        iterator->done = 1;
        return NULL;
    }
    RustMatch *result = rust_match_allocate(iterator->pattern, iterator->string, iterator->groupindex, iterator->groups, (Py_ssize_t)iterator->original, (Py_ssize_t)iterator->end);
    if (result == NULL) return NULL;
    memcpy(result->spans, begins, stride * sizeof(intptr_t));
    memcpy(result->spans + stride, ends, stride * sizeof(intptr_t));
    result->lastindex = last;
    if (begins[0] == ends[0]) {
        iterator->cursor = (size_t)begins[0];
        iterator->nonempty = 1;
    } else {
        iterator->cursor = (size_t)ends[0];
        iterator->nonempty = 0;
    }
    return (PyObject *)result;
}

static PyObject *rust_iterator_next(PyObject *value) {
    return rust_iterator_take((RustIterator *)value, 0);
}

static PyObject *rust_scanner_search(RustIterator *iterator, PyObject *ignored) {
    (void)ignored;
    PyObject *match = rust_iterator_take(iterator, 0);
    if (match == NULL && !PyErr_Occurred()) Py_RETURN_NONE;
    return match;
}

static PyObject *rust_scanner_match(RustIterator *iterator, PyObject *ignored) {
    (void)ignored;
    PyObject *match = rust_iterator_take(iterator, 1);
    if (match == NULL && !PyErr_Occurred()) Py_RETURN_NONE;
    return match;
}

static PyObject *rust_iterator_scanner_search(
    PyObject *value,
    PyTypeObject *defining_class,
    PyObject *const *args,
    Py_ssize_t nargs,
    PyObject *kwnames
) {
    (void)defining_class;
    (void)args;
    Py_ssize_t keywords = kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    if (nargs != 0 || keywords != 0) {
        return PyErr_Format(
            PyExc_TypeError,
            "search() takes no arguments (%zd given)",
            nargs + keywords
        );
    }
    return rust_scanner_search((RustIterator *)value, NULL);
}

static PyMethodDef rust_iterator_scanner_search_method = {
    "search",
    _PyCFunction_CAST(rust_iterator_scanner_search),
    METH_METHOD | METH_FASTCALL | METH_KEYWORDS,
    "Search for the next regular-expression match.",
};

static PyObject *rust_scanner_reduce(RustIterator *iterator, PyObject *ignored) {
    (void)ignored;
    return rust_owned_pickle_reconstruction((PyObject *)iterator);
}

static PyObject *rust_scanner_reduce_ex(RustIterator *iterator, PyObject *protocol) {
    (void)protocol;
    return PyErr_Format(
        PyExc_TypeError,
        "cannot pickle '%.200s' object",
        Py_TYPE(iterator)->tp_name
    );
}

static PyMethodDef rust_scanner_methods[] = {
    {"search", (PyCFunction)rust_scanner_search, METH_NOARGS, "Search for the next regular-expression match."},
    {"match", (PyCFunction)rust_scanner_match, METH_NOARGS, "Match at the scanner's current position."},
    {"__reduce__", (PyCFunction)rust_scanner_reduce, METH_NOARGS, "Return the generic scanner reconstruction protocol."},
    {"__reduce_ex__", (PyCFunction)rust_scanner_reduce_ex, METH_O, "Scanners cannot be pickled."},
    {NULL, NULL, 0, NULL},
};

static PyGetSetDef rust_iterator_getsets[] = {
    {"pattern", (getter)rust_iterator_get_pattern, NULL, "Compiled Rust regular expression.", NULL},
    {NULL, NULL, NULL, NULL, NULL},
};

static PyType_Slot rust_iterator_slots[] = {
    {Py_tp_dealloc, (void *)rust_iterator_dealloc},
    {Py_tp_doc, "Lazy, borrowed-subject Rust regular-expression match iterator."},
    {Py_tp_iter, (void *)PyObject_SelfIter},
    {Py_tp_iternext, (void *)rust_iterator_next},
    {Py_tp_getset, rust_iterator_getsets},
    {Py_tp_traverse, (void *)rust_iterator_traverse},
    {Py_tp_clear, (void *)rust_iterator_clear},
    {0, NULL},
};

static PyType_Spec rust_iterator_spec = {
    .name = "re._RustMatchIterator",
    .basicsize = (int)sizeof(RustIterator),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = rust_iterator_slots,
};

static PyType_Slot rust_scanner_slots[] = {
    {Py_tp_dealloc, (void *)rust_iterator_dealloc},
    {Py_tp_doc, "Borrowed-subject Rust regular-expression scanner."},
    {Py_tp_methods, rust_scanner_methods},
    {Py_tp_getset, rust_iterator_getsets},
    {Py_tp_traverse, (void *)rust_iterator_traverse},
    {Py_tp_clear, (void *)rust_iterator_clear},
    {0, NULL},
};

static PyType_Spec rust_scanner_spec = {
    .name = "_sre.SRE_Scanner",
    .basicsize = (int)sizeof(RustIterator),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = rust_scanner_slots,
};

static PyObject *rust_iterator_create(PyTypeObject *type, PyObject *pattern, void *handle, PyObject *groupindex, PyObject *pattern_value, size_t groups, PyObject *value, PyObject *pos, PyObject *endpos) {
    if (groups != rebar_groups(handle)) {
        PyErr_SetString(PyExc_ValueError, "Rust regex group count does not match the compiled program");
        return NULL;
    }
    Py_ssize_t requested_pos;
    Py_ssize_t requested_end;
    if (!rust_window_indices(pos, endpos, &requested_pos, &requested_end)) return NULL;
    RustIterator *iterator = (RustIterator *)PyType_GenericAlloc(type, 0);
    if (iterator == NULL) return NULL;
    iterator->pattern = Py_NewRef(pattern);
    iterator->string = Py_NewRef(value);
    iterator->groupindex = Py_NewRef(groupindex);
    iterator->handle = handle;
    iterator->groups = groups;
    if (!rust_subject_open(&iterator->subject, pattern_value, value, 1)) {
        Py_DECREF(iterator);
        return NULL;
    }
    rust_subject_clamp_window(
        &iterator->subject,
        requested_pos,
        requested_end,
        &iterator->cursor,
        &iterator->end
    );
    iterator->original = iterator->cursor;
    if (groups + 1 > RUST_ITERATOR_CAPTURE_WORDS) {
        size_t stride = groups + 1;
        if (stride == 0 || stride > SIZE_MAX / (sizeof(intptr_t) * 2)) {
            Py_DECREF(iterator);
            return PyErr_NoMemory();
        }
        iterator->heap = PyMem_Malloc(stride * sizeof(intptr_t) * 2);
        if (iterator->heap == NULL) {
            Py_DECREF(iterator);
            return PyErr_NoMemory();
        }
    }
    return (PyObject *)iterator;
}

static PyObject *rust_bound_iterator(PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames, const char *method, PyTypeObject *type) {
    PyObject *subject;
    PyObject *pos;
    PyObject *endpos;
    if (!rust_bound_window(args, nargs, kwnames, 5, method, &subject, &pos, &endpos)) return NULL;
    void *handle = PyLong_AsVoidPtr(args[1]);
    size_t groups = PyLong_AsSize_t(args[4]);
    if (PyErr_Occurred()) return NULL;
    return rust_iterator_create(type, args[0], handle, args[2], args[3], groups, subject, pos, endpos);
}

static PyObject *bridge_bound_finditer(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    RustBridgeState *state = module == NULL
        ? (nargs > 0 ? rust_bridge_state_from_type(Py_TYPE(args[0])) : NULL)
        : rust_bridge_state_from_module(module);
    if (state == NULL) {
        if (!PyErr_Occurred()) {
            PyErr_SetString(PyExc_SystemError, "Rust iterator has no owning bridge state");
        }
        return NULL;
    }
    PyObject *scanner = rust_bound_iterator(
        args, nargs, kwnames, "finditer", state->scanner_type
    );
    if (scanner == NULL) return NULL;
    PyObject *search = PyCMethod_New(
        &rust_iterator_scanner_search_method,
        scanner,
        NULL,
        state->scanner_type
    );
    Py_DECREF(scanner);
    if (search == NULL) return NULL;
    PyObject *iterator = PyCallIter_New(search, Py_None);
    Py_DECREF(search);
    return iterator;
}

static PyObject *bridge_bound_scanner(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    RustBridgeState *state = module == NULL
        ? (nargs > 0 ? rust_bridge_state_from_type(Py_TYPE(args[0])) : NULL)
        : rust_bridge_state_from_module(module);
    if (state == NULL) {
        if (!PyErr_Occurred()) {
            PyErr_SetString(PyExc_SystemError, "Rust scanner has no owning bridge state");
        }
        return NULL;
    }
    return rust_bound_iterator(
        args, nargs, kwnames, "scanner", state->scanner_type
    );
}

static int rust_append_batched_split(
    PyObject *result,
    const RustSubject *subject,
    size_t stride,
    size_t *previous,
    const intptr_t *begins,
    const intptr_t *ends
) {
    PyObject *prefix = rust_findall_item(
        subject,
        (intptr_t)*previous,
        begins[0]
    );
    if (rust_list_append_owned(result, prefix) != 0) return -1;

    for (size_t group = 1; group < stride; group++) {
        PyObject *piece = begins[group] < 0
            ? Py_NewRef(Py_None)
            : rust_findall_item(subject, begins[group], ends[group]);
        if (rust_list_append_owned(result, piece) != 0) return -1;
    }

    *previous = (size_t)ends[0];
    return 0;
}

static PyObject *bridge_bound_split(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    (void)module;
    Py_ssize_t keywords = kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    if (nargs < 3 || nargs - 3 + keywords > 2) {
        PyErr_Format(PyExc_TypeError, "split() takes at most 2 arguments (%zd given)", nargs < 3 ? 0 : nargs - 3 + keywords);
        return NULL;
    }
    PyObject *value = nargs >= 4 ? args[3] : NULL;
    PyObject *limit_value = nargs >= 5 ? args[4] : NULL;
    for (Py_ssize_t index = 0; index < keywords; index++) {
        PyObject *name = PyTuple_GET_ITEM(kwnames, index);
        if (PyUnicode_CompareWithASCIIString(name, "string") == 0) {
            if (value != NULL) {
                PyErr_SetString(PyExc_TypeError, "argument for split() given by name ('string') and position (1)");
                return NULL;
            }
            value = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "maxsplit") == 0) {
            if (limit_value != NULL) {
                PyErr_SetString(PyExc_TypeError, "argument for split() given by name ('maxsplit') and position (2)");
                return NULL;
            }
            limit_value = args[nargs + index];
        } else {
            if (!PyErr_Occurred()) PyErr_Format(PyExc_TypeError, "split() got an unexpected keyword argument '%U'", name);
            return NULL;
        }
    }
    if (value == NULL) {
        PyErr_SetString(PyExc_TypeError, "split() missing required argument 'string' (pos 1)");
        return NULL;
    }
    void *handle = PyLong_AsVoidPtr(args[0]);
    size_t groups = PyLong_AsSize_t(args[2]);
    if (PyErr_Occurred()) return NULL;
    if (groups != rebar_groups(handle)) {
        PyErr_SetString(PyExc_ValueError, "Rust regex group count does not match the compiled program");
        return NULL;
    }
    Py_ssize_t limit = 0;
    if (limit_value != NULL && !rust_index_arg(limit_value, &limit)) return NULL;
    RustSubject subject;
    if (!rust_subject_open(&subject, args[1], value, 1)) return NULL;
    PyObject *result = PyList_New(0);
    if (result == NULL) {
        rust_subject_release(&subject);
        return NULL;
    }
    size_t stride = groups + 1;
    if (
        stride == 0
        || stride > (SIZE_MAX / RUST_FINDALL_BATCH_CAPACITY - 1) / 2
    ) {
        rust_subject_release(&subject);
        Py_DECREF(result);
        return PyErr_NoMemory();
    }
    size_t words = RUST_FINDALL_BATCH_CAPACITY * (stride * 2 + 1);
    if (words > SIZE_MAX / sizeof(intptr_t)) {
        rust_subject_release(&subject);
        Py_DECREF(result);
        return PyErr_NoMemory();
    }
    intptr_t local[
        RUST_FINDALL_BATCH_CAPACITY * (RUST_FINDALL_INLINE_STRIDE * 2 + 1)
    ];
    intptr_t *storage = words <= sizeof(local) / sizeof(local[0])
        ? local
        : PyMem_Malloc(words * sizeof(intptr_t));
    if (storage == NULL) {
        rust_subject_release(&subject);
        Py_DECREF(result);
        return PyErr_NoMemory();
    }
    intptr_t *begins = storage;
    intptr_t *ends = begins + RUST_FINDALL_BATCH_CAPACITY * stride;
    intptr_t *lasts = ends + RUST_FINDALL_BATCH_CAPACITY * stride;
    size_t current = 0;
    size_t previous = 0;
    size_t produced = 0;
    uint8_t pending_nonempty = 0;
    int batched = !subject.text || rebar_collect_wide != NULL;

    while (
        limit >= 0
        && current <= subject.length
        && (limit == 0 || produced < (size_t)limit)
    ) {
        if (batched && pending_nonempty) {
            intptr_t last = -1;
            int found = rust_subject_match(
                handle,
                &subject,
                current,
                subject.length,
                1,
                1,
                begins,
                ends,
                &last
            );
            if (found < 0) {
                PyErr_SetString(
                    PyExc_RuntimeError,
                    "Rust continuation engine rejected the split bridge call"
                );
                goto split_error;
            }
            if (found > 0) {
                if (begins[0] == ends[0]) {
                    PyErr_SetString(
                        PyExc_RuntimeError,
                        "Rust nonempty continuation produced an empty match"
                    );
                    goto split_error;
                }
                if (
                    rust_append_batched_split(
                        result,
                        &subject,
                        stride,
                        &previous,
                        begins,
                        ends
                    ) != 0
                ) {
                    goto split_error;
                }
                produced++;
                current = (size_t)ends[0];
            } else {
                if (current == subject.length) break;
                current++;
            }
            pending_nonempty = 0;
            continue;
        }

        size_t capacity = batched ? RUST_FINDALL_BATCH_CAPACITY : 1;
        if (limit > 0) {
            size_t remaining = (size_t)limit - produced;
            if (remaining < capacity) capacity = remaining;
        }

        intptr_t count;
        if (!batched) {
            count = rust_subject_match(
                handle,
                &subject,
                current,
                subject.length,
                0,
                pending_nonempty,
                begins,
                ends,
                lasts
            );
        } else if (subject.text) {
            count = rebar_collect_wide(
                handle,
                subject.data,
                subject.length,
                subject.kind,
                current,
                subject.length,
                capacity,
                begins,
                ends,
                lasts
            );
        } else {
            count = rebar_collect_ascii(
                handle,
                subject.data,
                subject.length,
                current,
                subject.length,
                capacity,
                begins,
                ends,
                lasts
            );
        }
        if (count < 0 || (size_t)count > capacity) {
            PyErr_SetString(
                PyExc_RuntimeError,
                "Rust continuation engine rejected the split bridge call"
            );
            goto split_error;
        }
        if (count == 0) break;

        for (intptr_t match = 0; match < count; match++) {
            size_t offset = (size_t)match * stride;
            if (
                rust_append_batched_split(
                    result,
                    &subject,
                    stride,
                    &previous,
                    begins + offset,
                    ends + offset
                ) != 0
            ) {
                goto split_error;
            }
            produced++;
        }

        size_t last_offset = (size_t)(count - 1) * stride;
        current = (size_t)ends[last_offset];
        pending_nonempty = begins[last_offset] == ends[last_offset];
        if ((size_t)count < capacity) break;
    }
    PyObject *tail = rust_findall_item(&subject, (intptr_t)previous, (intptr_t)subject.length);
    if (rust_list_append_owned(result, tail) != 0) goto split_error;
    if (storage != local) PyMem_Free(storage);
    rust_subject_release(&subject);
    return result;

split_error:
    if (storage != local) PyMem_Free(storage);
    rust_subject_release(&subject);
    Py_DECREF(result);
    return NULL;
}

typedef struct {
    PyUnicodeWriter *unicode;
    PyObject *bytes;
    Py_ssize_t capacity;
    Py_ssize_t used;
    Py_ssize_t pieces;
    uint8_t text;
} RustOutputWriter;

static int rust_output_init(RustOutputWriter *writer, int text, Py_ssize_t estimate) {
    memset(writer, 0, sizeof(*writer));
    writer->text = (uint8_t)text;
    if (text) {
        writer->unicode = PyUnicodeWriter_Create(estimate);
        return writer->unicode == NULL ? -1 : 0;
    }
    writer->capacity = estimate < 16 ? 16 : estimate;
    writer->bytes = PyBytes_FromStringAndSize(NULL, writer->capacity);
    return writer->bytes == NULL ? -1 : 0;
}

static void rust_output_discard(RustOutputWriter *writer) {
    if (writer->unicode != NULL) {
        PyUnicodeWriter_Discard(writer->unicode);
        writer->unicode = NULL;
    }
    Py_CLEAR(writer->bytes);
}

static int rust_output_bytes(RustOutputWriter *writer, const uint8_t *data, Py_ssize_t count) {
    if (count == 0) return 0;
    if (count < 0 || writer->used > PY_SSIZE_T_MAX - count) {
        PyErr_NoMemory();
        return -1;
    }
    Py_ssize_t required = writer->used + count;
    if (required > writer->capacity) {
        Py_ssize_t grown = writer->capacity;
        while (grown < required) {
            if (grown > PY_SSIZE_T_MAX / 2) {
                grown = required;
                break;
            }
            grown *= 2;
        }
        if (_PyBytes_Resize(&writer->bytes, grown) < 0) return -1;
        writer->capacity = grown;
    }
    memcpy(PyBytes_AS_STRING(writer->bytes) + writer->used, data, (size_t)count);
    writer->used = required;
    return 0;
}

static int rust_output_subject(RustOutputWriter *writer, const RustSubject *subject, size_t start, size_t end) {
    if (end <= start) return 0;
    int result;
    if (writer->text) result = PyUnicodeWriter_WriteSubstring(writer->unicode, subject->object, (Py_ssize_t)start, (Py_ssize_t)end);
    else result = rust_output_bytes(writer, subject->data + start, (Py_ssize_t)(end - start));
    if (result == 0) writer->pieces++;
    return result;
}

static int rust_output_value(RustOutputWriter *writer, PyObject *value) {
    if (value == Py_None) return 0;
    if (writer->text) {
        if (!PyUnicode_Check(value)) {
            PyErr_Format(PyExc_TypeError, "sequence item %zd: expected str instance, %.200s found", writer->pieces, Py_TYPE(value)->tp_name);
            return -1;
        }
        if (PyUnicodeWriter_WriteStr(writer->unicode, value) < 0) return -1;
        writer->pieces++;
        return 0;
    }
    if (PyBytes_Check(value)) {
        if (rust_output_bytes(writer, (const uint8_t *)PyBytes_AS_STRING(value), PyBytes_GET_SIZE(value)) < 0) return -1;
        writer->pieces++;
        return 0;
    }
    Py_buffer view = {0};
    if (PyObject_GetBuffer(value, &view, PyBUF_SIMPLE) != 0) {
        PyErr_Clear();
        PyErr_Format(PyExc_TypeError, "sequence item %zd: expected a bytes-like object, %.200s found", writer->pieces, Py_TYPE(value)->tp_name);
        return -1;
    }
    int result = rust_output_bytes(writer, view.buf, view.len);
    PyBuffer_Release(&view);
    if (result == 0) writer->pieces++;
    return result;
}

static PyObject *rust_output_finish(RustOutputWriter *writer) {
    if (writer->text) {
        PyUnicodeWriter *unicode = writer->unicode;
        writer->unicode = NULL;
        return PyUnicodeWriter_Finish(unicode);
    }
    if (writer->used != writer->capacity && _PyBytes_Resize(&writer->bytes, writer->used) < 0) return NULL;
    PyObject *result = writer->bytes;
    writer->bytes = NULL;
    return result;
}

static PyObject *rust_sub_result(PyObject *value, size_t count, int want_count) {
    if (value == NULL) return NULL;
    if (!want_count) return value;
    if (count > (size_t)PY_SSIZE_T_MAX) {
        Py_DECREF(value);
        return PyErr_NoMemory();
    }
    PyObject *number = PyLong_FromSize_t(count);
    if (number == NULL) {
        Py_DECREF(value);
        return NULL;
    }
    PyObject *result = PyTuple_New(2);
    if (result == NULL) {
        Py_DECREF(value);
        Py_DECREF(number);
        return NULL;
    }
    PyTuple_SET_ITEM(result, 0, value);
    PyTuple_SET_ITEM(result, 1, number);
    return result;
}

static PyObject *rust_sub_unchanged(const RustSubject *subject) {
    if (subject->text) return PyUnicode_Substring(subject->object, 0, (Py_ssize_t)subject->length);
    if (PyBytes_CheckExact(subject->object)) return Py_NewRef(subject->object);
    return PyBytes_FromStringAndSize((const char *)subject->data, (Py_ssize_t)subject->length);
}

static int rust_output_capture(
    RustOutputWriter *writer,
    const RustSubject *subject,
    size_t begin,
    size_t end
) {
    if (writer->text || PyBytes_CheckExact(subject->object)) {
        return rust_output_subject(writer, subject, begin, end);
    }

    RustSubject capture;
    if (!rust_subject_open(&capture, NULL, subject->object, 0)) {
        return -1;
    }
    if (end > capture.length) {
        rust_subject_release(&capture);
        PyErr_SetString(
            PyExc_BufferError,
            "Rust captured buffer changed size during replacement"
        );
        return -1;
    }
    int result = rust_output_subject(writer, &capture, begin, end);
    rust_subject_release(&capture);
    return result;
}

static int rust_output_template(RustOutputWriter *writer, const RustSubject *subject, PyObject *tokens, PyObject *raw, const intptr_t *begins, const intptr_t *ends, size_t groups) {
    if (tokens == Py_None) return rust_output_value(writer, raw);
    if (!PyTuple_Check(tokens)) {
        PyErr_SetString(PyExc_TypeError, "Rust replacement tokens must be a tuple");
        return -1;
    }
    Py_ssize_t count = PyTuple_GET_SIZE(tokens);
    for (Py_ssize_t index = 0; index < count; index++) {
        PyObject *token = PyTuple_GET_ITEM(tokens, index);
        if (PyLong_Check(token)) {
            size_t group = PyLong_AsSize_t(token);
            if (PyErr_Occurred() || group > groups) {
                if (!PyErr_Occurred()) PyErr_SetString(PyExc_IndexError, "invalid Rust regex replacement group");
                return -1;
            }
            if (
                begins[group] >= 0
                && rust_output_capture(
                    writer,
                    subject,
                    (size_t)begins[group],
                    (size_t)ends[group]
                ) < 0
            ) {
                return -1;
            }
        } else if (rust_output_value(writer, token) < 0) {
            return -1;
        }
    }
    return 0;
}

static int rust_restore_original_template_error(PyObject *replacement) {
    PyObject *raised = PyErr_GetRaisedException();
    if (raised == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Rust template lost its original exception");
        return -1;
    }

    PyObject *message = PyObject_GetAttrString(raised, "msg");
    if (message == NULL) {
        PyErr_Clear();
        PyErr_SetRaisedException(raised);
        return -1;
    }

    PyObject *position = PyObject_GetAttrString(raised, "pos");
    if (position == NULL) {
        PyErr_Clear();
        Py_DECREF(message);
        PyErr_SetRaisedException(raised);
        return -1;
    }

    if (position == Py_None || !PyUnicode_Check(message)) {
        Py_DECREF(position);
        Py_DECREF(message);
        PyErr_SetRaisedException(raised);
        return -1;
    }

    if (
        PyUnicode_CompareWithASCIIString(
            message, "bad escape (end of pattern)"
        ) == 0
    ) {
        Py_ssize_t original_length = PyObject_Length(replacement);
        if (original_length < 0) {
            Py_DECREF(position);
            Py_DECREF(message);
            Py_DECREF(raised);
            return -1;
        }
        PyObject *original_position = PyLong_FromSsize_t(original_length - 1);
        if (original_position == NULL) {
            Py_DECREF(position);
            Py_DECREF(message);
            Py_DECREF(raised);
            return -1;
        }
        Py_SETREF(position, original_position);
    }

    PyObject *restored = PyObject_CallFunctionObjArgs(
        (PyObject *)Py_TYPE(raised), message, replacement, position, NULL
    );
    Py_DECREF(position);
    Py_DECREF(message);
    Py_DECREF(raised);
    if (restored != NULL) {
        PyErr_SetRaisedException(restored);
    }
    return -1;
}

static int rust_replacement_cache(PyObject *pattern, PyObject *templates, PyObject *replacement, PyObject *subject, Py_ssize_t length, PyObject **raw, PyObject **tokens) {
    PyObject *normalized = NULL;
    int escaped = 0;
    int original_hash_checked = 0;

    if (PyUnicode_Check(replacement)) {
        Py_ssize_t found = PyUnicode_FindChar(replacement, '\\', 0, PyUnicode_GET_LENGTH(replacement), 1);
        if (found < 0 && PyErr_Occurred()) return -1;
        escaped = found >= 0;
        if (escaped) {
            normalized = PyUnicode_FromObject(replacement);
            if (normalized == NULL) return -1;
        }
    } else if (PyBytes_Check(replacement)) {
        Py_ssize_t size = PyBytes_GET_SIZE(replacement);
        escaped = size != 0 && memchr(PyBytes_AS_STRING(replacement), '\\', (size_t)size) != NULL;
        if (escaped) {
            normalized = PyBytes_CheckExact(replacement) ? Py_NewRef(replacement) : PyBytes_FromObject(replacement);
            if (normalized == NULL) return -1;
        }
    } else {
        Py_buffer buffer = {0};
        if (PyObject_GetBuffer(replacement, &buffer, PyBUF_SIMPLE) == 0) {
            escaped = buffer.len != 0 && memchr(buffer.buf, '\\', (size_t)buffer.len) != NULL;
            PyBuffer_Release(&buffer);
            if (escaped) {
                int materialization_flags = PyBUF_SIMPLE;
                Py_hash_t original_hash = PyObject_Hash(replacement);
                original_hash_checked = 1;
                if (original_hash == -1) {
                    if (!PyErr_ExceptionMatches(PyExc_TypeError)) return -1;
                    PyErr_Clear();
                    materialization_flags = PyBUF_FULL_RO;
                }
                if (
                    PyObject_GetBuffer(
                        replacement, &buffer, materialization_flags
                    ) != 0
                ) {
                    return -1;
                }
                normalized = PyBytes_FromStringAndSize(NULL, buffer.len);
                if (
                    normalized != NULL
                    && buffer.len != 0
                    && PyBuffer_ToContiguous(
                        PyBytes_AS_STRING(normalized), &buffer, buffer.len, 'C'
                    ) < 0
                ) {
                    Py_CLEAR(normalized);
                }
                PyBuffer_Release(&buffer);
                if (normalized == NULL) return -1;
            }
        } else {
            PyErr_Clear();
            if (PyObject_CheckBuffer(replacement)) {
                Py_buffer retry = {0};
                if (
                    PyObject_GetBuffer(
                        replacement, &retry, PyBUF_SIMPLE
                    ) == 0
                ) {
                    normalized = PyBytes_FromStringAndSize(
                        (const char *)retry.buf, retry.len
                    );
                    PyBuffer_Release(&retry);
                    if (normalized == NULL) return -1;
                } else {
                    PyErr_Clear();
                }
            }
            if (normalized == NULL) {
                normalized = PyBytes_FromObject(replacement);
            }
            if (normalized == NULL) {
                if (PyErr_ExceptionMatches(PyExc_BufferError)) return -1;
                PyErr_Clear();
                if (PyObject_Hash(replacement) == -1) return -1;
                PyErr_Format(PyExc_TypeError, "decoding to str: need a bytes-like object, %.200s found", Py_TYPE(replacement)->tp_name);
                return -1;
            }
            if (
                PyMemoryView_Check(replacement)
                && PyObject_Hash(replacement) == -1
            ) {
                Py_DECREF(normalized);
                return -1;
            }
            Py_ssize_t size = PyBytes_GET_SIZE(normalized);
            escaped = size != 0 && memchr(PyBytes_AS_STRING(normalized), '\\', (size_t)size) != NULL;
            if (!escaped) {
                *raw = normalized;
                *tokens = Py_NewRef(Py_None);
                return 0;
            }
        }
    }

    if (!escaped) {
        *raw = Py_NewRef(replacement);
        *tokens = Py_NewRef(Py_None);
        return 0;
    }

    if (
        !original_hash_checked
        && !PyUnicode_CheckExact(replacement)
        && !PyBytes_CheckExact(replacement)
    ) {
        Py_hash_t fingerprint = PyObject_Hash(replacement);
        if (fingerprint == -1) {
            if (!PyErr_ExceptionMatches(PyExc_TypeError)) {
                Py_DECREF(normalized);
                return -1;
            }
            PyErr_Clear();
        }
    }

    if (PyDict_Check(templates)) {
        PyObject *value = PyDict_GetItemWithError(templates, normalized);
        if (value != NULL) {
            *raw = normalized;
            *tokens = Py_NewRef(value);
            return 0;
        }
        if (PyErr_Occurred()) {
            Py_DECREF(normalized);
            return -1;
        }
    }

    PyObject *loaded = PyObject_CallMethod(pattern, "_cached_template", "OOn", normalized, subject, length);
    Py_DECREF(normalized);
    if (loaded == NULL) {
        if (
            !PyUnicode_Check(replacement)
            && !PyBytes_Check(replacement)
            && PyObject_CheckBuffer(replacement)
        ) {
            return rust_restore_original_template_error(replacement);
        }
        if (((PyUnicode_Check(replacement) && !PyUnicode_CheckExact(replacement))
             || (PyBytes_Check(replacement) && !PyBytes_CheckExact(replacement)))
            && Py_TYPE(replacement)->tp_hash != PyObject_HashNotImplemented) {
            PyObject *raised = PyErr_GetRaisedException();
            if (raised != NULL && PyObject_HasAttrString(raised, "pattern")) {
                if (PyObject_SetAttrString(raised, "pattern", replacement) < 0) {
                    Py_DECREF(raised);
                    return -1;
                }
            }
            if (raised != NULL) PyErr_SetRaisedException(raised);
        }
        return -1;
    }
    if (!PyTuple_Check(loaded) || PyTuple_GET_SIZE(loaded) != 2) {
        Py_DECREF(loaded);
        PyErr_SetString(PyExc_RuntimeError, "Rust replacement-template cache returned invalid metadata");
        return -1;
    }
    *raw = Py_NewRef(PyTuple_GET_ITEM(loaded, 0));
    *tokens = Py_NewRef(PyTuple_GET_ITEM(loaded, 1));
    Py_DECREF(loaded);
    return 0;
}

static PyObject *rust_normalize_expand_buffer(PyObject *template) {
    if (PyObject_Hash(template) == -1) {
        if (!PyErr_ExceptionMatches(PyExc_TypeError)) return NULL;
        PyErr_Clear();
        return PyBytes_FromObject(template);
    }

    Py_buffer view = {0};
    if (PyObject_GetBuffer(template, &view, PyBUF_SIMPLE) == 0) {
        PyObject *normalized = PyBytes_FromStringAndSize(
            (const char *)view.buf, view.len
        );
        PyBuffer_Release(&view);
        return normalized;
    }

    PyErr_Clear();
    return PyBytes_FromObject(template);
}

static PyObject *rust_match_expand(RustMatch *match, PyObject *template) {
    RustBridgeState *state = rust_bridge_state_from_type(Py_TYPE(match));
    if (state == NULL) return NULL;
    if (state->template_helper == NULL) {
        return rust_match_expand_fallback(match, template);
    }

    int text = PyUnicode_CheckExact(match->string);
    int ordinary_bytes = PyBytes_CheckExact(match->string);
    int ordinary_bytearray = PyByteArray_CheckExact(match->string);
    int ordinary_memoryview = PyMemoryView_Check(match->string);
    if (
        (text && !PyUnicode_CheckExact(template))
        || (!text && !(ordinary_bytes || ordinary_bytearray || ordinary_memoryview))
        || (!text && !PyBytes_CheckExact(template))
    ) {
        if (
            !text
            && !PyBytes_Check(template)
            && PyObject_CheckBuffer(template)
        ) {
            PyObject *normalized = rust_normalize_expand_buffer(template);
            if (normalized == NULL) return NULL;
            PyObject *result = rust_match_expand_fallback(match, normalized);
            Py_DECREF(normalized);
            if (result == NULL) {
                (void)rust_restore_original_template_error(template);
            }
            return result;
        }
        return rust_match_expand_fallback(match, template);
    }

    Py_ssize_t source_length = text
        ? PyUnicode_GET_LENGTH(match->string)
        : ordinary_bytes
            ? PyBytes_GET_SIZE(match->string)
            : ordinary_bytearray
                ? PyByteArray_GET_SIZE(match->string)
                : match->endpos;
    PyObject *templates = PyObject_GetAttr(
        match->pattern,
        state->pattern_attribute_names[RUST_PATTERN_ATTRIBUTE_TEMPLATES]
    );
    if (templates == NULL) return NULL;
    if (templates != Py_None && !PyDict_CheckExact(templates)) {
        Py_DECREF(templates);
        return rust_match_expand_fallback(match, template);
    }

    PyObject *raw = NULL;
    PyObject *tokens = NULL;
    if (
        rust_replacement_cache(
            match->pattern, templates, template, match->string,
            source_length, &raw, &tokens
        ) < 0
    ) {
        Py_DECREF(templates);
        Py_XDECREF(raw);
        Py_XDECREF(tokens);
        return NULL;
    }
    Py_DECREF(templates);

    RustSubject subject;
    if (!rust_subject_open(&subject, NULL, match->string, 0)) {
        Py_DECREF(raw);
        Py_DECREF(tokens);
        return NULL;
    }

    size_t groups = (size_t)match->groups;
    size_t stride = groups + 1;
    const intptr_t *begins = match->spans;
    const intptr_t *ends = match->spans + stride;
    for (size_t group = 0; group < stride; group++) {
        intptr_t begin = begins[group];
        if (begin < 0) continue;
        intptr_t end = ends[group];
        if (end < begin || (size_t)end > subject.length) {
            rust_subject_release(&subject);
            Py_DECREF(raw);
            Py_DECREF(tokens);
            return rust_match_expand_fallback(match, template);
        }
    }

    Py_ssize_t estimate = text
        ? PyUnicode_GET_LENGTH(template)
        : PyBytes_GET_SIZE(template);
    RustOutputWriter writer = {0};
    PyObject *result = NULL;
    if (
        rust_output_init(&writer, text, estimate) == 0
        && rust_output_template(
            &writer, &subject, tokens, raw, begins, ends, groups
        ) == 0
    ) {
        result = rust_output_finish(&writer);
    }
    if (result == NULL) rust_output_discard(&writer);
    rust_subject_release(&subject);
    Py_DECREF(raw);
    Py_DECREF(tokens);
    return result;
}

static PyObject *rust_substitute_core(PyObject *pattern, void *handle, PyObject *groupindex, PyObject *pattern_value, PyObject *templates, size_t groups, PyObject *replacement, PyObject *value, Py_ssize_t limit, int want_count) {
    RustBridgeState *state = rust_bridge_state_from_type(Py_TYPE(pattern));
    if (state == NULL) return NULL;
    if (groups != rebar_groups(handle)) {
        PyErr_SetString(PyExc_ValueError, "Rust regex group count does not match the compiled program");
        return NULL;
    }
    RustSubject subject = {0};
    int callback = PyCallable_Check(replacement);
    PyObject *raw = NULL;
    PyObject *tokens = NULL;
    if (!rust_subject_open(&subject, pattern_value, value, 1)) {
        return NULL;
    }
    if (!callback) {
        if (subject.length > (size_t)PY_SSIZE_T_MAX) {
            rust_subject_release(&subject);
            return PyErr_NoMemory();
        }
        Py_ssize_t validation_length = (Py_ssize_t)subject.length;
        if (
            rust_replacement_cache(
                pattern, templates, replacement, value,
                validation_length, &raw, &tokens
            ) < 0
        ) {
            Py_XDECREF(raw);
            Py_XDECREF(tokens);
            rust_subject_release(&subject);
            return NULL;
        }
    }
    int deferred = callback || (
        tokens == Py_None && !PyUnicode_Check(raw) && !PyBytes_Check(raw)
    );
    if (limit < 0) {
        PyObject *unchanged = rust_sub_unchanged(&subject);
        Py_XDECREF(raw);
        Py_XDECREF(tokens);
        rust_subject_release(&subject);
        return rust_sub_result(unchanged, 0, want_count);
    }

    size_t stride = groups + 1;
    if (stride == 0 || stride > SIZE_MAX / (sizeof(intptr_t) * 2)) {
        Py_XDECREF(raw);
        Py_XDECREF(tokens);
        rust_subject_release(&subject);
        return PyErr_NoMemory();
    }
    intptr_t local_begins[RUST_LOCAL_CAPTURE_WORDS];
    intptr_t local_ends[RUST_LOCAL_CAPTURE_WORDS];
    intptr_t *begins = local_begins;
    intptr_t *ends = local_ends;
    if (stride > RUST_LOCAL_CAPTURE_WORDS) {
        begins = PyMem_Malloc(stride * sizeof(intptr_t) * 2);
        if (begins == NULL) {
            Py_XDECREF(raw);
            Py_XDECREF(tokens);
            rust_subject_release(&subject);
            return PyErr_NoMemory();
        }
        ends = begins + stride;
    }
    RustOutputWriter writer = {0};
    PyObject *pieces = NULL;
    if (deferred) {
        pieces = PyList_New(0);
        if (pieces == NULL) {
            if (begins != local_begins) PyMem_Free(begins);
            Py_XDECREF(raw);
            Py_XDECREF(tokens);
            rust_subject_release(&subject);
            return NULL;
        }
    }
    size_t previous = 0;
    size_t current = 0;
    size_t replaced = 0;
    uint8_t nonempty = 0;
    while (current <= subject.length && (limit == 0 || replaced < (size_t)limit)) {
        intptr_t last = -1;
        int found = rust_subject_match(handle, &subject, current, subject.length, 0, nonempty, begins, ends, &last);
        if (found < 0) {
            PyErr_SetString(PyExc_RuntimeError, "Rust continuation engine rejected the replacement bridge call");
            goto substitute_error;
        }
        if (found == 0) break;
        if (deferred) {
            if (previous < (size_t)begins[0]) {
                PyObject *prefix = rust_findall_item(&subject, (intptr_t)previous, begins[0]);
                if (rust_list_append_owned(pieces, prefix) != 0) goto substitute_error;
            }
            PyObject *piece;
            if (callback) {
                RustMatch *match = rust_match_allocate(pattern, value, groupindex, groups, 0, (Py_ssize_t)subject.length);
                if (match == NULL) goto substitute_error;
                memcpy(match->spans, begins, stride * sizeof(intptr_t));
                memcpy(match->spans + stride, ends, stride * sizeof(intptr_t));
                match->lastindex = last;
                piece = PyObject_CallOneArg(replacement, (PyObject *)match);
                Py_DECREF(match);
                if (piece == NULL) goto substitute_error;
            } else {
                piece = Py_NewRef(raw);
            }
            if (piece == Py_None) {
                Py_DECREF(piece);
            } else if (rust_list_append_owned(pieces, piece) != 0) {
                goto substitute_error;
            }
        } else {
            if (replaced == 0 && rust_output_init(&writer, subject.text, (Py_ssize_t)subject.length) < 0) goto substitute_error;
            if (rust_output_subject(&writer, &subject, previous, (size_t)begins[0]) < 0) goto substitute_error;
            if (tokens != Py_None && subject.text != (uint8_t)PyUnicode_Check(raw)) {
                if (state->template_helper == NULL) {
                    PyErr_SetString(PyExc_RuntimeError, "Rust replacement template helper has not been configured");
                    goto substitute_error;
                }
                RustMatch *match = rust_match_allocate(pattern, value, groupindex, groups, 0, (Py_ssize_t)subject.length);
                if (match == NULL) goto substitute_error;
                memcpy(match->spans, begins, stride * sizeof(intptr_t));
                memcpy(match->spans + stride, ends, stride * sizeof(intptr_t));
                match->lastindex = last;
                PyObject *piece = PyObject_CallFunctionObjArgs(
                    state->template_helper, raw, (PyObject *)match, NULL
                );
                Py_DECREF(match);
                if (piece == NULL) goto substitute_error;
                int written = rust_output_value(&writer, piece);
                Py_DECREF(piece);
                if (written < 0) goto substitute_error;
            } else if (rust_output_template(&writer, &subject, tokens, raw, begins, ends, groups) < 0) {
                goto substitute_error;
            }
        }
        previous = (size_t)ends[0];
        replaced++;
        if (begins[0] == ends[0]) {
            current = (size_t)begins[0];
            nonempty = 1;
        } else {
            current = (size_t)ends[0];
            nonempty = 0;
        }
    }
    PyObject *joined;
    if (replaced == 0) {
        joined = rust_sub_unchanged(&subject);
    } else if (deferred) {
        if (previous < subject.length) {
            PyObject *tail = rust_findall_item(&subject, (intptr_t)previous, (intptr_t)subject.length);
            if (rust_list_append_owned(pieces, tail) != 0) goto substitute_error;
        }
        PyObject *separator = Py_GetConstant(subject.text ? Py_CONSTANT_EMPTY_STR : Py_CONSTANT_EMPTY_BYTES);
        if (separator == NULL) goto substitute_error;
        joined = subject.text ? PyUnicode_Join(separator, pieces) : PyBytes_Join(separator, pieces);
        Py_DECREF(separator);
    } else {
        if (rust_output_subject(&writer, &subject, previous, subject.length) < 0) goto substitute_error;
        joined = rust_output_finish(&writer);
    }
    if (begins != local_begins) PyMem_Free(begins);
    Py_XDECREF(pieces);
    Py_XDECREF(raw);
    Py_XDECREF(tokens);
    rust_subject_release(&subject);
    return rust_sub_result(joined, replaced, want_count);

substitute_error:
    rust_output_discard(&writer);
    if (begins != local_begins) PyMem_Free(begins);
    Py_XDECREF(pieces);
    Py_XDECREF(raw);
    Py_XDECREF(tokens);
    rust_subject_release(&subject);
    return NULL;
}

static PyObject *rust_bound_substitute(PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames, int want_count) {
    const char *method = want_count ? "subn" : "sub";
    Py_ssize_t keywords = kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    if (nargs < 7 || nargs - 7 + keywords > 3) {
        PyErr_Format(PyExc_TypeError, "%s() takes at most 3 arguments (%zd given)", method, nargs < 7 ? 0 : nargs - 7 + keywords);
        return NULL;
    }
    PyObject *replacement = nargs >= 8 ? args[7] : NULL;
    PyObject *subject = nargs >= 9 ? args[8] : NULL;
    PyObject *limit_value = nargs >= 10 ? args[9] : NULL;
    for (Py_ssize_t index = 0; index < keywords; index++) {
        PyObject *name = PyTuple_GET_ITEM(kwnames, index);
        if (PyUnicode_CompareWithASCIIString(name, "repl") == 0) {
            if (replacement != NULL) {
                PyErr_Format(PyExc_TypeError, "argument for %s() given by name ('repl') and position (1)", method);
                return NULL;
            }
            replacement = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "string") == 0) {
            if (subject != NULL) {
                PyErr_Format(PyExc_TypeError, "argument for %s() given by name ('string') and position (2)", method);
                return NULL;
            }
            subject = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "count") == 0) {
            if (limit_value != NULL) {
                PyErr_Format(PyExc_TypeError, "argument for %s() given by name ('count') and position (3)", method);
                return NULL;
            }
            limit_value = args[nargs + index];
        } else {
            if (!PyErr_Occurred()) PyErr_Format(PyExc_TypeError, "%s() got an unexpected keyword argument '%U'", method, name);
            return NULL;
        }
    }
    if (replacement == NULL || subject == NULL) {
        const char *missing = replacement == NULL ? "repl" : "string";
        int position = replacement == NULL ? 1 : 2;
        PyErr_Format(PyExc_TypeError, "%s() missing required argument '%s' (pos %d)", method, missing, position);
        return NULL;
    }
    void *handle = PyLong_AsVoidPtr(args[1]);
    size_t groups = PyLong_AsSize_t(args[6]);
    if (PyErr_Occurred()) return NULL;
    Py_ssize_t limit = 0;
    if (limit_value != NULL && !rust_index_arg(limit_value, &limit)) return NULL;
    return rust_substitute_core(args[0], handle, args[2], args[3], args[5], groups, replacement, subject, limit, want_count);
}

static PyObject *bridge_bound_sub(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    (void)module;
    return rust_bound_substitute(args, nargs, kwnames, 0);
}

static PyObject *bridge_bound_subn(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    (void)module;
    return rust_bound_substitute(args, nargs, kwnames, 1);
}

typedef enum {
    RUST_PATTERN_SEARCH,
    RUST_PATTERN_MATCH,
    RUST_PATTERN_FULLMATCH,
    RUST_PATTERN_FINDALL,
    RUST_PATTERN_FINDITER,
    RUST_PATTERN_SCANNER,
    RUST_PATTERN_SPLIT,
    RUST_PATTERN_SUB,
    RUST_PATTERN_SUBN,
} RustPatternMethod;

typedef PyObject *(*RustPatternBridgeCall)(
    PyObject *, PyObject *const *, Py_ssize_t, PyObject *
);

static int rust_pattern_append_attribute(
    PyObject *pattern,
    RustPatternAttribute attribute,
    PyObject **owned,
    size_t *owned_count,
    PyObject **prefix,
    size_t *prefix_count
) {
    PyObject *value = rust_pattern_get_attribute(
        pattern,
        attribute
    );
    if (value == NULL) return 0;
    owned[*owned_count] = value;
    (*owned_count)++;
    prefix[*prefix_count] = value;
    (*prefix_count)++;
    return 1;
}

static int rust_pattern_append_attributes(
    PyObject *pattern,
    const RustPatternAttribute *attributes,
    size_t count,
    PyObject **owned,
    size_t *owned_count,
    PyObject **prefix,
    size_t *prefix_count,
    int *fast
) {
    *fast = 0;
    RustBridgeState *state = rust_bridge_state_from_type(Py_TYPE(pattern));
    if (state == NULL) return 0;
#ifndef Py_GIL_DISABLED
    PyTypeObject *type = Py_TYPE(pattern);
    unsigned int version = type->tp_version_tag;

    if (
        type == state->primary_pattern_type
        && version != 0
        && (type->tp_flags & Py_TPFLAGS_HEAPTYPE)
        && type->tp_itemsize == 0
        && type->tp_getattro == PyObject_GenericGetAttr
    ) {
        int ready = 1;
        if (
            state->pattern_slot_cache.type != type
            || state->pattern_slot_cache.version != version
        ) {
            int refreshed = rust_pattern_refresh_slot_cache(state, type, version);
            if (refreshed < 0) return 0;
            ready = refreshed;
        }

        if (ready) {
            size_t initial_owned_count = *owned_count;
            size_t initial_prefix_count = *prefix_count;
            for (size_t index = 0; index < count; index++) {
                RustPatternAttribute attribute = attributes[index];
                if (!state->pattern_slot_cache.eligible[attribute]) {
                    ready = 0;
                    break;
                }
                PyObject *value = *(PyObject **)(
                    (char *)pattern
                    + state->pattern_slot_cache.offsets[attribute]
                );
                if (value == NULL) {
                    ready = 0;
                    break;
                }
                value = Py_NewRef(value);
                owned[*owned_count] = value;
                (*owned_count)++;
                prefix[*prefix_count] = value;
                (*prefix_count)++;
            }
            if (ready) {
                *fast = 1;
                return 1;
            }
            while (*owned_count > initial_owned_count) {
                (*owned_count)--;
                Py_DECREF(owned[*owned_count]);
            }
            *prefix_count = initial_prefix_count;
        }
    }
#endif

    for (size_t index = 0; index < count; index++) {
        if (!rust_pattern_append_attribute(
                pattern,
                attributes[index],
                owned,
                owned_count,
                prefix,
                prefix_count
            )) {
            return 0;
        }
    }
    return 1;
}

static const RustPatternAttribute rust_pattern_matching_attributes[] = {
    RUST_PATTERN_ATTRIBUTE_HANDLE,
    RUST_PATTERN_ATTRIBUTE_GROUPINDEX,
    RUST_PATTERN_ATTRIBUTE_PATTERN,
    RUST_PATTERN_ATTRIBUTE_LITERAL,
};

static const RustPatternAttribute rust_pattern_findall_literal_attributes[] = {
    RUST_PATTERN_ATTRIBUTE_LITERAL,
};

static const RustPatternAttribute rust_pattern_findall_attributes[] = {
    RUST_PATTERN_ATTRIBUTE_HANDLE,
    RUST_PATTERN_ATTRIBUTE_PATTERN,
    RUST_PATTERN_ATTRIBUTE_GROUPS,
};

static const RustPatternAttribute rust_pattern_iterator_attributes[] = {
    RUST_PATTERN_ATTRIBUTE_HANDLE,
    RUST_PATTERN_ATTRIBUTE_GROUPINDEX,
    RUST_PATTERN_ATTRIBUTE_PATTERN,
    RUST_PATTERN_ATTRIBUTE_GROUPS,
};

static const RustPatternAttribute rust_pattern_substitution_attributes[] = {
    RUST_PATTERN_ATTRIBUTE_HANDLE,
    RUST_PATTERN_ATTRIBUTE_GROUPINDEX,
    RUST_PATTERN_ATTRIBUTE_PATTERN,
    RUST_PATTERN_ATTRIBUTE_LITERAL,
    RUST_PATTERN_ATTRIBUTE_TEMPLATES,
};

#define RUST_PATTERN_APPEND_ATTRIBUTE(name) \
    do { \
        if (!rust_pattern_append_attribute( \
                pattern, name, owned, &owned_count, prefix, &prefix_count \
            )) { \
            goto cleanup; \
        } \
    } while (0)

#define RUST_PATTERN_APPEND_ATTRIBUTES(names) \
    do { \
        if (!rust_pattern_append_attributes( \
                pattern, \
                names, \
                sizeof(names) / sizeof((names)[0]), \
                owned, \
                &owned_count, \
                prefix, \
                &prefix_count, \
                &fast_attributes \
            )) { \
            goto cleanup; \
        } \
    } while (0)

static PyObject *rust_pattern_dispatch(
    PyObject *pattern,
    PyObject *const *args,
    Py_ssize_t nargs,
    PyObject *kwnames,
    RustPatternMethod operation
) {
    RustBridgeState *state = rust_bridge_state_from_type(Py_TYPE(pattern));
    if (state == NULL) return NULL;
    PyObject *owned[7] = {NULL};
    PyObject *prefix[7] = {NULL};
    size_t owned_count = 0;
    size_t prefix_count = 0;
    RustPatternBridgeCall function = NULL;
    PyObject *result = NULL;
    int fast_attributes = 0;

    switch (operation) {
        case RUST_PATTERN_SEARCH:
        case RUST_PATTERN_MATCH:
        case RUST_PATTERN_FULLMATCH:
            prefix[prefix_count++] = pattern;
            RUST_PATTERN_APPEND_ATTRIBUTES(rust_pattern_matching_attributes);
            if (kwnames == NULL && nargs >= 1 && nargs <= 3) {
                void *handle = PyLong_AsVoidPtr(prefix[1]);
                if (PyErr_Occurred()) goto cleanup;

                PyObject *pos = nargs >= 2 ? args[1] : NULL;
                PyObject *endpos = nargs >= 3 ? args[2] : NULL;
                uint8_t mode = operation == RUST_PATTERN_SEARCH
                    ? 0
                    : operation == RUST_PATTERN_MATCH
                        ? 1
                        : 2;
                result = rust_pattern_direct(
                    pattern,
                    handle,
                    prefix[2],
                    prefix[3],
                    prefix[4],
                    args[0],
                    pos,
                    endpos,
                    mode
                );
                goto cleanup;
            }
            function = operation == RUST_PATTERN_SEARCH
                ? bridge_bound_search
                : operation == RUST_PATTERN_MATCH
                    ? bridge_bound_match
                    : bridge_bound_fullmatch;
            break;
        case RUST_PATTERN_FINDALL:
            RUST_PATTERN_APPEND_ATTRIBUTES(
                rust_pattern_findall_literal_attributes
            );
            if (prefix[0] != Py_None) {
                if (
                    fast_attributes
                    && kwnames == NULL
                    && nargs >= 1
                    && nargs <= 3
                ) {
                    PyObject *pos = nargs >= 2 ? args[1] : NULL;
                    PyObject *endpos = nargs >= 3 ? args[2] : NULL;
                    result = rust_pattern_literal_findall_direct(
                        prefix[0],
                        args[0],
                        pos,
                        endpos
                    );
                    goto cleanup;
                }
                function = bridge_bound_literal_findall;
            } else {
                int literal_fast = fast_attributes;
                prefix_count = 0;
                RUST_PATTERN_APPEND_ATTRIBUTES(
                    rust_pattern_findall_attributes
                );
                if (
                    literal_fast
                    && fast_attributes
                    && kwnames == NULL
                    && nargs >= 1
                    && nargs <= 3
                ) {
                    PyObject *pos = nargs >= 2 ? args[1] : NULL;
                    PyObject *endpos = nargs >= 3 ? args[2] : NULL;
                    result = rust_pattern_findall_direct(
                        prefix[0],
                        prefix[1],
                        prefix[2],
                        args[0],
                        pos,
                        endpos
                    );
                    goto cleanup;
                }
                function = bridge_bound_findall;
            }
            break;
        case RUST_PATTERN_FINDITER:
        case RUST_PATTERN_SCANNER:
            prefix[prefix_count++] = pattern;
            RUST_PATTERN_APPEND_ATTRIBUTES(
                rust_pattern_iterator_attributes
            );
            if (
                fast_attributes
                && kwnames == NULL
                && nargs >= 1
                && nargs <= 3
            ) {
                void *handle = PyLong_AsVoidPtr(prefix[1]);
                size_t groups = PyLong_AsSize_t(prefix[4]);
                if (PyErr_Occurred()) goto cleanup;

                PyObject *pos = nargs >= 2 ? args[1] : NULL;
                PyObject *endpos = nargs >= 3 ? args[2] : NULL;
                PyObject *scanner = rust_iterator_create(
                    state->scanner_type,
                    pattern,
                    handle,
                    prefix[2],
                    prefix[3],
                    groups,
                    args[0],
                    pos,
                    endpos
                );
                if (scanner == NULL) goto cleanup;
                if (operation == RUST_PATTERN_SCANNER) {
                    result = scanner;
                    goto cleanup;
                }

                PyObject *search = PyCMethod_New(
                    &rust_iterator_scanner_search_method,
                    scanner,
                    NULL,
                    state->scanner_type
                );
                Py_DECREF(scanner);
                if (search == NULL) goto cleanup;
                result = PyCallIter_New(search, Py_None);
                Py_DECREF(search);
                goto cleanup;
            }
            function = operation == RUST_PATTERN_FINDITER
                ? bridge_bound_finditer
                : bridge_bound_scanner;
            break;
        case RUST_PATTERN_SPLIT:
            RUST_PATTERN_APPEND_ATTRIBUTES(
                rust_pattern_findall_attributes
            );
            function = bridge_bound_split;
            break;
        case RUST_PATTERN_SUB:
        case RUST_PATTERN_SUBN:
            prefix[prefix_count++] = pattern;
            RUST_PATTERN_APPEND_ATTRIBUTES(
                rust_pattern_substitution_attributes
            );
            if (prefix[prefix_count - 1] == Py_None) {
                PyObject *templates = PyDict_New();
                if (templates == NULL) goto cleanup;
                if (
                    PyObject_SetAttr(
                        pattern,
                        state->pattern_attribute_names[
                            RUST_PATTERN_ATTRIBUTE_TEMPLATES
                        ],
                        templates
                    ) < 0
                ) {
                    Py_DECREF(templates);
                    goto cleanup;
                }
                Py_SETREF(owned[owned_count - 1], templates);
                prefix[prefix_count - 1] = templates;
            }
            RUST_PATTERN_APPEND_ATTRIBUTE(RUST_PATTERN_ATTRIBUTE_GROUPS);
            function = operation == RUST_PATTERN_SUB
                ? bridge_bound_sub
                : bridge_bound_subn;
            break;
        default:
            PyErr_SetString(
                PyExc_SystemError,
                "invalid native regular-expression pattern method"
            );
            goto cleanup;
    }

    if (nargs < 0 || nargs > PY_SSIZE_T_MAX - (Py_ssize_t)prefix_count) {
        PyErr_NoMemory();
        goto cleanup;
    }
    size_t positional = (size_t)nargs;
    size_t keywords = kwnames == NULL
        ? 0
        : (size_t)PyTuple_GET_SIZE(kwnames);
    if (
        positional > SIZE_MAX - keywords
        || prefix_count > SIZE_MAX - positional - keywords
    ) {
        PyErr_NoMemory();
        goto cleanup;
    }
    size_t user_count = positional + keywords;
    size_t total = prefix_count + user_count;
    PyObject *local[RUST_LOCAL_BOUND_ARGS];
    PyObject **call = local;
    if (total > RUST_LOCAL_BOUND_ARGS) {
        if (total > SIZE_MAX / sizeof(PyObject *)) {
            PyErr_NoMemory();
            goto cleanup;
        }
        call = PyMem_Malloc(total * sizeof(PyObject *));
        if (call == NULL) {
            PyErr_NoMemory();
            goto cleanup;
        }
    }
    for (size_t index = 0; index < prefix_count; index++) {
        call[index] = prefix[index];
    }
    for (size_t index = 0; index < user_count; index++) {
        call[prefix_count + index] = args[index];
    }
    result = function(
        NULL,
        call,
        (Py_ssize_t)(prefix_count + positional),
        kwnames
    );
    if (call != local) PyMem_Free(call);

cleanup:
    for (size_t index = 0; index < owned_count; index++) {
        Py_DECREF(owned[index]);
    }
    return result;
}

#undef RUST_PATTERN_APPEND_ATTRIBUTE
#undef RUST_PATTERN_APPEND_ATTRIBUTES

#define RUST_PATTERN_CMETHOD(name, operation) \
    static PyObject *rust_pattern_##name( \
        PyObject *pattern, \
        PyTypeObject *defining_class, \
        PyObject *const *args, \
        Py_ssize_t nargs, \
        PyObject *kwnames \
    ) { \
        (void)defining_class; \
        return rust_pattern_dispatch( \
            pattern, args, nargs, kwnames, operation \
        ); \
    }

RUST_PATTERN_CMETHOD(search, RUST_PATTERN_SEARCH)
RUST_PATTERN_CMETHOD(match, RUST_PATTERN_MATCH)
RUST_PATTERN_CMETHOD(fullmatch, RUST_PATTERN_FULLMATCH)
RUST_PATTERN_CMETHOD(finditer, RUST_PATTERN_FINDITER)
RUST_PATTERN_CMETHOD(scanner, RUST_PATTERN_SCANNER)
RUST_PATTERN_CMETHOD(sub, RUST_PATTERN_SUB)
RUST_PATTERN_CMETHOD(subn, RUST_PATTERN_SUBN)

#undef RUST_PATTERN_CMETHOD

static PyObject *rust_pattern_findall(
    PyObject *pattern,
    PyObject *const *args,
    Py_ssize_t nargs,
    PyObject *kwnames
) {
    return rust_pattern_dispatch(
        pattern, args, nargs, kwnames, RUST_PATTERN_FINDALL
    );
}

static PyObject *rust_pattern_split(
    PyObject *pattern,
    PyObject *const *args,
    Py_ssize_t nargs,
    PyObject *kwnames
) {
    return rust_pattern_dispatch(
        pattern, args, nargs, kwnames, RUST_PATTERN_SPLIT
    );
}

static PyMethodDef rust_pattern_methods[] = {
    {
        "search",
        _PyCFunction_CAST(rust_pattern_search),
        METH_METHOD | METH_FASTCALL | METH_KEYWORDS,
        "search($self, /, string, pos=0, endpos=sys.maxsize)\n--\n\n"
        "Scan through string looking for a match, and return a "
        "corresponding match object instance.\n\n"
        "Return None if no position in the string matches.",
    },
    {
        "match",
        _PyCFunction_CAST(rust_pattern_match),
        METH_METHOD | METH_FASTCALL | METH_KEYWORDS,
        "match($self, /, string, pos=0, endpos=sys.maxsize)\n--\n\n"
        "Matches zero or more characters at the beginning of the string.",
    },
    {
        "fullmatch",
        _PyCFunction_CAST(rust_pattern_fullmatch),
        METH_METHOD | METH_FASTCALL | METH_KEYWORDS,
        "fullmatch($self, /, string, pos=0, endpos=sys.maxsize)\n--\n\n"
        "Matches against all of the string.",
    },
    {
        "findall",
        _PyCFunction_CAST(rust_pattern_findall),
        METH_FASTCALL | METH_KEYWORDS,
        "findall($self, /, string, pos=0, endpos=sys.maxsize)\n--\n\n"
        "Return a list of all non-overlapping matches of pattern "
        "in string.",
    },
    {
        "finditer",
        _PyCFunction_CAST(rust_pattern_finditer),
        METH_METHOD | METH_FASTCALL | METH_KEYWORDS,
        "finditer($self, /, string, pos=0, endpos=sys.maxsize)\n--\n\n"
        "Return an iterator over all non-overlapping matches for "
        "the RE pattern in string.\n\n"
        "For each match, the iterator returns a match object.",
    },
    {
        "scanner",
        _PyCFunction_CAST(rust_pattern_scanner),
        METH_METHOD | METH_FASTCALL | METH_KEYWORDS,
        "scanner($self, /, string, pos=0, endpos=sys.maxsize)\n--\n\n",
    },
    {
        "split",
        _PyCFunction_CAST(rust_pattern_split),
        METH_FASTCALL | METH_KEYWORDS,
        "split($self, /, string, maxsplit=0)\n--\n\n"
        "Split string by the occurrences of pattern.",
    },
    {
        "sub",
        _PyCFunction_CAST(rust_pattern_sub),
        METH_METHOD | METH_FASTCALL | METH_KEYWORDS,
        "sub($self, /, repl, string, count=0)\n--\n\n"
        "Return the string obtained by replacing the leftmost "
        "non-overlapping occurrences of pattern in string "
        "by the replacement repl.",
    },
    {
        "subn",
        _PyCFunction_CAST(rust_pattern_subn),
        METH_METHOD | METH_FASTCALL | METH_KEYWORDS,
        "subn($self, /, repl, string, count=0)\n--\n\n"
        "Return the tuple (new_string, number_of_subs_made) found "
        "by replacing the leftmost non-overlapping occurrences "
        "of pattern with the replacement repl.",
    },
    {NULL, NULL, 0, NULL},
};

static PyObject *bridge_pattern_descriptors(
    PyObject *module, PyObject *pattern_type
) {
    RustBridgeState *state = rust_bridge_state_from_module(module);
    if (state == NULL) return NULL;
    if (!PyType_Check(pattern_type)) {
        PyErr_SetString(
            PyExc_TypeError,
            "pattern_descriptors() requires a pattern type"
        );
        return NULL;
    }
    RustBridgeState *pattern_state = rust_bridge_state_from_type(
        (PyTypeObject *)pattern_type
    );
    if (pattern_state == NULL) return NULL;
    if (pattern_state != state) {
        PyErr_SetString(
            PyExc_TypeError,
            "pattern descriptors require this interpreter's Rust pattern type"
        );
        return NULL;
    }
    const Py_ssize_t count = 9;
    PyObject *descriptors = PyTuple_New(count);
    if (descriptors == NULL) return NULL;
    for (Py_ssize_t index = 0; index < count; index++) {
        PyObject *descriptor = PyDescr_NewMethod(
            (PyTypeObject *)pattern_type,
            &rust_pattern_methods[index]
        );
        if (descriptor == NULL) {
            Py_DECREF(descriptors);
            return NULL;
        }
        PyTuple_SET_ITEM(descriptors, index, descriptor);
    }
    return descriptors;
}

static PyObject *bridge_pattern_type(
    PyObject *module, PyObject *pattern_base
) {
    RustBridgeState *state = rust_bridge_state_from_module(module);
    if (state == NULL) return NULL;
    if (!PyType_Check(pattern_base)) {
        PyErr_SetString(
            PyExc_TypeError,
            "pattern_type() requires a pattern base type"
        );
        return NULL;
    }
    PyTypeObject *base = (PyTypeObject *)pattern_base;
    if (
        base->tp_basicsize < 0
        || base->tp_basicsize > INT32_MAX
        || base->tp_itemsize != 0
        || !(base->tp_flags & Py_TPFLAGS_BASETYPE)
    ) {
        PyErr_SetString(
            PyExc_TypeError,
            "pattern_type() requires a fixed-size subclassable pattern base"
        );
        return NULL;
    }
    PyType_Slot slots[] = {
        {0, NULL},
    };
    PyType_Spec specification = {
        .name = "re.Pattern",
        .basicsize = (int)base->tp_basicsize,
        .itemsize = 0,
        .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
        .slots = slots,
    };
    PyObject *bases = PyTuple_Pack(1, pattern_base);
    if (bases == NULL) return NULL;
    PyObject *pattern_type = PyType_FromModuleAndSpec(
        module, &specification, bases
    );
    Py_DECREF(bases);
#ifndef Py_GIL_DISABLED
    if (pattern_type != NULL && state->primary_pattern_type == NULL) {
        state->primary_pattern_type =
            (PyTypeObject *)Py_NewRef(pattern_type);
    }
#endif
    return pattern_type;
}

static PyObject *rust_bound_call(PyObject *value, PyObject *const *args, size_t nargsf, PyObject *kwnames) {
    RustBoundMethod *method = (RustBoundMethod *)value;
    size_t prefix = (size_t)Py_SIZE(method);
    Py_ssize_t positional_count = PyVectorcall_NARGS(nargsf);
    if (positional_count < 0) {
        PyErr_SetString(PyExc_SystemError, "Rust bound vectorcall has a negative positional argument count");
        return NULL;
    }
    size_t positional = (size_t)positional_count;
    size_t keywords = kwnames == NULL ? 0 : (size_t)PyTuple_GET_SIZE(kwnames);
    if (prefix > SIZE_MAX - positional || prefix + positional > SIZE_MAX - keywords) return PyErr_NoMemory();
    size_t total = prefix + positional + keywords;
    PyObject *local[RUST_LOCAL_BOUND_ARGS];
    PyObject **call = local;
    if (total > RUST_LOCAL_BOUND_ARGS) {
        if (total > SIZE_MAX / sizeof(PyObject *)) return PyErr_NoMemory();
        call = PyMem_Malloc(total * sizeof(PyObject *));
        if (call == NULL) return PyErr_NoMemory();
    }
    for (size_t index = 0; index < prefix; index++) call[index] = method->prefix[index];
    for (size_t index = 0; index < positional + keywords; index++) call[prefix + index] = args[index];
    PyObject *result = PyObject_Vectorcall(method->function, call, prefix + positional, kwnames);
    if (call != local) PyMem_Free(call);
    return result;
}

static void rust_bound_dealloc(RustBoundMethod *method) {
    PyTypeObject *type = Py_TYPE(method);
    PyObject_GC_UnTrack(method);
    Py_CLEAR(method->function);
    Py_CLEAR(method->pattern);
    Py_CLEAR(method->signature);
    Py_ssize_t prefix = Py_SIZE(method);
    for (Py_ssize_t index = 0; index < prefix; index++) Py_CLEAR(method->prefix[index]);
    type->tp_free((PyObject *)method);
    Py_DECREF(type);
}

static int rust_bound_traverse(RustBoundMethod *method, visitproc visit, void *arg) {
    Py_VISIT(Py_TYPE(method));
    Py_VISIT(method->function);
    Py_VISIT(method->pattern);
    Py_VISIT(method->signature);
    Py_ssize_t count = Py_SIZE(method);
    for (Py_ssize_t index = 0; index < count; index++) Py_VISIT(method->prefix[index]);
    return 0;
}

static int rust_bound_clear(RustBoundMethod *method) {
    Py_CLEAR(method->function);
    Py_CLEAR(method->pattern);
    Py_CLEAR(method->signature);
    Py_ssize_t count = Py_SIZE(method);
    for (Py_ssize_t index = 0; index < count; index++) Py_CLEAR(method->prefix[index]);
    return 0;
}

static PyObject *rust_bound_get_self(RustBoundMethod *method, void *closure) {
    (void)closure;
    return Py_NewRef(method->pattern);
}

static PyObject *rust_bound_get_name(RustBoundMethod *method, void *closure) {
    (void)closure;
    PyObject *name = PyObject_GetAttrString(method->function, "__name__");
    if (name == NULL) return NULL;
    if (!PyUnicode_Check(name)) return name;
    Py_ssize_t length = PyUnicode_GET_LENGTH(name);
    if (PyUnicode_CompareWithASCIIString(name, "bound_literal_findall") == 0 || PyUnicode_CompareWithASCIIString(name, "_literal_findall") == 0) {
        Py_DECREF(name);
        return PyUnicode_InternFromString("findall");
    }
    if (length > 6
        && PyUnicode_READ_CHAR(name, 0) == 'b'
        && PyUnicode_READ_CHAR(name, 1) == 'o'
        && PyUnicode_READ_CHAR(name, 2) == 'u'
        && PyUnicode_READ_CHAR(name, 3) == 'n'
        && PyUnicode_READ_CHAR(name, 4) == 'd'
        && PyUnicode_READ_CHAR(name, 5) == '_') {
        PyObject *result = PyUnicode_Substring(name, 6, length);
        Py_DECREF(name);
        return result;
    }
    return name;
}

static PyObject *rust_bound_get_qualname(RustBoundMethod *method, void *closure) {
    (void)closure;
    PyObject *name = rust_bound_get_name(method, NULL);
    if (name == NULL) return NULL;
    PyObject *result = PyUnicode_FromFormat("Pattern.%U", name);
    Py_DECREF(name);
    return result;
}

static PyObject *rust_bound_get_doc(RustBoundMethod *method, void *closure) {
    (void)closure;
    return PyObject_GetAttrString(method->function, "__doc__");
}

static PyObject *rust_bound_get_signature(RustBoundMethod *method, void *closure) {
    (void)closure;
    if (method->signature != NULL) return Py_NewRef(method->signature);
    PyObject *functools = PyImport_ImportModule("functools");
    if (functools == NULL) return NULL;
    PyObject *partial_type = PyObject_GetAttrString(functools, "partial");
    Py_DECREF(functools);
    if (partial_type == NULL) return NULL;
    Py_ssize_t count = Py_SIZE(method);
    PyObject *arguments = PyTuple_New(count + 1);
    if (arguments == NULL) {
        Py_DECREF(partial_type);
        return NULL;
    }
    PyTuple_SET_ITEM(arguments, 0, Py_NewRef(method->function));
    for (Py_ssize_t index = 0; index < count; index++) PyTuple_SET_ITEM(arguments, index + 1, Py_NewRef(method->prefix[index]));
    PyObject *partial = PyObject_CallObject(partial_type, arguments);
    Py_DECREF(arguments);
    Py_DECREF(partial_type);
    if (partial == NULL) return NULL;
    PyObject *inspect = PyImport_ImportModule("inspect");
    if (inspect == NULL) {
        Py_DECREF(partial);
        return NULL;
    }
    PyObject *signature_function = PyObject_GetAttrString(inspect, "signature");
    Py_DECREF(inspect);
    if (signature_function == NULL) {
        Py_DECREF(partial);
        return NULL;
    }
    PyObject *signature = PyObject_CallOneArg(signature_function, partial);
    Py_DECREF(signature_function);
    Py_DECREF(partial);
    if (signature == NULL) return NULL;
    method->signature = signature;
    return Py_NewRef(signature);
}

static PyObject *rust_bound_repr(RustBoundMethod *method) {
    PyObject *name = rust_bound_get_name(method, NULL);
    if (name == NULL) return NULL;
    PyObject *result = PyUnicode_FromFormat("<built-in method %U of re.Pattern object at %p>", name, (void *)method->pattern);
    Py_DECREF(name);
    return result;
}

static PyGetSetDef rust_bound_getsets[] = {
    {"__self__", (getter)rust_bound_get_self, NULL, "The bound regular-expression pattern.", NULL},
    {"__name__", (getter)rust_bound_get_name, NULL, "The public pattern method name.", NULL},
    {"__qualname__", (getter)rust_bound_get_qualname, NULL, "The qualified pattern method name.", NULL},
    {"__doc__", (getter)rust_bound_get_doc, NULL, "The bound pattern method documentation.", NULL},
    {"__signature__", (getter)rust_bound_get_signature, NULL, "The Python-compatible bound method signature.", NULL},
    {NULL, NULL, NULL, NULL, NULL},
};

static PyMemberDef rust_bound_members[] = {
    {
        "__vectorcalloffset__",
        Py_T_PYSSIZET,
        offsetof(RustBoundMethod, vectorcall),
        Py_READONLY,
        "Interpreter-local native vectorcall offset.",
    },
    {NULL, 0, 0, 0, NULL},
};

static PyType_Slot rust_bound_slots[] = {
    {Py_tp_dealloc, (void *)rust_bound_dealloc},
    {Py_tp_repr, (void *)rust_bound_repr},
    {Py_tp_call, (void *)PyVectorcall_Call},
    {Py_tp_doc, "Fresh, native-vectorcall bound Rust regular-expression method."},
    {Py_tp_members, rust_bound_members},
    {Py_tp_getset, rust_bound_getsets},
    {Py_tp_traverse, (void *)rust_bound_traverse},
    {Py_tp_clear, (void *)rust_bound_clear},
    {0, NULL},
};

static PyType_Spec rust_bound_spec = {
    .name = "re.builtin_method",
    .basicsize = (int)offsetof(RustBoundMethod, prefix),
    .itemsize = (int)sizeof(PyObject *),
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_VECTORCALL | Py_TPFLAGS_HAVE_GC,
    .slots = rust_bound_slots,
};

static PyObject *bridge_bind(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    RustBridgeState *state = rust_bridge_state_from_module(module);
    if (state == NULL) return NULL;
    if (nargs < 2) {
        PyErr_Format(PyExc_TypeError, "bind() requires a function and pattern (%zd arguments given)", nargs);
        return NULL;
    }
    if (!PyCallable_Check(args[0])) {
        PyErr_SetString(PyExc_TypeError, "Rust bound method requires a callable");
        return NULL;
    }
    PyObject *cached_prefix = nargs == 3 && PyTuple_Check(args[2]) ? args[2] : NULL;
    Py_ssize_t prefix = cached_prefix == NULL ? nargs - 2 : PyTuple_GET_SIZE(cached_prefix);
    RustBoundMethod *result = (RustBoundMethod *)PyType_GenericAlloc(
        state->bound_method_type, prefix
    );
    if (result == NULL) return NULL;
    result->function = Py_NewRef(args[0]);
    result->pattern = Py_NewRef(args[1]);
    result->vectorcall = rust_bound_call;
    for (Py_ssize_t index = 0; index < prefix; index++) {
        PyObject *value = cached_prefix == NULL ? args[index + 2] : PyTuple_GET_ITEM(cached_prefix, index);
        result->prefix[index] = Py_NewRef(value);
    }
    return (PyObject *)result;
}

static PyMethodDef bridge_methods[] = {
    {"compile", (PyCFunction)(void (*)(void))bridge_compile, METH_FASTCALL, "Compile a from-scratch Rust regular expression in one native call."},
    {"compile_scanner", (PyCFunction)(void (*)(void))bridge_compile_scanner, METH_FASTCALL, "Compile independently parsed scanner phrases into one owned Rust regular expression."},
    {"free", (PyCFunction)bridge_free, METH_O, "Free a compiled Rust regular expression."},
    {"error", (PyCFunction)bridge_error, METH_NOARGS, "Return the most recent Rust compilation error."},
    {"set_template", (PyCFunction)bridge_set_template, METH_O, "Configure the compatible Rust match-template expander."},
    {"bind", (PyCFunction)(void (*)(void))bridge_bind, METH_FASTCALL, "bind($module, function, pattern, /, *prefix)\n--\n\nCreate a fresh native-vectorcall bound regular-expression method."},
    {"pattern_type", (PyCFunction)bridge_pattern_type, METH_O,
     "pattern_type($module, pattern_base, /)\n--\n\n"
     "Create the native public regular-expression pattern type."},
    {"pattern_descriptors", (PyCFunction)bridge_pattern_descriptors, METH_O,
     "pattern_descriptors($module, pattern_type, /)\n--\n\n"
     "Create native regular-expression pattern method descriptors."},
    {"pattern_match", (PyCFunction)(void (*)(void))bridge_pattern_match, METH_FASTCALL, "Run Rust and create a native match in one call."},
    {"bound_search", (PyCFunction)(void (*)(void))bridge_bound_search, METH_FASTCALL | METH_KEYWORDS, "bound_search($module, pattern, handle, groupindex, pattern_value, literal, string, pos=0, endpos=9223372036854775807)\n--\n\nSearch with a compiled Rust pattern."},
    {"bound_match", (PyCFunction)(void (*)(void))bridge_bound_match, METH_FASTCALL | METH_KEYWORDS, "bound_match($module, pattern, handle, groupindex, pattern_value, literal, string, pos=0, endpos=9223372036854775807)\n--\n\nMatch at the start with a compiled Rust pattern."},
    {"bound_fullmatch", (PyCFunction)(void (*)(void))bridge_bound_fullmatch, METH_FASTCALL | METH_KEYWORDS, "bound_fullmatch($module, pattern, handle, groupindex, pattern_value, literal, string, pos=0, endpos=9223372036854775807)\n--\n\nMatch a complete window with a compiled Rust pattern."},
    {"bound_findall", (PyCFunction)(void (*)(void))bridge_bound_findall, METH_FASTCALL | METH_KEYWORDS, "bound_findall($module, handle, pattern_value, groups, string, pos=0, endpos=9223372036854775807)\n--\n\nCollect all compiled Rust pattern matches."},
    {"bound_literal_findall", (PyCFunction)(void (*)(void))bridge_bound_literal_findall, METH_FASTCALL | METH_KEYWORDS, "bound_literal_findall($module, literal, string, pos=0, endpos=9223372036854775807)\n--\n\nCollect all exact literal matches in one native call."},
    {"bound_finditer", (PyCFunction)(void (*)(void))bridge_bound_finditer, METH_FASTCALL | METH_KEYWORDS, "bound_finditer($module, pattern, handle, groupindex, pattern_value, groups, string, pos=0, endpos=9223372036854775807)\n--\n\nCreate a lazy Rust regex match iterator."},
    {"bound_scanner", (PyCFunction)(void (*)(void))bridge_bound_scanner, METH_FASTCALL | METH_KEYWORDS, "bound_scanner($module, pattern, handle, groupindex, pattern_value, groups, string, pos=0, endpos=9223372036854775807)\n--\n\nCreate a Rust regex scanner."},
    {"bound_split", (PyCFunction)(void (*)(void))bridge_bound_split, METH_FASTCALL | METH_KEYWORDS, "bound_split($module, handle, pattern_value, groups, string, maxsplit=0)\n--\n\nSplit around Rust regex matches in one native call."},
    {"bound_sub", (PyCFunction)(void (*)(void))bridge_bound_sub, METH_FASTCALL | METH_KEYWORDS, "bound_sub($module, pattern, handle, groupindex, pattern_value, literal, templates, groups, repl, string, count=0)\n--\n\nSubstitute Rust regex matches in one native call."},
    {"bound_subn", (PyCFunction)(void (*)(void))bridge_bound_subn, METH_FASTCALL | METH_KEYWORDS, "bound_subn($module, pattern, handle, groupindex, pattern_value, literal, templates, groups, repl, string, count=0)\n--\n\nSubstitute Rust regex matches and return the replacement count."},
    {"run", (PyCFunction)(void (*)(void))bridge_run, METH_FASTCALL, "Run one Rust regular-expression match."},
    {"collect", (PyCFunction)(void (*)(void))bridge_collect, METH_FASTCALL, "Collect non-overlapping Rust regular-expression matches."},
    {"findall", (PyCFunction)(void (*)(void))bridge_findall, METH_FASTCALL, "Return all Rust regular-expression matches as Python values."},
    {NULL, NULL, 0, NULL},
};

static int rust_bridge_traverse(PyObject *module, visitproc visit, void *arg) {
    RustBridgeState *state = (RustBridgeState *)PyModule_GetState(module);
    if (state == NULL) return 0;
    Py_VISIT(state->match_type);
    Py_VISIT(state->iterator_type);
    Py_VISIT(state->scanner_type);
    Py_VISIT(state->bound_method_type);
    Py_VISIT(state->template_helper);
    Py_VISIT(state->generic_alias_factory);
    for (size_t index = 0; index < RUST_PATTERN_ATTRIBUTE_COUNT; index++) {
        Py_VISIT(state->pattern_attribute_names[index]);
    }
#ifndef Py_GIL_DISABLED
    Py_VISIT(state->primary_pattern_type);
#endif
    return 0;
}

static int rust_bridge_clear(PyObject *module) {
    RustBridgeState *state = (RustBridgeState *)PyModule_GetState(module);
    if (state == NULL) return 0;
#ifndef Py_GIL_DISABLED
    memset(&state->pattern_slot_cache, 0, sizeof(state->pattern_slot_cache));
    Py_CLEAR(state->primary_pattern_type);
#endif
    Py_CLEAR(state->template_helper);
    Py_CLEAR(state->generic_alias_factory);
    for (size_t index = 0; index < RUST_PATTERN_ATTRIBUTE_COUNT; index++) {
        Py_CLEAR(state->pattern_attribute_names[index]);
    }
    Py_CLEAR(state->match_type);
    Py_CLEAR(state->iterator_type);
    Py_CLEAR(state->scanner_type);
    Py_CLEAR(state->bound_method_type);
    return 0;
}

static void rust_bridge_free_module(void *module) {
    (void)rust_bridge_clear((PyObject *)module);
}

static int rust_bridge_exec(PyObject *module) {
    RustBridgeState *state = rust_bridge_state_from_module(module);
    if (state == NULL) return -1;
    if (
        state->match_type != NULL
        || state->iterator_type != NULL
        || state->scanner_type != NULL
        || state->bound_method_type != NULL
    ) {
        PyErr_SetString(
            PyExc_SystemError,
            "Rust regex bridge interpreter state was already initialized"
        );
        return -1;
    }
    if (rust_initialize_pattern_attribute_names(state) < 0) return -1;

    state->match_type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module, &rust_match_spec, NULL
    );
    if (state->match_type == NULL) return -1;
    state->iterator_type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module, &rust_iterator_spec, NULL
    );
    if (state->iterator_type == NULL) return -1;
    state->scanner_type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module, &rust_scanner_spec, NULL
    );
    if (state->scanner_type == NULL) return -1;
    state->bound_method_type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module, &rust_bound_spec, NULL
    );
    if (state->bound_method_type == NULL) return -1;

    if (
        PyModule_AddObjectRef(
            module, "Match", (PyObject *)state->match_type
        ) < 0
    ) {
        return -1;
    }
    return 0;
}

static PyModuleDef_Slot rust_bridge_slots[] = {
    {Py_mod_exec, (void *)rust_bridge_exec},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {Py_mod_gil, Py_MOD_GIL_USED},
    {0, NULL},
};

static struct PyModuleDef bridge_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_rust_bridge",
    .m_doc = "Dependency-free CPython bridge for the from-scratch Rust regex engine.",
    .m_size = (Py_ssize_t)sizeof(RustBridgeState),
    .m_methods = bridge_methods,
    .m_slots = rust_bridge_slots,
    .m_traverse = rust_bridge_traverse,
    .m_clear = rust_bridge_clear,
    .m_free = rust_bridge_free_module,
};

PyMODINIT_FUNC PyInit__rust_bridge(void) {
    return PyModuleDef_Init(&bridge_module);
}
