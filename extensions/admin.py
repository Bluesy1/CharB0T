import asyncio
import os
import time

import lightbulb
from hikari.embeds import Embed
from hikari.events.interaction_events import InteractionCreateEvent
from hikari.interactions.base_interactions import ResponseType
from hikari.messages import ButtonStyle
from lightbulb import commands
from lightbulb.checks import has_roles


def check_publisher(context):
    return context.author.id in [363095569515806722, 225344348903047168, 146285543146127361]


AdminPlugin = lightbulb.Plugin("AdminPlugin")
AdminPlugin.add_checks(lightbulb.Check(has_roles(338173415527677954, 253752685357039617, 225413350874546176, mode=any)))


@AdminPlugin.command
@lightbulb.command(
    "maketime", "makes a unix time constructor for use with discord's unix time feature",
    guilds=[225345178955808768])
@lightbulb.implements(commands.SlashCommand)
async def command(ctx):
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
        "UsUse this to decrease the time by 1 hout=r").add_to_menu()
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
    ts = round(time.time())
    ts -= ts % 1800
    embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
    await ctx.respond("Use the select menu to adjust the time", embed=embed, components=[add_buttons, sub_buttons])
    try:
        async with AdminPlugin.bot.stream(InteractionCreateEvent, timeout=15).filter(
                ('interaction.user.id', ctx.author.id)) as stream:
            async for event in stream:
                await event.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_UPDATE)
                key = event.interaction.custom_id
                if key == "Done":
                    embed = (Embed(title="Final times", description=f"timestamp: {ts}: <t:{ts}:F>")
                             .add_field(f"Default: `<t:{ts}>`", f"<t:{ts}>")
                             .add_field(f"Short Time: `<t:{ts}:t>`", f"<t:{ts}:t>")
                             .add_field(f"Long Time: `<t:{ts}:T>`", f"<t:{ts}:t>")
                             .add_field(f"Short Date: `<t:{ts}:d>`", f"<t:{ts}:d>")
                             .add_field(f"Long Date: `<t:{ts}:D>`", f"<t:{ts}:D>")
                             .add_field(f"Short Date/Time: `<t:{ts}:f>`", f"<t:{ts}:f>")
                             .add_field(f"Long Date/Time: `<t:{ts}:F>`", f"<t:{ts}:F>")
                             .add_field(f"Relative Time: `<t:{ts}:R>`", f"<t:{ts}:R>")
                             )
                    await ctx.edit_last_response(f"<t:{ts}", embed=embed, components=[])
                    return
                elif key == "+w":
                    ts += 604800
                    embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
                    await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed,
                                                 components=[add_buttons, sub_buttons])
                elif key == "+d":
                    ts += 86400
                    embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
                    await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed,
                                                 components=[add_buttons, sub_buttons])
                elif key == "+h":
                    ts += 3600
                    embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
                    await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed,
                                                 components=[add_buttons, sub_buttons])
                elif key == "+m":
                    ts += 1800
                    embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
                    await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed,
                                                 components=[add_buttons, sub_buttons])
                elif key == "-w":
                    ts -= 604800
                    embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
                    await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed,
                                                 components=[add_buttons, sub_buttons])
                elif key == "-d":
                    ts -= 86400
                    embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
                    await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed,
                                                 components=[add_buttons, sub_buttons])
                elif key == "-h":
                    ts -= 3600
                    embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
                    await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed,
                                                 components=[add_buttons, sub_buttons])
                elif key == "-m":
                    ts -= 1800
                    embed = Embed(title="Time builder", description=f"timestamp: {ts}: <t:{ts}:F>")
                    await ctx.edit_last_response("Use the select menu to adjust the time", embed=embed,
                                                 components=[add_buttons, sub_buttons])
    except asyncio.TimeoutError:
        await ctx.edit_last_response("Waited for 15 seconds... Timeout.", embed=None, components=[])


def load(bot): bot.add_plugin(AdminPlugin)


def unload(bot): bot.remove_plugin(AdminPlugin)
