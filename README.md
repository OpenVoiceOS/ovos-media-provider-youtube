# ovos-media-provider-youtube

This plugin is an OVOS MediaProvider for YouTube. It replaces the deprecated
OCP search skill [`ovos-skill-youtube`](https://github.com/OpenVoiceOS/ovos-skill-youtube).

The OCP pipeline does not broadcast `ovos.common_play.query` over the bus and
wait for skills to answer. Instead, it loads MediaProvider plugins in-process,
gates them by routing, and calls `search()` directly. This plugin wraps the
[`tutubo`](https://github.com/TigreGotico/tutubo) YouTube client. The client's
search results already convert to [`mediavocab.Release`](https://github.com/TigreGotico/mediavocab)
objects through its `mediavocab_bridge`.

## Install

```bash
pip install ovos-media-provider-youtube
```

## Routing

| Axis | Value |
|------|-------|
| `media` | `MOVIE`, `EPISODIC_SERIES`, `MUSIC_VIDEO`, `PODCAST`, `TV`, `GENERIC` |
| `playback_type` | `VIDEO`, `AUDIO` |
| `genre_filter` | *(none)* |

## Entry point

```toml
[project.entry-points."opm.media.provider"]
youtube = "ovos_media_provider_youtube:YouTubeMediaProvider"
```

## Configuration

| Key | Default | Description |
|-----|---------|-------------|
| `max_results` | `10` | Maximum number of results returned per search. |

## Related projects

- [`ovos-skill-youtube`](https://github.com/OpenVoiceOS/ovos-skill-youtube): the deprecated skill this plugin replaces.
- [`tutubo`](https://github.com/TigreGotico/tutubo): the YouTube client this plugin wraps.
- [`mediavocab`](https://github.com/TigreGotico/mediavocab): the shared media vocabulary this plugin's results use.

## License

Apache-2.0
