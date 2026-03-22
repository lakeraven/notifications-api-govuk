"""
Step definitions for organisation branding management.
"""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from tests.app.db import create_email_branding, create_letter_branding, create_organisation

scenarios("../features/organisations/organisation_branding.feature")


# -- Given steps --


@given("an organisation exists", target_fixture="organisation")
def an_organisation_exists(notify_db_session):
    return create_organisation(name=f"Org {uuid.uuid4()}")


@given("the organisation has email branding options", target_fixture="email_branding")
def org_has_email_branding(notify_db_session, organisation):
    branding = create_email_branding(name=f"Email Brand {uuid.uuid4()}")
    organisation.email_branding_pool.append(branding)
    from app import db

    db.session.commit()
    return branding


@given(parsers.parse('email branding "{name}" exists'), target_fixture="email_branding")
def email_branding_named_exists(notify_db_session, name):
    return create_email_branding(name=name)


@given("the organisation has email branding in its pool", target_fixture="email_branding")
def org_has_email_branding_in_pool(notify_db_session, organisation):
    branding = create_email_branding(name=f"Pool Brand {uuid.uuid4()}")
    organisation.email_branding_pool.append(branding)
    from app import db

    db.session.commit()
    return branding


@given("the organisation has letter branding options", target_fixture="letter_branding")
def org_has_letter_branding(notify_db_session, organisation):
    branding = create_letter_branding(name=f"Letter Brand {uuid.uuid4()}")
    organisation.letter_branding_pool.append(branding)
    from app import db

    db.session.commit()
    return branding


@given(parsers.parse('letter branding "{name}" exists'), target_fixture="letter_branding")
def letter_branding_named_exists(notify_db_session, name):
    return create_letter_branding(name=name)


@given("the organisation has letter branding in its pool", target_fixture="letter_branding")
def org_has_letter_branding_in_pool(notify_db_session, organisation):
    branding = create_letter_branding(name=f"Pool Letterhead {uuid.uuid4()}")
    organisation.letter_branding_pool.append(branding)
    from app import db

    db.session.commit()
    return branding


# -- When steps --


@when("I get the email branding pool", target_fixture="api_response")
def get_email_branding_pool(admin_client, organisation):
    resp = admin_client.get(f"/organisations/{organisation.id}/email-branding-pool")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I add the email branding to the organisation's pool", target_fixture="api_response")
def add_email_branding_to_pool(admin_client, organisation, email_branding):
    resp = admin_client.post(
        f"/organisations/{organisation.id}/email-branding-pool",
        data={"branding_id": str(email_branding.id)},
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I remove the email branding from the pool", target_fixture="api_response")
def remove_email_branding_from_pool(admin_client, organisation, email_branding):
    resp = admin_client.delete(
        f"/organisations/{organisation.id}/email-branding-pool/{email_branding.id}"
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the letter branding pool", target_fixture="api_response")
def get_letter_branding_pool(admin_client, organisation):
    resp = admin_client.get(f"/organisations/{organisation.id}/letter-branding-pool")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I add the letter branding to the organisation's pool", target_fixture="api_response")
def add_letter_branding_to_pool(admin_client, organisation, letter_branding):
    resp = admin_client.post(
        f"/organisations/{organisation.id}/letter-branding-pool",
        data={"branding_id": str(letter_branding.id)},
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I remove the letter branding from the pool", target_fixture="api_response")
def remove_letter_branding_from_pool(admin_client, organisation, letter_branding):
    resp = admin_client.delete(
        f"/organisations/{organisation.id}/letter-branding-pool/{letter_branding.id}"
    )
    return {"status_code": resp.status_code, "json": resp.json}
