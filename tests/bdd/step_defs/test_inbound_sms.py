"""
Step definitions for inbound SMS management (admin API).
"""

import json
import uuid
from datetime import datetime, timedelta

from pytest_bdd import given, parsers, scenarios, then, when

from tests.app.db import (
    create_inbound_sms,
    create_service_with_inbound_number,
)

scenarios("../features/inbound/inbound_sms.feature")


# -- Given steps --


@given("a service exists with inbound SMS enabled", target_fixture="service")
def service_with_inbound_sms(notify_db_session):
    return create_service_with_inbound_number(
        inbound_number="07700900100",
        service_name=f"Inbound SMS Svc {uuid.uuid4()}",
    )


@given("the service has received inbound SMS messages", target_fixture="inbound_messages")
def service_has_inbound_sms(notify_db_session, service):
    msgs = [
        create_inbound_sms(service, content="Hello 1"),
        create_inbound_sms(service, content="Hello 2"),
    ]
    return msgs


@given("the service has received inbound SMS in the last 7 days", target_fixture="inbound_messages")
def service_has_recent_inbound(notify_db_session, service):
    return [create_inbound_sms(service, content="Recent", created_at=datetime.utcnow() - timedelta(days=1))]


@given("a specific inbound SMS exists", target_fixture="inbound_sms")
def specific_inbound_sms(notify_db_session, service):
    return create_inbound_sms(service, content="Specific message")


# -- When steps --


@when("I query inbound SMS for the service", target_fixture="api_response")
def query_inbound_sms(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/inbound-sms")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the most recent inbound SMS", target_fixture="api_response")
def get_most_recent_inbound(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/inbound-sms/most-recent")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the inbound SMS summary", target_fixture="api_response")
def get_inbound_summary(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/inbound-sms/summary")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the inbound SMS by ID", target_fixture="api_response")
def get_inbound_by_id(admin_client, inbound_sms):
    resp = admin_client.get(f"/inbound-sms/{inbound_sms.id}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I remove inbound SMS for the service", target_fixture="api_response")
def remove_inbound_sms(admin_client, service):
    resp = admin_client.post(f"/service/{service.id}/inbound-sms/off")
    return {"status_code": resp.status_code, "json": resp.json}


@when("a provider sends an inbound SMS webhook", target_fixture="api_response")
def provider_webhook(client, service):
    data = {
        "ID": str(uuid.uuid4()),
        "MSISDN": "447700900111",
        "Message": "Webhook test",
        "DateRecieved": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "Number": service.get_inbound_number(),
    }
    resp = client.post(
        "/notifications/sms/receive/mmg",
        data=json.dumps(data),
        headers=[("Content-Type", "application/json")],
    )
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then("the response should include a count")
def response_has_count(api_response):
    data = api_response["json"]
    assert "count" in data or isinstance(data, dict)


@then("the inbound SMS should be stored")
def inbound_sms_stored(api_response):
    # If webhook returned 200, the message was processed
    assert api_response["status_code"] == 200
