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
import discord
import open_mafia_engine.api as mafia


class DiscordActor(mafia.Actor):
    def __init__(self, game: mafia.Game, member: discord.Member, role: str = "Inmate") -> None:
        super().__init__(game, member.display_name)
        self.member = member
        self.role = role
        self.id = member.id


class DiscordGame(mafia.Game):
    actors: list[DiscordActor]
    tally_key: str


Placeholder = mafia.Ability.generate(lambda: [], [], "Placeholder", "Fill a gap", "Placeholder")


@mafia.game_builder("Werewolf")
def build_werewolf(players: list[discord.Member]) -> DiscordGame:
    """Builds a Werewolf game.

    Parameters
    ----------
    players : list[discord.Member]
        A shuffled list of the players in the game.

    Returns
    -------
    DiscordGame
        The game object.
    """
    game = DiscordGame()
    mafia.GameEnder(game)
    tally = mafia.LynchTally(game)
    game.tally_key = tally.key
    town = mafia.Faction(game, "Town")
    mafia.OCLastFactionStanding(game, town)
    serial_killer = mafia.Faction(game, "Serial Killer")
    mafia.OCLastFactionStanding(game, serial_killer)
    # --------------------------------------------------------------
    # Add the Serial Killer
    # --------------------------------------------------------------
    killer_member = players.pop(0)
    killer = DiscordActor(game, killer_member, "Serial Killer")
    serial_killer.add_actor(killer)
    killer_vote = mafia.VoteAbility(game, killer, name="Vote", tally=tally)
    mafia.PhaseConstraint(game, killer_vote, phase=mafia.get_phase_by_name(game, "day"))
    kill_ability = mafia.KillAbility(game, killer, name="Kill", desc="Kills the target. 1 use per night.")
    mafia.LimitPerPhaseActorConstraint(game, kill_ability, 1)
    mafia.PhaseConstraint(game, kill_ability, phase=mafia.get_phase_by_name(game, "night"))
    mafia.ConstraintNoSelfFactionTarget(game, kill_ability)
    # --------------------------------------------------------------
    # Add a Snitch
    # --------------------------------------------------------------
    snitch_member = players.pop(0)
    snitch = DiscordActor(game, snitch_member, "Snitch")
    town.add_actor(snitch)
    snitch_vote = mafia.VoteAbility(game, snitch, name="Vote", tally=tally)
    mafia.PhaseConstraint(game, snitch_vote, phase=mafia.get_phase_by_name(game, "day"))
    placeholder = Placeholder(game, snitch, name="Placeholder", desc="Placeholder")
    mafia.PhaseConstraint(game, placeholder, phase=mafia.get_phase_by_name(game, "night"))
    # --------------------------------------------------------------
    # Add the Doctor
    # --------------------------------------------------------------
    doctor_member = players.pop(0)
    doctor = DiscordActor(game, doctor_member, "Doctor")
    town.add_actor(doctor)
    doctor_vote = mafia.VoteAbility(game, doctor, name="Vote", tally=tally)
    mafia.PhaseConstraint(game, doctor_vote, phase=mafia.get_phase_by_name(game, "day"))
    doctor_ability = mafia.ProtectFromKillAbility(
        game, doctor, name="Protect", desc="Protects the target. 1 use per night."
    )
    mafia.LimitPerPhaseActorConstraint(game, doctor_ability, 1)
    mafia.PhaseConstraint(game, doctor_ability, phase=mafia.get_phase_by_name(game, "night"))
    # --------------------------------------------------------------
    # Add the Cleaner
    # --------------------------------------------------------------
    cleaner_member = players.pop(0)
    cleaner = DiscordActor(game, cleaner_member, "Cleaner")
    town.add_actor(cleaner)
    cleaner_vote = mafia.VoteAbility(game, cleaner, name="Vote", tally=tally)
    mafia.PhaseConstraint(game, cleaner_vote, phase=mafia.get_phase_by_name(game, "day"))
    placeholder = Placeholder(game, cleaner, name="Placeholder", desc="Placeholder")
    mafia.LimitPerPhaseActorConstraint(game, placeholder, 1)
    # --------------------------------------------------------------
    # Add the townspeople
    # --------------------------------------------------------------
    for remaining_player in players:
        actor = DiscordActor(game, remaining_player)
        town.add_actor(actor)
        vote = mafia.VoteAbility(game, actor, name="Vote", tally=tally)
        mafia.PhaseConstraint(game, vote, phase=mafia.get_phase_by_name(game, "day"))
    return game
