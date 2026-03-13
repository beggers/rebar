//! CPython-extension boundary for the currently supported `rebar` slice.

use pyo3::exceptions::{PyFutureWarning, PyNotImplementedError, PyTypeError};
use pyo3::ffi::c_str;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyList, PyString};
use rebar_core::{
    compile as core_compile,
    conditional_group_exists_alternation_find_spans_str as core_conditional_group_exists_alternation_find_spans_str,
    conditional_group_exists_empty_else_find_spans_str as core_conditional_group_exists_empty_else_find_spans_str,
    conditional_group_exists_empty_yes_else_find_spans_str as core_conditional_group_exists_empty_yes_else_find_spans_str,
    conditional_group_exists_find_spans_str as core_conditional_group_exists_find_spans_str,
    conditional_group_exists_no_else_find_spans_str as core_conditional_group_exists_no_else_find_spans_str,
    escape_bytes as core_escape_bytes, escape_str as core_escape_str,
    expand_literal_replacement_template_str as core_expand_literal_replacement_template_str,
    grouped_alternation_find_spans_str as core_grouped_alternation_find_spans_str,
    grouped_literal_find_spans_str as core_grouped_literal_find_spans_str,
    literal_find_spans as core_literal_find_spans, literal_match as core_literal_match,
    nested_capture_find_spans_str as core_nested_capture_find_spans_str, CapturedMatchSpan,
    CompileStatus, MatchMode, MatchStatus, PatternRef, TARGET_CPYTHON_SERIES,
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

fn build_str_boundaries(value: &str) -> Vec<usize> {
    let mut boundaries = Vec::with_capacity(value.chars().count() + 1);
    boundaries.push(0);
    for (index, _) in value.char_indices().skip(1) {
        boundaries.push(index);
    }
    boundaries.push(value.len());
    boundaries
}

fn str_slice<'a>(value: &'a str, boundaries: &[usize], start: usize, end: usize) -> &'a str {
    &value[boundaries[start]..boundaries[end]]
}

fn split_limit(maxsplit: isize, total_matches: usize) -> Option<usize> {
    if maxsplit < 0 {
        None
    } else if maxsplit == 0 {
        Some(total_matches)
    } else {
        Some(usize::min(maxsplit as usize, total_matches))
    }
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

fn workflow_status(status: MatchStatus) -> &'static str {
    match status {
        MatchStatus::Unsupported => "unsupported",
        MatchStatus::Matched | MatchStatus::NoMatch => "supported",
    }
}

fn replacement_limit(count: isize, total_matches: usize) -> usize {
    if count == 0 {
        total_matches
    } else {
        usize::min(count as usize, total_matches)
    }
}

fn raise_re_error<T>(
    py: Python<'_>,
    pattern: &Bound<'_, PyAny>,
    message: &str,
    pos: Option<usize>,
) -> PyResult<T> {
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
fn boundary_compile(
    py: Python<'_>,
    pattern: &Bound<'_, PyAny>,
    flags: i32,
) -> PyResult<(&'static str, i32, bool, usize, Vec<(String, usize)>)> {
    let pattern_ref = py_pattern_ref(pattern)?;
    let outcome = match core_compile(pattern_ref, flags) {
        Ok(outcome) => outcome,
        Err(error) => return raise_re_error(py, pattern, error.message, error.pos),
    };

    if outcome.warning.is_some() {
        let category = py.get_type::<PyFutureWarning>();
        PyErr::warn(
            py,
            &category,
            c_str!("Possible nested set at position 1"),
            2,
        )?;
    }

    let status = match outcome.status {
        CompileStatus::Compiled => "compiled",
        CompileStatus::Unsupported => "unsupported",
    };
    Ok((
        status,
        outcome.normalized_flags,
        outcome.supports_literal,
        outcome.group_count,
        outcome
            .named_groups
            .into_iter()
            .map(|group| (group.name, group.index))
            .collect(),
    ))
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
) -> PyResult<(
    &'static str,
    usize,
    usize,
    Option<(usize, usize)>,
    Vec<Option<(usize, usize)>>,
    Option<usize>,
)> {
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

    Ok((
        status,
        outcome.pos,
        outcome.endpos,
        outcome.span,
        outcome.group_spans,
        outcome.lastindex,
    ))
}

#[pyfunction(signature = (pattern, flags, string, maxsplit=0))]
fn boundary_literal_split(
    py: Python<'_>,
    pattern: &Bound<'_, PyAny>,
    flags: i32,
    string: &Bound<'_, PyAny>,
    maxsplit: isize,
) -> PyResult<(&'static str, PyObject)> {
    let pattern_ref = py_pattern_ref(pattern)?;
    let string_ref = py_pattern_ref(string)?;
    let outcome = match core_literal_find_spans(pattern_ref, flags, string_ref, 0, None) {
        Ok(outcome) => outcome,
        Err(error) => return Err(PyTypeError::new_err(error.message())),
    };

    if outcome.status == MatchStatus::Unsupported {
        return Ok(("unsupported", py.None()));
    }

    let items = match string_ref {
        PatternRef::Str(value) => {
            let boundaries = build_str_boundaries(value);
            let Some(limit) = split_limit(maxsplit, outcome.spans.len()) else {
                let list = PyList::empty(py);
                list.append(PyString::new(py, value))?;
                return Ok(("supported", list.unbind().into_any()));
            };

            let list = PyList::empty(py);
            let mut last_end = 0;
            for &(start, end) in outcome.spans.iter().take(limit) {
                list.append(PyString::new(
                    py,
                    str_slice(value, &boundaries, last_end, start),
                ))?;
                last_end = end;
            }
            list.append(PyString::new(
                py,
                str_slice(value, &boundaries, last_end, boundaries.len() - 1),
            ))?;
            list.unbind().into_any()
        }
        PatternRef::Bytes(value) => {
            let Some(limit) = split_limit(maxsplit, outcome.spans.len()) else {
                let list = PyList::empty(py);
                list.append(PyBytes::new(py, value))?;
                return Ok(("supported", list.unbind().into_any()));
            };

            let list = PyList::empty(py);
            let mut last_end = 0;
            for &(start, end) in outcome.spans.iter().take(limit) {
                list.append(PyBytes::new(py, &value[last_end..start]))?;
                last_end = end;
            }
            list.append(PyBytes::new(py, &value[last_end..]))?;
            list.unbind().into_any()
        }
    };

    Ok(("supported", items))
}

#[pyfunction(signature = (pattern, flags, string, pos=0, endpos=None))]
fn boundary_literal_findall(
    py: Python<'_>,
    pattern: &Bound<'_, PyAny>,
    flags: i32,
    string: &Bound<'_, PyAny>,
    pos: isize,
    endpos: Option<isize>,
) -> PyResult<(&'static str, PyObject)> {
    let pattern_ref = py_pattern_ref(pattern)?;
    let string_ref = py_pattern_ref(string)?;
    let outcome = match core_literal_find_spans(pattern_ref, flags, string_ref, pos, endpos) {
        Ok(outcome) => outcome,
        Err(error) => return Err(PyTypeError::new_err(error.message())),
    };

    if outcome.status == MatchStatus::Unsupported {
        return Ok(("unsupported", py.None()));
    }

    let items = match string_ref {
        PatternRef::Str(value) => {
            let boundaries = build_str_boundaries(value);
            let list = PyList::empty(py);
            for &(start, end) in &outcome.spans {
                list.append(PyString::new(py, str_slice(value, &boundaries, start, end)))?;
            }
            list.unbind().into_any()
        }
        PatternRef::Bytes(value) => {
            let list = PyList::empty(py);
            for &(start, end) in &outcome.spans {
                list.append(PyBytes::new(py, &value[start..end]))?;
            }
            list.unbind().into_any()
        }
    };

    Ok(("supported", items))
}

#[pyfunction(signature = (pattern, flags, string, pos=0, endpos=None))]
fn boundary_literal_finditer(
    pattern: &Bound<'_, PyAny>,
    flags: i32,
    string: &Bound<'_, PyAny>,
    pos: isize,
    endpos: Option<isize>,
) -> PyResult<(&'static str, usize, usize, Vec<(usize, usize)>)> {
    let pattern_ref = py_pattern_ref(pattern)?;
    let string_ref = py_pattern_ref(string)?;
    let outcome = match core_literal_find_spans(pattern_ref, flags, string_ref, pos, endpos) {
        Ok(outcome) => outcome,
        Err(error) => return Err(PyTypeError::new_err(error.message())),
    };

    Ok((
        workflow_status(outcome.status),
        outcome.pos,
        outcome.endpos,
        outcome.spans,
    ))
}

#[pyfunction(signature = (pattern, flags, string, pos=0, endpos=None))]
fn boundary_grouped_alternation_finditer(
    pattern: &str,
    flags: i32,
    string: &str,
    pos: isize,
    endpos: Option<isize>,
) -> (
    &'static str,
    usize,
    usize,
    Vec<(usize, usize)>,
    Vec<(usize, usize)>,
) {
    let outcome = core_grouped_alternation_find_spans_str(pattern, flags, string, pos, endpos);
    (
        workflow_status(outcome.status),
        outcome.pos,
        outcome.endpos,
        outcome.matches.iter().map(|matched| matched.span).collect(),
        outcome
            .matches
            .iter()
            .map(|matched| matched.group_1_span)
            .collect(),
    )
}

#[pyfunction(signature = (pattern, flags, string, pos=0, endpos=None))]
fn boundary_nested_capture_finditer(
    pattern: &str,
    flags: i32,
    string: &str,
    pos: isize,
    endpos: Option<isize>,
) -> (
    &'static str,
    usize,
    usize,
    Vec<(usize, usize)>,
    Vec<Vec<Option<(usize, usize)>>>,
) {
    let outcome = core_nested_capture_find_spans_str(pattern, flags, string, pos, endpos);
    (
        workflow_status(outcome.status),
        outcome.pos,
        outcome.endpos,
        outcome.matches.iter().map(|matched| matched.span).collect(),
        outcome
            .matches
            .into_iter()
            .map(|matched| matched.group_spans)
            .collect(),
    )
}

#[pyfunction(signature = (pattern, flags, repl, string, count=0))]
fn boundary_literal_subn(
    py: Python<'_>,
    pattern: &Bound<'_, PyAny>,
    flags: i32,
    repl: &Bound<'_, PyAny>,
    string: &Bound<'_, PyAny>,
    count: isize,
) -> PyResult<(&'static str, PyObject, usize)> {
    let pattern_ref = py_pattern_ref(pattern)?;
    let string_ref = py_pattern_ref(string)?;
    let repl_ref = py_pattern_ref(repl)?;
    let literal_outcome = match core_literal_find_spans(pattern_ref, flags, string_ref, 0, None) {
        Ok(outcome) => outcome,
        Err(error) => return Err(PyTypeError::new_err(error.message())),
    };

    if count < 0 {
        return match string_ref {
            PatternRef::Str(value) => {
                Ok(("supported", PyString::new(py, value).unbind().into_any(), 0))
            }
            PatternRef::Bytes(value) => {
                Ok(("supported", PyBytes::new(py, value).unbind().into_any(), 0))
            }
        };
    }

    match (string_ref, repl_ref) {
        (PatternRef::Str(string_value), PatternRef::Str(repl_value)) => {
            let (status, spans) = if literal_outcome.status != MatchStatus::Unsupported {
                (
                    "supported",
                    literal_outcome
                        .spans
                        .into_iter()
                        .map(|span| CapturedMatchSpan {
                            span,
                            group_spans: Vec::new(),
                        })
                        .collect::<Vec<_>>(),
                )
            } else if let PatternRef::Str(pattern_value) = pattern_ref {
                let outcome = core_conditional_group_exists_find_spans_str(
                    pattern_value,
                    flags,
                    string_value,
                    0,
                    None,
                );
                if outcome.status != MatchStatus::Unsupported {
                    ("supported", outcome.matches)
                } else {
                    let outcome = core_conditional_group_exists_alternation_find_spans_str(
                        pattern_value,
                        flags,
                        string_value,
                        0,
                        None,
                    );
                    if outcome.status != MatchStatus::Unsupported {
                        ("supported", outcome.matches)
                    } else {
                        let outcome = core_conditional_group_exists_no_else_find_spans_str(
                            pattern_value,
                            flags,
                            string_value,
                            0,
                            None,
                        );
                        if outcome.status != MatchStatus::Unsupported {
                            ("supported", outcome.matches)
                        } else {
                            let outcome = core_conditional_group_exists_empty_else_find_spans_str(
                                pattern_value,
                                flags,
                                string_value,
                                0,
                                None,
                            );
                            if outcome.status != MatchStatus::Unsupported {
                                ("supported", outcome.matches)
                            } else {
                                let outcome =
                                    core_conditional_group_exists_empty_yes_else_find_spans_str(
                                        pattern_value,
                                        flags,
                                        string_value,
                                        0,
                                        None,
                                    );
                                if outcome.status == MatchStatus::Unsupported {
                                    return Ok(("unsupported", py.None(), 0));
                                }
                                ("supported", outcome.matches)
                            }
                        }
                    }
                }
            } else {
                return Ok(("unsupported", py.None(), 0));
            };

            let replacement_limit = if count == 0 {
                spans.len()
            } else {
                replacement_limit(count, spans.len())
            };
            if replacement_limit == 0 {
                return Ok((
                    status,
                    PyString::new(py, string_value).unbind().into_any(),
                    0,
                ));
            }

            let boundaries = build_str_boundaries(string_value);
            let mut output = String::new();
            let mut last_end = 0;
            for matched in spans.iter().take(replacement_limit) {
                let (start, end) = matched.span;
                output.push_str(str_slice(string_value, &boundaries, last_end, start));
                output.push_str(repl_value);
                last_end = end;
            }
            output.push_str(str_slice(
                string_value,
                &boundaries,
                last_end,
                boundaries.len() - 1,
            ));
            Ok((
                status,
                PyString::new(py, &output).unbind().into_any(),
                replacement_limit,
            ))
        }
        (PatternRef::Bytes(string_value), PatternRef::Bytes(repl_value)) => {
            if literal_outcome.status == MatchStatus::Unsupported {
                return Ok(("unsupported", py.None(), 0));
            }
            let replacement_limit = if count == 0 {
                literal_outcome.spans.len()
            } else {
                replacement_limit(count, literal_outcome.spans.len())
            };
            if replacement_limit == 0 {
                return Ok((
                    "supported",
                    PyBytes::new(py, string_value).unbind().into_any(),
                    0,
                ));
            }

            let mut output = Vec::new();
            let mut last_end = 0;
            for &(start, end) in literal_outcome.spans.iter().take(replacement_limit) {
                output.extend_from_slice(&string_value[last_end..start]);
                output.extend_from_slice(repl_value);
                last_end = end;
            }
            output.extend_from_slice(&string_value[last_end..]);
            Ok((
                "supported",
                PyBytes::new(py, &output).unbind().into_any(),
                replacement_limit,
            ))
        }
        _ => Err(PyTypeError::new_err("replacement must match pattern type")),
    }
}

#[pyfunction(signature = (pattern, flags, repl, string, count=0))]
fn boundary_literal_template_subn(
    py: Python<'_>,
    pattern: &Bound<'_, PyAny>,
    flags: i32,
    repl: &str,
    string: &Bound<'_, PyAny>,
    count: isize,
) -> PyResult<(&'static str, PyObject, usize)> {
    let pattern_ref = py_pattern_ref(pattern)?;
    let string_ref = py_pattern_ref(string)?;
    let (status, matches, group_count, named_groups) = match (pattern_ref, string_ref) {
        (PatternRef::Str(pattern_value), PatternRef::Str(string_value)) => {
            let literal_outcome =
                match core_literal_find_spans(pattern_ref, flags, string_ref, 0, None) {
                    Ok(outcome) => outcome,
                    Err(error) => return Err(PyTypeError::new_err(error.message())),
                };
            if literal_outcome.status != MatchStatus::Unsupported {
                (
                    literal_outcome.status,
                    literal_outcome
                        .spans
                        .into_iter()
                        .map(|span| CapturedMatchSpan {
                            span,
                            group_spans: Vec::new(),
                        })
                        .collect(),
                    0,
                    Vec::new(),
                )
            } else {
                let compile_outcome = core_compile(pattern_ref, flags)
                    .map_err(|error| PyTypeError::new_err(error.message))?;
                let grouped_literal_outcome = core_grouped_literal_find_spans_str(
                    pattern_value,
                    flags,
                    string_value,
                    0,
                    None,
                );
                if grouped_literal_outcome.status != MatchStatus::Unsupported {
                    (
                        grouped_literal_outcome.status,
                        grouped_literal_outcome
                            .spans
                            .into_iter()
                            .map(|span| CapturedMatchSpan {
                                span,
                                group_spans: if compile_outcome.group_count == 1 {
                                    vec![Some(span)]
                                } else {
                                    Vec::new()
                                },
                            })
                            .collect(),
                        compile_outcome.group_count,
                        compile_outcome.named_groups,
                    )
                } else {
                    let nested_capture_outcome = core_nested_capture_find_spans_str(
                        pattern_value,
                        flags,
                        string_value,
                        0,
                        None,
                    );
                    if nested_capture_outcome.status != MatchStatus::Unsupported {
                        (
                            nested_capture_outcome.status,
                            nested_capture_outcome.matches,
                            compile_outcome.group_count,
                            compile_outcome.named_groups,
                        )
                    } else {
                        let grouped_alternation_outcome = core_grouped_alternation_find_spans_str(
                            pattern_value,
                            flags,
                            string_value,
                            0,
                            None,
                        );
                        (
                            grouped_alternation_outcome.status,
                            grouped_alternation_outcome
                                .matches
                                .into_iter()
                                .map(|matched| CapturedMatchSpan {
                                    span: matched.span,
                                    group_spans: vec![Some(matched.group_1_span)],
                                })
                                .collect(),
                            compile_outcome.group_count,
                            compile_outcome.named_groups,
                        )
                    }
                }
            }
        }
        _ => {
            let outcome = match core_literal_find_spans(pattern_ref, flags, string_ref, 0, None) {
                Ok(outcome) => outcome,
                Err(error) => return Err(PyTypeError::new_err(error.message())),
            };
            (
                outcome.status,
                outcome
                    .spans
                    .into_iter()
                    .map(|span| CapturedMatchSpan {
                        span,
                        group_spans: Vec::new(),
                    })
                    .collect(),
                0,
                Vec::new(),
            )
        }
    };

    if core_expand_literal_replacement_template_str(
        repl,
        "",
        &vec![Some(""); group_count],
        &named_groups
            .iter()
            .map(|group| (group.name.as_str(), ""))
            .collect::<Vec<_>>(),
    )
    .is_none()
    {
        return Ok(("unsupported", py.None(), 0));
    }
    if status == MatchStatus::Unsupported {
        return Ok(("unsupported", py.None(), 0));
    }
    if count < 0 {
        return match string_ref {
            PatternRef::Str(value) => {
                Ok(("supported", PyString::new(py, value).unbind().into_any(), 0))
            }
            PatternRef::Bytes(value) => {
                Ok(("supported", PyBytes::new(py, value).unbind().into_any(), 0))
            }
        };
    }
    let replacement_limit = replacement_limit(count, matches.len());

    match string_ref {
        PatternRef::Str(string_value) => {
            if replacement_limit == 0 {
                return Ok((
                    "supported",
                    PyString::new(py, string_value).unbind().into_any(),
                    0,
                ));
            }

            let boundaries = build_str_boundaries(string_value);
            let mut output = String::new();
            let mut last_end = 0;
            for matched in matches.iter().take(replacement_limit) {
                let (start, end) = matched.span;
                output.push_str(str_slice(string_value, &boundaries, last_end, start));
                let whole_match = str_slice(string_value, &boundaries, start, end);
                let numbered_captures = matched
                    .group_spans
                    .iter()
                    .map(|span| {
                        span.map(|(capture_start, capture_end)| {
                            str_slice(string_value, &boundaries, capture_start, capture_end)
                        })
                    })
                    .collect::<Vec<_>>();
                let named_captures = named_groups
                    .iter()
                    .filter_map(|group| {
                        numbered_captures
                            .get(group.index - 1)
                            .copied()
                            .flatten()
                            .map(|capture| (group.name.as_str(), capture))
                    })
                    .collect::<Vec<_>>();
                let expanded = core_expand_literal_replacement_template_str(
                    repl,
                    whole_match,
                    &numbered_captures,
                    &named_captures,
                )
                .ok_or_else(|| PyTypeError::new_err("unsupported literal replacement template"))?;
                output.push_str(&expanded);
                last_end = end;
            }
            output.push_str(str_slice(
                string_value,
                &boundaries,
                last_end,
                boundaries.len() - 1,
            ));
            Ok((
                "supported",
                PyString::new(py, &output).unbind().into_any(),
                replacement_limit,
            ))
        }
        PatternRef::Bytes(_) => Err(PyTypeError::new_err("replacement must match pattern type")),
    }
}

#[pyfunction]
fn boundary_escape(py: Python<'_>, pattern: &Bound<'_, PyAny>) -> PyResult<PyObject> {
    if let Ok(value) = pattern.extract::<&str>() {
        return Ok(PyString::new(py, &core_escape_str(value))
            .unbind()
            .into_any());
    }
    if let Ok(value) = pattern.downcast::<PyBytes>() {
        return Ok(PyBytes::new(py, &core_escape_bytes(value.as_bytes()))
            .unbind()
            .into_any());
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
    module.add(
        "__doc__",
        "Native boundary module for the current rebar `re` subset.",
    )?;
    module.add("__rebar_scaffold__", true)?;
    module.add("TARGET_CPYTHON_SERIES", TARGET_CPYTHON_SERIES)?;
    module.add("SCAFFOLD_STATUS", SCAFFOLD_STATUS)?;
    module.add_function(wrap_pyfunction!(target_cpython_series, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_status, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_raise, module)?)?;
    module.add_function(wrap_pyfunction!(scaffold_pattern_raise, module)?)?;
    module.add_function(wrap_pyfunction!(boundary_compile, module)?)?;
    module.add_function(wrap_pyfunction!(boundary_literal_match, module)?)?;
    module.add_function(wrap_pyfunction!(boundary_literal_split, module)?)?;
    module.add_function(wrap_pyfunction!(boundary_literal_findall, module)?)?;
    module.add_function(wrap_pyfunction!(boundary_literal_finditer, module)?)?;
    module.add_function(wrap_pyfunction!(boundary_nested_capture_finditer, module)?)?;
    module.add_function(wrap_pyfunction!(
        boundary_grouped_alternation_finditer,
        module
    )?)?;
    module.add_function(wrap_pyfunction!(boundary_literal_subn, module)?)?;
    module.add_function(wrap_pyfunction!(boundary_literal_template_subn, module)?)?;
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
