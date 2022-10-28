// SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
//
// SPDX-License-Identifier: MIT
use std::collections::HashMap;

use crate::fluent::bundle;
use fluent::{FluentBundle, FluentResource, FluentArgs, FluentValue};
use fluent_syntax::unicode::unescape_unicode_to_string;
use pyo3::{PyAny, PyErr, PyResult};
use pyo3::exceptions::{PyKeyError, PyTypeError, PyValueError};

pub(crate) struct Translator {
    bundle: FluentBundle<FluentResource>,
    fallback_bundle: FluentBundle<FluentResource>,
}

impl Translator{
    pub(crate) fn new(locale: bundle::AvailableLocales) -> Result<Self, String> {
        let bundle = bundle::get_bundle(locale)?;
        let fallback_bundle = bundle::get_bundle(bundle::AvailableLocales::AmericanEnglish)?;
        Ok(Self {
            bundle,
            fallback_bundle,
        })
    }

    pub(crate) fn translate(&self, key: &str, args: HashMap<String, &PyAny>) -> PyResult<String> {
        let message = self.bundle.get_message(key).ok_or_else(|| {
            PyKeyError::new_err(format!("Message with key {key} not found"))
        })?;
        let pattern = message.value().ok_or_else(|| {
            PyValueError::new_err(format!("Message with key {key} has no value"))
        })?;
        let mut errors = vec![];
        let mut fluent_args = FluentArgs::new();
        let mut err: Option<PyErr> = None;
        args.iter().for_each(|(key, value)| {
            if let Ok(val) = value.extract::<String>() {
                fluent_args.set(key, FluentValue::from(val));
            } else if let Ok(val) = value.extract::<i64>() {
                fluent_args.set(key, FluentValue::from(val));
            } else if let Ok(val) = value.extract::<f64>() {
                fluent_args.set(key, FluentValue::from(val));
            } else {
                err = Some(PyTypeError::new_err(format!("Value for key {key} is not a string, int or float")));
            }
        });
        if let Some(err) = err {
            return Err(err);
        }
        let value = self.bundle.format_pattern(pattern, Some(&fluent_args), &mut errors);
        if errors.is_empty() {
                let s = unescape_unicode_to_string(value.parse::<String>().expect("Failed to parse value").as_str()).into_owned();
                Ok(s)
        } else {
            let message = self.fallback_bundle.get_message(key).ok_or_else(|| {
                PyKeyError::new_err(format!("Message with key {key} not found"))
            })?;
            let pattern = message.value().ok_or_else(|| {
                PyValueError::new_err(format!("Message with key {key} has no value"))
            })?;
            let mut errors = vec![];
            let value = self.fallback_bundle.format_pattern(pattern, Some(&fluent_args), &mut errors);
            if errors.is_empty() {
                let s = unescape_unicode_to_string(value.parse::<String>().expect("Failed to parse value").as_str()).into_owned();
                Ok(s)
            } else {
                Err(PyValueError::new_err("Translation failed"))
            }
        }
    }
}
