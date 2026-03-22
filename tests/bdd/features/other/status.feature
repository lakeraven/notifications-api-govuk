Feature: Health check and status endpoints
  As a platform operator
  I want to check the API health
  So that I can monitor availability

  Scenario: Basic health check
    When I request the root endpoint "/"
    Then the response status code should be 200

  Scenario: Detailed status check
    When I request "/_status"
    Then the response status code should be 200
    And the response should include git commit hash
    And the response should include database version

  Scenario: Live service and organisation counts
    When I request "/_status/live-service-and-organisation-counts"
    Then the response status code should be 200
    And the response should include service and organisation counts
