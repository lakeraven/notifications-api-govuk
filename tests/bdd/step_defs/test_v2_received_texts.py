"""
Step definitions for v2 received text messages (inbound SMS).

Tests run against the Flask test client using existing test fixtures.
"""

import json
import uuid
from datetime import datetime, timedelta

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from app.constants import INBOUND_SMS_TYPE, SMS_TYPE
from tests import create_service_authorization_header
from tests.app.db import (
    create_inbound_sms,
    create_service_with_inbound_number,
)

# Load all scenarios from the feature file
scenarios("../features/v2_inbound_sms/received_texts.feature")


# -- Fixtures --


@pytest.fixture
def test_context():
    """Mutable container for sharing state between Given/When/Then steps."""
    return {}


# -- Given steps --


@given("a service exists with inbound SMS enabled", target_fixture="service")
def a_service_with_inbound_sms(notify_db_session):
    return create_service_with_inbound_number(
        inbound_number="07700900111",
        service_permissions=[SMS_TYPE, INBOUND_SMS_TYPE],
    )


@given("the service has a valid API key")
def service_has_api_key(service):
    # API key is auto-created by create_service_authorization_header
    pass


@given(parsers.parse("the service has received {count:d} inbound SMS messages"), target_fixture="test_context")
def service_received_inbound_sms(service, test_context, count):
    messages = []
    for i in range(count):
        msg = create_inbound_sms(
            service=service,
            content=f"Inbound message {i + 1}",
            user_number=f"44770090{1000 + i}",
            created_at=datetime.utcnow() - timedelta(minutes=count - i),
        )
        messages.append(msg)
    test_context["inbound_messages"] = messages
    return test_context


# -- When steps --


@when("I list received text messages", target_fixture="api_response")
def list_received_texts(client, service):
    resp = client.get(
        "/v2/received-text-messages",
        headers=[create_service_authorization_header(service.id)],
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I list received texts older than the 3rd message", target_fixture="api_response")
def list_received_texts_older_than_3rd(client, service, test_context):
    messages = test_context["inbound_messages"]
    older_than_id = messages[2].id
    test_context["older_than_message"] = messages[2]
    resp = client.get(
        f"/v2/received-text-messages?older_than={older_than_id}",
        headers=[create_service_authorization_header(service.id)],
    )
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then(parsers.parse("the response should contain {count:d} received texts"))
def response_contains_n_texts(api_response, count):
    messages = api_response["json"]["received_text_messages"]
    assert len(messages) == count, f"Expected {count} messages, got {len(messages)}"


@then("each received text should include content, created_at, and user_number")
def each_text_has_required_fields(api_response):
    messages = api_response["json"]["received_text_messages"]
    assert len(messages) > 0
    for msg in messages:
        assert "content" in msg, f"Missing 'content' in received text: {msg}"
        assert "created_at" in msg, f"Missing 'created_at' in received text: {msg}"
        assert "user_number" in msg, f"Missing 'user_number' in received text: {msg}"


@then("all returned messages should be older than the 3rd message")
def messages_older_than_3rd(api_response, test_context):
    messages = api_response["json"]["received_text_messages"]
    older_than = test_context["older_than_message"]
    assert len(messages) > 0
    for msg in messages:
        assert msg["created_at"] < older_than.created_at.strftime("%Y-%m-%d %H:%M:%S.%f")
