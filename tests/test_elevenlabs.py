from unittest.mock import Mock

from homeassistant.components.tts import ATTR_VOICE
from homeassistant.const import CONF_API_KEY
import orjson
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
import respx

from custom_components.elevenlabs_tts.const import (
    CONF_MODEL,
    CONF_OPTIMIZE_LATENCY,
    CONF_SIMILARITY,
    CONF_STABILITY,
)
from custom_components.elevenlabs_tts.elevenlabs import ElevenLabsClient


@pytest.fixture
def mock_config_entry():
    return Mock()


@pytest.fixture
async def client(hass):
    # Create a mock config entry with options
    mock_entry = MockConfigEntry(
        domain="your_component_domain",
        data={CONF_API_KEY: "test_api_key"},
        options={
            ATTR_VOICE: "test_voice",
            CONF_STABILITY: 0.5,
            CONF_SIMILARITY: 0.7,
            CONF_MODEL: "custom_model",
            CONF_OPTIMIZE_LATENCY: 1,
        },
    )
    mock_entry.add_to_hass(hass)

    # Create an instance of the ElevenLabsClient class for testing
    client = ElevenLabsClient(hass, config_entry=mock_entry)

    yield client


def test_init_with_api_key(hass):
    """Test initialization of ElevenLabsClient with an API key."""
    # Arrange
    api_key = "your-api-key"

    # Act
    client = ElevenLabsClient(hass, api_key=api_key)

    # Assert
    assert client._api_key == api_key


def test_init_with_config_entry(hass, mock_config_entry):
    """Test initialization of ElevenLabsClient with a config entry."""
    # Arrange
    mock_config_entry.data = {"api_key": "your-api-key"}

    # Act
    client = ElevenLabsClient(hass, config_entry=mock_config_entry)

    # Assert
    assert client._api_key == mock_config_entry.data["api_key"]
    assert client.base_url == "https://api.elevenlabs.io/v1"
    assert client._headers == {"Content-Type": "application/json"}
    assert client._voices == []


def test_init_without_api_key_or_config_entry(hass):
    """Test initialization of ElevenLabsClient without an API key or config entry."""
    # Act & Assert
    with pytest.raises(ValueError):
        ElevenLabsClient(hass)


@pytest.mark.asyncio
async def test_get(client):
    """Test the get method of ElevenLabsClient."""
    with respx.mock:
        # Mock the HTTP GET request
        endpoint = "test"
        mock_response = {"key": "value"}
        respx.get(f"https://api.elevenlabs.io/v1/{endpoint}").respond(
            json=mock_response
        )

        # Call the method being tested
        response = await client.get(endpoint)

        # Assert that the response matches the expected value
        assert response == mock_response

        # Assert that the request was made with the correct URL and headers
        assert respx.calls[0].request.url == f"https://api.elevenlabs.io/v1/{endpoint}"
        assert respx.calls[0].request.headers["xi-api-key"] == client._api_key


@pytest.mark.asyncio
async def test_get_with_api_key(client):
    """Test the get method of ElevenLabsClient with a specific API key."""
    with respx.mock:
        # Mock the HTTP GET request
        endpoint = "test"
        mock_response = {"key": "value"}
        respx.get(f"https://api.elevenlabs.io/v1/{endpoint}").respond(
            json=mock_response
        )

        # Call the method being tested with a specific API key
        api_key = "test-api-key"
        response = await client.get(endpoint, api_key=api_key)

        # Assert that the response matches the expected value
        assert response == mock_response

        # Assert that the request was made with the correct URL and headers
        assert respx.calls[0].request.url == f"https://api.elevenlabs.io/v1/{endpoint}"
        assert respx.calls[0].request.headers["xi-api-key"] == api_key


@pytest.mark.asyncio
async def test_post(client):
    """Test the post method of ElevenLabsClient."""
    with respx.mock:
        # Mock the HTTP POST request
        endpoint = "test"
        mock_response = b'{"param":"value"}'
        respx.post(f"https://api.elevenlabs.io/v1/{endpoint}").respond(
            content=mock_response
        )

        # Call the method being tested
        response = await client.post(
            endpoint, data={"param": "value"}, params={"query": "param"}
        )

        # Assert that the response matches the expected value
        assert response.content == mock_response

        # Assert that the request was made with the correct URL, headers, and data
        expected_url = f"https://api.elevenlabs.io/v1/{endpoint}?query=param"
        assert respx.calls[0].request.url == expected_url
        assert respx.calls[0].request.headers["xi-api-key"] == client._api_key
        assert respx.calls[0].request.headers["accept"] == "audio/mpeg"
        assert respx.calls[0].request.content == b'{"param":"value"}'


@pytest.mark.asyncio
async def test_post_with_api_key(client):
    """Test the post method of ElevenLabsClient with a specific API key."""
    with respx.mock:
        # Mock the HTTP POST request
        endpoint = "test"
        mock_response = b'{"param":"value"}'
        respx.post(f"https://api.elevenlabs.io/v1/{endpoint}").respond(
            content=mock_response
        )

        # Call the method being tested with a specific API key
        api_key = "test-api-key"
        response = await client.post(
            endpoint,
            data={"param": "value"},
            params={"query": "param"},
            api_key=api_key,
        )

        # Assert that the response matches the expected value
        assert response.content == mock_response

        # Assert that the request was made with the correct URL, headers, and data
        expected_url = f"https://api.elevenlabs.io/v1/{endpoint}?query=param"
        assert respx.calls[0].request.url == expected_url
        assert respx.calls[0].request.headers["xi-api-key"] == api_key
        assert respx.calls[0].request.headers["accept"] == "audio/mpeg"
        assert respx.calls[0].request.content == b'{"param":"value"}'


@pytest.mark.asyncio
async def test_get_voices(client):
    with respx.mock:
        # Mock the HTTP GET request
        mock_response = {
            "voices": [
                {"voice_id": "1", "name": "Voice 1"},
                {"voice_id": "2", "name": "Voice 2"},
            ]
        }
        respx.get("https://api.elevenlabs.io/v1/voices").respond(json=mock_response)

        # Call the method being tested
        voices = await client.get_voices()

        # Assert that the returned value matches the expected value
        assert voices == mock_response["voices"]

        # Assert that the request was made with the correct URL and headers
        assert respx.calls[0].request.url == "https://api.elevenlabs.io/v1/voices"
        assert respx.calls[0].request.headers["xi-api-key"] == client._api_key

        # Assert that the client's _voices attribute is updated correctly
        assert client._voices == mock_response["voices"]


@pytest.mark.asyncio
async def test_get_voice_by_name_or_id(client):
    # Set up mock data and voice name
    voices = [
        {"voice_id": "1", "name": "Voice1"},
        {"voice_id": "2", "name": "Voice2"},
        {"voice_id": "3", "name": "Voice3"},
    ]
    client._voices = voices
    voice_name = "Voice2"

    # Call the method being tested
    voice = await client.get_voice_by_name_or_id(voice_name)

    # Assert that the returned voice matches the expected voice
    assert voice == {"voice_id": "2", "name": "Voice2"}


@pytest.mark.asyncio
async def test_get_voice_by_name_not_found(client):
    # Set up mock data and voice name
    voices = [
        {"voice_id": "1", "name": "Voice1"},
        {"voice_id": "2", "name": "Voice2"},
        {"voice_id": "3", "name": "Voice3"},
    ]
    client._voices = voices
    voice_name = "Voice4"  # Voice name not present in the mocked voices

    # Call the method being tested
    voice = await client.get_voice_by_name_or_id(voice_name)

    # Assert that the returned voice is an empty dictionary
    assert voice == {}


@pytest.mark.asyncio
async def test_get_tts_audio(client):
    with respx.mock:
        # Mock the HTTP POST request
        endpoint = "text-to-speech/1"
        message = "Hello, world!"
        mock_content = b"mock_audio_data"
        respx.post(f"https://api.elevenlabs.io/v1/{endpoint}").respond(
            content=mock_content
        )
        voices = [
            {"voice_id": "1", "name": "Voice1"},
            {"voice_id": "2", "name": "Voice2"},
            {"voice_id": "3", "name": "Voice3"},
        ]
        client._voices = voices

        # Define the options for the TTS audio generation
        options = {
            "voice": "Voice1",
            "stability": 0.5,
            "similarity": 0.7,
            "model": "custom_model",
            "optimize_latency": 1,
            "api_key": "test_api_key",
        }

        # Call the method being tested with the options
        audio_format, audio_data = await client.get_tts_audio(message, options)

        # Assert that the returned audio format and data are correct
        assert audio_format == "mp3"
        assert audio_data == mock_content

        # Assert that the request was made with the correct URL,
        # headers, data, and params
        request = respx.calls[0].request
        assert (
            request.url
            == f"https://api.elevenlabs.io/v1/{endpoint}?optimize_streaming_latency=1"
        )
        assert request.headers["xi-api-key"] == "test_api_key"
        assert request.headers["accept"] == "audio/mpeg"
        request_content = request.content
        expected_content = orjson.dumps(
            {
                "text": "Hello, world!",
                "model_id": "custom_model",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.7},
            }
        )
        assert request_content == expected_content


@pytest.mark.asyncio
async def test_get_tts_options_with_valid_voice_name(client):
    """Test get_tts_options with a valid voice name."""
    with respx.mock:
        # Define the example voices
        example_voices = [
            {"voice_id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel"},
            {"voice_id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi"},
            {"voice_id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella"},
            {"voice_id": "ErXwobaYiN019PkySvjV", "name": "Antoni"},
            {"voice_id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli"},
            {"voice_id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh"},
            {"voice_id": "VR6AewLTigWG4xSOukaG", "name": "Arnold"},
            {"voice_id": "pNInz6obpgDQGcFmaJgB", "name": "Adam"},
            {"voice_id": "yoZ06aMxZJJ28mfd3POQ", "name": "Sam"},
        ]

        # Mock the API response for getting voices
        respx.get("https://api.elevenlabs.io/v1/voices").respond(
            json={"voices": example_voices}
        )

        options = {
            ATTR_VOICE: "Rachel",
            CONF_STABILITY: 0.5,
            CONF_SIMILARITY: 0.7,
            CONF_MODEL: "custom_model",
            CONF_OPTIMIZE_LATENCY: 1,
            CONF_API_KEY: "test_api_key",
        }

        (
            voice_id,
            stability,
            similarity,
            model,
            optimize_latency,
            api_key,
        ) = await client.get_tts_options(options)
        assert voice_id == "21m00Tcm4TlvDq8ikWAM"
        assert stability == 0.5
        assert similarity == 0.7
        assert model == "custom_model"
        assert optimize_latency == 1
        assert api_key == "test_api_key"


@pytest.mark.asyncio
async def test_get_tts_options_with_valid_voice_name_not_found(client):
    """Test get_tts_options with a valid voice name not found in the list."""
    with respx.mock:
        # Define the example voices
        example_voices = [
            {"voice_id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel"},
            {"voice_id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi"},
            {"voice_id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella"},
            {"voice_id": "ErXwobaYiN019PkySvjV", "name": "Antoni"},
            {"voice_id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli"},
            {"voice_id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh"},
            {"voice_id": "VR6AewLTigWG4xSOukaG", "name": "Arnold"},
            {"voice_id": "pNInz6obpgDQGcFmaJgB", "name": "Adam"},
            {"voice_id": "yoZ06aMxZJJ28mfd3POQ", "name": "Sam"},
        ]

        # Mock the API response for getting voices
        respx.get("https://api.elevenlabs.io/v1/voices").respond(
            json={"voices": example_voices}
        )

        options = {
            ATTR_VOICE: "Unknown",
            CONF_STABILITY: 0.5,
            CONF_SIMILARITY: 0.7,
            CONF_MODEL: "custom_model",
            CONF_OPTIMIZE_LATENCY: 1,
            CONF_API_KEY: "test_api_key",
        }

        (
            voice_id,
            stability,
            similarity,
            model,
            optimize_latency,
            api_key,
        ) = await client.get_tts_options(options)
        assert (
            voice_id == "21m00Tcm4TlvDq8ikWAM"
        )  # Fallback to the first available voice
        assert stability == 0.5
        assert similarity == 0.7
        assert model == "custom_model"
        assert optimize_latency == 1
        assert api_key == "test_api_key"


@pytest.mark.asyncio
async def test_get_tts_options_with_valid_voice_name_refresh(client):
    """Test get_tts_options with a valid voice name after refreshing."""
    with respx.mock:
        # Define the example voices
        example_voices_initial = [
            {"voice_id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi"},
            {"voice_id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella"},
            {"voice_id": "ErXwobaYiN019PkySvjV", "name": "Antoni"},
        ]
        example_voices_refreshed = [
            {"voice_id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel"},
            {"voice_id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi"},
            {"voice_id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella"},
            {"voice_id": "ErXwobaYiN019PkySvjV", "name": "Antoni"},
        ]

        # Mock the API response for getting voices
        respx.get("https://api.elevenlabs.io/v1/voices").respond(
            json={"voices": example_voices_initial}
        )
        respx.get("https://api.elevenlabs.io/v1/voices").respond(
            json={"voices": example_voices_refreshed}
        )

        options = {
            ATTR_VOICE: "Rachel",
            CONF_STABILITY: 0.5,
            CONF_SIMILARITY: 0.7,
            CONF_MODEL: "custom_model",
            CONF_OPTIMIZE_LATENCY: 1,
            CONF_API_KEY: "test_api_key",
        }

        (
            voice_id,
            stability,
            similarity,
            model,
            optimize_latency,
            api_key,
        ) = await client.get_tts_options(options)
        assert voice_id == "21m00Tcm4TlvDq8ikWAM"
        assert stability == 0.5
        assert similarity == 0.7
        assert model == "custom_model"
        assert optimize_latency == 1
        assert api_key == "test_api_key"
