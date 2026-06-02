import uuid

from rdflib import ConjunctiveGraph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD

from src.ost_pyfat_api.api.v1.models import TestResult, FtrTestMetadata


class FtrClasses:
    """
    A class that implements the FAIR Testing Resource Vocabulary (FTR):
    https://ostrails.github.io/FAIR_testing_resource_vocabulary/
    """

    def __init__(self, appname: str, version: str, scm: str):
        # Define namespaces and their prefixes in a dictionary
        self.namespaces = {
            'prov': Namespace("http://www.w3.org/ns/prov#"),
            'ftr': Namespace("https://w3id.org/ftr#"),
            'sorg': Namespace("https://schema.org/"),
            'fair': Namespace("https://w3id.org/fair/principles/"),
            'xsd': Namespace("http://www.w3.org/2001/XMLSchema#"),
            'cln': Namespace("http://www.clarin.eu/ns/rubric#"),
            'sio': Namespace("http://semanticscience.org/resource/"),
            'dct': Namespace("http://purl.org/dc/terms/"),
            'dcat': Namespace("http://www.w3.org/ns/dcat#"),
            'vivo': Namespace("http://vivoweb.org/ontology/core#"),
            'dqv': Namespace("http://www.w3.org/ns/dqv#"),
            'dpv' : Namespace("https://w3id.org/dpv#"),
            'doap' : Namespace("http://usefulinc.com/ns/doap#")
        }
        # Assign as attributes
        for prefix, ns in self.namespaces.items():
            setattr(self, prefix, ns)
        #self.g = ConjunctiveGraph(identifier="http://www.example.com/")
        self.g = ConjunctiveGraph()
        self._bind_namespaces()
        # Start initialize software info
        self._initialize_software(appname, version, scm)

    def _bind_namespaces(self):
        for prefix, ns in self.namespaces.items():
            self.g.namespace_manager.bind(prefix, ns)

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

    def add_ftr_test_metadata(self, testmetadata: FtrTestMetadata) -> None:
        test_uri = URIRef(testmetadata.uri)
        self.g.add((test_uri, RDF.type, self.ftr.Test))
        self.g.add((test_uri, RDF.type, self.dcat.DataService))
        # Mandatoty fields
        self.g.add((test_uri, self.dct.creator, URIRef("https://ror.org/043c0p156")))
        self.g.add((test_uri, self.dct.identifier, test_uri))
        self.g.add((test_uri, self.dct.title, Literal(testmetadata.dcterms_title, lang="en")))
        self.g.add((test_uri, self.dct.description, Literal(testmetadata.dcterms_description, lang="en")))
        self.g.add((test_uri, self.dct.license, URIRef(testmetadata.dcterms_license)))
        self.g.add((test_uri, self.dcat.version, Literal(testmetadata.dcat_version)))

        # Optional fields
        if testmetadata.dcat_endpointDescription:
            self.g.add((test_uri, self.dcat.endpointDescription, Literal(testmetadata.dcat_endpointDescription, lang="en")))
        if testmetadata.dcat_endpointURL:
            self.g.add((test_uri, self.dcat.endpointURL, URIRef(testmetadata.dcat_endpointURL)))
        for keyword in testmetadata.dcat_keyword:
            self.g.add((test_uri, self.dcat.keyword, Literal(keyword, lang="en")))
        if testmetadata.vivo_abbreviation:
            self.g.add((test_uri, self.vivo.abbreviation, Literal(testmetadata.vivo_abbreviation)))
        if testmetadata.doap_repository:
            self.g.add((test_uri, self.doap.repository, URIRef(testmetadata.doap_repository)))
        if testmetadata.dcterms_type:
            self.g.add((test_uri, self.dct.type, URIRef(testmetadata.dcterms_type)))
        # adms:VersionNotes Literal
        # ftr:status Literal
        if testmetadata.dpv_isApplicableFor:
            self.g.add((test_uri, self.dpv.isApplicableFor, URIRef(testmetadata.dpv_isApplicableFor)))
        if testmetadata.ftr_supportedBy:
            self.g.add((test_uri, self.ftr.supportedBy, URIRef(testmetadata.ftr_supportedBy)))
        if testmetadata.ftr_applicationArea:
            self.g.add((test_uri, self.ftr.applicationArea, URIRef(testmetadata.ftr_supportedBy)))


        if testmetadata.dcat_contactPoint:
            self.g.add((test_uri, self.dcat.contactPoint, Literal(testmetadata.dcat_contactPoint)))
        if testmetadata.dcterms_creator:
            self.g.add((test_uri, self.dct.creator, Literal(testmetadata.dcterms_creator)))
        if testmetadata.rdfs_label:
            self.g.add((test_uri, self.sorg.name, Literal(testmetadata.rdfs_label, lang="en")))
        if testmetadata.dqv_inDimension:
            self.g.add((test_uri, self.dqv.inDimension, URIRef(testmetadata.dqv_inDimension)))
        for publisher in testmetadata.dcterms_publisher:
            self.g.add((test_uri, self.dct.publisher, Literal(publisher)))





    def __repr__(self) -> str:
        return self.g.serialize(format='ttl')

    def ttl(self) -> str:
        return self.g.serialize(format='ttl')

    def trix(self) -> str:
        return self.g.serialize(format='trix')

    def jsonld(self) -> str:
        # Create context from all available namespaces, so JSON-ld output uses prefixes.
        context = {prefix: str(ns) for prefix, ns in self.namespaces.items()}
        return self.g.serialize(format='json-ld', context=context, indent=2)
