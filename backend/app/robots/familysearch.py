"""
Implementation of the FamilySearch search source.

Normally this class would automate interactions with FamilySearch.org,
but here it returns a simulated negative result.  In a real
deployment, you would implement the scraping logic using Selenium
similar to other sources, paying attention to login, search forms and
pagination.
"""
import asyncio

from .base import SearchSource
from .. import models


class FamilySearchSource(SearchSource):
    name = "FamilySearch.org"

    async def search(self, order: models.SearchOrder) -> models.SearchResult:
        # Simulate network delay
        await asyncio.sleep(1)
        # Simulate no result found
        return models.SearchResult(
            order_id=order.id,
            source_name=self.name,
            status=models.ResultStatus.NOT_FOUND,
            found_data_json=None,
            screenshot_path=None,
        )
