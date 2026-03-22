Feature: Send letter notification via v2 API
  As an API consumer
  I want to send letter notifications
  So that I can communicate with users via post

  Background:
    Given a service with letter permissions exists
    And the service has a letter template with content "Dear ((name)), your reference is ((ref))"
    And the service has a valid API key

  Scenario: Send a basic letter notification
    When I send a letter notification with personalisation
      | name      | address_line_1 | address_line_2 | postcode  | ref   |
      | Jo Smith  | 10 Street      | London         | SW1A 1AA  | ABC   |
    Then the response status code should be 201
    And the response should contain a notification ID
    And the response body should contain "Dear Jo Smith"

  Scenario: Send a letter with a client reference
    When I send a letter notification with reference "letter-ref-789" and personalisation
      | name      | address_line_1 | address_line_2 | postcode  | ref   |
      | Jo Smith  | 10 Street      | London         | SW1A 1AA  | ABC   |
    Then the response status code should be 201
    And the response reference should be "letter-ref-789"

  Scenario: Send a letter with second class postage
    Given the letter template has second class postage
    When I send a letter notification with personalisation
      | name      | address_line_1 | address_line_2 | postcode  | ref   |
      | Jo Smith  | 10 Street      | London         | SW1A 1AA  | ABC   |
    Then the response status code should be 201
    And the notification postage should be "second"

  Scenario: Send a precompiled letter
    When I send a precompiled letter with reference "precomp-001" and a valid PDF
    Then the response status code should be 201
    And the response should contain the precompiled letter ID
    And the response reference should be "precomp-001"

  Scenario: Reject letter with missing address fields
    When I send a letter notification with incomplete address
      | name      | address_line_1 |
      | Jo Smith  | 10 Street      |
    Then the response status code should be 400

  Scenario: Reject letter when service has no letter permission
    Given a service without letter permissions exists
    When I send a letter notification using that service
    Then the response status code should be 400

  Scenario: Reject precompiled letter with invalid PDF
    When I send a precompiled letter with reference "bad-pdf" and invalid content
    Then the response status code should be 400

  Scenario: Send a letter to an international address
    Given the service has international letter permission
    When I send a letter notification with international address
      | name      | address_line_1 | address_line_2 | country  | ref   |
      | Jo Smith  | 10 Rue Victor  | Paris          | France   | ABC   |
    Then the response status code should be 201

  Scenario: Send a letter with QR code
    Given the letter template contains a QR code placeholder
    When I send a letter notification with personalisation
      | name      | address_line_1 | address_line_2 | postcode  | ref   | qr_code_data          |
      | Jo Smith  | 10 Street      | London         | SW1A 1AA  | ABC   | https://example.com/v |
    Then the response status code should be 201
