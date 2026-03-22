Feature: Manage templates via v2 API
  As an API consumer
  I want to retrieve and preview templates
  So that I can manage my notification content

  Background:
    Given a service exists with a valid API key
    And the service has an SMS template "Appointment reminder"
    And the service has an email template "Welcome email"

  Scenario: Get a template by ID
    When I request the SMS template by ID
    Then the response status code should be 200
    And the response should contain the template ID
    And the response name should be "Appointment reminder"
    And the response type should be "sms"
    And the response should include body content
    And the response should include version number

  Scenario: Get a template at a specific version
    Given the SMS template has been updated to version 2
    When I request the SMS template at version 1
    Then the response status code should be 200
    And the response version should be 1

  Scenario: Get all templates
    When I list all templates
    Then the response status code should be 200
    And the response should contain at least 2 templates

  Scenario: Filter templates by type
    When I list templates with type "sms"
    Then the response status code should be 200
    And all returned templates should be of type "sms"

  Scenario: Preview a template with personalisation
    Given the SMS template has content "Hello ((name))"
    When I preview the template with personalisation
      | name  |
      | World |
    Then the response status code should be 200
    And the preview body should contain "Hello World"

  Scenario: Reject request for template from another service
    Given another service has a template
    When I request that template by ID
    Then the response status code should be 404

  Scenario: Reject request for nonexistent template
    When I request a template with a random UUID
    Then the response status code should be 404

  Scenario: Reject request for invalid template ID
    When I request a template with ID "not-a-uuid"
    Then the response status code should be 404
