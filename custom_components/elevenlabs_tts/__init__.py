"""ElevenLabs TTS Custom Integration"""
import logging

from homeassistant import core
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
import requests

from .const import DOMAIN, DEFAULT_VOICE, PLATFORMS
from .elevenlabs import ElevenLabsClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: core.HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the ElevenLabs TTS component from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    client = ElevenLabsClient(hass, entry)

    hass.data[DOMAIN][entry.entry_id] = client

    try:
        await client.get_voices()
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 401:
            return False
        raise ConfigEntryNotReady from err
    except Exception as err:
        raise ConfigEntryNotReady from err

    voice = await client.get_voice_by_name(DEFAULT_VOICE)
    if not voice:
        return False

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True