Feature: User authentication flows
  As a user
  I want to authenticate securely
  So that my account is protected

  Background:
    Given an active user exists with a password

  Scenario: Verify correct password
    When I verify the user's password
    Then the response status code should be 204

  Scenario: Reject incorrect password
    When I verify an incorrect password
    Then the response status code should be 400

  Scenario: Send SMS 2FA code
    When I request an SMS 2FA code for the user
    Then the response status code should be 204

  Scenario: Send email 2FA code
    When I request an email 2FA code for the user
    Then the response status code should be 204

  Scenario: Verify correct 2FA code
    Given the user has a pending 2FA code
    When I verify the correct 2FA code
    Then the response status code should be 204

  Scenario: Reject incorrect 2FA code
    Given the user has a pending 2FA code
    When I verify an incorrect 2FA code
    Then the response status code should be 404

  Scenario: Reset failed login count
    Given the user has failed login attempts
    When I reset the failed login count
    Then the response status code should be 200

  Scenario: Complete WebAuthn login
    Given the user has a WebAuthn credential
    When I complete the WebAuthn login flow
    Then the response status code should be 204

  Scenario: Send password reset email
    When I request a password reset for the user
    Then the response status code should be 204

  Scenario: Update password
    When I update the user's password
    Then the response status code should be 200

  Scenario: Send email verification for new user
    Given a pending user exists
    When I send the email verification
    Then the response status code should be 204

  Scenario: Send change email verification
    When I send a change email verification to "newemail@example.gov.uk"
    Then the response status code should be 204
