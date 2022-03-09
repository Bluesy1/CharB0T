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
                tungsten.Button("A", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("B", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("C", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("D", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("E", hikari.ButtonStyle.PRIMARY),
            ],
            [
                tungsten.Button("F", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("G", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("H", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("I", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("J", hikari.ButtonStyle.PRIMARY),
            ],
            [
                tungsten.Button("K", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("L", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("M", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("N", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("O", hikari.ButtonStyle.PRIMARY),
            ],
            [
                tungsten.Button("P", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("Q", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("R", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("S", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("T", hikari.ButtonStyle.PRIMARY),
            ],
            [
                tungsten.Button("U", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("V", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("W", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("X", hikari.ButtonStyle.PRIMARY),
                tungsten.Button("Y", hikari.ButtonStyle.PRIMARY),
            ],
        ]
        kwargs["button_group"] = tungsten.ButtonGroup(button_rows)
        try:
            if args[0].author.id not in kwargs["allowed_ids"]:
                kwargs["allowed_ids"].append(args[0].author.id)
        except KeyError:
            kwargs["allowed_ids"] = [args[0].author.id]
        # Actually creates object
        super().__init__(*args, **kwargs)

    async def button_callback(
        self,
        button: tungsten.Button,  # pylint: disable=unused-argument
        x: int,
        y: int,
        interaction: hikari.ComponentInteraction,  # pylint: disable=invalid-name,unused-argument
    ) -> None:
        """Callback for when a button has been pressed"""
        if interaction.message.content == "Click a button!":
            await self.edit_msg(
                f"Order that buttons have been clicked in is: ({button.label})",
                components=self.build(),
            )
        else:
            await self.edit_msg(
                f"{interaction.message.content}, ({button.label})",
                components=self.build(),
            )

    async def timeout_callback(self) -> None:
        """Callback on timeouts"""
        await self.edit_msg(
            f"{self.message.content}. ***The interactions have expired.***",
            components=[],
        )


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
