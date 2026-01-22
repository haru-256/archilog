from typing import NoReturn

import httpx
import pytest
from pytest_mock import MockerFixture

from libs.http_utils import get_with_retry, is_rate_limit, post_with_retry


@pytest.mark.asyncio
async def test_is_rate_limit() -> None:
    response = httpx.Response(429)
    assert is_rate_limit(response) is True

    response = httpx.Response(200)
    assert is_rate_limit(response) is False

    response = httpx.Response(500)
    assert is_rate_limit(response) is False


@pytest.mark.asyncio
async def test_post_with_retry_success(mocker: MockerFixture) -> None:
    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)
    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_client.post.return_value = mock_response

    response = await post_with_retry(mock_client, "http://test.com", {}, {})

    assert response.status_code == 200
    assert mock_client.post.call_count == 1


@pytest.mark.asyncio
async def test_post_with_retry_backoff(mocker: MockerFixture) -> None:
    # Mock asyncio.sleep to verify it's called (and avoid real waiting)
    mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)

    # Setup: 429 twice, then 200
    resp_429 = mocker.Mock(spec=httpx.Response)
    resp_429.status_code = 429
    resp_429.url = "http://test.com"

    resp_200 = mocker.Mock(spec=httpx.Response)
    resp_200.status_code = 200

    mock_client.post.side_effect = [resp_429, resp_429, resp_200]

    response = await post_with_retry(mock_client, "http://test.com", {}, {})

    assert response.status_code == 200
    # Should be called 3 times (initial + 2 retries)
    assert mock_client.post.call_count == 3

    # Verify mock_sleep was called twice (once after each failure)
    assert mock_sleep.call_count == 2

    # Optional: We can check if sleep duration increases or is within range,
    # but since it's random/exponential, exact value check is tricky.
    # We just ensure backoff mechanism (sleep) is triggered.


@pytest.mark.asyncio
async def test_post_with_retry_exhausted(mocker: MockerFixture) -> None:
    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)

    resp_429 = mocker.MagicMock(spec=httpx.Response)
    resp_429.status_code = 429
    resp_429.url = "http://test.com"

    # raise_for_status mock for final error handling
    def raise_err() -> NoReturn:
        raise httpx.HTTPStatusError(
            "429 Too Many Requests",
            request=httpx.Request("POST", "http://test.com"),
            response=resp_429,
        )

    resp_429.raise_for_status.side_effect = raise_err

    mock_client.post.return_value = resp_429

    # Expect HTTPStatusError after retries exhausted (from log_and_raise_final_error)
    with pytest.raises(httpx.HTTPStatusError):
        await post_with_retry(mock_client, "http://test.com", {}, {})

    # Should stop after 5 attempts as per configured stop_after_attempt(5)
    assert mock_client.post.call_count == 5


@pytest.mark.asyncio
async def test_post_no_retry_on_500(mocker: MockerFixture) -> None:
    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)

    resp_500 = mocker.MagicMock(spec=httpx.Response)
    resp_500.status_code = 500

    def raise_err() -> NoReturn:
        raise httpx.HTTPStatusError(
            "500 Server Error",
            request=httpx.Request("POST", "http://test.com"),
            response=resp_500,
        )

    resp_500.raise_for_status.side_effect = raise_err

    mock_client.post.return_value = resp_500

    # Should raise immediately without retry
    with pytest.raises(httpx.HTTPStatusError):
        await post_with_retry(mock_client, "http://test.com", {}, {})

    assert mock_client.post.call_count == 1


@pytest.mark.asyncio
async def test_get_with_retry_backoff(mocker: MockerFixture) -> None:
    # Similar test for get_with_retry
    mock_sleep = mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)
    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)

    resp_429 = mocker.MagicMock(spec=httpx.Response)
    resp_429.status_code = 429
    resp_429.url = "http://test.com"

    resp_200 = mocker.MagicMock(spec=httpx.Response)
    resp_200.status_code = 200

    mock_client.get.side_effect = [resp_429, resp_200]

    response = await get_with_retry(mock_client, "http://test.com")

    assert response.status_code == 200
    assert mock_client.get.call_count == 2
    assert mock_sleep.call_count == 1
