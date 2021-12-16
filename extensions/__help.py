import lightbulb



class CustomHelp(lightbulb.BaseHelpCommand):
    async def send_bot_help(self, context):
        # Override this method to change the message sent when the help command
        # is run without any arguments.
        await context.respond(f"{self.app.slash_commands}")


    async def send_plugin_help(self, context, plugin):
        # Override this method to change the message sent when the help command
        # argument is the name of a plugin.
        await context.respond(f"{plugin.all_commands}")

    async def send_command_help(self, context, command):
        # Override this method to change the message sent when the help command
        # argument is the name or alias of a command.
        await context.respond(f"{command.options}")

    async def send_group_help(self, context, group):
        # Override this method to change the message sent when the help command
        # argument is the name or alias of a command group.
        await context.respond(f"{group.subcommands}")

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