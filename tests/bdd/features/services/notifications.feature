Feature: Service notification management (admin API)
  As a service admin
  I want to view and manage notifications sent by my service
  So that I can monitor delivery

  Background:
    Given a service exists with sent notifications

  Scenario: Get all notifications for a service
    When I get all notifications for the service
    Then the response status code should be 200
    And the response should contain a list of notifications

  Scenario: Get notifications for a service as CSV
    When I get notifications for the service in CSV format
    Then the response status code should be 200

  Scenario: Count notifications for a service
    When I count notifications for the service
    Then the response status code should be 200
    And the response should include a count

  Scenario: Get a specific notification for a service
    Given a notification exists for the service
    When I get the notification by ID via admin API
    Then the response status code should be 200
    And the response should contain the notification details

  Scenario: Cancel a scheduled notification
    Given a notification is scheduled for the service
    When I cancel the notification
    Then the response status code should be 200

  Scenario: Send a one-off notification via admin
    Given a template exists for the service
    When I send a one-off notification via admin API
    Then the response status code should be 201
