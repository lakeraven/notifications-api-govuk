"""
Step definitions for user permission management.

Tests run against the Flask test client using existing test fixtures.
"""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from app.dao.services_dao import dao_add_user_to_service
from tests.app.db import (
    create_organisation,
    create_service,
    create_user,
    create_webauthn_credential,
)

# Load all scenarios from the feature file
scenarios("../features/users/user_permissions.feature")


# -- Given steps --


@given("a second user belongs to the service", target_fixture="second_user")
def second_user_in_service(service, notify_db_session):
    user = create_user(email=f"second-{uuid.uuid4()}@example.gov.uk")
    dao_add_user_to_service(service, user)
    return user


@given("the user belongs to an organisation", target_fixture="organisation")
def user_in_organisation(second_user, notify_db_session):
    org = create_organisation(name=f"PermOrg-{uuid.uuid4()}")

    from app.dao.organisation_dao import dao_add_user_to_organisation

    dao_add_user_to_organisation(organisation_id=org.id, user_id=second_user.id)
    return org


@given("the user has WebAuthn credentials", target_fixture="webauthn_cred")
def user_has_webauthn_credentials(second_user, notify_db_session):
    return create_webauthn_credential(second_user, name="perm-key")


@given("the user has a WebAuthn credential", target_fixture="webauthn_cred")
def user_has_one_webauthn_credential(second_user, notify_db_session):
    return create_webauthn_credential(second_user, name="delete-key")


# -- When steps --


@when(
    parsers.parse('I set the user\'s permissions to "{perm1}" and "{perm2}"'),
    target_fixture="api_response",
)
def set_user_permissions(admin_client, service, second_user, perm1, perm2):
    data = {
        "permissions": [
            {"permission": perm1},
            {"permission": perm2},
        ],
    }
    resp = admin_client.post(
        f"/user/{second_user.id}/service/{service.id}/permission",
        data=data,
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I set the user's permissions to empty", target_fixture="api_response")
def set_user_permissions_empty(admin_client, service, second_user):
    data = {
        "permissions": [],
    }
    resp = admin_client.post(
        f"/user/{second_user.id}/service/{service.id}/permission",
        data=data,
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I set the user's organisation permissions", target_fixture="api_response")
def set_org_permissions(admin_client, second_user, organisation):
    data = {
        "permissions": [],
    }
    resp = admin_client.post(
        f"/user/{second_user.id}/organisation/{organisation.id}/permissions",
        data=data,
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the user's WebAuthn credentials", target_fixture="api_response")
def get_webauthn_credentials(admin_client, second_user):
    resp = admin_client.get(f"/user/{second_user.id}/webauthn")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I create a WebAuthn credential for the user", target_fixture="api_response")
def create_webauthn_cred(admin_client, second_user):
    data = {
        "name": "new-key",
        "credential_data": "NEWCRED123",
        "registration_response": "NEWREG456",
    }
    resp = admin_client.post(f"/user/{second_user.id}/webauthn", data=data)
    return {"status_code": resp.status_code, "json": resp.json}


@when("I delete the WebAuthn credential", target_fixture="api_response")
def delete_webauthn_cred(admin_client, second_user, webauthn_cred):
    resp = admin_client.delete(f"/user/{second_user.id}/webauthn/{webauthn_cred.id}")
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then("the response should contain the credentials")
def response_has_credentials(api_response):
    data = api_response["json"]["data"]
    assert len(data) > 0
    assert "id" in data[0]
    assert "name" in data[0]
