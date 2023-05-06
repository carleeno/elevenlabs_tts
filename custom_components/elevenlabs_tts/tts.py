import logging

from homeassistant import core
from homeassistant.components.tts import Provider, TtsAudioType

from .const import (
    CONF_MODEL,
    CONF_OPTIMIZE_LATENCY,
    CONF_SIMILARITY,
    CONF_STABILITY,
    CONF_VOICE,
)
from .elevenlabs import ElevenLabsClient

_LOGGER = logging.getLogger(__name__)


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
        return [CONF_VOICE, CONF_STABILITY, CONF_SIMILARITY, CONF_MODEL, CONF_OPTIMIZE_LATENCY]

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
