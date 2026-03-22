"""Step definitions for API keys BDD tests."""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from app.constants import KEY_TYPE_NORMAL
from tests.app.db import (
    create_api_key,
    create_service,
    create_template,
    create_user,
)

scenarios("../features/services/api_keys.feature")


# -- Given steps --


@given("the service has an API key", target_fixture="api_key")
def the_service_has_an_api_key(service):
    return create_api_key(service, key_type=KEY_TYPE_NORMAL, key_name="Test API Key")


@given("the service has a revoked API key", target_fixture="api_key")
def the_service_has_a_revoked_api_key(service, admin_client):
    api_key = create_api_key(service, key_type=KEY_TYPE_NORMAL, key_name="Revoked Key")
    admin_client.post(
        f"/service/{service.id}/api-key/revoke/{api_key.id}",
    )
    return api_key


# -- When steps --


@when("I create an API key for the service", target_fixture="api_response")
def create_api_key_via_api(admin_client, service):
    resp = admin_client.post(
        f"/service/{service.id}/api-key",
        data={
            "name": f"New API Key {uuid.uuid4()}",
            "created_by": str(service.created_by.id),
            "key_type": KEY_TYPE_NORMAL,
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I list the API keys for the service", target_fixture="api_response")
def list_api_keys(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/api-keys")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the API key by ID", target_fixture="api_response")
def get_api_key_by_id(admin_client, service, api_key):
    resp = admin_client.get(f"/service/{service.id}/api-keys/{api_key.id}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I revoke the API key", target_fixture="api_response")
def revoke_api_key(admin_client, service, api_key):
    resp = admin_client.post(
        f"/service/{service.id}/api-key/revoke/{api_key.id}",
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I try to send a notification with the revoked API key", target_fixture="api_response")
def send_with_revoked_key(service, api_key, service_api_client):
    template = create_template(service=service)
    service_api_client.set_service(service.id)
    resp = service_api_client.post(
        "/v2/notifications/sms",
        data={
            "phone_number": "+447700900855",
            "template_id": str(template.id),
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then("the response should contain the API key data")
def response_has_api_key_data(api_response):
    data = api_response["json"]["data"]
    assert data is not None


@then("the response should contain a list of API keys")
def response_has_api_keys_list(api_response):
    api_keys = api_response["json"]["apiKeys"]
    assert isinstance(api_keys, list)
    assert len(api_keys) >= 1


@then("the response should contain the API key details")
def response_has_api_key_details(api_response):
    api_keys = api_response["json"]["apiKeys"]
    assert isinstance(api_keys, list)
    assert len(api_keys) == 1
    assert "id" in api_keys[0]
    assert "name" in api_keys[0]


@then("the API key should be revoked")
def api_key_is_revoked(admin_client, service, api_key):
    resp = admin_client.get(f"/service/{service.id}/api-keys/{api_key.id}")
    keys = resp.json["apiKeys"]
    assert len(keys) == 1
    assert keys[0]["expiry_date"] is not None


@then("the notification send should be rejected")
def notification_rejected(api_response):
    assert api_response["status_code"] == 403
