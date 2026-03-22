"""
Step definitions for organisation lifecycle management.
"""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from tests.app.db import create_domain, create_organisation

scenarios("../features/organisations/organisation_lifecycle.feature")


# -- Given steps --


@given(parsers.parse('an organisation "{name}" exists'), target_fixture="organisation")
def an_organisation_named_exists(notify_db_session, name):
    return create_organisation(name=name)


@given(parsers.parse("{count:d} organisations exist"), target_fixture="organisations")
def n_organisations_exist(notify_db_session, count):
    return [create_organisation(name=f"Org {i}") for i in range(count)]


@given("an organisation exists", target_fixture="organisation")
def an_organisation_exists(notify_db_session):
    return create_organisation(name=f"Org {uuid.uuid4()}")


@given(parsers.parse('an organisation owns domain "{domain}"'), target_fixture="organisation")
def an_organisation_owns_domain(notify_db_session, domain):
    org = create_organisation(name="Domain Org")
    create_domain(domain, org.id)
    return org


# -- When steps --


@when(
    parsers.parse('I create an organisation named "{name}" of type "{org_type}"'),
    target_fixture="api_response",
)
def create_org(admin_client, name, org_type):
    resp = admin_client.post(
        "/organisations",
        data={"name": name, "organisation_type": org_type, "crown": True},
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the organisation by ID", target_fixture="api_response")
def get_org_by_id(admin_client, organisation):
    resp = admin_client.get(f"/organisations/{organisation.id}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I list all organisations", target_fixture="api_response")
def list_all_orgs(admin_client):
    resp = admin_client.get("/organisations")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I update the organisation name to "{name}"'),
    target_fixture="api_response",
)
def update_org(admin_client, organisation, name):
    resp = admin_client.post(
        f"/organisations/{organisation.id}",
        data={"name": name},
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I archive the organisation", target_fixture="api_response")
def archive_org(admin_client, organisation):
    resp = admin_client.post(f"/organisations/{organisation.id}/archive")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I look up the organisation by domain "{domain}"'),
    target_fixture="api_response",
)
def lookup_by_domain(admin_client, domain):
    resp = admin_client.get(f"/organisations/by-domain?domain={domain}")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I search organisations for "{query}"'),
    target_fixture="api_response",
)
def search_orgs(admin_client, query):
    resp = admin_client.get(f"/organisations?q={query}")
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then(parsers.parse('the organisation name should be "{name}"'))
def org_name_should_be(api_response, name):
    assert api_response["json"]["name"] == name


@then(parsers.parse("the response should contain at least {count:d} organisations"))
def response_has_at_least_n_orgs(api_response, count):
    assert len(api_response["json"]) >= count


@then("the response should contain the organisation")
def response_contains_org(api_response):
    assert api_response["json"] is not None
    assert "id" in api_response["json"] or "name" in api_response["json"]


@then(parsers.parse('the results should include "{name}"'))
def results_include_name(api_response, name):
    data = api_response["json"]
    names = [org["name"] for org in data] if isinstance(data, list) else []
    assert name in names, f"Expected '{name}' in {names}"
