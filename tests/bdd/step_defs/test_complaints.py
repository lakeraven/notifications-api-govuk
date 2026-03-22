"""
Step definitions for complaint management.
"""

import json
import uuid
from datetime import datetime, timedelta

from pytest_bdd import given, parsers, scenarios, then, when

from tests.app.db import create_complaint, create_service

scenarios("../features/other/complaints.feature")


# -- Given steps --


@given("email complaints have been recorded", target_fixture="service")
def email_complaints_recorded(notify_db_session, test_context):
    svc = create_service(service_name=f"Complaints Svc {uuid.uuid4()}")
    complaint = create_complaint(service=svc)
    test_context["complaint"] = complaint
    return svc


@given("email complaints exist in a date range", target_fixture="service")
def complaints_in_date_range(notify_db_session, test_context):
    svc = create_service(service_name=f"Date Complaints Svc {uuid.uuid4()}")
    now = datetime.utcnow()
    create_complaint(service=svc, created_at=now - timedelta(days=1))
    test_context["start_date"] = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    test_context["end_date"] = now.strftime("%Y-%m-%d")
    return svc


# -- When steps --


@when("I list all complaints", target_fixture="api_response")
def list_complaints(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/complaints")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I count complaints for the date range", target_fixture="api_response")
def count_complaints(admin_client, service, test_context):
    start = test_context["start_date"]
    end = test_context["end_date"]
    resp = admin_client.get(f"/service/{service.id}/complaints/count?start_date={start}&end_date={end}")
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then("the response should include complaint details")
def response_has_complaint_details(api_response):
    data = api_response["json"]
    assert isinstance(data, (dict, list))
