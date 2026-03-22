Feature: Billing and usage reporting
  As a platform admin
  I want to view billing and usage data
  So that I can track costs and quotas

  Background:
    Given a service exists with sent notifications

  Scenario: Get monthly usage for a service
    When I get the monthly usage for the current year
    Then the response status code should be 200
    And the response should include monthly breakdown

  Scenario: Get yearly usage summary
    When I get the yearly usage summary
    Then the response status code should be 200

  Scenario: Get free SMS fragment limit
    When I get the free SMS fragment limit
    Then the response status code should be 200
    And the response should include the free allowance

  Scenario: Set free SMS fragment limit
    When I set the free SMS fragment limit to 250000
    Then the response status code should be 201

  Scenario: Update free SMS fragment limit
    Given a free SMS fragment limit has been set
    When I update the free SMS fragment limit to 500000
    Then the response status code should be 201
