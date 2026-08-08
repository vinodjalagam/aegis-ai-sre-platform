from fastapi import APIRouter, Depends, Query

from app.core.security.dependencies import get_current_user_id
from app.modules.metrics.client import PrometheusClient
from app.shared.responses.success import success_response

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
)

client = PrometheusClient()


@router.get("/query")
async def query_metrics(
    query: str = Query(...),
    _: str = Depends(get_current_user_id),
):
    result = client.query(query)
    return success_response(result)