import logging

from homeassistant.components.tts import (
    ATTR_AUDIO_OUTPUT,
    ATTR_VOICE,
    TextToSpeechEntity,
    TtsAudioType,
    Voice,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_MODEL,
    CONF_OPTIMIZE_LATENCY,
    CONF_SIMILARITY,
    CONF_STABILITY,
    CONF_STYLE,
    CONF_USE_SPEAKER_BOOST,
    DOMAIN,
)
from .elevenlabs import ElevenLabsClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Wyoming speech to text."""
    client: ElevenLabsClient = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            ElevenLabsProvider(config_entry, client),
        ]
    )


class ElevenLabsProvider(TextToSpeechEntity):
    """The ElevenLabs TTS API provider."""

    def __init__(self, config_entry: ConfigEntry, client: ElevenLabsClient) -> None:
        """Initialize the provider."""
        self._client = client
        self._config_entry = config_entry
        self._name = "ElevenLabs TTS"

        self._attr_unique_id = f"{config_entry.entry_id}-tts"

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return "en"

    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        # This is for eleven_multilingual_v2, not all are supported in other models
        return [
            "en",  # English
            "ja",  # Japanese
            "zh",  # Chinese
            "de",  # German
            "hi",  # Hindi
            "fr",  # French
            "ko",  # Korean
            "pt",  # Portuguese
            "it",  # Italian
            "es",  # Spanish
            "id",  # Indonesian
            "nl",  # Dutch
            "tr",  # Turkish
            "fil",  # Filipino
            "pl",  # Polish
            "sv",  # Swedish
            "bg",  # Bulgarian
            "ro",  # Romanian
            "ar",  # Arabic
            "cs",  # Czech
            "el",  # Greek
            "fi",  # Finnish
            "hr",  # Croatian
            "ms",  # Malay
            "sk",  # Slovak
            "da",  # Danish
            "ta",  # Tamil
            "uk",  # Ukrainian
        ]

    @property
    def default_options(self):
        """Return a dict include default options."""
        return {ATTR_AUDIO_OUTPUT: "mp3"}

    @property
    def supported_options(self) -> list[str]:
        """Return list of supported options."""
        return [
            ATTR_VOICE,
            CONF_STABILITY,
            CONF_SIMILARITY,
            CONF_STYLE,
            CONF_USE_SPEAKER_BOOST,
            CONF_MODEL,
            CONF_OPTIMIZE_LATENCY,
            CONF_API_KEY,
            ATTR_AUDIO_OUTPUT,
        ]

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict | None = None
    ) -> TtsAudioType:
        """Load TTS from the ElevenLabs API."""
        return await self._client.get_tts_audio(message, options)

    def async_get_supported_voices(self, language: str) -> list[Voice] | None:
        """Return a list of supported voices for a language."""
        return self._client.voices

    @property
    def name(self) -> str:
        """Return provider name."""
        return self._name

    @property
    def extra_state_attributes(self) -> dict:
        """Return provider attributes."""
        return {"provider": self._name}
