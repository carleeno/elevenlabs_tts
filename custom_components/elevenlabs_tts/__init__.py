"""ElevenLabs TTS Custom Integration"""
import logging

from homeassistant import core
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
import requests

from .const import CONF_VOICE, DEFAULT_VOICE
from .elevenlabs import ElevenLabsClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: core.HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the ElevenLabs TTS component from a config entry."""
    voice_name = entry.data.get(CONF_VOICE, DEFAULT_VOICE)
    client = ElevenLabsClient(entry.data)

    try:
        await hass.async_add_executor_job(client.get_voices)
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 401:
            return False
        raise ConfigEntryNotReady from err
    except Exception as err:
        raise ConfigEntryNotReady from err

    voice = client.get_voice_by_name(voice_name)
    if not voice:
        return False

    return True
