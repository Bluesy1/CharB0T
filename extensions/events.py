import datetime
import re
import traceback

import hikari
import lightbulb
from hikari import Embed

EVENTS = lightbulb.Plugin("EVENTS")


@EVENTS.listener(hikari.GuildMessageCreateEvent)
async def on_guild_message(event: hikari.GuildMessageCreateEvent) -> None:
    """Guild Message Create Handler ***DO NOT CALL MANUALLY***"""
    if event.content is not None and event.is_human:
        if not any(role in event.member.role_ids for role in
                   [338173415527677954, 253752685357039617, 225413350874546176, 387037912782471179, 406690402956083210,
                    729368484211064944]):  # pylint: disable=using-constant-test, line-too-long
            if f"<@&{event.guild_id}>" in event.content or "@everyone" in event.content or "@here" in event.content:
                await event.message.member.add_role(676250179929636886)
                await event.message.member.add_role(684936661745795088)
                await event.message.delete()
                channel = await EVENTS.app.rest.fetch_channel(426016300439961601)
                embed = (Embed(description=event.content, title="Mute: Everyone/Here Ping sent by non mod",
                               color="0xff0000")
                         .set_footer(text=f"Sent by {event.message.member.display_name}-{event.message.member.id}",
                                     icon=event.message.member.avatar_url))
                await channel.send(embed=embed)
        if event.is_bot or not event.content:
            return
        if False and re.search(r"bruh", event.content, re.IGNORECASE):  # pylint: disable=condition-evals-to-constant
            await event.message.delete()
        elif (re.search(r"~~:.|:;~~", event.content, re.MULTILINE | re.IGNORECASE)
              or re.search(r"tilde tilde colon dot vertical bar colon semicolon tilde tilde",
                           event.content, re.MULTILINE | re.IGNORECASE)):
            await event.message.delete()


# noinspection PyBroadException
@EVENTS.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    """Error Handler ***DO NOT CALL MANUALLY***"""
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(
            f"Something went wrong while running command `{event.context.command.name}`."
            f"Bluesy#8150 has been notified.", flags=64)
        bluesy = await event.app.rest.fetch_user(363095569515806722)
        try:
            raise event.exception
        except:  # pylint: disable=bare-except
            embed = (Embed(
                title=f"Invocation Error in command {event.context.command.name}",
                timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
                description=f"```{traceback.format_exc()}```"))
            await bluesy.send(embed=embed)
            traceback.print_exc()
    exception = event.exception.__cause__ or event.exception  # Unwrap the exception to get the original cause
    if isinstance(exception, lightbulb.NotOwner):
        await event.context.respond("You are not the owner of this bot.", flags=64)
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(f"This command is on cooldown. Retry in `{exception.retry_after:.2f}` seconds.",
                                    flags=64)  # pylint: disable=line-too-long
    elif isinstance(exception, lightbulb.CheckFailure):
        if any(substring in str(exception) for substring in
               ["check_author_is_me", "punished", "check_author_work_allowed",
                "check_author_is_admin", "check_author_is_mod"]):
            await event.context.respond("You are not authorized to use this command", flags=64)
    elif isinstance(exception, lightbulb.MissingRequiredRole):
        await event.context.respond("You are not authorized to use this command", flags=64)
    elif isinstance(exception, lightbulb.CommandNotFound):
        return
    else:
        await event.context.respond(str(exception), flags=64)
        bluesy = await event.app.rest.fetch_user(363095569515806722)
        try:
            raise exception
        except:  # pylint: disable=bare-except
            embed = (Embed(
                title=f"Error in command {event.context.command.name}",
                timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
                description=f"```{traceback.format_exc()}```"))
            await bluesy.send(embed=embed)
            traceback.print_exc()


def load(bot):
    """Loads Plugin"""
    bot.add_plugin(EVENTS)


def unload(bot):
    """Unloads Plugin"""
    bot.remove_plugin(EVENTS)
