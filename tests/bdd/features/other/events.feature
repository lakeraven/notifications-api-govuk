Feature: Audit event creation
  As the platform
  I want to record audit events
  So that actions are traceable

  Scenario: Create an audit event
    When I create an event of type "sucessful_login" for a user
    Then the response status code should be 201
