import logging
from typing import Optional

from fastapi import APIRouter
from fastapi import Header
from fastapi.responses import JSONResponse, PlainTextResponse

from src.ost_pyfat_api.api.v1.ftr_graph import FtrClasses
from src.ost_pyfat_api.api.v1.models import TestResult, TestResultValue, FtrTestMetadata, ResourceIdentifierRequest
from src.ost_pyfat_api.infra.commons import app_settings, API_PREFIX
from src.ost_pyfat_api.utils.metrics_processor import MetricsProcessor


USER = app_settings.USER
PASS = app_settings.PASS
ENDPOINT = app_settings.ENDPOINT
router = APIRouter(prefix=API_PREFIX)

preproc = MetricsProcessor(app_settings.get("metrics_file", None))
@router.get("/metrics/", tags=["Metrics"], summary="Get all metrics", description="Returns metadata for all available metrics.",
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
async def get_all_metrics(accept: Optional[str] = Header(None)):

    ftr_output = FtrClasses(appname="pyFAT", version="0.1.4", scm="https://github.com/knaw-huc/ost-pyfat-api")

    for tst_id in preproc.all_test_ids():
        metric_test = preproc.get_metrictest_by_testid(tst_id)
        # Create FTRTest metadata
        test_metadata = FtrTestMetadata(
            uri=f"urn:pyFATtest:{tst_id}",
            dcterms_identifier=f"urn:fairtestoutput:{tst_id}",
            dcterms_title=metric_test.get("metric_test_name", None),
            dcterms_description=metric_test['metric_test_requirements'][0]['test'],
            dcterms_license="https://creativecommons.org/publicdomain/zero/1.0/",
            dcat_version=preproc.get_metrics_version()
        )

        ftr_output.add_ftr_test_metadata(test_metadata)

    try:
        if accept and "text/turtle" in accept:
            # Serialize to Turtle
            return PlainTextResponse(content=ftr_output.ttl(), media_type="text/turtle")
        else:
            # Default JSON-LD
            return PlainTextResponse(content=ftr_output.jsonld(), media_type="application/ld+json")

    except Exception as exc:
        logging.exception("Failed to get al metrics metadata")
        return JSONResponse(
            status_code=502,
            content={"detail": f"Failed to get metadata for [{tst_id}]", "Error": str(exc)},
        )