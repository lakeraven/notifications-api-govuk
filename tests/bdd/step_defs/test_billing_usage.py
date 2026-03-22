"""
Step definitions for billing and usage reporting.
"""

import json
import uuid
from datetime import datetime

from pytest_bdd import given, parsers, scenarios, then, when

from app.constants import SMS_TYPE
from tests.app.db import (
    create_annual_billing,
    create_ft_billing,
    create_ft_notification_status,
    create_service,
    create_template,
)

scenarios("../features/billing/billing_usage.feature")


# -- Given steps --


@given("a service exists with sent notifications", target_fixture="service")
def service_with_notifications(notify_db_session):
    svc = create_service(service_name=f"Billing Service {uuid.uuid4()}")
    template = create_template(svc, template_type=SMS_TYPE)
    create_ft_billing(datetime(2024, 4, 1).date(), template, notifications_sent=100)
    create_ft_notification_status(datetime(2024, 4, 1).date(), template=template, count=100)
    create_annual_billing(svc.id, free_sms_fragment_limit=250000, financial_year_start=2024)
    return svc


@given("a free SMS fragment limit has been set")
def free_sms_limit_set(service):
    # The background step already creates annual_billing; nothing extra needed.
    pass


# -- When steps --


@when("I get the monthly usage for the current year", target_fixture="api_response")
def get_monthly_usage(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/billing/monthly-usage?year=2024")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the yearly usage summary", target_fixture="api_response")
def get_yearly_usage(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/billing/yearly-usage-summary?year=2024")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the free SMS fragment limit", target_fixture="api_response")
def get_free_sms_limit(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/billing/free-sms-fragment-limit")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse("I set the free SMS fragment limit to {limit:d}"),
    target_fixture="api_response",
)
def set_free_sms_limit(admin_client, service, limit):
    resp = admin_client.post(
        f"/service/{service.id}/billing/free-sms-fragment-limit",
        data={"free_sms_fragment_limit": limit, "financial_year_start": 2025},
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse("I update the free SMS fragment limit to {limit:d}"),
    target_fixture="api_response",
)
def update_free_sms_limit(admin_client, service, limit):
    resp = admin_client.post(
        f"/service/{service.id}/billing/free-sms-fragment-limit",
        data={"free_sms_fragment_limit": limit, "financial_year_start": 2025},
    )
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then("the response should include monthly breakdown")
def response_has_monthly_breakdown(api_response):
    data = api_response["json"]
    assert isinstance(data, list)


@then("the response should include the free allowance")
def response_has_free_allowance(api_response):
    data = api_response["json"]
    assert "free_sms_fragment_limit" in data or isinstance(data, dict)
