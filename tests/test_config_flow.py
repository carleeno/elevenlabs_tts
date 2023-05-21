from unittest.mock import Mock, patch

from homeassistant import config_entries, data_entry_flow
from httpx import HTTPStatusError
import pytest

from custom_components.elevenlabs_tts.const import DOMAIN

from .mocks import MOCK_CONFIG


@pytest.mark.asyncio
async def test_successful_config_flow(hass):
    """Test a successful config flow."""
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    # If a user were to enter `test_username` for username and `test_password`
    # for password, it would result in this function call
    with patch(
        "custom_components.elevenlabs_tts.elevenlabs.ElevenLabsClient.get_voices"
    ) as mock_get_voices:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=MOCK_CONFIG
        )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert mock_get_voices.call_count == 2
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["title"] == "Eleven Labs TTS"
    assert result["data"] == MOCK_CONFIG
    assert result["result"]


@pytest.mark.asyncio
async def test_bad_api_key(hass):
    """Test a bad config flow."""
    # ARRANGE
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    # Prepare mock response
    response_mock = Mock()
    response_mock.status_code = 401  # set the status code you want to test
    response_mock.json.return_value = {
        "detail": {"status": "invalid_api_key"}
    }  # return value for json() method

    with patch(
        "custom_components.elevenlabs_tts.elevenlabs.ElevenLabsClient.get_voices",
        side_effect=HTTPStatusError(
            "An error occurred", request=Mock(), response=response_mock
        ),
    ) as mock_get_voices:
        # ACT
        try:
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"], user_input=MOCK_CONFIG
            )
        except HTTPStatusError:
            pass

    # ASSERT
    assert mock_get_voices.call_count == 1
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["errors"] == {"api_key": "invalid_api_key"}
    assert result["step_id"] == "user"


@pytest.mark.asyncio
async def test_server_error(hass):
    """Test a bad config flow."""
    # ARRANGE
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    # Prepare mock response
    response_mock = Mock()
    response_mock.status_code = 500  # set the status code you want to test
    response_mock.content = b"Server Error"

    with patch(
        "custom_components.elevenlabs_tts.elevenlabs.ElevenLabsClient.get_voices",
        side_effect=HTTPStatusError(
            "An error occurred", request=Mock(), response=response_mock
        ),
    ) as mock_get_voices:
        # ACT
        try:
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"], user_input=MOCK_CONFIG
            )
        except HTTPStatusError:
            pass

    # ASSERT
    assert mock_get_voices.call_count == 1
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["errors"] == {"api_key": "Server Error"}
    assert result["step_id"] == "user"
