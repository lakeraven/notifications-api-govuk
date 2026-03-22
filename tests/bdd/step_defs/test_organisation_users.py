"""
Step definitions for organisation user management.
"""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from tests.app.db import create_invited_org_user, create_organisation, create_user

scenarios("../features/organisations/organisation_users.feature")


# -- Given steps --


@given("an organisation exists", target_fixture="organisation")
def an_organisation_exists(notify_db_session):
    return create_organisation(name=f"Org {uuid.uuid4()}")


@given("a user belongs to the organisation", target_fixture="user")
def user_belongs_to_org(notify_db_session, organisation):
    user = create_user(email=f"orguser-{uuid.uuid4()}@example.gov.uk")
    organisation.users.append(user)
    from app import db

    db.session.commit()
    return user


@given(parsers.parse("the organisation has {count:d} users"), target_fixture="org_users")
def org_has_n_users(notify_db_session, organisation, count):
    users = []
    for i in range(count):
        u = create_user(email=f"orguser-{uuid.uuid4()}@example.gov.uk")
        organisation.users.append(u)
        users.append(u)
    from app import db

    db.session.commit()
    return users


@given("the organisation has pending invitations", target_fixture="org_invitations")
def org_has_pending_invitations(notify_db_session, organisation):
    inviter = create_user(email=f"inviter-{uuid.uuid4()}@example.gov.uk")
    inv = create_invited_org_user(organisation, inviter, email_address=f"pending-{uuid.uuid4()}@example.gov.uk")
    return [inv]


@given("an invitation exists for the organisation", target_fixture="invitation")
def invitation_exists(notify_db_session, organisation):
    inviter = create_user(email=f"inviter-{uuid.uuid4()}@example.gov.uk")
    return create_invited_org_user(organisation, inviter, email_address=f"accept-{uuid.uuid4()}@example.gov.uk")


@given("an invitation with a token exists", target_fixture="invitation")
def invitation_with_token(notify_db_session, organisation):
    inviter = create_user(email=f"inviter-{uuid.uuid4()}@example.gov.uk")
    return create_invited_org_user(organisation, inviter, email_address=f"token-{uuid.uuid4()}@example.gov.uk")


# -- When steps --


@when("I add the user to the organisation", target_fixture="api_response")
def add_user_to_org(admin_client, user, organisation):
    resp = admin_client.post(f"/organisations/{organisation.id}/users/{user.id}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I remove the user from the organisation", target_fixture="api_response")
def remove_user_from_org(admin_client, user, organisation):
    resp = admin_client.delete(f"/organisations/{organisation.id}/users/{user.id}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I list users in the organisation", target_fixture="api_response")
def list_org_users(admin_client, organisation):
    resp = admin_client.get(f"/organisations/{organisation.id}/users")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I invite "{email}" to the organisation'),
    target_fixture="api_response",
)
def invite_user_to_org(admin_client, organisation, email):
    inviter = create_user(email=f"admin-{uuid.uuid4()}@example.gov.uk")
    resp = admin_client.post(
        f"/organisations/{organisation.id}/invite",
        data={
            "email_address": email,
            "invited_by": str(inviter.id),
            "permissions": "can_make_services_live",
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I list invitations for the organisation", target_fixture="api_response")
def list_invitations(admin_client, organisation):
    resp = admin_client.get(f"/organisations/{organisation.id}/invitations")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('the invitation status is updated to "{status}"'),
    target_fixture="api_response",
)
def update_invitation_status(admin_client, invitation, status):
    resp = admin_client.post(
        f"/organisations/invite/{invitation.id}",
        data={"status": status},
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I validate the invitation token", target_fixture="api_response")
def validate_invitation_token(admin_client, invitation):
    resp = admin_client.get(f"/organisations/invite/{invitation.id}")
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then(parsers.parse("the response should contain {count:d} users"))
def response_has_n_users(api_response, count):
    assert len(api_response["json"]) == count
