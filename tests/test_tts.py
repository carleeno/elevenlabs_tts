from unittest.mock import AsyncMock, Mock

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import pytest

from custom_components.elevenlabs_tts.tts import (
    DOMAIN,
    ElevenLabsClient,
    ElevenLabsProvider,
    async_setup_entry,
)


@pytest.mark.asyncio
async def test_async_setup_entry():
    """Test async_setup_entry."""
    # Prepare mock objects
    hass = Mock(spec=HomeAssistant)
    config_entry = Mock(spec=ConfigEntry)
    async_add_entities = Mock()
    client = Mock(spec=ElevenLabsClient)

    # Mock the DOMAIN dictionary for the HomeAssistant data
    hass.data = {DOMAIN: {config_entry.entry_id: client}}

    await async_setup_entry(hass, config_entry, async_add_entities)

    # Ensure async_add_entities was called with correct parameters
    async_add_entities.assert_called_once()
    provider = async_add_entities.call_args[0][0][
        0
    ]  # access the first argument of first call, which
    # is a list and get its first element

    assert isinstance(provider, ElevenLabsProvider)
    assert provider._config_entry == config_entry
    assert provider._client == client


@pytest.mark.asyncio
async def test_async_get_tts_audio():
    """Test async_get_tts_audio."""
    # ARRANGE
    client = Mock()
    client.get_tts_audio = AsyncMock(return_value=("mocked_format", b"mocked_audio"))
    provider = ElevenLabsProvider(Mock(), client)
    message = "Hello world"
    language = "en"
    options = {"option": "value"}

    # ACT
    result = await provider.async_get_tts_audio(message, language, options)

    # ASSERT
    client.get_tts_audio.assert_called_once_with(message, options)
    assert result == ("mocked_format", b"mocked_audio")
