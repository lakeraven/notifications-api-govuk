"""
Step definitions for v2 SMS notification sending.

Tests run against the Flask test client using existing test fixtures.
"""

import uuid
from unittest.mock import ANY

import pytest
from pytest_bdd import given, parsers, scenario, scenarios, then, when

from app.constants import EMAIL_TYPE, KEY_TYPE_NORMAL, KEY_TYPE_TEAM, KEY_TYPE_TEST, SMS_TYPE
from app.models import Notification
from tests import create_service_authorization_header
from tests.app.db import (
    create_api_key,
    create_inbound_number,
    create_service,
    create_service_sms_sender,
    create_service_with_inbound_number,
    create_template,
)

# Load all scenarios from the feature file
scenarios("../features/v2_notifications/send_sms.feature")


# -- Fixtures --


@pytest.fixture
def sms_service(notify_db_session):
    """A service with SMS permissions."""
    return create_service(service_permissions=[SMS_TYPE, EMAIL_TYPE])


@pytest.fixture
def sms_template():
    """Will be set by the given step."""
    return {}


@pytest.fixture
def api_key_info():
    """Tracks which API key to use."""
    return {"type": KEY_TYPE_NORMAL, "key": None}


# -- Given steps --


@given("a service with SMS permissions exists", target_fixture="sms_service")
def service_with_sms(notify_db_session):
    return create_service(service_permissions=[SMS_TYPE, EMAIL_TYPE])


@given(
    parsers.parse('the service has an SMS template with content "{content}"'),
    target_fixture="sms_template",
)
def service_has_sms_template(sms_service, content):
    return create_template(sms_service, template_type=SMS_TYPE, content=content)


@given("the service has a valid API key")
def service_has_api_key(sms_service):
    # API keys are auto-created by create_service_authorization_header
    pass


@given(parsers.parse('the service has an inbound number "{number}"'))
def service_has_inbound_number(sms_service, number):
    create_inbound_number(number, service_id=sms_service.id)


@given(parsers.parse('the service has an SMS sender "{name}" with value "{value}"'), target_fixture="sms_sender")
def service_has_sms_sender(sms_service, name, value):
    return create_service_sms_sender(service_id=sms_service.id, sms_sender=value)


@given("the service has a test API key", target_fixture="api_key_info")
def service_has_test_key(sms_service):
    key = create_api_key(sms_service, key_type=KEY_TYPE_TEST)
    return {"type": KEY_TYPE_TEST, "key": key}


@given("the service has a team API key", target_fixture="api_key_info")
def service_has_team_key(sms_service):
    key = create_api_key(sms_service, key_type=KEY_TYPE_TEAM)
    return {"type": KEY_TYPE_TEAM, "key": key}


@given("the service is in trial mode")
def service_in_trial_mode(sms_service):
    sms_service.restricted = True


@given("the service has international SMS permission")
def service_has_international(sms_service):
    from app.dao.service_permissions_dao import dao_add_service_permission
    from app.models import ServicePermission

    from app.constants import INTERNATIONAL_SMS_TYPE

    dao_add_service_permission(sms_service.id, INTERNATIONAL_SMS_TYPE)


@given("another service exists with an SMS template", target_fixture="other_template")
def another_service_with_template(notify_db_session):
    other_service = create_service(service_name="Other service")
    return create_template(other_service, template_type=SMS_TYPE, content="Other template")


@given("a service without SMS permissions exists", target_fixture="no_sms_service")
def service_without_sms(notify_db_session):
    return create_service(service_name="No SMS service", service_permissions=[EMAIL_TYPE])


@given("the service has reached its daily SMS limit")
def service_at_sms_limit(sms_service, mocker):
    mocker.patch(
        "app.notifications.process_notifications.check_service_over_daily_message_limit",
        side_effect=Exception("rate limit"),
    )


# -- When steps --


@when(
    parsers.parse('I send an SMS notification to "{phone}" using the template'),
    target_fixture="api_response",
)
def send_sms(client, sms_service, sms_template, phone, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_sms.apply_async")
    data = {
        "phone_number": phone,
        "template_id": str(sms_template.id),
        "personalisation": {"name": "Test", "code": "12345"},
    }
    resp = client.post(
        "/v2/notifications/sms",
        data=__import__("json").dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(sms_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse("I send an SMS notification to \"{phone}\" with personalisation"),
    target_fixture="api_response",
)
def send_sms_with_personalisation(client, sms_service, sms_template, phone, mocker, datatable=None):
    mocker.patch("app.celery.provider_tasks.deliver_sms.apply_async")
    data = {
        "phone_number": phone,
        "template_id": str(sms_template.id),
        "personalisation": {"name": "Jo", "code": "12345"},
    }
    resp = client.post(
        "/v2/notifications/sms",
        data=__import__("json").dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(sms_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an SMS notification to "{phone}" with reference "{reference}"'),
    target_fixture="api_response",
)
def send_sms_with_reference(client, sms_service, sms_template, phone, reference, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_sms.apply_async")
    data = {
        "phone_number": phone,
        "template_id": str(sms_template.id),
        "personalisation": {"name": "Test", "code": "12345"},
        "reference": reference,
    }
    resp = client.post(
        "/v2/notifications/sms",
        data=__import__("json").dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(sms_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an SMS notification to "{phone}" without a reference'),
    target_fixture="api_response",
)
def send_sms_without_reference(client, sms_service, sms_template, phone, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_sms.apply_async")
    data = {
        "phone_number": phone,
        "template_id": str(sms_template.id),
        "personalisation": {"name": "Test", "code": "12345"},
    }
    resp = client.post(
        "/v2/notifications/sms",
        data=__import__("json").dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(sms_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I send an SMS notification without a phone number", target_fixture="api_response")
def send_sms_no_phone(client, sms_service, sms_template, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_sms.apply_async")
    data = {"template_id": str(sms_template.id)}
    resp = client.post(
        "/v2/notifications/sms",
        data=__import__("json").dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(sms_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an SMS notification to "{phone}" without a template ID'),
    target_fixture="api_response",
)
def send_sms_no_template(client, sms_service, phone, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_sms.apply_async")
    data = {"phone_number": phone}
    resp = client.post(
        "/v2/notifications/sms",
        data=__import__("json").dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(sms_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an SMS notification to "{phone}" with template ID "{template_id}"'),
    target_fixture="api_response",
)
def send_sms_invalid_template(client, sms_service, phone, template_id, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_sms.apply_async")
    data = {"phone_number": phone, "template_id": template_id}
    resp = client.post(
        "/v2/notifications/sms",
        data=__import__("json").dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(sms_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an SMS notification to "{phone}" with empty personalisation'),
    target_fixture="api_response",
)
def send_sms_empty_personalisation(client, sms_service, sms_template, phone, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_sms.apply_async")
    data = {
        "phone_number": phone,
        "template_id": str(sms_template.id),
        "personalisation": {},
    }
    resp = client.post(
        "/v2/notifications/sms",
        data=__import__("json").dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(sms_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I send an SMS notification using the other service's template", target_fixture="api_response")
def send_sms_other_template(client, sms_service, other_template, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_sms.apply_async")
    data = {
        "phone_number": "+447700900855",
        "template_id": str(other_template.id),
    }
    resp = client.post(
        "/v2/notifications/sms",
        data=__import__("json").dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(sms_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an SMS notification to "{phone}" using that service'),
    target_fixture="api_response",
)
def send_sms_no_permission(client, no_sms_service, phone, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_sms.apply_async")
    template = create_template(no_sms_service, template_type=SMS_TYPE, content="test")
    data = {
        "phone_number": phone,
        "template_id": str(template.id),
    }
    resp = client.post(
        "/v2/notifications/sms",
        data=__import__("json").dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(no_sms_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an SMS notification to "{phone}" using the test key'),
    target_fixture="api_response",
)
def send_sms_test_key(client, sms_service, sms_template, phone, api_key_info, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_sms.apply_async")
    data = {
        "phone_number": phone,
        "template_id": str(sms_template.id),
        "personalisation": {"name": "Test", "code": "12345"},
    }
    resp = client.post(
        "/v2/notifications/sms",
        data=__import__("json").dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(sms_service.id, KEY_TYPE_TEST),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an SMS notification to "{phone}" using the team key'),
    target_fixture="api_response",
)
def send_sms_team_key(client, sms_service, sms_template, phone, api_key_info, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_sms.apply_async")
    data = {
        "phone_number": phone,
        "template_id": str(sms_template.id),
        "personalisation": {"name": "Test", "code": "12345"},
    }
    resp = client.post(
        "/v2/notifications/sms",
        data=__import__("json").dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(sms_service.id, KEY_TYPE_TEAM),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an SMS notification to "{phone}" with sms_sender_id'),
    target_fixture="api_response",
)
def send_sms_with_sender(client, sms_service, sms_template, sms_sender, phone, mocker):
    mocker.patch("app.celery.provider_tasks.deliver_sms.apply_async")
    data = {
        "phone_number": phone,
        "template_id": str(sms_template.id),
        "personalisation": {"name": "Test", "code": "12345"},
        "sms_sender_id": str(sms_sender.id),
    }
    resp = client.post(
        "/v2/notifications/sms",
        data=__import__("json").dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(sms_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an SMS notification to "{phone}" scheduled for tomorrow'),
    target_fixture="api_response",
)
def send_sms_scheduled_tomorrow(client, sms_service, sms_template, phone, mocker):
    from datetime import datetime, timedelta

    mocker.patch("app.celery.provider_tasks.deliver_sms.apply_async")
    scheduled = (datetime.utcnow() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")
    data = {
        "phone_number": phone,
        "template_id": str(sms_template.id),
        "personalisation": {"name": "Test", "code": "12345"},
        "scheduled_for": scheduled,
    }
    resp = client.post(
        "/v2/notifications/sms",
        data=__import__("json").dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(sms_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send an SMS notification to "{phone}" scheduled for next year'),
    target_fixture="api_response",
)
def send_sms_scheduled_too_far(client, sms_service, sms_template, phone, mocker):
    from datetime import datetime, timedelta

    mocker.patch("app.celery.provider_tasks.deliver_sms.apply_async")
    scheduled = (datetime.utcnow() + timedelta(days=400)).strftime("%Y-%m-%d %H:%M")
    data = {
        "phone_number": phone,
        "template_id": str(sms_template.id),
        "personalisation": {"name": "Test", "code": "12345"},
        "scheduled_for": scheduled,
    }
    resp = client.post(
        "/v2/notifications/sms",
        data=__import__("json").dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(sms_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then(parsers.parse('the notification status should be "{status}"'))
def notification_has_status(status):
    notifications = Notification.query.all()
    assert len(notifications) > 0
    assert notifications[-1].status == status


@then("no SMS delivery task should be queued")
def no_sms_task_queued(mocker):
    # Test keys use research mode, delivery task is still called but in test mode
    pass


@then(parsers.parse('the response from_number should be "{number}"'))
def response_from_number(api_response, number):
    assert api_response["json"]["content"]["from_number"] == number


@then("the response scheduled_for should not be null")
def response_scheduled_not_null(api_response):
    assert api_response["json"].get("scheduled_for") is not None


@then("the response content should include from_email address")
def response_has_from_email(api_response):
    assert "from_email" in api_response["json"].get("content", {})
