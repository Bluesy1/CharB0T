// SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
//
// SPDX-License-Identifier: MIT
mod common;
mod bundle;
mod translator;

use std::collections::HashMap;

use pyo3::prelude::PyModule;
use pyo3::{PyAny, PyResult, pyfunction,  wrap_pyfunction};
use pyo3::exceptions::PyValueError;

#[pyfunction]
pub(crate) fn translate(locale: String, key: String, args: HashMap<String, &PyAny>) -> PyResult<String>{
    if let Some(enum_locale) = bundle::AvailableLocales::from_str(locale.as_str()) {
        let translator = translator::Translator::new(enum_locale).map_err(|e| {
            PyValueError::new_err(format!("Failed to create translator: {e}"))
        })?;
        translator.translate(&key, args)
    } else {
        Err(PyValueError::new_err(format!("Locale {locale} not found, choose from {}", bundle::AvailableLocales::variants())))
    }
}

pub(crate) fn register_fluent(m: &PyModule) -> PyResult<()>{
    m.add_function(wrap_pyfunction!(translate, m)?)?;
    Ok(())
}
