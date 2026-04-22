import { test, expect } from '@playwright/test';

test.describe('Learnwise Dashboard', () => {
  test('should load the home page successfully', async ({ page }) => {
    // Navigating to the homepage. App router will redirect to /dashboard.
    await page.goto('/');

    // Check if redirect happens (assuming it's automatic for testing env/unauthed state, or root serves it)
    await expect(page).toHaveURL(/.*dashboard|.*\//);

    // Assert that the page renders without a hard crash (e.g. looking for a known generic class or element)
    // We look for any h1, assuming Learnwise always renders an h1 in the UI
    const heading = page.locator('h1').first();
    await expect(heading).toBeVisible({ timeout: 10000 });
  });
});
