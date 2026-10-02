package com.mobelite.publisher.ui.steps;

import com.mobelite.factory.PlaywrightFactory;
import com.mobelite.publisher.ui.pages.AdminPage;
import io.cucumber.java.en.And;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.testng.Assert;

public class AdminSteps {

    private final AdminPage adminPage = new AdminPage(PlaywrightFactory.getPage());

    private static final String VALID_ADMIN_USERNAME = System.getProperty("admin.username", "admin");
    private static final String VALID_ADMIN_PASSWORD = System.getProperty("admin.password");

    @Given("I am on the admin login page")
    public void iAmOnTheAdminLoginPage() {
        adminPage.navigateToLoginPage();
        adminPage.waitForLoginPage();
    }

    @When("I log in with valid admin credentials")
    public void iLogInWithValidAdminCredentials() {
        if (VALID_ADMIN_PASSWORD == null || VALID_ADMIN_PASSWORD.isBlank()) {
            throw new IllegalStateException("Admin E2E credential missing. Set -Dadmin.username and -Dadmin.password or provide the same values in the test environment.");
        }
        adminPage.login(VALID_ADMIN_USERNAME, VALID_ADMIN_PASSWORD);
    }

    @Then("I should be redirected to the admin dashboard")
    public void iShouldBeRedirectedToTheAdminDashboard() {
        adminPage.waitForDashboardPage();
        Assert.assertTrue(adminPage.isDashboardPageVisible(), "Admin dashboard should be visible after successful login");
        Assert.assertTrue(adminPage.currentUrl().contains("/admin"), "User should be redirected to the admin dashboard");
    }

    @When("I log in with invalid admin credentials")
    public void iLogInWithInvalidAdminCredentials() {
        adminPage.login("admin", "wrong-password");
    }

    @Then("I should see the invalid admin credentials error")
    public void iShouldSeeTheInvalidAdminCredentialsError() {
        adminPage.waitForError();
        Assert.assertTrue(adminPage.isErrorVisible(), "Login error should be visible");
        Assert.assertTrue(adminPage.getErrorText().toLowerCase().contains("invalid") || adminPage.getErrorText().toLowerCase().contains("username"), "Error should indicate invalid credentials");
        Assert.assertTrue(adminPage.currentUrl().contains("/admin/login"), "User should remain on the login page after invalid login");
    }

    @Given("I visit the admin dashboard without logging in")
    public void iVisitTheAdminDashboardWithoutLoggingIn() {
        adminPage.navigateToDashboardPage();
    }

    @Then("I should be redirected back to the admin login page")
    public void iShouldBeRedirectedBackToTheAdminLoginPage() {
        adminPage.waitForLoginPage();
        Assert.assertTrue(adminPage.isLoginPageVisible(), "Login page should be visible after redirect");
        Assert.assertTrue(adminPage.currentUrl().contains("/admin/login"), "User should be redirected to admin login page");
    }

    @When("I log out from the admin dashboard")
    public void iLogOutFromTheAdminDashboard() {
        adminPage.logout();
    }

    @And("I visit the admin dashboard again")
    public void iVisitTheAdminDashboardAgain() {
        adminPage.navigateToDashboardPage();
    }
}
