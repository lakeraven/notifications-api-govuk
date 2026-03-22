"""
Step definitions for notification provider management.
"""

import json

from pytest_bdd import given, parsers, scenarios, then, when

from app.models import ProviderDetails

scenarios("../features/providers/provider_details.feature")


# -- Given steps --


@given("a provider exists", target_fixture="provider")
def a_provider_exists(notify_db_session):
    provider = ProviderDetails.query.first()
    assert provider is not None, "No seeded providers found"
    return provider


@given("a provider has been updated", target_fixture="provider")
def provider_has_been_updated(notify_db_session, admin_client):
    provider = ProviderDetails.query.first()
    # Trigger an update to create a version history entry
    admin_client.post(
        f"/provider-details/{provider.id}",
        data={"priority": provider.priority},
    )
    return provider


@given("an SMS provider exists", target_fixture="provider")
def an_sms_provider_exists(notify_db_session):
    provider = ProviderDetails.query.filter_by(notification_type="sms").first()
    assert provider is not None, "No seeded SMS providers found"
    return provider


# -- When steps --


@when("I list all providers", target_fixture="api_response")
def list_all_providers(admin_client):
    resp = admin_client.get("/provider-details")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the provider by ID", target_fixture="api_response")
def get_provider_by_id(admin_client, provider):
    resp = admin_client.get(f"/provider-details/{provider.id}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the provider version history", target_fixture="api_response")
def get_provider_versions(admin_client, provider):
    resp = admin_client.get(f"/provider-details/{provider.id}/versions")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse("I update the provider priority to {priority:d}"),
    target_fixture="api_response",
)
def update_provider_priority(admin_client, provider, admin_user, priority):
    resp = admin_client.post(
        f"/provider-details/{provider.id}",
        data={"priority": priority, "created_by": str(admin_user.id)},
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I set the provider to inactive", target_fixture="api_response")
def deactivate_provider(admin_client, provider, admin_user):
    resp = admin_client.post(
        f"/provider-details/{provider.id}",
        data={"active": False, "created_by": str(admin_user.id)},
    )
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then("the response should include SMS and email providers")
def response_has_sms_and_email(api_response):
    data = api_response["json"]
    types = {p.get("notification_type") for p in data} if isinstance(data, list) else set()
    assert "sms" in types or "email" in types


@then("each provider should have a priority and active status")
def providers_have_priority_and_active(api_response):
    data = api_response["json"]
    for p in data:
        assert "priority" in p
        assert "active" in p


@then("the response should include the provider identifier")
def response_has_identifier(api_response):
    assert "identifier" in api_response["json"]


@then("the response should include version entries")
def response_has_versions(api_response):
    data = api_response["json"]
    assert isinstance(data, list)


@then(parsers.parse("the provider priority should be {priority:d}"))
def provider_priority_is(api_response, priority):
    assert api_response["json"]["priority"] == priority


@then("the provider should be inactive")
def provider_is_inactive(api_response):
    assert api_response["json"]["active"] is False
