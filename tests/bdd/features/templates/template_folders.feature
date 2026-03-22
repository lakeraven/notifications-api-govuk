Feature: Template folder management
  As a service admin
  I want to organise templates into folders
  So that I can manage large template libraries

  Background:
    Given a service exists

  Scenario: Create a template folder
    When I create a template folder named "Appointments"
    Then the response status code should be 201

  Scenario: List template folders
    Given the service has 2 template folders
    When I list template folders for the service
    Then the response status code should be 200
    And the response should contain 2 folders

  Scenario: Update a template folder name
    Given a template folder "Old Name" exists
    When I update the folder name to "New Name"
    Then the response status code should be 200

  Scenario: Delete an empty template folder
    Given an empty template folder exists
    When I delete the template folder
    Then the response status code should be 204

  Scenario: Move a template into a folder
    Given a template and a folder exist
    When I move the template into the folder
    Then the response status code should be 204

  Scenario: Move a template to root
    Given a template is in a folder
    When I move the template to the root
    Then the response status code should be 204

  Scenario: Create a nested folder
    Given a template folder "Parent" exists
    When I create a template folder "Child" inside "Parent"
    Then the response status code should be 201
