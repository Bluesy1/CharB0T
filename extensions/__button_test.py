import hikari
import lightbulb
from lightbulb import commands
from lightbulb.ext import tungsten


@lightbulb.Check
def punished(context):
    """Checks if command user is punished"""
    roles = context.member.role_ids
    for role in roles:
        if role in [684936661745795088, 676250179929636886]:
            return False
    return True


button_plugin = lightbulb.Plugin("Buttons", include_datastore=True)
button_plugin.d.open_callbacks = {}


class ButtonTestOne(tungsten.Components):
    """Test Button Class"""

    def __init__(self, *args, **kwargs):
        """Creates a Button group object"""

        button_rows = [
            [
                tungsten.Button("0,0", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("1,0", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("2,0", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("3,0", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("4,0", hikari.ButtonStyle.PRIMARY)
            ], [
                tungsten.Button("0,1", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("1,1", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("2,1", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("3,1", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("4,1", hikari.ButtonStyle.PRIMARY)
            ], [
                tungsten.Button("0,2", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("1,2", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("2,2", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("3,2", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("4,2", hikari.ButtonStyle.PRIMARY)
            ], [
                tungsten.Button("0,3", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("1,3", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("2,3", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("3,3", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("4,3", hikari.ButtonStyle.PRIMARY)
            ], [
                tungsten.Button("0,4", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("1,4", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("2,4", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("3,4", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("4,4", hikari.ButtonStyle.PRIMARY)
            ]
        ]
        kwargs["button_group"] = tungsten.ButtonGroup(button_rows)
        # Actually creates object
        super().__init__(*args, **kwargs)

    async def button_callback(
            self, button: tungsten.Button,  # pylint: disable=unused-argument
            x: int, y: int, interaction: hikari.ComponentInteraction  # pylint: disable=invalid-name
    ) -> None:
        """Callback for when a button has been pressed"""
        if interaction.message.content == "Click a button!":
            await self.edit_msg(f"Order that buttons have been clicked in is: ({x},{y})", components=self.build())
        else:
            await self.edit_msg(f"{interaction.message.content}, ({x},{y})", components=self.build())

    async def timeout_callback(self) -> None:
        """Callback on timeouts"""
        await self.edit_msg(f"{self.message.content}. ***The interactions have expired.***", components=[])


@button_plugin.command
@lightbulb.add_checks(punished)
@lightbulb.command("buttons", "button test command")
@lightbulb.implements(commands.PrefixCommand)
async def button_test_one(ctx: lightbulb.Context) -> None:
    """Test command"""
    buttons = ButtonTestOne(ctx)
    response = await ctx.respond("Click a button!", components=buttons.build())
    await buttons.run(response)


def load(bot):
    """Loads the plugin"""
    bot.add_plugin(button_plugin)


def unload(bot):
    """Unloads the plugin"""
    bot.remove_plugin(button_plugin)
