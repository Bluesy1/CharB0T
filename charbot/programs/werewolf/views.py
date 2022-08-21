# -*- coding: utf-8 -*-
#  ----------------------------------------------------------------------------
#  MIT License
#
# Copyright (c) 2022 Bluesy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#  ----------------------------------------------------------------------------
"""View to gather the members for a game."""
from typing import cast, TypedDict, final

import discord
import open_mafia_engine.api as mafia
from discord import ui

from .builder import build_werewolf, DiscordGame, DiscordActor
from ... import CBot, GuildComponentInteraction as Interaction


class GatherView(ui.View):
    """A view to gather all the members who are going to participate"""

    def __init__(self, initial_member: discord.Member):
        super().__init__(timeout=300)
        self.initial_member = initial_member
        self.members: list[discord.Member] = [initial_member]
        self.message: discord.Message = discord.utils.MISSING

    async def _start_game(self):
        """Helper method to start the next step"""
        view = ...
        embed = discord.Embed(
            title="Serial Killer",
            description="This is essentially a game of Werewolf/mafia. The roles are as follows:"
            "\nSerial Killer:"
            " You are the serial killer, equivalent to the mafia or wolf in the traditional versions.\n"
            "Snitch: You are able to find out who is the serial killer, equivalent to the seer in the"
            " traditional versions.\n"
            "Doctor: You are the doctor, able to protect one person including yourself every night.\n"
            "Cleaner: You are able to know the profession of the person killed last night, similar"
            " to the medium in the traditional versions.\n"
            "Everyone else is an inmate, equivalent to the villager in the traditional versions.\n",
        )
        thread = await self.message.channel.create_thread(
            name="A game of Serial killer", type=discord.ChannelType.public_thread
        )
        await thread.send(
            content=f"The game is about to begin after everyone checks their roles\n: "
            f"{', '.join(member.mention for member in self.members)}",
            embed=embed,
            view=view,
        )
        await self.message.delete()
        self.stop()

    @ui.button(label="Join", style=discord.ButtonStyle.green)
    async def join(self, interaction: Interaction[CBot], _: ui.Button):
        """Join the game"""
        self.message = interaction.message
        if interaction.user not in self.members:
            await interaction.response.defer(ephemeral=True)
            self.members.append(interaction.user)
            if len(self.members) >= 16:
                await interaction.edit_original_response(content="The game is about to begin", embeds=[], view=None)
                await self._start_game()
            else:
                embed = self.message.embeds[0]
                embed.set_field_at(0, name="Signed Up", value=", ".join(member.mention for member in self.members))
                await interaction.edit_original_response(embed=embed)
                await interaction.followup.send("You have joined the game.", ephemeral=True)
        else:
            await interaction.response.send_message("You are already signed up.", ephemeral=True)

    @ui.button(label="Leave", style=discord.ButtonStyle.red)
    async def leave(self, interaction: Interaction[CBot], _: ui.Button):
        """Leave the game"""
        self.message = interaction.message
        if interaction.user in self.members:
            await interaction.response.defer(ephemeral=True)
            self.members.remove(interaction.user)
            embed = self.message.embeds[0]
            embed.set_field_at(0, name="Signed Up", value=", ".join(member.mention for member in self.members))
            await interaction.edit_original_response(embed=embed)
            await interaction.followup.send("You have left the game.", ephemeral=True)
        else:
            await interaction.response.send_message("You are not signed up.", ephemeral=True)

    async def on_timeout(self) -> None:
        """Called when the view times out"""
        if len(self.members) >= 8:
            await self._start_game()
        else:
            await self.message.edit(
                content="Not enough players to start the game", embeds=[], view=None, delete_after=60
            )


class GetRole(ui.View):
    """View to get to tell each member their role, and construct the game instance

    Parameters
    ----------
    thread : discord.Thread
        The thread to send the messages to
    members : list[discord.Member]
        The members playing the game
    """

    def __init__(self, thread: discord.Thread, members: list[discord.Member]):
        super().__init__(timeout=300)
        self.members = members
        self.thread = thread
        self.message = discord.utils.MISSING
        self.game: DiscordGame = build_werewolf(members)
        self.roles = {actor.id: actor.role for actor in self.game.actors}
        self.checked: set[discord.Member] = set()

    @ui.button(label="See roles", style=discord.ButtonStyle.grey)
    async def see_roles(self, interaction: Interaction[CBot], _: ui.Button):
        """See the roles"""
        await interaction.response.defer(ephemeral=True)
        role = self.roles.get(interaction.user.id)
        if role is None:
            await interaction.followup.send("You are not in the game.", ephemeral=True)
        else:
            await interaction.followup.send(f"You are a {role}.", ephemeral=True)
            self.checked.add(interaction.user)
            if len(self.checked) == len(self.members):
                await interaction.followup.send("The game is about to begin")
                self.game.change_phase()


class DaySection(ui.View):
    """View to process the day actions for a game."""

    def __init__(self, game: DiscordGame, members: list[discord.Member], previous_kill: DiscordActor | None) -> None:
        super().__init__(timeout=300)
        self.game = game
        self.members = members
        self.prev_kill = previous_kill
        self.dead: set[DiscordActor] = {actor for actor in self.game.actors if actor.status["dead"]}
        dead = {actor.id for actor in self.dead}
        self.voted: set[discord.Member] = set()
        self.vote.options = [
            discord.SelectOption(label=member.display_name, value=f"{member.id}")
            for member in members
            if member.id not in dead
        ]

    async def interaction_check(self, interaction: Interaction[CBot]) -> bool:
        """Check if the interaction is valid for this view."""
        if interaction.message.author not in self.members:
            await interaction.response.send_message("You are not in this game.")
            return False
        if interaction.user.id in self.dead:
            await interaction.response.send_message("You are dead.")
            return False
        if interaction.user in self.voted:
            await interaction.response.send_message("You have already voted.")
            return False
        return True

    @ui.select(placeholder="Select a member to vote for.")
    async def vote(self, interaction: Interaction[CBot], select: ui.Select) -> None:
        """Vote for a member."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        self.voted.add(interaction.user)
        actor = next(filter(lambda a: a.id == interaction.user.id, self.game.actors))
        ability = next(filter(lambda a: a.name == "Vote", actor.abilities))
        target = next(filter(lambda a: a.id == int(select.values[0]), self.game.actors))
        self.game.process_event(mafia.EActivate(self.game, ability, target.name))
        await interaction.followup.send(f"You have voted for **{target.name}**.", ephemeral=True)
        if len(self.voted) == len(self.members):
            await interaction.followup.send("All members have voted, processing votes.")
            killed: mafia.LynchTally = self.game.aux[self.game.tally_key]
            leaders = cast(list[DiscordActor], killed.results.vote_leaders)
            self.game.change_phase()
            if len(leaders) == 1:
                await interaction.followup.send(f"{leaders[0].name} has been killed by a majority vote.")
                over = self.game.current_phase.name == "shutdown"
                if over:
                    if leaders[0].role == "Serial Killer":
                        await interaction.followup.send(
                            "The Serial Killer has been found and the inmates have won the game."
                        )
                        # TODO: add point processing
                    else:
                        serial = next(filter(lambda f: f.name == "Serial Killer", self.game.factions)).actors[0]
                        await interaction.followup.send(f"The serial killer had won the game, they were {serial.name}.")
                        # TODO: add point processing
                    self.stop()
                    await interaction.message.edit(view=None)
            else:
                await interaction.followup.send("No one has been killed, the town could not come to a majority vote.")
            self.stop()


@final
class NightEvents(TypedDict):
    targeted: DiscordActor | None
    protected: DiscordActor | None


class NightSection(ui.View):
    """View to process the night actions for a game."""

    def __init__(
        self, game: DiscordGame, members: list[discord.Member], last_night_killed: DiscordActor | None
    ) -> None:
        super().__init__(timeout=300)
        self.game = game
        self.members = members
        self.killed = last_night_killed
        self.dead: set[DiscordActor] = {actor for actor in self.game.actors if actor.status["dead"]}
        self.acts: set[int] = {
            actor.id for actor in self.game.actors if (not actor.status["dead"]) and actor.role != "Inmate"
        }
        self.acted: set[discord.Member] = set()
        self.events: NightEvents = {"targeted": None, "protected": None}

    async def interaction_check(self, interaction: Interaction[CBot]) -> bool:
        """Check if the interaction is valid for this view."""
        if interaction.message.author not in self.members:
            await interaction.response.send_message("You are not in this game.")
            return False
        if interaction.user.id in self.dead:
            await interaction.response.send_message("You are dead.")
            return False
        if interaction.user.id not in self.acts:
            await interaction.response.send_message("You have no night abilities.")
            return False
        return True

    @ui.select(placeholder="Select an action to take.")
    async def night_action(self, interaction: Interaction[CBot], select: ui.Select) -> None:
        """Take a night action."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        actor = next(filter(lambda a: a.id == interaction.user.id, self.game.actors))
        if actor.role == "Cleaner":
            if self.killed:
                await interaction.followup.send(f"Last night's victim was a(n): {self.killed.role}.", ephemeral=True)
            else:
                await interaction.followup.send("Last night's victim was nobody.", ephemeral=True)
            self.game.process_event(
                mafia.EActivate(self.game, next(filter(lambda a: a.name == "Placeholder", actor.abilities)))
            )
        else:
            targeted = next(filter(lambda a: a.id == int(select.values[0]), self.game.actors))
            if actor.role == "Serial Killer":
                await interaction.followup.send(f"You have targeted {targeted.name} tonight.", ephemeral=True)
                self.game.process_event(
                    mafia.EActivate(
                        self.game, next(filter(lambda a: a.name == "Kill", actor.abilities)), target=targeted.name
                    )
                )
                self.events["targeted"] = targeted
            elif actor.role == "Doctor":
                await interaction.followup.send(f"You have protected {targeted.name} tonight.", ephemeral=True)
                self.game.process_event(
                    mafia.EActivate(
                        self.game, next(filter(lambda a: a.name == "Heal", actor.abilities)), target=targeted.name
                    )
                )
                self.events["protected"] = targeted
            else:
                await interaction.followup.send(f"{targeted.name} is a(n) {targeted.role}.", ephemeral=True)
                self.game.process_event(
                    mafia.EActivate(self.game, next(filter(lambda a: a.name == "Placeholder", actor.abilities)))
                )
        self.acted.add(interaction.user)
        if len(self.acted) == len(self.acts):
            await interaction.followup.send("All night actions have been taken, processing actions.")
            await interaction.message.edit(view=None)
            self.game.change_phase()
            self.stop()
            targeted = cast(DiscordActor, self.events["targeted"])
            if targeted == self.events["protected"]:
                await interaction.followup.send(
                    f"The serial killer targeted {targeted.name}, but was healed by the doctor."
                )
                new_view = DaySection(self.game, self.members, None)
            else:
                await interaction.followup.send(f"The serial killer killed {targeted.name}.")
                over = self.game.current_phase.name == "shutdown"
                if over:
                    serial = next(filter(lambda f: f.name == "Serial Killer", self.game.factions)).actors[0]
                    await interaction.followup.send(f"The serial killer had won the game, they were {serial.name}.")
                    # TODO: add point processing
                    return
                new_view = DaySection(self.game, self.members, self.events["targeted"])
            embed = discord.Embed(
                title="Daytime",
                description="The day has begun, discuss and then vote. You have 5 minutes, or until everyone has voted,"
                " whichever comes first.",
            )
            await interaction.followup.send(embed=embed, view=new_view)
