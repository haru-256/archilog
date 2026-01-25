import asyncio

from loguru import logger

from crawler.domain.paper import Paper
from crawler.domain.repository import PaperEnricher, PaperRetriever


class FetchRecSysPapers:
    """RecSysカンファレンスの論文情報を収集し、情報を充実させるユースケース。"""

    def __init__(
        self, paper_retriever: PaperRetriever, paper_enrichers: list[PaperEnricher]
    ) -> None:
        """FetchRecSysPapersインスタンスを初期化します。

        Args:
            paper_retriever: 論文一覧を取得するリポジトリ
            paper_enrichers: 論文情報を補完するリポジトリのリスト
        """
        self.paper_retriever = paper_retriever
        self.paper_enrichers = paper_enrichers

    async def execute(self, year: int, semaphore: asyncio.Semaphore) -> list[Paper]:
        """指定された年のRecSys論文を取得し、詳細情報を付与します。

        Args:
            year: 対象年
            semaphore: 並列実行制限用セマフォ

        Returns:
            情報が付与された論文リスト
        """
        # 1. DBLPから論文一覧を取得
        logger.info(f"Fetching RecSys {year} papers from DBLP...")
        papers = await self.paper_retriever.fetch_papers(
            conf="recsys", year=year, h=1000, sem=semaphore
        )
        logger.info(f"Fetched {len(papers)} papers from DBLP")

        # DOIのない論文は除外 (これ以降のEnrich処理でDOIが必要なため)
        papers = [p for p in papers if p.doi is not None]
        if not papers:
            return []

        # 2. 各リポジトリで情報を補完
        for paper_enricher in self.paper_enrichers:
            logger.info(f"Enriching with {paper_enricher.__class__.__name__}...")
            papers = await paper_enricher.enrich_papers(
                papers, semaphore=semaphore, overwrite=False
            )

        return papers
