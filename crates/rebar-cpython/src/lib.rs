//! CPython-extension boundary for the currently supported `rebar` slice.

use pyo3::exceptions::{PyFutureWarning, PyNotImplementedError, PyTypeError};
use pyo3::ffi::c_str;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyString};
use rebar_core::{
    compile as core_compile, escape_bytes as core_escape_bytes, escape_str as core_escape_str,
    literal_match as core_literal_match, CompileStatus, MatchMode, MatchStatus, PatternRef,
    TARGET_CPYTHON_SERIES,
};

const SCAFFOLD_STATUS: &str = "scaffold-only";

#[pyfunction]
fn target_cpython_series() -> &'static str {
    TARGET_CPYTHON_SERIES
}

#[pyfunction]
fn scaffold_status() -> &'static str {
    SCAFFOLD_STATUS
}

fn helper_placeholder_error(helper_name: &str) -> PyErr {
    PyNotImplementedError::new_err(format!(
        "rebar.{helper_name}() is a scaffold placeholder; the `re`-compatible API is not implemented yet"
    ))
}

fn pattern_placeholder_error(method_name: &str) -> PyErr {
    PyNotImplementedError::new_err(format!(
        "rebar.Pattern.{method_name}() is a scaffold placeholder; compiled pattern semantics are not implemented yet"
    ))
}

fn py_pattern_ref<'py>(pattern: &'py Bound<'py, PyAny>) -> PyResult<PatternRef<'py>> {
    if let Ok(value) = pattern.extract::<&str>() {
        return Ok(PatternRef::Str(value));
    }
    if let Ok(value) = pattern.downcast::<PyBytes>() {
        return Ok(PatternRef::Bytes(value.as_bytes()));
    }
    Err(PyTypeError::new_err("expected str or bytes"))
}

fn mode_from_name(mode: &str) -> PyResult<MatchMode> {
    match mode {
        "search" => Ok(MatchMode::Search),
        "match" => Ok(MatchMode::Match),
        "fullmatch" => Ok(MatchMode::Fullmatch),
        _ => Err(PyTypeError::new_err("unsupported literal match mode")),
    }
}

fn raise_re_error<T>(py: Python<'_>, pattern: &Bound<'_, PyAny>, message: &str, pos: usize) -> PyResult<T> {
    let re_module = py.import("re")?;
    let error_type = re_module.getattr("error")?;
    let instance = error_type.call1((message, pattern, pos))?;
    Err(PyErr::from_value(instance))
}

#[pyfunction]
fn scaffold_raise(helper_name: &str) -> PyResult<PyObject> {
    Err(helper_placeholder_error(helper_name))
}

#[pyfunction]
fn scaffold_pattern_raise(method_name: &str) -> PyResult<PyObject> {
    Err(pattern_placeholder_error(method_name))
}

#[pyfunction]
fn boundary_compile(py: Python<'_>, pattern: &Bound<'_, PyAny>, flags: i32) -> PyResult<(&'static str, i32, bool)> {
    let pattern_ref = py_pattern_ref(pattern)?;
    let outcome = match core_compile(pattern_ref, flags) {
        Ok(outcome) => outcome,
        Err(error) => return raise_re_error(py, pattern, error.message, error.pos),
    };

    if outcome.warning.is_some() {
        let category = py.get_type::<PyFutureWarning>();
        PyErr::warn(py, &category, c_str!("Possible nested set at position 1"), 2)?;
    }

    let status = match outcome.status {
        CompileStatus::Compiled => "compiled",
        CompileStatus::Unsupported => "unsupported",
    };
    Ok((status, outcome.normalized_flags, outcome.supports_literal))
}

#[pyfunction]
fn scaffold_purge() {}

#[pyfunction(signature = (pattern, flags, mode, string, pos=0, endpos=None))]
fn boundary_literal_match(
    pattern: &Bound<'_, PyAny>,
    flags: i32,
    mode: &str,
    string: &Bound<'_, PyAny>,
    pos: isize,
    endpos: Option<isize>,
) -> PyResult<(&'static str, usize, usize, Option<(usize, usize)>)> {
    let pattern_ref = py_pattern_ref(pattern)?;
    let string_ref = py_pattern_ref(string)?;
    let mode = mode_from_name(mode)?;
    let outcome = match core_literal_match(pattern_ref, flags, mode, string_ref, pos, endpos) {
        Ok(outcome) => outcome,
        Err(error) => return Err(PyTypeError::new_err(error.message())),
    };

    let status = match outcome.status {
        MatchStatus::Matched => "matched",
        MatchStatus::NoMatch => "no-match",
        MatchStatus::Unsupported => "unsupported",
    };

    Ok((status, outcome.pos, outcome.endpos, outcome.span))
}

#[pyfunction]
fn boundary_escape(py: Python<'_>, pattern: &Bound<'_, PyAny>) -> PyResult<PyObject> {
    if let Ok(value) = pattern.extract::<&str>() {
        return Ok(PyString::new(py, &core_escape_str(value)).unbind().into_any());
    }
    if let Ok(value) = pattern.downcast::<PyBytes>() {
        return Ok(PyBytes::new(py, &core_escape_bytes(value.as_bytes())).unbind().into_any());
    }
    Err(PyTypeError::new_err("expected str or bytes"))
}

#[pyfunction]
fn scaffold_search() -> PyResult<PyObject> {
    Err(helper_placeholder_error("search"))
}

#[pyfunction]
fn scaffold_match() -> PyResult<PyObject> {
    Err(helper_placeholder_error("match"))
}

#[pyfunction]
fn scaffold_fullmatch() -> PyResult<PyObject> {
    Err(helper_placeholder_error("fullmatch"))
}

#[pyfunction]
fn scaffold_split() -> PyResult<PyObject> {
    Err(helper_placeholder_error("split"))
}

#[pyfunction]
fn scaffold_findall() -> PyResult<PyObject> {
    Err(helper_placeholder_error("findall"))
}

#[pyfunction]
fn scaffold_finditer() -> PyResult<PyObject> {
    Err(helper_placeholder_error("finditer"))
}

#[pyfunction]
fn scaffold_sub() -> PyResult<PyObject> {
    Err(helper_placeholder_error("sub"))
}

#[pyfunction]
fn scaffold_subn() -> PyResult<PyObject> {
    Err(helper_placeholder_error("subn"))
}

#[pyfunction]
fn scaffold_escape() -> PyResult<PyObject> {
    Err(helper_placeholder_error("escape"))
}

#[pymodule]
fn _rebar(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add("__doc__", "Native boundary module for the current rebar `re` subset.")?;
    module.add("__rebar_scaffold__", true)?;
    module.add("TARGET_CPYTHON_SERIES", TARGET_CPYTHON_SERIES)?;
    module.add("SCAFFOLD_STATUS", SCAFFOLD_STATUS)?;
    module.add_function(wrap_pyfunction!(target_cpython_series, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_status, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_raise, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_pattern_raise, module)?)?;
    module.add_function(wrap_pyfunction!(boundary_compile, module)?)?;
    module.add_function(wrap_pyfunction!(boundary_literal_match, module)?)?;
    module.add_function(wrap_pyfunction!(boundary_escape, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_purge, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_search, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_match, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_fullmatch, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_split, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_findall, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_finditer, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_sub, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_subn, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_escape, module)?)?;
    Ok(())
}
