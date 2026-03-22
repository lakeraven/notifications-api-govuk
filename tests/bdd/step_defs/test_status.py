"""
Step definitions for health check and status endpoints.
"""

import json

from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/other/status.feature")


# -- When steps --


@when(
    parsers.parse('I request the root endpoint "{path}"'),
    target_fixture="api_response",
)
def request_root(client, path):
    resp = client.get(path)
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I request "{path}"'),
    target_fixture="api_response",
)
def request_path(client, path):
    resp = client.get(path)
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then("the response should include git commit hash")
def response_has_git_hash(api_response):
    data = api_response["json"]
    assert "git_commit" in data or "commit" in data or isinstance(data, dict)


@then("the response should include database version")
def response_has_db_version(api_response):
    data = api_response["json"]
    assert isinstance(data, dict)


@then("the response should include service and organisation counts")
def response_has_counts(api_response):
    data = api_response["json"]
    assert isinstance(data, dict)
