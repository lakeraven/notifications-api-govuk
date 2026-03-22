Feature: User management
  As a platform admin
  I want to manage user accounts
  So that the right people can access the platform

  Scenario: Create a new user
    When I create a user with email "newuser@example.gov.uk" and mobile "07700900001"
    Then the response status code should be 201
    And the user should have state "pending"

  Scenario: Get a user by ID
    Given a user exists
    When I get the user by ID
    Then the response status code should be 200
    And the response should contain the user's email

  Scenario: Update a user's name
    Given a user exists
    When I update the user's name to "New Name"
    Then the response status code should be 200
    And the user's name should be "New Name"

  Scenario: Fetch user by email
    Given a user exists with email "findme@example.gov.uk"
    When I fetch the user by email "findme@example.gov.uk"
    Then the response status code should be 200
    And the response should contain the user's ID

  Scenario: Find users by partial email
    Given a user exists with email "searchable@example.gov.uk"
    When I find users by email "searchable"
    Then the response status code should be 200
    And the results should include the user

  Scenario: Archive a user
    Given a user exists
    When I archive the user
    Then the response status code should be 204

  Scenario: Activate a user
    Given a pending user exists
    When I activate the user
    Then the response status code should be 200
    And the user state should be "active"

  Scenario: Get user's organisations and services
    Given a user belongs to a service and an organisation
    When I get the user's organisations and services
    Then the response status code should be 200
    And the response should include both the service and the organisation
