"""Consts module."""

from homeassistant.const import Platform

################################
# Do not change! Will be set by release workflow
INTEGRATION_VERSION = "main"  # git tag will be used
MIN_REQUIRED_HA_VERSION = "0.0.0"  # set min required version in hacs.json
################################

PLATFORMS = [Platform.TTS]

DOMAIN = "elevenlabs_tts"
VERSION = "1.0.0"

DEFAULT_VOICE = "Domi"
CONF_STABILITY = "stability"
DEFAULT_STABILITY = 0.75
CONF_SIMILARITY = "similarity"
DEFAULT_SIMILARITY = 0.9
CONF_MODEL = "model"
DEFAULT_MODEL = "eleven_multilingual_v1"
CONF_OPTIMIZE_LATENCY = "optimize_streaming_latency"
DEFAULT_OPTIMIZE_LATENCY = 0
CONF_STYLE = "style"
DEFAULT_STYLE = 0.2
CONF_USE_SPEAKER_BOOST = "use_speaker_boost"
DEFAULT_USE_SPEAKER_BOOST = True
