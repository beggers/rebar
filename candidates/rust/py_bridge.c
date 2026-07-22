#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

extern int rebar_match(const void *, const uint32_t *, const uint32_t *, const uint8_t *, size_t, size_t, size_t, uint8_t, uint8_t, intptr_t *, intptr_t *, intptr_t *);
extern int rebar_match_ascii(const void *, const uint8_t *, size_t, size_t, size_t, uint8_t, uint8_t, intptr_t *, intptr_t *, intptr_t *);
extern intptr_t rebar_collect_ascii(const void *, const uint8_t *, size_t, size_t, size_t, size_t, intptr_t *, intptr_t *, intptr_t *);

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
        if (PyUnicode_IS_ASCII(subject)) {
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
        matched = rebar_match_ascii(handle, view.buf, (size_t)view.len, pos, endpos, (uint8_t)mode, (uint8_t)nonempty, begins, ends, &last);
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
            item = Py_BuildValue("(nn)", (Py_ssize_t)begins[index], (Py_ssize_t)ends[index]);
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
    PyObject *result = PyTuple_Pack(2, spans, last_value);
    Py_DECREF(spans);
    Py_DECREF(last_value);
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
            else item = Py_BuildValue("(nn)", (Py_ssize_t)begins[base + group], (Py_ssize_t)ends[base + group]);
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
        if (!PyErr_Occurred()) PyErr_SetString(PyExc_OverflowError, "invalid Rust regex findall argument");
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

static PyMethodDef bridge_methods[] = {
    {"run", (PyCFunction)(void (*)(void))bridge_run, METH_FASTCALL, "Run one Rust regular-expression match."},
    {"collect", (PyCFunction)(void (*)(void))bridge_collect, METH_FASTCALL, "Collect non-overlapping Rust regular-expression matches."},
    {"findall", (PyCFunction)(void (*)(void))bridge_findall, METH_FASTCALL, "Return all Rust regular-expression matches as Python values."},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef bridge_module = {
    PyModuleDef_HEAD_INIT,
    "_rust_bridge",
    "Dependency-free CPython bridge for the from-scratch Rust regex engine.",
    -1,
    bridge_methods,
    NULL,
    NULL,
    NULL,
    NULL,
};

PyMODINIT_FUNC PyInit__rust_bridge(void) { return PyModule_Create(&bridge_module); }
