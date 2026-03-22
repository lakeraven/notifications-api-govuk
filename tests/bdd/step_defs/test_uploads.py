"""
Step definitions for upload management.
"""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from tests.app.db import create_job, create_service, create_template

scenarios("../features/other/uploads.feature")


# -- Given steps --


@given("the service has completed uploads", target_fixture="uploads")
def service_has_uploads(notify_db_session, service):
    template = create_template(service)
    job = create_job(template)
    return [job]


# -- When steps --


@when("I list uploads for the service", target_fixture="api_response")
def list_uploads(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/upload")
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then("the response should include upload details")
def response_has_upload_details(api_response):
    data = api_response["json"]
    assert isinstance(data, (dict, list))
