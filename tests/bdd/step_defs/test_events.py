"""
Step definitions for audit event creation.
"""

import json
import uuid

from pytest_bdd import given, parsers, scenarios, then, when

from tests.app.db import create_user

scenarios("../features/other/events.feature")


# -- When steps --


@when(
    parsers.parse('I create an event of type "{event_type}" for a user'),
    target_fixture="api_response",
)
def create_event(admin_client, notify_db_session, event_type):
    user = create_user(email=f"event-user-{uuid.uuid4()}@example.gov.uk")
    resp = admin_client.post(
        "/events",
        data={"event_type": event_type, "data": {"user_id": str(user.id)}},
    )
    return {"status_code": resp.status_code, "json": resp.json}
