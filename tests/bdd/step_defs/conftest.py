"""
Shared step definitions available to all BDD tests.

pytest-bdd step definitions in conftest.py are automatically discovered.
"""

import uuid

import pytest
from pytest_bdd import given, parsers, then, when

from tests.app.db import (
    create_api_key,
    create_notification,
    create_service,
    create_template,
    create_user,
)


# -- Common Given steps --


@given("a platform admin user exists", target_fixture="admin_user")
def a_platform_admin_user(notify_db_session):
    return create_user(email="admin@digital.cabinet-office.gov.uk", platform_admin=True)


@given("a service exists", target_fixture="service")
def a_service_exists(notify_db_session):
    return create_service()


@given(parsers.parse('a service "{name}" exists'), target_fixture="service")
def a_named_service_exists(notify_db_session, name):
    return create_service(service_name=name)


@given("a service exists with an admin user", target_fixture="service")
def a_service_with_admin(notify_db_session):
    return create_service()


@given("a user exists", target_fixture="user")
def a_user_exists(notify_db_session):
    return create_user(email=f"user-{uuid.uuid4()}@example.gov.uk")


@given("a new user exists", target_fixture="new_user")
def a_new_user_exists(notify_db_session):
    return create_user(email=f"newuser-{uuid.uuid4()}@example.gov.uk")


# -- Common Then steps --


@then(parsers.parse("the response status code should be {status_code:d}"))
def response_status_code(api_response, status_code):
    assert api_response["status_code"] == status_code, (
        f"Expected {status_code}, got {api_response['status_code']}: {api_response.get('json')}"
    )


@then("the response should contain a notification ID")
def response_has_notification_id(api_response):
    assert "id" in api_response["json"]
    assert api_response["json"]["id"] is not None


@then(parsers.parse('the response reference should be "{reference}"'))
def response_reference_is(api_response, reference):
    assert api_response["json"]["reference"] == reference


@then("the response reference should be null")
def response_reference_is_null(api_response):
    assert api_response["json"]["reference"] is None


@then("the response should contain a URI for the notification")
def response_has_uri(api_response):
    assert "uri" in api_response["json"]


@then("the response should include template details")
def response_has_template(api_response):
    assert "template" in api_response["json"]
    assert "id" in api_response["json"]["template"]
    assert "version" in api_response["json"]["template"]


@then(parsers.parse('the response body should contain "{text}"'))
def response_body_contains(api_response, text):
    body = api_response["json"].get("content", {}).get("body", "")
    assert text in body, f"Expected '{text}' in body: {body}"


@then(parsers.parse('the response type should be "{notification_type}"'))
def response_type_is(api_response, notification_type):
    assert api_response["json"]["type"] == notification_type


@then("the response should include created_at timestamp")
def response_has_created_at(api_response):
    assert api_response["json"].get("created_at") is not None


@then(parsers.parse('the response error should mention "{text}"'))
def response_error_mentions(api_response, text):
    json_data = api_response["json"]
    errors = json_data.get("errors", [])
    error_text = str(errors)
    assert text.lower() in error_text.lower(), f"Expected '{text}' in errors: {errors}"
