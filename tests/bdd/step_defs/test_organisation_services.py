"""
Step definitions for organisation service management.
"""

import json
import uuid
from datetime import datetime

from pytest_bdd import given, parsers, scenarios, then, when

from tests.app.db import (
    create_annual_billing,
    create_ft_billing,
    create_organisation,
    create_service,
    create_template,
)

scenarios("../features/organisations/organisation_services.feature")


# -- Given steps --


@given("an organisation exists", target_fixture="organisation")
def an_organisation_exists(notify_db_session):
    return create_organisation(name=f"Org {uuid.uuid4()}")


@given(parsers.parse("the organisation has {count:d} services"), target_fixture="org_services")
def org_has_n_services(notify_db_session, organisation, count):
    services = []
    for i in range(count):
        svc = create_service(service_name=f"Org Service {uuid.uuid4()}")
        svc.organisation = organisation
        from app import db

        db.session.commit()
        services.append(svc)
    return services


@given("the organisation has services with usage data", target_fixture="org_services")
def org_has_services_with_usage(notify_db_session, organisation):
    svc = create_service(service_name=f"Usage Service {uuid.uuid4()}")
    svc.organisation = organisation
    from app import db

    db.session.commit()
    template = create_template(svc)
    create_ft_billing(datetime(2024, 4, 1).date(), template, notifications_sent=10)
    create_annual_billing(svc.id, free_sms_fragment_limit=250000, financial_year_start=2024)
    return [svc]


# -- When steps --


@when("I link the service to the organisation", target_fixture="api_response")
def link_service_to_org(admin_client, service, organisation):
    resp = admin_client.post(
        f"/organisations/{organisation.id}/service",
        data={"service_id": str(service.id)},
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I list services in the organisation", target_fixture="api_response")
def list_org_services(admin_client, organisation):
    resp = admin_client.get(f"/organisations/{organisation.id}/services")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get services with usage for the current year", target_fixture="api_response")
def get_services_with_usage(admin_client, organisation):
    resp = admin_client.get(f"/organisations/{organisation.id}/services-with-usage?year=2024")
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then(parsers.parse("the response should contain {count:d} services"))
def response_has_n_services(api_response, count):
    assert len(api_response["json"]) == count


@then("the response should include usage figures")
def response_has_usage(api_response):
    data = api_response["json"]
    assert isinstance(data, list)
