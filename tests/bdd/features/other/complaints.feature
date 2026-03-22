Feature: Complaint management
  As a platform admin
  I want to view email complaints
  So that I can manage delivery reputation

  Scenario: List all complaints
    Given email complaints have been recorded
    When I list all complaints
    Then the response status code should be 200
    And the response should include complaint details

  Scenario: Count complaints by date range
    Given email complaints exist in a date range
    When I count complaints for the date range
    Then the response status code should be 200
    And the response should include a count
