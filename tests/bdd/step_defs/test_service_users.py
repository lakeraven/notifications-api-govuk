"""Step definitions for service users BDD tests."""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from tests.app.db import create_service, create_user

scenarios("../features/services/service_users.feature")


# -- Given steps --


@given("a user is added to the service", target_fixture="added_user")
def a_user_is_added_to_service(service, admin_client):
    user = create_user(email=f"added-{uuid.uuid4()}@digital.cabinet-office.gov.uk")
    admin_client.post(
        f"/service/{service.id}/users/{user.id}",
        data={
            "permissions": [{"permission": "manage_settings"}],
            "folder_permissions": [],
        },
    )
    return user


# -- When steps --


@when("I list the users for the service", target_fixture="api_response")
def list_service_users(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/users")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I add a new user to the service", target_fixture="api_response")
def add_user_to_service(admin_client, service, new_user):
    resp = admin_client.post(
        f"/service/{service.id}/users/{new_user.id}",
        data={
            "permissions": [{"permission": "manage_settings"}],
            "folder_permissions": [],
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I remove the added user from the service", target_fixture="api_response")
def remove_user_from_service(admin_client, service, added_user):
    resp = admin_client.delete(f"/service/{service.id}/users/{added_user.id}")
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then("the response should contain the list of service users")
def response_has_users_list(api_response):
    data = api_response["json"]["data"]
    assert isinstance(data, list)
    assert len(data) >= 1


@then("the response should contain the updated service with the new user")
def response_has_new_user(api_response, new_user):
    data = api_response["json"]["data"]
    user_ids = [u["id"] for u in data.get("users", [])]
    assert str(new_user.id) in user_ids


@then("the user should be removed from the service")
def user_is_removed(admin_client, service, added_user):
    resp = admin_client.get(f"/service/{service.id}/users")
    user_ids = [u["id"] for u in resp.json["data"]]
    assert str(added_user.id) not in user_ids
