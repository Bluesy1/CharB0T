import hikari
import lightbulb
from lightbulb import SlashCommandGroup, SlashSubCommand, SlashContext

from helper import MOD_SENSITIVE, MOD_GENERAL, EVERYONE_MODMAIL, user_perms, make_modmail_buttons, \
    blacklist_user, un_blacklist_user, get_blacklist

MODMAIL_PLUGIN = lightbulb.Plugin("Modmail_Plugin", include_datastore=True, default_enabled_guilds=[225345178955808768])
MODMAIL_PLUGIN.d.message_dict = {}


@MODMAIL_PLUGIN.listener(hikari.DMMessageCreateEvent)
async def on_dm(event: hikari.DMMessageCreateEvent):
    """Dm event handler"""
    if event.is_human:
        if event.content is not None:
            log = await event.app.rest.fetch_channel(906578081496584242)
            await log.send(event.content)
        modmail_buttons = make_modmail_buttons(MODMAIL_PLUGIN)
        message = await event.message.respond(
            "I noticed you've DMed me. If this was an attempt to speak to mods, choose the right category below,"
            " else ignore this:",
            components=modmail_buttons)
        MODMAIL_PLUGIN.d.message_dict.update({message.id: event.message.content})


@MODMAIL_PLUGIN.listener(hikari.InteractionCreateEvent)
async def button_press(event: hikari.InteractionCreateEvent):  # pylint: disable=too-many-branches
    """Modmail button press event handler"""
    if event.interaction.type in (hikari.InteractionType.MESSAGE_COMPONENT, 3):
        # noinspection PyTypeChecker
        interaction: hikari.ComponentInteraction = event.interaction
        if "Sensitive" in interaction.custom_id:
            if interaction.custom_id in ["Emergency_Sensitive", "Important_Sensitive",
                                         "Question_Sensitive", "Other_Sensitive"]:
                if "Emergency" in interaction.custom_id:
                    channel_header = "EMERGENCY"
                elif "Important" in interaction.custom_id:
                    channel_header = "IMPORTANT"
                elif "Question" in interaction.custom_id:
                    channel_header = "QUESTION"
                else:
                    channel_header = "OTHER"
                channel = await event.app.rest.create_guild_text_channel(
                    225345178955808768,
                    f"[{channel_header}]-{interaction.user.username}",
                    category=942578610336837632,
                    permission_overwrites=[MOD_SENSITIVE, EVERYONE_MODMAIL, user_perms(interaction.user.id)]
                )
                if interaction.custom_id == "Emergency_Sensitive":
                    await channel.edit_overwrite(
                        363095569515806722,
                        target_type=hikari.PermissionOverwriteType.MEMBER,
                        allow=(hikari.Permissions.VIEW_CHANNEL | hikari.Permissions.SEND_MESSAGES)
                    )
                await interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_CREATE,
                    f"Channel created: <#{channel.id}>",
                    flags=hikari.MessageFlag.EPHEMERAL)
                if interaction.guild_id is not None:
                    try:
                        await channel.send(
                            f"This was prompted from DMs. The starting message from <@{interaction.user.id}> :\n"
                            f"{MODMAIL_PLUGIN.d.message_dict[interaction.message.id]}")
                        del MODMAIL_PLUGIN.d.message_dict[interaction.message.id]
                    finally:
                        await interaction.edit_message(interaction.message.id, "Understood.", components=[])
                else:
                    await channel.send(f"<@{interaction.user.id}> please send your query/message here.")
        elif "General" in event.interaction.custom_id:
            if interaction.custom_id in ["Emergency_General", "Important_General",
                                         "Question_General", "Other_General"]:
                if "Emergency" in interaction.custom_id:
                    channel_header = "EMERGENCY"
                elif "Important" in interaction.custom_id:
                    channel_header = "IMPORTANT"
                elif "Question" in interaction.custom_id:
                    channel_header = "QUESTION"
                else:
                    channel_header = "OTHER"
                channel = await event.app.rest.create_guild_text_channel(
                    225345178955808768,
                    f"[{channel_header}]-{interaction.user.username}",
                    category=942578610336837632,
                    permission_overwrites=[MOD_GENERAL, EVERYONE_MODMAIL, user_perms(interaction.user.id)]
                )
                await interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_CREATE,
                    f"Channel created: <#{channel.id}>",
                    flags=hikari.MessageFlag.EPHEMERAL)
                if interaction.guild_id is not None:
                    try:
                        await channel.send(
                            f"This was prompted from DMs. The starting message from <@{interaction.user.id}> :\n"
                            f"{MODMAIL_PLUGIN.d.message_dict[interaction.message.id]}")
                        del MODMAIL_PLUGIN.d.message_dict[interaction.message.id]
                    finally:
                        await interaction.edit_message(interaction.message.id, "Understood.", components=[])
                else:
                    await channel.send(f"<@{interaction.user.id}> please send your query/message here.")


@MODMAIL_PLUGIN.command()
@lightbulb.add_checks(lightbulb.has_roles(225413350874546176, 253752685357039617,
                                          725377514414932030, 338173415527677954, mode=any))
@lightbulb.command("modmail", "modmail command group", auto_defer=True, ephemeral=True, hidden=True)
@lightbulb.implements(SlashCommandGroup)
async def modmail(ctx: SlashContext) -> None:
    """Modmail Command Group"""
    await ctx.respond("Invoked Modmail Group")


@modmail.child
@lightbulb.option("user", "user to change", type=hikari.User, required=True)
@lightbulb.option("add", "True to add to blacklist, False to remove", type=bool, required=True)
@lightbulb.command("edit_blacklist", "modmail command group", auto_defer=True,
                   ephemeral=True, hidden=True, inherit_checks=True)
@lightbulb.implements(SlashSubCommand)
async def modmail_edit_blacklist(ctx: SlashContext) -> None:
    """Modmail edit blacklist command"""
    successful = False
    if ctx.options.add:
        successful = blacklist_user(ctx.options.user.id)
    else:
        successful = un_blacklist_user(ctx.options.user.id)
    if ctx.options.add and successful:
        await ctx.respond(f"<@{ctx.options.user.id}> successfully added to the blacklist")
    elif ctx.options.add and not successful:
        await ctx.respond(
            f"Error: <@{ctx.options.user.id}> was already on the blacklist or was not able to be added to.")
    elif not ctx.options.add and successful:
        await ctx.respond(f"<@{ctx.options.user.id}> successfully removed from the blacklist")
    elif not ctx.options.add and not successful:
        await ctx.respond(f"<@{ctx.options.user.id}> was not on the blacklist or was not able to be removed from it.")
    else:
        await ctx.respond(
            "Error: unkown issue occured. If you're seeing this, ping bluesy, something has gone very wrong.")


@modmail.child
@lightbulb.command("query_blacklist", "modmail command group", auto_defer=True,
                   ephemeral=True, hidden=True, inherit_checks=True)
@lightbulb.implements(SlashSubCommand)
async def modmail_query_blacklist(ctx: SlashContext) -> None:
    """Modmail blacklist query command"""
    blacklisted = [f"<@{item}>" for item in get_blacklist()]
    await ctx.respond(embed=hikari.Embed(title="Blacklisted users", description="\n".join(blacklisted)))


def load(bot):
    """Loads the plugin"""
    bot.add_plugin(MODMAIL_PLUGIN)


def unload(bot):
    """Unloads the plugin"""
    bot.remove_plugin(MODMAIL_PLUGIN)
