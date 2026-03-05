import datetime
from dataclasses import dataclass, field
from enum import unique, StrEnum, auto
from typing import List, Optional


@unique
class TestResultValue(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    INDETERMINATE = "indeterminate"

@unique
class Modality(StrEnum):
    ANY = auto()
    ALL = auto()

@dataclass
class TestResult:
    result: TestResultValue
    completion: float
    testid: str
    metricid: str
    testdescription: str
    testname: str
    log: str
    resource_identifier: str
    gentime: datetime.date


@dataclass
class FtrTestMetadata:
    uri: str  # The subject URI, e.g., "https://w3id.org/foops/test/FIND2"
    dcterms_identifier: str
    dcterms_title: str
    dcterms_description: str

    dcat_endpointDescription: Optional[str] = None
    dcat_endpointURL: Optional[str] = None
    dcat_keyword: List[str] = field(default_factory=list)
    vivo_abbreviation: Optional[str] = None
    doap_repository: Optional[str] = None
    dcterms_type: Optional[str] = None
    dcterms_license: str = "https://creativecommons.org/publicdomain/zero/1.0/"
    dcat_version: str = ''
    adms_versionNotes: Optional[str] = None
    ftr_status: Optional[str] = None
    dpv_isApplicableFor: Optional[str] = None
    ftr_supportedBy: Optional[str] = None
    ftr_applicationArea: Optional[str] = None

    dcat_contactPoint: Optional[str] = None
    dcterms_creator: Optional[str] = None
    rdfs_label: Optional[str] = None
    dqv_inDimension: Optional[str] = None
    dcterms_publisher: List[str] = field(default_factory=list)



@dataclass
class FtrMetric:
    dcterms_identifier: str
    dcterms_title: str
    dcterms_description: str
    dcat_keyword: List[str] = field(default_factory=list)
    vivo_abbreviation: Optional[str] = None
    dcat_landingPage: Optional[str] = None
    dcat_version: str = ''
    ftr_status: Optional[str] = None
    dpv_isApplicableFor: Optional[str] = None
    ftr_supportedBy: Optional[str] = None
    ftr_applicationArea: Optional[str] = None
    ftr_hasPositiveValidation: str = ''
    ftr_hasNegativeValidation: str = ''
