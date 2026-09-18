"""Bot Extension for tracking playlists."""

import datetime
import logging

import aiohttp
import discord
import orjson
import yarl
from discord.ext import commands

from . import CBot, Config
from .types.youtube import Error
from .types.youtube.playlists import Playlist, YoutubeV3ListPlaylistsResponse


logger = logging.getLogger("charbot.playlists")

GAMES_FORUM_ID = 1019647326601609338
GAME_SUGGESTIONS_TAG = 1019691620741959730


class YoutubeError(Exception):
    """Base class for Youtube API errors."""

    def __init__(self, code: int, message: str, error: Error) -> None:
        self.code = code
        self.message = message
        self.error = error
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class Playlists(commands.Cog):
    """Playlists Cog for CharBot."""

    url = yarl.URL("https://youtube.googleapis.com/youtube/v3/playlists")

    def __init__(self, bot: CBot) -> None:
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self._cache: dict[str, Playlist] = bot.holder.get("yt_playlists_cache", {})
        self._last_request_time = bot.holder.get(
            "yt_playlists_last_request", discord.utils.utcnow() - datetime.timedelta(hours=24)
        )

    async def cog_unload(self) -> None:
        """Clean up the Playlists Cog, save instance properties."""
        self.bot.holder["yt_playlists_cache"] = self._cache
        self.bot.holder["yt_playlists_last_request"] = self._last_request_time

    async def _request_page(self, page_token: str | None = None) -> YoutubeV3ListPlaylistsResponse:
        """Request a page of playlists from the Youtube Data Api V3.

        Parameters
        ----------
        page_token : str, optional
            The page token for the page to request if not the first page, by default None

        Returns
        -------
        YoutubeV3ListPlaylistsResponse
            The response from the Youtube Data Api V3

        Raises
        ------
        YoutubeError
            If the request fails
        """
        config = Config["youtube"]
        params: dict[str, str] = config["params"]
        params["part"] = "snippet"
        if page_token is not None:
            params["pageToken"] = page_token
        req_url = self.url.with_query(params)
        async with self.session.get(req_url, headers=config["headers"]) as resp:
            if resp.status == 200:
                data: YoutubeV3ListPlaylistsResponse = await resp.json(loads=orjson.loads)
                return data
            else:
                error: Error = await resp.json(loads=orjson.loads)
                raise YoutubeError(resp.status, error["message"], error)

    async def fetch_playlists(self) -> list[Playlist]:
        """Get all playlists from the Youtube Data Api V3.

        If an error occurs, no playlists are returned or cached.

        Returns
        -------
        list[Playlist]
            A list of playlists fetched from the Youtube Data Api V3
        """
        logger.debug("Fetching playlists.")
        now = discord.utils.utcnow()
        if now - self._last_request_time < datetime.timedelta(hours=1):
            logger.warning(
                "Fetching playlists again, even though last fetch was less than an hour ago (%s).",
                self._last_request_time.strftime("%Y-%m-%d %H:%M:%S"),
            )
        self._last_request_time = now
        new_playlists: list[Playlist] = []
        page_token = None
        while True:
            data = await self._request_page(page_token)
            new_playlists.extend(data["items"])
            page_token = data.get("nextPageToken")
            if page_token is None:
                break
        logger.debug("Fetched %d playlists.", len(new_playlists))
        self._cache |= {playlist["id"]: playlist for playlist in new_playlists}
        return new_playlists

    async def get_or_fetch_playlists(self) -> list[Playlist]:
        """Get all playlists from the cache or fetch them if the cache is empty.

        Returns
        -------
        list[Playlist]
            A list of playlists from the cache or fetched from the Youtube Data Api V3
        """
        if not self._cache or (discord.utils.utcnow() - self._last_request_time) > datetime.timedelta(hours=1):
            return await self.fetch_playlists()
        return list(self._cache.values())

    async def get_playlists_by_name(self, name: str) -> list[Playlist]:
        """Get a playlist by name from the cache.

        Parameters
        ----------
        name : str
            The name of the playlist(s) to get

        Returns
        -------
        list[Playlist]
            A list of playlists from the cache that match the name
        """
        return [
            playlist
            for playlist in self._cache.values()
            if playlist["snippet"]["title"].lower().startswith(name.lower())
        ]

    async def get_playlist_exact(self, name: str) -> Playlist | None:
        """Get a playlist by name from the cache.

        Parameters
        ----------
        name : str
            The name of the playlist to get

        Returns
        -------
        Playlist | None
            The playlist from the cache that matches the name, or None if no match is found
        """
        return next(
            (playlist for playlist in self._cache.values() if playlist["snippet"]["title"] == name),
            None,
        )

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread) -> None:
        """Post if we can find a matching playlist for a game suggestion."""
        if thread.parent_id != GAMES_FORUM_ID:
            return

        if any(tag.id == GAME_SUGGESTIONS_TAG for tag in thread.applied_tags):
            playlists = await self.get_playlists_by_name(thread.name)
            if playlists:
                url = yarl.URL("https://www.youtube.com/playlist")
                msg = "\n".join(
                    f"- [{playlist['snippet']['title']}]({url.with_query(list=playlist['id'])})"
                    for playlist in playlists
                )
                await thread.send(
                    f"{f'{thread.owner.mention} ' if thread.owner else ''}It looks like charlie has played this game before:\n{msg}"
                    "\n *This is an automated message, if it seems incorrect or you have any questions, please ask the moderators!*",
                    suppress_embeds=True,
                )

    @commands.command(hidden=True)
    @commands.is_owner()
    async def search_playlist(self, ctx: commands.Context, name: str) -> None:
        """Search for a playlist by name."""
        playlist = await self.get_playlist_exact(name)
        if playlist is None:
            await ctx.send(f"No playlist found with the name `{name}`.")
        else:
            url = yarl.URL("https://www.youtube.com/playlist").with_query(list=playlist["id"])
            await ctx.send(f"Found playlist: {playlist['snippet']['title']} - {url}")


async def setup(bot: CBot) -> None:
    """Set up the Playlists Cog."""
    await bot.add_cog(Playlists(bot))
