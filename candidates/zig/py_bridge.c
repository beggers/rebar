#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

extern int rebar_zig_match(const void *, const uint8_t *, size_t, size_t, size_t, uint8_t, intptr_t *, intptr_t *);
extern size_t rebar_zig_groups(const void *);
extern int rebar_zig_match_captures(const void *, const uint8_t *, size_t, size_t, size_t, uint8_t, intptr_t *, intptr_t *, intptr_t *);

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
    if (nargs != 5) {
        PyErr_Format(PyExc_TypeError, "match() takes exactly 5 arguments (%zd given)", nargs);
        return NULL;
    }
    void *handle = PyLong_AsVoidPtr(args[0]);
    size_t pos = PyLong_AsSize_t(args[2]);
    size_t endpos = PyLong_AsSize_t(args[3]);
    unsigned long mode = PyLong_AsUnsignedLong(args[4]);
    if (PyErr_Occurred() || mode > UINT8_MAX) {
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
    int result = rebar_zig_match_captures(handle, data, length, pos, endpos, (uint8_t)mode, begins, ends, &last);
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

static PyMethodDef bridge_methods[] = {
    {"span", (PyCFunction)(void (*)(void))bridge_span, METH_FASTCALL, "Run one from-scratch Zig bytecode match."},
    {"match", (PyCFunction)(void (*)(void))bridge_match, METH_FASTCALL, "Run one capture-aware Zig bytecode match."},
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
