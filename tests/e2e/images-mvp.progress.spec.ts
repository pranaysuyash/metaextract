import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Visual-ish: assert the consolidated extraction header appears during upload
test('shows consolidated extraction header while uploading', async ({ page }) => {
  await page.goto('/images_mvp');
  await page.waitForLoadState('networkidle');

  // Intercept extract and delay so UI shows "in-progress" state
  await page.route('/api/images_mvp/extract', async route => {
    await new Promise(r => setTimeout(r, 1500));
    await route.fulfill({
      status: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fields_extracted: 1, mime_type: 'image/jpeg' }),
    });
  });

  const filePath = path.resolve(__dirname, 'fixtures/images/iphone_exif.jpg');
  const input = page.getByTestId('image-upload-input');
  await input.setInputFiles(filePath);

  // Click Analyze / Start
  const analyzeButton = page.getByRole('button', { name: 'Analyze' });
  await analyzeButton.click();

  // While server delayed, the extraction header should appear (target header specifically)
  const header = page.locator('text=Extracting Metadata...').first();
  await expect(header).toBeVisible({ timeout: 5000 });
  // Capture baseline visual for the consolidated header
  await expect(header).toHaveScreenshot('extraction-header.png');
  await expect(page.locator('div.font-mono').first()).toBeVisible();
});
