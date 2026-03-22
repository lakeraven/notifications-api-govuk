Feature: Email branding management
  As a platform admin
  I want to manage email branding options
  So that services can customise their email appearance

  Scenario: List all email branding options
    Given email branding options exist
    When I list all email branding
    Then the response status code should be 200

  Scenario: Create email branding
    When I create email branding named "Service Brand" with colour "#005ea5"
    Then the response status code should be 201

  Scenario: Get email branding by ID
    Given email branding "Test Brand" exists
    When I get the email branding by ID
    Then the response status code should be 200
    And the branding name should be "Test Brand"

  Scenario: Update email branding
    Given email branding exists
    When I update the branding name to "Updated Brand"
    Then the response status code should be 200

  Scenario: Archive email branding
    Given email branding exists
    When I archive the email branding
    Then the response status code should be 200

  Scenario: Get organisations and services using email branding
    Given email branding is used by services
    When I get the orgs and services for the branding
    Then the response status code should be 200
