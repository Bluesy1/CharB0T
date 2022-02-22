import asyncio
import json
import os
import time
from datetime import datetime, timezone

import lightbulb
from hikari.embeds import Embed
from hikari.events.interaction_events import InteractionCreateEvent
from hikari.interactions.base_interactions import ResponseType
from hikari.messages import ButtonStyle
from lightbulb import commands, SlashCommandGroup, SlashSubGroup, SlashContext, SlashSubCommand
from lightbulb.checks import has_roles

AdminPlugin = lightbulb.Plugin("AdminPlugin", default_enabled_guilds=[225345178955808768])
AdminPlugin.add_checks(has_roles(338173415527677954, 253752685357039617, 225413350874546176, mode=any))


@AdminPlugin.command
@lightbulb.command(
    "maketime", "makes a unix time constructor for use with discord's unix time feature",
    guilds=[225345178955808768])
@lightbulb.implements(commands.SlashCommand)
async def command(ctx):  # pylint: disable=too-many-statements
    """Command that makes a unix time constructor for use with discord's unix time feature"""
    time_menu = AdminPlugin.bot.rest.build_action_row()
    (time_menu.add_select_menu("Editing")
     .add_option("Done", "Done").set_emoji("✅").set_description("Use this to get the final options").add_to_menu()
     .add_option("+30 minutes", "+m").set_emoji("➡️").set_description(
        "Use this to increase the time by 30 minutes").add_to_menu()
     .add_option("-30 minutes", "-m").set_emoji("⬅️").set_description(
        "Use this to decrease the time by 30 minutes").add_to_menu()
     .add_option("+1 hour", "+h").set_emoji("➡️").set_description(
        "Use this to increase the time by 1 hour").add_to_menu()
     .add_option("-1 hour", "-h").set_emoji("◀️").set_description(
        "Use this to decrease the time by 1 hour").add_to_menu()
     .add_option("-1 day", "-d").set_emoji("⬅️").set_description("Use this to decrease the time by 1 day").add_to_menu()
     .add_option("+1 day", "+d").set_emoji("▶️").set_description("Use this to increase the time by 1 day").add_to_menu()
     .add_option("+1 week", "+w").set_emoji("➡️").set_description(
        "Use this to increase the time by 1 week").add_to_menu()
     .add_option("-1 week", "-w").set_emoji("◀️").set_description(
        "Use this to decrease the time by 1 week").add_to_menu()
     .add_to_container()
     )
    add_buttons = AdminPlugin.bot.rest.build_action_row()
    add_buttons.add_button(ButtonStyle.SUCCESS, "+w").set_label("+1 week").set_emoji("▶️").add_to_container()
    add_buttons.add_button(ButtonStyle.SUCCESS, "+d").set_label("+1 day").set_emoji("▶️").add_to_container()
    add_buttons.add_button(ButtonStyle.SUCCESS, "+h").set_label("+1 hour").set_emoji("▶️").add_to_container()
    add_buttons.add_button(ButtonStyle.SUCCESS, "+m").set_label("+30 minutes").set_emoji("▶️").add_to_container()
    add_buttons.add_button(ButtonStyle.PRIMARY, "Done").set_label("Done").set_emoji("✅").add_to_container()
    sub_buttons = AdminPlugin.bot.rest.build_action_row()
    sub_buttons.add_button(ButtonStyle.DANGER, "-w").set_label("-1 week").set_emoji("◀️").add_to_container()
    sub_buttons.add_button(ButtonStyle.DANGER, "-d").set_label("-1 day").set_emoji("◀️").add_to_container()
    sub_buttons.add_button(ButtonStyle.DANGER, "-h").set_label("-1 hour").set_emoji("◀️").add_to_container()
    sub_buttons.add_button(ButtonStyle.DANGER, "-m").set_label("-30 minutes").set_emoji("◀️").add_to_container()
    os.environ['TZ'] = 'US/Eastern'
    time.tzset()
    time_seconds = round(time.time())
    time_seconds -= time_seconds % 1800
    embed = Embed(title="Time builder", description=f"timestamp: {time_seconds}: <t:{time_seconds}:F>")
    await ctx.respond("Use the select menu to adjust the time", embed=embed, components=[add_buttons, sub_buttons])
    try:
        async with AdminPlugin.bot.stream(InteractionCreateEvent, timeout=15).filter(
                ('interaction.user.id', ctx.author.id)) as stream:
            async for event in stream:
                await event.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_UPDATE)
                key = event.interaction.custom_id
                if key == "Done":
                    embed = (Embed(title="Final times", description=f"timestamp: {time_seconds}: <t:{time_seconds}:F>")
                             .add_field(f"Default: `<t:{time_seconds}>`", f"<t:{time_seconds}>")
                             .add_field(f"Short Time: `<t:{time_seconds}:t>`", f"<t:{time_seconds}:t>")
                             .add_field(f"Long Time: `<t:{time_seconds}:T>`", f"<t:{time_seconds}:t>")
                             .add_field(f"Short Date: `<t:{time_seconds}:d>`", f"<t:{time_seconds}:d>")
                             .add_field(f"Long Date: `<t:{time_seconds}:D>`", f"<t:{time_seconds}:D>")
                             .add_field(f"Short Date/Time: `<t:{time_seconds}:f>`", f"<t:{time_seconds}:f>")
                             .add_field(f"Long Date/Time: `<t:{time_seconds}:F>`", f"<t:{time_seconds}:F>")
                             .add_field(f"Relative Time: `<t:{time_seconds}:R>`", f"<t:{time_seconds}:R>")
                             )
                    await ctx.edit_last_response(f"<t:{time_seconds}", embed=embed, components=[])
                    return
                if key == "+w":
                    time_seconds += 604800
                    embed = Embed(title="Time builder", description=f"timestamp: {time_seconds}: <t:{time_seconds}:F>")
                    await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed,
                                                 components=[add_buttons, sub_buttons])
                elif key == "+d":
                    time_seconds += 86400
                    embed = Embed(title="Time builder", description=f"timestamp: {time_seconds}: <t:{time_seconds}:F>")
                    await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed,
                                                 components=[add_buttons, sub_buttons])
                elif key == "+h":
                    time_seconds += 3600
                    embed = Embed(title="Time builder", description=f"timestamp: {time_seconds}: <t:{time_seconds}:F>")
                    await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed,
                                                 components=[add_buttons, sub_buttons])
                elif key == "+m":
                    time_seconds += 1800
                    embed = Embed(title="Time builder", description=f"timestamp: {time_seconds}: <t:{time_seconds}:F>")
                    await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed,
                                                 components=[add_buttons, sub_buttons])
                elif key == "-w":
                    time_seconds -= 604800
                    embed = Embed(title="Time builder", description=f"timestamp: {time_seconds}: <t:{time_seconds}:F>")
                    await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed,
                                                 components=[add_buttons, sub_buttons])
                elif key == "-d":
                    time_seconds -= 86400
                    embed = Embed(title="Time builder", description=f"timestamp: {time_seconds}: <t:{time_seconds}:F>")
                    await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed,
                                                 components=[add_buttons, sub_buttons])
                elif key == "-h":
                    time_seconds -= 3600
                    embed = Embed(title="Time builder", description=f"timestamp: {time_seconds}: <t:{time_seconds}:F>")
                    await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed,
                                                 components=[add_buttons, sub_buttons])
                elif key == "-m":
                    time_seconds -= 1800
                    embed = Embed(title="Time builder", description=f"timestamp: {time_seconds}: <t:{time_seconds}:F>")
                    await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed,
                                                 components=[add_buttons, sub_buttons])
    except asyncio.TimeoutError:
        await ctx.edit_last_response("Waited for 15 seconds... Timeout.", embed=None, components=[])


@AdminPlugin.command()
@lightbulb.command("sensitive", "sensitive topics parent group", ephemeral=True)
@lightbulb.implements(SlashCommandGroup)
async def sensitive(ctx: SlashContext) -> None:
    """sensitive topics parent group"""
    await ctx.respond("Invoked sensitive")


@sensitive.child
@lightbulb.command("words", "sensitive topic words subgroup", ephemeral=True)
@lightbulb.implements(SlashSubGroup)
async def sensitive_words(ctx: SlashContext) -> None:
    """Sensitive topic words subgroup"""
    await ctx.respond("Invoked sensitive words")


@sensitive_words.child()
@lightbulb.option("word", "Word to add")
@lightbulb.add_checks(has_roles(832521484378308660, 832521484378308659, 832521484378308658, mode=any))
@lightbulb.command("add", "adds a word to the sensitive topics word list")
@lightbulb.implements(SlashSubCommand)
async def add(ctx: lightbulb.Context):
    """adds a word to the sensitive topics list"""
    with open('sensitive_settings.json', encoding='utf8') as json_dict:
        fulldict = json.load(json_dict)
    joinstring = ", "
    if ctx.options.word.lower() not in fulldict['words']:
        fulldict['words'].append(ctx.options.word.lower())
        with open('sensitive_settings.json', 'w', encoding='utf8') as json_dict:
            json.dump(fulldict, json_dict)
        await ctx.respond(embed=Embed(title="New list of words defined as sensitive",
                                      description=f"||{joinstring.join(fulldict['words'])}||", color="0x00ff00",
                                      timestamp=datetime.now(tz=timezone.utc)))
    else:
        await ctx.respond(embed=Embed(title="Word already in list of words defined as sensitive",
                                      description=f"||{joinstring.join(fulldict['words'])}||", color="0x0000ff",
                                      timestamp=datetime.now(tz=timezone.utc)))


@sensitive_words.child
@lightbulb.add_checks(has_roles(832521484378308660, 832521484378308659, 832521484378308658, mode=any))
@lightbulb.command("query", "querys the sensitive topics word list")
@lightbulb.implements(SlashSubCommand)
async def query(ctx: lightbulb.Context):
    """queries the sensitive topics list"""
    with open('sensitive_settings.json', encoding='utf8') as json_dict:
        fulldict = json.load(json_dict)
    joinstring = ", "
    await ctx.respond(
        embed=Embed(title="List of words defined as sensitive", description=f"||{joinstring.join(fulldict['words'])}||",
                    color="0x0000ff", timestamp=datetime.now(tz=timezone.utc)))


@sensitive_words.child
@lightbulb.option("word", "Word to remove")
@lightbulb.command("remove", "removes a word from the sensitive topics word list")
@lightbulb.implements(SlashSubCommand)
async def remove(ctx: lightbulb.Context):
    """removes a word from sensitive topics list"""
    with open('sensitive_settings.json', encoding='utf8') as file:
        fulldict = json.load(file)
    joinstring = ", "
    if ctx.options.word.lower() in fulldict['words']:
        for i, word in enumerate(fulldict['words']):
            if word == ctx.options.word.lower():
                fulldict['words'].pop(i)
                await ctx.respond(embed=Embed(title="New list of words defined as sensitive",
                                              description=f"||{joinstring.join(fulldict['words'])}||",
                                              color="0x00ff00",
                                              timestamp=datetime.now(tz=timezone.utc)))
                with open('sensitive_settings.json', 'w', encoding='utf8') as file:
                    json.dump(fulldict, file)
                break
    else:
        await ctx.respond(embed=Embed(title="Word not in list of words defined as sensitive",
                                      description=f"||{joinstring.join(fulldict['words'])}||", color="0x0000ff",
                                      timestamp=datetime.now(tz=timezone.utc)))


def load(bot):
    """Loads Plugin"""
    bot.add_plugin(AdminPlugin)


def unload(bot):
    """Unloads Plugin"""
    bot.remove_plugin(AdminPlugin)
