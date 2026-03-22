Feature: Template statistics
  As a service admin
  I want to see template usage statistics
  So that I know which templates are used most

  Background:
    Given a service exists with templates and sent notifications

  Scenario: Get template statistics for today
    When I get template statistics for the last 0 days
    Then the response status code should be 200
    And the response should include template usage counts

  Scenario: Get template statistics for the last 7 days
    When I get template statistics for the last 7 days
    Then the response status code should be 200

  Scenario: Get last used date for a template
    Given a template has been used to send notifications
    When I get the last used date for the template
    Then the response status code should be 200
    And the response should include a datetime
