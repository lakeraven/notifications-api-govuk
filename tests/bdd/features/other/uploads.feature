Feature: Upload management
  As a service admin
  I want to view upload history
  So that I can track bulk send operations

  Background:
    Given a service exists

  Scenario: List uploads for a service
    Given the service has completed uploads
    When I list uploads for the service
    Then the response status code should be 200
    And the response should include upload details
