package com.mobelite.publisher.ui.pages;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.WaitForSelectorState;
import com.mobelite.config.ConfigManager;
import com.mobelite.publisher.ui.constants.AdminTestIds;

import static com.mobelite.publisher.ui.constants.PagesNavigate.ADMIN_DASHBOARD_NAVIGATE;
import static com.mobelite.publisher.ui.constants.PagesNavigate.ADMIN_LOGIN_NAVIGATE;

public class AdminPage {

    private final Page page;

    private static final String USERNAME_INPUT = "[data-testid='" + AdminTestIds.ADMIN.ADMIN_USERNAME_INPUT + "']";
    private static final String PASSWORD_INPUT = "[data-testid='" + AdminTestIds.ADMIN.ADMIN_PASSWORD_INPUT + "']";
    private static final String LOGIN_BUTTON = "[data-testid='" + AdminTestIds.ADMIN.ADMIN_LOGIN_BUTTON + "']";
    private static final String LOGIN_ERROR = "[data-testid='" + AdminTestIds.ADMIN.ADMIN_LOGIN_ERROR + "']";
    private static final String DASHBOARD_PAGE = "[data-testid='" + AdminTestIds.ADMIN.ADMIN_DASHBOARD_PAGE + "']";
    private static final String LOGOUT_BUTTON = "[data-testid='" + AdminTestIds.ADMIN.ADMIN_LOGOUT_BUTTON + "']";

    private final Locator usernameInput;
    private final Locator passwordInput;
    private final Locator loginButton;
    private final Locator loginError;
    private final Locator dashboardPage;
    private final Locator logoutButton;

    public AdminPage(Page page) {
        this.page = page;
        this.usernameInput = page.locator(USERNAME_INPUT);
        this.passwordInput = page.locator(PASSWORD_INPUT);
        this.loginButton = page.locator(LOGIN_BUTTON);
        this.loginError = page.locator(LOGIN_ERROR);
        this.dashboardPage = page.locator(DASHBOARD_PAGE);
        this.logoutButton = page.locator(LOGOUT_BUTTON);
    }

    public void navigateToLoginPage() {
        page.navigate(ConfigManager.getInstance().getUiBaseUrl() + ADMIN_LOGIN_NAVIGATE);
    }

    public void navigateToDashboardPage() {
        page.navigate(ConfigManager.getInstance().getUiBaseUrl() + ADMIN_DASHBOARD_NAVIGATE);
    }

    public void login(String username, String password) {
        usernameInput.fill(username);
        passwordInput.fill(password);
        loginButton.click();
    }

    public void logout() {
        logoutButton.click();
    }

    public void waitForLoginPage() {
        usernameInput.waitFor(new Locator.WaitForOptions()
                .setState(WaitForSelectorState.VISIBLE)
                .setTimeout(10000));
    }

    public void waitForDashboardPage() {
        dashboardPage.waitFor(new Locator.WaitForOptions()
                .setState(WaitForSelectorState.VISIBLE)
                .setTimeout(10000));
    }

    public void waitForError() {
        loginError.waitFor(new Locator.WaitForOptions()
                .setState(WaitForSelectorState.VISIBLE)
                .setTimeout(10000));
    }

    public boolean isLoginPageVisible() {
        return usernameInput.isVisible();
    }

    public boolean isDashboardPageVisible() {
        return dashboardPage.isVisible();
    }

    public boolean isErrorVisible() {
        return loginError.isVisible();
    }

    public String getErrorText() {
        return loginError.textContent().trim();
    }

    public String currentUrl() {
        return page.url();
    }
}
