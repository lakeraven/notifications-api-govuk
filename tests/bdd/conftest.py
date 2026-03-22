"""
BDD test configuration.

Bridges pytest-bdd to the existing notifications-api test infrastructure.
All fixtures from tests/conftest.py and tests/app/conftest.py are available
since pytest discovers them via the test hierarchy.
"""

import json
import uuid

import pytest
from flask import url_for

from tests import (
    create_admin_authorization_header,
    create_service_authorization_header,
)
from tests.app.db import (
    create_api_key,
    create_email_branding,
    create_inbound_number,
    create_job,
    create_letter_branding,
    create_notification,
    create_rate,
    create_service,
    create_template,
    create_user,
)


@pytest.fixture
def api_response():
    """Mutable container for capturing API responses across steps."""
    return {}


@pytest.fixture
def test_context():
    """Mutable container for sharing state between Given/When/Then steps."""
    return {}


@pytest.fixture
def admin_client(client):
    """Wrapper around Flask test client with admin auth."""

    class AdminClient:
        @staticmethod
        def get(path, **kwargs):
            return client.get(
                path,
                headers=[create_admin_authorization_header()],
                **kwargs,
            )

        @staticmethod
        def post(path, data=None, **kwargs):
            headers = [
                ("Content-Type", "application/json"),
                create_admin_authorization_header(),
            ]
            return client.post(
                path,
                data=json.dumps(data) if data else None,
                headers=headers,
                **kwargs,
            )

        @staticmethod
        def put(path, data=None, **kwargs):
            headers = [
                ("Content-Type", "application/json"),
                create_admin_authorization_header(),
            ]
            return client.put(
                path,
                data=json.dumps(data) if data else None,
                headers=headers,
                **kwargs,
            )

        @staticmethod
        def delete(path, **kwargs):
            return client.delete(
                path,
                headers=[create_admin_authorization_header()],
                **kwargs,
            )

    return AdminClient()


@pytest.fixture
def service_api_client(client):
    """Wrapper around Flask test client with service API key auth (for v2 endpoints)."""

    class ServiceApiClient:
        def __init__(self):
            self._service_id = None

        def set_service(self, service_id):
            self._service_id = service_id

        def get(self, path, key_type="normal", **kwargs):
            return client.get(
                path,
                headers=[create_service_authorization_header(self._service_id, key_type)],
                **kwargs,
            )

        def post(self, path, data=None, key_type="normal", **kwargs):
            headers = [
                ("Content-Type", "application/json"),
                create_service_authorization_header(self._service_id, key_type),
            ]
            return client.post(
                path,
                data=json.dumps(data) if data else None,
                headers=headers,
                **kwargs,
            )

    return ServiceApiClient()
