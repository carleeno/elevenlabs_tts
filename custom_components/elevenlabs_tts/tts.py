import logging

from homeassistant import core
from homeassistant.components.tts import Provider, TtsAudioType
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
import requests

from .const import CONF_SIMILARITY, CONF_STABILITY, CONF_VOICE, DEFAULT_VOICE
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


def get_engine(hass: core.HomeAssistant, config: dict, discovery_info=None) -> Provider:
    """Set up ElevenLabs TTS component."""
    client = ElevenLabsClient(config)

    return ElevenLabsProvider(client)


class ElevenLabsProvider(Provider):
    """The ElevenLabs TTS API provider."""

    def __init__(self, client: ElevenLabsClient) -> None:
        """Initialize the provider."""
        self._client = client
        self._name = "ElevenLabsTTS"

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return "en"

    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        return ["en"]

    @property
    def supported_options(self) -> list[str]:
        """Return list of supported options."""
        return [CONF_VOICE, CONF_STABILITY, CONF_SIMILARITY]

    def get_tts_audio(
        self, message: str, language: str, options: dict | None = None
    ) -> TtsAudioType:
        """Load TTS from the ElevenLabs API."""
        return self._client.get_tts_audio(message, options)

    @property
    def name(self) -> str:
        """Return provider name."""
        return self._name

    @property
    def extra_state_attributes(self) -> dict:
        """Return provider attributes."""
        return {"provider": self._name}
