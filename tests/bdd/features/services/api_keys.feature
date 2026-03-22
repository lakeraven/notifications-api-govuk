Feature: Service API key management
  As a service admin
  I want to manage API keys
  So that I can control access to notification sending

  Background:
    Given a service exists

  Scenario: Create a normal API key
    When I create an API key named "production-key" of type "normal"
    Then the response status code should be 201
    And the response should contain the API key secret

  Scenario: Create a test API key
    When I create an API key named "test-key" of type "test"
    Then the response status code should be 201

  Scenario: Create a team API key
    When I create an API key named "team-key" of type "team"
    Then the response status code should be 201

  Scenario: List API keys for a service
    Given the service has 2 API keys
    When I list API keys for the service
    Then the response status code should be 200
    And the response should contain 2 API keys

  Scenario: Get a specific API key
    Given the service has an API key
    When I get the API key by ID
    Then the response status code should be 200
    And the response should contain the key name

  Scenario: Revoke an API key
    Given the service has an API key
    When I revoke the API key
    Then the response status code should be 202
    And the API key should be expired

  Scenario: Revoked API key cannot send notifications
    Given the service has a revoked API key
    When I try to send a notification using the revoked key
    Then the response status code should be 403
