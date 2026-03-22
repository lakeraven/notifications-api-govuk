Feature: Organisation branding management
  As a platform admin
  I want to manage branding options for organisations
  So that notifications reflect the organisation's identity

  Background:
    Given an organisation exists

  Scenario: Get email branding pool for an organisation
    Given the organisation has email branding options
    When I get the email branding pool
    Then the response status code should be 200

  Scenario: Add email branding to an organisation's pool
    Given email branding "Gov Brand" exists
    When I add the email branding to the organisation's pool
    Then the response status code should be 200

  Scenario: Remove email branding from an organisation's pool
    Given the organisation has email branding in its pool
    When I remove the email branding from the pool
    Then the response status code should be 204

  Scenario: Get letter branding pool for an organisation
    Given the organisation has letter branding options
    When I get the letter branding pool
    Then the response status code should be 200

  Scenario: Add letter branding to an organisation's pool
    Given letter branding "Official Letterhead" exists
    When I add the letter branding to the organisation's pool
    Then the response status code should be 200

  Scenario: Remove letter branding from an organisation's pool
    Given the organisation has letter branding in its pool
    When I remove the letter branding from the pool
    Then the response status code should be 204
