import datetime
from dataclasses import dataclass
from enum import unique, StrEnum, auto


@unique
class TestResultValue(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    INDETERMINATE = "indeterminate"


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
