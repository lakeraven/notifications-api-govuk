"""
Step definitions for inbound number management.
"""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from tests.app.db import create_inbound_number, create_service

scenarios("../features/inbound/inbound_numbers.feature")


# -- Given steps --


@given("unassigned inbound numbers exist", target_fixture="inbound_number")
def unassigned_inbound_numbers(notify_db_session):
    return create_inbound_number("07700900111")


@given("a service has an inbound number assigned", target_fixture="service")
def service_has_inbound_number(notify_db_session, test_context):
    svc = create_service(service_name=f"Inbound Svc {uuid.uuid4()}")
    ib = create_inbound_number("07700900222", service_id=svc.id)
    test_context["inbound_number"] = ib
    return svc


@given("an available inbound number exists", target_fixture="inbound_number")
def available_inbound_number(notify_db_session):
    return create_inbound_number("07700900333")


# -- When steps --


@when("I list all inbound numbers", target_fixture="api_response")
def list_all_inbound_numbers(admin_client):
    resp = admin_client.get("/inbound-number")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I list available inbound numbers", target_fixture="api_response")
def list_available_inbound_numbers(admin_client):
    resp = admin_client.get("/inbound-number/available")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the inbound number for the service", target_fixture="api_response")
def get_inbound_for_service(admin_client, service):
    resp = admin_client.get(f"/inbound-number/service/{service.id}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I assign the number to a service", target_fixture="api_response")
def assign_number_to_service(admin_client, inbound_number, notify_db_session):
    svc = create_service(service_name=f"Assign Svc {uuid.uuid4()}")
    resp = admin_client.post(f"/inbound-number/{inbound_number.id}/service/{svc.id}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I deactivate the inbound number", target_fixture="api_response")
def deactivate_inbound_number(admin_client, service):
    resp = admin_client.post(f"/inbound-number/service/{service.id}/off")
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then("the response should include the phone number")
def response_has_phone_number(api_response):
    data = api_response["json"]
    assert "number" in data or "data" in data
