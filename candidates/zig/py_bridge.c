#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

extern int rebar_zig_match(const void *, const uint8_t *, size_t, size_t, size_t, uint8_t, intptr_t *, intptr_t *);
extern size_t rebar_zig_groups(const void *);
extern int rebar_zig_match_captures(const void *, const uint8_t *, size_t, size_t, size_t, uint8_t, uint8_t, intptr_t *, intptr_t *, intptr_t *);
extern intptr_t rebar_zig_collect_captures(const void *, const uint8_t *, size_t, size_t, size_t, size_t, intptr_t *, intptr_t *, intptr_t *);
extern intptr_t rebar_zig_collect_records(const void *, const uint8_t *, size_t, size_t, size_t, intptr_t *, size_t *, uint8_t *);

#define ZIG_LOCAL_CAPTURE_WORDS 1024
#define ZIG_INITIAL_CAPTURE_COUNT 64

typedef struct {
    intptr_t local[ZIG_LOCAL_CAPTURE_WORDS];
    intptr_t *storage;
    size_t stride;
    size_t words_per_match;
} ZigCaptureBuffer;

static void zig_capture_release(ZigCaptureBuffer *buffer) {
    if (buffer->storage != NULL && buffer->storage != buffer->local) PyMem_Free(buffer->storage);
    buffer->storage = NULL;
}

/*
 * Start with a small stack-backed capture buffer and grow only when the
 * matcher fills it. Records are append-only and matching resumes at the
 * exact cursor/empty-retry state, so dense calls never rescan prior input.
 */
static intptr_t zig_collect_growing(const void *handle, const uint8_t *data, size_t length,
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
        intptr_t count = rebar_zig_collect_records(handle, data, length, end, capacity - used, buffer->storage + used * words_per_match, &cursor, &retry_nonempty);
        if (count < 0) {
            zig_capture_release(buffer);
            return -1;
        }
        used += (size_t)count;
        if (used < capacity || capacity == maximum) return (intptr_t)used;
        capacity = capacity > maximum / 4 ? maximum : capacity * 4;
    }
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
    if (PyUnicode_Check(subject)) {
        if (!PyUnicode_IS_ASCII(subject)) {
            PyErr_SetString(PyExc_ValueError, "Zig bytecode probe currently requires ASCII text");
            return NULL;
        }
        data = PyUnicode_1BYTE_DATA(subject);
        length = (size_t)PyUnicode_GET_LENGTH(subject);
    } else {
        if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) return NULL;
        data = view.buf;
        length = (size_t)view.len;
    }
    intptr_t begin = -1;
    intptr_t finish = -1;
    int result = rebar_zig_match(handle, data, length, pos, endpos, (uint8_t)mode, &begin, &finish);
    if (view.obj != NULL) PyBuffer_Release(&view);
    if (result < 0) {
        PyErr_SetString(PyExc_RuntimeError, "Zig bytecode matcher rejected the bridge call");
        return NULL;
    }
    if (result == 0) Py_RETURN_NONE;
    return Py_BuildValue("(nn)", (Py_ssize_t)begin, (Py_ssize_t)finish);
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
    if (PyUnicode_Check(subject)) {
        if (!PyUnicode_IS_ASCII(subject)) {
            PyErr_SetString(PyExc_ValueError, "Zig capture probe currently requires ASCII text");
            return NULL;
        }
        data = PyUnicode_1BYTE_DATA(subject);
        length = (size_t)PyUnicode_GET_LENGTH(subject);
    } else {
        if (PyObject_GetBuffer(subject, &view, PyBUF_SIMPLE) != 0) return NULL;
        data = view.buf;
        length = (size_t)view.len;
    }
    size_t stride = rebar_zig_groups(handle) + 1;
    intptr_t local_begins[129];
    intptr_t local_ends[129];
    intptr_t *begins = local_begins;
    intptr_t *ends = local_ends;
    if (stride > 129) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        PyErr_SetString(PyExc_OverflowError, "too many Zig capture groups");
        return NULL;
    }
    intptr_t last = -1;
    int result = rebar_zig_match_captures(handle, data, length, pos, endpos, (uint8_t)mode, (uint8_t)nonempty, begins, ends, &last);
    if (view.obj != NULL) PyBuffer_Release(&view);
    if (result < 0) {
        PyErr_SetString(PyExc_RuntimeError, "Zig capture matcher rejected the bridge call");
        return NULL;
    }
    if (result == 0) Py_RETURN_NONE;
    PyObject *spans = PyTuple_New((Py_ssize_t)stride);
    if (spans == NULL) return NULL;
    for (size_t index = 0; index < stride; index++) {
        PyObject *item = begins[index] < 0 ? Py_NewRef(Py_None) : Py_BuildValue("(nn)", (Py_ssize_t)begins[index], (Py_ssize_t)ends[index]);
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
    ZigCaptureBuffer buffer;
    intptr_t count = zig_collect_growing(handle, data, length, pos, end, groups, 0, &buffer);
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
            PyObject *item = begin < 0 ? Py_NewRef(Py_None) : Py_BuildValue("(nn)", (Py_ssize_t)begin, (Py_ssize_t)finish);
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
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_OverflowError, "invalid Zig regex findall argument");
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
    ZigCaptureBuffer buffer;
    intptr_t count = zig_collect_growing(handle, data, length, pos, end, groups, 0, &buffer);
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
            else item = PyBytes_FromStringAndSize((const char *)data + begin, (Py_ssize_t)(finish - begin));
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

static PyObject *bridge_split(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 4) {
        PyErr_Format(PyExc_TypeError, "split() takes exactly 4 arguments (%zd given)", nargs);
        return NULL;
    }
    void *handle = PyLong_AsVoidPtr(args[0]);
    size_t groups = PyLong_AsSize_t(args[2]);
    Py_ssize_t maxsplit = PyLong_AsSsize_t(args[3]);
    if (PyErr_Occurred() || groups == SIZE_MAX) {
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_OverflowError, "invalid Zig regex split argument");
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
    intptr_t count = zig_collect_growing(handle, data, length, 0, length, groups, maxsplit > 0 ? (size_t)maxsplit : 0, &buffer);
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

static PyObject *bridge_subn(PyObject *module, PyObject *const *args, Py_ssize_t nargs) {
    (void)module;
    if (nargs != 5) {
        PyErr_Format(PyExc_TypeError, "subn() takes exactly 5 arguments (%zd given)", nargs);
        return NULL;
    }
    void *handle = PyLong_AsVoidPtr(args[0]);
    size_t groups = PyLong_AsSize_t(args[2]);
    Py_ssize_t limit = PyLong_AsSsize_t(args[4]);
    if (PyErr_Occurred() || groups == SIZE_MAX) {
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_OverflowError, "invalid Zig regex replacement argument");
        return NULL;
    }
    if (groups != rebar_zig_groups(handle)) {
        PyErr_SetString(PyExc_ValueError, "Zig regex group count does not match the compiled program");
        return NULL;
    }
    PyObject *subject = args[1];
    PyObject *tokens = args[3];
    if (!PyTuple_Check(tokens)) {
        PyErr_SetString(PyExc_TypeError, "Zig regex replacement tokens must be a tuple");
        return NULL;
    }
    Py_ssize_t token_count = PyTuple_GET_SIZE(tokens);
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
    if (limit < 0) {
        PyObject *unchanged = text_mode ? PyUnicode_Substring(subject, 0, (Py_ssize_t)length) : PyBytes_FromStringAndSize((const char *)data, (Py_ssize_t)length);
        if (view.obj != NULL) PyBuffer_Release(&view);
        if (unchanged == NULL) return NULL;
        return Py_BuildValue("(Nn)", unchanged, (Py_ssize_t)0);
    }
    ZigCaptureBuffer buffer;
    intptr_t count = zig_collect_growing(handle, data, length, 0, length, groups, limit > 0 ? (size_t)limit : 0, &buffer);
    if (count < 0) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        if (count == -2) return PyErr_NoMemory();
        PyErr_SetString(PyExc_RuntimeError, "Zig capture engine rejected the replacement bridge call");
        return NULL;
    }
    size_t stride = buffer.stride;
    size_t words = buffer.words_per_match;
    size_t pieces = (size_t)token_count + 1;
    if ((size_t)count > (SIZE_MAX - 1) / pieces || (size_t)count * pieces + 1 > (size_t)PY_SSIZE_T_MAX) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        zig_capture_release(&buffer);
        return PyErr_NoMemory();
    }
    PyObject *parts = PyList_New((Py_ssize_t)((size_t)count * pieces + 1));
    if (parts == NULL) goto subn_error;
    size_t previous = 0;
    Py_ssize_t output = 0;
    for (intptr_t match = 0; match < count; match++) {
        size_t base = (size_t)match * words;
        size_t begin = (size_t)buffer.storage[base];
        size_t finish = (size_t)buffer.storage[base + stride];
        PyObject *prefix = text_mode ? PyUnicode_Substring(subject, (Py_ssize_t)previous, (Py_ssize_t)begin) : PyBytes_FromStringAndSize((const char *)data + previous, (Py_ssize_t)(begin - previous));
        if (prefix == NULL) goto subn_error;
        PyList_SET_ITEM(parts, output++, prefix);
        for (Py_ssize_t index = 0; index < token_count; index++) {
            PyObject *token = PyTuple_GET_ITEM(tokens, index);
            PyObject *item;
            if (!PyLong_Check(token)) {
                item = Py_NewRef(token);
            } else {
                size_t group = PyLong_AsSize_t(token);
                if (PyErr_Occurred() || group >= stride) {
                    if (!PyErr_Occurred()) PyErr_SetString(PyExc_ValueError, "Zig regex replacement group is out of range");
                    goto subn_error;
                }
                intptr_t first = buffer.storage[base + group];
                intptr_t last = buffer.storage[base + stride + group];
                if (first < 0) item = text_mode ? PyUnicode_New(0, 127) : PyBytes_FromStringAndSize("", 0);
                else if (text_mode) item = PyUnicode_Substring(subject, (Py_ssize_t)first, (Py_ssize_t)last);
                else item = PyBytes_FromStringAndSize((const char *)data + first, (Py_ssize_t)(last - first));
            }
            if (item == NULL) goto subn_error;
            PyList_SET_ITEM(parts, output++, item);
        }
        previous = finish;
    }
    PyObject *tail = text_mode ? PyUnicode_Substring(subject, (Py_ssize_t)previous, (Py_ssize_t)length) : PyBytes_FromStringAndSize((const char *)data + previous, (Py_ssize_t)(length - previous));
    if (tail == NULL) goto subn_error;
    PyList_SET_ITEM(parts, output, tail);
    PyObject *separator = text_mode ? PyUnicode_New(0, 127) : PyBytes_FromStringAndSize("", 0);
    if (separator == NULL) goto subn_error;
    PyObject *joined = text_mode ? PyUnicode_Join(separator, parts) : PyObject_CallMethod(separator, "join", "O", parts);
    Py_DECREF(separator);
    if (joined == NULL) goto subn_error;
    Py_DECREF(parts);
    if (view.obj != NULL) PyBuffer_Release(&view);
    zig_capture_release(&buffer);
    return Py_BuildValue("(Nn)", joined, (Py_ssize_t)count);

subn_error:
    if (view.obj != NULL) PyBuffer_Release(&view);
    zig_capture_release(&buffer);
    Py_XDECREF(parts);
    return NULL;
}

static PyMethodDef bridge_methods[] = {
    {"span", (PyCFunction)(void (*)(void))bridge_span, METH_FASTCALL, "Run one from-scratch Zig bytecode match."},
    {"match", (PyCFunction)(void (*)(void))bridge_match, METH_FASTCALL, "Run one capture-aware Zig bytecode match."},
    {"collect", (PyCFunction)(void (*)(void))bridge_collect, METH_FASTCALL, "Collect non-overlapping Zig regex matches."},
    {"findall", (PyCFunction)(void (*)(void))bridge_findall, METH_FASTCALL, "Return all Zig regex matches as Python values."},
    {"split", (PyCFunction)(void (*)(void))bridge_split, METH_FASTCALL, "Split with one Zig regex boundary crossing."},
    {"subn", (PyCFunction)(void (*)(void))bridge_subn, METH_FASTCALL, "Replace with one Zig regex boundary crossing."},
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

PyMODINIT_FUNC PyInit__zig_bridge(void) { return PyModule_Create(&bridge_module); }
