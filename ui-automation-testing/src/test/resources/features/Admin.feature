Feature: Admin authentication flow
  In order to access protected admin features
  As an administrator
  I want to sign in, fail clearly on bad credentials, and stay redirected when unauthenticated

  @smoke
  Scenario: Successful admin login redirects to the dashboard
    Given I am on the admin login page
    When I log in with valid admin credentials
    Then I should be redirected to the admin dashboard

  @smoke @regression
  Scenario: Invalid admin credentials show an error and keep the user on login
    Given I am on the admin login page
    When I log in with invalid admin credentials
    Then I should see the invalid admin credentials error

  @regression
  Scenario: Unauthenticated access to the admin dashboard redirects to login
    Given I visit the admin dashboard without logging in
    Then I should be redirected back to the admin login page

  @regression
  Scenario: Logging out returns the user to login and blocks the dashboard again
    Given I am on the admin login page
    When I log in with valid admin credentials
    Then I should be redirected to the admin dashboard
    When I log out from the admin dashboard
    Then I should be redirected back to the admin login page
    And I visit the admin dashboard again
    Then I should be redirected back to the admin login page
