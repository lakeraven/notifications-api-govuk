"""
Step definitions for v2 template retrieval, listing, and preview.

Tests run against the Flask test client using existing test fixtures.
"""

import json
import uuid

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from app.constants import EMAIL_TYPE, LETTER_TYPE, SMS_TYPE
from tests import create_service_authorization_header
from tests.app.db import (
    create_service,
    create_template,
)

# Load all scenarios from the feature file
scenarios("../features/v2_templates/get_template.feature")


# -- Fixtures --


@pytest.fixture
def test_context():
    """Mutable container for sharing state between Given/When/Then steps."""
    return {}


# -- Given steps --


@given("a service exists with a valid API key", target_fixture="service")
def a_service_with_api_key(notify_db_session):
    return create_service(service_permissions=[SMS_TYPE, EMAIL_TYPE, LETTER_TYPE])


@given(
    parsers.parse('the service has an SMS template "{name}"'),
    target_fixture="sms_template",
)
def service_has_sms_template(service, name):
    return create_template(service, template_type=SMS_TYPE, content="Hello ((name))", name=name)


@given(
    parsers.parse('the service has an email template "{name}"'),
    target_fixture="email_template",
)
def service_has_email_template(service, name):
    return create_template(
        service,
        template_type=EMAIL_TYPE,
        content="Welcome body",
        subject="Welcome",
        name=name,
    )


@given("the SMS template has been updated to version 2")
def sms_template_updated_to_v2(service, sms_template, notify_db_session):
    from app.dao.templates_dao import dao_update_template

    sms_template.content = "Updated content v2"
    dao_update_template(sms_template)


@given(parsers.parse('the SMS template has content "{content}"'), target_fixture="sms_template")
def sms_template_with_content(service, sms_template, content, notify_db_session):
    from app.dao.templates_dao import dao_update_template

    sms_template.content = content
    dao_update_template(sms_template)
    return sms_template


@given("another service has a template", target_fixture="test_context")
def another_service_has_template(notify_db_session, test_context):
    other_service = create_service(service_name="Other Template Service")
    template = create_template(other_service, template_type=SMS_TYPE, content="Other", name="Other template")
    test_context["other_template"] = template
    return test_context


# -- When steps --


@when("I request the SMS template by ID", target_fixture="api_response")
def request_sms_template_by_id(client, service, sms_template):
    resp = client.get(
        f"/v2/template/{sms_template.id}",
        headers=[create_service_authorization_header(service.id)],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(parsers.parse("I request the SMS template at version {version:d}"), target_fixture="api_response")
def request_sms_template_at_version(client, service, sms_template, version):
    resp = client.get(
        f"/v2/template/{sms_template.id}/version/{version}",
        headers=[create_service_authorization_header(service.id)],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I list all templates", target_fixture="api_response")
def list_all_templates(client, service):
    resp = client.get(
        "/v2/templates",
        headers=[create_service_authorization_header(service.id)],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(parsers.parse('I list templates with type "{type}"'), target_fixture="api_response")
def list_templates_by_type(client, service, type):
    resp = client.get(
        f"/v2/templates?type={type}",
        headers=[create_service_authorization_header(service.id)],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I preview the template with personalisation", target_fixture="api_response")
def preview_template_with_personalisation(client, service, sms_template):
    data = {"personalisation": {"name": "World"}}
    resp = client.post(
        f"/v2/template/{sms_template.id}/preview",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I request that template by ID", target_fixture="api_response")
def request_other_template_by_id(client, service, test_context):
    template = test_context["other_template"]
    resp = client.get(
        f"/v2/template/{template.id}",
        headers=[create_service_authorization_header(service.id)],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I request a template with a random UUID", target_fixture="api_response")
def request_template_random_uuid(client, service):
    resp = client.get(
        f"/v2/template/{uuid.uuid4()}",
        headers=[create_service_authorization_header(service.id)],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(parsers.parse('I request a template with ID "{id}"'), target_fixture="api_response")
def request_template_invalid_id(client, service, id):
    resp = client.get(
        f"/v2/template/{id}",
        headers=[create_service_authorization_header(service.id)],
    )
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then("the response should contain the template ID")
def response_has_template_id(api_response, sms_template):
    assert api_response["json"]["id"] == str(sms_template.id)


@then(parsers.parse('the response name should be "{name}"'))
def response_name_is(api_response, name):
    assert api_response["json"]["name"] == name


@then("the response should include body content")
def response_includes_body(api_response):
    assert api_response["json"].get("body") is not None
    assert len(api_response["json"]["body"]) > 0


@then("the response should include version number")
def response_includes_version(api_response):
    assert "version" in api_response["json"]
    assert isinstance(api_response["json"]["version"], int)


@then(parsers.parse("the response version should be {version:d}"))
def response_version_is(api_response, version):
    assert api_response["json"]["version"] == version


@then("the response should contain at least 2 templates")
def response_has_at_least_2_templates(api_response):
    templates = api_response["json"]["templates"]
    assert len(templates) >= 2


@then(parsers.parse('all returned templates should be of type "{type}"'))
def all_templates_of_type(api_response, type):
    templates = api_response["json"]["templates"]
    assert len(templates) > 0
    for t in templates:
        assert t["type"] == type


@then(parsers.parse('the preview body should contain "{text}"'))
def preview_body_contains(api_response, text):
    body = api_response["json"].get("body", "")
    assert text in body, f"Expected '{text}' in body: {body}"
