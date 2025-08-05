"""
Implementation of the TJSPortal search source.
"""
import asyncio

from .base import SearchSource
from .. import models

class TJSPortalSource(SearchSource):
    name = "TJSP Portal"

    async def search(self, order: models.SearchOrder) -> models.SearchResult:
        await asyncio.sleep(1.5) # Simula busca
        
        search_summary = (
            f"Consulta realizada no portal do Tribunal de Justiça de São Paulo "
            f"para '{order.target_name}'. O sistema retornou indisponível no momento da busca."
        )

        return models.SearchResult(
            order_id=order.id,
            source_name=self.name,
            # Simula um status de erro/indisponibilidade
            status=models.ResultStatus.SOURCE_UNAVAILABLE, 
            details=search_summary,
            found_data_json=None,
            screenshot_path="/screenshots/tjsp_unavailable.png",
        )