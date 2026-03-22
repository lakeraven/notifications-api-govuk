Feature: Get notification status via v2 API
  As an API consumer
  I want to retrieve the status of sent notifications
  So that I can track delivery

  Background:
    Given a service exists with a valid API key
    And an SMS notification has been sent

  Scenario: Get an SMS notification by ID
    When I request the notification by ID
    Then the response status code should be 200
    And the response should contain the notification ID
    And the response type should be "sms"
    And the response should include created_at timestamp
    And the response should include template details

  Scenario: Get an email notification by ID
    Given an email notification has been sent
    When I request the notification by ID
    Then the response status code should be 200
    And the response type should be "email"
    And the response should include subject

  Scenario: Get a letter notification by ID
    Given a letter notification has been sent
    When I request the notification by ID
    Then the response status code should be 200
    And the response type should be "letter"
    And the response should include postage

  Scenario: Get notification with cost data
    Given a sent SMS notification with cost data ready
    When I request the notification by ID
    Then the response status code should be 200
    And the response should include cost_in_pounds
    And the response is_cost_data_ready should be true

  Scenario: Get a delivered notification
    Given a notification with status "delivered"
    When I request the notification by ID
    Then the response status should be "delivered"
    And the response should include sent_at timestamp
    And the response should include completed_at timestamp

  Scenario: Get a failed notification
    Given a notification with status "permanent-failure"
    When I request the notification by ID
    Then the response status should be "permanent-failure"

  Scenario: Reject request for notification from another service
    Given another service has a notification
    When I request that notification by ID
    Then the response status code should be 404

  Scenario: Reject request with invalid notification ID
    When I request a notification with ID "not-a-uuid"
    Then the response status code should be 404

  Scenario: Reject request with nonexistent notification ID
    When I request a notification with a random UUID
    Then the response status code should be 404

  Scenario: Get PDF for a letter notification
    Given a letter notification has been sent
    When I request the PDF for the letter notification
    Then the response status code should be 200
    And the response content type should be "application/pdf"

  Scenario: List notifications with default pagination
    Given 10 notifications have been sent
    When I list all notifications
    Then the response status code should be 200
    And the response should contain a list of notifications
    And the response should include pagination links

  Scenario: List notifications filtered by template type
    Given both SMS and email notifications have been sent
    When I list notifications with template_type "sms"
    Then the response status code should be 200
    And all returned notifications should be of type "sms"

  Scenario: List notifications filtered by status
    Given notifications with various statuses exist
    When I list notifications with status "delivered"
    Then the response status code should be 200
    And all returned notifications should have status "delivered"

  Scenario: List notifications filtered by reference
    Given notifications with reference "batch-42" exist
    When I list notifications with reference "batch-42"
    Then the response status code should be 200
    And all returned notifications should have reference "batch-42"

  Scenario: Paginate notifications using older_than
    Given 10 notifications have been sent
    When I list notifications older than the 5th notification
    Then the response status code should be 200
    And the returned notifications should all be older than the 5th notification
