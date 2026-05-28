import json
import logging
from typing import Optional

from fastapi import APIRouter, Request, Path, Body
from fastapi import Header
from fastapi.responses import Response, JSONResponse, PlainTextResponse

from src.ost_pyfat_api.api.v1.ftr_graph import FtrClasses
from src.ost_pyfat_api.api.v1.models import TestResult, TestResultValue, FtrTestMetadata, ResourceIdentifierRequest
from src.ost_pyfat_api.infra.commons import app_settings, API_PREFIX
from src.ost_pyfat_api.utils.metrics_processor import MetricsProcessor
from src.pyfat.exec_test import evaluate

USER = app_settings.USER
PASS = app_settings.PASS
ENDPOINT = app_settings.ENDPOINT
router = APIRouter(prefix=API_PREFIX)

preproc = MetricsProcessor(app_settings.get("metrics_file", None))

@router.post("/test/assess/{tst_id:path}", tags=["Tests"], responses={
    200: {
        "content": {
            "application/ld+json": {},
            "text/turtle": {},
            "application/xml": {},
        },
        "description": "Successful Response",
    },
    404: {"description": "Not Found"}
}, summary="Run a specific test on a resource identifier", description="Runs the specified test on the provided resource identifier and returns the result following the FTR specification.")
async def post_test(
        request_body: ResourceIdentifierRequest = Body(..., description="JSON object containing the resource identifier to test."),
        tst_id: str = Path(..., description="Identifier of the test to run."),
        accept: Optional[str] = Header(None)
):
    try:
        resource_identifier = request_body.resource_identifier
        logging.debug(f"Run test with test id={tst_id} and resource {resource_identifier}")


        preproc.get_metrics_tests_id_map()
        if not preproc.is_valid_testid(tst_id):
            logging.error(f"Test ID[{tst_id}] not found in preprocessor metrics tests map.")
            return JSONResponse(
                status_code=404,
                content={"detail": f"Test ID[{tst_id}] not found."},
            )

        test_result = evaluate(tst_id, resource_identifier)

        ftr_output = FtrClasses(appname="pyFAT", version="0.1.4", scm="https://github.com/knaw-huc/ost-pyfat-api")
        ftr_output.add_testresult(test_result)

        if accept and "text/turtle" in accept:
            # Serialize to Turtle
            return PlainTextResponse(content=ftr_output.ttl(), media_type="text/turtle")
        else: 
            if accept and "application/xml" in accept:
                # Serialize to Trix
                return Response(content=ftr_output.trix(), media_type="application/xml")
            else:
                # Default JSON-LD
                return Response(content=ftr_output.jsonld(), media_type="application/ld+json")

    except Exception as exc:
        logging.exception("Failed to run test")
        return JSONResponse(
            status_code=502,
            content={"detail": f"Failed to run test[{tst_id}] for res[{resource_identifier}]", "error": str(exc)},
        )


@router.get("/tests/", tags=["Tests"], summary="Get all tests", description="Returns metadata for all available tests.",
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
async def get_all_tests(accept: Optional[str] = Header(None)):

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
        logging.exception("Failed to get test metadata")
        return JSONResponse(
            status_code=502,
            content={"detail": f"Failed to get metadata for [{tst_id}]", "Error": str(exc)},
        )


@router.get(
    "/tests/{tst_id}",
    tags=["Tests"],
    summary="Get FTR test metadata by test-ID.",
    description="Returns test metadata for a specific test following the FTR specification.",
    responses={
        200: {
            "content": {
                "application/ld+json": {},
                "text/turtle": {},
            },
            "description": "OK",
        },
        404: {"description": "Not Found"}
    }
)
async def get_test_by_id(tst_id: str, accept: Optional[str] = Header(None)):
    if not preproc.is_valid_testid(tst_id):
        logging.error(f"Test ID[{tst_id}] not found in preprocessor metrics tests map.")
        return JSONResponse(
            status_code=404,
            content={"detail": f"Test ID[{tst_id}] not found."},
        )

    metric_test = preproc.get_metrictest_by_testid(tst_id)

    # Create FTRTest metadata response
    test_metadata = FtrTestMetadata(
        uri=f"urn:pyFATtest:{tst_id}",
        dcterms_identifier=f"urn:fairtestoutput:{tst_id}",
        dcterms_title=metric_test.get("metric_test_name", None),
        dcterms_description=metric_test['metric_test_requirements'][0]['test'],
        dcterms_license="https://creativecommons.org/publicdomain/zero/1.0/",
        dcat_version=preproc.get_metrics_version()
    )

    ftr_output = FtrClasses(appname="pyFAT", version="0.1.4", scm="https://github.com/knaw-huc/ost-pyfat-api")
    ftr_output.add_ftr_test_metadata(test_metadata)

    try:
        if accept and "text/turtle" in accept:
            # Serialize to Turtle
            return PlainTextResponse(content=ftr_output.ttl(), media_type="text/turtle")
        else:
            # Default JSON-LD
            return PlainTextResponse(content=ftr_output.jsonld(), media_type="application/ld+json")

    except Exception as exc:
        logging.exception("Failed to get test metadata")
        return JSONResponse(
            status_code=502,
            content={"detail": f"Failed to get metadata for [{tst_id}]", "Error": str(exc)},
        )
