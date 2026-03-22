Feature: Organisation service management
  As a platform admin
  I want to manage services within organisations
  So that services are properly associated

  Background:
    Given an organisation exists

  Scenario: Link a service to an organisation
    Given a service exists
    When I link the service to the organisation
    Then the response status code should be 204

  Scenario: List services in an organisation
    Given the organisation has 2 services
    When I list services in the organisation
    Then the response status code should be 200
    And the response should contain 2 services

  Scenario: Get organisation services with usage
    Given the organisation has services with usage data
    When I get services with usage for the current year
    Then the response status code should be 200
    And the response should include usage figures
