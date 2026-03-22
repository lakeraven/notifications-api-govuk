Feature: Job (bulk send) lifecycle
  As a service admin
  I want to manage bulk notification jobs
  So that I can send to many recipients at once

  Background:
    Given a service exists with templates

  Scenario: Create a job
    Given an SMS template exists
    When I create a job for the template with a CSV file
    Then the response status code should be 201
    And the job should have status "pending"

  Scenario: Get a job by ID
    Given a job exists
    When I get the job by ID
    Then the response status code should be 200
    And the response should include job statistics

  Scenario: List jobs for a service
    Given 3 jobs exist for the service
    When I list jobs for the service
    Then the response status code should be 200
    And the response should contain jobs

  Scenario: Cancel a scheduled job
    Given a scheduled job exists
    When I cancel the job
    Then the response status code should be 200

  Scenario: Cancel a letter job
    Given a letter job exists
    When I cancel the letter job
    Then the response status code should be 200

  Scenario: Get notifications for a job
    Given a job has been processed with notifications
    When I get notifications for the job
    Then the response status code should be 200
    And the response should contain the job's notifications

  Scenario: Get notification count for a job
    Given a job has been processed with 5 notifications
    When I get the notification count for the job
    Then the response status code should be 200
    And the count should be 5

  Scenario: Get scheduled job stats
    Given scheduled jobs exist
    When I get scheduled job stats for the service
    Then the response status code should be 200
