from homeassistant import config_entries, exceptions
from homeassistant.components.tts import ATTR_VOICE
from homeassistant.const import CONF_API_KEY
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from httpx import HTTPStatusError
import voluptuous as vol

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
    DOMAIN,
)
from .elevenlabs import ElevenLabsClient


class ElevenlabsTTSSetupFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        return await self.async_step_user(import_config)

    async def async_step_user(self, user_input: dict = None) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            # Validate the provided API key
            resp = await self._validate_api_key(user_input[CONF_API_KEY])
            if resp is not None:
                errors[CONF_API_KEY] = resp

            if not errors:
                return self.async_create_entry(title="Eleven Labs TTS", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return ElevenlabsTTSOptionsFlowHandler(config_entry)

    async def _validate_api_key(self, api_key) -> list[str]:
        """Perform API key validation."""
        # Implement your validation logic here, e.g., make an API
        # call to validate the key
        # Return None if the key is valid, otherwise Error
        client = ElevenLabsClient(self.hass, api_key=api_key)
        try:
            await client.get_voices()
        except HTTPStatusError as http_error:
            if 500 <= http_error.response.status_code < 600:
                return "Server Error"
            elif 400 <= http_error.response.status_code < 500:
                err_json = http_error.response.json()
                return err_json["detail"]["status"]
            else:
                return str(http_error.response.content)
        return None


class ElevenlabsTTSOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle TTS options."""

    def __init__(self, config_entry):
        """Initialize TTS options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the TTS options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_API_KEY,
                        default=self.config_entry.data.get(CONF_API_KEY),
                    ): str,
                    vol.Optional(
                        ATTR_VOICE,
                        default=self.config_entry.options.get(
                            ATTR_VOICE, DEFAULT_VOICE
                        ),
                    ): str,
                    vol.Optional(
                        CONF_STABILITY,
                        default=self.config_entry.options.get(
                            CONF_STABILITY, DEFAULT_STABILITY
                        ),
                    ): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=0, max=1),
                    ),
                    vol.Optional(
                        CONF_SIMILARITY,
                        default=self.config_entry.options.get(
                            CONF_SIMILARITY, DEFAULT_SIMILARITY
                        ),
                    ): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=0, max=1),
                    ),
                    vol.Optional(
                        CONF_MODEL,
                        default=self.config_entry.options.get(
                            CONF_MODEL, DEFAULT_MODEL
                        ),
                    ): str,
                    vol.Optional(
                        CONF_OPTIMIZE_LATENCY,
                        default=self.config_entry.options.get(
                            CONF_OPTIMIZE_LATENCY, DEFAULT_OPTIMIZE_LATENCY
                        ),
                    ): vol.All(int, vol.Range(min=0, max=4)),
                    vol.Optional(
                        CONF_STYLE,
                        default=self.config_entry.options.get(
                            CONF_STYLE, DEFAULT_STYLE
                        ),
                    ): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=0, max=1),
                    ),
                    vol.Optional(
                        CONF_USE_SPEAKER_BOOST,
                        default=self.config_entry.options.get(
                            CONF_USE_SPEAKER_BOOST, DEFAULT_USE_SPEAKER_BOOST
                        ),
                    ): bool,
                }
            ),
        )


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
