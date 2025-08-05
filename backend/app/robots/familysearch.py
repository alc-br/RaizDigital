"""
Implementation of the FamilySearch search source.
"""
import asyncio

from .base import SearchSource
from .. import models

class FamilySearchSource(SearchSource):
    name = "FamilySearch.org"

    async def search(self, order: models.SearchOrder) -> models.SearchResult:
        await asyncio.sleep(2)  # Simula uma busca mais demorada
        
        # Simula a criação de um relatório detalhado e um caminho para a "prova"
        search_summary = (
            f"Busca por '{order.target_name}' com data de nascimento aproximada "
            f"'{order.target_dob_approx or 'não informada'}'. "
            "Nenhum registro correspondente encontrado nos arquivos de imigrantes."
        )
        
        return models.SearchResult(
            order_id=order.id,
            source_name=self.name,
            status=models.ResultStatus.NOT_FOUND,
            details=search_summary,
            found_data_json=None,
            # Simula um link para uma imagem de prova
            screenshot_path="/screenshots/familysearch_not_found.png",
        )