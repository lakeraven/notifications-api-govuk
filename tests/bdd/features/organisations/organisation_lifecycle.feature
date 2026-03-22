Feature: Organisation lifecycle management
  As a platform admin
  I want to manage organisations
  So that services can be grouped

  Scenario: Create an organisation
    When I create an organisation named "Test Org" of type "central"
    Then the response status code should be 201

  Scenario: Get an organisation by ID
    Given an organisation "My Org" exists
    When I get the organisation by ID
    Then the response status code should be 200
    And the organisation name should be "My Org"

  Scenario: List all organisations
    Given 2 organisations exist
    When I list all organisations
    Then the response status code should be 200
    And the response should contain at least 2 organisations

  Scenario: Update an organisation
    Given an organisation exists
    When I update the organisation name to "Updated Org"
    Then the response status code should be 200
    And the organisation name should be "Updated Org"

  Scenario: Archive an organisation
    Given an organisation exists
    When I archive the organisation
    Then the response status code should be 204

  Scenario: Find organisation by email domain
    Given an organisation owns domain "example.gov.uk"
    When I look up the organisation by domain "example.gov.uk"
    Then the response status code should be 200
    And the response should contain the organisation

  Scenario: Search organisations
    Given an organisation "Searchable Org" exists
    When I search organisations for "Searchable"
    Then the response status code should be 200
    And the results should include "Searchable Org"
