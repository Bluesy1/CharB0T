use fluent::{FluentBundle, FluentResource}; // fluent translation stuff
use crate::fluent::common; // ftl files

#[derive(Debug, PartialEq, Eq)]  // COV_EXCL_LINE
pub enum AvailableLocales {
    AmericanEnglish,
    EuropeanSpanish,
    French,
    Dutch,
}

impl AvailableLocales {
    pub fn from_str(locale: &str) -> Option<AvailableLocales> {
        match locale {
            "en-US" => Some(AvailableLocales::AmericanEnglish),
            "es-ES" => Some(AvailableLocales::EuropeanSpanish),
            "fr" => Some(AvailableLocales::French),
            "nl" => Some(AvailableLocales::Dutch),
            _ => None,  //COV_EXCL_LINE
        }
    }
}

#[allow(unused)]
pub(crate) fn get_bundle(locale: AvailableLocales) -> Result<FluentBundle<FluentResource>, String>{
    match locale {
        AvailableLocales::AmericanEnglish => {
            let mut bundle = FluentBundle::new(
                vec!["en-US".parse().expect("Parsing failed")]
            );
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
        //COV_EXCL_START
        AvailableLocales::EuropeanSpanish => {
            let mut bundle = FluentBundle::new(
                vec!["es-ES".parse().expect("Parsing failed")])
                ;
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
            let mut bundle = FluentBundle::new(
                vec!["fr".parse().expect("Parsing failed")]
            );
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
            let mut bundle = FluentBundle::new(
                vec!["nl".parse().expect("Parsing failed")]
            );
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
        //COV_EXCL_STOP
    }
}

fn add_resource(bundle: &mut FluentBundle<FluentResource>, source: &'static str) -> Result<(), String> {
    match FluentResource::try_new(source.to_string()) {
        Ok(res) => {
            if bundle.add_resource(res).is_err() {
                return Err("Failed to add FTL resources to the bundle.".to_string());  //COV_EXCL_LINE
            }
        },
        Err(_) => return Err("String could not be turned into a FluentResource".to_string()),  //COV_EXCL_LINE
    }
    Ok(())
}


#[cfg(test)]
mod tests{

    #[test]
    fn test_available_locales_from_str() {
        use super::AvailableLocales;
        assert_eq!(AvailableLocales::from_str("en-US"), Some(AvailableLocales::AmericanEnglish));
        assert_eq!(AvailableLocales::from_str("es-ES"), Some(AvailableLocales::EuropeanSpanish));
        assert_eq!(AvailableLocales::from_str("fr"), Some(AvailableLocales::French));
        assert_eq!(AvailableLocales::from_str("nl"), Some(AvailableLocales::Dutch));
        assert_eq!(AvailableLocales::from_str("de"), None);
    }
}
