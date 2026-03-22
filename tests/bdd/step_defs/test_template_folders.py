"""
Step definitions for template folder management.

Tests run against the Flask test client using existing test fixtures.
"""

import json

from pytest_bdd import given, parsers, scenarios, then, when

from app.constants import SMS_TYPE
from tests.app.db import (
    create_template,
    create_template_folder,
)

# Load all scenarios from the feature file
scenarios("../features/templates/template_folders.feature")


# -- Given steps --


@given("the service has 2 template folders", target_fixture="test_context")
def service_has_2_folders(service, test_context, notify_db_session):
    folders = [
        create_template_folder(service, name="Folder A"),
        create_template_folder(service, name="Folder B"),
    ]
    test_context["folders"] = folders
    return test_context


@given(
    parsers.parse('a template folder "{name}" exists'),
    target_fixture="folder",
)
def a_template_folder_exists(service, name, notify_db_session):
    return create_template_folder(service, name=name)


@given("an empty template folder exists", target_fixture="folder")
def an_empty_folder_exists(service, notify_db_session):
    return create_template_folder(service, name="Empty Folder")


@given("a template and a folder exist", target_fixture="test_context")
def template_and_folder_exist(service, test_context, notify_db_session):
    template = create_template(service, template_type=SMS_TYPE, content="Movable template")
    folder = create_template_folder(service, name="Target Folder")
    test_context["template"] = template
    test_context["folder"] = folder
    return test_context


@given("a template is in a folder", target_fixture="test_context")
def template_in_folder(service, test_context, notify_db_session):
    folder = create_template_folder(service, name="Source Folder")
    template = create_template(service, template_type=SMS_TYPE, content="In folder", folder=folder)
    test_context["template"] = template
    test_context["folder"] = folder
    return test_context


# -- When steps --


@when(
    parsers.parse('I create a template folder named "{name}"'),
    target_fixture="api_response",
)
def create_folder(admin_client, service, name):
    data = {
        "name": name,
        "parent_id": None,
    }
    resp = admin_client.post(f"/service/{service.id}/template-folder", data=data)
    return {"status_code": resp.status_code, "json": resp.json}


@when("I list template folders for the service", target_fixture="api_response")
def list_folders(admin_client, service):
    resp = admin_client.get(f"/service/{service.id}/template-folder")
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I update the folder name to "{name}"'),
    target_fixture="api_response",
)
def update_folder_name(admin_client, service, folder, name):
    data = {"name": name}
    resp = admin_client.post(f"/service/{service.id}/template-folder/{folder.id}", data=data)
    return {"status_code": resp.status_code, "json": resp.json}


@when("I delete the template folder", target_fixture="api_response")
def delete_folder(admin_client, service, folder):
    resp = admin_client.delete(f"/service/{service.id}/template-folder/{folder.id}")
    return {"status_code": resp.status_code, "json": resp.json}


@when("I move the template into the folder", target_fixture="api_response")
def move_template_into_folder(admin_client, service, test_context):
    template = test_context["template"]
    folder = test_context["folder"]
    data = {
        "templates": [str(template.id)],
        "folders": [],
    }
    resp = admin_client.post(
        f"/service/{service.id}/template-folder/{folder.id}/contents",
        data=data,
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when("I move the template to the root", target_fixture="api_response")
def move_template_to_root(admin_client, service, test_context):
    template = test_context["template"]
    data = {
        "templates": [str(template.id)],
        "folders": [],
    }
    resp = admin_client.post(
        f"/service/{service.id}/template-folder/contents",
        data=data,
    )
    return {"status_code": resp.status_code, "json": resp.json}


@when(
    parsers.parse('I create a template folder "{child_name}" inside "{parent_name}"'),
    target_fixture="api_response",
)
def create_nested_folder(admin_client, service, folder, child_name, parent_name):
    data = {
        "name": child_name,
        "parent_id": str(folder.id),
    }
    resp = admin_client.post(f"/service/{service.id}/template-folder", data=data)
    return {"status_code": resp.status_code, "json": resp.json}


# -- Then steps --


@then(parsers.parse("the response should contain {count:d} folders"))
def response_has_n_folders(api_response, count):
    folders = api_response["json"]
    assert len(folders) == count
