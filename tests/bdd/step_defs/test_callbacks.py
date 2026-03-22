"""Step definitions for service callbacks BDD tests."""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from app.constants import ServiceCallbackTypes
from tests.app.db import create_service, create_service_callback_api, create_user

scenarios("../features/services/callbacks.feature")


# -- Given steps --


@given("the service has a delivery status callback", target_fixture="callback")
def the_service_has_delivery_callback(service):
    return create_service_callback_api(
        callback_type=ServiceCallbackTypes.delivery_status,
        service=service,
        url="https://example.com/delivery",
        bearer_token="super_secret_token_1234",
    )


@given("the service has an inbound SMS callback", target_fixture="callback")
def the_service_has_inbound_callback(service):
    return create_service_callback_api(
        callback_type=ServiceCallbackTypes.inbound_sms,
        service=service,
        url="https://example.com/inbound",
        bearer_token="super_secret_token_1234",
    )


# -- When steps --


@when("I create a delivery status callback for the service", target_fixture="api_response")
def create_delivery_callback(admin_client, service):
    resp = admin_client.post(
        f"/service/{service.id}/callback-api",
        data={
            "url": "https://example.com/delivery-new",
            "bearer_token": "new_secret_token_1234",
            "updated_by_id": str(service.users[0].id),
            "callback_type": ServiceCallbackTypes.delivery_status,
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the delivery status callback", target_fixture="api_response")
def get_delivery_callback(admin_client, service, callback):
    resp = admin_client.get(
        f"/service/{service.id}/callback-api/{callback.id}?callback_type={ServiceCallbackTypes.delivery_status}",
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I update the delivery status callback", target_fixture="api_response")
def update_delivery_callback(admin_client, service, callback):
    resp = admin_client.post(
        f"/service/{service.id}/callback-api/{callback.id}",
        data={
            "url": "https://example.com/delivery-updated",
            "bearer_token": "updated_secret_token_1234",
            "updated_by_id": str(service.users[0].id),
            "callback_type": ServiceCallbackTypes.delivery_status,
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I delete the delivery status callback", target_fixture="api_response")
def delete_delivery_callback(admin_client, service, callback):
    resp = admin_client.delete(
        f"/service/{service.id}/callback-api/{callback.id}?callback_type={ServiceCallbackTypes.delivery_status}",
    )
    return {"status_code": resp.status_code, "json": resp.json if resp.status_code != 204 else {}}


@when("I create an inbound SMS callback for the service", target_fixture="api_response")
def create_inbound_callback(admin_client, service):
    resp = admin_client.post(
        f"/service/{service.id}/callback-api",
        data={
            "url": "https://example.com/inbound-new",
            "bearer_token": "new_secret_token_1234",
            "updated_by_id": str(service.users[0].id),
            "callback_type": ServiceCallbackTypes.inbound_sms,
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the inbound SMS callback", target_fixture="api_response")
def get_inbound_callback(admin_client, service, callback):
    resp = admin_client.get(
        f"/service/{service.id}/callback-api/{callback.id}?callback_type={ServiceCallbackTypes.inbound_sms}",
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I update the inbound SMS callback", target_fixture="api_response")
def update_inbound_callback(admin_client, service, callback):
    resp = admin_client.post(
        f"/service/{service.id}/callback-api/{callback.id}",
        data={
            "url": "https://example.com/inbound-updated",
            "bearer_token": "updated_secret_token_1234",
            "updated_by_id": str(service.users[0].id),
            "callback_type": ServiceCallbackTypes.inbound_sms,
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I delete the inbound SMS callback", target_fixture="api_response")
def delete_inbound_callback(admin_client, service, callback):
    resp = admin_client.delete(
        f"/service/{service.id}/callback-api/{callback.id}?callback_type={ServiceCallbackTypes.inbound_sms}",
    )
    return {"status_code": resp.status_code, "json": resp.json if resp.status_code != 204 else {}}


# -- Then steps --


@then("the response should contain the callback details")
def response_has_callback_details(api_response):
    data = api_response["json"]["data"]
    assert "id" in data
    assert "url" in data
    assert "callback_type" in data


@then("the response should contain the updated callback")
def response_has_updated_callback(api_response):
    data = api_response["json"]["data"]
    assert "id" in data
    assert "url" in data


@then("the callback should be deleted")
def callback_is_deleted(api_response):
    assert api_response["status_code"] == 204
