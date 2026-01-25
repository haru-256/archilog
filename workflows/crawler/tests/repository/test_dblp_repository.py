from typing import Any

import pytest
from pytest_mock import MockerFixture

from crawler.repository.dblp_repository import DBLPRepository


@pytest.fixture
def headers() -> dict[str, str]:
    return {"User-Agent": "ArchilogBot/1.0"}


@pytest.fixture
def mock_dblp_response_data() -> dict[str, Any]:
    return {
        "result": {
            "hits": {
                "@total": "2",
                "hit": [
                    {
                        "info": {
                            "title": "Test Paper 1",
                            "authors": {
                                "author": [
                                    {"text": "Author A"},
                                    {"text": "Author B"},
                                ]
                            },
                            "year": "2025",
                            "venue": "RecSys",
                            "doi": "10.1145/test1",
                            "type": "Conference and Workshop Papers",
                            "ee": "https://doi.org/10.1145/test1",
                            "url": "https://dblp.org/rec/conf/recsys/test1",
                        }
                    },
                    {
                        "info": {
                            "title": "Test Paper 2",
                            "authors": {"author": {"text": "Author C"}},
                            "year": "2025",
                            "venue": "RecSys",
                            "doi": None,
                            "type": None,
                            "ee": None,
                            "url": None,
                        }
                    },
                ],
            }
        }
    }


def test_parse_papers_valid(
    headers: dict[str, str], mock_dblp_response_data: dict[str, Any]
) -> None:
    """正常系: パース処理のテスト"""
    repo = DBLPRepository(headers)
    papers = repo._parse_papers(mock_dblp_response_data)

    assert len(papers) == 2
    assert papers[0].title == "Test Paper 1"
    assert papers[0].authors == ["Author A", "Author B"]
    assert papers[0].year == 2025
    assert papers[0].venue == "RecSys"
    assert papers[0].doi == "10.1145/test1"

    assert papers[1].title == "Test Paper 2"
    assert papers[1].authors == ["Author C"]
    assert papers[1].doi is None


def test_parse_papers_no_hits(headers: dict[str, str]) -> None:
    """ヒットなしの場合のパーステスト"""
    repo = DBLPRepository(headers)
    data = {"result": {"hits": {"@total": "0"}}}
    papers = repo._parse_papers(data)
    assert papers == []


def test_parse_papers_invalid_data(headers: dict[str, str]) -> None:
    """不正なデータのパーステスト"""
    repo = DBLPRepository(headers)
    data = {"invalid": "data"}
    papers = repo._parse_papers(data)
    assert papers == []


def test_parse_authors(headers: dict[str, str]) -> None:
    """著者情報のパーステスト"""
    repo = DBLPRepository(headers)

    # リスト形式
    data_list = {"author": [{"text": "A"}, {"text": "B"}]}
    assert repo._parse_authors(data_list) == ["A", "B"]

    # 単一辞書形式
    data_dict = {"author": {"text": "C"}}
    assert repo._parse_authors(data_dict) == ["C"]

    # None
    assert repo._parse_authors(None) == []

    # 空辞書
    assert repo._parse_authors({}) == []


async def test_fetch_papers_integration_mock(
    headers: dict[str, str], mock_dblp_response_data: dict[str, Any], mocker: MockerFixture
) -> None:
    """fetch_papersメソッドの統合的テスト（APIコールのみモック）"""
    mock_api_response = mocker.MagicMock()
    mock_api_response.status_code = 200
    mock_api_response.json.return_value = mock_dblp_response_data

    mock_robots_response = mocker.MagicMock()
    mock_robots_response.status_code = 200
    mock_robots_response.text = "User-agent: *\nAllow: /"

    async def mock_get(*args: object, **kwargs: object) -> object:
        # URLを見てrobots.txtかAPIかを判定する簡易ロジック
        url = str(args[1]) if len(args) > 1 else ""
        if "robots.txt" in url:
            return mock_robots_response
        return mock_api_response

    mocker.patch("httpx.AsyncClient.get", side_effect=mock_get)
    mocker.patch("httpx.AsyncClient.aclose")

    async with DBLPRepository(headers) as repo:
        papers = await repo.fetch_papers(conf="recsys", year=2025)

    assert len(papers) == 2
    assert papers[0].title == "Test Paper 1"
