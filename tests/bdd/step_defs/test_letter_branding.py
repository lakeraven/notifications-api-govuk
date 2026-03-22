"""
Step definitions for letter branding management.
"""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from tests.app.db import create_letter_branding, create_organisation, create_service

scenarios("../features/branding/letter_branding.feature")


# -- Given steps --


@given("letter branding options exist", target_fixture="letter_branding")
def letter_branding_options_exist(notify_db_session):
    return create_letter_branding(name=f"Letterhead {uuid.uuid4()}")


@given(parsers.parse('letter branding "{name}" exists'), target_fixture="letter_branding")
def letter_branding_named_exists(notify_db_session, name):
    return create_letter_branding(name=name)


@given("letter branding exists", target_fixture="letter_branding")
def letter_branding_exists(notify_db_session):
    return create_letter_branding(name=f"Letterhead {uuid.uuid4()}")


@given("letter branding is used by services", target_fixture="letter_branding")
def letter_branding_used_by_services(notify_db_session):
    branding = create_letter_branding(name=f"Used Letterhead {uuid.uuid4()}")
    org = create_organisation(name=f"Letter Org {uuid.uuid4()}", letter_branding_id=branding.id)
    return branding


# -- When steps --


@when("I list all letter branding", target_fixture="api_response")
def list_letter_branding(admin_client):
    resp = admin_client.get("/letter-branding")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I create letter branding named "{name}"'),
    target_fixture="api_response",
)
def create_letter_branding_api(admin_client, name):
    resp = admin_client.post(
        "/letter-branding",
        data={"name": name, "filename": name.lower().replace(" ", "-")},
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the letter branding by ID", target_fixture="api_response")
def get_letter_branding_by_id(admin_client, letter_branding):
    resp = admin_client.get(f"/letter-branding/{letter_branding.id}")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I update the letter branding name to "{name}"'),
    target_fixture="api_response",
)
def update_letter_branding(admin_client, letter_branding, name):
    resp = admin_client.post(
        f"/letter-branding/{letter_branding.id}",
        data={"name": name, "filename": letter_branding.filename},
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the orgs and services for the letter branding", target_fixture="api_response")
def get_orgs_services_for_letter_branding(admin_client, letter_branding):
    resp = admin_client.get(f"/letter-branding/{letter_branding.id}/orgs-and-services")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I request a unique name based on "{name}"'),
    target_fixture="api_response",
)
def get_unique_name(admin_client, name):
    resp = admin_client.get(f"/letter-branding/get-unique-name?name={name}")
    return {"status_code": resp.status_code, "json": resp.json}
