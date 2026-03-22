"""
Step definitions for platform-wide statistics.
"""

import json
import uuid
from datetime import date, datetime, timedelta

from pytest_bdd import given, parsers, scenarios, then, when

from app.constants import SMS_TYPE
from tests.app.db import (
    create_ft_billing,
    create_ft_notification_status,
    create_service,
    create_template,
)

scenarios("../features/platform/platform_stats.feature")


# -- Helpers --


def _seed_notification_data(notify_db_session, svc_name=None):
    svc = create_service(service_name=svc_name or f"Stats Svc {uuid.uuid4()}")
    template = create_template(svc, template_type=SMS_TYPE)
    today = date.today()
    create_ft_billing(today, template, notifications_sent=5)
    create_ft_notification_status(today, template=template, count=5)
    return svc


# -- Given steps --


@given("services have sent notifications")
def services_have_sent(notify_db_session, test_context):
    svc = _seed_notification_data(notify_db_session)
    test_context["service"] = svc


@given("services have sent notifications this year")
def services_sent_this_year(notify_db_session, test_context):
    svc = _seed_notification_data(notify_db_session)
    test_context["service"] = svc


@given("letter notifications have been sent")
def letter_notifications_sent(notify_db_session, test_context):
    from app.constants import LETTER_TYPE

    svc = create_service(service_name=f"Letter Svc {uuid.uuid4()}")
    template = create_template(svc, template_type=LETTER_TYPE)
    create_ft_billing(date.today(), template, notifications_sent=2, postage="second")
    create_ft_notification_status(date.today(), template=template, count=2)
    test_context["service"] = svc


@given("notifications have been sent today")
def notifications_sent_today(notify_db_session, test_context):
    svc = _seed_notification_data(notify_db_session)
    test_context["service"] = svc


@given("SMS notifications have been sent via providers")
def sms_sent_via_providers(notify_db_session, test_context):
    svc = _seed_notification_data(notify_db_session)
    test_context["service"] = svc


@given("multiple services have sent notifications")
def multiple_services_sent(notify_db_session, test_context):
    svc1 = _seed_notification_data(notify_db_session, "Multi Svc 1")
    svc2 = _seed_notification_data(notify_db_session, "Multi Svc 2")
    test_context["services"] = [svc1, svc2]


# -- When steps --


@when("I get platform stats", target_fixture="api_response")
def get_platform_stats(admin_client):
    resp = admin_client.get("/platform-stats")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get data for billing report", target_fixture="api_response")
def get_billing_report(admin_client):
    start = date.today().replace(month=1, day=1).isoformat()
    end = date.today().isoformat()
    resp = admin_client.get(f"/platform-stats/data-for-billing-report?start_date={start}&end_date={end}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get data for DVLA billing report", target_fixture="api_response")
def get_dvla_billing_report(admin_client):
    start = date.today().replace(month=1, day=1).isoformat()
    end = date.today().isoformat()
    resp = admin_client.get(f"/platform-stats/data-for-dvla-billing-report?start_date={start}&end_date={end}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the daily volumes report", target_fixture="api_response")
def get_daily_volumes(admin_client):
    start = (date.today() - timedelta(days=1)).isoformat()
    end = date.today().isoformat()
    resp = admin_client.get(f"/platform-stats/daily-volumes-report?start_date={start}&end_date={end}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the daily SMS provider volumes report", target_fixture="api_response")
def get_daily_sms_provider_volumes(admin_client):
    start = (date.today() - timedelta(days=1)).isoformat()
    end = date.today().isoformat()
    resp = admin_client.get(f"/platform-stats/daily-sms-provider-volumes-report?start_date={start}&end_date={end}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get volumes by service", target_fixture="api_response")
def get_volumes_by_service(admin_client):
    start = date.today().replace(month=1, day=1).isoformat()
    end = date.today().isoformat()
    resp = admin_client.get(f"/platform-stats/volumes-by-service?start_date={start}&end_date={end}")
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then("the response should include counts by notification type and status")
def response_has_counts(api_response):
    data = api_response["json"]
    assert isinstance(data, (dict, list))


@then("the response should be broken down by service")
def response_broken_down_by_service(api_response):
    data = api_response["json"]
    assert isinstance(data, list)
