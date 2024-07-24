# ElevenLabs TTS for Home Assistant

This integration allows you to use ElevenLabs API as a text-to-speech provider for Home Assistant.

Disclaimer: This repo, the code within, and the maintainer/owner of this repo are in no way affiliated with ElevenLabs.

Privacy disclaimer: Data is transmitted to elevenlabs.io when using this TTS service, do not use it for text containing sensitive information.

You can find ElevenLab's privacy policy [here](https://beta.elevenlabs.io/privacy)

## Installation

This component is available via HACS as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories) which is the recommended method of installation.

You can also copy `custom_components/elevenlabs_tts` to your `custom_components` folder in HomeAssistant if you prefer to install manually.

## Setup

Go to Settings -> Devices & Services -> ADD INTEGRATION, and select ElevenLabs TTS

Enter your api key from your ElevenLabs account and click Submit.

### Options:

To customize the default options, in Devices & Services, click CONFIGURE on the ElevenLabs TTS card.

- `Voice` - Enter the name of one of the voices available in your account
- `Stability` - Sets the stability of the speech synthesis
- `Similarity` - Sets the clarity/similarity boost of the speech synthesis
- `Model` - Determines which model is used to generate speech
- `Optimize Streaming Latency` - Reduce latency at the cost of quality

## API key

To get an API key, create an account at elevenlabs.io, and go to Profile Settings to copy it.

Note that using this extension will count against your character quota. As such, **DO NOT** use this TTS service for critical announcements, it will stop working once you've used up your quota.

## Caching

This integration inherently uses caching for the responses, meaning that if the text and options are the same as a previous service call, the response audio likely will be a replay of the previous response. The downside is this negates the natural variability that ElevenLabs provides when using the same phrase multiple times. The upside is that it reduces your quota usage and speeds up responses.

## Example service call

```yaml
service: tts.speak
data:
  cache: true
  media_player_entity_id: media_player.bedroom_speaker
  message: Hello, how are you today?
  options:
    voice: Bella
    stability: 1
    similarity: 1
    style: 0.3 # Only supported in eleven_multilingual_v2
    use_speaker_boost: "true" # Only supported in eleven_multilingual_v2
    model: eleven_multilingual_v2
    optimize_streaming_latency: 3
target:
  entity_id: tts.elevenlabstts
```

The parameters in `options` are fully optional, and override the defaults specified in the integration config.
