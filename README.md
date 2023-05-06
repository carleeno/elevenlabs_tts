# ElevenLabs TTS for Home Assistant

This integration allows you to use ElevenLabs API as a text-to-speech provider for Home Assistant.

Disclaimer: This repo, the code within, and the maintainer/owner of this repo are in no way affiliated with ElevenLabs.

Privacy disclaimer: Data is transmitted to elevenlabs.io when using this TTS service, do not use it for text containing sensitive information.

You can find ElevenLab's privacy policy [here](https://beta.elevenlabs.io/privacy)

## Installation

This component is available via HACS as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories) which is the recommended method of installation.

You can also copy `custom_components/elevenlabs_tts` to your `custom_components` folder in HomeAssistant if you prefer to install manually.

## Example `tts` entry in your `configuration.yaml`

```yaml
tts:
  - platform: elevenlabs_tts
    api_key: !secret elevenlabs_api_key
    voice: Domi
    stability: 0.75
    similarity: 0.75
    model: eleven_multilingual_v1
    optimize_streaming_latency: 1
```

### Options:

- `platform` - specifies to use this component, must be `elevenlabs_tts`
- `api_key` - (optional) get access to your own account's voices
- `voice` - (optional, default: Domi) use a different voice
- `stability` - (optional, default: 0.75) set the stability of the speech synthesis
- `similarity` - (optional, default: 0.75) set the clarity/similarity boost of the speech synthesis
- `model` - (optional, default: eleven_monolingual_v1) change the model used for requests
- `optimize_streaming_latency` - (optional, default: 0) reduce latency at the cost of quality

## API key

At the time of writing, it's possible to use this without an API key, but don't expect it to work for long.

To get an API key, create an account at elevenlabs.io, and go to Profile Settings to copy it.

Note that using this extension will count against your character quota. As such, **DO NOT** use this TTS service for critical announcements, it will stop working once you've used up your quota.

## Caching

This integration inherently uses caching for the responses, meaning that if the text and options are the same as a previous service call, the response audio likely will be a replay of the previous response. The downside is this negates the natural variability that ElevenLabs provides when using the same phrase multiple times. The upside is that it reduces your quota usage and speeds up responses.

## Example service call

```yaml
service: tts.elevenlabs_tts_say
data:
  options:
    voice: Bella
    stability: 1
    similarity: 1
    model: eleven_multilingual_v1
    optimize_streaming_latency: 3
  entity_id: media_player.chromecast9105
  message: Hello there, how are you today?
```

The parameters in `options` are fully optional, this allows you to override what's defined in `configuration.yaml`.
