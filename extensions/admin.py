# coding=utf-8
import json
from datetime import datetime, timezone

import lightbulb
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Cog, Context
from hikari.embeds import Embed
from lightbulb import SlashCommandGroup, SlashSubGroup, SlashContext, SlashSubCommand
from lightbulb.checks import has_roles

AdminPlugin = lightbulb.Plugin("AdminPlugin", default_enabled_guilds=[225345178955808768])
AdminPlugin.add_checks(has_roles(338173415527677954, 253752685357039617, 225413350874546176, mode=any))


class Admin(Cog):

    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx: Context) -> bool:
        return any(role.id in (338173415527677954, 253752685357039617, 225413350874546176) for role in ctx.author.roles)


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
@lightbulb.command("add", "adds a word to the sensitive topics word list")
@lightbulb.implements(SlashSubCommand)
async def add(ctx: lightbulb.Context):
    """adds a word to the sensitive topics list"""
    with open('sensitive_settings.json', encoding='utf8') as json_dict:
        fulldict = json.load(json_dict)
    if ctx.options.word.lower() not in fulldict['words']:
        fulldict['words'].append(ctx.options.word.lower())
        with open('sensitive_settings.json', 'w', encoding='utf8') as json_dict:
            json.dump(fulldict, json_dict)
        await ctx.respond(embed=Embed(title="New list of words defined as sensitive",
                                      description=", ".join(fulldict['words']), color="0x00ff00",
                                      timestamp=datetime.now(tz=timezone.utc)))
    else:
        await ctx.respond(embed=Embed(title="Word already in list of words defined as sensitive",
                                      description=", ".join(fulldict['words']), color="0x0000ff",
                                      timestamp=datetime.now(tz=timezone.utc)))


@sensitive_words.child
@lightbulb.command("query", "querys the sensitive topics word list")
@lightbulb.implements(SlashSubCommand)
async def query(ctx: lightbulb.SlashContext):
    """queries the sensitive topics list"""
    with open('sensitive_settings.json', encoding='utf8') as json_dict:
        fulldict = json.load(json_dict)
    await ctx.respond(
        embed=Embed(title="List of words defined as sensitive", description=", ".join(fulldict['words']),
                    color="0x0000ff", timestamp=datetime.now(tz=timezone.utc)))


@sensitive_words.child
@lightbulb.option("word", "Word to remove")
@lightbulb.command("remove", "removes a word from the sensitive topics word list")
@lightbulb.implements(SlashSubCommand)
async def remove(ctx: lightbulb.Context):
    """removes a word from sensitive topics list"""
    with open('sensitive_settings.json', encoding='utf8') as file:
        fulldict = json.load(file)
    if ctx.options.word.lower() in fulldict['words']:
        for i, word in enumerate(fulldict['words']):
            if word == ctx.options.word.lower():
                fulldict['words'].pop(i)
                await ctx.respond(embed=Embed(title="New list of words defined as sensitive",
                                              description=", ".join(fulldict['words']),
                                              color="0x00ff00",
                                              timestamp=datetime.now(tz=timezone.utc)))
                with open('sensitive_settings.json', 'w', encoding='utf8') as file:
                    json.dump(fulldict, file)
                break
    else:
        await ctx.respond(embed=Embed(title="Word not in list of words defined as sensitive",
                                      description=", ".join(fulldict['words']), color="0x0000ff",
                                      timestamp=datetime.now(tz=timezone.utc)))


def setup(bot: commands.Bot):
    """Loads Plugin"""
    bot.add_cog(Admin(bot))
