import asyncio
from typing import Any
from unittest.mock import MagicMock

import httpx
import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def semaphore() -> asyncio.Semaphore:
    return asyncio.Semaphore(1)


@pytest.fixture
def headers() -> dict[str, str]:
    return {"User-Agent": "TestBot/1.0"}


@pytest.fixture
def mock_unpaywall_response() -> dict[str, Any]:
    """Sample Unpaywall API response."""
    return {
        "doi": "10.1145/test",
        "title": "Test Paper",
        "journal_name": "Test Journal",
        "best_oa_location": {"url_for_pdf": "https://example.com/paper.pdf"},
    }


class TestUnpaywallRepository:
    """UnpaywallRepositoryのユニットテスト。"""

    async def test_init(self, headers: dict[str, str]) -> None:
        """初期化時にheadersが設定され、clientはNoneであること。"""
        from crawler.repository.unpaywall_repository import UnpaywallRepository

        repo = UnpaywallRepository(headers)
        assert repo.headers == headers
        assert repo.client is None

    async def test_fetch_paper_success(
        self,
        headers: dict[str, str],
        mock_unpaywall_response: dict[str, Any],
        semaphore: asyncio.Semaphore,
        mocker: MockerFixture,
    ) -> None:
        """DOIで論文データが正常に取得できること。"""
        from crawler.repository.unpaywall_repository import UnpaywallRepository

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = mock_unpaywall_response
        mock_response.raise_for_status = MagicMock()

        mocker.patch(
            "crawler.repository.unpaywall_repository.get_with_retry", return_value=mock_response
        )

        async with UnpaywallRepository(headers) as repo:
            result = await repo.fetch_by_doi("10.1145/test", semaphore)

        assert result is not None
        assert result.doi == "10.1145/test"
        assert result.pdf_url == "https://example.com/paper.pdf"

    async def test_fetch_paper_not_found(
        self,
        headers: dict[str, str],
        semaphore: asyncio.Semaphore,
        mocker: MockerFixture,
    ) -> None:
        """404エラーの場合、Noneが返されること。"""
        from crawler.repository.unpaywall_repository import UnpaywallRepository

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404

        mocker.patch(
            "crawler.repository.unpaywall_repository.get_with_retry",
            side_effect=httpx.HTTPStatusError(
                "Not Found", request=MagicMock(), response=mock_response
            ),
        )
        mock_logger = mocker.patch("crawler.repository.unpaywall_repository.logger.debug")

        async with UnpaywallRepository(headers) as repo:
            result = await repo.fetch_by_doi("10.1145/notfound", semaphore)

        assert result is None
        mock_logger.assert_called_with(
            "No paper found for DOI 10.1145/notfound on Unpaywall (404)."
        )

    async def test_fetch_paper_http_error(
        self,
        headers: dict[str, str],
        semaphore: asyncio.Semaphore,
        mocker: MockerFixture,
    ) -> None:
        """HTTPエラーの場合、Noneが返されること。"""
        from crawler.repository.unpaywall_repository import UnpaywallRepository

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500

        mocker.patch(
            "crawler.repository.unpaywall_repository.get_with_retry",
            side_effect=httpx.HTTPStatusError(
                "Server Error", request=MagicMock(), response=mock_response
            ),
        )
        mock_logger = mocker.patch("crawler.repository.unpaywall_repository.logger.warning")

        async with UnpaywallRepository(headers) as repo:
            result = await repo.fetch_by_doi("10.1145/test", semaphore)

        assert result is None
        mock_logger.assert_called()

    async def test_client_not_initialized(
        self, headers: dict[str, str], semaphore: asyncio.Semaphore
    ) -> None:
        """コンテキストマネージャー外で呼び出された場合、RuntimeErrorが発生すること。"""
        from crawler.repository.unpaywall_repository import UnpaywallRepository

        repo = UnpaywallRepository(headers)
        with pytest.raises(RuntimeError, match="Client is not initialized"):
            await repo.fetch_by_doi("10.1145/test", semaphore)
