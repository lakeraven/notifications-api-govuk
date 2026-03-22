"""
Step definitions for v2 letter notification sending.

Tests run against the Flask test client using existing test fixtures.
"""

import base64
import json
import uuid

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from app.constants import EMAIL_TYPE, INTERNATIONAL_LETTERS, LETTER_TYPE, SMS_TYPE
from app.models import Notification
from tests import create_service_authorization_header
from tests.app.db import (
    create_service,
    create_template,
)

# Load all scenarios from the feature file
scenarios("../features/v2_notifications/send_letter.feature")


# -- Fixtures --


@pytest.fixture
def letter_service(notify_db_session):
    """A service with letter permissions."""
    return create_service(service_permissions=[SMS_TYPE, EMAIL_TYPE, LETTER_TYPE])


@pytest.fixture
def letter_template():
    """Will be set by the given step."""
    return {}


# -- Given steps --


@given("a service with letter permissions exists", target_fixture="letter_service")
def service_with_letter(notify_db_session):
    return create_service(service_permissions=[SMS_TYPE, EMAIL_TYPE, LETTER_TYPE])


@given(
    parsers.parse('the service has a letter template with content "{content}"'),
    target_fixture="letter_template",
)
def service_has_letter_template(letter_service, content):
    return create_template(
        letter_service,
        template_type=LETTER_TYPE,
        subject="Template subject",
        content=content,
    )


@given("the service has a valid API key")
def service_has_api_key_letter(letter_service):
    # API keys are auto-created by create_service_authorization_header
    pass


@given("the letter template has second class postage")
def letter_template_second_class(letter_template):
    # Templates created by create_template with LETTER_TYPE default to "second" postage
    letter_template.postage = "second"


@given("a service without letter permissions exists", target_fixture="no_letter_service")
def service_without_letter(notify_db_session):
    return create_service(service_name="No letter service", service_permissions=[SMS_TYPE, EMAIL_TYPE])


@given("the service has international letter permission")
def service_has_international_letters(letter_service):
    from app.dao.service_permissions_dao import dao_add_service_permission

    dao_add_service_permission(letter_service.id, INTERNATIONAL_LETTERS)


@given("the letter template contains a QR code placeholder", target_fixture="letter_template")
def letter_template_with_qr_code(letter_service):
    return create_template(
        letter_service,
        template_type=LETTER_TYPE,
        subject="Template subject",
        content="Dear ((name)), your reference is ((ref)) ((qr_code_data))",
    )


# -- When steps --


@when("I send a letter notification with personalisation", target_fixture="api_response")
def send_letter_with_personalisation(client, letter_service, letter_template, mocker, datatable):
    mocker.patch("app.celery.letters_pdf_tasks.get_pdf_for_templated_letter.apply_async")
    row = datatable[0]
    personalisation = dict(row)
    data = {
        "template_id": str(letter_template.id),
        "personalisation": personalisation,
    }
    resp = client.post(
        "/v2/notifications/letter",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(letter_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send a letter notification with reference "{reference}" and personalisation'),
    target_fixture="api_response",
)
def send_letter_with_reference(client, letter_service, letter_template, reference, mocker, datatable):
    mocker.patch("app.celery.letters_pdf_tasks.get_pdf_for_templated_letter.apply_async")
    row = datatable[0]
    personalisation = dict(row)
    data = {
        "template_id": str(letter_template.id),
        "personalisation": personalisation,
        "reference": reference,
    }
    resp = client.post(
        "/v2/notifications/letter",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(letter_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send a precompiled letter with reference "{reference}" and a valid PDF'),
    target_fixture="api_response",
)
def send_precompiled_letter(client, letter_service, reference, mocker):
    mocker.patch("app.v2.notifications.post_notifications.upload_letter_pdf", return_value="test.pdf")
    mocker.patch("app.celery.letters_pdf_tasks.notify_celery.send_task")
    pdf_content = base64.b64encode(b"%PDF-1.4 precompiled letter content").decode("utf-8")
    data = {
        "reference": reference,
        "content": pdf_content,
    }
    resp = client.post(
        "/v2/notifications/letter",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(letter_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I send a letter notification with incomplete address", target_fixture="api_response")
def send_letter_incomplete_address(client, letter_service, letter_template, mocker, datatable):
    mocker.patch("app.celery.letters_pdf_tasks.get_pdf_for_templated_letter.apply_async")
    row = datatable[0]
    personalisation = dict(row)
    data = {
        "template_id": str(letter_template.id),
        "personalisation": personalisation,
    }
    resp = client.post(
        "/v2/notifications/letter",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(letter_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I send a letter notification using that service", target_fixture="api_response")
def send_letter_no_permission(client, no_letter_service, letter_template, mocker):
    mocker.patch("app.celery.letters_pdf_tasks.get_pdf_for_templated_letter.apply_async")
    template = create_template(no_letter_service, template_type=LETTER_TYPE, content="test ((name))")
    data = {
        "template_id": str(template.id),
        "personalisation": {
            "address_line_1": "10 Street",
            "address_line_2": "London",
            "postcode": "SW1A 1AA",
            "name": "Jo Smith",
        },
    }
    resp = client.post(
        "/v2/notifications/letter",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(no_letter_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I send a precompiled letter with reference "{reference}" and invalid content'),
    target_fixture="api_response",
)
def send_precompiled_letter_invalid(client, letter_service, reference, mocker):
    mocker.patch("app.v2.notifications.post_notifications.upload_letter_pdf", return_value="test.pdf")
    data = {
        "reference": reference,
        "content": "not-valid-base64!!!",
    }
    resp = client.post(
        "/v2/notifications/letter",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(letter_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I send a letter notification with international address", target_fixture="api_response")
def send_letter_international(client, letter_service, letter_template, mocker, datatable):
    mocker.patch("app.celery.letters_pdf_tasks.get_pdf_for_templated_letter.apply_async")
    row = datatable[0]
    personalisation = dict(row)
    data = {
        "template_id": str(letter_template.id),
        "personalisation": personalisation,
    }
    resp = client.post(
        "/v2/notifications/letter",
        data=json.dumps(data),
        headers=[
            ("Content-Type", "application/json"),
            create_service_authorization_header(letter_service.id),
        ],
    )
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then(parsers.parse('the notification postage should be "{postage}"'))
def notification_postage_is(postage):
    notifications = Notification.query.all()
    assert len(notifications) > 0
    assert notifications[-1].postage == postage


@then("the response should contain the precompiled letter ID")
def response_has_precompiled_letter_id(api_response):
    assert api_response["json"]["id"] is not None
