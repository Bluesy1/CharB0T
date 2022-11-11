// SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
//
// SPDX-License-Identifier: MIT
use std::collections::HashMap;

use crate::fluent::bundle;
use fluent::{FluentBundle, FluentResource, FluentArgs, FluentValue};
use pyo3::{FromPyObject};
use encoding::all::ASCII;
use encoding::{DecoderTrap, EncoderTrap, Encoding};

// COV_EXCL_START
#[derive(FromPyObject, Clone)]
pub enum ArgTypes {
    #[pyo3(transparent)]
    Int(i64),
    #[pyo3(transparent)]
    Float(f64),
    #[pyo3(transparent)]
    String(String),
}
// COV_EXCL_STOP

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

    pub(crate) fn translate(&self, key: &str, args: HashMap<String, ArgTypes>) -> Result<String, String> {
        let message = self.bundle.get_message(key).ok_or_else(|| {
            format!("Message with key {key} not found")
        })?;
        let pattern = message.value().ok_or_else(|| {
            format!("Message with key {key} has no value")  //COV_EXCL_LINE
        })?;  //COV_EXCL_LINE
        let mut fluent_args = FluentArgs::new();
        args.iter().for_each(|(key, value)| {
            match value {
                ArgTypes::Int(int) => {
                    fluent_args.set(key, FluentValue::from(int));
                }
                ArgTypes::Float(float) => {
                    fluent_args.set(key, FluentValue::from(float));
                }
                ArgTypes::String(string) => {
                    fluent_args.set(key, FluentValue::from(string.as_str()));
                }
            }
        });
        let mut errors = vec![];
        let value = self.bundle.format_pattern(pattern, Some(&fluent_args), &mut errors);
        if errors.is_empty() {
            Ok(ASCII.decode(
                &ASCII.encode(value.parse::<String>()
                         .map_err(|e| format!("Failed to parse value: {e}"))?  //COV_EXCL_LINE
                         .as_str(), EncoderTrap::Ignore)?,
                DecoderTrap::Ignore
                )?)  // COV_EXCL_LINE
        } else {
            // COV_EXCL_START
            let message = self.fallback_bundle.get_message(key).ok_or_else(|| {
                format!("Message with key {key} not found")
            })?;
            let pattern = message.value().ok_or_else(|| {
                format!("Message with key {key} has no value")
            })?;
            let mut errors = vec![];
            let value = self.fallback_bundle.format_pattern(pattern, Some(&fluent_args), &mut errors);
            if errors.is_empty() {
                Ok(ASCII.decode(
                    &ASCII.encode(value.parse::<String>()
                                  .map_err(|e| format!("Failed to parse value: {e}"))?
                                  .as_str(), EncoderTrap::Ignore)?,
                    DecoderTrap::Ignore
                )?)
            } else {// COV_EXCL_STOP  // COV_EXCL_LINE
                Err(format!("Translation failed: {}", errors
                    .iter()
                    .map(|e| e.to_string())
                    .collect::<Vec<String>>()
                    .join(", ")))
            }

        }
    }
}

// COV_EXCL_START
#[cfg(test)]
mod tests {
    use std::collections::HashMap;

    use crate::fluent::bundle::AvailableLocales;
    use crate::fluent::translator::{ArgTypes, Translator};

    #[test]
    fn test_translate() {
        let translator = Translator::new(AvailableLocales::AmericanEnglish)
            .expect("Failed to create translator");
        let mut args = HashMap::new();
        args.insert("user".to_string(), ArgTypes::String("John".to_string()));
        args.insert("command".to_string(), ArgTypes::String("help".to_string()));
        match translator.translate("check-failed", args){
            Ok(translation) => {
                assert_eq!(translation, "John, you can't use help.");
            }
            Err(e) => {
                panic!("Failed to translate: {e}");
            }
        }
    }

    #[test]
    fn test_nonexistent_key() {
        let translator = Translator::new(AvailableLocales::AmericanEnglish)
            .expect("Failed to create translator");
        let mut args = HashMap::new();
        args.insert("user".to_string(), ArgTypes::String("John".to_string()));
        args.insert("command".to_string(), ArgTypes::String("help".to_string()));
        match translator.translate("nonexistent-key", args){
            Ok(_) => {
                panic!("Translation should have failed");
            }
            Err(e) => {
                assert_eq!(e, "Message with key nonexistent-key not found");
            }
        }
    }

    #[test]
    fn test_all_arg_types() {
        let translator = Translator::new(AvailableLocales::AmericanEnglish)
            .expect("Failed to create translator");
        let mut args = HashMap::new();
        args.insert("user".to_string(), ArgTypes::String("John".to_string()));
        args.insert("dice".to_string(), ArgTypes::String("1d6".to_string()));
        args.insert("result".to_string(), ArgTypes::Int(1));
        args.insert("total".to_string(), ArgTypes::Float(1.0));
        match translator.translate("success", args){
            Ok(translation) => {
                assert_eq!(translation, "John rolled `1d6` and got `1`for a total of `1`.");
            }
            Err(e) => {
                panic!("Failed to translate: {e}");
            }
        }
    }

    #[test]
    fn test_missing_test_key() {
        let translator = Translator::new(AvailableLocales::AmericanEnglish)
            .expect("Failed to create translator");
        let mut args = HashMap::new();
        args.insert("user".to_string(), ArgTypes::String("John".to_string()));
        args.insert("dice".to_string(), ArgTypes::String("1d6".to_string()));
        args.insert("rolled".to_string(), ArgTypes::Int(1));
        args.insert("total".to_string(), ArgTypes::Float(1.0));
        match translator.translate("success", args){
            Ok(_) => {
                panic!("Translation should have failed");
            }
            Err(e) => {
                assert_eq!(e, "Translation failed: Resolver error: Unknown variable: $result");
            }
        }
    }

    #[test]
    #[allow(clippy::assertions_on_constants)]
    fn test_giveaway_check_success_key() {
        let translator = Translator::new(AvailableLocales::AmericanEnglish)
            .expect("Failed to create translator");
        let mut args = HashMap::new();
        args.insert("bid".to_string(), ArgTypes::Int(1));
        args.insert("chance".to_string(), ArgTypes::Float(25.00));
        args.insert("wins".to_string(), ArgTypes::Int(1));
        match translator.translate("giveaway-check-success", args){
            Ok(_) => {
                assert!(true);
            }
            Err(e) => {
                panic!("Failed to translate: {e}");
            }
        }
    }

    #[test]
    #[allow(clippy::assertions_on_constants)]
    fn test_giveaway_bid_success_key() {
        let translator = Translator::new(AvailableLocales::AmericanEnglish)
            .expect("Failed to create translator");
        let mut args = HashMap::new();
        args.insert("bid".to_string(), ArgTypes::Int(1));
        args.insert("new_bid".to_string(), ArgTypes::Int(2));
        args.insert("points".to_string(), ArgTypes::Int(50));
        args.insert("chance".to_string(), ArgTypes::Float(25.00));
        args.insert("wins".to_string(), ArgTypes::Int(1));
        match translator.translate("giveaway-bid-success", args){
            Ok(_) => {
                assert!(true);
            }
            Err(e) => {
                panic!("Failed to translate: {e}");
            }
        }
    }
}
// COV_EXCL_STOP
