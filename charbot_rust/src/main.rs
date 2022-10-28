// SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
// SPDX-License-Identifier: MIT
use std::fs;

use fluent::{FluentBundle, FluentValue, FluentResource, FluentArgs};
// Used to provide a locale for the bundle.
use unic_langid::LanguageIdentifier;

fn main(){
    let ftl_string = fs::read_to_string("../i18n/en-US/dice.ftl")
        .expect("Should have been able to read the file");
    let res = FluentResource::try_new(ftl_string)
    .expect("Failed to parse an FTL string.");

    let langid_en: LanguageIdentifier = "en-US".parse().expect("Parsing failed");
    let mut bundle: FluentBundle<FluentResource> = FluentBundle::new(vec![langid_en]);

    bundle
        .add_resource(res)
        .expect("Failed to add FTL resources to the bundle.");

    let mut args = FluentArgs::new();
    args.set("user", FluentValue::from("Bluesy"));

    let msg = bundle.get_message("error")
        .expect("Message doesn't exist.");
    let mut errors = vec![];
    let pattern = msg.value().expect("Message has no value.");
    let value = bundle.format_pattern(pattern, Some(&args), &mut errors);
    println!("{value}");

    let mut args2 = FluentArgs::new();
    args2.set("user", FluentValue::from("Bluesy"));
    args2.set("dice", FluentValue::from("1d20+5"));
    args2.set("result", FluentValue::from("20+5"));
    args2.set("total", FluentValue::from("25"));
    let msg2 = bundle.get_message("success")
        .expect("Message doesn't exist.");
    let mut errors2 = vec![];
    let pattern2 = msg2.value().expect("Message has no value.");
    let value2 = bundle.format_pattern(pattern2, Some(&args2), &mut errors2);
    println!("{value2}");
}
