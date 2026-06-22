"""OVOS MediaProvider plugin for YouTube.

Replaces the deprecated OCP search skill ``ovos-skill-youtube``. Instead of
answering ``ovos.common_play.query`` over the bus, this provider is loaded
in-process by the OCP pipeline, gated by the three-axis routing test, and its
:meth:`search` is called directly.

All YouTube access (and all ``mediavocab.Release`` mapping) is delegated to the
``tutubo`` client library, whose ``YoutubeSearch`` previews already expose a
``to_release()`` method backed by ``tutubo/mediavocab_bridge.py``.
"""
from typing import List, Optional, Set, ClassVar

from ovos_utils.log import LOG

from mediavocab import MediaType, Release, Signals
from mediavocab.taxonomy import PlaybackType
from ovos_plugin_manager.templates.media_provider import MediaProvider

from ovos_media_provider_youtube.version import __version__  # noqa: F401


class YouTubeMediaProvider(MediaProvider):
    """Search YouTube and return ``mediavocab.Release`` playables.

    Routing (three-axis gate):

    * ``media`` — the broad set of YouTube-able media types.
    * ``playback_type`` — both ``VIDEO`` and ``AUDIO`` (a YouTube ``Release``
      can be consumed either way; the backend selector decides at playback).
    * ``genre_filter`` — empty (no genre gate).
    """

    name: ClassVar[str] = "youtube"

    media: ClassVar[Set[MediaType]] = {
        MediaType.MOVIE,
        MediaType.EPISODIC_SERIES,
        MediaType.MUSIC_VIDEO,
        MediaType.PODCAST,
        MediaType.TV,
        MediaType.GENERIC,
    }

    playback_type: ClassVar[Set[PlaybackType]] = {
        PlaybackType.VIDEO,
        PlaybackType.AUDIO,
    }

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        # max results per search, overridable via plugin config
        self.max_results: int = int(self.config.get("max_results", 10))

    def is_available(self) -> bool:
        """``tutubo`` is a hard dependency and YouTube needs no API key, so the
        provider is always available (network reachability is handled per-search
        by the pipeline's ``search_safe`` wrapper)."""
        return True

    def search(self, signals: Signals, lang: str = "en-us") -> List[Release]:
        """Search YouTube for ``signals.title`` and return candidate Releases.

        Delegates to ``tutubo.YoutubeSearch``: each ``VideoPreview`` it yields
        carries a ``to_release()`` that maps through tutubo's
        ``mediavocab_bridge`` into a ``mediavocab.Release``.
        """
        query = (signals.title or "").strip()
        if not query:
            return []

        from tutubo import YoutubeSearch

        releases: List[Release] = []
        try:
            search = YoutubeSearch(query)
            for preview in search.iterate_videos(max_res=self.max_results):
                try:
                    releases.append(preview.to_release())
                except Exception:
                    LOG.exception("Failed to convert YouTube result to Release")
        except Exception:
            LOG.exception(f"YouTube search failed for query: {query!r}")
        return releases
