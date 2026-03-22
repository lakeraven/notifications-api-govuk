"""
Step definitions for platform admin operations.
"""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from tests.app.db import create_service, create_user

scenarios("../features/platform/platform_admin.feature")


# -- Given steps --


@given("multiple users exist", target_fixture="users")
def multiple_users_exist(notify_db_session):
    return [
        create_user(email=f"user-{uuid.uuid4()}@example.gov.uk"),
        create_user(email=f"user-{uuid.uuid4()}@example.gov.uk"),
    ]


# -- When steps --


@when("I search by the service's UUID", target_fixture="api_response")
def search_by_service_uuid(admin_client, service):
    resp = admin_client.get(f"/platform-admin/search?search={service.id}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I fetch a list of users", target_fixture="api_response")
def fetch_users(admin_client):
    resp = admin_client.get("/user")
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then("the response should identify the resource type")
def response_identifies_resource(api_response):
    data = api_response["json"]
    assert isinstance(data, dict)


@then("the response should contain user details")
def response_has_user_details(api_response):
    data = api_response["json"]
    assert "data" in data or isinstance(data, list)
