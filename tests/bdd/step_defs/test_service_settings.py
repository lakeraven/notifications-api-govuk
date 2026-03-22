"""Step definitions for service settings BDD tests."""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from app.constants import EMAIL_TYPE, SMS_TYPE
from app.dao.organisation_dao import dao_add_service_to_organisation
from tests.app.db import (
    create_letter_contact,
    create_organisation,
    create_reply_to_email,
    create_service,
    create_service_data_retention,
    create_service_guest_list,
    create_service_sms_sender,
    create_user,
)

scenarios("../features/services/service_settings.feature")


# -- Given steps --


@given("the service has an email reply-to address", target_fixture="reply_to")
def the_service_has_reply_to(service):
    return create_reply_to_email(service, email_address="reply@example.gov.uk")


@given("the service has an SMS sender", target_fixture="sms_sender")
def the_service_has_sms_sender(service):
    return create_service_sms_sender(service, sms_sender="TestSender", is_default=False)


@given("the service has a letter contact", target_fixture="letter_contact")
def the_service_has_letter_contact(service):
    return create_letter_contact(service, contact_block="123 Test Street\nLondon\nSW1A 1AA")


@given("the service has a guest list", target_fixture="guest_list")
def the_service_has_guest_list(service):
    create_service_guest_list(service, email_address="allowed@example.gov.uk")
    return True


@given("the service has data retention settings", target_fixture="data_retention")
def the_service_has_data_retention(service):
    return create_service_data_retention(service, notification_type="sms", days_of_retention=7)


@given("the service is linked to an organisation", target_fixture="organisation")
def the_service_is_linked_to_org(service):
    org = create_organisation(name=f"Test Org {uuid.uuid4()}")
    dao_add_service_to_organisation(service, org.id)
    return org


# -- When steps: Email reply-to --


@when("I list the email reply-to addresses for the service", target_fixture="api_response")
def list_reply_to_addresses(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/email-reply-to")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I add an email reply-to address to the service", target_fixture="api_response")
def add_reply_to_address(admin_client, service):
    resp = admin_client.post(
        f"/service/{service.id}/email-reply-to",
        data={
            "email_address": f"new-reply-{uuid.uuid4()}@example.gov.uk",
            "is_default": False,
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I archive the email reply-to address", target_fixture="api_response")
def archive_reply_to_address(admin_client, service, reply_to):
    resp = admin_client.post(
        f"/service/{service.id}/email-reply-to/{reply_to.id}/archive",
    )
    return {"status_code": resp.status_code, "json": resp.json}


# -- When steps: SMS senders --


@when("I list the SMS senders for the service", target_fixture="api_response")
def list_sms_senders(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/sms-sender")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I add an SMS sender to the service", target_fixture="api_response")
def add_sms_sender(admin_client, service):
    resp = admin_client.post(
        f"/service/{service.id}/sms-sender",
        data={
            "sms_sender": "NewSender",
            "is_default": False,
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I update the SMS sender", target_fixture="api_response")
def update_sms_sender(admin_client, service, sms_sender):
    resp = admin_client.post(
        f"/service/{service.id}/sms-sender/{sms_sender.id}",
        data={
            "sms_sender": "UpdatedSender",
            "is_default": False,
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


# -- When steps: Letter contacts --


@when("I list the letter contacts for the service", target_fixture="api_response")
def list_letter_contacts(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/letter-contact")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I add a letter contact to the service", target_fixture="api_response")
def add_letter_contact(admin_client, service):
    resp = admin_client.post(
        f"/service/{service.id}/letter-contact",
        data={
            "contact_block": "456 New Street\nLondon\nEC1A 1BB",
            "is_default": False,
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


# -- When steps: Guest list --


@when("I get the guest list for the service", target_fixture="api_response")
def get_guest_list(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/guest-list")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I update the guest list for the service", target_fixture="api_response")
def update_guest_list(admin_client, service):
    resp = admin_client.put(
        f"/service/{service.id}/guest-list",
        data={
            "email_addresses": ["new-guest@example.gov.uk"],
            "phone_numbers": ["+447700900111"],
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


# -- When steps: Data retention --


@when("I list the data retention settings for the service", target_fixture="api_response")
def list_data_retention(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/data-retention")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I create a data retention setting for the service", target_fixture="api_response")
def create_data_retention(admin_client, service):
    resp = admin_client.post(
        f"/service/{service.id}/data-retention",
        data={
            "notification_type": "email",
            "days_of_retention": 5,
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I update the data retention setting", target_fixture="api_response")
def update_data_retention(admin_client, service, data_retention):
    resp = admin_client.post(
        f"/service/{service.id}/data-retention/{data_retention.id}",
        data={
            "days_of_retention": 14,
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


# -- When steps: Organisation --


@when("I get the organisation for the service", target_fixture="api_response")
def get_organisation_for_service(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/organisation")
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then("the response should contain a list of email reply-to addresses")
def response_has_reply_to_list(api_response):
    data = api_response["json"]
    assert isinstance(data, list)


@then("the response should contain the new email reply-to address")
def response_has_new_reply_to(api_response):
    data = api_response["json"]["data"]
    assert "email_address" in data
    assert "id" in data


@then("the email reply-to address should be archived")
def reply_to_is_archived(api_response):
    data = api_response["json"]["data"]
    assert data["archived"] is True


@then("the response should contain a list of SMS senders")
def response_has_sms_senders_list(api_response):
    data = api_response["json"]
    assert isinstance(data, list)


@then("the response should contain the new SMS sender")
def response_has_new_sms_sender(api_response):
    data = api_response["json"]
    assert "sms_sender" in data
    assert "id" in data


@then("the response should contain the updated SMS sender")
def response_has_updated_sms_sender(api_response):
    data = api_response["json"]
    assert data["sms_sender"] == "UpdatedSender"


@then("the response should contain a list of letter contacts")
def response_has_letter_contacts_list(api_response):
    data = api_response["json"]
    assert isinstance(data, list)


@then("the response should contain the new letter contact")
def response_has_new_letter_contact(api_response):
    data = api_response["json"]["data"]
    assert "contact_block" in data
    assert "id" in data


@then("the response should contain the guest list")
def response_has_guest_list(api_response):
    data = api_response["json"]
    assert "email_addresses" in data
    assert "phone_numbers" in data


@then("the guest list should be updated")
def guest_list_is_updated(api_response):
    # PUT guest-list returns 204 with no body
    assert api_response["status_code"] == 204


@then("the response should contain a list of data retention settings")
def response_has_data_retention_list(api_response):
    data = api_response["json"]
    assert isinstance(data, list)


@then("the response should contain the new data retention setting")
def response_has_new_data_retention(api_response):
    data = api_response["json"]["result"]
    assert "notification_type" in data
    assert "days_of_retention" in data


@then("the data retention setting should be updated")
def data_retention_is_updated(api_response):
    # POST data-retention/{id} returns 204 with no body
    assert api_response["status_code"] == 204


@then("the response should contain the organisation details")
def response_has_organisation(api_response, organisation):
    data = api_response["json"]
    assert data["name"] == organisation.name


@then("the response should be empty for organisation")
def response_is_empty_org(api_response):
    data = api_response["json"]
    assert data == {}
