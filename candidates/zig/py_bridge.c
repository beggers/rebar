#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

extern int rebar_zig_match(const void *, const uint8_t *, size_t, size_t, size_t, uint8_t, intptr_t *, intptr_t *);
extern size_t rebar_zig_groups(const void *);
extern int rebar_zig_match_captures(const void *, const uint8_t *, size_t, size_t, size_t, uint8_t, uint8_t, intptr_t *, intptr_t *, intptr_t *);
extern intptr_t rebar_zig_collect_captures(const void *, const uint8_t *, size_t, size_t, size_t, size_t, intptr_t *, intptr_t *, intptr_t *);

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
    intptr_t count = rebar_zig_collect_captures(handle, data, length, pos, end, capacity, begins, ends, lasts);
    if (view.obj != NULL) PyBuffer_Release(&view);
    if (count < 0) {
        PyMem_Free(storage);
        PyErr_SetString(PyExc_RuntimeError, "Zig capture engine rejected the collection bridge call");
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
            PyObject *item = begins[base + group] < 0 ? Py_NewRef(Py_None) : Py_BuildValue("(nn)", (Py_ssize_t)begins[base + group], (Py_ssize_t)ends[base + group]);
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
        PyObject *record = PyTuple_Pack(2, spans, last);
        Py_DECREF(spans);
        Py_DECREF(last);
        if (record == NULL) goto collect_error;
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
    intptr_t count = rebar_zig_collect_captures(handle, data, length, pos, end, capacity, begins, ends, lasts);
    if (count < 0) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        PyMem_Free(storage);
        PyErr_SetString(PyExc_RuntimeError, "Zig capture engine rejected the findall bridge call");
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
    PyMem_Free(storage);
    return result;

findall_error:
    if (view.obj != NULL) PyBuffer_Release(&view);
    PyMem_Free(storage);
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
    if (length > (SIZE_MAX - 1) / 2) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        return PyErr_NoMemory();
    }
    size_t capacity = length * 2 + 1;
    if (maxsplit > 0 && (size_t)maxsplit < capacity) capacity = (size_t)maxsplit;
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
    intptr_t count = rebar_zig_collect_captures(handle, data, length, 0, length, capacity, begins, ends, lasts);
    if (count < 0) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        PyMem_Free(storage);
        PyErr_SetString(PyExc_RuntimeError, "Zig capture engine rejected the split bridge call");
        return NULL;
    }
    if ((size_t)count > (SIZE_MAX - 1) / stride || (size_t)count * stride + 1 > (size_t)PY_SSIZE_T_MAX) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        PyMem_Free(storage);
        return PyErr_NoMemory();
    }
    PyObject *result = PyList_New((Py_ssize_t)((size_t)count * stride + 1));
    if (result == NULL) goto split_error;
    size_t previous = 0;
    Py_ssize_t output = 0;
    for (intptr_t match = 0; match < count; match++) {
        size_t base = (size_t)match * stride;
        size_t begin = (size_t)begins[base];
        size_t finish = (size_t)ends[base];
        PyObject *prefix = text_mode ? PyUnicode_Substring(subject, (Py_ssize_t)previous, (Py_ssize_t)begin) : PyBytes_FromStringAndSize((const char *)data + previous, (Py_ssize_t)(begin - previous));
        if (prefix == NULL) goto split_error;
        PyList_SET_ITEM(result, output++, prefix);
        for (size_t group = 1; group < stride; group++) {
            intptr_t first = begins[base + group];
            intptr_t last = ends[base + group];
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
    PyMem_Free(storage);
    return result;

split_error:
    if (view.obj != NULL) PyBuffer_Release(&view);
    PyMem_Free(storage);
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
    if (length > (SIZE_MAX - 1) / 2) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        return PyErr_NoMemory();
    }
    size_t capacity = length * 2 + 1;
    if (limit > 0 && (size_t)limit < capacity) capacity = (size_t)limit;
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
    intptr_t count = rebar_zig_collect_captures(handle, data, length, 0, length, capacity, begins, ends, lasts);
    if (count < 0) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        PyMem_Free(storage);
        PyErr_SetString(PyExc_RuntimeError, "Zig capture engine rejected the replacement bridge call");
        return NULL;
    }
    size_t pieces = (size_t)token_count + 1;
    if ((size_t)count > (SIZE_MAX - 1) / pieces || (size_t)count * pieces + 1 > (size_t)PY_SSIZE_T_MAX) {
        if (view.obj != NULL) PyBuffer_Release(&view);
        PyMem_Free(storage);
        return PyErr_NoMemory();
    }
    PyObject *parts = PyList_New((Py_ssize_t)((size_t)count * pieces + 1));
    if (parts == NULL) goto subn_error;
    size_t previous = 0;
    Py_ssize_t output = 0;
    for (intptr_t match = 0; match < count; match++) {
        size_t base = (size_t)match * stride;
        size_t begin = (size_t)begins[base];
        size_t finish = (size_t)ends[base];
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
                intptr_t first = begins[base + group];
                intptr_t last = ends[base + group];
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
    PyMem_Free(storage);
    return Py_BuildValue("(Nn)", joined, (Py_ssize_t)count);

subn_error:
    if (view.obj != NULL) PyBuffer_Release(&view);
    PyMem_Free(storage);
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
