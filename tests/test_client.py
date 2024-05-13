"Test client module."
from datetime import datetime, UTC
import pytest
from unittest.mock import Mock, patch, AsyncMock

from httpx import Response
import awsync.client as client


class TestHelpers:
    "Test helper functions."

    def test_utcnow(self) -> None:
        """
        Test utcnow method.
        Should return the same value as datetime.now(UTC).
        """
        with patch(f"awsync.client.datetime") as datetime_mock:
            mock_datetime = datetime(2000, 1, 1, 0, 0, 0, 0, tzinfo=UTC)
            datetime_mock.datetime.now.return_value = mock_datetime
            assert client.utcnow() == mock_datetime


@pytest.mark.asyncio
class TestRequest:
    "Test request functions."

    async def test_request_200(self) -> None:
        """
        Test request_with_retry with 200 OK response.
        Should return parsed Response object successfully.
        """
        mock_client = AsyncMock()
        mock_request = Mock()
        mock_logger = Mock()
        mock_client.request.return_value = Response(
            status_code=200, text="Mock response."
        )
        assert await client.request_with_retry(
            client=mock_client, request=mock_request, logger=mock_logger
        ) == client.Response(status=200, text="Mock response.")

    async def test_request_301(self) -> None:
        """
        Test request_with_retry with 301 Moved Permanently response.
        Should raise client.StatusError.
        """
        mock_client = AsyncMock()
        mock_request = Mock()
        mock_logger = Mock()
        mock_client.request.return_value = Response(
            status_code=301, text="Mock response."
        )
        with pytest.raises(client.StatusError):
            await client.request_with_retry(
                client=mock_client, request=mock_request, logger=mock_logger
            )

    async def test_request_500(self) -> None:
        """
        Test request_with_retry with perpetual 500 Internal Server Error response.
        Should raise request.MaxRetriesException after preforming retries.
        """
        mock_client = AsyncMock()
        mock_request = Mock()
        mock_logger = Mock()
        mock_client.request.return_value = Response(
            status_code=500, text="Mock response."
        )
        with patch(f"awsync.client.asyncio") as asyncio_mock, pytest.raises(
            client.MaxRetriesException
        ):
            asyncio_mock.sleep = AsyncMock()
            await client.request_with_retry(
                client=mock_client, request=mock_request, logger=mock_logger
            )

    async def test_request_500_then_200(self) -> None:
        """
        Test request_with_retry with 500 Internal Server Error response,
        then 200 OK second response.
        Should return parsed Response object successfully.
        """
        mock_client = AsyncMock()
        mock_request = Mock()
        mock_logger = Mock()
        mock_client.request.side_effect = [
            Response(status_code=500, text="Mock response."),
            Response(status_code=200, text="Mock response."),
        ]
        with patch(f"awsync.client.asyncio") as asyncio_mock:
            asyncio_mock.sleep = AsyncMock()
            assert await client.request_with_retry(
                client=mock_client, request=mock_request, logger=mock_logger
            ) == client.Response(status=200, text="Mock response.")

    async def test_request_custom_retries(self) -> None:
        """
        Test request_with_retry perpetual 500 Internal Server Error response,
        and custom retry amount set.
        Should raise request.MaxRetriesException after preforming expected number of retries.
        1 base attempt + 10 retires = 11 awaits.
        """
        mock_client = AsyncMock()
        mock_request = Mock()
        mock_logger = Mock()
        mock_client.request.return_value = Response(
            status_code=500, text="Mock response."
        )
        with patch(f"awsync.client.asyncio") as asyncio_mock:
            asyncio_mock.sleep = AsyncMock()
            try:
                await client.request_with_retry(
                    client=mock_client,
                    request=mock_request,
                    logger=mock_logger,
                    retries=10,
                )
            except client.MaxRetriesException:
                assert mock_client.request.await_count == 11
