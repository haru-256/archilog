import pytest

from crawler.repository.arxiv_repository import ArxivRepository


@pytest.fixture
def headers() -> dict[str, str]:
    return {"User-Agent": "TestBot/1.0"}


def test_parse_xml_valid(headers: dict[str, str]) -> None:
    """正常なXMLのパーステスト"""
    repo = ArxivRepository(headers)
    xml = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/1706.03762v5</id>
    <title>Attention Is All You Need</title>
    <summary>The dominant sequence transduction models...</summary>
    <published>2017-06-12T00:00:00Z</published>
    <link href="http://arxiv.org/abs/1706.03762v5" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/1706.03762v5" rel="related" type="application/pdf"/>
    <author>
      <name>Vaswani</name>
    </author>
  </entry>
</feed>
"""
    paper = repo._parse_xml(xml)
    assert paper is not None
    assert paper.title == "Attention Is All You Need"
    assert paper.abstract == "The dominant sequence transduction models..."
    assert paper.pdf_url == "http://arxiv.org/pdf/1706.03762v5"
    assert paper.year == 2017
    assert paper.authors == ["Vaswani"]


def test_parse_xml_no_entry(headers: dict[str, str]) -> None:
    """エントリがない場合のパーステスト"""
    repo = ArxivRepository(headers)
    xml = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"></feed>
"""
    paper = repo._parse_xml(xml)
    assert paper is None


def test_parse_xml_missing_fields(headers: dict[str, str]) -> None:
    """フィールドが欠けている場合のパーステスト"""
    repo = ArxivRepository(headers)
    xml = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/1706.03762v5</id>
    <!-- No title, summary, authors, links -->
  </entry>
</feed>
"""
    paper = repo._parse_xml(xml)
    assert paper is not None
    # 欠けているフィールドはデフォルト値またはNone
    assert paper.title == ""
    assert paper.abstract is None
    assert paper.pdf_url is None
