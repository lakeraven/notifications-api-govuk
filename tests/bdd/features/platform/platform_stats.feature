Feature: Platform-wide statistics
  As a platform admin
  I want to view platform-wide statistics
  So that I can monitor the health of the system

  Scenario: Get platform notification stats
    Given services have sent notifications
    When I get platform stats
    Then the response status code should be 200
    And the response should include counts by notification type and status

  Scenario: Get billing report data
    Given services have sent notifications this year
    When I get data for billing report
    Then the response status code should be 200

  Scenario: Get DVLA billing report data
    Given letter notifications have been sent
    When I get data for DVLA billing report
    Then the response status code should be 200

  Scenario: Get daily volumes report
    Given notifications have been sent today
    When I get the daily volumes report
    Then the response status code should be 200

  Scenario: Get daily SMS provider volumes
    Given SMS notifications have been sent via providers
    When I get the daily SMS provider volumes report
    Then the response status code should be 200

  Scenario: Get volumes by service
    Given multiple services have sent notifications
    When I get volumes by service
    Then the response status code should be 200
    And the response should be broken down by service
