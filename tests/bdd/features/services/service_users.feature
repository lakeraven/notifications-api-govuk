Feature: Service user management
  As a service admin
  I want to manage users on my service
  So that the right people have access

  Background:
    Given a service exists with an admin user

  Scenario: List users for a service
    When I list users for the service
    Then the response status code should be 200
    And the response should contain at least 1 user

  Scenario: Add a user to a service
    Given a new user exists
    When I add the user to the service
    Then the response status code should be 200

  Scenario: Remove a user from a service
    Given the service has 2 users
    When I remove the second user from the service
    Then the response status code should be 200
    And the service should have 1 user
