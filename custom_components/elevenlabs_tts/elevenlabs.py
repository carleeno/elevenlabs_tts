import logging

from homeassistant.components.tts import ATTR_AUDIO_OUTPUT, ATTR_VOICE, Voice
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import get_async_client
import httpx
import orjson

from .const import (
    CONF_MODEL,
    CONF_OPTIMIZE_LATENCY,
    CONF_SIMILARITY,
    CONF_STABILITY,
    CONF_STYLE,
    CONF_USE_SPEAKER_BOOST,
    DEFAULT_MODEL,
    DEFAULT_OPTIMIZE_LATENCY,
    DEFAULT_SIMILARITY,
    DEFAULT_STABILITY,
    DEFAULT_STYLE,
    DEFAULT_USE_SPEAKER_BOOST,
    DEFAULT_VOICE,
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

        response = await self.session.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    async def post(
        self, endpoint: str, data: dict, params: dict, api_key: str = None
    ) -> dict:
        """Make a POST request to the API."""
        url = f"{self.base_url}/{endpoint}"
        headers = self._headers.copy()
        headers["accept"] = "audio/mpeg"
        if api_key:
            headers["xi-api-key"] = api_key
        else:
            headers["xi-api-key"] = self._api_key

        json_str = orjson.dumps(data)

        response = await self.session.post(
            url,
            headers=headers,
            data=json_str,
            params=params,
            timeout=httpx.Timeout(60),
        )
        response.raise_for_status()
        return response

    async def get_voices(self) -> dict:
        """Get voices from the API."""
        endpoint = "voices"
        voices = await self.get(endpoint)
        self._voices = voices.get("voices", [])

        self.voices = []

        for voice in self._voices:
            new_voice = Voice(voice_id=voice["voice_id"], name=voice["name"])
            self.voices.append(new_voice)

        return self._voices

    async def get_voice_by_name_or_id(self, identifier: str) -> dict:
        """Get a voice by its name or ID."""
        _LOGGER.debug("Looking for voice with identifier %s", identifier)
        for voice in self._voices:
            if voice["name"] == identifier or voice["voice_id"] == identifier:
                _LOGGER.debug(
                    "Found voice %s from identifier %s", voice["voice_id"], identifier
                )
                return voice
        _LOGGER.warning("Could not find voice with identifier %s", identifier)
        return {}

    async def get_tts_audio(
        self, message: str, options: dict | None = None
    ) -> tuple[str, bytes]:
        """Get text-to-speech audio for the given message."""
        tts_options = await self.get_tts_options(options)
        voice_id, stability, similarity, model, optimize_latency, api_key = tts_options[
            :6
        ]

        endpoint = f"text-to-speech/{voice_id}"
        data = {
            "text": message,
            "model_id": model,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity,
            },
        }

        if model == "eleven_multilingual_v2":
            style, use_speaker_boost = tts_options[6:]
            data["voice_settings"]["style"] = style
            data["voice_settings"]["use_speaker_boost"] = use_speaker_boost

        params = {"optimize_streaming_latency": optimize_latency}
        _LOGGER.debug("Requesting TTS from %s", endpoint)
        _LOGGER.debug("Request data: %s", data)
        _LOGGER.debug("Request params: %s", params)

        resp = await self.post(endpoint, data, params, api_key=api_key)
        return "mp3", resp.content

    async def get_tts_options(
        self, options: dict
    ) -> tuple[str, float, float, str, int, str, float, bool]:
        """Get the text-to-speech options for generating TTS audio."""
        # If options is None, assign an empty dictionary to options
        if not options:
            options = {}

        if options.get(ATTR_AUDIO_OUTPUT, "mp3") != "mp3":
            raise ValueError("Only MP3 output is supported.")

        # Get the voice from options, or fall back to the configured default voice
        voice_opt = (
            options.get(ATTR_VOICE)
            or self.config_entry.options.get(ATTR_VOICE)
            or DEFAULT_VOICE
        )

        # Get the stability, similarity, model, and optimize latency from options,
        # or fall back to the configured default values
        stability = (
            options.get(CONF_STABILITY)
            or self.config_entry.options.get(CONF_STABILITY)
            or DEFAULT_STABILITY
        )

        similarity = (
            options.get(CONF_SIMILARITY)
            or self.config_entry.options.get(CONF_SIMILARITY)
            or DEFAULT_SIMILARITY
        )

        model = (
            options.get(CONF_MODEL)
            or self.config_entry.options.get(CONF_MODEL)
            or DEFAULT_MODEL
        )

        optimize_latency = (
            options.get(CONF_OPTIMIZE_LATENCY)
            or self.config_entry.options.get(CONF_OPTIMIZE_LATENCY)
            or DEFAULT_OPTIMIZE_LATENCY
        )

        api_key = (
            options.get(CONF_API_KEY)
            or self.config_entry.options.get(CONF_API_KEY)
            or self._api_key
        )

        # Convert optimize_latency to an integer
        optimize_latency = int(optimize_latency)

        # Get the voice ID by name from the TTS service

        voice = await self.get_voice_by_name_or_id(voice_opt)
        voice_id = voice.get("voice_id", None)

        # If voice_id is not found, refresh the list of voices and try again
        if not voice_id:
            _LOGGER.debug("Could not find voice, refreshing voices")
            await self.get_voices()
            voice = await self.get_voice_by_name_or_id(voice_opt)
            voice_id = voice.get("voice_id", None)

            # If voice_id is still not found, log a warning
            #  and use the first available voice
            if not voice_id:
                _LOGGER.warning(
                    "Could not find voice with name %s, available voices: %s",
                    voice,
                    [voice["name"] for voice in self._voices],
                )
                voice_id = self._voices[0]["voice_id"]

        if model == "eleven_multilingual_v2":
            style = (
                options.get(CONF_STYLE)
                or self.config_entry.options.get(CONF_STYLE)
                or DEFAULT_STYLE
            )
            use_speaker_boost = (
                options.get(CONF_USE_SPEAKER_BOOST)
                or self.config_entry.options.get(CONF_USE_SPEAKER_BOOST)
                or DEFAULT_USE_SPEAKER_BOOST
            )
            return (
                voice_id,
                stability,
                similarity,
                model,
                optimize_latency,
                api_key,
                style,
                use_speaker_boost,
            )

        return (
            voice_id,
            stability,
            similarity,
            model,
            optimize_latency,
            api_key,
        )

