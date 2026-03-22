"""
Step definitions for user management.

Tests run against the Flask test client using existing test fixtures.
"""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from app.dao.organisation_dao import dao_create_organisation
from app.dao.services_dao import dao_add_user_to_service
from tests.app.db import (
    create_organisation,
    create_service,
    create_user,
)

# Load all scenarios from the feature file
scenarios("../features/users/user_management.feature")


# -- Given steps --


@given("a user exists", target_fixture="user")
def user_exists(notify_db_session):
    return create_user(email=f"user-{uuid.uuid4()}@example.gov.uk")


@given(
    parsers.parse('a user exists with email "{email}"'),
    target_fixture="user",
)
def user_exists_with_email(notify_db_session, email):
    return create_user(email=email)


@given("a pending user exists", target_fixture="user")
def pending_user_exists(notify_db_session):
    return create_user(email=f"pending-{uuid.uuid4()}@example.gov.uk", state="pending")


@given("a user belongs to a service and an organisation", target_fixture="user")
def user_with_service_and_org(notify_db_session, test_context):
    user = create_user(email=f"orguser-{uuid.uuid4()}@example.gov.uk")
    service = create_service(user=user, service_name=f"UserService-{uuid.uuid4()}")
    org = create_organisation(name=f"UserOrg-{uuid.uuid4()}")

    from app.dao.organisation_dao import dao_add_user_to_organisation

    dao_add_user_to_organisation(organisation_id=org.id, user_id=user.id)

    test_context["service"] = service
    test_context["organisation"] = org
    return user


# -- When steps --


@when(
    parsers.parse('I create a user with email "{email}" and mobile "{mobile}"'),
    target_fixture="api_response",
)
def create_new_user(admin_client, email, mobile):
    data = {
        "name": "New User",
        "email_address": email,
        "mobile_number": mobile,
        "password": "ValidPassword123!",
        "auth_type": "sms_auth",
    }
    resp = admin_client.post("/user", data=data)
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the user by ID", target_fixture="api_response")
def get_user_by_id(admin_client, user):
    resp = admin_client.get(f"/user/{user.id}")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I update the user\'s name to "{name}"'),
    target_fixture="api_response",
)
def update_user_name(admin_client, user, name):
    data = {"name": name}
    resp = admin_client.post(f"/user/{user.id}", data=data)
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I fetch the user by email "{email}"'),
    target_fixture="api_response",
)
def fetch_user_by_email(admin_client, email):
    data = {"email": email}
    resp = admin_client.post("/user/email", data=data)
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I find users by email "{email}"'),
    target_fixture="api_response",
)
def find_users_by_partial_email(admin_client, email):
    data = {"email": email}
    resp = admin_client.post("/user/find-users-by-email", data=data)
    return {"status_code": resp.status_code, "json": resp.json}


@when("I archive the user", target_fixture="api_response")
def archive_user(admin_client, user, notify_db_session):
    # User must belong to a service to be archived
    service = create_service(user=user, service_name=f"ArchiveService-{uuid.uuid4()}")
    resp = admin_client.post(f"/user/{user.id}/archive", data={})
    return {"status_code": resp.status_code, "json": resp.json}


@when("I activate the user", target_fixture="api_response")
def activate_user(admin_client, user):
    resp = admin_client.post(f"/user/{user.id}/activate", data={})
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the user's organisations and services", target_fixture="api_response")
def get_orgs_and_services(admin_client, user):
    resp = admin_client.get(f"/user/{user.id}/organisations-and-services")
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then(parsers.parse('the user should have state "{state}"'))
def user_has_state(api_response, state):
    assert api_response["json"]["data"]["state"] == state


@then("the response should contain the user's email")
def response_has_user_email(api_response):
    data = api_response["json"]["data"]
    assert "email_address" in data
    assert data["email_address"] is not None


@then(parsers.parse('the user\'s name should be "{name}"'))
def user_name_is(api_response, name):
    assert api_response["json"]["data"]["name"] == name


@then("the response should contain the user's ID")
def response_has_user_id(api_response):
    data = api_response["json"]["data"]
    assert "id" in data
    assert data["id"] is not None


@then("the results should include the user")
def results_include_user(api_response, user):
    data = api_response["json"]["data"]
    user_ids = [u["id"] for u in data]
    assert str(user.id) in user_ids


@then(parsers.parse('the user state should be "{state}"'))
def user_state_is(api_response, state):
    assert api_response["json"]["data"]["state"] == state


@then("the response should include both the service and the organisation")
def response_has_service_and_org(api_response, test_context):
    data = api_response["json"]
    service_ids = [str(s["id"]) for s in data.get("services", [])]
    org_ids = [str(o["id"]) for o in data.get("organisations", [])]
    assert str(test_context["service"].id) in service_ids
    assert str(test_context["organisation"].id) in org_ids
