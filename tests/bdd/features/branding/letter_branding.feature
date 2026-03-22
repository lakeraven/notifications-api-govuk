Feature: Letter branding management
  As a platform admin
  I want to manage letter branding options
  So that services can customise their letter headers

  Scenario: List all letter branding
    Given letter branding options exist
    When I list all letter branding
    Then the response status code should be 200

  Scenario: Create letter branding
    When I create letter branding named "Official Logo"
    Then the response status code should be 201

  Scenario: Get letter branding by ID
    Given letter branding "Test Letterhead" exists
    When I get the letter branding by ID
    Then the response status code should be 200

  Scenario: Update letter branding
    Given letter branding exists
    When I update the letter branding name to "New Letterhead"
    Then the response status code should be 200

  Scenario: Get organisations and services using letter branding
    Given letter branding is used by services
    When I get the orgs and services for the letter branding
    Then the response status code should be 200

  Scenario: Get a unique name for letter branding
    When I request a unique name based on "My Brand"
    Then the response status code should be 200
