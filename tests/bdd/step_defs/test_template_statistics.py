"""
Step definitions for template statistics.

Tests run against the Flask test client using existing test fixtures.
"""

import json
from datetime import date, datetime, timedelta

from pytest_bdd import given, parsers, scenarios, then, when

from app.constants import SMS_TYPE
from tests.app.db import (
    create_ft_notification_status,
    create_notification,
    create_service,
    create_template,
)

# Load all scenarios from the feature file
scenarios("../features/templates/template_statistics.feature")


# -- Given steps --


@given("a service exists with templates and sent notifications", target_fixture="service")
def service_with_templates_and_notifications(notify_db_session, test_context):
    service = create_service()
    template = create_template(service, template_type=SMS_TYPE, content="Stats template")
    # Create fact table entries for today
    today = date.today()
    create_ft_notification_status(
        bst_date=today,
        template=template,
        notification_status="delivered",
        count=5,
    )
    test_context["service"] = service
    test_context["template"] = template
    return service


@given("a template has been used to send notifications", target_fixture="template")
def template_used_to_send(service, test_context, notify_db_session):
    template = test_context.get("template")
    if not template:
        template = create_template(service, template_type=SMS_TYPE, content="Used template")
    # Create a notification so the last-used date is populated
    create_notification(template=template, status="delivered")
    test_context["template"] = template
    return template


# -- When steps --


@when(
    parsers.parse("I get template statistics for the last {days:d} days"),
    target_fixture="api_response",
)
def get_template_statistics(admin_client, service, days):
    resp = admin_client.get(f"/service/{service.id}/template-statistics?whole_days={days}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the last used date for the template", target_fixture="api_response")
def get_last_used_date(admin_client, service, template, test_context):
    resp = admin_client.get(f"/service/{service.id}/template-statistics/last-used/{template.id}")
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then("the response should include template usage counts")
def response_has_usage_counts(api_response):
    data = api_response["json"]["data"]
    assert len(data) > 0
    for entry in data:
        assert "count" in entry
        assert "template_id" in entry
        assert "template_name" in entry


@then("the response should include a datetime")
def response_has_datetime(api_response):
    last_date = api_response["json"]["last_date_used"]
    assert last_date is not None
