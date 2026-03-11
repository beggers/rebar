//! CPython-extension scaffold for `rebar`.
//!
//! The module intentionally exposes only enough metadata and placeholder hooks
//! to prove out the PyO3/maturin boundary while the actual `re`-compatible API
//! is still pending.

use pyo3::exceptions::PyNotImplementedError;
use pyo3::prelude::*;
use rebar_core::TARGET_CPYTHON_SERIES;

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

#[pyfunction]
fn scaffold_raise(helper_name: &str) -> PyResult<PyObject> {
    Err(helper_placeholder_error(helper_name))
}

#[pyfunction(signature = (*_args, **_kwargs))]
fn scaffold_compile(_args: &Bound<'_, PyAny>, _kwargs: Option<&Bound<'_, PyAny>>) -> PyResult<PyObject> {
    Err(helper_placeholder_error("compile"))
}

#[pyfunction]
fn scaffold_purge() {}

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
    module.add("__doc__", "Native scaffold module for the future rebar `re` replacement.")?;
    module.add("__rebar_scaffold__", true)?;
    module.add("TARGET_CPYTHON_SERIES", TARGET_CPYTHON_SERIES)?;
    module.add("SCAFFOLD_STATUS", SCAFFOLD_STATUS)?;
    module.add_function(wrap_pyfunction!(target_cpython_series, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_status, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_raise, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_compile, module)?)?;
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
