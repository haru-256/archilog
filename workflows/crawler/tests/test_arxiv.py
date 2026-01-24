from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from pytest_mock import MockerFixture

from domain.paper import Paper
from usecase.arxiv import ArxivSearch


@pytest.fixture
def headers() -> dict[str, str]:
    return {"User-Agent": "TestBot/1.0"}


@pytest.fixture
def paper() -> Paper:
    return Paper(
        title="Attention Is All You Need",
        authors=["Vaswani et al."],
        year=2017,
        venue="NeurIPS",
        doi="10.1145/test",
    )


@pytest.fixture
def mock_arxiv_xml() -> str:
    """Sample arXiv Atom response XML."""
    return """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/1706.03762v5</id>
    <title>Attention Is All You Need</title>
    <summary>The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...</summary>
    <link href="http://arxiv.org/abs/1706.03762v5" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/1706.03762v5" rel="related" type="application/pdf"/>
  </entry>
</feed>
"""


async def test_init(headers: dict[str, str]) -> None:
    search = ArxivSearch(headers)
    assert search.headers == headers
    assert search.client is None


async def test_context_manager(headers: dict[str, str], mocker: MockerFixture) -> None:
    mock_client_aclose = mocker.patch("httpx.AsyncClient.aclose", new_callable=AsyncMock)

    async with ArxivSearch(headers) as search:
        assert isinstance(search.client, httpx.AsyncClient)

    mock_client_aclose.assert_called_once()


async def test_enrich_papers_success_doi(
    headers: dict[str, str], paper: Paper, mock_arxiv_xml: str, mocker: MockerFixture
) -> None:
    """DOIによる検索が成功するケース。"""
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = mock_arxiv_xml
    mock_response.raise_for_status = MagicMock()

    mocker.patch("usecase.arxiv.get_with_retry", return_value=mock_response)

    async with ArxivSearch(headers) as search:
        enriched_papers = await search.enrich_papers([paper])

    assert len(enriched_papers) == 1
    assert "The dominant sequence transduction models" in (enriched_papers[0].abstract or "")
    assert enriched_papers[0].pdf_url == "http://arxiv.org/pdf/1706.03762v5"


async def test_enrich_papers_success_title(
    headers: dict[str, str], paper: Paper, mock_arxiv_xml: str, mocker: MockerFixture
) -> None:
    """DOI検索が失敗し、タイトル検索で成功するケース。"""
    # 最初のDOI呼び出しは失敗（Noneを返す）、2クエリ目が成功
    mock_response_success = MagicMock(spec=httpx.Response)
    mock_response_success.status_code = 200
    mock_response_success.text = mock_arxiv_xml
    mock_response_success.raise_for_status = MagicMock()

    # 1回目のDOI検索は空のfeedを返すか、例外で失敗させる
    # ここではシンプルに `_fetch_from_arxiv` をモックして制御する方が確実だが、
    # `get_with_retry` の戻り値を制御してシミュレートする
    empty_xml = (
        '<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'
    )
    mock_response_empty = MagicMock(spec=httpx.Response)
    mock_response_empty.status_code = 200
    mock_response_empty.text = empty_xml
    mock_response_empty.raise_for_status = MagicMock()

    mocker.patch(
        "usecase.arxiv.get_with_retry", side_effect=[mock_response_empty, mock_response_success]
    )

    async with ArxivSearch(headers) as search:
        enriched_papers = await search.enrich_papers([paper])

    assert enriched_papers[0].pdf_url == "http://arxiv.org/pdf/1706.03762v5"


async def test_enrich_papers_no_match(
    headers: dict[str, str], paper: Paper, mocker: MockerFixture
) -> None:
    """検索結果が0件の場合、元のデータが変更されないこと。"""
    empty_xml = (
        '<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'
    )
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = empty_xml
    mock_response.raise_for_status = MagicMock()

    mocker.patch("usecase.arxiv.get_with_retry", return_value=mock_response)

    async with ArxivSearch(headers) as search:
        enriched_papers = await search.enrich_papers([paper])

    assert enriched_papers[0].abstract is None
    assert enriched_papers[0].pdf_url is None


async def test_overwrite_false(
    headers: dict[str, str], paper: Paper, mock_arxiv_xml: str, mocker: MockerFixture
) -> None:
    """overwrite=False の場合、既存のデータは上書きされないこと。"""
    paper.abstract = "Old Abstract"
    paper.pdf_url = "http://old.pdf"

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = mock_arxiv_xml
    mock_response.raise_for_status = MagicMock()

    mocker.patch("usecase.arxiv.get_with_retry", return_value=mock_response)

    async with ArxivSearch(headers) as search:
        enriched_papers = await search.enrich_papers([paper], overwrite=False)

    assert enriched_papers[0].abstract == "Old Abstract"
    assert enriched_papers[0].pdf_url == "http://old.pdf"


async def test_overwrite_true(
    headers: dict[str, str], paper: Paper, mock_arxiv_xml: str, mocker: MockerFixture
) -> None:
    """overwrite=True の場合、既存のデータが上書きされること。"""
    paper.abstract = "Old Abstract"
    paper.pdf_url = "http://old.pdf"

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = mock_arxiv_xml
    mock_response.raise_for_status = MagicMock()

    mocker.patch("usecase.arxiv.get_with_retry", return_value=mock_response)

    async with ArxivSearch(headers) as search:
        enriched_papers = await search.enrich_papers([paper], overwrite=True)

    assert "The dominant sequence transduction models" in (enriched_papers[0].abstract or "")
    assert enriched_papers[0].pdf_url == "http://arxiv.org/pdf/1706.03762v5"


async def test_client_not_initialized(headers: dict[str, str], paper: Paper) -> None:
    search = ArxivSearch(headers)
    with pytest.raises(RuntimeError, match="Use 'async with ArxivSearch"):
        await search.enrich_papers([paper])


async def test_api_error_handling(
    headers: dict[str, str], paper: Paper, mocker: MockerFixture
) -> None:
    """APIエラー発生時に例外で終了せず、ログを出力してNoneを返すこと。"""
    mocker.patch(
        "usecase.arxiv.get_with_retry",
        side_effect=httpx.HTTPStatusError("Error", request=MagicMock(), response=MagicMock()),
    )
    mock_logger = mocker.patch("usecase.arxiv.logger.warning")

    async with ArxivSearch(headers) as search:
        enriched_papers = await search.enrich_papers([paper])

    assert enriched_papers[0].abstract is None
    mock_logger.assert_called()
