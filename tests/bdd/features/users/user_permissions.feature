Feature: User permission management
  As a service admin
  I want to control what users can do
  So that access is appropriately restricted

  Background:
    Given a service exists with an admin user
    And a second user belongs to the service

  Scenario: Set user permissions on a service
    When I set the user's permissions to "send_messages" and "view_activity"
    Then the response status code should be 204

  Scenario: Remove all user permissions on a service
    When I set the user's permissions to empty
    Then the response status code should be 204

  Scenario: Set user permissions on an organisation
    Given the user belongs to an organisation
    When I set the user's organisation permissions
    Then the response status code should be 204

  Scenario: Get WebAuthn credentials for a user
    Given the user has WebAuthn credentials
    When I get the user's WebAuthn credentials
    Then the response status code should be 200
    And the response should contain the credentials

  Scenario: Create a WebAuthn credential
    When I create a WebAuthn credential for the user
    Then the response status code should be 201

  Scenario: Delete a WebAuthn credential
    Given the user has a WebAuthn credential
    When I delete the WebAuthn credential
    Then the response status code should be 204
