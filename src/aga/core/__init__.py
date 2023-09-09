"""The core library functionality."""

from .parameter import (
    param,
    test_case,
    test_cases,
    test_cases_params,
    test_cases_product,
    test_cases_singular_params,
    test_cases_zip,
)
from .problem import Problem, group, problem
from .suite import AgaTestCase, AgaTestSuite, SubmissionMetadata, TestMetadata

__all__ = [
    "TestMetadata",
    "SubmissionMetadata",
    "AgaTestCase",
    "AgaTestSuite",
    "Problem",
    "problem",
    "group",
    "test_case",
    "test_cases",
    "param",
    "test_cases_params",
    "test_cases_zip",
    "test_cases_product",
    "test_cases_singular_params",
]
