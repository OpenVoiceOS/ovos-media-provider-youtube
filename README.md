# ovos-media-provider-youtube

OVOS **MediaProvider** plugin for YouTube. Replaces the deprecated OCP search
skill [`ovos-skill-youtube`](https://github.com/OpenVoiceOS/ovos-skill-youtube).

Instead of broadcasting `ovos.common_play.query` over the bus and waiting for
skills to answer, the OCP pipeline loads MediaProvider plugins in-process, gates
them by routing, and calls `search()` directly. This plugin wraps the
[`tutubo`](https://github.com/TigreGotico/tutubo) YouTube client, whose search
results already convert to [`mediavocab.Release`](https://github.com/TigreGotico/mediavocab)
objects via its `mediavocab_bridge`.

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

## License

Apache-2.0
