Feature: Service callback management
  As a service admin
  I want to configure webhook callbacks
  So that I receive delivery status updates

  Background:
    Given a service exists

  Scenario: Create a delivery receipt callback
    When I create a delivery receipt callback with URL "https://example.com/callback"
    Then the response status code should be 201

  Scenario: Get a delivery receipt callback
    Given the service has a delivery receipt callback
    When I get the delivery receipt callback
    Then the response status code should be 200
    And the callback URL should be present

  Scenario: Update a delivery receipt callback
    Given the service has a delivery receipt callback
    When I update the callback URL to "https://example.com/new-callback"
    Then the response status code should be 200

  Scenario: Delete a delivery receipt callback
    Given the service has a delivery receipt callback
    When I delete the delivery receipt callback
    Then the response status code should be 204

  Scenario: Create an inbound SMS callback
    When I create an inbound SMS callback with URL "https://example.com/inbound"
    Then the response status code should be 201

  Scenario: Get an inbound SMS callback
    Given the service has an inbound SMS callback
    When I get the inbound SMS callback
    Then the response status code should be 200

  Scenario: Update an inbound SMS callback
    Given the service has an inbound SMS callback
    When I update the inbound SMS callback URL
    Then the response status code should be 200

  Scenario: Delete an inbound SMS callback
    Given the service has an inbound SMS callback
    When I delete the inbound SMS callback
    Then the response status code should be 204
