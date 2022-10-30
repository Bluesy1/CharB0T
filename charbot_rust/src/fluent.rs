// SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
//
// SPDX-License-Identifier: MIT
mod common;
mod bundle;
mod translator;

use std::collections::HashMap;

use pyo3::prelude::PyModule;
use pyo3::{PyResult, pyfunction, wrap_pyfunction};
use pyo3::exceptions::{PyRuntimeError};

#[pyfunction]
#[pyo3(text_signature = "
translate(locale, key, args, /)
--

Translate a string into the given locale.

Parameters
----------
locale : {'en-US', 'es-ES', 'fr', 'nl'}
    The locale to translate to, e.g. 'en-US'. If the locale exists, but the key does not,
     en-US will be used if the key exists there.
key : str
    The key to translate.
args : dict[str, int | float | str]
    The arguments to format the string with. If no arguments, pass an empty dict, ie ``{}``.

Returns
-------
str
    The translated string.

Raises
------
RuntimeError
    If anything errors.
")]
pub(crate) fn translate(locale: String, key: String, args: HashMap<String, translator::ArgTypes>) -> PyResult<String>{
    if let Some(enum_locale) = bundle::AvailableLocales::from_str(locale.as_str()) {
        let translator = translator::Translator::new(enum_locale).map_err(|e| {
            PyRuntimeError::new_err(format!("Failed to create translator: {e}"))
        }).map_err(|e| PyRuntimeError::new_err(e))?;
        translator.translate(&key, args).map_err(|e| PyRuntimeError::new_err(format!("Failed to translate: {e}")))
    } else {
        Err(PyRuntimeError::new_err(format!("Locale {locale} not found, choose from {}", bundle::AvailableLocales::variants())))
    }
}

pub(crate) fn register_fluent(m: &PyModule) -> PyResult<()>{
    m.add_function(wrap_pyfunction!(translate, m)?)?;
    Ok(())
}
