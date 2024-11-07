import pytest
import requests

from meal_max.utils.random_utils import get_random

# Constants for testing
RANDOM_FLOAT = 0.42

@pytest.fixture
def mock_random_org(mocker):
    # Patch the requests.get call
    # requests.get returns an object, which we have replaced with a mock object
    mock_response = mocker.Mock()
    # We are giving that object a text attribute
    mock_response.text = f"{RANDOM_FLOAT}"
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response

def test_get_random(mock_random_org):
    """
    Test retrieving a random number from random.org.
    """
    # Call the get_random function
    result = get_random()
    
    # Assert that the result is the mocked random number
    assert result == RANDOM_FLOAT, f"Expected random number {RANDOM_FLOAT}, but got {result}"

    # Verify that the correct URL was called
    requests.get.assert_called_once_with(
        "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new", 
        timeout=5
    )

def test_get_random_timeout(mocker):
    """
    Test handling of a timeout exception.
    """
    # Patch requests.get to raise a Timeout exception
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)
    
    # Assert that a RuntimeError is raised with the correct message
    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random()

def test_get_random_request_failure(mocker):
    """
    Test handling of a general request failure.
    """
    # Patch requests.get to raise a RequestException
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error"))
    
    # Assert that a RuntimeError is raised with the correct message
    with pytest.raises(RuntimeError, match="Request to random.org failed: Connection error"):
        get_random()

def test_get_random_invalid_response(mock_random_org):
    """
    Test handling of an invalid response from random.org.
    """
    # Set the mock response text to an invalid value
    mock_random_org.text = "invalid_response"
    
    # Assert that a ValueError is raised with the correct message
    with pytest.raises(ValueError, match="Invalid response from random.org: invalid_response"):
        get_random()
