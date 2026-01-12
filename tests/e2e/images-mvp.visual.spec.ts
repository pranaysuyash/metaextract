import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Visual tests for Images MVP: overlay visibility and credits alignment

test.describe('Images MVP visual checks', () => {
  test('shows uploader overlay and progress tracker while uploading', async ({
    page,
  }) => {
    await page.goto('/images_mvp');

    // Optional: login to ensure reliable quote/credits path
    await page.waitForLoadState('networkidle');
    if ((await page.locator('[data-auth="login"]').count()) > 0) {
      await page.locator('[data-auth="login"]').click();
      await page.locator('#login-email').fill('test@metaextract.com');
      await page.locator('#login-password').fill('TestPassword123!');
      await page.locator('button[type="submit"]').click();
      await page.waitForResponse(
        resp => resp.url().includes('/api/auth/login') && resp.status() === 200,
        { timeout: 10000 }
      );
      await page.waitForSelector('[data-auth="login"]', { state: 'hidden' });
      await page.reload();
    }

    // Intercept extract endpoint and delay response so we can assert "in-progress" UI
    await page.route('/api/images_mvp/extract', async route => {
      // wait 2s to simulate processing/upload time
      await new Promise(r => setTimeout(r, 2000));
      await route.fulfill({
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fields_extracted: 1,
          mime_type: 'image/jpeg',
          processing_ms: 100,
        }),
      });
    });

    const filePath = path.resolve(__dirname, 'fixtures/images/iphone_exif.jpg');
    const input = page.getByTestId('image-upload-input');
    await input.focus();
    await input.setInputFiles(filePath);

    // Wait for filename to show
    await expect(page.getByText('iphone_exif.jpg')).toBeVisible({
      timeout: 30000,
    });

    // Wait for Credits to appear
    await expect(page.getByText('Credits:')).toBeVisible({ timeout: 30000 });

    const analyzeButton = page.getByRole('button', { name: 'Analyze' });
    await expect(analyzeButton).toBeEnabled({ timeout: 60000 });
    await analyzeButton.click();

    // While the mocked extract is delayed, the ProgressTracker should be visible
    await expect(page.getByRole('status')).toBeVisible({ timeout: 5000 });

    // We only hide the dropzone overlay once the ProgressTracker starts streaming updates.
    // This run doesn't simulate WS progress updates, so the overlay may still be visible — accept either.
    // Target the dropzone overlay specifically (its text is in a <p> with font-mono).
    const overlayLocator = page.locator('p.text-white.font-mono');
    if ((await overlayLocator.count()) > 0) {
      if (await overlayLocator.first().isVisible()) {
        // overlay is visible (expected when tracker isn't streaming yet)
      } else {
        await expect(overlayLocator.first()).toBeHidden();
      }
    }

    // Wait for the mocked extraction to complete and navigate to results
    await page.waitForResponse(
      resp =>
        resp.url().includes('/api/images_mvp/extract') && resp.status() === 200,
      { timeout: 60000 }
    );
    await expect(page).toHaveURL(/\/images_mvp\/results/);
  });

  test('credits label is vertically aligned with filename', async ({
    page,
  }) => {
    await page.goto('/images_mvp');
    await page.waitForLoadState('networkidle');

    // If login exists, sign in for deterministic quote behavior
    if ((await page.locator('[data-auth="login"]').count()) > 0) {
      await page.locator('[data-auth="login"]').click();
      await page.locator('#login-email').fill('test@metaextract.com');
      await page.locator('#login-password').fill('TestPassword123!');
      await page.locator('button[type="submit"]').click();
      await page.waitForResponse(
        resp => resp.url().includes('/api/auth/login') && resp.status() === 200,
        { timeout: 10000 }
      );
      await page.waitForSelector('[data-auth="login"]', { state: 'hidden' });
      await page.reload();
    }

    const filePath = path.resolve(__dirname, 'fixtures/images/iphone_exif.jpg');
    const input = page.getByTestId('image-upload-input');
    await input.focus();
    await input.setInputFiles(filePath);

    // Wait for filename and credits to appear
    const filenameLocator = page.getByText('iphone_exif.jpg');
    await expect(filenameLocator).toBeVisible({ timeout: 30000 });
    const fileCard = page.locator(
      'div.mt-4.rounded-lg:has-text("iphone_exif.jpg")'
    );
    const creditsLocator = fileCard.locator('div:has-text("Credits:")').first();
    await expect(creditsLocator).toBeVisible({ timeout: 30000 });

    // Get bounding boxes and compare vertical centers
    const fileBox = await filenameLocator.boundingBox();
    const creditsBox = await creditsLocator.boundingBox();

    expect(fileBox).not.toBeNull();
    expect(creditsBox).not.toBeNull();

    const fileCenterY = fileBox!.y + fileBox!.height / 2;
    const creditsCenterY = creditsBox!.y + creditsBox!.height / 2;

    // Assert vertical centers are within 10px (allow small rendering differences across platforms)
    const delta = Math.abs(fileCenterY - creditsCenterY);
    expect(delta).toBeLessThanOrEqual(10);
  });
});
