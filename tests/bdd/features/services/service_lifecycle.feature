Feature: Service lifecycle management
  As a platform admin
  I want to manage services
  So that organisations can send notifications

  Background:
    Given a platform admin user exists

  Scenario: Create a new service
    When I create a service named "Test Service" for user
    Then the response status code should be 201
    And the service should have default permissions
    And the service should be in restricted mode

  Scenario: Get a service by ID
    Given a service "My Service" exists
    When I get the service by ID
    Then the response status code should be 200
    And the service name should be "My Service"

  Scenario: List all services
    Given 3 services exist
    When I list all services
    Then the response status code should be 200
    And the response should contain at least 3 services

  Scenario: Update a service name
    Given a service "Old Name" exists
    When I update the service name to "New Name"
    Then the response status code should be 200
    And the service name should be "New Name"

  Scenario: Update service to go live
    Given a service in trial mode exists
    When I update the service to set restricted to false
    Then the response status code should be 200
    And the service should not be restricted

  Scenario: Archive a service
    Given a service exists
    When I archive the service
    Then the response status code should be 204
    And the service should be archived

  Scenario: Get service history
    Given a service exists with changes in its history
    When I get the service history
    Then the response status code should be 200
    And the response should contain service history events

  Scenario: Find services by name
    Given a service "Unique Test Name" exists
    When I search for services by name "Unique Test"
    Then the response status code should be 200
    And the results should include "Unique Test Name"

  Scenario: Get live services data
    Given live services exist
    When I request live services data
    Then the response status code should be 200

  Scenario: Get service notification statistics
    Given a service exists with sent notifications
    When I get the service statistics
    Then the response status code should be 200
    And the response should include counts by notification type

  Scenario: Get monthly notification stats
    Given a service exists with sent notifications
    When I get the monthly notification stats
    Then the response status code should be 200
    And the response should be grouped by month

  Scenario: Get monthly template usage
    Given a service exists with notifications sent from multiple templates
    When I get the monthly template usage
    Then the response status code should be 200
    And the response should include template names and counts
