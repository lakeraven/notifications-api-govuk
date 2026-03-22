Feature: Platform admin operations
  As a platform admin
  I want to perform administrative lookups
  So that I can support services and users

  Scenario: Find a resource by UUID
    Given a service exists
    When I search by the service's UUID
    Then the response status code should be 200
    And the response should identify the resource type

  Scenario: List users matching criteria
    Given multiple users exist
    When I fetch a list of users
    Then the response status code should be 200
    And the response should contain user details
