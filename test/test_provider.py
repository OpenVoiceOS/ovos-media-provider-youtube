"""Tests for the YouTube MediaProvider plugin (network-free)."""
from unittest.mock import MagicMock, patch

from mediavocab import MediaType, Release, Signals, Work

from ovos_media_provider_youtube import YouTubeMediaProvider


def _make_release(title="Some Video"):
    work = Work(title=title, media_type=MediaType.EPISODIC_SERIES)
    return Release(work=work, uri="https://youtube.com/watch?v=abc", platform="youtube")


def test_instantiation():
    provider = YouTubeMediaProvider()
    assert provider.name == "youtube"


def test_search_empty_title_returns_empty():
    provider = YouTubeMediaProvider()
    assert provider.search(Signals(title="")) == []
    assert provider.search(Signals()) == []


def test_search_wires_to_tutubo_bridge():
    """search() drives tutubo.YoutubeSearch and returns list[Release] from
    each preview's bridge-backed .to_release()."""
    provider = YouTubeMediaProvider()

    preview = MagicMock()
    preview.to_release.return_value = _make_release("Blade Runner")

    fake_search = MagicMock()
    fake_search.iterate_videos.return_value = iter([preview])

    with patch("tutubo.YoutubeSearch", return_value=fake_search) as ctor:
        results = provider.search(
            Signals(title="blade runner"),
            lang="en-us",
            supported_playback_types={"video", "audio"},
            blocked_genres={"adult"},
            region="US",
            session_id="sess-1",
        )

    ctor.assert_called_once_with("blade runner")
    fake_search.iterate_videos.assert_called_once()
    preview.to_release.assert_called_once()

    assert isinstance(results, list)
    assert len(results) == 1
    assert all(isinstance(r, Release) for r in results)
    assert results[0].work.title == "Blade Runner"


def test_search_swallows_per_item_errors():
    provider = YouTubeMediaProvider()

    bad = MagicMock()
    bad.to_release.side_effect = RuntimeError("boom")
    good = MagicMock()
    good.to_release.return_value = _make_release("ok")

    fake_search = MagicMock()
    fake_search.iterate_videos.return_value = iter([bad, good])

    with patch("tutubo.YoutubeSearch", return_value=fake_search):
        results = provider.search(Signals(title="anything"))

    assert [r.work.title for r in results] == ["ok"]
