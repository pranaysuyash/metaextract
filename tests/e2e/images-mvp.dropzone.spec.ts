import { test, expect } from '@playwright/test';

test.describe('Images MVP dropzone', () => {
  test('native file input is hidden and dropzone shows free checks', async ({
    page,
  }) => {
    await page.goto('/images_mvp');

    // Wait for the dropzone to be present
    await page.waitForSelector('[data-testid="image-dropzone"]');

    // Native input should be visually hidden (opacity 0)
    const inputOpacity = await page.$eval(
      'input[type="file"]',
      el => getComputedStyle(el).opacity
    );
    expect(inputOpacity).toBe('0');

    // Browser default "Choose file" text should not be present
    const chooseCount = await page.locator('text=Choose file').count();
    expect(chooseCount).toBe(0);

    // Free checks badge should be visible for anonymous users
    await expect(page.locator('text=2 free checks')).toBeVisible();
  });
});
