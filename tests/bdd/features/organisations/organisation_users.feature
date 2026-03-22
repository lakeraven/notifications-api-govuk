Feature: Organisation user management
  As a platform admin
  I want to manage users within organisations
  So that the right people have access

  Background:
    Given an organisation exists

  Scenario: Add a user to an organisation
    Given a user exists
    When I add the user to the organisation
    Then the response status code should be 204

  Scenario: Remove a user from an organisation
    Given a user belongs to the organisation
    When I remove the user from the organisation
    Then the response status code should be 204

  Scenario: List users in an organisation
    Given the organisation has 2 users
    When I list users in the organisation
    Then the response status code should be 200
    And the response should contain 2 users

  Scenario: Invite a user to an organisation
    When I invite "newuser@example.gov.uk" to the organisation
    Then the response status code should be 201

  Scenario: List organisation invitations
    Given the organisation has pending invitations
    When I list invitations for the organisation
    Then the response status code should be 200

  Scenario: Accept an organisation invitation
    Given an invitation exists for the organisation
    When the invitation status is updated to "accepted"
    Then the response status code should be 200

  Scenario: Validate an organisation invitation token
    Given an invitation with a token exists
    When I validate the invitation token
    Then the response status code should be 200
