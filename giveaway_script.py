CHANNEL = 1478092238281249002
LOG_CHANNEL = 687817008355737606
START_MESSAGE = 1478093405278965890

import random
import tomllib
import pathlib

import discord


class GiveawayBot(discord.Client):
    
    async def setup_hook(self) -> None:
        
        channel = await self.fetch_channel(CHANNEL)
        assert isinstance(channel, discord.TextChannel)
        log_channel = await self.fetch_channel(LOG_CHANNEL)
        assert isinstance(log_channel, discord.TextChannel)
        await channel.set_permissions(channel.guild.default_role, send_messages=False)
        await log_channel.send(f"Channel {channel.mention} locked... Beginning Draw...")
        
        messages = [
            message
            async for message in channel.history(after=discord.Object(id=START_MESSAGE))
            if not message.author.bot and not message.is_system() and message.author.id != 225344348903047168
        ]
        
        if not messages:
            await log_channel.send("No valid entries found. Ending draw.")
            await self._close_bot()
        
        # Remove duplicate entries based on user ID
        unique_entries: dict[int, discord.Message] = {}
        for message in messages:
            if message.author.id not in unique_entries:
                unique_entries[message.author.id] = message
        
        unique_messages = list(unique_entries.values())
        await log_channel.send(f"Found {len(unique_messages)} unique entries. Selecting winners...")
        
        random.shuffle(unique_messages)
        
        BASE_GIVEN = 0
        
        first = unique_messages.pop(0)
        second = unique_messages.pop(0)
        LOG_MESSAGE = f"Selected winners: {first.author} ({first.jump_url}) and {second.author} ({second.jump_url})."
        result = f"""\
The giveaway has concluded! The winners are {first.author.mention} and {second.author.mention}!
"""
        
        
        if "dlc" not in first.content.strip().casefold():
            BASE_GIVEN += 1
        
        if "dlc" not in second.content.strip().casefold():
            BASE_GIVEN += 1

        if BASE_GIVEN < 2:
            result += "However, since "
            if BASE_GIVEN == 0:
                result += "neither winner wanted the base game, "
                two_extra = True
            else:
                result += "one of the winners only wanted the DLC, "
                two_extra = False
            
            extra_winners: list[discord.Message] = []
            
            while BASE_GIVEN < 2:
                next_message = unique_messages.pop(0)
                LOG_MESSAGE += f"\n Checking {next_message.author} ({next_message.jump_url}) for base game eligibility..."
                if "dlc" not in next_message.content.strip().casefold():
                    BASE_GIVEN += 1
                    LOG_MESSAGE += " Eligible for base game."
                    extra_winners.append(next_message)
                else:
                    LOG_MESSAGE += " Not eligible for base game."
            
            if two_extra:
                third, fourth = extra_winners[:2]
                result += f"both {third.author.mention} and {fourth.author.mention} have been selected to win copies of the base game!"
                LOG_MESSAGE += f" Also selected {third.author} ({third.jump_url}) and {fourth.author} ({fourth.jump_url}) as the base game winners."
            else:
                third = extra_winners[0]
                result += f"{third.author.mention} has been selected to win a copy of the base game!"
                LOG_MESSAGE += f" Also selected {third.author} ({third.jump_url}) as the base game winner."
        
        result += """
Congratulations to the winners! Remember to DM Charlie within 48 hours to claim your key(s)!
"""
        backup_winners = unique_messages[:5]
        backup_winners_mentions = ", ".join(f"{winner.author.mention} ({winner.jump_url})" for winner in backup_winners)
        LOG_MESSAGE += f"\n Backup winners in order are: {backup_winners_mentions}."
        await channel.send(result)
        await log_channel.send(LOG_MESSAGE)
        await log_channel.send("<@363095569515806722> Remember to remove the cronjob.")
        await self._close_bot()
    
    
    async def _close_bot(self):
        await self.close()
        exit(0)


if __name__ == "__main__":
    
    CONFIG_FILE = pathlib.Path(__file__).parent / "config.toml"
    with CONFIG_FILE.open("rb") as f:
        CONFIG = tomllib.load(f)
    token = CONFIG["discord"]["token"]
    del CONFIG
    
    
    intents = discord.Intents.default()
    intents.message_content = True
    bot = GiveawayBot(intents=intents)
    bot.run(token)