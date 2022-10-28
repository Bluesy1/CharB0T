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
KeyError
    If the key does not exist in the given locale.
ValueError
    If the key exists in the given locale, but the string cannot be interpreted, or translation fails.
TypeError
    If a non string, int, or float is passed as an arg value.
")]
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
