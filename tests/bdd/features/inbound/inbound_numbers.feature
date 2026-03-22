Feature: Inbound number management
  As a platform admin
  I want to manage inbound SMS numbers
  So that services can receive text messages

  Scenario: List all inbound numbers
    When I list all inbound numbers
    Then the response status code should be 200

  Scenario: List available inbound numbers
    Given unassigned inbound numbers exist
    When I list available inbound numbers
    Then the response status code should be 200

  Scenario: Get inbound number for a service
    Given a service has an inbound number assigned
    When I get the inbound number for the service
    Then the response status code should be 200
    And the response should include the phone number

  Scenario: Assign an inbound number to a service
    Given an available inbound number exists
    When I assign the number to a service
    Then the response status code should be 200

  Scenario: Deactivate inbound number for a service
    Given a service has an inbound number assigned
    When I deactivate the inbound number
    Then the response status code should be 200
