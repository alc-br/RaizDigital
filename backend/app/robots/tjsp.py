"""
Implementation of the TJSPortal search source.

This source would normally scrape the São Paulo Court portal for civil
certificates.  For demonstration purposes it returns a simulated
negative result.  To implement scraping, use Selenium to interact
with forms and parse the results.
"""
import asyncio

from .base import SearchSource
from .. import models


class TJSPortalSource(SearchSource):
    name = "TJSP Portal"

    async def search(self, order: models.SearchOrder) -> models.SearchResult:
        # Simulate delay
        await asyncio.sleep(1)
        # Simulate no result found
        return models.SearchResult(
            order_id=order.id,
            source_name=self.name,
            status=models.ResultStatus.NOT_FOUND,
            found_data_json=None,
            screenshot_path=None,
        )
