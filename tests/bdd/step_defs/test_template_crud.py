"""
Step definitions for template CRUD operations (admin API).

Tests run against the Flask test client using existing test fixtures.
"""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from app.constants import EMAIL_TYPE, LETTER_TYPE, SMS_TYPE
from app.dao.templates_dao import dao_update_template
from tests.app.db import (
    create_service,
    create_template,
)

# Load all scenarios from the feature file
scenarios("../features/templates/template_crud.feature")


# -- Given steps --


@given("the service has letter permissions", target_fixture="service")
def service_with_letter_permissions(service):
    from app.dao.service_permissions_dao import dao_add_service_permission

    dao_add_service_permission(service.id, LETTER_TYPE)
    return service


@given("an SMS template exists for the service", target_fixture="template")
def an_sms_template_exists(service, notify_db_session):
    return create_template(service, template_type=SMS_TYPE, content="Hello ((name))")


@given("the service has 3 templates", target_fixture="test_context")
def service_has_3_templates(service, test_context, notify_db_session):
    templates = []
    for i in range(3):
        t = create_template(
            service,
            template_type=SMS_TYPE,
            content=f"Template {i} content",
            template_name=f"Template {i}",
        )
        templates.append(t)
    test_context["templates"] = templates
    return test_context


@given(
    parsers.parse('an SMS template exists with content "{content}"'),
    target_fixture="template",
)
def sms_template_with_content(service, content, notify_db_session):
    return create_template(service, template_type=SMS_TYPE, content=content)


@given("a template has been updated 3 times", target_fixture="template")
def template_updated_3_times(service, notify_db_session):
    template = create_template(service, template_type=SMS_TYPE, content="Version 1")
    for i in range(2, 5):
        template.content = f"Version {i}"
        dao_update_template(template)
    return template


@given("a template has been updated", target_fixture="template")
def template_updated_once(service, notify_db_session, test_context):
    template = create_template(service, template_type=SMS_TYPE, content="Original content")
    test_context["original_content"] = "Original content"
    template.content = "Updated content"
    dao_update_template(template)
    return template


# -- When steps --


@when(
    parsers.parse('I create an SMS template named "{name}" with content "{content}"'),
    target_fixture="api_response",
)
def create_sms_template(admin_client, service, name, content):
    data = {
        "name": name,
        "template_type": SMS_TYPE,
        "content": content,
        "service": str(service.id),
        "created_by": str(service.created_by.id),
    }
    resp = admin_client.post(f"/service/{service.id}/template", data=data)
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I create an email template named "{name}" with subject "{subject}" and content "{content}"'),
    target_fixture="api_response",
)
def create_email_template(admin_client, service, name, subject, content):
    data = {
        "name": name,
        "template_type": EMAIL_TYPE,
        "content": content,
        "subject": subject,
        "service": str(service.id),
        "created_by": str(service.created_by.id),
    }
    resp = admin_client.post(f"/service/{service.id}/template", data=data)
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I create a letter template named "{name}" with content "{content}"'),
    target_fixture="api_response",
)
def create_letter_template(admin_client, service, name, content):
    data = {
        "name": name,
        "template_type": LETTER_TYPE,
        "content": content,
        "subject": "Letter subject",
        "service": str(service.id),
        "created_by": str(service.created_by.id),
    }
    resp = admin_client.post(f"/service/{service.id}/template", data=data)
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the template by ID", target_fixture="api_response")
def get_template_by_id(admin_client, service, template):
    resp = admin_client.get(f"/service/{service.id}/template/{template.id}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I list all templates for the service", target_fixture="api_response")
def list_all_templates(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/template")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I update the template content to "{content}"'),
    target_fixture="api_response",
)
def update_template_content(admin_client, service, template, content, test_context):
    test_context["original_version"] = template.version
    data = {
        "content": content,
        "created_by": str(service.created_by.id),
    }
    resp = admin_client.post(f"/service/{service.id}/template/{template.id}", data=data)
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get all versions of the template", target_fixture="api_response")
def get_all_versions(admin_client, service, template):
    resp = admin_client.get(f"/service/{service.id}/template/{template.id}/versions")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse("I get version {version:d} of the template"),
    target_fixture="api_response",
)
def get_specific_version(admin_client, service, template, version):
    resp = admin_client.get(f"/service/{service.id}/template/{template.id}/version/{version}")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I preview the template with personalisation name "{value}"'),
    target_fixture="api_response",
)
def preview_template(admin_client, service, template):
    resp = admin_client.get(f"/service/{service.id}/template/{template.id}/preview")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I create an SMS template with content "{content}"'),
    target_fixture="api_response",
)
def create_sms_template_with_content(admin_client, service, content):
    data = {
        "name": f"Template {uuid.uuid4()}",
        "template_type": SMS_TYPE,
        "content": content,
        "service": str(service.id),
        "created_by": str(service.created_by.id),
    }
    resp = admin_client.post(f"/service/{service.id}/template", data=data)
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    "I create an SMS template with content longer than the character limit",
    target_fixture="api_response",
)
def create_sms_template_too_long(admin_client, service):
    long_content = "x" * 10000
    data = {
        "name": "Too Long Template",
        "template_type": SMS_TYPE,
        "content": long_content,
        "service": str(service.id),
        "created_by": str(service.created_by.id),
    }
    resp = admin_client.post(f"/service/{service.id}/template", data=data)
    return {"status_code": resp.status_code, "json": resp.json}


@when("I archive the template", target_fixture="api_response")
def archive_template(admin_client, service, template):
    data = {
        "archived": True,
        "created_by": str(service.created_by.id),
    }
    resp = admin_client.post(f"/service/{service.id}/template/{template.id}", data=data)
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then(parsers.parse('the template type should be "{template_type}"'))
def template_type_is(api_response, template_type):
    assert api_response["json"]["data"]["template_type"] == template_type


@then(parsers.parse("the template version should be {version:d}"))
def template_version_is(api_response, version):
    assert api_response["json"]["data"]["version"] == version


@then("the response should contain the template details")
def response_has_template_details(api_response):
    data = api_response["json"]["data"]
    assert "id" in data
    assert "name" in data
    assert "content" in data
    assert "template_type" in data


@then(parsers.parse("the response should contain {count:d} templates"))
def response_has_n_templates(api_response, count):
    templates = api_response["json"]["data"]
    assert len(templates) == count


@then("the template version should be incremented")
def template_version_incremented(api_response, test_context):
    new_version = api_response["json"]["data"]["version"]
    assert new_version > test_context["original_version"]


@then(parsers.parse("the response should contain {count:d} versions"))
def response_has_n_versions(api_response, count):
    versions = api_response["json"]["data"]
    assert len(versions) == count


@then("the template content should be the original")
def template_content_is_original(api_response, test_context):
    content = api_response["json"]["data"]["content"]
    assert content == test_context["original_content"]


@then(parsers.parse('the preview should contain "{text}"'))
def preview_contains(api_response, text):
    content = api_response["json"]["data"]["content"]
    assert text in content


@then("the template should be archived")
def template_is_archived(api_response):
    assert api_response["json"]["data"]["archived"] is True
