"""OVOS MediaProvider plugin for YouTube.

Replaces the deprecated OCP search skill ``ovos-skill-youtube``. Instead of
answering ``ovos.common_play.query`` over the bus, this provider is loaded
in-process by the OCP pipeline, gated by the three-axis routing test, and its
:meth:`search` is called directly.

All YouTube access (and all ``mediavocab.Release`` mapping) is delegated to the
``tutubo`` client library, whose ``YoutubeSearch`` previews already expose a
``to_release()`` method backed by ``tutubo/mediavocab_bridge.py``.
"""
from typing import ClassVar, List, Optional, Set

from ovos_utils.log import LOG

from mediavocab import Release, Signals
from ovos_plugin_manager.templates.media_provider import MediaProvider

from ovos_media_provider_youtube.version import __version__  # noqa: F401


class YouTubeMediaProvider(MediaProvider):
    """Search YouTube and return ``mediavocab.Release`` playables."""

    name: ClassVar[str] = "youtube"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        # max results per search, overridable via plugin config
        self.max_results: int = int(self.config.get("max_results", 10))

    def search(self, signals: Signals, lang: str = "en-us", *,
               supported_playback_types: Optional[Set[str]] = None,
               blocked_genres: Optional[Set[str]] = None,
               region: Optional[str] = None,
               session_id: Optional[str] = None) -> List[Release]:
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
