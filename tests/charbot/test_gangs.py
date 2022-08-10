# -*- coding: utf-8 -*-
import discord
import pytest
from pytest_mock import MockerFixture

from charbot import CBot, gangs


class BaseMockAcquire:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entered = False

    def transaction(self):
        return self

    def acquire(self):
        return self

    async def __aenter__(self):
        self.entered = True
        return self

    async def __aexit__(self, *args):
        self.entered = False
        return True


@pytest.mark.asyncio
async def test_dues_button_paid(mocker: MockerFixture):
    """Test the dues button for an  already paid member."""

    class MockAcquire(BaseMockAcquire):
        async def fetchval(self, query, *args):
            if not self.entered:
                raise AssertionError("Not entered or past exit")
            return query == "SELECT paid FROM gang_members WHERE user_id = $1" and len(args) == 1

    interaction = mocker.AsyncMock(spec=discord.Interaction)
    interaction.client = mocker.AsyncMock(spec=CBot)
    interaction.client.pool = MockAcquire()
    interaction.response = mocker.AsyncMock(spec=discord.InteractionResponse)
    interaction.followup = mocker.AsyncMock(spec=discord.Webhook)
    button = gangs.DuesButton("White")
    await button.callback(interaction)
    interaction.response.defer.assert_awaited_once()
    assert interaction.response.defer.await_args.kwargs["ephemeral"] is True, "Ephemeral should be true"
    interaction.followup.send.assert_awaited_once_with("You have already paid your dues for this month.")
