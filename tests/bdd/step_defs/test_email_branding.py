"""
Step definitions for email branding management.
"""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from tests.app.db import create_email_branding, create_organisation, create_service

scenarios("../features/branding/email_branding.feature")


# -- Given steps --


@given("email branding options exist", target_fixture="email_branding")
def email_branding_options_exist(notify_db_session):
    return create_email_branding(name=f"Brand {uuid.uuid4()}")


@given(parsers.parse('email branding "{name}" exists'), target_fixture="email_branding")
def email_branding_named_exists(notify_db_session, name):
    return create_email_branding(name=name)


@given("email branding exists", target_fixture="email_branding")
def email_branding_exists(notify_db_session):
    return create_email_branding(name=f"Brand {uuid.uuid4()}")


@given("email branding is used by services", target_fixture="email_branding")
def email_branding_used_by_services(notify_db_session):
    branding = create_email_branding(name=f"Used Brand {uuid.uuid4()}")
    svc = create_service(service_name=f"Branded Svc {uuid.uuid4()}", email_branding=branding)
    return branding


# -- When steps --


@when("I list all email branding", target_fixture="api_response")
def list_email_branding(admin_client):
    resp = admin_client.get("/email-branding")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I create email branding named "{name}" with colour "{colour}"'),
    target_fixture="api_response",
)
def create_email_branding_api(admin_client, name, colour):
    resp = admin_client.post(
        "/email-branding",
        data={
            "name": name,
            "colour": colour,
            "logo": "test_x2.png",
            "alt_text": name,
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the email branding by ID", target_fixture="api_response")
def get_email_branding_by_id(admin_client, email_branding):
    resp = admin_client.get(f"/email-branding/{email_branding.id}")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I update the branding name to "{name}"'),
    target_fixture="api_response",
)
def update_email_branding(admin_client, email_branding, name):
    resp = admin_client.post(
        f"/email-branding/{email_branding.id}",
        data={
            "name": name,
            "colour": email_branding.colour,
            "logo": email_branding.logo,
            "alt_text": name,
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I archive the email branding", target_fixture="api_response")
def archive_email_branding(admin_client, email_branding):
    resp = admin_client.post(f"/email-branding/{email_branding.id}/archive")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the orgs and services for the branding", target_fixture="api_response")
def get_orgs_and_services_for_branding(admin_client, email_branding):
    resp = admin_client.get(f"/email-branding/{email_branding.id}/orgs-and-services")
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then(parsers.parse('the branding name should be "{name}"'))
def branding_name_is(api_response, name):
    assert api_response["json"]["name"] == name
