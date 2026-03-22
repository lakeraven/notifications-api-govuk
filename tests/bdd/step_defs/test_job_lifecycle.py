"""
Step definitions for job (bulk send) lifecycle.

Tests run against the Flask test client using existing test fixtures.
"""

import json
import uuid
from datetime import datetime, timedelta
from unittest.mock import ANY

from pytest_bdd import given, parsers, scenarios, then, when

from app.constants import EMAIL_TYPE, LETTER_TYPE, SMS_TYPE
from tests.app.db import (
    create_job,
    create_notification,
    create_service,
    create_template,
)

# Load all scenarios from the feature file
scenarios("../features/jobs/job_lifecycle.feature")


# -- Given steps --


@given("a service exists with templates", target_fixture="service")
def service_with_templates(notify_db_session):
    return create_service(service_permissions=[SMS_TYPE, EMAIL_TYPE, LETTER_TYPE])


@given("an SMS template exists", target_fixture="template")
def an_sms_template(service, notify_db_session):
    return create_template(service, template_type=SMS_TYPE, content="Job SMS ((name))")


@given("a job exists", target_fixture="job")
def a_job_exists(service, notify_db_session, test_context):
    template = create_template(service, template_type=SMS_TYPE, content="Job template")
    job = create_job(template, notification_count=10)
    test_context["template"] = template
    return job


@given("3 jobs exist for the service", target_fixture="test_context")
def three_jobs_exist(service, test_context, notify_db_session):
    template = create_template(service, template_type=SMS_TYPE, content="Multi job template")
    jobs = [create_job(template, notification_count=5) for _ in range(3)]
    test_context["jobs"] = jobs
    test_context["template"] = template
    return test_context


@given("a scheduled job exists", target_fixture="job")
def a_scheduled_job_exists(service, notify_db_session):
    template = create_template(service, template_type=SMS_TYPE, content="Scheduled template")
    return create_job(
        template,
        job_status="scheduled",
        scheduled_for=datetime.utcnow() + timedelta(hours=24),
    )


@given("a letter job exists", target_fixture="job")
def a_letter_job_exists(service, notify_db_session):
    template = create_template(
        service,
        template_type=LETTER_TYPE,
        content="Letter job content",
        subject="Letter subject",
    )
    job = create_job(template, notification_count=3, job_status="finished")
    # Create notifications for the job so the cancel check passes
    for _ in range(3):
        create_notification(
            template=template,
            job=job,
            status="created",
        )
    return job


@given("a job has been processed with notifications", target_fixture="job")
def job_with_notifications(service, test_context, notify_db_session):
    template = create_template(service, template_type=SMS_TYPE, content="Processed template")
    job = create_job(template, notification_count=3, job_status="finished")
    notifications = []
    for i in range(3):
        n = create_notification(template=template, job=job, status="delivered")
        notifications.append(n)
    test_context["notifications"] = notifications
    test_context["template"] = template
    return job


@given(
    parsers.parse("a job has been processed with {count:d} notifications"),
    target_fixture="job",
)
def job_with_n_notifications(service, count, test_context, notify_db_session):
    template = create_template(service, template_type=SMS_TYPE, content="Counted template")
    job = create_job(template, notification_count=count, job_status="finished")
    for _ in range(count):
        create_notification(template=template, job=job, status="delivered")
    test_context["template"] = template
    test_context["expected_count"] = count
    return job


@given("scheduled jobs exist", target_fixture="test_context")
def scheduled_jobs_exist(service, test_context, notify_db_session):
    template = create_template(service, template_type=SMS_TYPE, content="Sched stats template")
    for i in range(2):
        create_job(
            template,
            job_status="scheduled",
            scheduled_for=datetime.utcnow() + timedelta(hours=i + 1),
        )
    test_context["template"] = template
    return test_context


# -- When steps --


@when("I create a job for the template with a CSV file", target_fixture="api_response")
def create_job_with_csv(admin_client, service, template, mocker):
    job_id = str(uuid.uuid4())
    # Mock S3 metadata retrieval that the job creation endpoint calls
    mocker.patch(
        "app.job.rest.get_job_metadata_from_s3",
        return_value={
            "template_id": str(template.id),
            "original_file_name": "test.csv",
            "notification_count": 1,
            "valid": "True",
        },
    )
    mocker.patch("app.celery.tasks.process_job.apply_async")
    data = {
        "id": job_id,
        "template_id": str(template.id),
        "original_file_name": "test.csv",
        "notification_count": 1,
        "created_by": str(service.created_by.id),
    }
    resp = admin_client.post(f"/service/{service.id}/job", data=data)
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the job by ID", target_fixture="api_response")
def get_job_by_id(admin_client, service, job):
    resp = admin_client.get(f"/service/{service.id}/job/{job.id}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I list jobs for the service", target_fixture="api_response")
def list_jobs(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/job")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I cancel the job", target_fixture="api_response")
def cancel_job(admin_client, service, job):
    resp = admin_client.post(f"/service/{service.id}/job/{job.id}/cancel", data={})
    return {"status_code": resp.status_code, "json": resp.json}


@when("I cancel the letter job", target_fixture="api_response")
def cancel_letter_job(admin_client, service, job, mocker):
    mocker.patch("app.job.rest.dao_cancel_letter_job_notifications")
    resp = admin_client.post(f"/service/{service.id}/job/{job.id}/cancel-letter-job", data={})
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get notifications for the job", target_fixture="api_response")
def get_job_notifications(admin_client, service, job):
    resp = admin_client.get(f"/service/{service.id}/job/{job.id}/notifications")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get the notification count for the job", target_fixture="api_response")
def get_notification_count(admin_client, service, job):
    resp = admin_client.get(f"/service/{service.id}/job/{job.id}/notification_count")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I get scheduled job stats for the service", target_fixture="api_response")
def get_scheduled_job_stats(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/job/scheduled-job-stats")
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then(parsers.parse('the job should have status "{status}"'))
def job_has_status(api_response, status):
    assert api_response["json"]["data"]["job_status"] == status


@then("the response should include job statistics")
def response_has_job_stats(api_response):
    data = api_response["json"]["data"]
    assert "id" in data
    assert "statistics" in data


@then("the response should contain jobs")
def response_has_jobs(api_response):
    data = api_response["json"]["data"]
    assert len(data) > 0


@then("the response should contain the job's notifications")
def response_has_notifications(api_response):
    data = api_response["json"]
    notifications = data.get("notifications", data.get("data", []))
    assert len(notifications) > 0


@then(parsers.parse("the count should be {expected_count:d}"))
def count_matches(api_response, expected_count):
    assert api_response["json"]["count"] == expected_count
