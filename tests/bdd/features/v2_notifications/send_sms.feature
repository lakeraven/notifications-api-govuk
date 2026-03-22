Feature: Send SMS notification via v2 API
  As an API consumer
  I want to send SMS notifications
  So that I can communicate with users via text message

  Background:
    Given a service with SMS permissions exists
    And the service has an SMS template with content "Hello ((name)), your code is ((code))"
    And the service has a valid API key

  Scenario: Send a basic SMS notification
    When I send an SMS notification to "+447700900855" using the template
    Then the response status code should be 201
    And the response should contain a notification ID
    And the response should contain a URI for the notification
    And the notification status should be "created"

  Scenario: Send an SMS with personalisation
    When I send an SMS notification to "+447700900855" with personalisation
      | name  | code  |
      | Jo    | 12345 |
    Then the response status code should be 201
    And the response body should contain "Hello Jo, your code is 12345"

  Scenario: Send an SMS with a client reference
    When I send an SMS notification to "+447700900855" with reference "my-ref-123"
    Then the response status code should be 201
    And the response reference should be "my-ref-123"

  Scenario: Send an SMS with no reference returns null reference
    When I send an SMS notification to "+447700900855" without a reference
    Then the response status code should be 201
    And the response reference should be null

  Scenario: Send an SMS using an inbound number as sender
    Given the service has an inbound number "07700900001"
    When I send an SMS notification to "+447700900855" using the template
    Then the response status code should be 201
    And the response from_number should be "07700900001"

  Scenario: Send an SMS using a specific SMS sender
    Given the service has an SMS sender "custom-sender" with value "07700900002"
    When I send an SMS notification to "+447700900855" with sms_sender_id
    Then the response status code should be 201

  Scenario: Send an SMS with a test API key
    Given the service has a test API key
    When I send an SMS notification to "+447700900855" using the test key
    Then the response status code should be 201
    And no SMS delivery task should be queued

  Scenario: Send an SMS with a team API key to a non-team member
    Given the service has a team API key
    And the service is in trial mode
    When I send an SMS notification to "+447700900999" using the team key
    Then the response status code should be 400
    And the response error should mention "trial mode"

  Scenario: Reject SMS with missing phone number
    When I send an SMS notification without a phone number
    Then the response status code should be 400
    And the response error should mention "phone_number"

  Scenario: Reject SMS with missing template ID
    When I send an SMS notification to "+447700900855" without a template ID
    Then the response status code should be 400
    And the response error should mention "template_id"

  Scenario: Reject SMS with invalid template ID
    When I send an SMS notification to "+447700900855" with template ID "not-a-uuid"
    Then the response status code should be 400

  Scenario: Reject SMS when template belongs to another service
    Given another service exists with an SMS template
    When I send an SMS notification using the other service's template
    Then the response status code should be 400
    And the response error should mention "template"

  Scenario: Reject SMS when personalisation is missing required fields
    When I send an SMS notification to "+447700900855" with empty personalisation
    Then the response status code should be 400
    And the response error should mention "Missing personalisation"

  Scenario: Reject SMS when service has no SMS permission
    Given a service without SMS permissions exists
    When I send an SMS notification to "+447700900855" using that service
    Then the response status code should be 400

  Scenario: Reject SMS to an international number when not enabled
    When I send an SMS notification to "+33700900855" using the template
    Then the response status code should be 400
    And the response error should mention "international"

  Scenario: Send an SMS to an international number when enabled
    Given the service has international SMS permission
    When I send an SMS notification to "+33700900855" using the template
    Then the response status code should be 201

  Scenario: Schedule an SMS for future delivery
    When I send an SMS notification to "+447700900855" scheduled for tomorrow
    Then the response status code should be 201
    And the response scheduled_for should not be null

  Scenario: Reject SMS scheduled too far in advance
    When I send an SMS notification to "+447700900855" scheduled for next year
    Then the response status code should be 400

  Scenario: Rate limit SMS sending
    Given the service has reached its daily SMS limit
    When I send an SMS notification to "+447700900855" using the template
    Then the response status code should be 429
