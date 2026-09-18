"""Models for the youtube Playlist API."""

from typing import Literal, NotRequired, TypedDict


class Thumbnail(TypedDict):
    """Youtube Data Api V3 Thumbnail object."""

    url: str
    width: int
    height: int


class Thumbnails(TypedDict, total=False):
    """Youtube Data Api V3 Thumbnails object."""

    default: Thumbnail
    medium: Thumbnail
    high: Thumbnail
    standard: Thumbnail
    maxres: Thumbnail  # cspell: disable-line


class Localization(TypedDict):
    """Youtube Data Api V3 Localization object."""

    title: str
    description: str


class Snippet(TypedDict):
    """Youtube Data Api V3 Snippet object."""

    publishedAt: str
    channelId: str
    title: str
    description: str
    thumbnails: dict[str, dict[str, str]]
    channelTitle: str
    defaultLanguage: str
    localized: Localization


class Playlist(TypedDict):
    """Youtube Data Api V3 Playlist object."""

    kind: Literal["youtube#playlist"]
    etag: str
    id: str
    snippet: Snippet


class PageInfo(TypedDict):
    """Youtube Data Api V3 PageInfo object."""

    totalResults: int
    resultsPerPage: int


class YoutubeV3ListPlaylistsResponse(TypedDict):
    """Youtube Data Api V3 List Playlists Response object."""

    kind: Literal["youtube#playlistListResponse"]
    etag: str
    nextPageToken: NotRequired[str]
    prevPageToken: NotRequired[str]
    pageInfo: PageInfo
    items: list[Playlist]
