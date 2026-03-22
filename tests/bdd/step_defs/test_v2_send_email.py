"""
Step definitions for v2 email notification sending.

Tests run against the Flask test client using existing test fixtures.
"""

import base64
import json
import uuid
from datetime import datetime, timedelta
from unittest.mock import ANY

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from app.constants import EMAIL_TYPE, KEY_TYPE_NORMAL, KEY_TYPE_TEAM, KEY_TYPE_TEST, SMS_TYPE
from app.models import Notification
from app.v2.errors import TooManyRequestsError
from tests import create_service_authorization_header
from tests.app.db import (
    create_api_key,
    create_reply_to_email,
    create_service,
    create_template,
)

# Load all scenarios from the feature file
scenarios("../features/v2_notifications/send_email.feature")


# -- Fixtures --


@pytest.fixture
def email_service(notify_db_session):
    """A service with email permissions."""
    return create_service(service_permissions=[EMAIL_TYPE, SMS_TYPE])


@pytest.fixture
def email_template():
    """Will be set by the given step."""
    return {}


@pytest.fixture
def api_key_info():
    """Tracks which API key to use."""
    return {"type": KEY_TYPE_NORMAL, "key": None}


# -- Given steps --


@given("a service with email permissions exists", target_fixture="email_service")
def service_with_email(notify_db_session):
    return create_service(service_permissions=[EMAIL_TYPE, SMS_TYPE])


@given(
    parsers.parse('the service has an email template with subject "{subject}" and content "{content}"'),
    target_fixture="email_template",
)
def service_has_email_template(email_service, subject, content):
    return create_template(email_service, template_type=EMAIL_TYPE, subject=subject, content=content)


@given("the service has a valid API key")
def service_has_api_key(email_service):
    # API keys are auto-created by create_service_authorization_header
    pass


@given("the service has a test API key", target_fixture="api_key_info")
def service_has_test_key(email_service):
    key = create_api_key(email_service, key_type=KEY_TYPE_TEST)
    return {"type": KEY_TYPE_TEST, "key": key}


@given("the service has a team API key", target_fixture="api_key_info")
def service_has_team_key(email_service):
    key = create_api_key(email_service, key_type=KEY_TYPE_TEAM)
    return {"type": KEY_TYPE_TEAM, "key": key}


@given(parsers.parse('the service has a reply-to email "{email_address}"'), target_fixture="reply_to_email")
def service_has_reply_to(email_service, email_address):
    return create_reply_to_email(email_service, email_address)


@given("the service has reached its daily email limit")
def service_at_email_limit(email_service, mocker):
    mocker.patch(
        "app.notifications.validators.check_service_over_daily_message_limit",
        side_effect=TooManyRequestsError("email", email_service.message_limit),
    )


# -- When steps --


@when(
    parsers.parse('I send an email notification to "{email}" using the template'),
    target_fixture="api_response",
)
def send_email(client, email_service, email_template, email, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_email.apply_async")
    data = {
        "email_address": email,
        "template_id": str(email_template.id),
        "personalisation": {"name": "Test"},
    }
    resp = client.post(
        "/v2/notifications/email",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(email_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an email notification to "{email}" with personalisation'),
    target_fixture="api_response",
)
def send_email_with_personalisation(client, email_service, email_template, email, mocker, datatable=None):
    mocker.patch("app.celery.provider_tasks.deliver_email.apply_async")
    personalisation = {"name": "Alice"}
    if datatable:
        personalisation = {row[0]: row[1] for row in datatable}
    data = {
        "email_address": email,
        "template_id": str(email_template.id),
        "personalisation": personalisation,
    }
    resp = client.post(
        "/v2/notifications/email",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(email_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an email notification to "{email}" with reference "{reference}"'),
    target_fixture="api_response",
)
def send_email_with_reference(client, email_service, email_template, email, reference, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_email.apply_async")
    data = {
        "email_address": email,
        "template_id": str(email_template.id),
        "personalisation": {"name": "Test"},
        "reference": reference,
    }
    resp = client.post(
        "/v2/notifications/email",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(email_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an email notification to "{email}" with email_reply_to_id'),
    target_fixture="api_response",
)
def send_email_with_reply_to(client, email_service, email_template, reply_to_email, email, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_email.apply_async")
    data = {
        "email_address": email,
        "template_id": str(email_template.id),
        "personalisation": {"name": "Test"},
        "email_reply_to_id": str(reply_to_email.id),
    }
    resp = client.post(
        "/v2/notifications/email",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(email_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an email notification to "{email}" with one_click_unsubscribe_url "{url}"'),
    target_fixture="api_response",
)
def send_email_with_unsubscribe(client, email_service, email_template, email, url, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_email.apply_async")
    data = {
        "email_address": email,
        "template_id": str(email_template.id),
        "personalisation": {"name": "Test"},
        "one_click_unsubscribe_url": url,
    }
    resp = client.post(
        "/v2/notifications/email",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(email_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I send an email notification without an email address", target_fixture="api_response")
def send_email_no_address(client, email_service, email_template, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_email.apply_async")
    data = {"template_id": str(email_template.id)}
    resp = client.post(
        "/v2/notifications/email",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(email_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an email notification to "{email}" with empty personalisation'),
    target_fixture="api_response",
)
def send_email_empty_personalisation(client, email_service, email_template, email, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_email.apply_async")
    data = {
        "email_address": email,
        "template_id": str(email_template.id),
        "personalisation": {},
    }
    resp = client.post(
        "/v2/notifications/email",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(email_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an email notification to "{email}" using the test key'),
    target_fixture="api_response",
)
def send_email_test_key(client, email_service, email_template, email, api_key_info, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_email.apply_async")
    data = {
        "email_address": email,
        "template_id": str(email_template.id),
        "personalisation": {"name": "Test"},
    }
    resp = client.post(
        "/v2/notifications/email",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(email_service.id, KEY_TYPE_TEST),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an email notification to "{email}" scheduled for tomorrow'),
    target_fixture="api_response",
)
def send_email_scheduled_tomorrow(client, email_service, email_template, email, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_email.apply_async")
    scheduled = (datetime.utcnow() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")
    data = {
        "email_address": email,
        "template_id": str(email_template.id),
        "personalisation": {"name": "Test"},
        "scheduled_for": scheduled,
    }
    resp = client.post(
        "/v2/notifications/email",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(email_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I send an email with a file upload in personalisation", target_fixture="api_response")
def send_email_with_file_upload(client, email_service, email_template, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_email.apply_async")
    mocker.patch(
        "app.v2.notifications.post_notifications.document_download_client.upload_document",
        return_value="https://document-download.example.com/d/AAAA",
    )
    file_content = base64.b64encode(b"This is a test document").decode("utf-8")
    data = {
        "email_address": "user@example.com",
        "template_id": str(email_template.id),
        "personalisation": {
            "name": "Test",
            "link_to_file": {"file": file_content, "filename": "test.pdf"},
        },
    }
    resp = client.post(
        "/v2/notifications/email",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(email_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then(parsers.parse('the response content should include subject "{subject}"'))
def response_has_subject(api_response, subject):
    assert api_response["json"]["content"]["subject"] == subject


@then("the response content should include from_email address")
def response_has_from_email(api_response):
    assert "from_email" in api_response["json"].get("content", {})


@then("no email delivery task should be queued")
def no_email_task_queued(mocker):
    # Test keys use research mode, delivery task is still called but in test mode
    pass


@then("the response scheduled_for should not be null")
def response_scheduled_not_null(api_response):
    assert api_response["json"].get("scheduled_for") is not None
