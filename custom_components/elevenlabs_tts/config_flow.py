import logging
from types import MappingProxyType
from typing import Any

import aiohttp
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
)
import voluptuous as vol

from .const import (
    CONF_SIMILARITY,
    CONF_STABILITY,
    CONF_VOICE,
    DEFAULT_SIMILARITY,
    DEFAULT_STABILITY,
    DEFAULT_VOICE,
    DOMAIN,
)
from .elevenlabs import ElevenLabsClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_API_KEY): str,
    }
)

DEFAULT_OPTIONS = {
    CONF_VOICE: DEFAULT_VOICE,
    CONF_STABILITY: DEFAULT_STABILITY,
    CONF_SIMILARITY: DEFAULT_SIMILARITY,
}


async def validate_input(hass: HomeAssistant, data: dict) -> dict:
    """Validate the user input allows us to connect."""
    _LOGGER.debug("Config data: %s", data)
    client = ElevenLabsClient(data)
    await client.async_get_voices()


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ElevenLabs TTS."""

    VERSION = 1

    async def async_step_user(self, user_input: dict = None) -> FlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            await validate_input(self.hass, user_input)
        except aiohttp.ClientResponseError as err:
            if err.status == 401:
                errors["base"] = "invalid_auth"
            else:
                _LOGGER.exception("Unexpected response from API")
                errors["base"] = "cannot_connect"
        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title="ElevenLabs TTS", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlow(config_entry)


class OptionsFlow(config_entries.OptionsFlow):
    """Handle ElevenLabs TTS options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize ElevenLabs TTS options flow."""
        self.config_entry = config_entry
        _LOGGER.debug("OptionsFlow init data: %s", config_entry.data)

    async def async_step_init(self, user_input: dict = None) -> FlowResult:
        """Manage the ElevenLabs TTS options."""
        if user_input is not None:
            _LOGGER.debug("Creating entry with options: %s", user_input)
            return self.async_create_entry(title="ElevenLabs TTS", data=user_input)

        _LOGGER.debug(
            "OptionsFlow step_init w/o user input, options: %s",
            self.config_entry.options,
        )
        client = ElevenLabsClient(self.config_entry.options)
        voices = await client.async_get_voices()
        voice_names = [voice["name"] for voice in voices]
        _LOGGER.debug("Voice names: %s", voice_names)
        try:
            schema = elevenlabs_config_option_schema(
                self.config_entry.options, voice_names
            )
        except:
            _LOGGER.exception("Failed to make schema")
        _LOGGER.debug("OptionsFlow step_init schema: %s", schema)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
        )


def elevenlabs_config_option_schema(
    options: MappingProxyType[str, Any], voice_names: list[str]
) -> dict:
    """Return a schema for ElevenLabs TTS options."""
    if not options:
        _LOGGER.debug("Setting default options")
        options = DEFAULT_OPTIONS
    _LOGGER.debug("Options for schema: %s", options)
    return {
        vol.Optional(CONF_VOICE, default=options[CONF_VOICE]): SelectSelector(
            SelectSelectorConfig(options=voice_names)
        ),
        vol.Optional(CONF_STABILITY, default=options[CONF_STABILITY]): NumberSelector(
            NumberSelectorConfig(min=0, max=1, step=0.05)
        ),
        vol.Optional(CONF_SIMILARITY, default=options[CONF_SIMILARITY]): NumberSelector(
            NumberSelectorConfig(min=0, max=1, step=0.05)
        ),
    }
