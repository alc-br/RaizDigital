"""
Implementation of the RegistroCivil search source.

This class would normally use Selenium and BeautifulSoup to scrape
registrocivil.org.br for a certificate matching the order details.
Because scraping external sites is not possible in this environment, a
placeholder implementation is provided which returns a simulated
successful search for demonstration purposes.
"""
import asyncio
from typing import Optional

from .base import SearchSource
from .. import models


class RegistroCivilSource(SearchSource):
    name = "RegistroCivil.org.br"

    async def search(self, order: models.SearchOrder) -> models.SearchResult:
        # Simulate a network delay
        await asyncio.sleep(1)
        # Simulate a found result for demonstration
        found_data = {
            "cartorio": "Cartório Central",
            "livro": "Livro 1",
            "folha": "Folha 23",
        }
        result = models.SearchResult(
            order_id=order.id,
            source_name=self.name,
            status=models.ResultStatus.FOUND,
            found_data_json=str(found_data),
            screenshot_path=None,
        )
        return result
