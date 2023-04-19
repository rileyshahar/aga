"""The core library functionality."""

from .suite import TestMetadata, SubmissionMetadata, AgaTestCase, AgaTestSuite
from .problem import Problem, problem, group
from .parameter import (
    test_case,
    param,
    test_cases,
    test_cases_params,
    test_cases_zip,
    test_cases_product,
    test_cases_singular_params,
)


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
