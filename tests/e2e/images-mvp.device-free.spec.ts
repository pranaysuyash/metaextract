import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Device-free end-to-end smoke test: banner appears and locked preview is NOT shown
test('device_free flow shows banner and no locked preview', async ({
  page,
}) => {
  await page.goto('/images_mvp');
  await page.waitForLoadState('networkidle');

  // Prepare device_free response using debug fixture
  const backendDeviceFreePath = path.resolve(
    __dirname,
    '../debug_outputs/backend_device_free.json'
  );
  const payloadRaw = fs.readFileSync(backendDeviceFreePath, 'utf8');
  const deviceFree = JSON.parse(payloadRaw);

  // Ensure it contains access.mode = device_free and free_used set
  deviceFree.access = deviceFree.access || {};
  deviceFree.access.mode = 'device_free';
  deviceFree.access.free_used = deviceFree.access.free_used ?? 1;
  deviceFree.filename = deviceFree.filename || 'device_free.jpg';

  // Intercept extract endpoint and return the prepared device_free payload
  await page.route('/api/images_mvp/extract', async route => {
    await route.fulfill({
      status: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(deviceFree),
    });
  });

  // Upload a file (use the existing iphone_exif fixture)
  const filePath = path.resolve(__dirname, 'fixtures/images/iphone_exif.jpg');
  const input = page.getByTestId('image-upload-input');
  await input.focus();
  await input.setInputFiles(filePath);

  // Wait for filename and click Analyze
  await expect(page.getByText(/iphone_exif.jpg/)).toBeVisible({
    timeout: 20000,
  });
  const analyzeButton = page.getByRole('button', { name: 'Analyze' });
  await expect(analyzeButton).toBeEnabled({ timeout: 60000 });
  await analyzeButton.click();

  // Wait for response and results nav
  await page.waitForResponse(
    resp =>
      resp.url().includes('/api/images_mvp/extract') && resp.status() === 200,
    { timeout: 60000 }
  );
  await expect(page).toHaveURL(/\/images_mvp\/results/);

  // Assert banner is visible
  await expect(page.getByText(/Free check used/)).toBeVisible();

  // Assert limited/locked preview is NOT shown
  const lockedPreview = page.getByText('LOCKED FIELDS PREVIEW');
  await expect(lockedPreview).toHaveCount(0);
});
