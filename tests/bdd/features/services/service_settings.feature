Feature: Service settings management
  As a service admin
  I want to manage service configuration
  So that notifications are sent correctly

  Background:
    Given a service exists

  Scenario: Get email reply-to addresses
    Given the service has a reply-to email "replies@service.gov.uk"
    When I get email reply-to addresses for the service
    Then the response status code should be 200
    And the response should include "replies@service.gov.uk"

  Scenario: Add an email reply-to address
    When I add reply-to email "new-replies@service.gov.uk" to the service
    Then the response status code should be 201

  Scenario: Verify a reply-to email address
    When I verify reply-to email "verify-me@service.gov.uk"
    Then the response status code should be 201

  Scenario: Archive an email reply-to address
    Given the service has 2 reply-to emails
    When I archive the non-default reply-to email
    Then the response status code should be 200

  Scenario: Get SMS senders for a service
    When I get SMS senders for the service
    Then the response status code should be 200
    And the response should include the default sender

  Scenario: Add an SMS sender
    When I add SMS sender "07700900123" to the service
    Then the response status code should be 201

  Scenario: Update an SMS sender
    Given the service has an SMS sender
    When I update the SMS sender value
    Then the response status code should be 200

  Scenario: Archive an SMS sender
    Given the service has 2 SMS senders
    When I archive the non-default SMS sender
    Then the response status code should be 200

  Scenario: Get letter contacts for a service
    Given the service has a letter contact block
    When I get letter contacts for the service
    Then the response status code should be 200

  Scenario: Add a letter contact block
    When I add a letter contact block to the service
    Then the response status code should be 201

  Scenario: Get guest list
    When I get the guest list for the service
    Then the response status code should be 200

  Scenario: Update guest list
    When I update the guest list with emails and phone numbers
    Then the response status code should be 204

  Scenario: Get data retention rules
    When I get data retention rules for the service
    Then the response status code should be 200

  Scenario: Create a data retention rule
    When I create a data retention rule for SMS with 7 days
    Then the response status code should be 201

  Scenario: Modify a data retention rule
    Given a data retention rule exists for SMS
    When I modify the retention rule to 14 days
    Then the response status code should be 200

  Scenario: Get organisation for a service
    Given the service is linked to an organisation
    When I get the organisation for the service
    Then the response status code should be 200
    And the response should contain the organisation details
