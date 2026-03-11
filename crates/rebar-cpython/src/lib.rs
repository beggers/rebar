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

#[pyfunction(signature = (*_args, **_kwargs))]
fn scaffold_compile(_args: &Bound<'_, PyAny>, _kwargs: Option<&Bound<'_, PyAny>>) -> PyResult<PyObject> {
    Err(PyNotImplementedError::new_err(
        "rebar native compile scaffold is not implemented yet",
    ))
}

#[pymodule]
fn _rebar(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add("__doc__", "Native scaffold module for the future rebar `re` replacement.")?;
    module.add("__rebar_scaffold__", true)?;
    module.add("TARGET_CPYTHON_SERIES", TARGET_CPYTHON_SERIES)?;
    module.add("SCAFFOLD_STATUS", SCAFFOLD_STATUS)?;
    module.add_function(wrap_pyfunction!(target_cpython_series, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_status, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_compile, module)?)?;
    Ok(())
}
