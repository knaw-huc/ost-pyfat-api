import logging
from typing import Optional

from fastapi import APIRouter
from fastapi import Header
from fastapi.responses import JSONResponse, PlainTextResponse

from src.ost_pyfat_api.api.v1.ftr_graph import FtrClasses
from src.ost_pyfat_api.infra.commons import app_settings, API_PREFIX
from src.ost_pyfat_api.utils.metrics_processor import MetricsProcessor


USER = app_settings.USER
PASS = app_settings.PASS
ENDPOINT = app_settings.ENDPOINT
router = APIRouter(prefix=API_PREFIX)

preproc = MetricsProcessor(app_settings.get("metrics_file", None))


@router.get("/guidance/metrics", tags=["Guidance"], summary="Get all Metric guidance", description="Returns all guidance objects for all available metrics. Use the Accept header to select the response format.",
            responses={
                200: {
                    "content": {
                        "application/ld+json": {},
                        "text/turtle": {},
                    },
                    "description": "OK",
                },
                404: {"description": "Not Found"}
            })

async def get_all_metric_guidance(accept: Optional[str] = Header(None, description="Content type to return. Supported values: 'text/turtle', 'application/ld+json' (default)")):
    """
    Get all guidance objects for all metrics and return them in the requested format.
    Supports content negotiation for Turtle and JSON-LD formats.
    """
    try:
        # Create FtrClasses instance
        ftr_output = FtrClasses(appname="pyFAT", version="0.1.4", scm="https://github.com/knaw-huc/ost-pyfat-api")
        guidance_dict = preproc.get_all_metric_guidance()
        for metric_id, guidance_text in guidance_dict.items():
            ftr_output.add_guidance_triples(metric_id, preproc)

        # Content negotiation: check accept header and serialize accordingly
        if accept and "text/turtle" in accept:
            # Serialize to Turtle
            return PlainTextResponse(content=ftr_output.ttl(), media_type="text/turtle")
        else:
            # Default JSON-LD
            return PlainTextResponse(content=ftr_output.jsonld(), media_type="application/ld+json")

    except Exception as exc:
        logging.exception("Failed to get all guidance objects")
        return JSONResponse(
            status_code=502,
            content={"detail": "Failed to get guidance objects", "Error": str(exc)},
        )

@router.get("/guidance/tests", tags=["Guidance"], summary="Get all Test guidance", description="Returns all guidance objects for all available tests. Use the Accept header to select the response format.",
            responses={
                200: {
                    "content": {
                        "application/ld+json": {},
                        "text/turtle": {},
                    },
                    "description": "OK",
                },
                404: {"description": "Not Found"}
            })

async def get_all_test_guidance(accept: Optional[str] = Header(None, description="Content type to return. Supported values: 'text/turtle', 'application/ld+json' (default)")):
    """
    Get all guidance objects for all metrics and return them in the requested format.
    Supports content negotiation for Turtle and JSON-LD formats.
    """
    try:
        # Create FtrClasses instance
        ftr_output = FtrClasses(appname="pyFAT", version="0.1.4", scm="https://github.com/knaw-huc/ost-pyfat-api")
        guidance_dict = preproc.get_all_test_guidance()
        for metric_test_id, guidance_text in guidance_dict.items():
            ftr_output.add_guidance_triples(metric_test_id, preproc)

        # Content negotiation: check accept header and serialize accordingly
        if accept and "text/turtle" in accept:
            # Serialize to Turtle
            return PlainTextResponse(content=ftr_output.ttl(), media_type="text/turtle")
        else:
            # Default JSON-LD
            return PlainTextResponse(content=ftr_output.jsonld(), media_type="application/ld+json")

    except Exception as exc:
        logging.exception("Failed to get all guidance objects")
        return JSONResponse(
            status_code=502,
            content={"detail": "Failed to get guidance objects", "Error": str(exc)},
        )