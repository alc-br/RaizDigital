"""
Coordinator for executing search robots.

The ``run_search`` function instantiates each configured search source,
invokes it for the given order, persists the results and returns the
list of ``SearchResult`` instances.  The default implementation runs
the sources sequentially, but you could extend it to run in
parallel using asyncio.gather for improved performance.
"""
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from ..database import async_session_maker
from ..models import SearchOrder, SearchResult

from .registrocivil import RegistroCivilSource
from .familysearch import FamilySearchSource
from .tjsp import TJSPortalSource


async def run_search(order: SearchOrder) -> List[SearchResult]:
    """Run all configured search sources for the given order.

    Instantiates each source, performs the search and stores the
    resulting ``SearchResult`` rows in the database.  Returns the list
    of results so that the caller may inspect statuses.
    """
    sources = [RegistroCivilSource(), FamilySearchSource(), TJSPortalSource()]
    results: List[SearchResult] = []
    for source in sources:
        res = await source.search(order)
        results.append(res)
    # Persist results
    async with async_session_maker() as session:  # type: AsyncSession
        for res in results:
            session.add(res)
        await session.commit()
    return results
