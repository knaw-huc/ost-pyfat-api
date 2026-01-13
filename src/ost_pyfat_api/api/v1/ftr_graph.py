import uuid

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD

from src.ost_pyfat_api.api.v1.models import TestResult


class FtrClasses:
    """
    A class that implements the FAIR Testing Resource Vocabulary (FTR):
    https://ostrails.github.io/FAIR_testing_resource_vocabulary/
    """

    def __init__(self, appname: str, version: str, scm: str):
        self.prov = Namespace("http://www.w3.org/ns/prov#")
        self.ftr = Namespace("https://w3id.org/ftr#")
        self.sorg = Namespace("https://schema.org/")
        self.fair = Namespace("https://w3id.org/fair/principles/")
        self.xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
        self.cln = Namespace("http://www.clarin.eu/ns/rubric#")
        self.sio = Namespace("http://semanticscience.org/resource/")
        self.dct = Namespace("http://purl.org/dc/terms/")
        self.dcat = Namespace("http://www.w3.org/ns/dcat#")

        self.g = Graph()
        self._bind_namespaces()

        self._initialize_software(appname, version, scm)

    def _bind_namespaces(self):
        self.g.namespace_manager.bind('prov', self.prov)
        self.g.namespace_manager.bind('ftr', self.ftr)
        self.g.namespace_manager.bind('schema', self.sorg)
        self.g.namespace_manager.bind('fair', self.fair)
        self.g.namespace_manager.bind('xsd', self.xsd)
        self.g.namespace_manager.bind('cln', self.cln)
        self.g.namespace_manager.bind('sio', self.sio)
        self.g.namespace_manager.bind('dct', self.dct)
        self.g.namespace_manager.bind('dcat', self.dcat)

    def _initialize_software(self, appname: str, version: str, scm: str):
        app_software = URIRef("urn:software:6de8cc49-d44c-49c1-8ae4-a81142ed61ba")
        self.g.add((app_software, RDF.type, self.sorg.SoftwareApplication))
        self.g.add((app_software, self.sorg.url, Literal(scm)))
        self.g.add((app_software, self.sorg.softwareVersion, Literal(version, datatype=XSD.string)))
        self.g.add((app_software, self.sorg.name, Literal(appname)))

    def add_testresult(self, testresult: TestResult):
        tstresult = URIRef(f"urn:{testresult.testid}-{uuid.uuid4()}")
        self._add_testresult_triples(tstresult, testresult)

    def _add_testresult_triples(self, tstresult, testresult):
        self.g.add((tstresult, RDF.type, self.ftr.TestResult))
        self.g.add((tstresult, self.dct.identifier, Literal(tstresult)))
        self.g.add((tstresult, self.dct.title, Literal(testresult.testname, lang="en")))
        self.g.add((tstresult, self.dct.description, Literal(testresult.testdescription, lang="en")))
        self.g.add((tstresult, self.dct.license, URIRef("https://creativecommons.org/publicdomain/zero/1.0/")))
        self.g.add((tstresult, self.prov.value, Literal(testresult.result, lang="en")))
        self.g.add((tstresult, self.ftr.log, Literal(testresult.log)))
        self.g.add((tstresult, self.ftr.assessmentTarget, Literal(testresult.resource_identifier)))
        self.g.add(
            (tstresult, self.prov.generatedAtTime, Literal(testresult.gentime.isoformat(), datatype=XSD.dateTime)))
        # TODO: How can one determine TEST completion as a percentage, if a test result can only be True or False or Indeterminate?
        # Until mistery solved:
        self.g.add((tstresult, self.ftr.completion, Literal(testresult.completion, datatype=XSD.decimal)))

    def __repr__(self) -> str:
        return self.g.serialize(format='ttl')

    def ttl(self) -> str:
        return self.g.serialize(format='ttl')

    def trix(self) -> str:
        return self.g.serialize(format='trix')

    def jsonld(self) -> str:
        context = {
            "prov": "http://www.w3.org/ns/prov#",
            "ftr": "https://w3id.org/ftr#",
            "dct": "http://purl.org/dc/terms/",
            "dcat": "http://www.w3.org/ns/dcat#",
            "schema": "https://schema.org/"
        }
        return self.g.serialize(format='json-ld', context=context, indent=2)
