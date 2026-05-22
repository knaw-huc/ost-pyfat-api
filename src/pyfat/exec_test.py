import importlib
import logging
import os
from src.ost_pyfat_api.api.v1.models import TestResult, TestResultValue, Modality
from datetime import datetime
from src.ost_pyfat_api.infra.commons import app_settings
from src.ost_pyfat_api.utils.metrics_processor import MetricsProcessor
from importlib import resources
from saxonche import PySaxonProcessor, PyXdmValue, PySaxonApiError

preproc = MetricsProcessor(app_settings.get("metrics_file", None))

def get_variables(infra:str,res:str) -> dict:
    mod = importlib.import_module(f"src.pyfat.{infra}")
    func = getattr(mod,"get_variables")
    return func(res)

def get_xproc(proc: PySaxonProcessor):
    xpproc = proc.new_xquery_processor()
    # Load our namespaces into the XSLT processor:
    for k, v in preproc.get_nspace_map().items():
        xpproc.declare_namespace(k, v)
    xpproc.set_cwd(os.getcwd())
    return xpproc

def evaluate(tst_id: str, resource_identifier: str) -> TestResult:
    logging.info(f"Start executing test with ID: [{tst_id}] on resource_identifier: [{resource_identifier}].")

    with PySaxonProcessor(license=False) as proc:
        logging.info(f"Processor: {proc.version}")

        preproc = MetricsProcessor(app_settings.get("metrics_file", None))
        xslt_result = None  # Set to indeterminate
        infra = preproc.get_infrastructure()
        if infra==None:
            infra="clarin"
        logging.info(f"Infrastructure: {infra}")
        vars = get_variables(infra,resource_identifier)
        logging.info(f"Variables: {vars}")
        metric_test = preproc.get_metrictest_by_testid(tst_id)

        #- metric_test_identifier: CLFIP-F2-01M-1
        # metric_test_name: "Facet coverage score of the used CMD profile is larger than .2"
        # metric_test_score: 1
        # metric_test_requirements:
        #   - test: "xpath:xs:decimal(doc(concat('http://localhost:8000/proxy?accept=application/xml&amp;url=',encode-for-uri(concat('https://curation.clarin.eu/curate?url-input=',encode-for-uri(concat('https://catalog.clarin.eu/ds/ComponentRegistry/rest/registry/1.x/profiles/',//cmd:MdProfile,'/xsd'))))))//cmdProfileReport/facetReport/@score) > 0.2"
        #     modality: all
# {'metric_test_identifier': 'CLFIP-F1-01M-2', 'metric_test_name': 'Check to see if the selflink is a doi', 'metric_test_score': 0.5, 'metric_test_requirements': [{'test': "xpath:starts-with(//cmd:MdSelfLink, 'doi:')", 'modality': 'all'}]}
        log = f'\t=> Testing: {metric_test["metric_test_name"]}'
        metric_test_requirement = metric_test["metric_test_requirements"][0]
        if metric_test_requirement["test"].startswith("xpath:"):
            # In Xpath handler...
            xpproc = get_xproc(proc)

            cmdi=None
            if "CMDI" in vars:
                 cmdi = proc.parse_xml(xml_text=vars["CMDI"])
            if cmdi:
                xpproc.set_context(xdm_item=cmdi)
            #else: 
            #    TODO: fail!
            xpath_tst = metric_test_requirement["test"].split("xpath:", 1)[1]
            logging.info(f'\t\t=> Test XPath: {xpath_tst}, modality: {metric_test_requirement["modality"]}')
            log = log + f'Test modality = {metric_test_requirement["modality"]}'

            var_declare_list = []
            var_declare_str = ''
            if metric_test_requirement.get("variables", False):
                for variable in metric_test_requirement.get("variables"):
                    var_name = variable.split("=", 1)[0]
                    var_val = variable.split("=", 1)[1]
                    logging.debug(f'\t\t=> Var name={var_name}, value={var_val}')
                    varproc = proc.new_xpath_processor()
                    var_val = var_val.replace("$RECORDPATH", os.path.basename(str(cmdi_record_path)))  # TODO: $RECORDPATH parameter meaning must be known by the caller. Find a way to make this generic.
                    # Or create an external parameter for it:
                    # if '$RECORDPATH' in var_val:
                    # varproc.declare_variable('RECORDPATH')
                    # varproc.set_parameter('RECORDPATH', proc.make_string_value(os.path.basename(cmdi_record_path), encoding="UTF-8"))
                    json_result = varproc.evaluate(var_val)
                    xpproc.set_parameter(var_name, json_result)
                    var_declare_list.append(f"declare variable ${var_name} external")
                var_declare_str = '; '.join(var_declare_list) + ";"
                # Add declarations to the output Log:
                if var_declare_str: log = log + ", " + var_declare_str

            logging.info(f"\t\t=> Setting Xquery content on procc: {var_declare_str} {xpath_tst}")
            xpproc.set_query_content(f"{var_declare_str} {xpath_tst}")

            # Run Xpath query
            try:  # Beware: Looks like the parser might still print a java.io.IOException, that cannot be caught: FODC0002  I/O error reported by XML parser processing https://curation.clarin.eu/download/profile/clarin_eu_cr1_p_1650879720846. Caused by java.io.IOException: Server returned HTTP response code: 500 for URL: (...)
                xslt_result = xpproc.run_query_to_value(encoding="UTF-8")
            except (RuntimeError, BaseException, PySaxonApiError) as err:
                logging.error(f"\t\tError executing Xpath test: {xpath_tst}: {err}")
                xslt_result = None

            for item in xslt_result:
                print("xslt_result: "+item.string_value)

            if all(isinstance(item, PyXdmValue) and item.string_value in ["true", "false"] for item in xslt_result):
                print("All items in xslt_result are boolean strings.")

            if xslt_result and all(hasattr(item, 'string_value') and item.string_value in ["true", "false"] for item in xslt_result):

                if metric_test_requirement["modality"] == Modality.ANY:
                    # print("Modality is ANY, checking if any item is true.")
                    tst_result = TestResultValue.PASS.value if any(getattr(res, 'boolean_value', True) for res in xslt_result) else TestResultValue.FAIL.value
                elif metric_test_requirement["modality"] == Modality.ALL:
                    # print("Modality is ALL, checking if all items are true.")
                    tst_result = TestResultValue.PASS.value if all(getattr(res, 'boolean_value', True) for res in xslt_result) else TestResultValue.FAIL.value
                else:
                    print(f"Unknown modality: {metric_test_requirement['modality']}. Setting result to INDETERMINATE.")
                    tst_result = TestResultValue.INDETERMINATE.value
            else: #TODO: Handle non-boolean results (e.g: numeric scores, Indeterminate, etc.)
                logging.warning(f"Test identifier '{tst_id}' did NOT yield boolean results! Setting result to INDETERMINATE.")
                tst_result = TestResultValue.INDETERMINATE.value

        return TestResult(
            result=tst_result,
            completion=100,
            testid=tst_id,
            metricid=tst_id.rsplit("-", 1)[0],
            testdescription=metric_test_requirement["test"],
            testname=metric_test["metric_test_name"],
            log=log,
            resource_identifier=resource_identifier,
            gentime=datetime.now()
        )

def main():
    for cmdi in resources.files("resources.cmdi").iterdir():
        evaluate("dummy-test-id", str(cmdi))

if __name__ == '__main__':
    main()