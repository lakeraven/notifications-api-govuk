Feature: Retrieve received text messages via v2 API
  As an API consumer
  I want to retrieve inbound SMS messages
  So that I can process responses from users

  Background:
    Given a service exists with inbound SMS enabled
    And the service has a valid API key

  Scenario: List received text messages
    Given the service has received 3 inbound SMS messages
    When I list received text messages
    Then the response status code should be 200
    And the response should contain 3 received texts
    And each received text should include content, created_at, and user_number

  Scenario: Paginate received texts using older_than
    Given the service has received 5 inbound SMS messages
    When I list received texts older than the 3rd message
    Then the response status code should be 200
    And all returned messages should be older than the 3rd message

  Scenario: No received texts returns empty list
    When I list received text messages
    Then the response status code should be 200
    And the response should contain 0 received texts
