import pytest
from pytest_mock import MockerFixture

from crawler.domain.paper import Paper
from crawler.repository.semantic_scholar_repository import SemanticScholarRepository


@pytest.fixture
def headers() -> dict[str, str]:
    return {"User-Agent": "TestBot/1.0"}


def test_parse_single_paper(headers: dict[str, str]) -> None:
    """単一の論文レスポンスのパーステスト"""
    repo = SemanticScholarRepository(headers)

    item = {
        "externalIds": {"DOI": "10.1234/test"},
        "abstract": "Test Abstract",
        "openAccessPdf": {"url": "http://example.com/pdf"},
        "title": "Test Title",
        "year": 2024,
        "venue": "Test Venue",
        "authors": [
            {"authorId": "1", "name": "Author One"},
            {"authorId": "2", "name": "Author Two"},
        ],
        "url": "https://www.semanticscholar.org/paper/test",
    }

    paper = repo._parse_single_paper(item)
    assert paper is not None
    assert paper.doi == "10.1234/test"
    assert paper.abstract == "Test Abstract"
    assert paper.pdf_url == "http://example.com/pdf"
    assert paper.title == "Test Title"
    assert paper.year == 2024
    assert paper.venue == "Test Venue"
    assert paper.authors == ["Author One", "Author Two"]


def test_parse_single_paper_minimal(headers: dict[str, str]) -> None:
    """最小限のフィールドでのパーステスト"""
    repo = SemanticScholarRepository(headers)
    item = {"externalIds": {"DOI": "10.1234/test"}}

    paper = repo._parse_single_paper(item)
    assert paper is not None
    assert paper.doi == "10.1234/test"
    assert paper.abstract is None
    assert paper.pdf_url is None


def test_parse_single_paper_none(headers: dict[str, str]) -> None:
    """Noneのパーステスト"""
    repo = SemanticScholarRepository(headers)
    paper = repo._parse_single_paper({})  # Empty dict
    assert paper is None


@pytest.mark.asyncio
async def test_enrich_papers_merge_logic(headers: dict[str, str], mocker: MockerFixture) -> None:
    """enrich_papersの結合ロジックテスト"""
    repo = SemanticScholarRepository(headers)

    # 既存の論文（一部情報不足）
    paper = Paper(
        title="Original Title",
        authors=[],
        year=0,
        venue="",
        doi="10.1234/test",
    )

    # APIから取得される論文（情報あり）
    fetched_paper = Paper(
        title="New Title",
        authors=["Author A"],
        year=2024,
        venue="New Venue",
        doi="10.1234/test",
        abstract="New Abstract",
        pdf_url="http://new.pdf",
    )

    # fetch_papers_batchをモック
    mocker.patch.object(repo, "fetch_papers_batch", return_value=[fetched_paper])

    # overwrite=False: 元のTitleは保持され、欠損項目は埋まるはず
    await repo.enrich_papers([paper], overwrite=False)

    assert paper.title == "Original Title"  # 保持
    assert paper.abstract == "New Abstract"  # 更新
    assert paper.pdf_url == "http://new.pdf"  # 更新

    # overwrite=True: 全て更新されるはず
    await repo.enrich_papers([paper], overwrite=True)
    assert paper.abstract == "New Abstract"  # overwriteされる
    assert paper.pdf_url == "http://new.pdf"  # overwriteされる
    assert paper.title == "Original Title"  # titleはoverwriteされない
