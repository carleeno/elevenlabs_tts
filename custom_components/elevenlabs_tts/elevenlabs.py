import logging

from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.httpx_client import get_async_client
import httpx

from .const import (
    CONF_MODEL,
    CONF_OPTIMIZE_LATENCY,
    CONF_SIMILARITY,
    CONF_STABILITY,
    CONF_VOICE,
    DEFAULT_MODEL,
    DEFAULT_OPTIMIZE_LATENCY,
    DEFAULT_SIMILARITY,
    DEFAULT_STABILITY,
    DEFAULT_VOICE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class ElevenLabsClient:
    """A class to handle the connection to the ElevenLabs API."""

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry = None, api_key=None
    ) -> None:
        """Initialize the client."""
        _LOGGER.debug("Initializing ElevenLabs client")

        if api_key is None and config_entry is None:
            raise ValueError("Either 'api_key' or 'config_entry' must be provided.")

        self.config_entry = config_entry
        if api_key is not None:
            self._api_key = api_key
        else:
            self._api_key = config_entry.data[CONF_API_KEY]

        self.session: httpx.AsyncClient = get_async_client(hass)

        self.base_url = "https://api.elevenlabs.io/v1"
        self._headers = {"Content-Type": "application/json"}

        # [{"voice_id": str, "name": str, ...}]
        self._voices: list[dict] = []

    async def get(self, endpoint: str, api_key=None) -> dict:
        """Make a GET request to the API."""
        url = f"{self.base_url}/{endpoint}"
        headers = self._headers.copy()
        if api_key:
            headers["xi-api-key"] = api_key
        else:
            headers["xi-api-key"] = self._api_key

        try:
            response = await self.session.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            _LOGGER.error("Error during GET request: %s", str(e))
            return {}

    async def post(
        self, endpoint: str, data: dict, params: dict, api_key: str = None
    ) -> dict:
        """Make a POST request to the API."""
        url = f"{self.base_url}/{endpoint}"
        headers = self._headers.copy()
        if api_key:
            headers["xi-api-key"] = api_key
        else:
            headers["xi-api-key"] = self._api_key

        try:
            response = await self.session.post(
                url, headers=headers, json=data, params=params
            )
            response.raise_for_status()
            return response
        except httpx.HTTPError as e:
            _LOGGER.error("Error during POST request: %s", str(e))
            return {}

    async def get_voices(self) -> dict:
        """Get voices from the API."""
        endpoint = "voices"
        voices = await self.get(endpoint)
        self._voices = voices.get("voices", [])
        return self._voices

    async def get_voice_by_name(self, name: str) -> dict:
        """Get a voice by its name."""
        _LOGGER.debug("Looking for voice with name %s", name)
        for voice in self._voices:
            if voice["name"] == name:
                _LOGGER.debug("Found voice %s from name %s", voice["voice_id"], name)
                return voice
        _LOGGER.warning("Could not find voice with name %s", name)
        return {}

    async def get_tts_audio(
        self, message: str, options: dict | None = None
    ) -> tuple[str, bytes]:
        """Get text-to-speech audio for the given message."""
        (
            voice_id,
            stability,
            similarity,
            model,
            optimize_latency,
            api_key,
        ) = await self.get_tts_options(options)

        endpoint = f"text-to-speech/{voice_id}"
        data = {
            "text": message,
            "model_id": model,
            "voice_settings": {"stability": stability, "similarity_boost": similarity},
        }
        params = {"optimize_streaming_latency": optimize_latency}
        _LOGGER.debug("Requesting TTS from %s", endpoint)
        _LOGGER.debug("Request data: %s", data)
        _LOGGER.debug("Request params: %s", params)

        resp = await self.post(endpoint, data, params, api_key=api_key)
        return "mp3", resp.content

    async def get_tts_options(
        self, options: dict
    ) -> tuple[str, float, float, str, int, str]:
        """Get the text-to-speech options for generating TTS audio."""
        # If options is None, assign an empty dictionary to options
        if not options:
            options = {}

        # Get the voice from options, or fall back to the configured default voice
        voice = options.get(CONF_VOICE, self.config_entry.options[CONF_VOICE])

        # Get the stability, similarity, model, and optimize latency from options,
        # or fall back to the configured default values
        stability = options.get(
            CONF_STABILITY, self.config_entry.options[CONF_STABILITY]
        )
        similarity = options.get(
            CONF_SIMILARITY, self.config_entry.options[CONF_SIMILARITY]
        )
        model = options.get(CONF_MODEL, self.config_entry.options[CONF_MODEL])
        optimize_latency = options.get(
            CONF_OPTIMIZE_LATENCY, self.config_entry.options[CONF_OPTIMIZE_LATENCY]
        )

        api_key = options.get(CONF_API_KEY)

        # Convert optimize_latency to an integer
        optimize_latency = int(optimize_latency)

        # Get the voice ID by name from the TTS service
        voice = await self.get_voice_by_name(voice)
        voice_id = voice.get("voice_id", None)

        # If voice_id is not found, refresh the list of voices and try again
        if not voice_id:
            _LOGGER.debug("Could not find voice, refreshing voices")
            await self.get_voices()
            voice = await self.get_voice_by_name(voice)
            voice_id = voice.get("voice_id", None)

            # If voice_id is still not found, log a warning and use the first available voice
            if not voice_id:
                _LOGGER.warning(
                    "Could not find voice with name %s, available voices: %s",
                    voice,
                    [voice["name"] for voice in self._voices],
                )
                voice_id = self._voices[0]["voice_id"]

        return voice_id, stability, similarity, model, optimize_latency, api_key