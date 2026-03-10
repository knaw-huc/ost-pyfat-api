import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Path
from fastapi import Header
from fastapi.responses import JSONResponse

from src.ost_pyfat_api.api.v1.ftr_graph import FtrClasses
from src.ost_pyfat_api.api.v1.models import TestResult, TestResultValue
from src.ost_pyfat_api.infra.commons import app_settings, API_PREFIX

import requests

USER = app_settings.USER
PASS = app_settings.PASS
ENDPOINT = app_settings.ENDPOINT
router = APIRouter(prefix=API_PREFIX)

# TODO: I think we need a concrete test endpoint for each test. These will then show up in the OpenAPI docs. Suppliyng the TestID as a path parameter here 'hiddes' the available testID's and involves additional checking.
@router.post("/tests/{id:path}", tags=["Tests"], responses={
    200: {
        "content": {
            "application/ld+json": {},
            "text/turtle": {},
        },
        "description": "Successful Response",
    }
})
async def post_test(
        id: str = Path(..., description="Test identifier"),
        request: Request = None,
        accept: Optional[str] = Header(None)
):
    logging.debug(f"Run test with id=%s", id)

    test_body = await request.body()
    js = json.loads(test_body)
    res = js["resource_identifier"]

    logging.debug(f"Run test[%s] for resource[%s]",id,res)

    data = {"resource_identifier": res}
    # Execute TEST logic here ...

    logging.debug(f'res: %s', res)

    headers = {'Accept': 'application/x-cmdi+xml'}
    url = f'http://hdl.handle.net/{res}'
    logging.debug(f'url: %s', url)
    response = requests.post(url, headers=headers, timeout=10)
    logging.info(f"Status: %s",response.status_code)
    logging.debug(f"Body preview: %s", response.text)

# indien geen cmdi in reponse dan None
# anders vlo facetten:
    url = res.replace(':','_58_').replace('/','_47_')
    vlo = 'https://beta-vlo.clarin.eu/api/records/'
    logging.debug(f'url 2: {vlo}{url}')
    headers = {'Accept': 'application/json'}
    response = requests.get(f'{vlo}{url}', timeout=10)
    logging.info("Status 2: %s", response.status_code)
    logging.debug("Body preview 2: %s", response.text)
    res_json = json.loads(response.text)



    dummy_test_result = TestResult(
        result=res_json, # TestResultValue.PASS.value,
        completion=100,
        testid=id,
        metricid=id.rsplit("-", 1)[0],
        testdescription="Dummy test description",
        testname="DummyTest Name",
        log="No issues found.",
        resource_identifier=res,
        gentime=datetime.now()
    )

    ftr_output = FtrClasses(appname="pyFAT", version="0.1.4", scm="https://github.com/knaw-huc/ost-pyfat-api")
    ftr_output.add_testresult(dummy_test_result)

    try:
        if accept and "text/turtle" in accept:
            # Serialize to Turtle
            return JSONResponse(content=ftr_output.ttl(), media_type="text/turtle")
        else:
            # Default JSON-LD
            return JSONResponse(content=ftr_output.jsonld(), media_type="application/ld+json")

    except Exception as exc:
        logging.exception("Failed to run test")
        return JSONResponse(
            status_code=502,
            content={"detail": f"Failed to run test[{id}] for res[{res}]", "error": str(exc)},
        )
