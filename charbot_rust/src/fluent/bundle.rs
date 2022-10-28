// SPDX-FileCopyrightText: 2022 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
//
// SPDX-License-Identifier: MIT
use fluent::{FluentBundle, FluentResource}; // fluent translation stuff
use crate::fluent::common; // ftl files
// Used to provide a locale for the bundle.
use unic_langid::LanguageIdentifier;

#[allow(unused)]
pub enum AvailableLocales {
    AmericanEnglish,
    EuropeanSpanish,
    French,
    Dutch,
}

impl AvailableLocales {
    #[allow(unused)]
    pub fn get_locale(&self) -> LanguageIdentifier {
        match self {
            AvailableLocales::AmericanEnglish => "en-US".parse().expect("Parsing failed"),
            AvailableLocales::EuropeanSpanish => "es-ES".parse().expect("Parsing failed"),
            AvailableLocales::French => "fr".parse().expect("Parsing failed"),
            AvailableLocales::Dutch => "nl".parse().expect("Parsing failed"),
        }
    }
    #[allow(unused)]
    pub fn from_locale_string(locale: &str) -> Option<AvailableLocales> {
        match locale {
            "en-US" => Some(AvailableLocales::AmericanEnglish),
            "es-ES" => Some(AvailableLocales::EuropeanSpanish),
            "fr" => Some(AvailableLocales::French),
            "nl" => Some(AvailableLocales::Dutch),
            _ => None,
        }
    }
    #[allow(unused)]
    pub fn locale_string(&self) -> String {
        match self {
            AvailableLocales::AmericanEnglish => "en-US".to_string(),
            AvailableLocales::EuropeanSpanish => "es-ES".to_string(),
            AvailableLocales::French => "fr".to_string(),
            AvailableLocales::Dutch => "nl".to_string(),
        }
    }
}

#[allow(unused)]
pub(crate) fn get_bundle(locale: AvailableLocales) -> Result<FluentBundle<FluentResource>, String>{
    match locale {
        AvailableLocales::AmericanEnglish => {
            let mut bundle = FluentBundle::new(vec!["en-US".parse().expect("Parsing failed")]);
            let resources = vec![
                common::EN_US_DICE,
                common::EN_US_ERRORS,
                common::EN_US_GIVEAWAY,
                common::EN_US_LEVELS,
                common::EN_US_MINESWEEPER,
                common::EN_US_PROGRAMS
            ];
            for resource in resources {add_resource(&mut bundle, resource)?}
            Ok(bundle)
        },
        AvailableLocales::EuropeanSpanish => {
            let mut bundle = FluentBundle::new(vec!["es-ES".parse().expect("Parsing failed")]);
            let resources = vec![
                common::ES_ES_DICE,
                common::ES_ES_ERRORS,
                common::ES_ES_GIVEAWAY,
                common::ES_ES_LEVELS,
                common::ES_ES_MINESWEEPER,
                common::ES_ES_PROGRAMS];
            for resource in resources {add_resource(&mut bundle, resource)?}
            Ok(bundle)
        },
        AvailableLocales::French => {
            let mut bundle = FluentBundle::new(vec!["fr".parse().expect("Parsing failed")]);
            let resources = vec![
                common::FR_DICE,
                common::FR_ERRORS,
                common::FR_GIVEAWAY,
                common::FR_LEVELS,
                common::FR_MINESWEEPER,
                common::FR_PROGRAMS
            ];
            for resource in resources {add_resource(&mut bundle, resource)?}
            Ok(bundle)
        },
        AvailableLocales::Dutch => {
            let mut bundle = FluentBundle::new(vec!["nl".parse().expect("Parsing failed")]);
            let resources = vec![
                common::NL_DICE,
                common::NL_ERRORS,
                common::NL_GIVEAWAY,
                common::NL_LEVELS,
                common::NL_MINESWEEPER,
                common::NL_PROGRAMS
            ];
            for resource in resources {add_resource(&mut bundle, resource)?}
            Ok(bundle)
        },
    }
}

fn add_resource(bundle: &mut FluentBundle<FluentResource>, source: &'static str) -> Result<(), String> {
    match FluentResource::try_new(source.to_string()) {
        Ok(res) => {
            if bundle.add_resource(res).is_err() {
                return Err("Failed to add FTL resources to the bundle.".to_string());
            }
        },
        Err(_) => return Err("String could not be turned into a FluentResource".to_string()),
    }
    Ok(())
}
