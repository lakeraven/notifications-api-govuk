"""Step definitions for service lifecycle BDD tests."""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from app.constants import EMAIL_TYPE, SMS_TYPE
from tests.app.db import (
    create_notification,
    create_service,
    create_template,
    create_user,
)

scenarios("../features/services/service_lifecycle.feature")


# -- Given steps --


@given("3 services exist", target_fixture="services")
def three_services_exist(notify_db_session):
    services = []
    for i in range(3):
        svc = create_service(service_name=f"Service {i + 1} {uuid.uuid4()}")
        services.append(svc)
    return services


@given("a service in trial mode exists", target_fixture="service")
def a_service_in_trial_mode(notify_db_session):
    return create_service(restricted=True)


@given("a service exists with changes in its history", target_fixture="service")
def a_service_with_history(notify_db_session, admin_client):
    service = create_service()
    # Update the service to create a history entry
    admin_client.post(
        f"/service/{service.id}",
        data={"name": f"Updated {service.name}"},
    )
    return service


@given("live services exist", target_fixture="services")
def live_services_exist(notify_db_session):
    services = []
    for i in range(2):
        svc = create_service(
            service_name=f"Live Service {i + 1} {uuid.uuid4()}",
            restricted=False,
            go_live_at="2024-01-01 00:00:00",
        )
        services.append(svc)
    return services


@given("a service exists with sent notifications", target_fixture="service")
def a_service_with_notifications(notify_db_session):
    service = create_service()
    template = create_template(service=service, template_type=SMS_TYPE)
    for _ in range(3):
        create_notification(template=template, status="delivered")
    return service


@given("a service exists with notifications sent from multiple templates", target_fixture="service")
def a_service_with_multiple_templates(notify_db_session):
    service = create_service()
    sms_template = create_template(service=service, template_type=SMS_TYPE, template_name="SMS Template")
    email_template = create_template(service=service, template_type=EMAIL_TYPE, template_name="Email Template")
    for _ in range(2):
        create_notification(template=sms_template, status="delivered")
    for _ in range(2):
        create_notification(template=email_template, status="delivered")
    return service


# -- When steps --


@when("I create a new service via the admin API", target_fixture="api_response")
def create_service_via_api(admin_client):
    user = create_user(email=f"creator-{uuid.uuid4()}@digital.cabinet-office.gov.uk")
    resp = admin_client.post(
        "/service",
        data={
            "name": f"New Service {uuid.uuid4()}",
            "user_id": str(user.id),
            "email_message_limit": 1000,
            "sms_message_limit": 1000,
            "letter_message_limit": 1000,
            "international_sms_message_limit": 1000,
            "restricted": True,
            "email_from": "test.service",
        },
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the service by ID", target_fixture="api_response")
def get_service_by_id(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I list all services", target_fixture="api_response")
def list_all_services(admin_client):
    resp = admin_client.get("/service")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I update the service name", target_fixture="api_response")
def update_service_name(admin_client, service, test_context):
    new_name = f"Updated Service {uuid.uuid4()}"
    test_context["new_name"] = new_name
    resp = admin_client.post(
        f"/service/{service.id}",
        data={"name": new_name},
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I archive the service", target_fixture="api_response")
def archive_service(admin_client, service):
    resp = admin_client.post(f"/service/{service.id}/archive")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the service history", target_fixture="api_response")
def get_service_history(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/history")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I search for services by name", target_fixture="api_response")
def search_services_by_name(admin_client, service):
    resp = admin_client.get(
        f"/service/find-services-by-name?service_name={service.name}"
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get live services data", target_fixture="api_response")
def get_live_services_data(admin_client):
    resp = admin_client.get("/service/live-services-data")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the service notification statistics", target_fixture="api_response")
def get_service_statistics(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/statistics")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the service monthly notification statistics", target_fixture="api_response")
def get_monthly_stats(admin_client, service):
    from datetime import datetime

    year = datetime.utcnow().year
    resp = admin_client.get(f"/service/{service.id}/notifications/monthly?year={year}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the service monthly template usage", target_fixture="api_response")
def get_monthly_template_usage(admin_client, service):
    from datetime import datetime

    year = datetime.utcnow().year
    resp = admin_client.get(
        f"/service/{service.id}/notifications/templates_usage/monthly?year={year}"
    )
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then("the response should contain the service details")
def response_has_service_details(api_response):
    data = api_response["json"]["data"]
    assert "id" in data
    assert "name" in data


@then("the response should contain a list of services")
def response_has_service_list(api_response):
    data = api_response["json"]["data"]
    assert isinstance(data, list)
    assert len(data) >= 1


@then("the response should contain the updated service name")
def response_has_updated_name(api_response, test_context):
    data = api_response["json"]["data"]
    assert data["name"] == test_context["new_name"]


@then("the service should be archived")
def service_is_archived(api_response, admin_client, service):
    resp = admin_client.get(f"/service/{service.id}")
    assert resp.json["data"]["active"] is False


@then("the response should contain service history")
def response_has_service_history(api_response):
    data = api_response["json"]["data"]
    assert "service_history" in data
    assert "api_key_history" in data
    assert "template_history" in data
    assert "events" in data


@then("the response should contain the matching service")
def response_has_matching_service(api_response, service):
    data = api_response["json"]["data"]
    assert isinstance(data, list)
    assert len(data) >= 1
    names = [s["name"] for s in data]
    assert service.name in names


@then("the response should contain live services data")
def response_has_live_data(api_response):
    data = api_response["json"]["data"]
    assert isinstance(data, list)


@then("the response should contain notification statistics")
def response_has_notification_stats(api_response):
    data = api_response["json"]["data"]
    assert isinstance(data, dict)


@then("the response should contain monthly notification statistics")
def response_has_monthly_stats(api_response):
    data = api_response["json"]["data"]
    assert isinstance(data, dict)


@then("the response should contain monthly template usage data")
def response_has_template_usage(api_response):
    data = api_response["json"]
    # The monthly template usage endpoint returns a list
    assert isinstance(data, (list, dict))
