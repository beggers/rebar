//go:build rebar_go_python_bridge

#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include <limits.h>
#include <stdint.h>
#include <string.h>

/*
 * Independently owned CPython 3.14 adapter for the experiment's explicit Go
 * ABI. It does not import re, _sre, another candidate, or an external matcher.
 * The Go runtime never retains a CPython input or output pointer.
 */

enum {
    REBAR_GO_ABI_V1 = 0x52424731,
    REBAR_GO_INPUT_BYTES = 0,
    REBAR_GO_INPUT_UNICODE_1 = 1,
    REBAR_GO_INPUT_UNICODE_2 = 2,
    REBAR_GO_INPUT_UNICODE_4 = 4,
    REBAR_GO_STATUS_OK = 0,
    REBAR_GO_STATUS_PATTERN = 1,
    REBAR_GO_STATUS_ARGUMENT = 2,
    REBAR_GO_STATUS_RUNTIME = 3,
    REBAR_GO_STATUS_HANDLE = 4,
    REBAR_GO_IGNORECASE = 2,
    REBAR_GO_LOCALE = 4,
    REBAR_GO_MULTILINE = 8,
    REBAR_GO_DOTALL = 16,
    REBAR_GO_UNICODE = 32,
    REBAR_GO_VERBOSE = 64,
    REBAR_GO_DEBUG = 128,
    REBAR_GO_ASCII = 256
};

typedef struct {
    int32_t category;
    int64_t position;
    int64_t line;
    int64_t column;
    char message[256];
} rebar_go_status_v1;

typedef struct {
    int64_t *spans;
    uint64_t span_capacity;
    uint64_t capture_count;
    int64_t lastindex;
    uint32_t matched;
} rebar_go_match_v1;

extern uint32_t rebar_go_abi_version(void);
extern int rebar_go_compile(uint32_t, void *, uint64_t, uint32_t,
                            uintptr_t *, rebar_go_status_v1 *);
extern int rebar_go_metadata(uintptr_t, uint32_t *, uint64_t *,
                             rebar_go_status_v1 *);
extern int rebar_go_group_name(uintptr_t, uint64_t, void *, uint64_t,
                               uint64_t *, rebar_go_status_v1 *);
extern int rebar_go_match_at(uintptr_t, uint32_t, void *, uint64_t,
                             int64_t, int64_t, uint32_t,
                             rebar_go_match_v1 *, rebar_go_status_v1 *);
extern int rebar_go_search(uintptr_t, uint32_t, void *, uint64_t,
                           int64_t, int64_t, uint32_t,
                           rebar_go_match_v1 *, rebar_go_status_v1 *);
extern int rebar_go_fullmatch(uintptr_t, uint32_t, void *, uint64_t,
                              int64_t, int64_t,
                              rebar_go_match_v1 *, rebar_go_status_v1 *);
extern int rebar_go_release(uintptr_t, rebar_go_status_v1 *);

typedef struct {
    PyTypeObject *pattern_type;
    PyTypeObject *match_type;
    PyTypeObject *scanner_type;
    PyObject *pattern_error;
} GoModuleState;

typedef struct {
    uint32_t kind;
    void *data;
    Py_ssize_t length;
    Py_buffer view;
    int holds_view;
} GoInputLease;

typedef struct {
    PyObject_HEAD
    PyObject *original;
    PyObject *group_names;
    uintptr_t handle;
    uint32_t flags;
    Py_ssize_t group_count;
    int is_text;
} GoPattern;

typedef struct {
    PyObject_HEAD
    GoPattern *pattern;
    PyObject *subject;
    PyObject *cached_regs;
    int64_t *spans;
    Py_ssize_t capture_count;
    Py_ssize_t pos;
    Py_ssize_t endpos;
    Py_ssize_t lastindex;
    Py_buffer view;
    int holds_view;
} GoMatch;

typedef struct {
    PyObject_HEAD
    GoPattern *pattern;
    PyObject *subject;
    Py_buffer view;
    uint32_t kind;
    void *data;
    Py_ssize_t length;
    Py_ssize_t original_pos;
    Py_ssize_t position;
    Py_ssize_t endpos;
    int holds_view;
    int reject_empty;
    int exhausted;
} GoScanner;

typedef enum {
    GO_OPERATION_MATCH,
    GO_OPERATION_SEARCH,
    GO_OPERATION_FULLMATCH
} GoMatchOperation;

static GoModuleState *go_type_state(PyTypeObject *type)
{
    return (GoModuleState *)PyType_GetModuleState(type);
}

static int go_raise_status(GoModuleState *state, PyObject *pattern,
                           const rebar_go_status_v1 *status)
{
    if (status->category != REBAR_GO_STATUS_PATTERN) {
        PyObject *exception = status->category == REBAR_GO_STATUS_ARGUMENT
                                  ? PyExc_TypeError
                                  : PyExc_RuntimeError;
        PyErr_SetString(exception, status->message);
        return -1;
    }

    PyObject *message = NULL;
    if (status->position < 0) {
        message = PyUnicode_FromString(status->message);
    } else if (status->line > 1) {
        message = PyUnicode_FromFormat(
            "%s at position %lld (line %lld, column %lld)",
            status->message, (long long)status->position,
            (long long)status->line, (long long)status->column);
    } else {
        message = PyUnicode_FromFormat("%s at position %lld",
                                       status->message,
                                       (long long)status->position);
    }
    if (message == NULL) {
        return -1;
    }

    PyObject *instance = PyObject_CallOneArg(state->pattern_error, message);
    Py_DECREF(message);
    if (instance == NULL) {
        return -1;
    }

    PyObject *raw_message = PyUnicode_FromString(status->message);
    PyObject *position = status->position < 0
                             ? Py_NewRef(Py_None)
                             : PyLong_FromLongLong(status->position);
    PyObject *line = status->position < 0
                         ? Py_NewRef(Py_None)
                         : PyLong_FromLongLong(status->line);
    PyObject *column = status->position < 0
                           ? Py_NewRef(Py_None)
                           : PyLong_FromLongLong(status->column);
    if (raw_message == NULL || position == NULL || line == NULL ||
        column == NULL ||
        PyObject_SetAttrString(instance, "msg", raw_message) < 0 ||
        PyObject_SetAttrString(instance, "pattern",
                               pattern == NULL ? Py_None : pattern) < 0 ||
        PyObject_SetAttrString(instance, "pos", position) < 0 ||
        PyObject_SetAttrString(instance, "lineno", line) < 0 ||
        PyObject_SetAttrString(instance, "colno", column) < 0) {
        Py_XDECREF(raw_message);
        Py_XDECREF(position);
        Py_XDECREF(line);
        Py_XDECREF(column);
        Py_DECREF(instance);
        return -1;
    }
    Py_DECREF(raw_message);
    Py_DECREF(position);
    Py_DECREF(line);
    Py_DECREF(column);
    PyErr_SetObject(state->pattern_error, instance);
    Py_DECREF(instance);
    return -1;
}

static int go_read_index(PyObject *value, Py_ssize_t *result)
{
    Py_ssize_t converted = PyNumber_AsSsize_t(value, PyExc_OverflowError);
    if (converted == -1 && PyErr_Occurred()) {
        return -1;
    }
    *result = converted;
    return 0;
}

static int go_read_flags(PyObject *value, uint32_t *result)
{
    if (value == NULL) {
        *result = 0;
        return 0;
    }
    PyObject *index = PyNumber_Index(value);
    if (index == NULL) {
        return -1;
    }
    unsigned long converted = PyLong_AsUnsignedLong(index);
    Py_DECREF(index);
    if ((converted == (unsigned long)-1 && PyErr_Occurred()) ||
        converted > UINT32_MAX) {
        if (!PyErr_Occurred()) {
            PyErr_SetString(PyExc_OverflowError,
                            "regular-expression flags exceed 32 bits");
        }
        return -1;
    }
    *result = (uint32_t)converted;
    return 0;
}

static void go_release_lease(GoInputLease *lease)
{
    if (lease->holds_view) {
        PyBuffer_Release(&lease->view);
        lease->holds_view = 0;
    }
}

static int go_prepare_input(PyObject *subject, int require_text,
                            GoInputLease *lease)
{
    memset(lease, 0, sizeof(*lease));
    if (require_text) {
        if (!PyUnicode_Check(subject)) {
            PyErr_SetString(PyExc_TypeError,
                            "cannot use a string pattern on a bytes-like object");
            return -1;
        }
        int kind = PyUnicode_KIND(subject);
        if (kind != PyUnicode_1BYTE_KIND && kind != PyUnicode_2BYTE_KIND &&
            kind != PyUnicode_4BYTE_KIND) {
            PyErr_SetString(PyExc_RuntimeError,
                            "unsupported CPython Unicode storage kind");
            return -1;
        }
        lease->kind = (uint32_t)kind;
        lease->data = PyUnicode_DATA(subject);
        lease->length = PyUnicode_GET_LENGTH(subject);
        return 0;
    }

    if (PyUnicode_Check(subject)) {
        PyErr_SetString(PyExc_TypeError,
                        "cannot use a bytes pattern on a string-like object");
        return -1;
    }
    if (PyObject_GetBuffer(subject, &lease->view, PyBUF_SIMPLE) < 0) {
        PyErr_Clear();
        PyErr_Format(PyExc_TypeError,
                     "expected string or bytes-like object, got '%.200s'",
                     Py_TYPE(subject)->tp_name);
        return -1;
    }
    lease->holds_view = 1;
    lease->kind = REBAR_GO_INPUT_BYTES;
    lease->data = lease->view.buf;
    lease->length = lease->view.len;
    return 0;
}

static int go_parse_named(const char *function, PyObject *const *args,
                          Py_ssize_t nargs, PyObject *kwnames,
                          const char *const *names, Py_ssize_t field_count,
                          Py_ssize_t required, PyObject **values)
{
    for (Py_ssize_t index = 0; index < field_count; index++) {
        values[index] = NULL;
    }
    Py_ssize_t keyword_count =
        kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    if (nargs > field_count || keyword_count > field_count - nargs) {
        PyErr_Format(PyExc_TypeError,
                     "%s() takes at most %zd arguments (%zd given)",
                     function, field_count, nargs + keyword_count);
        return -1;
    }
    for (Py_ssize_t index = 0; index < nargs; index++) {
        values[index] = args[index];
    }
    for (Py_ssize_t index = 0; index < keyword_count; index++) {
        PyObject *name = PyTuple_GET_ITEM(kwnames, index);
        Py_ssize_t selected = -1;
        for (Py_ssize_t field = 0; field < field_count; field++) {
            int comparison = PyUnicode_CompareWithASCIIString(name,
                                                               names[field]);
            if (comparison == 0) {
                selected = field;
                break;
            }
            if (comparison == -1 && PyErr_Occurred()) {
                return -1;
            }
        }
        if (selected < 0) {
            PyErr_Format(PyExc_TypeError,
                         "%s() got an unexpected keyword argument '%U'",
                         function, name);
            return -1;
        }
        if (values[selected] != NULL) {
            PyErr_Format(PyExc_TypeError,
                         "argument for %s() given by name ('%s') and position (%zd)",
                         function, names[selected], selected + 1);
            return -1;
        }
        values[selected] = args[nargs + index];
    }
    for (Py_ssize_t index = 0; index < required; index++) {
        if (values[index] == NULL) {
            PyErr_Format(PyExc_TypeError,
                         "%s() missing required argument '%s' (pos %zd)",
                         function, names[index], index + 1);
            return -1;
        }
    }
    return 0;
}

static int go_parse_window(const char *function, PyObject *const *args,
                           Py_ssize_t nargs, PyObject *kwnames,
                           PyObject **subject, Py_ssize_t *start,
                           Py_ssize_t *end)
{
    static const char *const names[] = {"string", "pos", "endpos"};
    PyObject *values[3];
    if (go_parse_named(function, args, nargs, kwnames, names, 3, 1,
                       values) < 0) {
        return -1;
    }
    *subject = values[0];
    *start = 0;
    *end = PY_SSIZE_T_MAX;
    if (values[1] != NULL && go_read_index(values[1], start) < 0) {
        return -1;
    }
    if (values[2] != NULL && go_read_index(values[2], end) < 0) {
        return -1;
    }
    return 0;
}

static Py_ssize_t go_clamp(Py_ssize_t value, Py_ssize_t length)
{
    if (value < 0) {
        return 0;
    }
    return value > length ? length : value;
}

static int go_pattern_traverse(GoPattern *self, visitproc visit, void *arg)
{
    Py_VISIT(self->original);
    Py_VISIT(self->group_names);
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static int go_pattern_clear(GoPattern *self)
{
    if (self->handle != 0) {
        rebar_go_status_v1 status = {0};
        uintptr_t handle = self->handle;
        self->handle = 0;
        (void)rebar_go_release(handle, &status);
    }
    Py_CLEAR(self->original);
    Py_CLEAR(self->group_names);
    return 0;
}

static void go_pattern_dealloc(GoPattern *self)
{
    PyTypeObject *type = Py_TYPE(self);
    PyObject_GC_UnTrack(self);
    (void)go_pattern_clear(self);
    type->tp_free((PyObject *)self);
    Py_DECREF(type);
}

static int go_match_traverse(GoMatch *self, visitproc visit, void *arg)
{
    Py_VISIT(self->pattern);
    Py_VISIT(self->subject);
    Py_VISIT(self->cached_regs);
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static int go_match_clear(GoMatch *self)
{
    if (self->holds_view) {
        PyBuffer_Release(&self->view);
        self->holds_view = 0;
    }
    Py_CLEAR(self->cached_regs);
    Py_CLEAR(self->subject);
    Py_CLEAR(self->pattern);
    return 0;
}

static void go_match_dealloc(GoMatch *self)
{
    PyTypeObject *type = Py_TYPE(self);
    PyObject_GC_UnTrack(self);
    (void)go_match_clear(self);
    PyMem_Free(self->spans);
    self->spans = NULL;
    type->tp_free((PyObject *)self);
    Py_DECREF(type);
}

static int go_scanner_traverse(GoScanner *self, visitproc visit, void *arg)
{
    Py_VISIT(self->pattern);
    Py_VISIT(self->subject);
    Py_VISIT(Py_TYPE(self));
    return 0;
}

static int go_scanner_clear(GoScanner *self)
{
    if (self->holds_view) {
        PyBuffer_Release(&self->view);
        self->holds_view = 0;
    }
    Py_CLEAR(self->subject);
    Py_CLEAR(self->pattern);
    self->data = NULL;
    return 0;
}

static void go_scanner_dealloc(GoScanner *self)
{
    PyTypeObject *type = Py_TYPE(self);
    PyObject_GC_UnTrack(self);
    (void)go_scanner_clear(self);
    type->tp_free((PyObject *)self);
    Py_DECREF(type);
}

static PyObject *go_slice_subject(PyObject *subject, int is_text,
                                  const Py_buffer *view, Py_ssize_t start,
                                  Py_ssize_t end)
{
    if (start < 0 || end < start) {
        Py_RETURN_NONE;
    }
    if (is_text) {
        return PyUnicode_Substring(subject, start, end);
    }
    if (view == NULL || view->buf == NULL) {
        if (start == end) {
            return PyBytes_FromStringAndSize("", 0);
        }
        PyErr_SetString(PyExc_RuntimeError,
                        "live bytes capture has no owned exported buffer");
        return NULL;
    }
    return PyBytes_FromStringAndSize((const char *)view->buf + start,
                                     end - start);
}

static PyObject *go_make_match(GoPattern *pattern, PyObject *subject,
                               int64_t *spans, Py_ssize_t capture_count,
                               Py_ssize_t pos, Py_ssize_t endpos,
                               Py_ssize_t lastindex)
{
    GoModuleState *state = go_type_state(Py_TYPE(pattern));
    if (state == NULL) {
        PyMem_Free(spans);
        return NULL;
    }
    GoMatch *match = PyObject_GC_New(GoMatch, state->match_type);
    if (match == NULL) {
        PyMem_Free(spans);
        return NULL;
    }
    match->pattern = (GoPattern *)Py_NewRef((PyObject *)pattern);
    match->subject = Py_NewRef(subject);
    match->cached_regs = NULL;
    match->spans = spans;
    match->capture_count = capture_count;
    match->pos = pos;
    match->endpos = endpos;
    match->lastindex = lastindex;
    memset(&match->view, 0, sizeof(match->view));
    match->holds_view = 0;
    if (!pattern->is_text) {
        if (PyObject_GetBuffer(subject, &match->view, PyBUF_SIMPLE) < 0) {
            Py_DECREF(match);
            return NULL;
        }
        match->holds_view = 1;
    }
    PyObject_GC_Track(match);
    return (PyObject *)match;
}

static PyObject *go_execute(GoPattern *pattern, PyObject *subject,
                            const GoInputLease *lease, Py_ssize_t start,
                            Py_ssize_t end, Py_ssize_t original_pos,
                            int reject_empty, GoMatchOperation operation)
{
    GoModuleState *state = go_type_state(Py_TYPE(pattern));
    if (state == NULL) {
        return NULL;
    }
    if (pattern->group_count > (PY_SSIZE_T_MAX / 2) - 1) {
        PyErr_NoMemory();
        return NULL;
    }
    Py_ssize_t captures = pattern->group_count + 1;
    int64_t *spans = PyMem_Calloc((size_t)captures * 2, sizeof(*spans));
    if (spans == NULL) {
        PyErr_NoMemory();
        return NULL;
    }
    rebar_go_match_v1 result = {
        .spans = spans,
        .span_capacity = (uint64_t)captures,
        .capture_count = 0,
        .lastindex = -1,
        .matched = 0,
    };
    rebar_go_status_v1 status = {0};
    int outcome;
    if (operation == GO_OPERATION_SEARCH) {
        outcome = rebar_go_search(
            pattern->handle, lease->kind, lease->data,
            (uint64_t)lease->length, (int64_t)start, (int64_t)end,
            (uint32_t)reject_empty, &result, &status);
    } else if (operation == GO_OPERATION_FULLMATCH) {
        outcome = rebar_go_fullmatch(
            pattern->handle, lease->kind, lease->data,
            (uint64_t)lease->length, (int64_t)start, (int64_t)end,
            &result, &status);
    } else {
        outcome = rebar_go_match_at(
            pattern->handle, lease->kind, lease->data,
            (uint64_t)lease->length, (int64_t)start, (int64_t)end,
            (uint32_t)reject_empty, &result, &status);
    }
    if (outcome != 0) {
        PyMem_Free(spans);
        (void)go_raise_status(state, pattern->original, &status);
        return NULL;
    }
    if (!result.matched) {
        PyMem_Free(spans);
        Py_RETURN_NONE;
    }
    if (result.capture_count != (uint64_t)captures ||
        result.lastindex > (int64_t)pattern->group_count) {
        PyMem_Free(spans);
        PyErr_SetString(PyExc_RuntimeError,
                        "owned Go matcher returned inconsistent captures");
        return NULL;
    }
    return go_make_match(pattern, subject, spans, captures, original_pos,
                         end, (Py_ssize_t)result.lastindex);
}

static PyObject *go_pattern_window(GoPattern *self,
                                   PyObject *const *args, Py_ssize_t nargs,
                                   PyObject *kwnames, const char *name,
                                   GoMatchOperation operation)
{
    PyObject *subject;
    Py_ssize_t start, end;
    if (go_parse_window(name, args, nargs, kwnames, &subject, &start,
                        &end) < 0) {
        return NULL;
    }
    GoInputLease lease;
    if (go_prepare_input(subject, self->is_text, &lease) < 0) {
        return NULL;
    }
    start = go_clamp(start, lease.length);
    end = go_clamp(end, lease.length);
    PyObject *result = go_execute(self, subject, &lease, start, end,
                                  start, 0, operation);
    go_release_lease(&lease);
    return result;
}

static PyObject *go_pattern_search(GoPattern *self,
                                   PyObject *const *args, Py_ssize_t nargs,
                                   PyObject *kwnames)
{
    return go_pattern_window(self, args, nargs, kwnames, "search",
                             GO_OPERATION_SEARCH);
}

static PyObject *go_pattern_match(GoPattern *self,
                                  PyObject *const *args, Py_ssize_t nargs,
                                  PyObject *kwnames)
{
    return go_pattern_window(self, args, nargs, kwnames, "match",
                             GO_OPERATION_MATCH);
}

static PyObject *go_pattern_fullmatch(GoPattern *self,
                                      PyObject *const *args,
                                      Py_ssize_t nargs, PyObject *kwnames)
{
    return go_pattern_window(self, args, nargs, kwnames, "fullmatch",
                             GO_OPERATION_FULLMATCH);
}

static PyObject *go_build_scanner(GoPattern *pattern, PyObject *subject,
                                  Py_ssize_t start, Py_ssize_t end)
{
    GoModuleState *state = go_type_state(Py_TYPE(pattern));
    if (state == NULL) {
        return NULL;
    }
    GoInputLease lease;
    if (go_prepare_input(subject, pattern->is_text, &lease) < 0) {
        return NULL;
    }
    GoScanner *scanner = PyObject_GC_New(GoScanner, state->scanner_type);
    if (scanner == NULL) {
        go_release_lease(&lease);
        return NULL;
    }
    scanner->pattern = (GoPattern *)Py_NewRef((PyObject *)pattern);
    scanner->subject = Py_NewRef(subject);
    scanner->kind = lease.kind;
    scanner->data = lease.data;
    scanner->length = lease.length;
    scanner->original_pos = go_clamp(start, lease.length);
    scanner->position = scanner->original_pos;
    scanner->endpos = go_clamp(end, lease.length);
    scanner->reject_empty = 0;
    scanner->exhausted = 0;
    scanner->view = lease.view;
    scanner->holds_view = lease.holds_view;
    lease.holds_view = 0;
    PyObject_GC_Track(scanner);
    return (PyObject *)scanner;
}

static PyObject *go_pattern_scanner(GoPattern *self,
                                    PyObject *const *args, Py_ssize_t nargs,
                                    PyObject *kwnames)
{
    PyObject *subject;
    Py_ssize_t start, end;
    if (go_parse_window("scanner", args, nargs, kwnames, &subject,
                        &start, &end) < 0) {
        return NULL;
    }
    return go_build_scanner(self, subject, start, end);
}

static PyObject *go_scanner_advance(GoScanner *self,
                                    GoMatchOperation operation)
{
    if (self->exhausted) {
        Py_RETURN_NONE;
    }
    GoInputLease lease = {
        .kind = self->kind,
        .data = self->data,
        .length = self->length,
        .holds_view = 0,
    };
    PyObject *match = go_execute(self->pattern, self->subject, &lease,
                                 self->position, self->endpos,
                                 self->original_pos, self->reject_empty,
                                 operation);
    if (match == NULL) {
        return NULL;
    }
    if (match == Py_None) {
        self->exhausted = 1;
        return match;
    }
    GoMatch *value = (GoMatch *)match;
    Py_ssize_t beginning = (Py_ssize_t)value->spans[0];
    Py_ssize_t ending = (Py_ssize_t)value->spans[1];
    self->reject_empty = beginning == ending;
    self->position = ending;
    return match;
}

static PyObject *go_scanner_search(GoScanner *self,
                                   PyObject *Py_UNUSED(ignored))
{
    return go_scanner_advance(self, GO_OPERATION_SEARCH);
}

static PyObject *go_scanner_match(GoScanner *self,
                                  PyObject *Py_UNUSED(ignored))
{
    return go_scanner_advance(self, GO_OPERATION_MATCH);
}

static PyObject *go_scanner_pattern(GoScanner *self, void *closure)
{
    (void)closure;
    return Py_NewRef((PyObject *)self->pattern);
}

static PyObject *go_scanner_reduce_ex(GoScanner *self, PyObject *protocol)
{
    (void)self;
    (void)protocol;
    PyErr_SetString(PyExc_TypeError,
                    "cannot pickle '_sre.SRE_Scanner' object");
    return NULL;
}

static PyObject *go_scanner_reduce(GoScanner *self,
                                   PyObject *Py_UNUSED(ignored))
{
    PyObject *copyreg = PyImport_ImportModule("copyreg");
    if (copyreg == NULL) {
        return NULL;
    }
    PyObject *reconstructor = PyObject_GetAttrString(copyreg,
                                                     "_reconstructor");
    Py_DECREF(copyreg);
    if (reconstructor == NULL) {
        return NULL;
    }
    PyObject *arguments = PyTuple_Pack(3, (PyObject *)Py_TYPE(self),
                                       (PyObject *)&PyBaseObject_Type,
                                       Py_None);
    if (arguments == NULL) {
        Py_DECREF(reconstructor);
        return NULL;
    }
    PyObject *result = PyTuple_Pack(2, reconstructor, arguments);
    Py_DECREF(reconstructor);
    Py_DECREF(arguments);
    return result;
}

static PyObject *go_pattern_finditer(GoPattern *self,
                                     PyObject *const *args,
                                     Py_ssize_t nargs, PyObject *kwnames)
{
    PyObject *scanner = go_pattern_scanner(self, args, nargs, kwnames);
    if (scanner == NULL) {
        return NULL;
    }
    PyObject *search = PyObject_GetAttrString(scanner, "search");
    Py_DECREF(scanner);
    if (search == NULL) {
        return NULL;
    }
    PyObject *iterator = PyCallIter_New(search, Py_None);
    Py_DECREF(search);
    return iterator;
}

static int go_group_index(GoMatch *self, PyObject *group,
                          Py_ssize_t *number)
{
    if (group == NULL) {
        *number = 0;
        return 0;
    }
    if (PyUnicode_Check(group)) {
        PyObject *entry = PyDict_GetItemWithError(self->pattern->group_names,
                                                 group);
        if (entry == NULL) {
            if (!PyErr_Occurred()) {
                PyErr_SetString(PyExc_IndexError, "no such group");
            }
            return -1;
        }
        *number = PyLong_AsSsize_t(entry);
        return *number == -1 && PyErr_Occurred() ? -1 : 0;
    }
    if (!PyIndex_Check(group)) {
        PyErr_SetString(PyExc_IndexError, "no such group");
        return -1;
    }
    if (go_read_index(group, number) < 0) {
        return -1;
    }
    if (*number < 0 || *number >= self->capture_count) {
        PyErr_SetString(PyExc_IndexError, "no such group");
        return -1;
    }
    return 0;
}

static PyObject *go_match_group_number(GoMatch *self, Py_ssize_t number,
                                       PyObject *default_value)
{
    int64_t start = self->spans[number * 2];
    int64_t end = self->spans[number * 2 + 1];
    if (start < 0) {
        return Py_NewRef(default_value == NULL ? Py_None : default_value);
    }
    return go_slice_subject(self->subject, self->pattern->is_text,
                            self->holds_view ? &self->view : NULL,
                            (Py_ssize_t)start, (Py_ssize_t)end);
}

PyDoc_STRVAR(go_match_group_doc,
             "group([group1, ...]) -> str or tuple.\n"
             "    Return subgroup(s) of the match by indices or names.\n"
             "    For 0 returns the entire match.");

static PyObject *go_match_group(GoMatch *self, PyObject *args)
{
    Py_ssize_t count = PyTuple_GET_SIZE(args);
    if (count == 0) {
        return go_match_group_number(self, 0, NULL);
    }
    if (count == 1) {
        Py_ssize_t number;
        if (go_group_index(self, PyTuple_GET_ITEM(args, 0), &number) < 0) {
            return NULL;
        }
        return go_match_group_number(self, number, NULL);
    }
    PyObject *result = PyTuple_New(count);
    if (result == NULL) {
        return NULL;
    }
    for (Py_ssize_t index = 0; index < count; index++) {
        Py_ssize_t number;
        if (go_group_index(self, PyTuple_GET_ITEM(args, index), &number) < 0) {
            Py_DECREF(result);
            return NULL;
        }
        PyObject *value = go_match_group_number(self, number, NULL);
        if (value == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        PyTuple_SET_ITEM(result, index, value);
    }
    return result;
}

PyDoc_STRVAR(go_match_groups_doc,
             "groups($self, /, default=None)\n--\n\n"
             "Return a tuple containing all the subgroups of the match, from 1.\n\n"
             "  default\n"
             "    Is used for groups that did not participate in the match.");

static PyObject *go_match_groups(GoMatch *self, PyObject *const *args,
                                 Py_ssize_t nargs, PyObject *kwnames)
{
    static const char *const names[] = {"default"};
    PyObject *values[1];
    if (go_parse_named("groups", args, nargs, kwnames, names, 1, 0,
                       values) < 0) {
        return NULL;
    }
    PyObject *result = PyTuple_New(self->capture_count - 1);
    if (result == NULL) {
        return NULL;
    }
    for (Py_ssize_t index = 1; index < self->capture_count; index++) {
        PyObject *value = go_match_group_number(self, index, values[0]);
        if (value == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        PyTuple_SET_ITEM(result, index - 1, value);
    }
    return result;
}

PyDoc_STRVAR(go_match_groupdict_doc,
             "groupdict($self, /, default=None)\n--\n\n"
             "Return a dictionary containing all the named subgroups of the match, "
             "keyed by the subgroup name.\n\n"
             "  default\n"
             "    Is used for groups that did not participate in the match.");

static PyObject *go_match_groupdict(GoMatch *self,
                                    PyObject *const *args, Py_ssize_t nargs,
                                    PyObject *kwnames)
{
    static const char *const names[] = {"default"};
    PyObject *values[1];
    if (go_parse_named("groupdict", args, nargs, kwnames, names, 1, 0,
                       values) < 0) {
        return NULL;
    }
    PyObject *result = PyDict_New();
    if (result == NULL) {
        return NULL;
    }
    Py_ssize_t position = 0;
    PyObject *key;
    PyObject *number;
    while (PyDict_Next(self->pattern->group_names, &position, &key,
                       &number)) {
        Py_ssize_t index = PyLong_AsSsize_t(number);
        if (index == -1 && PyErr_Occurred()) {
            Py_DECREF(result);
            return NULL;
        }
        PyObject *value = go_match_group_number(self, index, values[0]);
        if (value == NULL || PyDict_SetItem(result, key, value) < 0) {
            Py_XDECREF(value);
            Py_DECREF(result);
            return NULL;
        }
        Py_DECREF(value);
    }
    return result;
}

static PyObject *go_match_coordinate(GoMatch *self, PyObject *const *args,
                                     Py_ssize_t nargs, int which)
{
    if (nargs > 1) {
        PyErr_Format(PyExc_TypeError,
                     "match coordinate takes at most 1 argument (%zd given)",
                     nargs);
        return NULL;
    }
    Py_ssize_t number;
    if (go_group_index(self, nargs == 0 ? NULL : args[0], &number) < 0) {
        return NULL;
    }
    int64_t start = self->spans[number * 2];
    int64_t end = self->spans[number * 2 + 1];
    if (which == 0) {
        return PyLong_FromLongLong(start);
    }
    if (which == 1) {
        return PyLong_FromLongLong(end);
    }
    PyObject *first = PyLong_FromLongLong(start);
    PyObject *second = PyLong_FromLongLong(end);
    if (first == NULL || second == NULL) {
        Py_XDECREF(first);
        Py_XDECREF(second);
        return NULL;
    }
    PyObject *result = PyTuple_Pack(2, first, second);
    Py_DECREF(first);
    Py_DECREF(second);
    return result;
}

PyDoc_STRVAR(go_match_start_doc,
             "start($self, group=0, /)\n--\n\n"
             "Return index of the start of the substring matched by group.");

static PyObject *go_match_start(GoMatch *self, PyObject *const *args,
                                Py_ssize_t nargs)
{
    return go_match_coordinate(self, args, nargs, 0);
}

PyDoc_STRVAR(go_match_end_doc,
             "end($self, group=0, /)\n--\n\n"
             "Return index of the end of the substring matched by group.");

static PyObject *go_match_end(GoMatch *self, PyObject *const *args,
                              Py_ssize_t nargs)
{
    return go_match_coordinate(self, args, nargs, 1);
}

PyDoc_STRVAR(go_match_span_doc,
             "span($self, group=0, /)\n--\n\n"
             "For match object m, return the 2-tuple "
             "(m.start(group), m.end(group)).");

static PyObject *go_match_span(GoMatch *self, PyObject *const *args,
                               Py_ssize_t nargs)
{
    return go_match_coordinate(self, args, nargs, 2);
}

static PyObject *go_match_subscript(GoMatch *self, PyObject *group)
{
    Py_ssize_t number;
    if (go_group_index(self, group, &number) < 0) {
        return NULL;
    }
    return go_match_group_number(self, number, NULL);
}

static PyObject *go_match_expand(GoMatch *self, PyObject *value)
{
    (void)self;
    (void)value;
    PyErr_SetString(PyExc_NotImplementedError,
                    "replacement-template expansion is not implemented "
                    "by the source-only Go experiment");
    return NULL;
}

static PyObject *go_identity_copy(PyObject *self,
                                  PyObject *Py_UNUSED(ignored))
{
    return Py_NewRef(self);
}

static PyObject *go_identity_deepcopy(PyObject *self, PyObject *memo)
{
    (void)memo;
    return Py_NewRef(self);
}

static PyObject *go_match_reduce(GoMatch *self,
                                 PyObject *Py_UNUSED(ignored))
{
    (void)self;
    PyErr_SetString(PyExc_TypeError, "cannot pickle 're.Match' object");
    return NULL;
}

static PyObject *go_match_pattern(GoMatch *self, void *closure)
{
    (void)closure;
    return Py_NewRef((PyObject *)self->pattern);
}

static PyObject *go_match_subject(GoMatch *self, void *closure)
{
    (void)closure;
    return Py_NewRef(self->subject);
}

static PyObject *go_match_pos(GoMatch *self, void *closure)
{
    (void)closure;
    return PyLong_FromSsize_t(self->pos);
}

static PyObject *go_match_endpos(GoMatch *self, void *closure)
{
    (void)closure;
    return PyLong_FromSsize_t(self->endpos);
}

static PyObject *go_match_lastindex(GoMatch *self, void *closure)
{
    (void)closure;
    if (self->lastindex < 0) {
        Py_RETURN_NONE;
    }
    return PyLong_FromSsize_t(self->lastindex);
}

static PyObject *go_match_lastgroup(GoMatch *self, void *closure)
{
    (void)closure;
    if (self->lastindex < 0) {
        Py_RETURN_NONE;
    }
    Py_ssize_t position = 0;
    PyObject *key;
    PyObject *value;
    while (PyDict_Next(self->pattern->group_names, &position, &key,
                       &value)) {
        Py_ssize_t index = PyLong_AsSsize_t(value);
        if (index == -1 && PyErr_Occurred()) {
            return NULL;
        }
        if (index == self->lastindex) {
            return Py_NewRef(key);
        }
    }
    Py_RETURN_NONE;
}

static PyObject *go_match_regs(GoMatch *self, void *closure)
{
    (void)closure;
    if (self->cached_regs != NULL) {
        return Py_NewRef(self->cached_regs);
    }
    PyObject *result = PyTuple_New(self->capture_count);
    if (result == NULL) {
        return NULL;
    }
    for (Py_ssize_t index = 0; index < self->capture_count; index++) {
        PyObject *first = PyLong_FromLongLong(self->spans[index * 2]);
        PyObject *second = PyLong_FromLongLong(self->spans[index * 2 + 1]);
        if (first == NULL || second == NULL) {
            Py_XDECREF(first);
            Py_XDECREF(second);
            Py_DECREF(result);
            return NULL;
        }
        PyObject *pair = PyTuple_Pack(2, first, second);
        Py_DECREF(first);
        Py_DECREF(second);
        if (pair == NULL) {
            Py_DECREF(result);
            return NULL;
        }
        PyTuple_SET_ITEM(result, index, pair);
    }
    self->cached_regs = Py_NewRef(result);
    return result;
}

static PyObject *go_match_repr(GoMatch *self)
{
    PyObject *value = go_match_group_number(self, 0, NULL);
    if (value == NULL) {
        return NULL;
    }
    PyObject *result = PyUnicode_FromFormat(
        "<re.Match object; span=(%lld, %lld), match=%R>",
        (long long)self->spans[0], (long long)self->spans[1], value);
    Py_DECREF(value);
    return result;
}

static PyObject *go_pattern_findall(GoPattern *self,
                                    PyObject *const *args,
                                    Py_ssize_t nargs, PyObject *kwnames)
{
    PyObject *scanner_object = go_pattern_scanner(self, args, nargs,
                                                  kwnames);
    if (scanner_object == NULL) {
        return NULL;
    }
    GoScanner *scanner = (GoScanner *)scanner_object;
    PyObject *result = PyList_New(0);
    if (result == NULL) {
        Py_DECREF(scanner_object);
        return NULL;
    }
    for (;;) {
        PyObject *item = go_scanner_advance(scanner, GO_OPERATION_SEARCH);
        if (item == NULL) {
            Py_DECREF(result);
            Py_DECREF(scanner_object);
            return NULL;
        }
        if (item == Py_None) {
            Py_DECREF(item);
            break;
        }
        GoMatch *match = (GoMatch *)item;
        PyObject *value;
        if (self->group_count == 0) {
            value = go_match_group_number(match, 0, NULL);
        } else if (self->group_count == 1) {
            PyObject *empty = self->is_text
                                  ? PyUnicode_FromString("")
                                  : PyBytes_FromStringAndSize("", 0);
            if (empty == NULL) {
                Py_DECREF(item);
                Py_DECREF(result);
                Py_DECREF(scanner_object);
                return NULL;
            }
            value = go_match_group_number(match, 1, empty);
            Py_DECREF(empty);
        } else {
            value = PyTuple_New(self->group_count);
            if (value != NULL) {
                for (Py_ssize_t index = 1; index <= self->group_count;
                     index++) {
                    PyObject *empty = self->is_text
                                          ? PyUnicode_FromString("")
                                          : PyBytes_FromStringAndSize("", 0);
                    PyObject *group = empty == NULL
                                          ? NULL
                                          : go_match_group_number(match,
                                                                  index,
                                                                  empty);
                    Py_XDECREF(empty);
                    if (group == NULL) {
                        Py_CLEAR(value);
                        break;
                    }
                    PyTuple_SET_ITEM(value, index - 1, group);
                }
            }
        }
        Py_DECREF(item);
        if (value == NULL || PyList_Append(result, value) < 0) {
            Py_XDECREF(value);
            Py_DECREF(result);
            Py_DECREF(scanner_object);
            return NULL;
        }
        Py_DECREF(value);
    }
    Py_DECREF(scanner_object);
    return result;
}

static PyObject *go_pattern_split(GoPattern *self,
                                  PyObject *const *args, Py_ssize_t nargs,
                                  PyObject *kwnames)
{
    static const char *const names[] = {"string", "maxsplit"};
    PyObject *values[2];
    if (go_parse_named("split", args, nargs, kwnames, names, 2, 1,
                       values) < 0) {
        return NULL;
    }
    Py_ssize_t limit = 0;
    if (values[1] != NULL && go_read_index(values[1], &limit) < 0) {
        return NULL;
    }
    PyObject *scanner_object = go_build_scanner(self, values[0], 0,
                                                PY_SSIZE_T_MAX);
    if (scanner_object == NULL) {
        return NULL;
    }
    GoScanner *scanner = (GoScanner *)scanner_object;
    PyObject *result = PyList_New(0);
    if (result == NULL) {
        Py_DECREF(scanner_object);
        return NULL;
    }
    Py_ssize_t previous = 0;
    Py_ssize_t completed = 0;
    while (limit == 0 || completed < limit) {
        PyObject *item = go_scanner_advance(scanner, GO_OPERATION_SEARCH);
        if (item == NULL) {
            goto split_failed;
        }
        if (item == Py_None) {
            Py_DECREF(item);
            break;
        }
        GoMatch *match = (GoMatch *)item;
        PyObject *prefix = go_slice_subject(
            values[0], self->is_text,
            scanner->holds_view ? &scanner->view : NULL,
            previous, (Py_ssize_t)match->spans[0]);
        if (prefix == NULL || PyList_Append(result, prefix) < 0) {
            Py_XDECREF(prefix);
            Py_DECREF(item);
            goto split_failed;
        }
        Py_DECREF(prefix);
        for (Py_ssize_t group = 1; group <= self->group_count; group++) {
            PyObject *capture = go_match_group_number(match, group, NULL);
            if (capture == NULL || PyList_Append(result, capture) < 0) {
                Py_XDECREF(capture);
                Py_DECREF(item);
                goto split_failed;
            }
            Py_DECREF(capture);
        }
        previous = (Py_ssize_t)match->spans[1];
        completed++;
        Py_DECREF(item);
    }
    PyObject *tail = go_slice_subject(
        values[0], self->is_text,
        scanner->holds_view ? &scanner->view : NULL,
        previous, scanner->length);
    if (tail == NULL || PyList_Append(result, tail) < 0) {
        Py_XDECREF(tail);
        goto split_failed;
    }
    Py_DECREF(tail);
    Py_DECREF(scanner_object);
    return result;

split_failed:
    Py_DECREF(result);
    Py_DECREF(scanner_object);
    return NULL;
}

static PyObject *go_literal_replacement(GoPattern *self, PyObject *repl)
{
    if (self->is_text) {
        if (!PyUnicode_Check(repl)) {
            PyErr_Format(PyExc_TypeError,
                         "decoding to str: need a bytes-like object, %.200s found",
                         Py_TYPE(repl)->tp_name);
            return NULL;
        }
        Py_ssize_t found = PyUnicode_FindChar(
            repl, '\\', 0, PyUnicode_GET_LENGTH(repl), 1);
        if (found == -2) {
            return NULL;
        }
        if (found >= 0) {
            PyErr_SetString(PyExc_NotImplementedError,
                            "replacement-template expansion is not implemented "
                            "by the source-only Go experiment");
            return NULL;
        }
        return Py_NewRef(repl);
    }
    Py_buffer view;
    if (PyObject_GetBuffer(repl, &view, PyBUF_SIMPLE) < 0) {
        return NULL;
    }
    if (memchr(view.buf, '\\', (size_t)view.len) != NULL) {
        PyBuffer_Release(&view);
        PyErr_SetString(PyExc_NotImplementedError,
                        "replacement-template expansion is not implemented "
                        "by the source-only Go experiment");
        return NULL;
    }
    PyObject *result = PyBytes_FromStringAndSize((const char *)view.buf,
                                                  view.len);
    PyBuffer_Release(&view);
    return result;
}

static PyObject *go_pattern_substitute(GoPattern *self,
                                       PyObject *const *args,
                                       Py_ssize_t nargs, PyObject *kwnames,
                                       int include_count)
{
    static const char *const names[] = {"repl", "string", "count"};
    PyObject *values[3];
    if (go_parse_named(include_count ? "subn" : "sub", args, nargs,
                       kwnames, names, 3, 2, values) < 0) {
        return NULL;
    }
    Py_ssize_t limit = 0;
    if (values[2] != NULL && go_read_index(values[2], &limit) < 0) {
        return NULL;
    }
    int callable = PyCallable_Check(values[0]);
    PyObject *literal = NULL;
    if (!callable) {
        literal = go_literal_replacement(self, values[0]);
        if (literal == NULL) {
            return NULL;
        }
    }
    PyObject *scanner_object = go_build_scanner(self, values[1], 0,
                                                PY_SSIZE_T_MAX);
    if (scanner_object == NULL) {
        Py_XDECREF(literal);
        return NULL;
    }
    GoScanner *scanner = (GoScanner *)scanner_object;
    PyObject *parts = PyList_New(0);
    if (parts == NULL) {
        Py_XDECREF(literal);
        Py_DECREF(scanner_object);
        return NULL;
    }
    Py_ssize_t previous = 0;
    Py_ssize_t completed = 0;
    while (limit == 0 || completed < limit) {
        PyObject *item = go_scanner_advance(scanner, GO_OPERATION_SEARCH);
        if (item == NULL) {
            goto substitution_failed;
        }
        if (item == Py_None) {
            Py_DECREF(item);
            break;
        }
        GoMatch *match = (GoMatch *)item;
        PyObject *prefix = go_slice_subject(
            values[1], self->is_text,
            scanner->holds_view ? &scanner->view : NULL,
            previous, (Py_ssize_t)match->spans[0]);
        if (prefix == NULL || PyList_Append(parts, prefix) < 0) {
            Py_XDECREF(prefix);
            Py_DECREF(item);
            goto substitution_failed;
        }
        Py_DECREF(prefix);
        PyObject *replacement = callable
                                    ? PyObject_CallOneArg(values[0], item)
                                    : Py_NewRef(literal);
        if (replacement == NULL) {
            Py_DECREF(item);
            goto substitution_failed;
        }
        if (replacement != Py_None &&
            PyList_Append(parts, replacement) < 0) {
            Py_DECREF(replacement);
            Py_DECREF(item);
            goto substitution_failed;
        }
        Py_DECREF(replacement);
        previous = (Py_ssize_t)match->spans[1];
        completed++;
        Py_DECREF(item);
    }
    PyObject *tail = go_slice_subject(
        values[1], self->is_text,
        scanner->holds_view ? &scanner->view : NULL,
        previous, scanner->length);
    if (tail == NULL || PyList_Append(parts, tail) < 0) {
        Py_XDECREF(tail);
        goto substitution_failed;
    }
    Py_DECREF(tail);
    PyObject *separator = self->is_text
                              ? PyUnicode_FromString("")
                              : PyBytes_FromStringAndSize("", 0);
    if (separator == NULL) {
        goto substitution_failed;
    }
    PyObject *joined = PyObject_CallMethod(separator, "join", "O", parts);
    Py_DECREF(separator);
    if (joined == NULL) {
        goto substitution_failed;
    }
    Py_DECREF(parts);
    Py_XDECREF(literal);
    Py_DECREF(scanner_object);
    if (!include_count) {
        return joined;
    }
    PyObject *count = PyLong_FromSsize_t(completed);
    if (count == NULL) {
        Py_DECREF(joined);
        return NULL;
    }
    PyObject *result = PyTuple_Pack(2, joined, count);
    Py_DECREF(joined);
    Py_DECREF(count);
    return result;

substitution_failed:
    Py_DECREF(parts);
    Py_XDECREF(literal);
    Py_DECREF(scanner_object);
    return NULL;
}

static PyObject *go_pattern_sub(GoPattern *self, PyObject *const *args,
                                Py_ssize_t nargs, PyObject *kwnames)
{
    return go_pattern_substitute(self, args, nargs, kwnames, 0);
}

static PyObject *go_pattern_subn(GoPattern *self, PyObject *const *args,
                                 Py_ssize_t nargs, PyObject *kwnames)
{
    return go_pattern_substitute(self, args, nargs, kwnames, 1);
}

static PyObject *go_pattern_original(GoPattern *self, void *closure)
{
    (void)closure;
    return Py_NewRef(self->original);
}

static PyObject *go_pattern_flags(GoPattern *self, void *closure)
{
    (void)closure;
    return PyLong_FromUnsignedLong(self->flags);
}

static PyObject *go_pattern_groups(GoPattern *self, void *closure)
{
    (void)closure;
    return PyLong_FromSsize_t(self->group_count);
}

static PyObject *go_pattern_groupindex(GoPattern *self, void *closure)
{
    (void)closure;
    if (PyDict_GET_SIZE(self->group_names) == 0) {
        return PyDict_New();
    }
    return PyDictProxy_New(self->group_names);
}

static PyObject *go_pattern_repr(GoPattern *self)
{
    if ((self->flags & ~REBAR_GO_UNICODE) == 0) {
        return PyUnicode_FromFormat("re.compile(%R)", self->original);
    }
    return PyUnicode_FromFormat("re.compile(%R, %u)",
                                self->original,
                                self->flags & ~REBAR_GO_UNICODE);
}

static PyObject *go_pattern_reduce(GoPattern *self,
                                   PyObject *Py_UNUSED(ignored))
{
    PyObject *module = PyType_GetModule(Py_TYPE(self));
    if (module == NULL) {
        return NULL;
    }
    PyObject *compile = PyObject_GetAttrString(module, "compile");
    if (compile == NULL) {
        return NULL;
    }
    PyObject *flags = PyLong_FromUnsignedLong(self->flags);
    if (flags == NULL) {
        Py_DECREF(compile);
        return NULL;
    }
    PyObject *arguments = PyTuple_Pack(2, self->original, flags);
    Py_DECREF(flags);
    if (arguments == NULL) {
        Py_DECREF(compile);
        return NULL;
    }
    PyObject *result = PyTuple_Pack(2, compile, arguments);
    Py_DECREF(compile);
    Py_DECREF(arguments);
    return result;
}

PyDoc_STRVAR(go_pattern_search_doc,
             "search($self, /, string, pos=0, endpos=sys.maxsize)\n--\n\n"
             "Scan through string looking for a match, and return a "
             "corresponding match object instance.\n\n"
             "Return None if no position in the string matches.");

PyDoc_STRVAR(go_pattern_match_doc,
             "match($self, /, string, pos=0, endpos=sys.maxsize)\n--\n\n"
             "Matches zero or more characters at the beginning of the string.");

PyDoc_STRVAR(go_pattern_fullmatch_doc,
             "fullmatch($self, /, string, pos=0, endpos=sys.maxsize)\n--\n\n"
             "Matches against all of the string.");

PyDoc_STRVAR(go_pattern_findall_doc,
             "findall($self, /, string, pos=0, endpos=sys.maxsize)\n--\n\n"
             "Return a list of all non-overlapping matches of pattern in string.");

PyDoc_STRVAR(go_pattern_finditer_doc,
             "finditer($self, /, string, pos=0, endpos=sys.maxsize)\n--\n\n"
             "Return an iterator over all non-overlapping matches for the "
             "RE pattern in string.\n\n"
             "For each match, the iterator returns a match object.");

PyDoc_STRVAR(go_pattern_scanner_doc,
             "scanner($self, /, string, pos=0, endpos=sys.maxsize)\n--\n\n");

PyDoc_STRVAR(go_pattern_split_doc,
             "split($self, /, string, maxsplit=0)\n--\n\n"
             "Split string by the occurrences of pattern.");

PyDoc_STRVAR(go_pattern_sub_doc,
             "sub($self, /, repl, string, count=0)\n--\n\n"
             "Return the string obtained by replacing the leftmost "
             "non-overlapping occurrences of pattern in string by the "
             "replacement repl.");

PyDoc_STRVAR(go_pattern_subn_doc,
             "subn($self, /, repl, string, count=0)\n--\n\n"
             "Return the tuple (new_string, number_of_subs_made) found by "
             "replacing the leftmost non-overlapping occurrences of pattern "
             "with the replacement repl.");

static PyMethodDef go_pattern_methods[] = {
    {"search", PyCFunction_CAST(go_pattern_search),
     METH_FASTCALL | METH_KEYWORDS, go_pattern_search_doc},
    {"match", PyCFunction_CAST(go_pattern_match),
     METH_FASTCALL | METH_KEYWORDS, go_pattern_match_doc},
    {"fullmatch", PyCFunction_CAST(go_pattern_fullmatch),
     METH_FASTCALL | METH_KEYWORDS, go_pattern_fullmatch_doc},
    {"findall", PyCFunction_CAST(go_pattern_findall),
     METH_FASTCALL | METH_KEYWORDS, go_pattern_findall_doc},
    {"finditer", PyCFunction_CAST(go_pattern_finditer),
     METH_FASTCALL | METH_KEYWORDS, go_pattern_finditer_doc},
    {"scanner", PyCFunction_CAST(go_pattern_scanner),
     METH_FASTCALL | METH_KEYWORDS, go_pattern_scanner_doc},
    {"split", PyCFunction_CAST(go_pattern_split),
     METH_FASTCALL | METH_KEYWORDS, go_pattern_split_doc},
    {"sub", PyCFunction_CAST(go_pattern_sub),
     METH_FASTCALL | METH_KEYWORDS, go_pattern_sub_doc},
    {"subn", PyCFunction_CAST(go_pattern_subn),
     METH_FASTCALL | METH_KEYWORDS, go_pattern_subn_doc},
    {"__copy__", go_identity_copy, METH_NOARGS, NULL},
    {"__deepcopy__", go_identity_deepcopy, METH_O, NULL},
    {"__reduce__", (PyCFunction)go_pattern_reduce, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL},
};

static PyGetSetDef go_pattern_getset[] = {
    {"pattern", (getter)go_pattern_original, NULL, NULL, NULL},
    {"flags", (getter)go_pattern_flags, NULL, NULL, NULL},
    {"groups", (getter)go_pattern_groups, NULL, NULL, NULL},
    {"groupindex", (getter)go_pattern_groupindex, NULL, NULL, NULL},
    {NULL, NULL, NULL, NULL, NULL},
};

static PyType_Slot go_pattern_slots[] = {
    {Py_tp_dealloc, go_pattern_dealloc},
    {Py_tp_traverse, go_pattern_traverse},
    {Py_tp_clear, go_pattern_clear},
    {Py_tp_methods, go_pattern_methods},
    {Py_tp_getset, go_pattern_getset},
    {Py_tp_repr, go_pattern_repr},
    {0, NULL},
};

static PyType_Spec go_pattern_spec = {
    .name = "re.Pattern",
    .basicsize = sizeof(GoPattern),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = go_pattern_slots,
};

PyDoc_STRVAR(go_match_expand_doc,
             "expand($self, /, template)\n--\n\n"
             "Return the string obtained by doing backslash substitution on "
             "the string template, as done by the sub() method.");

static PyMethodDef go_match_methods[] = {
    {"group", (PyCFunction)go_match_group, METH_VARARGS,
     go_match_group_doc},
    {"groups", PyCFunction_CAST(go_match_groups),
     METH_FASTCALL | METH_KEYWORDS, go_match_groups_doc},
    {"groupdict", PyCFunction_CAST(go_match_groupdict),
     METH_FASTCALL | METH_KEYWORDS, go_match_groupdict_doc},
    {"start", PyCFunction_CAST(go_match_start), METH_FASTCALL,
     go_match_start_doc},
    {"end", PyCFunction_CAST(go_match_end), METH_FASTCALL,
     go_match_end_doc},
    {"span", PyCFunction_CAST(go_match_span), METH_FASTCALL,
     go_match_span_doc},
    {"expand", (PyCFunction)go_match_expand, METH_O,
     go_match_expand_doc},
    {"__copy__", go_identity_copy, METH_NOARGS, NULL},
    {"__deepcopy__", go_identity_deepcopy, METH_O, NULL},
    {"__reduce__", (PyCFunction)go_match_reduce, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL},
};

static PyGetSetDef go_match_getset[] = {
    {"re", (getter)go_match_pattern, NULL, NULL, NULL},
    {"string", (getter)go_match_subject, NULL, NULL, NULL},
    {"pos", (getter)go_match_pos, NULL, NULL, NULL},
    {"endpos", (getter)go_match_endpos, NULL, NULL, NULL},
    {"lastindex", (getter)go_match_lastindex, NULL, NULL, NULL},
    {"lastgroup", (getter)go_match_lastgroup, NULL, NULL, NULL},
    {"regs", (getter)go_match_regs, NULL, NULL, NULL},
    {NULL, NULL, NULL, NULL, NULL},
};

static PyType_Slot go_match_slots[] = {
    {Py_tp_dealloc, go_match_dealloc},
    {Py_tp_traverse, go_match_traverse},
    {Py_tp_clear, go_match_clear},
    {Py_tp_methods, go_match_methods},
    {Py_tp_getset, go_match_getset},
    {Py_tp_repr, go_match_repr},
    {Py_mp_subscript, go_match_subscript},
    {0, NULL},
};

static PyType_Spec go_match_spec = {
    .name = "re.Match",
    .basicsize = sizeof(GoMatch),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = go_match_slots,
};

static PyMethodDef go_scanner_methods[] = {
    {"search", (PyCFunction)go_scanner_search, METH_NOARGS, NULL},
    {"match", (PyCFunction)go_scanner_match, METH_NOARGS, NULL},
    {"__reduce__", (PyCFunction)go_scanner_reduce, METH_NOARGS, NULL},
    {"__reduce_ex__", (PyCFunction)go_scanner_reduce_ex, METH_O, NULL},
    {NULL, NULL, 0, NULL},
};

static PyGetSetDef go_scanner_getset[] = {
    {"pattern", (getter)go_scanner_pattern, NULL, NULL, NULL},
    {NULL, NULL, NULL, NULL, NULL},
};

static PyType_Slot go_scanner_slots[] = {
    {Py_tp_dealloc, go_scanner_dealloc},
    {Py_tp_traverse, go_scanner_traverse},
    {Py_tp_clear, go_scanner_clear},
    {Py_tp_methods, go_scanner_methods},
    {Py_tp_getset, go_scanner_getset},
    {0, NULL},
};

static PyType_Spec go_scanner_spec = {
    .name = "_sre.SRE_Scanner",
    .basicsize = sizeof(GoScanner),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .slots = go_scanner_slots,
};

static int go_fill_group_names(GoModuleState *state, GoPattern *pattern)
{
    for (Py_ssize_t index = 1; index <= pattern->group_count; index++) {
        rebar_go_status_v1 status = {0};
        uint64_t required = 0;
        if (rebar_go_group_name(pattern->handle, (uint64_t)index, NULL, 0,
                                &required, &status) != 0) {
            return go_raise_status(state, pattern->original, &status);
        }
        if (required == 0) {
            continue;
        }
        if (required > (uint64_t)PY_SSIZE_T_MAX) {
            PyErr_NoMemory();
            return -1;
        }
        char *buffer = PyMem_Malloc((size_t)required);
        if (buffer == NULL) {
            PyErr_NoMemory();
            return -1;
        }
        if (rebar_go_group_name(pattern->handle, (uint64_t)index, buffer,
                                required, &required, &status) != 0) {
            PyMem_Free(buffer);
            return go_raise_status(state, pattern->original, &status);
        }
        PyObject *name = PyUnicode_DecodeUTF8(
            buffer, (Py_ssize_t)required - 1, "strict");
        PyMem_Free(buffer);
        PyObject *number = PyLong_FromSsize_t(index);
        if (name == NULL || number == NULL ||
            PyDict_SetItem(pattern->group_names, name, number) < 0) {
            Py_XDECREF(name);
            Py_XDECREF(number);
            return -1;
        }
        Py_DECREF(name);
        Py_DECREF(number);
    }
    return 0;
}

static PyObject *go_compile_pattern(PyObject *module, PyObject *original,
                                    PyObject *flag_object)
{
    GoModuleState *state = (GoModuleState *)PyModule_GetState(module);
    if (state == NULL) {
        return NULL;
    }
    uint32_t flags;
    if (go_read_flags(flag_object, &flags) < 0) {
        return NULL;
    }
    if (PyObject_TypeCheck(original, state->pattern_type)) {
        if (flags != 0) {
            PyErr_SetString(PyExc_ValueError,
                            "cannot process flags argument with a compiled pattern");
            return NULL;
        }
        return Py_NewRef(original);
    }
    int is_text = PyUnicode_Check(original);
    if (!is_text && !PyBytes_Check(original)) {
        PyErr_SetString(PyExc_TypeError,
                        "first argument must be string or compiled pattern");
        return NULL;
    }

    GoInputLease lease;
    if (go_prepare_input(original, is_text, &lease) < 0) {
        return NULL;
    }
    uintptr_t handle = 0;
    rebar_go_status_v1 status = {0};
    if (rebar_go_compile(lease.kind, lease.data, (uint64_t)lease.length,
                         flags, &handle, &status) != 0) {
        go_release_lease(&lease);
        (void)go_raise_status(state, original, &status);
        return NULL;
    }
    go_release_lease(&lease);

    uint32_t effective_flags = 0;
    uint64_t group_count = 0;
    if (rebar_go_metadata(handle, &effective_flags, &group_count,
                          &status) != 0 ||
        group_count > (uint64_t)PY_SSIZE_T_MAX) {
        if (group_count > (uint64_t)PY_SSIZE_T_MAX) {
            PyErr_SetString(PyExc_OverflowError,
                            "capture count exceeds the Python addressable range");
        } else {
            (void)go_raise_status(state, original, &status);
        }
        rebar_go_status_v1 ignored = {0};
        (void)rebar_go_release(handle, &ignored);
        return NULL;
    }

    GoPattern *result = PyObject_GC_New(GoPattern, state->pattern_type);
    if (result == NULL) {
        rebar_go_status_v1 ignored = {0};
        (void)rebar_go_release(handle, &ignored);
        return NULL;
    }
    result->original = Py_NewRef(original);
    result->group_names = PyDict_New();
    result->handle = handle;
    result->flags = effective_flags;
    result->group_count = (Py_ssize_t)group_count;
    result->is_text = is_text;
    if (result->group_names == NULL ||
        go_fill_group_names(state, result) < 0) {
        Py_DECREF(result);
        return NULL;
    }
    PyObject_GC_Track(result);
    return (PyObject *)result;
}

static PyObject *go_module_compile(PyObject *module,
                                   PyObject *const *args, Py_ssize_t nargs,
                                   PyObject *kwnames)
{
    static const char *const names[] = {"pattern", "flags"};
    PyObject *values[2];
    if (go_parse_named("compile", args, nargs, kwnames, names, 2, 1,
                       values) < 0) {
        return NULL;
    }
    return go_compile_pattern(module, values[0], values[1]);
}

static PyObject *go_module_match_operation(PyObject *module,
                                            PyObject *const *args,
                                            Py_ssize_t nargs,
                                            PyObject *kwnames,
                                            const char *operation)
{
    static const char *const names[] = {"pattern", "string", "flags"};
    PyObject *values[3];
    if (go_parse_named(operation, args, nargs, kwnames, names, 3, 2,
                       values) < 0) {
        return NULL;
    }
    PyObject *pattern = go_compile_pattern(module, values[0], values[2]);
    if (pattern == NULL) {
        return NULL;
    }
    PyObject *name = PyUnicode_FromString(operation);
    if (name == NULL) {
        Py_DECREF(pattern);
        return NULL;
    }
    PyObject *result = PyObject_CallMethodOneArg(pattern, name, values[1]);
    Py_DECREF(name);
    Py_DECREF(pattern);
    return result;
}

static PyObject *go_module_search(PyObject *module,
                                  PyObject *const *args, Py_ssize_t nargs,
                                  PyObject *kwnames)
{
    return go_module_match_operation(module, args, nargs, kwnames,
                                     "search");
}

static PyObject *go_module_match(PyObject *module,
                                 PyObject *const *args, Py_ssize_t nargs,
                                 PyObject *kwnames)
{
    return go_module_match_operation(module, args, nargs, kwnames,
                                     "match");
}

static PyObject *go_module_fullmatch(PyObject *module,
                                     PyObject *const *args,
                                     Py_ssize_t nargs, PyObject *kwnames)
{
    return go_module_match_operation(module, args, nargs, kwnames,
                                     "fullmatch");
}

static PyObject *go_module_findall(PyObject *module,
                                   PyObject *const *args, Py_ssize_t nargs,
                                   PyObject *kwnames)
{
    return go_module_match_operation(module, args, nargs, kwnames,
                                     "findall");
}

static PyObject *go_module_finditer(PyObject *module,
                                    PyObject *const *args,
                                    Py_ssize_t nargs, PyObject *kwnames)
{
    return go_module_match_operation(module, args, nargs, kwnames,
                                     "finditer");
}

static PyObject *go_module_split(PyObject *module,
                                 PyObject *const *args, Py_ssize_t nargs,
                                 PyObject *kwnames)
{
    static const char *const names[] = {
        "pattern", "string", "maxsplit", "flags"
    };
    PyObject *values[4];
    if (go_parse_named("split", args, nargs, kwnames, names, 4, 2,
                       values) < 0) {
        return NULL;
    }
    PyObject *pattern = go_compile_pattern(module, values[0], values[3]);
    if (pattern == NULL) {
        return NULL;
    }
    PyObject *result;
    if (values[2] == NULL) {
        result = PyObject_CallMethod(pattern, "split", "O", values[1]);
    } else {
        result = PyObject_CallMethod(pattern, "split", "OO", values[1],
                                     values[2]);
    }
    Py_DECREF(pattern);
    return result;
}

static PyObject *go_module_substitute(PyObject *module,
                                      PyObject *const *args,
                                      Py_ssize_t nargs, PyObject *kwnames,
                                      const char *operation)
{
    static const char *const names[] = {
        "pattern", "repl", "string", "count", "flags"
    };
    PyObject *values[5];
    if (go_parse_named(operation, args, nargs, kwnames, names, 5, 3,
                       values) < 0) {
        return NULL;
    }
    PyObject *pattern = go_compile_pattern(module, values[0], values[4]);
    if (pattern == NULL) {
        return NULL;
    }
    PyObject *result;
    if (values[3] == NULL) {
        result = PyObject_CallMethod(pattern, operation, "OO", values[1],
                                     values[2]);
    } else {
        result = PyObject_CallMethod(pattern, operation, "OOO", values[1],
                                     values[2], values[3]);
    }
    Py_DECREF(pattern);
    return result;
}

static PyObject *go_module_sub(PyObject *module, PyObject *const *args,
                               Py_ssize_t nargs, PyObject *kwnames)
{
    return go_module_substitute(module, args, nargs, kwnames, "sub");
}

static PyObject *go_module_subn(PyObject *module, PyObject *const *args,
                                Py_ssize_t nargs, PyObject *kwnames)
{
    return go_module_substitute(module, args, nargs, kwnames, "subn");
}

static int go_escaped_character(Py_UCS4 value)
{
    return value == '(' || value == ')' || value == '[' || value == ']' ||
           value == '{' || value == '}' || value == '?' || value == '*' ||
           value == '+' || value == '-' || value == '|' || value == '^' ||
           value == '$' || value == '\\' || value == '.' || value == '&' ||
           value == '~' || value == '#' || value == ' ' || value == '\t' ||
           value == '\n' || value == '\r' || value == '\v' || value == '\f';
}

static PyObject *go_module_escape(PyObject *module, PyObject *value)
{
    (void)module;
    int text = PyUnicode_Check(value);
    GoInputLease lease;
    if (go_prepare_input(value, text, &lease) < 0) {
        return NULL;
    }
    PyObject *pieces = PyList_New(0);
    if (pieces == NULL) {
        go_release_lease(&lease);
        return NULL;
    }
    for (Py_ssize_t index = 0; index < lease.length; index++) {
        Py_UCS4 unit;
        if (text) {
            unit = PyUnicode_READ((int)lease.kind, lease.data, index);
        } else {
            unit = (unsigned char)((const char *)lease.data)[index];
        }
        if (go_escaped_character(unit)) {
            PyObject *slash = text ? PyUnicode_FromString("\\")
                                   : PyBytes_FromStringAndSize("\\", 1);
            if (slash == NULL || PyList_Append(pieces, slash) < 0) {
                Py_XDECREF(slash);
                Py_DECREF(pieces);
                go_release_lease(&lease);
                return NULL;
            }
            Py_DECREF(slash);
        }
        PyObject *piece = text
                              ? PyUnicode_FromOrdinal((int)unit)
                              : PyBytes_FromStringAndSize(
                                    (const char *)lease.data + index, 1);
        if (piece == NULL || PyList_Append(pieces, piece) < 0) {
            Py_XDECREF(piece);
            Py_DECREF(pieces);
            go_release_lease(&lease);
            return NULL;
        }
        Py_DECREF(piece);
    }
    PyObject *separator = text ? PyUnicode_FromString("")
                               : PyBytes_FromStringAndSize("", 0);
    if (separator == NULL) {
        Py_DECREF(pieces);
        go_release_lease(&lease);
        return NULL;
    }
    PyObject *result = PyObject_CallMethod(separator, "join", "O", pieces);
    Py_DECREF(separator);
    Py_DECREF(pieces);
    go_release_lease(&lease);
    return result;
}

static PyObject *go_module_purge(PyObject *module,
                                 PyObject *Py_UNUSED(ignored))
{
    (void)module;
    Py_RETURN_NONE;
}

static PyMethodDef go_module_methods[] = {
    {"compile", PyCFunction_CAST(go_module_compile),
     METH_FASTCALL | METH_KEYWORDS, NULL},
    {"search", PyCFunction_CAST(go_module_search),
     METH_FASTCALL | METH_KEYWORDS, NULL},
    {"match", PyCFunction_CAST(go_module_match),
     METH_FASTCALL | METH_KEYWORDS, NULL},
    {"fullmatch", PyCFunction_CAST(go_module_fullmatch),
     METH_FASTCALL | METH_KEYWORDS, NULL},
    {"findall", PyCFunction_CAST(go_module_findall),
     METH_FASTCALL | METH_KEYWORDS, NULL},
    {"finditer", PyCFunction_CAST(go_module_finditer),
     METH_FASTCALL | METH_KEYWORDS, NULL},
    {"split", PyCFunction_CAST(go_module_split),
     METH_FASTCALL | METH_KEYWORDS, NULL},
    {"sub", PyCFunction_CAST(go_module_sub),
     METH_FASTCALL | METH_KEYWORDS, NULL},
    {"subn", PyCFunction_CAST(go_module_subn),
     METH_FASTCALL | METH_KEYWORDS, NULL},
    {"escape", (PyCFunction)go_module_escape, METH_O, NULL},
    {"purge", (PyCFunction)go_module_purge, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL},
};

static int go_add_constant(PyObject *module, const char *long_name,
                           const char *short_name, int value)
{
    if (PyModule_AddIntConstant(module, long_name, value) < 0) {
        return -1;
    }
    if (short_name != NULL &&
        PyModule_AddIntConstant(module, short_name, value) < 0) {
        return -1;
    }
    return 0;
}

static int go_module_exec(PyObject *module)
{
    if (rebar_go_abi_version() != REBAR_GO_ABI_V1) {
        PyErr_SetString(PyExc_ImportError,
                        "owned Go engine has an unexpected experiment ABI");
        return -1;
    }
    GoModuleState *state = (GoModuleState *)PyModule_GetState(module);
    if (state == NULL) {
        return -1;
    }
    state->pattern_error = PyErr_NewException(
        "rebar_go_v1.PatternError", PyExc_Exception, NULL);
    if (state->pattern_error == NULL ||
        PyModule_AddObjectRef(module, "PatternError",
                              state->pattern_error) < 0 ||
        PyModule_AddObjectRef(module, "error", state->pattern_error) < 0) {
        return -1;
    }

    PyObject *match = PyType_FromModuleAndSpec(module, &go_match_spec,
                                                NULL);
    if (match == NULL) {
        return -1;
    }
    state->match_type = (PyTypeObject *)match;
    if (PyModule_AddObjectRef(module, "Match", match) < 0) {
        return -1;
    }

    PyObject *scanner = PyType_FromModuleAndSpec(module, &go_scanner_spec,
                                                  NULL);
    if (scanner == NULL) {
        return -1;
    }
    state->scanner_type = (PyTypeObject *)scanner;

    PyObject *pattern = PyType_FromModuleAndSpec(module, &go_pattern_spec,
                                                  NULL);
    if (pattern == NULL) {
        return -1;
    }
    state->pattern_type = (PyTypeObject *)pattern;
    if (PyModule_AddObjectRef(module, "Pattern", pattern) < 0) {
        return -1;
    }

    if (go_add_constant(module, "IGNORECASE", "I",
                        REBAR_GO_IGNORECASE) < 0 ||
        go_add_constant(module, "LOCALE", "L", REBAR_GO_LOCALE) < 0 ||
        go_add_constant(module, "MULTILINE", "M",
                        REBAR_GO_MULTILINE) < 0 ||
        go_add_constant(module, "DOTALL", "S", REBAR_GO_DOTALL) < 0 ||
        go_add_constant(module, "UNICODE", "U", REBAR_GO_UNICODE) < 0 ||
        go_add_constant(module, "VERBOSE", "X", REBAR_GO_VERBOSE) < 0 ||
        go_add_constant(module, "ASCII", "A", REBAR_GO_ASCII) < 0 ||
        go_add_constant(module, "DEBUG", NULL, REBAR_GO_DEBUG) < 0 ||
        go_add_constant(module, "NOFLAG", NULL, 0) < 0) {
        return -1;
    }
    return 0;
}

static int go_module_traverse(PyObject *module, visitproc visit, void *arg)
{
    GoModuleState *state = (GoModuleState *)PyModule_GetState(module);
    if (state == NULL) {
        return 0;
    }
    Py_VISIT(state->pattern_type);
    Py_VISIT(state->match_type);
    Py_VISIT(state->scanner_type);
    Py_VISIT(state->pattern_error);
    return 0;
}

static int go_module_clear(PyObject *module)
{
    GoModuleState *state = (GoModuleState *)PyModule_GetState(module);
    if (state == NULL) {
        return 0;
    }
    Py_CLEAR(state->pattern_type);
    Py_CLEAR(state->match_type);
    Py_CLEAR(state->scanner_type);
    Py_CLEAR(state->pattern_error);
    return 0;
}

static void go_module_free(void *module)
{
    (void)go_module_clear((PyObject *)module);
}

static PyModuleDef_Slot go_module_slots[] = {
    {Py_mod_exec, go_module_exec},
#ifdef Py_mod_multiple_interpreters
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_NOT_SUPPORTED},
#endif
    {0, NULL},
};

static struct PyModuleDef go_module_definition = {
    PyModuleDef_HEAD_INIT,
    .m_name = "rebar_go_v1",
    .m_doc = "Source-first independently owned Go regex-engine experiment.",
    .m_size = sizeof(GoModuleState),
    .m_methods = go_module_methods,
    .m_slots = go_module_slots,
    .m_traverse = go_module_traverse,
    .m_clear = go_module_clear,
    .m_free = go_module_free,
};

PyMODINIT_FUNC PyInit_rebar_go_v1(void)
{
    return PyModuleDef_Init(&go_module_definition);
}
