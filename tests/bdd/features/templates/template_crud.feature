Feature: Template CRUD operations (admin API)
  As a service admin
  I want to create and manage notification templates
  So that I can control message content

  Background:
    Given a service exists

  Scenario: Create an SMS template
    When I create an SMS template named "Reminder" with content "Your appointment is on ((date))"
    Then the response status code should be 201
    And the template type should be "sms"
    And the template version should be 1

  Scenario: Create an email template
    When I create an email template named "Welcome" with subject "Welcome!" and content "Hello ((name))"
    Then the response status code should be 201
    And the template type should be "email"

  Scenario: Create a letter template
    Given the service has letter permissions
    When I create a letter template named "Notice" with content "Dear ((name))"
    Then the response status code should be 201
    And the template type should be "letter"

  Scenario: Get a template by ID
    Given an SMS template exists for the service
    When I get the template by ID
    Then the response status code should be 200
    And the response should contain the template details

  Scenario: List all templates for a service
    Given the service has 3 templates
    When I list all templates for the service
    Then the response status code should be 200
    And the response should contain 3 templates

  Scenario: Update a template
    Given an SMS template exists with content "Old content"
    When I update the template content to "New content ((name))"
    Then the response status code should be 200
    And the template version should be incremented

  Scenario: Get template versions
    Given a template has been updated 3 times
    When I get all versions of the template
    Then the response status code should be 200
    And the response should contain 4 versions

  Scenario: Get a specific template version
    Given a template has been updated
    When I get version 1 of the template
    Then the response status code should be 200
    And the template content should be the original

  Scenario: Preview a template
    Given an SMS template exists with content "Hello ((name))"
    When I preview the template with personalisation name "World"
    Then the response status code should be 200
    And the preview should contain "Hello World"

  Scenario: Reject template with invalid placeholders
    When I create an SMS template with content "Hello ((name)) and ((missing))"
    Then the response status code should be 201

  Scenario: Reject template that exceeds SMS character limit
    When I create an SMS template with content longer than the character limit
    Then the response status code should be 400

  Scenario: Archive a template
    Given an SMS template exists for the service
    When I archive the template
    Then the response status code should be 200
    And the template should be archived
