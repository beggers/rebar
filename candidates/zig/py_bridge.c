#define _GNU_SOURCE
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stddef.h>
#include <stdint.h>

extern int rebar_zig_match_wide(const void *, const uint8_t *, size_t, uint8_t, size_t, size_t, uint8_t, intptr_t *, intptr_t *);
extern void *rebar_zig_compile(const uint8_t *, size_t, uint32_t);
extern void rebar_zig_free(void *);
extern int rebar_zig_match_nonempty_wide(const void *, const uint8_t *, size_t, uint8_t, size_t, size_t, uint8_t, uint8_t, intptr_t *, intptr_t *);
extern size_t rebar_zig_groups(const void *);
extern uint32_t rebar_zig_flags(const void *);
extern size_t rebar_zig_name_count(const void *);
extern size_t rebar_zig_name_length(const void *, size_t);
extern size_t rebar_zig_name_group(const void *, size_t);
extern size_t rebar_zig_name_copy(const void *, size_t, uint8_t *, size_t);
extern int rebar_zig_match_captures_wide(const void *, const uint8_t *, size_t, uint8_t, size_t, size_t, uint8_t, uint8_t, intptr_t *, intptr_t *, intptr_t *);
extern int rebar_zig_match_inverted_wide(const void *, const uint8_t *, size_t, uint8_t, size_t, size_t, uint8_t, intptr_t *, intptr_t *, intptr_t *);
extern intptr_t rebar_zig_collect_records_wide(const void *, const uint8_t *, size_t, uint8_t, size_t, size_t, intptr_t *, size_t *, uint8_t *);

#define ZIG_LOCAL_CAPTURE_WORDS 1024
#define ZIG_ITERATOR_RECORD_WORDS 64
#define ZIG_INITIAL_CAPTURE_COUNT 64

typedef struct {
    intptr_t local[ZIG_LOCAL_CAPTURE_WORDS];
    intptr_t *storage;
    size_t stride;
    size_t words_per_match;
} ZigCaptureBuffer;

typedef struct {
    PyObject_VAR_HEAD
    PyObject *pattern;
    PyObject *string;
    PyObject *groupindex;
    PyObject *regs;
    Py_ssize_t groups;
    Py_ssize_t pos;
    Py_ssize_t endpos;
    Py_ssize_t lastindex;
    intptr_t spans[];
} ZigMatch;

typedef struct {
    PyObject_HEAD
    PyObject *pattern;
    PyObject *string;
    PyObject *groupindex;
    const void *handle;
    const uint8_t *data;
    size_t groups;
    size_t length;
    size_t cursor;
    size_t endpos;
    size_t original_pos;
    uint8_t kind;
    uint8_t nonempty;
    uint8_t done;
    Py_buffer view;
    intptr_t records[ZIG_ITERATOR_RECORD_WORDS];
    intptr_t *record_heap;
    size_t record_at;
    size_t record_count;
} ZigIterator;

static PyTypeObject ZigMatchType;
static PyTypeObject ZigIteratorType;
static PyTypeObject ZigScannerType;
static PyObject *zig_default_endpos;
static PyObject *zig_span(intptr_t begin, intptr_t finish);

static ZigMatch *zig_match_new(PyObject *pattern, PyObject *string, PyObject *groupindex, size_t groups, Py_ssize_t pos, Py_ssize_t endpos) {
    if (groups > (size_t)PY_SSIZE_T_MAX / 2 - 1) {
        PyErr_NoMemory();
        return NULL;
    }
    size_t stride = groups + 1;
    ZigMatch *match = (ZigMatch *)PyType_GenericAlloc(&ZigMatchType, (Py_ssize_t)(stride * 2));
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

static int zig_match_number(ZigMatch *match, PyObject *value, Py_ssize_t *number) {
    if (PyUnicode_Check(value)) {
        PyObject *item = PyDict_Check(match->groupindex) ? PyDict_GetItemWithError(match->groupindex, value) : PyObject_GetItem(match->groupindex, value);
        if (item == NULL) {
            PyErr_Clear();
            PyErr_SetString(PyExc_IndexError, "no such group");
            return 0;
        }
        *number = PyLong_AsSsize_t(item);
        if (!PyDict_Check(match->groupindex)) Py_DECREF(item);
    } else {
        PyObject *item = PyNumber_Index(value);
        if (item == NULL) {
            if (!PyErr_ExceptionMatches(PyExc_TypeError) ||
                (Py_TYPE(value)->tp_as_number != NULL &&
                 Py_TYPE(value)->tp_as_number->nb_index != NULL)) {
                return 0;
            }
            PyErr_Clear();
            PyErr_SetString(PyExc_IndexError, "no such group");
            return 0;
        }
        *number = PyLong_AsSsize_t(item);
        Py_DECREF(item);
    }
    if (PyErr_Occurred() || *number < 0 || *number > match->groups) {
        PyErr_Clear();
        PyErr_SetString(PyExc_IndexError, "no such group");
        return 0;
    }
    return 1;
}

static PyObject *zig_bytes_piece(PyObject *subject, const uint8_t *data,
                                 size_t length, size_t first, size_t last) {
    if (PyBytes_CheckExact(subject) && first == 0 && last == length) {
        return Py_NewRef(subject);
    }
    return PyBytes_FromStringAndSize((const char *)data + first,
                                     (Py_ssize_t)(last - first));
}

static PyObject *zig_match_piece(ZigMatch *match, Py_ssize_t group, PyObject *missing) {
    size_t stride = (size_t)match->groups + 1;
    intptr_t begin = match->spans[group];
    intptr_t finish = match->spans[stride + (size_t)group];
    if (begin < 0) return Py_NewRef(missing);
    if (PyUnicode_Check(match->string)) return PyUnicode_Substring(match->string, (Py_ssize_t)begin, (Py_ssize_t)finish);
    Py_buffer view = {0};
    if (PyObject_GetBuffer(match->string, &view, PyBUF_SIMPLE) != 0) return NULL;
    Py_ssize_t first = begin < 0 ? 0 : (Py_ssize_t)begin;
    Py_ssize_t last = finish < 0 ? 0 : (Py_ssize_t)finish;
    if (first > view.len) first = view.len;
    if (last > view.len) last = view.len;
    if (last < first) last = first;
    PyObject *result = zig_bytes_piece(match->string, (const uint8_t *)view.buf,
                                      (size_t)view.len, (size_t)first, (size_t)last);
    PyBuffer_Release(&view);
    return result;
}

static PyObject *zig_match_group(ZigMatch *match, PyObject *const *args, Py_ssize_t count) {
    if (count == 0) return zig_match_piece(match, 0, Py_None);
    if (count == 1) {
        Py_ssize_t group;
        if (!zig_match_number(match, args[0], &group)) return NULL;
        return zig_match_piece(match, group, Py_None);
    }
    PyObject *result = PyTuple_New(count);
    if (result == NULL) return NULL;
    for (Py_ssize_t index = 0; index < count; index++) {
        Py_ssize_t group;
        if (!zig_match_number(match, args[index], &group)) {
            Py_DECREF(result);
            return NULL;
        }
        PyObject *item = zig_match_piece(match, group, Py_None);
        if (item == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        PyTuple_SET_ITEM(result, index, item);
    }
    return result;
}

static PyObject *zig_match_groups(ZigMatch *match, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    PyObject *missing = Py_None;
    Py_ssize_t keywords = kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    if (keywords > 1) {
        PyErr_Format(PyExc_TypeError, "groups() takes at most 1 keyword argument (%zd given)", keywords);
        return NULL;
    }
    if (nargs + keywords > 1) {
        PyErr_Format(PyExc_TypeError, "groups() takes at most 1 argument (%zd given)", nargs + keywords);
        return NULL;
    }
    if (keywords != 0) {
        PyObject *name = PyTuple_GET_ITEM(kwnames, 0);
        if (PyUnicode_CompareWithASCIIString(name, "default") != 0) {
            PyErr_Format(PyExc_TypeError, "groups() got an unexpected keyword argument '%U'", name);
            return NULL;
        }
        missing = args[nargs];
    } else if (nargs != 0) missing = args[0];
    PyObject *result = PyTuple_New(match->groups);
    if (result == NULL) return NULL;
    for (Py_ssize_t group = 1; group <= match->groups; group++) {
        PyObject *item = zig_match_piece(match, group, missing);
        if (item == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        PyTuple_SET_ITEM(result, group - 1, item);
    }
    return result;
}

static PyObject *zig_match_groupdict(ZigMatch *match, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    PyObject *missing = Py_None;
    Py_ssize_t keywords = kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    if (keywords > 1) {
        PyErr_Format(PyExc_TypeError, "groupdict() takes at most 1 keyword argument (%zd given)", keywords);
        return NULL;
    }
    if (nargs + keywords > 1) {
        PyErr_Format(PyExc_TypeError, "groupdict() takes at most 1 argument (%zd given)", nargs + keywords);
        return NULL;
    }
    if (keywords != 0) {
        PyObject *name = PyTuple_GET_ITEM(kwnames, 0);
        if (PyUnicode_CompareWithASCIIString(name, "default") != 0) {
            PyErr_Format(PyExc_TypeError, "groupdict() got an unexpected keyword argument '%U'", name);
            return NULL;
        }
        missing = args[nargs];
    } else if (nargs != 0) missing = args[0];
    PyObject *result = PyDict_New();
    if (result == NULL) return NULL;
    if (PyDict_Check(match->groupindex)) {
        PyObject *name;
        PyObject *number;
        Py_ssize_t cursor = 0;
        while (PyDict_Next(match->groupindex, &cursor, &name, &number)) {
            Py_ssize_t group = PyLong_AsSsize_t(number);
            PyObject *value = PyErr_Occurred() ? NULL : zig_match_piece(match, group, missing);
            if (value == NULL || PyDict_SetItem(result, name, value) < 0) {
                Py_XDECREF(value);
                Py_DECREF(result);
                return NULL;
            }
            Py_DECREF(value);
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
        PyObject *value = PyErr_Occurred() ? NULL : zig_match_piece(match, group, missing);
        if (value == NULL || PyDict_SetItem(result, name, value) < 0) {
            Py_XDECREF(value);
            Py_DECREF(result);
            Py_DECREF(items);
            return NULL;
        }
        Py_DECREF(value);
    }
    Py_DECREF(items);
    return result;
}

static PyObject *zig_match_bound(ZigMatch *match, PyObject *const *args, Py_ssize_t nargs, int which, const char *name) {
    Py_ssize_t group = 0;
    if (nargs > 1) {
        PyErr_Format(PyExc_TypeError, "%s expected at most 1 argument, got %zd", name, nargs);
        return NULL;
    }
    if (nargs != 0 && !zig_match_number(match, args[0], &group)) return NULL;
    size_t stride = (size_t)match->groups + 1;
    intptr_t begin = match->spans[group];
    intptr_t finish = match->spans[stride + (size_t)group];
    if (which == 0) return PyLong_FromSsize_t(begin < 0 ? -1 : (Py_ssize_t)begin);
    if (which == 1) return PyLong_FromSsize_t(begin < 0 ? -1 : (Py_ssize_t)finish);
    return zig_span(begin < 0 ? -1 : begin, begin < 0 ? -1 : finish);
}

static PyObject *zig_match_start(ZigMatch *match, PyObject *const *args, Py_ssize_t nargs) { return zig_match_bound(match, args, nargs, 0, "start"); }
static PyObject *zig_match_end(ZigMatch *match, PyObject *const *args, Py_ssize_t nargs) { return zig_match_bound(match, args, nargs, 1, "end"); }
static PyObject *zig_match_span(ZigMatch *match, PyObject *const *args, Py_ssize_t nargs) { return zig_match_bound(match, args, nargs, 2, "span"); }

static PyObject *zig_match_expand(ZigMatch *match, PyObject *value) {
    PyObject *raw = value;
    PyObject *owned = NULL;
    if (PyByteArray_Check(value) || PyMemoryView_Check(value)) {
        owned = PyBytes_FromObject(value);
        if (owned == NULL) return NULL;
        raw = owned;
    }
    PyObject *templates = PyObject_GetAttrString(match->pattern, "_templates");
    if (templates == NULL) {
        Py_XDECREF(owned);
        return NULL;
    }
    PyObject *parts = PyDict_Check(templates) ? PyDict_GetItemWithError(templates, raw) : NULL;
    if (parts == NULL && PyErr_Occurred()) {
        Py_DECREF(templates);
        Py_XDECREF(owned);
        return NULL;
    }
    if (parts == NULL) {
        Py_DECREF(templates);
        Py_XDECREF(owned);
        return PyObject_CallMethod(match->pattern, "_expand", "OO", value, (PyObject *)match);
    }
    int byte_mode = PyBytes_Check(raw);
    Py_ssize_t count = PyTuple_GET_SIZE(parts);
    if (!byte_mode && PyUnicode_Check(match->string)) {
        PyUnicodeWriter *writer = PyUnicodeWriter_Create(16);
        if (writer == NULL) {
            Py_DECREF(templates);
            Py_XDECREF(owned);
            return NULL;
        }
        size_t stride = (size_t)match->groups + 1;
        for (Py_ssize_t index = 0; index < count; index++) {
            PyObject *part = PyTuple_GET_ITEM(parts, index);
            int written;
            if (PyLong_Check(part)) {
                Py_ssize_t group = PyLong_AsSsize_t(part);
                intptr_t begin = match->spans[group];
                intptr_t finish = match->spans[stride + (size_t)group];
                written = begin < 0 ? 0 : PyUnicodeWriter_WriteSubstring(writer, match->string, (Py_ssize_t)begin, (Py_ssize_t)finish);
            } else written = PyUnicodeWriter_WriteStr(writer, part);
            if (written < 0) {
                PyUnicodeWriter_Discard(writer);
                Py_DECREF(templates);
                Py_XDECREF(owned);
                return NULL;
            }
        }
        PyObject *result = PyUnicodeWriter_Finish(writer);
        Py_DECREF(templates);
        Py_XDECREF(owned);
        return result;
    }
    PyObject *pieces = PyList_New(count);
    if (pieces == NULL) {
        Py_DECREF(templates);
        Py_XDECREF(owned);
        return NULL;
    }
    for (Py_ssize_t index = 0; index < count; index++) {
        PyObject *part = PyTuple_GET_ITEM(parts, index);
        PyObject *item;
        if (PyLong_Check(part)) {
            Py_ssize_t group = PyLong_AsSsize_t(part);
            item = zig_match_piece(match, group, Py_None);
            if (item == Py_None) Py_SETREF(item, byte_mode ? PyBytes_FromStringAndSize("", 0) : PyUnicode_New(0, 127));
        } else item = Py_NewRef(part);
        if (item == NULL) {
            Py_DECREF(pieces);
            Py_DECREF(templates);
            Py_XDECREF(owned);
            return NULL;
        }
        PyList_SET_ITEM(pieces, index, item);
    }
    PyObject *empty = byte_mode ? PyBytes_FromStringAndSize("", 0) : PyUnicode_New(0, 127);
    PyObject *result = empty == NULL ? NULL : (byte_mode ? PyBytes_Join(empty, pieces) : PyUnicode_Join(empty, pieces));
    Py_XDECREF(empty);
    Py_DECREF(pieces);
    Py_DECREF(templates);
    Py_XDECREF(owned);
    return result;
}

static PyObject *zig_match_copy(ZigMatch *match, PyObject *ignored) { (void)ignored; return Py_NewRef(match); }
static PyObject *zig_match_deepcopy(ZigMatch *match, PyObject *memo) { (void)memo; return Py_NewRef(match); }
static PyObject *zig_match_reduce(ZigMatch *match, PyObject *ignored) { (void)match; (void)ignored; PyErr_SetString(PyExc_TypeError, "cannot pickle 're.Match' object"); return NULL; }
static PyObject *zig_match_class_getitem(PyObject *type, PyObject *item) { return Py_GenericAlias(type, item); }

static PyObject *zig_match_repr(ZigMatch *match) {
    PyObject *value = zig_match_piece(match, 0, Py_None);
    if (value == NULL) return NULL;
    size_t stride = (size_t)match->groups + 1;
    PyObject *result = PyUnicode_FromFormat("<re.Match object; span=(%zd, %zd), match=%.50R>", (Py_ssize_t)match->spans[0], (Py_ssize_t)match->spans[stride], value);
    Py_DECREF(value);
    return result;
}

static PyObject *zig_match_subscript(PyObject *value, PyObject *key) {
    ZigMatch *match = (ZigMatch *)value;
    Py_ssize_t group;
    if (!zig_match_number(match, key, &group)) return NULL;
    return zig_match_piece(match, group, Py_None);
}

static PyObject *zig_match_get_re(ZigMatch *match, void *closure) { (void)closure; return Py_NewRef(match->pattern); }
static PyObject *zig_match_get_string(ZigMatch *match, void *closure) { (void)closure; return Py_NewRef(match->string); }
static PyObject *zig_match_get_pos(ZigMatch *match, void *closure) { (void)closure; return PyLong_FromSsize_t(match->pos); }
static PyObject *zig_match_get_endpos(ZigMatch *match, void *closure) { (void)closure; return PyLong_FromSsize_t(match->endpos); }
static PyObject *zig_match_get_lastindex(ZigMatch *match, void *closure) { (void)closure; return match->lastindex < 0 ? Py_NewRef(Py_None) : PyLong_FromSsize_t(match->lastindex); }

static PyObject *zig_match_get_lastgroup(ZigMatch *match, void *closure) {
    (void)closure;
    if (match->lastindex < 0) Py_RETURN_NONE;
    if (PyDict_Check(match->groupindex)) {
        PyObject *name;
        PyObject *number;
        Py_ssize_t cursor = 0;
        while (PyDict_Next(match->groupindex, &cursor, &name, &number)) {
            if (PyLong_AsSsize_t(number) == match->lastindex) return Py_NewRef(name);
        }
        Py_RETURN_NONE;
    }
    PyObject *items = PyMapping_Items(match->groupindex);
    if (items == NULL) return NULL;
    Py_ssize_t count = PyList_GET_SIZE(items);
    for (Py_ssize_t index = 0; index < count; index++) {
        PyObject *pair = PyList_GET_ITEM(items, index);
        if (PyLong_AsSsize_t(PyTuple_GET_ITEM(pair, 1)) == match->lastindex) {
            PyObject *result = Py_NewRef(PyTuple_GET_ITEM(pair, 0));
            Py_DECREF(items);
            return result;
        }
    }
    Py_DECREF(items);
    Py_RETURN_NONE;
}

static PyObject *zig_match_spans(ZigMatch *match, int missing_none) {
    size_t stride = (size_t)match->groups + 1;
    PyObject *result = PyTuple_New((Py_ssize_t)stride);
    if (result == NULL) return NULL;
    for (size_t group = 0; group < stride; group++) {
        intptr_t begin = match->spans[group];
        intptr_t finish = match->spans[stride + group];
        PyObject *item = begin < 0 && missing_none ? Py_NewRef(Py_None) : zig_span(begin < 0 ? -1 : begin, begin < 0 ? -1 : finish);
        if (item == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        PyTuple_SET_ITEM(result, (Py_ssize_t)group, item);
    }
    return result;
}

static PyObject *zig_match_get_regs(ZigMatch *match, void *closure) {
    (void)closure;
    if (match->regs == NULL) {
        match->regs = zig_match_spans(match, 0);
        if (match->regs == NULL) return NULL;
    }
    return Py_NewRef(match->regs);
}
static PyObject *zig_match_get_private_spans(ZigMatch *match, void *closure) { (void)closure; return zig_match_spans(match, 1); }
static PyObject *zig_match_get_private_last(ZigMatch *match, void *closure) { return zig_match_get_lastindex(match, closure); }

static int zig_match_traverse(ZigMatch *match, visitproc visit, void *arg) {
    Py_VISIT(match->pattern);
    Py_VISIT(match->string);
    Py_VISIT(match->groupindex);
    Py_VISIT(match->regs);
    return 0;
}

static int zig_match_clear(ZigMatch *match) {
    Py_CLEAR(match->pattern);
    Py_CLEAR(match->string);
    Py_CLEAR(match->groupindex);
    Py_CLEAR(match->regs);
    return 0;
}

static void zig_match_dealloc(ZigMatch *match) {
    PyObject_GC_UnTrack(match);
    zig_match_clear(match);
    Py_TYPE(match)->tp_free((PyObject *)match);
}

static int zig_match_readonly(PyObject *match, PyObject *value, void *closure) {
    (void)match;
    (void)value;
    (void)closure;
    PyErr_SetString(PyExc_AttributeError, "readonly attribute");
    return -1;
}

static PyMethodDef zig_match_methods[] = {
    {"group", (PyCFunction)(void (*)(void))zig_match_group, METH_FASTCALL, "Return one or more captured groups."},
    {"groups", (PyCFunction)(void (*)(void))zig_match_groups, METH_FASTCALL | METH_KEYWORDS, "groups($self, /, default=None)\n--\n\nReturn all captured groups."},
    {"groupdict", (PyCFunction)(void (*)(void))zig_match_groupdict, METH_FASTCALL | METH_KEYWORDS, "groupdict($self, /, default=None)\n--\n\nReturn named captured groups."},
    {"start", (PyCFunction)(void (*)(void))zig_match_start, METH_FASTCALL, "start($self, group=0, /)\n--\n\nReturn the start of a group."},
    {"end", (PyCFunction)(void (*)(void))zig_match_end, METH_FASTCALL, "end($self, group=0, /)\n--\n\nReturn the end of a group."},
    {"span", (PyCFunction)(void (*)(void))zig_match_span, METH_FASTCALL, "span($self, group=0, /)\n--\n\nReturn a group span."},
    {"expand", (PyCFunction)zig_match_expand, METH_O, "expand($self, /, template)\n--\n\nExpand a replacement template."},
    {"__copy__", (PyCFunction)zig_match_copy, METH_NOARGS, "Return the immutable match."},
    {"__deepcopy__", (PyCFunction)zig_match_deepcopy, METH_O, "Return the immutable match."},
    {"__reduce__", (PyCFunction)zig_match_reduce, METH_NOARGS, "Matches cannot be pickled."},
    {"__reduce_ex__", (PyCFunction)zig_match_reduce, METH_O, "Matches cannot be pickled."},
    {"__class_getitem__", (PyCFunction)zig_match_class_getitem, METH_O | METH_CLASS, "Return a generic match alias."},
    {NULL, NULL, 0, NULL},
};

static PyGetSetDef zig_match_getsets[] = {
    {"re", (getter)zig_match_get_re, zig_match_readonly, "Compiled pattern.", NULL},
    {"string", (getter)zig_match_get_string, zig_match_readonly, "Input string.", NULL},
    {"pos", (getter)zig_match_get_pos, zig_match_readonly, "Search start.", NULL},
    {"endpos", (getter)zig_match_get_endpos, zig_match_readonly, "Search end.", NULL},
    {"lastindex", (getter)zig_match_get_lastindex, NULL, "Last matched group index.", NULL},
    {"lastgroup", (getter)zig_match_get_lastgroup, NULL, "Last matched group name.", NULL},
    {"regs", (getter)zig_match_get_regs, NULL, "Captured spans.", NULL},
    {"_spans", (getter)zig_match_get_private_spans, NULL, "Internal captured spans.", NULL},
    {"_lastindex", (getter)zig_match_get_private_last, NULL, "Internal last group index.", NULL},
    {NULL, NULL, NULL, NULL, NULL},
};

static PyMappingMethods zig_match_mapping = {0, zig_match_subscript, 0};

static PyTypeObject ZigMatchType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "re.Match",
    .tp_basicsize = offsetof(ZigMatch, spans),
    .tp_itemsize = sizeof(intptr_t),
    .tp_dealloc = (destructor)zig_match_dealloc,
    .tp_repr = (reprfunc)zig_match_repr,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .tp_doc = "Capture-aware Zig regular expression match.",
    .tp_traverse = (traverseproc)zig_match_traverse,
    .tp_clear = (inquiry)zig_match_clear,
    .tp_methods = zig_match_methods,
    .tp_getset = zig_match_getsets,
    .tp_as_mapping = &zig_match_mapping,
};

static PyObject *zig_span(intptr_t begin, intptr_t finish) {
    PyObject *item = PyTuple_New(2);
    if (item == NULL) return NULL;
    PyObject *left = PyLong_FromSsize_t((Py_ssize_t)begin);
    PyObject *right = PyLong_FromSsize_t((Py_ssize_t)finish);
    if (left == NULL || right == NULL) {
        Py_XDECREF(left);
        Py_XDECREF(right);
        Py_DECREF(item);
        return NULL;
    }
    PyTuple_SET_ITEM(item, 0, left);
    PyTuple_SET_ITEM(item, 1, right);
    return item;
}

static void zig_capture_release(ZigCaptureBuffer *buffer) {
    if (buffer->storage != NULL && buffer->storage != buffer->local) PyMem_Free(buffer->storage);
    buffer->storage = NULL;
}

/*
 * Start with a small stack-backed capture buffer and grow only when the
 * matcher fills it. Records are append-only and matching resumes at the
 * exact cursor/empty-retry state, so dense calls never rescan prior input.
 */
static intptr_t zig_collect_growing(const void *handle, const uint8_t *data, size_t length, uint8_t kind,
                                    size_t pos, size_t end, size_t groups, size_t limit,
                                    ZigCaptureBuffer *buffer) {
    buffer->storage = NULL;
    if (end < pos) return 0;
    size_t range = end - pos;
    if (range > (SIZE_MAX - 1) / 2 || groups == SIZE_MAX) return -2;
    size_t maximum = range * 2 + 1;
    if (limit != 0 && limit < maximum) maximum = limit;
    size_t stride = groups + 1;
    if (stride > (SIZE_MAX - 1) / 2) return -2;
    size_t words_per_match = stride * 2 + 1;
    size_t capacity = maximum < ZIG_INITIAL_CAPTURE_COUNT ? maximum : ZIG_INITIAL_CAPTURE_COUNT;
    if (capacity == 0) return 0;
    size_t used = 0;
    size_t cursor = pos;
    uint8_t retry_nonempty = 0;
    buffer->stride = stride;
    buffer->words_per_match = words_per_match;
    while (1) {
        if (capacity > SIZE_MAX / words_per_match || capacity * words_per_match > SIZE_MAX / sizeof(intptr_t)) return -2;
        size_t words = capacity * words_per_match;
        if (buffer->storage == NULL) {
            buffer->storage = words <= ZIG_LOCAL_CAPTURE_WORDS ? buffer->local : PyMem_Malloc(words * sizeof(intptr_t));
            if (buffer->storage == NULL) return -2;
        } else if (buffer->storage == buffer->local && words > ZIG_LOCAL_CAPTURE_WORDS) {
            intptr_t *storage = PyMem_Malloc(words * sizeof(intptr_t));
            if (storage == NULL) return -2;
            memcpy(storage, buffer->local, used * words_per_match * sizeof(intptr_t));
            buffer->storage = storage;
        } else if (buffer->storage != buffer->local) {
            intptr_t *storage = PyMem_Realloc(buffer->storage, words * sizeof(intptr_t));
            if (storage == NULL) {
                zig_capture_release(buffer);
                return -2;
            }
            buffer->storage = storage;
        }
        intptr_t count = rebar_zig_collect_records_wide(handle, data, length, kind, end, capacity - used, buffer->storage + used * words_per_match, &cursor, &retry_nonempty);
        if (count < 0) {
            zig_capture_release(buffer);
            return -1;
        }
        used += (size_t)count;
        if (used < capacity || capacity == maximum) return (intptr_t)used;
        capacity = capacity > maximum / 4 ? maximum : capacity * 4;
    }
}

static PyObject *bridge_match_object(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 9) {
        PyErr_Format(PyExc_TypeError, "match_object() takes exactly 9 arguments (%zd given)", nargs);
        return NULL;
    }
    PyObject *pattern = args[0];
    void *handle = PyLong_AsVoidPtr(args[1]);
    PyObject *groupindex = args[2];
    PyObject *subject = args[3];
    size_t pos = PyLong_AsSize_t(args[4]);
    size_t endpos = PyLong_AsSize_t(args[5]);
    unsigned long mode = PyLong_AsUnsignedLong(args[6]);
    int nonempty = PyObject_IsTrue(args[7]);
    Py_ssize_t original = PyLong_AsSsize_t(args[8]);
    if (PyErr_Occurred() || mode > UINT8_MAX || nonempty < 0) {
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_OverflowError, "invalid Zig match-object argument");
        return NULL;
    }
    Py_buffer view = {0};
    const uint8_t *data;
    size_t length;
    uint8_t kind = 1;
    if (PyUnicode_Check(subject)) {
        data = PyUnicode_DATA(subject);
        length = (size_t)PyUnicode_GET_LENGTH(subject);
        kind = (uint8_t)PyUnicode_KIND(subject);
    } else {
        if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) return NULL;
        data = view.buf;
        length = (size_t)view.len;
    }
    size_t groups = rebar_zig_groups(handle);
    size_t stride = groups + 1;
    size_t end = endpos < length ? endpos : length;
    ZigMatch *match = zig_match_new(pattern, subject, groupindex, groups, original, (Py_ssize_t)end);
    if (match == NULL) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        return NULL;
    }
    int result;
    if (groups == 0) result = rebar_zig_match_nonempty_wide(handle, data, length, kind, pos, end, (uint8_t)mode, (uint8_t)nonempty, &match->spans[0], &match->spans[stride]);
    else result = rebar_zig_match_captures_wide(handle, data, length, kind, pos, end, (uint8_t)mode, (uint8_t)nonempty, &match->spans[0], &match->spans[stride], &match->lastindex);
    if (view.obj != NULL) PyBuffer_Release(&view);
    if (result < 0) {
        Py_DECREF(match);
        PyErr_SetString(PyExc_RuntimeError, "Zig matcher rejected the match-object bridge call");
        return NULL;
    }
    if (result == 0) {
        Py_DECREF(match);
        Py_RETURN_NONE;
    }
    return (PyObject *)match;
}

static PyObject *bridge_compile(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 3) {
        PyErr_Format(PyExc_TypeError, "compile() takes exactly 3 arguments (%zd given)", nargs);
        return NULL;
    }
    if (!PyBytes_Check(args[0])) {
        PyErr_SetString(PyExc_TypeError, "Zig compiler expects encoded pattern bytes");
        return NULL;
    }
    unsigned long flags = PyLong_AsUnsignedLong(args[1]);
    int byte_mode = PyObject_IsTrue(args[2]);
    if (PyErr_Occurred() || flags > UINT32_MAX || byte_mode < 0) return NULL;
    const uint8_t *source = (const uint8_t *)PyBytes_AS_STRING(args[0]);
    size_t length = (size_t)PyBytes_GET_SIZE(args[0]);
    void *handle = rebar_zig_compile(source, length, (uint32_t)flags);
    if (handle == NULL) Py_RETURN_NONE;
    PyObject *names = PyDict_New();
    if (names == NULL) {
        rebar_zig_free(handle);
        return NULL;
    }
    size_t count = rebar_zig_name_count(handle);
    for (size_t index = 0; index < count; index++) {
        size_t width = rebar_zig_name_length(handle, index);
        if (width > 256) {
            Py_DECREF(names);
            rebar_zig_free(handle);
            PyErr_SetString(PyExc_OverflowError, "Zig group name exceeds the bridge limit");
            return NULL;
        }
        uint8_t name[256];
        if (rebar_zig_name_copy(handle, index, name, width) != width) {
            Py_DECREF(names);
            rebar_zig_free(handle);
            PyErr_SetString(PyExc_RuntimeError, "Zig group-name copy failed");
            return NULL;
        }
        PyObject *key = byte_mode ? PyUnicode_DecodeASCII((const char *)name, (Py_ssize_t)width, "strict") : PyUnicode_DecodeUTF8((const char *)name, (Py_ssize_t)width, "strict");
        PyObject *value = key == NULL ? NULL : PyLong_FromSize_t(rebar_zig_name_group(handle, index));
        if (key == NULL || value == NULL || PyDict_SetItem(names, key, value) < 0) {
            Py_XDECREF(key);
            Py_XDECREF(value);
            Py_DECREF(names);
            rebar_zig_free(handle);
            return NULL;
        }
        Py_DECREF(key);
        Py_DECREF(value);
    }
    PyObject *pointer = PyLong_FromVoidPtr(handle);
    PyObject *groups = PyLong_FromSize_t(rebar_zig_groups(handle));
    PyObject *effective = PyLong_FromUnsignedLong(rebar_zig_flags(handle));
    if (pointer == NULL || groups == NULL || effective == NULL) {
        Py_XDECREF(pointer);
        Py_XDECREF(groups);
        Py_XDECREF(effective);
        Py_DECREF(names);
        rebar_zig_free(handle);
        return NULL;
    }
    PyObject *result = PyTuple_Pack(4, pointer, groups, effective, names);
    Py_DECREF(pointer);
    Py_DECREF(groups);
    Py_DECREF(effective);
    Py_DECREF(names);
    if (result == NULL) rebar_zig_free(handle);
    return result;
}

static PyObject *bridge_free(PyObject *module, PyObject *value) {
    (void)module;
    void *handle = PyLong_AsVoidPtr(value);
    if (PyErr_Occurred()) return NULL;
    rebar_zig_free(handle);
    Py_RETURN_NONE;
}

static PyObject *bridge_span_object(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 8) {
        PyErr_Format(PyExc_TypeError, "span_object() takes exactly 8 arguments (%zd given)", nargs);
        return NULL;
    }
    PyObject *pattern = args[0];
    PyObject *subject = args[1];
    size_t groups = PyLong_AsSize_t(args[2]);
    PyObject *groupindex = args[3];
    Py_ssize_t begin = PyLong_AsSsize_t(args[4]);
    Py_ssize_t finish = PyLong_AsSsize_t(args[5]);
    Py_ssize_t pos = PyLong_AsSsize_t(args[6]);
    Py_ssize_t endpos = PyLong_AsSsize_t(args[7]);
    if (PyErr_Occurred()) return NULL;
    ZigMatch *match = zig_match_new(pattern, subject, groupindex, groups, pos, endpos);
    if (match == NULL) return NULL;
    size_t stride = groups + 1;
    for (size_t index = 0; index < stride * 2; index++) match->spans[index] = -1;
    match->spans[0] = begin;
    match->spans[stride] = finish;
    return (PyObject *)match;
}

static PyObject *bridge_collect_objects(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 7) {
        PyErr_Format(PyExc_TypeError, "collect_objects() takes exactly 7 arguments (%zd given)", nargs);
        return NULL;
    }
    PyObject *pattern = args[0];
    void *handle = PyLong_AsVoidPtr(args[1]);
    PyObject *groupindex = args[2];
    PyObject *subject = args[3];
    size_t groups = PyLong_AsSize_t(args[4]);
    size_t pos = PyLong_AsSize_t(args[5]);
    size_t endpos = PyLong_AsSize_t(args[6]);
    if (PyErr_Occurred() || groups != rebar_zig_groups(handle)) {
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_ValueError, "Zig regex group count does not match the compiled program");
        return NULL;
    }
    if (endpos < pos) return PyList_New(0);
    Py_buffer view = {0};
    const uint8_t *data;
    size_t length;
    uint8_t kind = 1;
    if (PyUnicode_Check(subject)) {
        data = PyUnicode_DATA(subject);
        length = (size_t)PyUnicode_GET_LENGTH(subject);
        kind = (uint8_t)PyUnicode_KIND(subject);
    } else {
        if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) return NULL;
        data = view.buf;
        length = (size_t)view.len;
    }
    size_t end = endpos < length ? endpos : length;
    ZigCaptureBuffer buffer;
    intptr_t count = zig_collect_growing(handle, data, length, kind, pos, end, groups, 0, &buffer);
    if (view.obj != NULL) PyBuffer_Release(&view);
    if (count < 0) {
        if (count == -2) return PyErr_NoMemory();
        PyErr_SetString(PyExc_RuntimeError, "Zig matcher rejected the collect-object bridge call");
        return NULL;
    }
    PyObject *result = PyList_New((Py_ssize_t)count);
    if (result == NULL) {
        zig_capture_release(&buffer);
        return NULL;
    }
    size_t stride = groups + 1;
    size_t words = buffer.words_per_match;
    for (intptr_t index = 0; index < count; index++) {
        size_t base = (size_t)index * words;
        ZigMatch *match = zig_match_new(pattern, subject, groupindex, groups, (Py_ssize_t)pos, (Py_ssize_t)end);
        if (match == NULL) {
            Py_DECREF(result);
            zig_capture_release(&buffer);
            return NULL;
        }
        memcpy(match->spans, buffer.storage + base, stride * 2 * sizeof(intptr_t));
        match->lastindex = buffer.storage[base + stride * 2];
        PyList_SET_ITEM(result, (Py_ssize_t)index, (PyObject *)match);
    }
    zig_capture_release(&buffer);
    return result;
}

static int zig_index_arg(PyObject *value, Py_ssize_t *result) {
    if (PyLong_CheckExact(value)) {
        *result = PyLong_AsSsize_t(value);
        return !PyErr_Occurred();
    }
    PyObject *index = PyNumber_Index(value);
    if (index == NULL) return 0;
    *result = PyLong_AsSsize_t(index);
    Py_DECREF(index);
    return !PyErr_Occurred();
}

static PyObject *zig_bad_bound_keyword(const char *method, PyObject *subject,
                                      PyObject *name) {
    if (subject == NULL) {
        PyErr_Format(PyExc_TypeError,
                     "%s() missing required argument 'string' (pos 1)", method);
    } else {
        PyErr_Format(PyExc_TypeError,
                     "%s() got an unexpected keyword argument '%U'", method,
                     name);
    }
    return NULL;
}

static PyObject *bridge_pattern_match(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 9) {
        PyErr_Format(PyExc_TypeError, "pattern_match() takes exactly 9 arguments (%zd given)", nargs);
        return NULL;
    }
    PyObject *pattern = args[0];
    void *handle = PyLong_AsVoidPtr(args[1]);
    PyObject *groupindex = args[2];
    PyObject *pattern_value = args[3];
    PyObject *literal = args[4];
    PyObject *subject = args[5];
    Py_ssize_t pos;
    Py_ssize_t requested_end;
    unsigned long mode = PyLong_AsUnsignedLong(args[8]);
    if (PyErr_Occurred() || mode > 2 || !zig_index_arg(args[6], &pos)) return NULL;
    Py_buffer view = {0};
    const uint8_t *data;
    size_t length;
    uint8_t kind = 1;
    int text_mode = PyUnicode_Check(subject);
    if (text_mode) {
        if (PyBytes_Check(pattern_value)) {
            PyErr_SetString(PyExc_TypeError, "cannot use a bytes pattern on a string-like object");
            return NULL;
        }
        data = PyUnicode_DATA(subject);
        length = (size_t)PyUnicode_GET_LENGTH(subject);
        kind = (uint8_t)PyUnicode_KIND(subject);
    } else {
        if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) {
            PyErr_Clear();
            PyErr_Format(PyExc_TypeError, "expected string or bytes-like object, got '%.200s'", Py_TYPE(subject)->tp_name);
            return NULL;
        }
        if (PyUnicode_Check(pattern_value)) {
            PyBuffer_Release(&view);
            PyErr_SetString(PyExc_TypeError, "cannot use a string pattern on a bytes-like object");
            return NULL;
        }
        data = view.buf;
        length = (size_t)view.len;
    }
    if (!zig_index_arg(args[7], &requested_end)) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        return NULL;
    }
    Py_ssize_t start = pos < 0 ? 0 : pos;
    Py_ssize_t end = requested_end < 0 ? 0 : requested_end;
    if ((size_t)start > length) start = (Py_ssize_t)length;
    if ((size_t)end > length) end = (Py_ssize_t)length;
    if (start > end && mode != 1) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        Py_RETURN_NONE;
    }
    intptr_t begin = -1;
    intptr_t finish = -1;
    size_t groups = rebar_zig_groups(handle);
    size_t stride = groups + 1;
    intptr_t begins[257];
    intptr_t ends[257];
    intptr_t last = -1;
    int result = 0;
    if (start > end) {
        result = rebar_zig_match_inverted_wide(handle, data, length, kind,
            (size_t)start, (size_t)end, 0, begins, ends, &last);
        if (result > 0) {
            begin = begins[0];
            finish = ends[0];
        }
    } else if (literal != Py_None) {
        Py_ssize_t width = text_mode ? PyUnicode_GET_LENGTH(literal) : PyBytes_GET_SIZE(literal);
        if (mode == 0) {
            if (text_mode && kind == 1 && PyUnicode_KIND(literal) == 1) {
                const void *found = memmem(data + start, (size_t)(end - start), PyUnicode_DATA(literal), (size_t)width);
                begin = found == NULL ? -1 : (intptr_t)((const uint8_t *)found - data);
            } else if (text_mode) begin = PyUnicode_Find(subject, literal, start, end, 1);
            else {
                const void *found = memmem(data + start, (size_t)(end - start), PyBytes_AS_STRING(literal), (size_t)width);
                begin = found == NULL ? -1 : (intptr_t)((const uint8_t *)found - data);
            }
        } else if (end - start >= width && (mode != 2 || end - start == width)) {
            if (text_mode) {
                int matches = PyUnicode_Tailmatch(subject, literal, start, end, -1);
                if (matches < 0) {
                    if (view.obj != NULL) PyBuffer_Release(&view);
                    return NULL;
                }
                begin = matches ? start : -1;
            } else begin = memcmp(data + start, PyBytes_AS_STRING(literal), (size_t)width) == 0 ? start : -1;
        }
        if (begin >= 0) {
            finish = begin + width;
            result = 1;
        }
    } else if (groups == 0) result = rebar_zig_match_wide(handle, data, length, kind, (size_t)start, (size_t)end, (uint8_t)mode, &begin, &finish);
    else result = rebar_zig_match_captures_wide(handle, data, length, kind, (size_t)start, (size_t)end, (uint8_t)mode, 0, begins, ends, &last);
    if (view.obj != NULL) PyBuffer_Release(&view);
    if (result < 0) {
        PyErr_SetString(PyExc_RuntimeError, "Zig matcher rejected the pattern bridge call");
        return NULL;
    }
    if (result == 0) {
        Py_RETURN_NONE;
    }
    ZigMatch *match = zig_match_new(pattern, subject, groupindex, groups, start, end);
    if (match == NULL) {
        return NULL;
    }
    if (groups == 0 || literal != Py_None) {
        match->spans[0] = begin;
        match->spans[stride] = finish;
    } else {
        memcpy(match->spans, begins, stride * sizeof(intptr_t));
        memcpy(match->spans + stride, ends, stride * sizeof(intptr_t));
        match->lastindex = last;
    }
    return (PyObject *)match;
}

static PyObject *bridge_bound_search(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    Py_ssize_t keyword_count = kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    if (nargs < 5 || nargs - 5 + keyword_count > 3) {
        PyErr_Format(PyExc_TypeError, "search() takes at most 3 arguments (%zd given)", nargs - 5 + keyword_count);
        return NULL;
    }
    PyObject *subject = nargs >= 6 ? args[5] : NULL;
    PyObject *pos = nargs >= 7 ? args[6] : Py_GetConstantBorrowed(Py_CONSTANT_ZERO);
    PyObject *endpos = nargs >= 8 ? args[7] : zig_default_endpos;
    for (Py_ssize_t index = 0; index < keyword_count; index++) {
        PyObject *name = PyTuple_GET_ITEM(kwnames, index);
        if (PyUnicode_CompareWithASCIIString(name, "string") == 0) {
            if (nargs >= 6) {
                PyErr_SetString(PyExc_TypeError, "argument for search() given by name ('string') and position (1)");
                return NULL;
            }
            subject = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "pos") == 0) {
            if (nargs >= 7) {
                PyErr_SetString(PyExc_TypeError, "argument for search() given by name ('pos') and position (2)");
                return NULL;
            }
            pos = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "endpos") == 0) {
            if (nargs >= 8) {
                PyErr_SetString(PyExc_TypeError, "argument for search() given by name ('endpos') and position (3)");
                return NULL;
            }
            endpos = args[nargs + index];
        } else return zig_bad_bound_keyword("search", subject, name);
    }
    if (subject == NULL) {
        PyErr_SetString(PyExc_TypeError, "search() missing required argument 'string' (pos 1)");
        return NULL;
    }
    PyObject *call[9] = {args[0], args[1], args[2], args[3], args[4], subject, pos, endpos, Py_GetConstantBorrowed(Py_CONSTANT_ZERO)};
    return bridge_pattern_match(module, call, 9);
}

static PyObject *bridge_bound_pattern_mode(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames, const char *method, unsigned long mode) {
    Py_ssize_t keyword_count = kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    if (nargs < 5 || nargs - 5 + keyword_count > 3) {
        PyErr_Format(PyExc_TypeError, "%s() takes at most 3 arguments (%zd given)", method, nargs - 5 + keyword_count);
        return NULL;
    }
    PyObject *subject = nargs >= 6 ? args[5] : NULL;
    PyObject *pos = nargs >= 7 ? args[6] : Py_GetConstantBorrowed(Py_CONSTANT_ZERO);
    PyObject *endpos = nargs >= 8 ? args[7] : zig_default_endpos;
    for (Py_ssize_t index = 0; index < keyword_count; index++) {
        PyObject *name = PyTuple_GET_ITEM(kwnames, index);
        if (PyUnicode_CompareWithASCIIString(name, "string") == 0) {
            if (nargs >= 6) {
                PyErr_Format(PyExc_TypeError, "argument for %s() given by name ('string') and position (1)", method);
                return NULL;
            }
            subject = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "pos") == 0) {
            if (nargs >= 7) {
                PyErr_Format(PyExc_TypeError, "argument for %s() given by name ('pos') and position (2)", method);
                return NULL;
            }
            pos = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "endpos") == 0) {
            if (nargs >= 8) {
                PyErr_Format(PyExc_TypeError, "argument for %s() given by name ('endpos') and position (3)", method);
                return NULL;
            }
            endpos = args[nargs + index];
        } else return zig_bad_bound_keyword(method, subject, name);
    }
    if (subject == NULL) {
        PyErr_Format(PyExc_TypeError, "%s() missing required argument 'string' (pos 1)", method);
        return NULL;
    }
    PyObject *mode_value = PyLong_FromUnsignedLong(mode);
    if (mode_value == NULL) return NULL;
    PyObject *call[9] = {args[0], args[1], args[2], args[3], args[4], subject, pos, endpos, mode_value};
    PyObject *result = bridge_pattern_match(module, call, 9);
    Py_DECREF(mode_value);
    return result;
}

static PyObject *bridge_bound_match(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    return bridge_bound_pattern_mode(module, args, nargs, kwnames, "match", 1);
}

static PyObject *bridge_bound_fullmatch(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    return bridge_bound_pattern_mode(module, args, nargs, kwnames, "fullmatch", 2);
}

static void zig_iterator_dealloc(ZigIterator *iterator) {
    if (iterator->view.obj != NULL) PyBuffer_Release(&iterator->view);
    PyMem_Free(iterator->record_heap);
    Py_XDECREF(iterator->pattern);
    Py_XDECREF(iterator->string);
    Py_XDECREF(iterator->groupindex);
    Py_TYPE(iterator)->tp_free((PyObject *)iterator);
}

static PyObject *zig_iterator_iter(PyObject *iterator) { return Py_NewRef(iterator); }

static ZigMatch *zig_iterator_record(ZigIterator *iterator, const intptr_t *record) {
    ZigMatch *match = zig_match_new(iterator->pattern, iterator->string, iterator->groupindex, iterator->groups, (Py_ssize_t)iterator->original_pos, (Py_ssize_t)iterator->endpos);
    if (match == NULL) return NULL;
    size_t stride = iterator->groups + 1;
    memcpy(match->spans, record, stride * 2 * sizeof(intptr_t));
    match->lastindex = record[stride * 2];
    return match;
}

static PyObject *zig_iterator_next(PyObject *value) {
    ZigIterator *iterator = (ZigIterator *)value;
    if (iterator->record_at == iterator->record_count) {
        if (iterator->done || iterator->cursor > iterator->endpos) {
            iterator->done = 1;
            return NULL;
        }
        size_t words = (iterator->groups + 1) * 2 + 1;
        size_t capacity = ZIG_ITERATOR_RECORD_WORDS / words;
        intptr_t *records = iterator->records;
        if (capacity == 0) {
            if (iterator->record_heap == NULL) {
                if (words > SIZE_MAX / sizeof(intptr_t)) return PyErr_NoMemory();
                iterator->record_heap = PyMem_Malloc(words * sizeof(intptr_t));
                if (iterator->record_heap == NULL) return PyErr_NoMemory();
            }
            records = iterator->record_heap;
            capacity = 1;
        }
        if (capacity > ZIG_INITIAL_CAPTURE_COUNT) capacity = ZIG_INITIAL_CAPTURE_COUNT;
        if (iterator->view.obj != NULL && !iterator->view.readonly) capacity = 1;
        intptr_t count = rebar_zig_collect_records_wide(iterator->handle, iterator->data, iterator->length, iterator->kind, iterator->endpos, capacity, records, &iterator->cursor, &iterator->nonempty);
        if (count < 0) {
            PyErr_SetString(PyExc_RuntimeError, "Zig matcher rejected the iterator bridge call");
            return NULL;
        }
        iterator->record_at = 0;
        iterator->record_count = (size_t)count;
        if (count == 0) {
            iterator->done = 1;
            return NULL;
        }
    }
    size_t words = (iterator->groups + 1) * 2 + 1;
    const intptr_t *record = (iterator->record_heap == NULL ? iterator->records : iterator->record_heap) + iterator->record_at * words;
    iterator->record_at += 1;
    size_t stride = iterator->groups + 1;
    iterator->nonempty = record[0] == record[stride];
    iterator->cursor = (size_t)record[stride];
    return (PyObject *)zig_iterator_record(iterator, record);
}

static PyObject *zig_scanner_search(ZigIterator *iterator, PyObject *ignored) {
    (void)ignored;
    PyObject *result = zig_iterator_next((PyObject *)iterator);
    if (result != NULL || PyErr_Occurred()) return result;
    Py_RETURN_NONE;
}

static PyObject *zig_scanner_match(ZigIterator *iterator, PyObject *ignored) {
    (void)ignored;
    iterator->record_at = 0;
    iterator->record_count = 0;
    if (iterator->done) Py_RETURN_NONE;
    size_t stride = iterator->groups + 1;
    intptr_t begins[257];
    intptr_t ends[257];
    intptr_t last = -1;
    int result;
    if (iterator->cursor > iterator->endpos) {
        result = rebar_zig_match_inverted_wide(iterator->handle, iterator->data,
            iterator->length, iterator->kind, iterator->cursor,
            iterator->endpos, iterator->nonempty, begins, ends, &last);
    } else if (iterator->groups == 0) {
        result = rebar_zig_match_nonempty_wide(iterator->handle, iterator->data,
            iterator->length, iterator->kind, iterator->cursor,
            iterator->endpos, 1, iterator->nonempty, &begins[0], &ends[0]);
    } else {
        result = rebar_zig_match_captures_wide(iterator->handle, iterator->data,
            iterator->length, iterator->kind, iterator->cursor,
            iterator->endpos, 1, iterator->nonempty, begins, ends, &last);
    }
    if (result < 0) {
        PyErr_SetString(PyExc_RuntimeError, "Zig matcher rejected the scanner bridge call");
        return NULL;
    }
    if (result == 0) {
        iterator->done = 1;
        Py_RETURN_NONE;
    }
    ZigMatch *match = zig_match_new(iterator->pattern, iterator->string, iterator->groupindex, iterator->groups, (Py_ssize_t)iterator->original_pos, (Py_ssize_t)iterator->endpos);
    if (match == NULL) return NULL;
    memcpy(match->spans, begins, stride * sizeof(intptr_t));
    memcpy(match->spans + stride, ends, stride * sizeof(intptr_t));
    match->lastindex = last;
    iterator->nonempty = begins[0] == ends[0];
    iterator->cursor = (size_t)ends[0];
    return (PyObject *)match;
}

static PyObject *zig_scanner_pattern(ZigIterator *iterator, void *closure) { (void)closure; return Py_NewRef(iterator->pattern); }

static PyMethodDef zig_scanner_methods[] = {
    {"search", (PyCFunction)zig_scanner_search, METH_NOARGS, "Return the next search match."},
    {"match", (PyCFunction)zig_scanner_match, METH_NOARGS, "Return the next anchored match."},
    {NULL, NULL, 0, NULL},
};

static PyGetSetDef zig_scanner_getsets[] = {
    {"pattern", (getter)zig_scanner_pattern, NULL, "Compiled pattern.", NULL},
    {NULL, NULL, NULL, NULL, NULL},
};

static PyTypeObject ZigIteratorType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "re.finditer",
    .tp_basicsize = sizeof(ZigIterator),
    .tp_dealloc = (destructor)zig_iterator_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = "Lazy, batched Zig regular-expression iterator.",
    .tp_iter = zig_iterator_iter,
    .tp_iternext = zig_iterator_next,
};

static PyTypeObject ZigScannerType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "re.ScannerState",
    .tp_basicsize = sizeof(ZigIterator),
    .tp_dealloc = (destructor)zig_iterator_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = "Lazy, batched Zig pattern scanner.",
    .tp_methods = zig_scanner_methods,
    .tp_getset = zig_scanner_getsets,
};

static PyObject *bridge_pattern_iterator(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 9) {
        PyErr_Format(PyExc_TypeError, "pattern_iterator() takes exactly 9 arguments (%zd given)", nargs);
        return NULL;
    }
    PyObject *pattern = args[0];
    void *handle = PyLong_AsVoidPtr(args[1]);
    PyObject *groupindex = args[2];
    PyObject *pattern_value = args[3];
    PyObject *subject = args[4];
    Py_ssize_t pos;
    Py_ssize_t requested_end;
    int scanner = PyObject_IsTrue(args[7]);
    size_t groups = PyLong_AsSize_t(args[8]);
    if (PyErr_Occurred() || scanner < 0 || !zig_index_arg(args[5], &pos) || groups != rebar_zig_groups(handle)) {
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_ValueError, "Zig regex group count does not match the compiled program");
        return NULL;
    }
    ZigIterator *iterator = (ZigIterator *)(scanner ? ZigScannerType.tp_alloc(&ZigScannerType, 0) : ZigIteratorType.tp_alloc(&ZigIteratorType, 0));
    if (iterator == NULL) return NULL;
    iterator->pattern = Py_NewRef(pattern);
    iterator->string = Py_NewRef(subject);
    iterator->groupindex = Py_NewRef(groupindex);
    iterator->handle = handle;
    iterator->groups = groups;
    iterator->kind = 1;
    iterator->nonempty = 0;
    iterator->done = 0;
    iterator->record_at = 0;
    iterator->record_count = 0;
    iterator->record_heap = NULL;
    iterator->view = (Py_buffer){0};
    if (PyUnicode_Check(subject)) {
        if (PyBytes_Check(pattern_value)) {
            Py_DECREF(iterator);
            PyErr_SetString(PyExc_TypeError, "cannot use a bytes pattern on a string-like object");
            return NULL;
        }
        iterator->data = PyUnicode_DATA(subject);
        iterator->length = (size_t)PyUnicode_GET_LENGTH(subject);
        iterator->kind = (uint8_t)PyUnicode_KIND(subject);
    } else {
        if (PyObject_GetBuffer(subject, &iterator->view, PyBUF_SIMPLE) != 0) {
            Py_DECREF(iterator);
            PyErr_Clear();
            PyErr_Format(PyExc_TypeError, "expected string or bytes-like object, got '%.200s'", Py_TYPE(subject)->tp_name);
            return NULL;
        }
        if (PyUnicode_Check(pattern_value)) {
            Py_DECREF(iterator);
            PyErr_SetString(PyExc_TypeError, "cannot use a string pattern on a bytes-like object");
            return NULL;
        }
        iterator->data = iterator->view.buf;
        iterator->length = (size_t)iterator->view.len;
    }
    if (!zig_index_arg(args[6], &requested_end)) {
        Py_DECREF(iterator);
        return NULL;
    }
    Py_ssize_t start = pos < 0 ? 0 : pos;
    Py_ssize_t end = requested_end < 0 ? 0 : requested_end;
    if ((size_t)start > iterator->length) start = (Py_ssize_t)iterator->length;
    if ((size_t)end > iterator->length) end = (Py_ssize_t)iterator->length;
    iterator->original_pos = (size_t)start;
    iterator->cursor = (size_t)start;
    iterator->endpos = (size_t)end;
    iterator->done = start > end && !scanner;
    return (PyObject *)iterator;
}

static PyObject *bridge_bound_finditer(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    Py_ssize_t keyword_count = kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    if (nargs < 5 || nargs - 5 + keyword_count > 3) {
        PyErr_Format(PyExc_TypeError, "finditer() takes at most 3 arguments (%zd given)", nargs - 5 + keyword_count);
        return NULL;
    }
    PyObject *subject = nargs >= 6 ? args[5] : NULL;
    PyObject *pos = nargs >= 7 ? args[6] : Py_GetConstantBorrowed(Py_CONSTANT_ZERO);
    PyObject *endpos = nargs >= 8 ? args[7] : zig_default_endpos;
    for (Py_ssize_t index = 0; index < keyword_count; index++) {
        PyObject *name = PyTuple_GET_ITEM(kwnames, index);
        if (PyUnicode_CompareWithASCIIString(name, "string") == 0) {
            if (nargs >= 6) {
                PyErr_SetString(PyExc_TypeError, "argument for finditer() given by name ('string') and position (1)");
                return NULL;
            }
            subject = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "pos") == 0) {
            if (nargs >= 7) {
                PyErr_SetString(PyExc_TypeError, "argument for finditer() given by name ('pos') and position (2)");
                return NULL;
            }
            pos = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "endpos") == 0) {
            if (nargs >= 8) {
                PyErr_SetString(PyExc_TypeError, "argument for finditer() given by name ('endpos') and position (3)");
                return NULL;
            }
            endpos = args[nargs + index];
        } else return zig_bad_bound_keyword("finditer", subject, name);
    }
    if (subject == NULL) {
        PyErr_SetString(PyExc_TypeError, "finditer() missing required argument 'string' (pos 1)");
        return NULL;
    }
    PyObject *call[9] = {args[0], args[1], args[2], args[3], subject, pos, endpos, Py_False, args[4]};
    return bridge_pattern_iterator(module, call, 9);
}

static PyObject *bridge_bound_scanner(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    Py_ssize_t keyword_count = kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    if (nargs < 5 || nargs - 5 + keyword_count > 3) {
        PyErr_Format(PyExc_TypeError, "scanner() takes at most 3 arguments (%zd given)", nargs - 5 + keyword_count);
        return NULL;
    }
    PyObject *subject = nargs >= 6 ? args[5] : NULL;
    PyObject *pos = nargs >= 7 ? args[6] : Py_GetConstantBorrowed(Py_CONSTANT_ZERO);
    PyObject *endpos = nargs >= 8 ? args[7] : zig_default_endpos;
    for (Py_ssize_t index = 0; index < keyword_count; index++) {
        PyObject *name = PyTuple_GET_ITEM(kwnames, index);
        if (PyUnicode_CompareWithASCIIString(name, "string") == 0) {
            if (nargs >= 6) {
                PyErr_SetString(PyExc_TypeError, "argument for scanner() given by name ('string') and position (1)");
                return NULL;
            }
            subject = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "pos") == 0) {
            if (nargs >= 7) {
                PyErr_SetString(PyExc_TypeError, "argument for scanner() given by name ('pos') and position (2)");
                return NULL;
            }
            pos = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "endpos") == 0) {
            if (nargs >= 8) {
                PyErr_SetString(PyExc_TypeError, "argument for scanner() given by name ('endpos') and position (3)");
                return NULL;
            }
            endpos = args[nargs + index];
        } else return zig_bad_bound_keyword("scanner", subject, name);
    }
    if (subject == NULL) {
        PyErr_SetString(PyExc_TypeError, "scanner() missing required argument 'string' (pos 1)");
        return NULL;
    }
    PyObject *call[9] = {args[0], args[1], args[2], args[3], subject, pos, endpos, Py_True, args[4]};
    return bridge_pattern_iterator(module, call, 9);
}

static PyObject *bridge_span(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 5) {
        PyErr_Format(PyExc_TypeError, "span() takes exactly 5 arguments (%zd given)", nargs);
        return NULL;
    }
    void *handle = PyLong_AsVoidPtr(args[0]);
    size_t pos = PyLong_AsSize_t(args[2]);
    size_t endpos = PyLong_AsSize_t(args[3]);
    unsigned long mode = PyLong_AsUnsignedLong(args[4]);
    if (PyErr_Occurred() || mode > UINT8_MAX) {
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_OverflowError, "invalid Zig regex bridge argument");
        return NULL;
    }
    PyObject *subject = args[1];
    Py_buffer view = {0};
    const uint8_t *data;
    size_t length;
    uint8_t kind = 1;
    if (PyUnicode_Check(subject)) {
        data = PyUnicode_DATA(subject);
        length = (size_t)PyUnicode_GET_LENGTH(subject);
        kind = (uint8_t)PyUnicode_KIND(subject);
    } else {
        if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) return NULL;
        data = view.buf;
        length = (size_t)view.len;
    }
    intptr_t begin = -1;
    intptr_t finish = -1;
    int result = rebar_zig_match_wide(handle, data, length, kind, pos, endpos, (uint8_t)mode, &begin, &finish);
    if (view.obj != NULL) PyBuffer_Release(&view);
    if (result < 0) {
        PyErr_SetString(PyExc_RuntimeError, "Zig bytecode matcher rejected the bridge call");
        return NULL;
    }
    if (result == 0) Py_RETURN_NONE;
    return zig_span(begin, finish);
}

static PyObject *bridge_match(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 5 && nargs != 6) {
        PyErr_Format(PyExc_TypeError, "match() takes 5 or 6 arguments (%zd given)", nargs);
        return NULL;
    }
    void *handle = PyLong_AsVoidPtr(args[0]);
    size_t pos = PyLong_AsSize_t(args[2]);
    size_t endpos = PyLong_AsSize_t(args[3]);
    unsigned long mode = PyLong_AsUnsignedLong(args[4]);
    int nonempty = nargs == 6 ? PyObject_IsTrue(args[5]) : 0;
    if (PyErr_Occurred() || mode > UINT8_MAX || nonempty < 0) {
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_OverflowError, "invalid Zig capture bridge argument");
        return NULL;
    }
    PyObject *subject = args[1];
    Py_buffer view = {0};
    const uint8_t *data;
    size_t length;
    uint8_t kind = 1;
    if (PyUnicode_Check(subject)) {
        data = PyUnicode_DATA(subject);
        length = (size_t)PyUnicode_GET_LENGTH(subject);
        kind = (uint8_t)PyUnicode_KIND(subject);
    } else {
        if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) return NULL;
        data = view.buf;
        length = (size_t)view.len;
    }
    size_t stride = rebar_zig_groups(handle) + 1;
    intptr_t local_begins[257];
    intptr_t local_ends[257];
    intptr_t *begins = local_begins;
    intptr_t *ends = local_ends;
    if (stride > 257) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        PyErr_SetString(PyExc_OverflowError, "too many Zig capture groups");
        return NULL;
    }
    intptr_t last = -1;
    int result = rebar_zig_match_captures_wide(handle, data, length, kind, pos, endpos, (uint8_t)mode, (uint8_t)nonempty, begins, ends, &last);
    if (view.obj != NULL) PyBuffer_Release(&view);
    if (result < 0) {
        PyErr_SetString(PyExc_RuntimeError, "Zig capture matcher rejected the bridge call");
        return NULL;
    }
    if (result == 0) Py_RETURN_NONE;
    PyObject *spans = PyTuple_New((Py_ssize_t)stride);
    if (spans == NULL) return NULL;
    for (size_t index = 0; index < stride; index++) {
        PyObject *item = begins[index] < 0 ? Py_NewRef(Py_None) : zig_span(begins[index], ends[index]);
        if (item == NULL) {
            Py_DECREF(spans);
            return NULL;
        }
        PyTuple_SET_ITEM(spans, (Py_ssize_t)index, item);
    }
    PyObject *last_value = last < 0 ? Py_NewRef(Py_None) : PyLong_FromSsize_t((Py_ssize_t)last);
    if (last_value == NULL) {
        Py_DECREF(spans);
        return NULL;
    }
    PyObject *value = PyTuple_Pack(2, spans, last_value);
    Py_DECREF(spans);
    Py_DECREF(last_value);
    return value;
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
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_OverflowError, "invalid Zig regex collection argument");
        return NULL;
    }
    if (groups != rebar_zig_groups(handle)) {
        PyErr_SetString(PyExc_ValueError, "Zig regex group count does not match the compiled program");
        return NULL;
    }
    PyObject *subject = args[1];
    Py_buffer view = {0};
    const uint8_t *data;
    size_t length;
    uint8_t kind = 1;
    if (PyUnicode_Check(subject)) {
        data = PyUnicode_DATA(subject);
        length = (size_t)PyUnicode_GET_LENGTH(subject);
        kind = (uint8_t)PyUnicode_KIND(subject);
    } else {
        if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) return NULL;
        data = view.buf;
        length = (size_t)view.len;
    }
    size_t end = endpos < length ? endpos : length;
    ZigCaptureBuffer buffer;
    intptr_t count = zig_collect_growing(handle, data, length, kind, pos, end, groups, 0, &buffer);
    if (view.obj != NULL) PyBuffer_Release(&view);
    if (count < 0) {
        if (count == -2) return PyErr_NoMemory();
        PyErr_SetString(PyExc_RuntimeError, "Zig capture engine rejected the collection bridge call");
        return NULL;
    }
    size_t stride = buffer.stride;
    size_t words = buffer.words_per_match;
    PyObject *records = PyList_New((Py_ssize_t)count);
    if (records == NULL) {
        zig_capture_release(&buffer);
        return NULL;
    }
    for (intptr_t match = 0; match < count; match++) {
        PyObject *spans = PyTuple_New((Py_ssize_t)stride);
        if (spans == NULL) goto collect_error;
        size_t base = (size_t)match * words;
        for (size_t group = 0; group < stride; group++) {
            intptr_t begin = buffer.storage[base + group];
            intptr_t finish = buffer.storage[base + stride + group];
            PyObject *item = begin < 0 ? Py_NewRef(Py_None) : zig_span(begin, finish);
            if (item == NULL) {
                Py_DECREF(spans);
                goto collect_error;
            }
            PyTuple_SET_ITEM(spans, (Py_ssize_t)group, item);
        }
        intptr_t last_value = buffer.storage[base + stride * 2];
        PyObject *last = last_value < 0 ? Py_NewRef(Py_None) : PyLong_FromSsize_t((Py_ssize_t)last_value);
        if (last == NULL) {
            Py_DECREF(spans);
            goto collect_error;
        }
        PyObject *record = PyTuple_Pack(2, spans, last);
        Py_DECREF(spans);
        Py_DECREF(last);
        if (record == NULL) goto collect_error;
        PyList_SET_ITEM(records, (Py_ssize_t)match, record);
    }
    zig_capture_release(&buffer);
    return records;

collect_error:
    Py_DECREF(records);
    zig_capture_release(&buffer);
    return NULL;
}

static PyObject *bridge_findall(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 6) {
        PyErr_Format(PyExc_TypeError, "findall() takes exactly 6 arguments (%zd given)", nargs);
        return NULL;
    }
    void *handle = PyLong_AsVoidPtr(args[0]);
    PyObject *pattern_value = args[1];
    PyObject *subject = args[2];
    size_t groups = PyLong_AsSize_t(args[3]);
    Py_ssize_t requested_pos;
    Py_ssize_t requested_end;
    if (PyErr_Occurred() || groups == SIZE_MAX || !zig_index_arg(args[4], &requested_pos)) {
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_OverflowError, "invalid Zig regex findall argument");
        return NULL;
    }
    if (groups != rebar_zig_groups(handle)) {
        PyErr_SetString(PyExc_ValueError, "Zig regex group count does not match the compiled program");
        return NULL;
    }
    Py_buffer view = {0};
    const uint8_t *data;
    size_t length;
    uint8_t kind = 1;
    int text_mode = PyUnicode_Check(subject);
    if (text_mode) {
        if (PyBytes_Check(pattern_value)) {
            PyErr_SetString(PyExc_TypeError, "cannot use a bytes pattern on a string-like object");
            return NULL;
        }
        data = PyUnicode_DATA(subject);
        length = (size_t)PyUnicode_GET_LENGTH(subject);
        kind = (uint8_t)PyUnicode_KIND(subject);
    } else {
        if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) {
            PyErr_Clear();
            PyErr_Format(PyExc_TypeError, "expected string or bytes-like object, got '%.200s'", Py_TYPE(subject)->tp_name);
            return NULL;
        }
        if (PyUnicode_Check(pattern_value)) {
            PyBuffer_Release(&view);
            PyErr_SetString(PyExc_TypeError, "cannot use a string pattern on a bytes-like object");
            return NULL;
        }
        data = view.buf;
        length = (size_t)view.len;
    }
    if (!zig_index_arg(args[5], &requested_end)) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        return NULL;
    }
    size_t pos = requested_pos < 0 ? 0 : (size_t)requested_pos;
    size_t end = requested_end < 0 ? 0 : (size_t)requested_end;
    if (pos > length) pos = length;
    if (end > length) end = length;
    if (pos > end) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        return PyList_New(0);
    }
    ZigCaptureBuffer buffer;
    intptr_t count = zig_collect_growing(handle, data, length, kind, pos, end, groups, 0, &buffer);
    if (count < 0) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        if (count == -2) return PyErr_NoMemory();
        PyErr_SetString(PyExc_RuntimeError, "Zig capture engine rejected the findall bridge call");
        return NULL;
    }
    size_t stride = buffer.stride;
    size_t words = buffer.words_per_match;
    PyObject *result = PyList_New((Py_ssize_t)count);
    if (result == NULL) goto findall_error;
    for (intptr_t match = 0; match < count; match++) {
        size_t base = (size_t)match * words;
        size_t first = groups == 0 ? 0 : 1;
        size_t values = groups <= 1 ? 1 : groups;
        PyObject *row = values == 1 ? NULL : PyTuple_New((Py_ssize_t)values);
        if (values != 1 && row == NULL) goto findall_error;
        for (size_t index = 0; index < values; index++) {
            size_t group = first + index;
            intptr_t begin = buffer.storage[base + group];
            intptr_t finish = buffer.storage[base + stride + group];
            PyObject *item;
            if (begin < 0) item = text_mode ? PyUnicode_New(0, 127) : PyBytes_FromStringAndSize("", 0);
            else if (text_mode) item = PyUnicode_Substring(subject, (Py_ssize_t)begin, (Py_ssize_t)finish);
            else item = zig_bytes_piece(subject, data, length,
                                        (size_t)begin, (size_t)finish);
            if (item == NULL) {
                Py_XDECREF(row);
                goto findall_error;
            }
            if (values == 1) row = item;
            else PyTuple_SET_ITEM(row, (Py_ssize_t)index, item);
        }
        PyList_SET_ITEM(result, (Py_ssize_t)match, row);
    }
    if (view.obj != NULL) PyBuffer_Release(&view);
    zig_capture_release(&buffer);
    return result;

findall_error:
    if (view.obj != NULL) PyBuffer_Release(&view);
    zig_capture_release(&buffer);
    Py_XDECREF(result);
    return NULL;
}

static PyObject *bridge_bound_findall(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    Py_ssize_t keyword_count = kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    if (nargs < 3 || nargs - 3 + keyword_count > 3) {
        PyErr_Format(PyExc_TypeError, "findall() takes at most 3 arguments (%zd given)", nargs - 3 + keyword_count);
        return NULL;
    }
    PyObject *subject = nargs >= 4 ? args[3] : NULL;
    PyObject *pos = nargs >= 5 ? args[4] : Py_GetConstantBorrowed(Py_CONSTANT_ZERO);
    PyObject *endpos = nargs >= 6 ? args[5] : zig_default_endpos;
    for (Py_ssize_t index = 0; index < keyword_count; index++) {
        PyObject *name = PyTuple_GET_ITEM(kwnames, index);
        if (PyUnicode_CompareWithASCIIString(name, "string") == 0) {
            if (nargs >= 4) {
                PyErr_SetString(PyExc_TypeError, "argument for findall() given by name ('string') and position (1)");
                return NULL;
            }
            subject = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "pos") == 0) {
            if (nargs >= 5) {
                PyErr_SetString(PyExc_TypeError, "argument for findall() given by name ('pos') and position (2)");
                return NULL;
            }
            pos = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "endpos") == 0) {
            if (nargs >= 6) {
                PyErr_SetString(PyExc_TypeError, "argument for findall() given by name ('endpos') and position (3)");
                return NULL;
            }
            endpos = args[nargs + index];
        } else return zig_bad_bound_keyword("findall", subject, name);
    }
    if (subject == NULL) {
        PyErr_SetString(PyExc_TypeError, "findall() missing required argument 'string' (pos 1)");
        return NULL;
    }
    PyObject *call[6] = {args[0], args[1], subject, args[2], pos, endpos};
    return bridge_findall(module, call, 6);
}

static PyObject *bridge_bound_literal_findall(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    (void)module;
    Py_ssize_t keyword_count = kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    if (nargs < 1 || nargs - 1 + keyword_count > 3) {
        PyErr_Format(PyExc_TypeError, "findall() takes at most 3 arguments (%zd given)", nargs - 1 + keyword_count);
        return NULL;
    }
    PyObject *literal = args[0];
    PyObject *subject = nargs >= 2 ? args[1] : NULL;
    PyObject *pos_value = nargs >= 3 ? args[2] : Py_GetConstantBorrowed(Py_CONSTANT_ZERO);
    PyObject *end_value = nargs >= 4 ? args[3] : zig_default_endpos;
    for (Py_ssize_t index = 0; index < keyword_count; index++) {
        PyObject *name = PyTuple_GET_ITEM(kwnames, index);
        if (PyUnicode_CompareWithASCIIString(name, "string") == 0) {
            if (nargs >= 2) {
                PyErr_SetString(PyExc_TypeError, "argument for findall() given by name ('string') and position (1)");
                return NULL;
            }
            subject = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "pos") == 0) {
            if (nargs >= 3) {
                PyErr_SetString(PyExc_TypeError, "argument for findall() given by name ('pos') and position (2)");
                return NULL;
            }
            pos_value = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "endpos") == 0) {
            if (nargs >= 4) {
                PyErr_SetString(PyExc_TypeError, "argument for findall() given by name ('endpos') and position (3)");
                return NULL;
            }
            end_value = args[nargs + index];
        } else return zig_bad_bound_keyword("findall", subject, name);
    }
    if (subject == NULL) {
        PyErr_SetString(PyExc_TypeError, "findall() missing required argument 'string' (pos 1)");
        return NULL;
    }
    Py_ssize_t requested_pos;
    Py_ssize_t requested_end;
    if (!zig_index_arg(pos_value, &requested_pos)) return NULL;
    int text_mode = PyUnicode_Check(literal);
    Py_buffer view = {0};
    const char *data = NULL;
    Py_ssize_t length;
    Py_ssize_t literal_length;
    if (text_mode) {
        if (!PyUnicode_Check(subject)) {
            PyErr_SetString(PyExc_TypeError, "cannot use a string pattern on a bytes-like object");
            return NULL;
        }
        length = PyUnicode_GET_LENGTH(subject);
        literal_length = PyUnicode_GET_LENGTH(literal);
    } else {
        if (PyUnicode_Check(subject)) {
            PyErr_SetString(PyExc_TypeError, "cannot use a bytes pattern on a string-like object");
            return NULL;
        }
        if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) {
            PyErr_Clear();
            PyErr_Format(PyExc_TypeError, "expected string or bytes-like object, got '%.200s'", Py_TYPE(subject)->tp_name);
            return NULL;
        }
        data = view.buf;
        length = view.len;
        literal_length = PyBytes_GET_SIZE(literal);
    }
    if (!zig_index_arg(end_value, &requested_end)) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        return NULL;
    }
    Py_ssize_t pos = requested_pos < 0 ? 0 : requested_pos;
    Py_ssize_t end = requested_end < 0 ? 0 : requested_end;
    if (pos > length) pos = length;
    if (end > length) end = length;
    PyObject *result = PyList_New(0);
    if (result == NULL) goto literal_findall_error;
    if (pos > end || literal_length == 0) goto literal_findall_done;
    Py_ssize_t cursor = pos;
    while (cursor <= end - literal_length) {
        Py_ssize_t found;
        if (text_mode) found = PyUnicode_Find(subject, literal, cursor, end, 1);
        else {
            const char *item = memmem(data + cursor, (size_t)(end - cursor), PyBytes_AS_STRING(literal), (size_t)literal_length);
            found = item == NULL ? -1 : (Py_ssize_t)(item - data);
        }
        if (found < 0) {
            if (PyErr_Occurred()) goto literal_findall_error;
            break;
        }
        PyObject *item = text_mode
            ? PyUnicode_Substring(subject, found, found + literal_length)
            : zig_bytes_piece(subject, (const uint8_t *)data, (size_t)length,
                              (size_t)found, (size_t)(found + literal_length));
        if (item == NULL) goto literal_findall_error;
        PyListObject *list = (PyListObject *)result;
        Py_ssize_t used = PyList_GET_SIZE(result);
        if (used < list->allocated) {
            PyList_SET_ITEM(result, used, item);
            Py_SET_SIZE(result, used + 1);
        } else {
            if (PyList_Append(result, item) < 0) {
                Py_DECREF(item);
                goto literal_findall_error;
            }
            Py_DECREF(item);
        }
        cursor = found + literal_length;
    }
literal_findall_done:
    if (view.obj != NULL) PyBuffer_Release(&view);
    return result;

literal_findall_error:
    if (view.obj != NULL) PyBuffer_Release(&view);
    Py_XDECREF(result);
    return NULL;
}

static PyObject *bridge_split(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 5) {
        PyErr_Format(PyExc_TypeError, "split() takes exactly 5 arguments (%zd given)", nargs);
        return NULL;
    }
    void *handle = PyLong_AsVoidPtr(args[0]);
    PyObject *pattern_value = args[1];
    PyObject *subject = args[2];
    size_t groups = PyLong_AsSize_t(args[3]);
    Py_ssize_t maxsplit;
    if (PyErr_Occurred() || groups == SIZE_MAX || !zig_index_arg(args[4], &maxsplit)) {
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_OverflowError, "invalid Zig regex split argument");
        return NULL;
    }
    if (groups != rebar_zig_groups(handle)) {
        PyErr_SetString(PyExc_ValueError, "Zig regex group count does not match the compiled program");
        return NULL;
    }
    Py_buffer view = {0};
    const uint8_t *data;
    size_t length;
    uint8_t kind = 1;
    int text_mode = PyUnicode_Check(subject);
    if (text_mode) {
        if (PyBytes_Check(pattern_value)) {
            PyErr_SetString(PyExc_TypeError, "cannot use a bytes pattern on a string-like object");
            return NULL;
        }
        data = PyUnicode_DATA(subject);
        length = (size_t)PyUnicode_GET_LENGTH(subject);
        kind = (uint8_t)PyUnicode_KIND(subject);
    } else {
        if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) {
            PyErr_Clear();
            PyErr_Format(PyExc_TypeError, "expected string or bytes-like object, got '%.200s'", Py_TYPE(subject)->tp_name);
            return NULL;
        }
        if (PyUnicode_Check(pattern_value)) {
            PyBuffer_Release(&view);
            PyErr_SetString(PyExc_TypeError, "cannot use a string pattern on a bytes-like object");
            return NULL;
        }
        data = view.buf;
        length = (size_t)view.len;
    }
    if (maxsplit < 0) {
        PyObject *item = text_mode ? PyUnicode_Substring(subject, 0, (Py_ssize_t)length) : PyBytes_FromStringAndSize((const char *)data, (Py_ssize_t)length);
        if (view.obj != NULL) PyBuffer_Release(&view);
        if (item == NULL) return NULL;
        PyObject *result = PyList_New(1);
        if (result == NULL) {
            Py_DECREF(item);
            return NULL;
        }
        PyList_SET_ITEM(result, 0, item);
        return result;
    }
    ZigCaptureBuffer buffer;
    intptr_t count = zig_collect_growing(handle, data, length, kind, 0, length, groups, maxsplit > 0 ? (size_t)maxsplit : 0, &buffer);
    if (count < 0) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        if (count == -2) return PyErr_NoMemory();
        PyErr_SetString(PyExc_RuntimeError, "Zig capture engine rejected the split bridge call");
        return NULL;
    }
    size_t stride = buffer.stride;
    size_t words = buffer.words_per_match;
    if ((size_t)count > (SIZE_MAX - 1) / stride || (size_t)count * stride + 1 > (size_t)PY_SSIZE_T_MAX) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        zig_capture_release(&buffer);
        return PyErr_NoMemory();
    }
    PyObject *result = PyList_New((Py_ssize_t)((size_t)count * stride + 1));
    if (result == NULL) goto split_error;
    size_t previous = 0;
    Py_ssize_t output = 0;
    for (intptr_t match = 0; match < count; match++) {
        size_t base = (size_t)match * words;
        size_t begin = (size_t)buffer.storage[base];
        size_t finish = (size_t)buffer.storage[base + stride];
        PyObject *prefix = text_mode ? PyUnicode_Substring(subject, (Py_ssize_t)previous, (Py_ssize_t)begin) : PyBytes_FromStringAndSize((const char *)data + previous, (Py_ssize_t)(begin - previous));
        if (prefix == NULL) goto split_error;
        PyList_SET_ITEM(result, output++, prefix);
        for (size_t group = 1; group < stride; group++) {
            intptr_t first = buffer.storage[base + group];
            intptr_t last = buffer.storage[base + stride + group];
            PyObject *item;
            if (first < 0) item = Py_NewRef(Py_None);
            else if (text_mode) item = PyUnicode_Substring(subject, (Py_ssize_t)first, (Py_ssize_t)last);
            else item = PyBytes_FromStringAndSize((const char *)data + first, (Py_ssize_t)(last - first));
            if (item == NULL) goto split_error;
            PyList_SET_ITEM(result, output++, item);
        }
        previous = finish;
    }
    PyObject *tail = text_mode ? PyUnicode_Substring(subject, (Py_ssize_t)previous, (Py_ssize_t)length) : PyBytes_FromStringAndSize((const char *)data + previous, (Py_ssize_t)(length - previous));
    if (tail == NULL) goto split_error;
    PyList_SET_ITEM(result, output, tail);
    if (view.obj != NULL) PyBuffer_Release(&view);
    zig_capture_release(&buffer);
    return result;

split_error:
    if (view.obj != NULL) PyBuffer_Release(&view);
    zig_capture_release(&buffer);
    Py_XDECREF(result);
    return NULL;
}

static PyObject *bridge_bound_split(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    Py_ssize_t keyword_count = kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    if (nargs < 3 || nargs - 3 + keyword_count > 2) {
        PyErr_Format(PyExc_TypeError, "split() takes at most 2 arguments (%zd given)", nargs - 3 + keyword_count);
        return NULL;
    }
    PyObject *subject = nargs >= 4 ? args[3] : NULL;
    PyObject *maxsplit = nargs >= 5 ? args[4] : Py_GetConstantBorrowed(Py_CONSTANT_ZERO);
    for (Py_ssize_t index = 0; index < keyword_count; index++) {
        PyObject *name = PyTuple_GET_ITEM(kwnames, index);
        if (PyUnicode_CompareWithASCIIString(name, "string") == 0) {
            if (nargs >= 4) {
                PyErr_SetString(PyExc_TypeError, "argument for split() given by name ('string') and position (1)");
                return NULL;
            }
            subject = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "maxsplit") == 0) {
            if (nargs >= 5) {
                PyErr_SetString(PyExc_TypeError, "argument for split() given by name ('maxsplit') and position (2)");
                return NULL;
            }
            maxsplit = args[nargs + index];
        } else {
            PyErr_Format(PyExc_TypeError, "split() got an unexpected keyword argument '%U'", name);
            return NULL;
        }
    }
    if (subject == NULL) {
        PyErr_SetString(PyExc_TypeError, "split() missing required argument 'string' (pos 1)");
        return NULL;
    }
    PyObject *call[5] = {args[0], args[1], subject, args[2], maxsplit};
    return bridge_split(module, call, 5);
}

static PyObject *bridge_subn(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 6) {
        PyErr_Format(PyExc_TypeError, "subn() takes exactly 6 arguments (%zd given)", nargs);
        return NULL;
    }
    void *handle = PyLong_AsVoidPtr(args[0]);
    PyObject *pattern_value = args[1];
    PyObject *subject = args[2];
    size_t groups = PyLong_AsSize_t(args[3]);
    PyObject *tokens = args[4];
    Py_ssize_t limit;
    if (PyErr_Occurred() || groups == SIZE_MAX || !zig_index_arg(args[5], &limit)) {
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_OverflowError, "invalid Zig regex replacement argument");
        return NULL;
    }
    if (groups != rebar_zig_groups(handle)) {
        PyErr_SetString(PyExc_ValueError, "Zig regex group count does not match the compiled program");
        return NULL;
    }
    if (!PyTuple_Check(tokens)) {
        PyErr_SetString(PyExc_TypeError, "Zig regex replacement tokens must be a tuple");
        return NULL;
    }
    Py_ssize_t token_count = PyTuple_GET_SIZE(tokens);
    Py_buffer view = {0};
    const uint8_t *data;
    size_t length;
    uint8_t kind = 1;
    int text_mode = PyUnicode_Check(subject);
    if (text_mode) {
        if (PyBytes_Check(pattern_value)) {
            PyErr_SetString(PyExc_TypeError, "cannot use a bytes pattern on a string-like object");
            return NULL;
        }
        data = PyUnicode_DATA(subject);
        length = (size_t)PyUnicode_GET_LENGTH(subject);
        kind = (uint8_t)PyUnicode_KIND(subject);
    } else {
        if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) {
            PyErr_Clear();
            PyErr_Format(PyExc_TypeError, "expected string or bytes-like object, got '%.200s'", Py_TYPE(subject)->tp_name);
            return NULL;
        }
        if (PyUnicode_Check(pattern_value)) {
            PyBuffer_Release(&view);
            PyErr_SetString(PyExc_TypeError, "cannot use a string pattern on a bytes-like object");
            return NULL;
        }
        data = view.buf;
        length = (size_t)view.len;
    }
    if (limit < 0) {
        PyObject *unchanged = text_mode ? PyUnicode_Substring(subject, 0, (Py_ssize_t)length) : PyBytes_FromStringAndSize((const char *)data, (Py_ssize_t)length);
        if (view.obj != NULL) PyBuffer_Release(&view);
        if (unchanged == NULL) return NULL;
        return Py_BuildValue("(Nn)", unchanged, (Py_ssize_t)0);
    }
    ZigCaptureBuffer buffer;
    intptr_t count = zig_collect_growing(handle, data, length, kind, 0, length, groups, limit > 0 ? (size_t)limit : 0, &buffer);
    if (count < 0) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        if (count == -2) return PyErr_NoMemory();
        PyErr_SetString(PyExc_RuntimeError, "Zig capture engine rejected the replacement bridge call");
        return NULL;
    }
    size_t stride = buffer.stride;
    size_t words = buffer.words_per_match;
    if (text_mode) {
        PyUnicodeWriter *writer = PyUnicodeWriter_Create((Py_ssize_t)length);
        if (writer == NULL) {
            zig_capture_release(&buffer);
            return NULL;
        }
        size_t previous = 0;
        for (intptr_t match = 0; match < count; match++) {
            size_t base = (size_t)match * words;
            size_t begin = (size_t)buffer.storage[base];
            size_t finish = (size_t)buffer.storage[base + stride];
            if (PyUnicodeWriter_WriteSubstring(writer, subject, (Py_ssize_t)previous, (Py_ssize_t)begin) < 0) {
                PyUnicodeWriter_Discard(writer);
                zig_capture_release(&buffer);
                return NULL;
            }
            for (Py_ssize_t token = 0; token < token_count; token++) {
                PyObject *value = PyTuple_GET_ITEM(tokens, token);
                int written;
                if (PyLong_Check(value)) {
                    Py_ssize_t group = PyLong_AsSsize_t(value);
                    if (PyErr_Occurred() || group < 0 || (size_t)group >= stride) {
                        PyUnicodeWriter_Discard(writer);
                        zig_capture_release(&buffer);
                        PyErr_SetString(PyExc_IndexError, "invalid Zig regex replacement group");
                        return NULL;
                    }
                    intptr_t first = buffer.storage[base + (size_t)group];
                    intptr_t last = buffer.storage[base + stride + (size_t)group];
                    written = first < 0 ? 0 : PyUnicodeWriter_WriteSubstring(writer, subject, (Py_ssize_t)first, (Py_ssize_t)last);
                } else written = PyUnicodeWriter_WriteStr(writer, value);
                if (written < 0) {
                    PyUnicodeWriter_Discard(writer);
                    zig_capture_release(&buffer);
                    return NULL;
                }
            }
            previous = finish;
        }
        if (PyUnicodeWriter_WriteSubstring(writer, subject, (Py_ssize_t)previous, (Py_ssize_t)length) < 0) {
            PyUnicodeWriter_Discard(writer);
            zig_capture_release(&buffer);
            return NULL;
        }
        PyObject *joined = PyUnicodeWriter_Finish(writer);
        zig_capture_release(&buffer);
        if (joined == NULL) return NULL;
        return Py_BuildValue("(Nn)", joined, (Py_ssize_t)count);
    }
    size_t output_length = length;
    for (intptr_t match = 0; match < count; match++) {
        size_t base = (size_t)match * words;
        size_t begin = (size_t)buffer.storage[base];
        size_t finish = (size_t)buffer.storage[base + stride];
        output_length -= finish - begin;
        for (Py_ssize_t index = 0; index < token_count; index++) {
            PyObject *token = PyTuple_GET_ITEM(tokens, index);
            size_t added;
            if (PyLong_Check(token)) {
                size_t group = PyLong_AsSize_t(token);
                if (PyErr_Occurred() || group >= stride) {
                    if (!PyErr_Occurred()) PyErr_SetString(PyExc_ValueError, "Zig regex replacement group is out of range");
                    goto subn_error;
                }
                intptr_t first = buffer.storage[base + group];
                intptr_t last = buffer.storage[base + stride + group];
                added = first < 0 ? 0 : (size_t)(last - first);
            } else if (PyBytes_Check(token)) added = (size_t)PyBytes_GET_SIZE(token);
            else {
                PyErr_SetString(PyExc_TypeError, "Zig bytes replacement token must be bytes");
                goto subn_error;
            }
            if (added > (size_t)PY_SSIZE_T_MAX - output_length) {
                PyErr_NoMemory();
                goto subn_error;
            }
            output_length += added;
        }
    }
    PyObject *joined = PyBytes_FromStringAndSize(NULL, (Py_ssize_t)output_length);
    if (joined == NULL) goto subn_error;
    uint8_t *output = (uint8_t *)PyBytes_AS_STRING(joined);
    size_t previous = 0;
    size_t written = 0;
    for (intptr_t match = 0; match < count; match++) {
        size_t base = (size_t)match * words;
        size_t begin = (size_t)buffer.storage[base];
        size_t finish = (size_t)buffer.storage[base + stride];
        size_t prefix = begin - previous;
        memcpy(output + written, data + previous, prefix);
        written += prefix;
        for (Py_ssize_t index = 0; index < token_count; index++) {
            PyObject *token = PyTuple_GET_ITEM(tokens, index);
            const uint8_t *piece;
            size_t piece_length;
            if (PyLong_Check(token)) {
                size_t group = (size_t)PyLong_AsSsize_t(token);
                intptr_t first = buffer.storage[base + group];
                intptr_t last = buffer.storage[base + stride + group];
                piece = first < 0 ? data : data + first;
                piece_length = first < 0 ? 0 : (size_t)(last - first);
            } else {
                piece = (const uint8_t *)PyBytes_AS_STRING(token);
                piece_length = (size_t)PyBytes_GET_SIZE(token);
            }
            memcpy(output + written, piece, piece_length);
            written += piece_length;
        }
        previous = finish;
    }
    memcpy(output + written, data + previous, length - previous);
    if (view.obj != NULL) PyBuffer_Release(&view);
    zig_capture_release(&buffer);
    return Py_BuildValue("(Nn)", joined, (Py_ssize_t)count);

subn_error:
    if (view.obj != NULL) PyBuffer_Release(&view);
    zig_capture_release(&buffer);
    return NULL;
}

static PyObject *bridge_literal_subn(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 4) {
        PyErr_Format(PyExc_TypeError, "literal_subn() takes exactly 4 arguments (%zd given)", nargs);
        return NULL;
    }
    PyObject *literal = args[0];
    PyObject *replacement = args[1];
    PyObject *subject = args[2];
    Py_ssize_t limit;
    if (!zig_index_arg(args[3], &limit)) return NULL;
    int text_mode = PyUnicode_Check(literal);
    if (text_mode != PyUnicode_Check(replacement)) {
        PyErr_Format(PyExc_TypeError, "sequence item 0: expected %s, %.200s found", text_mode ? "str instance" : "a bytes-like object", Py_TYPE(replacement)->tp_name);
        return NULL;
    }
    if (text_mode) {
        if (!PyUnicode_Check(subject)) {
            Py_buffer checked = {0};
            if (PyObject_GetBuffer(subject, &checked, PyBUF_SIMPLE) != 0) {
                PyErr_Clear();
                PyErr_Format(PyExc_TypeError, "expected string or bytes-like object, got '%.200s'", Py_TYPE(subject)->tp_name);
                return NULL;
            }
            PyBuffer_Release(&checked);
            PyErr_SetString(PyExc_TypeError, "cannot use a string pattern on a bytes-like object");
            return NULL;
        }
        Py_ssize_t length = PyUnicode_GET_LENGTH(subject);
        Py_ssize_t literal_length = PyUnicode_GET_LENGTH(literal);
        if (literal_length == 0 || limit < 0) return Py_BuildValue("(On)", subject, (Py_ssize_t)0);
        PyUnicodeWriter *writer = PyUnicodeWriter_Create(length);
        if (writer == NULL) return NULL;
        Py_ssize_t cursor = 0;
        Py_ssize_t count = 0;
        while (limit == 0 || count < limit) {
            Py_ssize_t found = PyUnicode_Find(subject, literal, cursor, length, 1);
            if (found == -2) {
                PyUnicodeWriter_Discard(writer);
                return NULL;
            }
            if (found < 0) break;
            if (PyUnicodeWriter_WriteSubstring(writer, subject, cursor, found) < 0 || PyUnicodeWriter_WriteStr(writer, replacement) < 0) {
                PyUnicodeWriter_Discard(writer);
                return NULL;
            }
            cursor = found + literal_length;
            count++;
        }
        if (PyUnicodeWriter_WriteSubstring(writer, subject, cursor, length) < 0) {
            PyUnicodeWriter_Discard(writer);
            return NULL;
        }
        PyObject *result = PyUnicodeWriter_Finish(writer);
        if (result == NULL) return NULL;
        return Py_BuildValue("(Nn)", result, count);
    }
    if (PyUnicode_Check(subject)) {
        PyErr_SetString(PyExc_TypeError, "cannot use a bytes pattern on a string-like object");
        return NULL;
    }
    Py_buffer view = {0};
    if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) {
        PyErr_Clear();
        PyErr_Format(PyExc_TypeError, "expected string or bytes-like object, got '%.200s'", Py_TYPE(subject)->tp_name);
        return NULL;
    }
    const uint8_t *data = view.buf;
    size_t length = (size_t)view.len;
    const uint8_t *needle = (const uint8_t *)PyBytes_AS_STRING(literal);
    size_t needle_length = (size_t)PyBytes_GET_SIZE(literal);
    const uint8_t *value = (const uint8_t *)PyBytes_AS_STRING(replacement);
    size_t value_length = (size_t)PyBytes_GET_SIZE(replacement);
    if (needle_length == 0 || limit < 0) {
        PyObject *result = PyBytes_FromStringAndSize((const char *)data, (Py_ssize_t)length);
        PyBuffer_Release(&view);
        if (result == NULL) return NULL;
        return Py_BuildValue("(Nn)", result, (Py_ssize_t)0);
    }
    size_t cursor = 0;
    size_t count = 0;
    while ((limit == 0 || count < (size_t)limit) && cursor + needle_length <= length) {
        const uint8_t *found = memmem(data + cursor, length - cursor, needle, needle_length);
        if (found == NULL) break;
        cursor = (size_t)(found - data) + needle_length;
        count++;
    }
    if (count > 0 && value_length > needle_length && count > ((size_t)PY_SSIZE_T_MAX - length) / (value_length - needle_length)) {
        PyBuffer_Release(&view);
        return PyErr_NoMemory();
    }
    size_t output_length = value_length >= needle_length ? length + count * (value_length - needle_length) : length - count * (needle_length - value_length);
    PyObject *result = PyBytes_FromStringAndSize(NULL, (Py_ssize_t)output_length);
    if (result == NULL) {
        PyBuffer_Release(&view);
        return NULL;
    }
    uint8_t *output = (uint8_t *)PyBytes_AS_STRING(result);
    cursor = 0;
    size_t written = 0;
    for (size_t index = 0; index < count; index++) {
        const uint8_t *found = memmem(data + cursor, length - cursor, needle, needle_length);
        size_t prefix = (size_t)(found - data) - cursor;
        memcpy(output + written, data + cursor, prefix);
        written += prefix;
        memcpy(output + written, value, value_length);
        written += value_length;
        cursor = (size_t)(found - data) + needle_length;
    }
    memcpy(output + written, data + cursor, length - cursor);
    PyBuffer_Release(&view);
    return Py_BuildValue("(Nn)", result, (Py_ssize_t)count);
}

static PyObject *bridge_subn_callable(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 7) {
        PyErr_Format(PyExc_TypeError, "subn_callable() takes exactly 7 arguments (%zd given)", nargs);
        return NULL;
    }
    PyObject *pattern = args[0];
    void *handle = PyLong_AsVoidPtr(args[1]);
    PyObject *groupindex = args[2];
    PyObject *pattern_value = args[3];
    PyObject *subject = args[4];
    PyObject *callback = args[5];
    Py_ssize_t limit;
    if (PyErr_Occurred() || !zig_index_arg(args[6], &limit)) return NULL;
    Py_buffer view = {0};
    const uint8_t *data;
    size_t length;
    uint8_t kind = 1;
    int text_mode = PyUnicode_Check(subject);
    if (text_mode) {
        if (PyBytes_Check(pattern_value)) {
            PyErr_SetString(PyExc_TypeError, "cannot use a bytes pattern on a string-like object");
            return NULL;
        }
        data = PyUnicode_DATA(subject);
        length = (size_t)PyUnicode_GET_LENGTH(subject);
        kind = (uint8_t)PyUnicode_KIND(subject);
    } else {
        if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) {
            PyErr_Clear();
            PyErr_Format(PyExc_TypeError, "expected string or bytes-like object, got '%.200s'", Py_TYPE(subject)->tp_name);
            return NULL;
        }
        if (PyUnicode_Check(pattern_value)) {
            PyBuffer_Release(&view);
            PyErr_SetString(PyExc_TypeError, "cannot use a string pattern on a bytes-like object");
            return NULL;
        }
        data = view.buf;
        length = (size_t)view.len;
    }
    if (limit < 0) {
        PyObject *unchanged = text_mode ? PyUnicode_Substring(subject, 0, (Py_ssize_t)length) : PyBytes_FromStringAndSize((const char *)data, (Py_ssize_t)length);
        if (view.obj != NULL) PyBuffer_Release(&view);
        if (unchanged == NULL) return NULL;
        return Py_BuildValue("(Nn)", unchanged, (Py_ssize_t)0);
    }
    size_t groups = rebar_zig_groups(handle);
    size_t stride = groups + 1;
    ZigCaptureBuffer buffer;
    intptr_t count = zig_collect_growing(handle, data, length, kind, 0, length, groups, limit > 0 ? (size_t)limit : 0, &buffer);
    if (count < 0) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        if (count == -2) return PyErr_NoMemory();
        PyErr_SetString(PyExc_RuntimeError, "Zig matcher rejected the callable-replacement bridge call");
        return NULL;
    }
    size_t words = buffer.words_per_match;
    if (text_mode) {
        PyUnicodeWriter *writer = PyUnicodeWriter_Create((Py_ssize_t)length);
        if (writer == NULL) {
            zig_capture_release(&buffer);
            return NULL;
        }
        size_t previous = 0;
        for (intptr_t index = 0; index < count; index++) {
            size_t base = (size_t)index * words;
            size_t begin = (size_t)buffer.storage[base];
            size_t finish = (size_t)buffer.storage[base + stride];
            ZigMatch *match = zig_match_new(pattern, subject, groupindex, groups, 0, (Py_ssize_t)length);
            if (match == NULL) {
                PyUnicodeWriter_Discard(writer);
                zig_capture_release(&buffer);
                return NULL;
            }
            memcpy(match->spans, buffer.storage + base, stride * 2 * sizeof(intptr_t));
            match->lastindex = buffer.storage[base + stride * 2];
            PyObject *replacement = PyObject_CallOneArg(callback, (PyObject *)match);
            Py_DECREF(match);
            if (replacement == NULL) {
                PyUnicodeWriter_Discard(writer);
                zig_capture_release(&buffer);
                return NULL;
            }
            if (!PyUnicode_Check(replacement)) {
                PyErr_Format(PyExc_TypeError, "sequence item %zd: expected str instance, %.200s found", (Py_ssize_t)(index * 2 + 1), Py_TYPE(replacement)->tp_name);
                Py_DECREF(replacement);
                PyUnicodeWriter_Discard(writer);
                zig_capture_release(&buffer);
                return NULL;
            }
            int written = PyUnicodeWriter_WriteSubstring(writer, subject, (Py_ssize_t)previous, (Py_ssize_t)begin);
            if (written == 0) written = PyUnicodeWriter_WriteStr(writer, replacement);
            Py_DECREF(replacement);
            if (written < 0) {
                PyUnicodeWriter_Discard(writer);
                zig_capture_release(&buffer);
                return NULL;
            }
            previous = finish;
        }
        if (PyUnicodeWriter_WriteSubstring(writer, subject, (Py_ssize_t)previous, (Py_ssize_t)length) < 0) {
            PyUnicodeWriter_Discard(writer);
            zig_capture_release(&buffer);
            return NULL;
        }
        PyObject *joined = PyUnicodeWriter_Finish(writer);
        zig_capture_release(&buffer);
        if (joined == NULL) return NULL;
        return Py_BuildValue("(Nn)", joined, (Py_ssize_t)count);
    }
    if ((size_t)count > ((size_t)PY_SSIZE_T_MAX - 1) / 2) {
        PyBuffer_Release(&view);
        zig_capture_release(&buffer);
        return PyErr_NoMemory();
    }
    PyObject *pieces = PyList_New((Py_ssize_t)count * 2 + 1);
    if (pieces == NULL) {
        PyBuffer_Release(&view);
        zig_capture_release(&buffer);
        return NULL;
    }
    size_t previous = 0;
    Py_ssize_t output = 0;
    for (intptr_t index = 0; index < count; index++) {
        size_t base = (size_t)index * words;
        size_t begin = (size_t)buffer.storage[base];
        size_t finish = (size_t)buffer.storage[base + stride];
        PyObject *prefix = PyBytes_FromStringAndSize((const char *)data + previous, (Py_ssize_t)(begin - previous));
        ZigMatch *match = zig_match_new(pattern, subject, groupindex, groups, 0, (Py_ssize_t)length);
        if (prefix == NULL || match == NULL) {
            Py_XDECREF(prefix);
            Py_XDECREF(match);
            Py_DECREF(pieces);
            PyBuffer_Release(&view);
            zig_capture_release(&buffer);
            return NULL;
        }
        memcpy(match->spans, buffer.storage + base, stride * 2 * sizeof(intptr_t));
        match->lastindex = buffer.storage[base + stride * 2];
        PyObject *replacement = PyObject_CallOneArg(callback, (PyObject *)match);
        Py_DECREF(match);
        if (replacement == NULL) {
            Py_DECREF(prefix);
            Py_DECREF(pieces);
            PyBuffer_Release(&view);
            zig_capture_release(&buffer);
            return NULL;
        }
        PyList_SET_ITEM(pieces, output++, prefix);
        PyList_SET_ITEM(pieces, output++, replacement);
        previous = finish;
    }
    PyObject *tail = PyBytes_FromStringAndSize((const char *)data + previous, (Py_ssize_t)(length - previous));
    if (tail == NULL) {
        Py_DECREF(pieces);
        PyBuffer_Release(&view);
        zig_capture_release(&buffer);
        return NULL;
    }
    PyList_SET_ITEM(pieces, output, tail);
    PyObject *empty = PyBytes_FromStringAndSize("", 0);
    PyObject *joined = empty == NULL ? NULL : PyBytes_Join(empty, pieces);
    Py_XDECREF(empty);
    Py_DECREF(pieces);
    PyBuffer_Release(&view);
    zig_capture_release(&buffer);
    if (joined == NULL) return NULL;
    return Py_BuildValue("(Nn)", joined, (Py_ssize_t)count);
}

static PyObject *bridge_bound_substitute(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames, int want_count) {
    const char *method = want_count ? "subn" : "sub";
    Py_ssize_t keyword_count = kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    if (nargs < 7 || nargs - 7 + keyword_count > 3) {
        PyErr_Format(PyExc_TypeError, "%s() takes at most 3 arguments (%zd given)", method, nargs - 7 + keyword_count);
        return NULL;
    }
    PyObject *replacement = nargs >= 8 ? args[7] : NULL;
    PyObject *subject = nargs >= 9 ? args[8] : NULL;
    PyObject *count = nargs >= 10 ? args[9] : Py_GetConstantBorrowed(Py_CONSTANT_ZERO);
    for (Py_ssize_t index = 0; index < keyword_count; index++) {
        PyObject *name = PyTuple_GET_ITEM(kwnames, index);
        if (PyUnicode_CompareWithASCIIString(name, "repl") == 0) {
            if (nargs >= 8) {
                PyErr_Format(PyExc_TypeError, "argument for %s() given by name ('repl') and position (1)", method);
                return NULL;
            }
            replacement = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "string") == 0) {
            if (nargs >= 9) {
                PyErr_Format(PyExc_TypeError, "argument for %s() given by name ('string') and position (2)", method);
                return NULL;
            }
            subject = args[nargs + index];
        } else if (PyUnicode_CompareWithASCIIString(name, "count") == 0) {
            if (nargs >= 10) {
                PyErr_Format(PyExc_TypeError, "argument for %s() given by name ('count') and position (3)", method);
                return NULL;
            }
            count = args[nargs + index];
        } else {
            PyErr_Format(PyExc_TypeError, "%s() got an unexpected keyword argument '%U'", method, name);
            return NULL;
        }
    }
    if (replacement == NULL || subject == NULL) {
        const char *name = replacement == NULL ? "repl" : "string";
        int position = replacement == NULL ? 1 : 2;
        PyErr_Format(PyExc_TypeError, "%s() missing required argument '%s' (pos %d)", method, name, position);
        return NULL;
    }
    PyObject *result;
    if (PyCallable_Check(replacement)) {
        PyObject *call[7] = {args[0], args[1], args[2], args[3], subject, replacement, count};
        result = bridge_subn_callable(module, call, 7);
    } else {
        PyObject *raw = replacement;
        PyObject *owned = NULL;
        if (PyByteArray_Check(replacement) || PyMemoryView_Check(replacement)) {
            owned = PyBytes_FromObject(replacement);
            if (owned == NULL) return NULL;
            raw = owned;
        }
        if (!PyUnicode_Check(raw) && !PyBytes_Check(raw)) {
            if (PyObject_Hash(raw) == -1 && PyErr_Occurred()) {
                Py_XDECREF(owned);
                return NULL;
            }
            PyErr_Format(PyExc_TypeError, "decoding to str: need a bytes-like object, %.200s found", Py_TYPE(raw)->tp_name);
            Py_XDECREF(owned);
            return NULL;
        }
        int text_mode = PyUnicode_Check(args[3]);
        if (text_mode != PyUnicode_Check(raw)) {
            PyErr_Format(PyExc_TypeError, "sequence item 0: expected %s, %.200s found", text_mode ? "str instance" : "a bytes-like object", Py_TYPE(raw)->tp_name);
            Py_XDECREF(owned);
            return NULL;
        }
        int literal = 0;
        if (args[4] != Py_None) {
            literal = PyUnicode_Check(raw) ? PyUnicode_FindChar(raw, '\\', 0, PyUnicode_GET_LENGTH(raw), 1) < 0 : memchr(PyBytes_AS_STRING(raw), '\\', (size_t)PyBytes_GET_SIZE(raw)) == NULL;
            if (PyErr_Occurred()) {
                Py_XDECREF(owned);
                return NULL;
            }
        }
        if (literal) {
            PyObject *call[4] = {args[4], raw, subject, count};
            result = bridge_literal_subn(module, call, 4);
        } else {
            PyObject *tokens = PyDict_GetItemWithError(args[5], raw);
            if (tokens == NULL && PyErr_Occurred()) {
                Py_XDECREF(owned);
                return NULL;
            }
            PyObject *created = NULL;
            if (tokens == NULL) {
                created = PyObject_CallMethod(args[0], "_cache_template", "OO", replacement, subject);
                if (created == NULL) {
                    Py_XDECREF(owned);
                    return NULL;
                }
                tokens = created;
            }
            PyObject *call[6] = {args[1], args[3], subject, args[6], tokens, count};
            result = bridge_subn(module, call, 6);
            Py_XDECREF(created);
        }
        Py_XDECREF(owned);
    }
    if (result == NULL || want_count) return result;
    if (!PyTuple_Check(result) || PyTuple_GET_SIZE(result) != 2) {
        Py_XDECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Zig replacement did not return a result/count pair");
        return NULL;
    }
    PyObject *value = Py_NewRef(PyTuple_GET_ITEM(result, 0));
    Py_DECREF(result);
    return value;
}

static PyObject *bridge_bound_sub(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    return bridge_bound_substitute(module, args, nargs, kwnames, 0);
}

static PyObject *bridge_bound_subn(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    return bridge_bound_substitute(module, args, nargs, kwnames, 1);
}

static PyObject *bridge_initialize_pattern(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 9) {
        PyErr_Format(PyExc_TypeError, "initialize_pattern() takes exactly 9 arguments (%zd given)", nargs);
        return NULL;
    }
    static const char *attribute_names[] = {"pattern", "flags", "groups", "_groupindex", "_handle", "_literal", "_templates"};
    static const size_t argument_indexes[] = {1, 2, 3, 5, 6, 7, 8};
    static PyObject *attribute_keys[7] = {NULL};
    for (size_t index = 0; index < 7; index++) {
        if (attribute_keys[index] == NULL) {
            attribute_keys[index] = PyUnicode_InternFromString(attribute_names[index]);
            if (attribute_keys[index] == NULL) return NULL;
        }
        if (PyObject_GenericSetAttr(args[0], attribute_keys[index], args[argument_indexes[index]]) < 0) return NULL;
    }
    Py_RETURN_NONE;
}

static PyMethodDef bridge_methods[] = {
    {"compile", (PyCFunction)(void (*)(void))bridge_compile, METH_FASTCALL, "Compile a Zig regex and return its metadata in one boundary crossing."},
    {"free", (PyCFunction)bridge_free, METH_O, "Release a compiled Zig regex."},
    {"initialize_pattern", (PyCFunction)(void (*)(void))bridge_initialize_pattern, METH_FASTCALL, "Initialize a read-only Zig pattern in one native boundary crossing."},
    {"pattern_iterator", (PyCFunction)(void (*)(void))bridge_pattern_iterator, METH_FASTCALL, "Create a lazy batched Zig iterator or scanner in one boundary crossing."},
    {"bound_finditer", (PyCFunction)(void (*)(void))bridge_bound_finditer, METH_FASTCALL | METH_KEYWORDS, "bound_finditer($module, pattern, handle, groupindex, pattern_value, groups, string, pos=0, endpos=9223372036854775807)\n--\n\nRun a bound Zig finditer with cached pattern metadata."},
    {"bound_scanner", (PyCFunction)(void (*)(void))bridge_bound_scanner, METH_FASTCALL | METH_KEYWORDS, "bound_scanner($module, pattern, handle, groupindex, pattern_value, groups, string, pos=0, endpos=9223372036854775807)\n--\n\nRun a bound Zig scanner with cached pattern metadata."},
    {"pattern_match", (PyCFunction)(void (*)(void))bridge_pattern_match, METH_FASTCALL, "Validate a pattern call, run Zig, and construct the match in one boundary crossing."},
    {"bound_search", (PyCFunction)(void (*)(void))bridge_bound_search, METH_FASTCALL | METH_KEYWORDS, "bound_search($module, pattern, handle, groupindex, pattern_value, literal, string, pos=0, endpos=9223372036854775807)\n--\n\nRun a bound Zig search with cached pattern metadata."},
    {"bound_match", (PyCFunction)(void (*)(void))bridge_bound_match, METH_FASTCALL | METH_KEYWORDS, "bound_match($module, pattern, handle, groupindex, pattern_value, literal, string, pos=0, endpos=9223372036854775807)\n--\n\nRun a bound Zig match with cached pattern metadata."},
    {"bound_fullmatch", (PyCFunction)(void (*)(void))bridge_bound_fullmatch, METH_FASTCALL | METH_KEYWORDS, "bound_fullmatch($module, pattern, handle, groupindex, pattern_value, literal, string, pos=0, endpos=9223372036854775807)\n--\n\nRun a bound Zig fullmatch with cached pattern metadata."},
    {"match_object", (PyCFunction)(void (*)(void))bridge_match_object, METH_FASTCALL, "Run one Zig match and construct its native match object."},
    {"span_object", (PyCFunction)(void (*)(void))bridge_span_object, METH_FASTCALL, "Construct a native Zig match from a known span."},
    {"collect_objects", (PyCFunction)(void (*)(void))bridge_collect_objects, METH_FASTCALL, "Collect Zig matches directly into native match objects."},
    {"span", (PyCFunction)(void (*)(void))bridge_span, METH_FASTCALL, "Run one from-scratch Zig bytecode match."},
    {"match", (PyCFunction)(void (*)(void))bridge_match, METH_FASTCALL, "Run one capture-aware Zig bytecode match."},
    {"collect", (PyCFunction)(void (*)(void))bridge_collect, METH_FASTCALL, "Collect non-overlapping Zig regex matches."},
    {"findall", (PyCFunction)(void (*)(void))bridge_findall, METH_FASTCALL, "Return all Zig regex matches as Python values."},
    {"bound_findall", (PyCFunction)(void (*)(void))bridge_bound_findall, METH_FASTCALL | METH_KEYWORDS, "bound_findall($module, handle, pattern_value, groups, string, pos=0, endpos=9223372036854775807)\n--\n\nRun a bound Zig findall with cached pattern metadata."},
    {"bound_literal_findall", (PyCFunction)(void (*)(void))bridge_bound_literal_findall, METH_FASTCALL | METH_KEYWORDS, "bound_literal_findall($module, literal, string, pos=0, endpos=9223372036854775807)\n--\n\nFind every non-overlapping literal with one native boundary crossing."},
    {"split", (PyCFunction)(void (*)(void))bridge_split, METH_FASTCALL, "Split with one Zig regex boundary crossing."},
    {"bound_split", (PyCFunction)(void (*)(void))bridge_bound_split, METH_FASTCALL | METH_KEYWORDS, "bound_split($module, handle, pattern_value, groups, string, maxsplit=0)\n--\n\nRun a bound Zig split with cached pattern metadata."},
    {"subn", (PyCFunction)(void (*)(void))bridge_subn, METH_FASTCALL, "Replace with one Zig regex boundary crossing."},
    {"literal_subn", (PyCFunction)(void (*)(void))bridge_literal_subn, METH_FASTCALL, "Replace a literal with one native boundary crossing."},
    {"subn_callable", (PyCFunction)(void (*)(void))bridge_subn_callable, METH_FASTCALL, "Run a callable Zig replacement with one native matching loop."},
    {"bound_sub", (PyCFunction)(void (*)(void))bridge_bound_sub, METH_FASTCALL | METH_KEYWORDS, "bound_sub($module, pattern, handle, groupindex, pattern_value, literal, templates, groups, repl, string, count=0)\n--\n\nRun a bound Zig substitution with cached pattern metadata."},
    {"bound_subn", (PyCFunction)(void (*)(void))bridge_bound_subn, METH_FASTCALL | METH_KEYWORDS, "bound_subn($module, pattern, handle, groupindex, pattern_value, literal, templates, groups, repl, string, count=0)\n--\n\nRun a bound Zig substitution/count with cached pattern metadata."},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef bridge_module = {
    PyModuleDef_HEAD_INIT,
    "_zig_bridge",
    "Dependency-free CPython bridge for the from-scratch Zig regex probe.",
    -1,
    bridge_methods,
    NULL,
    NULL,
    NULL,
    NULL,
};

PyMODINIT_FUNC PyInit__zig_bridge(void) {
    if (PyType_Ready(&ZigMatchType) < 0 || PyType_Ready(&ZigIteratorType) < 0 || PyType_Ready(&ZigScannerType) < 0) return NULL;
    if (zig_default_endpos == NULL) {
        zig_default_endpos = PyLong_FromSsize_t(PY_SSIZE_T_MAX);
        if (zig_default_endpos == NULL) return NULL;
    }
    PyObject *module = PyModule_Create(&bridge_module);
    if (module == NULL) return NULL;
    if (PyModule_AddObjectRef(module, "Match", (PyObject *)&ZigMatchType) < 0) {
        Py_DECREF(module);
        return NULL;
    }
    return module;
}
