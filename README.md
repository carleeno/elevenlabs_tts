# ElevenLabs TTS for Home Assistant

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
```

### Options:

- `platform` - specifies to use this component, must be `elevenlabs_tts`
- `api_key` - (optional) get access to your own account's voices
- `voice` - (optional, default: Domi) use a different voice
- `stability` - (optional, default: 0.75) set the stability of the speech synthesis
- `similarity` - (optional, default: 0.75) set the clarity/similarity boost of the speech synthesis

## Api key

At the time of writing, it's possible to use this without an API key, but don't expect it to work for long.

To get an API key, create an account at elevenlabs.io, and go to Profile Settings to copy it.

Note that using this extension will count against your character quota. As such, *NO NOT* use this TTS service for critical announcements, it will stop working once you've used up your quota.

## Example service call

```yaml
service: tts.elevenlabs_tts_say
data:
  options:
    voice: Bella
    stability: 1
    similarity: 1
  entity_id: media_player.chromecast9105
  message: Hello there, how are you today?
```

The parameters in `options` are fully optional, this allows you to override what's defined in `configuration.yaml`.
