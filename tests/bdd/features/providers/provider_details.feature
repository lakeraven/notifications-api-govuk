Feature: Notification provider management
  As a platform admin
  I want to manage notification providers
  So that I can control SMS and email delivery

  Scenario: List all providers
    When I list all providers
    Then the response status code should be 200
    And the response should include SMS and email providers
    And each provider should have a priority and active status

  Scenario: Get a provider by ID
    Given a provider exists
    When I get the provider by ID
    Then the response status code should be 200
    And the response should include the provider identifier

  Scenario: Get provider version history
    Given a provider has been updated
    When I get the provider version history
    Then the response status code should be 200
    And the response should include version entries

  Scenario: Update provider priority
    Given an SMS provider exists
    When I update the provider priority to 50
    Then the response status code should be 200
    And the provider priority should be 50

  Scenario: Deactivate a provider
    Given an SMS provider exists
    When I set the provider to inactive
    Then the response status code should be 200
    And the provider should be inactive
