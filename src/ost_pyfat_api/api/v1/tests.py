import json
import logging
from typing import Optional, Dict, Any, Set

from fastapi import APIRouter, Query, Request, Path
from fastapi.responses import JSONResponse
from pyld import jsonld

from src.ost_pyfat_api.infra import commons
from src.ost_pyfat_api.infra.commons import app_settings, API_PREFIX

USER = app_settings.USER
PASS = app_settings.PASS
ENDPOINT = app_settings.ENDPOINT
router = APIRouter(prefix=API_PREFIX)

@router.post("/tests/{id:path}", tags=["Tests"])
async def post_test(id: str = Path(..., description="Test identifier"), request: Request = None):
    logging.debug(f"Run test with id=%s", id)

    res="unknown"
    test_body = await request.body()
    js = json.loads(test_body)
    res = js["resource_identifier"]

    logging.debug(f"Run test[{id}] for resource[{res}]")

    try:
        return JSONResponse(content=foo, media_type="application/ld+json")
    except Exception as exc:
        logging.exception("Failed to run test")
        return JSONResponse(
            status_code=502,
            content={"detail": f"Failed to run test[{id}] for res[{res}]", "error": str(exc)},
        )
