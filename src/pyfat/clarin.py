import json
import logging
import requests
import idutils
from typing import Optional


def get_actionable_pid_url(pid: str) -> Optional[str]:
    id_scheme = idutils.detect_identifier_schemes(pid)
    if not id_scheme:
        logger.warn(f"Identifier scheme not recognised: {pid}")
        return None
    pidx = idutils.to_url(pid, id_scheme[0])
    if pidx.lower().startswith("http:") and pid.lower().startswith("https:"):
        pidx = pidx.lower().replace("http:", "https:")
    return pidx

def get_variables(res:str) -> dict:
    vars = {}
    
    # CMDI

    headers = {'Accept': 'application/x-cmdi+xml'}
    # TODO: snif a res to see how complete the url is
    url = get_actionable_pid_url(res)
    logging.debug(f'url: %s', url)
    response = requests.get(url, headers=headers, timeout=10)
    logging.info(f"Status: %s",response.status_code)
    if response.status_code == 200:
        logging.debug(f"Body preview: %s", response.text)
        vars['CMDI'] = response.text
        # TODO: if CMDI 1.1 upgrade to CMDI 1.2
        # no CMDI, set CMDI to None

    # VLO values
    url = res.replace(':','_58_').replace('/','_47_')
    vlo = 'https://beta-vlo.clarin.eu/api/records/'
    logging.debug(f'url 2: {vlo}{url}')
    headers = {'Accept': 'application/json'}
    response = requests.get(f'{vlo}{url}', timeout=10)
    logging.info("Status 2: %s", response.status_code)
    if response.status_code == 200:
        logging.debug("Body preview 2: %s", response.text)
        res_json = json.loads(response.text)
        vars['VLO_values'] = response.text

    # VLO facets
    # anders vlo facetten:
    url = res.replace(':','_58_').replace('/','_47_')
    vlo = 'https://beta-vlo.clarin.eu/api/facets'
    logging.debug(f'url 3: {vlo}?q=id:{url}')
    headers = {'Accept': 'application/json'}
    response = requests.get(f'{vlo}{url}', timeout=10)
    logging.info("Status 3: %s", response.status_code)
    if response.status_code == 200:
        logging.debug("Body preview 3: %s", response.text)
        res_json = json.loads(response.text)
        vars['VLO_facets'] = response.text

    return vars





