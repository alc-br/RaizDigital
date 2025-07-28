"""
Base class for search sources used by the automation robot.

Each source must implement the ``search`` method which accepts a
``SearchOrder`` and returns a ``SearchResult`` instance reflecting
whether the certificate was found.  Sources should handle their own
errors internally and return an appropriate status.
"""
import abc
from .. import models


class SearchSource(abc.ABC):
    """Abstract base class for a search source."""

    name: str

    @abc.abstractmethod
    async def search(self, order: models.SearchOrder) -> models.SearchResult:
        """Search for the certificate corresponding to the given order.

        Subclasses must implement this method and should return a
        ``SearchResult`` instance describing the outcome.
        """
        raise NotImplementedError
