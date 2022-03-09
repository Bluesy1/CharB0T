import lightbulb
from lightbulb import commands
from lightbulb.checks import has_roles

from roller import roll

dice_plugin = lightbulb.Plugin("DicePlugin", include_datastore=True)
dice_plugin.d.roll_error = (
    "Error invalid argument: specified dice can only be d2s, "
    "d4s, d6s, d8s, d10s, d12s, d20s, or d100s, or if a constant modifier must be a perfect "
    "integer, positive or negative, connexted with `+`, and no spaces. "
)


@dice_plugin.command
@lightbulb.add_checks(
    lightbulb.Check(
        has_roles(
            338173415527677954,
            253752685357039617,
            225413350874546176,
            914969502037467176,
            mode=any,
        )
    )
)
@lightbulb.command("roll", "roll group", guilds=[225345178955808768])
@lightbulb.implements(commands.SlashCommandGroup)
async def roll_group(ctx) -> None:
    """Roll Group"""
    await ctx.respond("invoked roll")


@roll_group.child
@lightbulb.option(
    "dice",
    "Dice to roll, accepts d2s, d4s, d6s, d8s, d10s, d12s, d20s, and d100s.",
    required=True,
)
@lightbulb.command(
    "standard",
    "D&D Standard Array 7 Dice roller, plus coin flips",
    inherit_checks=True,
    guilds=[225345178955808768],
)
@lightbulb.implements(commands.SlashSubCommand)
async def roll_comm(ctx: lightbulb.Context):  # pylint: disable=unused-variable
    """Dice roller"""
    await roll(ctx)


def load(bot):
    """Loads Plugin"""
    bot.add_plugin(dice_plugin)


def unload(bot):
    """Unloads Plugin"""
    bot.remove_plugin(dice_plugin)
