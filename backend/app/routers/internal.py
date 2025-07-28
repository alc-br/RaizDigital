"""
Internal endpoints not exposed to end users.

These endpoints are intended for use by the automation robot to submit
its search results.  Access is controlled via a static API key to
ensure that only trusted processes can call these endpoints.
"""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..config import get_settings
from ..database import get_session


router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/search_results", status_code=201)
async def submit_search_result(
    result_in: schemas.SearchResultCreate,
    api_key: str = Header(None, alias="X-Api-Key"),
    session: AsyncSession = Depends(get_session),
):
    """Accept a search result from the robot.

    The request must include the header ``X-Api-Key`` matching the
    configured internal API key.  If the key is valid, the result is
    persisted to the database.
    """
    settings = get_settings()
    if api_key != settings.internal_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    # Ensure the order exists
    order = await session.get(models.SearchOrder, result_in.order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    result = models.SearchResult(
        order_id=result_in.order_id,
        source_name=result_in.source_name,
        status=models.ResultStatus(result_in.status),
        found_data_json=result_in.found_data_json,
        screenshot_path=result_in.screenshot_path,
    )
    session.add(result)
    await session.commit()
    return {"detail": "Result saved"}
