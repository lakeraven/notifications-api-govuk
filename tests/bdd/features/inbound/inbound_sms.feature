Feature: Inbound SMS management (admin API)
  As a service admin
  I want to view received SMS messages
  So that I can monitor user responses

  Background:
    Given a service exists with inbound SMS enabled

  Scenario: Query inbound SMS for a service
    Given the service has received inbound SMS messages
    When I query inbound SMS for the service
    Then the response status code should be 200

  Scenario: Get most recent inbound SMS
    Given the service has received inbound SMS messages
    When I get the most recent inbound SMS
    Then the response status code should be 200

  Scenario: Get inbound SMS summary
    Given the service has received inbound SMS in the last 7 days
    When I get the inbound SMS summary
    Then the response status code should be 200
    And the response should include a count

  Scenario: Get a specific inbound SMS by ID
    Given a specific inbound SMS exists
    When I get the inbound SMS by ID
    Then the response status code should be 200

  Scenario: Remove inbound SMS for a service
    Given the service has received inbound SMS messages
    When I remove inbound SMS for the service
    Then the response status code should be 200

  Scenario: Receive an inbound SMS via provider webhook
    When a provider sends an inbound SMS webhook
    Then the response status code should be 200
    And the inbound SMS should be stored
