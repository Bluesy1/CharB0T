from hikari.embeds import Embed
from hikari.undefined import UNDEFINED
import lightbulb

def strip_class(arg:str):
    if arg is str :return "str"
    if arg is int :return "int"
    if arg is float:return "float"
    if arg is bool:return "boolean"
    return arg

def list_to_string(arg: list):
    arg = [str(x) for x in arg]
    tempstr = ", "
    return tempstr.join(arg)

def option_help(option: lightbulb.commands.base.OptionLike) -> str:
    vartype = strip_class(option.arg_type)
    output = f" Arg type: {vartype}"
    if option.choices is not None:
        output += ", Choices: "
        output += list_to_string(option.choices)
    if option.default is not UNDEFINED:
        output += ", Default: "
        output += option.default
    if option.required: output+=", Is required"
    if option.channel_types is not None:
        output += ", Channel Types: "
        output += list_to_string(option.channel_types)
    return output

class CustomHelp(lightbulb.BaseHelpCommand):
    async def send_bot_help(self, context):
        # Override this method to change the message sent when the help command
        # is run without any arguments.
        await context.respond(f"{self.app.slash_commands}")


    async def send_plugin_help(self, context, plugin):
        # Override this method to change the message sent when the help command
        # argument is the name of a plugin.
        embed = Embed(title=f"Commands in plugin {plugin.name}")
        for command in plugin.all_commands:
            if command is lightbulb.commands.SlashCommand or command is lightbulb.commands.SlashSubCommand:
                embed.add_field(command.name,command.options,inline=True)
            elif command is lightbulb.commands.SlashCommandGroup:
                for subcommand in command.subcommands:
                    if subcommand is lightbulb.commands.SlashSubCommand:
                        embed.add_field(subcommand.name,subcommand.options,inline=True)
                    else:
                        for subsubcommand in subcommand.subcommands:
                            embed.add_field(subsubcommand.name,subsubcommand.options,inline=True)
        await context.respond(embed=embed)

    async def send_command_help(self, context, command):
        # Override this method to change the message sent when the help command
        # argument is the name or alias of a command.
        embed = Embed(title=f"Commands in plugin {command.name}")
        embed.add_field("Options",command.options, inline=True)
        await context.respond(embed=embed)

    async def send_group_help(self, context, group):
        # Override this method to change the message sent when the help command
        # argument is the name or alias of a command group.
        embed = Embed(title=f"Commands in group {group.name}",description=group.subcommands)
        for command in group.subcommands:
            command=group.subcommands[command]
            embed.add_field("test",command)
            try:
                for subcommand in command.subcommands:
                    subcommand=command.subcommands[command]
                    embed.add_field(subcommand.name,subcommand.description)
                    for option in subcommand.options:
                        option = subcommand.options[option]
                        embed.add_field(f"Option {option.name}",option_help(option))
            except:
                embed.add_field(command.name,command.description,)
                for option in command.options:
                    option = command.options[option]
                    embed.add_field(f"Option {option.name}",option_help(option))
        await context.respond(embed=embed)

    """async def object_not_found(self, context, obj):
        # Override this method to change the message sent when help is
        # requested for an object that does not exist
        ..."""

def load(bot):
    bot.d.old_help_command = bot.help_command
    bot.help_command = CustomHelp(bot)

def unload(bot):
    bot.help_command = bot.d.old_help_command
    del bot.d.old_help_command